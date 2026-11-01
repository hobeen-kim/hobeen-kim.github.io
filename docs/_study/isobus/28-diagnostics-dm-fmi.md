---
title: "진단 (2): DM1·DM2·DM3, FMI, Functionalities"
description: "고장 코드 메시지 DM1·DM2·DM3의 바이트 배치와 송신 규칙, 알맞은 FMI를 고르고 읽는 법, CF가 지원 기능을 알리는 functionalities 메시지를 바이트 단위로 익힌다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, Diagnostics, DM1, FMI]
prev: /study/isobus/27-diagnostics-identification
next: /study/isobus/29-vt-basics
---

# 진단 (2): DM1·DM2·DM3, FMI, Functionalities

::: info 학습 목표
- DTC 4바이트를 비트 단위로 풀어 SPN, FMI, CM, OC를 구할 수 있다.
- DM1을 언제 보내야 하는지(활성이 되는 순간, 1초 주기, 해제되는 순간) 판단할 수 있다.
- DM3로 고장 기록을 지우고, 지워졌는지 확인하는 절차를 설명할 수 있다.
- 값이 놓인 영역과 방송 값 처리 방식으로 알맞은 FMI를 고를 수 있다.
- functionalities 메시지를 바이트 단위로 인코딩·디코딩할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [27장 진단 (1)](/study/isobus/27-diagnostics-identification), [15장 Transport Protocol 기초](/study/isobus/15-tp-bam-cmdt), [10장 요청과 응답](/study/isobus/10-j1939-request-ack)
- 이 장에서 처음 나오는 말
  - OC(Occurrence Count): 같은 고장이 몇 번 일어났는지 센 횟수.
  - CM(SPN Conversion Method): SPN을 바이트에 담는 방식을 표시하는 비트. ISOBUS에서는 0으로 둔다.
  - error indicator: "센서나 장치 오류로 지금은 올바른 값을 줄 수 없다"는 특수값. 1 byte 값이면 `FE`다.
  - functionality: UT(VT 기능), TC-BAS(기본 TC 기능)처럼 AEF가 정한 기능 단위.
  - generation: 같은 functionality의 세대 번호. 숫자가 클수록 나중 세대다.
:::

[27장](/study/isobus/27-diagnostics-identification)에서 고장 코드가 SPN(어디가)과 FMI(어떻게)의 조합이라는 것을 봤다. 이 장은 계기판 경고등에 빗대면 경고등이 언제 켜지고 꺼지는지(DM1 송신 규칙), 경고등 옆에 찍히는 코드가 바이트로 어떻게 생겼는지(DTC), 그 코드가 무슨 뜻인지(FMI)를 차례로 본다. 끝으로 장치가 "나는 이런 기능을 지원한다"고 알리는 functionalities 메시지를 본다.

## 1. DM1·DM2·DM3 바이트와 송신 규칙

[27장](/study/isobus/27-diagnostics-identification)에서 DM1~DM3의 역할을 봤다. 여기서는 바이트 배치, 언제 보내는가, 클리어가 됐는지 어떻게 아는가를 표준 규정 수준으로 내려간다. DTC(Diagnostic Trouble Code)는 SPN·FMI·발생 횟수를 4 byte로 묶은 고장 코드다.

### DTC 4 byte 패킹

표 읽는 법부터 짚는다. Byte 번호는 1부터 센다. 바이트 안의 bit 8이 가장 높은 자리, bit 1이 가장 낮은 자리다. 여러 바이트에 걸친 값은 낮은 자리 바이트가 먼저 온다(리틀 엔디언).

![DM1·DM2의 Byte 1~2는 FF 예약이고, DTC 4바이트 중 Byte 3과 Byte 4는 SPN 하위 16비트, Byte 5의 bit 8~6은 SPN 상위 3비트이고 bit 5~1은 FMI, Byte 6의 bit 8은 CM이고 bit 7~1은 OC임을 60 08 1F 01 예시의 비트값으로 보여 주는 배치도](/images/study-isobus/14-dtc-layout-light.png)
![DM1·DM2의 Byte 1~2는 FF 예약이고, DTC 4바이트 중 Byte 3과 Byte 4는 SPN 하위 16비트, Byte 5의 bit 8~6은 SPN 상위 3비트이고 bit 5~1은 FMI, Byte 6의 bit 8은 CM이고 bit 7~1은 OC임을 60 08 1F 01 예시의 비트값으로 보여 주는 배치도](/images/study-isobus/14-dtc-layout-dark.png)

| 위치 | 내용 |
|---|---|
| Byte 1, 2 | Reserved, `FF` |
| Byte 3 | SPN 하위 8비트 |
| Byte 4 | SPN 둘째 바이트 |
| Byte 5 bit 8~6 | SPN 상위 3비트 |
| Byte 5 bit 5~1 | FMI (5비트, 0~31) |
| Byte 6 bit 8 | SPN conversion method(CM). 0으로 설정 |
| Byte 6 bit 7~1 | Occurrence count(OC). 모르면 `7F` |

OC의 `7F`(127)는 7비트로 담을 수 있는 가장 큰 값이다. 발생 횟수를 알 수 없으면 이 값을 넣어 "모름"을 표시한다.

### DTC 하나를 단계별로 풀어 읽기

그림의 `60 08 1F 01`을 손으로 풀어 보자. 단일 프레임 DM1 `FF FF 60 08 1F 01 FF FF`에서 앞의 `FF FF`(Byte 1~2)는 예약이고, Byte 3~6이 DTC다.

| 단계 | 바이트 | 2진수 | 하는 일 | 결과 |
|---|---|---|---|---|
| 1 | Byte 3 = `60` | `0110 0000` | SPN 비트 1~8. 그대로 쓴다 | 96 |
| 2 | Byte 4 = `08` | `0000 1000` | SPN 비트 9~16. 256을 곱한다 | 8 × 256 = 2048 |
| 3 | Byte 5 = `1F` | `000 11111` | 위 3비트(bit 8~6) `000`은 SPN 비트 17~19. 65536을 곱한다 | 0 |
| 4 | Byte 5 = `1F` | `000 11111` | 아래 5비트(bit 5~1) `11111` | FMI 31 |
| 5 | 1~3단계 합 | | 96 + 2048 + 0 | SPN 2144 (0x860) |
| 6 | Byte 6 = `01` | `0 0000001` | bit 8은 CM, bit 7~1은 OC | CM 0, OC 1 |

결과는 SPN 2144, FMI 31, CM 0, OC 1이다. 이 DTC가 무슨 뜻인지는 아래 "주소 위반 DTC"에서 본다.

SPN의 위 3비트가 0이 아닌 예도 하나 보자. 아래 코드의 `C1 A3 AC 7F`다.

1. Byte 3 `C1` = 193.
2. Byte 4 `A3` = 163이므로 163 × 256 = 41728.
3. Byte 5 `AC` = `101 01100`. 위 3비트 `101` = 5이므로 5 × 65536 = 327680. 아래 5비트 `01100` = 12이므로 FMI 12.
4. SPN = 193 + 41728 + 327680 = 369601 = `0x5A3C1`.
5. Byte 6 `7F` = `0 1111111`이므로 CM 0, OC 127(모름).

