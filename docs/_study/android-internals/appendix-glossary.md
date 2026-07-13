---
title: "부록. 용어집"
description: "Android Internals 도메인에서 쓰이는 약어·용어 100여 개를 아키텍처·파티션·부팅·init·빌드·네이티브·보안·런타임·Binder 카테고리별로 풀네임과 짧은 설명, 관련 챕터 링크로 정리한 레퍼런스."
date: 2026-07-13
tags: [android, aosp, glossary, reference]
---

# 부록. 용어집

이 스터디 전 챕터에서 등장한 약어와 용어를 카테고리별로 모았다. 각 항목은 풀네임과 한두 문장 설명, 그리고 처음(또는 가장 자세히) 다룬 챕터 링크를 함께 둔다. 본문을 읽다 낯선 약어가 나오면 여기서 먼저 확인하고 돌아가면 된다. 같은 약어가 문맥에 따라 다른 뜻으로 쓰이는 경우(예: `EL`=Exception Level vs. `ELF`)는 별도 행으로 분리했다.

## 1. 아키텍처·하드웨어

부팅 이전의 물리 세계다. SoC·프로세서·신뢰 실행 환경 등 소프트웨어가 올라앉는 토대를 이룬다. 자세한 내용은 [CH1](/study/android-internals/01-architecture-evolution)·[CH2](/study/android-internals/02-hardware-soc)에서 다룬다.

| 약어/용어 | 풀네임 | 설명 | 관련 챕터 |
| --- | --- | --- | --- |
| AOSP | Android Open Source Project | 구글이 공개한 안드로이드 소스 트리 전체. 이 스터디가 커스텀하는 대상 그 자체다. | [CH1](/study/android-internals/01-architecture-evolution) |
| BSP | Board Support Package | SoC/보드 벤더가 제공하는 커널·부트로더·드라이버·HAL 묶음. AOSP를 특정 하드웨어에 올리는 출발점이다. | [CH2](/study/android-internals/02-hardware-soc) |
| SoC | System on Chip | CPU·GPU·모뎀·DSP·보안 코어를 한 다이에 통합한 칩. Qualcomm·MediaTek·Rockchip 등이 임베디드 안드로이드에 흔하다. | [CH2](/study/android-internals/02-hardware-soc) |
| SoM | System on Module | SoC에 RAM·eMMC·PMIC를 얹어 모듈화한 보드. 농기계 같은 소량 임베디드에서 bring-up 부담을 줄인다. | [CH2](/study/android-internals/02-hardware-soc) |
| ODM | Original Design Manufacturer | 완제품을 설계·제조하는 업체. `/odm` 파티션은 이들이 넣는 하드웨어별 커스터마이즈를 담는다. | [CH3](/study/android-internals/03-partitions-filesystems) |
| OEM | Original Equipment Manufacturer | 자사 브랜드로 기기를 파는 업체. `/oem` 파티션과 OEM 언락 개념이 여기서 나온다. | [CH2](/study/android-internals/02-hardware-soc) |
| ARM | Advanced RISC Machines | 안드로이드 기기 대다수가 쓰는 명령어 집합(아키텍처). AArch64가 64비트 실행 상태다. | [CH2](/study/android-internals/02-hardware-soc) |
| AArch64 | ARM 64-bit Architecture | ARMv8 이후의 64비트 실행 상태. `arm64-v8a` ABI가 이에 대응한다. | [CH15](/study/android-internals/15-native-level) |
| ABI | Application Binary Interface | 컴파일된 코드가 지키는 호출 규약·레지스터·자료형 배치. `arm64-v8a`, `x86_64` 등이 안드로이드 ABI다. | [CH15](/study/android-internals/15-native-level) |
| EL | Exception Level | ARMv8의 특권 계층(EL0 앱, EL1 커널, EL2 하이퍼바이저, EL3 시큐어 모니터). 부팅 신뢰 사슬의 물리적 기반이다. | [CH7](/study/android-internals/07-boot-process) |
| TEE | Trusted Execution Environment | 일반 OS와 격리된 보안 실행 영역. 키·지문 템플릿·DRM을 여기서 처리한다. | [CH16](/study/android-internals/16-selinux-avb) |
| TrustZone | ARM TrustZone | ARM이 제공하는 하드웨어 격리 기술. Secure World와 Normal World를 나눠 TEE를 구현한다. | [CH16](/study/android-internals/16-selinux-avb) |
| SMMU | System Memory Management Unit | 주변장치(DMA)용 MMU. IOMMU의 ARM 명칭으로 주변장치의 메모리 접근을 격리한다. | [CH2](/study/android-internals/02-hardware-soc) |
| PMIC | Power Management IC | 전압 레일·충전·리셋을 담당하는 전원 관리 칩. 부팅 최초에 레일을 세우는 주체다. | [CH13](/study/android-internals/13-power-management) |
| DTB | Device Tree Blob | 하드웨어 구성을 기술한 이진 트리. 커널이 부팅 시 읽어 어떤 주변장치가 달렸는지 파악한다. | [CH7](/study/android-internals/07-boot-process) |
| DTBO | Device Tree Blob Overlay | 기본 DTB에 보드별 차이를 덧씌우는 오버레이. `dtbo` 파티션에 담긴다. | [CH7](/study/android-internals/07-boot-process) |
| HAL | Hardware Abstraction Layer | 프레임워크와 드라이버 사이의 표준 인터페이스 계층. 요즘은 대부분 AIDL HAL로 정의된다. | [CH9](/study/android-internals/09-service-architecture) |
| HIDL | HAL Interface Definition Language | 8.0에서 도입된 HAL 인터페이스 언어. 13 이후 신규 HAL은 AIDL로 대체되며 사실상 레거시다. | [CH9](/study/android-internals/09-service-architecture) |
| Treble | Project Treble | 8.0에서 벤더 구현과 프레임워크를 분리한 아키텍처 개편. `/vendor` 분리와 VINTF의 근거다. | [CH1](/study/android-internals/01-architecture-evolution) |

