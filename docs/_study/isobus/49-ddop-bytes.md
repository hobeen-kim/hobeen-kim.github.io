---
title: "DDOP 바이트 구성"
description: "실제 7섹션 붐 살포기의 DDOP를 설계하고, 다섯 가지 오브젝트 레코드가 바이트열에 어떻게 놓이는지 읽은 뒤, 작은 DDOP를 바이트 하나하나 조립하고 거꾸로 풀어 본다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, TaskController, TC, DDOP, DeviceDescription, ObjectPool]
prev: /study/isobus/48-ddop-basics
next: /study/isobus/50-ddop-commands-design
---

# DDOP 바이트 구성

::: info 학습 목표
- 실제 7섹션 붐 살포기의 DDOP가 어떤 DET와 DDI로 이루어지는지 읽을 수 있다.
- 섹션의 Y 오프셋을 계산하고, 섹션 폭은 DPT로, 살포량은 DPD로 두는 이유를 설명할 수 있다.
- 다섯 가지 오브젝트 레코드(DVC, DET, DPD, DPT, DVP)의 바이트 배치를 읽을 수 있다.
- structure label, localization label, extended structure label을 구분할 수 있다.
- 작은 DDOP를 바이트 단위로 조립하고 거꾸로 풀 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [48장 DDOP 기초](/study/isobus/48-ddop-basics), [45장 TC 프로세스 데이터 기초](/study/isobus/45-tc-process-data-basics)
- 이 장에서 처음 나오는 말
  - 레코드: 오브젝트 하나를 바이트로 적은 덩어리
  - Table ID: 레코드 맨 앞 세 글자. 오브젝트 종류를 나타낸다(`DVC`, `DET` 등)
  - 리틀 엔디언: 여러 바이트로 된 수를 낮은 자리 바이트부터 싣는 방식
  - UTF-8: 글자를 바이트로 바꾸는 규칙. 영문과 숫자는 1바이트, 한글은 3바이트다
  - 오프셋(offset): 기준점에서 떨어진 거리
  - Condensed Work State: 여러 섹션의 켜짐·꺼짐 상태를 값 하나에 모은 것
:::

48장에서 쓴 자기소개서는 아직 말로 된 초안이다. TC에게 보내려면 칸과 순서가 정해진 서식에 맞춰 바이트로 옮겨 적어야 한다. 신분증에 이름, 생년월일, 주소 칸이 늘 같은 자리에 있듯, DDOP 레코드도 칸의 순서와 크기가 정해져 있다. 이 장에서는 먼저 실제 7섹션 살포기의 DDOP를 설계하고, 다섯 레코드의 칸 배치를 읽은 뒤, 48장의 작은 예제를 바이트 하나하나 조립한다.

## 1. 실물 예시: 7섹션 붐 살포기

[48장 4절](/study/isobus/48-ddop-basics)의 3섹션 예시는 살포량·섹션 ON/OFF만 다루는 최소 구성이었다. 실제 붐 살포기는 총계 보고(TC-BAS)·섹션 제어(TC-SC)·기하 정보(위치와 크기)까지 함께 갖춘다. TC-BAS와 TC-SC는 TC 기능성(TC가 제공하는 기능 묶음)의 이름이다. TC-BAS는 작업 총계를 기록하는 기본 기능이고, TC-SC는 섹션을 위치에 맞춰 자동으로 켜고 끄는 기능이다([41장](/study/isobus/41-tc-basics)).

이 절은 12m 붐에 1,714mm 폭 섹션 7개를 단 살포기의 DDOP를 설계한다. 값은 [Part 10 부록](/study/isobus/appendix-iso-part10)과 [DDI 부록](/study/isobus/appendix-ddi)에서 확인한 것만 쓴다. Part 10은 ISO 11783-10, 곧 TC와 작업기의 데이터 교환을 정하는 표준 문서다.

### DDOP 계층 구조

Device 아래 루트 DET(Element 0) 하나를 두고, 루트 아래에 커넥터(트랙터 히치 연결점, type 6)·빈(약액 탱크, type 3)·붐(Function, type 2)을 형제로 둔다. 그리고 붐 아래에 섹션(type 4) 7개를 매단다. Section의 Element Number는 <strong>기계 좌→우 순으로 증가</strong>시키는 것이 권장 규칙이므로, 11~17을 왼쪽에서 오른쪽으로 배정한다.

아래 나무 그림은 들여쓰기가 계층이다. 각 줄은 오브젝트 종류와 type, Element Number, Object ID 순으로 적었다.

```
DVC Device                                        Object ID 0
└─ DET type=1 device            Element 0         Object ID 2
   ├─ DET type=6 connector      Element 1         Object ID 3
   ├─ DET type=3 bin            Element 2         Object ID 4
   └─ DET type=2 function(붐)   Element 3         Object ID 5
      ├─ DET type=4 section 1   Element 11        Object ID 6
      ├─ DET type=4 section 2   Element 12        Object ID 7
      ├─ DET type=4 section 3   Element 13        Object ID 8
      ├─ DET type=4 section 4   Element 14        Object ID 9
      ├─ DET type=4 section 5   Element 15        Object ID 10
      ├─ DET type=4 section 6   Element 16        Object ID 11
      └─ DET type=4 section 7   Element 17        Object ID 12
```

이 배치는 다음 규칙을 따른다. "Function이 붐인 경우 actual/setpoint 값·X·Y offset·maximum working width는 모두 그 Function 안에 두고, 루트는 actual work state 속성 외의 actual/setpoint 값을 가지면 안 된다." 그래서 살포량·섹션 상태 관련 DPD는 전부 붐(Element 3) 아래에 몰려 있고, 루트(Element 0)에는 총계만 남는다.

### 레벨별 DPD·DPT

레벨은 나무의 층을 말한다. 표 읽는 법: Properties 열의 settable은 속성 바이트의 bit 2를 세웠다는 뜻이고, "(읽기 전용)"은 속성 비트를 하나도 세우지 않았다는 뜻이다. Trigger 열은 트리거 바이트에서 세운 비트다(48장 5절).

<strong>Device 레벨(Element 0)</strong>: 총계만 붙는다. TC-BAS는 "TC 클라이언트는 총계의 부분집합만 제공해도 되지만 최소한 DDI 119(total time)는 제공해야 한다"고 요구하므로 DDI 119는 필수다.

| Object ID | DDI | 이름 | 타입 | Properties | Trigger |
|---|---|---|---|---|---|
| 13 | 119 | Effective Total Time | DPD | settable | total, time interval |
| 14 | 116 | Total Area | DPD | settable | total |
| 15 | 117 | Total Distance | DPD | settable | total |

task total DDI(태스크 동안의 누적값)는 "trigger method total + property settable"을 함께 세우는 것이 일반 규칙이다. TC가 태스크를 다시 시작할 때 이어서 셀 시작값을 지정할 수 있어야 하기 때문이다([47장](/study/isobus/47-tc-totals-logging-peer)). DDI 119에만 time interval 트리거가 추가로 요구된다.

<strong>붐(Function) 레벨(Element 3)</strong>

| Object ID | DDI | 이름 | 타입 | Properties | Trigger | 비고 |
|---|---|---|---|---|---|---|
| 16 | 1 | Setpoint Volume Per Area | DPD | settable | - | TC→작업기, 살포량 목표 |
| 17 | 2 | Actual Volume Per Area | DPD | (읽기 전용) | on change | 작업기→TC, 실제 살포량 |
| 18 | 141 | Actual Work State | DPD | (읽기 전용) | on change, time interval | 붐의 마스터 작업 스위치 |
| 19 | 161 | Actual Condensed Work State | DPD | (읽기 전용) | on change, time interval | 7섹션 실제 ON/OFF 비트 |
| 20 | 290 | Setpoint Condensed Work State | DPD | settable | on change | 7섹션 목표 ON/OFF 비트, TC→작업기 |
| 21 | 160 | Section Control State | DPD | settable | on change | TC-SC 활성/비활성 스위치 |
| 22 | 70 | Maximum Working Width | DPT | - | - | 11,998mm |

Work State는 "지금 작업 중인가(켜짐·꺼짐)"를 나타내는 값이다. Actual은 실제 상태, Setpoint는 TC가 원하는 상태다. 141·161의 on change·time interval은 표준이 "Actual Work State(들)와 Actual Condensed Work State(들)에는 On Change·Time Interval 지원이 필수"라고 못 박은 항목이다. 160(Section Control State)은 같은 규칙에서 "settable + on-change 트리거 필수"로 명시된다.

<strong>섹션 레벨(대표: Section 1, Element 11)</strong>: DPD 없이 DPT만 붙는다.

| Object ID | DDI | 이름 | 타입 | 값 |
|---|---|---|---|---|
| 23 | 70 | Maximum Working Width | DPT | 1,714mm |
| 24 | 134 | Offset X | DPT | 0mm |
| 25 | 135 | Offset Y | DPT | −5,142mm |
| 26 | 136 | Offset Z | DPT | 0mm |

