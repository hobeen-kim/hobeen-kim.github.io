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
- **Address violation (주소 위반)**: 자기 SA를 소스로 쓴, Address Claimed가 아닌 메시지를 받은 상태. 그 CF는 전역으로 Address Claimed를 보내고 SPN 2000+SA·FMI 31인 DTC를 활성화해야 한다(ISO 11783-5 4.4.4.3). ([10장](/study/isobus/10-j1939-address))
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
- **Commanded Address**: 다른 CF(서비스 툴 등)가 특정 NAME의 CF에게 새 SA를 지정하는 메시지(PGN 65240). 9바이트라 전역 BAM으로 보내며, 받아들인 CF는 새 SA로 Address Claimed를 보낸다(ISO 11783-5 4.4.2.5). ([10장](/study/isobus/10-j1939-address))
- **Compliance certification (ISOBUS compliance certification)**: 특정 ECU의 ISOBUS 적합성 인증 상태를 알리는 메시지(PGN 64834). 요청이 올 때 보내며, 정의는 Part 12가 아니라 ISO 11783-7 B.27에 있다. ([14장](/study/isobus/14-isobus-network-mgmt))
- **Control function functionalities**: CF가 지원하는 AEF functionality(UT, AUX-N, TC-GEO 등)를 세대(generation)·옵션과 함께 알리는 진단 메시지(PGN 64654). 요청이 올 때 보낸다(ISO 11783-12 B.9). ([14장](/study/isobus/14-isobus-network-mgmt))
- **CRC (Cyclic Redundancy Check)**: 데이터 무결성 검증을 위한 오류 검출 코드. CAN 2.0에서는 15비트, CAN FD에서는 17/21비트 CRC를 사용한다.

### D

- **DA (Destination Address)**: 목적지 지정(destination-specific) 메시지에서 수신 대상 CF의 주소를 나타내는 8비트 필드. PDU1 형식의 PS 필드에 들어가며, 255(Global)는 모든 CF를 대상으로 하는 브로드캐스트 목적지다.
- **DDI (Data Dictionary Identifier)**: Task Controller에서 측정값이나 설정값의 종류(DDE)를 식별하는 16비트 번호. ISO 11783-11에 정의되어 있다.
- **DDOP (Device Descriptor Object Pool)**: 작업 컨트롤러가 장치의 기능과 측정 항목을 파악하기 위해 사용하는 기계의 자기 설명 데이터 구조.
- **DL (Data Logger)**: TC의 process data 프로토콜을 사용해 데이터 로깅을 수행하는 CF. ISO 11783-10에 정의되며, TC와 별도로 브로드캐스트 PG까지 수집할 수 있다.
- **DLC (Data Length Code)**: CAN 프레임의 데이터 필드 길이를 나타내는 4비트 필드. 0~8 바이트를 표현한다.
- **DM1 (Diagnostic Message 1)**: J1939에서 현재 활성화된 DTC(Diagnostic Trouble Code) 목록을 전송하는 PGN.
- **DM2 (Diagnostic Message 2)**: 이전에 발생했던(비활성) DTC 목록을 전송하는 PGN.
- **DM3 (Diagnostic Message 3)**: 비활성 DTC(DM2) 정보를 지우는 PG. 데이터가 없고, Request로 이 PGN(65228)을 요청하면 지운다(ISO 11783-12 B.8).
- **Dominant**: CAN 버스의 논리 0 상태. CAN_H와 CAN_L 사이의 전압 차가 약 2V 이상인 상태. 버스 충돌 시 Dominant가 Recessive를 이긴다.
- **DPO (Data Packet Offset)**: ETP.CM의 control byte 22 메시지. ETP.DT의 시퀀스 번호가 1바이트뿐이라, 송신 측이 CTS 묶음마다 기준 오프셋을 먼저 알리고 실제 패킷 번호는 시퀀스 번호 + 오프셋으로 센다(ISO 11783-3 5.11.5.5). ([11장](/study/isobus/11-j1939-transport))
- **DTC (Diagnostic Trouble Code)**: 결함 진단 코드. SPN + FMI 조합으로 구성된다. DM1·DM2에서는 SPN(19비트)·FMI(5비트)·CM(1비트)·OC(발생 횟수, 7비트)가 4바이트로 실린다(ISO 11783-12 B.6). ([14장](/study/isobus/14-isobus-network-mgmt))

