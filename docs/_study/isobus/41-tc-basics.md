---
title: "Task Controller(TC) 기초"
description: "Task Controller가 작업 지시를 받아 작업기에 일을 시키고 한 일을 기록하는 방식과 Section Control, Rate Control, GPS 연동, 클라이언트 연결 절차를 익힌다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, TaskController, TC, PrecisionAgriculture, SectionControl, RateControl, GPS]
prev: /study/isobus/40-vt-aux
next: /study/isobus/42-tc-task
---

# Task Controller(TC) 기초

::: info 학습 목표
- TC가 농장 사무실(FMIS)과 작업기 사이에서 하는 일을 "지시 → 실행 → 기록" 순서로 설명할 수 있다.
- TC-Server와 TC-Client가 각각 어디에 있고 무엇을 주고받는지 구분할 수 있다.
- Section Control(겹쳐 뿌리지 않기)과 Rate Control(위치마다 양 바꾸기)의 차이를 예를 들어 설명할 수 있다.
- GPS 위치가 처방 맵의 목표값으로 바뀌어 작업기까지 전달되는 길을 따라갈 수 있다.
- TC 클라이언트가 전원을 켠 뒤 TC와 연결을 맺고, 유지하고, 끊는 순서를 말할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [18장 ISOBUS 개요](/study/isobus/18-isobus-overview), [26장 네트워크 관리와 Working Set](/study/isobus/26-isobus-network-mgmt), [29장 VT 기초](/study/isobus/29-vt-basics)
- 이 장에서 처음 나오는 말
  - TC(Task Controller): 작업 지시를 받아 작업기에 목표값을 보내고, 실제로 한 일을 기록하는 기능
  - FMIS(Farm Management Information System): 농장 사무실 컴퓨터에서 작업을 계획하고 기록을 모으는 소프트웨어
  - 처방 맵(Prescription Map): 밭의 위치마다 뿌릴 양을 적어 둔 지도
  - Setpoint(설정값): TC가 작업기에 "이만큼 해라"라고 보내는 목표값
  - 섹션(Section): 작업기 폭을 나눈 구획. 구획마다 따로 켜고 끌 수 있다
  - DDOP(Device Descriptor Object Pool): 작업기가 자기 구조와 다룰 수 있는 값을 TC에 알리는 설명서
:::

농장 사무실에서 "오늘은 3번 밭에 비료를 위치마다 이만큼씩 뿌려라"라는 작업 지시서를 내려보냈다고 하자. 누군가는 그 지시서를 받아 기계에 일을 시키고, 일이 끝나면 어디에 얼마나 뿌렸는지 일지를 써서 사무실로 돌려보내야 한다. ISOBUS에서 이 현장 감독 역할을 맡는 것이 Task Controller(TC)다. 이 장은 TC가 하는 일의 큰 그림을 먼저 보고, 겹쳐 뿌리지 않기와 위치마다 양 바꾸기, GPS 연동을 거쳐, 작업기가 TC와 연결을 맺는 순서까지 따라간다.

## 1. TC란 무엇인가: 작업기의 현장 감독

정밀 농업은 밭을 한 덩어리로 보지 않고, 위치마다 흙과 작물 상태에 맞춰 다르게 작업하는 농업이다. 운전하면서 손으로 살포량을 수시로 바꾸기는 어렵다. 그래서 이 일을 자동으로 하는 기능이 필요하고, 그 기능이 TC다.

<strong>Task Controller(TC)</strong>는 ISO 11783-10에 정의된 정밀 농업의 핵심 컴포넌트이다. ISO 11783-10은 TC와 농장 관리 정보 시스템 사이의 데이터 교환을 정하는 표준 문서다. 영문 제목은 <em>Task Controller and Management Information System Data Interchange</em>이고, 이 스터디에서는 줄여서 Part 10이라고도 부른다.

### 현장 감독 비유

TC가 하는 일은 현장 감독의 하루와 닮았다.

1. 농장 사무실(FMIS)이 작업 지시서를 내려보낸다. 지시서에는 어느 밭에서 무엇을 할지, 위치마다 얼마나 뿌릴지(처방 맵)가 들어 있다.
2. 현장 감독(TC)이 지시서를 읽고, 지금 위치에 맞는 목표값을 기계(작업기)에 알려 준다.
3. 기계는 목표값대로 일하고, 실제로 얼마나 했는지 감독에게 보고한다.
4. 감독은 보고를 모아 작업 일지(작업 로그)를 쓰고, 일이 끝나면 사무실로 올려 보낸다.

![TC의 역할: FMIS가 처방 맵(작업 지시서)을 TC로 보내고, TC는 작업기 ECU에 설정값을 보내며 측정값을 보고받고, 작업 결과를 작업 로그(As-Applied)로 기록해 다시 FMIS로 올린다. 각 상자 아래에 농장 사무실, 현장 감독, 일하는 기계, 작업 일지라는 비유가 붙어 있다](/images/study-isobus/41-tc-role-flow-light.png)
![TC의 역할: FMIS가 처방 맵(작업 지시서)을 TC로 보내고, TC는 작업기 ECU에 설정값을 보내며 측정값을 보고받고, 작업 결과를 작업 로그(As-Applied)로 기록해 다시 FMIS로 올린다. 각 상자 아래에 농장 사무실, 현장 감독, 일하는 기계, 작업 일지라는 비유가 붙어 있다](/images/study-isobus/41-tc-role-flow-dark.png)

비유가 맞지 않는 곳도 있다. 현장 감독은 사람이지만 TC는 트랙터 단말기 같은 장치 안에서 도는 소프트웨어 기능이다. 작업 지시서도 종이가 아니라 XML 파일 묶음이다(파일 모양은 [56장](/study/isobus/56-practice-isoxml)에서 본다). 그리고 TC와 작업기는 말 대신 CAN 버스 메시지로 대화한다.

### TC의 두 가지 핵심 기능

TC는 두 가지 핵심 기능을 수행한다.

