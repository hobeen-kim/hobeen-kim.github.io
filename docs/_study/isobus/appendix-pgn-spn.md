---
title: "PGN/SPN 주요 목록"
description: "ISOBUS/J1939에서 자주 사용하는 PGN과 SPN을 표로 정리한 참조 자료입니다."
date: 2026-04-13
tags: [ISOBUS, 부록]
---

# PGN/SPN 주요 목록

## PGN (Parameter Group Number) 주요 목록

PGN은 J1939 29비트 CAN ID에서 추출되는 18비트 값으로, 메시지의 종류를 식별한다. ISO 11783이 직접 정의하는 PGN은 근거 Part를, SAE J1939에서 정의된 PGN은 "J1939 정의"를 표기했다.

| PGN (Dec) | PGN (Hex) | 이름 | 용도 | 데이터 바이트 | 전송 주기 |
|-----------|-----------|------|------|-------------|----------|
| 60928 | 0xEE00 | Address Claimed | 노드 주소 클레임/충돌 해결. SA=254면 Cannot Claim (Part 5) | 8 | 이벤트 (파워온·요청 시) |
| 65240 | 0xFED8 | Commanded Address | 특정 NAME의 CF에 새 SA 지정. 9바이트이므로 BAM으로 전송 (Part 5) | 9 | 이벤트 |
| 59904 | 0xEA00 | Request PGN | 특정 PGN 데이터 요청 (Part 3) | 3 | 이벤트 |
| 59392 | 0xE800 | Acknowledgement | 요청·명령에 대한 ACK/NACK/Access Denied 응답 (Part 3) | 8 | 이벤트 |
| 60416 | 0xEC00 | TP.CM (Transport Protocol - Connection Management) | 멀티패킷(9~1,785바이트) 전송 연결 관리 — RTS, CTS, EndOfMsgACK, BAM, Abort (Part 3) | 8 | 이벤트 |
| 60160 | 0xEB00 | TP.DT (Transport Protocol - Data Transfer) | 멀티패킷 데이터 전송. VT 오브젝트 풀·DDOP 업로드 등이 이 위에 실린다 (Part 3) | 8 | 이벤트 |
| 51200 | 0xC800 | ETP.CM (Extended Transport Protocol - Connection Management) | 1,785바이트 초과(최대 약 117 MB) 데이터 연결 관리 (Part 3 §5.11) | 8 | 이벤트 |
| 50944 | 0xC700 | ETP.DT (Extended Transport Protocol - Data Transfer) | 대용량 확장 TP 데이터 전송 (Part 3 §5.11) | 8 | 이벤트 |
| 61444 | 0xF004 | EEC1 (Electronic Engine Controller 1) | 엔진 토크 모드, 실제 토크, 엔진 회전수 — J1939 정의 | 8 | 10 ms |
| 61443 | 0xF003 | EEC2 (Electronic Engine Controller 2) | 가속 페달 위치, 엔진 부하 — J1939 정의 | 8 | 50 ms |
| 61442 | 0xF002 | ETC1 (Electronic Transmission Controller 1) | 변속기 출력축/입력축 회전수, 클러치 슬립 — J1939 정의 | 8 | 10 ms |
| 61445 | 0xF005 | ETC2 (Electronic Transmission Controller 2) | 선택/현재 기어, 실제 기어비 — J1939 정의 | 8 | 100 ms |
| 65262 | 0xFEEE | ET1 (Engine Temperature 1) | 엔진 냉각수 온도, 연료 온도 — J1939 정의 | 8 | 1000 ms |
| 65263 | 0xFEEF | EFL/P1 (Engine Fluid Level/Pressure 1) | 엔진 오일 압력, 수위 — J1939 정의 | 8 | 500 ms |
| 65267 | 0xFEF3 | Vehicle Position | 위도, 경도 — J1939 정의. ISOBUS 항법 위치는 NMEA 2000(IEC 61162-3) GNSS 메시지 사용이 규정이다 (Part 7 B.5) | 8 | 5000 ms |
| 65256 | 0xFEE8 | Vehicle Direction/Speed | 나침반 방위, 항법 기반 속도, 피치, 고도 — J1939 정의 | 8 | 100 ms |
| 65096 | 0xFE48 | Wheel-based Speed and Distance | Tractor ECU가 송신하는 휠 기반 속도·거리·주행 방향·key switch 상태 (Part 7 B.3) | 8 | 100 ms |
| 65097 | 0xFE49 | Ground-based Speed and Distance | 레이더 등 대지 기준 실제 속도·거리·주행 방향 (Part 7 B.2) | 8 | 100 ms |
| 61474 | 0xF022 | Machine Selected Speed | 트랙터가 wheel/ground/navigation 중 선택한 대표 속도·거리·소스 (Part 7 B.28.1) | 8 | 100 ms |
| 65095 | 0xFE47 | Maintain Power | 이그니션 OFF 후 2초 전원 유지 요청 + 임플리먼트 운용 상태 (Part 7 B.4) | 8 | 이벤트 |
| 65094 | 0xFE46 | Secondary or Front Hitch Status | 전방 히치 위치·드래프트 측정값 (Part 7 B.6) | 8 | 100 ms |
| 65093 | 0xFE45 | Primary or Rear Hitch Status | 후방 히치 위치·드래프트 측정값 (Part 7 B.7) | 8 | 100 ms |
| 65092 | 0xFE44 | Secondary or Front PTO Output Shaft | 전방 PTO 회전수·세트포인트·체결 상태 (Part 7 B.8) | 8 | engaged 시 100 ms |
| 65091 | 0xFE43 | Primary or Rear PTO Output Shaft | 후방 PTO 회전수·세트포인트·체결 상태 (Part 7 B.9) | 8 | engaged 시 100 ms |
| 65090 | 0xFE42 | Hitch and PTO Commands | 히치 위치·PTO 속도 세트포인트·PTO 체결 명령 (Part 7 B.10) | 8 | 활성 시 100 ms |
| 65039 | 0xFE0F | Language Command | 언어·단위계·날짜/시간 형식의 전역 통지. 초기화 후 VT가 송신 (Part 7 B.21) | 8 | 초기화 시 + 요청 시 |
| 65037 | 0xFE0D | Working Set Master | working set의 멤버 수 선언. master 자신도 멤버 수에 포함 (Part 7 B.23.2) | 8 | 필요 시 |
| 65036 | 0xFE0C | Working Set Member | working set 개별 멤버의 NAME. master가 멤버 수 − 1개 송신 (Part 7 B.23.3) | 8 | 필요 시 |
| 58880 | 0xE600 | VT to ECU (Virtual Terminal to ECU) | VT가 Working Set으로 보내는 응답·soft key/입력 이벤트·VT Status (Part 6) | 8 | 이벤트 + VT Status 1000 ms |
| 59136 | 0xE700 | ECU to VT (ECU to Virtual Terminal) | Working Set이 VT로 보내는 명령·오브젝트 풀 전송·Working Set Maintenance (Part 6) | 8 | 이벤트 + Maintenance 1000 ms |
| 51968 | 0xCB00 | Process Data (Task Controller) | TC ↔ 클라이언트 전 통신 단일 PGN — DDOP 전송, 값 요청/명령, measurement, TC Status. 첫 니블 command로 구분 (Part 10 Annex B) | 가변 (최소 8) | 이벤트 + TC Status 2000 ms |
| 43520 | 0xAA00 | Client to FS | 클라이언트 → 파일 서버 명령 (Part 13 Annex C) | 가변 | 이벤트 |
| 43776 | 0xAB00 | FS to Client | 파일 서버 → 클라이언트 응답·상태 (Part 13 Annex C) | 가변 | 이벤트 |
| 36352 | 0x8E00 | SCM to SCC | 시퀀스 컨트롤 마스터 → 클라이언트 (Part 14 Annex B) | 가변 (최소 8) | 이벤트 |
| 36096 | 0x8D00 | SCC to SCM | 시퀀스 컨트롤 클라이언트 → 마스터 (Part 14 Annex B) | 가변 (최소 8) | 이벤트 |
| 65226 | 0xFECA | DM1 (Active DTCs) | 현재 활성 고장 코드 목록 (Part 12 B.6) | 가변 | 활성 DTC 있는 동안 1000 ms + 상태 변화 시 |
| 65227 | 0xFECB | DM2 (Previously Active DTCs) | 이전 발생 고장 코드 목록 (Part 12 B.7) | 가변 | 요청 시 |

