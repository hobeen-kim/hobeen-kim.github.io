---
title: "Amazon IVS Real-Time Streaming"
description: "Amazon IVS Real-Time Streaming의 Stage·Participant Token 구조와 publish/subscribe 모델, 서버 측 합성·IVS 채널 연계·개별 참가자 녹화, WHIP 퍼블리시, 한도와 참가자 시간 과금을 정리하고 디바이스 영상 플랫폼 관점에서 평가한다."
date: 2026-10-19
tags: [WebRTC, AWS, IVS, WHIP, Streaming]
prev: /study/webrtc/23-chime-sdk
next: /study/webrtc/25-capstone-farm-platform
---

# Amazon IVS Real-Time Streaming

::: info 학습 목표
- IVS의 저지연 스트리밍(채널)과 실시간 스트리밍(스테이지)이 어떻게 다른지 안다.
- Stage·Participant·Participant Token의 관계와 `capabilities`·`duration`·`attributes`의 의미를 설명할 수 있다.
- API로 발급하는 토큰과 키 페어로 직접 서명하는 토큰을 비교하고, 백엔드 발급 코드를 작성할 수 있다.
- Web Broadcast SDK의 strategy 기반 publish/subscribe 모델로 운영자 뷰어를 구현할 수 있다.
- 서버 측 합성(Composition)으로 IVS 채널·S3에 내보내는 방법과 개별 참가자 녹화의 차이를 안다.
- OBS·GStreamer 같은 WHIP 클라이언트로 스테이지에 송출할 때의 엔드포인트·토큰·미디어 규격을 안다.
- 참가자 접속 위치 기준 participant-hour 과금으로 비용을 추정하고, 디바이스 영상 플랫폼에 맞는 지점과 안 맞는 지점을 판단할 수 있다.
:::

## 1. IVS Real-Time Streaming과 Stage 모델

Amazon IVS(Interactive Video Service)에는 두 가지 스트리밍 방식이 있다. 하나는 <strong>저지연 스트리밍</strong>으로, 인코더가 채널(channel)에 RTMPS로 송출하면 IVS가 HLS로 시청자에게 뿌린다. [01장](/study/webrtc/01-why-webrtc)에서 본 것처럼 수 초 수준의 지연을 내세우는 HLS 계열이다. 다른 하나가 이 장의 주제인 <strong>실시간 스트리밍(Real-Time Streaming)</strong>이다. 사용자 가이드는 "Deliver live streams with a latency that can be under 300 milliseconds from host to viewer."라고 소개한다. 출력은 WebRTC다.

실시간 스트리밍의 중심 리소스는 <strong>Stage</strong>다. 스테이지는 참가자들이 미디어를 주고받는 가상의 공간이고, 참가자는 스테이지에 영상·음성을 <strong>publish</strong>하거나 다른 참가자의 미디어를 <strong>subscribe</strong>한다. 구성 요소를 정리하면 다음과 같다.

| 개념 | 설명 |
|---|---|
| Stage | 참가자들이 미디어를 주고받는 리소스. 리전 단위 컨트롤 플레인에 만든다 |
| Participant | 스테이지에 접속한 클라이언트. publisher, subscriber, 또는 둘 다 |
| Participant token | 특정 스테이지 하나에 참가할 권한과 publish/subscribe 능력을 담은 토큰 |
| Composition | 스테이지 참가자를 한 화면으로 합성해 IVS 채널이나 S3로 내보내는 서버 측 작업 |
| EncoderConfiguration / StorageConfiguration | 합성 출력의 인코딩 설정 / 녹화용 S3 설정 |

컨트롤 플레인(스테이지 리소스 생성·토큰 발급)은 리전 단위이고, 서울에는 `ivsrealtime.ap-northeast-2.amazonaws.com` 엔드포인트가 있다. 반면 데이터 플레인(수집·시청)은 글로벌이다. 디바이스와 시청자는 리전과 상관없이 가까운 IVS 접점으로 붙는다.

기능 페이지 기준으로 입력은 RTMPS 또는 WHIP, 출력은 WebRTC다. 서버 측이 SFU라고 공식 문서가 명시한 문장은 확인하지 못했다. 다만 Web SDK 문서는 simulcast를 설명하며 "This allows the server to choose which rendition to send to other participants, based on their networking limitations."라고 적는다. 서버가 구독자마다 레이어를 골라 전달한다는 뜻이므로, 동작 방식은 [12장](/study/webrtc/12-topology-sfu)의 SFU와 같은 계열로 이해하면 된다.

![IVS Stage와 Participant Token 구조. 백엔드(토큰 발급 API)가 IVS Real-Time 컨트롤 플레인(ivsrealtime.ap-northeast-2)에 CreateParticipantToken을 호출해 token·participantId·expirationTime을 받는다. 농기계 디바이스에는 PUBLISH 능력의 60분 토큰을 MQTT로, 운영자 브라우저에는 SUBSCRIBE 능력과 role=operator 속성의 토큰을 HTTPS로 준다. 디바이스는 Stage에 WHIP으로 퍼블리시하고, 운영자는 WebRTC로 구독한다. Stage는 데이터 플레인이 글로벌이고, 스테이지당 publisher 최대 12(조정 불가), subscriber 최대 10,000(조정 가능)이며, simulcast 레이어를 구독자 상황에 맞춰 선택한다. 스테이지 리소스 자체는 리전의 컨트롤 플레인에 속한다](/images/study-webrtc/24-stage-token-light.png)
![IVS Stage와 Participant Token 구조. 백엔드(토큰 발급 API)가 IVS Real-Time 컨트롤 플레인(ivsrealtime.ap-northeast-2)에 CreateParticipantToken을 호출해 token·participantId·expirationTime을 받는다. 농기계 디바이스에는 PUBLISH 능력의 60분 토큰을 MQTT로, 운영자 브라우저에는 SUBSCRIBE 능력과 role=operator 속성의 토큰을 HTTPS로 준다. 디바이스는 Stage에 WHIP으로 퍼블리시하고, 운영자는 WebRTC로 구독한다. Stage는 데이터 플레인이 글로벌이고, 스테이지당 publisher 최대 12(조정 불가), subscriber 최대 10,000(조정 가능)이며, simulcast 레이어를 구독자 상황에 맞춰 선택한다. 스테이지 리소스 자체는 리전의 컨트롤 플레인에 속한다](/images/study-webrtc/24-stage-token-dark.png)

