---
title: "VT 오브젝트 풀 기초"
description: "VT 화면을 정의하는 오브젝트 풀이 무엇으로 이루어지고 어떻게 VT로 전송되는지 익히고, 간단한 화면 하나를 XML에서 바이트까지 직접 만들어 본다."
date: 2026-04-13
tags: [ISOBUS, VT, Object Pool, IOP, ISO-11783-6]
prev: /study/isobus/31-vt-connection
next: /study/isobus/33-vt-object-records
---

# VT 오브젝트 풀 기초

::: info 학습 목표
- 오브젝트 풀이 무엇이고 작업기가 왜 그것을 VT에 보내는지 설명할 수 있다.
- 주요 오브젝트 타입(마스크, 키, 입력, 출력, 속성)의 역할과 타입 번호를 구분할 수 있다.
- Working Set에서 Data Mask, 자식 오브젝트로 이어지는 계층 관계를 그림으로 그릴 수 있다.
- 오브젝트 풀 전송 과정을 순서대로 설명할 수 있다.
- 간단한 화면의 XML 설계를 오브젝트 레코드 바이트로 바꿔 읽을 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [29장 VT 기초](/study/isobus/29-vt-basics), [30장 VT 화면과 기술 데이터](/study/isobus/30-vt-display-technical-data), [31장 VT 연결 관리](/study/isobus/31-vt-connection)
- 이 장에서 처음 나오는 말
  - 오브젝트(object): 화면을 이루는 부품 하나. 글자 한 줄, 숫자 칸, 버튼, 글꼴 설정 같은 것이다.
  - 오브젝트 풀(object pool): 작업기 하나가 쓰는 오브젝트를 모두 모은 묶음. 작업기 화면의 설계도다.
  - Object ID: 풀 안에서 오브젝트 하나를 가리키는 번호(0~65534).
  - 오브젝트 타입(Object Type): 그 오브젝트가 버튼인지 글자인지 알려 주는 1바이트 번호.
  - 속성(attribute): 오브젝트의 위치, 크기, 색 같은 설정값.
  - 레코드(record): 오브젝트 하나를 바이트로 적은 것.
:::

레고 상자를 열면 부품과 조립 설명서가 함께 들어 있다. 설명서에는 어느 부품을 어디에 끼우는지가 적혀 있어서, 누가 조립해도 같은 모양이 나온다. VT(Virtual Terminal, 운전석에 있는 공용 화면 단말) 화면도 이렇게 만든다. 작업기는 화면 부품(글자, 숫자 칸, 버튼)과 배치 정보를 한 묶음으로 VT에 보내고, VT는 그 설명대로 화면을 조립해 그린다. 이 묶음이 오브젝트 풀이다.

비유가 맞지 않는 지점도 하나 있다. 레고는 한 번 조립하면 끝나지만, VT 화면은 떠 있는 동안에도 작업기가 명령을 보내 숫자나 글자를 계속 바꾼다. 이 장에서는 오브젝트 풀이 무엇으로 이루어지고 VT로 어떻게 옮겨지는지 본 뒤, 작은 화면 하나를 바이트까지 직접 만들어 본다.

## 1. 오브젝트 풀이란

VT는 트랙터에 붙어 있는 공용 화면이라, 어떤 회사의 작업기가 연결될지 미리 알지 못한다. 그래서 화면 설계는 작업기가 직접 갖고 와야 한다. 이 절에서는 그 설계도인 오브젝트 풀이 무엇으로 이루어지는지 본다.

<strong>오브젝트 풀(Object Pool)</strong>은 VT 화면 전체를 정의하는 <strong>바이너리 데이터 구조</strong>이다. 바이너리는 사람이 읽는 글자가 아니라 바이트를 그대로 나열한 데이터라는 뜻이다. 오브젝트 풀은 작업기 ECU(Electronic Control Unit, 작업기를 제어하는 컴퓨터)의 플래시 메모리에 저장되어 있다가, VT 연결 시 VT로 전송된다.

각 오브젝트는 세 가지 요소로 구성된다.

```
[Object ID: 16bit] [Object Type: 8bit] [속성(Attribute) 목록...]
```

- **Object ID**: 0x0000 ~ 0xFFFE(=0~65534) 범위의 고유 식별자(한 Working Set의 풀 안에서만 유일하면 된다). 0xFFFF(=65535)는 NULL Object ID로 예약
- **Object Type**: 오브젝트 종류를 나타내는 1바이트 코드
- **속성**: 오브젝트 타입에 따라 위치, 크기, 색상, 자식 오브젝트 목록 등

레고에 견주면 Object ID는 부품 번호, Object Type은 부품 종류(바퀴인지 벽돌인지), 속성은 그 부품의 크기와 색이다. NULL Object ID는 "아무 오브젝트도 가리키지 않음"을 뜻하는 특별한 번호다. 예를 들어 "이 화면에는 소프트키가 없다"를 나타낼 때 소프트키 자리에 65535를 적는다. Working Set은 VT에게 작업기 하나로 보이는 ECU 묶음이다([26장](/study/isobus/26-isobus-network-mgmt)). 오브젝트 풀은 Working Set마다 하나씩 있다.

### 설계부터 전송까지

오브젝트 풀은 사람이 바이트를 손으로 적어서 만들지 않는다. 보통 다음 순서를 거친다.

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

1. 개발자가 화면을 XML(태그로 구조를 적는 텍스트 형식)로 설계한다. IOP라는 이름은 5절에서 설명한다.
2. 툴체인(설계 파일을 변환하는 개발 도구 모음)이 XML을 바이너리 레코드로 바꾼다.
3. 바이너리를 작업기 ECU의 플래시 메모리에 넣는다.
4. 작업기가 VT에 연결되면 이 바이너리를 보낸다(4절).
5. VT가 바이너리를 읽어 화면을 그린다(렌더링).

XML(IOP 형식)로 화면을 설계하고 빌드 시 바이너리로 변환하는 방식이 일반적이다. 이를 통해 설계 시점에는 가독성을, 런타임에는 크기 효율성을 모두 확보한다. 사람은 읽기 쉬운 XML로 작업하고, 버스에는 크기가 작은 바이너리가 오른다.

## 2. 오브젝트 타입 총정리

풀에는 여러 종류의 부품이 섞여 있다. 종류마다 번호가 정해져 있어서, VT는 레코드 앞부분의 타입 번호만 보고 그 부품이 무엇인지 안다. 다른 장에서 타입 번호가 나오면 이 절의 표를 다시 찾아보면 된다.

ISO 11783-6(VT를 정하는 표준 문서)에는 40여 가지 오브젝트 타입이 정의되어 있다(v6 기준 Type 코드 0~48). 역할별로 분류하면 다음과 같다. v6은 VT 버전 6을 뜻하고, 표의 "Version 4+"는 VT 버전 4 이상에서만 쓸 수 있다는 뜻이다(VT 버전은 [29장](/study/isobus/29-vt-basics)).

