---
title: "CH9. 목적지 지정 통신"
description: "NAMEFilter 로 통신 상대를 정의하고 PartneredControlFunction 을 만들어 특정 장치에게만 메시지를 보낸다"
date: 2026-07-20
tags: [AgIsoStack, ISOBUS, C++]
---

# CH9. 목적지 지정 통신

## 학습 목표
- `isobus::NAMEFilter` 로 어떤 장치와 통신할지 조건을 기술한다
- 필터 여러 개를 조합할 때의 매칭 규칙을 안다
- `create_partnered_control_function` 으로 파트너를 만든다
- `send_can_message` 에 파트너를 넘겨 목적지 지정 메시지를 보낸다
- Hello World 코드와 합쳐 완전한 프로그램을 완성한다

## 왜 파트너가 필요한가

[CH7. ISOBUS Hello World](/study/agisostack/07-hello-world)에서 CAN 스택을 세우고 브로드캐스트 주소로 간단한 메시지를 보내는 법을 배웠다. 그런데 글로벌 주소가 아니라 특정 상대에게 보내고 싶다면 어떻게 할까? 예를 들어 버추얼 터미널(VT)과 콕 집어 대화하고 싶다고 하자.

여기서 등장하는 개념이 `PartneredControlFunction` 이다. 예제 프로그램에 VT 파트너를 추가해 보자.

문제는 상대의 주소를 미리 알 수 없다는 데 있다. ISOBUS 에서 주소는 전원이 들어올 때마다 주소 클레임으로 정해지므로, 코드에 주소를 박아 둘 수 없다. 대신 <strong>어떤 NAME 을 가진 장치</strong>인지를 기술해 두면, 스택이 그 조건에 맞는 장치가 버스에 나타날 때 알아서 묶어 준다.

::: info 관련 스터디
주소 클레임과 NAME 이 어떻게 주소를 결정하는지는 이론 스터디에 정리돼 있다.
[ISOBUS CH10. J1939 주소 체계](/study/isobus/10-j1939-address) · [ISOBUS CH14. ISOBUS 네트워크 관리](/study/isobus/14-isobus-network-mgmt) · [AgIsoStack CH3. Control Function 과 NAME](/study/agisostack/03-control-function-name)
:::

## NAME 필터

가장 먼저 할 일은 우리가 VT 에만 관심 있다는 사실을 CAN 스택에 알려줄 필터를 만드는 것이다. 이것을 <strong>NAME 필터</strong>라고 부른다.

`PartneredControlFunction` 을 만들 때는 반드시 NAME 필터를 함께 넘겨야 한다. 그래야 스택이 내가 어떤 종류의 장치와 대화하고 싶은지 알 수 있다. 필터는 원하는 만큼 구체적으로 쓸 수도 있고, 느슨하게 쓸 수도 있다. "function" 이나 "manufacturer code" 처럼 <strong>같은 키에 대해 값이 여러 개인 필터를 추가하면 스택은 그중 하나라도 맞으면 매칭</strong>으로 처리한다.

필터를 만들어 보자.

```cpp
std::vector<isobus::NAMEFilter> myPartnerFilter;

const isobus::NAMEFilter virtualTerminalFilter(isobus::NAME::NAMEParameters::FunctionCode, static_cast<std::uint8_t>(isobus::NAME::Function::VirtualTerminal));

myPartnerFilter.push_back(virtualTerminalFilter);
```

여기서 우리는 필터의 벡터 하나와 필터 자체 하나를 만들었다. 이 경우 function code 가 버추얼 터미널의 function code 와 일치하는 ECU 를 걸러내고 싶은 것이다. 그리고 그 필터를 필터 목록에 추가했다.

`NAMEFilter` 의 첫 인자는 NAME 의 어떤 필드를 볼지 지정하는 `isobus::NAME::NAMEParameters` 열거값이고, 두 번째 인자는 그 필드에 기대하는 값이다. 주로 쓰는 파라미터는 다음과 같다.

| `NAMEParameters` 값 | 거르는 대상 |
| --- | --- |
| `IdentityNumber` | 장치 고유 시리얼 번호 |
| `ManufacturerCode` | 제조사 코드 |
| `EcuInstance` | 같은 기능을 하는 ECU 들 사이의 인스턴스 번호 |
| `FunctionInstance` | 같은 function 안의 인스턴스 번호 |
| `FunctionCode` | 장치의 기능(VT, TC, TECU 등) |
| `DeviceClass` | 장치 클래스 |
| `DeviceClassInstance` | 장치 클래스 인스턴스 |
| `IndustryGroup` | 산업 그룹(농업 = 2) |
| `ArbitraryAddressCapable` | 주소 중재 지원 여부 |

이 필터가 실제로 무엇을 걸러내는지 그림으로 보면 이렇다.

