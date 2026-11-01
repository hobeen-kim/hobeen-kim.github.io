---
title: "J1939 메시지 구조: 29비트 ID, PGN, SPN"
description: "J1939가 29비트 CAN ID에 우선순위, 메시지 종류, 보낸 이를 담는 방법과 PGN, SPN을 읽는 법을 익힌다."
date: 2026-04-13
tags: [J1939, PGN, SPN, CAN, PDU]
prev: /study/isobus/08-j1939-intro
next: /study/isobus/10-j1939-request-ack
---

# J1939 메시지 구조: 29비트 ID, PGN, SPN

::: info 학습 목표
- 16진수 CAN ID를 2진수로 풀어 Priority, EDP, DP, PF, PS, SA 여섯 칸으로 손으로 나눌 수 있다.
- PF 값으로 PDU1(받는 주소를 적는 메시지)과 PDU2(모두에게 보내는 메시지)를 구분할 수 있다.
- ID에서 PGN을 계산하고, 거꾸로 PGN과 주소로 ID를 만들 수 있다.
- SPN의 위치, 분해능, 오프셋으로 데이터 바이트를 실제 값(예: 냉각수 온도)으로 바꿀 수 있다.
- 로그 한 줄 `18FEEE00#B03204FFFFFFFFFF`를 처음부터 끝까지 해석할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [8장 SAE J1939 입문](/study/isobus/08-j1939-intro), [4장 CAN 데이터 프레임](/study/isobus/04-can-data-frame)
- 이 장에서 처음 나오는 말
  - 비트 번호: 29비트 ID에서 비트의 자리 번호다. 맨 오른쪽(가장 낮은 자리)이 0번, 맨 왼쪽이 28번이다.
  - PDU1, PDU2: PF 값으로 나뉘는 두 메시지 형식이다. PDU1은 받는 장치의 주소를 적고, PDU2는 모두에게 보낸다.
  - DA(Destination Address): 받는 장치의 주소다. 255(`0xFF`)는 "모두에게"라는 뜻이다.
  - GE(Group Extension): PDU2에서 PS 칸이 맡는 역할이다. 메시지 종류 번호(PGN)의 일부가 된다.
  - SPN(Suspect Parameter Number): 메시지 데이터 안의 값 하나하나에 붙은 번호다.
  - 분해능(resolution)과 오프셋(offset): 데이터에 실린 원시값을 실제 값으로 바꾸는 곱셈 계수와 덧셈 상수다.
:::

택배 상자에 붙은 송장처럼, CAN 프레임 앞부분의 ID가 이 데이터가 무엇인지 알려 준다. [8장](/study/isobus/08-j1939-intro)에서는 J1939가 29비트 ID를 여섯 칸으로 나눈다는 큰 그림을 봤다. 이 장에서는 실제 16진수 ID를 손으로 쪼개 칸마다 값을 읽고, 그 값으로 메시지 종류(PGN)와 데이터 안의 값(SPN)을 찾아낸다. 장 끝에서는 로그 한 줄을 처음부터 끝까지 해석한다.

## 1. 29비트 ID를 손으로 쪼개기

이 절에서는 16진수로 적힌 CAN ID를 여섯 칸으로 나누는 과정을 손으로 따라 한다. 이 과정이 손에 익으면 로그를 볼 때마다 누가 무엇을 보냈는지 바로 읽힌다.

### 필드별 상세 설명

![J1939 29비트 CAN ID 필드 구조와 비트 번호(28~0)](/images/study-isobus/09-canid-fields-light.png)
![J1939 29비트 CAN ID 필드 구조와 비트 번호(28~0)](/images/study-isobus/09-canid-fields-dark.png)

그림 읽는 법: 상자 하나가 칸 하나이고, 상자 아래 눈금이 비트 번호다. 비트 번호는 오른쪽 끝(SA의 가장 낮은 비트)이 0번, 왼쪽 끝(Priority의 가장 높은 비트)이 28번이다. 10진수에서 오른쪽 끝이 일의 자리인 것처럼, 0번 비트가 가장 낮은 자리다. [8장](/study/isobus/08-j1939-intro)의 그림은 같은 칸을 버스에 나가는 순서(왼쪽부터 0번째)로 셌으니 세는 방향만 반대다.

| 필드 | 비트 위치 | 범위 | 설명 |
|---|---|---|---|
| **Priority** | 28~26 | 0~7 | 버스 중재 우선순위. **0이 최고, 7이 최저**. 기본값은 제어 지향 메시지 3, 그 외 6 |
| **EDP** | 25 | 0~1 | Extended Data Page. J1939에서는 0 고정 |
| **DP** | 24 | 0~1 | Data Page. 0: 기본 J1939, 1: 확장 PGN 공간 |
| **PF** | 23~16 | 0~255 | PDU Format. 메시지 종류 결정, PDU1/PDU2 구분 기준 |
| **PS** | 15~8 | 0~255 | PDU Specific. PF < 240이면 목적지 주소(DA), PF >= 240이면 그룹 확장 |
| **SA** | 7~0 | 0~253 | Source Address. 메시지 송신 노드 주소 |

각 필드가 차지하는 비트 위치는 위 그림의 눈금(28~0)과 표가 그대로 대응한다.

표의 "범위"는 칸에 들어갈 수 있는 값이다. 3비트 칸은 0~7, 8비트 칸은 0~255를 담는다. SA의 범위가 0~253인 것은 254와 255가 "주소 없음"과 "모두에게"라는 특별한 뜻으로 쓰이기 때문이다([8장](/study/isobus/08-j1939-intro)). Priority 기본값의 "제어 지향 메시지"는 무언가를 움직이라고 명령하는 메시지이고, "그 외"는 상태 정보나 요청 같은 메시지다.

