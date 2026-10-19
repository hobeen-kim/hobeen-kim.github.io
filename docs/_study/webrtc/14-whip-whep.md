---
title: "WHIP/WHEP와 스트리밍"
description: "HTTP 요청 한 번으로 WebRTC 세션을 여는 WHIP(RFC 9725)와 WHEP(IETF 드래프트)의 요청/응답 흐름·인증·운영 함정을 정리하고, OBS·GStreamer·FFmpeg 송출과 RTMP/HLS/LL-HLS를 섞은 1:N 방송 설계를 다룬다."
date: 2026-10-19
tags: [WebRTC, WHIP, WHEP, Streaming, HLS]
prev: /study/webrtc/13-native-webrtc
next: /study/webrtc/15-monitoring-debugging
---

# WHIP/WHEP와 스트리밍

::: info 학습 목표
- 시그널링을 HTTP 요청/응답으로 고정한 WHIP가 왜 필요했는지 이해하고, WHIP(RFC 9725)와 WHEP(드래프트)의 표준화 상태를 구분한다.
- POST → 201 Created(Location·ETag·Link) → PATCH(Trickle ICE) → DELETE 흐름과 응답 코드의 의미를 안다.
- Bearer 토큰·CORS·307 리다이렉트·세션 정리 등 WHIP 서버를 운영할 때의 함정을 파악한다.
- 브라우저 최소 WHIP 클라이언트를 작성하고 OBS·GStreamer·FFmpeg로 송출을 구성할 수 있다.
- WHEP 저지연 계층과 HLS/LL-HLS 대규모 계층을 섞는 1:N 방송 구조를 설계한다.
:::

## 1. 왜 HTTP 기반 표준 시그널링인가

[03장](/study/webrtc/03-signaling)에서 본 것처럼 WebRTC는 시그널링을 일부러 표준화하지 않았다. 화상회의 앱에는 장점이다. 방 모델·인증·메시지 스키마를 서비스에 맞게 고를 수 있다. 그런데 방송 쪽에서는 이 자유가 그대로 장벽이 됐다. 미디어 서버마다 WebSocket 위에 자체 프로토콜을 얹다 보니, OBS 같은 송출 소프트웨어나 하드웨어 인코더가 WebRTC로 내보내려면 서버 제품마다 전용 연동 코드를 넣어야 했다. 결과적으로 업계는 몇 초의 지연을 감수하고 RTMP로 인제스트한 뒤 서버에서 WebRTC로 바꿔 내보내는 구성을 오래 유지했다.

RTMP가 인제스트 표준 자리를 오래 지킨 이유는 프로토콜이 뛰어나서가 아니라 설정이 "서버 URL + 스트림 키" 두 칸이면 끝났기 때문이다. <strong>WHIP(WebRTC-HTTP Ingestion Protocol)</strong>는 이 경험을 WebRTC로 가져온다. 클라이언트는 SDP offer를 HTTP POST 한 번으로 보내고, 응답 본문으로 SDP answer를 받는다. 인증은 Bearer 토큰 하나다. 실제로 OBS의 WHIP 설정 화면에서 채울 칸도 "서버 URL"과 "Bearer 토큰" 두 개다.

시그널링을 HTTP 요청/응답으로 고정해도 되는 이유는 세 가지다.

- <strong>단방향 송출의 offer/answer는 왕복 한 번이면 끝난다.</strong> 회의처럼 상대 피어가 언제 들어올지 모르는 상황이 아니므로 서버가 먼저 말을 걸 일이 없다. 지속 연결(WebSocket)이 필요 없다.
- <strong>기존 HTTP 인프라를 그대로 쓴다.</strong> TLS 종단, 로드밸런서, 인증 게이트웨이, 307 리다이렉트로 미디어 서버 분산, 503 + `Retry-After`로 과부하 회피까지 이미 있는 도구로 해결된다.
- <strong>세션이 HTTP 리소스가 된다.</strong> POST가 만든 세션은 `Location` URL을 가진 리소스이고, 수정은 PATCH, 종료는 DELETE다. REST에 익숙한 백엔드 개발자에게 낯설지 않은 모델이다.

대신 범위를 좁혔다. RFC 9725는 "WHIP에서 SDP 재협상은 지원하지 않는다"고 명시한다. 세션이 열린 뒤 바뀔 수 있는 것은 ICE 정보(후보 추가, ICE restart)뿐이다. 트랙 구성도 제한된다. MediaStream은 하나만 허용하고, 같은 종류(오디오 또는 비디오)의 트랙을 둘 이상 넣으면 안 된다. 즉 "오디오 1 + 비디오 1"이 기본형이다. Simulcast는 SDP 협상으로 선택적으로 지원할 수 있다(MAY). 방향은 클라이언트 offer가 `sendonly`(SHOULD, `sendrecv`도 허용), 서버 answer는 `recvonly`(MUST)다.

재생 쪽을 같은 방식으로 정의한 것이 <strong>WHEP(WebRTC-HTTP Egress Protocol)</strong>다. 두 문서의 상태는 다르다.

| 항목 | WHIP | WHEP |
|---|---|---|
| 방향 | 송출(인제스트): 클라이언트 → 서버 | 재생(이그레스): 서버 → 플레이어 |
| 문서 | RFC 9725 (2025년 3월, Proposed Standard) | draft-ietf-wish-whep-05 (2026년 10월 11일자) |
| 상태(2026년 10월 기준) | 표준 확정. RFC 8840·8842를 갱신(update)한다 | WG를 통과해 IESG에 제출, AD 검토 단계. 아직 RFC 아님 |
| SDP 방향 | 클라이언트 `sendonly` / 서버 `recvonly` | 플레이어 `recvonly` / 서버 `sendonly` |
| 담당 WG | IETF WISH | IETF WISH |