[23장](/study/webrtc/23-chime-sdk)의 Chime SDK와 구조를 비교하면 차이가 보인다. Chime 미팅은 24시간이 지나면 자동으로 끝나는 세션이었지만, 스테이지는 지울 때까지 남아 있는 리소스다. 그래서 KVS 시그널링 채널처럼 "기계 한 대에 스테이지 하나"를 미리 만들어 둘 수 있다. 다만 참가자 한 명이 publish·subscribe를 이어갈 수 있는 시간은 최대 24시간이고, 계정·리전당 스테이지 수에도 한도(1,000)가 있다(§3).

## 2. Participant Token — capabilities·duration·attributes

### 토큰에 담기는 것

참가자 토큰은 "특정 스테이지 하나에 이런 능력으로 들어갈 수 있다"는 증명이다. `CreateParticipantToken` 요청 필드는 다음과 같다.

| 필드 | 의미 | 제약 |
|---|---|---|
| `stageArn` | 참가할 스테이지 | 필수 |
| `capabilities` | `PUBLISH`·`SUBSCRIBE` | 0~2개, 기본은 둘 다 |
| `duration` | 토큰 유효 시간(분) | 1~20160(14일), 기본 720(12시간) |
| `userId` | 우리 시스템의 사용자·디바이스 식별자 | 0~128자, 모든 참가자에게 노출 |
| `attributes` | 앱이 정하는 키-값 속성 | 합계 1 KB, 모든 참가자에게 노출 |

응답의 `participantToken`에는 `token`, `participantId`, `expirationTime`, `capabilities`, `duration`, `userId`, `attributes`가 들어 있다. 클라이언트에 넘기는 것은 `token` 문자열이고, `participantId`는 이후 이벤트·녹화 경로에서 참가자를 식별하는 키가 된다.

몇 가지 운영 포인트가 있다.

- <strong>`userId`와 `attributes`는 모든 참가자에게 보인다.</strong> 문서가 개인 식별 정보나 민감 정보를 넣지 말라고 명시한다. 운영자 이름 대신 내부 ID를, 기계 시리얼 대신 내부 식별자를 쓴다.
- <strong>토큰은 참가 시점에 검증된다.</strong> 키 페어 토큰 문서는 "The token is validated when the participant joins a stage."라고 적는다. 그러므로 `duration`은 "언제까지 참가할 수 있는가"를 정하는 값으로 보고, 이미 참가한 세션이 토큰 만료와 함께 끊길 것이라고 기대하지 않는 편이 안전하다. 참가 중인 사람을 내보내려면 `DisconnectParticipant` API를 쓴다.
- <strong>능력은 역할별로 최소화한다.</strong> 디바이스는 다른 참가자를 볼 필요가 없으므로 `PUBLISH`만 준다. 운영자는 `SUBSCRIBE`만, 디바이스 스피커로 음성 안내를 보내야 하는 운영자에게만 `PUBLISH`를 추가한다. 디바이스 토큰이 유출돼도 그 토큰으로 다른 기계 영상을 구독할 수 없다.

### 발급 방식 두 가지

토큰을 만드는 방법은 두 가지다.

| 방식 | 동작 | 장점 | 주의 |
|---|---|---|---|
| API 발급 | 백엔드가 SigV4로 `CreateParticipantToken` 호출 | 구현이 단순하다 | API 50 TPS 한도, 토큰 내용은 opaque로 다뤄야 함 |
| 키 페어 서명 | 백엔드가 ES384 JWT를 직접 서명, 공개 키는 `ImportPublicKey`로 등록 | API 호출 없이 발급, 대량 발급에 유리 | 키 만료 기능이 없어 유출 시 공개 키를 직접 삭제해야 함 |

API로 받은 토큰에 대해 문서는 "Treat tokens as opaque; do not build functionality based on token contents."라고 경고한다. 토큰 형식이 바뀔 수 있으니 JWT를 디코딩해 쓰는 코드를 만들지 말라는 뜻이다.

키 페어 방식은 P-384 EC 키를 만들고 공개 키를 IVS에 등록한 뒤, 백엔드가 개인 키로 JWT를 서명한다. 헤더는 `alg: ES384`, `typ: JWT`, `kid`(등록한 공개 키 ARN)이고, payload는 `exp`·`iat`·`jti`(참가자 ID, 최대 64자 영숫자·`-`·`_`)·`resource`(스테이지 ARN)·`topic`(스테이지 ID)·`events_url`·`whip_url`(`CreateStage`/`GetStage`가 돌려준 값, 최대 14일 캐시 가능)·`capabilities`(`allow_publish`·`allow_subscribe`)·`version`(`1.0`)이 필수이고 `user_id`·`attributes`는 선택이다. 만료는 기본 12시간을 권장하며 `iat`로부터 최대 14일까지 늘릴 수 있다.

디바이스 플랫폼에서 키 페어 방식이 의미 있는 순간이 있다. 통신 장애가 끝나 수백 대의 농기계가 동시에 재접속하면 토큰 발급 요청이 몰린다. `CreateParticipantToken`은 50 TPS 한도가 있으므로 API 방식은 스로틀링에 걸릴 수 있지만, 키 페어 방식은 백엔드의 서명 연산만으로 처리된다.

### 백엔드 코드: 스테이지 준비와 토큰 발급

AWS SDK for JavaScript v3의 `@aws-sdk/client-ivs-realtime`으로 디바이스 등록 시 스테이지를 만들고, 시청 요청마다 역할별 토큰을 발급하는 코드다.