### 16진수를 2진수로 바꾸는 표

16진수 한 자리는 2진수 네 자리(4비트)와 정확히 맞는다. 손으로 ID를 쪼개려면 아래 표만 있으면 된다.

| 16진수 | 2진수 | 16진수 | 2진수 |
|---|---|---|---|
| 0 | 0000 | 8 | 1000 |
| 1 | 0001 | 9 | 1001 |
| 2 | 0010 | A | 1010 |
| 3 | 0011 | B | 1011 |
| 4 | 0100 | C | 1100 |
| 5 | 0101 | D | 1101 |
| 6 | 0110 | E | 1110 |
| 7 | 0111 | F | 1111 |

A~F는 10진수 10~15다. 2진수 네 자리의 자릿값은 왼쪽부터 8, 4, 2, 1이다. 예를 들어 `1110`은 8 + 4 + 2 = 14 = `E`다.

### 예제: 0x18FEEE00 분해

CAN 29비트 ID `0x18FEEE00`을 hex → binary로 풀면 `0001 1000 1111 1110 1110 1110 0000 0000`(32bit)이고, 하위 29비트만 취해 필드로 나누면 다음과 같다.

![0x18FEEE00 CAN ID 분해: Priority=6, EDP=0, DP=0, PF=0xFE(254), PS=0xEE(238), SA=0x00](/images/study-isobus/09-canid-example-18feee00-light.png)
![0x18FEEE00 CAN ID 분해: Priority=6, EDP=0, DP=0, PF=0xFE(254), PS=0xEE(238), SA=0x00](/images/study-isobus/09-canid-example-18feee00-dark.png)

손으로 따라 하면 이렇다.

1. 16진수를 한 자리씩 2진수로 바꾼다: `1`→`0001`, `8`→`1000`, `F`→`1111`, `E`→`1110`, `E`→`1110`, `E`→`1110`, `0`→`0000`, `0`→`0000`.
2. 이어 쓰면 32비트다. CAN ID는 29비트이므로 맨 앞 3비트 `000`은 ID가 아니다. 버린다.
3. 남은 29비트를 왼쪽부터 3, 1, 1, 8, 8, 8비트로 자른다.

| 칸 | 비트 번호 | 잘라 낸 비트 | 값 |
|---|---|---|---|
| Priority | 28~26 | `110` | 6 |
| EDP | 25 | `0` | 0 |
| DP | 24 | `0` | 0 |
| PF | 23~16 | `1111 1110` | `0xFE` = 254 |
| PS | 15~8 | `1110 1110` | `0xEE` = 238 |
| SA | 7~0 | `0000 0000` | `0x00` = 0 |

4. 값을 해석한다. Priority 6은 정보 메시지의 기본값이다. PF 254는 240 이상이므로 PDU2이고(2절), PS `0xEE`는 받는 주소가 아니라 메시지 종류의 일부(GE)다. SA `0x00`은 보낸 장치가 엔진 ECU라는 뜻이다.

### 지름길: 맨 앞 두 자리만 2진수로 푼다

PF, PS, SA는 8비트씩이고 바이트 경계에 딱 맞게 놓여 있다. 그래서 16진수 여덟 자리 가운데 뒤 여섯 자리는 두 자리씩 끊기만 하면 PF, PS, SA다. 2진수로 풀어야 하는 것은 맨 앞 두 자리(첫 바이트)뿐이다.

![0x18FEEE00을 두 자리씩 18, FE, EE, 00으로 끊으면 뒤 세 바이트가 그대로 PF 254, PS 238, SA 0이 되고, 첫 바이트 18만 2진수 0001 1000으로 풀어 버리는 3비트, Priority 110(6), EDP 0, DP 0으로 나누는 지름길](/images/study-isobus/09-id-byte-shortcut-light.png)
![0x18FEEE00을 두 자리씩 18, FE, EE, 00으로 끊으면 뒤 세 바이트가 그대로 PF 254, PS 238, SA 0이 되고, 첫 바이트 18만 2진수 0001 1000으로 풀어 버리는 3비트, Priority 110(6), EDP 0, DP 0으로 나누는 지름길](/images/study-isobus/09-id-byte-shortcut-dark.png)

첫 바이트 8비트는 [버리는 3비트][Priority 3비트][EDP 1비트][DP 1비트]로 나뉜다. 자주 보는 첫 바이트를 미리 풀어 두면 다음과 같다.

| 첫 바이트 | 2진수 (3·3·1·1로 끊음) | Priority | EDP | DP |
|---|---|---|---|---|
| `0x0C` | `000 011 0 0` | 3 | 0 | 0 |
| `0x18` | `000 110 0 0` | 6 | 0 | 0 |
| `0x19` | `000 110 0 1` | 6 | 0 | 1 |
| `0x1C` | `000 111 0 0` | 7 | 0 | 0 |

예를 들어 `0x18FEEE00`은 `18 | FE | EE | 00`으로 끊고, `18`을 표에서 찾으면 Priority 6, EDP 0, DP 0이다. 나머지는 PF `FE`, PS `EE`, SA `00`이다.

<small>근거: ISO 11783-3 5.1.2, 5.2.2, Table 1</small>

## 2. PDU1과 PDU2: PF 값이 정하는 두 형식

PS 칸은 PF 값에 따라 뜻이 바뀐다. 송장의 한 칸이 어떤 때는 "받는 사람"이 되고 어떤 때는 "물건 종류의 세부 번호"가 되는 셈이다. 이 절에서는 그 기준과 두 형식의 차이를 본다. 3절의 PGN 계산도 이 구분에서 출발한다.

### 구분 기준: PF 값

