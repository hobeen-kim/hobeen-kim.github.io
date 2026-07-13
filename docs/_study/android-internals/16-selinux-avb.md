---
title: "CH16. SELinux와 Verified Boot"
description: "안드로이드 SELinux의 TE 기반 MAC 모델과 Treble의 platform/vendor 정책 분리, vendor 네이티브 데몬에 도메인을 만들어 SocketCAN·바인더 사용을 허용하는 .te 작성 실전, avc denial 디버깅, 그리고 커스텀 이미지를 올리기 위한 AVB(Verified Boot) 우회·재서명까지 다룬다."
date: 2026-07-13
tags: [android, aosp, selinux, sepolicy, avb, verified-boot]
---

# CH16. SELinux와 Verified Boot

vendor 데몬을 `/vendor/bin`에 올리고 init에 등록했는데 부팅 중 조용히 죽는다. logcat에는 `avc: denied { create } for ... scontext=u:r:agcand:s0`가 흐른다. SocketCAN 소켓 하나 여는 데도 커널이 막는다. 이 벽이 바로 <strong>SELinux</strong>다. 그리고 커스텀으로 빌드한 이미지를 실제 보드에 flash하면 이번엔 부트로더가 <strong>Verified Boot(AVB)</strong> 서명 검증에서 멈춘다. 네이티브 데몬을 실제로 올릴 때 반드시 부딪히는 이 두 관문을 이 챕터에서 실전 밀도로 정리한다.

## 학습 목표

- DAC와 MAC의 차이, TE(Type Enforcement) 기반 SELinux 모델과 컨텍스트 구조를 이해한다.
- Treble의 platform/vendor sepolicy 분리 구조와 정책 소스 위치를 파악한다.
- .te·file_contexts·service_contexts 등 정책 파일 문법과 매크로를 익힌다.
- vendor 데몬에 도메인을 만들어 SocketCAN·바인더 사용을 허용하는 정책을 직접 쓴다.
- avc denial을 읽고 audit2allow·permissive로 디버깅하는 워크플로를 익힌다.
- AVB(dm-verity·vbmeta) 신뢰 체인과 커스텀 이미지 개발 시 우회·재서명 방법을 안다.

## SELinux 기초

리눅스의 전통적 권한 모델은 <strong>DAC(Discretionary Access Control)</strong>다. 파일 소유자·그룹·rwx 비트가 전부이고, 소유자가 재량껏 권한을 바꿀 수 있다. 문제는 <strong>root가 되면 DAC가 무의미</strong>해진다는 점이다. 익스플로잇으로 프로세스가 root 권한을 얻으면 시스템 전체를 휘두른다.

<strong>MAC(Mandatory Access Control)</strong>는 이 위에 <strong>강제된 두 번째 관문</strong>을 놓는다. 프로세스가 root라도, 중앙 정책이 허용하지 않은 동작은 커널이 막는다. SELinux가 안드로이드의 MAC 구현이다. 핵심 슬로건은 "기본은 전부 거부(default deny), 명시적으로 허용한 것만 통과"다.

SELinux의 모델은 <strong>TE(Type Enforcement)</strong>다. 모든 주체(프로세스)와 객체(파일·소켓·프로퍼티 등)에 <strong>타입(type)</strong>이라는 라벨을 붙이고, "어떤 타입이 어떤 타입에 어떤 동작을 할 수 있는지"를 규칙으로 선언한다. 프로세스에 붙은 타입은 특별히 <strong>도메인(domain)</strong>이라 부른다.

라벨의 전체 형식은 <strong>컨텍스트</strong>다.

```
u:r:agcand:s0
│ │    │       │
│ │    │       └ level (MLS, 안드로이드는 대부분 s0)
│ │    └ type/domain (agcand)
│ └ role (프로세스는 r, 객체는 object_r)
└ user (안드로이드는 대부분 u)
```

