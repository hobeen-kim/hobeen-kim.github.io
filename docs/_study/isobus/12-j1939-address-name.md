---
title: "주소와 NAME: 누가 보냈는지 알아보는 법"
description: "J1939 장치가 프레임마다 싣는 8비트 소스 주소의 범위와 장치의 신원을 담은 64비트 NAME의 필드를 익히고, 실제 NAME 하나를 비트 단위로 풀어 읽는다."
date: 2026-04-13
tags: [ISOBUS, J1939, CAN, 주소, NAME]
prev: /study/isobus/11-j1939-request2-timing
next: /study/isobus/13-j1939-address-claim
---

# 주소와 NAME: 누가 보냈는지 알아보는 법

::: info 학습 목표
- 소스 주소(SA)가 29비트 CAN ID의 어디에 있고, 값의 범위마다 무슨 뜻인지 설명할 수 있다.
- 주소와 NAME이 왜 따로 있고 둘이 어떻게 다른지 설명할 수 있다.
- 64비트 NAME을 이루는 열 개 필드가 각각 무엇을 나타내는지 말할 수 있다.
- 16진수로 적힌 NAME 하나를 비트 단위로 풀어 필드 값을 읽을 수 있다.
- NAME이 CAN 데이터 필드에 실릴 때 바이트 순서가 뒤집히는 이유와 읽는 법을 설명할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [9장 J1939 메시지 구조](/study/isobus/09-j1939-message), [10장 요청과 응답](/study/isobus/10-j1939-request-ack)
- 이 장에서 처음 나오는 말
  - 소스 주소(SA): 메시지를 보낸 장치의 번호. 0~255 가운데 하나다.
  - NAME: 장치마다 하나씩 붙는 64비트 신원 정보. 무슨 장치이고 누가 만들었는지 담는다.
  - CF(Control Function, 제어 기능): 주소 하나를 쓰며 통신하는 기능 단위. ECU 하나에 CF가 여럿 들어 있을 수 있다.
  - 주소 클레임(address claim): CF가 "이 주소는 내가 쓴다"고 네트워크에 알리는 절차. 13장에서 자세히 본다.
  - preferred address(선호 주소): 특정 기능을 맡은 장치가 쓰도록 미리 정해 둔 주소.
  - self-configurable(자체 구성 가능): 원하는 주소를 얻지 못하면 다른 주소를 스스로 골라 옮겨 가는 능력.
:::

택배 상자에 보내는 사람 칸이 있듯, J1939 프레임에는 CAN ID 맨 끝 8비트에 보낸 장치의 주소가 들어간다. 주소는 짧아서 모든 프레임에 싣기 좋지만, 번호만 보고는 그 장치가 엔진인지 파종기인지 알 수 없다. 그래서 장치마다 명함처럼 자기 소개를 담은 64비트 NAME을 따로 둔다. 이 장은 주소와 NAME을 읽는 법을 익히고, 다음 [13장](/study/isobus/13-j1939-address-claim)에서 둘을 짝짓는 절차인 주소 클레임을 본다.

## 1. 주소와 NAME은 왜 둘 다 필요한가

이 절은 장치를 가리키는 두 식별자, 소스 주소와 NAME이 각각 무슨 일을 하는지 큰 그림으로 비교한다. 자세한 규칙은 2절(주소)과 3절(NAME)에서 본다.

CAN 프레임 자체에는 "누가 보냈는지"를 적는 칸이 없다. 그래서 J1939는 29비트 CAN ID의 마지막 8비트를 보낸 장치의 번호로 쓰기로 정했다. 이 번호가 <strong>소스 주소(Source Address, SA)</strong>다. 8비트라 값은 256가지뿐이지만, 짧아서 모든 프레임에 붙여도 부담이 없다.

번호만으로는 모자란 순간이 있다. 두 장치가 같은 주소를 원하면 누가 양보할지 정해야 한다. SA 0x80(=128)을 쓰는 장치가 어느 회사의 무슨 장치인지 알아야 할 때도 있다. 이때 쓰는 것이 <strong>NAME</strong>이다. NAME은 64비트(8바이트)짜리 신원 정보로, 장치의 종류와 기능, 제조사, 일련번호를 담는다. NAME은 일반 프레임에는 실리지 않는다. 주로 장치가 "이 주소는 내가 쓴다"고 알리는 Address Claimed 메시지의 데이터로 나간다. 그 밖에는 13장과 14장에서 볼 몇 가지 주소 관리 메시지에만 실린다.

![주소와 NAME의 관계: Address Claimed가 SA와 NAME의 짝을 알리고, 받는 쪽은 주소-NAME 대응표로 일반 프레임의 SA를 NAME으로 바꿔 읽는다](/images/study-isobus/12-sa-name-link-light.png)
![주소와 NAME의 관계: Address Claimed가 SA와 NAME의 짝을 알리고, 받는 쪽은 주소-NAME 대응표로 일반 프레임의 SA를 NAME으로 바꿔 읽는다](/images/study-isobus/12-sa-name-link-dark.png)

그림을 번호 순서로 읽으면 다음과 같다.

1. 장치가 Address Claimed 메시지로 "SA 0x80은 NAME이 `0xA00882000D27A120`인 내가 쓴다"고 모두에게 알린다. 짝이 CAN ID 끝 8비트(SA)와 데이터 8바이트(NAME)에 함께 실린다.
2. 다른 장치들은 이 짝을 주소-NAME 대응표에 적어 둔다.
3. 그 뒤로 SA가 0x80인 일반 프레임이 오면, 받는 쪽은 대응표에서 NAME을 찾아 보낸 장치가 누구인지 안다.

| 항목 | 소스 주소(SA) | NAME |
|---|---|---|
| 크기 | 8비트(0~255) | 64비트 |
| 실리는 곳 | 모든 프레임의 CAN ID 끝 8비트 | Address Claimed 같은 주소 관리 메시지의 데이터 8바이트 |
| 바뀌는가 | 주소 클레임 결과에 따라 바뀔 수 있다 | 원칙적으로 바뀌지 않는다. 일부 필드만 [14장](/study/isobus/14-name-management-init)의 방법으로 바꿀 수 있다 |
| 알려 주는 것 | 이 프레임을 보낸 자리 | 그 자리에 있는 장치가 누구인가 |
| 비유 | 회의실 좌석 번호 | 명함 |

