---
title: "Virtual Terminal 클라이언트"
description: "AgIsoStack++로 VT 클라이언트를 구현하고 오브젝트 풀·이벤트를 다룬다"
date: 2026-07-20
tags: [AgIsoStack, ISOBUS, VirtualTerminal, C++]
---

# Virtual Terminal 클라이언트

## 학습 목표

- `VirtualTerminalClient`를 파트너 CF·내부 CF와 함께 생성하고 초기화하는 절차를 익힌다
- 오브젝트 풀을 IOP 파일에서 읽어 `set_object_pool`로 등록하고, 버전 해시로 VT 캐시를 활용하는 법을 안다
- 버튼·소프트키 이벤트를 이벤트 디스패처로 받아 처리하고, `VirtualTerminalClientUpdateHelper`로 화면을 갱신할 수 있다
- VT 클라이언트가 제공하는 나머지 이벤트와 명령의 전체 목록을 파악한다
- IOP 파일 복사까지 포함한 CMake를 작성해 예제를 빌드·실행할 수 있다
- AUX-N(Auxiliary Control) API와 VT 서버 측 API의 구조를 개괄한다

::: info 관련 스터디
프로토콜 차원의 배경 지식은 이론 스터디에 정리돼 있다. 이번 챕터는 그 이론을 AgIsoStack++ 코드로 옮기는 작업이다.

- [ISOBUS CH15. VT 기초](/study/isobus/15-vt-basics)
- [ISOBUS CH16. VT 오브젝트 풀](/study/isobus/16-vt-object-pool)
- [ISOBUS CH17. VT 명령어](/study/isobus/17-vt-commands)

스택 사용법은 앞 챕터를 전제로 한다.

- [CH7. ISOBUS Hello World](/study/agisostack/07-hello-world)
- [CH8. 메시지 수신](/study/agisostack/08-receiving-messages)
- [CH3. Control Function과 NAME](/study/agisostack/03-control-function-name)
:::

## VT란 무엇인가 — 짧은 복습

Virtual Terminal(VT)은 운전자가 트랙터 캡 안의 단일 단말기로 여러 작업기를 조작할 수 있게 해주는 장치다. VT는 클라이언트와 서버 두 부분으로 나뉜다.

- <strong>클라이언트</strong>: 무엇을 표시할지를 결정하는 애플리케이션. 보통 작업기(implement)에서 돈다.
- <strong>서버</strong>: 클라이언트가 보낸 내용을 실제로 화면에 그리는 애플리케이션. 보통 트랙터에서 돈다.

둘은 별개의 애플리케이션이므로 거의 항상 서로 다른 장치에서 실행된다.

::: info 용어
VT는 문헌에 따라 Universal Terminal(UT)로도 불린다. 두 용어는 서로 바꿔 써도 된다.
:::

이번 챕터가 다루는 것은 <strong>클라이언트</strong> 쪽이다. 작업기 ECU가 자기 UI를 그리는 방법을 VT에게 설명하고, 화면 위에서 벌어지는 일을 되돌려 받는 과정 전체를 코드로 만든다.

## Virtual Terminal 클라이언트 만들기

VT와 통신하는 첫 단계는 `VirtualTerminalClient` 객체를 만드는 것이다. 이 객체가 모든 VT 통신의 창구가 된다. 인스턴스를 만들려면 두 가지가 필요하다.

- `PartneredControlFunction` — 상대할 VT 서버
- `InternalControlFunction` — 내가 통신할 때 쓸 주소

이 둘이 있어야 클라이언트가 연결 유지에 필요한 메시지를 대신 보내주고, 원시 CAN 메시지를 직접 다루는 것보다 훨씬 간단한 API를 제공할 수 있다.

깨끗한 폴더에서 시작한다.

```bash
mkdir vt_example
cd vt_example
git clone https://github.com/Open-Agriculture/AgIsoStack-plus-plus.git
```

그 폴더 안에 `main.cpp`를 만들고, 우선 필요한 컨트롤 펑션까지만 준비한다.

```cpp
#include "isobus/hardware_integration/available_can_drivers.hpp"
#include "isobus/hardware_integration/can_hardware_interface.hpp"
#include "isobus/isobus/can_network_manager.hpp"
#include "isobus/isobus/can_partnered_control_function.hpp"

#include <atomic>
#include <csignal>
#include <iostream>

//! It is discouraged to use global variables, but it is done here for simplicity.
static std::atomic_bool running = { true };

void signal_handler(int)
{
	running = false;
}

int main()
{
	std::signal(SIGINT, signal_handler);

	// Automatically load the desired CAN driver based on the available drivers
	std::shared_ptr<isobus::CANHardwarePlugin> canDriver = nullptr;
#if defined(ISOBUS_SOCKETCAN_AVAILABLE)
	canDriver = std::make_shared<isobus::SocketCANInterface>("can0");
#elif defined(ISOBUS_WINDOWSPCANBASIC_AVAILABLE)
	canDriver = std::make_shared<isobus::PCANBasicWindowsPlugin>(PCAN_USBBUS1);
#elif defined(ISOBUS_WINDOWSINNOMAKERUSB2CAN_AVAILABLE)
	canDriver = std::make_shared<isobus::InnoMakerUSB2CANWindowsPlugin>(0); // CAN0
#elif defined(ISOBUS_MACCANPCAN_AVAILABLE)
	canDriver = std::make_shared<isobus::MacCANPCANPlugin>(PCAN_USBBUS1);
#elif defined(ISOBUS_SYS_TEC_AVAILABLE)
	canDriver = std::make_shared<isobus::SysTecWindowsPlugin>();
#endif
	if (nullptr == canDriver)
	{
		std::cout << "Unable to find a CAN driver. Please make sure you have one of the above drivers installed with the library." << std::endl;
		std::cout << "If you want to use a different driver, please add it to the list above." << std::endl;
		return -1;
	}
	isobus::CANHardwareInterface::set_number_of_can_channels(1);
	isobus::CANHardwareInterface::assign_can_channel_frame_handler(0, canDriver);

	if ((!isobus::CANHardwareInterface::start()) || (!canDriver->get_is_valid()))
	{
		std::cout << "Failed to start hardware interface. The CAN driver might be invalid." << std::endl;
		return -2;
	}

	std::this_thread::sleep_for(std::chrono::milliseconds(250));

	isobus::NAME TestDeviceNAME(0);

	//! Consider customizing some of these fields, like the function code, to be representative of your device
	TestDeviceNAME.set_arbitrary_address_capable(true);
	TestDeviceNAME.set_industry_group(1);
	TestDeviceNAME.set_device_class(0);
	TestDeviceNAME.set_function_code(static_cast<std::uint8_t>(isobus::NAME::Function::SteeringControl));
	TestDeviceNAME.set_identity_number(2);
	TestDeviceNAME.set_ecu_instance(0);
	TestDeviceNAME.set_function_instance(0);
	TestDeviceNAME.set_device_class_instance(0);
	TestDeviceNAME.set_manufacturer_code(1407);

	const isobus::NAMEFilter filterVirtualTerminal(isobus::NAME::NAMEParameters::FunctionCode, static_cast<std::uint8_t>(isobus::NAME::Function::VirtualTerminal));
	const std::vector<isobus::NAMEFilter> vtNameFilters = { filterVirtualTerminal };
	auto TestInternalECU = isobus::CANNetworkManager::CANNetwork.create_internal_control_function(TestDeviceNAME, 0);
	auto TestPartnerVT = isobus::CANNetworkManager::CANNetwork.create_partnered_control_function(0, vtNameFilters);

	while (running)
	{
		// CAN stack runs in other threads. Do nothing forever.
		std::this_thread::sleep_for(std::chrono::milliseconds(1000));
	}

	isobus::CANHardwareInterface::stop();
	return 0;
}
```

앞선 챕터와 거의 같은 보일러플레이트지만, 두 가지가 특히 중요하다.

