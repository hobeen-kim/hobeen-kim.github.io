---
title: "ISOBUS (ISO 11783) 개요"
description: "농업 기계 전용 통신 표준인 ISOBUS(ISO 11783)의 탄생 배경, 파트 구성, J1939과의 관계, 생태계를 이해한다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, J1939, AEF, CAN]
prev: /study/isobus/11-j1939-transport
next: /study/isobus/13-isobus-architecture
---

# ISOBUS (ISO 11783) 개요

::: info 학습 목표
- ISOBUS가 무엇이고 왜 농업 기계에 필요한지 설명할 수 있다.
- ISO 11783의 파트 구성을 알고 각 파트의 역할을 구분할 수 있다.
- J1939과 ISOBUS의 계층적 관계를 도식화할 수 있다.
- AEF와 적합성 인증의 의미를 이해한다.
:::

---

## 1. ISOBUS란

<strong>ISOBUS</strong>는 농업·임업 기계를 위한 직렬 통신 표준이다. 공식 명칭은 다음과 같다.

> **ISO 11783 — Tractors and machinery for agriculture and forestry — Serial control and communications data network**

쉽게 말하면, 트랙터와 작업기(Implement) 사이에서 데이터를 주고받기 위한 규칙 모음이다. 속도, 엔진 RPM, GPS 위치, 작업기 상태 같은 정보를 표준화된 방식으로 교환한다.

핵심 목표는 <strong>상호운용성(Interoperability)</strong>이다. 어떤 제조사의 트랙터와 어떤 제조사의 작업기를 조합해도 동일한 방식으로 통신할 수 있어야 한다.

---

## 2. 왜 ISOBUS가 필요한가

### 과거의 문제

ISOBUS 이전에는 제조사마다 독자적인 통신 프로토콜을 사용했다. 트랙터 A의 커넥터와 작업기 B의 커넥터가 물리적으로 맞더라도, 프로토콜이 달라서 데이터를 교환할 수 없었다.

```mermaid
graph TD
    subgraph 과거_독자_프로토콜
        TA[트랙터 A\nProto-A] -- 연결 불가 --> IB[작업기 B\nProto-B]
        TB[트랙터 B\nProto-B] -- 연결 가능 --> IB
        TB -- 연결 불가 --> IA[작업기 A\nProto-A]
        TA -- 연결 가능 --> IA
    end
```

결과적으로 농민은 같은 제조사의 트랙터와 작업기만 조합할 수 있었고, 장비 구매 선택지가 크게 제한되었다.

### ISOBUS 도입 후

ISOBUS는 통신 규격을 표준화하여 제조사 간 장벽을 없앴다.

```mermaid
graph TD
    subgraph ISOBUS_표준화_이후
        T1[트랙터 A\nISOBUS] -- 연결 가능 --> I1[작업기 B\nISOBUS]
        T1 -- 연결 가능 --> I2[작업기 C\nISOBUS]
        T2[트랙터 B\nISOBUS] -- 연결 가능 --> I1
        T2 -- 연결 가능 --> I2
    end
```

트랙터와 작업기가 모두 ISOBUS 인증을 받았다면, 제조사에 관계없이 조합이 가능하다. 농민은 최적의 장비를 자유롭게 선택할 수 있다.

### "프로토콜 준수"란 구체적으로 무엇인가

"ISOBUS를 준수한다"는 것은 ISO 11783에 정의된 메시지 형식, 절차, 전기 규격을 그대로 따른다는 뜻이다. 세 가지 대표 사례를 보자.

**사례 1 — 트랙터 속도 브로드캐스트**

TECU(Tractor ECU)는 PGN 65097(Ground-Based Speed and Distance)을 100ms마다 브로드캐스트해야 한다. 데이터 형식도 정해져 있다.

```
CAN ID: 0x0CFE610E  (Priority=3, PGN=65097, SA=0x0E)
Data:   A0 0F 00 00 FF FF FF FF
        ↑
  Byte 1-2 = 0x0FA0 = 4000 → 4000 × 0.001 m/s = 4.0 m/s (약 14.4 km/h)
```

John Deere 트랙터든 Fendt 트랙터든 같은 PGN, 같은 바이트 위치, 같은 분해능(0.001 m/s)으로 전송한다. 덕분에 어떤 제조사의 작업기를 연결해도 속도를 정확히 읽을 수 있다. 만약 제조사가 자체 PGN을 쓰거나 분해능을 바꾸면, 다른 제조사 장비가 속도를 잘못 읽거나 아예 못 읽는다.

**사례 2 — VT 화면 표시**

작업기 ECU가 트랙터 디스플레이에 UI를 표시하려면 Object Pool을 VT로 전송해야 한다. 이 절차도 표준으로 정해져 있다.

```mermaid
sequenceDiagram
    participant ECU as 작업기 ECU
    participant VT as VT (트랙터 디스플레이)

    ECU->>VT: Address Claim (PGN 60928)
    VT-->>ECU: VT Status (버전, 메모리 정보)
    ECU->>VT: Object Pool 전송 (ETP)
    VT-->>ECU: End of Object Pool 응답
    VT->>VT: 화면 렌더링
    Note over ECU,VT: 어떤 제조사 조합이든 이 절차를 따르면 화면이 표시된다
```

Kverneland 파종기를 John Deere 트랙터에 꽂아도, Fendt 트랙터에 꽂아도 같은 절차로 화면이 표시된다. 반면 자체 프로토콜을 사용하면 같은 제조사 디스플레이에서만 동작한다.

**사례 3 — TC 가변 살포 제어**

