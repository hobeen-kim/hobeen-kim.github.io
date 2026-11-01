---
title: "ISOBUS 네트워크 관리와 Working Set"
description: "ISOBUS 장치가 주소를 정하고, 작업기 안의 여러 ECU를 Working Set이라는 팀으로 묶어 VT·TC 앞에 한 대의 작업기로 나서는 과정을 시간 순서로 따라간다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, AddressClaim, WorkingSet]
prev: /study/isobus/25-settings-safety-messages
next: /study/isobus/27-diagnostics-identification
---

# ISOBUS 네트워크 관리와 Working Set

::: info 학습 목표
- CF(Control Function)가 무엇인지, ISOBUS 장치가 주소 클레임으로 주소를 정하는 흐름을 설명할 수 있다.
- Working Set이 왜 필요한지, master와 member가 각각 무슨 일을 하는지 설명할 수 있다.
- 전원을 켠 뒤 주소 확정, Working Set 선언, VT 연결, TC 연결이 어떤 순서로 얼마 만에 이어지는지 설명할 수 있다.
- Working Set Master·Member 메시지의 바이트를 읽고, 정의가 빠졌을 때 다시 요청하고 포기하는 규칙을 적용할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [12장 주소와 NAME](/study/isobus/12-j1939-address-name), [13장 주소 클레임](/study/isobus/13-j1939-address-claim), [18장 ISOBUS 개요](/study/isobus/18-isobus-overview)
- 이 장에서 처음 나오는 말
  - CF(Control Function): 주소 하나를 갖고 네트워크에 참여하는 통신 주체. ECU 한 대 안에 여러 개가 있을 수 있다.
  - Working Set: 작업기 안의 여러 CF를 한 팀으로 묶은 것.
  - master: Working Set을 대표해 바깥과 이야기하는 CF. 팀장에 해당한다.
  - member: master와 같은 팀에 속한 나머지 CF. 팀원에 해당한다.
  - service provider: Working Set 바깥에서 Working Set에 서비스를 주는 CF. VT(트랙터 화면)와 TC(작업 컨트롤러)가 대표적이다.
:::

큰 작업기 하나에는 ECU(전자 제어 장치)가 여러 개 들어간다. 그런데 운전석의 화면(VT)이나 작업 컨트롤러(TC)는 ECU 하나하나가 아니라 "이 파종기" 한 대와 이야기하고 싶다. 회사에서 다른 부서와 일할 때 팀장이 팀을 대표해 이야기하듯, ISOBUS는 작업기 안의 ECU들을 Working Set이라는 팀으로 묶고 팀장 한 명을 대표로 세운다. 이 장은 장치가 주소를 정하는 단계부터 팀이 꾸려지고 화면이 뜨기까지를 시간 순서로 따라간다.

## 1. 주소 클레임: ISOBUS 장치가 주소를 정하는 방식

버스에서 메시지를 주고받으려면 장치마다 겹치지 않는 주소가 있어야 한다. 이 절은 ISOBUS가 주소를 정하는 방식을 다시 짚는다. 절차 자체는 [13장](/study/isobus/13-j1939-address-claim)에서 자세히 다뤘으니, 여기서는 ISOBUS에서 쓰는 이름과 규칙 위주로 본다.

ISOBUS의 주소 클레임은 J1939의 방식을 기반으로 하되, 농업 기계에 맞게 확장된 규칙을 적용한다.

### CF (Control Function)

ISOBUS에서는 네트워크에 참여하는 모든 통신 주체를 <strong>CF(Control Function)</strong>라고 부른다. 하나의 물리적 ECU가 여러 CF를 포함할 수도 있다. 각 CF는 독립적인 주소를 가진다.

건물 한 채에 회사 여러 곳이 입주해 각자 우편 주소를 갖는 것과 비슷하다. 건물이 ECU, 회사가 CF다. 예를 들어 트랙터의 ECU 한 대가 트랙터 ECU 기능과 VT 기능을 함께 맡으면, 버스에는 주소가 다른 CF 두 개가 보인다.

### 주소 범위

주소는 1바이트라 0~255 가운데 하나다. 범위마다 쓰임이 정해져 있다.

| 주소 범위 | 용도 |
|-----------|------|
| 0 ~ 127 | Preferred 주소 영역 (특정 기능에 할당) |
| 128 ~ 247 | <strong>Self-Configurable 주소</strong> (동적 협상) |
| 248 ~ 253 | Preferred 주소 영역 (특정 기능에 할당) |
| 254 | Null Address (소스 주소 전용: 클레임 전·실패 시 네트워크 관리 메시지에 사용) |
| 255 | Global Address (목적지 주소 전용: 브로드캐스트) |

- Preferred 주소는 "이 기능이면 이 주소를 먼저 써라"라고 미리 정해 둔 자리다.
- Null Address(254)는 아직 주소가 없는 CF가 보내는 쪽 주소(SA, Source Address) 칸에 쓰는 값이다.
- Global Address(255)는 받는 쪽 주소 칸에 써서 "모두에게"를 뜻한다.

ISOBUS 작업기 ECU는 대부분 <strong>128~247</strong> 범위의 self-configurable 주소를 쓴다. self-configurable은 원하던 주소를 다른 장치에 내주게 되면 스스로 다른 빈 주소를 골라 다시 신청할 수 있다는 뜻이다. 이 범위의 주소는 여러 장치가 동시에 원할 경우 NAME 값의 우선순위로 자동 협상된다. NAME은 장치마다 붙은 64비트 이름표이고, 값이 작을수록 우선순위가 높다([12장](/study/isobus/12-j1939-address-name)).

ISO 11783-5(주소와 NAME을 정하는 표준 문서)는 규격을 따르는 CF에 <strong>self-configurable 능력을 필수</strong>로 요구한다. 주소를 바꿀 수 없는 non-configurable CF는 구판·SAE J1939 호환을 위해 허용될 뿐이다.

### 주소 클레임 흐름

두 ECU가 같은 주소 128을 원하는 상황을 그림으로 보자. 가운데 세로줄이 버스다. 버스에 보낸 메시지는 모든 장치가 함께 듣는다.

![ECU A와 ECU B가 각각 SA 254로 주소 128을 조회하고 250 ms + RTxD를 기다린 뒤 둘 다 128을 클레임해 충돌하자, NAME이 낮은 ECU A가 128을 다시 보내 확정하고 ECU B는 129로 다시 클레임하는 시퀀스](/images/study-isobus/26-address-claim-flow-light.png)
![ECU A와 ECU B가 각각 SA 254로 주소 128을 조회하고 250 ms + RTxD를 기다린 뒤 둘 다 128을 클레임해 충돌하자, NAME이 낮은 ECU A가 128을 다시 보내 확정하고 ECU B는 129로 다시 클레임하는 시퀀스](/images/study-isobus/26-address-claim-flow-dark.png)