DTC 바이트 규칙을 정리하면 다음과 같다.

- SPN은 19비트라 0~524 287을 담는다. 하위 바이트부터 놓는 순서는 ISO 11783-7(트랙터와 작업기 메시지를 정하는 표준 문서)의 일반 규칙과 같다. FMI 5비트의 범위 0~31은 Part 12(ISO 11783-12, 진단 표준)가 정의한 FMI 범위와 같다(2절).
- 활성 고장이 없으면 Byte 3~6을 0으로 채운다. 즉 `FF FF 00 00 00 00`이다.
- Byte 1·2는 Part 12에서 파라미터가 하나도 없는 예약 바이트다. 램프 상태 같은 필드는 Part 12에 정의돼 있지 않다. 같은 PGN을 쓰는 SAE J1939-73 장치의 메시지까지 함께 받는 도구라면 이 두 바이트를 값 검사 없이 건너뛰는 편이 안전하다(추론: J1939-73 문서는 확인하지 못했다).
- DM1은 활성 DTC가 2개 이상이면 TP를 써야 한다(shall). DM2는 한 프레임에 안 들어갈 때만 TP를 쓴다. TP로 보낼 때 Byte 1·2는 맨 앞에 한 번만 오고 DTC마다 4 byte가 반복되므로, DTC n개의 데이터 길이는 2 + 4n이다.
- DTC가 0~1개라 6 byte인 메시지는 DLC(프레임에 실린 데이터 바이트 수) 8인 단일 프레임으로 보낸다. 멀티 패킷이 가능한 PG라도 이번에 보낼 데이터가 9 byte 미만이면 단일 프레임이기 때문이다. 남는 Byte 7~8은 Not Available 값인 `FF`로 채운다.
- DM1은 PF 254(PDU2)다. 주기·이벤트 송신은 전역이라 TP가 필요하면 BAM을 쓰고, 지정 요청에 대한 응답이 8 byte를 넘으면 RTS/CTS로 요청자에게 보낸다([27장의 요청·응답 표](/study/isobus/27-diagnostics-identification)). SA `0x90`(144)이 보내는 DM1의 CAN ID는 `0x18FECA90`이다. 이 ID를 풀면 priority 6, PGN 65226(`0xFECA`), SA `0x90`이다.

::: warning FMI 31과 채움 바이트
FMI 31은 SPN이 not available이면 "not available"을 뜻한다. 데이터를 다 보낸 뒤 패킷 나머지를 1로 채운 경우가 그렇다. `FF FF FF FF`를 DTC로 디코딩하면 SPN 524 287(0x7FFFF), FMI 31, CM 1, OC 127이 나오는데, 이것은 고장이 아니라 채움이다. TP의 전체 메시지 크기(2 + 4n)까지만 DTC로 자르면 이 함정을 피한다.
:::

### 주소 위반 DTC

그림의 `60 08 1F 01`은 주소 위반 DTC다. CF가 자기 SA를 쓴 메시지(주소 클레임 메시지 제외)를 받았다는 것은 같은 주소를 쓰는 다른 CF가 있다는 뜻이다. 이때 CF는 주소 클레임 메시지(Address Claimed)를 전역으로 다시 보내고, SPN = 2000 + SA, FMI = 31인 DTC를 활성화해야 한다. ISO 11783-5(주소와 NAME을 정하는 표준 문서) 2판(2011년)부터 생긴 규칙이다. SA가 `0x90`(144)이면 SPN 2144(0x860)다. 주소 클레임 절차 자체는 [13장](/study/isobus/13-j1939-address-claim)에서 다룬다.

아래 코드는 DTC를 4바이트로 묶고 풀며, 고장 없음·DTC 1개·DTC 2개인 DM1 프레임을 만든다. DTC 2개면 TP(BAM)로 나눠 보낸다.

::: details Python으로 DTC와 DM1 프레임 만들기
```python
def pack_dtc(spn, fmi, oc=0x7F, cm=0):
    assert 0 <= spn < 2 ** 19 and 0 <= fmi < 32 and 0 <= oc <= 0x7F
    return bytes([spn & 0xFF, (spn >> 8) & 0xFF, (spn >> 16) << 5 | fmi, cm << 7 | oc])


def unpack_dtc(b):
    return {"spn": b[0] | b[1] << 8 | (b[2] >> 5) << 16,
            "fmi": b[2] & 0x1F, "cm": b[3] >> 7, "oc": b[3] & 0x7F}


def dm_payload(dtcs):
    body = b"".join(pack_dtc(*d) for d in dtcs) or bytes(4)    # 고장 없음 = Byte 3~6이 0
    return b"\xFF\xFF" + body


def frames(pgn, payload, sa):
    if len(payload) <= 8:                                       # 단일 프레임, DLC 8
        return [((6 << 26) | (pgn << 8) | sa, payload.ljust(8, b"\xFF"))]
    n = -(-len(payload) // 7)
    bam = bytes([0x20, len(payload) & 0xFF, len(payload) >> 8, n, 0xFF,
                 pgn & 0xFF, (pgn >> 8) & 0xFF, pgn >> 16])
    out = [((7 << 26) | (0xECFF << 8) | sa, bam)]               # TP.CM_BAM
    for i in range(n):
        chunk = payload[i * 7:(i + 1) * 7].ljust(7, b"\xFF")
        out.append(((7 << 26) | (0xEBFF << 8) | sa, bytes([i + 1]) + chunk))   # TP.DT
    return out


def hx(b):
    return " ".join(f"{x:02X}" for x in b)


SA = 0x90
hitch = (1873, 3, 1)          # SPN 1873 rear hitch position, FMI 3 (E.1의 예)
violation = (2000 + SA, 31, 1)  # Part 5 4.4.4.3 주소 위반 DTC
big = (0x5A3C1, 12, 0x7F)     # 상위 3비트를 보이려고 고른 가상의 SPN, OC 미상

assert hx(pack_dtc(*hitch)) == "51 07 03 01"
assert hx(pack_dtc(*violation)) == "60 08 1F 01"
assert hx(pack_dtc(*big)) == "C1 A3 AC 7F"
assert unpack_dtc(pack_dtc(*big)) == {"spn": 0x5A3C1, "fmi": 12, "cm": 0, "oc": 0x7F}
assert unpack_dtc(b"\xFF\xFF\xFF\xFF") == {"spn": 0x7FFFF, "fmi": 31, "cm": 1, "oc": 0x7F}

for label, dtcs in [("고장 없음", []), ("DTC 1개", [violation]), ("DTC 2개", [hitch, violation])]:
    print(f"[{label}]")
    for cid, data in frames(65226, dm_payload(dtcs), SA):
        print(f"  ID=0x{cid:08X}  {hx(data)}")

# [고장 없음]
#   ID=0x18FECA90  FF FF 00 00 00 00 FF FF
# [DTC 1개]
#   ID=0x18FECA90  FF FF 60 08 1F 01 FF FF
# [DTC 2개]
#   ID=0x1CECFF90  20 0A 00 02 FF CA FE 00
#   ID=0x1CEBFF90  01 FF FF 51 07 03 01 60
#   ID=0x1CEBFF90  02 08 1F 01 FF FF FF FF
```

