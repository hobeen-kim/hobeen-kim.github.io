---
title: "ICE"
description: "host·srflx·prflx·relay 후보가 생기는 원리, RFC 8445 우선순위 공식과 후보 쌍 정렬, connectivity check와 정규 nomination, Trickle ICE·ICE restart·mDNS 후보·ICE-lite, iceConnectionState와 실패 원인을 다룬다."
date: 2026-10-19
tags: [WebRTC, ICE, NAT Traversal, RFC 8445]
prev: /study/webrtc/05-nat-stun
next: /study/webrtc/07-turn
---

# ICE

::: info 학습 목표
- host·srflx·prflx·relay 네 종류 후보가 어디서 생기는지 설명하고, `a=candidate` 줄을 필드 단위로 읽을 수 있다.
- RFC 8445의 후보 우선순위 공식과 후보 쌍 우선순위 공식을 계산하고, 공식이 왜 그렇게 생겼는지 이해한다.
- controlling/controlled 역할, connectivity check, 정규 nomination이 맞물려 하나의 경로가 선택되는 과정을 추적한다.
- Trickle ICE·ICE restart·mDNS 후보·ICE-lite가 각각 어떤 문제를 푸는지 알고, `iceConnectionState`로 실패 원인을 좁힐 수 있다.
:::

[05장](/study/webrtc/05-nat-stun)에서 STUN이 "NAT 바깥에서 본 내 주소"를 알려준다는 것까지 봤다. 그러나 주소를 아는 것과 그 주소로 실제 패킷이 통하는 것은 별개 문제다. 농기계는 LTE 라우터 뒤에, 운영자는 사무실 방화벽 뒤에 있다. 어떤 조합이 통할지는 미리 알 수 없다.

<strong>ICE(Interactive Connectivity Establishment, RFC 8445)</strong>는 이 불확실성을 정면으로 다룬다. 가능한 경로 후보를 전부 모으고, 짝을 지어 실제로 찔러 보고, 통하는 것 중 가장 좋은 것을 고른다. "추측하지 말고 측정하라"를 프로토콜로 만든 셈이다.

## 1. 후보의 네 종류

<strong>후보(candidate)</strong>는 상대가 나에게 패킷을 보낼 수 있을지도 모르는 전송 주소(IP·포트·프로토콜)다. ICE 에이전트는 후보를 네 가지 경로로 얻는다.

![디바이스 ICE 에이전트가 자기 NIC 주소로 host 후보를, NAT 라우터를 거쳐 STUN 서버에 Binding을 보내 srflx 후보를, TURN 서버에 Allocate를 보내 relay 후보를 얻고, 상대 피어와의 connectivity check 도중 처음 보는 주소로 prflx 후보를 발견하는 구조](/images/study-webrtc/06-candidate-types-light.png)
![디바이스 ICE 에이전트가 자기 NIC 주소로 host 후보를, NAT 라우터를 거쳐 STUN 서버에 Binding을 보내 srflx 후보를, TURN 서버에 Allocate를 보내 relay 후보를 얻고, 상대 피어와의 connectivity check 도중 처음 보는 주소로 prflx 후보를 발견하는 구조](/images/study-webrtc/06-candidate-types-dark.png)

| 종류 | 얻는 방법 | base | 특징 |
|---|---|---|---|
| <strong>host</strong> | 로컬 네트워크 인터페이스 주소 | 자기 자신 | 인터페이스마다 생긴다(Wi-Fi·LTE·VPN·Docker 브리지까지). 같은 LAN이면 가장 빠르다 |
| <strong>srflx</strong> (server reflexive) | STUN Binding 응답의 XOR-MAPPED-ADDRESS | host 후보 | NAT가 바꿔 준 공인 주소. NAT 매핑이 상대에게도 똑같이 쓰일 때만 통한다 |
| <strong>prflx</strong> (peer reflexive) | connectivity check 도중 발견 | host 후보 | 수집 단계에서는 절대 생기지 않는다. 체크 과정에서 "처음 보는 주소"로 학습된다 |
| <strong>relay</strong> | TURN Allocate 응답의 XOR-RELAYED-ADDRESS | 자기 자신 | TURN 서버가 빌려준 주소. 거의 항상 통하지만 서버 비용과 지연이 붙는다([07장](/study/webrtc/07-turn)) |

<strong>base</strong>는 이 후보로 패킷을 실제로 내보내는 로컬 소켓 주소다. RFC 8445는 "srflx 후보의 base는 Binding 요청을 보낸 host 후보", "relay 후보의 base는 그 후보 자신"이라고 정의한다. srflx 후보로 체크를 보낸다는 말은 사실 host 소켓에서 패킷을 내보내고 NAT가 그것을 srflx 주소로 바꿔 주기를 기대한다는 뜻이다. 이 성질 때문에 3절의 체크리스트에서 로컬 srflx 후보는 base로 치환되어 중복 제거된다.

