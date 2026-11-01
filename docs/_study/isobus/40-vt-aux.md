---
title: "보조 입력(AUX): 조이스틱을 기능에 연결하기"
description: "조이스틱 같은 보조 입력 장치의 입력을 작업기 기능에 연결하는 AUX-N 할당 절차와 메시지, 할당이 저장되고 풀리는 조건, learn mode와 v6 잠금을 익힌다."
date: 2026-04-13
tags: [ISOBUS, VT, AUX, Auxiliary Control, Joystick, ISO-11783-6]
prev: /study/isobus/39-vt-alarm-activation
next: /study/isobus/41-tc-basics
---

# 보조 입력(AUX): 조이스틱을 기능에 연결하기

::: info 학습 목표
- 입력 유닛, 기능, 할당이 어떻게 이어지는지 그림 한 장으로 설명할 수 있다.
- AUX-O(Type 1)와 AUX-N(Type 2)의 차이와, AUX-N이 입력을 SA 대신 NAME으로 식별하는 이유를 말할 수 있다.
- 입력 타입, 기능 타입, Function attributes 비트를 보고 할당이 가능한지 판단할 수 있다.
- Preferred Assignment, VT 검증, Status Enable, Assignment로 이어지는 할당 절차를 따라가고, 할당이 풀리는 원인을 진단할 수 있다.
- learn mode와 v6 잠금에서 Status 메시지의 Operating State 비트를 해석할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [29장 VT 기초](/study/isobus/29-vt-basics)(AUX 소개), [12장 주소와 NAME](/study/isobus/12-j1939-address-name), [38장 매크로와 운전자 입력 처리](/study/isobus/38-vt-macro-input)
- 이 장에서 처음 나오는 말
  - AUX(Auxiliary control, 보조 입력): 조이스틱 버튼처럼 VT 화면 밖에 있는 조작구로 작업기 기능을 움직이는 방식.
  - 입력 유닛(Auxiliary Input unit): 조작구를 가진 장치(예: 트랙터의 조이스틱). 그 안의 버튼·레버 하나하나가 입력(Auxiliary Input)이다.
  - 기능(Auxiliary Function): 작업기가 조작구에 맡기고 싶은 동작(예: 붐 올리기). 기능을 가진 작업기를 기능 Working Set이라 부른다.
  - 할당(assignment): 어느 입력이 어느 기능을 움직일지 정한 연결.
  - 선호 할당(Preferred Assignment): 기능 Working Set이 저장해 두었다가 전원을 켤 때마다 VT에 요청하는 "원하는 할당".
  - learn mode: 운전자가 실제 조작구를 움직여서 입력을 지정하는 할당 방식.
:::

자동차 운전대의 버튼을 "다음 곡"이나 "전화 받기" 가운데 원하는 기능에 연결할 수 있다고 생각해 보자. ISOBUS의 보조 입력(AUX)이 그런 장치로, 트랙터 조이스틱의 버튼과 레버를 작업기의 기능에 연결해 운전자가 화면을 누르지 않고도 손에 익은 조작구로 작업기를 움직이게 한다. 이 장은 이 연결(할당)을 누가 정하고, 어떤 메시지로 맺고, 언제 풀리는지를 단계별로 보고, 구현자에게만 필요한 바이트 세부는 5절(심화)에 모았다.

## 1. AUX 한눈에 보기: 조이스틱 버튼을 작업기 기능에 연결하기

[29장](/study/isobus/29-vt-basics)은 AUX의 구성 요소(입력 유닛, 기능, 할당)와 Preferred Assignment의 큰 흐름을 짧게 봤다. 이 절은 등장하는 장치 셋과 그 사이를 오가는 메시지를 그림 한 장으로 먼저 정리한다. 나머지 절은 이 그림의 화살표를 하나씩 자세히 본다. AUX의 규칙은 VT 표준 문서 ISO 11783-6에 있고, 이 장에서는 줄여서 Part 6이라고 부른다.

![조이스틱(AUX 입력 유닛)의 입력 0x0005, 0x0006을 VT(function instance 0)의 할당 표가 작업기(기능 Working Set)의 기능 0x0101, 0x0102에 연결하는 그림: ① 작업기가 VT에 선호 할당 요청, ② VT가 조이스틱에 상태 메시지 켜기, ③ VT가 작업기에 할당 알림, ④ 조이스틱이 입력 값(Status)을 버스 전체에 보내고 할당받은 기능이 읽음](/images/study-isobus/40-aux-big-picture-light.png)
![조이스틱(AUX 입력 유닛)의 입력 0x0005, 0x0006을 VT(function instance 0)의 할당 표가 작업기(기능 Working Set)의 기능 0x0101, 0x0102에 연결하는 그림: ① 작업기가 VT에 선호 할당 요청, ② VT가 조이스틱에 상태 메시지 켜기, ③ VT가 작업기에 할당 알림, ④ 조이스틱이 입력 값(Status)을 버스 전체에 보내고 할당받은 기능이 읽음](/images/study-isobus/40-aux-big-picture-dark.png)

그림의 세 장치는 다음과 같다.

| 장치 | 하는 일 |
|---|---|
| AUX 입력 유닛(조이스틱) | 조작구마다 Auxiliary Input 오브젝트를 담은 오브젝트 풀을 VT에 올린다. 조작 값을 Status 메시지로 알린다 |
| VT(function instance 0) | 어느 입력을 어느 기능에 연결할지 정하고 검사한다. 운전자는 VT의 할당 화면에서 할당을 바꿀 수 있다 |
| 작업기(기능 Working Set) | 기능마다 Auxiliary Function 오브젝트를 담은 풀을 VT에 올린다. 선호 할당을 저장해 두었다가 요청한다 |

입력 유닛도 자기 오브젝트 풀을 VT에 올리고 Working Set Maintenance를 보내는 하나의 Working Set이다. 이 장에서는 기능을 가진 쪽과 구별하려고 입력 유닛이라고 부른다. function instance는 NAME 안에서 같은 기능을 가진 장치를 구별하는 번호다([12장](/study/isobus/12-j1939-address-name)). 트랙터에 VT가 여러 대 있으면 function instance가 0인 VT만 AUX 할당을 맡는다(4절).

그림의 화살표는 할당이 맺어지는 큰 순서다.

1. 작업기가 VT에 "입력 `0x0005`를 내 기능 `0x0101`에 연결하고 싶다"는 선호 할당을 요청한다(Preferred Assignment).
2. VT가 요청을 검사한 뒤, 조이스틱에 그 입력의 상태 메시지를 켜라고 알린다(Status Enable).
3. VT가 작업기에 할당이 맺어졌다고 알린다(Auxiliary Assignment).
4. 조이스틱이 입력 값을 Status 메시지로 버스 전체에 보내고, 할당받은 작업기가 자기 기능에 연결된 입력의 값만 골라 읽는다.

핵심은 VT가 할당을 정하고 알려 줄 뿐, 조작 값을 중계하지 않는다는 점이다. 값은 입력 유닛이 직접 버스에 보낸다. 자동차 버튼 비유와 다른 점도 있다. 연결을 정하는 곳이 버튼(입력 유닛)도 기능(작업기)도 아닌 제3자 VT라는 점, 그리고 조이스틱이나 작업기가 바뀌어도 연결을 다시 찾아 잇는 규칙(선호 할당)이 있다는 점이다.

<small>근거: ISO 11783-6 J.1~J.3, J.7</small>

## 2. AUX-O와 AUX-N: 두 방식의 차이

현장에서는 AUX-O(옛 방식)와 AUX-N(새 방식)이라는 이름을 쓴다. 이 절은 두 방식이 무엇이 다른지, 왜 새 방식이 입력을 NAME으로 식별하는지 본다. 결론부터 말하면 v3 이상 장치는 AUX-N만 쓰고, 이 장의 나머지도 AUX-N만 다룬다.

