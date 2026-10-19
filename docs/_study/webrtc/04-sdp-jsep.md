---
title: "SDP와 Offer/Answer(JSEP)"
description: "브라우저가 실제로 만드는 SDP offer를 한 줄씩 읽고, 코덱 협상과 setCodecPreferences, transceiver direction, 시그널링 상태 머신·재협상·rollback, glare를 푸는 Perfect Negotiation 패턴, SDP munging의 위험까지 다룬다."
date: 2026-10-19
tags: [WebRTC, SDP, JSEP, Signaling]
prev: /study/webrtc/03-signaling
next: /study/webrtc/05-nat-stun
---

# SDP와 Offer/Answer(JSEP)

::: info 학습 목표
- Offer/Answer 모델과 JSEP(RFC 9429)가 브라우저 API로 어떻게 옮겨졌는지 이해한다.
- 실제 Chrome이 만든 SDP offer를 줄 단위로 읽고, BUNDLE·rtcp-mux·setup·fingerprint·ice-ufrag/pwd·extmap의 역할을 설명할 수 있다.
- 코덱 협상 규칙과 `setCodecPreferences()`, transceiver direction 협상을 디바이스(하드웨어 H.264 인코더) 관점에서 설계할 수 있다.
- 시그널링 상태 머신·재협상·rollback을 이해하고, MDN의 Perfect Negotiation 패턴으로 glare를 처리할 수 있다.
- SDP munging이 왜 위험한지, 어떤 표준 API로 대체하는지 안다.
:::

## 1. Offer/Answer 모델과 JSEP

[03장](/study/webrtc/03-signaling)에서 시그널링 서버는 "봉투를 나르는 우체부"일 뿐이라고 했다. 그 봉투에 들어가는 내용물이 <strong>SDP(Session Description Protocol)</strong>다. 이름에 Protocol이 붙어 있지만 SDP는 주고받는 절차가 아니라 <strong>세션을 기술하는 텍스트 포맷</strong>이다. 현재 규격은 RFC 8866(RFC 4566 대체)이고, 원래 SIP·RTSP 같은 VoIP/스트리밍 프로토콜에서 "나는 이 주소·포트로 이 코덱의 미디어를 받겠다"를 적어 보내려고 만든 형식이다.

SDP를 주고받는 절차는 별도 규격인 <strong>Offer/Answer 모델(RFC 3264)</strong>이 정한다. 한쪽이 "내가 할 수 있는 것"을 offer로 제안하면, 상대는 그중 자기도 할 수 있는 것만 골라 answer로 답한다. 결과는 두 능력의 교집합이다. 협상은 반드시 한 번에 하나씩, offer 하나에 answer 하나로 짝지어 진행된다.

이 모델을 브라우저 API로 옮긴 규칙이 <strong>JSEP(JavaScript Session Establishment Protocol)</strong>이다. 2021년 RFC 8829로 처음 표준화됐고, 2024년 <strong>RFC 9429</strong>가 RFC 8829를 대체(obsolete)했다. JSEP의 핵심 철학은 [03장](/study/webrtc/03-signaling)에서 본 그대로다. 브라우저는 SDP를 <strong>만들고 적용하는 일</strong>과 그에 따른 <strong>상태 머신</strong>만 책임지고, SDP를 어떤 전송 수단으로 상대에게 보낼지는 애플리케이션에 맡긴다.

![운영자 브라우저가 createOffer와 setLocalDescription으로 have-local-offer가 되고 offer SDP를 시그널링 서버를 거쳐 로봇에 보내면, 로봇이 setRemoteDescription으로 have-remote-offer, createAnswer와 setLocalDescription으로 stable이 된 뒤 answer를 돌려보내고, 브라우저가 setRemoteDescription(answer)로 stable이 되는 흐름. ICE candidate는 시그널링 서버를 거쳐 양방향으로 계속 오가고 DTLS-SRTP 미디어는 피어끼리 직접 흐른다](/images/study-webrtc/04-offer-answer-flow-light.png)
![운영자 브라우저가 createOffer와 setLocalDescription으로 have-local-offer가 되고 offer SDP를 시그널링 서버를 거쳐 로봇에 보내면, 로봇이 setRemoteDescription으로 have-remote-offer, createAnswer와 setLocalDescription으로 stable이 된 뒤 answer를 돌려보내고, 브라우저가 setRemoteDescription(answer)로 stable이 되는 흐름. ICE candidate는 시그널링 서버를 거쳐 양방향으로 계속 오가고 DTLS-SRTP 미디어는 피어끼리 직접 흐른다](/images/study-webrtc/04-offer-answer-flow-dark.png)

각 API가 실제로 하는 일을 정리하면 다음과 같다.

| API | 하는 일 | signalingState 변화 |
|---|---|---|
| `createOffer()` | 현재 transceiver·DataChannel 구성으로 offer SDP 문자열을 <strong>만들기만</strong> 한다 | 변화 없음 |
| `setLocalDescription(offer)` | offer를 내 설정으로 확정한다. 이때 ICE 후보 수집(gathering)이 시작된다 | stable → have-local-offer |
| `setRemoteDescription(offer)` | 상대 offer를 해석해 transceiver를 만들거나 매칭하고 `ontrack`을 발생시킨다 | stable → have-remote-offer |
| `createAnswer()` | 상대 offer와 내 능력의 교집합으로 answer를 만든다 | 변화 없음 |
| `setLocalDescription(answer)` | answer를 확정한다. 이 시점부터 ICE 연결 검사·DTLS가 진행될 수 있다 | have-remote-offer → stable |
| `setRemoteDescription(answer)` | 상대 answer를 적용해 협상을 끝낸다 | have-local-offer → stable |

`create*`는 문자열을 만들 뿐이고, 실제 부작용(후보 수집, 포트 할당, 코덱 확정)은 `set*`에서 일어난다는 점이 중요하다. 그래서 요즘은 `createOffer()`/`createAnswer()`를 따로 부르지 않고 <strong>인자 없는 `setLocalDescription()`</strong>을 쓴다. 현재 signalingState가 stable이면 offer를, have-remote-offer면 answer를 알아서 만들어 적용한다.

```javascript
// Offerer (operator browser)
const pc = new RTCPeerConnection({ iceServers: [{ urls: "stun:stun.example.com:3478" }] });
pc.onicecandidate = ({ candidate }) => signaler.send({ candidate });

await pc.setLocalDescription();              // creates and applies an offer
signaler.send({ description: pc.localDescription });

// Answerer (robot side, when the offer arrives)
await pc.setRemoteDescription(description);  // type: "offer"
await pc.setLocalDescription();              // creates and applies an answer
signaler.send({ description: pc.localDescription });
```

