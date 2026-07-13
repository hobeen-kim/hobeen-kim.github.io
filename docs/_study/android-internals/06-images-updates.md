---
title: "CH6. 시스템 이미지와 업데이트"
description: "팩토리 이미지와 OTA 패키지의 구성물, sparse image·super_empty·boot.img 버전별 해부, fastboot·recovery·update_engine과 Virtual A/B 업데이트 경로, 그리고 GSI/DSU로 커스텀 이미지를 임시 부팅하는 법을 다룬다."
date: 2026-07-13
tags: [android, aosp, ota, boot-image, update-engine, gsi, dsu]
---

# CH6. 시스템 이미지와 업데이트

## 학습 목표
- 팩토리 이미지와 OTA 패키지의 구성물(payload.bin·care_map 등)을 해부할 수 있다.
- Android sparse image·super_empty·block-based update 같은 표준 페이로드 포맷을 이해한다.
- boot.img의 버전별(v0~v4) 구조와 vendor_boot·init_boot 분리를 파악한다.
- fastboot·recovery·update_engine·Virtual A/B로 이어지는 업데이트 경로를 설명한다.
- GSI와 DSU로 커스텀 시스템 이미지를 임시 부팅하는 법을 안다(커스텀 OS 개발에 유용).

## 팩토리 이미지와 OTA 패키지

기기에 안드로이드를 얹는 방법은 크게 둘이다. <strong>팩토리 이미지</strong>는 스토리지를 통째로 채우는 "전체 설치본"이고, <strong>OTA 패키지</strong>는 이미 돌고 있는 기기를 새 버전으로 올리는 "업데이트본"이다.

팩토리 이미지 zip을 풀면 대략 이렇게 생겼다.

- <strong>bootloader.img, radio.img</strong> — 부트로더와 모뎀 펌웨어.
- <strong>boot.img, vendor_boot.img, init_boot.img, dtbo.img, vbmeta.img</strong> — 부팅 관련 파티션 이미지들([CH3](/study/android-internals/03-partitions-filesystems)).
- <strong>super.img</strong> 또는 <strong>super_empty.img</strong> + 개별 논리 파티션 이미지 — 동적 파티션 컨테이너.
- <strong>flash-all.sh / flash-all.bat</strong> — 위 이미지들을 fastboot로 순서대로 굽는 스크립트.

OTA 패키지(`ota.zip`)는 구성이 다르다. A/B 기기의 핵심 파일은 다음과 같다.

- <strong>payload.bin</strong> — 업데이트의 본체. 각 파티션을 새 상태로 만들기 위한 연산(전체 이미지 또는 블록 델타)이 담긴 바이너리. `update_engine`이 이걸 읽어 비활성 슬롯에 적용한다.
- <strong>payload_properties.txt</strong> — payload의 크기·해시·메타데이터. 스트리밍 OTA 시 서버가 이 값으로 무결성을 검증한다.
- <strong>care_map.txt</strong> — 파티션에서 "실제로 데이터가 있는 블록" 범위. 빈 블록까지 검증·복사하지 않도록 알려줘 시간과 대역폭을 아낀다.
- <strong>metadata</strong> — 대상 빌드 지문(fingerprint), 적용 전후 버전 조건 등.

```bash
# OTA zip 안을 열어 구성물 확인 (호스트에서)
unzip -l ota.zip | grep -E 'payload|care_map|metadata'
```

## 표준 페이로드 포맷

이미지 파일들은 몇 가지 표준 포맷을 쓴다. 이걸 알아야 이미지를 열어보고 수정할 수 있다.

<strong>Android sparse image</strong>는 파티션 이미지의 기본 배포 포맷이다. 파티션 대부분이 0으로 채워진 빈 공간이라, 이를 "이 구간은 전부 0" 같은 메타데이터로 압축해 파일 크기를 줄인다. fastboot가 이 포맷을 이해해 굽는다. 사람이 마운트해 내용을 보려면 raw로 풀어야 하는데, 이때 쓰는 도구가 <strong>`simg2img`</strong>다.

