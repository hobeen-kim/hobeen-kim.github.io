---
title: "ISOBUS 개요"
description: "농업 기계 통신 표준 ISOBUS(ISO 11783)가 왜 생겼고, 어떤 문서들로 이뤄지며, J1939과 어떻게 이어지는지 큰 그림을 잡는다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, J1939, AEF, CAN]
prev: /study/isobus/17-etp
next: /study/isobus/19-isobus-part1-requirements
---

# ISOBUS 개요

::: info 학습 목표
- ISOBUS가 어떤 불편을 없애려고 생겼는지 농가의 예로 설명할 수 있다.
- "ISOBUS를 지킨다"는 말이 메시지 형식, 통신 절차, 커넥터까지 같은 규칙을 따른다는 뜻임을 예로 들 수 있다.
- ISO 11783의 14개 파트가 각각 무엇을 정하는지, AEF 인증이 무엇을 보장하는지 구분할 수 있다.
- J1939과 ISOBUS가 어느 계층을 함께 쓰고 어디서 갈라지는지 설명할 수 있다.
- ECU와 CF를 구분하고, ECU 하나에 주소와 NAME이 몇 개 필요한지 셀 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [8장 SAE J1939 입문](/study/isobus/08-j1939-intro), [9장 J1939 메시지 구조](/study/isobus/09-j1939-message), [13장 주소 클레임](/study/isobus/13-j1939-address-claim)
- 이 장에서 처음 나오는 말
  - 작업기: 트랙터에 달거나 끌고 다니며 일하는 기계. 파종기, 분무기, 비료 살포기 같은 것이다.
  - 상호운용성: 만든 회사가 달라도 서로 맞물려 동작하는 성질.
  - ECU: 전자 제어 장치. 케이스 하나에 담긴 작은 컴퓨터 한 대다.
  - CF: ECU 안에서 네트워크 주소 하나를 갖고 일하는 기능 단위.
  - VT: 트랙터 운전석의 공용 화면. 작업기가 보낸 화면을 대신 띄운다.
  - TC: 작업 계획대로 작업기에 지시하고 작업 기록을 남기는 장치.
:::

컴퓨터에 어느 회사 마우스를 꽂아도 바로 움직이는 것은 USB라는 공통 규칙 덕분이다. 농기계에서 그 역할을 하는 표준이 ISOBUS다. 트랙터와 작업기를 만든 회사가 달라도 케이블을 꽂으면 트랙터 화면에 작업기 화면이 뜨고, 작업기는 트랙터가 알려 주는 속도를 읽는다. 이 장은 ISOBUS가 왜 생겼고, 어떤 문서들로 이뤄지며, 앞에서 배운 J1939과 어떻게 이어지는지 큰 그림을 잡는다.

## 1. 한 농가의 이야기: 꽂으면 동작해야 한다

이 절은 ISOBUS가 풀려는 문제를 농민의 눈으로 본다. 기술 용어 없이 이야기로 시작한다.

김 씨는 A사 트랙터로 농사를 짓는다. 올봄 파종기를 바꾸려고 보니 B사 파종기가 값도 성능도 마음에 들었다. ISOBUS가 없던 시절이라면 이 선택에는 대가가 따랐다.

1. 트랙터와 파종기가 서로의 말을 알아듣지 못한다. 커넥터 모양이 맞아도 데이터를 주고받는 규칙(프로토콜)이 회사마다 달랐기 때문이다.
2. 파종기를 조작하려면 B사 전용 모니터를 운전석에 하나 더 달아야 한다. 작업기를 바꿀 때마다 운전석의 모니터가 늘어난다.
3. 결국 김 씨는 같은 회사의 트랙터와 작업기만 사는 쪽을 택하게 된다. 고를 수 있는 장비가 크게 줄어든다.

ISOBUS가 있으면 이야기가 달라진다. 트랙터와 파종기가 둘 다 ISOBUS를 지키면, 김 씨는 파종기 케이블을 트랙터 뒤 커넥터에 꽂기만 하면 된다. 트랙터 운전석 화면에 B사 파종기의 조작 화면이 뜨고, 파종기는 트랙터가 알려 주는 주행 속도를 읽어 작업에 쓴다.

![ISOBUS 이전과 이후: 이전에는 같은 자체 프로토콜을 쓰는 트랙터와 작업기(Proto-A끼리, Proto-B끼리)만 연결되고, 이후에는 ISOBUS를 지키는 트랙터 A·B와 작업기 B·C가 서로 모두 연결된다](/images/study-isobus/18-isobus-before-after-light.png)
![ISOBUS 이전과 이후: 이전에는 같은 자체 프로토콜을 쓰는 트랙터와 작업기(Proto-A끼리, Proto-B끼리)만 연결되고, 이후에는 ISOBUS를 지키는 트랙터 A·B와 작업기 B·C가 서로 모두 연결된다](/images/study-isobus/18-isobus-before-after-dark.png)

그림 왼쪽이 ISOBUS 이전이다. 그 시절에는 제조사마다 독자적인 통신 프로토콜을 사용했다. 트랙터 A는 Proto-A, 작업기 B는 Proto-B를 쓰므로, 커넥터가 물리적으로 맞더라도 프로토콜이 달라서 데이터를 교환할 수 없었다. 같은 프로토콜을 쓰는 조합(A끼리, B끼리)만 동작했다. 결과적으로 농민은 같은 제조사의 트랙터와 작업기만 조합할 수 있었고, 장비 구매 선택지가 크게 제한되었다.

그림 오른쪽이 ISOBUS 이후다. ISOBUS는 통신 규격을 표준화하여 제조사 간 장벽을 없앴다. 트랙터와 작업기가 모두 ISOBUS 인증을 받았다면, 제조사에 관계없이 조합이 가능하다. 농민은 최적의 장비를 자유롭게 선택할 수 있다.

앞의 USB 비유는 "꽂으면 동작한다"는 점에서만 맞다. USB는 컴퓨터 한 대가 연결된 장치를 모두 관리하지만, ISOBUS에는 그런 주인이 없다. 장치 여러 대가 버스(여러 장치가 함께 매달려 쓰는 통신선, [2장](/study/isobus/02-can-intro)) 하나를 함께 쓰고, 각자 자기 주소를 정하고([13장](/study/isobus/13-j1939-address-claim)), 필요한 데이터를 직접 주고받는다.

## 2. ISOBUS란

이 절은 ISOBUS의 정식 이름과 목표를 정리한다.

