---
title: "ISO 11783 Part 1: 네트워크 요구사항과 공통 서비스"
description: "ISO 11783의 총론 문서(Part 1)가 네트워크 전체에 거는 요구사항을 계층별 규칙, 두 네트워크와 주소 범위, 전용 ECU 기능, 공통 서비스, 코드 등록 절차 순서로 정리한다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, OSI, TECU, 주소]
prev: /study/isobus/18-isobus-overview
next: /study/isobus/20-isobus-network-topology
---

# ISO 11783 Part 1: 네트워크 요구사항과 공통 서비스

::: info 학습 목표
- 표준 문장의 shall(반드시)과 should(권장)를 구분해 읽을 수 있다.
- ISO 11783의 각 파트가 OSI 7계층의 어느 층을 맡는지 설명할 수 있다.
- 트랙터 네트워크와 작업기 네트워크에 걸린 요구를 비교하고, 작업기 CF 주소가 128~237 안에 들어가는지 점검할 수 있다.
- VT, TECU, TC, FMIS 인터페이스와 공통 서비스가 각각 어느 파트에서 정해지는지 연결할 수 있다.
- 새 제조사 코드나 PGN이 필요할 때 isobus.net 요청부터 SAE J1939 등록까지의 경로를 설명할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [18장 ISOBUS 개요](/study/isobus/18-isobus-overview), [12장 주소와 NAME](/study/isobus/12-j1939-address-name), [15장 Transport Protocol 기초](/study/isobus/15-tp-bam-cmdt)
- 이 장에서 처음 나오는 말
  - shall / should: 표준 문장에서 "반드시 해야 한다"와 "그렇게 하기를 권한다"
  - OSI 7계층: 통신이 하는 일을 7개 층으로 나눠 본 참조 모형
  - 세그먼트: 양 끝을 종단 회로로 맺은 버스 한 토막
  - NIU: 세그먼트와 세그먼트를 잇는 장치
  - self-configurable address: 작업기 CF가 정해진 범위 안에서 스스로 골라 쓰는 주소
  - FMIS: 농장 사무실에서 쓰는 관리용 컴퓨터 시스템
:::

법은 총칙에서 모든 조문에 걸리는 원칙을 정하고, 세부는 각 조문에 맡긴다. ISO 11783에서 총칙 역할을 하는 문서가 Part 1이다. Part 1은 "CAN FD는 쓰지 않는다", "작업기 CF는 주소 128~237 안에서 쓴다"처럼 시리즈 전체에 걸리는 요구를 정하고, 세부는 각 파트에 넘긴다. 이 장은 그 요구를 계층 순서로 훑고, 표준 코드(PGN, 제조사 코드)를 새로 받는 절차까지 본다.

## 1. 표준 문장 읽는 법: shall과 should

이 절은 이 장의 표를 읽기 위한 준비다. 표준은 같은 "하라"도 얼마나 강하게 요구하는지 조동사로 구분한다. 이 구분을 모르면 권장 사항을 의무로, 의무를 권장으로 잘못 읽는다.

| 표준의 표현 | 뜻 | 이 장의 예 |
|---|---|---|
| shall / shall not | 반드시 해야 한다 / 해서는 안 된다. 어기면 표준 위반이다 | CAN FD 프레임 형식을 쓰면 안 된다 |
| should / it is recommended | 그렇게 하기를 권한다. 따르지 않아도 표준 위반은 아니다 | 트랙터 네트워크의 물리 계층은 Part 2를 따르기를 권장한다 |
| may / can | 해도 된다 / 할 수 있다 | 작업기 네트워크는 농장 관리 컴퓨터로 가는 게이트웨이를 둘 수 있다 |
| it is intended | 그렇게 되도록 의도한다. 요구라기보다 설계 의도를 밝히는 표현이다 | 트랙터 제조사 동의 없이 트랙터 네트워크에 CF를 연결하지 않는 것을 의도한다 |

구현자가 반드시 챙길 것은 shall이다. 이 장의 표와 목록은 원문의 요구 수준을 괄호 안에 (shall), (recommended)처럼 그대로 붙여 둔다.

## 2. OSI 7계층과 ISO 11783

이 절은 ISO 11783의 각 파트가 통신의 어느 층을 맡는지 본다. 결론부터 말하면 ISO 11783은 OSI 7계층 가운데 필요한 층만 정의한다. 5계층과 6계층은 따로 맡은 파트가 없고, 큰 메시지를 나누는 일(4계층의 일)은 데이터 링크 문서에 들어가 있다.

OSI 7계층은 ISO/IEC 7498-1이 정한 통신 참조 모형이다([8장](/study/isobus/08-j1939-intro)). 아래층은 전선 위로 비트를 실어 나르고, 위층으로 갈수록 사람이 쓰는 기능에 가까워진다. Part 1은 이 모형을 참조 틀로 쓰면서 두 가지를 분명히 한다.

- OSI 모델을 바탕으로 한 표준이라도 7계층으로 명시적으로 나눌 필요는 없다. 근본 기능이 지원되면 된다.
- ISO 11783은 특정 산업의 특정 응용을 위한 통신 시스템이라 <strong>필요한 계층만</strong> 정의한다. 계층마다 별도 파트가 있고, 다른 파트들이 그 계층들의 기능을 받쳐 준다.

Part 1의 계층 설명과 파트 배정을 맞대면 다음과 같다.

