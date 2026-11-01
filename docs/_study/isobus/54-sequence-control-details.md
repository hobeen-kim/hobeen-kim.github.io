---
title: "Sequence Control 세부: SCD 바이트, 메시지, 오류 처리"
description: "SCD 오브젝트 레코드의 바이트 배치, SC 메시지 지도와 재생 한 스텝의 바이트, 주기와 타임아웃, TAN 처리, 기능 고장과 Abort 같은 오류 처리를 익힌다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, SequenceControl, SCD, TAN]
prev: /study/isobus/53-sequence-control-basics
next: /study/isobus/55-practice-log-vt-tc
---

# Sequence Control 세부: SCD 바이트, 메시지, 오류 처리

::: info 학습 목표
- SCD의 세 오브젝트(basic, function, state)가 무엇을 담는지 설명하고, 레코드의 바이트 배치를 읽을 수 있다.
- SC 메시지 프레임(예: `33 05 02 12 4C 1D 00 00`)을 바이트마다 풀어 읽을 수 있다.
- 상태 메시지의 송신 주기와 타임아웃(활동 상태 600 ms, Ready 3 s)을 말하고, 메시지가 끊겼을 때 각 장치가 어디로 가는지 설명할 수 있다.
- 기록과 재생에서 TAN과 실행 상태로 반복 송신과 늦은 응답을 가려내는 방법을 설명할 수 있다.
- 기능 고장 보고, Abort, 규칙을 어기는 참여자에 대한 처리를 설명할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [53장 Sequence Control(SC) 기초](/study/isobus/53-sequence-control-basics), [9장 J1939 메시지 구조](/study/isobus/09-j1939-message), [15장 Transport Protocol 기초](/study/isobus/15-tp-bam-cmdt)
- 이 장에서 처음 나오는 말
  - 오브젝트 레코드(object record): SCD 안에서 오브젝트 하나를 정해진 바이트 순서로 적은 묶음이다.
  - NAME Mask: 저장된 SCD가 어느 장치의 것인지 맞춰 볼 때 NAME의 어느 비트를 비교할지 정하는 마스크다.
  - function value(기능 값): 히치가 멈춘 높이처럼 기능의 실행 결과를 숫자 하나로 담은 값이다. 기록 때 저장했다가 재생 때 돌려준다.
  - 실행 상태(function execution state): 기능 실행이 시작, 완료, 오류 가운데 어디인지 나타내는 2비트 값이다.
  - ClientFunctionErrorState: SCC가 자기 기능의 고장 여부를 상태 메시지에 실어 늘 알리는 값이다.
:::

53장에서 SC 대화의 순서를 봤다면, 이 장은 그 대화를 바이트 수준에서 들여다본다. 식당에 빗대면 53장은 "주문하고 음식을 받는 순서"였고, 이 장은 "주문서의 칸마다 무엇을 적는지"다. SCD 레코드, 메시지 지도, 재생 한 스텝, 타이밍, TAN, 오류 처리를 차례로 보고, 프레임은 바이트마다 풀어 읽는다.

## 1. SCD에는 무엇이 들어 있나

이 절에서는 SCC가 SCM에 건네는 자기소개서인 SCD(Sequence Control Data)의 내용을 본다. 바이트 배치는 2절로 미루고, 여기서는 무엇을 담는지와 꼭 알아야 할 필드의 뜻을 본다.

SCD는 VT 오브젝트 풀([32장](/study/isobus/32-vt-object-pool-basics))과 비슷한 레코드 묶음이다. 회사 조직도처럼 맨 위에 SCC 자체를 소개하는 basic object가 하나 있고, 그 아래에 기록할 수 있는 기능마다 function object가, 다시 그 아래에 기능이 가질 수 있는 상태마다 state object가 달린다.

![SCD 오브젝트 계층: Object ID 0인 basic object 하나 아래에 function object가 1~255개, 각 function object 아래에 state object가 0~64개 달린다. 예로 3점 히치 아래 하강과 상승 상태가 있다](/images/study-isobus/54-scd-object-tree-light.png)
![SCD 오브젝트 계층: Object ID 0인 basic object 하나 아래에 function object가 1~255개, 각 function object 아래에 state object가 0~64개 달린다. 예로 3점 히치 아래 하강과 상승 상태가 있다](/images/study-isobus/54-scd-object-tree-dark.png)

공통 규칙부터 본다.

- object ID는 SCD 전체에서 유일하고 범위는 0~65534다. 65535(0xFFFF)는 NULL(가리키는 대상 없음)로 예약된다.
- basic object는 SCD당 하나이고 object ID는 항상 0이다. function object는 basic object당 1~255개, state object는 function object당 0~64개다.
- Function ID가 1바이트, State ID가 6비트인 이유는 관련 CAN 메시지를 8바이트 안에 담기 위해서다. 그래서 SCD 하나의 기능은 최대 255개, 기능 하나의 상태는 최대 64개다.
- 자료형은 Bitmask(1바이트, Bit 0 = 최하위), Byte Array, Float(IEEE 754 32비트: 소수를 4바이트에 담는 표준 형식), Integer(1·2·4바이트)다.

구현할 때 눈여겨볼 필드는 다음과 같다.

- <strong>SCC NAME Mask</strong>: 저장된 SCD가 지금 연결된 SCC의 것인지 NAME(장치마다 고유한 64비트 이름, [12장](/study/isobus/12-j1939-address-name))으로 맞춰 볼 때 쓴다. 마스크 비트가 1이면 그 NAME 비트가 일치해야 하고, 0이면 무시해도 된다. 모두 1(0xFF × 8)이면 정확히 그 작업기만 맞고, Identity Number(NAME의 맨 아래 21비트에 있는 장치 고유 번호) 비트만 0이면 같은 기종 여러 대 가운데 아무것이나 맞는다. 검색어의 와일드카드와 비슷하다. SCM은 마스크보다 더 엄격하게 걸러도 된다. SCC NAME 자체는 SCD에 없고, SCM이 SCD와 함께 따로 저장한다.
- <strong>Version Label</strong>: ISO/IEC 8859-1(라틴 문자 집합)의 보이는 문자만 쓰고 길이에 맞게 뒤를 공백으로 채운다. 운전자에게 보이거나 파일 이름 일부로 쓰일 수 있어서 역슬래시, 큰따옴표, 작은따옴표, 백틱, 슬래시, 콜론, 별표, 부등호 두 개, 세로선, 물음표 11자는 금지다. 내용은 SCC 제조사 고유이고 검사 책임은 SCC에 있지만, SCM도 기록된 시퀀스(SCS)의 무결성을 위해 SCS를 정의할 때 쓴 두 레이블(Version Label과 Configuration Label)을 추적해야 한다.
- <strong>Designator</strong>: 화면에 보일 이름 글자다. 길이 제한은 VT string 오브젝트의 제약뿐이다. SCM이 화면에 맞게 자를 수 있지만 최소 32자는 보여야 한다.
- <strong>Preferred trigger</strong>: 이 기능에 알맞은 trigger(실행 시점을 정하는 기준)를 SCC가 추천하는 값이다. 1 시간 기반, 2 거리 기반, 255 상관없음 가운데 하나만 지정한다. SCM은 모든 trigger 방식을 지원할 의무도, 이 선호를 따를 의무도 없다.
- <strong>Function value 표시</strong>: 저장·전송되는 값은 항상 32비트 unsigned(부호 없는 정수)다. 화면 값 = (값 + Offset) × Scale이고, 역변환은 값 = 화면 값 / Scale − Offset이다. Min·Max도 같은 식으로 스케일링해 입력 범위로 쓴다. Attributes의 Bit 0-1이 00이면 SCM은 값을 표시하지 않고, 01이면 편집 화면에 표시만 하고, 10이면 표시하면서 범위 안의 변경을 허용한다. Min·Max는 00·01일 때, Offset·Scale·decimals·Unit String은 00일 때 FF로 채운다. FF는 "쓰지 않는 칸"이라는 표시다.