DTC 2개짜리 DM1은 10 byte라 TP.CM_BAM(제어 바이트 `0x20`, 크기 10, 패킷 2개, PGN `CA FE 00`) 뒤에 TP.DT 두 개로 나간다. TP.CM·TP.DT의 기본 priority는 7이다. 마지막 TP.DT 끝의 `FF FF FF FF`는 데이터가 끝난 뒤의 채움이다. 앞의 경고 상자에서 본 것처럼 DTC로 읽으면 안 된다.
:::

### DM1을 언제 보내나

계기판 경고등은 고장이 생기면 바로 켜지고, 고장이 있는 동안 켜져 있다가, 고장이 풀리면 꺼진다. DM1도 같다. 다만 "켜져 있음"을 1초마다 다시 보내는 방식으로 나타낸다. 규칙은 여섯 가지다.

1. DTC가 활성이 되는 순간 보내고, 그 뒤로는 1초에 한 번 보낸다.
2. 1초 이상 활성이던 고장이 비활성이 되면, 그 상태 변화를 반영한 DM1을 보내야 한다(shall). 그 뒤로 그 고장은 DM1에서 빠진다.
3. 1초 주기 사이에 다른 DTC의 상태가 바뀌면 새 DM1을 바로 보낸다.
4. 아주 빠른 간헐 고장 때문에 메시지가 쏟아지지 않도록, DTC 하나의 상태 변화는 초당 한 번 넘게 보내지 않는 것이 권고다(should). 1초 안에 두 번 켜졌다 꺼진 DTC는 활성을 알리는 메시지 한 번, 다음 주기 송신에서 비활성을 알리는 한 번으로 끝난다.
5. 오류가 하나라도 활성인 동안에는 가능하면 매초 보내고, 요청에도 응답해야 한다(shall). ISO 11783-3(데이터 링크 계층을 정하는 표준 문서)의 타이밍 제약 때문에 보낼 수 없으면 다음 1초 간격에 시작한다. 예를 들어 한 CF는 BAM을 한 번에 하나만 보낼 수 있으므로, 다른 PGN의 BAM이 진행 중이면 DM1의 BAM을 바로 시작할 수 없다(두 규정을 겹쳐 읽은 추론).
6. 활성 고장이 없으면 주기 송신 의무도 없다. 요청이 오면 Byte 3~6이 0인 DM1로 답한다.

아래 그림에서 위 세 줄은 DTC A·B·C가 활성인 구간이고, 맨 아래 줄의 세로 막대는 DM1이 나간 시점이다. 막대 옆의 `{A,B}`는 그 DM1에 실린 활성 DTC 목록이다. 이벤트 송신은 막대 위에, 1초 주기 송신은 막대 아래에 적었고, `x`는 1초 제한 때문에 보고를 미룬 변화다.

![DTC A·B·C의 활성 구간과 DM1 송신 시점을 6초 축에 그린 타임라인: 활성·해제 순간의 이벤트 송신, 1초 주기 송신, 1초 안에 반복된 C의 상태 변화를 다음 주기로 미루는 지점, 마지막 고장이 풀린 뒤 주기 송신이 끝나는 모습](/images/study-isobus/14-dm1-timeline-light.png)
![DTC A·B·C의 활성 구간과 DM1 송신 시점을 6초 축에 그린 타임라인: 활성·해제 순간의 이벤트 송신, 1초 주기 송신, 1초 안에 반복된 C의 상태 변화를 다음 주기로 미루는 지점, 마지막 고장이 풀린 뒤 주기 송신이 끝나는 모습](/images/study-isobus/14-dm1-timeline-dark.png)

- 0 s: A가 활성이 되자마자 `{A}`를 보낸다. 1 s, 2 s는 주기 송신이다.
- 2.4 s: B가 활성이 된다. 다른 DTC의 상태 변화이므로 주기를 기다리지 않고 `{A,B}`를 보낸다(규칙 3).
- 3.3 s: A가 풀린다. 1초 넘게 활성이었으니 곧바로 `{B}`를 보낸다(규칙 2).
- 4.2 s: C가 활성이 되어 `{B,C}`를 보낸다. 4.5·4.6·4.8 s의 변화는 C의 직전 보고(4.2 s)에서 1초가 안 지났으니 바로 보내지 않는다. 5 s 주기 송신이 C의 최종 상태(비활성)를 `{B}`로 반영한다(규칙 4).
- 5.6 s: B가 풀린다. 고장 없음 DM1 `FF FF 00 00 00 00 FF FF`를 한 번 보내고 주기 송신을 멈춘다(규칙 2, 6).

표준이 정하지 않아 구현이 골라야 하는 점이 둘 있다. 하나는 이벤트 송신 뒤에 1초 주기를 다시 세느냐다. 그림과 아래 코드는 첫 활성 시점 기준의 격자를 그대로 유지했다. 다른 하나는 미뤄 둔 상태 변화를 실어 줄 주기 송신이 없는 경우, 즉 다른 활성 고장이 없는 경우다. 코드는 미뤄 둔 변화가 남아 있으면 다음 1초 격자에서 한 번 보낸다.

아래 코드는 그림의 사건들을 100 ms 단위로 흘려 보내며 DM1이 나가는 시각과 종류(이벤트·주기)를 계산한다.

::: details Python으로 DM1 송신 시점 시뮬레이션
```python
EVENTS = {                                  # 100 ms 단위 시각: (DTC, 활성 여부)
    0: ("A", True), 24: ("B", True), 33: ("A", False),
    42: ("C", True), 45: ("C", False), 46: ("C", True), 48: ("C", False),
    56: ("B", False),
}


def simulate(events, end=70):
    active, last_reported, pending, sent = set(), {}, set(), []
    origin = None
    for t in range(end):
        trigger = None
        if t in events:
            dtc, on = events[t]
            if on:
                active.add(dtc)
            else:
                active.discard(dtc)
            if origin is None and on:
                origin = t
            if t - last_reported.get(dtc, -99) >= 10:   # 이 DTC의 직전 보고가 1 s 이상 전
                trigger, last_reported[dtc] = "event", t
            else:
                pending.add(dtc)                        # 1회/s 권고: 다음 송신으로 미룬다
        on_grid = origin is not None and t != origin and (t - origin) % 10 == 0
        if trigger is None and on_grid and (active or pending):
            trigger = "periodic"
        if trigger:
            for d in pending:
                last_reported[d] = t
            pending.clear()
            sent.append((t / 10, trigger, "".join(sorted(active))))
    return sent


for row in simulate(EVENTS):
    print(row)

assert simulate(EVENTS) == [
    (0.0, "event", "A"), (1.0, "periodic", "A"), (2.0, "periodic", "A"),
    (2.4, "event", "AB"), (3.0, "periodic", "AB"), (3.3, "event", "B"),
    (4.0, "periodic", "B"), (4.2, "event", "BC"), (5.0, "periodic", "B"),
    (5.6, "event", ""),
]
```

