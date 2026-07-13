---
title: "CH17. 패키지 관리"
description: "APK의 물리적 구조부터 v1~v4 서명 체계, RRO 오버레이, pm install 이면의 설치 파이프라인과 PackageManagerService, 그리고 커스텀 기기의 시스템 앱 프리로드·롤백까지 안드로이드 패키지 관리 전반을 해부한다."
date: 2026-07-13
tags: [android, aosp, apk, packagemanager, signing]
---

# CH17. 패키지 관리

안드로이드에서 "앱"은 결국 APK 파일 하나다. 이 챕터는 그 APK가 물리적으로 어떻게 생겼는지, 어떤 서명이 붙는지, `pm install` 한 줄이 내부적으로 어떤 파이프라인을 거치는지, 그리고 커스텀 기기를 만들 때 시스템 앱을 어떻게 이미지에 심는지를 파고든다. 임베디드 안드로이드를 만들 때 프리로드 앱 배치와 서명 키 관리는 반드시 마주치는 문제라 실무 관점을 앞세운다.

## 학습 목표

- APK가 ZIP 컨테이너로서 어떤 엔트리로 구성되고 각 파일이 무슨 역할을 하는지 이해한다.
- v1(JAR)부터 v2/v3(APK Signing Block), v4(fs-verity)까지 서명 체계의 진화와 apksigner 실습을 익힌다.
- AOSP 빌드 키 4종과 플랫폼 서명이 system UID·signature 권한에 필요한 이유, 릴리스 키 생성·교체를 이해한다.
- RRO(Runtime Resource Overlay)로 소스 수정 없이 리소스를 덮어쓰는 방법을 안다.
- `pm install`이 session → 검증 → installd → PMS 등록으로 이어지는 설치 파이프라인을 추적한다.
- 커스텀 기기에서 시스템 앱 프리로드, 커스텀 런처·SystemUI 구성, 자체 스토어의 사일런트 설치를 구현하는 실무를 파악한다.

## APK 해부

APK(Android Package)는 확장자만 다를 뿐 표준 ZIP 아카이브다. `unzip -l app.apk`로 그대로 내용을 볼 수 있고, 그 안에는 앱이 실행되는 데 필요한 모든 것이 담긴다.

![APK ZIP 엔트리 구성과 파일 물리 레이아웃에서 APK Signing Block이 ZIP 엔트리와 Central Directory 사이에 위치하는 구조](/images/study-android-internals/17-apk-structure-light.png)
![APK ZIP 엔트리 구성과 파일 물리 레이아웃에서 APK Signing Block이 ZIP 엔트리와 Central Directory 사이에 위치하는 구조](/images/study-android-internals/17-apk-structure-dark.png)

- <strong>AndroidManifest.xml</strong>은 사람이 읽는 텍스트 XML이 아니라 <strong>바이너리 XML</strong>로 컴파일돼 있다. 그냥 열면 깨져 보이고, `aapt2 dump xmltree app.apk --file AndroidManifest.xml`로 디코딩해야 한다. 패키지명·컴포넌트 선언·권한·minSdk/targetSdk가 여기 들어간다.
- <strong>classes.dex</strong>는 Dalvik/ART가 실행하는 바이트코드다. 메서드가 65536개를 넘으면 `classes2.dex`, `classes3.dex`로 나뉜다(multidex). DEX 포맷 자체는 [CH19](/study/android-internals/19-dalvik-dex)에서 자세히 다룬다.
- <strong>resources.arsc</strong>는 문자열·색상·치수 같은 값 리소스를 컴파일해 담은 바이너리 테이블이다. 리소스 ID(`0x7f...`)와 실제 값의 매핑, 그리고 언어·화면밀도별 설정(configuration) 분기가 이 안에 있다.
- <strong>res/</strong>는 레이아웃·drawable 같은 리소스 파일이고, <strong>assets/</strong>는 앱이 `AssetManager`로 직접 읽는 가공되지 않은 원본 파일이다. res는 aapt2가 인덱싱하지만 assets는 손대지 않는다.
- <strong>lib/&lt;abi&gt;/</strong>에는 ABI별 네이티브 라이브러리(`.so`)가 들어간다. `arm64-v8a`, `armeabi-v7a`, `x86_64` 등으로 나뉘며, 설치 시 기기 ABI에 맞는 것만 추출된다. CAN 통신 데몬처럼 네이티브 코드를 앱에 얹는 경우 이 디렉토리가 핵심이다.
- <strong>META-INF/</strong>에는 v1(JAR) 서명 산출물인 `MANIFEST.MF`, `CERT.SF`, `CERT.RSA`가 들어간다. v2 이상만 쓰면 이 디렉토리가 없거나 최소한으로 남는다.

