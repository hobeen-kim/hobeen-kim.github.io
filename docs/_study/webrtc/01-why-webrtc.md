---
title: "왜 WebRTC인가"
description: "실시간 미디어가 요구하는 지연·양방향성을 기준으로 HLS·LL-HLS·RTMP·WebSocket과 WebRTC를 비교하고, 브라우저 API와 IETF 프로토콜 스택으로 이뤄진 WebRTC의 구성과 표준화 역사, 사용 사례를 개관한다."
date: 2026-10-19
tags: [WebRTC, Streaming, Latency]
prev: /study/webrtc/
next: /study/webrtc/02-webrtc-api
---

# 왜 WebRTC인가

::: info 학습 목표
- "실시간"이 스트리밍과 무엇이 다른지 지연·양방향성·손실 처리 관점으로 설명할 수 있다.
- HLS·LL-HLS·RTMP·WebSocket 기반 전송과 WebRTC의 지연 범위를 비교하고, 각 방식이 느리거나 빠른 구조적 이유를 안다.
- WebRTC가 브라우저 API와 IETF 프로토콜 묶음으로 이뤄져 있고, 시그널링 경로와 미디어 경로가 분리돼 있음을 이해한다.
- 2011년 공개부터 2021년 표준 확정까지의 흐름과, 그 과정이 오늘날 코드에 남긴 흔적을 안다.
- 농기계·로봇 원격 영상 같은 사례에서 WebRTC가 맞는 지점과 맞지 않는 지점을 판단할 수 있다.
:::

## 1. 실시간 미디어가 요구하는 것

"영상을 보여준다"는 요구는 겉으로 같아 보여도 두 종류로 갈린다. 하나는 <strong>시청</strong>이다. 축구 중계나 농장 홍보 라이브처럼 시청자가 화면을 보기만 하면, 영상이 10초 늦게 도착해도 아무도 모른다. 대신 수만 명에게 끊김 없이 뿌리는 것이 중요하다. 다른 하나는 <strong>상호작용</strong>이다. 화상회의, 원격 조종, 원격 진료처럼 화면을 본 사람이 곧바로 반응하고 그 반응이 다시 화면에 돌아와야 하는 경우다. 이때는 지연 자체가 기능을 망가뜨린다.

농기계 원격 운영을 예로 들어보자. 트랙터가 시속 10 km로 움직이면 초당 약 2.8 m를 간다. 운영자 화면이 3초 늦다면 운영자는 이미 8 m 넘게 지나간 장면을 보고 있는 셈이다. 장애물을 보고 정지 버튼을 눌러도 그 명령이 디바이스에 닿을 때까지의 제어 지연이 또 더해진다. 원격 조작에서 중요한 것은 영상 지연 하나가 아니라 <strong>"보고 → 판단하고 → 명령이 도착할 때까지"의 루프 전체</strong>다.

사람의 대화 기준으로는 ITU-T G.114가 자주 인용된다. 단방향 지연 150 ms 이하면 대부분의 응용에서 지연을 거의 느끼지 못하고, 일반적인 망 설계에서는 400 ms를 넘기지 말라고 권고한다. 원격 조작도 대략 이 범위, 즉 <strong>수백 ms 이하</strong>를 목표로 잡는다.

실시간 미디어가 요구하는 것을 정리하면 다음과 같다.

| 요구 | 의미 | 시청형 스트리밍과의 차이 |
|---|---|---|
| 낮은 지연 | 캡처부터 화면 표시까지(glass-to-glass) 수백 ms 이하 | 시청형은 수 초~수십 초 허용 |
| 양방향 | 영상·음성·데이터가 양쪽으로 흐른다 | 시청형은 단방향 |
| 손실 내성 | 늦게 온 패킷은 버리고 다음 프레임으로 넘어간다 | 시청형은 버퍼를 늘려 손실을 숨긴다 |
| 네트워크 적응 | 대역폭이 줄면 화질을 낮춰서라도 지연을 지킨다 | 시청형은 화질 단계(ABR)를 바꾸되 버퍼로 흡수 |
| NAT 통과 | 사설망 뒤 두 단말이 직접 연결 | 시청형은 클라이언트→CDN 단방향 접속이면 충분 |
| 암호화 | 미디어 전 구간 암호화 | HTTPS로 충분 |

