---
title: "ISOBUS 네트워크 구성: 버스, 커넥터, ECU"
description: "ISOBUS 네트워크가 트랙터 버스와 작업기 버스로 나뉘는 까닭, 작업기를 꽂는 IBBC 커넥터와 버스 끝의 TBC, 주요 ECU의 역할, 시동 뒤 통신이 자리 잡는 순서를 익힌다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, IBBC, TBC, VT, TaskController, ECU]
prev: /study/isobus/19-isobus-part1-requirements
next: /study/isobus/21-niu-network-layer
---

# ISOBUS 네트워크 구성: 버스, 커넥터, ECU

::: info 학습 목표
- ISOBUS 네트워크가 트랙터 버스와 작업기 버스로 나뉘는 이유와, 두 버스를 TECU가 잇는 구조를 설명할 수 있다.
- IBBC(작업기를 꽂는 9핀 커넥터)와 TBC(버스 끝을 맺는 종단 회로)의 역할을 구분할 수 있다.
- VT, TC, TECU, Working Set Master 같은 주요 ECU의 역할과 소속 버스를 말할 수 있다.
- 시동 뒤 ISOBUS 통신이 자리 잡기까지의 메시지 흐름을 순서대로 설명할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [3장 CAN 물리 계층](/study/isobus/03-can-physical), [18장 ISOBUS 개요](/study/isobus/18-isobus-overview), [19장 ISO 11783 Part 1](/study/isobus/19-isobus-part1-requirements)
- 이 장에서 처음 나오는 말
  - 토폴로지: 장치들이 선으로 어떻게 이어졌는지 나타낸 배치도.
  - 게이트웨이: 두 네트워크 사이에서 메시지를 걸러 내고 다시 꾸며 넘겨 주는 장치.
  - IBBC: 트랙터 뒤에서 작업기 케이블을 꽂는 9핀 커넥터.
  - TBC: 버스 양 끝에 다는 능동 종단 회로.
  - Working Set: 작업기 한 대의 일을 나눠 맡는 CF 묶음. 대표 CF를 Working Set Master라고 한다.
  - 오브젝트 풀: 작업기가 VT에 보내는 화면 설계 데이터.
:::

회사는 사내망과 손님용 와이파이를 나누고, 그 사이에 방화벽을 둔다. 손님 노트북이 문제를 일으켜도 사내망은 멀쩡하게 지키려는 것이다. ISOBUS도 같은 생각으로 트랙터 자체의 버스와 작업기가 붙는 버스를 나누고, 그 사이에 TECU를 둔다. 이 장은 그 구조와 커넥터, 버스 위의 ECU들, 그리고 시동을 걸었을 때 통신이 자리 잡는 순서를 본다.

## 1. 네트워크 토폴로지: 버스 두 개

이 절은 ISOBUS 네트워크 전체의 배치(토폴로지)를 본다. 결론부터 말하면 버스가 두 개이고, 그 사이를 TECU가 지킨다.

ISOBUS 네트워크는 물리적으로 두 개의 네트워크 세그먼트로 구성된다. 세그먼트는 양 끝을 종단 회로로 맺은 버스 한 토막이다.

- <strong>트랙터 버스</strong>(tractor network): 엔진, 변속기, 브레이크, 히치 컨트롤러 등 트랙터 구동계·섀시 ECU들이 연결되는 버스. 트랙터 제조사가 관리하며 내부 규격(J1939 등)을 쓸 수도 있다.
- <strong>작업기 버스</strong>(implement network): VT, TC, 작업기 ECU 등 작업기 관련 CF들이 연결되는 버스. 트랙터 위와 작업기 위에 걸쳐 존재하며 ISO 11783을 반드시 준수해야 한다.

[19장](/study/isobus/19-isobus-part1-requirements)에서는 Part 1의 용어를 따라 같은 것을 트랙터 네트워크, 작업기 네트워크라고 불렀다. 구동계는 엔진의 힘을 바퀴까지 전하는 장치들이고, 섀시는 차체의 뼈대와 그에 붙은 장치들이다.