안드로이드는 SELinux의 user·role·MLS 기능을 거의 안 쓰고 <strong>type</strong>에 사실상 모든 정책을 싣는다. 그래서 실전에서 신경 쓰는 건 거의 type/domain 하나다.

동작 모드는 둘이다.

- <strong>enforcing</strong> — 정책 위반을 <strong>실제로 차단</strong>하고 로그를 남긴다. 양산 기기는 항상 이 모드다.
- <strong>permissive</strong> — 위반을 <strong>차단하지 않고 로그만</strong> 남긴다. 개발 중 정책을 만들 때 쓴다.

안드로이드 SELinux 적용 <strong>역사</strong>: 안드로이드 4.3에서 permissive로 처음 도입됐고, 4.4에서 일부 핵심 도메인이 enforcing으로 바뀌었으며, 5.0부터 <strong>전면 enforcing</strong>이 됐다. 이후 버전이 올라갈수록 정책이 촘촘해져, 지금은 vendor 데몬 하나 올리는 데도 정책을 반드시 써야 한다.

## 안드로이드 sepolicy 구조

Treble([CH1](/study/android-internals/01-architecture-evolution) 참고)의 원칙 — system과 vendor의 독립 업데이트 — 은 SELinux 정책에도 그대로 적용된다. 정책이 <strong>platform(플랫폼)과 vendor(벤더)로 분리</strong>돼 있다.

![플랫폼 정책(system/sepolicy)과 벤더 정책(device/.../sepolicy)이 각각 CIL로 컴파일돼 plat_sepolicy.cil·vendor_sepolicy.cil로 나뉘고 부팅 시 secilc가 결합해 커널에 로드되는 구조](/images/study-android-internals/16-sepolicy-split-light.png)
![플랫폼 정책(system/sepolicy)과 벤더 정책(device/.../sepolicy)이 각각 CIL로 컴파일돼 plat_sepolicy.cil·vendor_sepolicy.cil로 나뉘고 부팅 시 secilc가 결합해 커널에 로드되는 구조](/images/study-android-internals/16-sepolicy-split-dark.png)

- <strong>플랫폼 정책</strong>은 구글이 소유하고 `system/sepolicy`에 있다. 하위에 `public`(vendor가 참조할 수 있는 안정 인터페이스), `private`(플랫폼 내부용), `vendor`(vendor 컴포넌트용) 디렉토리가 나뉜다.
- <strong>벤더 정책</strong>은 우리가 소유하고 `device/<vendor>/<board>/sepolicy`에 둔다. [CH14](/study/android-internals/14-building-aosp)에서 본 `BOARD_VENDOR_SEPOLICY_DIRS`로 이 디렉토리를 빌드에 등록한다.

두 정책은 각각 <strong>CIL(Common Intermediate Language)</strong>로 컴파일돼 파티션별로 나뉘어 설치된다(`plat_sepolicy.cil`은 system 쪽, `vendor_sepolicy.cil`은 vendor 쪽). 부팅 시 init이 이 조각들을 <strong>secilc</strong>로 결합해 하나의 바이너리 정책을 만들고 커널에 로드한다. 이 분리 덕분에 구글이 플랫폼 정책을 업데이트해도 벤더 정책을 다시 안 짜도 되고, 반대로 우리가 데몬 정책을 바꿔도 플랫폼을 안 건드린다.

여기서 <strong>neverallow</strong>의 의미가 드러난다. 플랫폼 정책은 "vendor가 절대 하면 안 되는 것"을 `neverallow`로 못박아 둔다. 우리가 vendor 정책에서 그 선을 넘는 `allow`를 쓰면 <strong>빌드가 컴파일 단계에서 실패</strong>한다. 런타임 사고를 빌드 타임에 막는 안전장치다.

## 정책 문법

정책 파일은 종류별로 역할이 나뉜다.

