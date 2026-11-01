---
title: "TC 프로세스 데이터 기초"
description: "TC와 작업기가 주고받는 프로세스 데이터 메시지를 DDI, Element, 값 세 가지로 읽고, 8바이트 메시지 하나를 직접 조립하고 풀어 본다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, TaskController, TC, DDI, ProcessData, Measurement, Setpoint]
prev: /study/isobus/44-tc-multi-dl-functionality
next: /study/isobus/46-tc-commands-pdack
---

# TC 프로세스 데이터 기초

::: info 학습 목표
- 프로세스 데이터 메시지가 담는 세 가지(DDI, Element, 값)를 설명할 수 있다.
- 목표값(Setpoint)과 측정값(Measurement)의 차이, 그리고 둘의 차이인 제어 오차를 설명할 수 있다.
- "섹션 3에 200 L/ha" 같은 명령을 8바이트 메시지로 직접 조립하고, 받은 8바이트를 거꾸로 풀 수 있다.
- 클라이언트(작업기)가 TC에 값을 보내도 되는 세 가지 경우를 말할 수 있다.
- 가변 살포에서 처방 맵, DDOP, VT 오브젝트 풀이 각각 맡는 일을 설명할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [41장 TC 기초](/study/isobus/41-tc-basics), [43장 TC 연결 관리](/study/isobus/43-tc-connection), [9장 J1939 메시지 구조](/study/isobus/09-j1939-message)(여러 바이트 값을 낮은 자리 바이트부터 싣는 규칙)
- 이 장에서 처음 나오는 말
  - 프로세스 데이터(Process Data): TC와 작업기가 작업 중에 주고받는 숫자 값. 그 값을 나르는 메시지도 같은 이름으로 부른다.
  - DDI(Data Dictionary Identifier): 값의 종류(살포량, 유량, 작업 상태 등)를 가리키는 표준 번호
  - Element(Device Element): 작업기 안의 한 부분(펌프, 탱크, 붐의 섹션 등)과 그 부분에 붙인 번호
  - Setpoint와 Measurement: TC가 "이 값에 맞춰라"고 내리는 목표값과, 작업기가 센서로 실제로 잰 측정값
  - 분해능(resolution): 메시지 안의 정수 1이 실제로 얼마인지 정한 크기
  - 클라이언트(TC 클라이언트): TC에 연결해 일하는 작업기 쪽 ECU(Electronic Control Unit, 전자 제어 장치)
:::

아파트 관리실이 검침 기록을 남기는 장면을 떠올려 보자. "305호의 수도 계량기가 120"처럼 어느 집, 어느 계량기, 숫자 세 가지만 있으면 기록 한 줄이 된다. TC(Task Controller, 작업 계획에 따라 작업기를 제어하고 작업 기록을 남기는 장치)와 작업기가 주고받는 프로세스 데이터 메시지도 같다. 작업기의 어느 부분(Element), 무슨 값(DDI), 숫자(값) 세 가지에 "알려 달라" 또는 "이 값에 맞춰라" 같은 명령 하나를 붙여 8바이트에 담는다. 이 장은 세 가지를 하나씩 익힌 뒤, 메시지 하나를 바이트 단위로 직접 조립해 본다.

## 1. 프로세스 데이터 메시지가 담는 세 가지

이 절은 프로세스 데이터 메시지 한 통이 무엇으로 이루어지는지 큰 그림을 먼저 본다. 뒤의 절들은 여기 나오는 세 가지를 하나씩 자세히 보는 내용이다.

### 왜 필요한가

붐 스프레이어(긴 팔 모양의 붐에 노즐을 줄지어 단 액체 살포기)로 밭에 약을 뿌린다고 하자. 붐은 몇 칸으로 나뉘어 있고, 그 한 칸을 섹션(Section)이라고 부른다. TC는 처방 맵(밭의 위치마다 뿌릴 양을 적은 지도)을 보고 "섹션 3은 지금부터 200 L/ha로 뿌려라"라고 지시해야 한다. 작업기는 거꾸로 "섹션 3에서는 실제로 198 L/ha가 나가고 있다"고 알려야 한다. 이 지시와 보고가 모두 프로세스 데이터 메시지다.

### 쉽게 말하면: 표의 한 칸

작업기를 큰 표 하나로 생각하면 쉽다.

- 행은 작업기의 부분이다. 펌프, 탱크, 붐의 섹션 같은 것이다. 이것이 <strong>Element</strong>다.
- 열은 값의 종류다. 목표 살포량, 실제 살포량, 실제 유량 같은 것이다. 이것이 <strong>DDI</strong>다.
- 칸 안의 숫자가 그 부분의 그 값이다.

메시지 하나는 이 표의 칸 하나를 가리키고(Element와 DDI), 그 칸의 숫자를 알려 주거나 바꾸라고(명령과 값) 말한다.

![작업기를 표로 본 그림: 행은 Element(펌프, 섹션 2, 섹션 3), 열은 DDI(1 목표 살포량, 2 실제 살포량, 37 실제 유량), 칸은 값이다. 명령 3, Element 3, DDI 1, 값 2,000,000을 담은 메시지가 섹션 3의 목표 살포량 칸을 가리킨다](/images/study-isobus/45-process-data-table-light.png)
![작업기를 표로 본 그림: 행은 Element(펌프, 섹션 2, 섹션 3), 열은 DDI(1 목표 살포량, 2 실제 살포량, 37 실제 유량), 칸은 값이다. 명령 3, Element 3, DDI 1, 값 2,000,000을 담은 메시지가 섹션 3의 목표 살포량 칸을 가리킨다](/images/study-isobus/45-process-data-table-dark.png)

비유가 맞지 않는 곳도 있다. 실제 작업기의 표는 모든 칸이 차 있지 않다. 그림에서 펌프 행의 살포량 칸이 비어 있듯이, 부분마다 다룰 수 있는 값의 종류가 정해져 있다. 어느 부분이 어떤 DDI를 다루는지는 작업기가 연결할 때 TC에 올리는 DDOP(Device Descriptor Object Pool, 작업기가 자기 구조와 다룰 수 있는 값을 적어 보내는 데이터 묶음)에 적혀 있다([48장](/study/isobus/48-ddop-basics)). 없는 칸을 가리키는 메시지는 거절된다([46장](/study/isobus/46-tc-commands-pdack)의 PDACK).

### 정확한 정의

| 구성 요소 | 뜻 | 크기 | 예 |
|---|---|---|---|
| 명령(Command) | 이 메시지로 무엇을 하는지 | 4비트 | 3 = 값 전달, 2 = 값 요청 |
| Element 번호 | 작업기의 어느 부분인지 | 12비트(0~4095) | 3 = 섹션 3 |
| DDI | 어떤 종류의 값인지 | 16비트(0~65535) | 1 = 면적당 목표 살포량 |
| 값(Value) | 숫자 자체 | 32비트 부호 있는 정수 | 2,000,000 |

다 더하면 4 + 12 + 16 + 32 = 64비트, 정확히 8바이트다. CAN 데이터 프레임 하나에 실을 수 있는 최대 길이(8바이트)에 꼭 맞는다. 값이 "부호 있는 정수"라는 말은 음수도 담을 수 있다는 뜻이다(약 −21억~+21억).

### 예시

"섹션 3의 목표 살포량을 200 L/ha로 맞춰라"는 다음 네 값이 된다.

1. 명령: 3(값 전달)
2. Element 번호: 3(이 작업기가 섹션 3에 붙인 번호)
3. DDI: 1(면적당 목표 살포량)
4. 값: 2,000,000(200 L/ha를 정해진 규칙으로 바꾼 정수. 5절에서 계산한다)

이 장은 메시지를 `[DDI=1, Element=3, Value=200]`처럼 줄여 적기도 한다. 이 표기의 Value는 읽기 쉽게 물리 단위(L/ha)로 적은 것이다. 실제 버스에는 분해능에 맞춰 바꾼 정수가 실린다.

::: tip 정리
- 프로세스 데이터 메시지 = 명령 + Element 번호(어느 부분) + DDI(무슨 값) + 값(숫자).
- 네 가지를 합하면 8바이트, CAN 프레임 하나다.
:::

## 2. DDI: 값의 종류를 가리키는 번호

