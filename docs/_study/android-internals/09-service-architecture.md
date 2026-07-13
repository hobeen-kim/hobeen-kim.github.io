---
title: "CH9. 서비스 아키텍처"
description: "안드로이드에서 '서비스'의 세 가지 의미, 왜 소켓이 아닌 Binder인가, 세 개의 Binder 도메인(framework/vnd/hw), ServiceManager 부트스트랩, VINTF, 그리고 system_server의 3단계 기동과 서비스 그룹을 다룬다."
date: 2026-07-13
tags: [android, aosp, binder, servicemanager, system-server, vintf]
---

# CH9. 서비스 아키텍처

## 학습 목표
- 안드로이드에서 "서비스"의 세 가지 의미(init/system/app)를 구분한다.
- 왜 소켓·파이프가 아니라 Binder를 IPC의 중심으로 택했는지 이해한다.
- 세 개의 Binder 도메인(framework/vnd/hw)과 vendor 데몬이 어느 것을 쓰는지 안다.
- ServiceManager의 addService/getService 흐름과 부트스트랩 문제를 파악한다.
- system_server의 3단계 기동과 주요 서비스 그룹, watchdog을 이해한다.

## 1. "서비스"의 세 가지 의미

안드로이드 문서에서 "서비스"라는 단어는 문맥에 따라 완전히 다른 것을 가리킨다. 이 셋을 구분하지 못하면 이후 모든 논의가 흐려진다.

- <strong>init service</strong> — [CH8](/study/android-internals/08-init-zygote)에서 다룬 `*.rc`의 `service` 블록. init이 관리하는 <strong>네이티브 프로세스/데몬</strong>이다(예: `vold`, `netd`, 커스텀 `can_daemon`). "프로세스로서의 서비스".
- <strong>system service</strong> — `system_server` 안에서 도는 <strong>프레임워크 서비스</strong>(예: ActivityManagerService, PackageManagerService). Binder로 노출되고 ServiceManager에 등록된다. "Binder 객체로서의 서비스".
- <strong>app Service</strong> — 앱 개발자가 `android.app.Service`를 상속해 만드는 <strong>앱 컴포넌트</strong>. 백그라운드 작업용이며 Activity·Broadcast와 함께 앱의 4대 컴포넌트 중 하나다. [CH18](/study/android-internals/18-app-anatomy)에서 다룬다.

이 챕터의 주역은 두 번째, <strong>system service</strong>와 그것을 떠받치는 Binder·ServiceManager 인프라다.

<strong>프레임워크 서비스 호출 구조</strong>는 일관된 4단 패턴을 따른다. 앱이 `getSystemService(...)`로 <strong>Manager</strong> 객체를 얻으면, Manager 내부에는 실제 서비스의 <strong>프록시(proxy, Stub.Proxy)</strong>가 있다. 앱이 Manager 메서드를 호출하면 프록시가 인자를 `Parcel`로 마샬링해 <strong>Binder</strong>를 통해 다른 프로세스(`system_server`)의 <strong>실제 서비스(Stub 구현)</strong>로 넘긴다. 호출자는 마치 로컬 메서드를 부른 것처럼 결과를 돌려받는다.

```text
앱 프로세스                          system_server 프로세스
─────────────                       ──────────────────────
getSystemService()                  ActivityManagerService
   → ActivityManager (Manager)         (실제 구현 · Stub)
       → IActivityManager.Proxy  ──Binder──▶  onTransact()
          (Parcel 마샬링)                       (언마샬링·실행)
```

이 "원격인데 로컬처럼" 착시를 만들어내는 것이 Binder다.

## 2. Binder 첫 개요 — 왜 소켓이 아닌가

리눅스에는 이미 파이프, 소켓, System V IPC, 공유 메모리가 있다. 그런데 안드로이드는 <strong>Binder</strong>라는 자체 IPC를 커널 드라이버(`/dev/binder`)로 만들어 시스템 전체를 그 위에 얹었다. 이유가 있다. (Binder의 유저스페이스·커널 내부는 [CH21](/study/android-internals/21-binder-userspace)~[CH22](/study/android-internals/22-binder-kernel)에서 깊게 다루므로, 여기서는 개요만 잡는다.)

