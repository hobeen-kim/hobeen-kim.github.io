---
title: "ISOBUS 스터디"
description: "CAN 통신 기초부터 ISOBUS(ISO 11783)까지, 트랙터와 작업기가 주고받는 통신을 처음부터 차근차근 익히는 57장짜리 스터디다."
date: 2026-04-13
tags: [CAN, J1939, ISOBUS, VT, TC]
---

# ISOBUS 스터디

## 스터디 소개

ISOBUS(ISO 11783)는 트랙터와 작업기(트랙터에 달거나 끌고 다니는 농기계)가 서로 통신하는 방법을 정한 국제 표준이다. 제조사가 달라도 트랙터와 작업기가 함께 동작하도록, CAN(자동차와 농기계에서 널리 쓰는 통신 방식) 위에 SAE J1939(트럭·버스용으로 만든 통신 규칙)과 ISOBUS 규칙을 차례로 쌓아 올린 구조다.

이 스터디에서는 다음을 배운다.

- <strong>CAN 통신의 원리</strong>: 전선 위의 신호부터 프레임, 중재, 에러 처리, CAN FD까지
- <strong>SAE J1939</strong>: CAN 위에서 메시지 종류를 정하고, 장치 주소를 관리하고, 긴 데이터를 나눠 보내는 방법
- <strong>ISOBUS 네트워크</strong>: 버스와 커넥터 구성, 트랙터 ECU(트랙터 쪽 정보를 버스에 내보내는 제어 장치), 트랙터-작업기 메시지, 네트워크 관리와 진단
- <strong>Virtual Terminal(VT)</strong>: 트랙터 화면 하나에 여러 작업기의 조작 화면을 띄우는 방법
- <strong>Task Controller(TC)</strong>: 작업을 기록하고, 위치에 맞춰 살포량과 섹션을 제어하는 방법
- <strong>File Server와 Sequence Control</strong>: 버스 위의 공용 저장소, 반복 조작을 기록했다가 재생하는 기능

### 누구를 위한 글인가

CAN과 통신을 처음 접하는 사람을 위해 썼다. 비개발자도 따라올 수 있게 1장은 "기계끼리 왜 대화해야 하는가"에서 시작하고, 새 용어는 처음 나올 때 쉬운 말로 풀어 쓴다. 1장부터 순서대로 읽으면 앞 장에서 배운 것만으로 다음 장을 이해할 수 있게 짰다.

ISOBUS 장비를 다루는 실무자와 직접 구현하는 개발자도 함께 쓸 수 있게, 메시지의 바이트 배치와 타이밍 같은 세부는 지우지 않고 "(심화)" 절에 남겼다.

::: info 2026-10 개편
- <strong>ISO 원문 대조 보충</strong>: ISO 11783 원문(Part 1, 3~14)과 대조해 메시지 바이트 배치, 타이밍, 상태 머신, 오류 코드 같은 구현 세부와 바이트 단위 예제, 확인 문제를 더했다. 원문과 어긋나던 서술도 함께 바로잡았다.
- <strong>초보자용 재구성</strong>: 22장이던 글을 57장으로 나눴다. 장마다 학습 목표, 먼저 읽을 장, 핵심 정리, 확인 문제를 두고, 구현할 때만 필요한 세부는 "(심화)" 절로 표시했다.
- <strong>용어 사전 팝업</strong>: 본문에서 점선 밑줄이 그어진 용어를 누르면 풀이가 뜬다.
:::

## 읽는 법

모든 장은 같은 틀을 따른다. 처음에 학습 목표와 먼저 읽을 장이 나오고, 끝에 핵심 정리와 확인 문제가 있다. 제목 끝에 "(심화)"가 붙은 절은 직접 구현할 때 필요한 세부다. 처음 읽을 때는 건너뛰어도 흐름을 놓치지 않는다.

### 처음이라면: 입문 경로

아래 장만 순서대로 읽어도 ISOBUS의 큰 그림을 잡을 수 있다. 이 경로에서는 "(심화)" 절을 모두 건너뛴다. 빠진 장은 큰 그림을 잡은 뒤 필요할 때 펼쳐 보면 된다.

