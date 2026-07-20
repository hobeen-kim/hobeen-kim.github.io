---
title: "Task Controller 클라이언트"
description: "TaskControllerClient로 작업기를 TC에 붙이는 전체 절차와, 값 요청·명령 콜백, 그리고 TC 서버 API 개요."
date: 2026-07-20
tags: [AgIsoStack, ISOBUS, TaskController, C++]
---

# Task Controller 클라이언트

## 학습 목표
- `TaskControllerClient`를 만들고 `configure`로 작업기 능력을 선언할 수 있다.
- 값 요청 콜백과 명령 콜백의 시그니처·반환값 규칙을 설명할 수 있다.
- `initialize`/`terminate`로 클라이언트 수명을 관리하고, `on_value_changed_trigger`로 값 송신을 촉발할 수 있다.
- `TaskControllerServer` 추상 API가 무엇을 대신해 주고, 어떤 가상 함수를 구현해야 하는지 설명할 수 있다.

## Task Controller 클라이언트 만들기

TC와 통신하려면 먼저 <strong>자기 작업기의 능력부터 파악</strong>해야 한다. 섹션은 몇 개까지 제어할 수 있는가? 동시에 처리할 수 있는 VRA(가변 살포량) 레이트는 몇 개인가? TC가 제공하는 위치 기반(GNSS) 제어 없이도 정상 동작할 수 있는가?

