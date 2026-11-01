---
title: "Request2, Transfer와 수신·응답 규칙"
description: "한 장치가 여러 장치의 데이터를 신원과 함께 보고하는 Request2·Transfer, 받은 프레임을 분류하는 수신 루틴, 응답 시간 Tr·T3와 재시도 규칙을 익힌다."
date: 2026-04-13
tags: [J1939, ISOBUS, Request2, Transfer, 타임아웃]
prev: /study/isobus/10-j1939-request-ack
next: /study/isobus/12-j1939-address-name
---

# Request2, Transfer와 수신·응답 규칙

::: info 학습 목표
- Request(59904)로는 안 되고 Request2와 Transfer가 필요한 상황을 설명할 수 있다.
- Request2 8바이트와 Byte 4의 비트를 읽고 만들 수 있다.
- Transfer 데이터가 "요청 PGN + (길이, 신원, 데이터) 반복"으로 이뤄진다는 것을 예제로 설명할 수 있다.
- 받은 프레임을 무시할지, 어디에 저장할지 고르는 수신 루틴을 따라갈 수 있다.
- 응답 시간 Tr(0.2 s), 대기 시간 T3(1.25 s), 재시도 2회 규칙으로 요청하는 쪽의 타임아웃을 설계할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [10장 요청과 응답](/study/isobus/10-j1939-request-ack), [9장 J1939 메시지 구조](/study/isobus/09-j1939-message)
- 이 장에서 처음 나오는 말
  - Request2: 응답을 Transfer 형식으로 달라고 지정할 수 있는 확장 요청이다. PGN 51456을 쓴다.
  - Transfer: 여러 장치의 데이터를 장치 신원과 함께 한꺼번에 보고하는 메시지다. PGN 51712를 쓴다.
  - 확장 식별자(extended identifier): 요청할 PGN 데이터의 첫 1~3바이트 값을 미리 정해, 그 하위 기능만 골라 요청하는 필터다.
  - NAME: 장치마다 고유한 64비트 이름표다([12장](/study/isobus/12-j1939-address-name)). Transfer는 그 가운데 바이트 5~8을 신원으로 쓴다.
  - Tr, T3: 응답하는 쪽이 지킬 응답 시간(0.2 s)과 기다리는 쪽이 최소로 기다릴 시간(1.25 s)이다.
  - 브리지: 버스와 버스를 잇는 장치다. 메시지를 넘겨줄 때 시간이 조금 걸린다([21장](/study/isobus/21-niu-network-layer)).
:::

반장이 반 학생들의 숙제를 걷어 선생님께 낼 때, 공책마다 이름이 적혀 있어야 누구 숙제인지 안다. Request2와 Transfer는 장치 하나가 다른 장치들의 데이터까지 모아 보고할 때, 데이터 묶음마다 "누구 것인지"를 붙이는 방법이다. 이 장에서는 이 두 메시지와 함께, 받는 쪽이 프레임을 처리하는 순서와 응답을 얼마나 기다려야 하는지를 본다.

## 1. Request2와 Transfer가 필요한 이유

이 절에서는 [10장](/study/isobus/10-j1939-request-ack)의 Request만으로는 풀리지 않는 상황을 먼저 본다. 결론부터 말하면, 한 장치가 여러 장치 몫의 데이터를 답해야 할 때 데이터마다 주인을 붙일 방법이 필요하다.

CF 하나가 자기 데이터뿐 아니라 다른 CF들의 데이터까지 보고해야 하는 경우가 있다. ISO 11783-3(ISOBUS의 데이터 링크 계층을 정하는 표준 문서)이 드는 예는 ECU Identification, Component ID, Software Identification 같은 PGN이다. 각각 ECU 식별 정보, 부품 식별 정보, 소프트웨어 버전 정보를 담는다([27장](/study/isobus/27-diagnostics-identification)). Request(59904)로는 "누구의 데이터인지"를 구별해 여러 개를 받을 방법이 없다. Request2는 응답에 Transfer PGN을 쓰라고 지정할 수 있고, Transfer는 데이터 세트마다 그 데이터의 주인을 표시한다. Request2 지원은 선택 사항이다.

![위 줄은 VT가 작업기 ECU에 Request로 PGN 65242를 요청하면 ECU가 자기 소프트웨어 버전 SW1.0* 하나만 주인 표시 없이 답하는 경우, 아래 줄은 Request2로 Transfer 응답을 요구하면 ECU가 PGN 뒤에 자신의 신원과 SW1.0*, 맡은 CF의 신원과 SW2.3*을 세트로 붙여 Transfer로 답하는 경우](/images/study-isobus/11-request-vs-request2-light.png)
![위 줄은 VT가 작업기 ECU에 Request로 PGN 65242를 요청하면 ECU가 자기 소프트웨어 버전 SW1.0* 하나만 주인 표시 없이 답하는 경우, 아래 줄은 Request2로 Transfer 응답을 요구하면 ECU가 PGN 뒤에 자신의 신원과 SW1.0*, 맡은 CF의 신원과 SW2.3*을 세트로 붙여 Transfer로 답하는 경우](/images/study-isobus/11-request-vs-request2-dark.png)

그림 읽는 법: 위 줄이 Request, 아래 줄이 Request2다. 작업기 ECU(SA `0x80`)는 자기 소프트웨어 버전과, 자기가 보고를 맡은 하위 CF의 버전을 둘 다 안다. Request로 물으면 ECU는 자기 버전만 답한다. Request2로 "Transfer로 답하라"고 물으면 두 버전을 각각 주인의 신원과 함께 한 메시지에 담아 답한다. 이 예는 5절에서 바이트까지 따라간다.