Section 2~7도 같은 4개 DPT 패턴이 반복된다(Object ID 27~50). DDI 70(1,714mm)·134·136(0mm)은 7개 섹션이 전부 같고, DDI 135(Offset Y)만 섹션마다 다르다. 바로 아래에서 계산한다. Offset X·Z를 0mm로 둔 것은 이 예시에서 모든 섹션이 붐과 같은 전후·높이 위치에 일렬로 달려 있다고 가정했기 때문이다(실측값이 아니라 이 예시의 설계 가정).

표시용 DVP는 48장 예제와 같은 패턴으로 2개면 충분하다. Object ID 51(Offset 0, Scale 0.0001, L/ha)을 DDI 1·2가 참조하고, Object ID 52(Offset 0, Scale 1, mm)를 DDI 70·134·135·136이 참조한다. 여기까지 합치면 다음과 같다.

| 종류 | 개수 | 내역 |
|---|---|---|
| DVC | 1 | Object ID 0 |
| DET | 11 | 루트 1 + 커넥터·빈·붐 3 + 섹션 7 |
| DPD | 9 | 장치 3 + 붐 6 |
| DPT | 29 | 붐 1 + 섹션 7×4 |
| DVP | 2 | Object ID 51, 52 |

DVC 1개, DET 11개, DPD 9개, DPT 29개, DVP 2개로 총 52개 오브젝트다.

### Y 오프셋 계산

DDOP의 위치는 모두 DRP(Device Reference Point, 장치 기준점)에서 잰 거리로 적는다. 좌표는 오른손 좌표계를 쓴다. x는 주행 방향, y는 오른쪽, z는 아래(지면 쪽)가 양수다. 그래서 y축은 <strong>주행 방향 기준 우측이 양수</strong>다. 기준점을 어디로 잡는지는 [50장](/study/isobus/50-ddop-commands-design)의 점검표에서 본다.

섹션이 홀수 개(7개)이므로 가운데 4번 섹션이 y=0에 오고, 나머지 6개가 좌우로 대칭 배치된다. 이 계산은 각 섹션의 가운데 위치를 Y 오프셋으로 둔 것이다.

![위에서 내려다본 붐. 주행 방향은 위쪽이고, 붐은 폭 1,714 mm인 섹션 7개로 나뉜다. 가운데 Section 4가 y = 0이고 왼쪽 Section 1~3은 −5,142, −3,428, −1,714 mm, 오른쪽 Section 5~7은 1,714, 3,428, 5,142 mm다. 붐 전체 폭은 11,998 mm다](/images/study-isobus/49-section-y-offsets-light.png)
![위에서 내려다본 붐. 주행 방향은 위쪽이고, 붐은 폭 1,714 mm인 섹션 7개로 나뉜다. 가운데 Section 4가 y = 0이고 왼쪽 Section 1~3은 −5,142, −3,428, −1,714 mm, 오른쪽 Section 5~7은 1,714, 3,428, 5,142 mm다. 붐 전체 폭은 11,998 mm다](/images/study-isobus/49-section-y-offsets-dark.png)

| 섹션 | Element | Object ID(DDI 135) | Y 오프셋 |
|---|---|---|---|
| 1 | 11 | 25 | −5,142mm |
| 2 | 12 | 29 | −3,428mm |
| 3 | 13 | 33 | −1,714mm |
| 4 | 14 | 37 | 0mm |
| 5 | 15 | 41 | 1,714mm |
| 6 | 16 | 45 | 3,428mm |
| 7 | 17 | 49 | 5,142mm |

Section 1의 Y 오프셋을 단계별로 구해 보자.

1. Section 1은 가운데(Section 4)에서 왼쪽으로 세 칸 떨어져 있다.
2. 한 칸은 섹션 폭 1,714mm다.
3. 왼쪽은 음수이므로 −3 × 1,714 = −5,142mm다.

붐 전체 폭은 7 × 1,714mm = 11,998mm로, 정확히 12m는 아니고 2mm 모자란다. DDI 70(Maximum Working Width)에는 이 11,998mm를 붐(Function) 레벨 값으로 넣는다.

::: details 파이썬으로 검산해 보기
섹션 번호에서 4를 빼고 섹션 폭을 곱하면 Y 오프셋이 나온다. 코드는 그 값을 출력하고, 가운데가 0이고 좌우가 대칭인지 `assert`로 확인한다.

```python
n = 7
width = 1714  # mm, 섹션 1개 폭

offsets = {i: (i - 4) * width for i in range(1, n + 1)}
for i, y in offsets.items():
    print(f"section {i} (element {10+i}): Y = {y:+d} mm")

# 홀수 섹션 → 가운데(4번)가 0, 나머지는 좌우 대칭
assert offsets[4] == 0
assert offsets[1] == -offsets[7]
assert offsets[2] == -offsets[6]
assert offsets[3] == -offsets[5]

print("total width =", n * width, "mm")
```
```
section 1 (element 11): Y = -5142 mm
section 2 (element 12): Y = -3428 mm
section 3 (element 13): Y = -1714 mm
section 4 (element 14): Y = +0 mm
section 5 (element 15): Y = +1714 mm
section 6 (element 16): Y = +3428 mm
section 7 (element 17): Y = +5142 mm
total width = 11998 mm
```

출력이 위 표와 같고, 마지막 줄이 붐 전체 폭 11,998mm다.
:::

### 설계 판단 세 가지

<strong>섹션 폭은 DPT, 살포량은 DPD인 이유.</strong>

- 섹션 폭(1,714mm)은 물리적으로 고정된 값이라 DPT로 담는다. TC가 바꿀 수도, 저절로 바뀔 수도 없는 상수다.
- 살포량은 처방 맵·운전자 입력에 따라 태스크 중 계속 바뀌므로 DPD로 담아야 한다.
- 이 구분을 반대로 하면 안 되는 이유가 DDI 67(Actual Working Width, 실제 작업 폭)에서 드러난다. 붐(Function) 레벨의 DDI 67은 "On 상태인 하위 섹션 폭의 합"으로 정의된다. 섹션 하나가 꺼지면 이 값 자체가 줄어든다는 뜻이다. 섹션의 물리적 폭을 이 값 하나로만 표현했다면 "섹션이 꺼져서 폭이 줄어든 것"과 "섹션 자체 폭이 바뀐 것"을 구분할 수 없다.
- 그래서 이 설계는 <strong>섹션 개별 폭(고정, DPT 70)</strong>과 <strong>붐 레벨 Actual Working Width(가변, On 섹션의 합)</strong>를 별도 DDI로 분리해 둔다. 이번 DDOP에는 DDI 67 자체를 넣지 않았다. 넣었다면 반드시 붐 레벨의 DPD여야 하고, 섹션의 DPT가 되면 안 된다는 뜻이다.

<strong>섹션별 개별 setpoint 대신 Condensed를 쓰는 이유.</strong>

- ISO 11783-10은 "DDOP에서 섹션 작업 상태의 보고·제어에 허용되는 것은 Actual/Setpoint Condensed Work State뿐이다. Section 요소 안에 개별 Actual Work State(141)나 개별 Setpoint Work State(289)를 두면 안 된다"고 명시한다. 즉 섹션 7개마다 DDI 289를 하나씩 붙이는 구성은 최적화 이전에 <strong>표준 위반</strong>이다. 48장 4절의 단순화한 예제가 바로 이 구성이었다.
- 설령 허용됐더라도 대역폭이 문제다. [연결당·variable당 상한은 초당 10개](/study/isobus/45-tc-process-data-basics)인데, 이 상한을 넘겨도 되는 예외는 <strong>Condensed Work State류 DDI</strong>에만 적용된다. variable은 Element Number와 DDI로 가리키는 값 하나를 말한다.
- 헤드랜드(밭 끝에서 방향을 트는 구간) 진입처럼 여러 섹션을 한꺼번에 전환해야 하는 순간에도, DDI 290 하나로 7섹션 상태를 동시에 담으면 이 burst(짧은 순간 몰아 보내기) 예외를 그대로 쓸 수 있다.

<strong>settable 비트는 목표값, 스위치, 총계에만 세운다.</strong>

- DDI 2(Actual Volume Per Area)·141(Actual Work State)·161(Actual Condensed Work State)은 작업기가 실측·실제 상태를 보고하는 값이다.
- 이 DPD들의 Properties 바이트에 settable(bit2)을 세우면 TC가 "실측값"이라는 이름의 필드에 값을 명령할 수 있게 된다. [48장 5절](/study/isobus/48-ddop-basics)에서 다룬 Object 8(DDI 2)의 규칙과 같은 원리로 잘못이다. 읽기 전용이어야 할 DDI를 설정용으로 여는 것이 흔한 설계 실수다.
- 이 DDOP에서 settable은 DDI 1(살포량 목표)·290(섹션 목표 상태)·160(Section Control State, TC-SC 활성화 스위치), 그리고 앞서 Device 레벨에 둔 총계 3종(119·116·117)에만 세운다. 총계는 태스크 시작 시 TC가 이어서 셀 시작값을 지정할 수 있어야 하므로 성격이 다른 settable이다.

