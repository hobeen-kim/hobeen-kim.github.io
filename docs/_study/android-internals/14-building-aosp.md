---
title: "CH14. AOSP 소스 빌드와 device bring-up"
description: "repo·manifest로 AOSP 소스를 받고 Soong/Kati/Ninja 빌드 파이프라인을 이해한 뒤, Android.bp 문법과 lunch 타깃, 그리고 새 임베디드 device 트리를 처음부터 구성하는 device bring-up 전 과정을 다룬다."
date: 2026-07-13
tags: [android, aosp, soong, build, device-bringup]
---

# CH14. AOSP 소스 빌드와 device bring-up

지금까지는 완성된 안드로이드 시스템을 리눅스의 렌즈로 뜯어봤다. 이번 챕터부터는 방향이 바뀐다. 완성품을 분석하는 쪽에서 <strong>직접 만드는 쪽</strong>으로 넘어간다. AOSP 소스를 받아 커스텀 타깃을 세우고, 그 위에 네이티브 데몬을 올리는 전 과정의 첫 관문이 소스 빌드와 device bring-up이다. 농기계용 임베디드 타깃을 만들려면 결국 device 트리를 손으로 짜야 하고, 그 트리가 어떻게 빌드 시스템에 물리는지 알아야 한다.

## 학습 목표

- repo와 manifest로 AOSP 소스를 받고 브랜치·태그 체계를 이해한다.
- AOSP 최상위 디렉토리 구조와 코드 탐색 도구를 파악한다.
- Soong·Kati·Ninja로 이어지는 빌드 파이프라인과 Android.bp 문법을 이해한다.
- envsetup.sh·lunch·m으로 빌드를 실행하고 산출물의 위치를 안다.
- 새 임베디드 device 타깃을 처음부터 구성하는 device bring-up 절차를 익힌다.

## 소스 받기 — repo와 manifest

AOSP는 단일 git 저장소가 아니다. `frameworks/base`, `system/core`, `bionic`, `external/...` 등 <strong>1000개가 넘는 개별 git 프로젝트</strong>의 집합이다. 이걸 한꺼번에 다루려고 구글이 만든 것이 `repo`다. repo는 git 위에 얹힌 파이썬 래퍼로, 여러 저장소를 하나의 워크스페이스로 묶어 동기화한다.

repo가 어떤 프로젝트를 어디에 체크아웃할지는 <strong>manifest</strong>가 결정한다. manifest는 그 자체가 하나의 git 저장소(`platform/manifest`)이고, 핵심 파일은 `default.xml`이다.

```xml
<!-- .repo/manifests/default.xml (발췌) -->
<manifest>
  <remote name="aosp"
          fetch="https://android.googlesource.com/" />
  <default revision="android-16.0.0_r1"
           remote="aosp" sync-j="4" />

  <project path="frameworks/base"
           name="platform/frameworks/base" />
  <project path="system/core"
           name="platform/system/core" />
  <project path="bionic"
           name="platform/bionic"
           groups="pdk" />
  <!-- ... 수백 개 더 ... -->
</manifest>
```

각 `<project>`는 "원격의 어떤 저장소를 로컬 어느 경로에 둘지"를 한 줄로 표현한다. `revision`은 브랜치나 태그를 가리킨다.

소스를 처음 받는 흐름은 다음과 같다.

```bash
# repo 도구 설치
mkdir -p ~/bin && curl https://storage.googleapis.com/git-repo-downloads/repo > ~/bin/repo
chmod +x ~/bin/repo && export PATH=~/bin:$PATH

# 워크스페이스 초기화 — manifest 저장소를 특정 태그로 고정
mkdir aosp && cd aosp
repo init -u https://android.googlesource.com/platform/manifest -b android-16.0.0_r1

# 실제 소스 동기화 (병렬 8, 얕은 히스토리로 용량 절감)
repo sync -c -j8 --no-tags --optimize-fetch
```

`repo sync`는 처음이면 200GB 안팎을 내려받는다. `-c`(current-branch)와 `--no-tags`는 필요 없는 히스토리를 잘라 시간과 용량을 크게 줄인다.

<strong>local manifests</strong>는 실무에서 반드시 쓰게 된다. AOSP 기본 manifest를 건드리지 않고, 사내 저장소나 커스텀 device 트리를 워크스페이스에 추가하고 싶을 때 쓴다. `.repo/local_manifests/` 아래에 XML을 하나 더 놓으면 repo가 default.xml과 병합한다.

```xml
<!-- .repo/local_manifests/agmo.xml -->
<manifest>
  <remote name="agmo" fetch="ssh://git@git.agmo.internal/" />
  <project path="device/agmo/tractor"
           name="device/tractor" remote="agmo" revision="main" />
  <project path="vendor/agmo"
           name="vendor/agmo" remote="agmo" revision="main" />
</manifest>
```

이렇게 두면 `repo sync` 한 번으로 AOSP 소스와 사내 device 트리가 같이 갱신된다. 커스텀 OS를 굴리는 팀은 대부분 이 구조로 CI를 돌린다.

<strong>브랜치·태그 체계</strong>도 알아둬야 한다. AOSP는 릴리스 태그를 `android-<버전>.0.0_r<N>` 형식으로 붙인다. 예를 들어 `android-16.0.0_r1`은 안드로이드 16의 첫 릴리스 스냅샷이고, `_r2`, `_r3`는 이후 보안 패치가 반영된 후속 태그다. 실제 제품을 만들 때는 개발 브랜치(`main` 같은 이동 타깃)가 아니라 <strong>고정 태그</strong>에 물려야 재현 가능한 빌드가 나온다. (14.0 이전에는 태그가 `android-14.0.0_r1`처럼 동일한 규칙이었고, 그 이전 오래된 버전은 `android-4.4_r1`처럼 마이너 표기가 달랐다.)

용량과 시간이 부담되면 <strong>mirror</strong>를 쓴다. `repo init --mirror`로 순수 bare 저장소 집합을 한 번 받아 사내 서버에 두고, 개발자·CI는 그 mirror를 `--reference`로 참조한다. 여러 명이 각자 200GB를 받는 낭비를 없앤다.

```bash
# 사내 mirror 한 벌 구축
repo init -u https://android.googlesource.com/mirror/manifest --mirror
repo sync -j8

# 개발자는 mirror를 참조해 로컬 용량 절감
repo init -u ... --reference=/srv/aosp-mirror
```

## AOSP 프로젝트 투어

소스를 받으면 최상위에 디렉토리 수십 개가 펼쳐진다. 각각의 역할을 알면 코드를 찾을 때 헤매지 않는다.

