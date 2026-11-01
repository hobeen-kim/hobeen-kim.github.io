---
title: "DDOP 기초: 장치가 자기를 소개하는 방법"
description: "작업기가 TC에게 자기 구조와 능력을 알리는 DDOP가 무엇인지, 다섯 가지 오브젝트가 나무 구조로 어떻게 엮이는지, 어떤 순서로 TC에 올라가는지 익힌다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, TaskController, TC, DDOP, DeviceDescription, ObjectPool]
prev: /study/isobus/47-tc-totals-logging-peer
next: /study/isobus/49-ddop-bytes
---

# DDOP 기초: 장치가 자기를 소개하는 방법

::: info 학습 목표
- DDOP가 무엇이고 TC에게 왜 필요한지 설명할 수 있다.
- DDOP를 이루는 다섯 가지 오브젝트(DVC, DET, DPD, DPT, DVP)의 역할을 구분할 수 있다.
- 오브젝트들이 나무 구조로 이어진 그림을 읽을 수 있다.
- 작업기가 DDOP를 TC에 올리고 활성화하는 순서를 말할 수 있다.
- DPD의 속성 바이트와 트리거 바이트를 비트로 계산할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [41장 TC 기초](/study/isobus/41-tc-basics), [45장 TC 프로세스 데이터 기초](/study/isobus/45-tc-process-data-basics)
- 이 장에서 처음 나오는 말
  - DDOP: 작업기가 TC에게 건네는 자기소개 데이터 묶음
  - 오브젝트: DDOP를 이루는 항목 하나. 카드 한 장이라고 생각하면 된다
  - Object ID: 오브젝트마다 붙는 번호. 다른 오브젝트를 가리킬 때 쓴다
  - Structure Label: DDOP 구조의 버전을 나타내는 이름표
  - settable: TC가 값을 정해 줄 수 있다는 표시
  - 트리거: 작업기가 값을 언제 보고할 수 있는지 나타내는 조건
:::

처음 만난 사람에게 자기소개를 하듯, 트랙터에 새 작업기를 연결하면 작업기는 TC에게 먼저 자기를 소개한다. "나는 붐 살포기다. 붐은 하나이고 섹션은 7개다. 섹션 하나의 폭은 171.4 cm다. 살포량 목표를 받을 수 있고, 실제로 뿌린 양을 알려 줄 수 있다." 이 자기소개를 TC가 읽을 수 있는 정해진 서식으로 쓴 것이 DDOP다. 이 장에서는 그 서식이 어떤 항목으로 이루어지는지, 작업기가 그것을 어떤 순서로 TC에 건네는지 본다.

## 1. DDOP란: 작업기의 자기소개서

이 절에서는 DDOP가 무엇이고, DDOP가 없으면 왜 곤란한지 본다.

### TC는 작업기에 대해 아무것도 모른다

TC(Task Controller, 처방에 따라 작업기에 명령을 내리고 작업 기록을 남기는 장치)는 버스에 연결된 작업기에 대해 아무런 사전 정보가 없다. 작업기에 섹션(Section, 붐에서 따로 켜고 끌 수 있는 한 구간)이 몇 개인지 TC는 알 수 없다. 작업기가 어떤 DDI(Data Dictionary Identifier, 값의 종류를 가리키는 번호. [45장](/study/isobus/45-tc-process-data-basics)에서 봤다)를 지원하는지, 작업 폭이 얼마인지도 알 수 없다.

이 장에서는 TC 쪽 장치를 그냥 TC라고 부른다. 작업기 안에서 TC와 대화하는 ECU(Electronic Control Unit, 전자 제어 장치)는 TC 클라이언트, 줄여서 클라이언트라고 부른다.

### 정의

<strong>DDOP(Device Descriptor Object Pool, 장치 설명 오브젝트 풀)</strong>는 작업기가 자기 자신의 구조와 능력을 TC에게 알려 주는 데이터 묶음이다. "풀(pool)"은 여러 오브젝트를 한데 모아 둔 묶음이라는 뜻이다. DDOP는 이 정보를 정해진 형식으로 TC에 전달해서, TC가 작업기를 이해하고 제어할 수 있게 한다.

> DDOP는 "작업기의 자기소개서"이다.

![왼쪽은 위에서 내려다본 붐 살포기로, 트랙터 뒤에 탱크와 붐이 달리고 붐은 폭 171.4 cm인 섹션 7개로 나뉜다. 오른쪽은 이 살포기의 자기소개서 문장 일곱 줄과, 각 문장이 담기는 오브젝트 DVC, DET, DPT, DPD, DVP를 짝지은 표다](/images/study-isobus/48-ddop-self-intro-light.png)
![왼쪽은 위에서 내려다본 붐 살포기로, 트랙터 뒤에 탱크와 붐이 달리고 붐은 폭 171.4 cm인 섹션 7개로 나뉜다. 오른쪽은 이 살포기의 자기소개서 문장 일곱 줄과, 각 문장이 담기는 오브젝트 DVC, DET, DPT, DPD, DVP를 짝지은 표다](/images/study-isobus/48-ddop-self-intro-dark.png)

그림 왼쪽은 위에서 내려다본 살포기이고, 오른쪽은 이 살포기가 TC에게 내미는 자기소개서다. 문장마다 오른쪽에 적힌 세 글자(DVC, DET 등)가 그 문장을 담는 오브젝트의 종류다. 다섯 종류는 2절에서 하나씩 본다.

비유가 맞지 않는 곳도 있다. 사람의 자기소개서는 읽는 사람이 알아서 해석하지만, DDOP는 칸과 순서가 정해진 서식이라 TC가 기계적으로 읽는다. 칸 하나만 잘못 채워도 TC는 DDOP 전체를 받아들이지 않을 수 있다([50장](/study/isobus/50-ddop-commands-design)에서 본다).