<strong>ISOBUS</strong>는 농업·임업 기계를 위한 직렬 통신 표준이다. 직렬은 데이터를 전선 위로 한 비트씩 차례로 보내는 방식이다([1장](/study/isobus/01-communication-basics)). 공식 명칭은 다음과 같다.

> <strong>ISO 11783, Tractors and machinery for agriculture and forestry: Serial control and communications data network</strong>
>
> (농림업용 트랙터와 기계: 직렬 제어·통신 데이터 네트워크)

쉽게 말하면, 트랙터와 작업기(Implement) 사이에서 데이터를 주고받기 위한 규칙 모음이다. 속도, 엔진 RPM(분당 회전수), GPS 위치, 작업기 상태 같은 정보를 표준화된 방식으로 교환한다.

핵심 목표는 <strong>상호운용성(Interoperability)</strong>이다. 어떤 제조사의 트랙터와 어떤 제조사의 작업기를 조합해도 동일한 방식으로 통신할 수 있어야 한다.

ISOBUS와 ISO 11783은 같은 표준을 부르는 두 이름이다. 흔히 표준 문서를 가리킬 때는 ISO 11783, 그 표준을 따르는 네트워크와 장비를 가리킬 때는 ISOBUS라고 부른다.

## 3. "ISOBUS를 지킨다"는 것: 세 가지 사례

이 절은 "표준을 지킨다"는 말이 실제로 무엇을 맞춘다는 뜻인지 사례 세 개로 본다. 결론부터 말하면 메시지의 모양(어느 바이트에 무엇을 어떤 단위로 담는지), 주고받는 순서, 전기 규격까지 모두 같아야 한다.

"ISOBUS를 준수한다"는 것은 ISO 11783에 정의된 메시지 형식, 절차, 전기 규격을 그대로 따른다는 뜻이다.

### 사례 1: 트랙터 속도 브로드캐스트

TECU(Tractor ECU, 트랙터의 상태를 작업기 쪽에 알려 주는 트랙터 쪽 ECU)는 PGN 65097(Ground-Based Speed and Distance, 지면 기준 속도와 거리)을 100ms마다 브로드캐스트해야 한다. PGN은 메시지의 종류를 가리키는 번호이고([9장](/study/isobus/09-j1939-message)), 브로드캐스트는 받는 이를 정하지 않고 버스 전체에 흘려보내는 방식이다. 데이터 형식도 정해져 있다.

아래 그림은 이 메시지 한 프레임이다. 윗줄은 29비트 CAN ID를 우선순위(Priority), PGN, 보낸 이의 주소(SA)로 나눈 것이다. ID `0x0CFE490E`는 우선순위 3, PGN 65097(`0xFE49`), SA `0x0E`(=14)로 풀린다. 아랫줄은 8바이트 데이터이고, 바이트 번호는 1부터 센다.

![CAN ID 0x0CFE490E를 우선순위 3, PGN 65097(0xFE49), SA 0x0E로 나눈 칸과 8바이트 데이터: Byte 1~2의 A0 0F가 속도 값 0x0FA0이다](/images/study-isobus/12-speed-message-light.png)
![CAN ID 0x0CFE490E를 우선순위 3, PGN 65097(0xFE49), SA 0x0E로 나눈 칸과 8바이트 데이터: Byte 1~2의 A0 0F가 속도 값 0x0FA0이다](/images/study-isobus/12-speed-message-dark.png)

속도는 Byte 1~2 두 바이트에 담긴다. 그림의 값을 차례로 읽어 보자.

1. 받은 바이트는 Byte 1 = `A0`, Byte 2 = `0F`이다.
2. ISOBUS 메시지는 여러 바이트로 된 수를 리틀 엔디언으로 보낸다. 낮은 자리 바이트가 먼저 오므로, 두 바이트를 뒤집어 붙이면 `0x0FA0`이다.
3. `0x0FA0`은 10진수로 4000이다.
4. 이 값의 한 칸(분해능)은 0.001 m/s다. 그래서 속도는 4000 × 0.001 m/s = 4.0 m/s, 시속으로 약 14.4 km/h다.

한 줄로 줄이면 Byte 1-2 = 0x0FA0 = 4000 → 4000 × 0.001 m/s = 4.0 m/s (약 14.4 km/h)이다. 나머지 Byte 3~8에는 주행 거리와 진행 방향이 들어간다. 그 읽는 법은 [23장](/study/isobus/23-implement-messages-basics)에서 본다.

John Deere 트랙터든 Fendt 트랙터든 같은 PGN, 같은 바이트 위치, 같은 분해능(0.001 m/s)으로 전송한다. 덕분에 어떤 제조사의 작업기를 연결해도 속도를 정확히 읽을 수 있다. 만약 제조사가 자체 PGN을 쓰거나 분해능을 바꾸면, 다른 제조사 장비가 속도를 잘못 읽거나 아예 못 읽는다. 예를 들어 어떤 트랙터가 분해능을 0.01 m/s로 바꿔 같은 4.0 m/s를 400(`0x0190`)으로 보내면, 표준대로 읽는 작업기는 0.4 m/s로 잘못 읽는다(설명을 위한 가상의 예).

### 사례 2: VT 화면 표시

ISOBUS 작업기는 자기 화면 대신 트랙터 운전석의 VT(Virtual Terminal, 여러 작업기가 함께 쓰는 화면 단말)를 빌려 쓴다. 작업기 ECU가 트랙터 디스플레이에 UI(사용자가 보고 조작하는 화면)를 표시하려면 오브젝트 풀(Object Pool)을 VT로 전송해야 한다. 오브젝트 풀은 버튼, 숫자 칸, 그림 같은 화면 부품과 그 배치를 적은 데이터 묶음이다. 웹 브라우저가 서버에서 받은 HTML로 화면을 그리듯, VT는 받은 오브젝트 풀로 화면을 그린다. 이 절차도 표준으로 정해져 있다.

![작업기 ECU와 VT 사이의 화면 연결 순서: 작업기 ECU의 주소 클레임(PGN 60928), VT의 VT Status 브로드캐스트, Get Memory 요청과 응답(VT 버전, 메모리 여유), 오브젝트 풀 전송(TP·ETP), End of Object Pool과 그 응답, VT의 화면 표시](/images/study-isobus/18-vt-pool-handshake-light.png)
![작업기 ECU와 VT 사이의 화면 연결 순서: 작업기 ECU의 주소 클레임(PGN 60928), VT의 VT Status 브로드캐스트, Get Memory 요청과 응답(VT 버전, 메모리 여유), 오브젝트 풀 전송(TP·ETP), End of Object Pool과 그 응답, VT의 화면 표시](/images/study-isobus/18-vt-pool-handshake-dark.png)