- <strong>frameworks/</strong> — Java/Kotlin 프레임워크와 시스템 서비스. `frameworks/base`가 핵심으로, ActivityManager·PackageManager·WindowManager 등 대부분의 시스템 서비스와 SDK API가 여기 있다. `frameworks/native`는 SurfaceFlinger·libbinder 같은 네이티브 프레임워크다.
- <strong>system/</strong> — 저수준 유저스페이스 데몬과 라이브러리. `system/core`에 init·libcutils·logd·adbd가, `system/sepolicy`에 SELinux 정책이 있다.
- <strong>packages/</strong> — 기본 탑재 앱(Settings, Launcher, SystemUI 등)과 프로바이더.
- <strong>hardware/</strong> — HAL(Hardware Abstraction Layer) 인터페이스와 기본 구현. `hardware/interfaces`에 AIDL/HIDL HAL 정의가 있다.
- <strong>device/</strong> — 각 device·board별 설정 트리. 우리가 device bring-up에서 직접 짜는 곳이다.
- <strong>vendor/</strong> — 벤더가 제공하는 비공개 바이너리·설정. device와 짝을 이룬다.
- <strong>external/</strong> — 서드파티 오픈소스(libc++, openssl, protobuf 등). C++ CAN 라이브러리를 포팅한다면 대개 여기 아래 새 디렉토리로 들어간다.
- <strong>build/</strong> — 빌드 시스템 그 자체. `build/soong`(Soong 소스), `build/make`(레거시 make·envsetup·lunch)가 있다.
- <strong>prebuilts/</strong> — 미리 빌드된 툴체인(Clang, NDK), 호스트 도구. 소스에서 빌드하지 않고 그대로 쓴다.
- <strong>bionic/</strong> — 안드로이드 libc/libm/libdl. 다음 [CH15](/study/android-internals/15-native-level)의 주제다.
- <strong>art/</strong> — Android Runtime. [CH20](/study/android-internals/20-art-internals)에서 다룬다.

코드가 방대해서 로컬 grep으로는 한계가 있다. <strong>cs.android.com</strong>(Android Code Search)이 사실상 필수 도구다. 심볼 정의·참조를 크로스 레퍼런스로 따라갈 수 있고, 브랜치별로 코드를 볼 수 있다. "이 함수가 어디서 호출되나"를 추적할 때 로컬보다 훨씬 빠르다.

## 빌드 시스템의 진화

AOSP 빌드 시스템은 세 세대를 거쳤고, 지금은 과도기다. 이 역사를 알면 왜 `Android.mk`와 `Android.bp`가 한 트리에 공존하는지 이해된다.

<strong>1세대 — GNU Make.</strong> 초기 안드로이드는 순수 GNU Make로 빌드했다. 각 모듈이 `Android.mk`를 두고 `BUILD_SHARED_LIBRARY` 같은 매크로를 include하는 방식이다. 문제는 트리가 커지면서 make가 <strong>전체 그래프를 파싱하는 데만 수 분</strong>이 걸리게 됐다는 점이다. 증분 빌드조차 느렸다.

<strong>2세대 — Soong.</strong> 구글은 make 파싱 병목을 없애려고 Soong을 도입했다(안드로이드 7~8 무렵). 모듈은 이제 `Android.bp`라는 선언적 파일로 기술한다. Soong(Go로 작성)이 이 `.bp`를 읽어 <strong>Ninja 빌드 파일</strong>을 생성한다. 실제 컴파일은 Ninja가 한다.

그런데 기존 `Android.mk` 수천 개를 하루아침에 못 바꾼다. 그래서 <strong>Kati</strong>가 등장한다. Kati는 GNU Make를 실행하는 대신 <strong>make 파일을 파싱해 Ninja 파일로 변환</strong>하는 도구다. 즉 make의 문법은 유지하되, 실행 엔진만 Ninja로 통일했다.

<strong>3세대 — Bazel 시도와 회귀.</strong> 구글은 한때 전체 빌드를 Bazel로 옮기려 했다(Android Platform Build with Bazel). 하지만 마이그레이션 비용과 생태계 복잡도 때문에 <strong>전면 전환은 사실상 보류·회귀</strong>됐다. 안드로이드 16 시점에도 실전 빌드의 중심은 여전히 Soong + Kati + Ninja다. Bazel은 일부 영역에서 실험적으로만 남아 있다.

![Soong과 Kati가 각각 Android.bp/Android.mk를 파싱해 통합 build.ninja를 만들고 Ninja가 증분 실행해 out/ 이미지 산출물을 만드는 빌드 파이프라인](/images/study-android-internals/14-build-pipeline-light.png)
![Soong과 Kati가 각각 Android.bp/Android.mk를 파싱해 통합 build.ninja를 만들고 Ninja가 증분 실행해 out/ 이미지 산출물을 만드는 빌드 파이프라인](/images/study-android-internals/14-build-pipeline-dark.png)

정리하면 파이프라인은 이렇다. `Android.bp`는 <strong>Soong</strong>이, `Android.mk`는 <strong>Kati(ckati)</strong>가 각각 파싱해 Ninja 파일을 만든다. 둘이 만든 규칙을 하나의 `build.ninja` 그래프로 합치고, <strong>Ninja</strong>가 이 그래프를 증분 실행해 최종 `.img`를 뽑는다. Ninja는 make보다 훨씬 빠르게 "무엇이 바뀌었고 무엇을 다시 만들어야 하는지"를 계산한다.

## Android.bp 문법

`Android.bp`는 JSON에 가까운 선언적 문법이다. 튜링 완전한 로직이 없고(조건 분기·반복이 제한적) 순수하게 모듈을 <strong>기술</strong>만 한다. 로직이 필요하면 Soong 플러그인(Go 코드)이나 `genrule`로 뺀다. 이 제약이 오히려 파싱을 빠르고 예측 가능하게 만든다.

핵심 모듈 타입 몇 가지다.

```bp
// 네이티브 실행 파일 — 데몬을 만들 때 이걸 쓴다
cc_binary {
    name: "agcand",
    srcs: ["main.cpp", "can_socket.cpp"],
    shared_libs: ["liblog", "libbase", "libbinder"],
    static_libs: ["libagisostack"],
    cflags: ["-Wall", "-Werror", "-DAG_ISO_STACK"],
    init_rc: ["agcand.rc"],           // init이 읽을 rc 파일
    vintf_fragments: ["agcand.xml"],  // VINTF 매니페스트 조각
    vendor: true,                        // /vendor 파티션에 설치
}

// 공유 라이브러리
cc_library_shared {
    name: "libcanutil",
    srcs: ["util.cpp"],
    export_include_dirs: ["include"],
    shared_libs: ["liblog"],
    vendor_available: true,
}

// 정적 라이브러리
cc_library_static {
    name: "libagisostack",
    srcs: ["*.cpp"],
    export_include_dirs: ["include"],
}

// 앱(APK)
android_app {
    name: "TractorHmi",
    srcs: ["src/**/*.kt"],
    platform_apis: true,
}
```

실무에서 자주 만지는 속성을 짚자.

- <strong>srcs</strong> — 소스 파일 목록. 글롭(`**/*.cpp`)을 지원한다.
- <strong>shared_libs / static_libs</strong> — 동적·정적 링크할 라이브러리. 네이티브 데몬에서 링커 문제를 겪는다면 대개 여기 설정과 [CH15](/study/android-internals/15-native-level)의 linker namespace가 얽혀 있다.
- <strong>cflags</strong> — 컴파일 플래그. AOSP는 기본적으로 `-Werror`가 엄격하다.
- <strong>init_rc</strong> — 이 모듈이 서비스라면 init에게 어떻게 시작할지 알려주는 `.rc` 파일. [CH8](/study/android-internals/08-init-zygote) 참고.
- <strong>vintf_fragments</strong> — Treble의 VINTF 매니페스트에 이 서비스를 등록하는 조각.
- <strong>vendor: true</strong> — `/system`이 아니라 `/vendor` 파티션에 설치. 벤더 데몬은 거의 항상 이 설정이 필요하다.

