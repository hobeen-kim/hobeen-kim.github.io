---
title: "CH11. 리눅스 렌즈로 본 애플리케이션"
description: "안드로이드 앱을 프레임워크가 아니라 리눅스 프로세스로 내려다본다. Zygote 자식 구조와 /proc 훑기, uid/gid 모델, VSS/RSS/PSS/USS 메모리 지표, lmkd의 OOM 처리, cgroup·태스크 프로파일, ELF 네이티브 바이너리와 링커까지 파헤친다."
date: 2026-07-13
tags: [android, aosp, linux, process, memory, cgroup]
---

# CH11. 리눅스 렌즈로 본 애플리케이션

안드로이드 앱은 Activity·Service·Binder로 이야기하지만, 그 밑을 벗겨내면 결국 하나의 리눅스 프로세스다. 프레임워크의 추상을 잠시 걷어내고 `/proc`, uid/gid, 메모리 페이지, cgroup, ELF의 관점에서 앱을 다시 보면, "왜 이 프로세스가 죽었나", "메모리를 실제로 얼마나 쓰나", "네이티브 데몬이 왜 안 뜨나" 같은 질문에 정확히 답할 수 있게 된다. C++ 네이티브 데몬을 직접 올리는 임베디드 개발에서는 이 렌즈가 특히 값지다.

## 학습 목표
- 모든 앱이 Zygote의 자식이라는 사실과 `/proc/<pid>` 구조를 읽는 법을 익힌다.
- 앱 프로세스의 uid/gid·supplementary gid·isolated process 모델을 이해한다.
- VSS/RSS/PSS/USS의 정확한 정의와 차이, 측정 도구를 익힌다.
- oom_score_adj와 lmkd의 PSI 기반 kill 메커니즘을 파악한다.
- cgroup·태스크 프로파일로 스케줄링 그룹이 나뉘는 구조와 ELF·링커 기초를 안다.

## 프로세스 관점의 앱 — 모든 앱은 Zygote의 자식

안드로이드에서 앱을 실행한다는 것은 새 프로세스를 `fork+exec`하는 게 아니라, 이미 떠 있는 <strong>Zygote</strong>를 `fork`하는 것이다. Zygote는 부팅 시 ART 런타임과 프리로드된 클래스·리소스를 통째로 메모리에 올려둔 템플릿 프로세스다. 앱이 필요하면 Zygote가 자신을 fork하고, copy-on-write 덕분에 공유 페이지를 물려받아 순식간에 앱 프로세스가 뜬다. Zygote와 init의 상세 흐름은 [CH8 init과 Zygote](/study/android-internals/08-init-zygote)에서 다뤘다.

이 사실의 실질적 결과는 `ps`로 부모를 따라가 보면 드러난다.

```bash
adb shell ps -A -o PID,PPID,NAME | grep -E 'zygote|com.example'
#  PID  PPID NAME
#  789    1  zygote64          # init(1)의 자식
#  790    1  zygote            # 32비트용
# 4521  789  com.example.app   # 앱은 zygote64(789)의 자식
```

앱 프로세스의 속살은 `/proc/<pid>` 아래에 전부 노출된다. 이 가상 파일시스템은 [CH4 파일과 디렉토리 구조](/study/android-internals/04-files-directories)에서 소개한 procfs다. 앱을 디버깅할 때 실제로 훑는 항목은 이렇다.

```bash
PID=$(adb shell pidof com.example.app)

# status: uid/gid, 상태, 스레드 수, VmRSS 등 요약
adb shell cat /proc/$PID/status

# maps: 가상 주소 공간에 매핑된 모든 영역 (라이브러리·힙·스택)
adb shell cat /proc/$PID/maps

# smaps: maps + 각 매핑의 RSS/PSS/Private/Shared 상세
adb shell cat /proc/$PID/smaps

# fd: 열린 파일 디스크립터 (소켓·파일·Binder)
adb shell ls -l /proc/$PID/fd

# task: 이 프로세스의 모든 스레드
adb shell ls /proc/$PID/task
```

`/proc/<pid>/task`를 보면 앱 프로세스가 단일 스레드가 아님이 분명해진다. 대표적인 스레드들은 다음과 같다.

