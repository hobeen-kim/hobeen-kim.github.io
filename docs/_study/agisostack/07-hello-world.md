---
title: "CH7. ISOBUS Hello World"
description: "빈 C++ 프로젝트에서 시작해 NAME 구성·InternalControlFunction 생성·SocketCAN 연결을 거쳐 브로드캐스트 메시지 한 통을 버스에 올려 본다"
date: 2026-07-20
tags: [AgIsoStack, ISOBUS, C++]
---

# CH7. ISOBUS Hello World

## 학습 목표
- 빈 C++ 프로그램에 AgIsoStack++ 헤더를 붙이고 최소 골격을 세운다
- `isobus::NAME` 의 각 필드를 채워 내 장치의 정체성을 스택에 알려준다
- `InternalControlFunction` 을 만들어 NAME 과 CAN 채널을 묶는다
- `CANHardwareInterface` 와 `SocketCANInterface` 로 스택을 실제 CAN 하드웨어에 연결한다
- 주소 클레임이 끝날 때까지 기다린 뒤 PROPA(PGN 0xEF00) 메시지를 글로벌 주소로 보낸다
- CMake 로 라이브러리와 함께 빌드해 실행한다

## 이 챕터가 만드는 것

이번 챕터는 라이브러리를 새 C++ 프로그램에 붙이고, 브로드캐스트 주소로 기본 메시지 한 통을 보내는 것까지를 목표로 한다. 앞선 설치 과정을 마쳤고, NAME 과 Control Function 같은 개념을 한 번 훑었다는 전제로 진행한다.

ISOBUS 모듈은 크게 세 덩어리로 나뉜다. <strong>Hardware API</strong> 는 CAN 트랜시버 드라이버와 원시 CAN 프레임을 다룬다. <strong>Networking API</strong> 는 Control Function 을 통해 데이터를 듣고 다른 모듈에 보내는 일, 그리고 메시지 처리를 위한 전송 프로토콜을 담당한다. <strong>Application</strong> 은 수신한 데이터를 처리하고 무엇을 보낼지 결정하는, 내가 직접 쓰는 코드다.

![ISOBUS 모듈의 3계층](/images/study-agisostack/07-stack-layers-light.png)
![ISOBUS 모듈의 3계층](/images/study-agisostack/07-stack-layers-dark.png)

::: info 관련 스터디
NAME·주소 클레임·PGN 같은 밑바탕 개념이 흐릿하다면 이론 스터디를 먼저 보는 편이 좋다.
[ISOBUS CH9. J1939 메시지 구조](/study/isobus/09-j1939-message) · [ISOBUS CH10. J1939 주소 체계](/study/isobus/10-j1939-address) · [AgIsoStack CH3. Control Function 과 NAME](/study/agisostack/03-control-function-name)
:::

## 첫 단계

`main.cpp` 라는 파일에 표준적인 빈 C++ 프로그램을 만들고, 라이브러리를 쓰기 위해 필요한 기본 헤더를 넣는다.

```cpp
#include "isobus/isobus/can_network_manager.hpp"
#include "isobus/hardware_integration/socket_can_interface.hpp"
#include "isobus/hardware_integration/can_hardware_interface.hpp"
#include "isobus/isobus/can_partnered_control_function.hpp"

int main()
{
	return 0;
}
```

각 헤더의 역할은 이렇다.

| 헤더 | 역할 |
| --- | --- |
| `can_network_manager.hpp` | CAN 스택의 메인 인터페이스 |
| `socket_can_interface.hpp` | 소켓 CAN 용 하드웨어 연결부 |
| `can_hardware_interface.hpp` | 하드웨어 계층 추상화(채널 관리·스레드 기동) |
| `can_partnered_control_function.hpp` | 통신 상대 장치를 뜻하는 <em>partnered control function</em> 의 인터페이스 정의 |

## 스택에게 내가 누구인지 알려주기 (NAME)

