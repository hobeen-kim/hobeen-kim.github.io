---
title: "Android Internals — 안드로이드 OS 내부 구조"
description: "Jonathan Levin의 Android Internals Vol I/II 목차를 뼈대로, AOSP를 커스텀해 임베디드 장비용 안드로이드를 만들고 네이티브 데몬을 서비스로 올리는 관점에서 아키텍처·파티션·부팅·init·서비스·AOSP 빌드·Bionic·패키지·ART·Binder까지 OS 내부를 훑는다."
date: 2026-07-13
tags: [android, aosp, os]
---

# Android Internals — 안드로이드 OS 내부 구조

안드로이드는 세계에서 가장 많이 배포된 운영체제지만, "리눅스 커널 위에 자바 앱이 도는 폰 OS" 정도로만 알고 넘어가기 쉽다. 실제로 AOSP 소스를 받아 임베디드 보드에 올리고 네이티브 데몬을 서비스로 띄우려 하면, 익숙한 리눅스 배포판 상식이 절반쯤은 통하고 절반쯤은 배신한다. glibc 대신 Bionic이 있고, systemd 대신 init이 `.rc` 스크립트로 서비스를 관리하며, 파티션은 A/B로 갈라져 있고, `/system`은 읽기 전용에 dm-verity로 서명 검증까지 걸려 있다. 이 스터디는 그 간극을 메운다.

원전은 Jonathan Levin의 <strong>"Android Internals: A Confectioner's Cookbook" 2판</strong>(Android 16 기준) Vol I(Power User's View)·Vol II(Developer's View)다. 다만 이 스터디는 책의 순서를 그대로 옮기지 않고, <strong>AOSP를 커스텀해 농기계 같은 임베디드 장비용 안드로이드 OS를 만드는 백엔드 개발자</strong>의 실무 동선에 맞춰 재구성했다. 특히 C/C++ 네이티브 데몬(예: [CAN 통신](/study/can/) 스택 기반 통신 데몬)을 안드로이드 서비스로 올리는 작업을 최종 목적지로 두고, 그 지점에 도달하기까지 알아야 할 OS 내부 구조를 층층이 쌓아 올린다.

## 학습 로드맵

전체 23챕터는 7개 섹션으로 묶인다. 아래는 아키텍처·하드웨어에서 시작해 파티션·부팅·시스템 관리를 거쳐 AOSP 빌드와 네이티브, 그리고 마지막 Binder와 실전 데몬 케이스 스터디로 수렴하는 흐름이다.

![Android Internals 학습 로드맵 — S1 아키텍처와 하드웨어(CH1~2) → S2 파티션·스토리지·이미지(CH3~6) → S3 부팅과 시스템 기동(CH7~8) → S4 시스템 관리와 관찰(CH9~13) → S5 AOSP 빌드와 네이티브(CH14~16) → S6 패키지·앱·런타임(CH17~20) → S7 Binder와 실전(CH21~23) 순서로 이어지며, AOSP 빌드가 급하면 CH14부터 진입할 수 있는 곁가지를 함께 표시](/images/study-android-internals/00-roadmap-light.png)
![Android Internals 학습 로드맵 — S1 아키텍처와 하드웨어(CH1~2) → S2 파티션·스토리지·이미지(CH3~6) → S3 부팅과 시스템 기동(CH7~8) → S4 시스템 관리와 관찰(CH9~13) → S5 AOSP 빌드와 네이티브(CH14~16) → S6 패키지·앱·런타임(CH17~20) → S7 Binder와 실전(CH21~23) 순서로 이어지며, AOSP 빌드가 급하면 CH14부터 진입할 수 있는 곁가지를 함께 표시](/images/study-android-internals/00-roadmap-dark.png)

## 읽기 경로

기본은 <strong>CH1부터 순서대로</strong> 읽는 것이다. 각 챕터는 앞 챕터에서 쌓은 개념을 전제로 다음 층을 올리기 때문에, 처음 안드로이드 내부를 파고드는 사람이라면 순서를 지키는 편이 이해가 가장 빠르다.

다만 실무 상황에 따라 지름길이 있다.