1. 두 ECU가 각자 Request for Address Claimed를 보낸다. 이 메시지는 "주소를 원한다"는 요구가 아니라 <strong>해당 주소(또는 전체)의 클레임 상태를 조회</strong>하는 메시지다. 클레임 전의 CF는 SA를 NULL(254)로 하여 보낸다.
2. 최소 <strong>250 ms + RTxD</strong>를 기다린다. RTxD는 0~255 가운데 무작위로 고른 수에 0.6 ms를 곱한 지연(0~153 ms)이다. 여러 장치가 같은 순간에 말을 꺼낼 가능성을 줄이려고 기다리는 시간을 무작위로 늘린다.
3. 응답이 없으면 클레임을 진행해 Address Claimed(128)를 보낸다. 그림처럼 둘이 동시에 128을 클레임하면 충돌이다.
4. NAME 수치가 낮은 쪽(ECU A)이 우선권을 얻는다. ECU A는 Address Claimed(128)를 다시 보내 주소를 지킨다. 진 쪽(ECU B)은 self-configurable이라 다른 빈 주소(129)로 다시 클레임한다.
5. Address Claimed 송신 후 <strong>250 ms 동안</strong> 경합 클레임이 없어야 성공이며, 이 250 ms가 지나기 전에는 일반 메시지 송신을 시작할 수 없다(Request for Address Claimed에 대한 응답은 예외).

쓸 수 있는 주소가 하나도 없으면 어떻게 될까? 그때 보내는 것이 <strong>Cannot Claim Address</strong>다. NULL 주소(SA=254)로 보내는 실패 보고 메시지다. 이를 보낸 CF는 이후 Cannot Claim Address와 Request for Address Claimed 외에는 아무 메시지도 보내지 않는다.

정리하면, ISOBUS 장치는 주소를 "조회하고, 기다리고, 신청하고, 250 ms 동안 반론이 없는지 지켜보는" 순서로 정한다. 다툼은 NAME 값으로 가린다.

## 2. Working Set: 작업기 하나를 대표하는 팀

주소를 정한 CF들은 이제 각자 버스에서 말할 수 있다. 그런데 작업기 하나에 CF가 여럿이면 VT와 TC는 누구와 이야기해야 할까? 이 절은 그 답인 Working Set을 본다.

작업기(Implement)는 내부에 여러 ECU를 포함할 수 있다. 예를 들어 파종기(Seeder)는 메인 제어 ECU, 섹션 밸브 ECU, 속도 센서 ECU를 각각 가질 수 있다. 이 ECU들을 하나의 논리적 단위로 묶는 것이 <strong>Working Set</strong>이다.

### 팀과 팀장으로 이해하기

Working Set은 회사의 팀과 닮았다.

| 회사 | ISOBUS | 하는 일 |
|---|---|---|
| 팀 | Working Set | 같은 작업기를 위해 일하는 CF들의 묶음 |
| 팀장 | Working Set Master(이하 master) | 팀을 대표해 바깥 부서(VT, TC)와 이야기한다 |
| 팀원 | Working Set member(이하 member) | master와 같은 팀에서 각자 맡은 일을 한다 |
| 팀원 명단 제출 | Working Set Master·Member 메시지 | 팀장이 혼자서 "우리 팀은 몇 명이고 누구누구다"를 알린다 |

비유가 맞지 않는 곳도 있다. 회사 팀원은 바깥 부서와 직접 이야기하지 않기도 하지만, member는 필요하면 VT에 직접 메시지를 보내도 된다(5절). 반대로 TC의 명령은 master에게만 간다.

### master와 member의 관계

![파종기 Working Set 안에 master(메인 ECU, 주소 132)와 member 셋(섹션 밸브 ECU 133, 속도 센서 ECU 134, 비료 탱크 ECU 135)이 있고, 바깥의 VT는 UI 데이터 요청을, TC는 섹션 명령을 master에게 보내는 구조](/images/study-isobus/26-working-set-team-light.png)
![파종기 Working Set 안에 master(메인 ECU, 주소 132)와 member 셋(섹션 밸브 ECU 133, 속도 센서 ECU 134, 비료 탱크 ECU 135)이 있고, 바깥의 VT는 UI 데이터 요청을, TC는 섹션 명령을 master에게 보내는 구조](/images/study-isobus/26-working-set-team-dark.png)

그림의 파종기는 master 하나(주소 132)와 member 셋(주소 133~135)으로 이루어진다. VT는 화면에 띄울 데이터를, TC는 섹션 명령을 master에게 보낸다. master가 member에게 일을 나눠 주는 안쪽 화살표는 예시일 뿐이다. 그 방법은 표준이 정하지 않는다.

### Working Set 선언 메시지 (PGN 65037, 65036)

master는 주소 클레임을 마친 뒤 <strong>PGN 65037(Working Set Master 메시지)</strong>를 브로드캐스트하여 자신이 master임을 선언한다. 이 메시지에는 Working Set에 속한 멤버 수(master 자신 포함)가 포함된다.

member 식별용 <strong>PGN 65036(Working Set Member 메시지)</strong>도 member가 아니라 <strong>master가</strong> 송신한다. master는 멤버 수 − 1개의 Member 메시지를 각 member의 NAME을 담아 <strong>100 ms 간격</strong>으로 보내고, 수신 측은 마지막 Member 메시지 후 350 ms가 지나면 Working Set 정의가 완료된 것으로 간주한다.

VT와 TC는 이 메시지들을 수신하여 작업기의 구조를 파악하고, Working Set 대상 통신 대부분을 master의 주소로 보낸다. 특히 TC의 명령은 master에게만 전달되며, master가 member에게 명령을 전파하는 방법은 각 Working Set의 고유(proprietary) 설계 영역이다.

정리하면, Working Set은 "팀장 한 명이 팀 명단을 내고 팀을 대표하는" 구조다. 명단은 두 종류의 메시지로 나가며 둘 다 master가 보낸다.

## 3. 전원을 켜고 통신이 자리 잡기까지