TC(Task Controller)가 처방 맵 기반으로 구획별 살포량을 조절할 때도, DDOP와 Process Data 형식이 표준이다. 어떤 제조사의 TC 소프트웨어에서 만든 처방 맵이든, ISOXML 형식을 따르면 어떤 살포기에서든 가변 살포가 동작한다.

**준수 vs 미준수 비교**

| 영역 | 준수 | 미준수 |
|------|------|--------|
| 메시지 형식 | 정해진 PGN/SPN/분해능으로 전송 | 자체 형식 사용 |
| 주소 관리 | Address Claim 절차 수행 | 하드코딩된 주소 사용 |
| VT 화면 | Object Pool로 UI 전송 | 전용 디스플레이에만 표시 |
| TC 제어 | DDOP + Process Data 표준 명령 | 자체 제어 프로토콜 |
| 물리 계층 | 250 kbps, TBC 9핀 커넥터 | 다른 속도, 다른 커넥터 |

---

## 3. ISO 11783 파트 구성

ISO 11783은 14개의 파트(Part)로 구성된 표준이다.

| 파트 | 제목 | 주요 내용 |
|------|------|-----------|
| Part 1 | General | 표준의 범위, 용어 정의, 전체 구조 |
| Part 2 | Physical Layer | 전기적 특성, 케이블, 커넥터 (CAN 250kbps) |
| Part 3 | Data Link Layer | 프레임 형식, CAN 기반 데이터 링크 |
| Part 4 | Network Layer | 네트워크 상호연결, 브리지 |
| Part 5 | Network Management | 주소 클레임, CF(Control Function) 관리 |
| Part 6 | Virtual Terminal | 작업기 UI를 트랙터 화면에 표시 |
| Part 7 | Implement Messages | 작업기 기능 관련 PGN 정의 |
| Part 8 | Power Train Messages | 엔진·변속기 관련 PGN 정의 |
| Part 9 | Tractor ECU | 트랙터 정보(속도, PTO, 히치) 제공 ECU |
| Part 10 | Task Controller | 작업 계획·기록, 정밀 농업 |
| Part 11 | Mobile Data Element | 데이터 사전(Data Dictionary) |
| Part 12 | Diagnostics | 진단 메시지(DM), 고장 코드 |
| Part 13 | File Server | ECU 간 파일 전송 |
| Part 14 | Sequence Control | 작업 순서 자동화 |

---

## 4. J1939과 ISOBUS의 관계

ISOBUS는 SAE J1939을 기반으로 농업 기계에 맞게 <strong>확장</strong>한 표준이다. 프로토콜 계층 관점에서 살펴보면 다음과 같다.

```mermaid
graph TB
    subgraph ISOBUS_계층_구조
        direction TB
        L7["응용 계층 (Application Layer)\n─────────────────────────\nVT (Virtual Terminal) — ISO 11783-6\nTC (Task Controller) — ISO 11783-10\nTECU (Tractor ECU) — ISO 11783-9\n진단 (Diagnostics) — ISO 11783-12\n─────────────────────────\n★ ISOBUS 고유 기능"]

        L4["네트워크 계층 (Network Layer)\n─────────────────────────\nISO 11783-4 / J1939-31\nTP(Transport Protocol) 포함"]

        L3["데이터 링크 계층 (Data Link Layer)\n─────────────────────────\nISO 11783-3 / J1939-21\n29비트 CAN ID, PGN 체계"]

        L2["물리 계층 (Physical Layer)\n─────────────────────────\nISO 11783-2 / J1939-11\nCAN 250kbps, 종단 저항 120Ω"]

        L7 --> L4 --> L3 --> L2
    end
```

정리하면:
- **물리·데이터링크·네트워크 계층**: J1939과 동일한 기반 사용
- **응용 계층**: VT, TC, TECU 등 ISOBUS 고유 기능이 추가됨

J1939을 이해했다면 ISOBUS의 하위 계층은 이미 알고 있는 것과 다름없다. ISOBUS 학습은 응용 계층의 고유 기능에 집중한다.

---

## 5. ISOBUS 생태계

### AEF (Agricultural Industry Electronics Foundation)

AEF는 ISOBUS의 실질적 표준화를 이끄는 국제 단체이다. ISO 표준은 문서 수준의 규격이지만, AEF는 실제 장비 간 상호운용성을 보장하기 위한 활동을 한다.

- **AEF Conformance Test**: 제조사가 장비를 ISOBUS 적합성 테스트에 제출
- **ISOBUS 인증 마크**: 테스트를 통과한 장비에 부여. 인증 마크가 있으면 상호운용성 보장
- **AEF Database**: 인증된 제품 목록 공개, 농민이 조합 가능한 장비 확인 가능

### 주요 참여 제조사

John Deere, AGCO, CNH Industrial(케이스·뉴홀랜드), CLAAS, Fendt, Kverneland, Amazone, Horsch 등 전 세계 주요 농기계 제조사가 AEF 멤버로 참여하고 있다.

---

> **핵심 정리**
> - ISOBUS(ISO 11783)는 트랙터-작업기 간 통신을 표준화한 농업 전용 프로토콜이다.
> - J1939을 기반으로 하되, 응용 계층(VT, TC, TECU)이 ISOBUS 고유의 핵심 기능이다.
> - ISO 11783은 14개 파트로 구성되며, Part 6(VT)과 Part 10(TC)이 가장 핵심적이다.
> - AEF 적합성 인증을 통과한 장비끼리는 제조사에 관계없이 상호운용이 가능하다.

---

## 다음 챕터

- 다음 : [ISOBUS 네트워크 아키텍처](/study/isobus/13-isobus-architecture)
