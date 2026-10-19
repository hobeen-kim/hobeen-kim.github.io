---
title: "시그널링"
description: "WebRTC가 시그널링을 표준화하지 않은 이유(JSEP 철학)와 시그널링이 나르는 메시지를 정리하고, 방·피어 식별·메시지 스키마를 갖춘 WebSocket 시그널링 서버를 Node.js와 Spring으로 구현한다. WebSocket·HTTP·MQTT 전송 수단 비교와 인증·인가·TLS 보안까지 다룬다."
date: 2026-10-19
tags: [WebRTC, Signaling, WebSocket]
prev: /study/webrtc/02-webrtc-api
next: /study/webrtc/04-sdp-jsep
---

# 시그널링

::: info 학습 목표
- WebRTC가 시그널링 프로토콜을 정하지 않은 이유를 JSEP(RFC 9429)의 설계 원칙으로 설명할 수 있다.
- 시그널링이 나르는 메시지(세션 제어·SDP·ICE 후보)와 trickle ICE에서 생기는 순서 문제를 안다.
- 방·피어 식별·역할·메시지 스키마를 갖춘 WebSocket 시그널링 서버를 Node.js(ws) 또는 Spring으로 구현하고, 스케일아웃 구조를 설계할 수 있다.
- WebSocket·HTTP·MQTT를 시그널링 전송 수단으로 비교하고 디바이스 환경에 맞는 조합을 고를 수 있다.
- 시그널링이 곧 미디어 보안의 근간인 이유를 이해하고 인증·인가·TLS를 적용할 수 있다.
:::

## 1. 시그널링에 표준이 없는 이유 — JSEP 철학

[02장](/study/webrtc/02-webrtc-api)의 loopback 예제에서는 같은 페이지의 JavaScript가 offer·answer·후보를 함수 호출로 넘겼다. 실제로는 두 피어가 서로 다른 기기에 있으므로 누군가 이 정보를 날라줘야 한다. 이것이 <strong>시그널링</strong>이다. 그런데 WebRTC 명세 어디를 봐도 "시그널링은 WebSocket으로, 메시지 형식은 이렇게"라는 규정이 없다. 빠뜨린 것이 아니라 일부러 뺀 것이다.

WebRTC의 세션 수립 모델을 정의한 JSEP(JavaScript Session Establishment Protocol, RFC 9429)는 설계 원칙을 이렇게 밝힌다.

- WebRTC 호출 수립은 <strong>미디어 평면에 집중하고 시그널링 평면은 애플리케이션에 맡긴다</strong>. 애플리케이션은 SIP 같은 기존 프로토콜이든 자체 프로토콜이든 원하는 것을 쓸 수 있다.
- JSEP 구현은 핵심 시그널링 흐름과 거의 완전히 분리돼 있고, <strong>시그널링 상태 머신 전체를 JavaScript가 통제</strong>할 수 있다.
- 브라우저에 경량 시그널링 프로토콜을 내장하는 대안도 검토했지만 기각했다. 그렇게 하면 시그널링 제어권이 구현 쪽으로 넘어가고, 구현이 glare(양쪽이 동시에 offer를 보내는 충돌) 같은 개념까지 직접 처리해야 하기 때문이다.
- JSEP는 offer/answer 교환(RFC 3264) 외의 시그널링 모델을 규정하지 않는다. <strong>주소 지정, 재전송, 포킹, glare 처리는 전적으로 애플리케이션 몫</strong>이다.

브라우저가 제공하는 것은 "SDP 문자열을 만들고(createOffer/createAnswer), 받은 SDP를 적용하는(setRemoteDescription)" 기능까지다. 그 문자열을 어떤 경로로 누구에게 전달할지는 앱이 정한다.

### 이 선택의 득과 실

| 관점 | 시그널링을 표준화하지 않아서 얻은 것 | 대가 |
|---|---|---|
| 상호운용 | SIP·XMPP 같은 기존 VoIP 시스템과 게이트웨이로 연동하기 쉽다 | 서비스 A의 클라이언트가 서비스 B에 붙을 수 없다 |
| 인프라 재사용 | 이미 있는 WebSocket 서버, MQTT 브로커, HTTP API 위에 얹을 수 있다 | 매번 서버·메시지 형식·재연결을 새로 짜야 한다 |
| 인증·과금 | 앱의 기존 인증 체계를 그대로 시그널링에 적용한다 | 보안을 잘못 설계하면 미디어 암호화까지 무력화된다(5절) |
| 진화 | 시그널링 방식을 바꿔도 브라우저 업데이트가 필요 없다 | 생태계 도구(녹화·인제스트 서버)가 표준 진입점을 갖지 못한다 |

마지막 줄의 문제를 풀려고 나온 것이 WHIP(RFC 9725)와 WHEP다. 인제스트·재생이라는 좁은 용도에 한해 "HTTP POST로 SDP를 보내고 응답으로 SDP를 받는다"는 표준 시그널링을 정했다([14장](/study/webrtc/14-whip-whep)). AWS KVS WebRTC도 자체 WebSocket 시그널링 프로토콜을 정의해 관리형으로 제공한다([18장](/study/webrtc/18-kvs-signaling-api)). 즉 "시그널링은 앱 몫"이라는 원칙 위에서, 특정 용도별로 사실상의 표준이 따로 생기고 있다.

::: tip 시그널링 서버가 죽으면 영상도 끊기나
아니다. 시그널링은 연결을 <strong>맺을 때</strong>만 필요하다. 이미 ICE·DTLS가 수립된 연결의 미디어는 피어끼리(또는 TURN을 거쳐) 흐르므로, 시그널링 서버가 재시작돼도 영상은 계속 나온다. 다만 그동안 새 시청자 입장, 재협상, ICE restart가 불가능하다. 네트워크가 바뀌어 ICE restart가 필요한 순간 시그널링이 없으면 그때 끊긴다. 시그널링 서버의 가용성 목표는 "연결 수립 성공률"과 "복구 가능성"으로 잡는다.
:::

## 2. 시그널링이 나르는 것

시그널링 메시지는 크게 세 부류다.

| 부류 | 메시지 예 | 내용 | 시점 |
|---|---|---|---|
| 세션 제어 | 입장(join), 퇴장(leave), 피어 입장 알림, 오류 | 누가 어떤 방에 있고 누구와 연결할지 | 연결 전후 내내 |
| SDP | offer, answer | 코덱·방향·암호화 지문·ICE 자격증명([04장](/study/webrtc/04-sdp-jsep)) | 최초 협상, 재협상, ICE restart |
| ICE 후보 | candidate | 연결 시도할 주소·포트·우선순위([06장](/study/webrtc/06-ice)) | offer/answer 직후 수 초 동안 연달아 |

여기에 앱 메타데이터(운영자 이름, 권한, 마이크 상태 등)를 얹기도 하지만, 연결 후에는 DataChannel로 보내는 편이 시그널링 서버 부하를 줄인다.

농기계 원격 시청 시나리오에서 메시지가 오가는 순서는 다음과 같다. 디바이스는 켜지면 먼저 시그널링에 접속해 대기하고, 운영자가 들어오면 운영자가 offer를 보낸다.