주소 클레임과 Working Set 선언은 전원을 켤 때마다 일어난다. 이 절은 전원을 켠 순간부터 ISOBUS 통신이 완전히 확립될 때까지의 시간 흐름을 따라간다. 출근해서 사원증을 찍고(주소 확정), 팀 명단을 내고(Working Set 선언), 회의실 화면을 켜고(VT 연결), 다른 부서와 업무를 시작하는(TC 연결) 순서와 비슷하다.

![전원 ON부터 약 7초까지의 타임라인. 주소 정하기 줄은 Request 후 250 ms + RTxD 대기, 300 ms에 Address Claimed 송신, 250 ms 경합 감시를 거쳐 550 ms에 주소 확정. VT 줄은 VT Status 수신 뒤 1.2~1.5 s에 Object Pool 전송. Working Set 줄은 600 ms에 Master 메시지, 100 ms 간격 Member 메시지를 거쳐 1 s에 구성 완료. TC 줄은 주소 클레임 뒤 6 s 대기 후 Device Descriptor 교환을 거쳐 약 7 s에 정상 동작](/images/study-isobus/26-startup-timeline-light.png)
![전원 ON부터 약 7초까지의 타임라인. 주소 정하기 줄은 Request 후 250 ms + RTxD 대기, 300 ms에 Address Claimed 송신, 250 ms 경합 감시를 거쳐 550 ms에 주소 확정. VT 줄은 VT Status 수신 뒤 1.2~1.5 s에 Object Pool 전송. Working Set 줄은 600 ms에 Master 메시지, 100 ms 간격 Member 메시지를 거쳐 1 s에 구성 완료. TC 줄은 주소 클레임 뒤 6 s 대기 후 Device Descriptor 교환을 거쳐 약 7 s에 정상 동작](/images/study-isobus/26-startup-timeline-dark.png)

그림 가운데 1.6~6.4 s 구간은 아무 일도 없어 접어 두었다. 그림과 표에 처음 나오는 말은 다음과 같다.

- VT Status: VT가 1초마다 방송하는 "VT가 여기 있다"는 메시지다([29장](/study/isobus/29-vt-basics)). master는 이 메시지가 보이기를 기다린 뒤 Working Set을 VT에 알린다([31장](/study/isobus/31-vt-connection)).
- Object Pool: 작업기가 VT 화면에 띄울 버튼, 숫자 칸, 그림을 한데 묶은 데이터다([32장](/study/isobus/32-vt-object-pool-basics)).
- Device Descriptor: 작업기가 TC에게 자기 구조(붐, 섹션, 측정값 같은 것)를 알리는 데이터다. DDOP(Device Descriptor Object Pool)라고도 부른다([48장](/study/isobus/48-ddop-basics)).
- 클라이언트: TC의 서비스를 받는 쪽, 즉 작업기 쪽 CF다.

### 타임라인 요약

| 시점 | 이벤트 |
|------|--------|
| 0 ms | 전원 ON, 버스 전압 안정화 |
| ~50 ms | 각 ECU가 Request for Address Claimed 송신, 250 ms + RTxD 대기 시작 |
| ~300 ms | Address Claimed 송신 |
| ~550 ms | 250 ms 동안 경합 없음 확인: 주소 확정, 일반 통신 시작 |
| ~550 ms | VT Status 수신 시작: master는 이것을 기다린 뒤에 Working Set을 VT에 알린다 |
| ~600 ms | master가 Working Set 선언 (PGN 65037) 후 Member 메시지(PGN 65036)를 100 ms 간격 송신 |
| ~1,000 ms | Working Set 구성 완료 |
| ~1,500 ms | Object Pool 전송 완료, 화면 표시 시작 |
| ~7,000 ms | TC Device Descriptor 완료, 전체 통신 확립. TC와 클라이언트는 주소 클레임 뒤 6 s를 기다린 다음에야 연결을 시작한다 |

TC 연결이 VT 연결보다 한참 늦은 까닭은 6 s 대기 규칙이다. TC는 클라이언트가 보내는 주기 메시지가 6 s 동안 끊기면 클라이언트가 꺼진 것으로 본다. 클라이언트가 주소 클레임 뒤 6 s를 쉬어 주면, TC는 이 공백을 보고 클라이언트가 다시 시작했다는 것을 알아챌 수 있다. 연결 절차는 [43장](/study/isobus/43-tc-connection)에서 자세히 본다.

::: info 실제 현장에서의 차이
Object Pool 크기, ECU 수, 버스 부하에 따라 타임라인은 달라진다. 복잡한 작업기의 경우 Object Pool 전송만 수 초가 걸릴 수 있다. 250 ms, 100 ms, 350 ms, 6 s는 표준이 정한 값이고, 전원 안정화(50 ms)나 Object Pool 전송 시간은 이해를 돕는 예시 값이다.
:::

정리하면, 전원을 켜고 약 0.55초에 주소가 정해지고, 1초 안팎에 Working Set이 꾸려지며, 1.5초쯤 VT 화면이 뜬다. TC는 6초를 기다린 뒤 연결하므로 7초쯤에야 모든 통신이 자리 잡는다.

<small>근거: ISO 11783-6 4.6.6.2, ISO 11783-10 6.6.1 b), 6.6.2 b)</small>

## 4. Working Set 구성 따라가기

2절이 Working Set의 개념을 다뤘다면, 여기서는 <strong>ECU 3개로 이루어진 작업기가 Working Set을 선언하는 과정</strong>을 메시지 하나하나 끝까지 따라간다. 대상은 스프레이어(방제기) 작업기이며, 메인 컨트롤러가 좌·우 두 분무 섹션 컨트롤러를 거느린다.

### 구성

세 CF 모두 1절의 절차로 <strong>이미 주소 클레임을 마친 상태</strong>에서 이 절이 시작된다. 즉 여기서 다루는 건 클레임 이후, Working Set을 선언하는 단계만이다.

| CF | 역할 | SA (주소) | Working Set에서의 위치 |
|---|---|---|---|
| 메인 컨트롤러 | 스프레이어 전체 제어, VT·TC와 통신 | 0x90 (144) | Working Set Master |
| 좌측 섹션 컨트롤러 | 좌측 분무 섹션 개폐 | 0x91 (145) | Member 1 |
| 우측 섹션 컨트롤러 | 우측 분무 섹션 개폐 | 0x92 (146) | Member 2 |

`0x90`처럼 앞에 `0x`가 붙은 값은 16진수다. 괄호 안이 같은 값의 10진수다.

### 타임라인

Working Set 정의에는 두 메시지가 필요하다. 크기를 알리는 <strong>Working Set Master 메시지(PGN 65037)</strong>와 member를 식별하는 <strong>Working Set Member 메시지(PGN 65036)</strong>다. <strong>둘 다 master가 보낸다.</strong>

