---
title: "CH4. 파일과 디렉토리 구조"
description: "system-as-root로 바뀐 루트 파일시스템, /system·/vendor·/data의 내부 구조, 그리고 CE/DE 스토리지와 File-Based Encryption이 부팅 단계별로 어떻게 잠금 해제되는지를 adb 실습과 함께 파고든다."
date: 2026-07-13
tags: [android, aosp, filesystem, directory, fbe, storage]
---

# CH4. 파일과 디렉토리 구조

## 학습 목표
- ramdisk 루트에서 system-as-root로 넘어온 변천과 루트에 남은 심볼릭 링크들의 의미를 이해한다.
- `/system`·`/vendor`의 하위 디렉토리 구조와 둘 사이의 ABI 경계(VNDK)를 파악한다.
- `/data`의 구조와 CE/DE 스토리지, File-Based Encryption의 부팅 단계별 접근 시점을 설명할 수 있다.
- `adb shell`로 디렉토리와 SELinux 컨텍스트를 직접 훑는 명령을 익힌다.

## 루트 파일시스템 — ramdisk에서 system-as-root로

전통적인 리눅스는 부팅 시 커널이 <strong>initramfs</strong>(초기 RAM 파일시스템)를 루트(`/`)로 올리고, 그 안의 `init`이 진짜 루트 파티션을 찾아 마운트한 뒤 `switch_root`로 넘어간다. 안드로이드도 9.0 이전에는 이 방식이었다 — 작은 루트 ramdisk가 `/`가 되고, 그 아래에 `/system`을 별도로 마운트했다.

<strong>system-as-root</strong>(9.0)는 이 구조를 바꿨다. 별도 루트 ramdisk를 없애고 <strong>`system` 파티션 자체를 루트(`/`)로 마운트</strong>한다. 즉 `/`와 `/system`의 내용이 사실상 같아진다. dm-verity로 무결성이 보장되는 read-only `system`을 곧바로 루트로 삼아, 검증되지 않은 ramdisk 루트를 신뢰 사슬에서 제거하려는 목적이었다.

그런데 GKI(Generic Kernel Image, 11+)와 함께 상황이 다시 바뀐다. 커널과 유저스페이스를 분리하면서 <strong>generic ramdisk가 부활</strong>했고, 13.0부터는 이 generic ramdisk가 `init_boot` 파티션에 담긴다. 결과적으로 최신 기기의 부팅 초기 루트는 다시 ramdisk이지만, 이 ramdisk의 `init`이 곧바로 `system`을 마운트하고 넘어가는 흐름은 유지된다. 부팅 관점의 전체 흐름은 [CH7. 부트로더와 커널 부팅](/study/android-internals/07-boot-process)에서 이어간다.

루트에는 실제 디렉토리보다 <strong>심볼릭 링크</strong>가 많다. 역사적 경로 호환을 위해 옛 위치를 새 위치로 이어준다.

```bash
adb shell ls -l /
# bin -> /system/bin
# etc -> /system/etc
# vendor -> /vendor  (또는 super 안 논리 파티션 마운트)
```

`/bin`, `/etc` 같은 전통적 유닉스 경로가 전부 `/system/...`을 가리키는 링크다. 스크립트나 툴이 `/bin/sh`를 기대해도 실제로는 `/system/bin/sh`가 실행된다.

![system-as-root 아래 주요 최상위 디렉토리 트리 — 루트에서 /system·/vendor·/product·/system_ext·/data·/vendor(+odm)로 뻗는 구조와 각 디렉토리 역할](/images/study-android-internals/04-fs-tree-light.png)
![system-as-root 아래 주요 최상위 디렉토리 트리 — 루트에서 /system·/vendor·/product·/system_ext·/data·/vendor(+odm)로 뻗는 구조와 각 디렉토리 역할](/images/study-android-internals/04-fs-tree-dark.png)

## /system — 프레임워크의 집

`/system`은 AOSP 프레임워크와 핵심 런타임이 사는 곳이며 read-only로 마운트된다. 주요 하위 디렉토리는 다음과 같다.

