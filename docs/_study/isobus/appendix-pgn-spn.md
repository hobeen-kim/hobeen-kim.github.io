---
title: "PGN/SPN 주요 목록"
description: "ISOBUS/J1939에서 자주 사용하는 PGN과 SPN을 표로 정리한 참조 자료입니다."
date: 2026-04-13
tags: [ISOBUS, 부록]
---

# PGN/SPN 주요 목록

---

## PGN (Parameter Group Number) 주요 목록

PGN은 J1939 29비트 CAN ID에서 추출되는 18비트 값으로, 메시지의 종류를 식별한다.

| PGN (Dec) | PGN (Hex) | 이름 | 용도 | 데이터 바이트 | 전송 주기 |
|-----------|-----------|------|------|-------------|----------|
| 60928 | 0xEE00 | Address Claimed | 노드 주소 선언/충돌 해결 | 8 | 이벤트 |
| 60416 | 0xEC00 | TP.CM (Transport Protocol - Connection Management) | 멀티패킷 전송 연결 관리 (BAM, RTS, CTS, EOM, Abort) | 8 | 이벤트 |
| 60160 | 0xEB00 | TP.DT (Transport Protocol - Data Transfer) | 멀티패킷 데이터 전송 | 8 | 이벤트 |
| 61440 | 0xF000 | ETP.CM (Extended Transport Protocol - Connection Management) | 1,785바이트 초과 데이터 연결 관리 | 8 | 이벤트 |
| 61184 | 0xEF00 | ETP.DT (Extended Transport Protocol - Data Transfer) | 대용량 확장 TP 데이터 전송 | 8 | 이벤트 |
| 59904 | 0xEA00 | Request PGN | 특정 PGN 데이터 요청 | 3 | 이벤트 |
| 61444 | 0xF004 | EEC1 (Electronic Engine Controller 1) | 엔진 토크 모드, 실제 토크, 엔진 회전수 | 8 | 10 ms |
| 61443 | 0xF003 | EEC2 (Electronic Engine Controller 2) | 가속 페달 위치, 엔진 부하 | 8 | 50 ms |
| 61445 | 0xF005 | ETC1 (Electronic Transmission Controller 1) | 변속기 출력 회전수, 기어 | 8 | 10 ms |
| 65262 | 0xFEEE | ET1 (Engine Temperature 1) | 엔진 냉각수 온도, 연료 온도 | 8 | 1000 ms |
| 65263 | 0xFEEF | EFL/P1 (Engine Fluid Level/Pressure 1) | 엔진 오일 압력, 수위 | 8 | 500 ms |
| 65267 | 0xFEF3 | Vehicle Position (GNSS 위치) | 위도, 경도 | 8 | 100 ms |
| 65256 | 0xFEE8 | Vehicle Direction/Speed | 차량 속도, 방향 | 8 | 100 ms |
| 65093 | 0xFE45 | Wheel-Based Machine Speed | 바퀴 기반 속도, 방향 (ISOBUS TECU) | 8 | 100 ms |
| 65096 | 0xFE48 | Ground-Based Speed | 레이더/GPS 기반 실제 지면 속도 | 8 | 100 ms |
| 65091 | 0xFE43 | PTODE (PTO Drive Engagement) | PTO 회전수, 상태 | 8 | 100 ms |
| 57344 | 0xE000 | VT to ECU (Virtual Terminal to ECU) | VT가 작업기 ECU로 보내는 명령/입력 | 8 | 이벤트 |
| 57600 | 0xE100 | ECU to VT (ECU to Virtual Terminal) | 작업기 ECU가 VT로 보내는 응답/요청 | 8 | 이벤트 |
| 65534 | 0xFFFE | TC to Working Set (Task Controller to WS) | TC 명령 전달 | 8 | 이벤트 |
| 65535 | 0xFFFF | Working Set to TC | 작업 세트의 TC 응답/측정값 | 8 | 이벤트 |
| 60160 | 0xEB00 | Object Pool Transfer (TP.DT) | VT 오브젝트 풀 업로드 (TP 사용) | - | 이벤트 |
| 65226 | 0xFECA | DM1 (Active DTCs) | 현재 활성 고장 코드 목록 | 가변 | 1000 ms |
| 65227 | 0xFECB | DM2 (Previously Active DTCs) | 이전 발생 고장 코드 목록 | 가변 | 요청 시 |