두 버스는 <strong>TECU(Tractor ECU)</strong>가 연결한다. TECU는 두 세그먼트 사이의 게이트웨이 역할을 하는 특수 NIU(Network Interconnection Unit, 버스와 버스를 잇는 장치)다. VT와 TC는 물리적으로 트랙터 캐빈에 장착되지만 <strong>버스 소속은 작업기 버스</strong>이며, 외부 작업기는 <strong>IBBC(Implement Bus Breakaway Connector)</strong>를 통해 작업기 버스에 이어진다.

![ISOBUS 네트워크 토폴로지: 트랙터 안에서 엔진·변속기·히치 ECU가 트랙터 버스에 붙고, 트랙터 버스와 작업기 버스(250 kbit/s CAN) 사이를 게이트웨이 NIU인 TECU가 잇는다. 운전석의 VT와 TC는 작업기 버스에 붙고, 작업기 버스는 IBBC 9핀 커넥터를 지나 작업기로 이어져 Working Set Master와 Working Set Member 1·2가 붙는다](/images/study-isobus/20-two-bus-topology-light.png)
![ISOBUS 네트워크 토폴로지: 트랙터 안에서 엔진·변속기·히치 ECU가 트랙터 버스에 붙고, 트랙터 버스와 작업기 버스(250 kbit/s CAN) 사이를 게이트웨이 NIU인 TECU가 잇는다. 운전석의 VT와 TC는 작업기 버스에 붙고, 작업기 버스는 IBBC 9핀 커넥터를 지나 작업기로 이어져 Working Set Master와 Working Set Member 1·2가 붙는다](/images/study-isobus/20-two-bus-topology-dark.png)

그림을 위에서 아래로 읽는다.

1. 트랙터 안쪽 ECU(엔진, 변속기, 히치)는 트랙터 버스에 붙는다.
2. 트랙터 버스와 작업기 버스 사이에 TECU가 있다. 두 버스가 직접 맞닿는 곳은 없다.
3. 운전석의 VT와 TC는 작업기 버스에 붙는다. 둘 다 작업기와 대화하는 장치이기 때문이다.
4. 작업기 버스는 IBBC를 지나 작업기로 이어지고, 작업기 쪽 ECU들(Working Set Master와 Member)이 여기에 붙는다.

두 버스를 분리하는 이유는 <strong>트랙터 버스의 격리·보호</strong>다. TECU는 두 세그먼트 사이에서 전기적 격리와 메시지 격리(필터링)를 모두 제공해야 하며, 덕분에 외부 작업기의 전기적 문제나 과도한 트래픽이 트랙터 구동계 버스에 영향을 주지 않는다.

앞의 방화벽 비유와 다른 점도 있다. 방화벽은 데이터만 거르지만, TECU는 전기적으로도 두 버스를 갈라놓는다. 또 TECU는 작업기의 요청을 받아 트랙터 버스의 ECU들과 대신 통신하고, 트랙터 정보를 작업기 버스에 알려 준다([22장](/study/isobus/22-tractor-ecu)).

::: tip NIU의 다섯 가지 유형
ISO 11783-4(네트워크 계층을 정하는 문서)는 세그먼트를 연결하는 NIU를 기능 수준에 따라 나눈다. 리피터(받은 신호를 그대로 넘기는 단순 forwarding), 브리지(+ 필터링), 라우터(+ 주소 변환), 게이트웨이(+ 메시지 재조합)가 있고, 트랙터 버스와 작업기 버스를 잇는 <strong>Tractor ECU</strong>가 다섯 번째 특수 유형으로 정의된다. 작업기 내부에 하위 네트워크를 둘 때도 NIU로 작업기 버스와 격리한다. 유형별 비교는 [21장](/study/isobus/21-niu-network-layer)에서 본다.
:::

<small>근거: ISO 11783-1 6.6, 6.7.1, 6.7.2, ISO 11783-4 Clause 7</small>

## 2. IBBC 커넥터와 TBC 종단

이 절은 작업기를 트랙터에 꽂는 커넥터와, 버스 끝을 마무리하는 회로를 본다. 둘 다 약자가 비슷해 헷갈리기 쉽지만, 하나는 플러그이고 하나는 회로다.

