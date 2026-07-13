---
title: "CH21. Binder — 유저스페이스"
description: "AIDL·Parcel·libbinder를 관통하는 Binder 프로그래밍 모델. 프록시/스텁, AIDL 컴파일러가 생성하는 백엔드별 코드, Parcel wire format, framework와 native(libbinder)·NDK(libbinder_ndk)의 클래스 계층을 vendor 데몬 관점에서 해부한다."
date: 2026-07-13
tags: [android, aosp, binder, aidl, ipc, libbinder]
---

# CH21. Binder — 유저스페이스

::: info 학습 목표
- 프록시/스텁, 인터페이스 토큰, oneway와 동기 호출로 구성된 Binder 프로그래밍 모델을 이해한다.
- AIDL 문법과 컴파일러가 java/cpp/ndk/rust 백엔드별로 생성하는 코드, stable AIDL 버저닝 규칙을 파악한다.
- Parcel의 wire format과 파일 디스크립터·공유 메모리 전달 방식을 안다.
- framework의 `android.os.Binder`와 native `libbinder`(sp/BBinder/BpBinder/IPCThreadState)의 클래스 계층을 연결한다.
- vendor 데몬이 왜 `libbinder_ndk`(ndk 백엔드)를 쓰는지 이해하고 CH23의 실전 코드로 이어질 준비를 한다.
:::

Binder는 안드로이드 IPC의 심장이다. 앱이 `getSystemService()`로 받아 쓰는 거의 모든 시스템 서비스, `Intent`로 액티비티를 띄우는 동작, vendor 데몬이 앱에 데이터를 넘기는 경로가 전부 Binder 위에서 돈다. [CH9 서비스 아키텍처](/study/android-internals/09-service-architecture)에서 servicemanager와 세 개의 binder 도메인을 봤다면, 이 장은 그 위에서 개발자가 실제로 코드를 짜는 유저스페이스 층을 다룬다. 커널 드라이버 자체는 [CH22](/study/android-internals/22-binder-kernel)의 몫이다.

## Binder 프로그래밍 모델

Binder의 핵심 발상은 <strong>원격 객체를 마치 로컬 객체처럼 호출</strong>하는 것이다. 클라이언트는 인터페이스 참조 하나를 들고 메서드를 부르지만, 그 실체는 다른 프로세스 안에 있다. 이 환상을 만드는 두 축이 프록시(proxy)와 스텁(stub)이다.

<strong>프록시</strong>는 클라이언트 쪽 대역이다. 클라이언트가 `service.getFrame(id)`를 부르면, 프록시는 인자를 Parcel에 직렬화해서 커널에 `transact()`를 던지고 응답을 기다린다. 프록시는 진짜 로직을 하나도 갖고 있지 않다 — 오직 "포장해서 보내고 풀어서 돌려주는" 마샬링만 한다.

<strong>스텁</strong>은 서버 쪽 대역이다. 커널이 전달한 Parcel을 받아 어떤 메서드가 호출됐는지 코드(transaction code)로 판별하고, 인자를 역직렬화한 뒤 개발자가 구현한 실제 메서드를 호출한다. 반환값은 다시 Parcel에 담아 클라이언트로 돌려보낸다.

<strong>인터페이스 토큰(interface descriptor)</strong>은 이 통신의 신원 확인 장치다. 모든 transaction의 첫 부분에 `"android.os.ICanAccessService"` 같은 인터페이스 이름 문자열이 실린다. 스텁은 받은 토큰이 자기 인터페이스와 일치하는지 먼저 검사하고, 어긋나면 거부한다. 엉뚱한 프로세스가 우연히 같은 핸들로 아무 Parcel이나 던져 넣는 것을 막는다.

호출 방식은 두 가지다.

- <strong>동기(synchronous) 호출</strong>이 기본이다. 클라이언트 스레드는 `transact()`를 부른 뒤 서버가 응답을 돌려줄 때까지 블록된다. 반환값이나 `out` 파라미터를 받아야 하는 메서드는 반드시 동기다.
- <strong>oneway 호출</strong>은 "던지고 잊는(fire-and-forget)" 방식이다. 클라이언트는 커널에 transaction을 넘기는 즉시 반환된다. 서버의 처리 완료를 기다리지 않으므로 반환값을 받을 수 없고, 콜백·이벤트 통지처럼 응답이 불필요한 경우에 쓴다. 단 같은 Binder 객체로 보낸 oneway 호출들은 <strong>도착 순서가 보장</strong>된다는 점이 중요하다.

