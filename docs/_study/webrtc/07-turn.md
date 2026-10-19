---
title: "TURN"
description: "ICE의 마지막 보루인 TURN 릴레이의 동작(Allocate·Refresh·CreatePermission·ChannelBind·Send/Data), UDP·TCP·TLS 443 전송, 시간제한 credential 발급, coturn 설정과 배치, iceTransportPolicy relay 테스트, 릴레이 비율과 트래픽 비용 산정을 다룬다."
date: 2026-10-19
tags: [WebRTC, TURN, coturn, RFC 8656, NAT Traversal]
prev: /study/webrtc/06-ice
next: /study/webrtc/08-rtp-codecs
---

# TURN

::: info 학습 목표
- TURN이 필요한 상황과 할당(allocation)·권한(permission)·채널(channel)로 이루어진 릴레이 모델을 설명한다.
- Allocate 401 → 인증 → CreatePermission → ChannelBind → ChannelData로 이어지는 메시지 흐름과 각 상태의 수명을 안다.
- TURN over TLS 443이 방화벽에서 필요한 이유와 TCP 전송의 대가를 이해하고 `iceServers`를 구성한다.
- 시간제한 credential을 백엔드에서 발급하고, coturn을 공인 IP 환경에 안전하게 배치한다.
- `iceTransportPolicy: 'relay'`로 TURN 경로를 검증하고, 릴레이 비율을 측정해 트래픽 비용을 산정한다.
:::

[06장](/study/webrtc/06-ice)의 ICE는 host·srflx 후보로 직접 경로를 찾다가 모두 실패하면 relay 후보에 기댄다. 이 relay 후보를 만들어 주는 것이 <strong>TURN(Traversal Using Relays around NAT)</strong>이다. 현재 표준은 RFC 8656이며, 기존 RFC 5766과 IPv6 확장인 RFC 6156을 대체한다.

TURN은 연결 성공률을 끌어올리는 대신 서버 대역폭이라는 실제 돈을 쓴다. 그래서 "TURN을 둘지 말지"가 아니라 "몇 %가 TURN을 타고, 그 비용이 얼마인가"가 운영 질문이 된다.

## 1. TURN이 필요한 순간과 릴레이 모델

STUN만으로 연결이 안 되는 대표 상황은 세 가지다.

- <strong>양쪽 모두 주소 의존 매핑 NAT</strong>: symmetric NAT나 일부 CGNAT는 목적지마다 다른 공인 포트를 만든다([05장](/study/webrtc/05-nat-stun)). STUN 서버로 알아낸 srflx 주소가 상대에게는 쓸모없다.
- <strong>UDP 전면 차단</strong>: 기업망·병원·공공 Wi-Fi는 아웃바운드 UDP를 통째로 막기도 한다. 직접 경로는 아예 시도조차 못 한다.
- <strong>아웃바운드 포트 제한</strong>: TCP 80/443만 허용하는 망에서는 TURN조차 기본 포트(3478)로는 닿지 않는다. 3절의 TLS 443이 이 경우를 위한 것이다.

TURN의 해법은 단순하다. 공인 IP를 가진 서버가 클라이언트에게 <strong>주소 하나를 빌려준다</strong>. 상대는 그 주소로 보내고, 서버가 클라이언트에게 전달한다. 클라이언트 쪽에서 보면 서버까지 나가는 아웃바운드 연결 하나만 있으면 되므로 웬만한 NAT·방화벽을 통과한다.

| 용어 | 의미 |
|---|---|
| allocation(할당) | 클라이언트 한 명에게 묶인 서버 쪽 릴레이 상태. 클라이언트의 5-tuple(클라이언트 IP·포트, 서버 IP·포트, 전송 프로토콜)로 식별한다 |
| relayed transport address | 할당으로 빌린 서버의 공인 IP:포트. ICE의 relay 후보가 된다 |
| permission(권한) | 이 할당으로 패킷을 주고받아도 되는 피어 IP 목록. 포트는 보지 않는다 |
| channel(채널) | 피어 주소를 2바이트 번호로 줄여 부르는 바인딩. 헤더 오버헤드를 줄인다 |

운영자가 알아 둘 성질이 몇 가지 있다.

- <strong>TURN 서버는 미디어를 해석하지 않는다.</strong> DTLS-SRTP로 암호화된 패킷을 바이트 그대로 나른다([10장](/study/webrtc/10-dtls-srtp)). TURN 운영자도 영상을 볼 수 없다. 패킷을 복호화해 재분배하는 SFU([12장](/study/webrtc/12-topology-sfu))와 근본적으로 다르다.
- <strong>릴레이 구간(서버 ↔ 피어)은 UDP다.</strong> RFC 8656의 REQUESTED-TRANSPORT는 UDP(17)만 정의한다. 클라이언트 ↔ 서버 구간을 TCP·TLS로 바꿔도 서버 반대편은 UDP로 나간다.
- <strong>한쪽만 TURN을 써도 된다.</strong> 운영자만 relay 후보를 쓰고 디바이스는 srflx로 받는 조합도 흔하다. 양쪽이 모두 relay를 쓰면 트래픽이 TURN을 두 번 지난다(6절 비용 계산에 반영).
- <strong>TURN 서버는 STUN 서버도 겸한다.</strong> 3478 포트에서 Binding 요청에도 응답하므로 `stun:` URL을 같은 호스트로 지정해도 된다. Allocate 성공 응답에도 클라이언트의 공인 주소(XOR-MAPPED-ADDRESS)가 들어 있다.

