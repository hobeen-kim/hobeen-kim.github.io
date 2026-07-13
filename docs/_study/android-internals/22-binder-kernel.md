---
title: "CH22. Binder — 커널과 드라이버"
description: "/dev/binder 캐릭터 디바이스와 BinderFS, ioctl BINDER_WRITE_READ 프로토콜, one-copy 트랜잭션의 원리, flat_binder_object의 핸들 변환, binder_proc/node/ref 자료구조, 그리고 debugfs·perfetto로 Binder를 추적·디버깅하는 커널 층을 해부한다."
date: 2026-07-13
tags: [android, aosp, binder, kernel, driver, ioctl]
---

# CH22. Binder — 커널과 드라이버

::: info 학습 목표
- `/dev/binder`·`hwbinder`·`vndbinder` 캐릭터 디바이스와 BinderFS로의 전환을 이해한다.
- ioctl `BINDER_WRITE_READ` 중심의 BC_/BR_ 명령 프로토콜을 파악한다.
- one-copy 트랜잭션이 가능한 이유와 1MB 버퍼 한계·TransactionTooLargeException의 원인을 안다.
- flat_binder_object의 핸들↔포인터 변환으로 커널이 신원을 보증하는 메커니즘을 이해한다.
- binder_proc/node/ref/thread 자료구조와 debugfs·perfetto 기반 디버깅 방법을 익힌다.
:::

[CH21](/study/android-internals/21-binder-userspace)의 프록시·스텁·Parcel은 결국 `ioctl()` 한 번으로 커널에 도달한다. 이 장은 그 아래, `drivers/android/binder.c`의 세계다. Binder가 안드로이드에서 "빠른 IPC"로 통하는 이유, 1MB 제한이 왜 생기는지, `service call`로 뭔가를 찌를 때 커널 안에서 무슨 일이 벌어지는지가 여기서 드러난다. CH23에서 데몬이 안 뜰 때 이 층의 지식이 진단의 바탕이 된다.

## Binder 캐릭터 디바이스

Binder 드라이버는 캐릭터 디바이스로 노출된다. [CH9](/study/android-internals/09-service-architecture)에서 봤듯 도메인이 셋으로 갈린다.

- <strong>`/dev/binder`</strong>: framework binder. 앱·system_server·servicemanager가 쓴다.
- <strong>`/dev/hwbinder`</strong>: HAL 통신용. HIDL/AIDL HAL 서버와 클라이언트가 쓴다.
- <strong>`/dev/vndbinder`</strong>: vendor 프로세스 간 통신. vendor 데몬은 이 도메인을 쓰고 `vndservicemanager`에 등록한다.

세 디바이스는 커널 안에서 <strong>독립된 드라이버 인스턴스</strong>다. 컨텍스트가 분리돼 서로 통신하지 못하는 것이 Treble의 격리 원칙이다. agcand이 vndbinder에 등록되면 앱은 vndbinder를 통해서만 붙는다.

<strong>BinderFS로의 전환</strong>이 최근의 큰 변화다. 예전에는 이 디바이스 노드가 커널 설정에 하드코딩됐지만, Android 11부터 `binderfs`라는 전용 파일시스템으로 관리된다.

```
# /dev/binderfs 마운트 예
$ mount | grep binder
binder on /dev/binderfs type binder (rw,relatime)
$ ls /dev/binderfs
binder  binder-control  hwbinder  vndbinder
```

`binder-control`에 ioctl로 새 인스턴스를 동적으로 만들 수 있어, 컨테이너나 가상화 환경에서 여러 Binder 컨텍스트를 격리해 띄우는 것이 가능해졌다. 마이크로드로이드(APEX 안의 격리 VM) 같은 구조가 이 위에서 성립한다.

## ioctl 인터페이스