| t (ms) | 송신 CF | 메시지 (PGN, 8바이트 데이터) | 의미 |
|---|---|---|---|
| 0 | 메인 컨트롤러 (SA 0x90) | PGN 65037, `03 FF FF FF FF FF FF FF` | Working Set 크기 선언: 멤버 3명(master 자신 포함) |
| 100 | 메인 컨트롤러 (SA 0x90) | PGN 65036, `00 00 A8 82 00 80 0C A0` | 좌측 섹션 컨트롤러의 NAME 통지 |
| 200 | 메인 컨트롤러 (SA 0x90) | PGN 65036, `00 00 A8 82 01 80 0C A0` | 우측 섹션 컨트롤러의 NAME 통지 |
| 550 | (없음: 수신측 타임아웃) |  | 마지막 member 메시지 후 <strong>350 ms</strong> 경과, Working Set 구성 완료로 판정 |

t=100과 t=200 사이의 100ms 간격은 규격이 정한 값이다. 반면 t=0(master 메시지)에서 t=100(첫 member 메시지)까지의 간격은 표준에 규정이 없다. 위 표는 이해를 돕기 위해 같은 100ms 주기를 그대로 이어 쓴 예시일 뿐이다.

### 메시지 바이트 뜯어보기

아래 표에서 Byte 번호는 1부터 센다. CAN 프레임의 데이터 8바이트 가운데 맨 앞이 Byte 1이다.

<strong>Working Set Master 메시지 (PGN 65037)</strong>

| Byte | 값 | 의미 |
|---|---|---|
| 1 | `03` | Working Set 멤버 수: <strong>master 자신을 포함</strong>한 값. "member 2개 + master"이므로 `2`가 아니라 `3`이다 |
| 2~8 | `FF FF FF FF FF FF FF` | Reserved |

Reserved(예약)는 아직 쓰임이 정해지지 않은 칸이다. 보낼 때는 모든 비트를 1로 채우므로 `FF`가 된다(5절).

<strong>Working Set Member 메시지 (PGN 65036)</strong>

| Byte | 값 | 의미 |
|---|---|---|
| 1~8 | 해당 member의 NAME (8바이트) | 그 member가 주소를 클레임할 때 쓴 것과 동일한 NAME |

NAME은 Byte 1이 최하위 바이트다. 즉 낮은 자리 바이트가 먼저 온다. 좌측 컨트롤러의 NAME `00 00 A8 82 00 80 0C A0`을 높은 자리인 Byte 8부터 풀어 보자. NAME 필드의 전체 배치는 [12장](/study/isobus/12-j1939-address-name)에 있다. 바이트 안의 비트 번호는 8이 가장 높은 자리, 1이 가장 낮은 자리다.

| Byte | 값 | 2진수 | 읽은 결과 |
|---|---|---|---|
| 8 | `A0` | `1010 0000` | bit 8 = `1`: self-configurable(AAC) 1. bit 7~5 = `010`: industry group 2(농업 장비). bit 4~1 = `0000`: device class instance 0 |
| 7 | `0C` | `0000 1100` | bit 8~2 = `0000110`: device class 6(Sprayers, 방제기). bit 1 = `0`: 예약 비트 0 |
| 6 | `80` | `1000 0000` | function 128 |
| 5 | `00` | `0000 0000` | bit 8~4 = `00000`: function instance 0. bit 3~1 = `000`: ECU instance 0 |
| 1~4 | `00 00 A8 82` | | identity number와 manufacturer code (예시 값) |

우측은 Byte 5만 `01`(ECU instance 1)로 다르다. 한 function을 ECU 두 개가 맡으면 ECU instance를 0과 1로 두라는 것이 ISO 11783-5의 권고이고, 이 예는 그 표준의 예시를 따른 것이다. function 128은 예시 값이다. 128 이상의 function 코드는 device class에 따라 뜻이 달라지고, 실제 코드는 isobus.net 데이터베이스가 관리한다. Byte 1~4의 identity number와 manufacturer code도 예시 값이다.

master가 보내는 member 메시지의 개수는 <strong>멤버 수 − 1</strong>, 즉 3 − 1 = 2개다. master 자신의 NAME은 별도 메시지 없이 master의 주소 클레임 메시지에서 이미 알 수 있으므로 다시 보내지 않는다.

여기서 CAN ID를 보면 흥미로운 점이 하나 있다. PGN 65037 메시지와 두 PGN 65036 메시지 모두 <strong>Source Address가 0x90(메인 컨트롤러)으로 동일</strong>하다. 송신자가 항상 master이기 때문이다. master 메시지의 CAN ID는 `0x1CFE0D90`이고, 두 member 메시지는 CAN ID까지 `0x1CFE0C90`으로 같으며 데이터(NAME)만 다르다. `0x1CFE0D90`을 29비트 ID 구조([9장](/study/isobus/09-j1939-message))로 풀면 priority 7, PGN 65037(`0xFE0D`), SA `0x90`이다.

### 타이밍 규정

- member 메시지 간격: <strong>100 ms</strong>
- 완료 판정: 마지막 member 메시지 후 <strong>350 ms</strong> 경과 시 수신측(service provider)은 master가 모든 member NAME 송신을 마쳤다고 간주한다
- 실패 시: 정확한 개수의 member 메시지를 받지 못한 service provider는 master에게 PGN 65037을 재요청해야 하고, master는 요청을 받으면 master 메시지 + member 메시지 전체를 다시 보낸다. 응용 계층에 별도 규정이 없다면 <strong>최소 3회</strong> 완전한 member 목록 확보에 실패한 service provider는 해당 Working Set을 무시할 수 있다

### 흔한 오해 정정

member 메시지를 <strong>각 member ECU가 직접 보낸다</strong>고 생각하기 쉽지만, 실제로는 <strong>master가 대신 보낸다</strong>. 위 타임라인의 세 프레임, 즉 PGN 65037 1개와 PGN 65036 2개는 모두 SA 0x90(메인 컨트롤러)에서 나간다. 좌·우 섹션 컨트롤러(SA 0x91, 0x92)는 이 과정에서 <strong>아무 메시지도 보내지 않는다.</strong> 이들의 존재는 오직 master가 실어 보내는 NAME 바이트를 통해서만 네트워크에 드러난다.