핵심은 세 번째 줄이다. 실시간 미디어에서는 <strong>늦게 도착한 패킷은 잃어버린 패킷과 같다</strong>. 200 ms 전 프레임의 조각이 지금 도착해 봐야 이미 그 다음 프레임을 그려야 할 시점이다. TCP는 손실된 세그먼트를 재전송하고, 그 세그먼트가 도착할 때까지 뒤의 데이터를 애플리케이션에 넘기지 않는다(Head-of-Line blocking). 신뢰성을 보장하는 이 성질이 실시간 미디어에는 정확히 반대로 작용한다. 손실 한 번에 뒤따르는 모든 프레임이 함께 늦어지고, 그 지연은 버퍼에 누적된다.

그래서 WebRTC는 미디어를 UDP 위에 올리고, 손실 복구(NACK 재전송 요청·FEC)와 혼잡 제어를 미디어 계층에서 직접 한다. "얼마나 기다렸다가 포기할지"를 애플리케이션이 결정할 수 있다는 것이 UDP를 쓰는 진짜 이유다. 손실 복구와 혼잡 제어는 [09장](/study/webrtc/09-quality-latency)에서 자세히 다룬다.

## 2. 기존 방식과 지연 비교

영상을 브라우저에 보내는 기존 방식들과 WebRTC의 지연 범위를 나란히 놓으면 다음과 같다. 수치는 인코더 설정·세그먼트 길이·네트워크·플레이어 버퍼에 따라 크게 달라지는 <strong>대략적인 범위</strong>다.

![전송 방식별 지연 범위를 로그 스케일 막대로 비교한 그림. WebRTC는 약 100~500 ms로 G.114 대화 지연 기준선(150 ms, 400 ms) 근처에 있고, RTMP 송출 구간은 1~5초, LL-HLS는 2~5초, 6초 세그먼트 HLS는 10~30초 범위에 있다](/images/study-webrtc/01-latency-spectrum-light.png)
![전송 방식별 지연 범위를 로그 스케일 막대로 비교한 그림. WebRTC는 약 100~500 ms로 G.114 대화 지연 기준선(150 ms, 400 ms) 근처에 있고, RTMP 송출 구간은 1~5초, LL-HLS는 2~5초, 6초 세그먼트 HLS는 10~30초 범위에 있다](/images/study-webrtc/01-latency-spectrum-dark.png)

| 방식 | 전송 | 대략적 지연 | 방향 | 브라우저 재생 | 주 용도 |
|---|---|---|---|---|---|
| HLS | HTTP(TCP), 세그먼트 파일 | 10~30초 | 단방향 | Safari 등 일부 네이티브, 그 외 MSE(hls.js 등) | 대규모 방송, VOD |
| LL-HLS | HTTP(TCP), partial segment | 2~5초 | 단방향 | 위와 동일(플레이어 지원 필요) | 저지연 방송 |
| RTMP | TCP(기본 1935 포트) | 송출 구간 1~5초 | 단방향 | 불가(Flash 종료) | 인코더→서버 송출(ingest) |
| WebSocket + MSE | TCP, 자체 프레이밍 | 구현에 따라 수백 ms~수 초 | 양방향 가능 | MSE로 직접 구현 | 사내 도구, 레거시 |
| WebRTC | UDP(SRTP), 직접 또는 릴레이 | 수백 ms 미만 | 양방향 | 네이티브 | 회의, 원격 제어, 인터랙티브 방송 |

각 방식이 왜 이 범위에 있는지를 구조로 이해해두면, 나중에 "LL-HLS를 더 짧게 쪼개면 WebRTC만큼 되지 않나?" 같은 질문에 답할 수 있다.

<strong>HLS가 느린 이유</strong>는 세그먼트 단위로 일하기 때문이다. 인코더가 영상을 몇 초짜리 파일(세그먼트)로 잘라 올리고, 플레이어는 플레이리스트를 받아 세그먼트를 순서대로 내려받는다. Apple의 저작 가이드는 6초 세그먼트를 권장하고, HLS 명세(RFC 8216)는 클라이언트가 플레이리스트 끝에서 <strong>세 개의 목표 길이(target duration) 이내</strong>인 세그먼트로 재생을 시작하지 말라고 한다. 6초 세그먼트라면 플레이어는 최소 18초쯤 뒤처진 지점에서 시작하는 셈이고, 여기에 인코딩·패키징·CDN 전파 시간이 더해져 10~30초가 된다. AWS IVS 문서도 전통적인 OTT 스트림의 지연을 최대 30초 수준으로 언급한다.