::: warning WHEP는 아직 드래프트다
WHEP는 판이 바뀔 때마다 세부 동작이 달라졌다. 예를 들어 최근 판에는 서버가 플레이어의 offer를 받아들일 수 없을 때 `406 Not Acceptable` + SDP 카운터 offer를 돌려주고, 플레이어가 PATCH(`application/sdp`)로 answer를 보내는 흐름이 들어 있다. 미디어 서버와 플레이어 라이브러리가 몇 번째 판을 기준으로 구현했는지 확인하고 조합해야 한다.
:::

AWS 관리형 서비스 중에서는 IVS Real-Time이 WHIP 퍼블리시를 받는다([24장](/study/webrtc/24-ivs-real-time)). KVS WebRTC는 WHIP가 아니라 자체 시그널링 API를 쓴다([17장](/study/webrtc/17-kvs-architecture)).

## 2. WHIP 요청/응답 흐름

WHIP에는 역할이 셋 있다. <strong>WHIP 엔드포인트</strong>는 POST를 받는 URL로, RTMP의 "서버 URL + 스트림 키"에 해당한다. <strong>WHIP 세션</strong>은 POST 성공 시 `Location`으로 생기는 리소스로, 이후 PATCH·DELETE 대상이다. <strong>미디어 서버</strong>는 실제 ICE·DTLS·SRTP 상대다. RFC는 엔드포인트와 미디어 서버가 같은 호스트에 있을 필요가 없다고 명시한다. HTTP 계층과 미디어 계층을 분리해 스케일링할 수 있다는 뜻이다.

![WHIP 클라이언트가 엔드포인트에 Bearer 토큰과 함께 application/sdp offer를 POST하면 엔드포인트가 미디어 서버에 세션을 만들고 201 Created(SDP answer, Location, ETag, Link ice-server)를 돌려주며, 선택적으로 세션 리소스에 trickle-ice-sdpfrag PATCH를 보내 204를 받고, 이후 클라이언트와 미디어 서버가 ICE·DTLS를 거쳐 SRTP 미디어를 보내다가 DELETE와 200 OK로 세션을 끝내는 시퀀스](/images/study-webrtc/14-whip-sequence-light.png)
![WHIP 클라이언트가 엔드포인트에 Bearer 토큰과 함께 application/sdp offer를 POST하면 엔드포인트가 미디어 서버에 세션을 만들고 201 Created(SDP answer, Location, ETag, Link ice-server)를 돌려주며, 선택적으로 세션 리소스에 trickle-ice-sdpfrag PATCH를 보내 204를 받고, 이후 클라이언트와 미디어 서버가 ICE·DTLS를 거쳐 SRTP 미디어를 보내다가 DELETE와 200 OK로 세션을 끝내는 시퀀스](/images/study-webrtc/14-whip-sequence-dark.png)

### POST — offer를 보내고 answer를 받는다

요청은 `Content-Type: application/sdp`(MUST)이고 본문이 SDP offer다. 형식이 틀리거나 SDP가 깨졌으면 서버는 적절한 4xx로 거절한다.

```http
POST /whip/live/tractor-042 HTTP/1.1
Host: media.example.com
Content-Type: application/sdp
Authorization: Bearer eyJhbGciOiJFUzI1NiJ9...

v=0
o=- 5228595038118931041 2 IN IP4 127.0.0.1
s=-
t=0 0
a=group:BUNDLE 0 1
m=audio 9 UDP/TLS/RTP/SAVPF 111
a=mid:0
a=sendonly
a=rtpmap:111 opus/48000/2
...
m=video 9 UDP/TLS/RTP/SAVPF 96
a=mid:1
a=sendonly
a=rtpmap:96 H264/90000
...
```

성공 응답은 `201 Created`다.

```http
HTTP/1.1 201 Created
Content-Type: application/sdp
Location: https://media.example.com/whip/session/7f3c9a
ETag: "a1b2c3"
Link: <stun:stun.example.com>; rel="ice-server"
Link: <turn:turn.example.com?transport=udp>; rel="ice-server"; username="1760860800:tractor-042"; credential="Zm9vYmFy"

v=0
...
m=audio 9 UDP/TLS/RTP/SAVPF 111
a=mid:0
a=recvonly
...
```

| 응답 요소 | 규범 수준 | 의미 |
|---|---|---|
| `Content-Type: application/sdp` + 본문 | MUST | SDP answer |
| `Location` | MUST | 세션 리소스 URL. 이후 PATCH·DELETE 대상 |
| `ETag` | Trickle ICE·ICE restart를 지원하는 세션이면 필수 | 현재 ICE 세션을 식별하는 entity-tag |
| `Link: <...>; rel="ice-server"` | MAY | STUN/TURN URL과 자격증명 |
| `Link: <...>; rel="urn:ietf:params:whip:ext:..."` | 지원하는 확장은 반드시 광고 | 확장 기능 목록. 클라이언트는 모르는 rel을 무시한다 |

부분 수락은 하지 않는다. 서버가 offer 안의 특정 m-line(예: 지원하지 않는 비디오 코덱)만 거절하는 대신 POST 전체를 `422` 또는 `400`으로 거절하는 것이 권고 동작이다. 트랙 수 초과, `a=setup:active`만 제시한 DTLS offer를 지원하지 않는 경우도 마찬가지다.