::: tip 핵심 통찰
Working Set Master 메시지의 Byte 1은 "멤버 수(master 포함)"이지 "master 아닌 멤버 수"가 아니다. 그리고 이어지는 member 메시지의 개수는 그 값에서 1을 뺀 값이며, 두 메시지 모두 <strong>master의 SA</strong>로 나간다. 이 두 가지를 헷갈리면 Working Set 구성 로직이 어긋난다.
:::

아래 코드는 위 세 프레임의 CAN ID와 데이터를 계산하고, NAME 풀이와 member 메시지 수, 완료 시각을 확인한다.

::: details 파이썬으로 검산해 보기
```python
PRIORITY = 7                     # ISO 11783-7 B.23.2/B.23.3: 두 메시지 모두 priority 7
PF_MASTER, PS_MASTER = 0xFE, 0x0D  # PGN 65037 (0x00FE0D): Working Set Master
PF_MEMBER, PS_MEMBER = 0xFE, 0x0C  # PGN 65036 (0x00FE0C): Working Set Member


def can_id(priority, pf, ps, sa):
    return (priority << 26) | (pf << 16) | (ps << 8) | sa


MASTER_SA = 0x90                 # 메인 컨트롤러
MEMBER_SAS = [0x91, 0x92]        # 좌측·우측 섹션 컨트롤러 (참고용, 메시지 자체엔 SA가 실리지 않음)
NUM_MEMBERS = 1 + len(MEMBER_SAS)  # 마스터 자신 포함 = 3

NAME_LEFT  = [0x00, 0x00, 0xA8, 0x82, 0x00, 0x80, 0x0C, 0xA0]
NAME_RIGHT = [0x00, 0x00, 0xA8, 0x82, 0x01, 0x80, 0x0C, 0xA0]


def name_fields(name):           # ISO 11783-5 Table 1, Byte 1이 최하위 바이트
    v = int.from_bytes(bytes(name), "little")
    return (v >> 63, v >> 60 & 7, v >> 49 & 0x7F, v >> 48 & 1, v >> 40 & 0xFF, v >> 35 & 0x1F, v >> 32 & 7)


# (self-config, industry group, device class, 예약 비트, function, function instance, ECU instance)
assert name_fields(NAME_LEFT) == (1, 2, 6, 0, 128, 0, 0)
assert name_fields(NAME_RIGHT) == (1, 2, 6, 0, 128, 0, 1)

wsm_id   = can_id(PRIORITY, PF_MASTER, PS_MASTER, MASTER_SA)
wsm_data = [NUM_MEMBERS] + [0xFF] * 7          # Byte1=멤버 수, Byte2~8=Reserved

wsmem_id = can_id(PRIORITY, PF_MEMBER, PS_MEMBER, MASTER_SA)  # SA는 두 메시지 모두 master!

frames = [
    (0,   wsm_id,   wsm_data),
    (100, wsmem_id, NAME_LEFT),
    (200, wsmem_id, NAME_RIGHT),
]

for t, cid, data in frames:
    print(f"t={t:>4}ms  ID=0x{cid:08X}  DATA={' '.join(f'{b:02X}' for b in data)}")

assert wsm_data[0] == NUM_MEMBERS                       # Byte1 = 3 (마스터 포함)
assert len(frames) - 1 == NUM_MEMBERS - 1                # member 메시지 수 = 멤버 수 - 1 = 2
assert all(cid == wsmem_id for _, cid, _ in frames[1:])  # 모든 member 메시지가 master SA에서 나감

completion_ms = frames[-1][0] + 350                       # 마지막 member 메시지 + 350ms
print("Working Set 구성 완료 판정 시각:", completion_ms, "ms")

# 출력:
# t=   0ms  ID=0x1CFE0D90  DATA=03 FF FF FF FF FF FF FF
# t= 100ms  ID=0x1CFE0C90  DATA=00 00 A8 82 00 80 0C A0
# t= 200ms  ID=0x1CFE0C90  DATA=00 00 A8 82 01 80 0C A0
# Working Set 구성 완료 판정 시각: 550 ms
```

`name_fields()`는 8바이트를 하나의 64비트 정수로 합친 뒤(낮은 자리 바이트 먼저) 필드마다 비트를 잘라 낸다. 두 assert가 위 NAME 풀이 표와 같은 값을 확인한다.
:::

정리하면, Working Set 선언은 master가 보내는 프레임 세 개(크기 1개, NAME 2개)와 마지막 350 ms의 기다림으로 끝난다. member는 이 과정에서 말하지 않는다.

<small>근거: ISO 11783-5 4.3.2, Table 1, A.3; ISO 11783-10 Table F.1</small>

## 5. Working Set 메시지 규정 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 장 끝의 핵심 정리로 가도 된다.
:::

2절과 4절은 Working Set이 만들어지는 흐름을 따라갔다. 이 절은 그 두 메시지를 정의한 ISO 11783-7(트랙터와 작업기가 주고받는 메시지를 정하는 표준 문서)의 규정을 하나씩 읽는다. 표준 문장에서 shall은 "반드시 해야 한다", should는 "그렇게 하기를 권한다", may는 "해도 된다"는 뜻이다. 아래에서 괄호 안에 이 단어를 남긴 곳은 그 강도를 보여 주려는 것이다.

등장인물은 셋이다. master, member, 그리고 <strong>service provider</strong>다. service provider는 그 Working Set 바깥에서 Working Set과 통신하는 CF를 말한다. VT·TC가 전형적인 service provider이고, 다른 Working Set의 master나 member여도 상관없다.

### 두 메시지의 정의

| 항목 | Working Set Master | Working Set Member |
|---|---|---|
| PGN | 65037 (0xFE0D) | 65036 (0xFE0C) |
| DP / PF / PS | 0 / 254 / 13 | 0 / 254 / 12 |
| 기본 priority | 7 | 7 |
| 데이터 길이 | 8 byte | 8 byte |
| 전송 주기 | As required (주기 없음) | As required |
| Byte 1 | 멤버 수, master 포함 (SPN 2409, 1~250) | NAME 시작 |
| Byte 2~8 | Reserved | NAME 나머지 (SPN 2845) |
| 송신자 | master | master |

DP·PF·PS는 PGN을 이루는 세 칸(데이터 페이지, PDU 형식, PDU 고유값)이다([9장](/study/isobus/09-j1939-message)). SPN은 메시지 안 값 하나하나에 붙은 번호다.

