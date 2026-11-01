---
title: "주소 클레임: 주소를 정하는 절차"
description: "CF가 Request for Address Claimed와 Address Claimed로 주소를 정하는 순서와 같은 주소를 두고 NAME으로 승패를 가리는 방법을 익히고, Commanded Address와 주소 관리 메시지 네 가지의 프레임을 읽는다."
date: 2026-04-13
tags: [ISOBUS, J1939, CAN, 주소, 주소 클레임]
prev: /study/isobus/12-j1939-address-name
next: /study/isobus/14-name-management-init
---

# 주소 클레임: 주소를 정하는 절차

::: info 학습 목표
- 주소 클레임이 왜 필요한지 회의실 자리 정하기에 빗대어 설명할 수 있다.
- 주소 조회, 대기, Address Claimed 송신, 250 ms 확인으로 이어지는 순서를 말할 수 있다.
- 두 CF가 같은 주소를 원할 때 NAME 비교로 승패가 갈리고, 진 쪽이 AAC 값에 따라 다르게 움직이는 과정을 따라갈 수 있다.
- Commanded Address가 무엇이고 왜 BAM으로 보내는지 설명할 수 있다.
- 주소 관리 메시지 네 가지의 CAN ID와 데이터 바이트를 읽을 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [12장 주소와 NAME](/study/isobus/12-j1939-address-name), [10장 요청과 응답](/study/isobus/10-j1939-request-ack)
- 이 장에서 처음 나오는 말
  - Address Claimed: "이 주소는 내가 쓴다"고 자기 NAME과 함께 모두에게 알리는 메시지(PGN 60928).
  - Request for Address Claimed: Address Claimed를 보내 달라고 요청하는 메시지. 누가 어느 주소를 쓰는지 물을 때 쓴다.
  - Cannot Claim Address: 주소를 얻지 못했다고 알리는 메시지.
  - RTxD(Random Transmit Delay): 여러 CF가 같은 순간에 송신하지 않도록 넣는 무작위 대기 시간.
  - Commanded Address: 다른 장치가 특정 CF에게 쓸 주소를 지정해 주는 메시지.
  - BAM(Broadcast Announce Message): 8바이트보다 긴 데이터를 여러 프레임으로 나눠 모두에게 보내는 방법. [15장](/study/isobus/15-tp-bam-cmdt)에서 자세히 본다.
:::

좌석 번호가 붙은 회의실에 참석자들이 하나둘 들어와 빈자리를 찾아 앉는다고 하자. 누가 어느 자리에 앉았는지 서로 알고, 두 사람이 같은 자리를 원할 때 다툼 없이 정하는 규칙이 있어야 회의가 굴러간다. J1939 네트워크에서 이 일을 하는 것이 주소 클레임(address claim)이다. 이 장은 [12장](/study/isobus/12-j1939-address-name)에서 본 주소(SA)와 NAME을 짝짓는 절차를 비유, 순서, 실제 프레임 순으로 따라간다.

## 1. 주소 클레임을 비유로 보기

이 절은 주소 클레임 전체를 회의실 자리 정하기에 빗대어 먼저 훑는다. 메시지 이름과 숫자는 2절부터 정확히 다룬다.

좌석이 네트워크의 주소이고, 참석자가 CF(Control Function, 주소 하나를 쓰며 통신하는 기능 단위)다. 참석자는 저마다 명함, 곧 NAME을 들고 있다.

1. 새 참석자는 들어오자마자 "지금 누가 어느 자리에 앉아 있나요?"라고 묻는다.
2. 이미 앉은 사람들은 모두 "저는 n번 자리이고, 제 명함은 이것"이라고 답한다.
3. 새 참석자는 답을 다 들을 만큼 잠깐 기다린 뒤, 빈자리 하나를 골라 "이 자리는 제 자리"라고 명함과 함께 크게 선언한다.
4. 두 사람이 같은 자리를 선언하면 명함 번호(NAME 값)가 작은 사람이 앉는다. 이긴 사람도 한 번 더 선언해 자리를 굳힌다.
5. 진 사람은 다른 빈자리로 옮겨 다시 선언한다. 옮길 수 없는 사람은 "앉을 자리가 없다"고 알리고 듣기만 한다.
6. 선언하고 잠깐 동안 아무도 이의를 제기하지 않으면, 그때부터 회의(일반 통신)에 참여한다.

같은 흐름을 실제 메시지 이름으로 그리면 다음과 같다.

![주소 클레임 흐름도: 전원 ON, Request for Address Claimed, 250 ms + RTxD 대기, Address Claimed 송신, 경합이 없으면 250 ms 뒤 일반 통신, 경합이 있으면 NAME 비교 후 이기면 다시 클레임, 지면 AAC=1은 다른 주소로 다시 클레임하고 AAC=0은 Cannot Claim](/images/study-isobus/13-claim-flow-light.png)
![주소 클레임 흐름도: 전원 ON, Request for Address Claimed, 250 ms + RTxD 대기, Address Claimed 송신, 경합이 없으면 250 ms 뒤 일반 통신, 경합이 있으면 NAME 비교 후 이기면 다시 클레임, 지면 AAC=1은 다른 주소로 다시 클레임하고 AAC=0은 Cannot Claim](/images/study-isobus/13-claim-flow-dark.png)

| 회의실 | 주소 클레임 | 메시지 |
|---|---|---|
| "누가 어느 자리에 있나요?" | 주소 조회 | Request for Address Claimed |
| "저는 n번, 명함은 이것" | 조회에 대한 응답 | Address Claimed |
| "이 자리는 제 자리" | 주소 선언 | Address Claimed |
| 명함 번호가 작은 사람이 앉는다 | NAME 비교 | 메시지 없음. 각 CF가 스스로 비교한다 |
| "앉을 자리가 없다" | 클레임 실패 | Cannot Claim Address |
| 사회자가 "명함 X인 분은 m번으로" | 주소 지정 | Commanded Address |

비유가 맞지 않는 점이 둘 있다. 첫째, 회의실에서는 먼저 앉은 사람이 유리하지만 주소 클레임에서는 도착 순서와 상관없이 NAME이 작은 쪽이 이긴다. 이미 쓰던 주소라도 NAME이 더 작은 CF가 나타나면 내줘야 한다. 둘째, 실제 장치는 말 대신 프레임을 보내고, 선언은 언제나 네트워크 전체(Global)에 들린다.

