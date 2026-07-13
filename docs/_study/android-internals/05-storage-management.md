---
title: "CH5. 스토리지 관리와 APEX"
description: "loop/bind mount와 mount namespace, fs_mgr와 fstab 문법, 외부 스토리지의 Portable/Adoptable/Scoped 모델, vold·storaged 데몬, 그리고 Mainline의 핵심인 APEX 컨테이너의 구조와 apexd 활성화 흐름을 다룬다."
date: 2026-07-13
tags: [android, aosp, storage, apex, vold, mount, mainline]
---

# CH5. 스토리지 관리와 APEX

## 학습 목표
- loop/bind mount와 mount namespace가 무엇이며 안드로이드에서 어디에 쓰이는지 이해한다.
- `fs_mgr`와 `fstab.{hardware}` 문법(`fs_mgr_flags`)을 읽고 파티션 마운트 정책을 해석할 수 있다.
- Portable/Adoptable/Scoped Storage와 FUSE·MediaProvider의 관계를 설명한다.
- vold·storaged 등 스토리지 데몬의 역할과 이벤트 흐름을 파악한다.
- APEX의 등장 배경·파일 구조·apexd 활성화(verify→mount→activate) 흐름을 이해한다.

## 마운트의 종류

파일시스템을 디렉토리 트리에 붙이는 것이 마운트다. 안드로이드는 블록 디바이스를 직접 마운트하는 것 외에 여러 특수한 마운트를 적극 활용한다.

<strong>loop mount</strong>는 블록 디바이스가 아니라 <strong>파일 하나</strong>를 파일시스템처럼 마운트한다. 커널의 loop 디바이스(`/dev/loop*`)가 파일을 블록 디바이스인 것처럼 감싸준다. 뒤에 나올 APEX가 `apex_payload.img`라는 파일을 마운트하는 방식이 바로 loop mount다. 이미지 파일을 기기에서 마운트해 내용을 확인할 때도 이걸 쓴다.

<strong>bind mount</strong>는 이미 존재하는 디렉토리(또는 파일)를 <strong>다른 경로에도 동시에 보이게</strong> 하는 마운트다. 데이터를 복사하지 않고 같은 것을 두 위치에서 접근하게 만든다. APEX가 버전 붙은 경로(`/apex/<name>@ver`)를 버전 없는 경로(`/apex/<name>`)로 노출할 때, 그리고 외부 스토리지의 여러 뷰를 만들 때 쓰인다.

<strong>mount namespace</strong>는 리눅스 네임스페이스의 하나로, <strong>프로세스마다 다른 마운트 뷰</strong>를 갖게 한다. 안드로이드는 이걸로 앱마다 `/storage`를 다르게 보여준다. 어떤 앱은 자기 파일만, 다른 앱은 공유 미디어까지 — 같은 경로인데 프로세스별로 실제 내용이 다르다. 이 격리 개념은 컨테이너와 뿌리가 같아 [Kubernetes 스터디 CH1](/study/kubernetes/01-container-basics)의 namespace 설명과 통한다.

### fs_mgr와 fstab.{hardware}

부팅 시 파티션을 어떤 순서로, 어떤 옵션으로 마운트할지는 <strong>`fstab.{hardware}`</strong> 파일이 규정하고, 이를 읽어 실제로 마운트하는 것이 <strong>`fs_mgr`</strong>(filesystem manager) 라이브러리다. `init`이 `fs_mgr`를 호출해 초기 파티션들을 올린다. `{hardware}`는 `ro.hardware` 프로퍼티 값(예: `fstab.qcom`)이며, 최신 기기는 DT/DTB에서 오는 경우도 있다.

fstab 한 줄의 문법은 다음과 같다.

```
# <src>            <mnt_point>  <type>  <mnt_flags>       <fs_mgr_flags>
/dev/block/.../system  /system   erofs   ro              wait,slotselect,avb,logical
/dev/block/.../userdata /data    f2fs    noatime,nosuid,nodev  wait,check,fileencryption=aes-256-xts
```

마지막 칸 <strong>`fs_mgr_flags`</strong>가 안드로이드 고유의 마운트 정책을 담는다. 대표 플래그는 다음과 같다.