누가 offer를 만들지는 애플리케이션이 정한다. 예를 들어 [17장](/study/webrtc/17-kvs-architecture)에서 볼 KVS WebRTC는 <strong>뷰어(브라우저)가 offer를 만들고 마스터(디바이스)가 answer한다</strong>는 역할을 고정한다. 역할이 고정돼 있으면 양쪽이 동시에 offer를 보내는 충돌(glare)이 원천적으로 생기지 않는다. 역할을 고정할 수 없을 때 쓰는 해법이 6절의 Perfect Negotiation이다.

## 2. SDP 한 줄씩 읽기

아래는 Chrome 155(headless)에서 실제로 생성한 offer다. 원격 운영 시나리오에 맞춰 <strong>운영자 → 로봇 토크백 오디오(sendrecv)</strong>, <strong>로봇 카메라 영상 수신(recvonly)</strong>, <strong>제어용 DataChannel</strong> 세 가지를 구성했다.

```javascript
pc.addTrack(micTrack, micStream);                    // talkback audio
pc.addTransceiver("video", { direction: "recvonly" }); // robot camera
pc.createDataChannel("control");                     // control channel
await pc.setLocalDescription();
```

원본은 약 6.6KB이고 비디오 m-section에만 `a=` 줄이 164개 있다. VP9 4종, H.264 변형 7종, AV1 2종, RED·ULPFEC·FlexFEC 정의는 `...`로 줄였다. 나머지는 생성된 그대로다.

```text
v=0
o=- 4571671033818102437 2 IN IP4 127.0.0.1
s=-
t=0 0
a=group:BUNDLE 0 1 2
a=extmap-allow-mixed
a=msid-semantic: WMS 8ab77bd9-61fd-4873-9a57-809a16492965
m=audio 9 UDP/TLS/RTP/SAVPF 111 63 9 0 8 13 110 126
c=IN IP4 0.0.0.0
a=rtcp:9 IN IP4 0.0.0.0
a=ice-ufrag:UioA
a=ice-pwd:IFEUGwznwWr/7IhaC2WOdHre
a=ice-options:trickle
a=fingerprint:sha-256 FB:E3:2E:F5:37:30:8E:15:18:AB:2F:0D:46:68:A3:F4:F8:B3:FF:E1:15:FF:C6:32:5B:8D:FE:3C:E6:91:2D:B2
a=setup:actpass
a=mid:0
a=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level
a=extmap:2 http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time
a=extmap:3 http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01
a=extmap:4 urn:ietf:params:rtp-hdrext:sdes:mid
a=sendrecv
a=msid:8ab77bd9-61fd-4873-9a57-809a16492965 91e28b75-537c-4796-a39f-1f53dd302e25
a=rtcp-mux
a=rtcp-rsize
a=rtcp-xr:rcvr-rtt=all
a=rtpmap:111 opus/48000/2
a=rtcp-fb:111 transport-cc
a=fmtp:111 minptime=10;useinbandfec=1
a=rtpmap:63 red/48000/2
a=fmtp:63 111/111
a=rtpmap:9 G722/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:13 CN/8000
a=rtpmap:110 telephone-event/48000
a=rtpmap:126 telephone-event/8000
a=ssrc:886005477 cname:ZZmHq79vN+wZxPCs
a=ssrc:886005477 msid:8ab77bd9-61fd-4873-9a57-809a16492965 91e28b75-537c-4796-a39f-1f53dd302e25
m=video 9 UDP/TLS/RTP/SAVPF 96 97 98 99 100 101 35 36 37 38 102 103 104 107 108 109 114 115 116 117 39 40 41 42 43 44 45 46 47 48 118 119 120 49
c=IN IP4 0.0.0.0
a=rtcp:9 IN IP4 0.0.0.0
a=ice-ufrag:UioA
a=ice-pwd:IFEUGwznwWr/7IhaC2WOdHre
a=ice-options:trickle
a=fingerprint:sha-256 FB:E3:2E:F5:37:30:8E:15:18:AB:2F:0D:46:68:A3:F4:F8:B3:FF:E1:15:FF:C6:32:5B:8D:FE:3C:E6:91:2D:B2
a=setup:actpass
a=mid:1
a=extmap:14 urn:ietf:params:rtp-hdrext:toffset
a=extmap:2 http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time
a=extmap:13 urn:3gpp:video-orientation
a=extmap:3 http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01
a=extmap:5 http://www.webrtc.org/experiments/rtp-hdrext/playout-delay
a=extmap:6 http://www.webrtc.org/experiments/rtp-hdrext/video-content-type
a=extmap:7 http://www.webrtc.org/experiments/rtp-hdrext/video-timing
a=extmap:8 http://www.webrtc.org/experiments/rtp-hdrext/color-space
a=extmap:4 urn:ietf:params:rtp-hdrext:sdes:mid
a=extmap:10 urn:ietf:params:rtp-hdrext:sdes:rtp-stream-id
a=extmap:11 urn:ietf:params:rtp-hdrext:sdes:repaired-rtp-stream-id
a=recvonly
a=rtcp-mux
a=rtcp-rsize
a=rtcp-xr:rcvr-rtt=all
a=rtpmap:96 VP8/90000
a=rtcp-fb:96 goog-remb
a=rtcp-fb:96 transport-cc
a=rtcp-fb:96 ccm fir
a=rtcp-fb:96 nack
a=rtcp-fb:96 nack pli
a=rtpmap:97 rtx/90000
a=fmtp:97 apt=96
...
a=rtpmap:108 H264/90000
a=rtcp-fb:108 goog-remb
a=rtcp-fb:108 transport-cc
a=rtcp-fb:108 ccm fir
a=rtcp-fb:108 nack
a=rtcp-fb:108 nack pli
a=fmtp:108 level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=42e01f
a=rtpmap:109 rtx/90000
a=fmtp:109 apt=108
...
m=application 9 UDP/DTLS/SCTP webrtc-datachannel
c=IN IP4 0.0.0.0
a=ice-ufrag:UioA
a=ice-pwd:IFEUGwznwWr/7IhaC2WOdHre
a=ice-options:trickle
a=fingerprint:sha-256 FB:E3:2E:F5:37:30:8E:15:18:AB:2F:0D:46:68:A3:F4:F8:B3:FF:E1:15:FF:C6:32:5B:8D:FE:3C:E6:91:2D:B2
a=setup:actpass
a=mid:2
a=sctp-port:5000
a=max-message-size:262144
```

SDP는 <strong>세션 섹션 하나</strong>와 그 뒤에 이어지는 <strong>m-section(미디어 섹션) 여러 개</strong>로 이뤄진다. `m=` 줄이 나올 때마다 새 m-section이 시작되고, 다음 `m=` 줄 전까지의 `a=` 줄은 모두 그 m-section에 속한다.

