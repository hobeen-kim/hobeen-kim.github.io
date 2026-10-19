---
title: "보안: DTLS-SRTP"
description: "WebRTC가 암호화를 필수로 못 박은 이유, 하나의 UDP 5-tuple 위에서 STUN·DTLS·SRTP를 나누는 demux, a=setup 역할 결정과 a=fingerprint 검증, exporter로 SRTP 키를 도출하는 과정, 시그널링 무결성에 기대는 신뢰 모델과 IP 노출 문제를 다룬다."
date: 2026-10-19
tags: [WebRTC, DTLS, SRTP, Security]
prev: /study/webrtc/09-quality-latency
next: /study/webrtc/11-datachannel
---

# 보안: DTLS-SRTP

::: info 학습 목표
- WebRTC가 암호화를 선택이 아니라 필수로 정한 이유와 RFC 8827이 요구하는 최소 조건을 안다.
- 하나의 UDP 5-tuple 위에서 STUN·DTLS·SRTP가 첫 바이트로 구분되는 원리(RFC 7983)를 설명할 수 있다.
- `a=setup` 역할 결정, DTLS 핸드셰이크, `a=fingerprint`로 self-signed 인증서를 검증하는 방식을 이해한다.
- `use_srtp` 확장과 exporter로 SRTP 키가 도출되는 과정, 보호 프로파일별 차이를 안다.
- "시그널링 무결성이 곧 보안"이라는 신뢰 모델과 MITM 대응, 인증서 관리, IP 노출(mDNS) 문제를 운영 관점에서 정리한다.
:::

## 1. 암호화는 선택이 아니다

WebRTC 보안의 출발점은 두 RFC다. <strong>RFC 8826</strong>(Security Considerations for WebRTC)이 위협 모델을 정리하고, <strong>RFC 8827</strong>(WebRTC Security Architecture)이 구현이 반드시 지켜야 할 규칙을 정한다. 핵심 요구사항을 원문 그대로 옮기면 다음과 같다.

| 요구사항 | RFC 8827 원문 요지 |
|---|---|
| 미디어 암호화 필수 | 모든 미디어 채널은 SRTP·SRTCP로 보호해야 한다(MUST). 평문 RTP/RTCP 전송 금지, NULL 암호화 모드 협상 금지 |
| SDES 금지 | SDP security descriptions(`a=crypto`)를 offer해서도, 선택해서도 안 된다(MUST NOT) |
| DTLS-SRTP 필수 | 모든 미디어 채널에 DTLS-SRTP를 offer해야 한다(MUST) |
| 필수 구현 DTLS | DTLS 1.2 + `TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256` + P-256 곡선 |
| 필수 구현 SRTP 프로파일 | `SRTP_AES128_CM_HMAC_SHA1_80` |
| 선호 규칙 | Forward Secrecy 지원 cipher suite를 우선(MUST), AEAD를 우선(SHOULD) |

<strong>SDES를 금지한 이유</strong>가 이 설계 철학을 잘 보여준다. SDES는 SRTP 마스터 키를 SDP 안의 `a=crypto` 줄에 평문으로 넣어 보낸다. 그러면 시그널링 서버, 그 서버의 로그, 중간 프록시 모두가 미디어 키를 보게 된다. DTLS-SRTP는 키를 두 피어가 DTLS 핸드셰이크로 직접 합의하므로 키가 시그널링 경로에 절대 실리지 않는다. 시그널링 서버를 운영하는 쪽조차 미디어를 복호화할 수 없다는 점이 중요하다.

WebRTC 연결 위에서 무엇이 무엇으로 보호되는지 정리하면 다음과 같다.

| 트래픽 | 보호 수단 | 비고 |
|---|---|---|
| 오디오·비디오 | SRTP / SRTCP | 키는 DTLS에서 도출. RTP 헤더는 인증만 되고 암호화되지 않는다(3절) |
| DataChannel | DTLS 레코드 안의 SCTP | DTLS가 SCTP 패킷 전체를 암호화([11장](/study/webrtc/11-datachannel)) |
| ICE 연결성 검사 | STUN `MESSAGE-INTEGRITY` | `ice-pwd`로 HMAC 인증. 암호화는 아니다 |
| SDP · ICE 후보 | <strong>WebRTC 범위 밖</strong> | 시그널링을 직접 TLS로 보호해야 한다(4절) |

마지막 줄이 이 장의 핵심 복선이다. WebRTC는 미디어를 강제로 암호화하지만, 그 암호화의 신뢰 근거인 인증서 지문은 시그널링으로 전달된다. 시그널링 보호는 애플리케이션 몫으로 남겨져 있다.

<strong>consent freshness</strong>도 보안 장치다. RFC 8827은 연결 중에도 주기적으로 keepalive를 보내고, 실패하면 세션을 끝내도록 요구한다. 구체적인 절차는 RFC 7675에 있다. ICE Binding 요청을 계속 보내 상대가 여전히 수신에 동의하는지 확인하고, 30초 동안 응답이 없으면 송신을 멈춘다. 악성 페이지가 브라우저를 이용해 임의의 주소로 미디어를 쏘아 보내는 DDoS 증폭을 막기 위한 장치다.

### 하나의 5-tuple 위에서 프로토콜 나누기

[06장](/study/webrtc/06-ice)에서 ICE가 고른 후보 쌍은 결국 UDP 소켓 하나, 즉 5-tuple 하나다. BUNDLE과 rtcp-mux까지 쓰면 STUN(연결성 검사·consent), DTLS(핸드셰이크·DataChannel), SRTP/SRTCP(미디어)가 전부 같은 포트로 오간다. 수신 측은 datagram의 <strong>첫 바이트</strong>만 보고 어느 스택으로 넘길지 결정한다.

