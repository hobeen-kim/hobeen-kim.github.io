---
title: "트랙터 ECU: 클래스, 조명, 전원, Safe mode"
description: "작업기 버스에서 트랙터를 대표하는 TECU의 역할과 클래스 표기를 읽고, 조명 명령, 키 오프 뒤 전원을 유지하는 Maintain power, 통신이 끊겼을 때의 Safe mode 요구를 익힌다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, TECU, TractorECU, Lighting, MaintainPower, SafeMode]
prev: /study/isobus/21-niu-network-layer
next: /study/isobus/23-implement-messages-basics
---

# 트랙터 ECU: 클래스, 조명, 전원, Safe mode

::: info 학습 목표
- TECU가 작업기 버스에서 트랙터를 대표하는 방식(트랙터 정보를 자기 주소로 다시 보낸다)을 설명할 수 있다.
- TECU 클래스 표기(예: class 2GP)를 읽고 작업기가 트랙터에 보낼 수 있는 명령을 판단할 수 있다.
- Lighting command 프레임을 읽고 어떤 램프가 켜지고 꺼졌는지 풀 수 있다.
- 키를 끈 뒤 전원이 꺼지는 순서와, Maintain power 메시지를 언제 어떤 바이트로 보내는지 설명할 수 있다.
- 전원이나 통신이 끊겼을 때 작업기가 지켜야 할 Safe mode 요구를 말할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [20장 ISOBUS 네트워크 구성](/study/isobus/20-isobus-network-topology), [21장 네트워크 계층과 NIU](/study/isobus/21-niu-network-layer)
- 이 장에서 처음 나오는 말
  - TECU(Tractor ECU): 트랙터 버스와 작업기 버스(implement bus, [20장](/study/isobus/20-isobus-network-topology)에서 본 작업기 쪽 CAN 버스)를 잇고, 작업기 버스에서 트랙터를 대표하는 ECU.
  - 클래스(class): TECU가 작업기 버스에 어떤 메시지를 어디까지 내주는지 나타낸 등급. 숫자 1~3과 문자 N·F·G·P·M으로 적는다.
  - facility response: 트랙터가 실제로 갖춘 기능을 비트로 알리는 메시지.
  - ECU_PWR와 PWR: 트랙터가 작업기에 주는 두 전원. ECU_PWR은 ECU·센서 같은 전자 회로용, PWR은 밸브·모터 같은 액추에이터용이다.
  - 키 오프(key off): 운전자가 시동 키를 끄는 것. 그 뒤에도 전원이 잠깐 유지된다.
  - Safe mode: 전원이나 통신이 끊겼을 때 작업기가 위험하지 않은 상태로 들어가는 것.
:::

TECU는 트랙터의 대변인이다. 엔진, 변속기, 히치 컨트롤러가 작업기에게 저마다 말하는 대신, 대변인 하나가 정해진 양식으로 트랙터 소식을 알리고 작업기의 부탁을 트랙터 안으로 전한다. 대변인이 어디까지 알려 주고 어떤 부탁까지 들어주는지는 클래스라는 등급으로 표시한다. 이 장은 TECU의 역할과 클래스를 먼저 보고, TECU가 맡는 조명, 작업기 전원, 고장 때의 안전 규칙을 차례로 본다.

## 1. TECU의 역할: 작업기 버스에서 트랙터를 대표한다

[21장](/study/isobus/21-niu-network-layer)에서 TECU를 트랙터 버스와 작업기 버스를 잇는 특수 NIU(Network Interconnection Unit, 세그먼트를 잇는 장치)로 봤다. 이 절은 TECU가 두 버스 사이에서 메시지를 어떻게 옮기는지, 포트는 어떻게 정해져 있는지 본다.

ISO 11783-9(TECU를 정하는 표준 문서, 2012년 2판)는 TECU를 트랙터 버스와 작업기 버스 사이의 게이트웨이이면서 다른 기능도 하는 CF로 정의하고, 작업기 버스에서 VT 같은 기능에 대해 <strong>트랙터를 대표하는 CF</strong>라고 덧붙인다. CF(Control Function)는 ECU 안에서 주소 하나를 갖고 통신하는 기능 단위이고, VT(Virtual Terminal)는 운전석의 작업기 화면 장치다. 2판에서 새로 생긴 요구는 version 2 TECU와 Working Set(작업기 하나를 이루는 CF 묶음, [26장](/study/isobus/26-isobus-network-mgmt))의 요구로 표시된다. 이 장의 표에서 "v2"가 그 표시다.

### 포트

TECU는 작업기 버스용 포트를 적어도 하나 가져야 하고, 트랙터에 작업기 버스와 트랙터 버스가 둘 다 있으면 포트 두 개를 가져야 한다. 네트워크 메시지(NIU에게 말을 거는 메시지, [21장](/study/isobus/21-niu-network-layer))에서 포트를 가리킬 때는 port 1이 작업기 버스, port 2가 트랙터 버스다. 작업기 버스 포트는 ISO 11783-2(물리 계층을 정하는 표준 문서)의 물리 계층에 붙을 수 있게 설계해야 하고, 트랙터 버스 포트는 다른 물리 계층이어도 되지만 ISO 11783 물리 계층이 권장된다.

트랙터 버스는 트랙터 제조사가 관리하는 세그먼트다. 제조사의 동의 없이 CF를 붙이지 않는 것이 의도이고, ISO 11783-8(파워트레인 메시지 규칙)·ISO 11783-7(트랙터·작업기 메시지) 메시지와 제조사 독점 메시지를 쓸 수 있다. 두 네트워크 사이에는 전기적 격리와 메시지 격리를 위해 NIU가 있어야 한다.

### 메시지 방향별 규칙

TECU는 작업기 버스에서 여느 CF와 똑같이 보여야 한다. 특히 트랙터가 VT에 접근하는 방식은 다른 작업기와 같아야 한다. TECU는 연결된 네트워크 종류에 따라 gateway 또는 router처럼 동작한다. 메시지가 오가는 방향별로 TECU가 하는 일은 다음과 같다. SA(Source Address)는 보낸 쪽 주소다.

| 방향 | TECU가 하는 일 |
|---|---|
| 트랙터 버스 → 작업기 버스 | 자기 클래스에 해당하는 정보를 트랙터 버스나 직결 센서(ISO 11786 센서 등)에서 모두 모아, 클래스에 정해진 메시지에 담아 <strong>자기 SA</strong>로 다시 보낸다(shall) |
| 작업기 버스 → 트랙터 버스 | 클래스에 맞는 트랙터 제어 메시지(process data 포함)를 받아 트랙터 설계에 맞게 해석한 뒤, 트랙터 버스에 자기 SA로 global이나 특정 목적지로 보낸다(shall) |
| TECU 자신 → 작업기 버스 | 트랙터를 대표해 destination-specific 메시지를 직접 만든다. 예: VT에 트랙터 성능 화면 올리기 |

ISO 11786은 트랙터의 속도·PTO 회전수·히치 위치 같은 기본 측정 신호를 전선으로 내주는 트랙터 장착 센서 인터페이스 규격이다. process data는 TC(Task Controller, 작업 기록과 제어를 맡는 장치)가 다루는 작업 데이터다([45장](/study/isobus/45-tc-process-data-basics)). shall은 표준이 반드시 지키라고 한 요구, should는 권하는 요구다.

대역폭 규칙 두 개가 붙는다.

- 요청받은 정보를 작업기 버스에 올릴 때는 global destination을 쓰는 것이 좋다. 같은 정보를 여러 CF가 요청해도 한 번에 끝나고, TECU의 filter database 부담도 준다(should).
- TECU가 이미 표준 PG로 보내는 데이터를 Process Data 메시지로 중복해 보내지 않는다. ISO 11783-10(TC를 정하는 표준 문서)이 TC가 PG를 직접 받는 방법을 허용하기 때문이다. PG(Parameter Group)는 PGN 하나로 구별되는 메시지 하나다.