<strong>IBBC(Implement Bus Breakaway Connector)</strong>는 트랙터와 작업기의 작업기 버스를 물리적으로 연결하는 9핀 커넥터이다. ISO 11783-2(물리 계층을 정하는 문서)에 정의되어 있으며, 작업기가 분리(breakaway)되어도 트랙터 측 버스가 안전하게 유지되도록 설계된다. 브레이크어웨이는 당기면 빠지도록 만든 연결이라는 뜻이다. [3장](/study/isobus/03-can-physical)에서 본 진단용 9핀 커넥터와는 다른 커넥터다. Part 1도 작업기 연결용 커넥터와 진단 커넥터를 따로 구분한다.

<strong>TBC(Terminating Bias Circuit)</strong>는 커넥터가 아니라 <strong>종단 바이어스 회로</strong>다. 네트워크 세그먼트 양 끝단에 두어 CAN_H·CAN_L에 바이어스 전압과 공통 모드 임피던스 종단을 제공하는 능동 종단으로, 단순 120Ω 저항 종단(J1939-11)과 구별된다.

[3장](/study/isobus/03-can-physical)에서 CAN 버스 양 끝에 120 Ω 저항을 달아 신호가 끝에서 되튀지 않게 한다고 했다. TBC는 그 종단 역할에 더해, 전원을 받아 CAN_H와 CAN_L을 정해진 전압 쪽으로 잡아 준다(바이어스). 전원을 받아 스스로 동작하는 회로라서 "능동" 종단이라고 부른다.

### 9핀 커넥터 신호 구성

IBBC의 9개 신호는 세 그룹으로 나뉜다. CAN 그룹은 데이터, 전원 그룹은 작업기가 쓸 전기, 종단 제어 그룹은 TBC를 위한 선이다.

| 그룹 | 신호 | 설명 |
|------|------|------|
| CAN | CAN_H, CAN_L | 작업기 버스 신호선 1쌍 (트랙터 내부 버스는 커넥터를 지나지 않는다) |
| 전원 | PWR, GND, ECU_PWR, ECU_GND | 액추에이터용 전원(PWR)과 ECU 전자회로용 전원(ECU_PWR), 각각의 접지 |
| 종단 제어 | TBC_PWR, TBC_RTN, TBC_DIS | 종단 바이어스 회로(TBC)의 전원·리턴·비활성화 신호 |

액추에이터는 전기 신호를 받아 실제로 움직이는 부품(밸브, 모터)이고, 접지(GND)는 전류가 돌아오는 기준선이다. 핀 번호와 커넥터 모양은 Part 2가 정하는데, 이 스터디의 근거 자료에 Part 2가 없어 싣지 않는다.

![IBBC 9핀이 나르는 세 묶음: CAN_H와 CAN_L은 작업기 버스 데이터를 양방향으로 잇고, PWR·GND는 액추에이터 전원(12 V에서 최소 50 A), ECU_PWR·ECU_GND는 작업기 ECU·센서 전원(12 V에서 최소 15 A)을 트랙터에서 작업기로 보내며, TBC_PWR·TBC_RTN·TBC_DIS는 종단 바이어스 회로용 선이다. 두 전원의 분배는 TECU가 제어한다](/images/study-isobus/20-ibbc-signal-groups-light.png)
![IBBC 9핀이 나르는 세 묶음: CAN_H와 CAN_L은 작업기 버스 데이터를 양방향으로 잇고, PWR·GND는 액추에이터 전원(12 V에서 최소 50 A), ECU_PWR·ECU_GND는 작업기 ECU·센서 전원(12 V에서 최소 15 A)을 트랙터에서 작업기로 보내며, TBC_PWR·TBC_RTN·TBC_DIS는 종단 바이어스 회로용 선이다. 두 전원의 분배는 TECU가 제어한다](/images/study-isobus/20-ibbc-signal-groups-dark.png)

### 전원 공급 구조

트랙터는 IBBC를 통해 작업기에 전원을 공급한다. 전원은 용도별로 두 계열로 나뉜다.

- <strong>ECU_PWR</strong>: 작업기 ECU·센서 등 전자회로용 전원 (12V 기준 최소 15A)
- <strong>PWR</strong>: 밸브·모터 등 액추에이터용 전원 (12V 기준 최소 50A)

