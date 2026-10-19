---
title: "RTP/RTCP와 코덱"
description: "WebRTC 미디어가 실제로 실려 가는 RTP 헤더와 RTCP 보고·피드백, 헤더 확장, 브라우저 필수 코덱(VP8·H.264·Opus)과 H.264 RTP 패킷화(Single NAL·STAP-A·FU-A), 지터 버퍼와 립싱크, 디바이스에서의 하드웨어 인코더와 코덱 선택을 다룬다."
date: 2026-10-19
tags: [WebRTC, RTP, RTCP, H.264, Opus, Codec]
prev: /study/webrtc/07-turn
next: /study/webrtc/09-quality-latency
---

# RTP/RTCP와 코덱

::: info 학습 목표
- RTP 고정 헤더의 각 필드(V·P·X·CC·M·PT·seq·timestamp·SSRC)가 무엇을 위해 있는지, 비디오 90kHz·Opus 48kHz 클럭이 timestamp에 어떻게 반영되는지 설명할 수 있다.
- RTCP SR/RR/SDES/BYE와 피드백 메시지(RTPFB·PSFB)의 역할을 구분하고, RR 하나로 손실률·지터·RTT를 계산하는 방법을 안다.
- abs-send-time·transport-cc 같은 헤더 확장이 왜 필요한지, SDP의 `a=extmap`과 어떻게 연결되는지 안다.
- RFC 7742·7874가 정한 브라우저 필수 코덱과, H.264의 profile-level-id·packetization-mode가 협상에서 갖는 의미를 이해한다.
- H.264 NAL unit이 Single NAL·STAP-A·FU-A로 RTP에 실리는 과정을 따라가고, 지터 버퍼와 립싱크(SR의 NTP↔RTP 매핑)의 동작을 설명할 수 있다.
- 카메라 달린 디바이스에서 하드웨어 인코더와 코덱을 고를 때의 기준과 함정을 안다.
:::

## 1. RTP 헤더 — 미디어 패킷의 봉투

[06장](/study/webrtc/06-ice)·[07장](/study/webrtc/07-turn)까지는 "두 피어 사이에 UDP 길을 어떻게 뚫는가"를 다뤘다. 이 장부터는 그 길로 무엇이 흘러가는지를 본다. WebRTC의 오디오·비디오는 모두 <strong>RTP(Real-time Transport Protocol, RFC 3550)</strong> 패킷에 담겨 UDP로 전송된다. SDP의 m-line에 보이는 `UDP/TLS/RTP/SAVPF`가 바로 "UDP 위 DTLS로 키를 교환한 SRTP(Secure RTP), 피드백 확장 프로파일(AVPF)"이라는 뜻이다.

RTP는 TCP처럼 재전송·순서 보장을 해주지 않는다. 대신 수신측이 스스로 판단하는 데 필요한 정보를 헤더에 실어 보낸다. 몇 번째 패킷인지(sequence number), 이 데이터가 미디어 시간축의 어디에 놓이는지(timestamp), 어느 스트림 것인지(SSRC), 어떤 코덱으로 디코딩해야 하는지(PT)다. 재전송할지, 기다릴지, 버릴지는 이 정보를 본 수신측과 상위 로직이 정한다. 실시간 미디어에서 "늦게 온 정확한 데이터"는 쓸모가 없기 때문이다.

![RTP 고정 헤더 비트 레이아웃 — 첫 32비트에 V(2비트)·P·X·CC(4비트)·M·PT(7비트)·Sequence Number(16비트), 이어서 32비트 Timestamp와 32비트 SSRC까지 고정 헤더 12바이트, 그 뒤에 CC가 0보다 클 때의 CSRC 목록과 X=1일 때의 0xBEDE 헤더 확장(확장 요소들), 마지막으로 SRTP가 암호화하는 페이로드가 오는 구조](/images/study-webrtc/08-rtp-header-light.png)
![RTP 고정 헤더 비트 레이아웃 — 첫 32비트에 V(2비트)·P·X·CC(4비트)·M·PT(7비트)·Sequence Number(16비트), 이어서 32비트 Timestamp와 32비트 SSRC까지 고정 헤더 12바이트, 그 뒤에 CC가 0보다 클 때의 CSRC 목록과 X=1일 때의 0xBEDE 헤더 확장(확장 요소들), 마지막으로 SRTP가 암호화하는 페이로드가 오는 구조](/images/study-webrtc/08-rtp-header-dark.png)

| 필드 | 크기 | 의미 | WebRTC에서의 실제 |
|---|---|---|---|
| V (version) | 2비트 | 항상 2 | 첫 바이트가 `10xxxxxx`, 즉 128~191이 되는 이유 |
| P (padding) | 1비트 | 끝에 패딩 바이트가 있음 | 대역폭 프로빙용 패딩 패킷에서 쓰인다 |
| X (extension) | 1비트 | 헤더 확장이 붙음 | 거의 항상 1 (mid·transport-cc 등) |
| CC (CSRC count) | 4비트 | CSRC 개수 | P2P에서는 보통 0 |
| M (marker) | 1비트 | 프로파일이 정하는 경계 표시 | 비디오: 프레임의 마지막 패킷, 오디오: 무음 뒤 첫 패킷 |
| PT (payload type) | 7비트 | 어떤 코덱인지 | 96~127 동적 번호, SDP `a=rtpmap`으로 매핑 |
| Sequence Number | 16비트 | 패킷마다 +1 | 손실·순서 뒤바뀜 감지, NACK의 기준 |
| Timestamp | 32비트 | 미디어 샘플링 시각 | 클럭 단위, 같은 프레임은 같은 값 |
| SSRC | 32비트 | 동기화 소스 식별자 | 스트림(트랙·RTX·FEC)마다 별도 무작위 값 |

### timestamp는 "보낸 시각"이 아니라 "찍은 시각"이다

가장 자주 오해하는 필드가 timestamp다. RTP timestamp는 패킷을 보낸 벽시계 시각이 아니라, <strong>그 미디어가 샘플링(캡처)된 순간을 미디어 클럭 단위로 센 값</strong>이다. 단위는 코덱마다 고정돼 있다.

| 미디어 | RTP 클럭 | 한 단위 증가량 |
|---|---|---|
| 비디오 (VP8·VP9·H.264·AV1 공통) | 90,000 Hz | 30 fps → 프레임당 3,000 / 25 fps → 3,600 / 15 fps → 6,000 |
| Opus | 48,000 Hz (실제 샘플레이트와 무관하게 고정) | 20 ms 프레임 → 960 |
| G.711 (PCMU/PCMA) | 8,000 Hz | 20 ms 프레임 → 160 |

