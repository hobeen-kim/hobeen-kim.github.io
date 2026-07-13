---
title: "CH10. 설정과 관리"
description: "멀티 유저 uid 모델부터 config.xml·RRO·CarrierConfig·settings·device_config·sysconfig까지, 안드로이드가 설정값을 층층이 쌓아 실효값을 만드는 구조와 커스텀 기기에서 시스템 앱 권한을 부여하는 법을 다룬다."
date: 2026-07-13
tags: [android, aosp, configuration, settings, sysconfig]
---

# CH10. 설정과 관리

안드로이드에서 "설정"은 하나의 파일이 아니다. 빌드타임 리소스, 벤더 오버레이, 통신사 값, 런타임 데이터베이스, 원격 플래그, 권한 allowlist가 층층이 쌓여 하나의 실효값을 만든다. 이 계층을 모르면 "분명 config를 고쳤는데 왜 안 먹지"라는 함정에 빠진다. 커스텀 임베디드 장비를 만들 때는 특히 마지막 절의 sysconfig가 시스템 앱 권한 부여의 핵심이 된다.

## 학습 목표
- 멀티 유저 구조에서 uid가 userId와 appId로 어떻게 조합되는지 이해한다.
- config.xml·RRO·CarrierConfig가 이루는 설정의 계층과 오버라이드 순서를 파악한다.
- settings 서비스의 system/secure/global 테이블과 `settings` 명령 사용법을 익힌다.
- device_config·aconfig로 이어지는 원격 플래그 시스템을 안다.
- sysconfig의 allowlist로 커스텀 기기에서 시스템 앱에 권한을 부여하는 법을 익힌다.

## 멀티 유저 구조 — userId와 appId

안드로이드는 로우엔드부터 태블릿까지 하나의 사용자가 아니라 여러 사용자를 담을 수 있게 설계됐다. 이 멀티 유저 모델은 uid를 두 부분으로 쪼개는 것으로 구현된다.

![멀티 유저 uid 모델 — uid는 userId×100000 + appId로 계산되며 같은 appId라도 userId가 다르면 서로 다른 uid가 되어 데이터가 격리된다](/images/study-android-internals/10-uid-model-light.png)
![멀티 유저 uid 모델 — uid는 userId×100000 + appId로 계산되며 같은 appId라도 userId가 다르면 서로 다른 uid가 되어 데이터가 격리된다](/images/study-android-internals/10-uid-model-dark.png)

리눅스 커널이 보는 것은 오직 `uid` 하나의 32비트 정수다. 안드로이드는 이 값을 두 필드로 해석한다.

```
uid = userId × 100000 + appId
```

- <strong>userId</strong>는 사용자를 식별한다. 첫 사용자(소유자)는 `user 0`, 두 번째로 추가된 사용자는 관례적으로 `user 10`이다.
- <strong>appId</strong>는 앱을 식별한다. 서드파티 앱은 설치 시 `10000`(`Process.FIRST_APPLICATION_UID`)부터 `19999` 범위에서 하나를 배정받는다. 시스템 컴포넌트는 `1000`(system), `1001`(radio), `2000`(shell)처럼 `android_filesystem_config.h`에 고정된 AID를 쓴다.

이 조합이 만드는 결과가 핵심이다. 같은 앱(`appId = 10123`)이라도 `user 0`에서는 `uid = 10123`, `user 10`에서는 `uid = 1010123`이 된다. 커널 입장에서는 완전히 다른 두 사용자이므로, 파일 소유권·프로세스 권한이 자동으로 격리된다. 두 사용자의 같은 앱은 데이터를 절대 공유하지 못한다.

프레임워크에서는 `UserHandle.getUserId(uid)`와 `UserHandle.getAppId(uid)`로 이 두 필드를 역산한다. 명령줄에서는 이렇게 확인한다.

```bash
# 현재 존재하는 사용자 목록
adb shell pm list users
# UserInfo{0:Owner:c13} running
# UserInfo{10:Work profile:1030}

# 특정 앱이 각 사용자에서 어떤 uid를 쓰는지
adb shell dumpsys package com.example.app | grep userId
```

::: info 단일 사용자 임베디드 장비에서의 의미
농기계 단말처럼 사용자를 추가할 일이 없는 장비에서도 멀티 유저 골격은 그대로 살아 있다. 모든 앱이 `user 0`에 속하므로 실질적으로 `uid == appId`처럼 동작하지만, 프레임워크 코드·권한 검사·경로 규칙(`/data/user/0/...`)은 여전히 userId를 전제로 돈다. 그래서 `/data/data`는 사실 `/data/user/0`의 심볼릭 링크다. 멀티 유저를 안 쓴다고 이 구조를 걷어내려 하지 말고, "항상 user 0"이라는 단순화된 형태로 받아들이는 편이 안전하다.
:::