- <strong>wait</strong> — 해당 블록 디바이스가 나타날 때까지 기다렸다가 마운트한다.
- <strong>check</strong> — 마운트 전에 `fsck`로 파일시스템을 검사한다(주로 `/data`).
- <strong>avb</strong> — 이 파티션을 AVB로 검증한다(dm-verity 연결). [CH16](/study/android-internals/16-selinux-avb)에서 다룬다.
- <strong>slotselect</strong> — A/B 슬롯 접미사(`_a`/`_b`)를 현재 슬롯에 맞게 자동으로 붙인다([CH3](/study/android-internals/03-partitions-filesystems)).
- <strong>logical</strong> — 이 파티션이 super 안의 논리 파티션임을 나타낸다. `fs_mgr`가 `liblp` 메타데이터를 참조해 device-mapper 노드를 만든다.
- <strong>fileencryption</strong> — FBE 암호화 방식 지정([CH4](/study/android-internals/04-files-directories)).

```bash
# 현재 기기의 fstab 살펴보기 (위치는 기기마다 다르다)
adb shell cat /vendor/etc/fstab.* 2>/dev/null
adb shell cat /odm/etc/fstab.* 2>/dev/null
```

## 외부 스토리지

"외부 스토리지"는 물리적으로 SD카드일 수도, 내장 플래시의 일부일 수도 있다. 안드로이드는 사용 모델을 둘로 나눈다.

- <strong>Portable(휴대용)</strong> — SD카드를 여러 기기에서 꽂았다 뺐다 하는 모델. FAT/exFAT으로 포맷하며 암호화하지 않는다. 어느 기기에 꽂아도 사진·파일을 읽을 수 있다.
- <strong>Adoptable(내장 채택)</strong> — SD카드를 내부 스토리지의 연장으로 흡수하는 모델. ext4/f2fs로 포맷하고 그 기기 키로 암호화한다. 그 기기에서만 읽히며, 앱도 여기에 설치될 수 있다.

<strong>Scoped Storage</strong>(범위 지정 스토리지, 10.0 도입, 11.0에서 강제)는 외부 스토리지 접근 모델을 크게 바꿨다. 예전에는 `READ/WRITE_EXTERNAL_STORAGE` 권한 하나로 앱이 공유 저장소 전체를 넘나들었다. Scoped Storage에서는 앱이 <strong>자기 전용 디렉토리와 자기가 만든 미디어</strong>에만 자유롭게 접근하고, 남이 만든 파일은 `MediaStore`/`MediaProvider`를 거쳐야 한다.

이 격리를 파일시스템 레벨에서 구현하는 것이 <strong>FUSE 데몬</strong>과 <strong>MediaProvider</strong>다. `/storage/emulated/0/`은 실제 파일시스템이 아니라 FUSE로 에뮬레이션된 뷰이고, 앱이 여기에 접근하면 FUSE 데몬이 요청을 가로채 MediaProvider의 권한 규칙에 따라 허용/거부한다. 예전 `sdcardfs`(커널 오버레이)를 유저스페이스 FUSE로 대체하면서 정책을 유연하게 바꿀 수 있게 됐다.

## 스토리지 데몬들

스토리지 관리는 여러 데몬이 협업한다. 중심은 <strong>vold</strong>(Volume Daemon)다.

![vold 이벤트 흐름 — 커널 uevent에서 vold를 거쳐 StorageManagerService로 Binder 콜백하고 FUSE 데몬에 mount를 지시해 앱의 /storage 뷰가 만들어지며, storaged·storagestats가 I/O·사용량을 집계하는 구조](/images/study-android-internals/05-vold-flow-light.png)
![vold 이벤트 흐름 — 커널 uevent에서 vold를 거쳐 StorageManagerService로 Binder 콜백하고 FUSE 데몬에 mount를 지시해 앱의 /storage 뷰가 만들어지며, storaged·storagestats가 I/O·사용량을 집계하는 구조](/images/study-android-internals/05-vold-flow-dark.png)

