---
title: "CH15. 네이티브 레벨과 Bionic"
description: "안드로이드 libc인 Bionic의 구성과 glibc와의 차이, linker namespace가 vendor 프로세스의 라이브러리 로딩을 통제하는 방식, VNDK와 ABI 안정성, 그리고 네이티브 데몬이 크래시했을 때 tombstone을 해부하고 심볼화하는 디버깅 워크플로를 다룬다."
date: 2026-07-13
tags: [android, aosp, bionic, linker, native-debugging]
---

# CH15. 네이티브 레벨과 Bionic

[CH14](/study/android-internals/14-building-aosp)에서 데몬을 빌드해 `/vendor/bin`에 올렸다. 그런데 막상 실행하면 `dlopen failed: library "libfoo.so" not found`, `CANNOT LINK EXECUTABLE` 같은 메시지로 죽거나, 아무 로그 없이 사라진다. 이 문제들의 근원은 전부 네이티브 레벨 — <strong>Bionic(libc), 동적 링커, VNDK</strong> — 에 있다. 이 챕터는 그 계층을 해부하고, 데몬이 죽었을 때 tombstone으로 원인을 짚는 법까지 다룬다.

## 학습 목표

- Bionic이 glibc와 무엇이 다르고 어떻게 구성되는지 이해한다.
- linker namespace와 ld.config.txt가 라이브러리 로딩을 통제하는 방식을 파악한다.
- VNDK·LLNDK와 ABI 안정성 보장 구조, 그리고 16 기준 VNDK deprecation 흐름을 안다.
- lldb·strace로 네이티브 데몬을 디버깅하는 워크플로를 익힌다.
- crash_dump→tombstone 경로를 이해하고 tombstone을 완전히 해부·심볼화한다.

## Bionic 심층

Bionic은 안드로이드의 C 라이브러리다. 리눅스 데스크톱의 glibc 자리를 대체한다. 구글이 glibc를 안 쓰고 새로 만든 이유는 크게 둘이다.

- <strong>라이선스.</strong> glibc는 LGPL이다. 안드로이드는 모든 앱이 libc에 링크하므로, LGPL의 조건이 앱 배포에까지 파급되는 것을 피하고 싶었다. Bionic은 BSD 계열 라이선스라 이 부담이 없다.
- <strong>경량화.</strong> glibc는 서버·데스크톱을 겨냥해 무겁다. 모바일·임베디드는 메모리와 부팅 속도가 빡빡하다. Bionic은 필요한 것만 담아 작고 빠르다.

구성은 세 갈래로 본다.

- <strong>libc.so</strong> — 표준 C 라이브러리 본체. malloc, string, stdio, syscall 래퍼, 그리고 안드로이드 고유의 property·logging 훅이 들어 있다.
- <strong>libm.so</strong> — 수학 함수(sin, sqrt 등).
- <strong>libdl.so</strong> — `dlopen`/`dlsym`/`dlclose` 같은 동적 로딩 API의 얇은 프론트엔드. 실제 로딩은 링커가 한다.

glibc와 다른 실무 포인트가 몇 개 있다.

<strong>pthread가 libc에 통합돼 있다.</strong> glibc는 `-lpthread`를 따로 링크해야 했지만(최근 glibc는 통합), Bionic은 처음부터 스레드가 libc 안에 있다. TLS(Thread-Local Storage) 처리, 스레드 생성 오버헤드가 모바일에 맞게 최적화돼 있다. 단, glibc 대비 <strong>일부 POSIX 기능이 빠져 있거나 다르게 동작</strong>한다. 예를 들어 과거 Bionic은 `pthread_cancel`을 지원하지 않았고, locale 지원도 극히 제한적이다. glibc를 가정하고 짠 서드파티 코드(예: CAN 라이브러리)를 포팅할 때 이 차이에서 컴파일·런타임 에러가 난다.

<strong>system property와 logging이 libc에 녹아 있다.</strong> `__system_property_get()` 같은 property API, `__android_log_print()`로 이어지는 logging이 Bionic 레벨에 있다. 데몬에서 `ALOGE(...)`를 쓰면 결국 이 경로를 탄다([CH12](/study/android-internals/12-logging-monitoring) 참고).

