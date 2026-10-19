---
title: "Amazon Chime SDK"
description: "SFU 기반 Amazon Chime SDK의 회의 모델과 Meeting/Attendee API, 클라이언트 SDK, Media Pipelines, 한도와 과금을 정리하고, 농기계·로봇 영상 플랫폼에 맞는 지점과 맞지 않는 지점을 따져 본다."
date: 2026-10-19
tags: [WebRTC, AWS, Chime SDK, SFU, Media Pipelines]
prev: /study/webrtc/22-kvs-operations
next: /study/webrtc/24-ivs-real-time
---

# Amazon Chime SDK

::: info 학습 목표
- 지원이 끝난 Amazon Chime 앱과 Chime SDK를 구분하고, 2026년 PSTN Audio 일정이 어디까지 영향을 주는지 안다.
- Chime SDK 미디어 서비스가 비디오는 SFU로 전달하고 오디오는 서버에서 믹싱한다는 점과 그 결과를 설명할 수 있다.
- 백엔드가 `CreateMeeting`·`CreateAttendee`로 미팅을 만들고 JoinToken을 나눠 주는 흐름을 코드로 구현할 수 있다.
- control Region과 MediaRegion의 차이, 참석자·비디오 한도, 미팅 자동 종료 조건을 안다.
- Media Pipelines의 종류(capture·concatenation·live connector·media stream·compositing·media insights)와 용도를 구분한다.
- attendee-minute 과금으로 비용을 추정하고, 디바이스 영상 플랫폼에 Chime SDK가 맞는 지점과 안 맞는 지점을 판단할 수 있다.
:::

## 1. Chime SDK의 위치 — 종료된 것과 남은 것

[16장](/study/webrtc/16-aws-landscape)의 서비스 지도에서 Amazon Chime SDK는 "회의" 칸을 차지한다. 17~22장에서 다룬 KVS WebRTC는 시그널링 채널과 TURN만 관리해 주고 미디어는 피어끼리 직접 주고받는 P2P 모델이었다. Chime SDK는 반대로 <strong>모든 참석자가 AWS가 운영하는 미디어 서버에 붙는</strong> 모델이다. 미디어 서버가 가운데서 영상을 골라 나눠 주기 때문에 참석자가 늘어도 각자의 업링크는 늘지 않는다.

본론에 앞서 이름 혼동부터 정리한다. 2025~2026년에 "Chime이 종료된다"는 소식이 돌았는데, 종료된 것은 SDK가 아니다.

- <strong>Amazon Chime(완성형 회의 앱)</strong>: AWS는 2025-02-19 공지에서 그날부터 신규 고객을 받지 않는다고 밝혔고, <strong>2026-02-20에 지원을 종료</strong>했다. 같은 공지에 "This does not impact the availability of the Amazon Chime SDK service."라는 문장이 있다. 앱 사용자에게는 AWS Wickr와 파트너 솔루션(Zoom, Webex, Slack)을 대안으로 제시했다.
- <strong>Chime SDK</strong>: 개발자 가이드는 "The Amazon Chime SDK works independently of any Amazon Chime administrator accounts"라고 적는다. 앱 계정과 무관하게 동작하는 별도 서비스다.
- <strong>Chime SDK PSTN Audio(SIP media applications)</strong>: SDK 안에서도 전화망 연동 부분은 변화가 있다. <strong>2026-09-29부로 Maintenance Mode</strong>(신규 기능 개발 중단)에 들어갔고, <strong>2026-10-29부터 신규 고객을 받지 않는다</strong>. 기존 고객은 계속 쓸 수 있고 버그·보안 수정도 이어진다. 권장 이전처는 Amazon Connect Customer다. Meetings의 dial-in/dial-out(Join Meeting) 용도는 지원 케이스로 예외를 신청할 수 있다.

2026년 10월 현재 상태를 표로 정리하면 다음과 같다.

| 구성 요소 | 무엇인가 | 2026-10 기준 상태 |
|---|---|---|
| Amazon Chime 앱 | 완성형 회의·채팅 앱 | 2026-02-20 지원 종료 |
| Chime SDK Meetings | WebRTC 미디어 세션(이 장의 주제) | 앱 종료와 무관(AWS 명시) |
| Chime SDK Media Pipelines | 미팅 녹화·외부 송출 | 확인한 범위에서 종료 공지 없음 |
| Chime SDK PSTN Audio | SIP media application, 전화망 연동 | 2026-09-29 유지보수 모드, 2026-10-29 신규 고객 중단 |

::: warning "Chime SDK 전체 종료"도, "아무 변화 없음"도 틀리다
PSTN Audio 공지는 전화망 연동 범위에만 해당하고, Meetings·Media Pipelines에 대한 종료 공지는 확인되지 않았다. 반대로 "Chime SDK는 그대로다"라고만 쓰면 PSTN Audio의 신규 가입 중단을 놓친다. 이 글을 쓰는 2026-10-19 기준으로 신규 가입 중단까지 열흘이 남았다. 새로 설계하는 시스템에 전화 연결(디바이스 알람을 전화로 받는 기능 등)이 필요하다면 PSTN Audio 대신 Amazon Connect를 먼저 검토한다.
:::

이 장은 디바이스 영상 플랫폼과 관련 있는 Meetings와 Media Pipelines만 다룬다.

## 2. SFU 기반 회의 모델

### 비디오는 SFU, 오디오는 믹싱

개발자 가이드의 Architecture 절은 미디어 서비스를 이렇게 설명한다.

> The media service acts as a Selective Forwarding Unit (SFU) using a publish and subscribe model. Each attendee can publish one video source, up to a total of 25 simultaneous videos per meeting.

[12장](/study/webrtc/12-topology-sfu)에서 본 SFU 그대로다. 참석자는 비디오 소스 하나를 미디어 서비스에 publish하고, 다른 참석자는 보고 싶은 비디오를 subscribe한다. 서버는 디코딩하지 않고 패킷을 골라 전달한다.

오디오는 다르게 처리한다. 서버가 모든 참석자의 오디오를 <strong>믹싱해</strong> 각자에게 하나의 스트림으로 보낸다. 이때 받는 사람 자신의 소리는 빼고 섞는다. 코덱은 Opus이고 기본 32 kbps, 최대 128 kbps stereo / 64 kbps mono다.