![SDP 구조. 세션 섹션(v·o·s·t, a=group:BUNDLE 0 1 2) 아래에 m=audio(mid:0, sendrecv), m=video(mid:1, recvonly), m=application(mid:2, DataChannel) 세 m-section이 있고, 각 m-section에는 ice-ufrag/pwd·fingerprint·setup·rtcp-mux가 반복된다. BUNDLE에 묶인 세 m-section은 ICE+DTLS 전송 하나(5-tuple 하나)를 공유하고 수신 측은 mid 헤더 확장·SSRC·PT로 m-section을 구분한다](/images/study-webrtc/04-sdp-structure-light.png)
![SDP 구조. 세션 섹션(v·o·s·t, a=group:BUNDLE 0 1 2) 아래에 m=audio(mid:0, sendrecv), m=video(mid:1, recvonly), m=application(mid:2, DataChannel) 세 m-section이 있고, 각 m-section에는 ice-ufrag/pwd·fingerprint·setup·rtcp-mux가 반복된다. BUNDLE에 묶인 세 m-section은 ICE+DTLS 전송 하나(5-tuple 하나)를 공유하고 수신 측은 mid 헤더 확장·SSRC·PT로 m-section을 구분한다](/images/study-webrtc/04-sdp-structure-dark.png)

### 2.1 세션 섹션

| 줄 | 의미 |
|---|---|
| `v=0` | SDP 버전. 항상 0이다 |
| `o=- 4571671033818102437 2 IN IP4 127.0.0.1` | origin. 사용자명(`-`), 세션 ID(무작위 64비트), 세션 버전(`2`, 재협상으로 SDP가 바뀔 때마다 증가), 주소(의미 없는 자리채움 값) |
| `s=-` | 세션 이름. WebRTC에서는 쓰지 않으므로 `-` |
| `t=0 0` | 시작·종료 시각. `0 0`은 무기한 세션 |
| `a=group:BUNDLE 0 1 2` | mid 0·1·2인 m-section을 <strong>전송 하나로 묶는다</strong>(RFC 9143) |
| `a=extmap-allow-mixed` | RTP 헤더 확장의 1바이트·2바이트 형식을 한 스트림에서 섞어 써도 된다(RFC 8285) |
| `a=msid-semantic: WMS …` | 예전 Plan B 시절부터 남은 호환용 줄. `WMS`는 WebRTC MediaStream |

### 2.2 m-section의 전송·보안 줄

세 m-section 모두에 같은 값이 반복되는 줄들이다. BUNDLE로 전송을 공유하므로 값이 같을 수밖에 없다.

| 줄 | 의미 |
|---|---|
| `m=audio 9 UDP/TLS/RTP/SAVPF 111 63 9 …` | 미디어 종류, 포트, 프로토콜, 포맷(PT) 목록. 포트 `9`는 discard 포트로, 아직 후보가 없다는 자리채움 값이다(JSEP 규정). `UDP/TLS/RTP/SAVPF`는 DTLS-SRTP로 보호되는 RTP에 RTCP 피드백(AVPF)을 쓴다는 뜻이다. PT 목록 순서가 곧 <strong>선호 순서</strong>다 |
| `c=IN IP4 0.0.0.0` | 연결 주소. 역시 후보가 생기기 전의 자리채움 값이다 |
| `a=rtcp:9 IN IP4 0.0.0.0` | RTCP 포트. rtcp-mux를 쓰면 의미가 없지만 구형 구현 호환용으로 넣는다 |
| `a=ice-ufrag:UioA` / `a=ice-pwd:…` | ICE 연결 검사용 STUN 메시지의 단기 자격증명. ufrag는 최소 4자, pwd는 최소 22자다(RFC 8839). 값이 바뀌면 ICE restart다([06장](/study/webrtc/06-ice)) |
| `a=ice-options:trickle` | 후보를 SDP에 다 담지 않고 생기는 대로 따로 보내겠다(Trickle ICE, RFC 8838). 그래서 이 SDP에는 `a=candidate` 줄이 하나도 없다 |
| `a=fingerprint:sha-256 FB:E3:…` | DTLS 인증서의 해시. 핸드셰이크 때 받은 인증서가 이 값과 다르면 연결을 끊는다. 시그널링 무결성이 곧 보안인 이유가 여기 있다([10장](/study/webrtc/10-dtls-srtp)) |
| `a=setup:actpass` | DTLS 역할. offer는 반드시 `actpass`(아무 쪽이나 가능)를 쓰고, answer는 `active`(DTLS 클라이언트)를 쓰는 것이 권장이다(RFC 9429) |
| `a=mid:0` | m-section 식별자. BUNDLE 그룹과 RTP의 mid 헤더 확장이 이 값을 참조한다 |
| `a=rtcp-mux` | RTP와 RTCP를 같은 포트로 보낸다(RFC 5761). WebRTC에서는 사실상 필수다 |
| `a=rtcp-rsize` | 축소 크기(reduced-size) RTCP를 허용한다(RFC 5506). 피드백을 작게 자주 보낼 수 있다 |
| `a=rtcp-xr:rcvr-rtt=all` | RTCP XR 수신자 기준 시각 보고(RFC 3611). 수신만 하는 쪽도 RTT를 잴 수 있게 한다 |

<strong>BUNDLE과 rtcp-mux가 왜 중요한가.</strong> 초기 SIP 세계에서는 m-section마다, 그리고 RTP와 RTCP마다 포트를 따로 썼다. 오디오·비디오·데이터면 최대 6개 포트, 즉 6번의 ICE 연결 검사와 6개의 NAT 매핑, TURN을 쓰면 6개의 릴레이 할당이 필요했다. BUNDLE과 rtcp-mux를 쓰면 이것이 <strong>5-tuple 하나</strong>로 줄어든다. LTE 위의 디바이스처럼 NAT 매핑과 TURN 비용에 민감한 환경에서는 결정적인 차이다. 수신 측은 하나의 포트로 들어온 RTP를 mid 헤더 확장, SSRC, PT 순으로 보고 어느 m-section의 패킷인지 가려낸다.

### 2.3 m-section의 미디어 기술 줄

