---
title: "표준 정리: Part 10 — Task controller"
description: "ISO 11783-10(Task controller and MICS data interchange) — Process Data, DDOP, ISOXML 스키마를 정리한 표준 요약이다."
date: 2026-08-21
tags: [ISOBUS, ISO11783, 표준정리]
---

# ISO 11783-10: Task controller and management information system data interchange 정리

::: info 이 문서에 대해
ISO 11783-10 표준 원문을 학습 목적으로 재구성한 <strong>비공식 요약·해설</strong>이다. 규범적 판단이 필요할 때는 반드시 원문 표준을 확인해야 한다.
:::

## 개요

ISO 11783-10(2015, 2nd edition)은 ISO 11783 시리즈 중 <strong>Task Controller(TC)</strong> 애플리케이션 계층을 정의하는 파트다. 농기계 네트워크(ISOBUS) 위에서 TC와 ECU(클라이언트) 사이의 통신 요구사항·서비스, 그리고 농장 관리 컴퓨터(FMIS)와 주고받는 데이터 형식(ISOXML)을 규정한다.

이 파트가 다루는 세 가지 축은 다음과 같다.

| 축 | 내용 |
|---|---|
| FMIS ↔ TC 데이터 교환 | XML 기반 데이터 전송 파일 세트(task data file set)의 구조와 스키마 |
| TC ↔ 클라이언트 통신 | ISO 11783 네트워크 위의 Process Data 메시지, 연결 관리, DDOP 업로드 |
| 제어·로깅 | 태스크 실행, setpoint 제어, DataLogTrigger 기반 데이터 수집 |

2015년판(2nd edition)은 2009년판을 대체하며, 프로토콜 버전 4를 정의한다. 버전 4에서 Data Logger(DL) 기능, Peer Control, 시간대 정보, Template/Canceled 태스크 상태 등이 추가되었다.

:::info 문서 구성
본문(1~8장)은 개념·요구사항·파일 구조를 다루고, 부속서가 실질 레퍼런스다. Annex A(Device descriptor objects), B(메시지 정의), C(XML 요소 관계도), D(XML 요소·속성 정의), E(사전 정의 첨부), F(TC 기능성·DDOP 정의), G(태스크 기반 시간 기록)는 모두 normative다.
:::

### 참조 표준

ISO 11783-1(일반), -3(데이터 링크), -5(네트워크 관리), -6(Virtual Terminal), -7(Implement 메시지), -11(데이터 사전), -12(진단), ISO 11898-1(CAN), ISO/IEC 10646(UCS)을 normative reference로 삼는다. 특히 Process Data의 의미 정의는 Part 11의 DDI(Data Dictionary Identifier)에 의존한다.

## 3장 용어 정의 (핵심만)

| 용어 | 정의 |
|---|---|
| client | TC 또는 DL과 연결을 맺고, 로깅 데이터를 제공하거나 제어 명령을 받는 CF(Control Function). 버전 4에서 working set 개념을 대체해 도입 — TC/DL과의 통신은 Working Set Master와만 이뤄진다 |
| coding data | 기계·자재 정보처럼 자주 바뀌지 않는 데이터, 또는 태스크 할당을 위해 참조되는 데이터 |
| data logger (DL) | 데이터 로깅 기능만 수행하도록 정의된 CF. TC 기능의 부분집합 |
| data transfer file set | FMIS와 TC 사이 데이터 전송에 쓰이는 XML + 바이너리 파일 모음 |
| DDOP (device descriptor object pool) | 장치의 기능·구조를 태스크 제어와 로깅 목적으로 기술하는 객체와 관계들의 집합 |
| device element | 장치에서 개별 주소 지정이 가능한 항목 (예: 붐 스프레이어의 개별 노즐) |
| field / partfield | field는 농장 관리 관점의 토지 단위(하나 이상의 partfield 집합). partfield는 단일 작물 재배 단위로, 태스크가 할당되는 최소 단위 XML 요소 |
| grid cell | partfield 위에 그리드를 덮어 만든 직사각형 셀 |
| polygon | 외곽 경계 1개 + 내부 경계 0개 이상으로 정의된 평면. 내부 경계는 구멍을 의미하며, treatment zone 정의에 사용 |
| process data variable | 프로세스 상태를 기술하는 값 요소. range·resolution·units 속성은 데이터 사전(Part 11)에 정의 |
| setpoint value source | 태스크 중 다른 CF가 쓸 setpoint 값을 결정할 수 있는 CF. property 속성이 "control source"인 Device Process Data 객체를 보유 |
| setpoint value user | TC나 다른 source로부터 setpoint를 받아 실시간 동작(예: rate control)을 조정하는 CF. property 속성이 "settable" |
| TC number | TC의 function instance에서 유도되는 식별 번호 |

## 5장 General description

### 5.1 태스크 관리의 목적과 워크플로우

모바일 임플리먼트 제어 시스템(MICS)에서 태스크 관리의 목적은 두 가지다.

1. <strong>농장 자원 관리</strong> — 트랙터·임플리먼트·센서·작업자·자재의 계획과 평가. 자원 지정자(resource designator)는 coding data로 전송된다.
2. <strong>농장 활동 관리</strong> — 밭에서 계획됐거나 실행 중이거나 완료된 작업을 태스크로 구분해 관리.

데이터는 양방향으로 흐른다. 계획된 태스크는 FMIS → TC로, 작업 결과는 TC → FMIS로 전송되며, 태스크는 FMIS와 MICS 양쪽에서 생성될 수 있다.

전체 워크플로우는 다음 순서다.

1. FMIS에서 필드 태스크 계획·coding data 관리
2. 태스크 데이터를 XML로 변환
3. (선택) 임플리먼트/센서에 필요한 데이터를 태스크에 할당
4. FMIS → MICS의 TC로 전송
5. TC가 태스크 데이터 기반으로 임플리먼트 ECU에 process data 메시지 송신
6. TC가 DataLogTrigger에 따라 데이터 수집
7. 수집 데이터를 FMIS로 전송 (proprietary 포맷이면 XML로 변환)
8. FMIS가 XML을 읽어 저장·평가

FMIS와 MICS 사이 인터페이스 중 표준화된 것은 <strong>XML 데이터 전송 파일</strong>과 <strong>ISO 11783 네트워크 내 통신</strong>뿐이며, TC 인터페이스 드라이버와 데이터 캐리어(메모리 카드, 무선 링크 등) 구간은 표준화 대상이 아니다.

### 5.2 FMIS에서의 태스크 관리

태스크는 "무엇을, 어디서, 어떻게, 누가, 언제" 작업할지를 지정한다. 전송 데이터 양은 농장의 관리 요구에 따라 달라진다. 단순 기록만 원하면 coding data만 FMIS → MICS로 보내고 태스크는 MICS에서 생성한다. FMIS에서 태스크를 계획하는 농장이라면 계획 태스크(자원 할당만 있는 것부터 위치 기반 site-specific 정보까지)가 함께 내려간다.

### 5.3 장치 사전 선택과 할당

클라이언트 장치는 <strong>CF NAME</strong>(8바이트)으로만 유일하게 식별된다. FMIS 관점에서 NAME은 전 세계적으로 유일해야 하며, 제조사는 Identity Number와 NAME의 나머지 필드 조합이 유일하도록 보장할 책임이 있다.

- DeviceAllocation XML 요소에 계획된 장치 할당을 담는다. 지정 수준은 구체적(특정 장치)부터 불명확(장치 유형만)까지 가능하다.
- <strong>ClientNAMEValue</strong> 속성은 CF NAME 8바이트를 담고, <strong>ClientNAMEMask</strong>는 NAME 중 장치 선택에 유효한 비트를 표시하는 비트마스크다(논리 AND로 매칭).
- 모바일 시스템에서 실제 사용된 장치는 <strong>DeviceIdRef</strong> 속성에 기록되며, FMIS가 설정한 사전 선택 정보는 덮어쓰지 않는다.

### 5.4 TC 인터페이스 드라이버

TC 제조사의 드라이버가 농장 컴퓨터에서 실행되어 데이터 전송 파일 세트를 TC로 옮긴다. 전송 방식(메모리 카드, 무선 등)과 파일 → 네트워크 메시지 변환 절차는 표준화 대상이 아니다. 드라이버는 제조사가 제공한 device descriptor 데이터를 추가해 임플리먼트별 setpoint 데이터를 만들 수 있다.

### 5.5 TC 사용자 인터페이스

TC는 VT(Virtual Terminal)나 다른 인터페이스로 사용자 상호작용을 제공할 수 있다. 단순 TC는 UI가 없을 수도 있고, 고급 TC는 태스크 목록 선택, start/stop/resume/complete, 태스크 수정·생성, coding data 추가 등을 제공한다.

### 5.6 Data logger 기능

버전 4에서 도입된 DL은 네트워크에 별도로 설치되는 로깅 전용 CF다(예: 텔레메트리 로거).

- DL은 TC 프로토콜을 재사용한다 — device descriptor와 process data 메시지로 데이터를 수집하고, 추가로 네트워크에 브로드캐스트되거나 요청 가능한 다른 parameter group 데이터도 로깅할 수 있다.
- DL 기능은 TC 기능의 부분집합이며 동일한 연결 메커니즘을 쓴다. TC의 클라이언트 제어 기능과 간섭하지 않는다.
- 태스크와 무관한 일반 로깅에도 사용 가능하며 텔레메트리 환경에 국한되지 않는다.
- ISO 11783-10 버전은 네트워크에서는 Version 메시지로, 파일에서는 ISO11783_TaskData 요소의 VersionMajor 속성으로 전달된다.

## 6장 Task controller 요구사항

### 6.1 태스크 선택과 실행

TC는 태스크 실행 메커니즘을 반드시 제공해야 하고(shall), 선택 메커니즘은 제공할 수 있다(can). 선택은 오퍼레이터가 하거나 TC가 자동으로 할 수 있으며, 방식은 표준화하지 않고 TC 설계자에게 맡긴다.

<strong>태스크 상태</strong>는 다음과 같다.

| 상태 | 의미 |
|---|---|
| Planned | FMIS 또는 MICS에서 준비됐으나 아직 MICS에서 처리되지 않음 |
| Running | MICS에서 처리 중. TC당 동시에 하나의 태스크만 active 가능 |
| Paused | 실행됐다가 중단된 상태(미완료). TC 관점에서는 최종 상태일 수 있음 |
| Completed | 오퍼레이터만 설정 가능(선택적 지원). MICS가 자동으로 설정할 수 없음 |
| Template | 템플릿 태스크. 시작하면 복사본이 새 태스크로 시작됨. FMIS가 정의한 템플릿은 MICS가 수정 금지, 템플릿에서 실체화된 후에도 원본 수정 금지 (버전 4 도입) |
| Canceled | 태스크 철회 신호용 상태. FMIS/MICS 상호 간 철회 통지에 사용 (버전 4 도입) |

Paused·Completed 상태의 MICS 발원 태스크는 FMIS가 처리해야 한다.

### 6.2 시간·위치 로깅

- <strong>AllocationStamp</strong>와 <strong>Time</strong> XML 요소가 여러 XML 요소에 날짜·시간을 부여한다. 타입은 planned/effective로 구분되고, Time 요소는 태스크 수준에서 preparation·ineffective·repair·clearing 같은 세부 시간 유형도 지원한다.
- 버전 3까지는 로컬 시간·날짜만 허용됐으나, 버전 4부터 시간대(time zone) 정보를 추가할 수 있다.
- Task 안에는 Time 요소가 여러 개 올 수 있다. Time 요소는 태스크 상태 변화, 자원 할당 변경, TC 기동/종료 시에만 추가하며, 이미 기록된 Time 요소는 수정하지 않는다.
- AllocationStamp·Time에는 GNSS 위치(Position) 요소를 최대 2개 포함할 수 있다 — 첫 번째는 생성 시점, 두 번째는 완료 시점 위치. 1개만 있으면 시작 위치를 의미한다.
- 다수의 process data 값 할당이 필요하면 Time 안에 DataLogValue를 여러 개 담을 수 있으나, 태스크 내부 저장은 totals나 단일 인스턴스 값으로 제한한다. 대량 로깅은 <strong>TimeLog</strong> XML 요소 + 바이너리 로그 파일을 쓴다.
- TimeLog 파일 정의 하나당 파일 2개가 생긴다: 바이너리 데이터(.bin)와 그 구조를 정의하는 XML 헤더(.xml). 파일명 프리픽스의 유일성은 TC가 보장한다.

### 6.3 Parameter group 값 로깅

ProcessDataVariable 외에 다른 parameter group의 값도 로깅할 수 있다.

- DataLogTrigger·DataLogValue의 (선택적) 속성으로 로깅 대상 parameter group을 지정하며, 이때 DataLogDDI 속성은 ParameterGroupNumberValue(DDI = DFFE<sub>16</sub>)로 설정한다.
- 한 parameter group에 값이 여러 개 있을 수 있으므로 PGN + CAN 데이터 필드의 start/stop 비트를 함께 지정한다. 값 크기는 최대 32비트다.
- ProcessDataVariable 외 parameter group 로깅 데이터에도 DeviceElement 참조가 필요하다. ClientNAME 속성을 채운 device와 DeviceElement 요소를 TC가 생성하거나 FMIS가 공급한다.

### 6.4 태스크 이벤트 로깅

Worker·Device·Product·Comment·Control 등 자원의 계획/실제 할당은 allocation XML 요소 패턴으로 기록한다 — WorkerAllocation, DeviceAllocation, ProductAllocation, CommentAllocation, GuidanceAllocation, ControlAssignment. 한 태스크 안에 같은 자원의 할당이 여러 번 나타날 수 있다(계획 할당이 실제가 되는 순간, 자원 재연결 등). 이미 기록된 할당은 수정하지 않고 새 할당을 추가한다.

### 6.5 언어·형식·측정 단위

VT의 로케일 설정과 TC/DL의 로케일이 다를 수 있으므로, 클라이언트는 TC/DL에 로케일을 질의해 device descriptor의 텍스트 속성과 DeviceValuePresentation(DVP)을 TC/DL의 언어·형식·단위에 맞춰야 한다.

TC/DL 요구사항(VT가 있는 네트워크):

- TC는 ISO 11783-7의 표준 언어·형식·단위 메시지("standard setup")를 송신해야 하며, 주 연결된 VT의 standard setup을 따른다. VT 연결 전(공장 초기 상태)에는 제조사 기본값을 쓴다.
- TC는 클라이언트 초기화 시와 변경 시마다 standard setup을 보고해야 한다. 클라이언트는 device descriptor 수정 규칙에 따라 텍스트·DVP를 갱신한다.
- TC는 standard setup을 비휘발성 저장소에 저장하고 초기화 시 복원한다. VT 연결 후에는 VT 설정을 따른다.
- TC는 global address로 온 "Language Command" 요청과 TC로 직접 온 요청 모두에 응답해야 한다(버전 4 도입).
- VT를 쓰지 않는 TC는 proprietary 설정 수단을 제공해야 한다.

클라이언트 요구사항: device descriptor를 게시하는 대상 TC의 setup을 따라야 하며(버전 4 도입 — 버전 3까지는 VT/T-ECU setup을 따랐다), 선택된 언어를 지원하지 않으면 자체 기본 언어를 쓴다.

### 6.6 연결 관리

전원 인가 후 TC와 클라이언트는 정해진 초기화 시퀀스를 따라야 한다.

#### 6.6.1 TC 초기화

1. ISO 11783-5에 따라 address claim을 완료하고, global 주소(255)로 address claimed 요청도 송신
2. address claim 완료 후 <strong>6초 대기</strong>
3. Task Controller Status 메시지 송신 시작
4. 클라이언트의 DDOP 업로드·초기화 허용
5. 클라이언트가 TC 버전을 요청한 뒤에는 TC도 클라이언트 버전을 요청해야 함(버전 4 도입)

#### 6.6.2 클라이언트 초기화

1. address claim 완료 후 6초 대기
2. 선택한 TC가 Task Controller Status 메시지를 송신할 때까지 대기
3. Working Set Master/Member 메시지(ISO 11783-7)로 자신을 Working Set Master로 식별. 버전 4부터 TC와의 통신은 Working Set Master(클라이언트 CF)로 한정
4. Client Task 메시지 송신 시작
5. 버전 4 이상 클라이언트는 Request Version 메시지로 TC 버전을 질의하고, TC가 요구 버전·기능을 지원하지 않으면 자신의 기능을 TC가 지원하는 수준으로 제한
6. 버전 4 이상 TC가 보내는 Request Version에 응답
7. (선택) TC에 언어·형식 메시지 요청
8. TC에 자신의 DDOP가 이미 있는지 질의
9. DDOP가 TC에 이미 있으면 활성화, 없으면 TP/ETP(ISO 11783-3)로 DDOP를 전송한 뒤 활성화

#### 6.6.3 연결 유지

| 항목 | 값 |
|---|---|
| Task Controller Status 주기 | 2 s (상태 변화 시 즉시 송신, 단 메시지 간 최소 200 ms — 최대 5 Hz) |
| Client Task 메시지 주기 | 2 s |
| 타임아웃 | 양방향 모두 6 s |

- 클라이언트가 TC Status를 6초간 못 받으면 TC의 비정상 종료로 간주하고 Client Task 메시지 송신을 중단한다. 초기화 절차를 다시 밟아 재연결할 수 있다.
- TC가 Client Task 메시지를 6초간 못 받으면 클라이언트의 비정상 종료로 간주한다. 클라이언트는 address claim 후 6초를 기다린 뒤에야 Client Task를 보내므로 TC가 클라이언트 재시작을 감지할 수 있다.
- 모든 시간 값(200 ms, 2 s, 6 s)은 구현에 사용해야 하는 값이며, 정확도는 AEF 시험 요구사항의 대상이다.
- 활성 태스크 중 클라이언트가 재시작·접속하면 TC는 DDOP 업로드·활성화를 수락하고 해당 클라이언트에 measurement 명령을 내려야 한다.
- Structure Label 응답에서 해당 ECU의 device descriptor가 TC에 없다고 확인되면 "Request Localization Label" 단계는 생략한다.

#### 6.6.4 연결 종료(shutdown)

시스템 셧다운은 Key Switch가 off이면서 ECU Power는 유지되는 구간으로 정의된다. Key off 시 CF들의 행동은 다양하다 — 즉시 통신을 끊는 CF도 있고, 정돈된 종료를 위해 전원 유지를 요청하는 CF도 있다. 아래 절차는 버전 4에서 도입되어 버전 4 호환 구현에는 필수다(버전 3 이하 구현은 경고 없이 통신을 끊을 수 있음을 감안해야 한다).

<strong>TC 셧다운 행동</strong> ("Key switch not Off" → "Key switch Off" 전이 시):

1. "예상치 못한 클라이언트 종료 감지 로직"을 비활성화한다 — 일부 클라이언트만 먼저 꺼질 때 불필요한 오퍼레이터 알림을 막기 위함
2. 활성 DDOP를 가진 클라이언트의 마지막 "Maintain Power" 요청 이후 <strong>최소 2초</strong>간 서비스를 유지한다 — 셧다운 중 수집 데이터의 정상 마무리를 보장
3. Key Switch 상태 감시를 계속하고, "Key Switch Off" → "Not Off"로 돌아오면 TC Status 송신을 중단한 뒤 표준 초기화 절차로 재초기화한다

참고로 버전 2는 셧다운 행동을 정의하지 않았고 버전 3은 필수 요구가 아니었으므로, 구버전 TC는 TC Status 중단을 포함해 모든 통신을 그냥 끊을 수 있다.

<strong>클라이언트 셧다운 행동</strong>:

1. "Maintain Power" 메시지(ISO 11783-7)를 송신해 자신의 상태를 알리고, 필요 시 ECU/Actuator Power 유지를 요청
2. "Maximum time of tractor power" 파라미터(Wheel-based speed and distance 메시지)를 감시해 전원 관리에 활용
3. TC에 <strong>Connection Deactivate</strong> 명령을 송신해 예기치 못한 종료로 인식되는 것을 방지
4. TC Status 메시지 중단을 TC의 비정상 종료로 간주하지 않으며, 다른 TC로 연결을 시도하지 않는다
5. Key Switch가 "Not Off"로 돌아오면 재초기화

<strong>전원 사이클 후 태스크 재개</strong>: TC는 전원 사이클 전의 태스크 상태를 복원해야 한다(shall). 데이터 로깅·위치 기반 제어가 전원 차단 전에 활성이었다면 자동 재개하거나 오퍼레이터의 확인을 받아야 한다. 자동 재개가 불가능한 구현은 태스크 기능이 활성 상태였음을 오퍼레이터에게 알리고 재활성화를 요청해야 한다. 제어 명령 실행의 허용/거부는 클라이언트 책임이다.

### 6.7 Task controller number

- 네트워크에 TC가 존재하면 <strong>function instance 0인 TC가 반드시 존재</strong>해야 한다. TC는 공장 출하 시 function instance 0으로 설정되며, 오퍼레이터가 설정한 값을 유지한다.
- TC는 function instance를 설정하는 proprietary 수단을 제공할 책임이 있으며, TC 간 중복 instance가 생기지 않도록 해야 한다. 새로 설정한 값은 네트워크 재접속 후에만 유효하다.
- function instance 0인 TC를 <strong>primary TC</strong>라 한다. 오퍼레이터에게는 <strong>TC number = function instance + 1</strong>(1~32)로 표시한다 — 0 기반 번호에 익숙하지 않은 오퍼레이터를 위한 오프셋이며, 모든 제조사가 일관된 번호 체계를 제공하게 한다.
- function instance > 0인 TC도 동일한 연결 절차(6.6)를 따른다.

<strong>다중 TC 네트워크에서의 클라이언트 초기화</strong> (6.7.1):

- 기본적으로 클라이언트는 function instance 0인 TC에 연결한다. "Move to another Task Controller" 기능(예: "Next Task Controller" 소프트키)이 있으면 다른 TC로 옮길 수 있다.
- 이 기능은 네트워크에 TC가 2개 이상 감지될 때만 활성화되며, 실행 시 클라이언트는 ① 안전 상태로 전환(또는 안전 상태가 아니면 실행 차단), ② Connection Deactivate 송신 후 응답 대기, ③ Client Task 메시지 중단, ④ 다른 TC와 초기화 시작 순으로 진행한다.
- 새 TC는 다음 전원 사이클의 preferred TC로 저장한다. 기동 후 일정 시간 내 preferred TC가 없으면 다른 TC에 연결할 수 있다. 대기 시간은 오퍼레이터 설정 또는 preferred TC의 Version 메시지에 있는 boot time 사양에서 얻는다.
- 클라이언트는 동시에 <strong>TC 1개, DL 1개</strong>에만 연결할 수 있다. 다중 TC·다중 DL 동시 연결은 이 판에서 허용되지 않는다.

### 6.8 네트워크에서의 데이터 교환

TC는 데이터 전송 파일 세트의 데이터를 process data 메시지로 변환해 장치를 제어한다. site-specific 애플리케이션에서는 클라이언트 요소의 위치를 애플리케이션 그리드에서 조회하고 그 클라이언트의 동작 지연(operation delay)과 결합해 적절한 데이터를 전송하는 스케줄링 계산을 수행한다. 반대 방향으로는 클라이언트가 보낸 process data를 태스크 데이터로 변환해 파일 세트에 되돌린다. <strong>TC 관련 네트워크 데이터 교환은 모두 process data 메시지 기반</strong>이다.

제어 관련 통신(예: 섹션 작업 상태)은 짧은 고정 주기보다 <strong>on-change 트리거를 기본으로 하고 긴 주기 트리거를 fallback</strong>으로 조합하는 것이 권장된다. 대역폭 낭비를 막고 요청·명령의 확인을 보장하기 위한 교환 규칙은 다음과 같다.

| 규칙 | 내용 |
|---|---|
| 대역폭 상한 | 클라이언트-TC 연결당, process data variable당 초당 최대 10개 메시지. 헤드랜드 진입/이탈 시 work state 제어처럼 짧은 burst가 필요한 경우는 일시적으로 초과 가능 — 해당 예외는 Setpoint/Actual Condensed Work State 등 ISO 11783-11 데이터 사전에 명시된 DDI에 한정 |
| 요청-응답 동기화 | TC가 보낸 요청은 클라이언트가 응답한 뒤에야 같은 클라이언트로 다음 요청 송신 가능(버전 4 도입 — 버전 3까지는 응답을 기다리지 않는 블록 요청 가능) |
| measurement 명령 ACK | TC의 모든 measurement 명령(Command 값 4~8)에 클라이언트는 PDACK로 응답해야 하며, 응답 전에는 같은 클라이언트로 다음 measurement 명령 불가. 수락 시 positive ACK + 측정 시작 시점의 초기값 전송(버전 4 도입 — 버전 3까지는 거부 시 negative ACK만 요구) |
| 재시도 | PGN 응답 시간·요청 재시도 대기는 ISO 11783-3을 따름. 클라이언트가 특정 measurement를 지원하지 않아 TC가 주기적 값 요청으로 폴백하는 경우에도 동일 |

