---
title: "표준 정리: Part 12 — Diagnostics services"
description: "ISO 11783-12(Diagnostics services) — ECU 식별, DM 메시지, FMI 코드를 정리한 표준 요약이다."
date: 2026-08-21
tags: [ISOBUS, ISO11783, 표준정리]
---

# ISO 11783-12: Diagnostics services 정리

::: info 이 문서에 대해
ISO 11783-12 표준 원문을 학습 목적으로 재구성한 <strong>비공식 요약·해설</strong>이다. 규범적 판단이 필요할 때는 반드시 원문 표준을 확인해야 한다.
:::

## 개요

ISO 11783-12(3판, 2019-01)는 ISO 11783(ISOBUS) 네트워크의 <strong>진단 시스템</strong>을 정의하는 파트다. 트랙터와 작업기(implement)에 연결된 모든 ECU가 어떤 진단 정보를 제공해야 하는지, 그 정보를 어떤 메시지로 주고받는지를 규정한다. 목적은 명확하다. 운전자나 서비스 기술자가 네트워크에 연결된 장치 중 <strong>어느 유닛이 고장 났는지, 어떤 상태로 오동작 중인지</strong>를 식별할 수 있게 하는 것이다.

ISO 11783 자체는 ISO 11898(CAN) 기반 통신 시스템이며, 상당 부분이 트럭·버스용으로 개발된 SAE J1939 문서에 기반한다. Part 12의 진단 메시지도 SAE J1939-73(Application layer — Diagnostics)의 DM 메시지 체계를 그대로 가져와 농기계 환경에 맞게 요구사항을 좁힌 구조다.

:::info 3판(2019)의 주요 변경점
2판(ISO 11783-12:2014) 대비 변경 사항은 다음과 같다.

- 모든 파라미터에 SPN(Suspect Parameter Number) 추가
- Control Function Functionality 파라미터를 온라인 데이터베이스(ISOBUS.net)로 이관
- 참조 문서 갱신
:::

문서 구성은 본문(1~6절)이 짧고, 실질 내용 대부분이 부속서에 있다.

| 구성 | 성격 | 내용 |
|---|---|---|
| 1~5절 | 본문 | 적용 범위, 참조 문서, 용어, 약어, 일반 설명 |
| 6절 | 본문 | 진단 요구사항 (네트워크 정보·통계, CF 정보, Functionality 등) |
| Annex A | normative | 진단 정보 파라미터 정의 (SPN 포함) |
| Annex B | normative | 진단 정보 메시지 정의 (PGN, DM1/DM2 등) |
| Annex C | normative | Network configuration |
| Annex D | informative | 네트워크 설정 화면 예시 (진단 UI 화면) |
| Annex E | normative | FMI(Failure Mode Indicator) 정의 |

## 1~2. 적용 범위와 참조 문서

Part 12의 적용 범위는 ISO 11783 네트워크의 진단 시스템이다. ISO 11783 시리즈 전체가 다루는 대상은 농업·임업용 트랙터와 장착형·반장착형·견인형·자주식 작업기이고, 센서·액추에이터·제어 요소·정보 저장·표시 장치 간 데이터 전송 방법과 형식을 표준화한다.

인용 규격(normative references)은 다음과 같다.

| 규격 | 내용 |
|---|---|
| ISO 11783-1 | 시리즈 일반 표준 (모바일 데이터 통신) |
| ISO 11783-2 | Physical layer |
| ISO 11783-3 | Data link layer |
| ISO 11783-5 | Network management (NAME, address claim) |
| ISO 11783-7 | Implement messages application layer |
| ISO 14229-1 | UDS (Unified Diagnostic Services) Part 1 |
| SAE J1939-73 | Application layer — Diagnostics |

## 3~4. 용어와 약어

정의된 용어는 3개뿐이다.

| 용어 | 정의 |
|---|---|
| product | OEM이 생산한 장치 또는 ECU. 장치에 내장되어 출하되면 그 장치가 product이고, ECU 단독으로 시장에 나오면(애프터마켓 등) ECU 자체가 product다 |
| basic tractor ECU | ISO 11783-9 TECU에 특화된 functionality 특성 |
| server | mobile implement bus에서 client에게 서비스를 제공하는 control function |

주요 약어는 다음과 같다.

| 약어 | 의미 |
|---|---|
| CF | control function |
| DM | diagnostic message |
| DTC | diagnostic trouble code |
| FMI | failure mode indicator |
| OC | occurrence count |
| PG / PGN | parameter group / parameter group number |
| TECU | tractor ECU functionality |
| UT / VT | universal terminal / virtual terminal |
| AUX-N | AUX new functionality |
| TC-BAS / TC-GEO / TC-SC | task controller basic / geo / section control functionality |

## 5. 일반 설명

이 문서가 규정하는 표준 진단 시스템의 핵심 요구는 하나다. <strong>ISO 11783 네트워크에 연결된 모든 유닛은 이 문서에 정의된 정보를 제공해야 한다.</strong> 그래야 운전자·서비스 기술자가 네트워크 진단을 수행해 고장 유닛 또는 오동작 상태의 유닛을 특정할 수 있다.

## 6. 요구사항

