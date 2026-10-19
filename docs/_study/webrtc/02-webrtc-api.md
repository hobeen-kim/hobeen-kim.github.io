---
title: "WebRTC API 한눈에"
description: "getUserMedia·MediaStreamTrack으로 미디어를 얻고, RTCPeerConnection의 생명주기와 네 가지 상태 값, RTCRtpTransceiver·Sender·Receiver와 RTCDataChannel의 역할을 정리한 뒤, 한 페이지 안에서 두 PeerConnection을 연결하는 loopback 예제를 돌려본다."
date: 2026-10-19
tags: [WebRTC, JavaScript, Browser API]
prev: /study/webrtc/01-why-webrtc
next: /study/webrtc/03-signaling
---

# WebRTC API 한눈에

::: info 학습 목표
- `getUserMedia`로 카메라를 열고 `MediaStream`과 `MediaStreamTrack`의 관계와 주요 속성을 설명할 수 있다.
- `RTCPeerConnection`의 생명주기를 따라 `signalingState`·`iceGatheringState`·`iceConnectionState`·`connectionState`가 어떤 값으로 변하는지 안다.
- `RTCRtpTransceiver`·`RTCRtpSender`·`RTCRtpReceiver`의 역할을 구분하고, 수신 전용 연결과 재협상 없는 트랙 교체를 구현할 수 있다.
- `RTCDataChannel`을 만들고 메시지를 주고받을 수 있다.
- 같은 페이지 안 두 PeerConnection을 직접 연결하는 loopback 예제로 전체 흐름을 손으로 확인한다.
:::

## 1. 미디어 획득 — getUserMedia·MediaStream·MediaStreamTrack

WebRTC로 무언가를 보내려면 먼저 보낼 미디어가 있어야 한다. 브라우저에서 카메라·마이크를 여는 진입점이 `navigator.mediaDevices.getUserMedia()`다. 이 API는 엄밀히 말하면 WebRTC 명세가 아니라 W3C Media Capture and Streams 명세에 속하지만, WebRTC와 늘 함께 쓰인다.

```js
async function openCamera() {
  const constraints = {
    audio: false,
    video: {
      width: { ideal: 1280 },
      height: { ideal: 720 },
      frameRate: { ideal: 30, max: 30 },
      facingMode: 'environment', // 모바일이면 후면 카메라 우선
    },
  };

  try {
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    const [track] = stream.getVideoTracks();
    // 요청값이 아니라 실제로 적용된 값은 getSettings()로 확인한다
    console.log(track.label, track.getSettings());
    return stream;
  } catch (err) {
    switch (err.name) {
      case 'NotAllowedError':      // 사용자가 거부했거나 권한 정책이 막음
        console.error('카메라 권한이 없다');
        break;
      case 'NotFoundError':        // 조건에 맞는 장치가 없음
        console.error('카메라를 찾지 못했다');
        break;
      case 'NotReadableError':     // 다른 앱이 점유 중이거나 하드웨어 오류
        console.error('카메라를 열 수 없다');
        break;
      case 'OverconstrainedError': // exact·min·max 조건을 만족할 장치가 없음
        console.error('조건을 만족하지 못한 제약:', err.constraint);
        break;
      default:
        console.error(err);
    }
    throw err;
  }
}
```

몇 가지 규칙을 알아두면 삽질이 줄어든다.

- <strong>보안 컨텍스트에서만 동작한다.</strong> HTTPS 페이지나 `http://localhost`에서만 `navigator.mediaDevices`가 존재한다. 사내망 IP로 HTTP 접속하면 `navigator.mediaDevices`가 `undefined`라서 "getUserMedia is not a function" 같은 엉뚱한 오류가 난다.
- <strong>제약(constraints)은 희망 사항이다.</strong> `ideal`은 "가능하면", `min`·`max`·`exact`는 "반드시"다. `exact`를 남발하면 장치가 조금만 달라도 `OverconstrainedError`가 난다. 요청과 실제 결과가 다를 수 있으므로 `getSettings()`로 확인한다.
- <strong>권한 프롬프트는 사용자 몫이다.</strong> 사용자가 한 번 거부하면 페이지가 다시 물어볼 방법이 없고, 브라우저 설정에서 풀어야 한다. 카메라를 열기 전에 왜 필요한지 UI로 먼저 설명하는 편이 낫다.

### MediaStream과 MediaStreamTrack

`getUserMedia`가 돌려주는 `MediaStream`은 <strong>트랙의 묶음</strong>일 뿐이다. 실제 미디어의 단위는 `MediaStreamTrack`이고, 트랙 하나가 카메라 영상 하나 또는 마이크 음성 하나다. WebRTC로 보내는 것도 스트림이 아니라 트랙이다. 스트림은 "이 영상과 이 음성은 같은 사람 것이니 함께 재생(립싱크)하라"는 묶음 정보로만 쓰인다.

