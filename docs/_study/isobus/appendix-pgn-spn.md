---
title: "PGN/SPN 주요 목록"
description: "ISOBUS와 J1939에서 자주 쓰는 PGN과 SPN을 기능별 표로 정리한 참조 자료다."
date: 2026-04-13
tags: [ISOBUS, 부록]
prev: /study/isobus/appendix-glossary
next: /study/isobus/appendix-ddi
---

# PGN/SPN 주요 목록

::: tip 처음 읽는다면
이 부록은 PGN(메시지 종류 번호)과 SPN(메시지 안의 값 하나하나에 붙은 번호)을 찾아보는 사전이다. 처음부터 읽는 글이 아니라, 본문이나 CAN 로그에서 모르는 PGN 번호를 만났을 때 펼쳐 본다. PGN과 SPN이 처음이라면 [9장 J1939 메시지 구조: 29비트 ID, PGN, SPN](/study/isobus/09-j1939-message)을 먼저 읽는다.
:::

## PGN (Parameter Group Number) 주요 목록

PGN은 J1939 29비트 CAN ID에서 추출되는 18비트 값으로, 메시지의 종류를 식별한다. ISO 11783이 직접 정의하는 PGN은 근거 Part를, ISO 11783 원문에 정의가 없는 SAE J1939 PGN은 "J1939-71 소관"을 표기했다.

| PGN (Dec) | PGN (Hex) | 이름 | 용도 | 데이터 바이트 | 전송 주기 |
|-----------|-----------|------|------|-------------|----------|
| 60928 | 0xEE00 | Address Claimed | 노드 주소 클레임/충돌 해결. SA=254면 Cannot Claim (Part 5) | 8 | 이벤트 (파워온·요청 시) |
| 65240 | 0xFED8 | Commanded Address | 특정 NAME의 CF에 새 SA 지정. 9바이트이므로 BAM으로 전송 (Part 5) | 9 | 이벤트 |
| 59904 | 0xEA00 | Request PGN | 특정 PGN 데이터 요청 (Part 3) | 3 | 이벤트 |
| 59392 | 0xE800 | Acknowledgement | 요청·명령에 대한 ACK/NACK/Access Denied 응답 (Part 3) | 8 | 이벤트 |
| 60416 | 0xEC00 | TP.CM (Transport Protocol - Connection Management) | 멀티패킷(9~1,785바이트) 전송 연결 관리: RTS, CTS, EndOfMsgACK, BAM, Abort (Part 3) | 8 | 이벤트 |
| 60160 | 0xEB00 | TP.DT (Transport Protocol - Data Transfer) | 멀티패킷 데이터 전송. VT 오브젝트 풀·DDOP 업로드 등이 이 위에 실린다 (Part 3) | 8 | 이벤트 |
| 51200 | 0xC800 | ETP.CM (Extended Transport Protocol - Connection Management) | 1,785바이트 초과(최대 약 117 MB) 데이터 연결 관리 (Part 3 §5.11) | 8 | 이벤트 |
| 50944 | 0xC700 | ETP.DT (Extended Transport Protocol - Data Transfer) | 대용량 확장 TP 데이터 전송 (Part 3 §5.11) | 8 | 이벤트 |
| 61444 | 0xF004 | EEC1 (Electronic Engine Controller 1) | 엔진 토크 모드, 실제 토크, 엔진 회전수. J1939-71 소관 | 8 | 10 ms |
| 61443 | 0xF003 | EEC2 (Electronic Engine Controller 2) | 가속 페달 위치, 엔진 부하. J1939-71 소관 | 8 | 50 ms |
| 61442 | 0xF002 | ETC1 (Electronic Transmission Controller 1) | 변속기 출력축/입력축 회전수, 클러치 슬립. J1939-71 소관 | 8 | 10 ms |
| 61445 | 0xF005 | ETC2 (Electronic Transmission Controller 2) | 선택/현재 기어, 실제 기어비. J1939-71 소관 | 8 | 100 ms |
| 65262 | 0xFEEE | ET1 (Engine Temperature 1) | 엔진 냉각수 온도, 연료 온도. J1939-71 소관 | 8 | 1000 ms |
| 65263 | 0xFEEF | EFL/P1 (Engine Fluid Level/Pressure 1) | 엔진 오일 압력, 수위. J1939-71 소관 | 8 | 500 ms |
| 65267 | 0xFEF3 | Vehicle Position | 위도, 경도. J1939-71 소관. ISOBUS 항법 위치는 NMEA 2000(IEC 61162-3) GNSS 메시지 사용이 규정이다 (Part 7 B.5) | 8 | 5000 ms |
| 65256 | 0xFEE8 | Vehicle Direction/Speed | 나침반 방위, 항법 기반 속도, 피치, 고도. J1939-71 소관 | 8 | 100 ms |
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
| 58880 | 0xE600 | VT to ECU (Virtual Terminal to ECU) | VT가 Working Set으로 보내는 응답·soft key/입력 이벤트·VT Status (Part 6) | 가변 (최소 8) | 이벤트 + VT Status 1000 ms |
| 59136 | 0xE700 | ECU to VT (ECU to Virtual Terminal) | Working Set이 VT로 보내는 명령·오브젝트 풀 전송·Working Set Maintenance (Part 6) | 가변 (최소 8) | 이벤트 + Maintenance 1000 ms |
| 51968 | 0xCB00 | Process Data (Task Controller) | TC ↔ 클라이언트 사이의 모든 통신에 쓰는 단일 PGN: DDOP 전송, 값 요청/명령, measurement, TC Status. 첫 니블 command로 구분 (Part 10 Annex B) | 가변 (최소 8) | 이벤트 + TC Status 2000 ms |
| 43520 | 0xAA00 | Client to FS | 클라이언트 → 파일 서버 명령 (Part 13 Annex C) | 가변 | 이벤트 |
| 43776 | 0xAB00 | FS to Client | 파일 서버 → 클라이언트 응답·상태 (Part 13 Annex C) | 가변 | 이벤트 |
| 36352 | 0x8E00 | SCM to SCC | 시퀀스 컨트롤 마스터 → 클라이언트 (Part 14 Annex B) | 가변 (최소 8) | 이벤트 |
| 36096 | 0x8D00 | SCC to SCM | 시퀀스 컨트롤 클라이언트 → 마스터 (Part 14 Annex B) | 가변 (최소 8) | 이벤트 |
| 65226 | 0xFECA | DM1 (Active DTCs) | 현재 활성 고장 코드 목록 (Part 12 B.6) | 가변 | 활성 DTC 있는 동안 1000 ms + 상태 변화 시 |
| 65227 | 0xFECB | DM2 (Previously Active DTCs) | 이전 발생 고장 코드 목록 (Part 12 B.7) | 가변 | 요청 시 |

