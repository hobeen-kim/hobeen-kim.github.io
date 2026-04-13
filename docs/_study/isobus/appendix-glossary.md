---
title: "용어집 (Glossary)"
description: "ISOBUS/CAN 스터디에서 등장하는 주요 용어를 A-Z 순으로 정리한 참조 자료입니다."
date: 2026-04-13
tags: [ISOBUS, 부록]
---

# 용어집 (Glossary)

---

### A

- **ACK (Acknowledgement)**: CAN 프레임의 ACK 슬롯. 수신 노드가 프레임을 올바르게 수신했을 때 Dominant(0) 비트로 응답한다.
- **AEF (Agricultural Industry Electronics Foundation)**: ISOBUS 인증 및 상호운용성 테스트를 담당하는 농업 전자 산업 재단.
- **Arbitration (중재)**: 여러 노드가 동시에 전송을 시도할 때 CAN ID(우선순위)를 비트 단위로 비교하여 버스를 점유할 노드를 결정하는 과정. ID 값이 작을수록 우선순위가 높다.
- **AUX (Auxiliary Function/Input)**: VT에서 외부 입력 장치(조이스틱 등)를 오브젝트 풀 기능에 매핑하는 보조 기능.

---

### B

- **BAM (Broadcast Announce Message)**: TP(Transport Protocol)에서 멀티패킷 브로드캐스트 전송을 시작할 때 보내는 첫 번째 메시지. 총 바이트 수와 패킷 수를 포함한다.
- **BRS (Bit Rate Switch)**: CAN FD 프레임에서 중재 구간과 데이터 구간의 비트레이트를 전환하는 비트.
- **Bus Off**: CAN 컨트롤러의 TEC가 255를 초과할 때 진입하는 상태. 이 상태에서는 버스에서 완전히 분리되며 수신/송신 모두 불가능하다.

---

### C

- **CAN (Controller Area Network)**: Bosch가 개발한 직렬 통신 버스 프로토콜. 자동차 및 산업 분야에서 광범위하게 사용된다. ISO 11898로 표준화되어 있다.
- **CAN FD (CAN with Flexible Data-Rate)**: 기존 CAN을 확장한 규격. 최대 64바이트 페이로드와 데이터 구간 최대 8 Mbps 비트레이트를 지원한다. ISO 11898-1:2015로 표준화.
- **CF (ContinuationFrame)**: TP 멀티패킷 전송에서 BAM 또는 RTS/CTS 이후 데이터를 나누어 보내는 패킷.
- **CMDT (Connection Mode Data Transfer)**: TP에서 RTS/CTS 핸드셰이크를 사용하는 유니캐스트 멀티패킷 전송 방식.
- **CRC (Cyclic Redundancy Check)**: 데이터 무결성 검증을 위한 오류 검출 코드. CAN 2.0에서는 15비트, CAN FD에서는 17/21비트 CRC를 사용한다.

---

### D

- **DDI (Data Dictionary Identifier)**: Task Controller에서 측정값이나 설정값의 종류를 식별하는 번호. ISO 11783-11에 정의되어 있다.
- **DDOP (Device Descriptor Object Pool)**: 작업 컨트롤러가 장치의 기능과 측정 항목을 파악하기 위해 사용하는 기계의 자기 설명 데이터 구조.
- **DLC (Data Length Code)**: CAN 프레임의 데이터 필드 길이를 나타내는 4비트 필드. 0~8 바이트를 표현한다.
- **DM1 (Diagnostic Message 1)**: J1939에서 현재 활성화된 DTC(Diagnostic Trouble Code) 목록을 전송하는 PGN.
- **DM2 (Diagnostic Message 2)**: 이전에 발생했던(비활성) DTC 목록을 전송하는 PGN.
- **DM3 (Diagnostic Message 3)**: 비활성 DTC를 지우는 요청 메시지.
- **Dominant**: CAN 버스의 논리 0 상태. CAN_H와 CAN_L 사이의 전압 차가 약 2V 이상인 상태. 버스 충돌 시 Dominant가 Recessive를 이긴다.
- **DTC (Diagnostic Trouble Code)**: 결함 진단 코드. SPN + FMI 조합으로 구성된다.

---

### E

- **ECU (Electronic Control Unit)**: 전자 제어 장치. 버스 네트워크에 연결되는 개별 제어 노드.
- **EOF (End of Frame)**: CAN 프레임의 마지막 필드. 7개의 Recessive 비트로 구성되어 프레임 종료를 알린다.
- **ESI (Error Status Indicator)**: CAN FD 프레임에 포함된 1비트 필드. 송신 노드의 에러 상태(Error Active/Passive)를 나타낸다.
- **ETP (Extended Transport Protocol)**: J1939/ISOBUS에서 1,785바이트를 초과하는 대용량 데이터 전송에 사용하는 확장 TP 프로토콜.

