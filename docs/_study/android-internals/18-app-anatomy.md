---
title: "CH18. 애플리케이션 해부"
description: "4대 컴포넌트가 프레임워크 관점에서 무엇인지, Launcher 탭에서 첫 프레임까지의 앱 시작 시퀀스, Looper/Handler/MessageQueue 이벤트 루프와 ANR, JNI 호출 규약, oom_adj 기반 앱 생명주기, 그리고 디컴파일까지 안드로이드 앱의 내부를 해부한다."
date: 2026-07-13
tags: [android, aosp, app, jni, looper, lifecycle]
---

# CH18. 애플리케이션 해부

앱 개발자는 `Activity`를 상속하고 `onCreate`를 채우지만, 그 콜백이 <strong>어떻게 불리는지</strong>는 프레임워크의 몫이라 보이지 않는다. 이 챕터는 그 커튼 뒤를 본다. 4대 컴포넌트가 system_server 관점에서 실제로 무엇인지, 앱 프로세스가 어떻게 태어나 첫 콜백을 받는지, 메인 스레드가 왜 멈추면 ANR이 뜨는지, 그리고 네이티브 코드가 자바 세계와 만나는 JNI 경계를 짚는다. CAN 데몬 같은 네이티브 코드를 앱에 얹는 작업에 직접 닿는 내용이다.

## 학습 목표

- Activity/Service/BroadcastReceiver/ContentProvider가 프레임워크 관점에서 무엇인지 이해한다.
- Launcher 탭에서 Activity 첫 프레임까지의 앱 시작 시퀀스를 단계별로 추적한다.
- Looper/Handler/MessageQueue 이벤트 루프의 동작과 ANR의 정체를 파악한다.
- JNI_OnLoad·메서드 등록·JNIEnv·레퍼런스 관리와 CriticalNative/FastNative를 익힌다.
- oom_adj 기반 프로세스 상태와 앱 생명주기, 디컴파일 도구를 안다.

## 4대 컴포넌트의 실체

앱 개발 문서는 4대 컴포넌트를 "구성 요소"라 부르지만, 프레임워크 관점에서 이들의 공통된 실체는 <strong>system_server가 관리하는 기록과 Binder 콜백</strong>이다. 컴포넌트는 스스로 도는 무언가가 아니라, system_server의 상태 머신이 적절한 시점에 앱 프로세스로 Binder 호출을 보내 콜백을 트리거하는 대상이다.

- <strong>Activity</strong>는 화면 하나에 대응하지만, 그 생명주기(생성·시작·재개·정지·파괴)를 결정하는 것은 앱이 아니라 <strong>ActivityTaskManagerService(ATMS)</strong>다. 앱 프로세스에는 `ActivityThread`가 있고, ATMS가 `IApplicationThread` Binder 인터페이스를 통해 "onCreate 해라", "onResume 해라"를 지시한다. Activity의 back stack·task도 전부 system_server 쪽 자료구조다.
- <strong>Service</strong>는 UI 없는 백그라운드 작업 단위다. `startService`는 `ActivityManagerService(AMS)`에 서비스 기록을 만들고, `bindService`는 클라이언트와 서비스를 Binder로 연결한다. 서비스가 "살아있다"는 것도 AMS가 그 프로세스를 유지 대상으로 표시한다는 의미다.
- <strong>BroadcastReceiver</strong>는 이벤트 수신자다. AMS가 브로드캐스트를 받아 매칭되는 리시버 목록을 만들고 순서대로 `onReceive`를 Binder로 디스패치한다. 정적 등록(매니페스트)과 동적 등록(`registerReceiver`)의 차이도 AMS가 목록을 어디서 관리하느냐의 차이다.
- <strong>ContentProvider</strong>는 프로세스 간 데이터 공유 창구다. 다른 앱이 `content://` URI로 접근하면 AMS가 provider를 호스팅하는 프로세스를 찾아(없으면 띄워) Binder 채널을 연결한다. Provider는 사실상 <strong>Binder 위에 얹힌 데이터 게이트웨이</strong>다.