- <strong>객체(핸들) 전달.</strong> 소켓은 바이트 스트림만 옮긴다. Binder는 <strong>다른 프로세스의 객체 참조(binder handle)를 통째로 전달</strong>할 수 있다. A가 B에게 콜백 객체를 넘기면, B는 그 핸들로 A를 다시 호출한다. 분산 객체 시스템이 언어 차원에서 자연스럽다.
- <strong>신원 보증.</strong> 소켓으로는 상대가 누구인지 위조 없이 알기 어렵다. Binder는 커널이 <strong>호출자의 uid/pid를 커널에서 직접 실어 전달</strong>한다(`Binder.getCallingUid()`). 권한 검사가 위조 불가능하다 — 안드로이드 권한 모델의 토대다.
- <strong>참조 카운팅과 죽음 통지.</strong> 커널이 binder 객체의 참조 수를 세고, 상대 프로세스가 죽으면 <strong>death recipient</strong> 콜백으로 알려준다. 서비스가 죽었는데 프록시가 그걸 모르는 사태를 방지한다.
- <strong>동기 호출 + 스레드 풀.</strong> Binder는 원격 메서드 호출을 동기(호출자 블로킹)로 처리하고, 각 프로세스의 <strong>binder 스레드 풀</strong>이 들어오는 트랜잭션을 병렬 처리한다. RPC 프로그래밍 모델이 단순하다.
- <strong>단일 복사.</strong> 커널이 트랜잭션 버퍼를 관리해 데이터 복사를 최소화한다(전통 IPC의 이중 복사 대비 유리).

정리하면, Binder는 "권한이 보증되고, 객체를 주고받으며, 상대의 죽음을 알 수 있는 동기 RPC"다. 이게 소켓으로는 각각 직접 구현해야 하는 것들이다.

## 3. 세 개의 Binder 도메인

Binder는 하나가 아니다. 커널 드라이버가 <strong>세 개의 독립 인스턴스</strong>로 존재하고, 각 인스턴스는 서로 통신하지 못한다. Treble([CH1](/study/android-internals/01-architecture-evolution)) 이후 system과 vendor 코드를 분리하기 위한 핵심 장치다.

![framework binder(/dev/binder), vendor binder(/dev/vndbinder), hw binder(/dev/hwbinder) 세 도메인이 각각의 프로세스와 servicemanager를 가지고 분리돼 있는 구조](/images/study-android-internals/09-three-binders-light.png)
![framework binder(/dev/binder), vendor binder(/dev/vndbinder), hw binder(/dev/hwbinder) 세 도메인이 각각의 프로세스와 servicemanager를 가지고 분리돼 있는 구조](/images/study-android-internals/09-three-binders-dark.png)

- <strong>`/dev/binder` (framework binder).</strong> 앱·`system_server`·framework 서비스들이 쓰는 기본 도메인. 우리가 보통 "Binder"라 하면 이것이다. `servicemanager`가 레지스트리를 담당한다.
- <strong>`/dev/vndbinder` (vendor binder).</strong> <strong>vendor 프로세스끼리</strong>의 통신 전용. Treble이 vendor 코드가 framework 내부 API에 의존하지 못하게 막으면서, vendor 데몬끼리는 여전히 Binder IPC가 필요하니 별도 도메인을 준 것이다. `vndservicemanager`가 레지스트리다.
- <strong>`/dev/hwbinder` (hw binder).</strong> HAL(Hardware Abstraction Layer) 통신 전용. HIDL 시대에 HAL 서버/클라이언트가 이 도메인을 쓰고 `hwservicemanager`가 레지스트리였다. AIDL HAL로 전환되면서 HAL도 점차 `/dev/binder`(vendor 컨텍스트)를 쓰는 방향으로 이동 중이다.