## 계정 관리 — AccountManager

사용자(userId)와 별개로, 각 사용자 안에는 온라인 서비스 계정(구글, 회사 SSO 등)이 붙는다. 이를 관리하는 것이 `AccountManager`와 그 뒤의 `AccountManagerService`다.

계정 정보는 사용자별로 `/data/system_de/<userId>/accounts_de.db`, `/data/system_ce/<userId>/accounts_ce.db`(SQLite)에 저장된다. `ce`(credential encrypted)는 사용자가 화면 잠금을 푼 뒤에야 복호화되고, `de`(device encrypted)는 부팅 직후 접근 가능하다. 계정의 실제 비밀번호가 아니라 인증 토큰(auth token)이 저장되며, 앱은 `AccountManager.getAuthToken()`으로 토큰을 요청한다.

임베디드 장비는 대개 사용자 대면 계정 로그인이 없으므로 AccountManager를 직접 다룰 일은 드물다. 다만 클라우드 연동(예: 텔레메트리 업로드)을 커스텀 authenticator로 붙일 때 이 프레임워크를 재활용할 수 있다는 정도만 알아두면 된다.

## 설정의 계층 — config.xml과 오버레이

프레임워크의 수많은 기본 동작은 `frameworks/base/core/res/res/values/config.xml`에 정의된 리소스로 결정된다. 화면 회전 허용 여부, 기본 볼륨 단계, 지원 네트워크 타입 같은 값이 여기 들어 있다. 문제는 이걸 기기마다 다르게 바꿔야 하는데, AOSP 원본 파일을 직접 고치면 업스트림 병합이 지옥이 된다는 점이다. 그 해법이 오버레이다.

![설정의 계층 — config.xml 빌드타임 기본값 위에 RRO 오버레이·CarrierConfig·settings·device_config가 순서대로 오버라이드하여 실효 설정값을 만들고, sysconfig는 별도로 권한을 부여한다](/images/study-android-internals/10-settings-layers-light.png)
![설정의 계층 — config.xml 빌드타임 기본값 위에 RRO 오버레이·CarrierConfig·settings·device_config가 순서대로 오버라이드하여 실효 설정값을 만들고, sysconfig는 별도로 권한을 부여한다](/images/study-android-internals/10-settings-layers-dark.png)

- <strong>config.xml (빌드타임 기본값)</strong>: `framework-res.apk` 안에 컴파일돼 들어가는 원본 리소스. 안드로이드가 아무 커스텀 없이 갖는 디폴트다.
- <strong>RRO(Runtime Resource Overlay)</strong>: 별도의 오버레이 APK가 런타임에 원본 리소스를 치환한다. `/vendor/overlay`, `/product/overlay`에 놓인 오버레이가 대상 패키지(`android`)의 리소스를 덮어쓴다. 빌드타임 정적 오버레이와 달리 설치·활성화/비활성화가 런타임에 가능하다는 게 핵심이다. RRO의 상세한 매니페스트·`overlayable` 정책·`idmap2`는 [CH17 패키지 관리](/study/android-internals/17-package-management)에서 다룬다.
- <strong>CarrierConfig</strong>: 통신사·SIM별로 달라지는 값(VoLTE 지원, APN 기본값, 긴급번호 등)을 `CarrierConfigManager`가 SIM 정보에 맞춰 로드한다. 셀룰러가 없는 장비에는 무관하다.

RRO 활성화는 `overlay` 명령으로 런타임 제어할 수 있다.

```bash
# 설치된 오버레이 목록과 활성 상태
adb shell cmd overlay list
# [ ] com.android.internal.systemui.navbar.gestural
# [x] com.example.device.overlay        # x면 활성

# 오버레이 켜기/끄기
adb shell cmd overlay enable com.example.device.overlay
adb shell cmd overlay disable com.example.device.overlay
```

커스텀 장비에서는 기기 고유 설정을 담은 RRO 오버레이 APK 하나를 `/product/overlay`에 넣고 빌드에 포함시키는 방식이 표준이다. 이렇게 하면 AOSP 원본은 한 줄도 건드리지 않고 기기 동작을 바꿀 수 있다.

## settings 서비스 — system/secure/global

앞의 계층이 대체로 "빌드·벤더가 정하는 값"이라면, `settings`는 런타임에 바뀌는 사용자·시스템 설정을 담는다. `SettingsProvider`가 관리하며 세 개의 논리 테이블로 나뉜다.