<strong>LL-HLS</strong>는 세그먼트를 수백 ms 단위의 partial segment로 쪼개고, 플레이어가 다음 조각이 준비될 때까지 플레이리스트 요청을 서버에 걸어두는 blocking playlist reload와 preload hint로 폴링 지연을 없앴다. 그래도 HTTP 요청-응답 왕복, TCP 재전송, 플레이어가 안전하게 재생하려고 유지하는 몇 개 조각 분량의 버퍼가 남는다. 실무 수치는 대략 2~5초다. AWS IVS의 저지연(Low-Latency) 채널도 5초 미만을 내세운다.

<strong>RTMP</strong>는 원래 Flash 플레이어로 재생까지 하던 프로토콜이지만 Flash가 2020년 말 지원 종료되면서 지금은 거의 <strong>송출(ingest) 전용</strong>이다. OBS 같은 인코더가 RTMP로 미디어 서버에 영상을 올리면, 서버가 이를 HLS로 다시 포장해 시청자에게 뿌린다. 즉 시청자가 느끼는 지연은 결국 HLS 지연이다. RTMP 구간 자체도 TCP 위라 손실이 나면 HOL blocking으로 지연이 쌓인다.

<strong>WebSocket으로 직접 프레임을 보내는 방식</strong>(서버가 H.264 조각이나 fMP4를 WebSocket으로 밀고 브라우저가 MSE로 재생)은 세그먼트를 기다리지 않으니 HLS보다 빠를 수 있다. 하지만 TCP 위라는 한계가 그대로 남는다. 패킷 손실이 생기면 재전송이 끝날 때까지 뒤 프레임이 전부 멈추고, 혼잡하면 송신 버퍼에 프레임이 쌓여 지연이 계속 늘어난다. 프레임을 버리는 로직, 대역폭 추정, NAT 통과, 암호화, 지터 버퍼를 모두 직접 짜야 한다. 이 목록을 다 구현하면 결국 WebRTC를 다시 만드는 일이 된다.

<strong>WebRTC</strong>는 처음부터 상호작용을 목표로 설계됐다. UDP 위에서 늦은 패킷은 버리고, 대역폭이 줄면 인코더 비트레이트를 즉시 낮추며, 수신 측 지터 버퍼도 수십~수백 ms 수준으로 작게 유지한다. AWS IVS Real-Time(WebRTC 기반)은 300 ms 미만 지연을 내세운다. 같은 지역 안 P2P 연결이라면 수백 ms보다 훨씬 낮은 값도 흔히 나온다.

::: warning WebRTC가 공짜로 빠른 것은 아니다
WebRTC의 낮은 지연은 몇 가지를 포기한 대가다.

- <strong>CDN을 그대로 쓸 수 없다.</strong> HLS는 파일이라 CDN 캐시로 수만 명에게 뿌리는 비용이 싸다. WebRTC는 시청자마다 별도 연결이 필요하고, 다수에게 보내려면 SFU 같은 미디어 서버가 있어야 한다([12장](/study/webrtc/12-topology-sfu)).
- <strong>화질보다 지연이 먼저다.</strong> 네트워크가 나빠지면 버퍼를 늘리는 대신 해상도·프레임레이트를 깎는다. 녹화 품질이 중요한 용도라면 별도 녹화 경로가 필요하다([21장](/study/webrtc/21-kvs-ingestion-storage)).
- <strong>네트워크 복잡도가 높다.</strong> NAT·방화벽을 넘기 위해 STUN/TURN이 필요하고, TURN 릴레이는 트래픽 비용이 든다([07장](/study/webrtc/07-turn)).

그래서 "다수가 보기만 한다"면 HLS/LL-HLS가, "소수가 보고 반응한다"면 WebRTC가 맞다. 농기계 원격 운영은 운영자 소수가 실시간으로 보고 조작하는 전형적인 후자다. 반면 같은 농장의 수확 축제 라이브는 HLS로 충분하다.
:::

