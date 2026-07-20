---
title: "개발자 가이드"
description: "AgIsoStack++ 저장소를 클론해 빌드하고, CAN 드라이버를 CMake 옵션으로 고르고, ctest로 테스트와 예제를 돌리고, Doxygen 문서를 만들고, 기여 규칙에 맞춰 PR을 올리기까지의 전 과정을 다룬다."
date: 2026-07-20
tags: [AgIsoStack, ISOBUS, CMake]
---

# 개발자 가이드

## 학습 목표
- 저장소를 클론해서 CMake로 구성하고 빌드하는 기본 흐름을 익힌다.
- `CAN_DRIVER` 변수로 사용할 CAN 드라이버 플러그인을 지정하는 방법과 지원 목록을 안다.
- `BUILD_TESTING`, `BUILD_EXAMPLES` 옵션을 켜서 테스트와 예제를 실행한다.
- Doxygen 내부 API 문서를 온라인으로 보거나 로컬에서 직접 생성한다.
- 기여 가이드의 코딩 스타일과 PR 통과 조건을 파악한다.

## 1. 사전 준비물

작업을 시작하기 전에 아래 세 가지가 시스템에 설치되어 있어야 한다. 자세한 설치 방법은 [CH5. 설치와 프로젝트 통합](/study/agisostack/05-installation)의 환경 셋업 절에 있다.

- Git
- CMake
- C++ 컴파일러

![개발자 워크플로](/images/study-agisostack/06-build-flow-light.png)
![개발자 워크플로](/images/study-agisostack/06-build-flow-dark.png)

전체 흐름은 clone → configure → build 세 단계이고, 테스트·예제·CAN 드라이버 선택은 모두 <strong>configure 단계에서 주는 CMake 옵션</strong>으로 갈린다. Doxygen 문서 생성만 이 빌드 파이프라인과 무관하게 소스 트리에서 직접 돌아간다.

## 2. 프로젝트 다운로드

프로젝트를 내려받는 절차는 다음과 같다.

1. 터미널이나 명령 프롬프트를 연다.
2. 프로젝트를 내려받을 디렉터리로 이동한다.
3. 아래 명령으로 저장소를 클론한다.

```bash
git clone https://github.com/Open-Agriculture/AgIsoStack-plus-plus.git
```

이 명령이 프로젝트 저장소를 `agisostack-plus-plus`라는 이름의 디렉터리로 클론한다.

::: info CH5의 통합 방식과의 관계
여기서 하는 클론은 <strong>라이브러리 자체를 개발·테스트·기여하기 위한</strong> 다운로드다. 내 애플리케이션에 라이브러리를 끼워 넣는 것이 목적이라면 CH5의 Git 서브모듈이나 FetchContent 쪽을 쓰는 편이 낫다.
:::

## 3. 프로젝트 빌드

빌드는 세 단계다.

1. 프로젝트 디렉터리로 이동한다.

```bash
cd agisostack-plus-plus
```

2. `build`라는 이름의 빌드 디렉터리를 만든다.

```bash
cmake -S . -B build
```

3. 프로젝트를 빌드한다.

```bash
cmake --build build
```

`cmake -S . -B build`는 소스 디렉터리(`-S .`)와 빌드 디렉터리(`-B build`)를 지정해 구성만 수행하는 명령이다. 실제 컴파일은 `cmake --build build`에서 일어난다. 이 둘을 분리해 두면 옵션을 바꿔 재구성할 때 어디서 무엇이 결정되는지가 분명해진다. 뒤에 나오는 `-D...` 옵션은 전부 첫 번째 명령, 즉 구성 단계에 붙는다.

이 단계까지 마치면 이 프로젝트의 핵심인 정적 라이브러리들이 컴파일된다.

## 4. CAN 드라이버 선택

이 라이브러리는 SocketCAN이나 PEAK 같은 널리 쓰이는 CAN 인터페이스용 하드웨어 통합을 내장하고 있다.

CMake로 컴파일할 때 <strong>OS에 따라 기본 CAN 드라이버 플러그인이 자동으로 선택</strong>된다. 하지만 컴파일 시 `CAN_DRIVER` 변수를 주면 기본적으로 지원되는 드라이버 중 하나를 명시적으로 고를 수 있다.