이 네 컴포넌트를 이어주는 것이 <strong>Intent</strong>다. `startActivity`나 `sendBroadcast`에 담긴 Intent를 AMS가 받아, 설치된 패키지의 `<intent-filter>`와 대조해 어떤 컴포넌트가 처리할지 고르는 것이 <strong>intent resolution</strong>이다. 명시적 Intent(컴포넌트 지정)는 바로 매칭되고, 암시적 Intent(action/category/data)는 PMS가 등록해둔 필터를 질의해 후보를 추린다. Binder의 유저스페이스 동작은 [CH21](/study/android-internals/21-binder-userspace)에서 본격적으로 다룬다.

## 앱 시작의 이면

사용자가 Launcher에서 앱 아이콘을 탭하는 순간부터 첫 프레임이 그려지기까지, 여러 프로세스가 정해진 순서로 협업한다. 이 시퀀스를 알면 "콜드 스타트가 왜 느린지", "onCreate 앞에서 무슨 일이 있었는지"가 보인다.

![Launcher 탭에서 Activity 첫 프레임까지의 앱 시작 시퀀스 — system_server, Zygote fork, 앱 프로세스 attach와 bindApplication 흐름](/images/study-android-internals/18-app-launch-seq-light.png)
![Launcher 탭에서 Activity 첫 프레임까지의 앱 시작 시퀀스 — system_server, Zygote fork, 앱 프로세스 attach와 bindApplication 흐름](/images/study-android-internals/18-app-launch-seq-dark.png)

1. <strong>Launcher → system_server.</strong> Launcher도 하나의 앱일 뿐이라, 아이콘 탭은 `startActivity()` Binder 호출로 ATMS에 전달된다. ATMS는 대상 Activity를 호스팅할 프로세스가 이미 살아있는지 확인한다.
2. <strong>프로세스가 없으면 Zygote에 fork 요청.</strong> ATMS/AMS는 `Process.start()`로 이어져, [Zygote](/study/android-internals/08-init-zygote)의 소켓(`/dev/socket/zygote`)에 프로세스 생성을 요청한다. 이미 클래스와 리소스를 프리로드한 Zygote를 <strong>fork</strong>하므로 새 프로세스는 초기화 비용 없이 출발한다.
3. <strong>fork + specialize.</strong> Zygote가 자신을 fork하고, 자식은 대상 앱의 UID/GID·SELinux 컨텍스트·seccomp 필터를 적용(specialize)한 뒤 `ActivityThread.main()`으로 진입한다. 여기서 메인 Looper가 준비된다.
4. <strong>attachApplication.</strong> 새 앱 프로세스가 AMS에 `attachApplication()`을 Binder로 호출해 "나 떴다"고 알린다. AMS는 그 프로세스에 `IApplicationThread`를 통해 <strong>bindApplication</strong>을 지시한다.
5. <strong>bindApplication → onCreate.</strong> 앱 프로세스가 `Application` 객체를 만들고 `Application.onCreate()`를 부른 뒤, ATMS의 지시에 따라 대상 `Activity`를 인스턴스화하고 `onCreate → onStart → onResume`을 차례로 호출한다.
6. <strong>첫 프레임.</strong> `onResume` 이후 뷰 트리가 측정·배치·그리기를 거쳐 첫 프레임이 렌더된다. 이 지점이 사용자가 체감하는 "앱이 떴다"의 순간이다.

이미 프로세스가 살아있으면 2~5단계를 건너뛰는 <strong>warm/hot start</strong>가 되어 훨씬 빠르다. 콜드 스타트 최적화가 어려운 이유는 fork·bindApplication·리소스 로딩이라는 고정 비용이 앞단에 깔려 있기 때문이다.

## Looper/Handler/MessageQueue

앱의 메인 스레드는 단순한 함수 호출의 연속이 아니라 <strong>무한 이벤트 루프</strong>다. `ActivityThread.main()`은 마지막에 `Looper.loop()`를 호출하고 여기서 영원히 돌면서 이벤트를 처리한다. 생명주기 콜백, 터치 이벤트, 화면 갱신이 전부 이 루프 위의 메시지다.

