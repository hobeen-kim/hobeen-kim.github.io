---
title: "VT 오브젝트 풀 (Object Pool)"
description: "VT 화면을 정의하는 오브젝트 풀의 구조, 타입, 계층 관계, 전송 과정을 이해하고 간단한 화면을 직접 구성해본다."
date: 2026-04-13
tags: [ISOBUS, VT, Object Pool, IOP, ISO-11783-6]
prev: /study/isobus/15-vt-basics
next: /study/isobus/17-vt-commands
---

# VT 오브젝트 풀 (Object Pool)

::: info 학습 목표
- 오브젝트 풀의 개념과 바이너리 구조를 설명할 수 있다.
- 주요 오브젝트 타입의 역할을 구분할 수 있다.
- 오브젝트 간 계층 관계(Working Set → Data Mask → 자식 오브젝트)를 이해한다.
- 오브젝트 풀 전송 과정의 각 단계를 순서대로 설명할 수 있다.
- 간단한 화면을 XML(IOP) 형태로 구성할 수 있다.
:::

## 1. 오브젝트 풀이란

<strong>오브젝트 풀(Object Pool)</strong>은 VT 화면 전체를 정의하는 <strong>바이너리 데이터 구조</strong>이다. 작업기 ECU의 플래시 메모리에 저장되어 있다가, VT 연결 시 VT로 전송된다.

각 오브젝트는 세 가지 요소로 구성된다.

```
[Object ID: 16bit] [Object Type: 8bit] [속성(Attribute) 목록...]
```

- **Object ID**: 0x0000 ~ 0xFFFE 범위의 고유 식별자(한 Working Set의 풀 안에서만 유일하면 된다). 0xFFFF는 NULL Object ID로 예약
- **Object Type**: 오브젝트 종류를 나타내는 1바이트 코드
- **속성**: 오브젝트 타입에 따라 위치, 크기, 색상, 자식 오브젝트 목록 등

### 설계부터 전송까지

```
IOP XML 파일 설계
       ↓
바이너리 변환 (툴체인 사용)
       ↓
ECU 플래시에 저장
       ↓
VT 연결 시 전송
       ↓
VT가 화면 렌더링
```

XML(IOP 형식)로 화면을 설계하고 빌드 시 바이너리로 변환하는 방식이 일반적이다. 이를 통해 설계 시점에는 가독성을, 런타임에는 크기 효율성을 모두 확보한다.

## 2. 오브젝트 타입 총정리

ISO 11783-6에는 40여 가지 오브젝트 타입이 정의되어 있다(v6 기준 Type 코드 0~48). 역할별로 분류하면 다음과 같다.

### 컨테이너 및 화면 구조

| 타입 이름 | Type 코드 | 역할 |
|-----------|-----------|------|
| **Working Set Object** | 0 | 오브젝트 풀의 루트. 작업기 전체를 대표 |
| **Data Mask** | 1 | 일반 화면(마스크). 실제 UI가 표시되는 단위 |
| **Alarm Mask** | 2 | 경고/알람 전용 화면. 우선순위로 Data Mask 위에 표시 |
| **Container** | 3 | 여러 오브젝트를 묶는 그룹. 가시성 토글 가능 |
| **Window Mask** | 34 | Version 4+. 복수 윈도우 지원 |

### 소프트키 및 버튼

| 타입 이름 | Type 코드 | 역할 |
|-----------|-----------|------|
| **Soft Key Mask** | 4 | Data Mask에 연결되는 소프트키 버튼 집합 |
| **Key** | 5 | 소프트키 개별 버튼 |
| **Button** | 6 | 화면 내 일반 버튼 오브젝트 |
| **Key Group** | 35 | Version 4+. 키 그룹 |

### 입력 오브젝트

| 타입 이름 | Type 코드 | 역할 |
|-----------|-----------|------|
| **Input Boolean** | 7 | 체크박스 등 불리언 입력 |
| **Input String** | 8 | 문자열 입력 필드 |
| **Input Number** | 9 | 숫자 입력 필드 |
| **Input List** | 10 | 목록 선택 입력 |

### 출력 오브젝트

| 타입 이름 | Type 코드 | 역할 |
|-----------|-----------|------|
| **Output String** | 11 | 문자열 출력 |
| **Output Number** | 12 | 숫자 출력 (변수 참조 가능) |
| **Output Line** | 13 | 선 그리기 |
| **Output Rectangle** | 14 | 사각형 그리기 |
| **Output Ellipse** | 15 | 타원 그리기 |
| **Output Polygon** | 16 | 다각형 그리기 |
| **Output Meter** | 17 | 미터 게이지 |
| **Output Linear Bar Graph** | 18 | 선형 막대 그래프 |
| **Output Arched Bar Graph** | 19 | 호형 막대 그래프 |
| **Picture Graphic** | 20 | 비트맵 이미지 |
| **Output List** | 37 | 목록 출력 (Version 4+) |

### 속성 오브젝트