이 절은 메시지의 "무슨 값" 자리인 DDI를 본다. DDI마다 단위와 분해능이 정해져 있어서, 같은 정수라도 DDI가 다르면 뜻이 완전히 달라진다.

<strong>DDI</strong>(Data Dictionary Identifier, 데이터 사전 식별자)는 TC 프로세스 데이터 항목을 구분하는 표준화된 16비트 번호이다. 데이터 사전은 DDI 번호마다 이름, 단위, 분해능, 값 범위를 정리해 둔 목록이다. 이 목록은 ISO 11783-11(DDI 목록을 정하는 표준 문서)이 지정한 온라인 사전으로 관리된다([47장](/study/isobus/47-tc-totals-logging-peer)).

> DDI는 "어떤 종류의 데이터인가"를 나타낸다. 살포량인지, 속도인지, 면적인지를 숫자로 표현한다.

값을 주고받는 Process Data 메시지는 DDI를 포함하여 어떤 데이터를 주고받는지 명시한다. 주요 DDI는 다음과 같다. "방향"은 그 값이 보통 어느 쪽에서 어느 쪽으로 가는지다. 이름에 Setpoint가 붙은 목표값은 TC가 작업기에 내리고, Actual이 붙은 실제값은 작업기가 TC에 올린다.

| DDI | 이름 | 방향 | 설명 |
|-----|------|------|------|
| **1** | Setpoint Volume Per Area Application Rate | TC → 작업기 | 면적당 목표 살포량 (액체) |
| **2** | Actual Volume Per Area Application Rate | 작업기 → TC | 면적당 실제 살포량 (센서 측정) |
| **6** | Setpoint Mass Per Area Application Rate | TC → 작업기 | 면적당 목표 살포 질량 (고체) |
| **7** | Actual Mass Per Area Application Rate | 작업기 → TC | 면적당 실제 살포 질량 |
| **36** | Setpoint Volume Per Time Application Rate | TC → 작업기 | 시간당 목표 유량 |
| **37** | Actual Volume Per Time Application Rate | 작업기 → TC | 시간당 실제 유량 |
| **141** | Actual Work State | 작업기 → TC | 요소의 실제 작업 상태 (2비트: 00=Off, 01=On, 10=오류, 11=미설치) |
| **289** | Setpoint Work State | TC → 작업기 | 개별 요소의 ON/OFF 목표 명령 (DDI 141의 명령 짝) |
| **290** | Setpoint Condensed Work State (1-16) | TC → 작업기 | 섹션 1~16의 ON/OFF 일괄 명령 (섹션당 2비트) |

DDI 141의 "2비트"는 값 0~3 네 가지만 쓴다는 뜻이다. 00(0)은 꺼짐, 01(1)은 켜짐, 10(2)은 오류, 11(3)은 미설치다. DDI 290의 "섹션당 2비트"는 32비트 값을 2비트씩 16칸으로 나눠 섹션 16개의 ON/OFF 명령을 한 메시지에 담는다는 뜻이다.