`Android.mk`와의 공존은 이렇게 이해하면 된다. 한 트리 안에서 어떤 모듈은 `.bp`로, 어떤 모듈은 `.mk`로 기술돼도 된다. Soong과 Kati가 각자 파싱해 최종 Ninja 그래프에서 합쳐지기 때문이다. 신규 모듈은 `.bp`로 쓰는 것이 원칙이고, 레거시 `.mk`만 남겨둔다.

<strong>외부 C++ 라이브러리 포팅</strong>은 커스텀 OS 작업의 단골 과제다. AgIsoStack++ 같은 CMake 기반 프로젝트를 AOSP 모듈로 올리는 전략은 크게 셋이다.

1. <strong>Android.bp로 재기술(권장).</strong> CMake 빌드를 안 쓰고, 소스만 가져와 `cc_library_static`으로 다시 감싼다. 소스 목록과 include 경로만 옮기면 되고, AOSP 툴체인·sanitizer·VNDK 규칙에 자연스럽게 편입된다. 유지보수가 가장 깔끔하다.
2. <strong>prebuilt로 반입.</strong> 외부에서 미리 빌드한 `.a`/`.so`를 `cc_prebuilt_library`로 등록한다. 소스 공개가 곤란하거나 빌드가 복잡할 때 쓰지만, ABI·아키텍처가 AOSP와 맞아야 한다.
3. <strong>genrule로 CMake 실행.</strong> 빌드 중 CMake를 호출해 산출물을 만든다. 가능은 하지만 hermetic 빌드를 깨기 쉬워 최후의 수단이다.

대개 1번이 정답이다. 라이브러리 소스를 `external/agisostack/`에 두고 `Android.bp`를 손으로 써서 `cc_library_static`으로 만든 뒤, 데몬의 `static_libs`에 이름을 넣는다.

## 빌드 실행

환경 설정은 `envsetup.sh`를 소싱하는 것으로 시작한다. 이 스크립트가 `lunch`, `m`, `mm` 같은 셸 함수를 등록한다.

```bash
source build/envsetup.sh
```

다음은 <strong>lunch</strong>로 빌드 타깃을 고른다. 안드로이드 14부터 lunch 타깃 형식이 바뀌었다. 이제 `TARGET_PRODUCT-TARGET_RELEASE-TARGET_BUILD_VARIANT` 세 부분으로 구성된다.

```bash
# 형식: <product>-<release>-<variant>
lunch aosp_tractor-trunk_staging-userdebug
```

- <strong>product</strong> — 우리가 정의한 제품 이름(`aosp_tractor`).
- <strong>release</strong> — 릴리스 구성(`trunk_staging`, `next` 등). 안드로이드 14에서 도입된 개념으로, 버전별 플래그 집합을 분리한다. (14.0 이전에는 이 부분이 없어 `aosp_tractor-userdebug`처럼 2단이었다.)
- <strong>variant</strong> — `user`(양산·비루팅), `userdebug`(양산과 같되 root·디버그 허용), `eng`(개발자용, 검증 최소). 개발 중에는 `userdebug`가 표준이다.

빌드 명령은 세 층위다.

```bash
m                 # 전체 빌드 (트리 최상위 기준)
mm                # 현재 디렉토리 모듈만 빌드
mmm path/to/dir   # 지정 경로 모듈만 빌드
m agcand       # 특정 모듈만 이름으로 빌드
```

산출물은 `out/target/product/<device>/` 아래에 쌓인다. 핵심만 보면 이렇다.

```
out/target/product/tractor/
├── system.img          # /system 파티션 이미지
├── vendor.img          # /vendor 파티션 이미지
├── boot.img            # 커널 + ramdisk
├── super.img           # 동적 파티션 컨테이너
├── root/               # 루트 파일시스템 스테이징
├── system/             # system 파티션 스테이징(이미지 만들기 전)
└── obj/                # 중간 산출물(.o, .a)
```

<strong>빌드 속도 팁</strong>은 커스텀 OS 개발의 삶의 질을 좌우한다.

- <strong>ccache</strong> — 컴파일 결과를 캐시해 재빌드를 크게 앞당긴다. `export USE_CCACHE=1`과 캐시 크기 설정(`ccache -M 50G`)이면 된다.
- <strong>증분 빌드</strong> — 데몬 하나만 고쳤으면 `m agcand`으로 모듈만 다시 만든다. 전체 `m`은 필요할 때만.
- <strong>병렬도</strong> — Ninja는 코어 수에 맞춰 자동 병렬화한다. RAM이 병목이면 `-j`를 낮춰야 OOM을 피한다.
- <strong>ninja 로그 분석</strong> — 빌드가 느리면 `out/.ninja_log`로 어떤 타깃이 오래 걸리는지 볼 수 있다.

## device bring-up

이제 핵심이다. 새 임베디드 타깃을 만들려면 `device/<vendor>/<board>` 트리를 손으로 구성해야 한다. 예로 `device/agmo/tractor`를 만든다고 하자.

![device/agmo/tractor 아래 AndroidProducts.mk·tractor.mk·BoardConfig.mk·device.mk·sepolicy 각 파일의 역할을 보여주는 device 트리 구성도](/images/study-android-internals/14-device-tree-files-light.png)
![device/agmo/tractor 아래 AndroidProducts.mk·tractor.mk·BoardConfig.mk·device.mk·sepolicy 각 파일의 역할을 보여주는 device 트리 구성도](/images/study-android-internals/14-device-tree-files-dark.png)

<strong>AndroidProducts.mk</strong> — 이 트리가 어떤 제품을 제공하는지 lunch에게 알린다.

```makefile
# device/agmo/tractor/AndroidProducts.mk
PRODUCT_MAKEFILES := \
    $(LOCAL_DIR)/aosp_tractor.mk

COMMON_LUNCH_CHOICES := \
    aosp_tractor-trunk_staging-userdebug \
    aosp_tractor-trunk_staging-user
```

<strong>제품 정의(aosp_tractor.mk)</strong> — 제품에 무엇이 들어가는지 선언한다. 여기서 `inherit-product`로 AOSP 공통 베이스를 상속받는 것이 핵심이다.

```makefile
# device/agmo/tractor/aosp_tractor.mk

# 미니멀 임베디드 베이스 상속 (풀 스택이 아닌 최소 구성)
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_minimal.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/base_vendor.mk)

PRODUCT_NAME    := aosp_tractor
PRODUCT_DEVICE  := tractor
PRODUCT_BRAND   := agmo
PRODUCT_MODEL   := Tractor HMI Unit

# 이 제품에 포함할 모듈 — 우리 데몬을 여기 넣는다
PRODUCT_PACKAGES += \
    agcand \
    libcanutil \
    TractorHmi

# 파일을 이미지의 특정 경로로 복사 (src:dest)
PRODUCT_COPY_FILES += \
    device/agmo/tractor/init.tractor.rc:$(TARGET_COPY_OUT_VENDOR)/etc/init/hw/init.tractor.rc \
    device/agmo/tractor/ueventd.rc:$(TARGET_COPY_OUT_VENDOR)/etc/ueventd.rc
```