파일의 물리적 배치도 중요하다. `zipalign`은 ZIP 엔트리의 시작 오프셋을 4바이트(또는 페이지) 경계에 맞춰, 런타임이 리소스를 `mmap`으로 직접 읽을 수 있게 한다. 정렬이 어긋나면 복사가 발생해 메모리·성능 손해가 난다. 그래서 <strong>정렬 → 서명 순서</strong>를 지켜야 한다. 뒤에 나오는 v2 서명 블록은 정렬을 깨지 않도록 설계돼 있다.

```bash
# APK 내용 훑어보기
unzip -l app.apk

# 매니페스트 디코드
aapt2 dump xmltree app.apk --file AndroidManifest.xml

# 배지 정보(패키지명·버전·권한 요약)
aapt2 dump badging app.apk | head
```

## 서명 체계 — v1에서 v4까지

안드로이드는 모든 APK가 서명되기를 요구한다. 서명은 "누가 만들었는지"를 증명하고, 같은 키로 서명된 앱만 <strong>업데이트</strong>할 수 있게 하며, `sharedUserId`나 `signature` 보호 수준 권한의 기준이 된다. 서명 스킴은 네 세대에 걸쳐 진화했다.

![v1 JAR 서명에서 v2/v3 APK Signing Block, v4 fs-verity로 이어지는 서명 스킴 진화](/images/study-android-internals/17-apk-structure-light.png)

- <strong>v1 (JAR signing)</strong>은 자바 JAR 서명을 그대로 쓴다. `META-INF/`의 매니페스트에 각 파일의 다이제스트를 적고 그걸 서명한다. 문제는 <strong>ZIP 메타데이터·엔트리 순서·압축되지 않은 부가 데이터가 보호되지 않는다</strong>는 점이다. 파일 단위 검증이라 느리고, 서명 밖 영역을 조작할 여지가 있었다.
- <strong>v2 (APK Signature Scheme v2, Android 7.0)</strong>은 접근을 뒤집었다. ZIP의 Central Directory 바로 앞에 <strong>APK Signing Block</strong>을 삽입하고, 파일 전체를 청크로 나눠 <strong>바이트 단위로</strong> 해시·서명한다. 파일의 거의 전 영역이 서명에 포함돼 무결성이 훨씬 강해지고, 검증도 한 번에 끝나 빨라졌다.
- <strong>v3 (Android 9)</strong>은 v2 블록을 확장해 <strong>키 로테이션</strong>을 지원한다. "이전 키로 서명했고 이제 새 키로 넘어간다"는 증명(proof-of-rotation) 체인을 담아, 앱 서명 키를 안전하게 교체할 수 있다. v3.1(Android 13)은 로테이션 대상 SDK를 지정하는 세분화를 추가했다.
- <strong>v4 (Android 11)</strong>은 별도 `.apk.idsig` 파일에 <strong>fs-verity</strong>용 머클 트리 해시를 담는다. 전체 파일을 미리 읽지 않고 <strong>증분(incremental) 설치</strong>—필요한 페이지만 스트리밍하며 페이지 단위로 검증—를 가능하게 한다. Play의 빠른 실행이 이 기반이다.

실무에서 서명은 `apksigner`로 한다. 여러 스킴을 동시에 넣을 수 있고, 최소 스킴 버전을 지정할 수도 있다.

```bash
# 키스토어 생성 (개발용)
keytool -genkeypair -v -keystore my.keystore -alias dev \
  -keyalg RSA -keysize 2048 -validity 10000

# 정렬 후 서명 (v1+v2+v3)
zipalign -p 4 app-unsigned.apk app-aligned.apk
apksigner sign --ks my.keystore --ks-key-alias dev \
  --v1-signing-enabled true --v2-signing-enabled true \
  --v3-signing-enabled true --out app-signed.apk app-aligned.apk

# 서명 검증 (어떤 스킴으로 서명됐는지 확인)
apksigner verify --verbose --print-certs app-signed.apk
```

