---
title: "DDI 주요 목록"
description: "ISOBUS Task Controller에서 사용하는 주요 DDI(Data Dictionary Identifier)를 정리한 참조 자료입니다."
date: 2026-04-13
tags: [ISOBUS, 부록]
---

# DDI 주요 목록

DDI(Data Dictionary Identifier)는 ISO 11783-11이 규정하는 2바이트(16비트) 식별자로, Task Controller가 작업기의 측정값이나 설정값의 종류를 식별하는 데 사용한다. 개별 DDI 항목은 표준 문서 본문에 실려 있지 않고, ISO가 지명한 유지관리 기관(VDMA)이 관리하는 isobus.net의 ISOBUS Data Dictionary(온라인 사전 자체가 normative reference)에 정의된다. DDOP(Device Descriptor Object Pool) 안의 DPD(Device Process Data)·DPT(Device Property) 오브젝트에서 참조된다.

## 단위 범주별 DDI 목록

### 면적당 적용량 (Application Rate per Area)

| DDI | 이름 | 단위 | 설명 |
|-----|------|------|------|
| 1 | Setpoint Volume Per Area Application Rate as [mm³/m²] | mm³/m² (분해능 0.01, 1 L/ha = 100 mm³/m² = 원시값 10 000) | 면적당 설정 살포량 (액체) |
| 2 | Actual Volume Per Area Application Rate as [mm³/m²] | mm³/m² | 면적당 실제 살포량 (액체) |
| 3 | Default Volume Per Area Application Rate as [mm³/m²] | mm³/m² | 면적당 기본 살포량 |
| 6 | Setpoint Mass Per Area | mg/m² | 면적당 설정 살포량 (고체/분말). ISO 11783-10 Annex D 예시에서 15000 mg/m² = 150 kg/ha로 확인됨 |
| 7 | Actual Mass Per Area | mg/m² | 면적당 실제 살포량 (고체/분말) |
| 8 | Default Mass Per Area | mg/m² | 면적당 기본 살포량 (고체) |
| 11 | Setpoint Count Per Area | count/m² | 면적당 설정 입자/씨앗 수 (파종기) |
| 12 | Actual Count Per Area | count/m² | 면적당 실제 입자/씨앗 수 |