이 차이가 만드는 결과를 따져 보자. 순수 SFU에서는 참석자가 N명이면 각자 오디오 스트림 N-1개를 받는다. Chime SDK에서는 몇 명이 들어와도 오디오 다운링크는 믹스 스트림 1개다. 즉 오디오는 MCU처럼, 비디오는 SFU처럼 동작하는 혼합형이다. 비디오 다운링크는 subscribe한 타일 수에 비례하고, 참석자 한 명이 동시에 받을 수 있는 비디오는 25개까지다.

그 밖의 미디어 특성은 다음과 같다.

| 항목 | 값 |
|---|---|
| 클라이언트 ↔ 미디어 서비스 | secure WebSocket(시그널링) + DTLS(미디어) |
| 오디오 | Opus, 서버 믹싱, 기본 32 kbps, 최대 128 kbps stereo / 64 kbps mono |
| 비디오(JS 클라이언트) | 최대 1280x720 30fps, simulcast 사용 시 15fps |
| 비디오 해상도 옵션 | `MeetingFeatures.Video.MaxResolution` = `None`·`HD`(기본)·`FHD` |
| 데이터 메시지 | 건당 최대 2 KB |

![Chime SDK 회의 모델. 백엔드가 Chime SDK 컨트롤 플레인(meetings-chime.ap-northeast-2)에 CreateMeeting(MediaRegion)과 CreateAttendee를 호출해 MediaPlacement와 JoinToken을 받고, JoinToken을 운영자 브라우저·운영자 모바일·농기계 디바이스에 HTTPS 또는 MQTT로 전달한다. 세 클라이언트는 MediaRegion ap-northeast-2의 Chime 미디어 서비스에 WSS와 DTLS-SRTP로 접속하며, 미디어 서비스 안에는 시그널링, 회의당 최대 25개 비디오를 선택 전달하는 SFU, 자기 소리를 뺀 Opus 믹스를 만드는 오디오 믹서가 있다](/images/study-webrtc/23-meeting-model-light.png)
![Chime SDK 회의 모델. 백엔드가 Chime SDK 컨트롤 플레인(meetings-chime.ap-northeast-2)에 CreateMeeting(MediaRegion)과 CreateAttendee를 호출해 MediaPlacement와 JoinToken을 받고, JoinToken을 운영자 브라우저·운영자 모바일·농기계 디바이스에 HTTPS 또는 MQTT로 전달한다. 세 클라이언트는 MediaRegion ap-northeast-2의 Chime 미디어 서비스에 WSS와 DTLS-SRTP로 접속하며, 미디어 서비스 안에는 시그널링, 회의당 최대 25개 비디오를 선택 전달하는 SFU, 자기 소리를 뺀 Opus 믹스를 만드는 오디오 믹서가 있다](/images/study-webrtc/23-meeting-model-dark.png)

그림에서 중요한 점은 <strong>백엔드가 미디어 경로에 끼지 않는다</strong>는 것이다. 백엔드는 API로 미팅과 참석자를 만들고 JoinToken을 나눠 줄 뿐이다. 시그널링과 미디어는 클라이언트 SDK가 미디어 서비스와 직접 주고받는다. KVS에서 시그널링 메시지 형식(`SDP_OFFER`, `ICE_CANDIDATE` 등)을 직접 다뤘던 것과 달리([18장](/study/webrtc/18-kvs-signaling-api)), Chime SDK에서는 SDP 교환이 SDK 내부에 감춰져 있다.

### control Region과 MediaRegion

Chime SDK는 리전을 두 종류로 나눈다.

- <strong>control Region</strong>: API로 미팅을 생성·수정·삭제하는 리전이다. 백엔드의 `ChimeSDKMeetingsClient`에 설정하는 리전이 이것이다.
- <strong>media Region</strong>: 미팅이 실제로 호스팅되는 리전이다. `CreateMeeting`의 `MediaRegion` 필드로 정한다.

control Region은 같은 파티션 안의 어떤 media Region에도 미팅을 만들 수 있다. 하지만 <strong>수정은 미팅을 생성한 control Region에서만</strong> 된다. 백엔드를 여러 리전에 배포한다면 미팅 ID와 함께 생성 리전을 저장해 두고, `DeleteMeeting`·`CreateAttendee` 같은 후속 호출을 같은 리전으로 보내야 한다.

`MediaRegion` 유효값에는 서울(ap-northeast-2)이 있다. 전체 목록은 af-south-1, ap-northeast-1, ap-northeast-2, ap-south-1, ap-southeast-1, ap-southeast-2, ca-central-1, eu-central-1, eu-north-1, eu-south-1, eu-west-1, eu-west-2, eu-west-3, sa-east-1, us-east-1, us-east-2, us-west-1, us-west-2와 GovCloud 두 곳이다. 서울은 meetings control/media, media pipeline control/data가 모두 recommended 상태이고, API 엔드포인트는 `meetings-chime.ap-northeast-2.amazonaws.com`이다.

참석자가 여러 나라에 흩어져 있다면 `https://nearest-media-region.l.chime.aws`로 가장 가까운 media Region을 조회해 미팅을 만들 수 있다. 국내 농장과 국내 관제실만 있다면 `ap-northeast-2`로 고정하면 된다. `MediaPlacementNetworkType`(`Ipv4Only`·`DualStack`)으로 미디어 접속을 IPv4 전용으로 할지 듀얼 스택으로 할지도 정할 수 있다.

### JoinToken과 미팅 수명

`CreateAttendee`가 돌려주는 <strong>JoinToken</strong>은 참석자마다 하나씩 발급되는 opaque secret key다. 클라이언트는 이 값으로 미디어 서비스에 자신을 인증한다. 길이는 2~2048자이고, 미팅이 끝나거나 `DeleteAttendee`를 호출하면 만료된다. 사실상 "이 미팅에 이 사람으로 들어갈 권리"이므로 비밀번호처럼 다뤄야 한다. TLS 위로만 전달하고 로그에 남기지 않는다.

미팅은 영구 리소스가 아니다. `DeleteMeeting`을 호출하면 끝나고, 그 밖에 다음 경우 자동 종료된다.

- 미팅이 24시간을 넘었다.
- replica 미팅인데 primary 미팅이 끝났다.
- replica가 아닌 미팅에 연결된 참석자가 5분 연속 없다.