구현 관점에서 보면 작업기 버스에는 트랙터 버스 CF의 SA가 나타나지 않는다. 트랙터 속도든 히치 위치든 모두 TECU의 SA에서 온다. SIL(Software-in-the-Loop, 실제 장비 대신 소프트웨어로 상대를 흉내 내는 시험 환경)에서 트랙터를 흉내 낼 때도 트랙터 정보는 TECU 하나의 SA로 보내야 실제 배치와 같아진다(해석).

### 트랙터도 서비스를 쓴다: tractor set

트랙터도 작업기 CF와 똑같이 작업기 버스의 서비스(VT, TC, management computer gateway)를 쓸 수 있어야 한다. 서비스 쪽이 작업기 버스용과 트랙터 버스용 네트워크 드라이버를 따로 두지 않도록, TECU가 트랙터 버스의 CF들을 "tractor set"의 멤버로 묶는다. 묶는 방식은 작업기 CF나 Working Set Master가 CF를 묶는 방식과 비슷한 구조여야 한다(shall). Working Set을 알리는 메시지는 [26장 ISOBUS 네트워크 관리](/study/isobus/26-isobus-network-mgmt)에서 다룬다. ISO 11783-9는 tractor set을 메시지 수준에서 어떻게 알리는지까지는 적지 않는다.

<small>근거: ISO 11783-9 1, 4.1.1~4.1.3, 4.2.1~4.2.4, 4.3, ISO 11783-1 6.6.2, 6.7.2</small>

## 2. TECU 클래스 표기 읽기

작업기가 트랙터에게 무엇을 기대할 수 있는지는 TECU 클래스로 안다. 이 절은 "class 2GP" 같은 표기를 읽는 법을 본다.

클래스 표기는 숫자 하나와 문자 몇 개로 이루어진다. 숫자는 기본 클래스, 문자는 덧붙는 기능 묶음이다. "class 2GP"는 "기본 클래스 2에 G 묶음과 P 묶음을 더한 트랙터"라고 읽는다.

![TECU 클래스 표기 읽기: class 2GP의 숫자 2는 아래에서 위로 쌓이는 기본 클래스 1, 2, 3 가운데 Class 2를, 문자 G와 P는 덧붙는 기능 묶음 N, F, G, P, M 가운데 조향과 속도·주행 전략 묶음을 가리킨다](/images/study-isobus/22-tecu-class-notation-light.png)
![TECU 클래스 표기 읽기: class 2GP의 숫자 2는 아래에서 위로 쌓이는 기본 클래스 1, 2, 3 가운데 Class 2를, 문자 G와 P는 덧붙는 기능 묶음 N, F, G, P, M 가운데 조향과 속도·주행 전략 묶음을 가리킨다](/images/study-isobus/22-tecu-class-notation-dark.png)

숫자는 계단처럼 쌓인다. 클래스는 누적이라 class 3이면 class 1·2 메시지까지 다 낸다. 히치(hitch)는 작업기를 들어 올리고 내리는 연결 장치, PTO(Power Take-Off)는 엔진 힘을 작업기로 넘겨 주는 회전축, 리어(rear)는 트랙터 뒤쪽이다.

- Class 1: 속도, 엔진 회전수, 리어 히치 위치, 리어 PTO 회전수 같은 기본 측정값을 낸다.
- Class 2: Class 1에 시간·날짜, 주행 거리·방향, 견인력(히치에 걸리는 당기는 힘), 보조 밸브 유량, 조명 메시지를 더해 측정 기능을 모두 낸다.
- Class 3: Class 2에 더해 작업기가 보내는 리어 히치·PTO·보조 밸브 명령을 받아들인다. 보조 밸브(auxiliary valve)는 작업기의 유압 장치를 움직이는 트랙터 쪽 밸브다.

문자는 숫자와 따로 붙는 기능 묶음이고, 여러 개가 함께 붙을 수 있다. G, P, M은 version 2부터 생겼다.

- N: GPS 같은 항법 위치 메시지를 낸다.
- F: 전방(또는 보조) 히치·PTO 정보를 낸다.
- G: 조향 상태를 내고 조향 명령을 받는다.
- P: 속도·주행 전략 명령을 받는다.
- M: 발진(전진·후진 출발) 명령을 받는다.

예를 들어 class 3GP 트랙터는 리어 히치·PTO·보조 밸브 명령을 받고(3), 조향 명령(G)과 속도 명령(P)도 받는다. class 1N 트랙터는 기본 측정값과 항법 메시지를 내지만 히치·PTO·보조 밸브 명령은 받지 않는다.

트랙터는 자기 클래스를 facility response 메시지로 알린다. 이 메시지의 클래스 칸은 2비트이고 `00`이 class 1, `01`이 class 2, `10`이 class 3이다. `00`이 "클래스 없음"이 아니라는 점에 주의한다. 문자 묶음의 세부와 클래스를 매기는 규칙은 3절에서 본다.

<small>근거: ISO 11783-9 4.4.2.1~4.4.2.9, ISO 11783-7 A.27.4</small>

## 3. 클래스별 메시지와 클래스 규칙 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

2절의 클래스 설명과 [20장](/study/isobus/20-isobus-network-topology)의 TECU 클래스 표를 기능 묶음 단위로 다시 펼치고, 클래스를 매기는 규칙과 TECU가 여럿일 때의 규칙을 본다.

### 클래스와 최소 지원 메시지 세트

아래 표의 O는 요구, O(v2)는 version 2부터 요구라는 뜻이다. 파라미터 이름 단위 목록은 [부록 Part 9](/study/isobus/appendix-iso-part09)에 있다.

| 기능 묶음 | Class 1 | Class 2 | Class 3 |
|---|---|---|---|
| 전원 관리: key switch state, maximum time of tractor power, maintain power 요청 처리 | O(v2) | O | O |
| 속도: wheel-based·ground-based machine speed, engine speed(100 ms, Part 8) | O | O | O |
| 리어 히치 위치·in-work, 리어 PTO 회전수·engagement | O | O | O |
| VT 초기화용 기본 언어 저장 | O(v2) | O | O |
| tractor facilities response | O(v2) | O | O |
| time/date, 주행 거리·방향(ground·wheel), rear draft, aux valve 추정·측정 유량 | | O | O |
| ISO 16154가 지역별로 요구하는 조명 메시지 세트 | | O(v2) | O |
| 명령: 리어 히치 위치, 리어 PTO 회전수 set point·engagement, aux valve | | | O |
| 명령 피드백: limit status·exit/reason code, PTO engagement request status | | | O(v2) |

표에 나오는 말을 풀어 둔다.

- wheel-based speed는 바퀴 회전으로 잰 속도, ground-based speed는 레이더처럼 땅을 기준으로 잰 속도다([23장](/study/isobus/23-implement-messages-basics)). engine speed의 100 ms는 송신 주기이고, "Part 8"은 파워트레인 메시지 규칙을 정하는 ISO 11783-8을 뜻한다(7절).
- in-work는 작업기가 작업 중인지, engagement는 PTO가 물려 돌고 있는지를 나타낸다. rear draft는 리어 히치에 걸리는 견인력이다.
- ISO 16154는 공로 주행용 조명·신호 장치 설치를 정하는 규격이다.
- set point는 목표값, limit status와 exit/reason code는 명령이 어떻게 처리됐는지 알려 주는 상태 값이다([24장](/study/isobus/24-hitch-pto-valve-control)).

Class 1은 기존 센서를 간단한 네트워크 ECU에 붙여 빨리 ISO 적합성을 얻게 하려는 등급이고, 신규 트랙터 설계에는 쓰지 않는 것이 좋다. Class 3 트랙터도 작업기의 명령을 negative-acknowledge(거절 응답)로 거부할 수 있다.

### 클래스를 매기는 규칙

- 번호 클래스를 쓰려면 위 표에 나열된 그 인터페이스의 메시지를 모두 acknowledge할 수 있어야 한다. 클래스는 누적이라 class 3이면 class 1·2 메시지까지다.
- 리어 히치나 PTO가 물리적으로 없으면 클래스는 유지하고, 그 기능의 파라미터를 "not available"로 응답한다.
- 기능은 달려 있는데 메시지를 만들 데이터·제어 수단이 없으면, 달린 기능이 아니라 <strong>실제로 내보내는 메시지</strong> 기준으로 클래스를 매긴다.
- 다음 클래스 전체를 채우지 않고 메시지를 더 제공하는 것은 괜찮다.