- 컨트롤 펑션을 `std::shared_ptr`로 만든다. VT 클라이언트 클래스가 shared pointer를 요구하므로 처음부터 그 형태로 시작하는 게 낫다.
- 파트너를 "function code가 VT임을 나타내는 버스 상의 모든 장치"로 정의했다. 다른 function code가 궁금하면 `isobus::NAME::NAMEParameters::FunctionCode` API 문서를 보면 된다.

이제 VT 클라이언트를 만든다. 여기서 VT 갱신을 쉽게 해주는 헬퍼 클래스도 함께 도입한다.

```cpp
#include "isobus/isobus/isobus_virtual_terminal_client.hpp"
#include "isobus/isobus/isobus_virtual_terminal_client_update_helper.hpp"

//! It is discouraged to use global variables, but we have done it here for simplicity.
static std::shared_ptr<isobus::VirtualTerminalClient> TestVirtualTerminalClient = nullptr;
static std::shared_ptr<isobus::VirtualTerminalClientUpdateHelper> virtualTerminalUpdateHelper = nullptr;

int main()
{
	...

	TestVirtualTerminalClient = std::make_shared<isobus::VirtualTerminalClient>(TestPartnerVT, TestInternalECU);
	virtualTerminalUpdateHelper = std::make_shared<isobus::VirtualTerminalClientUpdateHelper>(virtualTerminalClient);

	...
}
```

생성자 시그니처는 다음과 같다. 파트너(VT 서버)가 먼저, 내부 CF가 나중이다.

```cpp
VirtualTerminalClient(std::shared_ptr<PartneredControlFunction> partner,
                      std::shared_ptr<InternalControlFunction> clientSource);
```

클라이언트가 만들어졌으니 이제 설정을 해야 한다. 구체적으로는 관리할 오브젝트 풀을 최소 하나는 줘야 한다.

### 클라이언트 상태 머신

`initialize`를 호출하면 클라이언트 내부 상태 머신이 돌기 시작한다. 이 상태 머신은 헤더의 `StateMachineState`로 공개돼 있어서, 지금 연결이 어디까지 진행됐는지 추적할 수 있다.

![VT 클라이언트 수명주기](/images/study-agisostack/13-vt-client-lifecycle-light.png)
![VT 클라이언트 수명주기](/images/study-agisostack/13-vt-client-lifecycle-dark.png)

| 상태 | 의미 |
| --- | --- |
| `Disconnected` | 아직 연결을 시도하지 않은 상태 |
| `WaitForPartnerVTStatusMessage` | 초기화 완료, VT 서버가 버스에 나타나기를 대기 |
| `SendWorkingSetMasterMessage` | 워킹셋 마스터 메시지 전송 중 |
| `ReadyForObjectPool` | 연결을 이어가려면 오브젝트 풀이 필요한 상태 |
| `SendGetMemory` / `WaitForGetMemoryResponse` | VT에 충분한 메모리가 있는지 조회 |
| `SendGetNumberSoftkeys` / `WaitForGetNumberSoftKeysResponse` | 소프트키 개수 조회 |
| `SendGetTextFontData` / `WaitForGetTextFontDataResponse` | 지원 폰트 조회 |
| `SendGetHardware` / `WaitForGetHardwareResponse` | 하드웨어(해상도·그래픽 모드) 조회 |
| `SendGetVersions` / `WaitForGetVersionsResponse` | 버전 라벨을 지정했다면 VT가 이미 그 버전을 갖고 있는지 확인 |
| `SendStoreVersion` / `WaitForStoreVersionResponse` | 버전 저장 명령 |
| `SendLoadVersion` / `WaitForLoadVersionResponse` | 버전 로드 명령 |
| `UploadObjectPool` | 오브젝트 풀 업로드 중 |
| `SendEndOfObjectPool` / `WaitForEndOfObjectPoolResponse` | 업로드 종료 통보와 응답 대기 |
| `Connected` | 연결 완료. 애플리케이션 계층이 주도권을 갖는다 |
| `Failed` | 오류로 연결하지 못한 상태 |

수명주기를 제어하는 함수들도 함께 알아두면 좋다.

```cpp
void initialize(bool spawnThread);   // 상태 머신 시작. true면 내부 스레드를 띄운다
bool get_is_initialized() const;     // 초기화 여부 (연결 여부와는 다르다)
bool get_is_connected() const;       // VT 서버와 실제로 연결됐는지
void terminate();                    // 종료하고 워커 스레드를 조인
void restart_communication();        // 통신을 정상적으로 멈췄다가 다시 시작
void update();                       // spawnThread=false일 때 직접 주기 호출해야 하는 함수
```

`initialize(false)`로 만들면 스레드를 띄우지 않으므로, 애플리케이션이 자기 루프에서 `update()`를 주기적으로 호출해줘야 한다. 임베디드처럼 스레드를 쓰기 곤란한 환경에서 유용하다.

## 오브젝트 풀

ISOBUS 오브젝트 풀은 여러 시각 컴포넌트(오브젝트)가 담긴 컨테이너라고 생각하면 된다. 각 오브젝트의 역할은 ISO 11783-6 표준이 정의한다. 이들을 조합한 결과가 VT 화면에 보이는 사용자 인터페이스다.

기술적으로 말하면, 화면이 없는(headless) 장치가 자기 UI를 어떻게 그려야 하는지를 VT에게 설명하는 방식이다. 기계와 플랫폼이 달라도 일관되게 이식된다는 점이 핵심이다.

데이터 자체는 결국 긴 오브젝트 목록이다. 다음 같은 것들이 들어간다.

- 폰트 속성(font attributes)
- 비트맵
- 문자열
- 숫자
- 포인터
- 선
- 사각형
- 폴리곤
- 타원
- 바 그래프나 그래픽 컨텍스트 같은 좀 더 복잡한 오브젝트 몇 종

ECU는 이 오브젝트 덩어리를 반계층적(semi-hierarchical) 관계와 함께 VT에 업로드한다. VT는 형식이 유효한지 검사한 뒤 화면에 그리기 시작한다. 그 다음부터 ECU는 CAN 메시지로 화면에 표시된 내용을 갱신하고, 반대로 VT는 버튼이 눌리는 등의 사건을 CAN 메시지로 ECU에 알린다. 이 왕복 통신이 ISOBUS 작업기 애플리케이션의 토대이며, 스택은 이 통신을 최대한 쉽게 만드는 걸 목표로 한다.

![오브젝트 풀 구조](/images/study-agisostack/13-object-pool-structure-light.png)
![오브젝트 풀 구조](/images/study-agisostack/13-object-pool-structure-dark.png)

### 오브젝트 종류

스택은 `isobus_virtual_terminal_objects.hpp`의 `VirtualTerminalObjectType` enum으로 오브젝트 타입을 정의한다. 주요 값은 다음과 같다.

