---
title: "표준 정리: Part 9 — Tractor ECU"
description: "ISO 11783-9(Tractor ECU) — TECU의 게이트웨이 역할, 클래스 구분, 전원 관리 시퀀스를 정리한 표준 요약이다."
date: 2026-08-21
tags: [ISOBUS, ISO11783, 표준정리]
---

# ISO 11783-9: Tractor ECU 정리

::: info 이 문서에 대해
ISO 11783-9 표준 원문을 학습 목적으로 재구성한 <strong>비공식 요약·해설</strong>이다. 규범적 판단이 필요할 때는 반드시 원문 표준을 확인해야 한다.
:::

## 개요

ISO 11783-9는 ISOBUS 네트워크에서 <strong>Tractor ECU(TECU)</strong>를 정의하는 파트다. TECU는 트랙터 내부 버스(tractor bus)와 작업기 버스(implement bus) 사이의 <strong>게이트웨이</strong> 역할을 하는 control function(CF)이며, 동시에 implement bus 위에서 "트랙터"라는 존재를 대표한다. 즉 작업기 쪽에서 보면 트랙터의 속도·히치·PTO 같은 정보는 전부 TECU라는 하나의 CF가 내보내는 메시지로 보인다.

이 문서는 2012년 발행된 2판(Second edition)으로, 2002년 초판을 기술적으로 개정한 것이다. 2판에서 새로 추가된 요구사항은 <strong>version 2 TECU</strong>라는 이름으로 구분된다. 문서 곳곳에 "TECU version 2 and later"라는 표기가 붙는 항목들이 이에 해당한다.

:::info TECU의 이중 역할
TECU는 단순한 프로토콜 변환기가 아니다. 두 가지 역할을 동시에 수행한다.

- <strong>게이트웨이/라우터</strong>: tractor bus의 메시지를 implement bus 형식으로 재포장(repackaging)하여 전달하고, 반대 방향도 처리한다
- <strong>트랙터의 대표 CF</strong>: implement bus에서 트랙터 자체를 나타내는 CF로 동작한다. 예를 들어 VT(Virtual Terminal)에 트랙터 성능 화면을 띄우는 것도 TECU가 여느 작업기 CF와 똑같은 방식으로 수행한다

자주식(self-propelled) 농기계에서도 트랙터에 해당하는 기능을 TECU가 담당한다.
:::

### 문서 구성

| 절 | 내용 |
| --- | --- |
| 1~3 | Scope, 인용 표준, 용어 정의 |
| 4.1 | Ports — TECU의 버스 포트 구성 |
| 4.2 | Functions and parameter repackaging — 메시지 중계 규칙 |
| 4.3 | Identity association — 트랙터 측 CF의 그룹화 |
| 4.4 | Classification — TECU 클래스(1/2/3)와 부가 분류(N/F/G/P/M), 최소 지원 메시지 |
| 4.5 | Control of lighting — 작업기 조명 제어 |
| 4.6 | Control of ECU_PWR and PWR — 작업기 전원 제어와 시스템 셧다운 |
| 4.7 | Safe-mode operation — 페일세이프 요구사항 |

### 인용 표준

Normative reference로 ISO 11783의 Part 1, 2, 4, 5, 6, 7, 8, 10과 함께 다음 두 표준이 등장한다.

- <strong>ISO 11786</strong>: 트랙터 장착 센서 인터페이스 — Class 1 TECU가 제공하는 기본 트랙터 측정값의 출처
- <strong>ISO 16154</strong>: 공로 주행용 조명·등화 장치 설치 — Class 2의 lighting 메시지 요구의 근거

참고로 ISO 11783 전체는 CAN(ISO 11898-1) 기반이며 SAE J1939와 공동 개발된 프로토콜 위에 서 있다.

## Ports (4.1)

TECU는 implement bus에 연결되는 포트를 최소 1개 가져야 한다. 트랙터에 tractor bus가 별도로 있는 경우에는 두 개의 포트를 가져야 하며, 포트 번호 참조 규칙이 고정되어 있다.