출력 한 줄은 (초, 송신 종류, 실린 DTC)다. 마지막 `(5.6, "event", "")`가 고장 없음 DM1이고, 그 뒤로는 주기 송신이 없다.
:::

### DM2

- 요청이 올 때만 보내고, 주기 송신은 없다. PGN을 지원하지 않으면 NACK을 보내야 한다(PGN 59392).
- 보낼 때는 OC가 0이 아닌 previously active DTC(예전에 활성이었던 고장 코드)를 하나도 빠짐없이 담아야 한다(shall).
- 바이트 배치는 DM1과 같다. "고장이 없으면 Byte 3~6을 0으로"라는 문장도 DM1과 같은 표현("no active faults")으로 적혀 있다.

### DM3 클리어 절차

정비사가 수리를 마치고 지난 고장 기록을 지우는 단계다.

- DM3(PGN 65228)는 데이터가 없는 PG다. Request(PGN 59904)로 이 PGN을 요청하는 것 자체가 클리어 명령이다.
- 요청을 받으면 previously active DTC(DM2)에 관한 진단 정보를 모두 지운다(shall). active DTC에 딸린 데이터는 건드리지 않는다.
- 클리어를 마쳤거나 지울 고장이 없으면 positive ACK를, 수행할 수 없으면 NACK을 보낸다(PGN 59392).
- 전역 주소로 온 요청에는 ACK도 NACK도 보내지 않는다. ISO 11783-3의 일반 규칙도 전역 요청에는 NACK을 금지한다.

Acknowledgement(PGN 59392)는 PF 232인 PDU1 메시지로, 8 byte다. PDU1은 CAN ID에 받는 쪽 주소 칸이 있는 형식이다.

| Byte | ACK | NACK |
|---|---|---|
| 1 | `00` Positive Acknowledgement | `01` Negative Acknowledgement |
| 2 | Group Function Value, 해당 없으면 `FF` | 같음 |
| 3~4 | `FF FF` | 같음 |
| 5 | 요청한 쪽의 주소 | 같음 |
| 6~8 | 대상 PGN, LSB부터. DM3면 `CC FE 00` | 같음 |

ISO 11783-3에는 control byte `2`(Access Denied, 접근 거부)와 `3`(Cannot Respond: 지원하지만 지금 바빠서 못 함)도 있다. Part 12는 DM3를 "수행할 수 없음"일 때 negative acknowledgement로 답하라고 지정하고, Part 12의 예시도 NACK으로 답한다.

진단 UI(SA `0x26`)가 ECU(SA `0x90`)의 기록을 지우는 교환을 바이트로 보면 다음과 같다. `0x26`(38)은 Part 12의 예시 진단 화면에 나오는 VT 주소를 빌려 온 값이다.

```
UI  -> ECU  Request(DM3)   ID=0x18EA9026 DLC=3  CC FE 00
ECU -> UI   ACK            ID=0x18E82690 DLC=8  00 FF FF FF 26 CC FE 00
ECU -> UI   NACK           ID=0x18E82690 DLC=8  01 FF FF FF 26 CC FE 00
UI  -> ECU  Request(DM2)   ID=0x18EA9026 DLC=3  CB FE 00
UI  -> all  Request(DM3)   ID=0x18EAFF26 DLC=3  CC FE 00
```

한 줄씩 읽으면 다음과 같다.

1. UI가 ECU에 DM3를 지정 요청한다. CAN ID `0x18EA9026`은 priority 6, Request(PF `EA`), 받는 쪽 `0x90`, 보내는 쪽 `0x26`이다. 데이터 `CC FE 00`이 PGN 65228이다.
2. 클리어에 성공하면 ECU가 ACK을 보낸다. ID `0x18E82690`은 Acknowledgement(PF `E8`), 받는 쪽 `0x26`, 보내는 쪽 `0x90`이다. 데이터는 `00`(ACK), `FF`(group function 없음), `FF FF`, `26`(요청한 쪽 주소), `CC FE 00`(DM3의 PGN)이다.
3. 수행할 수 없으면 같은 자리에 첫 바이트만 `01`(NACK)인 응답이 온다. 2와 3 가운데 하나만 온다.
4. 지워졌는지 확인하려고 DM2를 지정 요청한다(`CB FE 00`). Byte 3~6이 0인 DM2가 오면 기록이 비었다.
5. 받는 쪽 주소를 `FF`(전역)로 한 DM3 요청이다. 아무도 답하지 않는다.

- Working Set의 member도 독립 CF이므로, member의 고장 기록을 지우려면 master가 아니라 그 member의 SA로 요청해야 한다([26장](/study/isobus/26-isobus-network-mgmt)의 규칙 c).
- 전역 DM3에는 아무도 답하지 않으니 진단 UI는 성공 여부를 알 수 없다. 확인이 필요하면 CF마다 DM2를 지정 요청해 비었는지 보거나, 처음부터 CF마다 지정 DM3를 보내 ACK를 받는다(추론).

::: tip 정리
- DTC는 4 byte다. SPN 19비트는 Byte 3·4와 Byte 5 상위 3비트에, FMI는 Byte 5 하위 5비트에, CM(0)과 OC는 Byte 6에 들어간다. Byte 1·2는 `FF` 예약이다.
- DM1은 활성·해제 순간과 활성 중 1초마다 보낸다. DTC 하나의 상태 변화는 초당 한 번 넘게 보내지 않는 것이 권고다.
- DM3는 Request 자체가 명령이다. 지정 요청에는 ACK/NACK이 오고 전역 요청에는 아무것도 오지 않는다.
:::

<small>근거: ISO 11783-12 B.6, B.7, B.8, Annex E; ISO 11783-3 5.2.8.2, 5.4.3, 5.4.5, 5.10, 5.10.6.2; ISO 11783-5 4.4.4.3; ISO 11783-7 3.3.1, B.23.4</small>

## 2. FMI 해석

[27장](/study/isobus/27-diagnostics-identification)의 표는 자주 쓰는 FMI만 보였다. 이 절은 FMI 전체를 훑고, 구현자가 FMI를 고를 때 따지는 세 가지를 정리한다. 값이 어느 영역에 있나, 그 파라미터의 방송 값을 어떻게 하나, 논리 판정(rationality) 고장인가. SPN 611~615(System Diagnostic Code)의 쓰임과 FMI별 자세한 해설은 [부록](/study/isobus/appendix-iso-part12)에 있다.

### FMI 값 한눈에 보기