<small>근거: ISO 11783-3 5.4.7, 5.4.8</small>

## 2. Request2 (PGN 51456)

이 절에서는 Request2 8바이트의 배치와, 응답 방식을 정하는 Byte 4의 비트를 본다.

| 항목 | 값 |
|---|---|
| PF / PS | 201(`0xC9`) / DA (전역 또는 특정) |
| 데이터 길이 | 8바이트 |
| 기본 Priority | 6 |
| 송신 빈도 | 초당 2~3회 이하 권장 |
| 지원하는 CF의 의무 | 특정 목적지로 요청된 PG를 지원하지 않으면 NACK 필수 |

표 읽는 법: PF 201은 240보다 작으므로 Request2도 PDU1이고, PS에 받는 장치의 주소(또는 전역 255)를 적는다. Request(3바이트)와 달리 데이터가 8바이트다. 마지막 행은 Request2를 지원하는 장치라면 [10장](/study/isobus/10-j1939-request-ack)의 Request와 같은 NACK 규칙을 지켜야 한다는 뜻이다.

![Request2 8바이트 배치(Byte 1~3 요청 PGN, Byte 4 특수 지시, Byte 5~7 확장 식별자, Byte 8 예약)와 Byte 4의 비트 8~6 예약, 비트 5~3 확장 식별자 종류, 비트 2~1 Transfer 사용 여부, 그리고 Transfer의 a 요청 PGN 뒤에 b 길이·c CF 신원(NAME 바이트 5~8)·d 데이터가 반복되는 구조](/images/study-isobus/09-request2-transfer-layout-light.png)
![Request2 8바이트 배치(Byte 1~3 요청 PGN, Byte 4 특수 지시, Byte 5~7 확장 식별자, Byte 8 예약)와 Byte 4의 비트 8~6 예약, 비트 5~3 확장 식별자 종류, 비트 2~1 Transfer 사용 여부, 그리고 Transfer의 a 요청 PGN 뒤에 b 길이·c CF 신원(NAME 바이트 5~8)·d 데이터가 반복되는 구조](/images/study-isobus/09-request2-transfer-layout-dark.png)

그림 읽는 법: 맨 위 줄이 Request2의 8바이트다. Byte 1~3은 요청 PGN, Byte 4는 특수 지시, Byte 5~7은 확장 식별자, Byte 8은 예약이다. 가운데 줄은 Byte 4를 비트로 펼친 것이고, 맨 아래 줄은 4절에서 볼 Transfer 데이터의 구조다.

Byte 4(특수 지시)의 비트는 이렇게 나뉜다.

| 비트 | 이름 | 값 |
|---|---|---|
| 8~6 | 예약 | 값 정의 없음 |
| 5~3 | 확장 식별자 종류 | 000 없음(Byte 5~7은 FF), 001 1바이트, 010 2바이트, 011 3바이트, 100~110 예약, 111 동작 안 함 |
| 2~1 | Transfer PGN 사용 | 00 No, 01 Yes, 10 Undefined, 11 Not Allowed |

바이트 안의 비트 번호는 오른쪽(가장 낮은 자리)이 Bit 1, 왼쪽이 Bit 8이다. 2진수 `111 000 01`을 예로 들면, 왼쪽 세 자리 `111`이 Bit 8~6, 가운데 `000`이 Bit 5~3, 오른쪽 `01`이 Bit 2~1이다. "111 동작 안 함"은 해당 사항이 없다는 값이다.

확장 식별자는 "요청한 PGN의 데이터 첫 1~3바이트가 이 값인 것"을 고르는 필터다. 1바이트형이면 Byte 5가 요청 PGN의 data byte 1과 맞춰질 값이고, 2·3바이트형이면 Byte 6·7이 data byte 2·3과 맞춰진다. 쓰지 않는 바이트는 FF다. Group function PG의 특정 하위 기능을 요청할 때 쓴다. 확장 식별자를 쓴 Request2에 Acknowledgement로 답할 때는 [10장](/study/isobus/10-j1939-request-ack)에서 본 control 128~163을 쓴다.

Group function을 떠올리면 쓰임이 보인다. Group function은 PGN 하나 안에서 첫 데이터 바이트로 기능을 고른다([10장](/study/isobus/10-j1939-request-ack)). 확장 식별자는 바로 그 첫 바이트(들)를 지정해 "이 PGN 가운데 이 기능의 메시지를 보내 달라"고 요청하는 수단이다.

Use Transfer = 00이면 Request(59904)와 효과가 같고, 응답도 Transfer 없이 59904에 대한 응답과 똑같이 보낸다. 확장 식별자 종류 000은 "이 장치가 새 Request2 특수 지시 기능을 지원한다"는 표시도 겸한다.

<small>근거: ISO 11783-3 5.4.7</small>

## 3. Request2 바이트 예제

이 절에서는 Request2 두 개를 바이트 단위로 만든다. 하나는 Transfer 응답을 요구하는 전역 요청, 하나는 확장 식별자를 쓴 특정 요청이다.

VT(SA `0x26`)가 Software Identification(PGN 65242 = `0x00FEDA`)을 Transfer로 받으려고 전역 Request2를 보낸다. VT(Virtual Terminal)는 운전석의 작업기 조작 화면이다.