<small>근거: ISO 11783-10 A.1, F.2.1, F.3.3, F.3.4, F.3.5</small>

## 2. 이 DDOP로 만들 수 있는 메시지

이 절에서는 1절의 DDOP가 활성화된 뒤 TC가 보낼 수 있는 Process Data 메시지 두 개를 바이트로 만든다. DDOP에 무엇을 선언했는지가 어떤 메시지를 보낼 수 있는지를 정한다는 점을 확인한다.

이 DDOP는 붐(Element 3)에만 DDI 1을 정의하고 섹션(Element 11~17)에는 DDI 1을 두지 않는다. 즉 "섹션 1의 살포량만 따로 정한다"는 명령 자체가 이 설계에서 성립하지 않는다. `[DDI=1, Element=11]`로 명령을 보내면 작업기는 그 Element에 연결된 DPD가 없으므로 PDACK(command D, 명령을 처리하지 못했다는 응답)로 거부한다([46장](/study/isobus/46-tc-commands-pdack)). 붐 전체 살포량을 바꾸는 유일한 방법은 붐(Element 3)에 명령하는 것이다.

바이트 배치는 [45장](/study/isobus/45-tc-process-data-basics)에서 조립해 본 Process Data 메시지 구조를 그대로 따른다.

- Byte 1 하위 4비트: Command
- Byte 1 상위 4비트 + Byte 2: Element Number 12비트(낮은 4비트가 Byte 1에, 높은 8비트가 Byte 2에 들어간다)
- Byte 3~4: DDI
- Byte 5~8: 값(Value)

2바이트 이상인 수는 리틀 엔디언, 곧 낮은 자리 바이트부터 싣는다. 아래 표는 위 줄이 바이트 번호(1부터 센다), 아래 줄이 그 바이트의 값이다.

<strong>메시지 1: 붐 전체 살포량 220 L/ha 설정 (Element 3, DDI 1, Command 3)</strong>

| Byte | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| 값 | `0x33` | `0x00` | `0x01` | `0x00` | `0xC0` | `0x91` | `0x21` | `0x00` |

220 L/ha → 22,000 mm³/m² → raw = 22,000 ÷ 0.01 = 2,200,000(`0x2191C0`), LSB부터 `C0 91 21 00`.

단계별로 풀면 다음과 같다.

1. Byte 1: Command 3(Value command, 값을 정해 주는 명령)을 하위 니블에, Element Number 3의 낮은 4비트(3)를 상위 니블에 놓아 `0x33`(=51)이다.
2. Byte 2: Element Number 3의 높은 8비트는 0이라 `0x00`이다.
3. Byte 3~4: DDI 1을 리틀 엔디언으로 쓰면 `01 00`이다.
4. Byte 5~8: DDI 1의 단위는 mm³/m²이고 분해능(원시값 1이 나타내는 크기)은 0.01이다. 1 L/ha = 100 mm³/m²이므로 220 L/ha는 22,000 mm³/m²다. 이것을 0.01로 나눈 2,200,000(=`0x2191C0`)이 원시값이고, 낮은 자리부터 `C0 91 21 00`으로 싣는다.

<strong>메시지 2: 붐의 7섹션 ON/OFF 일괄 명령 (Element 3, DDI 290, Command 3)</strong>

가장자리 두 섹션(1·7)은 끄고 가운데 다섯 섹션(2~6)은 켜는 상황을 예로 든다. DDI 290은 [섹션당 2비트(00=Off, 01=On)로 최대 16섹션까지 한 32비트 값에 담는다](/study/isobus/45-tc-process-data-basics). 이 예시는 두 가지를 가정한다.

- 섹션 1이 LSB 쪽 2비트를 차지한다고 둔다. 이 대응 순서는 이 글이 확인한 자료에 적혀 있지 않아 이 예시의 가정이다.
- 정의되지 않은 8~16번은 141(Actual Work State)에서 확인된 2비트 코드표(00=Off, 01=On, 10=오류, 11=미설치) 중 "미설치(11)"를 빌려 채운다. 290 자체의 코드값은 이 글이 확인한 자료에 따로 적혀 있지 않다.

| Byte | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| 값 | `0x33` | `0x00` | `0x22` | `0x01` | `0x54` | `0xC5` | `0xFF` | `0xFF` |

Byte 1~2는 메시지 1과 같다. Byte 3~4는 DDI 290(=`0x0122`)을 리틀 엔디언으로 쓴 `22 01`이다. Byte 5~8은 섹션 2비트 코드를 다음처럼 채운다. 한 바이트 안에서는 번호가 큰 섹션이 왼쪽(높은 비트)에 온다.

| 바이트 | 담긴 섹션(왼쪽부터) | 2비트 코드 | 값 |
|---|---|---|---|
| Byte 5 | 4, 3, 2, 1 | 01 01 01 00 | `0x54` |
| Byte 6 | 8, 7, 6, 5 | 11 00 01 01 | `0xC5` |
| Byte 7 | 12, 11, 10, 9 | 11 11 11 11 | `0xFF` |
| Byte 8 | 16, 15, 14, 13 | 11 11 11 11 | `0xFF` |

Byte 6을 예로 읽으면, 섹션 8은 미설치(11), 섹션 7은 Off(00), 섹션 6·5는 On(01)이다. 이어 붙인 `1100 0101`이 `0xC5`(=197)다.

::: details 파이썬으로 검산해 보기
`build_frame`은 Command, Element Number, DDI, 값을 받아 8바이트를 만든다. 메시지 2는 섹션마다 2비트 코드를 제자리로 밀어 32비트 값을 만든 뒤 넘긴다.

```python
def build_frame(command, element, ddi, value):
    byte1 = ((element & 0xF) << 4) | (command & 0xF)
    byte2 = (element >> 4) & 0xFF
    ddi_bytes = ddi.to_bytes(2, "little")
    value_bytes = value.to_bytes(4, "little", signed=True)
    return bytes([byte1, byte2]) + ddi_bytes + value_bytes


# 메시지 1: 붐(Element 3)에 DDI 1, 220 L/ha
raw = int(220 * 100 / 0.01)
frame1 = build_frame(command=3, element=3, ddi=1, value=raw)
print(frame1.hex(' ').upper())   # 33 00 01 00 C0 91 21 00

# 메시지 2: 붐(Element 3)에 DDI 290, 섹션 1·7 Off / 2~6 On / 8~16 미설치
states = {1: 0, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 0}
value = 0
for i in range(1, 17):
    bits = states.get(i, 0b11)   # 정의 안 된 섹션(8~16)은 미설치
    value |= bits << (2 * (i - 1))
value_signed = value - 2**32 if value >= 2**31 else value

frame2 = build_frame(command=3, element=3, ddi=290, value=value_signed)
print(frame2.hex(' ').upper())   # 33 00 22 01 54 C5 FF FF
```

두 `print`의 출력이 위 두 표의 8바이트와 같다.
:::

두 메시지 모두 Byte 1이 `0x33`인 것은 우연이다. Command(3, Value command)와 Element Number(3, 붐)가 두 메시지에서 같은 값이라 니블이 똑같이 채워졌을 뿐이다. Byte 3~4(DDI)와 Byte 5~8(Value)이 완전히 다른 두 명령을 구분한다.

## 3. 레코드의 공통 머리와 바이트 읽는 법

[48장 5절](/study/isobus/48-ddop-basics)에서는 오브젝트의 필드와 폭까지만 봤다. 이 절부터는 필드가 바이트열의 몇 번째에 놓이는지까지 본다. DDOP는 오브젝트 레코드를 이어 붙인 바이트열이고, 모든 레코드는 같은 머리로 시작한다.

| 머리 필드 | 크기 | 값 |
|---|---|---|
| Table ID | 3바이트 문자열 | `DVC`·`DET`·`DPD`·`DPT`·`DVP` (XML 요소 이름) |
| Object ID | 2바이트 정수 | DVC는 항상 0, 나머지는 1~65534. 참조가 없을 때는 NULL Object ID `0xFFFF`(65535) |

Table ID는 TC가 DDOP를 XML 파일로 저장할 때 쓰는 요소 이름과 같다(6절). Object ID는 DDOP 전체에서 유일해야 한다. DET의 Parent ObjectId가 0이면 부모가 DVC라는 뜻이다.

표준의 레코드 표는 바이트 순서를 따로 적지 않는다. 이 시리즈의 메시지 형식 규칙대로 2·4·8바이트 정수는 LSB(가장 낮은 자리 바이트)부터, 문자열은 왼쪽 글자부터 싣는다. 이것은 ISO 11783-7(트랙터와 작업기 사이 메시지를 정하는 표준 문서)의 일반 규칙이다. 예를 들어 Object ID 3을 2바이트로 쓰면 `03 00`이다. 9,000(=`0x2328`)을 4바이트로 쓰면 `28 23 00 00`이다.