정리하면, 주소 클레임은 "묻고, 기다리고, 선언하고, 겹치면 NAME으로 가르는" 절차다.

## 2. 주소 클레임 절차

이 절은 1절의 비유를 실제 메시지와 시간 규칙으로 바꿔 본다.

J1939 장치는 네트워크에 연결되면 <strong>Address Claimed 메시지(PGN 60928, 0xEE00)</strong>를 브로드캐스트하여 주소를 선점한다. 브로드캐스트는 목적지를 Global(255)로 해서 모두에게 보내는 것이다. 같은 주소를 사용하려는 장치가 있으면 NAME 비교를 통해 충돌을 해결한다.

클레임에 앞서 <strong>주소 조회 시퀀스</strong>를 거치는 것이 표준 절차다. 순서는 다음과 같다.

1. Request for Address Claimed(PGN 59904)를 Global 또는 자신의 initial address(전원을 켤 때 처음 클레임을 시도하는 주소)로 보낸다. PGN 59904는 [10장](/study/isobus/10-j1939-request-ack)에서 본 Request, 곧 "이 PGN을 보내 달라"는 요청 메시지다. 여기서 요청하는 PGN이 Address Claimed(60928)다.
2. <strong>최소 250 ms + RTxD</strong>를 대기하면서 수신된 Address Claimed들로 사용 중인 주소를 파악한다.
3. 비어 있는 주소를 클레임한다.

여기서 <strong>RTxD(Random Transmit Delay)</strong>는 0~255 범위의 난수에 0.6 ms를 곱한 지연 시간이다. 여러 장치가 동시에 송신해 버스 오류를 일으키는 것을 막는다. 예를 들어 난수가 100이면 RTxD는 60 ms다. 같은 순간에 전원을 받은 장치들도 난수가 다르면 서로 다른 때에 송신하게 된다.

다음 그림은 두 ECU가 같은 주소 23을 동시에 클레임했을 때의 흐름이다. ECU A의 NAME은 `0x100`, ECU B의 NAME은 `0x200`이라고 하자. 실제 NAME은 64비트지만 크기 비교만 보이려고 짧은 값을 썼다.

![같은 주소 23을 두 ECU가 클레임할 때: A(NAME 0x100)와 B(NAME 0x200)가 SA=23을 클레임하고, 충돌을 감지한 뒤 A는 다시 클레임해 주소를 지키며, 진 B는 AAC=1이면 SA=128로 다시 클레임하고 AAC=0이면 SA=0xFE로 Cannot Claim을 보낸다](/images/study-isobus/13-claim-conflict-light.png)
![같은 주소 23을 두 ECU가 클레임할 때: A(NAME 0x100)와 B(NAME 0x200)가 SA=23을 클레임하고, 충돌을 감지한 뒤 A는 다시 클레임해 주소를 지키며, 진 B는 AAC=1이면 SA=128로 다시 클레임하고 AAC=0이면 SA=0xFE로 Cannot Claim을 보낸다](/images/study-isobus/13-claim-conflict-dark.png)

그림을 위에서부터 읽는다.

1. 전원이 켜지고 A와 B가 각자 SA=23으로 Address Claimed를 보낸다.
2. 두 ECU 모두 상대의 클레임을 받아 SA 23에서 충돌이 났음을 안다.
3. A는 상대 NAME(`0x200`)이 자기 NAME(`0x100`)보다 크므로 이겼다고 판단한다. 이긴 A도 SA=23으로 Address Claimed를 한 번 더 보내 주소를 지킨다.
4. B는 상대 NAME(`0x100`)이 자기 NAME(`0x200`)보다 작으므로 졌다고 판단한다.
5. B의 AAC(12장에서 본 NAME 맨 앞 비트)가 1이면 자동 재할당이 가능하다. 그래서 128~247 범위의 다른 주소(그림에서는 SA=128)로 다시 클레임해 성공한다.
6. AAC가 0이면 다른 주소로 옮길 수 없다. 그래서 Cannot Claim Address를 SA `0xFE`(=254, NULL 주소)로 보내고, NULL 주소로 남아 제한된 일만 한다.

### 절차 단계 요약

1. <strong>전원 ON</strong>: ECU가 사용할 SA를 선택한다(preferred address 또는 저장된 initial address).
2. <strong>주소 조회</strong>: Request for Address Claimed(PGN 59904)를 보내고 250 ms + RTxD 대기하며 사용 중인 주소를 파악한다.
3. <strong>Address Claimed 전송</strong>: 선택한 SA와 자신의 NAME을 PGN 60928으로 브로드캐스트한다.
4. <strong>충돌 감지</strong>: 같은 SA로 다른 NAME이 수신되면 충돌이다.
5. <strong>NAME 비교</strong>: 더 작은 NAME 값을 가진 장치가 해당 SA를 획득한다. <strong>승자도 자신의 NAME으로 Address Claimed를 재송신</strong>해 주소를 지켜야 한다.
6. <strong>패자 처리</strong>
   - AAC=1: 128~247 범위에서 다른 SA를 선택하여 재클레임한다.
   - AAC=0: RTxD만큼 기다렸다가 Cannot Claim(SA=0xFE)을 보내고, 그 뒤로는 수신 위주로 동작한다.

### 타이밍 규칙

| 항목 | 값 |
|------|----|
| 주소 조회(Request) 후 대기 | 최소 250 ms + RTxD |
| 클레임 성공 판정 | Address Claimed 송신 후 250 ms 동안 경합 클레임이 없어야 성공 |
| 일반 통신 시작 | 클레임 성공 후 250 ms 경과 전에는 일반 메시지 송신 금지 (Request 응답은 예외) |
| RTxD | 난수(0~255) × 0.6 ms |

규칙마다 이유가 있다.

- 조회 후 대기: 이미 주소를 가진 CF들이 Request에 응답할 시간을 준다. RTxD를 더하는 것은 같은 때 켜진 CF들이 같은 순간에 클레임하지 않게 하려는 것이다.
- 클레임 성공 판정: 내 클레임을 들은 다른 CF가 더 작은 NAME으로 반박할 시간을 준다.
- 일반 통신 시작: 주소가 확정되기 전에 그 주소로 일반 메시지를 보내면, 클레임에서 졌을 때 남의 주소로 보낸 셈이 된다(해석).