- <strong>main</strong>: 메인(UI) 스레드. `ActivityThread`의 메시지 루프가 돈다.
- <strong>Binder:&lt;pid&gt;_N</strong>: Binder 스레드풀. IPC 요청을 받는 워커들이다. Binder의 상세는 [CH21 Binder 유저스페이스](/study/android-internals/21-binder-userspace)에서 다룬다.
- <strong>RenderThread</strong>: 하드웨어 가속 렌더링을 전담한다.
- <strong>HeapTaskDaemon / GC</strong>: ART의 가비지 컬렉션 워커.
- <strong>Jit thread pool</strong>: JIT 컴파일 워커.

스레드 이름은 `/proc/<pid>/task/<tid>/comm`에서 직접 읽을 수 있어, 어떤 스레드가 CPU를 먹는지 추적할 때 유용하다.

## uid/gid 모델

[CH10](/study/android-internals/10-configuration)에서 uid가 `userId × 100000 + appId`로 조합된다고 봤다. 리눅스 렌즈에서 중요한 것은 이 uid/gid가 실제 파일 권한과 커널 자원 접근을 결정한다는 점이다.

- <strong>앱마다 고유 uid</strong>: 설치 시 배정된 uid가 그 앱의 프로세스와 데이터 디렉토리(`/data/data/<pkg>`) 소유자가 된다. 다른 앱의 데이터는 파일 권한상 애초에 못 읽는다. 이것이 안드로이드 샌드박스의 1차 방어선이다.
- <strong>supplementary gid</strong>: 앱이 특정 권한을 받으면, 그에 대응하는 보조 그룹이 프로세스에 추가된다. 예를 들어 `INTERNET` 권한은 `inet`(AID 3003) gid를, 외부 저장소 접근은 `sdcard_rw`/`media_rw` gid를 붙인다. 커널의 소켓·파일 접근 검사가 이 gid로 이뤄진다.

```bash
adb shell cat /proc/$PID/status | grep -E '^(Uid|Gid|Groups)'
# Uid:  10123 10123 10123 10123
# Gid:  10123 10123 10123 10123
# Groups: 3003 9997 20123 50123    # inet 등 supplementary gid
```

- <strong>isolated process</strong>: 웹뷰 렌더러나 `android:isolatedProcess="true"` 서비스는 `99000`~`99999` 범위의 임시 격리 uid로 뜬다. 거의 아무 권한도 없고 자기 부모 앱의 데이터조차 못 본다. 신뢰할 수 없는 코드(웹 콘텐츠, 파싱)를 최대한 가둬 실행하려는 장치다.

## 메모리 지표 — VSS / RSS / PSS / USS

"이 앱이 메모리를 얼마나 쓰나"라는 질문은 생각보다 답이 여럿이다. 공유 라이브러리 때문에 단순 합산이 실제 사용량을 뻥튀기하기 때문이다. 그래서 네 가지 지표를 구분해야 한다.

![메모리 지표 포함 관계 — VSS가 가상 주소 공간 전체를 담고, 그 안에 물리 페이지 전체인 RSS, 공유 페이지를 프로세스 수로 나눈 PSS, 이 프로세스만의 독점 페이지인 USS가 순서대로 중첩된다](/images/study-android-internals/11-memory-metrics-light.png)
![메모리 지표 포함 관계 — VSS가 가상 주소 공간 전체를 담고, 그 안에 물리 페이지 전체인 RSS, 공유 페이지를 프로세스 수로 나눈 PSS, 이 프로세스만의 독점 페이지인 USS가 순서대로 중첩된다](/images/study-android-internals/11-memory-metrics-dark.png)

- <strong>VSS(Virtual Set Size)</strong>: 프로세스가 <strong>매핑</strong>한 가상 주소 공간 전체. 실제로 물리 메모리에 올라왔는지와 무관하다. `mmap`으로 크게 예약만 해둔 영역도 포함되므로, 실사용량 지표로는 거의 쓸모없다.
- <strong>RSS(Resident Set Size)</strong>: 실제 물리 메모리에 올라온 페이지 전체. 문제는 <strong>공유 라이브러리를 통째로 계산</strong>한다는 것. `libc`가 50개 프로세스에 매핑돼 있으면, 50개 프로세스의 RSS에 각각 `libc` 전체 크기가 더해진다. 다 합치면 실제 물리 메모리보다 커진다.
- <strong>PSS(Proportional Set Size)</strong>: 공유 페이지를 그 페이지를 공유하는 프로세스 수로 <strong>나눠서</strong> 배분한 값. `libc` 한 페이지를 50개가 공유하면 각 프로세스에 1/50씩 잡힌다. 그래서 모든 프로세스의 PSS를 더하면 실제 물리 사용량과 거의 일치한다. 안드로이드가 메모리 회계의 기준으로 삼는 지표다.
- <strong>USS(Unique Set Size)</strong>: 오직 이 프로세스만 쓰는(공유되지 않은) 독점 페이지. 이 프로세스를 죽였을 때 실제로 회수되는 메모리가 대략 USS다.