29장에서 쓴 AUX-O·AUX-N은 현장에서 쓰는 이름이고, Part 6에는 나오지 않는다. Part 6은 VT version 2 방식의 항목에 "Type 1", version 3 이상 방식에 "Type 2"를 붙여 구분한다. 두 방식은 프로토콜과 알고리즘이 호환되지 않는다.

표의 괄호 안 숫자는 오브젝트 종류 번호(type)이고, 백틱 안의 두 자리 16진수는 메시지의 Byte 1(VT function 코드)이다.

| 항목 | Type 1(AUX-O, v2) | Type 2(AUX-N, v3부터) |
|---|---|---|
| 오브젝트 | Auxiliary Function Type 1(29), Auxiliary Input Type 1(30) | Auxiliary Function Type 2(31), Auxiliary Input Type 2(32), Auxiliary Control Designator Type 2 Object Pointer(33) |
| 기능 타입 | 3가지: latching Boolean, analogue, non-latching Boolean | 15가지(0~14, 3절 표) |
| 입력 식별 | 입력 장치의 SA + Input number(0~250) | 입력 유닛의 64-bit NAME + Auxiliary Input Object ID |
| 할당 명령 | Auxiliary Assignment Type 1(`20`, 8바이트) | Auxiliary Assignment Type 2(`24`, 14바이트) |
| 상태 메시지 | Auxiliary Input Type 1 status(`21`): 1초 + 변경 시, 최대 초당 5회 | Auxiliary Input Type 2 Status(`26`): VT가 enable해야 송신, 1초 + 변경 즉시, 입력당 최대 20 Hz |
| 선호 할당 | 없음 | 기능 Working Set이 저장하고 Preferred Assignment(`22`)로 전달 |
| 입력 유닛 생존 감시 | AUX 전용 메시지 없음 | Auxiliary Input Type 2 Maintenance(`23`), 100 ms |
| 잠금(lock) | 없음 | v6: Status Byte 8의 Bit 2·3 |

v3 이상 VT는 Type 1 오브젝트를 파싱·검증은 하지만 할당에는 쓰지 않는다. v3 이상 Working Set은 타입 29·30을 쓰면 안 되고, v3 이상 VT는 Type 1 메시지를 보내지 않는다.

입력 식별을 SA에서 NAME으로 바꾼 이유는 단계별로 보면 이해하기 쉽다.

1. SA(Source Address, 장치의 버스 주소)는 전원을 켤 때마다 주소 클레임 결과에 따라 달라질 수 있다([13장](/study/isobus/13-j1939-address-claim)).
2. 선호 할당은 기능 Working Set이 저장했다가 다음 전원 사이클에 복원하는 정보다.
3. 저장해 둔 SA는 다음 전원 사이클에 다른 장치를 가리킬 수 있다. 그래서 바뀌지 않는 식별자가 필요하고, 그것이 장치마다 고유한 64비트 NAME([12장](/study/isobus/12-j1939-address-name))이다.

Part 6이 이 이유를 직접 적지는 않으므로 이것은 추론이다.

<small>근거: ISO 11783-6 J.1, J.4.1, J.7.2</small>

## 3. 연결할 수 있는 짝: 입력과 기능의 타입과 속성

아무 입력이나 아무 기능에 연결할 수는 없다. 켜고 끄기만 하는 스위치로 아날로그 레버가 할 일을 시킬 수는 없기 때문이다. 이 절은 VT가 할당을 허락하는 조건, 곧 타입과 Function attributes 속성을 본다.

### Function attributes 바이트

Auxiliary Function Type 2(31)와 Auxiliary Input Type 2(32)의 핵심은 Function attributes 한 바이트다. 이 속성의 AID(Attribute ID, 속성마다 붙은 번호)는 `[2]`처럼 대괄호에 싸여 있으므로 읽기 전용이다. Change Attribute로 바꿀 수 없다([37장](/study/isobus/37-vt-command-details)의 Change Attribute 설명 참고).

비트 번호는 0부터 세고 Bit 7이 최상위 비트다.

| 비트 | Auxiliary Function Type 2 | Auxiliary Input Type 2 |
|---|---|---|
| 0~4 | 기능 타입(아래 타입 표) | 입력 타입(아래 타입 표) |
| 5 | Critical Control: 1이면 critical 입력(ISO 15077)으로만 제어 가능 | Critical Control: 1이면 critical 기능도 제어 가능 |
| 6 | Assignment Restriction: 1이면 Preferred Assignment로 정한 할당만 허용(그래도 해제는 가능) | 예약(0) |
| 7 | Single-assignment: 1이면 같은 입력에 다른 기능과 함께 할당 불가 | Single-assignment: 1이면 기능 하나에만 할당 가능 |

critical은 안전에 중요한 조작이라는 뜻이다. ISO 15077은 농업용 트랙터와 자주식 기계의 조작 장치가 지켜야 할 조작력, 움직임, 위치를 정한 표준이고, 그 기준을 만족하는 입력만 critical 입력이 될 수 있다.

예를 들어 Function attributes `0x43`은 "타입 3 + Assignment Restriction"인 기능이고, `0x83`은 "타입 3 + Single-assignment"다. 2진수로 풀면 다음과 같다.

- `0x43` = `0100 0011`: 하위 5비트 `00011` = 타입 3, Bit 6 = 1(Assignment Restriction)
- `0x83` = `1000 0011`: 하위 5비트 `00011` = 타입 3, Bit 7 = 1(Single-assignment)

Assignment Restriction은 이전 판에서 "Assignment Lock"이라 불렀다. v6의 입력 잠금(lock)과는 다른 개념이다(8절).

### 기능 타입과 입력 타입

기능 타입과 입력 타입은 <strong>정확히 같아야</strong> 할당된다. 할당을 운전자가 했든 Working Set이 했든 VT가 이를 보장해야 한다. 타입별 Status 값의 뜻을 줄여 보면 아래 표와 같다. Value 1과 Value 2는 입력이 보내는 Status 메시지(6절)의 두 값 칸이다. 전체 정의는 [ISO 11783-6 정리 부록](/study/isobus/appendix-iso-part06)의 Auxiliary control 항목에 있다.

표의 래치(latching)는 놓아도 그 자리에 머무는 것, 모멘터리(momentary)는 놓으면 제자리로 돌아오는 것이다([38장](/study/isobus/38-vt-macro-input) 참고). 전이(transition)는 상태가 바뀌는 것, 예를 들어 Off에서 On으로 바뀌는 것이다.

| 타입 | 조작구 | Value 1 | Value 2 |
|---|---|---|---|
| 0 | 2단 래치 스위치(On/Off) | 0 Off, 1 On | Off→On 전이 수 |
| 1 | 위치 유지 아날로그 | 0~100 % | 예약 `FFFF` |
| 2 | 2단 모멘터리 스위치 | 0 Off, 1 Momentary, 2 held | Off→not Off 전이 수 |
| 3 | 중앙(50 %) 복귀 아날로그 | 0~100 % | 예약 `FFFF` |
| 4 | 0 % 복귀 아날로그 | 0~100 % | 예약 `FFFF` |
| 5 | 3단 래치(On/Off/On) | 0 중앙 Off, 1 앞·위·오른쪽, 4 뒤·아래·왼쪽 | Off→On 전이 수 |
| 6 | 3단 모멘터리(중앙 복귀) | 0 Off, 1·2 앞쪽 Momentary·held, 4·8 뒤쪽 Momentary·held | Off→not Off 전이 수 |
| 7, 8 | 3단, 한쪽 래치·한쪽 모멘터리 | 1·2·4·8 조합(래치 방향이 타입마다 다름) | 전이 수 |
| 9, 10 | 아날로그 + 양 끝 래치 | 0~100 %, `FB00` 앞쪽 래치, `FB01` 뒤쪽 래치 | 비래치→래치 전이 수 |
| 11 | 직교 3단 스위치 2개 | 비트쌍 4개(앞·뒤·오른쪽·왼쪽, 쌍마다 00 Off·01 On·10 held) | 전이 수 |
| 12, 13 | 직교 아날로그 2축(위치 유지 / 중앙 복귀) | 축 1 0~100 % | 축 2 0~100 % |
| 14 | 양방향 엔코더 | 현재 카운트(롤오버) | 회전당 카운트(고정) |
| 31 | (할당 제거 명령에 쓰는 값) | | |