| 값 | 타입 | 설명 |
| --- | --- | --- |
| 0 | `WorkingSet` | 작업기 ECU(또는 ECU 그룹)를 기술하는 최상위 오브젝트 |
| 1 | `DataMask` | 워킹셋이 활성화하면 VT 화면의 현재 오브젝트 집합이 되는 최상위 오브젝트 |
| 2 | `AlarmMask` | 알람 화면을 기술하는 최상위 오브젝트 |
| 3 | `Container` | 오브젝트를 묶는 용도 |
| 34 | `WindowMask` | VT가 활성화하는 최상위 오브젝트 |
| 4 | `SoftKeyMask` | Key 오브젝트를 담는 최상위 오브젝트 |
| 5 | `Key` | 소프트키를 기술 |
| 6 | `Button` | 버튼 컨트롤을 기술 |
| 35 | `KeyGroup` | Key 오브젝트를 담는 최상위 오브젝트 |
| 7 | `InputBoolean` | 참/거짓 입력 |
| 8 | `InputString` | 문자열 입력 |
| 9 | `InputNumber` | 정수·실수 입력 |
| 10 | `InputList` | 미리 정의된 목록에서 항목 선택 |
| 11 | `OutputString` | 문자열 출력 |
| 12 | `OutputNumber` | 정수·실수 출력 |
| 37 | `OutputList` | 목록 항목 출력 |
| 13 | `OutputLine` | 선 출력 |
| 14 | `OutputRectangle` | 사각형·정사각형 출력 |
| 15 | `OutputEllipse` | 타원·원 출력 |
| 16 | `OutputPolygon` | 폴리곤 출력 |
| 17 | `OutputMeter` | 미터(게이지) 출력 |
| 18 | `OutputLinearBarGraph` | 선형 바 그래프 출력 |
| 19 | `OutputArchedBarGraph` | 호형 바 그래프 출력 |
| 36 | `GraphicsContext` | 그래픽 컨텍스트 출력 |
| 44 | `Animation` | 간단한 애니메이션 표시 |
| 20 | `PictureGraphic` | 픽처 그래픽(비트맵) 출력 |
| 46 | `GraphicData` | 그래픽 이미지의 데이터 정의 |
| 48 | `ScaledGraphic` | 그래픽 오브젝트의 스케일된 표현 표시 |
| 21 | `NumberVariable` | 32비트 부호 없는 정수 값 저장 |
| 22 | `StringVariable` | 고정 길이 문자열 값 저장 |
| 23 | `FontAttributes` | 폰트 관련 속성 묶음. 다른 오브젝트가 참조만 가능 |
| 24 | `LineAttributes` | 선 관련 속성 묶음. 참조만 가능 |
| 25 | `FillAttributes` | 채우기 관련 속성 묶음. 참조만 가능 |
| 26 | `InputAttributes` | 유효 문자 목록. 입력 필드 오브젝트만 참조 가능 |
| 38 | `ExtendedInputAttributes` | 유효 WideChar 목록. 입력 필드 오브젝트만 참조 가능 |
| 39 | `ColourMap` | 컬러 테이블 오브젝트 |
| 40 | `ObjectLabelRefrenceList` | 오브젝트 라벨 지정 |
| 27 | `ObjectPointer` | 다른 오브젝트를 참조 |
| 41 | `ExternalObjectDefinition` | 다른 워킹셋에서 참조 가능한 오브젝트 목록 |
| 42 | `ExternalReferenceNAME` | 참조 가능한 워킹셋의 WS 마스터를 식별 |
| 43 | `ExternalObjectPointer` | 다른 워킹셋의 오브젝트를 참조 |
| 28 | `Macro` | 이벤트에 반응해 실행할 명령 목록을 담는 특수 오브젝트 |
| 29 | `AuxiliaryFunctionType1` | AUX 함수의 지정자와 함수 타입 정의 (구버전) |
| 30 | `AuxiliaryInputType1` | AUX 입력의 지정자·키 번호·함수 타입 정의 (구버전) |
| 31 | `AuxiliaryFunctionType2` | AUX 함수의 지정자와 함수 타입 정의 (AUX-N) |
| 32 | `AuxiliaryInputType2` | AUX 입력의 지정자·키 번호·함수 타입 정의 (AUX-N) |
| 33 | `AuxiliaryControlDesignatorType2` | Auxiliary Input/Function Type 2 오브젝트 참조용 |
| 240~251 | `ManufacturerDefined1`~`12` | 제조사 정의 오브젝트. 다른 벤더의 VT로 보내면 안 된다 |

### IOP 파일 읽어 등록하기

스택의 `utility` 폴더에는 표준 ISOBUS `.iop` 파일을 읽는 헬퍼 함수가 들어 있다. `.iop`은 오브젝트 풀이라는 바이너리 덩어리를 저장하는 업계 표준 방식이다.

오브젝트 풀 디자이너 도구가 있으면 직접 만들 수 있지만, 학습용으로는 예제 폴더에 들어 있는 `VT3TestPool.iop`을 쓰면 된다. 이 파일을 `main.cpp`와 같은 디렉터리에 놓는다.

같은 폴더에 `objectPoolObjects.h`도 함께 둔다. 이 헤더는 IOP 안에 어떤 오브젝트가 들어 있는지와 그 오브젝트 ID를 알려준다. 보통 오브젝트 풀 디자이너 프로그램이 이런 파일을 자동 생성해준다. 덕분에 오브젝트 5001을 숫자로 참조하는 대신 `acknowledgeAlarm_SoftKey` 같은 읽기 좋은 이름으로 참조할 수 있다.

```cpp
// This is a file that will be auto-generated by your object pool designer application.
// These are the object IDs for the objects in the object pool
#define UNDEFINED 65535 //0xFFFF
#define example_WorkingSet 0 //0x0000
#define mainRunscreen_DataMask 1000 //0x03E8
#define example_AlarmMask 2000 //0x07D0
#define exampleNumberInc_Container 3000 //0x0BB8
#define mainRunscreen_SoftKeyMask 4000 //0x0FA0
#define alarm_SKeyMask 4001 //0x0FA1
#define alarm_SoftKey 5000 //0x1388
#define acknowledgeAlarm_SoftKey 5001 //0x1389
#define Plus_Button 6000 //0x1770
#define Minus_Button 6001 //0x1771
#define exampleOutput_OutNum 12000 //0x2EE0
#define ButtonExampleNumber_VarNum 21000 //0x5208
```

이제 IOP 파일을 읽어 VT 클라이언트에 유일한 오브젝트 풀로 넘기는 코드를 추가한다.

```cpp
#include "isobus/utility/iop_file_interface.hpp"


int main()
{
	...

	std::vector<std::uint8_t> testPool = isobus::IOPFileInterface::read_iop_file("VT3TestPool.iop");
	if (testPool.empty())
	{
		std::cout << "Failed to load object pool from VT3TestPool.iop" << std::endl;
		return -3;
	}
	std::cout << "Loaded object pool from VT3TestPool.iop" << std::endl;

	// Generate a unique version string for this object pool (this is optional, and is entirely application specific behavior)
	std::string objectPoolHash = isobus::IOPFileInterface::hash_object_pool_to_version(testPool);

	...

	TestVirtualTerminalClient->set_object_pool(0, testPool.data(), testPool.size());

	...
}
```

::: warning 포인터 수명에 주의
`testPool`이 `static`이 아니라는 점을 눈여겨봐라. `set_object_pool`에 넘긴 포인터는 오브젝트 풀 업로드가 끝날 때까지 반드시 유효해야 한다(즉, 삭제되거나 스코프를 벗어나면 안 된다). 그러지 않으면 애플리케이션이 크래시할 수 있다.
:::

`set_object_pool`은 두 가지 오버로드가 있다.

```cpp
// 버퍼 + 크기
void set_object_pool(std::uint8_t poolIndex,
                     const std::uint8_t *pool,
                     std::uint32_t size,
                     const std::string &version = "");

// 벡터 포인터
void set_object_pool(std::uint8_t poolIndex,
                     const std::vector<std::uint8_t> *pool,
                     const std::string &version = "");
```

둘 다 데이터를 전부 메모리에 갖고 있는 작은 풀에 적합하다. `version`은 선택 인자인데, 이 값을 주면 스택이 알아서 VT에 풀을 저장하거나 VT에서 불러온다.

::: warning 버전은 풀마다 다를 수 없다
같은 VT 서버에 올리는 모든 풀의 version 문자열은 동일해야 한다.
:::

### 버전 해시로 재업로드 피하기

예제에서는 오브젝트 풀의 해시를 만들었다.

```cpp
std::string objectPoolHash = isobus::IOPFileInterface::hash_object_pool_to_version(testPool);
```

이 해시는 오브젝트 풀을 대표하는 유일한 문자열이다. 지난번 업로드 이후 풀이 바뀌었는지를 VT에게 알려주는 역할을 한다. 바뀌었다면 VT는 ECU에게 새 오브젝트 풀을 요청한다. 바뀌지 않았다면 VT는 예전 풀과 같다고 판단해 다시 요청하지 않고 자기 캐시에서 로드한다. 수백 KB짜리 풀을 CAN으로 매번 올리는 시간을 아낄 수 있다.