- <strong>자동 제어</strong>: 작업 계획(처방 맵, Prescription Map)에 따라 작업기를 자동으로 제어한다. 밭의 위치별로 미리 지정된 살포량·파종량을 GPS 위치와 연동하여 자동으로 적용한다.
- <strong>작업 기록</strong>: 실제 작업 결과(As-Applied Data)를 수집하고 기록한다. 어느 위치에서 얼마나 살포했는지를 나중에 분석할 수 있도록 로그로 남긴다.

As-Applied는 "실제로 뿌려진 대로"라는 뜻이다. 계획(처방 맵)과 실제(As-Applied)를 나란히 두면 지시대로 일했는지 확인할 수 있다.

TC가 없던 시대에는 농민이 수동으로 살포량을 조절해야 했다. TC는 이 과정을 자동화하여 비료·농약 과용을 줄이고 생산성을 높인다.

## 2. TC의 역할: 지시에서 기록까지 네 단계

1절의 그림을 화살표 하나씩 다시 읽어 본다. 데이터가 어디서 와서 어디로 가는지 알면, 뒤에서 나올 메시지와 파일이 어느 단계의 것인지 바로 구분할 수 있다.

TC는 FMIS(Farm Management Information System, 농장관리시스템)와 작업기 사이를 연결하는 중간 다리이다. 여기서 작업기 쪽 상대는 작업기 ECU(Electronic Control Unit, 작업기 안의 제어 컴퓨터)이고, TC 입장에서는 이 ECU가 TC-Client(TC의 손님)다.

각 단계의 의미는 다음과 같다.

| 단계 | 방향 | 내용 |
|------|------|------|
| 처방 맵 수신 | FMIS → TC | 밭의 구획별 목표 살포량·파종량이 담긴 계획 파일 |
| Setpoint 전달 | TC → 작업기 | GPS 위치에 해당하는 목표 값을 작업기에 명령 |
| Measurement 수집 | 작업기 → TC | 실제 살포된 양, 속도 등 센서 측정값 보고 |
| 작업 로그 기록 | TC → 저장 | 위치·시간·실제값을 묶어 As-Applied 파일로 저장 |

- 첫 단계와 마지막 단계(FMIS와 TC 사이)는 파일이 오가는 단계다. 파일을 USB 메모리로 옮기든 무선으로 보내든 상관없다.
- 가운데 두 단계(TC와 작업기 사이)는 ISOBUS 버스 위에서 메시지가 오가는 단계다. Setpoint는 "이만큼 해라", Measurement(측정값)는 "실제로 이만큼 했다"에 해당한다.

정리하면 TC는 위로는 파일로 FMIS와, 아래로는 버스 메시지로 작업기와 이야기한다. 파일과 메시지 중 어디까지 표준이 정하는지는 [42장](/study/isobus/42-tc-task)에서 다룬다.

## 3. TC-Server와 TC-Client

TC 이야기에는 "서버"와 "클라이언트"라는 말이 계속 나온다. 누가 명령하고 누가 실행하는지 먼저 정해 두면 이후 메시지의 방향을 헷갈리지 않는다.

ISOBUS에서 TC는 역할에 따라 두 가지로 구분된다.

| 구분 | 위치 | 역할 |
|------|------|------|
| **TC-Server** | 트랙터(또는 별도 단말기) | 처방 맵을 읽고 TC-Client에 명령을 내림 |
| **TC-Client** | 작업기 ECU | 명령을 받아 실제 작업을 수행하고 결과를 보고 |

1절의 비유로 말하면 TC-Server가 현장 감독이고, TC-Client는 감독의 지시대로 일하고 "이만큼 했다"고 보고하는 기계다. 이 스터디에서 그냥 "TC"라고 하면 보통 TC-Server를 뜻하고, TC-Client는 줄여서 "클라이언트"라고 부른다.

![TC-Server와 TC-Client: 트랙터 안의 GNSS 수신기가 GPS 위치를 TC-Server에 주고, TC-Server는 작업기 안의 TC-Client에 Value Command(Setpoint)를 보낸다. TC-Client는 Process Data Value(Measurement)를 돌려보내고, 유량 센서 값을 받아 밸브와 액추에이터를 움직인다](/images/study-isobus/41-tc-server-client-light.png)
![TC-Server와 TC-Client: 트랙터 안의 GNSS 수신기가 GPS 위치를 TC-Server에 주고, TC-Server는 작업기 안의 TC-Client에 Value Command(Setpoint)를 보낸다. TC-Client는 Process Data Value(Measurement)를 돌려보내고, 유량 센서 값을 받아 밸브와 액추에이터를 움직인다](/images/study-isobus/41-tc-server-client-dark.png)

- <strong>TC-Server</strong>는 처방 맵에서 현재 GPS 위치에 해당하는 값을 조회하고, 그 값을 TC-Client에 전달한다.
- <strong>TC-Client</strong>는 수신한 Setpoint에 맞게 밸브나 모터를 조절하고, 유량 센서 등으로 실제 값을 측정하여 TC-Server에 보고한다.

그림의 Value Command는 "이 값으로 맞춰라"라는 명령 메시지이고, Process Data Value는 "지금 값은 이렇다"라는 보고 메시지다. 둘 다 같은 메시지 형식(프로세스 데이터)을 쓰며, 자세한 바이트는 [45장](/study/isobus/45-tc-process-data-basics)에서 본다. GNSS(Global Navigation Satellite System)는 GPS를 포함한 위성 항법 시스템을 통틀어 부르는 말이다.

### TC 연결 관리

명령을 주고받으려면 먼저 TC와 클라이언트가 서로 살아 있는지 계속 확인해야 한다. 전화 통화 중에 상대가 아무 말이 없으면 "여보세요?"라고 묻는 것처럼, 둘은 정해진 주기로 짧은 메시지를 보내 연결을 확인한다. TC가 보내는 것이 Task Controller Status 메시지(줄여서 TC Status), 클라이언트가 보내는 것이 Client Task 메시지다. TC와 클라이언트의 연결은 이 Task Controller Status 메시지를 중심으로 유지되고, 규칙은 다음과 같다.