- <strong>/system/bin</strong> — 네이티브 실행 파일. 핵심은 <strong>`toybox`</strong>와 <strong>`toolbox`</strong>다. `ls`·`cat`·`ps` 같은 커맨드가 개별 바이너리가 아니라 이 멀티콜 바이너리로 심볼릭 링크돼 있다. 과거에는 `toolbox`가 주였지만 지금은 대부분 `toybox`가 담당하고, `toolbox`는 안드로이드 고유 명령(`getprop`, `setprop`, `start`, `stop` 등) 위주로 남았다.
- <strong>/system/lib, /system/lib64</strong> — 공유 라이브러리(.so). 32비트는 `lib`, 64비트는 `lib64`에 들어간다. 내부적으로 성격이 나뉜다 — <strong>core</strong>(libc·libm 등 Bionic), <strong>framework</strong>(libandroid_runtime 등 프레임워크 지원), <strong>external</strong>(오픈소스 서드파티 이식본). 링킹 규칙은 `linkerconfig`가 생성하는 `ld.config.txt`가 통제한다([CH5](/study/android-internals/05-storage-management), [CH15](/study/android-internals/15-native-level)).
- <strong>/system/etc</strong> — 설정 파일. `init` 스크립트(`init.rc` 조각), SELinux 정책, 퍼미션 XML, `ld.config.txt` 등.
- <strong>/system/framework</strong> — 프레임워크 자바 코드가 담긴 `.jar`와, ART가 미리 컴파일한 <strong>`boot.art`/`boot.oat`</strong> 같은 부트 이미지. 모든 앱이 공유하는 프레임워크 클래스가 여기 있다([CH20. ART 내부 구조](/study/android-internals/20-art-internals)).
- <strong>/system/priv-app, /system/app</strong> — 선탑재 시스템 앱. <strong>priv-app</strong>은 서명된 권한 있는(privileged) 앱으로, 일반 앱에 허용되지 않는 시그니처/특권 권한을 쓸 수 있다. <strong>app</strong>은 일반 선탑재 앱이다.

```bash
# ls가 실제로 toybox 링크인지 확인
adb shell ls -l /system/bin/ls        # -> toybox
# 특정 라이브러리가 어디 있는지
adb shell ls /system/lib64/ | grep libc
```

## /vendor — 하드웨어 경계

`/vendor`는 SoC·보드 벤더의 영역이다. 구조는 `/system`과 닮았다.

- <strong>/vendor/bin</strong> — 벤더 데몬·실행 파일(HAL 서비스 프로세스 등).
- <strong>/vendor/lib[64]</strong> — 벤더 라이브러리와 HAL 구현 `.so`.
- <strong>/vendor/etc</strong> — 벤더 `init` 스크립트, `fstab.{hardware}`, 벤더 SELinux 정책 조각.
- <strong>/vendor/firmware</strong> — 무선 모뎀·Wi-Fi·GPU 등 디바이스 펌웨어 blob. 커널 드라이버가 로드한다.

`/system`과 `/vendor` 사이에는 엄격한 <strong>ABI 경계</strong>가 있다. Treble의 핵심으로, `vendor` 코드가 `system` 내부 구현에 직접 의존하지 못하게 막아 둘을 독립적으로 갱신할 수 있게 한다. 이 경계를 통과할 수 있는 라이브러리 집합이 <strong>VNDK</strong>(Vendor Native Development Kit)다. VNDK에 속한 안정 ABI 라이브러리만 벤더 프로세스가 `system`에서 빌려 쓸 수 있고, 나머지는 벤더가 `/vendor` 안에 자기 사본을 둬야 한다. 링커는 이 규칙을 namespace로 강제한다([CH15](/study/android-internals/15-native-level)).

농기계용 CAN 데몬처럼 하드웨어(트랜시버)에 붙는 네이티브 서비스는 성격상 `/vendor` 쪽에 두는 것이 Treble 철학에 맞다. 다만 실제 배치는 요구사항에 따라 달라지며, 이 케이스는 [CH23. 네이티브 데몬 서비스 만들기](/study/android-internals/23-native-daemon-case-study)에서 구체적으로 다룬다.

## /data — 사용자와 앱의 영역

`/data`는 유일하게 대규모로 읽기·쓰기되는 파티션이며, 보통 f2fs로 포맷하고 암호화한다. 주요 하위 구조는 다음과 같다.

- <strong>/data/data</strong> — 앱별 프라이빗 데이터 디렉토리(`/data/data/<package>/`). 실제로는 뒤에 설명할 CE 저장소로 심볼릭되며, 멀티유저에서는 `/data/user/<userId>/`가 정식 경로다.
- <strong>/data/app</strong> — 사용자가 설치한 앱의 APK와 네이티브 라이브러리. 각 앱은 `~~random~~/<package>-random/` 형태의 디렉토리에 들어간다([CH17. 패키지 관리](/study/android-internals/17-package-management)).
- <strong>/data/misc</strong> — 시스템 서비스별 잡다한 상태(키스토어, Wi-Fi 설정, 오디오 보정 등). 하위가 서비스 단위로 잘게 나뉜다.
- <strong>/data/system</strong> — 프레임워크 전역 상태. `packages.xml`(설치 앱 DB), 사용자 정보, 권한 부여 기록 등 핵심 메타데이터.
- <strong>/data/vendor</strong> — 벤더 프로세스가 쓰는 가변 데이터. `/data`의 벤더 몫이다.