`18C9FF26#DAFE00E1FFFFFFFF`

ID를 두 자리씩 끊으면 `18 | C9 | FF | 26`이다. Priority 6, PF `0xC9`(201, Request2), DA `0xFF`(전역), SA `0x26`(VT)이다.

| 바이트 | 값 | 해석 |
|---|---|---|
| 1~3 | `DA FE 00` | 요청 PGN 65242 |
| 4 | `E1` = `111 000 01` | 예약 111, 확장 식별자 없음(000), Transfer 사용 Yes(01) |
| 5~7 | `FF FF FF` | 확장 식별자가 없으므로 FF |
| 8 | `FF` | 예약 |

Byte 4를 한 번 더 풀면, `E1`은 2진수 `1110 0001`이고 이것을 3·3·2비트로 다시 묶은 것이 `111 000 01`이다.

표준은 Request2의 예약 비트·바이트에 넣을 값을 명시하지 않는다. 여기서는 Acknowledgement가 예약 바이트를 FF로 보내는 관례([10장](/study/isobus/10-j1939-request-ack))를 따라 1로 채웠다(가정).

두 번째 예는 확장 식별자를 쓴 특정 요청이다. VT가 SA `0x80`에게 "첫 데이터 바이트가 `0x12`인 Proprietary A 메시지"를 요청한다. ID는 `0x18C98026`, 데이터는 `00 EF 00 E4 12 FF FF FF`다. Byte 4 `E4` = `111 001 00`(1바이트 확장 식별자, Transfer No)이고 Byte 5가 `0x12`다. SA `0x80`이 이 메시지를 보내지 않는다면 [10장](/study/isobus/10-j1939-request-ack)에서 본 `81 12 FF FF 26 00 EF 00`(control 129)로 답한다.

이 요청도 한 단계씩 읽어 보자.

1. Byte 1~3 `00 EF 00`을 거꾸로 붙이면 `0x00EF00` = 61184, 제조사 독점 메시지 Proprietary A다([10장](/study/isobus/10-j1939-request-ack)).
2. Byte 4 `E4`는 2진수 `1110 0100`이고, 3·3·2로 묶으면 `111` | `001` | `00`이다. 확장 식별자는 1바이트, Transfer는 쓰지 않는다.
3. Byte 5 `12`가 그 1바이트 확장 식별자다. Byte 6~7은 쓰지 않으므로 FF다.

<small>근거: ISO 11783-3 5.4.5, 5.4.7</small>

## 4. Transfer (PGN 51712)

이 절에서는 Request2에 대한 응답인 Transfer의 데이터 구조를 본다.

| 항목 | 값 |
|---|---|
| PF / PS | 202(`0xCA`) / DA (특정 또는 전역) |
| 데이터 길이 | 9~1785바이트 (multi-packet) |
| 기본 Priority | 6 |
| 송신 시점 | "Use Transfer PGN" = 01인 Request2를 받았을 때 |

PF 202도 240보다 작으므로 PDU1이다. 데이터가 9바이트 이상이므로 Transfer는 늘 여러 프레임으로 나눠(multi-packet) TP로 보낸다([15장](/study/isobus/15-tp-bam-cmdt)).

데이터는 a 하나 뒤에 (b, c, d)가 반복되는 구조다.

- a (Byte 1~3): Request2가 요청한 PGN
- b (1바이트): 이 데이터 세트의 길이. 길이 바이트 자신 + 신원 4바이트 + 데이터이므로 b = 5 + d의 길이
- c (4바이트): 이 데이터의 주인인 CF의 신원. NAME의 바이트 5~8과 같은 배치다(Function Instance·ECU Instance, Function, Device Class, Self Configurable·Industry Group·Device Class Instance)
- d: 그 CF에 대한, 요청된 PGN의 데이터

NAME은 [12장](/study/isobus/12-j1939-address-name)에서 자세히 본다. 여기서는 c를 "어떤 기능(Function)을 하는 몇 번째(Instance) 장치이고, 어떤 기계 종류(Device Class)와 산업군(Industry Group)에 속하는가"를 담은 4바이트로 보면 된다.

규칙은 두 가지다. 응답하는 CF는 59904 요청을 받았을 때 보고했을 정보를 <strong>첫 데이터 세트</strong>로 보내야 한다. 데이터 세트가 하나뿐이어도 Transfer로 응답해야 한다.

<small>근거: ISO 11783-3 5.4.8</small>

## 5. Transfer 바이트 예제: Request2부터 BAM까지

3절의 전역 Request2에 대한 응답을 바이트 하나까지 만들어 본다. 마지막에는 이 응답이 TP로 어떻게 잘려 나가는지도 본다.

위 전역 Request2에 SA `0x80`인 작업기 ECU가 답한다. 이 ECU는 자신과, 자신이 보고를 맡은 CF 하나의 소프트웨어 버전을 안다(아래 값은 예시).

| 세트 | c (신원) | d (데이터) | b |
|---|---|---|---|
| 1 (자신) | `00 81 08 A0` | `"SW1.0*"` = `53 57 31 2E 30 2A` | 5 + 6 = 11 (`0x0B`) |
| 2 (맡은 CF) | `08 81 08 A0` | `"SW2.3*"` = `53 57 32 2E 33 2A` | 11 |

c의 `00 81 08 A0`은 Function Instance 0·ECU Instance 0, Function `0x81`, Device Class 4(Byte 7 = 4 × 2 + 예약 비트 0), Self Configurable 1·Industry Group 2·Device Class Instance 0을 담은 예시 값이다. 두 번째 세트는 Function Instance만 1이다(`08`).