둘째 줄과 셋째 줄의 250 ms는 따로 더하는 두 구간이 아니라 같은 구간이다. Address Claimed를 보낸 뒤 250 ms가 경합 없이 지나면 곧바로 일반 메시지를 보낼 수 있다. 4절의 시나리오에서 시각으로 확인하고, [14장](/study/isobus/14-name-management-init)에서 근거를 다시 본다.

<small>근거: ISO 11783-5:2019 3.4, 4.4.2.2~4.4.2.4, 4.5.1, 4.5.2</small>

## 3. Commanded Address: 다른 장치가 주소를 정해 주기

이 절은 CF가 스스로 주소를 고르는 대신 다른 장치가 주소를 정해 주는 방법을 본다. 회의 사회자가 "명함 X인 분은 m번 자리로 옮겨 주세요"라고 지정하는 것과 같다.

<strong>Commanded Address</strong>는 외부 장치가 특정 ECU에게 주소를 강제로 지정하는 메커니즘이다. <strong>PGN 65240 (0xFED8)</strong>을 사용하며, 지원 여부는 <strong>선택 사항</strong>이다.

### 메시지 구조

![Commanded Address 9바이트 구조: Byte 1~8은 대상 NAME, Byte 9는 새 SA. 8바이트를 넘어 BAM으로 전송한다](/images/study-isobus/10-commanded-address-light.png)
![Commanded Address 9바이트 구조: Byte 1~8은 대상 NAME, Byte 9는 새 SA. 8바이트를 넘어 BAM으로 전송한다](/images/study-isobus/10-commanded-address-dark.png)

그림처럼 Byte 1~8에 명령을 받을 CF의 NAME이, Byte 9에 새로 쓸 주소가 들어간다. 대상을 주소가 아니라 NAME으로 가리키므로, 지금 어느 주소에 있든, 심지어 주소를 얻지 못한 CF에게도 명령이 닿는다(7절).

데이터가 9바이트라 단일 CAN 프레임(8바이트)에 담을 수 없으므로 <strong>BAM(Broadcast Announce Message) 전송 프로토콜로 Global(255)에 송신</strong>한다. 따라서 Commanded Address를 지원하는 장치는 BAM 수신도 지원해야 한다. BAM은 긴 데이터를 여러 프레임에 나눠 모두에게 보내는 방법이다([15장](/study/isobus/15-tp-bam-cmdt)).

### 동작 방식

다음 그림은 관리 장치(예: 진단기)가 NAME이 `0xABCD`인 ECU에게 새 SA `0x10`(=16)을 쓰라고 명령하는 흐름이다. 이 NAME도 설명용으로 줄인 값이다.

![Commanded Address 흐름: 관리 장치가 BAM으로 Commanded Address(NAME=0xABCD, New SA=0x10)를 보내면 대상 ECU가 자기 NAME과 일치하는지 확인하고 SA=0x10으로 Address Claimed를 보낸다](/images/study-isobus/13-commanded-address-flow-light.png)
![Commanded Address 흐름: 관리 장치가 BAM으로 Commanded Address(NAME=0xABCD, New SA=0x10)를 보내면 대상 ECU가 자기 NAME과 일치하는지 확인하고 SA=0x10으로 Address Claimed를 보낸다](/images/study-isobus/13-commanded-address-flow-dark.png)

1. 관리 장치가 Commanded Address(NAME=`0xABCD`, New SA=`0x10`)를 BAM으로 보낸다.
2. 버스의 모든 CF가 이 메시지를 받는다.
3. 대상 ECU는 Byte 1~8의 NAME이 자기 NAME(`0xABCD`)과 같은지 확인한다.
4. 같으면 SA=`0x10`으로 Address Claimed(NAME=`0xABCD`)를 보낸다. 이 클레임이 성공하면 SA를 `0x10`으로 바꾸는 일이 끝난다.

### 사용 사례

| 상황 | 설명 |
|------|------|
| 공장 설정 | 제조 라인에서 장치에 고정 SA 부여 |
| 네트워크 재구성 | 시스템 통합 시 주소 충돌 사전 방지 |
| 진단/유지보수 | 특정 SA로 장치를 강제 이동 |

Commanded Address를 수락한 ECU는 명령받은 주소를 새 SA로 하는 <strong>Address Claimed 메시지를 발행</strong>해야 하며, 이때 일반 주소 클레임 요구사항이 그대로 적용된다. 수신했지만 주소를 변경할 수 없는 ECU는 <strong>현재 SA를 클레임하는 Address Claimed로 응답</strong>한다.

<small>근거: ISO 11783-5:2019 4.4.2.5</small>

## 4. 주소 클레임 따라가기: 두 파종기 컨트롤러

앞 절들이 절차를 일반화해서 설명했다면, 여기서는 <strong>서로 다른 제조사의 작업기 ECU 2개가 같은 주소를 동시에 클레임해 충돌하고, NAME 비교로 승패가 갈린 뒤, 진 쪽이 다른 주소를 재클레임하는 전 과정</strong>을 시각(ms) 단위로 끝까지 따라간다.

### 등장인물: 두 파종기 컨트롤러의 NAME

두 CF 모두 파종기 컨트롤러다. device class 4(Planter)는 [12장](/study/isobus/12-j1939-address-name)의 NAME 조립 예 A.3에서 본 파종기 값이다. 둘 다 ISOBUS 적합 장치라 self-configurable(AAC=1)이다. Industry Group(농업 장비)·device class·Function까지 같아서, NAME이 갈리는 지점은 제조사 고유 필드(Manufacturer Code, Identity Number)뿐이다.