::: warning platform key 관리
커스텀 기기에서 시스템 앱을 `platform` 키로 서명하면, 그 키가 유출됐을 때 `signatureOrSystem` 권한을 가진 악성 앱을 심을 수 있게 된다. AOSP 기본 test-key는 절대 양산에 쓰지 말고, `vendor/<oem>/security/`에 자체 릴리스 키를 만들어 관리한다. 키를 잃으면 그 키로 서명된 앱을 다시는 업데이트할 수 없다.
:::

## 플랫폼 서명 심층

일반 앱 서명은 "누가 만들었나"만 증명하면 되지만, 커스텀 OS를 만들면 <strong>플랫폼 서명</strong>이라는 훨씬 강력한 축을 다루게 된다. AOSP 빌드는 여러 개의 <strong>빌드 키</strong>를 쓰는데, `build/make/target/product/security/`에 기본(test) 키들이 들어 있고 릴리스 시 이를 자체 키로 교체한다.

- <strong>platform</strong> — 프레임워크(`system_server`)와 핵심 시스템 앱(Settings, SystemUI 등)을 서명하는 키. 이 키로 서명된 앱은 `android.uid.system` UID를 공유하거나 `signature` 보호 수준의 시스템 권한을 얻을 수 있다. 가장 민감한 키다.
- <strong>shared</strong> — 홈/연락처 계열처럼 데이터를 공유하는 일부 앱 묶음에 쓰는 키.
- <strong>media</strong> — 미디어/다운로드 프로바이더 계열에 쓰는 키.
- <strong>testkey (releasekey)</strong> — 위 카테고리에 속하지 않는 일반 패키지의 기본 키. AOSP 공개 소스라 <strong>누구나 아는 키</strong>이므로 양산 금지다. 릴리스 빌드에서는 이를 자체 `releasekey`로 교체한다.

<strong>왜 플랫폼 서명이 필요한가</strong>는 두 메커니즘에서 나온다. 첫째, `AndroidManifest.xml`에 `android:sharedUserId="android.uid.system"`을 선언한 앱은 `system` UID(1000)로 실행되어 프레임워크와 같은 프로세스 권한을 갖는데, <strong>system UID를 이미 점유한 플랫폼 키와 동일한 키로 서명</strong>돼야만 이 선언이 허용된다. 다른 키면 설치가 거부된다. 둘째, `protectionLevel="signature"` 권한(예: `MANAGE_USERS`, `WRITE_SECURE_SETTINGS` 일부)은 <strong>권한을 정의한 쪽과 같은 키로 서명</strong>된 앱에만 부여된다. 프레임워크가 정의한 signature 권한을 얻으려면 곧 플랫폼 키 서명이 필요하다는 뜻이다.

<strong>릴리스 키 생성.</strong> AOSP는 `development/tools/make_key` 스크립트로 4종 키를 만든다. 만든 키는 `vendor/<oem>/security/`에 두고 빌드가 그 경로를 참조하게 한다.

```bash
# 4종 릴리스 키 생성 (subject는 조직에 맞게)
subject='/C=KR/ST=Seoul/O=OEM/CN=OEM'
for k in platform shared media releasekey; do
  development/tools/make_key vendor/oem/security/$k "$subject"
done
```

빌드가 이 키를 쓰도록 제품 makefile에서 기본 인증서 경로를 덮는다.

```makefile
# device/oem/tractor/device.mk
PRODUCT_DEFAULT_DEV_CERTIFICATE := vendor/oem/security/releasekey
# APEX·OTA 서명 키도 함께 지정 (별도 변수)
```

<strong>키 교체(로테이션).</strong> 이미 배포한 뒤 플랫폼 키를 바꿔야 하면, 앞서 본 v3 서명의 proof-of-rotation 체인으로 앱 단위 키는 교체할 수 있다. 그러나 <strong>플랫폼 키 자체의 교체</strong>는 그 키로 서명된 모든 시스템 앱과 signature 권한 관계가 얽혀 있어, 사실상 전체 시스템 이미지를 새 키로 재서명해 OTA로 내리는 방식으로만 안전하다. 그래서 플랫폼 키는 <strong>처음부터 유출되지 않게 보관</strong>하는 것이 유일하게 현실적인 전략이다. HSM이나 격리된 서명 서버에 두고, 리포지토리에는 넣지 않는다.