### DDOP가 없을 때와 있을 때

<strong>DDOP가 없다면</strong>
- TC는 작업기에 어떤 명령을 보낼 수 있는지 모른다.
- 처방 맵(밭의 위치마다 뿌릴 양을 정해 둔 지도)의 살포량을 어느 DDI로 전달해야 하는지 알 수 없다.
- 섹션 제어(Section Control, 섹션을 위치에 맞춰 켜고 끄는 기능)를 하려 해도 섹션이 몇 개인지 파악하지 못한다.

<strong>DDOP가 있다면</strong>
- TC는 작업기의 구조를 파악하고 알맞은 명령을 고른다.
- 지원되지 않는 DDI로 명령하는 일을 미리 막는다.

정리하면, TC는 DDOP에 적힌 내용으로 작업기를 이해하고, 적힌 범위 안에서만 명령한다.

## 2. DDOP를 이루는 다섯 가지 오브젝트

이 절에서는 자기소개서를 이루는 다섯 종류의 카드, 곧 오브젝트를 하나씩 본다. 다섯 종류가 서로를 번호로 가리키며 나무 구조를 이룬다는 점이 핵심이다.

DDOP는 5가지 타입의 오브젝트로 구성된다.

| 오브젝트 타입 | 역할 | 주요 속성 |
|--------------|------|-----------|
| **Device** | 장치 전체 정보 (최상위) | 제조사, 제품명, 시리얼번호, Structure Label |
| **DeviceElement** | 장치의 논리적 구성 요소 | Element Type, Element Number, 부모 Element |
| **DeviceProcessData** | 지원하는 프로세스 데이터 항목 | DDI, Property Flag (default/settable/control source), Trigger Methods |
| **DeviceProperty** | 고정 속성값 | DDI, 값 (작업폭, 구획 폭 등) |
| **DeviceValuePresentation** | 데이터 표현 방식 | 오프셋, 스케일, 소수 자릿수, 단위 기호 |

표의 "구획"은 섹션과 같은 말이다. Device의 "제조사"는 따로 글자 칸이 있는 것이 아니다. 주소 클레임에 쓰는 NAME([12장](/study/isobus/12-j1939-address-name)) 안의 제조사 코드로 들어간다. 실제 칸 배치는 [49장](/study/isobus/49-ddop-bytes)에서 본다.

다섯 타입에는 각각 세 글자 약칭이 있다. 이 약칭은 49장에서 볼 바이트 레코드의 맨 앞 세 바이트에 실제로 적히는 이름이다. 그래서 이 장에서도 본문에서는 약칭으로 부른다.

| 약칭 | 원래 이름 | 우리말로 |
|---|---|---|
| DVC | Device | 장치 |
| DET | DeviceElement | 장치 요소 |
| DPD | DeviceProcessData | 장치 프로세스 데이터 |
| DPT | DeviceProperty | 장치 속성 |
| DVP | DeviceValuePresentation | 장치 값 표시 방식 |

### 나무 구조로 보기

다섯 오브젝트는 나무처럼 이어진다. DVC가 뿌리이고, DET가 가지, DPD와 DPT가 가지에 달린 잎이다. DVP는 여러 잎이 함께 쓰는 표시 규칙이다.

![DDOP 오브젝트 나무 구조. 맨 위 DVC(살포기 전체) 아래에 루트 DET(type Device)가 있고, 그 아래로 Section 1·2·3 DET와 작업 폭 9 m를 담은 DPT가 달린다. Section 1 아래에 DDI 1 Setpoint와 DDI 2 Actual을 담은 DPD 두 개가 있고, 두 DPD는 단위 L/ha, Scale 0.0001인 DVP 하나를 함께 가리킨다](/images/study-isobus/48-ddop-object-tree-light.png)
![DDOP 오브젝트 나무 구조. 맨 위 DVC(살포기 전체) 아래에 루트 DET(type Device)가 있고, 그 아래로 Section 1·2·3 DET와 작업 폭 9 m를 담은 DPT가 달린다. Section 1 아래에 DDI 1 Setpoint와 DDI 2 Actual을 담은 DPD 두 개가 있고, 두 DPD는 단위 L/ha, Scale 0.0001인 DVP 하나를 함께 가리킨다](/images/study-isobus/48-ddop-object-tree-dark.png)

그림은 섹션 3개짜리 살포기로 줄여 그렸다. 화살표는 "위 오브젝트가 아래 오브젝트를 가진다(가리킨다)"로 읽는다. Section 2·3 아래에도 Section 1과 같은 DPD가 붙지만 그림을 단순하게 하려고 뺐다. 전체 모습은 4절 예제에서 본다.

### 오브젝트별로 자세히

<strong>DVC (Device)</strong>
- DDOP 전체의 루트 오브젝트이다. DDOP 하나에 하나만 있다.
- `Structure Label`: DDOP 구조의 버전을 나타내는 식별자이다. 클라이언트는 TC에 이 라벨이 있는지 조회해서, DDOP를 새로 올릴지 TC에 저장된 것을 쓸지 결정한다.
- `Localization Label`: 언어·단위 설정을 나타내는 라벨이다.

