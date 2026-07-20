---
title: "CH17. HardwareInterface"
description: "CANHardwareInterface의 스레드·큐 구조, CMake로 CAN 드라이버 고르기, CANHardwarePlugin을 상속해 직접 드라이버 만들기"
date: 2026-07-20
tags: [AgIsoStack, ISOBUS, CAN, 임베디드]
---

# CH17. HardwareInterface

## 학습 목표
- `CANHardwareInterface`가 왜 존재하는지, 어떤 스레드와 큐로 스택을 굴리는지 설명할 수 있다.
- 주기 스레드가 매 주기마다 수행하는 3단계를 순서대로 말할 수 있다.
- CMake `CAN_DRIVER` 변수로 내장 드라이버를 고르고, 여러 개를 동시에 넣을 수 있다.
- `CANHardwareInterface`를 초기화해 채널에 드라이버를 붙이고 시작·정지할 수 있다.
- `CANHardwarePlugin`을 상속해 지원되지 않는 하드웨어용 드라이버를 직접 만들 수 있다.

## 하드웨어 인터페이스는 무엇을 해결하는가

CAN 스택을 실제 하드웨어에 붙이려면 두 가지를 동시에 해야 한다. 하나는 버스에서 프레임이 흘러나오는 즉시 낚아채는 일이고, 다른 하나는 프로토콜 로직(주소 클레임, 전송 계층, VT/TC 클라이언트)을 일정한 주기로 돌리는 일이다. 이 둘은 성격이 다르다. 앞은 지연에 민감하고, 뒤는 순서에 민감하다.

`CANHardwareInterface` 클래스는 바로 이 둘을 갈라서 담당한다. 모든 CAN 드라이버와 스택이 공유하는 <strong>공통 큐 계층과 스레드 계층</strong>을 제공해서, 통합 작업을 단순하게 만들고 무엇보다 스택을 제대로 굴리는 데 필요한 함수 호출들이 <strong>일관되고 안전한 순서</strong>로 실행되도록 보장한다.

여기서 중요한 설계 결정이 하나 있다. CAN 메시지의 송수신 자체는 멀티스레드로 일어나지만, 스택은 <strong>수신 큐를 소비하고 프로토콜을 갱신하는 부분을 사실상 단일 스레드로 만든다</strong>. 덕분에 스택 코어에서 비싼 뮤텍스를 걸 필요가 없어지고, 복잡도가 크게 줄어든다.

그리고 `CANHardwareInterface`는 구체적인 드라이버가 아니라 CAN 드라이버의 <strong>제네릭 기반 클래스</strong>인 `CANHardwarePlugin`을 상대한다. 그래서 하드웨어 인터페이스 자체도 완전히 하드웨어 비종속적이다.

![하드웨어 계층 구조](/images/study-agisostack/17-hardware-layers-light.png)
![하드웨어 계층 구조](/images/study-agisostack/17-hardware-layers-dark.png)

## 스레드와 큐가 도는 방식

높은 수준에서 보면 하드웨어 인터페이스는 이렇게 동작한다.

<strong>수신 스레드</strong>: 하드웨어 인터페이스는 수신 큐를 채우는 스레드를 하나 돌린다. 이 스레드가 있어서 메시지가 하드웨어나 소켓에서 <strong>적시에</strong> 꺼내지고, 처리될 때까지 안전하게 보관된다.

<strong>주기 스레드</strong>: 하드웨어 인터페이스는 네트워크 매니저의 메인 주기 스레드도 돌린다. 이 스레드는 세 단계로 동작한다.

1. 주기 스레드가 <strong>수신 큐를 비운다</strong>. 메시지는 이 스레드 위에서 네트워크 매니저가 처리한다. 애플리케이션으로 향하는 콜백 상당수가 바로 이 스레드에서 호출된다.
2. 네트워크 매니저의 <strong>메인 업데이트 루틴</strong>이 실행된다. 여기서 모든 주요 프로토콜 로직이 돈다.
3. 주기 스레드가 <strong>송신 큐의 메시지를 내보낸다</strong>. 송신이 한 번 실패할 때까지 계속 시도한다.

그리고 몇 밀리초 뒤에 같은 단계를 다시 반복한다.

![주기 스레드 3단계](/images/study-agisostack/17-plugin-threads-light.png)
![주기 스레드 3단계](/images/study-agisostack/17-plugin-threads-dark.png)

::: tip 콜백이 어느 스레드에서 오는가
수신 콜백이 주기 스레드에서 호출된다는 사실은 실무에서 중요하다. 콜백 안에서 오래 걸리는 작업(파일 I/O, 네트워크 요청, 긴 계산)을 하면 그만큼 프로토콜 갱신과 송신이 밀린다. 무거운 작업은 콜백에서 플래그만 세우고 별도 스레드에서 처리하는 편이 안전하다.
:::

