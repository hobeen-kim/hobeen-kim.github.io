---
title: "PGN 요청"
description: "ParameterGroupNumberRequestProtocol로 PGN 요청과 반복 주기 요청을 주고받는 방법."
date: 2026-07-20
tags: [AgIsoStack, ISOBUS, C++]
---

# PGN 요청

## 학습 목표
- PGN 요청이 무엇이고 어떤 응답이 가능한지 설명할 수 있다.
- `ParameterGroupNumberRequestProtocol` 인스턴스를 얻어 사용할 수 있다.
- 다른 CF에게 PGN을 요청하는 코드를 작성할 수 있다.
- PGN 요청 콜백을 등록하고, ACK/NACK를 스택에 위임하거나 직접 응답할 수 있다.
- 반복 주기 요청(Request for Repetition Rate)을 보내고 받을 수 있다.
- 스택이 자동으로 NACK하는 경우와 하지 않는 경우를 구분할 수 있다.

## 1. PGN 요청이란

누군가 나에게 PGN을 요청한다는 것은, <strong>그 PGN의 메시지를 보내달라</strong>거나 <strong>그에 해당하는 동작을 해달라</strong>고 정중히 부탁하는 것이다.

받는 쪽에는 세 가지 선택지가 있다.

1. 요청한 데이터를 담아 그 PGN의 메시지를 보낸다.
2. Acknowledgement PGN을 보낸다. 긍정이면 ACK, 부정이면 NACK다.
3. 아무것도 하지 않는다.

관련된 PGN은 두 개다.

| PGN | 값 | 용도 |
|---|---|---|
| Request | 59904 (0xEA00) | 다른 PGN을 요청 |
| Request for Repetition Rate | 52224 (0xCC00) | 특정 PGN을 주기적으로 보내달라고 요청 |

::: info 목적지 지정 PGN이다
둘 다 목적지 지정(destination specific) PGN이다. `candump`으로 버스를 들여다보면 뒤쪽 `00` 자리에 <strong>목적지 주소가 채워져</strong> 나타난다. 예를 들어 주소 0x1C로 보내는 요청은 `EA1C`로 보인다. PDU1 형식과 목적지 주소가 어떻게 인코딩되는지는 [ISOBUS CH9. J1939 메시지 구조](/study/isobus/09-j1939-message)를 참고하면 된다.
:::

ISOBUS에서 자주 쓰이는 상호작용 대부분이 이 두 PGN 위에 놓여 있다. 다른 CF에게 PGN을 요청하고, 남의 요청에 응답하고, 어떤 PGN을 일정 간격으로 보내달라고 부탁하고, 그런 부탁에 제대로 응답하는 것 말이다. 라이브러리는 이걸 PGN마다 직접 처리하는 것보다 훨씬 간단하게 만들어 주는 클래스를 제공한다.

## 2. 프로토콜 인스턴스 얻기

PGN 요청 프로토콜을 쓰려면 먼저 <strong>내부 제어 함수(Internal Control Function)</strong>가 있어야 한다. 프로토콜은 내부 CF에 <strong>귀속</strong>돼 있고, `get_pgn_request_protocol()`로 접근한다. 별도의 셋업 호출은 필요 없다.

```cpp
#include "isobus/isobus/can_parameter_group_number_request_protocol.hpp"

auto pgnRequestProtocol = internalECU->get_pgn_request_protocol().lock();
```

`get_pgn_request_protocol()`은 `std::weak_ptr`를 반환하므로 `.lock()`으로 `shared_ptr`을 얻어 쓴다. 반환값이 비어 있을 수 있으니 확인하고 쓰는 편이 안전하다.

이 시점부터 라이브러리는 <strong>내 대신 요청을 처리하기 시작한다</strong>. 기본 동작은 이렇다. 명시적으로 처리하겠다고 등록한 PGN이 아니면, 목적지 지정 요청에 대해 <strong>전부 NACK</strong>한다. 등록한 PGN에 대한 요청만 콜백으로 애플리케이션에 전달된다.

![PGN 요청 수신 경로](/images/study-agisostack/11-pgn-request-flow-light.png)
![PGN 요청 수신 경로](/images/study-agisostack/11-pgn-request-flow-dark.png)

## 3. PGN 요청 보내기

내부 CF를 만들었다면, 요청 보내기는 정적 함수 한 번이면 된다.

```cpp
static bool request_parameter_group_number(std::uint32_t pgn,
                                           std::shared_ptr<InternalControlFunction> source,
                                           std::shared_ptr<ControlFunction> destination);
```