<strong>네이티브 vendor 데몬은 어느 Binder를 쓰는가.</strong> 우리의 CAN 데몬처럼 `/vendor/bin`에 있는 네이티브 데몬이 Binder IPC를 하려면 기본적으로 <strong>`/dev/vndbinder`</strong>를 쓴다. 코드에서 `ProcessState::initWithDriver("/dev/vndbinder")`로 도메인을 명시하고, `vndservicemanager`에 등록한다. 만약 이 데몬이 자체 AIDL HAL 인터페이스를 노출해 framework에서 호출받아야 한다면, VINTF에 등록된 <strong>AIDL HAL</strong>로 만들어 vendor 컨텍스트의 `/dev/binder`를 통해 노출하는 방식을 택한다(5절 VINTF, 실습은 [CH23](/study/android-internals/23-native-daemon-case-study)).

```cpp
// vendor 네이티브 데몬에서 vndbinder 사용 (개념 예시)
android::ProcessState::initWithDriver("/dev/vndbinder");
sp<IServiceManager> sm = defaultServiceManager();  // vndservicemanager로 라우팅
sm->addService(String16("vendor.can.daemon"), new CanService());
```

## 4. ServiceManager — 레지스트리와 부트스트랩

Binder 트랜잭션을 하려면 상대 서비스의 <strong>binder 핸들</strong>을 알아야 한다. 그런데 처음 시작하는 프로세스는 그 핸들을 어디서 얻나? 이 문제를 푸는 것이 <strong>ServiceManager</strong>, 안드로이드의 이름→핸들 디렉토리 서비스다.

- <strong>addService(name, binder).</strong> 서비스가 자기 자신을 이름과 함께 등록한다. 예: `system_server`가 `"activity"` 이름으로 AMS를 등록.
- <strong>getService(name) / checkService(name).</strong> 클라이언트가 이름으로 서비스의 binder 핸들을 조회한다. `getService`는 아직 등록 안 됐으면 잠시 대기·재시도한다.
- <strong>listServices().</strong> 등록된 모든 서비스 이름을 나열한다.

<strong>부트스트랩 문제.</strong> ServiceManager 자신도 Binder 서비스다. 그런데 다른 서비스를 찾으려면 ServiceManager의 핸들이 필요한데, 그 ServiceManager의 핸들은 누가 알려주나? 닭과 달걀이다. 안드로이드는 이를 <strong>고정 핸들 0번</strong>으로 푼다. ServiceManager는 binder 드라이버에 자신을 <strong>context manager</strong>로 등록하고(`BINDER_SET_CONTEXT_MGR`), 이 특별한 노드는 <strong>항상 핸들 0</strong>이다. 따라서 어떤 프로세스든 "핸들 0에게 트랜잭션을 보내면 그게 ServiceManager"라는 약속만으로 부트스트랩이 성립한다. `defaultServiceManager()`가 내부에서 핸들 0을 감싼 프록시를 돌려준다.

```bash
# 등록된 서비스 목록 (framework binder)
adb shell service list
# 예: 0  activity: [android.app.IActivityManager]
#     1  package: [android.content.pm.IPackageManager] ...

adb shell service check activity     # 특정 서비스 등록 여부 확인

# vendor 도메인 레지스트리는 별도
adb shell vndservicemanager -l 2>/dev/null || adb shell service list | grep vendor.
```

`servicemanager`는 init이 아주 이른 단계에서 띄우는 `critical` 서비스다. 이게 죽으면 framework 전체가 서로를 찾지 못하므로 init이 시스템을 재시작한다.

## 5. VINTF — vendor 인터페이스의 계약

Treble은 system 이미지와 vendor 이미지를 <strong>독립적으로 업데이트</strong>할 수 있게 하는 것이 목표다. 그러려면 "이 vendor 이미지가 제공하는 HAL"과 "이 system 이미지가 요구하는 HAL"이 서로 호환되는지 검증할 방법이 필요하다. 그 계약이 <strong>VINTF(Vendor Interface)</strong>다.