추가 규칙:

- 클라이언트는 DDOP 활성화 전에 내부 process data variable을 올바른 운영값으로 초기화해야 한다 — DDOP 활성화 직후 TC가 장치 지오메트리를 요청해도 올바른 값을 받도록.
- TC는 태스크 파일에 없는 process data variable을 담은 메시지도 생성할 수 있으나(예: 센서 시스템 활용), <strong>클라이언트가 지원하는 variable만</strong> 송신·요청해야 한다.
- 클라이언트는 ① request value 명령, ② default data logging, ③ 개별 measurement 명령으로 요청된 값만 TC로 전송해야 한다.

<strong>"Task totals active" 비트와 measurement의 상호작용</strong>:

- 이 비트는 default data logging 명령 송신을 제외하면 Process Data 명령 송수신을 제한하지 않는다.
- 비트가 0일 때 TC가 시작한 measurement는 TC가 중지 명령으로 멈출 수 있으나, 비트를 0 → 1로 바꾸기 직전에 중지해서는 안 된다.
- 비트가 0↔1로 바뀌면 그 TC Status를 송신하는 CF가 지정한 모든 measurement는 클라이언트가 중지해야 하며, TC는 개별 measurement 명령 또는 default data logging 트리거로 재시작할 수 있다.
- 버전 3부터 태스크 비활성 중에도 TC가 measurement를 시작할 수 있다고 명시됐다(버전 2 이하 클라이언트는 지원 여부가 불확실).

#### 6.8.1 Site-specific 애플리케이션

위치 기반 제어에서는 태스크 데이터에 지오메트리를 정의해 실제 위치와 ProcessDataVariable을 매칭한다.

- 지오메트리는 <strong>gridcell</strong> 또는 <strong>polygon</strong>이며 유일한 식별자로 라벨링된다. 둘 다 site-specific 값이 연결된 <strong>TreatmentZone</strong>을 참조한다.
- 관련 DeviceElement가 새 TreatmentZone에 들어가면, 그 zone에 연결된 새 setpoint 값들이 네트워크로 해당 클라이언트에 전송된다.
- 겹치는 polygon이 있으면 TC는 항상 해당 위치의 <strong>외곽(exterior) polygon 정의를 사용</strong>한다. 내부 경계는 외곽 polygon의 구멍이다.

<strong>그리드 기반</strong> (6.8.1.1):

- Grid는 GridMaximumColumns/GridMaximumRows, GridMinimumNorthPosition/GridMinimumEastPosition, 셀 크기 속성으로 정의된다.
- 바이너리 파일 내 셀 순서: 원점(최소 북/동 위치)에서 시작해 <strong>열 오름차순(동쪽으로) → 행 오름차순(북쪽으로)</strong>, 각 행마다 최소 동 위치 열부터 다시 시작한다.
- 그리드 셀 정의는 별도 바이너리 파일에 저장되며 Grid XML 요소가 참조한다. <strong>태스크당 Grid 요소는 1개</strong>이고, 파일 세트 전체에서 유일한 프리픽스의 .bin(데이터) + .xml(헤더) 파일 쌍을 가리킨다. 그리드 파일명 유일성은 FMIS가 보장한다.

<strong>폴리곤 기반</strong> (6.8.1.2):

- TreatmentZone 지오메트리를 polygon으로도 정의할 수 있다. 태스크의 site-specific 작업(개별 자재, 개별 공간 가변 setpoint 타입)마다 별도의 polygon 세트를 정의한다 — 각 세트가 하나의 <strong>variable rate layer</strong>를 이룬다.
- TreatmentZone은 polygon을 여러 개 담을 수 있고, polygon으로 지오메트리를 정의한 TreatmentZone에는 <strong>ProcessDataVariable을 1개만</strong> 넣어야 한다. 결과적으로 한 레이어당 최대 하나의 variable rate가 지정된다.
- setpoint 전송 시 TC는 variable rate layer의 ProcessDataVariable에 setpoint device process data가 할당된 각 device element에 대해, 그 레이어의 TreatmentZone 중 어디에 위치하는지 판정한다.

#### 6.8.2 Data logging

- FMIS가 파일 세트에 지정한 DataLogTrigger를 TC가 process data measurement 명령으로 변환하고, 회신된 값을 로깅한다.
- 로깅용 measurement 명령은 태스크 시작·재개 후 송신되며, 태스크가 active인 동안 클라이언트가 값을 제공한다. 태스크가 일시정지되면 값 송신이 중지되고 measurement가 취소된다.
- 클라이언트가 요청보다 많은 데이터를 보내면 TC는 초과분을 무시해야 한다.

#### 6.8.3 Totals

totals는 두 종류로 나뉜다.

| 구분 | task total | lifetime total |
|---|---|---|
| TC의 제어 | 가능 — 태스크 시작 시 TC가 이어서 셀 시작값을 설정할 수 있음 | 불가 — 요청·저장만 가능 |
| DDOP 정의 | trigger method "total" + property "settable" 비트 설정 | trigger method "total" + settable 비트 = 0 |
| Start/Resume/Pause 영향 | 받음 | 받지 않음 — 갱신은 전적으로 클라이언트 소관 |

- total은 태스크 안의 Time XML 요소당 한 번씩 저장한다(태스크 재개 등으로 Time이 여러 개일 수 있음). TimeLog 데이터 로그 파일에는 더 자주 저장할 수도 있다.
- 태스크 재개 시 TC는 가장 최근 Time 요소에 저장된 task total을 클라이언트에 보내 이어 세게 한다. FMIS로 임포트되는 태스크의 최신 Time 요소는 그 태스크의 모든 total을 담고 있어야 한다.
- 클라이언트는 전원 인가 후 "Task totals active" 비트 = 1을 처음 수신하기 전까지 task total을 0으로 초기화해 둔다.

<strong>task total 처리 책임 (TC — DL은 선택적으로 동일 규칙 적용)</strong>:

1. 연결된 모든 클라이언트의 DDOP를 파싱해 전체 task total 내부 목록 구성
2. 태스크가 running → paused/completed로 바뀌면 모든 클라이언트에서 task total을 요청해 Time 요소에 저장
3. 태스크 재개 시 모든 클라이언트에 task total 복원
4. 예기치 못한 셧다운 대비, 정기적으로(예: 1분 간격) 모든 task total 요청. 시간·거리 간격 measurement 지원 권장
5. 최신 Time 요소에는 최근 실행 구간에 없던 클라이언트 것까지 포함해 그 태스크의 모든 task total 수록

태스크 이벤트별 클라이언트 행동: 시작 시 task total을 0으로 리셋, 일시정지 시 TC가 수집하고 값 유지, 재개 시 TC가 보낸 이전 값에서 이어서 카운트. "Task totals active" 비트 변경(0→1)을 알리는 TC Status는 total 설정 전에, (1→0)은 최종 total 요청 전에 송신해야 한다. task total은 TC가 관리하므로 클라이언트의 default data set에 넣지 않는 것이 권장된다.

<strong>lifetime total 처리</strong>: TC·DL 모두 요청·로깅 가능하며 책임은 task total과 유사하다(내부 목록 구성, 상태 변화 시 요청·저장, 정기 요청). lifetime total도 default data set에 넣지 않는 것이 권장된다.

#### 6.8.4 Data log triggers

- 로깅할 process data variable의 수·종류는 <strong>DataLogTrigger</strong> XML 요소가 지정한다. 어떤 device element에서 어떤 variable이 필요한지 정밀 지정이 가능하다.
- 대안으로 <strong>default data logging</strong> 메커니즘이 있다: RequestDefaultProcessData(DDI = DFFF<sub>16</sub>)라는 process data variable을 사용하며, 이때는 <strong>클라이언트가 스스로 정한</strong> 데이터·주기·트리거로 송신할 책임을 진다.
  - 용도: 클라이언트의 DeviceProcessData가 매우 많아 TC가 적절한 선택·주기를 모를 때, 또는 FMIS가 각 태스크에 DDI DFFF<sub>16</sub>을 추가해 로깅 활성화만 지시하고 싶을 때.
  - 태스크에 특정 DeviceProcessData용 트리거가 없으면 RequestDefaultProcessData DDI를 가진 DataLogTrigger를 넣는 것이 권장 관행이다 — 최소한 각 클라이언트의 default data set은 로깅되게 한다.
  - default data logging은 "Task totals active" 비트의 1 → 0 전이로만 중지되므로, 비트가 0일 때 TC는 request default data 명령을 쓰면 안 된다.
  - RequestDefaultProcessData는 장치의 <strong>device element 0</strong>에서만 요청할 수 있다. default set에 속하는 variable들은 DDOP에 지정되며, default set을 정의한 DDOP에는 DDI DFFF<sub>16</sub>의 DeviceProcessData 객체(ProcessDataTriggerMethod = 1F<sub>16</sub>)가 포함되어야 한다.

<strong>로깅 레코드 규칙</strong> (DDI별 송신 주기·지연이 제각각이므로):

1. 시간·위치 데이터는 TimeLog 인스턴스당 최대 1회 로깅
2. 각 process data variable 값도 TimeLog 인스턴스당 최대 1회 (TC 성능상 낮은 주기만 가능하면 어떤 값이 로깅될지는 TC 설계에 따름)
3. 갱신 주기가 가장 높은 DDI를 TC가 따라갈 수 있으면, 그 DDI 값이 도착할 때마다 새 레코드를 시작하고, 두 값 사이에 수신된 다른 값들은 현재 레코드에 기록
4. 수신 값은 최대 1회만 로깅. 다음 레코드에 새 값이 없으면 그 DDI는 기록하지 않음

여러 DDI를 묶어야 하면 <strong>Log Count(DDI = 0093<sub>16</sub>)</strong> process data variable을 가장 높은 반복률로 송신해 연관 값들의 로깅을 시간 태깅한다 — 그룹 전송 전에 항상 새 DataLog가 시작되므로 FMIS는 LogCount로 같은 그룹임을 판별할 수 있다.

#### 6.8.5 Peer Control

Peer Control은 <strong>임의의 CF가 다른 CF의 setpoint value source가 되도록</strong> TC가 할당을 제어·기록하는 메커니즘이다(버전 4 도입). 계획 시점에 결정할 수 없고 런타임에 정해지는 setpoint(예: on-the-go 센서 시스템의 직접 rate 결정, 계획 맵 rate의 수정)를 source·controller에 대한 사전 지식 없이 표준화된 방식으로 rate controller에 전달하는 요구를 해결한다.

- source와 user 모두 DDOP를 업로드·활성화한 TC 클라이언트여야 한다.
- setpoint value user의 DDOP에는 property가 <strong>"Settable"</strong>인 DPD 객체, source의 DDOP에는 property 비트 플래그가 <strong>"Setpoint Source"</strong>인 DPD 객체가 있어야 한다. 두 비트는 상호 배타적이다.
- source는 settable DPD도 함께 가질 수 있다 — <strong>Map Overlay</strong> 기능: TC가 보낸 위치 의존 setpoint를 source의 알고리즘이 수정해 최종 user로 전달할 값으로 쓴다.

<strong>할당(assignment) 절차</strong>:

- 버전 3까지 setpoint source는 variable rate map 레이어와 오퍼레이터 수동 설정뿐이었으나, 버전 4부터 control source property를 가진 임의 CF가 추가된다. DDI·객체 property의 할당 제한은 FMIS 계획 소스(TreatmentZone)든 외부 소스든 동일하게 적용된다.
- 할당 시 TC는 source와 user <strong>양쪽에 assignment 메시지</strong>를 보낸다. 각 클라이언트는 <strong>250 ms</strong> 안에 수락/거부로 응답해야 하며, 무응답은 (하위 호환을 위해) 거부로 간주한다.
- assignment 메시지는 Process Data 명령 메시지로, 연결 타입(settable/control source), Device Element, DDI, 상대 CF의 NAME을 지정한다. 새 address claim으로 SA가 바뀌면 추적 책임은 할당된 CF에 있다.
- 할당 후 source는 TC를 경유하지 않고 <strong>직접</strong> user에게 setpoint를 보낼 수 있고(지연·오버헤드 제거), user는 수신한 setpoint가 할당된 source에서 온 것인지 검증할 수 있다.

<strong>운영 규칙</strong>:

| 항목 | 값/규칙 |
|---|---|
| assignment 송신 시점 | 태스크 상태가 inactive → active로 바뀔 때마다 (device element별로) |
| setpoint 송신 주기 | 태스크 active 동안 1 Hz 주기 + on-change (최대 5 Hz) |
| setpoint 타임아웃 | 3 s 동안 미수신 시 target CF는 TC 통신 상실과 동일하게 대응 |
| TC 통신 상실 | source·user 모두 태스크 inactive처럼 동작 |
| 태스크 inactive | user는 setpoint 거부, source는 송신 중지, 양쪽 모두 할당 취소 |
| assignment 미수신/무효 | user는 태스크 active 동안 TC의 setpoint만 수용 (기본값) |

FMIS도 할당을 만들어 Task(TSK) 요소의 일부로 저장할 수 있다. FMIS 할당이 태스크 시작 시 가용하지 않으면 TC가 동일 규칙으로 할당할 수 있으며, TC가 만든 할당도 같은 방식으로 저장되어 이후 같은 태스크 시작에 재사용되고 FMIS가 참조할 수 있다. 저장에는 <strong>ControlAssignment(CAT)</strong> XML 요소를 쓴다.

## 7장 Data logger 요구사항

### 7.1 General

DL은 TC 클라이언트 제어 없이 태스크와 무관한 로깅을 수행하도록 네트워크에 설치되는 CF로, TC와는 별도의 function 정의(ISO 11783-1)로 구별된다. DL은 TC 기능의 부분집합만 쓴다 — 클라이언트 연결 메커니즘, DDOP 처리, process data 로깅은 TC와 동일하게 수행하되, 네트워크상 책임을 명확히 하기 위해 다음 제한이 있다.

<strong>DL이 해서는 안 되는 것</strong>: 섹션 제어, 위치 기반 제어, peer control 할당 설정(단 peer control CF가 DL에 연결해 로깅용 값을 공급하는 것은 가능), task total 외 DDI에 대한 set 명령 송신.

<strong>DL이 할 수 있는 것</strong>: 클라이언트로부터 process data 요청, measurement 명령 발행, default data logging 요청, parameter group 로깅 요청, TC Status의 "Task totals active" 비트로 task total 축적 제어(DL 클라이언트는 DL용 task total 세트를 별도로 유지).

### 7.2 연결 관리

- DL 클라이언트는 6.6.2와 동일한 방식으로 DL에 초기화하며 DDOP를 제공해야 한다. <strong>같은 클라이언트가 TC에 주는 DDOP와 DL에 주는 DDOP는 다를 수 있다</strong> — 목적별 최적화는 클라이언트 설계자 책임이다.
- 네트워크에 DL이 여러 개 있을 수 있으며 각각 유일한 function instance로 식별된다(설정은 proprietary 수단). TC와 달리 <strong>function instance 0인 DL에 특별한 역할이 없다</strong>. 클라이언트당 DL 연결은 최대 1개다.
- 가능한 네트워크 구성: ① TC + TC 클라이언트(버전 1부터), ② DL + DL 클라이언트(버전 4 도입), ③ TC + DL + TC/DL 클라이언트 — 양쪽 기능을 지원하는 CF는 TC와 DL에 동시 연결할 수 있다(버전 4 도입).

### 7.3 Measurements and totals

클라이언트가 TC와 DL에 동시에 연결하면:

- process data 값을 담은 DDOP를 DL에 올린 클라이언트는 DL용 <strong>활성 measurement 명령 세트를 별도로 유지</strong>해야 한다 — TC용과 DL용 measurement가 한 클라이언트 안에서 병렬로 동작한다.
- task total을 담은 DDOP를 DL에 올린 클라이언트는 <strong>DL용 task total 세트를 별도로 유지</strong>한다. TC용·DL용 세트가 각각 독립적으로 누적되고, 각 CF가 개별적으로 set/reset/trigger할 수 있으며 상호 간섭이 없어야 한다. DL이 task total을 자주 리셋하지 않더라도 이 메커니즘은 누적 시작점 지정과 최대값 도달 시 roll-over 방지에 유용하다.

## 8장 Data transfer

### 8.1 General

- FMIS ↔ MICS 통신은 데이터 전송 파일 기반이다. XML 파일은 XML 1.0, 텍스트 전용, <strong>UTF-8</strong>(ISO/IEC 10646) 인코딩이다.
- 그리드 셀 정의와 로깅 process data는 선택적으로 바이너리 파일로 포함될 수 있다. <strong>모든 파일은 같은 디렉터리</strong>에 있어야 한다.
- coding data와 task data는 같은 XML 파일 세트에 저장되며, TC 처리 중 수정될 수 있고 태스크 완료 후 FMIS로 반송된다.

### 8.2~8.3 XML과 스키마

- 데이터 전송 XML 파일에서 <strong>요소 안에 텍스트는 허용되지 않는다</strong> — 모든 정보는 속성으로 담는다. 메모리·대역폭 절약을 위해 요소명·속성명은 축약형을 쓴다(예: Worker → `<WKR A="WKR2" B="Miller"/>`).
- 태그·속성명은 대소문자를 구분하고, 속성값은 반드시 따옴표로 감싼다. 루트 요소는 <strong>ISO11783_TaskData</strong> 하나뿐이며, 그 자식으로 올 수 있는 primary 요소는 coding data 요소와 단일 태스크에 묶이지 않는 엔티티들이다.
- XML 파일은 항상 well formed(문법 준수)이면서 valid(스키마 검증 통과)해야 하며, 아니면 처리할 수 없다.

### 8.4 XML 스키마 정의

- 유효성은 <strong>ISO11783_TaskFile</strong> 스키마(W3C XMLSchema 기반, ISO 11783 전용 네임스페이스 없음)로 정의되며 isobus.net에 게시된다.
- 스키마 파일명 규칙: `ISO11783_TaskFile_V[VersionMajor]-[VersionMinor].xml` (예: 초판 = V2-0, 초판의 1차 개정 = V3-0). ISO11783_TaskData 요소의 VersionMajor/VersionMinor 속성값은 해당 스키마 파일에 고정값으로 설정된다. 구현자는 구버전 스키마와의 하위 호환을 유지할 책임이 있다.
- <strong>식별자 규칙</strong>: 모든 XML 요소는 엔티티이며, 식별자가 정의된 요소는 파일 세트 전체에서 유일한 식별자를 가져야 한다. 식별자는 네임스페이스 문자(요소 약어) + 최대 11자리 십진수(선행 0 없음), 최소 4바이트다. ID/IDREF 데이터 타입으로 참조하며, IDREF 속성은 단일 참조만 담는다.
  - 값 0과 −2147483648은 예약 — 사용 금지(0의 예약은 버전 3 도입).
  - MICS에서 coding data 요소는 변경·삭제 금지. non-coding data 요소는 편집 가능.
  - MICS(TC)에서 새로 생성된 엔티티는 <strong>음수 식별자</strong>(예: "WKR-1")를 써서 FMIS 제공 엔티티(양수)와 구별한다. 유일성 보장은 생성한 쪽(FMIS와 MICS 각각) 책임이다.

<strong>XML 요소 약어 목록</strong> (Table 2, †는 버전 4 도입, ○는 coding data):

| 약어 | 요소 | | 약어 | 요소 |
|---|---|---|---|---|
| ASP | AllocationStamp | | LSG | LineString |
| AFE† | AttachedFile ○ | | OTQ | OperationTechnique ○ |
| BSN† | BaseStation ○ | | OTR | OperationTechniqueReference ○ |
| CCT | CodedComment ○ | | OTP | OperTechPractice |
| CCG | CodedCommentGroup ○ | | PFD | Partfield ○ |
| CCL | CodedCommentListValue ○ | | PNT | Point |
| CLD | ColourLegend ○ | | PLN | Polygon |
| CRG | ColourRange ○ | | PTN | Position |
| CAN | CommentAllocation | | PDV | ProcessDataVariable |
| CNN | Connection | | PDT | Product ○ |
| CAT† | ControlAssignment | | PAN | ProductAllocation |
| CTP | CropType ○ | | PGP | ProductGroup ○ |
| CVT | CropVariety ○ | | PRN† | ProductRelation ○ |
| CPC | CulturalPractice ○ | | TSK | Task |
| CTR | Customer ○ | | TCC† | TaskControllerCapabilities |
| DLT | DataLogTrigger | | TIM | Time |
| DLV | DataLogValue | | TLG | TimeLog |
| DVC | Device ○ | | TZN | TreatmentZone |
| DAN | DeviceAllocation | | VPN | ValuePresentation ○ |
| DET | DeviceElement ○ | | WKR | Worker ○ |
| DOR | DeviceObjectReference ○ | | WAN | WorkerAllocation |
| DPD | DeviceProcessData ○ | | XFC | ExternalFileContents |
| DPT | DeviceProperty ○ | | XFR | ExternalFileReference |
| DVP | DeviceValuePresentation ○ | | FRM | Farm ○ |
| GRD | Grid | | GAN† | GuidanceAllocation |
| GGP† | GuidanceGroup ○ | | GPN† | GuidancePattern ○ |
| GST† | GuidanceShift | | | |

#### 8.4.1 Proprietary 스키마 확장

- 제조사 proprietary 요소·속성명은 `P` + 십진 제조사 코드 + `_` 프리픽스를 붙인다(예: 제조사 코드 500의 "MyElement" → `P500_MyElement`). 요소명·태그는 최대 16자, proprietary 속성의 데이터 길이는 최대 64자다.
- 다른 제조사의 MICS/FMIS는 proprietary 내용을 무시해야 하며, MICS는 반송 파일에서 이를 생략할 수 있다. 다중 제조사 환경에서 해석 불가하고 유실될 수 있으므로 proprietary 데이터는 최소화가 권장된다.
- 버전 4에서 도입된 AttachedFile(AFE) 요소로 proprietary 데이터를 표준 파일 세트에 연결된 별도 파일로 전송할 수 있다.

### 8.5 XML 데이터 전송 파일

- 루트 요소 ISO11783_TaskData를 담는 메인 파일명은 <strong>TASKDATA.XML</strong>이어야 한다. 이동식 저장 매체 사용 시 MICS는 루트 디렉터리의 <strong>TASKDATA</strong> 디렉터리에서 이 파일에 접근할 수 있어야 한다. 디렉터리명·파일명은 대문자이며 대소문자를 구분한다.
- 메인 파일은 coding data와 다수의 태스크를 담으며, <strong>XFR(ExternalFileReference)</strong> 요소로 다른 XML 파일을 참조할 수 있다. 참조는 중첩될 수 없다 — XFR은 메인 파일에만 올 수 있다. 참조된 외부 파일의 루트 요소는 <strong>XFC(ExternalFileContents)</strong>다.
- 참조된 외부 파일은 <strong>같은 타입의 최상위 요소만</strong> 담을 수 있다(예: customer 정의 파일에 partfield를 섞을 수 없음). 최상위 요소는 메인 파일과 외부 파일 양쪽에 정의될 수 있다.
- 모든 XML 파일은 `<?xml version="1.0" encoding="UTF-8"?>` 선언으로 시작해야 하며, 루트 파일의 모든 요소는 ISO11783_TaskData 루트 구조 안에 들어간다. 루트 요소의 주요 속성: VersionMajor, VersionMinor, TaskControllerManufacturer, TaskControllerVersion, ManagementSoftwareManufacturer, ManagementSoftwareVersion, DataTransferOrigin.

:::warning coding data 용량 한계
파일 세트 수신자는 <strong>요소 타입당 최소 2,000개, 전체 최소 20,000개</strong>의 coding data 요소를 지원해야 한다. 이 한계를 넘는 파일 세트는 처리되지 못할 위험이 있다. 이 제한은 coding data로 분류되지 않는 요소(예: 경계의 Point 개수 같은 지오메트리 요소)에는 적용되지 않는다.
:::

- XML 헤더의 방향 표시 속성(DataTransferOrigin: FMIS→MICS 또는 MICS→FMIS)은 FMIS와 MICS 모두 올바르게 갱신해야 한다.
- coding data 갱신에서 MICS는 <strong>새 인스턴스 추가만</strong> 허용된다 — FMIS coding data의 수정은 FMIS만 할 수 있다.
- TC(또는 TC 설정 프로그램)와 FMIS 모두 단일 파일이든 파일 세트든 수신할 준비가 되어 있어야 하며, 양쪽 다 바이너리 파일을 참조할 수 있다.

