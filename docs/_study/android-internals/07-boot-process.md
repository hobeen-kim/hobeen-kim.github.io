---
title: "CH7. 부트로더와 커널 부팅"
description: "Boot ROM부터 2차 부트로더, ABL/LK, 커널, initramfs, first/second-stage init까지 이어지는 안드로이드 신뢰 체인과 부트 컨트롤 HAL의 슬롯 롤백을 다룬다."
date: 2026-07-13
tags: [android, aosp, boot, bootloader, kernel]
---

# CH7. 부트로더와 커널 부팅

## 학습 목표
- Boot ROM(PBL)부터 init까지 이어지는 부트체인과 신뢰 체인(chain of trust)의 구조를 이해한다.
- Little Kernel(LK/ABL)의 역할, fastboot 모드 진입, boot image 로드 과정을 안다.
- 부트로더 락/언락이 AVB·사용자 데이터에 미치는 영향을 파악한다.
- 커널 cmdline(`androidboot.*`)과 DTB 전달, initramfs와 first/second-stage init 분리를 이해한다.
- Boot Control HAL의 A/B 슬롯 관리와 부팅 실패 시 롤백 메커니즘을 안다.

## 1. 부트체인 개관 — 전원부터 init까지

전원 버튼을 누른 순간부터 안드로이드 홈 화면이 뜨기까지, 실행 주체는 여러 번 바뀐다. 각 단계는 자기 다음에 실행할 코드의 서명을 검증한 뒤에만 제어를 넘긴다. 이 사슬을 <strong>신뢰 체인(chain of trust)</strong>이라 부르고, 그 시작점은 SoC 안에 물리적으로 구워진 불변 코드다.

![Boot ROM부터 2차 부트로더, Android Bootloader, 커널, init까지 각 단계가 다음 단계 서명을 검증하며 실행을 넘기는 부트체인](/images/study-android-internals/07-boot-chain-light.png)
![Boot ROM부터 2차 부트로더, Android Bootloader, 커널, init까지 각 단계가 다음 단계 서명을 검증하며 실행을 넘기는 부트체인](/images/study-android-internals/07-boot-chain-dark.png)

- <strong>Boot ROM(PBL, Primary Bootloader)</strong>은 SoC 제조 시점에 마스크 ROM으로 박힌 코드다. 수정도 삭제도 불가능하며, 이것이 신뢰 체인의 <strong>루트 오브 트러스트(hardware root of trust)</strong>다. PBL은 SoC 내부 eFuse에 구워진 공개키 해시로 다음 단계(2차 부트로더)의 서명을 검증한다. 검증에 실패하면 그 자리에서 부팅을 멈춘다.
- <strong>2차 부트로더</strong>는 SoC 벤더마다 이름이 다르다. Qualcomm은 XBL(eXtensible Bootloader, UEFI 기반), Samsung Exynos는 S-BOOT, MediaTek은 Preloader라 부른다. 이 단계에서 DRAM 초기화, 클럭·전원 설정, 저장장치(UFS/eMMC) 드라이버 초기화 같은 저수준 하드웨어 준비가 끝난다. Qualcomm 계열은 XBL이 다시 여러 하위 이미지(ABL, keymaster TA 등)를 로드하는 다단계 구조다.
- <strong>Android Bootloader(ABL 또는 LK)</strong>가 안드로이드 특화 로직을 담당한다. `boot` 파티션에서 커널+ramdisk를 읽어 메모리에 올리고, cmdline을 구성하고, fastboot 모드나 recovery 진입을 처리한다. 뒤 2절에서 자세히 다룬다.
- <strong>Linux Kernel</strong>이 압축 해제돼 실행되면 메모리 관리·스케줄러·드라이버가 올라오고, 마지막에 initramfs 안의 `/init`을 PID 1로 실행한다.
- <strong>init(PID 1)</strong>이 유저스페이스의 첫 프로세스로, 여기서부터 [CH8](/study/android-internals/08-init-zygote)의 세계가 시작된다.