## RRO — Runtime Resource Overlay

커스텀 기기를 만들다 보면 "프레임워크나 시스템 앱의 리소스 하나만 바꾸고 싶은데 소스를 포크하기는 싫은" 상황이 온다. 부팅 로고 색, 기본 배경, `config.xml`의 기능 플래그, 통신사/브랜드별 문자열 같은 것들이다. <strong>RRO</strong>가 바로 그걸 위한 메커니즘이다.

RRO는 <strong>대상 패키지의 리소스를 런타임에 덮어쓰는 별도 APK</strong>다. 코드는 없고 리소스만 담으며, `AndroidManifest.xml`에 어떤 패키지를 오버레이할지 `<overlay android:targetPackage="android">`로 선언한다. 부팅 시 `idmap2`가 오버레이 리소스 ID와 대상 리소스 ID를 매핑한 <strong>idmap</strong>을 만들고, 리소스 조회 시 오버레이 값이 우선 반환된다.

```xml
<!-- overlay APK의 매니페스트 -->
<manifest package="com.oem.overlay.framework">
  <overlay android:targetPackage="android"
           android:isStatic="true"
           android:priority="10" />
  <application android:hasCode="false" />
</manifest>
```

오버레이는 두 종류다. <strong>static overlay</strong>는 `isStatic="true"`로 부팅 시 항상 활성화되며 `/vendor/overlay/` 등에 프리로드한다—브랜드 상수처럼 절대 안 바뀌는 값에 쓴다. <strong>dynamic overlay(OMS)</strong>는 `OverlayManagerService`로 런타임에 켜고 끌 수 있어 테마 전환 같은 데 적합하다.

```bash
# 현재 등록된 오버레이 목록·상태
cmd overlay list

# 특정 오버레이 활성화 (dynamic)
cmd overlay enable com.oem.overlay.framework
```

커스텀 기기에서는 static RRO로 `frameworks/base`의 `config.xml` 값(예: `config_showNavigationBar`, 기본 밝기 곡선, 지원 로케일)을 소스 수정 없이 덮는 패턴이 매우 흔하다. 프레임워크를 포크하지 않으니 AOSP 업스트림 머지 부담이 줄어든다.

## 설치 파이프라인

`pm install app.apk`나 사용자가 화면에서 "설치"를 누르는 것은 겉으로 한 동작이지만, 내부는 여러 프로세스가 협업하는 파이프라인이다.

![pm install 이면의 설치 파이프라인 — install session 생성, 검증, installd 디렉토리 생성·dexopt, PMS 등록으로 이어지는 흐름](/images/study-android-internals/17-install-flow-light.png)
![pm install 이면의 설치 파이프라인 — install session 생성, 검증, installd 디렉토리 생성·dexopt, PMS 등록으로 이어지는 흐름](/images/study-android-internals/17-install-flow-dark.png)

1. <strong>session 생성.</strong> `PackageInstaller`가 install session을 열고 APK 바이트를 스트리밍해 받는다. 큰 앱이나 split APK도 여러 조각을 한 세션에 담아 원자적으로 커밋한다.
2. <strong>검증.</strong> `PackageManagerService`(PMS)가 서명을 확인하고, `minSdkVersion`이 기기와 맞는지, 기존 설치본이 있으면 <strong>같은 키로 서명됐는지</strong>(업데이트 자격)를 검사한다. 다운그레이드나 서명 불일치는 여기서 거부된다.
3. <strong>installd.</strong> root 권한의 데몬 `installd`가 `/data/app/<pkg>-<random>/` 디렉토리를 만들고 APK를 복사한 뒤, <strong>dexopt(dex2oat)</strong>를 트리거해 DEX를 최적화한다. 앱 데이터 디렉토리(`/data/user/0/<pkg>`)와 UID별 소유권·SELinux 컨텍스트도 이때 설정된다. dexopt는 [CH20](/study/android-internals/20-art-internals)의 주제다.
4. <strong>PMS 등록.</strong> 패키지 정보가 `/data/system/packages.xml`에 기록되고, UID 매핑은 `packages.list`에 추가된다. 권한이 부여되고 앱에 UID가 배정된다.
5. <strong>완료.</strong> `PACKAGE_ADDED` 브로드캐스트가 나가고, Launcher가 아이콘을 표시한다.

