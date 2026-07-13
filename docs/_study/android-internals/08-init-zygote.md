---
title: "CH8. init과 Zygote"
description: "PID 1 init의 역할과 ueventd, System Properties 심층 구조, rc 파일 문법 완전 정복(트리거·서비스 옵션), 커스텀 CAN 데몬 rc 예제, Zygote fork 모델, 그리고 안드로이드 네이티브 데몬 총람을 다룬다."
date: 2026-07-13
tags: [android, aosp, init, zygote, property, rc]
---

# CH8. init과 Zygote

## 학습 목표
- PID 1 init이 하는 일(프로세스 reaping, 파일시스템 마운트, ueventd)을 이해한다.
- System Properties의 네임스페이스·로드 순서·공유 메모리 구조와 property trigger를 파악한다.
- rc 파일 문법(import, on 트리거, 명령어, service 옵션)을 완전히 읽고 쓸 수 있다.
- 커스텀 네이티브 데몬(CAN 데몬)을 위한 rc 파일을 작성할 수 있다.
- Zygote fork 모델(preload + COW)과 왜 이 구조인지, 그리고 주요 네이티브 데몬들의 역할을 안다.

이 챕터는 시리즈의 심장이다. 커스텀 안드로이드에 네이티브 데몬을 서비스로 올리는 실제 작업([CH23](/study/android-internals/23-native-daemon-case-study))의 문법적·개념적 토대가 전부 여기서 나온다.

## 1. init의 역할 — PID 1이 짊어지는 것

[CH7](/study/android-internals/07-boot-process)에서 봤듯 커널은 마지막에 `/init`을 PID 1로 실행한다. 리눅스에서 PID 1은 특별하다. 모든 프로세스의 조상이고, 죽으면 커널 패닉(kernel panic)이 난다. 안드로이드 init은 이 자리에서 다음을 책임진다.

- <strong>프로세스 reaping.</strong> 유닉스에서 부모가 먼저 죽거나 자식을 명시적으로 회수하지 않으면 자식은 <strong>좀비(zombie)</strong>가 되고, 고아 프로세스는 PID 1로 입양된다. init은 `SIGCHLD`를 받아 죽은 자식을 `waitpid`로 회수해 좀비를 청소한다. `oneshot`이 아닌 서비스가 죽으면 여기서 감지해 재시작 정책을 적용한다.
- <strong>파일시스템 마운트.</strong> first-stage에서 핵심 파티션을, second-stage의 `on fs`/`on post-fs`/`on post-fs-data` 단계에서 나머지 마운트를 처리한다(4절 트리거 참고).
- <strong>watchdogd.</strong> init은 하드웨어 워치독(`/dev/watchdog`)을 주기적으로 쓰다듬어(pet) 시스템이 살아있음을 알린다. init 자신이 멈추면 pet이 끊기고 하드웨어가 기기를 리셋한다. 소프트웨어가 완전히 굳는 상황의 최후 방어선이다.
- <strong>서브 reaper / 서비스 관리.</strong> `start`/`stop`/`restart`로 서비스 생명주기를 관리하고, 프로퍼티 변화·트리거에 반응해 액션 큐를 실행한다.

### ueventd — /dev 노드와 콜드/핫플러그

리눅스 커널은 장치가 나타나거나 사라질 때 <strong>uevent</strong>를 netlink 소켓으로 브로드캐스트한다. 데스크톱 리눅스는 `udev`가 이를 받지만, 안드로이드는 init이 `ueventd` 모드로 동작해 직접 처리한다(`/system/bin/ueventd`는 init의 심볼릭 링크다).

- <strong>콜드플러그(cold plug).</strong> 부팅 시 이미 존재하는 장치들은 uevent를 이미 흘려보낸 뒤다. ueventd는 `/sys`를 훑어 기존 장치에 대한 uevent를 재생(replay)시켜 `/dev` 노드를 만든다.
- <strong>핫플러그(hot plug).</strong> 부팅 후 USB·SD카드처럼 나중에 붙는 장치는 실시간 uevent로 처리한다.
- <strong>노드 생성과 권한.</strong> `ueventd.rc`(및 `/vendor/ueventd.rc`)에 장치 경로별 소유자·그룹·권한을 정의한다. 예를 들어 CAN 컨트롤러를 문자 장치나 네트워크 인터페이스로 노출할 때, 그 노드에 어떤 uid/gid가 접근할 수 있는지를 여기서 정한다.

