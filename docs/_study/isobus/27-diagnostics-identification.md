---
title: "진단 (1): 진단 개요, ECU 식별, 인증 정보"
description: "ISOBUS 진단의 큰 그림(고장 코드와 DM1·DM2·DM3)을 잡고, 진단 화면이 CF마다 모으는 식별 정보와 인증 정보 메시지를 바이트 단위로 읽는다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, Diagnostics, DM1, ECUIdentification]
prev: /study/isobus/26-isobus-network-mgmt
next: /study/isobus/28-diagnostics-dm-fmi
---

# 진단 (1): 진단 개요, ECU 식별, 인증 정보

::: info 학습 목표
- 고장 코드가 SPN(어디가)과 FMI(어떻게)의 조합이라는 것을 설명할 수 있다.
- DM1, DM2, DM3가 각각 무엇을 알리거나 지우는지 구분할 수 있다.
- CF가 반드시 답해야 하는 진단 요청과, 그 응답이 단일 프레임·BAM·RTS/CTS 가운데 무엇으로 나가는지 판단할 수 있다.
- ECU identification 같은 `*` 구분 문자열 메시지와 ISOBUS 인증 정보 메시지를 바이트 단위로 읽고 만들 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [26장 ISOBUS 네트워크 관리와 Working Set](/study/isobus/26-isobus-network-mgmt), [10장 요청과 응답](/study/isobus/10-j1939-request-ack), [15장 Transport Protocol 기초](/study/isobus/15-tp-bam-cmdt)
- 이 장에서 처음 나오는 말
  - DTC(Diagnostic Trouble Code): 고장 하나를 숫자로 나타낸 고장 코드.
  - FMI(Failure Mode Indicator): 고장의 종류(너무 높음, 단선 등)를 가리키는 0~31 번호.
  - DM(Diagnostic Message): 진단 정보를 실어 나르는 메시지. DM1, DM2, DM3처럼 번호가 붙는다.
  - 진단 UI: 운전자나 정비사가 진단 정보를 보는 화면이나 장치.
- 다시 보는 말: [9장](/study/isobus/09-j1939-message)에서 본 SPN은 고장 코드에서 "고장 난 대상(어떤 값, 어떤 부품)"을 가리킨다.
:::

자동차 계기판에 엔진 경고등이 켜지면 운전자는 뭔가 고장 났다는 것만 안다. 정비소에서 진단기를 꽂아야 어느 부품이 어떻게 고장 났는지 알려 주는 고장 코드를 읽을 수 있다. ISOBUS에서는 각 CF가 고장을 숫자 코드로 만들어 버스에 알리고, 트랙터 화면(VT)이나 진단 장비가 그 코드와 함께 ECU의 이름표(부품 번호, 시리얼 번호, 소프트웨어 버전, 인증 정보)를 모아 보여 준다. 이 장은 진단의 큰 그림과 이름표 정보를 다루고, 고장 코드 메시지의 바이트와 송신 규칙은 [28장](/study/isobus/28-diagnostics-dm-fmi)에서 본다.

## 1. 진단 메시지 한눈에 보기

이 절은 ISOBUS 진단이 무엇을 주고받는지 큰 그림을 잡는다.

ISOBUS는 ISO 11783-12(진단 서비스를 정하는 표준 문서, 이하 Part 12)를 통해 표준화된 진단 메시지를 정의한다. SAE J1939-73(J1939의 진단 규격)의 DM 메시지 체계를 가져와 농기계 환경에 맞게 요구사항을 좁힌 구조다.

### 계기판 경고등으로 이해하기

| 자동차 | ISOBUS | 메시지 |
|---|---|---|
| 지금 켜져 있는 경고등 | 지금 활성인 고장 코드 목록 | DM1 |
| 정비 기록부에 남은 지난 고장 | 활성이었다가 해소된 고장 코드 | DM2 |
| 정비사가 지난 기록을 지움 | 이전 고장 기록 초기화 명령 | DM3 |

비유가 어긋나는 곳이 하나 있다. 자동차 고장 코드는 보통 진단기를 꽂아야 읽지만, ISOBUS의 DM1은 고장이 있는 동안 CF가 스스로 1초마다 버스에 방송한다. 버스에 붙은 VT가 따로 묻지 않아도 경고를 띄울 수 있는 까닭이다.

### 고장 코드 구조: SPN + FMI

모든 고장은 <strong>SPN(Suspect Parameter Number)</strong>과 <strong>FMI(Failure Mode Indicator)</strong>의 조합으로 식별한다.

- **SPN**: 어떤 파라미터에 문제가 생겼는지 (예: SPN 100 = 엔진 오일 압력)
- **FMI**: 어떤 종류의 고장인지 (예: FMI 1 = 데이터 낮음, FMI 3 = 전압 높음)

둘을 합치면 한 문장이 된다. "SPN 100 + FMI 1"은 엔진 오일 압력 값을 믿을 수 있는데 그 값이 정상보다 낮다는 뜻이다. 같은 SPN 100이라도 FMI 3이면 오일 압력 신호의 전압이 정상보다 높거나 높은 전원 쪽에 단락됐다는 뜻이다. 압력이 낮은 것이 아니라 신호 선이나 센서가 이상한 것이다.

SPN과 FMI에 고장 발생 횟수(OC, Occurrence Count)를 더해 4바이트로 묶은 것이 DTC(Diagnostic Trouble Code)다. DTC의 바이트 배치는 [28장](/study/isobus/28-diagnostics-dm-fmi)에서 본다.

### 주요 진단 메시지

| 메시지 | PGN | 이름 | 설명 |
|--------|-----|------|------|
| DM1 | 65226 | Active Diagnostic Trouble Codes | 현재 발생 중인 활성 고장 코드 목록. 상태 변화 시 즉시 + 활성 고장이 있는 동안 <strong>1초에 1회(1 Hz)</strong> 주기 전송 |
| DM2 | 65227 | Previously Active Diagnostic Trouble Codes | 이전에 발생했다가 해소된 고장 코드. <strong>요청(request) 시에만</strong> 전송하며 주기 전송은 없다 |
| DM3 | 65228 | Diagnostic Data Clear | 저장된 이전 고장 코드(DM2) 초기화 요청. 활성 고장(DM1) 데이터에는 영향 없음 |

![고장 발생 시 DM1 전송과 VT 화면 경고, 고장 해소 시 DM2로 이동, 정비사 요청 시 DM3 전송과 DM2 기록 삭제로 이어지는 세 갈래 흐름](/images/study-isobus/27-dm-flow-light.png)
![고장 발생 시 DM1 전송과 VT 화면 경고, 고장 해소 시 DM2로 이동, 정비사 요청 시 DM3 전송과 DM2 기록 삭제로 이어지는 세 갈래 흐름](/images/study-isobus/27-dm-flow-dark.png)