![하나의 UDP 소켓으로 들어온 datagram을 첫 바이트 값으로 분류하는 demux 구조. 0–3은 STUN, 20–63은 DTLS, 64–79는 TURN 서버에서 온 경우에만 TURN ChannelData, 128–191은 RTP/RTCP로 SRTP 복호화, 나머지는 폐기(80–127과 192–255는 QUIC 예약)](/images/study-webrtc/10-demux-light.png)
![하나의 UDP 소켓으로 들어온 datagram을 첫 바이트 값으로 분류하는 demux 구조. 0–3은 STUN, 20–63은 DTLS, 64–79는 TURN 서버에서 온 경우에만 TURN ChannelData, 128–191은 RTP/RTCP로 SRTP 복호화, 나머지는 폐기(80–127과 192–255는 QUIC 예약)](/images/study-webrtc/10-demux-dark.png)

이 구분이 가능한 이유는 각 프로토콜 헤더의 첫 바이트가 우연히(사실은 의도적으로) 겹치지 않기 때문이다.

- <strong>STUN</strong>: 메시지 타입 필드의 최상위 2비트가 항상 `00`이고 첫 바이트는 0~3 범위에 들어간다.
- <strong>DTLS</strong>: 첫 바이트는 레코드의 content type이다. change_cipher_spec(20), alert(21), handshake(22), application_data(23)가 모두 20~63 범위다.
- <strong>RTP/RTCP</strong>: 첫 2비트가 버전 번호 2(`10`)이므로 첫 바이트가 128~191이 된다. RTP와 RTCP 구분은 두 번째 바이트(PT)로 한다. RTCP 패킷 타입은 192~223 범위다(RFC 5761).

규칙은 세 번 진화했다. RFC 5764(2010)는 STUN 0~1, DTLS 20~63, RTP/RTCP 128~191만 정의했다. RFC 7983(2016)이 STUN을 0~3으로 넓히고 ZRTP(16~19)와 TURN ChannelData(64~79)를 추가했다. RFC 9443(2023)은 남은 범위(80~127, 192~255)를 QUIC에 배정하고, 64~79는 응답 중인 TURN 서버에서 온 패킷일 때만 TURN ChannelData로 보도록 바꿨다.

브라우저나 GStreamer webrtcbin, Pion 같은 스택은 이 분류를 내부에서 처리한다. 디바이스에서 미디어 경로 일부를 직접 구현하거나 패킷 캡처를 분석할 때는 같은 규칙을 그대로 쓰면 된다.

```go
// RFC 7983/9443 기준 첫 바이트 demux
func classify(pkt []byte, fromTURNServer bool) string {
	if len(pkt) == 0 {
		return "drop"
	}
	switch b := pkt[0]; {
	case b <= 3:
		return "stun"
	case b >= 20 && b <= 63:
		return "dtls"
	case b >= 64 && b <= 79 && fromTURNServer:
		return "turn-channeldata"
	case b >= 128 && b <= 191:
		if len(pkt) > 1 && pkt[1] >= 192 && pkt[1] <= 223 {
			return "srtcp" // RFC 5761: RTCP PT 범위
		}
		return "srtp"
	default:
		return "drop"
	}
}
```

Wireshark에서 WebRTC 트래픽이 전부 "UDP"로만 보일 때 "Decode As"로 DTLS·RTP를 지정하면 이 규칙으로 해석된다. 다만 SRTP 페이로드는 키 없이는 복호화되지 않는다. 헤더만 보인다는 사실 자체가 3절에서 다룰 SRTP의 한계와 연결된다.

## 2. DTLS 핸드셰이크와 a=setup 역할 결정

DTLS는 TLS를 UDP 위에서 동작하도록 고친 프로토콜이다. 레코드에 명시적 시퀀스 번호를 붙이고, 핸드셰이크 메시지에 재전송 타이머와 단편화 규칙을 추가했다. WebRTC에서 DTLS가 맡는 일은 두 가지다. 첫째, 상대가 SDP로 약속한 그 인증서를 가진 쪽인지 확인한다. 둘째, SRTP 키를 합의한다. DataChannel이 있으면 셋째로 SCTP를 실어 나른다.

### 누가 클라이언트인가: a=setup

TLS에는 클라이언트(ClientHello를 보내는 쪽)와 서버가 있다. P2P인 WebRTC는 둘 중 누가 클라이언트가 될지 SDP로 정한다. 이때 쓰는 속성이 `a=setup`이다. 원래 RFC 4145(TCP 연결 방향 협상)에서 왔고, DTLS 쪽 규칙은 RFC 8842가, WebRTC 쪽 규칙은 JSEP(RFC 9429)가 정한다.

| 값 | 의미 | 사용 위치 |
|---|---|---|
| `actpass` | 둘 다 가능. 상대가 정하라 | offer는 반드시 이 값(JSEP: MUST) |
| `active` | 내가 DTLS 클라이언트가 되어 ClientHello를 보낸다 | answer. JSEP은 answerer가 `active`를 쓰라고 권고(SHOULD) |
| `passive` | 내가 DTLS 서버가 되어 ClientHello를 기다린다 | answer에서 선택 가능 |
| `holdconn` | 연결 보류 | DTLS 협상에는 사용 금지(RFC 8842) |

answerer가 `active`를 맡는 데는 실무적 이유가 있다. answerer는 answer를 만드는 시점에 이미 offer 안의 offerer 지문을 알고 있다. 그래서 ICE가 연결되는 즉시 ClientHello를 보낼 수 있다. 반대로 offerer가 클라이언트라면 answer가 시그널링으로 돌아올 때까지 기다려야 한다.

운영자 브라우저가 offer를 보내고 농기계 디바이스가 answer하는 흔한 구성(KVS WebRTC의 Viewer→Master 흐름도 같다)이라면 다음 순서로 진행된다.