<strong>prflx는 두 방향에서 생긴다.</strong> 상대의 Binding 요청이 아직 시그널링으로 받지 못한 주소에서 도착하면 그 주소가 <strong>원격 prflx</strong>가 된다. 내 체크의 응답에 담긴 XOR-MAPPED-ADDRESS가 내가 아는 어떤 후보와도 다르면 그 주소가 <strong>로컬 prflx</strong>가 된다. 후자는 [05장](/study/webrtc/05-nat-stun)의 symmetric NAT에서 흔하다. STUN 서버로 갈 때와 상대 피어로 갈 때 NAT가 서로 다른 매핑을 만들기 때문이다. 전자는 Trickle ICE(4절)에서 흔하다. 상대의 체크가 후보 시그널링보다 먼저 도착하는 일이 잦다.

<strong>component</strong>도 알아 두자. 원래 ICE는 RTP(component 1)와 RTCP(component 2)에 각각 후보를 모았다. WebRTC는 [04장](/study/webrtc/04-sdp-jsep)의 `rtcp-mux`로 RTP와 RTCP를 한 포트에 싣고 BUNDLE로 모든 m-line을 한 트랜스포트에 묶는다. 그래서 실무에서는 PeerConnection 하나에 component 1짜리 ICE 트랜스포트 하나만 남는다.

### a=candidate 줄 읽기

SDP 안이나 시그널링으로 오가는 후보는 다음처럼 생겼다. 브라우저 `RTCIceCandidate.candidate` 문자열은 앞의 `a=`만 뺀 형태다.

```
a=candidate:1467250027 1 udp 2122260223 192.168.0.10 46243 typ host generation 0 network-id 1
a=candidate:2865433455 1 udp 1686052607 203.0.113.5 61722 typ srflx raddr 192.168.0.10 rport 46243 generation 0 network-id 1
a=candidate:3745178473 1 udp 41885439 198.51.100.20 50112 typ relay raddr 203.0.113.5 rport 61722 generation 0 network-id 1
a=candidate:1029393771 1 tcp 1518280447 192.168.0.10 9 typ host tcptype active generation 0 network-id 1
```

| 필드 | 예 | 의미 |
|---|---|---|
| foundation | `1467250027` | 타입·base IP·STUN/TURN 서버 IP·전송 프로토콜이 같은 후보끼리 같은 값을 갖는다. 3절의 Frozen 알고리즘이 이 값으로 묶는다 |
| component ID | `1` | 1=RTP, 2=RTCP. rtcp-mux를 쓰면 1만 나온다 |
| transport | `udp` / `tcp` | 후보의 전송 프로토콜. TCP 후보는 RFC 6544(ICE-TCP) 규칙을 따른다 |
| priority | `2122260223` | 2절의 공식으로 계산한 32비트 우선순위 |
| address port | `192.168.0.10 46243` | 후보의 전송 주소. mDNS가 켜지면 IP 자리에 `xxxx.local`이 온다(5절) |
| `typ` | `host` / `srflx` / `prflx` / `relay` | 후보 종류 |
| `raddr` `rport` | `192.168.0.10 46243` | related address. srflx·prflx는 base, relay는 TURN이 본 mapped address를 적는다. 진단용 정보이며 host에는 없다 |
| `tcptype` | `active` / `passive` / `so` | TCP 후보의 역할. active는 연결만 거는 쪽이라 포트가 의미 없어 `9`(discard)로 찍힌다 |
| `generation` `network-id` `network-cost` `ufrag` | `0`, `1` | libwebrtc 확장 속성. RFC 8839 문법은 모르는 확장 속성을 무시하라고 규정한다 |

세 번째 줄의 relay 후보는 `raddr 203.0.113.5`를 갖는다. TURN 서버가 본 디바이스의 공인 주소, 즉 Allocate 응답의 XOR-MAPPED-ADDRESS다. 후보 줄 네 개만으로도 "디바이스는 192.168.0.10에 있고, NAT 공인 주소는 203.0.113.5이며, TURN 릴레이도 확보했다"는 네트워크 지도가 그려진다. 장애 분석에서 후보 목록부터 보는 이유다.

## 2. 우선순위 공식

후보가 모이면 순서를 매겨야 한다. RFC 8445 5.1.2절의 공식은 다음과 같다.

```
priority = 2^24 × (type preference) + 2^8 × (local preference) + 2^0 × (256 − component ID)
```

32비트 정수를 세 칸으로 나눠 쓴다고 보면 된다. 상위 8비트는 type preference(0~126), 가운데 16비트는 local preference(0~65535), 하위 8비트는 `256 − component ID`다. 자릿수가 겹치지 않으므로 <strong>타입이 먼저, 그다음 인터페이스, 마지막으로 component</strong> 순으로 비교된다.

| 후보 타입 | RFC 8445 권장값 | libwebrtc(Chrome) 실제값 |
|---|---|---|
| host | 126 | UDP 126, TCP 90 |
| prflx | 110 | UDP 110, TCP 80 |
| srflx | 100 | 100 |
| relay | 0 | UDP 2, TCP 1, TLS 0 |

RFC가 강제하는 것은 몇 가지뿐이다. 값은 0~126이어야 하고, 같은 타입은 같은 값을, 다른 타입은 다른 값을 가져야 하며, <strong>prflx는 반드시 srflx보다 높아야 한다(MUST)</strong>. 나머지는 권장이다. libwebrtc는 relay를 전송 프로토콜별로 2/1/0으로 쪼개 같은 relay라도 UDP를 TCP·TLS보다 앞세운다. TCP 위 미디어는 손실 시 재전송 대기(head-of-line blocking)로 지연이 튀기 때문이다.