![29비트 CAN ID를 받으면 PF 값을 확인해, PF가 240보다 작으면 PDU1(Peer-to-Peer)로 보고 PS를 받는 주소(특정 노드 또는 전역 DA=255)로 읽고, 아니면 PDU2(Broadcast)로 보고 PS를 Group Extension으로 읽어 모든 노드에게 보낸 메시지로 처리하는 흐름](/images/study-isobus/09-pdu-format-decision-light.png)
![29비트 CAN ID를 받으면 PF 값을 확인해, PF가 240보다 작으면 PDU1(Peer-to-Peer)로 보고 PS를 받는 주소(특정 노드 또는 전역 DA=255)로 읽고, 아니면 PDU2(Broadcast)로 보고 PS를 Group Extension으로 읽어 모든 노드에게 보낸 메시지로 처리하는 흐름](/images/study-isobus/09-pdu-format-decision-dark.png)

기준은 숫자 하나, 240(`0xF0`)이다. 16진수로 보면 더 쉽다. PF의 첫 자리가 `F`이면(`F0`~`FF`) PDU2, 그 밖이면 PDU1이다. 그림의 Peer-to-Peer는 "한 장치가 다른 한 장치에게", Broadcast는 "한 장치가 모두에게"라는 뜻이다.

### PDU1 (PF < 240): 목적지 지정 메시지

```
PS = DA (Destination Address)

예: 진단 도구(SA=0xF9)가 엔진 ECU(DA=0x00)에게 요청
  Priority = 6, EDP=0, DP=0
  PF = 0xEA (234, < 240 → PDU1)
  PS = DA = 0x00 (엔진 ECU)
  SA = 0xF9 (진단 도구)
  → CAN ID: 0x18EA00F9
```

이 ID를 1절의 지름길로 읽으면 `18 | EA | 00 | F9`다. 첫 바이트 `18`은 Priority 6, EDP 0, DP 0이다. PF `0xEA`(234)는 240보다 작으므로 PDU1이고, PS `0x00`은 받는 장치(엔진 ECU)의 주소다. SA `0xF9`는 보낸 진단 도구다. PF 234는 "데이터를 보내 달라"는 Request(요청) 메시지로, [10장](/study/isobus/10-j1939-request-ack)에서 자세히 본다.

PDU1이 특정 노드 전용은 아니다. DA에 전역 주소 255(0xFF)를 넣으면 PDU1 메시지도 모든 노드를 대상으로 브로드캐스트할 수 있다. 반면 PDU2는 목적지를 지정할 수 없는 <strong>전역 전용</strong>이다.

### PDU2 (PF >= 240): 브로드캐스트 메시지

```
PS = Group Extension (PGN의 일부)

예: 엔진 ECU(SA=0x00)가 Engine Temperature 브로드캐스트
  Priority = 6, EDP=0, DP=0
  PF = 0xFE (254, >= 240 → PDU2)
  PS = 0xEE (238, Group Extension → PGN의 일부)
  SA = 0x00 (엔진 ECU)
  → CAN ID: 0x18FEEE00
  → PGN = 254 * 256 + 238 = 65262
```

여기서 PS `0xEE`는 받는 주소가 아니라 메시지 종류 번호의 일부다. 그래서 마지막 줄처럼 PGN 계산에 PS가 들어간다. 계산 방법은 3절에서 본다.

### 비교 표

| 항목 | PDU1 | PDU2 |
|---|---|---|
| PF 값 범위 | 0 ~ 239 (0x00 ~ 0xEF) | 240 ~ 255 (0xF0 ~ 0xFF) |
| PS 의미 | Destination Address | Group Extension (PGN의 일부) |
| 전송 방식 | 특정 노드 지정 (DA=255면 전역 전송) | 버스 전체 브로드캐스트 (전역 전용) |
| 주요 용도 | 요청/응답, 진단 | 센서 데이터 주기적 전송 |

"요청/응답, 진단"은 특정 장치에게 묻고 답하는 메시지이고, "센서 데이터 주기적 전송"은 온도·속도처럼 여러 장치가 함께 쓰는 값을 정해진 주기로 방송하는 메시지다.

<small>근거: ISO 11783-3 5.2.6, 5.3.1~5.3.3, Table 4</small>

## 3. PGN: 메시지 종류 번호

PGN(Parameter Group Number)은 ID에서 "이 메시지가 무엇인가"를 나타내는 번호다. 이 절에서는 ID에서 PGN을 계산하고, 거꾸로 PGN으로 ID를 만드는 법을 익힌다.

### PGN이란

PGN은 <strong>메시지의 종류(의미)</strong>를 식별하는 번호다. 같은 PGN을 가진 메시지는 항상 같은 형식의 데이터를 담는다.

```
PGN 65262 → Engine Temperature (엔진 온도 관련 파라미터들)
PGN 65265 → Cruise Control/Vehicle Speed
PGN 61444 → Electronic Engine Controller 1
```

Parameter Group(PG)은 함께 보내는 값들의 묶음이다. 예를 들어 PGN 65262 묶음에는 냉각수 온도, 연료 온도, 오일 온도 같은 엔진 온도 값이 들어 있다(4절). 받는 쪽은 PGN만 알면 데이터 8바이트 가운데 어디에 무엇이 있는지 안다.

### PGN 계산 공식

PGN 계산에는 PF 값이 핵심이다.

```
PF >= 240 (PDU2, 브로드캐스트):
  PGN = (EDP * 131072) + (DP * 65536) + (PF * 256) + PS

PF < 240 (PDU1, 목적지 지정):
  PGN = (EDP * 131072) + (DP * 65536) + (PF * 256)
  (PS는 목적지 주소이므로 PGN에 포함하지 않음)
```

> EDP는 J1939에서 보통 0이므로 EDP 항은 생략 가능.