전체 DDI 목록은 [isobus.net](https://www.isobus.net/isobus/dDI)에서 확인할 수 있다. 현재 약 600개 이상의 DDI가 정의되어 있다.

### DDI가 없으면 TC는 데이터를 해석할 수 없다

TC가 수신하는 메시지에는 32비트 정수 값이 포함된다. 그 값이 살포량인지, 유량인지, 속도인지는 오직 DDI가 결정한다. DDI 없이 값만 전달되면 TC는 바이트 데이터의 의미를 전혀 해석할 수 없다. DDI는 데이터의 "단위표"이자 "해석 키"이다.

### Resolution(분해능)과 단위

메시지의 값 자리에는 소수점 없는 정수만 들어간다. 그래서 DDI마다 "정수 1이 실제로 얼마인지"를 정해 둔다. 이것이 분해능이다. 분해능이 0.01이면 버스에 실린 정수(원시값, raw 값) 2,000,000은 실제로 2,000,000 × 0.01 = 20,000이다. [9장](/study/isobus/09-j1939-message)에서 본 SPN 값 변환과 같은 원리다.

각 DDI에는 표준으로 정해진 분해능과 단위가 있다. 클라이언트는 이 규칙에 따라 정수 값을 인코딩하여 전송하고, TC는 동일한 규칙으로 디코딩한다.

| DDI | 단위 | 분해능 | 예시 |
|-----|------|--------|------|
| 1 (Setpoint Volume Per Area) | mm³/m² | 0.01 | 원시값 2,000,000 → 20,000 mm³/m² = 200 L/ha |
| 2 (Actual Volume Per Area) | mm³/m² | 0.01 | 원시값 1,980,000 → 19,800 mm³/m² = 198 L/ha |
| 36 (Setpoint Volume Per Time) | mm³/s | 1 | 원시값 250,000 → 250,000 mm³/s = 15 L/min |
| 37 (Actual Volume Per Time) | mm³/s | 1 | 원시값 246,667 → 246,667 mm³/s ≈ 14.8 L/min |

표 첫 줄을 풀어 읽으면 이렇다. 원시값 2,000,000에 분해능 0.01을 곱하면 20,000 mm³/m²다. 아래 환산으로 바꾸면 200 L/ha다.

mm³/m²는 μL/m²와 같은 값이며, 1 L/ha = 100 mm³/m²다. 1 L는 1,000,000 mm³이고 1 ha는 10,000 m²이므로 1,000,000 ÷ 10,000 = 100이다. 시간당 유량은 1 L/min = 16,666.7 mm³/s로 환산된다(1,000,000 mm³ ÷ 60초). 분해능이 다른 DDI끼리 값을 교환하면 단위 불일치가 발생한다. TC 구현 시 DDI별 스케일 팩터(분해능)를 반드시 적용해야 한다.

### Setpoint DDI와 Actual DDI의 쌍 구조

에어컨 리모컨에 "설정 온도"와 "현재 온도"가 따로 있듯이, 하나의 물리량에도 목표값과 실제값이 따로 있다. ISOBUS 표준은 같은 물리량에 대해 Setpoint DDI와 Actual DDI를 쌍으로 정의한다. TC는 Setpoint DDI로 목표값을 명령하고, 클라이언트는 Actual DDI로 실제 측정값을 보고한다.

| 물리량 | <strong>Setpoint</strong> DDI (TC → 작업기) | <strong>Actual</strong> DDI (작업기 → TC) |
|--------|------|------|
| 면적당 살포량 | DDI 1 | DDI 2 |
| 시간당 유량 | DDI 36 | DDI 37 |
| 면적당 살포 질량 | DDI 6 | DDI 7 |
| 작업 상태(Work State) | DDI 289 | DDI 141 |

이 쌍 구조 덕분에 TC는 목표값(DDI 1)과 실제값(DDI 2)을 같은 물리 단위로 비교하여 제어 오차를 계산할 수 있다(6절).

::: tip 정리
- DDI는 값의 종류 번호다. 번호마다 단위와 분해능이 정해져 있다.
- 실제 값 = 원시값 × 분해능. 200 L/ha는 DDI 1에서 원시값 2,000,000이다.
- 같은 물리량에 Setpoint DDI(목표)와 Actual DDI(실제)가 짝으로 있다.
:::

## 3. Element: 기계의 어느 부분인지 가리키는 번호

이 절은 메시지의 "어느 부분" 자리인 Element를 본다. 같은 DDI라도 Element 번호가 다르면 다른 부분의 값이다. 섹션 3의 살포량과 섹션 1의 살포량을 구별하는 것이 Element 번호다.

<strong>Device Element(DeviceElement)</strong>는 작업기의 논리적 구성 단위이다. 물리적 장치를 계층적으로 표현한다. "논리적"이라는 말은 부품 하나하나가 아니라, TC가 제어하고 기록할 단위로 작업기를 나눈 것이라는 뜻이다.

### Element Type

Element마다 종류(type)가 있고, DDOP 안에서 숫자 코드로 적는다.

| 코드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| 1 | **Device** | 전체 장치 (최상위, DDOP당 1개, Element Number=0) | 살포기 전체 |
| 2 | **Function** | 기능 단위 | 살포 펌프, 교반기 |
| 3 | **Bin** | 저장 용기 | 약액 탱크, 비료 빈 |
| 4 | **Section** | 분할 구획 | 붐 스프레이어의 좌/우 섹션 |
| 5 | **Unit** | Section 하위의 가장 세분화된 주소 지정 단위 | 노즐, 파종 로우 유닛 |
| 6 | **Connector** | 연결 포인트 | 히치 연결부 |
| 7 | **Navigation Reference** | 위치 기준점 | GPS 안테나 기준 작업 위치 오프셋 |

각 Element는 <strong>Element Number</strong>(Element 번호)로 식별된다. 예를 들어, Section 1은 Element Number 1, Section 2는 Element Number 2로 구분된다.

Element 번호는 작업기 제조사가 DDOP를 만들 때 붙인다. 그래서 "몇 번째 섹션"과 Element 번호가 같을 필요는 없다. 아래 그림의 살포기는 왼쪽 섹션(Section 1)에 Element 3을 붙였다. 4절부터 나오는 예제는 섹션 3에 Element 3을 붙인 살포기를 가정한다.

![살포기의 Element 계층: 살포기 전체(Device, Element 0) 아래에 살포 펌프(Function, Element 1)와 약액 탱크(Bin, Element 2)가 있고, 살포 펌프 아래에 왼쪽·가운데·오른쪽 섹션(Section, Element 3·4·5)이 있다](/images/study-isobus/45-element-tree-light.png)
![살포기의 Element 계층: 살포기 전체(Device, Element 0) 아래에 살포 펌프(Function, Element 1)와 약액 탱크(Bin, Element 2)가 있고, 살포 펌프 아래에 왼쪽·가운데·오른쪽 섹션(Section, Element 3·4·5)이 있다](/images/study-isobus/45-element-tree-dark.png)

### Element 간 부모-자식 관계

Element는 계층 구조를 이룬다. <strong>Device</strong>가 최상위이며, 그 아래에 <strong>Function</strong>과 <strong>Bin</strong>이 중간 계층으로 위치한다. <strong>Section</strong>은 이 예시에서 가장 말단에 해당하며, 실제로는 그 아래에 노즐 단위인 <strong>Unit</strong>이 더 세분화된 계층으로 올 수 있다. TC가 특정 Element에 명령을 보낼 때는 해당 Element Number를 지정한다. 부모 Element에 명령을 보내면 그 아래 모든 자식 Element에 적용되는 것이 일반적이다.

TC가 특정 섹션에만 명령을 보내려면 그 섹션의 Element Number를 명시적으로 지정해야 한다. 예를 들어 오른쪽 섹션(Section 3, Element 5)에만 DDI 289(Setpoint Work State)로 OFF 명령을 보내면, 나머지 두 섹션(Section 1, Section 2)은 살포를 계속하고 오른쪽 섹션만 살포를 멈춘다. 클라이언트는 실제로 반영된 상태를 DDI 141(Actual Work State)로 되돌려 보고한다. 이 방식이 붐 스프레이어의 섹션별 살포 제어(Section Control)를 가능하게 한다.

::: tip 정리
- Element는 작업기의 부분(Device, Function, Bin, Section, Unit 등)이고, 번호로 가리킨다.
- Element 번호는 제조사가 DDOP에서 정한다. 섹션 순서와 번호가 같을 필요는 없다.
- 섹션 하나의 Element 번호를 지정하면 그 섹션만 켜고 끌 수 있다.
:::

## 4. 값을 주고받는 메시지: Value command와 Request value

이 절은 TC와 클라이언트가 실제로 어떤 메시지로 값을 주고받는지, 그 8바이트가 어떻게 배치되는지 본다.

TC와 클라이언트는 <strong>Process Data</strong> 메시지(PGN: 0x00CB00)를 통해 값을 주고받는다. PGN(Parameter Group Number)은 메시지의 종류를 가리키는 번호다([9장](/study/isobus/09-j1939-message)). 0x00CB00은 10진수로 51968이고, 줄여서 `0xCB00`이라고도 쓴다. 값 설정, 값 요청, 측정 설정, 확인 응답이 모두 이 PGN 하나를 쓰고, 첫 4비트의 명령으로 구별한다.

### 메시지 방향

| 메시지 | 방향 | Command 코드 | 설명 |
|--------|------|------|------|
| **Process Data Value Command** | TC → 클라이언트 | `0x3` (Value command) | 설정값(Setpoint) 전달, 작업기에 목표값 명령 |
| **Process Data Value** | 클라이언트 → TC | `0x3` (Value command) | 측정값(Measurement) 보고 |
| **Process Data Value Request** | TC → 클라이언트 | `0x2` (Request value) | 특정 DDI의 현재값을 1회 요청 |

표에서 보듯 목표값을 내릴 때와 측정값을 올릴 때 같은 명령 3을 쓴다. 3은 "값을 담은 메시지"라는 뜻이고, 누가 누구에게 보냈느냐로 설정인지 보고인지가 갈린다(46장).

Process Data 메시지의 첫 니블은 이처럼 `0x0`~`0xF`(0~15) 범위의 command 값으로 메시지 종류를 구분한다. 니블(nibble)은 4비트, 즉 16진수 한 자리다. 값 설정과 동시에 수신 확인이 필요하면 `0xA`(=10, Set Value and Acknowledge)를 쓰며, 이 경우 응답은 아래에서 다룰 PDACK(`0xD`=13)로 온다. 16가지 명령 전체는 [46장](/study/isobus/46-tc-commands-pdack)에서 본다.

### 주고받는 순서

![TC와 클라이언트의 값 교환 순서: TC가 Value command로 섹션 3(Element 3)의 DDI 1 목표 200 L/ha를 보내면 클라이언트가 DDI 2 실제 198 L/ha를 보고한다. 이어 TC가 Value Request로 펌프(Element 1)의 DDI 37을 요청하면 클라이언트가 15 L/min으로 답한다](/images/study-isobus/45-value-request-sequence-light.png)
![TC와 클라이언트의 값 교환 순서: TC가 Value command로 섹션 3(Element 3)의 DDI 1 목표 200 L/ha를 보내면 클라이언트가 DDI 2 실제 198 L/ha를 보고한다. 이어 TC가 Value Request로 펌프(Element 1)의 DDI 37을 요청하면 클라이언트가 15 L/min으로 답한다](/images/study-isobus/45-value-request-sequence-dark.png)

그림 위쪽은 TC가 목표값을 내리고 클라이언트가 실제값을 올리는 흐름이다. 아래쪽은 TC가 펌프의 실제 유량을 한 번 물어보고(Request value) 클라이언트가 값으로 답하는 흐름이다. 실선은 TC가 보내는 메시지, 점선은 클라이언트가 보내는 메시지다.

### PGN 0x00CB00 메시지 구조

Process Data 메시지는 총 8바이트로 구성되며, 필드 순서는 <strong>Command → Element Number → DDI → Value</strong>다.

표 읽는 법은 다음과 같다.
- 바이트 번호는 1부터 센다(Byte 1~8).
- 한 바이트 안의 비트는 가장 낮은 자리를 bit 1, 가장 높은 자리를 bit 8로 센다. "하위 4비트"는 bit 4~1, "상위 4비트"는 bit 8~5다.
- 여러 바이트에 걸친 값(DDI, Value)은 낮은 자리 바이트가 먼저 온다(리틀 엔디언, 9장).

| 바이트 | 필드 | 설명 |
|--------|------|------|
| Byte 1 (하위 4비트) | Command | 명령 코드 (2=Request Value, 3=Value Command, A=Set Value and Acknowledge 등) |
| Byte 1 (상위 4비트) + Byte 2 | Element Number | 대상 Element 번호 (12비트, 0~4095) |
| Byte 3~4 | DDI | 데이터 항목 번호 (16비트) |
| Byte 5~8 | Value | 32비트 부호 있는 정수 값 |

Element Number가 DDI보다 앞선 바이트에 위치한다는 점에 주의한다. "어느 요소의 값인가"를 먼저 지정하고, 그 뒤에 "어떤 종류의 값인가(DDI)"를 붙이는 순서다. 이 표를 숫자로 채우는 과정은 5절에서 단계별로 본다.

### 수락·거부 응답: PDACK

명령을 보낸 쪽은 상대가 받아들였는지 알아야 할 때가 있다. PDACK(Process Data Acknowledge)는 그 답장이다. 클라이언트와 TC는 명령을 수락·거부할 때 <strong>PDACK</strong>(command `0xD`)로 응답할 수 있다. 클라이언트가 여러 ECU로 이루어진 작업기라면 대표로 통신하는 Working Set Master([26장](/study/isobus/26-isobus-network-mgmt))가 보낸다. PDACK에는 Element Number·DDI·오류 코드(0=정상, 그 외 비트=명령 미지원/잘못된 Element/DDI 미지원/트리거 미지원/설정 불가/유효 범위 초과 등)를 담아 반환한다. 불필요한 버스 부하를 피하기 위해, 오류 코드 0(정상)인 PDACK는 Measurement 명령(Command 4~8)과 Set Value and Acknowledge(`0xA`)에 대해서만 보내고 나머지 명령에는 생략한다.

그래서 Command 3으로 목표값을 보냈을 때는 받아들여져도 답이 없고, 거절될 때만 PDACK가 온다. PDACK의 바이트와 오류 비트는 [46장](/study/isobus/46-tc-commands-pdack)에서 연다.

::: tip 정리
- 프로세스 데이터는 PGN 0xCB00 하나로 오가고, Byte 1 하위 4비트의 명령으로 종류를 나눈다.
- 목표값 전달과 측정값 보고는 둘 다 Command 3이다. 값 요청은 Command 2다.
- 배치는 Command(4비트) → Element 번호(12비트) → DDI(16비트) → 값(32비트)이다.
:::

## 5. 메시지 하나를 손으로 조립하기

지금까지는 `[DDI=1, Element=3, Value=200]`처럼 필드를 나열한 표기로 메시지를 설명했다. 실제 버스에는 이 값들이 8바이트 안에 정확한 비트 위치로 눌러 담겨 나간다. 4절의 바이트 배치표(Command → Element Number → DDI → Value)를 이번에는 숫자로 끝까지 채워본다. 순서는 세 단계다. (1) 물리값을 정수로 바꾸고, (2) Byte 1~2에 명령과 Element 번호를 넣고, (3) Byte 3~8에 DDI와 값을 넣는다.

### 목표: Section 3에 200 L/ha 명령하기

TC가 Section 3(Element Number 3)에 DDI 1(Setpoint Volume Per Area Application Rate)로 목표 살포량 200 L/ha를 명령하는 상황이다. 2절의 분해능 표에 따르면 DDI 1의 단위는 mm³/m², 분해능은 0.01이다.

### 1단계: 물리값을 정수로 바꾸기

1. 물리량 → mm³/m² 환산: 1 L/ha = 100 mm³/m²이므로 200 L/ha = 20,000 mm³/m²
2. mm³/m² → raw 값 환산: raw = 물리값 ÷ 분해능 = 20,000 ÷ 0.01 = 2,000,000

즉 버스에 실어야 하는 32비트 정수는 <strong>2,000,000</strong>(`0x1E8480`)이다. 4바이트를 꽉 채워 쓰면 `0x001E8480`이고, 높은 자리 바이트부터 읽으면 `00`, `1E`, `84`, `80`이다.

### 2단계: Byte 1~2에 Command 4비트와 Element Number 12비트를 나누어 담기

4절에서 다룬 대로 Command와 Element Number는 8비트 경계를 걸쳐 나뉜다. 헷갈리는 지점이 바로 여기다.

| 필드 | 비트 폭 | 위치 |
|---|---|---|
| Command | 4비트 | Byte 1의 <strong>하위</strong> 4비트(bit 4~1) |
| Element Number 하위 4비트 | 4비트 | Byte 1의 <strong>상위</strong> 4비트(bit 8~5) |
| Element Number 상위 8비트 | 8비트 | Byte 2 전체 |

Element Number는 한 바이트에 다 담기지 않는다. <strong>하위 4비트는 Command와 한 바이트를 나눠 쓰고, 남은 상위 8비트가 다음 바이트를 통째로 차지</strong>한다. Command가 Byte 1의 절반을 먼저 차지하고 있기 때문에 생기는 배치다.

이 명령은 Command = 3(Value command), Element Number = 3(Section 3)이다. Element Number 3을 12비트로 쓰면 `0000 0000 0011`이므로, 하위 4비트는 `0011`, 상위 8비트는 `0000 0000`이다.

| 니블 | 값 | 비트 |
|---|---|---|
| Byte 1 bit 8~5 (Element 하위 4비트) | 3 | `0011` |
| Byte 1 bit 4~1 (Command) | 3 | `0011` |
| Byte 1 전체 | `0x33` | `0011 0011` |
| Byte 2 (Element 상위 8비트) | 0 | `0000 0000` |

Element Number가 16 미만이면 Byte 2는 항상 `0x00`이 된다. Element Number가 16 이상으로 올라가야 비로소 Byte 2에 값이 실린다. 예를 들어 Element Number 20(`0001 0100`)이면 하위 4비트 `0100`이 Byte 1 상위 니블에, 상위 8비트 `0000 0001`이 Byte 2 전체에 들어가 Byte 2가 `0x01`이 된다.

### 3단계: Byte 3~8 채우기

| 바이트 | 필드 | 값 |
|---|---|---|
| Byte 3~4 | DDI(LSB, MSB) | DDI=1 → `0x01 0x00` |
| Byte 5~8 | Value(부호 있는 32비트, LSB부터) | 2,000,000 → `0x80 0x84 0x1E 0x00` |

LSB(Least Significant Byte)는 가장 낮은 자리 바이트, MSB(Most Significant Byte)는 가장 높은 자리 바이트다. DDI 1은 16비트로 `0x0001`이라 낮은 자리 `01`이 Byte 3, 높은 자리 `00`이 Byte 4에 간다. 값도 같은 규칙이다. 1단계에서 높은 자리부터 읽은 `00`, `1E`, `84`, `80`을 뒤집어 낮은 자리 `80`부터 Byte 5~8에 싣는다.

완성된 8바이트:

```
33 00 01 00 80 84 1E 00
```

![Process Data 8바이트 조립: Byte 1은 상위 니블 0011(Element 하위 4비트)과 하위 니블 0011(Command 3)이 합쳐진 0x33, Byte 2는 Element 상위 8비트 00, Byte 3~4는 DDI 1의 01 00, Byte 5~8은 2,000,000(0x001E8480)을 낮은 자리 바이트부터 실은 80 84 1E 00이다](/images/study-isobus/45-frame-assembly-light.png)
![Process Data 8바이트 조립: Byte 1은 상위 니블 0011(Element 하위 4비트)과 하위 니블 0011(Command 3)이 합쳐진 0x33, Byte 2는 Element 상위 8비트 00, Byte 3~4는 DDI 1의 01 00, Byte 5~8은 2,000,000(0x001E8480)을 낮은 자리 바이트부터 실은 80 84 1E 00이다](/images/study-isobus/45-frame-assembly-dark.png)

그림 아래쪽의 교차하는 화살표가 리틀 엔디언이다. 값의 가장 낮은 자리 바이트 `80`이 Byte 5로, 가장 높은 자리 바이트 `00`이 Byte 8로 간다.

### 분해: 수신한 8바이트에서 되돌리기

이번엔 반대 방향이다. TC가 Section 3의 DDI 2(Actual Volume Per Area Application Rate)를 Request Value(Command 2)로 요청했고, 클라이언트가 다음 8바이트로 응답했다고 하자.

```
33 00 02 00 60 36 1E 00
```

아래 표의 연산 기호는 이런 뜻이다. `&`는 필요한 비트만 남기는 비트 AND다. `>>`와 `<<`는 비트를 오른쪽·왼쪽으로 미는 시프트다. `|`는 두 값을 합치는 비트 OR다. 예를 들어 `0x33 & 0x0F`는 아래 4비트만 남겨 3을 얻고, `0x33 >> 4`는 위 4비트를 아래로 내려 3을 얻는다.

| 단계 | 연산 | 결과 |
|---|---|---|
| Command | Byte1 bit 4~1 | `0x33 & 0x0F` = 3 → Value command(값 응답) |
| Element Number | (Byte1 bit 8~5) \| (Byte2 << 4) | `(0x33 >> 4) \| (0x00 << 4)` = 3 → Section 3 |
| DDI | Byte3 \| (Byte4 << 8) | `0x02 \| (0x00 << 8)` = 2 → Actual Volume Per Area |
| Value(raw) | Byte5~8, LSB 우선, 부호 있는 32비트 | `0x1E3660` = 1,980,000 |

마지막 줄은 Byte 5~8 `60 36 1E 00`을 높은 자리부터 다시 놓아 `0x001E3660`을 만들고 10진수로 바꾼 것이다.

### 분해능을 반영해야 진짜 값이 나온다

raw 값 1,980,000은 그 자체로는 단위가 없다. DDI 2의 분해능 0.01을 곱해야 mm³/m²가 되고, 다시 100으로 나눠야 L/ha가 된다.

1,980,000 × 0.01 = 19,800 mm³/m² → 19,800 ÷ 100 = <strong>198 L/ha</strong>

2절 표의 값과 정확히 일치한다. 만약 분해능을 반영하지 않고 raw 200을 그대로 DDI 1에 실어 보냈다면 어떻게 될까. 조립 예제와 같은 8바이트 구조에 Value만 200을 넣으면 `33 00 01 00 C8 00 00 00`이 되고, 수신 측이 규정대로 0.01을 곱하면 200 × 0.01 = 2 mm³/m² = 0.02 L/ha로 해석된다. 목표한 200 L/ha의 1만분의 1이다. <strong>정수 200을 "200 L/ha"로 착각해 그대로 실어 보내는 것</strong>이 현장에서 흔히 나는 실수다.

### 같은 대상, 다른 Command: Byte 1이 어떻게 바뀌는가

Element Number(3)와 DDI(1)는 그대로 두고 Command만 바꿔보면, Byte 1의 상위 니블은 고정된 채 하위 니블만 움직인다.

| Command | 의미 | Byte 1 | 전체 프레임 |
|---|---|---|---|
| 2 | Request value(값 요청) | `0x32` | `32 00 01 00 00 00 00 00` |
| 3 | Value command(설정값 전달) | `0x33` | `33 00 01 00 80 84 1E 00` |
| A | Set Value and Acknowledge(설정 + 수신 확인 요구) | `0x3A` | `3A 00 01 00 80 84 1E 00` |

Request value(2)의 Value 필드는 위 표에서 0으로 채웠다. 값을 요청하는 메시지라 응답 전까지는 채울 값이 없기 때문이다. 다만 이 자리를 반드시 0으로 채워야 한다는 규칙이 표준에 적혀 있지는 않다. Command만 3에서 A로 바뀌어도 Byte 3~8은 동일하다는 점에 주목한다. 두 메시지의 차이는 "클라이언트가 PDACK로 수신 확인을 보내야 하는가"뿐이며, 가리키는 대상과 값은 같다.

아래 코드는 이 절의 조립과 분해를 함수로 옮긴 것이다. `build_frame`은 네 값을 8바이트로 만들고, `parse_frame`은 8바이트를 네 값으로 되돌린다.

:::details 파이썬으로 검산해 보기
```python
def build_frame(command, element, ddi, value):
    byte1 = ((element & 0xF) << 4) | (command & 0xF)
    byte2 = (element >> 4) & 0xFF
    ddi_bytes = ddi.to_bytes(2, "little")
    value_bytes = value.to_bytes(4, "little", signed=True)
    return bytes([byte1, byte2]) + ddi_bytes + value_bytes


def parse_frame(frame):
    command = frame[0] & 0x0F
    element = (frame[0] >> 4) | (frame[1] << 4)
    ddi = frame[2] | (frame[3] << 8)
    value = int.from_bytes(frame[4:8], "little", signed=True)
    return command, element, ddi, value


# 조립: Section 3(Element=3), DDI 1, 200 L/ha
raw = int(200 * 100 / 0.01)          # 200 L/ha -> 20,000 mm3/m2 -> raw
frame = build_frame(command=3, element=3, ddi=1, value=raw)
print(frame.hex(' ').upper())        # 33 00 01 00 80 84 1E 00

# 분해: 수신 프레임에서 필드 복원
received = bytes.fromhex("33 00 02 00 60 36 1E 00")
command, element, ddi, value = parse_frame(received)
print(command, element, ddi, value)  # 3 3 2 1980000
print(value * 0.01 / 100)            # 198.0 (L/ha)

# 해상도를 빼먹은 경우
mistake = build_frame(command=3, element=3, ddi=1, value=200)
print(mistake.hex(' ').upper())      # 33 00 01 00 C8 00 00 00
print(200 * 0.01 / 100)              # 0.02 (L/ha), 의도한 200의 1/10000
```
:::

실행하면 주석에 적은 값이 그대로 나온다. 코드 주석의 "해상도"는 이 장의 분해능과 같은 말이다. 마지막 두 줄은 분해능을 빼먹었을 때 200 L/ha가 0.02 L/ha로 읽히는 실수를 보여 준다.

::: tip 정리
- 물리값 ÷ 분해능 = 원시값. 200 L/ha는 DDI 1에서 2,000,000이다.
- Byte 1은 위 4비트가 Element 번호의 아래 4비트, 아래 4비트가 명령이다. Byte 2는 Element 번호의 위 8비트다.
- DDI와 값은 낮은 자리 바이트부터 싣는다. 받은 값에는 분해능을 곱해야 실제 값이 된다.
:::

## 6. Setpoint와 Measurement: 목표값과 측정값

이 절은 TC가 내리는 목표값과 작업기가 올리는 측정값을 나눠 보는 이유를 본다. TC가 목표를 내려도 기계가 정확히 그 값을 내지는 못한다. 그래서 둘을 따로 주고받고 비교한다.

TC 프로세스 데이터는 크게 두 가지로 구분된다.

| 구분 | 생성 주체 | 방향 | 의미 |
|------|-----------|------|------|
| **Setpoint** | TC | TC → 작업기 | TC가 처방 맵에서 조회한 목표 값 |
| **Measurement** | 작업기 센서 | 작업기 → TC | 작업기가 실제로 측정한 값 |

![Setpoint와 Measurement의 관계: 처방 맵에서 조회한 목표값(DDI 1 = 200 L/ha)이 Value Command로 작업기 ECU에 가고, 유량 센서가 잰 실제값(DDI 2 = 198 L/ha)이 Process Data Value로 TC에 온다. 두 값의 차이가 제어 오차 2 L/ha다](/images/study-isobus/45-setpoint-measurement-light.png)
![Setpoint와 Measurement의 관계: 처방 맵에서 조회한 목표값(DDI 1 = 200 L/ha)이 Value Command로 작업기 ECU에 가고, 유량 센서가 잰 실제값(DDI 2 = 198 L/ha)이 Process Data Value로 TC에 온다. 두 값의 차이가 제어 오차 2 L/ha다](/images/study-isobus/45-setpoint-measurement-dark.png)

**제어 오차(Control Error)** = Setpoint − Measurement

그림의 예에서 목표는 200 L/ha, 측정은 198 L/ha이므로 제어 오차는 2 L/ha다. 작업기의 제어 시스템은 이 오차를 최소화하도록 밸브 개도량(밸브가 열린 정도), 펌프 속도 등을 조절한다. TC는 오차가 허용 범위를 벗어나면 알람을 발생시킬 수 있다.

오차가 허용 범위를 벗어나면 TC는 ISO 11783-12(진단 서비스를 정하는 표준 문서)에 정의된 <strong>DM1(Diagnostic Message 1)</strong> 진단 코드를 생성할 수 있다. DM1은 지금 발생한 고장을 알리는 진단 메시지다([28장](/study/isobus/28-diagnostics-dm-fmi)). DM1 메시지는 SPN(Suspect Parameter Number, 문제가 된 값의 번호)과 FMI(Failure Mode Indicator, 고장의 종류를 나타내는 번호)를 포함하여 어떤 파라미터가 어떤 방식으로 이상 상태인지 기록한다. 예를 들어 실제 살포량이 목표값 대비 20% 이상 낮으면 "유량 부족" 진단 코드가 발생할 수 있다.

작업기 ECU 내부에서는 <strong>PID(Proportional-Integral-Derivative) 제어 루프</strong>가 오차를 줄이는 방향으로 밸브를 조절한다. P 항은 현재 오차에 즉각적으로 반응하고, I 항은 지속적인 정상 오차(Steady-State Error)를 제거하며, D 항은 오차 변화율에 반응하여 과도한 진동을 억제한다. TC는 Setpoint를 명령할 뿐이며, PID 제어는 전적으로 작업기 ECU(클라이언트 측)가 수행한다.

::: tip 정리
- Setpoint는 TC가 내리는 목표값, Measurement는 작업기가 잰 실제값이다.
- 제어 오차 = Setpoint − Measurement. 오차를 줄이는 제어는 작업기 ECU가 한다.
:::

## 7. 측정값을 보내는 조건: Trigger Method

이 절은 클라이언트가 측정값을 "언제" 보내는지 정하는 방법을 본다. 측정값을 아무 때나 보내면 버스가 혼잡해진다. 그래서 TC가 조건을 정해 주고, 클라이언트는 그 조건이 될 때만 보낸다.

자동차 운행 기록계에 "1초마다 적어라", "100 m마다 적어라", "속도가 10 km/h 넘게 바뀌면 적어라"처럼 기록 조건을 정하는 것과 같다. 클라이언트가 Measurement 값을 TC에 보고하는 조건을 <strong>Trigger Method</strong>(트리거 방법)라고 한다. TC는 Measurement 명령(Command 4~8)을 보내 클라이언트에 트리거 방법과 그 파라미터(간격·임계값)를 설정한다.

| 트리거 방법 | 설명 | 예시 |
|-------------|------|------|
| **Time Interval** | 일정 시간마다 보고 | 100ms마다 현재 유량 전송 |
| **Distance Interval** | 일정 거리마다 보고 | 1m 이동할 때마다 살포량 전송 |
| **Threshold** | 값이 최소 임계값보다 클 때(`0x6`) 또는 최대 임계값보다 작을 때(`0x7`) 보고 | 유량이 5 L/min 미만으로 떨어지면 전송 |
| **On Change** | 마지막 보고 이후 변화량이 설정한 임계값 이상일 때 보고 | 섹션 상태가 ON→OFF로 바뀔 때만 전송 |
| **Total** | 누적값 요청 시 보고 | 작업 종료 후 총 살포량 요청 |

Total은 나머지 넷과 성격이 다르다. Total을 거는 measurement 명령은 따로 없다. Total은 그 값이 누적값(총계)이라는 표시이고, 총계는 값 요청이나 시간·거리 간격 measurement로 받아 간다([46장](/study/isobus/46-tc-commands-pdack), [47장](/study/isobus/47-tc-totals-logging-peer)).

TC가 트리거 방법을 설정하는 흐름은 다음과 같다.

![트리거 설정 흐름: TC가 Measurement 명령(time interval, DDI 37, Element 1, 100 ms)을 보내고 클라이언트가 PDACK로 수락한 뒤 100 ms마다 현재 유량을 보낸다. 이어 TC가 다른 값(DDI 2, Element 3)에 distance interval 1 m를 걸면 클라이언트가 수락한 뒤 1 m마다 실제 살포량을 보낸다](/images/study-isobus/45-trigger-sequence-light.png)
![트리거 설정 흐름: TC가 Measurement 명령(time interval, DDI 37, Element 1, 100 ms)을 보내고 클라이언트가 PDACK로 수락한 뒤 100 ms마다 현재 유량을 보낸다. 이어 TC가 다른 값(DDI 2, Element 3)에 distance interval 1 m를 걸면 클라이언트가 수락한 뒤 1 m마다 실제 살포량을 보낸다](/images/study-isobus/45-trigger-sequence-dark.png)

그림의 PDACK는 클라이언트가 measurement 명령을 받아들였다는 답이다. ISO 11783-10(TC를 정하는 표준 문서) 버전 4부터는 이 답과 측정 시작 시점의 값을 반드시 보내야 한다(10절). 거리 간격 값은 명령 안에서 mm 단위로 실린다(46장).

트리거 방법을 적절히 설정하면 CAN 버스 트래픽을 줄이면서도 필요한 시점에 정확한 데이터를 수집할 수 있다.

::: tip 정리
- 측정값을 보낼 조건은 TC가 measurement 명령(4~8)으로 정한다: 시간 간격, 거리 간격, 임계값, 변화량.
- 클라이언트는 조건이 될 때만 Value command(3)로 값을 보낸다.
:::

## 8. 흐름 실습: GPS 위치에 따라 살포량 바꾸기

이 절은 지금까지 본 조각(DDI, Element, Value command, 측정값)이 실제 작업에서 어떻게 이어지는지 한 장면으로 본다.

### 시나리오: GPS 기반 살포량 제어

트랙터가 밭을 주행하면서 위치에 따라 비료 살포량을 자동으로 조절하는 시나리오이다.

<strong>조건</strong>
- 처방 맵: 구역 A = 200 L/ha, 구역 B = 150 L/ha
- 살포기: 3섹션, 각 3m 폭 (총 9m)
- DDI 1: Setpoint Volume Per Area / DDI 2: Actual Volume Per Area

위치 정보는 GNSS(Global Navigation Satellite System, GPS 같은 위성 측위 시스템) 수신기가 NMEA 2000 GNSS Position Data 메시지(PGN 129029)로 보낸다. NMEA 2000은 선박용으로 시작한 CAN 기반 통신 표준이고, ISOBUS는 위치 메시지에 이 PGN을 그대로 쓴다.

![GPS 기반 살포량 제어 순서: GNSS 수신기가 위치를 보내면 TC가 처방 맵에서 구역 A 목표 200 L/ha를 찾아 Value Command로 섹션 3에 보낸다. 클라이언트가 밸브를 조절하고 실제 198 L/ha를 보고하면 TC가 오차 2 L/ha를 정상으로 판단한다. 구역 B에 들어가면 같은 과정을 150 L/ha로 반복하고 실제 151 L/ha가 보고된다](/images/study-isobus/45-rate-control-sequence-light.png)
![GPS 기반 살포량 제어 순서: GNSS 수신기가 위치를 보내면 TC가 처방 맵에서 구역 A 목표 200 L/ha를 찾아 Value Command로 섹션 3에 보낸다. 클라이언트가 밸브를 조절하고 실제 198 L/ha를 보고하면 TC가 오차 2 L/ha를 정상으로 판단한다. 구역 B에 들어가면 같은 과정을 150 L/ha로 반복하고 실제 151 L/ha가 보고된다](/images/study-isobus/45-rate-control-sequence-dark.png)

그림을 위에서부터 읽으면 다음과 같다.

1. GNSS 수신기가 현재 위치(위도 37.123, 경도 127.456)를 보낸다.
2. TC가 처방 맵에서 그 위치의 목표값(구역 A, 200 L/ha)을 찾는다.
3. TC가 Value Command로 섹션 3(Element 3)에 200 L/ha를 내린다.
4. 클라이언트가 밸브를 조절하고, 유량 센서로 잰 실제값 198 L/ha를 Process Data Value로 보고한다.
5. TC는 오차 2 L/ha가 허용 범위 안이라고 판단한다.
6. 위치가 구역 B로 바뀌면 같은 과정을 150 L/ha로 반복한다.

이 시퀀스는 TC 프로세스 데이터의 전체 흐름을 보여준다. GPS 위치 변화에 따라 처방 맵의 목표값이 바뀌고, TC는 그 값을 즉시 클라이언트에 전달한다.

::: tip 1~8절 정리
- DDI(Data Dictionary Identifier)는 TC 데이터 항목을 구분하는 16비트 표준 번호이다. DDI 1=Setpoint Volume Per Area Application Rate, DDI 2=Actual Volume Per Area Application Rate.
- Device Element는 작업기의 논리적 구성 단위로, Device/Function/Bin/Section/Unit 등의 타입으로 분류된다.
- TC → 클라이언트 방향의 Value Command로 Setpoint를 전달하고, 클라이언트 → TC 방향의 Process Data Value로 Measurement를 보고한다.
- Setpoint는 처방 맵 기반 목표값이고, Measurement는 센서 실측값이며, 그 차이가 제어 오차가 된다.
- GPS 위치(NMEA 2000 GNSS Position Data, PGN 129029) → 처방 맵 조회 → Value Command 전송 → 밸브 조절 → Measurement 보고 순으로 제어 루프가 완성된다.
:::

## 9. 클라이언트가 값을 보내도 되는 경우

지금까지 다룬 예제는 대부분 TC가 먼저 명령이나 요청을 보내고 클라이언트가 응답하는 흐름이었다. 그런데 클라이언트가 스스로 값을 밀어 넣을 수 있는 경로도 있다(7절의 Trigger Method). 이 절은 그 송신 쪽에 표준이 정해 둔 기본 제약을 정리한다. 세부 규칙은 10절에서 본다.

### 핵심 원칙: 요청받은 것만 보낸다

클라이언트는 자기가 가진 값을 임의로 골라 TC에 뿌리지 않는다. 클라이언트가 값을 보낼 수 있는 경로는 다음 세 가지뿐이다.

| 경로 | 트리거 |
|---|---|
| Request value 명령 | TC의 1회성 요청(Command 2, 4절) |
| Default data logging | `RequestDefaultProcessData`(DDI `0xDFFF`)로 활성화된, 클라이언트 스스로 정한 데이터·주기 |
| 개별 measurement 명령 | TC가 지정한 Trigger Method(Command 4~8, 7절)에 따른 주기적 보고 |

Default data logging은 TC가 특별한 DDI `0xDFFF`(=57343)로 "기록할 값과 주기는 네가 정해서 보내라"고 맡기는 방식이다([47장](/study/isobus/47-tc-totals-logging-peer)). 이 세 경로 밖에서 클라이언트가 임의로 값을 송신하는 것은 표준을 벗어난 동작이다.

### 대역폭 상한과 burst 예외

버스의 전송 용량(대역폭)은 모든 장치가 나눠 쓴다. 그래서 값 하나가 버스를 독차지하지 못하게 상한을 둔다. <strong>연결당·process data variable당 초당 최대 10개 메시지</strong>가 기본 상한이다. process data variable(프로세스 데이터 변수)은 상태를 나타내는 값 하나다. 메시지에서는 Element 번호와 DDI로 가리키므로, 1절 표의 칸 하나라고 보면 된다.

예외적으로 헤드랜드(밭 끝에서 기계를 돌리는 구간) 진입·이탈처럼 work state를 짧게 몰아 제어해야 하는 상황에서는 이 상한을 일시적으로 넘길 수 있다. 이렇게 짧게 몰아 보내는 것을 burst라고 한다. 단 이 예외는 아무 DDI에나 적용되지 않고, <strong>Setpoint/Actual Condensed Work State(2절의 DDI 290 등) 같이 ISO 11783-11 데이터 사전에 명시된 DDI</strong>에 한정된다.

<small>근거: ISO 11783-10 6.8 a)</small>