회의에서 발언자를 "3번 자리"라고 부르면 짧고 편하다. 하지만 3번 자리에 누가 앉았는지는 명함을 봐야 안다. 다만 이 비유가 맞지 않는 점이 하나 있다. 회의실에서는 먼저 앉은 사람이 자리 주인이지만, J1939에서는 같은 자리를 원하는 장치끼리 NAME 값을 비교해 작은 쪽이 자리를 차지한다([13장](/study/isobus/13-j1939-address-claim)).

정리하면, SA는 프레임마다 붙는 짧은 자리 번호이고 NAME은 그 자리에 있는 장치의 신원이다. 둘을 이어 주는 것이 주소 클레임이다.

## 2. 소스 주소(SA)

이 절은 SA가 CAN ID의 어디에 있는지, 그리고 256개 값이 어떤 용도로 나뉘어 있는지 본다.

J1939 네트워크에서 모든 ECU는 <strong>소스 주소(Source Address, SA)</strong>를 가진다. SA는 8비트 값으로, 29비트 CAN ID의 <strong>하위 8비트(비트 7~0)</strong>에 위치한다. 정확히 말하면 주소는 ECU 안의 CF마다 하나씩이다. ECU 하나가 CF를 여럿 담으면 주소도 여럿 쓴다.

![29비트 CAN Identifier 비트 필드 배치](/images/study-isobus/10-can-id-bitfields-light.png)
![29비트 CAN Identifier 비트 필드 배치](/images/study-isobus/10-can-id-bitfields-dark.png)

그림은 왼쪽 끝이 최상위 비트(MSB, bit 28), 오른쪽 끝이 최하위 비트(LSB, bit 0)다. 아래 대괄호는 필드가 차지하는 비트 번호다. Priority(우선순위), R(예약 비트), DP(Data Page), PF(PDU Format, 메시지 종류를 고르는 8비트), PS(PDU Specific, 목적지 주소 DA 또는 그룹 확장 GE)는 [9장](/study/isobus/09-j1939-message)에서 봤다. 색을 칠한 마지막 8비트가 SA다.

실제 ID 하나로 확인해 보자. 다음 그림은 [13장](/study/isobus/13-j1939-address-claim)에서 다시 만날 Address Claimed 프레임의 ID `0x18EEFF80`을 비트로 펼쳐 필드별로 나눈 것이다.

![CAN ID 0x18EEFF80을 29비트로 펼친 모습: Priority 6, R 0, DP 0, PF 0xEE, PS 0xFF, 마지막 8비트 SA 0x80](/images/study-isobus/12-can-id-sa-light.png)
![CAN ID 0x18EEFF80을 29비트로 펼친 모습: Priority 6, R 0, DP 0, PF 0xEE, PS 0xFF, 마지막 8비트 SA 0x80](/images/study-isobus/12-can-id-sa-dark.png)

- Priority `110`은 6, R과 DP는 0이다.
- PF `0xEE`(=238)는 이 프레임이 Address Claimed 메시지라는 뜻이다.
- PS `0xFF`(=255)는 목적지가 "모두"라는 뜻이다.
- 마지막 8비트 `1000 0000`이 SA `0x80`(=128)이다.

16진수 한 자리는 4비트이므로 끝 두 자리가 정확히 마지막 8비트다. 그래서 CAN ID를 16진수로 적어 두면 끝 두 자리 `80`만 보고도 보낸 장치의 주소를 알 수 있다. 버스 로그를 읽을 때 가장 먼저 쓰는 요령이다.

### SA 값 범위

256개 값은 용도별로 나뉜다. 아래 표의 범위는 10진수다.

| 범위 | 의미 |
|------|------|
| 0 ~ 127, 248 ~ 253 | Preferred address 영역: 이 범위를 클레임하는 장치는 해당 주소에 정의된 기능을 실제로 수행해야 한다 |
| 128 ~ 247 | Self-configurable address 범위: preferred address가 없거나 클레임에 실패한 장치가 사용 |
| 254 (0xFE) | Null Address: <strong>소스 주소로만</strong> 사용. 주소 클레임 전, 또는 클레임 실패 시 |
| 255 (0xFF) | Global Address: <strong>목적지 주소로만</strong> 사용 (브로드캐스트) |

![SA 0~255의 용도 지도: 0~127과 248~253은 preferred, 128~247은 self-configurable(128~237은 작업기 CF, 238~247은 윗부분), 254는 NULL, 255는 Global](/images/study-isobus/12-sa-range-map-light.png)
![SA 0~255의 용도 지도: 0~127과 248~253은 preferred, 128~247은 self-configurable(128~237은 작업기 CF, 238~247은 윗부분), 254는 NULL, 255는 Global](/images/study-isobus/12-sa-range-map-dark.png)

그림은 0~255를 왼쪽에서 오른쪽으로 늘어놓고 용도별로 칠한 지도다. 칸의 폭은 읽기 쉽게 조정했으므로 값의 개수에 비례하지 않는다. 아래 괄호의 128~237과 238~247 구분은 뒤의 "범위별 세부 규칙"에서 다룬다.

254와 255는 장치에 배정하는 주소가 아니라 미리 약속한 특수값이다.

- 254(`0xFE`, NULL 주소)는 "아직 주소가 없음"을 뜻한다. 주소를 얻기 전이거나 얻지 못한 CF가 보내는 두 가지 메시지(Request for Address Claimed, Cannot Claim Address)의 SA 칸에만 쓴다. 두 메시지는 13장에서 본다.
- 255(`0xFF`, Global 주소)는 "모두에게"를 뜻한다. 목적지 칸(PS)에만 쓰며, 이 값을 목적지로 한 메시지는 네트워크의 모든 CF가 받는다. 이렇게 모두에게 보내는 것을 브로드캐스트라고 한다.

### 예약된 주소 (일부)

preferred address는 특정 기능에 미리 배정해 둔 주소다. 예를 들어 엔진은 0번이고, VT(Virtual Terminal, 작업기 화면을 운전석에 띄우는 단말기)는 38번, TC(Task Controller, 작업 기록과 처방을 맡는 장치)는 247번이다. 아래 표에서 `0x` 뒤의 값은 같은 주소의 16진수 표기다.

| SA | 장치 |
|----|------|
| 0 (0x00) | Engine #1 |
| 3 (0x03) | Transmission #1 |
| 23 (0x17) | Instrument Cluster #1 |
| 33 (0x21) | Body Controller |
| 38 (0x26) | Virtual Terminal (ISOBUS) |
| 49 (0x31) | Cab Controller (Primary) |
| 247 (0xF7) | Task Controller (ISOBUS) |