```text
# /vendor/ueventd.rc 예시 — 장치노드 권한 규칙
# subsystem/devpath      mode   uid       gid
/dev/spidev0.0           0660   system    can
/dev/can0                0660   system    can
```

::: info uevent를 직접 관찰
```bash
# 커널 uevent를 실시간으로 덤프 (root)
adb shell 'toybox nc -lu ...'   # 실제로는 아래가 간단
adb shell 'stat /dev/can0'      # ueventd가 만든 노드의 권한 확인
adb shell 'ls -lZ /dev/'        # SELinux 레이블까지 확인
```
:::

## 2. System Properties 심층

<strong>System Properties</strong>는 안드로이드의 전역 key-value 설정 저장소다. 유닉스의 환경변수와 비슷하지만, 프로세스 로컬이 아니라 <strong>시스템 전역이고 공유 메모리 기반</strong>이라 어떤 프로세스에서 읽어도 같은 값을 본다.

![prop 소스 파일들이 property_service를 통해 공유 메모리 property store에 로드되고, 클라이언트는 mmap으로 읽고 setprop은 소켓으로 쓰는 프로퍼티 시스템 구조](/images/study-android-internals/08-property-system-light.png)
![prop 소스 파일들이 property_service를 통해 공유 메모리 property store에 로드되고, 클라이언트는 mmap으로 읽고 setprop은 소켓으로 쓰는 프로퍼티 시스템 구조](/images/study-android-internals/08-property-system-dark.png)

### 네임스페이스 — 접두어가 곧 의미다

프로퍼티 이름의 접두어는 관례가 아니라 <strong>동작·권한을 규정하는 네임스페이스</strong>다.

- <strong>`ro.`</strong> — read-only. 부팅 중 한 번 설정되면 다시 못 바꾼다(예: `ro.build.version.sdk`, `ro.product.model`). 커널 cmdline의 `androidboot.*`는 `ro.boot.*`로 들어온다.
- <strong>`persist.`</strong> — `/data/property/`에 파일로 저장돼 재부팅 후에도 유지된다(예: `persist.sys.timezone`). 단 `/data`가 마운트된 뒤(`post-fs-data` 이후)에만 로드·저장된다.
- <strong>`sys.`</strong> — 런타임 시스템 상태(예: `sys.boot_completed`, `sys.usb.state`). 휘발성이다.
- <strong>`ctl.`</strong> — 특수 제어 네임스페이스. `setprop ctl.start <svc>`는 서비스를 시작시키는 명령으로 해석된다(뒤 5절).
- <strong>`vendor.`</strong> — 벤더 파티션 소유 프로퍼티. Treble 이후 vendor/system 프로퍼티 소유권이 분리됐고, SELinux로 누가 쓸 수 있는지가 엄격히 통제된다.
- <strong>`debug.`</strong>, <strong>`dalvik.`</strong>, <strong>`init.svc.`</strong> 등도 각각 디버그 플래그, ART 튜닝, 서비스 상태(`init.svc.<name>` = running/stopped) 용도로 쓰인다.

### prop 파일 로드 순서

부팅 시 init은 여러 파티션의 `build.prop` 계열 파일을 <strong>정해진 순서</strong>로 읽어 property store를 채운다. 대략적인 순서는 이렇다.

1. ramdisk의 `default.prop`(현재는 `/system/etc/prop.default`) — 가장 먼저, 기본값.
2. `/system/build.prop` — 시스템 이미지 빌드 정보.
3. `/system_ext/`, `/product/` 계열.
4. `/vendor/build.prop`, `/odm/etc/build.prop` — 벤더/ODM.
5. `post-fs-data` 이후 `/data/property/persistent_properties` — persist.* 복원.