J1939-71 소관 PGN의 전송 주기는 ISO 11783 원문에 없는 값이라 이 스터디에서 원문으로 검증하지 않았다(SAE J1939-71 확인 필요).

## 기능별 PGN 전체 목록

본문 장과 ISO 11783 표준 정리 부록에 나오는 PGN을 기능별로 모았다. 값·이름·정의 절은 ISO 11783 원문에서 확인했다(Part 3:2018, Part 4:2011, Part 5:2019, Part 6:2018, Part 7:2015와 Amd1:2018, Part 10:2015, Part 12:2019, Part 13:2011, Part 14:2013). 방향/주기 열에는 원문이 적은 내용만 옮겼고, 원문에 없으면 `-`로 두었다. "정의 파트·절" 열은 원문을 가진 독자가 찾아볼 수 있게 남긴 출처 표시라서, 표를 이해하는 데는 필요 없다.

### 네트워크 관리 (Part 5)

| PGN(10진) | PGN(16진) | 이름 | 정의 파트·절 | 방향/주기 | 다루는 장 |
|---|---|---|---|---|---|
| 60928 | 0xEE00 | Address claimed / Cannot claim source address | Part 5 4.4.2.3·4.4.2.4 | 필요 시. cannot-claim은 응답으로만 보낸다(SA 254) | [13장](/study/isobus/13-j1939-address-claim)·[26장](/study/isobus/26-isobus-network-mgmt) |
| 65240 | 0xFED8 | Commanded address | Part 5 4.4.2.5 | 필요 시. 9바이트라 전역(255) BAM으로 보낸다 | [13장](/study/isobus/13-j1939-address-claim) |
| 37632 | 0x9300 | NAME management (NM) | Part 5 4.4.3.2 | 필요 시. PS는 모드에 따라 대상 CF·명령 CF의 SA 또는 전역 | [14장](/study/isobus/14-name-management-init) |