- <strong>vold</strong> — 볼륨의 생명주기를 관리하는 네이티브 데몬. SD카드 삽입/제거 같은 이벤트를 커널의 <strong>uevent</strong>(netlink 소켓)로 받아, 마운트/언마운트/포맷을 수행한다. 동시에 <strong>`StorageManagerService`</strong>(프레임워크)에 Binder로 상태 변화를 알린다. 암호화 볼륨 준비, Adoptable 스토리지 설정, FBE 키 설치도 vold의 몫이다.
- <strong>StorageManagerService</strong> — 프레임워크 측 창구. vold의 저수준 동작을 앱과 시스템 서비스에 API로 노출한다. 앱이 보는 `StorageManager`가 이 서비스에 Binder로 연결된다([CH9. 서비스 아키텍처](/study/android-internals/09-service-architecture)).
- <strong>storaged</strong> — I/O 통계 수집 데몬. per-uid 디스크 읽기/쓰기량, foreground/background I/O를 집계한다.
- <strong>storagestats</strong> — 앱·유저·패키지별 스토리지 사용량(코드/데이터/캐시)을 계산해 설정 화면의 "저장공간" 항목에 데이터를 제공한다.

이벤트 흐름을 한 줄로 요약하면 이렇다 — <strong>커널 uevent → vold가 감지·마운트 → StorageManagerService에 Binder 알림 → 필요 시 FUSE 데몬으로 앱별 뷰 생성</strong>. 앱은 결국 자기 mount namespace에서 권한에 맞는 `/storage` 뷰를 보게 된다.

```bash
# vold가 관리하는 볼륨 상태 확인
adb shell dumpsys mount | head -40
# storaged가 본 per-uid I/O 통계
adb shell dumpsys storaged 2>/dev/null | head
```

## APEX — Mainline의 심장

지금까지의 파티션·마운트는 "OS를 어떻게 올리는가"였다. <strong>APEX</strong>(Android Pony EXpress)는 "OS의 일부를 어떻게 <strong>앱처럼 업데이트</strong>하는가"에 대한 답이다.

### 등장 배경 — Project Mainline

문제는 이랬다. 미디어 코덱, 타임존 데이터, 네트워크 스택 같은 저수준 컴포넌트에 보안 취약점이 생기면, 예전에는 <strong>전체 OTA</strong>를 만들어 기기를 재부팅시키며 갈아야 했다. OEM과 통신사를 거치는 이 경로는 느리고, 상당수 기기는 아예 패치를 못 받았다.

<strong>Project Mainline</strong>(10.0)은 이 컴포넌트들을 <strong>Google Play를 통해 직접 업데이트</strong>할 수 있게 모듈화했다. 그런데 앱(APK)만으로는 부족하다 — 미디어 코덱 같은 건 네이티브 라이브러리·데몬·설정을 포함하는 "OS 조각"이라, APK가 담기 어려운 것들이 들어간다. 그래서 만든 새 컨테이너 포맷이 APEX다.

### APEX 파일 구조

APEX는 확장자가 `.apex`인 ZIP 컨테이너다. 안을 열면 다음이 들어 있다.

![APEX 파일 구조와 apexd 활성화 — apex_payload.img·apex_manifest.pb·apex_pubkey·AndroidManifest.xml로 구성된 APEX와, apexd의 verify→mount→activate 파이프라인](/images/study-android-internals/05-apex-structure-light.png)
![APEX 파일 구조와 apexd 활성화 — apex_payload.img·apex_manifest.pb·apex_pubkey·AndroidManifest.xml로 구성된 APEX와, apexd의 verify→mount→activate 파이프라인](/images/study-android-internals/05-apex-structure-dark.png)

- <strong>apex_payload.img</strong> — 실제 내용이 담긴 ext4(또는 erofs) 파일시스템 이미지. 라이브러리·바이너리·설정이 정상 디렉토리 구조로 들어 있고, dm-verity 해시 트리가 붙어 무결성이 보장된다.
- <strong>apex_manifest.pb</strong> — 모듈 이름과 버전을 담은 protobuf 메타데이터. `apexd`가 어떤 버전을 활성화할지 판단하는 근거다.
- <strong>apex_pubkey</strong> — 이 APEX 서명 검증에 쓰는 공개키.
- <strong>AndroidManifest.xml</strong> — 패키지 매니저가 APEX를 인식·설치 관리하기 위한 메타데이터(APK와 형식을 공유).

### apexd 실행 흐름

부팅 초기에 <strong>`apexd`</strong> 데몬이 설치된 APEX들을 활성화한다. 흐름은 세 단계다.

