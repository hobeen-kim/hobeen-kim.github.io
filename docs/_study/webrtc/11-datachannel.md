---
title: "DataChannel"
description: "SCTP over DTLS 위에서 동작하는 DataChannel의 스택과 DCEP, 신뢰성·순서 옵션 조합, negotiated 채널, 메시지 크기 한계와 bufferedAmount 흐름 제어, 농기계·로봇 원격 제어 명령 채널 설계(시퀀스·데드맨·워치독), MQTT(AWS IoT Core)와의 역할 분담을 다룬다."
date: 2026-10-19
tags: [WebRTC, DataChannel, SCTP, RemoteControl]
prev: /study/webrtc/10-dtls-srtp
next: /study/webrtc/12-topology-sfu
---

# DataChannel

::: info 학습 목표
- DataChannel이 SCTP / DTLS / ICE / UDP 스택 위에서 동작하는 구조와 DCEP의 역할을 이해한다.
- `ordered`·`maxRetransmits`·`maxPacketLifeTime` 조합이 만드는 전달 의미론을 구분하고 용도에 맞게 고른다.
- `negotiated: true` + `id` 방식과 in-band(DCEP) 방식의 차이와 쓰임새를 안다.
- 메시지 크기 한계(`maxMessageSize`, 16KiB 권장 근거)와 `bufferedAmount` 흐름 제어를 코드로 구현한다.
- 원격 제어 명령 채널을 시퀀스 번호·데드맨 스위치·워치독으로 안전하게 설계하고, MQTT(AWS IoT Core)와 역할을 나눈다.
:::

## 1. 스택: SCTP over DTLS

### 왜 SCTP인가

DataChannel은 영상이 오가는 그 연결 위에서 임의의 바이트를 주고받는 통로다. 요구사항을 적어 보면 기존 전송 프로토콜 중 딱 맞는 것이 없다.

- <strong>여러 독립 채널</strong>: 제어 명령, 텔레메트리, 파일 전송이 서로를 막지 않아야 한다. TCP는 바이트 스트림 하나라서 한 채널의 손실이 전부를 멈춘다(head-of-line blocking).
- <strong>메시지 경계</strong>: 앱은 "메시지" 단위로 주고받고 싶다. TCP는 경계가 없다.
- <strong>신뢰성을 골라 쓰기</strong>: 파일은 반드시 도착해야 하지만 조이스틱 값은 늦게 오면 쓸모없다. TCP는 항상 신뢰성 모드고, UDP는 항상 비신뢰성 모드다.
- <strong>혼잡 제어</strong>: 날것의 UDP로 보내면 망을 망가뜨릴 수 있다.

SCTP(RFC 4960)는 이 요구를 한 번에 만족한다. 한 연결(association) 안에 최대 65535개 스트림을 두고, 메시지 경계를 보존하며, 혼잡 제어를 내장한다. 부분 신뢰성 확장(RFC 3758)과 재전송 횟수 제한 정책(RFC 7496)으로 메시지마다 신뢰성을 고를 수도 있다. 원래 통신망 시그널링용 커널 프로토콜이지만 NAT·방화벽을 거의 통과하지 못한다. 그래서 WebRTC는 SCTP를 <strong>DTLS 안에 넣어</strong>(RFC 8261) 보낸다. 브라우저는 사용자 공간 SCTP 구현을 내장하고 있다.

![한 피어 안의 프로토콜 스택. 미디어 열은 MediaStreamTrack → RTP/RTCP → SRTP/SRTCP, 데이터 열은 RTCDataChannel API → DCEP(PPID 50)와 사용자 메시지(PPID 51·53) → SCTP(스트림·부분 신뢰성·혼잡 제어) → DTLS로 내려가고, DTLS에서 SRTP로 키 도출(exporter) 화살표가 이어지며, 두 열 모두 하나의 후보 쌍·하나의 5-tuple을 쓰는 ICE → UDP로 합쳐지는 구조](/images/study-webrtc/11-stack-light.png)
![한 피어 안의 프로토콜 스택. 미디어 열은 MediaStreamTrack → RTP/RTCP → SRTP/SRTCP, 데이터 열은 RTCDataChannel API → DCEP(PPID 50)와 사용자 메시지(PPID 51·53) → SCTP(스트림·부분 신뢰성·혼잡 제어) → DTLS로 내려가고, DTLS에서 SRTP로 키 도출(exporter) 화살표가 이어지며, 두 열 모두 하나의 후보 쌍·하나의 5-tuple을 쓰는 ICE → UDP로 합쳐지는 구조](/images/study-webrtc/11-stack-dark.png)

[10장](/study/webrtc/10-dtls-srtp)과 이어서 보면 구조가 분명하다. 미디어는 DTLS로 키만 받아 SRTP로 따로 나가지만, SCTP 패킷은 통째로 DTLS 레코드 안에 들어간다. RFC 8831의 표현대로 DTLS가 SCTP 패킷 전체를 보호하므로 기밀성·무결성·출처 인증이 그대로 적용된다. 시그널링 보안이 깨지면 DataChannel도 MITM에 노출된다는 10장의 경고가 여기에도 똑같이 해당된다.

관련 규격은 네 개다.

| RFC | 내용 |
|---|---|
| RFC 8831 | WebRTC Data Channels: 스택, 채널 정의, PPID, 메시지 크기·인터리빙 권고 |
| RFC 8832 | DCEP(Data Channel Establishment Protocol): in-band 채널 열기 |
| RFC 8261 | SCTP over DTLS 캡슐화 |
| RFC 8841 | SDP 표현: `UDP/DTLS/SCTP`, `a=sctp-port`, `a=max-message-size` |

SDP에서는 별도 m-line 하나로 나타난다.