### 컨테이너 및 화면 구조

화면 한 장이나 화면 속 묶음을 만드는 오브젝트다. 다른 오브젝트를 안에 담는 상자 역할을 한다.

| 타입 이름 | Type 코드 | 역할 |
|-----------|-----------|------|
| **Working Set Object** | 0 | 오브젝트 풀의 루트. 작업기 전체를 대표 |
| **Data Mask** | 1 | 일반 화면(마스크). 실제 UI가 표시되는 단위 |
| **Alarm Mask** | 2 | 경고/알람 전용 화면. 우선순위로 Data Mask 위에 표시 |
| **Container** | 3 | 여러 오브젝트를 묶는 그룹. 가시성 토글 가능 |
| **Window Mask** | 34 | Version 4+. 복수 윈도우 지원 |

마스크(mask)는 VT 화면 한 장을 뜻한다. 루트(root)는 나무의 뿌리처럼 모든 오브젝트가 거슬러 올라가면 닿는 맨 위 오브젝트다.

### 소프트키 및 버튼

운전자가 누르는 오브젝트다. 소프트키(Soft Key)는 화면 옆에 늘어선 키로, 화면마다 뜻이 바뀐다.

| 타입 이름 | Type 코드 | 역할 |
|-----------|-----------|------|
| **Soft Key Mask** | 4 | Data Mask에 연결되는 소프트키 버튼 집합 |
| **Key** | 5 | 소프트키 개별 버튼 |
| **Button** | 6 | 화면 내 일반 버튼 오브젝트 |
| **Key Group** | 35 | Version 4+. 키 그룹 |

Window Mask와 Key Group은 여러 Working Set의 화면 조각과 키를 VT 화면 한 장에 모아 보여 주는 User-Layout 기능에서 쓴다([34장](/study/isobus/34-vt-layout-color)).

### 입력 오브젝트

운전자가 값을 넣는 칸이다.

| 타입 이름 | Type 코드 | 역할 |
|-----------|-----------|------|
| **Input Boolean** | 7 | 체크박스 등 불리언 입력 |
| **Input String** | 8 | 문자열 입력 필드 |
| **Input Number** | 9 | 숫자 입력 필드 |
| **Input List** | 10 | 목록 선택 입력 |

불리언(Boolean)은 참/거짓 두 값 중 하나라는 뜻이다.

### 출력 오브젝트

화면에 글자, 숫자, 도형, 그림을 보여 주기만 하는 오브젝트다.

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

혼자서는 화면에 나타나지 않고, 다른 오브젝트가 가리켜서 쓰는 설정 묶음이다. 여러 오브젝트가 같은 글꼴 설정을 함께 쓰면 풀이 작아진다.

| 타입 이름 | Type 코드 | 역할 |
|-----------|-----------|------|
| **Font Attributes** | 23 | 폰트 크기, 색상, 스타일 정의 |
| **Line Attributes** | 24 | 선 색상, 두께, 스타일 정의 |
| **Fill Attributes** | 25 | 채우기 색상, 패턴 정의 |
| **Input Attributes** | 26 | 입력 필드의 유효 문자 목록 |

### 기타

값을 보관하는 변수, 다른 오브젝트를 가리키는 포인터, 자동 실행 명령 묶음이다.

| 타입 이름 | Type 코드 | 역할 |
|-----------|-----------|------|
| **Number Variable** | 21 | 공유 숫자 변수 |
| **String Variable** | 22 | 공유 문자열 변수 |
| **Object Pointer** | 27 | 다른 오브젝트를 참조하는 포인터 |
| **Macro** | 28 | 이벤트 기반 자동화 명령 목록 |
| **External Object Pointer** | 43 | 다른 Working Set의 오브젝트 참조 (Version 5+) |

### 그 밖의 타입과 번호 범위

위 표에 없는 표준 타입과, 아직 아무 오브젝트에도 배정되지 않은 번호를 모았다. 0~255 가운데 어떤 번호가 어떤 뜻인지 이 표까지 보면 빠짐없이 알 수 있다.

| 타입 이름 | Type 코드 | 역할 |
|-----------|-----------|------|
| Auxiliary Function Type 1, Auxiliary Input Type 1 | 29, 30 | 옛 방식 보조 입력(AUX)의 기능·입력 정의. Version 3+ VT는 호환을 위해 읽기만 하고 기능은 지원하지 않는다 |
| Auxiliary Function Type 2, Auxiliary Input Type 2 | 31, 32 | 조이스틱 같은 보조 입력과 작업기 기능을 짝짓는 정의 (Version 3+, [40장](/study/isobus/40-vt-aux)) |
| Auxiliary Control Designator Type 2 Object Pointer | 33 | Auxiliary Input Type 2나 Auxiliary Function Type 2를 가리키는 포인터 (Version 3+) |
| Graphics Context | 36 | 그림을 그려 넣는 캔버스 (Version 4+, 선택 기능) |
| Extended Input Attributes | 38 | 입력 필드에 허용할 WideChar(2바이트 문자) 목록 (Version 4+) |
| Colour Map | 39 | 색 번호를 다른 색 번호로 바꿔 읽는 표 (Version 4+, 선택 기능, [34장](/study/isobus/34-vt-layout-color)) |
| Object Label Reference List | 40 | 오브젝트에 붙이는 이름표 목록 (Version 4+) |
| External Object Definition | 41 | 다른 Working Set이 참조해도 되는 오브젝트 목록 (Version 5+) |
| External Reference NAME | 42 | 참조할 상대 Working Set의 Master를 NAME으로 지정 (Version 5+) |
| Animation | 44 | 간단한 애니메이션 표시 (Version 5+) |
| Colour Palette | 45 | 색 팔레트를 다시 정의 (Version 6+, [34장](/study/isobus/34-vt-layout-color)) |
| Graphic Data | 46 | 그림 데이터 정의 (Version 6+) |
| Working Set Special Controls | 47 | Colour Map·Colour Palette 같은 특수 설정의 초기 선택 (Version 6+, [34장](/study/isobus/34-vt-layout-color)) |
| Scaled Graphic | 48 | 그림 오브젝트를 크기를 바꿔 표시 (Version 6+) |
| (예약) | 49~239 | 앞으로 쓰려고 비워 둔 번호. 어떤 오브젝트에도 배정되지 않았다 |
| 제조사 정의 오브젝트 | 240~254 | 제조사가 자기 VT용으로 정한 오브젝트 (Version 4+). 다른 제조사의 VT에는 보내지 않는 것이 권고다 |
| (예약) | 255 | 비워 둔 번호. 어떤 오브젝트에도 배정되지 않았다 |

