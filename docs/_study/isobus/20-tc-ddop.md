---
title: "TC 디바이스 디스크립션 (DDOP)"
description: "작업기가 자신의 구조와 능력을 TC에 알리는 Device Description Object Pool(DDOP)의 구조, 오브젝트 타입, 전송 과정을 이해한다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, TaskController, TC, DDOP, DeviceDescription, ObjectPool]
prev: /study/isobus/19-tc-process-data
next: /study/isobus/21-tc-task
---

# TC 디바이스 디스크립션 (DDOP)

::: info 학습 목표
- DDOP가 무엇이고 왜 필요한지 설명할 수 있다.
- DDOP를 구성하는 5가지 오브젝트 타입의 역할을 구분할 수 있다.
- DDOP 전송 과정을 시퀀스 다이어그램으로 그릴 수 있다.
- 3구획 살포기의 DDOP를 직접 설계하고 오브젝트 표를 작성할 수 있다.
:::

## 1. DDOP란

<strong>DDOP(Device Description Object Pool)</strong>는 작업기가 자기 자신의 구조와 능력을 TC에게 알려주는 데이터 집합이다.

> DDOP는 "작업기의 자기소개서"이다.

TC-Server는 버스에 연결된 작업기에 대해 아무런 사전 정보가 없다. 작업기가 어떤 구획(Section)을 가졌는지, 어떤 DDI를 지원하는지, 작업폭이 얼마인지를 TC는 알 수 없다. DDOP는 이 정보를 구조화된 형식으로 TC에 전달하여, TC가 작업기를 이해하고 제어할 수 있게 한다.

**DDOP가 없다면:**
- TC는 작업기에 어떤 명령을 보낼 수 있는지 모른다.
- 처방 맵의 살포량을 어느 DDI로 전달해야 하는지 알 수 없다.
- Section Control을 위해 몇 개의 구획이 있는지 파악하지 못한다.

**DDOP가 있다면:**
- TC는 작업기의 구조를 파악하고 적절한 명령을 선택한다.
- 지원되지 않는 DDI로의 명령 시도를 사전에 방지한다.

## 2. DDOP 오브젝트 구조

DDOP는 5가지 타입의 오브젝트로 구성된다.

| 오브젝트 타입 | 역할 | 주요 속성 |
|--------------|------|-----------|
| **Device** | 장치 전체 정보 (최상위) | 제조사, 제품명, 시리얼번호, Structure Label |
| **DeviceElement** | 장치의 논리적 구성 요소 | Element Type, Element Number, 부모 Element |
| **DeviceProcessData** | 지원하는 프로세스 데이터 항목 | DDI, Property Flag (default/settable/control source), Trigger Methods |
| **DeviceProperty** | 고정 속성값 | DDI, 값 (작업폭, 구획 폭 등) |
| **DeviceValuePresentation** | 데이터 표현 방식 | 오프셋, 스케일, 소수 자릿수, 단위 기호 |

```mermaid
graph TD
    DVC["Device<br>살포기 전체<br>제조사/모델/S/N"]

    DE_ROOT["DeviceElement<br>Type=Device<br>(전체 기능 루트)"]
    DE_SEC1["DeviceElement<br>Type=Section<br>Section 1 (3m)"]
    DE_SEC2["DeviceElement<br>Type=Section<br>Section 2 (3m)"]
    DE_SEC3["DeviceElement<br>Type=Section<br>Section 3 (3m)"]

    DPD_SP["DeviceProcessData<br>DDI=1<br>Setpoint Volume/Area"]
    DPD_MS["DeviceProcessData<br>DDI=2<br>Actual Volume/Area"]

    DPROP["DeviceProperty<br>DDI=작업폭<br>Value=9m"]

    DVP["DeviceValuePresentation<br>Unit=L/ha<br>Scale=0.01"]

    DVC --> DE_ROOT
    DE_ROOT --> DE_SEC1
    DE_ROOT --> DE_SEC2
    DE_ROOT --> DE_SEC3
    DE_SEC1 --> DPD_SP
    DE_SEC1 --> DPD_MS
    DE_ROOT --> DPROP
    DPD_SP --> DVP
    DPD_MS --> DVP
```

### 오브젝트 타입 상세

**Device**
- DDOP 전체의 루트 오브젝트이다.
- `Structure Label`: DDOP 버전을 나타내는 식별자이다. TC는 이 라벨을 보고 DDOP를 새로 받을지 캐시된 것을 쓸지 결정한다.
- `Localization Label`: 언어·단위 설정

