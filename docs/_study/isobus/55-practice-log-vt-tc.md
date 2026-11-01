---
title: "종합 실습 (1): 로그, PGN, VT, TC"
description: "CAN 로그를 PGN과 주소로 나눠 읽고, 파이썬으로 값을 디코딩하고, VT 오브젝트 풀과 TC 가변 살포 흐름을 직접 구성해 본다."
date: 2026-04-13
tags: [ISOBUS, CAN, PGN, VirtualTerminal, TaskController, Python]
prev: /study/isobus/54-sequence-control-details
next: /study/isobus/56-practice-isoxml
---

# 종합 실습 (1): 로그, PGN, VT, TC

::: info 학습 목표
- CAN 로그 한 줄을 우선순위, PGN, 받는 주소, 보낸 주소로 나눠 읽을 수 있다.
- 파이썬 코드로 CAN ID를 분해하고 엔진 회전수 같은 값을 꺼낼 수 있다.
- 두 화면짜리 VT 오브젝트 풀의 오브젝트 목록과 계층을 설명할 수 있다.
- 처방 맵으로 살포량을 바꾸는 작업이 어떤 순서로 흘러가는지 설명하고 시뮬레이터로 확인할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [9장 J1939 메시지 구조](/study/isobus/09-j1939-message), [32장 VT 오브젝트 풀 기초](/study/isobus/32-vt-object-pool-basics), [41장 TC 기초](/study/isobus/41-tc-basics)
- 이 장에서 처음 나오는 말
  - 로그: 버스에 흐른 CAN 프레임을 시간 순서대로 적어 둔 텍스트 파일
  - 디코딩: 바이트 묶음을 사람이 읽는 값(회전수, 속도 등)으로 바꾸는 일
  - 처방 맵: 밭의 위치마다 뿌릴 양을 정해 둔 지도
  - 가변 살포: 처방 맵을 따라 위치마다 살포량을 바꾸며 뿌리는 작업
  - As-Applied 기록: 실제로 뿌린 양을 위치, 시각과 함께 남긴 작업 기록
:::

외국어를 배울 때 단어와 문법을 익혔다면 다음은 실제 신문 기사를 읽어 볼 차례다. 이 장은 지금까지 배운 CAN, J1939, VT, TC를 실제와 같은 데이터에 적용해 보는 "신문 읽기" 단계다. 실습은 네 개이고, 버스 위의 바이트에서 시작해 작업 전체의 흐름까지 한 단계씩 올라간다. 각 실습은 목표, 필요한 지식, 준비물로 시작해 결과 확인으로 끝난다.

::: info 실습 전체 준비물
- 파이썬 3.10 이상. 4절 코드가 `float | None` 같은 3.10 문법을 쓴다.
- 코드를 붙여 넣을 텍스트 편집기와 터미널. 각 실습의 코드는 파일 하나로 저장해 `python3 파일이름.py`로 실행한다.
- 1절의 python-can 예제만 외부 패키지가 필요하다(`pip install python-can`). 나머지 코드는 파이썬 기본 기능만 쓴다.
- 실제 CAN 장비는 없어도 된다. 모든 실습은 이 글에 실린 데이터로 한다.
:::

## 1. 실습 1: CAN 로그 읽기

::: info 실습 안내
- 목표: 로그 12줄을 메시지 종류별로 나누고, 줄마다 누가 누구에게 무엇을 보냈는지 말할 수 있다.
- 필요한 지식: [4장 CAN 데이터 프레임](/study/isobus/04-can-data-frame)(확장 ID와 데이터 바이트), [9장 J1939 메시지 구조](/study/isobus/09-j1939-message)(29비트 ID와 PGN), [10장 요청과 응답](/study/isobus/10-j1939-request-ack)(Request), [13장 주소 클레임](/study/isobus/13-j1939-address-claim), [15장 TP 기초](/study/isobus/15-tp-bam-cmdt)(BAM)
- 준비물: 아래 로그, 16진수를 2진수로 바꿔 줄 계산기(운영체제의 프로그래머용 계산기면 충분하다)
:::

이 절에서는 로그를 손으로 읽는다. 분석 도구가 대신 해 주는 일을 한 번 직접 해 보면, 나중에 도구의 출력이 이상할 때 스스로 알아챌 수 있다.

### 1.1 예시 로그

아래는 실제 ISOBUS 트래픽과 같은 형식으로 만든 예시 로그이다.
형식은 `CAN_ID#DATA` (socketcan candump 포맷)이다.

`#` 앞의 16진수 8자리는 29비트 CAN ID이고, `#` 뒤는 데이터 바이트를 두 글자씩 붙여 쓴 것이다. 예를 들어 `18EAFFFE#00EE00`은 ID가 0x18EAFFFE이고 데이터가 `00 EE 00` 세 바이트다. candump가 파일로 저장한 로그에는 줄 앞에 시각과 인터페이스 이름이 붙지만(`(시각) can0 18EAFFFE#00EE00`), 여기서는 프레임 부분만 남겼다.

```
0CF00400#FF3C320000FFFF00
18EAFFFE#00EE00
18EEFF00#FFB0320400000200
0CFE49F0#014B00FA02000000
18EA2681#C5FD00
1CEA00F9#DAFE00
18ECFF26#20120003FF12FF00
18EBFF26#01B003020006043C
18EBFF26#02FFFFFFFFFFFFFE
18EBFF26#03FF640000FFFFFF
0CF00400#FF8C4B0000FFFF00
18E60026#000132000100051F
```

### 1.2 한 줄을 손으로 나눠 보기

CAN ID를 나누는 규칙은 [9장](/study/isobus/09-j1939-message)에서 배웠다. 한 줄로 복습하면, 29비트 ID는 앞에서부터 우선순위 3비트, 예약 비트 1비트, 데이터 페이지(DP) 1비트, PF 8비트, PS 8비트, SA 8비트로 이루어진다. PF(PDU Format)는 메시지 종류를 가르는 칸이고, SA(Source Address)는 보낸 장치의 주소다. PF가 0xF0(=240)보다 작으면 PS(PDU Specific)는 받는 장치의 주소(DA, Destination Address)이고, 0xF0 이상이면 PS는 PGN의 일부라서 받는 주소가 없는 방송 메시지가 된다.

로그 둘째 줄 `18EAFFFE#00EE00`을 이 규칙대로 나눠 보자.

1. ID 16진수 8자리를 두 글자씩 끊는다: `18` `EA` `FF` `FE`.
2. 마지막 바이트 `FE`가 SA다. 0xFE(=254)는 아직 주소를 얻지 못한 장치가 쓰는 "주소 없음(null)" 값이다.
3. 둘째 바이트 `EA`가 PF, 셋째 바이트 `FF`가 PS다. PF 0xEA(=234)는 0xF0보다 작으므로 PS `FF`는 받는 주소다. 0xFF(=255)는 "모두에게"를 뜻하는 전역 주소다.
4. 첫 바이트 `18`을 2진수로 쓰면 `0001 1000`이다. 16진수 8자리는 32비트라서 29비트 ID보다 3비트 길고, 맨 앞 3비트(`000`)는 ID에 속하지 않는 빈자리다. 그다음 3비트 `110`이 우선순위 6, 이어지는 `0`이 예약 비트, 마지막 `0`이 데이터 페이지다.
5. PGN을 만든다. PF가 0xF0보다 작으므로 PGN의 아래 8비트는 0으로 둔다. 데이터 페이지 0, PF `EA`, 아래 8비트 `00`을 이어 붙이면 0xEA00(=59904), 곧 Request(요청) 메시지다.
6. Request의 데이터 3바이트는 요청하는 PGN이다. 낮은 자리 바이트가 먼저 오는 리틀 엔디언이므로 `00 EE 00`을 거꾸로 읽어 0x00EE00, 곧 0xEE00(=60928) Address Claimed다.