"선택 기능"은 VT가 지원하지 않아도 되는 기능이라는 뜻이다. 그래도 버전 4 이상 VT는 풀에 그런 오브젝트가 들어 있으면 읽고 건너뛸 수는 있어야 한다. NAME은 장치마다 하나뿐인 64비트 이름이다([12장](/study/isobus/12-j1939-address-name)).

타입 번호 255(`FF`)는 비어 있다. 그래서 VT가 지원하는 타입 번호를 늘어놓는 메시지(Get Supported Objects 응답, [30장](/study/isobus/30-vt-display-technical-data))가 `FF`를 목록 끝 표시로 써도 실제 타입 번호와 겹칠 일이 없다. 표준은 255를 예약하면서 바로 이 Get Supported Objects 메시지를 함께 가리킨다. 이유를 적어 두지는 않았지만, 이 충돌을 피하려는 것으로 보인다.

### 직접 눌러 보기

아래는 오브젝트 타입별로 화면에 어떻게 그려지는지, 그리고 운전자가 누를 때 VT가 어떤 메시지를 내보내는지를 재현한 시뮬레이터다. 오브젝트를 누르면 해당 타입 설명과 실제 8바이트 메시지가 함께 표시된다.

<VtObjectPoolDemo />

출력 오브젝트(Output String·Output Number·Output Meter 등)는 눌러도 메시지가 나가지 않는다. 입력 오브젝트와 Button·Key만 운전자 조작을 Working Set에 통지한다. 메시지 종류와 바이트 배치는 [36장 VT 명령어 기초](/study/isobus/36-vt-commands-basics)와 [39장 경보와 활성화 메시지](/study/isobus/39-vt-alarm-activation)에서 더 자세히 다룬다.

정리하면, 타입 번호는 "이 레코드를 어떤 규칙으로 읽을지"를 정하는 열쇠다. 0~48이 표준 오브젝트, 240~254가 제조사 정의 오브젝트이고 나머지(49~239, 255)는 예약이다.

<small>근거: ISO 11783-6 Table A.1, D.14, D.15</small>

## 3. 오브젝트 간 계층 관계

오브젝트는 따로 떨어져 있지 않고 서로 담고 담기는 관계로 이어진다. 이 절에서는 그 연결 모양을 본다. 컴퓨터의 폴더 안에 하위 폴더와 파일이 들어 있는 모습을 떠올리면 된다.

오브젝트들은 트리 구조로 조직된다. <strong>Working Set Object</strong>가 루트이며, 모든 화면과 요소가 그 아래에 위치한다.

![오브젝트 계층 예: Working Set Object(ID 0) 아래에 Data Mask 1(일반 작업 화면), Data Mask 2(설정 화면), Alarm Mask(경고 화면)가 있다. Data Mask 1에는 Soft Key Mask(Key 1 시작, Key 2 정지)가 연결되고 Container(온도 정보 그룹: Output Number 85°C, Output String 엔진 온도)와 Button 확인이 들어 있으며, Output Number와 Output String은 같은 Font Attributes를 함께 가리킨다](/images/study-isobus/32-object-hierarchy-light.png)
![오브젝트 계층 예: Working Set Object(ID 0) 아래에 Data Mask 1(일반 작업 화면), Data Mask 2(설정 화면), Alarm Mask(경고 화면)가 있다. Data Mask 1에는 Soft Key Mask(Key 1 시작, Key 2 정지)가 연결되고 Container(온도 정보 그룹: Output Number 85°C, Output String 엔진 온도)와 Button 확인이 들어 있으며, Output Number와 Output String은 같은 Font Attributes를 함께 가리킨다](/images/study-isobus/32-object-hierarchy-dark.png)

그림을 위에서 아래로 읽는다. 실선 화살표는 부모가 자식을 안에 담는다는 뜻이고, 주황 점선은 속성 값에 Object ID를 적어 다른 오브젝트를 가리킨다(참조)는 뜻이다.

1. 맨 위 Working Set Object(ID 0)가 이 작업기 전체를 대표한다.
2. 그 아래에 화면 세 장이 있다. 일반 작업 화면(Data Mask 1), 설정 화면(Data Mask 2), 경고 화면(Alarm Mask)이다.
3. 일반 작업 화면에는 소프트키 묶음(Soft Key Mask)이 연결되어 있고, 온도 정보 묶음(Container)과 확인 버튼(Button)이 들어 있다.
4. 소프트키 묶음에는 '시작'과 '정지' 키가 있고, 온도 정보 묶음에는 숫자(85°C)와 글자('엔진 온도')가 있다.
5. 숫자와 글자는 같은 글꼴 정의(Font Attributes)를 함께 가리킨다.

5번에서 보듯 이 구조는 완전한 나무 모양은 아니다. 속성 오브젝트 하나를 여러 부모가 함께 가리킬 수 있기 때문이다. 폴더 비유도 여기서는 맞지 않는다. 파일 하나가 두 폴더에 동시에 들어 있는 셈이다.

계층의 핵심 규칙:

- <strong>Data Mask</strong>는 Working Set에서 active mask로 지정되어야 화면에 표시된다. active mask는 "지금 보여 줄 화면"을 가리키는 Working Set의 속성이다.
- <strong>Soft Key Mask</strong>는 Data Mask에 연결되어 함께 활성화된다. 화면이 바뀌면 그 화면에 연결된 소프트키 묶음도 함께 바뀐다.
- **속성 오브젝트**(Font, Line, Fill Attributes)는 여러 오브젝트에서 공유할 수 있다.
- <strong>Container</strong>는 가시성(visible/hidden) 속성으로 동적으로 표시/숨김이 가능하다.

정리하면, 오브젝트 풀은 Working Set을 뿌리로 화면(마스크), 화면 속 부품, 공유 설정(속성 오브젝트) 순으로 이어진다.

## 4. 오브젝트 풀 전송 과정

설계도는 VT에 도착해야 쓸모가 있다. 이 절에서는 풀을 보내는 순서와, 그 과정에서 생기는 기다림과 오류를 본다.

작업기 ECU가 VT에 처음 연결될 때 오브젝트 풀을 전송하는 절차는 다음과 같다. 그림의 왼쪽이 작업기 ECU(VT 클라이언트), 오른쪽이 VT(서버)이고 위에서 아래로 시간이 흐른다.

![오브젝트 풀 전송 순서: VT Status와 Working Set Maintenance가 1초마다 오가는 가운데 작업기가 Get Memory로 풀 크기를 알리고 응답을 받는다. 저장된 같은 버전이 있으면 Load Version과 응답으로 끝나고, 없으면 Object Pool Transfer(TP 또는 ETP, 응답 없음), End of Object Pool, VT의 파싱(parsing 비트 1), End of Object Pool Response, Store Version 순으로 진행한 뒤 VT가 Active Data Mask를 표시한다](/images/study-isobus/32-pool-transfer-light.png)
![오브젝트 풀 전송 순서: VT Status와 Working Set Maintenance가 1초마다 오가는 가운데 작업기가 Get Memory로 풀 크기를 알리고 응답을 받는다. 저장된 같은 버전이 있으면 Load Version과 응답으로 끝나고, 없으면 Object Pool Transfer(TP 또는 ETP, 응답 없음), End of Object Pool, VT의 파싱(parsing 비트 1), End of Object Pool Response, Store Version 순으로 진행한 뒤 VT가 Active Data Mask를 표시한다](/images/study-isobus/32-pool-transfer-dark.png)