![NAME 필터 매칭](/images/study-agisostack/09-partner-matching-light.png)
![NAME 필터 매칭](/images/study-agisostack/09-partner-matching-dark.png)

::: warning 너무 좁게 잡으면 못 만난다
필터를 `IdentityNumber` 까지 지정하면 특정 개체 하나만 매칭된다. 개발 장비를 바꾸거나 현장에 다른 개체가 들어오는 순간 파트너가 영원히 잡히지 않는다. 보통은 `FunctionCode` 수준으로 시작하고, 같은 종류의 장치가 여러 대 붙는 버스에서만 `ManufacturerCode` 나 인스턴스 값을 더한다.
:::

## 파트너 생성

먼저 파트너를 담을 포인터를 만든다. 예제에서는 `shared_ptr` 을 쓰지만, 일반 객체든 raw 포인터든 원하는 것을 써도 된다.

`shared_ptr` 을 쓰는 주된 이유는 `VirtualTerminalClient` 의 인터페이스가 그걸 기대하기 때문이다.

```cpp
std::shared_ptr<isobus::PartneredControlFunction> myPartner = nullptr;

myPartner = isobus::CANNetworkManager::CANNetwork.create_partnered_control_function(0, myPartnerFilter);
```

위에서 우리는 앞 단계에서 만든 필터를 써서 <em>CAN 채널 0 에</em> 파트너를 인스턴스화했다.

그 필터에 일치하는 장치가 버스에 나타나면, CAN 스택이 그 장치를 우리 `PartneredControlFunction` 에 연결해 준다.

이것을 내 메시지의 "목적지"라고 생각하면 된다. 목적지 지정 메시지를 보낼 때는 `send_can_message` 함수에 `PartneredControlFunction` 을 넘겨야 한다.

## 목적지 지정 메시지 전송

이 단계에서는 proprietary A 메시지를 만들어 파트너에게 보낸다.

```cpp
std::array<std::uint8_t, isobus::CAN_DATA_LENGTH> messageData = {0}; // Data is just all zeros

isobus::CANNetworkManager::CANNetwork.send_can_message(0xEF00, messageData.data(), isobus::CAN_DATA_LENGTH, myECU, myPartner);
```

보다시피, 네트워크 매니저에 메시지 전송을 요청하는 호출은 브로드캐스트 주소로 보낼 때와 거의 같고, 파트너 `myPartner` 가 추가됐다는 점만 다르다.

![브로드캐스트와 목적지 지정 송신 경로](/images/study-agisostack/09-send-paths-light.png)
![브로드캐스트와 목적지 지정 송신 경로](/images/study-agisostack/09-send-paths-dark.png)

`send_can_message` 가 받을 수 있는 모든 파라미터를 한 번 훑어 두면 어떤 선택지가 있는지 알 수 있어 좋다. 전체 시그니처는 이렇다.

```cpp
bool send_can_message(std::uint32_t parameterGroupNumber,
                      const std::uint8_t *dataBuffer,
                      std::uint32_t dataLength,
                      std::shared_ptr<InternalControlFunction> sourceControlFunction,
                      std::shared_ptr<ControlFunction> destinationControlFunction = nullptr,
                      CANIdentifier::CANPriority priority = CANIdentifier::CANPriority::PriorityDefault6,
                      TransmitCompleteCallback txCompleteCallback = nullptr,
                      void *parentPointer = nullptr,
                      DataChunkCallback frameChunkCallback = nullptr);
```

목적지를 생략하면 기본값 `nullptr` 이 되어 브로드캐스트가 된다. 우선순위, 송신 완료 콜백, 큰 메시지를 조각 단위로 공급받는 콜백까지 여기서 지정할 수 있다.

프로그램이 그대로 즉시 종료되는 구조라면, 메시지가 실제로 나가도록 약간의 지연을 넣는 편이 좋다.

```cpp
std::this_thread::sleep_for(std::chrono::milliseconds(10));
```

## 전체 코드 조립

이 튜토리얼의 최종 프로그램은 (앞선 Hello World 코드를 포함해서) 이렇게 된다.