이 수명 규칙이 디바이스 플랫폼 설계를 크게 바꾼다. KVS 시그널링 채널은 한 번 만들면 계속 남아 있어서 디바이스가 master로 붙어 "누가 보러 올 때까지" 기다릴 수 있었다([17장](/study/webrtc/17-kvs-architecture)). Chime 미팅은 24시간이 지나면 무조건 끝나는 <strong>세션</strong>이다. 디바이스가 미팅 안에서 상시 대기하는 구조는 만들 수 없고, 시청 요청이 올 때 미팅을 만들고 디바이스를 불러들이는 on-demand 구조가 기본이 된다(§3).

### 한도

General Reference(Service Quotas)의 기본값은 다음과 같다.

| 항목 | 기본값 | 조정 |
|---|---|---|
| 미팅당 참석자 | 250 | 불가 |
| 미팅당 동시 publish 비디오 | 25 | 가능 |
| 참석자당 동시 subscribe 비디오 | 25 | 불가 |
| 동시 미팅 수 | 250 | 가능 |
| primary 미팅당 replica 미팅 | 4 | 가능 |
| 동시 media pipeline | us-east-1 100, 그 외 리전 10 | 가능 |

참석자 상한은 미팅 생성 시 `MeetingFeatures.Attendee.MaxCount`(1~250)로 더 낮출 수 있다. 주의할 점은 고해상도 옵션이다. `Video.MaxResolution`을 `FHD`로 하거나 `Content.MaxResolution`을 `UHD`로 하면 <strong>최대 참석자가 250에서 25로 줄어든다</strong>.

::: warning replica 수치는 출처마다 다르다
Chime SDK 기능 페이지는 미팅이 "can be replicated to up to 40 additional WebRTC media sessions"이고 "10,000 audience members"까지 늘릴 수 있다고 소개한다. 반면 Service Quotas의 기본값은 primary당 replica 4(조정 가능)다. 40이 증설 후 상한일 가능성은 있지만 공식 문서에서 확인하지 못했다. 대규모 시청을 계획한다면 Service Quotas 콘솔에서 실제 값을 확인하고 증설 요청 가능 범위를 AWS에 문의하는 편이 안전하다.
:::

## 3. Meeting/Attendee API와 백엔드 역할

### 백엔드가 맡는 일

Chime SDK에서 백엔드는 미디어를 만지지 않는 대신 다음을 책임진다.

1. <strong>인가</strong>: 이 운영자가 이 기계의 영상을 볼 수 있는지 판단한다. Chime SDK는 JoinToken을 가진 사람을 들여보낼 뿐이고, 누구에게 JoinToken을 줄지는 백엔드가 정한다.
2. <strong>미팅 생성</strong>: `CreateMeeting`에 `ClientRequestToken`(요청 식별자), `ExternalMeetingId`(우리 시스템의 세션 ID), `MediaRegion`(필수 3종)과 `MeetingFeatures`·`Tags`를 넣는다.
3. <strong>참석자 생성</strong>: 역할마다 `CreateAttendee`에 `ExternalUserId`와 `Capabilities`를 넣어 JoinToken을 받는다. 처음부터 참석자를 같이 만들려면 `CreateMeetingWithAttendees`(`POST /meetings?operation=create-attendees`, 참석자 1~20명)를 쓴다.
4. <strong>JoinToken 전달</strong>: 브라우저에는 HTTPS 응답으로, 디바이스에는 MQTT로 보낸다.
5. <strong>정리</strong>: 권한을 회수할 때 `DeleteAttendee`, 시청이 끝나면 `DeleteMeeting`을 호출한다.
6. <strong>이벤트 처리</strong>: 참석자 입장·이탈 이벤트로 상태를 갱신한다.

### 미팅·참석자 생성 코드

AWS SDK for JavaScript v3의 `@aws-sdk/client-chime-sdk-meetings`로 "운영자가 트랙터 영상을 보려고 할 때" 미팅을 여는 코드다. 디바이스는 비디오만 보내고, 운영자는 비디오를 받고 음성을 주고받는다.

```js
// meeting-service.js — 백엔드에서만 실행한다 (AWS 자격증명 필요)
import {
  ChimeSDKMeetingsClient,
  CreateMeetingCommand,
  CreateAttendeeCommand,
  DeleteMeetingCommand,
} from '@aws-sdk/client-chime-sdk-meetings';
import { randomUUID } from 'node:crypto';

// control Region: 여기서 만든 미팅은 여기서만 수정·삭제할 수 있다
const chime = new ChimeSDKMeetingsClient({ region: 'ap-northeast-2' });

export async function openLiveSession(machineId, operatorId) {
  const { Meeting } = await chime.send(new CreateMeetingCommand({
    ClientRequestToken: randomUUID(),            // 요청 식별자. 미팅마다 다른 값을 쓴다
    ExternalMeetingId: `live-${machineId}-${Date.now()}`,
    MediaRegion: 'ap-northeast-2',               // 미디어가 실제로 호스팅되는 리전
    MeetingFeatures: {
      Video: { MaxResolution: 'HD' },            // FHD로 올리면 참석자 상한이 25로 내려간다
      Attendee: { MaxCount: 5 },                 // 디바이스 1 + 운영자 소수
    },
    Tags: [{ Key: 'machineId', Value: machineId }],
  }));

  // 디바이스: 비디오만 보낸다
  const { Attendee: device } = await chime.send(new CreateAttendeeCommand({
    MeetingId: Meeting.MeetingId,
    ExternalUserId: `machine:${machineId}`,
    Capabilities: { Audio: 'None', Video: 'Send', Content: 'None' },
  }));

  // 운영자: 음성은 주고받고, 비디오는 받기만 한다
  const { Attendee: operator } = await chime.send(new CreateAttendeeCommand({
    MeetingId: Meeting.MeetingId,
    ExternalUserId: `operator:${operatorId}`,
    Capabilities: { Audio: 'SendReceive', Video: 'Receive', Content: 'None' },
  }));

  return { Meeting, device, operator };
}

export async function closeLiveSession(meetingId) {
  // 참석자 JoinToken도 함께 만료된다
  await chime.send(new DeleteMeetingCommand({ MeetingId: meetingId }));
}
```

`CreateMeeting` 응답의 `MediaPlacement`에는 `AudioHostUrl`, `AudioFallbackUrl`, `SignalingUrl`, `TurnControlUrl`, `ScreenDataUrl`, `ScreenSharingUrl`, `ScreenViewingUrl`, `EventIngestionUrl`이 들어 있다. 클라이언트 SDK가 이 URL로 미디어 서비스에 접속하므로 백엔드는 `Meeting` 객체를 그대로 넘기면 된다.