Binder와의 모든 대화는 `ioctl()`로 이뤄진다. `read()`/`write()`가 아니라 ioctl인 이유는, 한 번의 시스템 콜에 "쓸 명령"과 "읽을 응답"을 함께 실어 왕복 횟수를 줄이기 위해서다. 중심 명령이 <strong>`BINDER_WRITE_READ`</strong>다.

```c
struct binder_write_read {
    binder_size_t write_size;      // 커널로 보낼 명령 버퍼 크기
    binder_size_t write_consumed;  // 커널이 소비한 양
    binder_uintptr_t write_buffer; // BC_* 명령들이 담긴 유저 버퍼
    binder_size_t read_size;       // 커널에서 받을 응답 버퍼 크기
    binder_size_t read_consumed;
    binder_uintptr_t read_buffer;  // BR_* 응답들이 담길 유저 버퍼
};
```

`write_buffer`에는 클라이언트가 커널에 지시하는 <strong>BC_(Binder Command)</strong>들이, `read_buffer`에는 커널이 프로세스에 통지하는 <strong>BR_(Binder Return)</strong>들이 담긴다. 대표적인 명령은 다음과 같다.

| 방향 | 명령 | 의미 |
|------|------|------|
| BC_ | `BC_TRANSACTION` | 트랜잭션을 대상에 전송 |
| BC_ | `BC_REPLY` | 수신한 트랜잭션에 응답 |
| BC_ | `BC_FREE_BUFFER` | 처리 끝난 수신 버퍼 반납 |
| BC_ | `BC_ENTER_LOOPER` / `BC_REGISTER_LOOPER` | 스레드를 수신 루프에 등록 |
| BR_ | `BR_TRANSACTION` | 처리할 트랜잭션 도착 |
| BR_ | `BR_REPLY` | 응답 도착 |
| BR_ | `BR_TRANSACTION_COMPLETE` | 전송 완료 통지 |
| BR_ | `BR_SPAWN_LOOPER` | 스레드풀을 늘리라는 지시 |
| BR_ | `BR_DEAD_BINDER` | 대상 프로세스 사망 통지 |

[CH21](/study/android-internals/21-binder-userspace)의 `IPCThreadState::talkWithDriver()`가 이 구조체를 채워 ioctl을 돌리는 루프다. 개발자는 이 프로토콜을 직접 만질 일이 거의 없지만, perfetto 트레이스나 커널 로그에 이 명령 이름들이 그대로 찍히므로 읽을 줄 알아야 한다.

## 트랜잭션 처리 — one-copy의 비밀

Binder가 소켓·파이프보다 빠르다고 하는 근거가 바로 <strong>one-copy</strong>다. 일반적인 IPC는 데이터가 "송신 프로세스 → 커널 버퍼 → 수신 프로세스"로 두 번 복사(two-copy)되지만, Binder는 한 번만 복사한다.

![Binder 트랜잭션 커널 경로 — 송신 프로세스 A의 Parcel이 BINDER_WRITE_READ ioctl로 드라이버에 들어와 대상 노드 조회 후 수신자 mmap 버퍼로 1회 copy_from_user되고 대상 스레드 todo 큐에 큐잉되며, 수신 프로세스 B는 읽기 전용 매핑으로 포인터만 받아 처리하는 one-copy 구조](/images/study-android-internals/22-transaction-flow-light.png)
![Binder 트랜잭션 커널 경로 — 송신 프로세스 A의 Parcel이 BINDER_WRITE_READ ioctl로 드라이버에 들어와 대상 노드 조회 후 수신자 mmap 버퍼로 1회 copy_from_user되고 대상 스레드 todo 큐에 큐잉되며, 수신 프로세스 B는 읽기 전용 매핑으로 포인터만 받아 처리하는 one-copy 구조](/images/study-android-internals/22-transaction-flow-dark.png)

비결은 <strong>수신 버퍼의 mmap</strong>이다. 모든 Binder 프로세스는 초기화 때 `ProcessState`가 `/dev/binder`를 `mmap`한다. 이 매핑은 커널 주소 공간과 수신 프로세스의 주소 공간에 <strong>동시에 걸쳐 있다</strong>. 트랜잭션이 오면 커널은 다음을 한다.