<strong>FORTIFY.</strong> Bionic은 `_FORTIFY_SOURCE`를 적극 활용한다. `memcpy`, `strcpy`, `sprintf` 같은 함수에 컴파일·런타임 경계 검사를 넣어, 버퍼 오버플로를 조기에 abort로 잡는다. AOSP 빌드에서 이유 없이 `FORTIFY: ... detected`로 죽는다면 실제 오버플로가 있는 것이다 — 끄지 말고 코드를 고쳐야 한다.

<strong>malloc 구현.</strong> Bionic의 기본 힙 할당자는 <strong>Scudo</strong>다(과거의 jemalloc·dlmalloc에서 넘어왔다). Scudo는 보안을 염두에 둔 할당자로, 청크 헤더 체크섬·격리(quarantine)·랜덤화로 힙 오버플로와 use-after-free를 악용하기 어렵게 만든다. 데몬이 힙 손상 시점보다 한참 뒤 엉뚱한 곳에서 abort하며 죽는다면, Scudo가 손상을 뒤늦게 감지한 것일 수 있다. 이럴 때 뒤의 메모리 디버깅 도구로 실제 손상 지점을 앞당겨 잡는다.

## 동적 링커

`linker64`(32비트는 `linker`)는 실행 파일과 `.so`를 메모리에 올리고 심볼을 잇는다. 안드로이드 링커의 핵심은 <strong>namespace</strong>다. 이 개념을 모르면 vendor 데몬의 라이브러리 로딩 문제를 절대 못 푼다.

![vendor 프로세스가 linker64를 통해 default·vndk·vendor/sphal namespace로 나뉘어 각기 다른 search path에서 라이브러리를 찾고, namespace 간에는 허용된 LLNDK만 링크되는 구조](/images/study-android-internals/15-linker-namespaces-light.png)
![vendor 프로세스가 linker64를 통해 default·vndk·vendor/sphal namespace로 나뉘어 각기 다른 search path에서 라이브러리를 찾고, namespace 간에는 허용된 LLNDK만 링크되는 구조](/images/study-android-internals/15-linker-namespaces-dark.png)

<strong>linker namespace</strong>는 "어떤 프로세스가 어떤 디렉토리에서만 라이브러리를 찾을 수 있는지"를 격리하는 장치다. Treble([CH1](/study/android-internals/01-architecture-evolution) 참고) 이후 system과 vendor를 분리하면서 도입됐다. 목적은 <strong>vendor 코드가 system의 비공개 라이브러리에 함부로 의존하지 못하게</strong> 막는 것이다. system 라이브러리가 버전업되면 그에 의존하던 vendor 바이너리가 깨지므로, 아예 접근 경로를 끊어 독립성을 강제한다.

대표적인 namespace는 이렇다.

- <strong>default</strong> — system 프로세스가 쓰는 기본 namespace. `/system/lib64`, `/system_ext/lib64`를 본다.
- <strong>vndk</strong> — VNDK 라이브러리(`/apex/com.android.vndk.../lib64`)를 담는 namespace.
- <strong>sphal</strong> — Same-Process HAL. SurfaceFlinger가 벤더 GPU 드라이버 같은 것을 같은 프로세스에서 dlopen할 때 쓰는 namespace로, `/vendor/lib64/egl` 등을 본다.
- <strong>vendor(또는 rs 등)</strong> — vendor 프로세스가 쓰는 namespace. `/vendor/lib64`, `/odm/lib64`를 본다.

이 규칙을 정의하는 파일이 <strong>ld.config.txt</strong>다. 파티션별로 여러 벌 있고(`/system/etc/ld.config.txt`, `/vendor/etc/ld.config.txt` 등), 프로세스가 어느 파티션의 바이너리냐에 따라 적용 config가 달라진다. 파일 안에는 각 namespace의 `search.paths`, `permitted.paths`, 그리고 <strong>namespace 간 링크 규칙</strong>(`namespace.vendor.link.vndk.shared_libs = ...`)이 들어 있다.