```text
m=application 9 UDP/DTLS/SCTP webrtc-datachannel
c=IN IP4 0.0.0.0
a=mid:2
a=sctp-port:5000
a=max-message-size:262144
```

### 알아 둘 구조적 사실

- <strong>PeerConnection당 SCTP association은 하나</strong>다. DataChannel 하나는 같은 번호의 스트림 쌍(송신·수신)이다. RFC 8831은 협상할 스트림 수로 최대값인 65535를 권한다.
- <strong>메시지 종류는 PPID로 구분</strong>한다. WebRTC String은 51, Binary는 53, 빈 메시지는 56/57, DCEP는 50이다. `send('text')`와 `send(arrayBuffer)`가 수신 측에서 문자열과 바이너리로 구분되는 이유다.
- <strong>혼잡 창은 association 단위</strong>다. 모든 DataChannel이 하나의 혼잡 창을 나눠 쓴다. 이 창은 미디어의 대역폭 추정(GCC, [09장](/study/webrtc/09-quality-latency))과 별개로 동작한다. 대용량 파일 전송이 영상과 같은 업링크를 놓고 경쟁할 수 있다는 뜻이다. LTE 업링크로 영상을 올리는 농기계라면 원격 조작 중에는 대용량 전송을 멈추거나 속도를 제한해야 한다.
- <strong>m-line이 있어야 한다</strong>. 첫 `createDataChannel()`을 offer 생성 전에 호출해야 SDP에 m=application이 들어간다. 연결이 된 뒤 처음 만들면 재협상(`negotiationneeded`)이 일어난다. 처음부터 채널을 쓸 계획이면 offer 전에 만들어 둔다.

## 2. 신뢰성·순서 옵션 조합

`createDataChannel(label, options)`의 전달 의미론은 세 옵션이 결정한다.

- `ordered`(기본 `true`): 보낸 순서대로 전달할지 여부
- `maxRetransmits`: 실패 시 재전송할 최대 횟수
- `maxPacketLifeTime`: 미확인 데이터를 (재)전송할 수 있는 시간 한도(ms)

`maxRetransmits`와 `maxPacketLifeTime`은 동시에 지정할 수 없다. 둘 다 주면 `TypeError`가 난다. 둘 다 없으면 완전 신뢰성(reliable)이다. 조합별 결과는 다음과 같다. 마지막 열은 DCEP가 상대에게 알리는 채널 타입 값(RFC 8832)이다.

| `ordered` | `maxRetransmits` | `maxPacketLifeTime` | 결과 | DCEP 채널 타입 |
|---|---|---|---|---|
| `true`(기본) | — | — | <strong>reliable ordered</strong>: TCP처럼 전부·순서대로 | `RELIABLE` (0x00) |
| `false` | — | — | <strong>reliable unordered</strong>: 전부 오지만 순서 무관 | `RELIABLE_UNORDERED` (0x80) |
| `true` | n | — | partial reliable ordered: n회까지 재전송, 포기한 메시지는 건너뜀 | `PARTIAL_RELIABLE_REXMIT` (0x01) |
| `false` | n | — | partial reliable unordered | `PARTIAL_RELIABLE_REXMIT_UNORDERED` (0x81) |
| `false` | 0 | — | <strong>unreliable unordered</strong>: UDP와 비슷 | 0x81 (재전송 0) |
| `true` | — | t | timed ordered: t ms 안에만 (재)전송 | `PARTIAL_RELIABLE_TIMED` (0x02) |
| `false` | — | t | timed unordered | `PARTIAL_RELIABLE_TIMED_UNORDERED` (0x82) |
| 아무 값 | 지정 | 지정 | `TypeError` | — |

표에 다 드러나지 않는 함정이 두 가지 있다.

<strong>ordered + 부분 신뢰성은 지연이 생각보다 길다.</strong> 순서를 지키려면 수신 측은 앞 메시지가 도착하거나, 송신 측이 그 메시지를 "포기"했다고 알려줄 때까지(SCTP FORWARD-TSN) 뒤 메시지를 쥐고 있어야 한다. `ordered: true, maxRetransmits: 0`도 손실이 나면 포기 통보가 올 때까지 뒤 메시지가 막힌다. 최신값만 의미 있는 스트림이라면 `ordered: false`로 두고 순서는 앱의 시퀀스 번호로 판단하는 편이 낫다(5절).

<strong>`maxPacketLifeTime`은 메시지 수명이다.</strong> 부분 신뢰성의 timed 정책(RFC 3758)은 송신자가 메시지에 TSN을 붙이기 전, 즉 처음 전송하기 전에도 수명을 검사해 만료된 메시지는 보내지 않도록 정한다(규칙 TR3). 송신 버퍼에 오래 쌓여 있으면 한 번도 전송되지 못하고 폐기될 수 있다는 뜻이다. "100ms 안에 도착하지 않으면 의미 없는 명령"을 정확히 표현하는 옵션이지만, 버퍼가 쌓이지 않도록 하는 흐름 제어(4절)와 함께 써야 의미가 있다.

농기계 원격 영상·제어 시나리오에 대입하면 채널을 용도별로 나누게 된다.

| 채널 | 용도 | 옵션 | 이유 |
|---|---|---|---|
| `teleop` | 조이스틱·PTZ 연속 조작(50Hz) | `ordered: false, maxRetransmits: 0` | 늦게 온 값은 다음 값이 대체한다. 재전송은 지연만 늘린다 |
| `hud` | 속도·방향·배터리 등 화면 표시용 텔레메트리(10Hz) | `ordered: false, maxPacketLifeTime: 200` | 약간의 손실은 허용하되 지나치게 늦은 값은 버린다 |
| `cmd` | 모드 변경·녹화 시작 등 이산 명령 | 기본값(reliable ordered) + 앱 수준 ack | 반드시 도착하고 순서가 중요하다 |
| `bulk` | 로그·스냅샷 파일 전송 | 기본값 + 흐름 제어 | 전부 도착해야 하고 다른 채널을 막지 않게 따로 둔다 |

