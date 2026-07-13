---
title: "CH23. 네이티브 데몬 서비스 만들기 (케이스 스터디)"
description: "AgIsoStack++ 기반 C++ CAN 데몬 agcand을 vendor 파티션에 처음부터 끝까지 올리는 end-to-end 케이스 스터디. 프로젝트 배치·라이브러리 포팅·AIDL(ndk)·init rc·sepolicy·VINTF·빌드·검증·트러블슈팅까지 시리즈 전체 지식을 실전으로 종합한다."
date: 2026-07-13
tags: [android, aosp, vendor, daemon, aidl, sepolicy, vintf, can]
---

# CH23. 네이티브 데몬 서비스 만들기 (케이스 스터디)

::: info 학습 목표
- vendor 파티션에 C++ 네이티브 데몬을 배치하는 전체 파일 구조와 Android.bp 빌드 규칙을 익힌다.
- CMake 기반 외부 라이브러리(AgIsoStack++)를 cc_library_static으로 포팅하는 요령을 안다.
- ndk 백엔드 AIDL·init rc·sepolicy·VINTF를 엮어 데몬을 servicemanager에 안전하게 등록한다.
- 빌드·flash·검증 절차와, 데몬이 안 뜰 때의 증상→원인→해법 진단 흐름을 손에 익힌다.
:::

이 장은 시리즈의 종착점이다. 지금까지 [파티션](/study/android-internals/03-partitions-filesystems)·[init](/study/android-internals/08-init-zygote)·[서비스 아키텍처](/study/android-internals/09-service-architecture)·[네이티브 레벨](/study/android-internals/15-native-level)·[SELinux](/study/android-internals/16-selinux-avb)·[Binder](/study/android-internals/21-binder-userspace)를 따로따로 봤다면, 여기서 그 모두를 하나의 실전 작업으로 합친다. 목표는 가상의 vendor CAN 데몬 <strong>agcand</strong>을 커스텀 AOSP에 서비스로 올리는 것 — [AgIsoStack++](/study/isobus/) 기반 C++ 데몬이 트랙터의 CAN 버스를 읽어 Binder로 앱에 넘기는 구조다. 단계마다 앞 챕터로 링크를 걸어두었으니, 막히는 지점에서 되짚어 읽으면 된다.

## 시나리오와 설계

농기계 장비의 요구는 이렇다 — CAN 버스(ISOBUS)로 들어오는 트랙터 상태 데이터를 상시 수집하고, 화면 앱이 그 값을 실시간 구독한다. 이를 위해 vendor 파티션에 네이티브 데몬을 두고, 앱과는 Binder로 통신한다.

![agcand 전체 아키텍처 — CAN 버스 HW가 커널 SocketCAN(can0)으로, 그 데이터가 vendor의 agcand(AgIsoStack++·SocketCAN 수신 루프·BnCanAccessService)으로 흘러 vndservicemanager에 addService로 등록되고, 앱(Java)이 ICanAccessService 프록시로 Binder를 통해 구독하는 구조](/images/study-android-internals/23-architecture-light.png)
![agcand 전체 아키텍처 — CAN 버스 HW가 커널 SocketCAN(can0)으로, 그 데이터가 vendor의 agcand(AgIsoStack++·SocketCAN 수신 루프·BnCanAccessService)으로 흘러 vndservicemanager에 addService로 등록되고, 앱(Java)이 ICanAccessService 프록시로 Binder를 통해 구독하는 구조](/images/study-android-internals/23-architecture-dark.png)

설계 결정은 다음과 같다.

- <strong>배치 위치</strong>는 vendor 파티션이다. CAN 하드웨어는 SoC·보드에 종속된 vendor 자산이므로, [Treble](/study/android-internals/16-selinux-avb) 원칙상 system이 아니라 vendor에 둔다.
- <strong>Binder 도메인</strong>은 vndbinder다. vendor 데몬이 vendor 컨텍스트에서 돌기 때문이다([CH9](/study/android-internals/09-service-architecture) 참고).
- <strong>AIDL 백엔드</strong>는 ndk다. [CH21](/study/android-internals/21-binder-userspace)에서 봤듯 `libbinder_ndk`의 ABI가 안정적이라 vendor가 안전하게 쓴다. 앱 쪽은 같은 AIDL의 java 백엔드로 붙는다.
- <strong>CAN 입력</strong>은 커널 SocketCAN(`can0`)을 통한다. SocketCAN 자체는 [CAN 스터디 CH13](/study/can/13-socketcan-basics)에서 다뤘다.