::: info 신뢰 체인이 끊기면
서명 검증에 실패하면 단계에 따라 동작이 다르다. PBL/XBL 단계 실패는 대개 벽돌(brick)에 가깝고, ABL이 boot 이미지 검증에 실패하면 기기 상태에 따라 부팅 거부, 경고 후 진행(언락 상태), recovery 진입 중 하나로 갈린다. 이 검증 로직이 곧 [CH16](/study/android-internals/16-selinux-avb)에서 다룰 Android Verified Boot(AVB)다.
:::

## 2. Little Kernel(LK)과 Android Bootloader

`LK`(Little Kernel)는 원래 임베디드용 경량 커널/부트로더 프로젝트다. Qualcomm이 이를 안드로이드 부트로더로 채택하면서 사실상 표준처럼 퍼졌고, 오늘날 ABL(Android Boot Loader, UEFI 앱 형태로 빌드된 LK)로 진화했다. 이름이 무엇이든 이 단계가 하는 일은 공통적이다.

<strong>부트 이미지 로드.</strong> `boot` 파티션의 이미지는 단순 커널 바이너리가 아니라 정해진 헤더 포맷을 가진 컨테이너다. `boot.img`는 헤더 + 커널 + ramdisk(+ 예전엔 second-stage 정보)로 구성되고, 헤더에 각 섹션의 크기와 로드 주소, cmdline이 들어 있다. 부트 이미지 버전은 안드로이드 릴리스마다 진화해왔다.

- <strong>v0~v1</strong>: 커널 + ramdisk가 `boot`에 함께.
- <strong>v2</strong>: DTB/DTBO 관련 필드 추가.
- <strong>v3~v4</strong>(Android 11+): ramdisk가 <strong>generic ramdisk</strong>(`boot`)와 <strong>vendor ramdisk</strong>(`vendor_boot`)로 분리됐다. GKI(Generic Kernel Image) 정책에 따라 Google이 서명한 공통 커널과 벤더 모듈을 분리하기 위한 구조다. [CH14](/study/android-internals/14-building-aosp)에서 GKI를 다룬다.

`unpack_bootimg`, `mkbootimg` 같은 AOSP 도구로 이미지를 뜯어보고 다시 조립할 수 있다.

```bash
# boot.img를 뜯어 헤더·커널·ramdisk를 분리
unpack_bootimg --boot_img boot.img --out ./out
# 헤더 필드(버전·cmdline·페이지 크기 등) 확인
unpack_bootimg --boot_img boot.img --format=mkbootimg
```

<strong>fastboot 모드 진입.</strong> ABL은 부팅 초기에 특정 조건을 만족하면 커널로 넘어가는 대신 fastboot 프로토콜 데몬으로 들어간다. 진입 조건은 보통 세 가지다 — 볼륨 다운 등 물리 키 조합, `boot` 파티션이 없거나 손상됨, 또는 실행 중인 안드로이드에서 `adb reboot bootloader`로 진입. fastboot 모드에서는 USB로 파티션을 직접 플래시하거나 이미지를 임시로 부팅할 수 있다.

```bash
fastboot devices                 # 연결된 fastboot 기기 확인
fastboot getvar all              # 부트로더 변수 덤프 (슬롯·언락 상태 등)
fastboot boot custom_boot.img    # 플래시 없이 이미지로 1회 부팅
fastboot flash boot boot.img     # boot 파티션에 실제 기록
```

::: info bootloader vs fastbootd
전통적 `fastboot`는 부트로더 안에서 도는 저수준 모드다. Android 10부터는 `fastbootd`가 추가됐는데, 이건 <strong>userspace fastboot</strong>로 recovery/ramdisk 안에서 실행된다. 동적 파티션(super) 안의 논리 파티션은 부트로더가 이해하지 못하므로, `fastboot flash system` 같은 명령은 `fastboot reboot fastboot`로 fastbootd에 진입한 뒤에 처리한다. 동적 파티션은 [CH5](/study/android-internals/05-storage-management)에서 다뤘다.
:::

## 3. 부트로더 락/언락

출고 상태의 부트로더는 <strong>락(locked)</strong>돼 있다. 락 상태에서는 AVB 검증에 통과한, 즉 OEM이 서명한 `boot`/`vbmeta` 이미지만 실행된다. 커스텀 이미지를 올리려면 언락이 필요하다.

