---
title: "CH8. 메시지 수신"
description: "PGN 콜백을 등록해 브로드캐스트·목적지 지정 메시지를 받고, TP/ETP 다중 프레임 메시지가 같은 콜백으로 도착하는 원리를 확인한다"
date: 2026-07-20
tags: [AgIsoStack, ISOBUS, C++]
---

# CH8. 메시지 수신

## 학습 목표
- 스택의 수신은 언제나 콜백 형태라는 것을 이해한다
- `add_global_parameter_group_number_callback` 으로 브로드캐스트 PGN 콜백을 등록한다
- 콜백 시그니처와 컨텍스트 포인터(`void *parentPointer`)의 쓰임을 안다
- 프로그램을 계속 살려 두는 메인 루프를 만들어 수신을 테스트한다
- 파트너에 콜백을 붙여 목적지 지정 메시지를 받는다
- TP/ETP 다중 프레임 메시지도 같은 콜백 하나로 도착한다는 사실을 확인한다

## 수신은 전부 콜백이다

여기까지 CAN 스택을 세우고, 브로드캐스트 메시지를 보내는 법을 봤다. 이제 메시지를 받는 법을 배운다.

CAN 스택에서 메시지를 받는 일은 <strong>언제나 콜백 형태로</strong> 이뤄진다. 애플리케이션이 버스를 폴링하는 게 아니라, 스택이 수신 스레드에서 프레임을 처리하고 조건에 맞는 메시지가 도착하면 내가 등록해 둔 함수를 불러 준다.

![수신 경로: CAN 프레임에서 콜백까지](/images/study-agisostack/08-rx-callback-flow-light.png)
![수신 경로: CAN 프레임에서 콜백까지](/images/study-agisostack/08-rx-callback-flow-dark.png)

::: info 관련 스터디
PGN 과 목적지 주소(DA)가 프레임 어디에 들어가는지는 이론 스터디에 정리돼 있다.
[ISOBUS CH9. J1939 메시지 구조](/study/isobus/09-j1939-message) · [ISOBUS CH11. J1939 전송 프로토콜](/study/isobus/11-j1939-transport)
:::

## 브로드캐스트 메시지 수신

브로드캐스트 메시지가 받기 가장 쉽다. 받고 싶은 PGN 에 대해 콜백을 등록하기만 하면 된다.

이 예제에서는 브로드캐스트 주소로 전송된 proprietary A 메시지를 전부 처리하는 함수를 정의한다.

```cpp
void propa_callback(const isobus::CANMessage &CANMessage, void *)
{
  std::cout << CANMessage.get_data_length() << std::endl;
}
```

이 콜백 자체는 딱히 쓸모 있는 일을 하지 않지만, 콜백 시스템을 어떻게 쓰는지는 보여 준다. 기본적으로, 브로드캐스트 주소로 전송된 PROPA 메시지가 수신될 때마다 그 메시지의 길이를 콘솔에 찍는다.

이제 적절한 메시지가 도착했을 때 그 콜백을 호출하라고 CAN 스택에 알려주기만 하면 된다.

```cpp
isobus::CANNetworkManager::CANNetwork.add_global_parameter_group_number_callback(0xEF00, propa_callback, nullptr);
```

위 코드는 PGN 0xEF00 인 브로드캐스트 메시지에 대해 저 함수를 호출하라고 스택에 알려주는 것이다. `nullptr` 자리는 범용 컨텍스트 변수다. 여기에 넘긴 값은 나중에 콜백이 호출될 때 그대로 콜백으로 전달된다.

이건 어떤 객체가 이 콜백을 원했는지 알아내는 데 유용하다. 예를 들어 어떤 클래스를 위해 이 콜백을 등록하는 상황이라면, 그 클래스가 `this` 를 이 인자로 넘겨서 콜백에서 자기 자신의 포인터를 돌려받게 할 수 있다.

지금 단계에서 마지막 인자의 쓰임이 잘 이해되지 않아도 괜찮다. 이 예제에서는 그냥 무시하고 있다.

::: tip 콜백 시그니처
등록되는 콜백의 타입은 라이브러리에 이렇게 정의돼 있다.

```cpp
using CANLibCallback = void (*)(const CANMessage &message, void *parentPointer);
```

일반 함수 포인터이므로 캡처가 있는 람다는 그대로 넘길 수 없다. 인스턴스 상태가 필요하면 `parentPointer` 로 객체 포인터를 넘기고 콜백 안에서 캐스팅해 쓰는 것이 이 라이브러리의 관용적인 패턴이다.
:::