version 2부터는 다음이 붙는다.

- 모든 클래스가 ISOBUS compliance certification message(인증 시험을 통과한 기능을 알리는 메시지), 특히 TECU class 파라미터를 지원한다([27장](/study/isobus/27-diagnostics-identification) 참고).
- 전원 인가 시와 요청 시에 tractor facility response를 보낸다. 내용은 작업기가 요구한 기능이 아니라 <strong>실제 설치된 기능</strong>이다.
- 작업기는 required tractor facilities 메시지로 필요한 기능의 송신을 켤 수 있다. 비트를 0으로 둔 기능은 TECU가 송신을 멈춰 대역폭을 아낄 수 있다. 여러 작업기에게서 받으면 모든 요구를 합친 응답 하나만 보낸다.
- facility response의 클래스 필드는 `00` = class 1, `01` = class 2, `10` = class 3, `11` = not available이다. `00`이 "클래스 없음"이 아니라 class 1이라는 점이 함정이다. 메시지 전체 구조는 [24장](/study/isobus/24-hitch-pto-valve-control)에서 다룬다.
- ISO 11783-7 3판(2015)의 설명에 따르면 최소 조명 세트는 Class 1 요구가 아니라 Class 2 요구다. 위 표의 ISO 11783-9 배치와 맞는다.

### 클래스 표기의 문자 자세히: N, F, G, P, M

| 문자 | 뜻 | 기본 클래스와의 관계 | 예 |
|---|---|---|---|
| N | GPS·DGPS 항법 메시지 제공(Part 7의 navigation location system messages) | 번호 뒤에 붙인다 | 3N |
| F | 전방(또는 보조) 히치·PTO 정보 제공 | 기본 클래스에 따라 범위가 늘어난다. 전방 <strong>명령</strong>은 class 3만 | 2F |
| G (v2) | 조향 상태·제어 파라미터 전부 제공 | 기본 클래스와 <strong>무관</strong> | 2G |
| P (v2) | 속도·주행 전략 명령 수용, 속도 상태·제어 파라미터 전부 제공 | 기본 클래스와 <strong>무관</strong> | 2P |
| M (v2) | 발진(전진·후진) 명령 수용. 메시지 세트는 "Part 7에서 정의될 예정"으로 적혀 있다 | 표준에 명시 없음 | 3M |

DGPS는 보정 신호로 정확도를 높인 GPS다. 표의 "Part 7"은 ISO 11783-7을 가리킨다.

문자는 여러 개 붙을 수 있다. class 3GP는 조향과 속도 제어를 모두 받는 class 3 트랙터다. 작업기 쪽 판단은 이렇게 갈린다. 조향 곡률 명령은 G가, 속도 set point는 P가 있으면 class 2에서도 보낼 수 있다. 리어 히치·PTO·aux valve 명령은 class 3이어야 한다.

P에서 주행 전략 제어와 정지(속도 0.0) 능력은 선택이고, 작업기는 tractor facilities response로 지원 여부를 확인한다. 제어에 쓰는 machine selected speed는 트랙터가 실제로 차속 제어에 쓰는 속도 소스여야 하며, 보통 wheel-based speed다. 제어 중 속도 소스가 바뀔 때 매끄럽게 넘기는 책임은 트랙터에 있다. 트랙터는 속도·토크·유량·압력·힘 같은 변수에 추가 제어 모드를 둘 수 있고, 각 모드의 제약을 스스로 판단해 적절할 때만 명령을 acknowledge한다. 조향·속도·히치·PTO 메시지의 바이트 배치는 [24장](/study/isobus/24-hitch-pto-valve-control)에서 다룬다.

### TECU가 여럿일 때: function instance

TECU 기능은 VT를 겸하는 디스플레이에 들어갈 수도 있다. 그래서 작업기 버스에 TECU가 여럿일 수 있고, 규칙은 NAME(장치마다 고유한 64비트 이름)의 function instance(같은 기능을 하는 장치가 여럿일 때 붙이는 번호, [12장](/study/isobus/12-j1939-address-name))로 정한다.

1. function instance 0이 primary, 1이 secondary다.
2. 전원 관리, 조명 제어, language command 응답은 instance 0이 맡는다.
3. 높은 instance의 TECU는 낮은 instance가 이미 보내는 메시지를 보내면 안 된다.
4. instance가 0이 아닌 TECU는 낮은 instance들에게 facility response를 요청하고, 그들에게 <strong>없는</strong> 기능 비트만 설정한다.

예를 들어 instance 0 TECU에 ground-based speed·distance가 없으면, GPS 수신기에 붙은 디스플레이 내장 TECU가 그 메시지를 보낼 수 있다. 작업기 CF는 facility response 여러 개를 받아 처리할 수 있어야 한다.

<small>근거: ISO 11783-9 4.4.2.1~4.4.2.9, 4.4.3, ISO 11783-7 A.27.4, B.24.3</small>

## 4. 조명 제어

version 2 TECU는 작업기 조명까지 맡는다. 이 절은 TECU의 조명 책임과, 램프를 켜고 끄는 Lighting command, 램프 상태를 돌려받는 Lighting data를 본다.

### TECU의 책임과 통신 장애 때의 대비책

version 2부터 instance 0 TECU(TECU가 여럿일 때 대표가 되는 TECU, 3절)가 작업기 조명 제어를 책임진다. 수단은 ISO 11783-7의 Lighting command·Lighting data 메시지와 ECU_PWR·PWR 제어다. TECU는 운전자 조작과 차량 시스템 내부에서 나온 조명 명령, 키 스위치 상태를 감시하고, 트랙터가 운용될 지역의 램프별 규칙을 적용한다. 조명 명령은 트랙터 버스의 조명 메시지나 TECU에 들어오는 운전자 입력으로 감시한다. 그다음 작업기 버스에 필요한 전원이 켜져 있게 하고 알맞은 조명 메시지를 보낸다. 표준의 ECU_PWR·PWR 제어 블록도에도 key·light·work light·hazard·marker 스위치가 TECU와 함께 나온다.

작업기 버스나 트랙터의 고장으로 작업기 버스 통신을 믿을 수 없게 되면, TECU는 <strong>ECU_PWR을 끊고 PWR을 경고등 점멸 주기로 켰다 껐다</strong> 해야 한다(shall). 조명이 동기화된 연결 장비는 이 방식으로 비상등을 제어한다. CAN이 죽어도 전원선 자체의 점멸로 작업기 황색 경고등을 깜빡이게 하는 하드웨어 폴백(fallback, 주된 방법이 안 될 때 쓰는 대비책)이다.

표준의 예시 그림에 나오는 구성 요소는 CAN 버스, twisted quad cable(네 가닥을 꼰 케이블), 과부하 보호, double pole NC 릴레이(전원이 없으면 닫혀 있는 2극 릴레이), implement lighting ECU, 좌·우 황색 경고등이다. 그림의 배선을 글로 확인하지는 못했지만, ECU_PWR이 끊기면 NC 릴레이가 경고등을 PWR에 바로 잇는 구성으로 읽힌다(추론). 점멸 주기 값은 ISO 11783-9에 수치로 없다.

### Lighting command: 램프를 켜고 끄는 명령

Lighting command는 8바이트에 램프 31개의 명령과 요청 비트 하나를 2비트씩 담는다. 2비트로 네 가지 값을 나타낸다. `00`은 끄기(Deactivate), `01`은 켜기(Activate), `10`은 예약(Reserved, 아직 쓰임이 없는 값), `11`은 Don't care(이 램프에는 아무것도 시키지 않고 지금 상태 그대로 둔다)다. 아래 그림은 바이트마다 어느 칸에 어떤 램프가 있는지 보여 준다.