### NIU (Part 4)

| PGN(10진) | PGN(16진) | 이름 | 정의 파트·절 | 방향/주기 | 다루는 장 |
|---|---|---|---|---|---|
| 60672 | 0xED00 | Network message | Part 4 6.5.1 | CF ↔ NIU, 필요 시. Byte 1의 function code로 기능을 가른다 | [21장](/study/isobus/21-niu-network-layer) |

### 요청·확인응답·전송 프로토콜 (Part 3)

| PGN(10진) | PGN(16진) | 이름 | 정의 파트·절 | 방향/주기 | 다루는 장 |
|---|---|---|---|---|---|
| 59904 | 0xEA00 | Request | Part 3 5.4.3 | 필요 시. 초당 2~3회 이하 권장 | [10장](/study/isobus/10-j1939-request-ack)·[13장](/study/isobus/13-j1939-address-claim) |
| 51456 | 0xC900 | Request2 | Part 3 5.4.7 | 필요 시. 초당 2~3회 이하 권장 | [11장](/study/isobus/11-j1939-request2-timing) |
| 51712 | 0xCA00 | Transfer | Part 3 5.4.8 | Use Transfer PGN = 01인 Request2에 대한 응답 | [11장](/study/isobus/11-j1939-request2-timing) |
| 59392 | 0xE800 | Acknowledgement | Part 3 5.4.5 | 이 형식의 응답을 요구하는 PGN을 받았을 때 | [10장](/study/isobus/10-j1939-request-ack) |
| 60416 | 0xEC00 | TP.CM (RTS·CTS·EndOfMsgACK·Abort·BAM) | Part 3 5.10.4 | 전송하는 PGN을 따른다. 우선순위 7 | [15장](/study/isobus/15-tp-bam-cmdt)·[16장](/study/isobus/16-tp-connection-rules) |
| 60160 | 0xEB00 | TP.DT | Part 3 5.10.5 | 전송하는 PGN을 따른다. 우선순위 7 | [15장](/study/isobus/15-tp-bam-cmdt)·[16장](/study/isobus/16-tp-connection-rules) |
| 51200 | 0xC800 | ETP.CM (RTS·CTS·DPO·EOMA·Abort) | Part 3 5.11.5 | 전송하는 PGN을 따른다. 우선순위 7 | [17장](/study/isobus/17-etp) |
| 50944 | 0xC700 | ETP.DT | Part 3 5.11.6 | 전송하는 PGN을 따른다. 우선순위 7 | [17장](/study/isobus/17-etp) |
| 61184 | 0xEF00 | Proprietary A | Part 3 5.4.6.2 | 사용자 요구에 따른다. PDU1(PS = DA) | [8장](/study/isobus/08-j1939-intro)·[10장](/study/isobus/10-j1939-request-ack) |
| 126720 | 0x1EF00 | Proprietary A2 | Part 3 5.4.6.3 | 사용자 요구에 따른다. 데이터 페이지 1의 PDU1 | [8장](/study/isobus/08-j1939-intro)·[10장](/study/isobus/10-j1939-request-ack) |
| 65280~65535 | 0xFF00~0xFFFF | Proprietary B | Part 3 5.4.6.4 | 사용자 요구에 따른다. PDU2(PS는 제조사가 정한다) | [8장](/study/isobus/08-j1939-intro)·[10장](/study/isobus/10-j1939-request-ack) |

### 진단 (Part 12, Part 7 B.27)