- <strong>AOSP 빌드가 당장 급하면</strong> — 보드를 받아 일단 부팅부터 시켜야 하는 상황이라면 [CH14. AOSP 소스 빌드와 device bring-up](/study/android-internals/14-building-aosp)부터 읽고, 빌드가 막히는 지점에서 필요한 앞 챕터(파티션은 [CH3](/study/android-internals/03-partitions-filesystems), 부팅은 [CH7](/study/android-internals/07-boot-process), SELinux·검증 부팅은 [CH16](/study/android-internals/16-selinux-avb))으로 되돌아오는 방식이 빠르다.
- <strong>네이티브 데몬 작업이 목적이면</strong> — C/C++ 데몬을 서비스로 올리는 게 핵심 목표라면 [CH8. init과 Zygote](/study/android-internals/08-init-zygote) → [CH9. 서비스 아키텍처](/study/android-internals/09-service-architecture) → [CH14~16 (빌드·Bionic·보안)](/study/android-internals/14-building-aosp) → [CH21~23 (Binder와 데몬 케이스 스터디)](/study/android-internals/21-binder-userspace) 경로가 최단 코스다. 이 경로만으로도 데몬을 `init.rc`에 등록하고 Binder 서비스로 노출하는 데 필요한 지식이 대부분 갖춰진다.

<strong>실전 통합 경로</strong>는 위의 두 지름길을 하나로 엮어, AOSP를 받아 실제로 커스텀 OS를 완성하기까지의 작업 순서를 따라간다. 각 단계가 앞 단계의 산출물을 전제로 쌓이므로, 실무를 처음 굴릴 때 이 순서대로 밟으면 막힘이 적다.

1. <strong>트리 구조·빌드 체득</strong> — [CH14. AOSP 소스 빌드와 device bring-up](/study/android-internals/14-building-aosp)으로 repo·Soong·lunch를 익히고 일단 이미지를 굽는다. 소스 트리가 어떻게 생겼는지 몸으로 안다.
2. <strong>부팅·init·데몬</strong> — [CH7. 부트로더와 커널 부팅](/study/android-internals/07-boot-process)·[CH8. init과 Zygote](/study/android-internals/08-init-zygote)로 기기가 어떻게 깨어나고 서비스가 어디서 시작되는지, 우리 데몬을 `init.rc`로 어떻게 띄우는지 잡는다.
3. <strong>Binder/AIDL</strong> — [CH9. 서비스 아키텍처](/study/android-internals/09-service-architecture)·[CH21. Binder 유저스페이스](/study/android-internals/21-binder-userspace)로 데몬을 시스템에 서비스로 노출하는 통신 계층을 익힌다.
4. <strong>SELinux</strong> — [CH16. SELinux와 Verified Boot](/study/android-internals/16-selinux-avb)로 새 데몬·서비스에 sepolicy를 붙인다. 이 단계를 건너뛰면 데몬이 permission denied로 조용히 죽는다.
5. <strong>패키지·런처</strong> — [CH17. 패키지 관리](/study/android-internals/17-package-management)로 HMI 앱을 서명·설치하고, 장비에 맞는 런처(또는 헤드리스 구성)를 정한다.
6. <strong>커널 config·BSP</strong> — [CH2. 하드웨어와 SoC](/study/android-internals/02-hardware-soc)·[CH14](/study/android-internals/14-building-aosp)로 되돌아와 Device Tree와 커널 config, 벤더 BSP를 우리 보드에 맞춘다.
7. <strong>종합</strong> — [CH23. 네이티브 데몬 서비스 만들기](/study/android-internals/23-native-daemon-case-study)에서 위 조각을 하나로 합쳐 실제 CAN 데몬을 init 서비스+Binder로 올리는 전 과정을 관통한다.

어느 경로로 들어오든, 결국 전체를 한 바퀴 도는 것을 권한다. 안드로이드의 각 계층은 서로 촘촘히 얽혀 있어서, 한 부분만 떼어 이해하면 반드시 다른 계층에서 발목이 잡힌다.

## 전체 목차

### 아키텍처와 하드웨어 (CH1~2)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 01 | [안드로이드 아키텍처와 진화](/study/android-internals/01-architecture-evolution) | 버전 변천, Android vs Linux, 코드 출처, 스택 조감, HAL·커널 Androidism |
| 02 | [하드웨어와 SoC](/study/android-internals/02-hardware-soc) | ARM 아키텍처, SoC 구조, Device Tree, 펌웨어 이미지 |

### 파티션·스토리지·이미지 (CH3~6)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 03 | [파티션과 파일시스템](/study/android-internals/03-partitions-filesystems) | GPT 파티션 레이아웃, A/B, ext4·f2fs·EROFS |
| 04 | [파일과 디렉토리 구조](/study/android-internals/04-files-directories) | `/system`·`/vendor`·`/data` 레이아웃과 마운트 구조 |
| 05 | [스토리지 관리와 APEX](/study/android-internals/05-storage-management) | 동적 파티션, APEX 모듈, sdcardfs·FBE |
| 06 | [시스템 이미지와 업데이트](/study/android-internals/06-images-updates) | 이미지 포맷, OTA, seamless update |