| 단계 | 읽을 장 | 얻는 것 |
|---|---|---|
| 1. 통신과 CAN | 1, 2, 3, 4, 5, 6장 | 전선 위의 0과 1이 메시지 한 개가 되는 과정 |
| 2. J1939 | 8, 9, 10, 12, 13, 15장 | 메시지 종류 번호(PGN), 장치 주소, 긴 데이터를 나눠 보내는 법 |
| 3. ISOBUS 큰 그림 | 18, 20, 23, 26장 | ISOBUS의 구성, 트랙터가 알려 주는 기본 정보, Working Set(여러 ECU를 한 장치로 묶는 단위) |
| 4. 주요 기능 | 29, 32, 36장(VT), 41, 45, 48장(TC) | 화면을 띄우는 VT, 작업을 기록하고 제어하는 TC |
| 5. 실습 | 55장 | 로그를 읽고 VT와 TC의 흐름을 따라가기 |

### 실무자라면: 장비를 연결하고 점검하는 사람

CAN 기초를 이미 안다면 J1939의 핵심 장(8, 9, 12, 13, 15장)을 빠르게 훑고 ISOBUS 장으로 넘어간다.

- ISOBUS 네트워크 전체: 18~28장(구성, 트랙터 메시지, Working Set, 진단)
- VT와 TC 연결: 29~31장, 40장(보조 입력), 41~45장
- 실습: 55~57장
- 현장에서 펼쳐 볼 부록: [흔한 실수와 트러블슈팅](/study/isobus/appendix-troubleshooting), [PGN/SPN 주요 목록](/study/isobus/appendix-pgn-spn), [DDI 주요 목록](/study/isobus/appendix-ddi), [AEF 기능 카테고리](/study/isobus/appendix-aef-functionalities)

### 직접 구현한다면: 제어 장치(ECU)나 VT·TC 클라이언트를 만드는 사람

1장부터 57장까지 "(심화)" 절을 포함해 모두 읽는다. 바이트 배치와 타이밍을 집중해서 다루는 장은 다음과 같다.

- J1939: 11, 14, 16, 17장
- ISOBUS 네트워크: 19, 21, 22, 24, 25장
- VT: 30, 31, 33, 34, 35, 37, 38, 39, 40장
- TC: 43, 46, 47, 49, 50장
- File Server와 Sequence Control: 52, 54장
- 파일 형식: 56, 57장

표준 문서의 구조대로 세부를 확인하고 싶으면 이 페이지 아래의 "ISO 11783 표준 정리" 부록을 함께 본다.

## 용어 사전 사용법

본문에서 점선 밑줄이 그어진 용어를 누르면 짧은 풀이가 팝업으로 뜬다. 밑줄은 절마다 그 용어가 처음 나오는 곳에만 그어진다. 팝업은 보조 수단이라, 본문도 용어가 처음 나올 때 풀어 쓴다. 전체 목록은 [용어 사전](/study/isobus/appendix-glossary)에서 볼 수 있다.

## 학습 로드맵

57장을 아홉 묶음으로 나누면 아래 흐름이 된다. 바탕이 되는 통신(CAN, J1939)을 먼저 쌓고, ISOBUS 공통 규칙(네트워크 구성, 트랙터-작업기 메시지, 네트워크 관리)을 익힌 뒤, VT와 TC 같은 기능으로 갈라진다. File Server와 Sequence Control은 VT, TC와 같은 바탕 위에서 동작하는 기능이고, 마지막 실습에서 모두 합쳐 본다.

![ISOBUS 스터디 학습 로드맵: 아홉 묶음의 흐름](/images/study-isobus/00-roadmap-light.png)
![ISOBUS 스터디 학습 로드맵: 아홉 묶음의 흐름](/images/study-isobus/00-roadmap-dark.png)

## 전체 목차

### 통신과 CAN 기초 (1~7장)