## 2. 파티션·이미지·업데이트

기기의 스토리지가 어떻게 조각나고, 그 조각이 어떻게 검증·교체되는지를 다루는 용어다. [CH3](/study/android-internals/03-partitions-filesystems)·[CH5](/study/android-internals/05-storage-management)·[CH6](/study/android-internals/06-images-updates)이 주 무대다.

| 약어/용어 | 풀네임 | 설명 | 관련 챕터 |
| --- | --- | --- | --- |
| GPT | GUID Partition Table | 디스크(eMMC/UFS)의 파티션 배치를 기술하는 현대적 파티션 테이블. 안드로이드 스토리지의 기본이다. | [CH3](/study/android-internals/03-partitions-filesystems) |
| A/B | A/B (Seamless) Update | 슬롯 두 벌을 두고 한쪽을 업데이트한 뒤 재부팅으로 전환하는 무중단 업데이트 방식. 실패 시 롤백이 쉽다. | [CH6](/study/android-internals/06-images-updates) |
| super | Super Partition | `system`·`vendor`·`product` 등을 담는 동적 파티션 컨테이너. 내부는 논리 파티션으로 나뉜다. | [CH3](/study/android-internals/03-partitions-filesystems) |
| Dynamic Partition | Dynamic Partition | super 안에서 크기를 유연하게 조정할 수 있는 논리 파티션. dmsetup/LVM 유사 매핑으로 노출된다. | [CH3](/study/android-internals/03-partitions-filesystems) |
| vbmeta | Verified Boot Metadata | AVB가 각 파티션의 해시·서명·롤백 인덱스를 모아 둔 메타데이터 파티션. 신뢰 사슬의 매듭이다. | [CH16](/study/android-internals/16-selinux-avb) |
| AVB | Android Verified Boot | 부팅 이미지의 무결성·롤백 방지를 검증하는 체계. vbmeta와 dm-verity를 묶는다. | [CH16](/study/android-internals/16-selinux-avb) |
| dm-verity | Device Mapper Verity | 읽기 전용 파티션을 블록 단위 해시 트리로 검증하는 커널 기능. 변조된 블록 읽기를 즉시 차단한다. | [CH16](/study/android-internals/16-selinux-avb) |
| OTA | Over-The-Air (Update) | 네트워크로 내려받아 적용하는 시스템 업데이트. full/incremental payload로 나뉜다. | [CH6](/study/android-internals/06-images-updates) |
| GSI | Generic System Image | 벤더 구현에 무관하게 부팅되는 표준 system 이미지. Treble 호환성 검증(VTS)에 쓰인다. | [CH6](/study/android-internals/06-images-updates) |
| DSU | Dynamic System Updates | 기존 system을 지우지 않고 GSI를 임시로 나란히 부팅하는 기능. 테스트에 유용하다. | [CH6](/study/android-internals/06-images-updates) |
| sparse image | Android Sparse Image | 0으로 채운 블록을 생략해 플래시 전송량을 줄인 이미지 포맷. `simg2img`로 raw로 푼다. | [CH6](/study/android-internals/06-images-updates) |
| APEX | Android Pony EXpress | 시스템 컴포넌트를 파티션 밖에서 독립 업데이트하는 컨테이너 포맷. 모듈러 시스템의 핵심이다. | [CH5](/study/android-internals/05-storage-management) |
| Mainline | Project Mainline | APEX/APK 모듈을 Play를 통해 OS와 별개로 갱신하는 프로젝트. 보안 패치를 OTA 없이 배포한다. | [CH5](/study/android-internals/05-storage-management) |
| F2FS | Flash-Friendly File System | 플래시 스토리지에 최적화된 파일시스템. `/data`의 기본 선택지로 널리 쓰인다. | [CH3](/study/android-internals/03-partitions-filesystems) |
| EROFS | Enhanced Read-Only File System | 읽기 전용 시스템 파티션에 쓰는 압축 파일시스템. `/system` 용량·읽기 성능을 개선한다. | [CH3](/study/android-internals/03-partitions-filesystems) |
| ext4 | Fourth Extended Filesystem | 리눅스 전통 저널링 파일시스템. 구형 `/data`나 일부 파티션에 여전히 쓰인다. | [CH3](/study/android-internals/03-partitions-filesystems) |
| BCB | Bootloader Control Block | `misc` 파티션에 담기는 부트로더·recovery 명령 교환 블록. OTA 진행 상태를 주고받는다. | [CH7](/study/android-internals/07-boot-process) |
| fastboot | Fastboot Protocol | 부트로더가 노출하는 플래시·언락 프로토콜. bring-up과 이미지 굽기의 기본 도구다. | [CH14](/study/android-internals/14-building-aosp) |
| flashboot slot | Boot Slot (_a/_b) | A/B 기기에서 현재/대기 슬롯을 가리키는 접미사. `bootctl`로 active 슬롯을 조회·전환한다. | [CH6](/study/android-internals/06-images-updates) |

## 3. 부트로더·커널 부팅

