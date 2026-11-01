---
title: "Totals, 로깅, Peer Control"
description: "작업 전체 살포량 같은 총계를 세고 이어 가는 규칙, 기본 로깅과 로그 레코드 규칙, 위치에 따른 setpoint 송신, 다른 기계의 값을 받아 제어하는 Peer Control을 익힌다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, TaskController, TC, Totals, DataLogging, PeerControl, DDI]
prev: /study/isobus/46-tc-commands-pdack
next: /study/isobus/48-ddop-basics
---

# Totals, 로깅, Peer Control

::: info 학습 목표
- task total과 lifetime total의 차이를 설명하고, 태스크를 멈췄다 다시 시작할 때 총계가 어떻게 이어지는지 말할 수 있다.
- default data logging(DDI `0xDFFF`)을 언제 쓰고 어떻게 멈추는지 설명할 수 있다.
- TC가 위치에 따라 setpoint를 보내는 조건과, 기계의 반응 지연을 보정하는 이유를 설명할 수 있다.
- Peer Control에서 TC, 값을 내는 기계, 값을 받는 기계가 각각 하는 일을 설명할 수 있다.
- DDI 사전(ISO 11783-11)이 정하는 것과 TC 구현이 사전에 기대는 부분을 말할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [45장 TC 프로세스 데이터 기초](/study/isobus/45-tc-process-data-basics), [46장 프로세스 데이터 명령](/study/isobus/46-tc-commands-pdack), [42장 태스크와 시간 기록](/study/isobus/42-tc-task)
- 이 장에서 처음 나오는 말
  - 총계(total): 면적, 시간, 살포량처럼 작업하는 동안 계속 쌓이는 누적값
  - task total과 lifetime total: 태스크(작업 하나) 동안만 세는 총계와, 기계가 만들어진 뒤로 계속 세는 총계
  - TimeLog: TC가 작업 중 받은 값을 시간 순서로 남기는 기록 파일
  - 처리 구역(TreatmentZone): 처방 맵에서 같은 목표값을 쓰는 구역
  - Peer Control: 한 기계(source)가 다른 기계(user)에게 setpoint를 직접 보내도록 TC가 짝지어 주는 방식
:::

자동차 계기판에는 거리계가 두 개 있다. 여행 한 번의 거리를 재고 0으로 되돌릴 수 있는 트립 거리계와, 차가 만들어진 뒤로 달린 거리를 모두 세는 누적 거리계다. ISOBUS 작업기도 같은 두 가지 총계를 센다. 다만 트립 거리계와 달리, 태스크를 잠시 멈췄다 다시 시작하면 TC가 저장해 둔 값을 되돌려 주어 이어서 센다. 이 장은 총계를 세고 기록하는 규칙, 위치에 따라 목표값을 보내는 규칙, 그리고 한 기계의 값을 다른 기계가 받아 제어하는 Peer Control을 본다.

이 장에서 TC(Task Controller)는 TC 서버를, 클라이언트는 TC에 연결해 일하는 작업기 쪽 ECU를 말한다.

## 1. Totals: 작업 전체 살포량은 누가 어떻게 세나

이 절은 "이번 작업에서 모두 몇 ha를 뿌렸나"라는 숫자가 어떻게 만들어지는지 본다. 태스크가 중간에 멈췄다 다시 시작해도 숫자가 끊기지 않아야 한다는 점이 핵심이다.

### 사례: 점심때 멈췄다 오후에 이어 뿌린 작업

농부가 아침에 살포 태스크를 시작해 3 ha를 뿌리고 점심때 일시정지했다. 오후에 재개해 2 ha를 더 뿌리고 완료했다. FMIS(Farm Management Information System, 농장 관리 소프트웨어)에 남아야 할 이 태스크의 총면적은 5 ha다. 한편 살포기 자체가 산 뒤로 뿌린 누적 면적은 태스크와 상관없이 계속 늘어야 한다. 앞의 숫자가 task total, 뒤의 숫자가 lifetime total이다.

![task total과 lifetime total의 시간 흐름: 태스크를 시작하면 task total이 0에서 세기 시작해 일시정지 때 3 ha에서 멈춘다. 재개하면 0으로 리셋된 뒤 TC가 보낸 3 ha로 복원돼 완료 때 5 ha가 된다. lifetime total은 태스크 사건과 상관없이 1,195 ha에서 1,200 ha까지 이어진다](/images/study-isobus/47-total-counters-light.png)
![task total과 lifetime total의 시간 흐름: 태스크를 시작하면 task total이 0에서 세기 시작해 일시정지 때 3 ha에서 멈춘다. 재개하면 0으로 리셋된 뒤 TC가 보낸 3 ha로 복원돼 완료 때 5 ha가 된다. lifetime total은 태스크 사건과 상관없이 1,195 ha에서 1,200 ha까지 이어진다](/images/study-isobus/47-total-counters-dark.png)

그림에서 재개 순간을 보자. 클라이언트는 재개를 시작처럼 처리해 task total을 0으로 되돌린다. 그 직후 TC가 일시정지 때 저장해 둔 3 ha를 Value command(3)로 보내 주고, 클라이언트는 거기서부터 이어서 센다. 그래서 완료 때 5 ha가 된다. lifetime total은 이런 사건에 영향을 받지 않는다(1,195 ha 같은 숫자는 예시 값이다).

### task total과 lifetime total

총계(total)는 면적·거리·시간·투입량 같은 누적값이다. 표준은 두 종류를 나눈다.

| 구분 | task total | lifetime total |
|---|---|---|
| TC가 값을 정할 수 있나 | 있다: 태스크를 시작·재개할 때 이어서 셀 값을 내려준다 | 없다: 요청하고 저장만 한다 |
| DDOP 표시 | trigger total + properties settable | trigger total + settable 0 |
| 시작·일시정지·재개 영향 | 받는다 | 받지 않는다. 갱신은 전적으로 클라이언트 몫 |
| 다루는 쪽 | TC는 필수, DL은 선택(다루면 TC와 같은 규칙) | TC·DL 모두 요청·기록 가능 |
| default data set | 넣지 않기를 권장 | 넣지 않기를 권장 |

표의 DL은 Data Logger(TC처럼 값을 기록하지만 제어는 하지 않는 장치, [44장](/study/isobus/44-tc-multi-dl-functionality))다. default data set은 2절의 기본 기록에 넣는 값의 묶음이다.

