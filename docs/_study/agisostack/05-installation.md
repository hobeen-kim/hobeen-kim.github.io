---
title: "설치와 프로젝트 통합"
description: "AgIsoStack++가 공식 지원하는 플랫폼과 환경 준비 방법, 그리고 Git Submodule·CMake FetchContent·사전 컴파일 배포라는 세 가지 통합 경로의 실제 코드와 선택 기준을 다룬다."
date: 2026-07-20
tags: [AgIsoStack, ISOBUS, CMake]
---

# 설치와 프로젝트 통합

## 학습 목표
- AgIsoStack++가 공식적으로 지원하는 플랫폼과 지원하지 않는 환경을 구분한다.
- Linux와 Windows에서 스택을 내려받아 컴파일하기 위한 최소 도구 체인을 갖춘다.
- Git Submodule, CMake FetchContent, 사전 컴파일 배포 세 가지 통합 방식의 실제 코드와 차이를 안다.
- `isobus::` ALIAS 타겟을 이용해 내 실행 파일에 스택을 링크하는 방법을 익힌다.
- 프로젝트 상황에 맞는 통합 방식을 근거를 갖고 고른다.

## 1. 공식 지원 플랫폼

AgIsoStack++는 <strong>소스에서 빌드하는 것</strong>을 전제로 만들어졌고, 아래 플랫폼에서의 소스 빌드를 공식 지원한다.

- Ubuntu Linux (WSL 제외)
- Raspberry Pi OS (Raspbian)
- RHEL
- Windows
- MacOS
- ESP32

![공식 지원 플랫폼과 기본 CAN 드라이버](/images/study-agisostack/05-supported-platforms-light.png)
![공식 지원 플랫폼과 기본 CAN 드라이버](/images/study-agisostack/05-supported-platforms-dark.png)

이 목록에 없는 플랫폼에서도 동작할 가능성은 충분히 있다. 스택 자체가 서로 다른 하드웨어를 수용하도록 설계되어 있기 때문이다. 다만 위 목록에 있는 플랫폼이 <strong>공식 지원 대상</strong>이고, 문제가 생겼을 때 가장 좋은 지원을 받을 수 있는 환경이다. 수요가 있으면 지원 플랫폼은 추가될 수 있다.

::: warning WSL은 지원하지 않는다
WSL은 지원 대상이 아니다. WSL 커널이 기본적으로 SocketCAN을 지원하지 않기 때문이다. WSL 커널을 SocketCAN 지원이 들어가도록 재컴파일하면 동작시킬 여지가 있지만, 그 사용 사례는 공식적으로 지원하지 않는다.

Ubuntu Linux를 쓴다고 적혀 있어도 "WSL 위의 Ubuntu"는 여기에 해당하지 않는다는 점을 헷갈리지 마라.
:::

또 하나 중요한 전제가 있다. <strong>현재 지원되는 통합 방법은 소스 빌드가 유일하다.</strong> 뒤에서 다룰 세 가지 방식 중 사전 컴파일 배포가 사실상 선택지에서 빠지는 이유가 여기에 있다.

## 2. 환경 셋업

스택을 내려받고 컴파일하려면 도구가 몇 개 필요하다. 요구 사항 자체는 상당히 기본적이라, 이미 갖춰져 있을 가능성이 높다.

::: tabs
@tab Linux
```bash
sudo apt install build-essential cmake git
```

`build-essential`이 gcc/g++를 포함한 컴파일 도구 묶음이고, `cmake`가 빌드 구성기, `git`이 소스를 받아오는 도구다. 이 셋이면 스택을 컴파일할 수 있다.

@tab Windows
Windows에서는 패키지 매니저 한 줄로 끝나지 않고, 아래 세 가지를 각각 설치한다.