```js
// ivs-service.js — 백엔드에서만 실행한다 (AWS 자격증명 필요)
import {
  IVSRealTimeClient,
  CreateStageCommand,
  CreateParticipantTokenCommand,
} from '@aws-sdk/client-ivs-realtime';

const ivs = new IVSRealTimeClient({ region: 'ap-northeast-2' });

// 디바이스 등록 시 1회: 기계마다 스테이지 하나, 개별 참가자 녹화를 켠다
export async function provisionStage(machineId) {
  const { stage } = await ivs.send(new CreateStageCommand({
    name: `machine-${machineId}`,
    tags: { machineId },
    autoParticipantRecordingConfiguration: {
      storageConfigurationArn: process.env.IVS_STORAGE_CONFIG_ARN, // 스테이지와 같은 리전의 S3
      mediaTypes: ['AUDIO_VIDEO'],
    },
  }));
  return { stageArn: stage.arn, endpoints: stage.endpoints }; // endpoints.whip 등을 저장해 둔다
}

// 시청 요청마다: 디바이스는 PUBLISH, 운영자는 SUBSCRIBE
export async function issueTokens(stageArn, machineId, operatorId) {
  const [device, operator] = await Promise.all([
    ivs.send(new CreateParticipantTokenCommand({
      stageArn,
      userId: `machine:${machineId}`,
      capabilities: ['PUBLISH'],
      duration: 60,                        // 분 단위
      attributes: { role: 'machine' },
    })),
    ivs.send(new CreateParticipantTokenCommand({
      stageArn,
      userId: `operator:${operatorId}`,    // 모든 참가자에게 보이므로 내부 ID만 쓴다
      capabilities: ['SUBSCRIBE'],
      duration: 60,
      attributes: { role: 'operator' },
    })),
  ]);
  return {
    deviceToken: device.participantToken.token,
    deviceParticipantId: device.participantToken.participantId, // DisconnectParticipant·녹화 경로에 쓴다
    operatorToken: operator.participantToken.token,
  };
}
```

키 페어 방식으로 같은 디바이스 토큰을 직접 서명하면 다음과 같다. `jose` 라이브러리를 쓴다고 가정한다. OpenSSL의 `ecparam -genkey`가 만드는 개인 키는 SEC1 형식이므로, `openssl pkcs8 -topk8 -nocrypt -in priv.pem -out priv-pkcs8.pem`으로 PKCS#8로 바꿔 두어야 `importPKCS8`로 읽을 수 있다.

```js
// self-signed-token.js — 공개 키는 미리 aws ivs-realtime import-public-key로 등록해 둔다
import { SignJWT, importPKCS8 } from 'jose';
import { randomUUID } from 'node:crypto';

const privateKey = await importPKCS8(process.env.IVS_PRIVATE_KEY_PKCS8, 'ES384');

export async function signDeviceToken({ stageArn, endpoints, machineId, publicKeyArn }) {
  return new SignJWT({
    user_id: `machine:${machineId}`,
    resource: stageArn,
    topic: stageArn.split('/').pop(),       // 스테이지 ID
    events_url: endpoints.events,           // CreateStage/GetStage가 돌려준 값
    whip_url: endpoints.whip,
    capabilities: { allow_publish: true },  // 구독 전용 토큰이면 allow_subscribe만 true
    attributes: { role: 'machine' },
    version: '1.0',
  })
    .setProtectedHeader({ alg: 'ES384', typ: 'JWT', kid: publicKeyArn })
    .setIssuedAt()
    .setExpirationTime('1h')
    .setJti(randomUUID())                   // 참가자 ID. 토큰마다 고유해야 한다
    .sign(privateKey);
}
```

## 3. publish/subscribe 모델과 운영자 뷰어

### strategy: 원하는 상태를 선언한다

IVS Broadcast SDK는 Web, Android(9.0+), iOS(14+)용이 있고, <strong>송출과 수신에 같은 SDK</strong>를 쓴다. 별도 플레이어 SDK가 없다. Web SDK의 핵심 개념은 stage, strategy, events 세 가지다.

strategy는 "지금 이렇게 되어 있으면 좋겠다"는 상태를 SDK에 알려 주는 객체다. 세 함수를 구현한다.

| 함수 | 반환 | 의미 |
|---|---|---|
| `stageStreamsToPublish()` | `LocalStageStream[]` | publish할 로컬 트랙 |
| `shouldPublishParticipant(participant)` | boolean | 로컬 참가자가 publish할지(토큰에 publish 권한이 있을 때만 질의) |
| `shouldSubscribeToParticipant(participant)` | `SubscribeType` | 원격 참가자를 `NONE`·`AUDIO_ONLY`·`AUDIO_VIDEO` 중 어떻게 구독할지 |

앱은 상태가 바뀔 때 strategy가 돌려줄 값을 바꾸고 `stage.refreshStrategy()`를 호출한다. SDK가 이전 값과 비교해 바뀐 부분만 적용하므로, 앱이 "상대가 publish를 시작했는지", "지금 연결 중인지" 같은 상태를 직접 추적할 필요가 없다. 문서도 `AUDIO_VIDEO`를 반환하면 SDK가 원격 참가자가 publish를 시작할 때까지 기다렸다가 구독한다고 설명한다. [04장](/study/webrtc/04-sdp-jsep)에서 재협상 상태 머신을 직접 다뤘던 것과 비교하면 추상화 수준이 한참 높다.

### 운영자 뷰어 코드

운영자 브라우저가 `role=machine` 속성을 가진 참가자만 구독하고, 자신은 아무것도 보내지 않는 뷰어다.

```js
import { Stage, SubscribeType, StageEvents } from 'amazon-ivs-web-broadcast';

const { token } = await fetch('/machines/tractor-07/watch', {
  method: 'POST', credentials: 'include',
}).then((r) => r.json());

const strategy = {
  stageStreamsToPublish: () => [],          // 운영자는 보내지 않는다
  shouldPublishParticipant: () => false,
  shouldSubscribeToParticipant: (participant) =>
    participant.attributes?.role === 'machine' ? SubscribeType.AUDIO_VIDEO : SubscribeType.NONE,
};

const stage = new Stage(token, strategy);
const videoEl = document.getElementById('machine-video');

stage.on(StageEvents.STAGE_PARTICIPANT_STREAMS_ADDED, (participant, streams) => {
  if (participant.isLocal) return;
  videoEl.srcObject = new MediaStream(streams.map((s) => s.mediaStreamTrack));
});
stage.on(StageEvents.STAGE_PARTICIPANT_STREAMS_REMOVED, () => {
  videoEl.srcObject = null;                 // 디바이스가 publish를 멈추거나 나갔다
});
stage.on(StageEvents.STAGE_CONNECTION_STATE_CHANGED, (state) => {
  console.info('stage 연결 상태', state);
});

await stage.join();
```

`STAGE_PARTICIPANT_STREAMS_REMOVED`는 원격 참가자가 publish를 멈출 때, 구독을 바꿀 때, 원격·로컬 참가자가 나갈 때 모두 호출되므로 화면 정리 로직을 한곳에 두면 된다. 네트워크가 끊기면 SDK가 알아서 재접속을 시도한다. 문서는 `ERRORED` 이후 `CONNECTING` 상태가 30초 이상 이어지면 네트워크가 끊긴 것으로 보라고 안내한다.