순서의 논리는 단순하다. host는 중계도 NAT 변환도 없어 가장 짧은 경로다. relay는 서버를 거치므로 지연과 비용이 붙어 마지막 수단이다. prflx가 srflx보다 높은 이유는 prflx가 실제 체크로 검증된 주소라서다. srflx는 "STUN 서버 방향 매핑이 상대에게도 통하기를 바라는" 추정에 가깝다.

<strong>local preference</strong>는 같은 타입 후보 사이에서 인터페이스를 고른다. 인터페이스가 하나면 65535를 쓰라고 RFC가 권한다. 인터페이스가 여럿이면 구현이 네트워크 종류·IP 버전 등을 반영해 값을 정한다. 하위 8비트의 `256 − component ID`는 같은 후보 안에서 RTP(255)를 RTCP(254)보다 앞세운다.

1절의 예시 숫자를 풀어 보자.

```
2122260223 = 126 × 16777216 + 32542 × 256 + 255   ← host (UDP)
1686052607 = 100 × 16777216 + 32542 × 256 + 255   ← srflx
  41885439 =   2 × 16777216 + 32542 × 256 + 255   ← relay (UDP, libwebrtc 값 2)
1518280447 =  90 × 16777216 + 32542 × 256 + 255   ← host (TCP)
```

같은 인터페이스(local preference 32542)에서 나온 후보들이 타입 값만 다르다. 후보 숫자를 보고 "이 relay는 UDP 할당이구나"를 역산할 수 있다는 점은 디버깅에 쓸모가 있다.

### 후보 쌍 우선순위

체크는 후보 하나가 아니라 <strong>후보 쌍(로컬, 원격)</strong> 단위로 한다. 쌍의 우선순위는 RFC 8445 6.1.2.3절의 공식으로 계산한다.

```
pair priority = 2^32 × MIN(G, D) + 2 × MAX(G, D) + (G > D ? 1 : 0)
```

G는 <strong>controlling</strong> 에이전트 쪽 후보의 우선순위, D는 <strong>controlled</strong> 쪽 후보의 우선순위다. 공식에는 두 가지 설계 의도가 들어 있다.

- <strong>MIN이 지배한다.</strong> 쌍의 품질은 약한 쪽이 결정한다. host와 relay를 짝지으면 결국 TURN을 거친다. 그래서 둘 중 낮은 값이 최상위 자리를 차지하고, 그 값이 같을 때만 MAX로, 그것도 같으면 마지막 1비트로 순서가 갈린다.
- <strong>로컬/원격이 아니라 역할로 정의한다.</strong> "내 후보·상대 후보"로 공식을 쓰면 양쪽이 서로 다른 숫자를 얻는다. G와 D를 역할로 고정하면 양쪽이 <strong>같은 쌍에 같은 숫자</strong>를 매기고 같은 순서로 체크한다. 두 에이전트가 거의 동시에 같은 쌍을 서로 찌르게 되고, 이것이 [05장](/study/webrtc/05-nat-stun)의 UDP 홀펀칭 타이밍을 맞춰 준다. 역할이 어긋나면 이 대칭이 깨지므로 3절의 role conflict 해소가 필요하다.

예를 들어 controlling 쪽 host(G=2122260223)와 controlled 쪽 srflx(D=1686052607)의 쌍은 `2^32 × 1686052607 + 2 × 2122260223 + 1 = 7241540810645061119`다. 64비트 정수가 필요하다는 점만 기억하면 된다.

## 3. 후보 쌍, connectivity check, nomination

### controlling과 controlled

ICE 에이전트 둘 중 하나는 <strong>controlling</strong>, 다른 하나는 <strong>controlled</strong> 역할을 맡는다. 최종 경로를 결정(nomination)하는 권한은 controlling에만 있다. 규칙은 RFC 8445 6.1.1절에 있다.

- 둘 다 full 구현이면 <strong>세션을 시작한 쪽(offerer)</strong>이 controlling이다. WebRTC에서는 offer를 보낸 쪽이다.
- 한쪽이 lite 구현(5절)이면 <strong>full 쪽이 항상 controlling</strong>이다.

양쪽이 동시에 자기가 controlling이라고 믿는 경우가 생길 수 있다. 시그널링 경합이나 구현 버그가 원인이다. 그래서 모든 체크 요청에는 `ICE-CONTROLLING` 또는 `ICE-CONTROLLED` 속성이 붙고, 그 값으로 64비트 무작위 <strong>tie-breaker</strong>를 싣는다. 충돌이 감지되면 tie-breaker가 큰 쪽이 controlling을 유지하고 작은 쪽이 controlled로 바꾼다. 역할을 유지하는 쪽은 상대에게 <strong>487 (Role Conflict)</strong> 오류 응답을 돌려줘 역할 전환을 알린다.

### 체크리스트 만들기

체크리스트는 다음 순서로 만든다.