- 윗줄: 고장이 생기면 그 CF가 DM1을 보내고, VT가 화면에 경고를 띄운다.
- 가운데 줄: 고장이 풀리면 그 코드는 이전 고장 기록(DM2)으로 옮겨진다.
- 아랫줄: 정비사가 진단 UI에서 DM3를 보내면 DM2 기록이 지워진다. 활성 고장(DM1)은 그대로다.

### FMI 주요 값

FMI는 0~31 가운데 하나다. 처음에는 아래 값만 알아도 고장 로그 대부분을 읽을 수 있다. 전체 목록과 고르는 법은 [28장](/study/isobus/28-diagnostics-dm-fmi)에 있다.

| FMI | 의미 |
|-----|------|
| 0 | 데이터는 유효하나 정상 범위보다 높음 (most severe) |
| 1 | 데이터는 유효하나 정상 범위보다 낮음 (most severe) |
| 2 | 데이터 불안정 / 간헐적 / 부정확 |
| 3 | 전압 높음 / 단락 (High) |
| 4 | 전압 낮음 / 단락 (Low) |
| 5 | 전류 낮음 / 단선 |
| 6 | 전류 높음 / 단락 (GND) |
| 12 | 지능형 장치·컴포넌트 내부 고장 (ECU 교체 필요) |
| 19 | 수신 네트워크 데이터 오류 |

most severe는 "가장 심한 수준"이라는 뜻이다. 현장에서 자주 보는 값을 풀어 쓰면 다음과 같다.

- FMI 0·1: 센서는 멀쩡하고 값도 믿을 수 있는데, 값 자체가 위험할 만큼 높거나 낮다. 실제 상태(압력, 온도)부터 확인한다.
- FMI 2: 값이 현실에서 불가능할 만큼 들쭉날쭉하거나 다른 정보와 맞지 않는다. 센서나 연결 상태를 의심한다.
- FMI 3·4: 신호 전압이 정상 범위를 벗어났다. 배선이 전원(high) 쪽이나 낮은 전위(low) 쪽에 닿은 단락이 전형적이다.
- FMI 5: 전류가 너무 적다. 선이 끊긴 단선이 전형적이다.
- FMI 6: 전류가 너무 많다. 접지(GND) 쪽 단락이 전형적이다.
- FMI 12: ECU 안의 고장이다. 더 작은 부품 단위로 고칠 수 없어 ECU를 바꿔야 한다.
- FMI 19: 네트워크로 받은 값이 처음부터 오류 표시로 와 있다. 고장 위치는 받은 쪽이 아니라 그 값을 보낸 쪽이다.

정리하면, ISOBUS 진단은 "어디가(SPN) 어떻게(FMI)"를 숫자로 알리는 체계이고, DM1·DM2·DM3가 각각 지금 고장, 지난 고장, 기록 지우기를 맡는다.

## 2. 진단 요구사항: CF가 꼭 지원해야 할 것

이 절은 구현자 관점의 두 질문에 답한다. CF는 무엇을 반드시 지원해야 하나? 요청이 오면 무엇을 어떤 방식으로 돌려줘야 하나?

Part 12(2019년 3판)는 본문이 짧고 규정 대부분이 부속서에 있다. 절별 요약은 [Part 12 정리 부록](/study/isobus/appendix-iso-part12)에 있다.

### 필수 메시지

- 1판에 있던 진단 level 0·level 1 구분은 폐기됐다. 옛 판은 진단 기능을 두 단계로 나눠 고르게 했지만 지금은 그런 선택이 없다.
- 모든 CF는 Part 12가 정한 진단 정보 메시지(아래 표의 열 가지) 전부와, 거기서 파생되는 요구사항을 지원해야 한다(shall). DM1·DM2·DM3는 고를 수 있는 선택지가 아니라 셋 다 필수다. Part 12에 나오는 DM은 이 셋뿐이고, DM11·DM22 같은 다른 DM 번호(SAE J1939-73에 있는 번호)는 나오지 않는다.
- 운전자나 정비사가 문제를 진단할 <strong>진단 사용자 인터페이스</strong>(diagnostic user interface, 이하 진단 UI)가 있어야 한다. VT가 맡아도 되고 다른 UI 장치여도 된다. 아래 "진단 UI가 모으는 정보" 표의 정보는 이 UI를 거쳐 사람에게 보여야 한다(shall).

shall은 표준 문장에서 "반드시 해야 한다", should는 "권고", may는 "해도 된다"는 뜻이다.

CF가 받을 수 있는 Request와 응답 방식을 한 표로 모으면 다음과 같다. Request(PGN 59904)는 요청할 PGN을 LSB(낮은 자리 바이트)부터 담은 3 byte 메시지다([10장](/study/isobus/10-j1939-request-ack)). 예를 들어 ECU identification의 PGN 64965는 16진수로 `0x00FDC5`이므로 Request 데이터는 `C5 FD 00`이다.

표의 "응답 방식"에 나오는 BAM과 RTS/CTS는 8바이트보다 긴 데이터를 나눠 보내는 TP(Transport Protocol)의 두 방식이다. BAM은 모두에게 방송하고, RTS/CTS는 한 상대와 연결을 맺어 보낸다. RTS/CTS는 [15장](/study/isobus/15-tp-bam-cmdt)에서 CMDT라고 부른 연결형 전송이다. ACK/NACK은 "처리했다/처리할 수 없다"는 응답이다.

| 메시지 | PGN | Request 데이터 | 길이 | 응답 방식 |
|---|---|---|---|---|
| ECU identification | 64965 (0xFDC5) | `C5 FD 00` | 가변 | 대개 8 byte 초과. 전역 요청이면 BAM, 지정 요청이면 RTS/CTS |
| Software identification | 65242 (0xFEDA) | `DA FE 00` | 가변 | 위와 같다 |
| ISOBUS certification | 64834 (0xFD42) | `42 FD 00` | 8 byte | 단일 프레임, 항상 전역 |
| NAME | 60928 (0xEE00) | `00 EE 00` | 8 byte | Address Claimed 메시지로 답한다. 항상 전역 |
| Diagnostic protocol | 64818 (0xFD32) | `32 FD 00` | 8 byte | 단일 프레임, 항상 전역 |
| DM1 | 65226 (0xFECA) | `CA FE 00` | 가변 | DTC 0~1개면 단일 프레임, 2개 이상이면 BAM 또는 RTS/CTS |
| DM2 | 65227 (0xFECB) | `CB FE 00` | 가변 | DM1과 같다. 지원하지 않으면 NACK |
| DM3 | 65228 (0xFECC) | `CC FE 00` | 없음 | 지정 요청이면 ACK/NACK(PGN 59392), 전역 요청이면 응답 없음 |
| Functionalities | 64654 (0xFC8E) | `8E FC 00` | 8 byte 이상 | 8 byte면 단일 프레임, 넘으면 BAM 또는 RTS/CTS |
| Product identification | 64653 (0xFC8D) | `8D FC 00` | 가변 | ECU identification과 같다 |