| PGN(10진) | PGN(16진) | 이름 | 정의 파트·절 | 방향/주기 | 다루는 장 |
|---|---|---|---|---|---|
| 65226 | 0xFECA | DM1 Active diagnostic trouble codes | Part 12 B.6 | DTC가 활성이 될 때와 그 뒤 1 s마다, 상태 변화 시, 요청 시 | [27장](/study/isobus/27-diagnostics-identification)·[28장](/study/isobus/28-diagnostics-dm-fmi) |
| 65227 | 0xFECB | DM2 Previously active diagnostic trouble codes | Part 12 B.7 | 요청 시에만 | [27장](/study/isobus/27-diagnostics-identification)·[28장](/study/isobus/28-diagnostics-dm-fmi) |
| 65228 | 0xFECC | DM3 Diagnostic data clear/reset previously active DTCs | Part 12 B.8 | 데이터 없음. 이 PGN을 Request로 요청하면 DM2 정보를 지운다 | [27장](/study/isobus/27-diagnostics-identification)·[28장](/study/isobus/28-diagnostics-dm-fmi) |
| 64965 | 0xFDC5 | ECU identification information | Part 12 B.1 | 요청 시 | [27장](/study/isobus/27-diagnostics-identification) |
| 65242 | 0xFEDA | Software identification | Part 12 B.2 | 요청 시 | [11장](/study/isobus/11-j1939-request2-timing)·[27장](/study/isobus/27-diagnostics-identification) |
| 64818 | 0xFD32 | Diagnostic protocol | Part 12 B.5 | 요청 시 | [27장](/study/isobus/27-diagnostics-identification) |
| 64654 | 0xFC8E | Control function functionalities | Part 12 B.9 | 요청 시 | [28장](/study/isobus/28-diagnostics-dm-fmi) |
| 64653 | 0xFC8D | Product identification | Part 12 B.10 | 요청 시 | [27장](/study/isobus/27-diagnostics-identification) |
| 64834 | 0xFD42 | ISOBUS compliance certification | Part 7 B.27 (Part 12 B.3이 참조) | 요청 시 | [27장](/study/isobus/27-diagnostics-identification) |

### VT (Part 6)

| PGN(10진) | PGN(16진) | 이름 | 정의 파트·절 | 방향/주기 | 다루는 장 |
|---|---|---|---|---|---|
| 58880 | 0xE600 | VT to ECU | Part 6 C.1 | VT → Working Set, 필요 시. 우선순위 5(VT v5 이하 문서는 7) | [29장](/study/isobus/29-vt-basics)·[36장](/study/isobus/36-vt-commands-basics) |
| 59136 | 0xE700 | ECU to VT | Part 6 C.1 | Working Set Master → VT, 필요 시. 우선순위 5 | [29장](/study/isobus/29-vt-basics)·[36장](/study/isobus/36-vt-commands-basics) |

### TC (Part 10)

| PGN(10진) | PGN(16진) | 이름 | 정의 파트·절 | 방향/주기 | 다루는 장 |
|---|---|---|---|---|---|
| 51968 | 0xCB00 | Process Data | Part 10 B.2 | TC·DL ↔ 클라이언트. 우선순위는 command 3·A·E·F가 3, D가 4, 0·1·2·4~9가 5(버전 4부터). TC Status는 2 s마다와 변화 시(간격 200 ms 이상) | [43장](/study/isobus/43-tc-connection)·[45장](/study/isobus/45-tc-process-data-basics)·[46장](/study/isobus/46-tc-commands-pdack)·[48장](/study/isobus/48-ddop-basics) |

### FS (Part 13)

| PGN(10진) | PGN(16진) | 이름 | 정의 파트·절 | 방향/주기 | 다루는 장 |
|---|---|---|---|---|---|
| 43520 | 0xAA00 | Client to File Server | Part 13 C.1.1 | 클라이언트 → FS, 필요 시. 우선순위 7 | [51장](/study/isobus/51-file-server-basics) |
| 43776 | 0xAB00 | File Server to Client | Part 13 C.1.1 | FS → 클라이언트, 필요 시. 우선순위 7. File Server Status는 2 s(busy면 200 ms) | [51장](/study/isobus/51-file-server-basics) |

### SC (Part 14)

| PGN(10진) | PGN(16진) | 이름 | 정의 파트·절 | 방향/주기 | 다루는 장 |
|---|---|---|---|---|---|
| 36352 | 0x8E00 | SCM to SCC | Part 14 B.2 | SCM → SCC, 필요 시. 우선순위 4 | [53장](/study/isobus/53-sequence-control-basics)·[54장](/study/isobus/54-sequence-control-details) |
| 36096 | 0x8D00 | SCC to SCM | Part 14 B.3 | SCC → SCM, 필요 시. 우선순위 4 | [53장](/study/isobus/53-sequence-control-basics)·[54장](/study/isobus/54-sequence-control-details) |

### 트랙터-작업기 메시지 (Part 7)