정리하면 "아직 주소가 없는 장치(0xFE)가 모든 장치(0xFF)에게 각자의 주소 클레임을 보내 달라고 요청했다"는 뜻이다. 아래 그림은 같은 방법으로 방송 메시지 하나(첫째 줄)와 1:1 메시지 하나(둘째 줄)를 나란히 나눈 것이다.

![CAN ID 0CF00400과 18EAFFFE를 우선순위, 예약 비트, 데이터 페이지, PF, PS, SA 칸으로 나누고, PF가 0xF0 이상이면 PS가 PGN에 들어가고 0xF0보다 작으면 PS가 받는 주소가 되는 차이를 보인 그림](/images/study-isobus/55-can-id-example-light.png)
![CAN ID 0CF00400과 18EAFFFE를 우선순위, 예약 비트, 데이터 페이지, PF, PS, SA 칸으로 나누고, PF가 0xF0 이상이면 PS가 PGN에 들어가고 0xF0보다 작으면 PS가 받는 주소가 되는 차이를 보인 그림](/images/study-isobus/55-can-id-example-dark.png)

### 1.3 메시지 분류표

12줄을 모두 같은 방법으로 나눈 결과가 아래 표다. 열은 왼쪽부터 로그의 줄 번호, CAN ID, PGN(메시지 종류 번호)과 이름, SA(보낸 주소), DA(받는 주소), 분류(무슨 내용인지)다. DA 칸의 `-`는 방송 메시지라서 받는 주소가 없다는 뜻이다.

각 메시지를 분석한다.

| # | CAN ID | PGN | SA | DA | 분류 |
|---|--------|-----|----|----|------|
| 1 | `0CF00400` | 0xF004 (EEC1) | 0x00 | - | Engine Speed (엔진 RPM) |
| 2 | `18EAFFFE` | 0xEA00 (Request PGN) | 0xFE | 0xFF | PGN 0xEE00 요청 (Address Claimed) |
| 3 | `18EEFF00` | 0xEE00 (Address Claimed) | 0x00 | 0xFF | 주소 클레임 (SA=0x00, 엔진 ECU의 NAME) |
| 4 | `0CFE49F0` | 0xFE49 (Ground-based Speed) | 0xF0 | - | 지상 속도 (Ground-based Speed and Distance) |
| 5 | `18EA2681` | 0xEA00 (Request PGN) | 0x81 | 0x26 | VT(0x26)에게 PGN 0xFDC5(ECU identification) 요청 |
| 6 | `1CEA00F9` | 0xEA00 (Request PGN) | 0xF9 | 0x00 | 엔진(0x00)에게 PGN 0xFEDA(Software identification) 요청 |
| 7 | `18ECFF26` | 0xEC00 (TP.CM) | 0x26 | 0xFF | Transport Protocol 연결 개시 (BAM: Proprietary B PGN 0xFF12, 18바이트·3패킷) |
| 8 | `18EBFF26` | 0xEB00 (TP.DT) | 0x26 | 0xFF | Transport Protocol 데이터 패킷 1 |
| 9 | `18EBFF26` | 0xEB00 (TP.DT) | 0x26 | 0xFF | Transport Protocol 데이터 패킷 2 |
| 10 | `18EBFF26` | 0xEB00 (TP.DT) | 0x26 | 0xFF | Transport Protocol 데이터 패킷 3 |
| 11 | `0CF00400` | 0xF004 (EEC1) | 0x00 | - | Engine Speed (같은 엔진의 다음 샘플) |
| 12 | `18E60026` | 0xE600 (VT-to-ECU) | 0x26 | 0x00 | VT 소프트키 상태 전송 (Soft Key Activation) |

표를 메시지 묶음으로 다시 보면 로그의 흐름이 보인다.

- <strong>1, 11행</strong>: 엔진(주소 0x00)이 주기적으로 방송하는 EEC1(Electronic Engine Controller 1, 엔진 상태 메시지)이다. 같은 ID가 반복해서 나오는 것은 주기 메시지의 전형적인 모습이다.
- <strong>2, 3행</strong>: 요청과 응답의 짝이다. 주소 없는 장치가 주소 클레임을 요청하자 엔진이 Address Claimed로 답했다. 3행의 데이터 8바이트가 엔진의 NAME(장치의 이름표, [12장](/study/isobus/12-j1939-address-name))이다.
- <strong>4행</strong>: 트랙터 ECU(TECU)가 방송하는 지상 속도다. 이 로그에서 TECU의 주소는 0xF0이다. 메시지 내용은 [23장](/study/isobus/23-implement-messages-basics)에서 다뤘다.
- <strong>5, 6행</strong>: 다른 장치에 정보를 달라는 Request다. 5행은 주소 0x81인 장치가 VT(0x26)에게 ECU identification(PGN 0xFDC5=64965)을, 6행은 주소 0xF9인 장치가 엔진에게 Software identification(PGN 0xFEDA=65242)을 요청했다. 두 응답은 이 12줄 안에 없다. 두 메시지는 [27장](/study/isobus/27-diagnostics-identification)에서 다뤘다.
- <strong>7~10행</strong>: VT가 8바이트보다 긴 데이터를 BAM(모두에게 보내는 TP 방식)으로 보냈다. 7행 TP.CM(PGN 0xEC00=60416)이 "18바이트를 3패킷으로 보낸다"고 예고하고, 8~10행 TP.DT(PGN 0xEB00=60160)가 7바이트씩 실어 나른다.
- <strong>12행</strong>: VT가 주소 0x00 장치에게 "소프트키가 눌렸다"고 알린 Soft Key Activation이다. VT가 작업기 ECU로 보내는 메시지는 모두 PGN 0xE600(=58880, VT to ECU)을 쓴다.

### 1.4 결과 확인: 세 메시지 직접 풀어 보기

표의 분류가 맞는지 데이터 바이트까지 열어 확인한다. 결과가 아래와 같으면 이 실습은 성공이다.

<strong>3행 NAME 읽기.</strong> 데이터 `FF B0 32 04 00 00 02 00`이 NAME 8바이트다. NAME은 리틀 엔디언이라 첫 바이트가 가장 낮은 자리다. 필드 배치는 [12장](/study/isobus/12-j1939-address-name)과 같다.

| 바이트 | 값 | 들어 있는 필드 | 읽은 값 |
|---|---|---|---|
| 1~3 (일부) | `FF B0 32` | 식별 번호 21비트 | 0x12B0FF(예시 값) |
| 3 (일부)~4 | `32 04` | 제조사 코드 11비트 | 33(예시 값) |
| 5 | `00` | ECU 인스턴스, 기능 인스턴스 | 0, 0 |
| 6 | `00` | 기능(Function) | 0 = 엔진 |
| 7 | `02` | 예약 비트 1비트 + 장치 클래스 7비트 | 예약 0, 장치 클래스 1 = 트랙터 |
| 8 | `00` | 장치 클래스 인스턴스, 산업 그룹, 자체 주소 설정 | 0, 0(전역), 0 |

