---
title: "CH19. API 구조 훑어보기"
description: "AgIsoStack++의 모듈 구성과 핵심 클래스 관계를 한 장의 지도로 정리하고, Doxygen 레퍼런스 활용법까지 짚는다."
date: 2026-07-20
tags: [AgIsoStack, ISOBUS, API, C++]
---

# CH19. API 구조 훑어보기

## 학습 목표
- AgIsoStack++가 어떤 모듈(CMake 타겟)로 나뉘어 있고, 각 모듈이 무엇을 책임지는지 설명할 수 있다.
- `CANNetworkManager`를 중심으로 Control Function·NAME·전송 프로토콜·애플리케이션 인터페이스가 어떻게 연결되는지 그릴 수 있다.
- 공식 문서가 다루는 "공개 API"의 범위와, Doxygen이 다루는 "내부 API"의 범위를 구분할 수 있다.
- 어떤 기능을 쓰고 싶을 때 어느 헤더·어느 챕터를 봐야 하는지 스스로 찾아갈 수 있다.

## 이 챕터의 위치

여기까지 오면서 Hello World부터 Virtual Terminal, Task Controller, 작업기 메시지, 하드웨어 이식까지 하나씩 손으로 만져 봤다. 이 챕터는 새 기능을 배우는 챕터가 아니다. 지금까지 조각조각 만난 클래스들을 <strong>한 장의 지도</strong> 위에 올려놓고, "이 라이브러리는 결국 이렇게 생겼다"를 확인하는 챕터다.

공식 문서의 API 섹션도 같은 태도로 쓰여 있다. 원문은 앞머리에서 이렇게 못 박는다.

::: info 공식 문서의 범위
문서화된 API는 라이브러리의 <strong>전체</strong>가 아니라 <strong>공개(public) 부분</strong>만 다룬다. 대부분의 사용자에게는 그 정도면 충분하다는 게 프로젝트의 판단이다. 내부 구현은 소스 코드의 주석에 문서화돼 있고, Doxygen으로 생성해서 볼 수 있다.
:::

즉 "공식 문서에 없다 = 없는 기능"이 아니다. 공식 문서에 없으면 Doxygen을, Doxygen에도 애매하면 헤더 파일 주석을 보면 된다. 이 순서를 알고 있는 것 자체가 이 챕터의 실용적인 수확이다.

## 공식 문서가 그리는 전형적인 ECU

원문 API 인덱스는 라이브러리의 대표적인 사용 시나리오를 이렇게 요약한다. 파종기나 살포기 같은 <strong>작업기를 제어하는 ISOBUS ECU</strong>를 만든다고 하자. 이 ECU는 다음을 조립한다.

1. CAN용 Hardware Interface를 구현해서 물리 버스에 붙인다.
2. Control Function을 여러 개 세운다. 명령을 <strong>받기</strong> 위한 내부 Control Function, 다른 모듈과 <strong>통신하기</strong> 위한 외부 Control Function.
3. Virtual Terminal 클라이언트를 구현해서 오브젝트 풀(IOP) 파일을 VT에 올린다. 그러면 "트랙터 캡 안의 화면"에 조작 UI와 상태 정보가 뜬다.
4. Task Controller 클라이언트를 구현해서 작업 지시(job)를 받는다.
5. 나머지는 전부 애플리케이션 로직이다. TC가 준 작업과 VT에서 온 명령을 근거로 작업기를 제어한다.

이 다섯 줄이 곧 CH7~CH18의 목차와 거의 일치한다. API 지도를 볼 때 이 시나리오를 배경에 깔아 두면 각 클래스가 어디에 끼워지는지 훨씬 빨리 감이 온다.

## 모듈 구성 — 세 개의 CMake 타겟

AgIsoStack++는 저장소 최상위에서 세 개의 디렉토리를 각각 별도 라이브러리 타겟으로 빌드한다. 세 타겟 모두 `isobus::` 네임스페이스 아래 별칭이 붙는다.