기본 우선순위와 메시지별 송신 주체 정리는 [25장](/study/isobus/25-settings-safety-messages)의 Part 7 메시지 요약 표에, 바이트 배치는 [ISO 11783-7 정리](/study/isobus/appendix-iso-part07)에 있다. 이 표의 방향은 원문 설명이 송신 주체를 밝힌 경우만 적었다.

| PGN(10진) | PGN(16진) | 이름 | 정의 파트·절 | 방향/주기 | 다루는 장 |
|---|---|---|---|---|---|
| 65254 | 0xFEE6 | Time/Date | Part 7 B.1 | 요청 시 | [23장](/study/isobus/23-implement-messages-basics) |
| 65097 | 0xFE49 | Ground-based speed and distance | Part 7 B.2 | 보통 TECU → 작업기 버스, 100 ms | [18장](/study/isobus/18-isobus-overview)·[23장](/study/isobus/23-implement-messages-basics)·[41장](/study/isobus/41-tc-basics) |
| 65096 | 0xFE48 | Wheel-based speed and distance | Part 7 B.3 | TECU → 작업기 버스, 100 ms | [5장](/study/isobus/05-can-arbitration)·[23장](/study/isobus/23-implement-messages-basics)·[41장](/study/isobus/41-tc-basics) |
| 65095 | 0xFE47 | Maintain power | Part 7 B.4 | 작업기 버스의 CF → TECU. 키 OFF를 알리는 메시지를 받은 뒤 필요 시, 파라미터 변화 시 | [22장](/study/isobus/22-tractor-ecu)·[31장](/study/isobus/31-vt-connection)·[43장](/study/isobus/43-tc-connection) |
| 65094 | 0xFE46 | Secondary or front hitch status | Part 7 B.6 | 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 65093 | 0xFE45 | Primary or rear hitch status | Part 7 B.7 | 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 65092 | 0xFE44 | Secondary or front PTO output shaft | Part 7 B.8 | 체결 시 100 ms, 그 외 요청 시 | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 65091 | 0xFE43 | Primary or rear PTO output shaft | Part 7 B.9 | 체결 시 100 ms, 그 외 요청 시 | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 65090 | 0xFE42 | Hitch and PTO commands | Part 7 B.10 | 활성 시 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 65040~65055 | 0xFE10~0xFE1F | Auxiliary valve 0~15 estimated flow | Part 7 B.11·B.14·B.15 | 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 65056~65071 | 0xFE20~0xFE2F | Auxiliary valve 0~15 measured flow | Part 7 B.12·B.14·B.16 | 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 65072~65087 | 0xFE30~0xFE3F | Auxiliary valve 0~15 command | Part 7 B.13·B.14·B.17 | 활성 시 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 65089 | 0xFE41 | Lighting command | Part 7 B.18 | 트랙터 → 모든 조명 컨트롤러(전역). 램프 상태 변화 시, 최대 1 s 간격, 전체 초당 10회 이하 | [22장](/study/isobus/22-tractor-ecu) |
| 65088 | 0xFE40 | Lighting data | Part 7 B.19 | 조명 컨트롤러 → TECU, 요청 시 | [22장](/study/isobus/22-tractor-ecu) |
| 53248 | 0xD000 | Background lighting level command | Part 7 B.20 | 배경 조명 레벨 변화 시, 최대 5 s 간격 | [22장](/study/isobus/22-tractor-ecu) |
| 65039 | 0xFE0F | Language command | Part 7 B.21 | VT → 전체(전원 투입·주소 클레임 뒤), 요청 시 | [25장](/study/isobus/25-settings-safety-messages)·[30장](/study/isobus/30-vt-display-technical-data)·[42장](/study/isobus/42-tc-task)·[49장](/study/isobus/49-ddop-bytes) |
| 52224 | 0xCC00 | Request for repetition rate | Part 7 B.22.1 | 메시지 사용자 → 송신자, 요청 시 | [25장](/study/isobus/25-settings-safety-messages) |
| 65038 | 0xFE0E | Response for repetition rate | Part 7 B.22.2 | 전역 응답, 요청 시 | [25장](/study/isobus/25-settings-safety-messages) |
| 65037 | 0xFE0D | Working Set Master | Part 7 B.23.2 | Working Set Master → 전체, 필요 시 | [20장](/study/isobus/20-isobus-network-topology)·[26장](/study/isobus/26-isobus-network-mgmt)·[31장](/study/isobus/31-vt-connection)·[43장](/study/isobus/43-tc-connection) |
| 65036 | 0xFE0C | Working Set Member | Part 7 B.23.3 | Working Set Master → 전체, 필요 시. 멤버 메시지 간격 100 ms(B.23.4) | [20장](/study/isobus/20-isobus-network-topology)·[26장](/study/isobus/26-isobus-network-mgmt)·[31장](/study/isobus/31-vt-connection)·[43장](/study/isobus/43-tc-connection) |
| 65035 | 0xFE0B | Tractor control mode command (폐기) | Part 7 B.24.1 | TC·작업기 → TECU, 기본 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 65034 | 0xFE0A | Tractor control command tractor response (폐기) | Part 7 B.24.2 | 명령마다 | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 65033 | 0xFE09 | Tractor facility response | Part 7 B.24.3 | TECU → 작업기 CF·TC, 전원 인가 시와 요청 시 | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 65032 | 0xFE08 | Required tractor facilities | Part 7 B.24.4 | 작업기 CF·TC → TECU, 요청 시 | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 50688 | 0xC600 | General-purpose valve estimated flow | Part 7 B.25.2 | 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 50432 | 0xC500 | General-purpose valve measured flow | Part 7 B.25.3 | 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 50176 | 0xC400 | General-purpose valve command | Part 7 B.25.4 | 활성 시 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 1792 | 0x0700 | General-purpose valve load sense pressure | Part 7 B.25.5 | 활성 시 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 44288 | 0xAD00 | Guidance system command | Part 7 B.26.1 | 가이던스 시스템 → 조향 시스템(TECU), 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 44032 | 0xAC00 | Guidance machine status | Part 7 B.26.2 | 조향 시스템 → 가이던스 시스템, 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 61474 | 0xF022 | Machine selected speed | Part 7 B.28.1 | 100 ms | [23장](/study/isobus/23-implement-messages-basics) |
| 64835 | 0xFD43 | Machine selected speed command | Part 7 B.28.2 | 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 64771 | 0xFD03 | Implement operating state command | Part 7 B.29 | TECU → 작업기 버스, 1 s와 상태 변화 시 | [25장](/study/isobus/25-settings-safety-messages) |
| 64770 | 0xFD02 | All implements stop operations switch state | Part 7 B.30 | 작업기 버스의 어느 CF든 보낼 수 있다. 1 s와 상태 변화 시 | [25장](/study/isobus/25-settings-safety-messages) |
| 64717 | 0xFCCD | Drive strategy status | Part 7 B.31 | 트랙터 → 작업기, 500 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 64718 | 0xFCCE | Drive strategy command | Part 7 B.32 | → 트랙터, 500 ms와 데이터 변화 시(100 ms보다 빠르면 안 된다) | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 61668 | 0xF0E4 | Heartbeat | Part 7 B.33.2 | 요청받은 CF가 100 ms마다 | [25장](/study/isobus/25-settings-safety-messages) |
| 61695 | 0xF0FF | Secondary or front hitch roll and pitch | Part 7 Amd1 B.6.2 | 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 64527 | 0xFC0F | Secondary or front hitch roll and pitch sensitivity | Part 7 Amd1 B.6.3 | 변화 시 100 ms, 변화 없으면 1 s | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 61696 | 0xF100 | Secondary or front hitch roll and pitch command | Part 7 Amd1 B.6.4 | 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 64387 | 0xFB83 | Secondary or front hitch yaw | Part 7 Amd1 B.6.5 | 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 61758 | 0xF13E | Secondary or front hitch yaw command | Part 7 Amd1 B.6.6 | 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 61697 | 0xF101 | Primary or rear hitch roll and pitch | Part 7 Amd1 B.7.2 | 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 64526 | 0xFC0E | Primary or rear hitch roll and pitch sensitivity | Part 7 Amd1 B.7.3 | 변화 시 100 ms, 변화 없으면 1 s | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 61698 | 0xF102 | Primary or rear hitch roll and pitch command | Part 7 Amd1 B.7.4 | 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 64386 | 0xFB82 | Primary or rear hitch yaw | Part 7 Amd1 B.7.5 | 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 61759 | 0xF13F | Primary or rear hitch yaw command | Part 7 Amd1 B.7.6 | 100 ms | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 64388 | 0xFB84 | Operator status | Part 7 Amd1 B.33.3.6 | 1 s와 상태 변화 시(200 ms보다 빠르면 안 된다) | [25장](/study/isobus/25-settings-safety-messages) |