| 장 | 제목 | 한 줄 설명 |
|---|---|---|
| 1 | [통신의 기초](/study/isobus/01-communication-basics) | 기계끼리 대화하는 이유와 디지털 신호, 직렬 통신, 버스, 프로토콜의 기본 개념 |
| 2 | [CAN 통신 입문](/study/isobus/02-can-intro) | CAN이 무엇이고 어디에 쓰이는지, 다른 통신 방식과 무엇이 다른지 |
| 3 | [CAN 물리 계층: 전선 위의 0과 1](/study/isobus/03-can-physical) | 두 전선의 전압 차로 0과 1을 보내는 방법, 종단 저항, 통신 속도와 선 길이 |
| 4 | [CAN 데이터 프레임](/study/isobus/04-can-data-frame) | CAN 메시지 한 개(프레임)를 이루는 칸들의 역할과 로그에서 프레임을 읽는 법 |
| 5 | [CAN 중재와 우선순위](/study/isobus/05-can-arbitration) | 여러 장치가 동시에 보낼 때 ID가 작은 메시지가 충돌 없이 먼저 나가는 원리 |
| 6 | [CAN 에러 처리](/study/isobus/06-can-error) | 오류를 찾아내는 다섯 가지 방법, 에러 카운터, 고장 난 장치가 버스에서 빠지는 Bus Off |
| 7 | [CAN FD](/study/isobus/07-can-fd) | 한 번에 더 많이, 더 빠르게 보내는 CAN FD의 구조와 기존 CAN, ISOBUS와의 관계 |

### SAE J1939 (8~17장)

| 장 | 제목 | 한 줄 설명 |
|---|---|---|
| 8 | [SAE J1939 입문](/study/isobus/08-j1939-intro) | CAN 위에 규칙을 더한 J1939의 역할과 29비트 ID에 담긴 정보 |
| 9 | [J1939 메시지 구조: 29비트 ID, PGN, SPN](/study/isobus/09-j1939-message) | ID를 쪼개 메시지 종류(PGN)와 값 번호(SPN)를 읽고 실제 값으로 바꾸는 법 |
| 10 | [요청과 응답: Request, ACK, Group function](/study/isobus/10-j1939-request-ack) | 다른 장치에 데이터를 달라고 요청하고, 받았다는 확인을 돌려주는 메시지 |
| 11 | [Request2, Transfer와 수신·응답 규칙](/study/isobus/11-j1939-request2-timing) | 확장된 요청 메시지와, 응답을 얼마나 빨리 해야 하는지 정한 시간 규칙 |
| 12 | [주소와 NAME: 누가 보냈는지 알아보는 법](/study/isobus/12-j1939-address-name) | 1바이트 주소와 64비트 이름(NAME)으로 장치를 구별하는 방법 |
| 13 | [주소 클레임: 주소를 정하는 절차](/study/isobus/13-j1939-address-claim) | 전원을 켠 장치들이 겹치지 않게 주소를 차지하는 절차와 충돌 해결 |
| 14 | [NAME 관리와 네트워크 초기화](/study/isobus/14-name-management-init) | 실행 중에 NAME을 바꾸는 명령, 주소 위반 처리, 전원을 켤 때의 초기화 순서 |
| 15 | [Transport Protocol 기초: 8바이트보다 긴 데이터 보내기](/study/isobus/15-tp-bam-cmdt) | 긴 데이터를 여러 프레임으로 나눠 보내는 두 방식, 모두에게 알리는 BAM과 1대1 연결인 CMDT |
| 16 | [TP 연결 규칙과 타이머](/study/isobus/16-tp-connection-rules) | TP 연결을 열고, 잠시 멈추고, 닫는 규칙과 타이머, 재전송 |
| 17 | [Extended Transport Protocol: 1,785바이트보다 큰 데이터](/study/isobus/17-etp) | VT 화면 데이터처럼 아주 큰 데이터를 보내는 ETP와 4,000바이트 전송 예 |

### ISOBUS 개요와 네트워크 (18~21장)

| 장 | 제목 | 한 줄 설명 |
|---|---|---|
| 18 | [ISOBUS 개요](/study/isobus/18-isobus-overview) | ISOBUS가 생긴 이유, ISO 11783의 파트 구성, J1939과의 관계, 인증을 맡는 AEF |
| 19 | [ISO 11783 Part 1: 네트워크 요구사항과 공통 서비스](/study/isobus/19-isobus-part1-requirements) | ISO 11783 전체가 따르는 네트워크 요구사항, 공통 서비스, 코드 데이터베이스 |
| 20 | [ISOBUS 네트워크 구성: 버스, 커넥터, ECU](/study/isobus/20-isobus-network-topology) | 트랙터와 작업기를 잇는 버스와 커넥터 구성, 주요 ECU의 역할 |
| 21 | [네트워크 계층과 NIU: 버스와 버스를 잇는 장치](/study/isobus/21-niu-network-layer) | 두 버스를 연결하는 장치(NIU)가 메시지를 넘기거나 걸러 내는 방법 |