DPD 바이트로 쓰면 다음과 같다. DPD(DeviceProcessData)는 DDOP(작업기가 자기 구조와 다루는 값을 TC에 알리는 데이터 묶음) 안에서 "이 Element가 이 DDI를 다룬다"고 밝히는 오브젝트다. properties는 성질 비트(bit 1 default set, bit 2 settable, bit 3 control source)이고, trigger는 지원하는 트리거 비트다([46장](/study/isobus/46-tc-commands-pdack) 9절). 아래는 trigger에 시간·거리 간격을 함께 세운 경우다. 표준이 두 총계 모두에 이렇게 하기를 권장한다.

| 종류 | properties | trigger | 예 |
|---|---|---|---|
| task total | `0x02` | `0x13` (total + distance + time) | DDI 116 Total Area |
| lifetime total | `0x00` | `0x13` | DDI 271 Lifetime Total Area |

`0x13`은 `0x10`(total) + `0x02`(distance) + `0x01`(time)이다. task total의 properties `0x02`는 settable 하나만 선 값이다.

### 클라이언트가 지킬 것

"Task totals active"는 TC Status 메시지(TC가 주기적으로 보내는 상태 메시지, [43장](/study/isobus/43-tc-connection))의 비트로, 태스크가 진행 중이라 총계를 세도 된다는 표시다. 클라이언트는 이 비트를 보고 총계를 다룬다.

- 전원을 켠 뒤 "Task totals active" = 1을 처음 받기 전까지 task total을 0으로 둔다. 태스크 시작 전에 요청을 받으면 0을 답한다.
- TC Status의 이 비트가 0→1로 바뀌면 task total을 0으로 리셋하고 세기 시작한다. 1→0으로 바뀌면 세기를 멈춘다. 멈춘 값은 TC·DL이 Request value로 읽어 간다.
- 재개는 시작처럼 처리하되, TC가 보내 준 이전 값에서부터 이어서 센다.
- lifetime total은 태스크 사건과 무관하게 스스로 갱신한다.

### TC가 지킬 것

1. 연결된 모든 클라이언트의 DDOP를 파싱해 task total 목록을 만든다.
2. 태스크가 실행에서 일시정지나 완료로 바뀌면 모든 task total을 요청해 Time 요소에 저장한다.
3. 재개하면 저장해 둔 값을 모든 클라이언트에 되돌려 준다.
4. 예기치 못한 종료에 대비해 정기적으로(예: 1분 간격) 모든 task total을 요청한다. measurement를 써도 된다.
5. 태스크의 가장 최근 Time 요소에 그 태스크의 모든 task total을 담는다. 최근 실행 구간에 없던 클라이언트의 것도 포함한다.

Time 요소는 태스크 파일 안에서 작업 구간 하나의 시작·끝 시각과 그때의 값을 적는 요소다([42장](/study/isobus/42-tc-task)).

lifetime total을 다루는 TC·DL은 1·2·4·5와 같은 책임을 진다. TC Status의 순서도 정해져 있다. 0→1을 알리는 TC Status는 total 값을 설정하기 전에, 1→0을 알리는 TC Status는 최종 total을 요청하기 전에 보낸다. total이 주기적으로 Process Data로 들어오고 있다면 정지 시점의 요청을 생략할 수도 있다. Time 요소와 TimeLog의 XML·바이너리 구조는 [56장](/study/isobus/56-practice-isoxml)과 [57장](/study/isobus/57-practice-binary-files)에서 다룬다.

![task total 처리 타임라인: TC Status로 totals active가 0에서 1이 되면 클라이언트가 total을 0으로 리셋하고, TC가 저장값을 Value command로 복원하고, measurement와 PDACK·초기값이 오가고, 주기 Request value로 수집하다가, 1에서 0이 되면 클라이언트가 measurement를 멈추고 TC가 최종 total을 요청해 Time 요소에 저장하는 흐름](/images/study-isobus/19-task-totals-timeline-light.png)
![task total 처리 타임라인: TC Status로 totals active가 0에서 1이 되면 클라이언트가 total을 0으로 리셋하고, TC가 저장값을 Value command로 복원하고, measurement와 PDACK·초기값이 오가고, 주기 Request value로 수집하다가, 1에서 0이 되면 클라이언트가 measurement를 멈추고 TC가 최종 total을 요청해 Time 요소에 저장하는 흐름](/images/study-isobus/19-task-totals-timeline-dark.png)

그림은 왼쪽 띠의 네 단계(시작·재개, 측정 설정, 주기 수집, 일시정지·완료)로 읽는다. 실선은 TC가, 점선은 클라이언트가 보내는 메시지다.

[45장](/study/isobus/45-tc-process-data-basics) 10절에서 본 대로 totals active 비트가 바뀌는 순간 클라이언트는 그 TC가 건 measurement를 모두 멈춘다. 그래서 재개 뒤에는 measurement를 다시 걸어야 한다.

### 바이트로 보기

| 단계 | 프레임 | 뜻 |
|---|---|---|
| 재개 직후 total 복원 | `03 00 74 00 39 30 00 00` | element 0, DDI 116 = 12,345 m² |
| 일시정지 뒤 요청 | `02 00 77 00 00 00 00 00` | element 0, DDI 119 요청 |
| 응답 | `03 00 77 00 28 23 00 00` | 9,000 s = 2.5 h |

첫 줄을 풀면 이렇다. Byte 1 `03`은 element 0(장치 전체)에 대한 Value command다. Byte 3~4 `74 00`은 DDI `0x0074` = 116(Total Area)이다. 값 `39 30 00 00`은 `0x3039` = 12,345이고 단위는 m²다.

DDI 116이 m², 119가 초 단위라는 것은 2절에서 볼 경운기 DDOP 예시의 DVP 배율에서 거꾸로 읽을 수 있다. DVP(DeviceValuePresentation)는 원시값을 화면에 보일 때 쓰는 배율·오프셋·단위를 정한 DDOP 오브젝트다([49장](/study/isobus/49-ddop-bytes)). 그 예에서 116에 붙은 DVP는 배율 1E-04로 ha를, 119에 붙은 DVP는 배율 2.777778E-04로 hr를 표시한다. 1 ha = 10,000 m², 1 hr = 3,600 s이므로 원시값 단위는 각각 m²와 s다.

