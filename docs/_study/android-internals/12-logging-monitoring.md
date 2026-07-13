---
title: "CH12. 로깅·통계·모니터링"
description: "logd의 로그 버퍼 구조와 logcat 고급 사용법, 커널 로그와 pstore, statsd 통계 프레임워크, incident·dropbox 수집, debuggerd와 tombstone, perfetto·eBPF 트레이싱까지 안드로이드의 관측 도구 전반을 다룬다."
date: 2026-07-13
tags: [android, aosp, logging, statsd, tracing, ebpf]
---

# CH12. 로깅·통계·모니터링

관측 능력은 임베디드 개발의 생사를 가른다. 데스크톱처럼 디버거를 붙이기 어려운 현장 단말에서, "무슨 일이 일어났나"를 사후에 재구성할 수 있느냐가 문제 해결 속도를 결정한다. 안드로이드는 logd·statsd·incidentd·debuggerd·perfetto로 이어지는 촘촘한 관측 스택을 갖췄다. 이 장은 각 계층이 무엇을 어떻게 수집하는지, 그리고 네이티브 데몬을 디버깅할 때 어디를 봐야 하는지를 정리한다.

## 학습 목표
- logd의 로그 버퍼 구조와 liblog 경로, logcat 고급 필터링을 익힌다.
- 커널 로그와 pstore(ramoops)로 재부팅 전 상태를 복구하는 법을 안다.
- statsd의 atom 기반 통계 수집과 IStats HAL 구조를 이해한다.
- incidentd·dropbox의 크래시·ANR·tombstone 수집 경로를 파악한다.
- debuggerd/tombstone 읽는 법과 perfetto·eBPF 트레이싱 기초를 익힌다.

## logd 아키텍처

안드로이드 로그는 파일이 아니라 <strong>logd</strong>라는 데몬이 관리하는 메모리 링 버퍼에 쌓인다. 파일이 아니라 메모리라는 점이 중요하다 — 빠르고, 디스크를 소모하지 않지만, 재부팅하면 사라진다.

![logd 흐름 — 앱·네이티브 데몬·커널이 liblog로 유닉스 소켓(/dev/socket/logdw)을 통해 logd에 로그를 보내면 main/system/radio/events/crash 링 버퍼에 쌓이고, logcat과 DropBox·statsd·incidentd 구독자가 이를 읽어간다](/images/study-android-internals/12-logd-flow-light.png)
![logd 흐름 — 앱·네이티브 데몬·커널이 liblog로 유닉스 소켓(/dev/socket/logdw)을 통해 logd에 로그를 보내면 main/system/radio/events/crash 링 버퍼에 쌓이고, logcat과 DropBox·statsd·incidentd 구독자가 이를 읽어간다](/images/study-android-internals/12-logd-flow-dark.png)

logd는 로그를 용도별 버퍼로 나눈다.

- <strong>main</strong>: 앱과 프레임워크의 일반 로그(`Log.d/i/w/e`)가 들어간다. 가장 흔히 보는 버퍼다.
- <strong>system</strong>: 시스템 컴포넌트(`system_server`, 시스템 데몬)의 로그.
- <strong>radio</strong>: 텔레포니·모뎀 관련 로그. 셀룰러 없는 장비는 거의 비어 있다.
- <strong>events</strong>: 구조화된 이벤트 로그. 텍스트가 아니라 바이너리 태그+값 형식이라, `am_proc_start` 같은 시스템 이벤트를 기계가 파싱하기 좋다.
- <strong>crash</strong>: 크래시 직전 로그를 별도로 모아 유실을 줄인다.

로그를 <strong>생산</strong>하는 쪽은 `liblog`를 통한다. 자바는 `android.util.Log`, 네이티브는 `__android_log_print()`나 `ALOGD` 매크로를 쓰며, 이들은 결국 유닉스 도메인 소켓 `/dev/socket/logdw`(write)로 logd에 넘긴다. <strong>소비</strong>하는 쪽은 `/dev/socket/logdr`(read)로 붙는다. `logcat`이 대표 소비자다.

logcat 고급 사용법은 실무에서 필수다.

```bash
# 특정 버퍼만 (-b), 여러 버퍼
adb logcat -b crash
adb logcat -b main -b system -b events

# 출력 포맷 (-v): threadtime이 시간+pid+tid까지 보여줘 기본으로 유용
adb logcat -v threadtime
adb logcat -v color        # 레벨별 색상

# 특정 프로세스만
adb logcat --pid=$(adb shell pidof com.example.app)

# 태그 필터: "MyTag"는 Debug 이상, 나머지는 Silent
adb logcat MyDaemon:D CANStack:V *:S

# 버퍼를 비우고 시작 (-c), 지금까지만 덤프하고 종료 (-d)
adb logcat -c
adb logcat -d > snapshot.txt
```