그림을 위에서부터 읽으면 다음과 같다.

1. 작업기 ECU가 주소 클레임(Address Claim, PGN 60928)으로 버스에서 쓸 주소를 정한다([13장](/study/isobus/13-j1939-address-claim)).
2. VT는 VT Status 메시지를 1초마다 버스 전체에 브로드캐스트한다. 작업기 ECU는 이 메시지를 보고 VT가 있음을 안다.
3. 작업기 ECU가 Get Memory 메시지로 풀을 담을 메모리가 있는지 묻는다. VT는 응답에 자기 버전과 메모리 여유를 담아 돌려준다.
4. 작업기 ECU가 오브젝트 풀을 보낸다. 풀은 8바이트보다 크므로 여러 프레임으로 나눠 보낸다. 1,785바이트까지는 TP, 그보다 크면 ETP를 쓴다([15장](/study/isobus/15-tp-bam-cmdt), [17장](/study/isobus/17-etp)).
5. 다 보내면 작업기 ECU가 End of Object Pool 메시지를 보낸다. VT는 풀을 해석한 뒤 End of Object Pool 응답을 돌려준다.
6. VT가 작업기 화면을 그린다.

어떤 제조사 조합이든 이 절차를 따르면 화면이 표시된다. Kverneland 파종기를 John Deere 트랙터에 꽂아도, Fendt 트랙터에 꽂아도 같은 절차로 화면이 표시된다. 반면 자체 프로토콜을 사용하면 같은 제조사 디스플레이에서만 동작한다.

실제 연결에는 작업기가 자기 구성원을 알리는 메시지와 1초마다 보내는 유지 메시지가 더 끼어든다. 전체 순서는 [20장](/study/isobus/20-isobus-network-topology)에서, 세부 규칙은 [31장](/study/isobus/31-vt-connection)에서 본다. 웹 비유와 다른 점도 있다. 작업기는 풀을 한 번 보낸 뒤에는 화면 전체를 다시 보내지 않고, 명령을 보내 필요한 값만 바꾼다([32장](/study/isobus/32-vt-object-pool-basics)).

### 사례 3: TC 가변 살포 제어

가변 살포는 밭의 구역마다 비료나 약을 다른 양으로 뿌리는 작업이다. 어느 구역에 얼마를 뿌릴지 적은 지도를 처방 맵이라고 한다. TC(Task Controller, 작업 계획대로 작업기에 지시하고 기록을 남기는 장치)는 처방 맵을 보고 지금 위치에 맞는 살포량을 작업기에 명령한다.

TC가 처방 맵 기반으로 구획별 살포량을 조절할 때도, DDOP와 Process Data 형식이 표준이다. 작업 파일 형식인 ISOXML도 표준이다.

- DDOP(Device Descriptor Object Pool): 작업기가 자기 구조(구간이 몇 개인지, 무엇을 재고 조절할 수 있는지)를 TC에 알리는 장치 설명서다([48장](/study/isobus/48-ddop-basics)).
- Process Data: TC와 작업기가 목표 살포량, 측정값 같은 값을 주고받는 메시지다([45장](/study/isobus/45-tc-process-data-basics)).
- ISOXML: 사무실 컴퓨터와 TC가 작업 계획과 기록을 주고받는 파일 형식이다([56장](/study/isobus/56-practice-isoxml)).

어떤 제조사의 TC 소프트웨어에서 만든 처방 맵이든, ISOXML 형식을 따르면 어떤 살포기에서든 가변 살포가 동작한다.

### 준수와 미준수 비교

세 사례에 주소 관리와 물리 계층을 더해 표로 모으면 다음과 같다. 어느 영역이든 자체 방식을 쓰면, 그 영역에서는 다른 회사 장비와 맞물리지 않는다.

| 영역 | 준수 | 미준수 |
|------|------|--------|
| 메시지 형식 | 정해진 PGN/SPN/분해능으로 전송 | 자체 형식 사용 |
| 주소 관리 | Address Claim 절차 수행 | 하드코딩된 주소 사용 |
| VT 화면 | Object Pool로 UI 전송 | 전용 디스플레이에만 표시 |
| TC 제어 | DDOP + Process Data 표준 명령 | 자체 제어 프로토콜 |
| 물리 계층 | 250 kbps, 9핀 브레이크어웨이 커넥터(IBBC) | 다른 속도, 다른 커넥터 |

표의 SPN은 메시지 안의 값 하나하나에 붙인 번호다([9장](/study/isobus/09-j1939-message)). "하드코딩된 주소"는 프로그램 안에 고정해 둔 주소다. 다른 장치와 주소가 겹쳐도 피할 방법이 없다. 주소 클레임은 이런 충돌을 정해진 절차로 풀어 준다. "9핀 브레이크어웨이 커넥터(IBBC)"는 작업기를 트랙터에 꽂는 커넥터로, [20장](/study/isobus/20-isobus-network-topology)에서 본다.

<small>근거: ISO 11783-7 B.2, A.5, ISO 11783-6 4.6.6.2, C.2.2, D.3, G.2</small>

## 4. ISO 11783은 14개 파트로 이뤄진다

이 절은 ISO 11783이라는 표준이 어떤 문서들로 나뉘는지 본다. 앞으로 "Part 6", "ISO 11783-10" 같은 말이 계속 나오는데, 이 표가 그 지도다.

ISO 11783은 14개의 파트(Part)로 구성된 표준이다. 파트는 따로 발행되는 문서 한 권이다. "ISO 11783-6"과 "Part 6"은 같은 문서(여섯 번째 파트)를 가리킨다.

| 파트 | 제목 | 주요 내용 |
|------|------|-----------|
| Part 1 | General | 표준의 범위, 용어 정의, 전체 구조 |
| Part 2 | Physical Layer | 전기적 특성, 케이블, 커넥터 (CAN 250kbps) |
| Part 3 | Data Link Layer | 프레임 형식, CAN 기반 데이터 링크 |
| Part 4 | Network Layer | 네트워크 상호연결 장치(NIU: 리피터·브리지·라우터·게이트웨이·TECU) |
| Part 5 | Network Management | 주소 클레임, CF(Control Function) 관리 |
| Part 6 | Virtual Terminal | 작업기 UI를 트랙터 화면에 표시 |
| Part 7 | Implement Messages | 작업기 기능 관련 PGN 정의 |
| Part 8 | Power Train Messages | 엔진·변속기 관련 PGN 정의 |
| Part 9 | Tractor ECU | 트랙터 정보(속도, PTO, 히치) 제공 ECU |
| Part 10 | Task Controller | 작업 계획·기록, 정밀 농업 |
| Part 11 | Mobile Data Element Dictionary | 데이터 사전(DDE/DDI 정의) |
| Part 12 | Diagnostics | 진단 메시지(DM), 고장 코드 |
| Part 13 | File Server | 파일 저장소 제공, 파일 접근 명령 |
| Part 14 | Sequence Control | 작업 순서 자동화 |