- 클라이언트는 address claim 완료 후 <strong>6초 대기</strong> → TC의 Status 메시지 수신 확인 → Working Set Master 메시지로 자신을 식별하며 연결 절차를 시작한다.
- TC는 Status 메시지를 <strong>2초 주기</strong>로 송신한다(상태 변화 시 즉시 송신해야 하며, 단 메시지 간 최소 200 ms).
- 타임아웃은 양방향 모두 <strong>6초</strong>다. 클라이언트가 TC Status를 6초간 못 받으면 TC의 비정상 종료로 간주하고, TC가 클라이언트의 Task 메시지를 6초간 못 받으면 클라이언트의 비정상 종료로 간주한다.
- 네트워크에는 TC가 여러 대 있을 수 있다. function instance 0인 TC가 <strong>primary TC</strong>이고, 오퍼레이터에게는 <strong>TC number</strong> = function instance + 1(1~32)로 표시한다. 클라이언트는 동시에 TC 1개·DL 1개에만 연결할 수 있다.

용어를 풀면 다음과 같다.

- address claim(주소 클레임): 버스에 처음 들어온 장치가 자기 주소를 정하고 알리는 절차다([13장](/study/isobus/13-j1939-address-claim)).
- Working Set Master: 여러 ECU가 한 기계를 이룰 때 그 묶음(Working Set)을 대표하는 ECU다([26장](/study/isobus/26-isobus-network-mgmt)).
- function instance: 같은 기능을 하는 장치가 여럿일 때 붙이는 0부터의 번호로, 장치 이름(NAME) 안에 들어 있다([12장](/study/isobus/12-j1939-address-name)).
- 오퍼레이터: 트랙터를 운전하며 단말기를 조작하는 사람이다.
- DL(Data Logger): 기록만 하는 TC의 사촌이다. 1개 TC와 1개 DL에 동시에 붙을 수 있다는 규칙과 함께 [44장](/study/isobus/44-tc-multi-dl-functionality)에서 다룬다.

연결 절차의 전체 순서는 아래 8절 "클라이언트 초기화와 연결 유지"에서 단계별로 본다.

## 4. Section Control과 Rate Control

TC의 두 가지 핵심 제어 기능이다. 하나는 "어디를 뿌리지 않을지", 다른 하나는 "어디에 얼마나 뿌릴지"를 정한다. 아래 그림의 왼쪽이 Section Control, 오른쪽이 Rate Control이다.

![Section Control과 Rate Control: 왼쪽은 9 m 폭 살포기의 세 구획 중 이미 살포된 구역 위에 있는 Section 3만 끄고 Section 1, 2는 켠 모습이다. 오른쪽은 처방 맵의 칸마다 목표량(100~250 L/ha)이 다르고, 트랙터가 있는 칸의 목표량이 Setpoint로 나가는 모습이다](/images/study-isobus/41-section-rate-control-light.png)
![Section Control과 Rate Control: 왼쪽은 9 m 폭 살포기의 세 구획 중 이미 살포된 구역 위에 있는 Section 3만 끄고 Section 1, 2는 켠 모습이다. 오른쪽은 처방 맵의 칸마다 목표량(100~250 L/ha)이 다르고, 트랙터가 있는 칸의 목표량이 Setpoint로 나가는 모습이다](/images/study-isobus/41-section-rate-control-dark.png)

### Section Control

작업기를 여러 <strong>구획(Section)</strong>으로 나누어 각 구획을 독립적으로 ON/OFF하는 기능이다. 이미 작업한 영역이나 작업이 필요 없는 영역의 구획을 자동으로 끈다.

<strong>목적</strong>: 중복 살포(Overlap) 방지 → 비료·농약·씨앗 절감

그림 왼쪽의 예를 단계별로 읽어 보자.

1. 살포기는 9 m 폭이고 3 m씩 3구획(Section 1, 2, 3)으로 나뉜다.
2. TC-Server는 GPS 위치로 각 구획이 지금 밭의 어디에 있는지 계산한다.
3. Section 3은 이미 살포된 구역 위에 있으므로 TC-Server가 "Section 3 OFF"를 보낸다.
4. Section 1, 2는 아직 뿌리지 않은 곳 위에 있으므로 "Section 1, 2 ON"을 보낸다.

결과적으로 같은 곳에 두 번 뿌리는 일이 없다. 밭 가장자리를 돌거나 비스듬히 지나갈 때 겹치는 면적이 특히 크게 줄어든다.

### Rate Control

GPS 위치에 따라 살포량(Rate)을 <strong>가변적으로</strong> 제어하는 기능이다. 처방 맵에 지정된 위치별 목표량을 실시간으로 반영한다.

<strong>목적</strong>: 토양 조건(양분 상태, 수분 함량)에 맞는 정밀 시비·시약

그림 오른쪽에서 트랙터가 있는 칸의 목표량은 200 L/ha다. L/ha는 1 ha(헥타르, 100 m × 100 m)에 몇 리터를 뿌리는지 나타내는 단위다. 트랙터가 250 L/ha 칸으로 넘어가면 TC는 새 목표량을 Setpoint로 보내고, 작업기는 밸브를 더 열어 양을 맞춘다.

| 구분 | 설명 | 제어 단위 |
|------|------|-----------|
| Section Control | 구획별 ON/OFF | 논리 값(켜짐/꺼짐) |
| Rate Control | 살포량 가변 조절 | 연속 수치(L/ha, kg/ha) |

두 기능은 함께 사용할 수 있다. 예를 들어, 밭의 경계에서 외부 구획은 OFF(Section Control)하면서 내부 구획의 살포량은 위치별로 조절(Rate Control)할 수 있다.

## 5. GPS 연동과 위치 기반 제어

Section Control과 Rate Control은 둘 다 "지금 어디에 있는가"를 알아야 한다. 이 절은 위치 정보가 어떤 메시지로 들어와 어떤 경로로 작업기 명령이 되는지 본다.

TC는 GPS 위치 데이터를 이용해 현재 위치에 해당하는 처방 맵의 값을 조회한다.

### 위치·속도 관련 메시지