로그 태그와 우선순위(`V/D/I/W/E/F`)는 필터의 축이다. `TAG:PRIORITY` 쌍을 나열하고 마지막에 `*:S`(전부 Silent)를 붙이면 원하는 태그만 남길 수 있다. 커스텀 네이티브 데몬은 고유 태그(`CANStack` 등)를 정해두면 이런 필터링으로 자기 로그만 골라볼 수 있어 편하다.

<strong>event log</strong>는 조금 다르다. `events` 버퍼의 항목은 `/system/etc/event-log-tags`에 정의된 숫자 태그+타입을 갖는 구조화 로그다. `am_anr`, `am_kill` 같은 시스템 이벤트가 여기 남아, 앱이 언제 어떤 이유로 죽었는지를 사후 추적할 때 결정적 단서가 된다.

```bash
adb logcat -b events -v threadtime
# ... am_kill  : [0,4521,com.example.cached,906,empty]
```

## 커널 로그와 pstore

logd는 유저스페이스 로그를 담지만, 커널 자체의 메시지는 별도다. 커널 링 버퍼는 `dmesg`(또는 `/dev/kmsg`)로 본다. 드라이버 오류, OOM, SELinux denial 등이 여기 남는다.

```bash
adb shell dmesg | tail -50
adb shell dmesg | grep -iE 'avc|denied|oom|panic'
```

문제는 <strong>커널 패닉이나 갑작스러운 재부팅</strong> 상황이다. 이때 dmesg는 이미 날아갔다. 이를 위한 장치가 <strong>pstore/ramoops</strong>다. 커널이 재부팅 사이에도 내용이 보존되는 특정 RAM 영역(persistent RAM)에 마지막 로그를 저장해두고, 재부팅 후 그 영역을 `/sys/fs/pstore`에 노출한다.

```bash
# 직전 부팅의 커널 콘솔 로그 (패닉 원인 추적의 핵심)
adb shell cat /sys/fs/pstore/console-ramoops-0
# 또는 구형 경로
adb shell cat /proc/last_kmsg
```

::: warning 임베디드 디버깅 필수
현장 단말이 원인 모르게 리부트될 때, `console-ramoops`가 유일한 단서인 경우가 많다. 커스텀 보드를 bring-up할 때 디바이스 트리에 ramoops 예약 메모리 영역을 반드시 잡아둬야 한다. 이게 없으면 패닉 원인을 영원히 못 잡는다. 워치독 리셋, 전원 순단, 드라이버 패닉을 구분하려면 이 로그가 필수다.
:::

## statsd

로그가 "무슨 일이 있었나"의 텍스트 기록이라면, <strong>statsd</strong>는 "얼마나 자주·얼마나"의 구조화된 통계를 담당한다. 배터리 소모, 앱 시작 시간, 네트워크 사용량 같은 지표를 수집해 집계한다.

statsd의 단위는 <strong>atom</strong>이다. 하나의 원자적 이벤트(예: `AppStart`, `WakelockStateChanged`)를 나타내는 스키마로, `stats_log.proto`에 정의된다. 컴포넌트들이 atom을 statsd로 푸시하거나(pushed), statsd가 주기적으로 당겨온다(pulled). `StatsCompanionService`가 프레임워크와 statsd 사이를 잇고, 하드웨어 지표(전력 레일 등)는 <strong>IStats HAL</strong>을 통해 벤더 구현에서 올라온다.

```bash
# statsd가 수집 중인 설정·atom 확인
adb shell dumpsys stats
adb shell cmd stats print-stats

# 특정 atom을 직접 기록 (테스트용)
adb shell cmd stats log-app-breadcrumb 1 2
```

일반 앱 개발에서 statsd를 직접 다룰 일은 드물지만, 커스텀 장비에서 자체 텔레메트리(예: 엔진 가동 시간, 특정 에러 발생 빈도)를 벤더 atom으로 정의해 수집하는 파이프라인을 구축할 수 있다는 점은 알아둘 가치가 있다.

## incident와 dropbox

크래시·ANR·tombstone처럼 "사후 분석이 필요한 무거운 덩어리"는 별도 수집 경로로 모인다.