처음에는 네 묶음으로 나눠 보면 쉽다.

- 총론(Part 1): 용어와 전체 구조, 시리즈 공통 요구를 정한다([19장](/study/isobus/19-isobus-part1-requirements)).
- 통신의 바탕(Part 2~5): 전선과 커넥터, 프레임, 버스 잇기, 주소 관리다. 앞에서 배운 CAN과 J1939에 해당한다.
- 트랙터와 작업기 사이의 메시지(Part 7~9): 속도, 히치, PTO 같은 트랙터 정보와 명령이다.
- 서비스 기능(Part 6, 10~14): 화면(VT), 작업 관리(TC), 데이터 사전, 진단, 파일 서버, 작업 순서 자동화다.

표에 나온 말 몇 가지를 풀어 둔다. 히치는 작업기를 트랙터에 걸고 들어 올리는 장치이고, PTO(Power Take-Off)는 엔진의 회전력을 작업기로 넘겨 주는 회전축이다. NIU(Network Interconnection Unit)는 버스와 버스를 잇는 장치다. DDI(Data Dictionary Identifier)는 "살포량", "작업 폭"처럼 작업 데이터의 종류마다 붙인 번호이고, DDE는 그 번호가 가리키는 데이터 항목이다. 이 스터디가 가장 많이 다루는 파트는 Part 6(VT)과 Part 10(TC)이다.

## 5. J1939과 ISOBUS의 관계

이 절은 앞 장까지 배운 J1939이 ISOBUS 안에서 어디에 쓰이는지 본다. 결론부터 말하면 아래 세 계층(물리, 데이터 링크, 네트워크)은 J1939과 맞춰 두었고, 맨 위 응용 계층에 ISOBUS만의 기능이 올라간다.

ISOBUS는 SAE J1939을 기반으로 농업 기계에 맞게 <strong>확장</strong>한 표준이다. SAE J1939은 트럭, 대형 버스 같은 상용차를 위해 만든 CAN 기반 통신 표준이다([8장](/study/isobus/08-j1939-intro)). 계층은 통신이 하는 일을 층으로 나눠, 아래층이 위층을 받쳐 주게 만든 구조다. 프로토콜 계층 관점에서 살펴보면 다음과 같다.

![ISOBUS 계층 구조: 아래에서부터 물리 계층(ISO 11783-2, J1939-11, CAN 250 kbit/s, 능동 종단 TBC), 데이터 링크 계층(ISO 11783-3, J1939-21, 29비트 CAN ID와 PGN 체계, TP·ETP), 네트워크 계층(ISO 11783-4, J1939-31, NIU), 응용 계층(VT ISO 11783-6, TC ISO 11783-10, TECU ISO 11783-9, 진단 ISO 11783-12)이고, 아래 세 계층이 J1939과 맞춘 공통 기반, 응용 계층이 ISOBUS 고유 기능이다](/images/study-isobus/18-isobus-layer-stack-light.png)
![ISOBUS 계층 구조: 아래에서부터 물리 계층(ISO 11783-2, J1939-11, CAN 250 kbit/s, 능동 종단 TBC), 데이터 링크 계층(ISO 11783-3, J1939-21, 29비트 CAN ID와 PGN 체계, TP·ETP), 네트워크 계층(ISO 11783-4, J1939-31, NIU), 응용 계층(VT ISO 11783-6, TC ISO 11783-10, TECU ISO 11783-9, 진단 ISO 11783-12)이고, 아래 세 계층이 J1939과 맞춘 공통 기반, 응용 계층이 ISOBUS 고유 기능이다](/images/study-isobus/18-isobus-layer-stack-dark.png)

그림은 아래에서 위로 읽는다.

1. 물리 계층: 전선과 전압의 규칙이다. CAN 250 kbit/s로 비트를 실어 나르고, 버스 끝은 능동 종단(TBC)으로 맺는다.
2. 데이터 링크 계층: 프레임 모양의 규칙이다. 29비트 CAN ID와 PGN 체계, 긴 데이터를 나눠 보내는 TP·ETP가 여기 있다.
3. 네트워크 계층: 버스와 버스를 잇는 NIU(세그먼트 상호연결 장치)의 규칙이다.
4. 응용 계층: VT, TC, TECU, 진단처럼 농작업에 직접 쓰는 기능이다. 여기가 ISOBUS 고유 기능이다.

정리하면:
- <strong>물리·데이터링크·네트워크 계층</strong>: J1939과 조화(harmonized)된 공통 기반 사용
- <strong>응용 계층</strong>: VT, TC, TECU 등 ISOBUS 고유 기능이 추가됨

조화(harmonized)는 두 표준이 같은 내용을 쓰도록 함께 맞춰 두었다는 뜻이다. Part 1은 그 목적을 상용차용 J1939 규격을 만족하는 전자 장치를 최소한의 변경으로 농림업 장비에 쓰게 하려는 것이라고 밝힌다.

TP와 ETP가 어느 계층인지는 헷갈리기 쉽다. 여기서 TP(Transport Protocol, 최대 1785바이트)와 ETP(Extended Transport Protocol, 최대 약 117MB)는 <strong>데이터 링크 계층인 Part 3</strong>에 정의된 멀티 패킷 전송 기능이다. 멀티 패킷 전송은 8바이트보다 긴 데이터를 여러 프레임으로 나눠 보내는 방법이다([15장](/study/isobus/15-tp-bam-cmdt), [17장](/study/isobus/17-etp)).

네트워크 계층(Part 4)은 전송 프로토콜이 아니라 세그먼트 간 메시지를 중계하는 NIU(Network Interconnection Unit)를 다룬다. 세그먼트는 양 끝을 종단으로 맺은 버스 한 토막이다. 큰 메시지를 나누는 일을 OSI 모형에서는 4계층의 일로 보는데도 ISO 11783이 데이터 링크 문서에 둔 사정은 [19장](/study/isobus/19-isobus-part1-requirements)에서 본다.

J1939을 이해했다면 ISOBUS의 하위 계층은 이미 알고 있는 것과 다름없다. ISOBUS 학습은 응용 계층의 고유 기능에 집중한다.