- <strong>manifest.xml.</strong> vendor(및 framework) 쪽이 "나는 이러이러한 HAL을 이 버전으로 제공한다"를 선언한다(`/vendor/etc/vintf/manifest.xml`). AIDL HAL이면 인터페이스 이름·버전, HIDL이면 패키지·버전을 명시한다.
- <strong>compatibility matrix.</strong> 반대쪽이 "나는 최소 이 버전 이상의 이런 HAL을 요구한다"를 선언한다(`compatibility_matrix.xml`). framework matrix ↔ vendor manifest, vendor matrix ↔ framework manifest를 교차 대조한다.
- <strong>호환성 검증.</strong> 부팅 시(그리고 OTA 전에) manifest와 matrix를 대조해 하나라도 요구를 만족하지 못하면 부팅/업데이트를 거부한다. `vintf` 명령으로 조회할 수 있다.

```bash
adb shell cat /vendor/etc/vintf/manifest.xml    # vendor가 제공하는 HAL 선언
adb shell vintf                                  # 현재 VINTF 상태 덤프 (지원 시)
adb shell lshal                                  # 등록된 HAL 목록·연결 상태
```

<strong>AIDL HAL을 등록하면 VINTF 검증에 걸린다.</strong> 커스텀 CAN 데몬을 단순 vendor 데몬이 아니라 <strong>AIDL HAL</strong>로 노출하려면, 그 인터페이스를 `manifest.xml`에 선언해야 하고, 선언과 실제 등록된 서비스가 어긋나면 `vts`/부팅 검증에서 실패한다. 이 등록·검증 실습은 [CH23](/study/android-internals/23-native-daemon-case-study)에서 처음부터 진행한다.

## 6. system_server 해부

[CH8](/study/android-internals/08-init-zygote)에서 Zygote가 부팅 직후 첫 자식으로 `system_server`를 fork한다고 했다. 이 프로세스 하나 안에 안드로이드 프레임워크의 <strong>수십 개 핵심 서비스</strong>가 스레드로 함께 산다.

![Zygote가 fork한 SystemServer.main이 startBootstrapServices, startCoreServices, startOtherServices 3단계로 서비스를 올리고 Watchdog이 감시하는 구조](/images/study-android-internals/09-system-server-light.png)
![Zygote가 fork한 SystemServer.main이 startBootstrapServices, startCoreServices, startOtherServices 3단계로 서비스를 올리고 Watchdog이 감시하는 구조](/images/study-android-internals/09-system-server-dark.png)

<strong>기동 과정.</strong> Zygote가 `com.android.server.SystemServer`를 진입점으로 fork하면 `SystemServer.main()` → `run()`이 실행된다. 여기서 서비스들을 <strong>세 그룹으로 순서대로</strong> 올린다. 순서가 중요한 이유는 뒤 서비스가 앞 서비스에 의존하기 때문이다.

- <strong>startBootstrapServices().</strong> 다른 거의 모든 것이 의존하는 최소 기반. `Installer`(installd 연동), `ActivityManagerService(AMS)`, `PowerManagerService`, `PackageManagerService(PMS)`, `LightsService` 등. AMS는 여기서 가장 먼저 자리를 잡는다.
- <strong>startCoreServices().</strong> 그다음 계층. `BatteryService`, `UsageStatsService`, `WebViewUpdateService` 등.
- <strong>startOtherServices().</strong> 나머지 대다수. `WindowManagerService(WMS)`, `InputManagerService`, `Connectivity/NetworkManagementService`, `AudioService`, `BluetoothService`... 여기서 만든 서비스들이 하나씩 `ServiceManager.addService()`로 등록된다.

각 서비스는 만들어지는 즉시 ServiceManager에 등록되므로, 그 시점부터 앱이 `getSystemService`로 접근할 수 있다. 세 단계를 마치면 `system_server`는 메인 루퍼(main looper)로 진입해 Binder 트랜잭션을 처리하는 상시 서버가 된다.

