---
title: "용어집 (Glossary)"
description: "ISOBUS/CAN 스터디에서 등장하는 주요 용어를 A-Z 순으로 정리한 참조 자료입니다."
date: 2026-04-13
tags: [ISOBUS, 부록]
---

# 용어집 (Glossary)

### A

- **ACK (Acknowledgement)**: CAN 프레임의 ACK 슬롯. 수신 노드가 프레임을 올바르게 수신했을 때 Dominant(0) 비트로 응답한다.
- **Address Claim (주소 클레임)**: CF가 자신의 NAME과 함께 사용할 SA를 네트워크에 선언하고, 충돌 시 NAME 값 비교로 주소를 중재하는 ISO 11783-5의 네트워크 관리 절차. 주소를 클레임하지 못한 CF는 SA를 NULL(254)로 하여 cannot-claim 메시지를 보낸다.
- **AEF (Agricultural Industry Electronics Foundation)**: ISOBUS 인증 및 상호운용성 테스트를 담당하는 농업 전자 산업 재단.
- **Arbitration (중재)**: 여러 노드가 동시에 전송을 시도할 때 CAN ID(우선순위)를 비트 단위로 비교하여 버스를 점유할 노드를 결정하는 과정. ID 값이 작을수록 우선순위가 높다.
- **AUX (Auxiliary Function/Input)**: VT에서 외부 입력 장치(조이스틱 등)를 오브젝트 풀 기능에 매핑하는 보조 기능.

### B

- **BAM (Broadcast Announce Message)**: TP(Transport Protocol)에서 멀티패킷 브로드캐스트 전송을 시작할 때 보내는 첫 번째 메시지. 총 바이트 수와 패킷 수를 포함한다.
- **BRS (Bit Rate Switch)**: CAN FD 프레임에서 중재 구간과 데이터 구간의 비트레이트를 전환하는 비트.
- **Bus Off**: CAN 컨트롤러의 TEC가 255를 초과할 때 진입하는 상태. 이 상태에서는 버스에서 완전히 분리되며 수신/송신 모두 불가능하다.

### C

- **CAN (Controller Area Network)**: Bosch가 개발한 직렬 통신 버스 프로토콜. 자동차 및 산업 분야에서 광범위하게 사용된다. ISO 11898로 표준화되어 있다.
- **CAN FD (CAN with Flexible Data-Rate)**: 기존 CAN을 확장한 규격. 최대 64바이트 페이로드와 데이터 구간 최대 8 Mbps 비트레이트를 지원한다. ISO 11898-1:2015로 표준화.
- **CF (Control Function)**: 장치 내에서 특정 기능을 수행하는 기능 단위. ISO 11783 네트워크에서 유일한 주소(SA) 하나와 NAME을 가지며, 하나의 ECU가 여러 CF를 담을 수 있다. TP 멀티패킷 전송의 데이터 프레임은 CF가 아니라 TP.DT다.
- **CMDT (Connection Mode Data Transfer)**: TP에서 RTS/CTS 핸드셰이크를 사용하는 유니캐스트 멀티패킷 전송 방식.
- **CRC (Cyclic Redundancy Check)**: 데이터 무결성 검증을 위한 오류 검출 코드. CAN 2.0에서는 15비트, CAN FD에서는 17/21비트 CRC를 사용한다.

### D

- **DA (Destination Address)**: 목적지 지정(destination-specific) 메시지에서 수신 대상 CF의 주소를 나타내는 8비트 필드. PDU1 형식의 PS 필드에 들어가며, 255(Global)는 모든 CF를 대상으로 하는 브로드캐스트 목적지다.
- **DDI (Data Dictionary Identifier)**: Task Controller에서 측정값이나 설정값의 종류(DDE)를 식별하는 16비트 번호. ISO 11783-11에 정의되어 있다.
- **DDOP (Device Descriptor Object Pool)**: 작업 컨트롤러가 장치의 기능과 측정 항목을 파악하기 위해 사용하는 기계의 자기 설명 데이터 구조.
- **DL (Data Logger)**: TC의 process data 프로토콜을 사용해 데이터 로깅을 수행하는 CF. ISO 11783-10에 정의되며, TC와 별도로 브로드캐스트 PG까지 수집할 수 있다.
- **DLC (Data Length Code)**: CAN 프레임의 데이터 필드 길이를 나타내는 4비트 필드. 0~8 바이트를 표현한다.
- **DM1 (Diagnostic Message 1)**: J1939에서 현재 활성화된 DTC(Diagnostic Trouble Code) 목록을 전송하는 PGN.
- **DM2 (Diagnostic Message 2)**: 이전에 발생했던(비활성) DTC 목록을 전송하는 PGN.
- **DM3 (Diagnostic Message 3)**: 비활성 DTC를 지우는 요청 메시지.
- **Dominant**: CAN 버스의 논리 0 상태. CAN_H와 CAN_L 사이의 전압 차가 약 2V 이상인 상태. 버스 충돌 시 Dominant가 Recessive를 이긴다.
- **DTC (Diagnostic Trouble Code)**: 결함 진단 코드. SPN + FMI 조합으로 구성된다.