::: warning oneway의 함정
oneway라고 무조건 빠르거나 안전한 게 아니다. oneway transaction은 별도의 작은 비동기 버퍼 공간(전체 트랜잭션 버퍼의 절반)을 공유하므로, 대용량 데이터를 oneway로 연달아 쏘면 버퍼가 고갈돼 이후 호출이 실패한다. 콜백 스트림에는 맞지만 대용량 전송에는 부적합하다.
:::

## AIDL 심층

프록시와 스텁을 손으로 짜는 것은 지옥이다. 그래서 안드로이드는 <strong>AIDL(Android Interface Definition Language)</strong>로 인터페이스만 선언하면 컴파일러가 양쪽 대역 코드를 생성해준다.

### 문법

AIDL 파일은 자바 인터페이스와 비슷하게 생겼지만 IPC 전용 문법이 얹혀 있다.

```java
// ICanAccessService.aidl
package com.agmo.agcand;

import com.agmo.agcand.CanFrame;

interface ICanAccessService {
    // 동기 호출 — 반환값이 있으므로 oneway 불가
    CanFrame getLatestFrame(int pgn);

    // in/out/inout 방향 지정 (원시 타입은 항상 in, 지정 불필요)
    void readBlock(in int[] pgns, out CanFrame[] frames);

    // oneway 콜백 등록
    oneway void subscribe(ICanCallback cb);
}
```

핵심 문법 요소는 다음과 같다.

- <strong>parcelable</strong>: 원시 타입(int, long, String, boolean 등)을 넘어 사용자 정의 구조체를 전달하려면 `parcelable`로 선언해야 한다. 이 타입이 Parcel로 직렬화 가능함을 컴파일러에 알린다.
- <strong>방향 지정자 in/out/inout</strong>: 비원시 타입 인자에는 데이터가 어느 방향으로 흐르는지 반드시 명시한다. `in`은 클라이언트→서버, `out`은 서버가 채워 돌려주는 값, `inout`은 양방향이다. 방향이 잘못되면 불필요한 복사가 일어나거나 값이 전달되지 않는다.
- <strong>oneway</strong>: 인터페이스 전체 또는 개별 메서드에 붙일 수 있다. 인터페이스에 붙이면 모든 메서드가 oneway가 된다.
- <strong>interface 상속</strong>: 콜백 인터페이스(`ICanCallback`)를 인자로 넘겨 서버가 클라이언트를 역호출하는 양방향 통신도 가능하다.

### AIDL 컴파일러가 생성하는 코드

`aidl` 컴파일러는 하나의 `.aidl`을 받아 선택한 백엔드에 맞는 프록시/스텁 쌍을 뽑아낸다.

![ICanAccessService.aidl 하나가 aidl 컴파일러를 거쳐 java(Stub/Proxy)·cpp(Bn/Bp+libbinder)·ndk(BnCanAccessService+libbinder_ndk)·rust(trait) 네 백엔드 코드로 생성되는 구조](/images/study-android-internals/21-aidl-codegen-light.png)
![ICanAccessService.aidl 하나가 aidl 컴파일러를 거쳐 java(Stub/Proxy)·cpp(Bn/Bp+libbinder)·ndk(BnCanAccessService+libbinder_ndk)·rust(trait) 네 백엔드 코드로 생성되는 구조](/images/study-android-internals/21-aidl-codegen-dark.png)

- <strong>Java 백엔드</strong>는 `ICanAccessService.java` 안에 `Stub`(abstract, 서버가 상속)과 `Stub.Proxy`(클라이언트가 받는 프록시)를 중첩 클래스로 만든다. `Stub.asInterface(binder)`로 IBinder를 인터페이스로 캐스팅하고, `onTransact(code, data, reply, flags)`가 스텁 디스패치의 진입점이다.
- <strong>C++ 백엔드</strong>는 `BnCanAccessService`(서버가 상속, Bn = Binder native)와 `BpCanAccessService`(클라이언트 프록시, Bp = Binder proxy)를 생성하고 `libbinder`에 링크한다.
- <strong>NDK 백엔드</strong>도 `BnCanAccessService`/`BpCanAccessService`를 만들지만 `libbinder_ndk`의 안정 C API 위에서 동작한다. vendor 데몬이 쓰는 것이 바로 이 백엔드다.
- <strong>Rust 백엔드</strong>는 `trait ICanAccessService`와 binder crate 바인딩을 생성한다.

