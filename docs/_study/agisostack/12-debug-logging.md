---
title: "디버그 로깅"
description: "CANStackLogger를 상속해 커스텀 로그 싱크를 만들고, 로그로 ISOBUS 문제를 진단하는 방법."
date: 2026-07-20
tags: [AgIsoStack, ISOBUS, C++]
---

# 디버그 로깅

## 학습 목표
- `CANStackLogger`를 상속해 커스텀 로거를 만들 수 있다.
- `sink_CAN_stack_log`를 오버라이드해 로그를 원하는 곳으로 흘려보낼 수 있다.
- 로거 인스턴스가 왜 `static`이어야 하는지 설명할 수 있다.
- 로그 레벨 다섯 단계를 알고, 상황에 맞게 조절할 수 있다.
- 로그 접두 태그로 문제 지점을 좁히고, 주소 클레임 실패·파트너 미발견·TP 세션 abort를 로그에서 식별할 수 있다.

## 1. 로그가 흘러가는 경로

CAN 스택에는 디버그 로깅이 내장돼 있다. 이걸로 애플리케이션의 문제, ISOBUS 통신의 문제, 심지어 스택 자체의 문제까지 찾을 수 있다.

로깅은 <strong>가상 클래스</strong> 형태로 제공된다. 이 클래스를 구현하면 로그를 원하는 어떤 목적지로든 흘려보낼 수 있다.

![로거 파이프라인](/images/study-agisostack/12-logger-pipeline-light.png)
![로거 파이프라인](/images/study-agisostack/12-logger-pipeline-dark.png)

스택 내부는 `LOG_DEBUG`, `LOG_INFO`, `LOG_WARNING`, `LOG_ERROR`, `LOG_CRITICAL` 매크로로 로그를 남긴다. 이 매크로들은 `CANStackLogger`의 정적 함수를 거쳐 `CAN_stack_log(level, text)`로 모이고, 여기서 현재 로그 레벨보다 낮은 것은 <strong>버려진다</strong>. 살아남은 로그만 내가 등록한 싱크의 `sink_CAN_stack_log`로 전달된다.

::: info 로깅을 통째로 빼고 싶다면
`DISABLE_CAN_STACK_LOGGER`를 정의하고 빌드하면 `LOG_*` 매크로가 전부 빈 매크로로 치환된다. 로그 문자열과 포맷팅 코드 자체가 바이너리에서 사라지므로, 자원이 빠듯한 임베디드 타깃에서 유용하다.
:::

## 2. 커스텀 로거 만들기

스택의 로그를 받아 `stdout`으로 뿌리는 아주 단순한 로거를 써 보자.

```cpp
#include "isobus/isobus/can_stack_logger.hpp"
#include <iostream>

class CustomLogger : public isobus::CANStackLogger
{
public:
	void sink_CAN_stack_log(CANStackLogger::LoggingLevel level, const std::string &text) override
	{
		std::cout << text << std::endl;
	}
};
```

스택의 `CANStackLogger`를 상속하고 `sink_CAN_stack_log` 함수를 구현했다. 이 예제에서는 스택이 로깅하는 텍스트가 콘솔에 출력된다.

