---
title: "표준 정리: Part 4 — Network layer"
description: "ISO 11783-4(Network layer) — NIU 유형, 메시지 포워딩·필터링, 네트워크 상호연결을 정리한 표준 요약이다."
date: 2026-08-21
tags: [ISOBUS, ISO11783, 표준정리]
---

# ISO 11783-4: Network layer 정리

::: info 이 문서에 대해
ISO 11783-4 표준 원문을 학습 목적으로 재구성한 <strong>비공식 요약·해설</strong>이다. 규범적 판단이 필요할 때는 반드시 원문 표준을 확인해야 한다.
:::

## 개요

ISO 11783-4:2011(2판)은 농업·임업용 트랙터와 작업기(implement)를 연결하는 ISO 11783 직렬 데이터 네트워크에서 <strong>네트워크 계층</strong>을 규정한다. 서로 다른 네트워크 세그먼트에 있는 CF(Control Function)끼리 통신할 수 있게 하는 요구사항과 서비스, 그리고 세그먼트를 연결하는 장치인 <strong>NIU(Network Interconnection Unit)</strong>의 종류를 정의한다. SAE J1939/31과 조화(harmonized)되어 있으며, 1판(2001)을 기술적으로 개정해 대체한 문서다.

문서 구조는 다음과 같다.

| 절 | 내용 |
| --- | --- |
| 1~3 | 적용 범위, 인용 규격, 용어 정의 |
| 4 | NIU와 네트워크 계층의 역할 개요 |
| 5 | 요구사항 (NIU 일반 요구, 토폴로지, 주소) |
| 6 | NIU 기능 상세 (forwarding, filtering, address translation, repackaging, network message, DB 관리, 토폴로지 정보, parametrics, connection) |
| 7 | NIU 유형 (repeater, bridge, router, gateway, tractor ECU) |

인용 규격은 ISO 11783의 Part 1(일반), 2(물리 계층), 3(데이터 링크 계층), 5(네트워크 관리), 7(implement 메시지), 9(Tractor ECU)이다. 서문·저작권 고지 등 상용구는 생략한다.

## 용어 정의 (3절)

| 용어 | 의미 |
| --- | --- |
| address space | 특정 서브네트워크에서 허용되는 주소 범위. NIU가 세그먼트를 분리하면 NIU 양쪽에서 같은 주소를 서로 다른 CF가 쓸 수 있다 |
| connection | 주소 공간이 다른 세그먼트의 CF끼리 메시지를 주고받기 위해 NIU 안에 동적 가상 주소를 만드는 것 |
| network interconnection unit (NIU) | 네트워크 또는 네트워크 세그먼트를 상호 연결하는 데 쓰이는 ECU |
| port | NIU에 붙는 네트워크 세그먼트 인터페이스. NIU는 서로 다른 세그먼트에 연결된 포트를 2개 이상 가진다 |
| port pair | 한 세그먼트에서 다른 세그먼트로의 데이터 흐름 방향을 나타내는 NIU의 포트 2개 조합 |
| transparent | 서비스를 제공받는 CF가 그 서비스의 출처를 인식하지 못하는 상태. CF는 중간에 NIU가 있다는 사실을 몰라도 된다 |
| virtual CF | 다른 세그먼트에 있는 실제 CF와 같은 NAME을 사용해 NIU가 한 세그먼트에 세워 주는 겉보기 CF |
| actual CF | ECU가 해당 세그먼트에 직접 세운 CF |

## NIU와 네트워크 계층의 역할 (4절)

### 메시지 전달

네트워크에 세그먼트가 여러 개 존재할 때, NIU는 한 세그먼트에서 다른 세그먼트로 메시지를 옮기는 수단이다. 세그먼트마다 하나씩 있는 포트 사이에서 개별 메시지 프레임을 전달한다. NIU 유형에 따라 다음 작업 중 하나 이상을 수행한다.

- forwarding (6.1)
- filtering (6.2)
- address translation (6.3)
- repackaging (6.4)

### NIU 성능 판단 기준 3가지

| 기준 | 의미 |
| --- | --- |
| 초당 forwarding 보장 최대 메시지 수 | 평균·피크 버스 부하로 이 수치를 넘으면 메시지가 유실될 수 있다 |
| 초당 filtering 보장 최대 메시지 수 | 데이터베이스 엔트리 수 때문에 이 수치를 넘으면 메시지가 과도하게 지연될 수 있다 |
| 최대 transit delay | 한 CF가 보낸 메시지가 다른 버스 세그먼트의 CF에 도달하기까지 최악의 지연을 판단하는 데 쓴다 |

### 네트워크 계층이 제공하는 서비스

네트워크 계층의 핵심 역할은 세그먼트 간 메시지 전달 관리다. 필요한 기능에 따라 여러 유형의 NIU가 서비스를 제공한다.

- <strong>repeater</strong>: 메시지를 그대로 forwarding (7.1)
- <strong>bridge</strong>: 메시지를 filtering하고 message-filter database를 관리 (7.2)
- <strong>router</strong>: address translation으로 한 네트워크 세그먼트가 다른 부분에서 하나의 CF처럼 보이게 함 (7.3)
- <strong>gateway</strong>: 파라미터를 다른 메시지로 repackaging해 CF가 전송·수신·해석하기 쉽게 함 (7.4)
- <strong>tractor ECU</strong>: 트랙터 버스와 implement 버스를 연결하는 특수 NIU (5.1.3, ISO 11783-9)

이와 함께 네트워크 계층은 NIU 내부 데이터베이스에 대한 접근·설정 수단을 제공한다.

:::info NIU와 address claim
NIU는 서브네트워크의 CF를 대신해 address-claim 절차(ISO 11783-5)에 참여할 수도 있다. 다만 독점(proprietary) 서브네트워크와의 인터페이스용 router·gateway는 응용 의존적이라 ISO 11783에서 정의하지 않으며, 부품 제조사·서브시스템 공급자·OEM이 구현을 정한다.
:::

전형적인 네트워크 토폴로지(표준의 Figure 1)는 다음과 같은 구성이다. 트랙터 내부에는 engine, transmission, brakes, hitch controller가 붙은 <strong>tractor network</strong>가 있고, tractor ECU가 P2(트랙터 쪽)·P1(implement 쪽) 포트로 이를 <strong>implement network</strong>와 연결한다. implement bus에는 virtual terminal, task controller, management computer gateway 등이 붙고, breakaway connector를 거쳐 후방·전방 작업기로 이어진다. 각 작업기 내부에는 자체 ECU들이 있고, 일부는 NIU를 통해 ISO 11783 또는 타 규격 네트워크(예: 조명 컨트롤러가 붙은 서브버스)를 다시 연결한다. 작업기당 최대 노드 수는 ISO 11783-2, 세그먼트당 겉보기 CF 수 제한은 ISO 11783-5의 주소 규정을 따른다.