| 줄 | 의미 |
|---|---|
| `a=extmap:3 http://…transport-wide-cc-extensions-01` | RTP 헤더 확장 ID와 URI의 매핑. ID 3번 확장은 transport-wide congestion control 시퀀스 번호라는 뜻이다. abs-send-time, transport-cc는 [09장](/study/webrtc/09-quality-latency)의 혼잡 제어가, sdes:mid는 BUNDLE 디멀티플렉싱이 쓴다 |
| `a=sendrecv` / `a=recvonly` | 이 m-section의 방향. 4절에서 자세히 본다 |
| `a=msid:<stream-id> <track-id>` | 이 m-section으로 보낼 트랙이 속한 MediaStream ID와 트랙 ID(RFC 8830). 상대의 `ontrack` 이벤트에서 `streams[0].id`로 보인다. recvonly인 비디오에는 보낼 트랙이 없어 이 줄이 없다 |
| `a=rtpmap:111 opus/48000/2` | PT 111 = Opus, 클럭 48kHz, 2채널 |
| `a=fmtp:111 minptime=10;useinbandfec=1` | 코덱 파라미터. 최소 패킷 길이 10ms, Opus 인밴드 FEC 사용(RFC 7587) |
| `a=rtpmap:63 red/48000/2` + `a=fmtp:63 111/111` | RED(RFC 2198)로 Opus 프레임을 중복 실어 보내는 오디오 중복 전송 |
| `a=rtpmap:110 telephone-event/48000` | DTMF 신호(RFC 4733). `CN`은 무음 구간의 comfort noise |
| `a=rtcp-fb:96 nack` / `nack pli` / `ccm fir` | 이 PT에 대해 허용하는 RTCP 피드백. 재전송 요청, 키프레임 요청 등이다. `goog-remb`, `transport-cc`는 대역폭 추정 방식이다 |
| `a=rtpmap:97 rtx/90000` + `a=fmtp:97 apt=96` | PT 97은 PT 96(VP8)의 재전송 스트림이다(RFC 4588). `apt`는 associated payload type |
| `a=fmtp:108 …profile-level-id=42e01f` | H.264 파라미터. 3절에서 자세히 본다 |
| `a=ssrc:886005477 cname:…` | 보낼 RTP 스트림의 SSRC와 CNAME. 같은 CNAME을 가진 오디오·비디오는 립싱크 대상이다 |
| `a=sctp-port:5000` / `a=max-message-size:262144` | DataChannel용 SCTP 포트와 최대 메시지 크기(RFC 8841). [11장](/study/webrtc/11-datachannel)에서 다룬다 |

::: tip SDP를 직접 보는 방법
`pc.localDescription.sdp`와 `pc.remoteDescription.sdp`를 콘솔에 찍어 보는 것이 가장 빠르다. Chrome은 `chrome://webrtc-internals`, Firefox는 `about:webrtc`에서 협상 이력 전체를 보여준다([15장](/study/webrtc/15-monitoring-debugging)).
:::

## 3. 코덱 협상과 setCodecPreferences

### 3.1 협상 규칙

코덱 협상은 m-section 단위로 일어난다. 규칙은 단순하다.

- offer의 `m=` 줄 PT 목록은 offerer의 <strong>선호 순서</strong>다.
- answer는 offer에 있던 포맷 중 자기가 지원하는 것만 남긴다. answerer가 코덱 선호(`setCodecPreferences()`)를 정하지 않았다면 JSEP는 answer의 포맷 순서를 offer 순서와 같게 만들도록 정하고, 정했다면 answerer의 선호 순서를 따른다.
- 보낼 때는 <strong>상대 SDP의 PT 매핑</strong>을 쓴다(RFC 9429). 상대가 H.264를 108번이라고 적었으면 108번으로 보낸다.
- 공통 코덱이 하나도 없으면 그 m-section은 거부된다(answer에서 포트 0).
- PT 번호는 그 SDP 안에서만 의미가 있는 별칭이다. 같은 H.264라도 세션마다 108일 수도 102일 수도 있다. 위 출력에서 보듯 Chrome은 동적 PT 범위(96~127)가 모자라자 35~63 같은 미할당 번호까지 쓴다. 따라서 <strong>PT 번호를 하드코딩하면 안 된다.</strong>

비디오 코덱 중 H.264는 `fmtp`까지 맞아야 같은 코덱으로 취급된다는 점이 디바이스 연동에서 자주 문제를 일으킨다.

| 파라미터 | 의미 | 함정 |
|---|---|---|
| `profile-level-id=42e01f` | 앞 2바이트는 프로파일(42e0 = Constrained Baseline), 마지막 1바이트는 레벨(1f = 3.1) | 디바이스 인코더가 High 프로파일만 낸다면, 상대 offer에 그 프로파일이 있는지 확인해야 한다 |
| `packetization-mode=1` | FU-A·STAP-A 패킷화 허용. 0이면 NAL 유닛 하나를 RTP 패킷 하나에 담아야 한다 | 1과 0은 서로 다른 코덱처럼 협상된다. 고해상도 프레임은 사실상 1이 필요하다([08장](/study/webrtc/08-rtp-codecs)) |
| `level-asymmetry-allowed=1` | 송신과 수신 레벨이 달라도 된다 | 없으면 양쪽 레벨을 맞춰야 한다 |

이번 Chrome 155 출력에는 `42001f`, `42e01f`, `4d001f`, `f4001f` 네 가지 profile-level-id가 각각 packetization-mode 0과 1로 들어 있었다. 브라우저 버전·OS·하드웨어 디코더 유무에 따라 이 목록은 달라지므로, 디바이스 인코더 설정은 <strong>실제 상대가 보내는 offer를 보고</strong> 정한다.

### 3.2 setCodecPreferences

농기계나 로봇의 카메라 파이프라인은 대개 하드웨어 H.264 인코더(Jetson NVENC, Raspberry Pi 등, [13장](/study/webrtc/13-native-webrtc))를 쓴다. 디바이스 CPU로 VP8을 소프트웨어 인코딩하는 것은 발열·전력 면에서 손해다. 따라서 운영자 브라우저가 offer를 만들 때부터 H.264를 앞세우는 것이 좋다. 이때 쓰는 표준 API가 `RTCRtpTransceiver.setCodecPreferences()`다.

```javascript
const videoTx = pc.addTransceiver("video", { direction: "recvonly" });

const { codecs } = RTCRtpReceiver.getCapabilities("video");
const isH264CB = (c) =>
  c.mimeType === "video/H264" &&
  /packetization-mode=1/.test(c.sdpFmtpLine) &&
  /profile-level-id=42e01f/.test(c.sdpFmtpLine);

const preferred = [
  ...codecs.filter(isH264CB),                          // 1st: H.264 Constrained Baseline
  ...codecs.filter((c) => c.mimeType === "video/VP8"), // fallback
  ...codecs.filter((c) => c.mimeType === "video/rtx"), // keep retransmission
];
videoTx.setCodecPreferences(preferred);

await pc.setLocalDescription();
```

같은 Chrome 155에서 이 코드로 만든 offer의 비디오 m-section은 이렇게 줄어든다(rtcp-fb·extmap 줄은 생략). 34개였던 PT가 4개가 됐다.

```text
m=video 9 UDP/TLS/RTP/SAVPF 108 109 96 97
...
a=rtpmap:108 H264/90000
a=fmtp:108 level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=42e01f
a=rtpmap:109 rtx/90000
a=fmtp:109 apt=108
a=rtpmap:96 VP8/90000
a=rtpmap:97 rtx/90000
a=fmtp:97 apt=96
```