DVP의 Scale은 표준 표에 "Float 4바이트"라고만 적혀 있다. 이 글의 예제는 IEEE 754 단정밀도(컴퓨터가 소수를 4바이트로 저장하는 표준 형식)를 LSB부터 싣는 것으로 두었다. 표준에서 바이트 표현은 확인하지 못했다(확인 필요).

![DDOP 오브젝트 레코드 5종의 필드 배치. 모두 Table ID 3바이트와 Object ID 2바이트로 시작한다. DVC는 designator·SW version·serial number 세 가변 문자열과 ClientNAME 8바이트, structure·localization label 7바이트씩, 버전 4 전용 extended structure label이 이어진다. DET·DPD·DPT·DVP는 길이 바이트 뒤에 UTF-8 문자열 하나를 품는다](/images/study-isobus/20-ddop-record-layouts-light.png)
![DDOP 오브젝트 레코드 5종의 필드 배치. 모두 Table ID 3바이트와 Object ID 2바이트로 시작한다. DVC는 designator·SW version·serial number 세 가변 문자열과 ClientNAME 8바이트, structure·localization label 7바이트씩, 버전 4 전용 extended structure label이 이어진다. DET·DPD·DPT·DVP는 길이 바이트 뒤에 UTF-8 문자열 하나를 품는다](/images/study-isobus/20-ddop-record-layouts-dark.png)

그림 읽는 법: 한 줄이 레코드 하나이고, 칸 아래 숫자는 그 칸의 바이트 수다. N, M, O, P 칸은 바로 뒤 문자열이 몇 바이트인지 적는 1바이트 칸이다. 색은 칸의 성격(머리, 고정 길이, 길이·개수, 가변 문자열, 버전 4 전용)을 나타낸다.

그림의 "버전 4 전용"에서 버전은 TC 표준의 판에 따른 기능 수준이다. TC와 클라이언트는 연결할 때 서로의 버전을 확인한다([43장](/study/isobus/43-tc-connection)). 버전 4에서 생긴 칸은 양쪽이 모두 버전 4 이상일 때만 쓴다(5절).

<small>근거: ISO 11783-10 A.1, Table A.1~A.5, D.21, ISO 11783-7:2015 3.3.1</small>

## 4. 다섯 레코드의 바이트 배치

이 절에서는 다섯 레코드의 칸을 하나씩 본다. 문자열 칸 때문에 뒤 칸 위치가 밀리는 점을 눈여겨본다.

### DVC: 가변 길이 문자열이 셋

표 읽는 법: Record byte는 레코드 첫 바이트를 1로 센 위치다. N, M, O, P는 앞에서 읽은 길이 바이트의 값이다. 그래서 "7+N"은 "designator가 N바이트를 차지하고 난 다음 자리"라는 뜻이다.

| Record byte | 필드 | 크기 | 범위·규칙 |
|---|---|---|---|
| 1~3 | Table ID | 3 | `DVC` |
| 4~5 | Object ID | 2 | 0 |
| 6 | designator 바이트 수 N | 1 | 0~128 |
| 7 | Device designator | N | UTF-8, 최대 32자 |
| 7+N | software version 바이트 수 M | 1 | 0~128 |
| 8+N | Device software version | M | UTF-8, 최대 32자 |
| 8+N+M | ClientNAME | 8 | 이 CF의 address claim NAME과 같아야 한다 |
| 16+N+M | serial number 바이트 수 O | 1 | 0~128 |
| 17+N+M | DeviceSerialNumber | O | UTF-8, 최대 32자 |
| 17+N+M+O | Device structure label | 7 | 각 바이트 0~254 |
| 24+N+M+O | Device localization label | 7 | 바이트 1~6은 0~254, 바이트 7은 255 |
| 31+N+M+O | extended structure label 바이트 수 P | 1 | 0~32(버전 4) |
| 32+N+M+O | Extended structure label | P | 각 바이트 0~255(버전 4) |

"Record byte" 열은 표준 표의 표기를 따랐다. 앞 문자열 길이에 따라 뒤 필드 위치가 밀리므로, 파서(바이트를 읽어 해석하는 프로그램)는 레코드를 처음부터 차례로 읽어야 한다. 예를 들어 designator가 `BoomSprayer-3S`(14바이트)이면 N = 14이고, software version 바이트 수 M은 7+14 = 21번째 바이트에 놓인다. 8절에서 이 계산을 끝까지 해 본다.

DVC에는 제조사 이름 필드가 없다. 제조사는 ClientNAME 안의 manufacturer code(ISO 11783-5가 정하는 NAME의 제조사 코드, [12장](/study/isobus/12-j1939-address-name))로 표현된다. CF(Control Function)는 버스에서 주소를 가진 제어 기능 하나이고, address claim NAME은 그 CF가 주소를 얻을 때 쓴 8바이트 이름이다.

### DET·DPD·DPT·DVP

나머지 네 레코드는 표 한 칸에 배치를 몰아 적었다. "8+N element number"는 "Record byte 8+N부터 element number가 온다"로 읽는다.

| 오브젝트 | Record byte 배치 |
|---|---|
| DET | 1~3 `DET` · 4~5 Object ID · 6 DeviceElementType(1~7) · 7 N · 8 designator · 8+N element number(0~4095) · 10+N Parent ObjectId(0~65534) · 12+N 참조 개수 K · 14+N 참조 Object ID 2바이트 × K |
| DPD | 1~3 `DPD` · 4~5 Object ID · 6~7 DDI(0~65535) · 8 properties(0~7) · 9 trigger methods(0~31) · 10 N · 11 designator · 11+N DVP Object ID |
| DPT | 1~3 `DPT` · 4~5 Object ID · 6~7 DDI · 8~11 property value(부호 있는 32비트) · 12 N · 13 designator · 13+N DVP Object ID |
| DVP | 1~3 `DVP` · 4~5 Object ID · 6~9 Offset(부호 있는 32비트) · 10~13 Scale(float) · 14 Number of decimals(0~7) · 15 N · 16 UnitDesignator |

"부호 있는 32비트"는 음수도 담을 수 있는 4바이트 정수라는 뜻이다(−2,147,483,648~2,147,483,647). Offset Y처럼 음수가 될 수 있는 값을 담기 위해서다.

구현할 때 놓치기 쉬운 참조 규칙은 셋이다.

- DET의 참조 목록에 들어가는 것은 DPD와 DPT뿐이다. 자식 DET는 참조 목록이 아니라 자식 쪽 Parent ObjectId로 연결한다. DVP는 DPD·DPT가 참조한다.
- DPD·DPT 하나를 여러 DET가 함께 참조할 수 있고, DVP 하나를 여러 DPD·DPT가 참조할 수 있다. 값이 같은 property는 오브젝트 하나로 공유할 수 있다는 뜻이다. [50장](/study/isobus/50-ddop-commands-design)에서 이 점을 활용한다.
- DPD·DPT의 DVP Object ID 범위는 1~65535이고, DVP가 없으면 NULL(`0xFFFF`)을 넣는다.

### Designator: 바이트 수와 글자 수는 다르다

designator는 사람이 읽을 이름표다. 문자열 속성은 BOM 없는 UTF-8이다. BOM(Byte Order Mark)은 글자 앞에 붙이기도 하는 표시 바이트인데, DDOP 문자열에는 붙이지 않는다.

UTF-8 한 글자는 최대 4바이트이므로 바이트 배열의 최대 길이는 XML 정의 글자 수의 4배다. 그래서 designator는 "최대 32자, 최대 128바이트"다. 128바이트 상한은 버전 4에서 32바이트에서 늘어난 것이다.

| 문자열 | 글자 | UTF-8 바이트 | 버전 3 상한(32 B) | 버전 4 상한(128 B, 32자) |
|---|---|---|---|---|
| `Section 1` | 9 | 9 | 통과 | 통과 |
| `좌측 섹션` | 5 | 13 | 통과 | 통과 |
| `좌측 붐 1번 섹션 노즐 그룹` | 16 | 36 | 초과 | 통과 |

한글은 UTF-8로 한 글자 3바이트다. `좌측 섹션`은 한글 4자 × 3바이트 = 12바이트에 공백 1바이트를 더해 13바이트다. 길이 바이트에는 글자 수가 아니라 바이트 수를 적는다. 클라이언트는 연결한 TC의 버전·기능에 자신을 맞춰야 하므로, 버전 3 TC에 연결할 때는 designator를 32바이트 안에 맞춘다(추론. 표준은 범위가 늘어났다는 사실만 적는다).

<small>근거: ISO 11783-10 A.1~A.7, Table A.1~A.5 각주, B.6.14, 6.6.2 f</small>

## 5. 라벨 세 가지: structure, localization, extended

이 절에서는 DVC 레코드 끝부분의 라벨 칸 세 개를 본다. 라벨은 TC가 "이 DDOP를 이미 갖고 있나"를 판단할 때 쓰는 이름표다.

### Structure label

