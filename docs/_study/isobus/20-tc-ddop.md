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

## 다음 챕터

- 다음 : [ISOBUS 기타 기능](/study/isobus/21-isobus-misc)