<strong>DET (DeviceElement)</strong>
- 작업기의 논리적 부품이다. 쇳덩어리 부품 하나하나가 아니라, TC가 따로 이름을 불러 명령하거나 값을 물을 수 있는 단위라는 뜻이다. Element Type(1바이트 코드)으로 역할을 정의한다.
- `1 Device`: 장치 전체를 대표하는 Element (DDOP당 1개)
- `2 Function`: 살포 펌프, 파종 유닛 등 기능 단위
- `3 Bin`: 씨앗·비료 저장 용기
- `4 Section`: 독립 제어 가능한 구간(섹션)
- `5 Unit`: Section 하위의 가장 세분화된 단위 (노즐, 파종 로우 유닛 등)
- `6 Connector`: 히치 연결점
- `7 Navigation Reference`: GPS 안테나 등 내비게이션 기준 위치
- Element Number는 12비트(0~4095)이며, Parent Object ID로 상위 Element(또는 Device)를 참조해 계층을 구성한다. 12비트로 나타낼 수 있는 가장 큰 수가 4095(2의 12제곱 빼기 1)다.

<strong>DPD (DeviceProcessData)</strong>
- DET에 연결되며, 그 Element에서 지원하는 DDI 항목 하나를 정의한다.
- `Property Flag`(3비트): bit1 = 기본값(default) 세트 멤버 여부, bit2 = settable(TC가 값을 설정 가능, Setpoint류), bit3 = control source(다른 CF의 setpoint 값을 결정하는 소스로 동작). bit2·bit3은 동시에 설정될 수 없다.
  - default 세트: TC가 "기본으로 기록할 값을 보내라"고 하면 보내는 값 목록이다([47장](/study/isobus/47-tc-totals-logging-peer)).
  - CF(Control Function)는 버스에서 주소를 가진 제어 기능 하나를 말한다. control source는 Peer Control([47장](/study/isobus/47-tc-totals-logging-peer))에서 다른 장치에 setpoint를 대 주는 쪽이다.
- `Trigger Methods`(5비트): time interval(시간 간격), distance interval(거리 간격), threshold limits(임계값), on change(변화량), total(누적값)
  - 작업기가 이 값을 어떤 조건에서 보고할 수 있는지 밝히는 칸이다. on change는 값이 바뀔 때 보고하는 방식이고, 얼마나 바뀌면 보낼지는 TC가 정한다. TC는 여기 밝힌 조건으로만 measurement 명령([46장](/study/isobus/46-tc-commands-pdack))을 건다.

<strong>DPT (DeviceProperty)</strong>
- 변하지 않는 고정 속성이다. 작업 폭, 섹션 폭 등이 여기에 해당한다.
- DPD와 달리 TC가 값을 변경하지 않는다.

<strong>DVP (DeviceValuePresentation)</strong>
- 숫자값을 사람이 읽기 쉬운 형식으로 변환하는 규칙이다.
- 공식: `표시값 = (원시값 + Offset) × Scale`
- 예: 원시값 2,000,000(DDI 1), Offset=0, Scale=0.0001 → 표시값 200.00 L/ha
- `Number of decimals`(0~7) 속성으로 표시 소수 자릿수도 함께 정의한다.

원시값은 버스로 오가는 정수 그대로의 값이다. 위 예를 단계별로 계산하면 다음과 같다.

1. 원시값에 Offset을 더한다: 2,000,000 + 0 = 2,000,000
2. Scale을 곱한다: 2,000,000 × 0.0001 = 200
3. Number of decimals가 2라면 소수 둘째 자리까지 보여 준다: 200.00
4. 단위 기호 L/ha(헥타르당 리터, 1 ha는 100 m × 100 m 넓이)를 붙인다.

정리하면, DVC는 장치 전체, DET는 장치 안의 부품 단위, DPD는 바뀌는 값, DPT는 고정된 값, DVP는 그 값을 보여 주는 방법이다.

<small>근거: ISO 11783-10 A.2~A.7</small>

## 3. DDOP를 TC에 올리는 순서

이 절에서는 작업기가 자기소개서를 어떤 순서로 TC에게 건네는지 본다.

DDOP 관련 메시지는 모두 <strong>클라이언트가 TC(또는 DL)에게 보내는 요청</strong>과 그에 대한 TC의 응답으로 구성된다. DL(Data Logger)은 기록만 맡는 TC 비슷한 장치다([44장](/study/isobus/44-tc-multi-dl-functionality)). TC가 먼저 DDOP를 요구하는 것이 아니다. 클라이언트가 자신의 device descriptor(장치 설명. 표준 메시지 이름에서 DDOP를 부르는 말)를 TC에 질의하고, 전송하고, 활성화하는 흐름이다.

관공서에 서류를 낼 때와 비슷하다. 먼저 "예전에 낸 서류가 있나요?"를 묻는다. 없으면 "이만큼 낼 건데 받을 자리가 있나요?"를 확인한 뒤 서류를 낸다. 마지막으로 "이 서류로 처리해 주세요"라고 한다.

![DDOP 전송 순서를 위에서 아래로 그린 시퀀스 그림. 왼쪽 세로줄이 TC 클라이언트(작업기 ECU), 오른쪽 세로줄이 TC다. 주소 클레임 뒤 클라이언트가 Working Set Master와 Request Structure Label을 보내고 TC가 Structure Label로 답한다. TC에 DDOP가 없거나 버전이 다르면 Request Object-pool Transfer와 응답, Object-pool Transfer와 응답이 오가고, 이미 있으면 기존 DDOP를 쓴다. 마지막으로 Object-pool Activate와 Activate Response가 오간다](/images/study-isobus/48-ddop-transfer-sequence-light.png)
![DDOP 전송 순서를 위에서 아래로 그린 시퀀스 그림. 왼쪽 세로줄이 TC 클라이언트(작업기 ECU), 오른쪽 세로줄이 TC다. 주소 클레임 뒤 클라이언트가 Working Set Master와 Request Structure Label을 보내고 TC가 Structure Label로 답한다. TC에 DDOP가 없거나 버전이 다르면 Request Object-pool Transfer와 응답, Object-pool Transfer와 응답이 오가고, 이미 있으면 기존 DDOP를 쓴다. 마지막으로 Object-pool Activate와 Activate Response가 오간다](/images/study-isobus/48-ddop-transfer-sequence-dark.png)

