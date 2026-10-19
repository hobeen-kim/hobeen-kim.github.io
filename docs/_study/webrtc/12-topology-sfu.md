---
title: "토폴로지: Mesh·SFU·MCU"
description: "다자간 WebRTC에서 Mesh·SFU·MCU가 업링크·다운링크·서버 CPU를 어떻게 나눠 갖는지 비교하고, Simulcast·SVC, 오픈소스 SFU, 캐스케이딩, 녹화, Encoded Transform·SFrame 기반 E2EE까지 SFU 운영의 핵심 주제를 다룬다."
date: 2026-10-19
tags: [WebRTC, SFU, Simulcast, SVC, E2EE, SFrame]
prev: /study/webrtc/11-datachannel
next: /study/webrtc/13-native-webrtc
---

# 토폴로지: Mesh·SFU·MCU

::: info 학습 목표
- N명 세션에서 Mesh·SFU·MCU의 업링크·다운링크 스트림 수와 서버 CPU 부담을 계산하고, "카메라 1대 → 운영자 여러 명" 시나리오에서 어떤 토폴로지가 맞는지 판단한다.
- Simulcast(`rid`, `RTCRtpEncodingParameters`)와 SVC(`scalabilityMode`)의 차이를 이해하고 브라우저 코드로 설정할 수 있다.
- mediasoup·Janus·LiveKit·Pion 기반 SFU의 언어·라이선스·특징을 비교하고, 캐스케이딩과 녹화 아키텍처를 설계할 수 있다.
- SFU가 평문 미디어를 보는 구조적 이유와, Encoded Transform(`RTCRtpScriptTransform`)·SFrame(RFC 9605)으로 E2EE를 얹는 원리를 설명할 수 있다.
:::

## 1. 세 가지 토폴로지 — 누가 누구에게 보내는가

지금까지(02~11장)는 PeerConnection 하나가 피어 둘을 잇는 1:1 구조만 다뤘다. 참가자가 셋 이상이 되면 "미디어를 누가 누구에게 보내는가"를 정해야 하고, 이 선택을 <strong>토폴로지</strong>라고 부른다. 선택지는 크게 세 가지다.

![Mesh는 피어 네 개가 서로 양방향 화살표로 전부 직접 연결돼 피어당 업링크·다운링크가 각각 N-1개이고, SFU는 피어마다 중앙 SFU로 업링크 1개를 보내고 SFU로부터 다운링크를 받으며, MCU는 피어마다 업링크 1개를 보내고 MCU가 합성한 다운링크 1개만 받는 세 패널 비교 그림](/images/study-webrtc/12-topologies-light.png)
![Mesh는 피어 네 개가 서로 양방향 화살표로 전부 직접 연결돼 피어당 업링크·다운링크가 각각 N-1개이고, SFU는 피어마다 중앙 SFU로 업링크 1개를 보내고 SFU로부터 다운링크를 받으며, MCU는 피어마다 업링크 1개를 보내고 MCU가 합성한 다운링크 1개만 받는 세 패널 비교 그림](/images/study-webrtc/12-topologies-dark.png)

<strong>Mesh(P2P 전체 연결)</strong>는 모든 피어가 나머지 모두와 PeerConnection을 하나씩 맺는다. 서버는 시그널링(필요하면 TURN)만 담당하고 미디어는 만지지 않는다. 문제는 피어마다 PeerConnection이 N-1개라는 점이다. libwebrtc 기반 브라우저는 PeerConnection마다 인코더를 따로 돌리므로, 같은 카메라 영상을 N-1번 인코딩하고 N-1번 업로드한다. 업링크 대역폭과 CPU가 참가자 수에 비례해 늘어난다.

<strong>SFU(Selective Forwarding Unit)</strong>는 각 피어가 서버와만 연결한다. 피어는 자기 스트림을 한 번만 올리고, SFU가 이를 다른 피어들에게 복제해 보낸다. SFU는 피어마다 ICE·DTLS-SRTP를 종단하므로 들어온 SRTP를 복호화하고, RTP 헤더(SSRC·시퀀스 번호·타임스탬프)를 수신자별로 다시 쓴 뒤, 수신자의 키로 재암호화해 내보낸다. 디코딩·인코딩은 하지 않는다. 이름의 "Selective"는 수신자마다 <strong>어떤 스트림·어떤 품질 계층을 보낼지 고른다</strong>는 뜻이다(2절).

<strong>MCU(Multipoint Control Unit)</strong>는 모든 입력 스트림을 디코딩해 하나의 레이아웃으로 합성하고, 다시 인코딩해 각 피어에게 한 개씩 보낸다. 클라이언트는 업 1·다운 1로 가장 가볍지만, 서버가 N개 디코드 + 합성 + 인코드를 하므로 CPU 비용이 압도적이고, 재인코딩만큼 지연과 화질 손실이 생기며, 레이아웃이 서버에서 고정된다. SIP/H.323 같은 레거시 회의 단말, 성능이 아주 낮은 수신 단말, "합성된 한 화면"을 방송·녹화로 내보내야 하는 경우에 여전히 쓰인다. 23·24장의 Chime SDK 미디어 파이프라인과 IVS Composition도 결국 서버 측 합성이라는 점에서 MCU의 역할을 일부 떠맡는다.

### N명일 때 비교

참가자 N명이 모두 송신·수신하는 회의를 가정한다(스트림은 비디오 트랙 기준).

| 항목 | Mesh | SFU | MCU |
|---|---|---|---|
| 클라이언트 업링크 스트림 | N-1 | 1 (Simulcast면 계층 수 k) | 1 |
| 클라이언트 다운링크 스트림 | N-1 | N-1 | 1 (합성본) |
| 클라이언트 인코딩 횟수 | N-1 (PeerConnection별) | 1 (Simulcast면 k) | 1 |
| 클라이언트 디코딩 횟수 | N-1 | N-1 | 1 |
| 서버 수신 / 송신 스트림 | 0 / 0 | N / N(N-1) | N / N |
| 서버 CPU | 없음 (시그널링만) | 낮음~중간 (SRTP 복호·재암호화, 헤더 재작성, 라우팅) | 매우 높음 (N 디코드 + 합성 + 인코드) |
| 서버가 더하는 지연 | 없음 | 작음 (패킷 포워딩) | 큼 (디코드·합성·재인코드) |
| 레이아웃 자유도 | 클라이언트 마음대로 | 클라이언트 마음대로 | 서버가 결정 |
| E2EE | 기본(원래 P2P) | Encoded Transform으로 가능 (6절) | 사실상 불가 (서버가 디코드해야 함) |