한 번 선언하면 네 언어의 대역 코드가 자동으로 맞춰 나오므로, 서버는 C++로 짜고 클라이언트는 Java로 짜는 혼합 구성이 자연스럽게 가능하다. agcand도 정확히 이 구조다 — 데몬은 C++(ndk), 앱은 Java.

### stable AIDL과 버저닝

일반 AIDL은 빌드할 때마다 새로 생성되므로 인터페이스를 마음대로 바꿔도 된다. 하지만 vendor 파티션의 데몬과 system 파티션의 앱은 <strong>서로 다른 시점에 빌드·업데이트</strong>되므로, 인터페이스가 조용히 바뀌면 ABI가 깨진다. 이 문제를 막는 것이 <strong>stable AIDL</strong>이다.

- `aidl_interface` Soong 모듈로 선언하면 인터페이스가 API 표면으로 관리된다.
- `.aidl_api/` 디렉토리에 각 버전의 스냅샷이 `.hash` 파일과 함께 <strong>frozen</strong>(동결)된다. `m <module>-freeze-api`로 현재 정의를 새 버전으로 굳힌다.
- `--version`으로 명시된 버전 번호가 wire에 실려, 클라이언트와 서버가 서로 다른 버전을 알아도 공통 범위 안에서 안전하게 통신한다.

핵심 규칙은 하나다 — <strong>기존 메서드는 변경·삭제 금지, 새 메서드는 추가만 허용</strong>. 이유는 이미 배포된 클라이언트 때문이다. 앱과 vendor 데몬은 서로 다른 시점에 업데이트되므로, 구버전 클라이언트가 신버전 서버에 붙거나 그 반대 상황이 상시 발생한다. 이때 메서드의 시그니처가 바뀌거나 순서가 흔들리면 <strong>transaction code가 어긋나</strong> 엉뚱한 메서드가 호출된다. 그래서 규칙은 이렇게 강제된다.

- 메서드는 인터페이스 <strong>끝에만 추가</strong>할 수 있다. transaction code는 선언 순서로 번호가 매겨지므로, 중간에 끼워 넣으면 이후 모든 코드가 밀려 기존 클라이언트가 깨진다.
- 동결된 버전의 스냅샷은 <strong>수정 불가</strong>다. 기존 메서드의 시그니처를 바꾸거나 삭제·재배치하려 하면 `.hash` 불일치로 빌드가 실패한다. 즉 호환성 위반을 사람이 아니라 <strong>빌드 시스템이 기계적으로 차단</strong>한다.
- 필드를 추가하는 parcelable도 마찬가지로 <strong>끝에만</strong> 추가하고, 구버전이 모르는 필드는 기본값으로 안전하게 채워진다.

::: tip 백엔드 선택 기준
- <strong>Java</strong>: 앱·framework 코드.
- <strong>NDK</strong>: vendor 코드 또는 APEX 안의 네이티브 코드. `libbinder_ndk`의 ABI가 안정적이라 플랫폼 업데이트와 독립적으로 빌드된다. **vendor 데몬은 이걸 쓴다.**
- <strong>CPP</strong>: system 파티션의 네이티브 코드. `libbinder`에 직접 링크하므로 vendor에서는 쓰지 않는다(ABI 불안정).
- <strong>Rust</strong>: 새로 작성하는 플랫폼 네이티브 컴포넌트.
:::

## Parcel — 직렬화 포맷

Parcel은 Binder transaction에 실리는 바이트 컨테이너다. 이름은 "소포"지만 범용 직렬화 포맷이 아니라 <strong>같은 기기의 프로세스 간 전송에 특화</strong>된 형식이다. 디스크에 저장하거나 네트워크로 보내는 용도가 아니다 — 버전 간 호환을 보장하지 않기 때문이다.