ISOBUS는 위치 정보를 자체 정의하지 않고 <strong>IEC 61162-3(NMEA 2000)</strong>의 항법 위치 메시지를 그대로 사용한다. IEC 61162-3은 원래 선박 항법 장비끼리 통신하려고 만든 표준이고, 흔히 NMEA 2000이라고 부른다. 바퀴를 새로 발명하지 않고 이미 널리 쓰이는 위치 메시지를 빌려 온 것이다. 속도는 Part 7(ISO 11783-7, 트랙터와 작업기 사이의 메시지를 정하는 표준 문서)이 자체 정의한 트랙터 메시지로 전달된다.

아래 표의 PGN(Parameter Group Number)은 메시지 종류를 가리키는 번호다([9장](/study/isobus/09-j1939-message)). 괄호 안 `0xFE48`처럼 `0x`로 시작하는 값은 같은 번호를 16진수로 쓴 것이다.

| 메시지 | PGN | 주요 데이터 |
|--------|-----|-------------|
| GNSS Position Data (NMEA 2000) | **129029** | 위도(Latitude), 경도(Longitude), 고도, 측위 방법 |
| COG & SOG, Rapid Update (NMEA 2000) | **129026** | 대지 진행 방향(COG), 대지 속도(SOG) |
| Wheel-based Speed and Distance (Part 7) | **65096** (0xFE48) | 휠 기준 차속·거리 |
| Ground-based Speed and Distance (Part 7) | **65097** (0xFE49) | 대지 기준(레이더 등) 차속·거리 |

- COG(Course Over Ground)는 땅 위에서 실제로 움직이는 방향, SOG(Speed Over Ground)는 땅 위에서 실제로 움직이는 속도다.
- 휠 기준 속도는 바퀴 회전으로 잰 속도라 바퀴가 미끄러지면 실제보다 빠르게 나온다. 대지 기준 속도는 레이더처럼 땅을 직접 보고 잰 속도다.
- 두 속도 메시지의 바이트 구성은 [23장](/study/isobus/23-implement-messages-basics)에서 본다.

### 위치 기반 제어 흐름

![위치 기반 제어 흐름: GNSS 수신기의 위치 데이터가 GNSS Position Data(PGN 129029)로 TC-Server에 들어오고, TC-Server는 처방 맵에서 위치별 목표값을 조회해 해당 위치 목표값을 Value Command(Setpoint 전달)로 TC-Client(작업기 ECU)에 보낸다](/images/study-isobus/41-position-control-flow-light.png)
![위치 기반 제어 흐름: GNSS 수신기의 위치 데이터가 GNSS Position Data(PGN 129029)로 TC-Server에 들어오고, TC-Server는 처방 맵에서 위치별 목표값을 조회해 해당 위치 목표값을 Value Command(Setpoint 전달)로 TC-Client(작업기 ECU)에 보낸다](/images/study-isobus/41-position-control-flow-dark.png)

그림을 왼쪽부터 순서대로 읽으면 다음과 같다.

1. GNSS 수신기가 위치를 계산해 GNSS Position Data(PGN 129029) 메시지로 버스에 싣는다.
2. TC-Server가 그 위치가 처방 맵의 어느 구획에 속하는지 찾는다.
3. 그 구획의 목표값을 Value Command에 담아 TC-Client로 보낸다.
4. TC-Client가 목표값대로 작업기를 움직인다.

처방 맵은 격자(Grid) 또는 폴리곤(Polygon) 형태로 밭을 구획하고, 각 구획에 목표 값을 지정해 놓는다(둘 다 TreatmentZone을 참조한다). TC는 현재 GPS 위치가 어느 구획(TreatmentZone)에 속하는지 계산하고, 해당 구획의 목표 값을 TC-Client에 전달한다.

- 격자는 밭을 바둑판처럼 같은 크기의 칸으로 나눈 지도이고, 폴리곤은 꼭짓점을 이어 만든 자유로운 모양의 구역이다.
- TreatmentZone(처리 구역)은 "이 구역에는 이 목표값을 쓴다"는 목표값 묶음이다. 격자의 칸이나 폴리곤이 TreatmentZone을 가리키는 방식으로 목표값을 얻는다. 격자 파일은 [57장](/study/isobus/57-practice-binary-files)에서 직접 만들어 본다.

### NMEA와 ISOBUS

GPS 수신기는 NMEA 0183(시리얼) 또는 NMEA 2000(CAN 기반) 프로토콜로 데이터를 제공한다. NMEA 0183은 한 줄씩 글자로 보내는 오래된 직렬 통신 방식이고, NMEA 2000은 CAN 버스 위에서 도는 방식이다. Part 7이 항법 위치 메시지를 IEC 61162-3(NMEA 2000)에 위임하므로, NMEA 2000 항법 메시지는 ISOBUS 네트워크에서 그대로 사용된다. 이때 여러 데이터 프레임이 필요한 메시지(GNSS Position Data 등)는 ISO 11783-3의 transport protocol이 아니라 <strong>NMEA fast packet protocol</strong>을 사용해야 한다.

GNSS Position Data는 8바이트 프레임 하나에 다 들어가지 않는다. 긴 데이터를 여러 프레임으로 나눠 보내는 방법으로 ISOBUS는 보통 transport protocol(TP, [15장](/study/isobus/15-tp-bam-cmdt))을 쓰지만, 위치 메시지만은 NMEA 2000의 방식인 fast packet을 그대로 쓴다는 뜻이다. 위치 메시지를 읽는 프로그램은 두 방식을 모두 알아야 한다.

<small>근거: ISO 11783-7 B.5</small>

::: tip 중간 정리
- TC(Task Controller)는 ISO 11783-10에 정의된 정밀 농업 컴포넌트로, 처방 맵 기반 자동 제어와 작업 로그 기록을 담당한다.
- TC-Server는 트랙터 측에서 처방 맵을 읽고 명령하며, TC-Client는 작업기 ECU로 명령을 실행한다. 연결은 TC Status 메시지(2초 주기)로 유지되고 타임아웃은 양방향 6초다.
- Section Control은 구획별 ON/OFF로 중복 살포를 방지하고, Rate Control은 위치별 살포량을 가변 조절한다.
- GPS 위치(NMEA 2000 GNSS Position Data, PGN 129029)를 처방 맵과 대조하여 해당 위치의 Setpoint를 실시간으로 TC-Client에 전달한다.
:::