| 포트 | 용도 |
| --- | --- |
| Port 1 | implement bus 포트 |
| Port 2 | tractor bus 포트 (tractor bus가 설치된 경우) |

물리 계층 요구사항은 다음과 같다.

- <strong>Implement bus 포트</strong>: ISO 11783-2 물리 계층에 연결 가능하도록 설계해야 한다 (필수)
- <strong>Tractor bus 포트</strong>: 다른 물리 계층을 써도 되지만, ISO 11783 물리 계층 사용이 권장된다

트랙터 제조사가 내부 버스로 J1939 등 다른 규격을 쓰는 경우가 많기 때문에, tractor bus 쪽은 강제하지 않고 implement bus 쪽만 표준 물리 계층을 강제하는 구조다.

## Functions and Parameter Repackaging (4.2)

TECU는 implement bus에서 트랙터와 그 메시지를 대표하는 CF이므로, 트랙터와 implement bus 상의 다른 CF 간 통신을 책임진다. 이때 핵심 원칙은 <strong>TECU가 시스템에서 여느 CF와 똑같이 보여야 한다</strong>는 것이다. 특히 트랙터가 VT에 접근하는 방식은 다른 작업기의 VT 접근 방식과 동일해야 한다.

### Tractor bus → Implement bus

- TECU는 tractor bus 또는 직결 센서(ISO 11786에 규정된 센서 등)로부터 자기 classification에 해당하는 정보를 전부 수집한다
- 수집한 데이터를 implement bus용으로 규정된 메시지에 담아, <strong>TECU 자신의 source address(SA)</strong>로 재전송한다
- 요청받은 정보를 implement bus에 올릴 때는 <strong>global destination</strong> 사용이 권장된다. 같은 정보를 여러 CF가 요청하는 경우 대역폭을 아끼고, TECU의 필터 데이터베이스 부담도 줄이기 때문이다

:::tip Task Controller와의 중복 방지
표준 PG(Parameter Group)로 이미 송신 중인 데이터는 Process Data 메시지로 중복 전송하지 않는다. ISO 11783-10은 Task Controller가 PG를 직접 수신하는 방법을 허용하므로, TECU가 이미 표준 PG로 내보내는 데이터는 그 경로를 활용해야 한다. implement bus 대역폭을 아끼기 위한 규칙이다.
:::

### Implement bus → Tractor bus

- TECU는 트랙터 기능을 제어하도록 설계된 모든 메시지(process data 포함)를 classification에 맞게 implement bus로부터 수신한다
- 수신한 메시지를 트랙터 설계에 맞는 방식으로 해석(parse)한다
- 그 후 tractor bus 상에서 자신의 SA로, global 또는 특정 제어 대상 목적지로 재전송한다

### TECU → Implement bus (자체 발신)

TECU는 트랙터를 대표하여 implement bus 상에서 destination-specific 메시지를 직접 만들어 보낼 수도 있다. 대표적인 예가 VT에 트랙터 성능 화면을 올리는 경우다.

## Identity Association (4.3)

트랙터도 implement bus의 서비스(VT, Task Controller, management computer gateway 등)에 작업기 CF와 동일하게 접근할 수 있어야 한다. 이때 서비스 쪽이 implement bus용과 tractor bus용 네트워크 드라이버를 각각 둘 필요가 없도록, <strong>tractor bus 상의 CF들을 "tractor set"의 멤버로 그룹화하는 작업을 TECU가 담당한다</strong>. 이 그룹화 방식은 작업기 CF나 working set master가 CF를 그룹화하는 방식과 유사한 구조를 따라야 한다.

## Classification (4.4)

### 클래스 체계

트랙터 클래스는 <strong>TECU가 implement bus에 연결된 작업기 CF들에게 제공해야 하는 최소 메시지 집합</strong>을 정의한다. 숫자 클래스 1, 2, 3이 기본이고, 여기에 기능별 문자 addendum이 붙는다.