## 3. WebRTC의 구성 — 브라우저 API + 프로토콜 스택

WebRTC라는 이름은 사실 두 표준 묶음을 함께 가리킨다.

- <strong>W3C가 정의한 JavaScript API</strong>: 카메라·마이크를 얻는 `getUserMedia`(Media Capture and Streams 명세), 피어 연결을 다루는 `RTCPeerConnection`, 임의 데이터를 보내는 `RTCDataChannel`이 핵심이다. [02장](/study/webrtc/02-webrtc-api)에서 다룬다.
- <strong>IETF가 정의한 프로토콜 묶음</strong>: 세션 기술(SDP), NAT 통과(ICE·STUN·TURN), 암호화(DTLS-SRTP), 미디어 전송(RTP/RTCP), 데이터 전송(SCTP)이 어떤 조합으로 어떻게 동작해야 하는지를 정한다. 브라우저든 디바이스든 이 프로토콜만 지키면 서로 통신할 수 있다.

### 두 개의 경로: 시그널링과 미디어

WebRTC를 처음 접할 때 가장 헷갈리는 지점이 "P2P라면서 왜 서버가 필요한가"다. 답은 <strong>경로가 두 개</strong>라는 데 있다.

![시그널링 경로와 미디어 경로가 분리된 구조. 위쪽 시그널링 서버(WebSocket·HTTPS)를 통해 농기계 디바이스와 운영자 브라우저가 SDP와 ICE 후보를 주고받고, 아래쪽에서는 두 피어가 SRTP와 SCTP/DTLS로 UDP 직접 연결을 맺으며, 직접 연결이 실패하면 STUN/TURN 서버를 거쳐 릴레이한다](/images/study-webrtc/01-two-paths-light.png)
![시그널링 경로와 미디어 경로가 분리된 구조. 위쪽 시그널링 서버(WebSocket·HTTPS)를 통해 농기계 디바이스와 운영자 브라우저가 SDP와 ICE 후보를 주고받고, 아래쪽에서는 두 피어가 SRTP와 SCTP/DTLS로 UDP 직접 연결을 맺으며, 직접 연결이 실패하면 STUN/TURN 서버를 거쳐 릴레이한다](/images/study-webrtc/01-two-paths-dark.png)

- <strong>시그널링 경로</strong>는 연결을 맺기 전에 "나는 이런 코덱을 쓸 수 있고(SDP), 이 주소들로 연락하면 된다(ICE 후보)"는 정보를 교환하는 길이다. 두 피어는 아직 서로의 주소를 모르므로 둘 다 접속할 수 있는 서버가 중개해야 한다. WebRTC 표준은 이 경로를 <strong>일부러 정의하지 않았다</strong>. WebSocket을 쓰든 HTTP를 쓰든 MQTT를 쓰든 애플리케이션 마음이다([03장](/study/webrtc/03-signaling)).
- <strong>미디어 경로</strong>는 실제 영상·음성·데이터가 흐르는 길이다. 시그널링으로 교환한 후보 주소들 중 통하는 쌍을 ICE가 찾아내면, 그 경로로 DTLS 핸드셰이크를 하고 SRTP와 SCTP로 미디어와 데이터를 보낸다. NAT 때문에 직접 연결이 안 되면 TURN 서버가 패킷을 중계한다.

백엔드 개발자 입장에서 이 분리는 중요하다. 시그널링 서버는 연결 수립 순간에만 작은 JSON 몇 개를 나르므로 부하가 작다. 반면 미디어는 연결이 유지되는 내내 초당 수 Mbps를 흘린다. P2P가 성공하면 미디어 트래픽은 서버를 아예 거치지 않는다. 서버 비용 구조가 "시그널링은 연결 수에 비례, 미디어는 TURN 릴레이 비율에 비례"로 갈리는 이유다.

### 프로토콜 스택

두 경로의 프로토콜 계층을 나란히 놓으면 다음과 같다.

