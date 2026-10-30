---
title: "CAN 데이터 프레임"
description: "CAN 통신에서 데이터를 담는 그릇, 프레임의 구조와 각 필드의 역할을 이해한다"
date: 2026-04-13
tags:
  - isobus
  - can
  - data-frame
---

<Header/>

[[toc]]

# CAN 데이터 프레임

::: info 학습 목표
- CAN 버스에서 사용하는 4가지 프레임 종류를 구분할 수 있다
- 데이터 프레임의 각 필드(SOF, ID, DLC, Data, CRC 등)의 역할을 설명할 수 있다
- Standard(11bit)와 Extended(29bit) ID의 차이를 이해한다
- 비트 스터핑의 목적과 동작 방식을 설명할 수 있다
- 실제 CAN 로그를 보고 ID, DLC, Data를 직접 파싱할 수 있다
- ISO 11783 29비트 ID의 각 필드가 CEFF 프레임 비트 1~39 중 어디에 놓이는지 짚고, PF가 SRR·IDE로 갈라지는 지점을 찾을 수 있다
- PG 정의 길이와 multi-packet 여부로 DLC와 채움 바이트를 결정할 수 있다
:::

## 1. 프레임의 종류

CAN 버스 위를 오가는 메시지는 목적에 따라 4가지 종류로 나뉜다.

| 프레임 종류 | 역할 |
|---|---|
| **데이터 프레임 (Data Frame)** | 실제 데이터를 전송하는 가장 일반적인 프레임 |
| **리모트 프레임 (Remote Frame)** | 다른 노드에게 특정 데이터를 보내달라고 요청하는 프레임 |
| **에러 프레임 (Error Frame)** | 오류를 감지한 노드가 버스 전체에 오류를 알리는 프레임 |
| **오버로드 프레임 (Overload Frame)** | 노드가 처리 준비가 안 됐을 때 다음 전송을 잠시 지연시키는 프레임 |

**비유로 이해하기**

CAN 버스를 무전기 채널이라고 생각해보자.
- **데이터 프레임**: "본부, 현재 위치 좌표는 37.5°N, 127.0°E이다." — 실제 정보 전달
- **리모트 프레임**: "본부, 현재 온도 데이터 좀 보내달라." — 데이터 요청
- **에러 프레임**: "잠깐! 방금 전송에 오류가 있었다!" — 오류 신호
- **오버로드 프레임**: "지금 처리 중이다, 잠깐만." — 전송 지연 요청

## 2. 데이터 프레임 필드 해부

데이터 프레임은 여러 필드로 구성되며, 각각 정해진 역할이 있다.

![CAN Standard Data Frame(2.0A) 필드 배치: SOF, Identifier 11bit, RTR, IDE, r0, DLC 4bit, Data 0~64bit, CRC 15bit, CRC Del, ACK Slot, ACK Del, EOF 7bit](/images/study-isobus/04-std-frame-light.png)
![CAN Standard Data Frame(2.0A) 필드 배치: SOF, Identifier 11bit, RTR, IDE, r0, DLC 4bit, Data 0~64bit, CRC 15bit, CRC Del, ACK Slot, ACK Del, EOF 7bit](/images/study-isobus/04-std-frame-dark.png)

각 필드를 순서대로 살펴보자.

| 필드 | 크기 | 역할 |
|---|---|---|
| **SOF** (Start of Frame) | 1 bit | 프레임 시작을 알리는 Dominant(0) 비트 |
| **Identifier** | 11 bit | 메시지 식별자 겸 우선순위. 값이 낮을수록 높은 우선순위 |
| **RTR** (Remote Transmission Request) | 1 bit | 0=데이터 프레임, 1=리모트 프레임 구분 |
| **IDE** (Identifier Extension) | 1 bit | 0=Standard(11bit), 1=Extended(29bit) 구분 |
| **r0** (Reserved) | 1 bit | 예약된 비트, 항상 Dominant(0) |
| **DLC** (Data Length Code) | 4 bit | 데이터 필드의 바이트 수 (0~8) |
| **Data** | 0~64 bit | 실제 전송 데이터 (0~8바이트) |
| **CRC** (Cyclic Redundancy Check) | 15 bit | 전송 오류 검출을 위한 체크섬 |
| **ACK** | 2 bit | 수신 노드의 정상 수신 확인 (ACK Slot + ACK Delimiter) |
| **EOF** (End of Frame) | 7 bit | 프레임 종료를 알리는 7개의 Recessive(1) 비트 |

::: tip Dominant vs Recessive
CAN 버스에서 0을 Dominant, 1을 Recessive라 부른다. 여러 노드가 동시에 신호를 내보낼 때 Dominant(0)가 항상 이긴다. 전선을 당기는(0) 쪽이 안 당기는(1) 쪽을 이기는 것과 같다.
:::