예약(preferred) 주소는 <strong>우선권</strong>을 가지지 않는다. 주소 클레임 경쟁에서는 NAME 값이 작은 쪽이 이긴다. 예약 주소라도 더 작은 NAME을 가진 장치가 있으면 양보해야 한다. 기능 판단도 SA가 아니라 반드시 NAME으로 해야 한다.

참고로 <strong>ISOBUS(ISO 11783) 적합 장치는 self-configurable address 능력이 필수</strong>이며, non-configurable 장치는 J1939·구판 호환을 위해 허용될 뿐이다. non-configurable은 정해진 주소 하나만 쓰고 다른 주소로 옮기지 못하는 장치를 말한다.

::: warning 주소로 기능을 추론하지 않는다
표준은 CF가 수행하는 기능을 SA만 보고 추론해서는 안 되며 기능은 NAME으로만 판단한다고 못 박는다. 표준의 첫 판(2001)은 주소와 기능의 관계를 강제하지 않았다는 설명도 붙어 있다. 그러니 "SA가 38이면 VT"처럼 주소 상수로 상대를 찾는 코드는 규정 위반이다. 상대의 NAME을 Address Claimed로 확인한 다음 그때의 SA를 쓴다.
:::

### 범위별 세부 규칙 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

위 표의 경계마다 따라붙는 규정이 있다. 구현할 때 실제로 걸리는 것은 표의 숫자보다 이 규정들이다. 규정은 대부분 ISO 11783-5(ISOBUS의 네트워크 관리 표준. 주소와 NAME, 주소 클레임 규칙을 정한다. 이하 Part 5)에 있다. 작업기 주소 수 제한 하나만 ISO 11783-1(ISOBUS 네트워크 전체의 요구사항을 정하는 문서. 이하 Part 1)에 있다.

| 범위 | 붙어 있는 규정 |
|---|---|
| 0~127, 248~253 (preferred) | 이 주소를 클레임한 CF는 그 주소에 배정된 기능을 실제로 수행해야 하고, 같은 기능을 NAME에도 적어야 한다. 이미 다른 CF가 쓰고 있으면 능력에 따라 다른 주소를 클레임하거나 Cannot Claim Address를 보낸다 |
| 128~247 (self-configurable) | preferred address가 없거나 그것을 얻지 못한 CF가 쓰는 120개다. 이 범위에서 주소를 고르는 CF는 self-configurable 능력을 갖춰야 한다 |
| 128~247의 윗부분 | Industry Group 2(농업·임업) 기능의 preferred address로 정의된 주소가 섞여 있다. 그 기능에 잠긴 주소는 아니라서 어느 self-configurable CF든 쓸 수 있지만, 밀려나 새 주소를 고르는 CF는 아래쪽부터 시도하고 아래쪽이 다 찼을 때만 이 영역을 쓰도록 권장한다 |
| 128~237 | 연결된 작업기에서 쓰는 CF 수는 이 110개 주소 안으로 제한해야 한다. Part 1의 규정이다 |
| 254 (NULL) | 소스 주소로만 쓰고, 그것도 Request for Address Claimed와 Cannot Claim Address 두 메시지의 SA에서만 허용된다 |
| 255 (Global) | 목적지 주소로만 쓴다 |

Part 5는 "윗부분"이 정확히 어디부터인지 적지 않는다. 다만 Part 1이 작업기 CF를 128~237로 묶는다. 또 같은 문서의 네트워크 구성 예는 TC를 247, TECU(트랙터 ECU. 트랙터 네트워크와 작업기 네트워크를 잇는 장치)를 240에 둔다. 이를 보면 238~247의 10개를 TC·TECU 같은 Industry Group 2 preferred 기능 몫으로 남겨 두는 구성으로 읽힌다(추론). 그 네트워크 구성 예는 [19장](/study/isobus/19-isobus-part1-requirements)에서 그림으로 다시 본다.

<strong>initial address</strong>(전원을 켤 때 처음 클레임을 시도하는 주소)에도 규칙이 있다. 생산 시점에는 preferred address로 설정하고, 시스템 구성을 위해 다시 프로그램할 수 있다. 그리고 새 주소를 클레임하게 되면 그 주소를 이후 모든 전원 인가에서 쓸 initial address로 저장해야 한다. 새 주소가 주소 중재(같은 주소를 원하는 CF끼리 NAME으로 승패를 가르는 일)의 결과든 Commanded Address(다른 장치가 주소를 지정해 주는 메시지)의 결과든 마찬가지다. preferred address를 배정받은 CF도 예외가 아니다. 주소 중재와 Commanded Address는 13장에서 본다.

<small>근거: ISO 11783-5:2019 4.2.1, 4.2.3, 4.3.3.2~4.3.3.6, 4.4.1, ISO 11783-1:2017 6.6.4</small>

## 3. NAME: 장치의 64비트 명함

이 절은 NAME이 무엇이고 왜 필요한지 본 뒤, 열 개 필드를 하나씩 살피고 실제 NAME 하나를 끝까지 풀어 읽는다.

<strong>NAME</strong>은 J1939 네트워크에서 ECU를 전 세계적으로 고유하게 식별하는 64비트 구조체이다. 주소 클레임 시 충돌이 발생하면 NAME 값을 비교해 우선순위를 결정한다. NAME 값이 <strong>수치적으로 더 작은</strong> 장치가 주소를 획득한다.

NAME은 명함과 닮았다. 명함에 업종, 부서, 직함, 회사 이름, 사원 번호가 정해진 자리에 적혀 있듯, NAME에도 산업 분야, 장치 종류, 기능, 제조사, 일련번호가 정해진 비트 자리에 들어간다. 명함과 다른 점은 NAME 전체를 하나의 큰 숫자로도 읽는다는 것이다. 두 장치가 같은 주소를 원하면 이 숫자가 작은 쪽이 이긴다.

### NAME은 열 개의 칸으로 나뉜다

![64비트 NAME 필드 구성: MSB(bit 63) AAC부터 LSB(bit 0) Identity Number까지](/images/study-isobus/10-name-fields-light.png)
![64비트 NAME 필드 구성: MSB(bit 63) AAC부터 LSB(bit 0) Identity Number까지](/images/study-isobus/10-name-fields-dark.png)