### simulcast와 레이어 선택

Web SDK에서 `LocalStageStream`에 `simulcast: { enabled: true }`를 주면 레이어 3개를 인코딩해 보낸다(Chromium 계열 브라우저에서만). 구독자 쪽은 따로 설정하지 않아도 서버가 기기·네트워크 상황에 맞춰 레이어를 바꿔 준다. 기본값은 가장 낮은 레이어부터 보내고 점점 올리는 방식이라 첫 화면이 빨리 뜬다. 특정 레이어를 고정하고 싶으면 strategy의 `preferredLayerForStream`을 쓴다.

디바이스가 WHIP으로 송출할 때는 사정이 다르다. IVS 문서는 OBS에 simulcast가 없다고 적는다. 레이어가 하나뿐이면 서버가 약한 구독자에게 낮은 레이어를 골라 줄 수 없으므로, 그만큼 송출 비트레이트를 보수적으로 잡아야 한다(§5).

### SEI: 프레임에 붙는 메타데이터

IVS Web SDK 문서에는 DataChannel 같은 범용 데이터 채널이 보이지 않는다. 대신 H.264 SEI(Supplemental Enhancement Information) NAL 유닛에 메타데이터를 실어 보내는 기능을 제공한다. publisher가 `inBandMessaging`을 켜고 `insertSeiMessage(payload)`를 호출하면, 구독자는 `STAGE_STREAM_SEI_MESSAGE_RECEIVED` 이벤트로 받는다.

| 항목 | 제약 |
|---|---|
| payload | ArrayBuffer, 0 KB 초과 1 KB 미만 |
| 전송량 | 초당 10 KB 이하 |
| 반복 | `repeatCount` 0~30으로 다음 N개 프레임에 반복 삽입 가능(수신 측 중복 제거 필요) |
| 전달 보장 | 없음. 네트워크가 나쁘면 유실될 수 있다 |
| 적용 범위 | H.264 비디오에만. 오디오 전용 스트림에는 쓸 수 없다 |

프레임과 정확히 맞물린 메타데이터, 예를 들어 "이 프레임을 찍은 순간의 GPS 좌표와 작업 속도"를 영상 위에 오버레이하는 데 잘 맞는다. 반대로 전달이 보장되지 않으므로 제어 명령 채널로는 쓸 수 없다. 원격 제어는 [11장](/study/webrtc/11-datachannel)의 기준대로 MQTT 같은 별도 채널에 둔다.

### 한도

Service Quotas 기준 한도다.

| 항목 | 값 | 조정 |
|---|---|---|
| 스테이지당 publisher | 12 | 불가 |
| 스테이지당 subscriber | 10,000 | 가능 |
| 계정·리전 동시 publisher / 동시 subscription / 스테이지 수 | 1,000 / 20,000 / 1,000 | - |
| 참가자 publish·subscribe 최대 시간 | 24시간 | - |
| publish 비트레이트 / download 비트레이트 | 8.5 Mbps / 8.5 Mbps | - |
| publish 해상도 | 720p | 불가 |
| `CreateParticipantToken` / 그 밖의 Stage API | 50 TPS / 5 TPS | - |

사용자 가이드의 소개 문장은 "Accommodate audiences beyond 25,000 viewers and enable up to 12 hosts"라고 적는다. 스테이지당 subscriber 기본값(10,000)보다 큰 숫자이므로, 이 규모는 quota 증설이나 IVS 채널 연계(§4)를 전제로 읽는 편이 안전하다. Broadcast SDK의 캡처는 최대 720p로 인코딩하고, 모바일 웹에서는 동시 publisher를 3명 이하로 권장한다. Web SDK는 webview를 지원하지 않는다.

## 4. Composition과 녹화

스테이지의 미디어를 남기거나 더 많은 사람에게 보내는 방법은 두 갈래다. 참가자들을 한 화면으로 합쳐 내보내는 <strong>서버 측 합성</strong>과, publisher마다 따로 저장하는 <strong>개별 참가자 녹화</strong>다.

![Composition과 녹화. Stage 안의 트랙터 전방 카메라(WHIP), 작업기 카메라(WHIP), 운영자(Web SDK, 음성)가 서버 측 합성(StartComposition, 레이아웃 grid·PiP)으로 들어가 destination 최대 2개, 즉 HLS 대규모 시청용 IVS 저지연 채널과 합성 영상 HLS를 저장하는 S3(StorageConfiguration)로 나간다. 아래쪽 경로에서는 개별 참가자 녹화(autoParticipantRecordingConfiguration)가 같은 리전 S3 버킷에 publisher별 HLS(fMP4), 썸네일, 메타데이터 JSON을 저장한다](/images/study-webrtc/24-composition-recording-light.png)
![Composition과 녹화. Stage 안의 트랙터 전방 카메라(WHIP), 작업기 카메라(WHIP), 운영자(Web SDK, 음성)가 서버 측 합성(StartComposition, 레이아웃 grid·PiP)으로 들어가 destination 최대 2개, 즉 HLS 대규모 시청용 IVS 저지연 채널과 합성 영상 HLS를 저장하는 S3(StorageConfiguration)로 나간다. 아래쪽 경로에서는 개별 참가자 녹화(autoParticipantRecordingConfiguration)가 같은 리전 S3 버킷에 publisher별 HLS(fMP4), 썸네일, 메타데이터 JSON을 저장한다](/images/study-webrtc/24-composition-recording-dark.png)

### 서버 측 합성(Server-side composition)

IVS 서버가 스테이지 참가자 전원의 오디오·비디오를 믹싱해 IVS 채널이나 S3로 보낸다. API는 `StartComposition`·`StopComposition`이고, 출력 인코딩은 `EncoderConfiguration`, S3 위치는 `StorageConfiguration` 리소스로 미리 만들어 둔다.

| 항목 | 값 |
|---|---|
| 레이아웃 | grid, PiP |
| destination | 최대 2개(IVS 채널, S3) |
| composition 최대 시간 | 24시간 |
| 동시 composition | 계정 20, 스테이지당 5(둘 다 조정 가능) |
| 자동 종료 | 참가자가 모두 나가거나 publish하는 참가자가 없는 상태가 1분 지속, 채널 송출 재시도 소진 등 |

