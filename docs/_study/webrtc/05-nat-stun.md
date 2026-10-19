---
title: "NAT와 STUN"
description: "NAT가 P2P 연결을 막는 원리를 RFC 4787의 매핑·필터링 동작으로 분해하고, STUN Binding과 XOR-MAPPED-ADDRESS로 공인 주소를 알아내는 과정, UDP 홀펀칭의 성공 조건, LTE·CGNAT 환경의 디바이스에 TURN이 필요해지는 이유를 다룬다."
date: 2026-10-19
tags: [WebRTC, NAT, STUN, CGNAT]
prev: /study/webrtc/04-sdp-jsep
next: /study/webrtc/06-ice
---

# NAT와 STUN

::: info 학습 목표
- NAT의 매핑 테이블이 왜 "먼저 말을 건 쪽"만 통신하게 만드는지, 그것이 P2P를 어떻게 막는지 이해한다.
- RFC 4787의 매핑 동작(EIM/ADM/APDM)과 필터링 동작(EIF/ADF/APDF)을 구분하고, symmetric NAT에서 STUN 결과가 쓸모없어지는 이유를 설명할 수 있다.
- STUN(RFC 8489) Binding 요청·응답의 구조와 XOR-MAPPED-ADDRESS가 XOR인 이유를 이해한다.
- UDP 홀펀칭의 동작 순서와 NAT 조합별 성공·실패를 판단할 수 있다.
- LTE·CGNAT 위의 디바이스가 왜 TURN을 전제로 설계해야 하는지, 무엇을 측정해야 하는지 안다.
:::

## 1. NAT가 P2P를 막는 이유

[04장](/study/webrtc/04-sdp-jsep)의 SDP에는 포트 `9`, 주소 `0.0.0.0`이라는 자리채움 값만 있었다. 실제로 패킷을 주고받을 주소는 ICE가 따로 찾아 trickle로 보낸다. 이 주소 찾기가 왜 복잡한 문제인지는 NAT를 알아야 이해된다.

IPv4 주소가 모자라면서 대부분의 단말은 RFC 1918 사설 주소(`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`)를 받고, 공유기나 통신사 장비의 <strong>NAT(정확히는 포트까지 바꾸는 NAPT)</strong>를 거쳐 인터넷에 나간다. NAT는 내부 단말이 밖으로 패킷을 보낼 때 출발지를 자기 공인 주소·포트로 바꾸고, 그 대응을 <strong>매핑 테이블</strong>에 기록한다.

| 내부 주소 | 외부(공인) 주소 | 생성 계기 |
|---|---|---|
| `192.168.8.10:5000` | `203.0.113.7:40001` | 내부 단말이 밖으로 UDP를 보냄 |

밖에서 `203.0.113.7:40001`로 패킷이 오면 NAT는 이 표를 보고 `192.168.8.10:5000`으로 돌려준다. 핵심은 <strong>매핑은 안에서 밖으로 보낼 때만 생긴다</strong>는 점이다. 표에 없는 주소·포트로 들어온 패킷은 갈 곳이 없으니 버린다. 매핑이 있더라도 NAT의 필터링 규칙(2절)에 따라 "내가 보낸 적 있는 상대"가 아니면 버리기도 한다.

클라이언트-서버 구조에서는 이것이 문제가 되지 않는다. 클라이언트가 항상 먼저 말을 걸고, 서버는 공인 주소를 갖고 있기 때문이다. 그러나 P2P에서는 양쪽 모두 NAT 뒤에 있다.

![LTE 망의 로봇(192.168.8.10)은 LTE 라우터 NAT(WAN 100.64.12.34)와 통신사 CGN(공인 203.0.113.7)을 거치는 이중 NAT 뒤에 있고, 사무실 망의 운영자 PC(192.168.0.10)는 공유기 NAT(공인 198.51.100.20) 뒤에 있다. 양쪽 모두 인터넷의 STUN 서버로 나가는 outbound는 통과하지만, 공유기 쪽에서 CGN으로 먼저 들어가는 요청 없는 inbound는 폐기된다](/images/study-webrtc/05-nat-topology-light.png)
![LTE 망의 로봇(192.168.8.10)은 LTE 라우터 NAT(WAN 100.64.12.34)와 통신사 CGN(공인 203.0.113.7)을 거치는 이중 NAT 뒤에 있고, 사무실 망의 운영자 PC(192.168.0.10)는 공유기 NAT(공인 198.51.100.20) 뒤에 있다. 양쪽 모두 인터넷의 STUN 서버로 나가는 outbound는 통과하지만, 공유기 쪽에서 CGN으로 먼저 들어가는 요청 없는 inbound는 폐기된다](/images/study-webrtc/05-nat-topology-dark.png)

로봇과 운영자 PC는 서로의 사설 주소를 알아도 쓸 수 없고, 상대의 공인 주소를 알아도 먼저 보내면 상대 NAT에서 버려진다. 서버를 운영하듯 포트 포워딩을 걸면 되지 않느냐고 생각할 수 있지만, LTE 망의 통신사 CGN은 고객이 설정할 수 없고, 현장에 흩어진 수백 대의 농기계 공유기를 하나하나 설정하는 것도 현실적이지 않다. UPnP·PCP 같은 포트 개방 프로토콜도 통신사 CGN에서는 기대하기 어렵다.

그래서 WebRTC는 세 단계 전략을 쓴다.