![시그널링 메시지 시퀀스. 농기계 디바이스가 join(room, device)으로 먼저 접속해 joined(peers 빈 목록)를 받고, 운영자 브라우저가 join(room, viewer)하면 서버가 브라우저에 joined(peers: device)를, 디바이스에 peer-joined(viewer)를 보낸다. 브라우저가 offer(to: device)를 보내면 서버가 offer(from: viewer)로 디바이스에 중계하고, 디바이스의 answer도 같은 방식으로 브라우저에 전달된다. 이어 양쪽이 서버를 거쳐 candidate를 trickle로 주고받고, 미디어와 DataChannel은 서버를 거치지 않고 직접 흐른다. 브라우저가 leave하거나 소켓이 끊기면 서버가 디바이스에 peer-left를 보내고 디바이스는 PeerConnection을 닫는다](/images/study-webrtc/03-signaling-sequence-light.png)
![시그널링 메시지 시퀀스. 농기계 디바이스가 join(room, device)으로 먼저 접속해 joined(peers 빈 목록)를 받고, 운영자 브라우저가 join(room, viewer)하면 서버가 브라우저에 joined(peers: device)를, 디바이스에 peer-joined(viewer)를 보낸다. 브라우저가 offer(to: device)를 보내면 서버가 offer(from: viewer)로 디바이스에 중계하고, 디바이스의 answer도 같은 방식으로 브라우저에 전달된다. 이어 양쪽이 서버를 거쳐 candidate를 trickle로 주고받고, 미디어와 DataChannel은 서버를 거치지 않고 직접 흐른다. 브라우저가 leave하거나 소켓이 끊기면 서버가 디바이스에 peer-left를 보내고 디바이스는 PeerConnection을 닫는다](/images/study-webrtc/03-signaling-sequence-dark.png)

### 누가 offer를 보내는가

시그널링 설계에서 가장 먼저 정할 것이 <strong>offer 주도권</strong>이다. 이 예제처럼 뷰어가 항상 offer를 보내고 디바이스는 항상 answer만 하도록 역할을 고정하면, 양쪽이 동시에 offer를 보내는 glare가 구조적으로 생기지 않는다. 뷰어가 수신 전용(`recvonly`) 트랜시버로 offer를 만들면 디바이스는 자신이 보낼 수 있는 트랙으로 답하면 된다. AWS KVS WebRTC도 뷰어가 offer를 보내는 모델이다([17장](/study/webrtc/17-kvs-architecture)).

반대로 연결 도중 양쪽 누구든 트랙을 추가하거나 방향을 바꿔야 하는 앱이라면 역할 고정만으로는 부족하다. 양쪽이 대칭적으로 재협상하면서도 충돌하지 않게 만드는 <strong>Perfect Negotiation</strong> 패턴(polite/impolite 피어)은 [04장](/study/webrtc/04-sdp-jsep)에서 다룬다.

### Trickle ICE와 순서 문제

ICE 후보는 한꺼번에 나오지 않는다. host 후보는 즉시, server reflexive 후보는 STUN 응답이 온 뒤, relay 후보는 TURN 할당이 끝난 뒤에 하나씩 나온다. 후보를 찾는 즉시 보내는 방식을 <strong>trickle ICE</strong>라 하고, 수집이 끝날 때까지(`iceGatheringState === 'complete'`) 기다렸다가 모든 후보를 SDP에 넣어 한 번에 보내는 방식을 non-trickle(vanilla ICE)이라 한다.

| 방식 | 장점 | 단점 |
|---|---|---|
| Trickle | 연결이 빠르다. host 후보로 먼저 점검을 시작한다 | 메시지가 많고, 후보가 SDP보다 먼저 도착하는 순서 문제를 처리해야 한다 |
| Non-trickle | 메시지가 offer·answer 두 개로 끝난다. HTTP 요청-응답에 잘 맞는다 | 가장 느린 후보(응답 없는 TURN 서버 등)를 기다리느라 수 초가 걸릴 수 있다 |

Trickle을 쓰면 시그널링 경로에서 메시지 순서가 뒤바뀌거나, 상대가 아직 SDP를 처리하는 중에 후보가 도착할 수 있다. [02장](/study/webrtc/02-webrtc-api)에서 봤듯 원격 설명이 적용되기 전에 `addIceCandidate()`를 부르면 실패하므로, 받는 쪽에서 후보를 버퍼링해야 한다.

```js
// 원격 설명이 적용될 때까지 후보를 쌓아 두는 패턴
const pending = [];

async function onRemoteCandidate(candidate) {
  if (pc.remoteDescription) {
    await pc.addIceCandidate(candidate);
  } else {
    pending.push(candidate);
  }
}

async function onRemoteDescription(description) {
  await pc.setRemoteDescription(description);
  for (const c of pending.splice(0)) {
    await pc.addIceCandidate(c);
  }
}
```

후보 메시지의 `payload`는 `RTCIceCandidate`를 JSON으로 직렬화한 것이다. `candidate` 문자열 안에 주소·포트·후보 종류(`typ host`/`srflx`/`relay`)가 들어 있다.

```json
{
  "candidate": "candidate:842163049 1 udp 1677729535 203.0.113.7 46154 typ srflx raddr 192.168.0.10 rport 46154",
  "sdpMid": "0",
  "sdpMLineIndex": 0,
  "usernameFragment": "Xk3p"
}
```

이 문자열에는 디바이스의 사설 IP(`192.168.0.10`)와 공인 IP가 그대로 들어 있다. 시그널링 메시지를 권한 없는 피어에게 흘리면 네트워크 정보가 노출된다는 뜻이다(5절).

## 3. WebSocket 시그널링 서버 설계

시그널링 서버는 브라우저와 디바이스가 모두 접속할 수 있는 중계소다. 양방향으로 즉시 메시지를 밀어줘야 하므로 WebSocket이 가장 흔한 선택이다(다른 선택지는 4절).

### 설계 결정

| 결정 | 선택 | 이유 |
|---|---|---|
| 방(room) | 디바이스 1대 = 방 1개, 방 이름은 디바이스 ID(`tractor-17`) | 권한·과금·로그 단위가 디바이스와 일치한다 |
| 피어 ID | 서버가 접속마다 발급(UUID) | 클라이언트가 정한 ID는 충돌·사칭이 가능하다 |
| 역할 | 방마다 `device` 1명, `viewer` 최대 N명 | P2P에서는 뷰어 수만큼 디바이스 업링크가 배로 든다([16장](/study/webrtc/16-aws-landscape)) |
| 전달 방식 | SDP·후보는 항상 `to`로 지정한 한 피어에게만 | 잘못된 피어에게 SDP가 가면 협상이 꼬이고 정보가 샌다 |
| 발신자 표기 | `from`은 서버가 기입, 클라이언트 값은 무시 | 다른 피어를 사칭한 메시지를 막는다 |
| offer 주도권 | viewer가 offer, device가 answer | glare가 구조적으로 생기지 않는다 |
| payload | 서버는 SDP·후보를 해석하지 않고 그대로 중계 | 서버를 단순하게 유지. 대신 크기 제한은 건다 |
| 상태 | 메모리에만 보관 | 재시작하면 모두 재접속·재협상. 미디어는 영향 없음(1절) |

방 안의 피어와 메시지 라우팅은 다음과 같다.