![OSI 7계층과 ISO 11783 파트의 대응: 7계층은 Part 6~14의 응용 메시지, 6계층과 5계층은 배정 없음, 4계층의 일인 TP·ETP는 실제로는 데이터 링크 문서인 Part 3에 규정, 3계층은 Part 4(NIU), 2계층은 Part 3, 1계층은 Part 2](/images/study-isobus/19-osi-part-map-light.png)
![OSI 7계층과 ISO 11783 파트의 대응: 7계층은 Part 6~14의 응용 메시지, 6계층과 5계층은 배정 없음, 4계층의 일인 TP·ETP는 실제로는 데이터 링크 문서인 Part 3에 규정, 3계층은 Part 4(NIU), 2계층은 Part 3, 1계층은 Part 2](/images/study-isobus/19-osi-part-map-dark.png)

| OSI 계층 | 계층의 역할 | ISO 11783에서 |
|---|---|---|
| 7 Application(응용) | 사용자에게 OSI 환경 접근과 분산 정보 서비스를 제공 | 각 응용 파트(Part 6~14)의 메시지 |
| 6 Presentation(표현) | 데이터 표현(문법) 차이로부터 응용을 독립시킴 | Part 1이 따로 배정하지 않음 |
| 5 Session(세션) | 협력하는 응용 사이의 세션 수립·관리·종료 | Part 1이 따로 배정하지 않음 |
| 4 Transport(전송) | 종단 간 신뢰 전송·오류 복구·흐름 제어, 큰 메시지 분할·재조립 | TP·ETP |
| 3 Network(네트워크) | 연결 기술로부터 상위 계층을 독립시키고 연결을 수립·유지·종료 | Part 4 (NIU) |
| 2 Data link(데이터 링크) | 물리 계층 위의 신뢰성 있는 블록 전송(동기·오류·순서·흐름 제어) | Part 3 |
| 1 Physical(물리) | 물리 매체 위의 비트 스트림 전송 | Part 2 |

표를 읽는 데 필요한 말을 풀어 둔다. 종단 간은 보낸 쪽 끝에서 받는 쪽 끝까지라는 뜻이고, 흐름 제어는 받는 쪽이 감당할 만큼만 보내도록 속도를 맞추는 일이다. Part 5(네트워크 관리)처럼 한 층에 놓이지 않고 여러 층을 받쳐 주는 파트도 있다. Part 1이 말한 "다른 파트들이 그 계층들의 기능을 받쳐 준다"가 이런 경우다(해석).

TP·ETP가 하는 일(큰 메시지의 분할·재조립)은 OSI로 보면 4계층의 일이지만, ISO 11783은 이를 데이터 링크 계층 문서에 둔다. 데이터 링크 계층 문서인 Part 3도 TP와 ETP 기능을 "데이터 링크 계층의 일부로" 기술한다고 밝힌다. [18장](/study/isobus/18-isobus-overview)의 계층 그림이 TP·ETP를 데이터 링크 층에 넣은 것과 이 표의 4계층 행이 어긋나 보이는 이유다.

ETP를 어느 파트가 정하는지는 문서의 판(edition)에 따라 서술이 다르다. Part 1의 2017년 판은 1786바이트 이상을 보내는 두 번째 전송 프로토콜(ETP)을 Part 6이 정한다고 적었다. 그런데 이 스터디가 근거로 쓴 Part 3의 2018년 판은 ETP를 직접 정의하고, Part 6의 2018년 판도 ETP를 Part 3에 규정된 것으로 가리킨다. 판이 바뀌면서 ETP 규정이 Part 3로 옮겨진 것으로 보인다(추론). 이 스터디는 [17장](/study/isobus/17-etp)처럼 ETP를 Part 3 기준으로 다룬다.

::: details 원문을 가진 독자를 위한 메모
- 위 표의 근거: 7계층 행은 Part 1 6.3 끝 문단과 6.7~6.14, 6계층과 5계층 행은 Clause 5, 4계층 행은 6.3, 3계층 행은 6.4, 2계층 행은 6.3, 1계층 행은 6.2다.
- ETP 소관 차이: Part 1 6.3은 Part 3가 1785바이트까지의 TP를, <strong>Part 6</strong>이 1786바이트~117 MB의 두 번째 전송 프로토콜을 규정한다고 적는다. 그런데 이 스터디가 근거로 쓴 ISO 11783-3:2018(FDIS)은 5.11에서 ETP를 직접 정의하고, ISO 11783-6:2018도 오브젝트 풀 전송(Annex C)에서 "ISO 11783-3에 규정된 extended transport protocol"을 참조한다.
- TP와 ETP를 데이터 링크 계층의 일부로 기술한다는 문장은 Part 3:2018 5.10.1(TP)과 5.11.1(ETP)에 있다.
:::

<small>근거: ISO 11783-1 Clause 5, 6.2~6.4, ISO 11783-3 5.10.1, 5.11.1, ISO 11783-6 C.2.1</small>

## 3. 계층별 요구사항

이 절은 Part 1이 계층마다 거는 요구를 짧게 본다. 각 계층의 자세한 내용은 해당 파트를 다루는 장에서 보므로, 여기서는 무엇이 반드시(shall)인지에 집중한다.

### 브로드캐스트가 기본이다

ISO 11783 네트워크(트랙터 네트워크와 작업기 네트워크)에서는 많은 메시지가 브로드캐스트된다. 트랙터 네트워크는 트랙터 안쪽 장치들의 버스이고, 작업기 네트워크는 작업기와 VT, TC가 붙는 버스다(4절). [20장](/study/isobus/20-isobus-network-topology)에서는 같은 것을 트랙터 버스, 작업기 버스라고 부른다.