- 두 PGN은 PF가 254(240 이상)인 PDU2 형식이다. CAN ID에 목적지 칸이 없으니 언제나 전역으로 나간다. service provider가 master에게 지정 주소로 Request를 보내도 응답은 전역이다. 그래서 한 service provider의 재요청으로 나간 재정의를 버스의 다른 service provider도 함께 받는다.
- 전송 주기가 "As required"라 주기 송신이 없다. 나중에 켜진 service provider는 정의를 본 적이 없는 채로 시작하므로, 아래 규칙 a)의 Request로 받아 오면 된다(추론: 표준은 늦게 합류한 경우를 따로 다루지 않는다).
- Byte 2~8의 Reserved에는 값이 적혀 있지 않다. ISO 11783-7의 일반 규칙이 "메시지 정의에 따로 적지 않았으면 예약 비트는 모두 1"이므로 `FF`로 채운다. 4절의 `03 FF FF FF FF FF FF FF`가 이 규칙을 따른 값이다.
- member 메시지에 싣는 NAME은 그 member가 주소를 클레임할 때 쓴 NAME과 같아야 한다. Working Set 자체는 master의 NAME으로 식별하고, NAME 기준으로 어떤 member도 동시에 두 Working Set에 속할 수 없다.
- 멤버 수의 범위는 1~250이다. 그런데 아래 규칙 d)는 Working Set이 더 필요 없을 때 멤버 수 0을 보내라고 한다. 두 규정을 함께 읽으면 0은 범위 밖의 특수값, 즉 삭제 통지다. 1~250만 받는 파서는 삭제 통지를 버리게 된다. 반대로 251~255는 1 byte 파라미터의 유효 범위 밖(지시자·예약·오류·미가용)이므로 멤버 수로 받아들이지 않는다.

ISO 11783-7은 1 byte 값의 쓰임을 아래처럼 나눈다. 251 이상은 측정값이 아니라 "값이 없다", "오류가 났다" 같은 상태를 알리는 데 쓴다.

| 1 byte 값 | 뜻 |
|---|---|
| 0~250 (`00`~`FA`) | 유효한 값 |
| 251 (`FB`) | 파라미터별 지시자 |
| 252~253 (`FC`~`FD`) | 앞으로 쓸 지시자를 위한 예약 |
| 254 (`FE`) | error indicator(오류 표시) |
| 255 (`FF`) | 미가용(not available, 장착 안 됨, 요청 안 됨) |

### 누가 누구에게 보내는가

- master의 주소는 Working Set 전체를 향하는 "전역의 부분집합" 목적지다. master 앞으로 보내는 것은 "이 팀 모두에게" 보내는 것과 같다는 뜻이다. service provider는 Working Set 몫의 데이터 대부분을 master의 SA로 보낸다.
- member도 직접 메시지를 보낼 수 있다. 표준이 드는 예는 파종기다. master 하나에 줄(row)마다 member가 하나씩 있고, VT는 master와 각 member의 명령을 모두 받아들이며, member는 자기 줄의 화면을 갱신한다.
- member가 보낸 Request의 응답은 service provider가 그 member에게 보낸다(shall). 그래서 TP(Transport Protocol, 8바이트보다 긴 데이터를 나눠 보내는 방식) 응답도 member가 직접 받는다.
- member는 다른 member 앞으로 온 지정 메시지를 지켜볼 의무가 없다.
- 다른 CF는 master에게 보내도 되고, 필요하면 member에게 직접 보내도 된다. member에게서 온 메시지는 그 Working Set의 것으로 해석해야 한다(shall).
- 표준은 이 메시지의 실제 쓰임이 응용 계층마다 다르고 더 좁을 수 있다고 적어 둔다. VT 쪽은 [29장](/study/isobus/29-vt-basics), TC 쪽은 [41장](/study/isobus/41-tc-basics)과 함께 읽는다.

### 운용 규칙 a)~h)

표준은 Working Set을 다루는 규칙을 a)부터 h)까지 여덟 개로 정리해 두었다. 아래 표와 코드의 "규칙 a)", "규칙 f)"는 이 목록을 가리킨다.

| 규칙 | 요지 | 구현 포인트 |
|---|---|---|
| a) | master 메시지 뒤에는 항상 (멤버 수 − 1)개의 member 메시지가 온다. 개수가 맞지 않으면 service provider는 master에게 PGN 65037을 Request해야 하고(shall), master는 master 메시지와 member 메시지 전부를 다시 보내야 한다(shall). 응용 계층 문서에 다른 규정이 없으면, 최소 3회 실패한 뒤에는 그 Working Set을 무시해도 된다(may). | 개수 검사, 재요청, 포기 카운터 |
| b) | Working Set은 member의 NAME으로 정의한다. member 메시지 간격은 100 ms다. member 메시지 뒤로 350 ms를 넘기면 수신 측은 master가 NAME을 다 보냈다고 본다(shall). | member마다 350 ms 타이머를 다시 건다 |
| c) | member도 독립된 CF다. 고장 메시지는 각자의 SA로 나가고, 고장표 클리어·파라미터 프로그래밍 같은 명령은 대상 CF의 SA로 보내야 한다(shall). master 앞으로 온 프로그래밍을 member 전원이 받아들이지 않도록 만들어야 한다(shall). 여러 member에 공통 데이터를 한 번에 넣으려면 그런 응용 소프트웨어가 따로 있어야 한다(표준의 참고 문장). | DM1은 member SA별로 모으고, DM3는 member SA로 보낸다([28장](/study/isobus/28-diagnostics-dm-fmi)) |
| d) | CF 하나는 Working Set 하나에만 속한다(shall not). 기존 master가 새 master 메시지를 보내면 service provider는 옛 정의를 새 정의로 바꾼다(shall). 바꿀 일이 생기면 master가 다시 정의하고, 더 필요 없으면 멤버 수 0을 보낸다(shall). | master 메시지 수신 = 정의 새로 시작 |
| e) | master가 NAME을 바꾸면 새 Working Set을 만든다(shall). 옛 정의는 멤버 수 0 메시지로 정리될 때까지 service provider 메모리에 남을 수 있다. 중복 member를 찾아 고치는 책임은 service provider에 있다. 표준의 참고 문장은 중복이나 안 쓰는 Working Set을 주기적으로 점검해 메모리를 회수하라고 권한다. | 중복 검사, 주기 정리 |
| f) | master의 SA가 바뀌어도 정의는 그대로다. service provider는 새 address claim을 보고 SA와 NAME의 연결을 고치고(shall), member는 Working Set 통신을 받으려고 보던 주소를 바꾼다(shall). | 재정의 없음 |
| g) | member의 SA가 바뀌면 service provider는 새 SA를 해당 Working Set에 연결한다(shall). NAME이 그대로면 address claim만 보고 처리할 수 있다. | 재정의 없음 |
| h) | member NAME 전부를 챙기는 책임은 master에 있다. member가 네트워크에 들어오거나 나가면 master가 정의를 고친다(shall). service provider는 메시지에 적힌 멤버 수로 Working Set을 만든 뒤, member가 주소를 claim할 때마다 SA를 채운다(shall). | NAME 먼저, SA는 나중 |

