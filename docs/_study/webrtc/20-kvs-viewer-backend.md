---
title: "뷰어·백엔드 구현"
description: "KVS JS SDK SignalingClient로 운영자 브라우저 뷰어를 구현하고, 뷰어 자격증명을 Cognito Identity Pool·백엔드 STS AssumeRole+세션 정책·백엔드 서명 URL 중 무엇으로 발급할지 비교한다. 디바이스 등록과 함께 시그널링 채널을 만들고 지우는 멱등한 프로비저닝 백엔드와 Android·iOS SDK 개요까지 다룬다."
date: 2026-10-19
tags: [WebRTC, AWS, KVS, IAM, STS, Cognito]
prev: /study/webrtc/19-kvs-c-sdk
next: /study/webrtc/21-kvs-ingestion-storage
---

# 뷰어·백엔드 구현

::: info 학습 목표
- JS SDK `SignalingClient`로 엔드포인트 조회 → ICE 서버 조회 → 시그널링 연결 → 오퍼/앤서 → `ontrack` 재생까지 동작하는 브라우저 뷰어를 작성할 수 있다.
- Cognito Identity Pool, 백엔드 STS AssumeRole + 세션 정책, 백엔드 서명 URL 대행을 권한 범위·만료·ClientId 통제·운영 부담 기준으로 비교하고 고를 수 있다.
- 특정 채널 ARN과 VIEWER 동작만 허용하는 세션 정책을 만들고, 이를 발급하는 백엔드 API를 구현할 수 있다.
- 디바이스 등록·폐기와 연동해 시그널링 채널을 멱등하게 만들고 지우는 프로비저닝 백엔드를 설계할 수 있다.
- Android·iOS SDK가 무엇을 제공하고 무엇을 직접 해야 하는지 안다.
:::

[19장](/study/webrtc/19-kvs-c-sdk)에서 농기계가 KVS 시그널링 채널에 master로 붙었다. 이 장은 반대편, 운영자 브라우저(viewer)와 그 뒤에 있는 백엔드를 만든다. 답해야 할 질문은 셋이다. 브라우저는 어떤 순서로 KVS를 호출하는가. 브라우저에 어떤 자격증명을 쥐여 주는가. 채널은 누가 언제 만들고 지우는가.

## 1. 브라우저 뷰어 구현 (JS SDK SignalingClient)

JS SDK(`awslabs/amazon-kinesis-video-streams-webrtc-sdk-js`)는 2026-10 현재 v2.9.0(2026-08-20)이 최신이다. npm 패키지 이름은 `amazon-kinesis-video-streams-webrtc`이고, `<script>`로 넣으면 전역 `window.KVSWebRTC`로 쓴다. 이 SDK가 주는 것은 사실상 `SignalingClient` 하나다. KVS 시그널링 WebSocket 연결, SigV4 서명, base64 메시지 인코딩을 감싸고, PeerConnection은 브라우저의 `RTCPeerConnection`을 그대로 쓴다. 엔드포인트·ICE 서버 조회는 AWS SDK로 한다.

README 예제는 AWS SDK for JavaScript v2(`AWS.KinesisVideo`)로 작성돼 있다. v2는 2025-09-08에 지원이 끝났으므로 새 코드는 v3 클라이언트(`@aws-sdk/client-kinesis-video`, `@aws-sdk/client-kinesis-video-signaling`)로 쓴다. 호출 순서는 같다.

![브라우저 뷰어 연결 시퀀스. ① 브라우저가 앱 백엔드에 POST /viewer-session을 보내고 ② 채널 ARN·ClientId·임시 자격증명을 받는다. ③ KVS API에 GetSignalingChannelEndpoint(VIEWER, WSS·HTTPS)와 ④ GetIceServerConfig로 TURN uris·username·password를 받는다. ⑤ SignalingClient open()이 ConnectAsViewer(X-Amz-ClientId)로 WSS를 열고 ⑥ open 이벤트에서 createOffer·sendSdpOffer로 오퍼가 디바이스까지 전달된다. ⑦ 디바이스의 앤서가 sdpAnswer 이벤트로 돌아와 setRemoteDescription하고 ⑧ iceCandidate를 양방향 교환한다. ⑨ ICE·DTLS가 P2P 또는 KVS TURN으로 맺어지면 ⑩ SRTP가 ontrack을 거쳐 video.srcObject로 재생된다](/images/study-webrtc/20-viewer-flow-light.png)
![브라우저 뷰어 연결 시퀀스. ① 브라우저가 앱 백엔드에 POST /viewer-session을 보내고 ② 채널 ARN·ClientId·임시 자격증명을 받는다. ③ KVS API에 GetSignalingChannelEndpoint(VIEWER, WSS·HTTPS)와 ④ GetIceServerConfig로 TURN uris·username·password를 받는다. ⑤ SignalingClient open()이 ConnectAsViewer(X-Amz-ClientId)로 WSS를 열고 ⑥ open 이벤트에서 createOffer·sendSdpOffer로 오퍼가 디바이스까지 전달된다. ⑦ 디바이스의 앤서가 sdpAnswer 이벤트로 돌아와 setRemoteDescription하고 ⑧ iceCandidate를 양방향 교환한다. ⑨ ICE·DTLS가 P2P 또는 KVS TURN으로 맺어지면 ⑩ SRTP가 ontrack을 거쳐 video.srcObject로 재생된다](/images/study-webrtc/20-viewer-flow-dark.png)

### 전체 코드

자격증명은 3절의 백엔드 API(`/viewer-session`)에서 받는다고 가정한다. 운영자는 영상을 보기만 하고, 원격 제어 명령은 DataChannel로 보낸다([11장](/study/webrtc/11-datachannel)).