![메인 스레드 Looper/Handler/MessageQueue 구조 — MessageQueue에서 Looper가 메시지를 꺼내 dispatch하고 큐가 비면 epoll_wait로 블록하며 Handler와 입력 소스가 enqueue하는 흐름](/images/study-android-internals/18-looper-light.png)
![메인 스레드 Looper/Handler/MessageQueue 구조 — MessageQueue에서 Looper가 메시지를 꺼내 dispatch하고 큐가 비면 epoll_wait로 블록하며 Handler와 입력 소스가 enqueue하는 흐름](/images/study-android-internals/18-looper-dark.png)

- <strong>MessageQueue</strong>는 실행 시각(`when`) 순으로 정렬된 메시지 연결 리스트다. 자바 객체지만 실제 대기는 네이티브 계층에서 이뤄진다.
- <strong>Looper</strong>는 `next()`로 큐에서 다음 메시지를 꺼내 대상 Handler의 `dispatchMessage`로 넘긴다. 큐가 비면 바쁘게 도는 게 아니라 네이티브의 <strong>epoll_wait</strong>에서 블록해 CPU를 0%로 내린다. 새 메시지가 들어오거나 등록된 fd에 이벤트가 오면 깨어난다.
- <strong>Handler</strong>는 특정 Looper에 묶여, `post()`/`sendMessage()`로 메시지를 큐에 <strong>enqueue</strong>한다. 다른 스레드에서 UI를 갱신하려면 메인 Handler에 작업을 던지는 것이 정석이다.
- <strong>입력 소스.</strong> 터치·센서 입력, `Choreographer`의 VSYNC 신호, Binder 콜백이 모두 이 큐로 흘러든다. `MessageQueue`는 자바 메시지뿐 아니라 네이티브 fd도 함께 감시(`addOnFileDescriptorEventListener`, 내부적으로 `epoll`)하기 때문에 이질적인 이벤트 소스를 하나의 루프에서 처리할 수 있다.

<strong>ANR(Application Not Responding)의 정체</strong>가 여기서 드러난다. ANR은 앱이 "죽은" 게 아니라 <strong>메인 스레드가 메시지 하나를 제때 처리하지 못한</strong> 상태다. 입력 이벤트가 큐에 들어왔는데 앞선 메시지(예: 오래 걸리는 DB 쿼리, 네트워크 대기)가 메인 스레드를 붙잡고 있으면, 정해진 시간(입력 디스패치 약 5초, 브로드캐스트 포그라운드 약 10초, 서비스 실행 등 종류별로 다름) 안에 처리를 못 해 AMS가 ANR을 띄운다. 그래서 무거운 작업은 반드시 별도 스레드로 보내야 한다. ANR 발생 시 AMS는 `/data/anr/traces.txt`에 모든 스레드의 스택을 덤프하므로, 이 파일에서 메인 스레드가 어디서 멈췄는지 확인하는 것이 1차 진단이다.

## JNI

앱에 네이티브 코드를 올리려면 자바와 C/C++ 사이의 다리인 <strong>JNI(Java Native Interface)</strong>를 거쳐야 한다. 임베디드 기기에서 CAN 통신 스택 같은 네이티브 라이브러리를 앱과 연결할 때 정확히 이 경계를 다루게 된다.

<strong>JNI_OnLoad.</strong> `System.loadLibrary("mylib")`로 `.so`가 로드되면 런타임이 그 라이브러리의 `JNI_OnLoad`를 부른다. 여기서 JNI 버전을 반환하고, 흔히 네이티브 메서드를 등록한다.

```cpp
// 동적 등록: 이름 매칭 대신 테이블로 한 번에 연결 (권장)
static jint nativeAdd(JNIEnv* env, jclass clazz, jint a, jint b) {
    return a + b;
}

static const JNINativeMethod kMethods[] = {
    {"nativeAdd", "(II)I", reinterpret_cast<void*>(nativeAdd)},
};

jint JNI_OnLoad(JavaVM* vm, void*) {
    JNIEnv* env = nullptr;
    if (vm->GetEnv(reinterpret_cast<void**>(&env), JNI_VERSION_1_6) != JNI_OK)
        return JNI_ERR;
    jclass c = env->FindClass("com/oem/can/CanBridge");
    env->RegisterNatives(c, kMethods, sizeof(kMethods) / sizeof(kMethods[0]));
    return JNI_VERSION_1_6;
}
```