`packages.xml`은 PMS의 영속 상태 그 자체다. 각 패키지의 서명 인증서, 부여된 권한, 설치 경로, 버전이 XML로 남고, 부팅 때 이걸 읽어 상태를 복원한다. `packages.list`는 더 단순한 텍스트로, 패키지명·UID·데이터 경로·SELinux seinfo를 한 줄씩 담는다.

```bash
# 설치된 패키지의 경로·설치 정보
pm path com.example.app
dumpsys package com.example.app | sed -n '1,40p'

# UID 매핑 확인
grep com.example.app /data/system/packages.list
```

## PackageManagerService

PMS는 시스템에서 앱에 관한 모든 것을 아는 중앙 레지스트리다. 부팅 시 하는 일과 런타임에 강제하는 규칙 몇 가지를 짚어둔다.

- <strong>부팅 시 스캔.</strong> `/system/app`, `/system/priv-app`, `/vendor/app`, `/data/app` 등 정해진 디렉토리를 훑어 APK를 발견하고 매니페스트를 파싱해 컴포넌트·권한을 등록한다. 스캔 결과는 캐시돼 매 부팅마다 전체 재파싱을 피한다.
- <strong>권한 부여.</strong> 설치/일반(normal) 권한은 자동, 위험(dangerous) 권한은 런타임 사용자 동의, 서명(signature) 권한은 앱 서명이 권한 정의자와 일치할 때만 부여한다.
- <strong>shared UID.</strong> `android:sharedUserId`를 선언하고 <strong>같은 키로 서명</strong>된 앱들은 하나의 UID를 공유해 데이터·프로세스를 공유할 수 있다. 강력하지만 한 번 배포하면 UID를 바꾸기 어려워 신규 사용은 권장되지 않는다(deprecated). 커스텀 시스템 앱 묶음에서만 신중히 쓴다.
- <strong>priv-app 권한 allowlist.</strong> `/system/priv-app`에 놓인 특권 앱이 요청하는 `signatureOrSystem` 권한은 `/etc/permissions/`의 allowlist XML에 명시돼야 한다. 목록에 없으면 <strong>부팅이 실패</strong>하거나(강제 모드) 권한이 거부된다. 커스텀 프리로드 앱을 만들 때 반드시 마주치는 관문이다.

```xml
<!-- /system/etc/permissions/privapp-permissions-oem.xml -->
<permissions>
  <privapp-permissions package="com.oem.systemui">
    <permission name="android.permission.STATUS_BAR"/>
    <permission name="android.permission.MANAGE_USERS"/>
  </privapp-permissions>
</permissions>
```

## 시스템 앱 프리로드 — 커스텀 기기 관점

임베디드 기기용 OS를 만들 때 핵심 작업 중 하나가 "우리 앱을 이미지에 미리 심는 것"이다. 방법과 배치 기준을 정리한다.

<strong>빌드에 포함시키기.</strong> `device.mk`나 제품 makefile에서 `PRODUCT_PACKAGES`에 앱 모듈을 추가하면 빌드 시 시스템 이미지에 들어간다.

```makefile
# device/oem/tractor/device.mk
PRODUCT_PACKAGES += \
    OemDashboard \
    OemCanMonitor
```

앱 모듈의 `Android.bp`에서는 서명 키와 특권 여부, 설치 파티션을 지정한다.

```
android_app {
    name: "OemDashboard",
    srcs: ["src/**/*.java"],
    certificate: "platform",   // platform key로 서명
    privileged: true,           // priv-app으로 설치
    system_ext_specific: false,
    platform_apis: true,
}
```

<strong>서명 선택.</strong> 프리로드 앱은 보통 `presigned`(이미 서명된 APK를 그대로 넣음) 또는 `platform`(빌드가 platform key로 서명)을 쓴다. platform 서명 앱은 `signatureOrSystem` 권한과 `system_server`와의 밀접한 상호작용이 가능해지지만, 그만큼 키 유출 위험이 커진다.

<strong>배치 파티션 기준.</strong> 어디에 두느냐로 신뢰 수준과 업데이트 정책이 갈린다.