전이 수(Number of Transitions)가 있는 이유는 상태 메시지가 확인응답 없이 브로드캐스트되기 때문이다. 입력이 전송 속도보다 빨리 바뀌거나 메시지가 유실되면 전이 하나를 놓칠 수 있다. 기능 Working Set은 전이 수의 증가폭으로 놓친 전이를 찾아낼 책임이 있다. 예를 들어 전이 수가 1이 아니라 2 이상 늘었으면, 그 사이에 받지 못한 전이가 있었다는 뜻이다.

기능을 제공하는 Working Set은 제공하는 기능 수만큼 입력 장치를 지원하는 것이 권고이고, 기능이 12개를 넘으면 최소 12개 입력 장치를 지원해야 한다.

<small>근거: ISO 11783-6 J.1, J.2, J.4.1, J.4.3, J.4.5, J.4.6</small>

## 4. 할당 절차를 단계별로 따라가기

이제 할당이 실제로 맺어지는 순서를 본다. 결론부터 말하면 순서는 "입력 유닛 준비, 기능 Working Set의 선호 할당 요청, VT 검증, 입력 쪽 Status Enable, 기능 쪽 Assignment, 상태 송신"이다. 각 메시지의 바이트는 5절(심화)에서 본다.

![AUX-N 할당 시퀀스: 입력 유닛이 Maintenance(Status=0)를 브로드캐스트하고 풀을 올린 뒤 Status=1 Ready로 바꾸면, 기능 WS가 Preferred Assignment를 보내고, VT가 할당 처리 후 입력 유닛에 Status Enable, 기능 WS에 Assignment Type 2를 보내 각각 응답을 받고, 입력 유닛이 Status를 브로드캐스트하며, 운전자가 해제하면 Assignment(NULL)와 Status Enable(disable)이 나가는 흐름](/images/study-isobus/17-aux-assignment-sequence-light.png)
![AUX-N 할당 시퀀스: 입력 유닛이 Maintenance(Status=0)를 브로드캐스트하고 풀을 올린 뒤 Status=1 Ready로 바꾸면, 기능 WS가 Preferred Assignment를 보내고, VT가 할당 처리 후 입력 유닛에 Status Enable, 기능 WS에 Assignment Type 2를 보내 각각 응답을 받고, 입력 유닛이 Status를 브로드캐스트하며, 운전자가 해제하면 Assignment(NULL)와 Status Enable(disable)이 나가는 흐름](/images/study-isobus/17-aux-assignment-sequence-dark.png)

그림은 조이스틱 하나와 작업기 하나로 할당이 만들어지고 해제되는 흐름이다. Part 6에 실린 할당 흐름 그림을 줄여 다시 그렸고, 그림의 WS는 Working Set의 줄임이다. 위에서 아래로 읽으면 다음과 같다.

1. 입력 유닛이 Maintenance(Status = 0, Initializing)를 100 ms마다 보내면서 자기 오브젝트 풀을 VT에 올린다.
2. 풀이 오류 없이 올라가면(End of Object Pool response) 입력 유닛은 Maintenance의 Status를 1(Ready)로 바꾼다.
3. 기능 Working Set이 Ready를 보고 Preferred Assignment command를 VT에 보내고, VT가 응답한다.
4. VT가 할당을 처리한다(충돌 검사).
5. VT가 입력 유닛에 Status Enable을 보내 그 입력의 상태 메시지를 켜고, 응답을 받는다.
6. VT가 기능 Working Set에 Auxiliary Assignment Type 2를 보내고, 1 s 안에 응답을 받는다.
7. 입력 유닛이 그 입력의 Status를 버스 전체에 보낸다. 기능 Working Set이 이 값을 읽어 기능을 움직인다.
8. 운전자가 할당을 해제하면 VT가 기능 Working Set에 Assignment(NULL = 할당 없음)를, 입력 유닛에 Status Enable(disable)을 보낸다. 입력 유닛은 그 입력의 Status 송신을 멈춘다.

### 할당은 VT 한 대만 한다

할당과 검증은 function instance 0인 VT만 한다. instance 0이 아닌 VT도 AUX 오브젝트가 든 풀을 받을 수 있지만, 파싱만 하고 할당에는 쓰지 않는다. 그 VT에서 운전자가 할당 화면을 열려고 하면 할 수 없다고 알려야 한다. 그래서 다른 VT에 화면을 띄우는 Working Set도, AUX를 쓰려면 Auxiliary Input·Function 오브젝트를 담은 풀을 instance 0 VT에 따로 올려야 할 수 있다. 두 VT를 쓰는 Working Set은 Working Set Maintenance를 두 VT 모두에 보낸다.

### Preferred Assignment: 기능 Working Set이 원하는 할당

Preferred Assignment command(`22`, v3부터)는 기능 Working Set이 "어느 입력을 어느 기능에 연결하고 싶은가"를 VT에 알리는 명령이다. 구현에서 지켜야 할 규칙은 다음과 같다.

- 이 명령은 그 Working Set의 <strong>할당 전체</strong>를 나타낸다. 명령에 없는 기능은 미할당이다. VT는 명령에 없는 기능을 "할당 제거" 명령으로 해석한다.
- 네트워크에 없는 입력 유닛을 참조하면 안 된다. 기능 Object ID는 메시지 안에 한 번씩만 나와야 하고, 이를 지키는 것은 Working Set 책임이다.
- 보낸 뒤에는 VT의 응답을 받기 전에 다른 명령을 보내지 않는다. 2 s 안에 응답이 없으면 재전송하고, 3회 실패하면 운전자에게 기능을 쓸 수 없다고 알린다.
- 풀을 로드한 뒤 <strong>한 번은 반드시</strong> 보내야 한다. VT는 이 명령을 받기 전까지 그 기능의 수동 할당도 허용하지 않기 때문이다. 저장된 선호 할당이 없을 때도 보낸다. 이때는 Byte 2(입력 유닛 수)를 0으로 보내는 것이 자연스럽다(추론). 이 명령을 빼먹은 기능 Working Set은 운전자가 할당 화면에서 아무리 시도해도 할당되지 않는다.
- 선호 입력 유닛을 찾았다면, 그 유닛의 Maintenance가 Status = Ready가 될 때까지 기다린 뒤 보낸다. 기다리지 않으면 응답에 Input Object ID 오류가 날 수 있다. 다른 선호 유닛을 찾으려고 더 기다려도 된다.
- 처음 보낸 뒤 다시 보내는 경우는 다음뿐이고, 조건마다 한 번만 보낸다. 선호 유닛이 새로 나타나거나 재초기화된 경우(Ready 대기 규칙 동일), 할당이 걸린 입력 유닛이 빠졌거나 다른 유닛으로 재구성할 때, 운전자가 Working Set 화면에서 다른 선호 할당 세트를 고른 경우(선택 사항), Working Set이 할당에 영향을 주도록 자기 풀을 고친 경우다.

선호 입력 유닛을 판단할 때는 Model Identification Code(입력 유닛 제조사가 정한 2바이트 모델 번호)와 NAME을 함께 본다. NAME에서는 Function Instance와 Manufacturer Code를 보고 Identity Number는 빼고 비교할 수 있다. 그래서 같은 제조사·같은 모델의 다른 조이스틱을 단 트랙터에 파종기를 옮겨 달아도 "기능적으로 동일한(Functionally Identical)" 유닛으로 받아들일 수 있다. NAME의 하위 21비트가 Identity Number이므로, 비교할 때 이 비트를 마스크(비교에서 빼려고 0으로 지움)하면 된다([12장](/study/isobus/12-j1939-address-name)).

VT는 이 명령을 받자마자 검증하고, 오류가 하나라도 있으면 <strong>명령 전체를 무시</strong>한다. 응답의 오류 비트는 5절에서 본다.