![라이브러리 모듈 구성](/images/study-agisostack/19-modules-light.png)
![라이브러리 모듈 구성](/images/study-agisostack/19-modules-dark.png)

| 타겟 | 디렉토리 | 책임 |
| --- | --- | --- |
| `isobus::Utility` | `utility/` | 스택 전체가 쓰는 저수준 도구. 시간 측정(`system_timing.hpp`), 이벤트 디스패처, IOP 파일 로더, 스레드 동기화 래퍼, 엔디언 처리 등 |
| `isobus::Isobus` | `isobus/` | ISO 11783 / J1939 프로토콜 본체. 네트워크 관리자, Control Function, NAME, 전송 프로토콜, VT/TC 클라이언트·서버, 작업기 메시지 인터페이스 |
| `isobus::HardwareIntegration` | `hardware_integration/` | 물리 CAN 하드웨어 연결. `CANHardwareInterface`와 각종 `CANHardwarePlugin` 구현체(SocketCAN, PEAK, TWAI, MCP2515 등) |

의존 방향은 한쪽이다. `Isobus`는 `Utility`에 의존하고, `HardwareIntegration`은 `Isobus`에 의존한다. 반대 방향 의존은 없다. 덕분에 프로토콜 코어는 하드웨어를 전혀 모른 채로 컴파일되고, 그게 이 라이브러리가 "플랫폼 독립"을 주장할 수 있는 구조적 근거다.

애플리케이션 코드는 보통 세 타겟을 다 링크한다. CH5에서 봤던 그 링크 줄이 바로 이 구조의 반영이다.

```cmake
target_link_libraries(my_app PRIVATE
    isobus::Isobus
    isobus::HardwareIntegration
    isobus::Utility
    Threads::Threads)
```

::: tip 헤더 경로 규칙
설치 후 include 경로는 디렉토리 이름을 그대로 따른다. `isobus/isobus/can_network_manager.hpp`, `isobus/hardware_integration/can_hardware_interface.hpp`, `isobus/utility/system_timing.hpp` 처럼 `isobus/<모듈>/<파일>` 형태다. 헤더 이름만 봐도 어느 타겟 소속인지 알 수 있다.
:::

## 핵심 클래스 관계도

Network API는 원문 표현으로 "규격에 맞게 ISOBUS 네트워크에서 통신하기 위한 라이브러리의 코어"다. 나머지 모든 기능이 이 위에 얹힌다.

![핵심 클래스 관계도](/images/study-agisostack/19-class-map-light.png)
![핵심 클래스 관계도](/images/study-agisostack/19-class-map-dark.png)

가운데의 `CANNetworkManager`가 전부의 허브다. 아래로는 하드웨어, 왼쪽으로는 신원(Control Function·NAME), 오른쪽으로는 데이터 전달(전송 프로토콜)과 애플리케이션 인터페이스가 붙는다.

### CANNetworkManager

싱글턴이다. 정적 멤버 `CANNetworkManager::CANNetwork` 하나로 스택 전체 기능에 접근한다.

| 대표 멤버 | 하는 일 |
| --- | --- |
| `update()` | 스택의 주기 처리. 수신 큐 소진 → 프로토콜 로직 → 송신 큐 배출 |
| `send_can_message(...)` | PGN·데이터·송신자·수신자를 받아 메시지를 보낸다. 길이에 따라 전송 프로토콜이 자동 선택된다 |
| `create_internal_control_function(...)` | 내 ECU용 Control Function 생성 (권장 생성 경로) |
| `create_partnered_control_function(...)` | 파트너 Control Function 생성 (권장 생성 경로) |
| `add_global_parameter_group_number_callback(...)` | 특정 PGN의 <strong>글로벌</strong>(브로드캐스트) 메시지 수신 콜백 등록 |
| `add_any_control_function_parameter_group_number_callback(...)` | 송신자를 가리지 않고 특정 PGN을 받는 콜백 등록 |
| `get_active_transport_protocol_sessions(portIndex)` | 해당 CAN 채널에서 진행 중인 전송 세션 목록 조회 |