1. <strong>내 공인 주소 알아내기</strong>: STUN 서버에 물어본다(4절).
2. <strong>양쪽에서 동시에 구멍 뚫기</strong>: 서로의 공인 주소로 동시에 보내 양쪽 NAT에 매핑·허용 규칙을 만든다(5절, UDP 홀펀칭). 이 과정을 체계화한 것이 [06장](/study/webrtc/06-ice)의 ICE다.
3. <strong>안 되면 중계</strong>: 양쪽이 모두 접근할 수 있는 공인 릴레이 서버를 거친다([07장](/study/webrtc/07-turn)의 TURN).

이 전략이 UDP를 기본으로 하는 이유도 여기 있다. UDP는 연결 상태가 없어 "양쪽이 동시에 보내기"만으로 경로가 열리지만, TCP는 SYN 동시 송신(simultaneous open)이 필요해 NAT를 통과시키기가 훨씬 까다롭다.

## 2. RFC 4787 매핑·필터링 동작

### 2.1 cone/symmetric 분류의 한계

예전 STUN 규격(RFC 3489)은 NAT를 full cone, restricted cone, port restricted cone, symmetric 네 가지로 분류했다. 그러나 실제 NAT는 이 넷 중 어디에도 깔끔하게 들어맞지 않는 경우가 많았고, 같은 장비도 상황에 따라 다르게 동작했다. 그래서 RFC 4787(BCP 127, "NAT Behavioral Requirements for Unicast UDP")은 분류 대신 <strong>독립된 동작 축</strong>으로 NAT를 기술한다. 그중 P2P에 결정적인 두 축이 매핑과 필터링이다.

- <strong>매핑(mapping)</strong>: 같은 내부 주소·포트에서 나가는 패킷에 <strong>어떤 외부 주소·포트를 붙이는가</strong>.
- <strong>필터링(filtering)</strong>: 밖에서 들어오는 패킷 중 <strong>무엇을 통과시키는가</strong>.

### 2.2 매핑 동작

내부 단말 `X:x`가 목적지 `Y1:y1`, `Y2:y2`로 차례로 보낼 때 외부 매핑이 어떻게 되는지로 구분한다.

| 매핑 동작 | 외부 매핑 재사용 조건 | 결과 |
|---|---|---|
| Endpoint-Independent Mapping (EIM) | 목적지와 상관없이 같은 내부 `X:x`면 같은 외부 매핑 | STUN 서버가 본 주소를 피어도 그대로 본다 |
| Address-Dependent Mapping (ADM) | 목적지 IP가 같을 때만 재사용 | 목적지 IP가 바뀌면 새 외부 포트 |
| Address and Port-Dependent Mapping (APDM) | 목적지 IP·포트가 모두 같을 때만 재사용 | 목적지마다 새 외부 포트 |

![같은 호스트 10.0.0.2:5000이 NAT(203.0.113.7)를 거쳐 STUN 서버 S:3478과 피어 B:50000으로 보낼 때, EIM에서는 두 목적지 모두 외부 포트 40001을 써서 STUN이 본 포트와 피어가 보는 포트가 같고, APDM에서는 STUN 서버에는 40001, 피어에는 40002를 써서 STUN이 알려준 포트와 다르다](/images/study-webrtc/05-mapping-behavior-light.png)
![같은 호스트 10.0.0.2:5000이 NAT(203.0.113.7)를 거쳐 STUN 서버 S:3478과 피어 B:50000으로 보낼 때, EIM에서는 두 목적지 모두 외부 포트 40001을 써서 STUN이 본 포트와 피어가 보는 포트가 같고, APDM에서는 STUN 서버에는 40001, 피어에는 40002를 써서 STUN이 알려준 포트와 다르다](/images/study-webrtc/05-mapping-behavior-dark.png)

### 2.3 필터링 동작

외부 매핑 `203.0.113.7:40001`이 이미 있다고 할 때, 밖에서 들어오는 패킷을 어떻게 거르는지로 구분한다.

| 필터링 동작 | 통과 조건 | 비유 |
|---|---|---|
| Endpoint-Independent Filtering (EIF) | 매핑만 있으면 누가 보냈든 통과 | 문을 한 번 열면 아무나 들어온다 |
| Address-Dependent Filtering (ADF) | 내부 단말이 <strong>그 IP로</strong> 보낸 적이 있어야 통과 | 내가 연락한 집에서 오는 건 어느 방이든 받는다 |
| Address and Port-Dependent Filtering (APDF) | 내부 단말이 <strong>그 IP·포트로</strong> 보낸 적이 있어야 통과 | 내가 연락한 바로 그 사람만 받는다 |

옛 분류와의 대략적인 대응은 다음과 같다. RFC 4787 자체는 이 대응을 공식화하지 않고 오히려 옛 용어가 부정확하다고 지적하므로, 용어를 읽을 때의 참고 정도로만 쓴다.

| 옛 이름 (RFC 3489) | 매핑 | 필터링 |
|---|---|---|
| Full cone | EIM | EIF |
| Restricted cone | EIM | ADF |
| Port restricted cone | EIM | APDF |
| Symmetric | ADM 또는 APDM | 보통 APDF |

### 2.4 RFC 4787의 주요 요구사항

RFC 4787은 NAT 제조사에 대한 권고(BCP)다. P2P와 관련 깊은 요구사항은 다음과 같다.