### 부팅과 시스템 기동 (CH7~8)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 07 | [부트로더와 커널 부팅](/study/android-internals/07-boot-process) | 부트체인, boot 이미지, 커널·ramdisk 로딩 |
| 08 | [init과 Zygote](/study/android-internals/08-init-zygote) | init `.rc` 언어, 프로퍼티 시스템, Zygote fork 모델 |

### 시스템 관리와 관찰 (CH9~13)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 09 | [서비스 아키텍처](/study/android-internals/09-service-architecture) | 네이티브·시스템 서비스, servicemanager, HAL 서비스 |
| 10 | [설정과 관리](/study/android-internals/10-configuration) | 프로퍼티, settings, 리소스 오버레이(RRO) |
| 11 | [리눅스 렌즈로 본 애플리케이션](/study/android-internals/11-linux-lens) | 프로세스·UID·cgroup·namespace 관점의 앱 |
| 12 | [로깅·통계·모니터링](/study/android-internals/12-logging-monitoring) | logd/logcat, statsd, dumpsys, tombstone |
| 13 | [전원 관리](/study/android-internals/13-power-management) | wakelock, suspend, Doze, 스케줄링 |

### AOSP 빌드와 네이티브 (CH14~16)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 14 | [AOSP 소스 빌드와 device bring-up](/study/android-internals/14-building-aosp) | repo·Soong·Bazel, lunch, device tree, 부트업 |
| 15 | [네이티브 레벨과 Bionic](/study/android-internals/15-native-level) | Bionic libc, NDK, 네이티브 바이너리·라이브러리 |
| 16 | [SELinux와 Verified Boot](/study/android-internals/16-selinux-avb) | sepolicy, 도메인·타입, AVB·dm-verity |

### 패키지·앱·런타임 (CH17~20)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 17 | [패키지 관리](/study/android-internals/17-package-management) | APK 서명, PackageManager, 설치 흐름 |
| 18 | [애플리케이션 해부](/study/android-internals/18-app-anatomy) | manifest, 컴포넌트, 리소스, 앱 프로세스 |
| 19 | [Dalvik과 DEX](/study/android-internals/19-dalvik-dex) | DEX 포맷, 바이트코드, Dalvik의 유산 |
| 20 | [ART 내부 구조](/study/android-internals/20-art-internals) | AOT/JIT, dex2oat, GC, 프로파일 가이드 컴파일 |

### Binder와 실전 (CH21~23)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 21 | [Binder — 유저스페이스](/study/android-internals/21-binder-userspace) | AIDL, Parcel, 프록시·스텁, servicemanager |
| 22 | [Binder — 커널과 드라이버](/study/android-internals/22-binder-kernel) | binder 드라이버, 트랜잭션, 스레드 풀, 참조 카운팅 |
| 23 | [네이티브 데몬 서비스 만들기 (케이스 스터디)](/study/android-internals/23-native-daemon-case-study) | 실제 C/C++ 데몬을 init 서비스+Binder로 올리는 전 과정 |

### 부록

| | 제목 | 설명 |
|--|------|------|
| | [용어집](/study/android-internals/appendix-glossary) | 안드로이드 내부 핵심 용어 정리 |
| | [참고 자료](/study/android-internals/appendix-references) | 원전·AOSP 문서·소스 트리 링크 |

## 대상

이미 리눅스와 시스템 프로그래밍에 익숙한 백엔드/임베디드 개발자를 대상으로 한다. 안드로이드를 앱 개발자 관점이 아니라 <strong>OS를 만드는 사람 관점</strong>에서 다루며, "왜 이렇게 설계됐나 · 리눅스와 무엇이 다른가 · 커스텀할 때 어디가 함정인가 · 네이티브 코드를 어떻게 올리나"에 무게를 둔다. 예시 코드와 명령은 Android 14~16을 기준으로 하고, 과거 버전의 동작은 "X.0 이전에는 ~였다" 식으로 병기한다.

## 원전 소개

Jonathan Levin의 Android Internals는 iOS/macOS 내부를 다룬 *OS Internals* 시리즈의 저자가 쓴 안드로이드 편으로, 유저 관점(Vol I)과 개발자 관점(Vol II)으로 나뉜다. AOSP 소스와 실제 기기 동작을 대조하며 파고드는 서술 방식이 특징이다. 이 스터디는 그 목차를 참고하되, [AOSP 공식 문서](https://source.android.com/docs)와 실제 소스 트리를 1차 근거로 삼아 임베디드 커스텀 관점에서 다시 쓴 것이다.

## 다음 챕터

[CH1. 안드로이드 아키텍처와 진화](/study/android-internals/01-architecture-evolution)에서 안드로이드가 왜 그냥 리눅스 배포판이 아닌지, 소프트웨어 스택이 어떤 층으로 쌓여 있는지, 실제 기기 이미지가 어떤 코드 출처들의 합성물인지부터 조감한다.