### 8.6 바이너리 데이터 전송 파일

파일 세트에 허용되는 바이너리 파일은 세 종류다: ① 그리드 셀 값, ② 로그 데이터(둘 다 태스크에 속함), ③ Point 지오메트리의 바이너리 인코딩(버전 4 도입).

#### 8.6.2 Grid 바이너리 파일 구조

그리드 셀은 바이너리 파일로만 정의할 수 있으며, 두 가지 타입이 있다.

| | Grid type 1 | Grid type 2 |
|---|---|---|
| 용도 | 제한된 수의 TreatmentZone이 정의되고 그리드가 zone 조회 테이블 역할 | ProcessDataValue가 소수의 TreatmentZone으로 분류되지 않는 경우(정밀 농업 맵) |
| 셀당 내용 | 그 셀이 속한 TreatmentZoneCode 1개 | 템플릿 TreatmentZone의 ProcessDataVariable 개수만큼의 값 |
| 바이너리 인코딩 | unsigned 8-bit integer | signed 32-bit integer (바이트 순서는 ISO 11783-6과 동일 규칙) |
| XML 측 정의 | Grid 요소의 TreatmentZoneIdRef가 비어 있음 | Grid 요소에 template TreatmentZoneCode 지정, 그 TreatmentZone의 PDV들은 ProcessDataValue 속성 값 없이 템플릿으로만 정의 |

type 2에서 바이너리 레코드 하나는 셀 하나에 해당하며, 템플릿 TreatmentZone에 정의된 PDV 순서대로 값들이 이어진다. 예를 들어 PDV 3개를 가진 템플릿이면 각 셀 레코드는 32-bit 값 3개다.

#### 8.6.3 Log data 바이너리 파일 구조

TimeLog XML 요소가 바이너리 로그 파일을 참조한다. 태스크 파일 안의 TimeLog 요소는 Time·Position·DataLogValue를 직접 담지 않고, <strong>XML 헤더 파일(.xml) + 바이너리 로그 파일(.bin)</strong> 두 파일을 가리킨다.

- 헤더 파일 안의 요소들은 속성으로 레코드 구조를 정의한다: <strong>값이 비어 있는 속성("")은 바이너리 파일에 기록되는 필드</strong>, 값이 채워진 속성은 모든 레코드에 공통인 고정값이다.
- 헤더에서 빈 값 속성의 나열 순서는 자유지만, 바이너리 파일 내 값 순서는 Table 3에 정의된 순서를 따라야 하며, Table 3에 없는 속성은 바이너리 파일에 쓸 수 없다.
- 버전 4의 시간대 정보 도입과 무관하게 바이너리 로그 파일의 TimeStart는 계속 <strong>로컬 시간</strong>으로 표기한다.

<strong>Table 3 — 바이너리 레코드 값 정의</strong> (기록 순서대로):

| 값 | XML 참조 | 타입 | N/A 값 | 정의 |
|---|---|---|---|---|
| TimeStart (time of day) | TIM, A | unsigned 32-bit | FFFFFFFF<sub>16</sub> | 자정 이후 밀리초 (로컬 시간) |
| TimeStart (date) | TIM, A | unsigned 16-bit | FFFF<sub>16</sub> | 1980-01-01 이후 일수 (로컬) |
| PositionNorth | PTN, A | 32-bit int | FFFFFFFF<sub>16</sub> | 10⁻⁷ deg, WGS-84 |
| PositionEast | PTN, B | 32-bit int | FFFFFFFF<sub>16</sub> | 10⁻⁷ deg, WGS-84 |
| PositionUp | PTN, C | 32-bit int | FFFFFFFF<sub>16</sub> | WGS-84 타원체 기준 mm |
| PositionStatus | PTN, D | byte | FF<sub>16</sub> | 0=no GPS fix, 1=GNSS, 2=DGNSS, 3=Precise GNSS, 4=RTK Fixed, 5=RTK Float, 6=Est(DR), 7=Manual, 8=Simulate, 9~13=Reserved, 14=Error, 15=N/A (NMEA2000 MethodGNSS 참조) |
| PDOP | PTN, E | unsigned 16-bit | FFFF<sub>16</sub> | 10⁻¹ 단위 |
| HDOP | PTN, F | unsigned 16-bit | FFFF<sub>16</sub> | 10⁻¹ 단위 |
| NumberOfSatellites | PTN, G | byte | FF<sub>16</sub> | 사용 위성 수 |
| GpsUtcTime | PTN, H | unsigned 32-bit | FFFFFFFF<sub>16</sub> | 자정 이후 UTC 밀리초 |
| GpsUtcDate | PTN, I | unsigned 16-bit | FFFF<sub>16</sub> | 1980-01-01 이후 UTC 일수 |
| #DLV | — | byte | n.a. | 뒤따르는 PDV 개수 |
| DLVn | — | byte | n.a. | 뒤따르는 PDV의 정의 순서 번호(0부터) |
| ProcessDataValue | DLV, B | 32-bit int | n.a. | DDI에 따른 값 |

DLV들은 헤더 정의 순서로 인덱싱되고, 바이너리 레코드에서는 #DLV(실제 저장 개수) + (DLVn, 값) 쌍의 나열로 동적 세트를 표현한다. 한 time 엔트리에 최대 <strong>255개 PDV</strong>가 올 수 있다.

#### 8.6.4 Point data 바이너리 파일 구조

Point 요소들의 나열을 XML 대신 바이너리로 전송할 수 있다(버전 4 도입). 바이너리 포맷에서는 Position North/East가 <strong>64-bit integer</strong>로 지정되어 더 높은 정밀도를 쓸 수 있다. 헤더 정의 방식은 TimeLog와 동일하다 — 빈 값 속성이 바이너리 필드, 채워진 속성은 전 레코드 공통 고정값.

<strong>Table 4 — 바이너리 Point 레코드 값 정의</strong> (기록 순서대로):

| 값 | XML 참조 | 타입 | N/A 값 | 정의 |
|---|---|---|---|---|
| PointType | PNT, A | unsigned 8-bit | FF<sub>16</sub> | PointType 열거값 |
| PositionNorth | PNT, C | 64-bit int | FFFFFFFFFFFFFFFF<sub>16</sub> | 10⁻¹⁶ deg, WGS-84 |
| PositionEast | PNT, D | 64-bit int | FFFFFFFFFFFFFFFF<sub>16</sub> | 10⁻¹⁶ deg, WGS-84 |
| PositionUp | PNT, E | 32-bit int | FFFFFFFF<sub>16</sub> | WGS-84 타원체 기준 mm |
| PointColour | PNT, F | unsigned 8-bit | FF<sub>16</sub> | ISO 11783-6 팔레트 방식 |
| PointHorizontalAccuracy | PNT, H | unsigned 16-bit | FFFF<sub>16</sub> | RMS 오차 (mm) |
| PointVerticalAccuracy | PNT, I | unsigned 16-bit | FFFF<sub>16</sub> | RMS 오차 (mm) |

### 8.7 Device descriptor object pool

DDOP은 MICS와 FMIS 양쪽에서 장치 속성을 지정하기 위한 것이다. 제조사가 XML 정의 세트로 공급해 FMIS에 임포트할 수 있고, FMIS가 알게 된 DDOP은 태스크 계획에 쓰이며 FMIS → MICS 파일 세트에 포함될 수 있다.

- 별도 파일이라면 XML 선언으로 시작하고 파일 세트 스키마의 device 정의를 따른다. device descriptor 파일은 태스크에서 그 장치를 쓸 때 필요한 모든 정보를 담아야 한다 — 예: 스프레이어라면 섹션/노즐 지오메트리, 탱크 수·용량, 지원 process data variable. 이는 DeviceElement, DeviceProperty, DeviceProcessData 요소로 지정한다.
- DeviceElement의 첫 요소는 장치 자체를 나타내며 <strong>ElementNumber = 0</strong>, ParentIdRef는 device 요소를 가리킨다. 나머지 (하위)요소의 ParentIdRef는 계층 구조를 만들기 위해 다른 DeviceElement를, 계층상 하위 위치가 없는 요소는 device를 직접 가리킨다.
- MICS의 장치에서 유래한 device descriptor는 Annex B의 process data 명령으로 네트워크를 통해 TC로 전송된다. TC는 태스크 실행 가능 여부 판단을 위해 이를 수신할 수 있어야 하며, FMIS로 반송하기 위해 저장도 해야 한다.

<strong>네트워크를 통한 DDOP 전송 절차</strong>:

1. 클라이언트가 request object-pool transfer 메시지로 TC의 가용 메모리를 확인 → TC가 response로 상태 코드 회신 → 메모리 충분 시 진행
2. TP 또는 ETP(ISO 11783-3)로 객체 전송 — 표준 핸드셰이킹·오류 검사·재전송 적용
3. 완료 후 클라이언트가 object-pool activate 메시지 송신
4. TC가 object-pool activate response로 응답

<strong>런타임 갱신</strong>: 클라이언트는 런타임에 DDOP을 갱신할 수 있으나 <strong>언어·측정 단위 관련 변경으로 한정</strong>된다(오퍼레이터가 선택한 언어·단위 포맷 반영 목적). 갱신 시점 제한은 없으나 태스크 active 중에는 가급적 피해야 한다. 갱신에는 device 객체(structure label은 유지, localization label만 갱신)와 DeviceValuePresentation 타입 객체만 포함할 수 있다. designator는 change designator 명령으로 갱신할 수 있다.

그 외의 변경은 <strong>완전한 DDOP 재전송</strong>으로 해야 한다: ① de-activate object pool 메시지 송신, ② 초기화 때와 같은 절차로 전체 pool 전송(device 객체에 갱신된 structure label 포함). structure label은 device element·property 값·process data variable의 집합을 유일하게 식별한다. 갱신 중 오류가 나면 TC는 object-pool activate response에 오류를 표시하고 <strong>갱신 이전 것까지 포함해 pool 전체를 휘발성 메모리에서 삭제</strong>하며, 알람류 방식으로 오퍼레이터에게 알릴 수 있다.

<strong>장치 지오메트리</strong>:

- 장치마다 좌표계가 있고 중심은 <strong>DeviceReferencePoint(DRP)</strong> = (0,0,0)이다. DeviceElement의 위치는 DRP 기준 상대 좌표이며 오른손 좌표계다: x축 = 주행 방향 양수, y축 = 주행 방향 기준 우측 양수, z축 = 지면 방향(아래) 양수.
- DRP는 트랙터는 뒷차축 중심, 바퀴 달린 임플리먼트는 앞차축 중심이다. 그 외에는 자유롭게 선택 가능(DRP = CRP 또는 DRP = ERP 등). 지오메트리에 각도가 생기면 장치 CF가 새 DRP/CRP를 재계산해 동적 데이터로 TC에 보내야 한다.
- <strong>CRP(ConnectorReferencePoint)</strong>: 장착부 위치(전·후방 3점 히치, 드로우바 등). 3점 히치의 CRP는 하부 링크 점들의 중심. 장치당 커넥터 여러 개 가능. 동적 변화(조향 차축 등) 시 장치가 새 CRP를 계산해 TC로 송신.
- <strong>ERP(DeviceElementReferencePoint)</strong>: device element(들)의 중심(예: 붐 중심). <strong>NRP(NavigationReferencePoint)</strong>: GPS 수신기 등 내비게이션 장치의 기준 위치. 트랙터가 NRP를 보고하지 않는데 TC가 필요로 하면 TC가 오프셋 지정 대체 수단을 제공할 수 있다.
- element 오프셋·시간 지연·용량 등 파라미터는 DeviceProperty(정적 — 변경하려면 새 descriptor 업로드 필요) 또는 DeviceProcessData(동적 — 연결 중·태스크 중 변경 가능)로 정의하고 DeviceElement가 참조한다. <strong>같은 DDI를 한 element에 DeviceProperty와 DeviceProcessData 양쪽으로 넣는 것은 금지</strong>다.
- TC·DL·FMIS에 이미 저장된 descriptor·로그 데이터와의 충돌을 피하기 위해, structure label이 요소·객체 번호 체계를 포함한 관계를 영구적으로 유일하게 기술하도록 하는 것은 클라이언트 책임이다.

임플리먼트·센서 시스템·트랙터를 구분하지 않고 동일한 기술 방식을 쓴다 — GPS 수신기를 단 센서 시스템이나 고정 DeviceElement를 가진 트랙터에도 그대로 적용된다.

## Annex A (normative) — Device descriptor objects

### A.1 General

Device는 "Device" 요소 1개 + "DeviceElement" 1개 이상 + 선택적 DeviceProcessData/DeviceProperty/ValuePresentation으로 정의된다. 이들을 ISO 11783-6의 object pool과 유사한 <strong>객체</strong>로 정의함으로써 장치 관련 데이터 전부를 TP/ETP로 TC에 전송할 수 있다. 이 부속서는 device descriptor XML 요소의 바이너리 객체 표현을 정의한다.

- 문자열 속성은 BOM 없는 UTF-8이며, 문자당 최대 4바이트 — 바이트 배열 최대 길이는 XML 정의 문자 수의 4배다.
- 객체 ID는 DDOP 전체에서 유일해야 한다. 참조가 없을 때는 NULL Object ID = 65535(FFFF<sub>16</sub>)를 쓴다.
- TC는 수신한 객체 정의를 XML 요소로 변환해 파일 세트에 저장한다. 현재 태스크 파일에 없는 장치면 추가하고, 같은 장치가 이미 있으면 structure label을 비교해 갱신 또는 새 device 요소로 저장한다.

### A.2 DeviceObject (Table ID "DVC", Object ID = 0)

DDOP당 정확히 1개. 주요 속성:

| 속성 | 타입/크기 | 설명 |
|---|---|---|
| Device designator | UTF-8 0~128바이트 | 오퍼레이터에게 표시 가능한 장치 식별 텍스트 (최대 32자) |
| Device software version | UTF-8 0~128바이트 | 소프트웨어 버전 (최대 32자) |
| ClientNAME | 8바이트 | 클라이언트 장치의 NAME(ISO 11783-5 구조). <strong>CF의 address claim과 동일해야 함</strong> |
| DeviceSerialNumber | UTF-8 0~128바이트 | 장치·제조사별 시리얼 번호 (최대 32자) |
| Device structure label | 7바이트 배열 | descriptor 구조 버전 식별 라벨 — TC에 있는 pool의 갱신 필요 여부 판단용. 내용은 제조사 정의 |
| Device localization label | 7바이트 배열 | 로컬라이제이션 식별. 바이트 1~6은 language command PGN(ISO 11783-7) 정의, 바이트 7은 예약(FF<sub>16</sub>) |
| Extended Structure Label | 0~32바이트 | structure label의 연장(버전 4 도입) |

- 버전 4에서 designator류 속성의 값 범위가 32 → 128바이트로 확장됐다.
- Extended structure label 관련 2개 속성은 <strong>TC와 클라이언트 모두 버전 4 이상일 때만</strong> 사용한다. 한쪽이 버전 3 이하면 최저 공통 버전으로 폴백하고 이 속성들을 쓰지 않는다. 버전 4 이상이면서 확장 라벨을 쓰지 않는 클라이언트는 바이트 수를 0으로 보고한다.

### A.3 DeviceElementObject (Table ID "DET", Object ID 1~65534)

속성: DeviceElementType(1바이트), designator, <strong>DeviceElementNumber</strong>(2바이트, 0~4095 — process data variable 주소 지정용), <strong>Parent ObjectId</strong>(부모 DeviceElement 또는 DeviceObject의 ID — 계층 구성), 뒤따르는 객체 참조 수 + DeviceProcessData/DeviceProperty 객체 ID 목록.

<strong>DeviceElementType</strong>:

| 값 | 타입 | 용도 |
|---|---|---|
| 1 | device | 장치 전체. DDOP당 1개, element number = 0 |
| 2 | function | 밸브·센서처럼 개별 접근 가능한 구성요소를 정의하는 범용 타입. 기능은 process data·property 목록으로 결정 |
| 3 | bin | 스프레이어 탱크, 시더의 빈 등 용기 |
| 4 | section | 붐 섹션, 시드 툴바 섹션 등. 지오메트리(x, y, z)와 작업 폭을 제공할 수 있음 |
| 5 | unit | 섹션 아래 계층 — 노즐, 시더 오프너, 플랜터 로우 유닛 등 가장 세분화된 주소 지정 수준 |
| 6 | connector | 장착·연결 위치. 장치당 여러 개 가능(전·후방). DRP와 같은 위치(x=y=z=0)여도 지오메트리를 process data 값 또는 property 값으로 제공해야 함 |
| 7 | navigation reference | GPS 수신기 등 내비게이션 기준 위치. x·y·z 위치를 process data 값 또는 property 값으로 참조해야 함 |

### A.4 DeviceProcessDataObject (Table ID "DPD", Object ID 1~65534)

XML 요소 DeviceProcessData의 객체 정의. 객체 하나가 process data variable 정의 1개를 담는다.

| 속성 | 설명 |
|---|---|
| Process data DDI | 2바이트, ISO 11783-11 및 Annex B 정의 |
| Process data properties | 비트셋: bit 1 = default set 멤버, bit 2 = settable, bit 3 = control source(버전 4 도입). bit 2와 3은 상호 배타 |
| Process data available trigger methods | 비트셋: bit 1 = time interval, bit 2 = distance interval, bit 3 = threshold limits, bit 4 = on change, bit 5 = total |
| designator | UTF-8 (최대 32자) |
| Device value presentation object ID | 참조 없으면 NULL object ID |

trigger method의 의미: time interval(시간 간격 기반 제공), distance interval(거리 간격), threshold limits(임계값 초과 시), on change(값 변경 시), total(누적값 — 6.8.3 참조).

### A.5 DevicePropertyObject (Table ID "DPT", Object ID 1~65534)

DeviceProperty의 객체 정의. 속성: Property DDI(2바이트), <strong>Property value</strong>(signed 4바이트, −2³¹~2³¹−1), designator, Device value presentation object ID.

### A.6 DeviceValuePresentationObject (Table ID "DVP", Object ID 1~65534)

DeviceProcessData/DeviceProperty 값의 표시 정보를 담는다. 언어·단위 변경 시 장치가 갱신할 수 있다.

| 속성 | 타입 | 설명 |
|---|---|---|
| Offset | signed 4바이트 | 표시용 값에 더할 오프셋 |
| Scale | float 4바이트 (0.000000001~100000000.0) | 표시용 배율 |
| Number of decimals | 1바이트 (0~7) | 소수점 이하 자릿수 |
| UnitDesignator | UTF-8 (최대 32자) | 단위 표기 |

### A.7 객체 계층

DDOP은 <strong>DeviceObject 정확히 1개</strong> + 다수의 DeviceElement/DeviceProcessData/DeviceProperty/DeviceValuePresentation 객체로 구성된다. DeviceProcessData·DeviceProperty 객체는 여러 DeviceElement에서 참조될 수 있고, DeviceValuePresentation 객체는 여러 DeviceProcessData/DeviceProperty에서 참조될 수 있다. DeviceElement는 DeviceObject(또는 부모 DeviceElement)를 참조한다.

## Annex B (normative) — Message definitions

### B.1~B.2 Process Data 메시지 개요

Process Data 메시지는 device descriptor 데이터, 측정 데이터, setpoint 명령의 전송에 쓰인다. <strong>첫 바이트의 첫 니블(bits 4~1)이 command</strong>를 식별하며, command 0<sub>16</sub>·1<sub>16</sub>은 나머지 command(2<sub>16</sub>~A<sub>16</sub>, D<sub>16</sub>~F<sub>16</sub>)와 메시지 구조가 다르다.

- Process Data 메시지는 "Task totals active" 비트 값과 무관하게 네트워크에 전송될 수 있으며, TC/DL-클라이언트 통신 범위 밖에서도 나타날 수 있다.
- proprietary DDI 값 범위를 참조하는 경우에도 메시지 포맷은 이 부속서의 정의를 따라야 한다.
- Process Data 요청·measurement 명령은 응답을 받은 뒤에야 다음 요청·명령을 보낼 수 있다(버전 4 도입 동기화).

<strong>Parameter group 정의</strong>:

| 항목 | 값 |
|---|---|
| PGN | 51968 (00CB00<sub>16</sub>) |
| Data page / Extended data page | 0 / 0 |
| PDU format | 203, PDU specific = destination address |
| 기본 우선순위 | 3 (command 3·A·E·F<sub>16</sub>), 4 (D<sub>16</sub>), 5 (0·1·2·4~9<sub>16</sub>) |
| 데이터 길이 | 가변, 최소 8바이트 |

우선순위 3단계 구분은 버전 4에서 도입됐다(버전 3까지는 모두 3) — ISO 11783-3의 우선순위 권고에 맞춰 제어·연결 유지 메시지를 요청·ACK 메시지보다 높게 둔다. global destination으로 보낼 수 있으나, 컨트롤러는 자신에게 주소 지정된 것으로 판단된 메시지만 처리해야 한다.

<strong>단일 TC는 네트워크에서 단일 CF로 표현</strong>되어야 하며, 모든 TC 통신은 working set master로 식별된 클라이언트와 TC 서버 사이에서 이뤄져야 한다(버전 4 도입). 버전 4의 peer control 도입으로 다중 CF의 multi-member working set으로 구성된 TC의 필요성이 없어졌다. multi-member working set은 VT 연결용으로는 여전히 선언될 수 있으나, TC와의 통신은 working set master만 한다.

<strong>Table B.1 — Process Data command 값</strong> (†는 버전 4 도입):

| Command | 의미 |
|---|---|
| 0<sub>16</sub> | Technical capabilities 서브커맨드 (B.5의 technical data 메시지들) |
| 1<sub>16</sub> | Device descriptor 전송·관리 서브커맨드 (B.6) |
| 2<sub>16</sub> | Request value — DDI가 지정한 데이터 엔티티 값 요청 |
| 3<sub>16</sub> | Value command — 값 응답 및 값 설정 겸용 |
| 4<sub>16</sub> | Measurement: time interval — 지정 주기(ms)로 값을 주기 송신 |
| 5<sub>16</sub> | Measurement: distance interval — 지정 거리(mm) 간격으로 값 송신 |
| 6<sub>16</sub> | Measurement: minimum threshold — 값이 임계값보다 높을 때 송신 |
| 7<sub>16</sub> | Measurement: maximum threshold — 값이 임계값보다 낮을 때 송신 |
| 8<sub>16</sub> | Measurement: change threshold — 마지막 송신 이후 변화량이 임계값 <strong>이상</strong>일 때 송신 (버전 3에서 "초과"→"이상"으로 명확화, DataLogTrigger 정의와 일치) |
| 9<sub>16</sub>† | Peer control assignment (B.4) |
| A<sub>16</sub>† | Set Value and Acknowledge — 값 설정 + 수신 확인 요구, 응답은 PDACK(D<sub>16</sub>) |
| B<sub>16</sub>, C<sub>16</sub> | Reserved |
| D<sub>16</sub> | Process Data Acknowledge (PDACK, B.7) |
| E<sub>16</sub> | Task Controller Status 메시지 (B.8.1) |
| F<sub>16</sub> | Client Task 메시지 — 클라이언트가 송신 (B.8.2) |

### B.3 Value·measurement 명령 (command 2~8, A)

<strong>바이트 배치</strong>:

| 위치 | 내용 |
|---|---|
| Byte 1, bits 4~1 | Command (2<sub>16</sub>~A<sub>16</sub>) |
| Byte 1, bits 8~5 + Byte 2 | Element number (12비트, 0~4095, SPN 5200) |
| Bytes 3~4 | DDI (LSB, MSB — 2바이트, SPN 5201, ISO 11783-11 정의) |
| Bytes 5~8 | Process variable value (signed long, 해상도·범위는 DDI 정의에 따름, SPN 5202) |

<strong>Element number</strong>는 명령을 수행할 제어 가능한 요소를 지정하며, 번호 체계는 device descriptor에 정의된다. {element number, parent number} 문법으로 구성을 기술한다. 예: 붐 3개(섹션당 노즐 6·8·6개)인 스프레이어에서 임플리먼트 전체는 0, 두 번째 붐 섹션은 2, 세 번째 붐의 두 번째 노즐은 19.

- 같은 타입·같은 계층의 요소 번호는 <strong>좌→우, 앞→뒤, 위→아래 오름차순</strong>이어야 한다. 행렬 배치면 좌→우로 시작해 앞→뒤, 위→아래 순으로 이어간다.
- 좌→우 나열된 요소들이 기하학적으로 연결되어 있을 필요는 없다(겹침·틈 허용, 단 섹션은 인접 권장). 위치 기반 제어 시에는 <strong>요소 오프셋·치수 값이 요소 번호보다 우선</strong>한다.