바이트 7 `02`는 2진수 `0000 0010`이다. 가장 낮은 비트 `0`이 예약 비트이고, 나머지 7비트 `0000001`이 장치 클래스 1이다. 결국 "트랙터의 엔진 ECU"라는 이름이다. 표준 문서는 엔진이 하나인 트랙터의 엔진 ECU NAME 예로 산업 그룹 0, 장치 클래스 1, 기능 0, 나머지 인스턴스 0을 드는데, 이 로그의 NAME이 바로 그 구성이다.

<strong>7~10행 BAM 다시 조립하기.</strong> 7행 TP.CM 데이터 `20 12 00 03 FF 12 FF 00`은 다음과 같이 읽는다.

1. `20`(=32): 제어 바이트. 32는 BAM이다.
2. `12 00`: 전체 크기. 리틀 엔디언이라 0x0012 = 18바이트다.
3. `03`: 패킷 수 3.
4. `FF`: BAM에서 쓰지 않는 자리라 `FF`로 채운다.
5. `12 FF 00`: 실어 나르는 메시지의 PGN. 거꾸로 읽어 0x00FF12 = 0xFF12(=65298)다. 0xFF00~0xFFFF는 제조사가 자유롭게 쓰는 Proprietary B 영역이다.

8~10행 TP.DT는 첫 바이트가 순서 번호(1, 2, 3)이고 나머지 7바이트가 데이터다. 18바이트 = 7 + 7 + 4이므로 3번 패킷은 앞 4바이트(`FF 64 00 00`)만 진짜 데이터이고 뒤 3바이트 `FF FF FF`는 빈자리를 채운 값이다. 이어 붙인 결과는 `B0 03 02 00 06 04 3C FF FF FF FF FF FF FE FF 64 00 00`이다. Proprietary B 메시지라서 내용의 뜻은 만든 제조사만 안다.

<strong>12행 Soft Key Activation 읽기.</strong> 데이터 `00 01 32 00 01 00 05 1F`는 다음과 같다. 메시지 구조는 [36장](/study/isobus/36-vt-commands-basics)에서 다뤘다.

| 바이트 | 값 | 뜻 |
|---|---|---|
| 1 | `00` | VT 기능 코드 0 = Soft Key Activation |
| 2 | `01` | 키 활성화 코드 1 = 눌렸다(0이면 뗐다, 2면 계속 누르고 있다, 3이면 누르기 취소) |
| 3~4 | `32 00` | 눌린 Key 오브젝트의 ID 0x0032(=50) |
| 5~6 | `01 00` | 그 키를 보여 주던 부모 오브젝트(보이는 데이터 마스크)의 ID 0x0001 |
| 7 | `05` | 소프트키 코드 5(Working Set이 정한 키 번호) |
| 8 | `1F` | 상위 4비트 = TAN 1(요청과 응답을 짝짓는 번호), 하위 4비트 = 예약 값 F |

이 로그는 3절의 오브젝트 풀과 다른 장치에서 나온 예시라서, 여기 나온 오브젝트 ID는 3절 표와 맞지 않는다.

### 1.5 분석 도구 소개

손으로 한 일을 도구로 자동화할 수 있다. 하나는 코드로 다루는 라이브러리, 하나는 화면으로 보는 프로그램이다.

**python-can**

```bash
pip install python-can
```

아래 코드는 로그 파일을 한 프레임씩 읽어 ID와 데이터를 출력한다. `msg.arbitration_id`가 CAN ID, `msg.data`가 데이터 바이트다.

```python
import can

# Log file replay
with can.Bus(interface="virtual", channel="test") as bus:
    with can.LogReader("isobus_capture.asc") as reader:
        for msg in reader:
            print(f"ID=0x{msg.arbitration_id:08X}  "
                  f"Data={msg.data.hex().upper()}")
```

실행하면 프레임마다 `ID=0x18EAFFFE  Data=00EE00` 같은 줄이 나온다. `isobus_capture.asc`는 Vector ASC 형식의 로그 파일 이름이다. `LogReader`는 확장자를 보고 파일 형식을 고르므로 candump로 저장한 `.log` 파일도 같은 방법으로 읽는다. 이 예제는 가상 버스(`virtual`)를 열어 두기만 하고 쓰지는 않는다.

**SavvyCAN**
- GUI 기반 CAN 분석 도구 (무료, 오픈소스)
- ISOBUS 전용 디코더 플러그인 지원
- J1939 PGN 데이터베이스 내장
- 다운로드: https://www.savvycan.com

<small>근거: ISO 11783-5 A.1, ISO 11783-6 H.2</small>

## 2. 실습 2: PGN 디코딩

::: info 실습 안내
- 목표: CAN ID에서 우선순위, PGN, 주소를 꺼내는 함수와 EEC1에서 엔진 회전수를 꺼내는 함수를 실행하고 결과를 읽는다.
- 필요한 지식: [9장 J1939 메시지 구조](/study/isobus/09-j1939-message)(PGN, SPN, 분해능과 오프셋), [23장 트랙터-작업기 메시지 (1)](/study/isobus/23-implement-messages-basics)(지상 속도)
- 준비물: 파이썬 3.10 이상. 2.1절과 2.2절의 코드를 한 파일(`decode_log.py`)에 차례로 이어 붙여 저장한다.
:::

1절에서 손으로 한 일을 코드로 옮긴다. 먼저 CAN ID를 나누는 함수를 만들고, 그 위에 메시지 종류별 해석 함수를 얹는다.

### 2.1 CAN ID에서 PGN·SA 추출 공식

29비트 CAN ID 구조 (J1939 기준):

![29비트 CAN Identifier 비트 필드 배치](/images/study-isobus/10-can-id-bitfields-light.png)
![29비트 CAN Identifier 비트 필드 배치](/images/study-isobus/10-can-id-bitfields-dark.png)

그림의 왼쪽이 최상위 비트(bit 28), 오른쪽이 최하위 비트(bit 0)다. 칸 아래 `[28:26]` 같은 숫자는 그 칸이 차지하는 비트 위치다. R은 예약 비트, DP는 데이터 페이지이고, PS 칸의 DA/GE는 PS가 받는 주소(DA)일 수도 있고 PGN을 넓히는 그룹 확장(GE)일 수도 있다는 뜻이다.

PF < 0xF0 이면 Peer-to-Peer(DA 있음), PF >= 0xF0 이면 Broadcast.

Peer-to-Peer는 받는 장치를 지정하는 1:1 메시지이고, Broadcast는 모두에게 보내는 방송이다. 아래 함수는 1.2절에서 손으로 한 일을 비트 연산으로 한다. `>>`는 비트를 오른쪽으로 미는 연산이고, `& 0xFF`는 아래 8비트만 남기는 연산(마스크)이다. 예를 들어 `(can_id >> 16) & 0xFF`는 ID를 16비트 오른쪽으로 민 다음 아래 8비트를 남겨 PF를 꺼낸다.

```python
def decode_can_id(can_id: int) -> dict:
    """
    Decode a 29-bit J1939/ISOBUS CAN ID into its components.
    Returns priority, pgn, da (if P2P), sa.
    """
    priority  = (can_id >> 26) & 0x7
    reserved  = (can_id >> 25) & 0x1
    data_page = (can_id >> 24) & 0x1
    pf        = (can_id >> 16) & 0xFF   # PDU Format
    ps        = (can_id >> 8)  & 0xFF   # PDU Specific
    sa        = can_id & 0xFF

    if pf >= 0xF0:
        # Broadcast: PS is part of PGN
        pgn = (data_page << 16) | (pf << 8) | ps
        da  = None
    else:
        # Peer-to-Peer: PS is Destination Address
        pgn = (data_page << 16) | (pf << 8)
        da  = ps

    return {
        "priority":  priority,
        "pgn":       pgn,
        "pgn_hex":   f"0x{pgn:04X}",
        "da":        f"0x{da:02X}" if da is not None else "Broadcast",
        "sa":        f"0x{sa:02X}",
    }
```

