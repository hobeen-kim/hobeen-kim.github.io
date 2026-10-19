---
title: "모니터링과 디버깅"
description: "getStats() 리포트 구조와 핵심 지표, 누적 카운터를 초당 값으로 바꾸는 수집 코드, chrome://webrtc-internals·about:webrtc 덤프 읽기, 증상별 장애 원인과 확인 방법, TURN·SFU 서버 측 관측까지 WebRTC 운영 가시성을 정리한다."
date: 2026-10-19
tags: [WebRTC, getStats, Debugging, Monitoring, Observability]
prev: /study/webrtc/14-whip-whep
next: /study/webrtc/16-aws-landscape
---

# 모니터링과 디버깅

::: info 학습 목표
- `getStats()` 리포트의 타입과 객체 사이의 id 참조 관계를 이해한다.
- candidate-pair·inbound-rtp·outbound-rtp·remote-inbound-rtp 핵심 지표의 의미와 단위, 누적값과 순간값의 차이를 안다.
- 통계를 주기적으로 수집해 누적 카운터를 초당 값으로 바꾸고 서버로 요약해 보내는 코드를 작성한다.
- `chrome://webrtc-internals` 덤프와 `about:webrtc`로 문제 구간을 좁힌다.
- 흔한 장애를 "증상 → 원인 → 확인 방법"으로 진단하고, TURN·SFU 서버 측 지표를 Prometheus/Grafana로 관측한다.
:::

## 1. getStats() 리포트 구조

WebRTC는 "연결이 됐다/안 됐다" 이상의 정보를 이벤트로 알려 주지 않는다. 화면이 왜 멈췄는지, 왜 흐려졌는지는 통계를 읽어야 안다. 그 창구가 `RTCPeerConnection.getStats()`다.

```js
const report = await pc.getStats();          // RTCStatsReport (maplike: id -> stats)
for (const stats of report.values()) {
  console.log(stats.type, stats.id, stats.timestamp);
}
const videoOnly = await pc.getStats(videoTrack);   // only objects related to this track
const senderStats = await pc.getSenders()[0].getStats();
```

`RTCStatsReport`는 id를 키로 통계 객체를 담은 Map 비슷한 구조다. 모든 객체에는 `id`, `type`, `timestamp`(밀리초, `performance.now()`와 같은 계열의 시각)가 있다. W3C `webrtc-stats` 명세가 정한 타입은 14개다.

| type | 담는 것 | 주로 보는 상황 |
|---|---|---|
| `candidate-pair` | ICE 후보 쌍 하나의 상태·RTT·대역폭 추정 | 연결 경로, 네트워크 RTT |
| `local-candidate` / `remote-candidate` | 후보 주소·종류(host/srflx/prflx/relay)·릴레이 프로토콜 | TURN 경유 여부 |
| `transport` | DTLS·ICE 전송 상태, 선택된 후보 쌍 id | 연결 단계 판정 |
| `inbound-rtp` | 내가 받는 RTP 스트림(SSRC 단위) | 수신 품질·프리즈 |
| `outbound-rtp` | 내가 보내는 RTP 스트림(SSRC 단위, simulcast면 레이어마다) | 송신 품질·인코더 제한 |
| `remote-inbound-rtp` | 상대가 RTCP RR로 알려 준 "내 송신 스트림의 수신 상태" | 상대 쪽 손실·RTT |
| `remote-outbound-rtp` | 상대가 RTCP SR로 알려 준 상대 송신 정보 | 수신 스트림의 원격 시각 |
| `media-source` | 캡처 원본(카메라·마이크) 정보 | 마이크 레벨, 캡처 해상도 |
| `media-playout` | 오디오 재생 경로 통계 | 오디오 재생 지연·합성 샘플 |
| `codec` | 협상된 코덱(mimeType·payloadType·fmtp) | 코덱 불일치 |
| `data-channel` | DataChannel별 메시지·바이트 수 | 제어 채널 트래픽 |
| `peer-connection` | DataChannel 개수 등 PC 전체 정보 | 거의 안 봄 |
| `certificate` | DTLS 인증서 fingerprint | 인증서 확인 |

예전 블로그 코드에 나오는 `track`, `stream` 같은 타입은 표준에서 빠졌다. 최신 크롬에서는 나오지 않으므로 해당 코드는 조용히 아무것도 못 찾는다.

통계 객체는 서로 id로 연결된 그래프다. 하나만 봐서는 답이 안 나오고, 참조를 따라가야 한다.

![getStats 리포트의 객체 관계 — transport의 selectedCandidatePairId가 candidate-pair를, candidate-pair의 localCandidateId와 remoteCandidateId가 local-candidate와 remote-candidate를 가리키고, outbound-rtp는 mediaSourceId로 media-source를 가리키며 remoteId/localId로 remote-inbound-rtp와 서로 연결되고, inbound-rtp는 codecId로 codec을 가리키며 remoteId/localId로 remote-outbound-rtp와 연결되는 구조](/images/study-webrtc/15-stats-graph-light.png)
![getStats 리포트의 객체 관계 — transport의 selectedCandidatePairId가 candidate-pair를, candidate-pair의 localCandidateId와 remoteCandidateId가 local-candidate와 remote-candidate를 가리키고, outbound-rtp는 mediaSourceId로 media-source를 가리키며 remoteId/localId로 remote-inbound-rtp와 서로 연결되고, inbound-rtp는 codecId로 codec을 가리키며 remoteId/localId로 remote-outbound-rtp와 연결되는 구조](/images/study-webrtc/15-stats-graph-dark.png)

- "지금 TURN을 타고 있나?"는 `transport.selectedCandidatePairId` → `candidate-pair.localCandidateId` → `local-candidate.candidateType === 'relay'` 순서로 따라가야 답이 나온다.
- 모든 RTP 통계는 `codecId`(그림에서는 inbound만 표시)와 `transportId`도 가진다.
- `remote-*` 객체는 상대가 보낸 RTCP에서 만들어진다. 그래서 RTCP가 한 번도 오지 않았으면 존재하지 않는다. 예를 들어 `remote-inbound-rtp.roundTripTime`은 DLSR이 0이 아닌 RR을 받기 전까지 없다.

마지막으로 꼭 구분해야 할 것이 <strong>누적값과 순간값</strong>이다.