### PATCH — Trickle ICE와 ICE restart

PATCH 본문은 `application/trickle-ice-sdpfrag`(RFC 8840) 형식의 SDP 조각이다. ICE 자격증명과 m-line·mid, 후보 줄로 구성된다.

```http
PATCH /whip/session/7f3c9a HTTP/1.1
Host: media.example.com
Authorization: Bearer eyJhbGciOiJFUzI1NiJ9...
If-Match: "a1b2c3"
Content-Type: application/trickle-ice-sdpfrag

a=group:BUNDLE 0 1
m=audio 9 UDP/TLS/RTP/SAVPF 111
a=mid:0
a=ice-ufrag:EsAw
a=ice-pwd:P2uYro0UCOQ4zxjKXaWCBui1
a=candidate:1387637174 1 udp 2122260223 192.0.2.1 61764 typ host generation 0 ufrag EsAw network-id 1
a=end-of-candidates
```

```http
HTTP/1.1 204 No Content
```

두 용도는 `If-Match` 값으로 갈린다.

- <strong>Trickle ICE(후보 추가)</strong>: `If-Match`에 201에서 받은 ETag를 넣는다. 성공하면 `204 No Content`이고 본문과 ETag가 없다. `If-Match`가 없으면 `428 Precondition Required`, 값이 현재 ICE 세션과 다르면 `412 Precondition Failed`다. ETag는 "지금 이 후보가 어느 ICE 세션 것인가"를 확인하는 장치다. ICE restart 직후 늦게 도착한 옛 세션의 후보를 걸러낸다.
- <strong>ICE restart</strong>: 새 `ice-ufrag`/`ice-pwd`를 담고 `If-Match: "*"`를 보낸다. 성공하면 `200 OK`와 함께 서버 쪽 새 ICE 자격증명(후보 포함 가능)이 본문으로, 새 ETag가 헤더로 온다. restart에 실패해도 서버는 세션을 즉시 끊지 않는다. 클라이언트는 기존 ICE 세션을 유지한 채 재시도하거나 DELETE한다.
- 세션이 둘 중 하나만 지원하면 지원하지 않는 쪽 PATCH에는 `422`를 돌려준다.

순서 제약도 하나 있다. 클라이언트는 201을 받기 전에 모은 후보를 버퍼에 쌓아 두었다가 응답이 온 뒤 PATCH로 보내야 한다. 세션 URL과 ETag를 모르면 보낼 곳이 없기 때문이다.

::: tip 실전에서는 Trickle을 생략하는 경우가 많다
RFC는 수집이 끝난 뒤 후보를 모두 담은 offer를 보내는 방식도 허용한다. 많은 WHIP 클라이언트가 이 "non-trickle" 방식을 쓴다. 이 방식이 잘 동작하는 이유는 미디어 서버가 보통 공인 IP를 가진다는 점에 있다. RFC는 공인 IP에 직접 붙은 미디어 서버라면 ICE-lite만 지원해도 된다고 허용한다(클라이언트는 full ICE 필수). 클라이언트의 host 후보에서 서버 공인 IP로 connectivity check를 보내면, 서버는 NAT를 거쳐 온 주소를 peer-reflexive 후보로 학습한다([06장](/study/webrtc/06-ice)). 그래서 서버가 공인망에 있으면 클라이언트 쪽 STUN 없이도 연결된다. 비용은 수집을 기다리는 시간이다. srflx·relay 수집이 늦어지면 수백 ms에서 수 초가 걸리므로 반드시 타임아웃을 둔다.
:::

### DELETE — 세션 종료

클라이언트는 `Location` URL에 DELETE를 보내 세션을 끝낸다. 흐름 그림 기준 응답은 `200 OK`다. 디바이스 전원이 갑자기 꺼져 DELETE가 오지 않으면 서버는 ICE consent freshness(RFC 7675)로 비정상 종료를 감지한다. consent는 마지막으로 성공한 확인 후 30초가 지나면 만료되므로, 서버는 그 시점에 세션 리소스를 정리해야 한다.

응답 코드를 한 표로 모으면 다음과 같다.

| 코드 | 상황 |
|---|---|
| `201 Created` | POST 성공. answer + `Location` |
| `204 No Content` | Trickle 후보 PATCH 성공 |
| `200 OK` | ICE restart PATCH 성공, DELETE 성공 |
| `307 Temporary Redirect` | 다른 엔드포인트로 분산. `301`·`302`는 쓰면 안 된다 |
| `400` / `422` | 받아들일 수 없는 SDP·트랙 구성, 지원하지 않는 PATCH 종류 |
| 4xx(보통 `415`) | `Content-Type`이 틀린 요청 |
| `401` / `403` | 토큰 없음·무효 / 권한 없음 |
| `412` / `428` | ETag 불일치 / `If-Match` 누락 |
| `503` (+ `Retry-After`) | 과부하. 클라이언트는 지정 시간 뒤 재시도 |

## 3. 인증과 운영 설계

### Bearer 토큰

RFC 9725는 모든 WHIP 구성 요소가 HTTP 인증을 지원해야 하고, 그중 Bearer 토큰(RFC 6750) 인증은 클라이언트·엔드포인트·세션 모두가 반드시 구현해야 한다고 정한다. 엔드포인트가 토큰을 요구할지는 선택(MAY)이다. 클라이언트는 POST·PATCH·DELETE 모든 요청에 `Authorization` 헤더를 붙이되, CORS preflight(OPTIONS)에는 붙이지 않는다. 토큰이 설정되지 않았으면 헤더 자체를 보내지 않는다. 토큰의 형식과 발급 방법은 범위 밖이다. 이 빈칸을 서비스가 채워야 한다.