전원 인가부터 커널이 유저스페이스에 제어를 넘기기까지의 단계들이다. Qualcomm 계열 명칭이 많다. [CH7](/study/android-internals/07-boot-process)이 중심이다.

| 약어/용어 | 풀네임 | 설명 | 관련 챕터 |
| --- | --- | --- | --- |
| PBL | Primary Boot Loader | SoC ROM에 마스크로 박힌 최초 실행 코드. 변경 불가하며 신뢰 사슬의 뿌리(RoT)다. | [CH7](/study/android-internals/07-boot-process) |
| SBL | Secondary Boot Loader | PBL이 로드하는 2차 부트로더. 클럭·DDR을 세우고 다음 단계를 검증·로드한다. | [CH7](/study/android-internals/07-boot-process) |
| XBL | eXtensible Boot Loader | Qualcomm의 UEFI 기반 2차 부트로더. 최신 SoC에서 SBL을 대체한다. | [CH7](/study/android-internals/07-boot-process) |
| ABL | Android Boot Loader | 리눅스/안드로이드 부팅을 담당하는 마지막 부트로더 단계. `boot`/`vbmeta`를 검증해 커널을 띄운다. | [CH7](/study/android-internals/07-boot-process) |
| LK | Little Kernel | 다수 부트로더(ABL 포함)의 뼈대가 된 경량 커널/부트로더 프레임워크. | [CH7](/study/android-internals/07-boot-process) |
| U-Boot | Das U-Boot | 임베디드에서 널리 쓰는 오픈소스 부트로더. Rockchip 등 비-Qualcomm 보드에서 흔하다. | [CH7](/study/android-internals/07-boot-process) |
| RoT | Root of Trust | 변조 불가한 하드웨어 신뢰의 시작점. 여기서부터 서명 검증이 사슬처럼 이어진다. | [CH16](/study/android-internals/16-selinux-avb) |
| initramfs | Initial RAM Filesystem | 커널이 부팅 초기에 램에 올려 마운트하는 최소 루트. first-stage init이 여기 산다. | [CH8](/study/android-internals/08-init-zygote) |
| ramdisk | Ramdisk | initramfs를 담은 압축 이미지. 최신 기기는 `boot`/`vendor_boot`로 나뉜다. | [CH7](/study/android-internals/07-boot-process) |
| GKI | Generic Kernel Image | 벤더 모듈과 분리된 공통 커널 바이너리. 커널 파편화를 줄이는 12+ 표준이다. | [CH7](/study/android-internals/07-boot-process) |
| KMI | Kernel Module Interface | GKI 커널과 벤더 모듈 사이의 안정 ABI. 커널 업데이트 시 모듈 호환을 보장한다. | [CH7](/study/android-internals/07-boot-process) |
| bootconfig | Boot Configuration | 커널 커맨드라인을 대체·보완하는 부팅 파라미터 전달 방식. `vendor_boot`에 담긴다. | [CH7](/study/android-internals/07-boot-process) |
| kaslr | Kernel Address Space Layout Randomization | 커널 주소 공간을 무작위화해 익스플로잇을 어렵게 만드는 방어 기법. | [CH16](/study/android-internals/16-selinux-avb) |
| DDR | Double Data Rate (Memory) | 주 메모리(RAM) 규격. 부트로더 초기 단계에서 트레이닝·초기화된다. | [CH7](/study/android-internals/07-boot-process) |

## 4. init·서비스·설정

커널이 넘긴 제어권을 받아 유저스페이스를 세우는 첫 프로세스와 서비스 골격이다. [CH8](/study/android-internals/08-init-zygote)·[CH9](/study/android-internals/09-service-architecture)·[CH10](/study/android-internals/10-configuration)에서 다룬다.

| 약어/용어 | 풀네임 | 설명 | 관련 챕터 |
| --- | --- | --- | --- |
| init | init (PID 1) | 유저스페이스 최초 프로세스. `.rc` 스크립트를 해석해 서비스·프로퍼티·트리거를 관리한다. | [CH8](/study/android-internals/08-init-zygote) |
| rc | init.rc / Android Init Language | init이 읽는 선언형 스크립트 언어. `service`·`on`·`trigger`로 부팅 동작을 기술한다. | [CH8](/study/android-internals/08-init-zygote) |
| property | System Property | `ro.`/`persist.`/`sys.` 등 키-값 시스템 설정 저장소. `getprop`/`setprop`으로 다룬다. | [CH10](/study/android-internals/10-configuration) |
| property_service | Property Service | init 안에서 프로퍼티 읽기·쓰기·감시를 중계하는 소켓 서비스. SELinux로 쓰기 권한을 통제한다. | [CH10](/study/android-internals/10-configuration) |
| Zygote | Zygote (App Spawner) | 미리 클래스·리소스를 로드해 둔 앱 부모 프로세스. fork로 앱을 빠르게 띄운다. | [CH8](/study/android-internals/08-init-zygote) |
| USAP | Unspecialized App Process | Zygote가 미리 fork해 대기시키는 앱 프로세스 풀. 앱 시작 지연을 더 줄인다. | [CH8](/study/android-internals/08-init-zygote) |
| system_server | System Server | 프레임워크 핵심 서비스(AMS·PMS·WMS 등)를 담는 거대 프로세스. Zygote가 최초로 낳는다. | [CH9](/study/android-internals/09-service-architecture) |
| ServiceManager | Service Manager | Binder 이름-핸들 등록소. 네임드 서비스가 여기 등록되고 조회된다(context manager). | [CH21](/study/android-internals/21-binder-userspace) |
| AMS | Activity Manager Service | 액티비티·프로세스 생명주기를 총괄하는 프레임워크 서비스. | [CH9](/study/android-internals/09-service-architecture) |
| PMS | Package Manager Service | 패키지 설치·권한·컴포넌트 정보를 관리하는 서비스. | [CH17](/study/android-internals/17-package-management) |
| VINTF | Vendor Interface | 벤더가 제공하는 HAL 집합과 프레임워크 요구를 매칭·검증하는 호환성 프레임워크. | [CH9](/study/android-internals/09-service-architecture) |
| FCM | Framework Compatibility Matrix | 프레임워크가 요구하는 HAL 버전 목록. 벤더 매니페스트와 대조해 부팅 가부를 가른다. | [CH9](/study/android-internals/09-service-architecture) |
| manifest.xml | Device/Framework Manifest | 기기가 실제 제공하는 HAL을 선언한 VINTF 문서. FCM과 짝을 이룬다. | [CH9](/study/android-internals/09-service-architecture) |
| lmkd | Low Memory Killer Daemon | 메모리 압박 시 프로세스를 선별 종료하는 유저스페이스 데몬. PSI를 신호로 쓴다. | [CH13](/study/android-internals/13-power-management) |
| ueventd | uevent Daemon | 커널 uevent를 받아 `/dev` 노드를 만들고 권한을 부여하는 init 모드. | [CH8](/study/android-internals/08-init-zygote) |
| vold | Volume Daemon | 저장소 마운트·암호화·볼륨 관리를 담당하는 데몬. FBE/어댑터블 스토리지의 실무자다. | [CH5](/study/android-internals/05-storage-management) |
| watchdog | Watchdog | 데드락·행 상태를 감지해 프로세스나 시스템을 재시작시키는 감시 장치. | [CH12](/study/android-internals/12-logging-monitoring) |