## 2. 메시지 흐름: Allocate부터 ChannelData까지

TURN 메시지는 STUN 메시지 형식을 그대로 쓴다. 아래 그림은 디바이스의 ICE 에이전트가 relay 후보를 얻고 상대와 데이터를 주고받기까지의 전 과정이다.

![TURN 메시지 흐름 시퀀스 — 클라이언트가 REQUESTED-TRANSPORT=UDP로 Allocate를 보내 401 Unauthorized(REALM·NONCE)를 받고, USERNAME·REALM·NONCE·MESSAGE-INTEGRITY를 붙여 재요청해 XOR-RELAYED-ADDRESS·XOR-MAPPED-ADDRESS·LIFETIME=600이 담긴 성공 응답을 받은 뒤, CreatePermission으로 피어 IP를 허용(300초)하고 Send/Data indication으로 데이터를 중계하며, ChannelBind로 채널 0x4000을 묶어(600초) 4바이트 헤더의 ChannelData로 오가는 과정](/images/study-webrtc/07-turn-sequence-light.png)
![TURN 메시지 흐름 시퀀스 — 클라이언트가 REQUESTED-TRANSPORT=UDP로 Allocate를 보내 401 Unauthorized(REALM·NONCE)를 받고, USERNAME·REALM·NONCE·MESSAGE-INTEGRITY를 붙여 재요청해 XOR-RELAYED-ADDRESS·XOR-MAPPED-ADDRESS·LIFETIME=600이 담긴 성공 응답을 받은 뒤, CreatePermission으로 피어 IP를 허용(300초)하고 Send/Data indication으로 데이터를 중계하며, ChannelBind로 채널 0x4000을 묶어(600초) 4바이트 헤더의 ChannelData로 오가는 과정](/images/study-webrtc/07-turn-sequence-dark.png)

### 할당과 인증

<strong>① 첫 Allocate는 일부러 자격증명 없이 보낸다.</strong> 클라이언트는 아직 서버의 realm과 nonce를 모르기 때문이다. 서버는 <strong>401 Unauthorized</strong>로 거절하면서 REALM과 NONCE를 알려준다. RFC 8656은 여기에 지원하는 비밀번호 알고리즘 목록(PASSWORD-ALGORITHMS)도 담을 수 있게 했다. 패킷 캡처나 TURN 서버 로그에 할당마다 401이 한 번씩 찍히는 것은 정상 흐름이다.

<strong>② 재요청에 USERNAME·REALM·NONCE·MESSAGE-INTEGRITY를 붙인다.</strong> 이것이 STUN의 <strong>long-term credential</strong> 메커니즘이다. MESSAGE-INTEGRITY는 메시지 전체에 대한 HMAC이며, 키는 `MD5(username ":" realm ":" password)`로 만든다. 비밀번호 자체는 전송되지 않는다. nonce는 서버가 정한 기간이 지나면 만료되고, 클라이언트는 <strong>438 Stale Nonce</strong>를 받으면 새 nonce로 다시 서명한다. RFC 8656은 SHA-256 기반 MESSAGE-INTEGRITY-SHA256과 알고리즘 협상도 정의하지만, 실제로 어떤 방식을 쓰는지는 클라이언트·서버 구현의 지원 범위에 달려 있다.

<strong>③ 성공 응답</strong>에는 세 가지가 담긴다.

- XOR-RELAYED-ADDRESS: 빌린 릴레이 주소. 이것이 relay 후보가 된다.
- XOR-MAPPED-ADDRESS: 서버가 본 클라이언트의 공인 주소. relay 후보의 `raddr`로 쓰인다.
- LIFETIME: 할당 수명. <strong>기본 10분(600초)</strong>이다.

할당은 가만두면 사라진다. 클라이언트는 만료 전에 <strong>Refresh</strong> 요청으로 수명을 연장하고, 더 쓰지 않을 때는 LIFETIME=0인 Refresh로 즉시 삭제한다. 브라우저는 이 과정을 알아서 처리한다. 디바이스 SDK를 직접 다룬다면 Refresh 실패(자격증명 만료 등)가 몇 분 뒤 연결 끊김으로 나타난다는 점을 기억하자.

### 권한

할당을 받았다고 아무나 그 주소로 패킷을 보낼 수 있는 것은 아니다. 클라이언트가 <strong>CreatePermission</strong>으로 허용한 피어 IP에서 온 패킷만 전달되고 나머지는 버려진다. TURN 서버가 인터넷 전체에 열린 수신함이 되지 않게 하는 장치다.

- 권한은 <strong>IP 단위</strong>다. 포트는 보지 않는다.
- 갱신하지 않으면 <strong>5분(300초)</strong> 뒤 만료된다. 명시적으로 지울 방법은 없고, 같은 요청을 다시 보내 갱신한다.
- ICE 에이전트는 체크할 원격 후보마다 권한을 설치한다. connectivity check 자체도 권한이 있어야 오가기 때문이다.

### 데이터 전달: indication과 채널

권한이 생기면 데이터를 보낼 수 있다. 방법은 두 가지다.