핵심은 `if pf >= 0xF0` 분기다. 방송이면 PS를 PGN의 아래 8비트로 넣고, 1:1 메시지면 PS를 받는 주소로 돌리고 PGN의 아래 8비트는 0으로 둔다. PGN 안에서 데이터 페이지는 PF 바로 위 비트(PGN의 bit 16)에 놓인다. 예약 비트(`reserved`)는 꺼내기만 하고 PGN에 넣지 않는다. ISO 11783 메시지는 이 비트를 언제나 0으로 보내므로 결과가 같다.

### 2.2 EEC1 (PGN 0xF004) SPN 디코딩: 엔진 RPM

EEC1은 엔진이 방송하는 상태 메시지이고, 그 안의 값 하나하나에 SPN(Suspect Parameter Number, 값의 번호)이 붙어 있다. 이 실습에서 꺼내는 값은 두 개다. 표를 읽을 때 주의할 점이 하나 있다. J1939 문서는 바이트를 1부터 세고 파이썬은 0부터 센다. 그래서 문서의 "바이트 4~5"는 코드에서 `data[3]`, `data[4]`다.

| 바이트(1부터) | 파이썬 인덱스 | SPN | 이름 | 분해능, 오프셋 |
|---|---|---|---|---|
| 2 | `data[1]` | 512 | Driver's Demand Engine - Percent Torque(운전자가 요구한 토크, %) | 1 %/bit, 오프셋 −125 % |
| 4~5 | `data[3]`, `data[4]` | 190 | Engine Speed(엔진 회전수) | 0.125 rpm/bit, 리틀 엔디언 |

분해능은 "원시값 1이 실제로 얼마인가", 오프셋은 "원시값 0이 실제로 얼마인가"다. 그래서 실제값 = 원시값 × 분해능 + 오프셋이다. 아래 코드에는 지상 속도 해석 함수와, 로그 여러 줄을 PGN에 따라 알맞은 함수로 보내는 `batch_decode`도 들어 있다.

```python
import struct

def decode_eec1(data: bytes) -> dict:
    """
    Decode PGN 0xF004 (Electronic Engine Controller 1), SAE J1939-71 definitions.
    SPN 190 = Engine Speed: bytes [3..4], resolution 0.125 rpm/bit.
    SPN 512 = Driver's Demand Engine - Percent Torque: byte [1], 1 %/bit, offset -125 %.
    """
    if len(data) < 8:
        raise ValueError("EEC1 requires 8 bytes")

    demand_raw = data[1]
    rpm_raw    = struct.unpack_from("<H", data, 3)[0]  # Little-endian uint16

    return {
        "engine_speed_rpm":         rpm_raw * 0.125,
        "driver_demand_torque_pct": demand_raw - 125,
    }


def decode_ground_speed(data: bytes) -> dict:
    """
    Decode TECU Ground-based Speed and Distance (PGN 0xFE49 / SPN 1859).
    Bytes [0..1]: speed in mm/s (1 bit = 1 mm/s), valid range 0..64255 (0xFAFF);
    0xFB00 and above are indicator values, not speeds (ISO 11783-7 3.3.3 Table 1).
    """
    if len(data) < 2:
        raise ValueError("Ground Speed requires at least 2 bytes")

    raw_speed = struct.unpack_from("<H", data, 0)[0]
    speed_mps = raw_speed / 1000.0  # Convert mm/s to m/s

    return {
        "speed_mm_s":   raw_speed,
        "speed_km_h":   round(speed_mps * 3.6, 2),
    }


def batch_decode(log_lines: list[str]) -> list[dict]:
    """
    Batch-decode a list of candump log lines (format: 'CANID#HEXDATA').
    Identifies PGN and dispatches to the appropriate decoder.
    """
    DECODERS = {
        0xF004: decode_eec1,
    }
    results = []
    for line in log_lines:
        line = line.strip()
        if not line or "#" not in line:
            continue
        id_str, data_str = line.split("#")
        can_id = int(id_str, 16)
        data   = bytes.fromhex(data_str)
        info   = decode_can_id(can_id)
        pgn    = info["pgn"]

        if pgn in DECODERS:
            decoded = DECODERS[pgn](data)
        else:
            decoded = {"raw": data_str}

        results.append({**info, **decoded, "raw_id": f"0x{can_id:08X}"})
    return results


# Example
if __name__ == "__main__":
    log = [
        "0CF00400#FF3C320000FFFF00",
        "0CFE49F0#014B00FA02000000",
        "0CF00400#FF8C4B0000FFFF00",
    ]
    for entry in batch_decode(log):
        print(entry)
```

`decode_ground_speed`의 설명에 있는 0xFAFF(=64255)는 속도로 쓸 수 있는 가장 큰 원시값이다. 0xFB00 이상은 "오류", "값 없음" 같은 상태를 알리는 특수값이라서 속도로 계산하면 안 된다. `DECODERS`는 PGN을 해석 함수에 이어 주는 표이고, 표에 없는 PGN은 원래 데이터를 `raw`로 그대로 돌려준다.

### 2.3 실행하고 결과 확인

1. 2.1절의 `decode_can_id`와 2.2절의 코드를 `decode_log.py` 한 파일에 이 순서로 붙여 넣는다.
2. 터미널에서 `python3 decode_log.py`를 실행한다.
3. 아래와 같은 세 줄이 나오면 성공이다.

실행 결과 예시:

```
{'priority': 3, 'pgn': 61444, 'pgn_hex': '0xF004', 'da': 'Broadcast',
 'sa': '0x00', 'engine_speed_rpm': 0.0, 'driver_demand_torque_pct': -65, 'raw_id': '0x0CF00400'}
{'priority': 3, 'pgn': 65097, 'pgn_hex': '0xFE49', 'da': 'Broadcast',
 'sa': '0xF0', 'raw': '014B00FA02000000', 'raw_id': '0x0CFE49F0'}
{'priority': 3, 'pgn': 61444, 'pgn_hex': '0xF004', 'da': 'Broadcast',
 'sa': '0x00', 'engine_speed_rpm': 0.0, 'driver_demand_torque_pct': 15, 'raw_id': '0x0CF00400'}
```

실제 출력은 한 항목이 한 줄로 나온다. 위에서는 읽기 쉽게 두 줄로 나눴다. 첫 줄을 항목별로 읽으면 다음과 같다.

- `priority: 3`: ID 첫 바이트 `0C`(2진수 `0000 1100`)에서 우선순위 3비트가 `011` = 3이다.
- `pgn: 61444`, `pgn_hex: '0xF004'`: EEC1이다. PF가 0xF0이라 PS `04`까지 PGN에 들어갔다.
- `da: 'Broadcast'`: PF가 0xF0 이상이라 받는 주소가 없다.
- `sa: '0x00'`: 엔진이 보냈다.
- `engine_speed_rpm: 0.0`: 바이트 4~5가 `00 00`이라 0 × 0.125 = 0 rpm이다.
- `driver_demand_torque_pct: -65`: 바이트 2가 `3C`(=60)라 60 − 125 = −65 %다.