### B.4 Peer control assignment 메시지 (command 9<sub>16</sub>, 버전 4)

setpoint value source와 user의 연결 수립용. TC → CF 방향은 <strong>14바이트</strong>(TP 사용), CF → TC 응답은 <strong>8바이트</strong>다.

| 위치 | 내용 |
|---|---|
| Byte 1 bits 4~1 | 1001 (Control assignment) |
| Byte 1 bits 8~5 + Byte 2 | Element number |
| Bytes 3~4 | DDI |
| Byte 5 bits 4~1 | Control assignment mode |
| Byte 5 bits 8~5 + Byte 6 | 대상(setpoint value user)의 Destination Element number |
| Bytes 7~14 | 할당 상대 CF의 NAME |

<strong>Control assignment mode</strong>:

| 값 | 의미 | 방향 |
|---|---|---|
| 0 | Assign Receiver — 지정 Element/DDI가 NAME의 CF로부터 데이터 수신 시작 | TC → user |
| 1 | Unassign Receiver | TC → user |
| 2 | Receiver Ack — 수신 할당/해제 수락 | user → TC |
| 3 | Assign Transmitter — 지정 Element/DDI가 NAME의 user CF로 setpoint 송신 가능 | TC → source |
| 4 | Unassign Transmitter | TC → source |
| 5 | Transmitter Ack | source → TC |
| 6~15 | Reserved | |

- Destination Element number는 Transmit 계열 할당에서만 사용한다(source가 user에게 보낼 "Value Command"에 쓸 user 측 element 번호). Receiver 계열에서는 FFF<sub>16</sub>으로 설정한다. DDI는 source와 target 양쪽 descriptor에서 같아야 하므로 하나만 존재한다.
- 응답은 같은 메시지를 mode만 올바른 Ack 값으로 바꾸고 Byte 5 bits 8~5 = F<sub>16</sub>, bytes 6~8 = FF<sub>16</sub>로 채워 단일 패킷으로 보낸다. <strong>응답 또는 타임아웃 전에는 한 CF에 다음 할당 메시지를 보낼 수 없다</strong>.
- 거부 시에는 PDACK로 응답하며 정의된 오류 비트로 사유를 표시한다.
- 연결은 task totals 상태가 active → inactive로 바뀌면 끊어진다. 그 전에 끊거나 상대가 할당을 거부하면, 동일 필드에 mode만 해제 값으로 바꾼 메시지를 보낸다.

### B.5 Technical data 메시지 (command 0<sub>16</sub>)

TC·참여 클라이언트의 특성을 질의하는 메시지들. Byte 1 bits 8~5가 파라미터를 구분한다.

<strong>B.5.2 Request Version</strong> (bits 8~5 = 0000): 8바이트, on request. 상대 구현의 ISO 11783-10 버전 확인용. bytes 2~8은 FF<sub>16</sub>.

<strong>B.5.3 Version 메시지</strong> (bits 8~5 = 0001): Request Version에 대한 응답.

| 바이트 | 내용 |
|---|---|
| 2 | 버전: 0=DIS, 1=FDIS.1, 2=FDIS.2·초판 IS, 3=2판 DIS(E2.DIS), 4=2판 FDIS·IS(E2.FDIS/E2.IS) |
| 3 | Boot time — 전원 사이클부터 첫 TC Status 송신까지 최대 초. 정보 없으면 FF<sub>16</sub>. <strong>TC/DL의 Version 메시지에서만 의미가 있고 클라이언트는 FF<sub>16</sub></strong>로 설정 (버전 3 도입) |
| 4 | Provided options: bit 1 = 문서화 지원(TC-BAS 기능성 — task totals 처리), bit 2 = 위치 기반 제어 없는 TC-GEO(위치 기반 로깅), bit 3 = 위치 기반 제어 포함 TC-GEO, bit 4 = peer control assignment, bit 5 = TC-SC(섹션 제어), bits 6~8 = 예약 (버전 3 도입) |
| 5 | Provided options byte 2 — 전부 예약 (버전 3 도입) |
| 6 | 섹션 제어 붐 수 — TC가 보고 시 지원 최대치, 클라이언트 보고 시 제어 가능한 수. "섹션 제어 붐" = Section Control State DDI를 참조하는 DPD를 가진 DeviceElement |
| 7 | 섹션 수(전체 붐 합산) — TC는 최대 지원치, 클라이언트는 제어 가능 수 |
| 8 | 위치 기반 제어 채널 수 — "위치 기반 제어 채널" = Prescription Control State DDI를 참조하는 DPD를 가진 DeviceElement |

TC 클라이언트는 TC-SC·TC-GEO 기능성(Annex F) 요구사항에 맞춰 붐·섹션·채널 수를 조정해 동작해야 하지만, Version 메시지에 보고하는 값은 조정치가 아니라 <strong>클라이언트 자체 능력</strong>이다.

<strong>B.5.4 Request Identify Task Controller</strong> (bits 8~5 = 0010, 버전 4): 클라이언트·TC 모두 송신 가능. 수신한 TC는 <strong>TC Number를 3초간 표시</strong>해야 한다. 통상 global 목적지로 보내며 destination-specific도 가능하다. 표시는 TC proprietary다. DL CF에도 유효하다. <strong>B.5.5 Identify Task Controller response</strong>: destination-specific으로 받은 경우의 응답(8바이트). GUI 없는 TC는 표시하지 못할 수 있다.

### B.6 Device descriptor 메시지 (command 1<sub>16</sub>)

클라이언트 → TC/DL로 device descriptor를 전송하고 DDOP을 유지하기 위한 메시지들. Byte 1 bits 8~5가 서브커맨드를 구분한다.

| bits 8~5 | 메시지 | 요지 |
|---|---|---|
| 0000 | Request Structure Label | 8~40바이트. 특정 structure label(+Extended)이 TC/DL에 있는지 확인. bytes 2~8을 FF<sub>16</sub>로 보내면 최신 descriptor의 라벨 질의(버전 3 이하 호환). Extended 라벨을 요청하면 TP 사용 |
| 0001 | Structure Label | 응답. 요청 라벨이 있으면 그 라벨(+Extended)을, 없으면 7바이트 전부 FF<sub>16</sub>인 단일 CAN 프레임 |
| 0010 | Request Localization Label | 8바이트. 특정 localization label 존재 확인. FF<sub>16</sub>로 보내면 최신 것 질의 |
| 0011 | Localization Label | 응답. 없으면 전부 FF<sub>16</sub>. 바이트 1~6은 language command PGN 정의, 바이트 7 예약(FF<sub>16</sub>) |
| 0100 | Request Object-pool Transfer | bytes 2~5 = 전송할 데이터 크기(바이트). DDOP 전송 허용 여부 확인 |
| 0101 | Request Object-pool Transfer Response | Byte 2: 0 = 메모리 충분할 수 있음(오버헤드 때문에 보장은 아님), 1 = 메모리 부족 — 전송 금지 |
| 0110 | Object-pool Transfer | bytes 2~n = 객체 레코드. 여러 메시지로 분할 가능하되 <strong>각 전송은 완전한 객체 기술 단위</strong>여야 함 |
| 0111 | Object-pool Transfer Response | Byte 2: 0 = 정상, 1 = 전송 중 메모리 소진, 2 = 기타 오류. bytes 3~6 = 수신 데이터 크기 |
| 1000 | Object-pool Activate/Deactivate | Byte 2: FF<sub>16</sub> = activate, 0 = deactivate. activate는 연결 절차 완료(pool 완성·사용 준비) 표시 — pool 전송 후, 운영 중 객체 재정의·추가 후, 또는 라벨 비교로 장치의 pool 버전이 TC/DL의 것과 같음이 확인된 후 송신. 업로드가 없었으면 TC/DL은 마지막으로 성공 응답한 Structure Label 요청의 pool을 활성화. deactivate는 의도적 연결 해제(버전 4 도입) |
| 1001 | Object-pool Activate/Deactivate Response | 아래 상술 |
| 1010 | Object-pool Delete | 송신 클라이언트의 DDOP 삭제. <strong>클라이언트가 정의한 pool만</strong> 삭제 가능 — FMIS에서 받은 pool은 영향 없음. 로그 데이터·태스크 할당 참조 때문에 삭제가 불가능할 수 있음 |
| 1011 | Object-pool Delete Response | Byte 2: 0 = 성공, 1 = 오류. Byte 3(버전 4): 0 = 태스크 데이터가 참조 중, 1 = 서버가 참조 확인 불가, FF<sub>16</sub> = 상세 없음. 버전 4부터 모든 Delete에 응답 필수(버전 3까지는 응답 여부가 불명확했음) |
| 1100 | Change Designator | bytes 2~3 = Object ID, byte 4 = designator 길이(0~128바이트, 최대 32 UTF-8 문자), bytes 5~n = UTF-8 designator(BOM 없음) |
| 1101 | Change Designator Response | bytes 2~3 = Object ID, byte 4 = 오류 코드(0/1) |

<strong>Object-pool Activate/Deactivate Response 상세</strong>:

- Byte 2 오류 코드: bit 1 = pool에 오류 있음(bytes 3~7 참조), bit 2 = 활성화 중 메모리 소진, bit 3 = 기타 오류, bit 4 = 동일 structure label의 다른 DDOP이 이미 TC에 존재해 미활성화(버전 4).
- Bytes 3~4 = 오류 객체의 부모 object ID, bytes 5~6 = 오류 객체의 object ID (오류 없으면 NULL object ID).
- Byte 7 object-pool 오류 코드: bit 1 = TC/DL이 지원하지 않는 method/attribute, bit 2 = 알 수 없는 객체 참조(누락), bit 3 = 기타, bit 4 = pool이 휘발성 메모리에서 삭제됨.
- <strong>activate에서 오류 응답 시 TC/DL은 pool을 휘발성 메모리에서 삭제</strong>하고, 사유를 오퍼레이터에게 알릴 수 있다. FMIS 파일 세트에 이미 있는 device descriptor를 클라이언트가 활성화하지 못하는 경우 그 클라이언트와의 통신은 계속하지 않는다. 오류가 있는 descriptor는 MICS → FMIS 파일 세트에 쓰지 않는다.
- 정상 deactivate 응답의 최대 응답 시간은 <strong>2 s</strong>다.

### B.7 Process Data Acknowledge (PDACK, command D<sub>16</sub>)

클라이언트(working set master) 또는 TC/DL이 명령·process data를 수락/거부할 때 보낸다. 사유는 process data value의 최하위 바이트에 담는다. 오류가 특정 element/DDI와 무관하면 element number = FFF<sub>16</sub>, DDI = FFFF<sub>16</sub>(not available)로 설정한다.

- 불필요한 버스 부하를 피하기 위해, <strong>오류 코드 0(정상)인 PDACK는 command 0·1·2·3·9·D·E·F<sub>16</sub>에 대한 응답으로 보내지 않는다</strong>. (즉 positive ACK가 필요한 것은 measurement 명령 4~8과 Set Value and Acknowledge A<sub>16</sub>)
- 구조: Byte 1 bits 4~1 = 1101, element number, bytes 3~4 = DDI, byte 5 = 오류 코드, byte 6 bits 4~1 = 이 PDACK가 응답하는 Process Data Command(무관하면 F<sub>16</sub>, 버전 4 도입).

<strong>Process Data 오류 코드 비트</strong>: bit 1 = 명령 미지원, bit 2 = 잘못된 element number, bit 3 = element가 지원하지 않는 DDI, bit 4 = trigger method 미지원, bit 5 = process data가 settable 아님, bit 6 = 무효/미지원 interval·threshold, bit 7 = 값이 DDI 정의에 부합하지 않음(버전 4), bit 8 = 값이 장치 운영 범위 밖(버전 4).

### B.8 Status 메시지

<strong>B.8.1 Task Controller Status</strong> (command E<sub>16</sub>): TC가 현재 태스크 상태를 알리는 메시지. 주기 2 s + 임의 바이트 변경 시 즉시(최소 간격 200 ms). PGN은 process data, <strong>global destination</strong>. element number·DDI 필드는 not available(FF/FFFF<sub>16</sub>)로 설정하고 클라이언트는 무시한다.

Byte 5 = 실제 TC/DL 상태:

| 비트 | 의미 |
|---|---|
| bit 1 | Task totals active — 태스크 시작·재개됨, total 누적 가능. 0→1 전이 시 클라이언트 내부 task total 0으로 리셋 후 카운트 시작, 1→0 전이 시 total 중지(TC/DL이 Request Value로 조회 가능) |
| bit 2 | 비휘발성 메모리에 저장 중(busy) |
| bit 3 | 비휘발성 메모리에서 읽는 중(busy) |
| bit 4 | B.6(device descriptor) 명령 실행 중(busy) |
| bit 8 | 메모리 부족 |

Byte 6 = 실행 중인 B.6 명령의 대상 클라이언트 소스 주소, Byte 7 = 실행 중인 B.6 명령의 Byte 1 (모두 bit 4 설정 시에만 유효, 아니면 0).

<strong>B.8.2 Client Task</strong> (command F<sub>16</sub>): 모든 클라이언트가 TC/DL로 보내는 상태 메시지. 주기 2 s + 태스크 상태 변화 시(최소 간격 200 ms), destination-specific. element number·DDI는 not available. Bytes 5~8의 bit 1 = task totals active(TC Status에서 수신한 값의 반향), 나머지 비트는 예약(0).

## Annex C (normative) — XML elements relationship diagram

Figure C.1/C.2가 전체 엔티티의 ERD를 정의하며, XML 파일 내용은 이 관계도를 따라야 한다. 다이어그램의 엔티티에 외래 키 식별자가 항상 표시되지는 않는다 — XML 파일 내 정의 순서로 결정 가능하기 때문이다.

- 예: Task는 WorkerAllocation과 1 대 0..n 관계다. worker가 할당되면 WorkerAllocation 정의는 TaskHeaderData 정의 뒤에 와서 태스크와의 관계를 얻는다. Worker는 Task와도 직접 1 대 0..n 관계가 있다 — 한 Worker가 여러 Task의 "Responsible Worker"일 수 있다.
- 관계 읽기: 선 끝은 "반대쪽 끝에서" 읽어 원 엔티티에서 상대 엔티티로의 다중도를 결정한다. 예: Worker ↔ WorkerAllocation은 "Worker는 0개 이상의 WorkerAllocation에 나타날 수 있고, WorkerAllocation은 정확히 1명의 worker에 묶인다".

주요 관계(ERD 요지): Customer–Farm–Partfield가 관리 계층을 이루고(Partfield는 2단계까지 중첩 가능한 frame partfield 구조), Task가 중심 엔티티로서 Worker/Device/Product/Comment/Guidance 할당, TreatmentZone·Grid·TimeLog·DataLogTrigger·ControlAssignment·Connection을 묶는다. Device 아래에 DeviceElement–DeviceProcessData/DeviceProperty–DeviceValuePresentation 계층이 있고, Product는 ProductGroup·ProductRelation과 연결된다. Guidance 계열은 Partfield–GuidanceGroup–GuidancePattern(–BaseStation)–LineString/BoundaryPolygon 구조이며, Task의 GuidanceAllocation이 GuidanceShift를 통해 실제 사용을 기록한다.

## Annex D (normative) — XML elements and attributes

각 XML 요소의 속성 정의를 담은 레퍼런스 부속서다. 속성 표는 Attribute(이름), XML(속성 태그 문자), Use(r = 필수, o = 선택), Type, Length/range, Comment 6열로 구성된다. 아래에서는 요소별 핵심 속성과 특이사항만 압축 정리한다.

:::info 공통 규칙
- <strong>xs:dateTime</strong> 포맷은 `CCYY-MM-DDThh:mm:ss.sss`이며, 끝에 시간대 표기를 붙일 수 있다 — `Z` = UTC, `+hh:mm`/`-hh:mm` = UTC 오프셋(−14:00~14:00). 시간대 표기가 없으면 <strong>로컬 시간</strong>으로 간주한다(UTC로 가정하지 않음).
- ID 형식은 `(약어|약어-)(숫자)+`이며 <strong>MICS에서 생성된 레코드는 음수 ID</strong>를 가진다(예: WKR-1). 길이는 최소 4, 최대 14자.
- designator류 문자열은 대부분 최대 32자다.
:::

### D.2 AllocationStamp — ASP (task data)

할당 이벤트의 기록. FMIS가 제공한 ASP는 <strong>planned</strong>, MICS가 제공한 ASP는 <strong>effective</strong> 타입이어야 한다.

| 속성 | XML | Use | 내용 |
|---|---|---|---|
| Start | A | r | 시작 시각 (xs:dateTime, 최대 29자) |
| Stop | B | o | 종료 시각 |
| Duration | C | o | 초 단위 (0~2³²−2). Start~Stop 경과 시간 |
| Type | D | r | 1 = Planned, 4 = Effective(Realized) |
| Position | — | o | 최대 2개의 Position 자식 요소 (시작·종료 위치) |

- 모든 ASP는 Start가 필수다. 유한 ASP는 Start+Stop 또는 Start+Duration으로 지정한다(나머지 하나는 계산 가능). Start만 기록하는 무한 ASP도 허용된다.
- 버전 4에서 시간대가 도입됐다: 시간대를 아는 경우 UTC(`Z`) 또는 오프셋 표기를 붙여야 한다 — 여러 시간대의 데이터를 FMIS가 정규화할 수 있게 하기 위함이다. 시간대를 모르면 표기 없이 로컬 시간으로 쓴다. 버전 3까지는 TimeLog 바이너리에 UTC와 로컬 시간이 모두 기록된 경우에만 그 차로 시간대를 계산할 수 있었다.
- CommentAllocation·DeviceAllocation·ProductAllocation·WorkerAllocation에 포함된다.

### D.3 AttachedFile — AFE (external data, 버전 4)

제조사 proprietary 파일을 파일 세트에 포함시키는 요소. 파일은 TASKDATA.XML과 같은 디렉터리에 있어야 하며 파일명은 대문자다.

| 속성 | XML | Use | 내용 |
|---|---|---|---|
| FilenameWithExtension | A | r | xs:ID, 12자 — 8.3 형식 파일명 (A-Z, 0-9), 예: "PROPDATA.BIN" |
| Preserve | B | r | 1 = TC가 보존할 필요 없음(즉시 삭제·AFE 생략 가능), 2 = TC가 보존해 FMIS로 반송 |
| ManufacturerGLN | C | r | ISO 사전 정의 첨부는 빈 값, 그 외에는 제조사 GS1 GLN |
| FileType | D | r | 1~127 = ISO 사전 정의(1 = LINKLIST — 고정 파일명 'LINKLIST.XML', TASKDATA.XML당 최대 1개), 128~254 = 제조사 정의 |
| FileVersion | E | o | 버전 문자열 (최대 32자) |
| FileLength | F | o | 파일 길이(바이트) |

다른 제조사의 첨부 파일 중 사전 정의 타입이 아닌 것은 TC가 내용을 무시할 수 있다. 반송이 불필요한 경우 Preserve = 1로 설정해 불필요한 전송을 막는다.

### D.4 BaseStation — BSN (coding data, 버전 4)

측위 시스템 기지국. GuidancePattern이 참조한다. 속성: BaseStationId(A, r), BaseStationDesignator(B, r, 최대 32자), BaseStationNorth(C, r, xs:decimal −90.0~90.0 WGS84), BaseStationEast(D, r, −180.0~180.0), BaseStationUp(E, r, WGS84 타원체 고도 mm).

### D.5~D.7 CodedComment(CCT) · CodedCommentGroup(CCG) · CodedCommentListValue(CCL) — coding data

태스크에 주석을 달기 위한 사전 정의 코멘트 체계.

- <strong>CCT</strong>: CodedCommentId(A, r), designator(B, r), <strong>CodedCommentScope</strong>(C, r — 1 = point, 2 = global, 3 = continuous), CodedCommentGroupIdRef(D, o), CCL 목록(o). 코멘트는 "low/medium/high" 같은 값 목록(CCL)을 가질 수 있고, 태스크에 할당할 때 그중 하나를 참조한다.
- <strong>CCG</strong>: id(A, r) + designator(B, r). 모바일 시스템에서 코멘트 탐색·선택을 돕는 그룹(예: "weeds" 그룹에 camomile·couch grass·thistle). CCT는 하나의 그룹에만 속할 수 있으며, 그룹 소속은 CCT의 CodedCommentGroupIdRef를 검사해 결정한다.
- <strong>CCL</strong>: id(A, r) + designator(B, r). 항상 단일 CCT에만 속한다.

### D.8~D.9 ColourLegend(CLD) · ColourRange(CRG) — coding data

그리드 맵 값의 색상 표시 정의. ValuePresentation이 CLD를 참조한다.

- <strong>CLD</strong>: id(A, r), DefaultColour(B, o, 0~254 — 어느 범위에도 안 들어가는 값의 색), CRG 목록(r).
- <strong>CRG</strong>: MinimumValue(A, r)·MaximumValue(B, r — 경계 포함, signed long), Colour(C, r, 0~254 — ISO 11783-6 팔레트).

### D.10 CommentAllocation — CAN (task data)

CodedComment 또는 자유 텍스트를 태스크에 할당한다. AllocationStamp로 시각·위치를 지정한다.

| 속성 | XML | Use | 내용 |
|---|---|---|---|
| CodedCommentIdRef | A | o | CCT 참조 |
| CodedCommentListValueIdRef | B | o | 할당된 CCT의 값 목록 중 하나 |
| FreeCommentText | C | o | 자유 텍스트 (최대 32자) |
| AllocationStamp | — | o | 단일 ASP |

- 하나의 CAN은 CodedComment 참조 <strong>또는</strong> FreeCommentText 중 하나만 배타적으로 가진다.
- CCT 할당 이벤트당 CAN은 1개만 기록한다. continuous 타입은 시작 시 위치를 담고, 종료 시 같은 CAN의 ASP에 start·stop을 모두 채운다.
- continuous 타입 CCT가 활성화되면 TC는 바이너리 로그의 시간·위치 로깅 활성 여부를 확인하고, 비활성이면 <strong>1 Hz</strong>로 활성화해야 한다. continuous 코멘트가 없고 다른 로깅 요청도 없으면 시간·위치 로깅을 중지한다 — continuous 코멘트 활성 동안 위치가 반드시 로깅되게 하는 규칙이다.

### D.11 Connection — CNN (task data)

한 태스크 안에서 두 장치가 어떻게 연결됐는지 지정한다. 두 장치의 <strong>connector 타입 DeviceElement</strong> 참조 쌍으로 구성되며, TC가 한 장치의 DeviceElement 위치를 다른 장치의 NavigationReferencePoint 등에 상대적으로 계산할 수 있게 한다.

속성: DeviceIdRef_0(A, r), DeviceElementIdRef_0(B, r), DeviceIdRef_1(C, r), DeviceElementIdRef_1(D, r). 각 DeviceElement는 해당 Device에 속해야 하고 타입이 "connector"여야 한다.

### D.12 ControlAssignment — CAT (task data, 버전 4)

setpoint value source CF → user CF 할당 기록(예: 센서 시스템 element의 process data 값 → 애플리케이션 컨트롤러 element). 태스크 실행 중 만들어진 할당을 기록해 재시작 시 오퍼레이터 개입 없이 같은 할당을 재수립하게 하며, FMIS가 계획 할당으로 쓸 수도 있다. 같은 CF·DDI 조합의 CAT가 여러 개 있으면(할당 시간 구간 기록) <strong>최신 타임스탬프의 것</strong>을 재수립에 쓴다.

| 속성 | XML | Use | 내용 |
|---|---|---|---|
| SourceClientNAME | A | r | source CF의 NAME (hexBinary 8바이트) |
| UserClientNAME | B | r | user CF의 NAME |
| SourceDeviceStructureLabel | C | r | source descriptor의 structure label (7바이트 + 확장 최대 32바이트) |
| UserDeviceStructureLabel | D | r | user descriptor의 structure label |
| SourceDeviceElementNumber | E | r | 0~4095 |
| UserDeviceElementNumber | F | r | 0~4095 |
| ProcessDataDDI | G | r | source·user 공통 DDI (hexBinary) |
| AllocationStamp | — | o | 단일 ASP |

### D.13~D.14 CropType(CTP) · CropVariety(CVT) — coding data

- <strong>CTP</strong>: partfield에서 재배 가능한 작물. id(A, r), designator(B, r), ProductGroupIdRef(C, o — 버전 4, "CropType" 타입 ProductGroup 참조로 상품(commodity)과 교차 참조 가능), CVT 목록(o).
- <strong>CVT</strong>: 작물 품종. 단일 CTP에 속한다. id(A, r), designator(B, r), ProductIdRef(C, o — 버전 4, CropType 그룹 내 Product 참조).