![시그널링 스택과 미디어 스택 비교. 시그널링은 IP·TCP·TLS·WebSocket/HTTPS 위에 SDP·ICE 후보·방 입퇴장을 담은 앱 JSON 메시지가 올라간다. 미디어는 IP·UDP·ICE(STUN·TURN) 위에, 왼쪽에는 SRTP/SRTCP가 ICE 위에 바로 얹혀 오디오·비디오 트랙을 나르고, 오른쪽에는 DTLS 위에 SCTP와 DataChannel이 올라가며, DTLS에서 SRTP로 키를 도출하는 화살표가 있다](/images/study-webrtc/01-protocol-stack-light.png)
![시그널링 스택과 미디어 스택 비교. 시그널링은 IP·TCP·TLS·WebSocket/HTTPS 위에 SDP·ICE 후보·방 입퇴장을 담은 앱 JSON 메시지가 올라간다. 미디어는 IP·UDP·ICE(STUN·TURN) 위에, 왼쪽에는 SRTP/SRTCP가 ICE 위에 바로 얹혀 오디오·비디오 트랙을 나르고, 오른쪽에는 DTLS 위에 SCTP와 DataChannel이 올라가며, DTLS에서 SRTP로 키를 도출하는 화살표가 있다](/images/study-webrtc/01-protocol-stack-dark.png)

그림에서 눈여겨볼 점은 <strong>SRTP가 DTLS 위에 있지 않다</strong>는 것이다. DTLS는 핸드셰이크로 키를 합의하는 데 쓰이고(DTLS-SRTP), 실제 미디어 패킷은 그 키로 암호화된 SRTP로 DTLS를 거치지 않고 바로 나간다. 반면 DataChannel은 SCTP 패킷을 DTLS 레코드로 감싸서 보낸다. 미디어에 DTLS 레코드 오버헤드를 붙이지 않으면서 키 교환은 TLS 계열의 검증된 방식을 쓰려는 설계다.

| 계층 | 프로토콜 | 대표 RFC | 역할 | 다루는 장 |
|---|---|---|---|---|
| 세션 기술 | SDP, JSEP | RFC 8866, RFC 9429 | 코덱·전송 파라미터를 기술하고 offer/answer로 합의 | [04장](/study/webrtc/04-sdp-jsep) |
| NAT 통과 | ICE, STUN, TURN | RFC 8445, RFC 8489, RFC 8656 | 통하는 주소 쌍 찾기, 공인 주소 확인, 릴레이 | [05](/study/webrtc/05-nat-stun)·[06](/study/webrtc/06-ice)·[07장](/study/webrtc/07-turn) |
| 미디어 | RTP/RTCP, SRTP | RFC 3550, RFC 3711 | 미디어 패킷화·타이밍·품질 피드백, 암호화 | [08장](/study/webrtc/08-rtp-codecs) |
| 키 교환 | DTLS-SRTP | RFC 5764 | 핸드셰이크와 인증서 지문 검증으로 SRTP 키 합의 | [10장](/study/webrtc/10-dtls-srtp) |
| 데이터 | SCTP over DTLS, DCEP | RFC 8261, RFC 8831, RFC 8832 | 신뢰성·순서를 선택할 수 있는 메시지 채널 | [11장](/study/webrtc/11-datachannel) |

몇 가지 설계 결정이 스택 전체에 영향을 준다.

- <strong>암호화는 선택이 아니다.</strong> WebRTC 보안 아키텍처(RFC 8827)는 미디어를 SRTP로, 데이터를 DTLS로 보호하도록 요구하고, 평문 RTP는 허용하지 않는다. 브라우저에서 암호화를 끌 방법이 없다.
- <strong>한 포트로 전부 보낸다.</strong> BUNDLE(RFC 8843)과 rtcp-mux(RFC 5761)를 쓰면 오디오·비디오·RTCP·DataChannel이 하나의 UDP 5-tuple을 공유한다. 수신 측은 패킷 첫 바이트 값으로 STUN·DTLS·SRTP를 구분한다(RFC 7983). NAT 바인딩과 ICE 점검을 한 번만 하면 되니 연결이 빠르고 방화벽 규칙도 단순해진다.
- <strong>필수 코덱이 정해져 있다.</strong> 브라우저는 비디오로 VP8과 H.264 Constrained Baseline을 모두 지원해야 하고(RFC 7742), 오디오로 Opus와 G.711을 지원해야 한다(RFC 7874). 디바이스가 하드웨어 H.264 인코더만 갖고 있어도 브라우저와 통할 수 있는 근거다([08장](/study/webrtc/08-rtp-codecs)).