```bash
fastboot flashing unlock          # 언락 요청 → 기기 화면에서 물리 확인
fastboot flashing lock            # 다시 락
fastboot flashing get_unlock_ability   # 언락 허용 여부(1/0)
```

언락은 단순히 "커스텀 이미지 허용" 스위치가 아니다. <strong>보안·데이터에 세 가지 영향</strong>을 준다.

- <strong>강제 데이터 초기화.</strong> `flashing unlock`을 실행하면 기기는 반드시 `/data`를 완전히 wipe한다. 도난당한 기기를 언락해 잠금화면을 우회하고 데이터를 빼내는 공격을 막기 위한 설계다. 이 wipe는 우회할 수 없다.
- <strong>AVB 상태 변경.</strong> 언락하면 부팅 시 노란색/주황색 경고 화면(`androidboot.verifiedbootstate`가 `orange`)이 뜬다. 락 + 정품 서명은 `green`, 락 + 커스텀 키는 `yellow`, 언락은 `orange`, 검증 실패는 `red`로 상태가 구분된다. 이 상태는 [CH16](/study/android-internals/16-selinux-avb)에서 Keystore 어테스테이션에도 반영된다.
- <strong>롤백 보호와 무결성 신호.</strong> 언락 상태에서는 dm-verity 강제가 완화되거나 꺼질 수 있어, SafetyNet/Play Integrity 같은 무결성 판정에서 기기가 실패로 분류된다. 결제·뱅킹 앱이 언락 기기에서 동작을 거부하는 이유다.

임베디드 기기를 개발할 때는 개발 단계에서 언락 상태로 커스텀 이미지를 반복 플래시하다가, 양산 시점에 자체 서명 키로 락(`avb_custom_key`)을 걸어 무결성을 확보하는 흐름을 밟는다.

## 4. 커널 부팅 — cmdline, DTB, 그리고 init까지

ABL이 커널로 제어를 넘길 때 두 가지를 함께 전달한다 — <strong>커널 cmdline</strong>과 <strong>DTB(Device Tree Blob)</strong>다.

<strong>커널 cmdline</strong>에는 부팅 파라미터가 공백으로 구분돼 들어간다. 안드로이드 특화 파라미터는 `androidboot.` 접두어를 가지며, 커널이 이를 읽어 나중에 유저스페이스 프로퍼티로 승격시킨다. 실행 중인 기기에서 확인할 수 있다.

```bash
adb shell cat /proc/cmdline
# 예시:
# androidboot.hardware=qcom androidboot.slot_suffix=_a \
# androidboot.verifiedbootstate=green androidboot.serialno=... \
# androidboot.boot_devices=soc/1d84000.ufshc console=ttyMSM0,115200
```

`androidboot.*` 파라미터는 [CH8](/study/android-internals/08-init-zygote)에서 다룰 `ro.boot.*` 프로퍼티로 변환된다. 예를 들어 `androidboot.hardware=qcom`은 `ro.boot.hardware=qcom`이 되고, 이는 다시 `ro.hardware`로 굳어져 HAL 라이브러리 이름 결정 등에 쓰인다. Android 12부터는 이 커널 cmdline 대신 `bootconfig`(별도 영역에 담긴 부팅 설정)로 옮겨가는 추세이며, `/proc/bootconfig`에서 볼 수 있다.

<strong>DTB(Device Tree)</strong>는 SoC의 하드웨어 구성(메모리 맵, 인터럽트, 주변장치 노드)을 커널에 알려주는 이진 트리다. GKI 정책 아래에서 커널은 특정 보드를 몰라야 하므로, 보드별 하드웨어 정보는 코드가 아닌 데이터(DTB)로 분리돼 `dtb`/`dtbo` 파티션이나 `vendor_boot`에 담긴다. ABL이 실행 중인 보드에 맞는 DTB를 골라 커널에 넘긴다. CAN 컨트롤러 같은 [주변장치](/study/can/13-socketcan-basics)를 SPI로 붙일 때도 이 device tree에 노드를 추가해 커널이 드라이버를 바인딩하게 만든다.

커널은 초기화를 마치면 initramfs를 루트 파일시스템(rootfs)으로 마운트하고 `/init`을 `execve`한다. 이 순간 커널의 역할은 끝나고 유저스페이스가 시작된다.