주소 클레임을 빼면 위 PGN은 모두 PF가 240 이상인 PDU2다. PDU2는 CAN ID에 받는 쪽 주소 칸이 없는 형식이라 언제나 모두에게 간다([9장](/study/isobus/09-j1939-message)). 그래서 응답이 8 byte 이하면 요청이 지정 주소로 왔어도 전역으로 나간다. 8 byte를 넘으면 요청 방식이 TP 방식을 정한다. 전역 요청이면 BAM, 지정 요청이면 RTS/CTS다. TP 자체는 [15장](/study/isobus/15-tp-bam-cmdt)에서 다뤘다. 주소 클레임(PGN 60928)은 지정 주소로 요청받아도 전역으로 답하는 예외다.

요청과 응답의 일반 규칙도 진단 UI 설계에 바로 걸린다.

- 지정 요청을 받은 CF는 반드시 답한다. 요청받은 PG(파라미터 그룹, 곧 메시지)를 보내거나, 지원하지 않으면 NACK(control byte 1)을 보낸다. 전역 요청에는 NACK을 보내면 안 된다.
- 응답은 200 ms(Tr) 안에 해야 한다(shall). 요청한 쪽은 최소 1.25 s(T3)를 기다린 뒤 다시 요청한다. 재시도는 2회, 즉 총 3회로 제한하라는 것이 권고다(should).
- Request PG의 전송 주기는 "보통 초당 두세 번 이하"가 권고다. CF 수십 개에 메시지 열 종류를 물어야 하는 진단 UI라면, 한꺼번에 쏟기보다 순서를 정해 하나씩 돌리는 편이 이 권고에 맞는다(추론).

### 진단 UI가 모으는 정보

Part 12는 진단 UI가 보여 줄 정보를 두 묶음으로 정한다. 네트워크에 누가 있는지(네트워크 정보)와 각 CF의 고장 상태(CF 정보)다. active DTC는 지금 활성인 고장 코드, previously active DTC는 예전에 활성이었던 고장 코드다.

| 묶음 | 내용 | 얻는 방법 |
|---|---|---|
| 네트워크 정보 | ECU part number·serial number·제조사명 | ECU identification 요청 |
| 네트워크 정보 | 각 CF의 NAME | 주소 클레임 감시 |
| 네트워크 정보 | 소프트웨어 버전 | Software identification 요청 |
| 네트워크 정보 | 적합성 시험 데이터 (시험소, 인증 데이터, 시험 연도) | ISOBUS certification 메시지 요청 (4절) |
| 네트워크 정보 | 제품 식별 | Product identification 요청 |
| CF 정보 | CF의 진단 프로토콜 | Diagnostic protocol 요청 |
| CF 정보 | active / previously active DTC (SPN·FMI) | DM1 수신·요청 / DM2 요청 |
| CF 정보 | 고장 발생 횟수 (있으면) | DTC의 OC 필드 |
| CF 정보 | previously active DTC 클리어 (요구되는 경우) | DM3 |

진단 UI는 주소 클레임 과정을 지켜보며 NAME과 SA를 얻고, 나머지는 CF에 요청해 얻는다. 같은 ECU 안의 CF는 모두 같은 ECU identification을 보내야 하므로, 진단 UI는 이 문자열이 같은 CF끼리 묶어 "ECU 한 대에 CF 몇 개"를 그릴 수 있다. Part 12에 실린 예시 화면(네트워크 정보 화면)이 그렇게 생겼다. 제조사·part number·serial number가 같은 VT·TECU(트랙터 ECU)·두 번째 VT CF 셋이 트랙터 ECU 하나에, Rate Control(살포량 제어) CF 셋이 작업기 ECU 하나에 들어 있다. Product identification도 제품 안에서 같아야 하므로 그 위에 "제품" 단위 묶음을 하나 더 만들 수 있다. 중복 주소 클레임이나 중복 NAME 같은 주소 오류는 진단 툴이 Request for Address Claimed로 찾아낼 수 있다.

### 네트워크 통계

- 네트워크 상태를 보여 주는 진단 UI는 자기 연결로 버스 통계를 직접 재야 한다. 하드웨어가 지원하면 최소한 bus load(버스가 메시지 전송에 쓰인 시간 비율), 송수신 중 검출한 CAN 에러, 네트워크 메시지 수를 보여야 한다(shall).
- 하드웨어가 허락하면 250 ms~5 s 동안의 평균 버스 전압도 넣는 것이 권고다(should).
- Part 12의 예시 화면(네트워크 통계 화면)에는 CAN_H·CAN_L 전압, bus load(%), 메시지 수와 함께 Stuff·Form·Ack·Bit 1·Bit 2·CRC 에러 카운트가 있다. 에러 이름은 [6장](/study/isobus/06-can-error)에서 본 CAN 에러 검출 메커니즘(Bit·Stuff·CRC·Form·ACK)과 같다. 예시 화면은 Bit 에러를 Bit 1·Bit 2 두 칸으로 나눠 보여 주는데, 표준은 둘의 차이를 설명하지 않는다.
- bus load를 어떤 식으로 계산하는지는 Part 12가 정하지 않는다.

### 서비스 툴과 진단 커넥터

진단 화면에서 문제가 특정 ECU의 특정 CF로 좁혀지면, 그 CF가 Diagnostic protocol 메시지로 알린 프로토콜을 쓰는 서비스 툴을 ISO 11783-2(물리 계층을 정하는 표준 문서)의 진단 커넥터에 연결해 표시된 DTC를 바탕으로 문제를 푼다. Part 12의 진단 메시지가 맡는 일은 어느 유닛이 고장 났는지 좁히는 데까지다.

Part 12는 진단 체계가 지원해야 하는 네트워크 구성 예를 그림으로 싣고 있다. 아래는 그 구성 요소와 연결 관계를 옮긴 것이다. 상자의 크기와 자리에는 뜻이 없다.