- <strong>/system/priv-app</strong> — OS의 일부로 취급되는 특권 앱. 프레임워크와 강결합된 런처·설정·SystemUI 커스텀이 여기 온다.
- <strong>/system/app</strong> — 특권 없는 기본 앱. 일반 권한만 필요한 프리로드 앱.
- <strong>/product/app, /system_ext/app</strong> — 제품/파생별로 갈리는 앱을 core system과 분리해 담는 파티션. 같은 하드웨어에 여러 제품 변형을 낼 때 유용하다.
- <strong>/vendor/app</strong> — 하드웨어·SoC에 종속적인 벤더 앱. 벤더 이미지에 묶여 프레임워크 업데이트와 독립적으로 관리된다.

농기계 같은 임베디드 기기라면, 프레임워크와 엮인 커스텀 UI는 `priv-app`에, CAN·GPS 하드웨어에 붙는 벤더 서비스 앱은 `/vendor/app`에 두어 <strong>시스템/벤더 경계</strong>를 지키는 것이 Treble 원칙에 맞다. 파티션 구조 자체는 [CH3](/study/android-internals/03-partitions-filesystems)를 참고한다.

## 커스텀 런처

키오스크·HMI 장비를 만들 때 가장 먼저 마주치는 요구가 "부팅하면 우리 홈 화면만 뜨게 하라"다. 여기서 중요한 사실은 <strong>런처(홈 앱)는 특별한 시스템 컴포넌트가 아니라 평범한 앱</strong>이라는 것이다. 매니페스트에 <strong>CATEGORY_HOME + CATEGORY_DEFAULT</strong> 인텐트 필터를 가진 Activity를 선언하면 그 앱이 홈 후보가 된다.

```xml
<activity android:name=".HomeActivity"
          android:launchMode="singleTask">
  <intent-filter>
    <action android:name="android.intent.action.MAIN" />
    <category android:name="android.intent.category.HOME" />
    <category android:name="android.intent.category.DEFAULT" />
  </intent-filter>
</activity>
```

홈 버튼을 누르거나 부팅이 끝나면 시스템이 `ACTION_MAIN` + `CATEGORY_HOME` Intent를 [resolve](/study/android-internals/18-app-anatomy)해 홈 앱을 띄운다. 후보가 여럿이면 사용자에게 선택을 묻지만, 커스텀 기기에서는 <strong>후보를 하나만 남기는 것</strong>이 정석이다.

<strong>기본 런처 지정.</strong> 두 가지를 함께 한다. 첫째, 우리 홈 앱을 `PRODUCT_PACKAGES`에 넣고 <strong>AOSP 기본 Launcher3를 제외</strong>한다. 둘째, RRO나 config로 기본 홈을 지정한다.

```makefile
# 우리 홈 앱 포함, Launcher3는 빼서 홈 후보를 단일화
PRODUCT_PACKAGES += OemHome
# device.mk에서 Launcher3를 PRODUCT_PACKAGES에 추가하지 않는다
# (상속받은 기본 제품이 넣는다면 명시적으로 제거)
```

프레임워크는 기본 홈을 `config_defaultLauncher` 같은 리소스로 참조하므로, static [RRO](/study/android-internals/17-package-management)로 이 값을 우리 홈 컴포넌트로 덮으면 부팅부터 우리 런처가 뜬다.

```xml
<!-- framework RRO: 기본 런처 컴포넌트 지정 -->
<string name="config_defaultLauncher"
        translatable="false">com.oem.home/.HomeActivity</string>
```

<strong>단일 홈(키오스크) 구성.</strong> HMI 장비에서는 여기에 더해, 사용자가 다른 홈으로 빠져나가지 못하게 막는다. 후보를 하나만 두는 것 외에, 기업 관리(Device Owner)의 <strong>lock task 모드</strong>로 특정 앱만 실행되게 고정하거나(`setLockTaskPackages`), 상태바·최근앱 같은 이탈 경로를 비활성화한다. Device Owner는 뒤의 사일런트 설치 절에서 다시 다룬다.

## SystemUI 커스텀

RRO로 웬만한 리소스는 소스 수정 없이 덮을 수 있지만, <strong>SystemUI는 코드 수정이 불가피한 몇 안 되는 지점</strong>이다. 상태바·알림 셰이드·내비게이션 바·잠금화면·최근앱 화면은 모두 `frameworks/base/packages/SystemUI`에 있는 하나의 특권 앱이 그린다.