두 전원의 분배 제어와 상태 메시지 송수신은 TECU(function instance 0)가 책임진다. function instance는 같은 기능의 장치가 여럿일 때 붙이는 순번이고, TECU가 여럿이면 0번인 첫째 TECU가 이 일을 맡는다. TBC_PWR은 ECU_PWR 또는 TECU 자체에서 급전되어, ECU 전원이 제어되는 상황에서도 버스 종단이 살아 있도록 한다. 작업기 자체 전원(배터리)이 없어도 트랙터에 연결하면 즉시 동작 가능하다.

두 계열을 나눈 덕분에 전원을 따로 다룰 수 있다. 예를 들어 키를 끈 뒤 작업기가 설정이나 기록 파일을 저장해야 하면 ECU_PWR만 유지해 달라고 요청할 수 있고, 밸브를 안전한 위치로 돌려놓아야 하면 PWR과 ECU_PWR을 함께 유지해 달라고 요청할 수 있다. 이 절차는 [22장](/study/isobus/22-tractor-ecu)에서 본다.

<small>근거: ISO 11783-1 3.63, 6.2, Figure 2, ISO 11783-9 4.4.2.1, 4.6.1, 4.6.2, 4.6.4</small>

## 3. ISOBUS 위의 ECU들

이 절은 ISOBUS 네트워크 위에서 일하는 주요 ECU를 본다. ISOBUS 네트워크 위에는 역할별로 명확히 구분된 ECU들이 존재한다.

운전자 자리에서 보면 쉽다. 운전자는 VT 화면으로 작업기를 보고 조작한다. TC는 작업 계획대로 작업기에 지시하고 기록을 남긴다. TECU는 트랙터의 속도와 상태를 알려 준다. 작업기 쪽에서는 Working Set Master(줄여서 WSM)가 대표로 이들과 대화하고, 작업기 안의 다른 ECU(Working Set Member)를 지휘한다.

![ISOBUS 위 ECU들의 역할과 관계: AUX 입력 장치가 VT로 조작 신호를, GPS 수신기가 TC로 위치 정보를 보내고, VT는 UI 요청과 응답을, TC는 작업 명령을, TECU는 속도·PTO 정보를 Working Set Master에 주며, Working Set Master는 Working Set Member를 내부 제어한다](/images/study-isobus/20-ecu-roles-light.png)
![ISOBUS 위 ECU들의 역할과 관계: AUX 입력 장치가 VT로 조작 신호를, GPS 수신기가 TC로 위치 정보를 보내고, VT는 UI 요청과 응답을, TC는 작업 명령을, TECU는 속도·PTO 정보를 Working Set Master에 주며, Working Set Master는 Working Set Member를 내부 제어한다](/images/study-isobus/20-ecu-roles-dark.png)

그림의 화살표는 주로 오가는 정보다. 정보가 WSM으로 모인다는 점을 보면 된다. VT, TC, TECU는 각자 작업기의 대표인 WSM과 대화하고, WSM이 작업기 안의 Member들에게 일을 나눠 준다.

### 각 ECU의 핵심 역할 요약

| ECU | 버스 소속 | 핵심 역할 |
|-----|------|-----------|
| VT (Virtual Terminal) | 작업기 버스 (캐빈 장착) | 작업기 화면 표시, 운전자 UI |
| TC (Task Controller) | 작업기 버스 (캐빈 장착) | 작업 계획·기록, 섹션 제어 |
| TECU (Tractor ECU) | 트랙터 버스 ↔ 작업기 버스 | 두 버스 연결(게이트웨이), 트랙터 상태 정보 제공 |
| GPS Receiver | 작업기 버스 | 위치 정보 제공 |
| AUX Input Device | 작업기 버스 | 추가 조작 입력 |
| Working Set Master | 작업기 버스 (작업기) | 작업기 대표, VT·TC와 통신 |
| Working Set Member | 작업기 버스 (작업기) | 작업기 내부 개별 제어 |