Opus는 내부적으로 8~48kHz 어느 대역으로 인코딩하든 RTP 클럭은 항상 48kHz로 쓴다(RFC 7587). 그래서 SDP에는 늘 `a=rtpmap:111 opus/48000/2`처럼 48000과 채널 수 2가 찍힌다. 비디오 프레임 하나가 패킷 여러 개로 쪼개지면 그 패킷들은 <strong>모두 같은 timestamp</strong>를 갖고, 마지막 패킷에만 M 비트가 선다. 수신측은 "timestamp가 바뀌거나 M=1을 만나면 프레임 하나가 끝났다"고 판단해 조립한다.

timestamp와 sequence number의 초기값은 무작위다(RFC 3550 권고). 값 자체에는 절대적인 의미가 없고, 같은 스트림 안의 <strong>차이</strong>만 의미가 있다. 서로 다른 스트림(오디오와 비디오)의 timestamp를 직접 비교할 수도 없다. 이 둘을 같은 시간축에 올리는 장치가 5절의 RTCP SR이다.

sequence number는 16비트라 금방 한 바퀴 돈다. 2 Mbps 비디오를 1,200바이트 패킷으로 보내면 초당 약 200패킷이므로 65,536개는 5분 남짓이면 소진된다. 수신측은 랩어라운드 횟수(cycles)를 더한 32비트 "확장 시퀀스 번호"로 관리한다. 디바이스에서 RTP를 직접 다룰 때 16비트 비교를 그대로 쓰면 5분마다 "엄청난 역순 패킷"이 생기는 버그가 난다.

### 한 포트로 여러 프로토콜 구분하기

WebRTC는 보통 BUNDLE(RFC 9143)과 rtcp-mux(RFC 5761)로 오디오·비디오·RTCP·DataChannel을 <strong>UDP 5-튜플 하나</strong>에 모은다. 같은 포트로 STUN, DTLS, SRTP/SRTCP가 섞여 들어오므로 수신측은 첫 바이트로 종류를 가른다(RFC 7983).

| 첫 바이트 | 프로토콜 |
|---|---|
| 0~3 | STUN (ICE connectivity check) |
| 20~63 | DTLS (핸드셰이크, SCTP 데이터) |
| 64~79 | TURN ChannelData |
| 128~191 | RTP / RTCP |

RTP와 RTCP는 둘째 바이트로 다시 구분한다. RTCP 패킷 타입(200~207)은 RTP 헤더 자리로 보면 "M=1, PT=72~79"와 겹친다. 그래서 rtcp-mux를 쓸 때는 RTP 페이로드 타입으로 64~95를 피하라고 RFC 5761이 권고하고, 브라우저는 동적 PT를 96 이상으로 쓴다. 같은 RTP 안에서 오디오·비디오·RTX를 구분하는 것은 SSRC와 PT, 그리고 3절의 MID 헤더 확장이다.

::: tip SRTP여도 헤더는 보인다
SRTP는 <strong>페이로드만 암호화</strong>하고 RTP 고정 헤더는 평문으로 둔다(무결성 태그로 변조만 막는다). 그래서 Wireshark에서 UDP를 RTP로 해석(Decode As → RTP)하면 암호화된 WebRTC 트래픽에서도 SSRC·seq·timestamp를 읽어 손실과 지터를 분석할 수 있다. SFU가 복호화 없이 패킷을 라우팅할 수 있는 것도 이 때문이다. 키 교환과 헤더 확장 암호화는 [10장](/study/webrtc/10-dtls-srtp)에서 다룬다.
:::

## 2. RTCP — 수신 보고와 피드백

RTP가 미디어를 나른다면 <strong>RTCP(RTP Control Protocol)</strong>는 그 미디어가 어떻게 도착하고 있는지를 양방향으로 알린다. RTCP가 하는 일은 네 가지다.

- <strong>품질 보고</strong>: 손실률·지터·RTT 계산 재료를 주고받는다.
- <strong>동기화</strong>: RTP timestamp와 벽시계(NTP)의 대응을 알려 립싱크를 가능하게 한다.
- <strong>식별</strong>: CNAME으로 "이 SSRC들은 같은 참가자 것"임을 알린다.
- <strong>피드백</strong>: 재전송 요청(NACK), 키프레임 요청(PLI/FIR), 대역폭 추정 정보를 보낸다.

### RTCP 패킷 종류

| PT | 이름 | 정의 | 역할 |
|---|---|---|---|
| 200 | SR (Sender Report) | RFC 3550 | 송신 통계 + NTP↔RTP timestamp 매핑 + 수신 보고 블록 |
| 201 | RR (Receiver Report) | RFC 3550 | 수신 보고 블록(손실·지터·LSR/DLSR) |
| 202 | SDES | RFC 3550 | 소스 설명. WebRTC에서는 사실상 CNAME만 쓴다 |
| 203 | BYE | RFC 3550 | 스트림 종료 알림 |
| 204 | APP | RFC 3550 | 애플리케이션 정의 (거의 안 쓴다) |
| 205 | RTPFB (전송 계층 피드백) | RFC 4585 | FMT=1 Generic NACK, FMT=3/4 TMMBR/TMMBN(RFC 5104), FMT=15 transport-cc 피드백 |
| 206 | PSFB (페이로드별 피드백) | RFC 4585 | FMT=1 PLI, FMT=2 SLI, FMT=3 RPSI, FMT=4 FIR(RFC 5104), FMT=15 AFB(REMB가 여기에 실린다) |
| 207 | XR (확장 보고) | RFC 3611 | 추가 지표 블록. 브라우저에서는 제한적으로 쓰인다 |

RTCP 패킷은 보통 여러 개를 이어 붙인 <strong>compound 패킷</strong>으로 보낸다(SR/RR이 맨 앞, SDES 포함). 그러나 NACK이나 PLI처럼 급한 피드백은 기다릴 수 없으므로, AVPF 프로파일(RFC 4585)은 정해진 주기를 기다리지 않는 "early feedback"을 허용하고, reduced-size RTCP(RFC 5506, SDP의 `a=rtcp-rsize`)는 피드백 패킷 하나만 단독으로 보내는 것을 허용한다. RFC 3550은 RTCP가 세션 대역폭의 5% 정도만 쓰도록 전송 주기를 조절하라고 정하고 있다.

### SR과 RR에 담긴 숫자

SR은 송신자가 보내는 보고로, 앞부분에 다음 네 값이 있다.

- <strong>NTP timestamp</strong>(64비트): 이 SR을 만든 순간의 송신측 벽시계
- <strong>RTP timestamp</strong>(32비트): 같은 순간을 그 스트림의 미디어 클럭으로 환산한 값
- <strong>sender's packet count / octet count</strong>: 지금까지 보낸 패킷 수와 페이로드 바이트 수

NTP와 RTP timestamp가 "같은 순간"을 가리킨다는 점이 핵심이다. 이 쌍이 있어야 수신측이 임의의 RTP timestamp를 송신측 벽시계 시각으로 바꿀 수 있다(5절 립싱크).

SR과 RR 뒤에는 수신 대상 SSRC마다 <strong>report block</strong>이 붙는다.