| 필드 | 비트 | CF A: 그린텍 파종기 컨트롤러 | CF B: 블루팜 파종기 컨트롤러 |
|------|------|------|------|
| Self-configurable address (AAC) | 1 | 1 (self-configurable) | 1 (self-configurable) |
| Industry Group (IG) | 3 | 2 (Agricultural) | 2 (Agricultural) |
| Device class instance (VSI) | 4 | 0 | 0 |
| Device class (VS) | 7 | 4 (Planter) | 4 (Planter) |
| Reserved | 1 | 0 | 0 |
| Function | 8 | 130 | 130 |
| Function Instance (FI) | 5 | 0 | 0 |
| ECU Instance (EI) | 3 | 0 | 0 |
| Manufacturer Code | 11 | 105 (그린텍) | 320 (블루팜) |
| Identity Number | 21 | 500000 | 250000 |

Function·Manufacturer Code·Identity Number의 실제 등록값은 isobus.net 데이터베이스(ISO 11783의 코드 값을 관리하는 공개 데이터베이스)가 관리하며 이 스터디의 부속서에는 실려 있지 않다. 위 표의 값은 필드 인코딩·비교 방식을 보여주기 위한 예시다. 이 값을 64비트로 이어 붙이면 다음과 같다.

```
NAME_A = 0xA00882000D27A120   (바이트: A0 08 82 00 0D 27 A1 20)
NAME_B = 0xA00882002803D090   (바이트: A0 08 82 00 28 03 D0 90)
```

NAME_A는 12장에서 비트 단위로 풀어 읽은 바로 그 값이다. 괄호 안의 바이트는 수치 표기 순서, 곧 Byte 8부터 Byte 1까지다.

### 타임라인: 충돌부터 재클레임까지

두 CF 모두 제조 시 저장된 initial address가 우연히 128(self-configurable 범위의 첫 주소)로 같다고 하자.

표 읽는 법: 시각은 두 CF가 Request를 보낸 순간을 0 ms로 잡았다. 한 줄이 한 사건이고, CAN ID `0x18EEFF80`의 끝 두 자리 `80`이 SA 128이다(12장).

| 시각(ms) | 송신자 | 메시지 (PGN, 데이터) | 버스 상태 | 판정 |
|------|------|------|------|------|
| 0 | CF A, CF B (각자) | Request for Address Claimed (PGN 59904, DA=255, 데이터=PGN 60928 조회) | 정상 송신 | 사용 중 주소 조회 시작: 각자 <strong>250 ms + RTxD</strong> 대기 진입 |
| 0~331.6 | CF A | (대기, RTxD_A = 136 × 0.6 ms = 81.6 ms) | 유휴: SA=128 클레임 수신 없음 | SA=128을 빈 주소로 판단 |
| 0~332.2 | CF B | (대기, RTxD_B = 137 × 0.6 ms = 82.2 ms) | 유휴: SA=128 클레임 수신 없음 | SA=128을 빈 주소로 판단 |
| 331.6 | CF A | Address Claimed (PGN 60928, CAN ID 0x18EEFF80, SA=128, DATA=NAME_A) | 정상 송신 | SA=128 클레임 시작 |
| 332.2 | CF B | Address Claimed (PGN 60928, CAN ID 0x18EEFF80, SA=128, DATA=NAME_B) | 정상 송신: RTxD 차이가 0.6 ms뿐이라 A의 클레임을 반영하기 전에 이미 자신의 클레임 전송에 들어간 상태 | SA=128 중복 클레임 발생 |
| 332.2 | CF A, CF B | (서로의 Address Claimed 수신) | SA=128 충돌 감지 | NAME 비교: `0xA00882000D27A120`(A) `<` `0xA00882002803D090`(B) → <strong>A 승, B 패</strong> |
| 332.2 | CF A | Address Claimed 재송신 (PGN 60928, SA=128, NAME_A) | 정상 송신 | 승자도 재송신해야 SA=128을 지킨다 |
| 332.2 | CF B | Address Claimed (PGN 60928, CAN ID 0x18EEFF81, SA=129, NAME_B) | 정상 송신 | AAC=1이므로 128~247 범위의 다음 빈 주소(129)를 즉시 재클레임 |
| 582.2 | - | 250 ms 동안 SA=128·SA=129 모두 경합 클레임 없음 | 유휴 | CF A는 SA=128, CF B는 SA=129 <strong>클레임 성공 확정</strong> |
| 582.2 이후 | CF A, CF B | 일반 메시지 송신 시작 | 정상 | 클레임 성공 후 250 ms 경과: 일반 통신 허용(Request 응답은 이 전에도 예외적으로 가능) |

대기 시간은 250 ms에 RTxD를 더한 값이다. A는 250 + 81.6 = 331.6 ms, B는 250 + 82.2 = 332.2 ms에 대기를 마친다. 두 RTxD가 한 단계(0.6 ms)만 달라서 둘 다 상대의 클레임을 반영하기 전에 같은 주소를 클레임했다.

### 승패 규칙: NAME을 64비트 정수로 통째 비교

NAME 비교는 각 필드를 개별로 견주는 것이 아니라, <strong>address-claimed 데이터 필드(8바이트) 전체를 하나의 정수로 취급해 비교</strong>한다. AAC를 최상위 비트로 놓고 이어 붙이면, 상위 필드가 같을 때만 하위 필드가 승패를 가른다.

이번 예시에서는 AAC·IG·VSI·VS·Reserved·Function·FI·EI가 완전히 같아 NAME의 앞 4바이트(`A0 08 82 00`)까지 일치한다. 갈리는 지점은 앞에서 5번째 바이트(12장의 바이트 번호로는 Byte 4), 즉 <strong>Manufacturer Code</strong>의 상위 8비트부터다. 그린텍은 `0x0D`(제조사 코드 105), 블루팜은 `0x28`(제조사 코드 320)이라 `0x0D < 0x28`이므로 그린텍(CF A)이 이긴다.

::: tip 핵심 통찰
NAME 비교는 상위 필드가 같으면 그대로 하위 필드로 내려가는 <strong>사전식(lexicographic) 비교</strong>다. 사전에서 첫 글자부터 견주고, 같으면 둘째 글자로 넘어가는 것과 같다. 그리고 self-configurable 비트(AAC)가 NAME의 <strong>최상위 비트</strong>이므로, 다른 필드가 전부 같더라도 AAC=0(non-configurable)인 CF는 AAC=1(self-configurable)인 CF를 항상 이긴다.
:::

### 패자의 행동: 재클레임 또는 Cannot Claim

패자(CF B)가 이후 무엇을 하는지는 <strong>AAC 값</strong>에 따라 갈린다.