![방 기반 라우팅 구조. 시그널링 서버 안에 rooms 맵이 있고 room tractor-17에는 뷰어 v-9e·v-7c와 디바이스 d-1a가, room tractor-23에는 뷰어 v-31과 디바이스 d-55가 들어 있다(device 1명, viewer 최대 N명). 뷰어 v-7c가 {"type":"offer","to":"d-1a"}를 보내면 서버가 같은 방에서 to로 대상을 조회하고 from을 기입해 디바이스 d-1a에 {"type":"offer","from":"v-7c"}로 전달한다](/images/study-webrtc/03-room-routing-light.png)
![방 기반 라우팅 구조. 시그널링 서버 안에 rooms 맵이 있고 room tractor-17에는 뷰어 v-9e·v-7c와 디바이스 d-1a가, room tractor-23에는 뷰어 v-31과 디바이스 d-55가 들어 있다(device 1명, viewer 최대 N명). 뷰어 v-7c가 {"type":"offer","to":"d-1a"}를 보내면 서버가 같은 방에서 to로 대상을 조회하고 from을 기입해 디바이스 d-1a에 {"type":"offer","from":"v-7c"}로 전달한다](/images/study-webrtc/03-room-routing-dark.png)

### 메시지 스키마

모든 메시지는 `type` 필드를 가진 JSON 텍스트 프레임이다. 예시의 피어 ID는 읽기 쉽게 줄였고, 실제로는 서버가 발급한 UUID다.

| 방향 | type | 필드 | 의미 |
|---|---|---|---|
| 클라이언트 → 서버 | `join` | `room`, `role` | 방 입장. `role`은 `device` 또는 `viewer` |
| 클라이언트 → 서버 | `offer` / `answer` | `to`, `payload` | SDP 전달 요청. `payload`는 `{ type, sdp }` |
| 클라이언트 → 서버 | `candidate` | `to`, `payload` | ICE 후보 전달 요청. `payload`는 `RTCIceCandidateInit` |
| 클라이언트 → 서버 | `leave` | | 방 퇴장(소켓 종료와 동일하게 처리) |
| 서버 → 클라이언트 | `joined` | `peerId`, `peers[]` | 입장 성공. 내 ID와 먼저 와 있던 피어 목록 |
| 서버 → 클라이언트 | `peer-joined` | `peerId`, `role` | 다른 피어가 들어왔다 |
| 서버 → 클라이언트 | `offer` / `answer` / `candidate` | `from`, `payload` | 중계된 메시지. `from`은 서버가 기입 |
| 서버 → 클라이언트 | `peer-left` | `peerId` | 피어가 나갔다(명시적 퇴장 또는 연결 끊김) |
| 서버 → 클라이언트 | `error` | `code`, `message` | 요청 거부 |

클라이언트가 서버로 보내는 메시지:

```json
{ "type": "join", "room": "tractor-17", "role": "viewer" }
{ "type": "offer", "to": "d-1a", "payload": { "type": "offer", "sdp": "v=0\r\no=- 4611731400430051336 2 IN IP4 127.0.0.1\r\n..." } }
{ "type": "candidate", "to": "d-1a", "payload": { "candidate": "candidate:...", "sdpMid": "0", "sdpMLineIndex": 0 } }
{ "type": "leave" }
```

서버가 클라이언트로 보내는 메시지:

```json
{ "type": "joined", "peerId": "v-7c", "peers": [{ "peerId": "d-1a", "role": "device" }] }
{ "type": "peer-joined", "peerId": "v-7c", "role": "viewer" }
{ "type": "offer", "from": "v-7c", "payload": { "type": "offer", "sdp": "v=0\r\n..." } }
{ "type": "peer-left", "peerId": "v-7c" }
{ "type": "error", "code": "ROOM_FULL", "message": "tractor-17" }
```

오류 코드는 클라이언트가 분기할 수 있게 고정 문자열로 둔다: `BAD_JSON`, `BAD_FORMAT`, `BAD_REQUEST`, `UNKNOWN_TYPE`, `NOT_JOINED`, `ALREADY_JOINED`, `FORBIDDEN`, `DEVICE_EXISTS`, `ROOM_FULL`, `NO_SUCH_PEER`.

### 서버 구현

인증(`authenticate`)과 인가(`authorize`)는 5절에서 구현하고, 여기서는 방·라우팅·하트비트에 집중한다.

::: tabs
@tab Node.js (ws)
```js
// server.mjs — Node.js 18+, npm i ws
import http from 'node:http';
import crypto from 'node:crypto';
import { WebSocketServer, WebSocket } from 'ws';
import { authenticate, authorize } from './auth.mjs'; // 5절

const PORT = Number(process.env.PORT ?? 8080);
const MAX_VIEWERS = 4; // P2P라 뷰어 수만큼 디바이스 업링크가 늘어난다
const RELAY_TYPES = new Set(['offer', 'answer', 'candidate']);

/** room 이름 → Map<peerId, peer> */
const rooms = new Map();

const server = http.createServer((req, res) => {
  if (req.url === '/healthz') return res.writeHead(200).end('ok');
  res.writeHead(404).end();
});

// noServer: 업그레이드 요청을 직접 받아 인증한 뒤에만 WebSocket으로 승격한다
const wss = new WebSocketServer({ noServer: true, maxPayload: 64 * 1024 });

server.on('upgrade', (req, socket, head) => {
  const auth = authenticate(req);
  if (!auth) {
    socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n');
    socket.destroy();
    return;
  }
  wss.handleUpgrade(req, socket, head, (ws) => wss.emit('connection', ws, req, auth));
});

wss.on('connection', (ws, req, auth) => {
  const peer = { id: crypto.randomUUID(), ws, auth, room: null, role: null };

  ws.isAlive = true;
  ws.on('pong', () => { ws.isAlive = true; });

  ws.on('message', (data, isBinary) => {
    if (isBinary) return sendError(ws, 'BAD_FORMAT', 'text frame only');
    let msg;
    try {
      msg = JSON.parse(data.toString());
    } catch {
      return sendError(ws, 'BAD_JSON', 'invalid JSON');
    }
    handle(peer, msg);
  });

  ws.on('close', () => leave(peer));
  ws.on('error', (err) => console.error('ws error', peer.id, err.message));
});

function handle(peer, msg) {
  if (msg === null || typeof msg !== 'object') {
    return sendError(peer.ws, 'BAD_FORMAT', 'object expected');
  }
  if (msg.type === 'join') return join(peer, msg);
  if (msg.type === 'leave') return leave(peer);
  if (RELAY_TYPES.has(msg.type)) return relay(peer, msg);
  return sendError(peer.ws, 'UNKNOWN_TYPE', String(msg.type));
}

function join(peer, { room, role }) {
  if (peer.room) return sendError(peer.ws, 'ALREADY_JOINED', peer.room);
  if (typeof room !== 'string' || (role !== 'device' && role !== 'viewer')) {
    return sendError(peer.ws, 'BAD_REQUEST', 'room and role required');
  }
  if (!authorize(peer.auth, room, role)) return sendError(peer.ws, 'FORBIDDEN', room);

  const members = rooms.get(room) ?? new Map();
  const others = [...members.values()];
  if (role === 'device' && others.some((m) => m.role === 'device')) {
    return sendError(peer.ws, 'DEVICE_EXISTS', room);
  }
  if (role === 'viewer' && others.filter((m) => m.role === 'viewer').length >= MAX_VIEWERS) {
    return sendError(peer.ws, 'ROOM_FULL', room);
  }

  peer.room = room;
  peer.role = role;
  members.set(peer.id, peer);
  rooms.set(room, members);

  send(peer.ws, {
    type: 'joined',
    peerId: peer.id,
    peers: others.map((m) => ({ peerId: m.id, role: m.role })),
  });
  for (const m of others) send(m.ws, { type: 'peer-joined', peerId: peer.id, role });
}

function relay(peer, msg) {
  if (!peer.room) return sendError(peer.ws, 'NOT_JOINED', msg.type);
  const target = rooms.get(peer.room)?.get(msg.to); // 같은 방 안에서만 찾는다
  if (!target) return sendError(peer.ws, 'NO_SUCH_PEER', String(msg.to));
  if (target.role === peer.role) return sendError(peer.ws, 'FORBIDDEN', 'same role');
  // from은 서버가 채운다 — 클라이언트가 보낸 from은 버린다
  send(target.ws, { type: msg.type, from: peer.id, payload: msg.payload });
}

function leave(peer) {
  const members = peer.room && rooms.get(peer.room);
  if (!members) return;
  members.delete(peer.id);
  for (const m of members.values()) send(m.ws, { type: 'peer-left', peerId: peer.id });
  if (members.size === 0) rooms.delete(peer.room);
  peer.room = null;
  peer.role = null;
}

function send(ws, obj) {
  if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(obj));
}

function sendError(ws, code, message) {
  send(ws, { type: 'error', code, message });
}

// 하트비트: 30초마다 ping, 다음 주기까지 pong이 없으면 죽은 연결로 보고 끊는다
const heartbeat = setInterval(() => {
  for (const ws of wss.clients) {
    if (ws.isAlive === false) {
      ws.terminate(); // close 이벤트 → leave()로 peer-left 전파
      continue;
    }
    ws.isAlive = false;
    ws.ping();
  }
}, 30_000);
wss.on('close', () => clearInterval(heartbeat));

server.listen(PORT, () => console.log(`signaling on :${PORT}`));
```