<strong>Send/Data indication</strong>은 데이터를 STUN 메시지에 담는다. 클라이언트가 Send indication에 피어 주소(XOR-PEER-ADDRESS)와 데이터(DATA)를 넣어 보내면, 서버가 릴레이 주소에서 피어로 UDP 데이터그램을 내보낸다. 반대 방향은 Data indication으로 감싸 클라이언트에게 전한다. indication은 응답이 없는 단방향 메시지다. 문제는 오버헤드다. IPv4 기준으로 STUN 헤더 20바이트, XOR-PEER-ADDRESS 12바이트, DATA 속성 헤더 4바이트를 합쳐 <strong>패킷마다 최소 36바이트</strong>가 붙는다.

<strong>ChannelBind</strong>는 이 오버헤드를 줄인다. 클라이언트가 피어 주소에 채널 번호를 묶어 두면, 이후 데이터는 <strong>ChannelData</strong> 메시지로 보낸다. ChannelData는 STUN 메시지가 아니라 채널 번호 2바이트와 길이 2바이트로 된 <strong>4바이트 헤더</strong>만 갖는다. 채널 바인딩은 <strong>10분(600초)</strong> 동안 유지되며, 바인딩을 갱신하면 해당 피어의 권한도 함께 갱신된다.

체감을 위해 계산해 보자. 2Mbps 영상을 1,200바이트 RTP 패킷으로 보내면 초당 약 208개 패킷이다. Send indication이면 208 × 36바이트 ≈ 7.5KB/s, 약 60kbps가 헤더로만 나간다. ChannelData면 208 × 4바이트 ≈ 0.8KB/s, 약 7kbps다. 브라우저 TURN 클라이언트가 채널을 적극적으로 쓰는 이유다.

<strong>채널 번호 범위는 0x4000~0x4FFF</strong>다. RFC 5766보다 범위가 좁아졌는데, 같은 포트로 들어오는 여러 프로토콜을 첫 바이트로 구분하는 RFC 7983의 규칙 때문이다. 첫 바이트가 0~3이면 STUN, 20~63이면 DTLS, 64~79면 TURN 채널, 128~191이면 RTP/RTCP다. 채널 번호 0x4000~0x4FFF의 첫 바이트가 정확히 64~79에 들어간다. RFC 8656은 0x5000 이상을 DTLS-SRTP 다중화와 충돌하지 않도록 예약해 둔다.

| 메시지 | 형태 | 역할 | 수명·비고 |
|---|---|---|---|
| Allocate | 요청/응답 | 릴레이 주소 할당 | 기본 600초 |
| Refresh | 요청/응답 | 할당 연장, LIFETIME=0이면 삭제 | 만료 전 주기적 전송 |
| CreatePermission | 요청/응답 | 피어 IP 허용 | 300초, IP 단위 |
| Send / Data | indication | STUN으로 감싼 데이터 전달 | 패킷당 36바이트 이상 |
| ChannelBind | 요청/응답 | 피어 주소 ↔ 채널 번호 바인딩 | 600초, 0x4000~0x4FFF |
| ChannelData | 비STUN 프레임 | 채널 번호로 데이터 전달 | 헤더 4바이트 |

## 3. 전송: UDP·TCP·TLS(443)

클라이언트 ↔ TURN 서버 구간은 세 가지 전송을 쓸 수 있다. TURN URL 문법은 RFC 7065가 정의한다.

| URL | 클라이언트 ↔ 서버 | 포트 | 쓰임 |
|---|---|---|---|
| `turn:turn.farm.example.com:3478?transport=udp` | UDP | 3478 (표준) | 기본값. 가장 효율적 |
| `turn:turn.farm.example.com:3478?transport=tcp` | TCP | 3478 (표준) | UDP만 막힌 망 |
| `turns:turn.farm.example.com:443?transport=tcp` | TLS over TCP | 443 (표준은 5349) | TCP 443만 열린 망, DPI가 있는 망 |

RFC 8656이 정한 기본 포트는 UDP·TCP 3478, TLS·DTLS 5349다. <strong>443은 표준 포트가 아니라 운영상의 선택</strong>이다.

![운영자 사무실망의 브라우저가 방화벽을 향해 UDP 3478과 TCP 3478로 시도하면 차단되고, egress로 TCP 443만 허용하는 방화벽을 TLS 443(turns:)으로는 HTTPS처럼 보이며 통과해 TURN 서버(coturn)에 닿고, TURN 서버와 농기계 디바이스 사이 relay 구간은 항상 UDP로 이어지는 구조](/images/study-webrtc/07-turn-transports-light.png)
![운영자 사무실망의 브라우저가 방화벽을 향해 UDP 3478과 TCP 3478로 시도하면 차단되고, egress로 TCP 443만 허용하는 방화벽을 TLS 443(turns:)으로는 HTTPS처럼 보이며 통과해 TURN 서버(coturn)에 닿고, TURN 서버와 농기계 디바이스 사이 relay 구간은 항상 UDP로 이어지는 구조](/images/study-webrtc/07-turn-transports-dark.png)

### 왜 TLS 443인가

- <strong>아웃바운드 허용 목록이 웹뿐인 망이 많다.</strong> 보안 정책이 엄격한 사무실 망은 업무에 필요한 HTTPS(TCP 443)만 열어 두고 UDP와 비표준 포트를 막는다. 3478은 UDP든 TCP든 막힌다.
- <strong>443이라도 평문 TCP는 막힐 수 있다.</strong> 차세대 방화벽이나 투명 프록시는 443 포트로 가는 트래픽이 실제 TLS인지 들여다본다. TURN over TCP를 443으로 띄우면 TLS 핸드셰이크가 없어 차단된다. TLS로 감싸야 바깥에서는 평범한 HTTPS 연결로 보인다.
- <strong>결국 "어디서든 붙는다"를 보장하는 마지막 경로다.</strong> 운영자가 어느 사무실에서 접속하든 영상이 떠야 한다면 `turns:...:443`은 필수 항목이다.