포함 관계는 `VSS ⊇ RSS ⊇ PSS ⊇ USS`다. 측정 도구는 상황별로 이렇게 쓴다.

```bash
# procrank: 모든 프로세스를 VSS/RSS/PSS/USS로 한눈에 (userdebug 빌드)
adb shell procrank

# showmap <pid>: 매핑별로 RSS/PSS/Private/Shared 분해
adb shell showmap $PID

# librank: 라이브러리별로 어느 프로세스가 얼마나 물고 있는지
adb shell librank

# dumpsys meminfo: 항목별(Java heap/Native heap/Graphics/...) PSS
adb shell dumpsys meminfo com.example.app
```

`dumpsys meminfo`의 출력은 실무에서 가장 자주 본다. Native Heap이 계속 커지면 C++ 쪽 누수, Java Heap이 커지면 자바 객체 누수를 의심하는 식으로 층위를 나눠 볼 수 있다.

::: details smaps 한 매핑 읽는 법
```
7f8a2c0000-7f8a2e0000 r-xp 00000000 fd:00 1234  /apex/com.android.runtime/lib64/bionic/libc.so
Size:                128 kB   # 가상 크기 (VSS 기여분)
Rss:                  96 kB   # 물리 상주 (RSS 기여분)
Pss:                   2 kB   # 공유 분할 후 (PSS 기여분) — 많은 프로세스가 공유
Private_Clean:         0 kB
Private_Dirty:         0 kB   # 이 둘의 합이 대략 USS 기여분
Shared_Clean:         96 kB   # 공유 중인 깨끗한 페이지 (코드)
```
`r-xp`(읽기+실행)는 코드 세그먼트, `rw-p`는 데이터/힙이다. Private_Dirty가 큰 매핑이 이 프로세스만의 실사용 메모리이므로, 누수를 좇을 때는 이 열을 본다.
:::

## OOM과 lmkd

메모리가 부족해지면 무언가는 죽어야 한다. 데스크톱 리눅스는 커널의 OOM killer가 처리하지만, 안드로이드는 유저스페이스 데몬 <strong>lmkd(Low Memory Killer Daemon)</strong>가 더 똑똑하게 판단한다.

핵심은 각 프로세스에 붙는 `oom_score_adj`(구 `oom_adj`) 값이다. `-1000`(절대 안 죽음)부터 `+1000`(가장 먼저 죽음)까지의 범위로, 프로세스의 중요도를 나타낸다. `system_server`의 `ProcessList`가 앱의 상태(포그라운드/보이는/서비스/캐시됨)에 따라 이 값을 계속 갱신한다.

```bash
# 특정 프로세스의 현재 oom_score_adj
adb shell cat /proc/$PID/oom_score_adj

# 전체 프로세스를 adj 순으로 (dumpsys)
adb shell dumpsys activity oom | head -40
```

`ProcessList`의 adj 단계는 대략 이렇게 나뉜다.

- <strong>포그라운드 앱</strong>(`FOREGROUND_APP_ADJ = 0`): 사용자가 지금 보고 있는 앱. 거의 안 죽는다.
- <strong>보이는 앱</strong>(`VISIBLE_APP_ADJ = 100`): 화면 일부에 보이는 앱.
- <strong>서비스</strong>(`SERVICE_ADJ = 500`): 백그라운드 서비스.
- <strong>캐시된 앱</strong>(`CACHED_APP_MIN_ADJ = 900~`): 종료돼도 되는 캐시 상태. 메모리 압박 시 가장 먼저 회수된다.

과거의 lmkd는 커널의 lowmemorykiller 드라이버와 minfree 임계값(빈 메모리가 이만큼 떨어지면 이 adj 이상을 죽여라)에 의존했다. 현재(Android 10+)의 lmkd는 커널 <strong>PSI(Pressure Stall Information)</strong>를 구독한다. PSI는 "메모리 부족으로 작업이 지연된 시간 비율"을 커널이 직접 알려주는 지표라, 단순 빈 메모리 양보다 실제 압박을 정확히 반영한다. lmkd는 PSI가 임계를 넘으면 `oom_score_adj`가 가장 높은 프로세스부터 `SIGKILL`한다.