숫자로 보면 차이가 확실하다. 720p 1.5 Mbps 스트림으로 6명이 회의하면,

- Mesh: 각 클라이언트 업링크 1.5 × 5 = <strong>7.5 Mbps</strong>, 인코더 5개. 가정용 업링크나 노트북 CPU가 먼저 무너진다. 실무 경험칙으로 Mesh는 3~4명 정도까지가 한계로 여겨진다.
- SFU: 업링크 1.5 Mbps(Simulcast 3계층이면 1.5 + 0.5 + 0.15 ≈ 2.15 Mbps), 다운링크는 최대 7.5 Mbps지만 SFU가 작은 화면에는 낮은 계층을 보내 줄일 수 있다. 대신 서버 송신은 N(N-1) = 30 스트림이다.
- MCU: 업·다운 각 1.5 Mbps 수준. 대신 서버가 6개 디코드 + 합성 + 인코드를 한다(참가자별로 자기 화면을 뺀 레이아웃을 주면 인코드도 6번).

### 디바이스 시나리오로 다시 보기 — 카메라 1대, 운영자 M명

이 스터디의 주 시나리오는 "농기계 카메라 1대 → 운영자 브라우저 M명"이다. 송신자가 하나뿐이라 회의와는 계산이 다르다.

| 구조 | 디바이스 업링크 | 디바이스 인코딩·암호화 부담 | 비고 |
|---|---|---|---|
| P2P (뷰어마다 PeerConnection) | M × 비트레이트 | 뷰어별 SRTP 세션 M개 (인코더 공유 여부는 구현에 따라 다름) | KVS WebRTC가 이 구조 (16·17장) |
| SFU 경유 | 1 × 비트레이트 | 세션 1개 | 뷰어 수와 무관 |

LTE 업링크는 위치·시간대에 따라 수 Mbps 수준에서 크게 출렁인다(05·09장). 1.5 Mbps 스트림을 P2P로 운영자 4명에게 보내면 6 Mbps가 필요하고, 한 명이 더 붙는 순간 모든 뷰어의 화질이 함께 떨어진다. "디바이스 1 : 소수 시청"이면 P2P가 단순하고 서버 비용도 없지만, 시청자가 늘거나 녹화·AI 분석 같은 서버 측 소비자가 붙을수록 SFU로 업링크를 1로 고정하는 편이 낫다. 이 판단이 16장의 KVS WebRTC vs IVS Real-Time 비교로 이어진다.

## 2. Simulcast와 SVC — SFU가 고를 거리를 만든다

SFU는 트랜스코딩을 하지 않는다. 그런데 수신자는 제각각이다. 광대역 PC의 운영자는 720p를 원하고, LTE 위의 모바일은 360p가 한계이며, 16개 카메라를 격자로 보는 관제 화면은 썸네일이면 충분하다. 트랜스코딩 없이 이 요구를 맞추려면 <strong>송신자가 여러 품질을 미리 만들어 보내야</strong> 한다. 방법이 두 가지다.

![위쪽 Simulcast 패널에서는 송신자가 f(1280×720, 1.5Mbps)·h(640×360, 500kbps)·q(320×180, 150kbps) 독립 스트림 세 개를 SFU로 보내고 SFU가 PC 운영자에게 f, 모바일에 h, 썸네일 그리드에 q를 골라 전달하며, 아래쪽 SVC 패널에서는 송신자가 L0·L1·L2 계층이 담긴 단일 SSRC 스트림 하나를 보내고 SFU가 상위 계층을 드롭해 PC에 L0+L1+L2, 모바일에 L0+L1, 썸네일에 L0만 전달하는 비교 그림](/images/study-webrtc/12-simulcast-svc-light.png)
![위쪽 Simulcast 패널에서는 송신자가 f(1280×720, 1.5Mbps)·h(640×360, 500kbps)·q(320×180, 150kbps) 독립 스트림 세 개를 SFU로 보내고 SFU가 PC 운영자에게 f, 모바일에 h, 썸네일 그리드에 q를 골라 전달하며, 아래쪽 SVC 패널에서는 송신자가 L0·L1·L2 계층이 담긴 단일 SSRC 스트림 하나를 보내고 SFU가 상위 계층을 드롭해 PC에 L0+L1+L2, 모바일에 L0+L1, 썸네일에 L0만 전달하는 비교 그림](/images/study-webrtc/12-simulcast-svc-dark.png)

### Simulcast — 독립 스트림 여러 개

<strong>Simulcast</strong>는 같은 원본을 해상도·비트레이트가 다른 <strong>독립 인코딩 여러 개</strong>로 동시에 보낸다. 각 인코딩은 별도 SSRC를 갖고, SDP와 RTP 헤더 확장의 <strong>RID(RTP Stream Identifier)</strong>로 구분한다(SDP `a=rid`는 RFC 8851, 헤더 확장 `rtp-stream-id`는 RFC 8852, SDP의 Simulcast 표현은 RFC 8853). 브라우저에서는 `addTransceiver()`의 `sendEncodings`에 `RTCRtpEncodingParameters`를 계층 수만큼 넣는다.

```javascript
const stream = await navigator.mediaDevices.getUserMedia({
  video: { width: 1280, height: 720, frameRate: 30 },
});
const [track] = stream.getVideoTracks();

const transceiver = pc.addTransceiver(track, {
  direction: 'sendonly',
  sendEncodings: [
    { rid: 'q', scaleResolutionDownBy: 4, maxBitrate: 150_000 },   // 320x180
    { rid: 'h', scaleResolutionDownBy: 2, maxBitrate: 500_000 },   // 640x360
    { rid: 'f', scaleResolutionDownBy: 1, maxBitrate: 1_500_000 }, // 1280x720
  ],
});
```

이렇게 만든 offer에는 다음과 같은 줄이 생긴다. SFU는 이 줄을 보고 "이 m-line에 RID q·h·f 세 스트림이 온다"는 것을 안다.

```text
a=extmap:4 urn:ietf:params:rtp-hdrext:sdes:rtp-stream-id
a=extmap:5 urn:ietf:params:rtp-hdrext:sdes:repaired-rtp-stream-id
a=rid:q send
a=rid:h send
a=rid:f send
a=simulcast:send q;h;f
```

송신 중에 계층을 끄거나 비트레이트 상한을 바꾸는 것은 `setParameters()`로 한다. 예컨대 SFU가 "지금 아무도 f를 구독하지 않는다"고 알려 주면 f를 꺼서 디바이스 업링크와 인코더 부하를 줄일 수 있다.