## 6. TC 기능성: 무엇을 할 수 있는지 나타내는 이름

TC 제품마다 할 수 있는 일이 다르다. 어떤 TC는 작업량 합계만 기록하고, 어떤 TC는 위치마다 양을 바꾸며 구획까지 끈다. 사는 사람과 만드는 사람이 같은 말로 이야기하려면 "어디까지 하는가"를 나누는 이름이 필요하다.

ISO 11783-10은 TC 기능을 네 가지 <strong>TC functionality</strong>(TC 기능성)로 구분한다. 제품이 어떤 기능성을 지원하는지에 따라 구현 요구사항이 달라진다.

| 기능성 | 의미 | 내용 |
|--------|------|------|
| **TC-BAS** | basic | 작업 총계(task total) 기록: 위치와 무관한 작업량 문서화 |
| **TC-GEO** | geo-based | 위치 기반 로깅과 (선택적으로) 처방 맵 기반 위치 제어 |
| **TC-SC** | section control | 섹션 자동 ON/OFF 제어 |
| **LOG** | data logger | 로깅 전용 기능(DL) |

- 작업 총계(task total)는 태스크 하나 동안 쌓인 합계다. 예를 들면 "이번 작업에서 뿌린 총량 1,200 L, 작업한 면적 8 ha" 같은 값이다.
- 로깅은 값을 시간이나 위치와 함께 기록해 두는 일이다.

운전면허에 종류가 있어 면허증만 보면 어떤 차를 몰 수 있는지 알 수 있듯이, 기능성 이름을 보면 그 제품이 TC 일 중 무엇을 할 수 있는지 알 수 있다. 다만 면허와 달리 한 제품이 여러 기능성을 함께 가질 수 있다.

TC 외의 기능(UT, AUX-N, TIM 등)까지 포함한 AEF 기능 단위 전체 구도는 [AEF 기능 카테고리](/study/isobus/appendix-aef-functionalities)에서 다룬다. AEF(Agricultural Industry Electronics Foundation)는 ISOBUS 제품의 호환성 시험을 운영하는 업계 단체다.

현행 2015년판(2nd edition)은 프로토콜 <strong>버전 4</strong>를 정의하며, 로깅만 수행하는 별도 CF인 <strong>Data Logger(DL)</strong>와 Peer Control 등이 버전 4에서 추가되었다. DL은 TC 기능의 부분집합으로 같은 연결 메커니즘을 쓰고, 클라이언트는 동시에 TC 1개와 DL 1개에 연결할 수 있다.

여기서 버전은 표준 문서의 초안과 판이 바뀔 때 함께 올라가는 TC 프로토콜 번호다(번호별 뜻은 [43장](/study/isobus/43-tc-connection)). CF(Control Function)는 버스 위에서 주소 하나를 가진 기능 단위를 말한다. 기능성별 Version 메시지 옵션 비트·게시 버전 번호와 TC-SC·LOG 요건은 [44장](/study/isobus/44-tc-multi-dl-functionality)에서 이어서 다룬다.

<small>근거: ISO 11783-10 Annex F.2</small>

## 7. TC-BAS·TC-GEO 최소 요건 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

기능성 이름을 내걸려면 최소한 무엇을 해야 하는지가 정해져 있다. 이 절은 TC-BAS와 TC-GEO의 최소 요건을 서버와 클라이언트로 나눠 본다.

같은 기능성이라도 <strong>TC 서버와 TC 클라이언트가 지는 부담은 다르다</strong>. TC 서버는 ISO 11783-11에 해당 기능성 관련으로 정의된 DDI를 전부 지원해야 하지만, TC 클라이언트는 자신이 실제로 다루는 부분집합만 제공하면 된다. 이 비대칭이 아래 요건 전체를 관통하는 원칙이다.

- DDI(Data Dictionary Identifier)는 "작업 폭", "총 살포량"처럼 값의 종류를 가리키는 번호다([45장](/study/isobus/45-tc-process-data-basics)).
- ISO 11783-11은 이 DDI 목록(데이터 사전)을 정하는 표준 문서다. 목록은 [DDI 부록](/study/isobus/appendix-ddi)에 있다.
- 서버는 어떤 작업기가 붙을지 모르니 다 받아 줄 준비를 해야 하고, 클라이언트는 자기가 아는 값만 말하면 된다. 그래서 부담이 비대칭이다.

| 기능성 | TC 서버 요건 | TC 클라이언트 요건 |
|--------|--------------|---------------------|
| **TC-BAS** | ISO 11783-11에 총계로 정의된 모든 DDI 지원 | 총계의 부분집합만 제공 가능하나 <strong>최소 DDI 119(total time)는 필수</strong>. DDOP에 rate DDI가 있으면 대응하는 total DDI도 필수 |
| **TC-GEO** | TC-BAS 서버 요건 + ISO 11783-11의 <strong>모든 DDI</strong> 지원 + <strong>Grid type 1·2 처리 필수(최소 350행×350열)</strong> | TC-BAS 클라이언트 요건 + TC-BAS 자체도 함께 지원 필수 |

표를 읽는 데 필요한 말을 풀면 다음과 같다.

- DDI 119(total time)는 실제로 작업한 시간의 합계(Effective Total Time)다([42장 9절](/study/isobus/42-tc-task)). TC-BAS 클라이언트라면 적어도 이 값 하나는 줄 수 있어야 한다.
- rate DDI는 "1 ha당 몇 L"처럼 비율로 나타낸 값이고, total DDI는 그 합계다. 비율을 보고하는 작업기라면 합계도 보고해야 한다.
- Grid type 1·2는 격자형 처방 맵을 담는 두 가지 바이너리 파일 형식이다([57장](/study/isobus/57-practice-binary-files)). TC-GEO 서버는 최소 350행×350열 크기의 격자를 처리해야 한다.

기능성마다 덧붙는 요건은 다음과 같다.