| 종류 | 예 | 다루는 법 |
|---|---|---|
| 누적 카운터(객체 생성 후 계속 증가) | `bytesSent`, `packetsLost`, `framesDecoded`, `framesDropped`, `nackCount`, `pliCount`, `freezeCount`, `jitterBufferDelay`, `retransmittedPacketsSent` | 두 시점의 차이를 시간으로 나눠야 의미가 생긴다 |
| 순간값·최근 추정치 | `jitter`, `currentRoundTripTime`, `availableOutgoingBitrate`, `framesPerSecond`, `qualityLimitationReason`, `roundTripTime`, `fractionLost` | 읽은 값을 그대로 쓴다 |

통화 30분째에 `packetsLost`가 1200이라는 것은 아무것도 말해 주지 않는다. 최근 2초 동안 몇 개를 잃었는지가 중요하다. 이 변환은 3절에서 코드로 다룬다.

## 2. 핵심 지표

수백 개 필드 중 운영에서 실제로 보는 것은 많지 않다. 타입별로 정리한다. 단위는 명세 기준이다.

### candidate-pair — 연결 경로

| 지표 | 단위 | 의미 | 주의 |
|---|---|---|---|
| `state` | 열거형 | 이 쌍의 ICE 체크리스트 상태: `frozen` / `waiting` / `in-progress` / `failed` / `succeeded` | PC 연결 상태가 아니라 쌍 하나의 상태다. 쌍이 여러 개라 일부가 `failed`여도 정상일 수 있다 |
| `nominated` | boolean | ICE nomination 플래그가 선 쌍 | 실제 사용 중인 쌍은 `transport.selectedCandidatePairId`로 확인하는 것이 정확하다 |
| `currentRoundTripTime` | 초 | 가장 최근 STUN 확인(consent 확인 포함)으로 잰 RTT | TURN 경유라면 TURN 서버를 거친 왕복이다. 네트워크 경로 자체의 RTT로 읽는다 |
| `availableOutgoingBitrate` | bps | 송신 측 혼잡 제어가 계산한 사용 가능 대역폭(1초 창) | 혼잡 제어가 송신 추정을 할 때만 존재한다. 수신 전용 뷰어에서는 보통 없다 |
| `bytesSent` / `bytesReceived` | 바이트(누적) | 이 경로로 오간 총량 | 경로 전환 시 새 쌍으로 카운트가 옮겨 간다 |
| `responsesReceived` | 개(누적) | STUN 확인 응답 수 | 증가가 멈추면 consent가 끊기는 중이다 |

`local-candidate`에서는 `candidateType`(host/srflx/prflx/relay)과 `relayProtocol`(udp/tcp/tls, 로컬 relay 후보에만 존재), `url`(어느 STUN/TURN 서버에서 얻은 후보인지)을 본다.

### inbound-rtp — 받는 쪽 품질

| 지표 | 단위 | 의미 | 주의 |
|---|---|---|---|
| `jitter` | 초 | RFC 3550 도착 간격 지터 추정치 | 순간값. 오디오·비디오 모두 있음 |
| `packetsLost` | 개(누적) | 잃은 패킷 수 | RFC 3550 계산상 중복 패킷 때문에 음수가 될 수 있다 |
| `framesDropped` | 개(누적) | 디코딩 전에 버리거나 표시 시점을 놓친 프레임 | 디코더 과부하·지터 버퍼 문제 신호 |
| `framesPerSecond` | fps | 최근 1초 동안 디코딩한 프레임 수 | 비디오 전용 |
| `jitterBufferDelay` / `jitterBufferEmittedCount` | 초(누적 합) / 개(누적) | 지터 버퍼에 머문 시간의 합과 내보낸 프레임(샘플) 수 | 나눠야 평균 지연이 된다. 지연 예산([09장](/study/webrtc/09-quality-latency))의 수신 측 항목 |
| `freezeCount` / `totalFreezesDuration` | 개 / 초(누적) | 프리즈 횟수와 총 시간 | 명세 정의: 프레임 간격이 max(3 × 평균 프레임 간격, 평균 + 150ms) 이상. 평균은 최근 30프레임 기준 |

이 밖에 `framesDecoded`, `keyFramesDecoded`, 수신자가 보낸 `nackCount`·`pliCount`, 오디오의 `concealedSamples`(손실을 메우려고 합성한 샘플 수)도 자주 쓴다.

### outbound-rtp — 보내는 쪽 품질

| 지표 | 단위 | 의미 | 주의 |
|---|---|---|---|
| `qualityLimitationReason` | 열거형 | 지금 해상도·프레임을 깎는 이유: `none` / `cpu` / `bandwidth` / `other` | 디바이스 송출 진단의 출발점. `qualityLimitationDurations`로 이유별 누적 시간도 있다 |
| `retransmittedPacketsSent` | 개(누적) | RTX로 재전송한 패킷 수 | `packetsSent`의 부분집합. 비율로 본다 |
| `nackCount` | 개(누적) | 이 송신자가 받은 NACK 수 | 상대 쪽 손실의 간접 지표 |
| `pliCount` | 개(누적) | 이 송신자가 받은 PLI 수 | 비디오 전용. 급증하면 수신 측이 계속 깨진 화면을 보고 있다는 뜻이다 |
| `targetBitrate`, `frameWidth`/`frameHeight`, `framesPerSecond` | bps, px, fps | 인코더 목표와 실제 출력 | 혼잡 제어가 화질을 어떻게 깎는지 보인다 |

simulcast로 보내면 레이어마다 `outbound-rtp`가 따로 생기고 `rid`로 구분된다.

### remote-inbound-rtp — 상대가 본 내 스트림

| 지표 | 단위 | 의미 | 주의 |
|---|---|---|---|
| `roundTripTime` | 초 | RTCP RR(LSR·DLSR)로 계산한 RTT | RR을 받기 전에는 없다 |
| `fractionLost` | 0~1 | 직전 RR 구간의 손실 비율(RFC 3550 §6.4.1) | 누적이 아니라 구간 값이다 |
| `packetsLost`, `jitter` | 개, 초 | 상대가 보고한 손실·지터 | |

::: warning SFU를 거치면 remote-inbound-rtp는 SFU까지만 본다
P2P에서는 RR을 보내는 쪽이 실제 시청자다. 하지만 SFU는 RTP·RTCP를 종단한다. 농기계가 SFU로 송출하면 디바이스의 `remote-inbound-rtp`는 "디바이스 → SFU" 구간의 손실·RTT만 보여 준다. 시청자의 품질은 시청자 브라우저의 `inbound-rtp`나 SFU의 구독자별 통계에서 봐야 한다([12장](/study/webrtc/12-topology-sfu)).
:::