여기서 실무의 핵심 함정이 나온다. <strong>vendor 프로세스가 system 라이브러리를 못 여는 이유.</strong> 벤더 데몬(`/vendor/bin/agcand`)은 vendor namespace에서 돈다. 이 namespace의 search path에는 `/system/lib64`가 없다. 그래서 데몬이 system에만 있는 `.so`를 `dlopen`하려 하면 링커가 "그 경로는 볼 수 없다"며 실패시킨다. 에러는 대개 이렇게 뜬다.

```
dlopen failed: library "libsomething.so" not found:
  needed by /vendor/bin/agcand in namespace (vendor)
```

<strong>해법은 상황별로 다르다.</strong>

1. <strong>필요한 라이브러리를 vendor로 가져온다.</strong> 그 라이브러리를 `vendor_available: true`로 만들어 `/vendor/lib64`에도 설치되게 한다. 가장 정석이다.
2. <strong>LLNDK를 쓴다.</strong> 어떤 system 라이브러리(liblog, libc, libm, libnativewindow 등)는 vendor가 써도 되도록 ABI가 안정화돼 있다. 이런 라이브러리는 vendor namespace에서 자동으로 링크된다.
3. <strong>정 필요하면 ld.config에 링크를 추가한다.</strong> 커스텀 OS라면 `ld.config.txt`를 수정해 vendor namespace가 특정 라이브러리를 볼 수 있게 열 수 있다. 단 이건 ABI 안정성 보증을 스스로 떠안는 것이라 신중해야 한다.

<strong>DT_RUNPATH</strong>도 알아두자. ELF 바이너리에는 `DT_RUNPATH`/`DT_RPATH`로 추가 검색 경로를 박아둘 수 있다. AOSP 모듈은 대개 링커가 namespace로 통제하지만, 외부에서 가져온 prebuilt가 이상한 RUNPATH를 갖고 있으면 로딩이 꼬인다. `readelf -d libfoo.so | grep RUNPATH`로 확인한다.

`ld.config.txt`의 실제 모습을 보면 namespace 구조가 손에 잡힌다. vendor 프로세스용 config는 대략 이렇게 생겼다.

```
# /vendor/etc/ld.config.txt (발췌)
[vendor]
namespace.default.search.paths    = /vendor/${LIB}:/odm/${LIB}
namespace.default.permitted.paths = /vendor/${LIB}:/odm/${LIB}
namespace.default.links           = vndk,llndk

# vendor namespace가 vndk namespace로 이어질 때 볼 수 있는 라이브러리 목록
namespace.vndk.search.paths       = /apex/com.android.vndk.v34/${LIB}
namespace.default.link.vndk.shared_libs  = libbase.so:libc++.so:libhardware.so

# LLNDK: 언제나 열려 있는 최저수준 라이브러리
namespace.default.link.llndk.shared_libs = libc.so:libm.so:libdl.so:liblog.so
```

핵심은 `namespace.default.link.<타깃>.shared_libs`다. 여기 <strong>이름이 적힌 라이브러리만</strong> vendor 프로세스가 다른 namespace에서 빌려 쓸 수 있다. 데몬이 여는 `.so`가 이 목록에 없으면 앞의 `dlopen failed`가 난다. 커스텀 OS에서 정 필요하면 이 줄에 라이브러리를 추가하지만, 그 순간 그 라이브러리의 ABI 호환을 스스로 책임져야 한다.

## VNDK와 ABI 안정성

VNDK(Vendor Native Development Kit)는 <strong>vendor 코드가 안전하게 링크할 수 있도록 ABI를 안정화한 system 라이브러리 집합</strong>이다. Treble의 목표인 "system과 vendor를 독립적으로 업데이트"를 네이티브 레벨에서 떠받치는 장치다.

분류를 정리하면 이렇다.

- <strong>VNDK-core</strong> — vendor 프로세스가 쓰도록 허용된, ABI가 고정된 라이브러리. system 업데이트와 무관하게 같은 인터페이스를 보장한다.
- <strong>VNDK-SP(Same-Process)</strong> — sphal namespace에서 같은 프로세스로 로드되는 것들(libRS, libhardware 일부).
- <strong>LLNDK(Low-Level NDK)</strong> — libc, libm, libdl, liblog, libvndksupport 등 가장 저수준의 필수 라이브러리. vendor가 항상 쓸 수 있다.