그림은 위에서 아래로 시간이 흐른다. 실선 화살표는 클라이언트가 보내는 요청이고, 점선 화살표는 TC의 응답이다. 메시지 이름 옆 괄호 속 두 자리 16진수(01, 11 등)는 그 메시지의 첫 바이트다(6절에서 설명한다). 순서를 말로 풀면 다음과 같다.

1. 주소 클레임([13장](/study/isobus/13-j1939-address-claim))으로 버스 주소를 얻은 뒤, 클라이언트가 Working Set Master 메시지(PGN 65037)로 버스에 참여했음을 알린다([26장](/study/isobus/26-isobus-network-mgmt)).
2. 클라이언트가 Request Structure Label로 "이 라벨의 DDOP를 갖고 있나?"를 묻는다. TC는 같은 라벨이 있으면 그 라벨을 그대로, 없으면 `FF`로 채운 라벨을 돌려준다.
3. TC에 DDOP가 없거나 버전이 다르면, 클라이언트가 Request Object-pool Transfer로 보낼 데이터 크기를 알린다. TC는 메모리 확인 결과를 Request Object-pool Transfer Response로 답한다.
4. 클라이언트가 Object-pool Transfer로 DDOP 본문을 보낸다. 길이가 길어서 TP나 ETP로 여러 패킷에 나눠 보낸다. TC는 성공·실패를 Object-pool Transfer Response로 답한다.
5. TC에 같은 DDOP가 이미 있으면 3~4단계를 건너뛰고 저장된 DDOP를 쓴다.
6. 클라이언트가 Object-pool Activate로 활성화를 요청하고, TC가 Object-pool Activate Response로 결과를 알린다. 이제 태스크를 수행할 준비가 끝났다.

`FF`(=255)는 ISOBUS에서 "값 없음"을 나타내는 특수값으로 자주 쓰인다. Structure Label의 각 바이트에는 255를 쓸 수 없게 정해져 있어서([49장](/study/isobus/49-ddop-bytes)), 라벨 자리를 `FF`로 채운 응답은 "그런 라벨 없음"이라는 뜻이 된다. Structure Label이 맞은 뒤 Localization Label까지 확인하는 구성도 흔하다. 이 확인을 포함한 하위 명령 전체는 [50장](/study/isobus/50-ddop-commands-design)에서 본다.

### 전송 프로토콜

DDOP 데이터는 일반적으로 수백 바이트~수 킬로바이트에 달하므로, 단일 CAN 프레임(데이터 8바이트)으로 전송할 수 없다. ISO 11783의 <strong>TP(Transport Protocol, TP.CM 60416/TP.DT 60160)</strong> 또는 <strong>ETP(Extended Transport Protocol, ETP.CM 51200/ETP.DT 50944)</strong>를 사용하여 멀티패킷으로 분할 전송한다. TP는 [15장](/study/isobus/15-tp-bam-cmdt), ETP는 [17장](/study/isobus/17-etp)에서 다뤘다. CM은 연결을 여닫는 관리 메시지, DT는 데이터를 실어 나르는 메시지다.

명령 바이트 1개를 포함한 Object-pool Transfer 메시지가 1,785바이트를 넘으면 ETP를 쓰거나, 완전한 오브젝트 단위로 나눠 Object-pool Transfer를 여러 번 보낸다. 1,785바이트는 TP 한 번에 보낼 수 있는 최대 길이다(패킷 255개 × 7바이트). 나눠 보낼 때는 오브젝트 하나를 중간에서 자르면 안 된다.

<small>근거: ISO 11783-10 B.6.8</small>

## 4. 연습 예제: 3섹션 붐 살포기의 DDOP

이 절에서는 섹션 3개짜리 작은 살포기의 DDOP를 설계해 본다. 오브젝트마다 번호(Object ID)를 붙이고, 누가 누구를 가리키는지 표로 정리한다.

::: warning 단순화한 예제다
이 예제는 다섯 오브젝트를 익히기 위한 최소 구성이다. 섹션마다 DDI 289(Setpoint Work State)를 두는 방식은 실제 섹션 제어 규칙에 어긋난다. 규칙에 맞는 설계는 [49장](/study/isobus/49-ddop-bytes)과 [50장](/study/isobus/50-ddop-commands-design)에서 본다.
:::

### 대상: 3섹션 붐 살포기

- 총 작업 폭: 9m (섹션 3개 × 3m)
- 지원 기능: 섹션 제어(Section Control, 섹션별 ON/OFF), 살포량 제어(Rate Control, 위치에 따라 살포량을 바꿈)
- 지원 DDI: DDI 1(Setpoint Volume/Area), DDI 2(Actual Volume/Area), DDI 289(Setpoint Work State, 섹션 ON/OFF 명령)

Setpoint는 TC가 정해 주는 목표값이고, Actual은 작업기가 실제로 잰 값이다.

### DDOP 계층 구조