![크래시 수집 경로 — 네이티브 프로세스의 시그널은 debuggerd→crash_dump→tombstone으로, 앱의 ANR·미처리 예외는 system_server(AMS)→ANR dump로 흐르며, 두 경로 모두 DropBoxManager에 사본이 적재돼 bugreport로 회수된다](/images/study-android-internals/12-crash-flow-light.png)
![크래시 수집 경로 — 네이티브 프로세스의 시그널은 debuggerd→crash_dump→tombstone으로, 앱의 ANR·미처리 예외는 system_server(AMS)→ANR dump로 흐르며, 두 경로 모두 DropBoxManager에 사본이 적재돼 bugreport로 회수된다](/images/study-android-internals/12-crash-flow-dark.png)

- <strong>DropBoxManager</strong>: 시스템 이벤트(앱 크래시, ANR, 커널 이슈, tombstone)의 스냅샷을 `/data/system/dropbox`에 시간순으로 적재한다. 각 항목은 태그(`data_app_crash`, `system_app_anr` 등)를 갖는다. bugreport가 이 디렉토리를 통째로 회수한다.
- <strong>incidentd</strong>: 온디맨드로 "지금 시스템 상태 스냅샷"을 뜨는 데몬이다. 여러 서비스의 `dumpsys` 출력·로그를 하나의 incident report(proto)로 묶는다. `incident` 명령이나 버그 리포트 흐름에서 트리거된다.

```bash
# DropBox에 쌓인 항목 목록·내용
adb shell dumpsys dropbox --print
adb shell dumpsys dropbox data_app_crash --print

# incident report 생성
adb shell incident 2>/dev/null > incident.pb
```

ANR(Application Not Responding)이 발생하면 `system_server`의 ActivityManager가 감지해 관련 스레드들의 스택을 `/data/anr/traces.txt`(현재는 시간별 파일)에 덤프하고, 사본을 DropBox에 넣는다. 이 traces가 "메인 스레드가 어디서 막혔나"를 보여주는 결정적 자료다.

## 디버깅 도구 — debuggerd와 tombstone

네이티브 코드가 `SIGSEGV`·`SIGABRT` 같은 치명 시그널로 죽으면, <strong>debuggerd</strong>가 개입한다. 앱/데몬 프로세스에는 debuggerd의 시그널 핸들러가 미리 심겨 있어, 크래시 순간 별도의 `crash_dump` 프로세스를 띄운다. `crash_dump`는 `ptrace`로 죽어가는 프로세스에 붙어 레지스터·스택을 언와인드하고, 그 결과를 <strong>tombstone</strong> 파일(`/data/tombstones/tombstone_NN`)로 남긴다.

tombstone을 읽는 법의 개요는 이렇다(상세 분석은 [CH15 네이티브 레벨과 Bionic](/study/android-internals/15-native-level)에서 다룬다).

```
*** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***
Build fingerprint: 'Example/device/...'
pid: 4521, tid: 4521, name: mydaemon  >>> /vendor/bin/mydaemon <<<
signal 11 (SIGSEGV), code 1 (SEGV_MAPERR), fault addr 0x0    # 널 포인터
    x0  0000000000000000  x1  ...                            # 레지스터 덤프
backtrace:
    #00 pc 0000000000012abc  /vendor/lib64/libcan.so (parse_pgn+0x4c)   # 심볼 있으면 함수명
    #01 pc 0000000000010def  /vendor/bin/mydaemon (main+0x120)
```

핵심은 `signal`(무슨 시그널로 죽었나), `fault addr`(어느 주소를 잘못 건드렸나), `backtrace`(어느 함수 체인에서 터졌나)다. `fault addr 0x0`이면 널 포인터 역참조라는 강한 신호다. backtrace의 심볼이 제대로 보이려면 심볼 정보가 있는 라이브러리로 대조(`ndk-stack`·`llvm-symbolizer`)해야 한다.

<strong>bugreport</strong>는 이 모든 걸 하나로 묶는 최상위 도구다. logcat 전 버퍼, dmesg, dumpsys 전체, tombstone, ANR traces, DropBox를 통째로 zip으로 뽑는다.

```bash
adb bugreport bugreport.zip
```

현장에서 재현 안 되는 이슈를 만나면, 무조건 bugreport부터 확보하는 게 정석이다. 그 안에 위에서 다룬 거의 모든 관측 데이터가 들어 있다.

## 트레이싱

로그·통계가 "무엇이 일어났나"라면, 트레이싱은 "언제·얼마나 오래·어떤 순서로"를 밀리초 이하 정밀도로 본다.

