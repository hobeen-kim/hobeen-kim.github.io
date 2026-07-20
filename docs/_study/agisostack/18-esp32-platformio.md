---
title: "CH18. ESP32와 PlatformIO"
description: "PlatformIO로 ESP32 프로젝트를 만들고 AgIsoStack++를 붙여 TWAI로 ISOBUS에 연결하기 — menuconfig 설정, 배선, VT 클라이언트 예제까지"
date: 2026-07-20
tags: [AgIsoStack, ISOBUS, ESP32, PlatformIO, 임베디드]
---

# CH18. ESP32와 PlatformIO

## 학습 목표
- PlatformIO 개발 환경을 설치하고 ESP-IDF 프레임워크로 ESP32 프로젝트를 만들 수 있다.
- `platformio.ini`에 AgIsoStack++ 의존성과 디버깅 옵션을 설정할 수 있다.
- ESP32의 TWAI 컨트롤러를 설정해 `TWAIPlugin`으로 스택에 연결할 수 있다.
- `menuconfig`에서 PThreads 스택 크기와 FreeRTOS 틱 레이트를 왜, 어떻게 맞춰야 하는지 설명할 수 있다.
- ESP32 - CAN 트랜시버 - 버스 커넥터 배선을 구성할 수 있다.
- VT 클라이언트 예제를 빌드해 실제 ISOBUS 디스플레이에 오브젝트 풀을 올릴 수 있다.

## 왜 ESP32인가

ESP32에는 사실상 <strong>클래식 CAN 2.0 컨트롤러가 내장</strong>돼 있다. Espressif는 이걸 TWAI(Two-Wire Automotive Interface)라고 부른다. 덕분에 MCP2515 같은 별도의 시리얼 CAN 컨트롤러를 붙이지 않고도 ISOBUS 노드를 만들 수 있다. AgIsoStack++는 이 TWAI를 감싼 `TWAIPlugin`을 내장 드라이버로 제공한다.

이번 챕터에서는 툴링을 세팅하고, 빈 프로젝트를 만들고, VT 클라이언트 예제를 돌리는 것까지 한 번에 훑는다.

![PlatformIO 프로젝트 셋업 흐름](/images/study-agisostack/18-platformio-flow-light.png)
![PlatformIO 프로젝트 셋업 흐름](/images/study-agisostack/18-platformio-flow-dark.png)

## 설치