### J1939-71·NMEA 2000 소관 PGN

ISO 11783 원문에 정의가 없고 본문 예제나 위치 정보에 쓰이는 PGN이다. ISO 11783-7(트랙터-작업기 메시지를 정하는 표준 문서)은 항법 위치 메시지로 IEC 61162-3(NMEA 2000)을 쓰게 하고, 최소 권장 메시지로 GNSS position data, Position delta high precision rapid update, COG & SOG rapid update, GNSS pseudo-range noise statistics를 든다. 여러 프레임이 필요한 NMEA 2000 메시지는 ISO 11783-3의 TP 대신 NMEA fast packet으로 보낸다.

| PGN(10진) | PGN(16진) | 이름 | 정의 파트·절 | 방향/주기 | 다루는 장 |
|---|---|---|---|---|---|
| 61444 | 0xF004 | EEC1 (Electronic engine controller 1) | J1939-71 소관 | - | [4장](/study/isobus/04-can-data-frame)·[5장](/study/isobus/05-can-arbitration)·[9장](/study/isobus/09-j1939-message)·[55장](/study/isobus/55-practice-log-vt-tc) |
| 61443 | 0xF003 | EEC2 (Electronic engine controller 2) | J1939-71 소관 | - | [55장](/study/isobus/55-practice-log-vt-tc) |
| 61442 | 0xF002 | ETC1 (Electronic transmission controller 1) | J1939-71 소관 | - | - |
| 61445 | 0xF005 | ETC2 (Electronic transmission controller 2) | J1939-71 소관 | - | - |
| 65262 | 0xFEEE | ET1 (Engine temperature 1) | J1939-71 소관 | - | [8장](/study/isobus/08-j1939-intro)·[9장](/study/isobus/09-j1939-message) |
| 65263 | 0xFEEF | EFL/P1 (Engine fluid level/pressure 1) | J1939-71 소관 | - | - |
| 65265 | 0xFEF1 | CCVS (Cruise control/vehicle speed) | J1939-71 소관 | - | [9장](/study/isobus/09-j1939-message) |
| 65251 | 0xFEE3 | Engine configuration | J1939-71 소관. ISO 11783-4의 필터 데이터베이스 조회 예에서, 트랙터 ECU가 작업기 쪽으로 막는 유일한 메시지로 나온다 | - | [21장](/study/isobus/21-niu-network-layer) |
| 65259 | 0xFEEB | Component identification | J1939-71 소관. ISO 11783-3의 연결 모드 TP 전송 예와 요청·응답 예에 쓰인다 | - | [4장](/study/isobus/04-can-data-frame)·[10장](/study/isobus/10-j1939-request-ack)·[15장](/study/isobus/15-tp-bam-cmdt) |
| 65260 | 0xFEEC | Vehicle identification | J1939-71 소관. ISO 11783-3의 BAM 전송 예에 쓰인다(원문은 tractor identification이라 부른다) | - | [16장](/study/isobus/16-tp-connection-rules) |
| 65267 | 0xFEF3 | Vehicle position | J1939-71 소관 | - | - |
| 65256 | 0xFEE8 | Vehicle direction/speed | J1939-71 소관 | - | - |
| 129029 | 0x1F805 | GNSS position data | IEC 61162-3(NMEA 2000) 소관. ISO 11783-7이 사용을 정한다 | - | [41장](/study/isobus/41-tc-basics)·[45장](/study/isobus/45-tc-process-data-basics)·[55장](/study/isobus/55-practice-log-vt-tc) |
| 129026 | 0x1F802 | COG & SOG, rapid update | IEC 61162-3(NMEA 2000) 소관. ISO 11783-7이 사용을 정한다 | - | [41장](/study/isobus/41-tc-basics) |

<small>근거: ISO 11783-7 B.5, ISO 11783-4 6.6.2.3, ISO 11783-3 Annex B·C</small>

## SPN (Suspect Parameter Number) 주요 목록

SPN은 PGN 내에서 개별 측정 파라미터를 식별하는 번호다. 트랙터 속도·PTO 파라미터는 ISO 11783-7이 정한 SPN을 쓰고, 엔진·변속기·위치 파라미터는 J1939 SPN을 그대로 쓴다.

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