![운영자 브라우저(offerer, passive로 DTLS 서버)와 디바이스(answerer, active로 DTLS 클라이언트)가 시그널링 서버를 거쳐 a=setup:actpass·fingerprint A가 담긴 offer와 a=setup:active·fingerprint B가 담긴 answer를 교환하고, ICE 연결성 검사 후 디바이스가 use_srtp 프로파일 목록을 담은 ClientHello를 보내며 DTLS 1.2 핸드셰이크를 마친 뒤 양쪽이 상대 인증서 해시를 SDP의 fingerprint와 비교하고 exporter로 SRTP 키를 도출해 SRTP 미디어와 SCTP 데이터를 주고받는 시퀀스](/images/study-webrtc/10-dtls-handshake-light.png)
![운영자 브라우저(offerer, passive로 DTLS 서버)와 디바이스(answerer, active로 DTLS 클라이언트)가 시그널링 서버를 거쳐 a=setup:actpass·fingerprint A가 담긴 offer와 a=setup:active·fingerprint B가 담긴 answer를 교환하고, ICE 연결성 검사 후 디바이스가 use_srtp 프로파일 목록을 담은 ClientHello를 보내며 DTLS 1.2 핸드셰이크를 마친 뒤 양쪽이 상대 인증서 해시를 SDP의 fingerprint와 비교하고 exporter로 SRTP 키를 도출해 SRTP 미디어와 SCTP 데이터를 주고받는 시퀀스](/images/study-webrtc/10-dtls-handshake-dark.png)

SDP에서는 다음 두 줄이 이 과정을 결정한다([04장](/study/webrtc/04-sdp-jsep)에서 한 줄씩 읽었던 그 속성들이다).

```text
# offer (브라우저)
a=fingerprint:sha-256 4A:AD:B9:B1:3F:82:18:3B:54:02:12:DF:3E:5D:49:6B:19:E5:7C:AB:3A:6F:0C:D2:1E:9F:7D:E4:A2:1B:93:0C
a=setup:actpass

# answer (디바이스)
a=fingerprint:sha-256 7F:21:03:9C:5E:D8:61:AA:0B:44:C7:9E:12:F3:85:6D:20:BB:4E:91:C6:3A:7D:58:E2:0F:13:9A:64:CB:7E:01
a=setup:active
```

### 지문으로 self-signed 인증서를 검증한다

웹 HTTPS는 CA가 서명한 인증서 체인을 검증한다. WebRTC 피어는 CA 인증서가 없다. 브라우저는 연결마다(또는 앱이 넘겨준) <strong>self-signed 인증서</strong>를 쓰고, 신뢰 근거는 SDP의 `a=fingerprint` 한 줄이다(형식은 RFC 8122). 지문은 DER로 인코딩된 인증서 전체의 해시이고, 실무에서는 `sha-256`을 쓴다.

검증 로직은 단순하다.

1. DTLS 핸드셰이크 중 상대가 보낸 `Certificate` 메시지에서 인증서를 꺼낸다.
2. 그 인증서를 SDP에 적힌 해시 함수로 해시한다.
3. 원격 SDP의 `a=fingerprint` 값과 일치하지 않으면 핸드셰이크를 실패시킨다.

<strong>상호 인증</strong>이라는 점이 중요하다. DTLS 서버(passive 쪽)는 `CertificateRequest`를 보내 클라이언트 인증서도 요구한다. 그래서 양쪽 모두 상대 지문을 검증한다. 시퀀스 그림의 마지막 노트 두 개가 바로 이 단계다.

여기에는 미묘한 경쟁 조건도 있다. answerer는 answer를 보내자마자 ICE 검사를 시작하고 곧이어 ClientHello를 보낸다. 그런데 이 시점에 offerer는 시그널링으로 오는 answer를 아직 못 받았을 수 있다. 상대 지문을 모르는 상태에서 핸드셰이크가 시작되는 셈이다. 구현은 원격 SDP가 적용될 때까지 지문 검증을 미루는 방식으로 이를 처리한다. 디바이스 측 스택을 직접 다룬다면 "answer 적용 전에 도착한 DTLS 패킷"을 버리지 않는지 확인해야 한다.

### 운영에서 만나는 DTLS 문제

| 증상 | 원인 | 확인·대응 |
|---|---|---|
| ICE는 `connected`인데 영상이 안 나옴, `dtlsState`가 `connecting`에 머묾 | 양쪽 다 passive거나 다 active(역할 충돌) | SDP의 `a=setup` 확인. 비표준 디바이스 스택이면 answer 역할을 맞춘다(Pion은 `SettingEngine.SetAnsweringDTLSRole`) |
| `dtlsState: failed` | 지문 불일치. SDP munging이 `a=fingerprint`를 건드렸거나, 시그널링이 SDP를 바꿨음 | 원격 SDP 지문과 실제 원격 인증서 지문을 비교(5절 코드) |
| LTE에서 첫 화면이 유독 늦음 | DTLS 1.2 전체 핸드셰이크는 2 RTT이고, 손실 시 재전송 타이머(초기 1초, RFC 6347)를 기다림 | ICE 지연과 별개로 DTLS 구간을 측정. 손실이 큰 회선이면 핸드셰이크 메시지 크기를 줄인다 |
| 특정 망에서만 핸드셰이크 실패 | RSA 인증서 등으로 핸드셰이크 메시지가 커져 단편화·MTU 문제가 생김 | ECDSA P-256 인증서를 쓰면 메시지가 작아진다 |

DTLS 버전도 바뀌는 중이다. RFC 8827은 DTLS 1.2를 필수 구현으로 정하면서 DTLS 1.3 표준화를 언급하고, "DTLS 1.2만 지원하는 엔드포인트는 상호운용 문제를 겪을 수 있다"고 적는다. Firefox는 WebRTC에서 DTLS 1.3을 기본으로 켰고, 이후 DTLS 1.2 전용 서버와의 상호운용 문제가 버그 트래커에 보고되기도 했다. 브라우저별 전환 시점이 다르므로, 디바이스 스택이 DTLS 1.2만 지원한다면 최신 브라우저와 주기적으로 상호운용 테스트를 해야 한다. 실제로 협상된 버전은 `getStats()`의 transport 항목 `tlsVersion`에서 보인다(3절 코드).