사용할 때 주의점은 다음과 같다.

- <strong>협상 전에 호출한다.</strong> `setLocalDescription()`(또는 `createOffer()`/`createAnswer()`) 전에 불러야 그 SDP에 반영된다.
- <strong>`negotiationneeded`를 발생시키지 않는다.</strong> 통화 중에 바꾸려면 직접 재협상을 시작해야 한다(MDN).
- <strong>rtx·red·FEC 항목을 빼면 그 기능도 빠진다.</strong> 위 코드처럼 rtx를 남겨야 NACK 재전송이 동작한다. 반대로 rtx·RED·FEC·CN만 넣고 실제 코덱을 하나도 넣지 않으면 `InvalidModificationError`가 난다.
- 수신 능력(`RTCRtpReceiver.getCapabilities()`)에 없는 코덱을 넣으면 `InvalidAccessError`가 난다.
- 지원 범위는 MDN 기준 Baseline 2024다. 2024년 중반 이후의 주요 브라우저는 모두 지원한다.

SDP가 작아지는 것도 부수 효과로 중요하다. 7절에서 보겠지만 임베디드 SDP 파서는 줄 수 제한이 있는 경우가 있다.

## 4. Transceiver와 direction

### 4.1 m-section = transceiver

[02장](/study/webrtc/02-webrtc-api)에서 본 `RTCRtpTransceiver`는 SDP의 m-section 하나와 1:1로 대응한다. transceiver의 `mid`가 곧 `a=mid` 값이다. 하나의 transceiver는 `sender`(보내는 쪽)와 `receiver`(받는 쪽)를 한 쌍으로 가진다.

- `addTrack(track, stream)`은 재사용할 수 있는 transceiver가 있으면 그것을, 없으면 새 transceiver를 `sendrecv`로 만든다.
- `addTransceiver(kind, { direction })`은 트랙 없이도 방향을 정해 m-section을 만든다. 운영자 뷰어처럼 <strong>받기만</strong> 하는 경우에 쓴다.

transceiver에는 방향 속성이 두 개 있다.

| 속성 | 의미 |
|---|---|
| `direction` | 내가 <strong>원하는</strong> 방향. 바꾸면 `negotiationneeded`가 발생한다 |
| `currentDirection` | 마지막 협상으로 <strong>확정된</strong> 방향. 협상 전에는 `null` |

### 4.2 direction 협상 규칙

answer의 방향은 offer 방향을 뒤집은 것과 answerer가 원하는 방향의 교집합이다.

| offer의 방향 | 가능한 answer 방향 | 해석 |
|---|---|---|
| `sendrecv` | `sendrecv` / `sendonly` / `recvonly` / `inactive` | answerer가 마음대로 좁힐 수 있다 |
| `sendonly` | `recvonly` / `inactive` | offerer가 보내기만 하니 answerer는 받거나 거절 |
| `recvonly` | `sendonly` / `inactive` | offerer가 받기만 하니 answerer는 보내거나 거절 |
| `inactive` | `inactive` | 아무도 보내지 않는다 |

3.2절의 offer에 답한 실제 answer의 해당 줄은 다음과 같았다. 같은 Chrome 155에서 두 번째 PeerConnection을 로봇 역할로 두고, 마이크 트랙 없이 비디오만 보내도록(sendonly) 설정했다.

```text
m=audio 9 UDP/TLS/RTP/SAVPF 111 63 9 0 8 13 110 126
a=setup:active
a=mid:0
a=recvonly          # offer was sendrecv, robot only receives talkback
m=video 9 UDP/TLS/RTP/SAVPF 108 109 96 97
a=setup:active
a=mid:1
a=sendonly          # offer was recvonly, robot sends camera video
a=ssrc-group:FID 2474666900 1153399277
```

answer는 `a=setup:active`로 DTLS 클라이언트 역할을 맡았고, 비디오 PT 목록은 offer의 선호 순서(108 → 96)를 그대로 따랐다. `a=ssrc-group:FID`는 원본 영상 SSRC와 그 재전송(rtx) SSRC를 묶는 줄이다(RFC 5576). SDP에는 주석 문법이 없으므로 `#` 뒤 설명은 이해를 돕기 위해 덧붙인 것이다.

### 4.3 토크백 켜고 끄기: 재협상할까, 말까

운영자가 토크백(운영자 음성 → 로봇 스피커)을 켜고 끄는 기능을 생각해 보자. 방법은 두 가지다.

```javascript
const audioTx = pc.getTransceivers().find((t) => t.mid === "0");

// Option A: change direction -> renegotiation (negotiationneeded fires)
audioTx.direction = talkbackOn ? "sendrecv" : "recvonly";

// Option B: keep SDP as is, swap the track -> no renegotiation
await audioTx.sender.replaceTrack(talkbackOn ? micTrack : null);
```

| 방법 | 재협상 | 장점 | 단점 |
|---|---|---|---|
| `direction` 변경 | 필요 | SDP가 실제 상태를 정확히 표현한다. 상대가 "보낼 생각이 없다"를 안다 | offer/answer 왕복이 필요하고 glare 가능성이 생긴다 |
| `replaceTrack(null)` | 불필요 | 즉시 반영되고 시그널링이 없다 | SDP상으로는 여전히 sendrecv다 |
| `track.enabled = false` | 불필요 | 가장 간단하다 | 무음(오디오)·검은 화면(비디오) 프레임을 계속 보낸다 |

원격 운영처럼 "빠른 반응"이 중요한 기능은 처음부터 m-section을 `sendrecv`로 만들어 두고 `replaceTrack()`으로 켜고 끄는 편이 단순하다. 재협상은 카메라를 하나 더 붙이는 것처럼 m-section 구성 자체가 바뀔 때로 미룬다.

::: warning m-section은 지워지지 않는다
`transceiver.stop()`을 호출해도 m-section은 SDP에서 사라지지 않는다. 다음 협상에서 포트가 0으로 바뀌어 "거부됨"으로 남고, 이후 새 transceiver가 그 자리를 재활용할 수 있을 뿐이다. 트랙을 붙였다 뗐다를 반복하는 설계는 m-section 수와 SDP 크기를 키운다.
:::

## 5. 시그널링 상태 머신·재협상·rollback

### 5.1 signalingState

`RTCPeerConnection.signalingState`는 JSEP 상태 머신의 현재 위치다. 값은 `stable`, `have-local-offer`, `have-remote-offer`, `have-local-pranswer`, `have-remote-pranswer`, `closed` 여섯 가지다. `closed`는 `close()`를 부르면 어느 상태에서든 도달하는 종착점이고, 나머지 다섯 상태 사이의 전이는 다음과 같다.