- <strong>.te</strong> — Type Enforcement 규칙 본체. type 선언과 allow/neverallow가 여기 있다.
- <strong>file_contexts</strong> — 파일 경로에 타입을 매핑. "이 경로의 파일은 이 타입"을 정한다.
- <strong>service_contexts</strong> — 바인더 서비스 이름에 타입을 매핑.
- <strong>property_contexts</strong> — system property 이름에 타입을 매핑.
- <strong>seapp_contexts</strong> — 앱(UID/seinfo)에 도메인·타입을 매핑.
- <strong>genfs_contexts</strong> — sysfs·procfs처럼 라벨을 파일에 저장 못 하는 파일시스템의 경로에 타입을 매핑.

`.te`의 핵심 구문은 이렇다.

```
# 타입(도메인) 선언
type agcand, domain;
type agcand_exec, exec_type, vendor_file_type, file_type;

# allow 규칙:  allow 주체도메인 대상타입:클래스 { 퍼미션 };
allow agcand self:global_capability_class_set { net_admin net_raw };

# neverallow: 이 선을 넘는 allow가 있으면 빌드 실패
neverallow agcand shell_data_file:file *;

# dontaudit: 거부는 하되 로그는 남기지 않음(노이즈 억제)
dontaudit agcand proc_net:file read;
```

`allow`의 구조는 항상 <strong>"누가(scontext domain) — 무엇에(tcontext type) — 어떤 클래스의 — 어떤 퍼미션을"</strong>이다. 클래스는 `file`, `dir`, `chr_file`, `socket`, `binder`, `capability` 등 커널 객체 종류다.

<strong>매크로</strong>가 정책 작성을 크게 줄여준다. 플랫폼이 제공하는 M4 매크로를 쓰면 반복되는 규칙 묶음을 한 줄로 표현한다. 가장 중요한 것이 `init_daemon_domain`이다.

```
# 이 한 줄이:
#  - agcand_exec 파일을 init이 실행하면 agcand 도메인으로 전이(domain transition)
#  - 그에 필요한 여러 allow를 한꺼번에 깔아준다
init_daemon_domain(agcand)
```

이 매크로가 없으면 "init이 이 실행 파일을 exec할 수 있고, 실행되면 agcand 도메인으로 바뀌고, 그 전이에 필요한 권한"을 일일이 써야 한다. 매크로가 그 보일러플레이트를 대신한다. 이 외에 `net_domain`(네트워크 기본 권한), `binder_use`(바인더 사용 기본 권한) 등 자주 쓰는 매크로가 있다.

## 네이티브 데몬 정책 실전

이제 실제로 vendor 데몬 `agcand`에 도메인을 만들어 보자. 이 데몬은 SocketCAN 소켓을 열어 CAN 버스와 통신하고, 바인더로 시스템 서비스와 대화하며, `/dev/socket`에 유닉스 소켓을 만든다. 필요한 파일은 `device/agmo/tractor/sepolicy/` 아래에 둔다.

먼저 <strong>agcand.te</strong> — 도메인 정의와 권한이다.

```
# device/agmo/tractor/sepolicy/agcand.te

# 도메인과 실행 파일 타입 선언
type agcand, domain;
type agcand_exec, exec_type, vendor_file_type, file_type;

# init이 /vendor/bin/agcand을 exec하면 agcand 도메인으로 전이
init_daemon_domain(agcand)

# --- SocketCAN ---
# AF_CAN raw 소켓 생성/제어에는 net_raw + net_admin capability가 필요
allow agcand self:global_capability_class_set { net_raw net_admin };
# CAN 소켓 클래스에 대한 동작 허용 (커널이 can_socket 클래스로 라벨)
allow agcand self:can_socket { create bind read write setopt getopt ioctl };

# --- 바인더 ---
# servicemanager를 찾고 바인더 IPC를 쓰기 위한 기본 권한
binder_use(agcand)
# 우리가 붙을 상대 서비스(예: 특정 vendor HAL) 호출 허용
binder_call(agcand, our_hal_server)

# --- /dev/socket 유닉스 소켓 ---
type agcand_socket, file_type, vendor_file_type;
allow agcand agcand_socket:sock_file { create write unlink };
allow agcand agcand:unix_stream_socket { create_stream_socket_perms };

# --- 로깅/프로퍼티 ---
# vendor 데몬이 흔히 쓰는 기본 권한 묶음
set_prop(agcand, vendor_can_prop)
```