HTTP 핸들러는 운영자에게는 운영자 참석자만, 디바이스에는 디바이스 참석자만 전달한다. 디바이스 쪽은 AWS IoT Core의 MQTT 토픽으로 보낸다([MQTT 프로토콜과 AWS IoT 적용](/posts/tech/2025-08-13-mqtt)).

```js
// routes/live.js
import express from 'express';
import { IoTDataPlaneClient, PublishCommand } from '@aws-sdk/client-iot-data-plane';
import { openLiveSession } from './meeting-service.js';

const iotData = new IoTDataPlaneClient({
  region: 'ap-northeast-2',
  endpoint: process.env.IOT_DATA_ENDPOINT,   // 'https://' + describe-endpoint --endpoint-type iot:Data-ATS 결과
});

export const router = express.Router();

router.post('/machines/:machineId/live', requireOperator, async (req, res) => {
  const { machineId } = req.params;
  await assertCanWatch(req.user, machineId);   // 인가: 이 운영자가 이 기계를 볼 수 있는가

  const { Meeting, device, operator } = await openLiveSession(machineId, req.user.id);

  // 디바이스에는 MQTT로 참가 정보를 보낸다 (토픽 구독 권한은 thing 단위로 제한한다)
  await iotData.send(new PublishCommand({
    topic: `machines/${machineId}/media/join`,
    qos: 1,
    payload: Buffer.from(JSON.stringify({ meeting: { Meeting }, attendee: { Attendee: device } })),
  }));

  // 브라우저에는 운영자 참석자만 준다. 디바이스 JoinToken을 섞어 보내지 않는다
  res.json({ meeting: { Meeting }, attendee: { Attendee: operator } });
});
```

`requireOperator`·`assertCanWatch`는 각자의 인증·인가 미들웨어 자리다. 디바이스가 구독하는 토픽은 IoT 정책에서 자기 thing 이름이 들어간 토픽으로만 제한해야 다른 기계의 JoinToken을 엿볼 수 없다([AWS IoT Core 완전 정복](/posts/tech/2025-06-27-iot)).

### Capabilities 규칙

`Audio`·`Video`·`Content`는 각각 `SendReceive`·`Send`·`Receive`·`None` 중 하나다. API 레퍼런스가 적은 모서리 규칙은 다음과 같다.

- 미팅을 `MeetingFeatures.Video.MaxResolution: None`으로 만들면, `Video`에 `SendReceive`·`Send`·`Receive`를 넣은 요청은 모두 `ValidationError 400`으로 거절된다. `Content`도 같은 규칙이다.
- `Content`를 `SendReceive`나 `Receive`로 하려면 `Video`도 `SendReceive`나 `Receive`여야 한다. 반대(비디오는 받고 콘텐츠는 안 받음)는 된다.
- `Audio`를 `None`·`Receive`에서 `Send`·`SendReceive`로 바꾸면 참석자가 음소거를 풀 때 바로 오디오가 흐른다.
- `Video`·`Content`를 받기 전용에서 보내기로 바꾸면, 클라이언트와 서버 사이의 미디어 재협상이 끝난 뒤에야 다른 참석자에게 보인다.

디바이스 참석자를 `Video: 'Send'`로 고정해 두면, 디바이스 JoinToken이 유출되더라도 그 토큰으로 다른 사람의 영상을 받아 볼 수는 없다. 역할별 최소 권한을 Capabilities로 표현하는 셈이다.

### 참가 시퀀스

![온디맨드 미팅 참가 시퀀스. 운영자 브라우저가 백엔드에 POST /machines/tractor-07/live를 보내면, 백엔드가 Chime 컨트롤 플레인에 CreateMeeting(MediaRegion)을 호출해 Meeting(MediaPlacement)을 받고, CreateAttendee를 두 번 호출해 Attendee(JoinToken)를 받는다. 백엔드는 AWS IoT Core에 MQTT join 명령을 publish해 농기계 디바이스에 전달하고, 브라우저에는 Meeting과 운영자 Attendee를 돌려준다. 디바이스는 Chime 미디어 서비스에 WSS와 JoinToken으로 join한 뒤 비디오를 publish하고, 브라우저도 join해 비디오를 subscribe하며 SFU가 전달한 비디오 타일을 SRTP로 받는다. 이후 AttendeeJoined 이벤트가 백엔드로 오고, 시청이 끝나면 백엔드가 DeleteMeeting을 호출한다](/images/study-webrtc/23-join-sequence-light.png)
![온디맨드 미팅 참가 시퀀스. 운영자 브라우저가 백엔드에 POST /machines/tractor-07/live를 보내면, 백엔드가 Chime 컨트롤 플레인에 CreateMeeting(MediaRegion)을 호출해 Meeting(MediaPlacement)을 받고, CreateAttendee를 두 번 호출해 Attendee(JoinToken)를 받는다. 백엔드는 AWS IoT Core에 MQTT join 명령을 publish해 농기계 디바이스에 전달하고, 브라우저에는 Meeting과 운영자 Attendee를 돌려준다. 디바이스는 Chime 미디어 서비스에 WSS와 JoinToken으로 join한 뒤 비디오를 publish하고, 브라우저도 join해 비디오를 subscribe하며 SFU가 전달한 비디오 타일을 SRTP로 받는다. 이후 AttendeeJoined 이벤트가 백엔드로 오고, 시청이 끝나면 백엔드가 DeleteMeeting을 호출한다](/images/study-webrtc/23-join-sequence-dark.png)

이 시퀀스에서 디바이스는 미팅이 생길 때까지 MQTT 연결만 유지한다. 영상 경로는 시청 요청이 있을 때만 열린다. KVS에서는 디바이스가 시그널링 채널에 상시 접속해 있었던 것과 대비된다.

### 미팅 이벤트로 디바이스 상태 보기

Chime SDK는 미팅 수명 주기 이벤트를 Amazon EventBridge, SNS, SQS로 보낸다. EventBridge 이벤트의 `source`는 `aws.chime`, `detail-type`은 `Chime Meeting State Change`이고, `detail.eventType`에 종류가 들어간다.