| 분류 | 이름 | 의미 |
| --- | --- | --- |
| Class 1 | 기본 측정 | ISO 11786 수준의 기본 트랙터 내부 측정값 제공 |
| Class 2 | 전체 측정 | 트랙터 측정 기능의 전체 집합 제공 |
| Class 3 | 명령 수용 | implement bus로부터의 제어 명령 수용 |
| xN | Navigational | GPS/DGPS 항법 메시지 제공 |
| xF | Front | 전방(또는 보조) 히치·PTO 메시지 제공 |
| xG | Guidance | 조향 시스템 상태·제어 (TECU version 2 이상) |
| xP | Powertrain | 속도/주행 전략 명령 수용 (TECU version 2 이상) |
| xM | Motion initiation | 차량 발진(전/후진) 명령 수용 (TECU version 2 이상) |

x는 클래스 번호이며, addendum은 복수로 붙을 수 있다. 예를 들어 <strong>class 3GP</strong>는 guidance와 powertrain 제어를 모두 지원하는 class 3 트랙터다.

클래스 판정과 관련된 규칙은 다음과 같다.

- 특정 클래스를 표방하려면 그 클래스까지의 <strong>세 클래스 전체 메시지를 모두 acknowledge</strong>할 수 있어야 한다
- 리어 히치나 PTO 같은 기능이 물리적으로 <strong>미장착</strong>인 경우에도 클래스는 유지할 수 있다. 이때 해당 파라미터는 "not available"로 응답한다
- 반대로 기능은 장착되어 있는데 메시지를 만들 데이터·제어 수단이 없다면, 장착된 기능이 아니라 <strong>실제로 제공 가능한 메시지 기준</strong>으로 클래스를 매긴다
- 제조사는 상위 클래스의 전체 메시지 집합을 채우지 않고도 추가 메시지를 개별 제공할 수 있다

### Version 2 TECU 공통 요구사항

다음 항목은 version 2 이상 TECU에 적용된다.

- 모든 클래스의 TECU는 <strong>ISOBUS compliance certification message</strong>(특히 TECU class 파라미터)를 지원해야 한다
- ISO 11783-7에 따라 전원 인가 시와 요청 시에 <strong>tractor facility response message</strong>를 송신해야 한다. 작업기 CF는 이 메시지로 TECU의 classification과 제공 기능(facility)을 파악한다
- facility response의 내용은 작업기가 요구한 기능이 아니라 <strong>실제 장착된 기능</strong> 기준이어야 한다
- 작업기 CF는 <strong>required tractor facilities message</strong>를 보내 필요한 기능의 메시지 송신을 활성화할 수 있다. 필요 없는 facility 비트를 0으로 내리면 TECU는 해당 메시지 송신을 중단해 대역폭을 아낄 수 있다
- 여러 작업기 CF로부터 required facilities 메시지를 받으면, TECU는 <strong>모든 요구를 합집합으로 반영한 하나의 facility response</strong>만 송신한다
- 작업기가 요구한 facility를 TECU가 지원하지 못하면, 작업기 CF가 운전자에게 누락 사실을 알릴 수 있다

### 복수 TECU 규칙 (version 2 이상)

TECU 기능은 VT 기능을 제공하는 디스플레이에 통합될 수도 있다. implement bus에 TECU가 여러 개 연결된 경우의 규칙은 다음과 같다.

| 규칙 | 내용 |
| --- | --- |
| Primary/Secondary | function instance 0이 primary TECU, function instance 1이 secondary TECU |
| Instance 0의 책임 | 전원 관리, 조명 제어, language command 응답은 instance 0이 담당 |
| 메시지 중복 금지 | 상위 instance TECU는 하위 instance TECU가 이미 제공하는 메시지를 제공해서는 안 된다 |
| 보완 제공 | instance 0이 아닌 TECU는 하위 instance TECU들에 facility response를 요청하고, 그들에게 <strong>없는</strong> facility 비트만 설정한다 |