| 번호 | 요구사항 | P2P에 주는 의미 |
|---|---|---|
| REQ-1 | NAT는 EIM이어야 한다(MUST) | 이것만 지켜지면 STUN 결과를 피어가 그대로 쓸 수 있다 |
| REQ-3 | 포트 오버로딩(여러 내부 단말이 같은 외부 포트 공유)을 하면 안 된다(MUST NOT) | 매핑이 단말별로 분리된다 |
| REQ-5 | UDP 매핑 타이머는 2분보다 짧게 만료되면 안 되고(MUST NOT), 기본값은 5분 이상이 권장된다 | 그보다 자주 패킷을 보내면 매핑이 유지된다 |
| REQ-6 | 밖으로 나가는 패킷이 매핑 타이머를 갱신해야 한다(MUST) | keepalive는 안에서 밖으로 보내야 효과가 확실하다 |
| REQ-8 | 투명성이 중요하면 EIF, 더 엄격한 필터링이 중요하면 ADF가 권장된다 | APDF는 권장되지 않지만 현실에는 흔하다 |
| REQ-9 | 헤어피닝(같은 NAT 뒤 단말끼리 공인 주소로 통신)을 지원해야 한다(MUST) | 같은 NAT 뒤 두 단말이 공인 주소 후보로도 연결된다 |

중요한 것은 이것이 <strong>권고일 뿐</strong>이라는 점이다. 가정용 공유기는 대체로 EIM을 따르지만, 엔터프라이즈 방화벽과 통신사 CGN 중에는 APDM으로 동작하는 장비가 적지 않다. 디바이스 플랫폼은 최악의 조합을 전제로 설계해야 한다.

## 3. Symmetric NAT

### 3.1 STUN 결과가 쓸모없어지는 이유

Symmetric NAT의 본질은 <strong>endpoint-dependent mapping</strong>(ADM 또는 APDM)이다. 목적지가 바뀌면 외부 매핑도 바뀐다. 위 그림 오른쪽처럼 STUN 서버에 물어서 얻은 `203.0.113.7:40001`은 <strong>STUN 서버로 갈 때만</strong> 쓰이는 매핑이다. 이 주소를 피어에게 알려줘도, 내가 피어에게 실제로 보내는 패킷은 `203.0.113.7:40002`처럼 새 포트에서 나간다. 게다가 대개 APDF가 함께 붙어 있어서, 피어가 `:40001`로 보낸 패킷은 "STUN 서버가 아닌 곳에서 온 패킷"이라 버려진다.

새 포트를 미리 예측하면 되지 않을까? 외부 포트를 1씩 증가시키며 할당하는 단순한 NAT라면 어느 정도 맞힐 수 있다. 하지만 같은 순간 다른 단말도 포트를 쓰고, CGN은 수많은 가입자가 포트를 나눠 쓰는 데다 RFC 6888은 CGN이 포트 번호를 추측하기 어렵게 할당할 것을 목표로 제시한다. ICE 표준도 포트 예측을 하지 않는다. 결국 symmetric NAT 뒤의 단말은 <strong>상대 NAT가 관대하면 운 좋게 연결되고, 아니면 TURN</strong>이다(5절의 표).

### 3.2 내 NAT가 symmetric인지 확인하기

가장 간단한 방법은 <strong>같은 UDP 소켓</strong>에서 IP가 다른 STUN 서버 두 곳에 Binding을 보내고 돌아온 매핑 포트를 비교하는 것이다. 포트가 같으면 EIM, 다르면 endpoint-dependent mapping이다. 다음 Node.js 스크립트는 외부 라이브러리 없이 4절의 STUN 메시지를 직접 만들어 보낸다.

```javascript
// stun-probe.mjs — compare mapped addresses from two STUN servers on one socket
import dgram from "node:dgram";
import crypto from "node:crypto";

const MAGIC = 0x2112a442;
const SERVERS = [
  ["stun.l.google.com", 19302],
  ["stun.cloudflare.com", 3478],
];

function bindingRequest() {
  const msg = Buffer.alloc(20);
  msg.writeUInt16BE(0x0001, 0);       // Binding Request
  msg.writeUInt16BE(0, 2);            // no attributes
  msg.writeUInt32BE(MAGIC, 4);        // magic cookie
  const tid = crypto.randomBytes(12); // 96-bit transaction ID
  tid.copy(msg, 8);
  return { msg, tid };
}

function parseXorMappedAddress(buf, tid) {
  if (buf.readUInt16BE(0) !== 0x0101) return null;        // Binding Success Response
  if (!buf.subarray(8, 20).equals(tid)) return null;       // transaction ID must match
  let off = 20;
  const end = 20 + buf.readUInt16BE(2);
  while (off + 4 <= end) {
    const type = buf.readUInt16BE(off);
    const len = buf.readUInt16BE(off + 2);
    if (type === 0x0020 && buf[off + 5] === 0x01) {        // XOR-MAPPED-ADDRESS, IPv4
      const port = buf.readUInt16BE(off + 6) ^ (MAGIC >>> 16);
      const ip = (buf.readUInt32BE(off + 8) ^ MAGIC) >>> 0;
      return `${ip >>> 24}.${(ip >>> 16) & 255}.${(ip >>> 8) & 255}.${ip & 255}:${port}`;
    }
    off += 4 + Math.ceil(len / 4) * 4;                     // attributes are 32-bit aligned
  }
  return null;
}

const sock = dgram.createSocket("udp4");
sock.bind(0, async () => {
  console.log("local port", sock.address().port);
  for (const [host, port] of SERVERS) {
    const { msg, tid } = bindingRequest();
    const mapped = await new Promise((resolve) => {
      const timer = setTimeout(() => resolve("timeout"), 3000);
      sock.once("message", (buf) => { clearTimeout(timer); resolve(parseXorMappedAddress(buf, tid)); });
      sock.send(msg, port, host);
    });
    console.log(`${host}:${port} -> mapped ${mapped}`);
  }
  sock.close();
});
```