자동 종료 조건은 문서마다 표현이 조금 다르다. API 레퍼런스는 "모든 참가자가 스테이지에서 나간 뒤 1분", "`StartComposition` 호출 시 참가자가 없으면 1분 뒤"라고 적고, 사용자 가이드는 "60초 동안 publish하는 참가자가 없으면"이라고 적는다. 어느 쪽이든 디바이스가 잠깐 끊겼다 1분 넘게 돌아오지 않으면 합성이 끝난다는 점은 같다. 디바이스 재접속 후 합성을 다시 시작하는 로직을 백엔드에 둔다.

::: warning 합성 입력 해상도와 publish 한도의 불일치
서버 측 합성 문서는 합성에 들어가는 publisher의 최대 해상도를 1080p로 적고, 넘으면 해당 참가자가 audio-only로 렌더링된다고 설명한다. 반면 Service Quotas의 스테이지 publish 해상도 한도는 720p(조정 불가)다. 두 문서가 서로 다른 숫자를 말하므로, 1080p 송출을 전제로 설계하기 전에 실제 계정에서 검증해야 한다. 안전한 기준은 720p다.
:::

농기계 수확 작업을 다수에게 보여 주는 "수확 현장 라이브" 같은 시나리오라면, 스테이지에서 합성한 화면을 IVS 저지연 채널로 보내고 시청자는 HLS로 보게 하는 구성이 자연스럽다. 실시간 상호작용이 필요한 소수(운영자)는 스테이지에서 WebRTC로, 다수는 채널에서 HLS로 보는 하이브리드 구조로, [14장](/study/webrtc/14-whip-whep)에서 다룬 1:N 방송 설계와 같은 발상이다.

```js
import { StartCompositionCommand, StopCompositionCommand } from '@aws-sdk/client-ivs-realtime';

const { composition } = await ivs.send(new StartCompositionCommand({
  stageArn,
  idempotencyToken: `harvest-live-${Date.now()}`,        // [a-zA-Z0-9-_], 최대 64자
  layout: { grid: { featuredParticipantAttribute: 'featured' } }, // 토큰 attributes의 featured 값으로 주인공 지정
  destinations: [
    { channel: {
        channelArn: process.env.IVS_CHANNEL_ARN,          // 저지연 채널 → HLS 시청자
        encoderConfigurationArn: process.env.IVS_ENCODER_HD_ARN } },
    { s3: {
        storageConfigurationArn: process.env.IVS_STORAGE_CONFIG_ARN,
        encoderConfigurationArns: [process.env.IVS_ENCODER_HD_ARN] } },
  ],
}));

// 방송이 끝나면
await ivs.send(new StopCompositionCommand({ arn: composition.arn }));
```

### 개별 참가자 녹화(Individual participant recording)

스테이지에 `autoParticipantRecordingConfiguration`을 설정하면, publisher가 붙을 때마다 IVS가 자동으로 S3에 녹화한다. §2 코드의 `provisionStage`가 이 설정을 넣은 예다.

| 항목 | 내용 |
|---|---|
| 설정 필드 | `storageConfigurationArn`, `mediaTypes`(`AUDIO_VIDEO`·`AUDIO_ONLY`·`NONE`), `thumbnailConfiguration`, `recordingReconnectWindowSeconds` |
| 저장물 | publisher별 HLS(fMP4), 썸네일, 메타데이터 JSON |
| 버킷 | 스테이지와 같은 리전이어야 한다. 기존 버킷이면 Object Ownership은 Bucket owner enforced/preferred, 기본 암호화는 SSE-S3여야 한다 |
| 보장 범위 | 5초 미만 연결한 참가자는 녹화가 보장되지 않는다 |
| 녹화 간 동기화 | `EXT-X-PROGRAM-DATE-TIME` 태그 |
| 비용 | 사용자 가이드 기준 표준 S3 비용만 든다. 썸네일에도 IVS 추가 요금이 없다 |

디바이스 플랫폼에는 합성보다 이쪽이 더 잘 맞는다. 기계마다 카메라 영상이 별도 HLS로 남으므로, "7호기 전방 카메라 10월 18일 14시" 같은 단위로 찾아보기 쉽다. 여러 카메라의 녹화를 나란히 재생할 때는 `EXT-X-PROGRAM-DATE-TIME`으로 시각을 맞춘다. 디바이스가 LTE 음영 지역에서 잠깐 끊겼다 돌아오는 경우가 문제인데, `recordingReconnectWindowSeconds`를 0보다 크게 설정하면 그 시간 안에 재접속한 publisher의 녹화를 같은 S3 prefix에 이어 붙여 하나의 녹화로 합친다. 기본값 0은 병합을 끈다. 대신 `Recording End` 이벤트와 `recording-ended.json`이 최소 그 시간만큼 늦게 나온다. 끊김이 잦은 농기계라면 30~60초 정도로 잡아 녹화가 잘게 쪼개지지 않게 하는 편이 낫다.

### EventBridge 이벤트

IVS는 스테이지·합성·녹화 상태를 EventBridge로 보낸다.

| detail-type | 대표 event_name |
|---|---|
| `IVS Stage Update` | Participant Published, Participant Unpublished, Participant Publish Error, Token Exchanged |
| `IVS Participant Recording State Change` | Recording Start, Recording End, Recording Start Failure, Recording End Failure |
| `IVS Composition State Change` | Session Start, Session End, Session Failure, Destination Start/End/Failure/Reconnecting |

`Recording End` 이벤트에는 `recording_s3_key_prefix`(`<stage_id>/<session_id>/<participant_id>/<시각>` 형태)와 `recording_duration_ms`가 들어 있어 녹화 인덱스 테이블을 채우기 좋다. `Participant Publish Error`의 `error_code`에는 `BITRATE_EXCEEDED` 같은 값이 온다.

::: warning 이벤트는 best-effort다
문서는 IVS 이벤트가 best-effort로 전달된다고 명시한다. 이벤트가 오지 않을 수도 있고, 몇 시간 늦게 올 수도 있고, 순서가 뒤바뀔 수도 있다(Participant Unpublished가 Published보다 먼저 오는 식). 디바이스 온라인 상태처럼 중요한 판단은 이벤트만 믿지 말고, MQTT 하트비트나 조회 API로 보정한다.
:::

참가자 단위로 다른 스테이지에 미디어를 복제하는 `StartParticipantReplication` API도 있다(참가자당 동시 replication 5). 기계별 스테이지의 디바이스 영상을 관제실 공용 스테이지로 끌어오는 식의 구성에 쓸 수 있다.