그다음, 작업기를 TC에 설명하는 <strong>DDOP를 만들어야 한다.</strong> 이 DDOP는 AgIsoStack이 TC에 접속할 때 업로드되어, 작업기가 무엇을 할 수 있는지 TC에 알린다. DDOP 만드는 법은 [CH14. Task Controller와 DDOP](/study/agisostack/14-tc-ddop)에서 다뤘고, [파종기 예제](https://github.com/Open-Agriculture/AgIsoStack-plus-plus/blob/main/examples/seeder_example/section_control_implement_sim.cpp#L98)도 좋은 참고 자료다.

이 질문들에 답하고 DDOP까지 준비했다면, `TaskControllerClient`를 만들고 작업기 능력에 맞게 구성하면 된다.

![TC 클라이언트 구성과 런타임 콜백](/images/study-agisostack/15-tc-client-flow-light.png)
![TC 클라이언트 구성과 런타임 콜백](/images/study-agisostack/15-tc-client-flow-dark.png)

### 생성과 구성

```cpp
#include "isobus/isobus/isobus_task_controller_client.hpp"

// Create a TaskControllerClient
// The parameters are, in order:
// The control function for the TC
// The control function used to send messages to the TC
// The control function for a virtual terminal you're connected to with the VT client (optional - helps synchronize language and units in some cases)
isobus::TaskControllerClient OurTaskControllerClient(PartnerTC, InternalECU, nullptr);

// Configure the TaskControllerClient with our DDOP.
// The parameters are, in order:
// Includes support for 1 boom, 10 sections, 1 rate
// Supports documentation, not supporting TC-GEO without position based control
// Supports TC-GEO with position based control, not supporting peer control
// Supports TC-SC section control
OurTaskControllerClient.configure(myDDOP, 1, 10, 1, true, false, true, false, true);
```

생성자 인자는 순서대로 이렇다.

- TC에 해당하는 제어 기능(파트너)
- TC로 메시지를 보낼 때 쓸 제어 기능(내부 ECU)
- VT 클라이언트로 접속 중인 가상 터미널의 제어 기능. 선택 사항이며, 경우에 따라 언어와 단위를 동기화하는 데 도움이 된다.

`configure`의 인자는 순서대로 이렇다.

- DDOP
- 붐 1개, 섹션 10개, 레이트 1개 지원
- documentation 지원, 위치 기반 제어 없는 TC-GEO는 미지원
- 위치 기반 제어가 있는 TC-GEO 지원, peer control 미지원
- TC-SC 섹션 제어 지원

### 값 요청 콜백

TC 클라이언트를 만들었으면, TC가 정보를 요청할 때와 무언가를 명령할 때 어떻게 할지 함수를 정의해야 한다. 먼저 요청 처리 함수다.

```cpp
bool request_value_command_callback(std::uint16_t elementNumber,
                                    std::uint16_t DDI,
                                    std::int32_t &value,
                                    void *parentPointer)
{

}
```

이 함수는 TC가 작업기에서 값을 요청할 때 TC 클라이언트가 호출한다. 요청된 값을 돌려주도록 내용을 채우면 된다. 보통은 DDI나 요소 번호로 `switch`를 돌려서, 작업기의 현재 동작에 맞는 값을 반환하는 형태가 된다.

TC가 유효한 DDI와 요소 번호를 줬고 그에 대한 값을 돌려줬다면 `true`를 반환한다. `false`를 반환하면 TC 클라이언트가 "요청한 값을 쓸 수 없다"는 에러 메시지를 TC로 보낸다. <strong>TC는 DDOP 안의 모든 DPD 값이 사용 가능하다고 기대하므로, 사실상 절대 `false`를 반환하면 안 된다.</strong>

구현 예시는 [파종기 예제](https://github.com/Open-Agriculture/AgIsoStack-plus-plus/blob/main/examples/seeder_example/section_control_implement_sim.cpp#L219)나 [TC 클라이언트 예제](https://github.com/Open-Agriculture/AgIsoStack-plus-plus/blob/main/examples/task_controller_client/section_control_implement_sim.cpp)를 참고하면 된다.

### 명령 콜백

다음은 명령 처리 함수다.

```cpp
bool command_value_command_callback(std::uint16_t elementNumber,
                                    std::uint16_t DDI,
                                    std::int32_t processVariableValue,
                                    void *parentPointer)
{

}
```

이 함수는 TC가 작업기에 명령을 보낼 때 TC 클라이언트가 호출한다. 명령을 처리하도록 내용을 채우면 된다. 여기서도 보통 DDI나 요소 번호로 `switch`를 돌려서 해당 값을 설정하는 형태가 된다.

TC가 유효한 DDI와 요소 번호를 줬고 명령을 성공적으로 실행했다면 `true`를 반환한다. `false`를 반환하면 TC 클라이언트가 "명령을 실행하지 못했다"는 에러 메시지를 TC로 보낸다. <strong>TC는 DDOP 안의 "settable" DPD 값이 모두 쓰기 가능하다고 기대하므로, 여기서도 사실상 절대 `false`를 반환하면 안 된다.</strong>

명령을 받았을 때, 명령이 수신·실행됐음을 확인하기 위해 값을 TC로 되돌려 보내야 하는 경우도 있다. 예를 들어 TC가 섹션을 켜라는 명령을 보내면 섹션을 켤 텐데, 그 섹션의 "Actual Condensed Work State"에 on-change 트리거가 걸려 있다면 바뀐 값을 TC로 보내야 한다.

이때, 그리고 사실상 <strong>TC로 값을 보내야 하는 모든 경우</strong>에 `TaskControllerClient` 객체의 `on_value_changed_trigger` 함수를 호출하면 된다. 그러면 인터페이스가 적절한 DDI와 요소 번호로 앞서 정의한 `request_value_command_callback`을 호출하고, 그 결과를 TC로 전송한다.

### 실행과 종료

마지막으로 TC 클라이언트를 돌리라고 지시한다. `initialize`를 호출하면 된다.

```cpp
OurTaskControllerClient.initialize(true); // The "true" parameter tells the TC client to start running in a separate thread. If you pass "false", the TC client will run in the same thread as your main program and you'll have to call `update` on it periodically.
```

`true`를 넘기면 TC 클라이언트가 별도 스레드에서 돈다. `false`를 넘기면 메인 프로그램과 같은 스레드에서 돌기 때문에 주기적으로 `update`를 직접 호출해야 한다.

이제 TC 클라이언트가 동작을 시작한다. TC로부터 오는 메시지를 처리하고, 필요할 때 `request_value_command_callback`과 `command_value_command_callback`을 호출한다. 모든 CAN 메시징은 대신 처리되므로, 프로세스 데이터 메시지를 손으로 보낼 일은 없다.

TC 클라이언트 사용을 마쳤으면 `terminate`를 호출해 동작을 멈춘다.

```cpp
OurTaskControllerClient.terminate();
```

## 그 외 유용한 기능

`TaskControllerClient` 객체에는 TC와 상호작용하는 함수가 이 밖에도 많다. 어떤 함수가 있는지는 [AgIsoStack 문서](https://delgrossoengineering.com/isobus-docs/isobus__task__controller__client_8hpp_source)에서 `TaskControllerClient` 클래스를 살펴보면 된다.

주요한 것 몇 가지는 다음과 같다.

- `reupload_device_descriptor_object_pool` — DDOP를 TC로 다시 업로드한다. TC 클라이언트가 이미 돌기 시작한 뒤에 DDOP를 바꿔야 할 때 유용하다.
- `request_task_controller_identification` — TC가 자기 "번호"를 화면에 표시하도록 요청한다(해당 기능이 있는 경우). 지금 어떤 TC에 붙어 있는지 눈으로 확인해야 할 때 유용하다.
- `get_is_connected` — TC 클라이언트가 TC에 연결돼 있으면 `true`, 아니면 `false`를 반환한다.
- `get_is_task_active` — TC가 현재 태스크를 수행 중이라고 표시하면 `true`, 아니면 `false`를 반환한다. 모든 TC가 이 값을 제대로 쓰는 것은 아니어서 항상 유용하지는 않다.

더 많은 사용법은 AgIsoStack의 예제들을 확인하면 된다.

## TC 서버 API 개요

Task Controller API는 클라이언트와 서버 양쪽으로 구성된다. VT와 마찬가지로 <strong>클라이언트가 서버가 예약한 태스크를 실행하는 쪽</strong>이다.

::: info Data Logger (DL)
Task Controller로 등록된 제어 기능이되 특별히 데이터 로깅 기능만 수행하도록 정의된 것을 <strong>Data Logger(DL)</strong>라고 부르는 경우가 많다.
:::

데이터 로깅, 매핑, 섹션 제어를 비롯한 흔한 ISOBUS 기능을 수행하는 태스크 컨트롤러 서버를 만드는 일은 매우 복잡한 작업이다. AgIsoStack++는 이 작업의 CAN 부분을 쉽게 만들어 주는 <strong>추상 서버 API</strong>를 제공한다. 가상 함수 몇 개만 구현하면 태스크 컨트롤러 서버를 만들 수 있고, CAN 통신의 대부분은 라이브러리가 처리한다.

제공하는 기능은 다음과 같다.

- TC-GEO, TC-SC, TC-BAS에 필요한 CAN 메시징 지원
- DDOP 전송을 대신 관리하고 클라이언트 접속 과정을 추상화해서, 애플리케이션 로직에 집중할 수 있게 한다
- ISO 11783-10의 TC 표준 버전 3과 4를 모두 지원
- TC 상태 메시지 관리
- 클라이언트 접속 상태와 타임아웃 추적
- Device Descriptor Object Pool 클래스와 잘 통합되어 제품·작업기 정보에 접근 가능
- 클라이언트로 명령을 보내고 값을 받는 단순한 인터페이스 제공
- DDOP 파싱 헬퍼 포함. 많은 코드를 짜지 않아도 작업기 기하 정보와 제품 정보를 빠르게 알 수 있다
- 클라이언트에게 필요한 모든 응답을 대신 전송하므로, 메시지를 직접 채울 필요가 없다

TC 서버를 동작시키려면 다음 함수들을 구현해야 한다. 순서는 상관없다.

- `activate_object_pool`
    - 유효하게 연결된 클라이언트가 자신이 마지막으로 업로드한 DDOP를 활성화해 달라고 요청하면 서버가 호출한다.
    - 이때 DDOP를 파싱해야 한다. (`store_device_descriptor_object_pool` 호출로 이전에 받아 둔 것이 있다면) [DDOP 클래스](https://github.com/Open-Agriculture/AgIsoStack-plus-plus/blob/main/isobus/include/isobus/isobus/isobus_device_descriptor_object_pool.hpp)를 활용할 수 있다.
    - 그런 다음 애플리케이션이 새 DDOP를 사용하도록 필요한 처리를 해서 DDOP를 "활성화"한다. 구체적인 방법은 태스크 컨트롤러 애플리케이션마다 다르다.
    - DDOP가 유효하고 활성화됐으면 `true`, 유효하지 않으면 `false`를 반환한다.
    - `false`를 반환한다면 DDOP가 유효하지 않은 이유를 에러 파라미터에 채워야 한다.
- `change_designator`
    - 유효하게 연결된 클라이언트가 DDOP 안의 무언가의 designator를 바꿔 달라고 요청하면 서버가 호출한다.
    - DDOP의 언어를 바꾸거나, 작업기 이름을 바꾸거나, 표시되는 제품명을 바꾸는 흔한 방법이다.
    - 오브젝트의 designator를 바꾸고 성공 여부를 반환하도록 구현한다.
- `deactivate_object_pool`
    - 유효하게 연결된 클라이언트가 현재 활성화된 DDOP를 비활성화해 달라고 요청하면 서버가 호출한다.
    - 애플리케이션이 그 DDOP 사용을 멈추도록 필요한 처리를 한다. 구체적인 방법은 애플리케이션마다 다르다.
    - 비활성화됐으면 `true`, 아니면 `false`를 반환한다. `false`라면 실패 이유를 에러 파라미터에 채워야 한다.
- `get_is_stored_device_descriptor_object_pool_by_structure_label`
    - 클라이언트 접속 과정에는, 클라이언트가 특정 구조 라벨을 가진 DDOP를 (자신의 NAME과 연관지어) 서버가 이미 갖고 있는지 묻는 단계가 있다.
    - 해당 클라이언트 NAME에 대해 그 구조 라벨의 DDOP를 비휘발성 메모리에 이미 저장하고 있으면 `true`, 아니면 `false`를 반환한다.
    - 구조 라벨은 항상 7바이트다. 확장 구조 라벨은 선택 사항이며 비어 있거나 최대 32바이트일 수 있다.
    - `true`를 반환하려면 <strong>두 라벨이 정확히 일치</strong>해야 한다. 확장 라벨이 제공되지 않았다면 무시해도 된다.
    - 보통 TC는 최신 DDOP 하나만 저장해야 하며, 같은 구조 라벨의 DDOP를 여러 개 저장해서는 안 된다.
- `get_is_stored_device_descriptor_object_pool_by_localization_label`
    - 마찬가지로 클라이언트가 특정 로컬라이제이션 라벨을 가진 DDOP를 서버가 이미 갖고 있는지 묻는 단계가 있다.
    - 로컬라이제이션 라벨은 DDOP의 단위·언어·국가를 서술한다.
    - 해당 클라이언트 NAME에 대해 그 라벨의 DDOP를 비휘발성 메모리에 저장하고 있으면 `true`, 아니면 `false`를 반환한다.
    - 로컬라이제이션 라벨은 항상 7바이트다.
    - 보통 TC는 같은 로컬라이제이션 라벨의 DDOP를 여러 개 저장하지 않고 최신 것 하나만 저장해야 한다.
- `get_is_enough_memory_available`
    - 클라이언트가 전송하려는 DDOP를 저장할 메모리(RAM과 ROM 모두)가 서버에 충분한지 판단할 때 호출된다.
    - 일반적으로 저장할 메모리가 충분하면 `true`, 아니면 `false`를 반환한다.
    - `true`의 의미는 "메모리가 충분할 수도 있다. 다만 오브젝트 저장에는 오버헤드가 있으므로 충분한지 예측하기란 불가능하다"이고, `false`의 의미는 "메모리가 부족하다. DDOP를 전송하지 마라"이다.
- `identify_task_controller`
    - 누군가 TC에게 스스로를 식별하라고 요청하면 호출된다. 호출되면 TC에 시각적 인터페이스가 있는 경우 <strong>TC 번호를 3초간 표시</strong>해야 한다.
- `on_client_timeout`
    - 연결된 클라이언트가 타임아웃되면 서버가 호출한다.
    - 타임아웃 시 하고 싶은 처리를 구현한다. 보통 해당 클라이언트의 DDOP도 함께 비활성화하게 된다.
- `on_process_data_acknowledge`
    - 클라이언트가, 자신에게 보낸 프로세스 데이터 명령에 대한 확인 응답(acknowledgement)을 보내면 서버가 호출한다.
    - `set_value_and_acknowledge` 함수를 쓸 때, 마지막으로 보낸 명령을 클라이언트가 받았는지 알아내는 데 유용하다.
- `on_value_command`
    - 클라이언트가 TC로 값 명령을 보내면 서버가 호출한다. <strong>클라이언트가 데이터를 제공하는 주된 통로</strong>다.
    - 값 명령이 왔을 때 하고 싶은 처리를 구현한다. 프로그램에 값을 설정하는 것부터 파일에 로깅, 지도에 그리기, 연결된 작업기에 명령 보내기까지 무엇이든 될 수 있다.
    - 클라이언트가 섹션 상태가 바뀌었다거나 붐 위치가 바뀌었다고 알려주는 통로이므로, TC를 "동작하게" 만들려면 아마 가장 중요한 함수다. 파라미터의 의미는 [ISOBUS 데이터 딕셔너리](https://www.isobus.net/isobus/)로 확인한다.
- `store_device_descriptor_object_pool`
    - 서버가 DDOP를 비휘발성 메모리(NVM)에 저장하기를 원할 때 호출된다.
    - DDOP를 NVM에 저장하도록 구현한다.
    - `appendToPool`이 `true`이면 NVM에 있는 기존 DDOP에 <strong>이어붙여야</strong> 한다. 클라이언트는 DDOP를 여러 조각으로 나눠 보낼 수 있으므로 이 처리를 정확히 하는 것이 필수다.

::: tip 핵심 정리
- `TaskControllerClient(PartnerTC, InternalECU, VTClientCF)`로 만들고, `configure(DDOP, 붐 수, 섹션 수, 레이트 수, 지원 플래그 5종)`으로 능력을 선언한다.
- 값 요청은 `request_value_command_callback(elementNumber, DDI, &value, parentPointer)`, 명령은 `command_value_command_callback(elementNumber, DDI, processVariableValue, parentPointer)`로 받는다. 둘 다 사실상 항상 `true`를 반환해야 한다.
- `on_value_changed_trigger`가 TC로 값을 보내는 통로다. 내부적으로 요청 콜백을 호출해 값을 얻어 전송한다.
- `initialize(true)`는 별도 스레드, `initialize(false)`는 직접 `update` 호출. 종료는 `terminate`.
- TC 서버는 `TaskControllerServer` 추상 클래스의 가상 함수를 구현하는 방식이다. 그중 `on_value_command`가 클라이언트 데이터를 받는 핵심이고, `store_device_descriptor_object_pool`의 `appendToPool` 처리가 특히 중요하다.
:::

## 원문 출처
- [AgIsoStack++ Docs — Task Controller Client](https://isobus-plus-plus.readthedocs.io/en/latest/Tutorials/Task%20Controller%20Client.html) (MIT License)
- [AgIsoStack++ Docs — Task Controller API (Client / Server)](https://isobus-plus-plus.readthedocs.io/en/latest/api/task%20controller/index.html)

## 다음 챕터
[CH16. 작업기 메시지와 ISB](/study/agisostack/16-implement-messages)로 이어진다.