공식의 곱셈은 "자리를 옮겨 붙이기"다. 256을 곱하면 8비트, 즉 16진수 두 자리만큼 왼쪽으로 옮겨진다. 65536(= 256 × 256)을 곱하면 16비트, 131072(= 65536 × 2)를 곱하면 17비트만큼 옮겨진다. 그래서 16진수로 보면 PGN은 DP, PF, PS를 이어 붙인 것과 같다.

- PDU2: PGN = DP, PF, PS를 이어 붙인 값. 예: `0x18FEEE00` → DP `0`, PF `FE`, PS `EE` → `0x0FEEE` = 65262
- PDU1: PGN = DP, PF, `00`을 이어 붙인 값. 예: `0x18EAFF26` → DP `0`, PF `EA`, PS 자리는 `00` → `0x0EA00` = 59904

![PDU2 예 0x18FEEE00에서는 Priority와 SA를 빼고 EDP·DP 0, PF FE, PS EE를 이어 PGN 0x0FEEE = 65262를 만들고, PDU1 예 0x18EAFF26에서는 받는 주소인 PS FF 대신 00을 넣어 PGN 0x0EA00 = 59904를 만드는 과정](/images/study-isobus/09-pgn-from-id-light.png)
![PDU2 예 0x18FEEE00에서는 Priority와 SA를 빼고 EDP·DP 0, PF FE, PS EE를 이어 PGN 0x0FEEE = 65262를 만들고, PDU1 예 0x18EAFF26에서는 받는 주소인 PS FF 대신 00을 넣어 PGN 0x0EA00 = 59904를 만드는 과정](/images/study-isobus/09-pgn-from-id-dark.png)

그림 읽는 법: 위 줄이 ID의 여섯 칸, 아래 줄이 PGN이다. 회색 칸(Priority, SA, 그리고 PDU1의 PS)은 PGN에 들어가지 않는다. PDU1에서 PS를 빼는 이유는 PS가 받는 주소이기 때문이다. 같은 요청 메시지를 엔진에게 보내든 변속기에게 보내든 메시지 종류는 같아야 한다.

### 계산 예제 1: PGN 65262 (Engine Temperature)

거꾸로 PGN에서 PF와 PS를 구할 수도 있다. DP가 0일 때 PGN을 256으로 나눈 몫이 PF, 나머지가 PS다.

```
목표: PGN 65262 → PF, PS 값 역산

65262 / 256 = 254.9... → PF = 254 = 0xFE (>= 240이므로 PDU2)
65262 - (254 * 256) = 65262 - 65024 = 238 → PS = 238 = 0xEE

검증:
  PF = 0xFE = 254, PS = 0xEE = 238
  PGN = 254 * 256 + 238 = 65024 + 238 = 65262  ✓

CAN ID 구성 (Priority=6, DP=0, EDP=0, SA=0x00):
  0x18FEEE00
```

마지막 줄의 ID는 1절 지름길 표의 첫 바이트 `0x18`(Priority 6, EDP 0, DP 0) 뒤에 PF `FE`, PS `EE`, SA `00`을 이어 쓴 것이다.

### 계산 예제 2: PGN 61444 (EEC1)

EEC1(Electronic Engine Controller 1)은 엔진 제어기가 보내는 메시지 가운데 하나다.

```
목표: PGN 61444 → PF, PS 역산

61444 / 256 = 240.0 → PF = 240 = 0xF0 (>= 240이므로 PDU2)
61444 - (240 * 256) = 61444 - 61440 = 4 → PS = 4 = 0x04

CAN ID (Priority=3, SA=0x00):
  Priority=3 → 0b011 → 0x0C000000 (비트 26~28)
  0x0CF00400
```

`Priority=3 → 0b011 → 0x0C000000` 줄은 Priority 3을 2진수 `011`로 쓰고, 그것을 비트 28~26 자리에 놓으면 `0x0C000000`이 된다는 뜻이다. 1절 지름길 표의 첫 바이트 `0x0C`가 바로 Priority 3이다. 여기에 PF `F0`, PS `04`, SA `00`을 이어 쓰면 `0x0CF00400`이다.

ID를 만드는 일반 규칙을 식으로 쓰면 다음과 같다.

- ID = Priority × 2²⁶ + (PGN + DA) × 256 + SA
- DA는 PDU1일 때만 더하고, PDU2이면 0으로 둔다.

예를 들어 VT(SA `0x26`)가 모두에게(DA `0xFF`) 보내는 요청(PGN 59904 = `0xEA00`)은 `0x18000000` + `0xEAFF00` + `0x26` = `0x18EAFF26`이다.

<small>근거: ISO 11783-3 5.1.3, 5.2.6, Table 2</small>

## 4. SPN: 데이터 안의 값 하나하나

PGN이 "상자의 종류"라면 SPN은 상자 안 칸마다 붙은 번호다. 이 절에서는 SPN이 데이터 8바이트의 어디에 놓이는지, 원시값을 실제 값으로 어떻게 바꾸는지 본다.

### SPN이란

SPN은 <strong>데이터 필드(8바이트) 내의 개별 파라미터</strong>를 식별하는 번호다. 하나의 PGN 메시지에 여러 SPN이 포함될 수 있다.

```
PGN 65262 (Engine Temperature) 내 SPN 목록:
  SPN 110 : Engine Coolant Temperature    (byte 1, 1byte)
  SPN 174 : Engine Fuel Temperature 1    (byte 2, 1byte)
  SPN 175 : Engine Oil Temperature 1     (byte 3~4, 2byte)
  SPN 176 : Engine Turbocharger Oil Temperature (byte 5~6, 2byte)
  SPN 52  : Engine Intercooler Temperature (byte 7, 1byte)
  SPN 1134: Engine Intercooler Thermostat Opening (byte 8, 1byte)
```