![제품 1(트랙터 또는 자주식 작업기) 안에 tractor bus와 ISO 11783 bus가 있고, tractor ECU CF와 진단 커넥터가 두 버스에 모두 연결된다. tractor bus에는 ECU 1~n이, ISO 11783 bus에는 CF1·CF2를 가진 OEM 설치 ECU, 제품 2인 애프터마켓 ECU, 작업기 연결 커넥터 너머의 작업기 CF가 붙고, 진단 툴은 툴 인터페이스를 거쳐 진단 커넥터에 연결되는 구성](/images/study-isobus/27-diagnostic-network-light.png)
![제품 1(트랙터 또는 자주식 작업기) 안에 tractor bus와 ISO 11783 bus가 있고, tractor ECU CF와 진단 커넥터가 두 버스에 모두 연결된다. tractor bus에는 ECU 1~n이, ISO 11783 bus에는 CF1·CF2를 가진 OEM 설치 ECU, 제품 2인 애프터마켓 ECU, 작업기 연결 커넥터 너머의 작업기 CF가 붙고, 진단 툴은 툴 인터페이스를 거쳐 진단 커넥터에 연결되는 구성](/images/study-isobus/27-diagnostic-network-dark.png)

- 제품: 한 제조사가 만든 장치 단위다. 트랙터에 달려 나온 ECU는 트랙터라는 제품의 일부이고, 따로 사서 단 애프터마켓 ECU는 그 자체가 제품이다.
- tractor bus는 트랙터 안의 장치끼리 쓰는 버스이고, ISO 11783 bus는 작업기까지 이어지는 ISOBUS다.
- 트랙터(제품 1) 안에 tractor bus와 ISO 11783 bus가 있고, tractor ECU가 두 버스에 함께 연결돼 있다. ISO 11783 bus에는 CF 두 개를 가진 OEM ECU, 별개 제품인 애프터마켓 ECU(제품 2), 커넥터 너머의 작업기 CF가 붙는다.
- 진단 커넥터는 두 버스에 모두 닿는 자리에 있다. 커넥터와 그 설치는 ISO 11783-2를 따른다.

정리하면, 모든 CF는 진단 요청 열 가지에 답해야 하고, 진단 UI는 그 답과 주소 클레임을 모아 "누가 있고, 무엇이 고장 났는지"를 보여 준다. 구체적인 수리는 진단 커넥터에 꽂는 서비스 툴의 몫이다.

<small>근거: ISO 11783-12 6.1~6.6, Annex B, Annex C, Annex D; ISO 11783-3 5.4.3, 5.13.3; ISO 11783-5 4.4.4.1, 4.5.3</small>

## 3. CF 정보 메시지를 바이트로 읽기

진단 UI가 모으는 정보 가운데 ECU identification, Software identification, Product identification은 사람이 읽는 문자열이다. 이 절은 그 문자열이 바이트로 어떻게 실리는지 본다. 칸마다 끝에 `*`를 찍어 이어 붙인 한 줄 메모라고 생각하면 된다. 예를 들어 `이름*주소*전화*`처럼 쓴다.

ECU identification, Software identification, Product identification은 가변 길이 문자열을 `*`로 끊어 싣는다. 형식은 단순하지만 구분자 규칙 하나만 놓쳐도 필드가 한 칸씩 밀린다.

### 문자열 공통 규칙

- 문자 하나가 1 byte이고, 허용 값은 32~126과 160~255다. Part 12는 이 191개를 "ASCII"라고 부른다. ISO/IEC 8859-1(Latin 1, 서유럽 문자를 담은 1바이트 문자 집합)의 그래픽 문자 191개이며, 나머지 65개(0~31, 127~159)는 제어 문자라 쓸 수 없다.
- 필드 값에는 `*`를 쓸 수 없다(구분자). Software identification은 `#`도 금지이고, ECU hardware ID는 `#`를 향후 용도로 예약해 두었다.
- 길이 상한은 ECU part number·serial number·location·type·manufacturer name이 각 200자, ECU hardware ID가 200 byte, software identification 전체가 200자, product identification의 세 필드가 각 50자다.
- 인코딩은 Latin 1 그대로다. 문자열을 UTF-8(요즘 컴퓨터가 흔히 쓰는, 문자 하나를 1~4바이트로 적는 방식)로 내보내면 `ü`가 `C3 BC` 두 바이트가 된다. 두 바이트 모두 160~255 안이라 범위 검사도 통과하지만, 받는 쪽 화면에는 `Ã¼`가 찍힌다.

### ECU identification (PGN 64965)

DP 0·PF 253·PS 197, priority 6, 요청이 올 때만 보낸다. 필드 여섯 개를 아래 순서로 놓고 각 필드 뒤에 `*`를 붙인다. 마지막 필드 뒤에도 붙는다.

| 순서 | 필드 | SPN |
|---|---|---|
| 1 | ECU part number(부품 번호) | SPN 2901 |
| 2 | ECU serial number(일련번호) | SPN 2902 |
| 3 | ECU location: 트랙터·작업기 위의 설치 위치 | SPN 2903 |
| 4 | ECU type: I/O 같은 능력 분류 | SPN 2904 |
| 5 | ECU manufacturer name(제조사명) | SPN 4304 |
| 6 | ECU hardware ID: 하드웨어 버전과 적합성 시험 성적서를 잇는 값 | SPN 6714 |

같은 ECU 안의 CF는 모두 같은 내용을 보내야 한다(shall). 예를 들어 `HC-2210-04*250930117*Right boom*Section I/O*Example Agri*HW 3.1*`(가상의 값)는 64 byte라 TP 패킷 10개로 나간다.

이 예를 바이트로 따라가 보자.

1. 앞부분 `HC-2210-04*`는 문자마다 1 byte라 `48 43 2D 32 32 31 30 2D 30 34 2A`다. `-`는 `0x2D`, `*`는 `0x2A`다.
2. 여섯 필드의 글자 수는 10, 9, 10, 11, 12, 6으로 합이 58이다. `*` 6개를 더하면 64 byte다.
3. 64 byte는 8 byte를 넘으므로 TP로 나간다. TP 패킷 하나는 데이터를 7 byte씩 싣는다. 64 ÷ 7을 올림하면 10개다.
4. 받는 쪽은 `*`마다 잘라 여섯 칸을 얻는다. 다섯 번째 칸 `Example Agri`가 제조사명이다.

### Software identification (PGN 65242)

- DP 0·PF 254·PS 218, priority 6, On request다.
- Byte 1은 software identification 필드 수다(0~250, 운용 범위 0~125). 문자열은 Byte 2부터 온다.
- 필드 사이는 `*`로 나누고, 필드가 하나뿐이어도 마지막에 `*`를 붙여야 한다.
- 한 필드 안의 소프트웨어 모듈(앱, 화면 데이터처럼 따로 버전이 붙는 부분)은 `#`로 나눈다. 마지막 모듈 뒤의 `#`는 붙여도 되고 안 붙여도 되므로 파서는 둘 다 받아야 한다.
- 예: 앱과 오브젝트 풀 버전을 한 필드에, 부트로더(전원을 켤 때 먼저 도는 작은 프로그램)를 다른 필드에 넣으면 `02` + `APP 3.2.1#VTPOOL 1.7*BOOT 1.04*`다.