신원 4바이트를 비트로 풀면 다음과 같다.

- `00` = `00000 000`: 위 5비트가 Function Instance 0, 아래 3비트가 ECU Instance 0이다.
- `81`: Function `0x81`이다.
- `08` = `0000100 0`: 위 7비트가 Device Class 4, 맨 아래 1비트가 예약 0이다. 그래서 4 × 2 = 8이다.
- `A0` = `1 010 0000`: Self Configurable 1, Industry Group 2(농업·임업 장비), Device Class Instance 0이다.
- 두 번째 세트의 `08` = `00001 000`: Function Instance 1, ECU Instance 0이다.

d는 글자 `SW1.0*`를 ASCII 코드로 적은 것이다(`S` = `53`, `W` = `57`, `1` = `31`, `.` = `2E`, `0` = `30`, `*` = `2A`). 6글자이므로 6바이트이고, b = 1(길이 바이트) + 4(신원) + 6(데이터) = 11이다.

Transfer 데이터는 3 + 11 + 11 = 25바이트다. 요청이 전역이었으므로 [10장의 응답 규칙](/study/isobus/10-j1939-request-ack)에 따라 BAM으로 보낸다. 25바이트는 TP.DT 4개다.

1. 길이: a(3) + 세트 1(11) + 세트 2(11) = 25바이트다. 8바이트를 넘으므로 TP를 쓴다.
2. 방식: 요청이 전역이었으므로 응답도 전역, 즉 모두에게 보내는 BAM이다.
3. 조각 수: 조각 프레임(TP.DT) 하나에 데이터를 7바이트씩 실으므로 25 ÷ 7 = 3.57…을 올림해 4개다. 마지막 조각은 4바이트만 차고 나머지 3바이트는 FF로 채운다.
4. 알림 프레임: BAM은 조각을 보내기 전에 TP.CM_BAM 프레임으로 "크기 25바이트, 조각 4개, PGN 51712를 보낸다"고 알린다.

| 프레임 | 데이터 |
|---|---|
| TP.CM_BAM | `20 19 00 04 FF 00 CA 00` (크기 25, 패킷 4, PGN 51712) |
| TP.DT 1 | `01 DA FE 00 0B 00 81 08` |
| TP.DT 2 | `02 A0 53 57 31 2E 30 2A` |
| TP.DT 3 | `03 0B 08 81 08 A0 53 57` |
| TP.DT 4 | `04 32 2E 33 2A FF FF FF` |

TP.CM_BAM의 바이트를 풀면, `20`은 BAM을 뜻하는 control 값 32, `19 00`은 크기 25(LSB 먼저), `04`는 조각 수, `FF`는 예약, `00 CA 00`은 PGN 51712(LSB 먼저)다. 각 TP.DT의 첫 바이트 `01`~`04`는 조각의 순서 번호이고, 나머지 7바이트는 Transfer 데이터 25바이트를 앞에서부터 차례로 자른 것이다.

BAM과 TP.DT의 규칙은 [15장 Transport Protocol 기초](/study/isobus/15-tp-bam-cmdt)에서 자세히 다룬다. ISO 11783-3이 드는 예도 같은 흐름이다. 엔진이 트랙터와 트레일러의 VIN을 둘 다 안다면, Use Transfer = 01인 전역 Request2에는 두 VIN을 Transfer에 담아 BAM으로 보내고, 00이었다면 트랙터 VIN만 Transfer 없이 BAM으로 보낸다. VIN(Vehicle Identification Number)은 차량마다 붙는 고유 번호다.

아래 코드는 3절과 이 절의 바이트를 함수로 다시 만들어 확인한다. `le(v, n)`은 값 `v`를 `n`바이트로 LSB부터 쪼개는 함수다.

::: details 파이썬으로 검산: Request2 만들기, Transfer 만들고 풀기
```python
import math


def le(v, n):
    return [(v >> (8 * i)) & 0xFF for i in range(n)]


def request2(pgn, use_transfer, ext=None, ext_len=0):
    """예약 비트·바이트는 1(FF)로 채운다고 가정(5.4.7은 값을 명시하지 않음)."""
    b4 = (0b111 << 5) | (ext_len << 2) | (0b01 if use_transfer else 0b00)
    ext_bytes = (le(ext, ext_len) + [0xFF] * (3 - ext_len)) if ext_len else [0xFF] * 3
    return le(pgn, 3) + [b4] + ext_bytes + [0xFF]


assert request2(65242, True) == [0xDA, 0xFE, 0x00, 0xE1, 0xFF, 0xFF, 0xFF, 0xFF]
assert request2(61184, False, ext=0x12, ext_len=1) == [0x00, 0xEF, 0x00, 0xE4, 0x12, 0xFF, 0xFF, 0xFF]


def identity(func_inst, ecu_inst, function, dev_class, ind_group, dci, self_cfg):
    """NAME 바이트 5~8과 같은 배치 (Part 3 5.4.8, Part 5 Table 1). 예약 비트는 0."""
    return [(func_inst << 3) | ecu_inst, function, dev_class << 1,
            (self_cfg << 7) | (ind_group << 4) | dci]


def transfer(pgn, datasets):
    out = le(pgn, 3)
    for ident, payload in datasets:
        out += [5 + len(payload)] + ident + list(payload)
    return out


def decode_transfer(d):
    pgn, i, sets = d[0] | d[1] << 8 | d[2] << 16, 3, []
    while i < len(d):
        n = d[i]
        sets.append((bytes(d[i + 1:i + 5]).hex(" "), bytes(d[i + 5:i + n])))
        i += n
    return pgn, sets


tr = transfer(65242, [(identity(0, 0, 0x81, 4, 2, 0, 1), b"SW1.0*"),
                      (identity(1, 0, 0x81, 4, 2, 0, 1), b"SW2.3*")])
assert len(tr) == 25
assert decode_transfer(tr) == (65242, [("00 81 08 a0", b"SW1.0*"), ("08 81 08 a0", b"SW2.3*")])

bam = [0x20] + le(len(tr), 2) + [math.ceil(len(tr) / 7), 0xFF] + le(51712, 3)
assert bam == [0x20, 0x19, 0x00, 0x04, 0xFF, 0x00, 0xCA, 0x00]
for s in range(math.ceil(len(tr) / 7)):
    chunk = tr[s * 7:(s + 1) * 7]
    print(" ".join(f"{b:02X}" for b in [s + 1] + chunk + [0xFF] * (7 - len(chunk))))
```