```javascript
const sender = transceiver.sender;
const params = sender.getParameters();
const f = params.encodings.find((e) => e.rid === 'f');
f.active = false;              // 최상위 계층 송신 중단
await sender.setParameters(params);
```

SFU 쪽에서는 수신자별로 계층을 고른다. mediasoup라면 Consumer에 선호 계층을 지정한다.

```javascript
// mediasoup (Node.js): 이 수신자에게는 중간 계층(h)을 보낸다
await consumer.setPreferredLayers({ spatialLayer: 1, temporalLayer: 2 });
```

Simulcast의 계층 전환에는 비용이 있다. 계층마다 독립 스트림이므로 q에서 h로 갈아탈 때 수신자 디코더는 h의 <strong>키프레임</strong>부터 받아야 한다. SFU는 전환 시점에 송신자에게 PLI를 보내 h 계층의 키프레임을 요청하고, 키프레임이 도착하면 SSRC·시퀀스 번호·타임스탬프를 이어 붙여 수신자에게는 끊김 없는 한 스트림처럼 보이게 만든다. 키프레임 요청이 잦으면 송신자 업링크에 큰 프레임이 몰리므로(09장) SFU는 전환을 일정 시간 묶어서 판단한다.

### SVC — 계층 스트림 하나

<strong>SVC(Scalable Video Coding)</strong>는 인코더 하나가 <strong>계층 구조를 가진 스트림 하나</strong>를 만든다.

- <strong>시간 계층(T, temporal)</strong>: 프레임을 참조 관계에 따라 층으로 나눈다. 30fps 스트림에서 T0만 받으면 7.5fps, T0+T1이면 15fps, 전부 받으면 30fps가 되는 식이다. 상위 시간 계층 프레임은 아무도 참조하지 않으므로 SFU가 그냥 버려도 디코딩이 깨지지 않는다.
- <strong>공간 계층(L, spatial)</strong>: 저해상도 기본 계층 위에, 그것을 참조해 차이만 담는 고해상도 계층을 쌓는다. 상위 계층이 하위 계층을 재활용하므로 같은 품질 조합을 Simulcast보다 적은 업링크로 보낼 수 있는 것이 SVC의 장점이다.

브라우저에서는 W3C "Scalable Video Coding (SVC) Extension for WebRTC"(현재 Working Draft)가 `RTCRtpEncodingParameters`에 `scalabilityMode` 문자열 하나를 추가한다. 이름 규칙은 다음과 같다.

| 표기 | 의미 | 예 |
|---|---|---|
| `LxTy` | 공간 계층 x개, 시간 계층 y개. 공간 계층 간 해상도 비율 2:1 | `L1T3`(시간 계층만 3개), `L3T3` |
| `h` 접미사 | 공간 계층 비율 1.5:1 | `L2T3h` |
| `_KEY` | 상위 공간 계층이 키프레임에서만 하위 계층을 참조 | `L3T3_KEY` |
| `SxTy` | 한 SSRC 안에 담긴 Simulcast(계층 간 참조 없음) | `S3T3` |

코덱별 제약이 중요하다. 명세에 따르면 <strong>VP8·H.264·H.265는 시간 계층(`L1T2`, `L1T3`)과 별도 SSRC Simulcast만</strong> 지원하고, 공간 SVC와 `S` 모드는 <strong>VP9·AV1</strong>에서만 쓸 수 있다. 또한 `S` 모드는 여러 RID Simulcast와 함께 쓸 수 없다.

```javascript
// 1) VP8/H.264: Simulcast + 계층마다 시간 계층 3개
pc.addTransceiver(track, {
  sendEncodings: [
    { rid: 'q', scaleResolutionDownBy: 4, scalabilityMode: 'L1T3' },
    { rid: 'h', scaleResolutionDownBy: 2, scalabilityMode: 'L1T3' },
    { rid: 'f', scalabilityMode: 'L1T3' },
  ],
});

// 2) VP9/AV1: 단일 인코딩에 공간 3 x 시간 3 SVC
const t = pc.addTransceiver(track, {
  sendEncodings: [{ scalabilityMode: 'L3T3_KEY' }],
});
const codecs = RTCRtpSender.getCapabilities('video').codecs;
t.setCodecPreferences([
  ...codecs.filter((c) => c.mimeType === 'video/AV1'),
  ...codecs.filter((c) => c.mimeType === 'video/VP9'),
  ...codecs.filter((c) => !['video/AV1', 'video/VP9'].includes(c.mimeType)),
]);
```

요청한 모드를 협상된 코덱이 지원하지 않으면 브라우저는 가능한 모드로 낮춰 적용할 수 있다. 실제 적용값은 협상이 끝난 뒤 `sender.getParameters().encodings[0].scalabilityMode`로 확인한다.

SFU가 SVC 스트림에서 계층을 버리려면 패킷이 어느 계층인지 알아야 한다. VP8은 페이로드 디스크립터의 TID, VP9은 VP9 페이로드 디스크립터의 공간·시간 ID, AV1은 <strong>Dependency Descriptor</strong> RTP 헤더 확장을 읽는다. 이 정보가 페이로드가 아닌 헤더(또는 페이로드 앞부분)에 있다는 점이 6절의 E2EE와 맞물린다.

### Simulcast vs SVC

| 항목 | Simulcast | SVC |
|---|---|---|
| 스트림 구조 | 계층마다 독립 인코딩·별도 SSRC | 계층 구조 스트림 하나 (`S` 모드 제외) |
| 업링크 | 계층 비트레이트의 합 | 계층 간 참조로 Simulcast보다 적음 |
| 송신 인코딩 부하 | 계층 수만큼 인코딩 | 인코더 1개 (계층 구조만큼 복잡) |
| 계층 내리기 | 키프레임 필요 (다른 스트림으로 전환) | 패킷 드롭만으로 즉시 |
| 계층 올리기 | 키프레임 필요 | 상위 계층을 디코드할 수 있는 시점까지 대기 (모드에 따라 다름) |
| 코덱 | VP8·H.264 포함 대부분 | 공간 SVC는 VP9·AV1 |
| SFU 구현 | SSRC 전환·헤더 이어붙이기 | 코덱별 디스크립터·Dependency Descriptor 파싱 |
| 하드웨어 인코더 | 인코더 세션 여러 개로 구현 가능 | HW 인코더의 SVC 지원은 제한적 |