<strong>Structure label</strong>(7바이트)은 DDOP 구조의 버전 라벨이다. 내용은 제조사가 정하고, 각 바이트는 0~254다. 255(`FF`)를 못 쓰는 이유가 표준에 적혀 있지는 않다. TC가 "그런 라벨 없음"을 7바이트 `FF`로 답하기 때문으로 보인다(추론, [50장](/study/isobus/50-ddop-commands-design)의 Structure Label 응답 참고). 구성이 여러 개인 장치는 구성마다 structure label(과 extended structure label) 조합을 따로 둔다.

### Localization label

<strong>Localization label</strong>(7바이트)은 언어·단위 설정의 라벨이다. 바이트 1~6은 Language command(PGN 65039, `0xFE0F`)의 바이트 1~6과 같고, 바이트 7은 예약값 `FF`다. Language command는 운전자가 고른 언어, 날짜 형식, 측정 단위를 버스의 모든 장치에 알리는 메시지다([25장](/study/isobus/25-settings-safety-messages)).

| 바이트 | Language command 내용 |
|---|---|
| 1~2 | 언어 코드(ISO 639 두 글자, 예: `en` = `65 6E`) |
| 3 | bit 8~7 소수점 기호(00 쉼표, 01 점), bit 6~5 시간 형식(00 24시간, 01 12시간) |
| 4 | 날짜 형식(0 = ddmmyyyy … 4 = yyyymmdd) |
| 5 | 거리·면적·부피·질량 단위(각 2비트, 00 = 미터법) |
| 6 | 온도·압력·힘 단위와 단위계(각 2비트) |
| 7 | 예약 `FF` |

8절 예제의 localization label `65 6E 00 00 00 00 FF`를 이 표로 읽어 보자.

1. 바이트 1~2 `65 6E`: ASCII로 `en`, 영어다.
2. 바이트 3 `00`: 소수점 기호는 쉼표(00), 시간은 24시간 형식(00)이다.
3. 바이트 4 `00`: 날짜 형식 0, 곧 ddmmyyyy다.
4. 바이트 5 `00`: 거리·면적·부피·질량 단위가 모두 미터법(00)이다.
5. 바이트 6 `00`: 온도·압력·힘 단위와 단위계 칸도 모두 00이다.
6. 바이트 7 `FF`: 예약값이다.

언어나 단위만 바꾸면 localization label만 바뀌고 structure label은 그대로다. [50장](/study/isobus/50-ddop-commands-design)의 런타임 변경 규칙이 이 구분에 기댄다.

### Extended structure label

<strong>Extended structure label</strong>(0~32바이트)은 버전 4에서 생긴 structure label의 연장이다. 두 가지 규칙이 구현을 가른다.

- TC와 클라이언트가 모두 버전 4 이상일 때만 쓴다. 한쪽이라도 버전 3 이하면 가장 낮은 공통 버전으로 내려가고 extended 관련 속성 2개(바이트 수와 라벨)를 모두 쓰지 않는다. 버전 3 TC에 보내는 DVC 레코드는 localization label에서 끝난다.
- extended label을 쓰지 않는 버전 4 클라이언트는 버전 4 TC에 바이트 수 0을 보낸다(레코드 끝에 `00` 1바이트).

같은 장치라도 상대 버전에 따라 DVC 레코드 길이가 달라진다는 뜻이다. 파서는 협상된 버전으로 레코드 끝을 판단해야 한다.

48장 예제의 Structure Label `SPRY3-V1.0`은 10바이트라 7바이트 필드에 다 들어가지 않는다. 버전 4 연결이면 `SPRY3-V`(7바이트)를 structure label에, `1.0`(3바이트)을 extended structure label에 나눠 담을 수 있다. 버전 3 TC와 연결되면 7바이트만으로 구성을 구별해야 한다. 8절의 바이트 예제는 버전 4 연결을 가정한다.

<small>근거: ISO 11783-10 A.2, Table A.1, B.6.3, ISO 11783-7 B.21, A.23</small>

## 6. 라벨 바이트 순서: XML과 CAN (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

TC는 받은 DDOP를 XML(태그로 구조를 적는 텍스트 형식) 파일 세트로 바꿔 저장한다. 이때 라벨은 xs:hexBinary(바이트를 16진수 글자로 적는 형식) 값이 되는데, 라벨 배열의 바이트 1이 hexBinary의 최하위 바이트(맨 오른쪽)다. 그래서 XML 문자열과 버스의 바이트 순서가 뒤집힌다. 표준에 실린 예는 다음과 같다.

| 라벨 | XML 속성 값 | CAN 버스 순서(바이트 1부터) |
|---|---|---|
| structure label | `F="F9FAFBFCFDFE39"` | `39 FE FD FC FB FA F9` |
| localization label | `G="FF000000006E65"` | `65 6E 00 00 00 00 FF` |
| structure label + extended 8바이트 | `F="E8E7E6E5E4E3E2E1F9FAFBFCFDFE39"` | `39 FE … F9` + localization 7바이트 + `08` + `E1 E2 … E8` |

첫 줄을 단계별로 바꿔 보자.

1. XML 값 `F9FAFBFCFDFE39`를 두 글자씩 끊으면 `F9 FA FB FC FD FE 39`다.
2. 맨 오른쪽 `39`가 라벨의 바이트 1이다.
3. 버스에는 바이트 1부터 나가므로 거꾸로 읽은 `39 FE FD FC FB FA F9` 순서가 된다.

XML에서는 extended label이 structure label 앞(상위 바이트 쪽)에 한 문자열로 이어 붙고, 버스에서는 둘 사이에 localization label과 바이트 수가 끼어든다. DDOP를 XML로 내보내는 TC 서버라면 이 변환을 따로 테스트해 두는 편이 좋다(추론).

<small>근거: ISO 11783-10 A.1, D.19</small>

## 7. DPD 속성값과 DVP 표시 공식

이 절에서는 DPD 속성 바이트에 실제로 쓸 수 있는 값과, DVP가 원시값을 사람이 읽을 값으로 바꾸는 계산을 본다.

### DPD properties는 0~5만 유효하다

표준의 DPD 표는 properties 범위를 0~7로 적지만, bit 2(settable)와 bit 3(control source)은 함께 설 수 없다. 실제로 쓸 수 있는 값은 여섯 가지다.

| 값 | 비트 | 뜻 |
|---|---|---|
| `0x00` | - | 읽기 전용 |
| `0x01` | bit 1 | default set 멤버 |
| `0x02` | bit 2 | settable |
| `0x03` | bit 1+2 | default set + settable |
| `0x04` | bit 3 | control source(버전 4) |
| `0x05` | bit 1+3 | default set + control source(버전 4) |

`0x06`(=6)과 `0x07`(=7)은 규칙 위반이다. 예를 들어 `0x06`은 4 + 2, 곧 bit 3과 bit 2가 함께 선 값이다. trigger methods는 0~31(`0x1F`, =31) 비트셋이고, 비트와 measurement 명령의 대응은 [46장](/study/isobus/46-tc-commands-pdack)에 정리했다. DDI `0xDFFF`(=57343)의 DPD는 trigger를 `0x1F`로 둔다. 이 DDI는 "기본 기록 값 전체를 보내라"는 요청에 쓰는 특수 DDI다([47장](/study/isobus/47-tc-totals-logging-peer)).

### DVP: 표시 공식과 float32

표시값 = (정수 값 + Offset) × Scale이고, 결과는 Number of decimals 자릿수로 반올림한다. Offset은 부호 있는 32비트, Scale은 0.000000001~100000000.0 범위의 float 4바이트, decimals는 0~7이다.

| 예 | 정수 값 | Offset | Scale | decimals | 표시 |
|---|---|---|---|---|---|
| DDI 1 → L/ha | 2,000,000 | 0 | 0.0001 | 2 | 200.00 L/ha |
| DDI 119 → hr (47장 경운기 예) | 9,000 | 0 | 2.777778E-04 | 2 | 2.50 hr |
| DDI 67 → m (47장 경운기 예) | 9,000 | 0 | 1.0E-03 | 1 | 9.0 m |

둘째 줄을 단계별로 계산하면 다음과 같다.

1. 정수 값 9,000에 Offset 0을 더한다.
2. Scale 2.777778E-04(곧 0.0002777778)를 곱하면 2.5000002다. 이 Scale은 1/3600에 가까운 값이라 초를 시간(hr)으로 바꾼다.
3. decimals 2로 반올림하면 2.50이다.

Scale은 float32라 십진수가 정확히 담기지 않는다. 0.0001을 float32로 바꾸면 `17 B7 D1 38`이고, 되읽으면 0.000099999997…이다. 표시값은 반올림이 오차를 덮지만, 이 배율을 거꾸로 써서 운전자 입력을 원시값으로 바꾸는 코드는 오차를 조심해야 한다(추론).