메서드 등록에는 두 방식이 있다. <strong>정적 등록</strong>은 `Java_com_oem_can_CanBridge_nativeAdd`처럼 이름 규칙을 맞추면 런타임이 심볼을 찾아 연결한다—간단하지만 이름이 길고 첫 호출 시 심볼 조회 비용이 있다. <strong>동적 등록</strong>은 위처럼 `RegisterNatives`로 테이블을 넘겨 즉시 연결한다—이름 규칙에서 자유롭고 성능·명확성 면에서 권장된다.

<strong>JNIEnv</strong>는 네이티브 코드가 자바 세계에 접근하는 핸들이다. 필드·메서드 조회, 객체 생성, 예외 처리 함수가 여기 달려 있다. <strong>스레드마다 다른 JNIEnv</strong>를 쓰며, 다른 언어 스레드에서 자바를 호출하려면 `AttachCurrentThread`로 붙여야 한다.

<strong>레퍼런스 관리</strong>는 JNI에서 가장 실수가 잦은 부분이다. <strong>로컬 레퍼런스</strong>는 네이티브 메서드가 리턴하면 자동 해제되며, 개수 제한이 있어 루프에서 대량 생성하면 넘칠 수 있다(`DeleteLocalRef`로 조기 해제). <strong>글로벌 레퍼런스</strong>는 `NewGlobalRef`로 만들어 여러 호출·스레드에 걸쳐 살아남지만 `DeleteGlobalRef`로 직접 해제해야 하며, 빠뜨리면 누수다.

<strong>CriticalNative/FastNative.</strong> JNI 호출은 기본적으로 스레드 상태 전환·레퍼런스 테이블 설정 같은 오버헤드가 있다. `@FastNative`는 이 전환을 줄이고, `@CriticalNative`는 `JNIEnv`·`jclass` 인자조차 없애고 GC 안전점 관리를 생략해 순수 계산 함수를 거의 직접 호출 수준으로 만든다. 다만 `@CriticalNative` 함수 안에서는 JNI 호출이나 객체 접근이 금지된다. 고빈도로 불리는 CAN 신호 파싱 같은 순수 함수에 적합하다.

## 네이티브에서 프레임워크 서비스 접근

네이티브 데몬이나 라이브러리가 자바를 거치지 않고 직접 시스템 서비스와 통신해야 할 때가 있다. 이때는 <strong>libbinder</strong>로 직접 Binder 채널을 열고, 인터페이스는 <strong>AIDL의 NDK 백엔드</strong>로 생성한 C++ 스텁을 쓴다.

```
// Android.bp — AIDL NDK 백엔드 활성화
aidl_interface {
    name: "com.oem.ican",
    srcs: ["com/oem/ICanService.aidl"],
    backend: { ndk: { enabled: true } },
}
```

생성된 `BnCanService`/`BpCanService`로 네이티브 서비스를 `servicemanager`에 등록하거나 조회할 수 있다. 이 방식은 CAN 데몬을 <strong>Binder 서비스로 노출</strong>해 앱과 통신시키는 [CH23 케이스 스터디](/study/android-internals/23-native-daemon-case-study)의 토대가 된다. libbinder의 유저스페이스 상세는 [CH21](/study/android-internals/21-binder-userspace)에서 다룬다.

## 앱 생명주기의 이면

안드로이드는 메모리가 부족하면 앱 프로세스를 죽인다. 어떤 프로세스를 죽일지는 각 프로세스의 <strong>oom_adj</strong>(리눅스 OOM killer가 참고하는 조정값)로 결정되고, AMS가 앱의 상태에 따라 이 값을 계속 갱신한다.