## 3. SRTP 키 도출과 보호 프로파일

### use_srtp 확장: DTLS는 키만 만든다

DTLS-SRTP(RFC 5764)의 아이디어는 "핸드셰이크는 DTLS로 하되, 미디어는 DTLS 레코드에 싣지 않는다"이다. 미디어 패킷마다 DTLS 레코드 헤더를 붙이면 오버헤드가 생기고, RTP 헤더를 보고 동작하는 장비(지터 버퍼, SFU)와도 맞지 않는다. 그래서 다음 순서를 밟는다.

1. DTLS 클라이언트가 ClientHello에 `use_srtp` 확장(타입 14)을 넣고, 지원하는 SRTP 보호 프로파일을 선호 순서대로 나열한다.
2. 서버는 그중 <strong>하나</strong>를 골라 ServerHello에 담는다. 클라이언트가 제시하지 않은 프로파일은 고를 수 없고, 공통 프로파일이 없으면 확장을 생략한다.
3. 핸드셰이크가 끝나면 TLS exporter로 키 머티리얼을 뽑는다.
4. 이후 RTP/RTCP는 SRTP/SRTCP 패킷으로 <strong>DTLS 레코드 없이</strong> 바로 UDP에 실린다. RFC 5764는 미디어가 DTLS application_data 레코드로 전송되는 일은 없다고 못 박는다. 반면 SCTP 같은 비(非)RTP 데이터는 일반 DTLS 레코드로 감싸 별도 datagram으로 보낸다.

1절의 demux가 이 구조 때문에 필요하다. 같은 5-tuple에 DTLS 레코드(20~63)와 날것의 SRTP 패킷(128~191)이 섞여 들어오기 때문이다.

### exporter로 키 뽑기

![DTLS 핸드셰이크의 master secret을 TLS exporter(label "EXTRACTOR-dtls_srtp")에 넣어 2×(키 16B + salt 14B)=60바이트를 뽑고, 이를 client key·server key·client salt·server salt 순으로 잘라 client key+client salt는 active(DTLS 클라이언트)→passive 방향, server key+server salt는 passive(DTLS 서버)→active 방향 SRTP 컨텍스트에 쓰는 구조](/images/study-webrtc/10-key-derivation-light.png)
![DTLS 핸드셰이크의 master secret을 TLS exporter(label "EXTRACTOR-dtls_srtp")에 넣어 2×(키 16B + salt 14B)=60바이트를 뽑고, 이를 client key·server key·client salt·server salt 순으로 잘라 client key+client salt는 active(DTLS 클라이언트)→passive 방향, server key+server salt는 passive(DTLS 서버)→active 방향 SRTP 컨텍스트에 쓰는 구조](/images/study-webrtc/10-key-derivation-dark.png)

- exporter 라벨은 `"EXTRACTOR-dtls_srtp"`, 컨텍스트는 비어 있다.
- 길이는 `2 × (master_key_len + master_salt_len)`이다. `AES_CM_128_HMAC_SHA1_80`이면 키 16바이트, salt 14바이트이므로 60바이트다.
- 잘라 쓰는 순서는 client 키, server 키, client salt, server salt다. 키 둘을 먼저 놓고 salt 둘을 뒤에 놓는 배치라 직접 구현할 때 실수가 잦다.
- 방향마다 키가 다르다. DTLS 클라이언트(active)가 보내는 SRTP는 client 키·salt로, 서버가 보내는 SRTP는 server 키·salt로 보호된다. 수신 측은 상대 방향 키로 복호화한다.
- 이렇게 얻은 마스터 키·salt는 다시 SRTP KDF(RFC 3711)를 거쳐 실제 암호화·인증 세션 키가 된다.

a=setup 역할이 키 배치까지 결정한다는 점을 기억해 두자. 역할을 잘못 해석하는 구현은 핸드셰이크는 성공하지만 SRTP 인증이 전부 실패한다. 그러면 "DTLS는 connected인데 영상 패킷이 전부 버려지는" 증상이 나타난다.

### 보호 프로파일 비교

| 프로파일 | 코드 | 암호화 / 인증 | 마스터 키·salt | 인증 태그 | 비고 |
|---|---|---|---|---|---|
| `SRTP_AES128_CM_HMAC_SHA1_80` | 0x0001 | AES-128 CTR + HMAC-SHA1 | 16B · 14B | 10B(80비트) | RFC 8827 필수 구현. 가장 넓은 호환성 |
| `SRTP_AES128_CM_HMAC_SHA1_32` | 0x0002 | AES-128 CTR + HMAC-SHA1 | 16B · 14B | 4B(32비트) | 태그가 짧아 위조 내성이 약하다 |
| `SRTP_AEAD_AES_128_GCM` | 0x0007 | AES-128-GCM (AEAD) | 16B · 12B | 16B | RFC 7714. 암호화와 인증을 한 번에 처리 |
| `SRTP_AEAD_AES_256_GCM` | 0x0008 | AES-256-GCM (AEAD) | 32B · 12B | 16B | RFC 7714 |
| `SRTP_NULL_HMAC_SHA1_80/32` | 0x0005/6 | 암호화 없음 | — | — | RFC 8827이 금지(NULL 암호화) |

GCM 프로파일은 RFC 8827의 "AEAD 우선" 원칙에 맞는다. AES 하드웨어 가속(x86 AES-NI, ARMv8 Crypto Extension)이 있으면 CTR+HMAC 조합보다 효율적이다. 반대로 가속이 없는 저사양 SoC에서 수 Mbps 영상을 암호화한다면 프로파일별 CPU 사용량을 직접 재 봐야 한다. 어떤 프로파일이 선택될지는 클라이언트의 제시 순서와 서버의 선택으로 정해지므로, 추측하지 말고 확인한다.