`update()`를 직접 부를 일은 보통 없다. CH17에서 봤듯 `CANHardwareInterface`가 주기 스레드에서 대신 돌려 준다. 직접 스레드를 관리하는 이식 환경에서만 손으로 부른다.

### Control Function 계열

`ControlFunction`이 공통 기반 클래스고, 여기서 두 갈래가 갈라진다.

```cpp
namespace isobus
{
    class ControlFunction
    {
    public:
        enum class Type
        {
            Internal,  ///< 우리 스택의 일부. 주소 클레임을 할 수 있다
            External,  ///< 버스 위의 다른 장치
            Partnered  ///< 명시적으로 통신하려는 외부 Control Function
        };

        std::uint8_t get_address() const;
        bool get_address_valid() const;
        std::uint8_t get_can_port() const;
        NAME get_NAME() const;
        Type get_type() const;
        std::string get_type_string() const;
    };
}
```

- <strong>`InternalControlFunction`</strong> — 내 ECU 자신이다. 주소 클레임 상태 기계를 돌려 버스에서 주소를 확보한다.
- <strong>`PartneredControlFunction`</strong> — 내가 말을 걸고 싶은 상대다. `NAMEFilter` 조건으로 버스에 나타난 장치들 중 조건에 맞는 것을 골라 매칭한다.
- 단순한 `External`은 버스에 존재하지만 내가 특별히 지목하지 않은 장치다.

::: warning 생성자를 직접 부르지 마라
`ControlFunction`의 생성자는 공개돼 있지만, 헤더 주석이 명시하듯 대부분의 경우 `CANNetworkManager::create_internal_control_function()` / `create_partnered_control_function()`을 써야 한다. 직접 생성자를 쓰는 건 고급 요구가 있을 때뿐이다. 자세한 내용은 [CH3. Control Function과 NAME](/study/agisostack/03-control-function-name)에서 다뤘다.
:::

### NAME과 NAMEFilter

`NAME`은 ISO 11783이 정의한 64비트 장치 신원이다. 제조사 코드, Function, Function Instance, Device Class, Identity Number 등의 필드로 구성된다. `NAMEFilter`는 "이 필드가 이 값인 상대"라는 조건 하나를 표현하고, 여러 개를 묶어 파트너 매칭 조건을 만든다. 필드 구성과 매칭 규칙은 [CH3](/study/agisostack/03-control-function-name)에서 자세히 다뤘다.

### 전송 프로토콜

8바이트를 넘는 메시지는 전송 프로토콜이 나눠 보내고 다시 합친다. 사용자는 보통 `send_can_message()`만 부르면 되고 프로토콜 선택은 스택이 알아서 한다. 다만 진행 상황을 들여다보고 싶을 때 쓰는 공개 API가 있다.

```cpp
auto sessions = isobus::CANNetworkManager::CANNetwork
                    .get_active_transport_protocol_sessions(0);

for (const auto &session : sessions)
{
    session->get_parameter_group_number();      // 어떤 PGN인가
    session->get_direction();                    // Transmit / Receive
    session->get_source();                       // 보내는 Control Function
    session->get_destination();                  // 받는 Control Function
    session->get_message_length();               // 전체 길이
    session->get_total_bytes_transferred();      // 지금까지 전송된 바이트
    session->get_percentage_bytes_transferred(); // 진행률 (%)
}
```

`TransportProtocolSessionBase`가 공통 기반이고, 여기서 세 구현이 파생된다.

| 클래스 | 담당 |
| --- | --- |
| `TransportProtocolManager` | ISO 11783-3 TP. 9~1785바이트 |
| `ExtendedTransportProtocolManager` | ETP. 1786바이트 초과 대용량 |
| `FastPacketProtocol` | NMEA 2000 Fast Packet |

각 프로토콜의 선택 기준과 동작은 [CH4. 전송 계층 개념](/study/agisostack/04-transport-concepts)과 [CH10. 전송 계층 사용하기](/study/agisostack/10-transport-layer)에서 다뤘다.