@tab Spring (Java)
```java
// build.gradle: implementation("org.springframework.boot:spring-boot-starter-websocket")
@Configuration
@EnableWebSocket
public class SignalingConfig implements WebSocketConfigurer {

    private final SignalingHandler handler;
    private final TicketHandshakeInterceptor ticketInterceptor; // 5절

    public SignalingConfig(SignalingHandler handler, TicketHandshakeInterceptor ticketInterceptor) {
        this.handler = handler;
        this.ticketInterceptor = ticketInterceptor;
    }

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(handler, "/ws")
                .addInterceptors(ticketInterceptor)                   // 핸드셰이크 단계 인증
                .setAllowedOrigins("https://console.example.com");
    }

    @Bean
    public ServletServerContainerFactoryBean webSocketContainer() {
        var container = new ServletServerContainerFactoryBean();
        container.setMaxTextMessageBufferSize(64 * 1024);             // 메시지 크기 상한
        container.setMaxSessionIdleTimeout(120_000L);
        return container;
    }
}
```

```java
@Component
public class SignalingHandler extends TextWebSocketHandler {

    private static final int MAX_VIEWERS = 4;
    private static final Set<String> RELAY_TYPES = Set.of("offer", "answer", "candidate");

    private final ObjectMapper om = new ObjectMapper();
    private final Object lock = new Object();
    /** room → (peerId → Peer). lock으로 보호한다 */
    private final Map<String, Map<String, Peer>> rooms = new HashMap<>();

    private static final class Peer {
        final String id = UUID.randomUUID().toString();
        final WebSocketSession session; // 동시 전송에 안전한 데코레이터
        final TicketAuth auth;
        String room;                    // lock 안에서만 읽고 쓴다
        String role;

        Peer(WebSocketSession session, TicketAuth auth) {
            this.session = session;
            this.auth = auth;
        }
    }

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        // WebSocketSession.sendMessage는 동시 호출에 안전하지 않다 → 데코레이터로 직렬화
        var safe = new ConcurrentWebSocketSessionDecorator(session, 5_000, 256 * 1024);
        var auth = (TicketAuth) session.getAttributes().get(TicketHandshakeInterceptor.AUTH_ATTR);
        session.getAttributes().put("peer", new Peer(safe, auth));
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws IOException {
        Peer peer = (Peer) session.getAttributes().get("peer");
        JsonNode msg;
        try {
            msg = om.readTree(message.getPayload());
        } catch (JsonProcessingException e) {
            sendError(peer, "BAD_JSON", "invalid JSON");
            return;
        }
        String type = msg.path("type").asText();
        if ("join".equals(type)) join(peer, msg.path("room").asText(null), msg.path("role").asText(null));
        else if ("leave".equals(type)) leave(peer);
        else if (RELAY_TYPES.contains(type)) relay(peer, type, msg);
        else sendError(peer, "UNKNOWN_TYPE", type);
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) throws IOException {
        Peer peer = (Peer) session.getAttributes().get("peer");
        if (peer != null) leave(peer);
    }

    private void join(Peer peer, String room, String role) throws IOException {
        if (room == null || !("device".equals(role) || "viewer".equals(role))) {
            sendError(peer, "BAD_REQUEST", "room and role required");
            return;
        }
        if (!peer.auth.allows(room, role)) {
            sendError(peer, "FORBIDDEN", room);
            return;
        }
        List<Peer> others;
        List<Map<String, String>> peers;
        String error = null;
        synchronized (lock) { // 입장 검사와 등록을 원자적으로
            Map<String, Peer> members = rooms.computeIfAbsent(room, r -> new HashMap<>());
            others = List.copyOf(members.values());
            peers = others.stream().map(m -> Map.of("peerId", m.id, "role", m.role)).toList();
            boolean hasDevice = others.stream().anyMatch(m -> "device".equals(m.role));
            long viewers = others.stream().filter(m -> "viewer".equals(m.role)).count();
            if (peer.room != null) error = "ALREADY_JOINED";
            else if ("device".equals(role) && hasDevice) error = "DEVICE_EXISTS";
            else if ("viewer".equals(role) && viewers >= MAX_VIEWERS) error = "ROOM_FULL";
            else {
                peer.room = room;
                peer.role = role;
                members.put(peer.id, peer);
            }
            if (members.isEmpty()) rooms.remove(room);
        }
        if (error != null) {
            sendError(peer, error, room);
            return;
        }
        send(peer, Map.of("type", "joined", "peerId", peer.id, "peers", peers));
        for (Peer m : others) send(m, Map.of("type", "peer-joined", "peerId", peer.id, "role", role));
    }

    private void relay(Peer peer, String type, JsonNode msg) throws IOException {
        String to = msg.path("to").asText();
        Peer target = null;
        String error = null;
        synchronized (lock) {
            Map<String, Peer> members = peer.room == null ? null : rooms.get(peer.room);
            if (members == null) error = "NOT_JOINED";
            else if ((target = members.get(to)) == null) error = "NO_SUCH_PEER";
            else if (target.role.equals(peer.role)) error = "FORBIDDEN";
        }
        if (error != null) {
            sendError(peer, error, to);
            return;
        }
        ObjectNode out = om.createObjectNode().put("type", type).put("from", peer.id); // from은 서버가 기입
        out.set("payload", msg.path("payload"));
        target.session.sendMessage(new TextMessage(om.writeValueAsString(out)));
    }

    private void leave(Peer peer) throws IOException {
        List<Peer> others;
        synchronized (lock) {
            if (peer.room == null) return;
            Map<String, Peer> members = rooms.get(peer.room);
            members.remove(peer.id);
            if (members.isEmpty()) rooms.remove(peer.room);
            others = List.copyOf(members.values());
            peer.room = null;
            peer.role = null;
        }
        for (Peer m : others) send(m, Map.of("type", "peer-left", "peerId", peer.id));
    }

    private void send(Peer to, Object body) throws IOException {
        if (to.session.isOpen()) to.session.sendMessage(new TextMessage(om.writeValueAsString(body)));
    }

    private void sendError(Peer to, String code, String message) throws IOException {
        send(to, Map.of("type", "error", "code", code, "message", message));
    }
}
```
:::