---

### F

- **FMI (Failure Mode Indicator)**: DTC의 일부로, 결함의 유형(예: 전압 범위 초과, 단락, 단선 등)을 나타내는 5비트 코드.
- **FMIS (Farm Management Information System)**: 농장 관리 정보 시스템. ISO 11783-10에서 정의된 외부 소프트웨어 인터페이스로, TC와 연계하여 작업 데이터를 관리한다.

---

### G

- **GPS (Global Positioning System)**: 위성 기반 위치 측위 시스템. ISOBUS에서는 기계 위치 정보를 PGN을 통해 버스에 공유한다.

---

### I

- **IDE (Identifier Extension bit)**: CAN 프레임이 11비트 표준 ID(0)인지 29비트 확장 ID(1)인지를 구분하는 비트.
- **ISOBUS**: ISO 11783 표준에 기반한 농업 기계용 통신 버스. J1939를 기반으로 농업 특화 레이어를 추가한 프로토콜.

---

### J

- **J1939**: SAE에서 정의한 상용차 및 농업 기계용 CAN 기반 상위 레이어 프로토콜. ISOBUS의 기반 표준.

---

### N

- **NAME**: J1939/ISOBUS에서 각 ECU를 고유하게 식별하는 64비트 값. 기능, 산업군, 제조사 코드 등을 포함한다.
- **NMEA (National Marine Electronics Association)**: NMEA 2000은 J1939를 기반으로 한 선박용 통신 표준. ISOBUS와 동일한 물리 계층을 공유한다.

---

### P

- **PF (PDU Format)**: PGN 구조에서 PDU 형식을 결정하는 8비트 필드. 0~239이면 PDU1(특정 주소 지정), 240~255이면 PDU2(브로드캐스트).
- **PGN (Parameter Group Number)**: J1939/ISOBUS에서 메시지 종류를 식별하는 18비트 번호. CAN 29비트 ID에서 추출된다.
- **PS (PDU Specific)**: PGN 구조의 필드. PDU1에서는 목적지 주소(DA), PDU2에서는 그룹 확장(GE)로 사용된다.
- **PDU (Protocol Data Unit)**: J1939에서 하나의 CAN 프레임 단위. 헤더(우선순위, PGN, SA)와 최대 8바이트 데이터로 구성.

---

### R

- **Recessive**: CAN 버스의 논리 1 상태. CAN_H와 CAN_L의 전압이 같거나 차이가 미미한 상태. Dominant에 의해 덮어쓰인다.
- **RTR (Remote Transmission Request)**: 다른 노드에게 특정 데이터를 요청하는 CAN 프레임 비트. CAN FD에서는 사용되지 않는다.

---

### S

- **SA (Source Address)**: CAN 29비트 ID의 하위 8비트. 메시지를 전송한 노드의 주소(0~253).
- **Section Control**: ISOBUS TC 기반으로 작업기의 섹션별 ON/OFF를 자동 제어하는 기능. GPS와 연계하여 중복 살포를 방지한다.
- **SOF (Start of Frame)**: CAN 프레임의 시작을 알리는 1비트 Dominant 신호.
- **SPN (Suspect Parameter Number)**: J1939에서 측정 파라미터를 식별하는 번호. PGN 안에서 바이트 위치, 길이, 해상도, 오프셋 정보와 함께 정의된다.
- **Stub**: ISOBUS 버스에서 백본에서 분기하는 짧은 배선 구간. ISO 11783에서 최대 1m로 제한된다.

---

### T

- **TC (Task Controller)**: 농업 작업 데이터(처방, 실적)를 관리하는 ISOBUS 컨트롤러. ISO 11783-10에 정의. FMIS와 연계한다.
- **TEC (Transmit Error Counter)**: CAN 컨트롤러의 송신 에러 카운터. 특정 임계값에 따라 Error Active/Passive/Bus Off 상태가 결정된다.
- **TECU (Tractor ECU)**: 트랙터의 기본 정보(차속, PTO 상태 등)를 버스에 제공하는 ECU. ISO 11783-7에 정의.
- **TP (Transport Protocol)**: 8바이트를 초과하는 데이터를 여러 CAN 프레임으로 나누어 전송하는 J1939/ISOBUS 프로토콜. BAM 및 CMDT 방식을 포함한다.

---

### V

- **VT (Virtual Terminal)**: 농업 기계 작업자에게 UI를 제공하는 ISOBUS 디스플레이 장치. ISO 11783-6에 정의. 작업기의 오브젝트 풀을 표시하고 입력을 처리한다.

---

### W

- **Working Set**: ISOBUS에서 VT에 연결되는 ECU 그룹. Working Set Master와 하나 이상의 Working Set Member로 구성된다.