ABI 안정성은 <strong>헤더 ABI 검사</strong>로 강제된다. AOSP 빌드는 VNDK/LLNDK 라이브러리의 심볼·구조체 레이아웃 덤프를 저장해두고, 변경이 생기면 빌드를 실패시킨다. 즉 "vendor가 의존하는 인터페이스를 실수로 깨는" 커밋이 트리에 들어가지 못한다.

<strong>16 기준 VNDK deprecation 흐름</strong>이 중요하다. 구글은 안드로이드 15부터 <strong>VNDK를 단계적으로 폐기(deprecate)</strong>하기 시작했다. VNDK가 유지보수 부담이 크고, 실제로는 APEX 기반 모듈화와 안정 인터페이스(AIDL·stable C API)로 같은 목표를 더 낫게 달성할 수 있다고 판단해서다. 안드로이드 16 시점에는 VNDK 컨셉의 비중이 더 줄었고, 벤더 라이브러리 의존성 관리가 "VNDK 목록 관리"에서 "필요한 것을 vendor에 직접 두거나 stable 인터페이스로 노출"하는 방향으로 이동하고 있다. 커스텀 OS를 만든다면 새 코드는 VNDK에 기대기보다 <strong>vendor_available</strong>과 <strong>stable AIDL/C API</strong>를 쓰는 편이 미래지향적이다.

## 네이티브 디버깅

데몬이 원하는 대로 안 돌 때 쓰는 도구들이다.

<strong>lldb + lldbserver.</strong> 안드로이드는 gdb 대신 LLVM의 lldb로 옮겨왔다(과거엔 gdbserver를 썼다). 디바이스에 `lldbserver`를 띄우고 호스트 lldb에서 붙는다.

```bash
# 디바이스: 실행 중인 데몬에 서버 붙이기
adb shell su root lldbserver *:5039 --attach $(pidof agcand)
adb forward tcp:5039 tcp:5039

# 호스트: lldb로 접속
lldb
(lldb) platform select remote-android
(lldb) platform connect connect://localhost:5039
(lldb) bt          # 백트레이스
```

AOSP 트리 안에서 빌드했다면 `lldbclient.py` 헬퍼가 심볼 경로까지 자동으로 잡아줘 훨씬 편하다.

<strong>strace로 syscall 추적.</strong> 데몬이 "왜 여기서 멈추나", "어떤 파일을 못 여나"를 볼 때 가장 빠르다. 특히 SELinux denial([CH16](/study/android-internals/16-selinux-avb))로 syscall이 `EACCES`로 막히는 경우를 즉시 잡아낸다.

```bash
# 실행 중 프로세스에 붙어 소켓 관련 호출만 추적
adb shell strace -f -e trace=network -p $(pidof agcand)

# 새로 실행하며 전체 추적
adb shell strace -f /vendor/bin/agcand
```

예를 들어 SocketCAN 소켓 생성이 막히면 `socket(AF_CAN, ...) = -1 EACCES`가 strace에 그대로 찍힌다. SocketCAN 자체의 동작은 [CAN 스터디 CH13](/study/can/13-socketcan-basics)에서 다룬다. 여기서는 "그 socket() 호출이 왜 EACCES인가"가 초점이고, 답은 대개 SELinux 정책이다.

## 크래시 해부

데몬이 세그폴트로 죽으면 안드로이드는 <strong>tombstone</strong>이라는 상세 크래시 리포트를 남긴다. 이걸 읽는 능력이 네이티브 개발의 핵심 역량이다.

![크래시 프로세스의 SIGSEGV를 libc 시그널 핸들러가 가로채 crash_dump를 fork하고, crash_dump가 ptrace로 스레드를 정지·언와인드한 뒤 tombstoned가 tombstone 파일과 logcat에 기록하는 파이프라인](/images/study-android-internals/15-crash-pipeline-light.png)
![크래시 프로세스의 SIGSEGV를 libc 시그널 핸들러가 가로채 crash_dump를 fork하고, crash_dump가 ptrace로 스레드를 정지·언와인드한 뒤 tombstoned가 tombstone 파일과 logcat에 기록하는 파이프라인](/images/study-android-internals/15-crash-pipeline-dark.png)