`self:can_socket`에서 보듯 SocketCAN은 커널이 별도 소켓 클래스로 라벨한다. 그래서 일반 네트워크 소켓 권한과 별개로 `can_socket` 퍼미션을 명시해야 한다. AF_CAN raw 소켓은 프로모스큐어스한 접근이라 `net_raw`/`net_admin` capability도 필요하다. SocketCAN 프로그래밍 자체는 [CAN 스터디 CH13](/study/can/13-socketcan-basics)에서 다룬다 — 여기서는 그 `socket(AF_CAN, ...)` 호출이 SELinux를 통과하도록 여는 것이 목적이다.

다음 <strong>file_contexts</strong> — 실행 파일과 소켓 경로에 타입을 매핑한다.

```
# device/agmo/tractor/sepolicy/file_contexts

/vendor/bin/agcand        u:object_r:agcand_exec:s0
/dev/socket/agcand(/.*)?  u:object_r:agcand_socket:s0
```

첫 줄이 없으면 `/vendor/bin/agcand`은 기본 타입(`vendor_file`)으로 라벨되고, `init_daemon_domain`이 기대하는 `agcand_exec` 타입이 아니어서 <strong>도메인 전이가 일어나지 않는다</strong>. 그러면 데몬이 init 도메인 그대로 돌다가 엉뚱한 denial을 맞는다. "정책은 다 썼는데 도메인이 안 바뀐다"의 90%가 file_contexts 누락이다.

<strong>seclabel과의 관계</strong>도 짚자. init `.rc`에서 서비스를 정의할 때 `seclabel u:r:agcand:s0`을 명시할 수도 있다. 하지만 `init_daemon_domain` + file_contexts 조합으로 <strong>자동 전이</strong>가 걸리면 seclabel을 굳이 안 써도 된다. 자동 전이를 쓰는 것이 표준이고, seclabel 명시는 전이가 애매한 특수 케이스에서만 쓴다.

```
# init.tractor.rc — 서비스 정의 (seclabel 없이도 file_contexts로 자동 전이됨)
service agcand /vendor/bin/agcand
    class hal
    user system
    group system inet
    capabilities NET_RAW NET_ADMIN
```

### 유닉스 도메인 소켓 접근 통제 — connectto 화이트리스트

데몬이 `/dev/socket/agcand`에 리스닝 소켓을 열면, "누가 이 소켓에 붙을 수 있는가"를 정책으로 통제해야 한다. 소켓을 여는 것과 <strong>거기에 연결하는 것</strong>은 별개의 퍼미션이다. 연결 쪽 퍼미션이 `unix_stream_socket`의 <strong>connectto</strong>다.

init에게 소켓을 대신 만들게 하려면 `.rc`에 `socket` 옵션을 준다. 이러면 init이 부팅 때 소켓을 만들어 데몬에 넘겨준다.

```
# init.tractor.rc
service agcand /vendor/bin/agcand
    class hal
    user system
    group system inet
    socket agcand stream 0660 system system   # /dev/socket/agcand 생성
    capabilities NET_RAW NET_ADMIN
```

이제 정책에서, <strong>특정 도메인만</strong> 이 소켓에 붙을 수 있게 연다. 예를 들어 우리 시스템 서비스 `tractorservice`만 허용하고 싶다면 이렇게 쓴다.

```
# agcand.te — 데몬 쪽: 소켓 생성/리슨
allow agcand agcand:unix_stream_socket { create_stream_socket_perms listen accept };

# tractorservice.te — 클라이언트 쪽: agcand 소켓 파일에 write + 연결
allow tractorservice agcand_socket:sock_file write;
allow tractorservice agcand:unix_stream_socket connectto;
```