디바이스 관점에서 마지막 줄이 결정적이다. Jetson이나 Raspberry Pi의 하드웨어 H.264 인코더로는 공간 SVC를 쓸 수 없다. 디바이스에서 품질 계층이 필요하면 <strong>HW 인코더 세션을 2~3개 띄워 Simulcast</strong>로 보내거나, 단일 스트림만 올리고 계층 선택은 포기한 채 비트레이트 적응(09장)에 맡기는 것이 현실적이다. 운영자 화면이 썸네일 격자와 확대 화면을 오간다면 저해상도 + 고해상도 2계층 Simulcast가 좋은 절충이다.

## 3. 오픈소스 SFU 비교

SFU를 직접 운영하기로 했다면 바닥부터 만들기보다 검증된 오픈소스를 고른다. 언어·라이선스·추상화 수준이 크게 다르다(언어·라이선스는 2026년 10월 기준 각 GitHub 저장소 표기).

| SFU | 언어 | 라이선스 | 특징 | 잘 맞는 경우 |
|---|---|---|---|---|
| <strong>mediasoup</strong> | C++ 워커 + Node.js(TypeScript) API, Rust 크레이트 | ISC | 시그널링·방 개념이 없는 저수준 라이브러리. Router·Transport·Producer·Consumer 모델, Simulcast·SVC, `PipeTransport`로 워커·호스트 간 연결, `PlainTransport`로 평문 RTP 입출력 | 시그널링·인증·방 로직을 직접 설계하려는 팀 |
| <strong>Janus</strong> | C | GPL-3.0 | 플러그인 구조(VideoRoom, Streaming, SIP, Record&Play 등), HTTP/WebSocket JSON API, 자체 녹화(`.mjr`) | SIP 게이트웨이, RTP/RTSP 카메라를 WebRTC로 내보내는 Streaming 플러그인 |
| <strong>LiveKit</strong> | Go (Pion 기반) | Apache-2.0 | 시그널링·방·JWT 인증·클라이언트 SDK까지 일체형, Redis로 다중 노드, Egress(녹화)·Ingress | 빠르게 제품 수준 기능이 필요할 때 |
| <strong>ion-sfu</strong> | Go (Pion 기반) | MIT | Pion 생태계의 초기 SFU. 저장소 마지막 푸시가 2023년 7월로 사실상 정체 | 학습·구조 참고용 |
| <strong>Galene</strong> | Go (Pion 기반) | MIT | 단일 바이너리 회의 서버, Simulcast·SVC(VP8/VP9)·디스크 녹화 | 소규모 회의·강의, 사내 도구 |
| <strong>Jitsi Videobridge</strong> | Kotlin/Java | Apache-2.0 | Jitsi Meet 스택의 SFU, 브리지 간 캐스케이딩(Octo) | 회의 서비스를 통째로 올릴 때 |
| <strong>Pion</strong> (라이브러리) | Go | MIT | SFU가 아니라 WebRTC 스택. `TrackLocalStaticRTP`로 RTP를 그대로 포워딩하는 단순 SFU를 직접 짤 수 있음 | 아주 특수한 라우팅 규칙이 필요할 때 |

선택할 때 볼 포인트를 정리한다.

- <strong>추상화 수준</strong>: mediasoup는 "미디어 라우팅 엔진"이고 방·사용자·권한은 전부 애플리케이션 몫이다. LiveKit은 반대로 거의 완성품이라 빨리 붙지만 내부 정책을 바꾸기 어렵다. 백엔드 팀이 시그널링 서버(03장)를 이미 갖고 있다면 mediasoup나 Janus가, 처음부터 만든다면 LiveKit이 출발이 빠르다.
- <strong>라이선스</strong>: Janus는 GPL-3.0이다. GPLv3에는 AGPL 같은 네트워크 조항이 없어 서버로 운영만 하는 것은 소스 공개 의무를 만들지 않지만, 수정한 Janus 바이너리를 장비에 넣어 <strong>배포</strong>하면 소스 공개 의무가 생긴다. 엣지 게이트웨이 장비에 SFU를 탑재하는 디바이스 회사라면 법무 검토가 필요하다.
- <strong>확장 모델</strong>: LiveKit 셀프 호스팅 문서는 Redis로 노드를 묶어도 "하나의 룸은 한 노드에 들어가야 한다"고 명시한다. 룸 하나의 참가자가 아주 많아질 서비스라면 4절의 캐스케이딩을 어떻게 지원하는지 먼저 확인한다.
- <strong>디바이스 입력 경로</strong>: 디바이스가 WebRTC 스택을 갖지 않아도 된다는 점이 중요하다. Janus Streaming 플러그인이나 mediasoup `PlainTransport`는 디바이스가 보내는 <strong>평문 RTP(또는 RTSP 소스)</strong>를 받아 브라우저에는 WebRTC로 내보낸다. 사설망·VPN 안의 카메라라면 디바이스는 GStreamer로 RTP만 쏘고, WebRTC의 복잡함은 서버가 떠안는 구성도 가능하다. 반대로 디바이스가 공인망 너머에 있다면 WHIP(14장)으로 SFU에 퍼블리시하는 것이 표준적인 방법이다.

## 4. 캐스케이딩 SFU

SFU 한 대에는 한계가 있다. 송신 스트림이 N(N-1)로 늘어 NIC 대역폭과 CPU가 먼저 찬다. 지리적 문제도 있다. 서울 리전 SFU에 붙은 농기계 영상을 미국 동부의 운영자가 보면, 운영자의 모든 패킷이 태평양을 건너고 NACK 재전송도 그만큼 느려진다. 여러 SFU를 서로 연결해 하나의 세션처럼 동작시키는 것을 <strong>캐스케이딩(cascading)</strong>이라고 한다.

![서울 리전에서는 농기계 카메라 A·B가 SFU-1로 송신하고 국내 운영자가 SFU-1에서 수신하며, SFU-1이 버지니아 리전 SFU-2로 스트림당 한 벌만 릴레이하고 SFU-2가 해외 운영자 세 명에게 나눠 주는 구조로, 반대 방향으로 PLI·RTCP 피드백이 흐르고 상단의 룸 배치 디렉터리(Redis 등)가 두 SFU의 배치를 관리하는 그림](/images/study-webrtc/12-cascading-light.png)
![서울 리전에서는 농기계 카메라 A·B가 SFU-1로 송신하고 국내 운영자가 SFU-1에서 수신하며, SFU-1이 버지니아 리전 SFU-2로 스트림당 한 벌만 릴레이하고 SFU-2가 해외 운영자 세 명에게 나눠 주는 구조로, 반대 방향으로 PLI·RTCP 피드백이 흐르고 상단의 룸 배치 디렉터리(Redis 등)가 두 SFU의 배치를 관리하는 그림](/images/study-webrtc/12-cascading-dark.png)