1. 로컬 후보와 원격 후보를 <strong>같은 component, 같은 주소 패밀리(IPv4/IPv6)</strong>끼리 짝짓는다.
2. 쌍 우선순위로 내림차순 정렬한다.
3. 로컬 후보가 srflx·prflx인 쌍은 로컬 후보를 <strong>base로 치환</strong>한 뒤, 같은 base·같은 원격 후보를 가진 중복 쌍을 제거한다(pruning). srflx로 보내는 체크는 어차피 host 소켓에서 나가기 때문이다.
4. 쌍 개수를 제한한다. RFC 8445의 기본 한도는 <strong>100쌍</strong>이다. 인터페이스가 많은 장비(LTE+Wi-Fi+VPN+Docker 브리지)는 이 한도에 금방 닿는다.

정렬된 쌍은 바로 다 체크하지 않는다. 처음에는 모든 쌍을 <strong>Frozen</strong>으로 두고, foundation마다 대표 쌍 하나만 <strong>Waiting</strong>으로 푼다. 같은 foundation은 같은 타입·같은 base IP·같은 서버에서 나왔으므로 결과도 비슷할 공산이 크다. 대표가 성공하면 같은 foundation의 나머지를 푼다. 쓸데없는 체크를 줄이는 장치다.

| 쌍 상태 | 의미 |
|---|---|
| Frozen | 아직 체크할 차례가 아님. 같은 foundation 쌍의 결과를 기다린다 |
| Waiting | 체크 대기열에 올라감 |
| In-Progress | Binding 요청을 보내고 응답 대기 중 |
| Succeeded | 체크 성공 |
| Failed | 응답 없음 또는 오류 응답 |

체크리스트 전체는 Running → Completed 또는 Failed 상태를 갖는다. 체크는 <strong>Ta 간격(기본 50ms)</strong>으로 하나씩 보낸다. 수십 개 STUN 요청을 한꺼번에 쏘면 NAT 매핑 테이블과 업링크를 순간적으로 압박하기 때문이다. RFC는 한 구현이 여러 ICE 에이전트를 동시에 돌리더라도 전체 트랜잭션이 5ms에 하나보다 잦으면 안 된다고 규정한다.

### connectivity check 메시지

체크는 후보 쌍 위에서 직접 주고받는 <strong>STUN Binding 요청</strong>이다. STUN 서버에 보내던 것과 같은 메시지지만 ICE 전용 속성이 붙는다.

| 속성 | 내용 |
|---|---|
| USERNAME | `상대ufrag:내ufrag`(RFC 표기로 `RFRAG:LFRAG`). SDP의 `a=ice-ufrag`에서 온다 |
| MESSAGE-INTEGRITY | 상대의 `a=ice-pwd`를 키로 쓴 HMAC. short-term credential이라 시그널링으로 교환한 SDP가 곧 인증 수단이다 |
| PRIORITY | 이 체크로 prflx 후보가 학습될 경우 그 후보에 매길 우선순위(prflx type preference로 계산) |
| ICE-CONTROLLING / ICE-CONTROLLED | 보내는 쪽의 역할과 64비트 tie-breaker |
| USE-CANDIDATE | controlling만 붙인다. "이 쌍을 쓰겠다"는 nomination 표시 |
| FINGERPRINT | 같은 포트로 들어오는 DTLS·RTP 패킷과 STUN을 구분하기 위한 CRC |

응답은 XOR-MAPPED-ADDRESS로 "요청이 어느 주소에서 왔는지"를 알려준다. 여기서 모르는 주소가 나오면 로컬 prflx가 생긴다.

![브라우저(controlling)와 디바이스(controlled)가 시그널링 서버를 통해 offer·answer·trickle candidate를 주고받은 뒤, 후보 쌍 위에서 직접 Binding 요청과 성공 응답, 역방향 triggered check와 응답으로 쌍을 valid로 만들고, 마지막에 controlling이 USE-CANDIDATE를 붙인 Binding 요청으로 nomination해 selected pair가 정해지는 시퀀스](/images/study-webrtc/06-connectivity-check-light.png)
![브라우저(controlling)와 디바이스(controlled)가 시그널링 서버를 통해 offer·answer·trickle candidate를 주고받은 뒤, 후보 쌍 위에서 직접 Binding 요청과 성공 응답, 역방향 triggered check와 응답으로 쌍을 valid로 만들고, 마지막에 controlling이 USE-CANDIDATE를 붙인 Binding 요청으로 nomination해 selected pair가 정해지는 시퀀스](/images/study-webrtc/06-connectivity-check-dark.png)

그림의 <strong>triggered check</strong>가 핵심이다. Binding 요청을 받은 쪽은 같은 쌍으로 역방향 체크를 대기열 맨 앞에 끼워 넣는다. 이렇게 하면 양방향 도달성을 빠르게 확인하고, 내 쪽 NAT에도 상대 방향 핀홀이 열린다. 체크가 성공한 쌍은 <strong>valid list</strong>에 오른다.

### 정규 nomination

valid 쌍이 여럿 생기면 controlling 에이전트가 하나를 골라 <strong>USE-CANDIDATE를 붙여 한 번 더 체크</strong>한다. 이 체크가 성공하면 양쪽이 그 쌍을 nominated로 표시하고, 해당 component의 <strong>selected pair</strong>로 쓴다. 이를 <strong>정규 nomination(regular nomination)</strong>이라 한다. controlled 쪽은 USE-CANDIDATE가 붙은 요청을 받았을 때 그 쌍이 이미 Succeeded면 즉시 nominated로 표시하고, 아니면 triggered check가 성공하는 순간 표시한다.