![JSEP 시그널링 상태 머신. stable에서 setRemote(offer)로 have-remote-offer, setLocal(offer)로 have-local-offer가 된다. have-remote-offer는 setLocal(answer)로, have-local-offer는 setRemote(answer)로 stable에 돌아온다. provisional answer 경로로 have-remote-offer에서 setLocal(pranswer)로 have-local-pranswer, have-local-offer에서 setRemote(pranswer)로 have-remote-pranswer가 되고 각각 최종 answer로 stable에 돌아온다. have-remote-offer와 have-local-offer에서는 rollback으로 stable에 돌아갈 수 있다](/images/study-webrtc/04-signaling-states-light.png)
![JSEP 시그널링 상태 머신. stable에서 setRemote(offer)로 have-remote-offer, setLocal(offer)로 have-local-offer가 된다. have-remote-offer는 setLocal(answer)로, have-local-offer는 setRemote(answer)로 stable에 돌아온다. provisional answer 경로로 have-remote-offer에서 setLocal(pranswer)로 have-local-pranswer, have-local-offer에서 setRemote(pranswer)로 have-remote-pranswer가 되고 각각 최종 answer로 stable에 돌아온다. have-remote-offer와 have-local-offer에서는 rollback으로 stable에 돌아갈 수 있다](/images/study-webrtc/04-signaling-states-dark.png)

- <strong>pranswer(provisional answer)</strong>는 SIP의 early media를 위한 잠정 응답이다. 최종 answer 전에 미디어를 먼저 흘릴 수 있지만, 순수 WebRTC 애플리케이션에서는 거의 쓰지 않는다. SIP 게이트웨이를 만들 때나 마주친다.
- 그림에는 생략했지만 have-local-offer에서 새 local offer를 다시 적용하거나, pranswer 상태에서 pranswer를 다시 적용하는 자기 전이도 허용된다.

### 5.2 재협상(renegotiation)

연결이 맺어진 뒤에도 m-section 구성이 바뀌면 offer/answer를 다시 한다. 이것이 재협상이다. 브라우저는 재협상이 필요해지면 stable 상태에서 `negotiationneeded` 이벤트를 발생시킨다.

| `negotiationneeded`를 발생시키는 작업 | 발생시키지 않는 작업 |
|---|---|
| `addTrack()` / `removeTrack()` | `sender.replaceTrack()` |
| `addTransceiver()` | `sender.setParameters()`(비트레이트·해상도 축소 등) |
| `transceiver.direction` 변경, `transceiver.stop()` | `track.enabled` 변경 |
| 첫 번째 `createDataChannel()` | 두 번째 이후 DataChannel 생성(이미 m=application이 있음) |
| `restartIce()` | `setCodecPreferences()`(직접 재협상해야 함) |

재협상은 기존 ICE·DTLS 전송을 그대로 재사용한다. ufrag/pwd가 바뀌지 않으면 ICE 연결 검사를 처음부터 다시 하지 않고, DTLS 핸드셰이크도 다시 하지 않는다. 반대로 `restartIce()`는 새 ufrag/pwd를 넣은 offer를 만들게 해서 ICE를 처음부터 다시 돌린다. 네트워크가 LTE에서 Wi-Fi로 바뀌는 상황의 복구 수단이다([06장](/study/webrtc/06-ice)).

### 5.3 rollback

offer를 적용한 뒤 협상을 없던 일로 되돌리고 싶을 때 쓰는 것이 <strong>rollback</strong>이다. 내용이 빈 `{ type: "rollback" }` 설명을 적용하면 제안 중이던 변경을 모두 버리고 stable로 돌아간다.

```javascript
// Explicit rollback: discard our pending local offer
if (pc.signalingState === "have-local-offer") {
  await pc.setLocalDescription({ type: "rollback" });
}
```

rollback은 have-local-offer, have-remote-offer에서만 가능하다. `stable`, `have-local-pranswer`, `have-remote-pranswer`에서 시도하면 `InvalidStateError`가 난다.

더 자주 쓰이는 것은 <strong>암묵적 rollback(implicit rollback)</strong>이다. have-local-offer 상태에서 상대 offer를 `setRemoteDescription()`으로 적용하면, 브라우저가 내 offer를 자동으로 rollback하고 상대 offer를 받아들인다. 예전 구현은 이 경우 예외를 던졌지만 지금은 명세상 정상 동작이다. 다음 절의 Perfect Negotiation이 이 동작에 기댄다.

::: warning 디바이스 쪽 재협상 지원은 구현마다 다르다
브라우저는 재협상·rollback을 모두 지원하지만, 디바이스에 올리는 네이티브 스택(Pion, GStreamer webrtcbin, KVS C SDK 등)이 어디까지 지원하는지는 구현마다 다르다([13장](/study/webrtc/13-native-webrtc), [19장](/study/webrtc/19-kvs-c-sdk)). 디바이스와 연결할 때는 <strong>시청 시작 시 필요한 m-section을 처음부터 모두 만들어 두고</strong> 재협상 없이 `replaceTrack()`으로 운용하는 설계가 가장 안전하다.
:::

## 6. Perfect Negotiation 패턴

### 6.1 glare

양쪽 모두 재협상을 시작할 수 있는 구조에서는 두 피어가 거의 동시에 offer를 보내는 일이 생긴다. 운영자가 토크백 transceiver를 추가하는 순간 로봇도 보조 카메라 트랙을 추가하는 식이다. 각자 have-local-offer 상태에서 상대 offer를 받게 되는데, 이를 <strong>glare</strong>라고 한다. 해결하지 않으면 양쪽 다 상대 offer를 거부하거나 상태가 꼬인다.

Perfect Negotiation은 W3C WebRTC 명세의 예제로 실려 있고 MDN이 공식 가이드로 자세히 설명하는 패턴이다. 핵심 아이디어는 두 피어에게 <strong>미리 역할을 나눠 주는 것</strong>이다.

- <strong>polite 피어</strong>: 충돌하면 양보한다. 자기 offer를 rollback하고 상대 offer에 answer한다.
- <strong>impolite 피어</strong>: 충돌하면 상대 offer를 무시하고 자기 offer를 밀어붙인다.

역할은 연결 상태와 무관하게 정해 두기만 하면 된다. 시그널링 서버가 먼저 입장한 쪽을 impolite로 지정하거나, 양쪽이 난수를 교환해 정해도 된다.