주기 간격은 `set_periodic_update_interval()`로 조정할 수 있고, `get_periodic_update_interval()`로 현재 값을 읽을 수 있다. 기본값은 4 ms다.

스레드를 아예 쓰지 않는 환경(베어메탈, Arduino 등)에서는 `start(false)`로 워커 스레드를 띄우지 않고, 애플리케이션이 직접 `CANHardwareInterface::update()`를 반복 호출해서 하드웨어 계층을 굴릴 수도 있다. 이 경우 <strong>최소 1 ms마다</strong> 호출해 CAN 메시지가 제때 하드웨어에서 회수되도록 해야 한다.

## CMake로 CAN 드라이버 고르기

라이브러리에는 SocketCAN, PEAK 같은 널리 쓰이는 CAN 인터페이스용 하드웨어 통합이 내장돼 있다.

CMake로 빌드하면 OS에 맞는 기본 CAN 드라이버 플러그인이 자동으로 선택된다. 하지만 `CAN_DRIVER` 변수를 넘겨서 원하는 드라이버를 명시적으로 고를 수도 있다.

| CMake 옵션 | 대상 |
| --- | --- |
| `-DCAN_DRIVER=SocketCAN` | Socket CAN (리눅스 기본값) |
| `-DCAN_DRIVER=WindowsPCANBasic` | 윈도우 PEAK PCAN 드라이버 (윈도우 기본값) |
| `-DCAN_DRIVER=MacCANPCAN` | MacCAN PEAK PCAN 드라이버 (macOS 기본값) |
| `-DCAN_DRIVER=TWAI` | ESP TWAI 드라이버 (ESP32에서 권장) |
| `-DCAN_DRIVER=MCP2515` | MCP2515 CAN 컨트롤러 |
| `-DCAN_DRIVER=WindowsInnoMakerUSB2CAN` | InnoMaker USB2CAN 어댑터 (윈도우) |
| `-DCAN_DRIVER=TouCAN` | Rusoku TouCAN (윈도우) |
| `-DCAN_DRIVER=SYS_TEC` | SYS TEC sysWORXX USB CAN 어댑터 (윈도우) |
| `-DCAN_DRIVER=NTCAN` | NTCAN 드라이버 (윈도우) |

여러 개를 동시에 넣고 싶으면 세미콜론으로 구분한 리스트를 준다.

```bash
cmake .. -DCAN_DRIVER="<driver1>;<driver2>"
```

예를 들어 리눅스에서 SocketCAN과 MCP2515를 함께 빌드하려면 이렇게 쓴다.

```bash
cmake -S . -B build -DCAN_DRIVER="SocketCAN;MCP2515"
```

