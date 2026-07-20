---
title: "전송 계층 사용하기"
description: "AgIsoStack++에서 8바이트를 넘는 메시지를 TP/ETP/Fast Packet으로 주고받는 방법."
date: 2026-07-20
tags: [AgIsoStack, ISOBUS, C++]
---

# 전송 계층 사용하기

## 학습 목표
- 8바이트를 초과하는 메시지를 `send_can_message` 한 번으로 보내는 방법을 안다.
- 스택이 페이로드 크기와 목적지에 따라 TP·ETP·단일 프레임 중 무엇을 고르는지 설명할 수 있다.
- 브로드캐스트 전송의 크기 한계와 속도 제약을 이해하고, 왜 권장되지 않는지 말할 수 있다.
- 8바이트를 초과하는 수신 메시지를 콜백으로 받는 방법을 안다.
- NMEA 2000 Fast Packet 메시지를 송신·수신하는 API를 사용할 수 있다.
- `get_active_transport_protocol_sessions`로 진행 중인 세션 상태를 관찰할 수 있다.

## 1. 8바이트 초과 전송하기

클래식 CAN 프레임의 데이터 필드는 8바이트가 전부다. 그보다 큰 데이터를 보내려면 <strong>전송 프로토콜(transport protocol)</strong>이 필요하다. AgIsoStack++는 이 과정을 사용자에게 거의 보이지 않게 감춘다.

방법은 단순하다. 평소처럼 메시지를 보내되, 길이만 크게 넘기면 된다.

```cpp
std::uint8_t longMessage[2000] = {0};

isobus::CANNetworkManager::CANNetwork.send_can_message(0xEF00, longMessage, 2000, myECU, myPartner);
```

이게 전부다. 페이로드 크기에 따라 TP 또는 ETP로 알아서 전송된다. 8바이트 이하를 보낼 때와 호출 형태가 <strong>완전히 같다</strong>. 세 번째 인자인 길이만 달라졌을 뿐이다.

내부적으로 `send_can_message`는 다음 순서로 프로토콜을 시도한다. 앞의 프로토콜이 "내가 처리할 수 없다"며 거절하면 다음으로 넘어간다.

![프로토콜 자동 선택](/images/study-agisostack/10-protocol-selection-light.png)
![프로토콜 자동 선택](/images/study-agisostack/10-protocol-selection-dark.png)

`TransportProtocolManager::protocol_transmit_message`는 데이터 크기가 8바이트 이하이거나 1785바이트를 초과하면 곧바로 `false`를 반환한다. 그러면 `ExtendedTransportProtocolManager`가 시도되고, ETP는 1785바이트 이하이거나 117,440,505바이트를 초과하면 거절한다. 둘 다 거절하면 마지막으로 단일 프레임 송신 경로(`send_can_message_raw`)가 쓰인다.

## 2. 프로토콜 자동 선택 규칙

스택이 실제로 무엇을 고르는지 표로 정리하면 이렇다.

| 페이로드 크기 | 목적지 지정 (destination != nullptr) | 브로드캐스트 (destination == nullptr) |
|---|---|---|
| 1 ~ 8 byte | 단일 CAN 프레임 (PDU1) | 단일 CAN 프레임 (PDU2 / DA = 0xFF) |
| 9 ~ 1785 byte | TP — CMDT (RTS/CTS 핸드셰이크) | TP — BAM (프레임 간 강제 지연) |
| 1786 ~ 117,440,505 byte | ETP | <strong>불가</strong> — ETP는 브로드캐스트를 허용하지 않는다 |
| 117,440,505 byte 초과 | 불가 | 불가 |

여기서 기억해 둘 제약이 두 가지다.

- 브로드캐스트 주소로는 <strong>1785바이트를 넘길 수 없다</strong>. ETP가 명시적으로 브로드캐스트를 금지하고, Fast Packet은 최대 223바이트까지만 다루기 때문이다.
- 절대 최대 크기는 <strong>117,440,505바이트</strong>다. ETP 규격 자체가 그 이상을 표현할 수 없다.

이 상수들은 라이브러리 안에 그대로 정의돼 있다.

```cpp
// isobus/can_transport_protocol.hpp
static constexpr std::uint32_t MAX_PROTOCOL_DATA_LENGTH = 1785;

// isobus/can_extended_transport_protocol.hpp
static constexpr std::uint32_t MAX_PROTOCOL_DATA_LENGTH = 117440505;
```