## 4. 표준화 역사

WebRTC는 한 회사의 코드 공개에서 시작해 두 표준 기구가 10년 가까이 다듬은 결과물이다.

| 시점 | 사건 |
|---|---|
| 2010년 5월 | Google이 VoIP·화상회의 엔진 업체 Global IP Solutions(GIPS)를 약 6,820만 달러에 인수. 에코 캔슬링·지터 버퍼·음성 코덱(iSAC 등) 기술 확보 |
| 2011년 6월 초 | Google이 GIPS 기술 기반 실시간 통신 코드를 BSD 라이선스로 공개(WebRTC 프로젝트) |
| 2011년 | W3C에 Web Real-Time Communications Working Group, IETF에 RTCWEB Working Group 출범. API는 W3C, 프로토콜은 IETF가 나눠 맡음 |
| 2013년 2월 | Chrome과 Firefox 사이 첫 플러그인 없는 영상 통화 시연(VP8·Opus·DTLS-SRTP·ICE) |
| 2017년 | Safari 11(macOS·iOS)이 WebRTC를 지원하면서 주요 브라우저 전부가 지원 |
| 2019년 | Chrome 72가 표준 SDP 형식인 Unified Plan을 기본값으로 전환(이전 Chrome 전용 형식은 Plan B) |
| 2021년 1월 | IETF가 WebRTC 핵심 RFC 묶음(RFC 8825~8835) 발행. 같은 달 26일 W3C가 WebRTC 1.0을 W3C Recommendation으로 확정 |
| 2024년 4월 | JSEP 개정판 RFC 9429 발행(RFC 8829 대체) |
| 2025년 3월 | HTTP 기반 인제스트 시그널링 WHIP가 RFC 9725로 발행. W3C WebRTC 명세도 후보 수정(candidate amendments)을 포함한 개정 Recommendation으로 갱신 |

2021년 1월 IETF 묶음의 구성은 다음과 같다. 나중 장에서 근거를 찾을 때 이 번호들을 자주 만난다.

| RFC | 제목 | 한 줄 요약 |
|---|---|---|
| 8825 | Overview: Real-Time Protocols for Browser-Based Applications | 전체 개요, 어떤 RFC가 무엇을 담당하는지 지도 |
| 8826 | Security Considerations for WebRTC | 위협 모델 |
| 8827 | WebRTC Security Architecture | 보안 아키텍처(DTLS-SRTP 필수 등) |
| 8828 | WebRTC IP Address Handling Requirements | 로컬 IP 노출 정책 |
| 8829 | JavaScript Session Establishment Protocol (JSEP) | offer/answer 모델(2024년 RFC 9429로 대체) |
| 8830 | WebRTC MediaStream Identification in SDP | msid 속성 |
| 8831 | WebRTC Data Channels | DataChannel 요구사항 |
| 8832 | WebRTC Data Channel Establishment Protocol | DataChannel 개설 프로토콜(DCEP) |
| 8833 | ALPN for WebRTC | DTLS ALPN 식별자 |
| 8834 | Media Transport and Use of RTP in WebRTC | RTP 사용 규칙 |
| 8835 | Transports for WebRTC | 전송 계층 요구사항(ICE·TURN·DTLS) |

10년이나 걸린 이유는 기술보다 합의에 있었다. 필수 비디오 코덱을 VP8로 할지 H.264로 할지 오래 다투다 "브라우저는 둘 다 지원"으로 타협했다(RFC 7742). SDP 문자열을 주고받는 모델 대신 객체 API로 가자는 ORTC 진영과의 논쟁 끝에, SDP는 유지하되 `RTCRtpTransceiver`·`RTCRtpSender` 같은 객체 API를 1.0에 흡수했다. 한 m-line에 여러 트랙을 넣던 Chrome의 Plan B와 트랙마다 m-line을 쓰는 Unified Plan의 대립은 Unified Plan으로 정리됐다.

::: warning 오래된 예제 코드의 함정
표준이 오래 흔들린 탓에 검색으로 찾은 예제 상당수가 지금 브라우저에서 동작하지 않거나 경고를 낸다. 다음 패턴이 보이면 2015~2018년 무렵 코드라고 보고 걸러낸다.