## 5. initramfs와 first/second-stage init 분리

<strong>initramfs</strong>(initial RAM filesystem)는 커널이 진짜 저장장치를 마운트하기 전에 메모리 위에 올려두는 초기 루트 파일시스템이다. ramdisk 안에는 최소한의 것만 들어 있다.

- `/init` — 정적 링크된 init 실행 파일(공유 라이브러리 없이 혼자 뜰 수 있어야 하므로).
- `*.rc` — first-stage에서 필요한 최소 rc 스크립트.
- `/system/etc/ramdisk/` 계열 fstab, AVB용 `vbmeta` 관련 정보.
- 부팅에 필요한 커널 모듈(`vendor_boot`의 vendor ramdisk에 위치).

과거에는 initramfs가 곧 최종 루트였지만, Android 10 무렵부터 <strong>system-as-root</strong>와 함께 init이 두 단계로 뚜렷이 나뉘었다.

![initramfs 안에서 도는 first-stage init이 파일시스템을 마운트하고 SELinux를 켠 뒤 execv로 second-stage init에 실행을 넘기는 구조](/images/study-android-internals/07-first-second-init-light.png)
![initramfs 안에서 도는 first-stage init이 파일시스템을 마운트하고 SELinux를 켠 뒤 execv로 second-stage init에 실행을 넘기는 구조](/images/study-android-internals/07-first-second-init-dark.png)

- <strong>first-stage init</strong>은 ramdisk 안의 정적 링크 바이너리다. 하는 일은 "진짜 파일시스템을 마운트할 수 있는 상태를 만드는 것"에 집중돼 있다 — `/dev`·`/proc`·`/sys` 마운트, early property 초기화, fstab을 읽어 `/system`·`/vendor` 등 핵심 파티션 마운트, dm-verity(AVB) 설정, SELinux 정책 로드 후 enforcing 전환. 마지막으로 자기 자신을 `/system/bin/init`으로 다시 `execve`한다.
- <strong>second-stage init</strong>은 방금 마운트한 `/system` 위의 동적 링크 init이다. 여기서 `libbase`, `libselinux` 등 정상적인 공유 라이브러리를 쓸 수 있고, `property_service`를 띄우고, ueventd로 `/dev` 노드를 만들고, 본격적으로 `*.rc` 파일을 파싱해 서비스들을 기동한다.

두 단계로 나눈 이유는 명확하다. 파일시스템과 SELinux가 준비되기 전에는 쓸 수 있는 자원이 극히 제한되므로, 그 최소 환경에서 돌 정적 바이너리(first-stage)와 완전한 환경에서 돌 동적 바이너리(second-stage)를 갈라놓은 것이다. 중요한 점은 <strong>execve로 이어지므로 PID는 계속 1</strong>이라는 것 — 새 프로세스를 fork하는 게 아니라 같은 프로세스가 자기 이미지만 바꿔 낀다.

```bash
# 실행 중 기기에서 init이 second-stage로 넘어간 뒤의 상태
adb shell ls -l /proc/1/exe     # → /system/bin/init 를 가리킴
adb shell cat /proc/1/cmdline   # → /system/bin/init second_stage
```

## 6. Boot Control HAL과 A/B 슬롯 롤백

현대 안드로이드 기기 대부분은 <strong>A/B(seamless) 업데이트</strong> 구조를 쓴다. `boot`, `system`, `vendor` 같은 핵심 파티션이 `_a`/`_b` 두 벌 존재하고, 한쪽(active)으로 부팅하는 동안 다른 쪽(inactive)에 OTA를 적용한다. A/B 자체는 [CH6](/study/android-internals/06-images-updates)에서 다뤘고, 여기서는 <strong>어느 슬롯으로 부팅할지와 실패 시 롤백을 관리하는 계층</strong>인 Boot Control HAL을 본다.

<strong>Boot Control HAL</strong>(과거 `android.hardware.boot@1.x` HIDL, 현재 `android.hardware.boot` AIDL)은 부트로더가 관리하는 슬롯 메타데이터를 유저스페이스에서 읽고 쓰는 인터페이스다. 슬롯마다 세 가지 상태 플래그가 있다.