| 속성·메서드 | 의미 | 실무 포인트 |
|---|---|---|
| `kind` | `"audio"` 또는 `"video"` | |
| `id`, `label` | 트랙 식별자, 장치 이름 | 로그에 `label`을 남기면 어떤 카메라가 열렸는지 추적하기 쉽다 |
| `enabled` | 쓰기 가능. `false`면 영상은 검은 프레임, 음성은 무음이 된다 | 연결은 유지한 채 "화면 가리기"를 할 때 |
| `muted` | 읽기 전용. 소스가 일시적으로 데이터를 못 줄 때 `true` | `enabled`와 헷갈리지 말 것. 앱이 바꾸는 값이 아니다 |
| `readyState` | `"live"` 또는 `"ended"` | `ended`가 되면 되살릴 수 없다 |
| `stop()` | 트랙 종료, 장치 해제 | 모든 트랙을 `stop()`해야 카메라 표시등이 꺼진다 |
| `getSettings()` | 실제 적용된 해상도·fps 등 | |
| `applyConstraints()` | 열린 트랙의 제약 변경 | 해상도·fps를 재협상 없이 바꿀 때 |

카메라 말고 화면을 보내려면 `navigator.mediaDevices.getDisplayMedia()`를, 장치 목록이 필요하면 `enumerateDevices()`를 쓴다. `enumerateDevices()`가 돌려주는 장치 이름(`label`)은 카메라·마이크 권한을 얻기 전에는 빈 문자열이다. 반면 농기계 디바이스 같은 네이티브 환경에는 `getUserMedia`가 없다. V4L2로 카메라를 열고 하드웨어 인코더 출력을 WebRTC 스택에 직접 넣는다([13장](/study/webrtc/13-native-webrtc)). 브라우저 쪽은 이 장에서 다루는 운영자 뷰어 역할이 주가 된다.

## 2. RTCPeerConnection 생명주기와 상태

`RTCPeerConnection`은 WebRTC의 중심 객체다. 상대 피어 하나와의 연결 하나를 나타내고, 그 안에서 ICE·DTLS·SRTP·SCTP를 모두 관리한다. 뷰어 세 명에게 영상을 보내는 디바이스라면 PeerConnection 세 개가 필요하다.

```js
const pc = new RTCPeerConnection({
  iceServers: [
    { urls: 'stun:stun.example.com:3478' },
    {
      urls: [
        'turn:turn.example.com:3478?transport=udp',
        'turns:turn.example.com:443?transport=tcp',
      ],
      username: '1760860800:operator-42',      // 시간제한 credential (07장)
      credential: '<서버가 HMAC으로 발급한 비밀번호>',
    },
  ],
  iceTransportPolicy: 'all',  // 'relay'면 TURN 릴레이 후보만 쓴다
  bundlePolicy: 'max-bundle', // 모든 미디어를 전송 하나에 묶는다
});
```

| 설정 | 값 | 의미 |
|---|---|---|
| `iceServers` | STUN/TURN 서버 목록 | NAT 통과용. 비우면 host 후보만 쓴다([05](/study/webrtc/05-nat-stun)~[07장](/study/webrtc/07-turn)) |
| `iceTransportPolicy` | `"all"`, `"relay"` | `relay`는 TURN만 사용. IP 노출 방지·TURN 테스트용 |
| `bundlePolicy` | `"balanced"`, `"max-compat"`, `"max-bundle"` | 미디어를 몇 개의 전송으로 나눌지. 최신 피어끼리는 `max-bundle`이 무난 |
| `rtcpMuxPolicy` | `"require"` | RTP와 RTCP를 한 포트로. 사실상 기본값 그대로 |
| `iceCandidatePoolSize` | 정수 | offer 전에 후보를 미리 수집해 둘 개수 |
| `certificates` | `RTCCertificate[]` | DTLS 인증서 지정([10장](/study/webrtc/10-dtls-srtp)) |

### 생명주기

PeerConnection 하나가 태어나서 연결되고 닫히기까지는 대략 다음 순서를 밟는다.

1. <strong>생성</strong>: `new RTCPeerConnection(config)`
2. <strong>보낼 것 등록</strong>: `addTrack()`·`addTransceiver()`·`createDataChannel()`. 처음 등록하면 `negotiationneeded` 이벤트가 발생한다.
3. <strong>offer 생성·적용</strong>: `createOffer()` → `setLocalDescription(offer)`. 이 순간 ICE 후보 수집이 시작되고 `icecandidate` 이벤트가 하나씩 발생한다.
4. <strong>시그널링</strong>: offer와 후보를 상대에게 보낸다. 방법은 앱 마음이다([03장](/study/webrtc/03-signaling)).
5. <strong>상대 쪽</strong>: `setRemoteDescription(offer)` → `createAnswer()` → `setLocalDescription(answer)` → answer와 후보를 돌려보낸다.
6. <strong>answer 적용</strong>: `setRemoteDescription(answer)`. 상대 후보는 `addIceCandidate()`로 넣는다.
7. <strong>연결</strong>: ICE가 후보 쌍을 점검해 통하는 경로를 찾고, 그 위에서 DTLS 핸드셰이크가 끝나면 미디어가 흐른다.
8. <strong>종료</strong>: `close()`. 닫힌 PeerConnection은 재사용할 수 없고, 다시 연결하려면 새로 만든다.

이 과정을 따라가는 동안 PeerConnection은 네 가지 상태 값을 바꿔가며 진행 상황을 알린다. offerer 쪽에서 본 전형적인 흐름은 다음과 같다.