단계별로 읽으면 다음과 같다.

1. VT는 VT Status 메시지를 1초마다 보낸다. 이 메시지에는 지금 활성인 마스크, VT가 바쁜지(busy) 같은 상태가 들어 있다. 작업기는 Working Set Maintenance 메시지를 1초마다 보내 "아직 연결되어 있다"고 알린다([31장](/study/isobus/31-vt-connection)).
2. 작업기가 Get Memory로 오브젝트 풀 크기를 알리고 VT 버전을 확인한다. VT는 Get Memory Response로 그만큼 저장할 수 있는지 답한다.
3. VT에 버전이 일치하는 오브젝트 풀이 이미 저장되어 있으면, 작업기는 Load Version으로 저장된 버전을 불러 달라고 요청한다. VT가 Load Version Response로 성공을 알리면 전송은 끝이다.
4. 새로 보내야 하면 작업기는 Object Pool Transfer로 풀을 보낸다. 풀은 보통 CAN 프레임 하나(8바이트)보다 크므로 TP(Transport Protocol, 긴 데이터를 여러 프레임으로 나눠 보내는 규칙, [15장](/study/isobus/15-tp-bam-cmdt))나 ETP(Extended TP, [17장](/study/isobus/17-etp))를 쓴다. 1785바이트를 넘으면 ETP를 쓰며, ETP로는 최대 117,440,505바이트까지 보낼 수 있다. VT는 Object Pool Transfer 메시지에 응답하지 않는다.
5. 작업기가 End of Object Pool로 "다 보냈다"고 알린다.
6. VT가 받은 풀을 파싱(바이트를 규칙대로 읽어 오브젝트로 해석)한다. 파싱하는 동안 VT Status의 parsing 비트는 1이다.
7. VT가 End of Object Pool Response로 파싱 결과를 돌려준다.
8. 작업기가 Store Version으로 풀을 저장해 달라고 요청한다. 다음 연결에서 3번의 Load Version을 쓰기 위해서다.
9. VT는 풀 파싱을 마치고 화면을 활성화한다. Working Set의 Active Data Mask가 화면에 나타난다.

### VT 능력 질의와 스케일링

VT마다 화면 크기와 소프트키 수가 다르다. 그래서 작업기는 풀을 보내기 전에 VT의 능력을 물어보고 풀을 맞출 수 있다.

전송 전에 Working Set Master(Working Set을 대표해 VT와 통신하는 ECU)는 Get Memory 외에도 기술 데이터(Technical data) 메시지(<strong>Get Number of Soft Keys</strong>, <strong>Get Text Font Data</strong>, <strong>Get Hardware</strong> 등)로 VT의 소프트키 수, 지원 폰트·스타일, 색상 모드, Data Mask 픽셀 크기를 질의할 수 있다. Master는 이 응답에 맞춰 풀을 조정해야 한다. 각 메시지의 바이트는 [30장](/study/isobus/30-vt-display-technical-data)에서 다룬다.

- **위치·크기**: VT의 Data Mask 영역·designator 크기에 맞춰 오브젝트의 위치와 크기를 스케일한다. designator는 소프트키 하나에 그려지는 그림 영역이다.
- **폰트**: 정의된 영역에 best-fit 알고리즘(주어진 칸에 가장 잘 맞는 것을 고르는 방법)으로 폰트를 선택한다. 최소 폰트는 6×8이며, 스케일 결과가 그보다 작으면 6×8을 쓴다.
- <strong>Picture Graphic</strong>은 VT가 오브젝트의 width 속성에 따라 자동 스케일한다.

스케일(scale)은 크기를 일정한 비율로 늘리거나 줄이는 것이다. 예를 들어 200×200 화면에 맞춰 만든 풀을 480×480 화면에 띄우려면 위치와 크기를 2.4배로 늘려야 한다.

### 전송 완료 대기와 오류 처리

End of Object Pool을 보낸 뒤 작업기는 결과를 기다려야 한다. 큰 풀은 파싱에 시간이 걸리므로 언제까지 기다릴지가 정해져 있다.

End of Object Pool message를 보낸 뒤 VT는 파싱을 마칠 때까지 VT Status message의 parsing 비트를 1로 유지한다. Working Set Master는 parsing 비트가 0인 VT Status message가 <strong>연속 3번</strong> 수신될 때까지 End of Object Pool response를 기다려야 하고, 그때까지 응답이 없으면 메시지 미도달로 간주해 최대 3회 재시도할 수 있다(Load Version도 같은 대기 규칙을 쓴다).

End of Object Pool response가 오류(풀 오류, 메모리 고갈 등)를 담으면 VT는 풀을 휘발성 메모리에서 삭제하고 Working Set 중단을 운전자에게 알람으로 알린다. 이 응답을 받은 ECU는 장치의 안전한 셧다운 절차를 제공하는 fail-safe 운전 모드로 들어가야 한다. 휘발성 메모리는 전원이 꺼지면 내용이 사라지는 메모리이고, fail-safe 모드는 고장이 나도 위험하지 않은 쪽으로 기계를 멈추는 운전 상태다. 오류 응답의 바이트를 읽는 법은 [35장](/study/isobus/35-vt-pool-transfer-charset)에서 다룬다.

### 버전 관리 (Store/Load Version)

같은 풀을 연결할 때마다 다시 보내면 시간이 아깝다. 그래서 VT가 풀을 기억해 두는 방법이 있다.

오브젝트 풀이 크면 전송에 수 초가 걸릴 수 있다. 이를 개선하기 위해 VT는 오브젝트 풀을 <strong>버전 라벨(7문자 문자열, Version 5+는 32문자 확장 라벨도 지원)</strong>과 함께 비휘발성 저장소(전원을 꺼도 지워지지 않는 저장소)에 저장할 수 있다. 다음 연결 시 **Load Version** 명령만으로 저장된 풀을 즉시 복원하여 전송 시간을 절약한다. 버전 라벨을 정하는 법과 저장 명령의 바이트는 [31장](/study/isobus/31-vt-connection)에서 다룬다.

정리하면, 풀 전송은 "크기 확인(Get Memory) → 저장본이 있으면 불러오기(Load Version), 없으면 보내기(Object Pool Transfer) → 결과 확인(End of Object Pool) → 저장(Store Version)" 순서다.