### Product identification (PGN 64653)

- DP 0·PF 252·PS 141, priority 6, On request다. `code*brand*model*` 순서로 싣는다.
- code는 형식판(type plate, 기계에 붙은 명판)에 적힌 번호다. 차량이면 VIN(차대번호)과 같을 수 있고, VT 같은 단독 시스템이면 ECU 식별 번호와 같을 수 있다. code와 brand의 조합은 전 세계에서 유일해야 하고(shall), model은 brand 안에서 제품을 가린다.
- 같은 제품에 속한 CF는 Request에 모두 같은 값으로 답해야 한다(shall).
- 앞으로 `*` 필드가 늘 수 있다고 Part 12가 예고한다. 파서는 네 번째 이후 필드를 오류로 보지 말고 건너뛴다.

### Diagnostic protocol (PGN 64818)

DP 0·PF 253·PS 50, priority 6, 8 byte, On request다. 각 CF는 이 메시지로 자기가 지원하는 진단 프로토콜을 알려야 한다(shall). 이 메시지를 보고 2절의 서비스 툴을 고른다.

| Byte 1 값 | 뜻 |
|---|---|
| `0x00` | ISO 11783 외의 추가 진단 프로토콜 없음 |
| `0x01` | SAE J1939-73 |
| `0x02` | ISO 14230 (KWP 2000, ISO 15765-3 TP 사용) |
| `0x04` | ISO 14229-3 (UDS on CAN) |
| `0x08`~`0x80` | ISO 할당 예약 |

KWP 2000과 UDS는 자동차 정비에서 널리 쓰는 진단 프로토콜이다.

- 값이 비트 하나씩 배정돼 있으니, 여러 프로토콜을 지원하면 비트를 함께 켠다. J1939-73(`0000 0001`)과 UDS on CAN(`0000 0100`)이면 두 비트를 합친 `0000 0101`, 곧 `0x05`다. 표준에 조합 예는 없다(추론).
- Byte 2~8은 "ISO 할당 예약"이고 채울 값은 Part 12에 적혀 있지 않다. ISO 11783-7의 일반 규칙(따로 적지 않은 예약 비트는 1)을 따르면 `FF`다(추론).
- 이 메시지는 진단 전용이며, CF가 런타임 동작(실제 작업 중의 동작 방식)을 구성하는 데 쓰면 안 된다(shall not).

아래 코드는 네 메시지의 데이터를 만들고, `*`로 잘라 되읽고, UTF-8 실수를 재현한다.

::: details Python으로 문자열 메시지 만들고 되읽기
```python
GRAPHIC = set(range(32, 127)) | set(range(160, 256))      # 6.7: Latin 1 그래픽 문자
assert len(GRAPHIC) == 191 and 256 - len(GRAPHIC) == 65


def field(text, forbidden="*", limit=200):
    raw = text.encode("latin-1")
    assert len(raw) <= limit and set(raw) <= GRAPHIC
    assert not any(ch in text for ch in forbidden)
    return raw


def star_join(fields, limit=200):
    return b"".join(field(f, "*", limit) + b"*" for f in fields)


def star_split(payload):
    parts = payload.decode("latin-1").split("*")
    assert parts[-1] == ""                    # 마지막 필드 뒤에도 '*'가 있어야 한다
    return parts[:-1]


def software_identification(fields):
    body = b"".join(b"#".join(field(m, "*#") for m in modules) + b"*" for modules in fields)
    assert len(body) <= 200
    return bytes([len(fields)]) + body


ecu_id = star_join(["HC-2210-04", "250930117", "Right boom", "Section I/O",
                    "Example Agri", "HW 3.1"])
sw_id = software_identification([["APP 3.2.1", "VTPOOL 1.7"], ["BOOT 1.04"]])
product = star_join(["SPR-0042-K", "Brand B", "Sprayer 24"], limit=50)
diag_protocol = bytes([0b00000101]) + b"\xFF" * 7          # J1939-73 + UDS on CAN

for name, pgn, payload in [("ECU identification", 64965, ecu_id),
                           ("Software identification", 65242, sw_id),
                           ("Product identification", 64653, product),
                           ("Diagnostic protocol", 64818, diag_protocol)]:
    packets = -(-len(payload) // 7) if len(payload) > 8 else 0
    print(f"{name:24} PGN {pgn} (0x{pgn:04X}) {len(payload):3} byte  TP 패킷 {packets}")

assert star_split(ecu_id)[4] == "Example Agri" and len(star_split(ecu_id)) == 6
assert sw_id == b"\x02" + b"APP 3.2.1#VTPOOL 1.7*BOOT 1.04*"
modules = [[m for m in f.split("#") if m] for f in star_split(sw_id[1:])]
assert modules == [["APP 3.2.1", "VTPOOL 1.7"], ["BOOT 1.04"]]
assert star_split(product + b"Extra*")[:3] == ["SPR-0042-K", "Brand B", "Sprayer 24"]

utf8 = "Güllefass".encode("utf-8")                          # ü -> C3 BC
assert set(utf8) <= GRAPHIC                                 # 범위 검사로는 못 잡는다
assert utf8.decode("latin-1") == "GÃ¼llefass"               # 받는 쪽 화면
assert "Güllefass".encode("latin-1") == b"G\xfcllefass"     # 올바른 1 byte 인코딩

# ECU identification       PGN 64965 (0xFDC5)  64 byte  TP 패킷 10
# Software identification  PGN 65242 (0xFEDA)  32 byte  TP 패킷 5
# Product identification   PGN 64653 (0xFC8D)  30 byte  TP 패킷 5
# Diagnostic protocol      PGN 64818 (0xFD32)   8 byte  TP 패킷 0
```

출력의 "TP 패킷"은 데이터가 8 byte를 넘을 때 7 byte씩 나눈 개수다. Diagnostic protocol은 8 byte라 TP 없이 단일 프레임으로 나간다. 마지막 네 줄은 `ü`를 UTF-8로 보내면 범위 검사를 통과하면서도 화면이 깨지고, Latin 1로 보내야 1 byte(`0xFC`)가 된다는 것을 보여 준다.
:::

정리하면, 식별 메시지는 Latin 1 문자열을 `*`로 끊어 싣는 단순한 형식이다. 마지막 칸 뒤의 `*`, 필드 안에 쓸 수 없는 문자(`*`, `#`), UTF-8 실수 세 가지만 조심하면 된다.

<small>근거: ISO 11783-12 B.1, B.2, B.5, B.10, Annex A, 6.5, 6.7</small>