`PRODUCT_PACKAGES`는 "빌드해서 이미지에 넣을 모듈 이름"이고, `PRODUCT_COPY_FILES`는 "빌드 없이 파일을 그대로 특정 경로에 복사"다. 데몬 바이너리는 전자로, 설정 파일은 후자로 넣는다.

<strong>BoardConfig.mk</strong> — 하드웨어·파티션·커널 수준 설정이다.

```makefile
# device/agmo/tractor/BoardConfig.mk

TARGET_ARCH             := arm64
TARGET_ARCH_VARIANT     := armv8-a
TARGET_CPU_ABI          := arm64-v8a

# 커널 — prebuilt 이미지 경로 또는 소스 빌드 설정
TARGET_NO_KERNEL        := false
BOARD_KERNEL_CMDLINE    := console=ttyS0,115200 androidboot.hardware=tractor

# 파티션 크기 (동적 파티션 super 사용)
BOARD_SUPER_PARTITION_SIZE       := 4294967296
BOARD_VENDORIMAGE_FILE_SYSTEM_TYPE := ext4

# 우리 vendor sepolicy 디렉토리 등록 — CH16에서 상세히 다룬다
BOARD_VENDOR_SEPOLICY_DIRS += device/agmo/tractor/sepolicy
```

여기서 <strong>BOARD_VENDOR_SEPOLICY_DIRS</strong>가 [CH16](/study/android-internals/16-selinux-avb)으로 이어지는 연결점이다. 벤더 데몬을 올리면 SELinux 정책을 이 디렉토리에 써넣어야 부팅이 막히지 않는다.

<strong>상속 구조(inherit-product)</strong>가 device bring-up의 뼈대다. 밑바닥부터 다 쓰는 게 아니라, AOSP가 제공하는 베이스 제품 makefile을 상속받고 필요한 것만 덧붙인다. 계층은 대략 이렇다.

- `core_minimal.mk` / `mainline_system.mk` — 부팅에 필요한 최소 시스템 구성.
- `base_vendor.mk` — vendor 파티션의 공통 구성.
- 그 위에 우리 `aosp_tractor.mk`가 device 고유 패키지·설정을 얹는다.

미니멀 임베디드 타깃의 요령은 <strong>풀 스택 제품(aosp_arm64 등)을 상속하지 않는 것</strong>이다. Launcher·Dialer 같은 폰 앱이 필요 없으니 `core_minimal` 계열에서 출발해 HMI에 필요한 것만 추가한다. 이미지가 훨씬 작아지고 부팅도 빨라진다.

트리를 다 짰으면 빌드는 앞 절과 같다.

```bash
source build/envsetup.sh
lunch aosp_tractor-trunk_staging-userdebug
m
# → out/target/product/tractor/*.img 생성
```

## 커널 config와 드라이버

device 트리를 짜도 <strong>커널이 그 기능을 지원하지 않으면</strong> 소용없다. CAN 통신이 대표적이다. 리눅스 커널의 SocketCAN 서브시스템은 기본 defconfig에서 꺼져 있는 경우가 많아, 명시적으로 켜야 `socket(AF_CAN, ...)`이 동작한다.

커널 기능은 <strong>config 심볼</strong>로 켜고 끈다. 기준이 되는 것이 `defconfig`(디폴트 config 스냅샷)이고, 그 위에 부분 변경을 얹는 것이 <strong>fragment</strong>다. CAN을 켜는 fragment는 이렇게 생겼다.

```
# device/agmo/tractor/kernel/tractor_can.fragment
CONFIG_CAN=y            # SocketCAN 코어
CONFIG_CAN_RAW=y        # AF_CAN raw 소켓 (agcand이 여는 소켓)
CONFIG_CAN_VCAN=y       # 가상 CAN 인터페이스 (호스트 테스트용 vcan0)
CONFIG_CAN_J1939=y      # J1939 프로토콜 스택 (농기계 ISOBUS 계열)
CONFIG_CAN_DEV=y        # CAN 디바이스 드라이버 프레임워크
# 실제 트랜시버 드라이버 (보드에 맞게)
CONFIG_CAN_MCP251XFD=m  # 예: SPI 연결 MCP2518FD 컨트롤러
```

각 심볼의 값 `y`(커널에 내장), `m`(모듈로 빌드), `n`(끔)의 구분이 실무에서 중요하다. `=y`는 커널 이미지 안에 박히고, `=m`은 `.ko` 파일로 따로 빠져 런타임에 `insmod`/`modprobe`로 올린다.

여기서 <strong>GKI(Generic Kernel Image)</strong> 환경이냐 아니냐로 작업이 갈린다.

- <strong>GKI + vendor 모듈.</strong> 안드로이드 11부터 구글은 커널을 <strong>GKI(공통 코어)</strong>와 <strong>vendor 모듈</strong>로 분리했다. 부팅에 쓰는 코어 커널(`boot.img`)은 구글이 서명한 GKI를 그대로 쓰고, 보드 고유 드라이버는 `vendor_boot.img`/`vendor_dlkm` 파티션에 <strong>커널 모듈(.ko)</strong>로 넣는다. 이 경우 코어 커널을 재빌드하지 않고, CAN 트랜시버 드라이버 같은 것을 `=m`으로 빌드해 vendor 모듈로 추가한다. GKI를 유지하면 구글의 커널 보안 업데이트를 그대로 받는 이점이 있다.
- <strong>커널 재빌드.</strong> `CONFIG_CAN` 같은 <strong>서브시스템 자체를 켜야</strong> 하는데 GKI가 그걸 `=n`으로 뒀다면, 커널을 직접 빌드해야 한다. 커스텀 임베디드 보드는 대개 GKI를 벗어나 자체 커널을 굴리므로 이 경로가 흔하다. 커널 소스에서 fragment를 병합해 config를 만들고, 그 커널을 `boot.img`에 넣는다.

```bash
# 커널 소스에서 defconfig + fragment 병합
cd kernel && \
  ./scripts/kconfig/merge_config.sh \
    arch/arm64/configs/tractor_defconfig \
    ../device/agmo/tractor/kernel/tractor_can.fragment
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-android- -j$(nproc)
# 산출 Image를 AOSP 빌드가 boot.img로 패키징
```

<strong>어떤 config가 켜졌는지 확인</strong>은 부팅한 기기에서 바로 된다.

```bash
adb shell zcat /proc/config.gz | grep CONFIG_CAN
# CONFIG_CAN=y / CONFIG_CAN_RAW=y ... 가 보이면 성공
```

이게 안 보이면 [CH15](/study/android-internals/15-native-level)에서 strace로 잡은 `socket(AF_CAN,...) = -1 EAFNOSUPPORT`(SELinux의 EACCES와는 다르다)를 만나게 된다. SocketCAN 프로그래밍 자체는 [CAN 스터디 CH13](/study/can/13-socketcan-basics)에서 다룬다.

## CAN 커널 드라이버와 SocketCAN 경계

config를 켜는 것으로 작업은 끝나지만, 그 아래에서 무슨 일이 벌어지는지 알아야 <strong>보드가 바뀌었을 때 무엇을 다시 해야 하는지</strong>를 판단할 수 있다. 커널의 CAN 수신 경로를 따라가 보면 칩셋 종속 코드와 공통 코드의 경계가 정확히 보인다.