| FMI | 이름 | 한 줄 풀이 |
|---|---|---|
| 0 | 데이터는 유효하나 정상보다 높음 (가장 심함) | 값을 믿을 수 있고, 그 값이 위험할 만큼 높다 |
| 1 | 데이터는 유효하나 정상보다 낮음 (가장 심함) | 값을 믿을 수 있고, 그 값이 위험할 만큼 낮다 |
| 2 | 데이터 불안정·간헐적·부정확 | 현실에서 불가능하게 튀거나 다른 정보와 모순된다 |
| 3 | 전압 높음 또는 high 쪽 단락 | 신호 전압이 범위 위로 벗어났다 |
| 4 | 전압 낮음 또는 low 쪽 단락 | 신호 전압이 범위 아래로 벗어났다 |
| 5 | 전류 낮음 또는 단선 | 전류가 흐르지 않는다 |
| 6 | 전류 높음 또는 접지 단락 | 전류가 너무 많이 흐른다 |
| 7 | 기계 장치 무응답 또는 조정 불량 | 전기·전자 쪽 고장이 아닌데 기계가 따라오지 않는다 |
| 8 | 주파수·펄스 폭·주기 이상 | 주파수나 PWM 신호가 범위를 벗어났다 |
| 9 | 갱신 주기 이상 | 네트워크 데이터가 제때 오지 않는다 |
| 10 | 변화율 이상 | 값은 유효한데 변하는 속도가 비정상이다 |
| 11 | 원인 미상 | 고장은 확인됐지만 정확한 종류를 모른다 |
| 12 | 지능형 장치·컴포넌트 불량 | ECU 내부 고장이라 ECU를 바꿔야 한다 |
| 13 | 캘리브레이션 불량 | 보정값이 낡았거나 기계 보정이 틀어졌다 |
| 14 | 특별 지시 | 원인을 후보 몇 개로만 좁혔다. 제조사 절차를 따른다 |
| 15 | 데이터는 유효하나 정상보다 높음 (약함) | 조금 높다 |
| 16 | 데이터는 유효하나 정상보다 높음 (중간) | 꽤 높다 |
| 17 | 데이터는 유효하나 정상보다 낮음 (약함) | 조금 낮다 |
| 18 | 데이터는 유효하나 정상보다 낮음 (중간) | 꽤 낮다 |
| 19 | 네트워크로 받은 데이터 오류 | 받은 값이 오류 표시로 와 있다. 원인은 보낸 쪽에 있다 |
| 20~30 | 예약 | 앞으로 쓸 자리 |
| 31 | 상태 존재 | SPN이 가리키는 상태가 일어났다 |

PWM(Pulse Width Modulation)은 켜짐과 꺼짐의 시간 비율로 값을 나타내는 신호다. 현장에서 가장 자주 보는 값은 범위 계열(0·1·15~18), 전기 계열(3~6), ECU 고장(12), 네트워크 계열(9·19), 상태 존재(31)다.

### 신호 범위 영역

FMI 0·1·3~6·15~18은 값이 "값의 축"에서 어디에 놓였는지로 정해진다. 체온계에 빗대면 c는 정상 체온, h·i는 약간 낮거나 높은 체온, j·k는 꽤 낮거나 높은 체온, d·e는 위험한 체온이다. f·g는 사람 체온으로 나올 수 없는 값(예: 영하)이라 체온이 아니라 체온계나 배선의 고장을 뜻한다.

![값 축을 낮은 쪽부터 f, d, j, h, c, i, k, e, g 영역으로 나누고 각 영역의 FMI(f는 4/5, d는 1, j는 18, h는 17, c는 정상, i는 15, k는 16, e는 0, g는 3/6)를 표시한 그림. b는 d부터 e까지의 물리적으로 가능한 범위, a는 f부터 g까지 전자 모듈이 잴 수 있는 전체 범위](/images/study-isobus/28-fmi-signal-regions-light.png)
![값 축을 낮은 쪽부터 f, d, j, h, c, i, k, e, g 영역으로 나누고 각 영역의 FMI(f는 4/5, d는 1, j는 18, h는 17, c는 정상, i는 15, k는 16, e는 0, g는 3/6)를 표시한 그림. b는 d부터 e까지의 물리적으로 가능한 범위, a는 f부터 g까지 전자 모듈이 잴 수 있는 전체 범위](/images/study-isobus/28-fmi-signal-regions-dark.png)

값 축을 낮은 쪽부터 놓으면 아래 순서다. region a는 전자 모듈이 잴 수 있는 전체 범위이고, region b는 응용이 정한 물리적으로 가능한 범위(d부터 e까지)다.

| 영역 (낮은 쪽부터) | 뜻 | FMI |
|---|---|---|
| f | 물리적으로 가능한 범위보다 낮음. low 쪽 단락을 뜻한다 | 4 (전압) / 5 (전류) |
| d | 정상 미만, most severe | 1 |
| j | 정상 미만, moderately severe | 18 |
| h | 정상 미만, least severe | 17 |
| c | 정상 | 해당 없음 |
| i | 정상 초과, least severe | 15 |
| k | 정상 초과, moderately severe | 16 |
| e | 정상 초과, most severe | 0 |
| g | 물리적으로 가능한 범위보다 높음. high 쪽 단락을 뜻한다 | 3 (전압) / 6 (전류) |

most severe는 가장 심한 수준, moderately severe는 중간 수준, least severe는 가장 약한 수준이다.

- 한 SPN에 모든 FMI가 맞지는 않는다. Part 12가 드는 예는 SPN 1873(rear hitch position, 뒤 히치 위치)이다. 이 입력을 전압으로 진단하는 CF는 FMI 3·4를 쓰고 FMI 5·6은 쓰지 않는다.
- FMI 3~6은 범위 이탈만 뜻하지 않는다. CF가 low로 명령했는데 high로 남은 외부 신호(FMI 3), high로 명령했는데 low인 신호(FMI 4), on으로 명령했는데 전류가 없는 신호(FMI 5), off로 명령했는데 전류가 흐르는 신호(FMI 6)도 포함한다.
- FMI 8은 주파수나 PWM 신호가 region b를 벗어난 경우다. Part 12는 FMI 4·5인 경우에 함께 고려하라고 적는다.

### 방송 값을 어떻게 하나

여기서 방송 값은 그 파라미터를 평소처럼 버스에 보내는 값이다. 예를 들어 속도 센서에 고장이 났을 때, 속도 메시지 안의 속도 값을 계속 그대로 보낼지가 문제다. FMI마다 그 파라미터를 계속 방송하는 값을 어떻게 할지가 함께 정해져 있다.

| 방송 처리 | FMI |
|---|---|
| 실제 값을 계속 보낸다 | 0, 1, 10, 15, 16, 17, 18 |
| error indicator로 바꿔 보낸다 | 2, 3, 4, 5, 6, 8, 11, 12(해당하면) |
| 원문이 "방송 값과 직접 관련될 수도 있고 아닐 수도 있다"고만 적음 | 7, 9, 14, 19, 31 |
| 언급 없음 | 13 |