## 5. WHIP 퍼블리시 — SDK 없이 스테이지에 송출하기

IVS 스테이지에는 Broadcast SDK 말고도 <strong>WHIP</strong>으로 송출할 수 있다. WHIP은 HTTP POST 한 번으로 SDP offer/answer를 교환하는 표준 시그널링이다([14장](/study/webrtc/14-whip-whep)). 디바이스 관점에서는 이것이 IVS의 가장 큰 장점이다. 전용 임베디드 SDK 없이 OBS나 GStreamer 같은 표준 WHIP 클라이언트로 붙을 수 있기 때문이다.

### IVS WHIP 엔드포인트의 규칙

| 항목 | 내용 |
|---|---|
| 엔드포인트 | `https://global.whip.live-video.net` |
| 리다이렉트 | 307 Temporary Redirect를 반환한다. 클라이언트는 헤더를 유지한 채 리다이렉트를 따라가야 한다 |
| 인증 | participant token을 WHIP bearer token으로 쓴다 |
| SDP 요건 | offer에 H.264 비디오 트랙이 반드시 있어야 한다. 오디오만 보낼 때도 마찬가지다 |
| OBS | v30부터 WHIP 지원. simulcast가 없으므로 2.5 Mbps 이하 권장 |

스테이지마다 `CreateStage`/`GetStage`가 돌려주는 WHIP 엔드포인트(`endpoints.whip`)도 있다. 키 페어 토큰의 `whip_url` 클레임에는 이 값을 넣는다.

IVS 문서는 아직 WHIP을 "IETF draft"로 부르며 draft-01에 링크한다. 실제로 WHIP은 2025년 3월 <strong>RFC 9725</strong>(Proposed Standard)로 발행됐다. 문서 표기가 오래된 것이다.

![IVS WHIP 퍼블리시 시퀀스. WHIP 클라이언트(OBS·GStreamer)가 global.whip.live-video.net에 SDP offer와 Bearer 참가자 토큰을 담아 POST하면 307 Temporary Redirect(Location)가 돌아온다. 클라이언트는 같은 헤더와 본문으로 리다이렉트된 WHIP 엔드포인트에 다시 POST하고 201 Created(SDP answer)를 받는다. 이어서 ICE 연결 확인과 DTLS 핸드셰이크를 거쳐 SRTP로 H.264 Baseline(B-frame 0)과 Opus를 보내고, 엔드포인트는 publisher로 Stage에 합류한다. Stage 쪽에서는 Participant Published 이벤트가 EventBridge로 best-effort 전달된다](/images/study-webrtc/24-whip-publish-light.png)
![IVS WHIP 퍼블리시 시퀀스. WHIP 클라이언트(OBS·GStreamer)가 global.whip.live-video.net에 SDP offer와 Bearer 참가자 토큰을 담아 POST하면 307 Temporary Redirect(Location)가 돌아온다. 클라이언트는 같은 헤더와 본문으로 리다이렉트된 WHIP 엔드포인트에 다시 POST하고 201 Created(SDP answer)를 받는다. 이어서 ICE 연결 확인과 DTLS 핸드셰이크를 거쳐 SRTP로 H.264 Baseline(B-frame 0)과 Opus를 보내고, 엔드포인트는 publisher로 Stage에 합류한다. Stage 쪽에서는 Participant Published 이벤트가 EventBridge로 best-effort 전달된다](/images/study-webrtc/24-whip-publish-dark.png)

::: warning 307 리다이렉트와 Authorization 헤더
307은 "같은 메서드와 본문으로 다시 요청하라"는 뜻이지만, 많은 HTTP 클라이언트는 다른 호스트로 리다이렉트될 때 보안상 `Authorization` 헤더를 떼어 낸다. 예를 들어 curl은 다른 호스트로 넘어갈 때 사용자가 지정한 인증 헤더를 보내지 않으며 `--location-trusted`를 줘야 유지한다. 직접 만든 WHIP 클라이언트나 오래된 WHIP 플러그인이 리다이렉트 뒤에 401/403을 받는다면 이 동작부터 의심한다.
:::

### 수집 미디어 규격

WHIP과 RTMP 수집에 공통으로 적용되는 규격이다.

| 항목 | 규격 |
|---|---|
| 오디오 코덱 | WHIP은 Opus, RTMP는 AAC-LC |
| 오디오 비트레이트 | 최대 160 Kbps |
| 비디오 코덱 | H.264 Baseline |
| 키프레임(IDR) 간격 | 1~2초 |
| 프레임레이트 | 10~60 FPS |
| B-frames | <strong>0</strong>(켜 두면 끊김이 생긴다) |
| 해상도 | 160p~720p |
| 비디오 비트레이트 | 최대 8.5 Mbps |

RTMP/RTMPS와 E-RTMP multitrack 수집도 지원하므로, RTMP만 되는 레거시 인코더도 스테이지에 붙일 수 있다.

### OBS로 송출하기

OBS 30 이상에서 설정은 다음과 같다.

| OBS 설정 | 값 |
|---|---|
| 방송 → 서비스 | WHIP |
| 서버 | `https://global.whip.live-video.net` |
| Bearer 토큰 | `PUBLISH` 능력이 있는 participant token |
| 출력 → 키프레임 간격 | 1~2초 |
| 출력 → 프로파일 | baseline |
| 출력 → B-frame | 0 |
| 출력 → 비트레이트 | 2.5 Mbps 이하(simulcast 없음) |
| 비디오 → 출력 해상도 | 720p 이하 |

### 디바이스(GStreamer)로 송출하기

농기계 같은 리눅스 디바이스는 GStreamer의 WHIP 요소로 송출할 수 있다. 요소 이름과 속성은 GStreamer 버전마다 다르므로 [14장](/study/webrtc/14-whip-whep)의 파이프라인을 기준으로 하고, IVS용으로는 인코더 설정만 규격에 맞추면 된다. 소프트웨어 인코더 x264를 쓰는 경우의 인코더 구간은 다음과 같다.

```bash
# 인코더 구간만 발췌: B-frame 0, 1초 키프레임(30fps 기준), baseline 프로파일, 2.5 Mbps
v4l2src device=/dev/video0 \
  ! video/x-raw,width=1280,height=720,framerate=30/1 \
  ! videoconvert \
  ! x264enc tune=zerolatency bframes=0 key-int-max=30 bitrate=2500 \
  ! video/x-h264,profile=baseline \
  ! ...   # 이후 RTP 패킷화와 WHIP 송출 요소(14장 참고)
```