- <strong>포그라운드</strong> 프로세스(화면에 보이는 Activity, 포그라운드 서비스)는 가장 낮은 oom_adj를 받아 마지막까지 살아남는다.
- <strong>visible / perceptible</strong>은 부분적으로 보이거나 사용자가 인지하는 작업이다.
- <strong>service</strong>는 백그라운드 서비스를 실행 중인 프로세스다.
- <strong>cached</strong> 프로세스는 아무 컴포넌트도 활성이 아니지만 재실행을 빠르게 하려고 캐시로 남겨둔 상태다. 메모리 압박이 오면 이 그룹부터 LRU 순으로 죽는다.

프로세스가 죽어도 <strong>상태는 복원</strong>될 수 있다. Activity는 죽기 전 `onSaveInstanceState`로 상태를 저장하고, 사용자가 돌아오면 시스템이 프로세스를 재생성해 `savedInstanceState`로 복원한다. 그래서 앱은 "언제든 죽을 수 있다"는 전제로 상태를 관리해야 한다. 리눅스 관점의 프로세스·메모리 지표는 [CH11](/study/android-internals/11-linux-lens)을 참고한다.

```bash
# 앱 프로세스의 oom_adj_score 확인
pid=$(pidof com.example.app)
cat /proc/$pid/oom_score_adj

# AMS가 본 프로세스 우선순위·상태
dumpsys activity oom | grep com.example.app
```

## 디컴파일

앱 내부를 역으로 들여다보는 도구들도 알아두면 문제 분석에 유용하다. 프리로드 앱의 동작을 검증하거나 서드파티 APK의 권한 사용을 감사할 때 쓴다.

- <strong>apktool</strong>은 APK를 풀어 바이너리 매니페스트를 텍스트로, DEX를 smali로 디코드한다. 리소스 구조와 매니페스트를 사람이 읽는 형태로 복원하는 데 좋다.
- <strong>jadx</strong>는 DEX를 <strong>자바 소스에 가깝게</strong> 역컴파일해 보여준다. 로직을 빠르게 파악할 때 가장 편하다.
- <strong>dexdump/baksmali</strong>는 DEX 바이트코드를 디스어셈블한다. smali/바이트코드 수준의 정밀 분석은 [CH19](/study/android-internals/19-dalvik-dex)의 주제다.

```bash
# 자바 소스에 가깝게 역컴파일
jadx -d out app.apk

# 리소스+smali로 분해
apktool d app.apk -o app_src
```

::: warning 디컴파일과 권리
자사가 만든 앱이나 정당한 분석 목적이 아니면 타사 APK의 역컴파일은 라이선스·법적 문제가 될 수 있다. 커스텀 기기의 프리로드 앱 검증처럼 권한 범위 안에서만 사용한다.
:::

::: tip 핵심 정리
- 4대 컴포넌트의 실체는 system_server(ATMS/AMS)가 관리하는 기록과 Binder 콜백이며, Intent resolution이 이들을 연결한다.
- 앱 시작은 Launcher → ATMS → Zygote fork/specialize → attachApplication → bindApplication → onCreate/Resume → 첫 프레임 순으로 진행된다.
- 메인 스레드는 Looper/Handler/MessageQueue 이벤트 루프이며, 큐가 비면 epoll_wait로 블록하고, 메인 스레드가 메시지를 제때 못 처리하면 ANR이 발생한다.
- JNI는 JNI_OnLoad·정적/동적 메서드 등록·스레드별 JNIEnv·로컬/글로벌 레퍼런스로 자바-네이티브를 잇고, CriticalNative/FastNative로 오버헤드를 줄인다.
- 프로세스는 oom_adj로 우선순위가 매겨져 cached부터 죽으며, onSaveInstanceState로 상태를 복원한다.
:::

## 다음 챕터

[CH19. Dalvik과 DEX](/study/android-internals/19-dalvik-dex)에서는 레지스터 기반 Dalvik VM이 왜 만들어졌는지, DEX 파일 포맷의 헤더와 인덱스 테이블, 65536 메서드 한계와 multidex, 그리고 DEX 바이트코드와 smali를 손으로 읽는 법을 다룬다.