### 메모리가 부족할 때 — 청크 콜백

풀이 너무 커서 메모리에 다 담기 어렵거나, 자원이 빠듯한 임베디드 플랫폼이라면 `register_object_pool_data_chunk_callback`을 쓴다. 업로드가 진행되면서 스택이 작은 조각 단위로 데이터를 요청한다. 외부 장치에서 세그먼트 단위로 읽어오거나 그냥 RAM을 아끼는 데 쓸 수 있다. IOP 파일에서 조금씩 읽어 올리기에도 가장 좋은 방식이다.

```cpp
void register_object_pool_data_chunk_callback(std::uint8_t poolIndex,
                                              std::uint32_t poolTotalSize,
                                              DataChunkCallback value,
                                              std::string version = "");
```

### 해상도가 다른 VT에 맞추기 — 자동 스케일링

스택이 오브젝트 풀을 실제 로드 대상 VT의 치수에 맞춰 자동으로 스케일하게 만들 수도 있다. 특정 데이터 마스크 크기를 전제로 풀을 디자인했는데 해상도가 다르거나 지원 폰트가 다른 VT에도 올려야 할 때 유용하다. `set_object_pool_scaling`으로 풀을 만들 때 사용한 치수를 알려주기만 하면 된다.

```cpp
void set_object_pool_scaling(std::uint8_t poolIndex,
                             std::uint32_t originalDataMaskDimensions_px,
                             std::uint32_t originalSoftKyeDesignatorHeight_px);
```

::: tip AgIsoTerminalDesigner
오브젝트 풀을 직접 디자인하고 싶다면 같은 Open-Agriculture 진영의 오픈소스 도구 <strong>AgIsoTerminalDesigner</strong>가 있다. 여기서 만든 결과물을 `.iop`으로 내보내면 이 챕터의 코드가 그대로 동작한다. 상용 VT 디자이너 도구들도 마찬가지로 `.iop`과 오브젝트 ID 헤더를 뽑아준다.
:::

::: info CMake 한 줄이 늘어난다
이제 IOP 파일을 읽기 위해 `isobus/utility` 폴더의 함수를 쓰므로, CMakeLists.txt에서 스택의 utility 라이브러리에도 링크해야 한다. `target_link_libraries` 구문에 `isobus::Utility`를 추가하면 된다. 또 IOP 파일을 빌드 산출물 위치로 옮기는 CMake도 필요하다. 컴파일된 프로그램이 접근할 수 있는 위치에 IOP가 있어야 하기 때문이다. 전체 CMake는 챕터 뒷부분에서 다룬다.
:::

여기까지 하면 풀을 VT에 업로드하는 데 필요한 코드는 다 갖췄다. 하지만 아직 실제 애플리케이션 로직은 없다. 통신 설정만 끝난 상태다.

## VT 애플리케이션 계층

이제 VT 클라이언트를 애플리케이션에서 어떻게 쓰는지 본다.

### 버튼·소프트키 이벤트

VT로부터 피드백을 받는 주된 통로가 버튼 이벤트다. 버튼이 눌리거나, 놓이거나, 눌린 채 유지되거나, 중단(눌렸지만 놓이지 않음)될 때마다 VT가 메시지를 보낸다. 프로그램에서 이 이벤트 처리를 준비해두면 그에 맞는 동작을 할 수 있다.

`VirtualTerminalClient::VTKeyEvent`를 받는 콜백을 만든다. 이 구조체가 발생한 키 이벤트 정보를 담고 있다.

```cpp
struct VTKeyEvent
{
	VirtualTerminalClient *parentPointer; ///< A pointer to the parent VT client
	std::uint16_t objectID; ///< The object ID
	std::uint16_t parentObjectID; ///< The parent object ID
	std::uint8_t keyNumber; ///< The key number
	KeyActivationCode keyEvent; ///< The key event
};
```

`keyEvent`에 들어가는 `KeyActivationCode`는 네 가지다.

| 값 | 이름 | 의미 |
| --- | --- | --- |
| 0 | `ButtonUnlatchedOrReleased` | 버튼이 놓였다 |
| 1 | `ButtonPressedOrLatched` | 버튼이 눌렸다 |
| 2 | `ButtonStillHeld` | 버튼이 눌린 채 유지 중 (주기적으로 전송) |
| 3 | `ButtonPressAborted` | 누른 상태에서 버튼 밖으로 이동해 놓지 않고 중단됨 |

버튼 콜백은 이렇게 쓴다.

```cpp
// This callback will provide us with event driven notifications of button presses from the stack
void handle_button_event(const isobus::VirtualTerminalClient::VTKeyEvent &event)
{
	switch (event.keyEvent)
	{
		case isobus::VirtualTerminalClient::KeyActivationCode::ButtonUnlatchedOrReleased:
		case isobus::VirtualTerminalClient::KeyActivationCode::ButtonStillHeld:
		{
			switch (event.objectID)
			{
				case Plus_Button:
				{
					virtualTerminalUpdateHelper->increase_numeric_value(ButtonExampleNumber_VarNum);
				}
				break;

				case Minus_Button:
				{
					virtualTerminalUpdateHelper->decrease_numeric_value(ButtonExampleNumber_VarNum);
				}
				break;

				default:
					break;
			}
		}
		break;

		default:
			break;
	}
}
```

이 함수는 먼저 VT가 보고한 키 이벤트를 보고 무엇을 할지 정한다. 예제에서는 `ButtonUnlatchedOrReleased`와 `ButtonStillHeld` 두 경우에 동작한다. 즉 버튼이 놓였을 때와 눌린 채 유지될 때 각각 무언가를 한다. `ButtonStillHeld`는 버튼을 누르고 있는 동안 일정 간격으로 계속 호출되므로, 버튼을 누르고 있으면 값이 계속 증가하거나 목록이 계속 스크롤되는 동작을 만들 때 유용하다. 그다음 `objectID`를 보고 무엇을 할지 정한다. 예제에서는 화면의 카운터를 올리고 내린다.

소프트키도 흔히 쓰는 상호작용 수단이니 리스너를 하나 더 붙인다.

```cpp
// This callback will provide us with event driven notifications of softkey presses from the stack
void handle_softkey_event(const isobus::VirtualTerminalClient::VTKeyEvent &event)
{
	if (event.keyNumber == 0)
	{
		// We have the alarm ACK code, so if we have an active alarm, acknowledge it by going back to the main runscreen
		virtualTerminalUpdateHelper->set_active_data_or_alarm_mask(example_WorkingSet, mainRunscreen_DataMask);
	}

	switch (event.keyEvent)
	{
		case isobus::VirtualTerminalClient::KeyActivationCode::ButtonUnlatchedOrReleased:
		{
			switch (event.objectID)
			{
				case alarm_SoftKey:
				{
					virtualTerminalUpdateHelper->set_active_data_or_alarm_mask(example_WorkingSet, example_AlarmMask);
				}
				break;

				case acknowledgeAlarm_SoftKey:
				{
					virtualTerminalUpdateHelper->set_active_data_or_alarm_mask(example_WorkingSet, mainRunscreen_DataMask);
				}
				break;

				default:
					break;
			}
		}
		break;

		default:
			break;
	}
}
```

버튼 콜백과 비슷하지만 `keyNumber`가 0인지도 확인한다. 이건 사용자가 VT의 전용 버튼을 눌러 알람을 확인(acknowledge)했을 때 전송되는 특수 소프트키 이벤트다. 그리고 여기서 하는 동작은 활성 마스크 전환이다. 메인 실행 화면 데이터 마스크 `mainRunscreen_DataMask`와 알람 마스크 `example_AlarmMask` 사이를 오간다. 이러면 VT에 팝업이 뜨고, 스피커가 있는 VT라면 경고음도 날 수 있다.

![VT 이벤트 흐름](/images/study-agisostack/13-vt-event-flow-light.png)
![VT 이벤트 흐름](/images/study-agisostack/13-vt-event-flow-dark.png)