## 5. 빌드 시스템

소스 트리를 실제 이미지로 굽는 도구 사슬이다. [CH14](/study/android-internals/14-building-aosp)가 이 카테고리를 통째로 다룬다.

| 약어/용어 | 풀네임 | 설명 | 관련 챕터 |
| --- | --- | --- | --- |
| Soong | Soong Build System | `Android.bp`를 Ninja 파일로 변환하는 안드로이드 빌드 프론트엔드. Make를 대체했다. | [CH14](/study/android-internals/14-building-aosp) |
| Android.bp | Android Blueprint File | 모듈을 선언하는 Soong 입력 파일. Blueprint 문법(JSON 유사)으로 작성한다. | [CH14](/study/android-internals/14-building-aosp) |
| Android.mk | Android Makefile | 구형 Make 기반 모듈 정의. 점차 `Android.bp`로 이관 중인 레거시다. | [CH14](/study/android-internals/14-building-aosp) |
| kati | kati (ckati) | 남은 `Android.mk`를 Ninja로 변환하는 Make 에뮬레이터. Soong과 공존한다. | [CH14](/study/android-internals/14-building-aosp) |
| ninja | Ninja Build | 실제 컴파일을 실행하는 저수준 빌드 엔진. Soong/kati가 생성한 파일을 돌린다. | [CH14](/study/android-internals/14-building-aosp) |
| lunch | lunch (Build Target Picker) | 빌드 대상 제품·variant를 고르는 envsetup 명령. `aosp_arm64-userdebug` 식으로 지정한다. | [CH14](/study/android-internals/14-building-aosp) |
| envsetup.sh | Build Environment Setup | `lunch`·`m`·`mm` 등 빌드 셸 함수를 정의하는 스크립트. 빌드의 진입점이다. | [CH14](/study/android-internals/14-building-aosp) |
| repo | repo (Multi-Git Tool) | 수백 개 git 저장소를 manifest로 묶어 관리하는 구글 도구. AOSP 소스 동기화의 기본이다. | [CH14](/study/android-internals/14-building-aosp) |
| PRODUCT_PACKAGES | PRODUCT_PACKAGES | 제품 이미지에 포함할 모듈 목록을 지정하는 make 변수. bring-up 시 자주 손댄다. | [CH14](/study/android-internals/14-building-aosp) |
| variant | Build Variant (user/userdebug/eng) | 디버그 가능성·루트 여부를 결정하는 빌드 종류. 출고는 user, 개발은 userdebug다. | [CH14](/study/android-internals/14-building-aosp) |
| device tree | Device Configuration Tree | `device/<vendor>/<board>` 아래의 제품 정의 묶음. bring-up 산출물의 집합소다. | [CH14](/study/android-internals/14-building-aosp) |
| mk | Product Makefile | `.mk` 제품/보드 구성 파일. `PRODUCT_*` 변수로 제품 정체성을 정의한다. | [CH14](/study/android-internals/14-building-aosp) |
| ccache | Compiler Cache | 컴파일 결과를 캐시해 재빌드를 가속하는 도구. 대형 AOSP 빌드에 큰 도움이 된다. | [CH14](/study/android-internals/14-building-aosp) |
| bazel | Bazel | 구글이 AOSP 빌드를 점진 이관 중인 차세대 빌드 시스템. Soong과 병행 단계다. | [CH14](/study/android-internals/14-building-aosp) |

## 6. 네이티브 레벨·Bionic

C/C++ 세계다. 농기계 CAN 데몬을 서비스로 올리는 작업이 바로 이 층에서 벌어진다. [CH15](/study/android-internals/15-native-level)가 핵심이며 [CH23](/study/android-internals/23-native-daemon-case-study) 케이스 스터디로 이어진다.