- <strong>active</strong> — 다음에 부팅을 시도할 슬롯.
- <strong>bootable</strong> — 부팅 가능하다고 표시된 슬롯. 남은 시도 횟수(retry count)를 가진다.
- <strong>successful</strong> — 부팅에 성공해 안정 상태로 표시된 슬롯.

<strong>롤백 시나리오</strong>는 이렇게 흐른다. OTA가 inactive 슬롯(예: `_b`)에 새 이미지를 쓰고 그 슬롯을 active로, retry count를 N(보통 7)으로 설정한다. 재부팅하면 부트로더는 `_b`로 부팅을 시도하며 retry count를 하나 줄인다. 부팅이 끝까지 성공해 안드로이드가 `markBootSuccessful()`을 호출하면 슬롯이 `successful`로 굳는다. 그러나 부팅이 계속 실패해 retry count가 0에 도달하면, 부트로더는 `_b`를 unbootable로 표시하고 <strong>이전에 successful이던 `_a` 슬롯으로 자동 롤백</strong>한다. 이 덕분에 망가진 OTA가 기기를 영구 벽돌로 만들지 않는다.

```bash
# 현재 슬롯 확인
adb shell getprop ro.boot.slot_suffix     # → _a 또는 _b

# bootctl로 슬롯 메타데이터 조회·조작 (root/AOSP 빌드)
adb shell bootctl get-current-slot        # 현재 부팅한 슬롯 번호
adb shell bootctl get-suffix 1            # 슬롯 1의 접미사(_b)
adb shell bootctl set-active-boot-slot 0  # 다음 부팅 슬롯을 강제 지정
adb shell bootctl mark-boot-successful    # 현재 슬롯을 성공으로 표시
```

`update_engine`이 OTA 적용 중에 이 HAL을 호출해 대상 슬롯을 active로 세팅하고, 부팅 성공 판정 로직이 `markBootSuccessful`을 부른다. 커스텀 임베디드 기기를 A/B로 구성하면, 현장에서 잘못된 업데이트가 배포돼도 기기가 스스로 이전 버전으로 돌아오므로 원격 복구 부담이 크게 준다.

::: warning virtual A/B와 non-A/B
저가·초기 기기 중에는 슬롯이 하나뿐인 non-A/B 구조(별도 `recovery` 파티션 사용)도 있다. 반대로 Android 11+ 다수 기기는 <strong>Virtual A/B</strong>를 쓰는데, 물리적으로 파티션을 두 벌 두는 대신 snapshot(dm-snapshot)으로 A/B 효과를 낸다. 어느 구조든 Boot Control HAL 인터페이스 자체는 동일하게 유지돼, 상위 `update_engine` 로직은 바뀌지 않는다.
:::

::: tip 핵심 정리
- 부팅은 Boot ROM(PBL, 하드웨어 루트 오브 트러스트) → 2차 부트로더(XBL/S-BOOT/Preloader) → ABL/LK → 커널 → init 순서로, 각 단계가 다음 단계 서명을 검증하는 신뢰 체인이다.
- ABL/LK는 `boot` 이미지를 로드하고 cmdline·DTB를 커널에 넘기며, 조건에 따라 fastboot/fastbootd 모드로 진입한다.
- `fastboot flashing unlock`은 커스텀 이미지를 허용하는 대신 강제로 `/data`를 wipe하고 AVB 상태를 orange로 바꿔 무결성 판정을 실패시킨다.
- 커널은 initramfs의 `/init`을 PID 1로 실행하고, init은 정적 first-stage(파일시스템·SELinux 준비) → `execve` → 동적 second-stage(서비스 기동)로 나뉘며 PID 1을 유지한다.
- Boot Control HAL은 A/B 슬롯의 active/bootable/successful 상태를 관리해, OTA 부팅이 retry count 안에 성공하지 못하면 직전 successful 슬롯으로 자동 롤백한다.
:::

## 다음 챕터
[CH8. init과 Zygote](/study/android-internals/08-init-zygote)에서는 PID 1 init의 rc 파일 문법과 서비스 정의, System Properties 심층 구조, 그리고 모든 앱의 부모가 되는 Zygote fork 모델을 파헤친다.