### 그 밖의 이벤트

예제는 버튼과 소프트키 이벤트만 쓰지만, 쓸 수 있는 이벤트는 훨씬 많다.

- Change Numeric Value Events
- Pointing Events
- Change String Value Events
- Select Input Object Events
- Change Active Mask Events
- User Layout Hide/Show Events
- Audio Signal Termination Events
- ESC Messages

이 이벤트들을 조합하면 사용자가 화면에서 무엇을 하고 있는지에 대한 온갖 맥락을 얻을 수 있다.

각 이벤트는 전용 디스패처와 전용 구조체를 갖는다. 클라이언트가 제공하는 디스패처 접근자는 다음과 같다.

```cpp
EventDispatcher<VTKeyEvent> &get_vt_soft_key_event_dispatcher();
EventDispatcher<VTKeyEvent> &get_vt_button_event_dispatcher();
EventDispatcher<VTPointingEvent> &get_vt_pointing_event_dispatcher();
EventDispatcher<VTSelectInputObjectEvent> &get_vt_select_input_object_event_dispatcher();
EventDispatcher<VTESCMessageEvent> &get_vt_esc_message_event_dispatcher();
EventDispatcher<VTChangeNumericValueEvent> &get_vt_change_numeric_value_event_dispatcher();
EventDispatcher<VTChangeActiveMaskEvent> &get_vt_change_active_mask_event_dispatcher();
EventDispatcher<VTChangeSoftKeyMaskEvent> &get_vt_change_soft_key_mask_event_dispatcher();
EventDispatcher<VTChangeStringValueEvent> &get_vt_change_string_value_event_dispatcher();
EventDispatcher<VTUserLayoutHideShowEvent> &get_vt_user_layout_hide_show_event_dispatcher();
EventDispatcher<VTAudioSignalTerminationEvent> &get_vt_control_audio_signal_termination_event_dispatcher();
EventDispatcher<AuxiliaryFunctionEvent> &get_auxiliary_function_event_dispatcher();
```

주요 이벤트 구조체의 필드는 이렇다.

```cpp
struct VTPointingEvent
{
	VirtualTerminalClient *parentPointer;
	std::uint16_t xPosition;
	std::uint16_t yPosition;
	std::uint16_t parentObjectID;
	KeyActivationCode keyEvent;
};

struct VTSelectInputObjectEvent
{
	VirtualTerminalClient *parentPointer;
	std::uint16_t objectID;
	bool objectSelected;
	bool objectOpenForInput;
};

struct VTESCMessageEvent
{
	VirtualTerminalClient *parentPointer;
	std::uint16_t objectID;
	ESCMessageErrorCode errorCode;
};

struct VTChangeNumericValueEvent
{
	VirtualTerminalClient *parentPointer;
	std::uint32_t value;
	std::uint16_t objectID;
};

struct VTChangeStringValueEvent
{
	std::string value;
	VirtualTerminalClient *parentPointer;
	std::uint16_t objectID;
};

struct VTUserLayoutHideShowEvent
{
	VirtualTerminalClient *parentPointer;
	std::uint16_t objectID;
	bool isHidden;
};

struct VTAudioSignalTerminationEvent
{
	VirtualTerminalClient *parentPointer;
	bool isTerminated;
};
```

마스크 변경 이벤트는 오류 플래그가 함께 온다는 점이 특징이다. 마스크를 바꾸라고 했는데 VT가 왜 실패했는지 알 수 있다.

```cpp
struct VTChangeActiveMaskEvent
{
	VirtualTerminalClient *parentPointer;
	std::uint16_t maskObjectID;
	std::uint16_t errorObjectID;
	std::uint16_t parentObjectID;
	bool missingObjects;
	bool maskOrChildHasErrors;
	bool anyOtherError;
	bool poolDeleted;
};

struct VTChangeSoftKeyMaskEvent
{
	VirtualTerminalClient *parentPointer;
	std::uint16_t dataOrAlarmMaskObjectID;
	std::uint16_t softKeyMaskObjectID;
	bool missingObjects;
	bool maskOrChildHasErrors;
	bool anyOtherError;
	bool poolDeleted;
};
```

`poolDeleted`가 켜져 있으면 VT가 우리 오브젝트 풀을 지웠다는 뜻이다. 이 경우 재연결·재업로드가 필요하다.

ESC 메시지의 오류 코드는 세 가지다.

| 값 | 이름 | 의미 |
| --- | --- | --- |
| 0 | `NoError` | 오류 없음 |
| 1 | `NoInputFieldOpen` | 열려 있는 입력 필드가 없음 |
| 5 | `OtherError` | 위에 해당하지 않는 오류 |

### VT 클라이언트 설정

콜백을 만들었으니 이제 VT 클라이언트에게 그 콜백의 존재를 알려줘야 한다.

```cpp
virtualTerminalClient->get_vt_soft_key_event_dispatcher().add_listener(handle_softkey_event);
virtualTerminalClient->get_vt_button_event_dispatcher().add_listener(handle_button_event);
```

이게 VT 클라이언트에 리스너를 추가하는 방식이다. 리스너는 원하는 만큼 추가할 수 있고, 해당 이벤트가 발생하면 전부 호출된다.

그다음 VT 클라이언트를 초기화한다. `initialize` 함수를 호출하면 오브젝트 풀을 VT에 업로드하는 과정이 시작되고, 동시에 VT가 현재 활성 마스크와 그 밖의 VT 정보를 우리에게 보내주는 과정도 시작된다.

마지막으로 VT 업데이트 헬퍼를 설정한다. 반드시 써야 하는 건 아니지만, VT 갱신을 쉽게 해주고 숫자 값과 소프트키 마스크를 추적해주는 편리한 기능을 제공한다. 어떤 오브젝트를 추적할지 알려준 다음 `initialize`를 호출하면 된다.

```cpp
virtualTerminalUpdateHelper->add_tracked_numeric_value(ButtonExampleNumber_VarNum, 214748364); // In the object pool the output number has an offset of -214748364 so we use this to represent 0.
virtualTerminalUpdateHelper->initialize();
```

::: info 왜 214748364인가
`Minus_Button`과 `Plus_Button` 처리를 추가할 때, 화면에 표시되는 값을 추적하기 위해 프로그램 안의 변수를 증감시킨다. 이 변수의 시작값이 214748364인 이유는 오브젝트 풀의 output number에 -214748364라는 오프셋이 적용돼 있기 때문이다. 즉 VT에 214748364를 보내면 화면에는 0으로 표시된다. 1을 빼면 -1로, 1을 더하면 1로 표시된다. VT가 음수를 다루는 방식이 이렇다.
:::

### 그 밖의 동작

물론 이벤트에 반응하는 것 말고도 할 수 있는 일이 많다. VT 클라이언트는 오브젝트 풀을 대상으로 VT에게 직접 뭔가를 시키는 함수를 여럿 노출한다.

전체 목록은 API 문서나 헤더 파일 `isobus_virtual_terminal_client.hpp`를 보면 되고, 가장 많이 쓰는 것들은 다음과 같다.

| 하려는 일 | 클라이언트 함수 | 업데이트 헬퍼 함수 |
| --- | --- | --- |
| 활성 마스크 변경 | `send_change_active_mask` | `set_active_data_or_alarm_mask` |
| 숫자 값 변경 | `send_change_numeric_value` | `set_numeric_value` / `increase_numeric_value` / `decrease_numeric_value` |
| 문자열 값 변경 | `send_change_string_value` | — |
| 소프트키 마스크 변경 | `send_change_softkey_mask` | `set_active_soft_key_mask` |
| 리스트 항목 변경 | `send_change_list_item` | — |
| 속성 변경(컨테이너 숨기기 등) | `send_change_attribute` | `set_attribute` |

업데이트 헬퍼가 제공하는 API 전체는 다음과 같다.