- `webkitRTCPeerConnection`, `mozRTCPeerConnection` 같은 접두사 생성자
- `pc.addStream()` / `pc.onaddstream` — 표준은 `addTrack()` / `ontrack`
- `createOffer(successCallback, failureCallback)` 같은 콜백 스타일 — 표준은 Promise
- `navigator.getUserMedia` — 표준은 `navigator.mediaDevices.getUserMedia`
- `sdpSemantics: 'plan-b'` 설정 — Plan B는 Chrome에서 제거됐다

브라우저 차이를 메우는 adapter.js가 여전히 쓰이지만, 최신 브라우저만 대상으로 한다면 표준 API만으로 충분하다.
:::

## 5. 사용 사례

WebRTC가 실제로 쓰이는 곳을 토폴로지와 미디어 방향으로 나눠 보면 각 사례에 필요한 구성 요소가 보인다.

| 사례 | 토폴로지 | 미디어 방향 | 핵심 요구 | 관련 장 |
|---|---|---|---|---|
| 1:1 화상 통화 | P2P | 양방향 영상·음성 | NAT 통과, 에코 캔슬링 | 05~07장 |
| 다자 화상회의 | SFU | 양방향, 참가자 N명 | Simulcast, 대역폭 적응 | [12장](/study/webrtc/12-topology-sfu), [23장](/study/webrtc/23-chime-sdk) |
| 원격 로봇·농기계 제어 | P2P 또는 SFU | 디바이스→운영자 영상, 양방향 제어 데이터 | 저지연, 제어 채널 신뢰성, 디바이스 구현 | [11장](/study/webrtc/11-datachannel), [13장](/study/webrtc/13-native-webrtc) |
| CCTV·IP 카메라 실시간 보기 | P2P(관리형 시그널링) | 카메라→시청자 | 디바이스 상시 대기, 녹화 병행 | [17장](/study/webrtc/17-kvs-architecture), [21장](/study/webrtc/21-kvs-ingestion-storage) |
| 인터랙티브 라이브 방송 | SFU + 서버 측 합성 | 소수 발표자→다수 시청자 | 1:N 확장, 표준 인제스트 | [14장](/study/webrtc/14-whip-whep), [24장](/study/webrtc/24-ivs-real-time) |
| 원격 데스크톱·클라우드 게임 | P2P 또는 서버 | 서버→사용자 영상, 사용자→서버 입력 | 초저지연, 입력 데이터 채널 | 09장, 11장 |

Google Meet, Discord 음성 채널처럼 이미 익숙한 서비스 상당수가 WebRTC 위에서 돈다. 이 스터디가 집중하는 사례는 세 번째 줄, <strong>카메라 달린 농기계·로봇을 운영자 브라우저에서 실시간으로 보고 제어하는 시나리오</strong>다. 이 사례는 일반 화상회의와 몇 가지가 다르다.

- <strong>미디어가 대부분 단방향이다.</strong> 디바이스가 영상을 보내고 운영자는 받기만 한다. 운영자 브라우저에는 카메라가 없어도 되고, 수신 전용(`recvonly`) 트랜시버로 연결한다([02장](/study/webrtc/02-webrtc-api)).
- <strong>송신자가 브라우저가 아니다.</strong> 디바이스에는 브라우저가 없으니 네이티브 WebRTC 스택이 필요하다(6절).
- <strong>업링크가 약하다.</strong> 들판의 디바이스는 LTE로 붙고, 업로드 대역폭이 들쭉날쭉하며 CGNAT 뒤에 있는 경우가 많다. NAT 통과와 비트레이트 적응이 회의보다 훨씬 중요하다([05장](/study/webrtc/05-nat-stun), [09장](/study/webrtc/09-quality-latency)).
- <strong>제어 데이터가 따라붙는다.</strong> 영상과 함께 정지·조향 같은 명령이 오간다. DataChannel로 보낼지 MQTT로 보낼지는 신뢰성·지연·감사 요구로 판단한다([11장](/study/webrtc/11-datachannel)).
- <strong>디바이스가 먼저 기다린다.</strong> 회의는 사람이 접속해서 시작하지만, 디바이스는 켜지면 시그널링 채널에 붙어 "누가 보러 올 때까지" 대기한다. AWS KVS WebRTC의 Master/Viewer 모델이 이 구조다([17장](/study/webrtc/17-kvs-architecture)).