**DeviceElement**
- 작업기의 논리적 부품이다. Element Type(1바이트 코드)으로 역할을 정의한다.
- `1 Device`: 장치 전체를 대표하는 Element (DDOP당 1개)
- `2 Function`: 살포 펌프, 파종 유닛 등 기능 단위
- `3 Bin`: 씨앗·비료 저장 용기
- `4 Section`: 독립 제어 가능한 구획
- `5 Unit`: Section 하위의 가장 세분화된 단위 (노즐, 파종 로우 유닛 등)
- `6 Connector`: 히치 연결점
- `7 Navigation Reference`: GPS 안테나 등 내비게이션 기준 위치
- Element Number는 12비트(0~4095)이며, Parent Object ID로 상위 Element(또는 Device)를 참조해 계층을 구성한다.

**DeviceProcessData**
- DeviceElement에 연결되며, 해당 Element에서 지원하는 DDI 항목을 정의한다.
- `Property Flag`(3비트): bit1 = 기본값(default) 세트 멤버 여부, bit2 = settable(TC가 값을 설정 가능 — Setpoint류), bit3 = control source(다른 CF의 setpoint 값을 결정하는 소스로 동작). bit2·bit3은 동시에 설정될 수 없다.
- `Trigger Methods`(5비트): time interval(시간 간격), distance interval(거리 간격), threshold limits(임계값), on change(변화량), total(누적값)

**DeviceProperty**
- 변하지 않는 고정 속성이다. 작업폭, 구획 폭 등이 여기에 해당한다.
- DeviceProcessData와 달리 TC가 값을 변경하지 않는다.

**DeviceValuePresentation**
- 숫자값을 사람이 읽기 쉬운 형식으로 변환하는 규칙이다.
- 공식: `표시값 = (원시값 + Offset) × Scale`
- 예: 원시값 20000, Offset=0, Scale=0.01 → 표시값 200.00 L/ha
- `Number of decimals`(0~7) 속성으로 표시 소수 자릿수도 함께 정의한다.

## 3. DDOP 전송 과정

DDOP 관련 메시지는 모두 <strong>TC-Client가 TC/DL에게 보내는 요청</strong>과 그에 대한 TC의 응답으로 구성된다 — TC가 먼저 DDOP를 요구하는 것이 아니라, 클라이언트가 자신의 device descriptor를 TC에 질의·전송·활성화하는 흐름이다.

```mermaid
sequenceDiagram
    participant CLIENT as TC-Client<br>(작업기 ECU)
    participant TC as TC-Server

    Note over CLIENT,TC: 네트워크 연결 및 주소 클레임 완료

    CLIENT ->> TC: Working Set Master 메시지<br>(PGN 65037, 버스 참여 알림)

    CLIENT ->> TC: Request Structure Label<br>(보유 중인 DDOP 버전 라벨 질의)

    TC -->> CLIENT: Structure Label 응답<br>(일치하면 "SPRAY-V2.1-20240101", 없으면 FF로 채움)

    alt TC에 DDOP가 없거나 버전이 다름
        CLIENT ->> TC: Request Object-pool Transfer<br>(전송할 데이터 크기 통보)
        TC -->> CLIENT: Request Object-pool Transfer Response<br>(메모리 확인 결과)
        CLIENT ->> TC: Object-pool Transfer<br>(DDOP 데이터, TP/ETP로 멀티패킷 전송)
        TC -->> CLIENT: Object-pool Transfer Response<br>(성공/실패)
    else TC에 DDOP가 이미 있음
        Note over TC: 기존 DDOP 사용
    end

    CLIENT ->> TC: Object-pool Activate<br>(DDOP 활성화 요청)
    TC -->> CLIENT: Object-pool Activate Response<br>(활성화 완료)

    Note over TC,CLIENT: Task 수행 준비 완료
```

### 전송 프로토콜

DDOP 데이터는 일반적으로 수백 바이트~수 킬로바이트에 달하므로, 단일 CAN 프레임으로 전송할 수 없다. ISO 11783의 <strong>TP(Transport Protocol, TP.CM 60416/TP.DT 60160)</strong> 또는 <strong>ETP(Extended Transport Protocol, ETP.CM 51200/ETP.DT 50944)</strong>를 사용하여 멀티패킷으로 분할 전송한다. 1,785바이트를 넘는 DDOP는 ETP를 써야 한다.

## 4. DDOP 설계 예제

### 대상: 3구획 붐 스프레이어

- 총 작업폭: 9m (3구획 × 3m)
- 지원 기능: Section Control(구획별 ON/OFF), Rate Control(살포량 가변)
- 지원 DDI: DDI 1(Setpoint Volume/Area), DDI 2(Actual Volume/Area), DDI 289(Setpoint Work State — 구획 ON/OFF 명령)

### DDOP 계층 구조