둘째 줄은 PGN 0xFE49가 `DECODERS`에 없어서 원래 데이터가 `raw`로 나왔다. 셋째 줄은 같은 엔진의 다음 샘플이고, 바이트 2가 `8C`(=140)라 140 − 125 = 15 %다. 이 실습에서 해석하지 않은 나머지 바이트에 보이는 `FF`는 J1939에서 흔히 "값 없음(Not available)"을 뜻하는 표시다. 값을 모를 때 0을 보내면 진짜 0과 구별할 수 없으므로 모든 비트를 1로 채워 보낸다.

EEC1의 바이트 배치와 SPN 정의는 SAE J1939-71(엔진 같은 차량 부품의 메시지와 값을 정하는 J1939 문서) 기준이며, 이 스터디가 근거로 삼은 ISO 11783 문서 밖의 내용이다. Byte 2(코드의 `data[1]`)는 SPN 512 Driver's Demand Engine – Percent Torque로, 1 %/bit에 −125 % 오프셋을 둔다. 그래서 `0x3C`(60)는 −65 %, `0x8C`(140)는 15 %가 된다. 가속 페달 위치(SPN 91)는 EEC1이 아니라 EEC2(PGN 61443)에 있다.

::: tip 더 해 보기: 지상 속도도 디코딩하기
`DECODERS`에 `0xFE49: decode_ground_speed,` 한 줄을 더하고 다시 실행하면 둘째 줄의 `raw` 대신 `'speed_mm_s': 19201, 'speed_km_h': 69.12`가 나온다. 바이트 1~2 `01 4B`를 리틀 엔디언으로 읽으면 0x4B01 = 19201 mm/s = 19.201 m/s이고, 3.6을 곱하면 69.12 km/h다.
:::

<small>근거: ISO 11783-3 5.1.3, ISO 11783-7 B.2</small>

## 3. 실습 3: VT 오브젝트 풀 구성

::: info 실습 안내
- 목표: 메인 화면과 설정 화면 두 장짜리 VT 화면을 오브젝트 목록으로 설계하고, 오브젝트 사이의 참조가 빠짐없이 이어지는지 확인한다.
- 필요한 지식: [29장 VT 기초](/study/isobus/29-vt-basics), [32장 VT 오브젝트 풀 기초](/study/isobus/32-vt-object-pool-basics), [33장 오브젝트 레코드](/study/isobus/33-vt-object-records)
- 준비물: 화면을 스케치할 종이와 펜. 이 실습은 코드를 실행하지 않는다.
:::

한 줄 복습: VT 오브젝트 풀은 작업기 ECU가 VT(Virtual Terminal, 트랙터 운전석의 공용 화면)에 올려 보내는 "화면 부품 상자"다. 부품마다 오브젝트 ID라는 번호가 있고, 부품끼리는 이 ID로 서로를 가리킨다. 이 절에서는 작은 화면 두 장을 부품 목록으로 바꿔 본다.

### 3.1 화면 구성 개요

아래 VT 오브젝트 풀은 다음 두 화면으로 구성된다.

- **메인 화면**: 엔진 RPM, 차속, 작업 상태 표시
- **설정 화면**: 살포량 목표값 입력

### 3.2 오브젝트 정의 목록

표에 나오는 오브젝트 종류를 먼저 쉬운 말로 정리한다.

- Working Set: 풀 전체의 대표 오브젝트. 어느 화면을 먼저 보여 줄지(Active Mask) 정한다.
- Data Mask: 화면 한 장.
- Soft Key Mask: 화면 옆에 늘어서는 소프트키 묶음. Key는 그 안의 소프트키 하나다.
- Container: 여러 오브젝트를 한 덩어리로 묶는 상자. 한꺼번에 옮기거나 숨길 때 쓴다.
- Output Number, Output String: 숫자와 글자를 보여 주기만 하는 칸.
- Input Number: 운전자가 숫자를 입력하는 칸.

| Object ID | 유형 | 이름 | 속성 |
|-----------|------|------|------|
| 0x0001 | Working Set | Root WS | 메인 데이터 마스크 참조 |
| 0x0010 | Data Mask | Main Screen | 크기는 VT의 데이터 마스크 영역(정사각형), 배경색 흰색 |
| 0x0011 | Data Mask | Settings Screen | 크기는 VT의 데이터 마스크 영역(정사각형), 배경색 회색 |
| 0x0020 | Output Number | Engine RPM | 값 범위 0~4000, 단위 rpm |
| 0x0021 | Output Number | Ground Speed | 값 범위 0~50, 단위 km/h |
| 0x0022 | Output String | Work Status | "WORKING" / "STOPPED" |
| 0x0030 | Input Number | Target Rate | 입력 범위 0~600, 단위 L/ha |
| 0x0040 | Soft Key Mask | Main SKM | 소프트키 4개 배치 |
| 0x0041 | Key | Key: Settings | 설정 화면으로 전환 |
| 0x0042 | Key | Key: Work ON | 작업 시작 명령 |
| 0x0043 | Key | Key: Work OFF | 작업 중지 명령 |
| 0x0050 | Container | RPM Container | RPM 레이블 + 출력 오브젝트 묶음 |
| 0x0051 | Container | Speed Container | 속도 레이블 + 출력 오브젝트 묶음 |
| 0x0060 | Output String | RPM Label | "Engine RPM" 고정 텍스트 |
| 0x0061 | Output String | Speed Label | "Speed (km/h)" 고정 텍스트 |

::: warning 데이터 마스크 크기는 VT가 정한다
Data Mask 오브젝트에는 너비·높이 속성이 없다. 화면 크기는 VT가 정하고, 작업기 ECU는 Get Hardware 메시지로 물어서 안다. 데이터 마스크 영역은 표준이 정사각형으로 정해 두었다(VT 버전 6 이상은 최소 480×480 픽셀). 그래서 800×480 같은 직사각형 화면의 VT라도 데이터 마스크는 정사각형(예: 480×480)이고, 남는 부분은 소프트키나 제조사 정보 표시에 쓰인다.
:::

ID는 풀 안에서 겹치지만 않으면 된다. 이 예제는 읽기 쉽도록 종류별로 십의 자리를 맞췄다(0x001x는 마스크, 0x002x는 출력 칸). 3.4절 XML은 같은 ID를 10진수로 적으니 미리 바꿔 두자: 0x0001 = 1, 0x0010 = 16, 0x0011 = 17, 0x0020 = 32, 0x0022 = 34, 0x0030 = 48, 0x0040 = 64, 0x0050 = 80, 0x0051 = 81.

### 3.3 화면 레이아웃 다이어그램

![메인 화면 Data Mask 0x0010 안에 RPM Container 0x0050, Speed Container 0x0051, Work Status 0x0022가 있고 옆에 Soft Key Mask 0x0040의 Settings, Work ON, Work OFF 키가 있으며, Settings 키로 설정 화면 Data Mask 0x0011(Target Rate 입력 0x0030, Back 키)로 가고 Back 키로 돌아오는 화면 구성](/images/study-isobus/55-vt-screen-layout-light.png)
![메인 화면 Data Mask 0x0010 안에 RPM Container 0x0050, Speed Container 0x0051, Work Status 0x0022가 있고 옆에 Soft Key Mask 0x0040의 Settings, Work ON, Work OFF 키가 있으며, Settings 키로 설정 화면 Data Mask 0x0011(Target Rate 입력 0x0030, Back 키)로 가고 Back 키로 돌아오는 화면 구성](/images/study-isobus/55-vt-screen-layout-dark.png)