<strong>wire format</strong>의 특징은 다음과 같다.

- 데이터는 <strong>4바이트 정렬</strong>로 채워진다. `writeInt()`, `writeString()` 등이 순서대로 버퍼에 append되고, 읽는 쪽은 정확히 같은 순서로 `readInt()`, `readString()`을 불러야 한다. 순서가 어긋나면 조용히 쓰레기 값을 읽는다.
- Parcel 안에 다른 Binder 객체나 파일 디스크립터가 섞이면, 그 위치를 가리키는 <strong>객체 오프셋 배열</strong>이 별도로 유지된다. 커널은 이 오프셋을 보고 "여기는 단순 데이터가 아니라 변환이 필요한 특수 객체"임을 안다(자세한 flat_binder_object 처리는 [CH22](/study/android-internals/22-binder-kernel)에서 다룬다).

<strong>파일 디스크립터 전달</strong>은 Parcel의 강력한 기능이다. `writeFileDescriptor()`로 fd를 넣으면 커널이 수신 프로세스에 <strong>새 fd를 복제</strong>해준다. 정수 값을 그대로 넘기는 게 아니라 커널의 fd 테이블 차원에서 진짜 파일 참조가 전달되므로, 소켓·파이프·메모리 파일을 프로세스 경계 너머로 공유할 수 있다.

이 위에서 <strong>공유 메모리(ashmem)</strong> 전달이 성립한다. Binder transaction 버퍼는 1MB 남짓으로 제한되므로(→ CH22), 비트맵이나 대용량 버퍼는 Parcel에 직접 담지 않는다. 대신 ashmem 영역을 만들어 그 fd만 Parcel로 넘기고, 수신 측이 같은 물리 메모리를 `mmap`한다. 큰 데이터는 "복사"가 아니라 "공유"로 처리하는 표준 패턴이다.

## Framework 관점

자바 층에서 Binder는 두 클래스로 드러난다.

- <strong>`android.os.Binder`</strong>는 서버가 상속하는 로컬 Binder 객체다. AIDL의 `Stub`이 이걸 상속한다. `onTransact()`를 오버라이드해 transaction을 디스패치한다.
- <strong>`android.os.BinderProxy`</strong>는 원격 객체의 핸들을 감싼 프록시다. 클라이언트가 서비스를 받으면 실제로는 BinderProxy 인스턴스를 쥐고, `transact()`가 JNI를 타고 native로 내려간다.

이 자바 객체와 native `libbinder` 사이를 잇는 것이 <strong>JNI 레이어</strong>인 `frameworks/base/core/jni/android_util_Binder.cpp`다. 자바 `Binder.transact()`가 여기서 native `IBinder::transact()`로, 자바 Parcel이 native Parcel로 변환된다. 자바 오브젝트와 native `BpBinder`의 수명을 연결하는 접착제가 이 파일에 모여 있다.

### Binder 보안 프리미티브 — 호출자 신원

Binder가 IPC를 넘어 <strong>보안 경계</strong>로 쓰이는 근거가 여기 있다. 서버는 트랜잭션을 처리하는 동안 호출자가 누구인지를 커널이 보증한 값으로 알 수 있다.

```java
// 서버(Stub) 안 — onTransact가 도는 Binder 스레드에서만 유효
int callingUid = Binder.getCallingUid();
int callingPid = Binder.getCallingPid();
if (callingUid != EXPECTED_UID) {
    throw new SecurityException("허가되지 않은 호출자");
}
```

- <strong>`Binder.getCallingUid()` / `getCallingPid()`</strong>는 지금 트랜잭션을 보낸 프로세스의 UID/PID를 돌려준다. 이 값은 클라이언트가 Parcel에 실어 보낸 게 아니라 <strong>커널 드라이버가 송신 프로세스의 자격에서 직접 채운 것</strong>이다([CH22](/study/android-internals/22-binder-kernel)의 트랜잭션 처리에서 커널이 이를 기입한다). 그래서 클라이언트가 위조할 수 없고, 서버의 <strong>권한 판정(permission check)</strong>이 이 값을 신뢰할 수 있다. `checkPermission`·`enforcePermission`도 결국 이 caller 신원 위에서 동작한다.
- 이 값은 <strong>Binder 스레드가 트랜잭션을 처리하는 동안에만</strong> 유효하다. onTransact 밖(예: 별도 워커 스레드)에서 부르면 자기 프로세스의 UID가 나와 무의미하다.