이 구조 덕분에, 예를 들어 instance 0 TECU에 ground-based speed가 없을 때 GPS 수신기가 연결된 디스플레이 내장 TECU가 그 메시지를 대신 송신할 수 있다. 작업기 CF는 복수의 tractor facility response 메시지를 수신·처리할 수 있어야 한다.

### Class 1 — 기본 인터페이스

Class 1은 단순한 네트워크 지원 ECU가 ISO 11786의 기본 트랙터 내부 측정값을 제공하는 인터페이스다. 기존 센서를 간단한 네트워크 ECU에 연결하는 것만으로 ISO 적합성을 빠르게 확보할 수 있게 하려는 의도이지만, <strong>신규 트랙터 설계에는 사용하지 않아야 한다</strong>.

version 2부터는 전원 관리, 기본 언어, tractor facilities response가 최소 요구에 포함됐다. Class 1이 지원하는 파라미터는 다음과 같다(엔진 회전수는 ISO 11783-8, 나머지는 ISO 11783-7에 규정).

| 분류 | 파라미터 |
| --- | --- |
| Power management | key switch state, maximum time of tractor power, maintain power requests |
| Speed | wheel-based machine speed, ground-based machine speed, engine speed (송신 주기 100 ms) |
| Hitch | rear hitch position, rear hitch in-work indication |
| PTO | rear PTO output shaft speed, rear PTO engagement |
| Language | VT 초기화용 default language를 TECU에 저장 |
| Facilities | tractor facilities response (version 2 이상) |

### Class 2 — 전체 측정 인터페이스

Class 2는 트랙터 측정 기능의 전체 집합을 제공한다. Class 1 대비 주요 확장은 다음 네 가지다.

- ground/wheel 기반 주행 거리·방향
- rear draft(견인력) 정보
- lighting 메시지
- auxiliary valve의 추정/측정 유량

이로써 작업기가 더 정교한 제어·안전 전략을 구현할 수 있다. Class 2는 Class 1 메시지 전부에 더해 다음 파라미터를 지원한다(ISO 11783-7 규정).

| 분류 | 파라미터 |
| --- | --- |
| Time | time/date |
| Speed & distance | ground-based machine distance/direction, wheel-based machine distance/direction |
| Hitch 추가 | rear draft |
| Lighting | ISO 16154가 해당 지역에 요구하는 작업기·트랙터 조명 메시지 세트 (version 2 이상) |
| Auxiliary valve | estimated or measured flow |

### Class 3 — 명령 수용 인터페이스

Class 3은 <strong>implement bus에서 오는 명령을 수용하는 TECU</strong>를 다룬다. rear hitch, PTO, auxiliary valve에 대한 기본 명령을 처리해야 하며, 이를 통해 작업기가 트랙터의 동력원과 히치 위치를 제어할 수 있게 된다. 트랙터는 명령을 <strong>negative-acknowledge로 거부할 수도 있다</strong>.

Class 3은 Class 2 메시지 전부에 더해 다음을 지원한다(ISO 11783-7 규정).

| 분류 | 파라미터/명령 |
| --- | --- |
| Hitch 정보 | rear hitch position limit status, rear hitch exit/reason code (모두 version 2 이상) |
| Hitch 명령 | rear hitch position command |
| PTO 정보 | rear PTO engagement request status, rear PTO shaft speed limit status, rear PTO exit/reason code (모두 version 2 이상) |
| PTO 명령 | rear PTO output shaft speed set point command, rear PTO engagement command |
| Aux valve 정보 | auxiliary valve exit flow limit status, auxiliary valve exit/reason code (모두 version 2 이상) |
| Aux valve 명령 | auxiliary valve command |

:::tip limit status와 exit/reason code
version 2에서 추가된 limit status·exit/reason code 계열 파라미터는 "명령이 왜 그대로 수행되지 않았는가"를 작업기에게 알려주는 피드백 채널이다. 명령 수용형(Class 3) 인터페이스에서 트랙터가 명령을 제한하거나 종료한 이유를 작업기가 알 수 있게 하여, 상호 제어의 투명성을 높인다.
:::