목록의 "byte 1"은 데이터 필드의 첫 번째 바이트다. 표준 문서는 바이트를 1부터 센다([4장](/study/isobus/04-can-data-frame)). "byte 3~4, 2byte"는 값 하나가 바이트 두 개에 걸쳐 있다는 뜻이다.

::: tip 멀티바이트 파라미터는 LSB 먼저
SPN 175처럼 2바이트 이상인 파라미터는 데이터 필드에 <strong>LSB 먼저</strong>(리틀엔디언) 배치한다. 예를 들어 byte 3~4에 놓인 2바이트 파라미터는 byte 3이 LSB, byte 4가 MSB다(ASCII 등 별도 명시된 경우는 예외).
:::

LSB(Least Significant Byte)는 값의 낮은 자리 바이트, MSB(Most Significant Byte)는 높은 자리 바이트다. 예를 들어 값 `0x1234`를 byte 3~4에 실으면 byte 3에 `34`, byte 4에 `12`가 들어간다. 읽을 때는 거꾸로 byte 4를 앞에, byte 3을 뒤에 붙여 `0x1234`로 만든다. 낮은 자리를 먼저 놓는 이 방식을 리틀 엔디언(little-endian)이라고 부른다.

### SPN 속성 (SPN 110 예시)

SPN 하나에는 위치와 계산 규칙이 함께 정해져 있다. 냉각수 온도(SPN 110)의 속성은 다음과 같다.

| 속성 | 값 |
|---|---|
| SPN 번호 | 110 |
| 이름 | Engine Coolant Temperature |
| PGN | 65262 |
| 데이터 위치 | byte 1 (offset 0) |
| 길이 | 1 byte |
| 분해능(Resolution) | 1 °C/bit |
| 오프셋(Offset) | -40 °C |
| 유효 범위 | -40 ~ 210 °C |
| 원시값 0xFF | Not Available (N/A) |

- 데이터 위치 "byte 1 (offset 0)": 표준 번호로는 1번째 바이트, 프로그램 배열 번호(0부터 셈)로는 0번이다.
- 분해능 "1 °C/bit": 원시값이 1 늘 때 실제 값이 1 °C 는다는 뜻이다.
- 오프셋 "-40 °C": 계산 마지막에 더하는 값이다. 원시값은 0 이상의 수만 담으므로, 영하의 온도를 나타내려고 기준점을 -40 °C로 내려 둔 것이다.
- 유효 범위 "-40 ~ 210 °C": 1바이트 값의 정상 범위 0~250(아래 특수값 표)을 공식에 넣은 결과다. 0 × 1 - 40 = -40, 250 × 1 - 40 = 210이다.

### 특수값: FF는 "값 없음"

데이터에는 정상 값 말고도 "지금은 값을 줄 수 없다"는 표시가 필요하다. 센서가 없거나 고장 난 경우다. ISO 11783-7(트랙터·작업기 메시지를 정하는 표준 문서)은 값의 크기마다 맨 위쪽 몇 값을 이런 표시로 떼어 둔다.

| 이름 | 1바이트 값 | 2바이트 값 | 뜻 |
|---|---|---|---|
| 정상 신호(Valid signal) | `00`~`FA` (0~250) | `0000`~`FAFF` | 실제 측정값 |
| 파라미터별 지시(Parameter-specific indicator) | `FB` (251) | `FBxx` | 파라미터마다 따로 정한 특별한 뜻 |
| 예약 | `FC`~`FD` (252~253) | `FC00`~`FDFF` | 나중에 쓰려고 비워 둔 값 |
| 오류 표시(Error indicator) | `FE` (254) | `FExx` | 센서나 장치 고장으로 값을 줄 수 없다 |
| 값 없음(Not available) | `FF` (255) | `FFxx` | 설치되지 않았거나 보내지 않는 값이다 |

`xx`는 아무 값이나 와도 된다는 뜻이다. 2바이트 값은 높은 자리 바이트(MSB)만 보면 어느 칸인지 알 수 있다. SPN 속성 표의 "원시값 0xFF = Not Available (N/A)"이 바로 이 규칙이다. 데이터 필드에서 쓰지 않는 바이트도 `FF`로 채운다.

### SPN 값 변환 공식

```
실제값 = 원시값(raw) * 분해능 + 오프셋

SPN 110, raw = 0xB0 = 176:
  실제 온도 = 176 * 1 + (-40) = 136 °C
```

단계별로 풀면 다음과 같다.

1. byte 1의 원시값 `0xB0`을 10진수로 바꾼다. `B`는 11이므로 11 × 16 + 0 = 176이다.
2. 분해능을 곱한다: 176 × 1 = 176.
3. 오프셋을 더한다: 176 + (-40) = 136.
4. 단위를 붙인다: 136 °C.

<small>근거: ISO 11783-3 5.4.1, ISO 11783-7 3.3.3</small>

## 5. 로그 한 줄 해석하기: 18FEEE00#B03204FFFFFFFFFF

지금까지 배운 것을 모두 써서 실제 로그 한 줄을 처음부터 끝까지 읽어 본다. 대상 메시지는 다음과 같다.

```
18FEEE00#B03204FFFFFFFFFF
```

`#` 앞은 CAN ID, 뒤는 데이터 바이트를 16진수로 이어 쓴 것이다. 리눅스의 CAN 도구(can-utils)가 쓰는 표기다.

### 1단계: CAN ID와 데이터 분리

```
CAN ID   : 18FEEE00 (hex, 29비트)
데이터   : B0 32 04 FF FF FF FF FF (8바이트)
           [0][1][2][3][4][5][6][7]
```

아래 줄의 `[0]`~`[7]`은 프로그램 배열 번호다. 표준 문서의 Byte 1~8과 한 칸씩 어긋나므로 `[0]`을 Byte 1로 바꿔 읽는다.