```mermaid
graph TD
    DVC["Device<br>오브젝트 ID: 1<br>3구획 붐 스프레이어"]

    DE0["DeviceElement<br>ID: 2, Type: Device<br>Element Number: 0<br>전체 기능 루트"]

    DE1["DeviceElement<br>ID: 3, Type: Section<br>Element Number: 1<br>Section 1 (좌, 3m)"]

    DE2["DeviceElement<br>ID: 4, Type: Section<br>Element Number: 2<br>Section 2 (중, 3m)"]

    DE3["DeviceElement<br>ID: 5, Type: Section<br>Element Number: 3<br>Section 3 (우, 3m)"]

    PROP["DeviceProperty<br>ID: 6<br>작업폭 = 9m"]

    DPD_SP1["DeviceProcessData<br>ID: 7<br>DDI=1 Setpoint<br>(Section 1)"]
    DPD_MS1["DeviceProcessData<br>ID: 8<br>DDI=2 Measurement<br>(Section 1)"]
    DPD_SC1["DeviceProcessData<br>ID: 9<br>DDI=289 SectionCtrl<br>(Section 1)"]

    DPD_SP2["DeviceProcessData<br>ID: 10<br>DDI=1 Setpoint<br>(Section 2)"]
    DPD_MS2["DeviceProcessData<br>ID: 11<br>DDI=2 Measurement<br>(Section 2)"]
    DPD_SC2["DeviceProcessData<br>ID: 12<br>DDI=289 SectionCtrl<br>(Section 2)"]

    DPD_SP3["DeviceProcessData<br>ID: 13<br>DDI=1 Setpoint<br>(Section 3)"]
    DPD_MS3["DeviceProcessData<br>ID: 14<br>DDI=2 Measurement<br>(Section 3)"]
    DPD_SC3["DeviceProcessData<br>ID: 15<br>DDI=289 SectionCtrl<br>(Section 3)"]

    DVP["DeviceValuePresentation<br>ID: 16<br>Unit=L/ha, Scale=0.01"]

    DVC --> DE0
    DE0 --> DE1
    DE0 --> DE2
    DE0 --> DE3
    DE0 --> PROP

    DE1 --> DPD_SP1
    DE1 --> DPD_MS1
    DE1 --> DPD_SC1

    DE2 --> DPD_SP2
    DE2 --> DPD_MS2
    DE2 --> DPD_SC2

    DE3 --> DPD_SP3
    DE3 --> DPD_MS3
    DE3 --> DPD_SC3

    DPD_SP1 --> DVP
    DPD_MS1 --> DVP
    DPD_SP2 --> DVP
    DPD_MS2 --> DVP
    DPD_SP3 --> DVP
    DPD_MS3 --> DVP
```

### DDOP 오브젝트 정의 표

| 오브젝트 ID | 타입 | 주요 속성 | 값 |
|------------|------|----------|-----|
| 1 | Device | 제품명 | BoomSprayer-3S |
|   |        | 제조사 | ExampleCo |
|   |        | Structure Label | SPRY3-V1.0 |
| 2 | DeviceElement | Type | Device |
|   |               | Element Number | 0 |
|   |               | 부모 | Device(1) |
| 3 | DeviceElement | Type | Section |
|   |               | Element Number | 1 |
|   |               | 부모 | DE(2) |
| 4 | DeviceElement | Type | Section |
|   |               | Element Number | 2 |
|   |               | 부모 | DE(2) |
| 5 | DeviceElement | Type | Section |
|   |               | Element Number | 3 |
|   |               | 부모 | DE(2) |
| 6 | DeviceProperty | DDI | 작업폭 DDI |
|   |               | Value | 9000 (단위: mm) |
|   |               | 연결 Element | DE(2) |
| 7 | DeviceProcessData | DDI | 1 (Setpoint Vol/Area) |
|   |                   | Property Flag | Setpoint 지원 |
|   |                   | 연결 Element | DE(3) — Section 1 |
| 8 | DeviceProcessData | DDI | 2 (Actual Vol/Area) |
|   |                   | Property Flag | Measurement 지원 |
|   |                   | Trigger | 변화량(10 L/ha 이상 변화 시) |
|   |                   | 연결 Element | DE(3) — Section 1 |
| 9 | DeviceProcessData | DDI | 289 (Setpoint Work State) |
|   |                   | Property Flag | Setpoint 지원 |
|   |                   | 연결 Element | DE(3) — Section 1 |
| 10–12 | DeviceProcessData | (Section 2 동일 구조) | DE(4) 연결 |
| 13–15 | DeviceProcessData | (Section 3 동일 구조) | DE(5) 연결 |
| 16 | DeviceValuePresentation | Offset | 0 |
|    |                         | Scale | 0.01 |
|    |                         | Unit Symbol | L/ha |

이 DDOP를 수신한 TC-Server는 다음을 파악한다.

- 이 작업기는 3개의 Section을 가진 살포기이다.
- 각 Section에 DDI 1(Setpoint), DDI 2(Measurement), DDI 289(Setpoint Work State)를 지원한다.
- 전체 작업폭은 9m이다.
- 값의 단위는 L/ha이며 스케일 인자는 0.01이다.