![offerer 쪽 RTCPeerConnection의 네 상태 값이 시간에 따라 변하는 표. 생성 직후 모두 stable/new, setLocalDescription(offer) 후 signalingState가 have-local-offer, iceGatheringState가 gathering이 되고, answer와 원격 후보를 받으면 signalingState가 stable로 돌아오며 iceConnectionState는 checking, connectionState는 connecting이 된다. 후보 쌍이 연결되면 iceConnectionState가 connected, DTLS까지 끝나면 connectionState가 connected가 된다. 네트워크가 끊기면 두 값이 disconnected, close() 후에는 closed가 되고 iceGatheringState는 변하지 않는다](/images/study-webrtc/02-state-timeline-light.png)
![offerer 쪽 RTCPeerConnection의 네 상태 값이 시간에 따라 변하는 표. 생성 직후 모두 stable/new, setLocalDescription(offer) 후 signalingState가 have-local-offer, iceGatheringState가 gathering이 되고, answer와 원격 후보를 받으면 signalingState가 stable로 돌아오며 iceConnectionState는 checking, connectionState는 connecting이 된다. 후보 쌍이 연결되면 iceConnectionState가 connected, DTLS까지 끝나면 connectionState가 connected가 된다. 네트워크가 끊기면 두 값이 disconnected, close() 후에는 closed가 되고 iceGatheringState는 변하지 않는다](/images/study-webrtc/02-state-timeline-dark.png)

후보 수집 완료(`complete`) 시점은 연결 성공과 독립적이다. 수집이 먼저 끝날 수도 있고, 연결된 뒤에도 느린 TURN 서버 응답을 기다리며 `gathering`에 머물 수도 있다. 그림은 가능한 흐름 하나일 뿐이다.

### 네 가지 상태 값

각 상태 값이 가질 수 있는 값은 명세에 정확히 정해져 있다.

<strong>signalingState</strong> — offer/answer 교환이 어디까지 진행됐는가

| 값 | 의미 |
|---|---|
| `stable` | 진행 중인 offer/answer가 없다. 초기 상태이자 교환이 끝난 상태 |
| `have-local-offer` | 내 offer를 `setLocalDescription`했고 answer를 기다린다 |
| `have-remote-offer` | 상대 offer를 `setRemoteDescription`했고 내가 answer할 차례다 |
| `have-local-pranswer` | 상대 offer에 임시 응답(provisional answer)을 로컬에 적용했다 |
| `have-remote-pranswer` | 내 offer에 대한 상대의 임시 응답을 적용했다 |
| `closed` | PeerConnection이 닫혔다 |

pranswer는 SIP 게이트웨이 연동 같은 특수한 경우에만 쓰이고, 일반 앱에서는 `stable` ↔ `have-local-offer`/`have-remote-offer` 왕복만 본다. 이 상태 머신과 재협상·rollback은 [04장](/study/webrtc/04-sdp-jsep)에서 자세히 다룬다.

<strong>iceGatheringState</strong> — 내 후보 수집이 어디까지 왔는가

| 값 | 의미 |
|---|---|
| `new` | 아직 수집을 시작하지 않았다 |
| `gathering` | 후보를 수집하고 있다 |
| `complete` | 수집이 끝났다. 이때 `icecandidate` 이벤트가 `candidate: null`로 한 번 더 발생한다 |

<strong>iceConnectionState</strong> — ICE가 통하는 경로를 찾았는가

| 값 | 의미 |
|---|---|
| `new` | 원격 후보를 기다리거나 수집 중이다 |
| `checking` | 원격 후보를 받아 후보 쌍을 점검하고 있다. 아직 통하는 쌍은 없다 |
| `connected` | 모든 컴포넌트에 쓸 수 있는 쌍을 찾았다. 더 나은 쌍을 계속 찾을 수 있다 |
| `completed` | 수집과 점검이 모두 끝났고 모든 컴포넌트가 연결됐다 |
| `failed` | 모든 쌍을 점검했지만 통하는 쌍을 찾지 못했다 |
| `disconnected` | 일부 컴포넌트의 연결 점검이 실패했다. 일시적일 수 있고 저절로 회복되기도 한다 |
| `closed` | ICE 에이전트가 종료됐다 |

<strong>connectionState</strong> — 결국 연결이 쓸 만한가

| 값 | 의미 |
|---|---|
| `new` | 전송들이 아직 시작 전이다 |
| `connecting` | 하나 이상의 전송이 연결을 수립하는 중이다(ICE 점검 또는 DTLS 핸드셰이크) |
| `connected` | 모든 전송이 연결됐다(ICE 연결 + DTLS 완료) |
| `disconnected` | 하나 이상의 전송이 끊겼다 |
| `failed` | 하나 이상의 전송이 실패했다 |
| `closed` | PeerConnection이 닫혔다 |

`iceConnectionState`가 ICE 계층만 보는 반면 `connectionState`는 <strong>ICE와 DTLS 전송 상태를 합친 종합 지표</strong>다. ICE는 연결됐는데 DTLS 핸드셰이크가 인증서 지문 불일치로 실패하면 `iceConnectionState`는 `connected`인데 `connectionState`는 `failed`가 된다. 앱 로직은 `connectionState`를 기준으로 짜고, `iceConnectionState`는 원인 진단에 쓴다.

### 상태 이벤트 다루기

```js
pc.addEventListener('connectionstatechange', () => {
  switch (pc.connectionState) {
    case 'connected':
      clearTimeout(reconnectTimer);
      showStatus('연결됨');
      break;
    case 'disconnected':
      // 일시적 끊김일 수 있다. 잠시 기다려 본다
      showStatus('네트워크 불안정');
      reconnectTimer = setTimeout(() => pc.restartIce(), 5000);
      break;
    case 'failed':
      // 모든 경로가 실패했다. ICE restart로 후보를 새로 수집한다
      pc.restartIce();
      break;
    case 'closed':
      cleanup();
      break;
  }
});
```