같은 이름이 여러 곳에 있으면 로드 순서상 나중 값이 이긴다(단 `ro.`는 최초 설정만 유효). `PropertyInit()`이 이 로딩을 수행하고, 이후 프로퍼티 접근은 모두 `property_service`를 거친다.

### property store — 공유 메모리 구조

프로퍼티는 `/dev/__properties__/` 아래 여러 파일에 <strong>tmpfs + mmap</strong>으로 올라간다. 핵심 자료구조는 프로퍼티 이름을 문자 단위로 쪼갠 <strong>trie(prefix tree)</strong>다. 이렇게 하면 `ro.build.` 같은 접두어 공유가 자연스럽고, SELinux 컨텍스트별로 프로퍼티를 별도 backing 파일에 분리해 접근 제어를 걸 수 있다.

- <strong>읽기</strong>는 각 프로세스가 이 공유 메모리를 자기 주소공간에 mmap해서 `libc`의 `__system_property_get()`으로 직접 읽는다. 즉 <strong>읽기에는 IPC가 없다</strong> — 그래서 매우 빠르다.
- <strong>쓰기</strong>는 아무나 못 한다. 클라이언트가 `property_service`의 유닉스 도메인 소켓(`/dev/socket/property_service`)에 요청을 보내면, init 안의 property_service가 SELinux 정책으로 <strong>보내는 쪽이 이 프로퍼티를 쓸 권한이 있는지</strong> 검사한 뒤에만 store를 갱신한다. 쓰기를 init 한 곳으로 몰아 감사·권한 통제를 집중시킨 구조다.

### 실습 — getprop / setprop / watchprops

```bash
adb shell getprop                       # 전체 프로퍼티 덤프
adb shell getprop ro.build.version.sdk  # 특정 프로퍼티 읽기
adb shell getprop | grep init.svc       # 서비스 상태 일괄 확인
adb shell setprop persist.sys.mylog 1   # 쓰기 (SELinux 허용 시)
adb shell watchprops                    # 프로퍼티 변화를 실시간 스트리밍
```

`watchprops`로 부팅 후 `sys.boot_completed`가 0→1로 바뀌는 순간이나, 서비스가 뜰 때 `init.svc.<name>`이 바뀌는 것을 직접 볼 수 있다.

### property triggers

프로퍼티는 단순 저장소를 넘어 <strong>이벤트 소스</strong>다. rc 파일에서 `on property:<name>=<value>`로 트리거를 걸면, 그 프로퍼티가 해당 값이 되는 순간 액션이 실행된다.

```text
# 특정 프로퍼티가 원하는 값이 되면 데몬을 시작
on property:vendor.can.ready=1
    start can_daemon

# sys.boot_completed가 뜨면 후처리
on property:sys.boot_completed=1
    setprop vendor.can.autostart 1
```

이 메커니즘 덕에 "vold가 키를 언락하면", "부팅이 끝나면", "특정 HAL이 준비되면" 같은 조건부 시작을 선언적으로 표현할 수 있다.

## 3. rc 파일 문법 완전 정복

init의 동작은 대부분 `*.rc` 파일에 <strong>선언적으로</strong> 기술된다. 문법은 Android Init Language라 부르며, 크게 <strong>action(트리거+명령)</strong>, <strong>service(데몬 정의)</strong>, <strong>import</strong>, <strong>on/command</strong> 요소로 이뤄진다.

### import와 로드 위치

init은 부팅 시 `/system/etc/init/hw/init.rc`를 진입점으로 읽고, 거기서 여러 디렉토리를 `import`한다. 오늘날 서비스 정의는 하나의 거대한 파일이 아니라, 각 파티션의 <strong>init 디렉토리에 파일별로 흩어져</strong> 있고 init이 자동으로 모두 로드한다.

- `/system/etc/init/` — 시스템 데몬.
- `/vendor/etc/init/` — 벤더 데몬(여기가 커스텀 CAN 데몬이 들어갈 자리다).
- `/odm/etc/init/`, `/product/etc/init/` 등.