> **핵심 정리**
> - DDOP(Device Description Object Pool)는 작업기가 TC에게 자신의 구조와 능력을 알리는 데이터로, "작업기의 자기소개서"이다.
> - DDOP는 Device, DeviceElement, DeviceProcessData, DeviceProperty, DeviceValuePresentation 5가지 오브젝트로 구성된다.
> - TC-Client는 연결 시 자신의 Structure Label을 TC에 질의하고, TC가 모르는 버전이면 스스로 DDOP 전체를 멀티패킷으로 전송한다.
> - TC는 DDOP를 파싱하여 지원 DDI, Section 구성, 작업폭 등을 파악한 뒤 Task를 활성화한다.
> - 3구획 살포기 DDOP에는 Section별로 DDI 1(Setpoint), DDI 2(Measurement), DDI 289(Setpoint Work State) 항목이 정의된다.

## 5. DDOP를 바이트로 보기

§2와 §4에서 다룬 DDOP 오브젝트들은 결국 TP/ETP로 전송되는 바이트열이다. 어디까지 바이트 단위로 확인 가능한지, 그리고 그 바이트가 §4의 3구획 스프레이어 예제에서 무엇을 나타내는지 살펴본다.

### 오브젝트 공통 구조

모든 DDOP 오브젝트는 <strong>Object ID</strong>(DDOP 전체에서 유일, 참조 없음은 NULL Object ID `0xFFFF`)와 오브젝트 타입(Device·DeviceElement·DeviceProcessData·DeviceProperty·DeviceValuePresentation 다섯 종류 중 하나) 뒤에 타입별 속성이 이어지는 구조다.

:::info 확인 범위
이 절에서 다루는 것은 <strong>타입별로 어떤 필드가 몇 바이트인지</strong>까지다. Object ID와 오브젝트 타입 식별자가 바이트열의 정확히 몇 번째 바이트에 어떤 순서로 놓이는지 — 오브젝트 타입을 텍스트로 싣는지 숫자 코드로 싣는지를 포함해서 — 는 이번에 확인한 정리 자료(`appendix-iso-part10.md`)에 명시돼 있지 않다. 그래서 전체 오브젝트를 바이트 오프셋까지 조립하는 대신, 각 오브젝트가 담아야 하는 필드와 그 폭까지만 다룬다.
:::

### DeviceElement — 계층을 만드는 필드

| 필드 | 폭 | §4 Object 3(DE, Section 1)의 값 |
|---|---|---|
| DeviceElementType | 1바이트 | 4(Section) |
| DeviceElementNumber | 2바이트 (0~4095) | 1 |
| Parent Object ID | Object ID와 같은 폭(2바이트) | 2 (DE(2), 전체 기능 루트) |

DeviceElementNumber가 4095까지인 것은 우연이 아니다. Process Data 메시지의 Element Number 필드도 12비트(0~4095)이므로, DDOP에서 선언한 Element Number를 그대로 [Process Data 메시지의 Element Number 자리](/study/isobus/19-tc-process-data)에 실어 보낼 수 있다.

### DeviceProcessData — DDI·property·trigger를 담는 필드

| 필드 | 폭 | 내용 |
|---|---|---|
| Process data DDI | 2바이트 | ISO 11783-11 정의 DDI |
| Process data properties | 1바이트(비트셋) | bit1=default set 멤버, bit2=settable, bit3=control source(bit2·3 동시 설정 불가) |
| Process data available trigger methods | 1바이트(비트셋) | bit1=time interval, bit2=distance interval, bit3=threshold limits, bit4=on change, bit5=total |
| Device value presentation object ID | 2바이트 | 없으면 NULL(`0xFFFF`) |

§4의 Object 7(Section 1의 DDI 1, Setpoint)과 Object 8(Section 1의 DDI 2, Measurement — 변화량 10 L/ha 이상 트리거)을 이 필드에 채우면 다음과 같다.

| Object | DDI | Properties 비트 | Properties 바이트 | Trigger 비트 | Trigger 바이트 |
|---|---|---|---|---|---|
| 7 (Setpoint) | 1 | bit2(settable)=1, 나머지 0 | `0x02` | §4 표에 트리거 명시 없음 | 확인 불가 |
| 8 (Measurement) | 2 | 전부 0(설정 불가) | `0x00` | bit4(on change)=1, 나머지 0 | `0x08` |