### 6.1 ISO 11783 diagnostics

- 이 문서는 control function의 진단 능력을 규정한다. 1판에 있던 "level 0" / "level 1" 진단 구분은 <strong>폐기(obsolete)</strong>되었다.
- 모든 CF는 Annex B에 정의된 <strong>ISO 11783 진단 정보 메시지 전부와 그 파생 요구사항</strong>을 지원해야 한다. 메시지의 파라미터는 Annex A에 정의된다.
- 운전자·서비스 기술자가 네트워크의 문제를 진단할 수 있는 <strong>진단 사용자 인터페이스(diagnostic user interface)</strong>가 필요하다. 이 UI는 VT(virtual terminal)가 제공할 수도 있고, 네트워크에 연결된 다른 형태의 UI일 수도 있다. 이하 6.2~6.5의 정보는 이 UI를 통해 사용자에게 제공되어야 한다.

### 6.2 Network information

네트워크에 연결된 모든 CF는 진단 UI에 네트워크 정보를 제공해야 한다. 이 정보는 동작 중인 네트워크에 연결된 모든 CF의 상태 개요가 된다. 포함해야 하는 항목은 다음과 같다.

| 항목 | 설명 |
|---|---|
| ECU 식별 | CF를 담고 있는 ECU의 part number, serial number, 제조사명 |
| NAME | ISO 11783-5에 정의된 각 CF의 NAME |
| 소프트웨어 버전 | 각 CF의 SW 버전(들)과 CF가 요구하는 ECU 관련 SW 버전들 |
| 적합성 시험 데이터 | 시험 수행 기관(랩), 인증 데이터, 시험 연도 |
| 제품 식별 | product identification message |

진단 UI는 address claim 과정의 메시지를 모니터링해 정보를 수집하고, 추가 정보는 CF에 요청(request)해서 얻는다. <strong>같은 ECU 안의 모든 CF는 동일한 ECU identification 정보를 보내야 한다.</strong> 전형적인 네트워크 상태 화면 예시는 Annex D에 있다.

### 6.3 Network statistics

네트워크 상태를 표시하는 진단 UI는 자신의 네트워크 연결을 이용해 <strong>버스 통계도 직접 측정</strong>해야 한다.

- 최소 요구(하드웨어가 지원하는 경우): bus load, 송수신 중 검출된 CAN error, network message count
- 권장(하드웨어가 지원하는 경우): 250 ms ~ 5 s 구간의 평균 bus voltage

### 6.4 Control function information

각 CF는 특정 ECU의 문제·고장을 판단할 수 있도록 추가 고장 정보를 진단 UI에 제공해야 한다.

| 항목 | 설명 |
|---|---|
| 진단 프로토콜 | non-ISO 11783 또는 ISO 11783 진단에 필요한 그 CF의 특정 프로토콜 |
| active DTC | 현재 활성 고장 코드 (SPN + FMI) |
| previously active DTC | 과거 활성이었던 고장 코드 (SPN + FMI) |
| fault occurrences | 고장 발생 횟수 (가용한 경우) |

- CF는 previously active DTC의 <strong>클리어(clear)</strong>도 지원해야 한다(요구되는 경우).
- 진단 UI는 Annex B의 메시지로 SPN·FMI 정보를 요청한다. FMI 각각의 정의는 Annex E에 있다.

### 6.5 Functionalities

각 CF는 자신의 <strong>활성(active) functionality 정보</strong>를 진단 UI에 제공해야 한다. 여기에는 모든 활성 functionality와 그 generation·option이 포함된다. 보고 범위의 원칙이 중요하다.

- 구현되어 있으나 <strong>비활성</strong>인 functionality → 추가 구현은 가능하지만 보고 대상 아님
- ECU에 존재하지만 <strong>시스템에서 현재 사용 불가</strong>한 functionality → 보고한다
- ECU에 존재하지만 <strong>CF에서 현재 비활성화</strong>된 functionality → 보고하지 않는다

:::details 보고 범위 예시
- 예시 1 — 시스템에서 사용 불가한 경우: 작업기 ECU의 CF1이 minimum CF, TC-GEO, TC-SC functionality를 가진다. 이 작업기가 TC-SC 서버가 없는 트랙터에 연결되면 TC-SC는 "존재하지만 시스템에서 사용 불가"다. 이때 CF1은 minimum CF, TC-GEO, <strong>TC-SC까지 모두</strong> functionality 정보 메시지로 보고한다.
- 예시 2 — CF에서 비활성화된 경우: 같은 구성에서 고객이 TC-GEO만 구매해 TC-SC가 ECU에서 disabled 상태라면, CF1은 minimum CF와 TC-GEO만 보고한다.
:::

진단 UI는 Annex B의 control function functionalities 메시지로 functionality·generation·option 정보를 요청한다. <strong>diagnostic protocol 메시지는 진단 목적 전용이며, CF가 런타임 동작 구성에 사용해서는 안 된다.</strong>

### 6.6 Control function diagnostics

진단 정보 화면에서 문제가 특정 ECU의 특정 CF로 좁혀지면, 그 CF가 사용하는 프로토콜을 지원하는 <strong>서비스 툴</strong>을 ISO 11783-2에 규정된 진단 커넥터를 통해 네트워크에 연결한다. 이후 표시된 DTC를 기반으로 서비스 툴로 문제를 해결하는 흐름이다.