왼쪽이 메인 화면, 오른쪽이 설정 화면이다. 각 칸의 괄호 안 숫자가 오브젝트 ID이고, 1600 rpm과 8.5 km/h는 화면에 보일 값의 예다. 운전자가 Settings 키를 누르면 VT가 Soft Key Activation을 작업기 ECU에 보내고, ECU가 VT에 Change Active Mask 명령을 보내 설정 화면으로 바꾼다. Back 키도 같은 방식으로 메인 화면으로 돌아온다. 명령 바이트는 [36장](/study/isobus/36-vt-commands-basics)에서 다뤘다.

### 3.4 VT 오브젝트 풀 ISOXML 예시 (핵심 발췌)

::: warning 이 XML은 표준 형식이 아니다
VT 오브젝트 풀의 표준 전송 형식은 바이너리 레코드다. ISO 11783-6(VT를 정하는 표준 문서)에는 오브젝트 풀을 XML로 적는 형식이 없다. 아래 XML은 풀 편집 도구들이 사람이 읽기 쉽게 쓰는 표기의 한 예이고, 요소 이름과 속성 이름은 도구마다 다르다. 표준이 정한 XML은 56장의 태스크 파일 쪽이다.
:::

```xml
<!-- Working Set Object (ID=0x0001) -->
<WorkingSet ObjectID="1" BackgroundColour="1" Selectable="true"
            ActiveMask="16">
  <Include ObjectID="16"/>  <!-- Main Screen -->
  <Include ObjectID="17"/>  <!-- Settings Screen -->
</WorkingSet>

<!-- Main Screen Data Mask (ID=0x0010) -->
<DataMask ObjectID="16" BackgroundColour="1" SoftKeyMask="64">
  <Include ObjectID="80"/>  <!-- RPM Container -->
  <Include ObjectID="81"/>  <!-- Speed Container -->
  <Include ObjectID="34"/>  <!-- Work Status String -->
</DataMask>

<!-- Engine RPM Output Number (ID=0x0020) -->
<OutputNumber ObjectID="32" BackgroundColour="1"
              Value="0" Offset="0" Scale="1.0"
              NumberOfDecimals="0" Format="false"
              Justification="right" Width="120" Height="30"
              VariableReference="0">
</OutputNumber>

<!-- Target Rate Input Number (ID=0x0030) -->
<InputNumber ObjectID="48" BackgroundColour="1"
             Value="150" Offset="0" Scale="1.0"
             NumberOfDecimals="0" Format="false"
             Justification="right" Width="100" Height="30"
             MinValue="0" MaxValue="600"
             VariableReference="0">
</InputNumber>
```

요소별로 읽으면 다음과 같다.

- `WorkingSet`: `ActiveMask="16"`이 처음 보여 줄 화면, 곧 메인 화면(0x0010)이다. `Selectable="true"`는 운전자가 VT에서 이 작업기 화면을 고를 수 있다는 뜻이다.
- `DataMask ObjectID="16"`: `SoftKeyMask="64"`로 소프트키 마스크 0x0040을 함께 띄운다. 안의 `Include` 셋(80, 81, 34)은 이 화면에 그릴 자식 오브젝트다.
- `OutputNumber ObjectID="32"`: 엔진 회전수 칸이다. VT는 (Value + Offset) × Scale을 계산해 `NumberOfDecimals` 자리까지 보여 준다. `Format="false"`는 지수 표기가 아닌 보통 소수 표기, `Width`와 `Height`는 픽셀 단위 크기다.
- `InputNumber ObjectID="48"`: 목표 살포량 입력 칸이다. 시작값 150이고 `MinValue`~`MaxValue`(0~600) 밖의 값은 받지 않는다.

::: warning 표준 바이너리로 옮길 때 다른 두 곳
- <strong>Working Set의 자식 목록</strong>: 표준 바이너리에서 Working Set 오브젝트의 자식 목록에는 이 Working Set을 알아보게 하는 표지(소프트키 칸 크기의 그림이나 글자)가 들어간다. 데이터 마스크는 자식이 아니라 Active Mask 속성으로 가리킨다. 위 XML의 `WorkingSet` 안 `Include`는 "이 Working Set에 딸린 화면"을 보여 주는 도구 표기로 읽어야 한다.
- <strong>참조 없음의 표기</strong>: 표준 바이너리는 "가리키는 오브젝트 없음"을 NULL 오브젝트 ID 65535(0xFFFF)로 적는다. 이 풀에는 ID 0인 오브젝트가 없으므로 `VariableReference="0"`을 바이너리로 옮길 때 그대로 0을 쓰면 없는 오브젝트를 가리키게 된다. 65535로 바꿔야 한다.
:::

### 3.5 결과 확인

설계가 맞는지 다음 순서로 확인한다.

1. <strong>모든 참조가 목록에 있는가.</strong> `ActiveMask` 16, `SoftKeyMask` 64, `Include`의 16, 17, 80, 81, 34가 모두 3.2절 표에 있다. 하나라도 없으면 VT는 풀 전송이 끝날 때 "없는 오브젝트를 가리킨다(unknown object reference)"는 오류로 답한다.
2. <strong>계층이 이어지는가.</strong> Working Set(1) → Data Mask(16) → Container(80, 81) → 출력 칸(0x0060과 0x0020, 0x0061과 0x0021)으로 위에서 아래까지 한 줄로 이어진다.
3. <strong>빠진 오브젝트는 없는가.</strong> Soft Key Mask 0x0040은 "소프트키 4개 배치"인데 Key는 0x0041~0x0043 세 개뿐이다. 또 그림의 설정 화면에 있는 Back 키는 표에 없다. 설정 화면용 Soft Key Mask와 Back 키를 새 ID로 더해 표를 완성해 보자. 예시 답: Soft Key Mask 0x0044(Settings SKM)와 Key 0x0045(Key: Back)를 추가하고, Data Mask 0x0011이 `SoftKeyMask="68"`(0x0044)로 그 마스크를 가리키게 한다.

<small>근거: ISO 11783-6 4.5.2, B.1, B.2</small>

## 4. 실습 4: TC 가변 살포 시나리오

::: info 실습 안내
- 목표: 처방 맵으로 살포량을 바꾸는 작업의 네 단계를 설명하고, 위치마다 목표 살포량을 고르는 시뮬레이터를 실행해 결과를 읽는다.
- 필요한 지식: [41장 TC 기초](/study/isobus/41-tc-basics), [42장 태스크와 시간 기록](/study/isobus/42-tc-task), [45장 TC 프로세스 데이터 기초](/study/isobus/45-tc-process-data-basics), [51장 File Server 기초](/study/isobus/51-file-server-basics)
- 준비물: 파이썬 3.10 이상, 4.2절 코드를 저장할 파일(`vra_sim.py`)
:::

한 줄 복습: TC(Task Controller)는 트랙터 쪽에서 작업(태스크)을 관리하는 장치다. 작업기에 목표값을 보내고, 실제로 한 일을 기록한다. 이 절은 가변 살포(VRA, Variable Rate Application)를 예로 그 흐름 전체를 따라간다.

### 4.1 처방 맵 기반 가변 살포 시나리오 전체 흐름

아래는 시퀀스 다이어그램이다. 세로선 하나가 참여자 하나이고, 위에서 아래로 시간이 흐른다. 실선 화살표는 요청이나 데이터, 점선 화살표는 응답이다.