<strong>`clearCallingIdentity()` / `restoreCallingIdentity()`</strong>는 이 신원을 일시적으로 벗는 패턴이다. 서버가 호출자를 대신해 <strong>또 다른 서비스를 호출</strong>할 때, 호출자의 제한된 신원이 아니라 서버 자신의 신원으로 동작해야 하는 경우에 쓴다.

```java
long token = Binder.clearCallingIdentity();  // 이후 caller 신원 = 내 프로세스
try {
    // 이 블록 안에서 하는 후속 Binder 호출은 '서버'의 신원으로 나간다
    otherService.doPrivilegedThing();
} finally {
    Binder.restoreCallingIdentity(token);     // 반드시 복원
}
```

`clearCallingIdentity()`를 부르면 이후 `getCallingUid()`가 서버 자신의 UID를 반환하고, 반환된 토큰을 `restoreCallingIdentity()`에 넘겨 원래 신원을 되돌린다. 복원을 빠뜨리면 이후 권한 판정이 서버 신원으로 잘못 이뤄지므로 반드시 `finally`로 감싼다. native 층에서는 `IPCThreadState::self()->getCallingUid()`와 `clearCallingIdentity()`가 같은 역할을 한다.

### 사망 통지로 리소스를 회수한다

<strong>사망 통지(death notification)</strong>는 상대 프로세스가 죽었을 때 반대편이 아는 메커니즘인데, 단순 "재연결 트리거"를 넘어 <strong>분산 리소스 회수의 핵심 도구</strong>다.

```java
IBinder binder = /* 원격 서비스 */;
binder.linkToDeath(new IBinder.DeathRecipient() {
    @Override public void binderDied() {
        // 상대가 죽었다 — 붙어 있던 콜백·세션·구독을 정리
    }
}, 0);
```

`linkToDeath()`로 DeathRecipient를 등록하면, 대상 프로세스가 종료될 때 커널이 통지를 보내고 `binderDied()`가 호출된다. 방향에 따라 두 가지 쓰임이 있다.

- <strong>클라이언트가 서버에 등록</strong>: vendor 데몬이 크래시하면 앱이 감지해 재구독한다.
- <strong>서버가 클라이언트(콜백)에 등록</strong>: 이쪽이 리소스 관리의 요체다. 서버가 `subscribe(callback)`으로 클라이언트 콜백을 들고 있을 때, 그 <strong>구독자 프로세스가 죽으면</strong> 커널이 서버에 통지하고, 서버는 죽은 콜백을 <strong>구독 목록에서 자동으로 제거</strong>한다. 이게 없으면 서버는 이미 죽은 클라이언트에 계속 oneway 통지를 쏘다가 콜백 리스트가 좀비 참조로 새고, 트랜잭션 실패가 누적된다. 즉 linkToDeath는 <strong>"연결이 끊기면 그에 매달린 세션·콜백·락을 자동 반납한다"</strong>는 리소스 수명 관리 패턴의 실현이다. CH23의 agcand가 정확히 이 방식으로 구독자를 관리한다.

## Native 관점 — libbinder

C++ 층의 `libbinder`가 Binder의 원형이다. 자바 API는 이 위에 얹힌 얇은 껍질에 가깝다.

![libbinder 클래스 관계 — 서버 측 IInterface·BnInterface·BBinder·IPCThreadState/ProcessState와 클라이언트 측 IInterface·BpInterface·BpBinder가 커널 binder 드라이버를 사이에 두고 transact/reply로 통신하며 양쪽 모두 sp/wp·RefBase로 참조 관리하는 구조](/images/study-android-internals/21-libbinder-classes-light.png)
![libbinder 클래스 관계 — 서버 측 IInterface·BnInterface·BBinder·IPCThreadState/ProcessState와 클라이언트 측 IInterface·BpInterface·BpBinder가 커널 binder 드라이버를 사이에 두고 transact/reply로 통신하며 양쪽 모두 sp/wp·RefBase로 참조 관리하는 구조](/images/study-android-internals/21-libbinder-classes-dark.png)