<strong>Object 7의 Properties 바이트가 `0x02`로 bit2(settable)를 세운 것</strong>이 [TC 프로세스 데이터 챕터의 "전체 흐름"](/study/isobus/19-tc-process-data)에서 말한 "DDOP에 없는 DDI는 쓸 수 없다"의 실체다. TC가 `[DDI=1, Element=3, Value=200]`처럼 Value Command를 내려도, 대상 Element에 연결된 DeviceProcessData의 Properties 바이트에 bit2가 서 있지 않으면 작업기는 이를 받아들일 근거가 없어 PDACK 오류 코드(bit5, "process data가 settable 아님")로 거부한다. Object 8은 반대로 bit2가 0이므로 TC가 setpoint로 내릴 수 없고, 오직 작업기가 측정값을 올리는 용도로만 쓰인다.

### DDOP 전송도 같은 PGN, 같은 바이트 배치를 쓴다

앞 챕터에서 다룬 Process Data 메시지(PGN 51968/`0xCB00`, Command 4비트 + Element/DDI/Value)는 살포량 같은 "값"을 나를 때의 구조다. DDOP 자체를 실어 나르는 메시지는 같은 PGN 위에서 <strong>Command 1(Device descriptor)</strong>의 서브커맨드로 오간다. Byte 1의 자리 배치는 형식적으로 같다 — 하위 4비트가 Command(`0001`), 상위 4비트는 이번엔 Element Number가 아니라 서브커맨드를 나타낸다.

| 서브커맨드(Byte 1 bit 8~5) | 메시지 | Byte 1 |
|---|---|---|
| `0000` | Request Structure Label | `0x01` |
| `0110` | Object-pool Transfer(DDOP 본문 전송) | `0x61` |
| `1000` | Object-pool Activate/Deactivate | `0x81` |

`0x61`(Object-pool Transfer)로 시작한 메시지의 뒤(Byte 2~n)에 위에서 채운 DVC·DET·DPD·DPT·DVP 오브젝트 레코드들이 이어져 TP(1,785바이트 이하) 또는 ETP(초과 시)로 분할 전송된다. 즉 DDOP 전송과 Process Data 값 전달은 같은 PGN·같은 Command 니블 구조를 공유하되, Command 값(1 vs 2~A)에 따라 그 뒤에 오는 바이트열의 의미가 완전히 달라진다.

:::details 파이썬으로 검산해 보기
```python
def properties_byte(default=False, settable=False, control_source=False):
    return (int(default) << 0) | (int(settable) << 1) | (int(control_source) << 2)


def trigger_byte(time_interval=False, distance_interval=False,
                  threshold=False, on_change=False, total=False):
    return (
        (int(time_interval) << 0)
        | (int(distance_interval) << 1)
        | (int(threshold) << 2)
        | (int(on_change) << 3)
        | (int(total) << 4)
    )


def device_descriptor_byte1(subcommand):
    command = 1  # Device descriptor
    return (subcommand << 4) | command


# Object 7 — DDI 1 Setpoint: settable만 세운다
print(hex(properties_byte(settable=True)))          # 0x2

# Object 8 — DDI 2 Measurement: settable 없음, on change 트리거
print(hex(properties_byte()))                       # 0x0
print(hex(trigger_byte(on_change=True)))            # 0x8

# Device descriptor 서브커맨드별 Byte 1
print(hex(device_descriptor_byte1(0b0000)))         # 0x1  Request Structure Label
print(hex(device_descriptor_byte1(0b0110)))         # 0x61 Object-pool Transfer
print(hex(device_descriptor_byte1(0b1000)))         # 0x81 Object-pool Activate/Deactivate
```
:::

## 6. 실물 예시: 7섹션 붐 살포기

§4의 3구획 예시는 살포량·구획 ON/OFF만 다루는 최소 구성이었다. 실제 붐 스프레이어는 총계 보고(TC-BAS)·구획 제어(TC-SC)·기하 정보까지 함께 갖춘다. 이 절은 12m 붐에 1,714mm 폭 섹션 7개를 단 살포기의 DDOP를, `appendix-iso-part10.md`의 Annex A·F와 `appendix-ddi.md`에서 확인한 값만으로 설계한다.

### DDOP 계층 구조

Device 아래 루트 Device Element(Element 0) 하나를 두고, 그 형제로 커넥터(트랙터 히치 연결점, type 6)·빈(약액 탱크, type 3)·붐(Function, type 2)을 배치한 뒤 붐 아래에 섹션(type 4) 7개를 매단다. Section의 Element Number는 <strong>기계 좌→우 순으로 증가</strong>시키는 것이 권장 규칙이므로(Annex F.3.5), 11~17을 좌에서 우로 배정한다.

```
DVC Device                                        Object ID 1
└─ DET type=1 device            Element 0         Object ID 2
   ├─ DET type=6 connector      Element 1         Object ID 3
   ├─ DET type=3 bin            Element 2         Object ID 4
   └─ DET type=2 function(붐)   Element 3         Object ID 5
      ├─ DET type=4 section 1   Element 11        Object ID 6
      ├─ DET type=4 section 2   Element 12        Object ID 7
      ├─ DET type=4 section 3   Element 13        Object ID 8
      ├─ DET type=4 section 4   Element 14        Object ID 9
      ├─ DET type=4 section 5   Element 15        Object ID 10
      ├─ DET type=4 section 6   Element 16        Object ID 11
      └─ DET type=4 section 7   Element 17        Object ID 12
```