<small>근거: ISO 11783-1 Introduction, ISO 11783-3 5.10.1, 5.11.1</small>

## 6. ISOBUS 생태계: AEF와 인증

이 절은 표준 문서 밖에서 상호운용성을 실제로 확인해 주는 단체와 인증 제도를 본다.

### AEF (Agricultural Industry Electronics Foundation)

AEF는 ISOBUS의 실질적 표준화를 이끄는 국제 단체이다. ISO 표준은 문서 수준의 규격이지만, AEF는 실제 장비 간 상호운용성을 보장하기 위한 활동을 한다. 같은 문서를 보고 만들어도 회사마다 구현 결과가 조금씩 다를 수 있으니, 실제 장비끼리 맞물리는지 시험하는 절차가 따로 있는 셈이다. 전기 제품의 인증 마크처럼, ISOBUS 인증 마크는 정해진 시험을 통과했다는 표시다.

- <strong>AEF Conformance Test</strong>(적합성 시험): 제조사가 장비를 ISOBUS 적합성 테스트에 제출
- <strong>ISOBUS 인증 마크</strong>: 테스트를 통과한 장비에 부여. 인증 마크가 있으면 상호운용성 보장
- <strong>AEF Database</strong>: 인증된 제품 목록 공개, 농민이 조합 가능한 장비 확인 가능

AEF는 인증을 장비 전체가 아니라 <strong>기능 단위</strong>로 부여한다. UT, AUX-N, TC-BAS/TC-GEO/TC-SC, TIM, ISB 같은 약어가 그 단위이며, 각 기능이 무엇이고 서로 어떤 관계인지는 [AEF 기능 카테고리](/study/isobus/appendix-aef-functionalities)에 정리했다. 대표적인 것만 풀면 다음과 같다.

| 약어 | 뜻 |
|---|---|
| UT | Universal Terminal. 작업기가 자기 조작 화면(오브젝트 풀)을 터미널에 올려 조작받는 기능이다. VT가 제공하는 화면 기능을 인증 단위로 부르는 이름이다 |
| AUX-N | 조이스틱, 버튼 패드 같은 보조 조작기를 작업기 기능에 할당해 쓰는 기능 |
| TC-BAS / TC-GEO / TC-SC | 작업 총계 기록 / 위치 기반 기록과 처방 맵 제어 / 붐 구간 자동 켜고 끄기 |
| TIM | Tractor Implement Management. 작업기가 트랙터의 속도, PTO, 유압 등을 제어하는 기능 |
| ISB | ISOBUS Shortcut Button. 버튼 하나로 모든 작업기 기능을 즉시 멈추게 하는 기능 |

### 주요 참여 제조사

John Deere, AGCO, CNH Industrial(케이스·뉴홀랜드), CLAAS, Fendt, Kverneland, Amazone, Horsch 등 전 세계 주요 농기계 제조사가 AEF 멤버로 참여하고 있다.

## 7. 꼭 구분할 용어: ECU, CF, node, Working Set

이 절은 ISO 11783 전체가 함께 쓰는 낱말 가운데 가장 자주 헷갈리는 묶음을 정리한다. 같은 말을 사람마다 다르게 쓰면 대화가 어긋나듯, 표준도 "ECU", "CF" 같은 말의 뜻을 먼저 못 박아 둔다. 그 일을 하는 문서가 ISO 11783-1이다.

ISO 11783-1:2017(이하 Part 1)은 시리즈 전체의 총론이다. 시리즈가 함께 쓰는 용어 71개를 정의하고, OSI 대응, 네트워크 구조, 전자 데이터베이스를 다룬다. 뒤의 셋은 [19장](/study/isobus/19-isobus-part1-requirements)에서 본다. 용어 전체 표는 [Part 1 부록](/study/isobus/appendix-iso-part01)에, 이 스터디 전체의 용어는 [용어 사전](/study/isobus/appendix-glossary)에 있다. 여기서는 구현하다 헷갈리기 쉬운 묶음만 짚는다.

### ECU와 CF는 다른 단위다

결론부터 말하면, 네트워크 주소와 NAME은 ECU가 아니라 CF마다 하나씩 붙는다. ECU(Electronic Control Unit)는 케이스 하나에 담긴 전자 장치이고, CF(Control Function)는 그 안에서 특정 일을 맡아 주소 하나로 통신하는 기능이다. NAME은 CF마다 붙는 64비트 신분증이다([12장](/study/isobus/12-j1939-address-name)).

건물과 입주 회사에 비유할 수 있다. ECU는 건물, CF는 그 건물에 입주한 회사다. 우편물이 건물이 아니라 회사 앞으로 오듯, 네트워크 주소도 CF마다 하나씩 붙는다. node는 건물이 도로(버스)에 닿는 출입구다. 다만 우편 주소와 달리 CF의 주소는 전원을 켤 때마다 주소 클레임으로 다시 정해질 수 있다([13장](/study/isobus/13-j1939-address-claim)).

![ECU, CF, node의 관계: ECU 6 하나에 VT(주소 38, NAME 1)와 관리 게이트웨이(주소 37, NAME 2) 두 CF가 들어 있고, 작업기 컨트롤러 ECU에는 CF가 하나 있으며, 두 ECU는 각각 node 하나로 버스에 닿는다](/images/study-isobus/18-ecu-cf-node-light.png)
![ECU, CF, node의 관계: ECU 6 하나에 VT(주소 38, NAME 1)와 관리 게이트웨이(주소 37, NAME 2) 두 CF가 들어 있고, 작업기 컨트롤러 ECU에는 CF가 하나 있으며, 두 ECU는 각각 node 하나로 버스에 닿는다](/images/study-isobus/18-ecu-cf-node-dark.png)

그림 왼쪽은 Part 1이 직접 드는 예다. VT와 관리 게이트웨이(농장 사무실 컴퓨터로 데이터를 넘기는 장치)를 한 ECU에 담으면, 그 ECU 안에 NAME과 주소가 둘씩 공존한다. [19장](/study/isobus/19-isobus-part1-requirements)의 토폴로지 그림에서 다시 본다.

### 장치와 기능의 단위

Part 1의 정의를 표로 모으면 다음과 같다. 마지막 열은 구현할 때 이 정의가 어디에 걸리는지다.