디바이스 플랫폼에서 고를 수 있는 방식은 두 가지다.

| 방식 | 장점 | 단점 | 맞는 경우 |
|---|---|---|---|
| 디바이스별 고정 토큰(스트림 키처럼) | OBS·하드웨어 인코더에 그대로 입력 가능, 구현 단순 | 유출되면 회수 전까지 계속 유효. 로테이션 절차 필요 | 사람이 설정하는 송출 장비 |
| 단기 JWT(백엔드 발급) | 만료가 짧아 유출 피해가 작음. 스트림 경로·권한을 클레임에 담음 | 디바이스가 먼저 백엔드에 인증해야 함 | 펌웨어로 직접 송출하는 농기계·로봇 |

단기 JWT 방식에서는 디바이스가 X.509 인증서(mTLS)로 백엔드에 자신을 증명하고, 백엔드가 `sub=tractor-042`, `stream=tractor-042`, `scope=publish`, `exp=+5분` 같은 클레임을 담은 토큰을 내준다. IoT 인증서로 임시 자격증명을 받는 패턴은 [AWS IoT Core 완전 정복](/posts/tech/2025-06-27-iot)에서 다룬 Credential Provider와 같은 구조다.

### 엔드포인트 골격(Node.js)

미디어 서버 앞에 얇은 WHIP 엔드포인트를 두면 인증·CORS·TURN 자격증명 발급을 백엔드가 통제할 수 있다. 아래는 그 골격이다. `mediaServer.*`는 사용하는 SFU의 API로 바꿔야 하는 가정 부분이다.

```js
// whip-endpoint.js — auth/CORS/headers in front of an SFU (mediaServer.* is SFU-specific)
import express from 'express';
import { jwtVerify, createRemoteJWKSet } from 'jose';
import { mediaServer } from './media-server.js';
import { issueTurnCredential } from './turn-credential.js'; // HMAC time-limited (ch07)

const app = express();
app.use(express.text({ type: ['application/sdp', 'application/trickle-ice-sdpfrag'] }));
const JWKS = createRemoteJWKSet(new URL('https://auth.example.com/.well-known/jwks.json'));

app.use((req, res, next) => {
  res.set({
    'Access-Control-Allow-Origin': 'https://console.example.com',
    'Access-Control-Allow-Methods': 'POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Authorization, Content-Type, If-Match',
    // Without this, browser fetch cannot read Location/Link/ETag
    'Access-Control-Expose-Headers': 'Location, Link, ETag',
  });
  if (req.method === 'OPTIONS') {
    return res.set('Accept-Post', 'application/sdp').sendStatus(200); // no auth on preflight
  }
  next();
});

async function verify(req, streamId) {
  const m = /^Bearer (.+)$/.exec(req.get('Authorization') ?? '');
  if (!m) return null;
  try {
    const { payload } = await jwtVerify(m[1], JWKS, { audience: 'whip' });
    return payload.scope === 'publish' && payload.stream === streamId ? payload : null;
  } catch {
    return null;
  }
}

app.post('/whip/live/:streamId', async (req, res) => {
  if (!req.is('application/sdp')) return res.sendStatus(415);
  const claims = await verify(req, req.params.streamId);
  if (!claims) return res.sendStatus(401);

  // Replace an existing session for the same stream (device reconnect case)
  await mediaServer.closeIngestByStream(req.params.streamId);
  const { sessionId, answerSdp, etag } =
    await mediaServer.createIngest(req.params.streamId, req.body);

  const turn = issueTurnCredential(claims.sub, 3600);
  res.status(201)
    .type('application/sdp')
    .set('Location', `https://media.example.com/whip/session/${sessionId}`)
    .set('ETag', etag)
    .append('Link', `<${turn.url}>; rel="ice-server"; username="${turn.username}"; credential="${turn.credential}"`)
    .send(answerSdp);
});

app.delete('/whip/session/:id', async (req, res) => {
  const session = await mediaServer.getIngest(req.params.id);
  if (!session) return res.sendStatus(404);
  if (!(await verify(req, session.streamId))) return res.sendStatus(401);
  await mediaServer.closeIngest(req.params.id);
  res.sendStatus(200);
});