### 2단계: 29비트 ID 분해

CAN ID `18FEEE00`을 binary로 풀어 필드별로 나누면 앞서 본 것과 동일하다 (PF = 0xFE = 254 → PDU2).

![0x18FEEE00 CAN ID 분해: Priority=6, EDP=0, DP=0, PF=0xFE(254), PS=0xEE(238), SA=0x00](/images/study-isobus/09-canid-example-18feee00-light.png)
![0x18FEEE00 CAN ID 분해: Priority=6, EDP=0, DP=0, PF=0xFE(254), PS=0xEE(238), SA=0x00](/images/study-isobus/09-canid-example-18feee00-dark.png)

지름길로 읽으면 `18 | FE | EE | 00`이고, `18`은 Priority 6, EDP 0, DP 0이다.

### 3단계: PGN 계산

```
PF = 254, PS = 238 (PDU2이므로 PS를 PGN에 포함)
PGN = DP * 65536 + PF * 256 + PS
    = 0 * 65536 + 254 * 256 + 238
    = 0 + 65024 + 238
    = 65262  → Engine Temperature
```

### 4단계: 데이터 필드 해석

![데이터 필드(8byte) 내 SPN 배치: byte[0]=SPN110→136°C, byte[1]=SPN174→10°C, byte[2~3]=SPN175(LSB/MSB), byte[4~5]=SPN176, byte[6]=SPN52, byte[7]=SPN1134](/images/study-isobus/09-spn-byte-layout-light.png)
![데이터 필드(8byte) 내 SPN 배치: byte[0]=SPN110→136°C, byte[1]=SPN174→10°C, byte[2~3]=SPN175(LSB/MSB), byte[4~5]=SPN176, byte[6]=SPN52, byte[7]=SPN1134](/images/study-isobus/09-spn-byte-layout-dark.png)

그림의 상자 여덟 개가 데이터 8바이트다. 상자 안 위쪽은 그 바이트를 쓰는 SPN, 아래쪽은 실제 바이트 값이고, 상자 밑은 해석 결과다. `byte[0]`은 배열 번호이므로 Byte 1이다. SPN 175와 176은 바이트 두 개씩 차지한다.

### 5단계: SPN 110 값 추출

```
SPN 110 (Engine Coolant Temperature):
  데이터 위치: byte 1 (offset 0) → byte[0] = 0xB0

  0xB0 = 176 (decimal)

  실제 온도 = 176 * 1 °C/bit + (-40 °C)
            = 176 - 40
            = 136 °C

결과: 엔진 냉각수 온도 = 136 °C
```

### 6단계: 전체 파싱 결과 요약

```
메시지   : 18FEEE00#B03204FFFFFFFFFF
Priority : 6
SA       : 0x00 (Engine ECU #1)
PGN      : 65262 (Engine Temperature)

SPN 110  Engine Coolant Temperature : 136 °C  (byte[0]=0xB0)
SPN 174  Engine Fuel Temperature 1  : 10 °C   (byte[1]=0x32, 50-40=10)
SPN 175  Engine Oil Temperature 1   : N/A     (byte[2~3]=0x04,0xFF → raw=0xFF04, N/A 영역)
SPN 176  Engine Turbocharger Oil Temp : N/A
SPN 52   Engine Intercooler Temp    : N/A
SPN 1134 Intercooler Thermostat Open : N/A
```

SPN 110 말고 나머지도 같은 방법으로 읽는다.

- SPN 174: byte 2 = `0x32` = 3 × 16 + 2 = 50이다. 50 × 1 - 40 = 10 °C.
- SPN 175: byte 3~4 = `04 FF`다. LSB가 먼저이므로 byte 4의 `FF`를 앞에 붙여 원시값 `0xFF04`가 된다. 높은 자리 바이트가 `FF`이므로 특수값 표의 "값 없음"이다.
- SPN 176, 52, 1134: 해당 바이트가 모두 `FF`라서 "값 없음"이다.

아래 함수는 1~5단계를 코드로 옮긴 것이다. ID에서 칸을 뽑을 때는 오른쪽으로 민 뒤(`>>`) 필요한 비트만 남긴다(`&`). 미는 칸 수가 그 칸의 가장 낮은 비트 번호다. 예를 들어 PS는 비트 15~8이므로 8칸 밀고 `& 0xFF`로 끝 8비트만 남긴다.

::: details Python 파싱 예제
```python
def parse_j1939_message(can_id_hex: str, data_hex: str):
    """
    J1939 CAN 메시지를 파싱한다.

    Args:
        can_id_hex: 29비트 CAN ID (hex string, e.g. "18FEEE00")
        data_hex:   데이터 필드 (hex string, e.g. "B03204FFFFFFFFFF")
    """
    can_id = int(can_id_hex, 16)

    # 29비트 ID 분해
    sa       = (can_id >> 0) & 0xFF
    ps       = (can_id >> 8) & 0xFF
    pf       = (can_id >> 16) & 0xFF
    dp       = (can_id >> 24) & 0x01
    edp      = (can_id >> 25) & 0x01
    priority = (can_id >> 26) & 0x07

    # PGN 계산
    if pf >= 240:   # PDU2: PS는 Group Extension
        pgn = (edp << 17) | (dp << 16) | (pf << 8) | ps
    else:           # PDU1: PS는 목적지 주소
        pgn = (edp << 17) | (dp << 16) | (pf << 8)

    print(f"Priority : {priority}")
    print(f"SA       : 0x{sa:02X} ({sa})")
    print(f"PF       : 0x{pf:02X} ({pf})")
    print(f"PS       : 0x{ps:02X} ({ps})")
    print(f"PGN      : {pgn} (0x{pgn:05X})")

    # 데이터 파싱
    data = bytes.fromhex(data_hex)

    if pgn == 65262:  # Engine Temperature
        print("\n[PGN 65262: Engine Temperature]")
        spn110_raw = data[0]  # SPN 110: byte 1 (offset 0)
        if spn110_raw == 0xFF:
            print("  SPN 110 Engine Coolant Temp: N/A")
        else:
            spn110_val = spn110_raw * 1 + (-40)
            print(f"  SPN 110 Engine Coolant Temp: {spn110_val} °C (raw=0x{spn110_raw:02X})")

        spn174_raw = data[1]  # SPN 174: byte 2 (offset 1)
        if spn174_raw == 0xFF:
            print("  SPN 174 Engine Fuel Temp 1 : N/A")
        else:
            spn174_val = spn174_raw * 1 + (-40)
            print(f"  SPN 174 Engine Fuel Temp 1 : {spn174_val} °C (raw=0x{spn174_raw:02X})")


# 실행 예시
parse_j1939_message("18FEEE00", "B03204FFFFFFFFFF")
```