### 6.7 ISO Latin 1 문자 집합

ISO/IEC 8859-1(Latin 1)에는 191개의 그래픽 문자와 65개의 제어 문자(0~31, 127~159)가 있다. 이 문서에서 "ASCII", "printable ASCII"는 이 <strong>191개 그래픽 문자 집합</strong>을 가리키며, 별도 명시가 없으면 ASCII 파라미터에는 이 191개 문자만 허용된다.

## Annex A — 진단 정보 파라미터 정의 (normative)

Annex B 메시지들에 실리는 파라미터의 정의다. 문자열 파라미터의 공통 형식은 "가변 길이, ASCII(1 byte), 문자당 32~126·160~255 범위(비인쇄 문자 제외)"이며, 구분자로 쓰이는 문자는 값에 사용할 수 없다.

| 절 | 파라미터 | 길이 | SPN | 비고 |
|---|---|---|---|---|
| A.1 | ECU part number | 가변, 최대 200자 | 2901 | `*` 사용 금지 (구분자) |
| A.2 | ECU serial number | 가변, 최대 200자 | 2902 | `*` 사용 금지 |
| A.3 | Number of software identification fields | 1 byte | 965 | 범위 0~250, 운용 범위 0~125 |
| A.4 | Software identification | 가변, 최대 200자 | 234 | `*`, `#` 사용 금지 (아래 참조) |
| A.5 | ECU manufacturer name | 가변, 최대 200자 | 4304 | `*` 사용 금지 |
| A.6 | Diagnostic protocol identification | 8 bits | TBD | 비트필드 (아래 참조) |
| A.7 | ECU location | 가변, 최대 200자 | 2903 | 트랙터·작업기 상의 물리적 위치. `*` 금지 |
| A.8 | ECU type | 가변, 최대 200자 | 2904 | ECU 능력 분류(예: I/O). `*` 금지 |
| A.9 | Number of functionalities | 1 byte | TBD | 범위 1~255 |
| A.10 | Functionalities | 1 byte | TBD | 값 0~255, ISOBUS 온라인 DB(ISOBUS.net) 참조 |
| A.11 | Functionality generation | 1 byte | TBD | 범위 1~255 |
| A.12 | Number of option bytes | 1 byte | TBD | 범위 0~255 (아래 참조) |
| A.13 | ECU hardware ID | 가변, 최대 200 bytes | 6714 | HW 버전 ↔ 적합성 시험 성적서 연결용. `*` 금지, `#` 예약 |
| A.14 | Product identification code | 가변, 최대 50자 | 6699 | `*` 구분. VIN과 같을 수 있음 |
| A.15 | Product identification brand | 가변, 최대 50자 | 6700 | `*` 구분 |
| A.16 | Product identification model | 가변, 최대 50자 | 6701 | `*` 구분 |

주요 파라미터 해설:

- <strong>Software identification (A.4)</strong> — CF의 소프트웨어와, CF가 요구하는 ECU 관련 소프트웨어 버전들의 식별 문자열이다. software identification field 사이의 구분자는 `*`이며, <strong>필드가 하나뿐이어도 마지막 필드 끝에 `*`가 필요하다</strong>. 한 field 안의 개별 소프트웨어 모듈은 `#`으로 구분하고, 마지막 모듈 뒤 `#`은 선택이다.
- <strong>Diagnostic protocol identification (A.6)</strong> — CF가 ISO 11783 외에 추가로 지원하는 진단 프로토콜을 나타내는 비트필드다.

| 값 (비트) | 의미 |
|---|---|
| 00000000 | 추가 진단 프로토콜 없음 |
| 00000001 | J1939-73 |
| 00000010 | ISO 14230 (KWP 2000, ISO 15765-3 transport protocol 사용) |
| 00000100 | ISO 14229-3 (UDS on CAN) |
| 그 외 비트 | ISO 할당 예약 |

- <strong>Number of option bytes (A.12)</strong> — 한 functionality가 지원하는 option을 나타내는 후속 바이트 수다. option byte 뒤쪽의 0인 바이트(trailing zero)는 모두 생략하고 개수에도 세지 않는다. option byte가 없는 functionality는 0으로 설정한다.
- <strong>Product identification (A.14~A.16)</strong> — 제조사가 부여하는 제품 식별로, 제품 명판의 번호에 해당한다. 차량이면 VIN과 같을 수 있고, VT 같은 독립 시스템이면 ECU 식별 번호와 같을 수 있다. <strong>code + brand 조합은 전 세계에서 유일해야 하고</strong>, model은 brand 내에서 제품을 유일하게 식별한다.

## Annex B — 진단 정보 메시지 정의 (normative)

CF가 지원해야 하는 진단 메시지들의 PGN·형식 정의다. 상당수가 SAE J1939 / J1939-73에 정의된 메시지를 기반으로 하되, ISO 11783에서 요구하는 파라미터를 지정한 것이다.

### B.1 ECU identification information (PGN 64965)