`restartIce()`를 호출하면 `negotiationneeded`가 발생하고, 다음 offer가 새 ICE 자격증명(ufrag/pwd)을 담아 후보 수집부터 다시 한다. 즉 ICE restart도 결국 시그널링으로 offer/answer를 한 번 더 주고받는 일이다([06장](/study/webrtc/06-ice)).

::: warning 상태 처리에서 자주 밟는 함정
- <strong>`setRemoteDescription` 전에 `addIceCandidate`를 부르면 실패한다.</strong> 원격 설명이 없는 상태에서는 `InvalidStateError`로 거부된다. 시그널링에서 후보가 SDP보다 먼저 도착할 수 있으므로, 원격 설명이 적용될 때까지 후보를 큐에 쌓아 두는 코드가 필요하다([03장](/study/webrtc/03-signaling)).
- <strong>`disconnected`를 곧바로 실패로 취급하지 않는다.</strong> LTE 핸드오버나 와이파이 순간 끊김에도 `disconnected`가 뜨고, 몇 초 안에 `connected`로 돌아오는 경우가 많다. 성급하게 PeerConnection을 새로 만들면 오히려 복구가 늦어진다.
- <strong>`close()`는 이벤트를 발생시키지 않는다.</strong> 내가 `close()`를 부르면 상태가 `closed`로 바뀌지만 `connectionstatechange`가 오지 않는다. 정리 로직은 `close()`를 부르는 쪽에서 직접 실행한다.
- <strong>상대가 탭을 닫아도 즉시 알 수 없다.</strong> 상대가 사라지면 ICE 동의 갱신(consent freshness, RFC 7675) 응답이 끊기고, 동의가 만료되기까지 수십 초가 걸린다. 빠른 종료 감지가 필요하면 시그널링 서버의 퇴장 알림이나 DataChannel `close` 이벤트를 함께 쓴다.
- <strong>`connected`와 `completed`를 모두 성공으로 본다.</strong> ICE가 `completed`까지 가는지는 구현과 상황에 따라 다르다. `iceConnectionState === 'completed'`만 기다리는 코드는 영원히 기다릴 수 있다.
:::

### 이벤트 정리

| 이벤트 | 발생 시점 | 보통 하는 일 |
|---|---|---|
| `negotiationneeded` | 트랙·트랜시버·첫 DataChannel 추가, `restartIce()` 등으로 재협상이 필요할 때 | offer 생성·전송(Perfect Negotiation, [04장](/study/webrtc/04-sdp-jsep)) |
| `icecandidate` | 로컬 후보를 하나 찾을 때마다, 끝나면 `candidate: null` | 시그널링으로 상대에게 전달 |
| `icecandidateerror` | STUN/TURN 서버 접속 실패 | TURN 설정 오류 진단 |
| `icegatheringstatechange` | `iceGatheringState` 변경 | non-trickle 방식이면 `complete`를 기다렸다 SDP 전송 |
| `iceconnectionstatechange` | `iceConnectionState` 변경 | 진단 로그 |
| `connectionstatechange` | `connectionState` 변경 | UI 상태, 재연결 로직 |
| `signalingstatechange` | `signalingState` 변경 | 협상 디버깅 |
| `track` | 원격 트랙이 생겼을 때 | `<video>`에 연결 |
| `datachannel` | 상대가 만든 DataChannel이 열릴 때 | 핸들러 등록 |

## 3. RTCRtpTransceiver·Sender·Receiver

PeerConnection 안에서 실제로 미디어를 나르는 객체들의 관계는 다음과 같다.

![API 객체 관계도. getUserMedia가 MediaStream을 만들고 그 안에 video·audio MediaStreamTrack이 있다. 각 트랙은 addTrack()으로 RTCPeerConnection 안의 RTCRtpTransceiver(mid 0 video, mid 1 audio)에 속한 RTCRtpSender에 연결된다. 각 트랜시버는 보낼 track을 가진 RTCRtpSender와 받은 track을 ontrack으로 넘기는 RTCRtpReceiver 쌍으로 이뤄진다. PeerConnection 안에는 RTCDataChannel과 BUNDLE로 공유되는 ICE·DTLS 전송이 있고, 원격 피어와 SRTP·SCTP/DTLS로 통신한다](/images/study-webrtc/02-api-objects-light.png)
![API 객체 관계도. getUserMedia가 MediaStream을 만들고 그 안에 video·audio MediaStreamTrack이 있다. 각 트랙은 addTrack()으로 RTCPeerConnection 안의 RTCRtpTransceiver(mid 0 video, mid 1 audio)에 속한 RTCRtpSender에 연결된다. 각 트랜시버는 보낼 track을 가진 RTCRtpSender와 받은 track을 ontrack으로 넘기는 RTCRtpReceiver 쌍으로 이뤄진다. PeerConnection 안에는 RTCDataChannel과 BUNDLE로 공유되는 ICE·DTLS 전송이 있고, 원격 피어와 SRTP·SCTP/DTLS로 통신한다](/images/study-webrtc/02-api-objects-dark.png)