## 6. 브라우저 밖의 WebRTC

WebRTC는 이름에 "Web"이 붙어 있지만, 프로토콜은 브라우저 전용이 아니다. 앞의 프로토콜 스택만 지키면 어떤 프로그램이든 브라우저와 미디어를 주고받을 수 있다. 디바이스에서 쓸 수 있는 대표적인 구현은 다음과 같다.

| 구현 | 언어 | 특징 |
|---|---|---|
| libwebrtc | C++ | Chrome에 들어간 바로 그 코드. 기능이 가장 완전하지만 빌드가 무겁고 크다 |
| Pion | Go | 순수 Go 구현. 크로스 컴파일이 쉽고 서버·디바이스 양쪽에 많이 쓰인다 |
| GStreamer webrtcbin | C(GStreamer 플러그인) | 기존 GStreamer 미디어 파이프라인에 WebRTC 송수신을 끼워 넣는다 |
| aiortc | Python | asyncio 기반. 프로토타입·테스트 도구에 적합 |
| Amazon KVS WebRTC C SDK | C | 임베디드용 경량 구현 + KVS 관리형 시그널링·TURN 연동 |

디바이스 측 구현이 브라우저와 가장 크게 다른 점은 <strong>미디어 소스</strong>다. 브라우저는 `getUserMedia`가 카메라를 열고 소프트웨어 인코더가 알아서 압축하지만, 디바이스는 V4L2로 카메라를 열고 Jetson의 NVENC나 SoC의 하드웨어 H.264 인코더로 인코딩한 결과를 WebRTC 스택에 밀어 넣어야 한다. CPU가 약한 임베디드 보드에서 소프트웨어 인코딩으로 720p 30fps를 버티기는 어렵기 때문이다. 메모리 제약, 크로스 컴파일, 시계 동기(인증서 유효기간 검증에 정확한 시각이 필요하다) 같은 임베디드 특유의 함정도 있다.

그래도 시그널링만 맞추면 브라우저와 그대로 통신한다는 점은 변하지 않는다. 디바이스 구현 선택지와 파이프라인 예제는 [13장](/study/webrtc/13-native-webrtc)에서, AWS 관리형 환경에 맞춘 KVS C SDK는 [19장](/study/webrtc/19-kvs-c-sdk)에서 다룬다.

::: tip 핵심 정리
- 실시간 미디어는 지연·양방향성이 기능의 일부다. 늦게 온 패킷은 잃어버린 패킷과 같으므로, WebRTC는 TCP 대신 UDP 위에서 손실 복구와 혼잡 제어를 직접 한다.
- HLS는 세그먼트·플레이어 버퍼 구조 때문에 10~30초, LL-HLS는 2~5초, RTMP는 송출 전용이며, WebRTC는 수백 ms 미만을 목표로 한다. 대신 CDN을 쓸 수 없고 화질보다 지연을 우선한다.
- WebRTC는 W3C API와 IETF 프로토콜 묶음이다. 시그널링 경로는 표준이 없고(앱 몫), 미디어 경로는 ICE·DTLS-SRTP·RTP·SCTP로 표준화돼 있다. SRTP는 DTLS가 합의한 키를 쓰지만 DTLS 위에 얹히지 않는다.
- 2011년 Google 공개 후 2021년 1월 W3C Recommendation과 RFC 8825~8835로 표준이 확정됐고, 이후 JSEP(RFC 9429)·WHIP(RFC 9725)가 추가됐다. 오래된 예제의 `addStream`·콜백 API·Plan B는 걸러낸다.
- 농기계·로봇 원격 영상은 단방향 미디어, 네이티브 송신자, 약한 LTE 업링크, 제어 데이터, 디바이스 상시 대기라는 특성을 가진다.
:::

## 다음 챕터

[WebRTC API 한눈에](/study/webrtc/02-webrtc-api)에서는 `getUserMedia`·`RTCPeerConnection`·`RTCRtpTransceiver`·`RTCDataChannel`의 역할과 연결 상태 값을 정리하고, 한 페이지 안에서 두 PeerConnection을 연결하는 loopback 예제를 직접 돌려본다.