표에 나온 말을 풀어 둔다. 섹션 제어는 분무기 붐 같은 작업 폭을 여러 구간(섹션)으로 나눠, 이미 뿌린 곳이나 밭 밖에서는 그 구간만 끄는 기능이다. AUX Input Device는 조이스틱이나 버튼 패드 같은 보조 조작기다([40장](/study/isobus/40-vt-aux)). GPS 수신기의 위치 정보는 TC가 처방 맵과 섹션 제어에 쓴다.

### TECU 클래스

ISO 11783-9(TECU를 정하는 문서)는 TECU가 작업기 버스에 제공해야 하는 최소 메시지 집합을 <strong>클래스</strong>로 구분한다. 클래스 번호가 클수록 앞 클래스의 메시지를 모두 포함하고 더 많이 제공한다. 작업기는 연결된 트랙터의 클래스를 보고 무엇을 읽고 시킬 수 있는지 판단한다.

| 클래스 | 의미 |
|--------|------|
| Class 1 | 기본 측정값 제공 (속도, 히치 위치, PTO 회전수 등. 신규 설계에는 비권장) |
| Class 2 | 측정 기능 전체 제공 (Class 1 + 주행 거리·방향, 견인력, 조명, 밸브 유량) |
| Class 3 | 작업기 버스로부터의 제어 명령 수용 (히치·PTO·보조 밸브 명령) |

여기에 기능별 addendum(덧붙이는 문자)이 붙는다: <strong>N</strong>(항법/GPS), <strong>F</strong>(전방 히치·PTO), <strong>G</strong>(조향 제어), <strong>P</strong>(속도·주행 전략 명령), <strong>M</strong>(발진 명령). 발진 명령은 트랙터를 앞이나 뒤로 움직이기 시작하게 하는 명령이다. 예를 들어 class 3GP는 조향과 속도 제어를 모두 수용하는 트랙터다.

작업기가 트랙터의 히치·PTO·보조 밸브를 명령하려면 Class 3이 필요하지만, 자동 조향(G)과 속도 제어(P)는 기본 클래스와 무관하게 붙는 addendum이다(예: class 2G, class 2P). 클래스를 알리는 메시지와 각 명령의 바이트는 [22장](/study/isobus/22-tractor-ecu)과 [24장](/study/isobus/24-hitch-pto-valve-control)에서 본다.

<small>근거: ISO 11783-9 4.4.2.1~4.4.2.9</small>

## 4. 시동부터 정상 동작까지: 메시지 흐름

이 절은 시동을 건 뒤 통신이 자리 잡는 순서를 본다. 트랙터에 작업기를 연결하고 시동을 켠 후, ISOBUS 통신이 확립되기까지 일련의 단계가 순서대로 진행된다.

회의에 들어가는 순서와 비슷하다. 명찰을 달고(주소 클레임), 사회자가 자리에 있는지 확인하고(VT Status), 우리 팀이 누구누구인지 알리고(Working Set), 출석을 이어서 확인받으며(Working Set Maintenance), 발표 자료를 넘긴다(오브젝트 풀). 다만 회의와 달리 주소 클레임은 모든 ECU가 거의 동시에 한다.

![시동 뒤 메시지 흐름: 전원 ON 뒤 TECU, WSM, VT, TC가 각자 주소 클레임을 하고 약 250 ms 안에 주소가 확정된다. VT가 1초 주기로 VT Status를 브로드캐스트하고, WSM이 이를 확인한 뒤 Working Set Master(PGN 65037)와 Working Set Member(PGN 65036, 멤버 수-1개)를 브로드캐스트해 약 1 s 안에 Working Set 구성을 마친다. 이어서 WSM이 Working Set Maintenance를 1초 주기로 보내기 시작하고, 오브젝트 풀을 VT에 보낸 뒤 End of Object Pool과 그 응답을 주고받는다. TC에는 Device Descriptor를 보낸다. 정상 동작에서는 TECU가 속도·PTO·히치 정보를, TC가 섹션 제어 명령을 WSM에 보내고, WSM이 VT 화면을 업데이트한다](/images/study-isobus/20-startup-sequence-light.png)
![시동 뒤 메시지 흐름: 전원 ON 뒤 TECU, WSM, VT, TC가 각자 주소 클레임을 하고 약 250 ms 안에 주소가 확정된다. VT가 1초 주기로 VT Status를 브로드캐스트하고, WSM이 이를 확인한 뒤 Working Set Master(PGN 65037)와 Working Set Member(PGN 65036, 멤버 수-1개)를 브로드캐스트해 약 1 s 안에 Working Set 구성을 마친다. 이어서 WSM이 Working Set Maintenance를 1초 주기로 보내기 시작하고, 오브젝트 풀을 VT에 보낸 뒤 End of Object Pool과 그 응답을 주고받는다. TC에는 Device Descriptor를 보낸다. 정상 동작에서는 TECU가 속도·PTO·히치 정보를, TC가 섹션 제어 명령을 WSM에 보내고, WSM이 VT 화면을 업데이트한다](/images/study-isobus/20-startup-sequence-dark.png)