| 필드 | 비트 수 | 위치 (MSB 기준) | 설명 |
|------|---------|-----------------|------|
| Arbitrary Address Capable (AAC) | 1 | bit 63 | 1이면 자동 주소 재할당 가능 |
| Industry Group (IG) | 3 | bit 62~60 | 0=Global, 2=Agricultural |
| Vehicle System Instance (VSI) | 4 | bit 59~56 | 동일 시스템 여러 개 구분 |
| Vehicle System (VS) | 7 | bit 55~49 | 시스템 유형 (예: 트랙터) |
| Reserved | 1 | bit 48 | 항상 0 |
| Function (F) | 8 | bit 47~40 | 장치 기능 (예: 엔진 제어) |
| Function Instance (FI) | 5 | bit 39~35 | 동일 기능 여러 개 구분 |
| ECU Instance (EI) | 3 | bit 34~32 | 동일 장치 내 ECU 구분 |
| Manufacturer Code | 11 | bit 31~21 | 제조사 코드 (SAE J1939 등록) |
| Identity Number | 21 | bit 20~0 | 제조사 내 일련번호 |

표 읽는 법: 64비트에 맨 앞(가장 높은 자리)부터 bit 63, bit 62, … 하고 번호를 매겨 맨 끝이 bit 0이다. 위치 열의 "bit 62~60"은 위에서 둘째부터 넷째까지 세 비트를 차지한다는 뜻이다. 비트 수 열을 모두 더하면 1+3+4+7+1+8+5+3+11+21 = 64다.

이름에 관해 하나 짚어 둔다. 이 표와 위 그림은 SAE J1939(트럭·버스용으로 먼저 만들어진 원조 표준)가 붙인 이름을 썼다. ISOBUS 표준인 ISO 11783-5는 같은 칸을 다른 이름으로 부른다. 두 이름의 대응은 뒤의 "ISO 11783-5의 필드 이름과 값 범위" 표에 모았다. 이 장부터는 ISO 11783의 이름을 쓴다. VSI는 device class instance, VS는 device class다. 맨 앞 1비트만은 짧게 AAC라고 부른다. ISO 11783은 이 비트를 Self-configurable address라고 부르며, AAC가 1이면 self-configurable 장치다.

### 필드마다 왜 있는가

열 개 필드는 네 가지 질문에 답한다. 아래 표는 질문별로 필드를 묶고, 각 필드가 왜 있는지 예와 함께 적은 것이다.

| 질문 | 필드(비트 수) | 하는 일 | 예 |
|---|---|---|---|
| 주소를 스스로 바꿀 수 있나 | AAC (1) | 1이면 원하는 주소를 얻지 못했을 때 다른 주소로 옮겨 갈 수 있다 | ISOBUS 장치는 1이어야 한다 |
| 무슨 장치인가 | Industry group (3) | 장비가 속한 산업. 같은 device class 번호라도 산업마다 뜻이 다르므로 산업부터 정한다 | 0은 모든 산업 공통, 2는 농업·임업 장비 |
| 무슨 장치인가 | Device class (7) | 장치의 종류 | 농업 장비에서 4는 파종기 |
| 무슨 장치인가 | Function (8) | 그 장치에서 맡은 기능 | 0은 엔진 |
| 몇 번째인가 | Device class instance (4) | 같은 종류 장치가 여러 대일 때 몇 번째인지 | 파종기 2대면 0과 1 |
| 몇 번째인가 | Function instance (5) | 같은 기능이 여러 개일 때 몇 번째인지 | 파종기의 1~8행이면 0~7 |
| 몇 번째인가 | ECU instance (3) | 한 기능을 ECU 여럿이 나눠 맡을 때 몇 번째 ECU인지 | 행마다 ECU가 2개면 0과 1 |
| 누가 만든 어느 제품인가 | Manufacturer code (11) | 제조사 번호. 표준 위원회가 배정한다 | 이 스터디의 예시 값 105, 320 |
| 누가 만든 어느 제품인가 | Identity number (21) | 제조사가 붙이는 일련번호. 같은 모델 두 대를 구분한다 | 이 스터디의 예시 값 500000 |
| (빈 자리) | Reserved (1) | 나중을 위해 비워 둔 자리 | 항상 0 |

"무슨 장치인가"에 답하는 세 필드는 큰 분류에서 작은 분류로 좁혀 간다. 산업(농업) → 장치 종류(파종기) → 기능 순서다. "몇 번째인가"에 답하는 instance 필드 셋은 같은 것이 여럿일 때 서로를 구분한다.

필드의 순서에도 뜻이 있다. NAME을 하나의 64비트 숫자로 보고 크기를 비교하면, 앞(높은 자리)에 있는 필드가 먼저 승패를 가른다. 맨 앞의 AAC가 0인 장치(주소를 못 바꾸는 장치)의 NAME은 AAC가 1인 장치의 NAME보다 언제나 작다. 그래서 주소를 다투면 AAC가 0인 쪽이 이긴다. 자세한 비교는 13장에서 본다.

### NAME을 바이트로 나누어 읽기

NAME은 보통 16진수 16자리로 적는다. 16진수 두 자리가 1바이트이므로 16자리는 8바이트다. NAME을 바이트로 나눌 때는 맨 앞(최상위) 바이트를 Byte 8, 맨 끝 바이트를 Byte 1이라고 부른다. 번호가 거꾸로인 까닭은 버스에 실리는 순서 때문인데, 이 절 뒤쪽의 "NAME은 Byte 1부터 버스에 실린다"에서 본다. NAME은 64비트나 되는 큰 수라 10진수로 바꾸지 않고, 필드별로 잘라 읽는다.

가장 단순한 예부터 보자. NAME 값 `0x2000000000000000`은 Arbitrary Address Capable = 0, Industry Group = 2(Agricultural equipment), Function = 0(Engine), Manufacturer Code = 0, Identity Number = 0을 뜻한다. 최상위 바이트(Byte 8) `0x20`을 8비트로 분해하면 AAC·IG·VSI 값을 얻을 수 있다.

![NAME=0x2000000000000000의 Byte 8(0x20)을 AAC·IG·VSI로 분해](/images/study-isobus/10-name-example-light.png)
![NAME=0x2000000000000000의 Byte 8(0x20)을 AAC·IG·VSI로 분해](/images/study-isobus/10-name-example-dark.png)

`0x20`(=32)을 2진수로 쓰면 `0010 0000`이다. 앞의 1비트 `0`이 AAC, 다음 3비트 `010`(=2)이 Industry group, 나머지 4비트 `0000`이 device class instance(그림의 VSI)다. 나머지 7바이트는 모두 `00`이라 device class, function, manufacturer code, identity number도 모두 0이다.