```cpp
explicit VirtualTerminalClientUpdateHelper(std::shared_ptr<VirtualTerminalClient> client);

bool set_container_shown(std::uint16_t objectId, bool shown);
bool set_numeric_value(std::uint16_t objectId, std::uint32_t value);
bool increase_numeric_value(std::uint16_t objectId, std::uint32_t step = 1);
bool decrease_numeric_value(std::uint16_t objectId, std::uint32_t step = 1);
void set_callback_validate_numeric_value(const std::function<bool(std::uint16_t, std::uint32_t)> &callback);
bool set_active_data_or_alarm_mask(std::uint16_t workingSetId, std::uint16_t dataOrAlarmMaskId);
bool set_active_soft_key_mask(VirtualTerminalClient::MaskType maskType, std::uint16_t maskId, std::uint16_t softKeyMaskId);
bool set_attribute(std::uint16_t objectId, std::uint8_t attribute, std::uint32_t value);
bool set_attribute(std::uint16_t objectId, std::uint8_t attribute, float value);
```

`set_callback_validate_numeric_value`는 VT에서 들어온 숫자 값 변경을 받아들일지 말지 애플리케이션이 판단하게 해준다. 예를 들어 사용자가 입력한 값이 허용 범위를 벗어나면 거부할 수 있다.

## 최종 결과

지금까지의 조각을 하나로 합치면 완성된 예제가 된다.

::: details 전체 예제 코드
```cpp
#include "isobus/hardware_integration/available_can_drivers.hpp"
#include "isobus/hardware_integration/can_hardware_interface.hpp"
#include "isobus/isobus/can_network_manager.hpp"
#include "isobus/isobus/can_partnered_control_function.hpp"
#include "isobus/isobus/isobus_virtual_terminal_client.hpp"
#include "isobus/isobus/isobus_virtual_terminal_client_update_helper.hpp"
#include "isobus/utility/iop_file_interface.hpp"

#include "objectPoolObjects.h"

#include <atomic>
#include <csignal>
#include <iostream>

//! It is discouraged to use global variables, but it is done here for simplicity.
static std::shared_ptr<isobus::VirtualTerminalClient> virtualTerminalClient = nullptr;
static std::shared_ptr<isobus::VirtualTerminalClientUpdateHelper> virtualTerminalUpdateHelper = nullptr;
static std::atomic_bool running = { true };

void signal_handler(int)
{
	running = false;
}

// This callback will provide us with event driven notifications of softkey presses from the stack
void handle_softkey_event(const isobus::VirtualTerminalClient::VTKeyEvent &event)
{
	if (event.keyNumber == 0)
	{
		// We have the alarm ACK code, so if we have an active alarm, acknowledge it by going back to the main runscreen
		virtualTerminalUpdateHelper->set_active_data_or_alarm_mask(example_WorkingSet, mainRunscreen_DataMask);
	}

	switch (event.keyEvent)
	{
		case isobus::VirtualTerminalClient::KeyActivationCode::ButtonUnlatchedOrReleased:
		{
			switch (event.objectID)
			{
				case alarm_SoftKey:
				{
					virtualTerminalUpdateHelper->set_active_data_or_alarm_mask(example_WorkingSet, example_AlarmMask);
				}
				break;

				case acknowledgeAlarm_SoftKey:
				{
					virtualTerminalUpdateHelper->set_active_data_or_alarm_mask(example_WorkingSet, mainRunscreen_DataMask);
				}
				break;

				default:
					break;
			}
		}
		break;

		default:
			break;
	}
}

// This callback will provide us with event driven notifications of button presses from the stack
void handle_button_event(const isobus::VirtualTerminalClient::VTKeyEvent &event)
{
	switch (event.keyEvent)
	{
		case isobus::VirtualTerminalClient::KeyActivationCode::ButtonUnlatchedOrReleased:
		case isobus::VirtualTerminalClient::KeyActivationCode::ButtonStillHeld:
		{
			switch (event.objectID)
			{
				case Plus_Button:
				{
					virtualTerminalUpdateHelper->increase_numeric_value(ButtonExampleNumber_VarNum);
				}
				break;

				case Minus_Button:
				{
					virtualTerminalUpdateHelper->decrease_numeric_value(ButtonExampleNumber_VarNum);
				}
				break;

				default:
					break;
			}
		}
		break;

		default:
			break;
	}
}

int main()
{
	std::signal(SIGINT, signal_handler);

	// Automatically load the desired CAN driver based on the available drivers
	std::shared_ptr<isobus::CANHardwarePlugin> canDriver = nullptr;
#if defined(ISOBUS_SOCKETCAN_AVAILABLE)
	canDriver = std::make_shared<isobus::SocketCANInterface>("can0");
#elif defined(ISOBUS_WINDOWSPCANBASIC_AVAILABLE)
	canDriver = std::make_shared<isobus::PCANBasicWindowsPlugin>(PCAN_USBBUS1);
#elif defined(ISOBUS_WINDOWSINNOMAKERUSB2CAN_AVAILABLE)
	canDriver = std::make_shared<isobus::InnoMakerUSB2CANWindowsPlugin>(0); // CAN0
#elif defined(ISOBUS_MACCANPCAN_AVAILABLE)
	canDriver = std::make_shared<isobus::MacCANPCANPlugin>(PCAN_USBBUS1);
#elif defined(ISOBUS_SYS_TEC_AVAILABLE)
	canDriver = std::make_shared<isobus::SysTecWindowsPlugin>();
#endif
	if (nullptr == canDriver)
	{
		std::cout << "Unable to find a CAN driver. Please make sure you have one of the above drivers installed with the library." << std::endl;
		std::cout << "If you want to use a different driver, please add it to the list above." << std::endl;
		return -1;
	}

	isobus::CANHardwareInterface::set_number_of_can_channels(1);
	isobus::CANHardwareInterface::assign_can_channel_frame_handler(0, canDriver);

	if ((!isobus::CANHardwareInterface::start()) || (!canDriver->get_is_valid()))
	{
		std::cout << "Failed to start hardware interface. The CAN driver might be invalid." << std::endl;
		return -2;
	}

	std::this_thread::sleep_for(std::chrono::milliseconds(250));

	isobus::NAME TestDeviceNAME(0);

	//! Consider customizing some of these fields, like the function code, to be representative of your device
	TestDeviceNAME.set_arbitrary_address_capable(true);
	TestDeviceNAME.set_industry_group(1);
	TestDeviceNAME.set_device_class(0);
	TestDeviceNAME.set_function_code(static_cast<std::uint8_t>(isobus::NAME::Function::SteeringControl));
	TestDeviceNAME.set_identity_number(2);
	TestDeviceNAME.set_ecu_instance(0);
	TestDeviceNAME.set_function_instance(0);
	TestDeviceNAME.set_device_class_instance(0);
	TestDeviceNAME.set_manufacturer_code(1407);

	std::vector<std::uint8_t> testPool = isobus::IOPFileInterface::read_iop_file("VT3TestPool.iop");

	if (testPool.empty())
	{
		std::cout << "Failed to load object pool from VT3TestPool.iop" << std::endl;
		return -3;
	}
	std::cout << "Loaded object pool from VT3TestPool.iop" << std::endl;

	// Generate a unique version string for this object pool (this is optional, and is entirely application specific behavior)
	std::string objectPoolHash = isobus::IOPFileInterface::hash_object_pool_to_version(testPool);

	const isobus::NAMEFilter filterVirtualTerminal(isobus::NAME::NAMEParameters::FunctionCode, static_cast<std::uint8_t>(isobus::NAME::Function::VirtualTerminal));
	const std::vector<isobus::NAMEFilter> vtNameFilters = { filterVirtualTerminal };
	auto TestInternalECU = isobus::CANNetworkManager::CANNetwork.create_internal_control_function(TestDeviceNAME, 0);
	auto TestPartnerVT = isobus::CANNetworkManager::CANNetwork.create_partnered_control_function(0, vtNameFilters);

	virtualTerminalClient = std::make_shared<isobus::VirtualTerminalClient>(TestPartnerVT, TestInternalECU);
	virtualTerminalClient->set_object_pool(0, testPool.data(), testPool.size(), objectPoolHash);
	virtualTerminalClient->get_vt_soft_key_event_dispatcher().add_listener(handle_softkey_event);
	virtualTerminalClient->get_vt_button_event_dispatcher().add_listener(handle_button_event);
	virtualTerminalClient->initialize(true);

	virtualTerminalUpdateHelper = std::make_shared<isobus::VirtualTerminalClientUpdateHelper>(virtualTerminalClient);
	virtualTerminalUpdateHelper->add_tracked_numeric_value(ButtonExampleNumber_VarNum, 214748364); // In the object pool the output number has an offset of -214748364 so we use this to represent 0.
	virtualTerminalUpdateHelper->initialize();

	while (running)
	{
		// CAN stack runs in other threads. Do nothing forever.
		std::this_thread::sleep_for(std::chrono::milliseconds(1000));
	}

	virtualTerminalClient->terminate();
	isobus::CANHardwareInterface::stop();
	return 0;
}
```
:::