| 타입 이름 | Type 코드 | 역할 |
|-----------|-----------|------|
| **Font Attributes** | 23 | 폰트 크기, 색상, 스타일 정의 |
| **Line Attributes** | 24 | 선 색상, 두께, 스타일 정의 |
| **Fill Attributes** | 25 | 채우기 색상, 패턴 정의 |
| **Input Attributes** | 26 | 입력 필드의 유효 문자 목록 |

### 기타

| 타입 이름 | Type 코드 | 역할 |
|-----------|-----------|------|
| **Number Variable** | 21 | 공유 숫자 변수 |
| **String Variable** | 22 | 공유 문자열 변수 |
| **Object Pointer** | 27 | 다른 오브젝트를 참조하는 포인터 |
| **Macro** | 28 | 이벤트 기반 자동화 명령 목록 |
| **External Object Pointer** | 43 | 다른 Working Set의 오브젝트 참조 (Version 5+) |

## 3. 오브젝트 간 계층 관계

오브젝트들은 트리 구조로 조직된다. <strong>Working Set Object</strong>가 루트이며, 모든 화면과 요소가 그 아래에 위치한다.

```mermaid
graph TD
    WS["Working Set Object<br>(ID: 0)"]
    DM1["Data Mask 1<br>일반 작업 화면"]
    DM2["Data Mask 2<br>설정 화면"]
    AM["Alarm Mask<br>경고 화면"]
    SKM["Soft Key Mask<br>소프트키 집합"]
    SK1["Key 1<br>'시작'"]
    SK2["Key 2<br>'정지'"]
    BTN["Button<br>'확인'"]
    CON["Container<br>온도 정보 그룹"]
    ON["Output Number<br>85°C"]
    OS["Output String<br>'엔진 온도'"]
    FA["Font Attributes<br>글꼴 정의"]

    WS --> DM1
    WS --> DM2
    WS --> AM
    DM1 --> SKM
    DM1 --> CON
    DM1 --> BTN
    SKM --> SK1
    SKM --> SK2
    CON --> ON
    CON --> OS
    ON --> FA
    OS --> FA
```

계층의 핵심 규칙:

- <strong>Data Mask</strong>는 Working Set에서 active mask로 지정되어야 화면에 표시된다.
- <strong>Soft Key Mask</strong>는 Data Mask에 연결되어 함께 활성화된다.
- **속성 오브젝트**(Font, Line, Fill Attributes)는 여러 오브젝트에서 공유할 수 있다.
- <strong>Container</strong>는 가시성(visible/hidden) 속성으로 동적으로 표시/숨김이 가능하다.

## 4. 오브젝트 풀 전송 과정

작업기 ECU가 VT에 처음 연결될 때 오브젝트 풀을 전송하는 절차는 다음과 같다.

```mermaid
sequenceDiagram
    participant ECU as 작업기 ECU (VT Client)
    participant VT as VT Server

    VT-->>ECU: VT Status Message (1초 주기 — 활성 마스크, busy 상태 등)
    ECU->>VT: Working Set Maintenance (1초 주기)

    ECU->>VT: Get Memory (오브젝트 풀 크기 전달, VT 버전 확인)
    VT-->>ECU: Get Memory Response (저장 가능 여부 확인)

    alt 버전이 일치하는 오브젝트 풀이 VT에 이미 저장된 경우
        ECU->>VT: Load Version (저장된 버전 로드 요청)
        VT-->>ECU: Load Version Response (성공)
    else 새로 전송해야 하는 경우
        ECU->>VT: Object Pool Transfer (TP/ETP로 전송, 응답 없음)
        Note over ECU, VT: 1785바이트 초과 시 ETP 사용<br>ETP 최대 117,440,505 바이트 전송 가능
        ECU->>VT: End of Object Pool (전송 완료 알림)
        Note over VT: 파싱 동안 VT Status의 parsing 비트 = 1
        VT-->>ECU: End of Object Pool Response (파싱 결과 반환)
        ECU->>VT: Store Version (이후 Load Version을 위해 저장)
    end

    VT->>VT: 오브젝트 풀 파싱 및 화면 활성화
    Note over VT: Working Set의 Active Data Mask 표시
```

### VT 능력 질의와 스케일링

전송 전에 Working Set Master는 Get Memory 외에도 기술 데이터(Technical data) 메시지 — <strong>Get Number of Soft Keys</strong>, <strong>Get Text Font Data</strong>, <strong>Get Hardware</strong> 등 — 로 VT의 소프트키 수, 지원 폰트·스타일, 색상 모드, Data Mask 픽셀 크기를 질의할 수 있다. Master는 이 응답에 맞춰 풀을 조정해야 한다.

- **위치·크기**: VT의 Data Mask 영역·designator 크기에 맞춰 오브젝트의 위치와 크기를 스케일한다.
- **폰트**: 정의된 영역에 best-fit 알고리즘으로 폰트를 선택한다. 최소 폰트는 6×8이며, 스케일 결과가 그보다 작으면 6×8을 쓴다.
- <strong>Picture Graphic</strong>은 VT가 오브젝트의 width 속성에 따라 자동 스케일한다.