- <strong>RTCRtpTransceiver</strong>는 SDP의 m-line(미디어 섹션) 하나에 대응한다. 표준 SDP 형식인 Unified Plan에서는 "트랙 하나 = m-line 하나 = 트랜시버 하나"다. 트랜시버는 `mid`(미디어 섹션 식별자)와 `direction`을 가지며, 항상 sender 하나와 receiver 하나를 쌍으로 갖는다.
- <strong>RTCRtpSender</strong>는 로컬 트랙을 인코딩해 RTP로 보낸다. 비트레이트·해상도 축소 같은 인코딩 파라미터를 여기서 조정한다.
- <strong>RTCRtpReceiver</strong>는 RTP를 받아 디코딩하고, 그 결과를 원격 트랙(`receiver.track`)으로 내놓는다. 이 트랙이 `track` 이벤트로 앱에 전달된다.

### addTrack과 addTransceiver

`addTrack(track, ...streams)`은 트랙을 보내겠다고 등록하는 가장 쉬운 방법이다. 내부적으로 쓸 수 있는 트랜시버를 찾거나 새로 만들고(`direction: "sendrecv"`), 그 sender를 돌려준다. 함께 넘긴 스트림 정보는 SDP의 msid로 실려 상대의 `event.streams`가 된다.

`addTransceiver(trackOrKind, init)`는 트랜시버를 직접 만든다. 방향을 명시할 수 있다는 점이 핵심이다. 농기계 영상을 보기만 하는 운영자 브라우저는 보낼 카메라가 없으므로, 수신 전용 트랜시버로 offer를 만든다.

```js
// 운영자 뷰어: 카메라 없이 영상·음성을 받기만 한다
const pc = new RTCPeerConnection(config);
pc.addTransceiver('video', { direction: 'recvonly' });
pc.addTransceiver('audio', { direction: 'recvonly' });

pc.addEventListener('track', (event) => {
  // 상대가 스트림 정보를 안 실었으면 event.streams가 비어 있을 수 있다
  const stream = event.streams[0] ?? new MediaStream([event.track]);
  if (remoteVideo.srcObject !== stream) remoteVideo.srcObject = stream;
});

const offer = await pc.createOffer();
await pc.setLocalDescription(offer);
// → offer를 시그널링으로 디바이스에 보낸다
```

`addTrack`만 알고 있으면 "보낼 게 없는데 어떻게 offer를 만들지?"에서 막힌다. 예전에는 `createOffer({ offerToReceiveVideo: true })` 옵션을 썼지만, 이는 레거시 방식이고 지금은 `recvonly` 트랜시버가 정석이다.

### 방향(direction)

| 값 | 의미 |
|---|---|
| `sendrecv` | 보내고 받기를 모두 제안 |
| `sendonly` | 보내기만 제안 |
| `recvonly` | 받기만 제안 |
| `inactive` | 둘 다 하지 않음(m-line은 유지) |
| `stopped` | 종료된 트랜시버. `stop()`으로만 진입하고, `direction`에 직접 대입하면 `TypeError` |

`direction`은 "내가 원하는 방향"이고, 실제 협상 결과는 `currentDirection`에 있다. `direction`을 바꾸면 즉시 반영되지 않고 `negotiationneeded`가 발생해 재협상이 끝난 뒤에 적용된다. 예를 들어 운영자가 마이크를 켜서 디바이스 스피커로 말하려면 audio 트랜시버를 `recvonly`에서 `sendrecv`로 바꾸고 재협상해야 한다.

### replaceTrack — 재협상 없는 트랙 교체

`sender.replaceTrack(newTrack)`은 협상을 다시 하지 않고 보내는 트랙만 바꾼다. 같은 종류(video→video)이고 협상된 코덱으로 인코딩할 수 있으면 즉시 반영된다.

```js
// 전면 ↔ 후면 카메라 전환
async function switchCamera(sender, facingMode) {
  const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode } });
  const [newTrack] = stream.getVideoTracks();
  const oldTrack = sender.track;
  await sender.replaceTrack(newTrack);
  oldTrack?.stop(); // 이전 카메라 해제
}

// 영상 송출을 잠시 멈추되 연결과 m-line은 유지
await sender.replaceTrack(null);
```

`track.enabled = false`가 검은 프레임을 계속 보내는 것과 달리, `replaceTrack(null)`은 아예 아무것도 보내지 않는다. 대역폭을 아끼려면 후자가 낫다.

### 인코딩 파라미터

sender의 `getParameters()`/`setParameters()`로 인코딩 설정을 재협상 없이 바꿀 수 있다. LTE 업링크가 약한 디바이스에서 최대 비트레이트를 제한하는 것이 대표적인 쓰임이다.

```js
const sender = pc.getSenders().find((s) => s.track?.kind === 'video');
const params = sender.getParameters();
if (!params.encodings.length) params.encodings = [{}]; // 협상 전 빈 배열 대비
params.encodings[0].maxBitrate = 1_500_000;            // 1.5 Mbps 상한
params.encodings[0].scaleResolutionDownBy = 1.5;       // 해상도 1/1.5로 축소
await sender.setParameters(params);
```

`getParameters()`로 받은 객체를 수정해서 그대로 돌려줘야 한다. 새 객체를 만들어 넘기면 트랜잭션 ID가 맞지 않아 거부된다. 비트레이트 적응과 `degradationPreference`는 [09장](/study/webrtc/09-quality-latency), 코덱 우선순위(`setCodecPreferences`)는 [04장](/study/webrtc/04-sdp-jsep), Simulcast용 다중 인코딩은 [12장](/study/webrtc/12-topology-sfu)에서 다룬다.