| 필드 | 크기 | 의미 |
|---|---|---|
| fraction lost | 8비트 | 직전 보고 이후 손실률 (값/256) |
| cumulative lost | 24비트 | 누적 손실 패킷 수 |
| extended highest seq | 32비트 | 받은 가장 큰 확장 시퀀스 번호 |
| interarrival jitter | 32비트 | 도착 간격 흔들림 추정치 (RTP 클럭 단위) |
| LSR | 32비트 | 마지막으로 받은 SR의 NTP timestamp 가운데 32비트 |
| DLSR | 32비트 | 그 SR을 받은 뒤 이 보고를 보내기까지 걸린 시간 (1/65536초 단위) |

<strong>RTT 계산</strong>은 송신자가 RR을 받은 시각을 A라 할 때 `RTT = A − LSR − DLSR`이다. 수신측이 SR을 붙잡고 있던 시간(DLSR)을 빼므로 양쪽 시계가 맞지 않아도 왕복 시간을 구할 수 있다. <strong>지터</strong>는 연속한 두 패킷의 "도착 간격 − 송신(timestamp) 간격" 차이 D의 절댓값을 지수 평활한 값이다.

```text
J(i) = J(i-1) + (|D(i-1, i)| - J(i-1)) / 16
```

결과는 RTP 클럭 단위라서 비디오라면 90으로 나눠야 ms가 된다. 브라우저 `getStats()`의 `inbound-rtp.jitter`는 초 단위로 환산해서 보여준다. 이 지표들은 [15장](/study/webrtc/15-monitoring-debugging)의 모니터링에서 다시 쓴다.

### SDP에서 피드백 협상 읽기

어떤 피드백을 쓸지는 SDP의 `a=rtcp-fb`로 코덱(PT)마다 협상한다. 브라우저가 만드는 비디오 m-section은 대략 다음과 같다(값은 예시).

```text
m=video 9 UDP/TLS/RTP/SAVPF 96 97 102 103
a=mid:1
a=rtcp-mux
a=rtcp-rsize
a=extmap:3 http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01
a=rtpmap:96 VP8/90000
a=rtcp-fb:96 goog-remb
a=rtcp-fb:96 transport-cc
a=rtcp-fb:96 ccm fir
a=rtcp-fb:96 nack
a=rtcp-fb:96 nack pli
a=rtpmap:97 rtx/90000
a=fmtp:97 apt=96
a=rtpmap:102 H264/90000
a=rtcp-fb:102 transport-cc
a=rtcp-fb:102 nack
a=rtcp-fb:102 nack pli
a=fmtp:102 level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=42e01f
a=rtpmap:103 rtx/90000
a=fmtp:103 apt=102
```

`nack`은 재전송 요청, `nack pli`는 키프레임 요청, `ccm fir`는 FIR, `transport-cc`와 `goog-remb`는 대역폭 추정 피드백이다. `rtx/90000`과 `apt=96`은 "PT 96의 재전송은 PT 97, 별도 SSRC로 보낸다"는 뜻이다(RFC 4588). 각 피드백을 언제 쓰고 어떤 트레이드오프가 있는지는 [09장](/study/webrtc/09-quality-latency)에서 자세히 본다. SDP 문법 전반은 [04장](/study/webrtc/04-sdp-jsep)에 정리돼 있다.

## 3. 헤더 확장 — abs-send-time, transport-cc, 그리고 친구들

고정 헤더 12바이트만으로는 현대 WebRTC가 필요로 하는 정보를 다 실을 수 없다. 그래서 X=1일 때 고정 헤더 뒤에 <strong>헤더 확장</strong>을 붙인다. 현재 규격은 RFC 8285다. 두 가지 형식이 있다.

- <strong>one-byte 헤더</strong>: 확장 블록이 `0xBEDE`로 시작하고, 각 요소가 ID(4비트)·길이(4비트)·데이터(1~16바이트)다. ID는 1~14만 쓸 수 있다.
- <strong>two-byte 헤더</strong>: `0x100`으로 시작하고 ID·길이에 1바이트씩 쓴다. 요소가 많거나 16바이트를 넘을 때 쓴다(SDP `a=extmap-allow-mixed`).

ID 번호는 고정이 아니라 SDP의 `a=extmap:<ID> <URI>`로 세션마다 협상한다. 그래서 같은 확장이 세션마다 다른 ID를 가질 수 있고, SDP를 보지 않고 패킷만 보면 어떤 확장인지 알 수 없다.

| 확장 (URI 요약) | 내용 | 쓰는 곳 |
|---|---|---|
| `urn:ietf:params:rtp-hdrext:sdes:mid` | 이 패킷이 속한 m-section의 MID | BUNDLE에서 SSRC를 모를 때 트랜시버 매핑 |
| `...sdes:rtp-stream-id` / `repaired-rtp-stream-id` | Simulcast 계층 RID | Simulcast([12장](/study/webrtc/12-topology-sfu)) |
| `http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time` | 송신 시각 (24비트, 6.18 고정소수점 초, 64초마다 순환) | 수신측 대역폭 추정(REMB) |
| `http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01` | 트랜스포트 전체 공통 16비트 시퀀스 번호 | 송신측 대역폭 추정(TWCC) |
| `urn:ietf:params:rtp-hdrext:ssrc-audio-level` | 오디오 레벨 dBov (RFC 6464) | 발화자 감지, SFU의 활성 화자 선택 |
| `urn:3gpp:video-orientation` | 카메라 회전(CVO) | 회전된 영상을 재인코딩 없이 수신측에서 돌려 표시 |
| `.../rtp-hdrext/playout-delay` | 송신측이 원하는 재생 지연 최소·최대 | 클라우드 게이밍 등 초저지연 요청 |
| `.../rtp-hdrext/abs-capture-time` | 캡처 시각(NTP) | 종단 간 지연 측정, 믹서 경유 동기화 |
| AV1 Dependency Descriptor | 프레임 간 의존 관계 | AV1·SVC 계층 선택(SFU) |

### transport-cc는 왜 따로 시퀀스 번호를 두는가

RTP 헤더에 이미 sequence number가 있는데 transport-cc가 별도 번호를 붙이는 이유가 있다. RTP seq는 <strong>SSRC마다</strong> 따로 증가한다. 오디오, 비디오, RTX 재전송, FEC가 각자 다른 SSRC로 나가므로, RTP seq만 보면 "이 UDP 경로로 나간 모든 패킷"의 순서와 도착 시각을 하나의 줄로 세울 수 없다. 대역폭 추정은 경로 전체의 혼잡을 봐야 하므로 <strong>트랜스포트(5-튜플) 전체에서 공통으로 증가하는 번호</strong>가 필요하다. 수신측은 이 번호별 도착 시각을 RTCP RTPFB(FMT=15)로 돌려보내고, 송신측은 이를 자기 송신 시각과 맞춰 지연 변화를 계산한다. 이것이 [09장](/study/webrtc/09-quality-latency)의 TWCC다.