```js
import { KinesisVideoClient, GetSignalingChannelEndpointCommand } from '@aws-sdk/client-kinesis-video';
import { KinesisVideoSignalingClient, GetIceServerConfigCommand } from '@aws-sdk/client-kinesis-video-signaling';
import { SignalingClient, Role } from 'amazon-kinesis-video-streams-webrtc';

export async function startViewer({ deviceId, videoEl, onState }) {
  // 0) 이 운영자·이 디바이스 전용 세션 (3절)
  const res = await fetch(`/api/devices/${deviceId}/viewer-session`, { method: 'POST', credentials: 'include' });
  if (!res.ok) throw new Error(`viewer-session ${res.status}`);
  const s = await res.json();
  // s = { region, channelArn, clientId, credentials: { accessKeyId, secretAccessKey, sessionToken, expiration } }
  const { region, channelArn, clientId } = s;
  const credentials = {
    accessKeyId: s.credentials.accessKeyId,
    secretAccessKey: s.credentials.secretAccessKey,
    sessionToken: s.credentials.sessionToken,
  };

  // 1) 엔드포인트 조회: WSS는 시그널링, HTTPS는 ICE 서버 조회 전용
  const kv = new KinesisVideoClient({ region, credentials });
  const ep = await kv.send(new GetSignalingChannelEndpointCommand({
    ChannelARN: channelArn,
    SingleMasterChannelEndpointConfiguration: { Protocols: ['WSS', 'HTTPS'], Role: Role.VIEWER },
  }));
  const endpoints = Object.fromEntries(ep.ResourceEndpointList.map((e) => [e.Protocol, e.ResourceEndpoint]));

  // 2) ICE 서버: STUN은 고정 문자열, TURN은 GetIceServerConfig (credential TTL 300초 → 캐시하지 않는다)
  const sig = new KinesisVideoSignalingClient({ region, credentials, endpoint: endpoints.HTTPS });
  const ice = await sig.send(new GetIceServerConfigCommand({ ChannelARN: channelArn, ClientId: clientId }));
  const iceServers = [{ urls: `stun:stun.kinesisvideo.${region}.amazonaws.com:443` }];
  for (const srv of ice.IceServerList ?? []) {
    iceServers.push({ urls: srv.Uris, username: srv.Username, credential: srv.Password });
  }

  // 3) PeerConnection: 받기만 한다
  const pc = new RTCPeerConnection({ iceServers });
  pc.addTransceiver('video', { direction: 'recvonly' });
  pc.addTransceiver('audio', { direction: 'recvonly' });
  const control = pc.createDataChannel('control', { ordered: true });   // 오퍼 전에 만들어야 m=application이 들어간다

  pc.ontrack = (ev) => {
    if (videoEl.srcObject !== ev.streams[0]) videoEl.srcObject = ev.streams[0];
  };
  pc.onconnectionstatechange = () => onState?.(pc.connectionState);

  // 4) SignalingClient
  const signaling = new SignalingClient({
    channelARN: channelArn,
    channelEndpoint: endpoints.WSS,
    clientId,                          // VIEWER는 필수, MASTER는 넣지 않는다
    role: Role.VIEWER,
    region,
    credentials,
    systemClockOffset: kv.config.systemClockOffset,   // 브라우저 시계 오차 보정 (SigV4)
  });

  signaling.on('open', async () => {
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    signaling.sendSdpOffer(pc.localDescription);   // viewer는 수신자를 안 정해도 master로 간다
  });
  signaling.on('sdpAnswer', async (answer) => {
    await pc.setRemoteDescription(answer);
  });
  signaling.on('iceCandidate', (candidate) => {
    pc.addIceCandidate(candidate).catch((e) => console.warn('addIceCandidate', e));
  });
  signaling.on('statusResponse', (st) => console.warn('KVS statusResponse', st));   // 실패할 때만 온다
  signaling.on('error', (e) => console.error('signaling error', e));
  signaling.on('close', () => onState?.('signaling-closed'));

  pc.onicecandidate = ({ candidate }) => {
    if (candidate) signaling.sendIceCandidate(candidate);   // Trickle ICE
  };

  signaling.open();
  return {
    pc, control, signaling,
    stop() { signaling.close(); pc.close(); },
  };
}
```

`<video>` 요소는 `autoplay playsinline muted`로 둔다. 오디오 트랙이 있는 스트림은 음소거하지 않으면 브라우저 자동 재생 정책에 막힌다. 운영자가 소리를 켜는 버튼을 따로 두면 된다.

### 놓치기 쉬운 동작

<strong>ClientId 규칙.</strong> `ConnectAsViewer`의 `X-Amz-ClientId`는 1~256자이고 `AWS_`로 시작할 수 없다. 같은 ClientId로 새로 연결하면 새 연결이 기존 연결을 대체한다. 운영자 ID만 ClientId로 쓰면 같은 운영자가 탭을 하나 더 열 때 첫 탭의 시그널링이 끊긴다. `op-<운영자ID>-<난수>`처럼 탭마다 고유하게 만들고, 백엔드가 발급한다(3절). 디바이스 쪽에서는 이 ClientId가 세션 해시 키라서([19장](/study/webrtc/19-kvs-c-sdk)) 로그 상관 분석에도 쓸모가 있다.

<strong>오퍼보다 먼저 온 후보.</strong> master의 ICE 후보가 앤서보다 먼저 도착할 수 있다. SDK는 원격 SDP를 받기 전에 온 후보를 내부 큐에 보관했다가 `sdpAnswer` 이벤트를 내보낸 직후에 `iceCandidate` 이벤트로 흘려준다. 순서를 앱이 직접 통제하고 싶으면 `enableEarlyIceCandidateBuffering: true`로 만들고 `setRemoteDescription`이 끝난 뒤 `drainPendingIceCandidates()`를 부른다.

<strong>GO_AWAY를 이벤트로 주지 않는다.</strong> KVS는 점검 때 `GO_AWAY`, TURN 연결을 끊을 때 `RECONNECT_ICE_SERVER`를 보낸다([18장](/study/webrtc/18-kvs-signaling-api)). 그런데 2026-10 기준 JS SDK `SignalingClient` 소스의 메시지 타입 enum에는 `SDP_OFFER`·`SDP_ANSWER`·`ICE_CANDIDATE`·`STATUS_RESPONSE`만 있어서, 이 두 메시지는 앱에 이벤트로 전달되지 않는다. 결국 앱이 기댈 신호는 `'close'` 이벤트다. 시그널링 연결은 최대 1시간, idle 10분이 hard 한도이므로 오래 켜 두는 관제 화면은 `'close'`를 받으면 새 자격증명으로 `SignalingClient`를 다시 만들어 연결해야 한다.

시그널링이 끊긴 동안 이미 맺어진 PeerConnection의 미디어가 계속 흐르는지는 KVS 문서에서 확인되지 않는다. 원리상 미디어는 피어 사이의 ICE·DTLS 경로로 흐르므로 WebSocket과 독립이고, 시그널링은 재협상이나 ICE restart를 할 때만 다시 필요하다. 다만 이 동작은 실기로 확인한 뒤 의존한다. `pc.iceConnectionState`가 `failed`로 가면 새 ICE 서버 설정을 받아 오퍼부터 다시 시작한다.

<strong>TURN credential은 캐시하지 않는다.</strong> `GetIceServerConfig`가 주는 TURN credential의 TTL은 API Reference(`Ttl` "Fixed value of 300")와 할당량 표(Credential Lifecycle 5분)가 300초로 적는다. AWS CLI 레퍼런스는 Ttl 범위를 30~86,400으로 적어 출처끼리 다르지만, 운영 기준은 300초로 잡는다. PeerConnection을 만들기 직전에 호출하고, 재연결할 때마다 다시 받는다.