### 스마트 포인터 — RefBase / sp / wp

libbinder의 모든 객체는 `RefBase`를 상속해 <strong>침입적 참조 카운팅</strong>을 한다. 원시 포인터 대신 `sp<T>`(strong pointer)와 `wp<T>`(weak pointer)로 다룬다. `sp`는 강한 참조로 카운트가 0이 되면 객체가 해제되고, `wp`는 순환 참조를 끊는 약한 참조다. Binder 객체는 여러 프로세스에 걸쳐 참조되므로 수동 delete가 사실상 불가능하고, 이 스마트 포인터 규율이 libbinder 코드 전체를 관통한다.

### IBinder / BBinder / BpBinder

- <strong>`IBinder`</strong>는 로컬이든 원격이든 모든 Binder 객체의 공통 인터페이스다. `transact()`가 핵심 메서드다.
- <strong>`BBinder`</strong>(Binder-Binder)는 서버 측 로컬 객체다. `onTransact()`를 오버라이드해 수신 처리를 한다.
- <strong>`BpBinder`</strong>(Binder-proxy)는 클라이언트 측 원격 핸들이다. 내부에 커널이 부여한 <strong>handle 정수</strong>를 들고 있고, `transact()`가 이 핸들 앞으로 커널에 명령을 던진다.

### IInterface / BnInterface / BpInterface

AIDL이 생성하는 것이 바로 이 계층이다.

- <strong>`IInterface`</strong>는 인터페이스 계약이다. `DECLARE_META_INTERFACE`/`IMPLEMENT_META_INTERFACE` 매크로가 인터페이스 디스크립터와 `asInterface()`/`getInterfaceDescriptor()`를 만들어준다.
- <strong>`BnInterface<ICanAccessService>`</strong>은 BBinder + IInterface를 결합한 서버 스텁이다. 개발자는 이걸 상속해 실제 메서드를 구현한다.
- <strong>`BpInterface<ICanAccessService>`</strong>은 BpBinder를 감싼 클라이언트 프록시다. 각 메서드가 인자를 Parcel로 포장해 `remote()->transact()`를 부른다.

### ProcessState와 IPCThreadState

이 둘이 프로세스와 커널 드라이버를 잇는 런타임이다.

- <strong>`ProcessState`</strong>는 프로세스당 하나(싱글턴)다. `/dev/binder`를 `open`하고 `mmap`으로 수신 버퍼를 매핑하며, Binder 스레드풀의 크기(기본 최대 15+1)를 관리한다. `ProcessState::self()->setThreadPoolMaxThreadCount(n)`으로 조정한다.
- <strong>`IPCThreadState`</strong>는 스레드당 하나다. 실제 `ioctl(BINDER_WRITE_READ)`를 돌리는 transact 루프가 여기 있다. `talkWithDriver()`가 커널과 명령을 주고받는 심장이다.
- <strong>`joinThreadPool()`</strong>은 현재 스레드를 Binder 수신 루프에 합류시킨다. 서버의 메인 스레드는 초기화를 마친 뒤 이걸 호출해 무한 수신 상태로 들어간다.

## NDK — libbinder_ndk

`libbinder`의 C++ ABI는 플랫폼 릴리스마다 바뀔 수 있어 vendor 코드가 직접 링크하기엔 위험하다. 이 문제를 풀려고 나온 것이 <strong>`libbinder_ndk`</strong>(도입: Android 10)다. 안정된 C API(`AIBinder`, `AStatus`, `AParcel`, `ABinderProcess_*`, `AServiceManager_*`)를 제공해, [Treble](/study/android-internals/16-selinux-avb) 이후 vendor/system 분리 정책과 맞물려 vendor가 안전하게 Binder를 쓸 수 있게 한다.

- `AIBinder`가 IBinder를, `AStatus`가 예외/상태를, `AParcel`이 Parcel을 대신한다.
- `ABinderProcess_startThreadPool()` / `ABinderProcess_joinThreadPool()`이 스레드풀을 관리한다.
- `AServiceManager_addService()` / `AServiceManager_getService()`로 서비스를 등록·조회한다.
- AIDL의 <strong>ndk 백엔드</strong>가 정확히 이 API 위에서 `BnCanAccessService`/`BpCanAccessService`를 생성한다. 즉 "ndk 백엔드 AIDL + libbinder_ndk"가 vendor 데몬의 표준 조합이다.