app.listen(8080);
```

### 운영 함정

- <strong>`Access-Control-Expose-Headers` 누락</strong>: 브라우저 클라이언트가 다른 오리진의 엔드포인트를 호출하면 `fetch`는 CORS 안전 목록에 없는 응답 헤더를 숨긴다. `Location`을 못 읽으면 DELETE를 못 보내고, 세션은 consent 만료까지 서버에 남는다. 송출은 되는데 종료가 안 되는 이상한 증상으로 나타난다.
- <strong>preflight에 인증을 걸기</strong>: `Authorization` 헤더가 붙은 요청은 preflight를 유발하고, preflight에는 토큰이 실리지 않는다. OPTIONS까지 401로 막으면 브라우저는 본 요청을 아예 보내지 않는다.
- <strong>재접속과 중복 송출 정책</strong>: LTE가 잠깐 끊긴 농기계가 다시 POST하면, 옛 세션은 consent가 만료될 때(약 30초)까지 살아 있다. "같은 스트림에 두 번째 송출은 거절"하는 정책이면 디바이스는 30초 동안 재접속에 실패한다. RFC가 정하지 않는 부분이므로 서비스가 정해야 하고, 디바이스 송출이라면 위 골격처럼 "새 POST가 오면 옛 세션을 끊고 교체"가 보통 낫다.
- <strong>307 분산과 세션 URL</strong>: 엔드포인트는 307로 여러 미디어 서버에 분산할 수 있다. `fetch`는 307을 따라가며 메서드와 본문을 유지한다. 단 RFC는 PATCH·DELETE의 리다이렉트를 요구하지 않으므로, `Location`은 처음부터 세션이 실제로 있는 인스턴스를 가리켜야 한다.
- <strong>세션 URL은 추측 불가능하게</strong>: 세션 URL을 아는 사람이 DELETE로 방송을 끊을 수 있다. 순번 대신 난수 ID를 쓰고, 세션 요청에도 토큰 검증을 유지한다.
- <strong>`Link`의 TURN 자격증명 타이밍</strong>: ICE 서버 정보는 201에 실려 오는데, 그 시점에 offer는 이미 만들어졌다. RFC는 이 정보를 쓰려면 `setLocalDescription` 전에 `setConfiguration`을 호출해야 할 수 있다고 적는다. non-trickle 클라이언트는 offer를 만들기 전에 후보 수집을 끝내야 하므로 보통 이 값을 쓰지 못한다. UDP가 막힌 현장(TURN TCP/TLS 필수)이라면 TURN 정보를 클라이언트에 미리 설정하거나, trickle 클라이언트로 201 뒤에 후보 수집을 시작하는 구현을 고른다. TURN 자격증명은 [07장](/study/webrtc/07-turn)의 시간제한 방식으로 발급한다.

## 4. 최소 WHIP 클라이언트 (브라우저)

브라우저 WHIP 클라이언트는 라이브러리 없이 50줄 정도면 된다. 아래는 non-trickle 방식이다. 노트북에 USB 카메라를 꽂아 농기계 송출을 흉내 내는 테스트 벤치로 쓰기에 충분하다.

```js
// whip-client.js — minimal WHIP publisher (non-trickle)
export async function publishWhip({ endpoint, token, stream, iceServers = [] }) {
  const pc = new RTCPeerConnection({ iceServers, bundlePolicy: 'max-bundle' });

  // WHIP: one MediaStream, at most one track per kind, sendonly
  for (const track of stream.getTracks()) {
    pc.addTransceiver(track, { direction: 'sendonly', streams: [stream] });
  }

  await pc.setLocalDescription(await pc.createOffer());
  await waitForIceGathering(pc, 1500); // put gathered candidates into the offer

  const auth = token ? { Authorization: `Bearer ${token}` } : {};
  const res = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/sdp', ...auth },
    body: pc.localDescription.sdp, // includes candidates gathered so far
  });
  if (res.status !== 201) {
    pc.close();
    throw new Error(`WHIP POST failed: ${res.status} ${await res.text()}`);
  }

  // Location may be relative; resolve it against the final URL (after 307)
  const sessionUrl = new URL(res.headers.get('Location'), res.url).href;
  await pc.setRemoteDescription({ type: 'answer', sdp: await res.text() });

  return {
    pc,
    sessionUrl,
    async stop() {
      pc.close();
      // keepalive lets the DELETE survive page unload
      await fetch(sessionUrl, { method: 'DELETE', headers: auth, keepalive: true })
        .catch(() => {});
    },
  };
}

function waitForIceGathering(pc, timeoutMs) {
  if (pc.iceGatheringState === 'complete') return Promise.resolve();
  return new Promise((resolve) => {
    const done = () => {
      clearTimeout(timer);
      pc.removeEventListener('icegatheringstatechange', onChange);
      resolve();
    };
    const onChange = () => { if (pc.iceGatheringState === 'complete') done(); };
    const timer = setTimeout(done, timeoutMs);
    pc.addEventListener('icegatheringstatechange', onChange);
  });
}
```

```js
// usage
const stream = await navigator.mediaDevices.getUserMedia({
  video: { width: 1280, height: 720, frameRate: 30 },
  audio: true,
});
const session = await publishWhip({
  endpoint: 'https://media.example.com/whip/live/tractor-042',
  token: await fetchPublishToken(), // issued by your backend
  stream,
});
session.pc.addEventListener('connectionstatechange', () => {
  console.log('whip', session.pc.connectionState);
});
window.addEventListener('pagehide', () => session.stop());
```

짚어 둘 부분은 다음과 같다.

- <strong>`addTransceiver(..., { direction: 'sendonly' })`</strong>: `addTrack`을 쓰면 기본 방향이 `sendrecv`가 된다. RFC가 `sendrecv`를 허용하긴 하지만 송출 전용임을 SDP에 명확히 하는 편이 서버 호환성에 유리하다.
- <strong>`localDescription.sdp`</strong>: `createOffer()` 결과가 아니라 `localDescription`을 보내야 수집된 후보가 들어간다. 타임아웃으로 빠져나와도 그때까지 모인 후보는 포함된다.
- <strong>`new URL(location, res.url)`</strong>: `Location`이 상대 경로일 수 있고, 307을 거쳤다면 기준 URL은 원래 엔드포인트가 아니라 최종 URL이다.
- <strong>코덱</strong>: 뒤에서 볼 HLS 패스스루를 생각하면 H.264를 우선하는 편이 좋다. 브라우저 기본 우선순위는 VP8인 경우가 많으므로 `setCodecPreferences`로 순서를 바꾼다([04장](/study/webrtc/04-sdp-jsep)).

### WHEP 플레이어는 거울상이다

재생은 방향만 뒤집으면 된다. 운영자 콘솔에서 농기계 영상을 띄우는 코드는 다음과 같다.

```js
// whep-player.js — minimal WHEP player (non-trickle)
export async function playWhep({ endpoint, token, videoEl }) {
  const pc = new RTCPeerConnection({ bundlePolicy: 'max-bundle' });
  pc.addTransceiver('video', { direction: 'recvonly' });
  pc.addTransceiver('audio', { direction: 'recvonly' });
  pc.ontrack = (e) => {
    // streams can be empty if the server omits msid
    videoEl.srcObject = e.streams[0] ?? new MediaStream([e.track]);
  };

  await pc.setLocalDescription(await pc.createOffer());
  await waitForIceGathering(pc, 1500);

  const auth = token ? { Authorization: `Bearer ${token}` } : {};
  const res = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/sdp', ...auth },
    body: pc.localDescription.sdp,
  });
  if (res.status !== 201) throw new Error(`WHEP POST failed: ${res.status}`);
  const sessionUrl = new URL(res.headers.get('Location'), res.url).href;
  await pc.setRemoteDescription({ type: 'answer', sdp: await res.text() });
  return { pc, stop: () => fetch(sessionUrl, { method: 'DELETE', headers: auth, keepalive: true }) };
}
```

`videoEl`에는 `autoplay`, `playsinline`, 그리고 오디오 자동재생 정책을 피하려면 `muted`를 붙인다. 최신 WHEP 드래프트를 구현한 서버라면 `406` + 카운터 offer 응답도 올 수 있다. 이 경우 응답 본문을 `setRemoteDescription({ type: 'offer' })`로 넣고 `createAnswer()` 결과를 PATCH(`application/sdp`)로 보내는 분기를 추가한다.

## 5. OBS·GStreamer·FFmpeg로 송출하기

### OBS Studio

OBS Studio는 30.0(2023년 11월)부터 WHIP 출력을 지원한다. 설정은 다음과 같다.

1. 설정 → 방송 → 서비스에서 <strong>WHIP</strong>를 고른다.
2. 서버에 WHIP 엔드포인트 URL(`https://media.example.com/whip/live/tractor-042`)을 넣는다.
3. Bearer 토큰 칸에 토큰을 넣는다.