| 용어 | Part 1의 정의 요지 | 구현자가 볼 점 |
|---|---|---|
| ECU | 물리적으로 독립된 전자 장치. CF를 하나 이상 담는다. 예: 작업기 컨트롤러, NIU, 운전자 단말 | 하드웨어 단위 |
| CF | 장치 안에서 특정 기능을 수행하는 단위. 네트워크에서 <strong>유일한 주소 하나</strong>를 가진다 | 주소·NAME의 단위. ECU 하나에 CF가 여럿이면 주소도 NAME도 여럿 |
| node | ECU가 네트워크에 물리적으로 접속하는 지점 | 세그먼트당 노드 수 제한([19장](/study/isobus/19-isobus-part1-requirements))의 셈 단위 |
| device | 트랙터·트레일러·작업기 같은 기계 시스템, 또는 독립 센서 시스템 | |
| machine | 기계 동력을 쓰거나 가하며, 정해진 기능으로 특정한 일을 하는 device | |
| tractor | 연결된 시스템의 1차 동력원인 machine. 자주식 장비는 동력원을 내장한 것으로 본다 | |
| implement | 특정 작업을 하며 보통 트랙터에 붙는 device 또는 machine | |
| equipment | 특정 포장 작업을 하는 device 또는 machine. 트랙터일 수도, 트랙터에 붙은 작업기일 수도 있다 | |
| MICS | ISO 11783 네트워크로 묶여 그 네트워크를 쓰는 device들 | "ISOBUS 시스템 전체"를 가리키는 공식 용어 |
| working set / working-set master | 하나의 애플리케이션을 분산 처리하는 CF들과 그 통신 조정자. master의 SA가 working set을 식별하고, 다른 CF는 그 SA로 working set과 통신한다 | VT·TC는 master의 SA로 working set을 상대한다([26장](/study/isobus/26-isobus-network-mgmt)) |

표의 낱말 몇 개를 풀어 둔다.

- 자주식 장비: 콤바인처럼 스스로 움직이는 농기계다.
- 포장(圃場): 농작물을 기르는 밭이나 논이다.
- MICS: Mobile Implement Control System의 약자다.
- SA(Source Address): CF가 쓰는 1바이트 주소다.
- working set: 작업기 하나의 일을 나눠 맡는 CF 묶음이고, 그 대표가 working-set master다. 예를 들어 파종기 한 대가 대표 CF 하나와 파종 줄마다 하나씩인 CF로 이뤄지면, 이 CF들이 하나의 working set이다.

<small>근거: ISO 11783-1 Clause 3, 6.5, ISO 11783-7 B.23.1</small>

## 8. Part 1 용어 더 보기 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절은 뒤의 장에서 하나씩 다시 나오는 Part 1 용어를 미리 모아 둔다. 표는 사전처럼 필요할 때 찾아보면 된다.

### 기능성(functionality) 3단 구분

AEF 인증의 단위와 직결되는 용어다. 6절에서 AEF가 장비 전체가 아니라 기능 단위로 인증한다고 했다. 그 기능 단위를 표준에서는 functionality(기능성)라고 부른다.

| 용어 | 정의 요지 | Part 1의 예 |
|---|---|---|
| functionality | 시장의 최종 사용자에게 제공되는, 특정 기능(군)을 수행하는 MICS 구성 요소의 능력 | minimum control function, universal terminal(server), task controller basic(client), file server |
| functionality characteristic | ISO 11783 개정 때문에 생기는 CF functionality 능력의 차이 | VT Ver 2 vs Ver 3, TECU Class1 Ver 1 vs Ver 2 |
| functionality generation | CF의 functionality characteristic이 어느 수준(세대)인지의 표시 | |
| minimum control function | Part 3·5·12에 특정된 functionality | |

표를 읽는 데 필요한 풀이다. 최종 사용자는 장비를 사서 쓰는 농민이다. universal terminal(server)은 화면을 제공하는 쪽, task controller basic(client)은 그 서비스를 쓰는 쪽이라는 표시다. 같은 기능도 표준이 개정되면 할 수 있는 일이 달라진다. VT Ver 2와 Ver 3의 차이가 그런 예이고, 이 차이를 functionality characteristic이라고 부른다.

minimum control function은 Part 3(데이터 링크), Part 5(네트워크 관리), Part 12(진단)로 정의된다. 이 점은 구현 순서의 힌트로 읽을 수 있다. 어떤 CF든 이 세 파트를 먼저 갖춘 뒤에 VT·TC 같은 상위 functionality를 얹는다는 뜻이다(해석).

UT는 Part 6의 능력 중 보조 조작(auxiliary control)을 뺀 functionality다. 보조 조작은 조이스틱 같은 별도 조작기로 작업기 기능을 움직이는 것이고([40장](/study/isobus/40-vt-aux)), AUX-O(Type 1)와 AUX-N(Type 2)으로 따로 센다. 공용 보조 조작을 제공하는 auxiliary input unit은 독립 CF이고, ECU 안에 있을 수도 VT 위에 있을 수도 있다. 인증 단위 전체 지도는 [AEF 기능 카테고리 부록](/study/isobus/appendix-aef-functionalities)에 있다.

### 메시지 구조 용어

PGN·PDU의 비트 구조는 [9장](/study/isobus/09-j1939-message)에서, 다중 패킷 전송은 [15장](/study/isobus/15-tp-bam-cmdt)과 [17장](/study/isobus/17-etp)에서 다뤘다. Part 1의 정의 중 구현에 바로 걸리는 문장만 옮긴다.

표에 나오는 약어부터 짚는다. PG(Parameter Group)는 한 메시지에 함께 담기는 데이터 묶음이고, PGN은 그 묶음의 번호다. DP(Data Page), EDP(Extended Data Page), PF(PDU Format), PS(PDU Specific), GE(Group Extension)는 29비트 ID 안의 칸 이름이다. ACK와 NACK는 각각 "알았다", "못 하겠다"는 응답이다.

| 용어 | 정의 요지 |
|---|---|
| PG | 단일·다중 패킷 메시지 안 데이터의 식별 단위. SA에 의존하지 않으므로 어느 발신자든 어떤 PG든 보낼 수 있다. 데이터뿐 아니라 명령·요청·ACK·NACK도 PG다 |
| PGN | DP·EDP·PF·GE 필드를 3바이트(24비트)로 나타낸 번호 |
| EDP | DP와 짝을 이루는 1비트. <strong>모든 ISO 11783 메시지는 송신 때 EDP를 0으로 둔다</strong> |
| PDU1 / PDU2 | PDU1은 PS에 목적지 주소(특정 또는 global), PDU2는 PS에 group extension이 들어간다 |
| SPN | 19비트. PG 안의 개별 파라미터마다, 그리고 지금은 PG에 없지만 진단에 필요한 항목에도 부여된다 |
| message / packet | message는 같은 PGN의 정보를 나르는 CAN 데이터 프레임 1개 이상이고, packet은 다중 프레임 메시지의 프레임 하나다. 데이터가 프레임 하나에 다 들어가면 packet이 곧 message다 |
| multi-packet message | 한 PGN의 데이터를 보내는 데 프레임이 여러 개 필요한 메시지. 프레임마다 CAN ID는 같고 데이터만 다르다 |
| ETP | 데이터가 1786~117440512바이트인 PG의 전송 프로토콜. 상한은 Part 1 정의의 값이고, ETP를 직접 규정하는 Part 3는 (2²⁴ − 1)패킷 × 7바이트 = 117 440 505바이트로 계산한다 |
| NACK | 메시지를 이해하지 못했거나 요청된 동작을 할 수 없음을 알리는 응답 |