CAN 버스에서 통신하려면 먼저 NAME 이 있어야 한다. NAME 은 버스 위에서 내 장치를 유일하게 식별하는 값이다.

::: tip 네임스페이스
스택에 속한 모든 것은 `isobus` 네임스페이스 안에 있다.
:::

먼저 빈 NAME 을 하나 만든다.

```cpp
#include "isobus/isobus/can_network_manager.hpp"
#include "isobus/hardware_integration/socket_can_interface.hpp"
#include "isobus/hardware_integration/can_hardware_interface.hpp"
#include "isobus/isobus/can_partnered_control_function.hpp"

int main()
{
 isobus::NAME myNAME(0); // Create an empty NAME

 return 0;
}
```

NAME 객체는 생겼지만 아직 알맹이가 없다. 내 컨트롤 펑션의 세부 정보를 채워 넣는다.

```cpp
#include "isobus/isobus/can_network_manager.hpp"
#include "isobus/hardware_integration/socket_can_interface.hpp"
#include "isobus/hardware_integration/can_hardware_interface.hpp"
#include "isobus/isobus/can_partnered_control_function.hpp"

int main()
{
 isobus::NAME myNAME(0); // Create an empty NAME

 // Set up NAME fields
 myNAME.set_arbitrary_address_capable(true);
 myNAME.set_industry_group(1);
 myNAME.set_device_class(0);
 myNAME.set_function_code(static_cast<std::uint8_t>(isobus::NAME::Function::SteeringControl));
 myNAME.set_identity_number(2);
 myNAME.set_ecu_instance(0);
 myNAME.set_function_instance(0);
 myNAME.set_device_class_instance(0);
 myNAME.set_manufacturer_code(1407);

 return 0;
}
```

이제 NAME 에 실제 정보가 인코딩됐다. 이 예제에서 나는 온하이웨이 조향 컨트롤러이고, 시리얼 번호는 2, 주소 중재(arbitrary address)를 지원하며, 제조사 코드 1407 — Open-Agriculture 제조사 코드 — 로 만들어졌다고 주장하고 있다.