요청할 PGN과, 어느 CF에게 요청할지를 넘긴다.

```cpp
isobus::ParameterGroupNumberRequestProtocol::request_parameter_group_number(
	static_cast<std::uint32_t>(isobus::CANLibParameterGroupNumber::ProprietaryA),
	TestInternalECU,
	nullptr);
```

`destination`에 `nullptr`을 넘기면 <strong>모든 CF에게 브로드캐스트</strong>로 요청한다. 허용은 되지만 일반적으로 좋은 생각은 아니다. 버스 위 전원에게 묻는 것보다는 파트너 제어 함수를 지정하는 편이 훨씬 낫다.

::: info 관련 스터디
파트너 제어 함수를 만들고 NAME 필터로 상대를 찾는 방법은 [CH9. 목적지 지정하기](/study/agisostack/09-adding-destination)에서 다뤘다.
:::

## 4. PGN 요청 받기

내 내부 CF 앞으로 PGN 요청이 오면 스택이 콜백을 불러 준다. 그 안에서 요청받은 데이터를 직접 송신해도 되고, 스택에게 대신 ACK/NACK를 보내달라고 지시해도 되고, 아무것도 안 해도 된다.

### 4.1. 콜백 작성

`PGNRequestCallback` 타입에 맞는 함수를 만든다.

```cpp
bool example_proprietary_a_pgn_request_handler(std::uint32_t parameterGroupNumber,
                                               std::shared_ptr<isobus::ControlFunction> requestingControlFunction,
                                               bool &acknowledge,
                                               isobus::AcknowledgementType &acknowledgeType,
                                               void *)
{
    if (static_cast<std::uint32_t>(isobus::CANLibParameterGroupNumber::ProprietaryA) == parameterGroupNumber)
    {
        acknowledge = true;
        acknowledgeType = isobus::AcknowledgementType::Positive;
        return true;
    }

    return false;
}
```

각 파라미터의 의미는 다음과 같다.

| 파라미터 | 의미 |
|---|---|
| `parameterGroupNumber` | 요청받은 PGN |
| `requestingControlFunction` | 요청한 상대 CF. 응답을 직접 보낼 때 목적지로 쓴다 |
| `acknowledge` (out) | `true`로 두면 스택이 대신 Acknowledgement PGN을 보낸다 |
| `acknowledgeType` (out) | 보낼 응답의 종류 |
| 반환값 | `true`면 "내가 이 PGN을 처리했다", `false`면 "나는 모르는 PGN이다" |

반환값이 중요하다. `false`를 반환하면 스택은 <strong>이 PGN을 처리할 다른 콜백을 계속 찾는다</strong>. 등록된 콜백이 여러 개일 때 체인처럼 동작한다.

`AcknowledgementType`은 네 가지다.

```cpp
enum class AcknowledgementType : std::uint8_t
{
    Positive = 0,     ///< "ACK" 요청이 완료됨
    Negative = 1,     ///< "NACK" 요청이 완료되지 않았거나 이 PGN을 지원하지 않음
    AccessDenied = 2, ///< 요청자의 CF에게는 이 PGN을 요청할 권한이 없음
    CannotRespond = 3 ///< 어떤 이유로든 요청을 받아들일 수 없음
};
```

### 4.2. 콜백 등록

만든 함수를 프로토콜에 등록한다. 여기서는 ProprietaryA(PROPA) PGN을 예로 든다.

```cpp
// 프로토콜 인스턴스를 얻는다
auto pgnRequestProtocol = internalECU->get_pgn_request_protocol().lock();

if (pgnRequestProtocol)
{
    pgnRequestProtocol->register_pgn_request_callback(
        static_cast<std::uint32_t>(isobus::CANLibParameterGroupNumber::ProprietaryA),
        example_proprietary_a_pgn_request_handler,
        nullptr);
}
```

세 번째 인자 `parentPointer`는 컨텍스트 변수다. 보통 콜백을 등록하는 클래스의 `this` 포인터를 넘겨, 콜백 안에서 자기 인스턴스로 되돌아갈 때 쓴다.

등록을 해제할 때는 `remove_pgn_request_callback`에 같은 인자를 넘긴다. 현재 등록된 개수는 `get_number_registered_pgn_request_callbacks()`로 확인할 수 있다.

### 4.3. 응답 규칙