```bash
# lmkd가 무엇을 왜 죽였는지
adb shell logcat -b all | grep -i lowmemorykiller
# lowmemorykiller: Kill 'com.example.cached' (4521), uid 10123,
#   oom_score_adj 906 to free ... because system is under memory pressure
```

::: warning 임베디드 장비에서 lmkd 튜닝
메모리가 넉넉지 않은 농기계 단말에서는 lmkd 설정이 안정성에 직결된다. `/vendor/etc/lmkd.rc`나 프로퍼티(`ro.lmk.*`)로 PSI 임계·minfree를 조정한다. 반드시 살아 있어야 하는 커스텀 데몬(예: CAN 통신 데몬)은 애초에 앱이 아니라 init 서비스로 올려 lmkd의 사정권 밖에 두거나, 매우 낮은 oom_score_adj를 부여해 보호해야 한다. 앱으로 올리면 메모리 압박 시 조용히 죽어 통신이 끊길 수 있다.
:::

## cgroup과 태스크 프로파일

메모리와 별개로, CPU를 어떻게 나눠 쓸지는 <strong>cgroup</strong>이 결정한다. 안드로이드는 리눅스 cgroup(control group)으로 프로세스를 스케줄링 그룹에 배치해, 포그라운드 앱은 빠르게·백그라운드는 절약해 돌린다. cgroup의 개념 자체는 컨테이너 격리와 뿌리가 같아 [Kubernetes 스터디 CH1 컨테이너 기초](/study/kubernetes/01-container-basics)와 직접 연결된다 — 컨테이너가 격리를 위해 쓰는 바로 그 커널 기능을, 안드로이드는 앱 스케줄링에 쓴다.

![cgroup·태스크 프로파일 — cgroup v2 루트 아래 top-app·foreground·background·system-background 그룹이 나뉘고 각 그룹이 task_profiles.json을 통해 cpuset·uclamp·cpu.shares 컨트롤러에 매핑된다](/images/study-android-internals/11-cgroup-hierarchy-light.png)
![cgroup·태스크 프로파일 — cgroup v2 루트 아래 top-app·foreground·background·system-background 그룹이 나뉘고 각 그룹이 task_profiles.json을 통해 cpuset·uclamp·cpu.shares 컨트롤러에 매핑된다](/images/study-android-internals/11-cgroup-hierarchy-dark.png)

안드로이드가 쓰는 대표 컨트롤러는 둘이다.

- <strong>cpuset</strong>: 프로세스를 특정 CPU 코어 집합에만 묶는다. big.LITTLE 구조에서 top-app은 대형 코어, background는 소형 코어로 제한하는 식이다.
- <strong>schedtune / uclamp</strong>: 스케줄러에게 이 그룹의 작업을 얼마나 공격적으로 부스트할지 알린다. 과거 schedtune이 하던 역할을 최신 커널에서는 <strong>uclamp(utilization clamping)</strong>가 대체한다. top-app은 최소 utilization을 높게 clamp해 빠르게 클럭을 올린다.

프로세스가 어느 그룹에 들어갈지는 `task_profiles.json`이 정의한다. 이 파일이 "TopAppforeground", "Background" 같은 프로파일 이름을, 실제 cgroup 파일(`cpuset.cpus`, `uclamp.min`, `cpu.shares`)에 쓸 값으로 매핑한다. `system_server`가 앱 상태가 바뀔 때마다 해당 프로파일을 적용한다.

```bash
# 특정 프로세스가 지금 어느 cgroup에 있는지
adb shell cat /proc/$PID/cgroup
# 0::/uid_10123/pid_4521          # cgroup v2 통합 계층

# 그룹별 소속 프로세스
adb shell cat /dev/cpuset/top-app/tasks
adb shell cat /dev/cpuset/background/tasks
```

Android 12 이후 cgroup v2로의 이행이 진행되면서 `/sys/fs/cgroup` 아래 통합 계층으로 정리됐지만, 하위 호환을 위해 `/dev/cpuset` 같은 v1 경로가 남아 있는 기기도 있다.

## ELF와 네이티브 바이너리