## 5. 간단한 화면 구성 실습

지금까지 본 오브젝트로 작은 화면 하나를 직접 설계한다. 이 화면은 6절과 7절에서 바이트로 바꾸고, 33장에서도 다시 쓴다.

"엔진 온도: 85°C"를 표시하는 화면을 구성해 보겠다.

### 필요한 오브젝트 구성

화면 하나에 오브젝트 다섯 개가 필요하다. 루트인 Working Set(ID 0), 화면인 Data Mask(ID 1), 글자 "엔진 온도:"를 보여 줄 Output String(ID 10), 숫자 85를 보여 줄 Output Number(ID 11), 두 오브젝트가 함께 쓰는 글꼴 설정 Font Attributes(ID 30)다.

![오브젝트 풀 계층 구조: Working Set(ID 0) → Data Mask(ID 1) → Output String(ID 10)·Output Number(ID 11) → Font Attributes(ID 30)](/images/study-isobus/16-object-pool-tree-light.png)
![오브젝트 풀 계층 구조: Working Set(ID 0) → Data Mask(ID 1) → Output String(ID 10)·Output Number(ID 11) → Font Attributes(ID 30)](/images/study-isobus/16-object-pool-tree-dark.png)

그림에서 Font Attributes가 두 번 그려진 것은 Output String과 Output Number가 같은 오브젝트(ID 30)를 함께 가리킨다는 뜻이다. 실제 풀에는 ID 30이 하나만 있다.

### IOP XML 예시

::: info IOP는 표준 용어가 아니다
ISO 11783-6 표준 문서에는 "IOP"라는 표기가 없다. 표준은 이것을 그냥 <strong>object pool</strong>이라 부르며, `.iop`는 오브젝트 풀을 설계·빌드하는 툴체인이 관례적으로 쓰는 파일 확장자다. 아래 XML도 표준이 정의한 형식이 아니라 툴이 쓰는 중간 표현이며, 실제로 버스에 오르는 것은 이를 변환한 바이너리 레코드다.
:::

아래 XML은 위 다섯 오브젝트를 태그 하나씩으로 적은 것이다. 태그 이름이 오브젝트 타입이고, `id`가 Object ID, 나머지 항목이 속성이다.

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

핵심 줄만 짚는다.

- `workingset`의 `active_mask="1"`: 처음 보여 줄 화면이 Data Mask 1이라는 뜻이다.
- `fontattributes`: 색 0(검정), 크기 6(24×32 픽셀) 글꼴을 정의한다. 색 번호는 VT 표준 팔레트(번호마다 색이 정해진 표)를 따른다.
- `datamask`의 `soft_key_mask="65535"`: 1절의 NULL Object ID다. 이 화면에는 소프트키가 없다.
- `include_object`: 자식 오브젝트와 그 위치다. 위치는 Data Mask 왼쪽 위 모서리를 (0, 0)으로 놓고 센다. Output String 10은 가로 10, 세로 20픽셀 떨어진 곳에, Output Number 11은 가로 130, 세로 20픽셀 떨어진 곳에 놓인다.
- `outputnumber`의 `variable_reference="65535"`: 값을 다른 변수 오브젝트에서 가져오지 않고, 이 오브젝트 안의 `value`를 직접 쓴다는 뜻이다.

### 런타임 데이터 갱신

화면이 뜬 뒤에는 풀을 다시 보내지 않고 바뀐 값만 보낸다. 레고 비유가 맞지 않던 바로 그 부분이다.

화면이 표시된 후, ECU는 실측 온도가 바뀔 때마다 `Change Numeric Value` 명령으로 Output Number의 값을 갱신한다. VT 명령은 ECU→VT 방향 PGN 0xE700(59136)으로 보내고, VT의 응답은 VT→ECU 방향 PGN 0xE600(58880)으로 돌아온다. VT는 별도의 오브젝트 풀 재전송 없이 해당 오브젝트만 업데이트하여 화면에 반영한다. PGN(Parameter Group Number)은 메시지 종류를 가리키는 번호다([9장](/study/isobus/09-j1939-message)).

```
ECU → VT: Change Numeric Value
  Object ID: 0x000B (Output Number ID 11)
  New Value : 92    (92°C로 갱신)
```

이 명령을 받으면 VT는 Object ID 11인 Output Number만 찾아 값을 92로 바꾸고 다시 그린다. 화면의 "85"가 "92"로 바뀐다. 명령의 바이트 배치는 [36장](/study/isobus/36-vt-commands-basics)에서 다룬다.

정리하면, 화면 설계는 오브젝트를 고르고(5개), ID를 붙이고, 부모가 자식의 위치를 정하는 일이다. 화면이 뜬 뒤에는 Object ID를 지정한 명령으로 오브젝트 하나만 바꾼다.

## 6. 오브젝트 레코드를 바이트로 보기

5절의 XML은 사람이 읽기 위한 것이고, 버스에는 바이트가 오른다. 이 절에서는 같은 화면을 바이트로 바꿔 한 바이트씩 읽는다.

2절의 타입 표는 이름과 역할을 보여줄 뿐, 실제로 버스에 오를 때 바이트가 어떻게 배치되는지는 보여주지 않는다. VT 표준이 정한 공통 규칙은 <strong>모든 오브젝트 레코드가 Object ID(2바이트, 리틀엔디언) + Object Type(1바이트) + 타입별 속성</strong> 순으로 이어진다는 것이다. 5절의 "엔진 온도: 85°C" 화면을 이루는 세 오브젝트(Font Attributes, Output String, Output Number)를 실제 바이트로 펼쳐본다.

### 표 읽는 법

- <strong>오프셋</strong>은 레코드 첫 바이트를 0으로 놓고 센 위치다. 33장의 표는 바이트 번호를 1부터 세므로 하나씩 차이가 난다.
- <strong>바이트(hex)</strong>는 16진수 두 자리가 한 바이트다. `1E`는 10진수 30이다.
- 2바이트 이상인 값은 <strong>리틀 엔디언</strong>(little endian)이다. 낮은 자리 바이트가 먼저 온다. `1E 00`은 거꾸로 붙여 0x001E로 읽고, 10진수로 30이다.
- <strong>XML 속성</strong> 칸은 5절 XML의 어느 항목에서 그 값이 왔는지 보여 준다. "태그"는 XML 태그 이름이 곧 타입을 정한다는 뜻이다. "(미지정)"은 XML에 적지 않은 속성이고, "(없음)"은 XML에 대응하는 항목이 아예 없는 바이트다.
- `FF FF`(65535)는 NULL이다. "가리키는 오브젝트 없음"을 뜻한다.