| eventType | 발생 시점 |
|---|---|
| `chime:MeetingStarted` / `chime:MeetingEnded` | 미팅 시작 / 종료(`DeleteMeeting` 호출 포함) |
| `chime:AttendeeAdded` / `chime:AttendeeDeleted` | 참석자 생성 / `DeleteAttendee`로 삭제 |
| `chime:AttendeeJoined` / `chime:AttendeeLeft` | 참석자가 실제로 접속 / 스스로 나감 |
| `chime:AttendeeDropped` | 서비스가 10~15초 동안 패킷을 받지 못해 끊긴 것으로 판단 |
| `chime:AttendeeAuthorized` | 이미 접속한 참석자의 JoinToken으로 다른 기기가 다시 접속(세션을 넘겨받음) |
| `chime:AttendeeVideoStarted` / `chime:AttendeeVideoStopped` | 비디오 송출 시작 / 중지 |

디바이스 관점에서 쓸모 있는 이벤트는 두 가지다. `AttendeeDropped`는 LTE 음영 지역에 들어간 농기계처럼 링크가 끊긴 상황을 10~15초 안에 알려 준다. 문서는 같은 이탈에 대해 `AttendeeLeft`와 `AttendeeDropped`를 둘 다 보내지 않는다고 명시하므로, Dropped만 세면 "의도하지 않은 끊김" 지표가 된다. `AttendeeAuthorized`는 같은 JoinToken으로 다른 기기가 들어와 세션을 넘겨받았다는 뜻이다. 사람이라면 노트북에서 휴대폰으로 옮긴 정상 상황이지만, <strong>디바이스 참석자에게 이 이벤트가 나면 JoinToken 유출을 의심</strong>해야 한다.

```json
{
  "source": ["aws.chime"],
  "detail-type": ["Chime Meeting State Change"],
  "detail": {
    "eventType": ["chime:AttendeeDropped", "chime:AttendeeAuthorized", "chime:MeetingEnded"]
  }
}
```

이 패턴으로 EventBridge 규칙을 만들고 Lambda나 SQS로 받아, `externalUserId`가 `machine:`으로 시작하는 이벤트만 디바이스 상태 테이블에 반영하면 된다.

## 4. 클라이언트 SDK

### 라이브러리 종류

공식 클라이언트 라이브러리는 다섯 가지다. 버전은 2026-10 기준 GitHub 릴리스다.

| 라이브러리 | 언어·플랫폼 | 최신 릴리스 | 비고 |
|---|---|---|---|
| `amazon-chime-sdk-js` | JavaScript/TypeScript, "WebRTC-enabled browsers" | v3.32.0 (2026-07-15) | npm 패키지 |
| `amazon-chime-sdk-android` | Kotlin, Android 5+ | v0.25.5 (2026-08-26) | |
| `amazon-chime-sdk-ios` | Swift, iOS 13+ | v0.27.4 (2026-08-25) | |
| `amazon-chime-sdk-cpp` (Windows) | C++, Windows 바이너리 | v0.11.2-cpp (2025-02-20) | 미리 빌드한 WebRTC 구현 포함 |
| `chime-sdk-signaling-cpp` | C++, 문서 표현으로 "embedded devices"용 | 위 저장소 하위 디렉터리 | WebRTC 구현 미포함 |

디바이스 관점에서 마지막 줄이 핵심이다. 클라이언트 라이브러리 문서는 C++ 시그널링 클라이언트를 "A C++ library that helps you set up signaling connections to Amazon Chime SDK meetings on embedded devices"라고 소개한다. 그런데 README는 이 SDK가 "does not include a WebRTC implementation required for media negotiation and tranmission with Amazon Chime SDK meetings"라고 적는다. 즉 <strong>시그널링만 해 주고, 미디어 송수신은 libwebrtc 같은 WebRTC 구현을 개발자가 직접 붙여야</strong> 한다. 빌드 안내는 Linux 기준이고, libwebsockets와 호환되는 OpenSSL 또는 mbedTLS가 필요하다.

KVS WebRTC C SDK가 시그널링·ICE·DTLS-SRTP·RTP 패킷화까지 한 덩어리로 제공하고 GStreamer 샘플까지 갖췄던 것([19장](/study/webrtc/19-kvs-c-sdk))과 비교하면, Chime SDK로 리눅스 임베디드 디바이스를 붙이는 일은 [13장](/study/webrtc/13-native-webrtc)에서 본 libwebrtc 빌드·크로스 컴파일 부담을 그대로 떠안는 일이다. 디바이스가 Android 기반(차량용 Android 단말, Android 기반 로봇 등)이라면 Android SDK가 현실적인 경로다.

### 브라우저 뷰어 코드

운영자 브라우저에서 §3의 응답을 받아 디바이스 영상만 화면에 붙이는 최소 코드다.

```js
import {
  ConsoleLogger,
  DefaultDeviceController,
  DefaultMeetingSession,
  LogLevel,
  MeetingSessionConfiguration,
} from 'amazon-chime-sdk-js';

const res = await fetch('/machines/tractor-07/live', { method: 'POST', credentials: 'include' });
const { meeting, attendee } = await res.json();

const logger = new ConsoleLogger('farm-viewer', LogLevel.WARN);
const deviceController = new DefaultDeviceController(logger);
const config = new MeetingSessionConfiguration(meeting, attendee);
const session = new DefaultMeetingSession(config, logger, deviceController);
const av = session.audioVideo;

const videoEl = document.getElementById('machine-video');

av.addObserver({
  videoTileDidUpdate: (tile) => {
    // 로컬 타일·콘텐츠 공유는 건너뛰고, 디바이스 참석자의 타일만 붙인다
    if (!tile.boundAttendeeId || tile.localTile || tile.isContent) return;
    if (!tile.boundExternalUserId?.startsWith('machine:')) return;
    av.bindVideoElement(tile.tileId, videoEl);
  },
  videoTileWasRemoved: (tileId) => console.info('타일 제거', tileId),
  audioVideoDidStop: (status) => console.warn('세션 종료', status.statusCode()),
});

// 믹스 오디오를 재생할 <audio> 요소. 운영자 음성을 보내려면 start 전에 마이크를 선택한다
await av.bindAudioElement(document.getElementById('meeting-audio'));
av.start();
```