<strong>한 디바이스에 몰리면 스로틀에 걸린다.</strong> 교대 시간에 운영자 여럿이 같은 농기계를 한꺼번에 열면 채널 단위 한도에 걸린다. `ConnectAsViewer`는 채널당 3 TPS, `GetSignalingChannelEndpoint`와 `GetIceServerConfig`는 채널당 5 TPS다. 초과하면 `ClientLimitExceededException`이 오므로 지터를 둔 재시도를 넣는다. 엔드포인트는 자주 바뀌지 않으니 백엔드가 채널별로 캐시해서 내려주면 호출 수가 준다(3절의 서명 URL 방식 예제 참고). viewer 수 자체도 채널당 기본 10(조정 가능)이고, viewer 하나가 늘 때마다 디바이스 업링크가 한 스트림씩 늘어난다는 점은 19장에서 봤다. 연결 품질 지표(`getStats()`)는 [15장](/study/webrtc/15-monitoring-debugging)에서 다룬다.

## 2. 자격증명 발급 방식 비교

`SignalingClient`는 SigV4로 서명된 WSS URL이 있어야 연결하고, 엔드포인트·ICE 조회도 SigV4 서명 호출이다. README 예제처럼 IAM 사용자의 액세스 키를 브라우저 코드에 넣는 건 데모에서만 할 일이다. 키가 페이지 소스에 그대로 노출된다. 실제로 쓸 수 있는 선택지는 셋이다.

![뷰어 자격증명 발급 방식 세 가지. A. Cognito Identity Pool은 브라우저(User Pool 로그인) → Identity Pool(GetId·GetCredentialsForIdentity) → 공용 IAM 역할(역할 정책·ABAC 태그) → 1시간짜리 임시 자격증명으로 브라우저가 KVS를 직접 호출한다. B. 백엔드 STS + 세션 정책은 브라우저(앱 로그인 토큰) → 앱 백엔드(DB로 시청 권한 확인) → STS AssumeRole(세션 정책: 채널 ARN·VIEWER) → 15분 이상 임시 자격증명으로 브라우저가 KVS를 직접 호출한다. C. 백엔드 서명 URL은 브라우저 → 앱 백엔드(권한 확인·Endpoint/ICE 조회) → SigV4RequestSigner로 WSS URL 서명(299초) → 브라우저는 서명 URL과 ICE 서버만 받고 자격증명이 없다](/images/study-webrtc/20-credential-options-light.png)
![뷰어 자격증명 발급 방식 세 가지. A. Cognito Identity Pool은 브라우저(User Pool 로그인) → Identity Pool(GetId·GetCredentialsForIdentity) → 공용 IAM 역할(역할 정책·ABAC 태그) → 1시간짜리 임시 자격증명으로 브라우저가 KVS를 직접 호출한다. B. 백엔드 STS + 세션 정책은 브라우저(앱 로그인 토큰) → 앱 백엔드(DB로 시청 권한 확인) → STS AssumeRole(세션 정책: 채널 ARN·VIEWER) → 15분 이상 임시 자격증명으로 브라우저가 KVS를 직접 호출한다. C. 백엔드 서명 URL은 브라우저 → 앱 백엔드(권한 확인·Endpoint/ICE 조회) → SigV4RequestSigner로 WSS URL 서명(299초) → 브라우저는 서명 URL과 ICE 서버만 받고 자격증명이 없다](/images/study-webrtc/20-credential-options-dark.png)

| 기준 | A. Cognito Identity Pool | B. 백엔드 STS + 세션 정책 | C. 백엔드 서명 URL |
|---|---|---|---|
| 브라우저가 받는 것 | 역할 권한 전체를 쓰는 임시 자격증명 | 역할 ∩ 세션 정책으로 줄어든 임시 자격증명 | 서명된 WSS URL + ICE 서버 목록(자격증명 없음) |
| 채널 단위 제한 | 역할 정책 또는 태그 기반 ABAC | 요청마다 채널 ARN 하나로 | 백엔드가 서명할 채널을 고름 |
| 권한 판단 위치 | IAM 정책(정적) | 앱 DB(동적) | 앱 DB(동적) |
| ClientId 통제 | 브라우저가 정함 | 브라우저가 정함 | 백엔드가 정해 서명에 포함 |
| 유효 시간 | 1시간(enhanced flow) | 900초 ~ 역할 최대 세션(역할 체이닝이면 최대 1시간) | URL 299초(`SigV4RequestSigner`) |
| 권한 회수 지연 | 최대 1시간 | 발급한 유효 시간만큼(최소 15분) | 이미 연결된 세션만 남음 |
| 백엔드 부하 | 거의 없음 | 시청 시작마다 AssumeRole 1회 | 연결마다 서명, 엔드포인트·ICE 조회 대행 |
| 감사 추적 | Cognito identity ID | CloudTrail의 RoleSessionName(운영자 ID) | 백엔드 로그 |
| 잘 맞는 경우 | 사용자↔리소스 관계를 태그로 표현할 수 있을 때 | 운영자↔디바이스 권한이 DB에 있을 때 | 브라우저에 자격증명을 전혀 두고 싶지 않을 때 |

### A. Cognito Identity Pool

Identity Pool의 enhanced(simplified) flow는 User Pool 같은 IdP가 준 ID 토큰을 `GetId` → `GetCredentialsForIdentity`에 넘겨 IAM 역할의 임시 자격증명을 받는다. Cognito 문서는 이 자격증명이 1시간 유효하다고 적는다. Android·iOS 샘플 앱이 이 방식을 쓴다(5절).

```js
import { fromCognitoIdentityPool } from '@aws-sdk/credential-providers';

const provider = fromCognitoIdentityPool({
  clientConfig: { region },
  identityPoolId: 'ap-northeast-2:00000000-0000-0000-0000-000000000000',
  logins: { [`cognito-idp.${region}.amazonaws.com/${userPoolId}`]: idToken },
});
const credentials = await provider();   // SignalingClient에는 값 객체로 넘긴다
```