브로드캐스트는 데이터를 특정 목적지로 보내지 않고 버스에 흘리는 방식이다. 교실 칠판에 적어 두면 누구나 읽을 수 있는 것과 같다. 그래서 어떤 CF든 추가 요청 메시지 없이 그 데이터를 쓸 수 있다. 특정 CF에게 보낼 때만 CAN ID 안에 목적지 주소를 넣는다. 이 때문에 메시지 형식은 global 목적지 형식(모두에게)과 destination-specific 형식(특정 CF에게) 두 가지이고, 제조사 고유(proprietary) 통신도 두 형식 중 하나로 허용된다.

구현 관점에서는 "필요한 데이터는 대개 이미 버스에 흐르고 있다"는 뜻이다. [18장](/study/isobus/18-isobus-overview) 사례 1의 지면 속도(PGN 65097)처럼 주기적으로 브로드캐스트되는 값은 요청 없이 수신 필터만 걸어 읽는다(해석).

### 물리 계층 요약

Part 2 원문은 이 스터디의 근거 자료에 없으므로, 물리 계층 내용은 Part 1의 요약에 있는 것만 옮긴다. ISO 11898은 CAN을 정한 국제 표준이다([3장](/study/isobus/03-can-physical)).

- ECU 인터페이스는 ISO 11898-1:2015의 물리 시그널링 서브계층과 ISO 11898-2:2016의 물리 매체 접근 서브계층을 따라야 한다(shall).
- 네트워크는 각 ECU에 노드로 연결되는 <strong>선형 quad-twisted 케이블 하나</strong>로 이뤄진다. 선형은 가지 없이 한 줄로 이어진 모양이고, quad-twisted는 네 가닥을 함께 꼰 케이블이다. 각 ECU는 짧은 리드 케이블로 이 케이블에 이어지고, 그 연결이 노드다.
- 네트워크 세그먼트의 양 끝에는 능동 TBC를 둔다. TBC(Terminating Bias Circuit)는 버스 끝을 맺는 종단 회로다([20장](/study/isobus/20-isobus-network-topology)).
- Part 2는 커넥터 세 가지(작업기를 트랙터에 연결, 장비에 설치된 네트워크에 ECU 추가, 서비스 툴 연결)와 네트워크 동작에 필요한 전원과 그 연결도 규정한다.

### 데이터 링크 계층 요약

- ISO 11783 ECU는 ISO 11898-1:2015의 <strong>CAN Classical Extended Frame Format</strong>을 써야 하고, <strong>CAN FD 프레임 형식은 쓰면 안 된다</strong>(shall not). Classical Extended Frame Format은 29비트 ID를 쓰는 고전 CAN 프레임이다([4장](/study/isobus/04-can-data-frame)). Part 3의 2018년 판도 머리말에서 이번 판의 첫 변경 사항으로 CAN FD 사용 배제를 적는다. [7장](/study/isobus/07-can-fd)의 CAN FD는 ISOBUS 버스에 올릴 수 없다는 뜻이다.
- Part 3는 8비트 PF, 8비트 PS, 2비트 data page 필드로 PDU를 식별한다. 셋 다 29비트 ID 안의 칸이다([9장](/study/isobus/09-j1939-message)). 메시지 오버헤드(데이터 말고 덧붙는 ID 같은 비트)를 줄이려고 연관된 데이터 항목 여러 개를 한 PDU에 묶는다.
- 제조사 고유 메시지가 따로 정의되어 있다.
- 8바이트를 넘는 데이터는 multi-packet 메시지로 보낸다. TP는 1785바이트까지, ETP는 1786바이트부터 117 MB까지다(2절의 ETP 소관 차이 참고).
- 응용 메시지별 송신 주기, 데이터 프레임 길이, data page, PF, PS 또는 DA, 기본 우선순위는 그 응용을 규정하는 파트가 정한다. DA(Destination Address)는 받는 쪽 주소다.

### 네트워크 계층 요약

- 네트워크 구조가 다른 두 네트워크를 연결할 때, 연결 시스템의 통합자는 NIU(network interconnect unit)로 각 세그먼트를 서로 격리해야 한다(shall). 통합자는 여러 장비를 묶어 하나의 시스템으로 꾸미는 쪽이다. NIU의 상세는 Part 4이고, [21장](/study/isobus/21-niu-network-layer)에서 다룬다.
- 복잡한 시스템은 Part 2가 정한 세그먼트당 <strong>30노드</strong> 전기적 한계를 넘을 수 있다. 그런 경우 작업기 시스템 제조사가 NIU로 세그먼트를 나눠 전기적 부하 한계를 지켜야 한다(shall).

### 네트워크 관리 요약

[12장](/study/isobus/12-j1939-address-name)과 [13장](/study/isobus/13-j1939-address-claim)에서 본 주소와 NAME 규칙을 Part 1은 이렇게 요약한다. SA(Source Address)는 CF가 쓰는 1바이트 주소이고, NAME은 CF마다 붙는 64비트 신분증이다.

- 통신하는 모든 CF는 SA가 필요하고, ECU 하나가 CF 여럿을 수행하면 CF마다 주소가 필요하다.
- CF를 유일하게 식별하려고 Part 5가 64비트 NAME을 규정하고, SA 결정과 주소 충돌 해소 절차도 Part 5가 정한다. SA는 미리 정해지거나(preset) 전원을 켤 때 컨트롤러마다 동적으로 클레임한다.
- 통신하는 모든 CF에 NAME을 배정해야 한다(shall). ECU 하나에 NAME·주소가 여럿 공존할 수 있다.
- isobus.net 데이터베이스가 NAME 필드용 코드를 관리한다. 네트워크 관리 규격을 쓰는 산업, 비특정 CF용 preset·preferred address, 농림업 장비용 initial address 할당, CF가 쓸 NAME, ECU 제조사 목록이다.