규칙 c)의 DM1·DM3는 고장 코드를 알리고 지우는 진단 메시지다([27장](/study/isobus/27-diagnostics-identification), [28장](/study/isobus/28-diagnostics-dm-fmi)). 표의 address claim은 1절의 주소 클레임 메시지를 말한다.

### 다시 선언하는 경우

| 상황 | master | service provider | 근거 |
|---|---|---|---|
| member 메시지 개수가 모자람 | Request를 받으면 master·member 메시지를 전부 다시 보낸다 | master에게 PGN 65037 Request. 최소 3회 실패 뒤에는 무시해도 된다 | a) |
| member 합류·이탈 | 정의를 고쳐 다시 보낸다 | 새 정의로 바꾼다 | h), d) |
| Working Set 종료 | 멤버 수 0을 보낸다 | 정의를 지운다 | d) |
| master NAME 변경 | 새 Working Set을 만든다 | 옛 정의는 정리될 때까지 남을 수 있다 | e) |
| master 또는 member SA 변경 | 다시 보내지 않는다 | address claim을 보고 SA만 고친다 | f), g) |

![Working Set Master가 멤버 수 3을 선언한 뒤 member 메시지 하나가 유실되자 VT가 350 ms 뒤 PGN 65037을 Request하고, master가 200 ms 안에 master 메시지와 member 메시지 두 개를 100 ms 간격으로 다시 보내 정의가 완료되는 시퀀스](/images/study-isobus/14-ws-sequence-light.png)
![Working Set Master가 멤버 수 3을 선언한 뒤 member 메시지 하나가 유실되자 VT가 350 ms 뒤 PGN 65037을 Request하고, master가 200 ms 안에 master 메시지와 member 메시지 두 개를 100 ms 간격으로 다시 보내 정의가 완료되는 시퀀스](/images/study-isobus/14-ws-sequence-dark.png)

그림은 member 메시지 하나가 유실된 경우다. 마지막 member 메시지 뒤로 350 ms가 지났는데 member가 하나뿐이니, VT는 master에게 Request(PGN 59904, 데이터 `0D FE 00`)를 보낸다. Request 데이터 `0D FE 00`은 요청할 PGN 65037(`0x00FE0D`)을 낮은 자리 바이트부터 적은 것이다. master는 ISO 11783-3(데이터 링크 계층을 정하는 표준 문서)의 응답 시간 Tr(200 ms) 안에 master 메시지부터 다시 보내고, member 메시지 두 개를 100 ms 간격으로 잇는다.

::: warning 수신 측에서 흔히 틀리는 곳
- 350 ms 타이머는 member 메시지가 올 때마다 다시 건다. 표준 문장의 기준점이 "a working-set-member message"이기 때문이다. master 메시지에서 첫 member까지의 간격, 그리고 member가 하나도 오지 않을 때 언제 포기할지는 표준에 없다. 아래 코드는 master 메시지 시각부터 같은 350 ms를 잰다(구현 선택).
- 새 master 메시지가 오면 받던 정의를 버리고 처음부터 센다(d). 이전 정의에 member를 이어 붙이면 개수가 틀어진다.
- Working Set의 키는 master의 NAME이다. SA를 키로 쓰면 master가 주소를 바꾸는 순간(f) Working Set을 잃는다.
- 멤버 수 0은 범위(1~250) 밖이지만 유효한 삭제 통지다.
:::

아래 코드는 VT 같은 service provider가 Working Set 정의를 모으는 수신기다. member 개수가 맞으면 정의를 저장하고, 모자라면 master에게 다시 요청하며, 세 번 요청하고도 완성하지 못하면 포기한다.

::: details Python으로 service provider 수신기 만들어 보기
```python
class WorkingSetTracker:
    def __init__(self, name_of, request_master):
        self.name_of, self.request_master = name_of, request_master
        self.sets, self.pending, self.requests_sent = {}, {}, {}

    def on_master(self, t, sa, size):
        key = self.name_of(sa)
        if size == 0:
            self.sets.pop(key, None)
            self.pending.pop(key, None)
            return
        self.pending[key] = {"sa": sa, "size": size, "names": [], "last": t}

    def on_member(self, t, sa, member_name):
        p = self.pending.get(self.name_of(sa))
        if p is not None:
            p["names"].append(member_name)
            p["last"] = t

    def tick(self, t):
        for key, p in list(self.pending.items()):
            if t - p["last"] <= 350:
                continue
            del self.pending[key]
            if len(p["names"]) == p["size"] - 1:
                self.sets[key] = p["names"]
                self.requests_sent[key] = 0
            elif self.requests_sent.get(key, 0) < 3:
                self.requests_sent[key] = self.requests_sent.get(key, 0) + 1
                self.request_master(t, p["sa"])


claims = {0x90: "NAME_M", 0xA0: "NAME_X"}       # address claim으로 알게 된 SA -> NAME
requests = []
vt = WorkingSetTracker(claims.get, lambda t, sa: requests.append((t, sa)))
L, R = "00 00 A8 82 00 80 0C A0", "00 00 A8 82 01 80 0C A0"


def run(start, stop):
    for t in range(start, stop, 10):
        vt.tick(t)


vt.on_master(0, 0x90, 3)                          # NAME_L 프레임은 유실됐다
vt.on_member(200, 0x90, R)
run(0, 600)
assert requests == [(560, 0x90)]                  # 200 + 350 ms를 넘긴 첫 tick에서 재요청

vt.on_master(600, 0x90, 3)
vt.on_member(700, 0x90, L)
vt.on_member(800, 0x90, R)
run(600, 1200)
assert vt.sets["NAME_M"] == [L, R]

for start in (2000, 3000, 4000, 5000):            # member가 끝내 오지 않는 Working Set
    vt.on_master(start, 0xA0, 2)
    run(start, start + 600)
assert [sa for _, sa in requests].count(0xA0) == 3 and "NAME_X" not in vt.sets

claims[0x95] = claims.pop(0x90)                   # master가 0x95로 다시 claim (규칙 f)
assert vt.sets["NAME_M"] == [L, R]                # 키가 NAME이라 정의는 그대로다
vt.on_master(6000, 0x95, 0)                       # 멤버 수 0 = 삭제 (규칙 d)
assert "NAME_M" not in vt.sets
print("재요청:", [(t, hex(sa)) for t, sa in requests])
# 재요청: [(560, '0x90'), (2360, '0xa0'), (3360, '0xa0'), (4360, '0xa0')]
```