출력되는 네 줄이 위 표의 TP.DT 1~4와 같다.
:::

<small>근거: ISO 11783-3 5.4.8, 5.10</small>

## 6. 받는 쪽의 처리 규칙과 수신 루틴 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

지금까지는 보내는 쪽의 규칙을 봤다. 이 절에서는 받는 쪽이 지켜야 할 처리 속도와, 프레임을 받을 때마다 무시할지 어디에 저장할지 고르는 전형적인 순서를 본다.

### 100% 부하에서도 잃지 않는다

컨트롤러는 데이터 링크가 100% 사용률일 때도 메시지를 잃지 않을 만큼 빠르게 처리해야 한다(shall). 버스가 한산할 때 프레임이 연달아 와도 마찬가지다. 이것은 응답을 즉시 만들라는 뜻이 아니라, 새 메시지가 이전 메시지를 덮어쓰지 않게 하라는 뜻이다. 갱신이 잦고 지연 요구가 엄격한 데이터는 가능하면 하드웨어 메시지 필터를 쓸 수 있게 설계하라는 권고도 있다.

100% 사용률은 버스가 쉬는 틈 없이 프레임을 계속 나르는 상태다. 하드웨어 메시지 필터는 CAN 칩이 ID를 보고 필요 없는 프레임을 미리 걸러 주는 기능이다([5장](/study/isobus/05-can-arbitration)).

### 전형적인 수신 루틴

ISO 11783-3은 참고용으로, CAN 칩이 프레임을 받았을 때 어디에 저장할지 정하는 전형적인 순서를 보여 준다.

![프레임을 받으면 Priority는 보지 않고, PF가 234(Request)이면 DA가 전역이거나 내 주소일 때 request queue에 ID 4바이트와 데이터 3바이트를 넣고, 아니면 PDU1은 DA가 전역이거나 내 주소일 때만, PDU2는 그대로 관심 PGN 점프 테이블을 거쳐 SA가 특별 관심 대상이면 전용 버퍼(데이터 8바이트), 아니면 순환 큐(ID 4 + 데이터 8 = 12바이트)에 넣는 흐름](/images/study-isobus/09-receive-routine-light.png)
![프레임을 받으면 Priority는 보지 않고, PF가 234(Request)이면 DA가 전역이거나 내 주소일 때 request queue에 ID 4바이트와 데이터 3바이트를 넣고, 아니면 PDU1은 DA가 전역이거나 내 주소일 때만, PDU2는 그대로 관심 PGN 점프 테이블을 거쳐 SA가 특별 관심 대상이면 전용 버퍼(데이터 8바이트), 아니면 순환 큐(ID 4 + 데이터 8 = 12바이트)에 넣는 흐름](/images/study-isobus/09-receive-routine-dark.png)

그림 읽는 법: 맨 위 "프레임 수신"에서 출발해 질문 상자마다 예·아니오를 따라간다. 파란 상자는 프레임을 저장하는 곳이고, 회색 "무시" 상자는 버리는 곳이다.

1. PF가 234(Request)이면, DA가 전역이거나 내 주소일 때만 request queue(요청 대기열)에 넣는다.
2. Request가 아니고 PDU1이면, DA가 전역이거나 내 주소일 때만 다음 단계로 간다. PDU2는 바로 다음 단계로 간다.
3. 관심 있는 PGN인지 점프 테이블로 확인한다. 관심 없으면 버린다.
4. 보낸 장치(SA)가 특별히 관심 있는 상대이면 전용 버퍼에, 아니면 순환 큐에 넣는다.

용어를 풀면 이렇다. 큐(queue)는 들어온 순서대로 쌓았다가 꺼내는 대기열이고, 순환 큐는 끝에 닿으면 처음으로 돌아가 다시 쓰는 큐다. 점프 테이블은 값(여기서는 PGN)마다 처리할 곳을 미리 적어 둔 표다. 버퍼는 데이터를 잠시 담아 두는 메모리 칸이다. 인터럽트는 프레임이 도착하는 순간 CPU가 하던 일을 멈추고 실행하는 짧은 처리 루틴이다.

이 루틴에서 읽어 낼 설계 원칙은 다음과 같다.