핵심은 <strong>connectto를 적어준 도메인만 연결된다</strong>는 것이다. 여기에 `tractorservice`만 적혀 있으면, 일반 앱 도메인(`untrusted_app` 등)은 이 소켓에 붙으려다 denial을 맞는다. 앱이 vendor 데몬의 내부 소켓에 직접 접근하는 것을 막는 전형적 패턴이다 — 앱은 정식 바인더 API를 거치게 하고, 원시 소켓은 신뢰된 시스템 서비스에만 연다.

이것이 SELinux의 <strong>화이트리스트 원칙</strong>이다. <strong>allow로 명시하지 않은 것은 전부 거부된다.</strong> "앱이 못 붙게 막는 규칙"을 따로 쓰는 게 아니라, "붙을 수 있는 도메인만 allow로 나열"하면 나머지는 자동으로 차단된다. 그래서 정책 작성은 언제나 "무엇을 금지할까"가 아니라 "무엇만 허용할까"를 정하는 일이다.

## denial 디버깅

정책을 다 썼다고 한 번에 되는 일은 거의 없다. denial을 읽고 좁혀가는 워크플로가 실전의 대부분이다.

<strong>avc denial 로그</strong>는 이렇게 생겼다.

```
avc: denied  { create } for  comm="agcand"
     scontext=u:r:agcand:s0 tcontext=u:r:agcand:s0
     tclass=can_socket permissive=0
```

읽는 법: <strong>{ create }</strong>가 거부된 퍼미션, <strong>scontext</strong>가 주체 도메인(agcand), <strong>tcontext</strong>가 대상, <strong>tclass</strong>가 객체 클래스(can_socket). `permissive=0`은 실제로 차단됐다는 뜻이다. 이 한 줄이 곧 필요한 allow를 알려준다 — "agcand이 can_socket을 create하게 허용하라".

denial 수집은 logcat과 dmesg 양쪽을 본다.

```bash
adb shell dmesg | grep 'avc: denied'
adb logcat -b events | grep avc
```

<strong>audit2allow</strong>는 denial 로그를 먹어 필요한 allow 규칙을 자동 생성한다.

```bash
adb shell dmesg | grep 'avc: denied' | audit2allow
# 출력 예:
#   allow agcand agcand:can_socket { create bind };
```

단 audit2allow의 출력을 <strong>그대로 붙여넣으면 안 된다</strong>. 너무 넓게 여는 규칙(예: 와일드카드에 가까운 권한)을 뱉기도 하고, neverallow를 위반하는 규칙을 제안하기도 한다. 출력은 "이 방향으로 열어야 한다"는 힌트로 보고, 최소 권한으로 다듬어 `.te`에 반영한다.

실전 워크플로는 <strong>"permissive로 열고 → 전체 denial 수집 → 정책 반영 → enforcing으로 조이기"</strong> 순서다. 개발 초기엔 데몬 도메인만 permissive로 두고 모든 denial을 한 번에 긁어낸다.

```
# 개발 중에만: agcand 도메인을 permissive로 (이 도메인만 로그만 남기고 통과)
permissive agcand;
```

이렇게 두면 데몬이 정상 동작하면서 필요한 denial이 <strong>전부 로그로</strong> 나온다. 그걸 모아 정책에 반영한 뒤, `permissive agcand;` 줄을 지워 다시 enforcing으로 돌린다. 양산 이미지에는 절대 permissive 도메인을 남기면 안 된다 — CTS/보안 검증에서 걸린다.

<strong>더 빠른 임시 방법 — setenforce 0.</strong> `permissive agcand;`은 정책을 고쳐 재빌드·재플래시해야 한다. 개발 중 처음 데몬을 올려 "어떤 denial이 나는지 일단 다 보고 싶을" 때는, userdebug 이미지에서 <strong>시스템 전체를 런타임에 permissive로</strong> 돌리는 게 더 빠르다.