- <strong>TC-BAS</strong>: FMIS·TC·TC 클라이언트 모두 파일 세트(ISO11783_TaskData 등)와 Version 메시지에 TC 버전 <strong>3</strong>을 게시해야 한다. 파일 세트에 미지원 XML 요소(OperationTechnique, CodedCommentGroup 등)가 있어도 <strong>파일 세트 자체를 거부하면 안 되고</strong>, 해당 요소만 건너뛴 채 나머지 내용은 읽어야 한다.
- <strong>TC-GEO</strong>: 폴리곤 기반 처방 처리는 선택 기능이며, 지원할 경우 Control function functionalities 메시지에 명시해야 한다. TC 클라이언트는 TC가 Version 메시지로 보고하는 <strong>위치 기반 제어 채널 수 이하로</strong> 자신의 device descriptor가 보고하는 제어 채널 수를 제한해야 한다. 서버가 지원 못 하는 채널을 클라이언트가 먼저 내세우면 안 된다는 뜻이다.

위 두 항목의 낯선 말은 다음과 같다.

- 파일 세트: FMIS와 TC가 주고받는 XML 파일 묶음이다. 중심 파일은 `TASKDATA.XML`이고, 그 안의 맨 바깥 요소 이름이 ISO11783_TaskData다([56장](/study/isobus/56-practice-isoxml)).
- Version 메시지: TC와 클라이언트가 서로의 버전과 능력을 알려 주는 메시지다([43장](/study/isobus/43-tc-connection)).
- Control function functionalities 메시지: 장치가 지원하는 기능성 목록을 버스로 알리는 진단 메시지다([28장](/study/isobus/28-diagnostics-dm-fmi)).
- device descriptor: 작업기가 TC에 주는 자기 설명이다. 앞에서 본 DDOP와 같은 것을 가리킨다.
- 위치 기반 제어 채널: 처방 맵을 따라 따로 제어되는 양 하나다. 예를 들어 씨앗과 비료를 함께 넣는 파종기라면 씨앗 양과 비료 양이 각각 채널 하나다.

::: info 그리드는 서버의 일
Grid type 1·2 처리(350행×350열 이상)는 <strong>TC 서버</strong>의 요건이지 클라이언트의 요건이 아니다. TC 클라이언트는 자신의 device element·process data 구조와 채널 수 제한만 신경 쓰면 된다.
:::

연결 절차 자체는 아래 8절 "클라이언트 초기화와 연결 유지"를 참조한다.

기능성별 Version 메시지 옵션 비트·게시 버전 번호와 TC-SC·LOG 요건은 [44장](/study/isobus/44-tc-multi-dl-functionality)에서 이어서 다룬다.

<small>근거: ISO 11783-10 Annex F.2.1, F.2.2</small>

## 8. 클라이언트 초기화와 연결 유지

앞 절들이 TC의 역할과 제어 기능을 다뤘다면, 여기서는 <strong>TC-Client가 전원이 켜진 순간부터 실제로 명령을 주고받기까지 반드시 거쳐야 하는 절차</strong>를 순서대로 짚는다. 새로 온 작업자가 현장에 도착하면 출입 등록을 하고, 감독에게 인사하고, 자기 소개서를 내고 나서야 일을 받는 것과 같다.

::: warning 흔한 오해: "DDOP만 올리면 준비 끝"
TC-Client 구현을 "DDOP를 만들어 업로드하는 일"로 요약하는 경우가 많은데, 반만 맞다. DDOP 업로드와 활성화는 클라이언트 초기화 <strong>9단계 중 8~9번째</strong>일 뿐이다. 그 앞에 주소 확정 → TC 확인 → Working Set Master 선언 → Task 메시지 시작 → 버전 협상까지 7단계가 정해진 순서대로 먼저 끝나야 하고, 순서를 건너뛰면 TC가 DDOP 자체를 받아주지 않는다.
:::

### 클라이언트 초기화 9단계

ISO 11783-10이 정의하는 순서다. 표의 "왜 이 순서인가" 열이 각 단계의 이유다.

| 단계 | 동작 | 왜 이 순서인가 |
|---|---|---|
| 1 | address claim 완료 후 <strong>6초 대기</strong> | 네트워크의 다른 CF들도 각자 주소 클레임 중일 수 있다. 6초는 클레임 경합이 가라앉을 시간을 준다 |
| 2 | 선택한 TC의 <strong>Task Controller Status 메시지 수신 대기</strong> | 클라이언트가 먼저 말을 걸지 않는다. TC가 살아 있고 통신 준비가 됐다는 신호를 먼저 받아야 한다 |
| 3 | Working Set Master/Member 메시지(ISO 11783-7)로 자신을 <strong>Working Set Master로 식별</strong> | 버전 4부터 TC와의 통신은 Working Set Master CF로만 한정된다. 이 선언이 없으면 이후 어떤 메시지도 TC가 받아주지 않는다 |
| 4 | Client Task 메시지 송신 시작 | 이 시점부터 TC가 클라이언트의 생존을 감시한다(연결 유지 타이머 시작) |
| 5 | (버전 4 이상) Request Version으로 TC 버전 질의 → TC가 요구 버전·기능을 지원하지 않으면 <strong>자신의 기능을 TC가 지원하는 수준으로 제한</strong> | 기능을 낮추는 쪽은 항상 클라이언트다. 신형 클라이언트가 구형 TC에 맞춰야 통신이 성립한다 |
| 6 | (버전 4 이상) TC가 보내는 Request Version에 응답 | 버전 질의는 상호적이다. 어느 쪽이 먼저 묻든 응답 의무가 있다 |
| 7 | (선택) TC에 언어·형식 메시지 요청 | 필수는 아니지만 로캘 설정을 맞추려면 이 단계에서 처리한다 |
| 8 | TC에 <strong>자신의 DDOP가 이미 있는지 질의</strong> | 재접속 상황이면 다시 올릴 필요가 없다. 있는지부터 확인하는 게 먼저다 |
| 9 | 있으면 <strong>활성화</strong>, 없으면 TP/ETP(ISO 11783-3)로 <strong>DDOP 전송 후 활성화</strong> | DDOP는 Working Set Master 선언·버전 협상이 끝나고 상대가 누군지 확정된 뒤에야 의미가 있다 |