## 컴포넌트 통합 4단계

데몬 하나를 올리는 일은 네 층에 각각 등록하는 작업의 합이다. 이 네 단계를 먼저 머릿속에 넣어두면, 이후 본문의 절들이 왜 그 순서로 나오는지 그리고 <strong>데몬이 안 뜰 때 어느 층을 의심할지</strong>가 분명해진다. 핵심은 <strong>각 단계가 빠졌을 때의 증상이 서로 다르다</strong>는 것이다 — 증상만 보면 어느 단계가 빠졌는지 역추적할 수 있다.

| 단계 | 무엇을 | 어디에 | 빠지면 생기는 증상 | 본문 절 |
|------|--------|--------|--------------------|---------|
| ① 빌드 | 소스·AIDL·라이브러리 빌드 규칙 | `Android.bp` | <strong>빌드 자체가 실패</strong>한다 | 포팅·AIDL·데몬 구현 |
| ② 탑재 | 산출물을 이미지에 포함 | 제품 `.mk`의 `PRODUCT_PACKAGES` | 빌드는 되는데 <strong>기기에 파일이 없다</strong> | 빌드·배포·검증 |
| ③ 실행 | 부팅 때 프로세스 기동 | `init.rc` (`Android.bp`의 `init_rc`로 배포) | 파일은 있는데 <strong>`ps`에 프로세스가 없다</strong> | init rc |
| ④ 허가 | 자원 접근 권한 | SELinux `.te` | 프로세스는 떠 있는데 <strong>소켓·Binder 접근이 거부</strong>된다 | sepolicy |