## 10. 송신 규칙 세부 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절은 9절의 원칙 밖에서 클라이언트와 TC가 지켜야 할 순서 규칙, 버전 차이, 초기화 의무를 모았다. 여기서 "버전"은 ISO 11783-10의 판(버전 3, 버전 4)을 말한다.

### measurement 명령 ACK: 응답 전에는 다음 명령 불가

TC가 보내는 measurement 명령(Command 4~8, 7절)에는 클라이언트가 반드시 <strong>PDACK</strong>(4절)로 응답해야 한다. 이 응답이 오기 전까지 TC는 같은 클라이언트로 다음 measurement 명령을 보낼 수 없다. 명령이 순차적으로만 진행된다는 뜻이다.

수락 시 클라이언트는 <strong>positive ACK(수락 응답)와 함께, 측정을 시작하는 시점의 초기값</strong>을 함께 보낸다. 이 초기값 전송은 버전 4에서 도입됐다. 버전 3까지는 거부할 때만 negative ACK(거부 응답)를 보내면 됐고, 수락 시 초기값을 함께 보내야 한다는 규정은 없었다.

### 요청-응답 동기화: 버전 3과 버전 4의 차이

버전 4부터는 TC가 보낸 요청에 클라이언트가 응답해야만 TC가 같은 클라이언트로 다음 요청을 보낼 수 있다. 버전 3까지는 이와 달리, 클라이언트의 응답을 기다리지 않고 요청을 여러 개 묶어 보내는 <strong>블록 요청</strong>이 가능했다. 즉 버전 4는 요청 흐름을 순차적(하나씩 확인하며 진행)으로 바꾼 변화다.