그림의 세로선 넷은 각 ECU이고, 위에서 아래로 시간이 흐른다. 가로 화살표가 메시지다. 띠로 표시한 칸은 그 시점에 끝나는 단계다. 각 단계의 의미는 다음과 같다.

1. <strong>주소 클레임</strong>: 모든 ECU가 네트워크에서 고유한 주소를 확보한다 (J1939 방식과 동일, [13장](/study/isobus/13-j1939-address-claim)). 그림의 약 250 ms는 주소를 클레임한 CF가 250 ms가 지나야 다른 메시지를 보낼 수 있다는 규칙에서 온 어림값이다.
2. <strong>Working Set 구성</strong>: WSM은 먼저 VT Status가 나타날 때까지 기다린다. VT Status는 VT가 1초 주기로 브로드캐스트하는 메시지다. 브로드캐스트는 받는 쪽을 정하지 않고 버스 전체에 보내는 것이다. 그래서 VT Status는 WSM의 요청에 대한 응답이 아니다. 그다음 작업기를 대표하는 WSM이 Working Set Master 메시지(PGN 65037)로 멤버 수를, Working Set Member 메시지(PGN 65036)로 각 멤버의 NAME을 브로드캐스트한다. 멤버 수에는 WSM 자신이 들어가므로 Member 메시지는 멤버 수보다 하나 적게 나간다. VT·TC 같은 서비스 제공자가 이를 수신해 Working Set을 인식한다([26장](/study/isobus/26-isobus-network-mgmt)).
3. <strong>VT 연결</strong>: Working Set Master·Member 메시지로 자신을 알린 뒤, WSM은 Working Set Maintenance를 1초 주기로 보내기 시작한다. 첫 메시지에만 initiating(새로 시작한다는 표시)을 단다. VT는 이 주기 메시지로 작업기가 아직 연결되어 있는지 확인한다([31장](/study/isobus/31-vt-connection)).
4. <strong>오브젝트 풀 전송</strong>: 작업기 UI 화면 데이터를 VT에 업로드한다. 풀은 크기에 따라 TP나 ETP로 나눠 보내며, 전송 세션이 끝나면 VT가 다 받았음을 확인해 준다. 이어서 WSM이 End of Object Pool 메시지를 보내면, VT는 풀을 해석한 뒤 End of Object Pool 응답을 돌려준다([32장](/study/isobus/32-vt-object-pool-basics)).
5. <strong>Device Descriptor 전송</strong>: 작업기의 기능 구조를 TC에 알린다. 이 장치 설명서를 DDOP(Device Descriptor Object Pool)라고 한다([48장](/study/isobus/48-ddop-basics)).
6. <strong>정상 동작</strong>: TECU 정보·TC 명령·VT 화면 업데이트가 주기적으로 이루어진다.

그림은 큰 흐름만 담았다. 실제 VT 연결에는 메모리 확인 같은 질의가 끼어들고, TC 연결에도 버전 확인 같은 단계가 더 있다. 세부 절차는 [31장](/study/isobus/31-vt-connection)과 [43장](/study/isobus/43-tc-connection)에서 본다.

<small>근거: ISO 11783-5 4.5.2, ISO 11783-6 4.6.6.2, 4.6.9, C.2.2, ISO 11783-7 B.23.2, B.23.3</small>