<small>근거: ISO 11783-1 6.1~6.5, ISO 11783-3 Foreword</small>

## 4. 트랙터 네트워크와 작업기 네트워크

이 절은 ISOBUS의 기본 구성인 두 네트워크에 Part 1이 거는 요구를 비교하고, 작업기 주소를 정할 때 쓰는 권장 구성을 본다.

ISO 11783은 세그먼트를 둘 이상 지원하고, 기본은 트랙터 네트워크와 작업기 네트워크다. 트랙터 네트워크는 엔진, 변속기처럼 트랙터를 움직이는 장치들의 버스이고, 작업기 네트워크는 작업기와 VT, TC가 붙는 버스다. 둘을 잇는 데 <strong>TECU가 필요</strong>하다. TECU(Tractor ECU)는 트랙터 쪽 정보를 작업기 네트워크에 알려 주고 두 네트워크 사이를 지키는 장치다. 두 버스의 물리 구조는 [20장](/study/isobus/20-isobus-network-topology)에서 보고, 여기서는 Part 1이 두 세그먼트에 거는 요구 수준(shall/should)을 나란히 놓는다.

| 항목 | 트랙터 네트워크 | 작업기 네트워크 |
|---|---|---|
| 역할 | 트랙터의 구동계·섀시 CF 사이의 제어·데이터 통신 | 작업기 사이, 그리고 트랙터와 작업기 사이의 통신을 지원하도록 설계해야 한다(shall) |
| 통제 | 트랙터 제조사가 통제한다 | - |
| ISO 11783 요구 적용 | - | 해당 요구사항을 만족해야 한다(shall) |
| 물리 계층 | Part 2 준수를 권장(recommended) | 커넥터는 Part 2를 따라야 한다(shall) |
| CF 추가 접속 | 트랙터 제조사의 동의 없이는 CF를 연결하지 않는 것을 의도한다(intended) | - |
| 응용 메시지 | Part 8(구동계)·Part 7 메시지와 Part 3의 proprietary 메시지를 쓸 수 있다 | Part 7이 정의한다. 작업기 네트워크의 CF 주소도 Part 8 메시지를 쓸 수 있다 |
| 위치 | 두 네트워크 모두 트랙터에 통합될 수 있다 | 트랙터 위와 작업기 위 양쪽에 존재한다 |

표의 "-"는 Part 1이 그 항목을 따로 정하지 않았다는 뜻이다. 구동계는 엔진의 힘을 바퀴까지 전하는 장치들이고, 섀시는 차체의 뼈대와 그에 붙은 장치들이다.

표에서 눈여겨볼 점은 요구의 세기다. 작업기 네트워크 쪽에는 shall이 많고, 트랙터 네트워크 쪽에는 권장과 의도뿐이다. 작업기 네트워크는 여러 회사 장비가 만나는 곳이고, 트랙터 네트워크는 트랙터 제조사가 자기 장비 안에서 관리하는 곳이기 때문으로 읽을 수 있다(해석).

### 권장 구성: 작업기 주소 계획

<strong>권장 구성</strong>은 주소 계획에 바로 쓰인다. 이름은 "권장"이지만 안에 shall 요구가 섞여 있으니 문장마다 요구 수준을 확인한다.

- 트랙터 네트워크의 CF는 isobus.net 데이터베이스의 preferred address를 쓰는 것이 권장된다. preferred address는 기능별로 미리 정해 둔 권장 주소다.
- 연결된 작업기에서 쓰는 CF 수는 self-configurable address로 <strong>128~237의 110개 주소</strong> 안으로 제한해야 한다(shall). 작업기 여러 대를 연결할 때는 현실적 한계가 있다는 점도 Part 1이 함께 적는다.
- 작업기 주소는 Part 5의 절차로 배정해야 한다(shall).
- 작업기는 추가 작업기를 직렬로 이어 붙일 수 있도록 네트워크 연장 연결을 제공해야 한다(shall).
- ECU가 여러 개인 작업기는 network interconnection ECU로 추가 ECU를 작업기 네트워크에서 격리할 수 있다.

128~237은 양 끝을 포함하므로 237 − 128 + 1 = 110개다. 예를 들어 CF가 3개인 작업기 두 대를 이으면 주소 6개가 필요하고, 110개 안에 넉넉히 들어간다. 주소를 고르고 겹칠 때 양보하는 절차는 [13장](/study/isobus/13-j1939-address-claim)에서 봤다.

Part 1은 이 구성을 CF 주소와 함께 보여 주는 예시 그림을 싣고 있다. 아래는 그 구조를 다시 그린 것이다.

![트랙터 네트워크와 작업기 네트워크의 예시 토폴로지: 트랙터 네트워크의 CF 주소 35, 7, 30, 31, 3, 0, 두 네트워크를 잇는 TECU(ECU 7, 주소 240), 작업기 네트워크에서 VT 38과 관리 게이트웨이 37이 함께 든 ECU 6, TC 247, 작업기 1·2의 self-configurable 주소 a1~a4](/images/study-isobus/12-network-topology-light.png)
![트랙터 네트워크와 작업기 네트워크의 예시 토폴로지: 트랙터 네트워크의 CF 주소 35, 7, 30, 31, 3, 0, 두 네트워크를 잇는 TECU(ECU 7, 주소 240), 작업기 네트워크에서 VT 38과 관리 게이트웨이 37이 함께 든 ECU 6, TC 247, 작업기 1·2의 self-configurable 주소 a1~a4](/images/study-isobus/12-network-topology-dark.png)