## 간단 예제

전체 통합은 [CH23](/study/android-internals/23-native-daemon-case-study)에서 파일 배치·빌드·sepolicy까지 함께 다루고, 여기서는 ndk 백엔드로 서비스를 등록·조회하는 최소 골격만 본다.

::: details ndk 백엔드 최소 서버 골격
```cpp
#include <android/binder_manager.h>
#include <android/binder_process.h>
#include "aidl/com/agmo/agcand/BnCanAccessService.h"

using aidl::com::agmo::agcand::BnCanAccessService;
using aidl::com::agmo::agcand::CanFrame;

class CanAccessService : public BnCanAccessService {
public:
    ::ndk::ScopedAStatus getLatestFrame(int32_t pgn, CanFrame* out) override {
        // 캐시에서 최신 프레임을 채워 반환
        *out = latestFor(pgn);
        return ::ndk::ScopedAStatus::ok();
    }
};

int main() {
    ABinderProcess_setThreadPoolMaxThreadCount(4);
    auto svc = ::ndk::SharedRefBase::make<CanAccessService>();
    const std::string name = std::string(CanAccessService::descriptor) + "/default";
    binder_status_t st = AServiceManager_addService(
        svc->asBinder().get(), name.c_str());
    if (st != STATUS_OK) return 1;

    ABinderProcess_joinThreadPool();  // 수신 루프 진입 — 여기서 블록
    return 0;
}
```
:::

::: details ndk 백엔드 최소 클라이언트 골격
```cpp
#include <android/binder_manager.h>
#include "aidl/com/agmo/agcand/ICanAccessService.h"

using aidl::com::agmo::agcand::ICanAccessService;
using aidl::com::agmo::agcand::CanFrame;

auto binder = ::ndk::SpAIBinder(
    AServiceManager_waitForService("com.agmo.agcand.ICanAccessService/default"));
auto svc = ICanAccessService::fromBinder(binder);

CanFrame frame;
if (svc->getLatestFrame(0xFEE5, &frame).isOk()) {
    // frame 사용
}
```
:::

`addService`로 등록하고 `joinThreadPool`로 수신을 도는 이 골격이 vendor 데몬의 뼈대다. 자바 앱 클라이언트는 같은 AIDL의 java 백엔드로 `ICanAccessService.Stub.asInterface(ServiceManager.getService(...))`를 써서 붙는다.

::: tip 핵심 정리
- Binder는 프록시(클라이언트 마샬링)와 스텁(서버 디스패치)으로 원격 객체를 로컬처럼 호출하게 하고, 인터페이스 토큰으로 신원을 확인하며 동기/oneway 두 호출 방식을 제공한다.
- AIDL은 인터페이스만 선언하면 java/cpp/ndk/rust 백엔드별 프록시·스텁을 생성하고, stable AIDL(aidl_interface + freeze)로 vendor/system 간 ABI를 버저닝한다.
- Parcel은 같은 기기 프로세스 간 전용 직렬화 포맷으로, 4바이트 정렬·객체 오프셋·fd 복제·ashmem 공유를 지원한다.
- framework의 Binder/BinderProxy는 JNI(android_util_Binder)를 거쳐 native libbinder의 BBinder/BpBinder로 내려가고, ProcessState(mmap·스레드풀)와 IPCThreadState(transact 루프)가 커널과 잇는다.
- vendor 데몬은 ABI가 안정된 libbinder_ndk + ndk 백엔드 AIDL 조합을 쓴다 — CH23의 agcand이 이 조합의 실전 사례다.
:::

## 다음 챕터

[CH22. Binder — 커널과 드라이버](/study/android-internals/22-binder-kernel)에서는 유저스페이스 아래의 `/dev/binder` 드라이버로 내려가, ioctl `BINDER_WRITE_READ` 프로토콜과 one-copy 트랜잭션, flat_binder_object의 핸들 변환, binder_proc/node/ref 자료구조, 그리고 debugfs·perfetto로 Binder를 추적·디버깅하는 법을 다룬다.