### Addendum N — Navigational

트랙터에 GPS 또는 DGPS 수신기가 설치되어 ISO 11783-7의 항법 메시지 세트를 implement bus에 제공하는 경우 클래스 번호에 "N"을 붙인다. 예를 들어 항법 메시지를 지원하는 class 3 인터페이스는 <strong>class 3N</strong>이 되며, ISO 11783-7의 "Navigation location system messages"를 지원해야 한다.

### Addendum F — 전방/보조 작업기 지원

전방(front-mounted) 또는 보조(secondary) 히치·PTO가 설치되어 그 정보를 implement bus에 제공하는 경우 "F"를 붙인다. 예: front 메시지를 지원하는 class 2 인터페이스는 <strong>class 2F</strong>.

front 관련 파라미터의 지원 범위는 기본 클래스에 따라 계단식으로 늘어난다. <strong>front 명령 메시지는 class 3에서만 지원 가능</strong>하다.

| 기본 클래스 | front 파라미터 |
| --- | --- |
| Class 1 TECU | front hitch position, front hitch in-work indication, front PTO output shaft speed, front PTO engagement |
| Class 2 TECU | (추가) front draft |
| Class 3 TECU | (추가) front hitch position limit status·exit/reason code, front hitch position command, front PTO engagement request status·shaft speed limit status·exit/reason code, front PTO output shaft speed set point command, front PTO engagement command (limit status·exit/reason code 계열은 version 2 이상) |

### Addendum G — Guidance (version 2 이상)

트랙터에 조향(guidance/steering) 시스템이 설치되어 guidance 기능을 제공할 수 있으면 "G"를 붙인다. F와 달리 <strong>G는 기본 클래스(1/2/3)와 무관하게 붙을 수 있다</strong>. G를 붙인 트랙터는 guidance의 상태와 제어를 아우르는 파라미터 전부를 제공해야 한다. 예: guidance를 지원하는 class 2 인터페이스는 <strong>class 2G</strong>이며 조향 시스템의 외부 제어를 지원해야 한다.

guidance 분류에 사용하는 파라미터(ISO 11783-7):

- curvature command
- estimate curvature
- curvature command status
- request reset command status
- steering input position status
- steering system readiness
- mechanical system lockout

### Addendum P — Powertrain (version 2 이상)

작업기 컨트롤러로부터 속도 및/또는 주행 전략(drive strategy) 명령을 수용할 수 있으면 "P"를 붙인다. G와 마찬가지로 <strong>기본 클래스와 무관</strong>하다. P를 붙인 트랙터는 속도의 상태·제어를 아우르는 파라미터 전부를 제공해야 한다. 단, 주행 전략 제어와 정지(속도 0.0) 능력은 선택 사항이며, 작업기는 tractor facilities response message로 그 지원 여부를 확인할 수 있다.

powertrain 분류에 사용하는 파라미터(ISO 11783-7):

- machine selected speed
- machine selected direction
- machine selected speed limit status (version 2 이상)
- machine selected speed exit/reason code (version 2 이상)
- machine selected speed source
- machine selected speed set point command
- machine selected speed direction command

제어에 사용될 때 machine selected speed는 트랙터가 차속 제어에 실제로 쓰는 속도 소스여야 한다. 보통 wheel-based speed지만 다른 소스일 수도 있으며, <strong>제어 중 속도 소스가 바뀌는 경우 매끄러운 전환을 보장하는 것은 트랙터의 책임</strong>이다.

### Addendum M — Motion Initiation (version 2 이상)

차량의 발진(전진/후진) 명령을 수용할 수 있으면 "M"을 붙인다. 예: 발진 명령을 지원하는 class 3 인터페이스는 <strong>class 3M</strong>. 해당 메시지 세트는 ISO 11783-7에서 정의될 예정으로 기술되어 있다.