| 약어/용어 | 풀네임 | 설명 | 관련 챕터 |
| --- | --- | --- | --- |
| Bionic | Bionic libc | 안드로이드 전용 C 라이브러리·동적 링커·libm 묶음. glibc 대신 쓰인다. | [CH15](/study/android-internals/15-native-level) |
| NDK | Native Development Kit | 네이티브(C/C++) 코드를 빌드하는 공식 툴킷. 앱·데몬의 네이티브 부분을 만든다. | [CH15](/study/android-internals/15-native-level) |
| VNDK | Vendor Native Development Kit | 벤더 프로세스가 쓸 수 있도록 스냅샷된 시스템 라이브러리 집합. Treble 격리의 일부다. | [CH15](/study/android-internals/15-native-level) |
| LLNDK | Low-Level NDK | 벤더가 직접 링크해도 되는 시스템 공용 저수준 라이브러리(libc·liblog 등). | [CH15](/study/android-internals/15-native-level) |
| ELF | Executable and Linkable Format | 리눅스/안드로이드 실행·라이브러리 바이너리 포맷. 링커가 이 헤더를 읽어 로드한다. | [CH15](/study/android-internals/15-native-level) |
| linker namespace | Linker Namespace | 프로세스별로 볼 수 있는 라이브러리 집합을 격리하는 동적 링커 기능. 시스템/벤더 lib 분리의 근거다. | [CH15](/study/android-internals/15-native-level) |
| linker | Dynamic Linker (linker64) | ELF의 의존 라이브러리를 찾아 매핑·재배치하는 Bionic 컴포넌트. `LD_*` 환경을 해석한다. | [CH15](/study/android-internals/15-native-level) |
| tombstone | Tombstone | 네이티브 크래시 시 남는 상세 덤프(레지스터·스택·맵). `/data/tombstones`에 쌓인다. | [CH12](/study/android-internals/12-logging-monitoring) |
| debuggerd | debuggerd | 네이티브 크래시를 잡아 tombstone과 backtrace를 생성하는 데몬. | [CH12](/study/android-internals/12-logging-monitoring) |
| ASan | Address Sanitizer | 메모리 오류(오버플로·UAF)를 런타임에 잡는 계측 도구. HWASan은 ARM 태그 메모리 버전이다. | [CH15](/study/android-internals/15-native-level) |
| bp2build | bp2build | `Android.bp`를 Bazel BUILD로 변환하는 마이그레이션 도구. | [CH14](/study/android-internals/14-building-aosp) |
| prebuilt | Prebuilt Binary | 소스 없이 미리 컴파일해 트리에 넣는 바이너리. 서드파티 CAN 데몬을 올릴 때 흔한 방식이다. | [CH23](/study/android-internals/23-native-daemon-case-study) |
| stub library | Stub / Version Script | 심볼 노출을 버전별로 통제하는 링커 스크립트. 시스템 라이브러리 ABI 안정성을 지킨다. | [CH15](/study/android-internals/15-native-level) |
| PIE | Position Independent Executable | 어느 주소에도 로드 가능한 실행 파일. ASLR과 함께 익스플로잇 난이도를 높인다. | [CH15](/study/android-internals/15-native-level) |

## 7. 보안·SELinux

강제 접근 제어와 저장소 암호화의 세계다. 커스텀 데몬을 올리면 반드시 sepolicy와 마주친다. [CH16](/study/android-internals/16-selinux-avb)이 중심이다.