### E

- **ECU (Electronic Control Unit)**: 물리적으로 독립된 하나의 전자 제어 장치. ISO 11783에서 하나의 ECU는 여러 CF(Control Function)를 담을 수 있다.
- **EOF (End of Frame)**: CAN 프레임의 마지막 필드. 7개의 Recessive 비트로 구성되어 프레임 종료를 알린다.
- **ESI (Error Status Indicator)**: CAN FD 프레임에 포함된 1비트 필드. 송신 노드의 에러 상태(Error Active/Passive)를 나타낸다.
- **ETP (Extended Transport Protocol)**: 1,785바이트를 초과하는 대용량 데이터(최대 117,440,505바이트) 전송에 사용하는 확장 전송 프로토콜. ISO 11783-3에 정의되며, SAE J1939와 조화되지 않은 ISOBUS 고유 기능이다.

### F

- **File Server (FS)**: 파일 저장소를 제공하고 파일 취급·접근 명령 집합을 제공하는 implement bus 상의 CF. ISO 11783-13에 정의되며, 네트워크상의 클라이언트가 파일 기반 저장 장치에 데이터를 읽고 쓸 수 있게 한다.
- **FMI (Failure Mode Indicator)**: DTC의 일부로, 결함의 유형(예: 전압 범위 초과, 단락, 단선 등)을 나타내는 5비트 코드.
- **FMIS (Farm Management Information System)**: 농장 관리 정보 시스템. 장부·자원·필지 관리, GIS, 의사결정 지원, 작업(task) 관리 소프트웨어를 포함하는 농장 사무용 컴퓨터 시스템으로, ISO 11783-10의 데이터 교환 형식을 통해 TC와 작업 데이터를 주고받는다.

### G

- **GPS (Global Positioning System)**: 위성 기반 위치 측위 시스템. ISOBUS에서는 기계 위치 정보를 PGN을 통해 버스에 공유한다.

### I

- **IDE (Identifier Extension bit)**: CAN 프레임이 11비트 표준 ID(0)인지 29비트 확장 ID(1)인지를 구분하는 비트.
- **Implement bus (작업기 버스)**: 트랙터의 TECU와 작업기·VT·TC 등의 CF들이 연결되는 ISO 11783 네트워크 세그먼트. breakaway connector를 통해 트랙터 외부의 작업기로 연장된다.
- **ISOBUS**: ISO 11783 표준에 기반한 농업 기계용 통신 버스. J1939를 기반으로 농업 특화 레이어를 추가한 프로토콜.

### J

- **J1939**: SAE에서 정의한 상용차 및 농업 기계용 CAN 기반 상위 레이어 프로토콜. ISOBUS의 기반 표준.

### N

- **NAME**: J1939/ISOBUS에서 각 CF(Control Function)를 고유하게 식별하는 64비트 값. 기능, 산업군, 제조사 코드 등을 포함하며, 주소 클레임 충돌 시 중재 값으로 사용된다. 한 ECU가 여러 CF를 가지면 CF마다 NAME을 가진다.
- **NIU (Network Interconnection Unit)**: 네트워크 또는 네트워크 세그먼트를 상호 연결하는 ECU. ISO 11783-4에 정의되며 repeater, bridge, router, gateway, tractor ECU 유형이 있다.
- **NMEA (National Marine Electronics Association)**: NMEA 2000은 J1939를 기반으로 한 선박용 통신 표준. ISOBUS와 동일한 물리 계층을 공유한다.

### O

- **Object Pool**: 하나의 Working Set의 운전자 인터페이스를 완전히 정의하는 오브젝트 집합. Working Set Master가 VT에 업로드해 두고 표시를 요청하며, ISO 11783-6에 정의된다.

### P