디바이스 쪽 WebRTC 스택이 transport-cc를 구현하지 않으면 송신측 대역폭 추정이 동작하지 않는다. 브라우저가 수신측일 때는 `goog-remb` + abs-send-time으로 대신 추정해 REMB를 보내줄 수 있지만, 둘 다 없으면 디바이스는 RR의 손실률 말고는 혼잡을 알 방법이 없다. 디바이스 스택을 고를 때 "어떤 헤더 확장과 피드백을 지원하는가"를 반드시 확인해야 하는 이유다.

## 4. 코덱 — 브라우저 필수 코덱과 선택지

### 필수 코덱: RFC 7742와 RFC 7874

WebRTC 초기에는 비디오 필수 코덱을 두고 VP8(로열티 프리) 진영과 H.264(하드웨어 보급) 진영이 오래 대립했다. 결론은 "둘 다"였다.

| 구분 | 규격 | 필수(MUST) 구현 | 비고 |
|---|---|---|---|
| 비디오 | RFC 7742 | <strong>VP8</strong> 과 <strong>H.264 Constrained Baseline</strong> | 브라우저는 둘 다 필수. 비브라우저(디바이스)도 비디오를 다루면 둘 다 MUST |
| 오디오 | RFC 7874 | <strong>Opus</strong>, <strong>G.711 (PCMU/PCMA)</strong>, telephone-event(DTMF, RFC 4733) | G.711처럼 자체 컴포트 노이즈가 없는 코덱에는 RFC 3389 CN 지원 MUST |

RFC 7742는 H.264에 대해 몇 가지를 더 못 박는다. <strong>packetization-mode 1은 반드시 지원</strong>해야 하고, profile-level-id를 SDP에 넣고 해석해야 하며, Constrained Baseline Level 1.2는 MUST, Constrained High Level 1.3은 SHOULD다. 또 SDP로 따로 정하지 않았다면 수신측은 최소 320×240, 20 fps는 디코딩할 수 있어야 한다.

실무에서 이 표가 주는 의미는 단순하다. <strong>H.264 Constrained Baseline + Opus 조합은 어떤 브라우저와도 통한다.</strong> 그 밖의 코덱은 "되면 좋은" 선택지다.

### 비디오 코덱 비교

| 코덱 | RTP 페이로드 규격 | 압축 효율 (같은 화질 대비) | 임베디드 HW 인코더 보급 | 비고 |
|---|---|---|---|---|
| VP8 | RFC 7741 | 기준 | 드묾 | 브라우저 필수. 디바이스에서는 대개 SW 인코딩이라 CPU 부담 |
| H.264 | RFC 6184 | VP8과 비슷 | <strong>매우 넓음</strong> | 브라우저 필수(CBP). 디바이스의 현실적 기본값 |
| VP9 | RFC 9628 | H.264보다 좋음 | 일부 SoC | SVC 지원. 브라우저·버전별 지원 차이 |
| H.265 (HEVC) | RFC 7798 | VP9과 비슷하거나 좋음 | 넓어지는 중 | 브라우저 WebRTC 지원은 하드웨어·버전 의존 |
| AV1 | AOMedia "RTP Payload Format for AV1" | 가장 좋음 | 최신 SoC 일부 | SW 인코딩은 무겁다. 브라우저 지원이 빠르게 변하는 중 |

::: warning VP9·AV1·H.265 지원은 런타임에 확인한다
선택 코덱의 지원 범위는 브라우저·버전·OS·하드웨어 조합마다 다르고 해마다 바뀐다. 예를 들어 Chrome은 M90부터 WebRTC에서 AV1 인코딩을 지원했지만, Safari는 하드웨어 AV1 디코더가 있는 기기 위주로 지원하고, Firefox는 최근 버전에서야 WebRTC AV1의 하드웨어 디코딩 경로가 추가되는 식이다. H.265도 Safari가 먼저 지원했고 Chrome은 하드웨어를 지원하는 플랫폼에서 비교적 최근에 지원을 추가했다. 이런 표를 외우기보다 <strong>`RTCRtpReceiver.getCapabilities('video')`로 실제 지원 목록을 확인</strong>하고, 협상 결과(`getStats()`의 codec 항목)를 로그로 남기는 편이 안전하다.
:::

```js
// List what this browser can actually decode, then prefer H.264 CBP on a recvonly transceiver.
const { codecs } = RTCRtpReceiver.getCapabilities('video');
codecs.forEach(c => console.log(c.mimeType, c.clockRate, c.sdpFmtpLine ?? ''));

const pc = new RTCPeerConnection(config);
const tr = pc.addTransceiver('video', { direction: 'recvonly' });

const isH264Cbp = c =>
  c.mimeType === 'video/H264' &&
  /profile-level-id=42e0/i.test(c.sdpFmtpLine ?? '') &&
  /packetization-mode=1/.test(c.sdpFmtpLine ?? '');

const preferred = codecs.filter(isH264Cbp);
tr.setCodecPreferences([...preferred, ...codecs.filter(c => !isH264Cbp(c))]);
```

`setCodecPreferences`는 SDP를 직접 고치지 않고 코덱 순서를 바꾸는 표준 방법이다. 동작 원리와 주의점은 [04장](/study/webrtc/04-sdp-jsep)에서 다뤘다.

### H.264의 profile-level-id 읽기

H.264는 같은 이름 아래 프로파일(사용 가능한 압축 도구 묶음)과 레벨(최대 해상도·프레임레이트·비트레이트 상한)이 다양하다. SDP의 `profile-level-id`는 16진수 6자리, 3바이트다.

```text
profile-level-id=42e01f
                 ││ ││ └┴─ level_idc   = 0x1f = 31  → Level 3.1 (1280x720@30 수준)
                 ││ └┴──── profile-iop = 0xe0       → constraint_set0/1/2 플래그
                 └┴─────── profile_idc = 0x42 = 66  → Baseline 계열
```

profile_idc가 66(Baseline)이고 constraint_set1 플래그가 켜져 있으면 <strong>Constrained Baseline(CBP)</strong>이다. 자주 보는 값은 다음과 같다.

| 값 | 의미 |
|---|---|
| `42e01f` | Constrained Baseline, Level 3.1 — WebRTC에서 가장 무난한 값 |
| `42001f` | Baseline, Level 3.1 |
| `4d001f` | Main, Level 3.1 |
| `64001f` | High, Level 3.1 |
| `640c1f` | Constrained High, Level 3.1 |

profile-level-id가 아예 없으면 기본값은 `420010`(Baseline, Level 1.0)으로 해석된다. 함께 쓰이는 파라미터도 알아둔다.