가정용 공유기 뒤에서 실행한 결과는 다음과 같은 형태다(주소는 문서용 예시로 바꿨다). 두 서버가 본 매핑이 같고 내부 포트까지 보존됐으니 EIM이다.

```text
local port 59835
stun.l.google.com:19302 -> mapped 203.0.113.7:59835
stun.cloudflare.com:3478 -> mapped 203.0.113.7:59835
```

같은 스크립트를 symmetric 성향의 망에서 돌리면 두 줄의 포트가 다르게 나온다. 이 방법은 매핑만 본다. 필터링까지 판별하려면 응답을 다른 IP·포트에서 보내 달라고 요청하는 RFC 5780(NAT Behavior Discovery, Experimental)의 `CHANGE-REQUEST`·`OTHER-ADDRESS` 속성을 지원하는 STUN 서버가 필요하다.

::: tip 디바이스 부팅 시 NAT 진단
이 스크립트와 같은 로직을 디바이스 에이전트에 넣어 부팅·망 전환 때마다 실행하고, 결과(매핑 동일 여부, 공인 IP)를 텔레메트리로 백엔드에 올려 두면 "이 농기계는 왜 늘 릴레이로 붙는가"를 나중에 데이터로 설명할 수 있다. 텔레메트리 채널로는 MQTT가 자연스럽다([MQTT 프로토콜과 AWS IoT 적용](/posts/tech/2025-08-13-mqtt)).
:::

## 4. STUN: Binding 요청과 XOR-MAPPED-ADDRESS

### 4.1 STUN이란

<strong>STUN(Session Traversal Utilities for NAT)</strong>의 현재 규격은 RFC 8489(2020년, RFC 5389 대체)다. 이름에 Utilities가 들어간 것처럼 STUN은 하나의 완결된 NAT 통과 해법이 아니라 <strong>도구 상자</strong>다. 메시지 형식, 트랜잭션, 인증, 속성(attribute) 체계를 정의하고, 이를 ICE([06장](/study/webrtc/06-ice))와 TURN([07장](/study/webrtc/07-turn))이 가져다 쓴다. 이 장에서는 가장 기본 기능인 <strong>Binding</strong>, 즉 "내가 밖에서 어떤 주소로 보이는가"를 묻는 기능만 본다.

기본 포트는 UDP·TCP 모두 3478이고, TLS·DTLS 위의 STUN은 5349다.

### 4.2 메시지 구조

모든 STUN 메시지는 20바이트 헤더와 0개 이상의 속성으로 이뤄진다.

| 필드 | 크기 | 값 / 의미 |
|---|---|---|
| Message Type | 2바이트 | 상위 2비트는 항상 0. 나머지 14비트에 메서드(Binding = 0x001)와 클래스(요청·인디케이션·성공 응답·오류 응답)를 섞어 담는다. Binding Request = `0x0001`, Binding Success Response = `0x0101` |
| Message Length | 2바이트 | 헤더 20바이트를 뺀 속성 부분의 길이. 속성은 4바이트 단위로 정렬되므로 항상 4의 배수다 |
| Magic Cookie | 4바이트 | 고정값 `0x2112A442` |
| Transaction ID | 12바이트 | 96비트 난수. 요청과 응답을 짝짓는다 |

상위 2비트가 0이고 Magic Cookie가 고정값이라는 점은 실전에서 중요하다. WebRTC는 BUNDLE과 rtcp-mux 덕분에 <strong>UDP 포트 하나</strong>로 STUN, DTLS, SRTP/SRTCP를 모두 받는다([04장](/study/webrtc/04-sdp-jsep)). 수신 측은 첫 바이트 값만 보고 갈래를 나눈다. RFC 7983에 따르면 0~3은 STUN, 20~63은 DTLS, 64~79는 TURN ChannelData, 128~191은 RTP/RTCP다.

UDP는 패킷이 사라질 수 있으므로 클라이언트가 직접 재전송한다. RFC 8489의 기본값은 초기 RTO 500ms 이상, 최대 7번 송신(Rc=7)이며 간격을 두 배씩 늘린다. RTO가 500ms라면 0, 500, 1500, 3500, 7500, 15500, 31500ms에 보내고, 마지막 송신 후 RTO의 16배(Rm=16)를 더 기다려 39.5초에 트랜잭션 실패로 판단한다.

### 4.3 Binding 흐름

![클라이언트(10.0.0.2:5000)가 TID=t1인 Binding Request를 보내면 NAT(공인 203.0.113.7)가 IP/UDP 헤더의 출발지만 203.0.113.7:40001로 재작성해 STUN 서버(198.51.100.1:3478)에 전달한다. STUN 서버는 보이는 출발지 203.0.113.7:40001을 매직 쿠키와 XOR해 XOR-MAPPED-ADDRESS에 담은 Binding Success를 돌려주고, NAT는 목적지만 10.0.0.2:5000으로 되돌리며 페이로드는 그대로 둔다. 중간 ALG가 공인 IP 바이트열을 찾아도 XOR 값이라 매칭되지 않으며, 클라이언트는 XOR을 풀어 srflx 주소 203.0.113.7:40001을 얻는다](/images/study-webrtc/05-stun-binding-light.png)
![클라이언트(10.0.0.2:5000)가 TID=t1인 Binding Request를 보내면 NAT(공인 203.0.113.7)가 IP/UDP 헤더의 출발지만 203.0.113.7:40001로 재작성해 STUN 서버(198.51.100.1:3478)에 전달한다. STUN 서버는 보이는 출발지 203.0.113.7:40001을 매직 쿠키와 XOR해 XOR-MAPPED-ADDRESS에 담은 Binding Success를 돌려주고, NAT는 목적지만 10.0.0.2:5000으로 되돌리며 페이로드는 그대로 둔다. 중간 ALG가 공인 IP 바이트열을 찾아도 XOR 값이라 매칭되지 않으며, 클라이언트는 XOR을 풀어 srflx 주소 203.0.113.7:40001을 얻는다](/images/study-webrtc/05-stun-binding-dark.png)