실행 결과:

```
Priority : 6
SA       : 0x00 (0)
PF       : 0xFE (254)
PS       : 0xEE (238)
PGN      : 65262 (0x0FEEE)

[PGN 65262: Engine Temperature]
  SPN 110 Engine Coolant Temp: 136 °C (raw=0xB0)
  SPN 174 Engine Fuel Temp 1 : 10 °C (raw=0x32)
```

Priority, SA, PF, PS, PGN이 2~3단계와 같고, SPN 110과 174의 값이 6단계와 같다.
:::

## 6. PDU 필드별 규칙: 보내는 쪽과 받는 쪽 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 장 끝의 핵심 정리로 가도 된다.
:::

1절은 29비트 ID의 필드를 "무엇이 들어 있나"로 봤다. ISO 11783-3(ISOBUS의 데이터 링크 계층을 정하는 표준 문서)은 같은 필드를 "송신 측은 무엇을 지켜야 하고 수신 측은 어떻게 읽어야 하나"로 규정한다. PDU는 Priority, EDP, DP, PF, PS, SA, 데이터의 7개 필드이고, 고전 CAN 프레임 하나에 PDU는 정확히 하나다.

| 필드 | 송신 측 규칙 | 수신 측 규칙 |
|---|---|---|
| Priority | 기본값은 제어 3, 그 밖 6. PGN별로 재설정할 수 있어야 함 | 마스킹해 무시 |
| EDP | 항상 0 | 1이면 DP와 함께 판별(둘 다 1이면 ISO 15765-2 프레임) |
| DP | 페이지 0·1 선택 | PGN 계산에 포함 |
| PF | PDU 형식과 PGN 결정. 8바이트를 다 쓰도록 파라미터를 묶는 것을 권장 | 240 미만 PDU1, 이상 PDU2 |
| PS | PDU1이면 DA, PDU2면 GE | DA가 자기 주소도 전역(255)도 아니면 무시. 255면 모두 듣고 해당하면 대응 |
| SA | 네트워크에서 SA 하나는 CF 하나만 쓴다 | 송신자 식별, 응답의 목적지 |
| 데이터 | DLC 규칙, 여러 바이트 값은 LSB 먼저, 남는 바이트는 FF | PG 정의로 해석 |

표의 낱말 몇 개를 풀면 이렇다. 마스킹(masking)은 특정 비트를 지워 비교에서 빼는 것이다. ISO 15765-2 프레임은 EDP와 DP가 모두 1인 자동차 진단 통신용 프레임이다([8장](/study/isobus/08-j1939-intro)). CF(Control Function)는 버스에서 주소 하나를 쓰는 기능 단위다. DLC(Data Length Code)는 프레임의 데이터 바이트 수를 적는 칸이다([4장](/study/isobus/04-can-data-frame)).

몇 가지는 풀어 둘 필요가 있다.

- <strong>Priority는 수신 측 판단에 쓰지 않는다.</strong> 같은 PGN이 다른 Priority로 와도 같은 메시지다. 필터 설정은 [CAN 중재와 우선순위](/study/isobus/05-can-arbitration) 챕터에서 다룬다.
- <strong>DA 비교는 집합으로 한다.</strong> 컨트롤러 하나가 여러 기능을 수행하면 주소를 여러 개 가질 수 있다. "내 주소는 값 하나"라고 가정하면 두 번째 CF 앞으로 온 메시지를 버린다.
- <strong>DA = 255는 "모두 들어라"이면서 "해당하면 대응하라"다.</strong> 전역 목적지 주소는 모든 컨트롤러에게 듣고 그에 맞게 응답하도록 요구한다. 무엇이 "맞게"인지는 [10장](/study/isobus/10-j1939-request-ack)의 요청 규칙이 정한다.
- <strong>GE는 PGN의 일부다.</strong> PF의 상위 4비트가 모두 1이면(PF ≥ 240) PS는 GE이고, GE와 PF의 하위 4비트가 합쳐 데이터 페이지당 4096개의 PG를 만든다. PF의 상위 4비트가 모두 1이라는 것은 16진수 첫 자리가 `F`라는 뜻이다(2절). PF의 하위 4비트 16가지와 GE 256가지를 곱하면 4096이다.

::: info PDU2는 정말 "전역 전용"인가
2절은 PDU2를 "목적지를 지정할 수 없는 전역 전용"이라고 했다. ISO 11783-3도 PDU2 형식을 고르면 그 PGN은 특정 목적지로 보낼 수 없다고 적는다. 단, 이것은 <strong>단일 프레임</strong>에 대한 이야기다. 8바이트를 넘는 PDU2 PGN은 TP로 보내는데, TP.CM 메시지 자체는 PDU1이라 DA를 가진다. 그래서 표준의 요청·응답 표는 8바이트를 넘는 PDU2 PGN을 특정 요청에 대해 RTS/CTS로 특정 목적지에 보낸다고 정리한다. 그 표는 [10장](/study/isobus/10-j1939-request-ack)에 옮겨 두었다. TP는 8바이트보다 긴 데이터를 나눠 보내는 방법이고, TP.CM은 그 전송을 열고 닫는 연결 관리 메시지, RTS/CTS는 한 장치에게 보내는 TP 방식이다([15장](/study/isobus/15-tp-bam-cmdt)).
:::