- <strong>packetization-mode</strong>: 0이면 NAL 하나를 RTP 패킷 하나에만 담는다(분할 불가). 1이면 STAP-A·FU-A를 쓸 수 있다. 0과 1은 서로 다른 코덱 항목처럼 취급돼 별도 PT로 협상된다. 생략하면 0이다.
- <strong>level-asymmetry-allowed=1</strong>: 양방향의 레벨이 달라도 된다는 뜻이다. 디바이스는 1080p를 보내고 브라우저는 그보다 낮은 레벨로 보내는 비대칭 구성이 가능해진다.

디바이스 인코더가 실제로 내보내는 스트림의 프로파일·레벨(SPS 안에 들어 있다)과 SDP에 광고한 값이 어긋나면, 협상은 성공했는데 화면이 검게 나오거나 일부 브라우저에서만 디코딩이 실패하는 현상이 생긴다. "SDP에는 42e01f를 광고했는데 하드웨어 인코더가 High 프로파일을 낸다"가 전형적인 사례다.

### 오디오 코덱: Opus

Opus(RFC 6716)는 6 kbps부터 510 kbps까지, 음성부터 음악까지 하나로 처리하는 코덱이다. 프레임 길이는 2.5~60 ms에서 고를 수 있지만 WebRTC 기본은 20 ms다. SDP의 `a=fmtp`로 동작을 조절한다(RFC 7587).

| fmtp 파라미터 | 의미 | 기본·권장 |
|---|---|---|
| `minptime=10` | 최소 패킷 길이 10 ms | 브라우저 기본 |
| `useinbandfec=1` | 인밴드 FEC(LBRR) 수신 가능 | 브라우저 기본. 손실 대비 ([09장](/study/webrtc/09-quality-latency)) |
| `usedtx=1` | 무음 구간 전송 중단(DTX) | 대역폭 절약, 기본은 꺼짐 |
| `stereo=1` | 스테레오 수신 선호 | 음성이면 불필요 |
| `maxaveragebitrate` | 평균 비트레이트 상한(bps) | 음성은 24~32 kbps면 충분 |

G.711은 64 kbps에 8kHz 협대역이라 음질·효율 모두 Opus보다 떨어지지만, 기존 전화망(SIP)과 연동할 때 트랜스코딩 없이 붙일 수 있어 필수 코덱에 남아 있다. 디바이스 입장에서 Opus 인코딩은 비디오에 비하면 CPU 부담이 작으므로, 오디오가 필요하면 Opus를 고르면 된다.

## 5. H.264 패킷화 — NAL unit, STAP-A, FU-A

인코더가 내놓는 H.264 스트림은 <strong>NAL unit</strong>(Network Abstraction Layer unit)의 연속이다. 파일이나 파이프로 흐를 때는 NAL 사이를 `00 00 00 01` 시작 코드로 구분하는 <strong>Annex-B 바이트 스트림</strong> 형식이고, RTP에 실을 때는 시작 코드를 떼고 NAL 자체를 페이로드로 담는다. 각 NAL의 첫 바이트가 NAL 헤더다.

```text
+---------------+
|0|1|2|3|4|5|6|7|
+-+-+-+-+-+-+-+-+
|F|NRI|  Type   |   F: 금지 비트(0), NRI: 중요도, Type: NAL 종류
+---------------+
```

| Type | NAL 종류 | 비고 |
|---|---|---|
| 1 | 비 IDR 슬라이스 (P 프레임 등) | 이전 프레임을 참조 |
| 5 | IDR 슬라이스 (키프레임) | 혼자 디코딩 가능, 참조 체인을 리셋 |
| 6 | SEI | 부가 정보 |
| 7 | SPS | 해상도·프로파일·레벨 등 시퀀스 파라미터 |
| 8 | PPS | 픽처 파라미터 |
| 9 | AUD | 액세스 유닛 구분자 |

RTP 페이로드의 첫 바이트도 같은 모양이고, Type 값으로 패킷 종류를 구분한다(RFC 6184). 1~23은 NAL 그대로(Single NAL), 24는 STAP-A, 28은 FU-A다.

![H.264 RTP 패킷화 — 인코더 출력의 AU 1(SPS·PPS·수십 KB IDR 슬라이스)과 AU 2(작은 P 슬라이스)가 각각 SPS·PPS는 STAP-A 한 패킷(RTP 헤더·STAP-A 헤더·크기·SPS·크기·PPS)으로 묶이고, 큰 IDR은 MTU 약 1,200바이트 이하 FU-A 조각들(FU 지시자·FU 헤더 S=1/E=0/E=1)로 쪼개져 같은 timestamp에 마지막 패킷만 M=1이 되며, 작은 P 슬라이스는 Single NAL 패킷 하나로 실리는 구조](/images/study-webrtc/08-h264-packetization-light.png)
![H.264 RTP 패킷화 — 인코더 출력의 AU 1(SPS·PPS·수십 KB IDR 슬라이스)과 AU 2(작은 P 슬라이스)가 각각 SPS·PPS는 STAP-A 한 패킷(RTP 헤더·STAP-A 헤더·크기·SPS·크기·PPS)으로 묶이고, 큰 IDR은 MTU 약 1,200바이트 이하 FU-A 조각들(FU 지시자·FU 헤더 S=1/E=0/E=1)로 쪼개져 같은 timestamp에 마지막 패킷만 M=1이 되며, 작은 P 슬라이스는 Single NAL 패킷 하나로 실리는 구조](/images/study-webrtc/08-h264-packetization-dark.png)

### 세 가지 패킷 형식

- <strong>Single NAL unit (Type 1~23)</strong>: NAL 하나가 MTU 안에 들어가면 그대로 한 패킷에 담는다. 작은 P 프레임이 여기에 해당한다.
- <strong>STAP-A (Type 24)</strong>: 작은 NAL 여러 개를 한 패킷에 묶는다. 각 NAL 앞에 2바이트 크기 필드가 붙는다. 수십 바이트짜리 SPS·PPS를 따로 보내면 헤더 오버헤드만 늘고 손실 확률도 올라가므로, 키프레임 앞의 SPS+PPS를 STAP-A 하나로 보내는 것이 일반적이다.
- <strong>FU-A (Type 28)</strong>: MTU보다 큰 NAL을 조각낸다. 원래 NAL 헤더는 반복하지 않고, 대신 2바이트를 붙인다. <strong>FU 지시자</strong>(원래 NAL의 F·NRI + Type 28)와 <strong>FU 헤더</strong>(S 시작 비트, E 끝 비트, R 예약 비트, 원래 NAL Type)다. 수신측은 S=1 조각부터 E=1 조각까지 모아 원래 NAL 헤더를 복원한다. 조각이 하나라도 빠지면 NAL 전체를 쓸 수 없다.

packetization-mode별로 쓸 수 있는 형식은 다음과 같다.

| 형식 | mode 0 (Single NAL) | mode 1 (Non-interleaved) | mode 2 (Interleaved) |
|---|---|---|---|
| Single NAL (1~23) | O | O | X |
| STAP-A (24) | X | O | X |
| STAP-B / MTAP (25~27) | X | X | O |
| FU-A (28) | X | O | O |
| FU-B (29) | X | X | O |