### E

- **ECU (Electronic Control Unit)**: 물리적으로 독립된 하나의 전자 제어 장치. ISO 11783에서 하나의 ECU는 여러 CF(Control Function)를 담을 수 있다.
- **EOF (End of Frame)**: CAN 프레임의 마지막 필드. 7개의 Recessive 비트로 구성되어 프레임 종료를 알린다.
- **ESI (Error Status Indicator)**: CAN FD 프레임에 포함된 1비트 필드. 송신 노드의 에러 상태(Error Active/Passive)를 나타낸다.
- **ETP (Extended Transport Protocol)**: 1,785바이트를 초과하는 대용량 데이터(최대 117,440,505바이트) 전송에 사용하는 확장 전송 프로토콜. ISO 11783-3에 정의되며, SAE J1939와 조화되지 않은 ISOBUS 고유 기능이다.

### F

- **File Server (FS)**: 파일 저장소를 제공하고 파일 취급·접근 명령 집합을 제공하는 implement bus 상의 CF. ISO 11783-13에 정의되며, 네트워크상의 클라이언트가 파일 기반 저장 장치에 데이터를 읽고 쓸 수 있게 한다.
- **Filter database (필터 데이터베이스)**: NIU가 port pair별로 PGN을 통과·차단하는 규칙표. filter mode 0은 적힌 PGN을 막고(기본 통과), 1은 적힌 PGN만 통과시킨다(기본 차단)(ISO 11783-4 6.6.2). ([13장](/study/isobus/13-isobus-architecture))
- **FMI (Failure Mode Indicator)**: DTC의 일부로, 결함의 유형(예: 전압 범위 초과, 단락, 단선 등)을 나타내는 5비트 코드. 값별 의미는 ISO 11783-12 Annex E가 정한다. ([14장](/study/isobus/14-isobus-network-mgmt))
- **FMIS (Farm Management Information System)**: 농장 관리 정보 시스템. 장부·자원·필지 관리, GIS, 의사결정 지원, 작업(task) 관리 소프트웨어를 포함하는 농장 사무용 컴퓨터 시스템으로, ISO 11783-10의 데이터 교환 형식을 통해 TC와 작업 데이터를 주고받는다.

### G

- **GPS (Global Positioning System)**: 위성 기반 위치 측위 시스템. ISOBUS에서는 기계 위치 정보를 PGN을 통해 버스에 공유한다.
- **Grid type 1 / type 2**: ISOXML 처방 맵을 셀 단위로 담는 grid 바이너리 형식. type 1은 셀마다 처리 구역(TZN) 코드 1바이트, type 2는 템플릿 TZN의 PDV마다 32비트 값을 담는다(ISO 11783-10 8.6.2). ([22장](/study/isobus/22-practice))
- **Group function**: PGN 하나에 여러 기능을 묶는 메시지 형식. 그룹은 PGN으로, 그룹 안의 기능은 보통 데이터 첫 바이트로 가른다. VT·TC·FS·SC 메시지와 TP.CM이 이 방식이다(ISO 11783-3 5.4.6.1). ([09장](/study/isobus/09-j1939-message))

### H

- **Heartbeat**: 안전 관련 통신이 살아 있는지 확인하려고 CF가 보내는 1바이트 시퀀스 번호 메시지(PGN 61668). 기본으로는 보내지 않고, 소비 CF가 Request for repetition rate로 요청하면 100 ms마다 보낸다(ISO 11783-7 B.33). ([13장](/study/isobus/13-isobus-architecture))

### I

- **IDE (Identifier Extension bit)**: CAN 프레임이 11비트 표준 ID(0)인지 29비트 확장 ID(1)인지를 구분하는 비트.
- **Implement bus (작업기 버스)**: 트랙터의 TECU와 작업기·VT·TC 등의 CF들이 연결되는 ISO 11783 네트워크 세그먼트. breakaway connector를 통해 트랙터 외부의 작업기로 연장된다.
- **ISB (All implements stop operations switch)**: 운전자가 연결된 모든 작업기를 한 번에 멈추는 전체 작업기 정지 스위치. 상태는 PGN 64770으로 1 s마다와 바뀔 때 방송하며, 원문은 ISB라는 약어의 풀이를 적지 않는다(ISO 11783-7 B.30). ([13장](/study/isobus/13-isobus-architecture))
- **ISOBUS**: ISO 11783 표준에 기반한 농업 기계용 통신 버스. J1939를 기반으로 농업 특화 레이어를 추가한 프로토콜.