이 배치는 "Function이 붐인 경우 actual/setpoint 값·X·Y offset·maximum working width는 모두 그 Function 안에 두고, 루트는 actual work state 속성 외의 actual/setpoint 값을 가지면 안 된다"(Annex F.3.4)는 규칙을 따른다 — 그래서 살포량·구획 상태 관련 DPD는 전부 붐(Element 3) 아래에 몰려 있고 루트(Element 0)에는 총계만 남는다.

### 레벨별 DPD·DPT

<strong>Device 레벨(Element 0)</strong> — 총계만 붙는다. TC-BAS는 "TC 클라이언트는 총계의 부분집합만 제공해도 되지만 최소한 DDI 119(total time)는 제공해야 한다"고 요구하므로 DDI 119는 필수다.

| Object ID | DDI | 이름 | 타입 | Properties | Trigger |
|---|---|---|---|---|---|
| 13 | 119 | Effective Total Time | DPD | settable | total, time interval |
| 14 | 116 | Total Area | DPD | settable | total |
| 15 | 117 | Total Distance | DPD | settable | total |

task total DDI는 "trigger method total + property settable"을 함께 세우는 것이 일반 규칙이다 — TC가 태스크 시작 시 이어서 셀 시작값을 지정할 수 있어야 하기 때문이다. DDI 119만 Annex F.3.3에 따라 time interval 트리거가 추가로 요구된다.

<strong>붐(Function) 레벨(Element 3)</strong>

| Object ID | DDI | 이름 | 타입 | Properties | Trigger | 비고 |
|---|---|---|---|---|---|---|
| 16 | 1 | Setpoint Volume Per Area | DPD | settable | - | TC→작업기, 살포량 목표 |
| 17 | 2 | Actual Volume Per Area | DPD | (읽기 전용) | on change | 작업기→TC, 실제 살포량 |
| 18 | 141 | Actual Work State | DPD | (읽기 전용) | on change, time interval | 붐의 마스터 작업 스위치 |
| 19 | 161 | Actual Condensed Work State | DPD | (읽기 전용) | on change, time interval | 7섹션 실제 ON/OFF 비트 |
| 20 | 290 | Setpoint Condensed Work State | DPD | settable | on change | 7섹션 목표 ON/OFF 비트, TC→작업기 |
| 21 | 160 | Section Control State | DPD | settable | on change | TC-SC 활성/비활성 스위치 |
| 22 | 70 | Maximum Working Width | DPT | - | - | 11,998mm |

141·161의 on change·time interval은 Annex F.3.5가 "Actual Work State(들)와 Actual Condensed Work State(들)에는 On Change·Time Interval 지원이 필수"라고 못 박은 항목이다. 160(Section Control State)은 같은 절에서 "settable + on-change 트리거 필수"로 명시된다.

<strong>섹션 레벨(대표: Section 1, Element 11)</strong> — DPD 없이 DPT만 붙는다.

| Object ID | DDI | 이름 | 타입 | 값 |
|---|---|---|---|---|
| 23 | 70 | Maximum Working Width | DPT | 1,714mm |
| 24 | 134 | Offset X | DPT | 0mm |
| 25 | 135 | Offset Y | DPT | −5,142mm |
| 26 | 136 | Offset Z | DPT | 0mm |

Section 2~7도 같은 4개 DPT 패턴이 반복된다(Object ID 27~50). DDI 70(1,714mm)·134·136(0mm)은 7개 섹션이 전부 동일하고, DDI 135(Offset Y)만 섹션마다 다르다 — 다음 절에서 계산한다. Offset X·Z를 0mm로 둔 것은 이 예시에서 모든 섹션이 붐과 같은 전후·높이 위치에 일렬로 달려 있다고 가정했기 때문이다(실측값이 아니라 이 예시의 설계 가정).

표시용 DeviceValuePresentation은 §4와 같은 패턴으로 2개면 충분하다 — Object ID 51(Offset 0, Scale 0.01, L/ha)을 DDI 1·2가 참조하고, Object ID 52(Offset 0, Scale 1, mm)를 DDI 70·134·135·136이 참조한다. 여기까지 합치면 DVC 1개, DET 11개, DPD 9개(장치 3 + 붐 6), DPT 29개(붐 1 + 섹션 7×4), DVP 2개로 총 52개 오브젝트다.

### Y 오프셋 계산