![CAN 수신 경로 — CAN 버스에서 컨트롤러 mailbox, 칩셋별 드라이버(flexcan 등)까지는 보드 종속이고, struct can_frame으로 변환된 뒤 SocketCAN 코어(af_can)와 agcand의 read()까지는 모든 보드에서 동일한 구조](/images/study-android-internals/14-can-rx-path-light.png)
![CAN 수신 경로 — CAN 버스에서 컨트롤러 mailbox, 칩셋별 드라이버(flexcan 등)까지는 보드 종속이고, struct can_frame으로 변환된 뒤 SocketCAN 코어(af_can)와 agcand의 read()까지는 모든 보드에서 동일한 구조](/images/study-android-internals/14-can-rx-path-dark.png)

수신 흐름은 다섯 단계다. CAN 프레임이 버스에 도착하면 ① 컨트롤러가 <strong>IRQ</strong>를 올리고, ② 드라이버가 컨트롤러의 mailbox <strong>레지스터에서 프레임을 읽어</strong>, ③ 표준 구조체 `can_frame`으로 변환해 skb에 담고, ④ `netif_receive_skb()`로 SocketCAN 코어(`net/can/af_can.c`)에 올리면, ⑤ raw/j1939 소켓 매칭을 거쳐 유저스페이스의 `read()`가 깨어난다.

이 중 ①~②가 칩셋 종속 코드다. NXP i.MX의 flexcan 드라이버를 단순화한 수신부를 보면, 레지스터 접근이 얼마나 칩에 묶여 있는지 드러난다.

::: details flexcan 수신부 단순화 (drivers/net/can/flexcan/flexcan-core.c 기반)
```c
// mailbox 레지스터에서 프레임을 꺼내 can_frame으로 변환
static struct sk_buff *flexcan_mailbox_read(struct can_rx_offload *offload,
                                            unsigned int n, u32 *timestamp)
{
    struct flexcan_mb __iomem *mb = flexcan_get_mb(priv, n);
    struct sk_buff *skb;
    struct can_frame *cf;

    u32 reg_ctrl = priv->read(&mb->can_ctrl);
    u32 reg_id   = priv->read(&mb->can_id);      // 하드웨어 레지스터에서 CAN ID

    skb = alloc_can_skb(offload->dev, &cf);       // 표준 can_frame용 skb 할당

    // 레지스터 값 → can_frame 변환. 여기서부터 하드웨어 독립 표현이 된다
    if (reg_ctrl & FLEXCAN_MB_CNT_IDE)
        cf->can_id = (reg_id & CAN_EFF_MASK) | CAN_EFF_FLAG;   // 29비트 확장 ID
    else
        cf->can_id = (reg_id >> 18) & CAN_SFF_MASK;            // 11비트 표준 ID

    cf->len = can_cc_dlc2len((reg_ctrl >> 16) & 0xf);
    *(__be32 *)(cf->data + 0) = cpu_to_be32(priv->read(&mb->data[0]));
    *(__be32 *)(cf->data + 4) = cpu_to_be32(priv->read(&mb->data[1]));

    return skb;   // netif_receive_skb()를 거쳐 SocketCAN 코어로
}
```
:::

경계가 되는 구조체가 `<linux/can.h>`의 `can_frame`이다. 이 변환이 일어나는 순간부터 하드웨어 정보는 완전히 사라지고, 유저스페이스(agcand)는 칩이 뭐든 동일한 코드로 받는다.

```c
struct can_frame {
    canid_t can_id;   /* 11/29비트 ID + EFF/RTR/ERR 플래그 */
    __u8    len;
    __u8    data[8] __attribute__((aligned(8)));
};
```

계층별로 <strong>무엇이 보드·칩셋에 따라 바뀌고 무엇이 불변인지</strong>를 정리하면 이렇다.

| 계층 | 보드·칩셋별로 바뀌나 | 무엇이 바뀌나 |
|---|---|---|
| 앱 / AIDL 서비스 / agcand | 불변 | — |
| SocketCAN 코어 (af_can, raw, j1939) | 불변 | 커널 공통 코드 |
| <strong>CAN 컨트롤러 드라이버</strong> | <strong>칩마다 교체</strong> | flexcan(i.MX) vs m_can(Bosch IP, Rockchip 등) vs mcp251x(SPI 외장) — 레지스터 맵·mailbox 구조가 전부 다름 |
| <strong>Device Tree</strong> | <strong>보드마다 교체</strong> | 같은 칩이라도 핀 배치·클럭·트랜시버 제어가 보드 배선에 따라 다름 |
| 커널 config | 프로젝트 선택 | 어느 드라이버 심볼을 켤지 (`CONFIG_CAN_FLEXCAN` vs `CONFIG_CAN_M_CAN` 등) |
| 트랜시버 하드웨어 | 보드마다 교체 | 순수 회로 — 커널은 standby 핀 GPIO 정도만 안다 |

즉 <strong>칩셋 종속성은 전부 BSP(드라이버 + Device Tree) 안에 격리</strong>되고, SocketCAN 위의 산출물은 이식 비용이 사실상 0이다. 보드를 i.MX8에서 RK3588로 바꿔도 `can0`이라는 인터페이스 이름과 `can_frame` 포맷은 그대로다. 앞의 보드 선정 체크리스트에 "CAN이 SocketCAN으로 노출되는가"를 넣는 이유가 이것이다. 참고할 실제 소스는 `drivers/net/can/flexcan/`, `drivers/net/can/m_can/`, `drivers/net/can/spi/mcp251x.c`, 그리고 공통 계층 `net/can/`이다.

### USB-CAN 어댑터도 SocketCAN이다

보드에 CAN 핀이 없거나 개발 PC에서 실물 버스를 관찰하고 싶을 때는 USB-CAN 어댑터를 쓴다. 이것도 결국 SocketCAN 드라이버라서, 커널에 드라이버만 켜져 있으면 꽂는 순간 `can0`이 생긴다.

| 드라이버 | 대상 어댑터 | 비고 |
|---|---|---|
| `gs_usb` | candleLight 펌웨어 계열 (CANable 2.0, Innomaker USB2CAN 등) | <strong>추천.</strong> 순수 커널 드라이버, 유저스페이스 데몬 불필요, 저가 |
| `peak_usb` | PEAK PCAN-USB | 산업 표준, 고가 |
| `kvaser_usb` | Kvaser 계열 | 산업 표준, 고가 |
| `slcan` | 시리얼 기반 저가 어댑터 | slcand 데몬이 필요해 안드로이드에선 번거로움 — 비추천 |

안드로이드에서 쓰려면 fragment에 `CONFIG_CAN_GS_USB=y`(또는 `=m`)를 추가하면 된다. 한 가지 실무 함정 — 안드로이드 이미지에는 `ip`(iproute2 full)나 `can-utils`가 기본으로 없어서, bitrate 설정(`ip link set can0 up type can bitrate 250000`)을 셸에서 못 할 수 있다. 해법은 둘이다: iproute2·can-utils를 `PRODUCT_PACKAGES`로 이미지에 넣거나, <strong>agcand가 기동 시 netlink(libsocketcan)로 직접 인터페이스를 올리게</strong> 하는 것이다. 후자가 제품에서는 더 깔끔하다.