두 구현에서 짚을 점이 있다.

- <strong>인증은 업그레이드 단계에서 끝낸다.</strong> Node.js는 `noServer` 모드로 HTTP `upgrade` 이벤트를 직접 받아 인증 실패 시 401로 소켓을 닫고, Spring은 `HandshakeInterceptor`가 `false`를 돌려 핸드셰이크를 거부한다. 일단 WebSocket을 열어주고 첫 메시지로 인증하는 방식은 인증 전 연결이 자원을 점유하므로 별도 타임아웃이 필요하다.
- <strong>메시지 크기를 제한한다.</strong> ws의 `maxPayload` 기본값은 100 MiB 수준으로 크다. SDP는 보통 수 KB이므로 64 KiB면 충분하고, 그 이상은 공격이거나 버그다.
- <strong>Spring의 동시 전송 함정</strong>: 같은 `WebSocketSession`에 여러 스레드가 동시에 `sendMessage`를 호출하면 예외가 난다. 시그널링 서버는 여러 피어의 메시지를 한 피어에게 동시에 중계하는 일이 흔하므로, `ConcurrentWebSocketSessionDecorator`로 감싸 전송을 직렬화하고 전송 시간·버퍼 한도를 둔다.
- <strong>하트비트는 필수다.</strong> 로드밸런서와 NAT는 일정 시간 트래픽이 없는 연결을 조용히 끊는다. AWS ALB의 기본 idle timeout은 60초다. 서버가 주기적으로 ping을 보내야 연결이 유지되고, 응답 없는 죽은 연결을 찾아 `peer-left`를 전파할 수 있다. Node.js 예제는 ws의 ping/pong을 쓰고, Spring 원시 WebSocket은 자동 ping이 없으므로 스케줄러로 `PingMessage`를 보내거나 앱 수준 ping 메시지를 정의한다.

### 브라우저 뷰어 클라이언트

뷰어는 입장 후 디바이스가 이미 있으면 바로, 없으면 `peer-joined`를 기다렸다가 offer를 보낸다. 앞의 후보 버퍼링 패턴이 들어 있다.

```js
// viewer.js — 운영자 브라우저 (<script type="module">로 로드)
const ROOM = 'tractor-17';
const iceServers = await fetchIceServers(); // TURN 단명 credential (07장)
const ticket = await fetchTicket(ROOM);     // 5절의 1회용 티켓
const ws = new WebSocket(`wss://signal.example.com/ws?ticket=${encodeURIComponent(ticket)}`);
const video = document.getElementById('remoteVideo');

/** peerId → { pc, pending: RTCIceCandidateInit[] } */
const sessions = new Map();
const send = (obj) => ws.send(JSON.stringify(obj));

ws.onopen = () => send({ type: 'join', room: ROOM, role: 'viewer' });

ws.onmessage = async ({ data }) => {
  const msg = JSON.parse(data);
  switch (msg.type) {
    case 'joined': {
      const device = msg.peers.find((p) => p.role === 'device');
      if (device) await call(device.peerId);
      break;
    }
    case 'peer-joined':
      if (msg.role === 'device') await call(msg.peerId);
      break;
    case 'answer': {
      const s = sessions.get(msg.from);
      if (!s) break;
      await s.pc.setRemoteDescription(msg.payload);
      for (const c of s.pending.splice(0)) await s.pc.addIceCandidate(c);
      break;
    }
    case 'candidate': {
      const s = sessions.get(msg.from);
      if (!s || !msg.payload) break;
      if (s.pc.remoteDescription) await s.pc.addIceCandidate(msg.payload);
      else s.pending.push(msg.payload);
      break;
    }
    case 'peer-left':
      sessions.get(msg.peerId)?.pc.close();
      sessions.delete(msg.peerId);
      break;
    case 'error':
      console.error('signaling error', msg.code, msg.message);
      break;
  }
};