```text
# init.rc 상단의 import 예시 (AOSP)
import /init.environ.rc
import /system/etc/init/hw/init.usb.rc
import /vendor/etc/init/hw/init.${ro.hardware}.rc
import /init.${ro.zygote}.rc
```

`import`는 파싱 시점에 즉시 펼쳐지지 않고 큐에 쌓였다가 순서대로 처리되며, 같은 트리거의 액션은 <strong>여러 파일에 나뉘어 있어도 파싱된 순서대로 이어 실행</strong>된다.

### on 트리거와 부트 단계

`on <trigger>` 블록은 트리거가 발생하면 그 안의 명령들을 순서대로 실행한다. 트리거는 부트 단계(`boot`, `fs` 등), 프로퍼티(`property:x=y`), 또는 커스텀 트리거(`trigger <name>`으로 발동)일 수 있다. 부트 단계 트리거는 <strong>정해진 순서</strong>로 발동한다.

![early-init부터 init, late-init, fs, post-fs, post-fs-data, zygote-start, boot까지 순서대로 발동하는 init 부트 단계 트리거 흐름](/images/study-android-internals/08-boot-stages-light.png)
![early-init부터 init, late-init, fs, post-fs, post-fs-data, zygote-start, boot까지 순서대로 발동하는 init 부트 단계 트리거 흐름](/images/study-android-internals/08-boot-stages-dark.png)

- <strong>early-init</strong> — 가장 이른 단계. ueventd 콜드플러그, SELinux 준비.
- <strong>init</strong> — 기본 디렉토리·심볼릭 링크 생성, 커널 파라미터 설정.
- <strong>late-init</strong> — 이후 단계들을 순서대로 큐잉하는 관문(`trigger fs`, `trigger post-fs` ...).
- <strong>fs</strong> — fstab 기반 파일시스템 마운트.
- <strong>post-fs</strong> — `/vendor` 등이 마운트된 뒤 접근 가능해지는 단계.
- <strong>post-fs-data</strong> — vold가 `/data`를 복호화·마운트한 뒤. 여기서부터 `/data`에 쓸 수 있고 `persist.*`가 로드된다.
- <strong>zygote-start</strong> — servicemanager·Zygote 등 코어 프로세스를 시작.
- <strong>boot</strong> — 부팅이 거의 끝난 시점의 마무리 액션.

<strong>커스텀 데몬을 어느 단계에서 시작할지</strong>가 실전에서 중요하다. `/data`에 로그를 써야 하면 `post-fs-data` 이후여야 하고, 다른 HAL/서비스에 의존하면 그게 준비된 뒤여야 한다. 보통은 `class_start`나 프로퍼티 트리거로 늦게 띄운다.

### 명령어 세트

`on` 블록 안에서 쓰는 대표 명령들이다.

```text
on post-fs-data
    mkdir /data/vendor/can 0770 system can   # 디렉토리 생성(+권한/소유자)
    chown system can /dev/can0               # 소유자 변경
    chmod 0660 /dev/can0                      # 권한 변경
    write /sys/class/net/can0/tx_queue_len 1000  # sysfs에 값 쓰기
    setprop vendor.can.ready 1                # 프로퍼티 설정
    start can_daemon                          # 서비스 시작
    exec_start wait_for_bus                    # 동기 실행(끝날 때까지 대기)
    copy /vendor/etc/can/default.cfg /data/vendor/can/cfg
    rm /data/vendor/can/stale.lock
```

`exec`/`exec_start`는 명령이 끝날 때까지 init을 블로킹하므로 남용하면 부팅이 느려진다. 대부분은 `start`(비동기 서비스 시작)를 쓴다.

### service 정의 — 옵션 총정리

`service` 블록은 init이 관리할 데몬을 정의한다. 형식은 `service <이름> <실행경로> [인자...]`이고, 그 아래 들여쓴 줄에 옵션을 나열한다. 주요 옵션은 다음과 같다.