인코더 설정에서 챙길 것은 세 가지다.

- <strong>오디오는 Opus</strong>: WebRTC는 AAC를 지원하지 않는다. WHIP 출력은 Opus로 오디오를 인코딩한다.
- <strong>B-프레임 0</strong>: WebRTC 수신 파이프라인은 디코딩 순서와 표시 순서가 같은 스트림을 전제로 만든 구현이 많다. FFmpeg의 WHIP muxer 문서도 "B-프레임 없는 H.264와 Opus를 쓰라"고 명시한다.
- <strong>키프레임 간격 1~2초</strong>: 새 시청자가 들어오거나 손실 뒤 복구할 때 다음 키프레임까지 기다려야 한다. 뒤에서 볼 HLS 세그먼트 정렬과도 맞물린다.

### GStreamer: whipclientsink

[13장](/study/webrtc/13-native-webrtc)의 GStreamer 파이프라인을 WHIP로 내보내는 요소는 두 가지다.

| 요소 | 플러그인 | 입력 | 특징 |
|---|---|---|---|
| `whipclientsink` | gst-plugins-rs `rswebrtc` (`webrtcsink` 기반) | raw 영상·음성(인코딩된 입력도 가능) | 인코더 선택·혼잡 제어를 요소가 처리. 현재 권장 |
| `whipsink` | gst-plugins-rs `webrtchttp` | RTP 페이로드까지 직접 만든 스트림 | 인코더·페이로더를 직접 구성. 실행 시 "향후 deprecated 예정, whipclientsink 권장" 경고를 낸다 |

`whipclientsink`는 `webrtcsink`의 시그널러만 WHIP로 바꾼 요소다. 그래서 `webrtcsink`의 장점, 즉 사용 가능한 인코더를 골라 붙이고 혼잡 제어 결과에 맞춰 비트레이트를 조절하는 기능을 그대로 쓴다. WHIP 관련 설정은 `signaller::` 접두사가 붙은 속성으로 넣는다(`whip-endpoint`, `auth-token`, `use-link-headers`, `timeout`).

```bash
# Test pattern -> WHIP
gst-launch-1.0 -e \
  videotestsrc is-live=true ! video/x-raw,width=1280,height=720,framerate=30/1 ! \
    videoconvert ! queue ! ws. \
  audiotestsrc is-live=true ! audioconvert ! audioresample ! queue ! ws. \
  whipclientsink name=ws \
    signaller::whip-endpoint="https://media.example.com/whip/live/tractor-042" \
    signaller::auth-token="$WHIP_TOKEN"
```

```bash
# Farm machine camera (V4L2) -> WHIP, H.264 only
gst-launch-1.0 -e \
  v4l2src device=/dev/video0 ! video/x-raw,width=1280,height=720,framerate=30/1 ! \
    videoconvert ! queue ! ws. \
  whipclientsink name=ws video-caps="video/x-h264" \
    signaller::whip-endpoint="https://media.example.com/whip/live/tractor-042" \
    signaller::auth-token="$WHIP_TOKEN" \
    signaller::use-link-headers=true
```

`video-caps`로 제안할 코덱을 H.264로 좁히면 서버 쪽 HLS 패스스루가 쉬워진다. 어떤 인코더(소프트웨어 x264인지, Jetson·VA-API 하드웨어 인코더인지)가 잡혔는지는 `GST_DEBUG=webrtcsink:5` 로그로 확인한다. 이미 하드웨어 인코더로 압축한 스트림을 넣을 수도 있지만, 그러면 요소가 인코더 비트레이트를 직접 바꿀 수 없어 혼잡 제어 효과가 줄어든다.