## SPN (Suspect Parameter Number) 주요 목록

SPN은 PGN 내에서 개별 측정 파라미터를 식별하는 번호다. 트랙터 속도·PTO 파라미터는 ISO 11783-7 Annex A의 SPN을 쓰고, 엔진·변속기·위치 파라미터는 J1939 SPN을 그대로 쓴다.

| SPN | 이름 | 속한 PGN | 바이트 위치 | 길이 (bit) | 해상도 | 오프셋 | 범위 |
|-----|------|----------|-----------|-----------|--------|--------|------|
| 190 | Engine Speed | EEC1 (61444) | 4-5 | 16 | 0.125 rpm/bit | 0 | 0 ~ 8,031.875 rpm |
| 91  | Accelerator Pedal Position 1 | EEC2 (61443) | 2 | 8 | 0.4 %/bit | 0 | 0 ~ 100 % |
| 92  | Engine Percent Load at Current Speed | EEC2 (61443) | 3 | 8 | 1 %/bit | 0 | 0 ~ 250 % |
| 94  | Engine Fuel Delivery Pressure | EFL/P1 (65263) | 1 | 8 | 4 kPa/bit | 0 | 0 ~ 1,000 kPa |
| 100 | Engine Oil Pressure | EFL/P1 (65263) | 4 | 8 | 4 kPa/bit | 0 | 0 ~ 1,000 kPa |
| 110 | Engine Coolant Temperature | ET1 (65262) | 1 | 8 | 1 °C/bit | -40 °C | -40 ~ 210 °C |
| 174 | Engine Fuel Temperature 1 | ET1 (65262) | 2 | 8 | 1 °C/bit | -40 °C | -40 ~ 210 °C |
| 191 | Transmission Output Shaft Speed | ETC1 (61442) | 2-3 | 16 | 0.125 rpm/bit | 0 | 0 ~ 8,031.875 rpm |
| 526 | Transmission Actual Gear Ratio | ETC2 (61445) | 2-3 | 16 | 0.001/bit | 0 | 0 ~ 64.255 |
| 1862 | Wheel-based Machine Speed | Wheel-based Speed and Distance (65096) | 1-2 | 16 | 0.001 m/s/bit | 0 | 0 ~ 64.255 m/s |
| 1864 | Wheel-based Machine Direction | Wheel-based Speed and Distance (65096) | 8 (bit 1-2) | 2 | - | - | 00=Reverse / 01=Forward / 10=Error / 11=N/A |
| 1859 | Ground-based Machine Speed | Ground-based Speed and Distance (65097) | 1-2 | 16 | 0.001 m/s/bit | 0 | 0 ~ 64.255 m/s |
| 1861 | Ground-based Machine Direction | Ground-based Speed and Distance (65097) | 8 (bit 1-2) | 2 | - | - | 00=Reverse / 01=Forward / 10=Error / 11=N/A |
| 1882 | Front PTO Output Shaft Speed | Front PTO Output Shaft (65092) | 1-2 | 16 | 0.125 rpm/bit | 0 | 0 ~ 8,031.875 rpm |
| 1883 | Rear PTO Output Shaft Speed | Rear PTO Output Shaft (65091) | 1-2 | 16 | 0.125 rpm/bit | 0 | 0 ~ 8,031.875 rpm |
| 584 | Latitude | Vehicle Position (65267) | 1-4 | 32 | 10⁻⁷ deg/bit | -210° | -210 ~ +211.1° |
| 585 | Longitude | Vehicle Position (65267) | 5-8 | 32 | 10⁻⁷ deg/bit | -210° | -210 ~ +211.1° |
| 1213 | Malfunction Indicator Lamp Status | DM1 (65226) | 1 (bit 7-8) | 2 | - | - | On / Off |
| 987 | Protect Lamp Status | DM1 (65226) | 1 (bit 1-2) | 2 | - | - | On / Off |

DM1의 램프 상태 비트(SPN 1213, 623, 624, 987)는 SAE J1939-73의 정의다. ISO 11783-12의 DM1은 Byte 1~2를 reserved(0xFF)로 규정하므로, 순수 ISOBUS CF의 DM1에서는 램프 상태가 실리지 않는다.

## PGN 구조 요약

J1939 29비트 CAN ID의 구성:

```
[28:26] Priority (3비트)   - 메시지 우선순위 (0=최고, 7=최저)
[25]    EDP (1비트)        - Extended Data Page
[24]    DP (1비트)         - Data Page, PGN 공간 확장 (0 또는 1)
[23:16] PF (1바이트)       - PDU Format (< 240: PDU1, >= 240: PDU2)
[15:8]  PS (1바이트)       - PDU1: 목적지 주소(DA), PDU2: 그룹 확장(GE)
[7:0]   SA (1바이트)       - 송신 노드 주소
```

- <strong>PDU1 (PF < 0xF0)</strong>: 특정 노드에 전송. PGN에 PS(DA)가 포함되지 않는다(PS 자리는 0으로 계산).
- <strong>PDU2 (PF >= 0xF0)</strong>: 브로드캐스트. PGN = EDP + DP + PF + PS.