### 트랙터와 작업기 메시지 (22~25장)

| 장 | 제목 | 한 줄 설명 |
|---|---|---|
| 22 | [트랙터 ECU: 클래스, 조명, 전원, Safe mode](/study/isobus/22-tractor-ecu) | 트랙터를 대표하는 ECU(TECU)의 등급(클래스), 조명 제어, 키를 껐을 때의 전원 관리, 안전 모드 |
| 23 | [트랙터-작업기 메시지 (1): 읽는 법과 시간·속도·위치](/study/isobus/23-implement-messages-basics) | 트랙터-작업기 메시지를 읽는 공통 규칙과 시간, 속도, 위치 메시지 |
| 24 | [트랙터-작업기 메시지 (2): 히치·PTO·밸브와 작업기의 트랙터 제어](/study/isobus/24-hitch-pto-valve-control) | 히치(작업기 연결 장치), PTO(동력 전달 축), 유압 밸브 메시지와 작업기가 트랙터를 제어하는 절차 |
| 25 | [트랙터-작업기 메시지 (3): 언어 설정, 안전 메시지, Part 7 요약](/study/isobus/25-settings-safety-messages) | 언어와 단위 설정 메시지, 전체 정지와 Heartbeat 같은 안전 메시지, Part 7 메시지 요약 |

### 네트워크 관리와 진단 (26~28장)

| 장 | 제목 | 한 줄 설명 |
|---|---|---|
| 26 | [ISOBUS 네트워크 관리와 Working Set](/study/isobus/26-isobus-network-mgmt) | ISOBUS의 주소 클레임과, 여러 ECU를 한 장치로 묶는 Working Set을 알리는 메시지 |
| 27 | [진단 (1): 진단 개요, ECU 식별, 인증 정보](/study/isobus/27-diagnostics-identification) | 고장 코드의 구조와 ECU의 제조사, 소프트웨어, 인증 정보를 읽는 메시지 |
| 28 | [진단 (2): DM1·DM2·DM3, FMI, Functionalities](/study/isobus/28-diagnostics-dm-fmi) | 현재와 과거 고장을 알리는 DM 메시지, 고장 종류 코드(FMI), 기능 목록 메시지 |

### Virtual Terminal (VT) (29~40장)

| 장 | 제목 | 한 줄 설명 |
|---|---|---|
| 29 | [Virtual Terminal(VT) 기초](/study/isobus/29-vt-basics) | 트랙터 화면 하나로 여러 작업기를 조작하는 VT의 개념, 동작 원리, 버전 |
| 30 | [VT 화면 구성과 기술 데이터](/study/isobus/30-vt-display-technical-data) | VT 화면의 영역과 소프트키 배치, VT가 자기 성능을 알려 주는 기술 데이터 메시지 |
| 31 | [VT 연결 관리: 초기화, 감시, 셧다운](/study/isobus/31-vt-connection) | 작업기가 VT에 연결해 화면을 올리고, 연결을 감시하고, 끝내는 전체 흐름 |
| 32 | [VT 오브젝트 풀 기초](/study/isobus/32-vt-object-pool-basics) | 화면을 이루는 부품(오브젝트)의 종류와 계층, 그 묶음을 VT로 보내는 과정 |
| 33 | [오브젝트 레코드: 공통 구조와 자주 쓰는 오브젝트](/study/isobus/33-vt-object-records) | 오브젝트 하나가 바이트로 어떻게 적히는지, 자주 쓰는 오브젝트의 바이트 배치 |
| 34 | [VT 화면 배치, User-Layout, 색](/study/isobus/34-vt-layout-color) | 좌표, 겹침, 크기 조절 같은 그리기 규칙과 사용자 배치 화면, 색 표현 |
| 35 | [오브젝트 풀 전송 심화와 문자 집합](/study/isobus/35-vt-pool-transfer-charset) | 오브젝트 풀을 나눠 보내고 일부만 고치는 방법, 화면 글자의 문자 집합 |
| 36 | [VT 명령어 기초](/study/isobus/36-vt-commands-basics) | VT와 작업기가 주고받는 명령: 버튼 눌림 알림, 값 바꾸기, 화면 전환 |
| 37 | [VT 명령 세부와 공통 규칙](/study/isobus/37-vt-command-details) | 명령과 응답의 공통 규칙, 오류 코드, 기능별 명령 세부 |
| 38 | [매크로와 운전자 입력 처리](/study/isobus/38-vt-macro-input) | 여러 명령을 묶어 실행하는 매크로와 운전자의 선택, 입력 처리 |
| 39 | [경보, 소리, 활성화 메시지](/study/isobus/39-vt-alarm-activation) | 경보 화면과 경보음, VT가 작업기에 보내는 활성화 메시지 전체 |
| 40 | [보조 입력(AUX): 조이스틱을 기능에 연결하기](/study/isobus/40-vt-aux) | 조이스틱과 버튼을 작업기 기능에 할당하는 AUX의 구조와 할당 절차 |