문제는 권한 범위다. 인증된 사용자 전원이 같은 역할을 받으므로, 역할 정책이 `channel/*`에 `ConnectAsViewer`를 허용하면 로그인한 누구나 모든 농기계를 볼 수 있다. 사용자마다 볼 수 있는 채널을 나누려면 Identity Pool의 attributes for access control(ABAC)을 쓴다. IdP 토큰의 클레임을 principal tag로 바꿔 세션에 붙이는 기능이다. KVS의 `channel` 리소스는 `aws:ResourceTag/${TagKey}` 조건 키를 지원하므로(Service Authorization Reference), 채널 태그와 사용자 태그를 맞추는 정책을 쓸 수 있다.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "kinesisvideo:DescribeSignalingChannel",
      "kinesisvideo:GetSignalingChannelEndpoint",
      "kinesisvideo:GetIceServerConfig",
      "kinesisvideo:ConnectAsViewer"
    ],
    "Resource": "arn:aws:kinesisvideo:ap-northeast-2:123456789012:channel/*",
    "Condition": {
      "StringEquals": { "aws:ResourceTag/farmId": "${aws:PrincipalTag/farmId}" }
    }
  }]
}
```

이 방식이 성립하려면 역할 신뢰 정책에 `sts:AssumeRoleWithWebIdentity`와 함께 `sts:TagSession`을 허용해야 한다. Cognito 문서는 두 가지를 경고한다. 사용자가 `UpdateUserAttributes`로 바꿀 수 있는 속성을 principal tag로 쓰면 보안 경계가 무너지니 모든 앱 클라이언트의 `WriteAttributes`에서 빼거나 변경 불가 속성으로 만들어야 한다. 그리고 속성 값에 `*`나 `?`가 들어가면 `StringLike`나 `Resource`에서 와일드카드로 해석돼 다른 테넌트 리소스까지 매칭될 수 있다.

ABAC는 "농장 A 직원은 농장 A 장비를 본다"처럼 관계가 정적이고 단순할 때 잘 맞는다. "이번 주 야간 교대 운영자가 임대 중인 트랙터 3대만 본다"처럼 권한이 앱 DB에서 수시로 바뀌면 태그로 표현하기 어렵다. 이때는 B나 C가 낫다.

### B와 C의 차이: 누가 서명하는가

B는 백엔드가 권한을 확인한 뒤 범위를 좁힌 자격증명을 내려주고, 서명은 브라우저가 한다. C는 백엔드가 서명까지 해서 URL만 내려준다. C에서 눈여겨볼 점은 ClientId다. JS SDK는 viewer일 때 `X-Amz-ChannelARN`과 `X-Amz-ClientId`를 쿼리 파라미터로 넣고 그 전체를 SigV4로 서명한다. 백엔드가 서명하면 ClientId를 백엔드가 정하고 브라우저는 바꿀 수 없다. A·B에서는 브라우저가 ClientId를 자유롭게 고를 수 있어서, 같은 채널을 볼 권한이 있는 사람이 다른 운영자의 ClientId로 접속해 그 연결을 밀어낼 수 있다. KVS IAM에는 ClientId나 Role 파라미터를 조건으로 거는 키가 없다(채널 리소스의 조건 키는 태그 관련 키뿐이다).

반대로 C의 서명 URL은 bearer 토큰과 같다. 299초 안에 그 URL을 가진 사람은 누구든 연결할 수 있으므로 URL을 로그에 남기지 않는다. C를 쓰면 백엔드가 엔드포인트와 ICE 서버도 대신 조회해 내려줘야 한다. 브라우저에 자격증명이 없으니 AWS API를 직접 부를 수 없기 때문이다. JS SDK README도 "you will also have to get other data, such as the ICE server config, on the backend"라고 적는다.

## 3. 백엔드 STS AssumeRole + 세션 정책

B 방식의 구조는 이렇다. 백엔드는 자기 역할(예: ECS 태스크 역할 `farm-backend`)로 `KvsViewerRole`을 assume하면서, 요청마다 세션 정책을 붙인다. STS 문서 원문은 "The resulting session's permissions are the intersection of the role's identity-based policy and the session policies"다. 역할 정책은 상한, 세션 정책은 이번 요청의 범위다. 세션 정책으로 역할보다 넓은 권한을 줄 수는 없다.

### 역할 두 개와 세션 정책

`KvsViewerRole`의 신뢰 정책은 백엔드 역할만 허용한다.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "AWS": "arn:aws:iam::123456789012:role/farm-backend" },
    "Action": "sts:AssumeRole"
  }]
}
```

`KvsViewerRole`의 권한 정책(상한)은 VIEWER에 필요한 네 동작을 이 리전의 채널 전체에 허용한다. 운영 환경 채널만 열고 싶으면 `aws:ResourceTag/env` 조건을 더한다.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "kinesisvideo:DescribeSignalingChannel",
      "kinesisvideo:GetSignalingChannelEndpoint",
      "kinesisvideo:GetIceServerConfig",
      "kinesisvideo:ConnectAsViewer"
    ],
    "Resource": "arn:aws:kinesisvideo:ap-northeast-2:123456789012:channel/*",
    "Condition": { "StringEquals": { "aws:ResourceTag/env": "prod" } }
  }]
}
```

요청마다 붙이는 세션 정책은 채널 ARN 하나만 연다.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "kinesisvideo:DescribeSignalingChannel",
      "kinesisvideo:GetSignalingChannelEndpoint",
      "kinesisvideo:GetIceServerConfig",
      "kinesisvideo:ConnectAsViewer"
    ],
    "Resource": "arn:aws:kinesisvideo:ap-northeast-2:123456789012:channel/tractor-0017/1760000000000"
  }]
}
```

"VIEWER 동작만"은 `ConnectAsMaster`가 빠져 있다는 뜻이다. 브라우저가 `GetSignalingChannelEndpoint`를 `Role: MASTER`로 불러 엔드포인트를 받더라도, `ConnectAsMaster` 권한이 없으니 master 자리를 빼앗을 수 없다. KVS IAM에는 `Role` 파라미터를 조건으로 거는 키가 없으므로, 이렇게 동작(action) 단위로 막는다.

STS 쪽 제약도 알아 둔다.

| 항목 | 값 (STS AssumeRole API Reference) |
|---|---|
| `DurationSeconds` | 900초 ~ 역할의 최대 세션 시간(1~12시간 설정). 기본 3,600초 |
| 역할 체이닝 | 역할 자격증명으로 다시 AssumeRole하면 최대 1시간. ECS 태스크 역할로 부르는 경우가 여기에 해당한다 |
| 세션 정책 크기 | 인라인·관리형 세션 정책 평문 합계 2,048자 이하. 세션 토큰 크기 초과 시 `PackedPolicyTooLarge` |
| `RoleSessionName` | 2~64자, `[\w+=,.@-]*`. 역할 주체 ARN과 CloudTrail에 남는다 |

그리드 화면처럼 여러 채널을 한 번에 열 때 ARN 목록을 세션 정책 하나에 다 넣으면 2,048자에 걸릴 수 있다. 채널마다 세션을 따로 받거나, 디바이스 그룹 태그 조건으로 바꾼다.