![Lighting command 8바이트 배치: 바이트마다 2비트 필드 4개, 31개 램프 명령과 Byte 8 bits 2·1의 Lighting data 요청 비트](/images/study-isobus/13-light-command-layout-light.png)
![Lighting command 8바이트 배치: 바이트마다 2비트 필드 4개, 31개 램프 명령과 Byte 8 bits 2·1의 Lighting data 요청 비트](/images/study-isobus/13-light-command-layout-dark.png)

| 항목 | 값 |
|---|---|
| PGN | 65089(0xFE41), PF 254·PS 65 → PDU2 broadcast |
| 기본 우선순위 | 3 |
| 송신 | 트랙터 → 트랙터·작업기의 모든 조명 컨트롤러 |
| 주기 | 램프 ON/OFF가 바뀔 때마다. 메시지 간격 최대 1 s, 모든 램프를 합쳐 초당 10개 이하 |
| 필드 값 | 2비트: `00` Deactivate, `01` Activate, `10` Reserved, `11` Don't care |

PDU2 broadcast는 받는 쪽을 지정하지 않고 모두에게 보내는 메시지다([9장](/study/isobus/09-j1939-message)).

점멸은 ON과 OFF를 번갈아 담은 메시지를 보내서 표현하고, 방향 지시등·비상등 점멸을 동기화하려고 주기적으로도 보낸다. 몇몇 필드는 정의에 주의가 필요하다. 방향 지시등은 트랙터와 연결된 모든 작업기의 램프에 대한 명령이다. rotating beacon(회전 경광등)은 저속 차량 표시등이고, 활성화되면 컨트롤러가 그 기능에 맞게 조명을 다뤄야 한다. alternate headlights는 로더·제설기처럼 주 전조등이 가려지는 경우용이다. Byte 8 bits 2·1은 램프가 아니라 모든 조명 컨트롤러에 Lighting data를 요청하는 비트다.

야간 도로 주행 중 왼쪽 방향 지시등이 깜빡이는 순간을 프레임으로 보면 다음과 같다(TECU SA는 예시 값 `0xF0`).

```text
ID 0x0CFE41F0   13 44 00 55 00 00 0F 01   점멸 ON 단계 + Lighting data 요청
ID 0x0CFE41F0   13 04 00 55 00 00 0F 00   점멸 OFF 단계, 요청 비트 내림
```

CAN ID `0x0CFE41F0`은 `0C`(우선순위 3이 들어 있는 앞부분), `FE41`(PGN 65089, Lighting command), `F0`(SA 240, TECU)로 나뉜다.

데이터 표 읽는 법: 한 바이트를 2비트씩 네 칸으로 나눈다. 비트 번호는 8(가장 높은 자리)부터 1까지 센다. 표의 "8·7 / 6·5 / 4·3 / 2·1"은 바이트 안에서 높은 자리 칸부터 낮은 자리 칸 순서이고, 위 그림의 왼쪽 칸부터 오른쪽 칸 순서와 같다. 예를 들어 `13`은 2진수 `0001 0011`이므로 네 칸이 차례로 `00`, `01`, `00`, `11`이다.

| 바이트 | 값 | 비트 쌍(8·7 / 6·5 / 4·3 / 2·1) | 뜻 |
|---|---|---|---|
| Byte 1 | `13` | 00 / 01 / 00 / 11 | 상향등 끔, 하향등 켬, alternate 끔, 주간 주행등 don't care |
| Byte 2 | `44` → `04` | 01→00 / 00 / 01 / 00 | 좌측 지시등 켬→끔(점멸), 우측 끔, beacon 켬, 트랙터 전방 안개등 끔 |
| Byte 4 | `55` | 01 / 01 / 01 / 01 | 트랙터·작업기 marker와 clearance 모두 켬 |
| Byte 7 | `0F` | 00 / 00 / 11 / 11 | 작업기 전방 작업등 끔, OEM option 1·2 don't care |
| Byte 8 | `01` → `00` | 00 / 00 / 00 / 01→00 | 작업기 작업등 끔, Lighting data 요청 → 내림 |

Byte 3·5·6은 `00`이라 정지등·후진등과 트랙터 작업등이 모두 꺼진 상태다. marker와 clearance는 차의 폭과 끝을 알리는 표시등이다.

Byte 2를 단계별로 읽어 보자.

1. `44`를 2진수로 바꾸면 `0100 0100`이다.
2. 2비트씩 자르면 `01 / 00 / 01 / 00`이다.
3. 그림의 Byte 2 칸 순서(좌측 지시등, 우측 지시등, rotating beacon, 트랙터 전방 안개등)에 맞추면 좌측 지시등 켬, 우측 끔, beacon 켬, 안개등 끔이다.
4. 다음 메시지의 `04`는 `0000 0100`이다. 첫 칸만 `00`으로 바뀌었다. 좌측 지시등 칸만 켬과 끔을 오가므로 점멸이다.

아래 코드는 32칸 이름 표(`FIELDS`)로 8바이트를 2비트씩 풀어 사전으로 만든다. 위 두 프레임을 넣어 하향등, 주간 주행등, 좌측 지시등의 점멸, beacon, 요청 비트를 확인한다.

::: details Lighting command 디코더 검산 (Python)
```python
FIELDS = [
    ["High-beam headlights", "Low-beam headlights", "Alternate headlights", "Daytime running lights"],
    ["Left-turn signal lights", "Right-turn signal lights", "Rotating beacon lights", "Tractor front fog lights"],
    ["Left stop lights", "Right stop lights", "Centre stop lights", "Back-up lights and alarm horn"],
    ["Tractor marker lights", "Implement marker lights", "Tractor clearance lights", "Implement clearance lights"],
    ["Tractor rear high-mounted work lights", "Tractor rear low-mounted work lights",
     "Tractor underside-mounted work lights", "Rear fog lights"],
    ["Tractor front high-mounted work lights", "Tractor front low-mounted work lights",
     "Tractor side high-mounted work lights", "Tractor side low-mounted work lights"],
    ["Implement left forward work lights", "Implement right forward work lights",
     "Implement OEM option 1 light", "Implement OEM option 2 light"],
    ["Implement rear work lights", "Implement left-facing work lights",
     "Implement right-facing work lights", "Lighting data message request"],
]

def decode_lighting(data):
    return {name: (data[byte] >> (6 - 2 * pair)) & 0b11
            for byte, names in enumerate(FIELDS) for pair, name in enumerate(names)}

on = decode_lighting(bytes.fromhex("1344005500000F01"))
off = decode_lighting(bytes.fromhex("1304005500000F00"))
assert on["Low-beam headlights"] == 1 and on["Daytime running lights"] == 3
assert (on["Left-turn signal lights"], off["Left-turn signal lights"]) == (1, 0)
assert on["Rotating beacon lights"] == off["Rotating beacon lights"] == 1
assert (on["Lighting data message request"], off["Lighting data message request"]) == (1, 0)
assert sum(len(names) for names in FIELDS) == 32
```
:::

`(data[byte] >> (6 - 2 * pair)) & 0b11`이 한 바이트에서 pair번째 2비트 칸을 꺼내는 줄이다. pair가 0이면 bits 8·7, 3이면 bits 2·1이다. 마지막 줄은 칸이 모두 32개(램프 31개와 요청 비트 1개)임을 확인한다.

### Lighting data: 램프 상태 보고

Lighting command의 요청 비트에 대한 응답이다. 트랙터와 작업기의 각 조명 컨트롤러는 요청받으면 이 메시지를 TECU에 보내야 하고, 트랙터는 이를 보고 어떤 조명 시스템이 동작하는지 판단한다. 램프 감지 기능이 있는 컨트롤러는 끊어진 전구도 보고해야 한다(shall). 표준은 많은 지역에서 이것이 법적 요구라고 덧붙인다.

| 항목 | 값 |
|---|---|
| PGN | 65088(0xFE40), PF 254·PS 64 |
| 기본 우선순위 | 6 |
| 주기 | 요청받을 때 |
| 배치 | Lighting command와 같다. 단 Byte 8 bits 2·1은 예약 |
| 필드 값 | 2비트 측정값: `00` Deactivated, `01` Activated, `10` Fault detected, `11` Not available |