1. 클라이언트가 속성 없는 Binding Request를 STUN 서버로 보낸다. 이 순간 NAT에 매핑이 생긴다.
2. STUN 서버는 받은 패킷의 IP/UDP 헤더에서 출발지 주소를 읽는다. 이것이 NAT가 붙인 외부 매핑이다.
3. 서버는 이 주소를 <strong>XOR-MAPPED-ADDRESS</strong> 속성에 담아 Binding Success Response로 돌려준다.
4. 클라이언트는 같은 Transaction ID인지 확인하고 XOR을 풀어 자기 공인 주소를 얻는다.

이렇게 얻은 주소가 ICE의 <strong>server reflexive(srflx) 후보</strong>다. "서버에 반사돼 보인 내 주소"라는 뜻이다.

### 4.4 XOR-MAPPED-ADDRESS가 XOR인 이유

XOR-MAPPED-ADDRESS(속성 타입 `0x0020`)는 주소를 그대로 담지 않고 섞어서 담는다.

- X-Port = 매핑 포트 XOR Magic Cookie의 상위 16비트(`0x2112`)
- X-Address(IPv4) = 매핑 IP XOR Magic Cookie(`0x2112A442`)
- X-Address(IPv6) = 매핑 IP XOR (Magic Cookie ‖ Transaction ID 96비트)

예를 들어 `203.0.113.7:40001`이면 포트는 `0x9C41 ⊕ 0x2112 = 0xBD53`(48467), IP는 `0xCB007107 ⊕ 0x2112A442 = 0xEA12D545`, 즉 `234.18.213.69`로 실린다. 패킷을 덤프해 보면 엉뚱한 주소처럼 보이는 이유다.

왜 이렇게 번거롭게 할까? RFC 8489는 배포 경험상 일부 NAT가 "선의로, 그러나 잘못된 방식으로 범용 ALG(Application Layer Gateway) 기능을 제공하려고" 페이로드 안에서 <strong>자기 공인 IP와 같은 32비트 값</strong>을 찾아 사설 IP로 바꿔 버리는 일이 있었다고 설명한다. 원래 SIP 같은 프로토콜의 본문 속 주소를 고쳐 주려는 기능인데, STUN 응답에 들어 있는 "당신의 공인 주소"까지 사설 주소로 되돌려 놓으니 STUN이 무의미해진다. XOR로 섞어 두면 NAT가 바이트열에서 자기 공인 IP를 찾을 수 없으므로 응답이 변조되지 않는다.

옛 형식인 MAPPED-ADDRESS(속성 타입 `0x0001`)는 주소를 평문으로 담는다. RFC 3489 구현과의 호환을 위해 남아 있을 뿐, 클라이언트는 XOR-MAPPED-ADDRESS를 우선 읽어야 한다. 위 Node.js 스크립트도 `0x0020`만 해석한다.

### 4.5 브라우저에서 srflx 후보 보기

브라우저에서는 `iceServers`에 STUN 서버를 넣기만 하면 ICE 에이전트가 Binding을 대신 수행한다.

```javascript
const pc = new RTCPeerConnection({
  iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
});
pc.onicecandidate = ({ candidate }) => {
  if (candidate) console.log(candidate.type, candidate.address, candidate.port);
};
pc.createDataChannel("probe");   // need at least one m-section to gather
await pc.setLocalDescription();
```

이때 나오는 srflx 후보의 SDP 표현은 다음과 같은 형태다(값은 예시).

```text
candidate:1467250027 1 udp 1686052607 203.0.113.7 40001 typ srflx raddr 0.0.0.0 rport 0 generation 0 ufrag UioA
```

`typ srflx` 뒤의 `raddr`/`rport`는 이 주소의 기반이 된 로컬 주소(관련 주소)인데, 브라우저는 사설 IP 노출을 줄이려고 이를 `0.0.0.0`으로 가리기도 한다. 우선순위 값(`1686052607`)이 어떻게 계산되는지는 [06장](/study/webrtc/06-ice)에서 본다.

여기서 쓰는 Binding은 인증이 없는 단순 요청이다. ICE가 피어끼리 주고받는 연결 검사(connectivity check)도 같은 Binding 메시지지만, [04장](/study/webrtc/04-sdp-jsep)의 `ice-ufrag`/`ice-pwd`로 만든 USERNAME·MESSAGE-INTEGRITY 속성과 PRIORITY 등 ICE 전용 속성이 붙는다.

::: warning 공개 STUN 서버는 테스트용이다
`stun.l.google.com:19302` 같은 공개 STUN 서버는 편리하지만 SLA가 없다. 운영 환경에서는 TURN 서버(coturn 등)가 STUN 기능도 함께 제공하므로 자체 TURN을 배치하거나([07장](/study/webrtc/07-turn)), KVS처럼 관리형 STUN/TURN을 제공하는 서비스를 쓴다([17장](/study/webrtc/17-kvs-architecture)).
:::

## 5. UDP 홀펀칭

### 5.1 동작 순서