### Spring 백엔드 구현

AWS SDK for Java v2 기준이다. 세션 정책 JSON은 문자열을 이어 붙이지 말고 직렬화기로 만든다.

```java
@RestController
@RequiredArgsConstructor
class ViewerSessionController {
    private final ViewerSessionService service;

    @PostMapping("/api/devices/{deviceId}/viewer-session")
    ViewerSession create(@AuthenticationPrincipal OperatorPrincipal me, @PathVariable String deviceId) {
        return service.issue(me.id(), deviceId);
    }
}

record TempCredentials(String accessKeyId, String secretAccessKey, String sessionToken, Instant expiration) {}
record ViewerSession(String region, String channelArn, String clientId, TempCredentials credentials) {}

@Service
@RequiredArgsConstructor
class ViewerSessionService {

    private static final List<String> VIEWER_ACTIONS = List.of(
            "kinesisvideo:DescribeSignalingChannel",
            "kinesisvideo:GetSignalingChannelEndpoint",
            "kinesisvideo:GetIceServerConfig",
            "kinesisvideo:ConnectAsViewer");

    private final StsClient sts;
    private final DeviceVideoChannelRepository channels;
    private final OperatorAccessPolicy access;          // 운영자↔디바이스 권한 (앱 DB)
    private final ObjectMapper objectMapper;

    @Value("${kvs.viewer-role-arn}") private String viewerRoleArn;
    @Value("${kvs.region}") private String region;

    ViewerSession issue(long operatorId, String deviceId) {
        DeviceVideoChannel ch = channels.findByDeviceId(deviceId)
                .filter(c -> c.getStatus() == ChannelState.ACTIVE)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
        if (!access.canView(operatorId, deviceId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN);
        }

        // 탭마다 고유. AWS_ 접두사 금지, 1~256자. RoleSessionName 규칙(2~64자)도 만족하게 만든다
        String clientId = "op-" + operatorId + "-" + UUID.randomUUID().toString().substring(0, 8);

        AssumeRoleResponse res = sts.assumeRole(r -> r
                .roleArn(viewerRoleArn)
                .roleSessionName(clientId)               // CloudTrail에서 누가 봤는지 추적
                .durationSeconds(900)                    // 최소값. 회수 지연을 줄인다
                .policy(sessionPolicy(ch.getChannelArn())));

        Credentials c = res.credentials();               // software.amazon.awssdk.services.sts.model.Credentials
        return new ViewerSession(region, ch.getChannelArn(), clientId,
                new TempCredentials(c.accessKeyId(), c.secretAccessKey(), c.sessionToken(), c.expiration()));
    }

    private String sessionPolicy(String channelArn) {
        Map<String, Object> statement = Map.of(
                "Effect", "Allow",
                "Action", VIEWER_ACTIONS,
                "Resource", channelArn);                 // 생성시각까지 포함한 정확한 ARN
        try {
            return objectMapper.writeValueAsString(
                    Map.of("Version", "2012-10-17", "Statement", List.of(statement)));
        } catch (JsonProcessingException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

몇 가지 설계 포인트가 있다.

- <strong>권한 회수는 만료로만 된다.</strong> 운영자 권한을 빼도 이미 발급한 자격증명은 최대 900초 동안 유효하다. 즉시 끊어야 한다면 디바이스에 MQTT 명령으로 해당 ClientId의 PeerConnection을 닫게 하는 경로를 따로 둔다([11장](/study/webrtc/11-datachannel)의 제어 채널 역할 분담).
- <strong>재연결은 새 세션으로.</strong> 브라우저가 `'close'`를 받고 다시 연결할 때 자격증명이 만료됐으면 `/viewer-session`을 다시 부른다. 만료 시각(`expiration`)을 같이 내려주는 이유다.
- <strong>정확한 ARN을 쓴다.</strong> 세션 정책의 리소스는 DB에 저장된 ARN(생성시각 포함)이다. 채널을 지웠다 다시 만들면 ARN이 바뀌는데, 이전 ARN으로 발급된 세션은 새 채널에 접근하지 못한다. 의도된 동작이다.
- <strong>동시 시청 상한.</strong> 업링크가 작은 디바이스라면 여기서 "이 디바이스에 현재 발급된 유효 세션 수"를 세어 상한을 넘으면 거절한다. KVS의 viewer 한도(기본 10)보다 디바이스 업링크가 먼저 바닥나는 경우가 많다.

### C 방식: Node.js 백엔드가 서명

같은 권한 확인 뒤에 URL을 서명해 내려주는 버전이다. JS SDK의 `SigV4RequestSigner`는 WebSocket URL 서명을 지원하고 백엔드용으로 쓰라고 README가 안내한다. 소스를 보면 `X-Amz-Expires`를 `299`로 고정한다.

```js
import express from 'express';
import { randomUUID } from 'node:crypto';
import { fromNodeProviderChain } from '@aws-sdk/credential-providers';
import { KinesisVideoClient, GetSignalingChannelEndpointCommand } from '@aws-sdk/client-kinesis-video';
import { KinesisVideoSignalingClient, GetIceServerConfigCommand } from '@aws-sdk/client-kinesis-video-signaling';
import { SigV4RequestSigner, Role } from 'amazon-kinesis-video-streams-webrtc';

const region = 'ap-northeast-2';
const provider = fromNodeProviderChain();             // 백엔드 역할: 이 채널들에 VIEWER 권한 필요
const kv = new KinesisVideoClient({ region, credentials: provider });
const endpointCache = new Map();                      // channelArn → { WSS, HTTPS }

async function endpointsFor(channelArn) {
  if (!endpointCache.has(channelArn)) {
    const r = await kv.send(new GetSignalingChannelEndpointCommand({
      ChannelARN: channelArn,
      SingleMasterChannelEndpointConfiguration: { Protocols: ['WSS', 'HTTPS'], Role: Role.VIEWER },
    }));
    endpointCache.set(channelArn, Object.fromEntries(r.ResourceEndpointList.map((e) => [e.Protocol, e.ResourceEndpoint])));
  }
  return endpointCache.get(channelArn);
}

const app = express();