## Virtual Terminal API 계열

VT는 여러 작업기를 <strong>하나의 단말</strong>로 조작하게 해 주는 규격이다. 원문이 주의를 주듯 VT는 Universal Terminal(UT)이라고도 불리며 두 용어는 같은 것을 가리킨다.

VT는 클라이언트와 서버 두 부분으로 나뉜다. 클라이언트는 <strong>무엇을 표시할지 정하는</strong> 애플리케이션이고, 서버는 <strong>그것을 실제로 그리는</strong> 애플리케이션이다. 둘은 거의 항상 서로 다른 장치에서 돈다. 클라이언트는 작업기에, 서버는 트랙터에 있다.

| 영역 | 대표 타입 | 문서 상태 |
| --- | --- | --- |
| 클라이언트 | `isobus::VirtualTerminalClient` | 공개 API 문서화 완료 |
| 서버 | `isobus::VirtualTerminalServer` 계열 | 원문 기준 "작성 중(Work in progress)" |
| 오브젝트 정의 | `isobus/isobus/isobus_virtual_terminal_objects.hpp` | 헤더 전체가 Doxygen으로 노출 |

보조 클래스로 `VirtualTerminalClientStateTracker`(클라이언트가 보낸 상태를 추적)와 `VirtualTerminalClientUpdateHelper`(값 변경을 편하게 반영)가 함께 제공된다.

### 보조 제어(AUX)

Auxiliary Control은 조이스틱·버튼·스위치 같은 <strong>물리 입력</strong>으로 작업기를 조작하게 해 주는 기능이다. 구조는 두 부분이다.

- <strong>Inputs</strong> — 조작자가 쓰는 개별 버튼·스위치·노브
- <strong>Functions</strong> — 작업기가 수행할 수 있는 동작(예: 올리기, 내리기)

둘을 잇는 것이 <strong>매핑</strong>이다. 어떤 입력이 어떤 기능을 제어할지는 조작자가 Virtual Terminal 화면에서 정하고, 그 매핑은 작업기 쪽에 저장된다. Inputs와 Functions는 둘 다 VT 클라이언트가 오브젝트 풀에 담은 보조 입력·보조 기능 오브젝트로 제공한다. 실제 클래스 이름은 `AuxiliaryInputType1`·`AuxiliaryInputType2`(입력), `AuxiliaryFunctionType1`·`AuxiliaryFunctionType2`(기능)다. Type1은 구형 계열이라 헤더 주석이 "파싱·검증은 되지만 버전 3 이상의 VT는 보조 제어 할당에 사용하지 않는다"고 못 박아 뒀다. 신규 설계라면 Type2를 쓴다.

::: warning AUX-N과 AUX-O는 호환되지 않는다
보조 제어 프로토콜에는 신형(AUX-N)과 구형(AUX-O)이 있고, 두 버전은 서로 <strong>호환되지 않는다</strong>. 어느 쪽을 지원할지는 처음부터 결정하고 들어가야 한다.
:::

자세한 사용법은 [CH13. Virtual Terminal 클라이언트](/study/agisostack/13-virtual-terminal)를 보면 된다.

## Task Controller API 계열

Task Controller는 데이터를 <strong>기록하고 계획하는</strong> 쪽이다. 조작자와 인터페이스해서 작업기가 수행할 작업을 스케줄링하며, 정밀 농업처럼 자동화된 정밀도가 중요한 작업의 핵심이다.

VT와 마찬가지로 클라이언트와 서버로 나뉜다. 서버가 스케줄링한 작업을 클라이언트가 실행한다.

::: info Data Logger(DL)
Task Controller로 등록됐지만 특히 데이터 로깅 기능을 수행하도록 정의된 Control Function을 <strong>Data Logger(DL)</strong>라고 부르는 경우가 많다. 별도 클래스가 있는 게 아니라 역할 이름이다.
:::