::: details 원문을 가진 독자를 위한 메모
- 필드별 규칙 표의 조항: Priority 5.2.2·Annex A, EDP 5.2.3·Table 3, DP 5.2.4, PF 5.2.5·5.3, PS 5.2.6, SA 5.2.7, 데이터 5.2.8·5.4.1.
- 주소를 여러 개 가질 수 있다는 내용은 Annex A NOTE 2, GE 4096개는 5.2.6 NOTE, PDU2 전역 전용은 5.3.3, 요청·응답 표는 Table 5다.
:::

<small>근거: ISO 11783-3 5.2.1~5.2.8, 5.3.3, 5.4.1, Table 3, Table 5, Annex A</small>

::: tip 핵심 정리
- 29비트 ID는 Priority(3) + EDP(1) + DP(1) + PF(8) + PS(8) + SA(8)로 구성된다. 16진수 ID는 뒤 여섯 자리를 두 자리씩 끊으면 PF, PS, SA이고, 맨 앞 두 자리만 2진수로 풀면 Priority, EDP, DP가 나온다.
- PF < 240이면 PDU1으로 PS는 받는 주소(DA)이고, DA=255로 전역 전송도 가능하다. PF >= 240이면 PDU2로 PS는 GE이고, 전역 전용 브로드캐스트다.
- **PGN** = PF가 >= 240이면 PS 포함, PF < 240이면 PS 제외하여 계산한다. 16진수로는 DP, PF, PS(PDU1이면 00)를 이어 붙인 값이다.
- <strong>SPN</strong>은 PGN 데이터 필드 내 개별 파라미터이며, `실제값 = raw * 분해능 + 오프셋` 공식으로 변환한다. 여러 바이트 값은 LSB가 먼저 오고, `FF`(2바이트면 `FFxx`)는 값 없음이다.
- `18FEEE00#B03204FFFFFFFFFF` 파싱 결과: Priority=6, PGN=65262, SA=0x00, 냉각수 온도=136°C.
:::

::: details 확인 문제
1. (개념) PF 값만 보고 PDU1과 PDU2를 어떻게 구분하는가? 각각 PS 칸은 무엇을 뜻하는가?
2. (읽기) ID `0x0CF00400`을 여섯 칸으로 나누고 PGN을 구하라.
3. (읽기) ID `0x18EA00F9`의 PGN은 얼마이고, 누가 누구에게 보낸 메시지인가?
4. (계산) PGN 65262 메시지의 byte 1이 `0x5A`이면 냉각수 온도는 몇 °C인가? byte 1이 `0xFE`나 `0xFF`이면 어떻게 읽어야 하는가?
5. (계산) 2바이트 SPN이 byte 3~4에 `20 4E`로 실려 있다. 원시값은 10진수로 얼마인가?
6. (만들기) Priority 6인 엔진 ECU(SA `0x00`)가 PGN 65265(Cruise Control/Vehicle Speed)를 보낼 때의 CAN ID를 구하라.
7. (심화) 수신 측이 PS(DA)를 자기 주소 하나와만 비교하면 어떤 문제가 생기는가?

**답 가이드**
1. PF가 240(`0xF0`) 미만이면 PDU1, 이상이면 PDU2다. 16진수로는 PF 첫 자리가 `F`이면 PDU2다. PDU1의 PS는 받는 장치의 주소(DA, 255면 모두에게)이고, PDU2의 PS는 PGN의 일부인 GE다.
2. `0C | F0 | 04 | 00`으로 끊는다. `0x0C` = `000 011 0 0`이므로 Priority 3, EDP 0, DP 0이다. PF `0xF0`(240)이라 PDU2, PS `0x04`는 GE, SA는 `0x00`이다. PGN = 240 × 256 + 4 = 61444(EEC1)다.
3. `18 | EA | 00 | F9`로 끊으면 Priority 6, PF `0xEA`(234)라 PDU1이다. PGN = 234 × 256 = 59904(Request)다. 진단 도구(SA `0xF9`)가 엔진 ECU(DA `0x00`)에게 보낸 요청이다.
4. `0x5A` = 5 × 16 + 10 = 90이고, 90 × 1 - 40 = 50 °C다. `0xFE`는 오류 표시(고장 등으로 값을 줄 수 없음), `0xFF`는 값 없음(Not available)이므로 온도로 계산하지 않는다.
5. LSB가 먼저이므로 byte 4의 `4E`를 앞에 붙여 `0x4E20`이다. 4 × 4096 + 14 × 256 + 2 × 16 + 0 = 20000이다.
6. 65265 ÷ 256 = 254, 나머지 241이므로 PF 254(`0xFE`), PS 241(`0xF1`)이다. PDU2라서 PS는 GE다. Priority 6이면 첫 바이트가 `0x18`이므로 ID는 `0x18FEF100`이다.
7. 컨트롤러 하나가 CF 여러 개를 품어 주소를 여러 개 가질 수 있다. 주소 하나와만 비교하면 두 번째 CF 앞으로 온 메시지를 버리게 된다. DA는 내 주소 집합 또는 전역(255)과 비교해야 한다.
:::

## 다음 챕터

- 다음: [10장 요청과 응답: Request, ACK, Group function](/study/isobus/10-j1939-request-ack)