## BSP 통합

실무에서는 커널·드라이버·부트로더를 처음부터 만들지 않는다. SoC 벤더나 보드 제조사가 주는 <strong>BSP(Board Support Package)</strong>를 받아 통합한다. BSP는 대략 이런 것들의 묶음이다.

- <strong>부트로더</strong> — U-Boot·ABL 등 보드용 부트로더 소스/바이너리.
- <strong>보드 커널과 드라이버</strong> — 해당 SoC·보드에 맞춘 커널 소스와 드라이버.
- <strong>Device Tree(DTB)</strong> — 보드의 하드웨어 구성(어떤 버스에 어떤 칩이 붙었는지)을 기술한 트리.
- <strong>HAL·펌웨어 blob</strong> — GPU·모뎀·카메라 등의 비공개 HAL 구현과 펌웨어 바이너리.

<strong>전달 형태</strong>는 벤더마다 다르지만 보통 둘 중 하나다. repo manifest XML(벤더 git 서버를 가리키는 방식 — NXP i.MX가 "AOSP + i.MX 패치"를 이렇게 배포한다)이거나, 수십 GB짜리 SDK tarball(Rockchip 방식)이다. 어느 쪽이든 받아서 `repo sync`(또는 압축 해제) → `lunch <보드타깃>` → `m` 하면 <strong>그 보드에서 부팅되는 이미지가 나오는 것</strong>이 BSP의 존재 이유다. "BSP를 준다"를 계약 관점으로 번역하면, 보드값에 "이 보드에서 부팅되는 안드로이드 소스 트리 + 바이너리 + 문서 + (기간 한정) 기술지원이 포함된다"는 뜻이다. 맨 AOSP는 그 보드의 부트로더도, 핀 배치를 아는 Device Tree도, 드라이버도 없어서 부팅조차 안 된다 — BSP가 그 "부팅되는 기준선"을 제공하고, 우리는 그 위에 증축만 한다.

::: warning BSP의 세 가지 현실
- <strong>버전 고정</strong> — BSP는 특정 안드로이드 버전 + 특정 커널 버전에 묶여 있다. "Android 13용 BSP"를 받았는데 16으로 올리는 건 벤더가 새 BSP를 내주지 않는 한 사실상 불가능하다. 보드 선정 시 "어느 버전 BSP를 언제까지 지원하나"를 반드시 확인해야 하는 이유다.
- <strong>품질 편차</strong> — NXP·Qualcomm급 대형 벤더는 문서·업데이트가 좋지만, 중소 보드사는 "한 번 주고 끝"인 경우가 많다.
- <strong>blob은 블랙박스</strong> — GPU 등 바이너리로만 오는 부분은 문제가 생겨도 디버깅할 수 없고 벤더에 의존해야 한다. 라이선스상 커널·U-Boot(GPL)는 소스를 받을 권리가 있지만, 유저스페이스 blob은 받을 수 없는 게 정상이다.
:::

통합의 <strong>원칙</strong>이 중요하다. BSP를 잘못 다루면 다음 버전 업데이트 때 지옥을 본다.

- <strong>device/는 폴더째 받아 수정하지 않는다.</strong> 벤더가 준 `device/<vendor>/<board>`를 직접 고치는 대신, 우리 제품 makefile에서 `inherit-product`로 <strong>확장</strong>만 한다. 벤더가 device 트리를 업데이트하면 그대로 교체할 수 있어야 하기 때문이다.
- <strong>vendor/ blob은 그대로 둔다.</strong> 비공개 바이너리는 손댈 수 없고 손대서도 안 된다. 받은 그대로 트리에 넣는다.
- <strong>커널만 config를 켜서 재빌드하는 것이 사실상 유일한 능동 작업</strong>이다. 앞 절의 CAN fragment처럼, 우리가 실제로 건드리는 건 커널 config가 거의 전부다. 나머지는 "받아서 상속"이다.

보드를 고를 때 쓰는 체크리스트다. 임베디드 안드로이드에서 보드 선정은 프로젝트 성패를 가른다.

| 확인 항목 | 왜 중요한가 |
|---|---|
| 안드로이드 BSP 제공 여부 | BSP가 리눅스만 지원하면 안드로이드 bring-up을 처음부터 해야 한다. 안드로이드 BSP가 있어야 device 트리·HAL을 받아 쓴다 |
| 지원 안드로이드 버전 | 우리가 쓰려는 버전(예: 16)의 BSP가 있는지. 오래된 버전만 있으면 업그레이드 부담이 크다 |
| 커널 소스 포함 여부 | `CONFIG_CAN`을 켜려면 커널을 재빌드해야 한다. 커널이 blob으로만 오면 config를 못 켠다 |
| CAN 컨트롤러·트랜시버 지원 | 보드에 CAN 인터페이스가 있고 해당 드라이버가 BSP 커널에 있는지. 없으면 SPI CAN 칩 + 드라이버 추가가 필요하다 |

## BSP가 없을 때 — 직접 bring-up과 상용 기기

안드로이드 BSP가 없는 하드웨어에 올려야 할 때도 있다. 리눅스만 도는 ARM 보드를 안드로이드화하거나, 시중 태블릿을 개조하는 경우다. 가능은 하지만 난이도와 리스크가 완전히 달라지므로, 무엇을 감수하는지 알고 선택해야 한다.

<strong>리눅스 ARM 보드를 직접 bring-up하는 경우</strong>, 먼저 전제 조건을 확인한다.

| 항목 | 최소 요건 | 비고 |
|---|---|---|
| CPU | ARMv8 64비트 (aarch64) | 32비트는 최신 AOSP에서 사실상 지원 종료 |
| RAM | 2GB 이상 권장 | 1GB로는 system_server 구동이 버겁다 |
| 스토리지 | 8GB 이상 | system + vendor + data 최소 구성 |
| 커널 | 소스 보유 + 재빌드 가능 | <strong>이게 사활이다</strong> — blob 커널이면 여기서 끝 |

작업의 핵심은 <strong>커널 안드로이드화</strong>인데, Binder가 메인라인 커널에 들어가 있어서 의외로 config 문제로 수렴한다.

```
CONFIG_ANDROID_BINDER_IPC=y
CONFIG_ANDROID_BINDERFS=y
CONFIG_PSI=y                  # lmkd가 요구 (CH11)
CONFIG_CGROUPS=y              # +cpuset, memcg 등
CONFIG_SECURITY_SELINUX=y
CONFIG_F2FS_FS=y              # 또는 EXT4 — /data용
```

그 위에 device 트리를 앞 절 그대로 직접 짜면 되는데, 복병은 <strong>그래픽</strong>이다. 디스플레이가 없는 headless 장비라도 SurfaceFlinger는 뜨려고 하고, 못 뜨면 부팅이 멈춘다. GPU 드라이버 없이 가려면 SwiftShader(소프트웨어 GL)와 drm_hwcomposer·가상 디스플레이 조합으로 해결한다. 커널이 안드로이드 config로 부팅까지 되면, system 이미지는 직접 빌드하기 전에 <strong>GSI(Generic System Image, [CH6](/study/android-internals/06-images-updates))를 그대로 얹어보는 것이 가장 빠른 검증</strong>이다 — GSI가 부팅하면 그 보드는 "안드로이드 가능"으로 증명된 것이다.