핵심은 <strong>원격 SFU당 스트림 한 벌</strong>이다. 버지니아에 운영자가 1명이든 30명이든 리전 간 링크에는 카메라 A의 스트림이 한 번만 지나가고, 복제는 SFU-2가 현지에서 한다. 각 클라이언트는 가장 가까운 SFU에 붙으므로 마지막 구간(last mile)의 RTT가 짧아지고 NACK·PLI 복구도 빨라진다.

구현 방식은 SFU마다 다르다.

- <strong>mediasoup</strong>: `router.pipeToRouter({ producerId, router })`가 같은 호스트의 다른 워커(Router)로 Producer를 이어 준다. 호스트 간에는 `createPipeTransport()`로 만든 PipeTransport 쌍을 애플리케이션이 직접 연결한다. CPU 코어 하나에 워커 하나라는 구조라 단일 호스트 안에서도 이 기능으로 큰 룸을 여러 코어에 나눈다.
- <strong>Jitsi Videobridge</strong>: Octo라는 이름으로 브리지 간 릴레이를 지원해 왔다.
- <strong>LiveKit(셀프 호스팅)</strong>: Redis 기반으로 노드를 묶어 룸을 분산 배치하지만, 공식 문서 기준 룸 하나는 한 노드에 있어야 한다. 즉 "룸 단위 수평 확장"이지 "룸 내부 캐스케이딩"은 아니다.

설계 시 따져야 할 것들이다.

| 항목 | 내용 |
|---|---|
| 배치 디렉터리 | 룸 ID → 각 리전의 SFU 노드 매핑을 어디에 둘지(Redis 등). 첫 참가자가 들어온 리전을 원점으로 삼을지, 송신자 위치를 우선할지 정책이 필요하다 |
| 계층 전달 정책 | 릴레이 링크로 Simulcast 전 계층을 보낼지, 원격 SFU가 실제 구독 중인 계층만 보낼지. 후자가 대역폭을 아끼지만 구독 변화가 원점까지 전파돼야 한다 |
| RTCP 피드백 | 원격 수신자의 PLI는 원격 SFU를 거쳐 원점 SFU, 송신자까지 올라가야 한다. 혼잡 제어(TWCC·REMB)는 홉별로 따로 돈다 — 원격 수신자 한 명의 나쁜 회선이 원점 송신자 비트레이트를 끌어내리지 않게 SFU마다 독립적으로 계층을 고른다 |
| 지연 | 홉마다 지터 버퍼는 없지만 큐잉·재전송 지연이 더해진다. 리전 간 링크 RTT 자체가 줄지는 않으며, 줄어드는 것은 last mile이다 |
| 장애 | 원격 SFU 장애 시 그 리전 클라이언트만 재연결하면 된다. 원점 SFU 장애는 송신자 재연결이 필요하다 |

농기계 플랫폼처럼 송신자(디바이스)가 국내에 몰려 있고 시청자가 소수라면 캐스케이딩은 대개 과설계다. 해외 지사·딜러가 실시간으로 장비를 지켜봐야 하는 요구가 생길 때 고려 대상이 된다.

## 5. 녹화 아키텍처

SFU는 녹화를 붙이기 좋은 자리다. 이미 SRTP를 복호화한 <strong>평문 RTP</strong>를 갖고 있으므로, 녹화기에 스트림 하나를 더 "구독"시키기만 하면 된다. 송신자(디바이스)는 녹화 여부와 무관하게 한 번만 올린다.

![송신자 카메라가 SRTP로 SFU에 보내고 SFU가 운영자 뷰어에게 SRTP로 전달하는 동시에 평문 RTP를 PlainTransport 등으로 포크해 녹화기로 보내며, 녹화기 안에서 지터 버퍼(rtpjitterbuffer) → depay·parse(rtph264depay) → 세그먼트 mux(splitmuxsink)를 거쳐 MP4/WebM 세그먼트가 오브젝트 스토리지로 올라가고, 녹화 시작 시 녹화기가 SFU를 거쳐 송신자에게 PLI로 키프레임을 요청하는 흐름](/images/study-webrtc/12-recording-light.png)
![송신자 카메라가 SRTP로 SFU에 보내고 SFU가 운영자 뷰어에게 SRTP로 전달하는 동시에 평문 RTP를 PlainTransport 등으로 포크해 녹화기로 보내며, 녹화기 안에서 지터 버퍼(rtpjitterbuffer) → depay·parse(rtph264depay) → 세그먼트 mux(splitmuxsink)를 거쳐 MP4/WebM 세그먼트가 오브젝트 스토리지로 올라가고, 녹화 시작 시 녹화기가 SFU를 거쳐 송신자에게 PLI로 키프레임을 요청하는 흐름](/images/study-webrtc/12-recording-dark.png)

녹화 방식은 두 갈래다.

| 방식 | 동작 | 장점 | 단점 |
|---|---|---|---|
| 트랙별(raw) 녹화 | 트랙마다 RTP를 포크해 역패킷화 후 컨테이너에 그대로 담음 (재인코딩 없음) | CPU 거의 안 씀, 원본 화질 | 트랙별 파일이라 합성·동기화는 후처리 몫 |
| 합성(composite) 녹화 | 헤드리스 브라우저가 룸에 참가해 화면을 녹화하거나 MCU처럼 서버에서 합성 | "사용자가 본 그대로", 단일 파일 | 디코드·합성·인코드 비용, 레이아웃 고정 |

디바이스 영상 플랫폼은 대부분 트랙별 녹화면 충분하다. 카메라 하나가 곧 트랙 하나이고, 증거 보관·사고 분석에는 원본 화질이 중요하기 때문이다. SFU별 지원은 다음과 같다. Janus는 Record&Play·VideoRoom이 RTP를 `.mjr` 파일로 떨어뜨리고 `janus-pp-rec`이 WebM/MP4 등으로 후처리한다. LiveKit은 별도 서비스인 Egress가 룸 합성·트랙 단위 녹화를 맡는다. mediasoup는 녹화 기능이 없으므로 `PlainTransport`로 RTP를 외부 프로세스(GStreamer·FFmpeg)에 넘긴다.

mediasoup에서 H.264 비디오 Producer를 GStreamer 녹화기로 포크하는 골격이다.