경로를 따라가자. 프로세스가 `SIGSEGV`/`SIGABRT` 등 치명 시그널을 받으면, <strong>Bionic이 미리 설치한 시그널 핸들러(debuggerd)</strong>가 먼저 가로챈다. 이 핸들러는 파이프를 만들고 <strong>crash_dump</strong> 프로세스를 fork·exec한다. crash_dump는 <strong>ptrace</strong>로 죽어가는 프로세스에 부착해 모든 스레드를 정지시키고, 스택을 언와인드하고, 레지스터·메모리 맵을 읽는다. 그 결과를 <strong>tombstoned</strong> 데몬에 넘기면, tombstoned가 `/data/tombstones/tombstone_NN` 파일로 쓰고 동시에 logcat(`F DEBUG` 태그)에도 요약을 남긴다.

tombstone을 열어보면 대략 이런 구조다.

```
*** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***
Build fingerprint: 'agmo/aosp_tractor/tractor:16/...'
ABI: 'arm64'
Timestamp: 2026-07-13 10:22:41.123
pid: 2314, tid: 2314, name: agcand  >>> /vendor/bin/agcand <<<
uid: 1000
signal 11 (SIGSEGV), code 1 (SEGV_MAPERR), fault addr 0x0000000000000010
Abort message: 'null CAN frame in dispatch()'      # abort()였다면 여기 이유
    x0  0000000000000000  x1  0000007fded23a10 ...  # 레지스터 덤프
backtrace:
      #00 pc 000000000004a1b8  /vendor/bin/agcand (dispatch(can_frame*)+40)
      #01 pc 000000000004a3c0  /vendor/bin/agcand (onRxReady()+220)
      #02 pc 00000000000512d4  /vendor/lib64/libcanutil.so (Loop::run()+96)
      #03 pc 00000000000a9c30  /apex/.../libc.so (__pthread_start(void*)+64)
memory map (fault address prefixed with --->):
    --->0000000000000000-...  ---  (첫 페이지, 널 역참조)
```

읽는 순서를 잡아두면 좋다.

1. <strong>signal</strong> — `SIGSEGV`(잘못된 메모리 접근)인지 `SIGABRT`(스스로 abort, 대개 assert·FORTIFY·C++ 예외)인지. code(`SEGV_MAPERR` 등)와 `fault addr`로 널 역참조(0 근처 주소)인지 판단한다.
2. <strong>Abort message</strong> — `SIGABRT`라면 여기에 이유가 그대로 있다. `CHECK` 실패, FORTIFY 감지 메시지 등.
3. <strong>backtrace</strong> — 크래시 시점의 콜스택. `#00`이 가장 안쪽이다. 각 프레임의 `pc` 오프셋과 라이브러리 경로가 나온다.
4. <strong>레지스터·memory map</strong> — 필요하면 `fault addr`가 어느 매핑에 속하는지 memory map에서 확인한다.

<strong>심볼화.</strong> 위 예시는 이미 함수명이 보이지만, 릴리스 바이너리는 스트립돼 있어 backtrace에 오프셋만 남는 경우가 많다. 이때 심볼 파일로 함수명·라인을 복원한다.

```bash
# ndk-stack: logcat/tombstone을 그대로 먹여 심볼화
adb logcat | ndk-stack -sym out/target/product/tractor/symbols/vendor/bin

# llvm-symbolizer: pc 오프셋을 직접 심볼로
llvm-symbolizer --obj=agcand 0x4a1b8
# → dispatch(can_frame*)  can_dispatch.cpp:88
```

AOSP 트리 안에서 빌드했다면 스트립되지 않은 심볼이 `out/target/product/<device>/symbols/` 아래에 그대로 있다. 이 디렉토리를 `ndk-stack`에 넘기면 tombstone의 오프셋들이 소스 라인으로 풀린다.