::: tip 핵심 정리
- ISOBUS 네트워크는 트랙터 버스와 작업기 버스로 분리되며, 두 버스는 TECU(게이트웨이 NIU)가 연결한다. 외부 작업기는 IBBC 9핀 커넥터로 작업기 버스에 접속하고, 각 세그먼트 양 끝단은 TBC(종단 바이어스 회로)로 종단한다.
- VT와 TC는 운전석에 달려 있어도 작업기 버스에 속한다. 두 버스를 나누는 목적은 트랙터 버스의 격리·보호다.
- IBBC는 CAN 신호선 한 쌍, 두 계열의 전원(PWR 최소 50 A, ECU_PWR 최소 15 A), TBC용 선을 함께 넘긴다. 전원 분배는 TECU가 책임진다.
- VT는 화면, TC는 작업 관리, TECU는 버스 연결과 트랙터 정보 제공, WSM은 작업기 대표 역할을 한다. 작업기가 트랙터를 명령하려면 TECU 클래스를 확인한다.
- 시동 후 주소 클레임 → VT Status 확인 → Working Set 구성 → Working Set Maintenance → 오브젝트 풀 전송 순으로 통신이 확립된다. 오브젝트 풀은 작업기 UI를 정의하는 데이터로, WSM이 VT에 전송하여 화면을 구성한다.
:::

::: details 확인 문제
1. (개념) VT는 트랙터 운전석에 달려 있다. 그런데 왜 트랙터 버스가 아니라 작업기 버스에 붙는가? 두 버스를 나누는 이유는 무엇인가?
2. (구분) IBBC와 TBC는 각각 무엇이고, 어디에 있는가?
3. (적용) 작업기의 유압 밸브와 작업기 ECU는 각각 IBBC의 어느 전원을 쓰는가? 각 전원이 12 V에서 내야 하는 최소 전류는 얼마인가?
4. (순서) 다음을 시동 뒤 일어나는 순서로 놓아라: Working Set Maintenance 송신 시작, 주소 클레임, 오브젝트 풀 전송, VT Status 확인, Working Set Master·Member 메시지. VT Status는 WSM의 요청에 대한 응답인가?
5. (판단) TECU가 자기를 class 2G라고 알린다. 작업기는 이 트랙터에 리어 히치 위치 명령을 보낼 수 있는가? 조향 명령은 어떤가?

**답 가이드**
1. VT는 작업기와 화면을 주고받는 장치라 작업기 버스에 붙는다. Part 1도 VT를 작업기 네트워크에 둔다. 두 버스를 나누는 이유는 트랙터 버스의 격리·보호다. TECU가 전기적 격리와 메시지 격리를 맡아, 외부 작업기의 전기적 문제나 과도한 트래픽이 트랙터 구동계 버스에 번지지 않게 한다.
2. IBBC는 트랙터와 작업기의 작업기 버스를 잇는 9핀 커넥터(플러그)로, 트랙터와 작업기의 연결 지점에 있다. TBC는 커넥터가 아니라 세그먼트 양 끝에 두는 능동 종단 회로로, CAN_H·CAN_L에 바이어스 전압과 공통 모드 임피던스 종단을 준다.
3. 유압 밸브 같은 액추에이터는 PWR(GND와 짝)을 쓰고, 12 V에서 최소 50 A를 낼 수 있어야 한다. 작업기 ECU는 ECU_PWR(ECU_GND와 짝)을 쓰고, 12 V에서 최소 15 A다.
4. 주소 클레임 → VT Status 확인 → Working Set Master·Member 메시지 → Working Set Maintenance 송신 시작 → 오브젝트 풀 전송 순서다. VT Status는 VT가 1초마다 스스로 브로드캐스트하는 메시지라 요청에 대한 응답이 아니다. WSM은 이 메시지가 나타날 때까지 기다린다.
5. 리어 히치 위치 명령은 Class 3이 있어야 받아들여지므로 class 2G 트랙터에는 보낼 수 없다. G(조향)는 기본 클래스와 무관하게 붙는 addendum이므로 조향 명령은 보낼 수 있다.
:::

## 다음 챕터

- 다음: [21장 네트워크 계층과 NIU: 버스와 버스를 잇는 장치](/study/isobus/21-niu-network-layer)