| AAC | 패자의 행동 |
|------|------|
| 1 (self-configurable, 이번 시나리오) | 128~247 범위에서 다음 빈 주소를 골라 재클레임한다. 위 타임라인처럼 SA=129를 클레임하고, 250 ms 무경합을 확인하면 통신을 시작한다 |
| 0 (non-configurable) | 재클레임을 시도하지 않고 <strong>RTxD를 삽입한 뒤 Cannot Claim Address(PGN 60928, SA=254, 데이터=자신의 NAME)</strong>를 송신한다. 이후 Null Address 상태로 남아 request-for-address-claimed 응답과 commanded-address 처리 외에는 통신할 수 없다 |

이번 시나리오의 CF B는 ISOBUS 적합 장치라 AAC=1이므로 위 표의 첫 줄대로 SA=129를 재클레임한다.

### 타이밍 규정이 시나리오에 어떻게 적용되는가

이 타임라인에 실제로 반영된 2절의 타이밍 규칙은 세 가지다.

- <strong>주소 조회 후 대기</strong>: t=0에서 Request for Address Claimed를 보낸 뒤 최소 250 ms + RTxD를 기다린 다음에야 Address Claimed를 송신했다(t=331.6ms, 332.2ms).
- <strong>클레임 성공 판정</strong>: A와 B 모두 마지막 Address Claimed(t=332.2ms) 이후 250 ms 동안 경합이 없어야 성공이 확정된다(t=582.2ms).
- <strong>일반 통신 시작</strong>: 클레임 성공 확정(t=582.2ms) 이전에는 일반 메시지를 보낼 수 없다.

다음 코드는 두 NAME을 필드 값에서 직접 만들어 크기를 비교하고, 처음 갈리는 바이트와 두 CF의 대기 시간을 계산한다.

::: details 파이썬으로 검산해 보기
```python
FIELDS = [  # (필드명, 비트 수): AAC가 최상위
    ("aac", 1), ("ig", 3), ("vsi", 4), ("vs", 7), ("rsvd", 1),
    ("func", 8), ("fi", 5), ("ei", 3), ("mfg", 11), ("ident", 21),
]


def encode_name(**kw):
    val = 0
    for name, bits in FIELDS:
        v = kw[name]
        assert 0 <= v < (1 << bits)
        val = (val << bits) | v
    assert val.bit_length() <= 64
    return val


# CF A - 그린텍 파종기 컨트롤러
NAME_A = encode_name(aac=1, ig=2, vsi=0, vs=4, rsvd=0,
                      func=130, fi=0, ei=0, mfg=105, ident=500000)
# CF B - 블루팜 파종기 컨트롤러
NAME_B = encode_name(aac=1, ig=2, vsi=0, vs=4, rsvd=0,
                      func=130, fi=0, ei=0, mfg=320, ident=250000)

print(hex(NAME_A), NAME_A.to_bytes(8, "big").hex())   # 0xa00882000d27a120 a00882000d27a120
print(hex(NAME_B), NAME_B.to_bytes(8, "big").hex())   # 0xa00882002803d090 a00882002803d090
print("A < B:", NAME_A < NAME_B)                      # True -> CF A(그린텍) 승

a_bytes, b_bytes = NAME_A.to_bytes(8, "big"), NAME_B.to_bytes(8, "big")
for i, (x, y) in enumerate(zip(a_bytes, b_bytes)):
    if x != y:
        print(f"byte[{i}]에서 최초로 갈림: A=0x{x:02X} B=0x{y:02X}")  # byte[4]: A=0x0D B=0x28
        break

# RTxD(0~255 난수 x 0.6ms)로 만든 두 대기 시간
RTXD_A, RTXD_B = 136 * 0.6, 137 * 0.6
print("t_A =", 250 + RTXD_A, "ms /", "t_B =", 250 + RTXD_B, "ms")  # 331.6 / 332.2
```
:::

`NAME_A < NAME_B`가 `True`이므로 A가 이긴다. `byte[4]`는 0부터 센 번호라 앞에서 5번째 바이트, 곧 Byte 4다. 마지막 줄의 331.6과 332.2는 타임라인 표의 클레임 시각과 같다.

<small>근거: ISO 11783-5:2019 4.4.2.3, 4.4.2.4, 4.5.2, 4.5.4.2, Annex A.3</small>

## 5. 주소 구성 능력 네 가지 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

<strong>주소 구성 능력(address configuration capability)</strong>은 CF가 주소 클레임에 쓸 SA를 정하는 방식이다. 2~4절은 AAC 비트(0/1)로 두 가지만 나눴지만, ISO 11783-5(ISOBUS의 네트워크 관리 표준. 이하 Part 5)는 기본 능력 2가지와 확장 능력 2가지를 정의한다.

| 능력 | 구분 | NAME에 드러나나 | 주소를 바꾸는 방법 | 원하는 주소를 못 쓰면 |
|---|---|---|---|---|
| Non-configurable | 기본 | Self-configurable address 비트 = 0 | 주소 클레임 과정에서 initial address를 바꿀 수 없다 | Cannot Claim Address 송신 |
| Self-configurable | 기본 | Self-configurable address 비트 = 1 | 독자 알고리즘으로 주소를 다시 계산해 재클레임 | 다른 주소를 골라 재클레임. 128~247이 전부 찼을 때만 Cannot Claim |
| Service-configurable | 확장 | 드러나지 않음 | "service" 동작 모드에서 서비스 기사가 독자 방법이나 Commanded Address로 변경. 서비스 툴을 쓸 수 있다 | Cannot Claim Address 송신 |
| Command-configurable | 확장 | 드러나지 않음 | Commanded Address로 언제든 변경. 서비스 툴이나 특수 모드가 필요 없지만, 명령을 보낼 CF가 네트워크에 있어야 한다 | Cannot Claim Address 송신 |

쉽게 말하면 기본 능력은 "주소 다툼에서 졌을 때 스스로 옮겨 갈 수 있나"이고, 확장 능력은 "남이 주소를 바꿔 줄 수 있나"다. 표에서 구현자가 놓치기 쉬운 점은 다섯 가지다.