::: warning 브로드캐스트로 긴 메시지를 보내지 마라
표준은 BAM 프레임 사이에 <strong>의무 지연</strong>을 두도록 규정하고, 스택도 이를 강제한다. 즉 브로드캐스트로 보내는 긴 메시지는 <strong>매우 느리다</strong>. 스택의 송신은 완전히 논블로킹이지만, BAM 세션은 <strong>한 번에 하나만</strong> 진행할 수 있다. 앞선 BAM이 아직 끝나지 않았는데 다른 BAM을 보내야 하는 상황이 오면 애플리케이션에 문제가 생긴다.
:::

::: info 관련 스터디
프로토콜 자체의 동작 원리(RTS/CTS, BAM, 타임아웃, abort 사유)는 [ISOBUS CH11. J1939 Transport Protocol](/study/isobus/11-j1939-transport)에서 다뤘다. 이 스터디 안에서는 [CH4. 전송 개념 잡기](/study/agisostack/04-transport-concepts)에서 개요를 정리했다.
:::

## 3. 8바이트 초과 수신하기

수신 쪽은 더 간단하다. 특별히 할 일이 <strong>없다</strong>.

어떤 PGN에 대해 콜백을 등록하면, 그 PGN으로 오는 <strong>모든 크기</strong>의 메시지에 대해 등록한 것이 된다. TP나 ETP로 쪼개져 온 메시지도 포함된다. 스택이 조각을 모아 재조립한 뒤, 완성된 하나의 `CANMessage`로 콜백을 <strong>한 번</strong> 호출해 준다.

```cpp
void check_can_message(const isobus::CANMessage &message, void *)
{
	// message.get_data_length()가 8을 훨씬 넘을 수 있다.
	// 재조립이 끝난 전체 페이로드가 여기로 들어온다.
	for (std::uint32_t i = 0; i < message.get_data_length(); i++)
	{
		// ...
	}
}

// 전역 콜백 — 이 PGN이면 누가 보냈든 받는다
isobus::CANNetworkManager::CANNetwork.add_global_parameter_group_number_callback(0xEF00, check_can_message, nullptr);

// 파트너 한정 콜백 — 특정 파트너가 내 ICF로 보낸 것만 받는다
myPartner->add_parameter_group_number_callback(0xEF00, check_can_message, nullptr, myECU);
```

콜백 등록 방법 자체는 [CH8. 메시지 수신하기](/study/agisostack/08-receiving-messages)에서 다룬 그대로다. 전송 계층 때문에 달라지는 것은 없다.

::: tip 하나 예외가 있다
TP와 ETP는 이렇게 투명하게 처리되지만, <strong>NMEA 2000 Fast Packet은 다르다</strong>. Fast Packet 메시지는 반드시 명시적으로 송신하고, 명시적으로 등록해야 한다. 다음 절에서 다룬다.
:::

## 4. Fast Packet 메시지 송수신

Fast Packet은 NMEA 2000(IEC 61162-3)에서 쓰는 프로토콜로, 최대 <strong>223바이트</strong>까지 스트리밍할 수 있다. TP/ETP와 결정적으로 다른 점은 <strong>각 프레임이 원래 PGN과 우선순위를 그대로 유지한다</strong>는 것이다.

![Fast Packet 프레임 구성](/images/study-agisostack/10-fast-packet-frames-light.png)
![Fast Packet 프레임 구성](/images/study-agisostack/10-fast-packet-frames-dark.png)

첫 프레임은 2바이트를 헤더로 쓴다. 첫 바이트에는 시퀀스 카운터(같은 PGN의 연속 전송을 구분)와 프레임 카운터(0)가 들어가고, 두 번째 바이트에는 전체 파라미터 그룹의 크기가 들어간다. 나머지 6바이트가 데이터다. 후속 프레임은 카운터 1바이트만 쓰고 7바이트를 데이터로 채운다. 그래서 최대 크기가 `6 + 31 × 7 = 223`바이트다.

### 4.1. 송신

Fast Packet 송신은 `FastPacketProtocol::send_multipacket_message`를 직접 호출한다. 네트워크 매니저를 통해서는 보낼 수 없다. 스택 입장에서 이 PGN을 TP가 아닌 FP로 보내야 한다는 걸 알 방법이 없기 때문이다.