## 요구사항 (5절)

### NIU 일반 요구사항 (5.1.1)

- filtering·forwarding 보장 속도를 제공해야 한다(shall).
- 최대 transit-delay 값을 초과하면 안 된다.
- 과도한 지연을 피하기 위해, 한 포트에서 받은 프레임을 다른 포트로 내보내는 순서는 프레임의 우선순위를 따라야 한다.
- 우선순위가 높은 메시지를 낮은 메시지보다 먼저 forwarding해야 한다.
- 같은 우선순위 안에서는 수신 순서대로 forwarding해야 한다.
- <strong>단순 FIFO 큐는 사용 금지다.</strong> 우선순위를 무시한 채 순서대로만 내보내면 특정 포트로 가는 메시지 전체가 과도하게 지연될 수 있기 때문이다.

### NIU 일반 권고사항 (5.1.2)

- filter database를 읽고 수정하는 기능을 제공하는 것이 좋다(should).
- bridge·router·gateway 관리에 해당하는 forwarding·filtering·address translation·repackaging 설정을 위한 표준 접근, 즉 database management를 지원하는 것이 좋다.
- 동작 중에는 네트워크의 어떤 CF에 대해서도 transparent해야 한다.

### Tractor ECU (5.1.3)

트랙터의 tractor network와 implement 세그먼트 사이에는 특수한 NIU인 <strong>tractor ECU</strong>가 있어야 하며, tractor network 세그먼트를 격리·보호해야 한다. gateway와 유사하게, tractor ECU는 implement 네트워크의 다른 CF에게 트랙터를 대표한다.

### 네트워크 토폴로지 (5.2)

시스템 네트워크 토폴로지는 <strong>CF 사이에 경로가 단 하나만 존재하도록</strong> 구성해야 한다.

:::warning 루프 책임은 OEM에
이 표준은 네트워크 루프 감지나 무한 복제 메시지 방지를 요구하지 않는다. 루프가 없도록 보장하는 것은 OEM 책임이다. 내결함성을 위한 중복(redundant) 버스 세그먼트를 쓸 수는 있지만, 라우팅 경로를 감지·선택·자동 재구성하는 메커니즘은 NIU 공급자 책임이다.
:::

### 네트워크 주소 (5.3)

데이터 링크 계층(ISO 11783-3)은 256개의 source address를 제공한다. null 주소와 global 주소를 빼면 네트워크에서 이론상 허용되는 CF 주소는 <strong>254개</strong>다. 실제로는 각 ECU가 버스에 주는 전기 부하 때문에 연결 가능한 노드 수가 제한된다(ISO 11783-2).

## NIU 기능 (6절)

### Forwarding (6.1)

NIU는 2개 이상의 포트(세그먼트당 1개) 사이에서 개별 메시지 프레임을 전달한다. 규칙은 다음과 같다.

- 같은 우선순위 레벨에서는 수신 순서를 보존해야 한다.
- 큐에 있는 높은 우선순위 메시지를 낮은 우선순위보다 먼저 모두 forwarding해야 한다. 단순 FIFO 큐로는 이 요구를 만족할 수 없다.
- repeater·bridge처럼 같은 주소 공간으로 forwarding할 때는 <strong>원 발신자와 동일한 주소</strong>를 사용한다. NIU는 메시지가 들어온 세그먼트로 재전송하지 않고, 주소는 해당 ISO 11783 네트워크 안에서 유일하므로 보통 arbitration 문제가 생기지 않는다.
- 유일한 예외는 address-claim 메시지를 forwarding한 세그먼트에서 다른 CF가 동시에 같은 주소를 claim하는 경우다. 이 낮은 확률의 상황에서 NIU는 CAN 프로토콜 칩의 자동 재전송을 중단시키는 것이 좋다. 그러지 않으면 다중 충돌로 NIU가 "bus off" 상태에 빠져, 복구할 때까지 다른 메시지 forwarding이 전부 막힌다.
- 단순 repeater나 bridge로 동작하는 NIU(address translation을 하지 않는 경우)는 자신이 주소를 claim하기 전에도 세그먼트 간 forwarding을 시작할 수 있다.

:::tip 전원 인가 직후
NIU가 power-up 시퀀스를 마치고 네트워크에 연결되기 전까지는, 그 뒤에 있는 서브네트워크와 CF들은 다른 메시지를 받을 수 없다.
:::

### Filtering (6.2)

Transport Protocol, Extended Transport Protocol, Fast Packet 등 패킷화 메커니즘으로 보낸 메시지는 <strong>내부에 담긴 메시지의 PGN</strong>을 기준으로 필터링한다. 담긴 PGN이 필터에 정의돼 있으면 프로토콜 처리 메시지 자체도 그 필터에 따라 처리한다.

| 모드 | 값 | 기본 동작 | 특징 |
| --- | --- | --- | --- |
| Block mode | 0 | 모든 메시지를 forwarding | filter database에 등록된 PGN만 차단(block). 세그먼트별 버스 트래픽을 줄이는 용도로, ISO 11783 bridge의 <strong>권장 동작 모드</strong>다. 엔트리는 보통 조립·초기 설정 때 만들어 비휘발성 메모리에 유지한다 |
| Pass mode | 1 | 모든 메시지를 차단 | forwarding하려면 해당 PGN 엔트리가 존재해야 한다. 특정 기능을 수행하는 서브네트워크를 잇는 포트에 적합하다. 전체 네트워크의 CF·기능을 미리 알아야 하거나 CF가 직접 엔트리를 추가할 수 있어야 하고, 큰 filter database를 감당할 메모리·처리 능력이 필요할 수 있다. network management, diagnostics, global request 같은 메시지는 항상 forwarding되도록 일부 엔트리를 영구(permanent) 설정할 필요가 있다 |

### Address translation (6.3)

NIU는 특정 메시지에 대해 address translation을 제공할 수 있다(router, 7.3). 세그먼트(작업기) 안의 특정 기능 주소(예: 조명)를 몰라도 하나의 주소로 그 세그먼트를 참조할 수 있게 한다. 이를 위해 look-up table로 대응되는 source/destination address를 식별하는 <strong>address translation database</strong>가 있어야 하며, NIU는 이 서비스를 제공하기 전에 유효한 claimed address를 가져야 한다.

### Message repackaging (6.4)