![FMIS, File Server, Task Controller, GPS 수신기, Section Control, As-Applied 로그 여섯 참여자가 작업 준비(처방 맵 업로드와 다운로드), 작업 시작, 1초 간격 실시간 살포 반복, 작업 종료와 로그 회수의 네 단계로 메시지를 주고받는 시퀀스](/images/study-isobus/55-tc-vra-sequence-light.png)
![FMIS, File Server, Task Controller, GPS 수신기, Section Control, As-Applied 로그 여섯 참여자가 작업 준비(처방 맵 업로드와 다운로드), 작업 시작, 1초 간격 실시간 살포 반복, 작업 종료와 로그 회수의 네 단계로 메시지를 주고받는 시퀀스](/images/study-isobus/55-tc-vra-sequence-dark.png)

네 단계를 말로 풀면 다음과 같다.

1. <strong>작업 준비</strong>: FMIS(농장 관리 소프트웨어)가 처방 맵 파일을 File Server에 올린다. TC는 그 파일을 내려받아 격자 칸마다 목표값을 읽어 둔다.
2. <strong>작업 시작</strong>: FMIS가 태스크 시작을 지시하고 TC가 확인한다.
3. <strong>실시간 살포</strong>: 1초마다 GPS 수신기가 현재 위치(NMEA 2000 GNSS Position Data, PGN 129029)를 보낸다. TC는 그 위치가 속한 칸의 목표 살포량을 찾아 작업기(Section Control)에 섹션 켜기·끄기와 목표 살포량을 보내고, 작업기의 실제 살포량을 받아 As-Applied 기록으로 남긴다.
4. <strong>작업 종료와 데이터 회수</strong>: 태스크를 멈추고, TC가 기록 파일을 File Server에 올리면 FMIS가 내려받아 실제 살포 지도(As-Applied Map)를 만든다.

::: warning 그림에서 단순화한 곳
- `prescription_map.xml`, `task_log_20260413.xml`은 설명용 이름이다. 실제 파일 이름 규칙은 [56장](/study/isobus/56-practice-isoxml)에서 다룬다.
- "Task Start 명령"과 "Task Stop 명령"에 해당하는 버스 메시지는 표준에 없다. 태스크를 고르고 시작·정지하는 방법은 TC를 만드는 쪽이 정한다. 버스에 드러나는 것은 TC가 Task Controller Status 메시지의 Byte 5 bit 1(task totals active)로 태스크 시작·재개를 알리는 것이다([42장](/study/isobus/42-tc-task)).
- "Section Control 명령"과 "Rate Control 명령"은 실제 버스에서는 TC가 보내는 프로세스 데이터 값 명령이다([45장](/study/isobus/45-tc-process-data-basics)).
:::

### 4.2 처방 맵 격자 조회 Python 시뮬레이션

아래 코드는 위 그림의 3단계(실시간 살포 반복)만 흉내 낸다. 구성은 네 부분이다.

- `GridCell`: 처방 맵의 칸 하나. 위도·경도 범위와 목표 살포량(L/ha)을 담는다.
- `AsAppliedRecord`: 기록 한 줄. 시각, 위치, 목표값, 실제값, 섹션 상태를 담는다.
- `PrescriptionMap`: 칸 목록을 들고, 위치를 받으면 그 위치가 들어 있는 칸의 목표값을 돌려준다. 어느 칸에도 없으면 `None`이다.
- `TaskControllerSimulator`: 위치 하나를 받을 때마다 목표값 찾기, 섹션 명령 정하기, 기록 남기기를 차례로 한다.

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class GridCell:
    """Single cell in a prescription map grid."""
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float
    target_rate_lha: float  # Target application rate (L/ha)


@dataclass
class AsAppliedRecord:
    """Single as-applied log record."""
    timestamp: str
    lat: float
    lon: float
    target_rate: float
    actual_rate: float
    sections_active: list[int]


class PrescriptionMap:
    """
    Simple prescription map with GPS-based cell lookup.
    In production, this would be loaded from an ISOXML TaskData file.
    """

    def __init__(self, cells: list[GridCell]):
        self.cells = cells

    def lookup(self, lat: float, lon: float) -> float | None:
        """Return target rate for the given GPS position, or None if outside map."""
        for cell in self.cells:
            if (cell.lat_min <= lat <= cell.lat_max and
                    cell.lon_min <= lon <= cell.lon_max):
                return cell.target_rate_lha
        return None


class TaskControllerSimulator:
    """
    Simulate TC variable-rate application based on a prescription map.
    Demonstrates Phase 3 of the scenario (real-time application loop).
    """

    def __init__(self, presc_map: PrescriptionMap, num_sections: int = 4):
        self.presc_map  = presc_map
        self.num_sections = num_sections
        self.log: list[AsAppliedRecord] = []

    def _determine_sections(self, target_rate: float) -> list[int]:
        """Simple rule: disable all sections if rate == 0."""
        if target_rate == 0:
            return [0] * self.num_sections
        return [1] * self.num_sections

    def process_position(self, lat: float, lon: float,
                         actual_rate: float) -> dict:
        """
        Process a GPS position update:
        1. Look up prescription map
        2. Determine section commands
        3. Log the record
        """
        target = self.presc_map.lookup(lat, lon)
        if target is None:
            target = 0.0  # Outside map: stop application

        sections = self._determine_sections(target)
        record = AsAppliedRecord(
            timestamp       = datetime.utcnow().isoformat(),
            lat             = lat,
            lon             = lon,
            target_rate     = target,
            actual_rate     = actual_rate,
            sections_active = sections,
        )
        self.log.append(record)

        return {
            "target_rate_lha": target,
            "section_cmd":     sections,
            "log_count":       len(self.log),
        }

    def export_log(self) -> list[dict]:
        return [vars(r) for r in self.log]


# --- Simulation entry point ---
if __name__ == "__main__":
    # Define a simple 2x2 prescription map grid
    cells = [
        GridCell(37.500, 37.501, 127.000, 127.001, target_rate_lha=150.0),
        GridCell(37.500, 37.501, 127.001, 127.002, target_rate_lha=200.0),
        GridCell(37.501, 37.502, 127.000, 127.001, target_rate_lha=100.0),
        GridCell(37.501, 37.502, 127.001, 127.002, target_rate_lha=180.0),
    ]
    presc_map = PrescriptionMap(cells)
    tc_sim    = TaskControllerSimulator(presc_map, num_sections=4)

    # Simulate 5 GPS position updates (tractor moving across field)
    gps_trace = [
        (37.5005, 127.0005),
        (37.5005, 127.0015),
        (37.5015, 127.0005),
        (37.5015, 127.0015),
        (37.5025, 127.0025),  # Outside map
    ]

    print("=== TC Variable-Rate Simulation ===")
    for lat, lon in gps_trace:
        result = tc_sim.process_position(lat, lon, actual_rate=148.0)
        print(f"GPS({lat:.4f},{lon:.4f}) → "
              f"Target={result['target_rate_lha']:6.1f} L/ha  "
              f"Sections={result['section_cmd']}")

    print(f"\nTotal as-applied records: {len(tc_sim.log)}")