app.post('/api/devices/:id/viewer-url', requireOperator, async (req, res) => {
  const ch = await channels.findActiveByDeviceId(req.params.id);
  if (!ch || !(await acl.canView(req.user.id, req.params.id))) return res.sendStatus(403);

  const ep = await endpointsFor(ch.channelArn);
  const clientId = `op-${req.user.id}-${randomUUID().slice(0, 8)}`;   // 백엔드가 정하고 서명에 묶는다

  const sig = new KinesisVideoSignalingClient({ region, credentials: provider, endpoint: ep.HTTPS });
  const ice = await sig.send(new GetIceServerConfigCommand({ ChannelARN: ch.channelArn, ClientId: clientId }));

  const signer = new SigV4RequestSigner(region, await provider());
  const url = await signer.getSignedURL(ep.WSS, {
    'X-Amz-ChannelARN': ch.channelArn,
    'X-Amz-ClientId': clientId,
  });

  res.json({
    region, channelArn: ch.channelArn, wssEndpoint: ep.WSS, clientId, url,   // url은 299초짜리 bearer, 로그 금지
    iceServers: [
      { urls: `stun:stun.kinesisvideo.${region}.amazonaws.com:443` },
      ...(ice.IceServerList ?? []).map((s) => ({ urls: s.Uris, username: s.Username, credential: s.Password })),
    ],
  });
});
```

브라우저는 `credentials` 대신 `requestSigner`를 넘긴다. 설정 검증 때문에 `channelARN`·`channelEndpoint`·`clientId`는 여전히 넣는다.

```js
const s = await fetch(`/api/devices/${deviceId}/viewer-url`, { method: 'POST' }).then((r) => r.json());
const pc = new RTCPeerConnection({ iceServers: s.iceServers });
const signaling = new SignalingClient({
  channelARN: s.channelArn,
  channelEndpoint: s.wssEndpoint,
  clientId: s.clientId,
  role: Role.VIEWER,
  region: s.region,
  requestSigner: { getSignedURL: async () => s.url },   // 재연결 때는 백엔드에서 새 URL을 받아 와야 한다
});
```

엔드포인트 캐시는 C SDK가 `Describe`·`GetEndpoint` 결과를 파일에 캐시하는 것과 같은 발상이다. 연결이 실패하면 해당 채널 항목을 비우고 다시 조회한다.

## 4. 채널 프로비저닝 백엔드 설계

### 누가 채널을 만드나

C SDK 샘플은 채널이 없으면 디바이스가 직접 `CreateSignalingChannel`을 부른다. 시작하기는 편하지만 제품에서는 백엔드가 디바이스 등록 때 만드는 편이 낫다.

- 디바이스 역할에서 `CreateSignalingChannel`을 빼면 디바이스 권한이 "자기 채널에 master로 붙기"로 줄어든다([19장](/study/webrtc/19-kvs-c-sdk) 4절 정책).
- 태그, 메시지 TTL, 나중에 붙일 저장소 설정([21장](/study/webrtc/21-kvs-ingestion-storage)의 `UpdateMediaStorageConfiguration`)을 중앙에서 일관되게 정한다.
- 뷰어 세션을 발급하려면 백엔드가 채널 ARN을 알아야 한다. 만든 쪽이 ARN을 저장하는 게 자연스럽다.
- 폐기된 디바이스의 채널을 지우는 책임도 백엔드에 있다.

### 이름과 태그

채널 이름은 IoT Thing 이름과 같게 한다. 19장에서 본 대로 Thing 이름(`[a-zA-Z0-9:_-]+`, 1~128자)과 채널 이름(`[a-zA-Z0-9_.-]+`, 1~256자)의 교집합인 `[a-zA-Z0-9_-]`, 128자 이하로 정한다. 채널 이름은 계정·리전 안에서 유일하므로 그 자체가 멱등성 키가 된다.

`CreateSignalingChannel`은 생성 시 태그를 0~50개 받는다. 태그는 두 곳에 쓰인다. 2절의 ABAC 조건(`aws:ResourceTag/...`)과 비용 배분이다. `tenant`, `farmId`, `deviceId`, `env` 정도면 충분하다. 생성 뒤에 태그를 바꿀 때는 `TagResource`를 쓴다(스트림용 `TagStream`과 다르다). 메시지 TTL(`MessageTtlSeconds`)은 5~120초이고 기본 60초다. `ChannelType`은 enum에 `FULL_MESH`가 있지만 문서상 지원 타입은 `SINGLE_MASTER`뿐이다.

### 상태 머신과 DB

`CreateSignalingChannel`과 `DeleteSignalingChannel`은 둘 다 비동기 작업이다. 응답이 왔다고 채널이 바로 `ACTIVE`인 게 아니라 `DescribeSignalingChannel`의 `ChannelStatus`(`CREATING | ACTIVE | UPDATING | DELETING`)를 확인해야 한다. 그래서 DB에 상태를 두고 작업 큐 워커가 전이시킨다.

![시그널링 채널 프로비저닝 상태 머신. REQUESTED(디바이스 등록 이벤트)에서 Describe로 확인해 없으면 CreateSignalingChannel을 호출해 CREATING(ARN 저장·생성 중)이 되고, Describe 폴링으로 ChannelStatus=ACTIVE를 확인하면 ACTIVE(뷰어 세션 발급 가능)가 된다. CREATING에서 스로틀·오류가 나면 RETRY(백오프 후 재시도)로 갔다가 Describe부터 다시 시작한다. 디바이스를 폐기하면 인증서를 비활성화한 뒤 DeleteSignalingChannel을 호출해 DELETING이 되고, Describe가 ResourceNotFound를 돌려주면 DELETED(행 보존·재등록 가능)가 된다. 왼쪽에는 device_video_channel 테이블의 컬럼(device_id, channel_name, channel_arn, channel_version, status·attempts, last_error·updated_at)이 있다](/images/study-webrtc/20-provisioning-light.png)
![시그널링 채널 프로비저닝 상태 머신. REQUESTED(디바이스 등록 이벤트)에서 Describe로 확인해 없으면 CreateSignalingChannel을 호출해 CREATING(ARN 저장·생성 중)이 되고, Describe 폴링으로 ChannelStatus=ACTIVE를 확인하면 ACTIVE(뷰어 세션 발급 가능)가 된다. CREATING에서 스로틀·오류가 나면 RETRY(백오프 후 재시도)로 갔다가 Describe부터 다시 시작한다. 디바이스를 폐기하면 인증서를 비활성화한 뒤 DeleteSignalingChannel을 호출해 DELETING이 되고, Describe가 ResourceNotFound를 돌려주면 DELETED(행 보존·재등록 가능)가 된다. 왼쪽에는 device_video_channel 테이블의 컬럼(device_id, channel_name, channel_arn, channel_version, status·attempts, last_error·updated_at)이 있다](/images/study-webrtc/20-provisioning-dark.png)

```sql
CREATE TABLE device_video_channel (
    device_id        VARCHAR(64)   PRIMARY KEY,
    channel_name     VARCHAR(128)  NOT NULL UNIQUE,   -- = IoT thing 이름
    channel_arn      VARCHAR(1024),                   -- channel/<이름>/<생성시각>
    channel_version  VARCHAR(64),                     -- Update/Delete의 CurrentVersion
    status           VARCHAR(16)   NOT NULL,          -- REQUESTED/CREATING/ACTIVE/RETRY/DELETING/DELETED
    attempts         INT           NOT NULL DEFAULT 0,
    last_error       VARCHAR(512),
    updated_at       TIMESTAMP     NOT NULL
);
```

디바이스 등록 트랜잭션에서는 이 행을 `REQUESTED`로 넣고 끝낸다. AWS 호출은 트랜잭션 밖, 큐 워커에서 한다. 등록 API가 KVS 응답을 기다리면 KVS 장애가 디바이스 등록 장애로 번진다. 이벤트는 아웃박스 테이블로 발행하면 "행은 들어갔는데 이벤트는 유실"되는 경우를 막을 수 있다.

### 멱등한 생성

같은 등록 이벤트가 두 번 오거나, 생성 직후 워커가 죽어 ARN을 저장하지 못하고 재시도하는 일은 반드시 생긴다. 그래서 "먼저 조회하고, 없을 때만 만들고, 만들다 실패하면 다시 조회"하는 순서로 짠다.

```java
@Component
@RequiredArgsConstructor
class ChannelProvisioner {