예를 들어 3점 히치 위치를 0~10 000(0.01 % 단위)으로 보내는 SCC가 Offset 0, Scale 0.01, decimals(소수 자릿수) 1로 정의하면, 기록된 값 7 500은 화면에 (7 500 + 0) × 0.01 = 75.0으로 보인다. SCC는 히치가 멈춘 위치를 이 값에 담아 완료를 보고하고, 재생 때 같은 값을 돌려받아 같은 높이에서 멈춘다.

<small>근거: ISO 11783-14 4.4.8, A.1~A.5</small>

## 2. SCD 레코드의 바이트 배치 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절에서는 세 오브젝트를 실제 바이트로 어떻게 적는지 본다. 표를 읽는 법은 다음과 같다.

- 바이트 번호는 1부터 센다. "1-2"는 1번과 2번 바이트 두 개를 묶어 값 하나를 담는다는 뜻이다.
- 여러 바이트로 된 값은 LSB 우선(little-endian: 낮은 자리 바이트가 먼저)으로 가정한다. SC 표준이 바이트 순서를 따로 적지 않기 때문이다([53장](/study/isobus/53-sequence-control-basics)의 표기 규칙).
- N, M, O, S는 레이블 길이나 하위 오브젝트 개수다. 레코드 전체 길이가 이 값에 따라 달라진다.

세 오브젝트의 레코드 바이트 배치는 다음과 같다. 속성의 뜻과 값 범위 전체는 [표준 정리: Part 14](/study/isobus/appendix-iso-part14)에 있다.

| 오브젝트 | 레코드 바이트 배치 | 전체 길이 |
|---|---|---|
| basic (Type 0) | 1-2 Object ID(=0) · 3 Type · 4 SC Version · 5-12 SCCWS Master NAME · 13-20 SCC NAME Mask · 21-22 SCD Designator · 23-24 SCD Graphic · 25 Version Label 길이 N · 26 Configuration Label 길이 M · 27 function object 수 O · 28~ Version Label, Configuration Label, function object ID × O | 27 + N + M + 2O |
| function (Type 1) | 1-2 Object ID · 3 Type · 4 Function ID · 5 Preferred trigger · 6 Attributes · 7-10 Min · 11-14 Max · 15-18 Offset · 19-22 Scale · 23 number of decimals · 24-25 Unit String · 26-27 Designator · 28-29 Graphic · 30 state object 수 S · 31~ state object ID × S | 30 + 2S |
| state (Type 2) | 1-2 Object ID · 3 Type · 4 State ID · 5-6 Designator · 7-8 Graphic | 8 |

Designator, Graphic, Unit String 칸에는 글자나 그림 자체가 아니라, SCC가 VT에 올린 오브젝트의 ID(2바이트)가 들어간다. 그래서 오브젝트 ID 하나마다 2바이트씩 차지한다.

아래 Python 예제가 만드는 basic object의 고정부 27바이트를 표대로 읽어 보자.

`00 00 00 02 78 56 34 12 00 81 0C A0 00 00 E0 FF FF FF FF FF 3B 00 3C 00 08 07 01`

| 바이트 | 값 | 뜻 |
|---|---|---|
| 1-2 | `00 00` | Object ID 0. basic object는 항상 0이다 |
| 3 | `00` | Type 0(basic) |
| 4 | `02` | SC Version 2 |
| 5-12 | `78 56 34 12 00 81 0C A0` | SCCWS Master NAME. 낮은 자리부터 왔으므로 거꾸로 읽으면 0xA00C810012345678이다 |
| 13-20 | `00 00 E0 FF FF FF FF FF` | NAME Mask 0xFFFFFFFFFFE00000. 맨 아래 21비트가 0이라 Identity Number를 무시한다 |
| 21-22 | `3B 00` | SCD Designator가 가리키는 오브젝트 ID 0x003B |
| 23-24 | `3C 00` | SCD Graphic이 가리키는 오브젝트 ID 0x003C |
| 25 | `08` | Version Label 길이 N = 8("SW 2.1.0") |
| 26 | `07` | Configuration Label 길이 M = 7("3PH+PTO") |
| 27 | `01` | function object 수 O = 1 |

28번 바이트부터 Version Label 8바이트, Configuration Label 7바이트, function object ID 1개(2바이트)가 이어진다. 그래서 basic object 전체는 27 + 8 + 7 + 2 = 44바이트다.

::: warning Scale 필드의 0xFFFFFFFF
표시 방식이 00이면 Scale(Float) 자리에도 0xFFFFFFFF를 넣는다. 이 비트 패턴을 IEEE 754로 읽으면 NaN(숫자가 아님)이다. 파서는 Float로 해석하기 전에 원시 4바이트가 0xFFFFFFFF인지 먼저 확인하는 편이 안전하다(추론).
:::

다음 예제는 세 오브젝트의 레코드를 바이트로 만들고, NAME Mask 비교와 화면 값 계산을 확인한다. SC 표준은 오브젝트 레코드의 모양만 정하고, SCDTransfer 메시지의 Byte 2~N에 레코드를 어떤 순서로 이어 붙일지는 따로 적지 않는다. 아래 예제는 VT 오브젝트 풀처럼 basic → function → state 순서로 이어 붙인다고 가정한다. 다중 바이트 값은 LSB 우선으로 가정한다.

::: details Python으로 SCD 레코드 만들기와 NAME Mask 매칭
```python
import struct

NULL_ID = 0xFFFF
FORBIDDEN = set('\\"\'`/:*<>|?')  # A.3: not allowed in an SCD Version Label


def basic_object(ws_master_name: int, name_mask: int, designator: int, graphic: int,
                 version: str, config: str, function_ids: list, sc_version: int = 2) -> bytes:
    """Table A.1 SCD basic object. Object ID = 0, Type = 0."""
    v, c = version.encode("latin-1"), config.encode("latin-1")
    assert 1 <= len(v) <= 64 and 1 <= len(c) <= 64
    assert not FORBIDDEN & set(version)
    assert 1 <= len(function_ids) <= 255
    head = struct.pack("<HBBQQHHBBB", 0, 0, sc_version, ws_master_name, name_mask,
                       designator, graphic, len(v), len(c), len(function_ids))
    assert len(head) == 27  # record bytes 1-27
    return head + v + c + b"".join(struct.pack("<H", i) for i in function_ids)


def function_object(obj_id: int, fn_id: int, trigger: int, attr: int,
                    vmin: int, vmax: int, offset: int, scale: float, decimals: int,
                    unit: int, designator: int, graphic: int, state_ids: list) -> bytes:
    """Table A.2 SCD function object. Type = 1."""
    assert 1 <= obj_id <= 65534 and trigger in (1, 2, 255) and len(state_ids) <= 64
    body = struct.pack("<HBBBBIIifBHHHB", obj_id, 1, fn_id, trigger, attr,
                       vmin, vmax, offset, scale, decimals, unit, designator, graphic,
                       len(state_ids))
    assert len(body) == 30  # record bytes 1-30
    return body + b"".join(struct.pack("<H", i) for i in state_ids)


def state_object(obj_id: int, state_id: int, designator: int, graphic: int) -> bytes:
    """Table A.3 SCD state object. Type = 2, 8 bytes."""
    assert 1 <= obj_id <= 65534 and 0 <= state_id <= 63
    return struct.pack("<HBBHH", obj_id, 2, state_id, designator, graphic)


def name_matches(stored: int, candidate: int, mask: int) -> bool:
    """A.3: mask bit 1 = this NAME bit shall match, 0 = may be ignored."""
    return (stored ^ candidate) & mask == 0