- `-DCAN_DRIVER=SocketCAN` — Socket CAN 지원 (Linux 기본값)
- `-DCAN_DRIVER=WindowsPCANBasic` — Windows PEAK PCAN 드라이버 (Windows 기본값)
- `-DCAN_DRIVER=MacCANPCAN` — MacCAN PEAK PCAN 드라이버 (Mac OS 기본값)
- `-DCAN_DRIVER=TWAI` — ESP TWAI 드라이버 (ESP32에서 선호되는 드라이버)
- `-DCAN_DRIVER=MCP2515` — MCP2515 CAN 컨트롤러
- `-DCAN_DRIVER=WindowsInnoMakerUSB2CAN` — InnoMaker USB2CAN 어댑터 (Windows)
- `-DCAN_DRIVER=TouCAN` — Rusoku TouCAN (Windows)
- `-DCAN_DRIVER=SYS_TEC` — SYS TEC sysWORXX USB CAN 어댑터 (Windows)
- `-DCAN_DRIVER=NTCAN` — NTCAN 드라이버 (Windows)

여러 개를 한꺼번에 쓰고 싶으면 세미콜론으로 구분한 리스트를 준다.

```bash
cmake -S . -B build -DCAN_DRIVER="<driver1>;<driver2>"
```

목표 하드웨어가 위 목록에 없어도 방법이 있다. 함수 몇 개만 구현하면 자신의 하드웨어를 어렵지 않게 통합할 수 있다. 새 CAN 드라이버는 `CANHardwarePlugin`을 상속받아 거기 정의된 함수들을 구현하면 되고, 개수는 다섯 개뿐이다.

CMake 구성으로 포함된 CAN 드라이버들에 접근하려면 아래 헤더를 include 하면 된다.

```cpp
#include "isobus/hardware_integration/available_can_drivers.hpp"
```

::: tip 드라이버 선택은 구성 단계의 결정이다
CAN 드라이버는 런타임 설정이 아니라 <strong>빌드 구성 시점</strong>에 결정된다. 드라이버를 바꾸려면 `-DCAN_DRIVER=...`를 바꿔 다시 구성해야 한다. CH5에서 사전 컴파일 바이너리가 배포되지 않는 배경도 이것과 이어진다.
:::

## 5. 테스트 실행

테스트는 GTest로 작성되어 있고 ctest를 통해 호출한다. 라이브러리가 컴파일되면 빌드 디렉터리로 이동해 테스트를 실행한다.

```bash
cmake -S . -B build -DBUILD_TESTING=ON
cmake --build build
cd build
ctest
```

이 명령이 프로젝트의 모든 테스트를 실행하고 결과를 출력한다.

::: info 옵션은 구성 단계에 붙는다
`-DBUILD_TESTING=ON`이 첫 줄, 즉 구성 명령에 붙어 있다는 점을 보라. 이미 `-DBUILD_TESTING` 없이 구성해 둔 빌드 디렉터리가 있다면, 같은 디렉터리에 옵션을 추가해 다시 구성하면 캐시가 갱신된다.
:::

## 6. 예제 실행

프로젝트에는 내장 예제들이 있다. <strong>기본적으로 예제는 빌드되지 않는다.</strong> 가장 쉬운 방법은 최상위에서 옵션을 켜고 빌드하는 것이다.

```bash
cmake -S . -B build -DBUILD_EXAMPLES=ON
cmake --build build
cd build
./examples/<example_name>
```

::: warning 예제 실행에는 실제 CAN 인터페이스가 필요하다
예제는 대부분 CAN 버스와 통신한다. Linux에서 SocketCAN을 쓴다면 `can0` 같은 인터페이스가 올라와 있어야 하고, Windows라면 PEAK 계열 하드웨어가 필요하다. 빌드가 성공했는데 실행이 곧바로 실패한다면 코드보다 CAN 인터페이스 상태를 먼저 의심해라.
:::

## 7. Doxygen 문서

이 프로젝트는 Doxygen을 사용해 최신 상태의 내부 API 문서를 자동 생성한다.

### 7-1. 사전 컴파일된 문서 보기

미리 컴파일된 최신 Doxygen 문서는 아래에서 볼 수 있다.

<https://delgrossoengineering.com/isobus-docs/index.html>

별도 설치 없이 브라우저만 있으면 되므로, 클래스 하나를 빠르게 찾아볼 때는 이쪽이 가장 빠르다.

### 7-2. 로컬에서 직접 생성하기

Doxygen을 직접 생성해 로컬에서 열람할 수도 있다. 내 프로젝트에서 `AgIsoStack-plus-plus` 폴더로 이동한다.

```bash
cd AgIsoStack-plus-plus
```

그리고 Doxygen이 설치되어 있는지 확인한다.

::: tabs
@tab Ubuntu
```bash
sudo apt install doxygen graphviz
```