아래 코드는 이 표의 프레임, 2절의 default logging 요청 프레임, 경운기 예시 DDOP의 비트 풀이를 검산한다. 주석의 "6.8.4 예 1"은 그 예시가 실린 표준 원문의 조항 번호다.

::: details 파이썬으로 검산해 보기: totals와 default logging
```python
def build_frame(command, element, ddi, value):
    byte1 = ((element & 0xF) << 4) | (command & 0xF)
    return (bytes([byte1, element >> 4]) + ddi.to_bytes(2, "little")
            + value.to_bytes(4, "little", signed=True))


hexs = lambda f: f.hex(" ").upper()

# 재개: TC가 Time 요소에 저장해 둔 total을 element 0으로 되돌려 준다
restore_area = build_frame(3, 0, 0x0074, 12_345)        # DDI 116 Total Area, m2
assert hexs(restore_area) == "03 00 74 00 39 30 00 00"

# 일시정지 뒤 최종 total 요청과 응답
req_time = build_frame(2, 0, 0x0077, 0)                  # DDI 119 Total Time
ans_time = build_frame(3, 0, 0x0077, 9_000)              # 9000 s
assert hexs(req_time) == "02 00 77 00 00 00 00 00"
assert hexs(ans_time) == "03 00 77 00 28 23 00 00"

# default data logging 요청: element 0, DDI DFFF
req_default = build_frame(2, 0, 0xDFFF, 0)
assert hexs(req_default) == "02 00 FF DF 00 00 00 00"

# 6.8.4 예 1의 DPD 속성(C)·트리거(D)를 비트로 풀기
PROPS = {1: "default set", 2: "settable", 4: "control source"}
TRIGS = {1: "time", 2: "distance", 4: "threshold", 8: "on change", 16: "total"}
bits = lambda v, table: [n for b, n in table.items() if v & b]
for ddi, c, d in [(0x0074, 2, 16), (0x0077, 2, 16), (0x008D, 1, 3),
                  (0x0043, 1, 3), (0xDFFF, 0, 31)]:
    print(f"DDI {ddi:5d} props={bits(c, PROPS)} triggers={bits(d, TRIGS)}")

# DVP 배율로 거꾸로 읽는 단위: hr = s * 2.777778E-04, ha = m2 * 1E-04
assert round(9_000 * 2.777778e-04, 2) == 2.50
assert round(12_345 * 1e-04, 2) == 1.23
```
```
DDI   116 props=['settable'] triggers=['total']
DDI   119 props=['settable'] triggers=['total']
DDI   141 props=['default set'] triggers=['time', 'distance']
DDI    67 props=['default set'] triggers=['time', 'distance']
DDI 57343 props=[] triggers=['time', 'distance', 'threshold', 'on change', 'total']
```
:::

::: warning 재개 뒤 총계가 0부터 다시 쌓이는 장애
재개는 클라이언트 입장에서 시작과 같다. 0→1 전이에서 total이 0이 되고, TC가 저장해 둔 값을 Value command로 보내야 거기서부터 이어서 센다. TC가 복원 단계를 빼먹으면 재개 이후의 값만 남는다. 클라이언트가 복원 값을 받고도 0부터 센다면 클라이언트 쪽 위반이다. 로그에서는 0→1 TC Status 바로 뒤에 total DDI(116·119 등)의 Command 3이 해당 element로 나갔는지부터 확인한다.
:::

<small>근거: ISO 11783-10 6.8, 6.8.3, 6.8.3.1, 6.8.3.2, 6.8.4 예 1, B.8.1</small>

## 2. Default data logging: DDI `0xDFFF`로 기본 기록 켜기

이 절은 TC가 기록할 값을 하나하나 지정하지 않고, 클라이언트에게 "기본으로 기록할 값을 알아서 보내라"고 맡기는 방법을 본다.

보통은 FMIS가 태스크 파일에 DataLogTrigger("이 DDI를 이런 조건으로 기록하라"는 요소, 46장)를 적어 DDI를 하나하나 지정한다. Default data logging은 그 대신, 클라이언트가 고른 데이터를 클라이언트가 정한 주기·트리거로 보내게 하는 방법이다. 특수 DDI `0xDFFF`(57343, RequestDefaultProcessData)를 쓴다. 쓰는 경우는 두 가지다.

- 클라이언트의 DPD가 너무 많아 TC가 무엇을 어떤 주기로 받아야 할지 모를 때. 고르는 일을 클라이언트에 맡긴다.
- FMIS가 태스크마다 `DFFF`를 넣어 "로깅을 켜라"는 뜻만 전할 때.

| 항목 | 규칙 |
|---|---|
| 요청 방법 | Request value(Command 2), DDI `0xDFFF` |
| 요청 대상 | 장치의 element 0에서만 |
| DDOP 요건 | DPD를 default set(properties bit 1)으로 지정했다면 DDI `0xDFFF`인 DPD를 하나 넣고 trigger를 `0x1F`로 둔다 |
| 사용 조건 | "Task totals active"가 0일 때 TC는 이 요청을 쓰면 안 된다 |
| 멈추는 방법 | "Task totals active"의 1→0 전이뿐 |
| 권장 관행 | 특정 DPD용 트리거가 없는 태스크에는 `DFFF` DataLogTrigger를 넣어 최소한 default set은 기록되게 한다 |
| 총계 | task·lifetime total은 default set에 넣지 않기를 권장 |

default set은 DPD properties의 bit 1로, "기본 기록에 넣을 값"이라는 표시다. trigger `0x1F`(=31)는 다섯 트리거 비트(`0x01`~`0x10`)를 모두 세운 값이다.

사용 조건은 멈추는 방법에서 나온다. 끌 방법이 비트의 1→0 전이 하나뿐이라, 비트가 0인 동안 켜면 끌 수단이 없다.

요청 프레임은 `02 00 FF DF 00 00 00 00`이다. Byte 3~4 `FF DF`가 낮은 자리부터 실린 `0xDFFF`다. Value 자리의 값은 표준이 정하지 않는다(45장 5절의 Request value처럼 0으로 채웠다).

### 표준 예시 DDOP 읽기: 경운기

ISO 11783-10(TC를 정하는 표준 문서)은 default logging을 설명하면서 경운기(Tiller) DDOP를 XML로 예시한다. DPD의 C 속성(properties)과 D 속성(trigger)을 비트로 풀면 다음과 같다.