```bash
# sparse → raw 변환 후 마운트해서 내용 보기 (호스트, root)
simg2img system.img system.raw.img
sudo mount -o ro,loop system.raw.img /mnt/system
ls /mnt/system
```

<strong>super_empty.img</strong>는 super 파티션의 <strong>메타데이터만 담은 껍데기</strong>다. 논리 파티션의 레이아웃(이름·크기·슬롯)만 있고 실제 데이터는 없다. fastboot가 이걸로 super의 파티션 테이블을 초기화한 뒤, `fastboot update`나 개별 `fastboot flash`로 각 논리 파티션을 채운다. `liblp`([CH3](/study/android-internals/03-partitions-filesystems))의 `lpmake`가 이 이미지를 만든다.

<strong>block-based update</strong>는 non-A/B OTA(recovery 방식)에서 쓰던 델타 포맷이다. `transfer.list`가 "이 블록을 저 블록으로 옮기고, 이 블록에 이 데이터를 써라" 같은 명령 목록을 담고, updater가 이를 실행해 `system`을 in-place로 패치한다. 재부팅 중 전원이 나가도 이어서 적용할 수 있도록 설계됐지만, A/B의 등장으로 신규 기기에서는 비중이 줄었다.

## boot.img 해부

`boot.img`는 부트로더가 커널을 찾는 파티션이며, 헤더 버전에 따라 구조가 크게 다르다. 공통 골격은 <strong>boot header + 커널 + ramdisk</strong>이고, 매직 `ANDROID!`로 시작한다.

![boot.img 버전별 구조 — v0~v2 통합형(header·kernel·ramdisk·second/dtb)과 GKI 분리형(boot.img=GKI 커널, init_boot.img=generic ramdisk, vendor_boot.img=vendor ramdisk+DTB)의 비교](/images/study-android-internals/06-boot-img-light.png)
![boot.img 버전별 구조 — v0~v2 통합형(header·kernel·ramdisk·second/dtb)과 GKI 분리형(boot.img=GKI 커널, init_boot.img=generic ramdisk, vendor_boot.img=vendor ramdisk+DTB)의 비교](/images/study-android-internals/06-boot-img-dark.png)

- <strong>v0~v2</strong> — 통합형. header 뒤에 커널·ramdisk가 이어지고, v1은 recovery DTBO, v2는 DTB를 추가로 담을 수 있다. 이 시절 ramdisk에는 `init`과 벤더 리소스가 함께 들어 있었다.
- <strong>v3</strong>(11+, GKI) — 커널을 벤더와 분리한다. `boot.img`는 <strong>GKI 커널 + generic ramdisk</strong>만 담고, 벤더 ramdisk와 DTB는 별도 <strong>`vendor_boot.img`</strong>로 뺀다. 구글이 커널을, 벤더가 vendor_boot를 각각 갱신할 수 있게 됐다.
- <strong>v4</strong>(13+) — GKI를 더 밀어붙여 generic ramdisk마저 <strong>`init_boot.img`</strong>로 분리한다. 이제 `boot.img`는 사실상 <strong>순수 GKI 커널</strong>만 담는다. `vendor_boot`에는 여러 ramdisk 조각을 순서대로 나열하는 `vendor_ramdisk_table`이 생겼다.

이 분리 덕분에 커널(boot)·초기 유저스페이스(init_boot)·벤더 리소스(vendor_boot)를 `update_engine`이 각각 독립적으로 갱신한다. 디렉토리 관점의 system-as-root 변천은 [CH4](/study/android-internals/04-files-directories)에서, 부팅 흐름은 [CH7](/study/android-internals/07-boot-process)에서 이어간다.

이미지를 뜯어보는 실습에는 표준 도구 `unpack_bootimg`(AOSP)나 `magiskboot`를 쓴다.

```bash
# AOSP 도구로 boot.img 언팩 (호스트)
unpack_bootimg --boot_img boot.img --out ./out
ls ./out          # kernel, ramdisk, vendor_ramdisk 등이 풀린다
# 헤더 버전 확인
unpack_bootimg --boot_img boot.img --format=info | grep -i version
```

## 업데이트 경로

새 이미지를 기기에 적용하는 경로는 목적에 따라 갈린다.

### fastboot / fastbootd