### DDOP 활성화 전 초기화 의무

클라이언트는 DDOP를 TC에 <strong>활성화하기 전에</strong> 내부 process data variable들을 올바른 운영값으로 초기화해 둬야 한다. DDOP가 활성화되면 TC는 곧바로 장치 지오메트리(붐 폭, 위치 오프셋 같은 치수) 등을 요청할 수 있다. 이때 클라이언트가 아직 초기화 전이라 임의값이나 미정의값을 돌려주면 TC는 그 잘못된 값을 그대로 신뢰하고 이후 제어를 시작하게 된다.

### Task totals active 비트와 measurement

TC Status 메시지(TC가 주기적으로 보내는 상태 메시지, [43장](/study/isobus/43-tc-connection))에는 <strong>"Task totals active" 비트</strong>가 있다. 태스크가 진행 중이라 총계를 세도 된다는 표시다. 이 비트가 0에서 1로, 또는 1에서 0으로 바뀌면(즉 태스크가 시작되거나 종료되는 시점마다) 그 TC Status를 송신하는 CF(Control Function, 버스에서 주소 하나를 쓰는 제어 기능)가 지정한 <strong>모든 measurement를 클라이언트가 중지</strong>해야 한다. 중지된 measurement는 TC가 개별 measurement 명령을 다시 보내거나 default data logging 트리거로 재시작한다.