::: details 전체 예제 코드 (main.cpp)
```cpp
#include "isobus/isobus/can_network_manager.hpp"
#include "isobus/hardware_integration/socket_can_interface.hpp"
#include "isobus/hardware_integration/can_hardware_interface.hpp"
#include "isobus/isobus/can_partnered_control_function.hpp"

#include <atomic>
#include <csignal>
#include <iostream>
#include <memory>

// This helps us handle control+c and other requests to terminate the program
static std::atomic_bool running = { true };

void signal_handler(int)
{
	running = false;
}

int main()
{
   isobus::NAME myNAME(0); // Create an empty NAME
   std::shared_ptr<isobus::InternalControlFunction> myECU = nullptr; // A pointer to hold our InternalControlFunction
   std::shared_ptr<isobus::PartneredControlFunction> myPartner = nullptr; // A pointer to hold a partner

   // Set up the hardware layer to use SocketCAN interface on channel "can0"
   std::shared_ptr<isobus::SocketCANInterface> canDriver = std::make_shared<isobus::SocketCANInterface>("can0");
   isobus::CANHardwareInterface::set_number_of_can_channels(1);
   isobus::CANHardwareInterface::assign_can_channel_frame_handler(0, canDriver);

   if ((!isobus::CANHardwareInterface::start()) || (!canDriver->get_is_valid()))
   {
      std::cout << "Failed to start hardware interface. The CAN driver might be invalid." << std::endl;
      return -1;
   }

   // Handle control+c
   std::signal(SIGINT, signal_handler);

   //! Consider customizing some of these fields, like the function code, to be representative of your device
   myNAME.set_arbitrary_address_capable(true);
   myNAME.set_industry_group(1);
   myNAME.set_device_class(0);
   myNAME.set_function_code(static_cast<std::uint8_t>(isobus::NAME::Function::SteeringControl));
   myNAME.set_identity_number(2);
   myNAME.set_ecu_instance(0);
   myNAME.set_function_instance(0);
   myNAME.set_device_class_instance(0);
   myNAME.set_manufacturer_code(1407);

   // Define a NAME filter for our partner
   std::vector<isobus::NAMEFilter> myPartnerFilter;
   const isobus::NAMEFilter virtualTerminalFilter(isobus::NAME::NAMEParameters::FunctionCode, static_cast<std::uint8_t>(isobus::NAME::Function::VirtualTerminal));
   myPartnerFilter.push_back(virtualTerminalFilter);

   // Create our InternalControlFunction
   myECU = isobus::CANNetworkManager::CANNetwork.create_internal_control_function(myNAME, 0);

   // Create our PartneredControlFunction
   myPartner = isobus::CANNetworkManager::CANNetwork.create_partnered_control_function(0, myPartnerFilter);

   std::this_thread::sleep_for(std::chrono::milliseconds(1000));

   std::array<std::uint8_t, isobus::CAN_DATA_LENGTH> messageData = {0}; // Data is just all zeros

   // Send a message to the broadcast address
   isobus::CANNetworkManager::CANNetwork.send_can_message(0xEF00, messageData.data(), isobus::CAN_DATA_LENGTH, myECU);

   // Send a message to our partner (if it is present)
   isobus::CANNetworkManager::CANNetwork.send_can_message(0xEF00, messageData.data(), isobus::CAN_DATA_LENGTH, myECU, myPartner);

   std::this_thread::sleep_for(std::chrono::milliseconds(10));

   // Clean up the threads
   isobus::CANHardwareInterface::stop();

   return 0;
}
```
:::

앞서와 마찬가지로 `cmake --build build` 로 컴파일하고 실행하면 된다.

::: warning 파트너가 아직 없으면
파트너에게 보내는 호출은 필터에 맞는 장치가 실제로 버스에서 주소 클레임을 마쳤을 때에만 의미가 있다. 그래서 원문 주석도 "Send a message to our partner (<em>if it is present</em>)" 라고 적어 둔 것이다. VT 가 없는 버스에서는 이 호출이 실제 프레임으로 이어지지 않는다.
:::

::: tip 핵심 정리
- ISOBUS 에서는 상대 주소를 코드에 박을 수 없다. 대신 NAME 조건으로 상대를 기술한다.
- `isobus::NAMEFilter(NAMEParameters::필드, 기댓값)` 를 `std::vector<isobus::NAMEFilter>` 에 모아 넘긴다.
- 같은 키에 값이 여러 개면 <strong>OR</strong> 매칭이다.
- `create_partnered_control_function(CANPort, NAMEFilters)` 가 파트너를 만든다. 조건에 맞는 장치가 나타나면 스택이 자동으로 연결한다.
- 브로드캐스트와 목적지 지정 송신의 차이는 `send_can_message` 의 다섯 번째 인자(목적지) 하나뿐이다.
- 파트너는 송신용이자 수신용이다. 파트너에 PGN 콜백을 붙이면 그 상대가 나에게 보낸 메시지만 받는다([CH8](/study/agisostack/08-receiving-messages) 참고).
:::

## 원문 출처
이 챕터는 AgIsoStack++ 공식 문서 [Adding A Destination](https://isobus-plus-plus.readthedocs.io/en/latest/Tutorials/Adding%20a%20Destination.html) 를 바탕으로 재구성했다. (MIT License)

## 다음 챕터
[CH10. 전송 계층 사용하기](/study/agisostack/10-transport-layer)로 이어진다.