DVP는 사람에게 보여 줄 때만 쓴다. Process Data 메시지의 값은 언제나 DDE(Data Dictionary Entity, DDI 하나의 단위와 분해능을 정한 사전 항목)의 분해능으로 해석한다. DVP를 바꿔도 버스의 원시값은 그대로다. 그래서 언어·단위가 바뀔 때 DVP만 다시 보내는 런타임 갱신이 허용된다([50장](/study/isobus/50-ddop-commands-design)).

::: details 파이썬으로 검산해 보기: 라벨, designator, DVP
아래 코드는 이 장 5~7절의 계산을 한 번에 확인한다. XML 라벨을 버스 순서로 뒤집고, localization label을 풀고, designator 길이를 재고, Scale을 float32로 바꿔 본다.

```python
import struct

# XML hexBinary는 배열 바이트 1이 맨 오른쪽(최하위). CAN에는 바이트 1부터 나간다(D.19 예 1)
xml_to_can = lambda h: bytes.fromhex(h)[::-1]
assert xml_to_can("F9FAFBFCFDFE39").hex(" ").upper() == "39 FE FD FC FB FA F9"
assert xml_to_can("FF000000006E65").hex(" ").upper() == "65 6E 00 00 00 00 FF"

# 확장 라벨 8바이트(D.19 예 2): XML은 15바이트 한 덩어리, CAN에서는 7 + (로컬 7) + 개수 1 + 8
ext_xml = "E8E7E6E5E4E3E2E1F9FAFBFCFDFE39"
label15 = xml_to_can(ext_xml)
label, ext = label15[:7], label15[7:]
assert ext.hex(" ").upper() == "E1 E2 E3 E4 E5 E6 E7 E8"

# localization label 디코딩(Part 7 B.21 Language command 바이트 1~6)
def decode_loc(loc):
    b3, b4, b5, b6 = loc[2], loc[3], loc[4], loc[5]
    two = lambda b, hi: (b >> (hi - 2)) & 0b11
    return dict(language=loc[:2].decode("ascii"),
                decimal=["comma", "point", "reserved", "no action"][two(b3, 8)],
                time=["24h", "12h", "reserved", "no action"][two(b3, 6)],
                date_format=b4,
                distance=two(b5, 8), area=two(b5, 6), volume=two(b5, 4), mass=two(b5, 2),
                temperature=two(b6, 8), pressure=two(b6, 6), force=two(b6, 4), system=two(b6, 2),
                byte7=hex(loc[6]))

print(decode_loc(xml_to_can("FF000000006E65")))
print(decode_loc(bytes([0x65, 0x6E, 0x40, 0x04, 0x00, 0x00, 0xFF])))

# designator: 버전 4는 128바이트·32자, 버전 3은 32바이트가 상한
for s in ["Section 1", "좌측 섹션", "좌측 붐 1번 섹션 노즐 그룹"]:
    n = len(s.encode("utf-8"))
    print(f"{s!r}: {len(s)}자 {n}B  v3 OK={n <= 32}  v4 OK={n <= 128 and len(s) <= 32}")

# DVP scale은 float32라 십진 값이 정확히 담기지 않는다
for scale in (0.0001, 2.777778e-04, 0.001):
    raw = struct.pack("<f", scale)
    print(scale, raw.hex(" ").upper(), struct.unpack("<f", raw)[0])
assert struct.pack("<f", 0.0001).hex(" ").upper() == "17 B7 D1 38"

# 표시값 = (정수 + Offset) x Scale, NumberOfDecimals로 반올림(D.25)
present = lambda raw, off, scale, dec: round((raw + off) * scale, dec)
assert present(2_000_000, 0, 0.0001, 0) == 200          # DDI 1, L/ha
assert present(9_000, 0, 2.777778e-04, 2) == 2.5         # DDI 119, hr
assert present(2_000_000, 0, 0.01, 2) == 20_000.0        # 0.01을 쓰면 100배 틀린다
```
```
{'language': 'en', 'decimal': 'comma', 'time': '24h', 'date_format': 0, 'distance': 0, 'area': 0, 'volume': 0, 'mass': 0, 'temperature': 0, 'pressure': 0, 'force': 0, 'system': 0, 'byte7': '0xff'}
{'language': 'en', 'decimal': 'point', 'time': '24h', 'date_format': 4, 'distance': 0, 'area': 0, 'volume': 0, 'mass': 0, 'temperature': 0, 'pressure': 0, 'force': 0, 'system': 0, 'byte7': '0xff'}
'Section 1': 9자 9B  v3 OK=True  v4 OK=True
'좌측 섹션': 5자 13B  v3 OK=True  v4 OK=True
'좌측 붐 1번 섹션 노즐 그룹': 16자 36B  v3 OK=False  v4 OK=True
0.0001 17 B7 D1 38 9.999999747378752e-05
0.0002777778 B5 A2 91 39 0.00027777781360782683
0.001 6F 12 83 3A 0.0010000000474974513
```

출력 첫 두 줄이 localization label 풀이, 다음 세 줄이 designator 길이 판정, 마지막 세 줄이 float32로 바꾼 Scale 바이트와 되읽은 값이다.
:::

<small>근거: ISO 11783-10 Table A.3, Table A.5, D.25, 6.8.4, 8.7, ISO 11783-11 4.2</small>

## 8. 48장 예제를 바이트열로 조립하기

이 절에서는 [48장 4절](/study/isobus/48-ddop-basics)의 3섹션 살포기 풀에서 오브젝트 7개를 떼어 실제 바이트로 만든다. 1절에서 본 대로 섹션마다 붙인 DDI 289는 섹션 제어(TC-SC) 규칙 위반이라 이 축소판에서는 뺐다. 작업폭 DPT는 Maximum Working Width(DDI 70)로 두었다.

| Object | 내용 |
|---|---|
| DVC 0 | designator `BoomSprayer-3S`, 버전 `1.0`, NAME `0xA00C8400073FFFC7`(표준 예시의 값), serial `SN-0001`, structure label `SPRY3-V` + extended `1.0`, localization `en`(표준 예시의 값) |
| DET 2 | type 1(device), element 0, 부모 0(DVC), 참조 DPT 6 |
| DET 3 | type 4(section), element 1, 부모 2, 참조 DPD 7·8 |
| DPT 6 | DDI 70 = 9,000 mm |
| DPD 7 | DDI 1, properties `0x02`, trigger `0x00`, DVP 16 |
| DPD 8 | DDI 2, properties `0x00`, trigger `0x08`, DVP 16 |
| DVP 16 | Offset 0, Scale 0.0001, decimals 0, `L/ha` |

일곱 레코드를 이어 붙인 전체 바이트열은 다음과 같다. 줄 맨 앞은 레코드 종류와 Object ID이고, 줄 끝은 그 레코드의 바이트 수다.

```
DVC  0  44 56 43 00 00 0E 42 6F 6F 6D 53 70 72 61 79 65 72 2D 33 53 03 31 2E 30
        C7 FF 3F 07 00 84 0C A0 07 53 4E 2D 30 30 30 31 53 50 52 59 33 2D 56
        65 6E 00 00 00 00 FF 03 31 2E 30                                    58 B
DET  2  44 45 54 02 00 01 07 53 70 72 61 79 65 72 00 00 00 00 01 00 06 00  22 B
DET  3  44 45 54 03 00 04 09 53 65 63 74 69 6F 6E 20 31 01 00 02 00 02 00
        07 00 08 00                                                         26 B
DPT  6  44 50 54 06 00 46 00 28 23 00 00 00 FF FF                           14 B
DPD  7  44 50 44 07 00 01 00 02 00 00 10 00                                 12 B
DPD  8  44 50 44 08 00 02 00 00 08 00 10 00                                 12 B
DVP 16  44 56 50 10 00 00 00 00 00 17 B7 D1 38 00 04 4C 2F 68 61            19 B
```

아래에서 레코드를 하나씩 바이트 단위로 풀어 본다. 표 읽는 법: "바이트"는 레코드 안 위치(1부터 센다)이고, 값은 16진수다. 2바이트 이상인 수는 리틀 엔디언이라 낮은 자리 바이트가 먼저 온다.

### DVC 0 (58바이트)

| 바이트 | 값 | 필드 |
|---|---|---|
| 1~3 | `44 56 43` | Table ID `DVC` |
| 4~5 | `00 00` | Object ID 0(DVC는 늘 0) |
| 6 | `0E` | designator 바이트 수 N = 14 |
| 7~20 | `42 6F 6F 6D … 33 53` | designator `BoomSprayer-3S` |
| 21 | `03` | software version 바이트 수 M = 3 |
| 22~24 | `31 2E 30` | software version `1.0` |
| 25~32 | `C7 FF 3F 07 00 84 0C A0` | ClientNAME `0xA00C8400073FFFC7`을 낮은 자리부터 |
| 33 | `07` | serial number 바이트 수 O = 7 |
| 34~40 | `53 4E 2D 30 30 30 31` | serial number `SN-0001` |
| 41~47 | `53 50 52 59 33 2D 56` | structure label `SPRY3-V` |
| 48~54 | `65 6E 00 00 00 00 FF` | localization label(5절에서 풀어 본 값) |
| 55 | `03` | extended structure label 바이트 수 P = 3 |
| 56~58 | `31 2E 30` | extended structure label `1.0` |