```javascript
// 협상 결과 확인: DTLS 버전·cipher·SRTP 프로파일·역할·인증서 지문
async function dumpSecurity(pc) {
  const stats = await pc.getStats();
  stats.forEach((s) => {
    if (s.type !== 'transport') return;
    const local = stats.get(s.localCertificateId);
    const remote = stats.get(s.remoteCertificateId);
    console.table({
      dtlsState: s.dtlsState,        // new | connecting | connected | closed | failed
      dtlsRole: s.dtlsRole,          // client | server | unknown
      tlsVersion: s.tlsVersion,      // 예: "FEFD" (DTLS 1.2)
      dtlsCipher: s.dtlsCipher,      // 예: TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
      srtpCipher: s.srtpCipher,      // 예: AEAD_AES_128_GCM, AES_CM_128_HMAC_SHA1_80 (표기는 구현마다 조금 다름)
      localFingerprint: local?.fingerprint,
      remoteFingerprint: remote?.fingerprint,
    });
  });
}
```

디바이스 쪽 Pion에서는 `SettingEngine`으로 제시할 프로파일과 순서를 정한다.

```go
import (
	"github.com/pion/dtls/v3"
	"github.com/pion/webrtc/v4"
)

func newAPI() *webrtc.API {
	se := webrtc.SettingEngine{}
	// 선호 순서대로 제시: GCM 우선, 필수 구현 프로파일로 폴백
	se.SetSRTPProtectionProfiles(
		dtls.SRTP_AEAD_AES_128_GCM,
		dtls.SRTP_AES128_CM_HMAC_SHA1_80,
	)
	return webrtc.NewAPI(webrtc.WithSettingEngine(se))
}
```

### SRTP가 숨기지 않는 것

SRTP는 <strong>페이로드만 암호화</strong>하고 RTP 헤더는 인증만 한다. SSRC, 시퀀스 번호, 타임스탬프, 페이로드 타입, marker 비트, 헤더 확장은 경로 위의 누구에게나 보인다. 패킷 크기와 간격도 그대로 드러난다.

- 오디오 레벨 헤더 확장(RFC 6464)이 켜져 있으면 "지금 말하고 있는지"가 평문으로 노출된다.
- 비디오 패킷 크기 변화로 장면 전환이나 움직임 정도를 추측하는 트래픽 분석이 가능하다.
- 헤더 확장 암호화(RFC 6904)나 cryptex(RFC 9335) 같은 확장 규격이 있지만, 기본 동작은 아니다.

헤더가 평문인 이유는 SFU 같은 중계 장비가 헤더를 보고 패킷을 라우팅해야 하기 때문이다. 같은 이유로 SFU를 거치면 DTLS-SRTP는 <strong>홉 단위 암호화</strong>가 된다. 브라우저→SFU, SFU→시청자 구간이 각각 따로 암호화되고, SFU 안에서는 미디어가 평문이다. 미디어 서버조차 내용을 못 보게 하려면 페이로드를 한 번 더 암호화하는 E2EE(Encoded Transform, SFrame)가 필요하다. 이 주제는 [12장](/study/webrtc/12-topology-sfu)에서 다룬다.

## 4. 신뢰 모델: 시그널링 무결성이 곧 보안

### 지문은 시그널링을 타고 온다

2절의 검증은 "SDP에 적힌 지문이 진짜 상대의 지문"이라는 전제 위에 서 있다. 그런데 그 SDP를 나르는 것은 시그널링 서버다. RFC 8827도 신원 검증이 없으면 "시그널링 서버가 잠재적으로 중간자(MITM) 공격을 할 수 있다"고 명시한다.

![왼쪽은 시그널링이 fingerprint A와 B를 원본 그대로 전달해 브라우저(인증서 A)와 디바이스(인증서 B) 사이에 DTLS 하나가 맺어지고 양쪽 해시가 일치하는 정상 흐름, 오른쪽은 탈취되거나 악의적인 시그널링이 fingerprint를 공격자 인증서 M·M'으로 바꾸고 ICE 후보도 공격자 주소로 바꿔 브라우저↔공격자(A↔M), 공격자↔디바이스(M'↔B) 두 개의 DTLS가 맺어지고 각자 해시가 일치해 경고 없이 평문이 열람되는 공격 흐름](/images/study-webrtc/10-mitm-light.png)
![왼쪽은 시그널링이 fingerprint A와 B를 원본 그대로 전달해 브라우저(인증서 A)와 디바이스(인증서 B) 사이에 DTLS 하나가 맺어지고 양쪽 해시가 일치하는 정상 흐름, 오른쪽은 탈취되거나 악의적인 시그널링이 fingerprint를 공격자 인증서 M·M'으로 바꾸고 ICE 후보도 공격자 주소로 바꿔 브라우저↔공격자(A↔M), 공격자↔디바이스(M'↔B) 두 개의 DTLS가 맺어지고 각자 해시가 일치해 경고 없이 평문이 열람되는 공격 흐름](/images/study-webrtc/10-mitm-dark.png)

공격 절차는 다음과 같다.

1. 공격자는 시그널링 경로를 장악한다. 서버 탈취, 평문 `ws://` 구간 도청·변조, 내부자, 취약한 프록시 등 경로는 여러 가지다.
2. 브라우저가 보낸 offer의 `a=fingerprint`(A)를 자기 인증서 M'의 지문으로, ICE 후보를 자기 릴레이 주소로 바꿔 디바이스에 전달한다.
3. 디바이스의 answer도 같은 방식으로 지문 B를 M으로 바꿔 브라우저에 전달한다.
4. 브라우저는 M과, 디바이스는 M'과 DTLS를 맺는다. 각자 검증한 해시는 SDP와 일치하므로 경고가 전혀 없다.
5. 공격자는 두 세션 사이에서 미디어와 DataChannel(원격 제어 명령 포함)을 복호화하고 다시 암호화해 전달한다.

WebRTC의 암호화는 "시그널링이 정직하다"는 가정 위에서만 종단 간이다. 원격 제어가 걸린 농기계라면 이 공격은 영상 유출을 넘어 <strong>제어 명령 주입</strong>으로 이어진다.