::: warning 알아둬야 할 규칙들
- 요청이 <strong>글로벌 주소</strong>로 왔다면 응답도 글로벌 주소로 보낸다. 라이브러리는 현재 ACK/NACK 응답을 항상 브로드캐스트 주소로 보낸다. 다만 애플리케이션이 직접 만드는 응답은 원하는 대로 보내면 되고, 스택의 ACK/NACK 기능 사용은 <strong>완전히 선택</strong>이다.
- 글로벌 요청에 NACK를 보내는 것은 바람직하지 않다. 스택은 글로벌 요청에 대해 NACK를 보내지 않는다.
- <strong>지원하지 않는 PGN에는 NACK가 필수</strong>다. 이 규칙을 지키려면 만드는 모든 내부 CF에 PGN 요청 프로토콜을 쓰는 것이 강력히 권장된다. 처리하라고 스택에 맡겨 두기만 하면, 처리되지 않은 요청은 스택이 알아서 NACK한다.
- 특정 내부 CF로 오는 <strong>모든 PGN</strong>을 하나의 콜백으로 처리하고 싶다면, 메타 PGN인 `isobus::CANLibParameterGroupNumber::Any`로 등록하면 된다.
:::

## 5. 반복 주기 요청 보내기

반복 주기 요청은 다른 CF에게 "이 PGN을 내가 원하는 간격으로 보내 달라"고 말하는 것이다. 정확한 간격을 상대에게 맡기고 싶다면 <strong>0</strong>을 요청하면 된다.

```cpp
static bool request_repetition_rate(std::uint32_t pgn,
                                    std::uint16_t repetitionRate_ms,
                                    std::shared_ptr<InternalControlFunction> source,
                                    std::shared_ptr<ControlFunction> destination);
```

```cpp
isobus::ParameterGroupNumberRequestProtocol::request_repetition_rate(
	static_cast<std::uint32_t>(isobus::CANLibParameterGroupNumber::ProprietaryA),
	100,  // 100 ms 간격으로 보내달라
	TestInternalECU,
	myPartner);
```

::: warning 이 메시지에 관한 중요한 사실들
- 제어 함수는 이 메시지를 버스에서 감시할 <strong>의무가 없다</strong>.
- 요청받은 주기를 쓸 수 없거나 쓰고 싶지 않은 CF는 — 고정 타이밍 제어 루프를 가진 시스템이라면 흔한 일이다 — 이 메시지를 <strong>무시해도 된다</strong>.
- 반복 주기에 대한 응답을 받지 못했다면, 요청자는 요청이 <strong>받아들여지지 않았다고 간주해야</strong> 한다. 그다음을 어떻게 처리할지는 애플리케이션의 몫이다.
:::

## 6. 반복 주기 요청 받기

내 내부 CF 앞으로 반복 주기 요청이 오면 역시 콜백을 받을 수 있다. 여기서 핵심은 <strong>실제 주기 송신은 스택이 아니라 애플리케이션이 한다</strong>는 점이다. 스택은 대부분의 PGN에 대해 애플리케이션이 무슨 데이터를 보내야 하는지 알지 못한다.

![반복 주기 요청 흐름](/images/study-agisostack/11-repetition-rate-light.png)
![반복 주기 요청 흐름](/images/study-agisostack/11-repetition-rate-dark.png)

### 6.1. 콜백 작성

`PGNRequestForRepetitionRateCallback` 타입에 맞는 함수를 만든다.

```cpp
bool example_proprietary_a_request_for_repetition_rate_handler(std::uint32_t parameterGroupNumber,
                                                               std::shared_ptr<isobus::ControlFunction> requestingControlFunction,
                                                               std::shared_ptr<isobus::ControlFunction> targetControlFunction,
                                                               std::uint32_t repetitionRate,
                                                               void *)
{
    if (static_cast<std::uint32_t>(isobus::CANLibParameterGroupNumber::ProprietaryA) == parameterGroupNumber)
    {
        return true;
    }

    return false;
}
```

PGN 요청 콜백과 달리 `acknowledge` 계열 출력 파라미터가 없다. 대신 요청된 주기(`repetitionRate`, 밀리초)와 대상 CF가 들어온다.

실제 예제는 요청자와 주기를 저장해 두고, 메인 루프에서 그 주기로 송신한다.