| 옵션 | 의미 |
|------|------|
| `class <name>` | 서비스 그룹. `class_start <name>`으로 그룹 단위 시작(예: `class main`, `class hal`) |
| `user` / `group` | 실행 uid/gid. 보조 그룹을 여럿 나열 가능 |
| `capabilities <CAP...>` | root 없이 특정 리눅스 capability만 부여(예: `NET_ADMIN`, `NET_RAW`) |
| `disabled` | 자동 시작 안 함. `start`/`class_start`로 명시적 기동 필요 |
| `oneshot` | 한 번 실행하고 끝. 죽어도 재시작 안 함 |
| `restart_period` / `restart` | 재시작 정책. `oneshot`이 아니면 죽을 때 자동 재시작 |
| `socket <name> <type> <perm> [uid gid]` | 유닉스 소켓을 미리 만들어 `/dev/socket/<name>`으로 전달 |
| `file <path> <mode>` | 파일 디스크립터를 열어 서비스에 상속 |
| `writepid <path...>` | 시작 시 자기 PID를 파일에 기록(cgroup 배치 등) |
| `seclabel <label>` | 이 서비스가 실행될 SELinux 도메인 지정 |
| `override` | 같은 이름의 앞선 정의를 덮어씀(벤더가 시스템 서비스 재정의) |
| `task_profiles <p...>` | cgroup 기반 task profile(스케줄·메모리 제한) 적용 |
| `priority <n>` / `oom_score_adjust <n>` | nice 값 / LMK OOM 점수 조정 |
| `setenv <k> <v>` | 환경변수 주입 |
| `onrestart <cmd>` | 재시작 시 실행할 명령 |

<strong>keychords</strong>는 물리 키 조합에 서비스를 묶는 특수 기능이다(`keycodes <k1> <k2> ...`). 지정한 키를 동시에 누르면 서비스가 시작돼, 진단 모드나 로그 수집 데몬 진입에 쓰인다.

아래는 AOSP `init.rc`에 실제로 들어 있는 `ueventd` 정의 조각이다. 옵션이 어떻게 조합되는지 보라.

```text
service ueventd /system/bin/ueventd
    class core
    critical            # 죽으면 시스템에 치명적 → 반복 실패 시 재부팅
    seclabel u:r:ueventd:s0
    shutdown critical    # 셧다운 시에도 늦게까지 유지
```

`critical`은 서비스가 정해진 시간 창(window) 안에 여러 번 죽으면 기기를 recovery/재부팅시키는 강한 플래그다. 함부로 붙이면 데몬 하나 때문에 부팅 루프에 빠질 수 있으니, 커스텀 데몬에는 신중히 쓴다.

## 4. 커스텀 서비스 rc 실전 — CAN 데몬

이제 실제 목표를 구체화하자. AgIsoStack++ 기반 네이티브 CAN 통신 데몬을 `/vendor/bin/can_daemon`으로 빌드해 올렸다고 하자. 이를 서비스로 등록하는 `/vendor/etc/init/can_daemon.rc`는 다음처럼 쓴다(본격 케이스 스터디는 [CH23](/study/android-internals/23-native-daemon-case-study)에서 다룬다).

```text
# /vendor/etc/init/can_daemon.rc
service can_daemon /vendor/bin/can_daemon --iface can0 --config /vendor/etc/can/agiso.cfg
    class hal                       # HAL 그룹으로 묶어 class_start hal 시 함께
    user system                     # root 대신 system uid로 실행
    group system can inet           # CAN·네트워크 접근용 보조 그룹
    capabilities NET_ADMIN NET_RAW  # SocketCAN 인터페이스 제어에 필요한 최소 권한
    seclabel u:r:can_daemon:s0      # 전용 SELinux 도메인 (정책은 CH16)
    disabled                        # 자동 시작 금지 → 아래 트리거로 제어
    oom_score_adjust -800           # LMK가 쉽게 죽이지 못하게
    writepid /dev/cpuset/system-background/tasks

# can0 인터페이스가 준비되면 데몬을 올린다
on property:vendor.can.iface_up=1
    start can_daemon

# /data가 준비된 뒤 런타임 디렉토리·권한 세팅
on post-fs-data
    mkdir /data/vendor/can 0770 system can
    chown system can /dev/can0
```