### TCP·TLS의 대가

TLS 443은 만능이 아니다. 클라이언트 ↔ 서버 구간이 TCP가 되면 패킷 손실 시 TCP가 재전송할 때까지 뒤 패킷이 모두 대기한다(head-of-line blocking). 실시간 영상은 늦게 온 패킷보다 버린 패킷이 낫다. 게다가 TCP 혼잡 제어 위에 WebRTC 혼잡 제어([09장](/study/webrtc/09-quality-latency))가 겹쳐 대역폭 추정이 흔들린다. TLS 핸드셰이크와 암호화는 서버 CPU도 쓴다.

그래서 <strong>세 가지를 모두 등록하되 UDP가 이기게</strong> 한다. [06장](/study/webrtc/06-ice)에서 본 대로 libwebrtc는 relay 후보의 type preference를 UDP 2, TCP 1, TLS 0으로 매긴다. UDP 릴레이가 통하면 TLS 경로는 선택되지 않는다.

```js
const pc = new RTCPeerConnection({
  iceServers: [
    { urls: 'stun:turn.farm.example.com:3478' },
    {
      urls: [
        'turn:turn.farm.example.com:3478?transport=udp',
        'turn:turn.farm.example.com:3478?transport=tcp',
        'turns:turn.farm.example.com:443?transport=tcp',
      ],
      username: cred.username,     // 4절의 시간제한 credential
      credential: cred.credential,
    },
  ],
});
```

### 443 운영 체크리스트