컨트롤러마다 자기 SA로 따로 응답하므로 TECU는 SA별로 모아 판단하게 되고, 컨트롤러에 없는 램프는 ISO 11783-7의 2비트 상태값 규칙대로 `11`(not available 또는 not installed)이 된다(해석). 2비트 상태값 규칙은 [23장](/study/isobus/23-implement-messages-basics)에서 다룬다. 명령의 `10`은 Reserved지만 측정값의 `10`은 Fault detected(고장 감지)라는 점도 주의한다.

### Background lighting level command: 배경 조명 밝기

계기판·스위치 같은 배경 조명의 밝기를 정하는 메시지다. 밝기가 바뀔 때마다, 그리고 최대 5 s 간격으로 보낸다.

| 항목 | 값 |
|---|---|
| PGN | 53248(0xD000), PF 208 → PDU1, PS = DA(특정 목적지 또는 global) |
| 기본 우선순위 | 3 |
| Byte 1 | Background illumination level: 0.4 %/bit, offset 0, 0~100 % |
| Byte 2~8 | 예약 |

분해능 0.4 %/bit는 값 1이 0.4 %라는 뜻이고, offset 0은 값 0이 0 %라는 뜻이다. 밝기 50 %는 50 / 0.4 = 125 = `0x7D`, 100 %는 250 = `0xFA`다. 1바이트 유효 범위 0~250과 정확히 맞는다([23장](/study/isobus/23-implement-messages-basics)의 무효값 규칙). global로 보내면 `ID 0x0CD0FFF0`, 데이터 `7D FF FF FF FF FF FF FF` 꼴이다. 표준이 이 메시지의 송신자를 명시하지 않으므로 SA `0xF0`(TECU)은 가정이다. PDU1은 PS 자리에 받는 쪽 주소(DA)를 넣는 메시지이고, `FF`(=255)를 넣으면 global(모두에게)이다.

### 2018년 개정: 정식 인증 조명은 7핀 커넥터로

ISO 11783-7의 2018년 개정(Amd.1, 표준을 고친 추가 문서)은 Lighting command 설명의 셋째 문단을 바꿔, Lighting command가 조명 상태를 "제어(control)"한다는 표현을 "전달(communicate)"한다로 고쳤다. 그리고 넷째 문단을 새로 넣었다. 작업기의 <strong>정식 인증(homologated) 조명은 7핀 조명 커넥터로 제어해야 하고(shall), 작업기 버스의 Lighting command에 의존하면 안 된다.</strong> Lighting command는 인증 대상이 아닌 조명의 제어와 진단에 쓸 수 있다. 정식 인증 조명은 도로 주행 법규 인증을 받은 조명이고, 7핀 조명 커넥터는 트랙터와 트레일러 조명을 잇는 전용 커넥터다.

ISO 11783-9(2012)는 이 개정보다 먼저 나왔으므로, TECU의 조명 책임을 읽을 때는 이 개정과 함께 봐야 한다. 공로 주행에 필요한 방향 지시등·정지등·차폭등은 7핀 배선이 1차 경로이고, ISOBUS 조명 메시지는 작업등·OEM 옵션 램프와 Lighting data를 통한 고장 진단에 쓰는 것으로 정리된다(해석).

<small>근거: ISO 11783-9 4.5, Figure 1, Figure 2, ISO 11783-7 B.18~B.20, A.22, 3.3.3, Table 1, ISO 11783-7 Amd.1:2018 B.18</small>

## 5. 작업기 전원과 키 오프

트랙터는 작업기에 ECU_PWR(전자 회로용)과 PWR(액추에이터용) 두 전원을 준다([20장](/study/isobus/20-isobus-network-topology)). 키를 끄면 전원이 바로 끊기지 않고 잠깐 유지되는데, 그동안 작업기가 밸브를 안전하게 닫고 설정을 저장한다. 이 절은 TECU의 전원 책임과, 키를 끈 뒤 전원이 꺼지는 순서를 본다. 컴퓨터를 끌 때 열린 파일을 저장할 시간을 준 뒤 꺼지는 것과 비슷하다.

### TECU의 전원 책임과 전류 용량

20장에서 본 두 전원의 책임 규정을 자세히 보면 다음과 같다.

- version 2부터 instance 0 TECU가 브레이크어웨이 커넥터(IBBC, 트랙터와 작업기를 잇는 9핀 커넥터)로 작업기에 가는 ECU_PWR 분배를 제어하고, 상태 메시지를 보내고, 제어 메시지를 받아 처리한다. ECU_PWR이 트랙터의 다른 곳에서 나와도 마찬가지다. PWR도 출처와 상관없이 같은 책임을 진다.
- TECU는 <strong>ECU_PWR을 켠 뒤에 address claim을 보낸다</strong>(shall). 작업기 ECU가 ECU_PWR로 깨어나 있어야 TECU의 claim을 듣고 자기 claim과 비교할 수 있기 때문으로 보인다(추론). address claim은 이 주소를 쓰겠다고 알리는 절차다([13장](/study/isobus/13-j1939-address-claim)).
- VT처럼 트랙터에 붙어 작업기 버스에 상시 연결된 ECU는 ECU_PWR에 연결하는 것이 좋다. bus extension connector로 붙은 트랙터 측 ECU를 ECU_PWR로 급전할지는 트랙터 제조사나 설치자가 정한다.
- TBC_PWR은 ECU_PWR이나 TECU 자체에서 받아야 하고, version 2부터는 TBC_PWR이 TBC_RTN이나 ECU_GND에 단락되는 경우를 막는 과부하 보호를 TBC_PWR과 ECU_PWR 연결부에 넣어야 한다. TBC는 버스 끝의 종단 바이어스 회로이고, TBC_PWR은 그 전원, TBC_RTN은 그 귀선, ECU_GND는 ECU 전원의 접지다.

| 전원 | 최소 전류 용량 |
|---|---|
| 12 V ECU_PWR | 15 A |
| 12 V PWR | 50 A (version 2에서 바뀐 요구) |
| ECU_PWR + PWR 합계 | 연속 55 A (version 2에서 바뀐 요구) |

### 키 스위치 상태와 남은 전원 시간

키 오프 판단에 쓰는 두 값은 TECU가 100 ms마다 보내는 Wheel-based speed and distance 메시지(PGN 65096(0xFE48))에 들어 있다. 이 메시지의 나머지 필드는 [23장](/study/isobus/23-implement-messages-basics)에서 다룬다.

| 위치 | 파라미터 | 값 |
|---|---|---|
| Byte 7 | Maximum time of tractor power | 현재 부하에서 남은 트랙터 전원 시간. 추정치여도 된다. 1 min/bit, 0~250 min |
| Byte 8 bits 4·3 | Key switch state | `00` Key switch off, `01` not off, `10` error, `11` not available |

Maximum time of tractor power는 트랙터가 지금 부하로 전원을 더 줄 수 있는 시간이고, 1 min/bit는 값 1이 1분이라는 뜻이다. Key switch state는 2비트 칸이다. `10` error는 키 상태를 읽는 데 문제가 생겼다는 표시, `11` not available은 값을 줄 수 없다는 표시다.

Key switch state는 엔진 시동 때 같은 <strong>예기치 않은 전원 순단(아주 짧은 정전)을 나타내지 않는다</strong>. ISO 11783-7은 키를 끄면 이 메시지를 2 s 더 보내도록 ECU_PWR과 PWR을 둘 다 유지해야 하며, 엔진 크랭킹(시동 모터로 엔진을 돌리는 동안) 중에는 그럴 필요가 없다고 적는다. ISO 11783-9도 시동 순단 중에는 key switch state 송신과 전원 유지 기능이 멈출 수 있다고 한다. CF는 key switch state가 `01`에서 `00`으로 바뀌는 것을 키 오프로 보고, 전원 순단 자체를 키 오프로 오인하지 않아야 한다.

### Maintain power 메시지