![3섹션 붐 살포기의 DDOP 계층. Object 0 DVC 아래 Object 2 루트 DET(Element 0)가 있고, 그 아래에 Object 3·4·5 Section DET(Element 1·2·3, 각 3 m)와 Object 6 DPT(작업 폭 9 m)가 달린다. 섹션마다 DPD가 셋(DDI 1 Setpoint, DDI 2 Measurement, DDI 289)씩 붙어 Object 7~15가 되고, 섹션마다 DDI 1과 DDI 2 DPD가 Object 16 DVP(L/ha, Scale 0.0001)를 가리킨다](/images/study-isobus/48-three-section-tree-light.png)
![3섹션 붐 살포기의 DDOP 계층. Object 0 DVC 아래 Object 2 루트 DET(Element 0)가 있고, 그 아래에 Object 3·4·5 Section DET(Element 1·2·3, 각 3 m)와 Object 6 DPT(작업 폭 9 m)가 달린다. 섹션마다 DPD가 셋(DDI 1 Setpoint, DDI 2 Measurement, DDI 289)씩 붙어 Object 7~15가 되고, 섹션마다 DDI 1과 DDI 2 DPD가 Object 16 DVP(L/ha, Scale 0.0001)를 가리킨다](/images/study-isobus/48-three-section-tree-dark.png)

그림의 "Obj"는 Object ID, "El"은 Element Number다. 위에서부터 DVC(뿌리), 루트 DET와 DPT, 섹션 DET 셋, 섹션마다 DPD 셋, 맨 아래 DVP 순이다. 이 예제에서 DDI 289 DPD는 DVP를 가리키지 않는다. 가리킬 DVP가 없는 칸에는 "없음" 표시를 넣는다(5절).

### DDOP 오브젝트 정의 표

표 읽는 법: 오브젝트 하나가 여러 줄을 차지한다. 첫 줄에 Object ID와 타입이 있고, 아래 줄은 같은 오브젝트의 다른 속성이다. 표에는 타입을 긴 이름으로 적었고, "DE(2)"는 "Object ID가 2인 DET"라는 뜻이다.

| 오브젝트 ID | 타입 | 주요 속성 | 값 |
|------------|------|----------|-----|
| 0 | Device | 제품명 | BoomSprayer-3S |
|   |        | 제조사 | ExampleCo |
|   |        | Structure Label | SPRY3-V1.0 |
| 2 | DeviceElement | Type | Device |
|   |               | Element Number | 0 |
|   |               | 부모 | Device(0) |
| 3 | DeviceElement | Type | Section |
|   |               | Element Number | 1 |
|   |               | 부모 | DE(2) |
| 4 | DeviceElement | Type | Section |
|   |               | Element Number | 2 |
|   |               | 부모 | DE(2) |
| 5 | DeviceElement | Type | Section |
|   |               | Element Number | 3 |
|   |               | 부모 | DE(2) |
| 6 | DeviceProperty | DDI | 작업폭 DDI |
|   |               | Value | 9000 (단위: mm) |
|   |               | 연결 Element | DE(2) |
| 7 | DeviceProcessData | DDI | 1 (Setpoint Vol/Area) |
|   |                   | Property Flag | Setpoint 지원 |
|   |                   | 연결 Element | DE(3), Section 1 |
| 8 | DeviceProcessData | DDI | 2 (Actual Vol/Area) |
|   |                   | Property Flag | Measurement 지원 |
|   |                   | Trigger | on change 지원(10 L/ha 임계값은 TC가 measurement 명령으로 지정) |
|   |                   | 연결 Element | DE(3), Section 1 |
| 9 | DeviceProcessData | DDI | 289 (Setpoint Work State) |
|   |                   | Property Flag | Setpoint 지원 |
|   |                   | 연결 Element | DE(3), Section 1 |
| 10~12 | DeviceProcessData | (Section 2 동일 구조) | DE(4) 연결 |
| 13~15 | DeviceProcessData | (Section 3 동일 구조) | DE(5) 연결 |
| 16 | DeviceValuePresentation | Offset | 0 |
|    |                         | Scale | 0.0001 |
|    |                         | Unit Symbol | L/ha |

한 행을 예로 읽어 보자. Object 8은 DPD이고 DDI 2(실제 살포량)를 다룬다. Property Flag가 Measurement, 곧 TC가 값을 정해 줄 수 없고 작업기가 잰 값을 보고만 한다. 값이 바뀌면 보고할 수 있고(on change), 얼마나 바뀌어야 보고할지(10 L/ha)는 TC가 정한다. 이 DPD는 Object 3인 DET, 곧 Section 1에 연결돼 있다.

두 가지를 덧붙인다.

- Object ID가 0 다음에 2로 건너뛴 것은 이 예제의 번호 붙이기일 뿐이다. 번호가 DDOP 안에서 겹치지만 않으면 된다.
- 표의 "제조사 ExampleCo"는 설명을 위해 적은 값이다. 실제 DVC 레코드에는 제조사 이름을 적는 글자 칸이 없고, 제조사는 ClientNAME(주소 클레임에 쓰는 NAME) 안의 제조사 코드로 나타난다. Structure Label `SPRY3-V1.0`도 10바이트라 7바이트짜리 칸에 다 들어가지 않는다. 두 가지 모두 [49장](/study/isobus/49-ddop-bytes)에서 실제 바이트로 풀어 본다.

이 DDOP를 수신한 TC는 다음을 파악한다.

- 이 작업기는 3개의 Section을 가진 살포기이다.
- 각 Section에 DDI 1(Setpoint), DDI 2(Measurement), DDI 289(Setpoint Work State)를 지원한다.
- 전체 작업폭은 9m이다.
- 값의 단위는 L/ha이며 스케일 인자는 0.0001이다.

## 5. 오브젝트 속을 들여다보기: 필드와 폭

지금까지 오브젝트를 말로 설명했다. 이 절에서는 오브젝트 하나가 어떤 칸(필드)으로 이루어지고, 칸마다 몇 바이트를 차지하는지 본다. 4절 예제의 값으로 칸을 직접 채워 본다.