- **PDU (Protocol Data Unit)**: J1939에서 하나의 CAN 프레임 단위. 헤더(우선순위, PGN, SA)와 최대 8바이트 데이터로 구성.
- **PF (PDU Format)**: PGN 구조에서 PDU 형식을 결정하는 8비트 필드. 0~239이면 PDU1(특정 주소 지정), 240~255이면 PDU2(브로드캐스트).
- **PGN (Parameter Group Number)**: J1939/ISOBUS에서 메시지 종류(Parameter Group)를 식별하는 번호. CAN 29비트 ID의 EDP·DP·PF·PS 필드에서 추출되어 3바이트(24비트)로 표현된다.
- **Process Data**: CF들이 주고받는 측정 데이터 및 설정값(set point) 명령. TC와 작업기 클라이언트 간의 작업 데이터 교환에 쓰이며, 메시지 구조는 ISO 11783-10, 데이터 정의(DDI)는 ISO 11783-11에 규정된다.
- **PS (PDU Specific)**: PGN 구조의 필드. PDU1에서는 목적지 주소(DA), PDU2에서는 그룹 확장(GE)로 사용된다.

### R

- **Recessive**: CAN 버스의 논리 1 상태. CAN_H와 CAN_L의 전압이 같거나 차이가 미미한 상태. Dominant에 의해 덮어쓰인다.
- **RTR (Remote Transmission Request)**: 다른 노드에게 특정 데이터를 요청하는 CAN 프레임 비트. CAN FD에서는 사용되지 않는다.

### S

- **SA (Source Address)**: CAN 29비트 ID의 하위 8비트. 메시지를 발신한 CF의 주소이며 유효 범위는 0~253이다. 254는 NULL 주소로 아직 주소를 클레임하지 못한 CF가 소스 주소로만 사용하고, 255(Global)는 목적지 주소로만 사용한다.
- **Section Control**: ISOBUS TC 기반으로 작업기의 섹션별 ON/OFF를 자동 제어하는 기능. GPS와 연계하여 중복 살포를 방지한다.
- **Sequence Control**: 운전자의 반복 조작 시퀀스(PTO 정지, 히치 상승 등)를 기록해 두었다가 명령 한 번으로 재생하는 기능. ISO 11783-14에 정의되며 SCM(master)과 SCC(client)로 구성된다. headland management가 대표 사례다.
- **SOF (Start of Frame)**: CAN 프레임의 시작을 알리는 1비트 Dominant 신호.
- **SPN (Suspect Parameter Number)**: J1939에서 측정 파라미터를 식별하는 번호. PGN 안에서 바이트 위치, 길이, 해상도, 오프셋 정보와 함께 정의된다.
- **Stub**: ISOBUS 버스에서 백본에서 분기하는 짧은 배선 구간. ISO 11783에서 최대 1m로 제한된다.

### T

- **TC (Task Controller)**: 농업 작업 데이터(처방, 실적)를 관리하는 ISOBUS 컨트롤러. process data의 송수신·기록을 담당하는 CF로, ISO 11783-10에 정의. FMIS와 연계한다.
- **TC-BAS / TC-GEO / TC-SC**: ISO 11783-10 Task Controller의 세부 능력(functionality) 구분. TC-BAS는 지리 참조가 필요 없는 기본 능력(합계 기록 등), TC-GEO는 지리 참조 기반 능력(위치별 처방 등), TC-SC는 구간 제어(section control) 능력이다.
- **TEC (Transmit Error Counter)**: CAN 컨트롤러의 송신 에러 카운터. 특정 임계값에 따라 Error Active/Passive/Bus Off 상태가 결정된다.
- **TECU (Tractor ECU)**: 트랙터 내부 버스(tractor bus)와 작업기 버스(implement bus) 사이의 게이트웨이 역할을 하며, 트랙터의 기본 정보(차속, PTO 상태 등)를 implement bus에 제공하는 CF. ISO 11783-9에 정의.
- **TP (Transport Protocol)**: 8바이트를 초과하는 데이터(최대 1,785바이트)를 여러 CAN 프레임으로 나누어 전송하는 J1939/ISOBUS 프로토콜. BAM 및 CMDT 방식을 포함한다.
- **TP.DT (Transport Protocol Data Transfer)**: TP 멀티패킷 전송에서 BAM 또는 RTS/CTS 이후 실제 데이터를 나누어 나르는 데이터 프레임. 첫 바이트가 시퀀스 번호, 나머지 7바이트가 데이터다.

### V

- **VT (Virtual Terminal)**: 농업 기계 작업자에게 UI를 제공하는 ISOBUS 디스플레이 장치. ISO 11783-6에 정의. 작업기의 오브젝트 풀을 표시하고 입력을 처리한다.

### W

- **Working Set**: 하나의 애플리케이션을 분산 프로세스로 제공하는 CF(Control Function)들의 집합. 구성원 중 하나가 Working Set Master로 지정되어 통신을 조정하며, master 자신도 멤버에 포함되므로 master 하나만으로도(멤버 수 1) 구성할 수 있다.