SAE J1939DA와 같은 메시지 기반이며, ECU 관련 식별 정보를 나른다. <strong>한 ECU 내 모든 CF는 동일한 ECU identification 정보를 보내야 한다.</strong> 필드 간 구분자는 ASCII `*`다.

| 항목 | 값 |
|---|---|
| 전송 주기 | On request |
| 데이터 길이 | 가변 |
| Data page / PDU format / PDU specific | 0 / 253 / 197 |
| 기본 우선순위 | 6 |
| PGN | 64965 (0x00FDC5) |

데이터 구성(각 필드 뒤에 `*` 구분자): ECU part number → ECU serial number → ECU location → ECU type → ECU manufacturer name → ECU hardware ID 순서다.

### B.2 Software identification (PGN 65242)

CF의 소프트웨어 버전(들)과 CF가 요구하는 ECU 관련 소프트웨어 버전을 알리는 메시지다. 역시 SAE J1939DA 기반이다.

| 항목 | 값 |
|---|---|
| 전송 주기 | On request |
| 데이터 길이 | 가변 |
| Data page / PDU format / PDU specific | 0 / 254 / 218 |
| 기본 우선순위 | 6 |
| PGN | 65242 (0x00FEDA) |

- Byte 1: software identification field 수 (A.3)
- Byte 2~n: software identification 문자열 (A.4)

:::details 소프트웨어 식별 문자열 구조 예시
field 3개짜리 CF(첫 field에 모듈 4개, 둘째에 2개, 셋째에 1개)라면 Byte 1은 0x03이고, 문자열은 `VT1.5#Module1 3.1#Module2 2.0#Module3 2.0#*OpSys XY MMDDYY2.12#Spooler 2.0#*Bootloader 2.12*` 형태가 된다. `#`이 모듈 구분, `*`이 field 구분이며 마지막 field 뒤에도 `*`가 붙는다.
:::

### B.3 ISOBUS certification

ISOBUS certification 메시지는 ISO 11783-7의 규정을 따른다.

### B.4 ISO 11783 NAME

ISO 11783-5의 규정을 따른다. industry, device class, function 코드는 해당 CF가 보낸 address claim 메시지에 실려 있으며, 코드 값 자체는 ISO 11783-1에 규정된다. 즉 진단 UI는 address claim에서 NAME 정보를 얻는다.

### B.5 Diagnostic protocol (PGN 64818)

각 CF는 자신이 지원하는 진단 프로토콜을 알리기 위해 이 메시지를 보내야 한다.

| 항목 | 값 |
|---|---|
| 전송 주기 | On request |
| 데이터 길이 | 8 bytes |
| Data page / PDU format / PDU specific | 0 / 253 / 50 |
| 기본 우선순위 | 6 |
| PGN | 64818 (0x00FD32) |

- Byte 1: diagnostic protocol identification (A.6)
- Byte 2~8: ISO 할당 예약

### B.6 Active diagnostic trouble codes — DM1 (PGN 65226)

SAE J1939-73의 DM1과 같은 메시지 기반으로, <strong>현재 활성인 DTC</strong>만을 전달한다.

<strong>전송 규칙</strong>이 이 메시지의 핵심이다.

- DTC가 활성 고장이 되는 순간 전송하고, 이후 <strong>1초에 1회</strong> 주기로 전송한다.
- 1초 이상 활성이었던 고장이 비활성이 되면, 상태 변화를 반영한 DM1을 한 번 더 보내고 그 오류에 대한 DM1은 중단한다.
- 1초 갱신 주기 내에 다른 DTC의 상태가 바뀌면 새 DM1을 즉시 보낸다.
- 고빈도 간헐 고장으로 인한 메시지 폭주를 막기 위해 <strong>DTC당 초당 1회 이하의 상태 변화만 전송</strong>해야 한다. 1초 안에 활성/비활성이 두 번 바뀐 DTC는 활성화를 알리는 메시지 한 번, 다음 주기 전송에서 비활성을 알리는 메시지 한 번으로 처리된다.
- 하나 이상의 오류가 활성인 동안 가능하면 매초 전송하고, 요청(request)에도 응답한다. ISO 11783-3 타이밍 제약으로 전송이 불가하면 다음 1초 간격에 전송을 시작한다.

| 항목 | 값 |
|---|---|
| 데이터 길이 | 가변 |
| Data page / PDU format / PDU specific | 0 / 254 / 202 |
| 기본 우선순위 | 6 |
| PGN | 65226 (0x00FECA) |

데이터 형식(DTC 1개 기준):

| 바이트 | 내용 |
|---|---|
| 1, 2 | Reserved, 0xFF로 설정 |
| 3 | SPN 하위 8비트 |
| 4 | SPN 두 번째 바이트 |
| 5 (bits 8–6) | SPN 상위 3비트 |
| 5 (bits 5–1) | FMI |
| 6 (bit 8) | SPN conversion method (0으로 설정) |
| 6 (bits 7–1) | Occurrence count |

- occurrence count를 알 수 없으면 0x7F로 설정한다.
- <strong>활성 고장이 없으면 Byte 3~6을 0으로</strong> 설정해 보낸다.
- 활성 DTC가 2개 이상이면 ISO 11783-3의 transport protocol을 사용해야 한다. 이때 Byte 1~2(reserved)는 반복하지 않고, DTC마다 Byte 3~6 형식이 반복된다.