## CMake 작성

이 프로그램의 CMake는 다른 예제보다 조금 복잡하다.

"ISOBUS Hello World" 때와 똑같이 시작한다.

```cmake
cmake_minimum_required(VERSION 3.16)

project(
  isobus_vt_tutorial
  VERSION 1.0
  LANGUAGES CXX
  DESCRIPTION "An example VT client program"
)

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

add_subdirectory("AgIsoStack-plus-plus")

add_executable(vt_example main.cpp)
```

"ISOBUS Hello World"에서는 그다음이 이랬다.

```cmake
target_link_libraries(isobus_hello_world PRIVATE isobus::Isobus isobus::HardwareIntegration Threads::Threads)
```

하지만 앞서 말했듯이 이제 isobus utility 라이브러리(`Utility`)의 함수인 IOP 파일 리더를 쓰므로 그것도 링크해야 한다.

```cmake
target_link_libraries(isobus_hello_world PRIVATE isobus::Isobus isobus::HardwareIntegration isobus::Utility Threads::Threads)
```

그리고 빌드가 끝난 뒤 IOP 파일이 실행 파일과 같은 폴더에 있도록 옮겨야 프로그램이 그 파일을 찾을 수 있다. 다음 CMake 조각으로 처리한다.

```cmake
add_custom_command(
	TARGET vt_example
	POST_BUILD
	COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/VT3TestPool.iop
	$<TARGET_FILE_DIR:vt_example>/VT3TestPool.iop)
```

이제 빌드하고 실행할 수 있다.

```bash
cmake -S . -B build
cmake --build build
cd build
./vt_example
```

VT와 지원되는 CAN 드라이버만 있으면, 테스트 풀이 업로드되는 걸 보고 화면의 모든 버튼과 상호작용할 수 있다.

## Auxiliary Control (AUX-N) API

Auxiliary Control(AUX)은 운전자가 물리적 입력 장치로 작업기를 조작하게 해주는 기능이다. 조이스틱 버튼 하나로 작업기 붐을 올리고 내리는 식이다.

::: warning AUX-N과 AUX-O는 호환되지 않는다
보조 제어 프로토콜에는 신형(AUX-N)과 구형(AUX-O) 두 버전이 있다. 두 버전은 서로 <strong>호환되지 않는다</strong>.
:::

AUX는 두 부분으로 이뤄진다.

- <strong>Inputs</strong>: 운전자가 작업기를 조작하는 데 쓰는 개별 버튼·스위치·노브
- <strong>Functions</strong>: 올리기·내리기처럼 작업기가 수행할 수 있는 기능

이 둘은 <strong>매핑</strong>으로 연결된다. 매핑은 어떤 입력이 어떤 기능을 제어하는지를 결정한다. 이 매핑은 운전자가 Virtual Terminal 위에서 직접 할 수 있고, 결과는 작업기에 저장된다.

Inputs와 Functions 모두 Virtual Terminal 클라이언트가 AuxiliaryInputObject와 AuxiliaryOutputObject로 제공한다. 오브젝트 풀 안의 `AuxiliaryInputType2`(32) / `AuxiliaryFunctionType2`(31) 오브젝트가 그 실체다.

### Functions 쪽 — 입력을 받는 작업기

작업기 애플리케이션은 AUX 함수 이벤트 디스패처에 리스너를 붙여 할당된 입력이 움직였을 때를 알 수 있다.

```cpp
// This callback will provide us with event driven notifications of auxiliary input from the stack
void handle_aux_function_input(const isobus::VirtualTerminalClient::AuxiliaryFunctionEvent &event)
{
	std::cout << "Auxiliary function event received: (" << event.function.functionObjectID
	          << ", " << event.function.inputObjectID
	          << ", " << static_cast<int>(event.function.functionType)
	          << "), value1: " << event.value1
	          << ", value2: " << event.value2 << std::endl;
}

// ...
TestVirtualTerminalClient->get_auxiliary_function_event_dispatcher().add_listener(handle_aux_function_input);
```

이벤트 구조체와 그 안에 담기는 할당 정보는 다음과 같다.

```cpp
struct AuxiliaryFunctionEvent
{
	AssignedAuxiliaryFunction function; ///< The function
	VirtualTerminalClient *parentPointer; ///< A pointer to the parent VT client
	std::uint16_t value1; ///< The first value
	std::uint16_t value2; ///< The second value
};

class AssignedAuxiliaryFunction
{
public:
	AssignedAuxiliaryFunction(std::uint16_t functionObjectID,
	                          std::uint16_t inputObjectID,
	                          AuxiliaryTypeTwoFunctionType functionType);

	bool operator==(const AssignedAuxiliaryFunction &other) const;

	std::uint16_t functionObjectID; ///< The object ID of the function present in our object pool
	std::uint16_t inputObjectID; ///< The object ID assigned on the auxiliary inputs end
	AuxiliaryTypeTwoFunctionType functionType; ///< The type of function
};
```

### Inputs 쪽 — 입력을 제공하는 장치

반대로 조이스틱 같은 AUX 입력 장치를 만든다면, 자신이 제공하는 입력 오브젝트를 등록하고 상태 변화를 주기적으로 알린다.

```cpp
TestVirtualTerminalClient->set_auxiliary_input_model_identification_code(MODEL_IDENTIFICATION_CODE);
TestVirtualTerminalClient->add_auxiliary_input_object_id(AUXN_INPUT_SLIDER);
TestVirtualTerminalClient->add_auxiliary_input_object_id(AUXN_INPUT_BUTTON);

// ...

// 버튼: 눌림 상태와 전이 횟수를 보고
TestVirtualTerminalClient->update_auxiliary_input(AUXN_INPUT_BUTTON, buttonPressed, buttonTransitions);

// 아날로그 슬라이더: 위치를 보고. 전이 횟수는 의미 없으므로 0xFFFF
TestVirtualTerminalClient->update_auxiliary_input(AUXN_INPUT_SLIDER, sliderPosition, 0xFFFF);
```

운전자가 VT에서 매핑을 만드는 동안에는 클라이언트가 "학습 모드"에 들어간다. 이 상태는 `get_auxiliary_input_learn_mode_enabled()`로 확인할 수 있고, 학습 모드일 때는 입력 값을 갱신하지 않는 게 보통이다.

전체 동작 예제는 스택 저장소의 `examples/virtual_terminal/aux_functions`와 `examples/virtual_terminal/aux_inputs`에 있다.

## VT 서버 API 개요

지금까지는 클라이언트 쪽이었다. 스택은 VT <strong>서버</strong>(즉 터미널 자체)를 만드는 뼈대도 제공한다. 공식 문서 기준으로 서버 API는 아직 작업 중(Work in progress)이지만, 헤더는 이미 상당히 구체적이다.

핵심은 두 클래스다.