그림에서 세 가지를 본다.

1. <strong>ECU와 CF는 다른 단위다.</strong> ECU 6 하나에 VT(38)와 관리 컴퓨터 게이트웨이(37) 두 CF가 들어 있고, 각자 주소를 가진다. ECU 6은 트랙터에 실려 있지만 작업기 네트워크에 붙는다.
2. <strong>TECU 위의 7은 ECU 번호이고 240이 주소다.</strong> 원래 그림은 노드 옆의 작은 숫자로 그 CF를 담은 ECU의 번호를, 반대편 숫자로 CF의 주소를 적는다. TECU는 두 노드 사이 위쪽에 ECU 번호를 적는다. 다시 그린 그림은 이를 "ECU 7 / 주소 240"처럼 풀어 적었다. 트랙터 쪽 CF의 "주소 7"과 TECU의 "ECU 7"을 헷갈리지 않아야 한다.
3. <strong>작업기 CF의 주소 a1~a4는 self-configurable 주소다.</strong> 앞의 권장 구성대로 128~237 안에서 Part 5 절차로 정해진다. TC(247)와 TECU(240)는 그 밖인 238~247에 있다.

::: details 원문을 가진 독자를 위한 메모
- 예시 토폴로지의 원본은 Part 1 Figure 3이다. 2번의 숫자 읽는 법은 그 그림의 NOTE 2, 3번의 a1~a4 설명은 NOTE 1이다.
- 두 네트워크 비교표의 열은 각각 6.6.2(트랙터 네트워크)와 6.6.3(작업기 네트워크), 권장 구성은 6.6.4, TECU가 필요하다는 문장은 6.6.1이다.
:::

<small>근거: ISO 11783-1 6.6.1~6.6.4, Figure 3</small>

## 5. 전용 ECU 기능: VT, TECU, TC, FMIS 인터페이스

이 절은 Part 1이 따로 이름을 붙여 정의하는 ECU 기능 네 가지를 본다. 기능별 상세는 해당 파트와 챕터로 넘기고, 여기서는 Part 1이 그 기능에 거는 요구만 정리한다.

| 기능 | Part 1의 규정 | 상세 |
|---|---|---|
| VT | 표준 메시지로 작업기나 트랙터의 운전자 인터페이스를 제공한다. 요구사항은 Part 6. VT는 작업기 네트워크에 붙는다. TECU나, 작업기 네트워크에 연결된 트랙터 안의 다른 ECU도 작업기 Working Set과 <strong>같은 방법으로</strong> VT를 쓸 수 있다 | [29장](/study/isobus/29-vt-basics) |
| TECU | 트랙터 네트워크와 작업기 네트워크 사이에는 전기적 격리와 메시지 격리를 모두 보장하는 NIU를 둬야 한다(shall). TECU는 작업기 CF가 보낸 Part 7 메시지 요청을 받아 해석하고 트랙터 네트워크의 ECU들과 통신한다. 요청·명령한 ECU에 적절한 ACK나 응답을 줘야 하고(shall), Part 9에 따라 기본 정보를 제공하고 명령 메시지대로 동작해야 한다(shall) | [22장](/study/isobus/22-tractor-ecu) |
| TC | ISO 11783 네트워크를 통해 작업기 기능을 스케줄 기반으로 제어한다. 동작과 메시지 형식은 Part 10, 데이터 요소 정의는 Part 11의 data dictionary | [41장](/study/isobus/41-tc-basics) |
| FMIS 인터페이스 | 작업기 네트워크는 농장 관리 컴퓨터로의 게이트웨이를 포함할 수 있다. FMIS 쪽 게이트웨이의 물리 인터페이스는 ISO 11783이 규정하지 않는다. FMIS의 파일에서 나온 데이터를 FMIS 인터페이스에 제공할 때는 Part 10에 정의된 메시지를 써야 한다(shall) | [56장](/study/isobus/56-practice-isoxml) |

Working Set은 작업기 하나의 일을 나눠 맡는 CF 묶음이다([18장](/study/isobus/18-isobus-overview)). ACK는 "받았다, 처리한다"는 확인 응답이다([10장](/study/isobus/10-j1939-request-ack)).

VT 행의 "같은 방법으로"는 트랙터 쪽 기능도 VT 앞에서는 작업기 Working Set과 똑같은 클라이언트(서비스를 받아 쓰는 쪽)라는 뜻이다. VT Server를 에뮬레이션(소프트웨어로 흉내 내어 만드는 것)할 때 트랙터 쪽 클라이언트를 위한 별도 경로가 필요 없다는 근거가 된다(해석).

TC를 중심으로 작업 데이터가 도는 흐름도 Part 1이 단계별로 적는다.

![TC 중심 작업 데이터 흐름: FMIS의 작업 데이터가 FMIS 인터페이스를 거쳐 TC에 저장되고, TC가 작업기 CF에 제어 메시지를 보내며, CF의 측정값을 기록해 같은 경로로 FMIS에 돌려준다. FMIS와 게이트웨이 사이의 물리 규격은 표준 밖이다](/images/study-isobus/12-tc-fmis-flow-light.png)
![TC 중심 작업 데이터 흐름: FMIS의 작업 데이터가 FMIS 인터페이스를 거쳐 TC에 저장되고, TC가 작업기 CF에 제어 메시지를 보내며, CF의 측정값을 기록해 같은 경로로 FMIS에 돌려준다. FMIS와 게이트웨이 사이의 물리 규격은 표준 밖이다](/images/study-isobus/12-tc-fmis-flow-dark.png)