### 실제 NAME 하나를 비트 단위로 읽기

이번에는 모든 필드에 값이 든 NAME을 끝까지 풀어 본다. 대상은 `0xA00882000D27A120`이다. 13장의 주소 클레임 예에서 "그린텍 파종기 컨트롤러"의 NAME(NAME_A)으로 다시 나오는 값이다. 순서는 네 단계다.

1. 16진수 16자리를 두 자리씩 끊어 8바이트로 나눈다. 앞에서부터 Byte 8, Byte 7, …, Byte 1이다.
2. 바이트마다 2진수 8비트로 바꾼다. 16진수 한 자리는 2진수 4비트다(`A` = `1010`, `D` = `1101`, `0` = `0000`).
3. 이어 붙인 64비트를 필드 경계에서 자른다. 앞에서부터 1, 3, 4, 7, 1, 8, 5, 3, 11, 21비트씩이다.
4. 잘라 낸 조각을 10진수로 바꾼다.

1~2단계의 결과는 다음과 같다.

| 바이트 | 16진수 | 2진수 |
|---|---|---|
| Byte 8 | `A0` | `1010 0000` |
| Byte 7 | `08` | `0000 1000` |
| Byte 6 | `82` | `1000 0010` |
| Byte 5 | `00` | `0000 0000` |
| Byte 4 | `0D` | `0000 1101` |
| Byte 3 | `27` | `0010 0111` |
| Byte 2 | `A1` | `1010 0001` |
| Byte 1 | `20` | `0010 0000` |

3단계는 그림으로 보면 쉽다. 위 줄이 8바이트, 가운데 줄이 64비트, 아래 줄이 필드 경계에서 자른 결과다. 색은 앞 절 표의 네 가지 질문을 나타낸다.

![NAME 0xA00882000D27A120을 64비트로 펼쳐 필드별로 자른 모습: AAC 1, IG 2, DCI 0, DC 4, R 0, Function 130, FI 0, EI 0, MC 105, Identity number 500000](/images/study-isobus/12-name-decode-light.png)
![NAME 0xA00882000D27A120을 64비트로 펼쳐 필드별로 자른 모습: AAC 1, IG 2, DCI 0, DC 4, R 0, Function 130, FI 0, EI 0, MC 105, Identity number 500000](/images/study-isobus/12-name-decode-dark.png)

4단계까지 마친 결과다.

| 필드 | 비트 위치 | 잘라 낸 비트 | 값 | 뜻 |
|---|---|---|---|---|
| AAC | 63 | `1` | 1 | self-configurable. 주소를 스스로 옮길 수 있다 |
| Industry group | 62~60 | `010` | 2 | 농업·임업 장비 |
| Device class instance | 59~56 | `0000` | 0 | 같은 종류의 첫째 장치 |
| Device class | 55~49 | `0000100` | 4 | 파종기 |
| Reserved | 48 | `0` | 0 | 규칙대로 0 |
| Function | 47~40 | `1000 0010` | 130 | 기능 번호 130(이 스터디의 예시 값) |
| Function instance | 39~35 | `00000` | 0 | 첫째 |
| ECU instance | 34~32 | `000` | 0 | 첫째 ECU |
| Manufacturer code | 31~21 | `0000 1101 001` | 105 | 제조사 105(예시 값) |
| Identity number | 20~0 | `0 0111 1010 0001 0010 0000` | 500000 | 일련번호 |

헷갈리기 쉬운 곳은 필드가 바이트 경계와 어긋나는 자리다.

- Byte 8은 AAC(1) + Industry group(3) + device class instance(4)로 딱 8비트다. `1010 0000`을 `1 | 010 | 0000`으로 나눈다.
- Byte 7은 device class(7)와 Reserved(1)다. `0000 1000`을 `0000100 | 0`으로 나누면 device class가 4다. 그래서 Byte 7은 device class의 두 배(4 × 2 = 8 = `0x08`)가 된다.
- Manufacturer code 11비트는 Byte 4 전체(`0000 1101`)와 Byte 3의 위쪽 3비트(`001`)에 걸친다. `0x0D`는 13이고, 3비트를 덧붙이면 13 × 8 + 1 = 105다.
- Identity number 21비트는 Byte 3의 아래쪽 5비트(`00111`)와 Byte 2, Byte 1 전체다. 16진수로 모으면 `0x07A120`이고, 10진수로는 7 × 65536 + 0xA1 × 256 + 0x20 = 458752 + 41216 + 32 = 500000이다.

이 NAME은 "농업 장비(IG 2) 가운데 파종기(device class 4)의 첫째 장치에서, 기능 130을 맡은 첫째 ECU이고, 제조사 105가 일련번호 500000을 붙였으며, 주소를 스스로 옮길 수 있다"로 읽힌다.

### ISO 11783-5의 필드 이름과 값 범위

위 표는 J1939식 이름(AAC, Vehicle System…)을 썼다. ISO 11783-5는 같은 자리를 다른 이름으로 부르므로, 표준 원문·데이터베이스·다른 챕터를 오갈 때 헷갈리지 않도록 대응을 정리한다. SPN과 바이트 위치까지 담은 전체 표는 ISO 11783-5를 정리한 [Part 5 부록](/study/isobus/appendix-iso-part05)에 있다.

| 이 절의 표기 | ISO 11783-5 이름 | 비트 | 값 범위 | 누가 정하나 / 무엇에 의존하나 |
|---|---|---|---|---|
| AAC | Self-configurable address | 1 | 0~1 | CF의 실제 능력. 언제나 알려진 값이어야 하고 능력과 맞게 설정해야 한다 |
| IG | Industry group | 3 | 0~7 | ISO가 정의·할당. 다른 필드에 의존하지 않는다 |
| VSI | Device class instance | 4 | 0~15 | 연결된 네트워크에서 같은 device class의 몇 번째인지. 해석은 industry group에 따른다 |
| VS | Device class | 7 | 0~127 | ISO가 정의·할당. industry group과 묶여야 "농업 장비의 파종기" 같은 뜻이 된다 |
| Reserved | Reserved | 1 | 0 | ISO 예약. 0으로 둬야 한다 |
| Function | Function | 8 | 0~255 | ISO가 정의·할당. 0~127은 다른 필드와 무관하고, 128~253은 device class에 따라 뜻이 달라진다 |
| FI | Function instance | 5 | 0~31 | 한 장치 시스템에서 같은 function의 몇 번째인지 |
| EI | ECU instance | 3 | 0~7 | 한 function에 딸린 ECU 무리 중 어느 ECU인지 |
| Manufacturer Code | Manufacturer code | 11 | 0~2047 | 위원회가 할당(Part 1의 데이터베이스). 다른 필드와 독립 |
| Identity Number | Identity number | 21 | 0~2,097,151 | ECU 제조사가 할당. manufacturer code에 의존 |