### VT의 할당 처리

VT(instance 0)는 다음 단계로 할당을 처리한다.

1. 입력을 제공하는 Working Set(입력 유닛)과 기능을 제공하는 Working Set(기능 Working Set)을 파악하고, 각 입력·기능의 타입과 designator를 확인한다.
2. Preferred Assignment로 시작된 처리라면, 명령에 있는 기능은 할당으로, 없는 기능은 할당 제거로 해석한다.
3. 선호 할당과 기존 할당을 함께 검사해 충돌을 찾는다(아래 표).
4. 충돌이 있는 할당은 기능 Working Set에 "할당 제거(NULL)"를 담은 Auxiliary Assignment Type 2를 보내고, 할당이 풀렸으니 할당 화면에서 다시 하라고 운전자에게 알린다.
5. 충돌이 없는 할당은 먼저 입력 유닛에 Status Enable을 보내 그 입력의 상태 메시지를 켠다. 그다음 기능 Working Set에 Auxiliary Assignment Type 2를 보낸다.
6. 할당이 없는 기능에는 할당 제거 명령을, 할당이 없는 입력에는 Status Enable(disable)을 보낸다.

1단계의 designator는 할당 화면 등에서 입력과 기능을 운전자에게 보여 주는 이름표(그림이나 글자)다.

| 충돌 조건 | 예 |
|---|---|
| (I) 기능 타입과 입력 타입이 다름 | 타입 3 기능을 타입 2 입력에 |
| (II) 기능의 Single-assignment = 1인데 그 입력이 여러 기능에 매핑됨 | |
| (III) 입력의 Single-assignment = 1인데 여러 기능에 매핑됨 | |
| (IV) 기능의 Assignment Restriction = 1인데 선호 할당이 아닌 입력에 매핑됨 | |
| (V) 입력의 Critical Control = 0인데 기능의 Critical Control = 1 | |
| (VI) 한 기능을 여러 입력에 할당하려 함 | |
| (VII) 할당된 입력·기능의 풀이 제거됨(의도적 삭제 또는 통신 상실) | |

할당과 충돌 검사의 순서는 VT 설계에 달렸다. Object ID 순서나 명령 안의 순서를 가정하면 안 된다.

### Auxiliary Assignment Type 2: 저장할지 말지 알려 주는 비트

VT는 할당 결과를 Auxiliary Assignment Type 2 command(`24`)로 기능 Working Set에 알린다. 이 명령에서 가장 중요한 것은 Preferred Assignment 비트(Byte 10의 Bit 7)다. 이 비트가 기능 Working Set에게 "이 할당을 새 선호 할당으로 저장하라(0)" 또는 "저장하지 말라(1)"를 알려 준다.

Preferred Assignment 비트는 <strong>운전자의 조작에서 비롯된 경우에만</strong> 0이다. 운전자가 할당 화면에서 입력을 고른 경우와, 운전자가 할당을 지운 경우다. Preferred Assignment 명령에서 비롯된 할당, 오류 상황(입력 유닛의 unexpected shutdown, 통신 오류)에 따른 제거 등 나머지는 모두 1이다. "아무것도 할당하지 않음"도 운전자의 선택이면 새 선호 할당으로 저장된다는 뜻이다.

| 할당이 바뀐 이유 | Bit 7 | 기능 Working Set이 할 일 |
|---|---|---|
| 운전자가 할당 화면에서 입력을 고름 | 0 | 새 선호 할당으로 저장 |
| 운전자가 할당을 지움 | 0 | "할당 없음"을 새 선호 할당으로 저장 |
| Preferred Assignment 명령에서 비롯됨 | 1 | 저장하지 않음 |
| 오류 상황에 따른 제거(입력 유닛 사라짐, 통신 오류) | 1 | 저장하지 않음 |

기능 Working Set은 이 명령에 <strong>1 s 안에</strong> 응답해야 한다. 응답 형식, 재전송 규칙, 할당을 거부할 때의 처리는 5절에서 본다.

할당을 받은 기능 쪽은 입력의 현재 상태와 기능의 상태가 어긋날 수 있다는 점을 처리해야 한다. Part 6의 예는 주차 브레이크다. 할당되는 순간 입력이 "해제"를 가리키면, 기능은 "체결" 신호를 먼저 본 적이 없다. 그래서 Alarm Mask로 확인을 받거나 입력을 한 번 체결 위치로 돌리게 한 뒤에야 해제 신호에 반응하도록 설계할 수 있다.

<small>근거: ISO 11783-6 J.3.1, J.5, J.6, J.7.5~J.7.8</small>

## 5. 할당 메시지의 바이트 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절은 4절의 메시지를 바이트로 본다. 2바이트 이상 값은 리틀 엔디언(낮은 자리 바이트가 먼저)이다. 8바이트를 넘는 메시지는 한 CAN 프레임에 들어가지 않으므로 TP(Transport Protocol, 긴 데이터를 여러 프레임으로 나눠 보내는 방식, [15장](/study/isobus/15-tp-bam-cmdt))로 간다. `FF`는 쓰지 않는 자리를 채우는 값이고, `FFFF`는 "없음"을 뜻하는 NULL ID다.

### Preferred Assignment command(`22`)

| 바이트 | 내용 |
|---|---|
| 1 | `22` |
| 2 | 입력 유닛 수 |
| 반복(유닛마다) | 64-bit NAME(8바이트), Model Identification Code(2바이트), 이 유닛의 선호 기능 수(1바이트), 반복 { Auxiliary Function Object ID(2바이트), Auxiliary Input Object ID(2바이트) } |

조이스틱(NAME `EF BE 60 24 00 80 02 A0`, Model Identification Code `0x0017`)의 입력 `0x0005`를 기능 `0x0101`에, 입력 `0x0006`을 기능 `0x0102`에 연결하고 싶다면 21바이트가 된다. 8바이트를 넘으므로 TP로 간다.

```text
22 01 | EF BE 60 24 00 80 02 A0 | 17 00 | 02 | 01 01 05 00 | 02 01 06 00
     유닛 1개   NAME(리틀 엔디언)          Model    기능 2개  0x0101<-0x0005  0x0102<-0x0006
```

이 NAME은 설명용 예시 값이다. 앞에서부터 읽으면 다음과 같다.

1. `22`: Preferred Assignment command
2. `01`: 입력 유닛 1개
3. `EF BE 60 24 00 80 02 A0`: 조이스틱의 NAME(8바이트)
4. `17 00`: Model Identification Code `0x0017`
5. `02`: 이 유닛에 연결하고 싶은 기능 2개
6. `01 01 05 00`: 기능 `0x0101` ← 입력 `0x0005`
7. `02 01 06 00`: 기능 `0x0102` ← 입력 `0x0006`

### Preferred Assignment response

VT는 명령을 받으면 즉시 검증해 Preferred Assignment response(8바이트)를 보낸다. 오류가 하나라도 있으면 <strong>명령 전체를 무시</strong>하고 할당 처리를 하지 않는다. 응답 Byte 2의 비트는 Bit 0 입력 유닛(NAME 또는 Model Identification Code) 무효, Bit 1 Function Object ID 무효, Bit 2 Input Object ID 무효, Bit 3 Function Object ID 중복, Bit 4 기타다. Byte 3~4에는 문제가 된 할당의 Function Object ID가 실리고, 오류가 없으면 NULL(`FFFF`)이다. 성공 응답은 `22 00 FF FF FF FF FF FF`이다.

### Auxiliary Assignment Type 2 command(`24`)

<strong>Auxiliary Assignment Type 2 command(`24`)</strong>는 VT→ECU 14바이트 메시지라 TP로 간다.

| 바이트 | 내용 |
|---|---|
| 2~9 | 입력 유닛의 64-bit NAME, 할당 제거면 `FF`×8 |
| 10 | Bit 7 Preferred Assignment(0 = 선호 할당으로 저장, 1 = 저장하지 말 것), Bit 6~5 예약(0), Bit 4~0 할당된 입력의 타입(할당 제거면 `1F`) |
| 11, 12 | Auxiliary Input Object ID, 할당 제거면 `FFFF` |
| 13, 14 | Auxiliary Function Object ID, `FFFF`면 그 Working Set의 모든 기능에서 할당 제거 |