NIU는 세그먼트 간 전달 시 메시지를 repackaging할 수 있다(gateway, 7.4). 메시지당 유효 파라미터 양을 늘려 버스 트래픽을 줄이고, 특정 CF가 수신하는 메시지 종류 수도 줄인다. 어떻게 repackaging할지 결정하는 데이터베이스나 처리 루틴이 있어야 한다.

### Network message (6.5)

NIU parametrics와 데이터베이스 접근에 쓰는 network message의 PGN 정의는 다음과 같다(Table 1).

| 항목 | 값 |
| --- | --- |
| 정의 | NIU parametrics·database 접근용 |
| 반복 전송 속도 | 사용자 요구에 따름, 초당 5회 초과 금지 |
| 데이터 길이 | 가변 |
| Extended data page / Data page | 0 / 0 |
| PDU format | 237 |
| PDU-specific field | Destination address |
| 기본 우선순위 | 6 |
| PGN | 60672 (00ED00₁₆) |

network message가 제공하는 기능은 네 가지다.

- database 접근·설정
- 포트 주소 접근
- NIU 내부 상태(status)·통계(statistics) 접근
- 네트워크 세그먼트 간 connection 열기·닫기

동작 규칙:

- 특정 목적지(global이 아닌)로 request나 command를 보내면 응답이 반드시 있어야 한다. 해당 function code를 지원하지 않거나 수행할 수 없다는 acknowledgement라도 보내야 한다.
- CF는 request/command를 보낸 뒤 응답 또는 "no response" 타임아웃(ISO 11783-3)까지 기다린 후에 다음 request/command를 보내야 한다.
- 멀티패킷 PGN의 경우 한 번의 request로 여러 CAN 데이터 프레임이 발생할 수 있다.
- 8바이트 미만의 가변 길이 메시지는 남는 바이트를 FF₁₆으로 채운다. 8바이트를 넘으면 transport protocol을 쓴다(ISO 11783-3).

#### Message function (6.5.2)

network message 데이터 필드의 <strong>1번째 바이트</strong>가 수신자가 수행할 기능을 식별한다(Table 2).

| Function code | 정의 | 방향 |
| --- | --- | --- |
| 0 | filter database 사본 요청 | CF → NIU |
| 1 | filter database 사본 요청에 대한 응답 | NIU → CF |
| 2 | filter database 엔트리 추가 | CF → NIU |
| 3 | filter database 엔트리 삭제 | CF → NIU |
| 4 | filter database 엔트리 clear | CF → NIU |
| 5 | 폐기(obsolete), 사용 금지 | N/A |
| 6 | filter database 엔트리 생성 | CF → NIU |
| 7 | NAME 조건부 filter database 엔트리 추가 요청 | CF → NIU |
| 8–63 | 예약 | N/A |
| 64 | source address 목록 요청 | CF → NIU |
| 65 | source address 목록 응답 | NIU → CF |
| 66 | source address + NAME 목록 요청 | CF → NIU |
| 67 | source address + NAME 목록 응답 | NIU → CF |
| 68–127 | 예약 | N/A |
| 128 | NIU general parametrics 요청 | CF → NIU |
| 129 | NIU general parametrics 응답 | NIU → CF |
| 130 | general 통계 파라미터 리셋 명령 | CF → NIU |
| 131 | NIU-specific parametrics 요청 | CF → NIU |
| 132 | NIU-specific parametrics 응답 | NIU → CF |
| 133 | specific 통계 파라미터 리셋 명령 | CF → NIU |
| 134–191 | 예약 | N/A |
| 192 | connection open 요청 | CF → NIU |
| 193 | connection open 요청 응답 | NIU → CF |
| 194 | connection close 요청 | CF → NIU |
| 195 | connection close 요청 응답 | NIU → CF |
| 196–255 | 예약 | — |

#### Port number (6.5.3)

포트 번호는 니블(nibble) 하나로 표현한다(Table 3).

| Port number | 정의 |
| --- | --- |
| 0 | Local (메시지를 수신한 그 포트) |
| 1~14 | 할당 가능 |
| 15 | Global (모든 포트) |

- <strong>0 (local)</strong>: 연결 포트 번호를 모를 때 CF가 NIU와 메시지를 주고받기 위해 사용한다. 메시지를 수신한 "local" 포트로 향한다.
- <strong>15 (global)</strong>: CF가 NIU의 포트 수를 몰라도 메시지를 보낼 수 있게 한다.

<strong>Port pair (from/to)</strong>: message function이 요구하는 경우, 2번째 바이트가 포트 간 메시지 방향을 나타낸다. 하위 니블(bits 3–0)이 "To" 포트, 상위 니블(bits 7–4)이 "From" 포트다. 둘 중 하나라도 global이면 NIU는 port pair별로 여러 개의 응답을 보낼 수 있다.

### Database management (6.6)

NIU 내부의 여러 데이터베이스(parametrics, 네트워크 토폴로지 포함)에 접근·설정하는 표준 방법을 제공하는 것이 좋다. 관련 기능은 전원 상실에도 값이 유지되도록 <strong>비휘발성 메모리</strong>를 쓰는 것이 좋으며, 정적 filter database를 유지할 때 특히 중요하다.

:::info 동적 filter database
CF가 추가·제거될 때 쉽게 재구성할 수 있도록 전원 상실 시 지워지는 별도의 동적 filter database를 둘 수도 있으나, 이 표준은 그 방식을 정의하지 않는다.
:::

#### Filter database 설정 방법 (6.6.2.1)

message filter database는 다음 세 방법으로 설정할 수 있다.

| 방법 | 설명 | 한계 |
| --- | --- | --- |
| 공급자 고정 DB | 제조 시점에 OEM이 사전 설정 | CF·메시지 전체를 미리 알아야 하고, 이후 네트워크 변경은 서비스 중 재설정 없이 반영 불가 |
| 진단 도구 설정 | 서비스 절차의 일부로 네트워크를 통해 bridge를 설정 | — |
| 임의 CF가 상시 설정 | 네트워크의 어떤 CF든 아무 때나 설정 | 별도 보안 절차가 필요할 수 있고, 재설정 접근 제한은 응용에 따라 다름 |

N.MFDB_Create_Entry로 만든 엔트리에는 생성한 CF의 <strong>NAME이 부착</strong>되며, 같은 NAME만 그 엔트리를 제거할 수 있다. 이는 요청 충돌 자체를 막지는 않지만 엔트리의 예기치 않은 삭제를 방지한다. 단, 진단 도구 사용 시 이 제약을 무시(override)할 수 있는 수단은 마련해야 한다.