표의 "Part 1의 데이터베이스"는 ISO 11783-1(ISOBUS 네트워크 전체의 요구사항을 정하는 문서)이 가리키는 코드 값 데이터베이스로, isobus.net에서 공개한다([19장](/study/isobus/19-isobus-part1-requirements)). 값 범위 열은 비트 폭에서 계산한 것이다. 예를 들어 4비트로 나타낼 수 있는 값은 0~15다. 표준의 NAME 정의 표에는 값 범위가 따로 적혀 있지 않다. 그림과 코드에서 device class instance를 DCI, device class를 DC로 줄여 쓰기도 한다.

### Function 코드는 device class에 매인다

Function 필드 8비트는 값의 구간마다 뜻을 정하는 방식이 다르다.

- <strong>0~127</strong>: 다른 어떤 필드와도 무관하게 정의된다. 엔진(function 0)이 예다. 표준은 이 범위의 function(엔진 등)이라면 industry group 0이 아닌 다른 industry group에서도 쓰일 수 있다고 덧붙인다.
- <strong>128~253</strong>: device class에 따라 뜻이 정해진다. 이 절 끝의 NAME 조립 예 A.2에서 129는 "트레일러(device class 2)의 ABS"다. 같은 129라도 device class가 다르면 다른 기능이다.
- <strong>254·255</strong>: 표준의 NAME 정의는 뜻을 정하지 않는다. [14장](/study/isobus/14-name-management-init)의 NAME management에서도 바꿔 넣을 수 있는 function 값의 범위는 0~254다.

device class 자체가 industry group에 의존하므로, 128 이상인 function을 해석하려면 (industry group, device class, function) 세 값을 함께 봐야 한다. NAME을 사람이 읽는 이름으로 바꾸는 표시 기능을 만든다면, 조회 키는 function 하나가 아니라 이 세 값의 조합이어야 한다는 뜻이다. 앞에서 읽은 NAME_A의 function 130도 128 이상이므로, "농업 장비의 파종기"라는 조합 안에서만 뜻이 정해진다.

### 필드끼리의 의존 관계와 instance 운용 규칙 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

표준은 어떤 필드가 다른 어떤 필드에 기대어 뜻이 정해지는지를 그림으로 정리해 두었다. 그 관계를 표로 옮기면 다음과 같다.

| 필드 | 의존하는 필드 |
|---|---|
| Self-configurable address, Industry group, Reserved, Function 0~127, Manufacturer code | 없음(독립 필드) |
| Device class | Industry group |
| Device class instance | Device class (표준의 필드 설명 문구로는 industry group) |
| Function 128~253 | Device class |
| Function instance | Function |
| ECU instance | Function instance |
| Identity number | Manufacturer code |

instance 필드를 운용하는 규칙도 표준에 있다.

- instance 필드는 ECU를 설치할 때, 또는 네트워크에 같은 것이 여럿 있을 때 NAME management 메시지로 바꿔 다시 구성할 수 있다([14장](/study/isobus/14-name-management-init)).
- function instance의 해석은 제조사와 시스템 통합자가 합의해 정할 수 있다. 표준의 예는 엔진 2개·변속기 2개 구성에서 "엔진 instance 0은 변속기 instance 0과, 엔진 instance 1은 변속기 instance 1과 물리적으로 연결한다"고 합의하는 경우다. 위치나 특수 기능을 표시하는 데 쓰기도 한다.
- 한 function을 같은 네트워크의 ECU 두 개가 나눠 맡으면 첫째 ECU의 ECU instance를 0, 둘째를 1로 두는 것이 권장(should)이다.

### NAME 유일성 규칙

이 절은 왜 NAME이 네트워크에서 하나뿐이어야 하는지, 그 책임이 누구에게 있는지 본다.

NAME 비교가 주소 중재(같은 주소를 원하는 CF 사이에서 누가 가질지 정하는 일)의 유일한 기준이므로, NAME이 똑같은 두 CF 사이에서는 중재가 승패를 가르지 못한다(추론). 그래서 표준은 유일성을 여러 겹으로 요구한다.

1. 네트워크에서 메시지를 보내는 모든 CF는 유일한 NAME을 가져야 한다.
2. 그 유일성을 보장할 책임은 네트워크 통합자와 ECU 제조사에게 있다.
3. ECU 제조사는 NAME이 전원을 끊어도 바뀌지 않게(non-varying) 해야 한다. NAME은 비휘발성 저장소에 둬야 한다는 뜻이다.
4. 다른 필드가 모두 다른 CF와 같아질 수 있는 경우에는 identity number(제품 일련번호, 날짜·시각 코드 등)로 유일하게 만들어야 한다.
5. identity number는 최초 제조 후 바꾸지 않는다. NAME management로도 이 필드는 바꿀 수 없다.
6. ECU 하나가 CF 여러 개를 구현하면 CF마다 NAME이 따로 있고 각자 유일한 SA를 클레임한다. 주소 구성 능력도 CF마다 다를 수 있다.

중복 NAME이나 중복 클레임은 진단 툴이 Request for Address Claimed(모든 CF에게 자기 주소와 NAME을 다시 알려 달라고 요청하는 메시지, 13장)를 보내 응답을 모아 보면 찾아낼 수 있다.

::: warning 같은 제품 두 대 = 같은 NAME?
같은 제조사의 같은 모델 두 대를 한 버스에 물리면 identity number를 뺀 필드가 전부 같다. identity number를 일련번호에서 가져오지 않고 펌웨어 상수로 박아 두면 두 대의 NAME이 완전히 같아진다. 4번 규칙이 막으려는 것이 바로 이 경우다.
:::

### NAME은 Byte 1부터 버스에 실린다

이 절은 NAME이 CAN 데이터 필드에 실릴 때의 바이트 순서를 본다. 버스 로그에서 NAME을 읽으려면 꼭 알아야 한다.