### 모든 오브젝트에 공통인 머리

모든 DDOP 오브젝트는 <strong>Object ID</strong>와 오브젝트 타입(DVC·DET·DPD·DPT·DVP 다섯 종류 중 하나) 뒤에 타입별 속성이 이어지는 구조다. Object ID는 DDOP 전체에서 유일해야 한다.

다른 오브젝트를 가리키는 칸에 가리킬 대상이 없으면 NULL Object ID `0xFFFF`(=65535)를 넣는다. 번호 칸을 비워 둘 수는 없으니, 실제 오브젝트에는 쓰지 않는 가장 큰 값을 "가리키는 것 없음" 표시로 정해 둔 것이다.

::: tip 이 절에서 보는 범위
이 절은 <strong>타입별로 어떤 필드가 몇 바이트인지</strong>까지만 본다. 바이트열에서 각 필드가 정확히 몇 번째에 놓이는지는 [49장](/study/isobus/49-ddop-bytes)에서 본다. 미리 말하면, 모든 레코드는 Table ID(ASCII 3바이트, `DVC`·`DET` 등)로 시작하고 그 뒤에 Object ID 2바이트가 온다. 오브젝트 타입은 숫자 코드가 아니라 이 세 글자로 싣는다.
:::

### DET: 계층을 만드는 필드

표 읽는 법: "폭"은 그 필드가 차지하는 바이트 수다. 1바이트는 0~255, 2바이트는 0~65535를 담을 수 있다. 오른쪽 열은 4절 예제의 Object 3(Section 1)을 채운 값이다.

| 필드 | 폭 | §4 Object 3(DE, Section 1)의 값 |
|---|---|---|
| DeviceElementType | 1바이트 | 4(Section) |
| DeviceElementNumber | 2바이트 (0~4095) | 1 |
| Parent Object ID | Object ID와 같은 폭(2바이트) | 2 (DE(2), 전체 기능 루트) |

Object 3은 DeviceElementType 칸에 4를 적어 "나는 섹션이다"라고 밝힌다. Element Number 칸에는 1을 적는다. Parent Object ID 칸에 2를 적어 "Object 2(루트 DET) 아래에 있다"고 밝힌다. 부모를 적는 쪽이 자식이라는 점을 기억해 두자. DET의 나무 구조는 자식이 부모 번호를 적는 방식으로 만들어진다.

DeviceElementNumber가 4095까지인 것은 우연이 아니다. Process Data 메시지의 Element Number 필드도 12비트(0~4095)이므로, DDOP에서 선언한 Element Number를 그대로 [Process Data 메시지의 Element Number 자리](/study/isobus/45-tc-process-data-basics)에 실어 보낼 수 있다. 2바이트 칸은 65535까지 담을 수 있지만 Element Number로는 4095까지만 쓴다.

::: warning Object ID와 Element Number는 다른 번호다
Object ID는 DDOP 안에서 오브젝트끼리 서로를 가리킬 때 쓰는 번호다. Element Number는 Process Data 메시지에서 TC가 그 DET를 부를 때 쓰는 번호다. 4절 예제의 Section 1은 Object ID가 3이고 Element Number가 1이다.
:::

### DPD: DDI, 속성, 트리거를 담는 필드

DPD의 속성 칸과 트리거 칸은 비트셋이다. 비트셋은 바이트 하나의 비트 8개를 스위치 8개처럼 쓰는 방식이다. 비트 번호는 가장 낮은 자리(오른쪽 끝)가 bit 1, 가장 높은 자리(왼쪽 끝)가 bit 8이다. bit n이 켜지면(1) 바이트 값에 2의 (n−1)제곱을 더한다. 곧 bit 1은 1, bit 2는 2, bit 3은 4, bit 4는 8, bit 5는 16이다.

| 필드 | 폭 | 내용 |
|---|---|---|
| Process data DDI | 2바이트 | ISO 11783-11 정의 DDI |
| Process data properties | 1바이트(비트셋) | bit1=default set 멤버, bit2=settable, bit3=control source(bit2·3 동시 설정 불가) |
| Process data available trigger methods | 1바이트(비트셋) | bit1=time interval, bit2=distance interval, bit3=threshold limits, bit4=on change, bit5=total |
| Device value presentation object ID | 2바이트 | 없으면 NULL(`0xFFFF`) |

ISO 11783-11은 DDI 목록(데이터 사전)을 정하는 표준 문서다. 마지막 칸은 이 DPD의 값을 보여 줄 때 쓸 DVP의 Object ID다.

4절의 Object 7(Section 1의 DDI 1, Setpoint)과 Object 8(Section 1의 DDI 2, Measurement. 변화량이 10 L/ha 이상이면 보고)을 이 필드에 채우면 다음과 같다.

| Object | DDI | Properties 비트 | Properties 바이트 | Trigger 비트 | Trigger 바이트 |
|---|---|---|---|---|---|
| 7 (Setpoint) | 1 | bit2(settable)=1, 나머지 0 | `0x02` | §4 표에 트리거 명시 없음 | 확인 불가 |
| 8 (Measurement) | 2 | 전부 0(설정 불가) | `0x00` | bit4(on change)=1, 나머지 0 | `0x08` |