```javascript
// SFU(Node.js) — 녹화기로 평문 RTP를 내보내는 PlainTransport
const transport = await router.createPlainTransport({
  listenInfo: { protocol: 'udp', ip: '127.0.0.1' },
  rtcpMux: false,
  comedia: false,
});
await transport.connect({ ip: '127.0.0.1', port: 5004, rtcpPort: 5005 });

const consumer = await transport.consume({
  producerId: videoProducer.id,
  rtpCapabilities: router.rtpCapabilities, // 실제로는 녹화기가 받을 코덱만 남긴다
  paused: true,                            // 녹화기 준비 전에는 흘리지 않는다
});
// consumer.rtpParameters.codecs[0].payloadType 을 녹화기 caps의 payload와 맞춘다

// 녹화기 프로세스가 준비되면
await consumer.resume();
await consumer.requestKeyFrame(); // 첫 프레임을 키프레임으로
```

```bash
# 녹화기 — RTP 수신 → 10분 단위 MP4 세그먼트
gst-launch-1.0 -e \
  udpsrc port=5004 caps="application/x-rtp,media=video,encoding-name=H264,clock-rate=90000,payload=102" ! \
  rtpjitterbuffer latency=200 ! rtph264depay ! h264parse ! \
  splitmuxsink location=/var/rec/cam-a-%05d.mp4 max-size-time=600000000000
```

운영에서 자주 밟는 함정이다.

- <strong>첫 프레임은 키프레임이어야 한다.</strong> 녹화기가 중간에 붙으면 다음 키프레임까지 디코딩 불가능한 데이터만 쌓인다. 구독 시작 직후 PLI(`requestKeyFrame()`)를 보낸다. 디바이스 키프레임 간격이 길면(09장) 녹화 앞부분이 비는 이유가 된다.
- <strong>Simulcast 계층을 고정한다.</strong> 녹화용 Consumer가 대역폭 추정에 따라 계층을 오가면 파일 중간에 해상도가 바뀐다. 녹화 Consumer는 최상위 계층으로 고정한다.
- <strong>손실 복구가 없다.</strong> `PlainTransport` → `udpsrc` 경로에는 보통 NACK가 없다. 녹화기를 SFU와 같은 호스트·같은 네트워크에 두거나, 손실이 문제라면 녹화기도 WebRTC 클라이언트로 붙여 NACK·FEC를 받는다.
- <strong>A/V 동기화는 RTCP SR로 맞춘다.</strong> 오디오·비디오는 RTP 타임스탬프 기준(clock rate)이 다르다. 트랙별 파일을 나중에 합칠 때는 각 트랙의 RTCP Sender Report가 주는 NTP 시각 ↔ RTP 타임스탬프 대응(08장)을 기록해 두어야 정렬할 수 있다.
- <strong>크래시에 강한 컨테이너를 고른다.</strong> 일반 MP4는 끝에 `moov` 인덱스를 쓰므로 프로세스가 죽으면 파일 전체를 못 연다. 세그먼트를 짧게 자르거나(위 예시의 `splitmuxsink`), fragmented MP4·Matroska/WebM처럼 스트리밍에 강한 포맷을 쓴다. VP8/VP9 + Opus는 WebM, H.264는 MP4가 자연스럽다.
- <strong>업로드는 세그먼트 단위로 비동기로 한다.</strong> 닫힌 세그먼트만 오브젝트 스토리지에 올리고 로컬에서 지운다. 디스크가 차면 녹화기만이 아니라 SFU 호스트 전체가 위험하다.

AWS를 쓴다면 이 녹화 파이프라인을 관리형으로 대신하는 길이 있다. KVS WebRTC의 저장 세션(21장), Chime SDK 미디어 파이프라인(23장), IVS 녹화(24장)가 각각의 방식으로 이 역할을 한다.

## 6. E2EE와 SFU — Encoded Transform과 SFrame

### SFU는 평문을 본다

10장에서 본 DTLS-SRTP는 <strong>홉 단위(hop-by-hop)</strong> 암호화다. P2P에서는 홉이 하나라 곧 종단 간 암호화지만, SFU를 끼우면 홉이 둘로 나뉜다. 송신자 ↔ SFU, SFU ↔ 수신자가 각각 별도의 DTLS 세션이고, SFU는 그 사이에서 SRTP를 풀어 평문 RTP를 손에 쥔다. 1·5절에서 장점으로 쓴 바로 그 성질이 보안 관점에서는 약점이다. SFU 운영자, SFU가 도는 클라우드, 침해된 SFU 프로세스가 영상을 볼 수 있다. 농기계 작업 영상이면 큰 문제가 아닐 수 있지만, 사람 얼굴이 찍히는 매장 CCTV나 의료 원격 진료라면 이야기가 다르다.

해법은 암호화를 한 층 더 두는 것이다. <strong>인코딩된 프레임을 패킷화 전에 애플리케이션이 암호화</strong>하고, 수신 측은 역패킷화 후 디코딩 전에 복호화한다. 그러면 SFU는 SRTP를 풀어도 페이로드가 암호문이라 내용을 볼 수 없다. 대신 RTP 헤더와 헤더 확장(Dependency Descriptor, 오디오 레벨 등)은 평문으로 남으므로 SFU는 여전히 라우팅·계층 선택을 할 수 있다.

![송신 측에서 인코더 → Encoded Transform(SFrame 암호화) → RTP 패킷화 → SRTP 암호화(홉 키)를 거쳐 SFU로 가고, SFU는 SRTP를 복호·재암호화하면서 RTP 헤더·확장만 읽고 페이로드는 SFrame 암호문인 채로 수신 측에 넘기며, 수신 측은 SRTP 복호(홉 키) → 역패킷화 → Encoded Transform(SFrame 복호) → 디코더 순으로 처리하고, 두 Encoded Transform 단계는 SFU가 모르는 같은 E2E 키를 공유하는 그림](/images/study-webrtc/12-e2ee-light.png)
![송신 측에서 인코더 → Encoded Transform(SFrame 암호화) → RTP 패킷화 → SRTP 암호화(홉 키)를 거쳐 SFU로 가고, SFU는 SRTP를 복호·재암호화하면서 RTP 헤더·확장만 읽고 페이로드는 SFrame 암호문인 채로 수신 측에 넘기며, 수신 측은 SRTP 복호(홉 키) → 역패킷화 → Encoded Transform(SFrame 복호) → 디코더 순으로 처리하고, 두 Encoded Transform 단계는 SFU가 모르는 같은 E2E 키를 공유하는 그림](/images/study-webrtc/12-e2ee-dark.png)