<strong>상용 기기(태블릿·폰)를 개조하는 경우</strong>는 성격이 다르다. 제조사는 안드로이드 BSP를 주지 않는다 — 공개되는 건 GPL 의무분인 커널 소스뿐이고, device 트리·vendor blob·부트로더는 없다. 그래서 순수 AOSP를 처음부터 빌드해 올리는 건 사실상 불가능하고, 현실 경로는 <strong>커스텀 롬 커뮤니티(LineageOS 계열)가 리버스 엔지니어링으로 만든 device 트리 + 순정 펌웨어에서 추출한 blob</strong>으로 빌드하는 것이다. 진행 전 확인할 것 세 가지: ① 부트로더 언락이 가능한 기기·지역인지(제조사·지역에 따라 원천 차단), ② 그 기기의 커뮤니티 빌드가 존재하는지, ③ 언락 시 보안 efuse(삼성 Knox 등)가 <strong>영구적으로</strong> 끊어져 되돌릴 수 없다는 점을 감수할지.

::: tip 어느 길을 갈까
학습 목적이면 직접 bring-up이 최고의 실습이다(이 챕터와 [CH7](/study/android-internals/07-boot-process)·[CH16](/study/android-internals/16-selinux-avb)의 내용을 벤더 도움 없이 몸으로 겪는다). 하지만 제품 프로토타입이 목적이면 <strong>안드로이드 BSP를 공식 제공하는 보드를 사는 것</strong>이 비용·시간 양쪽에서 압도적으로 유리하다. bring-up에 쓸 몇 주가 보드값보다 비싸다.
:::

## 외부 라이브러리 배치 기준

AgIsoStack++ 같은 서드파티 C++ 라이브러리를 트리에 넣을 때, <strong>어디에 두느냐</strong>는 명확한 관례가 있다.

- <strong>external/</strong> — 서드파티 <strong>오픈소스</strong>를 두는 곳이다. 원칙은 "포크하지 않고 커밋 고정으로 수입"이다. 상류(upstream) 저장소를 특정 커밋/태그에 고정해 그대로 들여오고, 우리 수정은 최소화한다. 이렇게 해야 상류 업데이트를 따라가기 쉽다. 로컬 매니페스트로 상류 저장소를 `external/agisostack`에 특정 revision으로 물리는 방식이 깔끔하다.
- <strong>vendor/&lt;회사&gt;/</strong> — <strong>자사 코드</strong>를 두는 곳이다. agcand 같은 우리가 만든 데몬, 사내 라이브러리가 여기 들어간다.

AgIsoStack++처럼 "서드파티지만 우리가 상당히 커스텀하는" 라이브러리는 두 관례가 공존한다.

1. <strong>external/agisostack/</strong> — 순수 오픈소스로 취급해 external에 두고, `Android.bp`만 우리가 덧붙인다. 상류를 거의 안 고칠 때 적합하다.
2. <strong>vendor/agmo/external/agisostack/</strong> — 자사 vendor 트리 밑에 external 하위 디렉토리를 두는 관례다. 상류를 포크해 사내 패치를 적극적으로 얹거나, 회사 소유로 관리하고 싶을 때 쓴다.