표에 나온 말 중 처음 보는 것을 풀면 다음과 같다.

- Request Version: 상대에게 "몇 버전이냐"고 묻는 메시지다. 답은 Version 메시지로 온다. 바이트는 [43장](/study/isobus/43-tc-connection)에서 본다.
- 로캘: 언어, 날짜 형식, 단위(미터법인지 야드파운드법인지) 같은 지역 설정이다.
- 활성화(activate): TC에 올라간 DDOP를 "이제부터 이 설명서를 쓴다"고 확정하는 일이다.
- TP/ETP: 8바이트보다 긴 데이터를 나눠 보내는 방법이다. DDOP는 보통 길어서 이 방법으로 보낸다([15장](/study/isobus/15-tp-bam-cmdt), [17장](/study/isobus/17-etp)).

### TC 초기화 5단계

클라이언트 혼자 순서를 지킨다고 되는 일이 아니다. TC 쪽도 정해진 순서로 움직여야 위 9단계가 맞물린다.

| 단계 | 동작 |
|---|---|
| 1 | ISO 11783-5에 따라 address claim 완료, global 주소(255)로 address claimed 요청도 송신 |
| 2 | address claim 완료 후 <strong>6초 대기</strong> |
| 3 | Task Controller Status 메시지 송신 시작 |
| 4 | 클라이언트의 DDOP 업로드·초기화 허용 |
| 5 | (버전 4 이상) 클라이언트가 TC 버전을 요청하면 TC도 클라이언트 버전을 요청 |

- ISO 11783-5는 주소 클레임과 장치 이름(NAME)을 정하는 표준 문서다.
- global 주소(255)는 "버스의 모두에게"를 뜻하는 특별한 목적지 주소다. 모두에게 "주소 클레임을 다시 알려 달라"고 요청하면, 이미 버스에 있던 장치들의 이름과 주소를 한 번에 모을 수 있다.

![TC 초기화 5단계와 클라이언트 초기화 9단계의 맞물림: TC가 주소 클레임과 6초 대기 뒤 TC Status를 보내기 시작하면 클라이언트의 2단계가 풀린다. 클라이언트가 5단계에서 Request Version을 보내면 TC가 5단계로 클라이언트 버전을 되묻고 클라이언트가 6단계에서 답한다. TC의 4단계(DDOP 업로드·초기화 허용)는 이후 계속 유지되며 클라이언트의 8~9단계를 받아 준다](/images/study-isobus/41-init-interlock-light.png)
![TC 초기화 5단계와 클라이언트 초기화 9단계의 맞물림: TC가 주소 클레임과 6초 대기 뒤 TC Status를 보내기 시작하면 클라이언트의 2단계가 풀린다. 클라이언트가 5단계에서 Request Version을 보내면 TC가 5단계로 클라이언트 버전을 되묻고 클라이언트가 6단계에서 답한다. TC의 4단계(DDOP 업로드·초기화 허용)는 이후 계속 유지되며 클라이언트의 8~9단계를 받아 준다](/images/study-isobus/41-init-interlock-dark.png)

두 순서를 맞대어 보면 왜 클라이언트가 "TC가 먼저 말할 때까지 기다린다"고 했는지 드러난다. TC의 3단계(Status 송신 시작)가 클라이언트의 2단계(Status 수신 대기)를 풀어주는 신호이고, TC의 4단계(DDOP 업로드 허용)가 클라이언트의 8~9단계를 받아주는 문이다. 버전 협상(클라이언트 5~6단계 / TC 5단계)도 서로가 서로를 향해 묻는 대칭 구조다. 즉 초기화는 클라이언트 혼자 진행하는 절차가 아니라, TC와 클라이언트가 각자의 5단계·9단계를 교대로 밟는 <strong>맞물린 절차</strong>다.

그림에서 TC의 4단계를 긴 막대로 그린 이유는 이 단계가 한 번 하고 끝나는 동작이 아니라 "이제부터 업로드를 받아 준다"는 허용 상태이기 때문이다. 메시지 하나하나의 순서는 [43장](/study/isobus/43-tc-connection)의 시퀀스 그림에서 더 자세히 본다.

### 연결 유지

연결이 성립한 뒤에는 3절의 "TC 연결 관리"에서 다룬 값들이 그대로 적용된다. TC Status는 2초 주기(상태 변화 시 즉시, 단 메시지 간 최소 200 ms), 타임아웃은 양방향 6초다. 여기에 클라이언트 쪽 값을 더하면 그림이 완성된다.

| 항목 | 값 |
|---|---|
| Task Controller Status 주기 | 2초(변화 시 즉시, 최소 200 ms 간격) |
| Client Task 메시지 주기 | 2초 |
| 타임아웃(양방향) | 6초 |

세 값은 이렇게 기억하면 쉽다. 2초마다 "살아 있다"를 말하고, 6초(주기 세 번만큼) 동안 소식이 없으면 끊긴 것으로 본다. 200 ms는 상태가 자주 바뀔 때 메시지가 버스를 도배하지 않도록 둔 최소 간격이다.

- 클라이언트가 TC Status를 6초간 못 받으면 <strong>TC의 비정상 종료</strong>로 간주하고 Client Task 송신을 중단한다. 이후 초기화 절차를 처음부터 다시 밟아야 재연결된다.
- TC가 Client Task를 6초간 못 받으면 <strong>클라이언트의 비정상 종료</strong>로 간주한다. 클라이언트가 address claim 후 6초를 기다린 뒤에야 Client Task를 보내는 이유가 여기 있다. 그 지연 자체가 TC 입장에서 "클라이언트가 막 재시작했다"는 신호로 읽힌다.

두 번째 항목을 풀어 보면 이렇다. 클라이언트가 재시작하면 주소 클레임과 6초 대기 때문에 Client Task가 적어도 6초 동안 끊긴다. 그러면 TC는 6초 타임아웃으로 "이전 연결은 끝났다"는 것을 알게 되고, 다음에 들어오는 Client Task를 새 연결로 받아들인다.