| 객체 | 자주 쓰는 멤버 | 용도 |
|---|---|---|
| `RTCRtpTransceiver` | `mid`, `direction`, `currentDirection`, `stop()`, `setCodecPreferences()` | 방향·코덱 협상 |
| `RTCRtpSender` | `track`, `replaceTrack()`, `getParameters()`, `setParameters()`, `getStats()` | 송신 트랙·인코딩 제어 |
| `RTCRtpReceiver` | `track`, `getStats()`, `jitterBufferTarget`(지원 브라우저 한정) | 수신 트랙·지터 버퍼 힌트 |

## 4. RTCDataChannel 맛보기

`RTCDataChannel`은 같은 PeerConnection 위에서 영상과 별개로 임의의 데이터를 주고받는 채널이다. WebSocket과 비슷한 API지만 서버를 거치지 않고 피어끼리 직접(또는 TURN을 거쳐) 흐르고, 신뢰성과 순서 보장 여부를 채널마다 고를 수 있다.

```js
// 디바이스 쪽(또는 offerer)에서 채널을 연다
const control = pc.createDataChannel('control', { ordered: true });
control.binaryType = 'arraybuffer';

control.addEventListener('open', () => {
  control.send(JSON.stringify({ type: 'hello', seq: 0 }));
});
control.addEventListener('message', (event) => {
  console.log('수신', event.data);
});
control.addEventListener('close', () => console.log('채널 닫힘'));

// 상대 쪽에서는 datachannel 이벤트로 받는다
pc.addEventListener('datachannel', ({ channel }) => {
  channel.addEventListener('message', (event) => {
    const cmd = JSON.parse(event.data);
    // 명령 처리...
  });
});
```

| 옵션 | 기본값 | 의미 |
|---|---|---|
| `ordered` | `true` | 순서 보장 여부 |
| `maxRetransmits` | 없음 | 재전송 최대 횟수. 지정하면 부분 신뢰성 |
| `maxPacketLifeTime` | 없음 | 재전송을 시도할 최대 시간(ms). `maxRetransmits`와 동시 지정 불가 |
| `negotiated` | `false` | `true`면 DCEP 개설 절차 없이 양쪽이 같은 `id`로 직접 만든다 |
| `id` | 자동 | `negotiated: true`일 때 양쪽이 합의한 채널 번호 |
| `protocol` | `""` | 하위 프로토콜 이름(앱 정의) |

`readyState`는 `"connecting"` → `"open"` → `"closing"` → `"closed"` 순으로 바뀐다. 채널을 만든 쪽은 `connecting`에서 시작하고, `datachannel` 이벤트로 받은 쪽은 `open` 상태의 채널을 받는다. `open` 전에 `send()`를 부르면 `InvalidStateError`가 난다.

알아둘 점이 두 가지 더 있다. 첫째, <strong>첫 DataChannel만 협상을 일으킨다</strong>. 첫 채널이 SDP에 `m=application` 섹션과 SCTP 연결을 만들고, 그 뒤에 만드는 채널은 이미 열린 SCTP 연결 위에서 DCEP로 열리므로 재협상이 필요 없다. 둘째, <strong>`send()`는 즉시 반환되고 데이터는 내부 버퍼에 쌓인다</strong>. 큰 데이터를 연달아 보내면 `bufferedAmount`가 계속 늘어나므로, `bufferedAmountLowThreshold`와 `bufferedamountlow` 이벤트로 흐름을 제어해야 한다. 원격 제어 명령 채널 설계(시퀀스 번호·데드맨 스위치·워치독)와 MQTT와의 역할 분담은 [11장](/study/webrtc/11-datachannel)에서 다룬다.

## 5. loopback 최소 예제

지금까지의 API를 한 번에 확인하는 가장 좋은 방법은 <strong>한 페이지 안에서 PeerConnection 두 개를 직접 연결</strong>해 보는 것이다. 시그널링 서버 대신 같은 페이지의 JavaScript가 offer·answer·후보를 함수 호출로 넘긴다. 서버도 NAT도 없으니 오로지 API 흐름만 남는다.

![같은 페이지 안 loopback 시퀀스. pc1(offerer)이 addTrack과 createDataChannel 후 createOffer와 setLocalDescription을 하고 offer를 pc2에 넘긴다. pc2는 setRemoteDescription, createAnswer, setLocalDescription 후 answer를 돌려주고 pc1이 setRemoteDescription한다. 양쪽은 onicecandidate로 얻은 후보를 상대의 addIceCandidate로 넘기고, ICE 점검과 DTLS를 거쳐 SRTP·SCTP 경로가 열리면 pc2에서 ontrack으로 원격 영상이 표시되고 DataChannel로 ping/pong이 오간다](/images/study-webrtc/02-loopback-light.png)
![같은 페이지 안 loopback 시퀀스. pc1(offerer)이 addTrack과 createDataChannel 후 createOffer와 setLocalDescription을 하고 offer를 pc2에 넘긴다. pc2는 setRemoteDescription, createAnswer, setLocalDescription 후 answer를 돌려주고 pc1이 setRemoteDescription한다. 양쪽은 onicecandidate로 얻은 후보를 상대의 addIceCandidate로 넘기고, ICE 점검과 DTLS를 거쳐 SRTP·SCTP 경로가 열리면 pc2에서 ontrack으로 원격 영상이 표시되고 DataChannel로 ping/pong이 오간다](/images/study-webrtc/02-loopback-dark.png)