### 경험적 출발점

명세에는 "좋다/나쁘다" 기준이 없다. 아래는 원격 영상·제어 서비스에서 출발점으로 쓸 만한 경험적 값이다. 서비스마다 기준선을 재서 조정해야 한다.

| 지표 | 양호 | 주의 | 나쁨 |
|---|---|---|---|
| RTT(`currentRoundTripTime`) | 150ms 미만 | 150~300ms | 300ms 초과(원격 조작이 어려움) |
| 손실률(구간) | 1% 미만 | 1~3%(NACK·FEC로 버팀) | 5% 초과 |
| 오디오 `jitter` | 30ms 미만 | 30~50ms | 50ms 초과 |
| 프리즈 | 0 | 분당 1회 이상 | 지속적 증가 |
| `qualityLimitationReason` | `none` | 일시적 `bandwidth` | 수십 초 이상 `bandwidth`/`cpu` |

## 3. 주기 수집과 델타 계산

지표를 쓸모 있게 만드는 핵심은 <strong>두 시점의 차이</strong>다. 아래 모듈은 `getStats()`를 주기적으로 호출해 이전 샘플과 비교하고, 누적 카운터를 초당 값·구간 비율로 바꾼다.

```js
// stats-monitor.js — poll getStats() and turn cumulative counters into per-interval values
export function startStatsMonitor(pc, { intervalMs = 2000, onSample }) {
  let prev = new Map();
  const timer = setInterval(async () => {
    if (pc.connectionState === 'closed') return clearInterval(timer);
    const report = await pc.getStats();
    onSample(summarize(report, prev));
    prev = new Map(report); // keep this sample for the next delta
  }, intervalMs);
  return () => clearInterval(timer);
}

// Difference of a cumulative counter; null on first sample or counter reset
function delta(cur, prev, key) {
  if (!prev || cur[key] == null || prev[key] == null) return null;
  const dv = cur[key] - prev[key];
  return dv >= 0 ? dv : null;
}

// Per-second rate using the stats' own timestamps (ms), not wall-clock timers
function rate(cur, prev, key) {
  const dv = delta(cur, prev, key);
  const dt = prev ? (cur.timestamp - prev.timestamp) / 1000 : 0;
  return dv != null && dt > 0 ? dv / dt : null;
}

const kbps = (cur, prev, key) => {
  const r = rate(cur, prev, key);
  return r != null ? (r * 8) / 1000 : null;
};
const ms = (sec) => (sec != null ? sec * 1000 : null);

function selectedPair(report) {
  for (const s of report.values()) {
    if (s.type === 'transport' && s.selectedCandidatePairId) {
      return report.get(s.selectedCandidatePairId);
    }
  }
  // Fallback for browsers without transport stats (Firefox exposes a non-standard `selected`)
  for (const s of report.values()) {
    if (s.type === 'candidate-pair' && (s.selected || (s.nominated && s.state === 'succeeded'))) {
      return s;
    }
  }
  return null;
}

function summarize(report, prev) {
  const out = { ts: Date.now(), path: null, inbound: [], outbound: [] };

  const pair = selectedPair(report);
  if (pair) {
    const local = report.get(pair.localCandidateId);
    out.path = {
      rttMs: ms(pair.currentRoundTripTime),
      availableOutKbps: pair.availableOutgoingBitrate != null
        ? pair.availableOutgoingBitrate / 1000 : null,
      localType: local?.candidateType ?? null,        // host | srflx | prflx | relay
      relayProtocol: local?.relayProtocol ?? null,    // udp | tcp | tls (relay only)
    };
  }

  for (const s of report.values()) {
    const p = prev.get(s.id); // same object id across samples; new SSRC => new id

    if (s.type === 'inbound-rtp' && s.kind === 'video') {
      const lost = delta(s, p, 'packetsLost');
      const recv = delta(s, p, 'packetsReceived');
      const emitted = delta(s, p, 'jitterBufferEmittedCount');
      const jbDelay = delta(s, p, 'jitterBufferDelay');
      out.inbound.push({
        id: s.id,
        kbps: kbps(s, p, 'bytesReceived'),
        fps: s.framesPerSecond ?? rate(s, p, 'framesDecoded'),
        lossPct: lost != null && recv != null && lost + recv > 0
          ? (lost / (lost + recv)) * 100 : null,
        jitterMs: ms(s.jitter),
        jitterBufferMs: emitted ? ms(jbDelay / emitted) : null,
        droppedPerSec: rate(s, p, 'framesDropped'),
        newFreezes: delta(s, p, 'freezeCount'),
        nackSentPerSec: rate(s, p, 'nackCount'),
        pliSentPerSec: rate(s, p, 'pliCount'),
      });
    }

    if (s.type === 'outbound-rtp' && s.kind === 'video') {
      const sent = delta(s, p, 'packetsSent');
      const rtx = delta(s, p, 'retransmittedPacketsSent');
      const remote = s.remoteId ? report.get(s.remoteId) : null;
      out.outbound.push({
        id: s.id,
        rid: s.rid ?? null,                                // simulcast layer
        kbps: kbps(s, p, 'bytesSent'),
        fps: s.framesPerSecond ?? null,
        resolution: s.frameWidth ? `${s.frameWidth}x${s.frameHeight}` : null,
        limitation: s.qualityLimitationReason ?? null,     // none | cpu | bandwidth | other
        rtxPct: sent ? ((rtx ?? 0) / sent) * 100 : null,
        nackRecvPerSec: rate(s, p, 'nackCount'),
        pliRecvPerSec: rate(s, p, 'pliCount'),
        remoteRttMs: ms(remote?.roundTripTime),
        remoteLossPct: remote?.fractionLost != null ? remote.fractionLost * 100 : null,
      });
    }
  }
  return out;
}
```

설계상 짚을 점은 다음과 같다.