### 전송 완료 대기와 오류 처리

End of Object Pool message를 보낸 뒤 VT는 파싱을 마칠 때까지 VT Status message의 parsing 비트를 1로 유지한다. Working Set Master는 parsing 비트가 0인 VT Status message가 <strong>연속 3번</strong> 수신될 때까지 End of Object Pool response를 기다려야 하고, 그때까지 응답이 없으면 메시지 미도달로 간주해 최대 3회 재시도할 수 있다(Load Version도 같은 대기 규칙을 쓴다).

End of Object Pool response가 오류(풀 오류, 메모리 고갈 등)를 담으면 VT는 풀을 휘발성 메모리에서 삭제하고 Working Set 중단을 운전자에게 알람으로 알린다. 이 응답을 받은 ECU는 장치의 안전한 셧다운 절차를 제공하는 fail-safe 운전 모드로 들어가야 한다.

### 버전 관리 (Store/Load Version)

오브젝트 풀이 크면 전송에 수 초가 걸릴 수 있다. 이를 개선하기 위해 VT는 오브젝트 풀을 <strong>버전 라벨(7문자 문자열, Version 5+는 32문자 확장 라벨도 지원)</strong>과 함께 비휘발성 저장소에 저장할 수 있다. 다음 연결 시 **Load Version** 명령만으로 저장된 풀을 즉시 복원하여 전송 시간을 절약한다.

## 5. 간단한 화면 구성 실습

"엔진 온도: 85°C"를 표시하는 화면을 구성해 보겠다.

### 필요한 오브젝트 구성

```
Working Set (ID: 0)
└── Data Mask (ID: 1) ← Active Data Mask로 지정
    ├── Output String (ID: 10) ← "엔진 온도:" 레이블
    │   └── Font Attributes (ID: 30) ← 검정, 24×32 픽셀
    └── Output Number (ID: 11) ← 85 (°C 단위)
        └── Font Attributes (ID: 30) ← 공유 사용
```

### IOP XML 예시

```xml
<objectpool>

  <!-- Working Set: 오브젝트 풀의 루트 -->
  <workingset id="0"
              background_colour="1"
              selectable="true"
              active_mask="1">
    <!-- active_mask="1" → Data Mask ID 1이 초기 화면 -->
  </workingset>

  <!-- Font Attributes: 검정, 24×32 픽셀 폰트 -->
  <fontattributes id="30"
                  font_colour="0"
                  font_size="6"
                  font_style="0" />
  <!-- font_colour 0 = 검정(VT 표준 팔레트 기준. 1 = 흰색) -->
  <!-- font_size 6 = 24×32 픽셀 -->

  <!-- Data Mask: 실제 화면 영역 -->
  <datamask id="1"
            background_colour="1"
            soft_key_mask="65535">
    <!-- soft_key_mask 65535 = 소프트키 없음 -->
    <include_object id="10" pos_x="10" pos_y="20" />
    <include_object id="11" pos_x="130" pos_y="20" />
  </datamask>

  <!-- Output String: "엔진 온도:" 레이블 -->
  <outputstring id="10"
                width="120"
                height="30"
                font_attributes="30"
                justification="0"
                value="엔진 온도:" />

  <!-- Output Number: 실시간 온도 값 -->
  <outputnumber id="11"
                width="80"
                height="30"
                font_attributes="30"
                variable_reference="65535"
                value="85"
                offset="0"
                scale="1.0"
                number_of_decimals="0"
                format="true"
                justification="0" />
  <!-- value="85": 초기값 85°C -->
  <!-- ECU가 Change Numeric Value 명령으로 실시간 갱신 -->

</objectpool>
```

### 런타임 데이터 갱신

화면이 표시된 후, ECU는 실측 온도가 바뀔 때마다 `Change Numeric Value` 명령으로 Output Number의 값을 갱신한다. VT 명령은 ECU→VT 방향 PGN 0xE700(59136)으로 보내고, VT의 응답은 VT→ECU 방향 PGN 0xE600(58880)으로 돌아온다. VT는 별도의 오브젝트 풀 재전송 없이 해당 오브젝트만 업데이트하여 화면에 반영한다.

```
ECU → VT: Change Numeric Value
  Object ID: 0x000B (Output Number ID 11)
  New Value : 92    (92°C로 갱신)
```

::: tip 핵심 정리
- 오브젝트 풀은 VT 화면 전체를 정의하는 바이너리 구조이며, 각 오브젝트는 ID + 타입 + 속성으로 구성된다.
- Working Set → Data Mask → Container/Output/Input → 속성 오브젝트 순의 계층 구조를 가진다.
- 오브젝트 풀 전송 시 TP/ETP를 사용하며(1785바이트 초과 시 ETP), Store/Load Version으로 재전송 시간을 절약한다.
- 화면 초기화 후 ECU는 Change Numeric Value 등의 명령어로 특정 오브젝트만 실시간 갱신한다.
:::

## 다음 챕터

- 다음 : [VT 명령어와 상호작용](/study/isobus/17-vt-commands)