작업기 버스의 어느 CF든 보낼 수 있는 메시지로, Wheel-based speed and distance로 키 오프를 알게 된 뒤 TECU에게 2 s 동안 전원을 끄지 말라고 요청한다. 연결된 작업기의 운용 상태도 함께 싣는다.

| 항목 | 값 |
|---|---|
| PGN | 65095(0xFE47), PF 254·PS 71 |
| 기본 우선순위 | 6 → CAN ID `0x18FE47xx` |
| 주기 | 키가 ON → OFF로 바뀐 것을 받은 뒤 필요할 때, 또는 파라미터 상태가 바뀔 때 |

CAN ID 끝의 `xx`는 보내는 CF의 SA 자리다. 데이터 표 읽는 법: "Byte 1 bits 8·7"은 Byte 1의 가장 높은 두 비트다. 2비트 칸 하나에 값 네 가지를 쓴다.

| 위치 | 파라미터 | 값 |
|---|---|---|
| Byte 1 bits 8·7 | Maintain ECU power | `00` 더 필요 없음, `01` ECU_PWR 2 s 더, `10` 예약, `11` don't care |
| Byte 1 bits 6·5 | Maintain actuator power | `00` 더 필요 없음, `01` PWR 2 s 더, `10` 예약, `11` don't care |
| Byte 1 bits 4~1 | 예약 | `1111` |
| Byte 2 bits 8·7 | Implement transport state | `00` 운반 불가, `01` 운반 가능 |
| Byte 2 bits 6·5 | Implement park state | `00` 분리 불가, `01` 분리 가능 |
| Byte 2 bits 4·3 | Implement ready-to-work state | `00` 작업 준비 안 됨, `01` 준비됨 |
| Byte 2 bits 2·1 | Implement in-work state | `00` 작업 중 아님, `01` 작업 중 |
| Byte 3~8 | 예약 | `FF` |

Byte 2의 네 상태는 `10`이 error, `11`이 not available이다. 예약 비트(아직 쓰임이 정해지지 않은 비트)는 ISO 11783-7의 관례대로 모두 1로 보낸다. 그러면 Byte 1에서 자주 쓰는 값이 정해진다.