![Perfect Negotiation에서 glare 처리. Polite 피어와 Impolite 피어가 각각 negotiationneeded로 makingOffer를 true로 두고 offer A와 offer B를 동시에 보내 교차한다. Impolite 피어는 offer A 충돌을 감지해 ignoreOffer를 true로 두고 무시한다. Polite 피어는 offer B 충돌 시 양보해 setRemoteDescription(B)로 implicit rollback한 뒤 setLocalDescription()으로 answer B를 보내고, Impolite 피어가 이를 적용해 stable이 된다. Polite 피어는 stable 복귀 후 남은 변경이 있으면 negotiationneeded가 다시 발생해 offer를 다시 보낸다](/images/study-webrtc/04-perfect-negotiation-light.png)
![Perfect Negotiation에서 glare 처리. Polite 피어와 Impolite 피어가 각각 negotiationneeded로 makingOffer를 true로 두고 offer A와 offer B를 동시에 보내 교차한다. Impolite 피어는 offer A 충돌을 감지해 ignoreOffer를 true로 두고 무시한다. Polite 피어는 offer B 충돌 시 양보해 setRemoteDescription(B)로 implicit rollback한 뒤 setLocalDescription()으로 answer B를 보내고, Impolite 피어가 이를 적용해 stable이 된다. Polite 피어는 stable 복귀 후 남은 변경이 있으면 negotiationneeded가 다시 발생해 offer를 다시 보낸다](/images/study-webrtc/04-perfect-negotiation-dark.png)

### 6.2 MDN 공식 패턴

아래 코드는 MDN의 Perfect negotiation 문서에 실린 현재 패턴을 그대로 옮긴 것이다. `signaler`는 [03장](/study/webrtc/03-signaling)의 WebSocket 시그널링을 감싼 객체로, `send()`와 `onmessage`만 있으면 된다. `polite`는 시그널링 서버가 정해 준 역할 값이다.

```javascript
const config = {
  iceServers: [{ urls: "stun:stun.my-stun-server.tld" }],
};

const signaler = new SignalingChannel();
const pc = new RTCPeerConnection(config);

const constraints = { audio: true, video: true };
const selfVideo = document.querySelector("video.self-view");
const remoteVideo = document.querySelector("video.remote-view");

async function start() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia(constraints);

    for (const track of stream.getTracks()) {
      pc.addTrack(track, stream);
    }
    selfVideo.srcObject = stream;
  } catch (err) {
    console.error(err);
  }
}

pc.ontrack = ({ track, streams }) => {
  track.onunmute = () => {
    if (remoteVideo.srcObject) {
      return;
    }
    remoteVideo.srcObject = streams[0];
  };
};

let makingOffer = false;

pc.onnegotiationneeded = async () => {
  try {
    makingOffer = true;
    await pc.setLocalDescription();
    signaler.send({ description: pc.localDescription });
  } catch (err) {
    console.error(err);
  } finally {
    makingOffer = false;
  }
};

pc.onicecandidate = ({ candidate }) => signaler.send({ candidate });

let ignoreOffer = false;
let isSettingRemoteAnswerPending = false;

signaler.onmessage = async ({ data: { description, candidate } }) => {
  try {
    if (description) {
      const readyForOffer =
        !makingOffer &&
        (pc.signalingState === "stable" || isSettingRemoteAnswerPending);
      const offerCollision = description.type === "offer" && !readyForOffer;

      ignoreOffer = !polite && offerCollision;
      if (ignoreOffer) {
        return;
      }
      isSettingRemoteAnswerPending = description.type === "answer";
      await pc.setRemoteDescription(description);
      isSettingRemoteAnswerPending = false;
      if (description.type === "offer") {
        await pc.setLocalDescription();
        signaler.send({ description: pc.localDescription });
      }
    } else if (candidate) {
      try {
        await pc.addIceCandidate(candidate);
      } catch (err) {
        if (!ignoreOffer) {
          throw err;
        }
      }
    }
  } catch (err) {
    console.error(err);
  }
};
```

### 6.3 줄 단위로 왜 그런가

| 요소 | 역할 | 왜 필요한가 |
|---|---|---|
| `makingOffer` | offer를 만드는 중인지 표시한다 | `signalingState`는 비동기로 바뀐다. `setLocalDescription()`이 끝나기 전에는 아직 stable로 보이므로, 상태만 보면 충돌을 놓친다 |
| `setLocalDescription()` 무인자 | 상태에 맞는 offer/answer를 만들어 적용한다 | `negotiationneeded`는 stable에서만 발생하므로 거기서는 항상 offer가, offer를 받은 뒤에는 항상 answer가 만들어진다. create와 set 사이의 경쟁 구간이 사라진다 |
| `isSettingRemoteAnswerPending` | answer를 적용하는 중인지 표시한다 | answer 적용이 끝나 stable이 되기 직전에 도착한 상대 offer는 충돌이 아니다. 이 플래그가 없으면 정상 offer를 충돌로 오판한다 |
| `readyForOffer` / `offerCollision` | 지금 offer를 받아도 되는지 판단한다 | offer를 만드는 중이 아니고, stable이거나 answer 적용 중이면 받을 수 있다. 그 외에 offer가 오면 충돌이다 |
| `ignoreOffer = !polite && offerCollision` | impolite는 충돌한 offer를 버린다 | 버린 offer에 딸린 ICE 후보도 곧 도착하는데, 그 `addIceCandidate()` 실패는 정상이므로 삼킨다 |
| polite의 `setRemoteDescription(offer)` | 별도 처리 없이 상대 offer를 적용한다 | 5.3절의 암묵적 rollback이 내 offer를 자동으로 버린다. 버려진 변경은 stable 복귀 후 `negotiationneeded`가 다시 발생해 재시도된다 |

이 패턴의 장점은 <strong>양쪽 코드가 완전히 같고 `polite` 값 하나만 다르다</strong>는 것이다. 미디어를 추가·제거하는 코드는 협상을 전혀 신경 쓰지 않고 `addTrack()`만 부르면 된다.

MDN 예제에는 없지만, 실무에서는 같은 구조 위에 ICE 실패 복구를 얹는 경우가 많다. `restartIce()`는 `negotiationneeded`를 발생시키므로 위 패턴이 그대로 처리한다.

```javascript
// Addition on top of the MDN pattern: recover from ICE failure
pc.oniceconnectionstatechange = () => {
  if (pc.iceConnectionState === "failed") {
    pc.restartIce();
  }
};
```

### 6.4 원격 운영 시나리오에서의 선택

- <strong>역할을 고정할 수 있으면 고정한다.</strong> 뷰어가 항상 offer하고 디바이스는 answer만 하는 구조(KVS 방식)라면 glare 자체가 없다. 디바이스 스택의 rollback 지원 여부를 따질 필요도 없다.
- <strong>양방향 재협상이 꼭 필요하면</strong> 운영자 브라우저를 polite, 디바이스를 impolite로 두는 편이 안전하다. 양보(rollback) 로직이 검증된 브라우저 쪽에서만 실행되기 때문이다.
- 다자 구성에서 SFU를 쓰면 SFU가 항상 offerer가 되는 식으로 역할이 정해지는 경우가 많다([12장](/study/webrtc/12-topology-sfu)).

## 7. SDP munging의 위험

### 7.1 munging이란