![DPD의 속성 바이트와 트리거 바이트를 비트 8칸으로 그린 그림. 속성 바이트는 bit 1 default set, bit 2 settable, bit 3 control source를 쓰고 bit 4~8은 0이다. Object 7은 bit 2만 1이라 0x02다. 트리거 바이트는 bit 1 time interval, bit 2 distance interval, bit 3 threshold limits, bit 4 on change, bit 5 total을 쓰고 bit 6~8은 0이다. Object 8은 bit 4만 1이라 0x08이다](/images/study-isobus/48-dpd-bits-light.png)
![DPD의 속성 바이트와 트리거 바이트를 비트 8칸으로 그린 그림. 속성 바이트는 bit 1 default set, bit 2 settable, bit 3 control source를 쓰고 bit 4~8은 0이다. Object 7은 bit 2만 1이라 0x02다. 트리거 바이트는 bit 1 time interval, bit 2 distance interval, bit 3 threshold limits, bit 4 on change, bit 5 total을 쓰고 bit 6~8은 0이다. Object 8은 bit 4만 1이라 0x08이다](/images/study-isobus/48-dpd-bits-dark.png)

Object 8의 트리거 바이트를 단계별로 만들어 보자.

1. 지원하는 트리거는 on change 하나이고, on change는 bit 4다.
2. bit 4의 값은 2의 3제곱, 곧 8이다.
3. 다른 비트는 모두 0이므로 바이트 값은 8이다. 16진수로 쓰면 `0x08`(=8)이다.

Object 7의 속성 바이트도 같은 방법으로 만든다. settable은 bit 2이고 값은 2이므로 `0x02`(=2)다. Object 8은 어떤 속성 비트도 세우지 않아 `0x00`(=0)이다. 4절 표에 Object 7의 트리거가 적혀 있지 않아서 위 표에서는 "확인 불가"로 두었다. 49장에서 이 오브젝트를 바이트로 조립할 때는 트리거를 하나도 세우지 않은 `0x00`으로 둔다.

<strong>Object 7의 Properties 바이트가 `0x02`로 bit2(settable)를 세운 것</strong>이 [45장의 "전체 흐름"](/study/isobus/45-tc-process-data-basics)에서 말한 "DDOP에 없는 DDI는 쓸 수 없다"의 실체다. TC가 `[DDI=1, Element=3, Value=200]`처럼 Value Command(값을 정해 주는 명령)를 내려도, 대상 Element에 연결된 DPD의 Properties 바이트에 bit2가 서 있지 않으면 작업기는 이를 받아들일 근거가 없다. 그래서 작업기는 PDACK(Process Data Acknowledge, 명령을 처리하지 못했을 때 돌려주는 응답) 오류 코드(bit5, "process data가 settable 아님")로 거부한다. PDACK는 [46장](/study/isobus/46-tc-commands-pdack)에서 다뤘다. Object 8은 반대로 bit2가 0이므로 TC가 setpoint로 내릴 수 없고, 오직 작업기가 측정값을 올리는 용도로만 쓰인다.

정리하면, 속성 바이트는 "TC가 이 값을 정해 줄 수 있는가"를, 트리거 바이트는 "작업기가 이 값을 언제 보고할 수 있는가"를 비트로 밝힌다.

<small>근거: ISO 11783-10 A.3, A.4</small>

## 6. DDOP를 나르는 메시지: Device descriptor 명령

이 절에서는 3절에서 본 메시지들이 실제로 어떤 바이트로 시작하는지 본다. DDOP는 살포량 같은 값을 나르는 Process Data 메시지와 같은 PGN(메시지 종류 번호)을 쓴다.

[45장](/study/isobus/45-tc-process-data-basics)에서 다룬 Process Data 메시지(PGN 51968/`0xCB00`, Command 4비트 + Element/DDI/Value)는 살포량 같은 "값"을 나를 때의 구조다. DDOP 자체를 실어 나르는 메시지는 같은 PGN 위에서 <strong>Command 1(Device descriptor)</strong>의 하위 명령(subcommand, 서브커맨드라고도 한다)으로 오간다. Byte 1의 자리 배치는 형식적으로 같다. 하위 4비트가 Command(`0001`)이고, 상위 4비트는 이번엔 Element Number가 아니라 하위 명령을 나타낸다.

4비트를 니블(nibble)이라고 부른다. 16진수 한 자리가 니블 하나다. 그래서 Byte 1을 16진수 두 자리로 쓰면 앞자리가 상위 니블(하위 명령), 뒷자리가 하위 니블(Command)이다.

표 읽는 법: 첫 열은 하위 명령 4비트를 2진수로 쓴 것이다. 그 오른쪽에 Command 1(`0001`)을 이어 붙이면 Byte 1이 된다.

| 하위 명령(Byte 1 bit 8~5) | 메시지 | Byte 1 |
|---|---|---|
| `0000` | Request Structure Label | `0x01` |
| `0110` | Object-pool Transfer(DDOP 본문 전송) | `0x61` |
| `1000` | Object-pool Activate/Deactivate | `0x81` |

Object-pool Transfer의 Byte 1을 단계별로 만들어 보자.

1. 하위 명령 `0110`(=6)을 상위 니블에 놓는다.
2. Command `0001`(=1)을 하위 니블에 놓는다.
3. 이어 붙이면 `0110 0001`이고, 16진수로 `0x61`(=97)이다.

같은 방법으로 `1000`과 `0001`을 이어 붙이면 `0x81`(=129), `0000`과 `0001`을 이어 붙이면 `0x01`(=1)이다.

`0x61`(Object-pool Transfer)로 시작한 메시지의 뒤(Byte 2~n)에 위에서 채운 DVC·DET·DPD·DPT·DVP 오브젝트 레코드들이 이어져 TP(1,785바이트 이하) 또는 ETP(초과 시)로 분할 전송된다. 즉 DDOP 전송과 Process Data 값 전달은 같은 PGN·같은 Command 니블 구조를 공유하되, Command 값(1 vs 2~A)에 따라 그 뒤에 오는 바이트열의 의미가 완전히 달라진다.