## 3. Standard(11bit) vs Extended(29bit)

CAN 2.0A는 11bit Identifier를, CAN 2.0B는 29bit Identifier를 사용한다. ISOBUS(ISO 11783)는 29bit Extended ID를 기반으로 한다.

![CAN Extended Data Frame(2.0B, 29bit ID) 필드 배치: SOF, Base ID 11bit, SRR, IDE=1, Extended ID 18bit, RTR, r1, r0, DLC 4bit, Data 0~64bit, CRC 15bit, CRC Del, ACK Slot, ACK Del, EOF 7bit](/images/study-isobus/04-ext-frame-light.png)
![CAN Extended Data Frame(2.0B, 29bit ID) 필드 배치: SOF, Base ID 11bit, SRR, IDE=1, Extended ID 18bit, RTR, r1, r0, DLC 4bit, Data 0~64bit, CRC 15bit, CRC Del, ACK Slot, ACK Del, EOF 7bit](/images/study-isobus/04-ext-frame-dark.png)

**Standard와 Extended의 차이**

| 항목 | Standard (2.0A) | Extended (2.0B) |
|---|---|---|
| Identifier 크기 | 11 bit | 29 bit (11 + 18) |
| 메시지 가짓수 | 2¹¹ = 2,048개 | 2²⁹ = 536,870,912개 |
| IDE 비트 | 0 | 1 |
| 추가 필드 | 없음 | SRR (Substitute Remote Request) |
| 주요 용도 | 일반 CAN | ISOBUS, CANopen 등 |

Extended 프레임에서 추가된 필드:
- **SRR** (Substitute Remote Request): Standard 프레임의 RTR 위치에 들어가는 Recessive 비트. Extended 프레임에서 항상 1
- **18bit Extension**: Base ID(11bit) 뒤에 붙는 추가 18bit로 총 29bit ID를 구성

프레임의 구조를 알았으니, 이 프레임이 버스 위를 실제로 이동할 때 적용되는 중요한 전송 규칙을 하나 살펴보자.

## 4. 비트 스터핑(Bit Stuffing)

**왜 필요한가?**

CAN은 클럭 신호 없이 데이터 신호만으로 통신한다. 수신 노드는 신호의 변화(0→1 또는 1→0)를 감지해 동기화를 유지한다. 그런데 같은 값이 너무 오래 연속되면 동기화 기준점을 잃어버릴 수 있다.

**동작 방식**

같은 값의 비트가 <strong>5개 연속</strong> 나타나면, 다음에 반드시 <strong>반대 값의 비트를 1개 삽입</strong>한다. 이 삽입된 비트를 <strong>Stuff Bit</strong>이라 한다.

```
원본 비트열: 1 1 1 1 1 0 0 0 0 0 1
                              ↑
                   5개 연속 1 뒤에 0 삽입됨

스터핑 후:  1 1 1 1 1 [0] 0 0 0 0 0 [1] 1
                       ↑             ↑
                   Stuff Bit      Stuff Bit
```

**수신측 처리**: 수신 노드는 5개 연속 비트 뒤에 오는 비트를 자동으로 제거(Destuffing)하여 원래 데이터를 복원한다.

::: tip 비트 스터핑 적용 범위
비트 스터핑은 SOF부터 CRC 필드까지 적용된다. EOF와 ACK 필드에는 적용되지 않는다.
:::

## 5. DLC와 데이터 길이

DLC(Data Length Code)는 4비트 필드로, 데이터 필드에 실제로 몇 바이트의 데이터가 있는지 알려준다.

| DLC 값 (10진수) | 데이터 바이트 수 |
|---|---|
| 0 | 0 바이트 |
| 1 | 1 바이트 |
| 2 | 2 바이트 |
| 3 | 3 바이트 |
| 4 | 4 바이트 |
| 5 | 5 바이트 |
| 6 | 6 바이트 |
| 7 | 7 바이트 |
| 8 | 8 바이트 |
| 9~15 | 8 바이트 (표준 CAN에서는 8을 초과하지 않음) |

::: info CAN FD의 DLC 확장
CAN FD(Flexible Data Rate)에서는 DLC 9~15가 12, 16, 20, 24, 32, 48, 64 바이트에 매핑되어 최대 64바이트 전송이 가능하다. 그러나 일반 CAN과 ISOBUS에서는 최대 8바이트다.
:::

이제 프레임의 모든 구성 요소를 알았다. 실제 CAN 로그를 보면서 직접 파싱해보자.

## 6. 비트열을 직접 잘라 읽기