### J

- **J1939**: SAE에서 정의한 상용차 및 농업 기계용 CAN 기반 상위 레이어 프로토콜. ISOBUS의 기반 표준.

### K

- **Key Group**: Key 1~4개를 묶은 VT 오브젝트(Type 35, VT version 4 이상). 운전자가 User-Layout Soft Key Mask에 묶음 단위로 배치한다(ISO 11783-6 B.20, 4.7). ([16장](/study/isobus/16-vt-object-pool))

### N

- **NAME**: J1939/ISOBUS에서 각 CF(Control Function)를 고유하게 식별하는 64비트 값. 기능, 산업군, 제조사 코드 등을 포함하며, 주소 클레임 충돌 시 중재 값으로 사용된다. 한 ECU가 여러 CF를 가지면 CF마다 NAME을 가진다.
- **NAME management (NM)**: 실행 중에 CF의 NAME 필드(주로 instance)를 바꾸는 절차와 메시지(PGN 37632). 명령받은 값은 pending NAME으로 보관했다가 Adopt 명령이 오면 채택하고, 새 NAME으로 주소를 다시 클레임한다(ISO 11783-5 4.4.3). ([10장](/study/isobus/10-j1939-address))
- **Network message**: NIU의 파라미터·filter database·토폴로지·connection을 다루는 메시지(PGN 60672). Byte 1의 function code로 기능을 가른다(ISO 11783-4 6.5). ([13장](/study/isobus/13-isobus-architecture))
- **NIU (Network Interconnection Unit)**: 네트워크 또는 네트워크 세그먼트를 상호 연결하는 ECU. ISO 11783-4에 정의되며 repeater, bridge, router, gateway, tractor ECU 유형이 있다.
- **NMEA (National Marine Electronics Association)**: NMEA 2000은 J1939를 기반으로 한 선박용 통신 표준. ISOBUS와 동일한 물리 계층을 공유한다.

### O

- **Object Pool**: 하나의 Working Set의 운전자 인터페이스를 완전히 정의하는 오브젝트 집합. Working Set Master가 VT에 업로드해 두고 표시를 요청하며, ISO 11783-6에 정의된다.

### P

- **PDACK (Process Data Acknowledge)**: TC·DL이나 클라이언트가 명령·process data를 수락하거나 거부할 때 보내는 Process Data 응답(command D). Element·DDI, 오류 비트 8개, 응답 대상 command를 담는다(ISO 11783-10 B.7). ([19장](/study/isobus/19-tc-process-data))
- **PDU (Protocol Data Unit)**: J1939에서 하나의 CAN 프레임 단위. 헤더(우선순위, PGN, SA)와 최대 8바이트 데이터로 구성.
- **Peer control**: TC가 한 CF를 다른 CF의 setpoint 공급원(source)으로 할당하고 기록하는 기능. Peer Control Assignment(command 9)로 할당하며 TC 버전 4에서 추가됐다(ISO 11783-10 6.8.5, B.4). ([19장](/study/isobus/19-tc-process-data))
- **PF (PDU Format)**: PGN 구조에서 PDU 형식을 결정하는 8비트 필드. 0~239이면 PDU1(특정 주소 지정), 240~255이면 PDU2(브로드캐스트).
- **PGN (Parameter Group Number)**: J1939/ISOBUS에서 메시지 종류(Parameter Group)를 식별하는 번호. CAN 29비트 ID의 EDP·DP·PF·PS 필드에서 추출되어 3바이트(24비트)로 표현된다.
- **Port pair**: NIU의 포트 두 개를 묶어 메시지가 어느 세그먼트에서 어느 세그먼트로 흐르는지 나타낸 값. network message에서는 한 바이트의 상위 니블이 From, 하위 니블이 To 포트다(ISO 11783-4 6.5.3). ([13장](/study/isobus/13-isobus-architecture))
- **Process Data**: CF들이 주고받는 측정 데이터 및 설정값(set point) 명령. TC와 작업기 클라이언트 간의 작업 데이터 교환에 쓰이며, 메시지 구조는 ISO 11783-10, 데이터 정의(DDI)는 ISO 11783-11에 규정된다.
- **Proprietary A / A2 / B**: 데이터 내용을 제조사가 정하는 독점 PG. A(PGN 61184)와 A2(PGN 126720)는 PDU1이라 PS가 DA이고, B(PGN 65280~65535)는 PDU2라 PS를 제조사가 정한다(ISO 11783-3 5.4.6). ([09장](/study/isobus/09-j1939-message))
- **PS (PDU Specific)**: PGN 구조의 필드. PDU1에서는 목적지 주소(DA), PDU2에서는 그룹 확장(GE)로 사용된다.