아래 파일을 `loopback.html`로 저장한다.

```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>WebRTC loopback</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 16px; }
    video { width: 320px; height: 240px; background: #000; margin-right: 8px; }
    pre { height: 260px; overflow: auto; background: #f6f8fa; padding: 8px; }
  </style>
</head>
<body>
  <video id="localVideo" autoplay playsinline muted></video>
  <video id="remoteVideo" autoplay playsinline></video>
  <div>
    <button id="startBtn">1. 카메라 열기</button>
    <button id="callBtn" disabled>2. 연결</button>
    <button id="hangupBtn" disabled>3. 종료</button>
  </div>
  <pre id="log"></pre>

  <script type="module">
    const $ = (id) => document.getElementById(id);
    const log = (msg) => {
      $('log').textContent += `${(performance.now() / 1000).toFixed(2)}s  ${msg}\n`;
    };

    let localStream;
    let pc1; // offerer  — 실제 서비스라면 농기계 디바이스 역할
    let pc2; // answerer — 실제 서비스라면 운영자 브라우저 역할

    function watchStates(pc, name) {
      pc.addEventListener('signalingstatechange', () =>
        log(`${name} signalingState=${pc.signalingState}`));
      pc.addEventListener('icegatheringstatechange', () =>
        log(`${name} iceGatheringState=${pc.iceGatheringState}`));
      pc.addEventListener('iceconnectionstatechange', () =>
        log(`${name} iceConnectionState=${pc.iceConnectionState}`));
      pc.addEventListener('connectionstatechange', () =>
        log(`${name} connectionState=${pc.connectionState}`));
    }

    // 한쪽에서 나온 후보를 반대쪽에 넣는다 — 실제로는 시그널링 서버를 거친다
    function relayCandidates(from, to, toName) {
      from.addEventListener('icecandidate', ({ candidate }) => {
        if (!candidate) return; // null은 수집 완료 신호
        to.addIceCandidate(candidate)
          .catch((err) => log(`${toName} addIceCandidate 실패: ${err.name}`));
      });
    }

    $('startBtn').onclick = async () => {
      localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      $('localVideo').srcObject = localStream;
      $('startBtn').disabled = true;
      $('callBtn').disabled = false;
    };

    $('callBtn').onclick = async () => {
      $('callBtn').disabled = true;
      $('hangupBtn').disabled = false;

      // 같은 머신이라 host 후보끼리 바로 연결된다 — iceServers 불필요
      pc1 = new RTCPeerConnection();
      pc2 = new RTCPeerConnection();
      watchStates(pc1, 'pc1');
      watchStates(pc2, 'pc2');
      relayCandidates(pc1, pc2, 'pc2');
      relayCandidates(pc2, pc1, 'pc1');

      // ① 보낼 미디어와 데이터 채널 등록
      for (const track of localStream.getTracks()) pc1.addTrack(track, localStream);

      const dc = pc1.createDataChannel('control');
      dc.onopen = () => { log('pc1 DataChannel open → ping'); dc.send('ping'); };
      dc.onmessage = (e) => log(`pc1 <- ${e.data}`);

      pc2.ondatachannel = ({ channel }) => {
        channel.onmessage = (e) => {
          log(`pc2 <- ${e.data}`);
          channel.send('pong');
        };
      };

      pc2.ontrack = (e) => {
        if ($('remoteVideo').srcObject !== e.streams[0]) {
          $('remoteVideo').srcObject = e.streams[0];
          log(`pc2 ontrack: ${e.track.kind} 트랙 수신`);
        }
      };

      // ②~⑤ offer/answer — 실제로는 이 SDP들이 시그널링 서버를 거친다
      try {
        const offer = await pc1.createOffer();
        await pc1.setLocalDescription(offer);
        await pc2.setRemoteDescription(offer);

        const answer = await pc2.createAnswer();
        await pc2.setLocalDescription(answer);
        await pc1.setRemoteDescription(answer);
      } catch (err) {
        log(`협상 실패: ${err.name} ${err.message}`);
      }
    };

    $('hangupBtn').onclick = () => {
      pc1?.close();
      pc2?.close();
      pc1 = pc2 = null;
      $('remoteVideo').srcObject = null;
      log('종료 (close()는 상태 이벤트를 발생시키지 않는다)');
      $('hangupBtn').disabled = true;
      $('callBtn').disabled = false;
    };
  </script>
</body>
</html>
```

`getUserMedia`는 보안 컨텍스트가 필요하므로 파일을 더블클릭해 열지 말고 로컬 서버로 띄운다.

```bash
python3 -m http.server 8000
# 브라우저에서 http://localhost:8000/loopback.html
```

### 무엇을 관찰할 것인가

버튼을 순서대로 누르면 오른쪽 비디오에 내 카메라 영상이 "상대가 보낸 영상"으로 나타나고, 로그에 상태 변화가 찍힌다. 두 피어의 이벤트가 섞여 찍히는 순서는 브라우저와 타이밍에 따라 조금씩 다르지만, 피어별로 보면 다음 흐름을 확인할 수 있다.