1. `BC_TRANSACTION`을 받아 대상 handle로 <strong>binder_node를 조회</strong>한다.
2. 송신자 유저 버퍼(Parcel)를 <strong>수신자의 mmap 버퍼로 딱 한 번 `copy_from_user`</strong>한다. 이 버퍼는 이미 수신 프로세스에도 매핑돼 있으므로, 수신자는 추가 복사 없이 그 주소를 그대로 읽는다.
3. 대상 스레드의 <strong>todo 큐에 트랜잭션을 큐잉</strong>하고 깨운다.

수신 프로세스는 자기 매핑 안의 포인터만 넘겨받아 읽는다. "커널→수신자" 복사가 사라지므로 one-copy다.

<strong>1MB 버퍼 한계</strong>가 여기서 나온다. 이 mmap 수신 버퍼의 크기가 프로세스당 약 1MB(정확히는 1MB - 8KB, 두 페이지 예약)로 고정돼 있다. 한 트랜잭션이 이 공간을 넘으면 커널이 `-ENOMEM`을 돌려주고, 자바 층에서 이것이 <strong>`TransactionTooLargeException`</strong>으로 표면화된다.

::: warning TransactionTooLargeException의 실제 원인
"내 데이터는 1MB보다 작은데 왜 터지지?"의 답은 <strong>버퍼가 프로세스 단위로 공유</strong>되기 때문이다. 그 순간 진행 중인 모든 트랜잭션이 이 1MB를 나눠 쓴다. 큰 Bitmap 하나, 수천 개 항목의 리스트, 혹은 동시 다발 호출이 겹치면 개별 크기가 작아도 합이 한계를 넘어 터진다. 해법은 데이터를 잘라 보내거나(paging), 대용량은 [CH21](/study/android-internals/21-binder-userspace)의 ashmem fd로 넘기는 것이다.
:::

## Flattened object — 핸들과 포인터의 변환

Parcel 안에 Binder 객체나 fd가 섞이면 단순 바이트 복사로는 안 된다. 송신자의 포인터·fd 번호는 수신자 프로세스에서 아무 의미가 없기 때문이다. 이 특수 항목을 표현하는 것이 <strong>`flat_binder_object`</strong>다.

```c
struct flat_binder_object {
    __u32 hdr;      // 타입: BINDER, HANDLE, FD ...
    __u32 flags;
    union {
        binder_uintptr_t binder;  // 로컬 객체일 때: 유저 포인터
        __u32 handle;             // 원격 객체일 때: 핸들 정수
    };
    binder_uintptr_t cookie;
};
```

커널은 Parcel의 객체 오프셋 배열을 따라가며 각 flat_binder_object를 <strong>변환</strong>한다. 이것이 Binder 보안의 핵심이다.

- 송신자가 <strong>로컬 객체(BBinder)</strong>를 보내면(`BINDER_TYPE_BINDER`), 커널은 그에 대응하는 `binder_node`를 만들거나 찾고, 수신자에게는 그 노드를 가리키는 <strong>handle 정수</strong>로 바꿔 전달한다.
- 송신자가 이미 <strong>원격 핸들(BpBinder)</strong>을 보내면(`BINDER_TYPE_HANDLE`), 커널은 그 핸들이 가리키는 실제 노드를 찾아 수신자 관점의 새 핸들로 재매핑한다.

핵심은 <strong>유저스페이스가 절대 노드 포인터를 직접 다루지 못한다</strong>는 것이다. 커널만 `binder_node`의 실주소를 알고, 유저는 불투명한 handle 정수만 쥔다. 그래서 프로세스가 handle을 위조해도 커널이 매핑 테이블로 검증하므로 남의 서비스를 사칭할 수 없다. <strong>신원 보증(identity guarantee)</strong>이 커널 차원에서 성립하는 이유다.