1. <strong>ISO 11783 적합 CF는 self-configurable이어야 한다(shall).</strong> non-configurable CF는 1판(ISO 11783-5:2001)이나 SAE J1939 장비와 호환하려고 네트워크에서 "용인(tolerate)"될 뿐이다.
2. <strong>확장 능력은 NAME에 표시되지 않는다.</strong> 12장에서 본 NAME 필드 가운데 그런 필드가 없다. 기본 능력과 별개로 CF는 확장 능력을 하나 이상 골라 구현할 수 있으므로, self-configurable이면서 command-configurable인 CF가 가능하다.
3. <strong>self-configurable CF가 initial address를 바꿔도 되는 때는 주소 중재에서 졌을 때뿐이다.</strong> 부팅할 때마다 새 주소를 고르는 구현은 이 규정에 어긋난다. 바꾼 주소는 다음 전원 인가부터 initial address로 쓰도록 저장한다.
4. <strong>self-configurable CF가 쓸 수 있는 주소는 128~247이다.</strong> 단, 그 CF의 기능에 preferred address가 배정되어 있으면 그 주소도 쓸 수 있다. 새 주소를 고르는 알고리즘은 CF 고유(proprietary)이지만, 결과는 반드시 자기 preferred address이거나 128~247 안이어야 한다.
5. <strong>non-configurable끼리 같은 주소를 다투면 NAME이 가장 작은 CF만 주소를 얻고, 나머지는 클레임 불가를 알려야 한다.</strong> non-configurable이 self-configurable을 언제나 이긴다는 점은 4절의 핵심 통찰에서 봤다.

::: tip 능력별로 구현해야 할 것
- Non-configurable: Address Claimed, Cannot Claim, Request 응답. 클레임 전 Request for Address Claimed는 생략할 수 있지만 보내는 것이 권장된다.
- Self-configurable: 위 전부 + 주소 재계산 + 새 initial address 저장.
- Command-configurable: 위에 더해 Commanded Address 수신 처리. Commanded Address는 BAM으로 오므로 BAM 수신도 필수다.
- Service-configurable: service 모드에 들어가는 방법과 그 모드에서의 주소 변경 수단(독자 방법 또는 Commanded Address).
:::

<small>근거: ISO 11783-5:2019 4.2.1~4.2.5, 4.3.3.4, 4.4.2.4, 4.4.2.5, 4.5.1, 4.5.3</small>

## 6. 주소 관리 메시지 네 가지를 프레임으로 보기

2절과 3절은 메시지의 역할을 설명했다. 이 절은 같은 네 메시지를 <strong>CAN ID·DLC·데이터 바이트</strong> 수준까지 내려가 다시 본다. 버스 로그에서 주소 클레임을 찾아 읽으려면 이 값들을 알아야 한다. 정의 전체는 ISO 11783-5(ISOBUS의 네트워크 관리 표준)를 정리한 [Part 5 부록](/study/isobus/appendix-iso-part05)에 있으니 여기서는 프레임을 실제로 조립할 때 필요한 값과 규칙에 집중한다.

### 네 메시지의 프레임 값

표 읽는 법: PF·PS·SA는 [9장](/study/isobus/09-j1939-message)에서 본 29비트 ID의 필드이고, DA는 목적지 주소다. DLC(Data Length Code)는 데이터 바이트 수다. 괄호 안의 `0x` 값은 같은 수의 16진수 표기다.

| 메시지 | PGN | 우선순위 | PF | PS | SA | DLC | 데이터 |
|---|---|---|---|---|---|---|---|
| Request for Address Claimed | 59904 (`0xEA00`) | 6 | 234 (`0xEA`) | DA: 255 또는 특정 주소 | 자기 SA. 클레임 전이면 254 | 3 | 요청 PGN 60928 → `00 EE 00` |
| Address Claimed | 60928 (`0xEE00`) | 6 | 238 (`0xEE`) | 255 | 0~253 | 8 | NAME (Byte 1부터) |
| Cannot Claim Address | 60928 (`0xEE00`) | 6 | 238 (`0xEE`) | 255 | 254 | 8 | NAME |
| Commanded Address | 65240 (`0xFED8`) | 6 | 254 (`0xFE`) | 216 (`0xD8`) | 명령하는 CF의 SA | 9바이트 → BAM | NAME + 새 SA |

Address Claimed와 Cannot Claim은 PGN이 같고 SA(254인지)로만 구별된다. Commanded Address는 PF가 240 이상인 PDU2라 PS 216은 목적지가 아니라 PGN의 일부(group extension)다. PDU2는 PS 칸을 목적지 대신 메시지 번호의 일부로 쓰는 형식이다(9장).

Request의 데이터 3바이트는 요청하는 PGN을 <strong>최하위 바이트부터</strong> 담는다. 60928 = `0x00EE00`이므로 `00 EE 00`이다. 아직 주소가 없는 CF가 전체에 묻는 Request는 다음 한 프레임이다.

```
CAN ID 0x18EAFFFE  DLC 3  00 EE 00
         │ │ │ └─ SA 0xFE (254, NULL)
         │ │ └─── DA 0xFF (Global)
         │ └───── PF 0xEA (Request)
         └─────── 0x18 = 우선순위 6, R 0, DP 0
```

위 그림처럼 CAN ID를 두 자리씩 끊어 읽는다. `18`은 우선순위 6이고, `EA`는 Request, `FF`는 목적지 Global, `FE`는 보낸 쪽이 아직 주소가 없다는 뜻(NULL 주소)이다.

4절의 그린텍 컨트롤러가 SA 0x80을 클레임하는 Address Claimed는 `0x18EEFF80`, DLC 8, 데이터 `20 A1 27 0D 00 82 08 A0`이다. NAME을 Byte 1부터 싣는 순서는 [12장](/study/isobus/12-j1939-address-name)에서 봤다. 같은 CF가 클레임에 실패했다면 Cannot Claim은 `0x18EEFFFE`에 같은 8바이트를 싣는다.

<small>근거: ISO 11783-5:2019 Table 2, 4.4.2.2~4.4.2.5, ISO 11783-3:2018 5.1.3, 5.4.3</small>

## 7. 받는 쪽의 응답 규칙과 주소를 못 얻은 CF (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

### 받는 쪽의 응답 규칙