- `isobus::VirtualTerminalServer` — 서버가 구현해야 하는 순수 가상 인터페이스. `VirtualTerminalBase`를 상속한다.
- `isobus::VirtualTerminalServerManagedWorkingSet` — 접속한 클라이언트 하나의 워킹셋(업로드된 오브젝트 풀 포함)을 서버 쪽에서 관리하는 클래스. `VirtualTerminalWorkingSetBase`를 상속한다.

`VirtualTerminalServer`가 요구하는 순수 가상 함수는 대체로 "이 터미널은 어떤 물건인가"를 답하는 것들이다.

```cpp
virtual bool get_is_enough_memory(std::uint32_t requestedMemory) const = 0;
virtual VTVersion get_version() const = 0;
virtual std::uint8_t get_number_of_navigation_soft_keys() const = 0;
virtual std::uint8_t get_soft_key_descriptor_x_pixel_width() const = 0;
virtual std::uint8_t get_soft_key_descriptor_y_pixel_height() const = 0;
virtual std::uint8_t get_number_of_possible_virtual_soft_keys_in_soft_key_mask() const = 0;
virtual std::uint8_t get_number_of_physical_soft_keys() const = 0;
virtual std::uint16_t get_data_mask_area_size_x_pixels() const = 0;
virtual std::uint16_t get_data_mask_area_size_y_pixels() const = 0;
virtual std::vector<std::uint8_t> get_supported_objects() const = 0;
virtual SupportedWideCharsErrorCode get_supported_wide_chars(std::uint8_t codePlane, /* ... */) = 0;
virtual void suspend_working_set(std::shared_ptr<VirtualTerminalServerManagedWorkingSet> workingSetWithError) = 0;
```

나머지 절반은 비휘발성 저장소를 다루는 함수들이다. 클라이언트가 버전 라벨과 함께 풀을 올렸을 때 서버가 그걸 저장하고 다시 꺼내주는 부분이다. 앞에서 본 해시 기반 재업로드 회피가 서버 쪽에서는 이 함수들로 구현된다.

```cpp
virtual std::vector<std::array<std::uint8_t, 7>> get_versions(NAME clientNAME) = 0;
virtual std::vector<std::uint8_t> load_version(const std::vector<std::uint8_t> &versionLabel, NAME clientNAME) = 0;
virtual bool save_version(const std::vector<std::uint8_t> &objectPool, const std::vector<std::uint8_t> &versionLabel, NAME clientNAME) = 0;
virtual bool delete_version(const std::vector<std::uint8_t> &versionLabel, NAME clientNAME) = 0;
virtual bool delete_all_versions(NAME clientNAME) = 0;
virtual bool delete_object_pool(NAME clientNAME) = 0;
```

기본 구현이 제공돼 필요할 때만 재정의하면 되는 가상 함수도 있다.

```cpp
virtual VirtualTerminalBase::GraphicMode get_graphic_mode() const;
virtual std::uint8_t get_powerup_time() const;
virtual std::uint8_t get_supported_small_fonts_bitfield() const;
virtual std::uint8_t get_supported_large_fonts_bitfield() const;
virtual void identify_vt();
virtual void screen_capture(std::uint8_t item, std::uint8_t path, std::shared_ptr<ControlFunction> requestor);
virtual std::uint8_t get_user_layout_datamask_bg_color() const;
virtual std::uint8_t get_user_layout_softkeymask_bg_color() const;
virtual void transferred_object_pool_parse_start(std::shared_ptr<VirtualTerminalServerManagedWorkingSet> &ws) const;
```

`VirtualTerminalServerManagedWorkingSet`은 클라이언트가 올린 풀을 별도 스레드에서 파싱하는 구조라, 파싱 상태를 조회하고 진행률을 볼 수 있게 돼 있다.

```cpp
void start_parsing_thread();
void join_parsing_thread();
ObjectPoolProcessingThreadState get_object_pool_processing_state();
bool get_any_object_pools() const;
std::shared_ptr<ControlFunction> get_control_function() const;

std::uint32_t get_working_set_maintenance_message_timestamp_ms() const;
void set_working_set_maintenance_message_timestamp_ms(std::uint32_t value);

bool get_was_object_pool_loaded_from_non_volatile_memory() const;
void set_object_focus(std::uint16_t objectID);
std::uint16_t get_object_focus() const;

void set_iop_size(std::uint32_t newIopSize);
float iop_load_percentage() const;
bool is_object_pool_transfer_in_progress() const;

void request_deletion();
bool is_deletion_requested() const;
```

`iop_load_percentage()`가 있으니 업로드 진행률 바를 터미널 화면에 띄우는 것도 가능하다. 이 부분은 실제로 터미널 제품을 만들 때 필요한 API이고, 작업기 애플리케이션만 개발한다면 클라이언트 쪽만 알아도 충분하다.

::: tip 핵심 정리
- VT 통신의 창구는 `VirtualTerminalClient`다. VT 서버를 가리키는 `PartneredControlFunction`과 자신의 `InternalControlFunction`을 shared pointer로 넘겨 만든다. 파트너는 `NAME::Function::VirtualTerminal` function code 필터로 잡는다.
- 오브젝트 풀은 ISO 11783-6이 정의한 오브젝트 목록의 바이너리 덩어리다. `IOPFileInterface::read_iop_file`로 `.iop`을 읽어 `set_object_pool(poolIndex, data, size, version)`으로 등록한다. 넘긴 포인터는 업로드가 끝날 때까지 유효해야 한다.
- `hash_object_pool_to_version`으로 만든 해시를 version으로 주면, 풀이 안 바뀐 경우 VT가 캐시에서 로드해 업로드 시간을 절약한다. RAM이 부족하면 `register_object_pool_data_chunk_callback`, 해상도가 다르면 `set_object_pool_scaling`을 쓴다.
- 이벤트는 디스패처에 리스너를 등록해 받는다. `get_vt_button_event_dispatcher()` / `get_vt_soft_key_event_dispatcher()`가 대표적이고, `VTKeyEvent`의 `keyEvent`(`KeyActivationCode`)와 `objectID`로 분기한다. 그 외에 포인팅·ESC·마스크 변경·문자열 변경 등 12종의 디스패처가 있다.
- `VirtualTerminalClientUpdateHelper`는 추적 중인 값을 관리하며 `increase_numeric_value` / `set_active_data_or_alarm_mask` 같은 편의 API를 제공한다. 저수준으로는 `send_change_numeric_value`, `send_change_active_mask` 등을 직접 호출할 수 있다.
- CMake에서는 `isobus::Utility`를 링크하고, `add_custom_command`로 `.iop` 파일을 실행 파일 옆에 복사해야 한다.
- AUX-N은 Inputs(물리 버튼·노브)와 Functions(작업기 동작)를 VT 위에서 매핑하는 기능이다. 작업기 쪽은 `get_auxiliary_function_event_dispatcher()`, 입력 장치 쪽은 `add_auxiliary_input_object_id` / `update_auxiliary_input`을 쓴다.
- VT 서버를 만들 때는 `VirtualTerminalServer`의 순수 가상 함수(터미널 능력·버전 저장소)를 구현하고, 접속한 클라이언트마다 `VirtualTerminalServerManagedWorkingSet`으로 풀을 관리한다.
:::

## 참고

- 원문: [Virtual Terminal Basics — AgIsoStack++ Documentation](https://isobus-plus-plus.readthedocs.io/en/latest/Tutorials/Virtual%20Terminal%20Basics.html)
- 원문: [Virtual Terminal API — AgIsoStack++ Documentation](https://isobus-plus-plus.readthedocs.io/en/latest/api/virtual%20terminal/index.html)
- 소스: [Open-Agriculture/AgIsoStack-plus-plus](https://github.com/Open-Agriculture/AgIsoStack-plus-plus) (MIT License)
- 예제: [`examples/virtual_terminal/version3_object_pool`](https://github.com/Open-Agriculture/AgIsoStack-plus-plus/tree/main/examples/virtual_terminal/version3_object_pool)

## 다음 챕터

[CH14. Task Controller와 DDOP](/study/agisostack/14-tc-ddop)로 이어진다.