```javascript
const pc = new RTCPeerConnection({ iceServers });

// offer 전에 만들어 SDP에 m=application이 들어가게 한다
const teleop = pc.createDataChannel('teleop', { ordered: false, maxRetransmits: 0 });
const hud = pc.createDataChannel('hud', { ordered: false, maxPacketLifeTime: 200 });
const cmd = pc.createDataChannel('cmd'); // reliable ordered
const bulk = pc.createDataChannel('bulk');

for (const dc of [teleop, hud, cmd, bulk]) dc.binaryType = 'arraybuffer';

// 지정한 옵션은 읽기 전용 속성으로 다시 확인할 수 있다
console.log(teleop.ordered, teleop.maxRetransmits, teleop.maxPacketLifeTime); // false 0 null
```

## 3. 채널 열기: DCEP와 negotiated

### in-band: DCEP

기본 방식에서는 한쪽이 `createDataChannel()`을 호출하면 브라우저가 DCEP(RFC 8832)로 상대에게 채널을 연다.

1. 여는 쪽이 SCTP 스트림 하나를 골라 `DATA_CHANNEL_OPEN`(메시지 타입 0x03, PPID 50)을 보낸다. 여기에는 label, protocol, 채널 타입(위 표의 값), 신뢰성 파라미터(재전송 횟수 또는 수명 ms)가 들어 있다.
2. 받는 쪽은 같은 번호 스트림으로 채널을 만들고 `datachannel` 이벤트를 발생시킨 뒤 `DATA_CHANNEL_ACK`(0x02)로 응답한다.
3. 여는 쪽은 ACK를 기다리지 않고 바로 데이터를 보내도 된다. 다만 ACK(또는 그 채널의 다른 메시지)를 받기 전까지는 채널 설정과 무관하게 순서대로 보내야 한다.

양쪽이 동시에 같은 스트림 번호를 고르면 충돌하므로 규칙이 하나 있다. <strong>DTLS 클라이언트는 짝수, DTLS 서버는 홀수</strong> 스트림 번호를 쓴다(위반하면 수신 측이 채널을 닫는다). 그래서 DTLS 역할이 정해지기 전에 만든 채널은 `id`가 `null`일 수 있다. 10장의 `a=setup`이 DataChannel 번호 체계까지 결정하는 셈이다.

```javascript
// 받는 쪽: in-band로 열린 채널은 이벤트로 들어온다
pc.addEventListener('datachannel', ({ channel }) => {
  console.log(channel.label, channel.id, channel.ordered, channel.maxRetransmits);
  channel.onmessage = (e) => handle(channel.label, e.data);
});
```

### out-of-band: negotiated: true + id

`negotiated: true`를 주면 브라우저는 DCEP를 쓰지 않는다. 양쪽이 <strong>같은 `id`로 각자</strong> `createDataChannel()`을 호출하고, 같은 번호 스트림이 서로 연결된다. `datachannel` 이벤트는 발생하지 않는다.

| 항목 | in-band (DCEP) | negotiated: true + id |
|---|---|---|
| 열기 | 한쪽만 호출, 상대는 이벤트로 받음 | 양쪽 모두 같은 id로 호출 |
| 왕복 | OPEN/ACK 교환(단, ACK 전 송신 가능) | 없음. SCTP가 연결되면 바로 사용 |
| id | 브라우저가 DTLS 역할에 따라 할당 | 앱이 지정(0~65534). `negotiated: true`인데 id가 없으면 `TypeError` |
| 설정 일치 | DCEP로 상대에게 전달 | <strong>검증 없음</strong>. 각 방향은 자기 쪽 설정으로 송신한다 |
| 어울리는 곳 | 동적으로 채널을 만드는 앱(채팅방, 파일별 채널) | 용도가 고정된 채널(디바이스 펌웨어와의 제어·텔레메트리) |

디바이스 플랫폼에는 negotiated 방식이 잘 맞는다. "0번은 teleop, 1번은 hud, 2번은 cmd" 같은 고정 번호를 프로토콜 문서와 펌웨어 상수로 정해 두면, 디바이스 쪽 코드가 `datachannel` 이벤트와 label 파싱에 의존하지 않는다. 대신 설정 불일치를 아무도 잡아 주지 않는다. 브라우저는 unordered, 디바이스는 ordered로 만들면 방향마다 의미론이 달라진다. 설정을 공유 상수 하나로 관리하고, 한 연결 안에서는 in-band와 negotiated 중 한 방식만 쓰는 편이 안전하다.

::: tabs
@tab 브라우저
```javascript
// 프로토콜 문서와 펌웨어가 공유하는 채널 표
const CHANNELS = {
  teleop: { id: 0, ordered: false, maxRetransmits: 0 },
  hud:    { id: 1, ordered: false, maxPacketLifeTime: 200 },
  cmd:    { id: 2 },
};

const ch = Object.fromEntries(
  Object.entries(CHANNELS).map(([label, opt]) => [
    label,
    pc.createDataChannel(label, { negotiated: true, ...opt }),
  ]),
);
ch.teleop.onopen = () => startTeleop(ch.teleop, { epoch, readStick }); // 5절
```