양쪽이 STUN으로 srflx 주소를 알아내고 시그널링으로 교환했다면, 이제 서로의 srflx로 동시에 패킷을 보낸다. 이것이 <strong>UDP 홀펀칭(hole punching)</strong>이다. 핵심은 "내가 상대에게 보낸 기록"이 내 NAT의 필터링 규칙을 열어 준다는 점이다.

![피어 A(로봇)와 피어 B(운영자)가 STUN으로 srflx를 확인하고 시그널링으로 후보를 교환한 뒤, 1단계에서 A가 B의 srflx로 보내면 NAT A에 B로 보낸 기록이 남지만 NAT B는 B가 먼저 보낸 적이 없어 폐기한다. 2단계에서 B가 A의 srflx로 보내면 NAT B에 기록이 남고 NAT A는 1단계 기록 덕에 통과시킨다. 3단계에서 A가 다시 보내면 NAT B도 통과해 양방향 UDP 경로가 확보되고 ICE connectivity check가 성공한다](/images/study-webrtc/05-hole-punching-light.png)
![피어 A(로봇)와 피어 B(운영자)가 STUN으로 srflx를 확인하고 시그널링으로 후보를 교환한 뒤, 1단계에서 A가 B의 srflx로 보내면 NAT A에 B로 보낸 기록이 남지만 NAT B는 B가 먼저 보낸 적이 없어 폐기한다. 2단계에서 B가 A의 srflx로 보내면 NAT B에 기록이 남고 NAT A는 1단계 기록 덕에 통과시킨다. 3단계에서 A가 다시 보내면 NAT B도 통과해 양방향 UDP 경로가 확보되고 ICE connectivity check가 성공한다](/images/study-webrtc/05-hole-punching-dark.png)

1. A가 B의 srflx로 보낸다. A의 NAT에는 "B로 보냈다"는 기록이 생긴다. B의 NAT는 B가 아직 A에게 보낸 적이 없으므로 이 패킷을 버린다. <strong>첫 패킷이 버려지는 것은 정상</strong>이다.
2. B가 A의 srflx로 보낸다. B의 NAT에 기록이 생기고, A의 NAT는 1단계 기록 덕분에 통과시킨다.
3. A가 다시 보내면 이번에는 B의 NAT도 통과시킨다. 이제 양방향 경로가 열렸다.

실제로는 애플리케이션이 이 순서를 직접 조율하지 않는다. ICE 에이전트가 모든 후보 쌍에 대해 양쪽에서 STUN Binding 연결 검사를 재전송하며 보내므로, 위 과정이 자연스럽게 일어난다. 연결 검사 도중 예상하지 못한 주소에서 요청이 오면 그 주소를 새 후보로 받아들이는데, 이것이 <strong>peer reflexive(prflx) 후보</strong>다. symmetric NAT 쪽에서 새로 만든 매핑이 이렇게 발견된다([06장](/study/webrtc/06-ice)).

### 5.2 NAT 조합별 성공·실패

양쪽 NAT 동작에 따라 홀펀칭 결과가 갈린다. 아래 표는 양쪽이 srflx를 교환하고 동시에 보낸다고 가정한 결과다. "EDM"은 endpoint-dependent mapping(ADM·APDM), 즉 symmetric 계열이다.

| A \ B | EIM + EIF | EIM + ADF | EIM + APDF | EDM (symmetric) |
|---|---|---|---|---|
| <strong>EIM + EIF</strong> | 성공 | 성공 | 성공 | 성공 (prflx) |
| <strong>EIM + ADF</strong> | 성공 | 성공 | 성공 | 성공 (B NAT가 같은 공인 IP를 쓸 때) |
| <strong>EIM + APDF</strong> | 성공 | 성공 | 성공 | <strong>실패 → TURN</strong> |
| <strong>EDM (symmetric)</strong> | 성공 (prflx) | 조건부 성공 | <strong>실패 → TURN</strong> | <strong>실패 → TURN</strong> |

왜 이렇게 되는지 경우별로 보면 다음과 같다.

- <strong>양쪽 EIM</strong>: 각자 STUN이 알려준 주소가 피어에게도 그대로 쓰인다. 필터링이 무엇이든 양쪽이 서로의 정확한 주소·포트로 보내므로 5.1의 순서대로 열린다.
- <strong>EIM + EIF/ADF 대 symmetric</strong>: symmetric 쪽 B가 A의 srflx로 보낼 때 B의 NAT는 새 포트(`:p'`)를 쓴다. A의 NAT가 EIF면 무조건, ADF면 B의 IP로 보낸 기록이 있으니 통과시킨다. A는 처음 보는 `B:p'`에서 온 요청을 prflx로 받아들이고 그 주소로 응답하는데, B의 NAT는 `:p'` 매핑을 정확히 A를 향해 만들었으므로 응답도 통과한다. ADF의 경우 B의 NAT가 새 매핑에도 같은 공인 IP를 써야 하는데, RFC 4787이 권장하고 RFC 6888이 CGN 기본값으로 요구하는 "paired" 주소 풀링이 바로 이 동작이다.
- <strong>EIM + APDF 대 symmetric</strong>: A의 NAT는 `B:p`(STUN이 알려준 포트)로 보낸 기록만 있고, B는 `B:p'`에서 보낸다. 포트가 다르니 버려진다. A는 `p'`를 알 방법이 없다.
- <strong>symmetric 대 symmetric</strong>: 양쪽 모두 상대에게 실제로 쓸 매핑을 미리 알 수 없다. 포트 예측 없이는 불가능하다.

실패 칸은 모두 TURN 릴레이로 간다. 실무에서 "P2P가 안 되는 비율"은 결국 이 표의 실패 칸에 해당하는 사용자 비율이다.