Jetson NVENC 같은 하드웨어 인코더를 쓸 때도 확인할 항목은 같다. B-frame 비활성화, baseline 프로파일, IDR 간격 1~2초, 720p 이하다. 그리고 앞의 경고처럼 WHIP 클라이언트가 307 리다이렉트를 헤더째 따라가는지 반드시 시험한다.

## 6. 과금

### 과금 방식

IVS Real-Time의 과금 단위는 <strong>participant-hour</strong>다. 가격 페이지의 규칙을 정리하면 다음과 같다.

- 스테이지에 연결된 host(publisher)와 viewer(subscriber) <strong>각각</strong>을 participant로 과금한다. 시청자도 과금 대상이다.
- 시간당 요율의 지역은 스테이지 리전이 아니라 <strong>참가자가 접속한 위치</strong>로 정한다.
- 초 단위로 올림한다.
- host 1명만 있어도 1 participant로 과금하고, 아무도 없으면 과금하지 않는다.
- audio-only는 표준 요율의 1/10이며, 1분 내내 오디오만 주고받았을 때만 적용된다.

### 요율표

AWS Price List API(AmazonIVS, publicationDate 2026-09-11)와 가격 페이지로 2026년 10월에 확인한 값이다. 단위는 USD이고, 월 첫 10,000시간 구간 요율이다.

| 접속 위치 | 표준(participant-hour) | audio-only | 사용량 구간이 오를 때 |
|---|---|---|---|
| North America | $0.0720 | $0.0072 | $0.0660 → $0.0600 → $0.0560 → $0.0480 |
| South Korea | $0.1250 | $0.0125 | $0.1180 → $0.1140 → $0.1110 → $0.1070 |

| 기타 항목 | 요율 |
|---|---|
| 서버 측 합성 인코딩(rendition·시간당, 글로벌) | SD $0.15, HD $0.30, Full HD $0.60 |
| 개별 참가자 녹화 | 사용자 가이드 기준 표준 S3 비용만. 가격 페이지의 별도 항목은 확인하지 못했다 |
| 참가자 replication | 가격 페이지에서 별도 요금을 확인하지 못했다 |
| 프리 티어(신규 고객 12개월) | 월 20 participant-hour + 합성 인코딩 5시간 |

요율이 접속 위치로 정해지므로, 국내 농장과 국내 관제실이라면 스테이지를 어느 리전에 만들든 한국 요율($0.1250)이 적용된다. "요금이 싼 리전에 스테이지를 만들자"는 최적화는 통하지 않는다.

### 비용 추정

[23장](/study/webrtc/23-chime-sdk)과 같은 시나리오로 계산해 본다. 모두 한국에서 접속한다고 가정한다.

- <strong>한 번 시청</strong>: 트랙터 1대 + 운영자 2명이 1시간이면 3 participant-hour × $0.125 = <strong>$0.375</strong>다(Chime SDK는 $0.306).
- <strong>한 달 운영</strong>: 기계 50대를 하루 2시간씩, 매번 운영자 1명이 30일 동안 본다. 2 × 2시간 × 30일 × 50대 = 6,000 participant-hour로 첫 구간(10,000시간) 안이므로 6,000 × $0.125 = <strong>$750</strong>다. 같은 사용량을 북미에서 접속하면 6,000 × $0.072 = $432다.
- <strong>상시 송출의 함정</strong>: 디바이스가 아무도 보지 않는 스테이지에 하루 종일 publish하면 혼자서도 1 participant로 과금된다. 24시간 × 30일 × $0.125 = <strong>기기당 월 $90</strong>이다. 50대면 월 $4,500이 아무도 보지 않는 영상에 쓰인다.
- <strong>다수 시청</strong>: 기계 1대를 500명이 1시간 동안 스테이지에서 직접 보면 501 × $0.125 = 약 $62.6이다. 시청자가 많고 수 초 지연을 허용할 수 있다면, 합성 인코딩(HD $0.30/시간)을 거쳐 IVS 채널의 HLS로 보내는 쪽과 비교해 볼 만하다. 채널 쪽 요금은 IVS 저지연 스트리밍 요금표를 따로 확인해야 한다.

결론은 Chime SDK와 같다. <strong>디바이스는 시청 요청이 있을 때만 publish해야 한다.</strong> 스테이지는 상시 리소스로 두되, 송출은 MQTT 명령으로 켜고 끈다.

## 7. 디바이스 영상 플랫폼 관점: 맞는 지점과 안 맞는 지점

### 맞는 지점

- <strong>표준 WHIP으로 송출한다.</strong> 디바이스에 전용 SDK를 넣을 필요가 없다. GStreamer 파이프라인에 하드웨어 H.264 인코더를 물려 WHIP으로 보내면 된다. Chime SDK의 "C++ 시그널링 + WebRTC 직접 연결"보다 구현 부담이 훨씬 작다.
- <strong>시청자가 늘어도 디바이스 업링크는 하나다.</strong> 스테이지당 subscriber 10,000(조정 가능)이고, 서버가 구독자별로 전달한다. KVS P2P처럼 viewer 수만큼 업링크가 늘지 않는다.
- <strong>스테이지가 상시 리소스다.</strong> 기계마다 스테이지를 하나씩 미리 만들어 두는 KVS 채널식 매핑이 가능하다.
- <strong>권한을 토큰으로 세밀하게 나눈다.</strong> 디바이스에는 `PUBLISH`만, 운영자에게는 `SUBSCRIBE`만 준다. 키 페어 서명으로 API 한도 없이 대량 발급할 수도 있다.
- <strong>기계별 녹화가 쉽다.</strong> 개별 참가자 녹화로 publisher별 HLS가 S3에 쌓이고, 사용자 가이드 기준 S3 비용만 든다. 대규모 공개 방송은 합성 → IVS 채널로 확장한다.

### 안 맞는 지점