앞 절들이 필드의 정의를 다뤘다면, 여기서는 <strong>버스에 실제로 흐르는 비트열 하나를 끝까지 분해</strong>한다. CAN에는 "여기부터 프레임이고 길이는 얼마"라고 알려주는 헤더가 없다. 그래서 어디서 끊을지를 스스로 판단해야 한다.

다음이 버스에서 관측한 비트열이다.

```
00010010001100000110101010111100110111110111001111001011111111
```

### 1단계 — 시작점 찾기

버스가 유휴할 때는 recessive(1)가 계속 흐른다. 그 상태에서 처음 나타나는 <strong>dominant(0)</strong>가 SOF이며, 거기서부터 프레임이 시작된다. 위 비트열의 첫 `0`이 그 지점이다.

### 2단계 — 스터핑 비트 제거

필드를 세기 전에 반드시 해야 하는 일이다. 송신 측은 같은 비트가 5개 연속되면 반대 비트를 강제로 끼워 넣는다([§4 비트 스터핑](#_4-비트-스터핑-bit-stuffing)). 이 비트는 데이터가 아니므로, 세기 시작하기 전에 빼내야 필드 경계가 맞는다.

이 프레임에는 스터핑 비트가 2개 들어 있어 62비트로 수신되지만 실제 내용은 60비트다.

![수신한 62비트에서 스터핑 비트 2개를 제거하고 60비트를 필드별로 자른 결과](/images/study-isobus/04-frame-decode-light.png)
![수신한 62비트에서 스터핑 비트 2개를 제거하고 60비트를 필드별로 자른 결과](/images/study-isobus/04-frame-decode-dark.png)

### 3단계 — 고정 순서로 세어 나가기

스터핑을 걷어내면 필드 순서가 정해져 있으므로 앞에서부터 정해진 개수만큼 끊으면 된다.

| 필드 | 비트 | 값 | 해석 |
|------|------|-----|------|
| SOF | 1 | `0` | 프레임 시작 |
| Identifier | 11 | `00100100011` | ID = <strong>0x123</strong> |
| RTR | 1 | `0` | 데이터 프레임 |
| IDE | 1 | `0` | 표준 11비트 ID |
| r0 | 1 | `0` | 예약 |
| DLC | 4 | `0010` | 데이터 <strong>2바이트</strong> |
| Data | 16 | `10101011 11001101` | <strong>0xAB 0xCD</strong> |
| CRC | 15 | `111111100111100` | 0x7F3C |
| CRC 구분자 | 1 | `1` | recessive 고정 |
| ACK 슬롯 | 1 | `0` | 수신 노드가 dominant로 덮어썼다 |
| ACK 구분자 | 1 | `1` | recessive 고정 |
| EOF | 7 | `1111111` | 프레임 끝 |

여기서 중요한 것은 <strong>DLC를 읽기 전에는 프레임의 전체 길이를 알 수 없다</strong>는 점이다. DLC가 2라는 걸 확인해야 "데이터는 16비트이고 그다음 15비트가 CRC"라는 경계가 정해진다. DLC가 8이었다면 데이터는 64비트가 되고 CRC 시작 위치도 그만큼 밀린다.

### 4단계 — CRC 검증

SOF부터 데이터 끝까지의 비트열(스터핑 제거 후)을 CRC-15 다항식으로 나눈 나머지가 CRC 필드와 같아야 한다.

```
x^15 + x^14 + x^10 + x^8 + x^7 + x^4 + x^3 + 1     (0x4599)
```

:::details 파이썬으로 검산해 보기
```python
def crc15(bits):
    crc = 0
    for b in bits:
        nxt = ((crc >> 14) & 1) ^ b
        crc = (crc << 1) & 0x7FFF
        if nxt:
            crc ^= 0x4599          # x^15+x^14+x^10+x^8+x^7+x^4+x^3+1
    return crc


def tobits(v, n):
    return [(v >> i) & 1 for i in range(n - 1, -1, -1)]


ID, DLC, DATA = 0x123, 2, [0xAB, 0xCD]

frame  = [0]                    # SOF
frame += tobits(ID, 11)         # Identifier
frame += [0, 0, 0]              # RTR, IDE, r0
frame += tobits(DLC, 4)         # DLC
for d in DATA:
    frame += tobits(d, 8)       # Data

print(hex(crc15(frame)))        # 0x7f3c
```
:::

### 실제로는 하드웨어가 여기까지 처리한다

지금까지의 과정은 <strong>CAN 컨트롤러 칩이 자동으로</strong> 수행한다. 비트 동기화, 스터핑 제거, 필드 분해, CRC 검증, ACK 응답이 전부 하드웨어 단에서 끝난다. 그래서 소프트웨어가 받아 보는 것은 검증을 통과한 ID·DLC·Data뿐이며, 다음 절에서 다루는 로그 형식이 바로 그 결과물이다.

## 7. CAN 로그 읽기 실습

실제 CAN 로그에서 자주 보이는 형식을 파싱해보자.

**로그 예시**

```
0CF004FE#FF3C320000FFFF00
```

이 형식은 `[CAN ID]#[Data]` 구조다.

### CRC, ACK, EOF는 어디에?

프레임 구조에는 SOF, CRC, ACK, EOF 등이 있는데 로그에는 ID와 Data만 보인다. 이유는 <strong>하드웨어(CAN 컨트롤러)가 자동으로 처리하는 영역</strong>과 <strong>소프트웨어가 다루는 영역</strong>이 나뉘기 때문이다.

| 필드 | 누가 처리 | 소프트웨어에서 보이는가 |
|------|-----------|----------------------|
| **ID** | 소프트웨어 | 보인다 |
| **DLC** | 소프트웨어 | 보인다 (Data 길이로 유추) |
| **Data** | 소프트웨어 | 보인다 |
| SOF | CAN 컨트롤러 자동 생성 | 안 보인다 |
| CRC | CAN 컨트롤러가 자동 생성/검증 | 안 보인다 |
| ACK | CAN 컨트롤러가 자동 응답 | 안 보인다 |
| EOF | CAN 컨트롤러가 자동 추가 | 안 보인다 |

CAN 컨트롤러 칩이 프레임을 보낼 때 CRC를 자동 계산해서 붙이고, 받을 때 자동 검증한다. CRC가 틀리면 에러 프레임을 전송하고, 맞으면 ACK를 보낸다. 이 과정이 전부 하드웨어에서 끝나기 때문에, 소프트웨어에는 <strong>검증을 통과한 ID + DLC + Data만 올라온다.</strong>

```
0CF004FE#FF3C320000FFFF00
^^^^^^^^ ^^^^^^^^^^^^^^^^
  ID만     Data만
```

CRC가 틀린 프레임은 애초에 소프트웨어까지 도달하지 않는다. 하드웨어 단에서 폐기된다.

**파싱 과정**

```
원본: 0CF004FE#FF3C320000FFFF00
       ↓
CAN ID: 0CF004FE (16진수 8자리 = 29bit Extended ID)
Data  : FF 3C 32 00 00 FF FF 00
```

**CAN ID 분해 (ISOBUS PGN 구조)**

0x0CF004FE를 32bit 이진수로 펼치면 `0000 1100 1111 0000 0000 0100 1111 1110`이다. 상위 3bit는 29bit ID를 32bit 16진수로 표기하면서 생기는 미사용 패딩이고, 그다음부터 Priority·EDP·DP·PF·PS·SA가 이어진다.

![CAN ID 0x0CF004FE를 4바이트로 나눠 Priority·EDP·DP·PF·PS·SA 비트로 분해한 결과, PF와 PS를 합치면 PGN 0xF004(61444, EEC1)](/images/study-isobus/04-can-id-decode-light.png)
![CAN ID 0x0CF004FE를 4바이트로 나눠 Priority·EDP·DP·PF·PS·SA 비트로 분해한 결과, PF와 PS를 합치면 PGN 0xF004(61444, EEC1)](/images/study-isobus/04-can-id-decode-dark.png)

| 필드 | 값 | 해석 |
|---|---|---|
| Priority | `011` (3bit) | 우선순위 3 |
| EDP (Reserved) | `0` (1bit) | — |
| DP (Data Page) | `0` (1bit) | — |
| PF | `0xF0` | PGN 상위 바이트 |
| PS | `0x04` | PGN 하위 바이트 → PGN = 0xF004 = 61444 (EEC1, 엔진 속도) |
| SA | `0xFE` | 소스 주소 254 |

::: tip 검산
`0x0C` = `0000 1100`인데 이 안에 패딩(3bit)·Priority(3bit)·EDP(1bit)·DP(1bit)가 모두 들어 있다. `000`(패딩) + `011`(Priority=3) + `0`(EDP) + `0`(DP) = `00001100` = `0x0C`로 정확히 맞아떨어진다.
:::

**Data 필드 해석**

DLC = 8이므로 Data는 8바이트다. PGN F004(EEC1) 기준으로 각 바이트를 해석하면 다음과 같다.

| 바이트 | 값 | 필드 | 해석 |
|---|---|---|---|
| Byte 0 | `FF` | Engine Torque Mode | 0xFF = 데이터 없음 |
| Byte 1 | `3C` | Driver's Demand Torque | 0x3C = 60 (offset -125 → -65%) |
| Byte 2 | `32` | Actual Engine Torque | 0x32 = 50 (offset -125 → -75%) |
| Byte 3-4 | `00 00` | Engine Speed | 0x0000 = 0 RPM |
| Byte 5 | `FF` | Source Address | 0xFF = 데이터 없음 |
| Byte 6 | `FF` | Engine Demand Torque | 0xFF = 데이터 없음 |
| Byte 7 | `00` | Reserved | — |

```mermaid
flowchart LR
    A["CAN 로그<br>0CF004FE#FF3C320000FFFF00"]
    A --> B["CAN ID<br>0x0CF004FE"]
    A --> C["Data<br>FF 3C 32 00 00 FF FF 00"]

    B --> D["Priority: 3<br>(상위 3bit)"]
    B --> E["PGN: 0xF004<br>= EEC1 엔진 속도"]
    B --> F["Source: 0xFE<br>= 주소 254"]

    C --> G["Byte 0-1: 토크 정보"]
    C --> H["Byte 2-3: 엔진 RPM"]
    C --> I["Byte 4-7: 기타"]
```

::: tip 핵심 정리

- CAN 프레임에는 데이터/리모트/에러/오버로드 4가지 종류가 있으며, 가장 많이 쓰이는 것은 <strong>데이터 프레임</strong>이다.
- 데이터 프레임은 SOF → ID → 제어 필드 → Data → CRC → ACK → EOF 순서로 구성된다.
- **Standard(11bit)** ID는 2,048개, **Extended(29bit)** ID는 5억 개 이상의 메시지를 구별할 수 있다. ISOBUS는 Extended를 사용한다.
- <strong>비트 스터핑</strong>은 5개 연속 동일 비트 뒤에 반대 비트를 삽입해 수신 노드의 동기화를 돕는다.
- **DLC** 0~8은 데이터 길이(바이트)와 1:1 대응한다.
- CAN 로그 `ID#DATA` 형식에서 ID를 분해하면 PGN과 소스 주소를 알 수 있다.

:::

## 8. ISO 11783가 정한 프레임 규칙

앞 절까지는 CAN 프레임 일반을 봤다. ISO 11783-3:2018(이하 Part 3)은 이 프레임 위에 몇 가지 규칙을 더 얹는다. Part 3은 CAN 규격(ISO 11898-1)과 자신이 다르면 Part 3이 우선한다고 정해 둔다(Part 3 5.1.1).

### 확장 프레임(CEFF)만 표준 통신에 쓴다

ISO 11898-1은 고전 CAN(Classical CAN)의 두 프레임 형식을 CBFF(Classical Base Frame Format)와 CEFF(Classical Extended Frame Format)라고 부른다. §3의 Standard(11bit)가 CBFF, Extended(29bit)가 CEFF다. Part 3의 취급은 다음과 같다.

| 형식 | Part 3의 취급 | 근거 |
|---|---|---|
| CEFF (29bit ID) | ISO 11783 컨트롤러는 CEFF를 써야 한다(shall). 표준화된 통신 전략은 CEFF에만 정의돼 있다 | 5.1.1 |
| CBFF (11bit ID) | 지원해도 된다(may). 다만 전부 제조사 독점(proprietary) 메시지이고, 다른 컨트롤러를 방해하지 않도록 최소 규칙만 정한다 | 5.1.1, 5.1.4 |
| FD 프레임 형식 | ISO 11783 네트워크에서 쓰면 안 된다(shall not) | 5.1.1 |

CEFF 메시지를 주고받지 못하는 하드웨어, 즉 ISO 11898-1을 따르지 않는 하드웨어는 네트워크에 쓰면 안 된다(Part 3 5.1.4의 IMPORTANT 문단). CAN FD를 금지하는 조항은 [CAN FD](/study/isobus/07-can-fd) 챕터에서 다시 본다.

Part 3은 주소를 쓰는 이유도 적어 둔다. CAN 규격은 정보 라우팅을 설명하면서 노드 주소를 쓰지 않는다고 하지만, ISO 11783은 여러 CF(Control Function, 제어 기능)가 같은 CAN 식별자를 쓰지 못하도록 CF 주소를 식별자에 넣는다(Part 3 5.1.1). 식별자 끝 8비트의 SA(Source Address, 소스 주소)가 그 장치다.

### 29비트 ID가 프레임 비트에 놓이는 위치

§3의 Extended 프레임 그림에서 Base ID(11bit)와 Extended ID(18bit) 사이에 SRR·IDE가 끼어 있었다. Part 3 Table 1은 이 비트들에 ISO 11783 필드를 하나씩 대응시킨다. SOF를 프레임 비트 1번으로 세면 다음과 같다.

![CEFF 프레임 비트 1~39에 SOF, P3~P1, EDP, DP, PF8~PF3, SRR, IDE, PF2~PF1, PS8~PS1, SA8~SA1, RTR(d), FDF(d), r0, DLC가 놓이고 PF 8비트가 SRR·IDE를 사이에 두고 갈라지는 모습, 아래는 CBFF의 SOF, P3~P1, SA8~SA1, RTR·IDE·FDF(d), DLC 배치](/images/study-isobus/04-iso-id-bit-mapping-light.png)
![CEFF 프레임 비트 1~39에 SOF, P3~P1, EDP, DP, PF8~PF3, SRR, IDE, PF2~PF1, PS8~PS1, SA8~SA1, RTR(d), FDF(d), r0, DLC가 놓이고 PF 8비트가 SRR·IDE를 사이에 두고 갈라지는 모습, 아래는 CBFF의 SOF, P3~P1, SA8~SA1, RTR·IDE·FDF(d), DLC 배치](/images/study-isobus/04-iso-id-bit-mapping-dark.png)

| 프레임 비트 | CAN 이름 | ISO 11783 이름 |
|---|---|---|
| 1 | SOF | SOF |
| 2~4 | ID28~ID26 | P3~P1 (Priority) |
| 5 | ID25 | EDP |
| 6 | ID24 | DP |
| 7~12 | ID23~ID18 | PF8~PF3 |
| 13~14 | SRR, IDE (둘 다 recessive) | SRR, IDE |
| 15~16 | ID17~ID16 | PF2~PF1 |
| 17~24 | ID15~ID8 | PS8~PS1 |
| 25~32 | ID7~ID0 | SA8~SA1 |
| 33 | RTR | RTR (dominant 고정) |
| 34 | FDF | FDF (dominant 고정) |
| 35 | r0 | r0 |
| 36~39 | DLC4~DLC1 | DLC4~DLC1 |

여기서 두 가지를 읽어 낼 수 있다.

- <strong>PF 필드가 SRR·IDE를 사이에 두고 갈라진다.</strong> PF의 상위 6비트(PF8~PF3)는 Base ID 구간에, 하위 2비트(PF2~PF1)는 Extended ID 구간에 있다. 로직 분석기로 비트를 직접 볼 때 PF를 한 덩어리로 찾으면 어긋난다. 소프트웨어가 받는 29비트 정수에서는 SRR·IDE가 빠지므로 PF가 다시 붙어 보인다.
- <strong>RTR과 FDF가 ISO 11783 열에서는 dominant로 고정</strong>돼 있다. CAN 열에서는 메시지에 따라 달라지는 비트(x)다. RTR이 dominant라는 것은 데이터 프레임만 쓴다는 뜻이고(아래 리모트 프레임 금지), FDF가 dominant라는 것은 고전 CAN 프레임만 쓴다는 뜻이다.

SOF·SRR·IDE·RTR·FDF·CRC·ACK·EOF와 제어 필드 일부는 CAN 규격이 전부 관리하고 데이터 링크 계층 위로는 보이지 않는다. ISO 11783은 이 비트들을 바꾸지 않는다(Part 3 5.2.1).

### CBFF(11bit) 메시지의 최소 규칙

CBFF를 쓰는 컨트롤러도 같은 버스를 쓰므로 Part 3은 11비트 ID의 해석 방식 하나만 정해 둔다. Table 1의 주석은 이를 "제조사 독점 11비트 식별자의 필수 형식"이라고 부른다(Part 3 5.1.4, Table 1).

| 프레임 비트 | 11비트 ID의 의미 |
|---|---|
| 2~4 | Priority 3비트 (5.2.2와 같은 의미) |
| 5~12 | 송신자의 SA 8비트 |
| 13~15 | RTR·IDE·FDF (모두 dominant) |

CBFF 메시지에는 PGN이 없다. 11비트 ID로 알 수 있는 것은 "누가(SA) 어떤 우선순위로" 보냈는지뿐이고, 내용 해석은 제조사 몫이다. CBFF와 CEFF가 같은 순간 중재에 들어가면 생기는 문제는 [CAN 중재와 우선순위](/study/isobus/05-can-arbitration) 챕터에서 비트 단위로 따라간다. Part 3 Annex D는 CBFF 트래픽을 별도 서브넷으로 분리해 CEFF 네트워크의 대역폭을 지키라고 강하게 권고한다.

### 리모트 프레임은 쓰지 않는다

§1의 네 가지 프레임 중 리모트 프레임은 ISOBUS에서 쓸 수 없다. Part 3 5.4.1은 RTR 비트를 recessive(논리 1)로 보내는 것을 금지한다.

이유도 원문에 있다. 리모트 프레임은 "이 ID의 데이터를 보내라"며 데이터 없이 ID만 버스에 올리는 방식이다. 그런데 ISO 11783의 ID 일부는 우선순위, 일부는 송신자 SA다. 응답할 장치의 ID로 리모트 프레임을 보내려면 요청자가 남의 SA를 단 프레임을 보내야 하는데, 장치는 다른 장치의 SA로 메시지를 보낼 수 없다. 그래서 ISO 11783은 데이터 프레임으로 된 별도 요청 메커니즘(Request PGN 59904)을 둔다. 요청 메시지의 규칙은 [J1939 메시지 구조](/study/isobus/09-j1939-message) 챕터에서 바이트 단위로 본다.

### 데이터 필드의 바이트·비트 번호

Part 3은 데이터 필드를 Byte 1~8, 바이트 안의 비트를 Bit 8~1로 부른다(Part 3 5.1.2, Figure 3). 이 번호 체계는 ISOBUS 문서 전체에서 쓰이므로 먼저 익혀 둔다.

- 가장 먼저 나가는 데이터 비트는 Byte 1의 MSB(Bit 8)이고, DLC 바로 뒤에 온다.
- 가장 나중에 나가는 데이터 비트는 Byte 8의 LSB(Bit 1)이고, CRC 바로 앞에 온다.
- 바이트 번호는 1부터 센다. §7 표가 Byte 0부터 센 것은 프로그래밍 배열 인덱스 관례다. 표준 문서를 읽을 때는 Byte 1 = `data[0]`으로 바꿔 읽어야 한다.

여러 바이트에 걸친 파라미터는 LSB를 앞 바이트에 둔다(Part 3 5.4.1). 2바이트 파라미터가 Byte 7~8에 있으면 Byte 7이 LSB, Byte 8이 MSB다. 데이터 필드 안에 PGN을 적을 때도 3바이트를 LSB부터 보낸다(Part 3 5.1.3). 예외는 ASCII 문자열처럼 따로 명시된 경우뿐이다.

### DLC와 남는 바이트

§5에서 DLC는 0~8이라고 했다. Part 3은 DLC를 무엇으로 정할지까지 규정한다.

| 상황 | DLC | 남는 바이트 | 근거 |
|---|---|---|---|
| PG 데이터 길이가 8바이트 이하로 정의됨 | 정의된 길이 그대로 (Request PGN 59904는 3) | 없음 | 5.2.8.1, 5.4.3 |
| multi-packet 가능 PG인데 이번에 보낼 데이터가 8바이트 이하 | 8 | "Not Available"(FF) | 5.2.8.2, 5.10.6.3 |
| 9바이트 이상을 TP로 나눠 보내는 각 프레임 | 8 | 마지막 패킷의 남는 바이트는 FF | 5.2.8.2, 5.10.5 |
| 같은 group function PG의 모든 하위 기능 | PG마다 하나로 고정 | 없음 | 5.2.8.1 |

Part 3이 덧붙이는 설계 규칙도 있다.

- PGN의 데이터 길이는 한 번 정하면 바꿀 수 없다. 처음에 multi-packet으로 정의하지 않았다면 나중에 multi-packet으로 바꿀 수도 없다(5.2.8.1). 그래서 확장될 여지가 있는 PGN은 처음부터 8바이트를 잡아 두라고 권고한다.
- group function PG는 CAN ID가 늘 같으므로 데이터 길이도 하나로 고정한다. 하위 기능은 데이터 필드(보통 첫 바이트)로 구분한다(5.2.8.1).

::: warning 구현 함정 — DLC만 보고 데이터 끝을 판단하지 않는다
multi-packet 가능 PG가 짧게 올 때 DLC는 8이고 뒤쪽은 FF다. 수신 측이 "DLC = 8이니 데이터도 8바이트"라고 읽으면 FF를 유효 값으로 오해할 수 있다. 실제 데이터의 끝은 PG 정의(길이 필드, 반복 횟수, 종결 문자 등)로 판단해야 한다. 표준은 DLC 규칙을 송신 측 의무로 적을 뿐이고, 이 함정은 그 규칙에서 따라 나오는 구현 해설이다.
:::

### 예제 — Request 프레임 하나를 비트 순서까지

Part 3 Annex C의 예처럼 SA 3(요청자)이 엔진(SA 0)에게 Component Identification(PGN 65259 = `0x00FEEB`)을 요청하는 프레임을 만든다.

| 항목 | 값 |
|---|---|
| Priority | 6 (Request의 기본값, Part 3 5.4.3) |
| PF / PS | 234(`0xEA`) / `0x00`(목적지 = 엔진) |
| SA | `0x03` |
| 29비트 ID | `0x18EA0003` |
| DLC | 3 |
| Data | `EB FE 00` (PGN 65259를 LSB부터) |

로그로 쓰면 `18EA0003#EBFE00`이다. §7의 로그와 달리 데이터가 3바이트뿐이다. DLC 3은 Request PGN의 정의 길이이고, 이 경우는 FF로 채워 8바이트를 만들지 않는다.

::: details 파이썬으로 검산 — 프레임 비트 1~39 배치
```python
def build_id(p, edp, dp, pf, ps, sa):
    return (p << 26) | (edp << 25) | (dp << 24) | (pf << 16) | (ps << 8) | sa


def frame_bits(can_id, dlc):
    """Part 3 Table 1 순서대로 (프레임 비트 번호, 이름, 값). 1 = recessive."""
    b = lambda n: (can_id >> n) & 1
    out = [(1, "SOF", 0)]
    names = ["P3", "P2", "P1", "EDP", "DP", "PF8", "PF7", "PF6", "PF5", "PF4", "PF3"]
    for i, name in enumerate(names):              # ID28..ID18
        out.append((2 + i, name, b(28 - i)))
    out += [(13, "SRR", 1), (14, "IDE", 1)]
    out += [(15, "PF2", b(17)), (16, "PF1", b(16))]
    for i in range(8):
        out.append((17 + i, f"PS{8 - i}", b(15 - i)))
    for i in range(8):
        out.append((25 + i, f"SA{8 - i}", b(7 - i)))
    out += [(33, "RTR", 0), (34, "FDF", 0), (35, "r0", 0)]
    for i in range(4):
        out.append((36 + i, f"DLC{4 - i}", (dlc >> (3 - i)) & 1))
    return out


PGN = 65259                                   # Component Identification
can_id = build_id(6, 0, 0, 0xEA, 0x00, 0x03)  # Request, DA=엔진(0x00), SA=0x03
data = [PGN & 0xFF, (PGN >> 8) & 0xFF, (PGN >> 16) & 0xFF]
assert can_id == 0x18EA0003
assert data == [0xEB, 0xFE, 0x00]

bits = frame_bits(can_id, dlc=len(data))
assert [n for n, _, _ in bits] == list(range(1, 40))
pf_bits = [v for n, name, v in bits if name.startswith("PF")]
assert int("".join(map(str, pf_bits)), 2) == 0xEA
print("PF 비트 위치:", [n for n, name, _ in bits if name.startswith("PF")])
print(f"log: {can_id:08X}#{''.join(f'{x:02X}' for x in data)}")
```

실행 결과:

```
PF 비트 위치: [7, 8, 9, 10, 11, 12, 15, 16]
log: 18EA0003#EBFE00
```
:::

::: tip 정리
- ISO 11783 표준 통신은 CEFF만 쓴다. CBFF는 제조사 독점용 최소 규칙(Priority + SA)만 있고, FD 형식은 금지다.
- 29비트 ID는 프레임 비트 2~32에 놓이고, PF는 SRR·IDE 때문에 프레임 비트 7~12와 15~16으로 갈라진다.
- RTR과 FDF는 dominant로 고정이다. 리모트 프레임 대신 Request PGN(59904)을 쓴다.
- 데이터는 Byte 1~8, Bit 8~1로 세고 여러 바이트 값은 LSB부터 놓는다.
- DLC는 PG 정의 길이(8 이하)이거나 8이다. multi-packet 가능 PG와 TP 프레임은 DLC 8에 남는 바이트를 FF로 채운다.
:::

::: details 확인 문제
1. (설명형) ISOBUS가 리모트 프레임을 금지하는 이유를 29비트 ID의 구조로 설명하라.
2. (디코딩) 로그 `18EAFF26#EBFE00`을 해석하라. Priority, PF와 메시지 종류, 목적지, 송신자, 요청하는 PGN, DLC를 모두 적는다.
3. (시나리오형) multi-packet 가능으로 정의된 PG를 이번에는 6바이트만 보내야 한다. TP를 써야 하는가? DLC와 Byte 7~8은 어떻게 채우는가?

**답 가이드**
1. ISO 11783 ID의 끝 8비트는 송신자 SA다. 리모트 프레임은 응답할 장치의 ID를 그대로 버스에 올려야 하므로 요청자가 남의 SA를 단 프레임을 보내게 된다. 장치는 다른 장치의 SA로 송신할 수 없으므로 RTR은 쓰지 않고 Request PGN을 쓴다(Part 3 5.4.1).
2. Priority 6, PF `0xEA`(234) = Request, PS `0xFF` = 전역 목적지, SA `0x26`, 데이터 `EB FE 00`은 LSB부터 읽어 PGN `0x00FEEB` = 65259(Component Identification)를 요청한다. DLC는 Request의 정의 길이인 3이다.
3. TP는 쓰지 않는다. 9바이트 미만이면 단일 프레임으로 보내고 DLC는 8, 남는 Byte 7~8은 "Not Available"(FF)로 채운다(Part 3 5.2.8.2, 5.10.6.3).
:::

## 다음 챕터

- 다음 : [CAN 중재와 우선순위](/study/isobus/05-can-arbitration)