@tab RHEL
```bash
sudo subscription-manager repos --enable codeready-builder-for-rhel-9-$(arch)-rpms

sudo dnf install doxygen graphviz
```

@tab Windows
Doxygen이 설치되어 있는지 확인한다: <https://www.doxygen.nl/download.html>
:::

그다음 문서를 생성한다.

```bash
doxygen doxyfile
```

문서는 `docs/html` 폴더에 생성된다. 그 안의 `index.html`을 웹 브라우저로 열면 문서를 둘러볼 수 있다.

::: info graphviz는 왜 같이 설치하나
graphviz는 Doxygen이 클래스 상속도나 호출 그래프 같은 다이어그램을 그릴 때 쓴다. 없어도 문서 생성 자체는 되지만 그림이 빠진다.
:::

## 8. 기여 가이드

프로젝트는 기여를 적극적으로 환영하고, 시작을 돕기 위한 가이드라인 문서를 두고 있다: [CONTRIBUTING.md](https://github.com/Open-Agriculture/AgIsoStack-plus-plus/blob/main/CONTRIBUTING.md)

기여의 범위는 새 기능 추가나 기존 코드 개선, 버그 수정만이 아니다. 테스트를 돕거나 문서를 다듬는 일도 포함된다.

![기여 절차](/images/study-agisostack/06-contributing-flow-light.png)
![기여 절차](/images/study-agisostack/06-contributing-flow-dark.png)

### 8-1. 수용 조건

행동 강령(Code of Conduct)을 지키는 모든 공개 기여를 받는다. PR에 대해서는 추가로 두 가지를 요구한다.

- 모든 자동 사전 머지 체크를 통과할 것
- 저장소 메인테이너의 수동 코드 리뷰를 받을 것

이는 높은 코드 품질과 프로젝트 표준을 유지하기 위한 장치다.

### 8-2. 코드 스타일 규칙

코드 스타일 규칙과 PR 리뷰는 Autosar의 `Guidelines for the use of the C++14 language in critical and safety-related systems`와 `MISRA C++` 권고를 느슨하게 기반으로 삼는다.

포맷은 저장소의 `.clang-format`, `.cmake-format` 파일에 정의된 스타일을 따라야 한다. PR을 올리기 전에 저장소 루트에서 아래를 실행하면 이 체크를 통과할 수 있다.

```bash
find . -iname *.hpp -o -iname *.cpp | xargs clang-format -i
find . -name CMakeLists.txt | xargs cmake-format -i
```

`docs/pre-commit-hook.sh`를 git pre-commit 훅으로 걸어 두는 것을 권장한다. 아래 한 줄이면 된다.

```bash
ln -s $PWD/docs/pre-commit-hook.sh $PWD/.git/hooks/pre-commit; chmod +x docs/pre-commit-hook.sh
```

코드 리뷰에서 확인하는 추가 스타일 요구 사항은 다음과 같다.

- 함수 이름은 `snake_case`
- 변수는 `camelCase`
- 상수 값은 `CAPITALIZED_SNAKE`
- `==`와 `!=` 비교에서 상수를 왼쪽에 둔다. `if (5 == value)`가 맞고 `if (value == 5)`는 틀렸다. 연산자에서 `=`를 하나 빠뜨려 런타임 버그가 생기는 것을 막기 위한 규칙이다.
- 모든 파일에 저작권 표기를 포함해야 한다.
- `nullptr`를 쓸 수 있는 자리에 `NULL`을 쓰지 않는다.
- `isobus` 네임스페이스 바깥의 네임스페이스, 특히 표준 라이브러리 `std::`에는 명시적 네임스페이스를 붙인다.
- 헤더 파일에서는 `using namespace` 지시자를 쓸 수 없다.
- 매개변수가 하나인 생성자는 `explicit`으로 표시한다.
- 클래스 멤버 변수를 수정하지 않는 함수에는 가능한 한 `const`를 붙인다.
- 컴파일 시점에 값이 결정되는 변수는 가능한 한 `constexpr`로 선언한다.
- 와이드 문자열 텍스트 안을 제외하면, C++ 언어 표준의 기본 소스 문자 집합에 지정된 문자만 소스 코드에 쓴다.
- 일반적으로 C보다 C++를 선호한다. 필요하면 예외가 허용될 수 있다.
- `CANStackLogger::warn/critical/error/info/debug` 메서드를 직접 호출하지 않고 `LOG_WARN/CRITICAL/ERROR/INFO/DEBUG` 매크로를 쓴다. 그러지 않으면 CAN 로거를 비활성화한 빌드가 실패한다.
- 이 목록이 전부는 아니며, 인클루드 가드 같은 모범 사례도 PR 리뷰에서 확인된다.

### 8-3. 그 밖의 통과 조건

- 프로젝트 루트에서 `doxygen doxyfile`을 실행했을 때 Doxygen이 경고 없이 컴파일되어야 한다.
- MIT보다 엄격한 라이선스의 코드, 또는 이 프로젝트 라이선스로 배포될 조건을 충족하지 못한 코드는 절대 추가할 수 없다.
- 컴파일 GitHub Action을 통과해야 한다.
- 최대한 넓은 "모던" 컴파일러 호환성을 위해 <strong>C++14에 존재하는 기능만</strong> 사용할 수 있다.
- 신규 코드에 대해 80% 코드 커버리지를 목표로 하되, 그 수치를 채우는 것보다 효과적이고 품질 좋은 테스트를 우선한다.

::: info 규칙이 많아 보여도
이 규칙들은 배제하거나 어렵게 만들려는 것이 아니다. 목표는 프로젝트의 코드 품질을 극대화하는 것 하나다. 첫 번째나 두 번째 PR에서 몇 가지를 놓쳐도 괜찮고, 메인테이너가 기준에 맞도록 도와준다.
:::

### 8-4. GUI 개발 환경 구성

Linux PC나 가상 머신을 개발 환경으로 꾸미는 것도 어렵지 않다. Ubuntu, Debian, RHEL, Raspbian을 권장하지만 다른 시스템도 동작할 수 있다. Windows 개발은 PEAK CAN 하드웨어 장치로 지원된다.

Linux에서 설치할 도구는 다음과 같다.

- git
- cmake
- build-essential (gcc와 g++, 또는 모던 CXX 컴파일러 아무거나)
- doxygen (선택)
- graphviz (선택)
- clang-format (선택)

IDE는 원하는 것을 쓰면 되고, 공식 가이드는 쉽다는 이유로 Visual Studio Code를 권한다. VS Code는 snap 스토어로 설치하거나 Microsoft에서 내려받을 수 있다. 저장소를 클론한 뒤 `File -> Open Folder`로 열고, C++ 확장 팩을 설치하고, "build" 버튼을 눌러 컴파일러를 선택하면 이 프로젝트의 핵심인 정적 라이브러리가 컴파일된다.

예제를 빌드하고 디버깅하려면 CMake Tools 확장 설정에서 구성 시점 인자로 `-DBUILD_EXAMPLES=ON`을 추가한 뒤 같은 "build" 버튼으로 다시 컴파일하면 된다. 그다음 디버거 실행 버튼을 눌러 디버깅할 타겟을 고르면 된다.

::: tip 핵심 정리
- 준비물은 Git·CMake·C++ 컴파일러 셋이고, 빌드는 `cmake -S . -B build` → `cmake --build build` 두 명령이 전부다.
- CAN 드라이버는 OS에 따라 기본값이 자동 선택되지만 `-DCAN_DRIVER=...`로 명시할 수 있고, 세미콜론 리스트로 여러 개를 함께 넣을 수 있다. 지원되지 않는 하드웨어는 `CANHardwarePlugin`을 상속해 함수 다섯 개만 구현하면 된다.
- 테스트는 `-DBUILD_TESTING=ON` 후 `ctest`, 예제는 `-DBUILD_EXAMPLES=ON` 후 `./examples/<example_name>`이다. 둘 다 기본적으로 꺼져 있다.
- Doxygen 문서는 온라인 사전 컴파일 버전을 보거나, `doxygen doxyfile`로 직접 생성해 `docs/html/index.html`을 열면 된다.
- 기여는 `.clang-format`·`.cmake-format` 준수, C++14 한정, 상수 좌측 비교 같은 스타일 규칙과 자동 체크 통과, 메인테이너 리뷰를 요구한다.
:::

## 참고 자료
- [AgIsoStack++ 공식 문서 — Developer Guide](https://isobus-plus-plus.readthedocs.io/en/latest/Developer%20Guide.html)
- [AgIsoStack++ 공식 문서 — HardwareInterface API (Choosing a CAN Driver with CMake)](https://isobus-plus-plus.readthedocs.io/en/latest/api/hardware/index.html)
- [AgIsoStack++ CONTRIBUTING.md](https://github.com/Open-Agriculture/AgIsoStack-plus-plus/blob/main/CONTRIBUTING.md)

## 다음 챕터
[CH7. ISOBUS Hello World](/study/agisostack/07-hello-world)로 이어진다.