### B.7 Previously active diagnostic trouble codes — DM2 (PGN 65227)

SAE J1939-73의 DM2와 같은 메시지 기반으로, <strong>과거에 활성이었던(previously active) DTC</strong>만을 전달한다. 송신 컴포넌트의 진단 이력을 네트워크의 다른 컴포넌트에 알리는 용도이며, 데이터에는 과거 활성 DTC 목록과 각각의 occurrence count가 담긴다. 이 메시지를 보낼 때는 <strong>occurrence count가 0이 아닌 모든 previously active DTC를 전부 포함</strong>해야 한다.

| 항목 | 값 |
|---|---|
| 전송 주기 | <strong>On request only</strong> (주기 전송 없음) |
| 데이터 길이 | 가변 |
| Data page / PDU format / PDU specific | 0 / 254 / 203 |
| 기본 우선순위 | 6 |
| PGN | 65227 (0x00FECB) |

- PGN을 지원하지 않는 경우 <strong>NACK</strong>이 요구된다 (ISO 11783-3, PGN 59392 Acknowledgement).
- 바이트 배치는 DM1과 동일하다: Byte 1~2 reserved(0xFF), Byte 3~5에 19비트 SPN + 5비트 FMI, Byte 6에 conversion method(0) + occurrence count. occurrence count 미상 시 0x7F, 고장 없음 시 Byte 3~6을 0으로 설정한다.
- DM1과 달리 transport protocol은 "DTC 2개 이상"이 아니라 <strong>단일 프레임으로 보낼 수 없을 때만</strong> 사용한다. transport protocol에서 Byte 1~2는 반복하지 않고 DTC마다 Byte 3~6이 반복된다.

### B.8 Diagnostic data clear/reset previously active DTCs — DM3 (PGN 65228)

DM3는 별도 데이터가 아니라 <strong>요청(request)에 의해 동작하는 클리어 명령</strong>이다. 이 PG가 요청되면 previously active DTC(DM2)에 관한 진단 정보가 모두 삭제된다. <strong>active DTC 관련 데이터는 영향받지 않는다.</strong>

| 항목 | 값 |
|---|---|
| PGN | 65228 (0x00FECC) |

응답 규칙:

- 클리어 완료 시, 또는 지울 고장이 없을 때 → positive acknowledgement (ISO 11783-3, PGN 59392)
- 클리어 요청을 지원하지만 지금 수행할 수 없을 때 → negative acknowledgement
- 요청이 <strong>global address로 전송된 경우 → 어떤 ACK/NACK도 보내지 않는다</strong> (설계자 주의사항)

:::details DM3 요청 흐름 예시
- 예시 1 — 정상 클리어: 진단 UI 또는 서비스 툴이 특정 ECU에 Request PGN 59904로 PGN 65228을 요청 → ECU가 클리어를 수행하고 PGN 65228에 대한 positive Acknowledgement(PGN 59392)로 응답한다.
- 예시 2 — 수행 불가: ECU가 클리어 요청 자체는 지원하지만 지금 수행할 수 없는 상태 → negative Acknowledgement로 응답한다.
- 예시 3 — 전체 클리어: 진단 UI가 global address로 PGN 65228을 요청 → 가능한 모든 ECU가 진단 데이터를 지우지만, global 요청이므로 <strong>아무도 ACK/NACK을 보내지 않는다</strong>.
:::

### B.9 Control function functionalities (PGN 64654)

CF가 지원하는 모든 functionality와 그 generation, functionality option을 식별하는 메시지다.

| 항목 | 값 |
|---|---|
| 전송 주기 | On request |
| 데이터 길이 | 가변, 최소 8 bytes |
| Data page / PDU format / PDU specific | 0 / 252 / 142 |
| 기본 우선순위 | 6 |
| PGN | 64654 (0x00FC8E) |

<strong>하위 호환성 규칙</strong> — 이 메시지는 향후 업데이트로 functionality의 option byte 수가 늘어날 수 있으므로, 수신자는 다음 규칙으로 파싱해야 한다.

- ISO 할당 예약(reserved) functionality 특성 값은 오류 없이 파싱해야 한다.
- 이 문서에 규정된 것보다 option byte 수가 크면, 수신 CF는 정의되지 않은 option byte를 무시하고 아는 option byte만 파싱한다.

데이터 구성:

| 바이트 | 내용 | 참조 |
|---|---|---|
| 1 | 0xFF 고정. 수신자는 Byte 1이 0xFF가 아니면 메시지를 처리하지 않아야 한다 | — |
| 2 | 이 메시지에 보고되는 functionality 수 | A.9 |
| 3 | 첫 번째 functionality | A.10 |
| 4 | 첫 번째 functionality의 generation | A.11 |
| 5 | 첫 번째 functionality의 option byte 수 | A.12 |
| 6 … n | 첫 번째 functionality의 option (제공 시). 비트로 지원 option 표시 | ISOBUS.net의 Functionality/Option list |
| n+1 이후 | 두 번째 이후 functionality마다 (functionality, generation, option byte 수, option byte들) 반복 | — |