### Identity Provider는 왜 안 쓰는가

RFC 8827은 이 문제의 정식 해법으로 <strong>Identity Provider(IdP)</strong> 메커니즘을 정의했다. 제3자 IdP가 발급한 신원 주장(identity assertion)을 지문에 묶어 SDP에 넣으면, 시그널링 서버는 이 주장을 제거할 수는 있어도 위조할 수는 없다. 그러나 RFC 8827 스스로 "IdP 메커니즘은 널리 채택되지 않았다"고 적는다. 브라우저 지원도 사실상 없다. MDN browser-compat-data 기준으로 `peerIdentity`, `getIdentityAssertion()`, `setIdentityProvider()`는 Firefox(40+)만 구현했고 Chrome과 Safari는 구현하지 않았다. 실무에서 IdP는 선택지가 아니다.

### 현실적인 대응

결국 시그널링을 신뢰 기반(TCB)의 일부로 보고 지키는 수밖에 없다.

| 대응 | 내용 | 막는 위협 |
|---|---|---|
| 시그널링 전 구간 TLS | 브라우저·디바이스 모두 `wss://`/HTTPS만 허용. 디바이스는 서버 인증서 검증을 끄지 않고, CA 번들과 시계를 관리한다 | 경로상 도청·변조 |
| 강한 인증 | 운영자는 짧은 수명 토큰(JWT 등), 디바이스는 X.509 인증서(mTLS)나 기기별 자격증명으로 연결한다 | 가짜 피어 참가 |
| 인가 | "이 운영자가 이 디바이스 방에 들어갈 수 있는가"를 서버가 판단한다. 클라이언트가 임의의 수신자 ID를 지정하게 두지 않는다 | 다른 디바이스 영상·제어 탈취 |
| 시그널링 서버 최소 권한·감사 | 배포·수정 권한을 최소화하고 접속·중계 로그를 남긴다. SDP에는 `ice-pwd`·지문·내부 IP가 들어 있으므로 로그는 민감 정보로 다룬다 | 내부자·서버 탈취 |
| (선택) 디바이스 지문 고정 | 디바이스가 영구 인증서를 쓰고, 프로비저닝 때 별도 인증 채널로 지문을 백엔드에 등록한다. 뷰어는 원격 지문을 등록값과 대조한다 | 시그널링 중계 구간 변조 |

시그널링 서버의 기본 골격은 [03장](/study/webrtc/03-signaling)에서 다뤘다. 보안 관점에서 지켜야 할 최소 조건을 Node.js로 요약하면 다음과 같다.

```javascript
// TLS 종료는 앞단(ALB 등)에서 하고, 평문 WS는 내부망에서만 받는다고 가정
import { WebSocketServer } from 'ws';
import { verifyJwt, canAccessDevice } from './auth.js';

const wss = new WebSocketServer({ noServer: true });

server.on('upgrade', async (req, socket, head) => {
  try {
    const token = new URL(req.url, 'https://x').searchParams.get('token');
    const principal = await verifyJwt(token);              // 서명·만료·aud 검증
    const deviceId = req.headers['x-device-id'];
    if (!(await canAccessDevice(principal, deviceId))) {   // 인가: 이 디바이스 방에 들어갈 수 있는가
      socket.destroy();
      return;
    }
    wss.handleUpgrade(req, socket, head, (ws) => join(ws, principal, deviceId));
  } catch {
    socket.destroy();
  }
});

function join(ws, principal, deviceId) {
  ws.on('message', (raw) => {
    const msg = JSON.parse(raw);
    // 수신자는 서버가 정한다(같은 방 피어만). SDP 본문은 절대 수정하지 않는다
    relayToRoom(deviceId, principal.sub, msg);
  });
}
```

<strong>디바이스 지문 고정</strong>은 디바이스 플랫폼에서 특히 쓸 만하다. 디바이스는 사람이 아니라 우리가 프로비저닝하는 장비이므로, 공장 출고나 등록 시점에 인증서를 만들고 지문을 미리 등록할 수 있다. 예를 들어 AWS IoT Core에 X.509 인증서로 붙는 디바이스라면 MQTT로 자기 DTLS 지문을 Device Shadow의 reported 상태에 올릴 수 있다. 시그널링 채널(예: KVS 시그널링)과 독립된 인증 채널이다([AWS IoT Core 완전 정복](/posts/tech/2025-06-27-iot) 참고). 뷰어는 연결 전에 백엔드 API에서 기대 지문을 받아 원격 SDP와 대조한다.

```javascript
// expected: 백엔드가 디바이스 등록 정보에서 내려준 지문 목록(회전 대비 복수 허용)
// 형식은 'sha-256 AB:CD:...'(알고리즘 소문자, 값 대문자)로 정규화해 둔다
function assertPinnedFingerprint(remoteSdp, expected) {
  const fps = [...remoteSdp.matchAll(/^a=fingerprint:(\S+) (\S+)$/gim)]
    .map(([, alg, value]) => `${alg.toLowerCase()} ${value.toUpperCase()}`);
  const ok = fps.length > 0 && fps.every((fp) => expected.includes(fp));
  if (!ok) throw new Error('DTLS fingerprint mismatch: 시그널링 변조 의심');
}

// answer 적용 직전에 검사하고, 연결 후 getStats의 remoteCertificate로 한 번 더 확인한다
assertPinnedFingerprint(answer.sdp, expectedFingerprints);
await pc.setRemoteDescription(answer);
```

한계도 분명하다. 기대 지문을 내려주는 백엔드와 시그널링 서버가 같은 시스템이고 그 시스템이 통째로 탈취되면 지문 고정도 무력하다. 이 방식은 시그널링 중계 구간(특히 외부 관리형 서비스)을 신뢰 경계 밖으로 밀어내는 장치로 이해해야 한다. 반대 방향(디바이스가 브라우저 지문을 검증)은 브라우저 인증서가 기본적으로 연결마다 새로 생기므로 고정이 어렵다. 이 방향은 시그널링 인증·인가에 기댄다.