::: details 레거시 whipsink 예시
```bash
gst-launch-1.0 videotestsrc ! videoconvert ! openh264enc ! rtph264pay ! \
  'application/x-rtp,media=video,encoding-name=H264,payload=97,clock-rate=90000' ! whip.sink_0 \
  audiotestsrc ! audioconvert ! opusenc ! rtpopuspay ! \
  'application/x-rtp,media=audio,encoding-name=OPUS,payload=96,clock-rate=48000,encoding-params=(string)2' ! whip.sink_1 \
  whipsink name=whip auth-token=$WHIP_TOKEN whip-endpoint=$WHIP_ENDPOINT
```
페이로더와 caps를 직접 맞춰야 하고 혼잡 제어에 따른 비트레이트 조절이 없다. 새 코드는 `whipclientsink`로 시작한다.
:::

### FFmpeg

FFmpeg 8.0에는 실험 기능으로 WHIP muxer(`-f whip`)가 들어왔다. DTLS를 위해 TLS 라이브러리(OpenSSL 등)와 함께 빌드돼 있어야 한다. 문서가 밝힌 제약은 "B-프레임 없는 H.264 + Opus"다.

```bash
ffmpeg -f v4l2 -framerate 30 -video_size 1280x720 -i /dev/video0 \
  -c:v libx264 -profile:v baseline -tune zerolatency -bf 0 -g 30 \
  -an \
  -authorization "$WHIP_TOKEN" \
  -f whip "https://media.example.com/whip/live/tractor-042"
```

GStreamer보다 파이프라인 표현력은 떨어지지만, 이미 FFmpeg로 영상을 다루는 디바이스라면 한 줄로 WHIP 송출을 시험할 수 있다. 혼잡 제어에 따른 비트레이트 적응은 기대하지 않는 편이 맞다.

## 6. RTMP/HLS/LL-HLS와의 관계와 1:N 방송 설계

WHIP·WHEP가 생겼다고 HLS가 사라지지는 않는다. 둘은 다른 문제를 푼다.

| 프로토콜 | 전송 | 주 용도 | 지연(대략) | 규모 확장 방식 | 브라우저 재생 |
|---|---|---|---|---|---|
| RTMP | TCP | 인제스트(레거시) | 인제스트 구간 수백 ms~수 초 | 서버 팬아웃 | 불가 |
| HLS | HTTP | 대규모 재생 | 6~30초 | CDN 캐시 | Safari 네이티브, 그 외는 보통 hls.js 같은 MSE 라이브러리 |
| LL-HLS | HTTP | 대규모 저지연 재생 | 2~5초 | CDN(블로킹 플레이리스트 요청 지원 필요) | 동일 |
| WebRTC(WHIP/WHEP) | UDP(SRTP) | 인제스트, 초저지연 재생 | 0.5초 미만 | SFU 팬아웃 | 네이티브 |

WebRTC가 HLS처럼 퍼지지 않는 이유는 시청자마다 <strong>상태 있는 세션</strong>이 생긴다는 데 있다.

- 시청자마다 ICE·DTLS 세션과 SRTP 키가 따로 있다. SFU는 같은 패킷도 시청자별로 따로 암호화해 보내야 한다.
- 같은 바이트를 모두에게 주는 구조가 아니라서 HTTP 캐시가 끼어들 자리가 없다. 엣지도 WebRTC를 아는 SFU여야 하고, 규모를 키우려면 캐스케이딩([12장](/study/webrtc/12-topology-sfu))이 필요하다.
- 시청자마다 NACK·PLI·혼잡 피드백이 SFU로 돌아온다. 시청자가 늘면 처리할 피드백도 비례해 는다.

반대로 HLS는 같은 세그먼트 파일을 모두에게 준다. CDN이 한 번 받아 두면 수만 명에게 그대로 나간다. 대신 세그먼트를 다 만들고, 플레이리스트에 올리고, 플레이어가 몇 개를 버퍼링한 뒤에야 재생하므로 지연이 초 단위가 된다.

그래서 실무 구성은 두 계층을 섞는다. 기준은 <strong>"누가 제어 루프 안에 있는가"</strong>다. 농기계를 원격으로 조작하거나 작업을 즉시 판단해야 하는 운영자는 0.5초 미만이 필요하다. 본사 교육 화면, 고객 데모, 현장 모니터링 대시보드를 보는 수백 명은 몇 초 늦어도 된다.

![인제스트 계층의 OBS(WHIP 출력)와 농기계 카메라(whipclientsink)가 WHIP로, 레거시 인코더가 RTMP로 미디어 서버·SFU에 송출하고, 미디어 서버가 저지연 계층의 운영자 콘솔·관제 화면에 WHEP로 0.5초 미만 영상을 보내는 동시에 RTP를 패키저·트랜스코더로 넘겨 Opus를 AAC로 바꾸고 세그먼트를 만든 뒤 CDN을 거쳐 다수 HLS 시청자에게 LL-HLS 2~5초, HLS 6~30초 지연으로 전달하는 하이브리드 구조](/images/study-webrtc/14-hybrid-broadcast-light.png)
![인제스트 계층의 OBS(WHIP 출력)와 농기계 카메라(whipclientsink)가 WHIP로, 레거시 인코더가 RTMP로 미디어 서버·SFU에 송출하고, 미디어 서버가 저지연 계층의 운영자 콘솔·관제 화면에 WHEP로 0.5초 미만 영상을 보내는 동시에 RTP를 패키저·트랜스코더로 넘겨 Opus를 AAC로 바꾸고 세그먼트를 만든 뒤 CDN을 거쳐 다수 HLS 시청자에게 LL-HLS 2~5초, HLS 6~30초 지연으로 전달하는 하이브리드 구조](/images/study-webrtc/14-hybrid-broadcast-dark.png)