<strong>fastboot</strong>는 부트로더가 제공하는 저수준 플래싱 프로토콜이다. 개발·복구용으로, USB로 연결해 파티션에 이미지를 직접 굽는다. 그런데 동적 파티션(super)이 등장하면서 부트로더만으로는 super 안 논리 파티션을 다루기 어려워졌다. 그래서 <strong>fastbootd</strong>(userspace fastboot)가 생겼다 — 안드로이드 유저스페이스에서 도는 fastboot 구현으로, `liblp`를 써서 논리 파티션을 이해한다. `fastboot reboot fastboot`로 진입한다.

```bash
adb reboot bootloader        # 부트로더 fastboot로
fastboot getvar all          # 슬롯·상태 등 변수 덤프
fastboot reboot fastboot     # userspace fastboot(fastbootd)로
fastboot flash system_a system.img
```

### recovery 업데이트

<strong>recovery</strong>는 별도의 최소 환경(자체 커널+ramdisk)으로 부팅해 OTA를 적용하는 전통 경로다. non-A/B 기기가 여기에 의존한다. `misc` 파티션의 BCB(Bootloader Control Block)에 "recovery로 부팅하라"는 커맨드를 심어 진입하고, recovery의 updater가 `transfer.list` 기반 블록 업데이트를 적용한다([CH3](/study/android-internals/03-partitions-filesystems)).

### A/B 업데이트와 update_engine

A/B 기기의 무중단 업데이트를 담당하는 데몬이 <strong>`update_engine`</strong>이다. 흐름은 이렇다.

![A/B 무중단 업데이트 — 활성 슬롯 A로 부팅해 사용하는 동안 update_engine이 payload.bin을 비활성 슬롯 B에 백그라운드로 적용하고, 재부팅 시 슬롯을 전환하며 실패 시 A로 롤백하는 흐름](/images/study-android-internals/06-ab-update-light.png)
![A/B 무중단 업데이트 — 활성 슬롯 A로 부팅해 사용하는 동안 update_engine이 payload.bin을 비활성 슬롯 B에 백그라운드로 적용하고, 재부팅 시 슬롯을 전환하며 실패 시 A로 롤백하는 흐름](/images/study-android-internals/06-ab-update-dark.png)

- <strong>스트리밍 OTA</strong> — 전체 패키지를 다 받고 시작하는 게 아니라, 서버에서 `payload.bin`을 스트리밍하며 곧바로 비활성 슬롯에 적용한다. `/cache`에 큰 파일을 둘 필요가 없다.
- <strong>백그라운드 적용</strong> — 사용자가 기기를 쓰는 동안 조용히 다른 슬롯에 기록한다. 활성 슬롯은 건드리지 않으므로 다운타임이 0이다.
- <strong>슬롯 전환</strong> — 적용이 끝나면 `bootctl`로 새 슬롯을 active로 표시하고, 다음 재부팅 때 새 버전으로 뜬다. 부팅에 실패하면 이전 슬롯으로 자동 롤백된다([CH3](/study/android-internals/03-partitions-filesystems)).

<strong>Virtual A/B</strong>(11+)는 여기서 한 발 더 나간다. 진짜 A/B는 슬롯 두 벌만큼 스토리지를 먹는데, Virtual A/B는 <strong>스냅샷(snapshot)</strong>으로 이 비용을 줄인다. 업데이트를 원본 위에 덮어쓰지 않고 별도 <strong>Copy-On-Write(COW) 영역</strong>에 기록한 뒤, 성공하면 병합(merge)하고 실패하면 스냅샷을 버려 원상 복구한다. 동적 파티션(super)과 device-mapper의 snapshot 타깃 위에서 동작하며, non-A/B에 가까운 저장 효율로 A/B의 롤백 안전성을 얻는 것이 목표다.

```bash
# update_engine 상태·진행률 로그
adb logcat -s update_engine
# 슬롯 상태 확인
adb shell bootctl get-current-slot
```

## GSI와 DSU

여기가 커스텀 OS 개발자에게 특히 유용한 부분이다.