규칙은 단순하다. 값을 믿을 수 있으면(측정은 정상이고 값이 범위를 벗어났을 뿐이면) 값을 그대로 보낸다. 측정 자체를 믿을 수 없으면 값 대신 error indicator를 보낸다.

error indicator 값은 ISO 11783-7이 자료형마다 정해 두었다([26장의 1 byte 값 표](/study/isobus/26-isobus-network-mgmt) 참고). 1 byte 파라미터는 `FE`, 2 byte는 `FExx`, 4 byte는 `FExxxxxx`, 문자열은 `00`이다. `xx`는 어떤 값이 와도 된다는 뜻이다. 같은 규칙은 반대쪽 경우도 정한다. 값이 유효한데 파라미터 범위만 넘으면 error indicator를 쓰지 말고 최솟값이나 최댓값으로 보낸다. 측정이 유효하면 값을 숨기지 않는다는 점에서 FMI 0·1·15~18의 "실제 값 유지"와 같은 쪽이다(해석).

### 헷갈리는 FMI 쌍

- FMI 2와 FMI 10은 둘 다 값이 이상하게 변하는 경우다. FMI 2는 현실에서 불가능한 속도로 변하는 값, 즉 측정 장치나 연결의 이상이고 방송 값을 error indicator로 바꾼다. FMI 10은 값 자체는 유효한데 변화율이 정상 시스템의 한계를 벗어난 경우이고 값을 계속 보낸다.
- FMI 9는 스마트 센서·액추에이터에서 네트워크로 받는 데이터가 기대하거나 요구하는 갱신 주기로 오지 않을 때다. CF 자신이 시스템이 요구하는 주기로 보내지 못하는 오류도 포함한다.
- FMI 19는 네트워크로 받은 값이 error indicator(`FE`)로 와 있을 때다. 실제 센서는 그 값을 보낸 모듈에 물려 있으므로 고장 위치는 받은 쪽이 아니라 보낸 쪽이다. 예를 들어 작업기가 트랙터에서 받은 속도 파라미터가 `FExx`로 오면, 작업기는 그 파라미터의 SPN에 FMI 19를 걸고 원인은 트랙터 쪽 DTC에서 찾는다(예시는 원문에 없는 추론).
- FMI 31은 SPN이 가리키는 상태가 존재한다는 뜻이다. 맞는 FMI가 없거나, SPN 이름 자체가 컴포넌트와 비표준 고장 모드를 다 말해 줄 때 쓴다. ISO 11783-5의 주소 위반 DTC(SPN 2000 + SA)가 FMI 31을 쓰는 것이 이 경우다(1절).

Part 12가 rationality 고장에 적용된다고 표시한 FMI는 2, 7, 9, 10, 12, 13, 14, 31이다. 전기 신호의 범위가 아니라 다른 정보와의 모순, 기계의 응답, 갱신 주기, 캘리브레이션처럼 논리로 판정하는 고장이다.

정리하면, FMI를 고를 때는 (1) 값이 범위의 어디에 있는지, (2) 측정을 믿을 수 있어 값을 계속 보내도 되는지, (3) 전기 신호가 아니라 논리로 판정한 고장인지를 차례로 따진다.

<small>근거: ISO 11783-12 Annex E(E.1~E.3); ISO 11783-7 3.3.3</small>

## 3. Control function functionalities 메시지

CF가 어떤 functionality(UT, AUX-N, TC-GEO처럼 AEF가 정의한 기능 단위)를 몇 세대(generation)로, 어떤 옵션과 함께 지원하는지 알리는 메시지다. 기능 단위 자체는 [AEF Functionality 부록](/study/isobus/appendix-aef-functionalities)에 정리돼 있다.

스마트폰 사양표에 "블루투스 5.3, Wi-Fi 6"처럼 기능과 세대를 적듯, CF는 이 메시지로 "UT 3세대, TC-GEO 1세대"처럼 자기 기능을 알린다. AEF(Agricultural Industry Electronics Foundation)는 ISOBUS 적합성 시험을 운영하는 농기계 업계 단체다. 이 절에 나오는 기능 이름은 UT(Universal Terminal, VT 기능), AUX-N(보조 입력, 조이스틱 같은 입력 장치), TC-BAS(기본 TC 기능), TC-GEO(위치 기반 TC 기능), TC-SC(섹션 제어), TECU(트랙터 ECU 기능)다.

| 항목 | 값 |
|---|---|
| PGN | 64654 (0xFC8E) |
| DP / PF / PS | 0 / 252 / 142 |
| 기본 priority | 6 |
| 데이터 길이 | 가변, 최소 8 byte |
| 전송 주기 | On request |

### 구조

| Byte | 내용 |
|---|---|
| 1 | `FF` 고정. 수신자는 `FF`가 아니면 메시지를 처리하지 않는다(shall not) |
| 2 | 이 메시지에 담긴 functionality 수 N (1~255) |
| 3 | 첫 functionality 코드 (0~255) |
| 4 | 그 generation (1~255) |
| 5 | 뒤따르는 option byte 수 k (0~255) |
| 6 ~ 5+k | option byte |
| 그다음 | 두 번째 functionality부터 같은 묶음 반복 |

- 8 byte를 넘으면 TP로 보내고, 8 byte보다 짧으면 남는 바이트를 `FF`로 채운다(shall).
- option byte 뒤쪽의 0 바이트(trailing zero)는 모두 빼고 개수에도 세지 않는다. option이 없으면 k = 0이다.

Byte 3부터는 "코드, generation, option byte 수 k, option byte k개"라는 묶음이 N번 이어진다. 묶음마다 길이가 3 + k라 고정되어 있지 않다는 점이 중요하다.

예시 메시지 `FF 02 00 01 00 01 02 00`(아래 코드의 예시 1)을 읽어 보자.

1. Byte 1 `FF`: 고정값이 맞으니 계속 읽는다.
2. Byte 2 `02`: functionality가 2개다.
3. Byte 3~5 `00 01 00`: 코드 `0x00`(Minimum CF), generation 1, option byte 0개.
4. Byte 6~8 `01 02 00`: 코드 `0x01`(UT), generation 2, option byte 0개.

즉 이 CF(VT)는 Minimum CF 1세대와 UT 2세대를 지원한다. 전체가 8 byte라 단일 프레임으로 나간다. option이 있는 묶음은 `06 01 01 05`처럼 생겼다. 코드 `0x06`(AUX-N), generation 1, option byte 1개, option `05`다.

### 코드와 option

3판부터 functionality 코드와 option 비트의 정의는 표준 본문이 아니라 ISOBUS 온라인 데이터베이스(www.ISOBUS.net)의 Functionality/Option list가 관리한다. Part 12에는 예시 메시지가 세 개 실려 있다. 예시 1은 VT, 예시 2는 Working Set Master, 예시 3은 Minimum CF만 따르는 독자 규격(proprietary) CF가 보내는 메시지다. 예시에 나오는 코드만 모으면 다음과 같다.