RFC 5245에는 <strong>aggressive nomination</strong>도 있었다. controlling이 처음부터 모든 체크에 USE-CANDIDATE를 붙여 첫 번째로 성공한 쌍을 바로 쓰는 방식이다. 빠르지만 더 좋은 쌍이 뒤늦게 성공하면 선택이 뒤집히는 등 양쪽 상태가 어긋나기 쉬웠다. <strong>RFC 8445는 aggressive nomination을 deprecated로 명시하고 정규 nomination만 남겼다.</strong>

실무에서 의미 있는 지점은 "controlling이 언제 nominate하느냐"가 구현 재량이라는 사실이다. 모든 체크를 기다리면 최선의 쌍을 고르지만 느리고, 쓸 만한 쌍이 나오자마자 nominate하면 빠르지만 차선일 수 있다. 같은 네트워크에서 브라우저와 디바이스 SDK 조합에 따라 연결 시간이 달라지는 원인 중 하나다.

### 연결 뒤에도 계속되는 체크

선택이 끝나도 STUN은 멈추지 않는다. <strong>consent freshness(RFC 7675)</strong>는 상대가 여전히 수신에 동의하는지 주기적으로 묻는다. 기본 5초를 0.8~1.2배로 흔든 간격(4~6초)으로 Binding 요청을 보내고, <strong>30초 동안 유효한 응답이 없으면 그 경로로의 전송을 중단</strong>해야 한다. 상대가 사라졌는데도 미디어를 계속 쏘는 일, 나아가 WebRTC가 트래픽 증폭 도구로 악용되는 일을 막는 장치다. 이 주기적 요청은 NAT 매핑을 살려 두는 keepalive 역할도 겸한다. 6절의 `disconnected` 상태는 이 체크가 실패할 때 나타난다.

## 4. Trickle ICE와 end-of-candidates

후보 수집은 공짜가 아니다. host는 즉시 나오지만 srflx·relay는 STUN·TURN 서버 왕복이 필요하다. TURN 서버 하나가 응답하지 않으면 타임아웃까지 기다려야 한다. 모든 후보를 모은 뒤 SDP에 담아 한 번에 보내는 방식(흔히 vanilla ICE라 부른다)은 가장 느린 서버가 연결 시간 전체를 결정한다.

<strong>Trickle ICE(RFC 8838)</strong>는 후보를 생기는 대로 시그널링으로 흘려보내고, 체크도 먼저 시작한다. host 후보끼리 통하는 환경이라면 TURN 할당이 끝나기도 전에 연결이 된다. 지원 여부는 SDP의 `a=ice-options:trickle`로 표시한다. JSEP를 따르는 브라우저는 기본으로 trickle을 쓴다.

- <strong>end-of-candidates</strong>는 "이 세대(ufrag/pwd 조합)에서 더 보낼 후보가 없다"는 표시다. 받는 쪽은 체크리스트를 확정할 수 있어 실패 판정을 빨리 내린다. SDP 속성 `a=end-of-candidates`는 RFC 8840에 정의돼 있다.
- <strong>half trickle</strong>은 offerer가 후보를 전부 모은 뒤 offer를 보내되 trickle 지원을 함께 표시하는 방식이다. 상대가 trickle을 지원하는지 모를 때 쓴다. answerer는 trickle로 응답할 수 있다.

브라우저 API에서는 후보 수집이 `icecandidate` 이벤트로 드러난다. 주의할 점이 두 가지 있다.

- `candidate` 문자열이 빈 문자열(`""`)인 이벤트가 end-of-candidates다. MDN은 이것을 일반 후보처럼 상대에게 전달하라고 안내한다.
- `event.candidate`가 `null`인 이벤트는 수집 완료를 알리는 하위 호환용이다. 상대에게 보낼 필요가 없다. 수집 완료는 `icegatheringstatechange`로 보는 편이 정확하다.

```js
const pc = new RTCPeerConnection({ iceServers });
const pendingCandidates = [];

pc.onicecandidate = ({ candidate }) => {
  // candidate가 null이면 수집 완료 → 전달 불필요
  // candidate.candidate === "" 인 end-of-candidates는 객체라서 그대로 전달된다
  if (candidate) {
    signaling.send({ type: 'candidate', candidate: candidate.toJSON() });
  }
};

signaling.onmessage = async (msg) => {
  if (msg.type === 'answer') {
    await pc.setRemoteDescription(msg);
    // remoteDescription 이전에 도착한 후보를 이제 적용한다
    for (const c of pendingCandidates.splice(0)) await pc.addIceCandidate(c);
  } else if (msg.type === 'candidate') {
    if (pc.remoteDescription) {
      await pc.addIceCandidate(msg.candidate);
    } else {
      pendingCandidates.push(msg.candidate); // 그냥 넣으면 InvalidStateError
    }
  }
};
```