<strong>watchdog.</strong> `system_server`가 죽으면 사실상 UI 전체가 재시작(soft reboot)된다. 그래서 내부에 <strong>Watchdog</strong> 스레드가 있어 주요 서비스의 락·핸들러가 정해진 시간(기본 60초) 안에 응답하는지 감시한다. 어떤 서비스가 데드락 등으로 오래 블로킹되면 Watchdog이 <strong>`system_server`를 의도적으로 죽여</strong> 재시작시킨다. 굳은 채로 방치되는 것보다 재시작이 낫다는 판단이다. `dmesg`/`logcat`에서 `Watchdog` 태그로 그 흔적을 볼 수 있다.

## 7. 서비스 조감도 — dumpsys와 service call

실제 기기에서 서비스를 관찰·호출하는 실전 도구는 `dumpsys`와 `service`다.

<strong>dumpsys</strong>는 등록된 각 system service에게 "네 상태를 사람이 읽을 수 있게 덤프해라"고 요청한다. 서비스마다 자기 내부 상태를 텍스트로 뱉는다.

```bash
adb shell dumpsys                 # 모든 서비스 덤프 (매우 김)
adb shell dumpsys -l              # 덤프 가능한 서비스 목록
adb shell dumpsys activity        # AMS: 액티비티/프로세스/태스크 상태
adb shell dumpsys package <pkg>   # PMS: 특정 패키지 정보·권한
adb shell dumpsys battery         # 배터리 상태 (조작도 가능: set/reset)
adb shell dumpsys meminfo <pkg>   # 프로세스 메모리 분석
```

<strong>service call</strong>은 한 단계 더 저수준이다. 서비스의 Binder 인터페이스에 <strong>트랜잭션 코드와 인자를 직접</strong> 던진다. 인터페이스의 메서드 순번(transaction id)과 Parcel 인자를 손으로 구성해야 하므로 디버깅·리버싱용이다.

```bash
adb shell service list                       # 서비스와 인터페이스 이름 확인
# SurfaceFlinger에 트랜잭션 코드 1013을 호출해 프레임 카운트 조회 (예시)
adb shell service call SurfaceFlinger 1013
```

커스텀 네이티브 데몬을 Binder 서비스로 올린 뒤에는, `service list`(또는 vendor 도메인 조회)로 등록 여부를 확인하고 `dumpsys`로 상태를 노출하도록 만드는 것이 표준적인 운영 관측 방법이다. 이 전 과정을 [CH23](/study/android-internals/23-native-daemon-case-study)에서 CAN 데몬으로 직접 구현한다.

::: tip 핵심 정리
- "서비스"는 init service(네이티브 데몬), system service(system_server 안 Binder 서비스), app Service(앱 컴포넌트) 셋으로 갈리며, 프레임워크 호출은 Manager → 프록시 → Binder → 실제 서비스 4단 패턴을 따른다.
- Binder를 택한 이유는 객체(핸들) 전달, 커널이 보증하는 호출자 uid/pid, 참조 카운팅·death notification, 동기 RPC+스레드 풀이며, 이는 소켓으로는 각각 직접 구현해야 하는 것들이다.
- Binder 도메인은 `/dev/binder`(framework)·`/dev/vndbinder`(vendor끼리)·`/dev/hwbinder`(HAL)로 분리되고, 네이티브 vendor 데몬은 기본적으로 vndbinder를, HAL로 노출하면 VINTF에 등록된 AIDL HAL 경로를 쓴다.
- ServiceManager는 이름→핸들 레지스트리이며, 자신을 고정 핸들 0(context manager)으로 등록해 부트스트랩 문제를 푼다.
- system_server는 Zygote가 첫 fork한 프로세스로, startBootstrap/Core/OtherServices 3단계로 AMS·PMS·WMS 등을 올려 ServiceManager에 등록하고, Watchdog이 블로킹을 감지하면 스스로 재시작한다.
:::

## 다음 챕터
[CH10. 설정과 관리](/study/android-internals/10-configuration)에서는 시스템 설정 데이터베이스(Settings provider), 디바이스 정책, 그리고 런타임 구성 관리를 다룬다.