1. FMIS 인터페이스가 받은 작업(task) 데이터를 TC에 저장한다.
2. TC가 작업을 스케줄링하고, 실행할 CF에게 작업기 네트워크로 제어 메시지를 보낸다.
3. 작업이 진행되는 동안 CF들로부터 받은 데이터를 TC가 기록한다.
4. 기록한 데이터를 작업기 네트워크의 FMIS 인터페이스를 거쳐 FMIS로 보낸다.

사무실에서 짠 작업 계획이 트랙터로 내려가고, 밭에서 쌓인 기록이 사무실로 돌아오는 왕복 흐름이다. 그림의 점선 구간(FMIS와 게이트웨이 사이)은 USB 메모리든 무선이든 표준이 정하지 않는다는 뜻이다.

<small>근거: ISO 11783-1 6.7.1~6.7.4</small>

## 6. 공통 서비스

이 절은 특정 ECU 하나가 아니라 네트워크 위의 여러 CF가 함께 쓰는 서비스들을 본다. Part 1은 서비스마다 어느 파트가 정하는지만 밝히고 세부는 그 파트에 맡긴다.

| 서비스 | Part 1의 규정 요지 | 상세 |
|---|---|---|
| 진단 | 네트워크 오동작의 원인이 되는 고장을 찾는 데 쓸 메시지를 Part 12가 규정한다. 같은 메시지가 참조되는 다른 진단 표준에도 있다 | [27장](/study/isobus/27-diagnostics-identification) |
| File server | 데이터 파일 저장소를 제공하는 CF와, 네트워크의 CF가 그 파일을 읽고 쓰는 데 쓸 명령 집합을 Part 13이 규정한다 | [51장](/study/isobus/51-file-server-basics) |
| Sequence control | 트랙터나 다른 CF의 운전자 조작 기능 시퀀스를 여러 개 기록해 두었다가 운전자 명령으로 재생하는 메시지를 Part 14가 규정한다. 두렁 선회 관리(headland management) 같은 제어 시스템을 만든다 | [53장](/study/isobus/53-sequence-control-basics) |
| Process data | TC에서 CF 하나 이상으로 데이터를 보내는 메시지. 작업기 네트워크의 다른 CF로 보낼 때도 쓸 수 있다. 메시지 구조는 Part 10, 데이터 정의는 isobus.net의 data dictionary | [45장](/study/isobus/45-tc-process-data-basics) |
| Working set | CF 집합을 특정 애플리케이션에 연관된 것으로 네트워크에 알리는 장치. 정의·운영 규칙·수립 메시지는 Part 6과 Part 7 | [26장](/study/isobus/26-isobus-network-mgmt) |
| Safe mode | 아래 경고 상자. 추가 safe mode 요구사항은 Part 9가 규정한다 | [22장](/study/isobus/22-tractor-ecu) |
| 파라미터·메시지 추가 | 트랙터-작업기 메시지는 Part 7, 트랙터 구동계 메시지는 Part 8이 규정한다. 특정 응용용으로 개발한 메시지 집합을 ISO 11783에 추가할 수 있고, 새 코드의 추가·갱신 요청은 데이터베이스에 게시된 code request form으로 유지관리 기관(MA)에 낸다 | 7절 |

두렁 선회 관리는 밭 끝에서 방향을 돌 때마다 반복하는 조작(히치 올리기, 살포 끄기 같은 것)을 기록해 두었다가 버튼 하나로 다시 실행하는 기능이다. safe mode는 고장이 나도 사람이 다치지 않는 상태로 동작하게 하는 방식이다.

::: warning 안전 책임은 제조사에 있다
Part 1은 VT·보조 조작기·TC로 보내는 정보와 제어가 이 표준을 따르더라도, <strong>그곳에 요청하는 제어가 적용 가능한 안전 표준에 맞게 설계·제작되었음을 제조사가 보장해야 한다</strong>(shall)고 적는다. 컨트롤러가 제공하는 기능은 의도한 효과가 나되 상해 위험으로 이어지지 않게 설계해야 한다(shall). 통신 규격을 지켰다는 사실이 기능 안전을 보증하지 않는다는 뜻이다. 예를 들어 VT 버튼으로 작업기 유압이 움직이는 구조라면, 버튼 이벤트가 늦거나 빠지거나 중복될 때의 동작까지 제조사가 설계 책임을 진다(예시).
:::

<small>근거: ISO 11783-1 6.8~6.14</small>

## 7. 전자 데이터베이스와 코드 요청

이 절은 PGN, 주소, NAME 코드 같은 번호들의 원본 목록이 어디에 있고, 새 번호를 어떻게 받는지 본다. 결론부터 말하면 원본은 표준 문서가 아니라 isobus.net의 온라인 데이터베이스다.

### 데이터베이스에 무엇이 있나

전화번호부처럼, 누가 어느 번호를 쓰는지 한곳에 모아 둔 공식 명부가 있다. Part 1의 2017년 판(2판)에서 가장 크게 바뀐 점은 2007년 판(1판)의 부록에 실려 있던 식별자(파라미터) 목록을 모두 전자 데이터베이스로 옮긴 것이다. 이제 PG·주소·identity(NAME 코드처럼 장치와 기능을 식별하는 값) 할당은 데이터베이스가 관리하고, SAE에 공식 등록되어 SAE J1939 권고 실무(recommended practice)의 일부가 된다. 데이터베이스는 isobus.net에서 접근하며 다음 일곱 목록을 제공한다. 모두 SAE J1939에 공식 등록된 현행 목록이다.