| DPD | DDI | C | D | 해석 |
|---|---|---|---|---|
| 2 | `0x0074`(116) "Area" | 2 | 16 | settable + total → task total |
| 3 | `0x0077`(119) "Time ON" | 2 | 16 | settable + total → task total |
| 4 | `0x008D`(141) "Work ON/OFF" | 1 | 3 | default set, 시간·거리 간격 |
| 5 | `0x0043`(67) "Width" | 1 | 3 | default set, 시간·거리 간격 |
| 6 | `0xDFFF` | 0 | 31 | default logging 지원 표시 |

task total 두 개는 default set이 아니고(권장 그대로), 작업 상태와 작업 폭만 default set이다. 이 장치에 `02 00 FF DF …`를 보내면 141과 67이 장치가 정한 방식으로 들어온다. 태스크 쪽에서는 `DLT` 요소(DataLogTrigger의 XML 이름)에 DDI `DFFF`와 방법 31을 적는다. DataLogTrigger의 XML 구조는 [56장](/study/isobus/56-practice-isoxml)에서 다룬다.

<small>근거: ISO 11783-10 6.8.3, 6.8.4 예 1·예 2</small>

## 3. 로그 레코드 규칙과 Log Count(DDI `0x0093`) (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절은 TC가 따로따로 도착하는 값을 TimeLog의 한 줄(레코드)로 묶는 규칙을 본다.

DDI마다 송신 주기와 응답 지연이 다르다. 그래서 TC는 들어오는 값을 어느 레코드(TimeLog 한 줄)에 넣을지 규칙이 필요하다. 아래의 TimeLog 인스턴스는 TimeLog 레코드 한 줄을 말한다.

1. 시간·위치는 TimeLog 인스턴스당 최대 한 번 기록한다.
2. process data 값도 TimeLog 인스턴스당 최대 한 번이다. TC 성능 때문에 낮은 주기로만 기록할 수 있다면 어떤 값이 남을지는 TC 설계에 달렸다.
3. TC가 가장 자주 오는 DDI의 속도를 따라갈 수 있으면, 그 DDI 값이 올 때마다 새 레코드를 연다. 그 사이에 온 다른 값은 현재 레코드에 넣는다.
4. 받은 값은 최대 한 번만 기록한다. 다음 레코드에 새 값이 없으면 그 DDI는 비워 둔다.

이 규칙대로면 한 레코드 안의 값들은 최대 레코드 간격만큼 시간이 어긋날 수 있다. 여러 DDI를 반드시 한 묶음으로 남기려면 클라이언트가 Log Count(DDI `0x0093`, 147)를 가장 높은 반복률로 보낸다. 묶음을 보내기 전에 항상 새 레코드가 열리므로, FMIS는 Log Count 값으로 같은 묶음을 가려낸다.

아래 코드는 규칙 3을 따라 레코드를 자르는 함수와 표준의 두 예를 검산한다. 주석의 "6.8.4 규칙 b·c·d"는 위 목록의 규칙 2·3·4이고, "예 3·예 4"는 표준 원문에 실린 예의 번호다.

::: details 파이썬으로 검산해 보기: 레코드 자르기
```python
def cut_records(stream, leader):
    """leader DDI가 도착할 때마다 새 레코드를 연다(6.8.4 규칙 c)."""
    records, current = [], None
    for ddi, value in stream:
        if ddi == leader or current is None:
            current = {}
            records.append(current)
        if ddi in current:            # 규칙 b: 레코드당 DDI 값은 한 번만
            continue
        current[ddi] = value          # 규칙 d: 받은 값은 한 번만 기록된다
    return records


# 6.8.4 예 3: A가 가장 자주 오는 DDI
ex3 = [("A", 1), ("B", 1), ("A", 2), ("C", 1), ("A", 3), ("A", 4)]
assert cut_records(ex3, "A") == [{"A": 1, "B": 1}, {"A": 2, "C": 1}, {"A": 3}, {"A": 4}]

# 6.8.4 예 4: Log Count(DDI 0x0093)를 맨 앞에 보내 묶음을 만든다
LC = 0x0093
ex4 = [(LC, 1), ("A", 1), ("B", 1), ("C", 1), ("D", 1),
       (LC, 2), ("A", 2), ("D", 2), ("B", 2), ("C", 2),
       (LC, 3), ("D", 3), ("B", 3), ("C", 3), ("A", 3)]
for record in cut_records(ex4, LC):
    print(record)
assert all(set(r) == {LC, "A", "B", "C", "D"} for r in cut_records(ex4, LC))
```
```
{147: 1, 'A': 1, 'B': 1, 'C': 1, 'D': 1}
{147: 2, 'A': 2, 'D': 2, 'B': 2, 'C': 2}
{147: 3, 'D': 3, 'B': 3, 'C': 3, 'A': 3}
```
:::

출력의 세 레코드는 모두 Log Count(147)로 시작하고 A~D 네 값을 하나씩 담는다. 값이 도착한 순서가 달라도 묶음이 깨지지 않는다.

TimeLog 바이너리 파일 구조는 [57장](/study/isobus/57-practice-binary-files)과 [Part 10 정리](/study/isobus/appendix-iso-part10)를 본다.

<small>근거: ISO 11783-10 6.8.4 예 3·예 4</small>

## 4. 위치에 따라 setpoint 보내기: site-specific 제어

이 절은 TC가 처방 맵의 목표값을 언제, 어느 Element에 보내는지 정하는 규칙을 본다. 밭의 위치마다 다른 양을 뿌리는 제어를 site-specific(위치별) 제어라고 부른다.

TC는 태스크 데이터의 지오메트리(처방 맵의 도형 정보)를 실제 위치와 맞춰 Process Data 송신 시점을 정한다. 45장 11절에서 본 "새 처리 구역(TreatmentZone)에 들어갈 때 setpoint를 보낸다"는 규칙의 세부는 다음과 같다.