### CE vs DE — File-Based Encryption 심층

여기가 이 챕터에서 가장 중요한 부분이다. 안드로이드는 7.0부터 <strong>FBE</strong>(File-Based Encryption, 파일 기반 암호화)를 쓴다. 예전 FDE(Full-Disk Encryption)가 파티션 전체를 하나의 키로 통째 암호화한 것과 달리, FBE는 <strong>파일(과 디렉토리)마다 다른 키</strong>로 암호화한다. 이 덕분에 서로 다른 보안 등급의 데이터를 한 파티션 안에서 다르게 보호할 수 있다.

FBE는 저장소를 두 종류로 나눈다.

- <strong>CE</strong>(Credential Encrypted, 자격증명 암호화) — 키가 <strong>사용자 자격증명(PIN·패턴·비밀번호)에서 파생</strong>된다. 사용자가 기기를 잠금 해제하기 전에는 복호화가 불가능하다. 앱의 일반 데이터가 여기 들어가며, 경로는 `/data/user/<userId>/`(≈ `/data/data`)다.
- <strong>DE</strong>(Device Encrypted, 기기 암호화) — 키가 <strong>기기 하드웨어 키에서 파생</strong>되며 사용자 인증과 무관하다. 부팅 직후, 사용자가 잠금 해제하기 전에도 접근 가능하다. 경로는 `/data/user_de/<userId>/`다.

이 구분이 왜 중요한가? <strong>부팅 단계별로 접근 가능한 저장소가 다르기 때문</strong>이다.

![CE/DE 스토리지의 부팅 단계별 잠금 해제 — 부트 초기(키 없음)·Direct Boot(DE 언락)·사용자 인증 후(CE 언락) 3단계와 각 단계에서 접근 가능한 저장 영역](/images/study-android-internals/04-ce-de-light.png)
![CE/DE 스토리지의 부팅 단계별 잠금 해제 — 부트 초기(키 없음)·Direct Boot(DE 언락)·사용자 인증 후(CE 언락) 3단계와 각 단계에서 접근 가능한 저장 영역](/images/study-android-internals/04-ce-de-dark.png)

- <strong>부트 초기</strong> — 어떤 사용자 키도 아직 준비되지 않아 CE·DE 모두 복호화 불가.
- <strong>Direct Boot 단계</strong> — 기기 키로 <strong>DE가 잠금 해제</strong>된다. 사용자가 아직 PIN을 입력하지 않았어도, `directBootAware`로 표시된 앱·서비스는 DE 저장소만으로 동작할 수 있다. 알람 시계, 전화 수신, 접근성 서비스처럼 잠금 화면 전에도 떠야 하는 것들이 대상이다.
- <strong>사용자 인증 후</strong> — 사용자가 PIN/패턴을 입력하면 그 자격증명으로 <strong>CE가 잠금 해제</strong>되고, 일반 앱의 전체 데이터가 열린다. 대부분의 앱은 이 시점부터 정상 동작한다.

<strong>directBootAware</strong>는 앱 매니페스트의 컴포넌트 속성이다. 이 플래그가 붙은 컴포넌트만 Direct Boot 단계에서 실행되며, 그때는 CE 데이터에 접근하면 안 되고 DE 저장소(`context.createDeviceProtectedStorageContext()`)만 써야 한다.

```bash
# CE(자격증명)와 DE(기기) 저장소 경로 비교 (root 필요)
adb shell ls /data/user/0/       # CE — 잠금 해제 후에만 내용이 보인다
adb shell ls /data/user_de/0/    # DE — 부팅 직후에도 접근 가능
# 특정 앱이 directBootAware인지 매니페스트에서 확인
adb shell dumpsys package <package> | grep -i directBoot
```

임베디드 기기라 자동 로그인/무인 부팅이 필요하다면 이 CE/DE 모델을 반드시 이해해야 한다. PIN 없이 부팅해 곧바로 동작해야 하는 데몬·앱은 CE 데이터에 의존할 수 없고 DE 저장소만 써야 한다. 키가 어떻게 관리되고 하드웨어(Keymaster/StrongBox)에 어떻게 묶이는지는 [CH16](/study/android-internals/16-selinux-avb)에서 다룬다.