DVC는 N=14, M=3, O=7이라 structure label이 Record byte 17+14+3+7 = 41~47, localization label이 48~54, extended 바이트 수가 55, extended label이 56~58에 놓인다.

ClientNAME은 8바이트 수 `0xA00C8400073FFFC7`을 리틀 엔디언으로 실은 것이다. 맨 뒤 두 자리 `C7`이 먼저, 맨 앞 두 자리 `A0`이 마지막에 온다.

### DET 2 (22바이트)

| 바이트 | 값 | 필드 |
|---|---|---|
| 1~3 | `44 45 54` | Table ID `DET` |
| 4~5 | `02 00` | Object ID 2 |
| 6 | `01` | type 1(device) |
| 7 | `07` | designator 7바이트 |
| 8~14 | `53 70 72 61 79 65 72` | `Sprayer` |
| 15~16 | `00 00` | element number 0 |
| 17~18 | `00 00` | 부모 Object ID 0(DVC) |
| 19~20 | `01 00` | 참조 1개 |
| 21~22 | `06 00` | DPT 6 |

### DET 3 (26바이트)

DET 3을 필드로 나누면 다음과 같다. 48장 5절의 표가 폭까지만 말했던 부분이다.

| 바이트 | 값 | 필드 |
|---|---|---|
| 1~3 | `44 45 54` | Table ID `DET` |
| 4~5 | `03 00` | Object ID 3 |
| 6 | `04` | section |
| 7 | `09` | designator 9바이트 |
| 8~16 | `53 65 … 31` | `Section 1` |
| 17~18 | `01 00` | element number 1 |
| 19~20 | `02 00` | 부모 Object ID 2 |
| 21~22 | `02 00` | 참조 2개 |
| 23~26 | `07 00 08 00` | DPD 7, DPD 8 |

![DET 3 레코드 26바이트를 한 칸씩 그린 그림. 바이트 1~3 44 45 54는 Table ID DET, 4~5 03 00은 Object ID 3, 6 04는 type section, 7 09는 designator 길이, 8~16은 Section 1 글자, 17~18 01 00은 element number 1, 19~20 02 00은 부모 Object ID 2, 21~22 02 00은 참조 개수 2, 23~26 07 00 08 00은 DPD 7과 DPD 8이다](/images/study-isobus/49-det3-bytes-light.png)
![DET 3 레코드 26바이트를 한 칸씩 그린 그림. 바이트 1~3 44 45 54는 Table ID DET, 4~5 03 00은 Object ID 3, 6 04는 type section, 7 09는 designator 길이, 8~16은 Section 1 글자, 17~18 01 00은 element number 1, 19~20 02 00은 부모 Object ID 2, 21~22 02 00은 참조 개수 2, 23~26 07 00 08 00은 DPD 7과 DPD 8이다](/images/study-isobus/49-det3-bytes-dark.png)

designator `Section 1`이 9바이트라서 element number가 바이트 17에서 시작한다. Record byte 공식으로는 8+N = 8+9 = 17이다.

### DPT 6 (14바이트)

| 바이트 | 값 | 필드 |
|---|---|---|
| 1~3 | `44 50 54` | Table ID `DPT` |
| 4~5 | `06 00` | Object ID 6 |
| 6~7 | `46 00` | DDI 70(=`0x0046`), Maximum Working Width |
| 8~11 | `28 23 00 00` | 값 9,000(=`0x2328`) mm |
| 12 | `00` | designator 0바이트(이름 없음) |
| 13~14 | `FF FF` | DVP Object ID NULL(표시 규칙 없음) |

### DPD 7과 DPD 8 (각 12바이트)

두 레코드는 칸 배치가 같아서 한 표에 나란히 적었다.

| 바이트 | DPD 7 | DPD 8 | 필드 |
|---|---|---|---|
| 1~3 | `44 50 44` | `44 50 44` | Table ID `DPD` |
| 4~5 | `07 00` | `08 00` | Object ID 7, 8 |
| 6~7 | `01 00` | `02 00` | DDI 1, DDI 2 |
| 8 | `02` | `00` | properties: settable, 읽기 전용 |
| 9 | `00` | `08` | trigger: 없음, on change |
| 10 | `00` | `00` | designator 0바이트 |
| 11~12 | `10 00` | `10 00` | DVP Object ID 16(=`0x10`) |

### DVP 16 (19바이트)

| 바이트 | 값 | 필드 |
|---|---|---|
| 1~3 | `44 56 50` | Table ID `DVP` |
| 4~5 | `10 00` | Object ID 16 |
| 6~9 | `00 00 00 00` | Offset 0 |
| 10~13 | `17 B7 D1 38` | Scale 0.0001(float32, 낮은 자리부터) |
| 14 | `00` | Number of decimals 0 |
| 15 | `04` | 단위 글자 4바이트 |
| 16~19 | `4C 2F 68 61` | `L/ha` |

### 크기 알리기와 전송

일곱 레코드를 합치면 163바이트다(58 + 22 + 26 + 14 + 12 + 12 + 19). 클라이언트는 먼저 Request Object-pool Transfer로 크기를 알린다.

```
41 A3 00 00 00 FF FF FF     Request Object-pool Transfer, 163 B (0x000000A3)
```

이 8바이트를 풀면 다음과 같다.

1. `41`: 하위 명령 `0100`과 Command 1을 이어 붙인 첫 바이트, 곧 Request Object-pool Transfer다.
2. `A3 00 00 00`: 크기 163(=`0xA3`)을 4바이트 리틀 엔디언으로 쓴 값이다.
3. `FF FF FF`: 쓰지 않는 바이트를 채운 값이다.

크기 필드를 표준은 "요청하는 전송 데이터 크기(바이트)"라고만 적는다. 이 예제는 명령 바이트를 뺀 레코드 바이트 수로 두었다(추론). Object-pool Transfer는 명령 바이트 `61`을 더해 164바이트이고, 1,785바이트 이하라 TP로 나간다.

::: details 파이썬으로 검산해 보기: 직렬화와 역파싱
직렬화는 값을 바이트열로 바꾸는 일, 역파싱은 바이트열에서 값을 되찾는 일이다. 아래 코드는 레코드 다섯 종류를 만드는 함수로 일곱 레코드를 만든 뒤, `parse` 함수로 다시 읽는다.