`toJSON()`은 `candidate`·`sdpMid`·`sdpMLineIndex`·`usernameFragment`를 담는다. `sdpMid`와 `sdpMLineIndex`가 둘 다 빠지면 `addIceCandidate()`가 `TypeError`를 던지고, `usernameFragment`가 현재 원격 description과 맞지 않으면(이전 세대 후보) `OperationError`가 난다. 디바이스 쪽 시그널링 코드를 직접 짤 때 이 필드를 빠뜨려 "후보가 하나도 안 붙는" 장애가 흔하다.

Trickle에는 <strong>순서 문제</strong>가 따라온다. 후보가 answer보다 먼저 도착할 수 있고, 위 코드처럼 버퍼링해야 한다. WebSocket은 한 연결 안에서 순서를 보장하지만, MQTT QoS 1 재전송이나 HTTP 폴링을 섞으면 순서가 뒤집힐 수 있다([03장](/study/webrtc/03-signaling)). KVS 시그널링도 `ICE_CANDIDATE` 메시지로 후보를 trickle한다([18장](/study/webrtc/18-kvs-signaling-api)).

수집을 더 앞당기고 싶다면 `RTCPeerConnection`의 `iceCandidatePoolSize` 옵션으로 `setLocalDescription()` 전에 후보를 미리 모아 둘 수 있다. 운영자가 "영상 보기"를 누르기 전에 PeerConnection을 만들어 두는 UI라면 체감 연결 시간이 줄어든다.

## 5. ICE restart, mDNS 후보, ICE-lite

### ICE restart

연결이 성립한 뒤에도 경로가 깨질 수 있다. 창고 Wi-Fi에 붙어 있던 농기계가 밭으로 나가며 LTE로 넘어가면 디바이스 IP가 바뀌고, 기존 후보 쌍은 전부 죽는다. 이때 PeerConnection을 새로 만들지 않고 ICE만 다시 돌리는 것이 <strong>ICE restart</strong>다. RFC 8445는 restart를 "ufrag와 pwd를 모두 바꾸는 것"으로 정의한다. 새 자격증명이 오가면 양쪽은 이전 체크 상태를 버리고(역할은 유지) 후보 수집과 체크를 처음부터 다시 한다.

브라우저에서는 `restartIce()`를 호출한다.

```js
pc.addEventListener('negotiationneeded', async () => {
  await pc.setLocalDescription();           // 새 ice-ufrag/ice-pwd가 담긴 offer
  signaling.send(pc.localDescription);
});

// 네트워크 전환이나 failed를 감지했을 때
pc.restartIce();
```

`restartIce()`는 `negotiationneeded`를 발생시키고, 다음 `createOffer()`가 restart offer가 되게 한다. 협상이 롤백되거나 다른 offer와 겹쳐 실패해도 요청을 기억했다가 `signalingState`가 `stable`로 돌아올 때 다시 `negotiationneeded`를 낸다. 일회성으로 `createOffer({ iceRestart: true })`를 써도 된다. MDN에 따르면 restart 동안에도 기존 경로가 살아 있는 한 미디어는 끊기지 않는다.

<strong>설계상 주의할 점</strong>이 하나 있다. restart는 offer를 보내는 쪽이 시작한다. 시그널링이 한쪽만 offer를 보내도록 짜여 있다면(KVS에서는 뷰어가 offer를 보낸다) 디바이스는 스스로 restart offer를 만들 수 없다. 디바이스가 네트워크 변경을 감지하면 시그널링으로 "재시작해 달라"는 메시지를 보내고, 뷰어가 `restartIce()`를 호출하도록 프로토콜을 설계해 둬야 한다. 양쪽 모두 offer를 낼 수 있다면 [04장](/study/webrtc/04-sdp-jsep)의 Perfect Negotiation이 충돌을 정리한다.

### mDNS 후보

host 후보는 사설 IP를 그대로 드러낸다. 웹 페이지가 `RTCPeerConnection`만 만들면 방문자의 내부망 주소를 읽을 수 있어 핑거프린팅과 내부망 정찰에 악용됐다. 그래서 브라우저는 host 후보의 IP를 <strong>무작위 `.local` 이름</strong>으로 바꾼다. 이름은 UUID v4로 만들고 mDNS(multicast DNS)로 LAN에 광고한다.

```
a=candidate:1467250027 1 udp 2122260223 3f2b8c1e-6a0d-4e57-9a4f-0c1d2e3f4a5b.local 46243 typ host generation 0
```

규격은 IETF 드래프트 `draft-ietf-mmusic-mdns-ice-candidates`이며 RFC로 발행되지 않았다(-03판이 2022년에 만료됐다). Chrome과 Firefox는 <strong>getUserMedia 권한을 받지 않은 페이지</strong>에서 이 치환을 적용한다. 카메라·마이크 권한을 받은 페이지는 어차피 더 신뢰받는 상태로 보고 실제 IP를 노출한다.