<strong>fd 전달</strong>(`BINDER_TYPE_FD`)도 같은 원리다. 커널이 송신자 fd 테이블에서 파일을 찾아 수신자 fd 테이블에 새 항목을 설치하고, 그 새 fd 번호를 Parcel에 써 넣는다. 정수를 복사하는 게 아니라 커널이 진짜 파일 참조를 이식한다.

## 드라이버 내부 상태

드라이버는 프로세스·스레드·객체·참조를 각각의 구조체로 추적한다.

![Binder 드라이버 자료구조 — 서버 binder_proc가 binder_node(서비스 실체)와 binder_thread 스레드풀을 소유하고, 클라이언트 binder_proc는 그 node를 가리키는 binder_ref와 handle 정수 매핑을 갖되 node 포인터는 커널만 보유해 ref→node로 신원을 보증하는 구조](/images/study-android-internals/22-driver-structs-light.png)
![Binder 드라이버 자료구조 — 서버 binder_proc가 binder_node(서비스 실체)와 binder_thread 스레드풀을 소유하고, 클라이언트 binder_proc는 그 node를 가리키는 binder_ref와 handle 정수 매핑을 갖되 node 포인터는 커널만 보유해 ref→node로 신원을 보증하는 구조](/images/study-android-internals/22-driver-structs-dark.png)

- <strong>`binder_proc`</strong>: `/dev/binder`를 연 프로세스마다 하나. 그 프로세스의 노드·참조·스레드·mmap 버퍼를 모두 관장한다.
- <strong>`binder_node`</strong>: 서버가 제공하는 Binder 객체의 커널 측 실체다. 소유 프로세스와 유저 포인터(cookie)를 안다.
- <strong>`binder_ref`</strong>: 클라이언트가 특정 노드를 참조할 때 만들어지는 핸들 항목이다. `handle 정수 → binder_ref → binder_node`로 이어진다. 유저스페이스가 아는 handle이 이 ref를 가리킨다.
- <strong>`binder_thread`</strong>: 프로세스 안에서 Binder 통신에 참여하는 스레드 하나. 자기 todo 큐와 트랜잭션 스택을 갖는다.

<strong>스레드 관리</strong>는 드라이버가 능동적으로 한다. 수신 대기 스레드가 모자라면 커널이 `BR_SPAWN_LOOPER`를 보내 유저스페이스에 스레드풀을 늘리라고 지시하고, `ProcessState`가 새 스레드를 만들어 `BC_REGISTER_LOOPER`로 합류시킨다. 상한이 `setThreadPoolMaxThreadCount`(기본 15+메인 1)다.

<strong>우선순위 상속(priority inheritance)</strong>도 커널이 처리한다. 낮은 우선순위 클라이언트가 높은 우선순위 서버를 호출하거나 그 반대일 때, 트랜잭션을 처리하는 서버 스레드가 요청 스레드의 우선순위(nice/RT)를 <strong>일시적으로 물려받는다</strong>. 우선순위 역전으로 UI 스레드가 vendor 데몬 뒤에서 굶는 상황을 막는 장치다.

## Death notification 커널 구현

[CH21](/study/android-internals/21-binder-userspace)의 `linkToDeath()`는 커널 안에서 `BC_REQUEST_DEATH_NOTIFICATION`으로 등록된다. 대상 노드의 소유 프로세스가 죽어 `binder_proc`가 정리될 때, 커널은 그 노드를 참조하던 모든 ref를 훑어 각 클라이언트에게 <strong>`BR_DEAD_BINDER`</strong>를 통지한다. 유저스페이스는 이걸 받아 `binderDied()`를 호출한다. 클라이언트가 죽은 서버를 계속 붙잡고 있는 좀비 참조를 막는다.

## 디버깅과 트레이싱

Binder 문제는 겉으로는 "앱이 멈췄다"로만 보이므로, 커널이 노출하는 관측 지점을 알아야 원인을 짚는다.