| 목록 | 구현에서 쓰는 곳 |
|---|---|
| Parameter group assignments | PGN 정의 |
| Industry groups | NAME의 industry group |
| Industry group 0 preferred addresses | 전 산업 공통 preferred address |
| Industry group 2 initial addresses | 농림업 장비의 initial address |
| NAMEs | NAME의 device class·function 코드 |
| All industry NAMEs | 전 산업 공통 NAME |
| Manufacturer codes | NAME의 manufacturer code |

표의 industry group, device class, function, manufacturer code는 NAME 안의 칸 이름이다. 각각 산업 분야, 장치 종류, 기능, 제조사를 나타내는 번호다([12장](/study/isobus/12-j1939-address-name)). industry group 2가 농림업 장비다.

Part 1은 적용 범위를 밝히는 부분에서, 이 데이터베이스가 응용 개발자에게 주소 할당·identity 할당·파라미터 정의의 현행 목록을 제공한다고 적는다. NAME을 정하는 Part 5도 NAME 필드 표에서 industry group·device class·function·manufacturer code의 수치를 직접 싣지 않고 Part 1로 미룬다. NAME을 조립하거나 PGN을 해석하는 코드의 상수표는 문서가 아니라 이 데이터베이스가 원본이라는 뜻이다. [12장](/study/isobus/12-j1939-address-name)의 예시 NAME이 등록값 대신 예시 값을 쓴 이유이기도 하다.

### 새 코드를 요청하는 흐름

![ISO 11783 코드 요청과 등록 흐름: 제조사가 isobus.net의 요청 양식을 내면 ISO/TMB가 지정한 유지관리 기관(VDMA, DIN 대행)이 처리하고, SAE J1939 위원회와 코드 등록을 동기화한 뒤 전자 데이터베이스의 일곱 목록에 게시한다](/images/study-isobus/12-code-request-flow-light.png)
![ISO 11783 코드 요청과 등록 흐름: 제조사가 isobus.net의 요청 양식을 내면 ISO/TMB가 지정한 유지관리 기관(VDMA, DIN 대행)이 처리하고, SAE J1939 위원회와 코드 등록을 동기화한 뒤 전자 데이터베이스의 일곱 목록에 게시한다](/images/study-isobus/12-code-request-flow-dark.png)

1. 새 PG·주소·identity 할당을 받거나 기존 할당의 설명을 고치려면 isobus.net 데이터베이스에 있는 요청 양식(request form)을 쓴다.
2. 요청은 ISO 기술관리이사회(ISO/TMB)가 지정한 유지관리 기관(MA)이 처리한다. MA의 사무국은 DIN(독일 표준화 기구)을 대신해 VDMA(독일기계공업협회)가 맡는다.
3. MA는 코드 등록을 SAE J1939 위원회와 동기화한다.
4. 특정 응용용으로 개발한 메시지 집합도 같은 경로로 ISO 11783에 추가할 수 있다.

예를 들어 자체 ECU를 시장에 내놓으려는 제조사는 manufacturer code부터 필요하다. Part 5에 따르면 NAME의 manufacturer code(11비트)는 위원회가 할당하는 값이고, 그 목록이 이 데이터베이스의 Manufacturer codes다. 임의 값을 넣은 NAME은 다른 제조사의 코드와 겹칠 수 있다.

<small>근거: ISO 11783-1 Foreword, Scope, Clause 7, 6.14, Annex A, ISO 11783-5 Table 1</small>

## 8. 표준 문서의 판

이 절은 이 스터디가 어느 판의 표준을 근거로 썼는지 밝힌다. 표준 문서도 소프트웨어처럼 개정되어 판(edition)이 바뀌고, ISO 11783의 파트는 저마다 따로 개정된다. 같은 개념이라도 판에 따라 위치나 규정이 다를 수 있다. 2절의 ETP 소관 차이가 한 예다.

처음 읽는 독자는 두 가지만 기억하면 된다. 하나, 이 스터디의 내용은 파트마다 특정 판을 기준으로 한다. 둘, 실제 장비끼리 맞물리는지는 판 번호보다 각 기능의 버전(VT 버전, TECU 버전 같은 functionality characteristic, [18장](/study/isobus/18-isobus-overview))으로 확인한다. 판 목록은 원문과 대조하려는 독자에게만 필요하므로 아래 메모에 접어 둔다.

::: details 원문을 가진 독자를 위한 메모
ISO 11783의 파트는 저마다 따로 개정된다. 같은 개념이라도 판에 따라 위치나 규정이 다를 수 있으므로(2절의 ETP 소관 차이가 한 예), 이 스터디가 근거로 쓴 판을 밝혀 둔다. 마지막 열은 각 판의 Foreword가 직접 밝힌 변경만 옮겼다.