각 filter database 엔트리는 필터링할 PGN 하나와 pass/block 여부, 그리고 port pair(방향)를 식별한다. 방향 지정은 특정 서브네트워크로의 트래픽을 제한하면서도 그 서브네트워크발 특정 메시지는 forwarding하도록 하는 데 필요하다. port pair의 한쪽이 15(global)이면 NIU 포트 번호를 몰라도 메시지를 보낼 수 있고, NIU는 모든 port pair에 대해 다중 응답을 낸다. NIU는 local(0)·global(15) 포트 식별 방식 둘 다로 filter database를 설정할 수 있는 것이 좋다.

예: tractor ECU는 엔진 데이터가 implement 세그먼트로 나가지 않게 필터링하면서, implement 세그먼트에서 오는 request는 트랙터로 forwarding하도록 설정한다.

#### Filter mode (6.6.2.2)

filter database에 등록된 PGN의 필터 모드는 filter mode byte로 식별한다(Table 4).

| 값 | 정의 |
| --- | --- |
| 0 | 지정 PGN을 block (기본 = 전부 pass) |
| 1 | 지정 PGN을 pass (기본 = 전부 block) |
| 2–255 | 예약 |

#### Filter database 설정 메시지 (6.6.2.3)

모든 메시지는 PGN 60672(00ED00₁₆), destination-specific으로 보낸다. 명령에 대한 확인 응답은 Acknowledgment Message(PGN 59392)로 제공된다.

<strong>N.MFDB_Request (function 0)</strong> — CF가 NIU에 filter database 사본을 요청.

| 바이트 | 내용 |
| --- | --- |
| 1 | Message function = 0 |
| 2 | Port pair (bits 3–0 "To", bits 7–4 "From") |
| 3–8 | 예약, FF₁₆ 전송 |

데이터 길이 8바이트.

<strong>N.MFDB_Response (function 1)</strong> — 필터링되는 PGN 엔트리와 filter mode를 담은 NIU의 응답. 데이터 길이 가변.

| 바이트 | 내용 |
| --- | --- |
| 1 | Message function = 1 |
| 2 | Port pair |
| 3 | Filter mode |
| 4–n | PGN 엔트리들 |

<strong>N.MFDB_Add (function 2)</strong> — filter database에 엔트리 1개 이상 추가. "To" 포트를 global로 하면 해당 "From" 포트를 포함하는 모든 port pair에 엔트리가 만들어진다. 이 명령에는 filter mode가 포함되지 않으므로, 사용하는 CF는 해당 port pair의 filter mode를 사전에 알고 있어야 한다. filter mode는 그 port pair의 database를 clear 후 재구축하지 않는 한 바꿀 수 없다.

| 바이트 | 내용 |
| --- | --- |
| 1 | Message function = 2 |
| 2 | Port pair |
| 3–n | PGN 엔트리들 |

<strong>N.MFDB_Delete (function 3)</strong> — 엔트리 1개 이상 삭제. 구조는 N.MFDB_Add와 같고 function code만 3이다.

<strong>N.MFDB_Clear (function 4)</strong> — 지정한 port pair·방향의 filter database를 통째로 clear. 데이터 길이 8바이트, 바이트 3–8은 FF₁₆.

<strong>N.MFDB_Create_Entry (function 6)</strong> — filter mode를 포함해 엔트리를 생성. "To" 포트가 global이면 해당 "From" 포트를 포함한 port pair마다 엔트리가 만들어질 수 있다. 포함된 filter mode는 기존 port pair의 filter mode를 바꾸지 못한다. clear되지 않은 database에 시도하면 요청자에게 오류를 반환하는 것이 권장된다. 하나의 database 레코드에 서로 다른 모드의 엔트리가 섞이는 것을 막기 위해, (Set_Mode 명령 폐기와 함께) N.MFDB_Add 사용으로 충분하도록 설계됐다.

| 바이트 | 내용 |
| --- | --- |
| 1 | Message function = 6 |
| 2 | Port pair |
| 3 | Filter mode |
| 4–n | PGN 엔트리들 |

<strong>N.MFDBNQ_Add (function 7)</strong> — PGN과 <strong>발신자 NAME</strong>을 함께 조건으로 하는 filter database 엔트리 추가. 공통 주소 공간·분리 주소 공간 모두에 적용할 수 있다.

- 주소 공간이 다른 세그먼트에서 메시지를 forwarding할 때, open connection(6.9)이 없으면 NIU는 <strong>자기 자신의 주소</strong>를 source address로 사용한다. 발신 CF와 open connection이 맺어져 있으면 virtual CF의 SA를 사용한다.
- PDU2 메시지와 global 주소로 보내진 PDU1 메시지를 bridge 너머로 필터링할 수 있다. 요청자가 64-bit NAME과 64-bit qualification mask를 지정하면, NIU가 자신의 source address/NAME 테이블에서 그 정체성에 해당하는 source address를 연결한다.
- 선택적으로 <strong>data rate reduction</strong>을 적용할 수 있다. 원 네트워크에서의 갱신 주기와 무관하게 forwarding 최대 갱신 주기를 지정하는 기능으로, forwarding 시에는 가장 최신 데이터를 사용해야 한다.