비디오는 "타일" 단위로 관리된다. 원격 참석자가 비디오를 publish하면 SDK가 타일을 만들고 `videoTileDidUpdate`를 호출한다. 앱은 타일을 `<video>` 요소에 바인딩만 하면 되고, subscribe·재협상·simulcast 레이어 선택은 SDK가 처리한다. `ExternalUserId`에 `machine:` 같은 접두사를 붙여 둔 이유가 여기서 드러난다. 타일 이벤트에서 참석자 종류를 구분할 수 있기 때문이다.

### 데이터 메시지

Chime SDK에는 참석자끼리 짧은 메시지를 주고받는 기능이 있다. 건당 최대 2 KB다.

```js
// 받기: 토픽 단위로 구독
av.realtimeSubscribeToReceiveDataMessage('ui', (msg) => {
  console.log(msg.senderExternalUserId, msg.json());
});
// 보내기: (토픽, 데이터, 보존 시간 ms)
av.realtimeSendDataMessage('ui', { action: 'pin', target: 'machine:tractor-07' }, 0);
```

"화면 고정", "줌 요청" 같은 가벼운 UI 신호에는 충분하다. 하지만 정지·조향 같은 제어 명령을 여기에 싣는 것은 권하지 않는다. 미팅이 없으면 채널도 없고, 디바이스가 미팅에 들어와 있을 때만 동작하기 때문이다. 제어는 [11장](/study/webrtc/11-datachannel)에서 정리한 기준대로 시퀀스 번호·워치독을 갖춘 별도 채널(MQTT 등)에 둔다.

## 5. Media Pipelines

미팅의 미디어는 SFU 안에만 있다. 녹화하거나 외부로 송출하려면 AWS 쪽에서 미팅 미디어를 받아 가공하는 구성 요소가 필요한데, 이것이 Media Pipelines다. 디바이스나 브라우저가 따로 녹화·송출할 필요가 없다는 점이 장점이다.

![Media Pipelines 종류와 목적지. Chime SDK 미팅에서 media capture 파이프라인(합성 옵션 GridView 등)이 S3에 스트림별 조각 파일과 미팅 이벤트·데이터 메시지를 저장하고, media concatenation 파이프라인이 capture 결과를 소스로 받아 S3에 하나로 합친 파일을 만든다. media live connector 파이프라인(합성 옵션)은 RTMP(S)로 IVS·YouTube·Twitch에 H.264 HD/FHD와 AAC로 송출하고, media stream 파이프라인은 KVS 스트림 풀에 참석자별 오디오와 믹스 오디오를 보낸다. media insights(call analytics)는 KVS 스트림을 소스로 받아 Transcribe·음성 분석·S3 녹음을 한다](/images/study-webrtc/23-media-pipelines-light.png)
![Media Pipelines 종류와 목적지. Chime SDK 미팅에서 media capture 파이프라인(합성 옵션 GridView 등)이 S3에 스트림별 조각 파일과 미팅 이벤트·데이터 메시지를 저장하고, media concatenation 파이프라인이 capture 결과를 소스로 받아 S3에 하나로 합친 파일을 만든다. media live connector 파이프라인(합성 옵션)은 RTMP(S)로 IVS·YouTube·Twitch에 H.264 HD/FHD와 AAC로 송출하고, media stream 파이프라인은 KVS 스트림 풀에 참석자별 오디오와 믹스 오디오를 보낸다. media insights(call analytics)는 KVS 스트림을 소스로 받아 Transcribe·음성 분석·S3 녹음을 한다](/images/study-webrtc/23-media-pipelines-dark.png)

| 종류 | 소스 → 목적지 | 하는 일 |
|---|---|---|
| media capture | 미팅 → S3 | 오디오·비디오·콘텐츠 공유 스트림과 미팅 이벤트·데이터 메시지를 S3에 저장한다. 미팅당 1개 |
| media concatenation | capture 결과 → S3 | capture가 남긴 조각 파일을 하나로 합친다 |
| media live connector | 미팅 → RTMP(S) | IVS·YouTube·Twitch 같은 스트리밍 서비스로 송출한다 |
| media stream | 미팅 → KVS | 참석자별 오디오와 믹스 오디오를 Kinesis Video Streams 스트림 풀에 보낸다. 미팅당 1개 |
| compositing | capture·live connector의 옵션 | 웹캠·콘텐츠 공유 영상을 한 화면으로 합성한다 |
| media insights (call analytics) | 실시간 오디오 → Transcribe 등 | 전사·통화 분석·음성 분석·S3 녹음 |

각 종류의 세부 사항은 다음과 같다.

- <strong>live connector</strong>는 RTMP over TLS(RTMPS)를 지원하고, 싱크 URL은 `rtmp(s)://{stream-server}/{stream-key}` 형식이다. 오디오는 AAC(44,100 Hz 기본, 48,000 Hz 가능, mono 기본), 비디오는 H.264로 HD 1280x720 또는 FHD 1920x1080, 30fps, 2초마다 키프레임이다. 문서는 IVS 예시로 `rtmps://...global-contribute.live-video.net:443/app/{IVS-stream-key}`를 든다.
- <strong>compositing</strong>의 기본 레이아웃은 `GridView`다. 웹캠 스트림을 최대 25개까지 카메라를 켠 순서대로 배치하고, Landscape(1280x720, FHD 1920x1080)와 Portrait(720x1280, FHD 1080x1920) 방향을 고를 수 있다. 콘텐츠 공유가 시작되면 `ActiveSpeakerOnlyConfiguration`·`PresenterOnlyConfiguration`·`VerticalLayoutConfiguration`·`HorizontalLayoutConfiguration` 중 지정한 레이아웃으로 자동 전환된다.
- <strong>media stream</strong>은 문서상 오디오(참석자별 오디오 + 믹스 오디오)만 다룬다. 비디오를 KVS로 보내는 용도가 아니다. 미팅이 opt-in 리전을 `MediaRegion`으로 쓰면 KVS 스트림도 같은 리전에 있어야 한다.
- <strong>media insights(call analytics)</strong>는 Amazon Transcribe, Transcribe Call Analytics, Chime SDK voice analytics와 연동해 실시간 오디오에서 인사이트를 만들고 통화를 S3에 녹음한다. 콘솔에서 Voice Connector에 구성을 연결하거나 API로 만든다. 별도 quota 절이 있다.

### capture 파이프라인으로 녹화하기

`@aws-sdk/client-chime-sdk-media-pipelines`로 미팅을 S3에 녹화하는 코드다.