def displayed(raw: int, offset: int, scale: float) -> float:
    """A.4: Displayed Value = (Value Attribute + Offset) * Scaling Factor."""
    return (raw + offset) * scale


if __name__ == "__main__":
    NAME = 0xA00C810012345678                 # example NAME of the SCC (= its WS master)
    MASK = 0xFFFFFFFFFFE00000                 # ignore the 21-bit Identity Number

    scd = (basic_object(NAME, MASK, designator=0x003B, graphic=0x003C,
                        version="SW 2.1.0", config="3PH+PTO", function_ids=[1])
           + function_object(1, fn_id=0x05, trigger=2, attr=0b10,
                             vmin=0, vmax=10000, offset=0, scale=0.01, decimals=1,
                             unit=0x0040, designator=0x0041, graphic=0x0042, state_ids=[2, 3])
           + state_object(2, state_id=1, designator=0x0043, graphic=0x0044)
           + state_object(3, state_id=2, designator=0x0045, graphic=0x0046))

    assert len(scd) == (27 + 8 + 7 + 2) + (30 + 4) + 8 + 8 == 94
    assert scd[24] == 8 and scd[25] == 7 and scd[26] == 1      # bytes 25, 26, 27
    assert scd[27:35] == b"SW 2.1.0"                           # bytes 28 .. 28+N-1

    mem_req = bytes([0x91]) + struct.pack("<I", len(scd)) + b"\xFF" * 3
    assert mem_req.hex(" ").upper() == "91 5E 00 00 00 FF FF FF"
    transfer = bytes([0x03]) + scd
    assert len(transfer) == 95                                 # > 8 bytes -> TP

    other_unit = NAME ^ 0x000000000001F00F                     # same model, other identity
    assert name_matches(NAME, other_unit, MASK)
    assert not name_matches(NAME, other_unit, 0xFFFFFFFFFFFFFFFF)

    assert round(displayed(7500, 0, 0.01), 2) == 75.0
    print(scd[:27].hex(" ").upper())
    print("SCD bytes:", len(scd), "/ SCDTransfer bytes:", len(transfer))
    print("all asserts passed")