여기서 설계 포인트는 세 가지다. (1) root로 돌리지 않고 `user system` + 필요한 `capabilities`만 부여해 최소 권한을 지킨다. (2) `disabled` + 프로퍼티 트리거로 "인터페이스가 실제 올라온 뒤"에만 시작해 경합을 피한다. (3) 전용 `seclabel` 도메인을 둬 SELinux로 이 데몬이 만질 수 있는 것을 좁힌다. SocketCAN 자체의 동작 원리는 [CAN 스터디 CH13](/study/can/13-socketcan-basics)을 참고하라.

## 5. Zygote — 왜 fork 모델인가

안드로이드의 모든 앱 프로세스와 `system_server`는 <strong>Zygote</strong>라는 하나의 부모에서 `fork`돼 나온다. Zygote(수정란)라는 이름 그대로다.

![Zygote가 프레임워크 클래스·리소스를 preload한 뒤 fork로 system_server와 앱 프로세스를 만들고 preload 페이지를 COW로 공유하는 모델](/images/study-android-internals/08-zygote-fork-light.png)
![Zygote가 프레임워크 클래스·리소스를 preload한 뒤 fork로 system_server와 앱 프로세스를 만들고 preload 페이지를 COW로 공유하는 모델](/images/study-android-internals/08-zygote-fork-dark.png)

<strong>왜 매번 새 VM을 띄우지 않고 fork하는가.</strong> 안드로이드 앱은 ART 위에서 돌고, 프레임워크 클래스(수천 개)와 리소스를 로드하는 비용이 크다. Zygote는 부팅 시 이 <strong>공통 프레임워크 클래스·리소스를 미리 로드(preload)</strong>해두고 소켓에서 대기한다. 새 앱이 필요하면 Zygote를 `fork`만 하면 되는데, 리눅스 `fork`는 <strong>COW(Copy-on-Write)</strong>라 부모의 메모리 페이지를 실제로 복사하지 않고 공유한다. 즉 모든 앱이 같은 preload된 프레임워크 페이지를 물리적으로 공유하다가, 자기가 쓴 페이지만 그때 복제한다. 결과적으로 <strong>앱 시작이 빠르고 전체 메모리 사용이 크게 준다</strong>.

- <strong>app_process.</strong> Zygote의 실체는 `/system/bin/app_process`(64비트는 `app_process64`)다. init이 이를 `--zygote --start-system-server` 인자로 띄운다.
- <strong>Zygote32/64.</strong> 32/64비트 앱을 모두 지원하려면 두 Zygote가 필요하다. `ro.zygote` 프로퍼티가 `zygote64_32`(64 주 + 32 보조) 같은 값으로 구성을 결정하고, init은 그에 맞는 `init.zygote64_32.rc`를 import한다.
- <strong>zygote 소켓 프로토콜.</strong> Zygote는 `/dev/socket/zygote` 유닉스 소켓에서 대기한다. AMS(ActivityManagerService)가 앱을 띄우려면 이 소켓으로 "이런 uid/gid/클래스명으로 fork해라"는 인자를 보내고, Zygote가 fork한 자식이 지정된 앱 클래스로 진입한다.
- <strong>webview_zygote.</strong> WebView 렌더러는 보안 격리를 위해 별도의 `webview_zygote`에서 fork돼 나온다.
- <strong>USAP 풀(Unspecialized App Process pool).</strong> Android 10+는 미리 fork만 해둔(아직 특정 앱으로 특수화되지 않은) 예비 프로세스 풀을 유지한다. 앱 시작 요청이 오면 fork를 기다리지 않고 풀에서 하나를 꺼내 특수화만 하므로 지연이 더 준다.

```bash
adb shell getprop ro.zygote                 # zygote 구성 확인 (예: zygote64_32)
adb shell ps -A | grep zygote               # 실행 중인 zygote 프로세스
adb shell 'cat /proc/$(pidof zygote64)/cmdline'  # app_process 인자 확인
```