::: tip 권고가 아니라 필수값
200 ms·2초·6초는 참고 수치가 아니라 <strong>구현이 반드시 지켜야 하는 값</strong>이며, 정확도는 AEF(Agricultural Industry Electronics Foundation) 시험 요구사항의 대상이다. 임의로 늘리거나 줄이면 상호운용성 인증을 통과할 수 없다.
:::

### 재접속

작업 도중 클라이언트가 재시작하면 연결이 끊긴 시점의 상태로 되돌아가지 않는다. TC는 재접속한 클라이언트의 <strong>DDOP 업로드·활성화 요청을 다시 수락</strong>해야 하고(위 9단계를 처음부터 다시 밟는다), 그 클라이언트에 내리던 measurement 명령도 <strong>다시 내려야</strong> 한다. 즉 재접속은 "끊긴 지점에서 이어 붙이기"가 아니라 초기화 시퀀스의 재실행이다.

measurement 명령은 TC가 클라이언트에게 "이 값을 이런 조건으로 계속 보고하라"고 미리 걸어 두는 명령이다([46장](/study/isobus/46-tc-commands-pdack)). 재시작한 클라이언트는 이 약속을 잊었으므로 TC가 다시 걸어야 한다.

### 연결 종료

Key Switch가 off로 전환되면(ECU Power는 유지된 채) 정돈된 종료 절차가 시작된다. 클라이언트는 <strong>Connection Deactivate</strong> 명령을 보내 TC가 이를 비정상 종료로 오인하지 않게 하고, TC는 활성 DDOP를 가진 클라이언트의 마지막 전원 유지 요청 이후 최소 2초간 서비스를 유지해 수집 중이던 데이터가 정상적으로 마무리되게 한다. Key Switch가 다시 켜지면 양쪽 모두 위 초기화 절차를 재실행한다.

- Key Switch는 트랙터의 시동 키다. 키를 꺼도 ECU에 들어가는 전원(ECU Power)은 잠시 유지될 수 있어서, 그 사이에 정리 작업을 할 수 있다([22장](/study/isobus/22-tractor-ecu)).
- Connection Deactivate는 "의도적으로 연결을 끊는다"고 TC에 알리는 명령이다. 말없이 사라지면 TC는 6초 뒤 고장으로 판단하고 경고를 띄울 수 있다.

키를 끈 뒤의 절차를 TC와 클라이언트 양쪽에서 자세히 보는 일은 [43장](/study/isobus/43-tc-connection)에서 한다.

<small>근거: ISO 11783-10 6.6.1~6.6.4</small>

::: tip 핵심 정리
- TC는 농장 사무실(FMIS)의 작업 지시와 처방 맵을 받아 작업기에 목표값(Setpoint)을 보내고, 실제로 한 일(As-Applied)을 기록해 돌려주는 현장 감독이다. ISO 11783-10이 정한다.
- TC-Server는 트랙터 쪽에서 처방 맵을 읽고 명령하며, TC-Client(작업기 ECU)는 명령을 실행하고 측정값을 보고한다.
- Section Control은 구획별 ON/OFF로 겹쳐 뿌리기를 막고, Rate Control은 위치마다 뿌리는 양을 바꾼다. 둘 다 GPS 위치(PGN 129029)를 처방 맵과 맞춰 본다.
- TC 기능성은 TC-BAS·TC-GEO·TC-SC·LOG 넷이고, 서버는 넓게 받아 주고 클라이언트는 자기가 아는 만큼만 제공한다.
- 클라이언트는 주소 클레임과 6초 대기 → TC Status 확인 → Working Set Master 선언 → Client Task 시작 → 버전 확인 → DDOP 순서로 연결한다. 양쪽은 2초 주기 메시지로 서로를 확인하고 6초 끊기면 비정상 종료로 본다.
:::

::: details 확인 문제
1. (개념) 처방 맵, Setpoint, As-Applied 데이터는 각각 누가 누구에게 주는가?
2. (개념) 9 m 폭을 3 m씩 3구획으로 나눈 살포기가 지나가는데, 오른쪽 구획 하나가 이미 뿌린 곳 위에 있다. 이 위치의 처방 맵 목표량은 200 L/ha다. Section Control과 Rate Control은 각각 무엇을 하는가?
3. (개념) 전원을 켠 클라이언트가 곧바로 DDOP부터 보내면 어떻게 되는가? 그 앞에 어떤 단계가 있어야 하는가?
4. (응용) 작업 중에 클라이언트가 TC Status를 6초 동안 받지 못했다. 클라이언트는 무엇을 멈추고, 다시 연결하려면 어떻게 해야 하는가? TC 쪽에서는 클라이언트가 재시작했다는 것을 무엇으로 알아채는가?

**답 가이드**
1. 처방 맵은 FMIS가 TC에 준다(파일). Setpoint는 TC가 작업기(TC-Client)에 보낸다(버스 메시지). As-Applied 데이터는 작업기의 측정값을 TC가 모아 기록한 것이고, TC가 FMIS로 올려 보낸다(파일).
2. Section Control은 이미 뿌린 곳 위에 있는 오른쪽 구획만 끄고(OFF) 나머지 두 구획은 켠다(ON). Rate Control은 켜진 구획이 200 L/ha를 뿌리도록 목표량을 Setpoint로 보낸다. 두 기능은 함께 쓸 수 있다.
3. TC가 받아 주지 않는다. DDOP 업로드와 활성화는 9단계 중 8~9번째다. 그 앞에 주소 클레임 후 6초 대기, TC Status 수신 대기, Working Set Master 선언, Client Task 송신 시작, (버전 4 이상) 버전 질의와 응답, (선택) 언어·형식 요청이 있어야 한다.
4. TC의 비정상 종료로 보고 Client Task 송신을 멈춘다. 다시 연결하려면 초기화 절차를 처음부터 다시 밟는다. TC 쪽에서는 클라이언트의 Client Task가 6초 끊기는 것으로 알아챈다. 클라이언트는 주소 클레임 후 6초를 기다린 뒤에야 Client Task를 보내므로, 재시작하면 반드시 이 끊김이 생긴다.
:::

## 다음 챕터

- 다음: [42장 태스크와 시간 기록](/study/isobus/42-tc-task)