NAME을 64비트 정수로 쓸 때 맨 앞(최상위)은 Self-configurable address 비트다. 그런데 Address Claimed의 데이터 필드에서 그 최상위 바이트는 <strong>Byte 8</strong>이고, 맨 먼저 전송되는 Byte 1은 identity number의 최하위 바이트다. 표준은 이를 비트 단위로도 못 박는다. Byte 1의 bit 8은 DLC(데이터 길이 코드)에 가장 가까운 비트, 곧 데이터 필드에서 처음 나가는 비트다. Byte 8의 bit 1은 마지막으로 나가는 데이터 비트로 CRC(오류 검출 코드)에 가장 가깝다. 표준은 NAME을 숫자처럼 다룰 수 있게 이렇게 배치했다고 설명한다. 이 배치는 ISO 11783-7(트랙터와 작업기 사이의 메시지를 정하는 문서)과 같은 방식이다.

앞에서 비트 단위로 읽은 NAME_A로 확인해 보자. `NAME_A = 0xA00882000D27A120`은 수치 표기이고, 실제 Address Claimed 프레임의 데이터는 바이트 순서가 거꾸로다.

| 표기 | 바이트 열 |
|---|---|
| 64비트 수치(최상위 Byte 8부터) | `A0 08 82 00 0D 27 A1 20` |
| CAN 데이터 필드(Byte 1부터 전송 순서) | `20 A1 27 0D 00 82 08 A0` |

![NAME_A의 두 표기: 수치로 적을 때는 Byte 8(A0)이 맨 앞이고, CAN 데이터 필드에서는 Byte 1(20)이 먼저 나가 바이트 순서가 거꾸로 된다](/images/study-isobus/12-name-wire-order-light.png)
![NAME_A의 두 표기: 수치로 적을 때는 Byte 8(A0)이 맨 앞이고, CAN 데이터 필드에서는 Byte 1(20)이 먼저 나가 바이트 순서가 거꾸로 된다](/images/study-isobus/12-name-wire-order-dark.png)

여러 바이트로 된 값을 낮은 자리 바이트부터 늘어놓는 순서를 리틀 엔디언(little endian)이라고 한다. 수신한 8바이트를 NAME 정수로 바꿀 때는 리틀 엔디언으로 읽어야 한다. 곧 첫 바이트 `20`을 가장 낮은 자리에, 마지막 바이트 `A0`을 가장 높은 자리에 놓는다. 이렇게 읽은 정수를 그대로 비교하면 [13장](/study/isobus/13-j1939-address-claim)에서 볼 "NAME 비교 = 64비트 정수 비교"가 성립한다. 반대로 데이터 필드를 받은 순서대로(빅 엔디언으로) 정수화하면 identity number의 하위 바이트가 최상위로 올라가 승패 판정이 틀어진다.

다음 코드는 NAME_A를 전송 순서의 바이트 열로 바꾸고, 그 바이트 열에서 NAME을 다시 복원해 본다.

::: details 파이썬으로 바이트 순서 검산
```python
NAME_A = 0xA00882000D27A120
wire = NAME_A.to_bytes(8, "little")              # Byte 1이 맨 앞
print(" ".join(f"{b:02X}" for b in wire))        # 20 A1 27 0D 00 82 08 A0
assert int.from_bytes(wire, "little") == NAME_A  # 수신 측 복원
assert wire[7] >> 7 == 1                         # Byte 8의 bit 8 = self-configurable address
```
:::

`to_bytes(8, "little")`이 리틀 엔디언으로 바꾸는 부분이고, 출력 `20 A1 27 0D 00 82 08 A0`이 위 표의 CAN 데이터 필드와 같다. 마지막 줄은 전송 순서로 8번째 바이트(`A0`)의 맨 위 비트가 AAC(=1)라는 것을 확인한다.

### 표준의 NAME 조립 예 세 가지 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

ISO 11783-5는 부록에 NAME을 조립하는 예 세 가지를 이진수로 싣고 A.1~A.3이라는 번호를 붙였다. 아래 표와 코드도 그 번호로 부른다. manufacturer code와 identity number는 제조사마다 달라 일반형(`mm…m`, `ii…i`)으로 두었으므로, 여기서는 상위 4바이트(Byte 8~5)만 16진수로 옮긴다.

| 예 | 조건 | Byte 8 | Byte 7 | Byte 6 | Byte 5 |
|---|---|---|---|---|---|
| A.1 단일 엔진 트랙터의 엔진 ECU | non-configurable, IG 0, device class 1(tractor), function 0(engine), instance 모두 0 | `00` | `02` | `00` | `00` |
| A.2 대형 도로용 트랙터의 첫 트레일러 ABS ECU | non-configurable, IG 0, device class 2(trailer), function 129(트레일러 ABS), instance 모두 0 | `00` | `04` | `81` | `00` |
| A.3 파종기 1, 1번 행, ECU 1 | self-configurable, IG 2, device class 4(planter), instance 모두 0 | `A0` | `08` | (미정) | `00` |

Byte 7이 `02`·`04`·`08`처럼 device class의 두 배로 나오는 것은 device class 7비트가 bit 8~2에 놓이고 bit 1이 Reserved(0)이기 때문이다. 앞에서 NAME_A의 Byte 7을 읽을 때 본 것과 같다.

A.3은 instance 필드 3종을 함께 쓰는 예라 구현자에게 특히 쓸모가 있다. 파종기 2대가 각각 8행을 따로 유도(row guidance)하고, 행마다 ECU가 2개다. 파종기는 농업 작업기이므로 self-configurable 비트를 1로 둔다. row guidance의 function 코드는 원문 작성 시점에 정의되지 않아 `ff…f`로 일반화되어 있다.

| 필드 | 무엇을 구분하나 | 값 |
|---|---|---|
| Device class instance | 파종기 1·2 | 0, 1 |
| Function instance | 행 1~8 | 0~7 |
| ECU instance | 행마다 ECU 1·2 | 0, 1 |
| Identity number | CF마다 다르게 | `ii…i`, `ii…i+n`, `ii…i+p`, … |

이 셋을 조합하면 2 × 8 × 2 = 32개 CF가 identity number 없이도 상위 4바이트만으로 모두 구분된다. Byte 5는 `(행 - 1) << 3 | (ECU - 1)`이 되어 파종기 1의 1행 ECU 1·2는 `00`·`01`, 2행은 `08`·`09`이고, 파종기 2의 8행은 `38`·`39`다. Byte 8은 파종기 1이 `A0`, 파종기 2가 `A1`이다.