@tab 디바이스 (Go · Pion)
```go
func u16(v uint16) *uint16 { return &v }
func b(v bool) *bool       { return &v }

func openChannels(pc *webrtc.PeerConnection) (teleop, hud, cmd *webrtc.DataChannel, err error) {
	if teleop, err = pc.CreateDataChannel("teleop", &webrtc.DataChannelInit{
		Negotiated: b(true), ID: u16(0), Ordered: b(false), MaxRetransmits: u16(0),
	}); err != nil {
		return
	}
	if hud, err = pc.CreateDataChannel("hud", &webrtc.DataChannelInit{
		Negotiated: b(true), ID: u16(1), Ordered: b(false), MaxPacketLifeTime: u16(200),
	}); err != nil {
		return
	}
	cmd, err = pc.CreateDataChannel("cmd", &webrtc.DataChannelInit{
		Negotiated: b(true), ID: u16(2),
	})
	return
}
```
:::

AWS 관리형 경로를 쓸 때도 DataChannel은 그대로 쓸 수 있다. KVS WebRTC C SDK는 DataChannel을 지원하고 빌드 옵션 `-DENABLE_DATA_CHANNEL`이 기본으로 켜져 있다([19장](/study/webrtc/19-kvs-c-sdk)).

## 4. 메시지 크기와 흐름 제어

### maxMessageSize와 16KiB 권장의 근거

한 번의 `send()`로 보낼 수 있는 최대 크기는 `pc.sctp.maxMessageSize`(`RTCSctpTransport.maxMessageSize`)다. W3C 명세는 이 값을 다음처럼 계산한다.

- 원격 SDP의 `a=max-message-size` 값을 읽는다. 속성이 없으면 <strong>65536</strong>으로 간주하고, 0은 "크기 제한 없음"을 뜻한다.
- 로컬 구현이 보낼 수 있는 크기(canSendSize)와 비교해 둘 다 양수면 작은 값을 쓴다.
- `send()`할 데이터가 이 값보다 크면 `TypeError`가 난다.

MDN은 대부분의 최신 브라우저가 최소 256KB 메시지를 지원한다고 적는다. 그렇다면 실전에서 흔히 말하는 "16KiB로 잘라 보내라"는 어디서 왔을까. 근거는 크기 <strong>한계</strong>가 아니라 <strong>지연</strong>이다.

- <strong>RFC 8831 §6.6</strong>: SCTP 기본 규격(RFC 4960)은 사용자 메시지 인터리빙을 지원하지 않으므로 큰 메시지 하나가 association을 독점할 수 있다. 이를 풀려고 RFC 8260(I-DATA)이 인터리빙 확장을 정의했고 사용해야 한다(SHOULD). 그리고 "메시지 인터리빙이 지원되지 않는 한, 송신자는 독점을 피하기 위해 최대 메시지 크기를 16KB로 제한해야 한다(SHOULD)"고 명시한다.
- <strong>Mozilla WebRTC 블로그(2017)</strong>: 당시 어떤 브라우저도 SCTP ndata(I-DATA) 확장을 지원하지 않아, 메시지 하나가 SCTP association 전체를 독점해 다른 채널(예: 채팅)을 지연시킨다고 설명했다. 같은 글에서 Firefox 57이 EOR 처리를 추가하기 전에는 Firefox–Chrome 사이 큰 메시지 전송에 문제가 있었다는 역사도 정리했다.
- <strong>webrtc/samples</strong>의 공식 파일 전송 예제도 `const chunkSize = 16384;`로 잘라 보낸다.

숫자로 보면 체감이 된다. 업링크 2Mbps인 LTE 디바이스가 256KiB 메시지 하나를 보내면 262144×8 ≈ 2.1Mbit이므로 전송에만 약 1초가 걸린다. 인터리빙이 없으면 그 1초 동안 같은 association의 teleop 채널 메시지도 줄을 선다. 16KiB 청크라면 한 메시지 점유 시간이 약 65ms로 줄고, 제어 메시지가 청크 사이에 끼어들 수 있다. 정리하면 이렇다. 크기 상한은 `maxMessageSize`로 확인하고, 실제 청크는 16KiB 안팎으로 잡는다. 이유는 지연이다.

### bufferedAmount 흐름 제어

`send()`는 절대 블록하지 않는다. 데이터는 브라우저 송신 큐에 쌓이고, 아직 전송되지 않은 바이트 수가 `bufferedAmount`에 반영된다. 큐가 구현 한도(명세의 MaxBufferSize)를 넘으면 `send()`가 `OperationError`를 던진다. 루프에서 무작정 `send()`를 호출하면 메모리가 불어나고, 큐가 쌓인 만큼 지연이 늘며, 결국 예외가 난다.

이를 막는 도구가 `bufferedAmountLowThreshold`(초기값 0)와 `bufferedamountlow` 이벤트다. `bufferedAmount`가 임계값 위에 있다가 임계값 이하로 떨어지는 순간 이벤트가 발생한다. 높은 수위(high water)에서 멈추고 낮은 수위(low water)에서 재개하는 고전적인 히스테리시스 패턴을 쓴다.

```javascript
const CHUNK = 16 * 1024;           // 독점 방지용 청크 (RFC 8831 §6.6)
const HIGH_WATER = 1024 * 1024;    // 1 MiB 넘게 쌓이면 멈춤
const LOW_WATER = 256 * 1024;      // 256 KiB 이하로 빠지면 재개

function waitDrain(dc) {
  return new Promise((resolve, reject) => {
    const onLow = () => { cleanup(); resolve(); };
    const onClose = () => { cleanup(); reject(new Error('channel closed')); };
    const cleanup = () => {
      dc.removeEventListener('bufferedamountlow', onLow);
      dc.removeEventListener('close', onClose);
    };
    dc.addEventListener('bufferedamountlow', onLow);
    dc.addEventListener('close', onClose);
  });
}

async function sendBlob(pc, dc, blob) {
  dc.bufferedAmountLowThreshold = LOW_WATER;
  const size = Math.min(CHUNK, pc.sctp?.maxMessageSize ?? CHUNK);
  for (let offset = 0; offset < blob.size; offset += size) {
    if (dc.bufferedAmount > HIGH_WATER) await waitDrain(dc);
    if (dc.readyState !== 'open') throw new Error('channel closed');
    dc.send(await blob.slice(offset, offset + size).arrayBuffer());
  }
}
```