---

## SPN (Suspect Parameter Number) 주요 목록

SPN은 PGN 내에서 개별 측정 파라미터를 식별하는 번호다.

| SPN | 이름 | 속한 PGN | 바이트 위치 | 길이 (bit) | 해상도 | 오프셋 | 범위 |
|-----|------|----------|-----------|-----------|--------|--------|------|
| 190 | Engine Speed | EEC1 (61444) | 4-5 | 16 | 0.125 rpm/bit | 0 | 0 ~ 8,031.875 rpm |
| 91  | Accelerator Pedal Position 1 | EEC2 (61443) | 2 | 8 | 0.4 %/bit | 0 | 0 ~ 100 % |
| 92  | Engine Percent Load at Current Speed | EEC2 (61443) | 3 | 8 | 1 %/bit | -125 % | -125 ~ 125 % |
| 94  | Engine Fuel Delivery Pressure | EFL/P1 (65263) | 1 | 8 | 4 kPa/bit | 0 | 0 ~ 1,000 kPa |
| 100 | Engine Oil Pressure | EFL/P1 (65263) | 4 | 8 | 4 kPa/bit | 0 | 0 ~ 1,000 kPa |
| 110 | Engine Coolant Temperature | ET1 (65262) | 1 | 8 | 1 °C/bit | -40 °C | -40 ~ 210 °C |
| 174 | Engine Fuel Temperature 1 | ET1 (65262) | 2 | 8 | 1 °C/bit | -40 °C | -40 ~ 210 °C |
| 513 | Actual Gear Ratio | ETC1 (65445) | 5-6 | 16 | 0.001/bit | -7.9 | -7.9 ~ 7.9 |
| 524 | Transmission Output Shaft Speed | ETC1 (65445) | 1-2 | 16 | 0.125 rpm/bit | 0 | 0 ~ 8,031.875 rpm |
| 84  | Wheel-Based Vehicle Speed | WBMS (65093) | 2-3 | 16 | 0.001 m/s/bit | 0 | 0 ~ 65.535 m/s |
| 598 | Wheel-Based Machine Direction | WBMS (65093) | 1 (bit 2-3) | 2 | - | - | Forward / Reverse / Error |
| 1862 | Ground-Based Machine Speed | GBS (65096) | 2-3 | 16 | 0.001 m/s/bit | 0 | 0 ~ 65.535 m/s |
| 584 | PTO Output Shaft Speed (Front) | PTODE (65091) | 3-4 | 16 | 0.125 rpm/bit | 0 | 0 ~ 8,031.875 rpm |
| 1113 | Latitude | Vehicle Position (65267) | 1-4 | 32 | 10⁻⁷ deg/bit | -210° | -90 ~ 90° |
| 1114 | Longitude | Vehicle Position (65267) | 5-8 | 32 | 10⁻⁷ deg/bit | -210° | -180 ~ 180° |
| 1213 | Malfunction Indicator Lamp Status | DM1 (65226) | 1 (bit 7-8) | 2 | - | - | On / Off |
| 1215 | Protect Lamp Status | DM1 (65226) | 1 (bit 3-4) | 2 | - | - | On / Off |

---

## PGN 구조 요약

J1939 29비트 CAN ID의 구성:

```
[28:26] Priority (3비트)   - 메시지 우선순위 (0=최고, 7=최저)
[25]    Reserved (1비트)   - 항상 0
[24]    Data Page (1비트)  - PGN 공간 확장 (0 또는 1)
[23:16] PF (1바이트)       - PDU Format (< 240: PDU1, >= 240: PDU2)
[15:8]  PS (1바이트)       - PDU1: 목적지 주소(DA), PDU2: 그룹 확장
[7:0]   SA (1바이트)       - 송신 노드 주소
```

- **PDU1 (PF < 0xF0)**: 특정 노드에 전송. PGN에 PS(DA)가 포함되지 않는다.
- **PDU2 (PF >= 0xF0)**: 브로드캐스트. PGN = DP + PF + PS (3바이트).