- 8바이트를 초과하면 transport protocol로 전송하고, 8바이트 미만이면 남는 바이트를 0xFF로 채운다.

:::details functionality 메시지 인코딩 예시
- 예시 1 — UT generation 2 + minimum CF generation 1인 VT: `FF 02 00 01 00 01 02 00` — Byte 2=0x02(functionality 2개), (0x00 minimum CF, gen 1, option 0개), (0x01 UT, gen 2, option 0개).
- 예시 2 — UT gen 3, AUX-N gen 1(function type 0·2), TC-BAS gen 1, TC-GEO gen 1(control channel 4개), TECU gen 1(Class 1·Navigation), minimum CF gen 1을 갖춘 Working Set Master: functionality 6개가 위 반복 구조로 23바이트에 걸쳐 인코딩된다 (transport protocol 사용). AUX-N은 option byte 1개(00000101 = function type 0, 2), TC-GEO는 option byte 1개(0x04 = control channel 수), TECU는 option byte 1개(00001001 = Class 1, Navigation)를 가진다.
- 예시 3 — minimum CF generation 1만 따르는 proprietary CF: `FF 01 00 01 00 FF FF FF` — 8바이트 미만이므로 나머지를 0xFF로 채운다.
:::

functionality 코드 값 자체(0x00 minimum CF, 0x01 UT 1st gen, 0x02 UT, 0x06 AUX-N, 0x08 TC-BAS, 0x0A TC-GEO, 0x0E TECU 등)와 option 비트 정의는 이 문서가 아니라 <strong>ISOBUS 온라인 데이터베이스(www.ISOBUS.net)의 Functionality/Option list</strong>에서 관리된다. 3판에서 온라인 DB로 이관된 부분이 바로 이것이다.

### B.10 Product identification (PGN 64653)

각 CF는 자신이 사용된 <strong>제품(product)</strong> 정보를 제공해야 한다. 서비스 기술자는 이 정보로 어떤 CF가 어떤 제품에 속하는지 알 수 있고, 딜러·제조사에 문의할 때 제품 식별에도 쓴다.

| 항목 | 값 |
|---|---|
| 전송 주기 | On request |
| 데이터 길이 | 가변 |
| Data page / PDU format / PDU specific | 0 / 252 / 141 |
| 기본 우선순위 | 6 |
| PGN | 64653 (0x00FC8D) |

- 데이터 구성(각 필드 뒤에 `*` 구분자): product identification code (A.14) → product identification brand (A.15) → product identification model (A.16). 예를 들어 Brand B의 모델 1926i, 식별 코드 1234567890ABC라면 `1234567890ABC*Brand B*1962i*` 형태다.
- <strong>한 제품의 모든 CF는 이 PGN 요청에 동일한 product identification 정보로 응답</strong>해야 한다.
- 향후 버전에서 `*` 구분 필드가 추가될 수 있으며, 이 문서 기준으로 구현된 CF는 최소한 이 문서에 규정된 정보를 인코딩할 수 있어야 한다.

## Annex C — Network configuration (normative)

### C.1 네트워크 구성

Figure C.1은 진단 시스템과 ISO 11783 진단 커넥터 연결을 지원해야 하는 네트워크 구성 예를 보여준다. 구성 요소를 텍스트로 정리하면 다음과 같다.

- <strong>Product 1</strong> — 트랙터 또는 자주식 작업기. 내부에 tractor ECU CF, OEM 설치 ECU(CF1·CF2 포함), tractor bus의 ECU 1~n, ISO 11783 bus가 있다.
- <strong>Product 2</strong> — ISO 11783 aftermarket ECU (CF n 포함). ISO 11783 bus에 연결된다.
- <strong>implement CF</strong> — breakaway connector 너머 작업기 측에서 ISO 11783 bus에 연결된다.
- <strong>진단 툴</strong> — diagnostic tool interface를 거쳐 <strong>ISO 11783 diagnostic connector</strong>로 네트워크에 접속한다. 진단 커넥터는 tractor bus와 ISO 11783 bus 양쪽에 접근할 수 있는 지점에 위치한다.

요지는 OEM ECU든 애프터마켓 ECU든 작업기 ECU든, 모두 진단 커넥터를 통해 접근 가능한 하나의 진단 체계 안에 있어야 한다는 것이다.

### C.2 진단 커넥터

진단 커넥터와 그 설치는 ISO 11783-2를 따라야 한다.

## Annex D — 네트워크 설정 화면 예시 (informative)

진단 UI가 어떤 화면을 제공해야 하는지 감을 주는 예시 모음이다. informative이므로 화면 구성 자체는 강제가 아니다.