흐름 제어에서 놓치기 쉬운 점은 다음과 같다.

- <strong>수신 측에는 배압(backpressure) API가 없다.</strong> `onmessage`를 잠시 멈출 방법이 없으므로 수신 처리가 느리면 메모리에 쌓인다. 대용량 전송이라면 "N개 청크마다 수신 측이 ack를 보내고 송신 측은 ack 창 안에서만 보낸다" 같은 앱 수준 창(window)을 둔다.
- <strong>제어 채널에도 수위를 본다.</strong> teleop 채널의 `bufferedAmount`가 0이 아니라는 것은 망이 50Hz 명령조차 소화하지 못하고 있다는 신호다. 이때 더 보내면 낡은 명령이 큐에 쌓인다. 쌓였으면 이번 틱을 건너뛰는 편이 낫다(5절 코드).
- <strong>디바이스 쪽도 같은 API가 있다.</strong> Pion은 `dc.BufferedAmount()`, `dc.SetBufferedAmountLowThreshold(th)`, `dc.OnBufferedAmountLow(f)`를 제공한다. 디바이스가 로그 파일을 올리는 방향에서도 같은 패턴을 쓴다.

## 5. 원격 제어 명령 채널 설계

DataChannel의 가장 매력적인 용도는 영상을 보면서 수십 ms 단위로 기계를 조작하는 원격 제어다. 동시에 가장 위험한 용도이기도 하다. 네트워크는 언제든 끊기고, 늦고, 순서를 뒤바꾼다. 설계 원칙은 하나다. <strong>신호가 없으면 정지한다(fail-safe).</strong>

### 설계 원칙

1. <strong>변화량이 아니라 목표 상태를 보낸다.</strong> "조향 +5도"가 아니라 "조향 목표 12도, 속도 목표 30%"를 보낸다. 메시지 하나를 잃어도 다음 메시지가 완전한 상태를 담고 있으므로 오차가 누적되지 않고, 같은 메시지를 두 번 적용해도 안전하다(멱등).
2. <strong>시퀀스 번호로 최신값만 적용한다.</strong> unordered 채널에서는 순서가 뒤바뀐다. 디바이스는 마지막으로 적용한 seq 이하의 메시지를 버린다. 세션마다 epoch를 새로 발급하면 이전 세션의 메시지나 재전송 공격도 같은 규칙으로 걸러진다.
3. <strong>타임스탬프는 신중하게 쓴다.</strong> 운영자 PC와 디바이스의 시계는 다르다. 송신 시각으로 "200ms 넘은 명령 폐기"를 하려면 시계 동기(NTP/chrony)나 왕복 측정으로 추정한 오프셋이 필요하다. 그보다 확실한 기준은 디바이스 로컬 시계로 잰 "마지막 유효 명령 이후 경과 시간"이다. 송신 타임스탬프는 지연 측정과 진단에 쓴다.
4. <strong>데드맨 스위치</strong>: 운영자가 버튼(또는 조이스틱 트리거)을 누르고 있는 동안에만 명령이 유효하다. 모든 메시지에 데드맨 비트를 싣고, 비트가 꺼지면 디바이스는 정지한다. 브라우저 탭이 백그라운드로 가면(`visibilitychange`) 데드맨을 해제한 것으로 처리한다. 백그라운드 탭에서는 타이머가 강하게 제한되어 50Hz 송신 자체가 불가능해지기 때문이다.
5. <strong>워치독</strong>: 디바이스 제어 루프는 마지막 유효 명령 이후 경과 시간을 매 주기 확인한다. 일정 시간(예: 150ms)을 넘으면 감속을 시작하고, 한계(예: 300ms)를 넘으면 안전정지한다. DataChannel `close`나 PeerConnection `disconnected`/`failed`를 받으면 기다리지 않고 즉시 정지한다.
6. <strong>자동 재개 금지</strong>: 안전정지 후 패킷이 다시 들어와도 그대로 움직이면 안 된다. 새 세션(epoch) 발급과 운영자의 명시적 재무장(arm)을 거쳐야 다시 움직인다.
7. <strong>네트워크 밖의 마지막 방어선</strong>: 제어 소프트웨어가 멈춰도 기계가 서야 한다. 별도 MCU/PLC의 하드웨어 워치독, 기계 본체의 물리 비상정지, 무선 리모컨 E-stop은 네트워크와 독립적으로 유지한다. 원격 E-stop은 DataChannel(cmd)과 MQTT 양쪽으로 중복 송신한다.

![운영자가 50Hz로 seq 101~108 명령을 보내는 타임라인. 101·102·104·106은 디바이스에 도착해 적용되고, 103은 손실되지만 재전송하지 않으며, 105는 지연되어 106보다 늦게 도착해 seq ≤ 106이므로 폐기된다. 링크가 끊긴 뒤 107·108은 도착하지 못하고, 마지막 유효 명령 이후 워치독 300ms 동안 디바이스 상태가 주행에서 감속을 거쳐 안전정지·재무장 대기로 바뀌며, 새 세션과 데드맨 재입력 전에는 명령을 무시한다](/images/study-webrtc/11-control-watchdog-light.png)
![운영자가 50Hz로 seq 101~108 명령을 보내는 타임라인. 101·102·104·106은 디바이스에 도착해 적용되고, 103은 손실되지만 재전송하지 않으며, 105는 지연되어 106보다 늦게 도착해 seq ≤ 106이므로 폐기된다. 링크가 끊긴 뒤 107·108은 도착하지 못하고, 마지막 유효 명령 이후 워치독 300ms 동안 디바이스 상태가 주행에서 감속을 거쳐 안전정지·재무장 대기로 바뀌며, 새 세션과 데드맨 재입력 전에는 명령을 무시한다](/images/study-webrtc/11-control-watchdog-dark.png)