농기계 원격 영상 시나리오에서 이 점이 중요하다. <strong>운영자 뷰어 페이지는 영상을 받기만 하므로 카메라 권한을 요청하지 않는다.</strong> 뷰어의 host 후보는 전부 `.local`이 된다. 디바이스의 ICE 스택이 mDNS를 해석하지 못하면 이 후보를 쓸 수 없다. 그래도 같은 LAN이면 대개 연결된다. 디바이스의 host 후보는 평범한 IP이므로 브라우저가 그쪽으로 체크를 보내고, 디바이스는 처음 보는 주소에서 온 요청을 <strong>원격 prflx</strong>로 학습해 triggered check를 돌린다. 그래서 getStats에 원격 후보가 `prflx`로 찍힌다면 이 상황을 의심하면 된다. 브라우저 쪽에서 디바이스 host 후보로 가는 패킷까지 막혀 있다면 srflx(공유기 hairpin 지원 필요)나 relay로 밀려나 같은 건물 안에서도 TURN 비용이 나온다.

### ICE-lite

<strong>ICE-lite</strong>는 공인 IP에 직접 붙은 서버용 간이 구현이다(RFC 8445 2.5절). lite 에이전트의 특징은 다음과 같다.

- host 후보만 쓴다(공인 IP라 STUN·TURN이 필요 없다).
- connectivity check를 <strong>보내지 않고 응답만</strong> 한다. 사실상 STUN 서버처럼 동작한다.
- 상태 머신을 유지하지 않는다.
- full 에이전트와 붙으면 <strong>항상 controlled</strong>다.

SDP 세션 레벨에 `a=ice-lite` 한 줄로 표시한다. SFU처럼 수천 개 연결을 받는 서버는 lite로 구현을 단순화하고 상태를 줄인다. mediasoup는 ICE-lite로 동작하고, Janus는 설정으로 lite 모드를 켤 수 있다([12장](/study/webrtc/12-topology-sfu)). 반대로 NAT 뒤에 있는 농기계 디바이스는 lite가 될 수 없다. 상대가 체크를 보내 올 공인 주소가 없기 때문이다.

## 6. 상태 머신과 실패 원인

ICE 진행 상황은 `RTCPeerConnection.iceConnectionState`로 드러난다. [02장](/study/webrtc/02-webrtc-api)에서 본 `connectionState`는 ICE와 DTLS를 합친 종합 상태라 사용자 화면에 쓰기 좋고, `iceConnectionState`는 경로 문제를 진단할 때 쓴다.

![iceConnectionState 상태 머신 — new에서 원격 후보가 들어오면 checking, 쌍 하나가 성공하면 connected, 모든 체크가 끝나면 completed로 가고, connected나 completed에서 consent/체크가 실패하면 disconnected로 갔다가 스스로 회복하거나 회복 실패 시 failed가 되며, checking에서 모든 쌍이 실패해도 failed가 되고, failed에서 restartIce()와 재협상으로 다시 checking으로 돌아가며 close()는 어느 상태에서든 closed로 보낸다](/images/study-webrtc/06-ice-states-light.png)
![iceConnectionState 상태 머신 — new에서 원격 후보가 들어오면 checking, 쌍 하나가 성공하면 connected, 모든 체크가 끝나면 completed로 가고, connected나 completed에서 consent/체크가 실패하면 disconnected로 갔다가 스스로 회복하거나 회복 실패 시 failed가 되며, checking에서 모든 쌍이 실패해도 failed가 되고, failed에서 restartIce()와 재협상으로 다시 checking으로 돌아가며 close()는 어느 상태에서든 closed로 보낸다](/images/study-webrtc/06-ice-states-dark.png)

| 상태 | 의미 | 운영 해석 |
|---|---|---|
| `new` | 후보 수집 중이거나 원격 후보를 기다림 | 오래 머물면 원격 후보가 안 들어오는 시그널링 문제 |
| `checking` | 체크 진행 중, 아직 통하는 쌍 없음 | 오래 머물면 방화벽이 체크를 삼키는 중 |
| `connected` | 모든 component에 쓸 수 있는 쌍을 찾음. 더 나은 쌍 체크는 계속될 수 있음 | 이 시점을 연결 성공으로 본다 |
| `completed` | 수집·체크가 모두 끝나고 모든 component에 연결이 있음 | 구현에 따라 이 상태를 거치지 않을 수 있어 기다리지 않는다 |
| `disconnected` | 최소 한 component에서 생존 확인이 실패 | 일시적일 수 있다. 바로 끊지 말고 잠시 기다린다 |
| `failed` | 모든 쌍을 체크했지만 통하는 쌍이 없음 | restart 또는 TURN 경로 점검 |
| `closed` | ICE 에이전트 종료 | `close()` 호출 후 |

`disconnected`는 MDN 표현대로 "불안정한 네트워크에서 간헐적으로 생겼다가 저절로 풀리는" 상태다. LTE 셀 핸드오버 몇 초 동안 잠깐 들어갔다 나오는 일이 흔하다. 바로 재연결하면 오히려 복구를 방해한다. 유예 시간을 두고, 그래도 안 풀리면 restart하는 패턴이 무난하다.

```js
let restartTimer;

pc.addEventListener('iceconnectionstatechange', () => {
  clearTimeout(restartTimer);
  switch (pc.iceConnectionState) {
    case 'disconnected':
      // 짧은 끊김은 스스로 회복하게 두고, 유예 후에도 그대로면 restart
      restartTimer = setTimeout(() => pc.restartIce(), 3000);
      break;
    case 'failed':
      pc.restartIce();
      break;
  }
});
```