### D.15 CulturalPractice — CPC (coding data)

작물 생산 목표를 실현하는 활동(예: "primary soil tillage", "seeding"). OperTechPractice를 통해 태스크에 할당된다. 여러 OperationTechnique 참조를 가질 수 있다(예: "fertilization" → liquid/organic/gaseous fertilization). 속성: id(A, r), designator(B, r), OperationTechniqueReference 목록(o).

### D.16 Customer — CTR (coding data)

고객 정보. Task·Farm·Partfield가 참조한다. 고객-농장/필지 관계는 다중이며, 소속 판정은 Farm/Partfield의 CustomerIdRef 매칭으로 한다. 속성: CustomerId(A, r), CustomerLastName(B, r), CustomerFirstName(C, o), 주소류(Street/POBox/PostalCode/City/State/Country, D~I, o), 연락처(Phone/Mobile/Fax J·K·L, o, 최대 20자; EMail M, o, 최대 64자).

### D.17 DataLogTrigger — DLT (task data)

태스크에 포함되어 어떤 ProcessDataVariable 값을 DataLogValue로 로깅할지 지정한다.

| 속성 | XML | Use | 내용 |
|---|---|---|---|
| DataLogDDI | A | r | 로깅할 DDI (hexBinary) |
| DataLogMethod | B | r | 비트 조합: 1 = time interval, 2 = distance interval, 4 = threshold limits, 8 = on change, 16 = total (1~31) |
| DataLogDistanceInterval | C | o | mm, 0~1000000. 0 = 측정 중지 |
| DataLogTimeInterval | D | o | ms, 0~60000. 0 = 중지, 최소 100 ms |
| DataLogThresholdMinimum | E | o | 최소 임계값 (2³¹−1 = 중지) |
| DataLogThresholdMaximum | F | o | 최대 임계값 (−2³¹+1 = 중지) |
| DataLogThresholdChange | G | o | 변화 임계값. 0 = 중지, 1 = 모든 변화 로깅 |
| DeviceElementIdRef | H | o | 대상 DeviceElement |
| ValuePresentationIdRef | I | o | 표시 정보 |
| DataLogPGN | J | o | 로깅할 parameter group (0~2¹⁸−1) |
| DataLogPGNStartBit / StopBit | K, L | o | 0~63. 데이터 프레임에서 값의 시작/끝 비트(경계 포함, start = LSB) |

- DeviceElementIdRef가 없으면 TC는 <strong>해당 DDI를 공급할 수 있는 모든 DeviceElement</strong>에서 로깅한다. 참조는 장치가 태스크에 할당되는 즉시 모바일 시스템에서 추가될 수 있고, FMIS에서 이미 지정됐다면 특정 장치가 계획된 것이다.
- time/distance/on change는 임의 조합 가능 — <strong>먼저 발생한 이벤트가 로깅을 트리거하고 세 방법 모두 재시작</strong>된다. threshold limits를 추가하면 값이 임계 범위 안에 있는 동안만 로깅이 활성화된다.
- ThresholdMinimum < ThresholdMaximum이면 그 사이 값에서 로깅 활성화. Minimum > Maximum이면 Minimum보다 크거나 Maximum보다 작은 값에서 활성화(범위 반전).
- "total" 방법은 다른 방법과 독립이며 임의 조합 가능. total 타입 DataLogValue는 태스크의 Time 요소당 1회 저장된다.
- parameter group 로깅 시 DataLogPGN·StartBit·StopBit를 지정하고 DataLogDDI = DFFE<sub>16</sub>(PGN log value)로 설정한다.

### D.18 DataLogValue — DLV (task data)

단일 DeviceElement가 공급한 단일 ProcessDataVariable의 값 1개. Time 요소에 포함되며 이 관계로 태스크에 귀속된다 — 위치·시각은 Time이 지정한다.

속성: ProcessDataDDI(A, r), ProcessDataValue(B, r, signed long), DeviceElementIdRef(C, r), DataLogPGN(D, o)·DataLogPGNStartBit(E, o)·DataLogPGNStopBit(F, o — parameter group 로깅 시 사용, 이때 DDI = DFFE<sub>16</sub>).

### D.19 Device — DVC (coding data)

기계나 센서 시스템 같은 완전한 장치를 기술한다. 장치는 최소 1개의 DeviceElement를 가져야 한다. DeviceElement·DeviceProcessData·DeviceProperty·DeviceValuePresentation을 자식으로 포함하고, Connection·DeviceAllocation이 참조한다.

| 속성 | XML | Use | 내용 |
|---|---|---|---|
| DeviceId | A | r | xs:ID |
| DeviceDesignator | B | o | 최대 32자 |
| DeviceSoftwareVersion | C | o | 최대 32자 |
| ClientNAME | D | r | 클라이언트의 NAME (hexBinary 8바이트) |
| DeviceSerialNumber | E | o | 최대 32자 (예: 차량·제품 식별 코드, ISO 11783-12 2판 정의) |
| DeviceStructureLabel | F | r | hexBinary. 하위 7바이트는 바이트당 00~FE<sub>16</sub>, 확장 라벨 바이트는 00~FF<sub>16</sub>, 확장 최대 32바이트 |
| DeviceLocalizationLabel | G | r | hexBinary 7바이트. 바이트 1~6 = language command PGN 정의, 바이트 7 = FF<sub>16</sub> 예약 |

:::tip 라벨의 바이트 순서
XML의 xs:hexBinary 표기에서 structure label 배열의 <strong>바이트 1이 최하위(문자열의 끝)</strong>이고 바이트 n이 최상위다. CAN 버스로 전송되는 DeviceObject에서는 배열 순서(바이트 1부터)로 나간다. 예: XML `F="F9FAFBFCFDFE39"`는 버스에서 39 FE FD FC FB FA F9 순으로 전송된다. localization label도 동일하다 — 언어 코드 'en'(65<sub>16</sub> 6E<sub>16</sub>)이면 XML 표기의 마지막 바이트가 65<sub>16</sub>이다. 확장 structure label(최대 32바이트)은 XML 표기에서 7바이트 라벨 앞쪽에 이어 붙는다.
:::

### D.20 DeviceAllocation — DAN (task data)

계획 태스크가 어떤 장치를 위해 만들어졌는지, 그리고 실제로 어떤 장치가 쓰였는지를 담는다. 계획 태스크에서는 ClientNAMEValue + (선택) NAME 마스크로 허용 장치 범위를 지정하고, 태스크 처리 중 TC가 실제 사용된 클라이언트 정보로 새 DeviceAllocation을 태스크에 추가한다.

| 속성 | XML | Use | 내용 |
|---|---|---|---|
| ClientNAMEValue | A | r | 대상/사용 클라이언트 NAME (hexBinary 8바이트) |
| ClientNAMEMask | B | o | 논리 AND용 비트마스크 — bit 1 = ClientNAMEValue의 해당 비트가 유효, 0 = 무관 |
| DeviceIdRef | C | o | Device 참조 |
| AllocationStamp | — | o | 단일 ASP |

예: 마스크로 "네트워크에서 처음 발견되는 스프레이어 machine controller"처럼 느슨하게 지정(특정 Device 참조 없음)할 수도, 마스크 전체 FF + 특정 Device 참조로 정확한 인스턴스를 지정할 수도 있다. 실제 사용 기록은 마스크 없이 NAME + DeviceIdRef + effective ASP로 추가된다.

### D.21 DeviceElement — DET (coding data)

장치의 기능적·물리적 요소. 계층 구조를 위해 다른 DeviceElement나 장치 자체를 참조해야 한다. ParentObjectId가 DeviceObject(object ID 0) 또는 부모 DeviceElementObject를 가리킨다. Connection·DataLogTrigger·DataLogValue·ProcessDataVariable·ProductAllocation이 참조한다.

| 속성 | XML | Use | 내용 |
|---|---|---|---|
| DeviceElementId | A | r | xs:ID |
| DeviceElementObjectId | B | r | 1~65534, descriptor 내 유일 |
| DeviceElementType | C | r | 1 = device, 2 = function, 3 = bin, 4 = section, 5 = unit, 6 = connector, 7 = navigation |
| DeviceElementDesignator | D | o | 최대 32자 |
| DeviceElementNumber | E | r | 0~4095 — process data variable 주소 지정용 element 번호 |
| ParentObjectId | F | r | 0~65534 |
| DeviceObjectReference | — | o | DOR 목록 |

### D.22 DeviceObjectReference — DOR (coding data)

DeviceElement가 포함하는, DeviceProcessData 또는 DeviceProperty 객체로의 참조. 속성은 DeviceObjectId(A, r, 1~65534) 하나다.

### D.23 DeviceProcessData — DPD (coding data)

이 요소를 참조하는 DeviceElement가 지원하는 ProcessDataVariable DDI를 기술한다.

| 속성 | XML | Use | 내용 |
|---|---|---|---|
| DeviceProcessDataObjectId | A | r | 1~65534 (장치 내 유일) |
| DeviceProcessDataDDI | B | r | hexBinary (ISO 11783-11) |
| DeviceProcessDataProperty | C | r | 비트 조합: 1 = default set 소속, 2 = settable, 4 = control source(버전 4). <strong>settable과 control source는 상호 배타</strong> |
| DeviceProcessDataTriggerMethods | D | r | 비트 조합: 1 = time interval, 2 = distance interval, 4 = threshold limits, 8 = on change, 16 = total |
| DeviceProcessDataDesignator | E | o | 최대 32자 |
| DeviceValuePresentationObjectId | F | o | 1~65534 |

### D.24 DeviceProperty — DPT (coding data)

DDI 참조 + 값으로 DeviceElement의 정적 속성을 기술한다. 속성: DevicePropertyObjectId(A, r), DevicePropertyDDI(B, r), DevicePropertyValue(C, r, signed long), designator(D, o), DeviceValuePresentationObjectId(E, o).

### D.25 DeviceValuePresentation — DVP (coding data)

장치 내부에서 쓰이는 데이터 사전 정수값의 표시 방법을 정의한다. 표시 공식은 다음과 같다.

<strong>표시값 = (정수값 + Offset) × Scale</strong>, NumberOfDecimals 자리로 반올림.

속성: DeviceValuePresentationObjectId(A, r, 1~65534), Offset(B, r, signed long), Scale(C, r, xs:decimal 0.000000001~100000000.0), NumberOfDecimals(D, r, 0~7), 그리고 단위 표기(UnitDesignator).


## 부속서 D — XML 요소 정의 (계속: D.26~)

### D.26 Farm — FRM

농장 하나를 기술하는 coding data 요소다. 데이터 전송 파일 세트 안에서 하나의 Farm은 다른 농장과 독립적으로 관리되는 필드(Partfield)들의 집합을 가질 수 있다. Customer와 Farm/Partfield의 관계는 다대다가 가능하며, 특정 고객 소속 여부는 각 Farm·Partfield의 CustomerIdRef를 CustomerId와 대조해 판별한다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| FarmId | A | r | xs:ID, 4~14자 | 고유 식별자. 형식 `(FRM\|FRM-)([0-9])+`, MICS 생성 레코드는 음수 ID |
| FarmDesignator | B | r | 최대 32자 | 농장 이름 |
| FarmStreet~FarmCountry | C~H | o | 최대 10~32자 | 주소 필드(도로명, 사서함, 우편번호, 도시, 주, 국가) |
| CustomerIdRef | I | o | xs:IDREF | 소속 Customer 참조 (`CTR` 형식) |

### D.27 Grid — GRD

그리드셀 집합의 크기·위치를 기술하는 task data 요소다. 최소 북/동 위치, 셀 하나의 크기, 북/동 방향 셀 개수를 정의한다. 핵심 제약은 다음과 같다.

- Task당 Grid는 최대 1개다. 그리드는 partfield와 연관되지만 정의 자체는 항상 task 종속이다.
- 그리드셀은 TreatmentZone 참조 또는 process data variable 값을 담는다.
- 셀 배열은 오름차순의 완전한 배열로 기록한다 — 셀 자체에는 순서 정보가 없다.
- 셀 데이터는 별도 바이너리 파일에 저장하며, grid·task당 바이너리 파일은 1개다. 파일은 데이터 전송 파일 세트와 같은 디렉터리에 있어야 하고 이름은 파일 세트 전체에서 유일해야 한다.
- OperTechPractice가 여러 개면 FMIS가 모든 OperTechPractice에 유효한 TreatmentZone을 지정하는 공통 Grid를 만들어야 한다. 하나의 TreatmentZone에 여러 ProcessDataVariable을 담아 다변수 위치 기반 제어를 하는 것은 grid type 1·2 모두 가능하다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| GridMinimumNorthPosition | A | r | −90.0~90.0 | 그리드 최소 북위(WGS84) |
| GridMinimumEastPosition | B | r | −180.0~180.0 | 그리드 최소 동경(WGS84) |
| GridCellNorthSize / EastSize | C, D | r | 0.0~1.0 | 셀의 북/동 방향 크기(도 단위) |
| GridMaximumColumn / Row | E, F | r | 0~2³²−1 | 동/북 방향 셀 개수 |
| Filename | G | r | 8자 | 셀 파일 이름. 형식 `GRD[0-9]{5}`, 파일 세트 내 유일 |
| Filelength | H | o | 0~2³²−2 | 셀 파일 바이트 길이 |
| GridType | I | r | 1~2 | 1 = grid type 1, 2 = grid type 2 |
| TreatmentZoneCode | J | o | 0~254 | grid type 2에서 사용할 TreatmentZoneCode |

### D.28 GuidanceAllocation — GAN

GuidanceGroup을 Task에 할당하는 task data 요소다(버전 4에서 추가). 내부의 AllocationStamp가 할당의 시작/종료 시각을 기록해 할당 변경 이력을 추적할 수 있게 한다. 포함되는 GuidanceShift 요소는 할당된 GuidanceGroup의 GuidancePattern들에 적용할 지리적 이동(shift)을 기술하며, shift가 여러 번 일어나면 각 shift마다 새 GuidanceShift 요소가 기록된다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| GuidanceGroupIdRef | A | r | xs:IDREF | GuidanceGroup 참조 (`GGP` 형식) |
| AllocationStamp | | r | 요소 | 단일 AllocationStamp 포함 |
| GuidanceShift | | o | 요소 | GuidanceShift 목록 포함 |

### D.29 GuidanceGroup — GGP

하나 이상의 GuidancePattern(GPN)을 묶는 coding data 요소다(버전 4에서 추가). 그룹 내 패턴들은 동시에 사용될 것을 의도한다. 전형적으로 헤드랜드(headland) 안내 패턴 2개 + 메인필드(mainfield) 안내 패턴 1개 구성이지만, 어떤 조합도 가능하다. 필드 경계가 여러 외곽 폴리곤으로 이루어진 경우 여러 헤드랜드/메인랜드 패턴이 필요할 수 있다. 패턴이 하나뿐인 그룹이라면 그 패턴은 mainland 패턴이어야 한다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| GuidanceGroupId | A | r | xs:ID | 고유 식별자 (`GGP` 형식, MICS는 음수) |
| GuidanceGroupDesignator | B | o | 최대 32자 | 그룹 이름 |
| GuidancePattern | | r | 요소 | GuidancePattern 목록 |
| BoundaryPolygon | | o | 요소 | 그룹의 유효 범위를 필드 경계 안 특정 영역으로 제한하는 Polygon 목록. 외곽 경계에 더해 내부 경계(제외 구역)를 가질 수 있다 |

### D.30 GuidancePattern — GPN

안내(guidance) 작업 실행에 필요한 데이터를 담는 coding data 요소다(버전 4에서 추가). GuidancePattern 요소가 패턴의 분류 속성을, 자식 LineString 요소가 지리 정보를 담는다. GuidancePattern은 항상 정확히 1개의 LineString을 가지며, LineString 안의 점 구성은 패턴 타입이 결정한다. 인접 경로 사이 간격(swathe width)은 LineString의 LineStringWidth 속성으로 표현한다.

패턴 타입별 점 구성:

| 타입 | 필수 점 | 선택 점 | 비고 |
| --- | --- | --- | --- |
| AB | 시작점 A, 끝점 B | 없음 | |
| A+ | A점 1개 | 없음 | heading 필수 — heading 없는 A+는 무효 |
| Curve | A → 안내점들 → B | A·B 사이 임의 개수의 안내점(type 9) | 곡선은 1차원 기하 프리미티브로, options에 달리 지정하지 않으면 동일 곡선 반복으로 간주. 자기 선 교차 허용 |
| Pivot | 중심점 1개 | 중심점 + A + B | A·B점은 비완전원의 시작/끝 각도 결정. options에 달리 지정하지 않으면 완전원 |
| Spiral | A → 안내점들 → B | A·B 사이 안내점(type 9) | |

동작 규칙:

- AB·A+·Curve 라인은 이전 라인과 평행하게 swathe width만큼 오프셋되어 생성된다. Spiral 라인은 이전 라인의 끝에서 이어지며 주로 헤드랜드에 쓰인다.
- 전파 방향(propagation direction)은 첫 점에 서서 둘째 점을 바라보는 기준으로 정의하며, GuidancePatternPropagationDirection·NumberOfSwathsLeft·BoundaryPolygon 정의는 서로 모순되면 안 된다.
- 수평/수직 정확도는 패턴 전체에 한 번 정의하거나 각 Point에 개별 정의할 수 있고, 둘 다 있으면 개별 Point 값이 우선한다.
- BoundaryPolygon은 패턴 라인이 전파되는 영역을 정의하며, 정의된 경우 해당 패턴이 속한 필드 경계 폴리곤 안에 들어가야 한다.
- 패턴은 기록 당시의 base station을 참조할 수 있지만, 모니터는 base station 참조 없이도 동작해야 한다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| GuidancePatternId | A | r | xs:ID | 고유 식별자 (`GPN` 형식, MICS는 음수) |
| GuidancePatternDesignator | B | o | 최대 32자 | 패턴 이름 |
| GuidancePatternType | C | r | 1~5 | 1=AB, 2=A+, 3=Curve, 4=Pivot, 5=Spiral |
| GuidancePatternOptions | D | o | 1~3 | Pivot용: 1=시계방향, 2=반시계방향, 3=완전원 |
| GuidancePatternPropagationDirection | E | o | 1~4 | 1=양방향, 2=왼쪽만, 3=오른쪽만, 4=전파 없음. 미정의 시 양방향 |
| GuidancePatternExtension | F | o | 1~4 | 라인 연장: 1=양끝, 2=A쪽만, 3=B쪽만, 4=없음. 미정의 시 양끝. 연장이란 패턴 끝점을 지나쳐도 안내 시스템이 안내를 계속하는 것 |
| GuidancePatternHeading | G | o | 0.0~360.0 | 진북 기준 시계방향 heading(도) |
| GuidancePatternRadius | H | o | 0~2³²−2 | Pivot 반지름(mm) |
| GuidancePatternGNSSMethod | I | o | 0~17 | NMEA 2000 GNSS Method 참조: 1=GNSS fix, 2=DGNSS, 3=Precise GNSS, 4=RTK Fixed Integer, 5=RTK Float, 6=DR, 7=수동 입력, 8=시뮬레이트, 16=데스크톱 생성, 17=기타 |
| GuidancePatternHorizontal/VerticalAccuracy | J, K | o | 0.0~65.0 | RMS 오차 추정치(m) |
| BaseStationIdRef | L | o | xs:IDREF | BaseStation 참조 |
| OriginalSRID | M | o | 32자 | 패턴 생성 시 좌표계/투영법의 WKID (예: `EPSG:4326`). GUI 재표현 보조용이며, 파일 세트 내 좌표는 항상 WGS-84로 기록 |
| NumberOfSwathsLeft / Right | N, O | o | 0~2³²−2 | 좌/우로 전파할 swath 수. 미정의 시 개수 제한 없이 PropagationDirection을 따름 |
| LineString | | r | 요소 | 단일 LineString 포함 |
| BoundaryPolygon | | o | 요소 | 패턴 유효 영역 제한 Polygon 목록 |

### D.31 GuidanceShift — GST

필드 작업 중 특정 안내 패턴에 적용된 이동(shift) 정보를 기록하는 task data 요소다(버전 4에서 추가). shift는 전파된 모든 패턴에 적용된다.

- EastShift/NorthShift의 전형적 용도는 측위 시스템 드리프트 보정이다. 직선·곡선·피벗 타입에는 패턴 평행 이동으로 적용되고, 스파이럴 타입에는 지정 패턴과 전파 패턴이 함께 이동한다.
- PropagationOffset은 전파된 패턴을 원 패턴에 수직 방향으로 오프셋한다. 직선 패턴에서는 NorthShift+EastShift 조합과 유사한 효과지만, 곡선·피벗·스파이럴에서는 전파 패턴이 이동되는 게 아니라 재생성된다는 점이 다르다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| GuidanceGroupIdRef | A | r | xs:IDREF | GuidanceGroup 참조. GuidanceGroup 또는 GuidancePattern 참조 중 하나는 필수 |
| GuidancePatternIdRef | B | r | xs:IDREF | GuidancePattern 참조 (위와 택일 관계) |
| GuidanceEastShift / NorthShift | C, D | o | −2³¹~2³¹−1 | A점 기준 투영 접평면상 이동량(mm) |
| PropagationOffset | E | o | −2³¹~2³¹−1 | 전파 오프셋(mm). 양수 = 패턴 오른쪽, 음수 = 왼쪽 |
| AllocationStamp | | o | 요소 | 단일 AllocationStamp 포함 |

### D.32 ISO11783_TaskData (루트 요소)

XML 파일의 루트 요소로, 파일 구성 정보(버전 번호 등)와 1차 XML 요소들의 사용을 정의한다.

주요 속성:

| 속성 | 필수 | 범위 | 설명 |
| --- | --- | --- | --- |
| VersionMajor | r | 0~4 | 이 태스크 데이터 파일이 준수하는 ISO 11783-10 버전. 0=DIS, 1=FDIS.1, 2=FDIS.2/1판 IS, 3=2판 DIS, 4=2판 FDIS |
| VersionMinor | r | 0~99 | XML 스키마 리비전 번호 |
| ManagementSoftwareManufacturer / Version | o/r | 32자 | 관리 소프트웨어 제조사·버전 |
| TaskControllerManufacturer / Version | o/r | 32자 | TC 제조사·버전. FMIS가 생성한 파일에서는 쓰지 않고, MICS 생성 파일에서는 필수 |
| DataTransferOrigin | r | 1~2 | 파일 세트를 마지막으로 생성한 시스템: 1=FMIS, 2=MICS |
| DataTransferLanguage (lang) | o | 32자 | 생성 시스템이 사용한 언어(버전 4 추가) |

포함 가능한 하위 요소(모두 선택): AttachedFile(AFE), BaseStation(BSN), CodedComment(CCT), CodedCommentGroup(CCG), ColourLegend(CLD), CropType(CTP), CulturalPractice(CPC), Customer(CTR), Device(DVC), Farm(FRM), OperationTechnique(OTQ), Partfield(PFD), Product(PDT), ProductGroup(PGP), Task(TSK), TaskControllerCapabilities(TCC, 버전 4 추가·MICS 생성 시 필수), ValuePresentation(VPN), Worker(WKR), ExternalFileReference(XFR).

### D.33 LineString — LSG

선의 위치·길이·모양을 기술하는 task data 요소다. Point 요소들을 나열 순서대로 이어 그린다.

- flag 타입 LineString은 라인 전체 위치에 코멘트를 붙이는 용도다. FMIS 쪽에서 만든 코멘트(LineStringDesignator에 저장)를 TC가 특정 위치에서 작업자에게 안내 메시지로 표시할 수 있게 한다.
- 폴리곤 외곽/내부 경계(타입 1·2)인 LineString은 닫혀 있어야 하며, GML 방식대로 첫 Point를 마지막 Point로 반복해 닫는다. 버전 4 이전(버전 2·3)에는 첫 점을 마지막에 반복할 필요 없이 마지막 점과 첫 점 사이에 선을 그리는 방식이었다는 점에 주의한다.
- LineStringId 속성은 LineString이 Polygon이나 GuidancePattern의 자식이 아닐 때만 사용한다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| LineStringType | A | r | 1~9 | 1=PolygonExterior, 2=PolygonInterior, 3=TramLine, 4=SamplingRoute, 5=GuidancePattern, 6=Drainage, 7=Fence, 8=Flag, 9=Obstacle(버전 4 추가, 접근 경고 생성 등) |
| LineStringDesignator | B | o | 최대 32자 | 이름 또는 코멘트 |
| LineStringWidth | C | o | 0~2³²−2 | 실세계 폭(mm). 타입 5에서는 안내 패턴 인접 경로 간 swathe width |
| LineStringLength | D | o | 0~2³²−2 | 실세계 길이(mm) |
| LineStringColour | E | o | 0~254 | 색상(ISO 11783-6 팔레트) |
| LineStringId | F | o | xs:ID | 고유 식별자(버전 4 추가, `LSG` 형식, MICS는 음수) |
| Point | | r | 요소 | Point 목록 |