    private final KinesisVideoClient kvs;
    @Value("${app.env}") private String env;

    /** 몇 번을 불러도 결과가 같다: 이미 있으면 그 채널을, 없으면 새로 만든 채널을 돌려준다 */
    ChannelInfo ensureChannel(DeviceVideoChannel row) {
        return describe(row.getChannelName()).orElseGet(() -> create(row));
    }

    private Optional<ChannelInfo> describe(String name) {
        try {
            return Optional.of(kvs.describeSignalingChannel(r -> r.channelName(name)).channelInfo());
        } catch (ResourceNotFoundException e) {
            return Optional.empty();
        }
    }

    private ChannelInfo create(DeviceVideoChannel row) {
        try {
            String arn = kvs.createSignalingChannel(r -> r
                    .channelName(row.getChannelName())
                    .channelType(ChannelType.SINGLE_MASTER)
                    .singleMasterConfiguration(c -> c.messageTtlSeconds(60))
                    .tags(Tag.builder().key("tenant").value(row.getTenantId()).build(),
                          Tag.builder().key("deviceId").value(row.getDeviceId()).build(),
                          Tag.builder().key("env").value(env).build()))
                    .channelARN();
            return kvs.describeSignalingChannel(r -> r.channelARN(arn)).channelInfo();
        } catch (KinesisVideoException e) {
            // 다른 워커가 방금 만들었을 수 있다. 이름 중복 때 어떤 예외가 오는지는 API 문서에 명시돼 있지 않으므로
            // 예외 종류에 기대지 않고 다시 조회해서 판단한다
            return describe(row.getChannelName()).orElseThrow(() -> e);
        }
    }