DRP(Device Reference Point) 기준 오른손 좌표계에서 y축은 <strong>주행 방향 기준 우측이 양수</strong>다(Annex A.1). 섹션이 홀수 개(7개)이므로 가운데 4번 섹션이 y=0에 오고, 나머지 6개가 좌우로 대칭 배치된다.

| 섹션 | Element | Object ID(DDI 135) | Y 오프셋 |
|---|---|---|---|
| 1 | 11 | 25 | −5,142mm |
| 2 | 12 | 29 | −3,428mm |
| 3 | 13 | 33 | −1,714mm |
| 4 | 14 | 37 | 0mm |
| 5 | 15 | 41 | 1,714mm |
| 6 | 16 | 45 | 3,428mm |
| 7 | 17 | 49 | 5,142mm |

붐 전체 폭은 7 × 1,714mm = 11,998mm — 정확히 12m는 아니고 2mm 모자란다. DDI 70(Maximum Working Width)에는 이 11,998mm를 붐(Function) 레벨 값으로 넣는다.

:::details 파이썬으로 검산해 보기
```python
n = 7
width = 1714  # mm, 섹션 1개 폭

offsets = {i: (i - 4) * width for i in range(1, n + 1)}
for i, y in offsets.items():
    print(f"section {i} (element {10+i}): Y = {y:+d} mm")

# 홀수 섹션 → 가운데(4번)가 0, 나머지는 좌우 대칭
assert offsets[4] == 0
assert offsets[1] == -offsets[7]
assert offsets[2] == -offsets[6]
assert offsets[3] == -offsets[5]

print("total width =", n * width, "mm")
```
```
section 1 (element 11): Y = -5142 mm
section 2 (element 12): Y = -3428 mm
section 3 (element 13): Y = -1714 mm
section 4 (element 14): Y = +0 mm
section 5 (element 15): Y = +1714 mm
section 6 (element 16): Y = +3428 mm
section 7 (element 17): Y = +5142 mm
total width = 11998 mm
```
:::

### 설계 판단 세 가지

**섹션 폭은 DPT, 살포량은 DPD인 이유.** 섹션 폭(1,714mm)은 물리적으로 고정된 값이라 DeviceProperty(DPT)로 담는다 — TC가 바꿀 수도, 바뀔 수도 없는 상수다. 반대로 살포량은 처방 맵·운전자 입력에 따라 태스크 중 계속 바뀌므로 DeviceProcessData(DPD)로 담아야 한다. 이 구분을 반대로 하면 안 되는 이유가 DDI 67(Actual Working Width)에서 드러난다 — 붐(Function) 레벨의 DDI 67은 "On 상태인 하위 섹션 폭의 합"으로 정의된다. 섹션 하나가 꺼지면 이 값 자체가 줄어든다는 뜻이라, 섹션의 물리적 폭을 이 값 하나로만 표현했다면 "섹션이 꺼져서 폭이 줄어든 것"과 "섹션 자체 폭이 바뀐 것"을 구분할 수 없다. 그래서 이 설계는 <strong>섹션 개별 폭(고정, DPT 70)</strong>과 <strong>붐 레벨 Actual Working Width(가변, on 섹션의 합)</strong>를 별도 DDI로 분리해 둔다 — 이번 DDOP에는 DDI 67 자체를 넣지 않았지만, 넣었다면 반드시 붐 레벨의 process data(DPD)여야지 섹션의 property가 되면 안 된다는 뜻이다.

**섹션별 개별 setpoint 대신 Condensed를 쓰는 이유.** ISO 11783-10 Annex F.3.5는 "DDOP에서 섹션 작업 상태의 보고·제어에 허용되는 것은 Actual/Setpoint Condensed Work State뿐이다 — Section 요소 안에 개별 Actual Work State(141)나 개별 Setpoint Work State(289)를 두면 안 된다"고 명시한다. 즉 섹션 7개마다 DDI 289를 하나씩 붙이는 구성은 최적화 이전에 <strong>표준 위반</strong>이다. 설령 허용됐더라도 대역폭이 문제다 — [연결당·variable당 상한은 초당 10개](/study/isobus/19-tc-process-data)인데, 이 상한을 넘겨도 되는 예외는 <strong>Condensed Work State류 DDI</strong>에만 적용된다. 헤드랜드 진입처럼 여러 섹션을 한꺼번에 전환해야 하는 순간에도, DDI 290 하나로 7섹션 상태를 동시에 담으면 이 burst 예외를 그대로 쓸 수 있다.