## /cache와 기타 디렉토리

- <strong>/cache</strong> — 임시·재생성 가능한 데이터. 예전 non-A/B OTA가 다운로드 패키지를 여기 뒀다. A/B 기기에서는 역할이 줄어 없는 경우도 있다.
- <strong>/metadata</strong> — FBE 키 자료와 체크포인트 등, `/data`를 복호화하기 전에 필요한 메타데이터. 파티션 관점은 [CH3](/study/android-internals/03-partitions-filesystems)에서 다뤘다.
- <strong>/mnt</strong> — 각종 런타임 마운트가 붙는 곳. `/mnt/user/`, `/mnt/runtime/` 아래에 앱별로 다른 외부 스토리지 뷰가 mount namespace로 제공된다([CH5](/study/android-internals/05-storage-management)).
- <strong>/storage</strong> — 사용자가 보는 외부 스토리지 경로. `/storage/emulated/0/`가 기본 사용자의 "내장 SD카드"이며, 실제로는 FUSE로 에뮬레이션된 뷰다.

## 실습 — adb로 디렉토리 훑기

디렉토리 구조는 눈으로 직접 봐야 감이 온다. 아래 명령들로 각 영역을 훑어보자.

```bash
# 최상위 트리와 심볼릭 링크 한눈에 보기
adb shell ls -l /

# 파티션이 어디에 어떤 파일시스템으로 마운트됐는지
adb shell mount | grep -E 'system|vendor|product|data'

# /system·/vendor의 실행 파일·라이브러리 살펴보기
adb shell ls /system/bin | head
adb shell ls /vendor/lib64

# SELinux 컨텍스트까지 함께 보기 (-Z)
adb shell ls -Z /system/bin/init
# u:object_r:init_exec:s0 처럼 파일마다 보안 컨텍스트가 붙어 있다
adb shell ls -Z /data/data 2>/dev/null | head
```

`-Z` 옵션으로 나오는 `u:object_r:init_exec:s0` 같은 문자열이 <strong>SELinux 보안 컨텍스트</strong>다. 안드로이드는 파일·프로세스마다 이 라벨을 붙이고, 정책으로 "누가 무엇에 접근할 수 있는지"를 강제한다. 여기서는 "파일마다 이런 라벨이 붙어 있다"는 것만 눈에 익히면 되고, 라벨 체계와 정책의 상세는 [CH16. SELinux와 Verified Boot](/study/android-internals/16-selinux-avb)에서 본격적으로 다룬다.

::: warning /data 접근은 권한이 필요하다
`/data` 하위는 일반 사용자 셸로는 대부분 접근이 막혀 있다. 위 실습 중 상당수는 `adb root`가 가능한 userdebug/eng 빌드에서만 온전히 보인다. 양산(user) 빌드에서는 SELinux와 파일 권한이 이를 강하게 차단한다.
:::

::: tip 핵심 정리
- 9.0의 system-as-root는 `system` 파티션을 곧 루트(`/`)로 마운트했고, GKI(11+)·`init_boot`(13+)로 generic ramdisk가 다시 분리됐다. 루트의 `/bin`·`/etc`는 `/system/...`을 가리키는 심볼릭 링크다.
- `/system`은 toybox/toolbox(bin), core/framework/external로 나뉜 라이브러리(lib64), 프레임워크 jar와 부트 이미지(framework), priv-app/app으로 구성된다.
- `/vendor`는 하드웨어 경계이며 `/system`과의 ABI는 VNDK로 통제된다. 벤더 프로세스는 VNDK 라이브러리만 `system`에서 빌려 쓴다.
- `/data`의 FBE는 파일마다 키가 다르며, CE(자격증명 기반, 잠금 해제 후)와 DE(기기 키 기반, 부팅 직후)로 나뉜다. `directBootAware` 컴포넌트만 Direct Boot 단계에서 DE 저장소로 동작한다.
- `adb shell ls -Z`로 파일마다 붙은 SELinux 컨텍스트를 미리 볼 수 있다. 무인 부팅이 필요한 임베디드 앱은 CE 대신 DE 저장소에 맞춰 설계해야 한다.
:::

## 다음 챕터

[CH5. 스토리지 관리와 APEX](/study/android-internals/05-storage-management)에서는 이 디렉토리들이 마운트되는 메커니즘 자체를 파고든다. loop/bind mount와 mount namespace, `fs_mgr`와 `fstab` 문법, vold·storaged 같은 스토리지 데몬, 그리고 Mainline의 핵심인 APEX 컨테이너의 구조와 활성화 흐름을 다룬다.