### 작업기 명령형 트랙터 — 제어 옵션 (4.4.3)

트랙터는 속도·토크·유량·압력·힘 등의 제어 변수에 대해, 전달 일관성을 높이거나 극대화하기 위한 <strong>추가 제어 모드</strong>를 제공할 수 있다(ISO 11783-7의 명령 사용). 제어 모드의 가용성은 트랙터 설계에 따라 다르며 tractor facilities message로 확인할 수 있다. 트랙터는 각 제어 모드의 제약을 스스로 판단하고, 적절한 경우에만 명령을 acknowledge해야 한다.

## Control of Lighting (4.5)

version 2 이상에서 <strong>function instance 0 TECU가 작업기 조명 제어를 책임진다</strong>. 제어 수단은 ISO 11783-7의 lighting command·lighting data 메시지와 ECU_PWR/PWR 제어(4.6)다.

동작 규칙은 다음과 같다.

- TECU는 조명 명령(운전자 조작 및 차량 시스템 내부 발생 모두)과 key switch 상태를 감시하고, 트랙터의 운용 지역 규정에 맞는 조명 운용 규칙을 적용한다
- 조명 명령은 tractor bus의 lighting 메시지 또는 TECU에 대한 운전자 입력으로 감시할 수 있다
- TECU는 implement bus에 필요한 전원이 켜져 있도록 보장하고, 적절한 lighting 메시지를 송신해야 한다

:::warning 통신 장애 시 경고등 폴백
implement bus나 트랙터의 고장으로 implement bus 통신 신뢰성이 훼손되면, TECU는 <strong>ECU_PWR을 차단하고 PWR을 경고등 점멸 주기로 on/off</strong>해야 한다. 조명 동기화가 되는 연결 장비는 이 방식으로 비상등(hazard lighting)을 제어한다. 즉 CAN 통신이 죽어도 전원선 자체를 점멸시켜 작업기의 황색 경고등을 깜빡이게 하는 하드웨어 수준의 폴백이 규정되어 있다.
:::

문서의 Figure 1은 이 경고등 제어 회로의 블록 다이어그램이다. 구성 요소는 CAN bus, twisted quad cable, 과부하 보호, double pole NC(normally closed) 릴레이, implement lighting ECU, 좌/우 amber warning light 등이다. NC 릴레이를 쓰기 때문에 ECU_PWR이 끊긴 상태에서 PWR 점멸이 그대로 경고등 점멸로 이어지는 구조다.

## Control of ECU_PWR and PWR (4.6)

implement bus 커넥터에는 두 계열의 전원이 있다. <strong>ECU_PWR</strong>은 ECU 전자회로용 전원, <strong>PWR</strong>은 액추에이터 등 부하용 전원이다. version 2 이상에서는 function instance 0 TECU가 두 전원의 분배 제어, 상태 메시지 송신, 제어 메시지 수신·처리를 책임진다.

### ECU_PWR (4.6.1)

- instance 0 TECU는 bus breakaway connector(ISO 11783-2)를 통해 작업기로 가는 ECU_PWR 분배를 제어하고, ECU_PWR 상태 메시지를 송신하며, ECU_PWR 제어 메시지를 수신·처리한다. 트랙터 내 다른 곳에서 ECU_PWR이 나오는 경우에도 마찬가지다
- TECU는 <strong>ECU_PWR을 켠 후에 address claim 메시지를 송신</strong>해야 한다
- VT처럼 트랙터에 장착되어 implement bus에 상시 연결된 ECU는 ECU_PWR에 연결하는 것이 좋다. bus extension connector로 연결된 트랙터 측 ECU를 ECU_PWR로 급전할지는 제조사/설치자가 결정한다
- implement bus의 종단 바이어스 회로 <strong>TBC_PWR은 ECU_PWR 또는 TECU 자체에서 급전</strong>해야 한다. ECU_PWR로 버스를 제어하는 ECU들이 있어도 종단 바이어스가 살아 있도록 하기 위함이다
- version 2 이상에서는 TBC_PWR과 ECU_PWR 연결부에 과부하 보호를 넣어 TBC_PWR이 TBC_RTN이나 ECU_GND로 단락되는 상황을 방어해야 한다