### R

- **Recessive**: CAN 버스의 논리 1 상태. CAN_H와 CAN_L의 전압이 같거나 차이가 미미한 상태. Dominant에 의해 덮어쓰인다.
- **Request2 / Transfer**: 응답을 Transfer(PGN 51712)로 받도록 지정할 수 있는 확장 요청(PGN 51456)과 그 응답. Transfer는 데이터 세트마다 주인 CF의 신원(NAME 바이트 5~8)을 붙여, 한 CF가 여러 CF의 데이터를 대신 보고할 수 있게 한다(ISO 11783-3 5.4.7·5.4.8). ([09장](/study/isobus/09-j1939-message))
- **RTR (Remote Transmission Request)**: 다른 노드에게 특정 데이터를 요청하는 CAN 프레임 비트. CAN FD에서는 사용되지 않는다.

### S

- **SA (Source Address)**: CAN 29비트 ID의 하위 8비트. 메시지를 발신한 CF의 주소이며 유효 범위는 0~253이다. 254는 NULL 주소로 아직 주소를 클레임하지 못한 CF가 소스 주소로만 사용하고, 255(Global)는 목적지 주소로만 사용한다.
- **SCD (Sequence Control Data)**: SCC가 초기화 때 SCM에 올리는 오브젝트 풀. SCC 식별(basic object) → 기록할 수 있는 기능(function object) → 기능별 상태(state object)의 계층이다(ISO 11783-14 Annex A). ([21장](/study/isobus/21-isobus-misc))
- **SCM / SCC (Sequence Control Master / Client)**: Sequence Control의 두 역할. SCM은 기록·재생을 주관하고, SCC는 PTO·히치·밸브 같은 기능을 가지고 재생 명령을 수동 조작과 같은 방식으로 실행한다. SCM → SCC는 PGN 36352, SCC → SCM은 PGN 36096이다(ISO 11783-14 Annex B). ([21장](/study/isobus/21-isobus-misc))
- **Section Control**: ISOBUS TC 기반으로 작업기의 섹션별 ON/OFF를 자동 제어하는 기능. GPS와 연계하여 중복 살포를 방지한다.
- **Self-configurable address**: NAME의 1비트 필드. 1이면 주소 중재에서 졌을 때 자기 preferred address나 128~247 범위에서 다른 주소를 골라 재클레임할 수 있다. ISO 11783 적합 CF는 self-configurable이어야 한다(ISO 11783-5 4.2). ([10장](/study/isobus/10-j1939-address))
- **Sequence Control**: 운전자의 반복 조작 시퀀스(PTO 정지, 히치 상승 등)를 기록해 두었다가 명령 한 번으로 재생하는 기능. ISO 11783-14에 정의되며 SCM(master)과 SCC(client)로 구성된다. headland management가 대표 사례다.
- **SOF (Start of Frame)**: CAN 프레임의 시작을 알리는 1비트 Dominant 신호.
- **SPN (Suspect Parameter Number)**: J1939에서 측정 파라미터를 식별하는 번호. PGN 안에서 바이트 위치, 길이, 해상도, 오프셋 정보와 함께 정의된다.
- **Structure label · Localization label**: TC 연결 때 DDOP를 식별하는 7바이트 라벨 두 개. Structure label은 제조사가 정하는 DDOP 구조 버전이고, Localization label은 Language command Byte 1~6에 예약 `FF`를 더한 값이다. 클라이언트는 TC에 같은 라벨이 있는지 물어 DDOP를 새로 올릴지 정한다(ISO 11783-10 Table A.1, B.6). ([20장](/study/isobus/20-tc-ddop))
- **Stub**: ISOBUS 버스에서 백본에서 분기하는 짧은 배선 구간. ISO 11783에서 최대 1m로 제한된다.

### T