어느 쪽이든 [Android.bp 문법](#android-bp-문법) 절에서 본 대로 `cc_library_static`으로 감싸 데몬의 `static_libs`에 넣는 것은 동일하다. 배치 위치가 달라질 뿐 빌드 방식은 같다.

## NDK와 크로스 컴파일

device 트리 안에서 빌드하는 것과 별개로, 데몬을 <strong>AOSP 트리 밖에서 독립적으로</strong> 크로스 컴파일하고 싶을 때가 있다. CI 파이프라인이 AOSP 전체 소스를 안 갖고 있거나, 라이브러리를 먼저 검증하고 싶을 때다. 이때 NDK를 쓴다.

NDK(Native Development Kit)는 안드로이드용 크로스 컴파일 툴체인(Clang)과 시스템 헤더·stub 라이브러리 묶음이다. <strong>standalone toolchain</strong>은 옛날 개념이고(과거엔 `make_standalone_toolchain.py`로 별도 추출했다), 지금은 NDK가 그 자체로 CMake·Make와 바로 연동된다.

CMake 프로젝트라면 NDK가 제공하는 toolchain 파일을 지정하면 끝이다.

```bash
cmake -DCMAKE_TOOLCHAIN_FILE=$ANDROID_NDK/build/cmake/android.toolchain.cmake \
      -DANDROID_ABI=arm64-v8a \
      -DANDROID_PLATFORM=android-34 \
      -S . -B build-android
cmake --build build-android
```

커스텀 Makefile이라면 NDK의 Clang을 직접 부른다.

```bash
export TOOLCHAIN=$ANDROID_NDK/toolchains/llvm/prebuilt/linux-x86_64
export CC=$TOOLCHAIN/bin/aarch64-linux-android34-clang
export CXX=$TOOLCHAIN/bin/aarch64-linux-android34-clang++
make ARCH=arm64
```

단, NDK로 만든 바이너리는 <strong>공개 NDK API</strong>만 쓸 수 있다. `libbinder`나 내부 시스템 라이브러리처럼 NDK가 노출하지 않는 것에 링크하려면 결국 AOSP 트리 안에서 `cc_binary`로 빌드해야 한다. 그래서 실무 패턴은 "라이브러리 로직은 NDK로 빠르게 검증하고, 최종 데몬은 AOSP 트리 안에서 빌드"로 나뉜다.

::: warning vendor 데몬은 트리 안에서 빌드하라
바인더·HAL·VINTF·SELinux까지 엮인 vendor 데몬을 NDK만으로 완결하려 하면 링커 namespace([CH15](/study/android-internals/15-native-level))와 정책([CH16](/study/android-internals/16-selinux-avb)) 문제에 반드시 부딪힌다. 최종 산출물은 `device/agmo/tractor`에 `cc_binary`로 넣어 AOSP 빌드에 태우는 것이 정석이다.
:::

## 개발·테스트 환경 — Cuttlefish와 검증 사다리

실물 보드는 하나뿐이고 부팅에 몇 분씩 걸린다. 매번 실보드로 반복하면 개발이 느려진다. 그래서 대부분의 검증은 <strong>가상 기기</strong>에서 먼저 한다.

<strong>Cuttlefish</strong>가 그 핵심이다. Cuttlefish는 구글이 <strong>BSP까지 제공하는 공식 가상 안드로이드 기기</strong>다. 호스트 리눅스에서 가상 머신으로 돌고, 실기기에 가까운 HAL·부팅 흐름을 재현한다. 단순 앱 테스트용인 안드로이드 에뮬레이터(AVD)와 결정적으로 다른 점은, Cuttlefish는 <strong>커스텀 커널·vendor 이미지·HAL을 그대로 부팅</strong>할 수 있다는 것이다. 즉 우리가 만든 device 빌드를 실보드 전에 검증하는 데 쓴다.

```bash
# aosp_cf(Cuttlefish) 타깃으로 빌드
lunch aosp_cf_arm64_only_phone-trunk_staging-userdebug
m

# 가상 기기 부팅
launch_cvd            # 또는 최신 워크플로: cvd create

# 커스텀 커널로 부팅 — CAN을 켠 커널을 실보드 없이 검증
launch_cvd -kernel_path out/.../Image -initramfs_path out/.../initramfs.img
```

`-kernel_path`로 앞서 CAN fragment를 병합해 빌드한 커널을 바로 부팅해볼 수 있다. `zcat /proc/config.gz | grep CONFIG_CAN`으로 config가 켜졌는지, `ip link add vcan0 type vcan`으로 가상 CAN이 뜨는지를 실보드 없이 확인한다.

<strong>개발 사이클 팁.</strong> 데몬 하나 고칠 때마다 풀빌드(`m`)를 돌리는 건 낭비다. 실전 루프는 이렇다.

- 코드를 고치면 <strong>NDK로 크로스 컴파일</strong>해 바이너리만 빠르게 만든다.
- `adb push`로 기기(Cuttlefish나 실보드)에 밀어 넣고 데몬을 재시작해 즉시 확인한다.
- 로직이 안정되면 그때 <strong>Soong으로 최종 통합 빌드</strong>해 이미지에 정식으로 넣는다.

```bash
# 빠른 반복: 빌드 → push → 재시작
adb root && adb remount
adb push out/agcand /vendor/bin/agcand
adb shell stop agcand && adb shell start agcand
adb logcat -s agcand
```

<strong>화면 없이 개발 — scrcpy.</strong> 실물 모니터가 없어도 개발에는 지장이 없다. 타깃이 안드로이드라는 점이 핵심인데, adb만 붙으면 <strong>scrcpy</strong>로 개발 PC에서 화면을 보면서 마우스·키보드 입력까지 보낼 수 있다. 클릭이 터치 이벤트로 들어가므로 HMI 앱 조작 테스트도 그대로 된다. HDMI에 아무것도 안 꽂아도 안드로이드는 기본 디스플레이를 렌더링하므로 동작하고, 스크린샷·화면 녹화도 scrcpy가 해준다.

```bash
brew install scrcpy            # 또는 apt install scrcpy
adb connect <보드IP>:5555      # 같은 네트워크면 무선, USB도 가능
scrcpy                          # PC 창에 보드 화면 + 클릭=터치
```

반대로 <strong>태블릿을 보드의 모니터로 쓰는 것은 안 된다</strong> — 태블릿의 USB-C/HDMI는 출력 전용이라 영상 입력을 받지 못한다. HDMI 캡처 동글로 태블릿에서 화면을 보는 우회는 가능하지만 터치가 보드로 전달되지 않는 보기 전용이라, scrcpy가 모든 면에서 낫다. 실물 터치 감각(장갑·직사광선) 검증이 필요한 단계에서만 HDMI+USB 터치 모니터를 붙인다.

CAN처럼 하드웨어가 얽힌 기능은 <strong>검증 사다리</strong>를 단계적으로 오른다. 아래로 갈수록 실물에 가깝고 비용이 크다.

1. <strong>호스트 vcan</strong> — 개발 PC에서 가상 CAN(`vcan0`)으로 프로토콜 로직만 검증. 하드웨어 0.
2. <strong>Cuttlefish</strong> — 가상 안드로이드 안에서 vcan으로, 실제 안드로이드 환경(SELinux·init·바인더)까지 포함해 검증.
3. <strong>USB-CAN 어댑터</strong> — 실제 CAN 프레임이 오가는지를 저렴한 USB-CAN 동글로 확인. 실물 버스 타이밍을 처음 만난다.
4. <strong>실보드</strong> — 최종 타깃 하드웨어에서 트랜시버·전기적 특성까지 포함해 검증.

앞 단계에서 걸러지는 버그가 대부분이라, 실보드까지 가는 반복 횟수를 크게 줄일 수 있다.

::: tip 핵심 정리
- AOSP는 1000개 넘는 git 프로젝트의 집합이고, `repo`와 manifest(default.xml + local manifests)로 동기화한다. 제품 빌드는 이동 브랜치가 아니라 `android-16.0.0_rN` 같은 고정 태그에 물린다.
- 최상위 디렉토리는 역할이 분명하다(frameworks·system·hardware·device·vendor·external·build·prebuilts). 코드 탐색은 cs.android.com이 사실상 필수다.
- 빌드 파이프라인은 Soong(Android.bp) + Kati(Android.mk) → 통합 build.ninja → Ninja 실행이다. Bazel 전면 전환은 보류됐고 16 시점에도 이 조합이 중심이다.
- device bring-up은 `device/<vendor>/<board>`에 AndroidProducts.mk·제품 makefile·BoardConfig.mk를 짜는 일이다. `inherit-product`로 미니멀 베이스를 상속받고 PRODUCT_PACKAGES·COPY_FILES로 데몬과 설정을 얹는다.
- CAN 같은 기능은 커널 config로 켠다(CONFIG_CAN·CAN_RAW·CAN_VCAN·CAN_J1939). GKI면 드라이버를 vendor 모듈(.ko)로, 서브시스템 자체를 켜야 하면 커널을 재빌드한다.
- BSP는 부트로더·보드 커널·DTB·HAL blob 묶음이다. device/는 폴더째 받아 inherit-product로 확장만 하고 vendor blob은 그대로 두며, 커널 config를 켜 재빌드하는 것이 사실상 유일한 능동 작업이다. 외부 오픈소스는 external/에 커밋 고정으로, 자사 코드는 vendor/<회사>/에 둔다.
- 벤더 데몬은 NDK로 로직만 검증하고 최종 산출물은 AOSP 트리 안 `cc_binary`로 빌드하는 것이 정석이다. BOARD_VENDOR_SEPOLICY_DIRS가 CH16 정책 작업으로 이어진다.
- 검증은 Cuttlefish(커스텀 커널 `-kernel_path` 부팅)로 실보드 전에 하고, NDK 크로스컴파일+adb push로 빠르게 반복하다 최종만 Soong 통합한다. CAN은 호스트 vcan → Cuttlefish → USB-CAN → 실보드 사다리로 오른다. 화면은 scrcpy로 충분해 개발 단계에선 모니터도 필요 없다.
- CAN 수신 경로에서 칩셋 종속 코드는 드라이버·Device Tree까지고, `struct can_frame`으로 변환된 뒤(SocketCAN 위)는 어떤 보드에서도 불변이다. USB-CAN 어댑터(gs_usb 계열)도 같은 SocketCAN 드라이버로 `can0`이 된다.
- 안드로이드 BSP가 없는 하드웨어는 직접 bring-up(커널 안드로이드화 config + GSI 검증)이 가능하지만, 제품 프로토타입이면 BSP 제공 보드를 사는 것이 정석이다. 상용 기기 개조는 언락 가능 여부·커뮤니티 트리 존재·efuse 영구 소손을 먼저 확인한다.
:::

## 다음 챕터

[CH15. 네이티브 레벨과 Bionic](/study/android-internals/15-native-level)에서는 방금 빌드한 데몬이 실제로 어떤 libc 위에서 돌고, linker namespace 때문에 왜 "vendor 프로세스가 system 라이브러리를 못 여는지", 그리고 데몬이 크래시했을 때 tombstone을 어떻게 해부하는지를 다룬다.