| 약어/용어 | 풀네임 | 설명 | 관련 챕터 |
| --- | --- | --- | --- |
| SELinux | Security-Enhanced Linux | 라벨 기반 강제 접근 제어(MAC). 안드로이드는 모든 프로세스·파일에 도메인/타입을 붙인다. | [CH16](/study/android-internals/16-selinux-avb) |
| MAC | Mandatory Access Control | 정책이 강제하는 접근 제어. 소유자 재량인 DAC(권한 비트) 위에 얹힌다. | [CH16](/study/android-internals/16-selinux-avb) |
| TE | Type Enforcement | SELinux의 핵심 규칙 유형. "어떤 도메인이 어떤 타입에 무엇을 허용"을 `allow`로 기술한다. | [CH16](/study/android-internals/16-selinux-avb) |
| AVC | Access Vector Cache | 커널의 SELinux 권한 판정 캐시. 거부 시 `avc: denied` 로그가 남는다. | [CH16](/study/android-internals/16-selinux-avb) |
| CIL | Common Intermediate Language | sepolicy 컴파일 중간 표현. `.te`가 이 형태로 변환·병합된다. | [CH16](/study/android-internals/16-selinux-avb) |
| sepolicy | SELinux Policy | `.te`/`file_contexts` 등으로 구성된 안드로이드 보안 정책 소스. 커스텀 데몬 추가 시 손댄다. | [CH16](/study/android-internals/16-selinux-avb) |
| te | Type Enforcement File (.te) | 도메인·타입·allow 규칙을 적는 정책 소스 파일. `system/sepolicy`와 벤더에 나뉜다. | [CH16](/study/android-internals/16-selinux-avb) |
| neverallow | neverallow Rule | 절대 허용해선 안 되는 접근을 컴파일 타임에 강제하는 규칙. CTS로도 검증된다. | [CH16](/study/android-internals/16-selinux-avb) |
| file_contexts | file_contexts | 경로에 SELinux 라벨을 매핑하는 파일. 새 실행 파일에 도메인을 붙일 때 편집한다. | [CH16](/study/android-internals/16-selinux-avb) |
| enforcing/permissive | Enforcing / Permissive Mode | 정책 위반을 차단(enforcing)하느냐 로그만 남기(permissive)느냐의 모드. bring-up 초기엔 permissive가 흔하다. | [CH16](/study/android-internals/16-selinux-avb) |
| FBE | File-Based Encryption | 파일 단위로 키를 달리해 암호화하는 방식. CE/DE 스토리지 분리를 가능케 한다. | [CH5](/study/android-internals/05-storage-management) |
| FDE | Full-Disk Encryption | 파티션 전체를 한 키로 암호화하던 구형 방식. 10부터 FBE로 대체됐다. | [CH5](/study/android-internals/05-storage-management) |
| CE | Credential Encrypted (Storage) | 사용자 인증(잠금 해제) 이후에만 열리는 암호화 저장소. `/data/user`가 대표적이다. | [CH5](/study/android-internals/05-storage-management) |
| DE | Device Encrypted (Storage) | 부팅 직후(잠금 전)부터 접근 가능한 암호화 저장소. Direct Boot 서비스가 쓴다. | [CH5](/study/android-internals/05-storage-management) |
| Keymint | Keymint (구 Keymaster) | TEE 안에서 키 생성·서명·인증을 수행하는 HAL. 하드웨어 백드 키의 관문이다. | [CH16](/study/android-internals/16-selinux-avb) |
| Gatekeeper | Gatekeeper | PIN/패턴/비밀번호를 TEE에서 검증하고 재시도를 제한하는 컴포넌트. | [CH16](/study/android-internals/16-selinux-avb) |
| StrongBox | StrongBox Keymaster | 별도 보안 칩(SE)에서 키를 다루는 강화 Keymint 구현. | [CH16](/study/android-internals/16-selinux-avb) |
| SPL | Security Patch Level | 기기가 반영한 보안 패치 기준일. `ro.build.version.security_patch`로 노출된다. | [CH16](/study/android-internals/16-selinux-avb) |
| rollback protection | Rollback Protection | 취약한 구버전으로의 다운그레이드를 막는 AVB 기능. 롤백 인덱스를 비교한다. | [CH16](/study/android-internals/16-selinux-avb) |

## 8. 패키지·런타임

앱이 설치되고, DEX가 기계어로 컴파일되고, ART 위에서 실행되는 과정이다. [CH17](/study/android-internals/17-package-management)~[CH20](/study/android-internals/20-art-internals)이 다룬다.

| 약어/용어 | 풀네임 | 설명 | 관련 챕터 |
| --- | --- | --- | --- |
| APK | Android Package | 앱 배포 단위(zip). manifest·DEX·리소스·서명을 담는다. | [CH17](/study/android-internals/17-package-management) |
| AAB | Android App Bundle | Play 업로드용 앱 번들. 기기별로 최적화된 APK(split)를 생성한다. | [CH17](/study/android-internals/17-package-management) |
| APK Signature Scheme | APK Signature Scheme v2/v3/v4 | APK 전체를 블록 단위로 서명·검증하는 방식. v4는 스트리밍(fs-verity) 설치를 지원한다. | [CH17](/study/android-internals/17-package-management) |
| DEX | Dalvik Executable | 안드로이드 바이트코드 포맷(`classes.dex`). 여러 클래스를 한 파일에 담는다. | [CH19](/study/android-internals/19-dalvik-dex) |
| OAT | Optimized Android (ELF) | dex2oat가 만드는 네이티브 코드 컨테이너(ELF). `.odex`로 배치된다. | [CH20](/study/android-internals/20-art-internals) |
| VDEX | Verified DEX | 검증·정규화된 DEX를 담아 재검증을 건너뛰게 하는 파일. OAT와 짝을 이룬다. | [CH20](/study/android-internals/20-art-internals) |
| ART | Android Runtime | 5.0부터 Dalvik을 대체한 앱 런타임. AOT+JIT+프로파일 기반 컴파일을 결합한다. | [CH20](/study/android-internals/20-art-internals) |
| Dalvik | Dalvik VM | 초기 안드로이드의 레지스터 기반 VM. ART로 대체됐으나 DEX 포맷과 용어에 흔적을 남겼다. | [CH19](/study/android-internals/19-dalvik-dex) |
| JIT | Just-In-Time Compilation | 실행 중 자주 쓰는 코드를 그때그때 컴파일하는 방식. 프로파일을 쌓아 AOT로 넘긴다. | [CH20](/study/android-internals/20-art-internals) |
| AOT | Ahead-Of-Time Compilation | 설치·유휴 시점에 DEX를 미리 네이티브로 컴파일하는 방식. 실행 성능을 높인다. | [CH20](/study/android-internals/20-art-internals) |
| dex2oat | dex2oat | DEX를 OAT/VDEX로 컴파일하는 ART 도구. 설치·유휴 최적화 시 돌아간다. | [CH20](/study/android-internals/20-art-internals) |
| baseline profile | Baseline Profile | 앱과 함께 배포되는 핫패스 힌트. 설치 직후부터 AOT 컴파일 대상을 좁힌다. | [CH20](/study/android-internals/20-art-internals) |
| GC | Garbage Collection | ART의 자동 메모리 회수. Concurrent Copying이 기본 컬렉터다. | [CH20](/study/android-internals/20-art-internals) |
| RRO | Runtime Resource Overlay | 앱을 재빌드하지 않고 리소스를 런타임에 덮어쓰는 오버레이. 브랜딩·커스터마이즈에 쓴다. | [CH17](/study/android-internals/17-package-management) |
| OverlayFS | Overlay Filesystem | 하위 계층 위에 쓰기 계층을 겹치는 파일시스템. `adb remount`·개발 편의에 쓰인다. | [CH4](/study/android-internals/04-files-directories) |
| AndroidManifest | AndroidManifest.xml | 앱의 컴포넌트·권한·인텐트 필터를 선언하는 필수 문서. PMS가 이를 파싱한다. | [CH18](/study/android-internals/18-app-anatomy) |
| resources.arsc | Compiled Resources Table | 컴파일된 리소스 인덱스. aapt2가 생성하며 런타임 리소스 해석의 근거다. | [CH18](/study/android-internals/18-app-anatomy) |
| aapt2 | Android Asset Packaging Tool 2 | 리소스를 컴파일·링크해 `resources.arsc`와 최종 APK를 만드는 도구. | [CH18](/study/android-internals/18-app-anatomy) |
| fs-verity | fs-verity | 파일 단위 무결성 검증 커널 기능. APK v4 스트리밍 설치와 결합한다. | [CH17](/study/android-internals/17-package-management) |