워치독 시간은 감이 아니라 계산으로 정한다. 시속 10km(약 2.8m/s)로 달리는 트랙터라면 워치독 300ms 동안 약 0.83m를 더 간다. 여기에 감속·제동 거리가 더해진다. 반대로 너무 짧게 잡으면 LTE의 일시적 지연 스파이크([09장](/study/webrtc/09-quality-latency)의 지연 예산)마다 기계가 멈춰 작업이 안 된다. 50Hz 송신이라면 300ms는 연속 15개 손실에 해당한다. 기계 속도, 정지 거리, 회선 품질을 함께 놓고 정한다.

### 메시지 형식

JSON보다 고정 길이 바이너리가 파싱 비용과 크기 면에서 유리하고, 펌웨어(C/Go)와 맞추기도 쉽다. 리틀 엔디언 20바이트 예시는 다음과 같다.

| 오프셋 | 크기 | 필드 | 설명 |
|---|---|---|---|
| 0 | 1 | `version` | 형식 버전(1) |
| 1 | 1 | `flags` | bit0 데드맨, bit1 E-stop |
| 2 | 2 | (예약) | 0 |
| 4 | 4 | `epoch` | 세션 번호(백엔드가 제어권 부여 시 발급) |
| 8 | 4 | `seq` | 세션 내 단조 증가 |
| 12 | 4 | `sentAtMs` | 운영자 시계 ms 하위 32비트(진단용) |
| 16 | 2 | `throttle` | -1000~1000 (‰) |
| 18 | 2 | `steer` | -1000~1000 (‰) |

### 브라우저 송신 측

```javascript
const FLAG_DEADMAN = 1, FLAG_ESTOP = 2;
const PERIOD_MS = 20; // 50Hz

function startTeleop(dc, { epoch, readStick }) {
  let seq = 0;
  let deadman = false;
  const buf = new ArrayBuffer(20);
  const view = new DataView(buf);

  const hold = document.getElementById('deadman');
  hold.addEventListener('pointerdown', () => { deadman = true; });
  for (const ev of ['pointerup', 'pointercancel', 'pointerleave']) {
    hold.addEventListener(ev, () => { deadman = false; });
  }
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) deadman = false; // 백그라운드 탭 = 데드맨 해제
  });

  const timer = setInterval(() => {
    if (dc.readyState !== 'open') return;
    if (dc.bufferedAmount > 0) return; // 망이 못 따라오면 낡은 명령을 쌓지 않고 이번 틱 건너뜀
    const { throttle, steer } = readStick(); // -1000..1000
    view.setUint8(0, 1);
    view.setUint8(1, deadman ? FLAG_DEADMAN : 0);
    view.setUint16(2, 0, true);
    view.setUint32(4, epoch, true);
    view.setUint32(8, ++seq, true);
    view.setUint32(12, Date.now() >>> 0, true);
    view.setInt16(16, deadman ? throttle : 0, true);
    view.setInt16(18, deadman ? steer : 0, true);
    dc.send(buf);
  }, PERIOD_MS);

  dc.addEventListener('close', () => clearInterval(timer));
  return () => clearInterval(timer);
}
```

### 디바이스 수신 측과 워치독

```go
package teleop

import (
	"encoding/binary"
	"errors"
	"sync"
	"time"

	"github.com/pion/webrtc/v4"
)

const (
	period    = 20 * time.Millisecond
	softLimit = 150 * time.Millisecond // 이 시간 동안 무수신이면 감속
	hardLimit = 300 * time.Millisecond // 이 시간 동안 무수신이면 안전정지
)

type Actuator interface {
	Apply(throttle, steer int16)
	RampDown()
	SafeStop()
	EmergencyStop()
}

type command struct {
	epoch, seq      uint32
	deadman, estop  bool
	throttle, steer int16
}

func decode(b []byte) (command, error) {
	if len(b) != 20 || b[0] != 1 {
		return command{}, errors.New("bad frame")
	}
	return command{
		deadman:  b[1]&1 != 0,
		estop:    b[1]&2 != 0,
		epoch:    binary.LittleEndian.Uint32(b[4:]),
		seq:      binary.LittleEndian.Uint32(b[8:]),
		throttle: int16(binary.LittleEndian.Uint16(b[16:])),
		steer:    int16(binary.LittleEndian.Uint16(b[18:])),
	}, nil
}

type Controller struct {
	act       Actuator
	mu        sync.Mutex
	armed     bool
	epoch     uint32
	lastSeq   uint32
	last      command
	lastValid time.Time
}

func New(act Actuator) *Controller { return &Controller{act: act} }

// Arm: 백엔드가 제어권(lease)과 새 epoch를 부여하고 운영자가 데드맨을 눌렀을 때만 호출
func (c *Controller) Arm(epoch uint32) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.armed, c.epoch, c.lastSeq = true, epoch, 0
	c.last = command{}
	c.lastValid = time.Now()
}

func (c *Controller) Disarm() {
	c.mu.Lock()
	c.armed = false
	c.mu.Unlock()
	c.act.SafeStop()
}

// Bind: teleop 채널과 PeerConnection 상태를 워치독에 연결
func (c *Controller) Bind(pc *webrtc.PeerConnection, teleop *webrtc.DataChannel) {
	teleop.OnMessage(func(m webrtc.DataChannelMessage) { c.onFrame(m.Data) })
	teleop.OnClose(c.Disarm)
	pc.OnConnectionStateChange(func(s webrtc.PeerConnectionState) {
		switch s {
		case webrtc.PeerConnectionStateDisconnected,
			webrtc.PeerConnectionStateFailed,
			webrtc.PeerConnectionStateClosed:
			c.Disarm() // 워치독 만료를 기다리지 않고 즉시 정지
		}
	})
}

func (c *Controller) onFrame(b []byte) {
	cmd, err := decode(b)
	if err != nil {
		return
	}
	if cmd.estop {
		c.mu.Lock()
		c.armed = false
		c.mu.Unlock()
		c.act.EmergencyStop()
		return
	}
	c.mu.Lock()
	defer c.mu.Unlock()
	if !c.armed || cmd.epoch != c.epoch { // 재무장 전이거나 다른 세션의 명령
		return
	}
	if cmd.seq <= c.lastSeq { // 순서 뒤바뀜·중복 → 최신값만 유효
		return
	}
	c.lastSeq, c.last, c.lastValid = cmd.seq, cmd, time.Now()
}

// Run: 고정 주기 제어 루프 (별도 고루틴, 실시간 우선순위 권장)
func (c *Controller) Run(stop <-chan struct{}) {
	t := time.NewTicker(period)
	defer t.Stop()
	for {
		select {
		case <-stop:
			c.act.SafeStop()
			return
		case <-t.C:
		}

		c.mu.Lock()
		age := time.Since(c.lastValid)
		released := c.lastSeq > 0 && !c.last.deadman
		if c.armed && (released || age > hardLimit) {
			c.armed = false // 데드맨 해제 또는 워치독 만료 → 재무장 전까지 정지 유지
		}
		armed, cmd := c.armed, c.last
		c.mu.Unlock()

		switch {
		case !armed:
			c.act.SafeStop()
		case age > softLimit:
			c.act.RampDown()
		default:
			c.act.Apply(cmd.throttle, cmd.steer)
		}
	}
}
```