- <strong>인터럽트에서는 분류와 저장만 한다.</strong> 응답은 request queue를 나중에 처리하면서 만든다. 앞에서 처리 속도 요구가 "즉시 응답하라는 뜻이 아니다"라고 한 것과 맞물린다.
- <strong>Priority는 처음부터 버린다.</strong>
- <strong>점프 테이블로 관심 PGN만 고른다.</strong> 관심 없는 PGN은 저장하지 않는다.
- <strong>SA에 따라 저장 방식을 나눈다.</strong> 원문은 특별 관심 SA의 데이터 8바이트는 전용 버퍼에, 나머지는 ID와 데이터 12바이트를 순환 큐에 넣는다. 최신값만 필요한 상대는 덮어쓰는 버퍼로, 순서와 개수가 중요한 메시지는 큐로 받는 구분으로 읽을 수 있다(추론).

표준의 의사코드는 Request가 아닌 PDU1 분기에서 DA를 내 주소와 비교하지 않는다. 그러나 다른 조항은 DA가 가리키지 않는 다른 컨트롤러는 그 메시지를 무시해야 한다고(should) 적으므로, 그림과 아래 코드처럼 DA가 내 주소 집합이나 전역일 때만 받도록 거르는 편이 맞다. 남의 메시지를 일부러 봐야 하는 NIU나 로거는 예외다(추론).

아래 함수는 그림의 순서를 코드로 옮긴 것이다. `tests`의 각 줄은 (CAN ID, 기대하는 처리) 쌍이다. 예를 들어 `0x0CFE481C`와 `0x18FE481C`는 Priority만 다른 같은 메시지이므로 처리도 같다. `MY_ADDRESSES`가 값 하나가 아니라 집합인 이유는 [9장](/study/isobus/09-j1939-message)에서 본 "DA 비교는 집합으로" 규칙 때문이다.

::: details 파이썬: 전형적 수신 루틴
```python
REQUEST_PF, GLOBAL = 0xEA, 0xFF
MY_ADDRESSES = {0x80, 0x81}           # 한 컨트롤러가 주소를 여러 개 가질 수 있다 (Annex A NOTE 2)
PGN_OF_INTEREST = {65096, 61184, 59392}
SA_OF_SPECIAL_INTEREST = {0x1C}


def pgn_of(can_id):
    dp, pf, ps = (can_id >> 24) & 1, (can_id >> 16) & 0xFF, (can_id >> 8) & 0xFF
    return (dp << 16) | (pf << 8) | (ps if pf >= 240 else 0)


def on_receive(can_id, data):
    """Part 3 Annex A의 전형적 수신 루틴. Priority 비트는 보지 않는다."""
    pf, ps, sa = (can_id >> 16) & 0xFF, (can_id >> 8) & 0xFF, can_id & 0xFF
    if pf == REQUEST_PF:
        if ps == GLOBAL or ps in MY_ADDRESSES:
            return "request queue"             # ID 4바이트 + 데이터 3바이트
        return "ignore"
    if pf < 240 and ps != GLOBAL and ps not in MY_ADDRESSES:
        return "ignore"                        # 5.2.6: 다른 컨트롤러는 무시
    if pgn_of(can_id) not in PGN_OF_INTEREST:
        return "ignore"
    if sa in SA_OF_SPECIAL_INTEREST:
        return "dedicated buffer"              # 데이터 8바이트
    return "circular queue"                    # ID 4 + 데이터 8 = 12바이트


tests = [
    (0x18EA8126, "request queue"),     # 나(0x81)에게 온 특정 요청
    (0x18EA2726, "ignore"),            # 남(0x27)에게 온 특정 요청
    (0x18EAFF26, "request queue"),     # 전역 요청
    (0x0CFE481C, "dedicated buffer"),  # PDU2, 관심 SA
    (0x18FE481C, "dedicated buffer"),  # 같은 PGN, Priority만 다름
    (0x0CFE4823, "circular queue"),    # PDU2, 일반 SA
    (0x18EF8023, "circular queue"),    # Proprietary A, DA = 나(0x80)
    (0x18EF2723, "ignore"),            # Proprietary A, DA = 남
    (0x18EFFF23, "circular queue"),    # Proprietary A, 전역
    (0x18FEEE00, "ignore"),            # 관심 없는 PGN
]
for cid, expected in tests:
    assert on_receive(cid, [0] * 8) == expected, hex(cid)
```
:::

::: details 원문을 가진 독자를 위한 메모
- 수신 루틴은 ISO 11783-3 Annex A(참고)다. Priority를 보지 않는다는 내용은 Annex A NOTE 1, 주소를 여러 개 가질 수 있다는 내용은 NOTE 2다.
- 본문의 "다른 조항"은 DA가 가리키지 않는 컨트롤러는 무시해야 한다(should)는 5.2.6이다.
- 100% 부하 처리 요구는 5.12, 하드웨어 필터 권고는 5.13.1이다.
:::

<small>근거: ISO 11783-3 5.2.6, 5.12, 5.13.1, Annex A</small>

## 7. 응답 시간, 재시도, 필수 응답

요청을 보낸 뒤 얼마나 기다려야 할까? 너무 짧으면 멀쩡한 응답을 놓치고, 너무 길면 고장을 늦게 알아챈다. 이 절에서는 표준이 정한 두 시간 값과 재시도 횟수를 본다.

### Tr과 T3

| 값 | 의미 |
|---|---|
| Tr = 0.2 s | 응답을 요구받은 모든 컨트롤러는 이 시간 안에 응답해야 한다(shall) |
| T3 = 1.25 s | 응답을 기다리는 모든 컨트롤러는 포기하거나 재시도하기 전에 최소 이만큼 기다려야 한다(shall) |