## 4. ISOBUS 인증 정보 메시지

ISOBUS 장치는 적합성 시험(표준을 제대로 따르는지 확인하는 시험)을 받는다. 가전제품에 붙은 인증 마크처럼, 이 메시지는 "어느 시험소가 어떤 시험 프로토콜로 시험했고 참조 번호가 무엇인지"를 8바이트로 알린다.

2절 표에서 진단 UI가 모으는 "적합성 시험 데이터"는 Part 12가 아니라 ISO 11783-7(트랙터와 작업기가 주고받는 메시지를 정하는 표준 문서)에 정의된 메시지로 나간다. 특정 ECU의 적합성 인증 상태를 알리는 메시지다.

| 항목 | 값 |
|---|---|
| PGN | 64834 (0xFD42) |
| DP / PF / PS | 0 / 253 / 66 |
| 기본 priority | 6 |
| 데이터 길이 | 8 byte |
| 전송 주기 | On request |

그림은 8바이트의 비트 배치다. 칸 위의 8~1은 바이트 안의 비트 번호다. 칸 안의 글자는 그 비트가 속한 필드(Y 연도, R 개정 번호, T 시험소 종류, L 시험소 ID, V 메시지 개정)이고, 글자 뒤 숫자는 그 필드 안에서 몇 번째 비트인지(1이 가장 낮은 자리)를 뜻한다.

![ISOBUS compliance certification 메시지의 3판 비트 배치: Byte 1에 개정 번호 하위 2비트와 시험 연도 6비트, Byte 2에 시험소 ID 하위 3비트·개정 번호 비트 5~4·시험소 종류 2비트·개정 번호 비트 3, Byte 3에 시험소 ID 상위 8비트, Byte 4~5 예약, Byte 6 bit 8 메시지 개정, Byte 7~8 참조 번호](/images/study-isobus/14-cert-layout-light.png)
![ISOBUS compliance certification 메시지의 3판 비트 배치: Byte 1에 개정 번호 하위 2비트와 시험 연도 6비트, Byte 2에 시험소 ID 하위 3비트·개정 번호 비트 5~4·시험소 종류 2비트·개정 번호 비트 3, Byte 3에 시험소 ID 상위 8비트, Byte 4~5 예약, Byte 6 bit 8 메시지 개정, Byte 7~8 참조 번호](/images/study-isobus/14-cert-layout-dark.png)

### 필드 (3판 이후 형식)

| 필드 | 비트 수 | 위치 | 정의 |
|---|---|---|---|
| 시험 프로토콜 발행 연도 (SPN 4313) | 6 | Byte 1 bit 6~1 | 1년/bit, 오프셋 2000 → 2000~2061 |
| 시험 프로토콜 개정 (SPN 4314) | 5 | 비트 2~1은 Byte 1 bit 8~7, 비트 3은 Byte 2 bit 1, 비트 5~4는 Byte 2 bit 5~4 | 같은 해에 시험 프로토콜 개정이 여럿이면 연도에 붙는 번호. 0~30 |
| 시험소 종류 (SPN 4315) | 2 | Byte 2 bit 3~2 | `00` 비인증 시험소·자가 인증, `01` AEF 인증 시험소, `10` 예약, `11` 미가용(인증 안 됨) |
| 시험소 ID (SPN 4316) | 11 | 하위 3비트는 Byte 2 bit 8~6, 상위 8비트는 Byte 3 | 시험을 수행한 시험소의 manufacturer code. 자가 인증이면 그 CF의 주소 클레임 메시지(NAME)에 든 manufacturer code와 같다 |
| 예약 | 23 | Byte 4~5, Byte 6 bit 7~1 | 0으로 보낸다 |
| 메시지 개정 (SPN 7446) | 1 | Byte 6 bit 8 | `0` 2판 형식, `1` 3판 이후 형식 |
| 인증 참조 번호 (SPN 4330) | 16 | Byte 7~8, LSB 먼저 | 시험소가 부여한 번호, 0~64 255. 시험소 ID·CF 제조사 ID와 함께 시험소의 시험 파일을 유일하게 가린다 |

"1년/bit, 오프셋 2000"은 값이 1 늘 때마다 1년씩 늘고 값 0이 2000년이라는 뜻이다. 값 17이면 2017년이다. AEF(Agricultural Industry Electronics Foundation)는 ISOBUS 적합성 시험을 운영하는 농기계 업계 단체다.

- 바이트 경계를 넘는 필드는 ISO 11783-7의 일반 규칙대로 하위 비트가 앞 바이트에, 상위 비트가 다음 바이트의 bit 1부터 들어간다. 시험소 ID는 `(Byte3 << 3) | (Byte2 >> 5)`로 복원한다. `<<`는 비트를 왼쪽으로 미는 연산, `>>`는 오른쪽으로 미는 연산, `|`는 두 값의 비트를 합치는 연산이다.
- 예약 비트가 1이 아니라 0이다. ISO 11783-7의 일반 규칙은 예약 비트를 기본적으로 1로 채우게 하지만, 메시지 정의가 따로 적으면 그것을 따른다. 같은 규칙은 일부 메시지가 앞으로의 호환을 위해 0을 기본값으로 쓰고, 그런 메시지에서 0은 "지원 안 함"을 뜻한다고 설명한다.
- 진단 UI는 적합성 시험 데이터를 이 메시지에서 얻는다. 다만 메시지에 실리는 연도는 시험을 한 해가 아니라 시험 프로토콜의 발행 연도다.

### 메시지 하나 풀어 읽기

아래 코드가 만드는 예시 메시지 `91 62 24 00 00 80 D2 04`(가상의 값)를 손으로 풀어 보자.

| Byte | 값 | 2진수 | 읽은 결과 |
|---|---|---|---|
| 1 | `91` | `10 010001` | bit 8~7 = `10`: 개정 번호 비트 2~1. bit 6~1 = `010001` = 17: 연도 2000 + 17 = 2017 |
| 2 | `62` | `011 00 01 0` | bit 8~6 = `011`: 시험소 ID 하위 3비트(3). bit 5~4 = `00`: 개정 번호 비트 5~4. bit 3~2 = `01`: AEF 인증 시험소. bit 1 = `0`: 개정 번호 비트 3 |
| 3 | `24` | `0010 0100` | 시험소 ID 상위 8비트 = 36 |
| 4~5 | `00 00` | | 예약(0) |
| 6 | `80` | `1 0000000` | bit 8 = `1`: 3판 이후 형식. 나머지는 예약(0) |
| 7~8 | `D2 04` | | LSB 먼저이므로 `0x04D2` = 1234: 인증 참조 번호 |