위 Preferred Assignment에서 온 할당이라면 Bit 7 = 1이므로 Byte 10은 `0x80 | 3 = 0x83`이다. `0x80`은 Bit 7만 1인 값이고, `|`는 두 값의 비트를 합치는(OR) 계산이다. 메시지는 `24 EF BE 60 24 00 80 02 A0 83 05 00 01 01`이다.

할당 제거는 두 형태만 허용된다. 기능 하나만 풀 때는 NAME `FF`×8, 타입 `1F`, 입력 `FFFF`, 기능 ID를 준다. 운전자가 기능 `0x0101`을 풀었다면 `24 FF FF FF FF FF FF FF FF 1F FF FF 01 01`이다. 그 Working Set의 할당을 모두 풀 때는 기능 ID도 `FFFF`로 준다. `1F`(=31)는 3절 타입 표의 "할당 제거 명령에 쓰는 값"이다.

### Assignment response

VT는 이 명령을 보낸 뒤 그 Working Set의 응답을 받기 전에는 그 Working Set에 다른 입력을 할당하지 않는다. 2 s 안에 응답이 없으면 재전송하고, 3회 실패하면 그 기능을 쓸 수 없다고 운전자에게 알린다. 기능 Working Set은 <strong>1 s 안에</strong> 응답해야 한다. 응답은 `24 01 01 00 FF FF FF FF`처럼 Byte 2~3에 기능 ID, Byte 4에 오류를 담는다. Bit 0 = 1이면 할당 거부다. 이때 VT는 운전자에게 알리고, 그 입력에 다른 기능이 없으면 상태 메시지를 끌 수 있다. Bit 1은 v5 이하에서 "이미 같은 입력에 할당됨"이었지만 오류가 아니며 동작을 바꾸면 안 된다. v6부터는 예약이다.

### Auxiliary Input Status Type 2 Enable(`25`)

<strong>Auxiliary Input Status Type 2 Enable(`25`)</strong>은 VT가 입력별 상태 메시지를 켜고 끄는 명령이다. 불필요한 버스 메시지를 줄이고, 할당되지 않은 입력에 기능이 반응할 가능성을 줄이려는 것이다.

| 프레임 | 바이트 | 의미 |
|---|---|---|
| 명령(VT→입력 유닛) | `25 05 00 01 FF FF FF FF` | 입력 `0x0005` 상태 메시지 켜기 |
| 응답(입력 유닛→VT) | `25 05 00 01 00 FF FF FF` | Byte 4 상태 1(켜짐), Byte 5 오류 0 |
| 명령(전부 끄기) | `25 FF FF 00 FF FF FF FF` | `FFFF`(모든 입력)는 <strong>끌 때만</strong> 쓸 수 있다 |

응답 오류 Bit 0은 Invalid Auxiliary Input Object ID, Bit 1은 기타다. VT는 응답을 받기 전에는 그 입력에 기능을 할당하지 않는다. 재전송 규칙은 2 s·3회다.

<small>근거: ISO 11783-6 J.7.5~J.7.8, J.7.11~J.7.12</small>

## 6. 입력 유닛이 보내는 메시지: Status와 Maintenance

입력 유닛은 두 가지를 보낸다. 조작구의 값을 알리는 Status와, "나 아직 살아 있다"를 알리는 Maintenance다. 이 절은 두 메시지의 규칙과 PGN 함정, 그리고 입력 유닛이 구성을 바꿀 때의 절차를 본다.

### Auxiliary Input Type 2 Status(`26`)

<strong>Auxiliary Input Type 2 Status(`26`)</strong>는 입력 유닛이 값을 알리는 메시지다.

| 바이트 | 내용 |
|---|---|
| 2, 3 | Auxiliary Input Object ID |
| 4, 5 | Value 1. 아날로그는 0.001 556 29 %/bit, 유효 `0000`~`FAFF`, 예약 `FB00`~`FDFF`, 오류 `FE00`~`FEFF`, N/A `FF00`~`FFFF` |
| 6, 7 | Value 2(같은 인코딩) |
| 8 | Operating State: Bit 0 learn mode, Bit 1 learn mode에서 조작됨, Bit 2 잠김(v6), Bit 3 잠긴 중 조작 감지(v6) |

Value 칸의 값 구간은 다음 뜻이다. 유효 구간은 정상 값, 예약 구간은 나중을 위해 비워 둔 값, 오류 구간은 센서나 스위치에 문제가 생겼다는 표시, N/A(Not Available)는 값을 줄 수 없다는 표시다. "0.001 556 29 %/bit"는 원시값 1이 0.001 556 29 %라는 뜻이라, 원시값에 이 수를 곱하면 %가 된다.

`FAFF`(64255) × 0.001 556 29 ≈ 100 %이고, 50 %는 `0x7D80`(32128)이다. 타입 9·10의 `FB00`·`FB01`(래치 표시)은 아날로그 예약 구간의 값을 쓴다. 0~2처럼 범위가 정해진 디지털 값은 그 범위가 유효 구간이고, 예약·오류·N/A 구간은 아날로그와 같다. 스위치 고착이나 단선처럼 입력이 무효 상태로 판정되면 오류 구간 값으로 알리고, 추가로 Alarm Mask를 띄울 수 있다.

전송 규칙은 다음과 같다.

- 초기화 후 VT가 켜기 전에는 자동으로 보내면 안 된다.
- 켜진 뒤에는 입력마다 초당 1회, 그리고 값이 바뀌면 즉시 보낸다. 같은 입력의 메시지 사이는 최소 50 ms(입력당 최대 20 Hz)다. 비래치 Boolean은 누르고 있는 동안 200 ms마다 보내고, 간격이 300 ms를 넘으면 기능 Working Set은 놓은 것으로 처리해야 한다(shall, 반드시 지킬 규칙).
- 여러 입력이 동시에 20 Hz로 보내면 버스가 무거워진다. 평균은 그대로인데 노이즈로 값이 오래 떨리는 아날로그 입력처럼 줄일 수 있는 경우에는 빈도를 줄이는 것이 권고다.
- learn mode가 아니면 전역 주소로 보내고 확인응답이 없다. learn mode에서는 function instance 0 VT에 목적지 지정으로 보낸다.
- 권장 우선순위는 3이다. 제어 목적 메시지의 표준 권고에 맞고, TP·ETP 메시지에 막히지 않게 하려는 것이다.

::: warning PGN 함정: 입력 유닛이 "VT to ECU" PGN을 쓴다
PGN(Parameter Group Number)은 메시지의 종류를 가리키는 번호다([9장](/study/isobus/09-j1939-message)). learn mode가 아닐 때 상태 메시지는 입력 유닛(ECU)이 보내는데도 <strong>"VT to ECU" PGN 58880(0xE600)</strong>을 전역 주소로 쓴다. learn mode에서는 "ECU to VT" PGN 59136(0xE700)으로 VT에 보낸다. SA가 `0x2C`인 조이스틱이 우선순위 3으로 보내면 CAN ID는 `0x0CE6FF2C`다. "PGN 0xE600은 VT의 SA에서만 온다"고 가정한 필터나 디코더는 이 메시지를 놓치거나 잘못 해석한다. Type 1 status도 같은 방식이다.

CAN ID `0x0CE6FF2C`를 두 자리씩 나누면 `0C`(우선순위 3, 예약·데이터 페이지 비트는 0), `E6`(PGN 0xE600의 PF 값), `FF`(전역 주소), `2C`(보낸 조이스틱의 SA)다.
:::

### Auxiliary Input Type 2 Maintenance(`23`)