- 지오메트리는 grid cell(바둑판처럼 나눈 칸) 또는 polygon(꼭짓점을 이어 둘러싼 다각형)이고, 고유 식별자를 붙인다. 둘 다 setpoint 값이 연결된 TreatmentZone을 가리킨다.
- polygon이 겹치면 TC는 그 위치의 바깥(exterior) polygon 정의를 쓴다. 안쪽 경계는 바깥 polygon의 구멍이다.
- polygon 방식은 제품·가변 setpoint 종류마다 polygon 세트를 따로 둔다. 이 세트 하나가 variable rate layer(가변 살포 층)다. polygon으로 정의한 TreatmentZone에는 ProcessDataVariable(구역의 목표값 하나)을 하나만 넣는다. 그래서 레이어 하나에는 가변 rate가 최대 하나다.
- setpoint를 보낼 때 TC는 레이어의 ProcessDataVariable에 setpoint DPD가 할당된 device element마다, 그 element가 레이어의 어느 TreatmentZone 안에 있는지 판정한다.
- grid 방식은 태스크당 Grid 요소가 하나이고, 셀 정의는 별도 바이너리 파일에 담는다. 파일 구조는 [57장](/study/isobus/57-practice-binary-files)에서 다룬다.

### 위치에 지연을 더한다

수도꼭지를 틀어도 긴 호스 끝에서는 물이 조금 늦게 나온다. 살포기도 목표값을 받은 뒤 실제 살포량이 바뀌기까지 시간이 걸리고, 그동안 기계는 앞으로 간다. 그래서 TC는 그만큼 앞의 위치에 맞는 setpoint를 미리 보낼 수 있다.

표준은 TC가 "클라이언트 element의 위치를 grid에서 찾아 그 클라이언트의 동작 지연과 결합해" 데이터를 보낸다고 설명한다. 그 지연을 DDOP로 알리는 DDI가 Physical Setpoint Time Latency(142)다.

- TC가 위치 갱신을 받고 rate 변경 명령을 보낸다. rate가 바뀌기 시작하는 시점을 T2, 바뀜이 끝나는 시점을 T4라 하면 T4−T2(ms)가 클라이언트가 보고하는 142 값이다.
- 보정하는 TC는 T2에 받은 위치를 T4 시점의 추정 위치로 옮기고, 그 위치의 setpoint를 보낸다.
- Physical Actual Time Latency(143)가 있으면 TC·FMIS가 맵 위 실제 값의 위치를 보정하는 데 쓴다. 143은 음수일 수 있지만 142는 양수만 가능하다.

예를 들어(예시 값) 10 km/h(약 2.78 m/s)로 달리고 142가 400 ms면, TC는 약 1.11 m 앞 위치의 setpoint를 미리 보낸다. 2.78 m/s × 0.4 s ≈ 1.11 m다.

### 순서 규칙: Prescription Control State(DDI 158)

Prescription Control State(158)는 처방에 따른 rate 제어를 켜고 끄는 상태 값이다. 붐에 setpoint DPD가 있으면 같은 레벨에 158도 있어야 하고, 이 DPD는 settable이면서 on change를 지원해야 한다. 메시지 순서도 정해진다.

1. 태스크가 멈추면 클라이언트는 스스로 158을 DISABLED/OFF로 둔다.
2. TC는 rate 값을 보내기 전에 158을 ENABLED/ON으로 설정한다.
3. ENABLED/ON을 받은 클라이언트는 대응하는 setpoint를 정해 둔 안전 값으로 리셋한다.
4. TC는 on change measurement로 158의 변화를 받는다.

섹션 제어의 Section Control State(DDI 160)도 같은 4단계 규칙을 따른다. ENABLED/ON 같은 상태가 어떤 정수인지는 ISO 11783-10이 아니라 ISOBUS Data Dictionary(7절)가 정한다. DDOP 쪽 배치는 [50장](/study/isobus/50-ddop-commands-design)에서 본다.

<small>근거: ISO 11783-10 6.8, 6.8.1, F.3.4.4, F.3.4.6, F.3.5.3</small>

## 5. Peer Control: 다른 기계가 정한 값으로 제어하기

이 절은 TC가 아닌 다른 기계가 setpoint를 정해 작업기에 직접 넘기는 방법을 본다. 달리면서 재는 센서와 살포기를 짝지을 때 쓴다.

### 사례: 작물 센서가 살포량을 정한다

트랙터 앞에 작물의 생육 상태를 재는 센서를 달고, 뒤에 액체 비료 살포기를 끈다고 하자. 처방 맵은 작업 전에 만든 것이라 지금 지나가는 작물의 상태를 반영하지 못한다. 센서가 주행하면서 "여기는 210 L/ha"를 정해 살포기의 rate controller(살포량 제어기)에 바로 넘기면 좋다. 센서가 처방 맵의 값을 받아 고친 뒤 넘기는 경우도 있다. 이렇게 한 기계가 정한 값을 다른 기계가 setpoint로 받게 하는 것이 Peer Control이다.

Peer control은 어떤 CF(Control Function, 버스에서 주소 하나를 쓰는 제어 기능)가 다른 CF의 setpoint 공급원(source)이 되게 하고, 그 할당을 TC가 정하고 기록하는 장치다(ISO 11783-10 버전 4). 작업 계획 때는 정할 수 없고 실행 중에 정해지는 setpoint(예를 들어 주행하며 재는 센서가 직접 rate를 정하거나 처방 맵 rate를 고치는 경우)를 표준 방식으로 rate controller에 넘기려고 만들었다.

![Peer Control의 세 역할: TC가 센서 CF(setpoint value source, DDI 1 control source)에 Assign Transmitter, 살포기 rate controller(setpoint value user, DDI 1 settable)에 Assign Receiver를 보내 짝을 짓고, 둘은 Ack로 답한다. 그 뒤 센서 CF가 살포기에 Value command로 setpoint를 직접 보낸다](/images/study-isobus/47-peer-control-roles-light.png)
![Peer Control의 세 역할: TC가 센서 CF(setpoint value source, DDI 1 control source)에 Assign Transmitter, 살포기 rate controller(setpoint value user, DDI 1 settable)에 Assign Receiver를 보내 짝을 짓고, 둘은 Ack로 답한다. 그 뒤 센서 CF가 살포기에 Value command로 setpoint를 직접 보낸다](/images/study-isobus/47-peer-control-roles-dark.png)

역할은 셋이다.

- setpoint value source(센서 CF): 값을 정해 보내는 쪽
- setpoint value user(rate controller): 받은 값을 setpoint로 써서 제어하는 쪽
- TC: 둘을 짝지어 주고(할당), 그 할당을 태스크에 기록하는 쪽

짝이 지어진 뒤에는 source가 user에게 Value command(3)를 직접 보낸다. TC를 거치지 않으니 전달이 빠르고, user는 받은 값이 할당된 source에서 왔는지 확인할 수 있다.