```js
import {
  ChimeSDKMediaPipelinesClient,
  CreateMediaCapturePipelineCommand,
  DeleteMediaPipelineCommand,
} from '@aws-sdk/client-chime-sdk-media-pipelines';

const pipelines = new ChimeSDKMediaPipelinesClient({ region: 'ap-northeast-2' });

export async function startRecording(accountId, meetingId) {
  const { MediaCapturePipeline } = await pipelines.send(new CreateMediaCapturePipelineCommand({
    SourceType: 'ChimeSdkMeeting',
    SourceArn: `arn:aws:chime::${accountId}:meeting:${meetingId}`,
    SinkType: 'S3Bucket',
    SinkArn: 'arn:aws:s3:::farm-live-recordings',   // 버킷 정책으로 미디어 파이프라인의 쓰기를 허용해야 한다
  }));
  return MediaCapturePipeline.MediaPipelineId;
}

export async function stopRecording(mediaPipelineId) {
  await pipelines.send(new DeleteMediaPipelineCommand({ MediaPipelineId: mediaPipelineId }));
}
```

::: warning 파이프라인 운영 함정
- <strong>live connector는 목적지 쪽에서 방송을 끝내도 멈추지 않는다.</strong> 문서는 "Ending a stream on a streaming platform such as IVS does not stop a media live connector pipeline."이라고 경고한다. 반드시 `DeleteMediaPipeline`으로 멈춘다. 잊으면 분당 요금이 계속 쌓인다.
- <strong>동시 파이프라인 한도가 낮다.</strong> us-east-1이 100, 서울을 포함한 그 밖의 리전은 10이다(조정 가능). 기계 수십 대를 동시에 녹화하려면 증설 요청이 먼저다.
- <strong>녹화 고지 의무.</strong> 문서는 미팅 녹화가 전자 통신 녹음 관련 법규의 적용을 받을 수 있고, 참석자에게 녹화 사실을 알리고 동의를 받을 책임이 개발자와 최종 사용자에게 있다고 명시한다. 운영자 음성이 섞이는 녹화라면 UI에 녹화 표시를 둔다.
:::

디바이스 영상 녹화라는 목적만 놓고 보면, capture는 조각 파일을 S3에 쌓고 concatenation으로 다시 합치는 2단계 구조다. KVS WebRTC ingestion이 Kinesis Video Stream에 바로 저장하고 HLS/DASH로 재생하게 해 주는 것([21장](/study/webrtc/21-kvs-ingestion-storage))과 비교해 후처리 단계가 하나 더 있다. 대신 여러 참석자의 영상·음성·이벤트를 한꺼번에 남길 수 있다는 점은 Chime 쪽이 낫다.

## 6. 한도와 과금

### 요금표

AWS Price List API(AmazonChimeServices/AmazonChimeFeatures, publicationDate 2026-09-11)로 2026년 10월에 확인한 값이다. us-east-1과 서울(ap-northeast-2)의 요율이 같다. 단위는 USD다.

| 항목 | 요율 |
|---|---|
| WebRTC attendee-minute(표준) | $0.0017 / 참석자·분 |
| FHD attendee-minute | $0.0034 / 참석자·분 |
| replica 미팅 분 / FHD replica | $0.0085 / $0.017 |
| media capture(오디오·비디오·콘텐츠 스트림당) | $0.0017 / 분 |
| active speaker capture | $0.0034 / 분 |
| compositing recording HD / FHD | $0.01 / $0.0125 per 분 |
| concatenation | $0.002 / 분 |
| live connector | $0.002 / 분 |
| compositing live connector HD / FHD | $0.09 / $0.125 per 분 |
| echo reduction | $0.0023 / 분 |

가격 페이지는 attendee-minute을 <strong>6초 단위로 과금하고 최소 6초</strong>라고 설명한다. call analytics는 가격 페이지 예시에 $0.023/분이 나오지만, media insights 파이프라인 단독 요금은 확인하지 못했다.

### 비용 추정

과금 단위가 "참석자·분"이라는 점이 핵심이다. <strong>디바이스도 참석자</strong>이므로 디바이스가 미팅에 있는 시간도 과금된다.

- <strong>한 번 시청</strong>: 트랙터 1대 + 운영자 2명이 1시간 미팅을 하면 3 × 60 × $0.0017 = <strong>$0.306</strong>이다.
- <strong>한 달 운영</strong>: 기계 50대를 하루 2시간씩, 매번 운영자 1명이 30일 동안 본다고 하자. 참석자 2 × 120분 × 30일 × 50대 = 360,000 참석자·분이므로 360,000 × $0.0017 = <strong>$612</strong>다.
- <strong>녹화 추가</strong>: 디바이스 비디오 스트림 1개만 capture한다면 50대 × 120분 × 30일 = 180,000분 × $0.0017 = $306이 더해진다. concatenation 요율을 같은 분 수에 곱하면 $360이 추가되고, S3 저장 비용은 별도다. 분당 요율에 녹화 분 수를 곱한 단순 추정이다.
- <strong>상시 접속의 함정</strong>: 디바이스 하나를 미팅에 하루 종일 넣어 두면 혼자 있어도 43,200분(30일) × $0.0017 = 월 $73.44다. 게다가 미팅은 24시간이 지나면 자동 종료되므로 상시 접속은 비용과 구조 모두에서 맞지 않는다.

같은 상황을 KVS WebRTC(서울)와 비교하면 차이가 분명하다. KVS는 활성 채널 월 $0.04, 시그널링 메시지 100만 건당 $2.75, TURN 1,000분당 $0.15이고, P2P 직결 경로에는 분당 미디어 요금이 없다([22장](/study/webrtc/22-kvs-operations)). 디바이스 1대를 소수가 가끔 보는 용도라면 KVS가 훨씬 싸다. Chime SDK의 요금은 서버가 미디어를 받아 전달·믹싱·녹화해 주는 대가다.

## 7. 디바이스 영상 플랫폼 관점: 맞는 지점과 안 맞는 지점

지금까지 본 사실을 "카메라 달린 농기계 → 운영자 브라우저" 시나리오에 대어 보자.

### 맞는 지점