<strong>Auxiliary Input Type 2 Maintenance(`23`)</strong>는 입력 유닛(개별 조작구가 아니라 Working Set 단위)이 <strong>100 ms마다</strong> 전역 주소로 보내는 생존 신호다. Part 6의 메시지 정의 표는 PGN을 "ECU to VT, Destination-Specific"으로 적었지만, 본문은 모든 Working Set이 받도록 전역 주소로 보내라고 한다. 두 기술을 합치면 PGN 59136(0xE700)에 목적지를 `FF`로 쓰는 것으로 읽힌다. 위 조이스틱이면 CAN ID는 `0x0CE7FF2C`다. 권장 우선순위는 역시 3이다.

| 바이트 | 내용 |
|---|---|
| 2, 3 | Model Identification Code(제조사 정의, 0~`FFFE`) |
| 4 | Status: 0 = Initializing(아직 할당에 쓸 수 없음), 1 = Ready(풀이 VT에 로드되어 할당 가능) |

`23 17 00 00 FF FF FF FF`(Initializing)에서 시작해, 오류 없는 End of Object Pool response나 Load Version·Extended Load Version response를 받으면 `23 17 00 01 FF FF FF FF`(Ready)로 바꾼다. 기능 Working Set은 이 Ready를 Preferred Assignment를 보낼 신호로 쓴다. 입력 유닛은 이 메시지와 <strong>별도로</strong> Working Set Maintenance도 초당 1회 보내야 한다. Model Identification Code는 한 구성 안에서는 런타임에 바뀌지 않고, 재구성할 때만 바뀐다.

### 입력 유닛이 구성을 바꿀 때

입력 유닛이 할당된 입력 오브젝트를 바꾸거나 지워야 할 때는 정해진 절차를 따른다.

1. 상태 메시지가 켜진 입력이 있었다면 AUX가 잠시 쓸 수 없을 수 있다고 운전자에게 알린다. v6에서 생긴 Working Set 쪽 의무다. 재구성 원인을 아는 쪽이 Working Set뿐이라 경고를 한 곳에서 하도록 정했다.
2. Maintenance 송신을 <strong>500 ms보다 길게</strong> 멈춘다.
3. Status = Initializing으로 송신을 재개한다. Model Identification Code는 바뀐 구성을 반영해 달라져야 한다.
4. 풀을 갱신한다. 기존 풀을 지우거나 부분 갱신을 보낸다.
5. 오류 없는 End of Object Pool response를 받으면 Status = Ready로 바꾼다.

![입력 유닛 재구성 시간축: 0~600 ms에 Maintenance(Ready)를 100 ms마다 보내다가 송신을 500 ms보다 길게 멈추고, 마지막 송신 300 ms 뒤인 900 ms에 VT와 기능 Working Set이 할당을 모두 제거하며, 1300 ms에 새 Model ID로 Initializing을 재개해 풀을 갱신하고, End of Object Pool response(오류 없음) 뒤 Ready가 되면 기능 Working Set이 Preferred Assignment를 다시 보냄](/images/study-isobus/40-aux-maintenance-timeline-light.png)
![입력 유닛 재구성 시간축: 0~600 ms에 Maintenance(Ready)를 100 ms마다 보내다가 송신을 500 ms보다 길게 멈추고, 마지막 송신 300 ms 뒤인 900 ms에 VT와 기능 Working Set이 할당을 모두 제거하며, 1300 ms에 새 Model ID로 Initializing을 재개해 풀을 갱신하고, End of Object Pool response(오류 없음) 뒤 Ready가 되면 기능 Working Set이 Preferred Assignment를 다시 보냄](/images/study-isobus/40-aux-maintenance-timeline-dark.png)

그림의 시각은 설명을 위해 고른 예다. Part 6은 이 절차가 기능과 입력의 연결을 안전하게 끊었다 다시 잇는 수단이라고 설명한다. 2단계의 "500 ms 넘게 멈춤"은 7절 표의 300 ms 타임아웃보다 길다. 그래서 VT와 기능 Working Set이 반드시 할당을 끊은 뒤 새 구성으로 다시 연결되도록 고른 값으로 보인다(추론).

<small>근거: ISO 11783-6 J.2, J.7.4, J.7.9, J.7.10</small>

## 7. 할당이 저장되는 조건과 풀리는 조건

할당이 왜 저장되고 왜 풀리는지 알면 "어제는 됐는데 오늘은 안 된다" 같은 장애를 빨리 찾을 수 있다. 이 절은 두 조건을 표로 정리한다.

선호 할당은 기능 Working Set이 저장한다.

- Assignment Type 2의 Preferred Assignment 비트가 0이면 그 할당을 새 선호 할당으로 저장한다.
- 언제 확정 저장할지는 Working Set이 정한다. 명령을 받을 때, 키 오프, 전원 상실, 고유 화면의 저장 버튼 등이다.
- 입력 구성별로 선호 할당 세트를 여러 개 둘 수 있다. File Server(파일을 저장해 두는 ISOBUS 장치)에 저장해 기능적으로 동일한 다른 Working Set에 옮길 수도 있다([51장](/study/isobus/51-file-server-basics)).
- Model Identification Code가 같고 기능적으로 동일한 다른 입력 유닛에 맞춰 Preferred Assignment를 고쳐 보낼 수 있다.

할당이 풀리는 경우는 다음과 같다.

| 원인 | 누가 무엇을 보내나 | Preferred Assignment 비트 |
|---|---|---|
| 운전자가 다른 입력으로 덮어쓰거나 NULL을 할당 | VT → 기능 Working Set: Assignment Type 2 | 0(저장) |
| 충돌 감지(타입 불일치, Single-assignment·Restriction·Critical 위반, 풀 제거) | VT → 기능 Working Set: 할당 제거 + 운전자 경고 | |
| Preferred Assignment에 그 기능이 없음 | VT가 할당 제거로 해석 | 1 |
| 입력 유닛의 Maintenance가 300 ms 동안 없음 | VT와 기능 Working Set이 그 유닛의 할당을 모두 제거 | 1(저장하지 말 것) |
| 할당이 걸린 Working Set의 풀 삭제·통신 상실 | VT가 그 Working Set에 매핑된 할당 제거 | |
| 기능 Working Set이 할당을 거부(응답 Bit 0) | VT가 운전자에게 알리고 상태 메시지를 끌 수 있음 | |
| Working Set 전원 차단 | | |

비트 칸이 빈 행은 그 경우를 다루는 조항이 비트 값을 따로 적지 않은 경우다. Assignment Type 2가 나가는 경우라면 4절의 일반 규칙(운전자 조작에서 비롯된 경우만 0)을 따른다.

입력 유닛이 사라졌을 때 Preferred Assignment 비트를 1로 보내는 이유가 중요하다. 비트가 0이면 기능 Working Set이 "할당 없음"을 새 선호 할당으로 저장해, 조이스틱이 다시 연결돼도 예전 할당이 복원되지 않는다. 기능 Working Set은 "Working State"(Part 6이 따로 정의하지 않은 말로, 작업기가 작업에 들어간 상태로 읽힌다)에 들어갔는데 필요한 기능이 할당되지 않았으면 운전자에게 할당 화면에서 할당하라고 알리는 등 조치해야 한다.

::: details 원문을 가진 독자를 위한 메모
위 "할당이 풀리는 경우" 표의 행별 근거 조항이다.

| 원인 | 근거 |
|---|---|
| 운전자가 다른 입력으로 덮어쓰거나 NULL을 할당 | J.6 규칙 9, J.5 단계 8~9 |
| 충돌 감지 | J.5 단계 6~7 |
| Preferred Assignment에 그 기능이 없음 | J.5 단계 5, J.7.7 |
| 입력 유닛의 Maintenance가 300 ms 동안 없음 | J.7.10 |
| 할당이 걸린 Working Set의 풀 삭제·통신 상실 | J.5, 4.6.9 |
| 기능 Working Set이 할당을 거부(응답 Bit 0) | J.7.6 |
| Working Set 전원 차단 | J.6 규칙 9 |