이 구조를 설계할 때 결정해야 할 것들은 다음과 같다.

### 코덱: 패스스루할 수 있게 고른다

인제스트에서 H.264를 쓰면 HLS 쪽은 비디오를 다시 인코딩하지 않고 컨테이너만 바꾸는 패스스루가 가능하다. VP8로 들어오면 HLS용으로 트랜스코딩해야 하고, 그 CPU·GPU 비용이 스트림 수만큼 늘어난다. 오디오는 사정이 반대다. WebRTC는 Opus, HLS 플레이어는 AAC가 가장 호환성이 높으므로 오디오 트랜스코딩은 보통 피할 수 없다. 다행히 오디오 트랜스코딩은 가볍다. 반대 방향, 즉 레거시 RTMP 인코더(AAC, 때로 B-프레임 포함) 입력을 WHEP로 내보낼 때도 오디오는 Opus로 바꿔야 하고 B-프레임이 있으면 영상까지 재인코딩해야 한다.

### 키프레임: PLI가 HLS를 흔든다

HLS 세그먼트는 키프레임에서 시작해야 하므로 송출 GOP를 세그먼트 길이(예: 2초)에 맞춘다. 그런데 WebRTC 인코더는 PLI를 받으면 즉시 키프레임을 만든다([09장](/study/webrtc/09-quality-latency)). WHEP 시청자 한 명이 손실을 겪고 보낸 PLI가 SFU를 거쳐 송출 디바이스까지 가면, 키프레임이 불규칙하게 끼어들어 세그먼트 길이가 흔들리고 업링크 비트레이트가 순간적으로 튄다. LTE 업링크가 빠듯한 농기계라면 이 스파이크가 다시 손실을 부른다. SFU가 여러 시청자의 PLI를 모아 송출자에게 보내는 빈도를 제한하고, 패키저는 가변 GOP를 견디도록 구성한다.

### 규모와 비용: 계층마다 단가가 다르다

WHEP 계층 비용은 "시청자 수 × 비트레이트"만큼의 SFU egress에 시청자별 암호화 CPU가 더해진다. HLS 계층은 CDN egress 단가와 패키징 비용이 대부분이다. 운영자 콘솔 같은 소수만 WHEP로 묶고 나머지를 HLS로 보내면, 시청자가 늘어도 비싼 계층은 커지지 않는다.

### 적응형 화질

WHEP 시청자 간 대역폭 차이는 Simulcast로 흡수한다. WHIP offer에 simulcast 레이어를 담으면(RFC상 선택 지원) SFU가 시청자마다 레이어를 고른다. HLS ABR 사다리는 패키저에서 트랜스코딩으로 만드는 것이 일반적이다. Simulcast 레이어를 그대로 ABR 변형으로 쓰려면 레이어 간 키프레임 위치가 맞아야 해서 까다롭다.

### 녹화

HLS 세그먼트는 그 자체로 녹화본이 된다. 패키저 출력을 오브젝트 스토리지에 남기면 별도 녹화 파이프라인 없이 다시보기를 만들 수 있다. SFU 쪽 녹화 구조는 [12장](/study/webrtc/12-topology-sfu)에서 다뤘다.

::: tip 핵심 정리
- WHIP는 SDP offer/answer를 HTTP POST 한 번(`application/sdp` → `201 Created`)으로 고정한 송출 표준이다. RFC 9725(2025년 3월)로 확정됐다. WHEP는 같은 방식의 재생 규격이지만 2026년 10월 현재 IESG 검토 중인 드래프트(-05)다.
- 세션은 `Location`이 가리키는 HTTP 리소스다. PATCH(`application/trickle-ice-sdpfrag`)로 후보 추가(`If-Match: ETag` → 204)와 ICE restart(`If-Match: "*"` → 200 + 새 ETag)를 하고, DELETE로 끝낸다. SDP 재협상은 지원하지 않는다.
- Bearer 토큰은 모든 구성 요소가 반드시 구현해야 하지만 형식·발급은 서비스 몫이다. 운영에서는 CORS `Expose-Headers`, preflight 인증 제외, 재접속 시 세션 교체 정책, 추측 불가능한 세션 URL을 챙긴다.
- 송출 도구는 OBS 30+(WHIP 서비스), GStreamer `whipclientsink`(혼잡 제어 포함, `whipsink`는 레거시), FFmpeg 8.0 `-f whip`(실험 기능)이 있다. 공통 제약은 B-프레임 없는 H.264와 Opus다.
- 1:N 방송은 제어 루프 안의 소수를 WHEP(0.5초 미만)로, 나머지 다수를 LL-HLS/HLS(수 초~수십 초)로 나누는 하이브리드가 정석이다. H.264 패스스루, Opus→AAC 변환, PLI 제한이 핵심 설계 포인트다.
:::

## 다음 챕터

[모니터링과 디버깅](/study/webrtc/15-monitoring-debugging)에서는 `getStats()`로 연결·품질 지표를 읽는 법과 누적 카운터를 초당 값으로 바꾸는 수집 코드, `chrome://webrtc-internals` 덤프 읽기, 흔한 장애의 증상별 원인과 확인 방법, TURN·SFU 서버 측 관측을 다룬다.