```cpp
#include "isobus/isobus/nmea2000_fast_packet_protocol.hpp"

constexpr std::uint8_t TEST_MESSAGE_LENGTH = 100;
std::uint8_t testMessageData[TEST_MESSAGE_LENGTH] = {0};

isobus::CANNetworkManager::CANNetwork.get_fast_packet_protocol(0)->send_multipacket_message(
	0x1F001,                                            // PGN
	testMessageData,                                    // 데이터
	TEST_MESSAGE_LENGTH,                                // 길이 (최대 223)
	TestInternalECU,                                    // 송신 내부 CF
	nullptr,                                            // 목적지 — nullptr이면 브로드캐스트
	isobus::CANIdentifier::CANPriority::PriorityLowest7, // 우선순위
	nmea2k_transmit_complete_callback);                 // 완료 콜백 (선택)
```

위 호출은 `TestInternalECU`에서 브로드캐스트 주소로 PGN 0x1F001의 100바이트 메시지를 보낸다.

전체 시그니처는 다음과 같다.

```cpp
bool send_multipacket_message(std::uint32_t parameterGroupNumber,
                              const std::uint8_t *data,
                              std::uint8_t messageLength,
                              std::shared_ptr<InternalControlFunction> source,
                              std::shared_ptr<ControlFunction> destination,
                              CANIdentifier::CANPriority priority = CANIdentifier::CANPriority::PriorityDefault6,
                              TransmitCompleteCallback txCompleteCallback = nullptr,
                              void *parentPointer = nullptr,
                              DataChunkCallback frameChunkCallback = nullptr);
```

`messageLength`가 `std::uint8_t`인 점에 주목할 만하다. 223바이트 상한이 타입 수준에서 드러나 있다.

### 4.2. 수신

Fast Packet으로 온 메시지를 받으려면, 해당 PGN을 <strong>Fast Packet으로 해석하라</strong>고 스택에 알려줘야 한다. 그러지 않으면 스택은 그 PGN의 프레임들을 그냥 8바이트짜리 일반 메시지 여러 개로 취급한다.

```cpp
void nmea2k_callback(const isobus::CANMessage &message, void *)
{
	// 재조립된 Fast Packet 메시지가 여기로 들어온다
}

isobus::CANNetworkManager::CANNetwork.get_fast_packet_protocol(0)->register_multipacket_message_callback(
	0x1F001, nmea2k_callback, nullptr);

// 더 이상 필요 없어지면 해제한다
isobus::CANNetworkManager::CANNetwork.get_fast_packet_protocol(0)->remove_multipacket_message_callback(
	0x1F001, nmea2k_callback, nullptr);
```

`register_multipacket_message_callback`의 네 번째 인자로 `std::shared_ptr<InternalControlFunction>`을 넘기면, 그 내부 CF를 목적지로 하는 메시지만 콜백을 받는다. `nullptr`(기본값)이면 아무 내부 CF로 온 메시지와 브로드캐스트를 모두 받는다.

내부 CF가 아닌 다른 CF들 사이의 Fast Packet 트래픽까지 엿보고 싶다면 `allow_any_control_function(true)`를 호출하면 된다.

::: details 원문 문서와 현재 API의 차이
공식 튜토리얼 문서는 `isobus::FastPacketProtocol::Protocol.send_multipacket_message(...)` 형태의 전역 인스턴스 접근을 보여준다. 하지만 현재 저장소의 헤더와 `examples/nmea2000/fast_packet_protocol/main.cpp`는 CAN 채널별 인스턴스를 반환하는 `CANNetworkManager::CANNetwork.get_fast_packet_protocol(채널번호)` 방식을 쓴다. Fast Packet 프로토콜 관리자가 채널마다 하나씩 존재하도록 바뀐 결과다. 새로 코드를 쓴다면 예제 쪽 형태를 따르면 된다.
:::

## 5. 진행 중인 세션 관찰하기

큰 메시지 전송은 시간이 걸린다. 진행 상황을 보고 싶다면 네트워크 매니저에서 활성 세션 목록을 가져올 수 있다.