- **TC (Task Controller)**: 농업 작업 데이터(처방, 실적)를 관리하는 ISOBUS 컨트롤러. process data의 송수신·기록을 담당하는 CF로, ISO 11783-10에 정의. FMIS와 연계한다.
- **TC-BAS / TC-GEO / TC-SC**: ISO 11783-10 Task Controller의 세부 능력(functionality) 구분. TC-BAS는 지리 참조가 필요 없는 기본 능력(합계 기록 등), TC-GEO는 지리 참조 기반 능력(위치별 처방 등), TC-SC는 구간 제어(section control) 능력이다.
- **TEC (Transmit Error Counter)**: CAN 컨트롤러의 송신 에러 카운터. 특정 임계값에 따라 Error Active/Passive/Bus Off 상태가 결정된다.
- **TECU (Tractor ECU)**: 트랙터 내부 버스(tractor bus)와 작업기 버스(implement bus) 사이의 게이트웨이 역할을 하며, 트랙터의 기본 정보(차속, PTO 상태 등)를 implement bus에 제공하는 CF. ISO 11783-9에 정의.
- **TECU class / addendum**: TECU가 작업기 버스에 제공하는 메시지 수준. Class 1~3(3은 히치·PTO·보조 밸브 명령 수용)에 기능별 addendum N(항법)·F(전방 히치·PTO)·G(조향)·P(속도·구동 전략 명령)·M(발진 명령)을 붙인다(예: class 3GP)(ISO 11783-9 4.4.2). ([13장](/study/isobus/13-isobus-architecture))
- **TimeLog (TLG)**: TC가 태스크 중 시간·위치와 process data 값을 기록하는 ISOXML 로그. 레코드 구조를 정하는 XML 헤더(`TLG00001.XML`)와 바이너리 레코드 파일(`TLG00001.BIN`) 한 쌍이다(ISO 11783-10 8.6.3). ([22장](/study/isobus/22-practice))
- **TP (Transport Protocol)**: 8바이트를 초과하는 데이터(최대 1,785바이트)를 여러 CAN 프레임으로 나누어 전송하는 J1939/ISOBUS 프로토콜. BAM 및 CMDT 방식을 포함한다.
- **TP.DT (Transport Protocol Data Transfer)**: TP 멀티패킷 전송에서 BAM 또는 RTS/CTS 이후 실제 데이터를 나누어 나르는 데이터 프레임. 첫 바이트가 시퀀스 번호, 나머지 7바이트가 데이터다.

### U

- **User-Layout Data Mask**: VT가 소유한 특수 Data Mask(VT version 4 이상). 2열 × 6행 Window Cell 격자에 운전자가 여러 Working Set의 Window Mask를 골라 배치한다(ISO 11783-6 4.7.2). ([16장](/study/isobus/16-vt-object-pool))

### V

- **Virtual CF**: NIU가 다른 세그먼트에 있는 실제 CF의 NAME으로 이쪽 세그먼트에 주소를 클레임해 세운 겉보기 CF. NIU connection이 열리면 생기고, NIU가 주소를 바꿔 메시지를 전달한다(ISO 11783-4 6.9). ([13장](/study/isobus/13-isobus-architecture))
- **VT (Virtual Terminal)**: 농업 기계 작업자에게 UI를 제공하는 ISOBUS 디스플레이 장치. ISO 11783-6에 정의. 작업기의 오브젝트 풀을 표시하고 입력을 처리한다.

### W

- **Window Mask**: Working Set이 User-Layout Data Mask에 내놓는 작은 창 오브젝트(Type 34, VT version 4 이상). type 0(free form)은 WS가 자식을 배치하고, type 1~18은 VT가 배치와 모양을 정하는 표준 창이다(ISO 11783-6 4.7, B.19). ([16장](/study/isobus/16-vt-object-pool))
- **Working Set**: 하나의 애플리케이션을 분산 프로세스로 제공하는 CF(Control Function)들의 집합. 구성원 중 하나가 Working Set Master로 지정되어 통신을 조정하며, master 자신도 멤버에 포함되므로 master 하나만으로도(멤버 수 1) 구성할 수 있다.
- **Working Set Special Controls**: 풀을 처음 그리기 전에 쓸 Colour Map·Colour Palette와 언어·국가 코드를 지정하는 VT 오브젝트(Type 47, VT version 6). 풀에 0개 또는 1개 둔다(ISO 11783-6 B.29). ([16장](/study/isobus/16-vt-object-pool))