원한다면 `level` 파라미터로 로깅 레벨을 확인해서, 심각도에 따라 다른 동작을 할 수 있다. 아니면 [spdlog](https://github.com/gabime/spdlog) 같은 평소 쓰던 로거로 이 텍스트를 넘겨도 된다.

```cpp
class CustomLogger : public isobus::CANStackLogger
{
public:
	void sink_CAN_stack_log(CANStackLogger::LoggingLevel level, const std::string &text) override
	{
		switch (level)
		{
			case LoggingLevel::Critical:
			case LoggingLevel::Error:
				std::cerr << "[ISOBUS] " << text << std::endl;
				break;

			default:
				std::cout << "[ISOBUS] " << text << std::endl;
				break;
		}
	}
};
```

이제 이 로거의 <strong>정적 인스턴스</strong>를 만들고, 스택에게 이걸 쓰라고 알려주면 된다.

```cpp
static CustomLogger logger;

isobus::CANStackLogger::set_can_stack_logger_sink(&logger);

// 로그 레벨을 바꾸고 싶다면 아래처럼 한다. 기본값은 Info다.
isobus::CANStackLogger::set_log_level(isobus::CANStackLogger::LoggingLevel::Debug);
```

::: warning 로거는 static이어야 한다
CAN 스택은 넘겨받은 로거 객체에 대한 <strong>레퍼런스만 저장한다</strong>. 그러므로 로거는 `static`이거나, 어떤 식으로든 스코프를 벗어나지 않아야 한다. 지역 변수로 만들어 넘기면 함수가 끝나는 순간 댕글링 포인터가 된다.
:::

이게 전부다. 이제 프로그램을 실행하면 콘솔에 로그 메시지들이 찍히기 시작한다.

::: details 원문 문서와 현재 소스의 차이
공식 튜토리얼은 로그 레벨을 `LoggingLevel::DEBUG`처럼 대문자로 표기한다. 하지만 현재 저장소의 `isobus/include/isobus/isobus/can_stack_logger.hpp`에 정의된 enum 값은 `Debug`, `Info`, `Warning`, `Error`, `Critical`이다. 파스칼 케이스를 쓰면 된다.
:::

## 3. 로그 레벨

`LoggingLevel`은 다섯 단계이고, 값이 낮을수록 상세하다.

```cpp
enum class LoggingLevel
{
	Debug = 0, ///< 상세 정보
	Info,      ///< 일반적인 상태 정보, 정상 동작 상황에 대한 메시지
	Warning,   ///< 정상 동작을 멈추지는 않지만 문제 해결 시 참고할 만한 사안
	Error,     ///< 정상 동작을 방해하는 문제
	Critical   ///< 스택이 제대로 동작하려면 반드시 해결해야 하는 근본적 문제
};
```

`set_log_level`로 지정한 레벨보다 <strong>낮은</strong> 로그는 싱크에 도달하지 않고 버려진다. 현재 설정은 `get_log_level()`로 읽을 수 있다.

| 상황 | 권장 레벨 |
|---|---|
| 처음 브링업, 주소 클레임·연결이 안 될 때 | `Debug` |
| 평상시 개발 | `Info` (기본값) |
| 필드 배포, 로그 용량이 부담될 때 | `Warning` 이상 |

실무에서 가장 흔한 실수는, 문제가 생겼는데 레벨이 `Info`로 남아 있어 정작 필요한 `[TP]` 세션 상태 로그(대부분 `Debug`)를 못 보는 것이다. 무언가 안 되면 <strong>먼저 `Debug`로 내려라</strong>.

## 4. 로그로 무엇을 진단할 수 있나

스택이 남기는 로그는 대부분 `[AC]`, `[TP]`, `[VT]` 같은 <strong>접두 태그</strong>로 시작한다. 이 태그만 봐도 문제가 어느 층에 있는지 절반은 좁혀진다.

![로그 태그별 진단 지도](/images/study-agisostack/12-log-triage-light.png)
![로그 태그별 진단 지도](/images/study-agisostack/12-log-triage-dark.png)

### 4.1. 주소 클레임 실패 — `[AC]`

내 ECU가 버스에 올라오지 못하는 가장 흔한 원인이다. `Critical` 레벨로 다음 로그가 찍힌다면 주소를 하나도 확보하지 못한 것이다.

```text
[AC]: Internal control function 00000000xxxxxxxx failed to claim an address on channel 0
```

NAME이 <strong>임의 주소를 허용하지 않는데</strong> 선호 주소가 이미 점유돼 있고 경합에서 졌다면 `Error`로 이렇게 나온다.

```text
[AC]: Internal control function ... failed to claim its preferred address ... as it cannot
tolerate for an arbitrary address and there is already a CF at the preferred address that
wins contention.
```

이 경우 해법은 둘 중 하나다. 선호 주소를 비어 있는 값으로 바꾸거나, NAME의 `set_arbitrary_address_capable(true)`로 임의 주소를 허용하는 것이다.

주소를 확보했다가 나중에 빼앗기는 경우도 로그로 드러난다.

```text
[AC]: Internal control function ... must re-arbitrate its address because it was stolen by
another ECU with NAME ...
```

::: info 관련 스터디
주소 경합의 규칙과 NAME 값이 우선순위를 어떻게 결정하는지는 [ISOBUS CH10. J1939 주소 관리](/study/isobus/10-j1939-address), 그리고 이 스터디의 [CH3. 제어 함수와 NAME](/study/agisostack/03-control-function-name)에서 다뤘다.
:::

### 4.2. 파트너를 못 찾을 때 — `[NM]`

파트너 제어 함수를 만들었는데 아무 통신도 일어나지 않는다면, 상대가 아직 주소를 클레임하지 않았거나 NAME 필터가 맞지 않는 것이다. 상대가 정상적으로 발견되면 `[NM]` 태그로 다음 로그가 남는다.

```text
[NM]: A partner with name 00000000xxxxxxxx has claimed address 26 on channel 0
```

이 줄이 <strong>안 보인다면</strong> 확인할 순서는 이렇다.

1. 버스에 상대 ECU의 Address Claimed 메시지가 실제로 흐르는가. `[NM]: A control function claimed address ... on channel ...` 로그로 확인한다.
2. 클레임은 되는데 파트너로 인식이 안 된다면, `NAMEFilter` 조건이 상대의 실제 NAME 필드와 일치하는지 확인한다.

주소가 유효하지 않은 CF로 메시지를 보내려 하면 다음 경고가 나온다.

```text
[NM]: Cannot send a message with PGN ...
```

### 4.3. TP 세션 abort — `[TP]` / `[ETP]` / `[FP]`

멀티프레임 전송이 실패할 때 가장 유용한 로그들이다. 세션이 정상적으로 시작되면 `Debug` 레벨로 다음이 찍힌다.

```text
[TP]: New tx session for 0x0EF00. Source: 28, destination: 29
[TP]: New broadcast tx session for 0x0EF00. Source: 28
```

상대가 세션을 중단시키면 `Error`로 abort 사유 코드가 함께 남는다.

```text
[TP]: Received an abort (reason=1) for a tx session for parameterGroupNumber 0x0EF00
[TP]: Received an abort (reason=1) for an rx session for parameterGroupNumber 0x0EF00
```

그 밖에 자주 보이는 것들과 의미를 정리하면 다음과 같다.

| 로그 | 무슨 일이 일어난 것인가 |
|---|---|
| `Ignoring Broadcast Announcement Message (BAM) ... configured maximum number of sessions reached` | 동시 수신 세션 한도를 넘었다. 네트워크 설정을 조정하거나 송신 측 빈도를 줄여야 한다 |
| `Received a Request To Send (RTS) while a session already existed ... aborting` | 같은 송신·수신 쌍에 대해 세션이 중복 시작됐다 |
| `Received a Clear To Send (CTS) message ... with a bad sequence number, aborting` | 프레임 유실이나 순서 꼬임. 버스 부하나 배선을 의심한다 |
| `Received a Broadcast Announcement Message (BAM) with a non-global destination, ignoring` | 상대가 BAM을 잘못된 목적지로 보냈다 |
| `Received a Data Transfer message from ... while not expecting one, sending abort` | 핸드셰이크 없이 데이터가 들어왔다 |

::: info 관련 스터디
abort 사유 코드의 의미와 RTS/CTS 타이밍 규칙은 [ISOBUS CH11. J1939 Transport Protocol](/study/isobus/11-j1939-transport)에 정리돼 있다. 전송 API 사용법은 [CH10. 전송 계층 사용하기](/study/agisostack/10-transport-layer)를 참고하면 된다.
:::

### 4.4. VT 연결 문제 — `[VT]`

Virtual Terminal 클라이언트가 화면을 못 띄울 때는 `[VT]` 태그를 따라가면 된다. 상태 머신의 각 단계가 타임아웃될 때마다 `Error`로 어느 단계인지 알려준다.

```text
[VT]: Get Versions Response Timeout
[VT]: Get End of Object Pool Response Timeout
[VT]: An object pool failed to upload. Resetting connection to VT.
[VT]: The VT Server is NACK-ing our VT messages. Disconnecting.
[VT]: Ready to upload pool, but VT server has timed out. Disconnecting.
```

어느 단계에서 멈췄는지가 곧 원인의 위치다. 오브젝트 풀 업로드 실패라면 풀 자체나 VT 버전 호환성을, `Status Timeout`이라면 VT 서버와의 연결 유지를 본다.

## 5. 실전 팁

::: tip 로그를 쓸모 있게 만드는 습관
- <strong>타임스탬프를 붙여라.</strong> 스택은 시각 정보를 넣지 않는다. 싱크에서 직접 붙이면 타임아웃 문제를 훨씬 빨리 잡을 수 있다.
- <strong>레벨을 같이 남겨라.</strong> `level` 파라미터를 문자열로 변환해 함께 출력하면 `Warning` 이상만 훑어볼 수 있다.
- <strong>파일로도 남겨라.</strong> 필드에서 재현되는 문제는 콘솔이 없다. 회전 로그 파일로 남기면 사후 분석이 가능하다.
- <strong>싱크에서 오래 걸리는 일을 하지 마라.</strong> `sink_CAN_stack_log`는 스택 스레드에서 호출된다. 네트워크 전송 같은 무거운 작업은 큐에 넣고 다른 스레드에서 처리한다.
- <strong>스레드 안전은 스택이 보장한다.</strong> 로거는 뮤텍스로 보호되므로 여러 스레드에서 로그가 들어와도 싱크 호출은 직렬화된다.
:::

::: details 내 애플리케이션 로그도 같은 싱크로 보내기
`CANStackLogger`의 정적 헬퍼는 애플리케이션에서도 그대로 쓸 수 있다. printf 스타일 포맷팅도 지원한다.

```cpp
isobus::CANStackLogger::info("내 앱 시작. 채널 %u", 0);
isobus::CANStackLogger::error("설정 파일을 읽지 못했다: %s", path.c_str());
```

스택 로그와 앱 로그가 한 스트림에 시간 순으로 섞이므로, "우리 코드가 X를 한 직후에 스택이 Y로 실패했다" 같은 인과 관계를 읽기 쉬워진다.
:::

::: tip 핵심 정리
- `isobus::CANStackLogger`를 상속하고 `sink_CAN_stack_log(level, text)`를 오버라이드하면 로그를 원하는 곳으로 보낼 수 있다.
- `set_can_stack_logger_sink(&logger)`로 등록하며, 스택은 <strong>레퍼런스만 저장</strong>하므로 로거는 `static`이어야 한다.
- 레벨은 `Debug` < `Info` < `Warning` < `Error` < `Critical`이고 기본값은 `Info`다. `set_log_level`로 바꾼다.
- 문제가 생기면 먼저 `Debug`로 내려라. `[TP]` 세션 진행 로그 같은 결정적 단서가 대부분 `Debug` 레벨이다.
- 접두 태그로 층을 좁힌다. `[AC]` 주소 클레임, `[NM]` 네트워크 매니저·파트너 발견, `[TP]`/`[ETP]`/`[FP]` 멀티프레임 전송, `[VT]` Virtual Terminal, `[TC]`/`[DDOP]` Task Controller.
- `DISABLE_CAN_STACK_LOGGER`를 정의하면 로깅 코드가 바이너리에서 제거된다.
:::

## 참고

- 원문: [Debug Logging — AgIsoStack++ Documentation](https://isobus-plus-plus.readthedocs.io/en/latest/Tutorials/Debug%20Logging.html)
- 소스: [`isobus/include/isobus/isobus/can_stack_logger.hpp`](https://github.com/Open-Agriculture/AgIsoStack-plus-plus/blob/main/isobus/include/isobus/isobus/can_stack_logger.hpp)
- 예제: [`examples/virtual_terminal/version3_object_pool/main.cpp`](https://github.com/Open-Agriculture/AgIsoStack-plus-plus/blob/main/examples/virtual_terminal/version3_object_pool/main.cpp)

## 다음 챕터
[CH13. Virtual Terminal 클라이언트](/study/agisostack/13-virtual-terminal)로 이어진다.