- [Build Tools for Visual Studio](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022) — MSVC 컴파일러와 빌드 도구
- [CMake](https://cmake.org/download/) — 빌드 구성기
- [Git](https://git-scm.com/download/win) — 소스 다운로드

Visual Studio IDE 전체가 아니라 "Build Tools"만으로도 충분하다.
:::

::: info Linux 배포판별 패키지 이름
위 명령은 `apt`를 쓰는 Debian 계열(Ubuntu, Raspberry Pi OS) 기준이다. RHEL 계열은 패키지 매니저와 이름이 다르므로 그에 맞는 방식으로 컴파일러·CMake·Git을 설치하면 된다.
:::

## 3. 통합 방식 세 가지

라이브러리를 내 프로젝트에 넣는 방법은 여러 가지다. 그중 가장 쉬운 길은 <strong>Git 서브모듈과 CMake의 조합</strong>이다.

![프로젝트 통합 방식](/images/study-agisostack/05-integration-methods-light.png)
![프로젝트 통합 방식](/images/study-agisostack/05-integration-methods-dark.png)

세 방식 모두 결국 도달하는 지점은 같다. `isobus::`로 시작하는 ALIAS 타겟을 내 실행 파일에 링크하는 것이다. 다른 것은 <strong>소스가 어디에서 어떻게 프로젝트에 들어오느냐</strong>다.

### 3-1. Git Submodule

라이브러리를 통합하려는 `CMakeLists.txt`가 있는 디렉터리에서 아래 명령을 실행한다.

```bash
git submodule add https://github.com/Open-Agriculture/AgIsoStack-plus-plus.git
git submodule update --init --recursive
```

이렇게 하면 프로젝트 안에 `AgIsoStack-plus-plus`라는 이름의 폴더가 생기고 그 안에 스택이 놓인다.

링크할 때는 노출된 <strong>ALIAS 타겟</strong>을 쓰는 것이 권장된다. ALIAS 타겟은 전부 `isobus::<target_name>` 형태의 이름을 따른다.

```cmake
find_package(Threads)

add_subdirectory(<path to this submodule>)

target_link_libraries(<your executable name> PRIVATE isobus::Isobus isobus::HardwareIntegration isobus::Utility Threads::Threads)
```

`find_package(Threads)`가 먼저 오는 이유는, 스택이 수신 스레드와 주기 스레드를 돌리기 때문에 스레드 라이브러리를 함께 링크해야 하기 때문이다. 그래서 링크 목록 마지막에 `Threads::Threads`가 붙는다.

전체 `CMakeLists.txt` 예제는 다음 챕터에서 다룰 첫 튜토리얼(ISOBUS Hello World) 말미에서 볼 수 있다.

스택을 최신 버전으로 올리고 싶을 때는 아래 명령을 쓴다.

```bash
git submodule update --remote --merge
```

이 명령이 최신 버전의 스택을 프로젝트로 끌어온다.

::: tip 서브모듈 방식의 성격
소스가 내 저장소 트리 안에 실체로 존재한다. 그래서 스택 코드를 직접 열어 읽거나 디버거로 들어가기가 가장 편하고, 커밋 해시로 버전이 고정되므로 재현성도 좋다. 대신 저장소를 클론하는 쪽에서 `--recursive`를 빠뜨리면 빈 폴더만 받게 되는 함정이 있다.
:::

### 3-2. CMake FetchContent

Git 서브모듈을 쓰고 싶지 않다면, CMake의 FetchContent 모듈로 스택을 내려받을 수 있다.

```cmake
include(FetchContent)

FetchContent_Declare(
   AgIsoStack
   GIT_REPOSITORY https://github.com/Open-Agriculture/AgIsoStack-plus-plus.git
   GIT_TAG        main # Replace this with tag or commit hash for better stability
)
FetchContent_MakeAvailable(AgIsoStack)

# Somewhere later in your CMakeLists.txt
target_link_libraries(<your executable name> PRIVATE isobus::Isobus isobus::HardwareIntegration isobus::Utility Threads::Threads)
```

이제 CMake 캐시를 구성하는 시점에 라이브러리가 GitHub에서 받아지고 자동으로 프로젝트에서 사용할 수 있게 된다.

::: warning GIT_TAG는 브랜치 대신 태그나 커밋 해시로
공식 권장 사항은 브랜치가 아니라 <strong>특정 태그나 커밋 해시</strong>를 지정하는 것이다. 이유는 두 가지다.

- 프로젝트에 더 나은 안정성을 준다. 브랜치를 가리키면 상류의 변경이 내 빌드에 예고 없이 들어온다.
- 구성 시간이 빨라진다. 브랜치가 아니면 CMake가 프로젝트를 구성할 때마다 업데이트를 확인할 필요가 없다.

위 예제의 `main`은 그대로 쓰라는 값이 아니라 "여기를 태그나 커밋 해시로 바꿔라"라는 표시다.
:::

### 3-3. Precompiled

세 번째 선택지는 사전 컴파일된 바이너리를 쓰는 것이다. 결론부터 말하면 <strong>현재는 불가능하다.</strong>

AgIsoStack++는 이 라이브러리를 바이너리 형태(예: DLL 파일)로 공식 배포하지 않는다. 그래서 실제로 고를 수 있는 통합 방식은 앞의 두 가지뿐이고, 이 챕터 첫머리에서 말한 "소스 빌드가 유일한 지원 통합 방법"이라는 문장과 정확히 맞물린다.

::: info 왜 바이너리 배포가 없나
이 라이브러리는 CMake 옵션으로 CAN 드라이버 플러그인을 선택해서 빌드한다. 즉 같은 소스라도 SocketCAN용, PEAK PCAN용, ESP32 TWAI용 산출물이 서로 다르다. 대상 OS·컴파일러·CAN 하드웨어 조합의 수를 생각하면 의미 있는 바이너리 매트릭스를 배포하기가 쉽지 않다. CAN 드라이버 선택 옵션은 다음 챕터에서 자세히 본다.
:::

## 4. 통합 방식 선택 가이드

| 항목 | Git Submodule | CMake FetchContent | Precompiled |
| --- | --- | --- | --- |
| 사용 가능 여부 | 가능 (가장 쉬운 방법) | 가능 | 공식 배포 없음 |
| 소스 위치 | 내 저장소 트리 안 (`AgIsoStack-plus-plus/`) | CMake 구성 시점에 빌드 디렉터리로 다운로드 | 해당 없음 |
| CMake 연결 | `add_subdirectory(<서브모듈 경로>)` | `FetchContent_Declare` + `FetchContent_MakeAvailable` | 해당 없음 |
| 버전 고정 | 서브모듈 커밋 해시로 고정 | `GIT_TAG`에 태그·커밋 해시 지정 시 고정 | 해당 없음 |
| 업데이트 | `git submodule update --remote --merge` | `GIT_TAG` 값을 바꿔 재구성 | 해당 없음 |
| 클론 시 주의 | `--recursive` 누락 시 소스가 비어 있음 | 첫 구성 시 네트워크 필요 | 해당 없음 |
| 스택 코드 열람·디버깅 | 가장 편함 | 가능하지만 빌드 디렉터리 안에 있음 | 해당 없음 |
| 링크 타겟 | `isobus::Isobus` `isobus::HardwareIntegration` `isobus::Utility` `Threads::Threads` | 동일 | 해당 없음 |

정리하면 선택 기준은 단순하다.

- 스택 코드를 자주 들여다보거나, 오프라인 빌드·정확한 버전 고정이 중요하면 <strong>Git Submodule</strong>.
- `CMakeLists.txt` 한 곳에서 의존성을 선언적으로 관리하고 저장소를 가볍게 유지하고 싶으면 <strong>FetchContent</strong>.
- 사전 컴파일 바이너리는 선택지가 아니므로, 어느 쪽이든 소스 빌드가 전제된다.

::: tip 핵심 정리
- 공식 지원 플랫폼은 Ubuntu Linux(WSL 제외), Raspberry Pi OS, RHEL, Windows, MacOS, ESP32 여섯 가지이고, WSL은 커널의 SocketCAN 미지원 때문에 제외된다.
- 필요한 도구는 컴파일러·CMake·Git이다. Linux는 `sudo apt install build-essential cmake git`, Windows는 Build Tools for Visual Studio·CMake·Git을 각각 설치한다.
- 통합은 Git 서브모듈과 CMake 조합이 가장 쉽고, FetchContent는 저장소를 건드리지 않는 대안이다. 사전 컴파일 바이너리는 공식 배포되지 않아 소스 빌드가 유일한 지원 방식이다.
- FetchContent를 쓸 때 `GIT_TAG`는 브랜치가 아니라 태그나 커밋 해시로 고정하는 것이 안정성과 구성 속도 모두에 유리하다.
- 어떤 방식이든 링크 대상은 `isobus::Isobus`, `isobus::HardwareIntegration`, `isobus::Utility`, 그리고 `Threads::Threads`로 동일하다.
:::

## 참고 자료
- [AgIsoStack++ 공식 문서 — Installation](https://isobus-plus-plus.readthedocs.io/en/latest/Installation.html)
- [AgIsoStack++ GitHub 저장소](https://github.com/Open-Agriculture/AgIsoStack-plus-plus)

## 다음 챕터
[CH6. 개발자 가이드](/study/agisostack/06-developer-guide)로 이어진다.