비트가 0인 동안(태스크 비활성 상태)에도 TC가 시작한 measurement는 존재할 수 있다. 이 measurement는 TC가 중지 명령으로 멈출 수 있지만, <strong>비트를 0에서 1로 바꾸기 직전에 미리 중지해서는 안 된다</strong>. "Task totals active" 비트 자체는 default data logging 명령의 송수신만 제한할 뿐, 그 외의 Process Data 명령 송수신 전반을 막지는 않는다.

### TC 쪽 대응 규칙: 참고

반대로 TC는 태스크 파일에 없는 process data variable을 담은 메시지도 만들 수 있다(예: 센서 시스템 값 활용). 다만 TC는 <strong>클라이언트가 지원한다고 밝힌 variable만</strong> 그 클라이언트에 송신·요청해야 한다. 클라이언트 입장에서는 DDOP에 선언한 범위를 벗어난 요청이 오지 않는다는 전제로 동작한다.

### 재시도

PGN 응답 대기 시간, 요청이 응답 없이 실패했을 때의 재시도 간격은 이 표준이 아니라 <strong>ISO 11783-3</strong>(데이터 링크 계층을 정하는 표준 문서)을 따른다. 클라이언트가 특정 measurement를 지원하지 않아 TC가 주기적 값 요청(Command 2)으로 폴백(대체 수단으로 전환)하는 경우도 마찬가지다.