### 두 CF의 DDOP 요건

| 역할 | DPD 요건 |
|---|---|
| setpoint value user(rate controller) | 그 DDI의 DPD properties가 settable(bit 2) |
| setpoint value source(센서 CF) | 같은 DDI의 DPD properties가 control source(bit 3, 버전 4) |

settable과 control source는 함께 설 수 없다. source도 settable DPD를 따로 가질 수 있는데, 이것이 Map Overlay다. TC가 보낸 위치 기반 setpoint를 source가 자기 알고리즘으로 고쳐 user에게 넘긴다. 한 장치가 같은 DDI의 source와 user를 겸하면 두 DPD를 한 device element에서 참조하면 안 되고 element를 둘로 나눠야 한다. 두 CF 모두 DDOP를 올리고 활성화한 TC 클라이언트여야 한다.

### 운영 규칙

| 항목 | 규칙 |
|---|---|
| 할당 시점 | 태스크가 inactive → active로 바뀔 때마다, 외부 source에 할당된 device element마다 |
| 응답 기한 | 250 ms. 응답이 없으면 거부로 본다(하위 호환) |
| source 송신 | 태스크 active 동안 1초 주기 + on change(최대 5 Hz) |
| 수신 타임아웃 | 3 s 동안 setpoint가 없으면 user는 TC 통신을 잃은 것처럼 대응 |
| TC 통신 상실 | TC Status로 판단한다. 양쪽 모두 태스크가 inactive가 된 것처럼 대응 |
| 태스크 inactive | user는 setpoint 거부, source는 송신 중지, 양쪽 모두 할당 취소 |
| 할당 없음·무효 | user는 태스크 active 동안 TC의 setpoint만 받는다 |
| 해제 | task totals가 active → inactive가 되면 끊긴다. 그 전에 끊으려면 같은 필드로 Unassign 모드를 보낸다 |
| 기록 | 할당은 Task 요소의 ControlAssignment(CAT)로 저장해 같은 태스크를 다시 시작할 때 쓰고 FMIS도 참조한다 |

표의 "하위 호환"은 이런 뜻이다. peer control을 모르는 옛 버전 장비는 할당 메시지에 답하지 않는다. 그래서 답이 없으면 거부로 처리해야 옛 장비와 섞여도 문제가 생기지 않는다. ControlAssignment(CAT)는 태스크 파일에 할당 내용을 적는 요소다.

![Peer control 할당 절차: 태스크가 active가 되면 TC가 source에 Assign Transmitter(mode 3), user에 Assign Receiver(mode 0)를 보내고, 각자 250 ms 안에 Ack(mode 5, 2)로 답한 뒤 source가 user에게 Value command를 1 Hz와 on change로 직접 보내며, 3 s 미수신이나 태스크 inactive에서 할당이 풀리는 흐름](/images/study-isobus/19-peer-control-sequence-light.png)
![Peer control 할당 절차: 태스크가 active가 되면 TC가 source에 Assign Transmitter(mode 3), user에 Assign Receiver(mode 0)를 보내고, 각자 250 ms 안에 Ack(mode 5, 2)로 답한 뒤 source가 user에게 Value command를 1 Hz와 on change로 직접 보내며, 3 s 미수신이나 태스크 inactive에서 할당이 풀리는 흐름](/images/study-isobus/19-peer-control-sequence-dark.png)

그림은 위에서부터 할당, 응답, 직접 전송, 해제 순서다. 그림의 DETx·DETy는 source와 user 쪽 element, "9 / mode 3"은 command 9의 mode 값 3이라는 뜻이다(6절).

<small>근거: ISO 11783-10 6.8.5, F.3.3</small>

## 6. Peer Control 메시지의 바이트 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절은 5절의 할당 메시지(command 9, Peer Control Assignment)를 바이트 단위로 연다.

### 메시지 배치

TC → CF 할당 메시지는 14바이트라 TP(Transport Protocol, 8바이트보다 긴 데이터를 여러 프레임으로 나눠 보내는 절차, [15장](/study/isobus/15-tp-bam-cmdt))로 나가고, CF → TC 응답은 8바이트 단일 프레임이다.

| 위치 | 내용 |
|---|---|
| Byte 1 bit 4~1 | `1001` (command 9) |
| Byte 1 bit 8~5, Byte 2 | 받는 CF 쪽 element number |
| Byte 3~4 | DDI |
| Byte 5 bit 4~1 | control assignment mode |
| Byte 5 bit 8~5, Byte 6 | Destination Element number(user 쪽 element, 12비트) |
| Byte 7~14 | 상대 CF의 NAME(8바이트) |

| mode | 이름 | 방향 |
|---|---|---|
| 0 | Assign Receiver | TC → user |
| 1 | Unassign Receiver | TC → user |
| 2 | Receiver Ack | user → TC |
| 3 | Assign Transmitter | TC → source |
| 4 | Unassign Transmitter | TC → source |
| 5 | Transmitter Ack | source → TC |
| 6~15 | 예약 | |

- Destination Element number는 Transmit 계열에서만 쓴다. source가 user에게 Value command를 보낼 때 실을 user 쪽 element 번호다. Receiver 계열에서는 `FFF`로 채운다.
- DDI 자리가 하나뿐인 이유는 source와 user의 DDOP에서 같은 DDI여야 TC가 할당할 수 있기 때문이다.
- 응답은 같은 메시지에서 mode만 Ack 값으로 바꾸고, Byte 5 상위 니블을 `F`, Byte 6~8을 `FF`로 채운 단일 프레임이다.
- 거부는 PDACK로 하고, 오류 비트로 사유를 밝힌다.
- 한 CF에는 응답이나 타임아웃 전까지 할당·해제 메시지를 하나만 보낸다.
- 상대를 NAME으로 지정하므로, 상대 SA가 새 address claim으로 바뀌면 그 변화를 따라가는 것은 할당받은 CF의 책임이다.

NAME은 장치마다 고유한 64비트 이름이고, SA(Source Address)는 그 장치가 버스에서 쓰는 1바이트 주소다. 주소는 address claim(주소를 정하는 절차)으로 바뀔 수 있어서 상대를 바뀌지 않는 NAME으로 가리킨다([12장](/study/isobus/12-j1939-address-name)).

### 바이트로 보기