async function call(deviceId) {
  sessions.get(deviceId)?.pc.close(); // 디바이스 재접속 시 이전 연결 정리
  const pc = new RTCPeerConnection({ iceServers });
  sessions.set(deviceId, { pc, pending: [] });

  pc.addTransceiver('video', { direction: 'recvonly' });
  pc.addTransceiver('audio', { direction: 'recvonly' });
  pc.ontrack = (e) => {
    video.srcObject = e.streams[0] ?? new MediaStream([e.track]);
  };
  pc.onicecandidate = ({ candidate }) => {
    if (candidate) send({ type: 'candidate', to: deviceId, payload: candidate });
  };

  await pc.setLocalDescription(await pc.createOffer());
  send({ type: 'offer', to: deviceId, payload: pc.localDescription });
}
```

디바이스 쪽은 같은 프로토콜을 네이티브 코드로 구현한다. `offer`를 받으면 `setRemoteDescription` → `createAnswer` → `setLocalDescription` 후 `answer`를 `from`에게 돌려보내고, 뷰어마다 PeerConnection을 하나씩 만든다. GStreamer webrtcbin·Pion 구현은 [13장](/study/webrtc/13-native-webrtc)에서 다룬다.

재연결도 설계에 포함해야 한다. 소켓이 끊기면 지수 백오프에 무작위 지연(jitter)을 더해 재접속하고, 티켓을 새로 받아 다시 `join`한다. 디바이스 수백 대가 서버 재시작 직후 동시에 재접속하면 그 자체가 부하 폭주가 되므로 jitter가 중요하다. 이미 연결된 미디어는 시그널링 재접속과 무관하게 유지되므로, 재접속 후 기존 PeerConnection이 살아 있으면 재협상 없이 그대로 둔다.

### 스케일아웃

위 서버는 방 정보를 프로세스 메모리에 들고 있으므로 인스턴스가 하나일 때만 동작한다. 인스턴스를 늘리면 같은 방의 뷰어와 디바이스가 서로 다른 노드에 붙을 수 있다.

![시그널링 서버 스케일아웃. 로드밸런서 뒤에 시그널링 노드 A와 B가 있고, 뷰어 v-7c는 노드 A에, 디바이스 d-1a는 노드 B에 소켓을 갖고 있다. ① 뷰어가 노드 A로 offer(to: d-1a)를 보내면 ② 노드 A가 Redis Pub/Sub·NATS 같은 브로커의 peer:d-1a 채널에 publish하고 ③ 그 채널을 구독 중인 노드 B가 수신해 ④ 디바이스에 offer(from: v-7c)를 전달한다](/images/study-webrtc/03-scaleout-light.png)
![시그널링 서버 스케일아웃. 로드밸런서 뒤에 시그널링 노드 A와 B가 있고, 뷰어 v-7c는 노드 A에, 디바이스 d-1a는 노드 B에 소켓을 갖고 있다. ① 뷰어가 노드 A로 offer(to: d-1a)를 보내면 ② 노드 A가 Redis Pub/Sub·NATS 같은 브로커의 peer:d-1a 채널에 publish하고 ③ 그 채널을 구독 중인 노드 B가 수신해 ④ 디바이스에 offer(from: v-7c)를 전달한다](/images/study-webrtc/03-scaleout-dark.png)

| 방식 | 동작 | 장점 | 단점 |
|---|---|---|---|
| 방 기준 고정 라우팅 | URL에 방을 넣고(`/ws?room=tractor-17`) LB가 방 이름 해시로 노드를 고른다 | 노드 간 통신이 없다. 기존 코드 그대로 | 노드 증감 시 재배치, 특정 방 쏠림, LB 기능 의존 |
| 노드 간 pub/sub | 각 노드가 자기 소켓의 `peer:{id}` 채널을 구독하고, 중계 시 대상 채널에 publish | 어느 노드에 붙어도 된다. 노드를 자유롭게 늘린다 | 방 멤버십을 Redis 등 공유 저장소로 옮겨야 하고, 노드가 죽으면 멤버십 정리(TTL)가 필요 |
| 관리형 시그널링 | KVS Signaling Channel 등 클라우드 서비스 사용 | 운영 부담이 없다 | 프로토콜·할당량·과금이 서비스에 묶인다([17장](/study/webrtc/17-kvs-architecture)) |

pub/sub 방식에서는 방 멤버십(누가 어느 방에 있는지)을 공유 저장소에 두고, 노드 장애로 정리되지 않은 멤버가 남지 않게 하트비트로 TTL을 갱신한다. 시그널링 메시지는 유실돼도 클라이언트가 재협상으로 복구할 수 있으므로, 영속 큐보다 가벼운 pub/sub이 잘 맞는다.

## 4. 시그널링 전송 수단 비교

WebSocket이 가장 흔하지만 유일한 답은 아니다. 디바이스 플랫폼에서는 이미 운영 중인 채널을 재사용하는 편이 나을 때가 많다.

| 기준 | WebSocket | HTTP (요청-응답 / SSE+POST / WHIP) | MQTT |
|---|---|---|---|
| 서버 → 클라이언트 푸시 | 즉시 | SSE나 long polling을 따로 써야 함. WHIP는 클라이언트가 시작하는 교환만 | 즉시(구독) |
| 브라우저 지원 | 네이티브 | 네이티브 | MQTT over WebSocket 라이브러리 필요 |
| 디바이스 친화성 | 별도 연결 유지 필요 | 디바이스가 응답자(대기)여야 하면 부적합 | 디바이스가 이미 브로커에 연결돼 있으면 추가 연결 없음 |
| 연결 상태 | stateful, 하트비트 필요 | stateless, LB·캐시·인증이 쉬움 | 브로커가 연결·세션 관리 |
| trickle ICE | 자연스러움 | WHIP는 PATCH로 trickle 지원, 일반 HTTP는 non-trickle이 편함 | 자연스러움 |
| 순서·중복 | TCP 연결 하나 안에서는 순서 보장 | 요청 단위 | 브로커에 따라 순서 비보장, QoS 1은 중복 가능 |
| 대표 사례 | 대부분의 자체 구현, KVS 시그널링 | WHIP/WHEP 인제스트·재생([14장](/study/webrtc/14-whip-whep)) | IoT 디바이스 플랫폼 |

WebSocket과 SSE의 차이 자체는 [WebSocket 과 SSE](/posts/tech/2025-07-20-ssewebsocket) 포스트에 정리해 두었다. 시그널링 관점에서 핵심은 "서버가 언제든 클라이언트에게 먼저 말을 걸 수 있어야 하는가"다. 디바이스가 대기하다가 offer를 받아야 하는 구조라면 서버 푸시가 필수다.

<strong>HTTP 요청-응답</strong>은 "보내는 쪽이 먼저 시작하는" 교환에 잘 맞는다. WHIP는 송출자가 `POST`로 offer를 보내고 `201 Created` 응답 본문으로 answer를 받으며, `Location` 헤더의 세션 URL로 `PATCH`(trickle 후보, ICE restart)와 `DELETE`(종료)를 보낸다. 서버가 stateless하게 수평 확장되고 기존 API 게이트웨이·인증을 그대로 쓸 수 있다. 하지만 디바이스가 "누가 보러 오면 응답하는" 쪽이라면 디바이스가 HTTP 서버를 열 수 없으니(NAT 뒤) 이 모델이 맞지 않는다.

<strong>MQTT</strong>는 디바이스 플랫폼에서 특히 매력적이다. 농기계는 이미 텔레메트리와 원격 명령을 위해 AWS IoT Core 같은 브로커에 MQTT로 상시 연결돼 있다. 같은 연결에 `signaling/{deviceId}/in`, `signaling/{deviceId}/out` 토픽을 추가하면 시그널링용 연결을 따로 유지할 필요가 없고, 디바이스 인증도 이미 갖춘 X.509 인증서(mTLS)를 그대로 쓴다. 다만 몇 가지를 감안해야 한다.

- <strong>메시지 크기 한도</strong>: AWS IoT Core의 MQTT 페이로드 한도는 128 KB다. SDP는 보통 수 KB라 문제없지만, 한도를 넘는 publish는 거부된다.
- <strong>순서와 중복</strong>: AWS IoT Core 브로커는 메시지 순서를 보장하지 않는다. QoS 1은 같은 메시지가 두 번 올 수 있다. 메시지에 세션 ID와 시퀀스 번호를 넣고, 받는 쪽에서 후보를 버퍼링하고 중복 offer를 무시해야 한다.
- <strong>오래된 메시지</strong>: 영속 세션이나 retained 메시지 때문에 디바이스가 재접속 후 몇 분 전 offer를 받을 수 있다. 메시지에 만료 시각을 넣어 오래된 협상을 버린다.
- <strong>브라우저 쪽 부담</strong>: 브라우저도 MQTT over WebSocket으로 브로커에 붙어야 하고, 브라우저용 인증(SigV4, 커스텀 권한 부여자 등)과 토픽 권한 정책을 따로 설계해야 한다.

그래서 실무에서는 하이브리드 구성이 자주 쓰인다. 브라우저는 익숙한 WebSocket으로 시그널링 백엔드에 붙고, 백엔드가 MQTT 브로커를 통해 디바이스와 메시지를 주고받는다.

![하이브리드 시그널링 구성. 운영자 브라우저는 WSS로 시그널링 백엔드(인증·인가·라우팅)에 접속하고, 백엔드는 AWS IoT Core 같은 MQTT 브로커와 pub/sub으로, 브로커는 농기계 디바이스와 MQTT(mTLS)로 연결된다. 토픽은 signaling/{deviceId}/in과 signaling/{deviceId}/out이다. 미디어와 DataChannel은 시그널링 경로와 무관하게 브라우저와 디바이스 사이에 직접(또는 TURN 경유) 흐른다](/images/study-webrtc/03-transport-bridge-light.png)
![하이브리드 시그널링 구성. 운영자 브라우저는 WSS로 시그널링 백엔드(인증·인가·라우팅)에 접속하고, 백엔드는 AWS IoT Core 같은 MQTT 브로커와 pub/sub으로, 브로커는 농기계 디바이스와 MQTT(mTLS)로 연결된다. 토픽은 signaling/{deviceId}/in과 signaling/{deviceId}/out이다. 미디어와 DataChannel은 시그널링 경로와 무관하게 브라우저와 디바이스 사이에 직접(또는 TURN 경유) 흐른다](/images/study-webrtc/03-transport-bridge-dark.png)

이 구성에서 백엔드는 브라우저 인증·인가를 책임지고, 디바이스 쪽은 IoT 정책으로 "자기 토픽만 구독·발행"하도록 제한한다. MQTT 토픽 설계와 IoT Core 권한 정책은 [MQTT 프로토콜과 AWS IoT 적용](/posts/tech/2025-08-13-mqtt) 포스트를 참고한다. 직접 운영이 부담스럽다면 KVS처럼 시그널링 자체를 관리형으로 쓰는 선택지도 있다([16장](/study/webrtc/16-aws-landscape)).

## 5. 시그널링 보안

### 시그널링 무결성이 곧 미디어 보안이다

WebRTC 미디어는 DTLS-SRTP로 반드시 암호화된다. 그런데 DTLS 핸드셰이크에서 상대 인증서가 진짜인지 확인하는 근거는 SDP에 담긴 <strong>인증서 지문(`a=fingerprint`)</strong>이다. 브라우저는 "시그널링으로 받은 지문과 DTLS로 받은 인증서가 일치하는가"만 검사한다.

이 말은 곧 <strong>시그널링 경로를 장악한 공격자는 미디어도 가로챌 수 있다</strong>는 뜻이다. 공격자가 offer와 answer의 지문을 자기 인증서 지문으로 바꿔치기하고 ICE 후보를 자기 주소로 바꾸면, 양쪽 피어는 각각 공격자와 정상적으로 DTLS 연결을 맺는다. 암호화는 되지만 상대가 공격자인 MITM이다. 시그널링 서버 운영자 자신도 이론상 같은 일을 할 수 있다. 신뢰 모델과 MITM 시나리오는 [10장](/study/webrtc/10-dtls-srtp)에서 자세히 다룬다.

따라서 시그널링에는 최소한 다음이 필요하다.

| 위협 | 대책 |
|---|---|
| 전송 중 도청·변조 | TLS 필수(`wss://`, `https://`). 평문 `ws://`는 개발 환경에서만 |
| 아무나 접속 | 연결 시점 인증(티켓·토큰·클라이언트 인증서) |
| 남의 디바이스 시청 | 방 단위 인가. "이 운영자가 이 농기계를 볼 권한이 있는가" |
| 역할 사칭 | 인증 정보에 역할을 묶는다. 뷰어 토큰으로 `device`로 입장 불가 |
| 다른 피어 사칭 | `from`은 서버가 기입. 클라이언트가 보낸 값은 버린다 |
| 방 밖으로 메시지 전달 | 중계 대상은 같은 방 안에서만 찾는다 |
| 자원 고갈 | 메시지 크기 상한, 초당 메시지 수 제한, 방당 인원 제한, 인증 전 연결 타임아웃 |
| 네트워크 정보 노출 | 후보에 사설·공인 IP가 들어 있으므로 권한 있는 피어에게만 전달 |