Byte 5 식에서 `<< 3`은 3비트 왼쪽으로 민다는 뜻이다. function instance(행 번호 - 1)가 Byte 5의 위쪽 5비트, ECU instance(ECU 번호 - 1)가 아래쪽 3비트에 들어가기 때문이다. 다음 코드는 32개 NAME을 실제로 만들어 상위 4바이트가 모두 다른지 확인한다.

::: details 파이썬으로 32개 NAME 검산
```python
FIELDS = [("aac", 1), ("ig", 3), ("dci", 4), ("dc", 7), ("rsvd", 1),
          ("func", 8), ("fi", 5), ("ei", 3), ("mfg", 11), ("ident", 21)]


def encode(**kw):
    v = 0
    for name, bits in FIELDS:
        assert 0 <= kw[name] < (1 << bits)
        v = (v << bits) | kw[name]
    return v


ROW_GUIDANCE = 0x80   # 예시 값: 원문에서 코드 미정(ff…f)
upper = set()
for planter in (0, 1):
    for row in range(8):
        for ecu in (0, 1):
            n = encode(aac=1, ig=2, dci=planter, dc=4, rsvd=0, func=ROW_GUIDANCE,
                       fi=row, ei=ecu, mfg=0, ident=0)
            upper.add(n >> 32)
assert len(upper) == 32          # identity number 없이도 32개가 모두 다르다

b = encode(aac=1, ig=2, dci=1, dc=4, rsvd=0, func=ROW_GUIDANCE,
           fi=7, ei=1, mfg=0, ident=0).to_bytes(8, "big")
print(f"파종기 2, 8행, ECU 2: Byte8={b[0]:02X} Byte7={b[1]:02X} Byte5={b[3]:02X}")  # A1 08 39
assert (encode(aac=0, ig=0, dci=0, dc=2, rsvd=0, func=129, fi=0, ei=0,
               mfg=0, ident=0) >> 32) == 0x00048100   # A.2의 상위 4바이트
```
:::

`encode()`는 필드 값을 앞(AAC)부터 차례로 이어 붙여 64비트 NAME을 만든다. `n >> 32`는 아래 32비트(manufacturer code와 identity number)를 버리고 상위 4바이트만 남긴다. 출력 `A1 08 39`는 위 문단의 "파종기 2의 8행 ECU 2"와 같고, 마지막 줄은 A.2 행의 `00 04 81 00`을 확인한다.

::: details 원문을 가진 독자를 위한 메모
- 필드 정의와 값 범위는 ISO 11783-5:2019 Table 1, 필드 사이 의존 관계는 Figure 2, 바이트 배치는 Figure 1이다.
- 의존 관계 표의 "Device class instance → Device class"는 Figure 2를 따른 것이다. Table 1의 설명 문구는 device class instance의 해석이 industry group에 따른다고 적는다.
- Function 254·255는 Table 1이 정의하지 않고, commanded function의 범위(0~254)는 4.4.3.3.4.5에 있다.
- 바이트 배치를 설명한 각주는 Table 1 각주 a~c이고, 조립 예는 Annex A.1~A.3이다.
:::

<small>근거: ISO 11783-5:2019 3.1, 4.3.1, 4.3.2, 4.4.3.1, 4.4.4.1, Table 1, Figure 1, Figure 2, Annex A</small>

::: tip 핵심 정리
- SA는 29비트 CAN ID의 하위 8비트에 있는 보낸 장치의 번호다. CAN ID를 16진수로 적으면 끝 두 자리다.
- SA 0~127·248~253은 preferred, 128~247은 self-configurable 범위이고, 254는 NULL(소스 전용), 255는 Global(목적지 전용)이다.
- preferred address도 우선권은 없다. 상대가 무슨 장치인지는 SA가 아니라 NAME으로 판단한다.
- NAME은 "주소를 옮길 수 있나(AAC)", "무슨 장치인가(industry group, device class, function)", "몇 번째인가(instance 3종)", "누가 만들었나(manufacturer code, identity number)"를 담은 64비트 신원이다. 값이 작을수록 주소 다툼에서 우선한다.
- Address Claimed의 데이터는 NAME을 Byte 1(identity number 최하위 바이트)부터 싣는다. 수신한 8바이트는 리틀 엔디언으로 정수화해 비교한다.
:::

::: details 확인 문제
1. (개념) 버스에서 CAN ID `0x18EEFF85`인 프레임을 받았다. 보낸 장치의 주소는 몇이고, 그 주소는 어느 범위에 속하는가?
2. (개념) SA 254와 255는 각각 언제 쓰는가? 둘 중 소스 주소 칸에 들어갈 수 있는 것은 무엇인가?
3. (개념) 같은 제조사의 같은 모델 두 대를 한 버스에 연결했다. 두 NAME을 다르게 만드는 필드는 무엇이고, 그 값을 펌웨어 상수로 박아 두면 어떤 문제가 생기는가?
4. (계산) NAME `0xA00882002803D090`을 비트 단위로 풀어 manufacturer code와 identity number를 구하라. 이 NAME을 Address Claimed의 데이터로 보낼 때 8바이트는 어떤 순서로 나가는가?

**답 가이드**
1. 끝 두 자리 `85`가 SA다. `0x85`는 133이고, 128~247 self-configurable 범위에 속한다.
2. 254(NULL)는 주소가 없는 CF가 보내는 Request for Address Claimed와 Cannot Claim Address의 SA로만 쓴다. 255(Global)는 목적지 주소로만 쓰며 "모두에게"를 뜻한다. 소스 주소 칸에 들어갈 수 있는 것은 254뿐이다.
3. identity number다. 상수로 박으면 두 대의 NAME이 완전히 같아진다. NAME 비교가 주소 중재의 유일한 기준이므로 두 CF 사이에서 승패를 가를 수 없다. 그래서 표준은 다른 필드가 같아질 수 있으면 identity number로 유일하게 만들라고 요구한다.
4. Byte 4는 `0x28` = `0010 1000`, Byte 3은 `0x03` = `0000 0011`이다. manufacturer code는 `0010 1000`에 Byte 3의 위쪽 3비트 `000`을 붙인 11비트로 0x28 × 8 + 0 = 320이다. identity number는 Byte 3의 아래쪽 5비트 `00011`에 Byte 2 `D0`, Byte 1 `90`을 붙인 `0x03D090` = 250000이다. 데이터 필드에는 Byte 1부터 `90 D0 03 28 00 82 08 A0` 순서로 나간다.
:::

## 다음 챕터

- 다음: [13장 주소 클레임: 주소를 정하는 절차](/study/isobus/13-j1939-address-claim)