### D.34 OperationTechnique — OTQ / D.35 OperationTechniqueReference — OTR

OperationTechnique는 "drilling", "spreading", "gaseous" 같은 작업 기법을 기술하는 coding data 요소다. 속성은 OperationTechniqueId(A, 필수, `OTQ` 형식)와 OperationTechniqueDesignator(B, 필수, 최대 32자) 둘뿐이다. OperTechPractice와 OperationTechniqueReference가 이를 참조한다.

OperationTechniqueReference는 단일 OperationTechnique에 대한 참조를 담는 coding data 요소로, CulturalPractice에 포함된다. 속성은 OperationTechniqueIdRef(A, 필수, xs:IDREF) 하나다.

### D.36 OperTechPractice — OTP

특정 operation technique과 단일 cultural practice의 조합을 Task에 할당하는 task data 요소다. Task에 포함된다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| CulturalPracticeIdRef | A | r | xs:IDREF | CulturalPractice 참조 (`CPC` 형식) |
| OperationTechniqueIdRef | B | o | xs:IDREF | OperationTechnique 참조 (`OTQ` 형식) |

### D.37 Partfield — PFD

Task를 할당할 수 있는 토지 단위를 기술하는 coding data 요소다. Partfield는 하나의 단위로 취급(처리)될 것이 확정되는 시점에 생성되는 동적 객체다.

- Partfield는 나지(bare)이거나 하나의 CropType으로 재배 중이다. 간작(undersown crop)의 경우 주 작물만 기재한다. 새 작물 생산 단위가 시작되거나 이웃 Partfield와 합쳐지면 Partfield는 종료된다.
- 필드 전체일 수도, 필드의 일부일 수도 있다. 여러 조각의 토지로 구성될 경우 조각들은 서로 가까이(예: 좁은 띠로만 분리) 있어야 하고, 각 조각은 단일 Polygon으로 경계 지어진다. 버전 4 이전에는 Partfield에 경계 Polygon 1개만 넣을 수 있었지만 버전 4부터는 여러 Polygon을 넣을 수 있다.
- Partfield는 TreatmentZone과 무관한 Polygon·LineString·Point만 참조할 수 있다.
- Partfield는 다른 Partfield의 자식이 될 수 있다. 재귀 깊이는 2단계로 제한되고, 부모는 1개까지만 가지며 그 부모는 또 다른 Partfield의 자식일 수 없다. 용례: 한 필드의 서로 다른 구역에 심은 두 품종을 추적할 때 부모 Partfield가 작물 종을, 자식 Partfield들이 개별 품종을 기재한다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| PartfieldId | A | r | xs:ID | 고유 식별자 (`PFD` 형식, MICS는 음수) |
| PartfieldCode | B | o | 최대 32자 | FMIS의 필드 번호 |
| PartfieldDesignator | C | r | 최대 32자 | 필드 이름 |
| PartfieldArea | D | r | 0~2³²−2 | 면적(m²) |
| CustomerIdRef / FarmIdRef | E, F | o | xs:IDREF | Customer/Farm 참조 |
| CropTypeIdRef / CropVarietyIdRef | G, H | o | xs:IDREF | 작물 종/품종 참조 |
| FieldIdRef | I | o | xs:IDREF | 부모 Partfield 참조 |
| Polygon / LineString / Point / GuidanceGroup | | o | 요소 | 각 요소 목록 |

### D.38 Point — PNT

점 위치와 모양을 기술하는 task data 요소다. flag 타입 점은 그 위치에 코멘트를 붙이는 용도로, PointDesignator에 저장된 FMIS 쪽 코멘트를 TC가 안내 메시지로 표시할 수 있다. PointId는 Point가 LineString의 자식이 아닐 때만 사용한다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| PointType | A | r | 1~11 | 1=Flag, 2=other, 3=Field Access(필드 진입점), 4=Storage(자재 보관 위치), 5=Obstacle, 6=Guidance Reference A, 7=Guidance Reference B, 8=Guidance Reference Center(피벗 중심), 9=Guidance Point(A/B/Center 외 안내점), 10=Partfield Reference Point(관리용 필드 식별 위치), 11=Homebase — 3~11은 버전 4 추가 |
| PointDesignator | B | o | 최대 32자 | 이름·설명·코멘트 |
| PointNorth / PointEast | C, D | r | ±90.0 / ±180.0 | WGS84 위도/경도 |
| PointUp | E | o | xs:long | 고도(mm, WGS84 타원체 기준) |
| PointColour | F | o | 0~254 | 색상(ISO 11783-6 팔레트) |
| PointId | G | o | xs:ID | 고유 식별자(버전 4 추가) |
| PointHorizontal/VerticalAccuracy | H, I | o | 0.0~65.0 | RMS 오차(m)(버전 4 추가) |
| Filename / Filelength | J, K | o | `PNT[0-9]{5}` / 바이트 | 점 바이너리 파일 이름·길이(버전 4 추가) |

버전 4부터 Point들을 XML 대신 바이너리 파일(`PNT00001` 등)로 담을 수 있다. 이때 XML의 PNT 요소는 C·D·E 값을 비워 두고 J(파일명)·K(길이)로 바이너리 파일을 가리킨다.

### D.39 Polygon — PLN

LineString들을 포함해 면적을 기술하는 task data 요소다. Partfield 경계나 TreatmentZone 영역 지정에 쓴다.

- 버전 4 이전에는 하나의 Polygon에 여러 외곽 경계 LineString을 넣을 수 있었지만, 버전 4부터 Polygon은 GML의 폴리곤 정의에 맞는 단일 표면만 기술한다.
- LineString 포함 규칙: 외곽 경계(outer boundary) 타입은 최대 1개, 내부 경계(inner boundary) 타입은 여러 개 가능하다. 내부 경계는 외곽 경계나 다른 내부 경계를 가로지르면 안 되고, 맞닿는 것은 허용된다.
- flag 타입 Polygon은 폴리곤 내부 전체 위치에 코멘트(PolygonDesignator)를 붙이는 용도다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| PolygonType | A | r | 1~12 | 1=Partfield Boundary, 2=TreatmentZone, 3=WaterSurface, 4=Building, 5=Road, 6=Obstacle, 7=Flag, 8=Other, 9=Mainfield(경작에 쓰는 주 영역), 10=Headland(선회 영역, 보통 주 영역과 다른 방향으로 파종), 11=BufferZone(환경 규제로 달리 처리해야 하는 영역), 12=Windbreak — 9~12는 버전 4 추가. Mainfield = Partfield 경계 − 장애물·수면·헤드랜드 |
| PolygonDesignator | B | o | 최대 32자 | 이름 |
| PolygonArea | C | o | 0~2³²−2 | 면적(m²) |
| PolygonColour | D | o | 0~254 | 색상(ISO 11783-6 팔레트) |
| PolygonId | E | o | xs:ID | 고유 식별자(버전 4 추가) |
| LineString | | r | 요소 | LineString 목록 |

### D.40 Position — PTN

측정된 위치를 기술하는 task data 요소다. AllocationStamp 또는 Time 명세의 일부로 쓰이며, Time과 함께 쓰면 DataLogValue를 위치와 함께 로깅하는 데 활용된다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| PositionNorth / PositionEast | A, B | r | ±90.0 / ±180.0 | WGS84 위도/경도 |
| PositionUp | C | o | −2³¹~2³¹−1 | 고도(mm, WGS84 타원체) |
| PositionStatus | D | r | 0~15 | NMEA2000 GNSS Method 참조: 0=no GPS fix, 1=GNSS fix, 2=DGNSS, 3=Precise GNSS, 4=RTK fixed integer, 5=RTK float, 6=Est(DR), 7=수동 입력, 8=시뮬레이트, 9~13=예약, 14=Error, 15=값 없음 |
| PDOP / HDOP | E, F | o | 0.0~99.9 | 품질 정보 |
| NumberOfSatellites | G | o | 0~254 | 사용 위성 수 |
| GpsUtcTime | H | o | 0~2³²−2 | 자정 이후 UTC 밀리초 |
| GpsUtcDate | I | o | 0~2¹⁶−2 | 1980-01-01 기준 일수 |

### D.41 ProcessDataVariable — PDV

TreatmentZone에 포함되는 task data 요소로, ProcessDataDDI와 그 값, 그리고 이 TreatmentZone에서 사용할 선택적 product·device element 정보를 담는다.

<strong>중첩 구조</strong>: PDV는 다른 PDV를 담을 수 있다. 이는 하나의 DeviceElement에 여러 product를 계획 할당하는 것을 기술하기 위한 구조다 — "부모" PDV가 TC가 DeviceElement로 보낼 ProcessDataDDI를 지정하고, "자식" PDV들이 product 명세를 담는다. 자식 PDV는 또 다른 PDV를 담을 수 없고 DeviceElementIdRef도 지정하면 안 된다.

<strong>버전 4의 그룹화 속성</strong>: ActualCulturalPracticeValue와 ElementTypeInstanceValue는 프로세스 데이터 값을 특정 작업(operation)이나 특정 element type 인스턴스에 할당·추적하기 위해 도입됐다. 한 Task 안에 여러 작업(예: 파종 + 시비 동시 제어)이나 같은 device element 타입의 여러 인스턴스가 있을 때 PDV 세트를 구분할 수 있게 한다. 버전별 그룹화 방법 정리:

- <strong>버전 3 이전</strong>: ① ProductIdRef로 제품별 그룹화(실제 product가 파일 세트에 있어야 함) ② DeviceElementIdRef로 기계 요소별 그룹화(실제 기계의 device descriptor가 파일 세트에 있어야 함) — 즉 실제 장비에 미리 할당해야만 그룹화 가능했다.
- <strong>버전 4 이후</strong>: ① 제품이 알려져 있으면 ProductIdRef로 그룹화 ② ActualCulturalPracticeValue로 작업별 그룹화 — device element가 ActualCulturalPractice DDI 값을 가지면 작업과 올바른 device element의 자동 매칭 가능 ③ 같은 DDI·ActualCulturalPracticeValue를 갖는 PDV들을 ElementTypeInstanceValue로 계획된 제어 대상 인스턴스별 그룹화 — 실제 장비 사전 할당 없이 rate controller 인스턴스별 그룹화 가능 ④ Task 실행 중 실제 기계가 선택되면 DeviceElementIdRef를 갱신해 할당을 저장할 수 있다.

DeviceElementIdRef는 선택 속성이다. TC 구현은 일치하는 ProcessDataDDI를 가진 device descriptor를 보유하고 이 PDV를 setpoint로 받을 수 있는 연결된 클라이언트에 PDV를 할당할 수 있어야 하며, ProductIdRef·ActualCulturalPracticeValue·ElementTypeInstanceId 그룹화가 이 할당 과정을 보조한다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| ProcessDataDDI | A | r | 0000₁₆~FFFF₁₆ | ISO 11783-11에 정의된 DDI |
| ProcessDataValue | B | r | −2³¹~2³¹−1 | DDI 값 |
| ProductIdRef | C | o | xs:IDREF | Product 참조 |
| DeviceElementIdRef | D | o | xs:IDREF | DeviceElement 참조 |
| ValuePresentationIdRef | E | o | xs:IDREF | ValuePresentation 참조 |
| ActualCulturalPracticeValue | F | o | xs:long | 계획/할당 대상 ActualCulturalPractice DDI 값(버전 4 추가) |
| ElementTypeInstanceValue | G | o | xs:long | 계획/할당 대상 ElementTypeInstance DDI 값(버전 4 추가) |
| ProcessDataVariable | | o | 요소 | 자식 PDV 목록 |

:::info 예시로 보는 활용
표준의 예시들은 다음 시나리오를 다룬다. ① Product+DeviceElement를 참조하는 setpoint 지정(DDI 6 = Setpoint Mass Per Area Application Rate, 15000 mg/m² = 150 kg/ha), ② 시비·파종 두 작업을 ActualCulturalPracticeValue로 구분하고 폴리곤 기반 위치 제어, ③ 비료 빈 2개 + 종자 빈 1개 플랜터에서 ActualCulturalPracticeValue + ElementTypeInstanceValue로 작업·빈 구분, ④ 같은 구성을 grid type 2로 지정, ⑤ 두 품종을 동시에 파종하는 2빈 장비에서 ElementTypeInstanceValue로 품종별 setpoint 구분.
:::

### D.42 Product — PDT

단일 제품, 제품 혼합물(mixture), 작물 품종의 산출물 또는 파종 자재를 기술하는 coding data 요소다. Product는 ProductGroup에 속할 수 있고, 품종 산출물·파종 자재를 정의하는 Product는 "CropType" 타입의 ProductGroup으로 묶는다. 특정 ProductGroup 소속 여부는 각 Product의 ProductGroupIdRef를 대조해 판별한다. Product는 태스크에서 사용되는 제품(작물보호제 등)과 태스크가 생산하는 제품(농산물) 모두를 가리킨다.

<strong>수량 표현</strong>: ValuePresentationIdRef와 QuantityDDI로 제품 수량의 표시와 정의를 지정한다. QuantityDDI에는 DDI 72(Actual Volume Content, ml), 75(Actual Mass Content, g), 78(Actual Count Content, count)을 사용해야 하며, 이 단위는 제품 적용 제어에 필요한 setpoint application rate DDI 단위 선택에도 쓰인다.

<strong>혼합물 규칙</strong>:

- ProductType으로 단일/혼합을 지정하며 미정의 시 기본값은 single이다.
- MixtureRecipeQuantity는 특정 태스크의 수량이 아니라 혼합 레시피의 총량이며, 모든 성분 수량의 합과 같아야 한다(예: 성분을 1/1000 단위로 지정하면 1000).
- 내장 ProductRelation들이 혼합물의 성분을 정의한다. single 타입 제품에는 ProductRelation을 쓰면 안 되고, ProductRelation은 mixture 타입 제품을 참조하면 안 된다(혼합물의 혼합물 금지).
- ProductRelation이 참조하는 single 제품에는 QuantityDDI가 지정돼 있어야 하고, 참조된 제품이 mixture라면 QuantityDDI와 MixtureRecipeQuantity를 모두 가져야 한다.
- FMIS/MICS 제품 목록에서 재사용·선택 가능하게 만들 혼합물은 "Mixture" 타입, 현장에서 재사용 의도 없이 만들어져 문서화만 필요하고 목록에서 선택은 불가능해야 하는 혼합물은 "TemporaryMixture" 타입을 쓴다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| ProductId | A | r | xs:ID | 고유 식별자 (`PDT` 형식, MICS는 음수) |
| ProductDesignator | B | r | 최대 32자 | 제품 이름 |
| ProductGroupIdRef | C | o | xs:IDREF | ProductGroup 참조 |
| ValuePresentationIdRef | D | o | xs:IDREF | ValuePresentation 참조 |
| QuantityDDI | E | o | hexBinary | 수량 DDI |
| ProductType | F | o | 1~3 | 1=Single(기본), 2=Mixture, 3=TemporaryMixture(버전 4 추가) |
| MixtureRecipeQuantity | G | o | 0~2³¹−1 | 레시피 성분 합계 수량(버전 4 추가) |
| DensityMassPerVolume | H | o | 0~2³¹−1 | 밀도 mg/l (DDI 121 대응, 버전 4 추가) |
| DensityMassPerCount | I | o | 0~2³¹−1 | 밀도 mg/1000 (DDI 122 대응, 버전 4 추가) |
| DensityVolumePerCount | J | o | 0~2³¹−1 | 밀도 ml/1000 (DDI 123 대응, 버전 4 추가) |
| ProductRelation | | o | 요소 | ProductType 2·3일 때 성분 목록(버전 4 추가) |

:::details 혼합물 계산 방식 (표준 예시 요약)
혼합물 적용 후 성분별 소모량은 FMIS가 배율로 계산한다. 예: 100 l 레시피(제품10 80 l + 제품20 20 l + 제품24 0.5 kg 완전 용해)의 혼합물을 7600 l 적용했다면 f = 7600/100 = 76이고, 각 성분 소모량은 ProductRelation의 QuantityValue × 76으로 구한다. 고체가 부피를 늘리는 경우(물 498 l + 건조 약품 22.5 kg → 500 l)나 고체 혼합물(질량 기준 레시피), 밀도 속성(H)을 이용해 태스크 setpoint 단위(질량/면적)와 장비 계량 단위(부피 기반)를 환산하는 예시도 제시된다. 액체 밀도 정보가 없으면 올바른 MixtureQuantity·MixtureDensity 계산은 운전자나 FMIS의 몫이다.
:::

### D.43 ProductAllocation — PAN

단일 제품의 태스크 할당을 지정하는 task data 요소다. 선택적으로 DeviceElement와 연관시켜 하나 또는 여러 제품이 빈(bin) 등 특정 DeviceElement에 할당된 것을 추적할 수 있다. 이동 수량은 QuantityDDI(72/75/78) + QuantityValue 조합으로 지정한다.

- "filling"·"emptying" 타입은 이동 수량(빈에 들어가거나 나온 양)을, "remainder" 타입은 절대 수량(빈에 남은 양)을 쓴다.
- 총계(totals)로 product allocation을 정의하면 TC가 실제 filling/emptying/remainder QuantityValue를 계산해야 한다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| ProductIdRef | A | r | xs:IDREF | Product 참조 |
| QuantityDDI | B | o | hexBinary | 수량 DDI |
| QuantityValue | C | o | 0~2³¹−1 | 이동량(filling/emptying) 또는 빈 잔량(remainder) |
| TransferMode | D | o | 1~3 | 1=Filling, 2=Emptying, 3=Remainder(버전 4 추가) |
| DeviceElementIdRef | E | o | xs:IDREF | DeviceElement 참조 |
| ValuePresentationIdRef | F | o | xs:IDREF | ValuePresentation 참조 |
| AllocationStamp | | o | 요소 | 단일 AllocationStamp |

:::info PAN으로 제품 소모량 계산하기 (표준 예시 요약)
태스크 실행 중 장비의 제품(혼합물)이 바뀌면 FMIS는 PAN 요소들에 의존해 제품별 수량을 계산해야 한다 — 태스크 TIM 요소의 장비 총계는 제품 구분이 없기 때문이다. 태스크 시작 시 type 3(remainder) PAN이 없으면 FMIS는 잔량 0으로 가정하고, 태스크 종료 시에도 마무리 remainder PAN이 없으면 탱크가 비었다고 가정한다.

표준 예시의 흐름: 계획(50 l filling) → 시작 시 잔량 2 l → 50 l까지 채움(48 l 주입) → 잔량 10 l(40 l 적용됨) → 재충전 50 l → 제품 교체 시 잔량 0 → 새 제품 30 l 주입 → 종료(마무리 remainder 없음 → 30 l 모두 적용으로 간주). 결과적으로 PDT250 90 l + PDT258 30 l 적용, TIM의 DLV 총계는 120 l가 된다.
:::

### D.44 ProductGroup — PGP

제품 또는 작물 품종의 산출물·파종 자재를 묶는 coding data 요소다. 태스크 실행 중 ProductAllocation을 태스크에 추가하는 방식으로 제품을 할당할 수 있고, 이렇게 하면 태스크 활성 중의 제품 할당·품종 명세 변경이 모두 기록된다. 소속 판별은 각 Product의 ProductGroupIdRef를 ProductGroupId와 대조하는 방식이다. CropType 타입 ProductGroup과 일치하는 제품들의 집합이 특정 작물 종의 품종 집합을 정의하며, CropType·CropVariety 요소와 ProductGroup·Product 요소 간 교차 참조로 Partfield의 작물과 Product의 상품(commodity)을 연결할 수 있다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| ProductGroupId | A | r | xs:ID | 고유 식별자 (`PGP` 형식, MICS는 음수) |
| ProductGroupDesignator | B | r | 최대 32자 | 그룹 이름 |
| ProductGroupType | C | o | 1~2 | 1=ProductGroup(기본, 제품 그룹), 2=CropType(작물 품종 그룹). 버전 4 추가 |

### D.45 ProductRelation — PRN

단일 제품을 혼합물 제품 정의에 할당하는 coding data 요소다(버전 4 추가). QuantityValue가 이 제품이 혼합물에서 차지하는 몫을 정의한다.

- PRN이 참조하는 Product는 QuantityDDI·MixtureQuantity 값을 가져야 한다(성분 비율 계산을 위해).
- PRN이 참조하는 Product는 혼합물 정의이면 안 된다(다단계 혼합물 금지).
- PRN이 참조하는 Product는 PRN을 포함한 Product 자신이면 안 된다(순환 참조 금지).
- 펠릿 안에 N-P-K-S 등을 결합한 복합 비료는 단일 제품으로 본다. 농장에서 단일 성분 비료들을 배합했다면 혼합물로 본다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| ProductIdRef | A | r | xs:IDREF | 성분 Product 참조 |
| QuantityValue | B | r | 0~2³¹−1 | 혼합물 내 몫 |

### D.46 Task — TSK

ISO 11783 태스크를 기술하는 task data 요소로, <strong>데이터 전송 파일 세트의 중심 요소</strong>다. 다양한 요소를 참조해 자원·작업 할당을 지정하고 기록한다.

- Task에 CustomerIdRef·FarmIdRef·PartfieldIdRef를 지정하면 태스크-고객-농장-필드 간 중복 관계가 생긴다. 이 중복은 허용되지만 요소 간 관계에 모순을 만들면 안 된다.
- ResponsibleWorkerIdRef는 이 태스크의 책임자(태스크를 지정한 사람 또는 상세 문의 가능한 사람) 참조다. 작업 기여자의 시작 시각·기간 기록은 WorkerAllocation으로 하며 한 태스크에 여러 개 지정 가능하다.
- TaskStatus 1~4·6이 태스크 생애주기를 나타내고, 5(template)는 특수 상태다 — template 태스크를 시작하면 그 복사본인 새 태스크가 생성·시작된다.
- MICS가 태스크를 시작했고 ISO 11783 네트워크에 시간 정보가 있으면 Time 요소를 최소 1개 추가해야 한다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| TaskId | A | r | xs:ID | 고유 식별자 (`TSK` 형식, MICS는 음수) |
| TaskDesignator | B | o | 최대 32자 | 태스크 이름 |
| CustomerIdRef / FarmIdRef / PartfieldIdRef | C, D, E | o | xs:IDREF | 고객/농장/필드 참조 |
| ResponsibleWorkerIdRef | F | o | xs:IDREF | 책임 Worker 참조 |
| TaskStatus | G | r | 1~6 | 1=planned, 2=running, 3=paused, 4=completed, 5=template, 6=canceled (5·6은 버전 4 추가) |
| DefaultTreatmentZoneCode | H | o | 0~254 | 기본 TreatmentZone 참조 |
| PositionLostTreatmentZoneCode | I | o | 0~254 | 측위 상실 시 TreatmentZone 참조 |
| OutOfFieldTreatmentZoneCode | J | o | 0~254 | 필드 밖 TreatmentZone 참조 |

포함 요소(모두 선택): TreatmentZone, Time, OperTechPractice(단일), WorkerAllocation, DeviceAllocation, Connection, ProductAllocation, DataLogTrigger, CommentAllocation, TimeLog, Grid(단일), ControlAssignment(버전 4), GuidanceAllocation(버전 4).

### D.47 TaskControllerCapabilities — TCC

데이터 전송 파일 세트를 생성한 TC의 구현 버전과 능력을 담는 요소다(버전 4 추가). 데이터 전송 출처가 MICS일 때만 파일 세트에 포함되며, 그 경우에도 최대 1개만 포함한다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| TaskControllerControlFunctionNAME | A | r | hexBinary | TC의 NAME (ISO 11783-5 참조) |
| TaskControllerDesignator | B | r | 최대 153자 | 제조사 제공 제품명 (ISO 11783-12 Product Identification 파라미터 그룹) |
| VersionNumber | C | r | 0~4 | TC가 준수하는 ISO 11783-10 버전 (0=DIS ~ 4=E2.FDIS) |
| ProvidedCapabilities | D | r | 0~63 | 비트 조합: 1=문서화(documentation), 2=위치 기반 제어 없는 TC-GEO, 4=위치 기반 제어 있는 TC-GEO, 8=peer control assignment, 16=implement section control, 32=폴리곤 처방 맵 |
| NumberOfBoomsSectionControl | E | r | 0~254 | 섹션 제어 지원 최대 붐 수(미지원 시 0) |
| NumberOfSectionsSectionControl | F | r | 0~254 | 섹션 제어 지원 최대 섹션 수(미지원 시 0) |
| NumberOfControlChannels | G | r | 0~254 | 지원 제어 채널 수(미지원 시 0) |