| 파트 | 제목 | 근거로 쓴 판 | 발행 | 대체한 판 | Foreword의 주요 변경 |
|---|---|---|---|---|---|
| 1 | General standard for mobile data communication | 2판 | 2017-12 | 1판(2007) | 1판 Annex A~G의 식별자를 전자 데이터베이스로 이관 |
| 2 | Physical layer | - | - | - | 근거 자료에 없음. 물리 계층은 Part 1 6.2 요약만 사용 |
| 3 | Data link layer | 4판 FDIS | 2018 (투표 2018-08-09~2018-10-04) | 3판(2014) | CAN FD 사용 배제, BAM.TP를 10 ms로 송신 허용, Request2가 확장 식별자를 쓰면 Acknowledgement PG도 지원 |
| 4 | Network layer | 2판 | 2011-12-01 | 1판(2001) | 기술적 개정(항목 미기재) |
| 5 | Network management | 3판 | 2019-06 | 2판(2011) | 물리 요구사항을 Part 2로 이동 |
| 6 | Virtual terminal | 4판 | 2018-06 | 3판(2014) | VT version 6. Select Active Working Set 명령, Colour Palette·Graphic Data·Scaled Graphic·Working Set Special Controls 오브젝트 추가 |
| 7 | Implement messages application layer | 3판 + Amendment 1 | 2015-03-15, Amd 1 2018-06 | 2판(2009) | 기술적 개정(항목 미기재) |
| 8 | Power train messages | 1판 | 2006-02-01 | - | - |
| 9 | Tractor ECU | 2판 | 2012-02-01 | 1판(2002) | 기술적 개정(항목 미기재) |
| 10 | Task controller and management information system data interchange | 2판 | 2015-09-15 | 1판(2009) | 기술적 개정(항목 미기재) |
| 11 | Mobile data element dictionary | 2판 | 2011-07-01 | 1판(2007) | 소규모 개정(minor revision) |
| 12 | Diagnostics services | 3판 | 2019-01 | 2판(2014) | 모든 파라미터에 SPN 부여, CF functionality 파라미터를 온라인 데이터베이스로 이관, 참조 문서 갱신 |
| 13 | File server | 2판 | 2011-04-01 | 1판(2007) | 소규모 개정(minor revision) |
| 14 | Sequence control | 1판 | 2013-09-15 | - | - |

FDIS(Final Draft International Standard)는 발행 직전의 최종 초안이다. 표의 "-"는 해당 정보가 없다는 뜻이다.
:::

::: tip 핵심 정리
- Part 1은 ISO 11783 시리즈 전체의 총칙이다. shall은 반드시, should는 권장, intended는 설계 의도다.
- ISO 11783은 OSI 7계층 중 필요한 층만 정의한다. 큰 메시지를 나누는 TP·ETP는 하는 일로는 4계층이지만 데이터 링크 문서(Part 3)에 들어 있다.
- ISOBUS 버스에는 고전 CAN 확장 프레임만 쓰고 CAN FD는 쓰지 않는다. 세그먼트당 30노드를 넘으면 NIU로 나눈다.
- 트랙터 네트워크는 트랙터 제조사가 관리하고, 작업기 네트워크는 ISO 11783 요구를 반드시 만족해야 한다. 둘 사이는 TECU가 전기적·메시지 격리를 맡는다.
- 연결된 작업기의 CF는 128~237의 110개 주소 안에서 Part 5 절차로 주소를 정한다.
- PGN, 주소, NAME 코드의 원본은 isobus.net 데이터베이스이고, 새 코드는 요청 양식으로 유지관리 기관에 신청한다.
:::

::: details 확인 문제
1. (구분) "트랙터 네트워크의 물리 계층은 Part 2를 따르기를 권장한다"와 "작업기 네트워크의 커넥터는 Part 2를 따라야 한다"는 요구의 세기가 어떻게 다른가?
2. (판단) 어떤 ECU가 CAN FD 프레임으로 한 번에 64바이트를 보내는 방식으로 ISOBUS 작업기 네트워크에 붙으려 한다. 허용되는가?
3. (연결) 진단, 파일 서버, 시퀀스 제어, 프로세스 데이터 메시지 구조를 각각 정하는 파트는 무엇인가?
4. (설계형) CF가 각각 4개, 6개, 3개인 작업기 세 대를 한 트랙터에 직렬로 연결하려 한다. Part 1의 주소 범위 요구를 만족하는지 판단하고, 이 구성에 걸리는 shall 요구를 이 장의 어느 절에서 다뤘는지와 함께 나열하라.

**답 가이드**
1. 앞은 should(권장)라 따르지 않아도 표준 위반이 아니다. 뒤는 shall이라 반드시 지켜야 한다. 여러 회사 작업기가 꽂히는 작업기 네트워크 쪽 요구가 더 강하다.
2. 허용되지 않는다. Part 1은 ISO 11783 ECU가 고전 CAN 확장 프레임 형식을 써야 하고 CAN FD 프레임 형식은 쓰면 안 된다(shall not)고 정한다. 8바이트를 넘는 데이터는 TP나 ETP로 나눠 보낸다.
3. 진단은 Part 12, 파일 서버는 Part 13, 시퀀스 제어는 Part 14, 프로세스 데이터 메시지 구조는 Part 10이다. 프로세스 데이터의 데이터 정의는 isobus.net의 data dictionary에 있다.
4. CF 합계 13개는 128~237의 110개 안에 들어간다(shall, 4절의 권장 구성). 이 밖에 작업기 주소는 Part 5 절차로 배정해야 하고(4절의 권장 구성), 작업기는 추가 작업기를 직렬로 이을 연장 연결을 제공해야 하며(4절의 권장 구성), 작업기 네트워크의 커넥터는 Part 2를 따라야 하고(4절의 비교표), 세그먼트가 30노드 전기적 한계를 넘으면 NIU로 나눠야 한다(3절의 네트워크 계층 요약).
:::

## 다음 챕터

- 다음: [20장 ISOBUS 네트워크 구성: 버스, 커넥터, ECU](/study/isobus/20-isobus-network-topology)