- 개정 번호: 비트 5~4(`00`), 비트 3(`0`), 비트 2~1(`10`)을 이어 붙이면 `00010` = 2다.
- 시험소 ID: `(0x24 << 3) | (0x62 >> 5)` = 36 × 8 + 3 = 291 = `0x123`이다.

### 2판 형식과의 차이 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 장 끝의 핵심 정리로 가도 된다.
:::

옛 장치(2판 형식)가 보낸 메시지까지 읽으려면 차이를 알아야 한다.

- 2판 형식에서 개정은 3비트였다. `000` 첫 개정(접미사 없음), `001` 둘째(접미사 A), `010` 셋째(B), `011` 넷째(C), `111` 미가용이다. 위치는 Byte 1 bit 8~7과 Byte 2 bit 1로, 지금의 비트 1~3 자리와 같다. 3판은 예약이던 Byte 2 bit 5~4를 비트 4~5로 붙여 5비트로 넓혔고, 알파벳 접미사 대신 번호를 쓴다.
- 2판의 Byte 4~5는 인증 종류 비트였다. Byte 4는 bit 8부터 Minimum CF, TECU Class 1, TECU Class 2, TECU Class 3, Class 3 ECU, VT, VT working set master, VT working set member이고, Byte 5는 bit 8부터 TC, TC working set master, TC working set member, File server, GPS receiver다. 3판은 이 비트를 모두 deprecated(더는 쓰지 않음)로 돌리고, functionality 정보를 Part 12의 functionalities 메시지([28장](/study/isobus/28-diagnostics-dm-fmi))로 옮겼다.
- 2판의 Byte 6은 전부 예약(0)이었다. 그래서 옛 장치가 보낸 메시지는 Byte 6 bit 8이 0이고, 수신 측은 이 비트 하나로 형식을 가른다.
- 시험소 종류는 2판에서 3비트 파라미터(`000` 비인증·자가 시험, `001` EU 인증 시험소, `010` NA 인증 시험소, `111` 미가용)로 정의됐다. 그런데 같은 2판 메시지 배치에는 Byte 2 bit 3~2의 2비트 자리만 있다. 표준 안에서 어긋나는 부분이라 확인이 필요하다.

아래 코드는 3판 형식으로 인코딩하고, Byte 6 bit 8을 보고 2판·3판을 갈라 디코딩한다.

::: details Python으로 인코딩·디코딩 검산
```python
LEGACY_BITS = {                       # 2판 형식 Byte 4~5 (3판에서 deprecated)
    (4, 8): "Minimum CF", (4, 7): "TECU Class 1", (4, 6): "TECU Class 2", (4, 5): "TECU Class 3",
    (4, 4): "Class 3 ECU", (4, 3): "VT", (4, 2): "VT WS master", (4, 1): "VT WS member",
    (5, 8): "TC", (5, 7): "TC WS master", (5, 6): "TC WS member", (5, 5): "File server",
    (5, 4): "GPS receiver",
}


def encode_cert(year, revision, lab_type, lab_id, reference):
    assert 2000 <= year <= 2061 and 0 <= revision <= 30
    assert 0 <= lab_type <= 3 and 0 <= lab_id < 2 ** 11 and 0 <= reference <= 64255
    b1 = (revision & 0b11) << 6 | (year - 2000)
    b2 = (lab_id & 0b111) << 5 | (revision >> 3) << 3 | lab_type << 1 | (revision >> 2) & 1
    return bytes([b1, b2, lab_id >> 3, 0x00, 0x00, 0x80, reference & 0xFF, reference >> 8])


def decode_cert(d):
    third = d[5] >> 7                                   # A.29.19 메시지 개정 비트
    revision = d[0] >> 6 | (d[1] & 1) << 2
    if third:
        revision |= ((d[1] >> 3) & 0b11) << 3
    return {
        "format": "3판 이후" if third else "2판",
        "year": 2000 + (d[0] & 0x3F),
        "revision": revision,
        "lab_type": (d[1] >> 1) & 0b11,
        "lab_id": d[2] << 3 | d[1] >> 5,
        "reference": d[6] | d[7] << 8,
        "legacy_types": None if third else
            [name for (byte, bit), name in LEGACY_BITS.items() if d[byte - 1] >> (bit - 1) & 1],
    }


def hx(b):
    return " ".join(f"{x:02X}" for x in b)


msg = encode_cert(year=2017, revision=2, lab_type=0b01, lab_id=0x123, reference=1234)  # 가상의 값
print(hx(msg), decode_cert(msg))
assert msg == bytes.fromhex("91 62 24 00 00 80 D2 04")

for rev in range(31):
    for lab in (0, 1, 0x123, 0x7FF):
        back = decode_cert(encode_cert(2020, rev, 0b01, lab, 7))
        assert (back["revision"], back["lab_id"]) == (rev, lab)

legacy = bytes([0x4C, 0x60, 0x24, 0b10000010, 0b01000000, 0x00, 0xD2, 0x04])
print(decode_cert(legacy))
assert decode_cert(legacy)["revision"] == 1                       # 001 = 접미사 A
assert decode_cert(legacy)["legacy_types"] == ["Minimum CF", "VT WS master", "TC WS master"]
```

첫 출력 줄이 위에서 손으로 풀어 본 `91 62 24 00 00 80 D2 04`다. 두 번째 출력은 2판 형식 예(`legacy`)를 디코딩한 것이다. Byte 6이 `0x00`이라 2판으로 읽고, 연도 2012(`0x4C`의 bit 6~1), 개정 1(접미사 A), Byte 4~5 비트에서 Minimum CF·VT WS master·TC WS master 인증을 읽어 낸다.
:::

정리하면, 인증 정보 메시지는 연도·개정·시험소·참조 번호를 8바이트에 비트 단위로 싣고, Byte 6 bit 8 하나로 2판과 3판 형식을 가른다.

<small>근거: ISO 11783-7 B.27, A.29, 3.3, 3.3.1; ISO 11783-12 B.3</small>