| 코드 | 원문 표기 | 나오는 곳 |
|---|---|---|
| `0x00` | Minimum CF | 예시 1·2·3 |
| `0x01` | UT | 예시 1 (VT가 보고) |
| `0x02` | UT | 예시 2 (Working Set Master가 보고) |
| `0x06` | AUX-N | 예시 2 |
| `0x08` | TC-BAS | 예시 2 |
| `0x0A` | TC-GEO | 예시 2 |
| `0x0E` | TECU | 예시 2 |

UT가 `0x01`과 `0x02`로 두 번 나온다. 표준은 차이를 설명하지 않는다. 하지만 `0x01`은 VT(서버)가, `0x02`는 Working Set Master(클라이언트)가 보고하므로 서버용과 클라이언트용 코드가 따로 있는 것으로 보인다(추론, 코드표는 ISOBUS.net에서 확인 필요). AEF가 서버와 클라이언트를 따로 인증한다는 점([AEF Functionality 부록](/study/isobus/appendix-aef-functionalities))과도 맞는다.

option byte는 비트 플래그일 때도 있고 값일 때도 있다. 비트 플래그는 비트 하나하나가 켜짐/꺼짐으로 항목 하나씩을 나타내는 방식이다. 예시 2에서 AUX-N의 option `00000101`은 오른쪽에서 첫째·셋째 비트가 켜져 function type 0과 2를, TECU의 `00001001`은 Class 1과 Navigation을 뜻한다. 반면 TC-GEO의 option `0x04`는 control channel이 4개라는 값이다. option byte는 functionality마다 따로 해석해야 한다.

Byte 1에 diagnostic protocol 비트를 넣으면 안 된다. Part 12의 예시에는 이전 판 구조의 흔적으로 보이는 표기가 남아 있지만(추론), 지금 판의 Byte 1은 그냥 `FF` 고정이다.

### 하위 호환 파싱 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

새 판에서 option byte가 늘어나도 옛 파서가 망가지지 않게 하는 규칙이다.

- ISO 할당 예약 코드도 오류 없이 파싱해야 한다(shall).
- 어떤 functionality의 option byte 수가 이 문서의 정의보다 많으면, 모르는 option byte는 무시하고 아는 것만 파싱한다(shall).
- 두 규칙 모두 "Byte 5의 k를 믿고 건너뛰라"는 뜻이다. functionality별 option byte 수를 상수로 박아 둔 파서는 새 판의 메시지를 받으면 다음 functionality부터 한 칸씩 어긋난다.

### 무엇을 보고하나

- 활성 functionality와 그 generation·option을 모두 보고한다(shall).
- ECU에 있지만 지금 시스템에서 쓸 수 없는 functionality는 보고한다(shall). 예를 들어 TC-SC 서버가 없는 트랙터에 붙은 작업기의 TC-SC가 그렇다.
- ECU에 있지만 CF에서 비활성화된 functionality는 보고하지 않는다(shall not). 예를 들어 고객이 사지 않아 꺼 둔 TC-SC가 그렇다.
- Part 12의 예시 화면(연결된 시스템의 기능 화면)에서 트랙터 쪽 UT가 4세대, 작업기 쪽이 3세대일 때 연결된 시스템의 generation은 3으로, AUX-N은 4세대와 2세대에서 2로 표시된다. 연결된 시스템은 양쪽 중 낮은 세대로 표시된 것으로 읽힌다(informative 그림에서 읽은 관찰이며 규정은 아니다).

아래 코드는 Part 12의 예시 세 개를 인코딩해 바이트열을 확인하고, option byte가 늘어난 새 판 메시지를 옛 파서가 k를 믿고 건너뛰며 읽는 모습을 보여 준다.

::: details Python으로 원문 예시 세 개 검산
```python
def encode(functionalities):
    out = bytearray([0xFF, len(functionalities)])
    for code, generation, options in functionalities:
        opts = bytes(options).rstrip(b"\x00")          # A.12: 뒤쪽 0 option byte는 뺀다
        out += bytes([code, generation, len(opts)]) + opts
    return bytes(out.ljust(8, b"\xFF"))                # 8 byte 미만이면 FF로 채운다


def decode(data, known_option_bytes=None):
    if data[0] != 0xFF:                                # Byte 1이 FF가 아니면 처리하지 않는다
        return None
    known = known_option_bytes or {}
    result, i = [], 2
    for _ in range(data[1]):
        code, generation, n = data[i], data[i + 1], data[i + 2]
        options = data[i + 3:i + 3 + n]
        result.append((code, generation, bytes(options[:known.get(code, n)])))
        i += 3 + n                                     # 모르는 option byte도 k만큼 건너뛴다
    return result


def hx(b):
    return " ".join(f"{x:02X}" for x in b)


ex1 = encode([(0x00, 1, []), (0x01, 2, [])])
ex2 = encode([(0x02, 3, []), (0x06, 1, [0b00000101]), (0x08, 1, []),
              (0x0A, 1, [0x04]), (0x0E, 1, [0b00001001]), (0x00, 1, [])])
ex3 = encode([(0x00, 1, [])])
for name, msg in (("예시 1", ex1), ("예시 2", ex2), ("예시 3", ex3)):
    print(f"{name} ({len(msg):2} byte): {hx(msg)}")

assert ex1 == bytes.fromhex("FF 02 00 01 00 01 02 00")
assert ex3 == bytes.fromhex("FF 01 00 01 00 FF FF FF")
assert len(ex2) == 23 and ex2[8] == 0b00000101 and ex2[15] == 0x04   # 원문 Byte 9, Byte 16
assert encode([(0x0E, 1, [0x09, 0x00])]) == encode([(0x0E, 1, [0x09])])

newer = bytes.fromhex("FF 02 0E 01 02 09 80 00 01 00")   # TECU option이 2 byte로 늘어난 가상의 새 판
assert decode(newer, known_option_bytes={0x0E: 1}) == [(0x0E, 1, b"\x09"), (0x00, 1, b"")]
assert decode(bytes.fromhex("00 02 00 01 00 01 02 00")) is None

# 예시 1 ( 8 byte): FF 02 00 01 00 01 02 00
# 예시 2 (23 byte): FF 06 02 03 00 06 01 01 05 08 01 00 0A 01 01 04 0E 01 01 09 00 01 00
# 예시 3 ( 8 byte): FF 01 00 01 00 FF FF FF
```

예시 3은 묶음이 하나뿐이라 5 byte인데, 8 byte에 못 미쳐 뒤를 `FF FF FF`로 채웠다. 예시 2는 23 byte라 TP로 나간다. `newer`는 TECU의 option byte가 2개로 늘어난 가상의 메시지다. 옛 파서는 option을 1개만 알지만 k = 2만큼 건너뛰므로 다음 묶음(Minimum CF)을 제대로 읽는다.
:::

정리하면, functionalities 메시지는 `FF`와 개수 N 뒤에 "코드, generation, k, option k개" 묶음을 이어 붙인 가변 길이 메시지다. 파서는 k를 믿고 건너뛰어야 새 판 메시지도 안전하게 읽는다.