쉽게 말하면 Tr은 답하는 쪽의 마감 시간(200 ms)이고, T3는 묻는 쪽이 참고 기다려야 하는 최소 시간(1250 ms)이다. T3가 Tr보다 훨씬 긴 것은 메시지가 오가는 길에서 생기는 지연까지 넉넉히 감안하기 때문이다.

특정 응용은 다른 값을 쓸 수 있다. 고속 제어 메시지라면 20 ms 응답을 기대할 수 있고, 그렇게 빨리 답하려면 버퍼에 쌓인 송신 메시지의 순서를 바꿔야 할 수도 있다. 최소 응답 시간 제한은 없다.

T3가 왜 1.25 s인지는 표준이 드는 예로 설명할 수 있다. 브리지 하나의 최대 전달 지연이 50 ms이고, 트랙터 1 + 트레일러 5 + 돌리 4로 브리지가 10개면 한 방향 네트워크 지연이 500 ms다. 여기에 타임아웃 마진 50 ms를 둔다. 원문은 합산식을 적지 않지만, 요청이 가는 500 ms + 응답 시간 Tr 200 ms + 응답이 오는 500 ms + 마진 50 ms를 더하면 정확히 1250 ms가 된다.

돌리(dolly)는 트레일러 여러 대를 이어 끌 때 사이에 넣는 바퀴 달린 연결 대차다. 차량마다 버스가 따로 있고, 브리지가 그 사이를 잇는다고 보면 된다. 계산을 단계로 나누면 다음과 같다.

1. 요청이 가는 길: 브리지 10개 × 50 ms = 500 ms
2. 상대가 답을 만드는 시간: Tr = 200 ms
3. 응답이 돌아오는 길: 다시 500 ms
4. 여유(마진): 50 ms
5. 합계: 500 + 200 + 500 + 50 = 1250 ms = T3

![정상 응답은 요청 뒤 Tr 200 ms 안에 오고, 무응답이면 T3 1.25 s 간격으로 요청을 세 번 보낸 뒤 3.75 s에 포기하며, T3는 요청 편도 500 ms(브리지 10개 x 50 ms)와 Tr 200 ms, 응답 편도 500 ms, 마진 50 ms를 더한 1250 ms인 타이밍](/images/study-isobus/09-request-timing-light.png)
![정상 응답은 요청 뒤 Tr 200 ms 안에 오고, 무응답이면 T3 1.25 s 간격으로 요청을 세 번 보낸 뒤 3.75 s에 포기하며, T3는 요청 편도 500 ms(브리지 10개 x 50 ms)와 Tr 200 ms, 응답 편도 500 ms, 마진 50 ms를 더한 1250 ms인 타이밍](/images/study-isobus/09-request-timing-dark.png)

그림 읽는 법: 가로축이 시간(초)이다. 맨 위 줄은 정상 응답으로, 요청 뒤 200 ms 안에 응답이 온다. 가운데 줄은 무응답으로, 1.25 s마다 요청을 다시 보내 세 번 보낸 뒤 3.75 s에 포기한다. 맨 아래 줄은 위 다섯 단계의 T3 계산을 막대로 그린 것이다.

### 재시도

응답 타임아웃 안에 응답(PG 또는 Acknowledgement)이 없으면 같은 Request를 다시 보낼 수 있다. 재시도는 2회로 제한하는 것이 권장되므로 요청은 최대 3번이다. 그래도 응답이 없으면 같은 정보 요청을 포기하거나, 초가 아니라 분 단위로 오래 기다렸다가 다시 시도한다. Request2도 같은 규칙이다. T3 = 1.25 s를 적용하면 첫 요청부터 포기까지 최소 3.75 s다.

3.75 s는 1.25 s × 3이다. 요청 1을 보내고 1.25 s, 요청 2를 보내고 1.25 s, 요청 3을 보내고 1.25 s를 기다린 결과다.

Cannot Respond(control 3)는 "지원하지만 지금은 바쁘니 나중에 다시 요청하라"는 뜻이다. 얼마 뒤에 다시 요청할지는 원문에 없다.

### 요청 스케줄링

요청을 언제 보낼지에 대한 권고도 있다.

- 요청하려던 정보가 요청을 보내기 전에 이미 들어왔다면 요청을 취소한다. 원문의 예는 요청 예정 시각 50 ms 전에 정보가 들어온 경우다.
- 브로드캐스트가 권장되는 PG는 요청하지 않는다. 권장 브로드캐스트 주기가 특별한 필요에 비해 너무 느린 경우는 예외다.
- 주기적으로 브로드캐스트하는 PGN은 대부분 전역 목적지로 보내는 것이 바람직하다.

아래 함수는 시도마다 응답이 몇 초 뒤에 왔는지(또는 오지 않았는지)를 받아, 몇 번째 요청에서 응답을 받았는지와 첫 요청부터 걸린 시간을 돌려준다. 두 번째 `assert`는 첫 요청이 무응답이고 두 번째 요청 뒤 0.18 s에 응답이 온 경우로, 1.25 + 0.18 = 1.43 s다.