## 9. Binder·IPC

안드로이드 프로세스 간 통신의 심장이다. 유저스페이스 프록시부터 커널 드라이버까지를 아우른다. [CH21](/study/android-internals/21-binder-userspace)·[CH22](/study/android-internals/22-binder-kernel)에서 다룬다.

| 약어/용어 | 풀네임 | 설명 | 관련 챕터 |
| --- | --- | --- | --- |
| Binder | Binder IPC | 안드로이드의 핵심 프로세스 간 통신 메커니즘. 커널 드라이버+유저 프록시로 구성된다. | [CH21](/study/android-internals/21-binder-userspace) |
| AIDL | Android Interface Definition Language | Binder 인터페이스를 선언하는 언어. 스텁·프록시 코드를 자동 생성한다. | [CH21](/study/android-internals/21-binder-userspace) |
| Parcel | Parcel | Binder로 실어 보낼 데이터를 직렬화하는 컨테이너. marshalling의 실무 단위다. | [CH21](/study/android-internals/21-binder-userspace) |
| Parcelable | Parcelable | Parcel에 쓰고 읽을 수 있게 만든 객체 인터페이스. AIDL이 자동 구현을 돕는다. | [CH21](/study/android-internals/21-binder-userspace) |
| BpBinder | Binder Proxy (Bp) | 클라이언트 쪽 원격 객체 프록시. 호출을 transact로 커널에 넘긴다. | [CH21](/study/android-internals/21-binder-userspace) |
| BBinder | Binder Native (Bn) | 서버 쪽 실제 객체. 커널이 전달한 transact를 onTransact로 받는다. | [CH21](/study/android-internals/21-binder-userspace) |
| IBinder | IBinder | Bp/Bn이 공유하는 Binder 객체 추상 인터페이스. `transact`/`onTransact`를 규정한다. | [CH21](/study/android-internals/21-binder-userspace) |
| IPCThreadState | IPCThreadState | 스레드별 Binder 상태와 커널 ioctl 루프를 관리하는 유저스페이스 객체. | [CH21](/study/android-internals/21-binder-userspace) |
| ProcessState | ProcessState | 프로세스당 하나인 Binder 드라이버 오픈·mmap 상태 보유 객체. | [CH21](/study/android-internals/21-binder-userspace) |
| binder driver | /dev/binder | 실제 IPC를 중계하는 커널 캐릭터 디바이스. `ioctl(BINDER_WRITE_READ)`이 관문이다. | [CH22](/study/android-internals/22-binder-kernel) |
| BinderFS | binderfs | Binder 디바이스 노드를 동적으로 만드는 파일시스템. 컨테이너·다중 도메인에 쓰인다. | [CH22](/study/android-internals/22-binder-kernel) |
| oneway | oneway (Asynchronous) | 응답을 기다리지 않는 비동기 Binder 호출. 콜백·이벤트 통지에 쓴다. | [CH21](/study/android-internals/21-binder-userspace) |
| hwbinder | /dev/hwbinder | HIDL HAL 통신 전용 Binder 도메인. 프레임워크/벤더 IPC를 분리한다. | [CH22](/study/android-internals/22-binder-kernel) |
| vndbinder | /dev/vndbinder | 벤더 프로세스끼리의 AIDL 통신 전용 Binder 도메인. | [CH22](/study/android-internals/22-binder-kernel) |
| transaction buffer | Binder Transaction Buffer | 각 프로세스가 mmap한 수신용 커널 버퍼. 복사 1회로 데이터를 전달한다. | [CH22](/study/android-internals/22-binder-kernel) |
| death recipient | Death Recipient / linkToDeath | 원격 Binder가 죽었을 때 통지받는 콜백 등록. 서비스 감시에 쓴다. | [CH21](/study/android-internals/21-binder-userspace) |
| HwBinder / libhwbinder | HwBinder Library | HIDL용 Binder 프록시/네이티브 구현 라이브러리. AIDL HAL 전환으로 축소 중이다. | [CH22](/study/android-internals/22-binder-kernel) |

## 10. 로깅·진단·전원

기기의 상태를 관찰하고 전력을 다루는 용어들이다. [CH12](/study/android-internals/12-logging-monitoring)·[CH13](/study/android-internals/13-power-management)에서 다룬다.