### Task Controller (TC) (41~50장)

| 장 | 제목 | 한 줄 설명 |
|---|---|---|
| 41 | [Task Controller(TC) 기초](/study/isobus/41-tc-basics) | 작업을 기록하고 제어하는 TC의 역할, 섹션과 살포량 제어, GPS 연동 |
| 42 | [태스크와 시간 기록](/study/isobus/42-tc-task) | TC가 다루는 작업 단위(태스크)의 상태와 시간, 위치 기록 규칙 |
| 43 | [TC 연결 관리와 메시지 바이트](/study/isobus/43-tc-connection) | 작업기가 TC에 연결하는 순서, 셧다운, 연결 메시지의 바이트 |
| 44 | [다중 TC, Data Logger, TC 기능성](/study/isobus/44-tc-multi-dl-functionality) | TC가 여럿일 때 붙을 TC를 고르는 법, 기록 전용 Data Logger, TC 기능 단위 |
| 45 | [TC 프로세스 데이터 기초](/study/isobus/45-tc-process-data-basics) | 값의 뜻을 정하는 번호(DDI), 장치의 부품(Element), 값을 주고받는 메시지 |
| 46 | [프로세스 데이터 명령: 니블, PDACK, 측정 명령](/study/isobus/46-tc-commands-pdack) | 명령 번호 0x0~0xF의 뜻, 확인 응답(PDACK), 값을 언제 보낼지 정하는 측정 명령 |
| 47 | [Totals, 로깅, Peer Control](/study/isobus/47-tc-totals-logging-peer) | 누적값(Totals)과 기본 로깅, 위치 기반 제어, 한 장치가 다른 장치의 목표값을 정하는 Peer Control |
| 48 | [DDOP 기초: 장치가 자기를 소개하는 방법](/study/isobus/48-ddop-basics) | 작업기가 자기 구조와 데이터를 TC에 알리는 DDOP의 구조와 설계 예 |
| 49 | [DDOP 바이트 구성](/study/isobus/49-ddop-bytes) | 7섹션 붐 살포기 예와 DDOP 오브젝트 레코드의 실제 바이트 배치 |
| 50 | [DDOP 전송 명령과 설계 점검](/study/isobus/50-ddop-commands-design) | DDOP를 올리고 활성화하고 지우는 명령, 실행 중 변경 규칙, 설계 점검표 |

### File Server와 Sequence Control (51~54장)

| 장 | 제목 | 한 줄 설명 |
|---|---|---|
| 51 | [File Server(FS) 기초](/study/isobus/51-file-server-basics) | 버스 위의 공용 저장소인 FS의 파일 구조, 접근 흐름, 메시지 형식과 타이밍 |
| 52 | [File Server 세부: 볼륨, 경로, 파라미터, 바이트 따라가기](/study/isobus/52-file-server-details) | 저장 매체(볼륨)와 경로 문법, 플래그와 오류 코드, 디렉터리를 읽는 바이트 예 |
| 53 | [Sequence Control(SC) 기초](/study/isobus/53-sequence-control-basics) | 두렁에서 반복하는 조작을 기록했다가 재생하는 SC의 개념과 상태 머신 |
| 54 | [Sequence Control 세부: SCD 바이트, 메시지, 오류 처리](/study/isobus/54-sequence-control-details) | 기록 데이터(SCD)의 바이트 구조, 재생 메시지, 타임아웃과 오류 처리 |