1. [Visual Studio Code](https://code.visualstudio.com/download)를 설치한다.
2. [Git](https://git-scm.com/downloads)을 설치한다.
3. VS Code에서 PlatformIO 확장을 설치한다. VS Code 왼쪽 사이드바의 확장(Extensions) 탭에서 "PlatformIO IDE"를 검색해 설치하면 된다.
4. PlatformIO 확장을 선택하고 설치가 끝날 때까지 기다린다. 몇 분이 걸릴 수 있다.
5. 설치가 끝나면 VS Code를 재시작하거나 다시 로드하라는 안내가 뜰 수 있다. 뜨면 그대로 따른다.

여기까지 하면 필요한 건 전부 설치된 상태다.

::: tabs
@tab macOS
```bash
brew install --cask visual-studio-code
brew install git
```
이후 VS Code 확장 탭에서 PlatformIO IDE를 설치한다.

@tab Linux
```bash
sudo apt install git
```
VS Code는 배포판 패키지나 [공식 .deb](https://code.visualstudio.com/download)로 설치한 뒤, 확장 탭에서 PlatformIO IDE를 설치한다.

@tab Windows
```powershell
winget install Microsoft.VisualStudioCode
winget install Git.Git
```
이후 VS Code 확장 탭에서 PlatformIO IDE를 설치한다.
:::

## 빈 프로젝트로 시작하기

AgIsoStack을 쓰는 빈 PlatformIO 프로젝트를 만드는 기본 절차는 이렇다.

### 프로젝트 생성

1. VS Code를 열고 PlatformIO 확장을 선택한 뒤 "Create New Project" 또는 "New Project"를 클릭한다. PlatformIO 홈 화면 가운데에 있는 버튼이다.
2. 프로젝트 이름을 정하고, 대상 ESP32 보드를 선택한다. 이때 <strong>Framework는 반드시 `Espidf`</strong>를 골라야 한다. Arduino 프레임워크가 아니다.
3. PlatformIO가 프로젝트를 만들 때까지 기다린다. 인터넷에서 받아와야 할 데이터 양에 따라 몇 분이 걸릴 수 있다.
4. 프로젝트가 만들어지면 VS Code가 워크스페이스를 신뢰할지 물어볼 수 있다. "Yes"를 누르고, 원한다면 프로젝트 폴더를 항상 신뢰하도록 체크해 둔다.
5. 이제 빈 프로젝트가 생겼다. 여기까지 제대로 했는지 확인하려면 이 상태로 한 번 빌드해 보면 된다. 성공해야 한다.

### C++로 전환하기

이제 이 프로젝트에 AgIsoStack 라이브러리를 붙일 차례다.

AgIsoStack++는 C++ 라이브러리이므로, 메인 파일을 C가 아니라 C++로 컴파일해야 한다. 그런데 ESP-IDF 프레임워크는 `app_main`이 <strong>C 링키지</strong>를 가질 것을 기대한다. 파일을 C++로 바꿨으니 `extern "C"` 데코레이션을 붙여 줘야 한다. 안 그러면 빌드할 때 링커 에러가 난다.

1. `main.c` 파일 이름을 `main.cpp`로 바꾼다.
2. `app_main` 정의를 `extern "C" void app_main()`으로 바꾼다.

### 라이브러리 의존성 추가

`platformio.ini` 파일에 다음 한 줄을 추가한다.

```ini
lib_deps = https://github.com/Open-Agriculture/AgIsoStack-plus-plus.git
```

이렇게 하면 PlatformIO가 GitHub에서 라이브러리를 내려받아 CMake로 자동 통합해 준다.

::: warning 자동 업데이트는 안 된다
PlatformIO는 AgIsoStack을 자동으로 업데이트하지 않는다. PlatformIO Core CLI에서 `pio pkg update`를 실행해서 직접 갱신해야 한다. 최신 기능과 버그 픽스를 반영하려면 <strong>가끔씩 이 작업을 해 주는 게 중요하다</strong>.
:::

### 디버깅 옵션

선택 사항이지만, CAN 스택이 기록한 에러·경고 메시지를 시리얼 모니터로 보내고 애플리케이션이 크래시했을 때 백트레이스를 해석해 주도록 `platformio.ini`에 다음을 추가하면 좋다.

```ini
build_type = debug
upload_protocol = esptool
monitor_speed = 115200
monitor_rts = 0
monitor_dtr = 0
monitor_filters = esp32_exception_decoder
```

최종적으로 `platformio.ini`는 다음과 비슷한 모양이 된다. 보드와 환경 이름은 다를 수 있다.

```ini
; PlatformIO Project Configuration File
;
;   Build options: build flags, source filter
;   Upload options: custom upload port, speed and extra flags
;   Library options: dependencies, extra library storages
;   Advanced options: extra scripting
;
; Please visit documentation for the other options and examples
; https://docs.platformio.org/page/projectconf.html

[env:denky32]
platform = espressif32
board = denky32
framework = espidf

lib_deps = https://github.com/Open-Agriculture/AgIsoStack-plus-plus.git

build_type = debug
upload_protocol = esptool
monitor_speed = 115200
monitor_rts = 0
monitor_dtr = 0
monitor_filters = esp32_exception_decoder
```

이 설정은 ESP-WROOM-32(denky32)를 기준으로 만든 것이다. 다른 보드를 쓴다면 여기에 맞게 고쳐야 한다.

### 헤더 인클루드

AgIsoStack++는 꽤 큰 라이브러리다. 파일이 많고, 각각이 특정 CAN·ISOBUS 기능별로 나뉘어 있다. 무엇을 인클루드할지는 다른 튜토리얼이나 아래 VT 예제를 참고하면 된다.

무언가를 보내거나 받으려면 <strong>최소한</strong> 다음 파일들이 필요하다.

```cpp
#include "isobus/hardware_integration/twai_plugin.hpp"
#include "isobus/hardware_integration/can_hardware_interface.hpp"
#include "isobus/isobus/can_network_manager.hpp"
#include "isobus/isobus/can_partnered_control_function.hpp"
```

### TWAI 설정

앞서 말했듯 ESP32에는 클래식 CAN 2.0 컨트롤러가 내장돼 있다. 그래서 MCP2515 같은 시리얼 CAN 컨트롤러를 따로 붙이지 않고 ESP32의 TWAI 인터페이스를 쓸 수 있다.

::: warning 트랜시버는 여전히 필요하다
TWAI 컨트롤러의 저전압 출력을 실제 CAN 신호 전압으로 변환하려면 <strong>CAN 트랜시버가 반드시 있어야 한다</strong>. TWAI 핀에 CAN 버스를 직접 연결하면 안 된다. SN65HVD230 계열 보드가 흔히 쓰인다.
:::

다음 코드를 추가하면 TWAI가 설정된다.

```cpp
extern "C" void app_main()
{
    twai_general_config_t twaiConfig = TWAI_GENERAL_CONFIG_DEFAULT(GPIO_NUM_21, GPIO_NUM_22, TWAI_MODE_NORMAL);
    twai_timing_config_t twaiTiming = TWAI_TIMING_CONFIG_250KBITS();
    twai_filter_config_t twaiFilter = TWAI_FILTER_CONFIG_ACCEPT_ALL();
    std::shared_ptr<isobus::CANHardwarePlugin> canDriver = std::make_shared<isobus::TWAIPlugin>(&twaiConfig, &twaiTiming, &twaiFilter);
}
```

이 코드가 하는 일은 네 가지다.

- GPIO 21과 GPIO 22를 각각 TWAI 송신·수신 핀으로 설정한다.
- ISO11783/J1939의 기본 보 레이트인 250 kbit/s를 설정한다.
- 버스의 모든 메시지가 스택까지 전달되도록 한다. 하드웨어 단에서 아무것도 필터링하지 않는다.
- AgIsoStack의 TWAI 드라이버 클래스 인스턴스를 만든다. 이후 TWAI 관리는 이 객체가 맡는다.

GPIO 핀을 꼭 이 조합으로 할 필요는 없다. 다만 이 조합은 잘 동작한다고 알려져 있다.

### NAME 설정과 스택 시작

거의 모든 AgIsoStack 프로젝트에 들어가는 보일러플레이트다. ESP32에 맞게 약간 손본 형태다.

```cpp
#include "esp_log.h"
#include "freertos/task.h"

extern "C" void app_main()
{
    twai_general_config_t twaiConfig = TWAI_GENERAL_CONFIG_DEFAULT(GPIO_NUM_21, GPIO_NUM_22, TWAI_MODE_NORMAL);
    twai_timing_config_t twaiTiming = TWAI_TIMING_CONFIG_250KBITS();
    twai_filter_config_t twaiFilter = TWAI_FILTER_CONFIG_ACCEPT_ALL();
    std::shared_ptr<isobus::CANHardwarePlugin> canDriver = std::make_shared<isobus::TWAIPlugin>(&twaiConfig, &twaiTiming, &twaiFilter);

    isobus::CANHardwareInterface::set_number_of_can_channels(1);
    isobus::CANHardwareInterface::assign_can_channel_frame_handler(0, canDriver);
    isobus::CANHardwareInterface::set_periodic_update_interval(10); // Default is 4ms, but we need to adjust this for default ESP32 tick rate of 100Hz

    if (!isobus::CANHardwareInterface::start() || !canDriver->get_is_valid())
    {
        ESP_LOGE("AgIsoStack", "Failed to start hardware interface, the CAN driver might be invalid");
    }

    isobus::NAME TestDeviceNAME(0);

    //! Consider customizing some of these fields, like the function code, to be representative of your device
    TestDeviceNAME.set_arbitrary_address_capable(true);
    TestDeviceNAME.set_industry_group(1);
    TestDeviceNAME.set_device_class(0);
    TestDeviceNAME.set_function_code(static_cast<std::uint8_t>(isobus::NAME::Function::RateControl));
    TestDeviceNAME.set_identity_number(2);
    TestDeviceNAME.set_ecu_instance(0);
    TestDeviceNAME.set_function_instance(0);
    TestDeviceNAME.set_device_class_instance(0);
    TestDeviceNAME.set_manufacturer_code(1407);
    auto TestInternalECU = isobus::CANNetworkManager::CANNetwork.create_internal_control_function(TestDeviceNAME, 0);

    while (true)
    {
        // CAN stack runs in other threads. Do nothing forever.
        vTaskDelay(10);
    }

    isobus::CANHardwareInterface::stop();
}
```

이게 스택이 <strong>주소 클레임을 수행하고 메시지를 받을 준비를 마치기 위한 절대 최소한</strong>이다.

::: info 관련 스터디
NAME의 각 필드가 무슨 뜻인지, function code와 industry group을 어떻게 골라야 하는지는 [CH3. Control Function과 NAME](/study/agisostack/03-control-function-name)에서 다룬다. 주소 클레임 절차 자체는 [ISOBUS CH10. J1939 주소 관리](/study/isobus/10-j1939-address)를 참고하면 된다.
:::

### ESP32의 OS·PThread 옵션 조정

앞서 본 것처럼 AgIsoStack은 꽤 크고 멀티스레드로 도는 라이브러리다. 그래서 라이브러리가 매끄럽게 돌아가도록 플랫폼 설정을 몇 가지 조정해야 한다. <strong>이걸 안 하면 런타임에 장치가 계속 크래시할 가능성이 높다.</strong> 구체적으로는 기본 스택 크기와 pthreads 태스크에 할당되는 스택 양을 조정해야 한다.

PlatformIO에서 `menuconfig`를 실행한다. `pio run -t menuconfig`를 직접 돌리거나, PlatformIO 확장의 프로젝트 태스크 목록에서 "Platform → Run Menuconfig"를 고르면 된다.

::: warning menuconfig 실행 에러
`menuconfig` 실행 중 에러가 난다면, `src/` 폴더 안의 `CMakeLists.txt` 파일에 아래 줄이 있는 경우 주석 처리해야 할 수 있다. menuconfig가 끝나면 <strong>반드시 주석을 다시 풀어라</strong>.

```cmake
target_add_binary_data(${COMPONENT_TARGET} "object_pool/object_pool.iop" BINARY)
```
:::

<strong>PThreads 스택 크기</strong>

menuconfig가 뜨면 `Component config -> PThreads`로 이동해서 pthreads의 스택 크기를 <strong>8192 바이트</strong>로 바꾼다. 이렇게 하면 스택이 메모리를 다 써 버리는 일을 막을 수 있다. 그래도 크래시가 계속되면 이 값을 더 키워야 할 수도 있다.

<strong>FreeRTOS 틱 레이트</strong>

마지막으로, FreeRTOS의 틱 레이트를 올리거나 <strong>또는</strong> 스택의 갱신 주기를 낮춰서 둘을 맞춰 줘야 한다.

FreeRTOS 틱 레이트를 올리려면 `Component config -> FreeRTOS -> Kernel`로 이동해 `configTICK_RATE_HZ`를 설정한다. 스택의 갱신 주기(기본 4 ms)와 맞추는 것이 권장된다. 따라서 `configTICK_RATE_HZ`로는 <strong>250Hz</strong>가 좋은 값이다.

반대로 스택의 갱신 주기를 낮추려면 init/main 함수에서 원하는 값으로 설정하면 된다. 10 ms 갱신 주기를 원한다면 이렇게 쓴다.

```cpp
isobus::CANHardwareInterface::set_can_driver_update_period(10)
```

이 값은 ESP32의 기본 FreeRTOS 틱 레이트인 100Hz와 맞아떨어진다.

| 방향 | 설정 | 값 |
| --- | --- | --- |
| FreeRTOS를 스택에 맞추기 | `Component config -> FreeRTOS -> Kernel`의 `configTICK_RATE_HZ` | 250Hz (스택 기본 4 ms) |
| 스택을 FreeRTOS에 맞추기 | `set_can_driver_update_period(10)` | 10 ms (기본 틱 100Hz) |

::: tip 왜 틱 레이트를 맞춰야 하나
FreeRTOS의 지연·대기 함수는 틱 단위로 동작한다. 기본 틱이 100Hz(10 ms)인데 스택이 4 ms마다 깨어나려 하면, 요청한 주기를 시스템이 표현할 수 없다. 결과적으로 주기가 들쭉날쭉해지고 스택의 타이밍 기반 로직(주소 클레임 타임아웃, 전송 계층 타임아웃)이 어긋난다. 둘 중 어느 쪽을 맞추든 상관없지만, <strong>맞추기는 해야 한다</strong>.
:::

### 마무리

1. 키보드에서 `Q`를 눌러 menuconfig를 닫고, 이어서 `Y`를 눌러 변경 사항을 저장한다.
2. 애플리케이션 코드를 추가하고 PlatformIO 확장으로 프로젝트를 빌드한다.

여기까지가 끝이다. 이제 ESP32에서 돌아가는 AgIsoStack 프로젝트가 생겼다.

여기까지 왔는데 라이브러리로 실제 동작하는 애플리케이션을 어떻게 만드는지 모르겠거나 컴파일에 애를 먹고 있다면, 다음 절의 VT 클라이언트 예제를 확인하고 다른 튜토리얼도 읽어 보는 게 좋다.

## VT 클라이언트 예제

최소한이지만 인터랙티브하게 동작하는, ISOBUS 오브젝트 풀을 버추얼 터미널 디스플레이에 올리는 프로젝트를 빌드해 돌려 보려면 [GitHub 저장소](https://github.com/Open-Agriculture/AgIsoStack-plus-plus/tree/main/examples/virtual_terminal)에서 ESP32 PlatformIO 예제를 내려받아, 앞서 만든 것과 같은 빈 PlatformIO 프로젝트에 ESP32 프로젝트의 파일을 전부 복사해 넣으면 된다.

::: warning 예제를 쓸 때 확인할 것
- 이 예제는 TWAI 인터페이스를 GPIO 21과 22에서 돌리도록 설정한다. 외부 CAN 컨트롤러는 필요 없지만, <strong>CAN 트랜시버는 필요하다</strong>.
- 예제의 `platformio.ini`는 WROOM/Denky-32 보드용으로 설정돼 있다. 보드가 다르면 맞게 수정해야 한다.
:::

::: details 오브젝트 풀 같은 바이너리 파일을 펌웨어에 심는 법
오브젝트 풀처럼 바이너리 파일을 프로젝트에 임베드하려면 `CMakeLists.txt`에서 `target_add_binary_data` 함수를 쓴다.

```cmake
target_add_binary_data(${COMPONENT_TARGET} "object_pool/object_pool.iop" BINARY)
```

여기에 더해 `platformio.ini`에서 `board_build.embed_txtfiles` 아래에 해당 파일을 지정해야 오브젝트 풀이 바이너리에 임베드된다.

ESP32와 PlatformIO 조합에서 파일을 임베드하는 자세한 방법은 PlatformIO의 [바이너리 데이터 임베딩 문서](https://docs.platformio.org/en/latest/platforms/espressif32.html#embedding-binary-data)를 참고하면 된다.
:::

::: info 관련 스터디
오브젝트 풀이 무엇이고 어떻게 만드는지는 [ISOBUS CH16. VT 오브젝트 풀](/study/isobus/16-vt-object-pool)에서, VT 클라이언트를 코드로 다루는 법은 [CH13. Virtual Terminal 클라이언트](/study/agisostack/13-virtual-terminal)에서 다룬다.
:::

### 배선

예제에서는 GPIO 21과 22로 CAN 트랜시버를 구동한다. 이 구성으로 ESP32, CAN 트랜시버, 버스를 연결하면 다음과 같은 모양이 된다.

![ESP32 CAN 배선](/images/study-agisostack/18-esp32-wiring-light.png)
![ESP32 CAN 배선](/images/study-agisostack/18-esp32-wiring-dark.png)

| ESP32 | CAN 트랜시버 | 비고 |
| --- | --- | --- |
| GPIO 21 | CTX (TX 입력) | TWAI 송신 |
| GPIO 22 | CRX (RX 출력) | TWAI 수신 |
| 3V3 | VCC | SN65HVD230은 3.3V 동작 |
| GND | GND | 공통 접지 |

트랜시버의 CANH·CANL은 버스 커넥터로 나간다. 공식 예제 사진에서는 <strong>Deutsch DT 4-way 플러그</strong>로 CAN 버스에 연결하지만, 같은 일을 여러 표준 ISOBUS 커넥터로도 할 수 있다. 예를 들어 <strong>ISOBUS 진단 커넥터</strong>를 작업기 버스(implement bus) 쪽 핀만 결선해서 쓰는 방식도 가능하다.

::: warning 종단 저항
CAN 버스는 양 끝에 120Ω 종단 저항이 필요하다. 트랙터의 ISOBUS 버스에 물릴 때는 이미 종단이 되어 있는 경우가 많으므로, 트랜시버 보드에 달린 종단 저항 점퍼를 그대로 두면 버스 임피던스가 어긋난다. 벤치에서 단둘이 테스트할 때는 양쪽 종단이 필요하고, 실제 버스에 물릴 때는 보드의 종단을 떼는 게 보통이다.
:::

::: info 관련 스터디
차동 신호, 종단 저항, 버스 길이 제한 같은 물리 계층 얘기는 [ISOBUS CH3. CAN 물리 계층](/study/isobus/03-can-physical)에서 자세히 다룬다.
:::

### 빌드와 실행

예제 파일을 전부 프로젝트에 복사하고, 사용하는 보드에 맞게 설정하고, 장치를 제대로 연결했다면 PlatformIO로 프로젝트를 빌드하고 ESP32에 플래시한다.

모든 게 제대로 설정돼 있다면, 프로그래밍이 끝나는 즉시 ESP32가 예제 오브젝트 풀을 ISOBUS 디스플레이에 자동으로 올린다. 디스플레이 화면에 예제 풀의 화면이 뜨면 성공이다.

아무 일도 일어나지 않는다면 시리얼 모니터를 열어 애플리케이션에서 나오는 에러 메시지를 확인한다. 이 메시지들이 무슨 일이 일어나고 있는지 파악하는 데 도움이 된다.

::: details 아무것도 안 뜰 때 확인 순서
1. 시리얼 모니터(115200 bps)에 스택 로그가 나오는가. 안 나오면 `monitor_speed`와 보드 설정을 먼저 의심한다.
2. `canDriver->get_is_valid()`가 `true`인가. `false`면 TWAI 초기화 자체가 실패한 것이다. GPIO 번호와 트랜시버 전원을 확인한다.
3. 주소 클레임 로그가 보이는가. 안 보이면 버스에 프레임이 전혀 나가지 않는 것이다 — 배선(CANH/CANL 뒤바뀜), 종단 저항, 보 레이트(250 kbit/s)를 확인한다.
4. 주소 클레임은 되는데 VT를 못 찾는다면, 디스플레이가 실제로 같은 버스에 있는지, VT 클라이언트가 파트너를 어떤 조건으로 찾는지 확인한다.
5. 크래시가 반복된다면 PThreads 스택 크기(8192)와 틱 레이트 설정을 다시 본다. 이 두 가지가 ESP32에서 가장 흔한 크래시 원인이다.
:::

::: info 관련 스터디
빌드가 안 될 때 CMake·의존성 쪽 문제를 푸는 방법은 [CH6. 개발자 가이드](/study/agisostack/06-developer-guide), 로그 출력 설정은 [CH12. 디버그 로깅](/study/agisostack/12-debug-logging)을 참고하면 된다.
:::

## 기본을 넘어서

VT 예제를 고쳐서 나만의 VT 애플리케이션을 돌리려면 `object_pool.iop` 파일을 내 ISOBUS 오브젝트 풀로 교체하고, 그 풀 안의 입출력을 처리하도록 예제를 수정해야 한다. 방법은 [CH13. Virtual Terminal 클라이언트](/study/agisostack/13-virtual-terminal)에서 다룬다.

AgIsoStack에는 ESP32에서 자기만의 ISOBUS 애플리케이션을 개발하기 쉽게 해 주는 인터페이스가 이 밖에도 많다.

- 차량 가이던스와 속도 메시징
- 작업기 섹션 컨트롤과 처방도(prescription map)를 위한 ISO11783-10 Task Controller 클라이언트
- ISOBUS Shortcut Button (ISB)
- 표준 ISOBUS 진단

라이브러리의 여러 헤더 파일을 시간을 들여 훑어보면서 관심 있는 프로토콜과 기술을 찾아보길 권한다.

튜토리얼이 더 필요하거나 이 튜토리얼에 대한 피드백이 있다면 [GitHub 페이지](https://github.com/Open-Agriculture/AgIsoStack-plus-plus)를 방문해 논의를 열거나 기존 논의에 참여하면 된다.

::: tip 핵심 정리
- ESP32에는 클래식 CAN 2.0 컨트롤러(TWAI)가 내장돼 있어 외부 CAN 컨트롤러 없이 ISOBUS 노드를 만들 수 있다. 단 <strong>CAN 트랜시버는 반드시 필요하다</strong>.
- PlatformIO 프로젝트는 framework를 `espidf`로 만들고, `main.c`를 `main.cpp`로 바꾼 뒤 `extern "C" void app_main()`으로 선언해야 링커 에러가 안 난다.
- `lib_deps = https://github.com/Open-Agriculture/AgIsoStack-plus-plus.git` 한 줄로 라이브러리가 붙는다. 자동 갱신은 안 되므로 `pio pkg update`를 가끔 돌려야 한다.
- TWAI는 `TWAI_GENERAL_CONFIG_DEFAULT(GPIO_NUM_21, GPIO_NUM_22, TWAI_MODE_NORMAL)`, `TWAI_TIMING_CONFIG_250KBITS()`, `TWAI_FILTER_CONFIG_ACCEPT_ALL()` 조합으로 설정하고 `TWAIPlugin`에 넘긴다.
- menuconfig에서 PThreads 스택을 8192 바이트로 올리고, `configTICK_RATE_HZ`를 250Hz로 맞추거나 `set_can_driver_update_period(10)`으로 스택 주기를 10 ms로 내려 둘을 맞춘다. 안 하면 런타임에 반복 크래시한다.
- 오브젝트 풀 같은 바이너리는 `target_add_binary_data`와 `board_build.embed_txtfiles`로 펌웨어에 임베드한다.
:::

## 원문 출처
이 챕터는 AgIsoStack++ 공식 문서 [Using ESP32 and PlatformIO](https://isobus-plus-plus.readthedocs.io/en/latest/Tutorials/ESP32%20PlatformIO.html)의 내용을 한국어 학습 자료로 재구성한 것이다. 원문의 스크린샷은 텍스트 설명과 다이어그램으로 대체했다. 원문과 라이브러리는 MIT 라이선스로 배포된다.

## 다음 챕터
[CH19. API 구조 훑어보기](/study/agisostack/19-api-reference)로 이어진다.
