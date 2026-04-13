---
title: "DDI 주요 목록"
description: "ISOBUS Task Controller에서 사용하는 주요 DDI(Data Dictionary Identifier)를 정리한 참조 자료입니다."
date: 2026-04-13
tags: [ISOBUS, 부록]
---

# DDI 주요 목록

DDI(Data Dictionary Identifier)는 ISO 11783-11에 정의된 식별자로, Task Controller가 작업기의 측정값이나 설정값의 종류를 식별하는 데 사용한다. DDOP(Device Descriptor Object Pool) 안의 DPD(Device Process Data) 오브젝트에서 참조된다.

---

## 단위 범주별 DDI 목록

### 면적당 적용량 (Application Rate per Area)

| DDI | 이름 | 단위 | 설명 |
|-----|------|------|------|
| 1 | Setpoint Volume Per Area | ml/m² (× 10⁻⁶ L/m² = L/ha 환산 가능) | 면적당 설정 살포량 (액체) |
| 2 | Actual Volume Per Area | ml/m² | 면적당 실제 살포량 (액체) |
| 3 | Default Volume Per Area | ml/m² | 면적당 기본 살포량 |
| 6 | Setpoint Mass Per Area | mg/m² | 면적당 설정 살포량 (고체/분말) |
| 7 | Actual Mass Per Area | mg/m² | 면적당 실제 살포량 (고체/분말) |
| 8 | Default Mass Per Area | mg/m² | 면적당 기본 살포량 (고체) |
| 11 | Setpoint Count Per Area | count/m² | 면적당 설정 입자/씨앗 수 (파종기) |
| 12 | Actual Count Per Area | count/m² | 면적당 실제 입자/씨앗 수 |

---

### 단위 시간당 적용량 (Application Rate per Time)

| DDI | 이름 | 단위 | 설명 |
|-----|------|------|------|
| 16 | Setpoint Volume Per Time | ml/s | 시간당 설정 살포량 (액체) |
| 17 | Actual Volume Per Time | ml/s | 시간당 실제 살포량 |
| 21 | Setpoint Mass Per Time | mg/s | 시간당 설정 살포량 (고체) |
| 22 | Actual Mass Per Time | mg/s | 시간당 실제 살포량 (고체) |
| 116 | Setpoint Application Rate | 용도별 단위 | 설정 살포율 (범용). 단위는 DDI 맥락에 따라 결정 |
| 117 | Actual Application Rate | 용도별 단위 | 실제 살포율 (범용) |

---

### 작업 폭 (Working Width)

| DDI | 이름 | 단위 | 설명 |
|-----|------|------|------|
| 43 | Actual Working Width | mm | 현재 실제 작업 폭 |
| 44 | Setpoint Working Width | mm | 설정 작업 폭 |
| 45 | Default Working Width | mm | 기본 작업 폭 |

---

### 면적 (Area)

| DDI | 이름 | 단위 | 설명 |
|-----|------|------|------|
| 67 | Lifetime Total Area | m² | 기기 출하 후 누적 총 작업 면적 |
| 68 | Lifetime Effective Total Area | m² | 누적 유효 작업 면적 (중복 제외) |
| 69 | Lifetime In-Effective Total Area | m² | 누적 비유효 면적 (비작업 구간) |
| 70 | Total Area | m² | 현재 작업 세션의 총 면적 |
| 71 | Effective Total Area | m² | 현재 세션의 유효 면적 |
| 72 | In-Effective Total Area | m² | 현재 세션의 비유효 면적 |
| 141 | Lifetime Total Area (alternative) | m² | Lifetime Total Area 동의어로 쓰이는 경우 있음 |

---

### 거리/속도 (Distance / Speed)

| DDI | 이름 | 단위 | 설명 |
|-----|------|------|------|
| 46 | Actual Distance Traveled Per Time | mm/s | 현재 이동 속도 |
| 47 | Setpoint Distance Per Time | mm/s | 설정 이동 속도 |
| 57 | Lifetime Total Distance | m | 누적 총 이동 거리 |
| 58 | Total Distance | m | 현재 세션 이동 거리 |

---

### 섹션 제어 (Section Control)

| DDI | 이름 | 단위 | 설명 |
|-----|------|------|------|
| 160 | Section Control State | - | 섹션 제어 활성화 상태 (0=Off, 1=On) |
| 161 | Actual Section Control State | - | 실제 섹션 제어 상태 |
| 162 | Setpoint Section Control State | - | 설정 섹션 제어 상태 |

---

### 기기 정보 및 기타

| DDI | 이름 | 단위 | 설명 |
|-----|------|------|------|
| 0 | No DDI | - | 사용 안 함 (예약) |
| 130 | Last Loaded Weight | mg | 마지막으로 적재한 무게 |
| 131 | Last Unloaded Weight | mg | 마지막으로 하역한 무게 |
| 271 | Device Element Offset X | mm | 장치 요소의 기준점 대비 X축 오프셋 |
| 272 | Device Element Offset Y | mm | 장치 요소의 기준점 대비 Y축 오프셋 |
| 273 | Device Element Offset Z | mm | 장치 요소의 기준점 대비 Z축 오프셋 |
| 275 | Connector Type | - | 커넥터 유형 코드 |
| 276 | Connector X Offset | mm | 연결점의 X축 오프셋 |

---

## DDI 값 표현 방식

DDI 값은 모두 <strong>부호 있는 32비트 정수(int32)</strong>로 전송된다. 실제 단위 값으로 변환하려면 DDI별 해상도(Resolution)를 적용해야 한다.

예시:
- DDI 1 (Setpoint Volume Per Area): 1 bit = 0.000001 ml/m²
- DDI 43 (Actual Working Width): 1 bit = 1 mm
- DDI 67 (Lifetime Total Area): 1 bit = 1 m²

---

## 참고

- DDI 전체 목록은 AEF 공개 문서 및 ISO 11783-11 Data Dictionary에서 확인할 수 있다.
- isobus.net에서 DDI 검색 도구를 제공한다.