| Byte 1 | 뜻 |
|---|---|
| `5F` | ECU_PWR·PWR 둘 다 2 s 더 |
| `4F` | ECU_PWR만 2 s 더, PWR은 더 필요 없음 |
| `0F` | 둘 다 더 필요 없음 |
| `FF` | 전원 요청과 무관하게 작업기 상태만 알림(don't care) |

`5F`가 나오는 과정을 따라가 보자.

1. bits 8·7(Maintain ECU power)에 `01`(ECU_PWR 2 s 더)을 넣는다.
2. bits 6·5(Maintain actuator power)에 `01`(PWR 2 s 더)을 넣는다.
3. bits 4~1(예약)은 `1111`로 채운다.
4. 이어 붙이면 `0101 1111`, 16진수로 `5F`다. PWR 칸만 `00`으로 바꾸면 `0100 1111` = `4F`, 둘 다 `00`이면 `0000 1111` = `0F`다.

`FF`의 쓰임은 "파라미터 상태가 바뀔 때"라는 송신 조건과 `11` = don't care를 합쳐 읽은 것이다(해석).

### 키 오프 시퀀스: 시간 축으로 보기

System shutdown은 key switch state가 off를 가리킨 뒤 ECU_PWR이 <strong>적어도 2 s</strong> 유지되는 기간이다. PWR은 이 동안 ECU_PWR과 함께 유지될 수도, 아닐 수도 있다. 아래 그림은 요청이 이어지는 예를 시간 축에 놓은 것이다. 가로축은 키를 끈 순간을 0으로 둔 시간(초)이다.

![키 오프 시간 축: t = 0에 키 스위치 상태가 off로 바뀌고, CF가 0.5~4.5 s에 Maintain power 5F, 5.5~7.5 s에 4F를 보내면 PWR은 마지막 5F 2 s 뒤인 6.5 s에, ECU_PWR은 마지막 4F 2 s 뒤인 9.5 s에 마지막 off 메시지를 보낸 다음 100 ms 안에 꺼진다](/images/study-isobus/22-keyoff-timeline-light.png)
![키 오프 시간 축: t = 0에 키 스위치 상태가 off로 바뀌고, CF가 0.5~4.5 s에 Maintain power 5F, 5.5~7.5 s에 4F를 보내면 PWR은 마지막 5F 2 s 뒤인 6.5 s에, ECU_PWR은 마지막 4F 2 s 뒤인 9.5 s에 마지막 off 메시지를 보낸 다음 100 ms 안에 꺼진다](/images/study-isobus/22-keyoff-timeline-dark.png)

1. t = 0: 운전자가 키를 끈다. TECU는 100 ms마다 보내는 key switch state를 `01`(not off)에서 `00`(off)으로 바꾼다.
2. 0.5~4.5 s: 밸브·액추에이터를 안전한 위치로 정리하는 CF가 Maintain power `5F`(ECU_PWR·PWR 둘 다 2 s 더)를 1 s마다 보낸다.
3. 5.5~7.5 s: 정리가 끝나 PWR은 필요 없어졌다. 설정을 저장하는 동안 `4F`(ECU_PWR만 2 s 더)를 보낸다.
4. PWR: 마지막 `5F`(4.5 s)의 효력이 2 s 뒤인 6.5 s에 끝나므로, TECU는 6.5 s부터 PWR을 끌 수 있다.
5. ECU_PWR: 마지막 `4F`(7.5 s)의 효력이 9.5 s에 끝난다. TECU는 그 뒤 마지막 key switch off 메시지를 보내고, 100 ms 안에 ECU_PWR을 끈다.

요청이 하나도 없었다면 TECU는 키 오프 뒤 2 s 이상 key off 메시지를 보내고, 마지막 메시지 뒤 100 ms 안에 두 전원을 함께 끈다.

아래 그림은 같은 흐름을 메시지 순서로 그린 것이다. 표준이 드는 예 가운데 CF가 밸브 정리를 먼저 끝내고 데이터 저장을 이어 가는 경우를 옮겼다.

![키 오프 시퀀스: TECU가 100 ms마다 Key switch off와 Maximum time을 보내고, CF가 1 s마다 Maintain power를 보내다가 PWR 요청을 먼저 내리면 PWR이 먼저 꺼지고, 마지막 ECU_PWR 요청 2 s 뒤 마지막 Key switch off를 보낸 다음 100 ms 안에 ECU_PWR이 꺼진다](/images/study-isobus/13-power-keyoff-light.png)
![키 오프 시퀀스: TECU가 100 ms마다 Key switch off와 Maximum time을 보내고, CF가 1 s마다 Maintain power를 보내다가 PWR 요청을 먼저 내리면 PWR이 먼저 꺼지고, 마지막 ECU_PWR 요청 2 s 뒤 마지막 Key switch off를 보낸 다음 100 ms 안에 ECU_PWR이 꺼진다](/images/study-isobus/13-power-keyoff-dark.png)

그림 속 3 min, 2 min은 예시 값이다. Maximum time은 부하에 따른 추정치이고 시간이 지나며 줄어든다. 그림에서 1 min이 지난 뒤 2 min으로 줄어드는 모습이 그것이다.

### CF 구현 절차

키 오프 뒤 정리에 2 s가 넘게 걸리는 CF만 Maintain power를 보낸다. 2 s 안에 끝나는 일은 기본 유지 시간 안에 하면 된다.

1. Wheel-based speed and distance의 Byte 8 bits 4·3을 감시하다 `01` → `00` 전환을 잡는다.
2. 밸브·액추에이터를 셧다운 상태로 만드는 데 2 s 넘게 걸리면 Byte 1 = `5F`를 1 s에 1회 이상 보낸다. 끝나면 PWR 요청을 내린다(`4F` 또는 `0F`).
3. 설정·로그 저장에 2 s 넘게 걸리면 `4F`를 1 s에 1회 이상 보낸다. 끝나면 송신을 멈추거나 `0F`를 보낸다.
4. 그동안 Byte 7의 Maximum time을 보고 남은 시간이 충분한지 판단한다. 허용 시간 안에 못 끝낼 것 같으면 다음 전원 인가 때 운전자에게 알려 설정 확인, 밸브·액추에이터 상태 점검, 배터리 교체 같은 조치를 하게 하는 것이 권장된다.

<small>근거: ISO 11783-9 4.6.1~4.6.4, Figure 6, ISO 11783-7 B.3, B.4, A.11~A.17, A.33, 3.3.3</small>

## 6. 키 오프 시간 규정과 검산 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

5절의 흐름을 만드는 시간 규정 전체와, 표준이 드는 네 가지 경우를 정리하고 코드로 검산한다.

| 규정 | 값 |
|---|---|
| key switch state 송신 주기 | 100 ms |
| 키 오프 뒤 전원 유지 하한 | 요청이 없어도 2 s 이상 |
| 유지 요청 1회의 효력 | 다음 2 s |
| 요청 반복 간격 | 1 s에 1회 이상(shall). 그림의 간격 표시는 2 s 미만 |
| 마지막 요청 → 차단 | 2 s 이상 |
| 마지막 Key switch off 메시지 → 차단 | 100 ms 미만 |
| Maximum time이 0 min | 요청과 무관하게 2 s 이상 뒤 마지막 메시지, 100 ms 안에 차단 |

"요청 반복 간격" 행의 "그림"은 표준의 예시 그림을 말한다. 그 그림에는 요청 사이 간격이 2 s 미만으로 표시돼 있다.

표준은 네 가지 경우를 그림으로 든다. 5절의 시퀀스 그림이 경우 4다.

| 경우 | 상황 | TECU 동작 |
|---|---|---|
| 경우 1 | 유지 요청 없음 | key off 메시지를 2 s 이상 보내고, 마지막 메시지 뒤 100 ms 안에 ECU_PWR·PWR을 함께 끈다 |
| 경우 2 | ECU_PWR·PWR 요청, Maximum time 안에 끝남 | 마지막 요청 뒤 2 s 이상 지나 마지막 key off를 보내고 100 ms 안에 둘 다 끈다 |
| 경우 3 | Maximum time 안에 못 끝냄 | Maximum time이 0 min이 되면 요청이 이어져도 2 s 이상 뒤 끈다 |
| 경우 4 | PWR 작업을 먼저 끝냄 | PWR을 먼저 끄고, ECU_PWR은 ECU 요청이 끝난 뒤 끈다 |

표준의 그림은 요청 CF가 하나인 경우만 보여 준다. 여러 CF가 동시에 요청하면 TECU는 아직 효력이 남은 요청이 하나라도 있는 동안 전원을 유지한다고 보는 것이 "요청 1회의 효력은 다음 2 s"라는 정의와 맞는다(해석).

아래 코드는 Maintain power 바이트를 만드는 함수, Wheel-based speed 프레임에서 key switch state를 꺼내는 함수, 그리고 전원을 가장 일찍 끌 수 있는 시각을 계산하는 함수다. 5절 시간 축 그림의 예(5F를 0.5~4.5 s, 4F를 5.5~7.5 s)도 들어 있다.

::: details Maintain power 인코딩과 최소 차단 시각 검산 (Python)
```python
def maintain_power(ecu, pwr, transport=3, park=3, ready=3, in_work=3):
    byte1 = (ecu << 6) | (pwr << 4) | 0x0F
    byte2 = (transport << 6) | (park << 4) | (ready << 2) | in_work
    return bytes([byte1, byte2]) + b"\xff" * 6

def key_switch_state(wheel_speed_frame):
    return (wheel_speed_frame[7] >> 2) & 0b11

assert maintain_power(1, 1).hex(" ").upper() == "5F FF FF FF FF FF FF FF"
assert maintain_power(1, 0, 0, 0, 0, 0)[:2].hex(" ").upper() == "4F 00"
assert maintain_power(0, 0)[0] == 0x0F
assert key_switch_state(bytes([0, 0, 0, 0, 0, 0, 3, 0b11110001])) == 0b00

def earliest_off(key_off, ecu_requests, pwr_requests, max_time_s=None):
    pwr = max([key_off + 2.0] + [t + 2.0 for t in pwr_requests])
    ecu = max([key_off + 2.0, pwr] + [t + 2.0 for t in ecu_requests])
    if max_time_s is not None:
        deadline = key_off + max_time_s + 2.0
        pwr, ecu = min(pwr, deadline), min(ecu, deadline)
    return pwr, ecu

both = [0.5, 1.5, 2.5, 3.5, 4.5]
assert earliest_off(0.0, [], []) == (2.0, 2.0)
assert earliest_off(0.0, both, both) == (6.5, 6.5)
assert earliest_off(0.0, both + [5.5, 6.5, 7.5], both) == (6.5, 9.5)
assert earliest_off(0.0, [0.5 + i for i in range(400)],
                   [0.5 + i for i in range(400)], max_time_s=180) == (182.0, 182.0)
```

`earliest_off`는 위 네 가지 경우를 "이보다 먼저 끄면 안 되는 시각"으로 옮긴 해석 모델이다. 실제 차단은 이 시각 뒤 마지막 Key switch off 메시지로부터 100 ms 안에 일어난다.
:::

세 번째 `assert`의 `(6.5, 9.5)`가 5절 시간 축 그림의 PWR 6.5 s, ECU_PWR 9.5 s다. 마지막 `assert`는 경우 3이다. 요청이 400 s 동안 이어져도 Maximum time 180 s(3 min)가 끝나고 2 s 뒤인 182 s에 둘 다 끌 수 있다.

::: details 원문을 가진 독자를 위한 메모
- 경우 1~4는 ISO 11783-9:2012 Figure 3~6이다. 5절의 시퀀스 그림은 Figure 6을 옮긴 것이다.
- 시간 규정 표의 근거: 송신 주기 100 ms는 Figure 3~6과 ISO 11783-7 B.3, 유지 하한 2 s는 4.6.4.1·Figure 3·B.3, 1회 효력 2 s는 ISO 11783-7 A.13·A.14, 반복 간격은 4.6.4.2 b)·4.6.4.3 b)·Figure 4, 마지막 요청 → 차단은 Figure 4·6, 마지막 off → 차단 100 ms는 Figure 3~6, Maximum time 0 min은 Figure 5다.
:::

<small>근거: ISO 11783-9 4.6.4, Figure 3~6, ISO 11783-7 B.3, A.13, A.14</small>

## 7. Safe mode와 파워트레인 메시지 규칙

전원이나 통신이 끊기는 일은 언제든 생길 수 있다. 이 절은 그때 작업기가 지켜야 할 Safe mode 요구와, 엔진·변속기 같은 파워트레인 메시지를 어느 문서에서 찾는지 정한 규칙을 본다.

### Safe mode

트랙터와의 전원이나 통신이 끊기면 작업기는 페일세이프(fail-safe, 고장이 나도 안전한 쪽으로 멈추는 설계) 상태로 들어가야 한다. 전원 공급의 중단, 중단 뒤 재개, 어떤 형태의 변동도 위험을 만들면 안 되고, 제어 로직의 결함이나 제어 회로의 고장·손상도 위험으로 이어지면 안 된다. 세부 요구는 모두 shall이다. 오른쪽 열은 그 요구를 소프트웨어로 지키는 방법의 예다(해석).