### PWR (4.6.2)

- TECU는 PWR에 대해서도 동일하게 분배 제어·상태 송신·제어 메시지 처리를 책임진다. PWR이 트랙터의 어디에서 나오든 무관하다

### 전류 용량 요구

| 항목 | 최소 용량 | 비고 |
| --- | --- | --- |
| implement bus 12 V ECU_PWR | 15 A | |
| implement bus 12 V PWR | 50 A | version 2에서 변경된 요구 |
| ECU_PWR + PWR 합산 | 연속 55 A | version 2에서 변경된 요구 |

### System Shutdown (4.6.4, version 2 이상)

<strong>System shutdown</strong>은 key switch 상태가 "off"를 가리킨 뒤에도 ECU_PWR이 최소 2초 이상 유지되는 기간이다. 이 동안 PWR은 ECU_PWR과 함께 유지될 수도, 안 될 수도 있다.

각 CF는 key switch 상태를 감시하다가 "Key switch not off" → "Key switch off" 전환을 보면 자신의 운용 요구에 따라 전원 차단 전 마무리 작업을 수행한다.

- 설정이나 로그 파일 저장만 필요하면 <strong>ECU_PWR만 유지 요청</strong>한다
- 밸브·액추에이터를 셧다운 상태로 만들어야 하면 <strong>ECU_PWR과 PWR 둘 다 유지 요청</strong>하여 액추에이터를 구동하고 네트워크에서 제어 메시지 통신을 계속한다

:::info 엔진 시동 시 전원 순단
엔진 시동은 예기치 않은 전원 순단을 일으킬 수 있다. 이런 순단 중에는 key switch state 파라미터의 송신과 ECU_PWR/PWR의 power maintain 기능이 억제될 수 있다.
:::

#### 데이터 저장이 필요한 CF (4.6.4.2)

key off 전환을 감지했고 저장에 2초 이상 걸리는 CF는 다음과 같이 동작한다.

1. "Maintain power" 메시지를 <strong>ECU_PWR 2초 추가 유지 요구</strong>와 함께 송신하여 TECU에 알린다
2. 저장이 끝날 때까지 이 메시지를 <strong>최소 1초에 1회</strong> 반복 송신한다
3. 저장 완료 후에는 송신을 멈추거나, ECU_PWR 유지 요구를 해제한 "Maintain power" 메시지를 보낸다

#### 밸브/액추에이터 셧다운이 필요한 CF (4.6.4.3)

밸브·액추에이터 셧다운에 2초 이상 걸리는 CF는 다음과 같이 동작한다.

1. "Maintain power" 메시지를 <strong>ECU_PWR 2초 추가 + PWR 2초 추가 유지 요구</strong>와 함께 송신한다
2. 셧다운이 끝날 때까지 최소 1초에 1회 반복 송신한다
3. 셧다운 완료 후에는 액추에이터 전원(PWR) 유지 요구를 해제한 메시지를 보낸다
4. 이후 저장할 데이터가 있으면 4.6.4.2의 절차로 넘어가고, 없으면 송신을 멈추거나 ECU_PWR·PWR 유지 요구를 모두 해제한 메시지를 보낸다

CF는 <strong>"Maximum time of tractor power"</strong> 파라미터를 함께 감시하여 셧다운을 끝낼 시간이 충분한지 판단해야 한다. 허용 시간 내에 셧다운을 못 끝낼 것 같으면, 다음 전원 인가 시 운전자에게 알려 적절한 조치(설정 확인, 밸브/액추에이터 상태 점검, 배터리 교체 등)를 하도록 권고된다.

#### 셧다운 메시지 시퀀스 (Figure 3~6)