- <strong>디바이스 업링크가 시청자 수와 무관하다.</strong> SFU라서 디바이스는 미디어 서비스에 한 번만 올린다. KVS WebRTC는 viewer마다 PeerConnection을 따로 맺어 업링크가 viewer 수만큼 늘어난다([16장](/study/webrtc/16-aws-landscape)). LTE 업링크가 빠듯한 농기계에 의미 있는 차이다.
- <strong>다자 음성 협업에 강하다.</strong> 고장 난 콤바인의 카메라 영상을 놓고 현장 기사(모바일), 관제실 운영자(브라우저), 제조사 원격 엔지니어(브라우저)가 대화하는 "원격 정비 지원" 같은 시나리오에 딱 맞는다. 오디오가 서버에서 믹싱되므로 참석자가 늘어도 각자 받는 오디오는 하나다.
- <strong>녹화·송출을 서버에서 한다.</strong> Media Pipelines로 S3 녹화나 RTMP(S) 송출을 디바이스 부담 없이 붙일 수 있다.
- <strong>상태 이벤트가 있다.</strong> `AttendeeDropped`(10~15초)와 `AttendeeAuthorized`로 디바이스 링크 끊김과 토큰 유출 징후를 감시할 수 있다.
- <strong>서울 MediaRegion</strong>과 성숙한 브라우저·모바일 SDK가 있다.

### 안 맞는 지점

- <strong>리눅스 임베디드용 "미디어 포함" SDK가 없다.</strong> 공식 경로는 C++ 시그널링 클라이언트이고, WebRTC 미디어 구현은 직접 붙여야 한다. Jetson이나 Raspberry Pi 기반 카메라 유닛이라면 KVS C SDK보다 구현 부담이 훨씬 크다.
- <strong>미팅은 세션이다.</strong> 24시간 자동 종료, 참석자 없이 5분이면 종료라서 디바이스가 상시 대기하는 채널 모델을 만들 수 없다. 시청 요청 → 미팅 생성 → MQTT로 디바이스 호출이라는 on-demand 흐름과 그만큼의 영상 시작 지연을 받아들여야 한다.
- <strong>참석자 하나에 비디오 소스 하나다.</strong> 전방·후방·작업기·운전석 카메라 4대를 단 콤바인은 참석자 4개로 들어와야 하고, attendee-minute도 JoinToken 관리도 4배가 된다. KVS C SDK에는 비디오 4개·오디오 1개를 함께 보내는 `kvsWebrtcClientMaster_4Video_1Audio` 샘플이 있는 것과 대조적이다.
- <strong>디바이스 시간도 과금된다.</strong> 미팅에 머무는 매 분이 비용이다. 시청이 끝나면 즉시 `DeleteMeeting`을 호출하는 정리 로직이 필수다.
- <strong>화질 상한과 트레이드오프.</strong> JS 클라이언트 기준 비디오는 720p 30fps이고, FHD를 켜면 참석자 상한이 25로 내려가고 요율이 2배가 된다.
- <strong>제어 채널로 쓰기 어렵다.</strong> 데이터 메시지는 건당 2 KB이고 미팅이 있을 때만 존재한다. 원격 제어는 미팅과 무관하게 살아 있는 MQTT 쪽에 둔다.

### 정리: 언제 Chime SDK를 고르나

| 요구 | 추천 | 이유 |
|---|---|---|
| 운영자 소수가 디바이스 1대를 언제든 바로 본다 | KVS WebRTC([17장](/study/webrtc/17-kvs-architecture)) | 채널 상시 대기, C SDK, 저렴한 고정비 |
| 디바이스 영상을 놓고 여러 사람이 음성으로 협업한다 | Chime SDK | SFU + 오디오 믹싱, 회의용 SDK, Media Pipelines |
| 디바이스 영상을 다수에게 방송한다 | IVS Real-Time([24장](/study/webrtc/24-ivs-real-time)) | 스테이지당 대규모 구독, WHIP 송출 |

실무에서는 하나만 고르기보다 섞는 경우가 많다. 평소 관제는 KVS로 하고, 원격 정비 같은 협업이 필요할 때만 Chime 미팅을 여는 식이다. 이때 디바이스가 두 SDK를 모두 품기는 부담스러우므로, 어느 쪽을 디바이스에 넣고 어느 쪽을 브라우저 측에서 연결할지가 설계 포인트가 된다. 전체 플랫폼 관점의 선택은 [25장](/study/webrtc/25-capstone-farm-platform)에서 다시 정리한다.

::: tip 핵심 정리
- 2026-02-20에 지원이 끝난 것은 완성형 앱 Amazon Chime이고, Chime SDK는 영향이 없다고 AWS가 명시했다. 다만 SDK 안의 PSTN Audio는 2026-09-29 유지보수 모드, 2026-10-29 신규 고객 중단이다.
- 미디어 서비스는 비디오를 SFU(publish/subscribe, 미팅당 25개)로 전달하고, 오디오는 서버에서 Opus로 믹싱해 자기 소리를 뺀 스트림 하나를 보낸다.
- 백엔드는 control Region에서 `CreateMeeting`(`ClientRequestToken`·`ExternalMeetingId`·`MediaRegion`)과 `CreateAttendee`(`ExternalUserId`·`Capabilities`)를 호출하고 JoinToken을 역할별로 나눠 준다. 미디어 경로에는 끼지 않는다.
- 미팅은 24시간, 무참석 5분이면 자동 종료되는 세션이다. 참석자 250(FHD·UHD 시 25), 비디오 25가 기본 한도이고, replica는 Quota 기본 4와 마케팅 페이지의 40이 다르다.
- Media Pipelines는 capture(S3)·concatenation·live connector(RTMP(S))·media stream(KVS, 오디오)·compositing(GridView)·media insights로 나뉜다. live connector는 반드시 `DeleteMediaPipeline`으로 멈춘다.
- 과금은 attendee-minute($0.0017, 6초 단위)이고 디바이스도 참석자다. 디바이스 업링크 절약과 다자 협업에는 맞지만, 임베디드 미디어 SDK 부재·세션형 미팅·참석자당 비디오 1개라는 점에서 상시 디바이스 관제에는 맞지 않는다.
:::

## 다음 챕터

[Amazon IVS Real-Time Streaming](/study/webrtc/24-ivs-real-time)에서는 Stage와 Participant Token으로 이뤄진 IVS의 publish/subscribe 모델, 서버 측 합성(Composition)과 녹화, 브라우저 SDK 없이 WHIP으로 송출하는 방법, 참가자 접속 위치 기준 과금을 다루고 디바이스 영상 플랫폼 관점에서 다시 평가한다.