```

실행하면 basic object의 고정부 27바이트 `00 00 00 02 78 56 34 12 00 81 0C A0 00 00 E0 FF FF FF FF FF 3B 00 3C 00 08 07 01`과 전체 크기가 출력되고 모든 assert가 통과한다. SCD가 94바이트(0x5E)이므로 SCMasterMemoryRequest는 `91 5E 00 00 00 FF FF FF`(코드 0x91, 크기 94를 4바이트 LSB 우선, 나머지 FF)이고, SCDTransfer는 Byte 1(`0x03`)을 더한 95바이트라 TP로 보낸다.
:::

<small>근거: ISO 11783-14 A.1~A.5, C.4, D.6</small>

## 3. 메시지 지도: 누가 어떤 코드로 말하나

이 절에서는 SC 메시지 전체를 지도 한 장으로 본다. CAN ID를 어떻게 만드는지, 메시지 코드마다 누가 누구에게 보내는지, 여러 메시지가 함께 쓰는 바이트 규칙이 무엇인지 본다.

PGN(메시지 종류 번호)은 두 개뿐이다. SCM→SCC는 PGN 36352(0x8E00), SCC→SCM은 PGN 36096(0x8D00)이고, 둘 다 PDU1(받는 주소를 지정하는 형식)이라 PS 자리에 목적지 주소가 들어간다. 데이터 길이는 "가변(최소 8바이트)"이다. 기본 우선순위 4는 SC 자동 기능을 덮어쓸 수 있는 VT auxiliary control(조이스틱 같은 보조 입력, [40장](/study/isobus/40-vt-aux))처럼 더 높은 우선순위의 메시지를 방해하지 않으려고 정한 값이다. 예시로 SCM의 주소가 0x8C(=140), SCC의 주소가 0x81(=129)이라고 하면 29비트 CAN ID는 다음과 같다.

| 메시지 | DA | CAN ID |
|---|---|---|
| SCM → SCC (일반) | 0x81 | `0x108E818C` |
| SCC → SCM (일반) | 0x8C | `0x108D8C81` |
| SCMasterStatus (전역 broadcast) | 0xFF | `0x108EFF8C` |
| SCClientAbort (전역) | 0xFF | `0x108DFF81` |

DA(Destination Address)는 받는 쪽 주소이고, 0xFF는 모두에게 보내는 전역 주소다. 첫 줄 `0x108E818C`를 앞에서부터 나눠 읽으면 다음과 같다. 29비트 ID의 구조는 [9장](/study/isobus/09-j1939-message)에서 다뤘다.

- `10`: 우선순위 4. 우선순위 3비트가 이 바이트의 위쪽에 있어서, 4를 왼쪽으로 2비트 민 값 0x10이 된다.
- `8E`: PF(PDU Format). PGN 0x8E00의 앞 바이트다.
- `81`: PS(PDU Specific). PDU1이므로 받는 쪽 주소, 곧 SCC(0x81)다.
- `8C`: SA(Source Address). 보내는 쪽 주소, 곧 SCM(0x8C)이다.

메시지 종류는 Byte 1의 message code로 가른다.

| code | 메시지 | 방향 | 응답·확인 |
|---|---|---|---|
| 0x01~0x07 | SCD operation: Version, ConfigurationLabel, Transfer, Activation, Delete, Store, Load | SCC 요청 → SCM 응답 | 같은 code의 Response |
| 0x30 | SCStateCommand | SCM → SCC | 전용 응답 없음. SCClientStatus Byte 2로 확인 |
| 0x31 | SCClientAbort | SCC → 전역 | SCMasterStatus의 Abort |
| 0x32 | SCExecutionIndication / Response | SCC → SCM / SCM → SCC | Response가 확인 |
| 0x33 | SCMasterExecutionCommand | SCM → SCC | SCClientExecutionStatus |
| 0x34 | SCClientExecutionStatus / Acknowledgement | SCC → SCM / SCM → SCC | Acknowledgement가 확인 |
| 0x35 | SCClientFunctionErrorRequest / Response | SCM → SCC / SCC → SCM | Response |
| 0x90 | SCMasterCapabilityRequest / Response | SCC → SCM / SCM → SCC | Response (10바이트) |
| 0x91 | SCMasterMemoryRequest / Response | SCC → SCM / SCM → SCC | Response |
| 0x95 | SCMasterStatus | SCM → 전역 | 없음(상태 방송) |
| 0x96 | SCClientStatus | SCC → SCM | 없음(상태 보고) |

코드는 모두 16진수다(0x30~0x35는 10진수 48~53, 0x90·0x91은 144·145, 0x95·0x96은 149·150). 요청과 응답이 같은 code를 쓰므로 방향은 PGN으로 가른다. 0x34는 PGN 0x8D00이면 SCClientExecutionStatus, 0x8E00이면 SCClientExecutionAcknowledgement다.

<strong>시퀀스 번호.</strong> 상태 메시지의 Byte 3 시퀀스 번호는 0x00~0x31(10진 0~49)이고, Ready일 때와 SCM inactive·SCC disabled일 때는 0xFF다. 표준이 범위를 16진수로 적으므로 0~31로 읽으면 안 된다. SCC가 싣는 번호는 지금 SCExecutionIndication을 보내거나 SCMasterExecutionCommand를 실행 중인 시퀀스의 번호이고, 진단 용도로만 쓴다.

<strong>Byte 3에 두 값을 함께 담는 법.</strong> 기록·재생 메시지(SCExecutionIndication과 그 Response, SCClientExecutionStatus와 그 Acknowledgement)의 Byte 3은 Bits 1-6에 State ID, Bits 7-8에 function execution state(실행 상태)를 담는다. 비트는 1~8로 세고 Bit 1이 최하위다. 실행 상태 00은 시작과 완료가 동시, 01은 시작, 10은 완료, 11은 실행 중 오류다. SCExecutionIndication의 11은 재생 중 운전자 개입도 뜻한다. State ID가 2라면 00 → `0x02`, 01 → `0x42`, 10 → `0x82`, 11 → `0xC2`다. SCMasterExecutionCommand는 Bits 7-8을 0으로 둔다.

![Byte 3 비트 배치: 0x42를 2진수 0100 0010으로 펼치면 위 2비트(Bits 7-8) 01은 실행 상태 시작, 아래 6비트(Bits 1-6) 000010은 State ID 2다](/images/study-isobus/54-byte3-bits-light.png)
![Byte 3 비트 배치: 0x42를 2진수 0100 0010으로 펼치면 위 2비트(Bits 7-8) 01은 실행 상태 시작, 아래 6비트(Bits 1-6) 000010은 State ID 2다](/images/study-isobus/54-byte3-bits-dark.png)

::: warning TAN과 error code의 바이트 위치가 메시지마다 다르다
| 메시지 | Byte 4 | Byte 5 | 나머지 |
|---|---|---|---|
| SCExecutionIndication | TAN | function value 시작 | Byte 5~8 function value. 시작만 알리면 FFFFFFFF |
| SCExecutionIndicationResponse | error code | TAN | Byte 6~8 FF |
| SCMasterExecutionCommand | TAN | function value 시작 | Byte 5~8 function value |
| SCClientExecutionStatus | error code | TAN | Byte 6~8 FF |
| SCClientExecutionAcknowledgement | TAN | FF | Byte 5~8 FF |

error code가 없는 SCExecutionIndication, SCMasterExecutionCommand, SCClientExecutionAcknowledgement는 TAN이 Byte 4에 있고, error code를 싣는 SCExecutionIndicationResponse와 SCClientExecutionStatus는 error code가 Byte 4, TAN이 Byte 5다. SCClientExecutionAcknowledgement는 응답이지만 error code가 없어 TAN이 Byte 4에 온다. SCStateCommand는 Byte 3을, SCClientAbort는 Byte 2~3을 예약으로 비워 두는데, 표준은 "error code를 모든 메시지에서 같은 바이트에 두려고"라고 이유를 단다. 그래서 SCClientAbort의 error code도 Byte 4다. 파서를 메시지 종류별로 따로 짜야 하는 이유다.
:::

<small>근거: ISO 11783-14 B.1~B.3, Annex C~F(E.2~E.8, F.2, F.3)</small>

## 4. 재생 한 스텝을 바이트로 따라가기

이 절에서는 재생 중 스텝 하나가 실행되는 동안 오가는 프레임 여섯 개를 바이트마다 읽는다. 3절의 지도를 실제 프레임에 대 보는 연습이다.

상황은 이렇다. 시퀀스 0x02를 재생 중이고, SCM이 function 0x05(3점 히치)의 state 2(상승)를 function value 7 500으로 명령한다. SCM의 직전 TAN은 0x11이었다고 하자. 그래서 이번 명령의 TAN은 1 올린 0x12(=18)다.

![재생 한 스텝의 메시지 순서: SCM이 상태를 방송하고 실행 명령을 보내면, SCC가 실행 시작을 보고하고 SCM이 확인하며, 히치가 멈춘 뒤 SCC가 완료를 보고하고 SCM이 다시 확인한다](/images/study-isobus/54-playback-step-light.png)
![재생 한 스텝의 메시지 순서: SCM이 상태를 방송하고 실행 명령을 보내면, SCC가 실행 시작을 보고하고 SCM이 확인하며, 히치가 멈춘 뒤 SCC가 완료를 보고하고 SCM이 다시 확인한다](/images/study-isobus/54-playback-step-dark.png)

| # | 방향 | CAN ID | 데이터 | 뜻 |
|---|---|---|---|---|
| 1 | SCM → 전역 | `0x108EFF8C` | `95 01 02 04 00 FF FF FF` | SCMasterStatus: Active, 시퀀스 0x02, Play back, busy 없음 |
| 2 | SCM → SCC | `0x108E818C` | `33 05 02 12 4C 1D 00 00` | 실행 명령: function 0x05, state 2, TAN 0x12, value 7 500(0x1D4C) |
| 3 | SCC → SCM | `0x108D8C81` | `34 05 42 00 12 FF FF FF` | 실행 시작(01), error 00, TAN 0x12 |
| 4 | SCM → SCC | `0x108E818C` | `34 05 42 12 FF FF FF FF` | 시작 확인. TAN은 Byte 4 |
| 5 | SCC → SCM | `0x108D8C81` | `34 05 82 00 12 FF FF FF` | 실행 완료(10), TAN 0x12 |
| 6 | SCM → SCC | `0x108E818C` | `34 05 82 12 FF FF FF FF` | 완료 확인 |

2번 프레임 `33 05 02 12 4C 1D 00 00`을 바이트마다 읽으면 다음과 같다.

1. `33`: SCMasterExecutionCommand(실행 명령)다.
2. `05`: Function ID 0x05, 곧 3점 히치다.
3. `02`: Byte 3. 아래 6비트가 State ID 2(상승)이고, 위 2비트는 이 메시지에서 쓰지 않아 00이다.
4. `12`: TAN 0x12다.
5. `4C 1D 00 00`: function value. 낮은 자리부터 왔으므로 거꾸로 읽으면 0x00001D4C = 7 500이다.

3번 프레임 `34 05 42 00 12 FF FF FF`은 SCClientExecutionStatus다. `05`는 같은 기능, `42`는 실행 상태 01(시작)과 State ID 2, `00`은 error code 없음, `12`는 명령과 같은 TAN, 마지막 `FF FF FF`는 쓰지 않는 자리다. 4번 확인 프레임은 error code가 없어서 TAN `12`가 한 칸 앞의 Byte 4로 온다.

반복 규칙도 같이 본다. SCM은 2번을 같은 TAN으로 100 ms마다 반복하다가 3번이 오면 멈춘다. SCC는 3번을 100 ms마다 반복하다가 4번을 받거나, SCM이 Abort로 바뀌거나, 타임아웃이 나거나, 완료를 보고할 시점(5번)에 이르면 멈춘다. 받은 응답의 TAN, function ID, state ID 가운데 하나라도 다르면 무시한다.

다음 코드는 위 표의 바이트를 만들고 되읽는다. function value의 바이트 순서는 LSB 우선으로 가정했다.

::: details Python으로 SC 메시지 인코딩·디코딩
```python
import struct

# ISO 11783-14 message codes (Byte 1). The standard writes them in hex (30₁₆ ...).
SC_STATE_COMMAND        = 0x30  # E.2  SCM -> SCC
SC_CLIENT_ABORT         = 0x31  # E.3  SCC -> global
SC_EXEC_INDICATION      = 0x32  # E.4 / E.5 (request and response share the code)
SC_MASTER_EXEC_COMMAND  = 0x33  # E.6  SCM -> SCC
SC_CLIENT_EXEC_STATUS   = 0x34  # E.7 / E.8
SC_FUNCTION_ERROR       = 0x35  # E.9 / E.10
SC_MASTER_STATUS        = 0x95  # F.2  SCM -> broadcast
SC_CLIENT_STATUS        = 0x96  # F.3  SCC -> SCM

PGN_SCM_TO_SCC = 0x8E00  # 36352 (B.2)
PGN_SCC_TO_SCM = 0x8D00  # 36096 (B.3)

SEQ_STATE = {0x01: "Ready", 0x02: "Recording", 0x03: "Recording completion",
             0x04: "Play back", 0x05: "Abort", 0xFF: "n/a"}
EXEC_STATE = {0b00: "started+completed", 0b01: "started",
              0b10: "completed", 0b11: "error"}