문서의 Figure 3~6은 TECU와 전원 유지를 요청하는 ECU 사이의 메시지 시퀀스를 보여준다. 공통 흐름을 정리하면 다음과 같다.

| 단계 | TECU 동작 |
| --- | --- |
| Ignition On 중 | "Key switch not off"를 100 ms 주기로 송신 |
| Ignition Off 직후 | "Key switch off" + "Maximum time of tractor power 3 min"을 100 ms 주기로 송신 |
| 유지 요청 수신 중 | 요청 ECU가 "Request for 2 s more" 메시지를 2초 이내 간격으로 반복 송신하는 동안 전원 유지. 시간이 지나면서 Maximum time은 3 min → 2 min → … 으로 감소 |
| 종료 | 마지막 "Key switch off" 송신 후 100 ms 이내에 ECU_PWR·PWR 차단 |

각 Figure가 다루는 시나리오는 다음과 같다.

- <strong>Figure 3</strong>: 아무 CF도 전원 유지를 요청하지 않는 경우. key off 후 "Key switch off, Maximum time 3 min" 메시지를 2초 이상 송신한 뒤 마지막 메시지로부터 100 ms 이내에 ECU_PWR과 PWR을 끈다
- <strong>Figure 4</strong>: 요청 CF가 maximum time 안에 작업을 끝내는 경우. CF의 "2 s more" 요청이 이어지는 동안 유지하다가, 요청이 멈추면 ≥ 2 s 후 종료 절차로 들어간다
- <strong>Figure 5</strong>: 요청 CF가 maximum time 안에 못 끝내는 경우. Maximum time이 0 min까지 카운트다운되면 요청과 무관하게 ECU_PWR·PWR을 차단한다
- <strong>Figure 6</strong>: PWR을 먼저 끝내는 경우. CF가 "Done with PWR"을 알린 뒤 ECU_PWR만 계속 요청하면, TECU는 <strong>PWR을 먼저 끄고</strong> ECU_PWR은 요청이 끝난 뒤에 끈다

## Safe-mode Operation (4.7)

트랙터와의 전원 또는 통신이 끊기면 <strong>작업기는 페일세이프 상태로 들어가야 한다</strong>. 전원 공급의 중단·재개·변동이 어떤 형태로 일어나든 위험 상황을 초래해서는 안 되며, 제어 로직의 결함이나 제어 회로의 고장·손상도 위험으로 이어져서는 안 된다. 이를 보장하기 위한 구체 요구사항은 다음과 같다.

| 조항 | 요구사항 |
| --- | --- |
| 4.7.2 | 작업기가 예기치 않게 기동해서는 안 된다 |
| 4.7.3 | 정지 명령이 내려진 뒤 정지가 방해받아서는 안 된다 |
| 4.7.4 | 작업기의 어떤 부분도, 작업기가 붙잡고 있는 물체도 낙하하거나 튕겨 나가서는 안 된다 |
| 4.7.5 | 움직이는 부품의 자동·수동 정지가 저해되어서는 안 된다 |
| 4.7.6 | 보호 장치는 완전한 효력을 유지해야 한다 |
| 4.7.7 | 운전자가 원격 제어하는 작업기는, 감지 가능한 고장으로 원격 제어가 불가능해지면 자동으로 정지하도록 설계·제작해야 한다 |
| 4.7.8 | 운전자는 작업기가 제어하는 시스템을 오버라이드할 수 있어야 한다 |

:::tip Class 3와 안전
Safe-mode 요구는 특히 Class 3(작업기가 트랙터를 명령하는 구조)에서 중요하다. 작업기→트랙터 제어 경로가 열려 있는 만큼, 통신 두절이나 고장 시 시스템이 안전한 쪽으로 수렴하는 것과 운전자의 최종 오버라이드 권한이 표준 수준에서 못 박혀 있다.
:::

## Bibliography

- ISO 11898-1:2003 — CAN 데이터 링크 계층·물리 시그널링
- SAE J1939 — Serial Control and Communications Vehicle Network 권고 규격