- <strong>publish 720p 상한(조정 불가).</strong> 1080p 이상의 점검용 고화질 영상은 보낼 수 없다. 합성 문서의 1080p 언급과 숫자가 맞지 않으므로 720p를 기준으로 설계한다.
- <strong>코덱·인코딩 제약.</strong> WHIP은 H.264 Baseline과 Opus만, B-frame은 0이어야 한다. H.265 하드웨어 인코더의 이점은 쓸 수 없다.
- <strong>스테이지당 publisher 12(조정 불가)와 스테이지 수 1,000.</strong> 카메라 수십 대를 한 스테이지에 모을 수 없고, 기계가 1,000대를 넘으면 스테이지 수 한도에 걸린다. 대규모 함대는 스테이지를 풀로 두고 시청 요청 때 할당하는 설계가 필요하다.
- <strong>시청자도 과금되고 한국 요율이 높다.</strong> 한국 접속은 participant-hour당 $0.125로 북미($0.072)보다 비싸다. 상시 송출은 기기당 월 $90이다.
- <strong>범용 데이터 채널이 보이지 않는다.</strong> 확인한 범위에서 데이터 전달 수단은 SEI(1 KB 미만, 전달 보장 없음)뿐이다. 원격 제어는 MQTT에 둔다.
- <strong>디바이스가 구독하는 공식 경로가 좁다.</strong> 구독은 Broadcast SDK(Web, Android 9.0+, iOS 14+)로 한다. 확인한 범위에서 리눅스 디바이스가 스테이지를 구독하는 공식 경로(WHEP 등)는 없다. 운영자 음성을 기계 스피커로 내보내는 양방향 음성이 필요하면 별도 설계가 필요하다.
- <strong>참가 최대 24시간, 이벤트는 best-effort.</strong> 장시간 송출은 재접속 로직이 필요하고, 상태 판단은 이벤트만으로 하면 안 된다.

### 세 서비스 비교

디바이스 영상 관점에서 KVS WebRTC, Chime SDK, IVS Real-Time을 나란히 놓으면 다음과 같다(전체 비교는 [16장](/study/webrtc/16-aws-landscape)).

| 항목 | KVS WebRTC | Chime SDK | IVS Real-Time |
|---|---|---|---|
| 미디어 경로 | P2P(직결 실패 시 TURN relay), 저장 모드는 storage session 경유 | SFU + 서버 오디오 믹싱 | publish/subscribe, 서버가 레이어 선택 |
| 디바이스 송출 수단 | KVS C SDK | C++ 시그널링 + WebRTC 직접 / Android SDK | WHIP(OBS·GStreamer) / RTMP(S) |
| 대기 모델 | 채널 상시, 디바이스가 master로 대기 | 미팅은 24시간 세션 | 스테이지 상시, 참가는 최대 24시간 |
| 시청자 규모 | 채널당 viewer 10(조정 가능) | 미팅당 참석자 250 | 스테이지당 subscriber 10,000(조정 가능) |
| 디바이스 업링크 | viewer 수만큼 늘어남 | 1개 | 1개 |
| 데이터 | DataChannel | 데이터 메시지 2 KB | SEI 1 KB 미만, 보장 없음 |
| 과금(한국 기준) | 채널 월 $0.04 + 메시지 + TURN 분 요금(+ relay 데이터 전송) | 참석자·분 $0.0017 | participant-hour $0.125 |

### on-demand 송출 패턴

IVS를 디바이스 플랫폼에 쓸 때의 기본 흐름은 다음과 같다.

1. 디바이스 등록 시 `CreateStage`로 기계별 스테이지를 만들고(개별 참가자 녹화 설정 포함), `stageArn`과 `endpoints`를 저장한다.
2. 운영자가 시청을 요청하면 백엔드가 인가를 확인하고, 디바이스용 `PUBLISH` 토큰과 운영자용 `SUBSCRIBE` 토큰을 발급한다.
3. 디바이스 토큰과 WHIP 엔드포인트를 MQTT 명령으로 디바이스에 보낸다. 디바이스는 GStreamer WHIP 파이프라인을 시작한다.
4. 운영자 브라우저는 Web SDK로 스테이지에 참가해 `role=machine` 참가자를 구독한다.
5. 운영자가 나가면 백엔드가 MQTT로 송출 중지를 명령하거나 `DisconnectParticipant`로 디바이스를 내보낸다. 녹화는 `Recording End` 이벤트로 인덱싱한다.

이 패턴에서 영상 시작 지연은 "MQTT 명령 전달 + WHIP 협상 + 첫 키프레임"이다. 키프레임 간격을 1초로 잡아 두면 첫 화면이 빨리 뜬다.

::: tip 핵심 정리
- IVS Real-Time은 Stage에 참가자가 publish/subscribe하는 WebRTC 서비스로, host에서 viewer까지 300 ms 미만 지연을 내세운다. 컨트롤 플레인은 리전, 데이터 플레인은 글로벌이다.
- Participant Token은 스테이지 하나에 대한 참가 권한이다. `capabilities`(`PUBLISH`·`SUBSCRIBE`), `duration`(1~20160분, 기본 720), `attributes`(1 KB, 전원 노출)로 역할을 표현하고, API 발급과 ES384 키 페어 서명 두 방식이 있다.
- Web SDK는 strategy 세 함수로 원하는 상태를 선언하고 SDK가 차이를 적용한다. simulcast 레이어는 서버가 구독자별로 고르며, SEI는 1 KB 미만·전달 보장 없는 프레임 메타데이터다.
- 한도는 스테이지당 publisher 12(조정 불가)·subscriber 10,000(조정 가능), publish 720p(조정 불가)다. 합성 문서의 1080p와는 불일치한다.
- 서버 측 합성은 grid·PiP로 IVS 채널·S3(최대 2곳)에 내보내고, 개별 참가자 녹화는 publisher별 HLS를 같은 리전 S3에 남긴다. 이벤트는 best-effort다.
- WHIP 엔드포인트는 `https://global.whip.live-video.net`(307 리다이렉트, 토큰이 bearer)이고 H.264 Baseline·B-frame 0·720p 이하가 규격이다. WHIP은 RFC 9725로 발행됐다.
- 과금은 host·viewer 모두 participant-hour이고 요율은 접속 위치로 정한다(한국 $0.125, 북미 $0.072). 디바이스 송출은 반드시 on-demand로 한다.
:::

## 다음 챕터

[캡스톤: 농기계 원격 영상·제어 플랫폼](/study/webrtc/25-capstone-farm-platform)에서는 지금까지 다룬 WebRTC 원리와 KVS·Chime SDK·IVS의 특성을 바탕으로, 다수 농기계와 소수 운영자를 잇는 원격 영상·제어 플랫폼의 전체 아키텍처와 시퀀스, 장애 시나리오, 비용을 설계한다.