앱의 자바 코드는 ART가 돌리지만, 그 밑의 네이티브 라이브러리(`.so`)와 데몬 실행 파일은 리눅스의 표준 <strong>ELF(Executable and Linkable Format)</strong>다. C++ 네이티브 데몬을 직접 빌드해 올리는 임베디드 개발에서는 ELF와 링커를 이해해야 "왜 심볼을 못 찾나", "왜 라이브러리를 못 여나"를 풀 수 있다.

```bash
# ELF 헤더: 아키텍처(EM_AARCH64), 타입(EXEC/DYN), 엔트리 포인트
adb shell readelf -h /system/bin/mediaserver

# 동적 의존성: 이 바이너리가 필요로 하는 .so 목록
adb shell readelf -d /system/bin/mediaserver | grep NEEDED
#  0x0000000000000001 (NEEDED)  Shared library: [libbinder.so]
#  0x0000000000000001 (NEEDED)  Shared library: [libutils.so]

# 심볼 테이블·디스어셈블 (호스트에서 objdump 권장)
llvm-objdump -d out/.../mydaemon
```

바이너리를 실제로 실행 가능하게 잇는 것은 동적 링커 `/system/bin/linker64`(64비트)다. 안드로이드의 링커는 데스크톱 리눅스와 다른 중요한 특징이 있는데, <strong>linker namespace</strong>다. `/system`, `/vendor`, APEX가 각자의 라이브러리 검색 경로를 격리해, 예컨대 벤더 라이브러리가 시스템의 사적인 `.so`를 함부로 링크하지 못하게 막는다(Treble 아키텍처의 일부다). 그래서 커스텀 데몬이 특정 `.so`를 못 찾을 때는, 파일이 있느냐뿐 아니라 그 데몬이 속한 namespace의 검색 경로에 그 라이브러리가 노출돼 있느냐를 확인해야 한다. namespace와 Bionic 링커의 상세는 [CH15 네이티브 레벨과 Bionic](/study/android-internals/15-native-level)에서 다룬다.

빌드 관점의 최적화도 짚어둘 만하다. AOSP 네이티브 코드는 <strong>LTO(Link Time Optimization)</strong>로 링크 단계에서 함수 인라이닝·죽은 코드 제거를 하고, 성능이 중요한 컴포넌트는 <strong>PGO(Profile Guided Optimization)</strong>로 실제 실행 프로파일에 맞춰 핫 경로를 최적화한다. 커스텀 데몬을 빌드할 때 `Android.bp`에서 이 옵션을 켤 수 있지만, 디버깅 중에는 최적화가 스택 추적을 뭉개므로 개발 단계에서는 끄는 편이 낫다.

::: tip 핵심 정리
- 모든 앱은 Zygote를 fork한 자식이며, `/proc/<pid>`의 status·maps·smaps·fd·task로 그 속살을 전부 들여다볼 수 있다.
- 앱마다 고유 uid로 샌드박스되고, 권한은 supplementary gid로, 신뢰 불가 코드는 isolated process(99xxx)로 격리된다.
- 메모리는 `VSS ⊇ RSS ⊇ PSS ⊇ USS` 관계이며, 공유 라이브러리를 공정하게 나눈 PSS가 회계 기준이다. procrank·showmap·dumpsys meminfo로 측정한다.
- lmkd는 각 프로세스의 oom_score_adj와 커널 PSI를 보고 메모리 압박 시 우선순위가 낮은 프로세스를 kill한다. 살아야 할 데몬은 init 서비스로 보호한다.
- cgroup(cpuset·uclamp)과 task_profiles.json이 프로세스를 top-app/foreground/background 그룹에 배치해 CPU를 차등 분배하며, 이는 컨테이너의 cgroup과 같은 커널 기능이다.
- 네이티브 바이너리는 ELF이고 linker64가 namespace 단위로 격리해 링크한다. readelf로 의존성을 추적하고, LTO/PGO는 양산 시 켜되 디버깅 시엔 끈다.
:::

## 다음 챕터

[CH12. 로깅·통계·모니터링](/study/android-internals/12-logging-monitoring)에서는 logd의 로그 버퍼 구조와 logcat 고급 사용법, 커널 로그와 pstore, statsd 통계 프레임워크, incident·dropbox 수집 경로, debuggerd와 tombstone, 그리고 perfetto·eBPF 트레이싱까지 안드로이드의 관측 도구 전반을 훑는다.