## 5. 인증서 생성과 관리: generateCertificate

### 브라우저: 기본은 연결마다 새 인증서

`RTCPeerConnection`을 만들 때 `certificates`를 주지 않으면 브라우저가 인증서를 직접 생성한다. 기본 동작에서는 연결마다 지문이 달라질 수 있다. 앱이 인증서를 직접 관리하려면 `RTCPeerConnection.generateCertificate()`를 쓴다.

- 모든 브라우저가 지원해야 하는 알고리즘은 두 가지다. `{ name: 'ECDSA', namedCurve: 'P-256' }`과 `{ name: 'RSASSA-PKCS1-v1_5', modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256' }`이다. ECDSA는 필수 cipher suite(ECDHE_ECDSA)와 맞고 핸드셰이크 메시지가 작아 기본으로 권장된다.
- <strong>유효 기간</strong>은 기본 30일(2592000000ms), 최대 365일(31536000000ms)이다. 브라우저가 이보다 더 짧게 제한할 수도 있다.
- `RTCCertificate`는 serializable 객체라 IndexedDB에 저장할 수 있다. 직렬화되는 것은 개인 키 자체가 아니라 키에 대한 핸들이고, 생성한 origin에서만 쓸 수 있다.
- 만료된 인증서로 `RTCPeerConnection`을 만들면 `InvalidAccessError`가 난다. 인증서는 생성자에서만 지정하고, `setConfiguration()`으로 바꿀 수 없다.

운영자 콘솔에서 인증서를 재사용하면 지문이 고정되어 감사 로그에서 "같은 운영자 단말"을 추적하기 쉬워진다. 만료 전에 갱신하는 코드는 다음과 같다.

```javascript
const DB = 'webrtc-cert', STORE = 'certs', KEY = 'operator';
const RENEW_BEFORE_MS = 7 * 24 * 3600 * 1000; // 만료 7일 전 갱신

function idb(mode, fn) {
  return new Promise((resolve, reject) => {
    const open = indexedDB.open(DB, 1);
    open.onupgradeneeded = () => open.result.createObjectStore(STORE);
    open.onerror = () => reject(open.error);
    open.onsuccess = () => {
      const tx = open.result.transaction(STORE, mode);
      const req = fn(tx.objectStore(STORE));
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    };
  });
}

async function getOrCreateCertificate() {
  let cert = await idb('readonly', (s) => s.get(KEY)).catch(() => undefined);
  if (!cert || cert.expires - Date.now() < RENEW_BEFORE_MS) {
    cert = await RTCPeerConnection.generateCertificate({
      name: 'ECDSA',
      namedCurve: 'P-256',
      expires: 90 * 24 * 3600 * 1000, // 90일 (브라우저가 더 짧게 제한할 수 있음)
    });
    await idb('readwrite', (s) => s.put(cert, KEY)).catch(() => {}); // 사생활 보호 모드 등 저장 실패 허용
  }
  return cert;
}

const cert = await getOrCreateCertificate();
console.log(cert.getFingerprints()); // [{ algorithm: 'sha-256', value: '4a:ad:...' }] (소문자 hex)
const pc = new RTCPeerConnection({ certificates: [cert], iceServers });
```

### 디바이스: 영구 키와 지문 등록

디바이스는 지문 고정(4절)을 하려면 재부팅해도 같은 인증서를 써야 한다. 개인 키를 보안 저장소(TPM, Secure Element, 최소한 권한이 제한된 파일)에 두고 매번 같은 키로 인증서를 만든다. Pion 예시는 다음과 같다.

```go
import (
	"crypto/ecdsa"
	"log"

	"github.com/pion/webrtc/v4"
)

func newPeerConnection(api *webrtc.API, priv *ecdsa.PrivateKey) (*webrtc.PeerConnection, error) {
	// priv: 보안 저장소에서 로드한 P-256 개인 키 (최초 1회 생성 후 재사용)
	cert, err := webrtc.GenerateCertificate(priv)
	if err != nil {
		return nil, err
	}
	fps, _ := cert.GetFingerprints() // []DTLSFingerprint{Algorithm, Value}
	for _, fp := range fps {
		log.Printf("DTLS fingerprint %s %s", fp.Algorithm, fp.Value) // 프로비저닝 때 백엔드에 등록
	}
	return api.NewPeerConnection(webrtc.Configuration{
		Certificates: []webrtc.Certificate{*cert},
	})
}
```

인증서 유효 기간과 회전 정책은 직접 정해야 한다. 장기간 쓸 인증서라면 `webrtc.NewCertificate(key, x509.Certificate{...})`로 템플릿(유효 기간 등)을 명시한다. 회전할 때는 새 지문을 먼저 등록해 두고, 일정 기간 옛 지문과 새 지문을 함께 허용한 다음 교체한다. 그래야 회전 순간에 뷰어 연결이 끊기지 않는다. 앞의 `assertPinnedFingerprint`가 `expected`를 목록으로 받는 이유다.

## 6. 권한과 IP 노출: getUserMedia와 mDNS

### getUserMedia 권한

카메라·마이크 접근은 브라우저 보안 모델이 직접 통제한다.

- `getUserMedia()`는 <strong>secure context</strong>(HTTPS 또는 localhost)에서만 동작한다.
- 사용자가 권한 프롬프트에서 허용해야 한다. 권한은 origin 단위로 기억된다.
- iframe 안에서 쓰려면 부모 페이지가 Permissions Policy로 위임해야 한다(`allow="camera; microphone"`).

농기계 원격 영상 시나리오에서 운영자 브라우저는 대개 <strong>수신 전용</strong>이다. 디바이스 영상을 보기만 한다면 `addTransceiver('video', { direction: 'recvonly' })`로 충분하고, getUserMedia 권한이 전혀 필요 없다. 운영자 음성을 현장 스피커로 내보내는 기능을 넣을 때만 마이크 권한을 요청한다. 권한을 적게 요구할수록 다음에 볼 IP 보호도 유지된다.