::: info 정확도 표기
아래 표의 값 중 5절 XML에 명시된 속성(width, height, font_attributes, justification, value, font_colour, font_size, font_style 등)은 ISO 11783-6이 정한 레코드 형식을 그대로 적용한 <strong>확정값</strong>이다. XML에 없는 속성(background colour, Options, 일부 Font type)은 "(가정)"으로 표시했고, 실제 툴체인 결과와 다를 수 있다.
:::

### Font Attributes(ID 30): 8바이트

Output String·Output Number가 공유 참조하는 오브젝트부터 본다.

| 오프셋 | 바이트(hex) | 크기 | XML 속성 | 설명 |
|---|---|---|---|---|
| 0 | `1E 00` | 2 | `id="30"` | Object ID = 30, 리틀엔디언 |
| 2 | `17` | 1 | 태그 `fontattributes` | Object Type = 23(0x17) = Font Attributes |
| 3 | `00` | 1 | `font_colour="0"` | 검정 |
| 4 | `06` | 1 | `font_size="6"` | 24×32 픽셀(고정폭 크기 6) |
| 5 | `00` (가정) | 1 | (미지정) | Font type: XML에 없는 속성. 0 = ISO 8859-1(Latin 1)로 가정 |
| 6 | `00` | 1 | `font_style="0"` | 일반 텍스트(Bold·Italic 등 비트 없음) |
| 7 | `00` | 1 | (없음) | Number of macros to follow = 0. 매크로가 없어도 이 바이트는 있다 |

![Font Attributes 레코드 8바이트: 1E 00은 Object ID 30(리틀 엔디언), 17은 타입 23 Font Attributes, 00은 글자 색 0 검정, 06은 글자 크기 6(24×32), 00은 Font type 0(가정), 00은 글자 스타일 없음, 00은 매크로 개수 0](/images/study-isobus/32-font-record-bytes-light.png)
![Font Attributes 레코드 8바이트: 1E 00은 Object ID 30(리틀 엔디언), 17은 타입 23 Font Attributes, 00은 글자 색 0 검정, 06은 글자 크기 6(24×32), 00은 Font type 0(가정), 00은 글자 스타일 없음, 00은 매크로 개수 0](/images/study-isobus/32-font-record-bytes-dark.png)

레코드 전체 `1E 00 17 00 06 00 00 00`을 앞에서부터 따라 읽는다.

1. `1E 00`: Object ID다. 리틀 엔디언이라 뒤의 `00`이 높은 자리, 앞의 `1E`가 낮은 자리다. 0x001E = 30이다.
2. `17`: Object Type이다. 0x17 = 23이고, 2절 표에서 23은 Font Attributes다. 이제 VT는 나머지 바이트를 Font Attributes 규칙대로 읽는다.
3. `00`: 글자 색 0번, 검정이다.
4. `06`: 글자 크기 6번, 24×32 픽셀이다.
5. `00`: Font type(어떤 문자 집합으로 글자를 해석할지) 0번이다. ISO 8859-1(라틴 문자)로 가정했다.
6. `00`: 글자 스타일이다. 굵게, 기울임 같은 비트가 하나도 켜지지 않은 일반 글자다.
7. `00`: 뒤따르는 매크로 개수 0이다. 매크로는 어떤 일이 생겼을 때 VT가 자동으로 실행하는 명령 묶음이다([33장](/study/isobus/33-vt-object-records)). 개수가 0이므로 레코드가 여기서 끝난다.

### Output String(ID 10): 31바이트

글자를 보여 주는 오브젝트다. 앞부분은 Font Attributes와 같은 방식으로 읽히고, 뒤에 길이가 바뀔 수 있는 문자열이 붙는다.

| 오프셋 | 바이트(hex) | 크기 | XML 속성 | 설명 |
|---|---|---|---|---|
| 0 | `0A 00` | 2 | `id="10"` | Object ID = 10 |
| 2 | `0B` | 1 | 태그 `outputstring` | Object Type = 11(0x0B) = Output String |
| 3 | `78 00` | 2 | `width="120"` | 120픽셀 |
| 5 | `1E 00` | 2 | `height="30"` | 30픽셀 |
| 7 | `01` (가정) | 1 | (미지정) | Background colour: Data Mask와 같은 흰색으로 가정 |
| 8 | `1E 00` | 2 | `font_attributes="30"` | Font Attributes ID 30 참조 |
| 10 | `00` (가정) | 1 | (미지정) | Options: 불투명·Auto-Wrap 없음으로 가정 |
| 11 | `FF FF` | 2 | (미지정, 추정) | Variable reference: XML에 없지만 `value`가 직접 있으므로 스펙상 NULL(65535) 확정 |
| 13 | `00` | 1 | `justification="0"` | 좌측 정렬 |
| 14 | `0E 00` | 2 | (계산값) | Length = 14바이트(아래 Value 참고) |
| 16 | `FF FE D4 C5 C4 C9 20 00 28 C6 C4 B3 3A 00` | 14 | `value="엔진 온도:"` | WideString(UTF-16LE): BOM(`FF FE`) + "엔"(U+C5D4)"진"(U+C9C4)" "(U+0020)"온"(U+C628)"도"(U+B3C4)":"(U+003A) |
| 30 | `00` | 1 | (없음) | Number of macros to follow = 0. 가변 길이 Value 뒤에 온다 |

앞에서부터 따라 읽는다.

1. `0A 00` `0B`: Object ID 10, 타입 11(Output String)이다.
2. `78 00` `1E 00`: 폭 0x0078 = 120픽셀, 높이 0x001E = 30픽셀이다.
3. `01`: 배경색 1번(흰색)이다. XML에 없어서 가정한 값이다.
4. `1E 00`: 글꼴은 Font Attributes 30을 쓴다. 이렇게 Object ID를 적어 다른 오브젝트를 가리키는 것을 참조라고 한다.
5. `00`: Options(배경 투명 여부, 자동 줄바꿈 등)다. 가정한 값이다.
6. `FF FF`: 변수 참조가 NULL이다. 문자열을 다른 변수 오브젝트에서 가져오지 않고 이 레코드 안에 직접 담는다.
7. `00`: 왼쪽 정렬이다.
8. `0E 00`: 뒤따르는 문자열의 길이가 0x000E = 14바이트라는 뜻이다. VT는 이 값을 보고 문자열이 어디서 끝나는지 안다.
9. `FF FE` + 12바이트: 문자열 14바이트다. 처음 두 바이트 `FF FE`는 "이 문자열은 WideString"이라는 표시이고, 그 뒤로 2바이트가 한 글자다. 예를 들어 `D4 C5`는 리틀 엔디언이라 0xC5D4로 읽고, 유니코드 U+C5D4는 "엔"이다.
10. `00`: 매크로 개수 0이다. Output String에서는 이 바이트가 문자열 <strong>뒤에</strong> 온다.