```bash
adb root                       # userdebug에서만 됨 (user 빌드는 불가)
adb shell setenforce 0         # 전체 SELinux를 permissive로 (재부팅 전까지)
adb shell getenforce           # Permissive 확인

# 이제 데몬을 실행/재시작하고 정상 동작에 필요한 denial을 전부 수집
adb shell start agcand
adb shell dmesg | grep 'avc: denied' > denials.txt

adb shell setenforce 1         # 다시 enforcing으로 (또는 재부팅)
```

`setenforce 0`은 <strong>차단은 멈추되 denial 로그는 그대로 남기므로</strong>, 데몬을 끝까지 정상 동작시키면서 필요한 모든 규칙을 한 번에 긁어낼 수 있다. 그 로그로 `.te`를 작성한 뒤 `setenforce 1`로 돌려 검증한다. 단 이건 <strong>userdebug 전용</strong>이고(user 빌드는 `adb root`·`setenforce`가 막혀 있다), 재부팅하면 원래대로 enforcing으로 복귀한다. 즉 "정책을 임시로 끄는 개발용 스위치"일 뿐 영구 설정이 아니다.

<strong>neverallow 위반</strong>으로 빌드가 깨질 때가 있다. 이건 런타임 denial이 아니라 컴파일 에러다.

```
libsepol.report_failure: neverallow on line 1234 ...
  violated by allow agcand proc:file { read };
```

대처는 셋 중 하나다. (1) 정말 그 권한이 필요 없다면 규칙을 뺀다. (2) 더 좁은 대상 타입으로 바꿔 neverallow에 안 걸리게 한다(예: `proc` 전체가 아니라 특정 `proc_xxx` 타입만). (3) 그 동작이 근본적으로 잘못된 접근이라는 신호이므로 데몬 설계를 바꾼다. neverallow는 대부분 (2)나 (3)으로 풀어야 하고, 억지로 우회하면 보안 모델을 스스로 무너뜨리는 것이다.

## Verified Boot(AVB)

정책까지 통과해 데몬이 뜨면, 이제 이 커스텀 이미지를 실제 보드에 flash해야 한다. 여기서 <strong>AVB(Android Verified Boot)</strong>가 막아선다. AVB는 부팅되는 모든 파티션이 <strong>변조되지 않았음을 암호학적으로 검증</strong>하는 체계다.

![락된 부트로더가 공개키로 vbmeta 서명을 검증하고, vbmeta의 디스크립터가 boot.img·system·vendor 각 파티션의 해시(dm-verity hashtree)를 검증하는 AVB 신뢰 체인](/images/study-android-internals/16-avb-chain-light.png)
![락된 부트로더가 공개키로 vbmeta 서명을 검증하고, vbmeta의 디스크립터가 boot.img·system·vendor 각 파티션의 해시(dm-verity hashtree)를 검증하는 AVB 신뢰 체인](/images/study-android-internals/16-avb-chain-dark.png)

핵심 부품은 둘이다.

<strong>dm-verity</strong> — system·vendor 같은 읽기 전용 파티션의 무결성을 <strong>해시 트리</strong>로 보장한다. 파티션을 블록 단위로 해시하고, 그 해시들을 다시 해시해 트리를 만들면 최상단에 <strong>root hash</strong> 하나가 남는다. 커널의 device-mapper가 블록을 읽을 때마다 해시를 재계산해 트리와 대조하고, 하나라도 어긋나면 읽기를 실패시킨다. 즉 파티션 어디를 한 바이트만 바꿔도 root hash가 달라져 부팅이 막힌다.