### Insertable Streams에서 RTCRtpScriptTransform으로

브라우저가 "인코딩된 프레임"에 손댈 수 있게 해 주는 API는 두 세대가 있다.

| API | 형태 | 상태 |
|---|---|---|
| Insertable Streams (`createEncodedStreams()`) | `RTCPeerConnection({ encodedInsertableStreams: true })` 후 sender/receiver에서 Readable/Writable 스트림 쌍을 꺼내 메인 스레드나 워커로 넘김 | Chrome이 먼저 출시한 비표준 API |
| WebRTC Encoded Transform (`RTCRtpScriptTransform`) | 워커를 지정해 `sender.transform` / `receiver.transform`에 할당, 워커에서 `rtctransform` 이벤트로 스트림을 받음 | W3C 표준 트랙(Working Draft). MDN 기준 Safari 15.4·Firefox 117·Chrome 141부터 지원, Baseline 2025 |

새 코드는 `RTCRtpScriptTransform`으로 쓰고, 구형 Chrome 대응이 필요할 때만 `createEncodedStreams()`로 폴백한다. 메인 스레드 쪽 코드다.

```javascript
// main.js
const worker = new Worker('e2ee-worker.js');
worker.postMessage({ type: 'setKey', keyId: 1, rawKey }); // rawKey: 32바이트 ArrayBuffer

function attachSender(sender) {
  if ('RTCRtpScriptTransform' in window) {
    sender.transform = new RTCRtpScriptTransform(worker, { operation: 'encrypt' });
  } else {
    // 구형 Chrome: new RTCPeerConnection({ encodedInsertableStreams: true }) 필요
    const { readable, writable } = sender.createEncodedStreams();
    worker.postMessage({ type: 'legacy', operation: 'encrypt', readable, writable },
                       [readable, writable]);
  }
}

const sender = pc.addTrack(track, stream);
attachSender(sender); // addTrack 직후에 붙여야 첫 프레임부터 암호화된다

pc.ontrack = ({ receiver }) => {
  receiver.transform = new RTCRtpScriptTransform(worker, { operation: 'decrypt' });
};
```

워커는 프레임마다 AES-GCM으로 암호화한다. 아래는 원리를 보여 주는 단순화된 예다(실제 SFrame 헤더 형식이 아니다).

```javascript
// e2ee-worker.js — 단순화된 프레임 암호화 (개념 예시)
let key, keyId;
let counter = 0;

// VP8은 프레임 앞 몇 바이트를 평문으로 남긴다 (W3C webrtc/samples 관례)
const CLEAR_BYTES = { key: 10, delta: 3, undefined: 1 };

self.onmessage = async ({ data }) => {
  if (data.type === 'setKey') {
    keyId = data.keyId;
    key = await crypto.subtle.importKey('raw', data.rawKey, 'AES-GCM', false,
                                        ['encrypt', 'decrypt']);
  } else if (data.type === 'legacy') {
    pipe(data.operation, data.readable, data.writable);
  }
};

self.onrtctransform = ({ transformer }) => {
  pipe(transformer.options.operation, transformer.readable, transformer.writable);
};

function pipe(operation, readable, writable) {
  const fn = operation === 'encrypt' ? encrypt : decrypt;
  readable.pipeThrough(new TransformStream({ transform: fn })).pipeTo(writable);
}

async function encrypt(frame, controller) {
  const clear = CLEAR_BYTES[frame.type];
  const data = new Uint8Array(frame.data);
  const iv = new Uint8Array(12);
  // 프레임마다 고유 IV. 같은 키를 여러 송신자가 쓰면 IV가 겹치므로 송신자별 키(keyId)를 쓴다
  new DataView(iv.buffer).setUint32(8, counter++);
  const cipher = new Uint8Array(await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv, additionalData: data.subarray(0, clear) },
    key, data.subarray(clear)));
  // [평문 헤더][암호문+태그][IV 12바이트][keyId 1바이트]
  const out = new Uint8Array(clear + cipher.length + 13);
  out.set(data.subarray(0, clear), 0);
  out.set(cipher, clear);
  out.set(iv, clear + cipher.length);
  out[out.length - 1] = keyId;
  frame.data = out.buffer;
  controller.enqueue(frame);
}

async function decrypt(frame, controller) {
  const clear = CLEAR_BYTES[frame.type];
  const data = new Uint8Array(frame.data);
  const iv = data.subarray(data.length - 13, data.length - 1);
  // 실제로는 마지막 바이트(keyId)로 송신자별 키를 골라야 한다. 예시는 키 하나만 쓴다
  try {
    const plain = new Uint8Array(await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv, additionalData: data.subarray(0, clear) },
      key, data.subarray(clear, data.length - 13)));
    const out = new Uint8Array(clear + plain.length);
    out.set(data.subarray(0, clear), 0);
    out.set(plain, clear);
    frame.data = out.buffer;
    controller.enqueue(frame);
  } catch {
    // 키 불일치·손상 프레임은 버린다 (디코더에 쓰레기를 넣지 않는다)
  }
}
```

몇 가지 설계 포인트가 있다.

- <strong>앞부분을 평문으로 남기는 이유</strong>: W3C 샘플 코드는 VP8 키프레임 10바이트·델타 3바이트, Opus TOC 1바이트를 암호화하지 않는다. 주석이 밝히는 이유는 "중간 장치가 키프레임 여부나 Opus 모드를 판단할 수 있게" 하고, 복호화 실패 시 디코더가 즉시 치명적 오류를 내지 않게 하려는 것이다. 이 평문 영역은 AAD로 넣어 위변조는 막는다.
- <strong>코덱별 처리가 필요하다</strong>: 패킷화기가 프레임 내부 구조를 해석하는 코덱(H.264는 NAL 경계를 start code로 찾는다)은 암호문이 그 구조를 깨뜨리지 않도록 암호화 범위를 조정해야 한다. 코덱마다 다르게 처리해야 하므로 E2EE를 쓰는 서비스는 보통 VP8/VP9/AV1로 코덱을 좁힌다.
- <strong>송신자마다 다른 키</strong>: AES-GCM은 같은 키로 nonce(IV)를 재사용하면 기밀성이 무너진다. 참가자 여럿이 한 키를 공유하면 각자 0부터 센 카운터가 겹치므로, 송신자마다 별도 키를 두고 프레임에 키 ID를 실어 수신자가 고르게 한다. SFrame의 KID가 바로 이 역할이다.
- <strong>키 교체와 키프레임</strong>: 참가자가 나가면 그 사람이 앞으로의 영상을 못 보도록 키를 바꿔야 한다. 새 키로 바꾼 직후에는 `RTCRtpScriptTransformer.generateKeyFrame()`으로 송신 측 키프레임을 만들고, 수신 측은 `sendKeyFrameRequest()`로 키프레임을 요청할 수 있다.