`value` 속성이 한글을 담고 있어 8-bit 인코딩(ISO 8859 계열의 8비트 문자 집합)으로는 표현할 수 없다. 그래서 실제 바이너리 변환 시 이 Value는 <strong>WideString</strong>으로 인코딩된다. 첫 2바이트가 `FF FE`(BOM)로 시작하는 것으로 VT가 WideString임을 판별한다(VT 표준의 "첫 2바이트가 FF FE이면 WideString" 규칙). XML 자체에는 이를 나타내는 플래그가 없고, 바이너리 변환 도구가 문자열 내용을 보고 결정한다.

용어를 풀면 이렇다. 8비트 인코딩은 글자 하나를 1바이트로 적는 방식이라 한 문자 집합에 최대 256자만 담는다. 영문 같은 라틴 문자는 담지만 한글은 담지 못한다. WideString은 글자 하나를 2바이트로 적는 문자열이고, 여기서는 UTF-16LE(유니코드 번호를 2바이트 리틀 엔디언으로 적는 방식)를 쓴다. BOM(Byte Order Mark, 바이트 순서 표시)은 문자열 맨 앞의 `FF FE` 두 바이트다. 문자 집합은 [35장](/study/isobus/35-vt-pool-transfer-charset)에서 자세히 다룬다.

### Output Number(ID 11): 29바이트

숫자를 보여 주는 오브젝트다. 숫자는 정수 원시값(raw value)으로 저장하고, 화면에 보일 때 Offset과 Scale로 계산한다.

| 오프셋 | 바이트(hex) | 크기 | XML 속성 | 설명 |
|---|---|---|---|---|
| 0 | `0B 00` | 2 | `id="11"` | Object ID = 11 |
| 2 | `0C` | 1 | 태그 `outputnumber` | Object Type = 12(0x0C) = Output Number |
| 3 | `50 00` | 2 | `width="80"` | 80픽셀 |
| 5 | `1E 00` | 2 | `height="30"` | 30픽셀 |
| 7 | `01` (가정) | 1 | (미지정) | Background colour: 위와 동일하게 가정 |
| 8 | `1E 00` | 2 | `font_attributes="30"` | Font Attributes ID 30 참조 |
| 10 | `00` (가정) | 1 | (미지정) | Options: 불투명·선행0 없음·0도 표시·반올림으로 가정 |
| 11 | `FF FF` | 2 | `variable_reference="65535"` | NULL: Value 속성 직접 사용 |
| 13 | `55 00 00 00` | 4 | `value="85"` | 원시값 85(unsigned 32bit, LE) |
| 17 | `00 00 00 00` | 4 | `offset="0"` | Offset(signed 32bit) |
| 21 | `00 00 80 3F` | 4 | `scale="1.0"` | Scale: IEEE-754 단정밀도 부동소수 1.0(LE) |
| 25 | `00` | 1 | `number_of_decimals="0"` | 소수점 이하 0자리 |
| 26 | `01` (가정) | 1 | `format="true"` | Format(0=고정소수/1=지수 표기): XML의 `true` 표기가 이 0/1 enum과 정확히 어떻게 대응하는지 이 챕터 범위에서는 확정할 수 없어 1로 가정 |
| 27 | `00` | 1 | `justification="0"` | 좌측 정렬 |
| 28 | `00` | 1 | (없음) | Number of macros to follow = 0 |

Output String과 다른 부분만 따라 읽는다.

1. `55 00 00 00`: 원시값이다. 4바이트 리틀 엔디언이라 0x00000055 = 85다. unsigned는 음수가 없는 정수라는 뜻이다.
2. `00 00 00 00`: Offset 0이다. signed는 음수도 담는 정수라는 뜻이다.
3. `00 00 80 3F`: Scale이다. IEEE-754 단정밀도 부동소수는 소수를 4바이트로 담는 표준 형식이다. 리틀 엔디언이라 거꾸로 붙이면 0x3F800000이고, 이 비트 배치가 1.0이다.
4. `00`: 소수점 아래 0자리로 보여 준다.

표시값 계산식 `(value + Offset) × Scale = (85 + 0) × 1.0 = 85`로, XML 주석의 "초기값 85°C"와 일치한다.

정리하면, 세 레코드 모두 "Object ID 2바이트 + 타입 1바이트"로 시작하고, 그 뒤는 타입이 정한 순서대로 속성이 이어진다. XML에 적지 않은 속성도 바이너리에는 반드시 자리가 있다.

<small>근거: ISO 11783-6 4.6.19.7, B.9.2, B.9.3, B.14.2, Table K.1</small>

## 7. 풀 전체 크기와 TP·ETP

레코드 크기를 알면 풀 전체 크기를 셀 수 있다. 이 크기가 4절의 Get Memory에 들어가는 값이고, TP와 ETP 중 무엇으로 보낼지도 이 크기로 정해진다.

### Object Pool Transfer에 실리는 순서

Object Pool Transfer 메시지는 <strong>Byte 1 = 함수코드 `0x11`</strong>(=17) 뒤에 오브젝트 레코드가 그대로 이어지는 구조다. 함수 코드는 VT 메시지의 첫 바이트로, 이 메시지가 무슨 일을 하는지 알려 주는 번호다. 5절 화면의 풀 전체를 구성하면 다음과 같다.

| 순서 | 오브젝트 | 바이트 수 | 비고 |
|---|---|---|---|
| 1 | Working Set(ID 0) | 10 | designator 오브젝트 0개로 단순화한 크기. VT 표준은 Working Set이 <strong>Soft Key designator 크기의 식별용 오브젝트를 최소 1개</strong> 포함해야 한다고 규정하지만 5절 XML은 이를 생략했으므로, 실제 툴체인이 만드는 정확한 바이트 수는 이보다 클 수 있다 |
| 2 | Data Mask(ID 1) | 20 | 자식 오브젝트 2개(Output String 10, Output Number 11) 포함 |
| 3 | Font Attributes(ID 30) | 8 | 위 표 참고 |
| 4 | Output String(ID 10) | 31 | 위 표 참고 |
| 5 | Output Number(ID 11) | 29 | 위 표 참고 |
| 합계 | | <strong>98</strong> | Object Pool Transfer message 전체 길이 = 1(함수코드) + 98 = 99바이트 |

Working Set 행의 식별용 오브젝트는 VT가 이 작업기를 알아보게 보여 주는 작은 그림이나 글자다. 소프트키 하나(Soft Key designator) 크기 안에 들어가야 한다.

이 98바이트가 [29장](/study/isobus/29-vt-basics)의 VT 연결 타임라인에서 Get Memory 메시지에 그대로 들어가는 Memory Required 값이다.

### ETP가 필요해지는 지점