| 영역 | 대표 타입 | 관련 챕터 |
| --- | --- | --- |
| 클라이언트 | `isobus::TaskControllerClient` | [CH15](/study/agisostack/15-tc-client) |
| 서버 | `isobus::TaskControllerServer` (추상 클래스) | [CH14](/study/agisostack/14-tc-ddop) |
| 서버 옵션 | `isobus::TaskControllerOptions` | [CH14](/study/agisostack/14-tc-ddop) |
| DDOP | `isobus::DeviceDescriptorObjectPool`, `DeviceDescriptorObjectPoolHelpers` | [CH14](/study/agisostack/14-tc-ddop) |
| 클라이언트 오브젝트 | `isobus/isobus/isobus_task_controller_client_objects.hpp` | [CH14](/study/agisostack/14-tc-ddop) |

서버 API는 추상 클래스다. 몇 개의 가상 함수만 구현하면 CAN 통신 부분은 라이브러리가 대신 처리한다. 원문이 열거하는 서버 API의 특징은 이렇다.

- TC-GEO, TC-SC, TC-BAS에 필요한 CAN 메시징 지원
- DDOP 전송을 대신 관리하고, 클라이언트 연결 과정을 추상화
- ISO 11783-10의 TC 버전 3과 4를 모두 지원
- TC 상태 메시지 관리
- 클라이언트 연결 상태와 타임아웃 추적
- DDOP 클래스와의 통합으로 제품·작업기 정보 접근
- 클라이언트에게 필요한 응답을 전부 자동 전송

## Implement Messages API 계열

AgIsoStack++는 ISO 11783-7이 정의하는 <strong>트랙터-작업기 간 메시지</strong>를 간단하게 쓰도록 여러 인터페이스를 제공한다.

| 인터페이스 | 무엇을 하나 |
| --- | --- |
| `HeartbeatInterface` | 하트비트 메시지(PGN 61668 / 0xF0E4). 시퀀스 번호가 정상 범위로 증가하는 한 해당 CF가 동작 중이고 데이터가 정확함을 알린다. <strong>기본 활성화</strong>되어 있고 끌 수 있다 |
| `AgriculturalGuidanceInterface` | 가이던스 메시지 송수신. ISOBUS 기계·조향 밸브·작업기 조향 |
| `MaintainPowerInterface` | "전원 유지" 메시지. 점화 OFF 이후에도 TECU가 2초간 전원을 끊지 않도록 요청. 연결된 작업기의 동작 상태도 함께 전달하고, ECU 전원과 별개로 액추에이터 전원 유지도 선택할 수 있다 |
| `ShortcutButtonInterface` | ISOBUS Shortcut Button(ISB). 모든 작업기에게 안전 상태로 진입하라는 명령. 수신·송신·양쪽 다 선택 가능 |
| `SpeedMessagesInterface` | ISOBUS 속도 메시지 처리·송신 클래스 모음 |

::: warning 안전 관련 주의
가이던스 인터페이스로 기계를 조향하려 한다면 <strong>극도로 조심해야 한다</strong>. 이 라이브러리는 MIT 라이선스이며, 라이브러리를 받는 순간 그리고 이것으로 기계를 조향하려 시도하는 순간 그 라이선스 조건에 동의한 것이다.

ISB를 <strong>소비</strong>한다면 VT 오브젝트 풀에 관련 알람을 반드시 구현해야 하고, 홈 화면에 working set master가 ISB를 지원한다는 아이콘이나 표시를 넣어야 한다. AEF 적합성 요구사항이다.
:::

::: info 가이던스 메시지의 미래
이 메시지들은 AEF에 의해 언젠가 TIM(Tractor Implement Management)으로 대체되거나 최소한 잉여가 될 것으로 예상된다. 다만 시점은 알려져 있지 않고, TIM보다 단순하다는 이유로 많은 기계가 앞으로도 계속 이 인터페이스를 지원할 가능성이 높다. AgIsoStack++ 프로젝트는 AEF와 무관하며 AEF의 승인을 받은 적이 없다.
:::