이 코드에서 확인할 지점은 다음과 같다.

- 메시지 수신(`onFrame`)은 상태만 갱신하고, 액추에이터 출력은 고정 주기 루프(`Run`)만 한다. 메시지가 몰려 오든 끊기든 출력 주기가 일정하고, 워치독 판단이 한곳에 모인다.
- `Arm` 직후 `hardLimit` 안에 첫 유효 명령이 오지 않으면 다시 정지 상태로 돌아간다. 그 사이 출력은 0(정지)이다. 재무장은 "명령이 실제로 흐르고 있음"이 확인되어야 유지된다.
- E-stop 비트는 epoch·seq 검사보다 먼저 처리한다. 정지 명령은 어떤 세션에서 왔든 따른다.
- seq는 32비트이므로 50Hz로 2년 넘게 보내야 한 바퀴 돈다. 세션마다 epoch를 새로 받으므로 실무에서 랩어라운드는 문제가 되지 않는다.
- 제어권은 한 번에 한 운영자만 갖는다. 백엔드가 lease를 발급하고 epoch를 함께 내려보내면(6절의 MQTT 경로), 디바이스는 그 epoch의 DataChannel 명령만 받는다. DataChannel 자체의 인증은 10장의 시그널링 인증과 DTLS 지문 검증에 기댄다.

운영자 화면에는 왕복 지연을 표시하고, 기준을 넘으면 조작을 막는 것이 좋다. 디바이스가 hud 채널로 마지막 seq와 수신 시각을 주기적으로 돌려주면 브라우저가 RTT를 계산할 수 있다. "지연 450ms — 원격 조작 불가" 같은 표시는 운영자가 위험한 조작을 시도하지 않게 하는 가장 값싼 안전장치다.

## 6. DataChannel vs MQTT(AWS IoT Core) 역할 분담

농기계 플랫폼에는 이미 MQTT 경로가 있는 경우가 많다. 텔레메트리, Device Shadow, Jobs가 AWS IoT Core 위에서 돌고 있다면 "제어 명령을 어디로 보낼까"가 실제 설계 질문이 된다. 답은 둘 중 하나를 고르는 것이 아니라 <strong>성격에 따라 나누는 것</strong>이다. MQTT와 IoT Core 자체는 [MQTT 프로토콜과 AWS IoT 적용](/posts/tech/2025-08-13-mqtt)과 [AWS IoT Core 완전 정복](/posts/tech/2025-06-27-iot)에서 다뤘다.

![운영자 브라우저와 농기계·로봇이 DataChannel(P2P, 세션 중에만)로 직접 연결되어 조이스틱·PTZ 연속 조작(unordered, 재전송 0, 최신값만 유효, 수십 ms)을 주고받고, 별도로 운영자 브라우저가 백엔드 API(인가·감사 로그)에 HTTPS로 명령을 요청하면 백엔드가 AWS IoT Core(MQTT·Shadow·Jobs)에 publish하고 IoT Core와 디바이스가 모드 변경·작업 명령(QoS 1), 텔레메트리·상태, Shadow desired/reported, 오프라인 큐(영구 세션)를 주고받는 역할 분담 구조](/images/study-webrtc/11-dc-vs-mqtt-light.png)
![운영자 브라우저와 농기계·로봇이 DataChannel(P2P, 세션 중에만)로 직접 연결되어 조이스틱·PTZ 연속 조작(unordered, 재전송 0, 최신값만 유효, 수십 ms)을 주고받고, 별도로 운영자 브라우저가 백엔드 API(인가·감사 로그)에 HTTPS로 명령을 요청하면 백엔드가 AWS IoT Core(MQTT·Shadow·Jobs)에 publish하고 IoT Core와 디바이스가 모드 변경·작업 명령(QoS 1), 텔레메트리·상태, Shadow desired/reported, 오프라인 큐(영구 세션)를 주고받는 역할 분담 구조](/images/study-webrtc/11-dc-vs-mqtt-dark.png)