::: tip 확인 근거
DDI 6은 ISO 11783-10 Annex D 예시 문장에서 값과 함께 직접 확인했다. 개별 DDI의 이름·단위·분해능은 Part 10/11 본문에 없고 [isobus.net Data Dictionary](https://www.isobus.net/isobus/dDEntity)가 관리한다. DDI 1·2·3의 이름과 단위(mm³/m²), DDI 1의 분해능 0.01은 그 사전에서 확인했다(2026-10 기준). 대유량(분뇨 살포 등)용으로 ml/m² 단위를 쓰는 별도 DDI(588 Setpoint, 589 Actual, 591 Maximum, 592 Default)가 따로 있으니 DDI 1과 혼동하지 않는다.
:::

### 단위 시간당 적용량 (Application Rate per Time)

| DDI | 이름 | 단위 | 설명 |
|-----|------|------|------|
| 36 | Setpoint Volume Per Time Application Rate | mm³/s | 시간당 설정 살포량 (액체) |
| 37 | Actual Volume Per Time Application Rate | mm³/s | 시간당 실제 살포량 |
| 41 | Setpoint Mass Per Time Application Rate | mg/s | 시간당 설정 살포량 (고체) |
| 42 | Actual Mass Per Time Application Rate | mg/s | 시간당 실제 살포량 (고체) |

::: tip 혼동하기 쉬운 번호
이 표는 예전에 시간당 유량을 16·17, 시간당 질량을 21·22로 적었으나 isobus.net Data Dictionary로 확인한 결과 틀린 번호였다. 16·17은 Setpoint·Actual <strong>Spacing</strong> Application Rate(간격, mm)이고, 21·22는 Volume Per Volume Application Rate(mm³/m³)다. ISO 11783-10 Table F.2가 16·17을 Seeders/Planters의 권장 rate DDI로 드는 것도 파종 간격이기 때문이다. [TC 프로세스 데이터 챕터](/study/isobus/19-tc-process-data)의 36·37(mm³/s)이 맞다.
:::

### 작업 폭 (Working Width)

| DDI | 이름 | 단위 | 설명 |
|-----|------|------|------|
| 67 | Actual Working Width | mm | 실제 작업 폭. Device/Function(붐) 수준에서는 "On" 상태인 하위 섹션 폭의 합 |
| 70 | Maximum Working Width | mm | 최대 작업 폭. 붐 geometry의 필수 속성(offset X·Y와 함께 최소 구성) |
| 68 | Default Working Width | mm | 기본 작업 폭 |

Section이 복수 종류의 작업 폭을 제공하면 Section Controller는 <strong>Actual(67) → Maximum(70) → Default(68)</strong> 순으로 우선 사용해야 한다(ISO 11783-10 Annex F.3.5.2). "Setpoint Working Width"라는 명칭의 별도 DDI는 표준 본문에서 확인되지 않아 목록에서 제외했다.

### 면적 (Area)

| DDI | 이름 | 단위 | 설명 |
|-----|------|------|------|
| 116 | Total Area | m² | 현재 태스크(세션)의 총 작업 면적 |
| 271 | Lifetime Total Area | m² | 기기 출하 후 누적 총 작업 면적 (LOG 기능용) |

Effective/In-Effective(유효/비유효) 면적 계열 DDI는 isobus.net Data Dictionary에 존재하는 것으로 알려져 있으나, 이 스터디의 기준 자료(ISO 11783-10/-11 본문)에서는 그 식별번호를 확인할 수 없어 이번 검증에서는 신설하지 않았다.

### 거리/속도 (Distance / Speed)

| DDI | 이름 | 단위 | 설명 |
|-----|------|------|------|
| 46 | Actual Distance Traveled Per Time | mm/s | 현재 이동 속도 |
| 47 | Setpoint Distance Per Time | mm/s | 설정 이동 속도 |
| 117 | Total Distance | m | 현재 태스크(세션)의 총 이동 거리 |
| 272 | Lifetime Total Distance | m | 누적 총 이동 거리 (LOG 기능용) |
| 273 | Lifetime Ineffective Total Distance | m | 누적 비유효 이동 거리 (LOG 기능용) |

### 시간 (Time)

| DDI | 이름 | 단위 | 설명 |
|-----|------|------|------|
| 119 | Total Time | s | 현재 태스크의 총 작업 시간. TC-BAS 클라이언트 필수(ISO 11783-10 F.2.1). 단위는 Part 10 6.8.4 예 1의 DVP 배율(2.777778E-04 → hr)로 역산한 값 |
| 120 | Ineffective Total Time | 확인 필요 | 비유효 작업 시간 (Annex F 트랙터 예시) |
| 274 | Lifetime Effective Total Time | 확인 필요 | 누적 유효 작업 시간. LOG 클라이언트 필수(F.2.4) |
| 275 | Lifetime Ineffective Total Time | 확인 필요 | 누적 비유효 작업 시간 (LOG 트랙터 예시) |

### 작업 상태 (Work State)

| DDI | 이름 | 단위 | 설명 |
|-----|------|------|------|
| 141 | Actual Work State | - | Device/Function(붐) 단위의 실제 작업 On/Off 상태 |
| 160 | Section Control State | - | 섹션 제어 활성화 상태 (0=Off, 1=On) |
| 161 | Actual Condensed Work State | - | 여러 섹션의 실제 On/Off 상태를 비트로 압축한 값 |
| 290 | Setpoint Condensed Work State | - | 여러 섹션의 설정 On/Off 상태를 비트로 압축한 값 |

### 기기 정보 및 기타

| DDI | 이름 | 단위 | 설명 |
|-----|------|------|------|
| 0 | No DDI | - | 사용 안 함 (예약) |
| 130 | Last Loaded Weight | mg | 마지막으로 적재한 무게 |
| 131 | Last Unloaded Weight | mg | 마지막으로 하역한 무게 |
| 134 | Device Element Offset X | mm | 장치 요소의 기준점 대비 X축 오프셋 |
| 135 | Device Element Offset Y | mm | 장치 요소의 기준점 대비 Y축 오프셋 |
| 136 | Device Element Offset Z | mm | 장치 요소의 기준점 대비 Z축 오프셋 |
| 157 | Connector Type | - | 커넥터 유형 코드 (property로 정의되는 것이 일반적) |
| 276 | Lifetime Total Fuel Consumption | - | 누적 총 연료 소비량 (LOG 기능용) |

Connector·Navigation 타입 device element는 별도의 "Connector Offset" DDI 없이 위 Offset X/Y(134/135)를 그대로 사용한다(ISO 11783-10 Annex F.3.4.2).

### 제어·지연·로깅 (ISO 11783-10 본문·Annex F에서 확인)

| DDI | 이름 | 단위 | 설명 |
|-----|------|------|------|
| 142 | Physical Setpoint Time Latency | ms | setpoint 변경이 실제로 반영되기까지의 시간(T4−T2). 양수만 가능. TC가 명령을 앞당기는 데 쓴다(F.3.4.6) |
| 143 | Physical Actual Time Latency | 확인 필요 | 실제 값의 측정 지연. 음수 가능. 맵 위치 보정용(F.3.4.6) |
| 147 (0093₁₆) | Log Count | - | 여러 DDI를 한 로그 묶음으로 남길 때 가장 높은 반복률로 보낸다(6.8.4) |
| 158 | Prescription Control State | - | setpoint가 있는 붐에 settable + on change로 둔다. TC는 rate 명령 전에 ENABLED로 설정(F.3.4.4) |
| 178 | Element Type Instance | - | 운전자가 빈을 고를 수 있게 Bin element 안에 둔다(F.3.3) |
| 179 | Actual Cultural Practice | - | 붐이 여럿일 때 붐 Function이나 그 아래 Bin에 두어 작업을 구별한다(F.3.3) |
| 205 | SC Turn On Time | 확인 필요 | 섹션 켜기 지연. 붐에 settable + on change. TC-SC가 on 명령을 앞당긴다(F.3.5.5) |
| 206 | SC Turn Off Time | 확인 필요 | 섹션 끄기 지연. 205와 같은 규칙(F.3.5.5) |

이름은 Part 10 Annex F 그림과 본문에서 확인했다. 값 코드(ENABLED/ON 등)와 단위가 비어 있는 항목은 온라인 사전에서 확인해야 한다.

### 제품 수량 (Product Quantity)

| DDI | 이름 | 단위 | 설명 |
|-----|------|------|------|
| 72 | Actual Volume Content | ml | 제품(액체)의 실제 수량. Product의 QuantityDDI로 사용 |
| 75 | Actual Mass Content | g | 제품(고체)의 실제 수량 |
| 78 | Actual Count Content | count | 제품(개수 단위)의 실제 수량 |

### 특수/예약 DDI

| DDI | 값 | 이름 | 설명 |
|-----|------|------|------|
| DFFE₁₆ | 57342 | Parameter Group Number Value | PGN 단위 로깅 시 DataLogDDI에 사용 (DataLogPGN·StartBit·StopBit와 조합) |
| DFFF₁₆ | 57343 | Request Default Process Data | device element 0에서만 요청 가능. 클라이언트가 스스로 정한 데이터·주기·트리거로 로깅하게 하는 트리거 |
| FFFF₁₆ | 65535 | Not available | 오류 응답 등에서 특정 element/DDI와 무관함을 나타내는 sentinel 값 |

## DDI 값 표현 방식

DDI 값은 모두 <strong>부호 있는 32비트 정수(int32, −2³¹~2³¹−1)</strong>로 전송된다(ISO 11783-10 Annex A ProcessDataValue 정의). 실제 단위 값으로 변환하려면 DDI별 해상도(Resolution)를 적용해야 한다.

예시:
- DDI 1 (Setpoint Volume Per Area): 1 bit = 0.01 mm³/m² (1 L/ha = 원시값 10 000)
- DDI 67 (Actual Working Width): 1 bit = 1 mm
- DDI 271 (Lifetime Total Area): 1 bit = 1 m²

위 해상도 수치는 예시이며, 각 DDI의 공식 해상도·값 범위는 isobus.net의 ISOBUS Data Dictionary에서 확인해야 한다.

::: info DDI 1 분해능의 근거
DDI 1의 단위 mm³/m²와 분해능 0.01은 isobus.net Data Dictionary 항목에서 확인했다(CAN 범위 0~2 147 483 647, 표시 범위 0.00~21 474 836.47). [TC 프로세스 데이터 챕터](/study/isobus/19-tc-process-data) §1·§6의 계산(1 L/ha = 원시값 10 000)과 일치한다.
:::

## 참고

- DDI 전체 목록은 AEF 공개 문서 및 ISO 11783-11 Data Dictionary에서 확인할 수 있다.
- isobus.net에서 DDI 검색 도구를 제공한다.