<strong>RRO로 처리 가능한 범위.</strong> SystemUI가 리소스로 노출한 값은 오버레이로 바꿀 수 있다. 상태바 높이·색, 특정 아이콘 표시 여부, 내비바 버튼 배치 같은 것이 `config_*`/`dimen`/`bool` 리소스로 열려 있으면 static RRO로 덮으면 된다. 예를 들어 `config_showNavigationBar`를 false로 오버레이해 소프트 내비바를 통째로 숨기는 것은 코드 수정 없이 된다.

```xml
<!-- SystemUI/framework RRO로 내비바 숨김 -->
<bool name="config_showNavigationBar">false</bool>
```

<strong>코드 수정이 필요한 범위.</strong> 리소스로 열려 있지 않은 동작 자체—예컨대 상태바를 아예 없애거나, 알림 셰이드를 못 내리게 하거나, HMI 전용 커스텀 상태 영역을 넣는 것—는 SystemUI 소스를 고쳐야 한다. 접근법은 두 가지다.

- <strong>기존 SystemUI 수정.</strong> `frameworks/base/packages/SystemUI`를 포크해 필요한 부분을 고친다. 가장 직접적이지만 AOSP 업스트림 머지 부담이 크다.
- <strong>SystemUI 교체.</strong> 커스텀 SystemUI를 별도 앱으로 만들어 `config_systemUIServiceComponent` 등으로 대체 지정한다. 상태바를 완전히 자체 구현하려는 키오스크에서 쓰지만, SystemUI가 담당하는 다른 필수 기능(볼륨 UI, 최근앱 등)까지 직접 구현해야 해 범위가 크다.

임베디드 HMI에서는 "상태바·내비바를 숨기고 우리 홈 앱이 전체 화면을 쓰게" 하는 정도가 흔한데, 이는 대개 RRO(내비바 숨김) + 몰입 모드(immersive) + 커스텀 런처 조합으로 <strong>SystemUI 소스 수정 없이</strong> 달성한다. 상태 영역까지 완전히 바꿔야 할 때만 소스 수정으로 넘어간다.

## 프리인스톨과 사일런트 설치

앱을 기기에 올리는 경로는 크게 둘이다. 하나는 빌드 타임에 이미지에 <strong>내장</strong>하는 것이고, 다른 하나는 런타임에 <strong>사일런트 설치</strong>하는 것이다.

<strong>경로 1 — 이미지 내장(프리인스톨).</strong> 앞의 시스템 앱 프리로드에서 본 대로 `PRODUCT_PACKAGES`로 APK를 시스템/제품 파티션에 굽는다. 공장 출하 시점부터 존재하고, 사용자가 지울 수 없으며(특권 앱), OTA로만 갱신된다. 반드시 처음부터 있어야 하는 핵심 앱—런처, 계기판, CAN 모니터—에 적합하다.

<strong>경로 2 — 자체 마켓의 사일런트 설치.</strong> 커스텀 기기는 대개 Play 스토어 대신 <strong>자체 스토어(마켓) 앱</strong>을 두어, 출하 후에도 앱을 원격 배포·업데이트한다. 이 스토어 앱이 사용자 확인 대화상자 없이 앱을 까는 것이 <strong>사일런트 설치</strong>다. 일반 앱에는 허용되지 않고, 두 방식 중 하나로 권한을 얻어야 한다.

- <strong>플랫폼 서명 + INSTALL_PACKAGES.</strong> 스토어 앱을 플랫폼 키로 서명하고 특권 앱으로 배치한 뒤 `android.permission.INSTALL_PACKAGES`(signature|privileged 권한)를 priv-app allowlist에 넣으면, `PackageInstaller` 세션을 사용자 프롬프트 없이 커밋할 수 있다. 우리가 OS까지 만드는 경우의 정석이다.
- <strong>Device Owner(DPC).</strong> OS를 직접 만들지 못하는 상황이면, 기기를 <strong>Device Owner</strong>(기업 관리 정책 앱, DPC)로 프로비저닝해 사일런트 설치 권한을 얻는다. Device Owner는 플랫폼 서명 없이도 `PackageInstaller` 세션 결과를 자동 승인할 수 있다.

두 경우 모두 실제 설치는 `PackageInstaller` <strong>세션 API</strong>로 한다. 세션을 열어 APK 스트림을 쓰고 커밋하면, 앞서 본 [설치 파이프라인](/study/android-internals/17-package-management)(검증 → installd → PMS 등록)을 그대로 탄다.