<small>근거: ISO 11783-10 6.8, 6.8 b)~d), B.8.1</small>

## 11. 전체 흐름: 두 오브젝트 풀과 처방 맵

8절은 이미 작업이 시작된 뒤의 제어 루프만 보여준다. 그런데 그 루프가 성립하려면 그 전에 준비가 끝나 있어야 한다. TC는 어떻게 DDI 1이 이 살포기의 살포량이라는 걸 알았고, 화면의 숫자는 누가 고치는가. 연결부터 실적 기록까지를 한 줄로 이으면 다음과 같다.

### 데이터가 어디에 있는가

먼저 짚을 것은, 작업기 ECU가 <strong>서로 다른 두 개의 오브젝트 풀</strong>을 플래시 메모리에 갖고 있다는 점이다. 오브젝트 풀은 화면 요소나 장치 구성 요소 같은 "오브젝트"를 한데 묶은 데이터다. 하나는 VT(Virtual Terminal, 운전석의 화면 단말)에 올리는 VT 오브젝트 풀이고, 다른 하나는 TC에 올리는 DDOP다.

| | VT 오브젝트 풀 | DDOP |
|---|---|---|
| 정의 | ISO 11783-6 | ISO 11783-10 |
| 올리는 곳 | Virtual Terminal | Task Controller |
| 담는 것 | Data Mask, Output Number, Button 등 <strong>그리는 방법</strong> | DVC, DET, DPD 등 <strong>기계의 구조와 쓸 수 있는 DDI</strong> |
| 읽는 주체 | 사람(운전자) | 소프트웨어(TC) |
| 값 식별 | Object ID | DDI |
| PGN | 0xE700 / 0xE600 | 0xCB00 |