::: details 같은 NAT 뒤의 두 피어
같은 농장의 LTE 라우터에 붙은 로봇 두 대, 또는 같은 사무실의 운영자 두 명처럼 같은 NAT 뒤의 피어는 보통 host 후보(사설 주소)끼리 바로 연결된다. VLAN이 나뉘어 사설 주소끼리 닿지 않는다면 srflx 후보로 NAT를 한 바퀴 돌아 연결해야 하는데, 이때 NAT가 헤어피닝(RFC 4787 REQ-9)을 지원해야 한다. 지원하지 않으면 같은 건물 안인데도 TURN으로 붙는 기묘한 상황이 생긴다.
:::

## 6. CGNAT·LTE 환경 — 디바이스 관점

### 6.1 CGN이 끼면 무엇이 달라지나

LTE로 연결된 농기계·로봇은 거의 예외 없이 <strong>CGN(Carrier-Grade NAT, CGNAT)</strong> 뒤에 있다. 통신사가 가입자 단말에 사설 또는 공유 주소를 주고, 통신사 코어의 대형 NAT가 공인 IPv4 주소 하나를 수많은 가입자가 나눠 쓰게 만든다. 이를 위해 RFC 6598은 `100.64.0.0/10`을 CGN 전용 <strong>공유 주소 공간(Shared Address Space)</strong>으로 예약했다. 디바이스나 LTE 라우터의 WAN 주소가 `100.64.x.x`~`100.127.x.x` 범위라면 CGN 뒤에 있다는 강력한 신호다. LTE 라우터 뒤에 다시 디바이스가 붙으면 1절 그림처럼 <strong>이중 NAT</strong>가 된다.

CGN의 요구사항을 정리한 RFC 6888은 다음을 요구한다.

| 요구사항 | 내용 | 디바이스에 주는 의미 |
|---|---|---|
| REQ-1 | 전송 프로토콜별 동작 요구사항을 따라야 한다. UDP는 RFC 4787 | 원칙적으로는 EIM이어야 한다 |
| REQ-2 | 주소 풀링 기본값은 "paired"(같은 가입자는 같은 공인 IP) | 매핑마다 공인 IP가 바뀌는 최악은 피한다 |
| REQ-4 | 가입자별 외부 포트 수를 제한할 수 있어야 한다 | 디바이스 하나가 쓸 수 있는 동시 매핑 수에 상한이 있다 |
| 5절(포트 할당) | 포트 활용 극대화, 로그량 최소화, 포트 번호 추측 곤란을 목표로 제시 | 포트 예측 기반 홀펀칭은 기대할 수 없다 |

원칙은 이렇지만 현실의 모바일 망 CGN과 LTE 라우터가 모두 이 권고를 따르지는 않는다. endpoint-dependent mapping(symmetric) 성향의 동작이 모바일 망에서 흔히 관찰되고, 이중 NAT라면 두 NAT 중 <strong>더 엄격한 쪽의 동작</strong>이 전체 동작을 결정한다. 둘 중 하나라도 symmetric이면 전체가 symmetric이다. 통신사·요금제·지역·장비 펌웨어마다 결과가 다르고 시간이 지나면 바뀌기도 하므로, "우리 디바이스는 P2P로 붙는다"를 가정해서는 안 된다.

### 6.2 그래서 TURN을 전제로 설계한다

5.2의 표를 원격 운영 시나리오에 대입해 보자. 로봇은 LTE CGN 뒤(symmetric 성향), 운영자는 회사 방화벽 뒤(APDF이거나 아예 UDP를 막는 경우도 있음)다. 표의 실패 칸에 해당할 확률이 상당히 높다. 따라서 디바이스 플랫폼은 다음을 기본값으로 둔다.

- <strong>TURN 서버를 항상 `iceServers`에 넣는다.</strong> STUN만으로 운영하면 일부 사용자는 영원히 연결되지 않는다.
- <strong>UDP가 막힌 망을 대비해 TURN over TCP/TLS(443)를 함께 제공한다.</strong> 회사 방화벽은 443 TCP만 열어 두는 경우가 많다([07장](/study/webrtc/07-turn)).
- <strong>릴레이 비용을 예산에 넣는다.</strong> 릴레이로 붙으면 영상 트래픽 전량이 TURN 서버를 지나간다. 디바이스 업링크 대역폭 × 시청 시간 × 릴레이 비율이 곧 TURN 트래픽이다.
- <strong>뷰어 수를 제한한다.</strong> P2P 구조에서는 뷰어마다 PeerConnection이 하나씩 생기고, 그만큼 NAT 매핑·TURN 할당·업링크 대역폭이 늘어난다. KVS WebRTC가 P2P라 뷰어 수만큼 업링크가 배수가 된다는 점은 [16장](/study/webrtc/16-aws-landscape)에서 다시 다룬다.

### 6.3 매핑 타이머와 keepalive

NAT 매핑은 일정 시간 패킷이 없으면 사라진다. RFC 4787은 UDP 매핑 타이머를 2분 이상으로 요구하지만, 모바일 망에서는 이보다 짧은 타이머를 쓰는 장비도 보고된다. 매핑이 사라지면 영상이 끊기고, 다음 패킷은 새 외부 포트로 나가 상대가 알아보지 못한다.

연결된 뒤에는 WebRTC가 알아서 매핑을 유지한다. ICE의 <strong>consent freshness(RFC 7675)</strong>가 선택된 후보 쌍으로 평균 5초(0.8~1.2배 무작위화, 최소 4초)마다 STUN Binding 요청을 보내고, 30초 동안 응답이 없으면 연결을 끊는다. RFC 7675는 이 요청이 NAT 매핑 keepalive 역할도 한다고 명시한다. 영상이 멈춰 있는 동안에도 이 요청은 계속 흐른다.