| 바이트 | 내용 |
| --- | --- |
| 1 | Message function = 7 |
| 2 | Port pair |
| 3 | Filter mode |
| 4 | 예약 |
| (t) 5 | 최대 전송 속도: 0 = 예약, 1–250 = 해당 PGN의 초당 메시지 수, 251–254 = ISO 용도, 255 = 속도 제한 없음 |
| (p) 6–8 | PGN 엔트리 |
| (d) 9–16 | Desired source NAME (이 PGN을 수용할 CF의 NAME) |
| (n) 17–24 | NAME qualifier (64-bit 마스크. 비트 1 = 그 비트가 desired NAME과 일치해야 함, 비트 0 = don't care) |

바이트 t, p, d, n 묶음은 엔트리 수만큼 반복된다.

:::details filter database 접근 예 (Table 5)
오프보드 진단 도구(SA = 249)가 tractor ECU(SA = 240)의 filter database에서, implement로 가는 방향(port 1 → port 2)에서 필터링 중인 PGN 목록을 요청하는 시나리오다.

| 구분 | PRI | EDP | DP | PF | DA | SA | Control code | Port pair | Filter mode | PGN | 예약 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| N.MFDB_Request | 110 | 0 | 0 | 237 | 240 | 249 | 0 | 12₁₆ | FF₁₆ | FFFFFF₁₆ | FFFF₁₆ |
| N.MFDB_Response | 110 | 0 | 0 | 237 | 249 | 240 | 1 | 12₁₆ | 00₁₆ | 00FEE3₁₆ | FFFF₁₆ |

응답을 해석하면: filter mode 0(block)이고 차단 중인 유일한 메시지는 engine configuration(00FEE3₁₆)이다.
:::

### Network topology information (6.7)

이 표준을 따르는 모든 NIU는 다른 CF에게 transparent해야 한다. 그런데 database를 제대로 설정하려면 네트워크 토폴로지 지식이 필요할 수 있으므로, 그 빠진 정보를 얻기 위한 메시지가 정의돼 있다.

데이터 바이트의 하위 니블에 담기는 포트 번호로 NIU 포트에 연결된 주소를 식별한다. 네트워크에 NIU가 여러 개면 하나의 응답만으로는 source address가 어느 포트에 있는지 확정할 수 없다. 특정 source address는 원격 버스 세그먼트에 있을 수 있으므로, 각 NIU의 응답을 비교해 어느 local 버스 세그먼트에 해당 주소가 있는지 판별해야 한다. NIU는 먼저 request-for-address-claim을 수행한 뒤 포트별 source address 목록을 구축해야 한다.

:::tip 주소 요청 타임아웃
address request의 타임아웃은 <strong>300 ms</strong>를 쓴다. NIU 1단 지연 + CF 응답 시간을 합한 값이다.
:::

#### N.NT_Request / N.NT_Response (6.7.2.1, 6.7.2.2) — 구형, 신규 설계 비권장

N.NT_Request(function 64)는 NIU 포트의 source address 목록을 요청한다. port pair가 <strong>같은 주소 공간</strong>을 공유할 때, NIU 기준 포트들의 물리적 배치·토폴로지를 파악하려는 용도다. bridge의 경우 address claim이 NIU 양쪽에 다 나타나므로, 어느 포트가 어느 세그먼트에 속하는지 이 메시지로 알아낼 수 있다.

| 메시지 | 구조 |
| --- | --- |
| N.NT_Request (function 64, CF→NIU, 8바이트) | Byte 1 = 64, Byte 2: bits 3–0 = 포트 번호·bits 7–4 = F₁₆, Byte 3–8 = FF₁₆ |
| N.NT_Response (function 65, NIU→CF, 가변) | Byte 1 = 65, Byte 2: bits 3–0 = 포트 번호·bits 7–4 = F₁₆, Byte 3–n = source address 엔트리들 |

:::warning 신규 설계에는 사용하지 말 것
두 메시지 모두 신규 설계에는 권장되지 않는다. NAME까지 함께 주는 N.NTX(6.7.2.3/6.7.2.4)를 사용한다.
:::

#### N.NTX_Request (6.7.2.3, function 66)

NIU 포트의 source address와 그에 연결된 NAME 목록을 요청한다. 조회 대상 세그먼트가 요청자와 <strong>다른 주소 공간</strong>일 때(즉 NIU가 그 port pair에 대해 router로 동작할 때) 사용한다. 이 경우 요청자는 대상 세그먼트의 address claim을 직접 본 적이 없기 때문이다. global 포트 번호로는 요청할 수 없다.

| 바이트 | 내용 |
| --- | --- |
| 1 | Message function = 66 |
| 2 | bits 3–0 = 요청 포트 번호(0–14), bits 7–4 = F₁₆ |
| 3–8 | 예약, FF₁₆ |

8바이트, CF → NIU, destination-specific.

#### N.NTX_Response (6.7.2.4, function 67)

지정 포트에 연결된 네트워크 세그먼트의 source address와 NAME 전체 엔트리를 반환한다. <strong>그 세그먼트에서 NIU 자신이 claim한 주소와 NAME도 포함</strong>한다.

| 바이트 | 내용 |
| --- | --- |
| 1 | Message function = 67 |
| 2 | bits 3–0 = 요청 포트 번호(0–14), bits 7–4 = F₁₆ |
| 3 | 현재 포트에서 보고하는 source address/NAME 쌍 개수(Port_Num) |
| 4 | 첫 번째 source address |
| 5–12 | 첫 번째 source address의 NAME |
| 13, 14–21, … | 두 번째 이후 쌍. 9바이트(SA 1 + NAME 8) 단위로 Port_Num개 반복 |

가변 길이, NIU → CF, destination-specific.

### NIU parametrics (6.8)

NIU의 상태(status)·통계(statistics)에 접근하는 message function은 두 세트다. NIU 전체에 적용되는 항목은 <strong>general parametric</strong> 메시지로, 특정 port pair에 적용되는 항목은 <strong>specific parametric</strong> 메시지로 접근한다. 유효 값 범위는 ISO 11783-7 규약을 따르며, 모든 비트가 1이면 "not available"이다. parametric identifier는 각 1바이트다.

- 응답 목록의 parametric 순서는 요청 목록의 identifier 순서와 같다. 모든 parametric과 identifier가 고정 길이라 구분자가 필요 없다.
- 한 주소에 대해 응답을 받은 후에야 다음 요청을 보낼 수 있지만, 요청 하나로 여러 parametric을 물을 수 있다.
- <strong>항상 Parameter 0으로 요청하는 것이 권장</strong>된다. 전체 목록이 번호 순으로 반환된다.

#### NIU parametrics 목록 (Table 6)

| Parametric ID | 바이트 수 | 리셋 가능 | 정의 |
| --- | --- | --- | --- |
| 0 | N/A | — | 전체 파라미터를 번호 순으로 요청 (응답에는 쓰이지 않음) |
| 1 | 2 | — | Buffer size (bytes) |
| 2 | 2 | — | Maximum filter database size (bytes) |
| 3 | 2 | — | Number of filter database entries |
| 4 | 2 | — | 초당 최대 수신 메시지 수 |
| 5 | 2 | — | 초당 최대 forwarding 메시지 수 |
| 6 | 2 | — | 초당 최대 filtering 메시지 수 |
| 7 | 2 | — | Maximum transit delay time (ms) |
| 8 | 2 | Yes | Average transit delay time (ms) |
| 9 | 2 | Yes | 버퍼 오버플로로 유실된 메시지 수 |
| 10 | 2 | Yes | transit delay 초과 메시지 수 |
| 11 | 2 | Yes | 초당 평균 수신 메시지 수 |
| 12 | 2 | Yes | 초당 평균 forwarding 메시지 수 |
| 13 | 2 | Yes | 초당 평균 filtering 메시지 수 |
| 14 | 4 | — | 마지막 power-on reset 이후 uptime (s) |
| 15 | 1 | — | 포트 수 |
| 16 | 1 | — | NIU Type |
| 17–255 | N/A | — | ISO 향후 할당 예약 |

파라미터 정의 공통 사항: 1바이트 초과 데이터는 ISO 11783-7의 바이트 순서 규약을 따르고, 값 범위 규약도 ISO 11783-7을 따른다(별도 명시가 없는 한). 2바이트 파라미터의 데이터 범위는 0~64 255, 분해능은 1 단위/bit·offset 0이다(예: transit delay는 1 ms/bit). 파라미터에 따라 NIU 전체용, 특정 port pair용, 또는 둘 다일 수 있다.

주요 파라미터 보충:

- <strong>Parametric 14 (uptime)</strong>: 4바이트, 1 s/bit, 범위 0~4 211 081 215초. 이전 판(2001)에서 정의가 바뀌어 SAE J1939-31과 조화된 항목이다.
- <strong>Parametric 15 (포트 수)</strong>: 1바이트, 범위 2~14. 이 파라미터는 F₁₆(Not Available) 외의 모든 값 상태를 유효 데이터로 쓴다.
- <strong>Parametric 16 (NIU Type)</strong>: port pair마다 다른 타입을 신고할 수 있다. 값 배정은 다음과 같다(Table 7).

| 값 | 정의 |
| --- | --- |
| 0 | None (해당 port pair에 상호작용 없음) |
| 1 | Repeater |
| 2 | Bridge |
| 3 | Router |
| 4 | Gateway |
| 5 | Tractor ECU |
| 6–249 | 예약 |
| 250 | Multiple (타입이 다른 port pair가 여럿일 때 general parametric에서 사용) |
| 251–255 | 예약 |

:::info Repeater/Bridge 값의 전제
Repeater·Bridge 값은 repeater가 네트워크 통신용 주소를 claim한 경우에만 쓸 수 있다. 이 타입들은 transparent할 수 있어서 다른 CF가 그 존재 자체를 모를 수 있다.
:::

#### General parametric 메시지 (6.8.3)

<strong>N.GP_Request (function 128, CF→NIU)</strong> — parametric 1개 이상 요청. parametric 0을 요청하면 전체 목록이 반환된다. 8바이트 초과면 transport protocol 사용, 7개 미만 요청 시 남는 바이트는 FF₁₆. identifier는 오름차순으로 나열해야 한다.

| 바이트 | 내용 |
| --- | --- |
| 1 | Message function = 128 |
| 2–n | Parametric identifier, 바이트당 1개 |

<strong>N.GP_Response (function 129, NIU→CF)</strong> — 요청받은 parametric들을 반환. parametric 0 요청에 대한 응답은 전체 parametric을 번호 순으로 담는다. 반환 목록이 기대보다 짧으면, NIU가 목록의 추가 항목을 알지 못해 마지막으로 아는 파라미터에서 멈췄다는 뜻이다.

| 바이트 | 내용 |
| --- | --- |
| 1 | Message function = 129 |
| 2, 3 | 첫 번째 요청 parametric |
| 4–n | 나머지 요청 parametric들 |

<strong>N.GP_Reset_Statistics (function 130, CF→NIU, 8바이트)</strong> — Table 6에서 리셋 가능("Yes")으로 표시된 통계 파라미터 전부를 clear하는 명령. 바이트 2–8은 FF₁₆. Acknowledgment Message(PGN 59392)로 확인 응답한다.

#### Specific parametric 메시지 (6.8.4)

port pair 단위 parametric용이며 구조는 general과 같되 <strong>2번째 바이트에 port pair</strong>(bits 3–0 "To", bits 7–4 "From")가 들어간다.

| 메시지 | function | 방향 | 구조 |
| --- | --- | --- | --- |
| N.SP_Request | 131 | CF → NIU | Byte 1 = 131, Byte 2 = port pair, Byte 3–n = parametric identifier(오름차순, 6개 미만이면 FF₁₆ 패딩) |
| N.SP_Response | 132 | NIU → CF | Byte 1 = 132, Byte 2 = port pair, Byte 3,4 = 첫 parametric, Byte 5–n = 나머지 |
| N.SP_Reset_Statistics | 133 | CF → NIU | Byte 1 = 133, Byte 2 = port pair, Byte 3–8 = FF₁₆. PGN 59392로 확인 응답 |

### Connection을 통한 destination-specific 메시지 forwarding (6.9)

#### 배경 (6.9.1)

gateway나 router가 implement 서브네트워크를 ISO 11783 implement network에 연결하는 토폴로지에서, 각 서브네트워크 세그먼트는 implement network와 <strong>분리된 자체 주소 공간</strong>을 가진다. 이런 세그먼트에는 센서·액추에이터·저성능 컨트롤러처럼 메인 세그먼트와의 통신량이 적은 CF들이 놓인다.

전형적인 router(7.3)는 address translation database를 이용해 주소 공간이 다른 세그먼트 간에 메시지를 라우팅한다. 이 능력 덕분에 서비스 도구가 <strong>한 연결점에서 여러 네트워크 세그먼트를 진단</strong>할 수 있고, 소프트웨어·캘리브레이션 다운로드도 쉬워진다. 여러 세그먼트를 가진 작업기의 CF가 메인 implement network의 VT(virtual terminal)와 통신해야 하는 경우도 예다.

address translation 대신, <strong>CF가 동적으로 설정하는 router</strong>도 있다. 네트워크의 "발견된(discover)" 토폴로지와 NAME이 나타내는 CF 기능을 근거로 connection을 만든다. connection이 맺어진 뒤에는 NIU가 메시지 전달을 알아서 처리하므로, 참여 CF들은 초기 토폴로지 발견·connection 열기 절차 외에는 <strong>기존 소프트웨어 구현을 바꿀 필요 없이</strong> 단일·멀티패킷 destination-specific 메시지를 그대로 쓸 수 있다.

#### Connection 수립 절차 (6.9.2)

network segment 1의 CF A가 segment 2의 CF C와 통신해야 하는 상황(표준의 Figure 2)의 흐름은 다음과 같다.

| 단계 | 동작 |
| --- | --- |
| 1 | CF A가 NIU B에 N.NTX_Request를 보내 network 2에 연결된 CF들의 NAME 목록을 얻는다 |
| 2 | 목록에서 대상 CF C가 network 2에 있음을 확인하면, NIU B에 connection open을 요청한다 |
| 3 | NIU B는 forwarding용 connection 정보를 기록하고, network 1에 CF C의 NAME으로 주소를 claim해 <strong>virtual CF C^</strong>를 만든다. 이 주소는 CF C가 network 2에서 claim한 주소와 같을 필요가 없고, network 1에서 사용 가능한 self-configurable 주소 범위에서 고른다 |
| 4 | NIU는 network 2에도 CF A의 NAME과 가용 주소로 <strong>virtual CF A^</strong>를 claim한다 |
| 5 | C^의 address claim이 성공하면, CF A는 자기 세그먼트의 여느 주소처럼 C^로 destination-specific 메시지를 보내기 시작한다 |
| 6 | NIU B는 목적지가 C^인 메시지를 받으면 forwarding 정보를 참조해, source address = A^, destination = CF C로 바꿔 network 2에 재전송한다 |
| 7 | CF C는 A^에게서 온 메시지로 받아들여 보안 접근 권한 평가, 하드웨어 동작, 필요한 응답·acknowledgement·NACK 송신 등 통상적인 처리를 한다 |

connection을 연 CF는, 다른 CF가 그 connection을 붙들고 있지 않는 한 닫을 수도 있다. 같은 CF가 같은 connection을 여러 번 열었어도 <strong>하나의 connection</strong>으로 간주되어 close 명령 한 번으로 닫힌다.

#### 다중 connection (6.9.3)

- CF A가 CF C에 이어 network 2의 CF D에도 연결하는 경우(Figure 3): A^가 이미 network 2에 존재하므로 재사용하고, D^의 주소만 network 1에 추가로 claim한다. 첫 connection이 닫히지 않았으므로 A^는 C^·D^ 양쪽으로 메시지를 forwarding한다.
- network 1의 다른 CF F가 같은 CF C에 연결하는 경우(Figure 4): F가 C^로 메시지를 보내면 등록된 open connection이 없으므로 ISO 11783-3에 정의된 <strong>Access Denied</strong> control byte로 acknowledge된다. F는 CF C와의 connection open을 요청해야 하며, 그 결과 network 2에 F^가 세워지고 network 1의 C^는 재사용된다. 이후 F가 C^로 보낸 메시지는 CF C로 forwarding된다.
- 한 네트워크 세그먼트에서 이미 claim된 주소는 추가 connection을 열 때 다시 claim할 필요가 없다.
- 이 절차를 반복하면 network 2에 있는 또 다른 NIU의 포트 너머 CF들도 알아낼 수 있고, 그렇게 <strong>네트워크 전체의 최말단 세그먼트까지</strong> 탐색할 수 있다(Figure 5의 멀티 세그먼트 예: A가 NIU E 너머 network 3의 G까지 G^^로 연결).

#### Connection 요구사항 (6.9.4)

두 네트워크 세그먼트 간 connection을 수립하는 NIU는 다음을 지켜야 한다.

1. 한 번 열린 connection은 현재 power cycle 동안, 또는 처음 연 CF가 닫을 때까지 유지되어 메시지를 계속 주고받을 수 있다.
1. transport protocol이 필요한 메시지도 보낼 수 있다. NIU는 transport 세션 타이밍 요구를 지킬 만큼 충분히 작은 지연으로 재전송해야 한다.
1. 세그먼트 간 virtual connection 수는 NIU의 유지 능력과 세그먼트당 총 253개 CF 주소 한계로만 제한된다. self-configurable 주소는 <strong>128~247</strong>만 사용할 수 있다.
1. virtual CF는 원본 CF와 같은 NAME을 갖되, 나타나는 네트워크에서의 source address는 원본과 같아도 되고 달라도 된다.
1. open connection에 참여 중인 CF가 어떤 이유로든 주소를 바꾸면, NIU는 이를 추적해 connection 정보를 갱신해야 한다.
1. open connection에 참여 중인 CF가 NAME의 일부라도 바꾸려면 <strong>먼저 자신의 open connection을 모두 닫아야</strong> 한다. 닫지 않고 바꾸면 NIU가 예측 불가능하게 동작할 수 있다. 새 NAME과 주소로 새 connection을 수립해야 한다.
1. open connection의 CF가 어떤 이유로든 address claim을 재전송하면, NIU도 virtual CF의 서브네트워크에서 해당 주소로 address claim을 보내야 한다.
1. open connection의 CF가 주소를 claim하지 못해 CANNOT claim을 보내면, NIU는 virtual connection을 닫고 virtual CF의 서브네트워크에 CANNOT claim을 보내야 한다.
1. 한 네트워크 세그먼트에서 하나의 CF에 대한 virtual 표현은 <strong>하나만</strong> 존재해야 한다. 그 virtual CF가 여러 connection에 연관될 수는 있다.
1. connection을 닫아도 virtual CF가 네트워크에서 제거되지는 않는다. 그 virtual CF가 관련된 <strong>모든 connection이 닫힐 때까지</strong> 연결 상태를 유지한다.
1. NIU가 다른 네트워크 세그먼트(port pair)의 NAME·주소 테이블을 보고할 때, 그 세그먼트에서의 자기 자신의 NAME·주소도 함께 보고해야 한다.

virtual CF는 다른 CF들에게 보통 CF처럼 보이므로, connection을 열지 않은 actual CF도 통신을 시도할 수 있다. NIU는 해당 virtual CF에 대한 open connection이 설정되지 않은 CF가 virtual CF로 보낸 메시지를 <strong>NACK해야</strong> 한다. Acknowledge 메시지의 Address Acknowledged(ADD_NACK) 파라미터에 virtual CF의 주소를 담고, control byte는 "access denied"(2)로 설정한다.

#### Connection 메시지 (6.9.5)

:::warning function code 표기 불일치
Table 2(6.5.2)에는 192 = open 요청, 193 = open 응답, 194 = close 요청, 195 = close 응답으로 정리돼 있으나, 6.9.5의 개별 메시지 정의에는 192 = N.OC_Request, 193 = N.CC_Request, 194 = N.OC_Response, 195 = N.CC_Response로 적혀 있다. 원문 자체의 불일치이므로 구현 시 상호 운용 대상과 해석을 맞춰야 한다.
:::

<strong>N.OC_Request (function 192)</strong> — 다른 네트워크 세그먼트로의 connection open 요청. 요청 CF가 NIU로 보내며, 목적지 세그먼트의 port pair와 목적지 세그먼트에 있는 원하는 CF의 NAME을 담는다. 10바이트라 Transport Protocol을 사용한다.

| 바이트 | 내용 |
| --- | --- |
| 1 | Message function = 192 |
| 2 | Port pair — bits 3–0 "To": connection 대상 CF의 세그먼트에 연결된 NIU 포트, bits 7–4 "From": 요청자 세그먼트에 연결된 포트(local port 0 권장) |
| 3–10 | "To" 포트에서 연결할 CF의 NAME |

요청 CF는 network message의 N.NTX_Request(6.7.2.3)로 목적지 세그먼트의 CF 정체를 먼저 파악해 원하는 CF를 골라야 한다. 이미 활성인 connection과 정확히 일치하는 open 요청이 오면 응답은 평소처럼 보내고 connection 상태는 바뀌지 않는다.

<strong>N.CC_Request (function 193)</strong> — connection close 요청. 구조는 N.OC_Request와 같고(10바이트, Transport Protocol) 바이트 3–10은 원격 네트워크에서 분리할 CF의 NAME이다. <strong>connection을 처음 연 CF만</strong> 닫을 수 있으며, 열 때 사용한 것과 같은 NAME을 사용해야 한다.

<strong>N.OC_Response (function 194)</strong> — open 요청에 대한 NIU의 응답. 8바이트, NIU → 요청 CF.

| 바이트 | 내용 |
| --- | --- |
| 1 | Message function = 194 |
| 2 | Port pair — bits 3–0 "To": 요청자 세그먼트 쪽 포트(local port 0), bits 7–4 "From": 대상 CF 세그먼트 쪽 포트 |
| 3 | Status — bits 1,2: 0x01 = 성공, 0x00 = 실패. bits 3–8 예약 |
| 4 | Failure Reason Code |
| 5–8 | 예약(FF₁₆) |

| Failure Reason Code | 의미 |
| --- | --- |
| 0 | 해당 NAME의 CF를 찾을 수 없음 |
| 1 | 그 NAME에 대한 connection 수 초과 |
| 2 | NIU의 connection 수 초과 |
| 3 | Busy |
| 4 | 지원하지 않는 요청 타입 |
| 5–254 | 예약 |
| 255 | Not available |

<strong>N.CC_Response (function 195)</strong> — close 요청에 대한 NIU의 응답. 구조는 N.OC_Response와 같다(8바이트, Status + Failure Reason Code).

## NIU 유형 (7절)

### Repeater (7.1)

- 네트워크의 어떤 CF에게도 본질적으로 transparent하다.
- <strong>같은 데이터 속도</strong>로 동작하는 버스 세그먼트 사이에서, sub-bit-time 간격으로 신호를 재생(regenerate)해 forwarding하며 anti-loopback/lockout을 갖는다.
- 메시지를 필터링할 수 없으므로 전부 forwarding한다.
- sub-bit-time 지연으로 동작하므로 최대 transit delay는 <strong>bit time의 10% 미만(250 kbit/s에서 400 ns)</strong>이 좋다. 이렇게 하면 repeater를 가로질러 bit-wise arbitration이 올바르게 일어나면서도 합리적인 전파 지연(케이블 거리)을 허용한다.
- fault isolation을 제공한다면, 세그먼트의 버스 fault를 감지했을 때 해당 송신기(들)를 비활성화할 수 있다.

:::info 참고
repeater에는 NIU data management 기능이 정의되지 않는다. 또 일부 물리 계층은 CAN arbitration에 영향을 주는 transit delay 때문에 repeater를 지원할 수 없다.
:::

### Bridge (7.2)

- 네트워크의 어떤 CF에게도 본질적으로 transparent하다.
- 버스 세그먼트 간에 forwarding과 <strong>filtering</strong>을 모두 수행하며, 그 과정에서 메시지를 저장한다.
- filtering으로 각 세그먼트의 버스 트래픽 양을 효과적으로 줄일 수 있다. 응용에 따라 수신 메시지의 일부·전부를 필터링하거나 아예 하지 않을 수 있다.
- bridge 통과 transit delay가 존재하며 최대치는 응용 의존적이지만, 이 표준이 권장하는 최대 transit delay는 <strong>10 ms</strong>다.

### Router (7.3)

- <strong>address claim 메시지는 router를 통과하지 않는다.</strong>
- 동작 상태에 들어가면 어떤 CF에게도 본질적으로 transparent한 것이 좋다.
- forwarding·filtering에 더해 한 포트(버스 세그먼트)에서 다른 포트로 <strong>주소를 재매핑(address translation)</strong>할 수 있다.
- data management 기능은 필수는 아니나, forward·filter·address-translation database 설정의 표준 접근을 위해 지원하는 것이 좋다.
- address remapping(message routing) 덕분에 서브시스템이 네트워크의 다른 부분에는 <strong>하나의 주소</strong>로 보인다. message filter database는 보통 pass mode(1)로 설정해 특정 엔트리가 있는 메시지 외에는 전부 차단한다. CF가 시스템의 다른 개별 CF(주소)를 알 필요가 없어져 CF 개발이 단순해진다.
- 다만 address claim이 router를 넘지 못하므로 address-translation map을 제공하는 look-up table이 반드시 있어야 하며, translation·forwarding 지연이 다소 발생한다.

### Gateway (7.4)

- router의 동작(7.3)에 더해 수행하는 핵심 기능이 <strong>message repackaging</strong>이다.
- 동작 상태에서는 어떤 CF에게도 본질적으로 transparent한 것이 좋다.
- 하나 이상의 메시지에서 파라미터들을 꺼내 하나 이상의 "새" 메시지로 재조합할 수 있다. 여러 CF의 파라미터를 묶어 다른 CF가 전송·수신·해석하기 쉽게 만든다.
- database 기능은 필수는 아니나 forward·filter·address-translation·message-repackaging database 설정의 표준 접근을 위해 지원하는 것이 좋다.
- router처럼 CF가 서브시스템의 다른 개별 CF(주소)를 몰라도 되므로 CF 개발이 단순해진다. message filter database는 보통 pass mode(1)로 설정한다.
- translation·repackaging·forwarding 지연이 있으며, repackaging용 database를 포함한 message-building 기능이 필요하다.

### Tractor ECU (7.5)

트랙터 또는 자주식(self-propelled) 작업기에서 implement bus와 tractor bus를 연결하는 특수 NIU다. 상세는 5.1.3, ISO 11783-1, ISO 11783-9를 따른다.

## 참고 문헌 (Bibliography)

ISO 11898-1(CAN data link layer), ISO 11898-2(CAN high-speed medium access unit), SAE J1939, SAE J1939-31(Network Layer)이 참고 문헌으로 실려 있다.

:::tip 실무 요약
- 세그먼트 간 전달은 우선순위 기반 큐가 필수이고 단순 FIFO는 금지다.
- bridge는 block mode(기본 pass) 권장, router·gateway는 pass mode(기본 block)가 전형이다.
- 같은 주소 공간이면 repeater/bridge(원 주소 유지 forwarding), 다른 주소 공간이면 router/gateway(address translation 또는 connection + virtual CF)를 쓴다.
- NIU 상태·설정 접근은 전부 PGN 60672(00ED00₁₆) network message 하나로, 1번째 바이트의 function code로 구분한다.
- 권장 성능 지표: bridge 최대 transit delay 10 ms, repeater는 bit time의 10% 미만, address request 타임아웃 300 ms, network message 반복률 최대 5회/s.
:::