- <strong>같은 IP의 443을 웹 서버와 나눠 쓸 수 없다.</strong> TURN 전용 IP나 인스턴스를 둔다. SNI를 보고 L4 프록시에서 분기하는 방법도 있지만 구성이 복잡해진다.
- <strong>정식 인증서를 쓴다.</strong> `turns:` URL의 호스트명과 일치하는 인증서(Let's Encrypt 등)를 coturn에 건다. IP 주소로 URL을 쓰면 인증서 검증이 꼬이므로 도메인을 쓴다.
- <strong>비root로 443에 바인딩</strong>하려면 Linux에서 `CAP_NET_BIND_SERVICE` 권한이 필요하다.
- <strong>할당 수가 곱해진다.</strong> 브라우저는 후보 수집 단계에서 등록된 TURN URL마다(네트워크 인터페이스마다) 할당을 시도한다. URL 세 개를 등록하면 PeerConnection 하나가 할당 여러 개를 만들 수 있다. 서버 할당 한도를 계산할 때 반영한다.

## 4. 인증: long-term credential과 시간제한 credential

TURN은 반드시 인증해야 한다. 열린 릴레이는 남의 트래픽을 공짜로 실어 나르고, 트래픽 출처를 세탁하는 데 쓰이며, 다음 절에서 볼 내부망 접근(SSRF)의 발판이 된다.

문제는 <strong>브라우저에 건네는 자격증명은 숨길 수 없다</strong>는 점이다. `iceServers`의 `username`과 `credential`은 개발자 도구에서 그대로 보인다. 고정 계정을 박아 두면 누구든 복사해 자기 서비스의 TURN으로 쓸 수 있다.

### TURN REST API 패턴

해법은 <strong>짧게 살다 죽는 credential</strong>을 백엔드에서 발급하는 것이다. 흔히 "TURN REST API"라 부르는 이 패턴은 `draft-uberti-behave-turn-rest-00`에서 나왔다. 만료된 개인 드래프트지만 coturn을 비롯한 TURN 서버들이 사실상 표준처럼 지원한다.

- 백엔드와 TURN 서버가 <strong>비밀값(secret)</strong>을 미리 공유한다.
- `username = 만료시각(Unix 초) + ":" + 사용자ID`
- `password = base64(HMAC-SHA1(secret, username))`
- TURN 서버는 같은 secret으로 HMAC을 다시 계산해 비교하고, username 앞의 만료 시각이 이미 지났으면 거부한다.

![시간제한 TURN credential 흐름 — 브라우저/디바이스가 앱 인증 토큰으로 백엔드 API에 GET /turn-credentials를 요청하고, secret을 보관한 백엔드가 username=1792414800:robot-17, credential=base64(HMAC-SHA1(secret, username)), ttl=3600을 응답하면, 클라이언트가 그 USERNAME과 MESSAGE-INTEGRITY로 coturn에 Allocate하고, 같은 static-auth-secret을 사전 공유한 coturn이 HMAC을 재계산해 비교하며 timestamp가 현재보다 과거면 거부하는 구조](/images/study-webrtc/07-credential-flow-light.png)
![시간제한 TURN credential 흐름 — 브라우저/디바이스가 앱 인증 토큰으로 백엔드 API에 GET /turn-credentials를 요청하고, secret을 보관한 백엔드가 username=1792414800:robot-17, credential=base64(HMAC-SHA1(secret, username)), ttl=3600을 응답하면, 클라이언트가 그 USERNAME과 MESSAGE-INTEGRITY로 coturn에 Allocate하고, 같은 static-auth-secret을 사전 공유한 coturn이 HMAC을 재계산해 비교하며 timestamp가 현재보다 과거면 거부하는 구조](/images/study-webrtc/07-credential-flow-dark.png)

이 방식의 장점은 <strong>TURN 서버가 상태를 갖지 않는다</strong>는 것이다. 사용자 DB를 조회할 필요가 없고, 백엔드와 TURN 서버 사이에 API 호출도 없다. secret 하나만 맞으면 된다. credential이 유출돼도 만료 시각까지만 유효하다.

### Node.js 발급 엔드포인트

```js
// turn-credentials.js
import crypto from 'node:crypto';
import express from 'express';

const TURN_SECRET = process.env.TURN_SECRET;   // coturn static-auth-secret과 같은 값
const TURN_HOST = 'turn.farm.example.com';
const TTL_SEC = 3600;

export function createTurnCredential(userId, ttlSec = TTL_SEC) {
  const expiresAt = Math.floor(Date.now() / 1000) + ttlSec;  // 만료 시각(Unix 초)
  const username = `${expiresAt}:${userId}`;
  const credential = crypto
    .createHmac('sha1', TURN_SECRET)
    .update(username)
    .digest('base64');
  return { username, credential, ttl: ttlSec };
}

const app = express();

// requireAuth: 앱의 기존 인증 미들웨어(운영자 세션 또는 디바이스 인증서)
app.get('/api/turn-credentials', requireAuth, (req, res) => {
  const { username, credential, ttl } = createTurnCredential(req.user.id);
  res.set('Cache-Control', 'no-store');
  res.json({
    ttl,
    iceServers: [
      { urls: `stun:${TURN_HOST}:3478` },
      {
        urls: [
          `turn:${TURN_HOST}:3478?transport=udp`,
          `turn:${TURN_HOST}:3478?transport=tcp`,
          `turns:${TURN_HOST}:443?transport=tcp`,
        ],
        username,
        credential,
      },
    ],
  });
});
```

`req.user.id`가 `operator-42`라면 username은 `1792414800:operator-42` 같은 모양이 된다. 설계 포인트를 정리한다.

- <strong>사용자 ID를 넣어 추적성을 얻는다.</strong> coturn 로그에 username이 남으므로 "어느 운영자·어느 디바이스가 릴레이를 얼마나 썼는가"를 집계할 수 있다. ID에 구분자 `:`가 들어가면 안 된다. coturn은 `rest-api-separator` 옵션으로 구분자를 바꿀 수 있다.
- <strong>secret은 백엔드에만 둔다.</strong> 브라우저나 디바이스 펌웨어에 secret을 넣는 순간 이 패턴의 의미가 사라진다.
- <strong>디바이스도 같은 방식으로 받는다.</strong> 농기계는 IoT 인증서(mTLS)로 백엔드에 인증하고 credential을 받는다([AWS IoT Core 완전 정복](/posts/tech/2025-06-27-iot)). KVS의 `GetIceServerConfig`가 TURN URI·username·password·TTL을 돌려주는 것도 정확히 이 패턴을 관리형으로 제공하는 것이다([18장](/study/webrtc/18-kvs-signaling-api)).
- <strong>시계를 맞춘다.</strong> 만료 시각은 백엔드가 계산하고 TURN 서버가 자기 시계로 판정한다. 두 서버의 NTP 동기화가 틀어지면 갓 발급한 credential이 거부된다.

### TTL은 얼마로

드래프트는 하루(86400초)를 권장하지만 노출 위험을 생각하면 더 짧게 잡는 편이 낫다. 다만 너무 짧으면 장시간 연결에서 문제가 생긴다. 만료 시각이 지나면 새 할당은 거부된다. 진행 중인 할당의 Refresh까지 거부되는지는 서버 구현에 달려 있다. 농기계 모니터링처럼 몇 시간씩 이어지는 세션이라면 다음 중 하나를 택한다.

- TTL을 최대 세션 길이보다 넉넉하게 잡는다.
- ICE restart 전에 credential을 새로 받아 `pc.setConfiguration({ iceServers })`로 교체한다. 이후 restart의 후보 수집은 새 서버 설정을 쓴다.

## 5. coturn 설정과 배치

<strong>coturn</strong>은 가장 널리 쓰이는 오픈소스 TURN 서버다. 여기서는 AWS EC2 한 대에 Elastic IP를 붙여 운영하는 구성을 기준으로 한다.

### 공인 IP와 external-ip

EC2 인스턴스는 자기 NIC에서 사설 IP(예: 172.31.10.20)만 본다. Elastic IP(예: 203.0.113.20)는 VPC 경계에서 1:1 NAT로 변환된다. coturn이 이 사실을 모르면 Allocate 응답의 XOR-RELAYED-ADDRESS에 <strong>사설 IP를 적어 보낸다</strong>. 상대는 그 주소로 보낼 수 없으니 relay 후보가 있어도 relay 쌍이 전부 실패한다. [06장](/study/webrtc/06-ice) 실패 원인 표의 그 증상이다. `external-ip=공인IP/사설IP`로 매핑을 알려줘야 한다.

### 열어야 할 포트

| 포트 | 프로토콜 | 용도 |
|---|---|---|
| 3478 | UDP, TCP | TURN·STUN |
| 443 (또는 5349) | TCP | TURN over TLS |
| 49152~65535 | UDP | relay 포트 범위(`min-port`~`max-port`). 피어가 이 포트로 보낸다 |
| 9641 | TCP | Prometheus 지표(내부망에만) |

relay 포트 범위를 보안 그룹에서 빠뜨리는 실수가 흔하다. Allocate는 성공하는데(3478은 열려 있으니) 미디어가 안 흐르는 증상으로 나타난다.

### turnserver.conf 예시

```ini
# /etc/turnserver.conf — 농기계 원격 영상용 TURN (EC2 + Elastic IP)

# ---------- 리스너 ----------
listening-port=3478
tls-listening-port=443
listening-ip=172.31.10.20
relay-ip=172.31.10.20
# 공인IP/사설IP. 1:1 NAT 뒤(EC2 Elastic IP)라면 필수
external-ip=203.0.113.20/172.31.10.20

# ---------- relay 포트 범위 (기본값과 같음) ----------
min-port=49152
max-port=65535

# ---------- 인증: TURN REST API (시간제한 credential) ----------
# use-auth-secret은 내부적으로 lt-cred-mech를 함께 켠다. 둘을 같이 적지 않는다
use-auth-secret
static-auth-secret=CHANGE_ME_TO_A_LONG_RANDOM_SECRET
realm=turn.farm.example.com
fingerprint
# nonce 수명(초). 값을 생략하면 600
stale-nonce=600

# ---------- TLS ----------
cert=/etc/letsencrypt/live/turn.farm.example.com/fullchain.pem
pkey=/etc/letsencrypt/live/turn.farm.example.com/privkey.pem

# ---------- 남용 방지 ----------
# 서버 전체 동시 할당 상한
total-quota=1200
# 세션당 대역폭 상한(바이트/초). 1250000 = 약 10Mbps
max-bps=1250000
# WebRTC는 TCP relay(RFC 6062)를 쓰지 않는다
no-tcp-relay
no-multicast-peers
# 사설·링크로컬·CGNAT 대역으로의 릴레이 금지 (SSRF 방지)
denied-peer-ip=0.0.0.0-0.255.255.255
denied-peer-ip=10.0.0.0-10.255.255.255
denied-peer-ip=100.64.0.0-100.127.255.255
denied-peer-ip=127.0.0.0-127.255.255.255
denied-peer-ip=169.254.0.0-169.254.255.255
denied-peer-ip=172.16.0.0-172.31.255.255
denied-peer-ip=192.168.0.0-192.168.255.255

# ---------- 관리 인터페이스 ----------
# 4.10 미만에서만 필요. 4.10부터 telnet CLI가 기본 OFF이고 no-cli는 deprecated
no-cli

# ---------- 로그 ----------
log-file=stdout
simple-log
```

주석은 반드시 별도 줄에 둔다. 값 뒤에 붙인 주석은 값의 일부로 읽힐 수 있다. 항목별 의도는 다음과 같다.

- <strong>`use-auth-secret` + `static-auth-secret`</strong>: 4절의 시간제한 credential을 켠다. coturn 예제 설정 주석에 따르면 `use-auth-secret`은 내부적으로 `lt-cred-mech`를 자동으로 켜며, 인증 방식은 한 번에 하나만 쓰라고 안내한다.
- <strong>`realm`</strong>: 401 응답에 실려 클라이언트에 전달되고 long-term 키 계산(`MD5(username:realm:password)`)에 들어간다. 운영 도메인으로 고정한다.
- <strong>`fingerprint`</strong>: TURN 메시지에 FINGERPRINT 속성을 붙인다. coturn 기본값은 off다.
- <strong>`denied-peer-ip`</strong>: 가장 중요한 보안 설정이다. 이것이 없으면 인증받은 사용자가 TURN 서버를 발판 삼아 서버가 속한 VPC 내부 서비스나 <strong>클라우드 메타데이터 엔드포인트(169.254.169.254)</strong>로 패킷을 보낼 수 있다. TURN을 통한 내부망 접근은 실제 서비스에서 보고된 공격 유형이다. 루프백은 coturn이 기본으로 막지만(`allow-loopback-peers`가 기본 off) 사설 대역은 직접 막아야 한다.
- <strong>`max-bps`·`total-quota`</strong>: credential이 유출되거나 클라이언트 버그로 할당이 폭증해도 서버 전체가 무너지지 않게 한다.
- <strong>`no-cli`</strong>: 구버전 coturn은 telnet 관리 CLI(기본 127.0.0.1:5766)를 기본으로 켰다. 4.10.0부터 CLI가 기본 OFF가 됐고, 최신 버전에서 `no-cli`를 쓰면 "deprecated, see --cli" 오류 로그만 남기고 무시된다. 사용 중인 버전을 확인하고 남기거나 지운다.

### 배치와 확장

- <strong>Docker로 띄운다면 host 네트워크 모드</strong>가 일반적이다. relay 포트 수만 개를 `-p`로 하나하나 매핑하는 것은 비현실적이다.
- <strong>할당 수의 상한은 relay 포트 수다.</strong> 49152~65535는 16,384개 포트이므로 relay IP 하나가 동시에 유지할 수 있는 할당도 그 이하다.
- <strong>TURN 서버의 병목은 대개 네트워크다.</strong> 중계만 하므로 CPU보다 인스턴스의 네트워크 대역폭과 초당 패킷 수가 먼저 한계에 닿는다. 인스턴스 타입은 네트워크 성능 기준으로 고른다.
- <strong>사용자 가까이 둔다.</strong> TURN을 거치면 경로가 "디바이스 → TURN → 운영자"로 꺾인다. 한국 농장과 한국 운영자 사이에 해외 리전 TURN을 두면 RTT가 수십~수백 ms 늘어난다.
- <strong>여러 대로 늘릴 때</strong>는 서버마다 독립된 할당 상태를 가지므로 DNS로 분산하거나 백엔드가 응답하는 `iceServers`에 리전별 서버를 넣는다. 모든 서버가 같은 `static-auth-secret`을 공유해야 한다.

### 동작 확인

- <strong>Trickle ICE 샘플 페이지</strong>(webrtc.github.io/samples의 Trickle ICE)에 TURN URL과 credential을 넣고 후보를 수집해 본다. `relay` 타입 후보가 나오면 할당까지는 성공이다.
- coturn에 동봉된 <strong>`turnutils_uclient`</strong>로 할당·중계를 명령줄에서 시험하거나 부하를 걸 수 있다.
- `prometheus` 옵션을 켜면 9641 포트로 지표를 노출한다. 수집과 대시보드는 [관측성 스터디](/study/observability/)의 방법을 그대로 쓴다.

## 6. iceTransportPolicy relay 테스트와 릴레이 비율·비용

### relay 강제 테스트

TURN 설정 오류는 개발 환경에서 드러나지 않는다. 개발자 PC와 테스트 디바이스는 같은 사무실 LAN에 있어 host 후보로 바로 붙기 때문이다. TURN이 고장 나 있어도 아무도 모르다가 현장에서 TURN이 꼭 필요한 사용자만 조용히 연결에 실패한다.

`iceTransportPolicy: 'relay'`는 relay 후보만 쓰게 강제한다. host·srflx 후보는 상대에게 알리지 않는다.

```js
const pc = new RTCPeerConnection({
  iceServers,                    // 4절에서 받은 시간제한 credential
  iceTransportPolicy: 'relay',   // relay 후보만 사용
});

pc.addEventListener('icecandidate', ({ candidate }) => {
  if (candidate && candidate.candidate) {
    console.log(candidate.type, candidate.protocol, candidate.address);  // 전부 relay여야 한다
  }
});
```

이 옵션을 활용하는 방법은 다음과 같다.

- <strong>스테이징 E2E 테스트</strong>에서 relay 강제로 연결·영상 수신까지 확인한다. TURN 서버 배포·인증서 갱신·secret 교체 뒤에 반드시 돌린다.
- <strong>전송별로 쪼개 시험</strong>한다. `urls`에 `turns:...:443?transport=tcp` 하나만 넣고 relay를 강제하면 "TCP 443만 열린 사무실"을 흉내 낼 수 있다.
- <strong>IP 노출을 막는 용도</strong>로도 쓴다. 운영자 IP를 디바이스나 상대 피어에게 드러내고 싶지 않다면 운영 환경에서도 relay를 강제할 수 있다. 대신 모든 트래픽이 TURN을 타므로 아래 비용 계산의 100% 행이 된다.

### 릴레이 비율 측정

실제로 몇 %가 TURN을 타는지는 <strong>측정해야 한다</strong>. 공개된 수치는 출처마다 다르고, 사용자 망 구성에 크게 좌우된다. LTE 라우터와 CGNAT 뒤에 있는 농기계 플릿은 가정용 브로드밴드 위주의 일반 통계와 전혀 다른 값이 나올 수 있다.

연결이 성립하면 선택된 후보 쌍을 뽑아 백엔드로 보낸다.

```js
async function getSelectedPath(pc) {
  const stats = await pc.getStats();
  let pair;
  stats.forEach((r) => {
    if (r.type === 'transport' && r.selectedCandidatePairId) {
      pair = stats.get(r.selectedCandidatePairId);
    }
  });
  if (!pair) {
    // transport 리포트가 없는 브라우저 대비
    stats.forEach((r) => {
      if (r.type === 'candidate-pair' && r.nominated && r.state === 'succeeded') pair = r;
    });
  }
  if (!pair) return null;

  const local = stats.get(pair.localCandidateId);
  const remote = stats.get(pair.remoteCandidateId);
  return {
    localType: local.candidateType,      // host | srflx | prflx | relay
    remoteType: remote.candidateType,
    relayProtocol: local.relayProtocol,  // udp | tcp | tls (로컬이 relay일 때만)
    rttMs: pair.currentRoundTripTime * 1000,
  };
}

pc.addEventListener('connectionstatechange', async () => {
  if (pc.connectionState === 'connected') {
    const path = await getSelectedPath(pc);
    navigator.sendBeacon('/api/webrtc/path', JSON.stringify({ deviceId, ...path }));
  }
});
```

집계 기준은 "로컬이나 원격 중 하나라도 relay인 세션의 비율"이다. `relayProtocol` 분포도 같이 본다. TLS 비율이 높다면 운영자 사무실 망이 엄격하다는 뜻이고, TCP 위 미디어 품질 문제가 같이 나타날 것이다. 연결 도중 ICE restart로 경로가 바뀔 수 있으므로 restart 후에도 다시 보고한다.

### 트래픽 비용 산정

TURN 서버는 받은 만큼 내보낸다. 클라우드는 대개 인바운드를 무료로, 인터넷 방향 아웃바운드(egress)를 GB 단위로 과금한다. 디바이스 → TURN → 운영자 경로라면 영상 바이트만큼이 TURN 서버의 egress가 된다. 양쪽이 모두 relay를 쓰면 트래픽이 TURN을 두 번 지나므로 egress도 최대 두 배가 된다.

```
월 TURN egress(GB) = 월 시청시간(h) × 시간당 영상량(GB/h) × 릴레이 비율 × 경유 배수(1~2)
시간당 영상량(GB/h) = 비트레이트(bps) × 3600 / 8 / 10^9
```

예시로 계산해 보자. <strong>아래 값은 모두 가정</strong>이다. 실제 egress 단가는 클라우드·리전·사용량 구간마다 다르므로 요금표에서 확인한다.

- 농기계 200대, 대당 하루 평균 3시간 시청, 30일 → 월 18,000 시청시간
- 영상 2Mbps(720p H.264 수준 가정) → 시간당 0.9GB → 월 전체 16,200GB
- egress 단가 GB당 $0.09로 가정, 경유 배수 1

| 릴레이 비율 | 월 TURN egress | 월 egress 비용 (가정 단가) |
|---|---|---|
| 5% | 810 GB | 약 $73 |
| 20% | 3,240 GB | 약 $292 |
| 50% | 8,100 GB | 약 $729 |
| 100% (relay 강제) | 16,200 GB | 약 $1,458 |

이 표가 말해 주는 것은 두 가지다. 첫째, <strong>비용은 릴레이 비율에 정비례</strong>한다. relay를 강제하면 P2P 대비 비용이 비율의 역수만큼 커진다. 둘째, <strong>TURN은 디바이스 업링크 사용량을 바꾸지 않는다.</strong> 위 예에서 디바이스 한 대가 월 81GB를 LTE로 올리는 것은 P2P든 TURN이든 같다. TURN 비용은 서버 egress라는 별도 항목이고, LTE 요금은 시청 시간과 비트레이트가 결정한다. 그 위에 TURN 인스턴스 비용이 더해진다.

### 비용을 줄이는 방법

- <strong>시청이 끝나면 즉시 `pc.close()`</strong>한다. 탭을 띄워 둔 채 자리를 비운 운영자가 밤새 relay 트래픽을 쓰는 일이 가장 흔한 낭비다. 화면이 보이지 않으면(`visibilitychange`) 일정 시간 뒤 연결을 끊는 idle 타임아웃을 둔다.
- <strong>relay 경로일 때 비트레이트를 낮춘다.</strong> `getSelectedPath()` 결과가 relay면 `RTCRtpSender.setParameters()`로 `maxBitrate`를 내린다([09장](/study/webrtc/09-quality-latency)). 디바이스 측 송신 설정이라 시그널링으로 요청을 보내 조정한다.
- <strong>UDP 경로를 살린다.</strong> UDP 3478이 막혀 TLS로 밀려나는 운영자 사무실이 많다면 해당 망 관리자에게 TURN 서버 IP·포트 허용을 요청하는 편이 품질과 비용 모두에 낫다.
- <strong>직접 경로 성공률을 높인다.</strong> 디바이스가 STUN 서버를 제대로 쓰는지, ICE restart 뒤에도 srflx 후보가 다시 수집되는지 확인한다. relay는 마지막 수단이어야 한다.
- <strong>관리형 TURN과 비교한다.</strong> KVS WebRTC는 관리형 STUN/TURN을 제공하며 과금 구조가 직접 운영과 다르다. 비교는 [22장](/study/webrtc/22-kvs-operations)에서 다룬다.

::: tip 핵심 정리
- TURN(RFC 8656)은 공인 서버가 릴레이 주소를 빌려주어 어떤 NAT·방화벽에서도 연결을 보장하는 마지막 수단이다. 서버는 암호화된 미디어를 해석하지 않고 바이트 그대로 나른다.
- 흐름은 Allocate → 401(REALM·NONCE) → 서명한 Allocate → 성공(XOR-RELAYED-ADDRESS·LIFETIME 600초) → CreatePermission(IP 단위, 300초) → ChannelBind(0x4000~0x4FFF, 600초) → ChannelData(헤더 4바이트)다. Send/Data indication은 패킷당 36바이트 이상이 붙는다.
- 기본 포트는 3478(UDP·TCP)과 5349(TLS)지만, TCP 443만 열리고 DPI가 있는 망을 뚫으려면 `turns:...:443`이 필요하다. TCP 구간은 head-of-line blocking이 있어 UDP가 우선되게 둔다.
- 브라우저에 건네는 credential은 숨길 수 없으므로 `username=만료시각:사용자ID`, `password=base64(HMAC-SHA1(secret, username))`의 시간제한 credential을 백엔드에서 발급한다.
- coturn은 `external-ip`(1:1 NAT), relay 포트 범위 개방, `use-auth-secret`·`static-auth-secret`·`realm`, 그리고 SSRF를 막는 `denied-peer-ip`가 핵심이다. `no-cli`는 4.10 미만에서만 의미가 있다.
- `iceTransportPolicy: 'relay'`로 TURN 경로를 정기적으로 검증하고, `getStats()`로 릴레이 비율을 측정해 비용(시청시간 × 영상량 × 릴레이 비율 × 경유 배수)을 산정한다.
:::

## 다음 챕터

[RTP/RTCP와 코덱](/study/webrtc/08-rtp-codecs)에서는 ICE와 TURN이 뚫어 놓은 경로 위로 실제 미디어가 어떻게 실려 가는지, 즉 RTP 헤더(SSRC·PT·seq·timestamp)와 RTCP 피드백, 헤더 확장, VP8·VP9·H.264·AV1·Opus 코덱과 패킷화, 지터 버퍼와 립싱크를 다룬다.