<strong>vbmeta</strong> — 이 root hash들과 파티션 메타데이터를 담고 <strong>서명된</strong> 파티션이다. vbmeta 안에는 각 파티션에 대한 <strong>디스크립터</strong>가 들어 있다. boot.img처럼 통째로 해시하는 것은 hash 디스크립터로, system/vendor처럼 dm-verity를 쓰는 것은 hashtree 디스크립터로 기술한다.

신뢰 체인은 이렇게 흐른다. <strong>락된 부트로더</strong>가 기기에 박힌 공개키(ROT, Root of Trust)로 <strong>vbmeta의 서명</strong>을 검증한다. vbmeta가 진짜임이 확인되면, vbmeta 안의 디스크립터에 든 해시로 boot·system·vendor를 검증한다. 부트로더가 vbmeta를 믿고, vbmeta가 나머지 파티션을 보증하는 <strong>연쇄</strong>다. 하나라도 서명·해시가 안 맞으면 부팅이 중단된다.

<strong>rollback index</strong>는 다운그레이드 공격을 막는다. vbmeta에 롤백 인덱스(버전 번호 비슷한 것)를 넣고, 기기의 안전한 저장소에 마지막으로 본 최댓값을 기록한다. 공격자가 예전의 취약한(그러나 정상 서명된) 이미지로 되돌리려 해도, 롤백 인덱스가 기기 기록보다 낮으면 부팅을 거부한다.

## 커스텀 이미지 개발 시의 AVB

문제는 <strong>우리가 만든 이미지는 구글 키로도, 기기 제조사 키로도 서명돼 있지 않다</strong>는 점이다. 락된 부트로더는 우리 vbmeta를 검증하지 못해 부팅을 거부한다. 개발 단계에서 이걸 넘는 방법이 둘이다.

<strong>1. verity/verification 비활성화.</strong> 개발용으로 vbmeta를 만들 때 검증 플래그를 꺼서, 부트로더가 해시·서명 검증을 건너뛰게 한다. `avbtool`로 vbmeta를 만들거나 flash할 때 플래그를 준다.

```bash
# vbmeta 이미지에 검증/verity 비활성 플래그를 넣어 생성
avbtool make_vbmeta_image \
    --flags 3 \
    --output vbmeta.img
# flags 3 = AVB_VBMETA_IMAGE_FLAGS_VERIFICATION_DISABLED(2)
#          | AVB_VBMETA_IMAGE_FLAGS_HASHTREE_DISABLED(1)

# flash 시점에 비활성 플래그를 주는 방법도 있다
fastboot --disable-verity --disable-verification flash vbmeta vbmeta.img
```

`--disable-verity`는 dm-verity(해시트리 검증)를, `--disable-verification`은 vbmeta 서명 검증을 끈다. 개발 중에는 대개 둘 다 끈다. 그래야 서명 안 된 커스텀 system/vendor로 부팅된다.

<strong>2. 커스텀 키로 재서명하고 부트로더에 등록.</strong> 좀 더 제대로 된 방법이다. 자체 서명 키를 만들어 vbmeta를 서명하고, 그 공개키를 부트로더에 등록(디바이스에 따라 `avb_custom_key`)한다. 그러면 락 상태에서도 우리 이미지를 정상 검증한다. 양산에 가까운 임베디드 제품이라면 이 방향으로 간다.

```bash
# 커스텀 키로 vbmeta 서명
avbtool make_vbmeta_image \
    --key custom_rsa4096.pem --algorithm SHA256_RSA4096 \
    --include_descriptors_from_image system.img \
    --include_descriptors_from_image vendor.img \
    --output vbmeta.img

# 부트로더에 공개키 등록 (기기별 절차)
fastboot flash avb_custom_key custom_pubkey.bin
```

<strong>락 상태와의 관계</strong>가 중요하다. 부트로더는 <strong>unlocked</strong>과 <strong>locked</strong> 상태를 갖는다.