::: details 원문을 가진 독자를 위한 메모
- 2절 "필수 메시지"는 Part 12 6.1, 진단 UI 정보 표는 6.2 a)~e)(네트워크 정보)와 6.4 a)~d)(CF 정보, 마지막 줄의 클리어는 6.4 끝 문장), 네트워크 통계는 6.3, 서비스 툴은 6.6과 5절, 네트워크 구성 그림은 Annex C의 Figure C.1(커넥터는 C.2), 예시 화면은 Annex D.1(네트워크 정보)과 D.2(네트워크 통계)다.
- 요청·응답 표의 메시지는 Part 12 Annex B 순서다. ECU identification B.1, Software identification B.2, ISOBUS certification B.3(실제 정의는 Part 7 B.27), NAME B.4(Part 5), Diagnostic protocol B.5, DM1 B.6, DM2 B.7, DM3 B.8, Functionalities B.9, Product identification B.10. Request 형식은 Part 3 5.4.3, PDU2 응답과 TP 방식은 Part 3 Table 5, NAME 요청에 전역으로 답하는 예외는 Part 3 5.4.3과 Part 5 4.5.3, Tr·T3는 Part 3 5.13.3, 주소 오류 검출은 Part 5 4.4.4.1이다.
- 3절의 문자 범위는 A.1 등과 6.7, Software identification의 `#` 금지는 A.4, ECU hardware ID의 `#` 예약은 A.13이다. ECU identification 필드는 A.1(part number), A.2(serial number), A.7(location), A.8(type), A.5(manufacturer name), A.13(hardware ID), Software identification 필드 수는 A.3, Product identification은 A.14(code)와 A.16(model), Diagnostic protocol 값은 A.6이다. "진단 전용, 런타임 구성에 쓰지 말 것" 문장은 6.5(Functionalities 절)의 마지막 문장이다. 문장은 Functionalities 절 끝에 놓여 있지만 문언이 지목하는 대상은 diagnostic protocol 메시지다.
- 원문 예시 2의 `LG-LK123–20050421`에 찍힌 대시는 원문 텍스트에서 en dash(U+2013)다. Latin 1에 없는 문자라 그대로는 인코딩되지 않으니, 테스트 벡터로 옮길 때는 하이픈(`0x2D`)으로 읽는다(원문 의도에 대한 추론). 원문 예시 1은 [부록](/study/isobus/appendix-iso-part12)에 옮겨 두었다.
- Product identification 원문 예시는 설명에 model 1926i라고 적고 바이트열에는 `1962i`를 썼다. 둘 중 하나는 원문 오기다.
- 4절은 ISO 11783-7:2015 B.27이다(Part 12 B.3이 이 메시지를 가리킨다). 필드는 A.29.1(연도), A.29.2(개정), A.29.3(시험소 종류), A.29.4(시험소 ID), A.29.18(참조 번호), A.29.19(메시지 개정), 2판 인증 종류 비트는 A.29.5~A.29.17(3판에서 deprecated)이다. 2판 시험소 종류의 3비트 정의는 A.29.3의 Note에 있다. 2018년 Amendment 1은 B.27과 A.29를 고치지 않았다. 바이트 경계 규칙은 Part 7 3.3.1, 예약 비트 기본값 설명은 Part 7 3.3이다.
:::

::: tip 핵심 정리
- 고장 코드는 SPN(어디가)과 FMI(어떻게)의 조합이다. 여기에 발생 횟수(OC)를 더해 4바이트 DTC로 묶는다.
- DM1은 현재 활성 고장(활성 중 1 Hz 전송), DM2는 이전 고장 이력(요청 시에만 전송), DM3는 이전 고장 기록(DM2) 초기화 명령이다.
- 모든 CF는 Part 12의 진단 요청 열 가지에 답해야 한다. 8 byte를 넘는 응답은 전역 요청이면 BAM, 지정 요청이면 RTS/CTS로 나간다.
- ECU·소프트웨어·제품 식별 정보는 Latin 1 문자열을 `*`로 끊어 싣는다. 마지막 필드 뒤에도 `*`가 붙는다.
- ISOBUS 인증 정보 메시지는 시험 프로토콜 연도·개정, 시험소 종류·ID, 참조 번호를 8바이트에 싣고, Byte 6 bit 8로 2판과 3판 형식을 가른다.
:::

::: details 확인 문제
1. (개념) "SPN 100 + FMI 1"과 "SPN 100 + FMI 3"은 각각 무엇을 뜻하나? 정비사가 먼저 볼 곳은 어떻게 다른가?
2. (개념) 계기판 경고등 비유로 DM1, DM2, DM3를 한 문장씩 설명하라. DM3를 보내면 DM1에 있던 활성 고장도 사라지는가?
3. (계산) 진단 UI가 SA `0x90`(144)인 CF에게 Software identification을 지정 요청하려 한다. Request 데이터 3바이트는 무엇인가? 응답이 32 byte라면 어떤 방식으로 오는가?
4. (디코딩) ECU identification 응답이 `HC-2210-04*250930117*Right boom*Section I/O*Example Agri*HW 3.1*`이다. 제조사명과 hardware ID는 무엇인가? 응답은 몇 byte이고 TP 패킷 몇 개로 오는가?
5. (디코딩) ISOBUS certification 메시지 `91 62 24 00 00 80 D2 04`에서 형식(2판/3판), 시험 프로토콜 연도, 개정 번호, 시험소 종류, 시험소 ID, 참조 번호를 구하라.

**답 가이드**
1. 둘 다 엔진 오일 압력(SPN 100)에 관한 고장이다. FMI 1은 값은 믿을 수 있는데 정상보다 낮다(가장 심한 수준)는 뜻이라 실제 오일 압력부터 본다. FMI 3은 신호 전압이 정상보다 높거나 높은 전원 쪽에 단락됐다는 뜻이라 센서와 배선부터 본다.
2. DM1은 지금 켜져 있는 경고등 목록, DM2는 정비 기록부에 남은 지난 고장 목록, DM3는 그 지난 기록을 지우라는 명령이다. DM3는 이전 고장(DM2) 기록만 지우고 활성 고장(DM1) 데이터에는 영향을 주지 않는다.
3. PGN 65242 = `0x00FEDA`를 낮은 자리 바이트부터 적은 `DA FE 00`이다. 32 byte는 8 byte를 넘고 요청이 지정 주소로 갔으므로 RTS/CTS로 요청자에게 온다.
4. 다섯 번째 필드 `Example Agri`가 제조사명, 여섯 번째 `HW 3.1`이 hardware ID다. 글자 58개에 `*` 6개를 더해 64 byte이고, TP 패킷 하나가 7 byte씩 실으므로 10개로 온다.
5. Byte 6 bit 8이 1이라 3판 이후 형식이다. Byte 1 `91`의 bit 6~1이 17이므로 연도는 2017이다. 개정 번호는 Byte 2의 bit 5~4(`00`)와 bit 1(`0`), Byte 1의 bit 8~7(`10`)을 이어 붙인 `00010` = 2다. Byte 2 `62`의 bit 3~2가 `01`이라 AEF 인증 시험소다. 시험소 ID는 `(0x24 << 3) | (0x62 >> 5)` = 288 + 3 = 291(`0x123`), 참조 번호는 `D2 04`를 LSB부터 읽은 `0x04D2` = 1234다.
:::

## 다음 챕터

- 다음: [28장 진단 (2): DM1·DM2·DM3, FMI, Functionalities](/study/isobus/28-diagnostics-dm-fmi)