| 절 | 화면 | 표시 내용 |
|---|---|---|
| D.1 | Network information screen | 네트워크의 CF 목록. CF마다 NAME 구성 요소(Industry, Device Class, Function, Function Instance, ECU Instance, Address)와 제조사·part number·serial number·SW 버전·적합성 인증(인증 ID + 날짜)을 표시 (6.2 대응) |
| D.2 | Network statistics screen | CAN_H/CAN_L 전압, bus load(%), network message count, CAN 에러 카운트(Stuff/Form/Ack/Bit 1/Bit 2/CRC error) (6.3 대응) |
| D.3 | Network diagnostic screen | CF별 고장 목록. CF의 NAME 정보와 함께 진단 프로토콜(예: SAE J1939-73, ISO 15765), active DTC의 SPN·FMI·occurrence count 표시 (6.4 대응) |
| D.4 | Connected system functionalities screen | 현재 연결된 시스템에 구성된 functionality(UT, AUX-O, AUX-N, TC-BAS, TC-GEO, TC-SC, TECU 등)와 각 generation을 체크리스트로 표시 (6.5 대응) |
| D.5 | Implement capable functionalities screen | functionality별로 트랙터 측 실제 지원 generation과 작업기 측 실제 지원 generation을 나란히 비교 표시 (6.5 대응) |
| D.6 | Functionality alarm mask | 비호환 경고 화면. 요구 functionality(예: AUX-N type 2 입력)와 실제 가용 functionality(예: AUX-O type 0 입력)를 대비해 "Functionality Not Compatible" 알람을 띄우는 예 |

## Annex E — Failure mode indicator 정의 (normative)

### E.1~E.2 개요와 신호 범위 모델

FMI 사용 시 일관성을 위해 각 FMI의 의미를 정의한다. <strong>모든 FMI가 모든 SPN에 적용 가능한 것은 아니다.</strong> 예를 들어 SPN 1873(rear hitch position) 같은 입력을 진단하는 CF는 FMI 3·4(전압 계열)를 쓸 수 있고, 그 경우 FMI 5·6(전류 계열)은 쓰지 않는다.

FMI 설명에 쓰이는 기본 용어는 다음과 같다.

- <strong>Data</strong> — 전압·전류·PWM·데이터 스트림 형태로 전자 모듈에 전달되는, 물리적 상태에 관한 정보
- <strong>Real world</strong> — 전압·전류·PWM·데이터 스트림으로 측정 가능한 기계적 파라미터 또는 운전 조건
- <strong>Signal range</strong> — 신호 값 축을 영역(region)으로 나눈 모델. FMI가 어느 영역의 이상인지를 가리키는 기준이 된다.

신호 범위 영역 모델(Figure E.1)은 값 축을 낮은 쪽부터 f–d–j–h–c–i–k–e–g 순으로 배치한다.

| Region | 의미 |
|---|---|
| a | 전자 모듈이 측정 가능한 전체 신호 입력 범위 |
| b | 애플리케이션이 정의한, 물리적으로 가능한 전체 신호 범위 |
| c | 해당 실측정의 정상(normal) 범위 |
| d / e | 정상 미만 / 초과 — <strong>most severe</strong> 수준 |
| j / k | 정상 미만 / 초과 — moderately severe 수준 |
| h / i | 정상 미만 / 초과 — least severe 수준 |
| f | 물리적으로 가능한 범위보다도 낮음 → low source로의 단락(short) 시사 |
| g | 물리적으로 가능한 범위보다도 높음 → high source로의 단락 시사 |

### E.3 FMI 목록

| FMI | 의미 | Region / 비고 |
|---|---|---|
| 0 | Data valid but above normal — most severe | Region e. 데이터 방송은 정상 지속 |
| 1 | Data valid but below normal — most severe | Region d. 데이터 방송은 정상 지속 |
| 2 | Data erratic, intermittent or incorrect | 값이 error indicator로 대체됨. rationality 계열 |
| 3 | Voltage above normal or shorted to high source | Region g. error indicator로 대체 |
| 4 | Voltage below normal or shorted to low source | Region f. error indicator로 대체 |
| 5 | Current below normal or open circuit | Region f. error indicator로 대체 |
| 6 | Current above normal or grounded circuit | Region g. error indicator로 대체 |
| 7 | Mechanical system not responding or improperly adjusted | 전기·전자 고장이 아닌 기계적 원인. rationality 계열 |
| 8 | Abnormal frequency or pulse width or period | 주파수·duty가 Region b 밖. FMI 4·5와 함께 고려 |
| 9 | Abnormal update rate | 네트워크 수신 데이터의 갱신 주기가 기대치 밖. rationality 계열 |
| 10 | Abnormal rate of change | 값은 유효하나 변화율이 정상 범위 밖. 방송은 정상 지속. rationality 계열 |
| 11 | Root cause not known | 고장은 검출됐으나 정확한 원인 미상. error indicator로 대체 |
| 12 | Bad intelligent unit or component | ECU 교체가 필요한 내부 고장. rationality 계열 |
| 13 | Out of calibration | 캘리브레이션 불량(SW 캘리브레이션 구버전 또는 기계 서브시스템 캘리브레이션 이탈). 신호 범위 모델과 무관 |
| 14 | Special instructions | 고장을 소수 후보로만 좁힐 수 있는 경우. 제조사 절차 참조 필요 (아래 참조) |
| 15 | Data valid but above normal — least severe | Region i. 방송 정상 지속 |
| 16 | Data valid but above normal — moderately severe | Region k. 방송 정상 지속 |
| 17 | Data valid but below normal — least severe | Region h. 방송 정상 지속 |
| 18 | Data valid but below normal — moderately severe | Region j. 방송 정상 지속 |
| 19 | Received network data in error | 네트워크로 받은 값이 error indicator(0xFE, ISO 11783-3 참조)로 대체되어 있음. 고장 위치는 데이터를 <strong>송신한 모듈 쪽</strong>(센서 직결 모듈)이지 수신 모듈이 아님 |
| 20–30 | Reserved | 향후 할당 예약 |
| 31 | Condition exists | SPN이 가리키는 상태가 존재함. 적용할 FMI가 없거나 SPN 이름 자체가 컴포넌트+고장 모드를 설명하는 경우. SPN도 not available이면 "not available" 의미 |