ETP 행의 두 상한은 7바이트 차이가 난다. Part 1의 117440512는 2²⁴ × 7이고, Part 3의 117 440 505는 패킷 번호로 쓸 수 있는 최대값 (2²⁴ − 1)에 7을 곱한 값이다. 실제 전송 한도는 Part 3의 값이다.

### 그 밖에 자주 나오는 용어

뒤의 장에서 계속 나오는 용어를 모았다. 표의 바이어스는 전압을 정해진 값 쪽으로 잡아 주는 것이고, 텔레메트리는 기계의 데이터를 원격으로 모아 보내는 시스템이며, GIS는 지도 정보 시스템이다.

| 용어 | 뜻 | 자세히 |
|---|---|---|
| TBC | 세그먼트 양 끝마다 필요한 회로. CAN_H·CAN_L에 바이어스 전압과 공통 모드 임피던스 종단을 준다 | [3장](/study/isobus/03-can-physical), [20장](/study/isobus/20-isobus-network-topology) |
| safe state | 제어 시스템이 전부 또는 일부 고장 나도 운전자·주변인의 위험이 허용 수준인 운전 모드 | [19장](/study/isobus/19-isobus-part1-requirements)의 safe mode와 이어진다 |
| data mask · alarm mask · soft key mask | VT 화면을 이루는 오브젝트. data mask는 VT의 예약 영역에 표시·조작 오브젝트를 담는 최상위 UI 오브젝트다 | [32장](/study/isobus/32-vt-object-pool-basics) |
| TC 계열 | TC는 MICS에서 process data를 보내고 받고 기록하는 CF다. TC-BAS는 지리 참조가 필요 없는 능력, TC-GEO는 지리 참조가 필요한 능력, TC-SC는 구간 제어(section control) 사양이다 | [41장](/study/isobus/41-tc-basics) |
| DL | TC의 process data 프로토콜로 데이터 로깅을 하는 CF. 텔레메트리 시스템의 일부일 수도 있고, device description·process data에 더해 브로드캐스트되거나 요청할 수 있는 다른 PG까지 모으는 별도 CF일 수도 있다(Part 10에 정의) | [44장](/study/isobus/44-tc-multi-dl-functionality) |
| DD · DDE · DDI | DDI는 DDE를 유일하게 식별하는 16비트 번호이고, process data 메시지에서 값이나 명령의 대상 DDE를 지정한다. 목록은 isobus.net에 있다 | [45장](/study/isobus/45-tc-process-data-basics), [DDI 부록](/study/isobus/appendix-ddi) |
| client · FS | client는 서버나 master의 서비스를 쓰는 CF다. FS는 파일 저장소와 파일 취급·접근 명령 집합을 제공하는 CF다 | [51장](/study/isobus/51-file-server-basics) |
| FMIS | 농민이나 작업 대행업자가 쓰는 농장 사무용 컴퓨터 시스템. 장부·급여, 기계·자재·인력 관리, 필지 관리, GIS, 의사결정 지원, 작업 관리 소프트웨어를 포함한다 | [19장](/study/isobus/19-isobus-part1-requirements) |

<small>근거: ISO 11783-1 Clause 3, ISO 11783-3 5.11.3</small>

## 9. 문자열 인코딩: WideChar와 WideString (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절은 VT 화면에 글자를 띄우거나 파일 서버에 파일 이름을 보낼 때 문자열을 바이트로 바꾸는 규칙을 본다. VT·FS 등이 문자열을 주고받을 때 쓰는 원시 타입이 WideChar와 WideString이다.

먼저 바탕이 되는 생각부터 짚는다. 컴퓨터는 글자를 번호로 저장한다. "A"는 65(`0x41`), "가"는 44032(`0xAC00`)처럼 세계의 글자마다 번호를 붙인 표가 Unicode다. U+AC00은 그 번호를 16진수로 적은 표기다. 이 번호를 바이트열로 적는 방법을 인코딩이라고 한다.

| 용어 | 정의 요지 |
|---|---|
| char | 크기 1바이트인 문자 하나. 주로 ISO/IEC 8859 문자에 쓴다(ISO/IEC 8859-1에서 `0x41`이 "A") |
| character | 알파벳 같은 문자 하나. 크기는 인코딩 방식에 따라 다르다 |
| WideChar | <strong>리틀 엔디언 2바이트</strong>로 인코딩한 문자 하나. `41 00`이 "A"다. WideChar 두 개를 묶어 16비트를 넘는 코드를 나타낼 수 있다 |
| WideString | WideChar 0개 이상으로 이뤄지고 <strong>항상 BOM `FEFF`가 앞에 붙는</strong> 문자열 |
| code plane | 문자 코드 65536개의 묶음. Unicode/ISO/IEC 10646은 0~16번, 17개 code plane으로 문자를 정리한다 |
| surrogate pair | 16비트 high + 16비트 low로 이뤄진 32비트 문자 코드. code plane 1~16 문자의 UTF-16 표현이다 |

표의 ISO/IEC 8859는 유럽 언어용 1바이트 문자표이고, BOM(Byte Order Mark)은 바이트 순서를 알리려고 문자열 맨 앞에 붙이는 표시 `FEFF`(=65279)다. UTF-16은 문자 하나를 16비트 단위로 적는 인코딩이다.

Part 1은 "ABC"를 예로 든다. 바이트열은 `FF FE 41 00 42 00 43 00`이고, 이 WideString의 Length(길이)는 8바이트이며 표시되는 문자 수는 3이다. 바이트를 차례로 읽으면 다음과 같다.

1. BOM `FEFF`를 리틀 엔디언으로 적으면 낮은 자리 `FF`가 먼저 와서 `FF FE`가 된다. 여기까지 2바이트다.
2. "A"(`0x0041`)는 `41 00`, "B"는 `42 00`, "C"는 `43 00`이다. 여기까지 6바이트다.
3. 합계는 8바이트이고, 화면에 보이는 문자는 3개다.