    /** 스케줄러가 CREATING 행을 주기적으로 확인 */
    void pollCreating(DeviceVideoChannel row) {
        ChannelInfo info = kvs.describeSignalingChannel(r -> r.channelARN(row.getChannelArn())).channelInfo();
        if (info.channelStatus() == Status.ACTIVE) {
            row.markActive(info.channelARN(), info.version());
        }
    }
}
```

워커는 `ensureChannel` 결과로 ARN과 버전을 저장하고 `CREATING`으로 바꾼 뒤, 이미 `ACTIVE`면 바로 `ACTIVE`로 넘긴다. 실패는 `attempts`를 늘리고 지수 백오프로 `RETRY`에 둔다. `AccountChannelLimitExceededException`(계정·리전 채널 한도 초과)은 재시도로 풀리지 않으니 바로 알람을 보낸다.

호출 한도는 공장에서 디바이스를 대량 등록할 때 문제가 된다. `CreateSignalingChannel`은 50 TPS(조정 가능), `DescribeSignalingChannel`·`GetSignalingChannelEndpoint`는 계정 300 TPS에 채널당 5 TPS, `Delete`·`Update`·`Tag` 계열은 계정 50 TPS에 리소스당 5 TPS다(조정 불가). 1,000대를 한 번에 등록하면 워커에 레이트 리미터를 두고 흘려보낸다.

### 삭제와 정합성 점검

디바이스를 폐기할 때는 순서가 중요하다.

1. IoT 인증서를 먼저 비활성화한다. 디바이스가 더는 자격증명을 받지 못해 재접속하거나 채널을 다시 만들 수 없다.
2. `DeleteSignalingChannel(ChannelARN)`을 호출한다. 비동기이고, `CurrentVersion`을 생략하면 최신 버전을 지운다. `ResourceNotFoundException`은 "이미 목표 상태"로 보고 성공 처리한다.
3. Describe가 `ResourceNotFoundException`을 돌려주면 `DELETED`로 바꾼다. 행은 지우지 않는다. 감사 추적이 남고, 같은 디바이스를 다시 등록할 때 이 행을 `REQUESTED`로 되돌려 재사용한다.
4. 인제스트 모드를 썼다면 연결된 Kinesis Video Stream의 보존 기간과 삭제 정책도 같이 처리한다(21장).

```java
void deleteChannel(DeviceVideoChannel row) {
    try {
        kvs.deleteSignalingChannel(r -> r.channelARN(row.getChannelArn()));
        row.markDeleting();
    } catch (ResourceNotFoundException e) {
        row.markDeleted();                              // 이미 없다 = 원하던 결과
    }
}
```

같은 이름으로 다시 만들면 ARN의 생성시각 부분이 바뀐다. 디바이스 IAM 정책은 `channel/${credentials-iot:ThingName}/*` 와일드카드라 영향이 없지만, DB의 `channel_arn`은 반드시 새 값으로 갱신해야 한다. 세션 정책에 쓰는 ARN이 이 값이다.

마지막으로 하루 한 번 정합성 점검 작업을 돌린다. `ListSignalingChannels`에 `ChannelNameCondition { ComparisonOperator: BEGINS_WITH, ComparisonValue: "tractor-" }`를 주고 페이지를 넘기며 DB와 대조한다. AWS에만 있는 채널은 고아이므로 알람 후 정리하고, DB에는 `ACTIVE`인데 AWS에 없는 채널은 `REQUESTED`로 되돌려 다시 만든다. `ListSignalingChannels`는 리소스 단위 권한을 지원하지 않아 IAM에서 리소스를 `*`로 줘야 하니, 이 작업만 쓰는 별도 역할로 분리한다.

### 한도와 비용

채널 수 한도는 문서끼리 숫자가 다르다. WebRTC 개발자 가이드는 us-east-1·us-west-2 10,000개, 그 외 리전 5,000개라고 적고, General Reference(Service Quotas)는 각각 20,000개, 10,000개라고 적는다. 둘 다 조정 가능하다. 설계할 때는 Service Quotas 콘솔에서 계정의 실제 값을 확인한다.

비용은 "활성 채널" 기준이다. 그 달에 디바이스나 앱이 한 번이라도 연결한 채널만 과금되며, Price List API 기준 서울 리전이 채널·월당 $0.04, us-east-1이 $0.03이다. 창고에 세워 둔 농기계의 채널은 그 달에 아무도 연결하지 않으면 요금이 나오지 않지만, 한도는 차지한다. 비용 구조 전체는 [22장](/study/webrtc/22-kvs-operations)에서 다룬다.

## 5. 모바일 SDK 개요

운영자가 현장에서 태블릿으로 보는 경우도 많다. AWS가 공개한 모바일 저장소는 두 개다.

| | Android | iOS |
|---|---|---|
| 저장소 | `awslabs/amazon-kinesis-video-streams-webrtc-sdk-android` | `awslabs/amazon-kinesis-video-streams-webrtc-sdk-ios` |
| 최신 릴리스 | v1.3.0 (2025-12-22) | v1.2.0 (2025-12-22) |
| 성격 | 데모 앱(`KinesisVideoWebRTCDemoApp`) | 샘플 앱(`AWSKinesisVideoWebRTCDemoApp`, Swift) |
| WebRTC 엔진 | Google WebRTC(libwebrtc). `.aar`을 직접 빌드하거나 미리 빌드된 바이너리를 넣는다 | `WebRTC.framework`(GoogleWebRTC) CocoaPod |
| AWS 연동 | AWS SDK for Android의 KVS 클라이언트 | AWS Mobile SDK for iOS의 `AWSKinesisVideo`·`AWSKinesisVideoSignaling` |
| 시그널링 WebSocket | 앱 코드 | Starscream |
| 자격증명 | Cognito User Pool + Identity Pool(`awsconfiguration.json`) | Cognito(`Constants.swift`, `awsconfiguration.json`) |
| 역할 | master·viewer 모두 | master·viewer 모두 |
| 인제스트 | master는 오디오+비디오로 저장 세션 참여, viewer는 오디오만(최대 3명) | README에서 확인되지 않음 |

이름은 SDK지만 두 저장소 모두 README 제목이 "Sample"·"DemoApp"이다. JS SDK처럼 패키지를 받아 쓰는 라이브러리라기보다, KVS 시그널링을 libwebrtc에 붙이는 방법을 보여 주는 참고 구현에 가깝다. 실제 앱에서는 시그널링·PeerConnection 관리 코드를 가져다 쓰고, libwebrtc 바이너리 빌드·업데이트는 직접 떠안게 된다. Android README는 Trickle ICE가 기본이며(`ContinualGatheringPolicy.GATHER_CONTINUALLY`), 끄려면 `GATHER_ONCE`로 바꾸라고 적는다. 에뮬레이터에는 H.264 인코딩 지원이 없을 수 있다는 점도 README에 나온다.

설계 관점에서 정리하면 다음과 같다.

- <strong>자격증명은 웹과 같은 백엔드 API로 통일한다.</strong> 샘플은 Cognito를 쓰지만, 3절의 `/viewer-session`을 그대로 부르도록 바꾸면 웹·모바일의 권한 판단이 한 곳에 모인다. 모바일 AWS SDK의 KVS 클라이언트에 STS 임시 자격증명을 넣는 방식은 각 SDK의 credentials provider 인터페이스를 따른다.
- <strong>네트워크 전환을 처리한다.</strong> 현장 태블릿은 Wi-Fi와 LTE를 오간다. 경로가 바뀌면 ICE가 끊기므로 ICE restart 또는 재연결 로직이 필요하다([06장](/study/webrtc/06-ice)).
- <strong>WebView도 선택지다.</strong> JS SDK README의 호환성 표는 Android WebView 53, iOS Safari 11 이상을 지원 대상으로 적는다. 시청 전용 화면이라면 1절의 웹 뷰어를 WebView로 감싸는 편이 libwebrtc를 직접 관리하는 것보다 훨씬 싸다. 앱이 백그라운드로 갈 때 연결을 끊고 돌아오면 다시 붙는 생명주기 처리만 챙기면 된다.

::: tip 핵심 정리
- 브라우저 뷰어는 `GetSignalingChannelEndpoint`(WSS·HTTPS) → HTTPS 엔드포인트로 `GetIceServerConfig` → `SignalingClient.open()` → `'open'`에서 오퍼 → `'sdpAnswer'`·`'iceCandidate'` 처리 → `ontrack` 순서다. AWS SDK는 v3를 쓴다.
- ClientId는 탭마다 고유하게 백엔드가 발급한다. 같은 ClientId는 기존 연결을 대체한다. JS SDK는 `GO_AWAY`를 이벤트로 주지 않으니 `'close'`에서 재연결하고, TURN credential(300초)은 매번 새로 받는다.
- 자격증명은 세 가지다. Cognito는 백엔드 부담이 없지만 권한이 역할·태그 단위다. 백엔드 STS + 세션 정책은 요청마다 채널 ARN 하나와 VIEWER 동작만 연다(유효 권한 = 역할 정책 ∩ 세션 정책). 서명 URL은 브라우저에 자격증명을 주지 않고 ClientId까지 백엔드가 통제한다.
- 채널은 디바이스 등록 때 백엔드가 만든다. 이름 = Thing 이름, 생성·삭제는 비동기라 DB 상태 머신과 Describe 폴링으로 관리하고, "조회 → 없으면 생성 → 실패하면 재조회"로 멱등하게 만든다.
- 폐기 순서는 인증서 비활성화 → 채널 삭제 → 상태 확인이다. 재생성하면 ARN이 바뀌므로 DB를 갱신하고, 정기 점검으로 고아 채널을 찾는다. 채널 수 한도는 문서끼리 다르니 Service Quotas에서 확인한다.
- Android·iOS 저장소는 libwebrtc 기반 참고 구현이다. 자격증명은 웹과 같은 백엔드 API로 통일하고, 시청 전용이면 WebView도 검토한다.
:::

## 다음 챕터

[WebRTC 인제스트와 저장](/study/webrtc/21-kvs-ingestion-storage)에서는 Kinesis Video Streams의 스트림·프래그먼트·보존 기간 기본을 정리하고, 시그널링 채널을 스트림에 연결해(`UpdateMediaStorageConfiguration`) 실시간 시청과 클라우드 녹화를 함께 하는 저장 세션의 흐름과 제약을 다룬다.