- <strong>시간은 통계 객체의 `timestamp`로 잰다.</strong> 백그라운드 탭에서는 `setInterval`이 느려지고, `getStats()` 응답 시각도 들쭉날쭉하다. 타이머 주기로 나누면 비트레이트가 출렁인다.
- <strong>카운터 리셋을 견딘다.</strong> SSRC가 바뀌면(재협상 등) 새 id의 객체가 생기므로 첫 샘플은 `prev`가 없어 `null`이 된다. 차이가 음수인 경우(예: `packetsLost`가 중복 패킷으로 줄어든 경우)도 `null`로 버린다. 0으로 채우면 대시보드에 가짜 급락이 생긴다.
- <strong>구간 손실률은 `lost / (lost + received)`다.</strong> `packetsLost / packetsReceived`처럼 누적값끼리 나누면 통화 초반의 손실이 끝까지 희석돼서 지금의 상태를 못 보여 준다.
- <strong>주기는 화면용 1~2초, 업로드용 10초 정도가 무난하다.</strong> `getStats()`도 내부 스레드를 거쳐 값을 모으는 비용이 있으므로 수백 ms 단위로 부르지 않는다.

### 서버로 보내기

2초 샘플을 그대로 서버로 보내면 세션 수 × 0.5회/초의 요청이 생긴다. 클라이언트에서 10초 단위로 요약하고, 세션을 식별하는 키를 붙여 보낸다.

```js
// stats-uploader.js — aggregate 2s samples into a 10s summary with a correlation key
import { startStatsMonitor } from './stats-monitor.js';

export function reportStats(pc, { sessionId, deviceId, endpoint = '/api/webrtc-stats' }) {
  let samples = [];
  const stopMonitor = startStatsMonitor(pc, { onSample: (s) => samples.push(s) });

  const flush = () => {
    if (!samples.length) return;
    const batch = samples;
    samples = [];
    const v = batch.flatMap((s) => s.inbound);
    const vals = (k) => v.map((x) => x[k]).filter((x) => x != null);
    const avg = (a) => (a.length ? a.reduce((x, y) => x + y, 0) / a.length : null);
    const body = JSON.stringify({
      sessionId,
      deviceId,
      ts: Date.now(),
      path: batch.at(-1).path,                  // localType tells relay vs direct
      kbpsAvg: avg(vals('kbps')),
      fpsMin: vals('fps').length ? Math.min(...vals('fps')) : null,
      lossPctMax: vals('lossPct').length ? Math.max(...vals('lossPct')) : null,
      jitterBufferMsAvg: avg(vals('jitterBufferMs')),
      freezes: vals('newFreezes').reduce((x, y) => x + y, 0),
    });
    navigator.sendBeacon(endpoint, body);
  };

  const timer = setInterval(flush, 10_000);
  window.addEventListener('pagehide', flush);
  return () => { clearInterval(timer); stopMonitor(); flush(); };
}
```

`sendBeacon`은 페이지가 닫히는 순간에도 전송을 보장받기 쉬워서 마지막 요약을 잃지 않는다. `sessionId`는 시그널링 서버나 WHIP 엔드포인트([14장](/study/webrtc/14-whip-whep))가 세션을 열 때 발급한 값을 쓴다. 이 키가 6절에서 서버 로그와 클라이언트 통계를 잇는 고리가 된다.

디바이스 쪽도 같은 지표를 얻을 수 있다. Pion은 `PeerConnection.GetStats()`로 W3C와 같은 계열의 타입을 돌려주고, GStreamer `webrtcbin`은 `get-stats` 액션 시그널로 통계를 `GstStructure`로 준다([13장](/study/webrtc/13-native-webrtc)). 디바이스가 이 요약을 MQTT나 HTTPS로 올리면 송신 측과 수신 측을 같은 세션 키로 나란히 볼 수 있다.

## 4. chrome://webrtc-internals와 about:webrtc

직접 수집 코드가 없거나 현장에서 바로 원인을 봐야 할 때는 브라우저 내장 도구를 쓴다.

### chrome://webrtc-internals

크롬(및 크로미움 계열) 주소창에 `chrome://webrtc-internals`를 치면 브라우저 안의 모든 PeerConnection을 보여 준다. <strong>통화를 시작하기 전에 새 탭으로 열어 둔다.</strong> 열기 전의 이벤트는 기록에서 빠질 수 있다.

화면 구성은 다음과 같다.

- <strong>getUserMedia 요청 탭</strong>: 어떤 제약 조건으로 카메라·마이크를 요청했는지.
- <strong>PeerConnection별 탭</strong>(페이지 URL과 id로 구분):
  - `RTCConfiguration`: `iceServers`(TURN이 들어 있는지), `iceTransportPolicy`, `bundlePolicy` 등 생성 옵션.
  - 이벤트 로그: `createOffer`, `setLocalDescription`, `setRemoteDescription`, `icecandidate`, `addIceCandidate`, `iceconnectionstatechange`, `connectionstatechange`, `icecandidateerror` 같은 API 호출과 이벤트가 시각과 함께 나열된다. SDP 원문도 여기서 볼 수 있다.
  - 통계 표와 그래프: 1절의 통계 객체가 표로, 숫자 필드는 시계열 그래프로 나온다. 초당 비트처럼 도구가 계산한 파생 값은 대괄호로 묶어 표시한다. 최근 버전에는 후보 쌍을 한눈에 보는 표도 있다.
- <strong>덤프</strong>: 페이지 상단의 "Create a WebRTC-Internals dump" 영역을 펼쳐 다운로드하면 지금까지의 이벤트와 통계 시계열이 JSON 텍스트 파일(`webrtc_internals_dump.txt`)로 저장된다. 버튼 문구는 크롬 버전마다 조금 다르다. 같은 영역에는 대역폭 추정 내부까지 분석할 때 쓰는 진단용 이벤트 로그 기록 옵션도 있다.

현장 운영자에게 "문제가 생기면 이 탭을 열어 둔 채로 재현하고 덤프를 보내 달라"고 요청하는 것이 가장 싼 원격 진단이다. 단, 덤프에는 로컬·공인 IP 주소와 SDP 전문이 들어 있으므로 개인정보처럼 취급한다.

### 덤프 구조와 읽는 순서

덤프는 대략 다음 구조다(크롬 버전에 따라 필드가 조금 다르다).

```json
{
  "getUserMedia": [ { "origin": "https://console.example.com", "video": "...", "audio": "..." } ],
  "PeerConnections": {
    "21456-1": {
      "url": "https://console.example.com/machines/tractor-042",
      "rtcConfiguration": "{ iceServers: [turn:turn.example.com:443?transport=tcp], iceTransportPolicy: all, ... }",
      "updateLog": [
        { "time": "2026. 10. 19. 오전 9:12:03", "type": "setRemoteDescription", "value": "type: offer, sdp: v=0 ..." },
        { "time": "2026. 10. 19. 오전 9:12:04", "type": "iceconnectionstatechange", "value": "checking" }
      ],
      "stats": {
        "IT01V1234567890-jitter": {
          "statsType": "inbound-rtp",
          "startTime": "2026-10-19T00:12:04.512Z",
          "endTime": "2026-10-19T00:14:10.512Z",
          "values": "[0.004,0.005,0.031,0.087]"
        }
      }
    }
  },
  "UserAgent": "Mozilla/5.0 ..."
}
```