<small>근거: ISO 11783-12 B.9, A.9~A.12, 6.5, Annex D</small>

::: details 원문을 가진 독자를 위한 메모
- 1절의 DM1은 Part 12 B.6, DM2는 B.7, DM3는 B.8이다. FMI 범위 0~31은 Annex E, FMI 31 채움 설명은 E.3.22, 코드 주석의 SPN 1873 예는 E.1이다. 단일 프레임 규칙은 Part 3 5.2.8.2, TP.CM·TP.DT priority는 5.10, BAM을 하나씩만 보내는 규칙은 5.10.6.2, 전역 요청 NACK 금지는 5.4.3, Acknowledgement 메시지는 5.4.5다. 주소 위반 DTC는 Part 5 4.4.4.3, Working Set member 규칙 c)는 Part 7 B.23.4 c)다. 예시 진단 화면은 Part 12 Annex D.1, DM3에 NACK으로 답하는 예는 B.8의 예시 2다. DTC 바이트 순서의 일반 규칙은 Part 7 3.3.1이다.
- 2절의 신호 범위 영역은 E.2와 Figure E.1, FMI 3~6의 "명령과 반대로 남은 신호"는 E.3.4~E.3.7의 b), FMI 8은 E.3.9, FMI 2와 10은 E.3.3과 E.3.11, FMI 9는 E.3.10, FMI 19는 E.3.20, FMI 31은 E.3.22다. error indicator 값과 범위 초과 시 최솟값·최댓값 규칙은 Part 7 3.3.3과 Table 1이다.
- E.3.2(FMI 1)의 본문은 "least severe level limits"라고 적었지만, 제목과 region d의 정의는 most severe다. 오기로 보이며 region d·most severe로 읽는다(추론).
- 3절은 Part 12 B.9, 필드는 A.9(개수), A.10(코드), A.11(generation), A.12(option byte 수)다. 코드와 option의 온라인 데이터베이스 이관은 서문과 A.10에 있다. 보고 규칙은 6.5, 예시 화면은 Annex D.4·D.5다.
- B.9 예시 1의 제목은 "Diagnostic protocol and functionality message"이고, 예시 2는 Byte 1에 "(See A.6)"을 달아 두었다. 본문 3절의 "이전 판 구조의 흔적"은 이 두 표기를 말한다.
:::

::: tip 핵심 정리
- DTC는 4바이트다. SPN 19비트는 Byte 3·4와 Byte 5 위 3비트에, FMI는 Byte 5 아래 5비트에, CM(0)과 OC는 Byte 6에 들어간다. DM1·DM2의 Byte 1·2는 `FF` 예약이다.
- DM1은 고장이 활성이 되는 순간과 해제되는 순간, 그리고 활성 중 1초마다 보낸다. DTC가 2개 이상이면 TP로 보낸다.
- DM3는 Request 자체가 클리어 명령이다. 지정 요청에는 ACK/NACK이 오고 전역 요청에는 아무것도 오지 않는다.
- FMI는 값이 놓인 영역(정상에서 벗어난 정도, 단락), 방송 값을 유지하는지, 논리 판정 고장인지로 고른다.
- functionalities 메시지는 `FF`와 개수 뒤에 "코드, generation, option byte 수, option들" 묶음을 반복한다. 파서는 option byte 수를 믿고 건너뛴다.
:::

::: details 확인 문제
1. (개념) DTC `51 07 03 01`을 단계별로 풀어 SPN, FMI, OC를 구하라.
2. (개념) 활성 고장이 하나도 없는 CF에 DM1을 요청하면 어떤 8바이트가 오는가? 이 CF는 평소에 DM1을 주기적으로 보내는가?
3. (개념) 온도 값이 정상 범위를 조금 넘었다(가장 약한 수준). FMI는 몇이고, 그 파라미터의 방송 값은 어떻게 하나? 센서 선이 전원 쪽에 단락돼 전압이 범위 위로 벗어났다면?
4. (디코딩·장애 진단) SA `0x90`인 CF가 단일 프레임 DM1 `FF FF 60 08 1F 01 FF FF`를 보내기 시작했다. SPN·FMI·OC를 구하고, 이 CF에 무슨 일이 있었는지와 다음에 확인할 것을 말하라.
5. (설계) 진단 UI가 모든 CF의 고장 이력을 지우려고 전역 주소로 DM3를 요청했는데 응답이 하나도 없다. 성공한 것인가? 확인하려면 어떻게 하나? Working Set member의 이력은 어떻게 지우나?

**답 가이드**
1. Byte 3 `51` = 81, Byte 4 `07` = 7이므로 7 × 256 = 1792다. Byte 5 `03` = `000 00011`이라 SPN 위 3비트는 0이고 FMI는 `00011` = 3이다. SPN = 81 + 1792 = 1873(rear hitch position)이다. Byte 6 `01`은 CM 0, OC 1이다. 뒤 히치 위치 신호의 전압이 정상보다 높거나 high 쪽에 단락된 고장이 한 번 일어났다는 뜻이다.
2. `FF FF 00 00 00 00 FF FF`가 온다. Byte 3~6이 0이면 활성 고장이 없다는 뜻이다. 활성 고장이 없으면 주기 송신 의무가 없으므로 평소에는 보내지 않고, 요청이 올 때만 이렇게 답한다.
3. 정상 초과·least severe는 region i이므로 FMI 15이고, 실제 값을 계속 방송한다. 전원 쪽 단락으로 전압이 범위 위로 벗어났다면 region g의 FMI 3이고, 방송 값은 error indicator(1 byte면 `FE`)로 바꿔 보낸다.
4. `SPN = 0x60 | 0x08 << 8 | (0x1F >> 5) << 16 = 0x860 = 2144`, `FMI = 0x1F & 0x1F = 31`, CM = 0, OC = 1이다. 2144 = 2000 + 0x90이므로 1절에서 본 주소 위반 DTC다. 이 CF는 주소 클레임 메시지가 아닌 메시지 중 자기 주소 `0x90`을 SA로 쓴 프레임을 받았다. 즉 다른 CF가 같은 주소를 쓰고 있다. 이 CF는 Address Claimed를 전역으로 다시 보냈을 것이다. 진단 툴은 Request for Address Claimed를 전역으로 보내 `0x90`을 클레임하는 NAME이 둘인지 확인한다.
5. 알 수 없다. 전역 요청에는 ACK도 NACK도 보내지 않는 것이 규정이라 무응답은 성공도 실패도 뜻하지 않는다. 확인하려면 CF마다 DM2를 지정 요청해 Byte 3~6이 0인지 보거나, 처음부터 CF마다 지정 DM3를 보내 ACK·NACK을 받는다. Working Set member는 독립 CF이므로 master가 아니라 각 member의 SA로 요청해야 한다([26장](/study/isobus/26-isobus-network-mgmt)의 규칙 c).
:::

## 다음 챕터

- 다음: [29장 Virtual Terminal(VT) 기초](/study/isobus/29-vt-basics)