- <strong>unlocked</strong> — AVB 검증 실패를 경고만 하고 부팅을 허용한다(대개 경고 화면이 뜬다). 개발 중에는 부트로더를 unlock해두고 verity/verification을 꺼서 빠르게 반복한다.
- <strong>locked</strong> — 검증 실패 시 부팅을 <strong>거부</strong>한다. 여기서는 커스텀 키를 등록해 우리 서명이 통과되게 해야만 부팅된다. 보안이 필요한 양산 제품의 최종 상태다.

개발 흐름은 "unlock + verity/verification off로 빠르게 개발 → 안정화되면 커스텀 키 재서명 + lock으로 보안 확보"가 표준이다.

::: warning verity를 끈 채로 양산하지 마라
`--disable-verity`/`--disable-verification`은 개발 편의용이다. 이 상태로 출하하면 누구든 파티션을 변조해도 기기가 그대로 부팅한다 — 무결성 보증이 통째로 사라진다. 임베디드 농기계처럼 물리적 접근이 가능한 환경일수록 최종 이미지는 커스텀 키 재서명 + locked 상태로 가야 한다.
:::

## FBE 키와 Keymint 한 줄 개요

무결성(AVB)과 짝을 이루는 것이 <strong>기밀성</strong>이다. 안드로이드는 <strong>FBE(File-Based Encryption)</strong>로 `/data`를 파일 단위로 암호화하고([CH5](/study/android-internals/05-storage-management) 참고), 그 암호화 키는 <strong>Keymint</strong>(과거 Keymaster)가 TEE/Secure Element 같은 하드웨어 보안 환경 안에서 관리한다. 즉 AVB가 "부팅 코드가 진짜인가"를, FBE+Keymint가 "저장 데이터가 안전한가"를 담당한다. 두 주제는 각각 스토리지·보안 챕터에서 더 깊게 다룬다.

::: tip 핵심 정리
- SELinux는 DAC 위에 강제되는 MAC이다. TE(Type Enforcement) 모델로 프로세스(도메인)와 객체(타입)에 라벨을 붙이고 "허용한 것만 통과"시킨다. 안드로이드는 5.0부터 전면 enforcing이다.
- Treble로 정책이 platform(system/sepolicy)과 vendor(device/.../sepolicy, BOARD_VENDOR_SEPOLICY_DIRS)로 분리되고, CIL로 컴파일돼 부팅 시 secilc가 결합한다. neverallow는 vendor가 넘으면 빌드를 깨는 안전선이다.
- vendor 데몬 도메인은 agcand.te(init_daemon_domain·can_socket·binder·capability)와 file_contexts(실행 파일·소켓 라벨)로 만든다. 도메인 전이가 안 되면 file_contexts 누락을 먼저 의심한다.
- 유닉스 도메인 소켓은 connectto 퍼미션으로 접근을 통제한다. 붙어도 되는 도메인만 allow에 나열하면(예: 시스템 서비스만) 앱은 자동 차단된다 — allow로 적지 않은 것은 전부 거부되는 화이트리스트 원칙이다.
- denial은 avc 로그의 { perm }·scontext·tclass로 읽는다. userdebug에서 adb root + setenforce 0으로 전체를 임시 permissive로 돌려 denial을 전부 수집 → audit2allow를 힌트 삼아 최소 권한으로 반영 → setenforce 1/enforcing으로 조인다. neverallow 위반은 우회가 아니라 좁히기·재설계로 푼다.
- AVB는 dm-verity(해시트리) + 서명된 vbmeta로 부트로더→vbmeta→파티션의 신뢰 체인을 만든다. 커스텀 이미지는 개발 중 --disable-verity/--disable-verification로 넘기고, 최종엔 커스텀 키 재서명 + locked로 간다. rollback index가 다운그레이드를 막는다.
:::

## 다음 챕터

[CH17. 패키지 관리](/study/android-internals/17-package-management)에서는 시선을 다시 위로 올려, APK가 어떻게 설치·검증·서명되고 PackageManager가 앱의 생애주기를 어떻게 관리하는지를 다룬다.