신경 써야 할 것은 <strong>시그널링 연결</strong>이다. 디바이스가 시청 요청을 기다리며 WebSocket을 열어 두는 동안 트래픽이 없으면 CGN이 TCP 매핑을 정리할 수 있다. 시그널링 클라이언트는 ping 주기를 망에서 실측한 유휴 타임아웃보다 짧게 잡고, 끊기면 지수 백오프로 재연결해야 한다([03장](/study/webrtc/03-signaling), [WebSocket 과 SSE](/posts/tech/2025-07-20-ssewebsocket)). LTE와 Wi-Fi를 오가는 디바이스라면 망 전환 직후 공인 주소 자체가 바뀌므로 ICE restart가 필요하다([06장](/study/webrtc/06-ice)).

### 6.4 IPv6는 탈출구인가

모바일 망은 IPv6를 할당하는 경우가 많다. IPv6에는 NAT가 없으므로 양쪽이 모두 IPv6를 가지면 host 후보끼리 직접 연결될 가능성이 생긴다. ICE는 IPv4·IPv6 후보를 모두 모아 검사하므로 별도 작업 없이 이 혜택을 본다. 다만 NAT가 없을 뿐 통신사·가정용 장비의 <strong>상태 기반 방화벽</strong>은 여전히 요청 없는 inbound를 막을 수 있고, 운영자 쪽 망이 IPv6를 지원하지 않으면 소용이 없다. "되면 좋은 보너스"로 보고, 설계는 IPv4 + TURN을 기준으로 한다.

### 6.5 측정: 실제로 어떤 경로로 붙었나

설계의 근거는 측정이다. 연결이 맺어진 뒤 `getStats()`로 선택된 후보 쌍의 타입을 읽어 백엔드로 보내면, 디바이스별·통신사별 릴레이 비율을 집계할 수 있다.

```javascript
async function selectedPath(pc) {
  const stats = await pc.getStats();
  let pair;
  stats.forEach((r) => {
    if (r.type === "transport" && r.selectedCandidatePairId) {
      pair = stats.get(r.selectedCandidatePairId);
    }
  });
  if (!pair) {
    // Fallback for browsers that expose a non-standard `selected` flag (Firefox)
    stats.forEach((r) => {
      if (r.type === "candidate-pair" && r.selected) pair = r;
    });
  }
  if (!pair) return null;
  const local = stats.get(pair.localCandidateId);
  const remote = stats.get(pair.remoteCandidateId);
  return {
    local: local.candidateType,    // host | srflx | prflx | relay
    remote: remote.candidateType,
    protocol: local.protocol,      // udp | tcp
    relayProtocol: local.relayProtocol, // udp | tcp | tls (relay only)
    rttMs: pair.currentRoundTripTime * 1000,
  };
}
```

`local` 또는 `remote`가 `relay`면 TURN을 거친 연결이다. 이 값을 3.2절의 부팅 시 NAT 진단 결과와 함께 모으면 "이 통신사 망의 디바이스는 대부분 릴레이로 붙는다" 같은 운영 판단을 숫자로 내릴 수 있다. getStats 지표 전반은 [15장](/study/webrtc/15-monitoring-debugging)에서 다룬다.

::: tip 핵심 정리
- NAT 매핑은 안에서 밖으로 보낼 때만 생기고, 요청 없는 inbound는 버려진다. 양쪽이 모두 NAT 뒤에 있는 P2P는 이 때문에 그냥은 연결되지 않는다.
- RFC 4787은 NAT를 매핑(EIM/ADM/APDM)과 필터링(EIF/ADF/APDF)이라는 독립된 축으로 기술한다. EIM을 요구(MUST)하지만 권고일 뿐이고 현실에는 APDM·APDF가 흔하다.
- symmetric NAT(endpoint-dependent mapping)에서는 STUN이 알려준 주소가 STUN 서버를 향한 매핑일 뿐이라 피어에게는 쓸모가 없다.
- STUN(RFC 8489) Binding은 20바이트 헤더(타입·길이·매직 쿠키 0x2112A442·96비트 Transaction ID)로 "밖에서 보이는 내 주소"를 묻는다. XOR-MAPPED-ADDRESS는 페이로드 속 공인 IP를 고쳐 쓰는 ALG를 피하려고 주소를 매직 쿠키와 XOR한다.
- UDP 홀펀칭은 양쪽이 서로의 srflx로 동시에 보내 각자의 NAT에 허용 기록을 남기는 기법이고, EIM끼리는 성공하지만 symmetric 대 APDF·symmetric 대 symmetric은 실패해 TURN으로 간다.
- LTE 디바이스는 CGN(100.64.0.0/10)·이중 NAT 뒤에 있어 symmetric 성향이 흔하다. TURN(UDP + TCP/TLS 443)을 기본으로 두고, keepalive와 망 전환 시 ICE restart를 챙기고, 선택된 후보 쌍 타입을 측정해 릴레이 비율을 관리한다.
:::

## 다음 챕터

[ICE](/study/webrtc/06-ice)에서는 이 장의 재료(host·srflx 후보, STUN 연결 검사, 홀펀칭)를 하나의 절차로 엮는 ICE를 다룬다. 후보 종류와 우선순위 공식, 후보 쌍과 연결 검사·nomination, Trickle ICE와 ICE restart, mDNS 후보와 ICE-lite, 그리고 연결 실패의 흔한 원인까지 살펴본다.