자세한 사용법은 [CH16. 작업기 메시지와 ISB](/study/agisostack/16-implement-messages)에서 다뤘다.

## Hardware Interface API

`CANHardwareInterface`는 스택과 모든 CAN 드라이버를 돌리기 위한 <strong>공통 큐잉·스레드 계층</strong>이다. 통합을 단순화하고, 무엇보다 스택을 제대로 구동하는 데 필요한 함수 호출들의 순서를 일관되고 안전하게 보장하기 위해 만들어졌다.

핵심은 이 설계 결정이다. 송수신은 멀티스레드지만, <strong>수신 큐 소비와 프로토콜 갱신은 사실상 단일 스레드</strong>로 만든다. 그래서 스택 코어에 값비싼 뮤텍스가 필요 없다.

동작은 두 스레드로 요약된다.

1. <strong>수신 스레드</strong> — 하드웨어나 소켓에서 메시지를 제때 꺼내 수신 큐에 채운다.
2. <strong>주기 스레드</strong> — ① 수신 큐를 비우며 네트워크 관리자가 메시지를 처리한다(애플리케이션 콜백 다수가 이 스레드에서 호출된다) → ② 네트워크 관리자의 메인 갱신 루틴을 돌려 프로토콜 로직을 실행한다 → ③ 송신 큐에서 메시지를 꺼내 전송이 실패할 때까지 내보낸다. 몇 밀리초 뒤 같은 단계를 반복한다.

드라이버 쪽은 `CANHardwarePlugin`이라는 하드웨어 무관 추상 기반 클래스로 다룬다. 지원되지 않는 하드웨어라면 이 클래스를 상속해 <strong>5개의 함수</strong>만 구현하면 된다.

```cpp
auto canDriver = std::make_shared<isobus::SocketCANInterface>("can0");

isobus::CANHardwareInterface::set_number_of_can_channels(1);
isobus::CANHardwareInterface::assign_can_channel_frame_handler(0, canDriver);
isobus::CANHardwareInterface::start();
```

`start()`의 반환값과 `canDriver->get_is_valid()`를 함께 확인하면 초기화가 제대로 됐는지 알 수 있다.

CMake의 `CAN_DRIVER` 변수로 드라이버를 고르며, 세미콜론으로 여러 개를 동시에 넣을 수도 있다(`-DCAN_DRIVER="SocketCAN;VirtualCAN"` 형태). 어떤 드라이버가 실제로 포함됐는지는 `isobus/hardware_integration/available_can_drivers.hpp`를 include 하면 알 수 있다. 지원 드라이버 목록과 직접 드라이버를 쓰는 방법은 [CH17. HardwareInterface](/study/agisostack/17-hardware-interface)에서 다뤘다.

## 어떤 기능을 쓰고 싶을 때 어디를 보나

| 하고 싶은 것 | 볼 곳 | 챕터 |
| --- | --- | --- |
| 버스에 붙고 주소를 얻기 | `can_hardware_interface.hpp`, `can_internal_control_function.hpp` | [CH7](/study/agisostack/07-hello-world) |
| 특정 PGN 수신 처리 | `can_network_manager.hpp` 콜백 계열 | [CH8](/study/agisostack/08-receiving-messages) |
| 특정 상대에게만 보내기 | `can_partnered_control_function.hpp`, `can_NAME_filter.hpp` | [CH9](/study/agisostack/09-adding-destination) |
| 8바이트 초과 메시지 | `can_network_manager.hpp`의 `send_can_message` | [CH10](/study/agisostack/10-transport-layer) |
| PGN 요청 주고받기 | `can_parameter_group_number_request_protocol.hpp` | [CH11](/study/agisostack/11-pgn-requests) |
| 스택 로그 보기 | `can_stack_logger.hpp` | [CH12](/study/agisostack/12-debug-logging) |
| 화면 UI 올리기 | `isobus_virtual_terminal_client.hpp` | [CH13](/study/agisostack/13-virtual-terminal) |
| 작업 데이터 주고받기 | `isobus_task_controller_client.hpp`, `isobus_device_descriptor_object_pool.hpp` | [CH14](/study/agisostack/14-tc-ddop), [CH15](/study/agisostack/15-tc-client) |
| 속도·가이던스·ISB | `isobus_speed_distance_messages.hpp`, `isobus_guidance_interface.hpp`, `isobus_shortcut_button_interface.hpp` | [CH16](/study/agisostack/16-implement-messages) |
| 새 하드웨어 이식 | `can_hardware_plugin.hpp` | [CH17](/study/agisostack/17-hardware-interface), [CH18](/study/agisostack/18-esp32-platformio) |