Command 1의 하위 명령은 모두 14개다. 여기서 본 3개 말고 나머지는 [50장](/study/isobus/50-ddop-commands-design)에서 본다.

::: details 파이썬으로 검산해 보기
아래 코드는 속성 바이트, 트리거 바이트, Byte 1을 비트 연산으로 만든다. `<<`는 비트를 왼쪽으로 미는 연산이고, `|`는 비트를 합치는 연산이다.

```python
def properties_byte(default=False, settable=False, control_source=False):
    return (int(default) << 0) | (int(settable) << 1) | (int(control_source) << 2)


def trigger_byte(time_interval=False, distance_interval=False,
                  threshold=False, on_change=False, total=False):
    return (
        (int(time_interval) << 0)
        | (int(distance_interval) << 1)
        | (int(threshold) << 2)
        | (int(on_change) << 3)
        | (int(total) << 4)
    )


def device_descriptor_byte1(subcommand):
    command = 1  # Device descriptor
    return (subcommand << 4) | command


# Object 7 (DDI 1 Setpoint): settable만 세운다
print(hex(properties_byte(settable=True)))          # 0x2

# Object 8 (DDI 2 Measurement): settable 없음, on change 트리거
print(hex(properties_byte()))                       # 0x0
print(hex(trigger_byte(on_change=True)))            # 0x8

# Device descriptor 서브커맨드별 Byte 1
print(hex(device_descriptor_byte1(0b0000)))         # 0x1  Request Structure Label
print(hex(device_descriptor_byte1(0b0110)))         # 0x61 Object-pool Transfer
print(hex(device_descriptor_byte1(0b1000)))         # 0x81 Object-pool Activate/Deactivate
```

출력의 `0x2`, `0x0`, `0x8`은 5절 표의 Object 7·8 값과 같다. 마지막 세 줄은 이 절 표의 Byte 1과 같다.
:::

::: tip 핵심 정리
- DDOP(Device Descriptor Object Pool)는 작업기가 TC에게 자기 구조와 능력을 알리는 데이터, 곧 "작업기의 자기소개서"다.
- DDOP는 DVC, DET, DPD, DPT, DVP 다섯 가지 오브젝트로 이루어지고, 오브젝트끼리 Object ID로 서로를 가리켜 나무 구조를 만든다.
- 클라이언트는 연결할 때 자기 Structure Label을 TC에 묻고, TC가 모르는 버전이면 스스로 DDOP 전체를 TP나 ETP로 보낸 뒤 활성화한다.
- TC는 DDOP를 읽어 지원 DDI, 섹션 구성, 작업 폭 등을 파악한 뒤 태스크를 시작한다.
- 3섹션 살포기 예제는 섹션마다 DDI 1(Setpoint), DDI 2(Measurement), DDI 289(Setpoint Work State)를 정의했다. 실제 규칙에 맞춘 설계는 49장과 50장에서 본다.
- DPD 속성 바이트의 bit 2(settable)가 서 있어야 TC가 그 값을 명령할 수 있다.
:::

::: details 확인 문제
1. (개념) DDOP를 "자기소개서"에 빗대는 이유를 한 문장으로 말하라. DDOP가 없으면 TC가 할 수 없는 일 두 가지를 들어라.
2. (구분) 다음은 DVC, DET, DPD, DPT, DVP 가운데 무엇으로 담아야 하나?
   - (a) 섹션 하나의 폭 3 m
   - (b) TC가 바꿔 줄 살포량 목표
   - (c) 원시값 2,000,000을 200.00 L/ha로 보여 주는 규칙
   - (d) Section 2 그 자체
3. (순서) 클라이언트가 처음 연결할 때 보내는 DDOP 관련 요청 네 가지를 순서대로 적어라. TC에 같은 Structure Label의 DDOP가 이미 있으면 어느 단계를 건너뛰나?
4. (계산) DPD의 속성 바이트가 `0x03`이면 어떤 비트가 섰나? 트리거 바이트가 `0x09`(=9)이면 어떤 트리거를 지원하나?
5. (계산) 하위 명령이 `0100`인 Device descriptor 메시지의 Byte 1은 16진수로 얼마인가?

**답 가이드**
1. TC는 버스에 연결된 작업기에 대해 아무것도 모르고, 작업기가 스스로 자기 구조와 능력을 정해진 서식으로 알려 주기 때문이다. DDOP가 없으면 TC는 어떤 명령을 보낼 수 있는지, 처방 맵의 살포량을 어느 DDI로 보낼지, 섹션이 몇 개인지 알 수 없다(이 중 두 가지).
2. (a) DPT (b) DPD(settable 비트를 세운 것) (c) DVP (d) DET(Element Type 4, Section)
3. Request Structure Label → Request Object-pool Transfer → Object-pool Transfer → Object-pool Activate 순이다. 같은 DDOP가 이미 있으면 Request Object-pool Transfer와 Object-pool Transfer를 건너뛰고 바로 Activate를 보낸다.
4. `0x03` = 2 + 1이므로 bit 2와 bit 1이 섰다. default set 멤버이면서 settable이다. `0x09` = 8 + 1이므로 bit 4(on change)와 bit 1(time interval)을 지원한다.
5. `0100`과 `0001`을 이어 붙인 `0100 0001`, 곧 `0x41`(=65)이다. Request Object-pool Transfer이고 [50장](/study/isobus/50-ddop-commands-design)에서 자세히 본다.
:::

## 다음 챕터

- 다음: [49장 DDOP 바이트 구성](/study/isobus/49-ddop-bytes)