source CF의 element 2가 내는 DDI 1(Setpoint Volume Per Area)을 user CF의 element 3이 받게 하는 할당이다. 두 NAME은 예시 값이다.

```
TC -> source    29 00 01 00 33 00 C7 FF 3F 07 00 84 0C A0   Assign Transmitter, 목적지 element 3, user NAME (14B, TP)
source -> TC    29 00 01 00 F5 FF FF FF                      Transmitter Ack
TC -> user      39 00 01 00 F0 FF 01 00 40 00 00 8E 10 A0   Assign Receiver, 목적지 FFF, source NAME (14B, TP)
user -> TC      39 00 01 00 F2 FF FF FF                      Receiver Ack
source -> user  33 00 01 00 20 0B 20 00                      Value command, element 3, 210 L/ha
```

첫 프레임 Byte 5의 `33`은 상위 니블 3(목적지 element 하위 4비트)과 하위 니블 3(Assign Transmitter)이 우연히 같아서 생긴 값이다. NAME 8바이트는 Address Claimed 메시지처럼 LSB부터 싣는다. NAME은 수(number)로 다룰 수 있게 필드가 배열돼 있고, 다바이트 수치는 LSB부터 보내기 때문이다. 마지막 줄의 값 `20 0B 20 00`은 `0x200B20` = 2,100,000이고, 45장의 분해능대로 210 L/ha다.

아래 코드는 위 다섯 줄을 조립해 검산한다. `USER_NAME` 주석의 "Part 10 D.19 예의 값"은 표준 원문의 예시에 나오는 NAME을 가져왔다는 뜻이다.

::: details 파이썬으로 검산해 보기: peer control assignment
```python
def element_bytes(low_nibble_owner, element):
    return ((element & 0xF) << 4) | low_nibble_owner, element >> 4


def assignment(element, ddi, mode, dest_element, name):
    b1, b2 = element_bytes(0x9, element)
    b5 = ((dest_element & 0xF) << 4) | mode
    b6 = (dest_element >> 4) & 0xFF
    return (bytes([b1, b2]) + ddi.to_bytes(2, "little") + bytes([b5, b6])
            + name.to_bytes(8, "little"))


def assignment_ack(element, ddi, ack_mode):
    b1, b2 = element_bytes(0x9, element)
    return bytes([b1, b2]) + ddi.to_bytes(2, "little") + bytes([0xF0 | ack_mode, 0xFF, 0xFF, 0xFF])


hexs = lambda f: f.hex(" ").upper()
USER_NAME = 0xA00C8400073FFFC7       # 예시 NAME(Part 10 D.19 예의 값)
SRC_NAME = 0xA0108E0000400001        # 예시 NAME

# TC -> source: source의 element 2, DDI 1을 user의 element 3으로 보내라(Assign Transmitter)
to_src = assignment(element=2, ddi=1, mode=3, dest_element=3, name=USER_NAME)
assert len(to_src) == 14             # 8바이트 초과 -> TP
assert hexs(to_src) == "29 00 01 00 33 00 C7 FF 3F 07 00 84 0C A0"

# TC -> user: user의 element 3, DDI 1이 source에서 setpoint를 받는다(Assign Receiver)
to_user = assignment(element=3, ddi=1, mode=0, dest_element=0xFFF, name=SRC_NAME)
assert hexs(to_user) == "39 00 01 00 F0 FF 01 00 40 00 00 8E 10 A0"

# 응답: mode만 Ack로 바꾸고 Byte 5 상위 니블 F, Byte 6~8 FF, 단일 프레임
assert hexs(assignment_ack(2, 1, 5)) == "29 00 01 00 F5 FF FF FF"
assert hexs(assignment_ack(3, 1, 2)) == "39 00 01 00 F2 FF FF FF"

# 할당 뒤 source가 user에게 직접 보내는 Value command (210 L/ha)
b1, b2 = element_bytes(0x3, 3)
direct = bytes([b1, b2]) + (1).to_bytes(2, "little") + (2_100_000).to_bytes(4, "little", signed=True)
assert hexs(direct) == "33 00 01 00 20 0B 20 00"
print(hexs(to_src)); print(hexs(to_user)); print(hexs(direct))
```
:::

실행하면 모든 `assert`를 통과하고 위 표의 첫째, 셋째, 다섯째 줄이 그대로 출력된다.

<small>근거: ISO 11783-10 B.4, 6.8.5, ISO 11783-5 4.3.2, ISO 11783-7 3.3.1</small>

## 7. ISO 11783-11: DDI 사전은 무엇을 정하나

이 절은 지금까지 쓴 DDI 번호들이 어디서 정해지고, TC 구현이 그 사전에 무엇을 기대는지 본다.

ISO 11783-11:2011(DDI 목록을 정하는 표준 문서, 이하 Part 11)은 본문이 3쪽뿐이다. 범위는 "Part 10(ISO 11783-10, TC를 정하는 표준 문서)의 Process Data 메시지에 쓰는 데이터 요소의 식별자"이고, 실제 목록은 싣지 않는다. 대신 온라인 ISOBUS Data Dictionary(isobus.net)를 필수 참조 문서로 지정하고, Process Data 메시지로 보내는 가변 데이터는 이 사전 정의를 따라야 한다고 정한다. 사전 유지관리는 ISO/TMB(ISO 기술관리이사회)가 지명한 maintenance agency(유지관리 기관)인 VDMA(독일 기계공업협회)가 맡는다. 절별 요약은 [Part 11 정리](/study/isobus/appendix-iso-part11)에 있다.

### 사전 항목(DDE)이 갖출 것

Part 10은 사전 항목 하나를 data dictionary entity(DDE)라 부르고 "식별자·정의·값 범위·분해능·단위를 기술한 것"으로 정의한다. Part 11도 같은 다섯 속성을 요구한다.

| 속성 | 구현에서 쓰는 곳 |
|---|---|
| identification number | 메시지 Byte 3~4, DPD·DPT의 DDI 필드 |
| definition | 어떤 물리량인지, Setpoint·Actual·Default 중 무엇인지 |
| range | PDACK bit 7(DDI 정의 위반) 판정 기준 |
| resolution | 원시 정수와 물리값 사이 변환(45장 5절) |
| units | 표시 단위, DVP 배율 계산의 출발점 |