### ICE 후보는 IP를 드러낸다

ICE 후보에는 주소가 들어 있다. W3C WebRTC 명세도 "IP 주소 노출은 위치와 연결 수단을 드러낼 수 있어 민감하다"고 적는다. host 후보는 사설 IP를, srflx 후보는 공인 IP를 상대에게 알려 준다. 과거에는 웹 페이지가 사용자 몰래 PeerConnection을 만들어 사설 IP를 수집하는 데 이 점을 악용했다.

<strong>mDNS 후보</strong>가 이에 대한 대응이다. 브라우저는 host 후보의 사설 IP를 무작위 UUID 형태의 `.local` 호스트명으로 바꿔 내보낸다. 상대는 같은 LAN에 있을 때만 멀티캐스트 DNS로 이 이름을 실제 주소로 풀 수 있다.

```text
a=candidate:1 1 udp 2122260223 1f4712db-ea17-4bcf-a596-105139dfd8bf.local 54321 typ host generation 0
a=candidate:2 1 udp 1686052607 203.0.113.24 54321 typ srflx raddr 0.0.0.0 rport 0 generation 0
```

Chrome은 이 동작을 Chrome 73부터 단계적으로 도입해 2019년 Chrome 76 무렵 전면 적용했다. 이때 공지된 예외가 하나 있다. 이미 getUserMedia 권한을 받은 사이트는 더 신뢰한다고 보고 실제 사설 IP를 노출한다. srflx 후보의 공인 IP는 mDNS와 무관하게 노출된다는 점도 기억하자(`raddr`만 가려진다).

디바이스 플랫폼에서 mDNS가 일으키는 문제와 대응은 다음과 같다.

| 상황 | 영향 | 대응 |
|---|---|---|
| 디바이스 스택이 `.local` 후보를 해석하지 못함 | 브라우저의 host 후보가 무시되어 srflx·relay 쌍만 남는다. 운영자가 농장 Wi-Fi에서 같은 LAN의 장비를 볼 때도 NAT 헤어핀이나 TURN을 거치게 된다 | 디바이스 스택의 mDNS 조회를 켠다(Pion: `SettingEngine.SetICEMulticastDNSMode(ice.MulticastDNSModeQueryOnly)`). 멀티캐스트가 막힌 망이면 srflx 경로로 충분한지 측정한다 |
| 수신 전용 뷰어 | getUserMedia 권한이 없으므로 mDNS 보호가 유지된다 | 보호와 LAN 직결 중 무엇이 중요한지 정한다. 권한을 일부러 요청해 IP를 노출시키는 우회는 권하지 않는다 |
| 디바이스 공인 IP가 뷰어에게 노출 | 연결에 성공한 모든 뷰어가 농장·LTE 회선의 공인 IP를 알게 된다 | 시그널링 인가로 뷰어를 제한한다. 더 강하게 숨기려면 디바이스 측 `iceTransportPolicy: 'relay'`로 TURN 주소만 노출한다. 대신 비용과 지연이 늘어난다([07장](/study/webrtc/07-turn)) |
| 기업망·보안 확장 | 브라우저 정책이나 확장 프로그램이 WebRTC IP 처리 방식을 바꿔 host 후보가 아예 없을 수 있다 | 운영자 환경이 제한적이면 TURN(TCP/TLS 443) 폴백을 반드시 준비한다 |

후보에 담긴 주소, SDP의 `ice-pwd`와 지문은 모두 민감 정보다. 4절에서 시그널링 로그를 민감 정보로 다루라고 한 것도 같은 이유다. 디버깅 편의를 위해 SDP 전문을 장기 로그에 남기는 습관은 버리고, 필요하면 마스킹해서 남긴다.

::: tip 핵심 정리
- RFC 8827은 SRTP 암호화를 필수로, SDES를 금지로, DTLS-SRTP를 유일한 키 교환으로 정했다. 키가 시그널링 경로에 실리지 않는다.
- STUN(0–3)·DTLS(20–63)·RTP/RTCP(128–191)는 같은 5-tuple을 쓰고 첫 바이트로 구분된다(RFC 7983/9443).
- offer는 `a=setup:actpass`, answer는 `active`(권고) 또는 `passive`다. active 쪽이 ClientHello를 보내는 DTLS 클라이언트다.
- self-signed 인증서는 SDP의 `a=fingerprint`로 상호 검증한다. SRTP 키는 `use_srtp`로 프로파일을 정하고 exporter(`EXTRACTOR-dtls_srtp`)로 client/server 키·salt를 뽑아 방향별로 쓴다.
- SRTP는 페이로드만 암호화하고 RTP 헤더는 평문이다. SFU를 거치면 홉 단위 암호화가 된다(E2EE는 12장).
- 지문이 시그널링으로 오므로 시그널링이 변조되면 경고 없는 MITM이 된다. IdP는 Firefox만 구현해 실무에서 못 쓴다. TLS·인증·인가로 시그널링을 지키고, 디바이스는 지문 고정을 더할 수 있다.
- `generateCertificate()` 인증서는 기본 30일·최대 365일이고 IndexedDB에 저장할 수 있다. 디바이스는 영구 키와 회전 정책을 갖춘다.
- host IP는 mDNS `.local`로 가려지지만 srflx 공인 IP는 노출된다. 디바이스 스택의 mDNS 해석 여부를 확인하고, 필요하면 relay 정책으로 주소를 숨긴다.
:::

## 다음 챕터

[DataChannel](/study/webrtc/11-datachannel)에서는 이 장에서 맺은 DTLS 위에 SCTP를 올려 임의의 데이터를 주고받는 DataChannel의 구조, 신뢰성·순서 옵션 조합, 흐름 제어, 그리고 농기계·로봇 원격 제어 명령 채널 설계를 다룬다.