4절에서 "1785바이트 초과 시 ETP"라고 했다. 이번 예제 풀은 98바이트라 TP 한 세션이면 충분하다. 하지만 오브젝트 5개의 평균 크기가 98 ÷ 5 ≈ 19.6바이트인 것을 기준으로 보면, <strong>1785 ÷ 19.6 ≈ 91개</strong>다. 이 정도 크기의 오브젝트 90여 개만 모여도 ETP 임계값을 넘는다. 실제 작업기 화면은 여러 Data Mask에 버튼·라벨·컨테이너가 수십~수백 개씩 들어가는 경우가 흔하고, Picture Graphic처럼 원시 비트맵 데이터를 통째로 담는 오브젝트(2절 "Picture Graphic")가 하나만 있어도 크기가 급격히 커진다. 풀이 조금만 커져도 ETP 경로를 타게 되는 이유다.

아래 코드는 6절 표의 바이트를 파이썬으로 다시 만들어 크기를 확인한다. 실행하면 `assert`가 모두 통과하고 마지막 줄에 풀 전체 크기 98바이트가 찍힌다.

::: details 파이썬으로 바이트 구성 검산해 보기
```python
def le(v, n):
    return v.to_bytes(n, "little", signed=False)


# Font Attributes(ID 30)
font_attr = le(30, 2) + bytes([23, 0, 6, 0, 0, 0])
assert font_attr.hex(" ").upper() == "1E 00 17 00 06 00 00 00"
assert len(font_attr) == 8

# Output String(ID 10): Value는 WideString(BOM + UTF-16LE)
text = "엔진 온도:"
value = b"\xFF\xFE" + text.encode("utf-16-le")
assert value.hex(" ").upper() == "FF FE D4 C5 C4 C9 20 00 28 C6 C4 B3 3A 00"
assert len(value) == 14

output_string = (
    le(10, 2) + bytes([11])
    + le(120, 2) + le(30, 2)
    + bytes([0x01])          # background colour(가정)
    + le(30, 2)               # font attributes
    + bytes([0x00])           # options(가정)
    + le(0xFFFF, 2)            # variable reference(NULL)
    + bytes([0])               # justification
    + le(len(value), 2)
    + value
    + bytes([0])               # number of macros to follow
)
assert len(output_string) == 31

# Output Number(ID 11)
import struct
scale = struct.pack("<f", 1.0)
assert scale.hex(" ").upper() == "00 00 80 3F"

output_number = (
    le(11, 2) + bytes([12])
    + le(80, 2) + le(30, 2)
    + bytes([0x01])            # background colour(가정)
    + le(30, 2)
    + bytes([0x00])            # options(가정)
    + le(0xFFFF, 2)
    + le(85, 4)                 # value
    + (0).to_bytes(4, "little", signed=True)  # offset
    + scale
    + bytes([0, 1, 0])          # decimals, format(가정=1), justification
    + bytes([0])                # number of macros to follow
)
assert len(output_number) == 29

pool_size = len(font_attr) + len(output_string) + len(output_number) + 10 + 20  # + Working Set(10) + Data Mask(20)
assert pool_size == 98
print("풀 전체 크기:", pool_size, "바이트, Get Memory의 Memory Required와 일치")
```
:::

정리하면, 풀 크기는 레코드 크기의 합이고 Object Pool Transfer 메시지는 그 앞에 함수 코드 1바이트가 붙을 뿐이다. 풀이 1785바이트를 넘으면 ETP로 보낸다.

<small>근거: ISO 11783-6 B.1, C.2.3</small>

::: tip 핵심 정리
- 오브젝트 풀은 작업기 화면을 이루는 부품(오브젝트)을 모두 모은 바이너리 묶음이다. 오브젝트마다 Object ID, 타입 번호, 속성이 있다.
- 타입 번호는 0~48이 표준 오브젝트, 240~254가 제조사 정의 오브젝트이고, 49~239와 255는 예약이다.
- 오브젝트는 Working Set을 뿌리로 Data Mask, 자식 오브젝트, 속성 오브젝트 순으로 이어진다. 속성 오브젝트는 여러 오브젝트가 함께 쓸 수 있다.
- 풀은 Get Memory로 공간을 확인한 뒤 TP/ETP(1785바이트 초과 시 ETP)로 보내고, End of Object Pool로 결과를 받는다. Store/Load Version으로 재전송 시간을 줄인다.
- 레코드는 Object ID(2바이트, 리틀 엔디언) + 타입(1바이트) + 속성 순이다. XML에 없는 속성도 바이너리에는 있고, 한글 문자열은 WideString(BOM + UTF-16LE)으로 바뀐다.
- 화면이 뜬 뒤에는 Change Numeric Value 같은 명령으로 오브젝트 하나만 바꾼다.
:::

::: details 확인 문제
1. VT는 어떤 작업기가 연결될지 모르는데도 여러 회사의 작업기 화면을 그릴 수 있다. 무엇 덕분인가?
2. 레코드 `1E 00 17 00 06 00 00 00`의 Object ID와 오브젝트 타입은 무엇인가?
3. VT가 같은 버전의 풀을 이미 저장하고 있을 때와 그렇지 않을 때, 전송 과정은 어떻게 다른가?
4. 타입 번호 200과 255에 해당하는 오브젝트는 무엇인가?
5. 5절 화면의 글자를 영문 "TEMP:"로 바꾸면 Output String의 Value는 어떻게 인코딩될 수 있는가? 한글일 때와 무엇이 다른가?

**답 가이드**
1. 작업기가 자기 화면의 설계도인 오브젝트 풀을 갖고 있다가 연결할 때 VT에 보내기 때문이다. VT는 풀에 적힌 오브젝트와 속성대로 화면을 그린다.
2. `1E 00`은 리틀 엔디언이라 0x001E = 30이 Object ID다. `17` = 23은 Font Attributes 타입이다.
3. 저장본이 있으면 Get Memory 뒤에 Load Version과 그 응답만으로 끝난다. 없으면 Object Pool Transfer(TP/ETP)로 풀을 보내고 End of Object Pool로 끝을 알린 뒤 End of Object Pool Response로 결과를 받는다. 이어서 Store Version으로 저장해 두면 다음 연결부터는 Load Version을 쓸 수 있다.
4. 둘 다 없다. 200은 49~239 예약 범위에 들고, 255도 예약 번호다. 어떤 오브젝트에도 배정되지 않았다.
5. 영문은 8비트 문자 집합으로 담을 수 있으므로 글자 하나가 1바이트인 8비트 문자열로 인코딩될 수 있다. 이때는 앞에 `FF FE`(BOM)가 붙지 않는다. 한글은 8비트 문자 집합에 없어서 `FF FE`로 시작하는 WideString(글자당 2바이트)이 되어야 한다. 어느 쪽으로 할지는 XML이 아니라 바이너리 변환 도구가 문자열 내용을 보고 정한다.
:::

## 다음 챕터

- 다음: [33장 오브젝트 레코드: 공통 구조와 자주 쓰는 오브젝트](/study/isobus/33-vt-object-records)