- <strong>system</strong>: 사용자별, 앱이 읽고 쓸 수 있는 UI 성격의 값(화면 밝기, 벨소리 등). 보안 민감하지 않다.
- <strong>secure</strong>: 사용자별, 읽기는 자유롭지만 쓰기는 시스템 권한이 필요한 값(활성 입력기, 접근성 서비스, `android_id` 등).
- <strong>global</strong>: 전 사용자 공통 단일 값(비행기 모드, ADB 활성화, 개발자 옵션 등).

명령줄 실습이 가장 빠르다.

```bash
# 읽기: settings get <namespace> <key>
adb shell settings get global adb_enabled          # 1
adb shell settings get system screen_brightness     # 128
adb shell settings get secure default_input_method

# 쓰기: settings put <namespace> <key> <value>
adb shell settings put global stay_on_while_plugged_in 7   # 충전 중 항상 켜둠
adb shell settings put system screen_off_timeout 2147483647

# 특정 사용자 대상 (멀티 유저)
adb shell settings --user 10 list secure
```

내부적으로 이 값들은 과거에는 SQLite `settings.db`였지만, Android 6.0(M) 이후로는 사용자별 XML 파일(`/data/system/users/<userId>/settings_system.xml` 등)에 저장되고 메모리에 캐시되는 구조로 바뀌었다. 앱은 `Settings.System.getInt()` 같은 API나 `content://settings/...` URI로 접근하며, `SettingsProvider`가 권한 검사와 변경 통지(`ContentObserver`)를 담당한다.

::: warning 임베디드 장비에서 자주 쓰는 값
`stay_on_while_plugged_in`은 상시 전원 장비에서 화면이 꺼지지 않게 하는 대표 값이다. 비트마스크로 AC(1)·USB(2)·무선(4) 충전원을 조합한다. `7`이면 어떤 충전이든 항상 켜둔다. 다만 이건 "화면"만 담당하고, CPU suspend를 막는 건 [CH13 전원 관리](/study/android-internals/13-power-management)의 wakelock 몫이다. 둘을 혼동하면 "화면은 켜졌는데 백그라운드 작업이 멈춘다"는 증상을 만난다.
:::

## device_config와 서버 설정 플래그

`settings global`이 로컬·수동 설정이라면, `device_config`는 구글이 서버에서 원격으로 던지는 기능 플래그를 담는 별도 네임스페이스 시스템이다. Phenotype이라는 백엔드가 A/B 실험이나 단계적 롤아웃을 위해 플래그를 내려보내고, `DeviceConfig` API로 프레임워크·앱이 읽는다.

```bash
# 네임스페이스 목록과 플래그 조회
adb shell device_config list
adb shell device_config list activity_manager
adb shell device_config get activity_manager max_cached_processes

# 로컬 오버라이드 (실험용)
adb shell device_config put activity_manager max_cached_processes 16
```

Android 14(U)부터는 빌드타임 기능 플래그를 위한 <strong>aconfig</strong>가 도입됐다. `device_config`가 런타임에 서버가 던지는 값이라면, aconfig는 소스에 `.aconfig` 파일로 플래그를 선언하고 빌드 설정(release configuration)에 따라 켜고 끄는 컴파일타임 성격이 강하다. 커널의 기능 게이팅처럼, 새 기능을 코드에 넣되 특정 릴리스에서만 활성화하는 용도다.

```bash
# aconfig 플래그 상태 (14+)
adb shell device_config list  # aconfig 플래그도 여기 노출되는 경우가 있음
adb shell dumpsys device_config
```

커스텀 장비에서는 device_config의 원격 소스(Phenotype)에 접근할 일이 없으므로, 대개 로컬 기본값으로 고정하거나 아예 관련 서비스를 비활성화한다. 다만 프레임워크 자체가 이 플래그로 동작을 분기하는 곳이 있으므로, 특정 기능이 예상과 다르게 동작하면 `dumpsys device_config`로 플래그 상태를 먼저 확인하는 습관이 필요하다.

## sysconfig — 권한 allowlist

지금까지가 "값"을 정하는 계층이었다면, `sysconfig`는 "권한"을 정하는 특별한 계층이다. `/etc/sysconfig`, `/vendor/etc/sysconfig`, `/product/etc/sysconfig` 등에 놓인 XML 파일들을 `SystemConfig`가 부팅 시 읽어, 시스템 앱에 부여할 권한·기능을 allowlist 방식으로 확정한다. 커스텀 임베디드 OS를 만들 때 <strong>가장 자주 손대는 파일</strong>이 바로 여기다.