<strong>debugfs</strong>가 1차 창구다.

```
# 전체 프로세스의 노드·ref·버퍼 상태
$ cat /sys/kernel/debug/binder/state

# 진행 중·대기 중 트랜잭션
$ cat /sys/kernel/debug/binder/transactions

# 최근 트랜잭션 로그 (실패 포함)
$ cat /sys/kernel/debug/binder/transaction_log
$ cat /sys/kernel/debug/binder/failed_transaction_log

# 프로세스별 상세 (PID로)
$ cat /sys/kernel/debug/binder/proc/<pid>
```

`stats`에는 BC_/BR_ 명령별 카운트가 쌓여, 어떤 명령이 폭주하는지 볼 수 있다. BinderFS 환경에서는 일부가 `/dev/binderfs/binder_logs/`로 옮겨진 경우도 있다.

<strong>perfetto</strong>가 실전 도구다. 시스템 트레이스를 뜨면 Binder transaction이 별도 트랙으로 시각화돼, 어느 스레드가 어떤 서비스를 호출하고 얼마나 걸렸는지 타임라인으로 보인다. `atrace`의 `binder_driver`·`binder_lock` 카테고리를 켜면 커널 이벤트까지 딸려온다. [관측성 스터디](/study/observability/26-profile-types-ebpf)의 eBPF 트레이싱과 같은 결의 접근이다.

<strong>흔한 문제</strong>의 진단 패턴은 다음과 같다.

- <strong>스레드풀 고갈</strong>: 서버의 모든 Binder 스레드가 긴 작업이나 재진입 호출에 묶여 새 요청을 못 받는 상태다. `transactions`에 대기 트랜잭션이 쌓이고 클라이언트가 무한 블록된다. 스레드풀 크기를 늘리거나, 서버 콜백 안에서 오래 걸리는 작업을 별도 워커로 빼서 해결한다.
- <strong>데드락</strong>: A가 B를 동기 호출하고 그 처리 중 B가 다시 A를 동기 호출하면 서로를 기다린다. 트랜잭션 스택에 순환이 보이면 이 경우다. 한쪽을 oneway로 바꾸거나 호출 방향을 재설계한다.
- <strong>TransactionTooLargeException</strong>: 위에서 다룬 1MB 초과. `failed_transaction_log`에 `-ENOMEM`으로 남는다.

::: tip 핵심 정리
- Binder는 `/dev/binder`·`hwbinder`·`vndbinder` 세 캐릭터 디바이스로 도메인이 갈리고, Android 11+는 BinderFS로 인스턴스를 동적 관리한다.
- 모든 통신은 ioctl `BINDER_WRITE_READ`로 BC_(명령)/BR_(응답)를 한 시스템 콜에 실어 주고받는다.
- 수신 프로세스의 mmap 버퍼로 딱 한 번 복사하는 one-copy가 Binder의 속도 비결이고, 이 버퍼가 프로세스당 약 1MB라 초과 시 TransactionTooLargeException이 난다.
- flat_binder_object에서 커널이 로컬 객체↔핸들·fd를 변환하며, 유저는 불투명 handle만 쥐므로 커널이 신원을 보증한다.
- binder_proc/node/ref/thread 자료구조와 debugfs(state·transactions·transaction_log)·perfetto로 스레드풀 고갈·데드락·버퍼 초과를 진단한다.
:::

## 다음 챕터

[CH23. 네이티브 데몬 서비스 만들기](/study/android-internals/23-native-daemon-case-study)에서는 지금까지의 모든 지식을 모아, AgIsoStack++ 기반 C++ CAN 데몬 agcand을 vendor 파티션에 처음부터 올린다. 프로젝트 배치·라이브러리 포팅·AIDL·init rc·sepolicy·VINTF·빌드·검증·트러블슈팅까지 end-to-end 케이스 스터디로 다룬다.