### SFrame — 프레임 암호화의 표준 형식

위 예시처럼 서비스마다 제각각 프레임 포맷을 정하면 상호운용이 안 된다. 이를 표준화한 것이 <strong>SFrame(Secure Frame)</strong>, RFC 9605(2024년 8월, Standards Track)이다.

- <strong>구조</strong>: SFrame 헤더 + 암호문 + 인증 태그. 헤더는 설정 바이트 하나에 작은 <strong>KID(Key ID)</strong>와 <strong>CTR(카운터)</strong>를 직접 담고, 값이 크면 뒤에 가변 길이로 붙인다. 헤더 전체가 AAD로 인증된다.
- <strong>키 유도</strong>: 기본 키(base key)에서 HKDF로 KID별 암호화 키와 salt를 뽑고, nonce는 salt XOR CTR로 만든다. 프레임마다 CTR이 증가하므로 IV를 따로 실어 보낼 필요가 없다.
- <strong>암호 스위트</strong>: AES-128-CTR + HMAC-SHA256(태그 80/64/32비트), AES-128-GCM-SHA256, AES-256-GCM-SHA512.
- <strong>적용 단위</strong>: RFC는 프레임 단위·패킷 단위 적용을 모두 일반론으로 다루며 RTP와 독립적으로 정의된다. WebRTC에서는 Encoded Transform과 맞물리는 <strong>프레임 단위</strong>가 자연스럽다.
- <strong>키 관리는 범위 밖</strong>: SFrame은 "받은 키로 어떻게 암호화하는가"만 정한다. 참가자 간 키 합의·교체는 별도 프로토콜이 맡으며, 그룹 키 합의 표준인 <strong>MLS(Messaging Layer Security, RFC 9420)</strong>와 짝짓는 것이 대표적인 구성이다. 작은 서비스라면 인증된 시그널링 채널로 키를 배포하되, 그 경우 시그널링 서버가 키를 볼 수 있다는 한계를 인정해야 한다(10장의 "시그널링 무결성이 곧 보안" 원칙과 같은 구조다).

Encoded Transform 명세 초안에는 브라우저가 SFrame을 직접 처리하는 `RTCRtpSFrameEncryptor`·`RTCRtpSFrameDecryptor`와 `RTCRtpScriptTransform`의 `"sframe"` 옵션도 정의돼 있다. 아직 Working Draft라 실전에서는 워커에서 SFrame을 직접 구현하거나 SFrame 라이브러리를 쓰는 경우가 많다.

### E2EE의 대가

E2EE를 켜는 순간 SFU가 할 수 있던 서버 측 기능이 대부분 사라진다.

| 기능 | E2EE 적용 시 |
|---|---|
| 라우팅·Simulcast 계층 선택 | 가능 (RTP 헤더·확장은 평문) |
| 서버 녹화 | 암호문만 저장됨. 키를 가진 "녹화 참가자"를 따로 두어야 함 |
| MCU 합성·서버 트랜스코딩 | 불가 |
| 실시간 AI 분석(객체 인식 등)·자막 | 불가 (클라이언트에서 해야 함) |
| SIP/전화망 게이트웨이 | 불가 |
| 메타데이터 보호 | 안 됨. 누가 말하는지(오디오 레벨), 프레임 크기·타이밍은 SFU가 본다 |

디바이스 플랫폼에서는 이 표가 결정을 대신해 준다. 서버 측 녹화와 AI 분석이 핵심 가치라면 E2EE 대신 SFU 자체를 신뢰 경계 안에 두는(자체 VPC 운영, 접근 통제·감사) 편이 맞다. 디바이스 측에서 E2EE를 하려면 디바이스 WebRTC 스택이 프레임 변환 훅을 제공해야 하는데, libwebrtc는 네이티브 프레임 트랜스포머 인터페이스를 갖고 있지만 다른 스택에서는 패킷화 이전 단계에 직접 끼워 넣어야 한다. 디바이스 스택 선택은 [13장](/study/webrtc/13-native-webrtc)에서 다룬다.

::: tip 핵심 정리
- Mesh는 피어당 업·다운 N-1로 3~4명이 한계이고, SFU는 업 1·다운 N-1로 서버가 디코드 없이 패킷만 고른다. MCU는 업 1·다운 1이지만 서버가 디코드·합성·재인코드를 떠안는다.
- "카메라 1대 → 운영자 M명"에서 P2P는 디바이스 업링크가 M배가 된다. 뷰어·녹화·분석 소비자가 늘수록 SFU로 업링크를 1로 고정하는 편이 유리하다.
- Simulcast는 `rid`별 독립 인코딩(계층 전환에 키프레임 필요), SVC는 `scalabilityMode`(`L1T3`, `L3T3_KEY` 등)로 계층 스트림 하나를 보낸다. 공간 SVC는 VP9·AV1 전용이고, HW H.264 디바이스는 다중 인코더 Simulcast가 현실적이다.
- 오픈소스 SFU는 저수준 라이브러리(mediasoup, ISC)부터 일체형(LiveKit, Apache-2.0)까지 스펙트럼이 넓고, Janus(GPL-3.0)는 배포 시 라이선스를 검토해야 한다.
- 캐스케이딩은 원격 SFU당 스트림 한 벌만 넘겨 last mile을 줄이고, 녹화는 SFU에서 평문 RTP를 포크해 키프레임부터 세그먼트 컨테이너로 저장한다.
- SFU는 홉 단위 DTLS-SRTP 때문에 평문을 본다. E2EE는 Encoded Transform(`RTCRtpScriptTransform`)으로 프레임을 패킷화 전에 암호화하고, 형식은 SFrame(RFC 9605), 키 관리는 MLS 등 별도 프로토콜이 맡는다. 대가로 서버 녹화·합성·분석을 잃는다.
:::

## 다음 챕터

[브라우저 밖 WebRTC: 디바이스 구현](/study/webrtc/13-native-webrtc)에서는 브라우저가 대신해 주던 캡처·인코딩·패킷화를 디바이스에서 직접 조립한다. libwebrtc·Pion·GStreamer webrtcbin·aiortc·KVS C SDK를 비교하고, Jetson·Raspberry Pi 하드웨어 인코더 파이프라인과 임베디드 배포 체크리스트를 다룬다.