## 어떻게 테스트하나

예제 프로그램이 메시지를 받으려면 계속 실행 중이어야 한다. 그러니 방금의 변경을 테스트하려면, 우리가 명시적으로 종료를 원할 때까지 프로그램을 살려 둬야 한다. 이를 위해 메인 스레드를 일정 간격으로 재우고, 가끔 깨워서 프로그램을 끝낼지 계속 돌릴지 확인하게 한다.

```cpp
while (running)
{
   // CAN stack runs in other threads. Do nothing for a while.
   std::this_thread::sleep_for(std::chrono::milliseconds(1000));
}
```

`running` 은 [CH7](/study/agisostack/07-hello-world)에서 만든 SIGINT 핸들러가 내려 주는 `std::atomic_bool` 이다. 즉 Ctrl+C 를 누르면 루프가 빠져나가고 `stop()` 으로 이어진다.

그래서 갱신된 예제 프로그램은 이제 이런 모습이 된다.

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

void propa_callback(const isobus::CANMessage &CANMessage, void *)
{
  std::cout << CANMessage.get_data_length() << std::endl;
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

   // Create our InternalControlFunction
   myECU = isobus::CANNetworkManager::CANNetwork.create_internal_control_function(myNAME, 0);

   // Define a NAME filter for our partner
   std::vector<isobus::NAMEFilter> myPartnerFilter;
   const isobus::NAMEFilter virtualTerminalFilter(isobus::NAME::NAMEParameters::FunctionCode, static_cast<std::uint8_t>(isobus::NAME::Function::VirtualTerminal));
   myPartnerFilter.push_back(virtualTerminalFilter);

   // Register to receive broadcast PROPA messages
   isobus::CANNetworkManager::CANNetwork.add_global_parameter_group_number_callback(0xEF00, propa_callback, nullptr);

   // Create our PartneredControlFunction
   myPartner = isobus::CANNetworkManager::CANNetwork.create_partnered_control_function(0, myPartnerFilter);

   std::this_thread::sleep_for(std::chrono::milliseconds(1000));

   std::array<std::uint8_t, isobus::CAN_DATA_LENGTH> messageData = {0}; // Data is just all zeros

   // Send a message to the broadcast address
   isobus::CANNetworkManager::CANNetwork.send_can_message(0xEF00, messageData.data(), isobus::CAN_DATA_LENGTH, myECU);

   // Send a message to our partner (if it is present)
   isobus::CANNetworkManager::CANNetwork.send_can_message(0xEF00, messageData.data(), isobus::CAN_DATA_LENGTH, myECU, myPartner);

   while (running)
   {
      // CAN stack runs in other threads. Do nothing for a while.
      std::this_thread::sleep_for(std::chrono::milliseconds(1000));
   }

   // Clean up the threads
   isobus::CANHardwareInterface::stop();

   return 0;
}
```

::: warning 테스트는 생각보다 까다롭다
이 코드를 테스트하기는 만만치 않다. 스택이 메시지를 받아 내 콜백으로 넘겨주려면, 버스 위에 <strong>제대로 주소 클레임을 마친</strong> 또 다른 유효한 ISO 11783 장치가 있으면서 이 메시지를 보내 주고 있어야 하기 때문이다.

요점은, 이 코드를 내 필요에 맞게 고쳐서 내가 관심 있는 메시지를 받으라는 것이다.
:::

::: info 버스 관찰 팁
콜백이 불리지 않을 때 문제가 어디에 있는지 좁히려면, 우선 프레임이 버스에 실제로 오가는지부터 보는 게 빠르다. can-utils 의 `candump can0` 로 트래픽을 그대로 볼 수 있고, 내 프로그램이 주소 클레임(PGN 0xEE00)을 보내고 있는지, PROPA(0xEF00)가 나가는지 확인할 수 있다. 다만 `cansend` 로 아무 프레임이나 쏘아서는 콜백이 불리지 않는다. 위 경고처럼 송신자가 주소 클레임을 마친 컨트롤 펑션이어야 스택이 그 메시지를 넘겨준다.
:::

## 목적지 지정 메시지 수신

특정 목적지로 메시지를 보낼 때와 마찬가지로, 특정 상대로부터 오는 메시지를 받을 때도 `PartneredControlFunction` 이 필요하다.

수신 대상을 특정한 파트너(혹은 최소한 원하는 function code)로 제한하는 것은 애플리케이션의 효율에 도움이 된다. 항상 모든 사람으로부터 모든 메시지를 받는 것만큼 성능을 빠르게 죽이는 일도 없다.

앞의 코드에서, 우리 VT 파트너가 보내는 PROPA 메시지에 대해 콜백을 받고 싶다면 이렇게 추가하면 된다.

```cpp
myPartner->add_parameter_group_number_callback(0xEF00, propa_callback, nullptr);
```

이걸로 끝이다. 이제 그 파트너가 우리에게 특정해서 PROPA 메시지를 보낼 때마다 콜백이 호출된다. 물론 같은 콜백 함수를 브로드캐스트용으로도 등록해 뒀으니, 이제 그 함수는 브로드캐스트 PROPA 일 때도, 파트너가 우리에게 보낸 PROPA 일 때도 호출된다.

::: tip 두 등록 지점의 차이
| 등록 | 대상 | 호출 조건 |
| --- | --- | --- |
| `CANNetworkManager::add_global_parameter_group_number_callback(pgn, cb, ctx)` | 네트워크 매니저 전역 | 해당 PGN 의 <strong>브로드캐스트</strong> 메시지 |
| `partner->add_parameter_group_number_callback(pgn, cb, ctx)` | 특정 파트너 객체 | 그 파트너가 <strong>나에게</strong> 보낸 해당 PGN 메시지 |

같은 함수를 양쪽에 걸어 두면 두 경우 모두에서 불린다. 어느 쪽으로 온 메시지인지 구분해야 한다면 콜백 안에서 `CANMessage` 의 목적지·송신자 정보를 확인하거나, 콜백을 나눠 등록하면 된다.
:::

`NAMEFilter` 를 만들고 파트너를 생성하는 부분은 다음 챕터에서 자세히 다룬다.

## TP·ETP 메시지 수신에 관한 한마디

다중 프레임 메시지는 다음 챕터에서 좀 더 이야기하겠지만, 여기서 짚고 갈 것이 있다. <strong>지금 배운 이 방법이 곧 다중 프레임 TP·ETP 메시지를 받는 방법이기도 하다.</strong>

예를 들어 누군가 BAM 으로 1785바이트짜리 PROPA 메시지를 보내면, 그것 역시 우리 콜백으로 전달된다.

![TP/ETP 재조립: 다중 프레임도 콜백은 한 번](/images/study-agisostack/08-tp-reassembly-light.png)
![TP/ETP 재조립: 다중 프레임도 콜백은 한 번](/images/study-agisostack/08-tp-reassembly-dark.png)

즉 프레임 조각을 모으고 세션을 관리하는 일은 전부 스택이 처리하고, 애플리케이션은 완성된 메시지를 한 번에 받는다. 콜백 안에서 `get_data_length()` 를 찍어 보면 8 이 아니라 1785 가 나온다. 이제 크기와 PGN 을 가리지 않고 메시지를 받는 법을 알게 된 셈이다.

::: tip 핵심 정리
- 스택의 수신은 전부 콜백이다. 폴링하는 API 는 없다.
- 브로드캐스트: `CANNetworkManager::CANNetwork.add_global_parameter_group_number_callback(PGN, callback, context)`.
- 목적지 지정: 파트너 객체에 `add_parameter_group_number_callback(PGN, callback, context)`.
- 콜백 타입은 `void (*)(const isobus::CANMessage &, void *)` 이며, 세 번째 등록 인자가 그대로 두 번째 콜백 인자로 돌아온다.
- 수신하려면 프로그램이 계속 살아 있어야 한다. `while (running)` 루프로 메인 스레드를 유지하고, Ctrl+C 로 빠져나온 뒤 `stop()` 한다.
- 받을 것을 파트너/PGN 으로 좁히는 것이 성능에 유리하다.
- TP·ETP 다중 프레임도 같은 콜백 하나로 재조립되어 도착한다.
:::

## 원문 출처
이 챕터는 AgIsoStack++ 공식 문서 [Receiving Messages](https://isobus-plus-plus.readthedocs.io/en/latest/Tutorials/Receiving%20Messages.html) 를 바탕으로 재구성했다. (MIT License)

## 다음 챕터
[CH9. 목적지 지정 통신](/study/agisostack/09-adding-destination)으로 이어진다.