## Doxygen 레퍼런스 활용하기

공식 문서가 다루지 않는 내부 API는 Doxygen이 담당한다. 이 프로젝트는 Doxygen으로 최신 내부 API 문서를 자동 생성한다.

### 미리 빌드된 문서 보기

가장 빠른 길이다. 아래 주소에서 최신 Doxygen 문서를 바로 볼 수 있다.

```text
https://delgrossoengineering.com/isobus-docs/index.html
```

### 로컬에서 직접 생성하기

버전을 정확히 맞춰 보고 싶거나 오프라인에서 봐야 한다면 직접 생성한다. 저장소 루트로 이동한 뒤 Doxygen을 설치하고 실행하면 된다.

```bash
cd AgIsoStack-plus-plus
```

::: details 플랫폼별 Doxygen 설치
<strong>Ubuntu</strong>

```bash
sudo apt install doxygen graphviz
```

<strong>RHEL</strong>

```bash
sudo subscription-manager repos --enable codeready-builder-for-rhel-9-$(arch)-rpms
sudo dnf install doxygen graphviz
```

<strong>Windows</strong>

`https://www.doxygen.nl/download.html` 에서 Doxygen을 설치한다.
:::

설치가 끝났으면 저장소에 포함된 `doxyfile`로 생성한다.

```bash
doxygen doxyfile
```

문서는 `docs/html` 폴더에 생긴다. `index.html`을 브라우저로 열면 브라우징을 시작할 수 있다.

::: tip graphviz를 같이 설치하는 이유
`graphviz`가 있어야 Doxygen이 클래스 상속도·협력 다이어그램을 그려 준다. 이 챕터에서 손으로 그린 클래스 관계도를 Doxygen이 자동으로 만들어 주는 셈이라, 코드를 파고들 때는 오히려 이쪽이 더 정확하다.
:::

## 정리

::: tip 핵심 정리
- 라이브러리는 `isobus::Utility` → `isobus::Isobus` → `isobus::HardwareIntegration` 순의 단방향 의존을 갖는 세 타겟으로 구성된다. 프로토콜 코어가 하드웨어를 모르는 게 플랫폼 독립성의 근거다.
- 모든 것의 허브는 싱글턴 `CANNetworkManager::CANNetwork`다. 송수신, 콜백 등록, Control Function 생성, 전송 세션 조회가 전부 여기를 거친다.
- 신원은 `ControlFunction` 3형제(Internal / External / Partnered)와 `NAME`·`NAMEFilter`가 담당하고, 데이터 전달은 `TransportProtocolSessionBase`에서 파생된 TP·ETP·Fast Packet이 담당한다.
- 애플리케이션 계층은 VT 클라이언트/서버, TC 클라이언트/서버, 그리고 ISO 11783-7 작업기 메시지 인터페이스들로 나뉜다. 전부 네트워크 코어 위에 얹힌 소비자다.
- 공식 문서는 공개 API만 다룬다. 그 너머는 `https://delgrossoengineering.com/isobus-docs/index.html` 의 미리 빌드된 Doxygen이나 `doxygen doxyfile`로 직접 생성한 문서를 보면 된다.
:::

## 다음 챕터

[FAQ·릴리스·라이선스](/study/agisostack/appendix-faq)