### D.48 Time — TIM

시간 이벤트의 기록을 지정하는 task data 요소다. 선택적으로 시각과 함께 위치를 기록할 수 있고, Type 속성이 어떤 종류의 시간인지 지정한다.

- FMIS가 제공하는 Time은 모두 type 1(planned)이어야 한다. planned Time은 태스크의 계획 시작/종료 또는 기간을 지정하며 계획·스케줄링 전용이고, 태스크당 최대 1개다.
- MICS가 type 2(Preliminary)~8(Powered Down)로 상세한 시간 구분을 제공하지 않는 경우, MICS 제공 Time은 모두 type 4(Effective)여야 한다. 이때 기록된 effective 시간의 합이 총 작업 시간이며 더 세부적인 시간 유형으로 분해할 수 없다. 세부 시간 유형은 Annex G에 설명된다.
- type 8(Powered Down)은 TC가 속한 기계의 전원 차단 시각 기록용이다(버전 4 추가).
- 모든 Time은 Start 속성이 정의돼야 한다. Duration은 항상 양수이며 Start와 Stop 사이 경과 시간과 같다. 유한한 Time은 Start+Stop(Duration 계산 가능) 또는 Start+Duration(Stop 계산 가능)으로 지정하며, Start만 기록하는 무한 Time도 허용된다.
- Type 3(Preparation)은 버전 4에서 폐기(deprecated)됐다 — type 2(Preliminary) 대비 추가 정보가 없었기 때문이다.

<strong>타임존 처리(버전 4)</strong>: datetime 타입이 타임존 정보를 포함하거나 명시적 UTC로 확장됐다. 타임존을 아는 경우 "Z" 표기로 UTC를 지정하거나 start/stop 속성에 타임존 오프셋을 포함해야 한다. 이는 FMIS가 여러 타임존에서 온 데이터를 정규화할 때 필요하다. 타임존 정보가 전혀 없으면 모든 시각은 타임존 없는 로컬 시간으로 표현한다. 버전 4 이전에는 TimeLog 바이너리에 UTC와 로컬 시간이 모두 기록된 경우에만 (로컬 − UTC 차로) 타임존을 역산할 수 있었고, 계산된 타임존은 같은 파일 세트의 모든 타임스탬프에 적용할 수 있다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| Start | A | r | xs:datetime | 시작 시각 `yyyy-mm-ddThh:mm:ss.sss` + 선택적 타임존 |
| Stop | B | o | xs:datetime | 종료 시각 (Stop 또는 Duration 중 하나로 유한화) |
| Duration | C | o | 0~2³²−2 | 시작~종료 초 |
| Type | D | r | 1~2, 4~8 | 1=Planned, 2=Preliminary, 4=Effective, 5=Ineffective, 6=Repair, 7=Clearing, 8=Powered Down |
| Position | | o | 요소 | 최대 2개 — Start·Stop 시각의 위치 |
| DataLogValue | | o | 요소 | DataLogValue 목록 |

### D.49 TimeLog — TLG

Time 요소는 XML 파일 안의 내장 리스트로 쓰이거나, TimeLog 안의 <strong>시간 템플릿 명세</strong>로 쓰인다. TimeLog는 모든 DataLogValue를 바이너리 데이터 로그 파일로 수집할 수 있게 한다. TimeLog 안에서 Time의 TimeType은 4(effective)여야 한다. TimeLogType은 로깅 방식의 향후 확장을 위한 속성으로, 현행 방식(6.8.2·6.8.4에 규정)은 값 1이다.

TimeLog는 항상 태스크에 속하며 고유 이름의 파일 2개 세트(XML 헤더 + 바이너리)를 가리킨다. 두 파일은 파일 세트의 다른 파일들과 같은 디렉터리에 있어야 하고, 이름은 파일 세트의 모든 태스크가 참조하는 TimeLog 전체에서 유일해야 한다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| Filename | A | r | xs:ID, 8자 | `TLG[0-9]{5}` 형식 |
| Filelength | B | o | 0~2³²−2 | 바이너리 파일 바이트 길이 |
| TimeLogType | C | r | 1 | 1 = binary timelog file type 1 |