`system_server`는 Zygote가 부팅 직후 처음으로 fork하는 특별한 자식이다. 그 내부는 [CH9](/study/android-internals/09-service-architecture)에서 해부한다.

## 6. 안드로이드 데몬 총람

init이 관리하는 네이티브 데몬들은 안드로이드 시스템의 뼈대다. 자주 마주치는 것들을 정리한다.

| 데몬 | 위치 | 역할 |
|------|------|------|
| `servicemanager` | /system/bin | framework binder 서비스 레지스트리([CH9](/study/android-internals/09-service-architecture)) |
| `hwservicemanager` | /system/bin | HIDL HAL용 레지스트리(hwbinder). AIDL 전환으로 축소 중 |
| `vold` | /system/bin | Volume Daemon. 저장소 마운트·암호화·`/data` 복호화 |
| `netd` | /system/bin | 네트워크 설정(라우팅·iptables·DNS) 데몬 |
| `logd` | /system/bin | 로그 버퍼 데몬. `logcat`이 여기서 읽는다([CH12](/study/android-internals/12-logging-monitoring)) |
| `lmkd` | /system/bin | Low Memory Killer Daemon. 메모리 압박 시 프로세스 종료 |
| `installd` | /system/bin | APK 설치·dexopt·앱 데이터 디렉토리 관리([CH17](/study/android-internals/17-package-management)) |
| `statsd` | /system/bin | 통계·메트릭 수집(statsdmetrics) |
| `ueventd` | /system/bin | (init 링크) `/dev` 노드 생성·핫플러그(1절) |
| `gatekeeperd` | /system/bin | 잠금화면 인증(PIN/패턴) 검증, HAL 연동 |
| `keystore2` | /system/bin | 하드웨어 지원 키 저장·서명(Keymint 연동) |
| `adbd` | /system/bin | ADB 데몬. USB/TCP로 셸·파일 전송 제공 |
| `init` | /system/bin | PID 1. 나머지 전부의 부모 |

```bash
adb shell ps -A -o PID,USER,NAME | grep -E 'vold|netd|logd|lmkd|servicemanager'
adb shell getprop | grep init.svc.vold    # vold 서비스 상태
```

커스텀 CAN 데몬도 결국 이 표에 한 줄 추가되는 것과 같다 — init이 관리하고, 전용 uid/SELinux 도메인을 갖고, 필요한 데몬(예: `vold`가 `/data`를 열어준 뒤)에 순서를 맞춰 뜨는 하나의 네이티브 서비스가 된다.

::: tip 핵심 정리
- init은 PID 1로서 프로세스 reaping, 파일시스템 마운트, watchdogd, 서비스 관리를 맡고, ueventd 모드로 `/dev` 노드와 핫플러그·권한을 처리한다.
- System Properties는 공유 메모리(trie) 기반 전역 key-value로, 읽기는 mmap으로 IPC 없이 빠르고 쓰기는 property_service 소켓 + SELinux로 통제된다. `ro./persist./sys./vendor.` 등 접두어가 동작을 규정하고, `on property:` 트리거로 이벤트 소스가 된다.
- rc 파일은 `import`, `on <trigger>`(early-init→...→post-fs-data→zygote-start→boot 순), 명령어, `service`(class/user/capabilities/disabled/oneshot/socket/seclabel...)로 데몬을 선언적으로 정의한다.
- 커스텀 CAN 데몬은 `user system`+최소 `capabilities`, `disabled`+프로퍼티 트리거 시작, 전용 `seclabel` 도메인으로 최소 권한 원칙에 맞춰 `/vendor/etc/init/`에 등록한다.
- Zygote는 프레임워크를 preload한 뒤 fork(COW)로 앱·system_server를 만들어 시작 속도와 메모리를 아끼며, USAP 풀로 지연을 더 줄인다.
:::

## 다음 챕터
[CH9. 서비스 아키텍처](/study/android-internals/09-service-architecture)에서는 "서비스"의 세 가지 의미를 구분하고, 세 개의 Binder 도메인(framework/vnd/hw), ServiceManager, VINTF, 그리고 Zygote가 낳은 `system_server`의 내부 구조를 다룬다.