| 번호 | 요구 | 구현 관점의 예 |
|---|---|---|
| 1 | 작업기가 예기치 않게 기동하지 않는다 | 전원이 돌아온 뒤 액추에이터를 이전 상태로 자동 복귀하지 않고 운전자 확인을 받는다 |
| 2 | 정지 명령이 내려진 뒤 정지가 방해받지 않는다 | 정지 경로가 버스 통신 성공에 의존하지 않게 한다 |
| 3 | 작업기 부품이나 작업기가 쥔 물체가 떨어지거나 튕겨 나가지 않는다 | 전원이 없을 때 하중을 잡는 쪽이 기본 상태가 되게 밸브를 고른다 |
| 4 | 움직이는 부품의 자동·수동 정지가 방해받지 않는다 | 소프트웨어 인터록이 수동 정지를 막지 않게 한다 |
| 5 | 보호 장치가 완전한 효력을 유지한다 | 통신 장애 모드에서도 보호 기능을 끄지 않는다 |
| 6 | 운전자가 원격 제어하는 작업기는 감지 가능한 고장으로 원격 제어를 못 하게 되면 자동으로 멈춘다 | VT·TC·TECU 메시지의 수신 타임아웃을 고장으로 감지해 정지한다 |
| 7 | 운전자가 작업기 제어 시스템을 오버라이드할 수 있다 | 자동 제어 중에도 수동 조작이 우선하게 한다 |

인터록(interlock)은 조건이 맞지 않으면 동작을 막는 잠금 장치, 오버라이드(override)는 자동 제어를 사람이 덮어써 직접 조작하는 것이다.

이 요구는 작업기가 트랙터를 명령하는 Class 3·G·P 구성에서 특히 중요하다. 트랙터는 명령을 거부할 수 있고 제약을 스스로 판단해 적절할 때만 acknowledge한다(3절). 작업기는 명령이 거부되거나 통신이 끊기는 경우를 정상 경로로 다뤄야 한다. 통신 무결성을 확인하는 heartbeat 메시지(살아 있다는 신호를 주기적으로 보내는 메시지)는 [25장](/study/isobus/25-settings-safety-messages)에서 다룬다.

### 파워트레인 메시지 적용 규칙

ISO 11783-8(2006년 1판)은 문서 전체가 세 쪽뿐인 짧은 파트다. 트랙터나 자주식 작업기(콤바인처럼 스스로 움직이는 작업기)의 파워트레인(엔진·변속기처럼 동력을 만들고 전하는 장치) 모니터링·제어를 위한 메시지 세트를 다루지만, 메시지를 직접 정의하지 않고 규칙 두 개만 둔다.

- 파워트레인 제어에 필요한 <strong>파라미터</strong>는 SAE J1939-71의 정의를 쓴다. 단 Part 7에도 정의된 파라미터는 Part 7 정의를 따라야 한다(shall).
- <strong>파라미터 그룹</strong>도 같다. J1939-71의 정의를 쓰되 Part 7에도 있는 PG는 Part 7 정의를 따른다(shall).

SAE J1939-71은 트럭·버스용 J1939의 응용 계층 메시지(엔진 회전수 같은 값의 정의)를 담은 문서이고, Part 7은 ISO 11783-7이다.

다른 파트와의 연결은 세 군데다. 트랙터 네트워크는 Part 8·Part 7 메시지와 독점 메시지를 쓸 수 있고, 파워트레인 메시지는 작업기 네트워크의 CF도 쓸 수 있다. Class 1 TECU가 보내는 engine speed가 Part 8 소관이며, 송신 주기 100 ms는 Part 9(ISO 11783-9)가 덧붙인 요구다. 엔진 회전수 같은 파워트레인 메시지의 PGN과 바이트 배치는 ISO 11783 문서에 없으므로 J1939-71에서 확인해야 한다. 구현 순서는 "Part 7에 있으면 Part 7, 없으면 J1939-71"이다. ISO 11783-8의 머리말은 J1939 공동 문서의 목적을 트럭·버스용 J1939 규격을 만족하는 전자 장치를 농림 장비에 최소한의 변경으로 쓰게 하는 데 두는데, Part 8의 참조 규칙은 그 목적을 파워트레인 영역에서 실현하는 장치로 읽힌다(해석).

<small>근거: ISO 11783-9 4.7.1~4.7.8, 4.4.2.2, 4.4.2.4, 4.4.3, ISO 11783-8 Introduction, 4.1~4.3, ISO 11783-1 6.6.2, 6.6.3</small>

::: tip 핵심 정리
- TECU는 작업기 버스에서 트랙터를 대표하는 하나의 CF다. 트랙터 정보는 모두 TECU의 SA로 나오고, 포트는 1이 작업기 버스, 2가 트랙터 버스다.
- 클래스 숫자는 측정(1·2)과 명령 수용(3)을 가르고, G·P는 기본 클래스와 무관하다. facility response의 클래스 코드는 `00`이 class 1이다.
- 조명은 instance 0 TECU 책임이지만, 2018년 개정 이후 정식 인증 조명은 7핀 커넥터가 1차 경로다.
- 키 오프 뒤 전원은 요청이 없어도 2 s 이상 유지되고, 그보다 오래 필요하면 Maintain power를 1 s에 1회 이상 보낸다. 마지막 Key switch off 뒤 100 ms 안에 전원이 끊긴다.
- 전원이나 통신이 끊기면 작업기는 스스로 안전한 상태로 멈춰야 하고, 운전자의 수동 조작이 언제나 우선한다.
:::

::: details 확인 문제
1. (개념) 작업기 버스에서 트랙터 속도 메시지를 받았다. 이 메시지의 SA는 트랙터 버스에 있는 변속기 ECU의 주소인가, TECU의 주소인가? 이유는?
2. (디코딩) Lighting command의 Byte 1이 `13`이다. 2비트 칸 네 개의 값을 쓰고, 하향등이 켜졌는지 답하라.
3. (개념) 키를 끈 뒤 아무 CF도 Maintain power를 보내지 않으면 ECU_PWR과 PWR은 언제 꺼지는가?
4. (판단) TECU가 tractor facility response로 class 2GP를 알렸다. 작업기가 보낼 수 있는 명령은 조향 곡률 명령, 속도 set point, 리어 히치 위치 명령 중 무엇인가? facility response의 클래스 필드 값은 무엇이어야 하나?
5. (설계) 분무기 ECU는 키 오프 뒤 붐을 접는 데 5 s, 로그를 저장하는 데 4 s가 걸린다. 어떤 신호를 보고, 어떤 Maintain power 바이트를 언제 보내야 하나? TECU는 PWR과 ECU_PWR을 각각 언제부터 끌 수 있나?

**답 가이드**
1. TECU의 주소다. TECU는 트랙터 버스의 정보를 모아 자기 SA로 다시 보내므로 작업기 버스에는 트랙터 버스 CF의 SA가 나타나지 않는다.
2. `13`은 2진수 `0001 0011`이라 네 칸이 차례로 `00`, `01`, `00`, `11`이다. 상향등 끔, 하향등 켬, alternate 끔, 주간 주행등 don't care다. 하향등은 켜졌다.
3. TECU는 key off 메시지를 2 s 이상 보내고, 마지막 메시지 뒤 100 ms 안에 ECU_PWR과 PWR을 함께 끈다. 키를 끈 뒤 약 2 s 지나 두 전원이 함께 꺼진다.
4. G와 P는 기본 클래스와 무관하므로 조향 곡률 명령과 속도 set point는 보낼 수 있다(정지·주행 전략 제어는 선택이라 facility로 확인한다). 리어 히치 위치 명령은 class 3이 필요하므로 이 트랙터에는 보낼 수 없다. 클래스 필드는 `01`(class 2)이다.
5. Wheel-based speed and distance(PGN 65096) Byte 8 bits 4·3이 `01` → `00`으로 바뀌는 것을 본다. 붐을 접는 약 5 s 동안 Byte 1 = `5F`를 1 s에 1회 이상, 이어서 로그 저장 약 4 s 동안 `4F`를 1 s에 1회 이상 보내고, 끝나면 멈추거나 `0F`를 보낸다. Byte 7의 Maximum time이 필요한 시간보다 큰지도 확인한다. TECU는 PWR을 마지막 `5F`로부터 2 s 이상 지난 뒤에 끌 수 있고, ECU_PWR은 마지막 `4F`로부터 2 s 이상 지나 마지막 Key switch off를 보낸 뒤 100 ms 안에 끈다.
:::

## 다음 챕터

- 다음: [23장 트랙터-작업기 메시지 (1): 읽는 법과 시간·속도·위치](/study/isobus/23-implement-messages-basics)