def can_id(pgn: int, da: int, sa: int, priority: int = 4) -> int:
    """29-bit identifier for a PDU1 PGN (PF < 240): DA goes into the PS field."""
    return (priority << 26) | ((pgn >> 8) << 16) | (da << 8) | sa


def pack_state(state_id: int, exec_state: int) -> int:
    """Byte 3: bits 1-6 = state ID, bits 7-8 = function execution state."""
    assert 0 <= state_id <= 63 and 0 <= exec_state <= 3
    return (exec_state << 6) | state_id


def unpack_state(b3: int) -> tuple:
    return b3 & 0x3F, (b3 >> 6) & 0x03


def master_status(state: int, seq_no: int, seq_state: int, busy: int = 0) -> bytes:
    return bytes([SC_MASTER_STATUS, state, seq_no, seq_state, busy, 0xFF, 0xFF, 0xFF])


def parse_status(frame: bytes) -> dict:
    code, state, seq_no, seq_state, b5 = frame[:5]
    assert code in (SC_MASTER_STATUS, SC_CLIENT_STATUS)
    out = {"code": hex(code), "state": state, "seq_no": seq_no,
           "seq_state": SEQ_STATE.get(seq_state, f"reserved({seq_state:#04x})")}
    if code == SC_MASTER_STATUS:
        out["nvm_busy"] = bool(b5 & 0x01)   # Bit 1
        out["parsing"] = bool(b5 & 0x02)    # Bit 2
    else:
        out["error_state"] = b5             # ClientFunctionErrorState
    return out


def master_exec_command(fn_id: int, state_id: int, tan: int, value: int) -> bytes:
    # E.6: bits 7-8 of byte 3 are reserved (0); function value assumed LSB first
    return bytes([SC_MASTER_EXEC_COMMAND, fn_id, pack_state(state_id, 0), tan]) + struct.pack("<I", value)


def client_exec_status(fn_id: int, state_id: int, exec_state: int, err: int, tan: int) -> bytes:
    # E.7: error code in byte 4, TAN in byte 5
    return bytes([SC_CLIENT_EXEC_STATUS, fn_id, pack_state(state_id, exec_state), err, tan, 0xFF, 0xFF, 0xFF])


def exec_ack(fn_id: int, state_id: int, exec_state: int, tan: int) -> bytes:
    # E.8: TAN in byte 4 (not byte 5)
    return bytes([SC_CLIENT_EXEC_STATUS, fn_id, pack_state(state_id, exec_state), tan, 0xFF, 0xFF, 0xFF, 0xFF])


def parse_function_errors(frame: bytes) -> list:
    """E.10: Byte 2 = count, then 2-byte structures (function ID, error status)."""
    assert frame[0] == SC_FUNCTION_ERROR
    out = []
    for i in range(frame[1]):
        fn_id, b = frame[2 + 2 * i], frame[3 + 2 * i]
        out.append({"function_id": fn_id, "status": b & 0x0F, "confirm": bool(b & 0x80)})
    return out


if __name__ == "__main__":
    SCM, SCC = 0x8C, 0x81  # example source addresses

    assert can_id(PGN_SCM_TO_SCC, SCC, SCM) == 0x108E818C
    assert can_id(PGN_SCC_TO_SCM, SCM, SCC) == 0x108D8C81
    assert can_id(PGN_SCM_TO_SCC, 0xFF, SCM) == 0x108EFF8C   # SCMasterStatus, global
    assert can_id(PGN_SCC_TO_SCM, 0xFF, SCC) == 0x108DFF81   # SCClientAbort, global

    st = master_status(0x01, 0x02, 0x04)
    assert st.hex(" ").upper() == "95 01 02 04 00 FF FF FF"
    assert parse_status(st)["seq_state"] == "Play back"

    cmd = master_exec_command(0x05, 0x02, 0x12, 7500)
    assert cmd.hex(" ").upper() == "33 05 02 12 4C 1D 00 00"

    started = client_exec_status(0x05, 0x02, 0b01, 0x00, 0x12)
    assert started.hex(" ").upper() == "34 05 42 00 12 FF FF FF"
    assert unpack_state(started[2]) == (2, 0b01)
    ack = exec_ack(0x05, 0x02, 0b01, 0x12)
    assert ack.hex(" ").upper() == "34 05 42 12 FF FF FF FF"
    done = client_exec_status(0x05, 0x02, 0b10, 0x00, 0x12)
    assert done.hex(" ").upper() == "34 05 82 00 12 FF FF FF"

    # The same code 0x34 in both directions: only the PGN tells E.7 and E.8 apart
    assert started[0] == ack[0] == SC_CLIENT_EXEC_STATUS

    errs = parse_function_errors(bytes.fromhex("35 02 05 82 07 03 FF FF"))
    assert errs == [{"function_id": 5, "status": 2, "confirm": True},
                    {"function_id": 7, "status": 3, "confirm": False}]

    for f in (st, cmd, started, ack, done):
        print(f.hex(" ").upper())
    print("all asserts passed")