즉 "빌드 실패 → ①, 파일 없음 → ②, ps에 없음 → ③, 자원 거부 → ④"로 증상과 단계가 일대일 대응한다. 뒤의 [트러블슈팅 모음](#트러블슈팅-모음)이 정확히 이 대응을 진단 플로로 확장한 것이다. 여기에 서비스 등록 계약을 알리는 <strong>VINTF</strong>가 얹혀 다섯 조각이 완성된다. 이제 각 단계를 순서대로 만든다.

## 프로젝트 배치

vendor 아래에 회사 네임스페이스로 디렉토리를 만든다. 하나의 모듈이 소스·AIDL·init·sepolicy·VINTF를 모두 품는다.

![agcand 프로젝트 파일 배치도 — vendor/agmo/agcand/ 아래 Android.bp·aidl/ICanAccessService.aidl·src/main.cpp·src/CanAccessService.cpp·external/AgIsoStack·agcand.rc·sepolicy(te/file_contexts/service_contexts)·manifest_agcand.xml가 놓이고 PRODUCT_PACKAGES로 제품에 포함되는 트리](/images/study-android-internals/23-files-map-light.png)
![agcand 프로젝트 파일 배치도 — vendor/agmo/agcand/ 아래 Android.bp·aidl/ICanAccessService.aidl·src/main.cpp·src/CanAccessService.cpp·external/AgIsoStack·agcand.rc·sepolicy(te/file_contexts/service_contexts)·manifest_agcand.xml가 놓이고 PRODUCT_PACKAGES로 제품에 포함되는 트리](/images/study-android-internals/23-files-map-dark.png)

```
vendor/agmo/agcand/
├── Android.bp                      # 빌드 규칙 (Soong)
├── aidl/
│   └── com/agmo/agcand/
│       ├── ICanAccessService.aidl
│       ├── ICanCallback.aidl
│       └── CanFrame.aidl
├── src/
│   ├── main.cpp                    # 데몬 진입점
│   └── CanAccessService.cpp        # BnCanAccessService 구현
├── external/
│   └── AgIsoStack/                 # 포팅한 ISOBUS 스택
├── agcand.rc                    # init 스크립트
├── manifest_agcand.xml          # VINTF 조각
└── sepolicy/
    ├── agcand.te
    ├── file_contexts
    └── service_contexts
```

`vendor/`에 두면 빌드 결과가 `/vendor/bin/`, `/vendor/etc/init/`, `/vendor/etc/vintf/`에 설치된다([CH4 파일과 디렉토리](/study/android-internals/04-files-directories) 참고).

## 외부 라이브러리 포팅

AgIsoStack++는 CMake로 빌드되는 오픈소스 ISOBUS 스택이다. AOSP는 [Soong](/study/android-internals/14-building-aosp)(Android.bp)으로 빌드하므로, CMake 프로젝트를 그대로 쓸 수 없고 <strong>`cc_library_static`으로 재선언</strong>해야 한다.

포팅의 요령은 다음과 같다.

- CMake의 `add_library(... 소스들)`을 그대로 Soong `srcs`로 옮긴다. glob(`**/*.cpp`)이 되지만, AOSP는 명시적 나열을 선호하므로 소스를 직접 적는 편이 안전하다.
- `target_include_directories`는 `export_include_dirs`로 변환한다. 이 디렉토리가 이 라이브러리를 링크하는 쪽에 자동 노출된다.
- CMake 옵션(`-DCMAKE_...`)으로 켜던 기능 플래그는 `cflags`로 옮긴다.
- SocketCAN 백엔드를 선택한다. AgIsoStack++는 여러 CAN 드라이버 플러그인을 갖는데, 안드로이드에서는 커널 SocketCAN을 쓰므로 <strong>SocketCAN 하드웨어 인터페이스 소스만 포함</strong>하고 나머지 플랫폼 백엔드는 뺀다. SocketCAN은 리눅스 표준 `<linux/can.h>`에 의존하며 Bionic에서 제공되므로 별도 의존성이 없다([CH15 Bionic](/study/android-internals/15-native-level) 참고).

```python
// Android.bp — 라이브러리 부분
cc_library_static {
    name: "libAgIsoStack",
    vendor: true,
    srcs: [
        "external/AgIsoStack/isobus/src/*.cpp",
        "external/AgIsoStack/hardware_integration/src/socket_can_interface.cpp",
    ],
    export_include_dirs: [
        "external/AgIsoStack/isobus/include",
        "external/AgIsoStack/hardware_integration/include",
    ],
    cflags: ["-Wall", "-fexceptions"],
    rtti: true,
}
```

::: warning C++ 예외·RTTI
AOSP 네이티브 코드는 기본적으로 예외와 RTTI를 끈다. AgIsoStack++가 이를 쓴다면 `cflags: ["-fexceptions"]`와 `rtti: true`를 명시해야 링크가 된다. 라이브러리가 STL을 많이 쓰면 `stl: "libc++_static"`도 고려한다.
:::

## AIDL 인터페이스 정의

데몬이 앱에 제공할 계약을 AIDL로 선언한다. [CH21](/study/android-internals/21-binder-userspace)에서 본 stable AIDL 규칙을 그대로 적용한다.

```java
// aidl/com/agmo/agcand/CanFrame.aidl
package com.agmo.agcand;

@VintfStability
parcelable CanFrame {
    int pgn;
    long timestampMs;
    byte[] data;
}
```

```java
// aidl/com/agmo/agcand/ICanAccessService.aidl
package com.agmo.agcand;

import com.agmo.agcand.CanFrame;
import com.agmo.agcand.ICanCallback;

@VintfStability
interface ICanAccessService {
    CanFrame getLatestFrame(int pgn);
    oneway void subscribe(ICanCallback cb);
    oneway void unsubscribe(ICanCallback cb);
}
```

빌드 규칙에서 `aidl_interface` 모듈로 선언한다. VINTF 안정성과 vendor 사용을 명시하는 것이 핵심이다.

```python
// Android.bp — AIDL 부분
aidl_interface {
    name: "com.agmo.agcand",
    vendor_available: true,
    srcs: ["aidl/com/agmo/agcand/*.aidl"],
    stability: "vintf",              // VINTF 안정 인터페이스
    owner: "agmo",
    backend: {
        ndk: { enabled: true },      // 데몬(C++)이 쓸 백엔드
        java: { enabled: true },     // 앱이 쓸 백엔드
        cpp: { enabled: false },
    },
    versions_with_info: [
        { version: "1", imports: [] },
    ],
}
```

- <strong>`stability: "vintf"`</strong>는 이 인터페이스가 vendor/system 경계를 넘는 안정 계약임을 선언한다. 이 표시가 있어야 vndservicemanager에 vintf stability로 등록된다.
- <strong>`@VintfStability`</strong> 어노테이션을 AIDL 타입에도 붙여야 한다.
- <strong>버전 freeze</strong>: `m com.agmo.agcand-freeze-api`로 버전 1을 동결하면 `aidl_api/`에 스냅샷이 남는다. 이후 메서드는 끝에만 추가할 수 있다([CH21](/study/android-internals/21-binder-userspace)의 stable AIDL 참고).

## 데몬 구현

`main()`은 스레드풀을 세우고 서비스를 등록한 뒤 수신 루프로 들어간다. [CH21](/study/android-internals/21-binder-userspace)의 ndk 골격에 SocketCAN 수신을 붙인 형태다.

::: details src/main.cpp
```cpp
#include <android/binder_manager.h>
#include <android/binder_process.h>
#include <android-base/logging.h>
#include "CanAccessService.h"

using aidl::com::agmo::agcand::CanAccessService;

int main() {
    // 1) Binder 스레드풀 준비 (CH21의 ABinderProcess)
    ABinderProcess_setThreadPoolMaxThreadCount(4);

    // 2) 서비스 인스턴스 생성 및 등록
    auto service = ::ndk::SharedRefBase::make<CanAccessService>();
    const std::string name =
        std::string(CanAccessService::descriptor) + "/default";
    binder_status_t status =
        AServiceManager_addService(service->asBinder().get(), name.c_str());
    if (status != STATUS_OK) {
        LOG(ERROR) << "addService failed: " << status;
        return 1;
    }

    // 3) SocketCAN 수신 루프를 별도 스레드로 (CAN 스터디 CH13)
    service->startCanRxLoop("can0");

    // 4) Binder 수신 루프 진입 — 여기서 블록
    ABinderProcess_joinThreadPool();
    return 0;   // 도달하지 않음
}
```
:::

::: details src/CanAccessService.cpp (핵심 발췌)
```cpp
#include "CanAccessService.h"
#include <isobus/hardware_integration/socket_can_interface.hpp>
#include <linux/can.h>
#include <thread>

using aidl::com::agmo::agcand::CanFrame;
using aidl::com::agmo::agcand::ICanCallback;

// getLatestFrame — 동기 호출, 캐시 반환
::ndk::ScopedAStatus CanAccessService::getLatestFrame(
        int32_t pgn, CanFrame* out) {
    std::lock_guard<std::mutex> lk(mLock);
    *out = mCache[pgn];
    return ::ndk::ScopedAStatus::ok();
}

// subscribe — oneway, 콜백 등록 + 사망 통지 링크 (CH21 linkToDeath)
::ndk::ScopedAStatus CanAccessService::subscribe(
        const std::shared_ptr<ICanCallback>& cb) {
    std::lock_guard<std::mutex> lk(mLock);
    mCallbacks.push_back(cb);
    return ::ndk::ScopedAStatus::ok();
}

// SocketCAN 수신 루프 — 프레임을 캐시에 넣고 구독자에 통지
void CanAccessService::startCanRxLoop(const std::string& iface) {
    std::thread([this, iface] {
        isobus::SocketCANInterface can(iface.c_str());
        can.open();
        isobus::CANMessageFrame raw;
        while (can.read_frame(raw)) {
            CanFrame f;
            f.pgn = extractPgn(raw);
            f.timestampMs = nowMs();
            f.data.assign(raw.data, raw.data + raw.dataLength);
            {
                std::lock_guard<std::mutex> lk(mLock);
                mCache[f.pgn] = f;
                for (auto& cb : mCallbacks) cb->onFrame(f);  // oneway 통지
            }
        }
    }).detach();
}
```
:::

빌드 규칙의 실행 파일 부분은 이렇다.

```python
// Android.bp — 데몬 바이너리
cc_binary {
    name: "agcand",
    vendor: true,
    srcs: ["src/main.cpp", "src/CanAccessService.cpp"],
    shared_libs: [
        "libbinder_ndk",            // CH21 NDK Binder
        "liblog",
        "libbase",
    ],
    static_libs: [
        "libAgIsoStack",
        "com.agmo.agcand-V1-ndk",  // 생성된 ndk 스텁
    ],
    init_rc: ["agcand.rc"],
    vintf_fragments: ["manifest_agcand.xml"],
}
```

## init rc

[init](/study/android-internals/08-init-zygote)이 부팅 때 데몬을 띄우도록 서비스를 선언한다.

```bash
# agcand.rc
service agcand /vendor/bin/agcand
    class hal
    user system
    group system inet
    capabilities NET_RAW NET_ADMIN
    socket agcand stream 0660 system system
```

각 지시자의 의미는 다음과 같다.

- <strong>`class hal`</strong>: HAL 서비스 클래스로 묶어 다른 vendor HAL과 같은 시점에 시작·정지된다.
- <strong>`user system` / `group ... inet`</strong>: 데몬의 실행 UID/GID다. SocketCAN 소켓(`PF_CAN`)을 열려면 네트워크 접근이 필요하므로 `inet` 그룹을 준다.
- <strong>`capabilities NET_RAW NET_ADMIN`</strong>: raw CAN 소켓 생성과 인터페이스 제어에 필요한 리눅스 capability다. root로 돌리는 대신 <strong>필요한 권한만</strong> 부여하는 것이 원칙이다([CH11 리눅스 렌즈](/study/android-internals/11-linux-lens) 참고).

이 파일은 `init_rc`로 지정하면 빌드 시 `/vendor/etc/init/agcand.rc`에 설치되고, init이 부팅 중 자동으로 파싱한다.

### init이 만들어 물려주는 소켓

Binder 외에 <strong>제어용 유닉스 도메인 소켓</strong>을 하나 두는 패턴이 흔하다. 위 rc의 `socket` 옵션이 그것이다.

- <strong>`socket agcand stream 0660 system system`</strong>을 선언하면, init이 데몬을 실행하기 <strong>전에</strong> `/dev/socket/agcand` 소켓을 직접 만들어 열고, 그 <strong>fd를 환경변수 `ANDROID_SOCKET_agcand`로 데몬에 물려준다</strong>. 데몬은 `android_get_control_socket("agcand")`로 이 fd를 받아 `listen`만 하면 된다. 데몬이 스스로 소켓 파일을 만들지 않으므로, 권한(0660)·소유자(system:system)를 init이 <strong>일관되게 통제</strong>한다.
- 이 방식의 이점은 <strong>레이스가 없다</strong>는 것이다. 소켓이 init 단계에서 이미 존재하므로, 데몬이 아직 `listen`을 안 걸었어도 클라이언트의 연결 시도가 커널 큐에 안전하게 쌓인다.

이 소켓을 특정 클라이언트만 쓰게 하려면 SELinux에서 <strong>`connectto`를 명시적으로 허용</strong>해야 한다. 소켓 노드에 도메인 라벨을 붙이고, 접속 주체(예: 특정 앱·서비스 도메인)에게만 그 라벨로의 `unix_stream_socket connectto`를 열어준다. 자세한 규칙은 [sepolicy](#sepolicy) 절에서 이어 다룬다. 즉 소켓 자체는 init이 만들고, <strong>누가 접속할 수 있는지는 SELinux가 결정</strong>하는 이중 통제다.

## sepolicy

[SELinux](/study/android-internals/16-selinux-avb)가 enforcing이면, 정책이 없는 데몬은 소켓 하나 못 열고 죽는다. 도메인을 정의하고 필요한 접근을 허용해야 한다.

```bash
# sepolicy/agcand.te
type agcand, domain;
type agcand_exec, exec_type, vendor_file_type, file_type;

# init이 실행 파일에서 agcand 도메인으로 전이
init_daemon_domain(agcand)

# raw CAN 소켓 생성·사용 (SocketCAN)
allow agcand self:socket { create bind read write };
allow agcand self:capability net_raw;

# Binder 사용 및 서비스 등록
binder_use(agcand)
add_service(agcand, agcand_service)

# vndbinder 컨텍스트 사용
vndbinder_use(agcand)

# init이 만든 제어 소켓(/dev/socket/agcand) 사용
type agcand_socket, file_type, vendor_file_type;
allow agcand agcand_socket:sock_file { read write };
# 허용된 클라이언트 도메인만 이 소켓에 접속 (connectto)
allow agcand_client agcand:unix_stream_socket connectto;
allow agcand_client agcand_socket:sock_file write;
```

```bash
# sepolicy/file_contexts — 실행 파일과 제어 소켓에 라벨 부여
/vendor/bin/agcand           u:object_r:agcand_exec:s0
/dev/socket/agcand           u:object_r:agcand_socket:s0
```

```bash
# sepolicy/service_contexts — 서비스명에 라벨 부여
com.agmo.agcand.ICanAccessService/default    u:object_r:agcand_service:s0
```

핵심 구분이 <strong>service vs vndservice</strong>다. vendor 데몬은 vndbinder에 등록되므로, framework용 `service_contexts`가 아니라 <strong>`vndservice_contexts`</strong>에 라벨을 넣고 `vndbinder_use`를 허용해야 한다. 클라이언트가 vendor 프로세스면 이 경로가 맞다. 만약 <strong>앱(system 파티션의 자바)</strong>이 직접 붙어야 한다면 얘기가 달라진다 — 그때는 인터페이스를 framework binder 쪽으로 노출하거나, vendor↔system 경계를 넘는 별도 브릿지 구성을 검토해야 한다. agcand 시나리오처럼 vendor 앱이 소비하는 경우 vndservice 경로가 표준이다.

::: warning avc denial은 조용히 죽인다
정책이 빠지면 데몬은 에러 메시지 없이 소켓 생성이나 addService에서 실패한다. 이때 `dmesg | grep avc`에 `avc: denied { create } for ... scontext=...:agcand`처럼 찍히므로, 부팅 후 반드시 이 로그를 확인한다. 개발 중에는 `audit2allow`로 denial을 규칙으로 변환해 초안을 잡되, 최종본은 최소 권한으로 다듬는다.
:::

## VINTF

[Treble](/study/android-internals/16-selinux-avb)의 VINTF(Vendor Interface)는 vendor가 제공하는 인터페이스와 system이 기대하는 인터페이스의 호환성을 <strong>빌드·부팅 시 검증</strong>한다. 안정 AIDL 서비스는 vendor manifest에 조각으로 등록해야 한다.

```xml
<!-- manifest_agcand.xml -->
<manifest version="1.0" type="device">
    <hal format="aidl">
        <name>com.agmo.agcand</name>
        <version>1</version>
        <interface>
            <name>ICanAccessService</name>
            <instance>default</instance>
        </interface>
    </hal>
</manifest>
```

`vintf_fragments`로 지정하면 `/vendor/etc/vintf/manifest/`에 설치되고, 부팅 때 device manifest에 병합된다. FCM(Framework Compatibility Matrix)과 대조해 <strong>버전이 맞지 않으면 부팅 자체가 거부</strong>될 수 있으므로, AIDL 버전(1)과 manifest 버전을 일치시킨다.

## 빌드·배포·검증

제품에 데몬을 포함시키고 빌드한다.

```bash
# device/agmo/<board>/device.mk 에 추가
PRODUCT_PACKAGES += agcand
```

```bash
# 빌드 (CH14 참고)
$ source build/envsetup.sh
$ lunch agmo_board-userdebug
$ m agcand                       # 데몬만 빌드
$ m                                 # 전체 이미지

# 배포 — 방법 A: 전체 flash
$ fastboot flashall

# 배포 — 방법 B: vendor만 빠르게 (userdebug, adb root)
$ adb root && adb remount
$ adb sync vendor
$ adb reboot
```

부팅 후 <strong>검증 절차</strong>를 순서대로 밟는다.

```bash
# 1) 프로세스가 떴나
$ adb shell ps -A | grep agcand
system  1234  1  ...  /vendor/bin/agcand

# 2) servicemanager에 등록됐나 (vndbinder이므로 vndservice)
$ adb shell "su 0 vndservice list | grep agcand"
com.agmo.agcand.ICanAccessService/default: [com.agmo.agcand.ICanAccessService]

# 3) 로그 확인
$ adb logcat -s agcand

# 4) SELinux denial이 없나
$ adb shell "dmesg | grep 'avc.*agcand'"

# 5) 트랜잭션 응답이 오나 (CH22의 service call)
$ adb shell "su 0 service call com.agmo.agcand.ICanAccessService/default 1 i32 0xFEE5"
```

다섯 단계가 모두 통과하면 앱에서 java 백엔드로 `ICanAccessService`를 받아 `subscribe()`하면 된다.

### vcan으로 실보드 없이 검증

CAN 하드웨어가 아직 없어도 데몬의 로직은 검증할 수 있다. 리눅스 커널의 <strong>vcan(가상 CAN)</strong> 인터페이스와 `can-utils`로 가짜 CAN 트래픽을 흘려보내면 된다. SocketCAN은 실제 `can0`이든 가상 `vcan0`이든 동일한 API로 동작하므로([CAN 스터디 CH13](/study/can/13-socketcan-basics) 참고), 데몬 입장에서는 차이가 없다.

```bash
# 1) vcan 인터페이스 생성 (커널에 vcan 모듈 필요)
$ modprobe vcan
$ ip link add dev vcan0 type vcan
$ ip link set up vcan0

# 2) 데몬을 vcan0에 붙여 실행 (iface 인자를 vcan0로)
#    main.cpp의 startCanRxLoop("vcan0") 로 빌드하거나 프로퍼티로 주입

# 3) candump로 버스를 관찰하는 창을 하나 띄우고
$ candump vcan0

# 4) 다른 창에서 cansend로 프레임을 주입
$ cansend vcan0 18FEE500#0102030405060708

# 5) 데몬이 이 프레임을 캐시에 넣었는지 Binder로 확인
$ su 0 service call com.agmo.agcand.ICanAccessService/default 1 i32 0xFEE5
```

`cansend`로 쏜 PGN이 `service call`(또는 앱 구독)으로 되돌아오면, SocketCAN 수신 → 캐시 → Binder 응답의 <strong>전 경로가 실하드웨어 없이 검증</strong>된다.

이 vcan 검증은 <strong>검증 사다리</strong>의 첫 칸이다. 아래로 갈수록 실제에 가까워지고 비용도 커진다.

- <strong>① 호스트 vcan</strong>: 리눅스 PC나 에뮬레이터에서 vcan0로 로직만 빠르게 검증. 하드웨어·보드 이미지 불필요.
- <strong>② Cuttlefish</strong>: AOSP 가상 기기([CH14](/study/android-internals/14-building-aosp))에 vcan을 얹어, 실제 vendor 이미지·sepolicy·VINTF까지 포함한 상태로 데몬을 기동해 검증. 정책·namespace 문제가 여기서 드러난다.
- <strong>③ USB-CAN 어댑터</strong>: 개발 보드나 PC에 USB-CAN 동글을 물려 진짜 CAN 전기 신호로 프레임을 주고받으며 타이밍·에러 처리를 검증.
- <strong>④ 실장비</strong>: 최종적으로 트랙터 등 실제 ISOBUS 버스에 연결해 현장 데이터로 확인.

로직 버그는 ①에서, 통합(정책·이미지) 문제는 ②에서 대부분 잡고, 하드웨어·전기적 문제만 ③④로 넘긴다. 위 칸을 건너뛰고 바로 실장비로 가면 원인 층이 뒤섞여 진단이 어려워진다.

## 트러블슈팅 모음

데몬이 안 뜰 때는 위 검증 순서를 그대로 진단 플로로 쓴다. 막힌 단계의 오른쪽 원인부터 짚는다.

![agcand 기동 실패 진단 플로 — ps로 프로세스 확인(→rc 미로드/seclabel 누락), logcat/dmesg(→capability 누락), dmesg avc(→te allow 추가), service list(→service_contexts/VINTF 불일치), service call(→라이브러리 namespace 로드 실패) 순으로 각 단계에서 막히면 대응 원인부터 점검하는 흐름](/images/study-android-internals/23-bringup-checklist-light.png)
![agcand 기동 실패 진단 플로 — ps로 프로세스 확인(→rc 미로드/seclabel 누락), logcat/dmesg(→capability 누락), dmesg avc(→te allow 추가), service list(→service_contexts/VINTF 불일치), service call(→라이브러리 namespace 로드 실패) 순으로 각 단계에서 막히면 대응 원인부터 점검하는 흐름](/images/study-android-internals/23-bringup-checklist-dark.png)

| 증상 | 원인 | 해법 |
|------|------|------|
| `ps`에 프로세스가 없음 | init이 rc를 안 읽음 | `agcand.rc`가 `/vendor/etc/init/`에 설치됐는지, `PRODUCT_PACKAGES`에 포함됐는지 확인 |
| 프로세스가 즉시 죽음 (crash loop) | seclabel 누락 / 도메인 전이 실패 | `init_daemon_domain` 선언, `file_contexts` 라벨 확인 |
| 소켓 생성 실패로 죽음 | capability·정책 부족 | rc의 `capabilities NET_RAW`, `agcand.te`의 socket allow 확인 |
| `dmesg`에 avc denied | sepolicy 규칙 누락 | denial 메시지의 클래스·컨텍스트를 보고 `.te`에 allow 추가 (`audit2allow` 참고) |
| 프로세스는 떴는데 service list에 없음 | 서비스 라벨·등록 실패 | `vndservice_contexts` 라벨, `add_service` 정책, `addService` 반환값 확인 |
| 부팅이 아예 실패/거부 | VINTF 불일치 | manifest 버전과 AIDL 버전 일치, FCM 호환성 확인 |
| 클라이언트가 제어 소켓에 연결 실패 | `connectto` 정책 누락 | `agcand.te`의 `unix_stream_socket connectto`와 소켓 라벨(`agcand_socket`) 확인 |
| `dlopen`/링크 에러로 죽음 | vendor namespace 라이브러리 로드 실패 | `shared_libs`가 vendor에서 접근 가능한지, `vendor: true` 누락 확인 |

특히 마지막 <strong>namespace 라이브러리 로드 실패</strong>는 흔하면서 헷갈린다. vendor 프로세스는 linker namespace가 격리돼 system 라이브러리를 아무거나 못 쓴다([CH15 Bionic linker](/study/android-internals/15-native-level) 참고). VNDK/LLNDK로 노출된 라이브러리만 쓸 수 있고, 그 외는 정적 링크하거나 vendor에 함께 배치해야 한다. `logcat`에 `library "libXXX.so" not found`가 뜨면 이 경우다.

## 시리즈 마무리

여기까지가 <strong>Android Internals</strong> 시리즈의 끝이다. [아키텍처와 진화](/study/android-internals/01-architecture-evolution)에서 출발해 [파티션](/study/android-internals/03-partitions-filesystems)·[부팅](/study/android-internals/07-boot-process)·[init과 Zygote](/study/android-internals/08-init-zygote)로 시스템이 어떻게 서는지 봤고, [네이티브 레벨](/study/android-internals/15-native-level)·[SELinux와 Verified Boot](/study/android-internals/16-selinux-avb)로 그 아래 리눅스 기반과 보안 경계를 짚었으며, [ART](/study/android-internals/20-art-internals)와 [Binder](/study/android-internals/21-binder-userspace) 두 축으로 앱과 시스템이 어떻게 만나는지 파고들었다.

이 마지막 장은 그 지식이 흩어진 이론이 아니라 <strong>하나의 데몬을 실제로 올리는 능력</strong>으로 합쳐진다는 것을 보였다. agcand 하나를 부팅에서 앱까지 연결하는 데 파티션·init·capability·Binder·AIDL·sepolicy·VINTF·linker namespace가 전부 동원됐다. 커스텀 AOSP로 농기계 장비를 만드는 작업은 결국 이 조각들을 상황에 맞게 다시 조립하는 일이다. 각 장으로 돌아가 필요한 지식을 꺼내 쓰면 된다.

::: tip 핵심 정리
- 데몬 올리기는 <strong>빌드(Android.bp) → 탑재(PRODUCT_PACKAGES) → 실행(init.rc) → 허가(SELinux)</strong> 4단계 + VINTF의 합이며, 각 단계 누락 시 증상(빌드 실패 / 파일 없음 / ps에 없음 / 자원 거부)이 달라 역추적이 된다.
- CMake 라이브러리는 `cc_library_static`으로 재선언(srcs·export_include_dirs·cflags)하고, SocketCAN 백엔드만 골라 포팅한다.
- AIDL은 ndk 백엔드 + `stability: "vintf"`로 선언하고 버전을 freeze하며, 데몬은 `ABinderProcess` 스레드풀 + `AServiceManager_addService` + `joinThreadPool`로 올린다.
- init rc는 class hal·capability와 함께 제어 소켓(`socket` 옵션)을 만들어 데몬에 물려주고, SELinux는 그 소켓의 `connectto`로 접속 주체를 통제한다.
- 안 뜰 때는 ps→logcat→avc→service list→service call 순으로 진단하고, 검증은 <strong>vcan → Cuttlefish → USB-CAN → 실장비</strong> 사다리로 층을 나눠 원인을 분리한다.
:::