`stats`의 키는 "통계 객체 id-필드 이름"이고, `values`는 JSON 배열을 문자열로 담고 있다. 시각화는 오픈소스 [webrtc-dump-importer](https://fippo.github.io/webrtc-dump-importer/)에 파일을 올리면 그래프로 볼 수 있다. 여러 덤프를 반복해서 봐야 한다면 간단한 스크립트로 필요한 것만 뽑는 편이 빠르다.

```js
// dump-summary.mjs — node dump-summary.mjs webrtc_internals_dump.txt
import { readFileSync } from 'node:fs';

const dump = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const WATCH = /-(currentRoundTripTime|jitter|packetsLost|framesDecoded|freezeCount|qualityLimitationReason)$/;

for (const [pcId, pc] of Object.entries(dump.PeerConnections ?? {})) {
  console.log(`\n# ${pcId} ${pc.url}\nconfig: ${pc.rtcConfiguration}`);

  for (const e of pc.updateLog ?? []) {
    if (/statechange|icecandidateerror/.test(e.type)) console.log(`${e.time}  ${e.type}  ${e.value}`);
  }

  for (const [key, series] of Object.entries(pc.stats ?? {})) {
    if (!WATCH.test(key)) continue;
    const values = JSON.parse(series.values);
    const nums = values.filter(Number.isFinite);
    const max = nums.length ? Math.max(...nums) : '-';
    console.log(`${series.statsType.padEnd(14)} ${key}  last=${values.at(-1)}  max=${max}`);
  }
}
```

덤프를 읽는 순서는 5절의 디버깅 플로와 같다.

1. <strong>`rtcConfiguration`</strong>: TURN 서버가 들어 있는가, `iceTransportPolicy`가 의도대로인가.
2. <strong>이벤트 로그의 시그널링 순서</strong>: offer/answer가 `stable`까지 갔는가, `setRemoteDescription`이 에러로 끝나지 않았는가.
3. <strong>`icecandidate`와 `icecandidateerror`</strong>: 로컬 후보에 `typ srflx`·`typ relay`가 있는가. `icecandidateerror`에 `errorCode` 701(STUN/TURN 서버에 닿지 못함)이나 401(인증 실패)이 찍혔는가, 어느 `url`인가.
4. <strong>`iceconnectionstatechange` 흐름</strong>: `checking → connected`인지, `checking → failed`인지, `connected → disconnected → failed`인지(연결 후 끊김).
5. <strong>통계 그래프</strong>: 선택된 후보 쌍(relay인가), `bytesReceived` 증가, `framesDecoded` 증가, `freezeCount`, `qualityLimitationReason`의 시간대별 변화를 사용자가 문제를 말한 시각과 맞춰 본다.

### about:webrtc와 그 밖의 환경

파이어폭스는 `about:webrtc`에서 PeerConnection별 ICE 후보 쌍 표(선택된 쌍 표시), 로컬·원격 SDP, RTP 통계를 보여 주고, 페이지를 파일로 저장하거나 상세 로그를 켜는 기능을 제공한다. 크롬과 파이어폭스의 통계 구현이 조금씩 달라서(예: 파이어폭스의 비표준 `selected` 필드), 한 브라우저에서만 재현되는 문제는 양쪽 도구를 함께 본다. 사파리에는 이 수준의 내부 페이지가 없어서 직접 수집한 `getStats()`가 더 중요해진다.

디바이스 쪽에서는 로그가 같은 역할을 한다. GStreamer는 `GST_DEBUG=webrtcbin:6`, Pion은 `PION_LOG_DEBUG=ice,dtls` 같은 환경변수로 ICE·DTLS 단계 로그를 켠다. KVS C SDK의 로그 레벨은 [19장](/study/webrtc/19-kvs-c-sdk)에서 다룬다.

## 5. 흔한 장애: 증상 → 원인 → 확인 방법

같은 "영상이 안 나와요"도 원인은 여러 계층에 걸쳐 있다. 증상별로 정리하면 다음과 같다.

| 증상 | 흔한 원인 | 확인 방법 |
|---|---|---|
| <strong>ICE failed</strong><br>(`iceConnectionState`가 `failed`, 연결 자체가 안 됨) | UDP가 막힌 망인데 TURN이 없거나 TCP/TLS 443을 제공하지 않음<br>TURN 자격증명 오류·만료<br>TURN `external-ip` 미설정으로 relay 후보에 사설 IP가 실림<br>후보 교환 누락(시그널링 메시지 유실, `setRemoteDescription` 전 `addIceCandidate` 실패)<br>디바이스 스택이 mDNS(`.local`) 후보를 해석하지 못함 | 로컬 후보에 `relay`·`srflx`가 있는지<br>`icecandidateerror`의 `errorCode`(701/401)와 `url`<br>후보 쌍이 모두 `failed`인지, 아예 원격 후보가 없어 쌍이 안 생겼는지<br>`iceTransportPolicy: 'relay'`로 TURN만 써서 재현<br>relay 후보 주소가 공인 IP인지, `turnutils_uclient`로 TURN 서버 직접 시험 |
| <strong>연결은 되는데 검은 화면</strong> | 수신 바이트 0: 송신 트랙 없음·`enabled=false`·`replaceTrack(null)`, transceiver 방향 불일치, SFU 구독 누락<br>바이트는 오는데 디코딩 0: 키프레임 미도착(송신 측이 PLI에 응답 안 함), 코덱·프로파일 미지원, E2EE 복호화 실패<br>디코딩은 되는데 안 보임: `video` 요소 재생 실패(자동재생 정책, `srcObject` 미연결, iOS `playsinline` 누락) | `inbound-rtp`의 `bytesReceived` → `framesReceived` → `framesDecoded` → `keyFramesDecoded` 중 어디서 멈추는지<br>수신 측 `pliCount`는 느는데 송신 측 `keyFramesEncoded`가 그대로인지<br>`codec`의 `mimeType`·`sdpFmtpLine`<br>`transceiver.currentDirection`, `video.videoWidth`, `video.play()`의 거부 사유 |
| <strong>단방향 오디오</strong><br>(한쪽만 들림) | 한쪽이 트랙을 붙이지 않고 offer, `sendonly`/`recvonly` 설정 실수<br>마이크 권한 거부·장치 음소거·`track.enabled=false`<br>수신 측 오디오 자동재생 차단, 출력 장치 선택 오류 | A의 `media-source.audioLevel` > 0 → A의 `outbound-rtp(audio).packetsSent` 증가 → B의 `inbound-rtp(audio).packetsReceived` 증가 → B의 `audioLevel`·`concealedSamples` 비율 순으로 끊긴 곳 찾기<br>양쪽 SDP의 `a=sendrecv`/`a=sendonly` |
| <strong>몇 분 후 끊김</strong><br>(`connected` → `disconnected` → `failed`) | TURN 시간제한 자격증명이 만료돼 allocation Refresh 실패(TTL이 세션보다 짧음)<br>시그널링 WebSocket이 로드밸런서 idle timeout으로 끊겨 ICE restart·재협상 불가<br>LTE 셀 전환·Wi-Fi 이동으로 IP가 바뀌었는데 ICE restart 미구현<br>방화벽의 UDP 세션 강제 종료, 디바이스 발열·메모리 문제로 프로세스 정지 | 연결 시작부터 끊김까지 간격이 매번 같은지(TURN TTL·LB idle timeout과 비교)<br>`candidate-pair.responsesReceived` 증가가 멈춘 시각(consent 실패, 30초 뒤 만료)<br>TURN 로그에서 해당 username의 401·종료 사유<br>시그널링 서버의 연결 종료 로그·close code, `local-candidate` 주소 변화 |
| <strong>화질 급락</strong><br>(해상도·fps 하락, 블록 노이즈) | 업링크 대역폭 부족(LTE 혼잡)으로 대역폭 추정 하향<br>인코더 CPU 부족·발열 스로틀<br>손실 증가로 NACK·PLI 폭증<br>SFU가 낮은 simulcast 레이어로 전환<br>TURN TCP/TLS 경유로 head-of-line blocking | `outbound-rtp.qualityLimitationReason`·`qualityLimitationDurations`, `availableOutgoingBitrate` 추이, `frameWidth`·`targetBitrate`<br>`remote-inbound-rtp.fractionLost`, `roundTripTime` 상승(큐 지연)<br>재전송 비율, `local-candidate.relayProtocol`이 `tcp`/`tls`인지<br>수신 측 해상도·`rid` 변화 |
| <strong>코덱 불일치</strong><br>(협상 실패 또는 영상 m-line 거절) | 디바이스 하드웨어 인코더는 H.264만, 상대는 VP8만 허용<br>H.264 `profile-level-id`·`packetization-mode` 불일치 | answer SDP의 `m=video` 포트가 0(거절)인지<br>양쪽 `a=rtpmap`·`a=fmtp` 교집합([04장](/study/webrtc/04-sdp-jsep)), `setRemoteDescription` 에러 메시지 |

"몇 분 후 끊김"은 특히 TURN 자격증명 TTL을 의심할 만하다. allocation은 주기적으로 Refresh 요청을 보내 수명을 늘리는데, 이 요청도 인증을 거친다. [07장](/study/webrtc/07-turn)의 HMAC 시간제한 자격증명은 username에 만료 시각이 들어 있으므로, TTL이 지나면 Refresh가 거절되고 릴레이가 끊긴다. TTL을 최대 세션 길이보다 길게 잡거나, 만료 전에 새 자격증명으로 ICE restart한다. 로드밸런서 idle timeout(예: AWS ALB 기본 60초)보다 짧은 주기로 시그널링 연결에 ping을 보내는 것도 같은 부류의 대책이다.

### 디버깅 플로

표를 외우는 것보다 계층 순서로 위에서 아래로 좁혀 가는 습관이 중요하다. 아래 단계는 서로 의존한다. 위 단계가 실패했는데 아래 지표를 들여다보는 것은 시간 낭비다.

![디버깅 플로 — ① 시그널링 완료(signalingState stable)? ② ICE 연결(iceConnectionState connected)? ③ DTLS 연결(transport.dtlsState connected)? ④ 패킷 수신(inbound bytesReceived 증가)? ⑤ 디코딩(framesDecoded 증가)? ⑥ 품질 정상(손실·RTT·qualityLimitationReason)? 순서로 예이면 아래로 내려가고, 아니오이면 각각 시그널링 서버 로그·offer/answer 순서·인증, 후보 종류·TURN 도달성·UDP 차단, fingerprint 불일치·setup 역할·패킷 차단, transceiver 방향·트랙 누락·SFU 구독, 키프레임 부재·코덱 불일치·재생 정책, 혼잡·비트레이트·CPU·지터 버퍼 튜닝을 확인하는 흐름](/images/study-webrtc/15-debug-flow-light.png)
![디버깅 플로 — ① 시그널링 완료(signalingState stable)? ② ICE 연결(iceConnectionState connected)? ③ DTLS 연결(transport.dtlsState connected)? ④ 패킷 수신(inbound bytesReceived 증가)? ⑤ 디코딩(framesDecoded 증가)? ⑥ 품질 정상(손실·RTT·qualityLimitationReason)? 순서로 예이면 아래로 내려가고, 아니오이면 각각 시그널링 서버 로그·offer/answer 순서·인증, 후보 종류·TURN 도달성·UDP 차단, fingerprint 불일치·setup 역할·패킷 차단, transceiver 방향·트랙 누락·SFU 구독, 키프레임 부재·코덱 불일치·재생 정책, 혼잡·비트레이트·CPU·지터 버퍼 튜닝을 확인하는 흐름](/images/study-webrtc/15-debug-flow-dark.png)

- ①에서 막히면 미디어는 아예 관계없다. 시그널링 서버 로그, offer/answer 순서, 토큰 인증부터 본다.
- ②는 네트워크 문제다. 후보 수집과 교환, TURN 도달성을 본다. 대부분의 "현장에서만 안 돼요"가 여기서 걸린다.
- ③은 드물지만 fingerprint가 시그널링 도중 바뀌었거나(SDP를 가공한 경우), DTLS 패킷만 막는 장비가 있을 때 생긴다([10장](/study/webrtc/10-dtls-srtp)).
- ④·⑤는 미디어 협상과 송신 측 문제다. 바이트가 오는지, 프레임이 디코딩되는지를 분리해서 본다.
- ⑥까지 왔다면 연결은 정상이고 튜닝의 영역이다([09장](/study/webrtc/09-quality-latency)).

### 배포 전 체크리스트

- TURN이 UDP 3478과 함께 TCP/TLS 443을 제공하고, `iceTransportPolicy: 'relay'` 단독 테스트를 통과한다.
- TURN 자격증명 TTL이 최대 세션 길이보다 길거나, 만료 전 ICE restart가 구현돼 있다.
- 시그널링 연결의 keepalive 주기가 로드밸런서 idle timeout보다 짧다.
- 네트워크 변경(`connectionState`가 `disconnected`/`failed`)에 ICE restart로 대응한다.
- 디바이스 시계가 NTP로 동기화된다(DTLS 인증서 유효기간, 서명 기반 인증).
- 송신 측이 PLI에 키프레임으로 응답한다(하드웨어 인코더의 키프레임 강제 API 연결).
- 디바이스 인코더 프로파일과 시청 브라우저 디코더의 코덱 교집합을 확인했다.
- 클라이언트 `getStats()` 요약이 세션 키와 함께 서버로 수집된다.

## 6. 서버 측 관측

클라이언트 통계는 한 세션의 증상을 보여 주지만, 패턴은 서버에서 보인다. 특정 통신사 가입자만 relay 비율이 갑자기 오르면 그 망이 UDP를 막기 시작했다는 뜻이고, TURN 인증 실패가 한꺼번에 늘면 자격증명 발급 코드에 문제가 생긴 것이다. 이런 신호는 개별 덤프로는 절대 안 보인다.

![서버 측 관측 구조 — 운영자 브라우저(getStats 요약)와 디바이스(Pion·GStreamer 통계)가 10초 요약을 HTTPS·MQTT로 수집 API에 보내고, 수집 API는 세션 요약 로그를 Loki로 보내며 집계 지표를 Prometheus에 노출하고, TURN 서버(coturn)는 --prometheus 9641 포트, SFU·시그널링 서버는 /metrics로 Prometheus에 스크레이프되고 세션 로그는 수집 에이전트로 Loki에 들어가며, Grafana가 Loki와 Prometheus를 함께 조회해 대시보드와 알림을 만드는 구조](/images/study-webrtc/15-server-observability-light.png)
![서버 측 관측 구조 — 운영자 브라우저(getStats 요약)와 디바이스(Pion·GStreamer 통계)가 10초 요약을 HTTPS·MQTT로 수집 API에 보내고, 수집 API는 세션 요약 로그를 Loki로 보내며 집계 지표를 Prometheus에 노출하고, TURN 서버(coturn)는 --prometheus 9641 포트, SFU·시그널링 서버는 /metrics로 Prometheus에 스크레이프되고 세션 로그는 수집 에이전트로 Loki에 들어가며, Grafana가 Loki와 Prometheus를 함께 조회해 대시보드와 알림을 만드는 구조](/images/study-webrtc/15-server-observability-dark.png)

Prometheus·Loki·Grafana 자체의 구조와 운영은 [관측성 스터디](/study/observability/)에서 자세히 다룬다. 여기서는 WebRTC 구성 요소가 무엇을 내보내고 무엇을 봐야 하는지에 집중한다.

### TURN(coturn) 로그

coturn은 세션 단위로 로그를 남긴다. `--log-file`(또는 `stdout`), `--syslog`로 출력 위치를 정하고, `--new-log-timestamp`로 ISO-8601 시각을 붙이면 수집 에이전트가 파싱하기 쉽다. 아래는 형식 예시다(버전에 따라 문구가 조금씩 다르다).

```text
session 001000000000000012: realm <turn.example.com> user <1760864400:tractor-042>: incoming packet ALLOCATE processed, success
session 001000000000000012: realm <turn.example.com> user <1760864400:tractor-042>: incoming packet REFRESH processed, error 401: Unauthorized
session 001000000000000012: usage: realm=<turn.example.com>, username=<1760864400:tractor-042>, rp=183245, rb=170118933, sp=1532, sb=98211
session 001000000000000012: closed (2nd stage), user <1760864400:tractor-042> realm <turn.example.com> origin <>, local 10.0.1.5:3478, remote 203.0.113.7:51234, reason: allocation timeout
```

- username이 `만료시각:디바이스ID` 형식(07장의 REST 자격증명 패턴)이므로, 로그에서 바로 어느 디바이스의 세션인지, 자격증명이 언제 만료되는지 알 수 있다. 두 번째 줄처럼 REFRESH가 401로 실패한 뒤 세션이 닫혔다면 5절의 "몇 분 후 끊김" 중 TTL 만료가 원인이다.
- `usage` 줄의 `rp/rb/sp/sb`는 받은·보낸 패킷과 바이트다. 세션별 릴레이 트래픽, 즉 TURN 비용의 근거가 된다.

### TURN(coturn) 메트릭

coturn은 `--prometheus` 옵션으로 Prometheus 메트릭을 연다. 기본 포트는 9641(`--prometheus-port`로 변경), 경로는 `/metrics`이고, 같은 포트의 `/`는 헬스체크로 쓸 수 있다. 배포판 패키지 빌드에는 이 기능이 빠져 있을 수 있으므로 공식 컨테이너 이미지나 직접 빌드를 확인한다.

| 메트릭 | 종류 | 용도 |
|---|---|---|
| `turn_total_allocations` | gauge | 현재 할당 수. 동시 릴레이 세션 규모 |
| `turn_traffic_rcvb` / `turn_traffic_sentb` (realm 라벨) | counter | 릴레이 바이트. 단, <strong>종료된 세션</strong> 기준으로 갱신된다 |
| `turn_total_traffic_rcvb` / `turn_total_traffic_sentb` | counter | 전체 합계(역시 종료된 세션 기준) |

트래픽 카운터가 "종료된 세션" 기준이라는 점이 함정이다. 몇 시간짜리 농기계 세션은 끝나기 전까지 트래픽 그래프에 나타나지 않는다. 실시간 대역폭은 호스트 네트워크 메트릭(node_exporter의 인터페이스 바이트)으로 보완한다. 또 `--prometheus-username-labels`는 기본으로 꺼져 있는데, 켜면 사용자 이름을 라벨로 붙인다. REST 방식의 일회성 username과 함께 쓰면 라벨 값이 끝없이 늘어 메모리 누수가 생길 수 있다고 공식 문서가 경고한다. 카디널리티 문제는 [관측성 스터디 04장](/study/observability/04-pull-push-cardinality)에서 다룬 그대로다.

### SFU 메트릭

SFU마다 관측 방식이 다르다. LiveKit은 설정 파일의 `prometheus_port`로 `/metrics`를 연다. mediasoup은 내장 익스포터가 없어서 애플리케이션이 `transport.getStats()`·`producer.getStats()`·`consumer.getStats()`를 주기적으로 호출해 직접 노출해야 한다. Janus는 Admin API와 이벤트 핸들러로 상태를 꺼낸다. 어느 쪽이든 봐야 할 것은 비슷하다.

- 활성 룸·참가자·트랙 수, 인입·송출 비트레이트
- 구독자별 손실률·RTT, 수신한 NACK·PLI 비율(14장의 PLI 폭주 감시)
- 워커 CPU, 이벤트 루프 지연, 사용 중인 UDP 포트 수

### 클라이언트 요약을 지표로

3절의 수집 API는 받은 요약을 두 갈래로 나눈다. <strong>세션별 상세는 로그(Loki)로</strong>, <strong>집계는 메트릭(Prometheus)으로</strong> 보낸다. `sessionId`나 `deviceId`를 Prometheus 라벨로 쓰면 세션마다 새 시계열이 생겨 카디널리티가 폭발한다. 라벨은 브라우저 계열, 경로(direct/relay), relay 프로토콜, 지역처럼 값이 몇 개로 정해진 것만 쓴다.

아래는 직접 정의한 메트릭 이름을 가정한 알림·대시보드 쿼리 예다.

```promql
# ICE failure ratio over 10 minutes (alert above 5%)
sum(rate(webrtc_ice_result_total{result="failed"}[10m]))
  / sum(rate(webrtc_ice_result_total[10m])) > 0.05