이 값들은 반드시 내 장치의 정체성에 맞게 바꿔야 한다. 각 값을 어떻게 정할지 모르겠다면 [isobus.net](https://www.isobus.net/isobus/) 을 참고하면 된다.

참고로 여기서 쓴 `isobus::NAME::Function::SteeringControl` 처럼 편의를 위해 미리 정의된 function 값들이 있지만, 표준에 정의된 값이라면 무엇이든 쓸 수 있다.

## InternalControlFunction 만들기

NAME 을 정의했으니, 이제 그 NAME 을 내 장치의 CAN 채널에 연결해야 한다. 그래야 CAN 스택이 이 NAME 으로 주소 클레임을 수행할 수 있다.

스택에게 NAME 을 알려주는 수단이 `InternalControlFunction` 이다. 내가 보내는 메시지의 "출발지"라고 생각하면 된다. 나중에 이 객체를 쓸 때, 그것이 곧 어떤 NAME/주소에서 메시지를 보낼지를 스택에 알려주는 역할을 한다.

아래 예제는 `shared_ptr` 로 `InternalControlFunction` 을 담지만, 일반 객체든 raw 포인터든 원하는 방식을 써도 된다.

```cpp
#include "isobus/isobus/can_network_manager.hpp"
#include "isobus/hardware_integration/socket_can_interface.hpp"
#include "isobus/hardware_integration/can_hardware_interface.hpp"
#include "isobus/isobus/can_partnered_control_function.hpp"

#include <memory>

int main()
{
 isobus::NAME myNAME(0); // Create an empty NAME
 std::shared_ptr<isobus::InternalControlFunction> myECU = nullptr; // A pointer to hold our InternalControlFunction

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
 myECU = isobus::CANNetworkManager::CANNetwork.create_internal_control_function(myNAME, 0, 0x1C);

 return 0;
}
```

이 예제에서는 선호 주소(preferred address)를 0x1C 로 두고 CAN 채널 0 에 컨트롤 펑션을 할당했다. 선호 주소를 생략하면 API 기본값은 0xFE(NULL CAN 주소)인데, 이는 0xFE 를 클레임하려 시도하라는 뜻이 아니라 유효한 동적 범위에서 스택이 알아서 임의의 주소를 고르라는 뜻이다.

그런데 여기서 문제가 하나 생긴다. CAN 채널 0 이란 대체 무엇인가? 다음 절에서 그걸 설정한다.

## 스택을 CAN 하드웨어에 연결하기

이 절에서는 소켓 CAN 장치를 CAN 채널 0 으로 설정한다. 소켓 CAN 장치 이름으로는 `can0` 을 쓴다.

시스템에 CAN 어댑터가 있다면 지금 꽂혀 있는지 확인할 시점이다.

터미널을 열고 `can0` 을 ISOBUS 네트워크용(250k baud)으로 설정하고 인터페이스를 올린다.

```bash
sudo ip link set can0 up type can bitrate 250000
```

이 단계가 실패하면 인터페이스를 먼저 내렸다가 다시 올려야 할 수도 있다.

```bash
sudo ip link set can0 down
sudo ip link set can0 up type can bitrate 250000
```

이제 `can0` 과 CAN 스택을 잇는 코드를 프로그램에 추가한다. 필요한 줄은 다음과 같다.

```cpp
std::shared_ptr<isobus::SocketCANInterface> canDriver = std::make_shared<isobus::SocketCANInterface>("can0");
isobus::CANHardwareInterface::set_number_of_can_channels(1);
isobus::CANHardwareInterface::assign_can_channel_frame_handler(0, canDriver);

if ((!isobus::CANHardwareInterface::start()) || (!canDriver->get_is_valid()))
{
   std::cout << "Failed to start hardware interface. The CAN driver might be invalid." << std::endl;
   return -1;
}
```

`CANHardwareInterface` 는 CAN 스택에 직접 묶여 있지 않은 독립 컴포넌트다. 어떤 하드웨어를 쓰든 그 차이를 스택으로부터 감춰 주는 역할을 한다.

각 줄이 하는 일을 하나씩 보면 이렇다.

- `std::shared_ptr<isobus::SocketCANInterface> canDriver = std::make_shared<isobus::SocketCANInterface>("can0");` — 새 `SocketCANInterface` 객체를 만들어 `shared_ptr` 에 담는다. 소켓 CAN 드라이버와 실제로 대화하는 객체다.
- `isobus::CANHardwareInterface::set_number_of_can_channels(1)` — 하드웨어 계층(여기서는 소켓 CAN)에 CAN 어댑터를 1개 쓸 것이라고 알려준다.
- `isobus::CANHardwareInterface::assign_can_channel_frame_handler(0, canDriver);` — 방금 만든 `SocketCANInterface` 객체를 CAN 채널 0 의 핸들러로 쓰겠다고 알려준다.
- `isobus::CANHardwareInterface::start();` — 소켓을 관리하고 메시지 수신 시 콜백을 발생시키는 여러 스레드를 띄운다. 스택을 주기적으로 'tick' 하는 콜백도 여기서 제공된다. 이 함수의 반환값과 `get_is_valid()` 를 확인하면 하부 CAN 드라이버가 하드웨어에 연결됐는지 알 수 있다. 소켓 CAN 을 쓰는 지금은 소켓 바인딩에 성공했는지를 알려주는 셈이다.

여기까지 합치면 이렇게 된다.

```cpp
#include "isobus/isobus/can_network_manager.hpp"
#include "isobus/hardware_integration/socket_can_interface.hpp"
#include "isobus/hardware_integration/can_hardware_interface.hpp"
#include "isobus/isobus/can_partnered_control_function.hpp"

#include <memory>
#include <iostream>

int main()
{
   isobus::NAME myNAME(0); // Create an empty NAME
   std::shared_ptr<isobus::InternalControlFunction> myECU = nullptr; // A pointer to hold our InternalControlFunction

   // Set up the hardware layer to use SocketCAN interface on channel "can0"
   std::shared_ptr<isobus::SocketCANInterface> canDriver = std::make_shared<isobus::SocketCANInterface>("can0");
   isobus::CANHardwareInterface::set_number_of_can_channels(1);
   isobus::CANHardwareInterface::assign_can_channel_frame_handler(0, canDriver);

   if ((!isobus::CANHardwareInterface::start()) || (!canDriver->get_is_valid()))
   {
      std::cout << "Failed to start hardware interface. The CAN driver might be invalid." << std::endl;
      return -2;
   }

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
   myECU = isobus::CANNetworkManager::CANNetwork.create_internal_control_function(myNAME, 0, 0x1C);

   return 0;
}
```

메시지를 보낼 준비가 거의 다 됐다. 다만 프로그램이 끝날 때 CAN 스택을 우아하게 멈추는 코드를 몇 줄 더 넣어야 한다. 메모리 누수와 종료 시 크래시를 막는 데 도움이 된다.

## 정리하기

프로그램이 끝날 때는 `isobus::CANHardwareInterface::stop();` 을 호출해 하드웨어 계층을 정리하고 `start()` 로 띄운 스레드를 멈춰야 한다.

또한 사용자가 Ctrl+C 를 누르면(즉 프로그램에 SIGINT 를 보내면) 종료되도록 해야 한다. 그러니 그런 상황에서 우아하게 정리해 줄 작은 시그널 핸들러를 추가한다.

`csignal` 과 `atomic` 헤더를 잊지 말고 포함한다. `csignal` 은 Ctrl+C 같은 시그널 처리를 위한 것이고, `atomic` 은 종료 시점을 안전하게 판단하는 데 쓸 `running` 플래그를 위한 것이다.

```cpp
#include "isobus/isobus/can_network_manager.hpp"
#include "isobus/hardware_integration/socket_can_interface.hpp"
#include "isobus/hardware_integration/can_hardware_interface.hpp"
#include "isobus/isobus/can_partnered_control_function.hpp"

#include <atomic>
#include <memory>
#include <csignal>
#include <iostream>

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

   // Set up the hardware layer to use SocketCAN interface on channel "can0"
   std::shared_ptr<isobus::SocketCANInterface> canDriver = std::make_shared<isobus::SocketCANInterface>("can0");
   isobus::CANHardwareInterface::set_number_of_can_channels(1);
   isobus::CANHardwareInterface::assign_can_channel_frame_handler(0, canDriver);

   if ((!isobus::CANHardwareInterface::start()) || (!canDriver->get_is_valid()))
   {
      std::cout << "Failed to start hardware interface. The CAN driver might be invalid." << std::endl;
      return -2;
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
   myECU = isobus::CANNetworkManager::CANNetwork.create_internal_control_function(myNAME, 0, 0x1C);

   // Clean up the threads
   isobus::CANHardwareInterface::stop();

   return 0;
}
```

## 서둘러서… 기다리기

메시지를 보내기 전에 하나 더. 주소 클레임은 스택이 완료하기까지 시간이 걸린다. 그래서 `main` 스레드에 짧은 지연을 넣어, 다른 일을 하기 전에 주소 클레임이 끝나기를 기다린다.

```cpp
std::this_thread::sleep_for(std::chrono::milliseconds(1000));
```

여기까지의 결과는 이렇다.

```cpp
#include "isobus/isobus/can_network_manager.hpp"
#include "isobus/hardware_integration/socket_can_interface.hpp"
#include "isobus/hardware_integration/can_hardware_interface.hpp"
#include "isobus/isobus/can_partnered_control_function.hpp"

#include <atomic>
#include <memory>
#include <csignal>
#include <iostream>

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

 // Set up the hardware layer to use SocketCAN interface on channel "can0"
 std::shared_ptr<isobus::SocketCANInterface> canDriver = std::make_shared<isobus::SocketCANInterface>("can0");
 isobus::CANHardwareInterface::set_number_of_can_channels(1);
 isobus::CANHardwareInterface::assign_can_channel_frame_handler(0, canDriver);

 if ((!isobus::CANHardwareInterface::start()) || (!canDriver->get_is_valid()))
 {
 	 std::cout << "Failed to start hardware interface. The CAN driver might be invalid." << std::endl;
 	 return -2;
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
 myECU = isobus::CANNetworkManager::CANNetwork.create_internal_control_function(myNAME, 0, 0x1C);

 std::this_thread::sleep_for(std::chrono::milliseconds(1000));

 // Clean up the threads
 isobus::CANHardwareInterface::stop();

 return 0;
}
```

지금까지의 기동·종료 순서를 한 장으로 정리하면 이렇다.

![Hello World 프로그램의 기동·종료 순서](/images/study-agisostack/07-startup-sequence-light.png)
![Hello World 프로그램의 기동·종료 순서](/images/study-agisostack/07-startup-sequence-dark.png)

## 메시지 보내기

드디어 기다리던 순간이다. CAN 메시지를 보낸다.

이 예제에서는 proprietary A 메시지(PGN 0xEF00)를 글로벌/브로드캐스트 주소(0xFF)로 보낸다.

가장 기본적인 송신 방법은 `CANNetworkManager` 인터페이스의 `send_can_message` 함수를 호출하는 것이다. 8바이트 메시지를 만들고, 데이터를 채우고, 보낸다.

```cpp
 std::array<std::uint8_t, isobus::CAN_DATA_LENGTH> messageData = {0}; // Data is just all zeros

isobus::CANNetworkManager::CANNetwork.send_can_message(0xEF00, messageData.data(), isobus::CAN_DATA_LENGTH, myECU);

// Give the CAN stack some time to send the message
std::this_thread::sleep_for(std::chrono::milliseconds(10));
```

이 코드는 전부 0 으로 채운 8바이트 메시지를, PROPA 용 PGN(0xEF00)으로 글로벌 주소에 보낸다. 그리고 종료 전에 잠깐 기다려서 메시지가 확실히 버스에 나가도록 한다. 대기 시간은 임의의 값이고, 보통의 프로그램에서는 이런 대기가 필요 없다. 다만 이 예제는 대기가 없으면 즉시 종료되기 때문에 CAN 스택에 메시지를 처리할 시간을 주는 것이다.

::: warning 대기는 예제용 장치다
`sleep_for` 로 주소 클레임과 송신을 기다리는 건 예제를 짧게 만들기 위한 방법이다. 실제 애플리케이션은 계속 돌아가는 메인 루프를 갖게 되므로 이런 인위적 대기가 필요 없다. 메인 루프 형태는 [CH8. 메시지 수신](/study/agisostack/08-receiving-messages)에서 다룬다.
:::

## CMake 로 컴파일하기

설치 안내를 따랐다면 방금 쓴 프로그램은 어떤 폴더 안에 있고, 라이브러리는 `AgIsoStack-plus-plus` 라는 디렉토리에 있을 것이다. 이런 모양이다.

```bash
ls
AgIsoStack-plus-plus main.cpp
```

CMake 로 전부 컴파일되게 하려면 `CMakeLists.txt` 파일을 추가한다. 새 파일 `CMakeLists.txt` 에 다음을 넣는다.

```cmake
cmake_minimum_required(VERSION 3.16)

project(
  isobus_hello
  VERSION 1.0
  LANGUAGES CXX
  DESCRIPTION "ISOBUS Hello World Program"
)

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

add_subdirectory("AgIsoStack-plus-plus")

add_executable(isobus_hello_world main.cpp)

target_link_libraries(isobus_hello_world PRIVATE isobus::Isobus isobus::HardwareIntegration isobus::Utility Threads::Threads)
```

저장하고 닫은 뒤, CMake 로 타깃을 구성한다.

```bash
cmake -S . -B build
```

그리고 컴파일한다.

```bash
cmake --build build
```

모두 잘 됐다면 이렇게 실행할 수 있다.

```bash
./build/isobus_hello_world
```

이걸로 끝이다. 이제 버스 위에서 말을 하고 있는 셈이다.

::: details 전체 예제 코드 (main.cpp)
```cpp
#include "isobus/isobus/can_network_manager.hpp"
#include "isobus/hardware_integration/socket_can_interface.hpp"
#include "isobus/hardware_integration/can_hardware_interface.hpp"
#include "isobus/isobus/can_partnered_control_function.hpp"

#include <atomic>
#include <memory>
#include <csignal>
#include <iostream>

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

 // Set up the hardware layer to use SocketCAN interface on channel "can0"
 std::shared_ptr<isobus::SocketCANInterface> canDriver = std::make_shared<isobus::SocketCANInterface>("can0");
 isobus::CANHardwareInterface::set_number_of_can_channels(1);
 isobus::CANHardwareInterface::assign_can_channel_frame_handler(0, canDriver);

 if ((!isobus::CANHardwareInterface::start()) || (!canDriver->get_is_valid()))
 {
 	 std::cout << "Failed to start hardware interface. The CAN driver might be invalid." << std::endl;
 	 return -2;
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
 myECU = isobus::CANNetworkManager::CANNetwork.create_internal_control_function(myNAME, 0, 0x1C);

 std::this_thread::sleep_for(std::chrono::milliseconds(1000));

 std::array<std::uint8_t, isobus::CAN_DATA_LENGTH> messageData = {0}; // Data is just all zeros

 isobus::CANNetworkManager::CANNetwork.send_can_message(0xEF00, messageData.data(), isobus::CAN_DATA_LENGTH, myECU);

 // Give the CAN stack some time to send the message
 std::this_thread::sleep_for(std::chrono::milliseconds(10));

 // Clean up the threads
 isobus::CANHardwareInterface::stop();

 return 0;
}
```
:::

::: tip 핵심 정리
- 스택 사용의 최소 골격은 <strong>하드웨어 계층 준비 → 스레드 기동 → NAME 구성 → InternalControlFunction 생성 → 주소 클레임 대기 → 송신 → stop()</strong> 이다.
- `isobus::NAME` 은 내 장치가 누구인지 선언하는 값이다. function code, 제조사 코드, identity number 등을 실제 장치에 맞게 바꿔야 한다.
- `create_internal_control_function(NAME, CANPort, preferredAddress)` 로 NAME 과 CAN 채널을 묶는다. 선호 주소를 생략하면 기본값 0xFE 가 되어 스택이 동적 범위에서 주소를 고른다.
- `CANHardwareInterface` 는 스택과 분리된 하드웨어 추상 계층이다. `start()` 가 수신·tick 스레드를 띄우고, `stop()` 이 정리한다. `start()` 반환값과 `get_is_valid()` 를 둘 다 확인해야 한다.
- 주소 클레임은 즉시 끝나지 않는다. 송신 전에 스택이 클레임을 마칠 시간을 줘야 한다.
- 링크할 타깃은 `isobus::Isobus`, `isobus::HardwareIntegration`, `isobus::Utility`, 그리고 `Threads::Threads` 다.
:::

## 원문 출처
이 챕터는 AgIsoStack++ 공식 문서 [The ISOBUS Hello World!](https://isobus-plus-plus.readthedocs.io/en/latest/Tutorials/The%20ISOBUS%20Hello%20World.html) 를 바탕으로 재구성했다. (MIT License)

## 다음 챕터
[CH8. 메시지 수신](/study/agisostack/08-receiving-messages)으로 이어진다.