| 상황 | 해야 할 일 |
|---|---|
| Global(255)로 온 Request for Address Claimed | Address Claimed로 응답한다. 클레임에 실패한 상태면 Cannot Claim으로 응답한다 |
| 자기 주소로 온 Request for Address Claimed | 응답하되 목적지는 <strong>Global(255)</strong>로 한다 |
| 아직 클레임을 시도한 적 없는 CF | 어떤 Request에도 응답하지 않고 Cannot Claim도 보내지 않는다. 그 전에는 Request for Address Claimed 말고는 통신에 참여하지 않는다 |
| 자기가 Global로 보낸 Request | 자기 요청에도 응답해야 한다 |
| 자기 SA를 클레임하는 Address Claimed 수신 | NAME을 비교해 이기면 자기 Address Claimed를 다시 보내고, 지면 새 주소를 클레임하거나 Cannot Claim을 보낸다 |
| Cannot Claim으로 응답할 때 | 트리거 메시지를 받은 뒤 RTxD만큼 기다렸다가 보낸다 |

셋째 줄과 넷째 줄은 함께 읽어야 한다. 클레임을 시도하기 전의 CF는 자기 요청에도 응답하지 않고, 2절의 대기(250 ms + RTxD)를 마친 뒤 Address Claimed를 보낸다.

둘째 줄이 대표적인 구현 함정이다. ISO 11783-3(메시지 형식과 요청·응답 규칙을 정하는 데이터 링크 계층 표준. 이하 Part 3)의 일반 규칙은 "특정 주소로 온 요청에는 특정 주소로 응답한다"인데([10장](/study/isobus/10-j1939-request-ack)), Address Claimed만은 요청이 특정 주소로 왔어도 Global로 보낸다. Part 3과 Part 5가 모두 이 예외를 직접 적어 두었다. Part 5는 그 이유도 밝힌다. 클레임 사실을 네트워크의 모든 CF에 알려야 하기 때문이다. 범용 Request 처리기에 PGN별 응답 함수를 붙이는 구조라면 PGN 60928만 따로 Global로 돌려야 한다.

### 주소를 못 얻은 CF가 할 수 있는 일

Cannot Claim을 보낸 CF의 송신 범위는 표준의 두 곳이 나눠서 정한다.

- Cannot Claim Address 메시지를 정의하는 곳: Cannot Claim Address와 Request for Address Claimed 말고는 보내지 않는다. 다만 Commanded Address 같은 Global 메시지의 수신·처리는 계속할 수 있다.
- 네트워크 초기화에서 클레임 실패를 다루는 곳: Request for Address Claimed에 응답하는 Cannot Claim과 Commanded Address에 대한 응답 말고는 보내지 않는다. 전원을 다시 켜면 클레임을 다시 시도할 수 있다.

두 규정을 합치면, 주소 없는 CF에게도 Commanded Address를 받아 새 주소로 클레임하는 길은 열려 있다. 표준이 서비스 툴(일부 시스템에서는 브리지, 곧 두 네트워크를 잇는 장치)에게 주소 클레임 실패를 감지·해결하는 역할을 기대하는 이유다. 서비스 툴은 Cannot Claim을 모니터링해 운용자에게 문제를 알릴 수 있다.

<small>근거: ISO 11783-5:2019 4.4.2.2~4.4.2.4, 4.5.2, 4.5.3, 4.5.5, ISO 11783-3:2018 5.4.3</small>

## 8. Commanded Address를 프레임으로 조립하기 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

3절의 Commanded Address는 9바이트라 BAM으로 나간다. 서비스 툴(SA 0x9A, 예시 값)이 4절의 CF B(블루팜 파종기 컨트롤러, NAME_B)에게 SA 0x95(149)를 쓰라고 명령하는 경우를 프레임으로 풀면 다음과 같다. BAM은 먼저 "이런 데이터를 몇 조각으로 보낸다"는 안내 프레임(TP.CM_BAM)을 보내고, 이어 조각 프레임(TP.DT)을 보낸다. TP.CM·TP.DT의 일반 구조는 [15장](/study/isobus/15-tp-bam-cmdt)에서 다룬다.

| 순번 | 프레임 | CAN ID | 데이터 | 의미 |
|---|---|---|---|---|
| 1 | TP.CM_BAM | `0x1CECFF9A` | `20 09 00 02 FF D8 FE 00` | Control `0x20`, 총 9바이트(`09 00`), 패킷 2개, 대상 PGN 65240(`D8 FE 00`) |
| 2 | TP.DT #1 | `0x1CEBFF9A` | `01 90 D0 03 28 00 82 08` | 순번 1 + NAME Byte 1~7 |
| 3 | TP.DT #2 | `0x1CEBFF9A` | `02 A0 95 FF FF FF FF FF` | 순번 2 + NAME Byte 8 + 새 SA `95` + `FF` 채움 |
| 4 | Address Claimed | `0x18EEFF95` | `90 D0 03 28 00 82 08 A0` | CF B가 새 주소 0x95로 클레임 |

TP.CM과 TP.DT는 운반하는 PGN과 상관없이 우선순위 7이라 CAN ID가 `0x1C`로 시작한다. 브로드캐스트 패킷 사이 간격은 10~200 ms다. 명령 대상은 Byte 1~8의 NAME으로 지정되므로, 수신 측은 9바이트를 다 모은 뒤 그 NAME이 자기 NAME과 같을 때만 Byte 9를 새 주소로 받아들이게 된다(해설).

데이터를 이어 보면 NAME이 어떻게 두 프레임에 나뉘는지 보인다. 2번 프레임의 순번 `01` 뒤 7바이트(`90 D0 03 28 00 82 08`)와 3번 프레임의 순번 `02` 뒤 첫 바이트(`A0`)를 이으면 NAME_B의 전송 순서 8바이트가 된다. 그다음 `95`가 Byte 9, 곧 새 주소다.

4번 프레임 전후의 규칙은 다음과 같다.