1. <strong>verify</strong> — APEX 서명과 `apex_payload.img`의 dm-verity 해시를 검증한다. 롤백 인덱스를 확인해 다운그레이드 공격도 막는다. 신뢰 사슬은 AVB와 연결된다([CH16](/study/android-internals/16-selinux-avb)).
2. <strong>mount</strong> — `apex_payload.img`를 loop 디바이스로 `/apex/<name>@<version>` 경로에 마운트한다. 파일 하나가 정상 파일시스템으로 펼쳐진다.
3. <strong>activate</strong> — 버전 붙은 경로를 버전 없는 `/apex/<name>`으로 bind mount해 노출하고, <strong>`linkerconfig`</strong>를 다시 생성한다. linkerconfig는 APEX가 제공하는 라이브러리를 다른 프로세스가 찾을 수 있도록 링커 namespace(`ld.config.txt`)를 갱신한다([CH15](/study/android-internals/15-native-level)).

부팅 시 `/apex`에는 파티션(system)에 프리로드된 APEX가 먼저 올라오고, 이후 `/data`에 다운로드된 업데이트 버전이 있으면 그쪽으로 교체된다. 그래서 Play로 받은 새 코덱이 재부팅 후 활성화되는 것이다.

```bash
# 활성화된 APEX 목록과 버전
adb shell ls /apex
adb shell cmd -w apexservice getActivePackages 2>/dev/null
# 하나가 loop로 마운트된 모습
adb shell mount | grep apex | head
```

<strong>flattened vs compressed</strong> 구분도 알아둘 만하다. 개발/에뮬레이터 빌드에서는 `apex_payload.img` 없이 내용을 디렉토리로 펼친 <strong>flattened APEX</strong>를 쓰기도 한다(loop mount 부담 회피). 반대로 양산 기기의 프리로드 APEX는 스토리지 절약을 위해 <strong>compressed APEX</strong>(`.capex`)로 두고, 필요할 때 `/data`에 풀어서 활성화한다.

## Obb/ASec 레거시

APEX 이전 시대의 컨테이너 두 개는 이름만 정리하고 넘어간다.

- <strong>OBB</strong>(Opaque Binary Blob) — 게임 등 대용량 앱이 APK와 별도로 배포하는 확장 리소스 파일(`.obb`). 지금도 일부 쓰이며, `/storage`의 `Android/obb/` 아래에 놓인다.
- <strong>ASEC</strong>(Android Secure External Caching) — 예전 "앱을 SD카드에 설치"(apps2sd) 시절 암호화 컨테이너였다. Adoptable Storage로 대체되며 사실상 폐기됐다.

::: tip 핵심 정리
- loop mount는 파일을 파일시스템처럼, bind mount는 한 디렉토리를 여러 경로에, mount namespace는 프로세스마다 다른 마운트 뷰를 만든다. APEX와 외부 스토리지가 이들을 조합해 동작한다.
- `fs_mgr`가 `fstab.{hardware}`를 읽어 파티션을 마운트하며, `fs_mgr_flags`(wait·check·avb·slotselect·logical 등)가 안드로이드 고유의 마운트 정책을 담는다.
- 외부 스토리지는 Portable/Adoptable로 나뉘고, Scoped Storage는 FUSE 데몬+MediaProvider로 앱별 접근을 격리한다.
- vold가 커널 uevent를 받아 마운트하고 StorageManagerService에 Binder로 알리며, storaged/storagestats가 I/O·사용량을 집계한다.
- APEX는 Mainline의 컨테이너로, apex_payload.img를 담고 apexd가 verify→mount(loop)→activate(bind + linkerconfig) 순으로 활성화한다. OS 조각을 Play로 업데이트하는 기반이다.
:::

## 다음 챕터

[CH6. 시스템 이미지와 업데이트](/study/android-internals/06-images-updates)에서는 이 파티션·APEX가 담긴 이미지 전체가 어떻게 만들어지고 배포되는지를 다룬다. 팩토리 이미지와 OTA 패키지의 구성물, sparse image·boot.img 해부, fastboot·recovery·update_engine 업데이트 경로, 그리고 GSI/DSU로 커스텀 이미지를 임시 부팅하는 법까지 파고든다.