```

실행하면 위 표의 1~5번 프레임이 차례로 출력되고 모든 assert가 통과한다. `pack_state`는 실행 상태를 6비트 왼쪽으로 밀어 State ID와 합치고, `unpack_state`는 `0x3F`로 아래 6비트, `>> 6`으로 위 2비트를 꺼낸다.
:::

<small>근거: ISO 11783-14 4.4.7.1, 4.6, E.6~E.8, F.2</small>

## 5. 주기와 타임아웃

이 절에서는 상태 메시지를 얼마나 자주 보내고, 얼마 동안 오지 않으면 상대가 사라졌다고 보는지 정리한다. 상태 메시지는 심장 박동과 같다. 박동이 일정 시간 멈추면 상대에게 문제가 생겼다고 판단하고 안전한 쪽으로 물러난다.

![상태 메시지와 타임아웃: 활동 상태에서는 200 ms마다 오던 SCMasterStatus가 끊기고 600 ms가 지나면 SCC가 Disabled로 가고, Ready에서는 1 s마다 오던 메시지가 끊기고 3 s가 지나야 타임아웃이다](/images/study-isobus/54-status-timeout-light.png)
![상태 메시지와 타임아웃: 활동 상태에서는 200 ms마다 오던 SCMasterStatus가 끊기고 600 ms가 지나면 SCC가 Disabled로 가고, Ready에서는 1 s마다 오던 메시지가 끊기고 3 s가 지나야 타임아웃이다](/images/study-isobus/54-status-timeout-dark.png)

| 항목 | 값 |
|---|---|
| SCMasterStatus 송신 | Byte 2~5가 바뀌면 즉시. Ready 1회/s, Recording·Recording Completion·Play Back·Abort 5회/s. 메시지 간 최소 100 ms |
| inactive SCM의 SCMasterStatus | 시동 직후 Initialization 1회, 운전자 입력으로 상태가 바뀐 직후 Inactive 1회만 |
| SCMasterStatus 타임아웃 (SCC가 감시) | 활동 상태 600 ms, Ready 3 s |
| SCClientStatus 송신 | Byte 2~5가 바뀌면 즉시. Ready·disabled 1회/s, Recording·Play Back·Abort 5회/s. 메시지 간 최소 100 ms |
| SCClientStatus 타임아웃 (SCM이 감시) | Recording·Play Back·Abort 600 ms, Ready 3 s |
| 명령·요청 반복 (메시지 일반 규칙) | 응답이 올 때까지 초당 최대 5회, 반복 간 최소 100 ms. 최소 1.6 s 동안 응답이 없으면 무응답 |
| 같은 TAN 반복 (기록·재생 절차 설명) | 100 ms 간격 |
| SCD operation 응답 | 개별 타임아웃 없음. busy flag가 켜진 동안 측정 정지 |

활동 상태에서는 송신 주기를 5배로 촘촘히 하고 타임아웃을 600 ms로 줄인다. 600 ms는 200 ms 주기의 3배, 3 s는 1 s 주기의 3배라서 연속 두 메시지를 잃어도 버티도록 잡은 값으로 보인다(추론).

::: warning 반복 주기가 표준 안에서 엇갈린다
메시지 일반 규칙은 반복을 "초당 최대 5회"(간격 200 ms 이상)와 "반복 간 최소 100 ms"로 적고, 기록·재생 절차 설명은 같은 TAN을 "100 ms 간격"으로 반복하라고 적는다. 100 ms 간격은 초당 10회라 "최대 5회"와 글자 그대로는 맞지 않는다. 표준이 둘의 관계를 설명하지 않으므로 확인이 필요하다.
:::

SCMasterStatus가 사라졌을 때의 처리는 SCC 상태에 따라 다르다.

- enabled SCC는 타임아웃 뒤 SCC_D([53장](/study/isobus/53-sequence-control-basics) SCC 상태 표의 "SCMasterStatus 타임아웃" 조건)로 Disabled가 되고, 통신 오류를 감지한 쪽으로서 일반 안전 요구를 고려해 스스로 조치한다.
- 이미 disabled인 SCC는 운전자 경고를 띄우지 말고 정상 종료로 해석해, 새 SC 통신이 시작될 때까지 자기 SCClientStatus도 멈춘다.

SCM이 정상 종료할 때는 Ready를 계속 보내면서 enabled SCC를 모두 disable시키고, 모두 disabled를 반영하면 Inactive를 한 번 알린 뒤 송신을 멈춘다. 이 한 번을 놓친 쪽은 타임아웃으로 종료를 판단한다.

SCC가 SC 통신에서 빠질 때는 먼저 SCClientStatus Byte 2를 Disabled로 바꾸고, 첫 NACK(Negative Acknowledgement, "받았지만 처리하지 않는다"는 거절 응답)을 받을 때까지 계속 보낸다. SCM이 불필요한 타임아웃 경고를 띄우지 않게 하려는 절차다.

<small>근거: ISO 11783-14 4.4.4.1, 4.4.4.2, 4.4.5.2, 4.4.7.1, 4.5.2, D.1, E.1, F.2, F.3</small>

## 6. 기록할 때 TAN과 실행 상태 다루기

이 절에서는 기록 중 SCC가 조작을 알리고 SCM이 저장하는 과정을 TAN과 실행 상태 중심으로 본다. 같은 기능을 연달아 조작해도 기록이 꼬이지 않는 이유가 여기에 있다.

SCM은 SCC가 기능 실행 시작을 보고할 때 trigger를 기록하고, 완료를 보고할 때 function value를 기록한다. 시작과 완료를 모두 받은 기능만 SCS(기록된 시퀀스)에 저장되고, 00(시작·완료 동시)은 둘을 한 번에 알린다. SCC는 다음을 지킨다.

- 기능을 활성화할 때마다 자기 TAN을 1 올린 SCExecutionIndication을 보낸다. SCM이 Ready로 돌아가거나, 타임아웃이 나거나, SCExecutionIndicationResponse로 확인할 때까지 같은 TAN으로 100 ms마다 반복한다.
- 시작만 알리는 표시의 function value(Byte 5~8)는 FFFFFFFF다. 아직 결과 값이 없다는 표시다.
- 고장 난 기능은 SCExecutionIndication을 보내지 않는다. Task Controller([41장](/study/isobus/41-tc-basics)) 같은 다른 시스템의 명령으로 생긴 동작도 보통 보고하지 않는다. 조작 한 번이 붐 상승과 유량 차단을 함께 일으키면 command 두 개로 보고해도, 복합 command 하나로 보고해도 된다.

SCM의 SCExecutionIndicationResponse Byte 4가 저장 결과다.

| Byte 4 | 뜻 |
|---|---|
| 00 | 저장됨 |
| 01 | 정의되지 않은 Function ID |
| 02 | 정의되지 않은 State ID |
| 03 | 실행 상태 불일치 |
| 04 | SCM 메모리 부족 |
| 05 | 재생은 계속하되 이 기능에는 더 명령하지 않는다(재생 중 실행 상태 11에 대한 응답 전용) |
| 06 | 운전자 개입으로 재생을 멈췄다(재생 중 실행 상태 11에 대한 응답 전용) |
| FF | 기타 |

00이 아니면 SCC가 운전자에게 폐기 사실을 알릴 수 있다.

완료 전에 같은 기능을 다시 조작하는 경우를 바이트로 보면 TAN 처리가 분명해진다. 운전자가 히치 상승(state 2)을 시작하고, 끝나기 전에 하강(state 1)을 누른 경우다.

| # | 방향 | 데이터 | 뜻 |
|---|---|---|---|
| 1 | SCC → SCM | `32 05 42 07 FF FF FF FF` | 상승 시작(01), TAN 0x07, value 없음 |
| 2 | SCM → SCC | `32 05 42 00 07 FF FF FF` | 저장 확인(error 00). TAN은 Byte 5 |
| 3 | SCC → SCM | `32 05 82 07 4C 1D 00 00` | 같은 TAN으로 상승 완료(10), 멈춘 위치 7 500 |
| 4 | SCM → SCC | `32 05 82 00 07 FF FF FF` | 완료 확인 |
| 5 | SCC → SCM | `32 05 41 08 FF FF FF FF` | 곧바로 TAN 0x08로 하강 시작(01) |

읽는 요령은 이렇다. 1번의 `42`는 실행 상태 01과 State ID 2, 3번의 `82`는 실행 상태 10과 State ID 2, 5번의 `41`은 실행 상태 01과 State ID 1이다. 상승은 시작부터 완료까지 TAN 0x07 하나로 묶이고, 새 조작인 하강은 TAN 0x08로 새로 시작한다. 그래서 SCM은 3번이 1번 상승의 완료라는 것을 헷갈리지 않는다.

다른 기능을 이전 기능이 끝나기 전에 시작하는 경우(예: 히치가 내려가는 도중 특정 높이에서 PTO를 켬)도 기능마다 TAN이 달라 command와 응답이 섞이지 않는다. 그래서 SC에서는 미결 command(아직 응답을 받지 못한 명령)가 동시에 여러 개 있을 수 있다.

<small>근거: ISO 11783-14 4.4.5.2, 4.4.8, 4.6, E.4, E.5</small>

## 7. 재생할 때 실행 상태와 시퀀스 검증

이 절에서는 재생 중 SCC가 실행 상태를 어떻게 보고하는지, 운전자가 끼어들면 무슨 일이 생기는지, 재생 전에 SCM이 시퀀스를 어떻게 검증하는지 본다.

SCClientExecutionStatus 보고도 기록과 짝을 이룬다.

- 시작과 완료가 동시면 00을 한 번 보낸다.
- 오래 걸리면 01(시작)을 보낸 뒤 10(완료)을 보낸다.
- 도중에 오류가 나면 01 뒤 11을 보내고, 완료는 보내지 않는다.
- 고장 난 기능에 명령이 오면 바로 11과 error code(01 기능 오류, 02 운전자 개입, 03 SCC 조건상 실행 불가)를 보낸다.
- 실행 중인 기능에 새 명령이 겹치면, 먼저 첫 명령의 TAN으로 완료(10)를 보내고 곧바로 둘째 명령의 TAN으로 해당 상태를 보낸다.

재생 중 운전자가 기능을 손으로 조작하면 SCC는 SCExecutionIndication에 11을 실어 알린다. SCM은 다음 가운데 하나를 고를 수 있다.

- 전체 재생을 Abort한다(SCM_F*, [53장](/study/isobus/53-sequence-control-basics)의 상태 표).
- 이번 재생 동안 그 기능에만 명령을 보내지 않는다(Response error 05).
- 그냥 무시한다.

다만 메시지 응답 자체는 생략할 수 없다. SCM이 타임아웃 안에 올바른 TAN·function ID·state ID의 응답을 받지 못하면 재생을 멈춘다.

TAN은 File Server([51장](/study/isobus/51-file-server-basics))에도 있지만 쓰임새가 다르다.

| 항목 | SC (ISO 11783-14) | FS (ISO 11783-13) |
|---|---|---|
| TAN 카운터 | 참여자마다(SCM·SCC 각자). 새 command를 시작하는 쪽이 1씩 올린다 | 클라이언트마다. FS는 카운터가 없다 |
| 동시 미결 명령 | 여러 개 가능 (기능마다 다른 TAN) | 하나뿐 (응답 전에 다음 명령 금지) |
| 응답 짝 맞춤 | TAN, function ID, state ID 셋 다 일치 | TAN 일치 |
| 재전송 처리 | 같은 TAN 반복을 같은 명령으로 인식 | FS가 클라이언트별 직전 TAN·응답을 기억해 실행 없이 재전송 |
| 반복 주기 | 100 ms (메시지 일반 규칙은 초당 최대 5회) | 타임아웃 뒤 재요청 (busy가 아니면 600 ms) |

<strong>검증, 편집, 저장.</strong> active SCM은 다음 순간마다 선택된 시퀀스를 재생 전에 검증한다: 저장된 시퀀스를 불러온 뒤, SCClientStatus 타임아웃 뒤, 수동 정의·편집을 마친 뒤, SCC의 예기치 않은 상태 변화 뒤, SCD 업로드 뒤. 요건은 두 가지다.

1. SCC·Working Set Master의 64비트 NAME(NAME Mask 적용)과 SCD Version·Configuration Label이 시퀀스에 저장된 값과 일치한다.
2. 시퀀스의 모든 기능이 로드된 SCD에 있다.

Manual Edit(수동 편집)는 SCM 내부 상태라 SCC에 알리지 않고, 그동안 SCMasterStatus는 Ready에 시퀀스 번호 0xFF를 싣는다. 운전자가 바꿀 수 없게 정의된 function value는 새 스텝에서 FFFFFFFF로 두고 기존 스텝에서는 보존한다. 시퀀스를 저장하는 SCM은 나중에 불러올 때 무결성을 검사할 수 있게(예: 체크섬, 데이터 손상을 확인하는 검사 값) 저장해야 하고, 손상된 시퀀스는 불러오지 않는다.

<small>근거: ISO 11783-14 4.4.5.3, 4.4.6, 4.4.7.2, 4.4.9.1, 4.4.9.2, 4.6; ISO 11783-13 5.3, C.1.1</small>

## 8. 오류 처리: 기능 고장, Abort, 규칙을 어기는 참여자

이 절에서는 일이 잘못됐을 때의 규칙을 본다. 기능 하나가 고장 났을 때, 재생을 당장 멈춰야 할 때, 참여자가 규칙을 어길 때를 차례로 다룬다.

### 기능 고장 보고

SCC는 SCClientStatus Byte 5(ClientFunctionErrorState)로 기능 상태를 늘 알린다. 자동차 계기판의 경고등처럼 "무언가 바뀌었다"만 먼저 알리고, 자세한 내용은 SCM이 물어볼 때 답한다.

| 값 | 뜻 | SCM의 의무 |
|---|---|---|
| 0x00 | 오류 없음 | 없음 |
| 0x01 | 마지막 상세 보고 이후 오류 상태 변화 없음 | 없음 |
| 0x02 | 변화 있음. SCM 조치는 필요 없음(SCC가 자체 경고하는 경우 등) | 상세 요청은 선택(may) |
| 0x03 | 운전자 확인이 필요한 변화 있음. 0x02보다 우선한다 | 상세 요청 필수(shall) |
| 0xFF | disabled | 없음 |

상세는 SCClientFunctionErrorRequest(`35 FF FF FF FF FF FF FF`)로 묻는다. SCC는 Response에 기능당 2바이트 구조(function ID, 오류 상태)를 실어 답한 뒤 Byte 5를 0x01로 되돌린다. 오류 상태의 Bits 1-4는 01 일회성, 02 영구, 03 잠김(locked), 04 운전자가 SCC에서 비활성화, 0F 기타이고, Bit 8이 1이면 운전자 확인이 필요하다. Bit 8은 자체 화면이 없는 SCC가 SCM에 알림을 맡길 때 쓰는 비트이고, SCM은 Bit 8이 켜진 기능을 즉시 운전자에게 알려야 한다.

예를 들어 `35 02 05 82 07 03 FF FF`는 구조 2개다. 바이트마다 읽으면 다음과 같다.

1. `35`: SCClientFunctionErrorResponse다.
2. `02`: 구조 개수 2.
3. `05 82`: function 0x05의 오류 상태 0x82(2진수 `1000 0010`). Bits 1-4가 02(영구 오류)이고 Bit 8이 1(확인 필요)이다.
4. `07 03`: function 0x07의 오류 상태 0x03. 잠김이고 Bit 8이 0이라 확인이 필요 없다.
5. `FF FF`: 빈자리를 채운 값이다.

구조가 3개 미만이면 FF로 8바이트를 채우고, 3개면 정확히 8바이트, 4개부터는 TP가 필요하다.

기능 고장에 대한 조치 책임은 SCC에 있다. 진행 중 동작을 멈추거나 추가 명령을 무시하는 식이다. SCM은 SCC가 고장 해소를 알릴 때까지 그 기능의 스텝을 건너뛸 수 있고, 다음 시퀀스에서도 계속 건너뛸 수 있다.

### Abort: 재생을 당장 멈춰야 할 때

재생을 멈춰야 하는 SCC는 SCM의 Abort 상태를 받을 때까지 전역 SCClientAbort를 반복하고, 자기 SCClientStatus에도 Abort를 싣는다. Byte 4 error code는 01 상태 메시지 타임아웃, 02 운전자 상호작용, 03 기능 실행 중 오류, FF 기타다. 운전자가 작업기 쪽 정지 버튼을 눌렀다면 CAN ID `0x108DFF81`, 데이터 `31 FF FF 02 FF FF FF FF`가 된다. `31`은 SCClientAbort, 이어진 `FF FF`는 예약 자리, `02`는 운전자 상호작용, 나머지 `FF`는 쓰지 않는 자리다.

- Abort 동안 SCC는 이번 시퀀스에서 SCM이 명령했던 기능만 SCC가 정의한 safe state(안전 상태)로 보낸다. SCM이 명령하지 않은 기능은 건드리지 않는다.
- SCMasterStatus와 SCClientStatus는 Abort 중에도 계속 보낸다.
- SCM은 모든 enabled SCC의 Abort 반영을 확인하면 Ready로 돌아간다(SCM_T). 중단된 재생은 SCM에 대한 운전자의 명시적 확인 없이는 다시 시작할 수 없다.

### 규칙을 어기는 참여자와 통신 장애

규칙을 어기는 SCC에 대해 SCM이 쓰는 수단은 하나로 모인다. 그 SCC의 SCD를 휘발성 메모리(전원이 꺼지면 지워지는 작업용 메모리)에서 지우고, 이후 SC 메시지를 NACK한다. 로드·검증된 SCD가 초기화 완료의 일부라서, SCD가 지워진 연결은 무효가 되고 SCC는 재초기화할 수밖에 없다. SCM이 이렇게 처리하는 경우는 다음과 같다.

- 응답이나 상태 메시지가 빠졌다.
- SCC가 SCM 상태를 따라오지 않는다.
- enable/disable 명령 뒤 명령·요청의 무응답 기준 시간(최소 1.6 s) 안에 상태를 바꾸지 않았다. 이때 SCM은 SCC가 명령받은 상태를 보고할 때까지 그 SCC에 아무 메시지도 보내지 않는다.
- SCC가 예기치 않게 disabled로 바뀌었다.

초기화 뒤 보내면 안 되는 메시지, 예를 들어 disabled SCC의 SCExecutionIndication도 NACK한다. SCC 쪽은 서로 다른 SCMasterStatus를 받아 active SCM이 둘 이상이라고 판단하면 즉시 Disabled로 간다.

통신 장애에 대한 조치는 누가 감지했느냐에 따라 다르다. SCC는 일반 안전 요구를 고려해 스스로 조치하고, SCM은 선택한 시퀀스에 속한 기능과의 통신 장애를 감지하면 기록·재생을 허용하지 않고, 이미 진행 중이면 기록을 취소하거나 재생을 멈춘다. 장애가 간헐적일 수 있으므로 다시 허용하기 전에 운전자 개입을 요구할 수 있다.

::: info NACK은 어떤 메시지인가
SC 표준은 NACK의 형식을 따로 정하지 않는다. ISO 11783-3(데이터 링크 계층을 정하는 표준 문서)의 Acknowledgement 메시지(PGN 59392, 0xE800)에서 control byte 1(Negative Acknowledgement)을 쓰는 것이 자연스러워 보인다(추론). 이 메시지는 [10장 요청과 응답](/study/isobus/10-j1939-request-ack)에서 다뤘다. SCC는 상태 메시지에 NACK이 오면 언제든 Disabled로 돌아가 연결을 다시 세울 수 있다. PGN 59392는 [PGN·SPN 부록](/study/isobus/appendix-pgn-spn)에도 정리돼 있다.
:::

::: tip SC 구현 체크리스트
- message code는 16진수(SCD operation 0x01~0x07, 0x30~0x35, 0x90·0x91, 0x95·0x96)이고, 요청과 응답은 같은 code를 PGN(0x8E00·0x8D00)으로 구분한다.
- SCM은 모든 enabled SCC가 Ready일 때만 Recording에, 시퀀스의 모든 SCC가 Ready일 때만 Play Back에 들어간다. Abort는 Play Back에서만 생긴다.
- SCC 초기화는 capability(0x90) → 버전·레이블(0x01·0x02) → 메모리(0x91) → 전송(0x03) 또는 로드(0x07) → 활성화(0x04) 순서이고, Enabled는 그 뒤 SCStateCommand로만 받는다.
- SCExecutionIndication, SCMasterExecutionCommand, SCClientExecutionAcknowledgement는 TAN이 Byte 4에 있고, error code를 싣는 SCExecutionIndicationResponse와 SCClientExecutionStatus는 error code가 Byte 4, TAN이 Byte 5다.
- 상태 메시지 타임아웃은 활동 상태 600 ms, Ready 3 s다. 규칙을 어기는 SCC에 대한 SCM의 답은 SCD 삭제와 NACK이다.
:::

<small>근거: ISO 11783-14 4.4.2.2, 4.4.7.3, 4.5, 4.5.1, 4.5.2, 4.5.3.1~4.5.3.6, E.3, E.9, E.10, F.3; ISO 11783-3:2018 5.4.5</small>

::: tip 핵심 정리
- SCD는 basic object 하나, 그 아래 function object 1~255개, 기능마다 state object 0~64개로 된 레코드 묶음이고, 글자와 그림은 VT 오브젝트의 ID로 가리킨다.
- SC 메시지는 PGN 0x8E00(SCM→SCC)과 0x8D00(SCC→SCM)에 실리고, Byte 1의 코드로 종류를, Byte 3의 위 2비트와 아래 6비트로 실행 상태와 State ID를 나타낸다.
- TAN과 error code의 위치는 메시지마다 다르다. error code가 있는 메시지만 TAN이 Byte 5로 밀린다.
- 상태 메시지는 활동 상태에서 초당 5번, Ready에서 초당 1번 오고, 각각 600 ms와 3 s 동안 끊기면 타임아웃이다.
- 기능 고장은 ClientFunctionErrorState로 먼저 알리고 상세는 요청 때 답한다. 재생은 SCClientAbort로 멈추고, 규칙을 어기는 SCC는 SCD 삭제와 NACK으로 재연결시킨다.
:::

::: details 확인 문제
1. (개념) SCD 하나에 function object는 최대 몇 개, 기능 하나에 state object는 최대 몇 개 둘 수 있는가? 그런 한계가 생긴 이유는?
2. (바이트) SCClientExecutionStatus의 Byte 3이 `0x82`다. State ID와 실행 상태는 무엇인가?
3. (TAN) SCM이 function 0x05, state 2, TAN 0x12로 실행 명령을 보냈는데 `34 05 41 00 12 FF FF FF`가 왔다. SCM은 이 프레임을 명령의 응답으로 받아들이는가?
4. (디코딩) 재생 중인 SCM이 PGN 0x8D00으로 SCC에게서 `96 01 02 04 03 FF FF FF`와 `34 05 C2 03 12 FF FF FF`를 연달아 받았다. 두 프레임의 뜻은 무엇이고, SCM은 무엇을 보내야 하는가?
5. (시나리오) Play Back 중 SCC가 SCMasterStatus를 700 ms 동안 받지 못했다. SCC와 SCM은 각각 어느 상태로 가는가? 같은 일이 Ready 상태에서 일어났다면 어떤가?

<strong>답 가이드</strong>
1. function object는 최대 255개, state object는 기능마다 최대 64개다. Function ID가 1바이트, State ID가 6비트이기 때문이고, 이렇게 정한 이유는 관련 CAN 메시지를 8바이트 안에 담기 위해서다.
2. `0x82`는 2진수 `1000 0010`이다. 위 2비트(Bits 7-8) 10은 실행 완료, 아래 6비트(Bits 1-6) 000010은 State ID 2다.
3. 받아들이지 않는다. TAN(0x12)과 function ID(0x05)는 같지만 Byte 3 `0x41`의 State ID가 1이라 명령의 state 2와 다르다. 받는 쪽은 TAN, function ID, state ID가 모두 맞을 때만 응답을 처리하므로 이 프레임은 무시한다.
4. 첫 프레임은 SCClientStatus(0x96)다. Enabled, 시퀀스 0x02, Play back(0x04), ClientFunctionErrorState 0x03(운전자 확인이 필요한 변화)이다. 둘째는 SCClientExecutionStatus(0x34)다. function 0x05, Byte 3 0xC2는 state 2에 실행 상태 11(오류), error code 03은 SCC 조건상 실행 불가, TAN 0x12다. SCM은 먼저 SCClientExecutionAcknowledgement `34 05 C2 12 FF FF FF FF`(TAN은 Byte 4)로 확인한다(4절 "재생 한 스텝을 바이트로 따라가기"). ErrorState가 0x03이므로 SCClientFunctionErrorRequest `35 FF FF FF FF FF FF FF`로 상세를 받아, Bit 8이 켜진 기능을 즉시 운전자에게 알려야 한다(8절의 "기능 고장 보고"). 재생은 Abort(SCM_P*)할 수도, 그 기능을 건너뛰고 계속할 수도 있다.
5. 활동 상태에서 SCMasterStatus 타임아웃은 600 ms다. SCC는 SCC_D로 Disabled가 되고, 통신 오류를 감지한 쪽으로서 안전 요구를 고려해 스스로 조치한다. SCM이 살아 있다면 SCC가 예기치 않게 Disabled로 떨어진 것을 보고 재생을 중단(SCM_R*, Abort)하고, 그 SCC의 SCD를 지우고 메시지를 NACK해 재연결을 강제한다. Ready에서는 타임아웃이 3 s라 700 ms 공백만으로는 아무 일도 일어나지 않는다.
:::

## 다음 챕터

- 다음: [55장 종합 실습 (1): 로그, PGN, VT, TC](/study/isobus/55-practice-log-vt-tc)