주요 FMI 해설:

- <strong>FMI 2 (erratic/incorrect)</strong> — erratic·intermittent는 현실 세계에서 불가능한 속도로 변하는 측정값으로, 측정 장치나 그 연결의 이상이 원인이다. incorrect는 수신되지 않은 데이터와 FMI 3~6 상황에 해당하지 않는 모든 잘못된 데이터를 포함하며, 시스템의 다른 정보와 모순되는 데이터도 포함한다(rationality 고장).
- <strong>FMI 3~6 (전압·전류 계열)</strong> — 각각 (a) 신호가 사전 정의된 한계 밖(Region f/g)인 경우와, (b) CF가 명령한 상태와 반대로 유지되는 외부 신호(예: low로 명령했는데 high 유지, on으로 명령했는데 전류 off 유지)인 경우 모두를 포함한다.
- <strong>FMI 14 (Special instructions)</strong> — 온보드 시스템이 고장을 단일 지점이 아닌 소수 후보로만 격리할 수 있을 때 사용한다. 서비스 기술자의 추가 진단 작업이 필요하며 보통 제조사가 그 절차를 제공한다. 용례는 (a) 배출가스 관련 진단에서 센서 범위 이탈인지 실제 값의 경계 상황인지 구분 불가한 경우, (b) 구형 SPN 611~615에서 상호작용하는 복수 회로 중 수리 대상 특정이 필요한 경우다.

:::info System Diagnostic Codes (SPN 611~615)
SPN 611~615는 특정 현장 교체 부품(field-replaceable component)에 귀속시킬 수 없는 고장을 나타내는 "System Diagnostic Code"다. 진단 정보를 특정 컴포넌트+고장 모드로 표현할 수 없을 때만 사용해야 하며(제조사 정의 코드는 표준화 관점에서 바람직하지 않으므로), 표준 SPN/FMI 형식을 유지하기 때문에 표준 진단 툴·전자 대시보드 등이 그대로 읽을 수 있다는 장점이 있다. 사용 사유로는 컴포넌트 단위 고장 격리 비용이 정당화되지 않는 경우, 새로운 차량 전체 진단 개념·전략 개발 중인 경우가 있다. 이들 SPN은 컴포넌트 특정적이지 않아 FMI 0~13, 15~31이 의미를 갖기 어려우므로 <strong>보통 FMI 14와 함께</strong> 쓰고, 기술자를 제조사 트러블슈팅 매뉴얼로 안내하는 것이 목적이다.
:::

## Bibliography

참고 문헌(informative)으로 ISO/IEC 7498(OSI 참조 모델), ISO/IEC 8859-1(Latin 1), ISO 11783-9(Tractor ECU), ISO 11898(CAN), ISO 14229-3(UDSonCAN), ISO 14230(KWP, DoK-Line), SAE J1939, SAE J1939DA(Digital Annex)가 열거된다.

## 정리 — Part 12 진단 메시지 한눈에 보기

| 메시지 | PGN | 전송 | 내용 |
|---|---|---|---|
| ECU identification information | 64965 (0xFDC5) | On request | ECU part no·serial no·location·type·제조사명·HW ID (`*` 구분) |
| Software identification | 65242 (0xFEDA) | On request | SW 식별 field 수 + SW 식별 문자열 (`*`·`#` 구분) |
| Diagnostic protocol | 64818 (0xFD32) | On request | 추가 지원 진단 프로토콜 비트필드 |
| DM1 (active DTC) | 65226 (0xFECA) | 상태 변화 시 + 활성 중 1 Hz | 현재 활성 DTC (SPN+FMI+OC) |
| DM2 (previously active DTC) | 65227 (0xFECB) | On request only | 과거 활성 DTC 목록 (OC≠0 전부) |
| DM3 (clear DTC) | 65228 (0xFECC) | Request로 트리거 | previously active DTC 클리어. active는 불변 |
| Control function functionalities | 64654 (0xFC8E) | On request | functionality + generation + option (ISOBUS.net DB 참조) |
| Product identification | 64653 (0xFC8D) | On request | 제품 code·brand·model (`*` 구분) |

여기에 address claim(NAME, ISO 11783-5)과 ISOBUS certification(ISO 11783-7)을 더하면 6.2~6.5가 요구하는 진단 UI 정보가 모두 채워진다. DTC의 고장 모드 의미는 Annex E의 FMI 0~31 정의를 따르고, functionality 코드·option 정의만 온라인 DB(ISOBUS.net)에서 관리된다는 점이 3판 구조의 특징이다.