BOM `FEFF`가 리틀 엔디언이라 `FF FE`로 나가고, <strong>길이에는 BOM 2바이트가 들어가지만 문자 수에는 들어가지 않는다</strong>는 점이 구현 함정이다. 길이 필드를 "문자 수 × 2"로 계산하면 2바이트가 모자란다.

| 문자열 | WideString 바이트 | 바이트 수 | 표시 문자 수 |
|---|---|---|---|
| "ABC" | `FF FE 41 00 42 00 43 00` | 8 | 3 |
| "가" (U+AC00, code plane 0) | `FF FE 00 AC` | 4 | 1 |
| U+1F69C (code plane 1) | `FF FE 3D D8 9C DE` | 6 | 1 (WideChar 2개 = surrogate pair) |

"가"는 65535(`0xFFFF`) 이하인 code plane 0 안의 글자라서 WideChar 하나(`00 AC`)로 끝난다. U+1F69C(트랙터 그림 문자)는 65535를 넘으므로 WideChar 두 개를 묶은 surrogate pair(`D83D` + `DE9C`)가 필요하다. 각 WideChar가 리틀 엔디언으로 나가므로 바이트열은 `3D D8 9C DE`가 된다.

아래 파이썬 코드는 표의 세 줄을 직접 만들어 확인한다. `encode("utf-16-le")`가 리틀 엔디언 2바이트 인코딩이고, 그 앞에 BOM 바이트 `FF FE`를 붙인다.

::: details 파이썬으로 WideString 검산
```python
def widestring(text):
    return b"\xff\xfe" + text.encode("utf-16-le")   # BOM FEFF를 리틀 엔디언으로


def hx(bs):
    return " ".join(f"{b:02X}" for b in bs)


abc = widestring("ABC")
assert hx(abc) == "FF FE 41 00 42 00 43 00" and len(abc) == 8   # Part 1 3.69의 예
assert hx(widestring("가")) == "FF FE 00 AC"

plane1 = widestring("\U0001F69C")
assert hx(plane1) == "FF FE 3D D8 9C DE"                         # D83D DE9C = surrogate pair
assert len(plane1[2:]) // 2 == 2                                 # WideChar 2개
print("WideString 검산 통과")
```
:::

모든 단언이 통과하면 마지막 줄의 "WideString 검산 통과"가 출력된다. 마지막 단언은 BOM을 뺀 나머지 4바이트가 WideChar 2개라는 뜻이다.

<small>근거: ISO 11783-1 3.6~3.9, 3.57, 3.68, 3.69</small>

::: tip 핵심 정리
- ISOBUS(ISO 11783)는 트랙터와 작업기 사이 통신을 표준화한 농업 기계 전용 규격이다. 목표는 제조사가 달라도 꽂으면 동작하는 상호운용성이다.
- 표준을 지킨다는 것은 메시지 형식(PGN, 바이트 위치, 분해능), 절차(주소 클레임, 오브젝트 풀 전송), 물리 규격(250 kbit/s, IBBC)을 모두 같게 맞춘다는 뜻이다.
- ISO 11783은 14개 파트로 이뤄지며, 이 스터디에서 가장 비중이 큰 것은 Part 6(VT)과 Part 10(TC)이다.
- J1939을 기반으로 하되 아래 세 계층은 J1939과 맞춰 두었고, VT, TC, TECU 같은 응용 계층이 ISOBUS 고유 기능이다.
- AEF 적합성 인증을 통과한 장비끼리는 제조사에 관계없이 상호운용이 가능하다. 인증은 기능 단위로 받는다.
- ECU는 물리 장치, CF는 주소와 NAME을 하나씩 갖는 기능 단위다. ECU 하나에 CF가 여럿이면 주소와 NAME도 여럿이다.
:::

::: details 확인 문제
1. (개념) ISOBUS 이전에 A사 트랙터를 가진 농민이 B사 작업기를 사면 어떤 불편을 겪었나? ISOBUS는 이를 어떻게 풀었나?
2. (계산) 트랙터가 보낸 Ground-Based Speed and Distance(PGN 65097) 메시지의 Byte 1~2가 `E8 03`이다. 속도는 몇 m/s이고 시속 몇 km인가?
3. (구분) 물리 계층, 데이터 링크 계층, 네트워크 계층, 응용 계층 가운데 J1939과 맞춰 둔 공통 기반은 어느 것이고, ISOBUS 고유 기능이 올라가는 곳은 어디인가?
4. (구분형) VT와 관리 컴퓨터 게이트웨이가 한 ECU에 들어 있다. 이 ECU가 가져야 할 NAME과 주소는 각각 몇 개이고, 그 이유는 무엇인가?
5. (계산형, 심화) VT에 보낼 문자열 "AB가"를 WideString으로 인코딩한 바이트열과 그 Length(바이트 수)를 쓰라.

**답 가이드**
1. 회사마다 프로토콜이 달라 커넥터가 맞아도 데이터를 주고받지 못했다. 작업기 전용 모니터를 따로 달거나, 같은 회사 장비만 사야 했다. ISOBUS는 메시지 형식, 절차, 커넥터를 표준으로 정해, 인증받은 장비끼리는 제조사와 관계없이 연결되게 했다.
2. 리틀 엔디언이라 두 바이트를 뒤집으면 `0x03E8` = 1000이다. 1000 × 0.001 m/s = 1.0 m/s이고, 시속으로는 3.6 km/h다.
3. 물리, 데이터 링크, 네트워크 계층이 J1939과 맞춘 공통 기반이다. VT, TC, TECU, 진단이 있는 응용 계층이 ISOBUS 고유 기능이 올라가는 곳이다.
4. 둘씩이다. 통신하는 모든 CF에 NAME을 배정해야 하고(shall), ECU 하나가 CF 여럿을 수행하면 CF마다 주소가 필요하다. Part 1이 이 경우를 직접 예로 든다. [19장](/study/isobus/19-isobus-part1-requirements) 토폴로지 그림의 ECU 6(VT 38, 관리 게이트웨이 37)이 그 모습이다.
5. BOM `FF FE` + "A" `41 00` + "B" `42 00` + "가" `00 AC` = `FF FE 41 00 42 00 00 AC`. Length는 8바이트이고 표시 문자 수는 3이다.
:::

## 다음 챕터

- 다음: [19장 ISO 11783 Part 1: 네트워크 요구사항과 공통 서비스](/study/isobus/19-isobus-part1-requirements)