```cpp
std::list<std::shared_ptr<isobus::TransportProtocolSessionBase>>
	get_active_transport_protocol_sessions(std::uint8_t canPortIndex) const;
```

반환되는 `TransportProtocolSessionBase`에서 쓸 만한 것들은 다음과 같다.

| 메서드 | 반환 | 설명 |
|---|---|---|
| `get_direction()` | `Direction` | `Transmit` 또는 `Receive` |
| `get_message_length()` | `std::uint32_t` | 이 세션이 다루는 전체 바이트 수 |
| `get_total_bytes_transferred()` | `std::uint32_t` | 지금까지 보내거나 받은 바이트 수 |
| `get_percentage_bytes_transferred()` | `float` | 0 ~ 100 사이 진행률 |
| `get_source()` / `get_destination()` | `std::shared_ptr<ControlFunction>` | 송신·수신 CF |
| `get_parameter_group_number()` | `std::uint32_t` | 세션의 PGN |

예제(`examples/transport_layer/main.cpp`)는 이걸로 진행률 막대를 그린다.

```cpp
std::shared_ptr<isobus::TransportProtocolSessionBase> session = nullptr;

if (isobus::CANNetworkManager::CANNetwork.send_can_message(PARAMETER_GROUP_NUMBER, sendBuffer.data(), message_length, originatorECU, recipientPartner))
{
	session = isobus::CANNetworkManager::CANNetwork.get_active_transport_protocol_sessions(0).front();
}

// ...

float percentage = session->get_percentage_bytes_transferred();
```

::: warning 세션 포인터는 언제든 사라진다
`get_active_transport_protocol_sessions`가 돌려주는 것은 세션에 대한 포인터일 뿐이고, 세션은 언제든 완료되거나 실패해 없어질 수 있다. 예제는 이 점을 이용해 `session.use_count() == 1`(내가 유일한 소유자다 = 스택은 이미 손을 뗐다)로 세션 종료를 감지한다.
:::

## 6. 정리

전송 계층을 쓸 때 실제로 신경 쓸 것은 이 정도로 좁혀진다.

- 일반 메시지는 <strong>크기만 키워서</strong> `send_can_message`를 호출하면 된다. 프로토콜 선택은 스택이 한다.
- 수신은 <strong>아무것도 바꾸지 않아도</strong> 재조립된 메시지가 콜백으로 온다.
- 브로드캐스트는 1785바이트 상한이 있고 느리므로, 가능하면 목적지를 지정한다.
- <strong>Fast Packet만</strong> 송신 API와 수신 등록이 별도다.

::: tip 핵심 정리
- `send_can_message`에 8바이트 초과 페이로드를 넘기면 TP(≤1785B) → ETP(≤117,440,505B) 순으로 시도되고, 둘 다 안 되면 단일 프레임으로 나간다.
- ETP는 브로드캐스트를 지원하지 않는다. 브로드캐스트 상한은 TP의 1785바이트다.
- BAM은 프레임 간 의무 지연 때문에 느리고, 동시에 하나만 진행된다.
- PGN 콜백은 크기와 무관하게 동작한다. TP/ETP로 온 메시지도 재조립된 상태로 한 번에 온다.
- Fast Packet은 최대 223바이트이고, `get_fast_packet_protocol(채널)`의 `send_multipacket_message` / `register_multipacket_message_callback`로 명시적으로 다뤄야 한다.
- `get_active_transport_protocol_sessions(채널)`로 진행률을 볼 수 있지만, 세션 객체는 언제든 사라질 수 있다.
:::

## 참고

- 원문: [Using the Transport Layer — AgIsoStack++ Documentation](https://isobus-plus-plus.readthedocs.io/en/latest/Tutorials/Transport%20Layer.html)
- 원문: [Transport Protocol API — AgIsoStack++ Documentation](https://isobus-plus-plus.readthedocs.io/en/latest/api/network/transport%20protocols.html)
- 예제: [`examples/transport_layer`](https://github.com/Open-Agriculture/AgIsoStack-plus-plus/tree/main/examples/transport_layer), [`examples/nmea2000/fast_packet_protocol`](https://github.com/Open-Agriculture/AgIsoStack-plus-plus/tree/main/examples/nmea2000/fast_packet_protocol)

## 다음 챕터
[CH11. PGN 요청](/study/agisostack/11-pgn-requests)으로 이어진다.