### 브라우저 WebSocket 인증의 제약

브라우저의 `WebSocket` API는 `Authorization` 같은 <strong>커스텀 헤더를 설정할 수 없다</strong>. 그래서 REST API처럼 Bearer 토큰을 헤더에 싣는 방식을 그대로 쓸 수 없고, 다음 중 하나를 고른다.

| 방식 | 동작 | 주의점 |
|---|---|---|
| 쿠키 | 같은 사이트의 세션 쿠키가 핸드셰이크에 자동으로 실린다 | 다른 사이트가 사용자 브라우저로 WebSocket을 여는 CSWSH 공격에 취약. `Origin` 검사 필수 |
| URL 쿼리 토큰 | `wss://.../ws?token=...` | URL은 LB·프록시 접근 로그에 남는다. 장기 토큰을 넣으면 안 된다 |
| 1회용 티켓 | 인증된 REST API로 수십 초짜리 1회용 티켓을 받아 쿼리에 싣는다 | 로그에 남아도 이미 소모된 티켓이라 재사용 불가. 이 장의 예제 방식 |
| `Sec-WebSocket-Protocol` | 서브프로토콜 헤더에 토큰을 끼워 넣는다 | 편법이다. 서버가 같은 값을 응답해야 하고 프록시 호환성 문제 |
| 첫 메시지 인증 | 연결 후 첫 메시지로 토큰 전송 | 인증 전 연결이 자원을 점유. 짧은 타임아웃 필요 |

KVS 시그널링은 SigV4로 서명한 presigned URL(쿼리 문자열에 서명 포함)로 이 문제를 푼다([18장](/study/webrtc/18-kvs-signaling-api)). 원리는 1회용 티켓과 같다. URL 자체가 짧은 수명의 자격증명이다.

### 1회용 티켓 구현

흐름은 이렇다. 운영자는 이미 로그인한 웹 콘솔에서 `POST /tickets`를 호출하고, 백엔드는 세션을 검증한 뒤 "이 사용자는 `viewer` 역할로 `tractor-17` 방에 들어갈 수 있다"는 정보를 담은 30초짜리 티켓을 발급한다. 브라우저는 그 티켓으로 즉시 WebSocket을 연다. 디바이스는 IoT 인증서(mTLS)로 보호된 엔드포인트에서 `device` 역할 티켓을 받거나, 시그널링 서버가 직접 클라이언트 인증서를 검증하게 할 수 있다. 디바이스 인증서와 자격증명 관리는 [AWS IoT Core 완전 정복 - Shadow, 인증, Job까지](/posts/tech/2025-06-27-iot) 포스트를 참고한다.