```cpp
static std::uint32_t propARepetitionRate_ms = 0xFFFFFFFF;
static std::shared_ptr<isobus::ControlFunction> repetitionRateRequestor = nullptr;

// ... 콜백 안에서
repetitionRateRequestor = requestingControlFunction;
propARepetitionRate_ms = repetitionRate;

// ... 메인 루프에서
while (running)
{
	if (0xFFFFFFFF != propARepetitionRate_ms)
	{
		std::array<std::uint8_t, isobus::CAN_DATA_LENGTH> buffer = { 0 };
		isobus::CANNetworkManager::CANNetwork.send_can_message(
			static_cast<std::uint32_t>(isobus::CANLibParameterGroupNumber::ProprietaryA),
			buffer.data(),
			isobus::CAN_DATA_LENGTH,
			TestInternalECU,
			repetitionRateRequestor);
		std::this_thread::sleep_for(std::chrono::milliseconds(propARepetitionRate_ms));
	}
	else
	{
		std::this_thread::sleep_for(std::chrono::milliseconds(5));
	}
}
```

### 6.2. 콜백 등록

```cpp
// 프로토콜 인스턴스를 얻는다
auto pgnRequestProtocol = internalECU->get_pgn_request_protocol().lock();

// PROPA PGN에 대한 반복 주기 요청을 처리할 콜백을 등록한다
if (pgnRequestProtocol)
{
    pgnRequestProtocol->register_request_for_repetition_rate_callback(
        static_cast<std::uint32_t>(isobus::CANLibParameterGroupNumber::ProprietaryA),
        example_proprietary_a_request_for_repetition_rate_handler,
        nullptr);
}
```

내 내부 CF에 귀속된 프로토콜 인스턴스를 스택에서 가져와, 이 경우엔 PROPA PGN에 대한 반복 주기 요청이 들어올 때마다 내 콜백을 불러 달라고 말하는 것이다.

해제는 `remove_request_for_repetition_rate_callback`, 등록 개수 확인은 `get_number_registered_request_for_repetition_rate_callbacks()`다.

모든 PGN을 처리할 필요는 없다. 관심 있는 것만 하면 된다. ISOBUS는 반복 주기 요청을 <strong>아무 응답 없이 전부 무시하는 것</strong>도 허용한다.

## 7. 두 콜백 비교

헷갈리기 쉬우니 나란히 놓고 정리한다.

| | PGN 요청 콜백 | 반복 주기 요청 콜백 |
|---|---|---|
| 타입 | `PGNRequestCallback` | `PGNRequestForRepetitionRateCallback` |
| 트리거 PGN | 59904 (0xEA00) | 52224 (0xCC00) |
| 등록 | `register_pgn_request_callback` | `register_request_for_repetition_rate_callback` |
| 추가 입력 | 없음 | `targetControlFunction`, `repetitionRate` |
| 출력 파라미터 | `acknowledge`, `acknowledgeType` | 없음 |
| 스택의 자동 응답 | 미등록 PGN은 자동 NACK | 없음 |
| 실제 데이터 송신 | 앱이 하거나, 스택에 ACK/NACK 위임 | <strong>전적으로 앱이 한다</strong> |

::: tip 핵심 정리
- PGN 요청(0xEA00)은 "이 PGN을 보내달라"는 부탁이고, 응답은 데이터 송신 / ACK / NACK / 무시 중 하나다.
- 프로토콜 인스턴스는 내부 CF에 귀속돼 있다. `internalECU->get_pgn_request_protocol().lock()`으로 얻는다.
- 등록하지 않은 PGN에 대한 목적지 지정 요청은 스택이 자동으로 NACK한다. 이는 규격 준수에 필요하다. 글로벌 요청에는 NACK를 보내지 않는다.
- 콜백이 `false`를 반환하면 스택은 다른 콜백을 계속 찾는다.
- `CANLibParameterGroupNumber::Any`로 등록하면 그 내부 CF의 모든 PGN 요청을 한 콜백에서 받는다.
- 반복 주기 요청(0xCC00)은 강제력이 없다. 상대는 무시해도 되고, 응답이 없으면 거절로 간주해야 한다.
- 반복 주기 요청을 받아들였다면, 정해진 간격으로 실제 메시지를 보내는 것은 <strong>애플리케이션의 책임</strong>이다.
:::

## 참고

- 원문: [PGN Requests — AgIsoStack++ Documentation](https://isobus-plus-plus.readthedocs.io/en/latest/Tutorials/PGN%20Requests.html)
- 예제: [`examples/pgn_requests/main.cpp`](https://github.com/Open-Agriculture/AgIsoStack-plus-plus/blob/main/examples/pgn_requests/main.cpp)

## 다음 챕터
[CH12. 디버그 로깅](/study/agisostack/12-debug-logging)으로 이어진다.
