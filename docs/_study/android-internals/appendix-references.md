---
title: "부록. 참고 자료"
description: "이 Android Internals 스터디의 뼈대가 된 Jonathan Levin의 원전부터 source.android.com 공식 문서, cs.android.com 코드 탐색, 핵심 도서, 커뮤니티·사내 스터디까지 챕터별 연관성과 함께 정리한 레퍼런스 모음."
date: 2026-07-13
tags: [android, aosp, references, reference]
---

# 부록. 참고 자료

이 스터디를 만들며 참고했고, 각 챕터를 더 파고들 때 실제로 열어 볼 만한 자료를 카테고리별로 모았다. 항목마다 어떤 챕터와 연결되는지, 왜 볼 가치가 있는지 한 줄로 붙였다. 백엔드 개발자가 AOSP를 커스텀해 임베디드 장비를 만드는 이 스터디의 목적에 맞춰, "읽을거리"보다 "곁에 두고 찾아볼 것" 위주로 골랐다.

## 1. 원전 — 이 스터디의 뼈대

이 스터디의 챕터 구성·용어·깊이는 아래 원전을 뼈대로 삼았다. 한 권으로 정리된 안드로이드 내부 레퍼런스는 사실상 이것뿐이다.

| 자료 | 링크 | 연관 챕터 | 코멘트 |
| --- | --- | --- | --- |
| Jonathan Levin, *Android Internals: A Confectioner's Cookbook* Vol I (Power User's View) | [newandroidbook.com](http://newandroidbook.com/) | [CH1](/study/android-internals/01-architecture-evolution)~[CH13](/study/android-internals/13-power-management) | 파티션·부팅·init·서비스·전원까지 "유저·운영자 관점"의 내부 구조. 이 스터디 전반부의 뼈대다. |
| Jonathan Levin, *Android Internals* Vol II (Developer's View) | [newandroidbook.com](http://newandroidbook.com/) | [CH14](/study/android-internals/14-building-aosp)~[CH22](/study/android-internals/22-binder-kernel) | 빌드·네이티브·보안·런타임·Binder까지 "개발자 관점". 후반부의 뼈대다. 2판은 Android 16 기준으로 갱신됐다. |
| Levin, *Android Internals* 자료실(툴·부록·정오표) | [newandroidbook.com/tools](http://newandroidbook.com/tools/) | [CH12](/study/android-internals/12-logging-monitoring), [CH21](/study/android-internals/21-binder-userspace) | 저자가 만든 진단 툴(`jtrace` 등)과 각 장 보충 자료. 실습으로 확인하고 싶을 때 유용하다. |
| Levin, *MOXiI*(*Mac OS X and iOS Internals*) 시리즈 | [newosxbook.com](http://newosxbook.com/) | [CH15](/study/android-internals/15-native-level), [CH22](/study/android-internals/22-binder-kernel) | 같은 저자의 커널·Mach-O 내부 시리즈. Binder를 다른 OS의 IPC와 비교해 이해할 때 관점을 넓혀 준다. |

## 2. 공식 문서 — source.android.com

플랫폼을 실제로 커스텀할 때 1차 근거가 되는 문서다. 버전에 따라 내용이 갱신되므로 항상 최신을 확인한다.

| 섹션 | 링크 | 연관 챕터 | 코멘트 |
| --- | --- | --- | --- |
| Architecture 개요 | [source.android.com/docs/core/architecture](https://source.android.com/docs/core/architecture) | [CH1](/study/android-internals/01-architecture-evolution), [CH9](/study/android-internals/09-service-architecture) | HAL·프레임워크·Treble의 계층 구조를 그림으로 설명. 전체 지도를 다시 맞출 때 첫 페이지다. |
| Partitions & Filesystems | [source.android.com/docs/core/architecture/partitions](https://source.android.com/docs/core/architecture/partitions) | [CH3](/study/android-internals/03-partitions-filesystems) | dynamic partition·super·A/B의 공식 설명. bring-up 파티션 레이아웃 설계의 근거다. |
| HAL / AIDL for HALs | [source.android.com/docs/core/architecture/aidl/aidl-hals](https://source.android.com/docs/core/architecture/aidl/aidl-hals) | [CH9](/study/android-internals/09-service-architecture), [CH21](/study/android-internals/21-binder-userspace) | HIDL→AIDL 전환 이후 HAL 작성의 표준. 새 HAL을 정의할 때 반드시 본다. |
| SELinux for Android | [source.android.com/docs/security/features/selinux](https://source.android.com/docs/security/features/selinux) | [CH16](/study/android-internals/16-selinux-avb) | sepolicy 작성·`avc: denied` 디버깅의 공식 가이드. 커스텀 데몬이 막힐 때 첫 참조처다. |
| Android Verified Boot (AVB) | [source.android.com/docs/security/features/verifiedboot](https://source.android.com/docs/security/features/verifiedboot) | [CH7](/study/android-internals/07-boot-process), [CH16](/study/android-internals/16-selinux-avb) | vbmeta·롤백 인덱스·`avbtool` 사용법. 서명 이미지를 직접 구울 때 필요하다. |
| Soong / Build 문서 | [source.android.com/docs/setup/build](https://source.android.com/docs/setup/build) | [CH14](/study/android-internals/14-building-aosp) | `envsetup`·`lunch`·`m` 워크플로와 `Android.bp` 레퍼런스. 빌드 진입점 문서다. |
| Bootloader / Boot Image | [source.android.com/docs/core/architecture/bootloader](https://source.android.com/docs/core/architecture/bootloader) | [CH7](/study/android-internals/07-boot-process) | boot/vendor_boot 헤더 버전·ramdisk 구성 규격. 커널 이미지를 다룰 때 본다. |
| Runtime / ART & Dalvik | [source.android.com/docs/core/runtime](https://source.android.com/docs/core/runtime) | [CH19](/study/android-internals/19-dalvik-dex), [CH20](/study/android-internals/20-art-internals) | dex2oat·프로파일 컴파일·GC 설정의 공식 설명. 런타임 튜닝의 근거다. |
| Power / Power Management | [source.android.com/docs/core/power](https://source.android.com/docs/core/power) | [CH13](/study/android-internals/13-power-management) | wakelock·Doze·suspend 동작과 전력 측정. 장시간 가동 장비의 전력 이슈에 참고. |
| GKI (Generic Kernel Image) | [source.android.com/docs/core/architecture/kernel/generic-kernel-image](https://source.android.com/docs/core/architecture/kernel/generic-kernel-image) | [CH7](/study/android-internals/07-boot-process) | GKI+벤더 모듈 구조와 KMI. 커널을 자체 빌드할지 정할 때 판단 근거다. |
| Compatibility / VINTF | [source.android.com/docs/core/architecture/vintf](https://source.android.com/docs/core/architecture/vintf) | [CH9](/study/android-internals/09-service-architecture) | FCM·매니페스트 매칭 규칙. 부팅이 VINTF에서 막힐 때 원인을 찾는 곳이다. |

## 3. 개발자 문서 — developer.android.com

앱·네이티브 개발자 관점의 공식 문서다. 특히 NDK 문서는 네이티브 데몬 작업에 직접 쓰인다.

| 섹션 | 링크 | 연관 챕터 | 코멘트 |
| --- | --- | --- | --- |
| NDK Guides | [developer.android.com/ndk/guides](https://developer.android.com/ndk/guides) | [CH15](/study/android-internals/15-native-level), [CH23](/study/android-internals/23-native-daemon-case-study) | ABI·CMake 툴체인·`android_get_device_api_level` 등 네이티브 빌드의 실무 문서. CAN 데몬 크로스컴파일에 직접 쓴다. |
| App Bundles / APK | [developer.android.com/guide/app-bundle](https://developer.android.com/guide/app-bundle) | [CH17](/study/android-internals/17-package-management), [CH18](/study/android-internals/18-app-anatomy) | AAB·split APK·서명 스킴. 패키지 포맷을 해부할 때 참조한다. |
| Baseline Profiles | [developer.android.com/topic/performance/baselineprofiles](https://developer.android.com/topic/performance/baselineprofiles) | [CH20](/study/android-internals/20-art-internals) | AOT 대상 힌트 작성법. 앱 시작 성능을 ART 관점에서 다룰 때 본다. |
| Perfetto / System Tracing | [developer.android.com/topic/performance/tracing](https://developer.android.com/topic/performance/tracing) | [CH12](/study/android-internals/12-logging-monitoring) | Perfetto 트레이스 수집·분석. Binder·전력 병목을 눈으로 볼 때 쓴다. |

## 4. 코드 탐색

내부 동작이 헷갈릴 때 결국 소스를 읽는 게 가장 빠르다. 아래 사이트는 브라우저에서 AOSP 소스를 바로 검색·추적하게 해 준다.

| 자료 | 링크 | 연관 챕터 | 코멘트 |
| --- | --- | --- | --- |
| Code Search (cs.android.com) | [cs.android.com](https://cs.android.com/) | 전 챕터 | 심볼 정의·참조를 클릭으로 따라가는 공식 코드 검색. `IPCThreadState`·`dex2oat` 등을 추적할 때 첫 도구다. |
| android.googlesource.com | [android.googlesource.com](https://android.googlesource.com/) | [CH14](/study/android-internals/14-building-aosp) | git 원본 저장소. `repo` manifest·특정 커밋·태그를 볼 때 쓴다. |
| AndroidXRef | [androidxref.com](http://androidxref.com/) | [CH15](/study/android-internals/15-native-level), [CH22](/study/android-internals/22-binder-kernel) | OpenGrok 기반 버전별 크로스레퍼런스. 구버전 동작(예: HIDL 시절)과 대조할 때 유용하다. |
| aospxref (Shift-JIS 계열) | [aospxref.com](https://aospxref.com/) | [CH8](/study/android-internals/08-init-zygote), [CH21](/study/android-internals/21-binder-userspace) | 최신 릴리스까지 인덱싱된 OpenGrok 미러. androidxref가 뒤처졌을 때 대안이다. |

## 5. 도서

원전(Levin) 외에 관점을 보완해 주는 책이다. 각기 강점 영역이 다르다.

| 도서 | 저자 | 연관 챕터 | 코멘트 |
| --- | --- | --- | --- |
| *Inside the Android OS* | Meike & Schiefer | [CH1](/study/android-internals/01-architecture-evolution), [CH9](/study/android-internals/09-service-architecture) | 플랫폼 아키텍처를 설계 의도 중심으로 설명. "왜 이렇게 나뉘었나"를 잡는 데 좋다. |
| *Embedded Android* | Karim Yaghmour | [CH2](/study/android-internals/02-hardware-soc), [CH14](/study/android-internals/14-building-aosp) | 임베디드 bring-up·device tree·빌드 커스텀의 고전. 이 스터디의 실무 목적과 가장 맞닿는다. |
| *Android Internals: Architecture and AOSP Foundations* | Janhangeer (2026) | [CH3](/study/android-internals/03-partitions-filesystems), [CH16](/study/android-internals/16-selinux-avb) | 최신 AOSP 기준 아키텍처·파티션·보안 정리. 근래 버전 변화를 따라갈 때 보완용으로 좋다. |
| *Android Security Internals* | Nikolay Elenkov | [CH16](/study/android-internals/16-selinux-avb), [CH17](/study/android-internals/17-package-management) | 권한·서명·키스토어·검증 부팅의 보안 관점 심화. sepolicy 밖의 보안 모델을 이해할 때 본다. |

## 6. 커뮤니티·블로그

공식 문서에 없는 "실제로 해 봤더니" 지식이 모이는 곳이다. 커스텀 ROM·bring-up 삽질 사례가 특히 값지다.

| 자료 | 링크 | 연관 챕터 | 코멘트 |
| --- | --- | --- | --- |
| LineageOS Wiki | [wiki.lineageos.org](https://wiki.lineageos.org/) | [CH6](/study/android-internals/06-images-updates), [CH14](/study/android-internals/14-building-aosp) | 기기별 빌드·device tree 구성의 실전 레퍼런스. bring-up 절차를 남의 기기로 먼저 익힐 때 좋다. |
| XDA Developers | [xda-developers.com](https://xda-developers.com/) | [CH6](/study/android-internals/06-images-updates), [CH7](/study/android-internals/07-boot-process) | 부트로더 언락·이미지·파티션 관련 실사용 사례의 보고. 특정 SoC 이슈 검색에 강하다. |
| aosp-devs / AOSP 개발자 포럼 | [aosp-devs.org](https://aosp-devs.org/) | [CH14](/study/android-internals/14-building-aosp) | AOSP 빌드·패치 관련 개발자 논의. Gerrit 리뷰 문화를 익히기에도 좋다. |
| ART / dalvik 개발자 그룹 아카이브 | [groups.google.com/g/android-platform](https://groups.google.com/g/android-platform) | [CH20](/study/android-internals/20-art-internals) | 런타임·컴파일러 설계 논의가 오가는 곳. 미묘한 ART 동작의 배경을 찾을 때 뒤진다. |

## 7. 관련 사내 스터디

이 스터디의 실무 종착점인 [CH23. 네이티브 데몬 서비스 만들기](/study/android-internals/23-native-daemon-case-study)는 CAN 통신과 직접 이어진다. 아래 사내 스터디를 함께 보면 데몬이 실제로 무엇을 주고받는지가 채워진다.

| 스터디 | 링크 | 연관 챕터 | 코멘트 |
| --- | --- | --- | --- |
| CAN 통신 심화 | [/study/can/](/study/can/) | [CH23](/study/android-internals/23-native-daemon-case-study), [CH11](/study/android-internals/11-linux-lens) | SocketCAN·프레임 구조·필터링을 다룬다. 데몬이 여는 CAN 소켓의 기반이다. [CAN CH13](/study/can/13-socketcan-basics)가 특히 직결된다. |
| ISOBUS | [/study/isobus/](/study/isobus/) | [CH23](/study/android-internals/23-native-daemon-case-study) | 농기계 표준 프로토콜(ISO 11783). AgIsoStack++ 데몬이 구현하는 상위 규격이다. |
| Kubernetes(컨테이너 기초) | [/study/kubernetes/01-container-basics](/study/kubernetes/01-container-basics) | [CH11](/study/android-internals/11-linux-lens) | cgroup·namespace를 컨테이너 관점에서 설명. 안드로이드의 프로세스 격리와 비교해 읽으면 좋다. |
| 관측성(eBPF) | [/study/observability/26-profile-types-ebpf](/study/observability/26-profile-types-ebpf) | [CH12](/study/android-internals/12-logging-monitoring) | eBPF 프로파일링을 다룬다. 안드로이드의 eBPF 기반 통계 수집과 맞닿는다. |

::: tip 핵심 정리
- 무언가를 진지하게 커스텀할 땐 순서가 있다 — 원전(Levin)으로 개념을 잡고, source.android.com으로 최신 규격을 확인하고, cs.android.com에서 실제 코드로 못을 박는다.
- 임베디드 bring-up 실무는 공식 문서만으로 부족하다. *Embedded Android*와 LineageOS wiki의 실전 사례가 빈틈을 메운다.
- CAN 데몬 작업([CH23](/study/android-internals/23-native-daemon-case-study))은 이 문서의 7번 사내 스터디들과 반드시 교차 참조한다 — 안드로이드 쪽 그릇([CH15](/study/android-internals/15-native-level)·[CH16](/study/android-internals/16-selinux-avb))과 CAN 쪽 내용물이 만나는 지점이다.
:::

이 부록으로 Android Internals 스터디의 본편과 부록이 모두 마무리된다. 전원 인가부터 커스텀 네이티브 데몬을 서비스로 올리기까지 — 23개 챕터를 관통한 하나의 질문은 "이 계층은 왜 이렇게 나뉘어 있고, 내가 만든 코드는 그 사슬 어디에 끼워지는가"였다. 그 지도를 손에 넣었다면, 이제 남은 건 실제 보드 위에서 확인하는 일이다.