WebRTC에서는 사실상 mode 1만 쓴다. mode 0으로는 큰 NAL을 쪼갤 수 없어서 인코더가 슬라이스 크기를 MTU 이하로 강제해야 하는데, 이를 지원하지 않는 인코더가 많다.

### FU-A 분할을 코드로 보면

개념은 단순하다. Pion 같은 스택이 내부에서 하는 일을 최소한으로 줄이면 다음과 같다.

```go
// fragmentNAL splits one NAL unit (no start code) into RTP payloads.
// Small NALs go out as-is (Single NAL); large ones become FU-A fragments.
func fragmentNAL(nal []byte, maxPayload int) [][]byte {
	if len(nal) <= maxPayload {
		return [][]byte{nal}
	}
	hdr := nal[0]
	fuIndicator := (hdr & 0xE0) | 28 // keep F+NRI, type = 28 (FU-A)
	nalType := hdr & 0x1F
	data := nal[1:] // original NAL header is carried in the FU header instead

	var out [][]byte
	for len(data) > 0 {
		n := min(len(data), maxPayload-2)
		fuHeader := nalType
		if len(out) == 0 {
			fuHeader |= 0x80 // S: first fragment
		}
		if n == len(data) {
			fuHeader |= 0x40 // E: last fragment
		}
		out = append(out, append([]byte{fuIndicator, fuHeader}, data[:n]...))
		data = data[n:]
	}
	return out
}
```

여기에 RTP 헤더를 붙일 때 같은 프레임(액세스 유닛)의 모든 패킷에 같은 timestamp를 주고, <strong>프레임의 마지막 패킷에만 M=1</strong>을 세운다. timestamp는 캡처 시각을 90kHz로 환산한 값이다.

### 왜 1,200바이트인가

libwebrtc의 비디오 패킷 최대 크기와 KVS WebRTC C SDK의 기본 MTU는 모두 1,200바이트다. 이더넷 MTU 1,500에 비해 한참 작다. 이유는 오버헤드와 경로 다양성이다. IP(IPv6면 40바이트)·UDP 헤더, SRTP 인증 태그, 헤더 확장, TURN을 거치면 ChannelData나 TCP/TLS 프레이밍이 더 붙는다. LTE·VPN·PPPoE 경로는 MTU 자체가 1,500보다 작다. IP 단편화가 일어나면 조각 하나만 잃어도 패킷 전체를 잃고, 어떤 방화벽은 단편화된 UDP를 버린다. IPv6 최소 MTU 1,280 아래로 여유 있게 잡은 1,200이 사실상 표준값이 된 이유다.

::: warning 디바이스 H.264 스트림의 흔한 함정
- <strong>SPS/PPS가 키프레임마다 반복되지 않는다</strong>: 스트림 시작에만 SPS/PPS를 내는 인코더가 많다. 그러면 나중에 붙은 뷰어나 패킷을 잃은 뷰어는 키프레임을 받아도 디코딩하지 못해 검은 화면을 본다. GStreamer라면 `h264parse config-interval=-1`로 IDR마다 다시 넣는다.
- <strong>B 프레임</strong>: B 프레임은 재정렬 지연을 만들고 Constrained Baseline에는 없는 기능이다. 인코더에서 B 프레임을 끈다(`bframes=0`).
- <strong>AVC 형식 출력</strong>: 일부 인코더·mux는 시작 코드 대신 길이 접두(AVCC) 형식을 낸다. RTP 패킷화기가 Annex-B를 기대한다면 `stream-format=byte-stream`으로 맞춘다.
- <strong>프로파일 불일치</strong>: 앞서 본 profile-level-id 불일치. 인코더 출력 SPS를 실제로 파싱해 확인한다.
:::

## 6. 지터 버퍼와 립싱크

### 지터 버퍼: 흔들림을 지연으로 바꾸는 장치

송신측은 20 ms마다 오디오 패킷을, 33 ms마다 비디오 프레임을 일정하게 보낸다. 그러나 네트워크를 지나면 패킷마다 겪는 큐잉 지연이 달라 도착 간격이 들쭉날쭉해진다. 이 흔들림이 <strong>지터</strong>다. 도착하는 대로 재생하면 소리가 끊기고 영상이 덜컥거린다. 그래서 수신측은 패킷을 잠깐 모아뒀다가 다시 일정한 간격으로 꺼내 재생한다. 이것이 <strong>지터 버퍼</strong>다.