- 명령을 받아들인 CF는 새 SA로 Address Claimed를 보내고, 일반 클레임 요구사항이 그대로 적용된다. 250 ms 동안 경합이 없어야 하고 그 전에는 송신을 재개하지 않는다.
- 주소를 바꿀 수 없는 CF는 <strong>현재 SA를 클레임하는 Address Claimed</strong>로 응답한다. 그 뒤 운용자나 기사가 다른 방법으로 주소를 바꿀 수 있다. 서비스 툴은 응답 프레임의 SA가 명령한 0x95인지 원래 주소인지로 수락 여부를 가릴 수 있다(추론).
- ECU 제조사는 브리지·서비스 툴 외의 CF가 보낸 Commanded Address를 거부하거나, 수락 전에 보안 검증을 요구하도록 제품을 만들 수 있다.
- Commanded Address를 지원하는 CF는 BAM도 지원해야 한다.

::: info 주소-NAME 대응표
Request for Address Claimed로 모은 응답으로 <strong>주소-NAME 대응표</strong>를 만들 수 있다. 표준의 예는 변속기가 보내는 토크·속도 제어 메시지가 올바른 목적지로 가도록, 구동계 엔진이 정말 주소 0에 있는지 표로 확인하는 경우다. 필요한 대응이 몇 개뿐이면 특정 주소로, 진단 툴처럼 네트워크 전체를 볼 때는 Global로 요청한다.

VT·TC 서버를 구현한다면 이 표를 상시 유지하는 편이 좋다. 표준은 클레임에 실패한 CF와 통신하던 CF가, 그 CF의 Cannot Claim과 주소를 가로챈 상위 우선순위 CF의 Address Claimed를 지켜보고 상대가 "disabled"(더는 통신할 수 없는 상태)되었음을 알아챌 수 있어야 한다고 요구한다. 세션을 SA가 아니라 NAME에 묶어 두면, 같은 SA에 다른 NAME이 나타났을 때 이전 클라이언트가 사라졌음을 바로 판단할 수 있다.
:::

::: details 원문을 가진 독자를 위한 메모
- 주소를 못 얻은 CF의 송신 범위를 정한 두 곳은 ISO 11783-5:2019 4.4.2.4와 4.5.5다.
- Address Claimed를 Global로 응답하는 예외는 ISO 11783-3:2018 5.4.3과 ISO 11783-5:2019 4.5.2 b)에 있다.
- TP.CM·TP.DT의 우선순위는 ISO 11783-3:2018 5.10.4, 5.10.5, 브로드캐스트 패킷 간격은 5.10.2.4, 5.13.3이다.
- 주소-NAME 대응표의 예는 ISO 11783-5:2019 Annex A.4, disabled 감지 요구는 4.5.3이다.
:::

<small>근거: ISO 11783-5:2019 4.4.2.5, 4.5.2, 4.5.3, Annex A.4, ISO 11783-3:2018 5.10.2.4, 5.10.4, 5.10.5, 5.13.3</small>

::: tip 핵심 정리
- CF는 Request for Address Claimed로 사용 중인 주소를 묻고, 최소 250 ms + RTxD를 기다린 뒤 빈 주소로 Address Claimed(PGN 60928)를 Global로 보낸다. RTxD는 난수(0~255) × 0.6 ms다.
- 같은 주소를 두 CF가 클레임하면 NAME을 64비트 정수로 비교해 작은 쪽이 이긴다. 이긴 쪽도 Address Claimed를 다시 보낸다.
- 진 쪽은 AAC=1이면 128~247에서 다른 주소를 클레임하고, AAC=0이면 RTxD 뒤 Cannot Claim Address(SA 254)를 보낸다. ISO 11783 적합 CF는 self-configurable이어야 한다.
- Address Claimed를 보낸 뒤 250 ms 동안 경합이 없어야 성공이고, 그 전에는 Request 응답 말고는 보내지 않는다.
- Commanded Address(PGN 65240)는 NAME 8바이트와 새 SA 1바이트로 9바이트라 BAM으로 Global에 보낸다.
- 특정 주소로 온 Request에도 Address Claimed는 Global로 응답한다. 요청·응답 일반 규칙(10장)의 예외다.
:::

::: details 확인 문제
1. (개념) 주소 클레임에서 RTxD를 넣는 이유는 무엇인가? RTxD가 가질 수 있는 가장 짧은 값과 가장 긴 값은?
2. (개념) AAC가 0인 CF와 AAC가 1인 CF가 같은 주소를 클레임했다. 나머지 필드를 보지 않고도 승자를 알 수 있는 이유는?
3. (개념) Address Claimed와 Cannot Claim Address는 PGN이 같다. 버스 로그에서 둘을 어떻게 구별하는가?
4. (계산) 4절 시나리오에서 CF B의 RTxD 난수가 137이 아니라 200이었다면 결과는 어떻게 달라지는가? 두 Request는 모두 Global로 보냈다.
5. (프레임) 주소 클레임을 마친 CF A(SA 0x80)에게 다른 CF가 목적지를 0x80으로 해서 Request for Address Claimed를 보냈다. CF A가 보내는 응답의 CAN ID는 무엇인가?

**답 가이드**
1. 같은 때 전원을 받은 CF들이 같은 순간에 송신해 충돌하는 것을 막기 위해서다. 난수가 0~255이므로 RTxD는 0 × 0.6 = 0 ms부터 255 × 0.6 = 153 ms까지다.
2. AAC가 NAME의 최상위 비트이기 때문이다. AAC=0인 NAME은 AAC=1인 NAME보다 언제나 작아서, 나머지 필드와 상관없이 AAC=0인 CF가 이긴다.
3. 소스 주소로 구별한다. Cannot Claim Address는 SA가 254(`0xFE`)이므로 CAN ID가 `0x18EEFFFE`이고, Address Claimed는 SA가 0~253이다.
4. B의 RTxD는 200 × 0.6 = 120 ms라 B는 370 ms까지 기다린다. 그 사이 331.6 ms에 A의 Address Claimed(SA 128)를 받으므로 128이 쓰인다는 것을 안다. 대기가 끝난 370 ms에 128이 아닌 빈 주소(예: 129)를 클레임하므로 NAME 비교 없이 끝난다. B의 클레임 성공은 370 + 250 = 620 ms다.
5. `0x18EEFF80`이다. 특정 주소로 온 Request라도 Address Claimed는 목적지를 Global(`FF`)로 해서 보낸다.
:::

## 다음 챕터

- 다음: [14장 NAME 관리와 네트워크 초기화](/study/isobus/14-name-management-init)