::: details 파이썬: 요청 재시도 타이밍
```python
T3, RETRIES = 1.25, 2


def request_outcome(response_delays):
    """시도별 응답 지연(초) 또는 None(무응답) -> (결과, 첫 요청부터 경과 시간)"""
    t = 0.0
    for attempt in range(1 + RETRIES):
        delay = response_delays[attempt] if attempt < len(response_delays) else None
        if delay is not None and delay <= T3:
            return (f"{attempt + 1}번째 요청에서 응답", round(t + delay, 3))
        t += T3
    return ("포기(또는 분 단위로 기다린 뒤 다시)", t)


assert request_outcome([0.15]) == ("1번째 요청에서 응답", 0.15)
assert request_outcome([None, 0.18]) == ("2번째 요청에서 응답", 1.43)
assert request_outcome([None, None, None]) == ("포기(또는 분 단위로 기다린 뒤 다시)", 3.75)

bridge = 50 * 10                                   # 편도 지연 (5.13.3 EXAMPLE)
assert bridge + 200 + bridge + 50 == 1250          # = T3
```
:::

::: warning 구현 함정: 전역 요청 뒤의 침묵
전역 요청에는 NACK도 ACK도 오지 않는다. 그래서 전역 요청 뒤 T3 동안 아무 응답이 없다는 것은 "그 PG를 송신하는 CF가 지금 없다"는 뜻이지 "요청이 거절됐다"는 뜻이 아니다. 반대로 특정 요청에 T3까지 아무것도 오지 않으면 상대가 규칙(미지원이면 NACK 필수)을 어겼거나 버스에 없다는 신호다. 두 경우의 재시도·진단 로직을 분리해 두는 것이 좋다(추론).
:::

<small>근거: ISO 11783-3 5.4.3, 5.4.5, 5.4.7, 5.13.2~5.13.5</small>

::: tip 핵심 정리
- Request2와 Transfer로 한 CF가 여러 CF의 데이터를 신원 4바이트(NAME 바이트 5~8)와 함께 보고한다. Use Transfer = 00이면 Request와 같다.
- Request2는 8바이트이고, Byte 4의 비트로 확장 식별자 종류와 Transfer 사용 여부를 정한다. 확장 식별자는 요청 PGN의 첫 1~3바이트를 고르는 필터다.
- Transfer 데이터는 요청 PGN 뒤에 (길이, 신원, 데이터) 세트가 반복된다. 길이 = 5 + 데이터 길이이고, 9바이트 이상이므로 TP로 보낸다.
- 수신 측은 Priority를 무시하고, DA는 내 주소 집합 또는 전역과 비교한다. 받은 프레임은 분류·저장만 하고 응답은 나중에 만든다.
- 응답은 Tr 0.2 s 안에 하고, 기다리는 쪽은 T3 1.25 s 이상 기다리며, 재시도는 2회(총 3회)까지다.
:::

::: details 확인 문제
1. (개념) Request(59904) 대신 Request2를 써야 하는 상황은 언제인가?
2. (읽기) Request2의 Byte 4가 `E1`이다. 확장 식별자 종류와 Transfer 사용 여부는?
3. (계산) Transfer로 데이터 세트 하나(신원 4바이트, 데이터 10바이트)를 보낸다. b(길이)와 Transfer 데이터 전체 길이는?
4. (디코딩) VT가 `18C98026#00EF00E412FFFFFF`를 보냈고 곧바로 `18E82680#8112FFFF2600EF00`을 받았다. 두 프레임을 해석하라.
5. (시나리오) TC(Task Controller, 작업 지시와 기록을 맡는 장치) 클라이언트를 만들면서 부팅 직후 어떤 PGN을 전역으로 요청한다. 1초 기다려 응답이 없으면 "NACK도 없으니 실패"로 기록하고, 200 ms마다 같은 요청을 무기한 반복하도록 했다. 표준과 어긋나는 점을 모두 찾아라.

**답 가이드**
1. CF 하나가 자기 데이터뿐 아니라 다른 CF들의 데이터까지 보고해야 할 때다(예: ECU 식별, Component ID, Software Identification). Request로는 데이터마다 주인을 구별할 수 없지만, Request2로 Transfer 응답을 요구하면 데이터 세트마다 주인의 신원이 붙는다.
2. `E1` = `111 000 01`이다. 예약 111, 확장 식별자 종류 000(없음, Byte 5~7은 FF), Transfer 사용 01(Yes)이다.
3. b = 1 + 4 + 10 = 15(`0x0F`)다. 전체는 요청 PGN 3바이트 + 15 = 18바이트이고, 8바이트를 넘으므로 TP로 보낸다.
4. 첫 프레임은 VT(`0x26`)가 SA `0x80`에게 보낸 특정 Request2다. 요청 PGN 61184(Proprietary A), Byte 4 `E4` = 확장 식별자 1바이트·Transfer No, 확장 식별자 `0x12`다. 두 번째는 `0x80`의 Acknowledgement로 control 129 = 확장 1바이트형 NACK, 확장 식별자 `0x12`, 주소 `0x26`, PGN 61184다. 첫 바이트가 `0x12`인 Proprietary A 메시지는 보내지 않는다는 답이다.
5. 전역 요청에는 NACK이 오지 않으므로 침묵을 "실패"로 볼 근거가 없다. 기다림은 1초가 아니라 최소 T3 1.25 s여야 한다. 200 ms 간격 반복은 초당 5회로 "초당 2~3회 이하" 권고를 넘고, 재시도는 2회(총 3회)로 제한한 뒤 포기하거나 분 단위로 기다려야 한다.
:::

## 다음 챕터

- 다음: [12장 주소와 NAME: 누가 보냈는지 알아보는 법](/study/isobus/12-j1939-address-name)