```java
// PackageInstaller 세션으로 설치 (권한 확보 시 사일런트)
PackageInstaller installer = getPackageManager().getPackageInstaller();
SessionParams params =
    new SessionParams(SessionParams.MODE_FULL_INSTALL);
int sessionId = installer.createSession(params);
try (PackageInstaller.Session session = installer.openSession(sessionId);
     OutputStream out = session.openWrite("base.apk", 0, apkSize);
     InputStream in = new FileInputStream(apkFile)) {
    in.transferTo(out);
    session.fsync(out);
    session.commit(statusReceiver.getIntentSender());
}
```

명령줄로 같은 흐름을 확인하려면 `pm install-create` → `install-write` → `install-commit`를 순서대로 쓴다. 사일런트 여부는 결국 <strong>호출자가 위 권한을 가졌는지</strong>로 갈린다. 권한이 없으면 시스템이 확인 Activity를 띄운다.

```bash
# 세션 기반 설치 (권한 없으면 확인 UI가 뜬다)
sid=$(pm install-create -S $(stat -c %s app.apk) | grep -o '[0-9]\+')
pm install-write $sid base.apk app.apk
pm install-commit $sid
```

## 스냅샷·롤백

OTA나 앱 업데이트가 기기를 망가뜨릴 위험을 줄이려고 안드로이드는 롤백 장치를 둔다.

<strong>Rollback Manager</strong>는 업데이트 직전 이전 버전의 APK와 데이터를 잠시 보관한다. 업데이트 후 일정 시간 안에 크래시 루프 같은 문제가 감지되면 자동으로 이전 버전으로 되돌린다. 앱은 매니페스트에 `android:rollbackDataPolicy`로 데이터 복원 정책을 선언할 수 있다.

<strong>apk-in-apex</strong>는 APK를 [APEX](/study/android-internals/05-storage-management) 안에 담아 배포하는 방식이다. APEX가 원자적 활성화와 A/B 롤백을 지원하므로, apk-in-apex 앱은 APEX 단위로 함께 롤백된다. Mainline 모듈로 배포되는 시스템 컴포넌트에서 이 패턴을 쓴다.

```bash
# 롤백 가능 상태 확인
dumpsys rollback

# 수동 롤백 커밋 (테스트용)
pm rollback-app com.example.app
```

커스텀 기기에서는 A/B 파티션([CH6](/study/android-internals/06-images-updates))과 조합해, OTA 실패 시 슬롯 전체를 되돌리는 시스템 레벨 롤백과 개별 앱 롤백을 함께 설계하는 것이 안전하다.

::: tip 핵심 정리
- APK는 ZIP 컨테이너로, 바이너리 매니페스트·classes.dex·resources.arsc·res/assets·lib/&lt;abi&gt;·META-INF로 구성되며 zipalign으로 mmap 정렬된다.
- 서명은 v1(JAR, 파일 단위) → v2/v3(APK Signing Block, 바이트 단위·키 로테이션) → v4(fs-verity 증분 설치)로 진화했고 apksigner로 관리한다.
- 플랫폼 서명(platform/shared/media/releasekey 4종)은 system UID 공유와 signature 권한의 전제이며, 릴리스 키는 vendor/.../security에 만들어 유출 없이 보관한다.
- RRO는 소스 포크 없이 리소스를 런타임에 덮어쓰며, static overlay로 커스텀 기기의 config·브랜딩을 오버라이드하는 데 쓴다.
- pm install은 session → 검증 → installd(디렉토리·dexopt) → PMS 등록(packages.xml/list) 파이프라인을 거친다.
- 시스템 앱은 PRODUCT_PACKAGES로 프리로드하고, 런처는 CATEGORY_HOME 앱을 단일화해 지정하며, SystemUI는 RRO로 덮되 동작 변경은 소스 수정이 필요하다.
- 사일런트 설치는 플랫폼 서명+INSTALL_PACKAGES 또는 Device Owner로 권한을 얻어 PackageInstaller 세션으로 구현한다.
:::

## 다음 챕터

[CH18. 애플리케이션 해부](/study/android-internals/18-app-anatomy)에서는 4대 컴포넌트의 프레임워크 관점 실체, Launcher 탭에서 첫 프레임까지의 앱 시작 시퀀스, Looper/Handler/MessageQueue 이벤트 루프, JNI, 그리고 oom_adj 기반 앱 생명주기를 다룬다.