<strong>SDP munging</strong>은 `createOffer()`/`createAnswer()`가 만든 SDP 문자열을 정규식 등으로 고친 뒤 `setLocalDescription()`에 넘기는 관행이다. 표준 API가 부족하던 시절에는 코덱 순서 바꾸기, `b=AS:` 줄로 비트레이트 제한, Opus `stereo=1` 추가, simulcast용 SSRC 그룹 삽입 같은 일을 모두 이렇게 했다. 지금도 오래된 예제 코드에 흔히 남아 있다.

문제는 이것이 <strong>표준 위반</strong>이라는 점이다. RFC 9429는 `createOffer()`/`createAnswer()`가 만든 SDP를 `setLocalDescription()`에 넘기기 전에 바꾸면 안 된다(MUST NOT)고 명시하고, 정밀한 제어가 필요하면 createOffer 옵션이나 RtpTransceiver API를 쓰라고 한다.

munging이 위험한 이유는 다음과 같다.

- <strong>브라우저 업데이트에 깨진다.</strong> SDP 출력 형식은 API 계약이 아니다. 줄 순서, PT 번호, 새 속성 추가는 버전마다 바뀐다. 이번 출력만 봐도 PT 번호 35~49 같은 값은 정규식이 "96 이상"을 가정했다면 놓쳤을 것이다.
- <strong>브라우저가 점점 거부한다.</strong> Chromium의 WebRTC 팀은 2025년 4월 discuss-webrtc 공지에서 `ice-ufrag`/`ice-pwd`를 바꾼 SDP의 `setLocalDescription()`을 앞으로 거부하겠다고 밝혔고, 추가 제한도 이어질 가능성이 높다고 예고했다.
- <strong>내부 상태와 SDP가 어긋난다.</strong> 문자열만 바꾸고 transceiver·sender 상태는 그대로이므로, `getParameters()`나 `getStats()`가 보여주는 값과 실제 협상 내용이 달라진다. 디버깅이 매우 어려워진다.

### 7.2 표준 API로 대체하기

| munging으로 하던 일 | 표준 대안 |
|---|---|
| 코덱 순서 변경·제거 | `transceiver.setCodecPreferences()` (3.2절) |
| `b=AS:`로 송신 비트레이트 제한 | `sender.setParameters()`의 `encodings[i].maxBitrate` ([09장](/study/webrtc/09-quality-latency)) |
| 해상도 낮추기 | `encodings[i].scaleResolutionDownBy` |
| simulcast SSRC 그룹 삽입 | `addTransceiver(track, { sendEncodings: [{ rid: "h" }, { rid: "l", scaleResolutionDownBy: 2 }] })` ([12장](/study/webrtc/12-topology-sfu)) |
| 사설 IP 후보 제거, TURN만 쓰기 | `RTCPeerConnection({ iceTransportPolicy: "relay" })` ([07장](/study/webrtc/07-turn)) |
| m-section 방향 바꾸기 | `transceiver.direction` |
| ICE 자격증명 교체 | `restartIce()` |

Opus `stereo=1` 같은 일부 `fmtp` 파라미터는 아직 깔끔한 표준 API가 없어 munging이 남아 있는 영역이다. 꼭 써야 한다면 바꾸는 범위를 한 줄로 최소화하고, 브라우저 버전별 회귀 테스트를 붙인다.

### 7.3 디바이스 관점: SDP 크기

munging을 하고 싶어지는 또 하나의 이유가 SDP 크기다. 2절에서 본 Chrome 155 기본 offer는 약 6.6KB이고, 비디오 m-section 하나에 `a=` 줄이 164개였다. 임베디드 SDP 파서는 메모리를 아끼려고 고정 크기 배열을 쓰는 경우가 많다. 예를 들어 KVS WebRTC C SDK는 m-section당 `a=` 속성 최대 개수(`MAX_SDP_ATTRIBUTES_COUNT`)의 기본값이 256이고, README에서 "큰 recvonly offer를 보내는 브라우저와 연동하려면 320 정도로 올리라"고 안내한다([19장](/study/webrtc/19-kvs-c-sdk)).

브라우저 버전이 올라가 코덱이 하나 더 추가되면 어느 날 갑자기 디바이스가 offer 파싱에 실패할 수 있다는 뜻이다. 대응 순서는 다음과 같다.

1. 브라우저 쪽에서 `setCodecPreferences()`로 <strong>디바이스가 실제로 쓰는 코덱만</strong> 남긴다. 표준 API로 SDP를 줄이는 방법이다.
2. 디바이스 SDK의 SDP 한도를 여유 있게 잡고 빌드한다.
3. 새 브라우저 버전이 나오면 실제 offer를 디바이스 파서에 넣어 보는 회귀 테스트를 CI에 둔다.

::: tip 핵심 정리
- SDP는 세션 기술 포맷(RFC 8866), Offer/Answer는 교환 절차(RFC 3264), JSEP(RFC 9429, RFC 8829 대체)는 이를 브라우저 API와 상태 머신으로 옮긴 규칙이다.
- 실제 부작용은 `set*Description`에서 일어난다. 요즘은 인자 없는 `setLocalDescription()`으로 offer/answer 생성과 적용을 한 번에 한다.
- BUNDLE과 rtcp-mux는 모든 미디어를 5-tuple 하나로 묶어 ICE 검사·NAT 매핑·TURN 할당을 하나로 줄인다. fingerprint는 DTLS 인증서를 시그널링에 묶고, ice-ufrag/pwd는 ICE 검사의 자격증명이다.
- 코덱은 m-section 단위로 교집합 협상되며 PT 번호는 하드코딩하면 안 된다. 하드웨어 H.264 인코더를 쓰는 디바이스와 연결할 때는 `setCodecPreferences()`로 H.264를 앞세우고 SDP도 줄인다.
- direction은 offer를 뒤집은 것과 answerer 희망의 교집합이다. 빠르게 켜고 끄는 기능은 재협상 대신 `replaceTrack()`으로 처리한다.
- glare는 Perfect Negotiation(polite/impolite, makingOffer, ignoreOffer, 무인자 setLocalDescription, 암묵적 rollback)으로 해결하고, 역할을 고정할 수 있다면 고정하는 것이 가장 단순하다.
- SDP munging은 표준 위반이고 브라우저가 점점 거부하는 방향이다. 표준 API로 대체한다.
:::

## 다음 챕터

[NAT와 STUN](/study/webrtc/05-nat-stun)에서는 SDP에 자리채움 값(포트 9, `0.0.0.0`)으로 남아 있던 "실제 주소"를 어떻게 알아내는지 다룬다. NAT가 P2P 연결을 막는 원리를 RFC 4787의 매핑·필터링 동작으로 분해하고, STUN Binding으로 공인 주소를 얻는 과정과 LTE·CGNAT 환경의 디바이스가 왜 TURN을 필요로 하는지 살펴본다.