### 종합 실습 (55~57장)

| 장 | 제목 | 한 줄 설명 |
|---|---|---|
| 55 | [종합 실습 (1): 로그, PGN, VT, TC](/study/isobus/55-practice-log-vt-tc) | CAN 로그를 해석하고 VT 화면과 TC 작업을 시나리오로 따라가는 실습 |
| 56 | [종합 실습 (2): ISOXML 태스크 파일](/study/isobus/56-practice-isoxml) | 농장 관리 컴퓨터와 TC가 주고받는 ISOXML 작업 파일을 읽고 쓰는 실습 |
| 57 | [종합 실습 (3): grid, TimeLog, Point 바이너리](/study/isobus/57-practice-binary-files) | 처방 맵(grid), 작업 기록(TimeLog), 위치 점(Point) 바이너리 파일을 만들고 읽는 실습 |

### 부록

| 부록 | 설명 |
|---|---|
| [용어 사전](/study/isobus/appendix-glossary) | 본문에 나오는 ISOBUS와 CAN 용어의 풀이 전체 목록 |
| [PGN/SPN 주요 목록](/study/isobus/appendix-pgn-spn) | 자주 쓰는 PGN(메시지 종류 번호)과 SPN(값 번호)을 기능별 표로 정리 |
| [DDI 주요 목록](/study/isobus/appendix-ddi) | TC가 주고받는 값의 종류 번호(DDI)를 용도별로 정리 |
| [AEF 기능 카테고리](/study/isobus/appendix-aef-functionalities) | UT, AUX-N, TC-BAS·TC-GEO·TC-SC, TIM, ISB 같은 인증 기능 단위와 그 관계 |
| [흔한 실수와 트러블슈팅](/study/isobus/appendix-troubleshooting) | 통합 과정에서 자주 겪는 문제의 증상, 원인, 해결 방법 |
| [참고 자료](/study/isobus/appendix-references) | 표준 문서, 분석 도구, 오픈소스 스택, 학습 자료 |

### ISO 11783 표준 정리

ISO 11783 표준 원문(Part 1~14, Part 2 제외)을 학습 목적으로 재구성한 비공식 요약·해설 시리즈다. 표준의 절 구조를 그대로 따르므로, 본문 장을 읽은 뒤 세부를 표준의 구조대로 확인하고 싶을 때 펼쳐 본다.

| Part | 제목 | 내용 |
|------|------|------|
| 1 | [General standard](/study/isobus/appendix-iso-part01) | 시리즈 전체 구조, 네트워크 개요, 공통 용어 |
| 3 | [Data link layer](/study/isobus/appendix-iso-part03) | CAN 식별자 구성, PGN 체계, Transport Protocol |
| 4 | [Network layer](/study/isobus/appendix-iso-part04) | NIU 유형, 메시지 포워딩·필터링 |
| 5 | [Network management](/study/isobus/appendix-iso-part05) | 64비트 NAME, 주소 클레임, 상태 천이 |
| 6 | [Virtual terminal](/study/isobus/appendix-iso-part06) | VT 동작 원리, 오브젝트 정의, 명령 메시지, Auxiliary control |
| 7 | [Implement messages](/study/isobus/appendix-iso-part07) | 트랙터-작업기 메시지·파라미터, Amendment 1 |
| 8 | [Power train messages](/study/isobus/appendix-iso-part08) | J1939-71 파워트레인 메시지 적용 규칙 |
| 9 | [Tractor ECU](/study/isobus/appendix-iso-part09) | TECU 게이트웨이 역할, 클래스, 전원 관리 |
| 10 | [Task controller](/study/isobus/appendix-iso-part10) | Process Data, DDOP, ISOXML 스키마 |
| 11 | [Data dictionary](/study/isobus/appendix-iso-part11) | DDI 체계, 온라인 사전 운영 |
| 12 | [Diagnostics services](/study/isobus/appendix-iso-part12) | ECU 식별, DM 메시지, FMI 코드 |
| 13 | [File server](/study/isobus/appendix-iso-part13) | 파일 서버 프로토콜, 명령/응답, 에러 처리 |
| 14 | [Sequence control](/study/isobus/appendix-iso-part14) | SCM/SCC 상태 머신, 오브젝트 풀, 메시지 |