![지터 버퍼 동작 — 송신측이 #1~#6 패킷을 20ms 간격으로 보내면 네트워크 지연이 제각각이라 도착 간격이 들쭉날쭉하고, 수신측은 버퍼 목표 지연 40ms만큼 기다렸다가 다시 20ms 간격으로 재생하는데, 목표 지연보다 늦게 도착한 #5는 재생 시각을 놓쳐 손실 은닉(PLC)으로 대체되는 타임라인](/images/study-webrtc/08-jitter-buffer-light.png)
![지터 버퍼 동작 — 송신측이 #1~#6 패킷을 20ms 간격으로 보내면 네트워크 지연이 제각각이라 도착 간격이 들쭉날쭉하고, 수신측은 버퍼 목표 지연 40ms만큼 기다렸다가 다시 20ms 간격으로 재생하는데, 목표 지연보다 늦게 도착한 #5는 재생 시각을 놓쳐 손실 은닉(PLC)으로 대체되는 타임라인](/images/study-webrtc/08-jitter-buffer-dark.png)

지터 버퍼의 본질은 트레이드오프다. 목표 지연을 크게 잡으면 늦게 온 패킷도 제때 재생할 수 있어 매끄럽지만 그만큼 화면이 늦다. 작게 잡으면 지연은 줄지만 늦은 패킷이 "손실"로 처리돼 끊김이 늘어난다. 그래서 WebRTC의 지터 버퍼는 고정값이 아니라 <strong>최근 지터를 관찰해 목표 지연을 계속 조절하는 적응형</strong>이다.

오디오와 비디오는 지터 버퍼의 성격이 다르다.

- <strong>오디오</strong>: libwebrtc의 오디오 지터 버퍼는 NetEQ다. 패킷 단위로 다루며, 버퍼가 차면 재생 속도를 살짝 높이고(가속), 모자라면 소리를 늘려(확장) 사람이 거의 못 느끼게 지연을 조절한다. 패킷이 없으면 PLC(손실 은닉)로 그럴듯한 소리를 만들어 채운다.
- <strong>비디오</strong>: 패킷이 아니라 <strong>프레임 단위</strong>로 다룬다. 프레임을 이루는 패킷이 모두 모여야 하고, 그 프레임이 참조하는 이전 프레임도 디코딩돼 있어야 꺼낼 수 있다. 오디오처럼 "그럴듯하게 채우기"가 어려워서, 빠진 패킷이 있으면 NACK으로 재전송을 기다리거나 키프레임을 요청해야 한다. 재전송을 기다릴 시간도 결국 지터 버퍼 지연에서 나온다.

브라우저에서 지터 버퍼 상태는 `getStats()`의 `inbound-rtp`에서 볼 수 있다. `jitterBufferDelay / jitterBufferEmittedCount`가 평균 버퍼 지연이고, `jitterBufferTargetDelay`와 `jitterBufferMinimumDelay`로 목표치를 확인한다. 애플리케이션이 목표를 조정하는 `RTCRtpReceiver.jitterBufferTarget`은 [09장](/study/webrtc/09-quality-latency)의 지연 예산에서 다룬다.

### 립싱크: SR의 NTP↔RTP 매핑

오디오와 비디오는 서로 다른 SSRC, 다른 클럭(48kHz와 90kHz), 무작위 초기값을 가진 별개의 RTP 스트림이다. 게다가 각자의 지터 버퍼를 거치므로 수신측에 도착해 재생 준비가 되는 시각도 다르다. 그대로 두면 입 모양과 소리가 어긋난다. 이를 맞추는 열쇠가 RTCP SR이다.

![립싱크 원리 — 오디오 SR은 NTP T0와 RTP 160000을, 비디오 SR은 NTP T0+33ms와 RTP 900000을 대응시키고, 수신측은 오디오 RTP 164800을 T0 + 4800/48000 = T0+100ms로, 비디오 RTP 906000을 T0+33ms + 6000/90000 = T0+100ms로 환산해 같은 캡처 시각임을 알아내 함께 재생하는 세 시간축(오디오 RTP 48kHz, 송신측 NTP 벽시계, 비디오 RTP 90kHz) 그림](/images/study-webrtc/08-lipsync-light.png)
![립싱크 원리 — 오디오 SR은 NTP T0와 RTP 160000을, 비디오 SR은 NTP T0+33ms와 RTP 900000을 대응시키고, 수신측은 오디오 RTP 164800을 T0 + 4800/48000 = T0+100ms로, 비디오 RTP 906000을 T0+33ms + 6000/90000 = T0+100ms로 환산해 같은 캡처 시각임을 알아내 함께 재생하는 세 시간축(오디오 RTP 48kHz, 송신측 NTP 벽시계, 비디오 RTP 90kHz) 그림](/images/study-webrtc/08-lipsync-dark.png)

동작은 세 단계다.

1. 송신측은 각 스트림의 SR에 "지금 NTP 시각 = 이 스트림의 RTP timestamp 얼마"라는 쌍을 실어 보낸다. 두 스트림의 NTP는 <strong>같은 송신측 시계</strong>여야 한다.
2. 수신측은 패킷의 RTP timestamp를 가장 최근 SR 기준으로 환산한다. `캡처 NTP = SR_NTP + (RTP_ts − SR_RTP) / 클럭`. 그림에서 오디오 RTP 164800과 비디오 RTP 906000은 둘 다 T0+100ms로 환산된다.
3. 같은 캡처 시각의 오디오와 비디오가 같은 순간에 재생되도록, 먼저 준비되는 쪽(보통 오디오)의 재생을 늦춘다. 실제 구현은 두 스트림의 지연 차이를 계속 측정해 한쪽 지터 버퍼에 추가 지연을 주는 방식이다.

어떤 오디오와 어떤 비디오를 짝지을지는 RFC 3550에서는 SDES CNAME으로 정한다. 브라우저 구현(libwebrtc)은 같은 MediaStream(SDP의 `a=msid`)에 묶인 오디오·비디오 트랙을 동기화 쌍으로 본다. 그래서 송신측에서 오디오와 비디오 트랙을 같은 스트림으로 `addTrack(track, stream)` 해야 립싱크가 동작한다.

몇 가지 운영 포인트가 있다.

- <strong>첫 SR 전에는 동기화가 없다</strong>: SR은 주기적으로 오므로 연결 직후 처음 몇 초는 립싱크가 맞지 않을 수 있다.
- <strong>디바이스는 같은 시계로 타임스탬프를 찍어야 한다</strong>: 카메라와 마이크가 서로 다른 시계(USB 카메라의 자체 클럭, ALSA 오디오 클럭)로 PTS를 붙이면 RTP timestamp와 SR의 대응이 조금씩 틀어져 시간이 지날수록 립싱크가 벌어진다. 디바이스 코드에서 오디오·비디오 프레임 모두에 하나의 단조 증가 시계(예: `CLOCK_MONOTONIC`) 기준 캡처 시각을 붙여 WebRTC 스택에 넘기는 것이 원칙이다.
- <strong>원격 조작에서는 립싱크가 지연을 늘릴 수 있다</strong>: 비디오가 오디오보다 늦게 준비되면 오디오를 늦추지만, 반대로 오디오 지터 버퍼가 크면 비디오가 오디오를 기다리게 된다. 운영자가 영상 지연에 민감하고 소리는 부가적이라면, 오디오를 별도 스트림으로 분리해 동기화 쌍에서 빼는 선택지도 있다.

## 7. 하드웨어 인코더와 코덱 선택

### 디바이스에서는 H.264 하드웨어 인코딩이 현실적 기본값이다

카메라 달린 농기계·로봇에서 영상을 보낼 때 코덱 선택을 좌우하는 것은 압축 효율보다 <strong>디바이스의 인코딩 능력</strong>이다. 720p30을 소프트웨어로 인코딩하면 임베디드 ARM CPU 코어 상당 부분을 잡아먹고, 열과 전력이 늘며, 다른 제어 소프트웨어의 실시간성을 해친다. 하드웨어 인코더는 이 일을 전용 블록에서 수 ms 안에 처리한다. 그리고 임베디드 SoC의 하드웨어 인코더가 가장 널리 지원하는 코덱이 H.264다. 브라우저 필수 코덱이라 수신측 호환성 걱정도 없다. 그래서 "H.264 하드웨어 인코더 + Opus"가 디바이스의 출발점이다.

| 플랫폼 | H.264 하드웨어 인코더 | GStreamer 요소 (대표) | 주의 |
|---|---|---|---|
| NVIDIA Jetson (Xavier, Orin NX/AGX 등) | NVENC | `nvv4l2h264enc` | <strong>Jetson Orin Nano에는 NVENC가 없어</strong> SW 인코딩이 필요하다 |
| Raspberry Pi 4 | V4L2 M2M 인코더 (최대 1080p30) | `v4l2h264enc` | <strong>Raspberry Pi 5에는 H.264 하드웨어 인코더가 없다</strong> |
| Rockchip (RK3588 등) | MPP | `mpph264enc` (벤더 플러그인) | 벤더 BSP 버전에 따라 동작 차이 |
| Intel x86 | Quick Sync / VA-API | `vah264enc`, `qsvh264enc` | 산업용 PC 게이트웨이 |

보드 세대가 바뀔 때 하드웨어 인코더가 빠지는 경우가 실제로 있으므로, 하드웨어 선정 단계에서 "H.264 하드웨어 인코딩 지원 여부와 최대 해상도·동시 세션 수"를 체크리스트에 넣어야 한다. 하드웨어 파이프라인 구성은 [13장](/study/webrtc/13-native-webrtc)에서 자세히 다룬다.

### WebRTC용 인코더 설정 체크리스트

녹화·방송용 기본 설정은 WebRTC에 맞지 않는 경우가 많다. 다음 항목을 확인한다.

| 항목 | WebRTC에 맞는 설정 | 이유 |
|---|---|---|
| 프로파일 | Constrained Baseline 또는 SDP에 광고한 값과 일치 | 브라우저 호환성, profile-level-id 불일치 방지 |
| B 프레임 | 끔 | 재정렬 지연 제거, CBP에는 없음 |
| SPS/PPS | IDR마다 반복 | 늦게 붙은 뷰어·손실 복구 |
| 키프레임 | 주기 + <strong>요청 시 즉시 생성</strong>(PLI 대응) | 손실 복구 속도 ([09장](/study/webrtc/09-quality-latency)) |
| 레이트 제어 | CBR 또는 상한 있는 VBR, 작은 VBV 버퍼 | 비트레이트 버스트가 곧 손실·지연 |
| 지연 옵션 | lookahead 끔, zerolatency 계열 프리셋 | 인코더 내부 버퍼링 제거 |
| 비트레이트 변경 | 실행 중 변경 가능해야 함 | 대역폭 추정 결과 반영 |

소프트웨어 기준 파이프라인으로 보면 다음과 같다. KVS WebRTC C SDK가 샘플 프레임을 만들 때 쓰는 설정과 같은 계열이다.

```bash
gst-launch-1.0 v4l2src device=/dev/video0 \
  ! video/x-raw,width=1280,height=720,framerate=30/1 \
  ! videoconvert \
  ! x264enc bframes=0 speed-preset=veryfast tune=zerolatency \
            key-int-max=60 bitrate=1500 byte-stream=true \
  ! h264parse config-interval=-1 \
  ! video/x-h264,stream-format=byte-stream,alignment=au,profile=constrained-baseline \
  ! fakesink
```

`x264enc`의 `bitrate`는 kbps 단위이고, `key-int-max=60`은 30 fps에서 2초마다 키프레임을 뜻한다. 하드웨어 인코더로 바꿀 때는 요소 이름만 바뀌는 게 아니라 속성 이름과 단위도 바뀐다(예: Jetson의 `nvv4l2h264enc`는 `bitrate`가 bps 단위이고 `iframeinterval`, `insert-sps-pps` 같은 별도 속성을 쓴다). 실제 디바이스 연동은 [13장](/study/webrtc/13-native-webrtc)과 [19장](/study/webrtc/19-kvs-c-sdk)에서 이어진다.

### 시나리오별 코덱 결정

| 상황 | 권장 | 이유 |
|---|---|---|
| 일반적인 디바이스 → 브라우저 원격 영상 | H.264 CBP(HW) + Opus | 호환성·CPU·전력 모두 유리 |
| 대역폭이 극도로 빠듯한 업링크, 디바이스에 HW 지원 있음 | H.265 또는 AV1 검토 | 같은 화질에 비트레이트 절감. 단 뷰어 브라우저 지원을 먼저 확인 |
| HW 인코더가 없는 보드 | 해상도·fps를 낮춘 SW H.264, 또는 HW 있는 보드로 교체 검토 | SW VP8/VP9/AV1은 더 무겁다 |
| 녹화·저장 경로와 함께 써야 함 | 저장 서비스가 받는 코덱에 맞춤 | 실시간과 저장의 코덱 제약이 다를 수 있다([21장](/study/webrtc/21-kvs-ingestion-storage)) |
| 다수 뷰어에게 계층 전송(SFU) | Simulcast(H.264/VP8) 또는 SVC(VP9/AV1) | [12장](/study/webrtc/12-topology-sfu) |

브라우저 쪽 함정도 하나 기억해 둔다. Firefox는 H.264를 Cisco가 배포하는 OpenH264 플러그인으로 처리하는데, 이 플러그인은 처음 필요할 때 내려받는다. 인터넷이 막힌 현장 운영 PC나 키오스크에서는 H.264가 안 될 수 있다. 일부 Chromium 파생 빌드도 독점 코덱을 빼고 빌드돼 H.264가 없을 수 있다. 운영자 브라우저 환경을 통제할 수 있다면 지원 브라우저를 명시하고, 아니라면 VP8 폴백을 남겨 두는 것이 안전하다.

::: tip 핵심 정리
- RTP 헤더의 timestamp는 "캡처 시각"을 미디어 클럭(비디오 90kHz, Opus 48kHz)으로 센 값이다. 같은 프레임의 패킷은 같은 timestamp를 갖고, 비디오는 프레임 마지막 패킷에 M=1이 선다.
- RTCP SR/RR은 손실률·지터·RTT(`A − LSR − DLSR`)와 NTP↔RTP 매핑을 나르고, RTPFB/PSFB 피드백은 NACK·PLI·FIR·대역폭 추정 정보를 나른다.
- transport-cc 헤더 확장은 트랜스포트 전체 공통 시퀀스 번호로 송신측 대역폭 추정(TWCC)을 가능하게 한다. 디바이스 스택의 지원 여부를 반드시 확인한다.
- 브라우저 필수 코덱은 VP8·H.264 CBP(RFC 7742)와 Opus·G.711(RFC 7874)이다. H.264는 packetization-mode=1과 profile-level-id(예: 42e01f)가 협상의 핵심이다.
- 큰 H.264 NAL은 FU-A로 약 1,200바이트 이하로 쪼개고, SPS/PPS는 STAP-A로 묶는다. SPS/PPS를 IDR마다 반복하지 않으면 늦게 붙은 뷰어가 검은 화면을 본다.
- 지터 버퍼는 흔들림을 지연으로 바꾸는 적응형 장치이고, 립싱크는 SR의 NTP↔RTP 쌍으로 두 스트림을 같은 벽시계에 올려 맞춘다.
- 디바이스에서는 H.264 하드웨어 인코딩이 현실적 기본값이다. B 프레임 끄기, SPS/PPS 반복, 요청 시 키프레임, 실행 중 비트레이트 변경을 확인한다.
:::

## 다음 챕터

[품질 제어와 지연 예산](/study/webrtc/09-quality-latency)에서는 이 장에서 본 NACK·PLI·FEC 피드백과 transport-cc를 실제로 써서 손실을 복구하고 대역폭을 추정하는 방법, `setParameters`로 비트레이트·해상도를 조절하는 방법, 그리고 캡처부터 렌더까지의 glass-to-glass 지연을 분해하고 LTE 업링크에 맞춰 튜닝하는 방법을 다룬다.