이 장의 나머지 대응: 3절 타입 표는 J.4.6(Table J.5), 4절 그림은 Figure J.7을 줄인 것, 4절 충돌 조건 표는 J.5 단계 6, "Preferred Assignment는 반드시 한 번 보낸다"는 J.6 규칙 1, 5절의 할당 제거 두 형태는 J.7.5 Figure J.10, 선호 할당 저장 규칙은 J.6 규칙 8, 3절의 "Assignment Lock" 개명은 J.1이다.
:::

<small>근거: ISO 11783-6 J.5, J.6, J.7.5~J.7.10</small>

## 8. 능력 조회, learn mode, 버전 6의 잠금

마지막으로 할당을 돕는 장치 세 가지를 본다. 지금 어떤 AUX 입력·기능이 있는지 묻는 능력 조회, 조작구를 직접 움직여 할당하는 learn mode, 오조작을 막는 v6 잠금이다.

### Auxiliary Capabilities(v5부터)

어떤 CF(Control Function, 버스에 참여하는 하나의 기능 단위)든 function instance 0 VT에 "지금 어떤 AUX 입력·기능이 있는가"를 물을 수 있다(Type 2 전용). 기능 Working Set은 이 정보로 지금 시스템의 입력 장치에 맞는 기능 제공 전략을 세울 수 있고, 진단에도 쓸 수 있다.

- 요청: `27 00 FF FF FF FF FF FF`. Byte 2가 0이면 입력 유닛, 1이면 기능 유닛의 능력을 묻는다.
- 응답: Byte 2에 그 종류의 유닛 수(Request Type이 무효면 0)가 오고, 유닛마다 NAME(8바이트), set 수(1바이트), set마다 3바이트 { 인스턴스 수, Function attribute, Assigned attribute }가 이어진다. Assigned attribute의 Bit 0은 0 = 입력, 1 = 기능이고, Bit 1은 1 = 유효한 할당이 있음이다.
- 보고 기준은 풀 안에 오브젝트가 <strong>있는지</strong>뿐이다. 입력의 현재 상태나 초기 선호 할당은 반영하지 않는다. 풀을 VT에 성공적으로 올린 유닛만 목록에 나온다.
- 요청 전에 각 입력 유닛의 Maintenance가 Ready인지 확인할 수 있다. 기능 쪽에는 이런 Ready 표시가 없다.

조이스틱 하나에 "타입 3 입력 2개(할당됨)"와 "타입 6 입력 4개(미할당)"가 있으면 응답은 `27 01 EF BE 60 24 00 80 02 A0 02 02 03 02 04 06 00`(17바이트, TP)이다. 풀어 보면 `27`은 Auxiliary Capabilities, `01`은 유닛 1개, 다음 8바이트는 NAME, `02`는 set 2개다. 첫 set `02 03 02`는 인스턴스 2개, 타입 3, Assigned attribute 2(Bit 1 = 1 할당 있음, Bit 0 = 0 입력)이고, 둘째 set `04 06 00`은 인스턴스 4개, 타입 6, 할당 없는 입력이다.

### learn mode

learn mode는 운전자가 할당 화면에서 기능을 고른 뒤 <strong>실제 조작구를 움직여</strong> 입력을 지정하는 VT의 선택 기능이다. "이 기능에 쓸 버튼을 지금 눌러 주세요" 방식이다.

- VT의 AUX 할당 화면이 떠 있는 동안에만 켤 수 있다. 켜고 끄는 방법은 VT 고유다.
- 켜져 있는 동안 VT는 VT Status Byte 7 Bit 6을 1로 둔다. [37장](/study/isobus/37-vt-command-details)에서 본 대로 이 비트가 바뀌면 VT Status가 즉시 나간다.
- 모든 입력 유닛은 enable 여부와 무관하게 정상 주기로 상태 메시지를 보낸다. 이때는 instance 0 VT에 목적지 지정(PGN 0xE700)으로 보내고, Operating State Bit 0(learn mode)과 Bit 1(learn mode에서 조작됨)을 쓴다. 메시지를 VT에만 보내는 것은 작업기가 이 메시지를 명령으로 오해할 가능성을 줄이기 위해서다.
- VT는 상태 메시지를 지켜보다가 실제로 움직인 입력에 선택된 기능을 할당한다.
- 기능 Working Set은 VT Status가 learn mode를 표시하는 동안 상태 메시지로 어떤 기능도 실행하면 안 된다.
- learn mode에 들어가고 나올 때 조작구와 기능의 상태가 어긋날 수 있다. 이를 해소하는 것은 기능의 책임이다. Part 6은 Assignment Type 2와 같은 주차 브레이크 예를 든다.

### 버전 6의 잠금(lock)

v6는 상태 메시지에 "잠김" 상태를 추가했다. 오조작을 막으려고 조작구를 잠그는 기능이다. 잠그는 방법은 고유 설계다. 입력 하나만 잠글 수도 있고, 다기능 조이스틱의 "lock" 스위치처럼 여러 입력을 한 번에 잠글 수도 있다. 현재 잠금 상태를 운전자가 볼 수 있게 표시하는 것이 권고다.

- 잠긴 동안 Value는 <strong>잠근 순간의 값</strong>으로 고정된다(Byte 8 Bit 2 = 1).
- 잠긴 상태에서 조작구를 움직이면 Value는 그대로 두고 Interaction Detected(Bit 3)를 1로 세운다. 잠금이 풀리면 Bit 3은 0으로 돌아간다.
- 작업기 기능은 Interaction Detected를 보고, 잠글 때 진행 중이던 동작을 멈추는 데 쓸 수 있다.

단계로 나누면 그림과 같다.

![v6 AUX 입력 잠금의 네 단계: 1 평상시(Value가 조작을 따라감, Bit 2 = 0, Bit 3 = 0), 2 잠김(Value가 잠근 순간 값 50 %에 고정, Bit 2 = 1), 3 잠긴 채 조작(Value는 그대로, Bit 2 = 1, Bit 3 = 1, 예: 26 05 00 80 7D FF FF 0C), 4 잠금 해제(Bit 2 = 0, Bit 3 = 0)](/images/study-isobus/40-aux-lock-states-light.png)
![v6 AUX 입력 잠금의 네 단계: 1 평상시(Value가 조작을 따라감, Bit 2 = 0, Bit 3 = 0), 2 잠김(Value가 잠근 순간 값 50 %에 고정, Bit 2 = 1), 3 잠긴 채 조작(Value는 그대로, Bit 2 = 1, Bit 3 = 1, 예: 26 05 00 80 7D FF FF 0C), 4 잠금 해제(Bit 2 = 0, Bit 3 = 0)](/images/study-isobus/40-aux-lock-states-dark.png)

`26 05 00 80 7D FF FF 0C`는 "입력 `0x0005`(타입 3)가 50 %에서 잠겼고, 잠긴 뒤 운전자가 조작구를 건드렸다"는 뜻이다. 한 칸씩 보면 `26`은 Status, `05 00`은 입력 `0x0005`, `80 7D`는 Value 1 = `0x7D80` = 50 %, `FF FF`는 Value 2(타입 3에서는 예약)다. 마지막 `0C`는 2진수 `0000 1100`이라 Bit 2(잠김)와 Bit 3(잠긴 중 조작 감지)가 1이다. 기능 Working Set은 50 %를 새 명령으로 해석하면 안 된다. 잠금 전의 값이 그대로 실려 있을 뿐이다.

아래 코드는 이 장의 바이트 예제를 직접 조립하고 해석해 본다. 주석의 J.7.7 같은 번호는 Part 6의 조항 번호라서 읽지 않아도 된다.