```python
import struct

u8 = lambda v: bytes([v])
u16 = lambda v: v.to_bytes(2, "little")
i32 = lambda v: v.to_bytes(4, "little", signed=True)


def text(s):
    raw = s.encode("utf-8")              # BOM 없는 UTF-8
    assert len(raw) <= 128 and len(s) <= 32
    return u8(len(raw)) + raw


def dvc(designator, sw, name, serial, label, loc, ext=None):
    assert len(label) == 7 and 0xFF not in label
    assert len(loc) == 7 and loc[6] == 0xFF
    rec = (b"DVC" + u16(0) + text(designator) + text(sw) + name.to_bytes(8, "little")
           + text(serial) + label + loc)
    if ext is not None:                  # 양쪽이 버전 4 이상일 때만
        rec += u8(len(ext)) + ext
    return rec


def det(oid, etype, designator, number, parent, refs):
    return (b"DET" + u16(oid) + u8(etype) + text(designator) + u16(number)
            + u16(parent) + u16(len(refs)) + b"".join(u16(r) for r in refs))


def dpd(oid, ddi, props, triggers, designator="", dvp=0xFFFF):
    return b"DPD" + u16(oid) + u16(ddi) + u8(props) + u8(triggers) + text(designator) + u16(dvp)


def dpt(oid, ddi, value, designator="", dvp=0xFFFF):
    return b"DPT" + u16(oid) + u16(ddi) + i32(value) + text(designator) + u16(dvp)


def dvp(oid, offset, scale, decimals, unit):
    return b"DVP" + u16(oid) + i32(offset) + struct.pack("<f", scale) + u8(decimals) + text(unit)


pool = [
    dvc("BoomSprayer-3S", "1.0", 0xA00C8400073FFFC7, "SN-0001",
        b"SPRY3-V", bytes.fromhex("65 6E 00 00 00 00 FF"), ext=b"1.0"),
    det(2, 1, "Sprayer", 0, 0, [6]),
    det(3, 4, "Section 1", 1, 2, [7, 8]),
    dpt(6, 70, 9000),                                   # Maximum Working Width, mm
    dpd(7, 1, 0x02, 0x00, dvp=16),                      # settable
    dpd(8, 2, 0x00, 0x08, dvp=16),                      # on change
    dvp(16, 0, 0.0001, 0, "L/ha"),
]
for rec in pool:
    print(f"{len(rec):3d}B  {rec.hex(' ').upper()}")

assert pool[1].hex(" ").upper() == "44 45 54 02 00 01 07 53 70 72 61 79 65 72 00 00 00 00 01 00 06 00"
assert pool[4].hex(" ").upper() == "44 50 44 07 00 01 00 02 00 00 10 00"
assert pool[6][9:13].hex(" ").upper() == "17 B7 D1 38"      # record byte 10~13, float32 0.0001

size = sum(map(len, pool))
request = bytes([0x41]) + size.to_bytes(4, "little") + b"\xFF" * 3
transfer = bytes([0x61]) + b"".join(pool)
print("pool", size, "B | request", request.hex(" ").upper())
print("transfer", len(transfer), "B ->", "TP" if len(transfer) <= 1785 else "ETP")


def parse(buf, v4=True):
    """레코드를 순서대로 읽는다. 문자열 길이 때문에 다음 필드 위치가 매번 달라진다."""
    pos, out = 0, []

    def take(n):
        nonlocal pos
        pos += n
        return buf[pos - n:pos]

    num = lambda n, signed=False: int.from_bytes(take(n), "little", signed=signed)
    txt = lambda: take(num(1)).decode("utf-8")
    while pos < len(buf):
        tid, oid = take(3).decode(), num(2)
        if tid == "DVC":
            obj = dict(designator=txt(), sw=txt(), name=hex(num(8)), serial=txt(),
                       label=take(7), loc=take(7).hex(" "))
            if v4:
                obj["ext"] = take(num(1))
        elif tid == "DET":
            obj = dict(type=num(1), designator=txt(), number=num(2), parent=num(2))
            obj["refs"] = [num(2) for _ in range(num(2))]
        elif tid == "DPD":
            obj = dict(ddi=num(2), props=num(1), triggers=num(1), designator=txt(), dvp=num(2))
        elif tid == "DPT":
            obj = dict(ddi=num(2), value=num(4, True), designator=txt(), dvp=num(2))
        elif tid == "DVP":
            obj = dict(offset=num(4, True), scale=struct.unpack("<f", take(4))[0],
                       decimals=num(1), unit=txt())
        else:
            raise ValueError(f"unknown table id {tid!r} at {pos - 5}")
        out.append((tid, oid, obj))
    return out


for tid, oid, obj in parse(transfer[1:]):
    print(tid, oid, obj)

# 버전 3 TC처럼 extended label 필드가 없다고 보고 읽으면 DVC 끝 4바이트가 다음 레코드로 잘못 읽힌다
try:
    parse(transfer[1:], v4=False)
except (ValueError, UnicodeDecodeError) as e:
    print("v3 parser:", e)
```
```
 58B  44 56 43 00 00 0E 42 6F 6F 6D 53 70 72 61 79 65 72 2D 33 53 03 31 2E 30 C7 FF 3F 07 00 84 0C A0 07 53 4E 2D 30 30 30 31 53 50 52 59 33 2D 56 65 6E 00 00 00 00 FF 03 31 2E 30
 22B  44 45 54 02 00 01 07 53 70 72 61 79 65 72 00 00 00 00 01 00 06 00
 26B  44 45 54 03 00 04 09 53 65 63 74 69 6F 6E 20 31 01 00 02 00 02 00 07 00 08 00
 14B  44 50 54 06 00 46 00 28 23 00 00 00 FF FF
 12B  44 50 44 07 00 01 00 02 00 00 10 00
 12B  44 50 44 08 00 02 00 00 08 00 10 00
 19B  44 56 50 10 00 00 00 00 00 17 B7 D1 38 00 04 4C 2F 68 61
pool 163 B | request 41 A3 00 00 00 FF FF FF
transfer 164 B -> TP
DVC 0 {'designator': 'BoomSprayer-3S', 'sw': '1.0', 'name': '0xa00c8400073fffc7', 'serial': 'SN-0001', 'label': b'SPRY3-V', 'loc': '65 6e 00 00 00 00 ff', 'ext': b'1.0'}
DET 2 {'type': 1, 'designator': 'Sprayer', 'number': 0, 'parent': 0, 'refs': [6]}
DET 3 {'type': 4, 'designator': 'Section 1', 'number': 1, 'parent': 2, 'refs': [7, 8]}
DPT 6 {'ddi': 70, 'value': 9000, 'designator': '', 'dvp': 65535}
DPD 7 {'ddi': 1, 'props': 2, 'triggers': 0, 'designator': '', 'dvp': 16}
DPD 8 {'ddi': 2, 'props': 0, 'triggers': 8, 'designator': '', 'dvp': 16}
DVP 16 {'offset': 0, 'scale': 9.999999747378752e-05, 'decimals': 0, 'unit': 'L/ha'}
v3 parser: unknown table id '\x031.' at 54
```

출력 앞 일곱 줄이 위 바이트열과 같다. 이어서 요청 메시지와 전송 크기, 다시 읽은 일곱 레코드가 나오고, 마지막 줄이 버전 3 파서의 실패다.
:::

마지막 줄이 5절의 extended label 규칙을 보여 준다. 버전 3 TC처럼 extended 필드가 없다고 보고 읽으면, DVC 끝의 `03 31 2E 30`이 다음 레코드의 Table ID 자리로 읽혀 파싱이 깨진다. 협상된 버전과 레코드 형식이 어긋나면 이렇게 된다.

<small>근거: ISO 11783-10 Annex A, B.6.6, D.19, F.3.5.1</small>

::: tip 핵심 정리
- 실제 7섹션 살포기의 DDOP는 루트 DET 아래에 커넥터, 빈, 붐(Function)을 두고 붐 아래에 섹션 7개를 매단다. 살포량과 섹션 상태 DPD는 붐에, 총계는 루트에 둔다.
- 섹션 폭처럼 바뀌지 않는 값은 DPT, 살포량처럼 바뀌는 값은 DPD다. 섹션 상태는 섹션마다 두지 않고 Condensed Work State(161·290) 하나에 모은다.
- 모든 레코드는 Table ID 3바이트와 Object ID 2바이트로 시작하고, 수는 리틀 엔디언으로 싣는다. 문자열 앞에는 바이트 수 1바이트가 붙어서 뒤 칸 위치가 밀린다.
- DVC 끝에는 structure label(7바이트)과 localization label(7바이트)이 오고, 양쪽이 버전 4 이상일 때만 extended structure label이 더 붙는다.
- 48장 예제의 오브젝트 7개는 163바이트이고, 명령 바이트를 더한 164바이트를 TP로 보낸다.
:::

::: details 확인 문제
1. (개념) 섹션 폭(1,714mm)은 DPT로, 살포량 목표는 DPD로 담는 이유는 무엇인가?
2. (계산) 섹션이 5개이고 섹션 폭이 2,000mm인 붐에서, 가운데 섹션을 y=0에 둘 때 Section 1과 Section 5의 Y 오프셋은 얼마인가? 붐 전체 폭은 얼마인가?
3. (읽기) DPD 레코드 `44 50 44 14 00 02 00 00 09 00 FF FF`를 필드별로 풀어라.
4. (계산) designator `우측 섹션`의 길이 바이트 값은 얼마인가? 버전 3 TC에 그대로 보내도 되나?
5. (버전) 버전 4 클라이언트가 DVC 레코드를 보낼 때, 상대가 버전 3 TC일 때와 버전 4 TC일 때 레코드 끝이 어떻게 다른가? extended label을 쓰지 않는 버전 4 클라이언트가 버전 4 TC에 보낼 때는 어떤가?

**답 가이드**
1. 섹션 폭은 기계가 바뀌지 않는 한 고정된 상수라 TC가 바꿀 일이 없으므로 DPT다. 살포량은 처방 맵과 운전자 입력에 따라 태스크 중에 계속 바뀌므로 DPD다. 거꾸로 하면, 예를 들어 섹션이 꺼져서 줄어든 폭과 섹션 자체 폭의 변화를 구분할 수 없다.
2. 가운데는 Section 3이다. Section 1은 (1 − 3) × 2,000 = −4,000mm, Section 5는 (5 − 3) × 2,000 = 4,000mm다. 붐 전체 폭은 5 × 2,000 = 10,000mm다.
3. `44 50 44` Table ID `DPD`, `14 00` Object ID 20, `02 00` DDI 2, `00` properties 읽기 전용, `09` trigger = 8 + 1이라 on change와 time interval, `00` designator 없음, `FF FF` DVP 없음(NULL)이다.
4. 한글 4자 × 3바이트 + 공백 1바이트 = 13바이트이므로 길이 바이트는 `0D`(=13)다. 32바이트 이하라 버전 3 TC에도 보낼 수 있다.
5. 버전 3 TC에는 localization label에서 레코드가 끝난다(바이트 수 P와 extended label 없음). 버전 4 TC에는 localization label 뒤에 바이트 수 P와 extended label P바이트가 붙는다. extended label을 쓰지 않는 버전 4 클라이언트는 버전 4 TC에 바이트 수 0, 곧 `00` 1바이트를 붙인다.
:::

## 다음 챕터

- 다음: [50장 DDOP 전송 명령과 설계 점검](/study/isobus/50-ddop-commands-design)