Part 10은 process data variable도 "범위·분해능·단위 속성으로 이뤄진다"고 정의한다. 메시지 안에서 DDI는 2바이트(LSB 먼저, SPN 5201), 값은 부호 있는 4바이트(SPN 5202)이고, 분해능과 범위는 DDE를 따른다. SPN(Suspect Parameter Number)은 메시지 안의 값 하나하나에 붙인 번호다.

### Part 10이 사전에 맡겨 둔 것

다섯 속성 말고도 Part 10은 몇 가지 판단을 사전에 넘긴다.

- variable당 초당 10개 상한의 예외(burst)가 허용되는 DDI. 예외는 사전에 명시돼야 한다([45장](/study/isobus/45-tc-process-data-basics) 9절).
- 어떤 DDI가 총계인지. TC-BAS·LOG 서버는 사전에 총계로 정의된 DDI를 모두 지원해야 한다.
- TC-GEO 서버는 사전의 모든 DDI를 지원해야 한다.
- Prescription Control State(158)와 Section Control State(160)의 값 정의. Part 10의 기능별 지침은 사전 정의에 동작 규칙만 더한다(4절).

TC-BAS, TC-GEO, TC-LOG는 TC가 지원하는 기능 묶음의 이름이다. 차례로 기본 기능(총계 기록), 위치 기반 제어, 데이터 기록을 뜻한다([44장](/study/isobus/44-tc-multi-dl-functionality)).

사전이 바뀌면 TC 서버의 적합성 범위도 바뀐다는 뜻이다. TC 서버를 만든다면 사전 내보내기 파일을 버전으로 관리하고, 모르는 DDI의 값은 버리지 말고 원시값 그대로 기록하는 편이 안전하다(추론).

### Part 10이 직접 쓰는 특수 값

| 값 | 이름 | 쓰는 곳 |
|---|---|---|
| DDI `0xDFFE`(57342) | ParameterGroupNumberValue | 다른 PGN의 비트 구간을 로깅할 때 DataLogDDI에 넣는다(42장) |
| DDI `0xDFFF`(57343) | RequestDefaultProcessData | default data logging(2절) |
| DDI `0x0093`(147) | Log Count | 로그 묶음 표시(3절) |
| DDI `0xFFFF` | not available | PDACK·Status의 "해당 없음"(46장) |
| element `0xFFF` | not available | 같은 용도(46장) |

독점(proprietary, 제조사가 자체로 정한) DDI는 Part 10이 "독점 DDI 값 범위"라는 말로 언급하지만, 그 범위의 숫자는 Part 10과 Part 11 어디에도 없다. 온라인 사전에서 확인해야 한다(확인 필요). 범위가 어디든 메시지 형식은 46장에서 본 메시지 형식 그대로다.

::: warning DDI 범위 표기가 두 곳에서 다르다
Part 10의 DDOP 오브젝트 정의는 DPD의 DDI 필드를 0~65535로, 메시지 정의는 메시지 DDI의 데이터 범위를 0~65255로 적는다. 파서가 65255보다 큰 DDI를 버리면 not available(`0xFFFF`)을 담은 PDACK·Status까지 버리게 된다. 필드는 2바이트 전체(0~65535)로 받고, 의미 판정은 사전과 위 특수 값 표로 하는 편이 안전하다(추론).
:::

<small>근거: ISO 11783-11 1, 2, 4.1, 4.2, ISO 11783-10 3.3, 3.14, 6.3, 6.8 a), B.1.1, B.3.3, B.3.4, Table A.3, D.17, F.2.1, F.2.2, F.2.4, F.3.4.4, F.3.5.3</small>

::: tip 핵심 정리
- task total은 태스크마다 0에서 세고, 일시정지 때 TC가 받아 저장했다가 재개 때 되돌려 준다. lifetime total은 태스크와 상관없이 계속 센다.
- default data logging은 element 0에 DDI `0xDFFF`를 Request value로 보내 켜고, "Task totals active" 1→0 전이로만 꺼진다.
- TC는 Element가 새 처리 구역에 들어갈 때 setpoint를 보내고, 기계의 반응 지연(DDI 142)만큼 앞 위치의 값을 미리 보낼 수 있다.
- Peer Control은 TC가 source와 user를 짝지어 주면 source가 user에게 setpoint를 직접 보내는 방식이다(버전 4).
- DDI의 이름·범위·분해능·단위는 온라인 DDI 사전이 정하고, ISO 11783-11은 그 사전을 따르라고 정한다.
:::

::: details 확인 문제
1. task total과 lifetime total 가운데 TC가 값을 설정할 수 있는 것은 어느 쪽이고, 왜 그래야 하는가?
2. 태스크가 진행 중이지 않을 때("Task totals active" = 0) TC가 `02 00 FF DF 00 00 00 00`을 보내면 안 되는 이유는 무엇인가?
3. Peer Control 할당이 끝난 뒤 source가 3초 동안 setpoint를 보내지 않았다. user는 어떻게 대응하는가?
4. (진단) 일시정지했다가 재개한 태스크의 Total Area가 재개 시점부터 0에서 다시 쌓였다. 버스 로그에서 무엇을 어떤 순서로 확인하는가?

<strong>답 가이드</strong>

1. task total이다. 태스크를 재개할 때 TC가 저장해 둔 값을 되돌려 줘야 이어서 셀 수 있기 때문이다. 그래서 task total DPD는 settable이고, lifetime total DPD는 settable이 아니다.
2. default data logging을 끄는 방법은 "Task totals active"의 1→0 전이뿐이다. 비트가 0일 때 켜면 끌 수단이 없다.
3. TC와의 통신을 잃은 것처럼 대응한다. 운영 규칙 표를 이어 읽으면, 태스크가 inactive가 된 것처럼 setpoint를 거부하고 할당을 취소하는 것이다.
4. ① 재개 때 totals active 0→1 TC Status가 나갔는지 ② 그 직후 TC가 저장해 둔 Total Area를 Command 3(DDI 116 = `0x0074`)으로 해당 element에 보냈는지 ③ 이후 클라이언트가 보고한 값이 복원 값에서 이어지는지 ④ 일시정지 때 1→0 TC Status 뒤에 Request value로 최종값을 받아 Time 요소에 저장했는지. ②가 없으면 TC 쪽, ②가 있는데 0부터 세면 클라이언트 쪽 문제다.
:::

## 다음 챕터

- 다음: [48장 DDOP 기초: 장치가 자기를 소개하는 방법](/study/isobus/48-ddop-basics)