::: details AUX 메시지 조립·해석 검산 (Python)
```python
def le(v, n):
    return list(v.to_bytes(n, "little"))

def hx(b):
    return " ".join(f"{x:02X}" for x in b)

def name(identity, mfr, ecu_inst, func_inst, func, dev_class, dev_inst, group, self_cfg):
    return (identity | mfr << 21 | ecu_inst << 32 | func_inst << 35 | func << 40
            | dev_class << 49 | dev_inst << 56 | group << 60 | self_cfg << 63)

# 예시 값으로 만든 조이스틱 NAME (필드 값은 설명용)
JOY = name(0x0BEEF, 0x123, 0, 0, 0x80, 1, 0, 2, 1)
assert hx(le(JOY, 8)) == "EF BE 60 24 00 80 02 A0"

# J.7.7: Identity Number(하위 21비트)를 빼고 비교하면 "기능적으로 동일한" 유닛을 찾을 수 있다
def same_kind(a, b):
    mask = ~0x1FFFFF & (2**64 - 1)
    return a & mask == b & mask

assert same_kind(JOY, name(0x1F00D, 0x123, 0, 0, 0x80, 1, 0, 2, 1))

# Preferred Assignment command (VT function 34)
def preferred(units):
    out = [0x22, len(units)]
    for unit_name, model, pairs in units:
        out += le(unit_name, 8) + le(model, 2) + [len(pairs)]
        for func_id, input_id in pairs:
            out += le(func_id, 2) + le(input_id, 2)
    return out

pa = preferred([(JOY, 0x0017, [(0x0101, 0x0005), (0x0102, 0x0006)])])
assert len(pa) == 21                                 # 8바이트 초과 -> TP
assert hx(pa) == "22 01 EF BE 60 24 00 80 02 A0 17 00 02 01 01 05 00 02 01 06 00"

# Auxiliary Assignment Type 2 command (VT function 36, 14바이트)
def assignment(unit_name, func_type, input_id, func_id, store_preferred):
    flags = (0 if store_preferred else 0x80) | func_type
    return [0x24] + le(unit_name, 8) + [flags] + le(input_id, 2) + le(func_id, 2)

asg = assignment(JOY, 3, 0x0005, 0x0101, store_preferred=False)
assert len(asg) == 14 and hx(asg) == "24 EF BE 60 24 00 80 02 A0 83 05 00 01 01"
remove_one = [0x24] + [0xFF] * 8 + [0x1F] + le(0xFFFF, 2) + le(0x0101, 2)
assert hx(remove_one) == "24 FF FF FF FF FF FF FF FF 1F FF FF 01 01"

# Auxiliary Input Type 2 Status (VT function 38) 해석
RES = 0.00155629                                     # %/bit

def decode_status(d):
    oid = d[1] | d[2] << 8
    v1, v2, op = d[3] | d[4] << 8, d[5] | d[6] << 8, d[7]
    return oid, v1, v2, {"learn": op & 1, "activated": op >> 1 & 1,
                         "locked": op >> 2 & 1, "interaction": op >> 3 & 1}

oid, v1, v2, op = decode_status([0x26, 0x05, 0x00, 0x80, 0x7D, 0xFF, 0xFF, 0x00])
assert oid == 5 and round(v1 * RES, 1) == 50.0 and v2 == 0xFFFF
oid, v1, v2, op = decode_status([0x26, 0x06, 0x00, 0x01, 0x00, 0x07, 0x00, 0x0C])
assert (v1, v2) == (1, 7) and op["locked"] == 1 and op["interaction"] == 1

# 상태 메시지의 CAN ID: 우선순위 3, PGN 0xE600(VT to ECU), DA 0xFF(전역), SA 0x2C(예시)
can_id = 3 << 26 | 0xE6 << 16 | 0xFF << 8 | 0x2C
assert f"{can_id:08X}" == "0CE6FF2C"
print("block C: OK")
```
:::

실행하면 모든 `assert`가 통과하고 `block C: OK`가 찍힌다. `name()`은 NAME의 각 필드를 정해진 비트 위치로 밀어 64비트 수 하나로 합친다. `same_kind()`는 하위 21비트(Identity Number)를 지운 뒤 비교한다. `assignment()`의 `store_preferred=False`는 "저장하지 말 것"이므로 Bit 7이 1이 되어 `83`이 나온다. `decode_status()`는 Operating State 바이트에서 비트를 하나씩 꺼낸다.

<small>근거: ISO 11783-6 J.1, J.7.9, J.7.13~J.7.14, J.8</small>

::: tip 핵심 정리
- AUX는 입력 유닛(조이스틱)의 입력을 작업기의 기능에 연결한다. 연결(할당)은 function instance 0 VT가 정하고, 입력 값은 입력 유닛이 버스 전체에 보내 기능 Working Set이 직접 읽는다.
- AUX-N(Type 2)은 입력을 SA가 아니라 NAME과 Object ID로 식별한다. 그래서 선호 할당을 저장했다가 다음 전원 사이클에 복원할 수 있다.
- 입력 타입과 기능 타입은 정확히 같아야 하고, Function attributes의 Critical Control, Assignment Restriction, Single-assignment 비트도 지켜야 한다.
- AUX-N 할당은 Preferred Assignment, VT 검증, Status Enable, Assignment Type 2 순서다. Preferred Assignment 비트가 저장 여부를 정하고, 입력 유닛의 Maintenance가 300 ms 끊기면 할당이 풀린다.
- learn mode에서는 상태 메시지가 VT로만 가고 기능은 반응하지 않는다. v6 잠금 중에는 Value가 고정되고 Bit 2·3으로 잠김과 조작 감지를 알린다.
:::

::: details 확인 문제
1. (개념) 운전자가 조이스틱 버튼을 누르면 그 값은 VT를 거쳐 작업기로 가는가?
2. (개념) 같은 조이스틱인데도 전원을 켤 때마다 SA가 바뀔 수 있다. AUX-N은 이 문제를 어떻게 피하는가?
3. (판단) 기능의 Function attributes가 `0x43`이고, 운전자가 할당 화면에서 Function attributes가 `0x02`인 입력에 연결하려 한다. VT는 이 할당을 허락하는가?
4. (장애 진단) 트랙터의 조이스틱을 같은 모델의 새 제품으로 바꾼 뒤, 작업기의 AUX 기능이 전원을 켤 때마다 할당되지 않는다. Preferred Assignment response는 `22 01 01 01 FF FF FF FF`다. 원인과 대책은 무엇인가?

**답 가이드**
1. 아니다. 입력 유닛이 Status 메시지를 버스 전체에 보내고, 그 입력을 할당받은 기능 Working Set이 직접 읽는다. VT는 할당을 정하고 Status Enable과 Assignment로 알려 줄 뿐이다. learn mode에서만 상태 메시지가 VT로 간다.
2. 입력을 SA 대신 64비트 NAME과 Auxiliary Input Object ID로 식별한다. 기능 Working Set도 선호 할당을 NAME으로 저장하므로, SA가 바뀌어도 같은 유닛을 찾아 Preferred Assignment를 보낼 수 있다.
3. 허락하지 않는다. `0x43`의 하위 5비트는 타입 3이고, `0x02`의 하위 5비트는 타입 2라 타입이 다르다(충돌 조건 I). 게다가 `0x43`은 Bit 6(Assignment Restriction)이 1이라 Preferred Assignment로 정한 할당만 허용한다. 그 입력이 선호 할당의 입력이 아니라면 타입이 같았더라도 운전자가 연결할 수 없다(충돌 조건 IV).
4. Byte 2 = `0x01`은 Bit 0(입력 유닛의 NAME 또는 Model Identification Code 무효)이고, Byte 3~4는 문제가 된 할당의 기능 ID `0x0101`이다. 저장된 선호 할당이 예전 조이스틱의 NAME을 그대로 참조해, VT가 명령 전체를 무시했다. 기능 Working Set은 NAME을 비교할 때 Identity Number(하위 21비트)를 빼고, Model Identification Code까지 같은 유닛을 "기능적으로 동일한" 유닛으로 보고 Preferred Assignment를 그 유닛의 NAME으로 고쳐 보내야 한다. 새 유닛의 Maintenance가 Ready가 된 뒤에 보내야 Bit 2(Input Object ID 무효)도 피할 수 있다.
:::

## 다음 챕터

- 다음: [41장 Task Controller(TC) 기초](/study/isobus/41-tc-basics)