"최소 3회"를 보수적으로 읽어, Request를 세 번 보내고도 완성하지 못했을 때 포기하게 했다. 출력의 `(560, '0x90')`은 마지막 member 시각 200 ms에 350 ms를 더한 550 ms를 넘긴 첫 점검(10 ms 간격)에서 재요청이 나갔다는 뜻이다. `0xa0` 쪽은 세 번 요청한 뒤 네 번째 실패에서는 더 요청하지 않는다.
:::

::: tip 정리
- Working Set Master·Member 메시지는 PDU2·priority 7·8 byte이고, 주기 없이 필요할 때 master가 보낸다.
- service provider는 member 개수를 세고, 모자라면 master에게 PGN 65037을 Request해야 한다. 최소 3회 실패한 뒤에는 무시해도 된다.
- 재선언은 개수 부족·member 변동·종료(멤버 수 0)·master NAME 변경 때 일어나고, SA 변경만으로는 일어나지 않는다.
:::

<small>근거: ISO 11783-7 B.23, A.24, 3.3; ISO 11783-3 5.4.3, 5.13.3</small>

::: details 원문을 가진 독자를 위한 메모
- 두 메시지 정의는 ISO 11783-7:2015 B.23.2(Working Set Master)와 B.23.3(Working Set Member), 송수신 관계는 B.23.1, 규칙 a)~h)는 B.23.4다. 2018년 Amendment 1은 B.23을 고치지 않았다.
- 멤버 수(SPN 2409)는 A.24.1, member NAME(SPN 2845)은 A.24.2에 정의돼 있다. 예약 비트를 1로 채우는 일반 규칙은 Part 7 3.3, 1 byte 값 범위표는 Part 7 3.3.3의 Table 1이다.
- PDU2 응답이 요청 방식과 상관없이 전역으로 나가는 규칙은 ISO 11783-3:2018 5.4.3의 Table 5, 응답 시간 Tr(200 ms)은 5.13.3이다.
- 3절 표의 "master가 VT Status를 기다린다"는 ISO 11783-6:2018 4.6.6.2, "주소 클레임 뒤 6 s 대기"는 ISO 11783-10:2015 6.6.1 b)와 6.6.2 b)다.
- 4절의 NAME 바이트 순서는 ISO 11783-5:2019 4.3.2 Table 1, ECU instance 권고는 4.3.2와 Annex A.3의 예, device class 6(Sprayers)은 ISO 11783-10:2015 Table F.1이다.
:::

::: tip 핵심 정리
- ISOBUS에서 통신 주체는 CF라고 부른다. ECU 한 대에 CF가 여럿일 수 있고, CF마다 주소가 따로 있다.
- 작업기 ECU는 대부분 128~247의 self-configurable 주소를 NAME 우선순위로 정한다. 같은 주소를 원하면 NAME 값이 작은 쪽이 이긴다.
- Working Set은 작업기 안의 CF들을 한 팀으로 묶은 것이다. 팀장인 master가 Master·Member 메시지(PGN 65037/65036)를 모두 보내 구성을 선언하고, VT·TC와의 통신을 대표한다.
- 전원 ON 후 약 2초 안에 주소 클레임, VT Status 확인, Working Set 선언, VT 연결(Object Pool)까지 끝난다. TC 연결은 주소 클레임 뒤 6초를 기다린 다음에 이루어진다.
- 수신 측은 member 메시지 개수를 세고, 모자라면 master에게 다시 요청한다. 최소 3회 실패한 뒤에는 그 Working Set을 무시해도 된다.
:::

::: details 확인 문제
1. (개념) ECU와 CF는 어떻게 다른가? ECU 한 대가 버스에서 주소 두 개로 보일 수 있는가?
2. (개념) Working Set Master 메시지의 Byte 1이 `03`이다. 이어서 오는 member 메시지는 몇 개이고, 그 메시지들의 SA는 누구의 주소인가?
3. (개념) 전원을 켠 뒤 VT 화면은 1.5초쯤 뜨는데 TC 연결은 7초쯤에야 끝난다. 왜 이렇게 차이가 나는가?
4. (시나리오) VT가 SA `0x90`에서 멤버 수 4인 Working Set Master 메시지를 받았다. 이어서 member 메시지가 두 개만 왔고, 마지막 것으로부터 350 ms가 지났다. VT는 무엇을 해야 하나? 같은 일이 계속 되풀이되면? 나중에 master가 SA `0x95`(149)로 주소를 다시 claim했다면 정의를 다시 받아야 하나?

**답 가이드**
1. ECU는 물리적인 전자 제어 장치이고, CF는 주소 하나를 갖고 버스에 참여하는 통신 주체다. ECU 한 대 안에 CF가 여러 개 있을 수 있고 CF마다 주소가 따로 있으므로, ECU 한 대가 주소 두 개(또는 그 이상)로 보일 수 있다.
2. member 메시지는 3 − 1 = 2개다. Byte 1은 master를 포함한 수이기 때문이다. 두 member 메시지도 master가 보내므로 SA는 master의 주소다.
3. VT 쪽은 주소가 정해지고 VT Status를 확인하면 곧바로 Working Set 선언과 Object Pool 전송으로 넘어간다. TC 쪽은 TC와 클라이언트 모두 주소 클레임을 마친 뒤 6초를 기다려야 한다. 이 공백이 있어야 TC가 클라이언트의 재시작을 알아챌 수 있다.
4. member 메시지가 3개(4 − 1)여야 하는데 2개뿐이므로, VT는 master(`0x90`)에게 PGN 65037을 지정 Request(데이터 `0D FE 00`)해야 한다. master는 master 메시지와 member 메시지 3개를 전부 다시 보낸다(규칙 a). 응용 계층에 다른 규정이 없으면 최소 3회 실패한 뒤에는 그 Working Set을 무시해도 된다. master의 SA가 바뀌어도 정의는 바뀌지 않는다(규칙 f). 주소 클레임 메시지를 보고 SA와 NAME의 연결만 고치면 되고, Working Set을 master의 NAME으로 관리했다면 다시 받을 필요가 없다.
:::

## 다음 챕터

- 다음: [27장 진단 (1): 진단 개요, ECU 식별, 인증 정보](/study/isobus/27-diagnostics-identification)