# Share of sessions relayed through TURN (sudden jumps = a network started blocking UDP)
sum by (relay_protocol) (rate(webrtc_ice_result_total{result="connected", path="relay"}[30m]))
  / ignoring(relay_protocol) group_left
  sum(rate(webrtc_ice_result_total{result="connected"}[30m]))

# p95 time from offer to connected
histogram_quantile(0.95, sum by (le) (rate(webrtc_connect_duration_seconds_bucket[10m])))

# Freezes per minute across viewers
sum(rate(webrtc_video_freezes_total[5m])) * 60

# Concurrent TURN allocations
sum(turn_total_allocations)
```

이런 비율 지표는 SLI로 삼기 좋다. "연결 시도의 99%가 5초 안에 `connected`", "시청 시간 중 프리즈 비율 1% 미만" 같은 목표를 세우고 오류 예산 기반으로 알림을 거는 방법은 [관측성 스터디 15장](/study/observability/15-slo-sli-alerting)을 참고한다.

### 상관 키로 잇기

서버 측 관측이 진짜 힘을 내는 순간은 신호를 이을 때다. 세션을 열 때 발급한 `sessionId`를 다음 모든 곳에 남긴다.

- 시그널링 서버·WHIP 엔드포인트 로그
- 클라이언트·디바이스 통계 요약(3절)
- TURN username(예: `만료시각:tractor-042`처럼 디바이스 ID를 넣고, 세션 시작 로그에 `sessionId`와 username을 함께 기록)
- SFU 참가자 메타데이터

그러면 Grafana에서 "프리즈 급증" 패널을 클릭해 해당 시간대 세션 요약 로그로 내려가고, 그 세션의 TURN 로그에서 `REFRESH ... error 401`을 찾는 식으로 한 번에 원인까지 간다. 메트릭에서 로그로 이어 가는 방법은 [관측성 스터디 32장](/study/observability/32-signal-correlation)에서 다룬다. KVS 같은 관리형 서비스를 쓰면 TURN·시그널링 서버 대신 CloudWatch 메트릭을 보게 되는데, 이는 [22장](/study/webrtc/22-kvs-operations)에서 다룬다.

::: tip 핵심 정리
- `getStats()`는 id로 엮인 통계 객체 그래프다. 경로는 `transport → candidate-pair → local-candidate`, 송신 품질은 `outbound-rtp ↔ remote-inbound-rtp`, 수신 품질은 `inbound-rtp`에서 읽는다. SFU를 거치면 `remote-inbound-rtp`는 SFU 구간만 반영한다.
- 핵심 지표는 `currentRoundTripTime`·`availableOutgoingBitrate`(경로), `jitter`·`packetsLost`·`framesDropped`·`jitterBufferDelay/EmittedCount`·`freezeCount`(수신), `qualityLimitationReason`·`nackCount`·`pliCount`(송신), `roundTripTime`·`fractionLost`(원격 수신)다. 단위는 초·bps이고, 누적값과 순간값을 구분해야 한다.
- 누적 카운터는 통계 객체의 `timestamp`로 델타를 내 초당 값과 구간 비율로 바꾼다. 리셋과 음수를 `null`로 처리하고, 10초 요약을 세션 키와 함께 서버로 보낸다.
- `chrome://webrtc-internals`는 통화 전에 열고 덤프를 받는다. 설정 → 시그널링 순서 → 후보·후보 오류 → ICE 상태 흐름 → 통계 그래프 순으로 읽는다. 파이어폭스는 `about:webrtc`다.
- 장애는 시그널링 → ICE → DTLS → 패킷 수신 → 디코딩 → 품질 순서로 좁힌다. "몇 분 후 끊김"은 TURN 자격증명 TTL과 로드밸런서 idle timeout을 먼저 의심한다.
- 서버 측은 coturn(`--prometheus`, 세션 로그)·SFU 메트릭·클라이언트 요약을 Prometheus/Loki/Grafana로 모은다. 세션 ID는 라벨이 아니라 로그에 두고, 상관 키로 메트릭과 로그를 잇는다.
:::

## 다음 챕터

[AWS 관리형 WebRTC 서비스 지도](/study/webrtc/16-aws-landscape)에서는 지금까지 직접 구축 관점에서 본 시그널링·TURN·SFU를 AWS가 어떻게 나눠 제공하는지, KVS WebRTC·Amazon Chime SDK·Amazon IVS Real-Time을 토폴로지·규모·지연·과금 기준으로 비교한다.