동작 원리: `TLG00001.xml` 같은 헤더 파일에 TIM 템플릿을 넣되, 값이 채워진 속성은 바이너리 전 레코드에 걸친 고정값으로, 빈 문자열(`A=""`)인 속성은 레코드마다 바이너리에 기록되는 가변값으로 해석한다. 예를 들어 템플릿이 TimeStart·위치(북/동)·PositionStatus를 비워 두고 DLV 2개를 선언하면, 바이너리 레코드는 (TimeStart, PositionNorth, PositionEast, PositionStatus, #DLV, DLV0, PDV0, DLV1, PDV1) 구조가 된다.

### D.50 TreatmentZone — TZN

같은 process data DDI들과 같은 값으로 처리할 영역을 기술하는 task data 요소다.

태스크 안에서 특수 의미를 갖는 TreatmentZone 참조가 3가지 있다.

- <strong>DefaultTreatmentZone</strong>: 포함된 PDV 값을 태스크 전체에 전역 적용한다. 태스크 시작·재개 시 TC가 이 안의 모든 PDV 값을 해당하는 모든 클라이언트로 전송한다. 폴리곤·그리드가 없는 비위치특정(non-site-specific) 태스크에도 존재할 수 있다.
- <strong>PositionLostTreatmentZone</strong>: 측위가 불가능해졌을 때 클라이언트로 보낼 PDV들을 담는다.
- <strong>OutOfFieldTreatmentZone</strong>: 클라이언트(의 일부)가 필드 경계 폴리곤 영역을 벗어났을 때 해당 device element로 보낼 PDV들을 담는다.

PositionLost·OutOfField는 위치특정(site-specific) 태스크용이다.

기하 규칙: 버전 4 이전에는 TreatmentZone에 Polygon 1개만 넣을 수 있었지만 버전 4부터 Polygon 목록이 가능하며 각 Polygon은 단일 표면만 기술한다. 기하가 폴리곤으로 정의된 TreatmentZone에는 PDV를 <strong>1개만</strong> 넣어야 한다(버전 4에서 리스트→단일로 변경). 기하 정의가 없는 TreatmentZone(Grid나 Task 속성에서 참조되는 것)은 PDV 목록을 가질 수 있다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| TreatmentZoneCode | A | r | 0~254 | 태스크 내 고유 코드 |
| TreatmentZoneDesignator | B | o | 최대 32자 | 이름 |
| TreatmentZoneColour | C | o | 0~254 | 색상(ISO 11783-6 팔레트) |
| Polygon | | o | 요소 | TreatmentZone 타입 Polygon 목록 |
| ProcessDataVariable | | o | 요소 | 단일 또는 목록(위 규칙 참조) |

### D.51 ValuePresentation — VPN

데이터 딕셔너리 정의 정수 값의 표시 방식을 지정하는 coding data 요소다. 표시 공식은 <strong>표시값 = (정수값 + Offset) × Scale</strong>이고, 표시값은 항상 NumberOfDecimals 자리로 반올림한다. (장치 내부용인 DeviceValuePresentation과 동일 공식이다.)

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| ValuePresentationId | A | r | xs:ID | 고유 식별자 (`VPN` 형식) |
| Offset | B | r | −2³¹~2³¹−1 | 표시용 오프셋 |
| Scale | C | r | 0.000000001~100000000.0 | 표시용 배율 |
| NumberOfDecimals | D | r | 0~7 | 소수점 이하 자릿수 |
| UnitDesignator | E | o | 최대 32자 | 단위 문자열 |
| ColourLegendIdRef | F | o | xs:IDREF | ColourLegend 참조 |

### D.52 Worker — WKR / D.53 WorkerAllocation — WAN

Worker는 태스크가 참조할 수 있는 작업자를 기술하는 coding data 요소다. 모든 작업자 할당은 파일 세트 안에 시간 정보와 함께 로깅된다. 태스크 속성 ResponsibleWorkerIdRef가 참조하는 작업자는 추가 로깅 데이터 없이 태스크에서 직접 참조된다는 특수 의미가 있다.

Worker 속성: WorkerId(A, 필수), WorkerLastName(B, 필수, 최대 32자), WorkerFirstName(C, o), 주소 필드(D~I: Street/POBox/PostalCode/City/State/Country), WorkerPhone(J)·WorkerMobile(K, 최대 20자), WorkerLicenseNumber(L), WorkerEmail(M, 최대 64자).

WorkerAllocation은 작업자의 태스크 할당을 기술하는 task data 요소다. AllocationStamp가 할당의 시작/종료 시각과 태스크 내 할당 변경을 기록한다. 속성은 WorkerIdRef(A, 필수)와 단일 AllocationStamp(선택)다.

### D.54 ExternalFileContents — XFC / D.55 ExternalFileReference — XFR

ExternalFileContents는 메인 XML 전송 파일 외부에 있는 XML 파일의 모든 요소를 묶어 외부 파일을 well-formed로 유지하기 위한 요소다. CodedCommentGroup, CodedComment, ColourLegend, CulturalPractice, CropType, Customer, Device, Farm, OperationTechnique, Product, Partfield, ProductGroup, Task, ValuePresentation, Worker를 담을 수 있다.

ExternalFileReference는 메인 XML 파일에서 외부 XML 파일을 참조하는 요소다. 규칙:

- 외부 파일은 최상위 요소(ISO11783_TaskData에 넣을 수 있는 요소)만 담을 수 있다.
- 외부 파일 하나에는 <strong>한 가지 타입</strong>의 XML 요소만 넣을 수 있다.
- XFR의 재귀 사용 금지, XFC의 재귀 사용 금지.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| Filename | A | r | xs:ID, 8자 | `(CCG\|CCT\|CLD\|CPC\|CTP\|CTR\|DVC\|FRM\|OTQ\|PDT\|PFD\|PGP\|TSK\|VPN\|WKR)[0-9]{5}` 형식 (예: `TSK00001`) |
| Filetype | B | r | 1 | 1 = XML |

## 부속서 E (규범) — 사전 정의 ISO 11783 첨부 파일

### E.1 Link List 개요

FMIS와 MICS가 XML 데이터 세트의 객체에 대한 <strong>추가 키 정보</strong>를 교환하고 싶은 상황이 있다. 사전 정의 첨부물인 Link List는 파일 세트의 XML 요소를 하나 이상의 추가 키 값과 연관시키는 표준 방법을 제공한다. 이 관계의 전제 조건은 객체 ID의 존재다. XML 요소 객체 ID와 추가 키 값 사이의 연관("매핑")은 별도 파일인 링크 리스트 파일에 저장하며, 파일명은 항상 대문자 `LINKLIST.XML`이다.

링크 리스트 파일은 `<?xml version="1.0" encoding="UTF-8"?>` 선언으로 시작하는 well-formed XML이어야 하고, 모든 링크 정의를 담는 루트 요소 하나를 가진다. 링크 리스트 파일과 그 안의 요소들은 버전 4에서 도입됐다.

### E.2 ISO11783LinkList (루트 요소)

링크 리스트 파일의 루트 요소로, 파일 구성 정보와 1차 요소 포함을 정의한다.

- FileVersion 속성으로 LINKLIST.XML과 TASKDATA.XML 간 고유 관계를 정의한다.
- TASKDATA.XML은 첨부 LINKLIST.XML의 전송을 지정하는 AttachedFile 요소 `<AFE A="LINKLIST.XML" B="1" C="" D="1" F="12988"/>`를 포함해야 한다.
- TASKDATA.XML에서 참조할 수 있는 LINKLIST.XML은 최대 1개다.

| 속성 | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- |
| VersionMajor | r | 4~99 | 이 링크 리스트 파일이 준수하는 ISO 11783-10 버전 (4 = E2.FDIS. LinkList 자체가 버전 4에서 도입) |
| VersionMinor | r | 0~99 | XML 스키마 리비전 |
| ManagementSoftwareManufacturer / Version | r | 32자 | 관리 소프트웨어 제조사·버전 |
| TaskControllerManufacturer / Version | o | 32자 | TC 제조사·버전 |
| FileVersion | o | 32자 | 링크 리스트 파일 버전 |
| DataTransferOrigin | r | 1~2 | 1=FMIS, 2=MICS |
| LinkGroup (LGP) | r | 요소 | LinkGroup 목록 |

### E.3 Link — LNK

파일 세트 안의 XML 요소(객체)와 ISO 11783 범위 밖 엔티티에 해당하는 키 값을 연결(매핑)하는 coding data 요소다. 키 값의 형식과 의미는 부모 LinkGroup의 LinkGroupType이 결정한다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| ObjectIdRef | A | r | xs:ID | 객체 식별자. 유일성 범위는 데이터 전송 파일 세트 |
| LinkValue | B | r | 최대 255자 | 객체의 링크(키) 값 |
| LinkDesignator | C | o | 최대 32자 | 링크 이름 |

### E.4 LinkGroup — LGP

Link 요소는 다양한 목적·다양한 외부 키 타입으로 만들어질 수 있다. LinkGroup은 공통 키 타입 하나의 Link들을 묶고 그룹 공통 데이터도 보관하는 coding data 요소다.

| 속성 | XML | 필수 | 타입/범위 | 설명 |
| --- | --- | --- | --- | --- |
| LinkGroupId | A | r | xs:ID | 링크 리스트 파일 내 고유 식별자 (`LGP` 형식, MICS는 음수) |
| LinkGroupType | B | r | 1~4 | 1=UUIDs, 2=Manufacturer Proprietary, 3=Unique Resolvable URIs, 4=Informational Resolvable URIs |
| ManufacturerGLN | C | o | anyURI, 최대 64자 | 제조사의 GS1 Global Location Number. 타입 2에서는 필수 |
| LinkGroupNamespace | D | o | 최대 255자 | 타입 3·4용 접두어 — 그룹 내 모든 LinkValue 앞에 붙는다. 타입 3에서는 마지막 콜론까지의 URI를 담아야 한다 |
| LinkGroupDesignator | E | o | 최대 32자 | 그룹 이름 |
| Link | | o | 요소 | Link 목록 |

<strong>타입 1 — UUID</strong>: 파일 세트 내 객체 식별자의 유일성은 파일 세트 범위로 한정되므로, 더 넓은 시스템 범위에서 FMIS·MICS가 객체를 동기화하려면 객체 ID를 가진 모든 요소에 UUID를 연관시킬 수 있다. UUID는 ISO/IEC 9834-8(RFC 4122 호환)에 따라 생성하며 이 표준에서는 버전 4(랜덤) 알고리즘을 사용해야 한다. MICS가 UUID 생성 능력이 있으면 TC가 LINKLIST.XML에 새 항목을 추가할 수 있고, 새로 만든 객체 식별자는 네임스페이스 문자 + 음수여야 한다. MICS에서 새로 생성된 요소의 UUID는 항상 ManufacturerGLN이 빈 타입 1 LinkGroup에 추가하며, ManufacturerGLN이 빈 LinkGroup들 안에서는 파일 세트의 XML 요소 하나당 Link가 최대 1개여야 한다.

<strong>타입 2 — 제조사 독점 키</strong>: 제조사 고유 키 교환용이다. 같은 요소로의 다중 링크가 허용되고, 스키마 검증만 통과하면 Link 사용 방식은 제조사 재량이다(파트너에게 공유할 책임도 제조사에 있다). 키 값으로 UUID를 쓸 수도 있다. 용례: 고객·제품을 독점 ID 값에 매핑, 인수합병으로 한 고객이 과거 ID를 여러 개 갖는 경우 등.

<strong>타입 3 — 고유 해석 가능 URI</strong>: 요소를 시간이 지나도 일관되게 그 요소를 유일하게 식별하는 URI에 연결한다(GS1 GTIN 코드 연계 등). LGP.D와 LNK.B의 연결(concatenation)이 해석 가능한 URI여야 한다 — 중복 데이터를 없애고 그룹 내용을 프로그램적으로 인식 가능하게 하기 위함이다. URI가 URN인 특수한 경우 네임스페이스 지정에 쓰인 마지막 콜론에서 분할해, 콜론 포함 앞부분을 LinkGroupNamespace(D)에, 뒷부분을 LinkValue(B)에 넣는다. 같은 요소로의 다중 링크가 허용된다.

<strong>타입 4 — 정보성 해석 가능 URI</strong>: 제조사·농장 홈페이지, 제품 정보 시트 같은 링크 저장 메커니즘이다. 휘발성 인터넷 페이지에 적합하며 <strong>식별·매핑 용도로 쓰면 안 된다</strong>. LGP.D + LNK.B 연결이 해석 가능한 URI여야 하고, 같은 요소를 참조하는 Link가 여러 개 있을 수 있다. 타입 3과 달리 URI 분할 위치에 대한 규정은 없다.

## 부속서 F (규범) — TC Functionality와 Device Descriptor Object Pool 정의

### F.1 개요

Annex A의 객체 집합으로 같은 장치에 대해 다양한 device descriptor object pool을 구성할 수 있고, 제품마다 이 표준의 통신 방법·시스템 기능 구현 범위도 다르다. 서로 다른 제조사 제품들이 공통 기능 수준에서 동작하려면 기능의 추가 분류·정의가 필요하다. 이 부속서는 제품 설계자를 위해 어떤 기능 집합을 목표로 설계할지, 장치의 제어 가능 측면을 잘 반영하고 데이터 처리에 다루기 쉬운 device descriptor 구조를 어떻게 잡을지에 대한 지침과 예시를 제공한다. 이 지침·예시는 AEF와 협력해 작성됐다(적합성 시험·구현 지원).

### F.2 TC functionality

TC functionality는 ISO 11783-10 기반 기능의 구분된 집합 정의로, 시스템에서 올바르게 연동하기 위해 제품에 구현해야 할 기능을 식별한다. 미래 발전과 제품의 기술적 제약을 수용하기 위해 세대(generation) 번호로 버전이 매겨지고 일부는 선택 기능을 가진다. 정의된 TC functionality는 4가지다: <strong>TC-BAS</strong>(basic), <strong>TC-GEO</strong>(geo-based), <strong>TC-SC</strong>(section control), <strong>LOG</strong>(data logger) — 모두 generation 1.

#### F.2.1 TC-BAS generation 1

태스크 기반 <strong>총계(totals) 수집</strong> — TC 클라이언트 device element들의 총계 값 읽기·쓰기다. 총계는 입출력 자원·거리·시간 등의 누적값(총 면적, 총 수확 질량 등)으로, 위치 특정적일 필요가 없어 시간·위치 데이터를 요구하지 않는다.

- TC 서버가 TC-BAS에 적합하려면 ISO 11783-11에 총계로 정의된 모든 DDI를 지원해야 한다.
- TC 클라이언트는 총계의 부분집합만 제공해도 되지만 최소한 DDI 119(total time)는 제공해야 한다. DDOP에 rate DDI가 정의돼 있으면 대응하는 total 값도 제공해야 한다.
- TC-BAS gen 1을 따르는 FMIS·TC·TC 클라이언트는 파일 세트(ISO11783_TaskData 등)와 Version 메시지에 TC 버전 번호 <strong>3</strong>을 게시해야 한다.
- FMIS는 임베디드 TC 구현의 한계를 고려해야 하고 그 역도 같다 — 대형 파일 세트 생성을 피해야 하며, 최소한 총 20,000개 XML 요소·요소 타입당 2,000개를 FMIS·TC 구현이 지원해야 한다.
- TC-BAS gen 1 구현은 OperationTechnique, OperationTechniqueReference, CodedCommentGroup, Connection, 모든 기하/지리 참조 요소의 처리가 요구되지 않는다. 이 요소들이 파일 세트에 있으면 건너뛰어도 되지만, 이를 포함한 나머지 내용은 읽어야 하고 미지원 요소 때문에 파일 세트를 거부하면 안 된다.

장치 클래스별 권장 총계 DDI(Table F.1 요약): Tractor(117·118·119·120·148), Tillage·Secondary Tillage(116·117·119), Seeders/Planters(81 또는 82, 116·117·119), Fertilizers(81·116·117·119), Sprayers(80·116·117·119), Harvesters(89 또는 90 또는 91, 116·117·119), Irrigation(80·119), Transport/Trailers(117·119), Farmstead(119·120), Earthworks(119), Skidders(119·148), Sensor Systems(119), Slurry Applicators(80·116·117·119) 등.

#### F.2.2 TC-GEO generation 1

TC 클라이언트 device element들의 <strong>지리적 위치 기반 위치특정 값 처리</strong>를 정의한다. GNSS 수신기 등 위치 소스가 TC에 연결돼야 한다. 적용 rate 가변 제어만을 의미하지 않는다 — 제어 가능 요소가 없는 클라이언트가 매핑용 "as-applied" 데이터(콤바인 수확량 센서, 플랜터 파종 밀도 등)를 제공하는 경우에도 적용된다.

- TC 서버 적합 요건: ISO 11783-11의 모든 DDI 지원. 클라이언트는 자신이 제어·로깅하는 프로세스에 관련된 DDI 부분집합만 제공 가능. rate 제어 프로세스가 있으면 setpoint rate + actual rate DDI 쌍 최소 1개 지원 권장. application rate 외의 setpoint DDI(경운 작업 깊이 등)도 제어 가능하다.
- TC-GEO를 지원하면 TC-BAS도 지원해야 한다. 파일 세트와 Version 메시지에 TC 버전 <strong>3</strong> 게시.
- Grid type 1·2 처리는 필수이며 최소 350행 × 350열을 지원해야 한다.
- 폴리곤 기반 GEO 처방 처리는 선택이다. 지원한다면 Control function functionalities 메시지(ISO 11783-12 정의)에 명시해야 한다.
- TC 서버의 위치 기반 제어 채널은 최소 1개다. 병렬 처리 가능한 채널 수는 Control function functionalities 메시지와 Version 메시지에 명시하며, TC 클라이언트는 Version 메시지에 보고된 채널 수를 근거로 자신의 device descriptor에 보고하는 제어 채널 수를 제한해야 한다.

장치 클래스별 권장 rate DDI(Table F.2 요약): Seeders/Planters(6·7·11·12·16·17), Fertilizers·Sprayers·Slurry Applicators(1·2·6·7), Harvesters(7·84·181), Root Harvesters(7·84), Forage(7·84·181), Irrigation(1·2).

#### F.2.3 TC-SC generation 1

TC 클라이언트 device element들의 <strong>지리 위치 기반 on/off 제어</strong>를 정의한다. 기존 살포 완료 영역이나 특정 영역(헤드랜드, 필드 밖 등)과의 조우를 판정해 중복 살포·누락을 최소화하는 능력을 포함한다. GNSS 등 위치 소스가 필요하다.

- TC-SC 서버는 최소 붐 1개·섹션 3개를 지원해야 하고, 클라이언트는 붐 1개·섹션 1개부터 적합하다. 서버가 클라이언트의 물리 제어 가능 수보다 적은 붐/섹션만 제어할 수 있으면, 클라이언트가 자기 device descriptor의 붐·섹션 수를 서버가 제어 가능한 수에 맞춰 줄여야 한다 — 물리적으로 제어 가능한 요소들을 묶어 더 적은 수로 통신한다. 지원/제어 가능 붐·섹션 수는 Control function functionalities 메시지와 Version 메시지에 명시한다.
- TC-SC는 TC-BAS·TC-GEO와 <strong>독립적</strong>이다 — 조합 지원이 요구되지 않으며, TC-SC만 제공하는 경우 파일 세트 처리나 FMIS-TC 연결 지원 요구가 없다.
- TC·클라이언트는 Version 메시지에 TC 버전 <strong>3</strong> 게시.
- TC-SC 필수 지원 DDI(Table F.3): 67, 70, 134, 135, 141, 142, 143, 160, 161~176, 205, 206, 290~305.

#### F.2.4 LOG generation 1

<strong>수명 총계(lifetime totals) 기록</strong> — LOG 클라이언트 device element들의 수명 총계 읽기다. 수명 총계는 위치 특정적일 필요가 없어 시간·위치 데이터를 요구하지 않는다.

- LOG 서버 적합 요건: ISO 11783-11에 총계로 정의된 모든 DDI 지원. 클라이언트는 부분집합 제공 가능하되 최소 DDI 274(lifetime total time)는 필수다. DDOP에 rate DDI가 있으면 대응 lifetime total도 제공해야 한다.
- LOG gen 1 구현은 파일과 Version 메시지에 TC 버전 번호 <strong>4</strong>를 게시해야 한다.
- 파일 크기 하한은 TC-BAS와 같다(총 20,000개 / 타입당 2,000개).

장치 클래스별 권장 lifetime total DDI(Table F.4 요약): Tractor(272~276), Tillage 계열(271·272·274), Seeders/Planters(271·272·274, 266 또는 267), Fertilizers(…266), Sprayers(…325), Harvesters(271·272·274 + 268/269/270 중 하나), Irrigation(274·325), Farmstead(274·275), Skidders(274·276) 등.

### F.3 Device descriptor object pool 예시

농업 필드 작업에 흔한 장치들에 대해 구현을 안내하는 device descriptor object pool 예시가 작성돼 있다. 예시는 TC functionality별로 묶이며 기능 적은 기본 장치에서 복잡한 장치로 점진적으로 전개된다. 각 단계의 설계 규칙이 함께 정의되며, <strong>변형 구현 시에도 이 설계 규칙을 따라야 한다</strong>. 한 예시가 여러 functionality에 걸쳐 쓰이는 경우 해당 functionality에 관련된 속성만 그림에 표시된다 — 장치가 여러 functionality를 지원하면 각 functionality 예시의 속성을 합친 집합을 device descriptor에 담아야 한다.

#### F.3.1 붐(boom) device element 정의

붐은 "Function" 타입 또는 "Device"(루트) 타입의 device element다. 붐 개념은 장치의 개별 작업(operation) 하나 — 그 장치의 단일 커버리지 레이어(작업 영역) — 를 나타낸다. 장치에 붐이 여러 개면 여러 작업/커버리지 레이어를 동시에 추적·제어할 수 있다. 붐을 나타내는 device element는 더 세밀한 커버리지 제어와 단일 붐으로 여러 제품을 살포하는 장치 지원을 위해 "Section"·"Bin" 타입 자식 요소들을 가질 수 있다. 붐의 예: 수확기의 헤더, 액상 살포기의 노즐 달린 스프레이어 붐, 플랜터의 파종 유닛 달린 플랜터 바.

#### F.3.2 다이어그램 표기법

예시 다이어그램은 device element 타입(device/function/bin/section/unit/navigation reference/connector)별 도형과, DDI 속성 수준의 기호를 쓴다. 기호는 property(자물쇠), lifetime total(연필), total, setpoint, control source, time interval 측정, on-change 측정, distance interval 측정을 구분하고, 배경색으로 settable(파랑)/읽기 전용(흰색)을 구분한다.

#### F.3.3 TC-BAS gen 1 예시 풀의 설계 규칙

기본형에서 복잡형으로 이어지는 예시들(Figure F.3~F.14)의 핵심 규칙:

- 최소형: 루트 device element에 total time(DDI 119, settable total + time interval 트리거)만 있는 구성이 가장 기본이다.
- rate DDI를 포함하는 장치는 그 rate에 대응하는 total DDI를 제공해야 한다.
- 작업 폭·연결 오프셋은 장치에서 상수면 property로, 작동 중 변할 수 있으면 process data로 통신하는 것이 <strong>필수</strong>다. connector type 속성은 connector device element에 두는 것을 권장한다.
- 총계는 여러 device element에 나눠 제공할 수 있다. Device(루트) 수준 총계와 Function 수준 총계는 각자 자기 요소의 로직으로 갱신되며, Function 수준 총계의 합이 Device 수준 총계와 일치할 필요는 없다. TC-BAS에서는 Device 수준 total time이 필수고 다른 요소 안의 total time은 선택이다.
- Actual Cultural Practice DDI(179)를 Function들에 붙이면 한 장치가 수행하는 두 작업(예: 시비 + 파종)의 총계를 독립 기록할 수 있다. 붐이 여러 개면 DDI 179는 붐 Function 또는 그 아래 Bin에 둔다. 베일러 예시처럼 장치 클래스(forage harvesting)만으로 베일러/모어를 구분할 수 없을 때 DDI 179 값으로 장치 성격을 식별한다.
- rate DDI와 관련 총계는 Bin device element의 속성으로도 지정할 수 있다. Bin을 루트(붐)의 자식으로 두면 그 빈의 제품이 그 붐으로 살포됨을 명시한다. <strong>같은 rate DDI를 루트와 Bin에 동시에 붙이는 것은 금지</strong>이며, Function과 Bin에 동시에 두는 것도 금지다. 루트의 total time은 필수고, total rate DDI는 actual rate DDI가 있는 요소와 같은 요소에 있어야 한다.
- Element Type Instance DDI(178)는 운전자가 어느 빈에서 제품을 살포할지 선택할 수 있도록 빈을 식별하는 용도로, <strong>Bin device element 안에</strong> 둬야 한다.
- 트랙터 예시: 루트에 effective/ineffective total distance(117·118)·effective/ineffective total time(119·120)·total fuel consumption(148), 커넥터(front/rear drawbar/rear three-point-hitch)와 navigation device element는 TC-BAS에선 선택.
- peer control 가능 장치(온라인 센서 등)가 같은 setpoint DDI의 값 소스(source)와 값 사용자(user)를 모두 가지면, 그 DeviceProcessDataObject들을 한 device element에서 참조하면 안 된다 — 별도 device element 2개가 필요하다.

#### F.3.4 TC-GEO gen 1 예시 풀의 설계 규칙

TC-GEO 적합 최소 구조는 단일 붐 장치다(TC-GEO 적합 장치의 최소 붐 수는 1). 붐의 최소 기능은 공간적으로 기록 가능한 actual 값 제공이며, 이 actual 값 process data 속성들은 최소 "Time Interval" 측정 트리거를 지원해야 한다.

- <strong>Work state</strong>: 붐은 actual work state process data 정의를 포함해야 하고, 이 데이터는 "Change Threshold" 트리거를 지원해야 한다.
- <strong>Geometry</strong>: 각 붐은 작업 영역 산출을 위해 완전한 기하 정의를 제공해야 한다. 최소 구성은 offset X·offset Y·maximum working width DDI(property 또는 process data). offset X·Y는 붐마다 필수다. 붐 기하를 자식 섹션들로부터 유도하면 안 된다. property와 process data의 혼합은 허용된다(예: connector type은 수명 동안 불변이므로 property, 나머지 기하는 구성 변경 시 바뀔 수 있으므로 process data). 기하 process data에는 "On Change" 트리거 권장. TC-GEO 지원 TC는 시스템 기동 시 장치에 기하 DDI 값을 질의해 커버리지·위치 기반 명령에 올바른 기하를 써야 한다. TC-GEO에는 트랙터 연결점을 지정하는 connector가 필요하고, 한 pool에 여러 connector 정의가 허용된다. Connector·Navigation 타입 요소는 <strong>루트 바로 아래에만</strong> 둘 수 있으며 X·Y offset과 connector type 정의를 포함해야 한다.
- <strong>Working width</strong>: maximum working width는 처방 setpoint가 적용될 수 있는 폭이다. 일부 작업기에서는 동적으로 변할 수 있고 고정 폭 붐에서는 정적 property일 수 있다. 붐은 선택적으로 actual working width를 제공할 수 있다 — Device/Function 수준의 actual working width는 하위 섹션들의 actual work state에 따라 달라져야 한다("On"인 섹션 폭의 합으로 보고). TC·FMIS는 섹션 작업 폭으로 섹션 기하를 판정하고 어디서 섹션이 On/Off였는지 매핑한다.
- <strong>Prescription control state</strong>: 붐이 setpoint 값 process data를 포함하면 같은 수준에 prescription control state process data(DDI 158)도 포함해야 한다. 이 속성은 settable이어야 하고 on-change 트리거를 지원해야 한다. ISOBUS Data Dictionary 명세에 더해 다음 규칙이 적용된다: ⓐ 태스크 정지 시 TC 클라이언트는 내부적으로 prescription control state를 DISABLED/OFF로 설정한다. ⓑ TC는 rate 값 명령을 보내기 전에 prescription control state를 ENABLED/ON으로 설정해야 한다. ⓒ ENABLED/ON 명령 수신 시 TC 클라이언트는 대응 setpoint process data를 정해진 안전 상태 값으로 리셋해야 한다. ⓓ TC는 클라이언트의 prescription control state 변경을 on-change 측정 명령으로 수신해야 한다. setpoint 값 process data를 포함하는 붐은 대응 actual 값 process data도 포함해야 한다.
- <strong>Boom sections</strong>: 붐에 섹션 device element들을 추가할 수 있으며, TC-GEO 적합 붐에 TC-SC 요건까지 포함하는 경우 Prescription Control State(TC-GEO)와 Section Control State(TC-SC) 속성이 붐 요소에 공존한다.
- <strong>Function이 붐인 경우</strong>: 붐이 Function device element로 정의되면 actual/setpoint 값, X·Y offset, maximum working width, prescription control state를 모두 그 Function 안에 둬야 하고, 이때 루트(DET-0)는 actual work state 속성 외의 actual/setpoint 값을 가지면 안 된다. 붐 아래에 Bin을 추가해 그 붐으로 제품이 살포됨을 표현할 수 있으며, 단일 작업 장치라면 Bin 안의 Element Type Instance DDI는 선택이다(Actual Cultural Practice DDI도 필수는 아니지만 Bin이 어떤 작업용으로 구성됐는지 명시하는 것을 권장).
- <strong>Control latency</strong>: device element에 physical setpoint time latency(DDI 142) 속성이 있으면 TC는 그 값으로 클라이언트의 구동 지연을 보정해 setpoint 명령 전송 시점을 조정해야 한다. 시퀀스: TC가 위치 갱신을 받아 rate 변경 명령을 보내면 T2에 rate 변화가 시작되고 T4에 완료된다 — 이 T4−T2(ms)가 클라이언트가 보고하는 physical setpoint time latency다. 보정하는 TC는 T2에 수신한 위치를 T4 시점의 추정 위치로 투영해 그 위치의 setpoint 값을 전송해야 한다. physical actual time latency(DDI 143)가 있으면 TC·FMIS가 맵상 값 위치 보정에 사용해야 하며, 143은 음수도 가능하지만 142는 양수만 가능하다. rate process data 속성은 루트 또는 Bin 중 <strong>한쪽에만</strong> 있어야 한다.
- <strong>다중 제어 채널</strong>: 독립 살포 제어 작업이 2개인 장치는 Function 2개(예: 시비 = ACP 1, 파종 = ACP 2)로 모델링한다. TC는 Actual Cultural Practice 값으로 붐 정의를 구별한다. Element Type Instance(178)는 운전자에게 각 빈을 식별시키는 용도로 Bin 안에 둔다. 같은 rate 속성을 루트와 붐에, 또는 붐 역할 Function과 Bin에 동시에 두는 것은 금지다. ACP·ETI 속성은 TC-GEO 태스크 실행을 다른 장치로 옮기는 과정도 보조한다 — 계획한 device descriptor와 실제가 불일치하면 PDV "그룹"들을 가용 장치에 재할당해야 하며, TC는 장치 재할당과 setpoint PDV 그룹의 device element 매핑을 처리할 수 있어야 한다.
- <strong>서브붐(sub-boom)</strong>: 서브붐/섹션 수준에서 rate를 가변할 수 있는 장치는 rate 속성을 가진 서브붐 Function 또는 Section 요소로 모델링한다. 최상위 붐에 수신된 rate 제어 명령은 장치가 자식 Function들로 자동 전달해야 하고, 최하위 수준에 수신된 명령은 지정된 Function에만 적용된다. 최상위 붐의 actual rate는 자식들의 평균이다. 서브붐 계층은 <strong>최대 1단계</strong>만 허용되고, 서브붐은 X·Y offset과 maximum working width를 포함한 완전한 기하 정의를 가져야 한다.

#### F.3.5 TC-SC gen 1 예시 풀의 설계 규칙

기하 전체를 device property로 제공하면 TC-SC 컨트롤러가 연결 시 질의하거나 동작 중 변경을 모니터할 필요가 없다. 기하가 동작 중 변할 수 있으면 process data로 제공하며 property/process data 혼합이 허용된다(기하 process data에는 "On Change" 트리거 권장, TC-SC는 기동 시 초기 기하 DDI 값을 질의해야 한다).

- <strong>Work state</strong>: DDOP에서 섹션 작업 상태의 보고·제어에 허용되는 것은 Actual/Setpoint <strong>Condensed</strong> Work State뿐이다 — Section 요소 안에 개별 Actual Work State(141)나 개별 Setpoint Work State(289)를 두면 안 된다. 붐의 개별 Actual Work State는 그 작업의 마스터 작업 스위치를 나타내며 on-change·time interval로 보고할 수 있다. Setpoint Condensed Work State에는 "On Change" 지원 권장(전송한 명령별 확인 수신용), Actual Work State(들)와 Actual Condensed Work State(들)에는 "On Change"·"Time Interval" 지원이 필수다. 섹션의 작업 상태는 device element 계층을 따라 결합해 판정한다 — 루트의 Actual Work State가 "Off"면 섹션들이 "On"이어도 TC-SC 컨트롤러는 "Off"로 처리한다.
- <strong>Working width</strong>: 각 Section은 최소 한 종류의 working width를 제공해야 하고, 여러 종류가 있으면 Section Controller는 Actual(67) → Maximum(70) → Default(68) 우선순위로 사용할 수 있어야 한다. Section의 Actual Working Width는 그 섹션의 작업 상태에 <strong>의존하면 안 되고</strong>, Device/Function(붐) 수준의 Actual Working Width는 하위 섹션 상태에 의존해야 한다("On"인 섹션 폭의 합). Section의 Element Number는 기계 좌→우 순 증가를 권장하되 섹션 순서 판정에는 기하 정의가 Element Numbering보다 우선한다. 한 붐에 속한 Section들은 기하적으로 겹침·틈 없이 정확히 일렬로 배치돼야 한다.
- <strong>Section control state</strong>: TC-SC용 붐은 setpoint condensed work state와 같은 수준에 Section Control State process data(DDI 160)를 포함해야 한다. settable + on-change 트리거 필수. TC-SC 불가능한 붐은 이 속성을 포함하면 안 된다. 추가 규칙: ⓐ 태스크 정지 시 클라이언트는 내부적으로 DISABLED/OFF로 설정 ⓑ TC는 setpoint condensed work state 명령 전에 ENABLED/ON 설정 ⓒ ENABLED/ON 수신 시 클라이언트는 대응 work state를 안전 상태 값으로 리셋 ⓓ TC는 on-change 측정 명령으로 클라이언트의 상태 변경을 수신.
- <strong>기하 최소 정의와 예외</strong>: 붐 역할의 모든 Section·device element는 폭과 오프셋(Offset X·Y, Width — property 또는 process data)을 제공해야 한다. 유일한 예외: 부모가 Offset X를 정의하면 자식 Section들은 Offset X를 생략할 수 있다(부모 값이 모든 자식 Section에 유효) — Section 요소 크기 최적화용이다.
- <strong>Control latency(TC-SC)</strong>: 신규 설계 권장 방식은 붐 수준에 별도의 SC Turn On Time(DDI 205)·SC Turn Off Time(DDI 206)을 두는 것이다. 두 값은 붐 요소의 settable process data로 정의하고 on-change 트리거를 지원해야 한다(TC-SC 운전자 인터페이스에서 조정해 클라이언트에 저장 가능). TC-SC 서버는 Turn On/Off Time만큼 섹션 on/off 명령을 <strong>앞당겨</strong> 전송해 클라이언트의 지연을 보정하며, 클라이언트는 보고한 시간과 다르게 on/off 타이밍을 바꾸면 안 된다(값은 섹션의 물리 성능 기준). 켜는 시간과 끄는 시간은 다를 수 있다. 하위 호환: 섹션 요소에 Physical Setpoint Time Latency(142)도 있으면 Turn On/Off Time이 우선하고 142는 섹션 제어 명령에서 무시한다. 142만 있으면 서버가 그 값으로 on/off 명령을 앞당긴다 — 이 경우 켜기/끄기 지연을 구분할 수 없다. 시퀀스 다이어그램상 setpoint CWS 명령에 대한 응답 메시지와 섹션 상태 변화 시작 즉시의 actual 상태 갱신 전송은 필수이며, 맵 커버리지 갱신 등에 Turn On/Off Time을 반영할 책임은 TC-SC 서버에 있다.
- <strong>멀티붐·멀티 제품</strong>: 붐이 여러 개면 각 Function이 자기 물리 붐과 섹션 집합을 갖고 붐별 섹션 수는 달라도 된다(ACP로 구별). 단일 붐으로 여러 제품을 살포하는 장치는 한 붐 아래 Bin 여러 개를 둔다 — TC-SC 관점에서는 단일 붐이며 그 붐이 TC-SC 적합 붐의 모든 필수 속성을 담아야 한다. 멀티붐 장치를 서버 능력에 맞춰 줄일 때는 TC-SC 붐 수를 서버 지원 수 이하로, TC-SC 붐들의 총 섹션 수도 서버 지원 수 이하로 조정한다. TC-SC 제어 가능 붐과 불가능 붐의 차이는 Section Control State 속성 유무다(제어 가능 붐만 settable + on-change로 포함). 단일 TC-SC 붐 안에서 절반씩 다른 rate를 적용하려면 중간 Function 수준(서브붐)으로 각 절반의 rate를 표현한다 — condensed work state를 붐 전체에 효과적으로 쓰려면 TC-SC 붐 정의(Section Control State, Actual/Setpoint Condensed Work State)는 rate 제어 절반들의 <strong>부모 요소(최상위 붐)</strong>에 둬야 하며, 서브붐은 최대 1단계다.
- <strong>동적 기하</strong>: 다중 섹션 TC-SC 붐의 Offset Y는 하위 섹션 on/off로 바뀌면 안 된다(붐 중심 고정). 반면 커버 영역을 올바르게 나타내기 위해 Offset Y의 동적 갱신이 필요한 장치도 있다 — 예: 좌측 또는 우측부터 부분 사용 가능한 커터바. 좌측 절반만 절단 중이면 Actual Working Width를 최대 폭의 절반으로 줄이고 Offset Y를 절단 중인 커터바 영역의 중심으로 조정한다.
- <strong>Actual working length</strong>: Actual Working Length(DDI 226)로 전체 작업 또는 섹션 등 device element의 작업 길이를 정의할 수 있다. 길이가 중심에 있지 않으면 같은 요소의 오프셋으로 이동량을 정의한다. 붐에 Actual Working Length가 있으면 그 값과 붐의 Offset X는 모든 하위 섹션에 적용된다(상속). 섹션별로 값이 다르면 붐이 아니라 섹션 요소에 둬야 한다.

#### F.3.6 LOG gen 1 예시 풀의 설계 규칙

TC-BAS 예시와 같은 전개(최소형 → Function 분리 → Bin → 멀티 작업 → 장치 클래스별)를 lifetime total DDI로 반복한다.

- 최소형: 루트에 Lifetime Effective Total Time(DDI 274) 하나만 있는 구성이다. <strong>lifetime total DDI는 TC/DL 서버가 설정할 수 없으므로</strong> settable 배경을 갖지 않는다(time interval 트리거로 전송 요청은 가능).
- rate DDI를 포함하는 장치는 그 rate의 lifetime total DDI를 제공해야 한다.
- lifetime total은 여러 device element에 나눠 제공할 수 있고, Function 수준 값들의 합이 Device 수준과 일치할 필요는 없다. LOG gen 1에서 Device 수준 lifetime total time은 필수, 다른 요소 안의 것은 선택이다.
- rate DDI와 lifetime total은 Bin의 속성으로도 지정할 수 있다. 같은 rate DDI를 루트와 Bin, Function과 Bin, 루트와 붐 Function에 동시에 붙이는 것은 금지다. lifetime total rate DDI는 actual rate DDI가 있는 요소와 같은 요소에 있어야 한다.
- ACP(179)·ETI(178) 활용 규칙은 TC-BAS와 동일하다: 멀티붐이면 179는 붐 Function 또는 하위 Bin에, 178은 Bin 안에. 베일러 예시(ACP=5로 forage harvesting 클래스 내 베일러/모어 구분), 2단계 베일 카운트 예시(Lifetime Precut(285) + Uncut(286) Total Count의 합 = Lifetime Yield Total Count(270)), 트랙터 예시(272·273·274·275·276) 등이 제시된다.

## 부속서 G (규범) — 태스크 기반 시간 등록

### G.1 시간 등록 수준

ISO 11783-10에서 시간 등록은 두 수준으로 가능하다. 첫째는 <strong>Task 수준</strong> — 태스크가 거치는 여러 시간 유형의 발생을 등록한다. 둘째는 <strong>장치 데이터 로깅 수준</strong> — 각 장치가 working·in-transport 같은 상태를 TC/DL에 보고하고 상태 변화를 timelog에 등록한다.

### G.2 Task 수준 시간 등록

각 태스크 안에 Time 요소를 추가해 여러 시간 유형의 시작·기간·종료를 등록한다. TC의 시간 등록 구현 상세 수준에 따라 사용하는 시간 유형 집합이 달라진다.

시간 유형 정의(Table G.1):

| Time Type | 정의 |
| --- | --- |
| 2. Preliminary | 농장에서의 준비, 필드로 이동, 필드에서의 준비에 쓴 시간. 태스크 활성화 시점에 시작해 Effective 작업 또는 다른 시간 유형이 시작되면 끝난다. 이 유형을 기록할 수 없으면 Ineffective로 분류한다 |
| 4. Effective | 작업 프로세스 수행에 절대적·직접적으로 필요한 활동. 태스크의 주 작업이 시작될 때 시작하며 주 작업에 쓴 시간을 담는다. <strong>MICS가 제공해야 하는 최소 요건</strong>이다 |
| 5. Ineffective | 태스크의 주(effective) 작업이 활성 상태가 아닌 시간. Effective 구간 사이에 쓸 수 있다 |
| 6. Repair | 태스크 중 수리 작업에 할당된 시간. 기록 불가 시 Ineffective로 분류 |
| 7. Clearing | 태스크 중 Effective 작업이 마지막으로 정지된 시점부터 태스크 정지까지. 기록 불가 시 Ineffective로 분류 |
| 8. Powered Down | 시간 등록이 동작하는 기계의 전원이 꺼진 시점부터. 기록 불가 시 Ineffective로 분류 |

시간 등록 수준(Table G.2):

| 수준 | MICS 지원 TimeType | 설명 |
| --- | --- | --- |
| 1. Minimal | 4 (Effective)만 | 태스크당 이 유형만으로 시간 기록 제공. 태스크 내 모든 effective Time의 합 = 그 태스크의 총 작업 시간 |
| 2. Intermediate | 2, 4, 5, 6, 7, 8 | 주 작업 감지로 2·4·5·7 유형의 자동 기록이 가능하다(태스크에 할당된 장치들의 work status 정보 활용 가능). 6(Repair)은 운전자 입력이 필요할 수 있고, 8(Powered Down)은 implement bus에 방송되는 정보 기반 자동 기록 가능 |

예: Minimal 수준은 태스크 시작~종료를 Effective(총 작업 시간) 하나로 기록하고, Intermediate 수준은 같은 구간을 Preliminary → Effective → Ineffective → Effective → Ineffective → Effective → Clearing으로 분해해 기록한다.

### G.3 장치 수준 시간 등록

장치 관련 데이터 로깅은 Data Dictionary 엔티티의 데이터 정의 또는 로깅 가능한 Parameter Group의 존재에 기반한다. Data Dictionary에 정의된 총 시간 엔티티는 2개다.

| DDI | 엔티티 | 정의 | 단위 |
| --- | --- | --- | --- |
| 119 | Effective Total Time | 작업 위치에 있고 (거의 모든 필드 작업에서) 전진 속도가 있는 누적 시간. 관개 펌프를 구동하는 트랙터는 전진 속도 없는 effective time의 예다 | s |
| 120 | Ineffective Total Time | 작업 위치 밖이거나 정지 상태의 누적 시간 | s |

쟁기가 작업 위치에 있어도 트랙터가 주행하지 않으면 그 시간은 Effective가 아니라 Ineffective다. 이 두 정의로 장치(또는 그 일부)가 Effective/Ineffective 작업 상태였던 총 시간을 로깅할 수 있다. ISO 11783-7과 SAE J1939에도 시간 기록에 유용한 Parameter Group들이 있다 — 예: "Wheel-based speed and distance", "Implement operating state command".

## 참고 문헌 (Bibliography)

- SAE J1939 — Recommended Practice for a Serial Control and Communications Vehicle Network
- AEF(Ag Industry Electronics Foundation) — ISOBUS functionality 정의 가이드라인
- ISO 19136:2007 — Geographic information — Geography Markup Language (GML)