목록에 없는 하드웨어가 대상이라면, 함수 몇 개만 구현해서 직접 통합할 수 있다. 이 방법은 아래 [직접 CAN 드라이버 작성하기](#직접-can-드라이버-작성하기)에서 다룬다.

CMake 설정으로 어떤 드라이버가 포함됐는지 코드에서 알고 싶으면 다음 헤더를 인클루드하면 된다.

```cpp
#include "isobus/hardware_integration/available_can_drivers.hpp"
```

이 헤더는 `ISOBUS_SOCKETCAN_AVAILABLE`, `ISOBUS_TWAI_AVAILABLE` 같은 매크로에 따라 실제로 빌드에 포함된 드라이버 헤더만 골라서 인클루드해 준다.

::: info 관련 스터디
CAN 물리 계층과 트랜시버, 종단 저항이 왜 필요한지는 [ISOBUS CH3. CAN 물리 계층](/study/isobus/03-can-physical)에서 다룬다. 플랫폼별 설치와 CMake 통합 방법 전반은 [CH5. 설치와 프로젝트 통합](/study/agisostack/05-installation)을 함께 보면 좋다.
:::

## 하드웨어 인터페이스 사용하기

`CANHardwareInterface`를 쓰는 절차는 간단하다. CAN 플러그인을 최소 하나 만들고, CAN 채널 수를 최소 1로 설정하고, 드라이버를 채널 인덱스에 할당한 다음, `start`를 호출한다.

```cpp
std::shared_ptr<isobus::CANHardwarePlugin> canDriver = std::make_shared<isobus::SocketCANInterface>("can0");

isobus::CANHardwareInterface::set_number_of_can_channels(1);
isobus::CANHardwareInterface::assign_can_channel_frame_handler(0, canDriver);

isobus::CANHardwareInterface::start();
```

모든 게 제대로 동작하는지 확인하려면 `start`의 반환값과 `canDriver->get_is_valid()`의 반환값을 함께 검사하는 게 좋다.

```cpp
if (!isobus::CANHardwareInterface::start() || !canDriver->get_is_valid())
{
    std::cout << "CAN 하드웨어 인터페이스를 시작하지 못했다. 드라이버가 유효하지 않을 수 있다." << std::endl;
    return -1;
}
```

이 패턴은 [공식 예제 모음](https://github.com/Open-Agriculture/AgIsoStack-plus-plus/tree/main/examples)에서 그대로 확인할 수 있다.

### 주요 정적 함수

`CANHardwareInterface`의 함수는 모두 정적(static) 함수다. 자주 쓰는 것들을 정리하면 이렇다.

| 함수 | 하는 일 |
| --- | --- |
| `set_number_of_can_channels(value, queueCapacity)` | 관리할 CAN 채널 수를 설정한다. 큐 용량 기본값은 40이다. 줄이면 남는 채널 객체가 삭제된다. |
| `get_number_of_can_channels()` | 현재 관리 중인 채널 수를 돌려준다. |
| `assign_can_channel_frame_handler(channelIndex, canDriver)` | 채널에 드라이버를 할당한다. |
| `unassign_can_channel_frame_handler(channelIndex)` | 채널에서 드라이버를 뗀다. |
| `get_assigned_can_channel_frame_handler(channelIndex)` | 채널에 할당된 드라이버를 돌려준다. 없으면 `nullptr`. |
| `start(start_thread = true)` | 스택과 드라이버 관리 스레드를 시작한다. |
| `stop()` | 모든 CAN 관리 스레드를 멈추고 Tx·Rx 큐에 남은 메시지를 버린다. |
| `is_running()` | 스레드가 돌고 있는지 확인한다. |
| `transmit_can_frame(frame)` | 프레임을 해당 채널의 Tx 큐에 넣는다. |
| `update()` | 스레드를 끈 경우 애플리케이션이 직접 주기적으로 호출한다. |
| `set_periodic_update_interval(value)` / `get_periodic_update_interval()` | 주기 갱신 간격(ms)을 설정·조회한다. |

::: warning 설정 순서를 지켜라
`set_number_of_can_channels()`와 `assign_can_channel_frame_handler()`는 <strong>이미 채널에 드라이버가 할당돼 있거나 인터페이스가 이미 시작된 상태면 실패한다</strong>. 채널 수 설정 → 드라이버 할당 → `start()` 순서를 지켜야 하고, 반환값을 확인하지 않으면 조용히 아무것도 안 된 상태로 넘어갈 수 있다.
:::

### 이벤트 디스패처

프레임이 오갈 때 훅을 걸고 싶으면 이벤트 디스패처를 쓸 수 있다. 로깅이나 버스 트레이스를 붙일 때 유용하다.

| 디스패처 | 발생 시점 |
| --- | --- |
| `get_can_frame_received_event_dispatcher()` | 하드웨어에서 CAN 프레임을 수신했을 때 |
| `get_can_frame_transmitted_event_dispatcher()` | 하드웨어로 CAN 프레임을 내보낼 때 |
| `get_periodic_update_event_dispatcher()` | 주기 갱신이 호출될 때 |

## 직접 CAN 드라이버 작성하기

라이브러리가 내 CAN 하드웨어를 지원하지 않아도, 함수 몇 개만 구현하면 쉽게 지원을 추가할 수 있다.

새 CAN 드라이버는 `CANHardwarePlugin`을 상속해서 그 안에 정의된 함수를 전부 구현하면 된다. 걱정할 필요 없다. <strong>다섯 개뿐</strong>이다.

상속할 [기반 클래스는 여기](https://github.com/Open-Agriculture/AgIsoStack-plus-plus/blob/main/hardware_integration/include/isobus/hardware_integration/can_hardware_plugin.hpp)에 있다.

```cpp
namespace isobus
{
	class CANHardwarePlugin
	{
	public:
		virtual ~CANHardwarePlugin() = default;

		/// 플러그인 이름 (예: 콤보박스에 표시할 용도)
		virtual std::string get_name() const = 0;

		/// 드라이버가 준비되어 정상 상태인지
		virtual bool get_is_valid() const = 0;

		/// 하드웨어 연결을 끊는다
		virtual void close() = 0;

		/// 드라이버를 초기화하고 하드웨어에 연결한다
		virtual void open() = 0;

		/// 버스에서 프레임 하나를 동기적으로 읽는다
		virtual bool read_frame(isobus::CANMessageFrame &canFrame) = 0;

		/// 버스로 프레임 하나를 (동기적으로) 쓴다
		virtual bool write_frame(const isobus::CANMessageFrame &canFrame) = 0;
	};
}
```

각 함수의 계약을 정리하면 이렇다.

| 함수 | 반환 | 계약 |
| --- | --- | --- |
| `get_name()` | `std::string` | 사용자에게 보여줄 수 있는 형식의 플러그인 이름 |
| `get_is_valid()` | `bool` | `open` 호출 전에는 `false`, `close` 호출 후에도 `false`, 하드웨어 분리 등으로 드라이버가 무효화돼도 `false`. 정상 연결 상태에서만 `true` |
| `open()` | `void` | 드라이버 초기화 및 하드웨어 연결 |
| `close()` | `void` | 하드웨어와의 연결 해제 |
| `read_frame(canFrame)` | `bool` | 프레임을 읽었으면 `true`, 아니면 `false`. 인자는 in/out |
| `write_frame(canFrame)` | `bool` | 프레임을 썼으면 `true`, 아니면 `false` |

::: details 직접 만든 드라이버 뼈대 예시
```cpp
#include "isobus/hardware_integration/can_hardware_plugin.hpp"
#include "isobus/isobus/can_message_frame.hpp"

class MyCustomCANPlugin : public isobus::CANHardwarePlugin
{
public:
	std::string get_name() const override
	{
		return "My Custom CAN Adapter";
	}

	bool get_is_valid() const override
	{
		return isConnected;
	}

	void open() override
	{
		// 하드웨어 핸들 열기, 비트레이트 설정 등
		isConnected = true;
	}

	void close() override
	{
		// 핸들 닫기
		isConnected = false;
	}

	bool read_frame(isobus::CANMessageFrame &canFrame) override
	{
		// 하드웨어에서 프레임 하나를 꺼내 canFrame에 채운다
		// identifier, isExtendedFrame, dataLength, data, channel 등을 채워야 한다
		return false;
	}

	bool write_frame(const isobus::CANMessageFrame &canFrame) override
	{
		// canFrame을 하드웨어 형식으로 변환해 전송한다
		return false;
	}

private:
	bool isConnected = false;
};
```

`read_frame`은 <strong>동기</strong> 함수다. 하드웨어 인터페이스의 수신 스레드가 이 함수를 계속 호출하므로, 내부에서 블로킹 읽기(타임아웃 있는)를 하는 것이 일반적이다. 논블로킹으로 구현해 프레임이 없을 때 즉시 `false`를 돌려주면 수신 스레드가 바쁘게 도는 스핀 루프가 되니 주의해야 한다.
:::

이렇게 만든 드라이버는 애플리케이션에 추가해서 내장 플러그인과 <strong>완전히 똑같은 방식</strong>으로 쓰면 된다.

```cpp
auto canDriver = std::make_shared<MyCustomCANPlugin>();

isobus::CANHardwareInterface::set_number_of_can_channels(1);
isobus::CANHardwareInterface::assign_can_channel_frame_handler(0, canDriver);
isobus::CANHardwareInterface::start();
```

::: tip 핵심 정리
- `CANHardwareInterface`는 모든 CAN 드라이버와 스택이 공유하는 공통 큐·스레드 계층이다. 호출 순서를 일관되고 안전하게 보장하는 게 존재 이유다.
- 수신 스레드가 Rx 큐를 채우고, 주기 스레드가 (1) Rx 큐 비우기 → (2) 프로토콜 갱신 → (3) Tx 큐 송신 3단계를 반복한다. 스택 코어가 사실상 단일 스레드라 뮤텍스가 필요 없다.
- CMake `-DCAN_DRIVER=<이름>`으로 내장 드라이버를 고른다. 세미콜론 리스트로 여러 개도 가능하다. OS별 기본값은 리눅스 SocketCAN, 윈도우 WindowsPCANBasic, macOS MacCANPCAN이다.
- 사용법은 플러그인 생성 → `set_number_of_can_channels` → `assign_can_channel_frame_handler` → `start` 네 단계. 반환값과 `get_is_valid()`를 함께 확인해라.
- 지원되지 않는 하드웨어는 `CANHardwarePlugin`을 상속해 `get_name` / `get_is_valid` / `open` / `close` / `read_frame` / `write_frame`만 구현하면 내장 플러그인과 동일하게 쓸 수 있다.
:::

## 원문 출처
이 챕터는 AgIsoStack++ 공식 문서 [HardwareInterface API](https://isobus-plus-plus.readthedocs.io/en/latest/api/hardware/index.html)의 내용을 한국어 학습 자료로 재구성한 것이다. 원문과 라이브러리는 MIT 라이선스로 배포된다.

## 다음 챕터
[CH18. ESP32와 PlatformIO](/study/agisostack/18-esp32-platformio)로 이어진다. 이번 챕터에서 배운 하드웨어 인터페이스를 실제 ESP32 보드 위에서 TWAI 드라이버로 돌려 본다.