::: tabs
@tab Node.js
```js
// auth.mjs — 1회용 접속 티켓
import crypto from 'node:crypto';

const TICKET_TTL_MS = 30_000;
const ALLOWED_ORIGINS = new Set(['https://console.example.com']);
/** ticket → { sub, role, rooms: Set<string>, exp } */
const tickets = new Map();

// 인증된 REST API(POST /tickets)에서 호출한다
export function issueTicket({ sub, role, rooms }) {
  const ticket = crypto.randomBytes(32).toString('base64url');
  tickets.set(ticket, { sub, role, rooms: new Set(rooms), exp: Date.now() + TICKET_TTL_MS });
  return ticket;
}

export function authenticate(req) {
  // 브라우저는 Origin을 보낸다. 디바이스(네이티브 클라이언트)는 보통 보내지 않는다
  const origin = req.headers.origin;
  if (origin && !ALLOWED_ORIGINS.has(origin)) return null;

  const url = new URL(req.url, 'http://placeholder');
  if (url.pathname !== '/ws') return null;

  const ticket = url.searchParams.get('ticket');
  const entry = ticket ? tickets.get(ticket) : undefined;
  if (!entry) return null;
  tickets.delete(ticket); // 1회용: 검사 결과와 무관하게 즉시 소모
  return entry.exp >= Date.now() ? entry : null;
}

export function authorize(auth, room, role) {
  return auth.role === role && auth.rooms.has(room);
}

// 쓰이지 않고 만료된 티켓 청소
setInterval(() => {
  const now = Date.now();
  for (const [t, e] of tickets) if (e.exp < now) tickets.delete(t);
}, 60_000).unref();
```

```js
// server.mjs의 HTTP 핸들러에 티켓 발급 라우트를 추가한다
import { issueTicket } from './auth.mjs';

const server = http.createServer(async (req, res) => {
  if (req.method === 'POST' && req.url === '/tickets') {
    const user = await verifySession(req); // 기존 로그인 세션·JWT 검증 (서비스별 구현)
    if (!user) return res.writeHead(401).end();
    const ticket = issueTicket({ sub: user.id, role: 'viewer', rooms: user.allowedDevices });
    res.writeHead(200, { 'content-type': 'application/json', 'cache-control': 'no-store' });
    return res.end(JSON.stringify({ ticket }));
  }
  if (req.url === '/healthz') return res.writeHead(200).end('ok');
  res.writeHead(404).end();
});
```

@tab Spring (Java)
```java
public record TicketAuth(String sub, String role, Set<String> rooms) {
    public boolean allows(String room, String requestedRole) {
        return role.equals(requestedRole) && rooms.contains(room);
    }
}

/** 1회용 티켓 저장소. 여러 인스턴스라면 Redis GETDEL처럼 조회와 삭제를 원자적으로 */
public interface TicketStore {
    String issue(TicketAuth auth, Duration ttl);
    Optional<TicketAuth> consume(String ticket); // 조회와 동시에 삭제, 만료면 empty
}

@Component
public class TicketHandshakeInterceptor implements HandshakeInterceptor {

    public static final String AUTH_ATTR = "auth";
    private final TicketStore tickets;

    public TicketHandshakeInterceptor(TicketStore tickets) {
        this.tickets = tickets;
    }

    @Override
    public boolean beforeHandshake(ServerHttpRequest request, ServerHttpResponse response,
                                   WebSocketHandler wsHandler, Map<String, Object> attributes) {
        String ticket = UriComponentsBuilder.fromUri(request.getURI()).build()
                .getQueryParams().getFirst("ticket");
        Optional<TicketAuth> auth = ticket == null ? Optional.empty() : tickets.consume(ticket);
        if (auth.isEmpty()) {
            response.setStatusCode(HttpStatus.UNAUTHORIZED);
            return false; // 핸드셰이크 거부
        }
        attributes.put(AUTH_ATTR, auth.get());
        return true;
    }

    @Override
    public void afterHandshake(ServerHttpRequest request, ServerHttpResponse response,
                               WebSocketHandler wsHandler, Exception exception) {
    }
}
```
:::

`Origin` 검사는 티켓 방식에서 필수는 아니다. 공격자 사이트는 사용자의 티켓을 얻을 수 없으니 CSWSH가 성립하지 않는다. 하지만 쿠키 인증을 섞어 쓰게 될 때를 대비한 방어선으로 남겨 둔다. Spring 예제의 `setAllowedOrigins`가 같은 역할이다.

### 그 밖의 운영 체크리스트

- <strong>TURN credential도 시그널링 계층에서 발급한다.</strong> `iceServers`의 TURN 비밀번호는 장기 고정값이 아니라 사용자·만료 시각에 묶인 HMAC 기반 단명 credential로 내려준다. 고정 비밀번호를 프론트엔드에 박으면 누구나 TURN을 무료 릴레이로 쓴다([07장](/study/webrtc/07-turn)).
- <strong>시그널링 로그에 SDP 전문을 남기지 않는다.</strong> SDP와 후보에는 IP 주소와 ICE 비밀번호(`a=ice-pwd`)가 들어 있다. 디버깅용으로는 메시지 타입·크기·피어 ID·방 정도만 남기고, 전문은 샘플링하거나 마스킹한다.
- <strong>권한 회수를 반영한다.</strong> 운영자의 디바이스 접근 권한이 회수되면 새 티켓 발급을 막는 것만으로는 부족하다. 이미 연결된 시그널링 소켓을 끊고, 필요하면 디바이스에 해당 뷰어 PeerConnection을 닫으라고 알린다.
- <strong>방당 뷰어 수와 메시지 속도를 제한한다.</strong> 악의적이거나 버그 있는 클라이언트가 offer를 초당 수백 개 보내면 디바이스가 PeerConnection을 계속 만들다 멈춘다. 서버에서 피어별 메시지 속도를 제한하고, 디바이스도 동시 PeerConnection 수에 상한을 둔다.

::: tip 핵심 정리
- JSEP는 미디어 평면만 표준화하고 시그널링(주소 지정·재전송·glare 처리)은 앱에 맡겼다. 덕분에 기존 인프라를 재사용하지만 서비스마다 시그널링을 새로 짜야 하고, WHIP·KVS 같은 용도별 표준·관리형 서비스가 그 빈자리를 채운다.
- 시그널링은 세션 제어·SDP·ICE 후보를 나른다. offer 주도권을 viewer로 고정하면 glare가 생기지 않고, trickle ICE에서는 원격 설명 전에 도착한 후보를 버퍼링해야 한다.
- WebSocket 서버는 방(디바이스 단위)·서버 발급 피어 ID·역할·`to` 지정 1:1 중계·서버 기입 `from`을 기본으로 설계한다. 업그레이드 단계 인증, 메시지 크기 제한, 하트비트, Spring의 동시 전송 직렬화가 운영 필수 요소다. 다중 인스턴스는 방 기준 라우팅이나 노드 간 pub/sub으로 확장한다.
- 디바이스가 이미 MQTT로 브로커에 연결돼 있다면 MQTT 시그널링이 유리하지만, 순서 비보장·중복·오래된 메시지·크기 한도를 처리해야 한다. 브라우저는 WebSocket, 디바이스는 MQTT인 하이브리드가 실용적이다.
- `a=fingerprint`가 시그널링으로 전달되므로 시그널링을 장악하면 DTLS-SRTP도 MITM당한다. TLS, 연결 시점 인증(1회용 티켓), 방·역할 인가, `from` 위조 방지, 자원 제한을 갖춘다.
:::

## 다음 챕터

[SDP와 Offer/Answer(JSEP)](/study/webrtc/04-sdp-jsep)에서는 시그널링이 나르는 SDP를 한 줄씩 읽고, 코덱 협상과 트랜시버 방향, 시그널링 상태 머신과 재협상·rollback, 그리고 이 장에서 예고한 Perfect Negotiation 패턴을 다룬다.