**settable 비트는 DDI 1과 290에만 세운다.** DDI 2(Actual Volume Per Area)·141(Actual Work State)·161(Actual Condensed Work State)은 작업기가 실측·실제 상태를 보고하는 값이다. 이 DPD들의 Properties 바이트에 settable(bit2)을 세우면 TC가 "실측값"이라는 이름의 필드에 값을 명령할 수 있게 되는데, §5에서 다룬 Object 8(DDI 2)의 규칙과 같은 원리로 잘못이다 — 읽기 전용이어야 할 DDI를 설정용으로 여는 것이 흔한 설계 실수다. 이 DDOP에서 settable은 DDI 1(살포량 목표)·290(구획 목표 상태)·160(Section Control State, TC-SC 활성화 스위치)·그리고 앞서 device 레벨에 둔 총계 3종(119·116·117 — 총계는 태스크 시작 시 TC가 이어서 셀 시작값을 지정할 수 있어야 하므로 성격이 다른 settable이다)에만 세운다.

### 이 DDOP로 만들 수 있는 메시지

이 DDOP는 붐(Element 3)에만 DDI 1을 정의하고 섹션(Element 11~17)에는 DDI 1을 두지 않는다 — 즉 "섹션 1의 살포량만 따로 정한다"는 명령 자체가 이 설계에서 성립하지 않는다. `[DDI=1, Element=11]`로 명령을 보내면 작업기는 그 Element에 연결된 DeviceProcessData가 없으므로 PDACK(command D)로 거부한다. 붐 전체 살포량을 바꾸는 유일한 방법은 붐(Element 3)에 명령하는 것이다.

바이트 배치는 [CH19 §6](/study/isobus/19-tc-process-data)의 Command 4비트(Byte 1 하위)+Element Number 12비트(Byte 1 상위 4비트+Byte 2)를 그대로 따른다.

**메시지 1 — 붐 전체 살포량 220 L/ha 설정 (Element 3, DDI 1, Command 3)**

| Byte | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| 값 | `0x33` | `0x00` | `0x01` | `0x00` | `0xC0` | `0x91` | `0x21` | `0x00` |

220 L/ha → 22,000 mm³/m² → raw = 22,000 ÷ 0.01 = 2,200,000(`0x2191C0`), LSB부터 `C0 91 21 00`.

**메시지 2 — 붐의 7섹션 ON/OFF 일괄 명령 (Element 3, DDI 290, Command 3)**

가장자리 두 섹션(1·7)은 끄고 가운데 다섯 섹션(2~6)은 켜는 상황을 예로 든다. DDI 290은 [섹션당 2비트(00=Off, 01=On)로 최대 16섹션까지 한 32비트 값에 담는다](/study/isobus/19-tc-process-data). 섹션 1이 LSB 쪽 2비트를 차지한다고 두면(이 대응 순서 자체는 이번 확인 자료에 명시돼 있지 않아 이 예시의 가정이다), 정의되지 않은 8~16번은 141(Actual Work State)에서 확인된 2비트 코드표(00=Off, 01=On, 10=오류, 11=미설치) 중 "미설치(11)"를 빌려 채운다 — 290 자체의 코드값이 이번 확인 자료에 별도로 명시돼 있지는 않다.

| Byte | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| 값 | `0x33` | `0x00` | `0x22` | `0x01` | `0x54` | `0xC5` | `0xFF` | `0xFF` |

:::details 파이썬으로 검산해 보기
```python
def build_frame(command, element, ddi, value):
    byte1 = ((element & 0xF) << 4) | (command & 0xF)
    byte2 = (element >> 4) & 0xFF
    ddi_bytes = ddi.to_bytes(2, "little")
    value_bytes = value.to_bytes(4, "little", signed=True)
    return bytes([byte1, byte2]) + ddi_bytes + value_bytes


# 메시지 1: 붐(Element 3)에 DDI 1, 220 L/ha
raw = int(220 * 100 / 0.01)
frame1 = build_frame(command=3, element=3, ddi=1, value=raw)
print(frame1.hex(' ').upper())   # 33 00 01 00 C0 91 21 00

# 메시지 2: 붐(Element 3)에 DDI 290, 섹션 1·7 Off / 2~6 On / 8~16 미설치
states = {1: 0, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 0}
value = 0
for i in range(1, 17):
    bits = states.get(i, 0b11)   # 정의 안 된 섹션(8~16)은 미설치
    value |= bits << (2 * (i - 1))
value_signed = value - 2**32 if value >= 2**31 else value

frame2 = build_frame(command=3, element=3, ddi=290, value=value_signed)
print(frame2.hex(' ').upper())   # 33 00 22 01 54 C5 FF FF
```
:::

두 메시지 모두 Byte 1이 `0x33`인 것은 우연이다 — Command(3, Value command)와 Element Number(3, 붐)가 두 메시지에서 같은 값이라 니블이 똑같이 채워졌을 뿐이다. Byte 3~4(DDI)와 Byte 5~8(Value)이 완전히 다른 두 명령을 구분한다.

## 다음 챕터

- 다음 : [ISOBUS 기타 기능](/study/isobus/21-isobus-misc)