<strong>coredump.</strong> tombstone만으로 부족하면 코어 덤프를 받을 수 있다. `/proc/sys/kernel/core_pattern`과 rlimit을 조정해 프로세스가 죽을 때 코어 파일을 남기게 하고, 이를 lldb로 사후 분석한다. 임베디드에서는 저장 공간 탓에 상시로 켜기보다 재현 시에만 켜는 편이다.

## 메모리 디버깅

크래시가 "이미 늦은" 증상이라면, 메모리 디버깅 도구는 원인을 <strong>더 이른 시점</strong>에 잡는다.

- <strong>ASan(AddressSanitizer)</strong> — 힙·스택 오버플로, use-after-free를 컴파일 계측으로 즉시 잡는다. `Android.bp`에 `sanitize: { address: true }`를 넣어 빌드한다. 느리고 메모리를 많이 먹어 개발 빌드용이다.
- <strong>HWASan(Hardware-assisted ASan)</strong> — arm64의 top-byte-ignore 하드웨어 기능을 써서 ASan보다 훨씬 낮은 오버헤드로 같은 종류의 버그를 잡는다. 안드로이드가 미는 방향이다. `sanitize: { hwaddress: true }`.
- <strong>malloc debug</strong> — Bionic 내장 기능. 재빌드 없이 property로 켠다. front/rear guard로 오버플로를, backtrace 옵션으로 누수 지점을 잡는다.

```bash
# 재빌드 없이 특정 프로세스에 malloc debug 적용
adb shell setprop libc.debug.malloc.options "guard backtrace"
adb shell setprop wrap.agcand "\$@"
# 데몬 재시작하면 계측된 malloc으로 동작
```

- <strong>libmemunreachable</strong> — 도달 불가능한(누수된) 힙 블록을 스캔한다. 장시간 도는 데몬의 느린 누수를 잡을 때 유용하다.

```bash
adb shell dumpsys meminfo --unreachable $(pidof agcand)
```

::: warning sanitizer는 vendor 데몬에도 그대로 쓸 수 있다
`sanitize: { hwaddress: true }`를 데몬 `cc_binary`에 넣고 userdebug 빌드로 올리면 실제 CAN 트래픽을 받는 상태에서 메모리 버그를 잡을 수 있다. 다만 sanitizer 런타임 라이브러리가 vendor namespace에서 로드돼야 하므로, 로딩 실패가 나면 링커 namespace 설정을 먼저 의심한다.
:::

::: tip 핵심 정리
- Bionic은 라이선스(BSD)와 경량화를 이유로 만든 안드로이드 libc다. libc(property·logging·FORTIFY 포함)·libm·libdl로 구성되고, glibc 가정 코드는 POSIX 차이에서 문제가 난다.
- 링커는 namespace(default·vndk·sphal·vendor)로 라이브러리 접근을 격리한다. vendor 프로세스가 system `.so`를 못 여는 것은 vendor namespace의 search path에 없기 때문이고, `vendor_available`·LLNDK·ld.config 조정으로 푼다. 규칙은 ld.config.txt에 있다.
- VNDK/LLNDK는 vendor가 안전하게 링크하도록 ABI를 고정한 집합이나, 16 기준으로 VNDK는 deprecation 흐름에 있다. 새 코드는 vendor_available·stable AIDL/C API가 낫다.
- 크래시는 SIGSEGV/SIGABRT → debuggerd 핸들러 → crash_dump(ptrace) → tombstoned → /data/tombstones + logcat 경로로 tombstone을 남긴다. signal→abort message→backtrace 순으로 읽고 ndk-stack·llvm-symbolizer로 심볼화한다.
- 크래시 이전에 원인을 잡으려면 HWASan(권장)·ASan·malloc debug·libmemunreachable을 쓴다. sanitizer는 vendor 데몬에도 적용 가능하다.
:::

## 다음 챕터

[CH16. SELinux와 Verified Boot](/study/android-internals/16-selinux-avb)에서는 방금 strace에서 본 `EACCES`의 진짜 범인인 SELinux 정책을 다룬다. vendor 데몬에 도메인을 만들어 SocketCAN 소켓과 바인더 사용을 허용하는 `.te` 작성부터, 커스텀 이미지를 올리기 위한 AVB(Verified Boot) 우회·재서명까지 실전으로 짚는다.