- <strong>strace</strong>: 프로세스의 시스템 콜을 추적한다. 네이티브 데몬이 어느 `open`/`ioctl`에서 실패하는지 잡을 때 유용하다.
  ```bash
  adb shell strace -f -p $(adb shell pidof mydaemon)
  adb shell strace -f -e trace=ioctl ./mydaemon   # ioctl만
  ```
- <strong>atrace / perfetto</strong>: 안드로이드 시스템 전반의 트레이싱. `atrace`는 커널 ftrace와 유저스페이스 트레이스포인트(`ATRACE_*`)를 수집하고, <strong>perfetto</strong>는 그 상위의 통합 트레이싱 스택으로, CPU 스케줄링·프레임·바인더 트랜잭션을 하나의 타임라인으로 시각화한다.
  ```bash
  # perfetto 트레이스 수집 (기간·카테고리 지정)
  adb shell perfetto -t 10s -o /data/misc/perfetto-traces/trace \
      sched freq idle am wm gfx binder_driver
  adb pull /data/misc/perfetto-traces/trace
  # → ui.perfetto.dev 에서 열어 분석
  ```
- <strong>jtrace</strong>: Levin이 만든 향상된 ftrace 프론트엔드로, 커널 트레이스포인트를 더 편하게 다룬다.

<strong>eBPF</strong>는 커널에 안전한 프로그램을 로드해 이벤트를 계측하는 최신 관측 기술이다. 안드로이드는 부팅 시 `bpfloader`가 `/system/etc/bpf`의 `.o` 프로그램을 로드하고, 핀된 맵·프로그램을 `/sys/fs/bpf`에 노출한다. 네트워크 통계·전력 프로파일링 등에 쓰인다.

```bash
adb shell ls /sys/fs/bpf              # 로드된 eBPF 맵·프로그램
adb shell dumpsys netstats            # eBPF 기반 네트워크 통계가 여기 반영
```

eBPF의 개념과 프로파일링 활용은 관측성 스터디에서 깊게 다뤘다 — [관측성 CH26 프로파일 타입과 eBPF](/study/observability/26-profile-types-ebpf)와 연결해 보면, 리눅스 서버에서 쓰는 바로 그 eBPF가 안드로이드 커널에서도 동일한 원리로 동작함을 알 수 있다.

::: info 네이티브 데몬 디버깅 관점 팁
커스텀 CAN 통신 데몬이 "가끔 멈춘다"는 식의 재현 어려운 문제를 만나면 층을 나눠 접근한다. (1) logcat에서 데몬 태그 필터로 마지막 정상 동작 지점 확인, (2) tombstone이 있으면 크래시인지 확인, 없으면 데드락/블로킹 의심, (3) `strace -f`로 어느 syscall(대개 `ioctl`이나 소켓 `read`)에서 멈췄는지 확인, (4) perfetto로 스케줄링·바인더 관점에서 blocked 상태를 시각화. SocketCAN 레벨의 문제라면 [CAN 스터디 CH13 SocketCAN 기초](/study/can/13-socketcan-basics)로 내려가 인터페이스·필터 설정을 점검한다.
:::

::: tip 핵심 정리
- logd는 main/system/radio/events/crash 링 버퍼(메모리)로 로그를 나눠 담고, liblog가 `/dev/socket/logdw`로 쓰고 logcat이 `logdr`로 읽는다. `-b`·`-v`·`--pid`·태그 필터가 실무 핵심이다.
- 커널 로그는 dmesg로 보고, 재부팅으로 날아간 직전 로그는 pstore(`console-ramoops`)로 복구한다 — 임베디드 패닉 추적의 필수 장치다.
- statsd는 atom 단위로 구조화 통계를 수집하며, 하드웨어 지표는 IStats HAL로 올라온다.
- DropBox·incidentd가 크래시·ANR·tombstone을 적재하고, bugreport가 이 전부를 하나로 회수한다.
- 네이티브 크래시는 debuggerd→crash_dump→tombstone 경로로 남으며, signal·fault addr·backtrace가 원인 분석의 축이다.
- strace(syscall)·perfetto/atrace(타임라인)·eBPF(커널 계측)로 트레이싱하며, eBPF는 리눅스 서버의 그것과 같은 원리다.
:::

## 다음 챕터

[CH13. 전원 관리](/study/android-internals/13-power-management)에서는 suspend/resume와 wakelock의 커널·유저스페이스 양면, PowerManagerService와 Doze, healthd에서 health HAL로의 배터리 스택, cpufreq governor와 EAS, thermal 관리, 그리고 배터리 없는 상시 전원 임베디드 장비에서 무엇을 끄고 무엇을 남길지를 다룬다.