대표적인 allowlist는 이렇다.

- <strong>privapp-permissions</strong>: `/system/priv-app`, `/vendor/priv-app` 등에 놓인 특권 앱(privileged app)이 시그니처/특권 보호 수준의 위험 권한을 받으려면, 여기에 명시적으로 allowlist돼 있어야 한다. 없으면 부팅이 막히거나(강제 정책) 권한이 거부된다.
- <strong>hidden-api-whitelist / allowed-vendor-apis</strong>: 특정 시스템 앱이 hidden API·벤더 API를 쓰도록 허용.
- <strong>allow-in-power-save / allow-in-data-usage-save</strong>: Doze·데이터 절약 모드에서 예외로 둘 앱 지정.
- <strong>feature</strong>: `PackageManager.hasSystemFeature()`가 보고할 하드웨어/소프트웨어 기능(`android.hardware.camera` 등) 선언·제거.

privapp-permissions 파일의 형태는 이렇다.

```xml
<!-- /vendor/etc/sysconfig/com.example.device-permissions.xml -->
<permissions>
    <privapp-permissions package="com.example.device.telemetry">
        <permission name="android.permission.MANAGE_USERS"/>
        <permission name="android.permission.WRITE_SECURE_SETTINGS"/>
        <permission name="android.permission.REBOOT"/>
    </privapp-permissions>
</permissions>
```

이 파일이 없으면, 시스템 파티션에 설치한 특권 앱이 `WRITE_SECURE_SETTINGS` 같은 권한을 요청해도 프레임워크가 거부한다. 심한 경우 `ro.control_privapp_permissions=enforce` 정책이 켜진 기기에서는 <strong>allowlist 누락이 부팅 실패로 이어진다</strong>. 그래서 커스텀 시스템 앱(예: CAN 데이터를 클라우드로 올리는 텔레메트리 앱)을 `/product/priv-app`에 넣을 때는, 그 앱이 요구하는 모든 특권 권한을 sysconfig에 함께 선언하는 것이 필수 절차다.

::: details privapp-permissions 위반 부팅 로그 예시
```
PackageManager: Privileged permission android.permission.MANAGE_USERS
  for package com.example.device.telemetry (/product/priv-app/Telemetry) not
  in privapp-permissions allowlist
```
`ro.control_privapp_permissions`가 `enforce`면 이 로그와 함께 앱이 비활성화되거나 부팅 루프가 발생한다. `log`로 두면 경고만 남기고 통과시키므로, 개발 중에는 `log`로 두고 양산 전에 allowlist를 완성한 뒤 `enforce`로 조이는 흐름이 일반적이다.
:::

이 sysconfig 계층은 [CH16 SELinux와 Verified Boot](/study/android-internals/16-selinux-avb)의 SELinux 정책, [CH17 패키지 관리](/study/android-internals/17-package-management)의 서명·설치 위치와 함께 "커스텀 시스템 앱을 어떻게 신뢰된 컴포넌트로 올릴 것인가"라는 하나의 큰 그림을 이룬다. 네이티브 데몬을 서비스로 올리는 실전 흐름은 [CH23 네이티브 데몬 서비스 만들기](/study/android-internals/23-native-daemon-case-study)에서 종합한다.

::: tip 핵심 정리
- uid는 `userId × 100000 + appId`로 조합되며, 같은 앱이라도 사용자가 다르면 uid가 달라 데이터가 격리된다. 단일 사용자 장비도 "항상 user 0" 형태로 이 골격을 그대로 쓴다.
- 설정은 config.xml(빌드타임) → RRO 오버레이 → CarrierConfig → settings(런타임) → device_config(원격) 순으로 층층이 오버라이드돼 실효값이 된다.
- settings는 system/secure/global 세 네임스페이스로 나뉘고, `settings get/put` 명령으로 즉시 읽고 쓸 수 있다.
- device_config는 원격 기능 플래그, aconfig(14+)는 빌드타임 기능 플래그 시스템이다.
- sysconfig의 privapp-permissions는 커스텀 시스템 앱에 특권 권한을 부여하는 필수 관문이며, 누락 시 권한 거부나 부팅 실패로 이어진다.
:::

## 다음 챕터

[CH11. 리눅스 렌즈로 본 애플리케이션](/study/android-internals/11-linux-lens)에서는 안드로이드 앱을 프레임워크가 아니라 리눅스 프로세스로 내려다본다. `/proc` 훑기, VSS/RSS/PSS/USS 메모리 지표, lmkd의 OOM 처리, cgroup과 태스크 프로파일, ELF 네이티브 바이너리까지 파헤친다.