| 약어/용어 | 풀네임 | 설명 | 관련 챕터 |
| --- | --- | --- | --- |
| logd | Logger Daemon | 링버퍼에 로그를 모으는 데몬. `logcat`이 이로부터 읽어 출력한다. | [CH12](/study/android-internals/12-logging-monitoring) |
| logcat | logcat | 시스템/앱 로그를 조회하는 도구. main·system·radio·crash 버퍼를 노출한다. | [CH12](/study/android-internals/12-logging-monitoring) |
| dmesg | Kernel Ring Buffer | 커널 로그 버퍼. 드라이버·부팅 초기 문제 진단의 1차 소스다. | [CH12](/study/android-internals/12-logging-monitoring) |
| dumpsys | dumpsys | 시스템 서비스의 내부 상태를 덤프하는 진단 도구. 서비스별 상태 조회의 표준이다. | [CH12](/study/android-internals/12-logging-monitoring) |
| bugreport | Bug Report | 로그·상태·트레이스를 한 번에 모은 종합 진단 산출물. | [CH12](/study/android-internals/12-logging-monitoring) |
| ANR | Application Not Responding | 앱이 정해진 시간 안에 응답하지 못한 상태. traces로 원인을 추적한다. | [CH12](/study/android-internals/12-logging-monitoring) |
| perfetto | Perfetto | 시스템 전역 트레이싱 프레임워크. CPU·전력·Binder 트레이스를 한데 모은다. | [CH12](/study/android-internals/12-logging-monitoring) |
| statsd | Statistics Daemon | 사용·성능 지표를 수집·집계하는 데몬. 메트릭 파이프라인의 근간이다. | [CH12](/study/android-internals/12-logging-monitoring) |
| eBPF | extended Berkeley Packet Filter | 커널에 안전한 프로그램을 주입해 관찰·계측하는 기술. 네트워크·전력 통계에 쓰인다. [관측성 CH26](/study/observability/26-profile-types-ebpf) 참고. | [CH12](/study/android-internals/12-logging-monitoring) |
| wakelock | Wake Lock | CPU/화면이 잠들지 못하게 붙잡는 전원 관리 잠금. 남용은 배터리 소모의 주범이다. | [CH13](/study/android-internals/13-power-management) |
| Doze | Doze Mode | 유휴 시 백그라운드 활동을 억제해 절전하는 모드. App Standby와 짝이다. | [CH13](/study/android-internals/13-power-management) |
| suspend | Suspend-to-RAM | 램만 유지하고 대부분을 끄는 저전력 상태. wakeup source가 이를 깨운다. | [CH13](/study/android-internals/13-power-management) |
| PSI | Pressure Stall Information | CPU·메모리·IO 압박을 수치화한 커널 지표. lmkd가 종료 판단에 쓴다. | [CH13](/study/android-internals/13-power-management) |
| cgroup | Control Group | 프로세스 자원(CPU·메모리)을 그룹 단위로 제한하는 커널 기능. 스케줄 정책에 쓰인다. [Kubernetes CH1](/study/kubernetes/01-container-basics) 참고. | [CH11](/study/android-internals/11-linux-lens) |

## 11. CAN·임베디드 연계

이 스터디의 실무 목적인 농기계 CAN 데몬과 맞닿는 용어다. 자세한 배경은 [CAN 통신 심화](/study/can/)·[ISOBUS](/study/isobus/) 스터디를 함께 본다.

| 약어/용어 | 풀네임 | 설명 | 관련 챕터 |
| --- | --- | --- | --- |
| SocketCAN | Socket CAN | CAN 버스를 소켓 API로 다루는 리눅스 서브시스템. 네이티브 데몬이 이를 연다. [CAN CH13](/study/can/13-socketcan-basics) 참고. | [CH23](/study/android-internals/23-native-daemon-case-study) |
| ISOBUS | ISO 11783 | 농기계 표준 CAN 프로토콜. 트랙터-작업기 통신의 기반이다. [ISOBUS 스터디](/study/isobus/) 참고. | [CH23](/study/android-internals/23-native-daemon-case-study) |
| AgIsoStack++ | AgIsoStack++ | ISOBUS를 구현한 오픈소스 C++ 스택. 이 스터디가 서비스로 올리는 데몬의 뼈대다. | [CH23](/study/android-internals/23-native-daemon-case-study) |
| J1939 | SAE J1939 | 상용차·중장비용 CAN 상위 프로토콜. ISOBUS가 이를 확장한다. | [CH23](/study/android-internals/23-native-daemon-case-study) |
| CAN FD | CAN with Flexible Data-rate | 프레임 페이로드와 속도를 확장한 CAN. 최신 SoC/트랜시버가 지원한다. | [CH23](/study/android-internals/23-native-daemon-case-study) |

::: tip 핵심 정리
- 약어가 막히면 카테고리(아키텍처→파티션→부팅→init→빌드→네이티브→보안→런타임→Binder)로 좁혀 찾는다.
- 같은 약어라도 문맥이 다르면(예: `EL`=Exception Level, `ELF`=바이너리 포맷) 반드시 관련 챕터 링크로 원 맥락을 확인한다.
- 커스텀 데몬을 올릴 때 반복해 마주칠 핵심 축은 `Soong`·`sepolicy`·`init.rc`·`Binder`·`SocketCAN` 다섯이다 — 이 다섯 용어의 챕터는 특히 여러 번 돌아오게 된다.
:::

## 다음 챕터

[부록. 참고 자료](/study/android-internals/appendix-references)에서 이 스터디의 원전과 공식 문서·코드 탐색 사이트·도서·커뮤니티를 카테고리별로 정리한다.