표의 Data Mask(화면 한 장), Output Number(숫자 표시칸), Button(버튼)은 VT 화면 요소다([32장](/study/isobus/32-vt-object-pool-basics)). DVC(장치), DET(Element), DPD(Element가 다루는 DDI 하나)는 DDOP의 오브젝트다([48장](/study/isobus/48-ddop-basics)). PGN 0xE700(=59136)과 0xE600(=58880)은 VT와 작업기가 서로 주고받는 두 방향의 메시지 종류다.

여기에 세 번째 데이터가 더해진다. <strong>처방 맵</strong>이다. 처방 맵은 작업기가 아니라 FMIS(Farm Management Information System, 농장 관리 소프트웨어)가 만들어 USB로 들어오고, CAN이 아니라 파일로 전달된다. TASKDATA.XML 안에 TreatmentZone(처리 구역)과 그 구역의 목표값(ProcessDataVariable)이 들어 있고, 격자형 맵은 셀 값이 별도 바이너리 파일에 담긴다([56장](/study/isobus/56-practice-isoxml), [57장](/study/isobus/57-practice-binary-files)).

정리하면 <strong>작업기는 "나를 어떻게 그리는지"와 "나를 어떻게 조작하는지"를, FMIS는 "밭의 어디에 얼마를 뿌릴지"를 각각 들고 온다.</strong> 이 셋이 만나야 가변 살포가 성립한다.

### 직접 재생해 보기

아래 애니메이션은 전원을 켠 순간부터 실제 살포까지를 그대로 재생한다. 위쪽에서는 패킷이 버스를 타고 노드 사이를 날아다니며 각 장치가 데이터를 하나씩 채워 가고, 아래에서는 트랙터가 처방 맵 위를 지나간다. <strong>붐의 섹션 6개가 각각 다른 색으로 바뀌는 순간</strong>을 보자. 그때마다 Value command가 나간다. 화면을 누르면 멈추고 다시 누르면 이어진다.

<IsobusFlowDemo />

### 흐름에서 놓치기 쉬운 것

<strong>두 풀은 서로를 모른다.</strong> TC가 setpoint를 바꿔 보내도 VT 화면은 저절로 바뀌지 않는다. 작업기 ECU가 값을 받은 뒤 <strong>따로</strong> VT에 Change Numeric Value(VT 화면의 숫자를 바꾸는 명령, [36장](/study/isobus/36-vt-commands-basics))를 보내 화면을 고친다. 표준에는 이 둘을 잇는 자동 경로가 없고, 동기화는 작업기 펌웨어의 몫이다. 이 분리 덕분에 VT만 있는 트랙터에서도 화면은 뜨고, TC만 지원하는 작업기도 처방 맵 제어가 된다.

<strong>setpoint는 주기적으로 나가지 않는다.</strong> 표준은 관련 DeviceElement가 새 TreatmentZone(처리 구역)에 들어갔을 때 그 구역의 setpoint를 전송하도록 규정한다. 구역 경계를 넘는 순간이 트리거다.

<strong>구역 판정은 기계 단위가 아니라 device element 단위다.</strong> 12미터 붐이 경계에 걸쳐 있으면 왼쪽 섹션과 오른쪽 섹션이 서로 다른 구역에 속할 수 있고, 각각 다른 setpoint를 받는다. 이것이 정밀 살포의 핵심이며, DDOP에서 섹션을 DET로 하나하나 선언하는 이유이기도 하다.

<strong>DDOP에 없는 DDI는 쓸 수 없다.</strong> DPD의 property 비트에 settable(TC가 값을 설정할 수 있음)이 서 있는 DDI만 TC가 setpoint로 내릴 수 있고, 선언되지 않은 DDI로 명령하면 작업기는 PDACK로 거부한다. 8절의 `[DDI=1, Element=3, Value=200]`이 성립하는 근거가 바로 연결 시점에 올라간 DDOP다.

:::tip 한 줄 요약
작업기는 VT 풀(화면)과 DDOP(구조)를 각각 다른 서버에 올리고, FMIS는 처방 맵을 파일로 넣는다. TC는 DDOP로 "무엇을 보낼 수 있는지"를, 처방 맵으로 "얼마를 보낼지"를, GNSS로 "지금 어디인지"를 알아 Value command 한 줄을 만든다.
:::

<small>근거: ISO 11783-10 6.8.1</small>

::: tip 핵심 정리
- 프로세스 데이터 메시지는 명령(4비트), Element 번호(12비트), DDI(16비트), 값(32비트)을 합친 8바이트다.
- DDI는 값의 종류와 단위·분해능을, Element 번호는 작업기의 어느 부분인지를 정한다. 받은 정수에 DDI의 분해능을 곱해야 실제 값이 된다.
- TC는 Value command(3)로 목표값을 내리고, 클라이언트는 Value command(3)로 측정값을 올린다. 둘의 차이가 제어 오차다.
- 클라이언트는 요청받은 값만 보낸다: 값 요청, default data logging, measurement 트리거.
- 가변 살포는 DDOP(무엇을 보낼 수 있나), 처방 맵(얼마를), GNSS(지금 어디인가)가 만나야 성립한다.
:::

::: details 확인 문제
1. 프로세스 데이터 메시지가 담는 세 가지를 1절의 "표의 한 칸" 비유로 설명하라. 명령은 무엇에 해당하는가?
2. TC가 Element 2의 DDI 1(면적당 목표 살포량)을 150 L/ha로 설정하려 한다. Command 3으로 보낼 8바이트를 조립하라.
3. TC가 200 L/ha를 보내려고 DDI 1의 Value 자리에 정수 200을 그대로 넣었다. 클라이언트는 몇 L/ha로 읽는가?
4. 클라이언트가 TC의 요청 없이 DDI 37(실제 유량) 값을 100 ms마다 스스로 보내기 시작했다. 표준에 맞는 동작인가? 맞으려면 무엇이 먼저 있어야 하는가?
5. 목표값 200 L/ha, 측정값 198 L/ha일 때 제어 오차는 얼마이고, 그 오차를 줄이는 제어는 누가 하는가?

<strong>답 가이드</strong>

1. Element 번호가 행(어느 부분), DDI가 열(값의 종류), 값이 칸 안의 숫자다. 명령은 그 칸으로 무엇을 할지(값을 알려 달라, 이 값으로 맞춰라)를 정한다.
2. 150 L/ha = 15,000 mm³/m², 원시값 = 15,000 ÷ 0.01 = 1,500,000 = `0x16E360`이다. Byte 1 = (2 << 4) | 3 = `0x23`, Byte 2 = `0x00`, DDI 1 = `01 00`, 값 = `60 E3 16 00`(낮은 자리부터). 답은 `23 00 01 00 60 E3 16 00`이다.
3. 200 × 0.01 = 2 mm³/m² = 0.02 L/ha로 읽는다. 의도한 값의 1만분의 1이다. 원시값 2,000,000을 넣어야 한다.
4. 맞지 않는다. 클라이언트가 값을 보낼 수 있는 경로는 TC의 값 요청(Command 2), default data logging(DDI `0xDFFF`), TC가 건 measurement 명령(Command 4~8) 세 가지뿐이다. 예를 들어 TC가 DDI 37에 time interval 100 ms measurement를 걸고 클라이언트가 PDACK로 수락했다면 같은 송신이 정상이다.
5. 200 − 198 = 2 L/ha다. 오차를 줄이는 PID 같은 제어는 작업기 ECU(클라이언트)가 한다. TC는 목표값을 명령하고, 측정값을 받아 비교하고 기록한다.
:::

## 다음 챕터

- 다음: [46장 프로세스 데이터 명령: 니블, PDACK, 측정 명령](/study/isobus/46-tc-commands-pdack)