- <strong>pc1</strong>: `signalingState`가 `have-local-offer` → `stable`, `iceGatheringState`가 `gathering` → `complete`, `iceConnectionState`가 `checking` → `connected`, `connectionState`가 `connecting` → `connected`.
- <strong>pc2</strong>: `signalingState`가 `have-remote-offer` → `stable`, 이후 ICE·연결 상태는 pc1과 비슷하게 진행된다.
- <strong>DataChannel</strong>: 연결 후 `pc1 DataChannel open → ping`, `pc2 <- ping`, `pc1 <- pong`이 찍힌다.

실행 중에 Chrome에서 `chrome://webrtc-internals`를 열면 두 PeerConnection의 SDP·후보·상태 전이·통계를 그래프로 볼 수 있다. 디버깅 도구는 [15장](/study/webrtc/15-monitoring-debugging)에서 다룬다.

### 코드에서 짚을 점

- <strong>후보 큐 없이도 동작하는 이유</strong>: PeerConnection의 메서드는 내부 작업 큐(operations chain)에 순서대로 쌓인다. `await pc1.setLocalDescription(offer)` 직후 이어지는 `pc2.setRemoteDescription(offer)` 호출은 pc1의 첫 `icecandidate` 이벤트보다 먼저 실행되므로, pc2의 `addIceCandidate`는 항상 원격 설명 적용 뒤에 처리된다. 시그널링 서버를 거치는 실제 환경에서는 이 순서가 보장되지 않으므로 후보 큐가 필요하다([03장](/study/webrtc/03-signaling)).
- <strong>offer와 answer는 그대로 직렬화된다</strong>: `createOffer()`가 돌려주는 값은 `type`과 `sdp` 두 필드가 전부라 `JSON.stringify`하면 `{ "type": "offer", "sdp": "..." }`가 되고, 받는 쪽은 이 객체를 그대로 `setRemoteDescription()`에 넘기면 된다. `RTCIceCandidate`도 `toJSON()`이 있어 `candidate`·`sdpMid`·`sdpMLineIndex`·`usernameFragment`가 직렬화된다.
- <strong>역할 분담</strong>: 이 예제에서는 미디어를 보내는 pc1이 offer를 만들었지만, 반드시 그럴 필요는 없다. 수신 전용 트랜시버를 가진 뷰어가 offer를 만들고 디바이스가 answer하는 구성도 흔하다. AWS KVS WebRTC가 뷰어가 offer를 보내는 방식이다([17장](/study/webrtc/17-kvs-architecture)).

### 이 예제에 빠진 것

loopback은 API 흐름만 보여준다. 실제 서비스가 되려면 다음이 더해져야 하고, 이 스터디의 나머지 장이 바로 이 목록이다.

| 빠진 것 | 실제 환경에서 필요한 이유 | 다루는 장 |
|---|---|---|
| 시그널링 서버 | 두 피어가 서로 다른 기기에 있다 | [03장](/study/webrtc/03-signaling) |
| SDP 이해·재협상 | 코덱·방향 변경, glare 처리 | [04장](/study/webrtc/04-sdp-jsep) |
| STUN/TURN | 두 피어가 서로 다른 NAT 뒤에 있다 | [05](/study/webrtc/05-nat-stun)·[06](/study/webrtc/06-ice)·[07장](/study/webrtc/07-turn) |
| 품질 제어 | 실제 네트워크는 손실·지터·대역폭 변동이 있다 | [09장](/study/webrtc/09-quality-latency) |
| 디바이스 구현 | 송신자는 브라우저가 아니라 농기계다 | [13장](/study/webrtc/13-native-webrtc) |

::: tip 핵심 정리
- `getUserMedia`는 보안 컨텍스트에서만 동작하고, 결과는 트랙의 묶음인 `MediaStream`이다. WebRTC가 보내는 단위는 트랙이며 `enabled`(앱이 끄는 것)와 `muted`(소스 사정)는 다르다.
- `RTCPeerConnection`은 피어 하나와의 연결이다. offer/answer 진행은 `signalingState`, 후보 수집은 `iceGatheringState`, 경로 탐색은 `iceConnectionState`, ICE와 DTLS를 합친 종합 상태는 `connectionState`가 알려준다. 앱 로직은 `connectionState` 기준으로 짠다.
- `disconnected`는 일시적일 수 있고 `failed`에는 `restartIce()`로 대응한다. 원격 설명 전에 도착한 후보는 큐에 쌓고, `close()`는 이벤트를 발생시키지 않는다.
- 트랜시버는 m-line 하나에 대응하는 sender·receiver 쌍이다. 보기만 하는 뷰어는 `recvonly` 트랜시버로 offer를 만들고, 카메라 전환은 `replaceTrack()`, 비트레이트 제한은 `setParameters()`로 재협상 없이 한다.
- DataChannel은 첫 채널만 협상을 일으키고, 신뢰성·순서를 채널마다 고를 수 있다.
:::

## 다음 챕터

[시그널링](/study/webrtc/03-signaling)에서는 loopback에서 함수 호출로 대신했던 부분, 즉 서로 다른 기기의 두 피어가 SDP와 ICE 후보를 주고받는 시그널링 서버를 설계한다. 표준이 없는 이유, 메시지 스키마, Node.js·Spring 서버 예제, 전송 수단 비교, 보안을 다룬다.