유예 시간 3초는 예시다. 제어 명령을 보내는 원격 조작이라면 짧게, 단순 모니터링 영상이라면 길게 잡는다. restart를 몇 번 해도 `failed`가 반복되면 경로 자체가 없다는 뜻이므로 UI에 알리고 재시도 간격을 늘린다.

### 흔한 실패 원인

| 증상 | 원인 후보 | 확인 방법 | 대응 |
|---|---|---|---|
| `checking` → `failed`, 로컬 후보에 relay가 없음 | TURN 미설정, 자격증명 오류, TURN 서버 접근 차단 | `icecandidateerror` 이벤트의 `errorCode`(401이면 인증 실패, 701이면 서버 도달 불가) | [07장](/study/webrtc/07-turn)의 TURN 설정·자격증명 점검 |
| srflx끼리 체크가 전부 실패 | 양쪽 모두 symmetric NAT·CGNAT | 후보 목록에 srflx는 있으나 성공한 쌍이 없음 | TURN 필수. [05장](/study/webrtc/05-nat-stun) 참고 |
| UDP 후보 체크가 전부 실패 | 기업망·공공 Wi-Fi의 UDP 전면 차단 | relay UDP 할당도 실패, TCP 후보만 남음 | TURN over TCP/TLS 443 |
| `new`에서 진행이 없음 | 원격 후보가 안 붙음(시그널링 버그) | `addIceCandidate()` 예외(`InvalidStateError`·`OperationError`·`TypeError`) 로그 | 4절의 버퍼링과 `sdpMid`·`usernameFragment` 전달 |
| relay 후보는 있는데 relay 쌍도 실패 | coturn `external-ip` 누락으로 relay 주소가 사설 IP, relay 포트 범위가 보안 그룹에서 막힘 | relay 후보의 주소가 10.x·172.16~31.x인지 확인 | [07장](/study/webrtc/07-turn)의 coturn 배치 |
| 같은 LAN인데 relay로 연결됨 | mDNS `.local` 미해석, 공유기 hairpin 미지원 | 선택된 쌍의 후보 타입 | 디바이스 스택 mDNS 지원 확인, LAN 정책 점검 |
| `connected` 후 주기적 `disconnected` | LTE 핸드오버, CGNAT의 짧은 UDP 매핑 타임아웃 | 끊김 시각과 디바이스 네트워크 이벤트 대조 | 유예 후 restart, 디바이스 쪽 네트워크 변경 감지 시 restart 요청 |

진단의 출발점은 언제나 "후보가 어떻게 모였고 어느 쌍이 선택됐는가"다. `chrome://webrtc-internals`의 ICE candidate grid와 `getStats()`의 `candidate-pair`·`local-candidate`·`remote-candidate` 리포트로 이를 확인한다. 선택된 쌍을 뽑아 내는 코드는 [07장](/study/webrtc/07-turn)의 릴레이 비율 측정에서, 지표 전반은 [15장](/study/webrtc/15-monitoring-debugging)에서 다룬다.

::: tip 핵심 정리
- 후보는 host(로컬 NIC)·srflx(STUN이 본 NAT 주소)·prflx(체크 도중 발견)·relay(TURN이 빌려준 주소) 네 종류다. srflx의 base는 host이고 relay의 base는 자기 자신이다.
- 후보 우선순위는 `2^24·type pref + 2^8·local pref + (256 − component ID)`다. RFC 권장 type preference는 host 126, prflx 110, srflx 100, relay 0이며, libwebrtc는 relay를 UDP 2·TCP 1·TLS 0으로 나눈다.
- 쌍 우선순위 `2^32·MIN(G,D) + 2·MAX(G,D) + (G>D?1:0)`은 약한 쪽이 순위를 지배하게 하고, 역할 기준으로 정의해 양쪽이 같은 순서로 체크하게 만든다.
- connectivity check는 USERNAME·MESSAGE-INTEGRITY·PRIORITY·ICE-CONTROLLING/CONTROLLED가 붙은 STUN Binding이다. controlling이 USE-CANDIDATE로 정규 nomination을 하며, aggressive nomination은 RFC 8445에서 deprecated됐다.
- Trickle ICE(RFC 8838)는 후보를 생기는 대로 보내 연결 시간을 줄인다. end-of-candidates는 전달하고, remoteDescription 전에 온 후보는 버퍼링한다.
- 네트워크 전환에는 `restartIce()`로 대응한다. 뷰어 페이지의 host 후보는 mDNS `.local`로 가려지며, ICE-lite는 공인 IP 서버 전용이다.
- `disconnected`는 일시적일 수 있으니 유예 후 restart하고, `failed`가 반복되면 TURN 경로부터 점검한다.
:::

## 다음 챕터

[TURN](/study/webrtc/07-turn)에서는 ICE의 마지막 보루인 relay 후보를 만드는 TURN 프로토콜의 메시지 흐름(Allocate·CreatePermission·ChannelBind), 방화벽을 넘기 위한 TLS 443 전송, 시간제한 credential 발급, coturn 설정과 배치, 그리고 릴레이 비율에 따른 트래픽 비용 산정을 다룬다.