| 기준 | DataChannel | MQTT (AWS IoT Core) |
|---|---|---|
| 경로 | 피어 간 직결(필요 시 TURN 경유) | 브로커 경유(발행자 → IoT Core → 구독자) |
| 지연 | 경로 RTT 수준. 브로커 홉이 없다 | 브로커 홉이 추가된다 |
| 존재 기간 | WebRTC 세션이 열려 있는 동안만 | 디바이스가 온라인인 동안 상시 연결 |
| 전달 보장 | 채널마다 선택(reliable ~ 재전송 0, 수명 제한) | QoS 0·1. QoS 2는 지원하지 않는다 |
| 순서 | 채널마다 선택 | 브로커가 메시지·ACK 수신 순서를 보장하지 않는다 |
| 오프라인 | 세션이 없으면 전달 불가 | 영구 세션이 미확인·신규 QoS 1 메시지를 보관(MQTT 3 기본 만료 1시간, 조정 가능). Shadow desired로 최종 상태를 동기화 |
| 1:N | 피어마다 채널 별도 | 토픽 구독으로 팬아웃 |
| 인증·인가 | 시그널링 인증 + DTLS 지문(10장) | X.509 상호 TLS + IoT 정책(토픽 단위) |
| 메시지 크기 | `maxMessageSize`(실전 16KiB 청크) | publish당 128KB |
| 기록·연계 | 앱이 직접 남겨야 한다 | Rules Engine으로 저장·분석 서비스와 연계 |
| 적합한 용도 | 조이스틱·PTZ·고빈도 HUD 텔레메트리 | 모드 변경·작업 지시·설정·상태 보고·알림·E-stop 중복 경로 |

나누는 기준을 문장으로 정리하면 다음과 같다.

- <strong>값의 수명이 수백 ms 이하면 DataChannel</strong>이다. 조이스틱 값은 브로커를 돌아오는 사이에 이미 낡는다. 끊기면 버려도 되는(버려야 하는) 데이터다.
- <strong>연결이 끊겨도 살아남아야 하거나 감사가 필요하면 MQTT·백엔드</strong>다. "자동 주행 모드로 전환", "이 작업 경로 실행" 같은 명령은 백엔드 API가 인가하고 기록한 뒤 IoT Core로 보낸다. 디바이스가 잠시 오프라인이면 영구 세션이나 Shadow desired 상태가 받아 둔다.
- <strong>제어권 자체는 MQTT·백엔드로 관리</strong>한다. 원격 조작 세션 시작(lease 발급·epoch 전달)과 종료는 백엔드가 결정해 MQTT로 알린다. DataChannel 명령은 그 lease가 유효한 동안만 받는다(5절의 `Arm`).
- <strong>텔레메트리는 둘로 나눈다.</strong> 관제 대시보드용 저빈도 상태(예: 1Hz)는 항상 MQTT로 보낸다. 운영자가 영상을 보는 동안의 고빈도 HUD 데이터만 DataChannel로 보낸다.
- <strong>정지 명령은 양쪽으로 보낸다.</strong> 한쪽 경로가 죽어 있을 수 있으므로 원격 E-stop은 DataChannel과 MQTT로 중복 송신하고, 디바이스는 먼저 도착한 쪽을 따른다. 물론 둘 다 끊긴 경우에 대한 답은 5절의 워치독이다.

이 분담은 [25장 캡스톤](/study/webrtc/25-capstone-farm-platform)에서 전체 아키텍처의 일부로 다시 등장한다.

::: tip 핵심 정리
- DataChannel은 SCTP를 DTLS 안에 넣어(RFC 8261) ICE/UDP로 보낸다. PeerConnection당 association 하나, 채널 하나는 같은 번호의 스트림 쌍이며, 혼잡 창은 모든 채널이 공유하고 미디어 혼잡 제어와는 별개다.
- `ordered`·`maxRetransmits`·`maxPacketLifeTime`으로 reliable ordered부터 unreliable unordered까지 고른다. 뒤의 둘은 동시에 지정할 수 없다. 최신값 스트림은 `ordered: false, maxRetransmits: 0`에 앱 시퀀스 번호를 더한다.
- in-band 채널은 DCEP OPEN/ACK로 열리고 DTLS 클라이언트는 짝수, 서버는 홀수 id를 쓴다. `negotiated: true` + `id`는 왕복 없이 고정 번호 채널을 만들지만 설정 불일치를 검증하지 않는다.
- 크기 상한은 `maxMessageSize`(원격 `a=max-message-size`, 없으면 65536)다. 16KiB 권장은 인터리빙 없는 SCTP에서 큰 메시지가 association을 독점하지 않게 하라는 RFC 8831 §6.6의 지연 권고다.
- `send()`는 블록하지 않는다. `bufferedAmount`·`bufferedAmountLowThreshold`·`bufferedamountlow`로 high/low water 흐름 제어를 한다.
- 원격 제어는 목표 상태 + epoch/seq(최신값만 유효) + 데드맨 비트 + 디바이스 워치독(감속→안전정지, 자동 재개 금지)으로 설계하고, 하드웨어 워치독·물리 E-stop을 네트워크와 독립적으로 둔다.
- DataChannel은 수명이 짧은 저지연 조작, MQTT(AWS IoT Core)는 신뢰성 있는 명령·상태·오프라인 큐·제어권 관리를 맡는다. E-stop은 양쪽으로 보낸다.
:::

## 다음 챕터

[토폴로지: Mesh·SFU·MCU](/study/webrtc/12-topology-sfu)에서는 1:1 P2P를 넘어 다수 참가자로 확장할 때의 Mesh·SFU·MCU 비교, Simulcast·SVC, 오픈소스 SFU, 그리고 10장에서 예고한 SFU 환경의 E2EE(Encoded Transform, SFrame)를 다룬다.