<strong>GSI</strong>(Generic System Image)는 구글이 배포하는 <strong>순수 AOSP `system` 이미지</strong>다. 특정 기기의 `vendor`와 조합해 부팅할 수 있도록 Treble ABI에 맞춰 빌드돼 있다. Treble이 `system`과 `vendor`를 갈라놨기 때문에, 기기의 `vendor`는 그대로 두고 `system`만 GSI로 바꿔 순정 안드로이드 동작을 확인할 수 있다. VTS(Vendor Test Suite) 통과 여부를 GSI로 검증하는 것이 대표 용도다.

<strong>DSU</strong>(Dynamic System Update, 10.0)는 GSI(또는 임의의 커스텀 system 이미지)를 <strong>기존 시스템을 건드리지 않고 임시로 부팅</strong>하게 해준다. 원본 `/data`와 `system`은 그대로 두고, DSU가 `/data`의 여유 공간에 커스텀 이미지용 논리 파티션을 임시로 만들어 그쪽으로 부팅한다. 다 쓰고 재부팅하면 원래 시스템으로 돌아온다. 이 전환을 담당하는 데몬이 <strong>`gsid`</strong>다.

```bash
# 커스텀 system.img.gz를 DSU로 임시 부팅 (개발 기기)
adb shell gsi_tool install --gsi system.img.gz --userdata-size 8G
adb reboot                    # 커스텀 이미지로 부팅
# 원래 시스템으로 복귀
adb shell gsi_tool disable    # 또는 wipe
adb reboot
```

농기계용 커스텀 안드로이드를 만들 때, 매번 파티션을 fastboot로 굽지 않고 <strong>DSU로 후보 `system` 이미지를 임시 부팅해 검증</strong>하면 반복 주기가 크게 짧아진다. 원본을 망칠 위험 없이 새 빌드를 실기기에서 돌려볼 수 있다는 점이 device bring-up([CH14](/study/android-internals/14-building-aosp)) 단계에서 큰 이점이다.

## AVB와의 관계

지금까지의 이미지·업데이트는 전부 <strong>서명과 무결성 검증</strong>을 전제로 한다. `vbmeta`가 각 파티션의 해시·서명을 담고, 부팅 시 이 신뢰 사슬을 검증하며, OTA·APEX는 롤백 인덱스로 다운그레이드를 막는다. 이 Verified Boot(AVB) 메커니즘 전체는 [CH16. SELinux와 Verified Boot](/study/android-internals/16-selinux-avb)에서 본격적으로 다룬다. 여기서는 "모든 이미지에는 서명이 붙고, 부팅·업데이트가 그것을 검증한다"는 사실만 짚고 넘어간다.

::: tip 핵심 정리
- 팩토리 이미지는 전체 설치본, OTA 패키지는 업데이트본이다. A/B OTA의 핵심은 payload.bin(본체)·care_map(유효 블록)·metadata다.
- Android sparse image는 fastboot 배포 포맷이며 `simg2img`로 raw로 풀어 마운트한다. super_empty.img는 super의 메타데이터 껍데기다.
- boot.img는 v0~v2 통합형에서 v3/v4로 가며 GKI 커널(boot)·generic ramdisk(init_boot, 13+)·vendor ramdisk+DTB(vendor_boot, 11+)로 분리됐다. `unpack_bootimg`/`magiskboot`로 해부한다.
- 업데이트 경로는 fastboot(+fastbootd)·recovery·update_engine으로 나뉘며, A/B는 비활성 슬롯에 스트리밍·백그라운드 적용 후 슬롯 전환한다. Virtual A/B는 스냅샷으로 스토리지 비용을 줄인다.
- GSI는 순수 AOSP system 이미지, DSU(gsid)는 그것을 기존 시스템을 건드리지 않고 임시 부팅하는 기능이다. 커스텀 OS 개발의 반복 검증을 크게 단축한다.
:::

## 다음 챕터

[CH7. 부트로더와 커널 부팅](/study/android-internals/07-boot-process)에서는 전원이 들어온 순간부터 부트로더가 이 이미지들을 로드하고, 커널이 올라와 첫 유저스페이스 프로세스로 넘어가기까지의 부팅 체인을 단계별로 추적한다.