```

`cells`는 위도 37.500~37.502, 경도 127.000~127.002를 0.001도씩 나눈 2×2 격자다. 남쪽 줄 두 칸이 150과 200, 북쪽 줄 두 칸이 100과 180이다. `gps_trace`는 트랙터가 지나간 위치 다섯 개이고, 마지막 위치는 일부러 지도 밖에 두었다. 실제 살포량은 작업기 피드백 대신 모든 위치에서 148.0으로 고정했다.

### 4.3 실행하고 결과 확인

1. 위 코드를 `vra_sim.py`로 저장한다.
2. `python3 vra_sim.py`를 실행한다.
3. 아래 결과가 나오면 성공이다.

실행 결과:

```
=== TC Variable-Rate Simulation ===
GPS(37.5005,127.0005) → Target= 150.0 L/ha  Sections=[1, 1, 1, 1]
GPS(37.5005,127.0015) → Target= 200.0 L/ha  Sections=[1, 1, 1, 1]
GPS(37.5015,127.0005) → Target= 100.0 L/ha  Sections=[1, 1, 1, 1]
GPS(37.5015,127.0015) → Target= 180.0 L/ha  Sections=[1, 1, 1, 1]
GPS(37.5025,127.0025) → Target=   0.0 L/ha  Sections=[0, 0, 0, 0]

Total as-applied records: 5
```

결과는 이렇게 읽는다.

- 처음 네 위치는 각각 남서, 남동, 북서, 북동 칸 안에 있어서 그 칸의 목표값(150, 200, 100, 180)이 나왔고 섹션 네 개가 모두 켜졌다.
- 다섯째 위치는 위도 37.5025가 격자의 북쪽 끝 37.502보다 크다. 어느 칸에도 없으니 목표값이 0이 되고 섹션이 모두 꺼졌다.
- 기록은 위치마다 하나씩 다섯 개가 쌓였다.

파이썬 3.12 이상에서는 결과 위에 `datetime.utcnow()`가 앞으로 없어질 함수라는 `DeprecationWarning`이 한 번 함께 찍힌다. 경고일 뿐 결과에는 영향이 없다.

::: tip 더 해 보기: 칸 경계 위의 점
`gps_trace`에 네 칸이 만나는 점 `(37.501, 127.001)`을 넣어 보자. `lookup`은 범위 양 끝을 모두 포함(`<=`)하고 목록을 앞에서부터 찾으므로, 첫 칸의 150이 나온다. 경계 위의 점을 어느 칸에 넣을지는 구현마다 다를 수 있다. [57장](/study/isobus/57-practice-binary-files)의 grid 파일 방식은 이 점을 다르게 처리한다.
:::

<small>근거: ISO 11783-10 6.1, B.8.1</small>

::: tip 핵심 정리
- CAN ID 29비트에서 Priority / PGN / DA / SA를 분리하면 모든 ISOBUS 메시지를 분류할 수 있다.
- PF가 0xF0보다 작으면 PS가 받는 주소이고, 0xF0 이상이면 PS가 PGN의 일부인 방송 메시지다.
- EEC1(0xF004) SPN 190은 0.125 rpm/bit 해상도로 엔진 RPM을 인코딩한다.
- VT 오브젝트 풀은 Working Set → Data Mask → Container → Output/Input 계층으로 구성된다.
- TC 시나리오는 처방 맵 로드 → GPS 위치 수신 → 셀 조회 → 명령 전송 → As-Applied 로그 순서로 동작한다.
:::

::: details 확인 문제
1. (개념) 로그 한 줄 `18EA2681#C5FD00`에서 보낸 주소, 받는 주소, 요청한 PGN을 말하라.
2. (개념) PF가 0xF0 이상인 메시지에는 왜 받는 주소가 없나?
3. (계산) EEC1 데이터가 `FF 7D 7D 40 1F FF FF FF`라면 엔진 회전수와 운전자 요구 토크는 얼마인가?
4. (설계) 3절 풀에서 운전자가 Settings 키를 눌렀을 때 설정 화면이 보이게 하려면, 작업기 ECU는 Working Set의 어느 속성을 어떤 값으로 바꿔야 하나?
5. (시뮬레이션) 4.2절 시뮬레이터에 위치 `(37.5012, 127.0018)`을 넣으면 목표 살포량은 얼마이고 섹션은 어떻게 되나?
6. (디버깅) 동료가 짠 `decode_can_id`가 아래와 같다. 2.1절 함수와 한 줄만 다르다. NMEA 2000 위치 메시지(PGN 129029 = 0x1F805)의 CAN ID `0DF8051C`를 넣었더니 PGN이 194565(0x2F805)로 나왔다. 어디가 틀렸고 어떻게 고치나?

```python
def decode_can_id(can_id: int) -> dict:
    """
    Decode a 29-bit J1939/ISOBUS CAN ID into its components.
    Returns priority, pgn, da (if P2P), sa.
    """
    priority  = (can_id >> 26) & 0x7
    reserved  = (can_id >> 25) & 0x1
    data_page = (can_id >> 24) & 0x1
    pf        = (can_id >> 16) & 0xFF   # PDU Format
    ps        = (can_id >> 8)  & 0xFF   # PDU Specific
    sa        = can_id & 0xFF

    if pf >= 0xF0:
        # Broadcast: PS is part of PGN
        pgn = (data_page << 17) | (pf << 8) | ps
        da  = None
    else:
        # Peer-to-Peer: PS is Destination Address
        pgn = (data_page << 17) | (pf << 8)
        da  = ps

    return {
        "priority":  priority,
        "pgn":       pgn,
        "pgn_hex":   f"0x{pgn:04X}",
        "da":        f"0x{da:02X}" if da is not None else "Broadcast",
        "sa":        f"0x{sa:02X}",
    }
```

**답 가이드**
1. ID `18EA2681`에서 SA = 0x81, PF = 0xEA(0xF0보다 작음)이므로 DA = 0x26(VT)이다. 데이터 `C5 FD 00`을 거꾸로 읽으면 0xFDC5(=64965), ECU identification을 요청했다. 우선순위는 6이다.
2. PF가 0xF0 이상이면 PS 8비트가 PGN의 일부(그룹 확장)로 쓰여서 받는 주소를 담을 자리가 남지 않는다. 그래서 이런 메시지는 언제나 모두에게 가는 방송이다.
3. 바이트 2 `7D`(=125)이므로 125 − 125 = 0 %다. 바이트 4~5 `40 1F`를 리틀 엔디언으로 읽으면 0x1F40 = 8000이고, 8000 × 0.125 = 1000 rpm이다.
4. Active Mask 속성을 설정 화면 Data Mask의 ID 17(0x0011)로 바꾼다. 실제로는 Change Active Mask 명령을 VT에 보낸다.
5. 위도 37.5012는 37.501~37.502, 경도 127.0018은 127.001~127.002 범위라 북동 칸이다. 목표 살포량은 180.0 L/ha이고 섹션은 `[1, 1, 1, 1]`로 모두 켜진다.
6. 데이터 페이지를 17비트 밀어 넣은 `(data_page << 17)` 두 줄이 틀렸다. PGN은 위에서부터 0 여섯 비트, 예약 비트, 데이터 페이지, PF 8비트, PS 8비트로 이루어지므로 데이터 페이지는 bit 16에 놓여야 한다. `(data_page << 16)`으로 고치면 0DF8051C에서 데이터 페이지 1, PF 0xF8, PS 0x05가 0x1F805 = 129029로 맞게 나온다. 데이터 페이지가 0인 메시지(이 장의 로그 전부)에서는 두 코드의 결과가 같아서 버그가 숨어 있었다.
:::

## 다음 챕터

- 다음: [56장 종합 실습 (2): ISOXML 태스크 파일](/study/isobus/56-practice-isoxml)
