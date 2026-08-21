---
title: "표준 정리: Part 6 — Virtual terminal"
description: "ISO 11783-6(Virtual terminal) — VT 동작 원리, 오브젝트 정의, 명령 메시지, Auxiliary control을 정리한 표준 요약이다."
date: 2026-08-21
tags: [ISOBUS, ISO11783, 표준정리]
---

# ISO 11783-6: Virtual terminal 정리

::: info 이 문서에 대해
ISO 11783-6 표준 원문을 학습 목적으로 재구성한 <strong>비공식 요약·해설</strong>이다. 규범적 판단이 필요할 때는 반드시 원문 표준을 확인해야 한다.
:::

## 개요

ISO 11783-6:2018(4판)은 농업·임업용 트랙터와 작업기(implement)가 공유하는 범용 조작 단말인 <strong>Virtual Terminal(VT)</strong>을 정의한다. ISO 11783 시리즈는 ISO 11898(CAN) 기반의 직렬 제어·통신 네트워크 규격이며, Part 6는 그중 운전자 인터페이스 계층을 담당한다. VT 사양의 뿌리는 DIN 9684-4이고, SAE J1939와 공동 개발된 부분 위에 올라가 있다.

4판(2018)은 3판(2014)을 대체하며 <strong>VT version 6</strong> 요구사항을 새로 규정한다. 주요 변경점은 다음과 같다.

- 기존 VT 오브젝트·커맨드 동작의 명확화
- Select Active Working Set 커맨드: 한 Working Set이 협력 관계의 다른 Working Set에게 active mask 제어권을 넘길 수 있게 됨
- 신규 오브젝트 추가: Colour Palette object, Graphic Data object, Scaled Graphic object, Working Set Special Controls object

문서 전반의 표기 관례로, 특정 정의를 가진 오브젝트·커맨드 용어는 각 단어의 첫 글자를 대문자로 쓴다(예: Output Linear Bar Graph object, Change Numeric Value command).

### 문서 구성

본문(1~4절)이 VT의 동작 원리를 정의하고, 세부 데이터 정의는 모두 normative annex로 분리되어 있다.

| Annex | 내용 |
| --- | --- |
| A | 오브젝트·이벤트·컬러·커맨드 코드 |
| B | 오브젝트 정의(속성 테이블) |
| C | Object transport protocol |
| D | Technical data messages |
| E | 비휘발성 메모리 조작 커맨드 |
| F | Command·Macro 메시지 |
| G | Status 메시지 |
| H | Activation 메시지 |
| I | 기타 메시지 |
| J | Auxiliary control |
| K | Character sets |

## 1~2. 적용 범위와 인용 규격

Part 6는 트랙터와 작업기가 공용으로 쓸 수 있는 범용 VT를 기술한다. 인용 규격은 ISO 11783-3(Data link layer), ISO 11783-5(Network management), ISO 11783-7(Implement messages application layer), ISO 15077(조작 장치 요구사항)이다.

## 3. 용어 정의

실무에서 자주 등장하는 핵심 용어만 추린다.

| 용어 | 정의 |
| --- | --- |
| auxiliary input unit | 공용 Auxiliary Control을 제공하는 자율 CF. 별도 ECU나 VT 내부에 물리적으로 위치할 수 있음 |
| object pool | 하나의 작업기 또는 하나의 Working Set의 운전자 인터페이스를 완전히 정의하는 오브젝트 집합. VT 전체 화면 정의는 Working Set별 object pool 하나씩으로 구성됨 |
| Object ID | object pool 내에서 오브젝트를 식별하는 숫자 값. 범위 0~FFFF₁₆(65535), 65535는 NULL Object ID |
| attribute ID (AID) | 오브젝트의 특정 속성을 참조하는 값. 범위 0~FF₁₆, 255는 NULL_AID |
| char | 크기 1바이트의 단일 문자(주로 ISO 8859 계열) |
| character | 인코딩에 따라 크기가 달라지는 단일 문자소 |
| code plane | 65536개 문자 코드의 그룹. Unicode/ISO 10646은 plane 0~16으로 구성 |
| open input object | 포커스를 가지며 운전자 입력이 열려 있는 입력 오브젝트 상태(= data input) |
| selected input object | 포커스는 있으나 입력은 열리지 않은 상태(= has focus) |
| surrogate pair | 16bit high/low 쌍으로 구성되는 32bit 문자 코드(UTF-16, code plane 1~16) |
| WideChar | 리틀 엔디안 2바이트 단일 문자 |
| WideString | WideChar 문자열. 항상 byte order mark FEFF₁₆로 시작 |
| 8-bit string | char로 구성된 가변 길이 문자열 |
| VT Number | 운전자에게 각 VT를 유일하게 식별시키는 번호 |
| User-Layout Data Mask | VT가 제어하되 운전자가 배치(layout)하는 특수 Data Mask |
| Window Cell | User-Layout Data Mask 격자의 직사각형 표시 셀 |
| Window Mask object | 인접한 Window Cell 하나 이상으로 구성되는 직사각형 표시 영역 |
| User-Layout Soft Key Mask | VT가 제어하되 운전자가 배치하는 Soft Key Mask |
| Key Cell | User-Layout Key Mask에서 Soft Key designator 크기의 셀 |
| Key Group object | Key Cell 하나 이상 영역에 Key object들을 묶는 오브젝트 |
| Non-VT Screen / Non-VT Area | VT 애플리케이션이 아니거나 VT가 배치를 제어하지 않는 화면/영역(예: 차량 정보 표시) |
| referenced WS | 다른 object pool이 External Object Pointer object로 참조해 보여주는 오브젝트를 가진 Working Set |
| referencing WS | External Object Pointer object로 다른 pool의 오브젝트를 보여주는 Working Set |
| Functionally Identical WS | Self Configurable, Instance 필드, Identity Number를 제외한 NAME이 완전히 일치하는 Working Set들 |
| Line End | 다음 문자를 font height만큼 아래·행의 맨 왼쪽에 위치시키는 커서 제어 |
| Model Identification Code | Auxiliary Input Unit의 모델·버전을 정의하는 제조사 고유 코드. 런타임에는 불변, 비호환 신형이 나올 때 개정 |

## 4. 기술 요구사항

### 4.1 VT 개요

VT는 그래픽 디스플레이와 입력 수단을 갖춘 ECU 내의 control function(CF)이다. ISO 11783 네트워크에 연결되어, 작업기(또는 작업기 그룹)를 대표하는 <strong>Working Set</strong>이 운전자와 상호작용할 수 있는 수단을 제공한다. 동작 모델의 핵심은 다음과 같다.

- Working Set은 자신의 표시용 오브젝트를 VT 내부 저장소에 미리 적재(업로드)해 두고, 필요할 때 표시를 요청한다
- 운전자 입력은 반대 방향으로 Working Set에 신호로 전달된다
- 화면 전환은 Change Active Mask 커맨드 한 번으로 이뤄지므로 런타임 버스 트래픽이 최소화된다

표준은 서로 다른 제조사의 VT와 Working Set이 호환되도록 <strong>기능(function)</strong>을 정의하되 <strong>디자인</strong>은 제약하지 않는다. 물리적 배치·부품·처리 성능·화면 크기·해상도·방향(landscape/portrait)·터치스크린 여부는 모두 VT 설계자 재량이다. 이를 위해 요구사항은 오브젝트 지향으로 조직되어 각 오브젝트의 속성과 동작이 명확히 정의된다.

VT 화면은 개념적으로 다음 영역으로 나뉜다(Figure 1).

| 영역 | 설명 |
| --- | --- |
| Data Mask area | Data Mask·Alarm Mask가 표시되는 정사각형 영역 |
| Soft Key Mask area | Soft Key designator(라벨)들이 표시되는 영역 |
| physical Soft Key | designator와 짝을 이루는 실제 키(터치스크린이면 화면상 버튼) |

VT는 반드시 픽셀 주소 지정이 가능한(pixel-addressable) 그래픽 디스플레이를 가져야 한다.

#### 4.1.1 VT version 6 요구사항

VT의 특성은 Annex D의 Technical data message로 조회할 수 있다. VT version 6가 강제하는 요구사항은 다음과 같다.

| 항목 | 요구사항 |
| --- | --- |
| Physical Soft Keys | 최소 60 × 60 픽셀(정사각형 권장) |
| Text Fonts | 모든 small/large font 크기, 모든 font style 지원 |
| Graphic Type | 최소 256색. Colour Palette·Graphic Data object 지원을 위해 16bit 이상 색상 권장(예: 24bit PNG를 16bit로 다운스케일 표시 가능) |
| Data Mask Size | 최소 480 × 480 픽셀 |
| Window Mask object | 완전 파싱 필수, 표시(presentation)는 선택 |
| Key Group object | 완전 파싱 필수, 표시는 선택 |
| Graphics Context object | 완전 표시 지원 필수 |

### 4.2 운전자 입력·제어 수단

VT는 다섯 가지 입력·제어 수단을 제공해야 한다(Figure 2).

| 수단 | 역할 | 비고 |
| --- | --- | --- |
| Soft | 소프트웨어로 라벨(designator)이 바뀌는 키. 표시 중인 Soft Key Mask에 따라 기능이 달라짐 | Soft Key와 designator의 연관이 운전자에게 명확해야 함 |
| Navigation | active Data Mask 안에서 입력 필드·Button을 선택하는 수단 | 키를 쓰더라도 키 자체의 활성화 정보는 Working Set에 전송되지 않음(VT 고유 영역) |
| Data Input | active Data Mask의 입력 필드에서 값을 입력·편집하는 수단 | 입력 필드에 유효한 모든 숫자·문자 시퀀스를 입력할 수 있어야 함 |
| Control | Working Set 간 전환 + 알람 ACK | 두 수단 모두 필수. WS 선택 수단은 세 개의 원형 화살표 또는 유사 그래픽으로 표시 권장. ACK만 key activation 정보를 WS로 전송 |
| Auxiliary Input | Auxiliary Function에 할당된 Auxiliary Control로 WS에 입력 커맨드를 전달(Annex J) | |

<strong>Data Input의 두 방식</strong>

- <strong>Editing</strong> — 새 값을 VT 고유의 방식으로 조합해 입력한다. 조합 중에는 변경이 Working Set에 전달되지 않는다. ENTER(입력 완료·새 값 전달)와 ESC(입력 중단) 수단이 반드시 제공되어야 하며, 상시 키이거나 입력 중에만 나타나는 키여도 된다. 운전자가 ESC를 누르면 VT는 VT ESC message를, Working Set이 ESC command를 보내면 그 응답을 전송한다.
- <strong>Real-time editing</strong> — Input Number·Input List object가 포커스를 갖고 열린 상태에서 값 변경이 주기적으로 Working Set에 전달된다. VT Change Numeric Value message는 <strong>5 Hz</strong> 업데이트 레이트로 제한된다. 전송된 각 값 변경은 ENTER가 눌린 것과 같은 완결 트랜잭션이며 ESC로 되돌릴 수 없다. 값 증분이 균일할 필요는 없으나 어떤 값이든 설정 가능해야 한다(빠른 스크롤 + 미세 조정 조합 허용). real-time editing 중 ESC가 활성화되면 VT는 화면 값이 마지막으로 WS에 보낸 값과 같도록 보장해야 하고, 동기화를 위해 ESC 응답 전에 최종 값을 보낼 수 있다. real-time editing은 ISO 15077의 조작 장치 요구사항을 만족해야 한다.

data input 동작 중에도 VT Status message는 active Working Set과 입력 대상 오브젝트가 속한 active mask를 계속 가리킨다.

### 4.3 음향 알람

VT는 음향 알람을 제공해야 한다. 단순 on/off 부저여도 되고, 주파수·음량 가변 컴포넌트여도 된다(지원 여부는 Annex D.9로 보고).

### 4.4 좌표계

- 위치·크기는 별도 언급이 없는 한 항상 <strong>물리 픽셀</strong> 단위다.
- 2차원 (x, y) 평면을 쓰며 x는 왼쪽→오른쪽, y는 위→아래로 증가한다.
- 좌표는 <strong>부호 있는 값</strong>이다.
- 모든 오브젝트 좌표계의 원점 (0, 0)은 <strong>부모 오브젝트의 좌상단</strong>이다.

### 4.5 표시 영역

#### 4.5.2 Data Mask 영역

- VT는 Data Mask·Alarm Mask 표시용 영역을 반드시 예약해야 한다(= Data Mask area).
- VT마다 물리적 방향이 달라도 올바르게 표시되도록 Data Mask는 <strong>정사각형 종횡비</strong>를 엄격히 강제한다.
- 최소 크기는 200 × 200 픽셀, <strong>VT version 6 이상은 480 × 480</strong>. 그 이상 어떤 정사각형 해상도든 허용(240, 320, 480, 600, 800, 1024 등).
- 이 요구는 사용 가능한 Data Mask 영역에 대한 것이지 물리 디스플레이 해상도·크기를 제한하지 않는다. 남는 화면 영역은 차량 데이터, VT 통계 등 제조사 고유 정보 표시에 활용이 권장된다.

#### 4.5.3 Soft Key Mask 영역과 Soft Key designator

Soft Key 라벨 영역(Soft Key Mask area)은 Data Mask 영역과 분리해 예약해야 하며 Data Mask 영역의 일부여서는 안 된다(인접하거나 물리적으로 떨어져 있어도 된다). 각 Soft Key는 라벨 표시 영역인 <strong>Soft Key designator</strong>를 갖는다.

- designator 최소 크기: 60 × 32 픽셀(화면 방향 무관). <strong>VT version 6 이상은 60 × 60</strong>.
- designator에는 텍스트·그래픽 또는 둘 다 넣을 수 있다.
- VT는 개별 designator 사이를 시각적으로 명확히 구분해야 한다(예: 1픽셀 선). 구분선은 designator 영역 밖에 그리는 것이 원칙이고, 최소 크기 확보가 불가능할 때만 designator 경계 위에 그리는 것이 허용된다.

<strong>Soft Key 3분류와 개수 관계</strong>: Navigation Soft Keys < Physical Soft Keys ≤ Virtual Soft Keys.

| 구분 | 정의 | 요구사항 |
| --- | --- | --- |
| Physical Soft Keys | VT가 active Working Set에 상시 제공하는 키 수. 물리 버튼일 필요는 없고 터치스크린 상 버튼도 가능 | VT v4 이상: 최소 6개. v3 이하: 개수 요구 없음 |
| Virtual Soft Keys | Working Set의 Data Mask마다 VT가 지원하는 Soft Key 수 | v4 이상: 정확히 64개/Soft Key Mask. v3 이하: 최대 64개, 최소한 보고한 physical 수만큼 지원 |
| Navigation Soft Keys | Soft Key 간 탐색(페이징)에 할당 가능한 physical Soft Key 수 | physical 수보다 적어야 함. physical Soft Key를 쓰지 않는 별도 탐색 수단이 있으면 0으로 보고 |

<strong>물리 Soft Key 번호 배치 규칙</strong>

- 세로 배치: 키 1은 우측 최상단, 키 2는 그 아래. 첫 열이 차면 다음 열은 왼쪽으로 이어진다.
- 가로 배치: 키 1은 상단 행 맨 왼쪽, 키 2는 그 오른쪽. 첫 행이 차면 다음 행은 아래로 이어진다.
- 명확한 가로/세로 배치가 없으면(예: 터치스크린 매트릭스) 세로 배치 규칙을 따른다.

<strong>Soft Key 탐색(페이징)</strong>

- Soft Key Mask의 키 수 ≤ physical Soft Key 수이면: 모든 키가 physical Soft Key로 접근 가능해야 하고 VT는 탐색 수단을 제공하지 않아야 한다.
- 키 수가 더 많으면: VT는 <strong>스크롤이 아닌 그룹 단위 페이징</strong>으로 탐색을 제공해야 한다. "group" = physical Soft Keys 수 − navigation Soft Keys 수. navigation 키는 모든 페이지에서 같은 물리 위치를 차지해야 한다(특정 페이지에서 비활성화는 가능, 제거는 불가). 마지막 페이지는 다 못 채울 수 있으며 남는 designator는 사용하지 않는다.
- Soft Key 목록에서 NULL Object ID를 가리키는 Pointer는 Soft Key 위치를 예약(빈 자리 유지)한다. 단, 목록 끝의 NULL Pointer는 자리를 예약하지 않고 페이징 계산에서도 제외된다.

### 4.6 동작(Behaviour)

#### 4.6.1 Object pool

한 Working Set의 운전자 인터페이스 정의 전체가 오브젝트 집합, 즉 <strong>object pool</strong>이다.

- 오브젝트 타입·이벤트·네트워크 커맨드 요약은 Annex A, 오브젝트 상세 정의는 Annex B·J에 있다.
- Working Set이 pool 내 각 오브젝트에 유일한 Object ID를 부여한다. ID는 한 Working Set의 pool 안에서만 유일하면 되고, Working Set 간에는 중복될 수 있다.
- pool은 초기화 시 Annex C의 절차(object transport protocol)로 VT에 전송된다.
- VT는 pool을 수정 가능한 메모리에 저장할 수 있어야 하며, 버전 라벨이 다르면 한 Working Set의 pool 여러 개를 비휘발성 메모리에 저장할 수 있다(예: 언어만 다른 pool들).
- 오브젝트는 화면의 mask에서 활성화되기 전에 완전히 기술되어 있어야 한다.
- pool이 하나도 로드되지 않았을 때의 VT 동작은 제조사 고유 사항이다.

<strong>NULL Object ID</strong>: FFFF₁₆(65535)는 NULL Object ID로 예약된다. 그리기 문맥에서 NULL Object ID는 "해당 오브젝트에 대해 아무것도 그리지 않음"을 의미한다.

<strong>오브젝트 처리(트리 순회)</strong>

- 부모 오브젝트에 나열된 자식 오브젝트가 다시 자식을 가질 수 있어 pool은 트리 계층을 이룬다. 처리 순서는 항상 부모에 나열된 순서대로 <strong>depth-first</strong>다(자식 참조를 만나면 자식을 끝까지 처리한 뒤 부모로 복귀).
- VT version 5 이상은 최소 <strong>계층 깊이 30</strong>을 지원해야 한다(v4 이하는 미규정).
- 깊이 계산은 Data Mask, Alarm Mask, Window Mask, Soft Key Mask, Key Group object에서 시작해 자식으로 내려갈 때마다 1씩 증가한다. Pointer 오브젝트가 참조하는 오브젝트도 자식으로 센다.
- 포함된(contained) 자식만 계층 수에 포함된다. 속성으로 참조만 되는 오브젝트(예: Working Set object가 Data Mask를 속성으로 참조)는 세지 않는다.

#### 4.6.2 Working Set

Working Set Master가 공급한 object pool은 그 Working Set의 모든 멤버와 연관된다. 이로써 Working Set을 구성하는 여러 CF의 오브젝트 정보가 하나의 공통 pool로 제시된다.

- Working Set마다 CF 하나가 <strong>Working Set Master</strong>로 지정된다. Master는 통신 조정자로서 VT 사용권을 확보하고 초기 object pool 정의를 제공하며, 멤버들의 NAME을 알리는 Working Set message를 보낸다(정의는 ISO 11783-7).
- Working Set Member가 Master 전용 커맨드를 보내거나, Working Set 멤버로 식별되지 않은 CF가 Working Set 전용 커맨드를 보내면 VT는 Acknowledgement:NACK로 응답한다(ISO 11783-3).
- 멤버 식별과 pool 로드가 끝나면 런타임에는 어느 멤버든 오브젝트 데이터 제공·속성 변경이 가능하다.
- 운전자가 입력 필드에 넣은 데이터는 항상 <strong>Working Set Master에게</strong> 전송된다.
- VT 자신은 Working Set Member를 가질 수 없고 Working Set Master/Member 메시지를 전송해서는 안 된다.

<strong>VT Response 메시지의 수신자(Table 1)</strong> — 이 문서의 VT Response 처리 규정은 "응답은 WS Master에게만" 이라는 ISO 11783-1 규정보다 우선한다.

| 구성 | WS Version | VT Version | 동작 |
| --- | --- | --- | --- |
| 1 | 3 이하 | 3 이하 | 모든 커맨드 응답을 WS Master에게 전송 |
| 2 | 3 이하 | 4 이상 | 모든 커맨드 응답을 WS Master에게 전송 |
| 3 | 4 이상 | 3 이하 | 모든 커맨드 응답을 WS Master에게 전송 |
| 4 | 4 이상 | 4 이상 | 응답을 <strong>커맨드 발신자(originator)</strong>에게 전송 |

- 구성 1~3: Member는 자기 커맨드와 응답을 짝짓기 위해 VT→WS Master의 destination specific 메시지를 모두 모니터링해야 한다. Master는 멤버가 유발한 unsolicited 응답을 받게 되며 자신이 보낸 메시지와 정확히 짝지을 수 없다.
- 구성 4: 응답이 발신 노드로 직접 가므로 Transport Protocol 경유 응답(예: Get Supported WideChars response)이 가능해지고, Master는 unsolicited 응답을 더 받지 않으며 Member의 모니터링 의무도 없어진다.

<strong>하위 호환</strong>: Working Set은 낮은 버전 VT에 높은 버전 메시지를 보내서는 안 된다(예: version 4 커맨드를 version 2 VT로). 이때 VT 동작은 예측 불가로 간주된다(NACK 응답 또는 무시 등 설계마다 다름). 연결된 VT가 Working Set의 기능 요구를 지원하지 못하면(필요 기능 미지원, Data Mask 크기 부족 등) Working Set은 최소 호환 pool을 보내 기능 비호환을 운전자에게 알린다. 반대로 VT도 낮은 버전 Working Set에 높은 버전 메시지(예: version 4 이벤트)를 보내서는 안 된다. VT version 5 이상의 VT·Working Set은 VT Unsupported VT Function message / Unsupported VT Function message를 지원해야 하며, 이로써 미지원 기능에 대한 응답이 예측 가능해진다(v4 이하 설계도 구현 가능).

#### 4.6.3 시각적으로 유사한 다수의 Working Set

같은 제조사의 시각적으로 유사한 Working Set이 한 네트워크에 여럿 들어오면(예: 같은 제조사 살포기 2대, 유사 Auxiliary Input unit 2대 이상) NAME의 <strong>Instance 필드</strong>로 각 인스턴스를 위치와 상관지어 유일하게 식별해야 한다. 일관된 구성이 되도록 Instance는 왼쪽→오른쪽, 앞→뒤, 아래→위 순으로 낮은 값부터 배치하는 것이 권장된다.

제조사는 작업 구성을 확립할 수단을 제공해야 하며, 방법은 다음 중 하나 이상(또는 여기 명시되지 않은 다른 수단)이다.

- Instance 기반으로 위치 파악: 유닛 라벨에 Instance 표기, 또는 하네스 배선이 위치에 따라 Instance를 자동 설정
- 위치 기반으로 Instance 설정: 유닛의 Instance 스위치, Data Mask 상의 Instance 설정 화면, 서비스 툴의 commanded name message(ISO 11783-5)

#### 4.6.4 표시용 Working Set 번호

유사한 Working Set이 여럿 있으면 Working Set은 자기 working set 번호를 <strong>Working Set object</strong>에 표시해야 하고, 보이는 mask들에도 표시하는 것이 권장된다. 번호는 제조사가 정의하되 Function Instance, Device Class Instance, ECU Instance 등과 연관 짓는 것이 권장되며(예: 번호 = Function Instance + 1), 같은 제조사의 유사 장비는 모두 같은 규칙을 적용해야 한다.

#### 4.6.5 언어·형식·측정 단위 선택

<strong>VT 측 의무</strong>

- 언어 설정이 없거나 TECU 변경을 감지하면 트랙터 ECU에 Language command를 질의할 수 있다
- ISO 11783-7에 정의된 표준 언어·형식·단위 메시지("standard setups")를 전송해야 한다
- 지원 언어의 <strong>superset 목록</strong>을 구성해 운전자에게 제시해야 한다. superset = 모든 Working Set이 VT에 알려온 언어 + VT가 지원하는 관련 언어. VT가 지원하는 언어가 훨씬 많으면 무관한 언어는 생략 가능
- Working Set 연결 해제 시 더 이상 필요 없는 언어를 목록에서 줄일 수 있다. superset 목록은 비휘발성 메모리에 저장해서는 안 된다
- 운전자가 superset 목록을 보고 선택할 수단을 제공해야 하며, VT 자신이 그 언어를 지원하지 않으면 적절한(또는 기본) 언어로 전환하는 고유 방법을 제공해야 한다
- 형식(시간·날짜 등)과 측정 단위 선택 수단도 제공해야 한다. 전원 인가 시와 변경 시마다 운전자 선택값을 보고해야 한다 — Working Set은 이 메시지로 자기 pool을 선택 언어에 맞게 수정한다(문자열 갱신, 단위 선택, 오프셋·스케일 변경 등)
- standard setups는 비휘발성 저장소에 저장하고 초기화 시 복원해야 한다
- 글로벌 주소 및 자기 앞으로 온 ISO 11783-7 Language Command 요청에 응답해야 한다
- Language Command는 언어 코드(ISO 639-1)와 국가 코드(ISO 3166-1)를 함께 싣는 것이 권장된다

<strong>Working Set 측</strong>

- 초기 지원 언어 목록은 Working Set object로 알린다. Working Set Special Controls object를 보내 이 목록을 대체할 수 있다(언어+국가 코드 포함 가능)
- pool을 게시하는 VT에 맞춰 standard setups를 구성해야 한다(VT마다 다른 setups 게시 가능 — 예: auxiliary 오브젝트는 Function instance 0인 VT에, 나머지는 다른 VT에)
- 선택된 언어·형식·단위를 지원하지 않으면 고유 방법으로 적절한(기본) 설정을 선택해야 한다

#### 4.6.6 초기화

<strong>VT 초기화 순서</strong>

1. ISO 11783-5에 따라 address claim을 완료하고, 글로벌 목적지 주소(255)로 address claim request도 전송한다
2. VT Status message 송신을 시작한다. 리셋·복구의 경우 이전 VT Status message와 최초 VT Status message 사이에 <strong>3초 초과</strong> 간격을 보장해야 한다
3. 운전자가 언어를 선택한 적 없으면 트랙터 ECU에 기본 언어를 요청하거나 운전자와 상호작용해 선택할 수 있다
4. Working Set들의 초기화·object pool 로드를 허용한다

<strong>Working Set 초기화 순서(VT와의 연결)</strong>

1. Auxiliary Function이 있으면 휘발성 메모리의 할당(assignment)을 모두 지운다
2. Master(와 Member들)가 address claim을 완료한다
3. Master는 VT가 VT Status message 송신을 시작할 때까지 기다린다
4. Master는 ISO 11783-7의 메시지로 자신과 멤버들을 VT에 식별시킨다. 초기화 후 멤버 목록을 재구성할 필요가 있으면 Working Set Master/Member 메시지를 다시 보내 멤버를 추가·제거할 수 있다(재초기화 불필요)
5. Master는 Working Set Maintenance message의 주기 전송을 시작한다. 첫 메시지만 initiating 상태(v3에서 도입된 initiating bit, Byte 2 Bit 0)를 표시할 수 있다. VT가 이전에 shutdown을 감지해 Maintenance에 NACK로 응답 중이었다면 다음 두 경우 NACK를 중단한다: (I) 메시지가 VT version 3 이상 준수 표시 + initiating bit 설정 + 직전 maintenance 이후 Working Set Master message 수신, (II) version 2 이하 준수 표시 + Working Set Master message 수신
6. Master는 언어·형식 메시지를 아직 못 받았고 표현이 언어·단위 의존적이면 VT에 요청할 수 있다
7. Master는 VT 능력을 질의하고, 응답에 따라 스케일링·폰트·색상 등에 맞게 pool을 조정해야 한다
8. 자기 pool이 이미 VT 비휘발성 메모리에 있는지 질의할 수 있다
9. object pool 전송을 시작·완료해야 한다. 비휘발성 메모리에서의 전송(Annex E) 또는 Annex C의 프로토콜을 쓴다
10. pool이 지원하는 언어들을 알릴 수 있다

<strong>다중 VT 네트워크에서의 초기화</strong> — Master는 "Move to another VT" 기능을 제공해야 한다(예: "Next VT" Soft Key/Button, Identify VT message와 조합 가능). 동작은 다음과 같다.

1. 네트워크에서 VT를 2대 이상 감지했을 때만 활성화된다
2. 활성화되면 Master는 (I) 안전 상태로 전환(또는 안전 상태가 아니면 기능 활성화 차단), (II) Delete Object Pool command를 보내고 응답 대기, (III) Working Set Maintenance 송신 중단, (IV) 다른 VT와 초기화 시작, (V) 새 VT를 다음 전원 사이클의 <strong>preferred VT</strong>로 저장한다. 시동 후 일정 시간 내 preferred VT가 없으면 다른 VT로 초기화할 수 있다. 최대 대기 시간은 운전자 설정 수단을 제공하거나 preferred VT의 Get Hardware response의 부팅 시간 사양에서 얻을 수 있다

#### 4.6.7 시스템 셧다운

"System Shutdown"은 Key Switch가 off인데 ECU Power는 유지되는 기간이다(Actuator Power 유지 여부는 무관, ISO 11783-7 참조). 키 off 전환 시 어떤 장치는 즉시 모든 통신을 끊고, 어떤 장치는 정돈된 셧다운을 위해 전원 유지를 요청하며, 어떤 장치는 키 상태를 무시하고 계속 동작한다. Key Switch 상태 판단은 Wheel-based speed and distance(PGN 65096), 전원 유지 요청은 Maintain Power(PGN 65095)를 쓴다. 아래는 권장 관행이다.

<strong>VT 권장 동작</strong> — "Key switch not Off" → "Key switch Off" 전환 시:

1. 불필요한 셧다운 경보를 피하기 위해 unexpected shutdown 감지 로직을 비활성화한다(한 애플리케이션은 즉시 꺼지고 다른 애플리케이션이 3초 타임아웃 이상 ECU Power를 유지하는 경우 대비)
2. Key Switch Off 동안, 그리고 pool을 VT 휘발성 메모리에 올린 ECU들의 마지막 "Maintain ECU Power" 요청 후 최소 2초간 서비스를 유지한다
3. 키가 다시 켜지면 재초기화한다. VT Status message가 중단되었었다면 표준 초기화 절차를 수행한다

NOTE: VT version 3 이하는 셧다운 동작 미규정이라 VT Status message 중단을 포함한 전 통신 중단이 있을 수 있다.

<strong>Working Set 권장 동작</strong> — 키 off 전환 시:

1. "Maintain Power" message로 자기 상태를 알리고, 선택적으로 전원 유지를 요청할 수 있다
2. "Maximum time of tractor power" 파라미터를 모니터링해 전원 관리에 활용할 수 있다
3. Delete Object Pool command를 보내 unexpected shutdown 표시 가능성을 없앨 수 있다
4. VT Status message 부재를 VT의 unexpected shutdown으로 간주하지 말고, 다른 VT로 연결을 시도하지도 않아야 한다
5. 키가 다시 켜지면 재초기화한다

#### 4.6.8 Working Set object와 active mask

초기 pool 정의에서 각 Master는 <strong>Working Set object를 정확히 하나</strong> 제공해 descriptor, active mask, 지원 언어를 정의해야 한다. descriptor는 그래픽·텍스트·혼합 가능하나 Soft Key designator 크기 영역에 맞아야 하고, 벗어나는 부분은 클리핑된다. VT는 Working Set을 운전자에게 표현할 필요가 있을 때(통신 알람, Auxiliary Control 설정 등) 언제든 descriptor를 쓸 수 있다.

<strong>active/inactive 상태</strong>

- Working Set이 "active"면 독점적 입력 포커스를 갖고 VT 디스플레이에 표시된다. "inactive"여도 표시는 될 수 있으나 입력 포커스는 없다
- VT는 운전자가 active로 만들 Working Set을 선택할 수단을 제공해야 한다. 어느 시점이든 active Working Set은 하나뿐이다
- Working Set은 자신이 보이지 않을 때 자기 mask를 강제로 표시시킬 수 없고, 다른 Working Set이 active일 때 자신을 active로 강제할 수 없다. 예외: active mask를 <strong>Alarm mask</strong>로 설정하면 소유 Working Set이 active가 된다(현재 active Working Set의 active mask가 같거나 높은 우선순위의 alarm mask인 경우 제외)
- VT version 4 이상은 active Working Set 외에 inactive Working Set들도 함께 표시할 수 있다. VT는 VT On User-Layout Hide/Show message로 inactive Working Set에게 자기 Data Mask/Soft Key Mask가 보이는 상태이니 갱신하라고 알린다. Working Set이 해당 mask에 hidden 상태로 응답하면 이 기능 미지원으로 간주하고, VT는 표시 정보가 갱신되지 않을 수 있음을 운전자에게 알린 뒤 그대로 표시할 수 있다

<strong>상태 전이 시 VT 동작</strong>

Active mask만 지원하는 VT(Table 2):

| 전이 | VT 동작 |
| --- | --- |
| Active → Inactive | 해당 WS의 active Data/Alarm Mask와 Soft Key Mask를 숨김. VT Status message를 글로벌(255)로 전송 |
| Inactive → Active | 해당 WS의 active Data/Alarm Mask와 Soft Key Mask를 표시. VT Status message를 글로벌로 전송 |

다수 Working Set·Window Mask 동시 표시를 지원하는 VT(Table 3):

| 전이 | VT 동작 |
| --- | --- |
| Active → Inactive+Visible | active 표시 제거, VT Status 글로벌 전송, VT On User-Layout Hide/Show(Shown) 전송 |
| Inactive+Visible → Active | Hide/Show(Hidden — 특수 케이스, H.20 참조) 전송, active Data/Alarm Mask·Soft Key Mask 표시, active임을 시각 표시, VT Status 글로벌 전송 |
| Hidden → Active | active mask·Soft Key Mask 표시, active 시각 표시, VT Status 글로벌 전송 |
| Active → Hidden | mask 숨김, VT Status 글로벌 전송 |
| Inactive+Visible → Hidden | Hide/Show(Hidden) 전송 |
| Hidden → Inactive+Visible | Hide/Show(Shown) 전송 |

공통 규칙: 한 WS의 inactive→active 전이가 다른 WS의 active→inactive를 유발하면 VT Status message는 <strong>한 번만</strong>(새 active WS를 명시) 보낸다.

Working Set은 Change Active Mask command로 Working Set object의 active mask 속성을 바꿔 다른 Data Mask를 선택하거나 Alarm Mask를 활성화할 수 있다. inactive 상태에서도 active mask 변경은 가능하다 — 나중에 보이게 될 때 적절한 mask가 표시되도록 하기 위함이다. inactive Working Set의 active mask는 보이지 않아도 그 Working Set의 active mask로 유지된다.

#### 4.6.9 연결 관리

<strong>VT Status message — 1초 주기.</strong> Working Set은 이 메시지로 VT 존재·상태를 확인한다. <strong>3초간</strong> 못 받으면 VT 셧다운으로 판정하고 <strong>안전 상태(safe state)</strong>로 진입해야 한다. 안전 상태란 VT 인터페이스에 의존하는 모든 기능이 운전자·기계를 위험에 빠뜨리지 않는 기지(known) 상태다. 재연결하도록 설계된 Working Set은 초기화 절차를 재시작한다.

<strong>Working Set Maintenance message — 1초 주기.</strong> VT는 이 메시지로 각 Working Set의 존재를 확인한다. 3초간 못 받거나 initiating bit가 설정된 메시지를 다시 받으면 Master의 unexpected shutdown으로 판정한다.

| 상황 | VT의 운전자 경보 |
| --- | --- |
| pool 삭제를 명령한 뒤 Maintenance 중단(자발적 이탈) | 경보 안 함 |
| 점화 키 off 감지 가능 + off로 보고됨 | 경보 안 함 |
| 해당 WS의 pool이 휘발성 메모리에 없음 | 경보 안 함 |
| pool 삭제 명령 없음 + 키 off 아님 + pool 존재 | <strong>unexpected shutdown</strong> — 운전자에게 경보 후 휘발성 메모리에서 pool 삭제(경보 수단은 VT 고유) |

보이는 Working Set의 pool이 삭제되면 그 WS의 모든 표시(Data Mask, Window Mask 등)가 제거된다. active Alarm Mask가 있었으면 VT가 자동 해제한다. VT는 다른 연결된 Working Set이나 VT 고유 화면에 제어를 넘길 수 있고 VT Status message를 갱신해야 한다. 삭제된 WS에 매핑된 auxiliary assignment도 제거해야 한다.

unexpected shutdown을 감지한 상태에서 initiating bit 없는 Maintenance를 받으면 VT는 Acknowledgement:NACK를 WS Master에게 보낸다. Working Set은 초기화 절차를 재시작해 재연결할 수 있다.

#### 4.6.10 운전자 인터페이스 갱신

<strong>대역폭 관리 권장</strong>: CAN 대역폭과 VT 처리 대역폭은 모든 Working Set이 공유하는 유한 자원이다. active(또는 inactive지만 visible) Working Set은 운전자에게 보이는 변화가 있을 때만 커맨드를 보내고, 표시 중인 mask가 없는 inactive Working Set은 갱신 빈도를 줄이거나 없애는 것이 권장된다.

<strong>속성·값 변경(4.6.10.2)</strong>

- 오브젝트 속성은 attribute ID(AID)가 부여되어 있고, read-only가 아니면 Change Attribute command로 변경할 수 있다. 효율을 위해 여러 속성을 묶은 change 커맨드도 있다(예: Change Font Attributes)
- 연관 Data Mask가 보이지 않아도 속성·값 변경은 가능하다 — 나중에 활성·표시될 때 최신 데이터가 준비되도록
- Working Set과 운전자가 동시에 같은 오브젝트를 바꾸면 <strong>race condition</strong>이 생길 수 있다. 오브젝트가 입력용으로 열렸는지 알 수 있어도(H.8) 처리 지연(FIFO) 때문에 운전자 상호작용 시작 직후 커맨드가 도착할 수 있다. VT발 커맨드 검증은 Working Set 책임이다
- VT version 5 이하는 요구가 일관되지 않아 일부 커맨드가 "object in use" 오류를 반환했다. 이 오류 코드는 <strong>v6부터 deprecated</strong>다. v6 이상에서는 오브젝트가 "in use"여도 속성 변경이 가능하며, VT는 즉시 적용하거나 적용 가능 시점까지 캐시할 수 있다
- 허용은 되지만 "in use" 중 변경을 피해야 하는 속성: Key/Button의 Key code, 입력 필드의 Value·Variable 참조, Input String의 Input attributes·Extended Input attributes, Input String이 참조하는 String Variable, Input Number의 Minimum·Maximum·Offset·Scale, Input object가 참조하는 Font Attributes의 font type, Input Number·Input List가 참조하는 Number Variable
- 팝업 다이얼로그 같은 비원자적 편집 수단에서는 이들 속성을 원자적 집합으로 편집 수단에 넘기고, 런타임 변경은 편집 완료 시 적용한다. 예: 팝업 키패드로 편집 중인 Input Number의 배경색 변경 커맨드가 오면 VT는 오류 없이 수용하되, 편집 종료 후 표시가 복원될 때 적용된 색이 보이면 된다

<strong>오브젝트 교체·추가·삭제(4.6.10.3)</strong>

- 런타임에 오브젝트 교체 가능. 단 교체 오브젝트는 <strong>같은 타입</strong>이어야 한다
- 추가는 transport protocol 세션으로 오브젝트를 보내면 된다. 기존 Object ID로 오브젝트가 오면 기존 것이 교체된다(소유자는 소스 주소로 판별). 크기 변경은 허용되나 VT 메모리 고갈을 유발할 수 있다
- <strong>개별 오브젝트 삭제는 불가</strong> — pool 전체를 Delete Object Pool command로 삭제한 뒤 해당 오브젝트를 뺀 pool을 다시 업로드해야 한다

#### 4.6.11 특수 오브젝트

<strong>Container object</strong> — 두 용도로 쓴다: (1) 오브젝트들을 논리적으로 묶어 컨테이너 단위로 재사용(여러 mask에 같은 컨테이너를 Object ID로 삽입), (2) 오브젝트 그룹의 hide/show. 예: 특정 기능이 있는 작업기에서만 보여야 할 텍스트들을 컨테이너에 넣고, 런타임에 기능 유무에 따라 컨테이너를 숨긴다.

<strong>Attribute object</strong> — font, line, fill, input, extended input의 5종. 다른 오브젝트들이 참조하는 공유 속성 집합으로, 하나를 바꾸면 참조하는 모든 오브젝트가 갱신되어 일관된 look 유지가 쉽다.

<strong>Variable object</strong> — 둘 이상의 오브젝트가 데이터를 공유하게 한다. 예: Meter object와 Output Number object가 같은 Number Variable을 참조하면 Change Numeric Value command 한 번으로 둘 다 갱신되어 버스 트래픽이 준다.

<strong>Macro(4.6.11.4)</strong> — 인터페이스 성능 향상용. 규칙:

- Macro에는 Annex F의 커맨드만 담을 수 있다
- Macro가 다른 Macro를 유발하는 이벤트를 트리거하면 현재 Macro를 먼저 완료한다. Macro는 트리거된 순서로 실행된다
- Macro 안에서 Execute (Extended) Macro command를 실행하면 그 Macro가 <strong>즉시 함수 호출처럼</strong> 실행된 뒤 현재 Macro의 남은 커맨드가 이어진다(이벤트 큐에 뒤로 붙이는 방식은 잘못된 동작)
- 커맨드 실행으로 트리거된 Macro는 다음 버스 커맨드 시작 전에 완료되어야 한다
- Macro Object ID 범위: v4 이하 0~255, v5 이상 0~65534
- Macro는 응답 메시지를 트리거하지 않는다. Macro 내 커맨드에 대해 VT는 CAN 버스에 응답을 보내지 않는다(예: Macro의 Change Active Mask는 VT Status message는 유발하지만 Change Active Mask response는 없음) — 따라서 CAN 트래픽이 감소한다
- Working Set과 Macro가 같은 오브젝트를 바꾸면 race condition 가능 — 예측 가능한 동작인지 평가해야 한다(비동기 TP 전송과 Macro의 값 변경이 겹치는 경우 등)
- <strong>순환 참조 금지</strong> — 무한 Macro 루프는 VT를 모든 Working Set에 대해 동작 불능으로 만들 수 있다

<strong>Object Pointer(4.6.11.5)</strong> — 포함된 오브젝트의 런타임 교체를 가능하게 한다. Pointer 값을 바꾸면 같은 위치에 다른 오브젝트가 그려진다. 참조 가능한 오브젝트 타입은 부모 오브젝트에 따라 제한된다. Object Pointer는 항상 다른 Object Pointer를 가리킬 수 있다. NULL Object ID를 가리키면 아무것도 그리지 않는다. 런타임 변경으로 잘못된 참조가 생기면 VT는 즉시 검출하지 않아도 되고, 해당 Pointer를 담은 Data/Alarm Mask 활성화 시점까지 지연할 수 있다 — 이때 Change Active Mask response(F.35) 또는 VT Change Active Mask message(H.14)로 알리고 pool을 삭제할 수 있다. 즉시 검출하는 경우 Change Numeric Value response에 "invalid value" 오류를 실어 보낸다.

<strong>External Object Pointer(4.6.11.6)</strong> — 한 WS가 다른 WS pool의 오브젝트를 표시할 수 있게 한다.

- 참여 WS의 소프트웨어 업데이트 후에도 참조가 유효하도록, referenced WS와 referencing WS는 외부 참조 활성화 전에 참조 오브젝트 정보를 교환해야 한다(최소한 Object ID 전달). 어느 쪽이든 재시작하면 교환을 반복한다. SCC/SCM(ISO 11783-14)처럼 표준화된 교환 방법이 없으면 제조사 간 합의된 고유 방법을 쓴다
- 무단 참조 방지를 위해 referenced WS는 <strong>External Object Definition object</strong>에 참조 허용 오브젝트를 나열한다. 이 오브젝트는 정확히 하나의 referencing WS에 할당되며, 여러 WS에 참조를 허용하려면 여러 개를 둔다
- referencing WS는 <strong>External Reference NAME object</strong>로 참조할 WS를 식별한다
- 세 오브젝트(External Object Definition, External Object Pointer, External Reference NAME)의 속성이 모두 유효해야 외부 오브젝트를 표시할 수 있다. 정보 교환 완료 전에는 <strong>reset state</strong>여야 한다: External Object Pointer는 External Object Id 속성 = NULL, External Object Definition·External Reference NAME은 Options의 Enable bit = 0
- pool을 VT 비휘발성 저장소에서 로드하면 속성 유효성이 보장되지 않으므로 VT가 이 세 오브젝트 전부를 reset state로 설정해야 한다. WS master가 pool을 업로드하는 경우에는 VT가 reset하지 않는다 — 교환이 미완이면 master가 업로드 전에 reset state로 만들어야 한다
- 표시 전 VT의 유효성 검사 — 다음 전부 충족 시 유효: External Object Pointer의 External Reference NAME ID 속성이 활성화된(enabled) External Reference NAME object를 가리킴, referenced WS의 pool이 VT 휘발성 메모리에 존재, 그 pool에 NAME이 referencing WS를 가리키는 활성화된 External Object Definition이 있음, External Object Id가 그 Definition의 오브젝트 목록에 포함됨
- 참조 오브젝트가 NULL이거나 무효면 External Object Pointer의 Default Object ID 속성이 가리키는 오브젝트를 그린다
- 같은 NAME의 External Object Definition이 여러 개면, 하나 이상에서 유효하면 유효한 참조다

#### 4.6.12 상대 X/Y 위치

X, Y position 속성은 오브젝트가 그려질 위치를 결정하며 <strong>항상 부모 오브젝트의 좌상단 기준 상대 좌표</strong>다. X, Y 위치는 항상 부모 오브젝트 쪽에 있다(자식이 자기 위치를 갖는 게 아니라 부모가 자식의 위치를 나열).

#### 4.6.13 오브젝트 중첩(Overlaid objects)

- 두 오브젝트가 같은/겹치는 공간을 차지하는 mask 구성이 가능하며 VT는 이를 지원해야 한다
- 부모의 자식 목록에서 <strong>먼저 나열된 오브젝트가 계층상 아래</strong>다. 나중에 나열된 오브젝트가 먼저 나열된 오브젝트를 덮어 그려진다(마지막 오브젝트 전체가 보이고, 이전 오브젝트는 겹치지 않는 부분만 보임)
- 오브젝트가 변경되면 겹쳐서 손상된 모든 오브젝트를 다시 그려야 한다(<strong>refresh event</strong>). 모든 오브젝트가 직사각형 크기를 명시·암시하는 것은 겹침 탐색을 단순화하기 위함이다
- 예: 오브젝트 1 hide 명령 → VT는 오브젝트 영역을 부모 mask 배경색으로 채워 오브젝트와 자식들을 지우고 → 손상 가능성이 있는 다른 오브젝트(오브젝트 2)를 refresh한다. 중간 단계가 운전자에게 보이지 않게 구현할 수 있다
- <strong>알파 채널(v6 이상)</strong>: VT 표준 색상 팔레트를 알파(투명도) 포함 팔레트로 재정의할 수 있다. 위 오브젝트가 불투명이 아니면 겹친 영역에서 알파 블렌딩이 일어난다. 알파 0 = 완전 투명, 255 = 완전 불투명. 블렌딩 공식: blended = source × alpha/255 + destination × (255 − alpha)/255 (source = 위 오브젝트 색, destination = 아래 오브젝트가 이미 블렌딩되어 렌더된 색. 반올림·절사 허용). 셋 이상 겹치면 맨 아래부터 층별로 순차 계산한다. 불투명 오브젝트가 알파 있는 오브젝트 위에 있으면 블렌딩은 일어나지 않는다

#### 4.6.14 알람 처리

Working Set은 언제든 Alarm Mask로 알람 정보를 표시할 수 있다. 여러 Working Set이 Alarm Mask를 활성화하면 VT는 우선순위 순으로 표시한다.

- 우선순위 판정: 1차 = Alarm Mask object의 priority 속성, 2차 = 활성화 시간순. 같은 priority면 VT가 먼저 처리한 것이 active mask가 된다
- 최고 우선순위 알람은 소유 Working Set이 active mask를 바꿀 때까지 항상 표시된다. active Working Set이 더 낮은 우선순위 알람이나 Data Mask로 바꾸면 다음 순위 Alarm Mask가 처리된다
- v6 이상에서는 선택 불가능한(not selectable) Working Set도 Change Active Mask command로 Alarm Mask를 활성화할 수 있다. 해제는 Data Mask 활성화로 한다. VT는 일반 알람 규칙을 적용한다
- 알람 활성화로 중단된 운전자 입력은 모든 Alarm Mask가 ACK된 후 재개되도록 보존할 수 있다
- Alarm Mask에는 속성으로 Soft Key Mask가 연관되며 알람 표시 중 함께 표시된다

<strong>알람 프로토콜 순서</strong>

1. Master가 Change Active Mask command로 Alarm Mask를 활성화한다(Working Set당 active Alarm Mask는 1개)
2. VT가 Change Active Mask response로 응답한다
3. 우선순위에 따라 VT가 Alarm Mask와 연관 Soft Key Mask를 표시한다. Alarm Mask가 나타나거나 재등장하는 mask 전환 시 연관 음향 신호를 울려야 한다. 진행 중인 더 낮은 우선순위 알람의 음향은 종료해야 한다(높은 쪽이 silent라도). multisound 미지원 VT는 진행 중인 Control Audio Signal command의 음향도 종료해야 하며, v4 이상은 VT Control Audio Signal Termination message로 종료를 알린다. 알람 음향이 끝나거나 silent 설정이면 ECU들의 Control Audio Signal command를 수용해야 한다
4. VT가 글로벌 주소로 VT Status message를 보내 Working Set들에 알린다
5. 운전자가 VT 고유 ACK 수단으로 알람을 확인하면 VT는 key code 0의 Soft Key Activation message를 Working Set에 보낸다. 또는 Working Set이 내부 로직으로 Change Active Mask(Data Mask 활성화)로 알람을 해제할 수 있다
6. ACK가 허용되지 않으면 Working Set은 ACK 수단을 무시할 수 있고, Change Active Mask로 Alarm/Data Mask 전환도 가능하다
7. VT가 Change Active Mask response로 응답하고 새 mask를 표시한다

<strong>mask 전환 시 VT 동작(Table 4)</strong> — 요청자가 현재 active Working Set인지에 따라:

| 전환 | 요청자 = active WS? | VT 동작 |
| --- | --- | --- |
| Data → Data | Yes | 현재 Data Mask 숨기고 새 Data Mask 표시 |
| Data → Data | No | 단일 visible Data Mask VT면 시각 변화 없음. 다중 visible 지원이고 해당 WS가 보이는 중이면 현재 mask 숨기고 새 mask 표시 |
| Data → Alarm | Yes | Data Mask 숨기고 Alarm Mask 표시 |
| Data → Alarm | No | 최고 우선순위 알람이면 현재 WS 비활성화, 이 WS 활성화 |
| Alarm → Alarm | Yes | 최고 우선순위면 현재 Alarm Mask 숨기고 새 것 표시. 아니면 이 WS 비활성화, 최고 우선순위 알람 WS 활성화 |
| Alarm → Alarm | No | 최고 우선순위면 현재 WS 비활성화, 이 WS 활성화 |
| Alarm → Data | Yes | 다른 WS에 알람 있으면 이 WS 비활성화, 최고 우선순위 알람 WS 활성화. 아니고 이 WS가 마지막 visible Data Mask였으면 Alarm 숨기고 Data 표시. 그 외에는 이 WS 비활성화, 마지막 visible Data Mask 보유 WS 활성화(그런 WS 없으면 표시할 mask 없음 상태와 동일) |
| Alarm → Data | No | 시각 변화 없음 |

#### 4.6.15 클리핑

대부분의 오브젝트는 명시적·암시적 크기를 갖는다. VT는 오브젝트 정의 크기 밖에 그려지는 모든 것을 클리핑해야 하며, 클리핑은 항상 <strong>픽셀 단위(그래픽 기준)</strong>다. 텍스트·숫자 오브젝트에도 같은 규칙이 적용된다 — 줄바꿈(wrapping) 여부와 무관하게 영역에 다 들어가지 않는 텍스트는 픽셀 단위로 잘린다(문자 단위가 아님).

#### 4.6.16 스케일링

Working Set은 VT의 Data Mask 영역·Soft Key designator 크기를 파악해 자기 오브젝트 정의를 그에 맞게 조정해야 한다. 조정은 pool 전송 전이든 후든 가능하다(단, 전송된 pool이 그 VT에서 무효가 되면 안 됨 — 예: 흑백 VT에 컬러 오브젝트를 보낸 뒤 흑백으로 바꾸는 것은 불가). 즉 mask 외관의 완전한 제어권은 Working Set에 있다.

- <strong>위치·크기</strong>: Working Set이 VT의 Data Mask 영역과 designator에 맞춰 위치·크기를 스케일해야 한다
- <strong>폰트</strong>: Working Set이 정의된 영역에 대해 best-fit 알고리즘으로 최적 폰트를 선택해야 하고, 선택한 폰트·스타일을 VT가 지원하는지 확인해야 한다. 최소 폰트는 6 × 8이며, 스케일 결과가 6 × 8 미만이면 6 × 8을 쓴다. 이로 인해 필드 경계 근처 텍스트가 잘리거나, 오브젝트 크기와 무관하게 폰트가 스케일되어 인접 텍스트가 겹칠 수 있다 — Working Set 설계자가 대비해야 한다
- <strong>Picture Graphic object</strong>: VT가 오브젝트의 width 속성에 따라 자동 스케일한다

#### 4.6.17 운전자 입력(내비게이션·데이터 입력 상태 기계)

활성화된 visible 입력 오브젝트나 Button이 있는 Data Mask를 표시 중인 VT는 항상 <strong>Navigating</strong> 또는 <strong>Data input</strong> 상태 중 하나다(Button이 포커스를 가진 동안은 Data input 상태가 될 수 없음).

<strong>입력 오브젝트의 가시성 판정</strong> — 다음 경우에도 오브젝트는 visible로 간주된다: 폭·높이가 0, 다른 오브젝트에 완전히 덮임, 부모 계층의 클리핑 한계 밖에 완전히 위치. 다만 이런 오브젝트는 터치스크린에서 활성화가 불가능할 수 있으므로 권장되지 않으며, 필요에 따라 enable/disable하는 편이 내비게이션 동작을 예측 가능하게 한다.

- 새 active Data Mask가 선택되면 상태는 Navigating으로 리셋된다. Alarm Mask가 선택된 경우 VT는 상태를 기억했다가 알람 표시 후 같은 Data Mask로 복귀하면 복원할 수 있다. 이 방식을 구현했는데 다른 Data Mask로 복귀하면 일반적인 Data Mask 변경으로 간주해 해당 메시지를 보내야 한다
- 초기 포커스 지점과 탭 순서는 VT 고유이나, 부모 오브젝트 내 입력 오브젝트 정의 순서가 탭 순서를 결정할 수 있음을 Working Set은 알아야 한다
- VT는 내비게이션 중 지나치는 모든 오브젝트마다 VT Select Input Object message를 보내지 않아도 된다(로터리 컨트롤을 빠르게 돌릴 때는 포커스를 잃는 오브젝트와 최종 획득 오브젝트에만 보내도 됨)
- Navigating 상태에서 VT는 어떤 input·Button·Key가 선택(포커스)됐는지 운전자에게 표시해야 한다(방법은 VT 고유 — 프레임, 배경색 변경, 터치 시 순간 하이라이트 등). 터치스크린은 포커스 획득 즉시 입력을 열고 입력 완료 시 포커스를 제거하는 동작이 흔하다(필수는 아님)
- Working Set의 Select Input Object command는 운전자 주의를 특정 필드로 끌기 위한 수단일 수 있다(설정 마법사 등) — VT 설계자는 이를 인지해야 한다
- VT는 disabled 입력 오브젝트를 표시해야 한다(방법은 VT 고유). disabled 표시를 위한 시각 변화는 오브젝트의 폭/높이를 벗어나면 안 되고 오브젝트는 읽을 수 있어야 한다
- Data input 상태의 VT 동작은 고유 영역이며 입력 중 Data Mask 일부/전부를 덮을 수 있다. 입력 중 해당 오브젝트의 속성 변경은 현재 입력 중인 값에 영향을 주지 않아야 한다(예: Input Number Scale 변경이 입력 중 표시 값을 바꾸면 안 됨)
- VT version 3 이하는 VT Select Input Object message로 Button·Key 선택을 지원하지 않는다

<strong>내비게이션·입력 이벤트에 대한 VT 반응(Table 5 요약)</strong> — 응답 메시지 순서는 규정이 아니므로 Master는 어떤 순서로 와도 처리하도록 설계해야 한다.

| 현재 상태 | 커맨드/이벤트 | 새 상태 | 주요 응답 |
| --- | --- | --- | --- |
| Navigating | Select Input Object command (byte 4 = FF₁₆) | Navigating | Select Input Object response |
| Navigating | Enable/Disable Object command(포커스 오브젝트 disable) | Navigating | 오브젝트 disabled·포커스 상실(VT가 다음 오브젝트로 이동 가능), response + 포커스 잃는/얻는 오브젝트에 VT Select Input Object message |
| Navigating | Change Active Mask command | Navigating | 포커스 잃는 오브젝트 Select 메시지, response, VT Status(active WS발이면), 포커스 얻는 오브젝트 Select 메시지 |
| Navigating | Select Active Working Set command | Navigating | 포커스 잃는 오브젝트 Select 메시지, response, VT Status(새 WS·Data Mask), 포커스 얻는 오브젝트 Select 메시지 |
| Navigating | ESC command | Navigating | ESC response(입력 열린 것 없음 오류 코드) |
| Navigating | 운전자가 Button 활성화 | Navigating | Button Activation message |
| Navigating | 운전자가 새 오브젝트로 이동 | Navigating | 잃는/얻는 오브젝트에 VT Select Input Object message |
| Navigating | 운전자가 오브젝트를 입력용으로 열기 | Data input | VT Select Input Object message(포커스 오브젝트) |
| Navigating | Select Input Object command (byte 4 = 00₁₆) | Data input | Select Input Object response |
| Data input | Select Input Object command(포커스 없는 오브젝트 선택) | Data input | response(다른 필드 입력 중 오류 코드) |
| Data input | Enable/Disable Object command(포커스 오브젝트 disable) | Data input | 오브젝트는 enabled·포커스 유지, response(운전자 입력 활성 오류 코드) |
| Data input | Change Numeric Value command(포커스 오브젝트) | Data input | Change Numeric Value response |
| Data input | Change String Value command(포커스 오브젝트 또는 그것이 참조하는 Input Attribute) | Data input | Change String Value response |
| Data input | Change Active Mask command | Navigating | VT ESC message, 잃는 오브젝트 Select 메시지, response, VT Status, 얻는 오브젝트 Select 메시지 |
| Data input | Select Active Working Set command | Navigating | VT ESC message, Select 메시지, response, VT Status, Select 메시지 |
| Data input | Change Attribute command(포커스 오브젝트) | Data input | Change Attribute response |
| Data input | Change List Item command(포커스 오브젝트) | Data input | Change List Item response |
| Data input | Pool Update가 포커스 오브젝트를 변경 | Navigating | VT ESC message + Select 메시지들 |
| Data input | 부모 Container가 hidden됨 | Navigating | VT ESC message + Select 메시지들 |
| Data input | 이 오브젝트를 가리키던 Pointer가 변경됨 | Navigating | VT ESC message + Select 메시지들 |
| Data input | ESC command | Navigating | ESC response + Select 메시지 |
| Data input | 운전자가 ESC 수단 활성화 | Navigating | VT ESC message + Select 메시지 |
| Data input | 운전자가 ENTER 수단 활성화 | Navigating | VT Change Numeric Value 또는 VT Change String Value message(새 값이 이전과 같아도 전송) + Select 메시지 |

Change Active Mask·Select Active Working Set의 상태 전이는 새 mask가 새 Data Mask이거나, Alarm Mask인데 VT가 입력 오브젝트 상태를 저장하지 않는 경우에 해당한다.

#### 4.6.18 Soft Key·Button 활성화

Key object·Button object·ACK 키가 눌리거나(pressed), 떼지거나(released), 래치(latched)될 때마다 VT는 Soft Key Activation message 또는 Button Activation message를 <strong>Working Set Master에게</strong> 보낸다. 키 눌림에 Macro가 연관돼 있으면 VT가 실행한다 — 키 이벤트에 mask 전환 같은 Macro를 연관시키면 인터페이스 반응성이 좋아진다.

- v5 이상에서 ACK 키는 Key·Button과 일관된 메시지(pressed, held, released)를 보낸다(v4 이하는 미정의라 구현 편차가 있었음)
- 활성화된 상태에서 Key·비래치 Button이 화면에서 지워지면(Change Active Mask, Change Soft Key Mask, Hide/Show 등) VT는 그 부모 Data Mask 상의 오브젝트에 대해 released를 보내고, 운전자가 물리적으로 뗄 때까지 그 키를 무시해야 한다
- 눌린 채 Button이 active mask의 다른 위치로 이동하면: 물리 키로 활성화된 경우 pressed 유지, 터치·포인팅으로 활성화됐고 터치 지점을 벗어난 위치로 이동한 경우 released 전송 후 물리적으로 뗄 때까지 무시
- 터치스크린에서 운전자가 누른 채 손가락을 오브젝트 밖으로 미끄러뜨리면, 추적 가능한 VT는 <strong>abort</strong>를 나타내는 Activation message를 보내야 한다. 이동과 슬라이드가 겹치면 먼저 발생한 이벤트가 우선한다
- visible Data Mask 변경 시: 이전 mask의 활성화된 오브젝트에 released를 보내고, 새 mask에 대한 Activation message는 보내지 않는다
- Soft Key Mask는 Data/Alarm Mask의 자식으로 간주된다. active Data/Alarm Mask가 바뀌면 <strong>같은 Soft Key Mask를 쓰더라도</strong> Soft Key Mask도 바뀐 것으로 처리된다 — 눌린 Soft Key에 released를 보내고 뗄 때까지 무시하며, Soft Key Mask의 On Hide·On Show Macro도 실행한다
- Change Active Mask·Change Soft Key Mask가 결과적으로 현재 mask를 바꾸지 않으면 pressed/held/released 상태 변화도, On Hide/On Show Macro 실행도 없다
- <strong>동시 활성화</strong>: Technical data의 "동시 활성화 지원" 비트(D.9)가 0이면 VT는 한 번에 하나의 Soft Key(또는 Button)만, 정해진 시퀀스(no Keys pressed → pressed → [held] → released → no Keys pressed)로만 지원한다. 첫 키가 pressed/held로 감지된 상태에서 두 번째 키가 눌리면 무시한다. 지원하면 겹치는 메시지 시퀀스를 보낸다
- 전원 인가 시 이미 눌려 있는 Key·Button은 held로 보고하지 않는다(운전자 진단 메시지 사유는 될 수 있음)

#### 4.6.19 폰트 렌더링

VT가 지원해야 하는 필수·선택 문자 집합은 Annex K에 있고, 여기서는 표현(presentation) 요구사항을 정의한다.

- v4 이상 VT에서 접근 가능한 문자 집합에는 모든 폰트 크기에서 읽기 어려운 문자·기호·표의문자가 포함될 수 있다. 저해상도에서 판독을 보장해야 하면 다른 언어·인코딩 또는 Picture Graphic object로 전달할 필요가 있다
- WideString 텍스트의 정밀한 표현 정의는 이 문서 범위 밖이다(고급 레이아웃/폰트 렌더링 엔진 영역). UNICODE 제어 코드와 아래 속성이 충돌하면 <strong>지원되는 UNICODE 제어 코드가 우선</strong>한다. 미지원 제어 코드는 표시 공간을 차지하지 않아야 한다. justification은 보존될 것으로 기대되나 auto-wrap·비인쇄 문자 규칙은 다를 수 있다

<strong>텍스트 justification(4.6.19.2)</strong>

텍스트 기반 오브젝트는 justification 속성을 가지며, width·height로 정의된 필드 내에서 문자열의 수평·수직 위치를 지정한다. v3 이하는 문자 단위(정밀 정의 없음), <strong>v4 이상은 항상 픽셀 단위(그래픽 기준)</strong>다. VT의 렌더링 엔진이 ascender/descender나 문자 자체를 위해 공간을 예약하면 약간의 여백은 허용된다. 데이터 입력 중에는 justification을 필드가 닫힐 때까지 보류할 수 있다(표시용일 뿐 저장 값은 불변).

수평 justification별 공백 처리·클리핑 규칙:

| 구분 | 규칙 |
| --- | --- |
| Left | 선행 공백 제거 안 함. 첫 문자가 필드 왼쪽에 위치. auto-wrap 시 이후 줄들의 선행 공백은 justification 전에 제거. 넘치면 오른쪽에서 픽셀 클리핑 |
| Middle | justification 전에 선행·후행 공백 모두 제거. 픽셀 기준 중앙 정렬. 넘치면 좌우 양쪽 클리핑 |
| Right | 후행 공백 제거. 마지막 문자가 필드 오른쪽에 위치. 넘치면 왼쪽에서 클리핑 |

공통: auto-wrap 시 justification 규칙은 각 줄에 적용되고 빈 줄은 제거하지 않는다. auto-wrap 후 줄의 선행 공백은 left/middle에서 제거되고, forced line break(`<CR>`) 후 줄의 선행 공백은 left에서 유지된다. NBSP(0xA0)는 비공백 문자처럼 취급된다.

수직 justification(v4 이상): Top = 필드 최상단부터 표시, Middle = 수직 중앙(그래픽 기준), Bottom = 텍스트 블록 하단을 필드 하단에 맞춤. auto-wrap 여부와 무관하게 적용되고 빈 줄은 제거하지 않는다.

<strong>Non-proportional 폰트(4.6.19.3)</strong>

- VT는 non-proportional 블록 폰트를 지원해야 한다. 크기는 항상 X-Y 쌍(예: 8 × 10 = 폭 8·높이 10픽셀)
- 문자는 스타일과 무관하게 폰트 크기 박스를 초과할 수 없다(8 × 10 bold italic도 8 × 10 안에 들어가야 함). 박스 내부 하단·우측에 여백을 두어 인접 문자·행을 수용하는 것이 권장된다
- 폰트 크기·스타일 구성은 VT 설계자 선택이나 <strong>기본 6 × 8 normal(upright)은 최소 요구</strong>다. Working Set은 Get Text Font Data message로 VT의 폰트 능력을 파악한다
- 문자는 해당 오브젝트 options 속성에 따라 투명(배경 투과) 또는 불투명(배경색 채움)으로 렌더링된다

<strong>Proportional 폰트(4.6.19.4)</strong>

- v4 이상 VT의 선택 기능. 문자 폭이 가변이고 height 속성은 8부터 Get Text Font Data response가 알린 최대 지원 폰트 높이까지 완전 스케일 가능. 폰트 크기의 height 속성만 적용되고 width는 무시된다. 렌더된 문자는 선택된 폰트 높이를 초과하면 안 된다
- proportional 지원을 표명한 VT는 8부터 최대 크기까지 전 높이 범위를 지원해야 한다(1픽셀 해상도 — 단 렌더링 엔진·글자 모양 특성상 모든 문자에서 1픽셀 차이가 감지되지 않을 수 있음)
- 일반 클리핑 규칙이 그대로 적용되므로 Working Set 설계자는 가변 폭을 감안해 충분한 필드 폭을 잡아야 한다
- Working Set은 사용 전에 VT의 proportional 지원 여부를 질의해야 하며, 미지원이면 pool 업로드·이후 Change Font Attributes에서 non-proportional만 써야 한다. 미지원 VT가 proportional 요청을 받으면: pool 검증 중 Font Attributes object가 proportional을 가리키면 pool 거부, Change Font Attributes command가 무효 크기·타입이면 오류 응답

<strong>Auto-wrap(4.6.19.5)</strong>

표시할 텍스트가 오브젝트 폭보다 길고 auto-wrap이 활성화되면 VT는 다음 조건에서 다음 줄로 개행한다(proportional 여부 무관, 텍스트는 오브젝트 폭 경계를 넘지 않아야 함).

- 단어 사이 Space(20₁₆)
- Soft Hyphen(AD₁₆) — 개행이 일어나면 줄 끝에 soft hyphen을 표시하고, 아니면 표시하지 않음
- Hyphen(2D₁₆) — 텍스트 오브젝트의 Wrap on Hyphen 옵션 비트가 TRUE일 때 하이픈과 다음 문자 사이에서 개행 가능
- 위 규칙으로 줄 안에 개행점이 없으면 줄에서 완전히 보이는 마지막 문자에서 개행
- Line End에서(4.6.19.6)

다음 줄의 선행 공백은 억제되며 추가 auto-wrap 판단에서도 제외된다. auto-wrap이 `<CR>` 같은 forced wrap 위치와 겹치면 하나의 line end로 해석되고, 겹치지 않으면 별개로 처리된다.

<strong>문자열 내 비인쇄 문자(4.6.19.6)</strong> — v4 이상 기준:

- BS(Back Space)는 무시된다(Annex K에서 가위 표시된 문자들도 동일)
- 단일 CR, 단일 LF, 시퀀스 CRLF는 각각 <strong>line end 1개</strong>로 해석된다. 따라서 LFCR은 line end 2개다
- 00₁₆(WideChar는 0000₁₆)은 정의된 문자열 길이 전이라도 표현을 종료한다. 종료 0 이후의 문자는 입력·표현 모두에서 무시된다. 편집으로 겉보기 길이를 length 속성까지 늘릴 수 있으며, length 속성이 편집 한도를 제어한다
- 그 외 표시 불가 문자는 그리기·정렬 판단에서 커서를 전진시키지 않아야 하며, VT가 효율을 위해 문자열에서 제거할 수 있다

<strong>문자열 인코딩(4.6.19.7)</strong>

- 텍스트는 8-bit char 또는 (v4부터) Unicode/ISO 10646 WideChar로 인코딩된다. 문자 집합은 Font Attributes object의 Font type 속성이 가리키지만 <strong>WideString에서는 Font type이 무시</strong>된다
- WideString은 UTF-16 리틀 엔디안이며 항상 BOM(FEFF₁₆)으로 시작한다. BOM은 표시 문자가 아니고 텍스트에 포함되지 않는다. 첫 2바이트가 FF₁₆ FE₁₆이면 WideString, 아니면 8-bit string이다
- length 속성은 항상 <strong>바이트 수</strong>다. WideChar 문자 수 = length/2 − (surrogate pair 수) − 1. length가 홀수 바이트를 가리키면 마지막 바이트는 무시된다
- VT는 Unicode의 어떤 문자든 지원할 수 있으나 최소한 Table K.8의 문자들을 지원해야 한다. 미지원 문자가 포함된 WideString도 표시해야 하며, 미지원 문자는 표시 가능한 문자(예: "□", VT 고유)로 대체한다
- VT는 Input String 오브젝트 값의 인코딩을 바꾸면 안 된다 — WideString을 담은 오브젝트에 대한 VT Change String Value message도 WideString이어야 한다
- FFFF₁₆ 초과 문자는 surrogate pair로 표현한다: S = 문자코드 − 10000₁₆, high surrogate = D800₁₆ + (S >> 10), low surrogate = DC00₁₆ + (S의 하위 10비트). 최대 문자 10FFFF₁₆ = pair DBFF₁₆, DFFF₁₆

#### 4.6.20 렌더링 정확도와 VT 설계 자유도

이 문서의 목적은 제조사 간 상호운용이며, 원 설계가 운전자에게 올바르게 해석될 만큼 정확히 전달되면 된다. 많은 오브젝트는 표현 요소가 전부 정의되어 있지 않아 VT 개발자가 성능·시각 스타일 등을 고려해 구현을 선택할 수 있다. 예: Output Meter의 바늘 크기·모양, Output Linear Bar Graph의 fill·set point mark·tic mark, 0/45/90도가 아닌 Output Line 등은 그리기 알고리즘에 따라 비슷하지만 다른 결과가 나올 수 있어 <strong>픽셀 수준 정확도는 보장되지 않는다</strong>. 픽셀 정확도가 필요하면 Picture Graphic object를 쓰되 VT가 스케일하지 않도록(Width = Actual width) 해야 한다.

#### 4.6.21 라인 아트와 도형 채우기

- VT는 line art(선 패턴)를 continuous 방식(도형 전체에 패턴 연속 적용) 또는 restarting 방식(변마다 패턴 재시작)으로 렌더할 수 있다. 시작점은 일관되게 적용해야 한다(polygon은 첫 점, rectangle은 좌상단, ellipse는 시작 각도). 굵은 선·line suppression 조합의 정확한 표현은 VT 설계에 달렸다
- <strong>솔리드 채우기는 scan-line 방식</strong>으로 구현해야 한다. flood-fill·boundary-fill은 오브젝트 겹침으로 채우기가 끊길 수 있고 성능 문제도 있어 부적합하다. 채우기는 오브젝트 내부만 포함하며 <strong>테두리에 해당하는 픽셀은 제외</strong>한다(테두리 line art 사용·억제 시 잘못된 채우기가 특히 눈에 띔)
- <strong>패턴 채우기 규칙</strong>: 패턴은 Table B.50 폭 제한을 만족하는 Picture Graphic object여야 하고, raw data를 그대로 쓰며 오브젝트 속성과 무관하게 스케일하지 않는다. 패턴 버퍼 좌상단은 VT의 물리 Data Mask(또는 개별 designator, user-layout window mask)의 좌상단에 앵커되어 가로·세로로 반복된다 — 이래야 Data Mask 영역 내 오브젝트 간 패턴이 이어지고 모든 VT에서 같아 보인다. 채우기 패턴에서는 투명·점멸 옵션 속성이 무시된다

#### 4.6.22 이벤트

- Working Set이나 VT의 오브젝트 조작은 이벤트를 발생시킨다. 많은 오브젝트가 이벤트·Macro 그룹의 선택적 목록을 갖는다
- 발생한 이벤트에 Macro가 연관돼 있으면, 커맨드가 <strong>유효한 커맨드로 수용된 시점</strong>에 VT가 Macro를 실행한다. 커맨드가 실제 파라미터·값·표시 갱신을 유발하지 않아도 실행된다. 예: 같은 값으로의 Change Numeric Value도 Macro를 실행하고, 이미 hidden인 컨테이너에 대한 hide 커맨드도 실행한다. 무효 값 커맨드는 거부되고 Macro도 실행되지 않는다
- Macro는 event/Macro 목록에서 만나는 순서로 실행된다. 같은 event id를 목록에 여러 번 나열할 수 있다
- 이벤트+Macro를 쓰면 Master가 직접 응답하지 않아도 되므로 인터페이스 반응성이 좋아진다(예: Soft Key press 이벤트로 Data Mask 전환)

<strong>Macro 참조 인코딩</strong>

- v4 이하: 오브젝트 정의 내 그룹당 2바이트 — Event ID(0~254) 1바이트 + Macro ID(0~255) 1바이트. Macro Object ID가 0~255로 제한됨
- v5 이상: 16bit Macro Object ID(0~65534)도 지원해야 한다. 하위 호환을 위해 같은 2바이트 그룹 구조를 쓰되, <strong>첫 바이트 Event ID = 255</strong>(Use Extended Macro Reference)면 그룹 2개를 연결해 하나의 16bit 참조로 해석한다: 1바이트 = FF₁₆, 2바이트 = Macro ID 하위 바이트, 3바이트 = 실제 Event ID(0~254), 4바이트 = Macro ID 상위 바이트

#### 4.6.23 터치스크린과 포인팅 디바이스

VT는 터치스크린이나 포인팅 방식(마우스·조이스틱)을 선택적으로 지원할 수 있다. Working Set은 Get Hardware message로 이 능력을 파악해 pool을 조정한다. Button object는 Data Mask에 터치·클릭 가능한 버튼을 넣도록 정의되어 있다. <strong>Pointing Event message</strong>는 버튼·입력 오브젝트와 연관되지 않은 Data Mask(또는 Free Form Window Mask type 0) 영역이 터치·클릭됐음을 active Working Set에 알린다. v4·5는 Alarm Mask도 포함했으나 v6부터 deprecated다.

#### 4.6.24 고유(Proprietary) 수단

VT는 다양한 고유 수단(Proprietary Objects·Events·Colours·Commands·Fonts)을 지원할 수 있다. VT 제조사와 다른 제조사의 Working Set이 고유 수단을 쓰는 것은 최대한의 ISO 호환성을 위해 권장되지 않는다 — 고유 항목은 제조사가 공지 없이 바꿀 수 있고, 정의를 모르는 Proprietary Object는 파싱이 불가능해 VT가 pool을 거부할 수 있다.

또한 Working Set과 VT는 낮은 버전 요구사항과 모순되지 않는 한 <strong>더 높은 버전의 메시지·오브젝트</strong>를 교환·지원할 수 있다(예: version 2 VT가 v4에서 표준화된 Font type 5 Cyrillic 지원). 이는 표준을 활용하지만 낮은 버전에는 정의가 없으므로 고유 수단으로 간주된다 — 상대가 신기능을 지원하는지 고유 수단으로 확인해야 하고, 지원을 가정해서는 안 된다. VT는 pool에 미지원 기능이 있으면 거부해야 하고, 표시·메시징 동작 모두 완전 지원되는 경우에만 수용할 수 있다.

#### 4.6.25 VT Number

- VT는 공장 출하 시 function instance 0으로 설정되지만 운전자가 구성한 function instance를 유지한다
- 같은 function instance의 VT가 여럿이거나 instance 0인 VT가 없는 충돌을 해소하기 위해, VT는 <strong>디스플레이 자체에서 function instance를 설정하는 고유 수단</strong>을 제공해야 한다. 이 수단은 VT 간 중복 instance가 생기지 않도록 보장해야 하며, 새 instance는 VT 재초기화 후에만 사용된다
- function instance 0인 VT가 <strong>primary VT</strong>다
- 설정 수단은 운전자에게 <strong>VT Number</strong>로 표현되어야 한다 — 모든 제조사의 VT가 일관된 번호 체계로 primary/secondary VT 선택을 제공하기 위함이다. Identify VT message(D.18)로 모든 VT가 자기 설정을 화면에 표시하게 할 수 있다

#### 4.6.26 패킷 패딩

정확히 8데이터 바이트로 명시 정의되지 않은 모든 VT↔ECU 메시지는 FF₁₆로 8바이트 경계까지 패딩해야 한다.

#### 4.6.27 Momentary(비래치) 수단

Momentary 수단은 운전자가 활성화하는 동안 ON이고 놓으면 자동으로 OFF로 돌아간다(Button, Key, Touch Event, Auxiliary Input control 등). 규칙:

- 활성화 시 OFF→ON 전이를 보고해야 한다
- 활성화가 유지되면 <strong>Held</strong> 상태를 보고하고, 활성화가 끝날 때까지 반복한다(타이밍 값은 각 수단의 정의에 규정)
- 활성화가 끝나면 ON/Held→OFF 전이를 보고해야 한다
- ON·Held·OFF는 일반 용어이고 수단별로 다른 용어를 쓸 수 있다(버튼은 Pressed·Held·Released)

#### 4.6.28 미지원 오브젝트

v4 이상은 일부 오브젝트의 선택적 지원을 정의한다. Working Set은 Get Supported Objects message(D.14)로 지원 오브젝트를 질의할 수 있다. 이 선택성에도 VT에는 다음 요구가 부과된다.

- Working Set은 Get Memory response가 보고한 VT 버전과 호환되게 정의된 <strong>모든 비고유 오브젝트</strong>를 담은 pool을 전송할 수 있다
- VT는 지원 목록에 없는 비고유 오브젝트도 <strong>파싱은 해야 한다</strong>(기능 지원은 안 해도 됨) — 덕분에 Working Set이 같은 pool을 여러 VT에 쓸 수 있다
- Working Set은 대상 VT가 지원하지 않는 오브젝트로 커맨드를 보내지 않는 것이 권장된다. 보내면 VT는 0이 아닌 Error Code를 실은 응답을 보낸다(구체적 코드 값은 VT 설계에 따름)

#### 4.6.29 오류 코드

커맨드 실행 중 오류가 검출되면 그 커맨드의 응답 메시지에 적용 가능한 오류 코드를 최소 1개 실어야 한다. 여러 오류가 검출되면 검출된 오류 코드 전부를 싣는 것이 권장된다.

### 4.7 한 mask에 여러 Working Set의 데이터 표시

4.7 전체는 <strong>VT version 4 이상</strong>에 적용된다. VT는 여러 Working Set의 데이터를 한 화면에 제공할 수 있고, 설계에 따라 표준 Data Mask·Soft Key Mask와 동시에 제공할 수도 있다.

<strong>최소 요구(4.7.1.2)</strong> — 이 기능은 선택 사항이지만, VT는 미지원이어도 Window Mask·Key Group object를 <strong>파싱은 해야 한다</strong>. 그래서 Working Set은 pool 수정 없이 이 오브젝트들을 모든 v4 이상 VT에 업로드할 수 있다. 지원하는 경우 최소한 Window Mask object의 "free form"(type 0)을 지원해야 하고, 다른 non-zero window mask type들도 원하는 만큼 지원할 수 있다(전 타입 구현 권장). 미지원 window mask type의 Window Mask object가 업로드되면 파싱 후 무시하며 오류를 내지 않는다. 미지원 타입은 운전자 선택 목록에 나타나지 않는다.

#### 4.7.2 User-Layout Data Mask

- VT는 임의 개수의 User-Layout Data Mask를 지원할 수 있다. 이는 <strong>VT가 소유하는 특수 Data Mask</strong>이며, VT는 운전자가 접근할 수단을 제공해야 한다
- 각 User-Layout Data Mask는 표준 Data Mask와 같은 크기이되 <strong>정확히 2열 × 6행의 Window Cell 격자</strong>로 나뉜다

#### 4.7.3~4.7.6 Window Mask object

- Working Set pool에 선택적으로 포함되는 Window Mask object를 <strong>운전자가</strong> User-Layout Data Mask 격자의 원하는 위치에 배치한다. 하나의 Window Mask는 여러 Window Cell(최대 2 × 6 전체)을 차지할 수 있다. 폭넓은 선택지를 위해 가능하면 1 × 1이 권장된다
- <strong>표현 방식(Window Type 속성)</strong>: type 0(free form)이면 Data Mask처럼 동작한다 — 콘텐츠·표현 모두 Working Set이 정의. non-zero type이면 Working Set은 특정 오브젝트 집합의 참조만 제공하고 <strong>VT가 표현을 제어</strong>한다(참조 오브젝트의 시각 서식 속성을 무시할 수 있음). 후자는 여러 제조사의 정보를 VT 안에서 일관된 look and feel로 합치기 위한 것이다
- VT는 어느 Window Mask object를 어느 Window Cell에 놓을지 선택하는 <strong>고유 매핑 수단</strong>을 제공해야 한다. 선택된 Cell에 맞지 않는 오브젝트는 선택하지 못하게 해야 하고, Cell 선택 시 그 Cell(들)에 맞는 모든 Window Mask object 목록을 제시해야 한다(단 options 속성상 available인 것만). 운전자가 정한 레이아웃은 <strong>비휘발성 메모리에 저장</strong>해 다음 전원 인가 시 복원한다. 해당 Working Set이 없으면 그 Cell은 배경색으로 블랭크 처리한다
- Window Mask의 options가 not available을 가리키면 연관 Cell을 블랭크한다. available 상태는 런타임에 바뀔 수 있다
- v4 이상이지만 User-Layout Data Mask 미지원 VT는 Window Mask object를 파싱 후 폐기하면 된다
- Window Mask object의 폭·높이는 차지하는 Window Cell(들)의 폭·높이와 같아야 한다
- <strong>Window Cell 크기</strong>: Cell 폭 = Data Mask 폭/2(내림), Cell 높이 = Data Mask 높이/6(내림). 예: 200 × 200 Data Mask면 Cell은 100 × 33, 2 × 2 Window Mask는 200 × 66
- <strong>테두리</strong>: VT는 각 Window Mask 둘레에 테두리를 그릴 수 있다(그릴지 여부는 VT 고유, 권장). 테두리 영역은 Window Mask object 전체 둘레 바깥 1픽셀을 차지하되 <strong>Window Mask 영역 안쪽에</strong> 그려진다. 따라서 free form(type 0) 사용 시 자식 오브젝트를 테두리 영역에 붙이지 않는 것이 권장된다. Window Mask 영역 밖 픽셀은 (자식 포함) 모두 클리핑된다
- <strong>스케일링</strong>: type 0이면 Window Mask와 자식의 스케일링은 전적으로 Working Set 책임이다. VT 해상도와 무관하게 종횡비는 알 수 있다(User-Layout Data Mask는 항상 2 × 6 격자, Data Mask는 항상 정사각형). non-zero type이면 레이아웃·서식·스케일링 대부분을 VT가 제어하되, Window Icon·Button 속성은 Working Set이 미리 스케일하고 VT가 추가 스케일할 수 있다

#### 4.7.7 User-Layout Data Mask 밖에서의 Window Mask 사용

VT는 제조사 설계가 지원하면 Non-VT Screen·Non-VT Area에서도 Window Mask object를 쓸 수 있다. 따라서 Working Set은 Window Mask가 User-Layout Data Mask 밖에서도 쓰일 수 있음을 인지하고, <strong>VT Status message의 소스 주소와 무관하게</strong> VT On User-Layout Hide/Show message를 모니터링해 보이는 Window Mask·키를 갱신해야 한다.

#### 4.7.8~4.7.12 User-Layout Soft Key Mask와 Key Group

- User-Layout Data Mask를 지원하는 VT는 User-Layout Data Mask당 <strong>정확히 하나의 User-Layout Soft Key Mask</strong>도 지원해야 한다. 이 역시 VT 소유의 특수 Soft Key Mask다
- User-Layout Soft Key Mask는 <strong>Key Cell</strong>들로 나뉜다(물리 Soft Key를 쓰면 물리 키당 1셀). Key Cell 수는 VT 설계 고유이고, 각 Key Cell 크기는 일반 Soft Key designator와 같다
- VT 설계자는 User-Layout Soft Key Mask당 지원 키 수를 최대 64까지 정한다. 지원 키 수가 물리 Soft Key 수를 넘으면 Soft Key Mask와 동일한 페이징 메커니즘을 제공해야 한다
- <strong>Key Group object</strong>(B.20): Working Set pool에 선택적으로 포함되며 운전자가 User-Layout Soft Key Mask에 배치한다. Key Group은 <strong>Key object 1~4개</strong>를 담고(1개가 일반적) 하나 이상의 Key Cell을 차지한다. VT는 어느 Key Group을 어느 Key Cell에 놓을지 고유 매핑 수단을 제공해야 하고, Cell 선택 시 available한 모든 Working Set의 Key Group 목록을 제시해야 한다. 운전자 레이아웃은 비휘발성 메모리에 저장·복원한다. 제공 Working Set이 없으면 할당 Cell을 블랭크한다
- Key Group의 options가 not available이면 연관 Key Cell을 블랭크해 Key가 보이지도 활성화되지도 않게 한다. available 상태는 런타임에 바뀔 수 있다
- Key는 있을 수도 없을 수도 있고 배치는 운전자 소관이므로 <strong>Window Mask object는 특정 Key Group의 존재에 의존해서는 안 된다</strong>
- Key가 어느 Working Set 소속인지 인식되도록 설계해야 한다(예: "STOP" 텍스트만 있는 Key가 3개 겹치면 혼동). 권장 레이아웃: designator 좌하단에 작업기 식별자(표준 designator 높이의 60%를 내림한 정사각형), 나머지 픽셀 전체를 Key object가 사용
- Key Cell 크기·테두리는 Soft Key Mask object와 같은 그리기 규칙을 따른다. Key Group 자식의 스케일링은 Working Set 책임이다
- VT는 User-Layout Soft Key Mask 밖(Non-VT 영역)에서도 Key Group을 쓸 수 있다 — Working Set은 VT Status의 소스 주소와 무관하게 VT On User-Layout Hide/Show message를 모니터링해 보이는 키를 갱신해야 한다

#### 4.7.13 운전자 입력(User-Layout 환경)

여러 Working Set의 입력 오브젝트가 동시에 화면에 있을 수 있다. 일반 내비게이션·입력 규칙이 적용되되 예외가 있다.

- User-Layout Data Mask 표시 중에는 <strong>어느 Working Set의 Select Input Object command도 실행되지 않는다</strong>(Data Mask 소유자가 VT이므로). VT는 오류를 표시한 Select Input Object response를 보낸다
- 내비게이션 순서는 VT 고유다
- 입력 오브젝트 이벤트에 연관된 Macro는 실행되지만, 해당 Working Set이 active가 아니므로 가시적 효과가 없을 수 있다(Macro가 조작한 오브젝트가 화면에 없거나, Data Mask를 선택하는 Change Active Mask가 무효)
- Window Mask 안의 입력 오브젝트가 활성화되면 VT는 VT Status message의 Byte 2를 FF₁₆, FE₁₆ 또는 VT 소스 주소로 설정해야 한다. Working Set Data Mask도 함께 보이는 중이면 그 mask의 "active Data Mask" 표시를 제거해야 한다(이제 VT가 active Working Set이므로). Window Mask 둘레의 active 표시 여부는 VT 고유이며, VT는 이 변경을 VT On User-Layout Hide/Show message로 Working Set에 알려야 한다

#### 4.7.14 화면 데이터 갱신

- 화면에 있는 Window Mask·Key Group의 값·오브젝트 갱신 책임은 Working Set에 있다. Working Set이 타임아웃되면 연결 관리 규칙에 따라 VT가 해당 Working Set의 Window Mask·Key Group을 화면에서 제거한다
- Working Set이 무엇이 보이는지 알 수 있도록 VT는 표시되거나 제거된 <strong>각 Window Mask·Key Group마다</strong> VT On User-Layout Hide/Show message(H.20)를 보내야 한다. VT Status message는 Window Mask·Key Group 갱신 시점 판단에 쓰이지 않는다

#### 4.7.15 Look and Feel

여러 Working Set의 Window Mask를 섞으면 정렬·색상·폰트가 제각각이라 look and feel이 무너지기 쉽다. 전략: Working Set은 VT가 렌더에 필요할 수 있는 속성의 superset을 공급하고, window type > 0이면 <strong>무엇을 어디에 표시할지는 VT가 결정</strong>한다.

- type 0이 아니면 창의 배경색·투명도는 VT가 결정한다. 필요하면 Working Set은 Get Window Mask Data message로 VT 배경색을 질의할 수 있다
- VT는 type 0이 아닌 창에서 Working Set이 공급한 오브젝트 참조의 시각 서식 속성을 무시할 수 있다
- <strong>Window Title·Window Icon</strong>: VT는 title 문자열을 창 제목으로 쓸 수 있다(서식은 VT 고유). Title과 Icon은 기능적으로 동등한 창 설명 요소로 간주되어 VT는 <strong>둘 중 하나 이상을 항상 표시</strong>해야 한다
- <strong>Window Icon 크기</strong>: Icon Area는 정사각형이고 한 변 = Window Cell 높이의 90%(내림). 예: 200 × 200 Data Mask → Cell 100 × 33 → Icon Area 29 × 29. 테두리·여백 공간이 확보된다. Working Set은 Icon Picture Graphic을 설계 시 미리 스케일하거나 런타임에 width 속성으로 스케일할 수 있다. Icon Area보다 작거나 큰 아이콘, 비정사각형 종횡비도 허용된다 — 작으면 VT가 원하는 위치에 배치 가능, 크면 중앙 정렬 후 클리핑(X·Y 각각 독립 적용). 아이콘은 표시 기능뿐 아니라 데이터 출처(Working Set)를 운전자가 알 수 있게 디자인하는 것이 권장된다
- <strong>서식(4.7.15.4)</strong>: type > 0에서 VT는 숫자·문자열 값 필드에 최소 문자 수 표시를 보장해야 하고, Working Set이 공급한 숫자 스케일링·서식 속성(options bit 1·2·3, variable reference, value, offset, scale, number of decimals, format)을 지켜야 한다. justification·색상 같은 look and feel 속성은 VT가 무시할 수 있다

#### 4.7.16 새 Window Mask·Key Group 업로드(Table 7)

런타임에 오브젝트 타입만 같으면 완전히 새 오브젝트 업로드가 허용된다(Annex C). Window Mask·Key Group에 대해 VT가 처리해야 하는 케이스:

| 이벤트 | VT 동작 |
| --- | --- |
| 단순 외관 변경(배경색·옵션·자식 변경 등)의 새 Window Mask/자식 업로드 | visible이면 refresh |
| available → not available로 바뀌는 Window Mask 업로드 | visible이면 차지 영역을 배경색으로 블랭크(화면에서 제거) |
| 크기가 줄어드는 Window Mask 업로드 | visible이면 오브젝트와 원래 차지하던 모든 cell을 refresh하고, 더 이상 안 쓰는 cell은 블랭크. 저장된 매핑을 갱신 |
| 크기가 커지는 Window Mask 업로드 | 현재 격자 위치에서 화면에 들어가는지, 확장 위치에 빈 cell이 있는지 판정. 가능하면 refresh + 매핑 갱신, 불가능하면 매핑에서 자동 제거하고 visible이었다면 원래 cell들을 블랭크 |
| window type이 바뀌는 Window Mask 업로드 | visible이면 refresh |
| 단순 외관 변경의 새 Key Group 업로드 | visible이면 refresh |
| available → not available로 바뀌는 Key Group 업로드 | 차지 영역 블랭크(제거). 다른 매핑된 Key Group 위치는 영향 없음 |
| 키 수가 줄어드는 Key Group 업로드 | visible이면 refresh하고 안 쓰는 키 위치 블랭크, 매핑 갱신. 다른 Key Group 위치 영향 없음 |
| 키 수가 늘어나는 Key Group 업로드 | 같은 페이지의 빈 키 위치로 수용 가능하면 매핑 확장 + refresh. 불가능하면 매핑에서 자동 제거하고 visible이었다면 원래 키 위치 블랭크. 다른 Key Group 위치 영향 없음 |

### 4.8 색상 제어

Working Set은 자기 pool에 적용되는 색상 팔레트를 조작해 화면 표현을 제어할 수 있다.

- 기본적으로 VT는 <strong>VT 표준 색상 팔레트</strong>(A.3)를 쓴다 — 256색이며 그중 24색은 proprietary다
- <strong>Colour Map object</strong>(v4 이상, B.17): 오브젝트의 colour 속성값 → 표준 팔레트 인덱스의 대응 관계를 바꾼다(예: 색 0과 1을 맞바꿈)
- <strong>Colour Palette object</strong>(v6 이상, B.26): 팔레트의 색 자체를 재정의한다(ARGB)
- 둘 다 <strong>그 오브젝트를 담은 object pool에만 개별 적용</strong>되며 다른 pool의 표현을 바꾸지 않는다
- VT 표준 팔레트가 정의한 초기 색상 매핑은 Working Set Special Controls object(B.29)로 오버라이드할 수 있다
- 초기화 이후 런타임의 표현 색상 변경은 Select Colour Map or Palette command(F.60)로 수행한다

## Annex A — 오브젝트·이벤트·컬러·커맨드 코드

### A.1 오브젝트 타입

VT는 Table A.1의 오브젝트 집합을 관리할 수 있어야 한다(기능적으로 지원하지 않는 오브젝트도 파싱 요구 포함). 오브젝트 타입과 Type ID:

| 분류 | 오브젝트 | Type ID | 설명 / 최소 버전 |
| --- | --- | --- | --- |
| Top level | Working Set object | 0 | 작업기 ECU(그룹)를 기술. Working Set당 정확히 1개 필수 |
| Top level | Data Mask object | 1 | 다른 오브젝트를 담는 최상위. 활성화되면 화면의 active 오브젝트 집합이 됨 |
| Top level | Alarm Mask object | 2 | 알람 표시 기술 |
| Top level | Container object | 3 | 오브젝트 그룹화 |
| Top level | Window Mask object | 34 | VT가 활성화하는 최상위 오브젝트 (v4+, 파싱만 필수) |
| Key | Soft Key Mask object | 4 | Key object들을 담는 최상위 |
| Key | Key object | 5 | Soft Key 기술 |
| Key | Button object | 6 | Button 컨트롤 기술 |
| Key | Key Group object | 35 | Key object들을 담는 최상위 (v4+, 파싱만 필수) |
| Input field | Input Boolean object | 7 | TRUE/FALSE 입력 |
| Input field | Input String object | 8 | 문자열 입력 |
| Input field | Input Number object | 9 | 정수·실수 입력 |
| Input field | Input List object | 10 | 목록에서 항목 선택 |
| Output field | Output String object | 11 | 문자열 출력 |
| Output field | Output Number object | 12 | 정수·실수 출력 |
| Output field | Output List object | 37 | 목록 항목 출력 (v4+) |
| Output shape | Output Line object | 13 | 선 |
| Output shape | Output Rectangle object | 14 | 사각형 |
| Output shape | Output Ellipse object | 15 | 타원·원 |
| Output shape | Output Polygon object | 16 | 다각형 |
| Output graphic | Output Meter object | 17 | 미터 |
| Output graphic | Output Linear Bar Graph object | 18 | 선형 바 그래프 |
| Output graphic | Output Arched Bar Graph object | 19 | 아치형 바 그래프 |
| Output graphic | Graphics Context object | 36 | 그래픽 컨텍스트 (v4+, 파싱만 필수) |
| Output graphic | Animation object | 44 | 단순 애니메이션 (v5+) |
| Picture graphic | Picture Graphic object | 20 | 비트맵 출력 |
| Picture graphic | Graphic Data object | 46 | 그래픽 이미지 데이터 정의 (v6+) |
| Picture graphic | Scaled Graphic object | 48 | 그래픽 오브젝트의 스케일 표현 (v6+) |
| Variable | Number Variable object | 21 | 32bit unsigned 정수 저장 |
| Variable | String Variable object | 22 | 고정 길이 문자열 저장 |
| Attribute | Font Attributes object | 23 | 폰트 속성 그룹(참조 전용) |
| Attribute | Line Attributes object | 24 | 선 속성 그룹(참조 전용) |
| Attribute | Fill Attributes object | 25 | 채우기 속성 그룹(참조 전용) |
| Attribute | Input Attributes object | 26 | 유효 문자 목록(입력 필드 참조 전용) |
| Attribute | Extended Input Attributes object | 38 | 유효 WideChar 목록 (v4+) |
| Attribute | Colour Map object | 39 | 색상 테이블 (v4+, 파싱만 필수) |
| Attribute | Object Label Reference List object | 40 | 오브젝트 라벨 (v4+) |
| Attribute | Colour Palette object | 45 | 색상 팔레트 (v6+) |
| Attribute | Working Set Special Controls object | 47 | 색상 맵·팔레트 특수 제어 (v6+) |
| Pointer | Object Pointer object | 27 | 다른 오브젝트 참조 |
| Pointer | External Object Definition object | 41 | 타 WS가 참조 가능한 오브젝트 나열 (v5+) |
| Pointer | External Reference NAME object | 42 | 참조 대상 WS Master 식별 (v5+) |
| Pointer | External Object Pointer object | 43 | 타 WS의 오브젝트 참조 (v5+) |
| Macro | Macro object | 28 | 이벤트에 대응해 실행할 커맨드 목록. v4+: Execute Macro command, v5+: Execute Extended Macro command |
| Auxiliary | Auxiliary Function Type 1 object | 29 | (v3+ 파싱만, 기능 미지원) |
| Auxiliary | Auxiliary Input Type 1 object | 30 | (v3+ 파싱만, 기능 미지원) |
| Auxiliary | Auxiliary Function Type 2 object | 31 | Auxiliary Function의 designator·기능 타입 (v3+) |
| Auxiliary | Auxiliary Input Type 2 object | 32 | Auxiliary Input의 designator·키 번호·기능 타입 (v3+) |
| Auxiliary | Auxiliary Control Designator Type 2 Object Pointer | 33 | Auxiliary Input/Function Type 2 참조 (v3+) |
| Proprietary | Manufacturer Defined Objects | 240~254 | 타 벤더 VT에 보내지 말 것 |
| Reserved | — | 49~239, 255 | 향후 예약 |

<strong>표기 관례(A.1.2)</strong> — Annex B 오브젝트 정의에서 쓰는 데이터 타입:

| 표기 | 의미 |
| --- | --- |
| [ ] (AID 둘레) | read-only 속성. Get Attribute Value message로만 접근. 대괄호 없는 AID는 Change Attribute command로 쓰기 가능 |
| Array | 정의된 길이의 1바이트 unsigned 정수 시퀀스 |
| Bitmask | 1바이트 논리 비트 집합. Bit 0이 항상 최하위 비트 |
| Boolean | TRUE(1)/FALSE(0), 1바이트 |
| Byte | 1바이트 정수(부호 유무 불문) |
| Float | IEEE 754-1985 32bit 부동소수점, 4바이트 |
| Integer | 1·2·4바이트 정수 |
| String | Char 또는 WideChar로 구성된 가변 길이 문자열 |
| Length | 오브젝트 크기. 항상 바이트 수 |

<strong>오브젝트 포함 관계(A.1.3, Table A.2)</strong> — pool의 오브젝트는 부모-자식 계층을 이루며, Table A.2가 부모별 허용 자식 타입과 그 조합이 허용되는 최소 VT 버전을 정의한다(이후 버전 포함). 요지:

- Working Set·Data Mask·Alarm Mask·Container·Window Mask·Key·Button·Key Group·Input List·Output List가 부모가 될 수 있고, 대부분의 출력·입력 오브젝트가 자식으로 허용된다
- Alarm Mask·Data Mask에 Container는 v2부터, 대부분 출력 오브젝트는 v2부터, Animation·Scaled Graphic 등 신오브젝트는 각각 v5·v6부터 허용된다
- 부모의 포함 규칙이 자식의 포함 규칙을 오버라이드한다. Object Pointer가 가리키는 오브젝트는 부모 계층의 포함 규칙을 위반할 수 없다

### A.2 이벤트 타입(Table A.3)

각 이벤트에는 Event ID가 부여되어 Macro object와 연관시킬 수 있다. 오브젝트별 구체적 VT 동작은 각 오브젝트의 이벤트 표에 정의된다.

| Event ID | 이벤트 | 발생 조건 |
| --- | --- | --- |
| 0 | Reserved | — |
| 1 | On activate | Working Set이 active가 될 때 |
| 2 | On deactivate | Working Set이 inactive가 될 때 |
| 3 | On show | Container: hide/show command의 show. mask: 화면에 보이게 될 때 |
| 4 | On hide | Container: hide/show command의 hide. mask: 화면에서 제거될 때 |
| N/A | On refresh | 이미 표시 중인 오브젝트가 다시 그려질 때(이 이벤트에는 Macro 연관 불가, event ID 없음) |
| 5 | On enable | 입력 오브젝트 enable(enabled 오브젝트만 내비게이션 가능). Animation object는 애니메이션 enable |
| 6 | On disable | 입력 오브젝트 disable / Animation 정지 |
| 7 | On Change Active Mask | Change Active Mask command |
| 8 | On Change Soft Key Mask | Change Soft Key Mask command |
| 9 | On Change Attribute | Change Attribute command |
| 10 | On Change Background Colour | Change Background Colour command |
| 11 | On Change Font Attributes | Change Font Attributes command |
| 12 | On Change Line Attributes | Change Line Attributes command |
| 13 | On Change Fill Attributes | Change Fill Attributes command |
| 14 | On Change Child Location | Change Child Location command |
| 15 | On Change Size | Change Size command |
| 16 | On Change Value | Change Numeric Value 또는 Change String Value command |
| 17 | On Change Priority | Change Priority command |
| 18 | On Change End Point | Change End Point command |
| 19 | On Input Field Selection | 입력 필드·Key·Button이 포커스를 받음(운전자 내비게이션 또는 Select Input Object command) |
| 20 | On Input Field Deselection | 포커스 상실 |
| 21 | On ESC | 운전자 또는 Working Set에 의한 입력 중단 |
| 22 | On entry of a value | ENTER로 입력 완료(값 변경 여부 무관) |
| 23 | On entry of a new value | ENTER로 입력 완료(값이 바뀐 경우) |
| 24 | On key press | Soft Key·Button pressed |
| 25 | On key release | Soft Key·Button released |
| 26 | On Change Child Position | Change Child Position command |
| 27 | On pointing event press (v5+) | 포인팅 이벤트를 유발하는 영역 터치·클릭 |
| 28 | On pointing event release (v5+) | 터치·클릭 해제 |
| 240~254 | Proprietary Events | 제조사 코드가 다른 ECU-VT 간 사용 금지 |
| 255 | Use Extended Macro Reference (v5+) | 이벤트가 아님 — 오브젝트의 이벤트 목록에서 발견되면 16bit Macro Object ID 참조를 뜻함 |

비고: 여러 입력 오브젝트가 같은 variable object를 참조할 때 그중 하나가 수정되면 On entry of a (new) value Macro는 <strong>수정된 입력 오브젝트에서만</strong> 실행된다. 이미 포커스를 가진 오브젝트를 운전자가 열거나 닫을 때는 On Input Field Selection Macro가 실행되지 않는다(Select Input Object command에는 "유효 커맨드는 항상 이벤트를 발생시킨다"는 4.6.22.1 규칙 적용).

### A.3 VT 표준 색상 팔레트

- 표준 팔레트는 웹 브라우저 안전 216색 팔레트 기반이다. RGB 각 성분에 00·33·66·99·CC·FF의 16진 값을 써서 6 × 6 × 6 = 216 색 큐브를 이룬다
- 인덱스 구성: 0(Black)·1(White)은 monochrome 모드용. 0~15는 16색 모드용(Black, White, Green, Teal, Maroon, Purple, Olive, Silver, Grey, Blue, Lime, Cyan, Red, Magenta, Yellow, Navy). 16~231은 정렬된 오름차순 색 큐브. <strong>232~255는 VT 설계 고유(proprietary)</strong> 확장 색이다
- 처음 16색이 팔레트 내 다른 위치에 반복되므로 256색 모드가 실제로 256개의 고유 색을 주지는 않는다
- 오브젝트 속성·비트맵 데이터의 색·픽셀 값은 이 팔레트 테이블의 인덱스다
- <strong>세 가지 색 모드</strong>(상위 모드 지원 VT는 하위 모드도 지원해야 함): monochrome(유효 색 코드 0~1), 16-colour mode(0~15, monochrome 포함 지원), 256-colour mode(0~255 전체)
- v5 이하에서 그레이스케일 구현을 택한 VT는 16·256 색 모드를 회색조로 매핑할 수 있다
- v6 이상에서는 팔레트가 색마다 <strong>알파 채널 값</strong>을 포함한다. 기본은 불투명(alpha 255)이라 v5 이하와 완전 호환되며, Working Set별로 Colour Palette object로 재정의할 수 있다. pool 로드 시 대체 색 구성이 활성화되도록 colour map·palette를 pool 안에 정의할 수도 있다(B.29). v4 이상은 active Colour Map 변경 가능(B.17, F.60)

### A.4 커맨드/파라미터 코드 요약(Table A.5)

모든 메시지와 function code. VT→ECU와 ECU→VT가 같은 function code를 공유한다(방향으로 구분). "v"는 도입 VT 버전.

<strong>Object pool 전송(Annex C)</strong>

| Function(hex) | 메시지 | 방향 | v |
| --- | --- | --- | --- |
| 11 | Object pool transfer message | ECU→VT | 2 |
| 12 | End of Object Pool message / response | ECU→VT / VT→ECU | 2 |

<strong>Technical data(Annex D)</strong>

| Function(hex) | 메시지 | v |
| --- | --- | --- |
| C0 | Get Memory message/response | 2 |
| C2 | Get Number of Soft Keys message/response | 2 |
| C3 | Get Text Font Data message/response | 2 |
| C7 | Get Hardware message/response | 2 |
| C1 | Get Supported WideChars message/response | 4 |
| C4 | Get Window Mask Data message/response | 4 |
| C5 | Get Supported Objects message/response | 4 |
| C6 | Screen Capture command/response | 6 |
| BB | Identify VT message/response | 4 |

<strong>비휘발성 메모리(Annex E)</strong>

| Function(hex) | 메시지 | v |
| --- | --- | --- |
| DF/E0 | Get Versions message / response | 2 |
| D0 | Store Version command/response | 2 |
| D1 | Load Version command/response | 2 |
| D2 | Delete Version command/response | 2 |
| D3 | Extended Get Versions message/response | 5 |
| D4 | Extended Store Version command/response | 5 |
| D5 | Extended Load Version command/response | 5 |
| D6 | Extended Delete Version command/response | 5 |

<strong>커맨드(Annex F)</strong> — Macro 허용 여부 포함(command는 대부분 Yes, response는 항상 No):

| Function(hex) | 커맨드 | Macro 허용 | v |
| --- | --- | --- | --- |
| A0 | Hide/Show Object | Yes | 2 |
| A1 | Enable/Disable Object | Yes | 2 |
| A2 | Select Input Object | Yes | 2 |
| 92 | ESC | Yes | 2 |
| A3 | Control Audio Signal | Yes | 2 |
| A4 | Set Audio Volume | Yes | 2 |
| A5 | Change Child Location | Yes | 2 |
| B4 | Change Child Position | Yes | 2 |
| A6 | Change Size | Yes | 2 |
| A7 | Change Background Colour | Yes | 2 |
| A8 | Change Numeric Value | Yes | 2 |
| B3 | Change String Value | Yes | 2 |
| A9 | Change End Point | Yes | 2 |
| AA | Change Font Attributes | Yes | 2 |
| AB | Change Line Attributes | Yes | 2 |
| AC | Change Fill Attributes | Yes | 2 |
| AD | Change Active Mask | Yes | 2 |
| AE | Change Soft Key Mask | Yes | 2 |
| AF | Change Attribute | Yes | 2 |
| B0 | Change Priority | Yes | 2 |
| B1 | Change List Item | Yes | 2 |
| B2 | Delete Object Pool | No | 2 |
| BD | Lock/Unlock Mask | Yes | 4 |
| BE | Execute Macro | Yes | 4 |
| B5 | Change Object Label | Yes | 4 |
| B6 | Change Polygon Point | Yes | 4 |
| B7 | Change Polygon Scale | Yes | 4 |
| B8 | Graphics Context | Yes | 4 |
| B9 | Get Attribute Value message/response | No | 4 |
| BA | Select Colour Map or Palette | Yes | 4 |
| BC | Execute Extended Macro | Yes | 5 |
| 90 | Select Active Working Set | Yes | 6 |

<strong>Status(Annex G)</strong>

| Function(hex) | 메시지 | 방향 | v |
| --- | --- | --- | --- |
| FE | VT Status message | VT→ECU | 2 |
| FF | Working Set Maintenance message | ECU→VT | 2 |
| FD | (VT) Unsupported VT Function message | 양방향 | 5 |

<strong>Activation(Annex H)</strong> — VT→ECU가 message, ECU→VT가 response:

| Function(hex) | 메시지 | v |
| --- | --- | --- |
| 00 | Soft Key Activation message/response | 2 |
| 01 | Button Activation message/response | 2 |
| 02 | Pointing Event message/response | 2 |
| 03 | VT Select Input Object message/response | 2 |
| 04 | VT ESC message/response | 2 |
| 05 | VT Change Numeric Value message/response | 2 |
| 06 | VT Change Active Mask message/response | 2 |
| 07 | VT Change Soft Key Mask message/response | 2 |
| 08 | VT Change String Value message/response | 2 |
| 09 | VT On User-Layout Hide/Show message/response | 4 |
| 0A | VT Control Audio Signal Termination message | 4 |

<strong>Auxiliary control(Annex J)</strong>

| Function(hex) | 메시지 | v |
| --- | --- | --- |
| 20 | Auxiliary Assignment Type 1 command/response | 2 |
| 21 | Auxiliary Input Type 1 status | 2 |
| 24 | Auxiliary Assignment Type 2 command/response | 3 |
| 22 | Preferred Assignment command/response | 3 |
| 26 | Auxiliary Input Type 2 Status message | 3 |
| 23 | Auxiliary Input Type 2 Maintenance message | 3 |
| 25 | Auxiliary Input Status Type 2 Enable command/response | 3 |
| 27 | Auxiliary Capabilities request/response | 5 |

function code 60₁₆~7F₁₆은 Proprietary Command 영역이고, 나머지 미정의 코드는 예약이다.

## Annex B — 오브젝트 정의

Annex B는 각 오브젝트의 허용 커맨드, 이벤트별 VT 동작, 속성·레코드 포맷을 정의한다. 공통 패턴:

- 모든 오브젝트 레코드는 Object ID(2바이트) + Type(1바이트)으로 시작한다
- AID가 대괄호로 표기된 속성은 read-only(Get Attribute Value로만 조회), 아니면 Change Attribute로 변경 가능
- 자식 목록은 "Number of objects to follow" 뒤에 {Object ID(2) + X Location(2, signed) + Y Location(2, signed)} 6바이트 레코드가 반복되는 형태다(위치는 부모 좌상단 기준 상대 좌표)
- Macro 참조는 "Number of macros to follow" 뒤에 {Event ID(1) + Macro ID(1)} 2바이트 그룹이 반복된다. v5 이상에서 16bit Macro ID 참조는 그룹 2개를 쓰며 이 카운트에서 2로 센다

### B.1 Working Set object (Type 0)

Working Set을 기술한다. pool당 정확히 1개 제공해야 하며, Soft Key designator 안에 들어가는 식별용 오브젝트를 하나 이상 포함해야 한다. VT는 통신 알람·Auxiliary Control 설정 등 Working Set 식별이 필요한 곳에 이 designator를 쓸 수 있다. <strong>이 오브젝트의 활성화는 VT만 할 수 있으며</strong>, 활성화되면 해당 Working Set이 VT를 "소유"한다.

허용 커맨드: Change Active Mask, Change Background Colour, Change Child Location, Change Child Position, Get Attribute Value.

주요 이벤트: On Activate(운전자가 이 WS 선택 — 현재 WS에 deactivate 이벤트, 이 WS의 active Data Mask에 show 이벤트, VT Status message), On Deactivate, On Change Active Mask(active mask 속성 변경, active WS면 기존 mask hide + 새 mask show), On Change Background Colour / Child Location / Child Position(designator가 보이면 지우고 refresh).

| 속성 | AID | 크기 | 값 | 설명 |
| --- | --- | --- | --- | --- |
| Object ID | | 2 | 0~65534 | pool 내 유일 |
| Type | [0] | 1 | =0 | |
| Background colour | [1] | 1 | 0~255 | 배경색 |
| Selectable | [2] | 1 | 0/1 | 운전자가 이 WS를 선택 가능한지. v6는 Selectable=0이어도 Alarm Mask 지원(4.6.14). v5 이하는 이 경우 정의가 불명확했음 |
| Active mask | [3] | 2 | 0~65534 | active(또는 visible)일 때 표시할 Data/Alarm Mask의 Object ID. v6 호환 WS는 selectable이 아니어도 유효한 mask를 참조해야 함. v5 이하 호환 WS는 Selectable=0이면 이 속성 무시(범위 검증 안 함) |
| Number of objects / macros / languages to follow | | 각 1 | | 이어지는 designator 오브젝트·Macro 참조·언어 코드 수 |
| {Object ID, X, Y} 반복 | | 6 | | designator 구성 오브젝트(전체가 Soft Key designator 안에 들어가야 하며 밖은 클리핑) |
| {Event ID, Macro ID} 반복 | | 2 | | Macro 참조 |
| {Language Code} 반복 | | 2 | | 지원 언어 2글자 코드(ISO 639. 단 ISO 639 변경 대비 a-z·A-Z 전 조합 수용) |

### B.2 Data Mask object (Type 1)

Data Mask 영역에 나타날 오브젝트들을 기술한다. Data Mask 크기는 VT가 정의하고 Working Set은 Get Hardware message로 얻는다.

허용 커맨드: Change Background Colour, Change Child Location, Change Child Position, Change Soft Key Mask, Change Attribute, Get Attribute Value.

주요 이벤트 동작: On Show(배경색으로 채우고 자식들을 나열 순서로 그림, 연관 Soft Key Mask show, VT Status message), On Hide(연관 Soft Key Mask hide), On Refresh(손상된 오브젝트 다시 그림), On Change Soft Key Mask(visible이면 기존 Soft Key Mask hide + 새 것 show, visible이면 VT Status message), On Pointing Event press/release(Pointing Event message).

| 속성 | AID | 크기 | 값 | 설명 |
| --- | --- | --- | --- | --- |
| Object ID | | 2 | 0~65534 | |
| Type | [0] | 1 | =1 | |
| Background colour | 1 | 1 | 0~255 | 쓰기 가능 |
| Soft Key Mask | 2 | 2 | 0~65534, 65535 | 연관 Soft Key Mask의 Object ID. 이 Data Mask가 표시되면 함께 표시. NULL이면 Soft Key 없음(designator 클리어 권장) |
| Number of objects / macros | | 각 1 | | |
| {Object ID, X, Y} 반복 | | 6 | | 포함 오브젝트(위치는 Data Mask 좌상단 기준) |
| {Event ID, Macro ID} 반복 | | 2 | | |

### B.3 Alarm Mask object (Type 2)

동작은 4.6.14 참조. 허용 커맨드는 Data Mask와 같고 Change Priority command가 추가된다.

특유 이벤트: On Change Priority — 이 mask가 해당 WS의 현재 mask이면 알람 우선순위를 재평가한다. (a) 이 Alarm Mask가 visible인데 더 이상 최고 우선순위가 아니면 이 WS를 비활성화하고 최고 우선순위 알람의 WS를 활성화, (b) visible이 아닌데 최고 우선순위가 되면 현재 WS를 비활성화하고 이 WS를 활성화.

| 속성 | AID | 크기 | 값 | 설명 |
| --- | --- | --- | --- | --- |
| Object ID | | 2 | 0~65534 | |
| Type | [0] | 1 | =2 | |
| Background colour | 1 | 1 | 0~255 | |
| Soft Key Mask | 2 | 2 | 0~65534, 65535 | 연관 Soft Key Mask(NULL이면 designator 클리어) |
| Priority | 3 | 1 | 0~2 | 0 = High(운전자 위험·긴급 고장), 1 = Medium(일반 알람·기계 고장), 2 = Low(정보성) |
| Acoustic signal | 4 | 1 | 0~3 | 0 = 최고 우선순위 음, 1 = 중간, 2 = 최저, 3 = none(무음) |
| Number of objects / macros, 자식·Macro 반복 | | | | Data Mask와 동일 구조 |

### B.4 Container object (Type 3)

오브젝트 그룹을 이동·숨김·공유하기 위한 논리적 그룹. <strong>컨테이너 자체는 보이는 오브젝트가 아니다.</strong> mask와 달리 런타임에 Working Set 제어로 hide/show할 수 있다. 겹침 판정을 돕기 위해 크기 한계가 정의된다.

허용 커맨드: Hide/Show Object, Change Child Location, Change Child Position, Change Size, Get Attribute Value.

주요 이벤트: On Show(이미 visible이어도 show command로 트리거 — 자식을 나열 순서로 그리고 부모 mask refresh, Hide/Show command로 유발된 경우에만 response), On Hide(mask 배경색으로 다시 그리고 부모 mask refresh), On Change Size(자식들을 배경색으로 지우고 refresh).

| 속성 | AID | 크기 | 값 | 설명 |
| --- | --- | --- | --- | --- |
| Object ID | | 2 | 0~65534 | |
| Type | [0] | 1 | =3 | |
| Width / Height | [1]/[2] | 각 2 | 0~65535 | 컨테이너 영역 최대 크기(픽셀). 영역 밖 자식은 클리핑 |
| Hidden | [3] | 1 | 0/1 | TRUE = 컨테이너와 자식이 숨겨짐 |
| Number of objects / macros, 자식·Macro 반복 | | | | 공통 구조 |

### B.5 Soft Key Mask object (Type 4)

Key object·Object Pointer·External Object Pointer를 담는 컨테이너. Pointer는 NULL 또는 Key object로만 해석되어야 한다. Key는 나열 순서로 물리 Soft Key에 할당된다. Key가 하나도 없는 Soft Key Mask도 허용된다(이 mask 활성화로 모든 Soft Key를 사실상 비활성화).

- NULL Object ID를 가리키는 Pointer는 Soft Key 자리를 예약한다(나머지 Key가 앞으로 당겨지지 않고, 뒤쪽 Key로 내비게이션 가능). 목록 끝의 NULL Pointer는 표시하지 않으며 페이징 계산에서 제외한다. Pointer 값을 NULL로/에서 바꾸면 런타임에 페이징 요구가 동적으로 변할 수 있다

허용 커맨드: Change Background Colour, Change Attribute, Get Attribute Value.

| 속성 | AID | 크기 | 값 | 설명 |
| --- | --- | --- | --- | --- |
| Object ID | | 2 | 0~65534 | |
| Type | [0] | 1 | =4 | |
| Background colour | 1 | 1 | 0~255 | Key object 자체의 배경색 속성이 이를 오버라이드 |
| Number of objects / macros | | 각 1 | | |
| {Object ID} 반복 | | 2 | | 포함 Key(위치 좌표 없음 — designator 순서 할당) |
| {Event ID, Macro ID} 반복 | | 2 | | |

### B.6 Key object (Type 5)

Soft Key의 designator와 key code를 정의한다. designator 밖의 오브젝트는 클리핑된다.

허용 커맨드: Select Input Object(v4+), Change Background Colour, Change Child Location, Change Child Position, Change Attribute, Get Attribute Value.

주요 이벤트: On Key Press / On Key Release(운전자가 Soft Key를 누르고 뗌 → Soft Key Activation message), On Input Field Selection/De-selection(v4+, 포커스 획득·상실 — VT는 Key가 선택됐음을 운전자가 알 수 있게 표시).

| 속성 | AID | 크기 | 값 | 설명 |
| --- | --- | --- | --- | --- |
| Object ID | | 2 | 0~65534 | |
| Type | [0] | 1 | =5 | |
| Background colour | 1 | 1 | 0~255 | |
| Key code | 2 | 1 | 1~255 | Soft Key Activation message에 보고되는 코드. <strong>0은 ACK 수단 전용으로 예약</strong> |
| Number of objects / macros, 자식·Macro 반복 | | | | 공통 구조(위치는 designator 좌상단 기준) |

### B.7 Button object (Type 6)

버튼 컨트롤을 정의한다. 주로 터치스크린·포인팅 지원 VT용이지만 <strong>모든 VT가 지원해야 한다</strong> — 터치·포인팅이 없으면 Button으로 내비게이션할 수단을 제공해야 한다. 활성화되면 VT가 Button Activation message를 Master에게 보낸다. VT는 options에 따라 Button의 선택(포커스)·pressed·latched 상태를 표시해야 한다.

<strong>Button의 3요소 구조</strong>

| 요소 | 정의 |
| --- | --- |
| Button Area | width·height 속성이 정의하는 전체 영역 |
| Button Face | 배경색이 칠해지고 자식 오브젝트가 배치되는 영역. 자식은 Face의 폭·높이로 클리핑된다. Face는 Button Area보다 폭·높이 각각 <strong>8픽셀 작다</strong>(Options의 No border 비트가 TRUE면 Area 전체로 확장) |
| Button Border | VT 고유의 8픽셀 영역. border colour 속성 기반으로 렌더되나 위치·변별 폭·색 특성(투명도·색조 등) 표현은 VT 고유(표준 팔레트 밖 색도 가능). 따라서 Area 안에서 Face의 오프셋은 VT 고유다((0,0)~(8,8)). Suppress border 비트로 숨기고 No border 비트로 제거할 수 있다 |

허용 커맨드: Enable/Disable Object(v4+), Select Input Object(v4+), Change Background Colour, Change Size, Change Child Location, Change Child Position, Change Attribute, Get Attribute Value.

주요 이벤트: On Enable/Disable(disabled면 선택 불가, VT는 disabled임을 명확히 표시), On Input Field Selection/De-selection, On Key Press/Release(운전자 활성화 또는 latchable Button 상태를 바꾸는 Change Attribute → Button Activation message는 운전자 조작 시에만 전송).

| 속성 | AID | 크기 | 값 | 설명 |
| --- | --- | --- | --- | --- |
| Object ID | | 2 | 0~65534 | |
| Type | [0] | 1 | =6 | |
| Width / Height | 1 / 2 | 각 2 | 0~65535 | Button Area 최대 크기(픽셀) |
| Background colour | 3 | 1 | 0~255 | |
| Border colour | 4 | 1 | 0~255 | |
| Key Code | 5 | 1 | 0~255 | Button Activation message에 보고되는 코드 |
| Options | 6 (v4+) | 1 | bitmask | 아래 참조 |
| Number of objects / macros, 자식·Macro 반복 | | | | 자식 위치는 Button <strong>안쪽(inner) 좌상단</strong> 기준. inner border 밖은 클리핑 |

Options 비트:

| Bit | 의미 |
| --- | --- |
| 0 | Latchable. TRUE면 다음 활성화까지 눌린 상태 유지, FALSE면 momentary. <strong>런타임 Change Attribute로 변경 불가</strong>(변경은 무시됨) |
| 1 | latchable Button의 현재 상태(0 = released, 1 = latched). momentary에서는 무시 |
| 2 | Suppress border. TRUE면 테두리를 그리지 않음(Face 위치는 유지) |
| 3 | Transparent Background. TRUE면 내부 배경이 항상 투명(배경색 속성 미사용) (v4+) |
| 4 | Disabled. TRUE면 disabled로 그려지고 선택·활성화 불가 (v4+) |
| 5 | No border. TRUE면 Bit 2 무시, 테두리를 절대 그리지 않고 Face가 Button Area 전체로 확장 (v4+) |

momentary Button + 비트 2·3·5 + 런타임 외관 변경을 조합하면 "radio button" 류 동작을 구현할 수 있다.

### B.8 입력 필드 오브젝트

Boolean·String·Number·List 4종. <strong>VT는 입력 필드 둘레에 테두리를 그리지 않는다.</strong> 입력 오브젝트의 3상태: hidden(표시 안 됨), shown+enabled(표시·입력 가능), shown+disabled(표시·입력 불가). show/hide 속성이 없으므로 숨기려면 Container나 Object Pointer에 담아야 한다.

공통 허용 커맨드: Enable/Disable Object, Select Input Object, ESC, Change Background Colour(Input List 제외), Change Numeric Value(Input String 제외), Change String Value(Input String만), Change Attribute, Change Size, Get Attribute Value.

공통 이벤트(Table B.15): On Enable/Disable, On Input Field Selection/De-selection, <strong>On ESC</strong>(운전자 ESC 키 또는 WS의 ESC command — real-time editing이 아니면 값을 입력 시작 전 값으로 되돌리고 다시 그림 → VT ESC message 또는 ESC response), On Change Value(커맨드로 값 변경 — 표시 중이면 새 값으로 다시 그리고 부모 refresh), <strong>On Entry of Value</strong>(ENTER로 저장, 값 변경 무관 — VT Change Numeric/String Value message로 WS 갱신), On Entry of New Value(값이 바뀐 경우 — 추가 통지는 없음).

#### B.8.2 Input Boolean object (Type 7)

TRUE/FALSE 입력(예: 체크박스). 그래픽 오브젝트이며 값 > 0일 때 표시기 모양은 VT 재량이되 width 속성의 정사각 영역에 맞아야 한다. 값 0이면 영역이 배경색, 값 > 0이면 배경 위에 전경색으로 표시기를 그린다. v4 이상은 값 > 0 전부를 TRUE 표시로 그리고, 값 변경 시 VT는 {0, 1} 값으로 WS에 알린다(v3 이하는 {0,1} 외 값의 표현이 불명확했음).

| 속성 | AID | 크기 | 값 | 설명 |
| --- | --- | --- | --- | --- |
| Object ID / Type | / [0] | 2/1 | =7 | |
| Background colour | 1 | 1 | 0~255 | |
| Width | 2 | 2 | 0~65535 | 입력 필드 폭이자 높이(정사각형) |
| Foreground colour | 3 | 2 | 0~65534 | <strong>Font Attributes object의 Object ID</strong> — 유효 속성은 font colour뿐 |
| Variable reference | 4 | 2 | 0~65534, 65535 | 값을 저장·조회할 Number Variable의 Object ID. NULL이면 value 속성에 직접 저장 |
| Value | [5] | 1 | 0, 1~255 | variable reference가 NULL일 때만 사용 |
| Enabled | [6] (v4+) | 1 | 0/1 | 현재 상태 |
| Macro 참조 | | | | 공통 구조 |

#### B.8.3 Input String object (Type 8)

문자열 입력. 표시 가능 문자는 Annex K, 특수 서식 문자는 4.6.19.6 규칙대로 해석해야 한다.

| 속성 | AID | 크기 | 값 | 설명 |
| --- | --- | --- | --- | --- |
| Object ID / Type | / [0] | 2/1 | =8 | |
| Width / Height | 1 / 2 | 각 2 | 0~65535 | 영역 밖 클리핑 |
| Background colour | 3 | 1 | 0~255 | options의 Transparent 비트가 0일 때만 사용. Width × Height 전체 사각형에 적용 |
| Font attributes | 4 | 2 | 0~65534 | 서식용 Font Attributes object |
| Input attributes | 5 | 2 | 0~65534, 65535 | 문자 검증용 Input Attributes 또는 Extended Input Attributes object. NULL이면 검증 없음. 참조 오브젝트와 문자열 값의 타입(8-bit ↔ Input Attributes, WideString ↔ Extended Input Attributes)이 일치해야 하며, 다르면 검증하지 않음 |
| Options | 6 | 1 | bitmask | Bit 0 = Transparent(배경 투과), Bit 1 = Auto-Wrap, Bit 2 = Wrap on Hyphen(v4+, Auto-Wrap TRUE일 때만 적용) |
| Variable reference | 7 | 2 | 0~65534, 65535 | String Variable object ID. NULL이 아니면 Length·Value 속성은 사용하지 않음. v3 이하에서는 이 경우 Length를 0으로 설정해야 함 |
| Justification | 8 | 1 | 0~15 (v4+) | Bits 0–1 수평: 0 = Left, 1 = Middle, 2 = Right. Bits 2–3 수직(v4+): 0 = Top, 1 = Middle, 2 = Bottom. 입력 중 justification 보류는 VT 재량 |
| Length | | 1 | 0~255 | 값의 최대 고정 길이(바이트). variable reference 사용 시 0 가능. 참조 변수는 255바이트 초과 금지(VT Change String Value message의 length 필드가 1바이트이므로) |
| Value | | Length | String | variable reference가 NULL일 때만. Length 크기를 항상 채워야 하며(공백 패딩) 8-bit·WideString 모두 가능. <strong>VT는 문자열 타입을 바꿀 수 없고</strong> Working Set은 바꿀 수 있음 |
| Enabled | [9] (v4+) | 1 | 0/1 | |
| Macro 참조 | | | | 공통 구조 |

#### B.8.4 Input Number object (Type 9)

정수 raw 값에 스케일을 적용해 서식화·표시·변경한다. 핵심 수식:

- 표시 값 = (value 속성 + Offset) × Scaling Factor — <strong>값이 min/max 범위 밖이어도 이 수식으로 표시</strong>한다
- options에 따라 표시 값은 Number of decimals 자리로 절사(truncate) 또는 반올림된다. 반올림 오차 최소화를 위해 double precision 연산 구현이 권장된다
- ENTER로 입력을 닫을 때 VT는 (Min + Offset) × Scale ≤ 새 값 ≤ (Max + Offset) × Scale일 때만 수용한다. 아니면 ENTER를 무시하고 입력을 연 상태로 유지한다
- 수용 시: value 속성(또는 참조 변수) = 새 값/Scaling Factor − Offset
- 운전자는 min/max 밖 값을 입력할 수 없지만 <strong>Working Set은</strong> pool 업로드나 Change Numeric Value command로 임의 값을 설정할 수 있다

| 속성 | AID | 크기 | 값 | 설명 |
| --- | --- | --- | --- | --- |
| Object ID / Type | / [0] | 2/1 | =9 | |
| Width / Height | 1 / 2 | 각 2 | 0~65535 | |
| Background colour | 3 | 1 | 0~255 | Transparent 비트가 0일 때만 |
| Font attributes | 4 | 2 | 0~65534 | |
| Options | 5 | 1 | bitmask | Bit 0 = Transparent. Bit 1 = Display leading zeros(필드 폭까지 왼쪽을 0으로 채운 뒤 justification 적용). Bit 2 = Display zero as blank(표시 값이 정확히 0일 때만 빈 필드). Bit 3 = Truncate(TRUE면 소수 자리 절사, FALSE면 반올림)(v4+, v3 이전엔 미정의). 빈 필드가 아니면 소수점 앞에 항상 최소 1자리 표시(예: 2, 0.2). 설계자는 단항 마이너스 기호와 leading zero·필드 폭을 감안해야 함 |
| Variable reference | 6 | 2 | 0~65534, 65535 | Number Variable object ID(raw unscaled 값 저장). NULL이면 value 속성 사용. VT는 raw unscaled 값을 WS에 전송 |
| Value | [14] | 4 | 0~2³²−1 | 스케일 전 raw unsigned 값 |
| Min value / Max value | 7 / 8 | 각 4 | 0~2³²−1 | raw 최소·최대(실제 한계는 Offset·Scale 적용 후) |
| Offset | 9 | 4 | −2³¹~2³¹−1 | signed. 입력 값·min/max에 적용 |
| Scale | 10 | 4 | Float | 입력 값·min/max에 적용 |
| Number of decimals | 11 | 1 | 0~7 | 소수점 뒤 표시 자리수 |
| Format | 12 | 1 | 0/1 | 0 = 고정 소수(####.nn), 1 = 지수([-]###.nnE[±]##). n은 Number of decimals |
| Justification | 13 | 1 | 0~15 (v4+) | Input String과 동일 인코딩 |
| Options 2 | [15] (v4+) | 1 | bitmask | Bit 0 = Enabled. Bit 1 = real time editing(TRUE면 변경 중 값을 Master로 전송, 4.2 참조) |
| Macro 참조 | | | | 공통 구조 |

#### B.8.5 Input List object (Type 10)

오브젝트 집합 중 하나를 표시하고 운전자가 하나를 선택하게 한다. 표시할 오브젝트는 Value 속성 또는 Variable reference가 정한다.

- 구현·외관은 VT 고유(+/− 키 순회, 스크롤바 팝업 리스트 등). 편집용으로 열려 있지 않으면 현재 값만 표시하며 width·height는 표시 값 영역만 정의한다
- Master에 전송되는 값은 선택된 <strong>리스트 인덱스</strong>(0~254)다. <strong>255 = 항목 미선택</strong>(v3 이하에서는 미정의였음). CF는 미선택 표시 목적으로 255를 설정할 수 있으나 운전자가 255나 무효 인덱스(항목 수 − 1 초과)를 선택하는 것은 허용되지 않는다. 단 number variable 참조 시 WS나 다른 입력 오브젝트를 통해 무효 인덱스 값이 들어갈 수는 있다
- 리스트 항목이 NULL 값 Object Pointer이거나 hidden 상태 Container면 <strong>빈 오브젝트</strong>로 간주된다 — 표시 리스트에서 자리를 차지하고 내용 없이도 선택 가능하다
- 리스트 항목의 Object ID가 NULL이면 <strong>보이지 않는 오브젝트</strong>다 — 표시 리스트에서 자리를 차지하지 않고 선택 불가하나, 인덱스 계산에는 포함되어 리스트 내 위치를 유지한다
- 다음 경우 VT는 선택 항목에 아무것도 표시하지 않는다: 인덱스 255, 무효 인덱스, NULL placeholder 항목, NULL 값 Object Pointer 항목, hidden Container 항목

허용 커맨드: Enable/Disable Object, Select Input Object, ESC, Change Numeric Value, Change Attribute, Change List Item, Change Size, Get Attribute Value.

| 속성 | AID | 크기 | 값 | 설명 |
| --- | --- | --- | --- | --- |
| Object ID / Type | / [0] | 2/1 | =10 | |
| Width / Height | 1 / 2 | 각 2 | 0~65535 | |
| Variable reference | 3 | 2 | 0~65534, 65535 | Number Variable object ID. NULL이면 value 속성 사용 |
| Value | [4] | 1 | 0~254, 255 | 선택된 리스트 인덱스(첫 항목 = 0). 255 = 미선택 |
| Number of list items | | 1 | 0~255 | 이어지는 오브젝트 참조 수. <strong>리스트 크기는 이 수를 초과할 수 없고 이 속성은 변경 불가</strong> |
| Options | [5] (v4+) | 1 | bitmask | Bit 0 = Enabled, Bit 1 = real time editing |
| {Object ID} 반복 | | 2 | 0~65534, 65535 | 리스트 구성 오브젝트. NULL = placeholder(보이지 않는 항목). Change List Item command로 교체·제거 가능 |
| Macro 참조 | | | | 공통 구조 |

### B.9 출력 필드 오브젝트(개요)

출력 필드는 string·number·list 3종으로, 서로 유사한 관계·동작을 갖되 속성이 다르다. 공통 허용 커맨드: Change Background Colour, Change Numeric Value(Output String 제외), Change String Value(Output String만), Change Attribute, Change Size, Get Attribute Value. (세부 정의는 문서 114페이지 이후 — 다음 담당 범위에서 이어짐)

## B.9 Output field 오브젝트

### B.9.1 개요

Output field는 문자열(Output String), 숫자(Output Number), 리스트(Output List) 세 종류가 있다. 세 오브젝트는 관계와 동작이 비슷하고 속성만 다르다. Input field와 달리 오퍼레이터 입력을 받지 않는 표시 전용 오브젝트다.

공통 허용 명령: Change Background Colour, Change Numeric Value(Output String 제외), Change String Value(Output String 전용), Change Attribute, Change Size, Get Attribute Value. Output List는 추가로 Change List Item을 허용한다.

Output field 공통 이벤트는 다음과 같다.

| 이벤트 | 발생 원인 | VT 동작 | 응답 메시지 |
|---|---|---|---|
| On Refresh | Data Mask Refresh 조건 | 오브젝트 재그리기 | — |
| On Change Background Colour | Change Background Colour 명령 | 배경색 채운 뒤 새 배경색으로 재그리기 | Change Background Colour Response |
| On Change Value | Change Numeric/String Value 명령 | 새 값으로 재그리기, 부모 갱신 | Change Numeric/String Value response |
| On Change Attribute | Change Attribute 명령 | 표시 중이면 재그리기, 부모 갱신 | Change Attribute response |
| On Change Size | Change Size 명령 | 현재 위치를 배경색으로 지우고 부모 마스크 갱신 | Change Size response |

:::info 매크로 레코드 공통 구조
Annex B의 거의 모든 오브젝트 레코드는 끝부분에 <strong>Number of macros to follow</strong>(1바이트) + {Event ID(1), Macro ID(1)} 반복 쌍을 가진다. 지정된 이벤트가 발생하면 연결된 Macro가 실행된다. VT version 5 이상에서 16-bit Object ID를 가진 Macro를 참조하면 이 카운트에서 참조 2개로 계산하며, Event ID 자리에는 이벤트 타입 또는 0xFF, Macro ID 자리에는 Macro Object ID의 하위/상위 바이트가 들어간다. 이하 각 오브젝트 표에서는 이 공통 매크로 필드를 생략한다.
:::

### B.9.2 Output String object (Type 11)

텍스트 문자열을 출력한다. 표시 가능한 문자는 Annex K의 코드플레인 표를 따르고, 값 안에 특수 포맷팅 문자(개행 등)를 넣을 수 있으며 VT가 4.6.19.6 규칙대로 해석한다.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID | — | 2 | 0~65534 | 오브젝트 풀 내 유일 식별자 |
| Type | [0] | 1 | =11 | Output String |
| Width | 1 | 2 | 0~65535 | 필드 최대 폭(픽셀). 벗어나는 부분은 클리핑 |
| Height | 2 | 2 | 0~65535 | 필드 최대 높이(픽셀) |
| Background colour | 3 | 1 | 0~255 | Options의 transparent 비트가 0일 때만 사용 |
| Font attributes | 4 | 2 | 0~65534 | 표시에 쓸 Font Attributes 오브젝트 ID |
| Options | 5 | 1 | 비트마스크 | Bit 0 = Transparent, Bit 1 = Auto-Wrap, Bit 2 = Wrap on Hyphen(v4+, Auto-Wrap이 TRUE일 때만 유효) |
| Variable reference | 6 | 2 | 0~65534, 65535 | 값을 가져올 String Variable의 ID. NULL(65535)이면 Value 속성에 직접 저장. NULL이 아니면 Length·Value 속성은 무시 |
| Justification | 7 | 1 | 0~2ᵃ / 0~15ᵇ | Bit 0–1 수평(0=Left, 1=Middle, 2=Right), Bit 2–3 수직(0=Top, 1=Middle, 2=Bottom, v4+). 정렬은 픽셀 단위 그래픽 기준 |
| Length | — | 2 | 0~65535 | Value의 고정 길이(바이트). variable reference 사용 시 0 가능 |
| Value | — | Length | — | 출력할 문자열. Length만큼 공백 패딩 필요. 8-bit 또는 WideString 가능 |

ᵃ VT v3 이하, ᵇ VT v4 이상. (v3 이하에서 Variable reference가 NULL이 아니면 Length는 0이어야 한다.)

### B.9.3 Output Number object (Type 12)

정수 원시값을 받아 포맷해 출력한다. 표시값 계산식은 다음과 같다.

```
표시값 = (value + Offset) × Scale
```

Options에 따라 표시값을 "Number of decimals" 자리수로 절사(truncate)하거나 반올림한다. 반올림 오차를 줄이기 위해 VT는 배정밀도(double) 연산을 구현하는 것이 권장된다.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =12 | Output Number |
| Width, Height | 1, 2 | 각 2 | 0~65535 | 필드 크기(픽셀), 초과분 클리핑 |
| Background colour | 3 | 1 | 0~255 | transparent가 아닐 때 사용 |
| Font attributes | 4 | 2 | 0~65534 | Font Attributes 오브젝트 ID |
| Options | 5 | 1 | 비트마스크 | Bit 0 = Transparent, Bit 1 = 선행 0 표시(필드 폭까지 0 채운 뒤 정렬), Bit 2 = 값이 정확히 0이면 빈 필드 표시, Bit 3 = Truncate(TRUE면 절사, FALSE면 반올림, v4+) |
| Variable reference | 6 | 2 | 0~65534, 65535 | 원시값을 가져올 Number Variable ID. NULL이면 Value 속성 사용 |
| Value | [12] | 4 | 0~2³²−1 | 스케일 전 원시값(unsigned 32-bit). variable reference가 NULL일 때만 사용 |
| Offset | 7 | 4 | −2³¹~2³¹−1 | 표시용 오프셋(signed 32-bit) |
| Scale | 8 | 4 | float | 표시용 배율 |
| Number of decimals | 9 | 1 | 0~7 | 소수점 이하 표시 자리수 |
| Format | 10 | 1 | 0/1 | 0 = 고정소수(####.nn), 1 = 지수 표기([−]###.nnE[+/−]##) |
| Justification | 11 | 1 | 0~2ᵃ/0~15ᵇ | Output String과 동일한 수평/수직 정렬 비트 |

빈 필드 옵션이 꺼져 있으면 VT는 소수점 앞에 항상 최소 한 자리 숫자를 표시한다(예: 2,2 → 0,2).

### B.9.4 Output List object (Type 37)

VT version 4에서 추가된 오브젝트로, 오브젝트 집합 중 하나를 골라 표시한다. 표시 대상은 Value 속성 또는 Variable reference가 가리키는 값(리스트 인덱스)으로 결정된다. Input List의 출력 전용 판이라 보면 된다.

다음 경우 VT는 아무것도 표시하지 않는다.

- 인덱스가 255("no item chosen")인 경우
- 인덱스가 유효 범위를 벗어난 경우(항목 수 − 1 초과)
- 선택된 항목이 no-item placeholder(NULL)인 경우
- 선택된 항목이 값이 NULL인 Object Pointer인 경우
- 선택된 항목이 hidden 상태의 Container인 경우

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =37 | Output List |
| Width, Height | 1, 2 | 각 2 | 0~65535 | 필드 크기, 초과분 클리핑 |
| Variable reference | 3 | 2 | 0~65534, 65535 | 인덱스를 담은 Number Variable ID. NULL이면 Value 사용 |
| Value | [4] | 1 | 0~254, 255 | 선택된 리스트 인덱스. 첫 항목이 0, 255는 미선택 |
| Number of list items | — | 1 | 0~255 | 뒤따르는 오브젝트 참조 수. 리스트 크기의 상한이며 변경 불가 |
| Repeat: {Object ID} | — | 각 2 | 0~65534, 65535 | 리스트 구성 오브젝트. NULL은 no-item placeholder. Change List Item 명령으로 교체·제거 가능 |

이벤트는 On Refresh, On Change Value(Change Numeric Value로 인덱스 변경), On Change Attribute, On Change Size로 Output field 공통 패턴과 같다.

## B.10 Output shape 오브젝트

### B.10.1 개요

도형 출력 오브젝트는 line, rectangle, ellipse, polygon 네 종류다. 도형의 점은 정사각형 "paintbrush"로 그리는데, 실제 점이 브러시의 좌상단 모서리에 오도록 찍거나, 선 방향에 맞춰 브러시를 회전시켜 더 매끈한 선을 만들 수도 있다. 안티앨리어싱도 허용된다.

- 브러시 폭 = Line Attributes의 line width 속성. 폭 0인 선은 그리지 않는다.
- 끝점은 부모 오브젝트의 X-Y 시작 위치 기준 상대 좌표다.
- 선 폭이 1픽셀보다 크면 선 두께를 안쪽·바깥쪽·중앙 어느 쪽으로 키워도 되지만, 오브젝트의 클리핑 영역을 벗어나 잘린 선이 생기면 안 된다.
- 끝점은 둘러싼 사각형이 정의한 선 길이 밖에 그리면 안 되고, ellipse의 segment/section 타입과 polygon에서는 인접 선이 한 점에서 만나야 한다.

### B.10.2 Output Line object (Type 13)

선 하나를 출력한다. 시작점은 부모 오브젝트가 정한 위치다. 허용 명령: Change End Point, Change Attribute, Change Size, Get Attribute Value.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =13 | Output Line |
| Line attributes | 1 | 2 | 0~65534 | Line Attributes 오브젝트 ID |
| Width | 2 | 2 | 0~65535 | 둘러싼 가상 사각형 폭(픽셀). X + Width − 1, Y + Height − 1이 클리핑 한계 |
| Height | 3 | 2 | 0~65535 | 둘러싼 가상 사각형 높이(픽셀) |
| Line Direction | 4 | 1 | 0/1 | 선 그리는 방향(아래 참조) |

Line Direction에 따른 시작·끝점 계산:

| 값 | 의미 | 시작점 | 끝점 |
|---|---|---|---|
| 0 | 좌상 → 우하 | (X, Y) | (X + Width − LineWidth, Y + Height − LineWidth) |
| 1 | 좌하 → 우상 | (X, Y + Height − LineWidth) | (X + Width − LineWidth, Y) |

계산 결과 EndX < StartX면 EndX = StartX로, 세로 방향도 마찬가지로 보정한다(선이 사각형 밖으로 나가지 않게 하는 규칙).

이벤트: On Refresh, On Change End Point(Change End Point 명령 → 재그리기 + 부모 갱신), On Change Attribute, On Change Size.

### B.10.3 Output Rectangle object (Type 14)

사각형을 출력한다. 허용 명령: Change Size, Change Attribute, Get Attribute Value.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =14 | Output Rectangle |
| Line attributes | 1 | 2 | 0~65534 | Line Attributes 오브젝트 ID |
| Width, Height | 2, 3 | 각 2 | 0~65535 | 픽셀 크기. (StartX, StartY)~(StartX+Width−1, StartY+Height−1)이 클리핑 한계. 끝점 = Start + 크기 − LineWidth |
| Line suppression | 4 | 1 | 0~15 | 변 생략 비트마스크. 0 = 닫힌 사각형, Bit 0 = 윗변(최소 Y), Bit 1 = 오른변(최대 X), Bit 2 = 아랫변(최대 Y), Bit 3 = 왼변(최소 X) 생략. 조합 가능 |
| Fill attributes | 5 | 2 | 0~65534, 65535 | Fill Attributes 오브젝트 ID, NULL이면 채우기 없음 |

채워진 사각형에 line suppression을 적용하면 테두리에 해당하는 픽셀만 생략되고 내부 채움은 유지된다. 이때 테두리 폭은 line width를 반영해 계산한다.

### B.10.4 Output Ellipse object (Type 15)

타원 또는 원을 출력한다. 허용 명령: Change Size, Change Attribute, Get Attribute Value.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =15 | Ellipse |
| Line attributes | 1 | 2 | 0~65534 | Line Attributes 오브젝트 ID |
| Width, Height | 2, 3 | 각 2 | 0~65535 | 둘러싼 가상 사각형 크기. 클리핑 한계 동일 |
| Ellipse type | 4 | 1 | 0~3 | 0 = 닫힌 타원, 1 = 시작/끝 각으로 정의된 열린 타원(호), 2 = 닫힌 segment(현으로 닫음), 3 = 닫힌 section(중심까지 반지름으로 닫음, 부채꼴) |
| Start angle | 5 | 1 | 0~180 | 시작각/2 (도 단위). 양의 x축 기준 반시계, 90° = 수직 위 |
| End angle | 6 | 1 | 0~180 | 끝각/2 (도 단위) |
| Fill attributes | 7 | 2 | 0~65534, 65535 | Fill Attributes ID, NULL이면 채우기 없음 |

- 각도는 실제 각도의 절반 값으로 저장한다(1바이트에 0~360°를 담기 위한 인코딩).
- type > 0인데 시작각 = 끝각이면 닫힌 타원으로 그린다.
- type = closed segment이고 시작각 = 끝각이면, 중심점부터 그 각도가 가리키는 테두리 점까지 폭 = border width인 선 하나를 그린다.

:::warning 비원형 타원의 각도 렌더링
원이 아닌 타원에서 열림각은 실제 각도로 정확히 측정돼야 한다. 원을 그린 뒤 세로로 스케일만 하는 흔한 렌더링 알고리즘을 쓰면 열림각이 지정값보다 작아져 부정확한 결과가 된다. 단, 디스플레이 픽셀의 종횡비가 정사각이 아닌 경우까지 보정할 의무는 없다.
:::

### B.10.5 Output Polygon object (Type 16)

다각형을 출력한다. 허용 명령: Change Attribute, Change Size, Change Polygon Point, Change Polygon Scale, Get Attribute Value.

- 다각형 타입은 convex, non-convex, complex, open 네 가지다. 채워질 다각형이면 Working Set이 타입을 정확히 지정해야 채우기 알고리즘 효율에 도움이 된다. 모르면 complex로 둔다(complex 채우기 알고리즘은 세 가지 채우기 가능 타입 모두에 동작하므로, VT가 complex 알고리즘만 구현하고 타입 속성을 무시하는 것도 허용된다).
- 채우기 규칙은 <strong>even-odd</strong>만 지원한다. non-zero winding은 지원하지 않는다.
- 시작점은 목록의 첫 점이고, 나열 순서대로 그린다. 점은 최소 3개 필요하며, 좌표는 Output Polygon 좌상단 기준 상대값이다.
- 타입이 open이 아닌데 Working Set이 다각형을 닫지 않았으면 VT가 첫 점과 끝 점을 이어 자동으로 닫는다.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =16 | Polygon |
| Width, Height | 1, 2 | 각 2 | 0~65535 | 둘러싼 가상 사각형 크기, 클리핑 한계 |
| Line attributes | 3 | 2 | 0~65534 | Line Attributes 오브젝트 ID |
| Fill attributes | 4 | 2 | 0~65534, 65535 | Fill Attributes ID, NULL이면 채우기 없음 |
| Polygon type | 5 | 1 | 0~3 | 0 = Convex(수평선이 다각형과 최대 2점에서 교차), 1 = Non-Convex(2점 초과 교차 가능하나 변이 서로 교차하지 않음), 2 = Complex(변이 교차, complex fill 알고리즘 사용), 3 = Open(채우기 불가). 타입 변경은 open↔not open 방향으로만 가능 |
| Number of points | — | 1 | 3~255 | 점 개수. 점 하나당 4바이트 |
| Repeat: {Point X, Point Y} | — | 각 2 | 0~65535 | 다각형 좌상단 기준 상대 좌표 |

## B.11 Output graphic 오브젝트

### B.11.1 개요

Output graphic은 Output Meter, Output Linear Bar Graph, Output Arched Bar Graph 세 종류다.

VT version 4 이상에서의 값 제약 처리: min ≥ max이면 값·target에 관계없이 value = min인 것처럼 그린다. value(또는 target value)가 min보다 작으면 min으로, max보다 크면 max로 클램프해서 그린다. VT version 3 이하에서는 이 제약이 정의돼 있지 않았다.

### B.11.2 Output Meter object (Type 17)

원형 계기(아날로그 미터)다. 정사각형 영역에 내접하는 원을 중심으로 그리며, 세부 외관은 VT 재량이다. 각도 속성은 양의 x축 기준 수학적 양의 방향(반시계)으로 계산한다. 바늘이 움직여도 아래에 겹쳐 놓은 다른 오브젝트가 손상되지 않도록 VT가 처리해야 하며, 이 오브젝트는 투명하게 그려져 밑에 오브젝트를 깔아 외관을 꾸밀 수 있다. 부모 오브젝트에서의 위치 속성은 방향과 무관하게 항상 둘러싼 정사각형의 좌상단을 가리킨다. 눈금(tick) 길이는 미터 폭의 10 %(최소 1픽셀)가 권장된다.

허용 명령: Change Numeric Value, Change Attribute, Change Size, Get Attribute Value.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =17 | Output Meter |
| Width | 1 | 2 | 0~65535 | 둘러싼 정사각형의 폭이자 높이. 미터는 이 영역을 벗어날 수 없음 |
| Needle colour | 2 | 1 | 0~255 | 바늘(지시자) 색 |
| Border colour | 3 | 1 | 0~255 | 테두리 색(그릴 경우) |
| Arc and tick colour | 4 | 1 | 0~255 | 호와 눈금 색(그릴 경우) |
| Options | 5 | 1 | 0~15 | Bit 0 = Draw Arc, Bit 1 = Draw Border, Bit 2 = Draw Ticks, Bit 3 = Deflection Direction(0 = min→max 반시계, 1 = min→max 시계) |
| Number of ticks | 6 | 1 | 0~255 | 눈금 수. 1개면 호 중앙에, 2개 이상이면 호 양 끝에 놓고 나머지를 균등 배치 |
| Start angle | 7 | 1 | 0~180 | 시작각/2 (도). 양의 x축 기준 반시계, 90° = 수직 위. 시작각 = 끝각이면 호가 닫힘(360°) |
| End angle | 8 | 1 | 0~180 | 끝각/2 (도) |
| Min value | 9 | 2 | 0~65535 | 바늘이 호 시작에 있을 때 값 |
| Max value | 10 | 2 | 0~65535 | 바늘이 호 끝에 있을 때 값 |
| Variable reference | 11 | 2 | 0~65534, 65535 | 값을 가져올 Number Variable ID. NULL이면 Value 속성 사용. 참조 변수 값은 0~65535 범위여야 함 |
| Value | [12] | 2 | 0~65535 | 현재 값. 바늘 위치를 결정 |

### B.11.3 Output Linear Bar Graph object (Type 18)

선형 바 그래프 또는 온도계 형태의 오브젝트다. 둘러싼 사각형 안에서 상·하·좌·우 네 방향 중 하나로 그려지며, 목표값(target value)을 선으로 표시할 수 있다. 위치 속성은 방향과 무관하게 둘러싼 사각형의 좌상단을 가리킨다. 이 오브젝트도 투명하게 그려져 밑에 오브젝트를 깔 수 있다.

허용 명령: Change Numeric Value, Change Attribute, Change Size, Get Attribute Value.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =18 | Output Linear Bar Graph |
| Width, Height | 1, 2 | 각 2 | 0~65535 | 둘러싼 사각형 크기. 바 그래프는 이 영역을 벗어날 수 없음 |
| Colour | 3 | 1 | 0~255 | 바 채움·테두리 색 |
| Target line colour | 4 | 1 | 0~255 | 목표선 색(그릴 경우) |
| Options | 5 | 1 | 0~63 | Bit 0 = Draw border, Bit 1 = Draw target line, Bit 2 = Draw ticks, Bit 3 = 바 타입(0 = 채움, 1 = 채우지 않고 현재 값 위치에 선 하나로 표시), Bit 4 = 축 방향(0 = 수직, 1 = 수평), Bit 5 = 증가 방향(0 = 음의 방향(왼쪽/아래), 1 = 양의 방향(오른쪽/위)) |
| Number of ticks | 6 | 1 | 0~255 | 눈금 수. 배치 규칙은 Meter와 동일 |
| Min value / Max value | 7, 8 | 각 2 | 0~65535 | 최소·최대값 |
| Variable reference | 9 | 2 | 0~65534, 65535 | 값을 가져올 Number Variable ID. NULL이면 Value 사용 |
| Value | [12] | 2 | 0~65535 | 현재 값. min/max에서 계산된 위치까지 바를 채우거나 이동. 범위를 벗어나면 가득 채우거나 비워서 표시하고 오류는 발생시키지 않음 |
| Target value variable reference | 10 | 2 | 0~65534, 65535 | 목표값을 가져올 Number Variable ID. NULL이면 Target value 속성 사용 |
| Target value | 11 | 2 | 0~65535 | 목표값. 바 그래프 위에 선으로 표시. 범위를 벗어나면 바 그래프 한쪽 끝에 표시하고 오류는 발생시키지 않음 |

### B.11.4 Output Arched Bar Graph object (Type 19)

개념상 선형 바 그래프와 같지만 호 형태로 그려진다. 사각형에 내접하는 Output Ellipse를 따라 그려지며, 각도는 양의 x축 기준 반시계로 계산한다. 위치 속성은 항상 둘러싼 사각형 좌상단이며, 투명하게 그려진다.

Change Size 명령으로 "bar graph width"가 오브젝트 폭·높이의 절반 이상이 될 수 있는데, 이는 풀 거부 사유가 아니다. VT는 그리기 목적에 한해 bar graph width 값을 줄여 사용할 수 있고, 줄인 값을 오브젝트에 저장하지는 않는다.

허용 명령: Change Numeric Value, Change Attribute, Change Size, Get Attribute Value.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =19 | Output Arched Bar Graph |
| Width, Height | 1, 2 | 각 2 | 0~65535 | 둘러싼 사각형 크기 |
| Colour | 3 | 1 | 0~255 | 바 채움·테두리 색 |
| Target line colour | 4 | 1 | 0~255 | 목표선 색 |
| Options | 5 | 1 | 0~31 | Bit 0 = Draw border(TRUE면 시작선·끝선 포함 테두리를 항상 그림), Bit 1 = Draw a target line, Bit 2 = 미정의(0 권장), Bit 3 = 바 타입(0 = 채움, 1 = 현재 값 위치에 선으로 표시), Bit 4 = 편향 방향(0 = 반시계, 1 = 시계) |
| Start angle / End angle | 6, 7 | 각 1 | 0~180 | 각도/2 (도). 시작각 = 끝각이면 호가 닫힘(360°) |
| Bar graph width | 8 | 2 | 0~65535 | 바 폭(픽셀). 전체 폭 또는 높이 중 작은 쪽의 절반 미만이어야 함 |
| Min value / Max value | 9, 10 | 각 2 | 0~65535 | 최소·최대값 |
| Variable reference | 11 | 2 | 0~65534, 65535 | 값 참조 Number Variable ID, NULL이면 Value 사용 |
| Value | [14] | 2 | 0~65535 | 현재 값. 범위 초과 시 가득/비움으로 표시, 오류 없음 |
| Target value variable reference | 12 | 2 | 0~65534, 65535 | 목표값 참조 변수, NULL이면 Target value 사용 |
| Target value | 13 | 2 | 0~65535 | 목표값. 범위 초과 시 한쪽 끝에 표시, 오류 없음 |

## B.12 Picture Graphic 오브젝트 (Type 20)

### B.12.1 개요

비트맵을 표시한다. VT는 그림을 실제 크기(Actual width/height)에서 목표 폭(Width)과 그로부터 계산되는 목표 높이로 스케일한다. 종횡비를 유지해 왜곡을 막는다.

허용 명령: Change Attribute, Get Attribute Value. 이벤트는 On Refresh(Opaque/Transparent 또는 Flashing 옵션 비트 변경 시 포함)와 On Change Attribute뿐이다.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =20 | Picture Graphic |
| Width | 1 | 2 | 0~65535 | 목표 폭(픽셀). 높이는 종횡비 유지를 위해 Actual width/height와 이 값에서 계산 |
| Actual width | [4] | 2 | 0~65535 | 원본 데이터의 실제 폭 |
| Actual height | [5] | 2 | 0~65535 | 원본 데이터의 실제 높이 |
| Format | [6] | 1 | 0~2 | 0 = Monochrome(1bpp, 바이트당 8픽셀, 팔레트 인덱스 0/1), 1 = 4-bit colour(바이트당 2픽셀, 니블당 인덱스 0~15), 2 = 8-bit colour(바이트당 1픽셀, 인덱스 0~255) |
| Options | 2 | 1 | 0~7 | Bit 0: 0 = Opaque, 1 = Transparent(transparency colour와 같은 인덱스 픽셀은 배경이 비침), Bit 1: 1 = Flashing(스타일·주기는 VT 재량), Bit 2: 1 = Run-Length Encoded 데이터. Bit 2는 런타임 Change Attribute로 변경 불가(변경 시도는 무시됨) |
| Transparency colour | 3 | 1 | 0~255 | 투명 처리할 색 인덱스 |
| Number of bytes in raw data | — | 4 | 0~2³²−1 | 원시 데이터 바이트 수 |
| Repeat: {raw data} | — | 1 | 0~255 | 그래픽 원시 데이터 |

### B.12.2 원시 데이터 형식과 압축

원시 데이터는 픽셀 정보를 줄 단위로, 왼쪽에서 오른쪽·위에서 아래로 담는다. 각 바이트는 왼쪽 픽셀부터 최상위 비트(모노크롬)/최상위 니블(4-bit) 순으로 해석한다. 한 줄이 바이트 경계에서 끝나지 않으면 줄 끝 바이트의 남는 부분을 0으로 채우고, VT는 줄 끝의 미사용 비트를 무시한다.

- 데이터가 정의된 행·열보다 <strong>길면</strong> 초과 바이트를 무시한다.
- 데이터가 <strong>짧아서</strong> 정의되지 않은 픽셀이 남으면 오류다. End of Object Pool response 또는 VT Change Active Mask 메시지로 Working Set에 보고해야 한다.

전송량을 줄이기 위해 그림은 가능한 최소 크기로 전송하는 것이 권장되며, run-length encoding으로 압축할 수 있다. 압축 방식은 2바이트 쌍의 나열로, 첫 바이트 = 반복 횟수, 둘째 바이트 = 반복할 값이다. 예를 들어 0,0,0,0,0,0,3,3,3,1,1,2는 6,0 3,3 2,1 1,2로 압축된다(33 % 압축). 쌍의 첫 바이트가 0이면 둘째 바이트는 무시된다. RLE는 버퍼 없이 실시간 압축·해제가 가능해서 채택됐지만, 복잡한 그림에서는 오히려 데이터가 커질 수 있으므로 그 경우 원시 데이터로 전송하고 Options Bit 2를 끄는 것이 권장된다.

## B.13 Variable 오브젝트

값을 저장해 다른 오브젝트가 참조하게 하는 오브젝트다. number와 string 두 종류가 있으며, <strong>참조로만 사용되고 부모의 child로 직접 포함되지 않는다.</strong> 이벤트는 On Change Value(Change Numeric/String Value 명령) 하나로, 이 변수를 참조하며 현재 표시 중인 모든 오브젝트를 다시 그린다.

### B.13.2 Number Variable object (Type 21)

32-bit unsigned integer 값 하나를 담는다. 허용 명령: Change Numeric Value, Get Attribute Value.

| 속성 | AID | 크기(B) | 설명 |
|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | Type = 21 |
| Value | [1] | 4 | 32-bit unsigned 정수 값 |

### B.13.3 String Variable object (Type 22)

고정 길이 문자열을 담는다. Length보다 짧은 문자열은 공백으로 패딩한다. Length 속성은 변수 정의 후 변경할 수 없다. 값은 8-bit String 또는 WideString일 수 있고, Working Set이 타입을 서로 변환할 수 있다. 허용 명령: Change String Value, Get Attribute Value.

| 속성 | AID | 크기(B) | 설명 |
|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | Type = 22 |
| Length | — | 2 | 문자열 값의 고정 길이(바이트) |
| Value | — | Length | 문자열. 공백 패딩 |

## B.14 Attribute 오브젝트

### B.14.1 개요

여러 오브젝트가 공유하는 공통 속성 묶음을 담는 오브젝트로, font, line, fill, input 네 종류가 있다. Variable과 마찬가지로 참조로만 쓰이고 child로 직접 포함되지 않는다.

### B.14.2 Font Attributes object (Type 23)

글꼴 관련 속성을 담는다. Change Font Attributes 명령(모든 글꼴 속성 일괄 변경), Change Attribute 명령(개별 속성), 또는 새 오브젝트 전송으로 변경할 수 있다. Change Attribute로 개별 속성만 바꾸면 VT가 지원하지 않는 Font size + Font style 조합이 만들어져 오브젝트 풀이 invalid 상태가 될 수 있으므로, Change Font Attributes 명령을 쓰면 이런 문제 없이 원하는 결과를 얻을 수 있다.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =23 | Font Attributes |
| Font colour | 1 | 1 | 0~255 | 글자 색 |
| Font size | 2 | 1 | 0~14ᵃ / 0~14 또는 8~Nᵇ | 아래 참조 |
| Font type | 3 | 1 | 0, 1, 255ᵃ / 0~2, 4, 5, 7, 240~255ᵇ | 코드플레인 선택(Table K.1). WideString에 적용될 때는 무시됨 |
| Font style | 4 | 1 | 0~127ᵃ / 0~255ᵇ | 아래 참조 |

ᵃ VT v3 이하, ᵇ VT v4 이상.

<strong>Font size</strong>: 비례(proportional) 여부는 Font style bit 7이 결정한다.

- 고정폭 글꼴: 값 0~14가 픽셀 크기(폭×높이)에 대응한다 — 0 = 6×8, 1 = 8×8, 2 = 8×12, 3 = 12×16, 4 = 16×16, 5 = 16×24, 6 = 24×32, 7 = 32×32, 8 = 32×48, 9 = 48×64, 10 = 64×64, 11 = 64×96, 12 = 96×128, 13 = 128×128, 14 = 128×192.
- 비례 글꼴(v4+): 값 8~N이 글꼴 높이(픽셀)를 직접 나타낸다. N은 Get Text Font Data response의 Font size 값으로 식별되는 VT의 최대 지원 높이이고, 문자 폭은 가변이다.

<strong>Font style</strong> 비트마스크 (조합 가능, 0 = 일반 텍스트):

| 비트 | 의미 |
|---|---|
| 0 | Bold |
| 1 | Crossed Out(취소선) |
| 2 | Underlined |
| 3 | Italic |
| 4 | Inverted(배경색과 펜 색 교환. 배경 투명 규칙 적용) |
| 5 | Inverted 상태와 bit 0~3 스타일 사이를 번갈아 깜빡임 |
| 6 | 배경과 전경 모두 Hidden과 bit 0~4 스타일 사이 깜빡임("hidden" 주기에 텍스트 오브젝트 전체가 숨겨짐). bit 5보다 우선 |
| 7 | 비례 글꼴 렌더링(0이면 고정폭)ᵇ |

### B.14.3 Line Attributes object (Type 24)

Output shape 오브젝트가 참조하는 선 속성 묶음이다. 허용 명령: Change Line Attributes, Change Attribute, Get Attribute Value. 두 명령 모두 이 오브젝트를 참조하며 표시 중인 모든 오브젝트를 다시 그리게 한다. 선의 끝점은 계산될 수 있어도 Line art가 적용되면 반드시 그려지는 것은 아니다.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =24 | Line Attributes |
| Line colour | 1 | 1 | 0~255 | 펜 색 |
| Line width | 2 | 1 | 0~255 | 펜 두께(픽셀). 이 크기의 정사각 paintbrush로 그림 |
| Line art | 3 | 2 | 0~65535 | 선 패턴 비트마스크. 각 비트가 브러시 한 칸이며 1 = 선 색으로 그림, 0 = 건너뜀(배경색). 비트 하나의 길이 = 현재 브러시 크기. 예: 00110011은 두 칸 생략 + 두 칸 그림의 반복 |

Line art의 비트 단위가 브러시 크기이므로, 같은 패턴이라도 line width가 커지면 점선 마디도 함께 커진다.

### B.14.4 Fill Attributes object (Type 25)

Output shape 채우기 속성 묶음이다. 허용 명령: Change Fill Attributes, Change Attribute, Get Attribute Value.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =25 | Fill Attributes |
| Fill type | 1 | 1 | 0~3 | 0 = 채우기 없음, 1 = line colour로 채움, 2 = Fill colour 속성의 색으로 채움, 3 = Fill pattern 속성의 패턴으로 채움 |
| Fill colour | 2 | 1 | 0~255 | Fill type = 2일 때만 사용 |
| Fill pattern | 3 | 2 | 0~65534, 65535 | 패턴으로 쓸 Picture Graphic 오브젝트 ID. Fill type ≠ 3이면 무시. Fill type = 3인데 NULL이면 채우지 않음 |

:::warning Fill pattern 관련 규칙
- Fill Type을 0/1/2에서 3으로 바꿀 때는 <strong>Fill Pattern 속성을 먼저, Fill Type 속성을 나중에</strong> 수정해야 한다. 순서를 지키지 않으면 VT 동작을 예측할 수 없다.
- 모노크롬·16색 VT 단순화를 위해, 패턴으로 참조되는 Picture Graphic은 미사용 비트가 없는 패턴 버퍼여야 한다. 즉 Format 0(모노크롬)이면 폭이 8의 배수, Format 1(16색)이면 폭이 2의 배수여야 한다. 위반 시 VT는 End of Object Pool response 또는 VT Change Active Mask로 오류를 보고해야 한다.
:::

### B.14.5 Input Attributes object (Type 26)

Input String 오브젝트에 대해 유효/무효 문자를 정의한다. VT는 이 오브젝트를 확인해 무효 문자의 오퍼레이터 입력을 막아야 한다. 참조하는 Input String(또는 그 String Variable)이 8-bit string이 아니면 검증을 수행하지 않는다. 허용 명령: Change String Value, Get Attribute Value.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =26 | Input Attributes |
| Validation type | [1] | 1 | 0~1 | 0 = 유효 문자를 나열, 1 = 무효 문자를 나열 |
| Length | — | 1 | 0~255 | 검증 문자열 길이(바이트). 검증 문자열은 8-bit String이어야 함 |
| Validation string | — | Length | — | 유효 또는 무효 문자 코드 전체를 담은 문자열 |

### B.14.6 Extended Input Attributes object (Type 38)

VT version 4에서 추가된, WideString용 입력 문자 검증 오브젝트다. 참조하는 Input String(또는 String Variable)이 WideString이 아니면 검증하지 않는다. 정의된 문자 범위에 VT가 지원하지 않는 문자가 포함될 수 있는데, VT는 그 문자를 무시하고 나머지 문자로 검증을 계속한다. 허용 명령은 Get Attribute Value뿐이다(런타임 변경 불가).

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =38 | Extended Input Attributes |
| Validation type | [1] | 1 | 0~1 | 0 = 유효 문자 나열, 1 = 무효 문자 나열 |
| Number of code planes | — | 1 | 1~17 | 유효/무효 문자가 있는 코드플레인 수 |
| Repeat: {Code plane number} | — | 1 | 0~16 | 문자 범위가 속한 코드플레인(0 = U+0000~U+FFFF, 1 = U+10000~U+1FFFF, …) |
| {Number of character ranges} | — | 1 | 1~255 | 문자 범위 수 |
| Repeat: `{{First character}, {Last character}}` | — | 각 2 | 0~65535 | 범위의 첫/끝 문자(WideChar, first ≤ last) |

## B.15 Object Pointer object (Type 27)

다른 오브젝트를 간접 참조하는 오브젝트다(개념은 4.6.11.5 참조). Value 속성이 참조 대상의 Object ID 또는 NULL을 담는다. Change Numeric Value로 Value를 바꾸면 이전 오브젝트를 숨기고 새 오브젝트를 보여주며 부모를 갱신한다. 허용 명령: Change Numeric Value, Get Attribute Value.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =27 | Object Pointer |
| Value | [1] | 2 | 0~65534, 65535 | 참조 오브젝트 ID 또는 NULL |

## B.16 Macro object (Type 28)

이벤트에 연결하거나 Execute Macro 명령(v4+) 또는 Execute Extended Macro 명령(v5+)으로 실행할 수 있는 명령 목록을 정의한다. Macro는 하나 이상의 명령 패킷 연속으로 정의된다. 실행 전 매크로가 오브젝트 풀과 일관되도록(예: 없는 오브젝트를 참조하지 않도록) 보장하는 것은 Working Set의 책임이다. 명령 패킷은 Annex F에 정의돼 있지만 모든 명령이 Macro 안에서 허용되는 것은 아니다.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =28 | Macro. Object ID 범위는 v4 이하 0~255, v5+ 0~65534 |
| Number of bytes to follow | — | 2 | 0~65535 | 뒤따르는 바이트 수. 8바이트 미만 명령(예: 2바이트 문자열의 Change String Value)은 나머지를 FF₁₆으로 채워 8바이트 경계에 맞춤 |
| Repeat: {Command} | — | — | — | 명령 메시지 패킷들. Annex F에 나열된 명령만 허용, 형식도 Annex F를 따름 |

## B.17 Colour Map object (Type 39)

VT 색 인덱스 → RGB 변환 테이블을 런타임에 바꿀 수 있게 하는 오브젝트다. VT version 4·5에서는 선택 사항, version 6 이상에서는 필수다. 배경·테두리에 색 오브젝트 몇 개만 쓰는 Working Set이 색 테이블 교체만으로 전체 표현을 쉽게 바꿀 수 있다.

- 풀에는 Colour Map을 여러 개 담을 수 있다. 풀 로드 직후에는 기본 Colour Map을 쓰고, 유효한 Select Colour Map or Palette 명령을 받으면 해당 Working Set의 활성 팔레트 접근이 바뀐다. Working Set 풀의 모든 오브젝트는 그 Working Set의 Colour Map으로 표시된다.
- Colour Map은 유효한 색 인덱스 각각의 정의를 담는다. 선택 시 결과 값이 VT 능력 범위에서 유효해야 하며, 아니면 Select Colour Map or Palette response로 실패를 알린다. 모노크롬 VT는 엔트리 2개, 256색 VT는 256개를 유지한다. VT 능력을 넘는 Colour Map(예: 2색 VT에 256엔트리 맵 업로드)은 허용되지만, VT 능력보다 <strong>적은</strong> 색 인덱스를 가질 수는 없다.
- 기본 팔레트는 Table A.4에 정의되며 색 인덱스가 배열 첨자다. Colour Map은 이 RGB 테이블로 가는 간접 참조 한 단계를 제공한다. 예를 들어 [1, 0, …] 값의 Colour Map을 선택하면 색 0과 1이 뒤바뀐다.
- v6 이상은 Colour Palette 오브젝트로 VT 표준 팔레트 자체를 Working Set 정의 팔레트로 바꾸는 것도 지원한다.

허용 명령: Get Attribute Value.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =39 | Colour Map |
| Number of colour indexes | — | 2 | 2, 16, 256 | 그래픽 타입 0(모노크롬) = 2, 타입 1(16색) = 16, 타입 2(256색) = 256 |
| Colour Map | — | 가변 | 0~255 | 각 색 인덱스에 대해 실제로 표시할 VT 색 |

## B.18 Graphics Context object (Type 36)

캔버스와 뷰포트를 가진 비트맵으로, Working Set이 런타임에 조작(그리기)할 수 있다. v4 이상 선택 사항, v6 이상 필수다. VT가 지원하지 않는데 풀에서 참조되면 NULL을 가리키는 Object Pointer처럼 처리된다(그리지 않고, 열린 Input List에서 선택 가능한 자리를 차지). 이 경우 추가 메모리는 할당되지 않는다.

- <strong>캔버스에 메모리가 있다</strong>: 그리기 영역(canvas)의 픽셀은 화면에서 제거되거나 다른 마스크가 선택돼도 유지된다. 이를 이용해 Working Set이 VT 화면에 런타임 드로잉을 할 수 있다 — 예를 들어 정밀농업 앱에서 움직이는 작업기 이미지 뒤에 작업 궤적(swathe)을 그리는 용도.
- 캔버스 크기는 업로드 후 변경 불가(새 오브젝트를 올려야 함). 비트맵 메모리 요구량은 캔버스 크기에서 직접 계산된다.
- <strong>뷰포트</strong>는 캔버스 중 보이는 부분이자 화면상 표시 크기다. 뷰포트를 부모 마스크·컨테이너의 child로 앵커하면 뷰포트 안에서 하부 내용을 쉽게 팬(pan)할 수 있다. 뷰포트 크기는 런타임 변경 가능하다.
- 이 오브젝트 내용은 Store Version 명령으로 저장되지 않는다. 그린 내용을 보존하려면 저장 전에 캔버스를 Picture Graphic으로 복사해야 한다.
- 여러 sub-command를 가진 단일 Graphics Context 명령으로 내용을 수정하며, Macro에 담아 더 효율적으로 갱신할 수도 있다. 대부분의 명령은 CAN 패킷 하나에 들어간다.
- 현재 드로잉 컨텍스트(속성들)는 항상 기억되므로, 반복 사용할 속성은 한 번만 설정하면 된다. graphics cursor가 다음 그리기 시작 X/Y 위치를 나타내고, 그리기 명령이 커서를 이동시킨다. 즉 드로잉은 절차적 명령의 나열이다(SET FOREGROUND COLOUR → SET GRAPHICS CURSOR → DRAW LINE → … 식).
- Picture Graphic처럼 투명 옵션이 있어 Graphics Context를 여러 장 겹쳐 그래픽 "레이어"를 만들 수 있다. 예를 들어 아래 깔린 지도 이미지를 건드리지 않고 swathe 선만 지울 수 있다.

:::warning 메모리 주의
Graphics Context는 VT에서 상당한 메모리를 차지한다(256색 VT 기준 Canvas Width × Canvas Height 바이트 이상). 메모리 제약으로 풀이 거부되지 않도록 아껴서, 작게 유지해야 한다.
:::

허용 명령: Graphics Context command, Change Attribute, Change Background Colour, Get Attribute Value.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =36 | Graphics Context (v4+) |
| Viewport Width / Height | 1, 2 | 각 2 | 0~32767 | 보이는 뷰포트 크기(픽셀) |
| Viewport X / Y | 3, 4 | 각 2 | −32768~32767 | 캔버스 좌상단 기준 뷰포트 좌상단 위치. 캔버스 치수에 제약되지 않음 |
| Canvas Width / Height | [5], [6] | 각 2 | 0~32767 | 캔버스 크기(픽셀). 런타임 변경 불가 |
| Viewport Zoom | 7 | 4 | −32,0~+32,0 | 뷰포트 배율(float) |
| Graphics Cursor X / Y | 8, 9 | 각 2 | −32768~32767 | 캔버스 좌상단 기준 커서 위치. 다음 픽셀이 그려질 자리 |
| Foreground Colour | 10 | 1 | 0~255 | Options bit 1 = 0일 때 그리기 전경색 |
| Background Colour | 11 | 1 | 0~255 | Options bit 1 = 0일 때 배경색. 파싱 시점에 오브젝트가 이 색으로 채워짐. <strong>런타임에 이 속성을 쓰면 오브젝트가 다시 채워져 내용이 지워진다</strong> |
| Font / Line / Fill Attributes Object | 12, 13, 14 | 각 2 | 0~65534, 65535 | 텍스트·선·채우기에 쓸 속성 오브젝트 ID, 미사용 시 NULL |
| Format | 15 | 1 | 0~2 | 캔버스 타입: 0 = 모노크롬, 1 = 4-bit colour, 2 = 8-bit colour (Picture Graphic과 동일) |
| Options | 16 | 1 | 0~3 | Bit 0 = Transparency(0 = Opaque, 1 = Transparent), Bit 1 = Colour(0 = 이 오브젝트의 Foreground/Background Colour 사용, 1 = Line/Font/Fill Attributes의 색 사용) |
| Transparency Colour | 17 | 1 | 0~255 | 투명 처리할 색 인덱스. Opaque면 무시 |

## B.19 Window Mask object (Type 34)

### B.19.1 개요

VT version 4에서 추가된 특수 부모 마스크 오브젝트로, VT의 User-Layout Data Mask에서만 사용된다(4.7.1.2 참조). Working Set은 Window Mask 오브젝트를 풀에 넣는 것으로 VT의 User-Layout Data Mask에 참여할 수 있다.

Window Type이 free form(type 0)이면 Working Set이 다른 오브젝트처럼 이 오브젝트를 VT의 Window Cell 치수에 맞게 스케일해야 한다. User-Layout Data Mask에는 항상 창 셀 12개(2열 × 6행)가 있고 Data Mask는 항상 풀 마스크 해상도의 정사각형이므로, Get Hardware response의 Data Mask 크기에서 Window Cell 크기를 계산할 수 있다.

허용 명령: Change Background Colour, Change Child Location, Change Child Position, Change Attribute, Get Attribute Value.

주요 이벤트: On Show / On Hide(이 Window Mask를 담은 User-Layout Data Mask가 표시되거나 화면에서 제거될 때, VT On User-Layout Hide/Show message로 통지), On Refresh, On Change Background Colour, On Change Child Location/Position, On Change Attribute, On Pointing Event press/release(Free Form 창에서만 Pointing Event message 보고).

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =34 | Window Mask |
| Width | — | 1 | 1~2 | 폭(User-Layout Data Mask 열 수). Window Type 0(Free Form)일 때만 사용 |
| Height | — | 1 | 1~6 | 높이(행 수). Free Form일 때만 사용 |
| Window Type | — | 1 | 0~18 | 아래 표 참조 |
| Background Colour | 1 | 1 | 0~255 | Window Type > 0이면 VT가 형식을 통제하므로 무시됨 |
| Options | 2 | 1 | 0~3 | Bit 0 = Available(0이면 정의돼 있어도 현재 사용 불가 — VT는 오퍼레이터가 매핑하지 못하게 하고, 이미 매핑됐으면 해당 창 셀을 비움), Bit 1 = Transparent(1이면 배경색 무시, 창 투명) |
| Name | 3 | 2 | 0~65534 | 이 창의 이름 문자열을 담은 Output String(또는 그를 가리키는 Object Pointer) ID. VT는 색·글꼴을 무시하고 자체 형식을 적용할 수 있으며, 독자적 매핑 화면에서 이 이름을 사용. 최소 20자 표시 가능해야 함 |
| Window Title | — | 2 | 0~65534, 65535 | 창 제목 문자열 Output String ID. type 0에서는 NULL이어야 하고, type > 0에서는 필수 |
| Window Icon | — | 2 | 0~65534, 65535 | 창을 나타낼 아이콘 출력 오브젝트 ID. type 0에서만 NULL 허용, 그 외 타입에서는 반드시 제공 |
| Number of object references | — | 1 | 0~2 | 창 타입별 필수 오브젝트 참조 수. type 0이면 0 |
| Number of objects to follow | — | 1 | 0~255 | 포함(child) 오브젝트 수. Free Form(0)일 때만 필요, 그 외 타입이면 0. child 하나당 6바이트(ID 2 + X/Y 위치 각 2) |

Window Type 값(치수는 창 셀 단위 폭×높이):

| 값 | 유형 |
|---|---|
| 0 | Free Form |
| 1 / 10 | 1×1 / 2×1 Numeric Output Value with Units |
| 2 / 11 | 1×1 / 2×1 Numeric Output Value, no Units |
| 3 / 12 | 1×1 / 2×1 String Output Value |
| 4 / 13 | 1×1 / 2×1 Numeric Input Value with Units |
| 5 / 14 | 1×1 / 2×1 Numeric Input Value, no Units |
| 6 / 15 | 1×1 / 2×1 String Input Value |
| 7 / 16 | 1×1 / 2×1 Horizontal Linear Bar Graph, no Units |
| 8 / 17 | 1×1 / 2×1 Single Button |
| 9 / 18 | 1×1 / 2×1 Double Button |

### B.19.2 Window Mask Window Types

Window Type 속성과 오브젝트 구성 참조 덕분에 VT는 모든 Working Set의 표준화된 창을 통일된 look & feel로 만들 수 있고, type 0(Free Form)이면 Working Set이 완전히 자유로운 표현을 만들 수 있다.

Free Form을 제외한 Window Mask에 Linear Bar Graph가 포함된 경우, VT는 bar graph의 min/max 속성이 표시 가능한 측정 단위라고 가정할 수 없으므로 눈금에 라벨을 붙이지 않아야 한다.

<strong>B.19.2.1 Free Form Window Mask (type 0)</strong>: Working Set이 창 안의 모든 child를 직접 공급·배치한다. look & feel을 Working Set이 완전히 통제하며, VT는 child 오브젝트, 위치, 크기, 투명도 속성 등 지정된 그대로 렌더링해야 한다.

<strong>B.19.2.2 ~ B.19.2.19 표준 창 타입(type 1~18)</strong>: 표준의 B.19.2.2부터 B.19.2.19까지는 창 타입 1~18을 각각 하나의 절로 정의하는데, 구조가 동일하게 반복되므로 공통 규칙과 타입별 차이만 정리한다.

공통 규칙(모든 표준 창 타입):

- Window Designator: Window Icon과 Window Title 둘 다 선택 사항이지만 VT는 <strong>둘 중 최소 하나</strong>를 표시해야 한다.
- VT는 창 형식을 자유롭게 정하고, 참조 오브젝트의 색·Font Attributes를 무시할 수 있다. 다만 필드 길이는 아래 요구치를 만족해야 한다. VT는 Window Icon을 제외한 오브젝트를 스케일할 수 있다.
- Working Set은 형식·레이아웃에 대한 통제권이 없고, Window Icon 오브젝트를 4.7.15.3에 따라 스케일해야 한다.
- Bar graph 타입 창: Working Set이 수평 방향의 Output Linear Bar Graph를 공급해야 하며, 증가 방향은 자유지만 왼쪽→오른쪽이 권장된다.

| Type | 창 내용 | 오브젝트 참조(순서대로) | Title | Value | Units |
|---|---|---|---|---|---|
| 1 / 10 | Numeric Output + Units (1×1 / 2×1) | Output Number, Output String(단위) | 11 / 20자 | 5 / 10자 | 5 / 9자 |
| 2 / 11 | Numeric Output, no Units | Output Number | 11 / 20자 | 11 / 20자 | — |
| 3 / 12 | String Output | Output String | 11 / 20자 | 11 / 20자 | — |
| 4 / 13 | Numeric Input + Units | Input Number, Output String(단위) | 11 / 20자 | 5 / 10자 | 5 / 9자 |
| 5 / 14 | Numeric Input, no Units | Input Number | 11 / 20자 | 11 / 20자 | — |
| 6 / 15 | String Input | Input String | 11 / 20자 | 11 / 20자 | — |
| 7 / 16 | Horizontal Linear Bar Graph | Output Linear Bar Graph | 11 / 20자 | — | — |
| 8 / 17 | Single Button | Button | 11 / 20자 | — | — |
| 9 / 18 | Double Button | Button(왼쪽), Button(오른쪽) | 11 / 20자 | — | — |

숫자 Value 자릿수는 소수점 포함 기준이다.

Button 타입 창에서는 Working Set이 Button 오브젝트와 그 children을 다음 식으로 스케일해야 한다(반내림).

| 창 | Button Width | Button Height |
|---|---|---|
| 1×1 Single Button (type 8) | Window Cell Width × 65 % | Window Cell Height × 57 % |
| 1×1 Double Button (type 9) | Window Cell Width × 30 % | Window Cell Height × 57 % |
| 2×1 Single Button (type 17) | Window Cell Width × 80 % | Window Cell Height × 57 % |
| 2×1 Double Button (type 18) | Window Cell Width × 40 % | Window Cell Height × 57 % |

스케일 팩터가 Data Mask와 다르기 때문에 <strong>같은 Button 오브젝트를 Data Mask와 Window Mask에서 동시에 쓸 수 없다.</strong> VT 쪽에서도 Button 오브젝트는 child 클리핑을 피하기 위해 크기를 유지하거나 키우는 것만 허용된다.

## B.20 Key Group object (Type 35)

VT version 4에서 추가된 부모 오브젝트로, VT의 User-Layout Soft Key Mask에서만 사용된다(4.7.8 참조). Key 오브젝트와 Object Pointer를 담는데, Object Pointer는 Key, 다른 Object Pointer, 또는 NULL만 가리켜야 한다.

- 이 오브젝트에 담긴 Key들은 하나의 그룹이다. VT는 오퍼레이터가 Key 레이아웃을 매핑할 때 이 그룹을 — 보이는 Soft Key 페이지 경계를 넘더라도 — 쪼개지 못하게 하고, 그룹 전체를 함께 매핑하도록 요구해야 한다. 따라서 이 오브젝트 하나가 여러 Key Cell을 차지할 수 있다.
- Working Set은 Key Group 오브젝트를 풀에 넣어 User-Layout Soft Key Mask에 참여한다.
- Key Group은 투명하게 만드는 것이 권장된다. 그러면 VT가 각 child Key의 배경색을 설정해 모든 Key가 같은 배경색을 갖게 할 수 있다. 필요하면 Working Set이 Get Window Mask Data message로 VT의 배경색을 알아낼 수 있다.
- NULL을 가리키는 Object Pointer는 Key 자리 하나를 예약한다(나머지 Key가 앞으로 당겨지지 않고, 뒤의 Key로 탐색 가능).

허용 명령: Change Attribute, Get Attribute Value.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =35 | Key Group |
| Options | 1 | 1 | 0~3 | Bit 0 = Available(0이면 현재 사용 불가 — 매핑 금지, 이미 매핑된 키 셀은 비움), Bit 1 = Transparent(1이면 VT가 child Key들의 배경색 속성을 무시하고 원하는 배경색을 설정) |
| Name | 2 | 2 | 0~65534 | 그룹 이름 문자열 Output String(또는 Object Pointer) ID. VT 독자 매핑 화면에서 사용, 최소 20자 표시 가능해야 함 |
| Key Group Icon | — | 2 | 0~65534, 65535 | 그룹 아이콘 출력 오브젝트 ID(선택). NULL이면 표현은 VT 재량. 배경색을 알 수 없는 매핑 화면에 나타날 수 있으므로 투명 배경은 권장되지 않음 |
| Number of objects | — | 1 | 1~4 | Key/Object Pointer 수. 포인터 역참조 후 기준 Key Group당 <strong>최대 Key 4개</strong> |
| Repeat: {Object ID} | — | 각 2 | 0~65534 | 그룹에 담긴 오브젝트 ID |

## B.21 Object Label Reference List object (Type 40)

VT version 4에서 추가된 오브젝트로, 다른 오브젝트에 String Variable(텍스트 라벨) 그리고/또는 그래픽 지시자(designator)를 라벨로 할당하는 메커니즘이다. <strong>풀에는 이 오브젝트를 최대 1개만</strong> 담을 수 있다.

오브젝트 라벨은 VT의 독자적 화면·팝업 메시지·에디터에서만 쓰이도록 의도됐고, 새 Working Set 설계에 다음 두 용도가 권장된다.

- Working Set 오브젝트에 텍스트 이름 라벨을 제공 — VT가 독자 화면·알람에서 Working Set들을 구별하는 데 사용(예: "Planter").
- 모든 입력 오브젝트에 라벨 제공 — VT의 팝업 에디터 창이 포커스된 입력 오브젝트를 가릴 수 있으므로, 에디터 창에 라벨을 표시해 오퍼레이터가 무엇을 편집 중인지 알 수 있게 한다.

운영 규칙:

- 라벨은 독자 화면용이므로 이미 표시 중인 라벨을 런타임에 바꿔도 기존 표시가 즉시 갱신되지 않을 수 있다. 변경은 라벨이 다음에 나타날 때(예: 팝업 에디터를 닫았다 다시 열 때) 보이면 된다.
- 32자를 넘는 문자열은 VT가 32자로 클리핑할 수 있다. 그래픽 지시자는 Soft Key designator 영역에 맞아야 하고, Table A.2의 Object Label graphic representation에 나열된 오브젝트만 담을 수 있다.
- 한 오브젝트에 라벨을 둘 이상 할당할 수 없다. 라벨 대상 Object ID가 목록에 두 번 이상 나오면 <strong>풀 전체가 거부된다.</strong> 라벨로 쓰인 오브젝트 자신이 라벨을 갖고 있으면 그 라벨은 표시하지 않는다.
- 라벨을 비활성화하려면 String Variable 참조와 그래픽 참조를 둘 다 NULL로 두면 되고, VT는 그 경우 라벨을 표시하지 않도록 설계돼야 한다.

허용 명령: Change Object Label, Get Attribute Value.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =40 | Object Label Reference List |
| Number of Labelled objects | [1] | 2 | 0~65535 | 라벨 항목 수. 항목당 7바이트 |
| Repeat: {Object ID} | — | 2 | 0~65534 | 라벨을 붙일 대상 오브젝트 ID |
| {String Variable reference} | — | 2 | 0~65535 | 라벨 문자열을 담은 String Variable ID, 텍스트 없으면 FFFF₁₆ |
| {Font type} | — | 1 | 0~255 | 글꼴 타입(Annex K). String Variable 참조가 NULL이거나 WideString이면 무시 |
| {Object Label graphic representation} | — | 2 | 0~65535 | 그래픽 라벨 오브젝트 ID, 없으면 FFFF₁₆. VT가 그릴 때 Soft Key designator 크기로 클리핑 |

## B.22 External Object Definition object (Type 41)

VT version 5에서 추가. 다른 Working Set이 External Object Pointer를 통해 참조할 수 있도록 <strong>공개하는 오브젝트 목록</strong>을 정의한다. 비휘발성 메모리에서 풀이 로드될 때 VT는 모든 External Object Definition의 Enable 비트를 클리어해야 한다. 허용 명령: Change Attribute, Change List Item, Get Attribute Value.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =41 | External Object Definition |
| Options | 1 | 1 | 0~1 | Bit 0 = Enabled. TRUE면 NAME으로 식별된 WS가 목록의 오브젝트를 External Object Pointer로 참조 가능. FALSE면 비활성(무시) |
| NAME 0 / NAME 1 | 2, 3 | 각 4 | — | 참조를 허용할 WS Master NAME의 바이트 1~4 / 5~8. NAME 갱신 전에 Enabled 비트를 먼저 끄는 것이 권장 |
| Number of objects | — | 1 | 0~255 | 목록 크기(0 가능) |
| Repeat: {Object ID} | — | 각 2 | 0~65534, 65535 | 외부에서 참조 가능한 오브젝트 목록. NULL은 placeholder. Change List Item으로 교체 가능 |

## B.23 External Reference NAME object (Type 42)

VT version 5에서 추가. External Object Pointer로 <strong>참조할 대상</strong> WS의 WS Master를 식별한다. 역시 비휘발성 로드 시 Enable 비트가 클리어된다. 허용 명령: Change Attribute, Get Attribute Value. Change Attribute가 오면 이 오브젝트를 참조하는 표시 중인 모든 External Object Pointer를 재평가한다.

| 속성 | AID | 크기(B) | 설명 |
|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | Type = 42 |
| Options | 1 | 1 | Bit 0 = Enabled. FALSE면 이 오브젝트를 참조하는 External Object Pointer는 모두 invalid로 간주 |
| NAME 0 / NAME 1 | 2, 3 | 각 4 | 참조 대상 WS Master NAME의 바이트 1~4 / 5~8 |

## B.24 External Object Pointer object (Type 43)

VT version 5에서 추가. <strong>다른 Working Set의 오브젝트 풀에 있는 오브젝트를 자기 화면에 표시</strong>할 수 있게 하는 포인터다. 포인터 값을 바꾸면 같은 자리에 다른 오브젝트를 참조할 수 있다. NULL을 가리키면 Default Object가 그려진다.

Default Object가 그려지는 조건:

- External Object Pointer(또는 그 뒤에 이어진 Object Pointer)가 NULL을 가리킬 때
- 오브젝트 계층 규칙(Table A.2) 기준으로 참조 대상의 child가 invalid일 때

비휘발성 메모리에서 풀이 로드되면 VT는 모든 External Object Pointer의 External Object ID 속성을 NULL로 설정한다. 이는 WS가 External Object ID를 다시 갱신하도록 강제한다.

:::info 소유권과 이벤트 컨텍스트
External Object Pointer로 참조된 오브젝트(및 계층)의 소유·통제권은 여전히 원 부모 Working Set과 그 오브젝트 풀에 있다.

- 참조된 오브젝트에 정의된 이벤트·매크로는 <strong>원 부모 오브젝트 풀의 컨텍스트</strong>에서 실행된다. 예를 들어 참조된 Button의 On Key Press 매크로 실행 결과 메시지는 참조한 WS가 아니라 원 부모 WS로 전송되며, 매크로가 일으키는 추가 이벤트도 원 부모 풀 컨텍스트에서 실행된다.
- 원 부모 WS가 참조된 오브젝트의 속성을 바꾸는 명령을 보내면, 그 오브젝트는 표시 중인 참조 마스크·부모 안에서도 갱신된다. 그리기에 쓰이는 모든 속성(현재 Colour Map·Colour Palette 포함)은 원 부모 풀의 컨텍스트에서 온다.
- <strong>참조하는 WS가 다른 WS에서 참조한 오브젝트에 직접 명령을 보내거나 매크로를 만드는 것은 허용되지 않는다.</strong>
- 참조된 오브젝트와 관련된 모든 메시지(내비게이션·데이터 입력 등)는 VT가 참조한 WS가 아니라 <strong>원 부모 WS로</strong> 보낸다. 이때 메시지에 "Parent ID"·"Parent Mask" 류 속성이 필요하면 VT는 원 부모 풀의 External Object Definition 오브젝트 ID를 쓴다(참조 WS의 NAME에 할당된 External Object Definition이 여럿이면 어느 것을 쓸지는 VT 재량). 이는 수신 WS가 활성 WS가 아니어도, 다른 WS의 컨텍스트에서 이벤트가 일어났음을 알리는 특별한 통지다.
:::

허용 명령: Change Numeric Value, Change Attribute, Get Attribute Value.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =43 | External Object Pointer |
| Default Object ID | 1 | 2 | 0~65535 | External Object ID가 무효거나 NULL일 때 표시할 오브젝트(항상 자기 풀의 오브젝트) |
| External Reference NAME ID | 2 | 2 | 0~65535 | External Reference NAME 오브젝트 ID 또는 NULL |
| External Object ID | 3 | 2 | 0~65535 | 참조 대상 오브젝트 ID 또는 NULL. NAME으로 식별된 WS Master의 풀에서 찾으며, 해당 External Object Definition에 나열돼 있어야 함 |

## B.25 Animation object (Type 44)

VT version 5에서 추가. 오브젝트 ID 목록 중 Value(인덱스)가 가리키는 하나를 그려 애니메이션을 표현한다.

동작 규칙:

- VT 성능은 예측할 수 없으므로 개별 오브젝트는 작게, 리프레시 주기는 적당히(200 ms 이상 권장) 잡아야 한다. Refresh Interval 속성은 제안값일 뿐 VT가 보장하지 않으며, VT가 제한·수정할 수 있다.
- 오브젝트가 enabled이고 리프레시 주기가 0이 아니며 활성 마스크의 보이는 멤버일 때, 주기가 만료되면 VT가 인덱스 Value를 증가시킨다. 보이지 않으면 타이머가 정지돼 인덱스가 증가하지 않는다. 여러 인스턴스가 보이면 모두 같은 참조 오브젝트를 표시하며, Refresh Interval은 오브젝트 기준이라 인스턴스 수와 무관하다.
- 인덱스 증가 준비 시 First/Last Child Index로 범위 검사를 한다. Value < First Child Index면 First Child Index로 맞춘 뒤 증가시키고(이 경우 First Child Index의 오브젝트는 표시되지 않음), Value > Last Child Index면 Last Child Index로 맞춘 뒤 Options의 Animation Sequence에 따라 동작한다.
- 목록에는 First~Last Child Index 범위보다 많은 child를 담을 수 있다. First/Last Child Index 속성만 바꿔 새 목록 업로드 없이 애니메이션을 교체할 수 있다.
- 표시하지 않는 조건은 Output List와 같고(인덱스 255, 범위 초과, NULL placeholder, NULL Object Pointer, hidden Container), 추가로 enabled 상태에서 0 ≤ First Child Index ≤ Last Child Index, 0 ≤ Last Child Index < 항목 수, 0 ≤ Default Child Index < 항목 수 중 하나라도 깨지면 표시하지 않는다.
- 런타임에 WS가 인덱스 Value를 바꾸면 현재 리프레시 주기가 재시작되고 선택된 오브젝트가 그려진다.

애니메이션 시퀀스 모드(Options bit 0):

| 모드 | 동작 |
|---|---|
| Single Shot (0) | 인덱스를 First Child Index로 초기화해 한 번만 재생하고 Last Child Index에서 정지. 오브젝트가 enabled인 동안 마지막 child가 계속 표시됨. 인덱스 변경 또는 disable 후 re-enable(인덱스가 First로 리셋됨)로 재생을 바꾸거나 반복할 수 있음. 풀에서 처음부터 enabled면 최초 표시 시 Index Value가 가리키는 child부터 재생 |
| Loop (1) | enabled인 동안 반복. Last Child Index의 child를 표시한 뒤 인덱스를 First Child Index로 리셋하고 반복 |

disable 시 표현 모드(Options bit 1~2, Disabled Behaviour):

| 모드 | 동작 |
|---|---|
| Pause (0) | 인덱스 유지, 해당 child 표시. 애니메이션 child를 건너뛰지 않고 enable/disable 가능 |
| Reset to First (1) | 인덱스를 First Child Index로 리셋하고 그 child 표시 |
| Default Object (2) | 인덱스는 유지하되 Default Child Index의 child 표시 |
| Blank (3) | 인덱스 유지, 아무것도 표시하지 않음 |

허용 명령: Enable/Disable Object, Change Numeric Value, Change Attribute, Change List Item, Change Size, Get Attribute Value.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =44 | Animation |
| Width, Height | 1, 2 | 각 2 | 0~65535 | 영역 크기, 초과분 클리핑 |
| Refresh Interval | 3 | 2 | 0~65535 | 리프레시 간격(ms). 0이면 타이머 정지(단, enabled = 0과 동등하지 않음) |
| Value | 4 | 1 | 0~254, 255 | 표시할 리스트 인덱스(첫 항목 = 0) |
| Enabled | 5 | 1 | 0/1 | 1 = 애니메이션 동작, 0 = 정지 |
| First / Last / Default Child Index | 6, 7, 8 | 각 1 | 0~254 | 시퀀스의 첫/끝/기본 child 인덱스 |
| Options | 9 | 1 | 0~7 | Bit 0 = Animation Sequence(0 = Single Shot, 1 = Loop), Bit 1~2 = Disabled Behaviour(0 = Pause, 1 = Reset to First, 2 = Default Object, 3 = Blank) |
| Repeat: {Object ID, X, Y} | — | 각 2 | — | child 오브젝트 ID와 Animation 좌상단 기준 상대 위치(child당 6바이트) |

## B.26 Colour Palette object (Type 45)

VT version 6에서 추가. 이 Working Set이 쓰는 <strong>VT 표준 색 팔레트 자체를 교체</strong>한다. VT 색 번호 순서로 최대 256개의 ARGB 값을 담아 Working Set이 사용할 색을 완전히 정의할 수 있다.

- 풀에는 Colour Palette를 0개 이상 담을 수 있다. 풀 로드 후 VT는 Working Set Special Controls 오브젝트가 정의한 팔레트를 사용하며, 그 Working Set 풀의 모든 오브젝트가 해당 팔레트로 표시된다. 표시 색 결정 과정에서 Colour Map 오브젝트도 함께 작동할 수 있다.
- "Number of ARGB values" 속성으로 색 0부터 시작하는 팔레트의 부분 집합만 재정의할 수 있다. 교체 Colour Palette가 포함된 풀 업데이트가 처리되면 VT는 먼저 그 Working Set의 팔레트를 VT 표준 팔레트로 초기화한 뒤 새 오브젝트 기준으로 갱신한다.
- Alpha 채널로 표현력이 높아지지만, 아래에 깔린 오브젝트 색을 설계자가 통제할 수 없는 곳에서는 투명도를 피해야 한다(예: Data Mask 배경색의 투명 — 마스크 아래 색을 알 수 없음. External Object Pointer로 참조될 수 있는 Button의 투명도도 비권장).
- ARGB 값은 리틀엔디언으로 배치돼 바이트 순서가 <strong>B, G, R, A</strong>가 된다.

허용 명령: Change Attribute, Get Attribute Value.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =45 | Colour Palette |
| Options | 1 | 1 | 0 | 예약, 0으로 전송 |
| Number of ARGB values | — | 2 | 0~256 | 뒤따르는 팔레트 엔트리 수 |
| Repeat: {B, G, R, A} | — | 각 1 | 0~255 | 엔트리당 4바이트. A는 0(투명)~255(불투명) |

## B.27 Graphic Data object (Type 46)

VT version 6에서 추가. 그래픽 표현용 원시 데이터를 담는다. <strong>완전한 색 팔레트를 오브젝트 내부에 포함</strong>하므로, 다른 오브젝트와 달리 Colour Map이나 Colour Palette의 영향을 받지 않는다. 허용 명령: 없음.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =46 | Graphic Data |
| Format | [1] | 1 | 0 | 그래픽 타입: 0 = PNG(최대 32bit RGBA로 제한) |
| Number of bytes in raw data | — | 4 | 0~2³²−1 | 원시 데이터 바이트 수 |
| Repeat: {raw data} | — | 1 | — | 포맷에 따라 해석되는 원시 바이트 |

## B.28 Scaled Graphic object (Type 48)

VT version 6에서 추가. 참조된 그래픽 오브젝트를 실제 크기에서 목표 폭·높이로 <strong>스케일해 표시</strong>한다. Scaled Graphic에서 참조될 때 Picture Graphic의 target width 속성은 무시된다. 허용 명령: Change Attribute, Change Numeric Value(Value 속성 대상), Get Attribute Value.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =48 | Scaled Graphic |
| Width, Height | 1, 2 | 각 2 | 0~65535 | 목표 폭·높이(픽셀) |
| ScaleType | 3 | 1 | 0~127 | Bit 0~2 = 스케일 방식: 0 = 스케일 없음(원시 크기 그대로), 1 = 폭 기준 비율 유지, 2 = 높이 기준 비율 유지, 3 = 폭·높이 모두 맞춤(왜곡 가능), 4 = 비율 유지하며 영역에 맞는 최대 크기. Bit 3~4 = 수평 정렬(0 = Left, 1 = Middle, 2 = Right), Bit 5~6 = 수직 정렬(0 = Top, 1 = Middle, 2 = Bottom) |
| Options | 4 | 1 | 0~1 | Bit 0 = Flashing(스타일·주기는 VT 재량) |
| Value | 5 | 2 | 0~65535 | 그래픽 오브젝트(Graphic Data 또는 Picture Graphic) 또는 그를 가리키는 Object Pointer의 ID. NULL이면 아무것도 표시하지 않음 |

## B.29 Working Set Special Controls object (Type 47)

VT version 6에서 추가. Working Set의 <strong>초기 Colour Map·초기 Colour Palette</strong>, 그리고 Working Set 오브젝트의 언어 목록을 대체하는 언어·국가 코드 쌍 목록을 정의한다.

- "Number of bytes to follow" 속성으로 확장 가능하게 정의돼 있어, 파서가 인식 못 하는 기능을 건너뛰고 다음 오브젝트를 찾을 수 있다(전방·후방 호환).
- 풀에는 이 오브젝트를 0 또는 1개 담을 수 있다. 오브젝트나 그 속성(AID 2 이상)이 없으면 VT는 해당 속성의 NULL 상당값을 사용한다.
- NULL이 아닌 Colour Map·Colour Palette 참조는 오브젝트 풀의 <strong>첫 렌더링 전에</strong> 활성화된다.
- Working Set이 Select Colour Map or Palette 명령이나 이 오브젝트를 대상으로 한 Change Attribute 명령을 보내면 이 오브젝트의 속성이 갱신되며, VT는 화면 전체나 일부를 다시 그려야 할 수 있다.
- 언어·국가 코드 쌍이 하나 이상 제공되면 Working Set 오브젝트의 언어 목록은 무시된다.

허용 명령: Get Attribute Value.

| 속성 | AID | 크기(B) | 범위 | 설명 |
|---|---|---|---|---|
| Object ID / Type | —/[0] | 2/1 | =47 | Working Set Special Controls |
| Number of Bytes to follow | [1] | 2 | 5~65535 | 이후 바이트 수(버전 확장 대비 파싱용) |
| Colour Map object ID | [2] | 2 | 0~65535 | 초기 Colour Map, NULL이면 미사용 |
| Colour Palette object ID | [3] | 2 | 0~65535 | 초기 Colour Palette, NULL이면 VT 표준 팔레트 |
| Number of language pairs | — | 1 | 0~255 | 언어 쌍 수 |
| Repeat: {Language Code, Country Code} | — | 각 2 | — | ISO 639-1 언어 2자 + ISO 3166-1 국가 2자(해당 없으면 20₁₆ 20₁₆). 표준 개정 대비 a-z·A-Z 전 조합 허용 |

## Annex C (normative) — Object transport protocol

### C.1 VT 메시지와 오브젝트 전송

Working Set → VT, VT → Working Set 명령은 Annex C의 PGN으로 전송한다. <strong>Working Set Master만</strong>(Member 불가) Annex C의 명령을 보낼 수 있고, 발신 마스터는 응답을 받기 전에는 다음 명령을 보내지 않아야 한다.

VT 메시지 프로토콜에 예약된 PGN 두 개:

| 방향 | PGN | PDU format | PDU specific | 기본 우선순위 |
|---|---|---|---|---|
| VT → ECU | 58880 (00E600₁₆) | 230 | 목적지 주소 | 5 |
| ECU → VT | 59136 (00E700₁₆) | 231 | 목적지 주소 | 5 |

기본 우선순위 5는 ISO 11783-3의 권고를 따른 것으로, VT version 5 이전 문서에는 7로 적혀 있었다.

- Working Set Master는 풀을 구축하기 전에 Get Technical Data 메시지(Annex D)로 VT 특성 정보를 얻어 풀을 VT 능력에 맞출 수 있다.
- 계산된 데이터 길이가 8바이트 미만인 모든 VT↔ECU 메시지는 FF₁₆으로 8바이트까지 패딩한다.
- 두 PGN은 Group Function 메시지다. 첫 바이트에 미지·예약 명령이 있는 메시지를 받은 CF는 Unsupported VT Function message(v5) 또는 VT Unsupported VT Function message로 응답해야 한다(v5 이전에는 동작 미정의).

### C.2 오브젝트 풀 구축

<strong>C.2.1 개요</strong>

풀은 single packet(비권장), ISO 11783-3의 TP(transport protocol)·ETP(extended TP)로 VT에 전송한다. 목적지 지정 메시지와 Connection Management를 구현해야 한다. 풀은 하나의 큰 데이터 블록로 취급되며, 각 오브젝트와 속성이 하나의 가변 길이 레코드를 이룬다. 총 크기가 일반 TP 한계인 <strong>1 785바이트</strong>를 넘으면 ETP를 써야 하고, VT는 모든 전송 프로토콜 기능을 지원해야 한다.

- VT는 수신한 오브젝트를 파싱·저장한다. 파싱 중 기존 ID와 같은 ID의 새 오브젝트를 만나면 <strong>기존 오브젝트의 교체</strong>로 처리한다.
- 1바이트보다 큰 데이터·속성은 항상 리틀엔디언(LSB 먼저)으로 전송한다.
- Working Set Master는 접속된 VT 하드웨어와 보고된 VT 버전에 맞게 조정된 "깨끗한" 풀을 전송해야 한다. 파싱·표시가 제대로 안 되는 무효 풀(무효 색 등)을 보내 놓고 나중에 change 명령으로 고치는 방식은 허용되지 않는다 — 파싱 오류·오류 표시를 유발하고, VT가 해당 오브젝트·매크로를 무시하거나 풀을 휘발성 저장소에서 삭제하고 Working Set을 중단시킬 수 있다.
- VT는 무효 풀을 식별하고 오퍼레이터에게 알려야 한다(통지는 나중으로 미룰 수 있음 — 예: 무효 참조를 담은 Data Mask 활성화 시점). End of Object Pool response의 오류 코드나 VT Change Active Mask 메시지의 오류가 무효 풀 식별을 나타낸다. VT가 무효 풀로 계속 진행하기로 해도, Working Set Master는 오류 표시를 받으면 안전 상태로 갈 수 있다.

<strong>C.2.2 오브젝트 풀 전송 절차</strong>

1. Working Set Master가 Get Memory message(D.2)로 VT 메모리 가용성을 확인한다. VT는 Get Memory response로 응답한다(이 요청으로 풀 메모리를 할당하는 VT 설계도 가능). 오류가 없으면 진행하고, 메모리가 부족하면 더 작은 값(예: 축소 기능 풀 크기)으로 재시도한다.
2. single packet(비권장)·TP·ETP 또는 이들의 조합으로 Object pool transfer message(C.2.3)를 이용해 풀을 옮긴다. ISO 11783-3에 따른 정상 핸드셰이킹·오류 검사·재전송을 구현해야 한다. 다른 풀이 로드되는 동안 VT가 패킷 수 0의 CTS를 보낼 수 있고 이것이 상당 시간 지속될 수 있음을 알아야 한다.
   - 전체 풀을 여러 세션(single packet/TP/ETP 조합)으로 나눠 보낼 수 있고, End of Object Pool message 전에 몇 세션이든 보낼 수 있다.
   - 오브젝트 레코드는 세션 안에서 완결돼야 하고 TP/ETP 세션 사이에서 "쪼개지면" 안 된다. single packet 전송은 완전한 오브젝트를 담아야 한다.
   - 오브젝트 레코드가 없는 전송 세션은 허용되지 않는다.
3. Working Set Master가 End of Object Pool message(C.2.4)를 보내 풀 완성을 알린다.
   - VT는 이 메시지를 받으면 파싱을 마치고 End of Object Pool response를 보낼 때까지 VT Status message의 "parsing" 비트를 1로 설정한다.
   - Working Set Master는 "parsing" 비트가 0인 VT Status message가 <strong>연속 3번</strong> 수신될 때까지 End of Object Pool response를 기다려야 한다(이미 송신 큐에 있던 Status message가 파싱 상태를 잘못 나타내는 경쟁 상태를 피하기 위함).
   - response를 받지 못하면 End of Object Pool message가 VT에 도달하지 않았다고 가정하고 최대 3회 재시도할 수 있으며, 그래도 안 되면 VT의 예기치 못한 셧다운으로 간주하고 4.6.9(Connection management) 요구를 따른다.
   - response가 풀 삭제를 나타내면 절차를 재시도할 수 있다(예: 메모리 부족 응답 후 축소 기능 풀 선택).

<strong>C.2.3 Object pool transfer message</strong> (ECU → VT, 가변 길이)

| 바이트 | 내용 |
|---|---|
| 1 | VT function = 17 (bits 7~4 = 0001 Command, bits 3~0 = 0001 Object Pool Transfer) |
| 2~n | 오브젝트 풀 레코드 |

이 메시지에는 응답이 없으므로, 한 패킷에 들어가는 단일 오브젝트라도 single packet으로 보내지 않는 것이 권장된다.

<strong>C.2.4 End of Object Pool message</strong> (ECU → VT, 8바이트)

풀이 완성돼 사용 준비가 됐음을 알린다. 최초 풀 정의 후는 물론, 운영 중 오브젝트를 재정의·추가한 뒤에도 보낸다. 바이트 1 = VT function 18, 바이트 2~8 = FF₁₆.

<strong>C.2.5 End of Object Pool response</strong> (VT → ECU, 8바이트)

VT가 어떤 종류든 오류로 응답하는 경우, VT는 풀을 휘발성 메모리에서 삭제하고 Working Set 중단을 알람 방식으로 오퍼레이터에게 알리고 삭제 사유를 표시해야 한다. 이 응답을 받은 책임 ECU는 장치 전체의 안전한 셧다운 절차를 제공하는 fail-safe 운전 모드로 들어가야 한다. VT의 풀 파싱은 오래 걸릴 수 있으며, response는 파싱 완료까지 지연되고 그동안 VT Status message가 파싱 중 상태를 반영한다.

| 바이트 | 내용 |
|---|---|
| 1 | VT function = 18 |
| 2 | Error Codes(0 = 오류 없음): Bit 0 = 풀에 오류 있음(바이트 3~8 참조), Bit 1 = 전송 중 VT 메모리 고갈, Bit 4 = 기타 오류 |
| 3, 4 | 결함 오브젝트의 부모 Object ID(오류 없으면 NULL) |
| 5, 6 | 결함 오브젝트의 Object ID(오류 없으면 NULL) |
| 7 | Object Pool Error Codes: Bit 0 = VT가 지원하지 않는 방법·속성, Bit 1 = 미지의 오브젝트 참조(누락 오브젝트), Bit 2 = 기타 오류, Bit 3 = 풀이 휘발성 메모리에서 삭제됨 |
| 8 | 예약(FF₁₆) |

<strong>C.2.6 런타임 풀 업데이트</strong>

Working Set은 운영 중 풀을 수정·추가할 수 있다(예: 문자열 길이를 늘린 교체 오브젝트 전송). 초기 업로드와 같은 메시지·절차를 쓴다.

1. Get Memory message로 메모리를 확인하되, Memory Required 파라미터는 원래 풀 + 업데이트가 아니라 <strong>이번 업데이트 크기 기준</strong>이다. 메모리가 부족하면 복구 방법(풀 삭제 후 축소 기능 풀 전송 등)은 Working Set Master가 결정한다.
2. single packet(비권장)·TP·ETP로 오브젝트를 전송한다.
3. End of Object Pool message로 업데이트 완료를 알리고, 이후는 C.2.2의 3단계와 같다.

- 바뀌어야 하는 오브젝트만 전송하면 되고, 나머지는 VT 메모리에 그대로 유지된다.
- 업데이트에 오류가 있으면 VT는 End of Object Pool response로 알리고, <strong>풀 전체를</strong>(업데이트 전 원본 포함) 휘발성 메모리에서 삭제하며, 알람 방식으로 Working Set 중단과 사유를 알린다.
- VT는 Working Set이 풀을 업데이트하는 동안에도 그 Working Set의 명령·매크로를 처리해야 한다(예: 업데이트 중 오퍼레이터가 Soft Key를 누르면 풀 업데이트 완료를 기다리지 않고 즉시 매크로·명령을 실행).
- VT는 End of Object Pool message 수신 전까지 신규·갱신 오브젝트를 원본 풀과 분리해 유지하고, End of Object Pool response 송신 전에 원본 풀에 병합한다. End of Object Pool message 후 response 수신 전에 신규·갱신 오브젝트에 작용하는 명령을 보내면 원본 풀과 갱신 풀 중 어느 쪽에 적용될지 예측할 수 없으므로, response를 받을 때까지 그런 명령을 보내지 않는 것이 권장된다.
- 풀 업데이트는 처리 시간이 걸리므로, 가능하면 Annex F 명령을 쓰는 편이 낫다(예: Change Size 명령이 새 크기의 오브젝트 재업로드보다 빠름).

## Annex D (normative) — Technical data messages

### D.1 개요

Technical data 메시지는 VT의 특성을 조회하는 요청·응답 쌍이다. <strong>매크로에서는 사용할 수 없다.</strong> Working Set master·member는 물론 어떤 CF든 보낼 수 있다. 응답 파라미터는 VT의 버전에 따라 달라질 수 있으며, Working Set의 버전에 맞춰 조정되지 않는다(VT가 아직 Working Set 버전을 모를 수 있기 때문).

### D.2 Get Memory message / D.3 Get Memory response

Get Memory message(VT function 192, ECU→VT, 8바이트)는 VT의 메모리 부족 여부 확인과 VT 버전 확인에 쓰인다.

- Memory Required 파라미터(바이트 3~6): v3 이하에서는 전송할 풀의 바이트 수. Graphics Context를 지원하는 v4 이상에서는 풀 바이트 수 + 풀에 정의된 모든 Graphics Context 오브젝트(GCO)의 추정 저장량의 합. Working Set은 통보한 양보다 적게 보내도 된다.
- GCO 저장량 추정식: RoundUp(GCO.width ÷ VT.PixelsPerByte) × GCO.height. VT.PixelsPerByte는 모노크롬 = 8, 16색 = 2, 256색 = 1.
- Memory Required = Σ(각 풀 오브젝트 크기) + Σ(각 GCO 크기) (뒤 항은 v4 이상만).
- VT 버전 번호만 알고 싶으면 Memory Required = 0으로 보낸다. 이 메시지 기반으로 메모리를 할당하는 VT 설계라면, Memory Required가 0이거나 발신 CF가 아직 Working Set Master로 식별되지 않았을 때는 할당하지 않아야 한다.

Get Memory response(VT function 192, VT→ECU, 8바이트):

| 바이트 | 내용 |
|---|---|
| 2 | Version Number: 0 = Hannover Agritechnica 2001 한정 기능판, 1 = 2002 FDIS, 2 = 2004 초판, 3·4 = 2010 2판, 5 = 2014 3판, 6 = 2018 4판 |
| 3 | Status: 0 = 메모리가 충분할 수 있음, 1 = 메모리 부족 — 풀을 전송하지 말 것 |

status 0이 "충분할 수 있음"인 이유: 오브젝트 저장에는 오버헤드가 있어서 풀의 정확한 내용을 모르면 충분 여부를 단정할 수 없기 때문이다. 버전은 하위 호환이므로 버전 N용으로 설계된 Working Set이 N보다 높은 버전의 VT를 특별 취급할 필요는 없다. 새 설계는 구버전을 구현하더라도 최신 문서 개정판을 기준으로 해야 한다.

### D.4 / D.5 Get Number of Soft Keys message·response

Soft Key descriptor의 X·Y축 픽셀 수, 사용 가능한 가상 Soft Key 수, 물리 Soft Key 수를 조회한다(VT function 194). v4 이상은 가상 Soft Key 탐색에 쓰는 물리 Soft Key 수도 제공한다.

response 구성:

| 바이트 | 내용 |
|---|---|
| 2 | Navigation Soft Keys — 가상 Soft Key 탐색용 물리 키 수(v4+, v3 이하 FF₁₆) |
| 5 / 6 | X Dots / Y Dots — Soft Key descriptor의 x·y축 픽셀 수 |
| 7 | Virtual Soft Keys — Soft Key Mask의 가능한 가상 Soft Key 수(v3 이하: 6~64, v4 이상: 64 고정) |
| 8 | Physical Soft Keys — 물리 Soft Key 수 |

### D.6 / D.7 Get Text Font Data message·response

글꼴·크기·스타일·색 능력을 조회한다(VT function 195). response는 비트마스크 3개를 반환한다.

| 바이트 | 내용 |
|---|---|
| 6 | Small font sizes: bit 0~7 = 8×8, 8×12, 12×16, 16×16, 16×24, 24×32, 32×32 지원 여부(6×8은 기본이라 비트 없음, 0000 0000 = 6×8만) |
| 7 | Large font sizes: bit 0~6 = 32×48, 48×64, 64×64, 64×96, 96×128, 128×128, 128×192 |
| 8 | Font styles: bit 0~7 = Bold, Crossed out, Underlined, Italics, Inverted, Flash inverted, Flash hidden, Proportional font rendering(v4+, 이 비트는 v3 이하 Working Set에도 전송될 수 있음) |

### D.8 / D.9 Get Hardware message·response

VT의 하드웨어 설계를 조회한다(VT function 199).

| 바이트 | 내용 |
|---|---|
| 2 | Boot time — VT 전원 인가·리셋부터 첫 VT Status message 송신까지 최대 초. 정보 없으면 FF₁₆ (v4+에서 도입, v4 이전에도 허용) |
| 3 | Graphic Type: 0 = 모노크롬(색 0·1, 모노크롬 Picture Graphic만), 1 = 16색(색 0~15, 모노+16색 Picture Graphic), 2 = 256색(색 0~255, 모든 Picture Graphic 포맷) |
| 4 | Hardware 비트: Bit 0 = 터치스크린 + Pointing Event 지원, Bit 1 = 포인팅 장치 + Pointing Event 지원, Bit 2 = 다주파수 오디오 출력, Bit 3 = 볼륨 조절 오디오, Bit 4 = 물리 Soft Key 전 조합 동시 활성 지원, Bit 5 = Button 전 조합 동시 활성 지원, Bit 6 = 드래그 조작을 Pointing Event로 보고(Bit 0 또는 1 필요), Bit 7 = 드래그 중 중간 좌표 지원(Bit 6 필요). Bit 4~7은 v4+ |
| 5, 6 / 7, 8 | X-Pixels / Y-Pixels — Data Mask 영역의 가로/세로 픽셀 수(16-bit). Data Mask는 정사각형이므로 Y는 항상 X와 같음 |

### D.10 / D.11 Get Supported Widechars message·response

v4 이상 전용. VT가 지원하는 WideChar를 조회한다(VT function 193). 한 메시지는 <strong>단일 코드플레인</strong>의 문자만 요청하며(여러 플레인은 여러 메시지), First WideChar ≤ Last WideChar 범위를 담는다. 큰 범위 하나 대신 작은 범위 여러 번으로 나누면 응답 프레임 크기를 줄일 수 있다.

response(가변 길이): 코드플레인, 조회 범위, Error Codes(Bit 0 = 범위 내 부분 범위가 255개 초과, Bit 1 = 코드플레인 오류, Bit 4 = 기타 오류), 범위 수, 그리고 {first WideChar, last WideChar} 쌍의 배열이 이어진다. 오류가 있으면 범위 수는 0이다. CF가 이 메시지를 꼭 쓸 필요는 없다 — VT는 지원하지 않는 문자가 포함돼도 WideString을 표시하며, 코드플레인 0 요청의 응답에는 WideChar 최소 문자 집합이 포함된다.

### D.12 / D.13 Get Window Mask Data message·response

Window Mask를 지원하는 v4 이상 VT 전용(VT function 196). User-Layout Data Mask의 배경색(바이트 2)과 User-Layout Soft Key Mask의 Key Cell 배경색(바이트 3)을 반환한다. Window Mask·Key Group을 투명하게 만들 때 이 값으로 VT 배경색에 맞출 수 있다.

### D.14 / D.15 Get Supported Objects message·response

v4 이상 전용(VT function 197). VT가 지원하는 전체 오브젝트 타입 목록을 조회한다. VT는 지원 필수 타입 전부, 지원하는 선택 타입 전부, 그리고 지원하는 독자(proprietary) 타입을 반환해야 한다. 독자 타입은 접속한 WS에 따라 다를 수 있고 아예 나열하지 않을 수도 있으며, 나열 여부와 무관하게 VT는 독자 오브젝트가 포함된 풀을 거부할 수 있다. <strong>Auxiliary Input Type 1과 Auxiliary Function Type 1은 목록에 넣지 않아야 한다.</strong>

response(8바이트): 바이트 2 = 뒤따르는 바이트 수(미래 호환을 위해 타입 수와 같다고 보장되지 않음), 바이트 3~n = 지원 Object Type의 <strong>오름차순 정렬</strong> 목록(타입당 1바이트). 파싱 중 FF₁₆을 만나면 목록 끝이며 이후 바이트는 무시한다.

### D.16 / D.17 Screen Capture command·response

v6 이상 전용(VT function 198). VT에 무손실 화면 캡처를 요청한다. 주로 테스트 시스템 용도라서 VT 설계자는 기본 비활성으로 두고 독자적 상호작용으로만 활성화하게 할 수 있다(비활성 상태는 응답 오류 코드로 표시). <strong>매크로 사용 불가.</strong>

command: 바이트 2 = Item Requested(0 = Screen Image, 240~255 = 제조사 독자), 바이트 3 = Path(1 = VT 접근 가능 저장소/이동식 미디어, 240~255 = 제조사 독자).

response: 바이트 2~3은 요청값 반향, 바이트 4 = Error Codes(Bit 0 = Screen Capture 비활성, Bit 1 = VT 전송 버퍼 사용 중, Bit 2 = Item 미지원, Bit 3 = Path 미지원, Bit 4 = 이동식 미디어 가득 참/사용 불가, Bit 5 = 기타). 오류가 없고 Path = 1이면 바이트 5~6에 Image Identification number(0~65535)가 온다. VT는 이 번호를 저장 파일명에 인코딩하고(예: IMG00001.PNG) 캡처마다 증가시킨다(파일 시스템 초기 상태에 따라 1부터 시작하지 않을 수 있음). PNG·BMP 같은 일반 파일 포맷으로 SD 카드·USB 등에 저장한다.

### D.18 / D.19 Identify VT message·response

v4 이상 전용(VT function 187). 이 메시지를 받은 VT는 <strong>Alarm Mask가 활성 상태가 아닐 때만</strong> VT Number를 3초간 표시한다. Destination-Global 송신이 의도된 메시지지만 Destination-Specific으로도 보낼 수 있고, 후자의 경우에만 VT가 response를 보낸다. <strong>매크로 사용 불가.</strong>

- VT Number 표시는 VT 독자 영역이라, VT Number의 용도를 알리는 다른 정보를 함께 표시해도 된다.
- VT Number = VT Function Instance + 1이며 1~32 범위다(Function Instance 0~31 대응). 0 기반 번호에 익숙하지 않은 오퍼레이터를 위한 +1 오프셋이다.

## Annex E (normative) — Non-volatile memory operations commands

### E.1 개요

VT는 Working Set별 오브젝트 풀 전체를 비휘발성 저장소에 저장·복원하는 기능을 제공한다. Working Set은 접속 시 메시지 하나로 자기 풀을 비휘발성 저장소에서 휘발성 메모리로 복사해 달라고 요청할 수 있다. 비휘발성 저장 영역의 유무·구성은 VT마다 다르다.

- 저장·복원은 모든 오브젝트 정의를 포함한다. VT 내부에는 저장된 풀을 특정 Working Set에 유일하게 귀속시키는 방법이 있어야 한다. Annex D의 특성(Data Mask 크기 등)을 바꿀 수 있는 VT라면, 저장된 풀을 특정 특성 집합에 연관시키거나 저장된 풀을 삭제하는 내부 방법도 있어야 한다.
- VT 설계에 따라 Working Set당 풀 하나만 또는 임의 개수를 관리할 수 있다. 각 풀은 version label로 식별한다.
- Working Set은 자신의 WS Master <strong>전체 ISO NAME</strong>으로 식별된다. 각 WS Master는 자기 풀 버전만 조작할 수 있고, 다른 Working Set이 만든 버전에 이 부속서의 명령을 수행하면 안 된다. 이 부속서의 명령은 <strong>Working Set Master만</strong> 보낼 수 있다.
- 비휘발성 연산은 얼마나 걸릴지 알 수 없으므로 응답이 지연될 수 있다. VT Status message가 VT의 현재(바쁨) 상태를 반영하고, 비휘발성 연산이 끝난 뒤에야 응답을 보낸다.
- <strong>이 부속서의 메시지는 매크로에서 사용할 수 없다.</strong>

:::info Version label 규칙
Version label은 오퍼레이터에게 표시될 수 있고 파일명으로도 쓰일 수 있다. 그래서 font type 0(ISO 8859-1 Latin 1)의 표시 가능 문자로 구성해야 하고, 정의된 라벨 길이까지 뒤를 공백으로 패딩한다. 다음 문자는 사용 금지: `\` `"` `'` `` ` `` `/` `:` `*` `<` `>` `|` `?`
:::

버전 관리는 VT 버전에 따라 다르다.

- <strong>v4 이하</strong>: version label은 7자 8-bit string. Extended 계열 메시지는 사용 불가.
- <strong>v5 이상</strong>: 7자 또는 <strong>32자</strong> 8-bit string 두 가지이며, 각각에 맞는 메시지를 써야 한다(7자 = E.2~E.9, 32자 = E.10~ Extended 계열).

Working Set은 VT에 저장된 버전들을 탐지해, 자기 현재 소프트웨어 버전에 맞는 버전이 있는지 확인한 뒤에 풀을 VT 오브젝트 버퍼로 복사해야 한다.

### E.2 / E.3 Get Versions message·response

요청 Working Set에 연관된 <strong>7자</strong> version label 목록을 조회한다(function 223). response(function 224, 가변 길이)는 바이트 2 = 버전 문자열 수, 바이트 3~n = 7바이트씩의 version label들이다. 저장된 7자 버전이 없으면 수를 0으로 하고 나머지를 FF₁₆로 채운다. 필요 시 TP·ETP를 쓴다.

### E.4 / E.5 Store Version command·response

현재 오브젝트 풀의 사본을 VT 비휘발성 저장소에 저장한다(function 208). 언제든 보낼 수 있다.

- 사본은 지정한 version label의 버전으로 저장된다. 같은 라벨의 사본이 이미 있으면 덮어쓴다.
- 모든 오브젝트는 <strong>현재 상태 그대로</strong>(현재 속성·입력값 포함) 저장된다.
- 라벨이 전부 공백이면 비휘발성 저장소의 마지막 저장 7자 버전을 덮어쓰고, 그때까지 저장된 7자 버전이 없으면 VT가 오류를 표시한다.

response(function 208)의 바이트 6 = Error Codes: 0 = 저장 성공, Bit 1 = version label 부정확, Bit 2 = 메모리 부족, Bit 3 = 기타 오류.

### E.6 / E.7 Load Version command·response

비휘발성 저장소의 풀 사본을 로드한다(function 209). 이미 로드된 풀이 있으면 덮어쓴다. VT가 긍정 응답하면 Working Set은 모든 오브젝트를 정상 전송한 것처럼 진행할 수 있다. 라벨이 전부 공백이면 마지막 저장 7자 버전을 로드한다.

- VT는 Load Version command를 받으면 풀 파싱을 마치고 Load Version response를 보낼 때까지 VT Status message의 "parsing" 비트를 1로 둔다.
- Working Set Master는 "parsing" 비트 0인 VT Status message가 <strong>연속 3번</strong> 올 때까지 response를 기다리고, 그 시점까지 response가 없으면 command가 VT에 도달하지 않았다고 간주한다(3회 대기 이유는 End of Object Pool과 같은 경쟁 상태 회피).

response(function 209)의 바이트 6 = Error Codes: 0 = 로드 성공, Bit 0 = 파일 시스템 오류·풀 데이터 손상(v4+), Bit 1 = version label 부정확·미지 라벨, Bit 2 = 메모리 부족, Bit 3 = 기타 오류.

### E.8 / E.9 Delete Version command·response

비휘발성 저장소의 7자 버전을 삭제한다(function 210). <strong>비휘발성 저장소에만 작용</strong>하며, 같은 버전이 휘발성 메모리에 로드돼 있어도 그쪽은 보존된다(휘발성 풀 삭제는 Annex F의 Delete Object Pool 명령).

- 라벨이 전부 공백이면 마지막 저장 7자 버전을 삭제한다. 반복하면 매번의 "마지막 저장 버전"이 차례로 삭제된다.
- 라벨이 별표(*) 하나 + 공백 6자면 와일드카드로 해석해, 요청한 Working Set 소유의 <strong>모든 7자 버전 풀을 삭제</strong>한다(v6 이상). 다른 Working Set 소유의 풀은 삭제하지 않는다.

response(function 210)의 바이트 6 = Error Codes: 0 = 삭제 성공(또는 와일드카드 삭제 수행), Bit 1 = version label 부정확·미지 라벨, Bit 3 = 기타 오류.

### E.10 / E.11 Extended Get Versions message·response

v5 이상 전용(function 211). 요청 Working Set에 연관된 <strong>확장(32자)</strong> version label 목록을 조회한다. response(가변 길이)는 바이트 2 = 버전 문자열 수(각 32바이트), 바이트 3~n = 32자 version label들(미사용 바이트는 공백, 8-bit String만 허용)이다. 확장 버전이 없으면 수를 0으로 하고 나머지를 FF₁₆로 채우며, 필요 시 TP·ETP를 쓴다.

### E.12 / E.13 Extended Store Version command·response

v5 이상 전용(function 212, command 길이 33바이트). 현재 풀 사본을 <strong>확장(32자) version label</strong>로 비휘발성 저장소에 저장한다. 동작 규칙은 Store Version과 동일하다 — 언제든 송신 가능, 같은 라벨은 덮어쓰기, 현재 속성·입력값 그대로 저장, 라벨이 전부 공백이면 마지막 저장 확장 버전을 덮어쓰고 저장된 확장 버전이 없으면 오류.

response(8바이트)의 바이트 6 = Error Codes: 0 = 저장 성공, Bit 1 = version label 부정확, Bit 2 = 메모리 부족, Bit 3 = 기타 오류.

### E.14 / E.15 Extended Load Version command·response

v5 이상 전용(function 213, command 길이 33바이트). 확장 version label의 풀 사본을 비휘발성 저장소에서 로드한다. 이미 로드된 풀은 덮어쓰고, 긍정 응답을 받으면 모든 오브젝트를 정상 전송한 것처럼 진행할 수 있으며, 라벨이 전부 공백이면 마지막 저장 확장 버전을 로드한다.

- VT는 command 수신 시 파싱 완료 후 Extended Load Version response를 보낼 때까지 VT Status message의 "parsing" 비트를 1로 유지한다.
- Working Set Master는 "parsing" 비트 0인 VT Status message가 연속 3번 수신될 때까지 response를 기다리고, 그때까지 response가 없으면 command 미도달로 간주한다(경쟁 상태 회피를 위한 3회 대기는 Load Version과 동일).

response(8바이트)의 바이트 6 = Error Codes: 0 = 로드 성공, Bit 0 = 파일 시스템 오류·풀 데이터 손상, Bit 1 = version label 부정확·미지 라벨, Bit 2 = 메모리 부족, Bit 3 = 기타 오류.

### E.16 Extended Delete Version command

v5 이상 전용. 비휘발성 저장소의 확장 버전을 삭제한다. 휘발성 메모리에 같은 버전 사본이 있으면 그쪽은 보존된다(비휘발성 저장소에만 작용, 휘발성 풀 삭제는 F.44 Delete Object Pool 명령).

- 라벨이 전부 공백이면 마지막 저장 확장 버전을 삭제하며, 반복하면 매번의 "마지막 저장 버전"이 차례로 삭제된다.
- 라벨이 별표(*) 하나 + 공백 31자면 와일드카드로 해석해, 요청 Working Set 소유의 모든 확장 버전 풀을 삭제한다(v6 이상). 다른 Working Set 소유의 풀은 삭제하지 않는다.


## Annex E 말미 — Extended Delete Version (E.16~E.17)

Annex E의 마지막 부분은 VT 비휘발성 메모리에서 저장된 오브젝트 풀 버전을 삭제하는 Extended Delete Version 명령/응답이다. 둘 다 VT version 5 이상에서만 사용 가능하다.

**Extended Delete Version command** (ECU→VT, 33바이트, On request)

| 바이트 | 내용 |
|---|---|
| 1 | VT function = 214 (상위 니블 1101 = Non Volatile Memory, 하위 니블 0110 = Extended Delete Version) |
| 2~33 | Version label — 32문자 버전 문자열. 미사용 바이트는 space로 채운다. 8-bit String만 허용 |

**Extended Delete Version response** (VT→ECU, 8바이트)

| 바이트 | 내용 |
|---|---|
| 1 | VT function = 214 |
| 2~5 | Reserved, FF₁₆ |
| 6 | Error Codes (0 = 에러 없음: 삭제 성공 또는 wild card 삭제 수행)<br>Bit 1 = Version label이 잘못되었거나 알 수 없음<br>Bit 3 = 기타 에러 (Bit 0, 2는 Reserved) |
| 7~8 | Reserved, FF₁₆ |

## Annex F (normative) — Command·Macro 메시지

### F.1 일반 원칙

Working Set이 VT에게 보내는 명령 메시지 모음이다. 핵심 규칙은 다음과 같다.

- 명령은 Annex C에 정의된 PGN으로 전송하며, Working Set Master뿐 아니라 멤버도 보낼 수 있다.
- VT는 해당 Working Set의 오브젝트 풀이 로드되어 있지 않아도 이 명령들에 응답해야 한다.
- 송신자는 응답을 받은 뒤 다음 명령을 보내는 것이 원칙이다. 단, <strong>1,5 s</strong> 안에 응답이 없으면 다음 명령을 보낼 수 있다.
- Working Set은 이전 명령을 재전송할 수 있다(통상 3회 이하). 단 "Change Child Location"처럼 반복 시 누적 효과가 생기는 명령은 재전송에 주의해야 한다.
- 이 Annex의 명령은 별도 언급이 없는 한 Macro 안에서도 사용할 수 있다.
- 응답 메시지에 명령과 동일한 속성 필드가 존재하면, 그 값은 <strong>명령에서 받은 값 그대로</strong> 되돌려준다. 즉 응답 프레임은 명령을 반영하는 것이지 오브젝트의 실제 상태를 반영하는 것이 아니다. 예를 들어 disable이 불가능한 상태의 오브젝트에 Enable/Disable Object(disable)를 보내면, 응답에도 disable 값이 실리고 Error Code로 실패 원인을 알린다.

:::tip 응답 타임아웃 설계
VT가 디스플레이 리프레시와 명령 응답을 결합해 처리하면 Working Set 쪽에서 응답 타임아웃이 날 수 있다. 표준은 응답 생성을 리프레시와 분리(decouple)하는 설계를 권하지만, 이 경우 Working Set과 VT 간 동기화 문제가 생길 수 있음을 함께 경고한다.
:::

### F.2~F.3 Hide/Show Object

Container 오브젝트의 표시/숨김을 제어한다. 가시성뿐 아니라 "기억되는 상태(remembered state)"에도 영향을 준다.

**command** (VT function = 160, ECU→VT, 8바이트, Macro 허용)

| 바이트 | 내용 |
|---|---|
| 2, 3 | Object ID (Container) |
| 4 | 0 = Hide, 1 = Show |
| 5~8 | Reserved, FF₁₆ |

**response** (VT→ECU, Macro 불가) — Byte 2~4는 명령과 동일 반향, Byte 5 = Error Codes: Bit 0 = 누락된 child 오브젝트 참조, Bit 1 = Invalid Object ID, Bit 2 = Command error, Bit 4 = 기타 에러. 누락 child 참조 검증은 즉시 보고할 수도 있고, Container가 실제로 표시되는 시점까지 미뤄 VT Change Active Mask 메시지로 보고할 수도 있다(VT 설계 재량).

### F.4~F.5 Enable/Disable Object

입력 필드 오브젝트·Button 오브젝트의 접근 가능성(accessibility), 그리고 Animation 오브젝트의 동작을 제어한다. 이미 enable된 오브젝트를 다시 enable하거나 이미 disable된 것을 다시 disable하는 것은 허용되며, 이때 응답은 "no errors"이고 매크로도 실행된다. VT version 3 이하는 Button의 enable/disable을 지원하지 않는다.

**command** (VT function = 161, 8바이트, Macro 허용): Byte 2,3 = Object ID / Byte 4 = 0 Disable, 1 Enable.

**response** Byte 5 Error Codes: Bit 1 = Invalid Object ID, Bit 2 = Enable/Disable 명령 값 오류, Bit 3 = 완료 불가(해당 입력 오브젝트가 현재 수정 중), Bit 4 = 기타 에러.

### F.6~F.7 Select Input Object

입력 필드·Button·Key 오브젝트를 강제로 선택(포커스)하거나 입력용으로 여는 명령이다. VT는 선택된 오브젝트를 운전자가 인지할 수 있게 표시해야 한다. 대상이 disable 상태이거나 보이지 않으면 에러 코드를 반환한다. 같은 마스크에 대상 오브젝트가 여러 번 포함되어 있으면 어느 인스턴스가 선택되는지는 VT 재량이다.

- 이 명령으로 오브젝트가 입력 활성화되어도 값 자체는 바뀌지 않는다(예: Input Boolean이 토글되지 않음).
- 운전자 조작에 의한 선택 변경은 반대 방향 메시지인 VT Select Input Object message(H.8)로 통지된다.
- VT version 3 이하는 Button/Key 선택을 지원하지 않는다.

**command** (VT function = 162, 8바이트, Macro 허용)

| 바이트 | 내용 |
|---|---|
| 2, 3 | Object ID. NULL이면 아무것도 선택하지 않음(포커스 제거). 이때 Byte 4는 FF₁₆이어야 함 |
| 4 | Option: FF₁₆ = 포커스 설정(또는 NULL이면 포커스 제거), 0 = 해당 오브젝트를 데이터 입력용으로 활성화(Button·Key에는 무효, Input Boolean은 VT 설계에 따라 무효일 수 있음, VT version 4 이상) |

**response** Byte 4 = Response: 0 = 선택 안 됨(또는 NULL 오브젝트, 또는 에러), 1 = 선택됨, 2 = 편집용으로 열림(v4 이상). Byte 5 Error Codes: Bit 0 = 오브젝트 disabled, Bit 1 = Invalid Object ID, Bit 2 = 오브젝트가 활성 마스크에 없거나 숨겨진 Container 안에 있음, Bit 3 = 완료 불가(다른 입력 필드 수정 중 또는 Button/Soft Key 홀드 중), Bit 4 = 기타 에러, Bit 5 = Option 값 오류(v4 이상). 화면 밖이거나 폭/높이 0인 오브젝트라도 enable 상태이고 숨김 Container 안이 아니면 선택·편집 열기 모두 가능하며 에러가 아니다.

### F.8~F.9 ESC

운전자 입력을 중단(abort)시키는 명령이다. **command** (VT function = 146, 8바이트, Macro 불가): Byte 2~8 모두 Reserved(FF₁₆). **response**: Byte 2,3 = 에러가 없을 때 입력이 중단된 Object ID, Byte 4 Error Codes: Bit 0 = 열려 있는 입력 필드가 없어 ESC 무시됨, Bit 4 = 기타 에러.

### F.10~F.11 Control Audio Signal

VT의 오디오(비프음)를 제어한다. 동작 규칙:

- 새 명령 수신 시 같은 Working Set이 진행 중이던 오디오는 종료되고 새 명령으로 대체된다. 단 Alarm Mask에 연동된 음향 신호는 이 대체 규칙의 예외다. 이전 명령 종료 시 톤이 순간적으로 끊길 수 있다.
- 연속음(continuous tone)은 권장하지 않지만, 255회 활성화 × 65 535 ms = 약 278분의 연속음이 가능하다. 부족하면 만료 전에 명령을 추가로 보내면 된다.
- 단일 Working Set만 지원하는 VT가 다른 Working Set의 명령을 처리 중이면 응답에 "Audio device busy"를 표시한다. 복수 Working Set 동시 지원("multisound") VT는 능력 한도까지 명령을 수락한다.
- 명령으로 생성되는 오디오는 일반 VT 메시지 처리 이상으로 큐잉·지연되어서는 안 된다.
- 이 명령은 현재 활성 Working Set과 무관하게 동작한다. 즉 비활성 Working Set도 오디오를 울릴 수 있다.

multisound 미지원 VT에서는 Alarm Mask의 음향이 발생하면 기존 Working Set의 오디오가 종료되고(그림 F.1), multisound 지원 VT에서는 각 Working Set의 오디오가 끊기지 않고 겹쳐 재생된다(그림 F.2).

**command** (VT function = 163, 8바이트, Macro 허용)

| 바이트 | 내용 |
|---|---|
| 2 | Activations: 0 = 해당 Working Set의 진행 중 오디오 종료(주파수·시간 값 무시), 1~255 = 활성화 횟수 |
| 3, 4 | 주파수(Hz). VT의 재생 가능 범위를 벗어나면 VT가 범위 내로 제한 |
| 5, 6 | On-time(ms). VT 최소 제어 단위보다 작으면 최소 단위로 조정 |
| 7, 8 | Off-time(ms). 동일 조정 규칙. On-time이 0이면 무시하고 0 사용 |

**response**: Byte 2 Error Codes: Bit 0 = Audio device busy, Bit 4 = 기타 에러.

### F.12~F.13 Set Audio Volume

발행 Working Set의 이후 Control Audio Signal 명령에 적용되는 볼륨을 설정한다. 현재 재생 중인 톤에도 적용되어야 하며(should), 재생 중 톤의 볼륨을 바꿀 수 없는 VT는 응답에 busy 비트를 세운다. 다른 Working Set의 볼륨 설정과 Alarm Mask 볼륨에는 영향을 주지 않는다. 기본 볼륨은 VT version 4 이하에서는 미정의, version 5 이상에서는 운전자가 설정한 최대 볼륨의 100 %다.

**command** (VT function = 164, 8바이트, Macro 허용): Byte 2 = 운전자 설정 최대 볼륨 대비 퍼센트(0~100 %). **response**: Byte 2 Error Codes: Bit 0 = Audio device busy(명령은 새 설정을 사용), Bit 1 = 명령 미지원(v5 이상에서 정의), Bit 4 = 기타 에러.

### F.14~F.15 Change Child Location (상대 이동)

오브젝트의 위치를 <strong>현재 위치 기준 상대값</strong>으로 옮긴다. 오브젝트가 여러 부모에 포함될 수 있으므로 Parent Object ID를 함께 지정한다. 한 부모가 같은 child를 여러 번 포함하면 모든 인스턴스가 이동한다. 이동 시 부모 오브젝트는 다시 그려져야 한다. 위치 값은 −127 오프셋 인코딩이다: 값 0 = −127픽셀 이동, 255 = +128픽셀 이동. 양수는 아래(Y)/오른쪽(X), 음수는 위(Y)/왼쪽(X)이다.

:::warning 메시지 유실과 누적 오차
상대 이동은 메시지가 유실되면 위치가 어긋난 채 남는다. 위치 보장이 필요하면 절대 좌표를 쓰는 Change Child Position 명령을 사용해야 한다.
:::

**command** (VT function = 165, 8바이트, Macro 허용): Byte 2,3 = Parent Object ID / Byte 4,5 = 이동할 Object ID / Byte 6 = X 상대 변화 / Byte 7 = Y 상대 변화 / Byte 8 = Reserved.

**response**: Byte 6 Error Codes: Bit 0 = 지정한 부모가 없거나 대상의 부모가 아님, Bit 1 = 대상이 없거나 이 명령을 적용할 수 없는 오브젝트, Bit 4 = 기타 에러.

### F.16~F.17 Change Child Position (절대 이동)

오브젝트 위치를 <strong>부모 오브젝트의 좌상단 기준 절대 좌표</strong>로 설정한다. 부모가 같은 child를 여러 번 포함하면 모든 인스턴스가 같은 위치로 이동한다(상대 운동으로 모두 옮기려면 Change Child Location을 쓰라고 안내). 좌표는 signed integer이며 양수는 부모 좌상단의 아래(Y)/오른쪽(X)이다.

**command** (VT function = 180, <strong>9바이트</strong>, Macro 허용): Byte 2,3 = Parent Object ID / Byte 4,5 = 이동할 Object ID / Byte 6,7 = 새 X / Byte 8,9 = 새 Y. **response**(8바이트)의 에러 코드 구성은 Change Child Location과 동일하다.

### F.18~F.19 Change Size

오브젝트의 크기를 변경한다. 폭 또는 높이가 0이면 크기 0으로 취급되어 그려지지 않는다. **command** (VT function = 166, 8바이트, Macro 허용): Byte 2,3 = Object ID / Byte 4,5 = 새 폭 / Byte 6,7 = 새 높이. **response**: Byte 4 Error Codes: Bit 0 = Invalid Object ID, Bit 4 = 기타 에러.

### F.20~F.21 Change Background Colour

오브젝트의 배경색을 변경한다. **command** (VT function = 167, 8바이트, Macro 허용): Byte 2,3 = Object ID / Byte 4 = 새 배경색(A.3 색상표). **response**: Byte 5 Error Codes: Bit 0 = Invalid Object ID, Bit 1 = Invalid colour code, Bit 4 = 기타 에러.

### F.22~F.23 Change Numeric Value

숫자 "value" 속성을 가진 오브젝트의 값을 변경한다. 오브젝트 크기는 바뀌지 않으며, 명령에 지정한 오브젝트만 변경된다 — 오브젝트가 참조하는 변수(Variable)는 바뀌지 않는다.

**command** (VT function = 168, 8바이트, Macro 허용): Byte 2,3 = Object ID / Byte 4 = Reserved(FF₁₆) / Byte 5~8 = 새 값. 값 크기는 오브젝트 타입에 따라 다르며, 1바이트 값은 Byte 5에, 2바이트 값은 Byte 5~6에 두고 리틀엔디언(LSB first)으로 전송, 미사용 바이트는 0으로 채운다.

| 오브젝트 타입 | 값 크기 |
|---|---|
| Input Boolean | 1바이트 (TRUE/FALSE) |
| Input Number / Output Number / Number Variable | 4바이트 정수 |
| Input List / Output List(v4+) | 1바이트 리스트 인덱스 |
| Output Meter / Output Linear Bar Graph / Output Arched Bar Graph | 2바이트 정수 |
| Object Pointer | 2바이트 Object ID |
| External Object Pointer(v5+) | Byte 5~6 = External Reference NAME Object ID, Byte 7~8 = 참조 대상 Object ID |
| Animation(v5+) | 2바이트 Object ID |
| Scaled Graphic(v6+) | 1바이트 리스트 인덱스 + 2바이트 Object ID |

업데이트 빈도는 Working Set 설계 재량이나, 대역폭 한계(4.6.10.1)를 고려해야 한다.

**response**: Byte 4 Error Codes: Bit 0 = Invalid Object ID, Bit 1 = Invalid value(포인터 값을 존재하지 않는 오브젝트로 바꾸려 할 때만 세움), Bit 2 = Reserved(v4·v5에서는 "값 사용 중(입력 열림)"을 의미했으나 v6부터 deprecated), Bit 4 = 기타 에러. Byte 5~8은 명령의 값을 그대로 반향.

### F.24~F.25 Change String Value

문자열 "value" 속성을 가진 오브젝트의 값을 변경한다. 규칙:

- 메시지가 단일 패킷에 들어가면 transport protocol을 쓰지 않는다. 전송 문자열이 3바이트 이하이면 단일 패킷의 남는 바이트는 FF₁₆로 채운다.
- 전송 문자열은 대상 오브젝트의 value 속성 길이보다 짧아도 되며, 이 경우 VT가 남는 부분을 space로 패딩한다. 전송 바이트 수는 대상 length 속성 이하여야 한다(문자열 길이 증가 불가).

**command** (VT function = 179, 가변 길이, Macro 허용): Byte 2,3 = Object ID / Byte 4,5 = 전송 문자열 바이트 수 / Byte 6~n = 새 문자열. **response**(8바이트): Byte 2,3 = Reserved(FF₁₆), Byte 4,5 = Object ID, Byte 6 Error Codes: Bit 1 = Invalid Object ID, Bit 2 = 문자열이 너무 김, Bit 3 = 기타 에러, Bit 4 = Reserved(v4·v5의 "값 사용 중" 표시는 v6부터 deprecated).

### F.26~F.27 Change End Point

Output Line 오브젝트의 끝점을 폭·높이·line direction 속성 변경으로 바꾼다. **command** (VT function = 169, 8바이트, Macro 허용): Byte 2,3 = Output Line Object ID / Byte 4,5 = 폭(픽셀) / Byte 6,7 = 높이(픽셀) / Byte 8 = Line Direction. **response**: Byte 4 Error Codes: Bit 0 = Invalid Object ID, Bit 1 = Invalid Line Direction, Bit 4 = 기타 에러.

### F.28~F.29 Change Font Attributes

Font Attributes 오브젝트의 속성 일괄 변경. **command** (VT function = 170, 8바이트, Macro 허용): Byte 2,3 = Object ID / Byte 4 = Font colour(A.3) / Byte 5 = Font size / Byte 6 = Font type / Byte 7 = Font style. **response**: Byte 4 Error Codes: Bit 0 = Invalid Object ID, Bit 1 = Invalid colour, Bit 2 = Invalid size, Bit 3 = Invalid type, Bit 4 = Invalid style, Bit 5 = 기타 에러.

### F.30~F.31 Change Line Attributes

Line Attributes 오브젝트의 속성 일괄 변경. **command** (VT function = 171, 8바이트, Macro 허용): Byte 2,3 = Object ID / Byte 4 = Line Colour(A.3) / Byte 5 = Line Width / Byte 6,7 = Line Art. **response**: Byte 4 Error Codes: Bit 0 = Invalid Object ID, Bit 1 = Invalid colour, Bit 2 = Invalid width, Bit 4 = 기타 에러.

### F.32~F.33 Change Fill Attributes

Fill Attributes 오브젝트의 속성 일괄 변경. **command** (VT function = 172, 8바이트, Macro 허용): Byte 2,3 = Object ID / Byte 4 = Fill Type / Byte 5 = Fill Colour(A.3) / Byte 6,7 = Fill Pattern Object ID. **response**: Byte 4 Error Codes: Bit 0 = Invalid Object ID, Bit 1 = Invalid type, Bit 2 = Invalid colour, Bit 3 = Invalid pattern Object ID, Bit 4 = 기타 에러.

### F.34~F.35 Change Active Mask

Working Set의 활성 마스크를 Data Mask 또는 Alarm Mask로 전환한다. **command** (VT function = 173, 8바이트, Macro 허용): Byte 2,3 = Working Set Object ID / Byte 4,5 = 새 Active Mask Object ID. **response**: Byte 2,3 = 새 Active Mask Object ID, Byte 4 Error Codes: Bit 0 = Invalid Working Set Object ID, Bit 1 = Invalid Mask Object ID, Bit 4 = 기타 에러. VT 주도의 마스크 변경 통지는 별도 메시지(H.14 VT Change Active Mask)로 이루어진다.

### F.36~F.37 Change Soft Key Mask

Data Mask 또는 Alarm Mask에 연결된 Soft Key Mask를 교체한다. **command** (VT function = 174, 8바이트, Macro 허용): Byte 2 = Mask Type(1 = Data, 2 = Alarm) / Byte 3,4 = Data 또는 Alarm Mask Object ID / Byte 5,6 = 새 Soft Key Mask Object ID. **response**: Byte 2,3 = Mask Object ID, Byte 4,5 = 새 Soft Key Mask Object ID, Byte 6 Error Codes: Bit 0 = Invalid Data/Alarm Mask Object ID, Bit 1 = Invalid Soft Key Mask Object ID, Bit 2 = Missing Objects, Bit 3 = 마스크 또는 child 오브젝트에 에러, Bit 4 = 기타 에러. VT 주도 변경은 H.16 참조.

### F.38~F.39 Change Attribute

AID(Attribute ID)가 부여된 <strong>모든 속성</strong>을 범용으로 변경하는 명령이다. 단 문자열 변경에는 사용할 수 없다(문자열은 Change String Value 사용).

**command** (VT function = 175, 8바이트, Macro 허용): Byte 2,3 = Object ID / Byte 4 = AID / Byte 5~8 = 새 값. 값 크기는 속성 데이터 타입에 따라 다르며 1바이트 초과 값은 리틀엔디언, 미사용 바이트는 0으로 채운다: Boolean 1바이트, Integer 1·2·4바이트(오브젝트 표 정의대로), Float 4바이트, Bitmask 1바이트.

**response**: Byte 5 Error Codes: Bit 0 = Invalid Object ID, Bit 1 = Invalid Attribute ID, Bit 2 = Invalid value, Bit 3 = Reserved(v4·v5의 "값 사용 중" 표시, v6부터 deprecated), Bit 4 = 기타 에러.

### F.40~F.41 Change Priority

Alarm Mask의 우선순위를 변경한다. 이 명령을 받으면 VT는 모든 활성 마스크의 우선순위를 재평가하며, 변경된 Alarm Mask가 활성 Working Set·마스크가 되어야 하거나 더 이상 활성이 아니어야 하는 경우 다른 마스크로의 전환이 일어날 수 있다.

**command** (VT function = 176, 8바이트, Macro 허용): Byte 2,3 = Alarm Mask Object ID / Byte 4 = 새 priority. **response**: Byte 5 Error Codes: Bit 0 = Invalid Object ID, Bit 1 = Invalid priority, Bit 4 = 기타 에러.

### F.42~F.43 Change List Item

Input List·Output List(v4+)·Animation(v5+)·External Object Definition(v5+) 오브젝트의 리스트 항목을 교체한다.

**command** (VT function = 177, 8바이트, Macro 허용): Byte 2,3 = 대상 Object ID / Byte 4 = List Index(0부터 시작) / Byte 5,6 = 새 Object ID 또는 FFFF₁₆(빈 항목으로 설정). **response**: Byte 7 Error Codes: Bit 0 = 대상 오브젝트 ID 무효, Bit 1 = Invalid List Index, Bit 2 = Invalid New List Item Object ID, Bit 3 = Reserved(v4·v5 "값 사용 중", v6부터 deprecated), Bit 4 = 기타 에러.

### F.44~F.45 Delete Object Pool

해당 Working Set의 오브젝트 풀 전체를 VT의 <strong>휘발성 저장소</strong>에서 삭제한다. 다른 VT로 풀을 옮기려 할 때, 셧다운 시, 또는 풀 개발 과정에서 사용한다. 비휘발성 저장소의 풀 삭제는 E.8(Delete Version)을 쓴다.

**command** (VT function = 178, 8바이트, Macro <strong>불가</strong>): Byte 2~8 Reserved. **response**: Byte 2 Error Codes(0 = 삭제 성공): Bit 0 = Deletion error, Bit 4 = 기타 에러.

### F.46~F.47 Lock/Unlock Mask

Working Set이 소유한 표시 중인 Data Mask 또는 User-Layout Data Mask의 <strong>화면 리프레시를 금지/허용</strong>한다. 여러 변경을 동기화해 시각적으로 원자적(atomic)으로 보이게 할 때(예: 애니메이션) 사용한다. v4 이상에서 사용 가능.

Lock의 의미: 그리기가 멈추는 것이 아니라, 표시 중인 마스크에 대한 변경이 운전자에게 <strong>보이지 않게</strong> 된다는 뜻이다. 다음 unlock 메커니즘 중 하나가 발생할 때까지 유지된다.

- Unlock 명령 수신 후 표시 마스크 리프레시 완료
- Lock 메시지의 timeout 속성에 따른 타임아웃
- Data Mask 위 입력 오브젝트·Button으로의 내비게이션 또는 활성화
- 마스크가 표시 상태에서 숨김 상태로 전환
- 풀 삭제
- VT 고유 사유(예: 입력 다이얼로그 닫힘)

잠금 중 동작 규칙:

- 잠긴 마스크의 화면 표시는 어떤 이유로도 갱신되지 않는다. 점멸(flashing) 오브젝트와 마스크 위 Animation 오브젝트도 포함된다. 타이머 기반 Animation은 백그라운드에서 타이머가 계속 돌고 비표시 사본에는 갱신이 반영되지만, 화면에는 unlock까지 반영되지 않는다.
- 잠금 중에도 CAN 메시지/명령, 키·버튼 누름, 이벤트, 매크로는 정상 처리된다.
- 잠금 상태는 Soft Key Mask와 Alarm Mask에는 적용되지 않는다 — 이들은 무조건 표시된다.
- Lock 명령 수신 시 어떤 Working Set이든 Alarm Mask가 같은 display area에 활성 상태면 Lock은 거부된다.
- VT는 Lock 명령에는 최대한 빨리 응답한다. Unlock 명령에 대한 응답은 상황에 따라 다르다: Data Mask/User-Layout Data Mask가 숨겨져 있으면(홈 페이지·설정 화면 표시 중 등) 즉시 응답하며 "명령 무시됨"을 표시한다. 마스크가 보이는 상태면 잠금 중의 모든 변경이 화면에 완전히 반영된 후에야 응답한다.
- 타임아웃이 발생하거나 마스크가 숨겨지는 변화가 생기면 VT는 <strong>unsolicited</strong>(요청 없는) Lock/Unlock Mask Response를 적절한 에러 코드와 함께 보낸다.

:::tip 권장 사용 패턴
Working Set은 마스크를 잠그고 → 필요한 변경 명령들을 보내고 → 잠금을 해제한 뒤 → Lock/Unlock Mask Response를 기다린다. 운전자 인터페이스 지연·내비게이션 문제·점멸 타이밍 흔들림을 피하려면 잠금은 밀리초 단위의 아주 짧은 시간만 유지하는 것이 권장된다.
:::

**command** (VT function = 189, 8바이트, Macro 허용)

| 바이트 | 내용 |
|---|---|
| 2 | 0 = Unlock, 1 = Lock |
| 3, 4 | 잠글/해제할 Data Mask 또는 User-Layout Data Mask Object ID. 표시 중인 마스크와 다르면 실패 |
| 5, 6 | Lock timeout(ms), 0 = 무제한. 만료 시 Working Set이 해제하지 않았어도 VT가 자동 해제. Unlock 명령에는 미적용 |

**response**: Byte 2 = Command 반향, Byte 3 Error Codes: Bit 0 = 명령 무시(표시 중 마스크 없음 또는 Object ID 불일치), Bit 1 = Lock 무시(이미 잠김), Bit 2 = Unlock 무시(잠기지 않음), Bit 3 = Lock 무시(Alarm Mask 활성), Bit 4 = Unsolicited unlock: 타임아웃, Bit 5 = Unsolicited unlock: 마스크 숨겨짐, Bit 6 = Unsolicited unlock: 운전자 유발 또는 기타 에러, Bit 7 = 기타 에러.

### F.48~F.49 Execute Macro

Macro 오브젝트를 실행한다(v4 이상). **command** (VT function = 190, 8바이트, Macro 허용): Byte 2 = Macro Object ID(1바이트임에 유의 — Macro ID는 255 이하). **response**: Byte 3 Error Codes: Bit 0 = Object ID 없음, Bit 1 = Macro 오브젝트가 아님, Bit 2 = 기타 에러.

### F.50~F.51 Change Object Label

오브젝트의 라벨(운전자용 표시 이름)을 변경한다(v4 이상, B.21 Object Label Reference List 참조).

**command** (VT function = 181, 8바이트, Macro 허용)

| 바이트 | 내용 |
|---|---|
| 2, 3 | 라벨을 연결할 대상 Object ID |
| 4, 5 | 라벨 문자열(최대 32문자)을 담은 String Variable Object ID, 텍스트 미제공 시 FFFF₁₆ |
| 6 | Font type(Annex K). String Variable 참조가 NULL이거나 문자열이 WideString이면 무시 |
| 7, 8 | 라벨의 그래픽 표현으로 쓸 Object ID, 미제공 시 FFFF₁₆. VT가 그릴 때 Soft Key designator 크기로 클리핑 |

**response**: Byte 2 Error Codes: Bit 0 = Invalid Object ID(Object Label Reference List에 없음), Bit 1 = Invalid String Variable Object ID, Bit 2 = Invalid font type, Bit 3 = 풀에 Object Label Reference List 오브젝트 없음, Bit 4 = designator가 무효 오브젝트 참조, Bit 5 = 기타 에러.

### F.52~F.53 Change Polygon Point

Output Polygon 오브젝트의 한 점을 수정한다(v4 이상). 여러 점을 바꿀 때 반복적인 다시 그리기를 피하려면 Lock/Unlock Mask 명령을 먼저 쓰는 것이 좋다.

**command** (VT function = 182, 8바이트, Macro 허용): Byte 2,3 = Output Polygon Object ID / Byte 4 = 교체할 점의 인덱스(첫 점이 0) / Byte 5,6 = 폴리곤 좌상단 기준 새 X / Byte 7,8 = 새 Y. **response**: Byte 4 Error Codes: Bit 0 = Invalid Object ID, Bit 1 = Invalid point index, Bit 2 = 기타 에러.

### F.54~F.55 Change Polygon Scale

Output Polygon 전체의 스케일을 변경한다(v4 이상). Change Size와 비슷하지만 폴리곤 점 좌표까지 재계산된다는 점이 다르다. VT는 폴리곤의 외곽 영역(width·height 속성)을 바꾸고 모든 점 위치를 다음 32비트 unsigned 정수 연산으로 조정해야 한다(구현 간 일관성 확보 목적).

```
new_x = [(old_x × new_width) + (old_width/2)] / old_width
new_y = [(old_y × new_height) + (old_height/2)] / old_height
```

**command** (VT function = 183, 8바이트, Macro 허용): Byte 2,3 = Output Polygon Object ID / Byte 4,5 = 새 width / Byte 6,7 = 새 height. **response**: Byte 8 Error Codes: Bit 0 = Invalid object id, Bit 4 = 기타 에러.

### F.56~F.57 Graphics Context command

Graphics Context 오브젝트를 조작하는 그리기 명령 집합이다(v4 이상 VT 전용). 8바이트 초과 메시지는 Transport Protocol을 쓰고, 8바이트 미만 명령은 FF₁₆로 8바이트까지 패딩한다. 그리기 규칙:

- 이 명령으로 그리는 그래픽은 캔버스 크기로 클리핑된다. 그리기 명령이 그래픽 커서를 오브젝트 정의 영역 밖으로 옮기면, 그림은 오브젝트 경계에서 클리핑하되 커서는 경계 밖 새 종점으로 이동시킨다.
- 그리기 규칙은 일반 VT 오브젝트의 그리기 규칙(B.10)과 동일하다(예: 항상 "square" 브러시).
- 전경색은 Options bit 1 상태에 따라 Graphics Context 오브젝트의 foreground colour 속성 또는 Line Attributes의 Line Colour 중 하나를 쓴다. 배경색도 같은 방식으로 background colour 속성 또는 Fill Attributes의 Fill Colour 중 선택된다. 텍스트 전경색은 foreground colour 속성 또는 Font Attributes의 Font colour 중 선택된다.
- 줌: zoom 값 1,0 = 배율 없음(뷰포트:캔버스 1:1), 2,0 = 2:1 확대, 3,0 = 3:1 확대. 0,5 = 1:2 축소, 0,25 = 1:4 축소. 확대 시 캔버스 1픽셀이 뷰포트에서 n×n 픽셀로 표시되고, 축소 시 n×n 픽셀 블록이 1픽셀로 합쳐진다. 정확한 줌 알고리즘은 VT 고유이며 픽셀 병합·확장 시 최근접 색상 매칭을 쓸 수 있다.
- 줌은 <strong>뷰포트에만</strong> 적용되고 캔버스에는 적용되지 않는다. Viewport X/Y 위치는 줌 안 된 캔버스 기준이다. 즉 줌 앵커는 뷰포트의 좌상단이며, 뷰포트 위치를 안 움직이고 줌만 하면 좌상단에서 우하단 방향으로 이미지가 늘어나는 것처럼 보인다.

**command** (VT function = 184, 가변 길이, Macro 허용): Byte 2,3 = Graphics Context Object ID / Byte 4 = Sub-Command ID / Byte 5~n = 서브커맨드별 파라미터.

**Table F.1 — 그래픽 서브커맨드 요약**

| ID | 이름 | 동작·파라미터 |
|---|---|---|
| 0 | Set Graphics Cursor | 커서 X/Y 절대 설정. Byte 5~6 = X, 7~8 = Y (−32768~+32767) |
| 1 | Move Graphics Cursor | 커서를 현재 위치 기준 상대 이동. Byte 5~6 = X offset, 7~8 = Y offset |
| 2 | Set Foreground Colour | 전경색 속성 변경(Byte 5). 커서 이동 없음 |
| 3 | Set Background Colour | 배경색 속성 변경(Byte 5). 커서 이동 없음 |
| 4 | Set Line Attributes Object ID | 이후 그리기에 쓸 Line Attributes 지정(Byte 5~6). NULL = 선 그리기 억제 |
| 5 | Set Fill Attributes Object ID | 이후 그리기에 쓸 Fill Attributes 지정. NULL = 채우기 없음 |
| 6 | Set Font Attributes Object ID | 이후 텍스트에 쓸 Font Attributes 지정. NULL = 텍스트 미사용 |
| 7 | Erase Rectangle | 커서 위치에 현재 배경색으로 사각형 채움(Byte 5~6 = 폭, 7~8 = 높이). Options bit 1과 무관하게 Fill Attributes를 쓰지 않음. 커서는 사각형 내부 우하단 픽셀로 이동 |
| 8 | Draw Point | 커서 기준 오프셋 위치 픽셀을 전경색으로 설정. 커서는 해당 점으로 이동 |
| 9 | Draw Line | 커서에서 지정 끝 픽셀(커서 기준 오프셋)까지 전경색 선. Output Line 규칙·Line Attributes 적용. 커서는 끝 픽셀로 이동 |
| 10 | Draw Rectangle | 커서 위치에 사각형(폭·높이 지정). Rectangle 규칙 적용 — Line Attributes 정의 시 테두리, Fill Attributes 정의 시 채움. 커서는 내부 우하단으로 이동 |
| 11 | Draw Closed Ellipse | 커서 위치와 폭·높이가 정의하는 사각형에 내접하는 닫힌 타원. Output Ellipse 규칙 적용. 커서는 경계 사각형 내부 우하단으로 이동 |
| 12 | Draw Polygon | Byte 5 = 점 개수(0~255), 이후 점마다 4바이트(커서 기준 X·Y 오프셋, 첫 점부터 순차 연결). 마지막 점 오프셋이 0,0이면 닫힘(0,0은 시작 커서 좌표이므로). 닫히지 않으면 자동 닫기 없이 채우기 무시. Output Polygon 규칙 적용. 커서는 리스트 마지막 점으로 이동 |
| 13 | Draw Text | Byte 5 = 0 Opaque/1 Transparent, Byte 6 = 바이트 수, Byte 7~n = 텍스트(8-bit 또는 WideString). Font Attributes의 flashing 비트는 무시. Opaque면 배경색 속성 사용. 커서는 텍스트 범위 우하단으로 이동 |
| 14 | Pan Viewport | Viewport X/Y 속성 변경 후 강제 리드로 — 하부 콘텐츠 "패닝". 커서 이동 없음 |
| 15 | Zoom Viewport | Byte 5~8 = zoom 값(Float, −32,0~+32,0). 커서 이동 없음 |
| 16 | Pan and Zoom Viewport | 14+15 결합: Byte 5~6 = Viewport X, 7~8 = Y, 9~12 = zoom(Float) |
| 17 | Change Viewport Size | 뷰포트 크기 변경(Byte 5~6 = 새 폭, 7~8 = 새 높이, 0~32767). 오브젝트 자체 크기(메모리)는 불변. 커서 이동 없음 |
| 18 | Draw VT Object | Byte 5~6 = 그릴 Object ID. 지정 오브젝트를 현재 커서 위치(좌상단 기준)에 그림. Graphics Context 자신 또는 자신을 포함한 오브젝트는 불가(순환 참조 금지). 명령 시점의 현재 값·상태(enable/disable 포함)로 그리되, 점멸 비트맵은 점멸 상태와 무관하게 그림. 포커스 표시는 그리지 않으며, 운전자가 편집 중인 오브젝트는 마지막 확정 값으로 그림. 커서는 그린 오브젝트의 우하단으로 이동. 일반 VT 오브젝트 투명도 규칙 적용. 이 Graphics Context가 허용하지 않는 색은 투명 처리 |
| 19 | Copy Canvas to Picture Graphic | Byte 5~6 = 대상 Picture Graphic Object ID. 현재 캔버스를 Picture Graphic으로 복사. 대상이 작으면 클리핑, 크면 초과 픽셀 불변. 캔버스의 투명색 픽셀은 복사되지 않고 대상 픽셀 유지. Picture Graphic은 Graphics Context 이상의 색 수를 가져야 함. 허용 범위 밖 색은 투명 처리 |
| 20 | Copy Viewport to Picture Graphic | 19와 같지만 캔버스 대신 <strong>현재 뷰포트</strong>(줌·팬 적용 상태)를 복사 |

**response** (F.57, 8바이트): Byte 2,3 = Graphics Context Object ID, Byte 4 = Sub-command ID, Byte 5 Error codes: Bit 0 = Invalid Object ID 또는 Graphics Context 오브젝트 아님, Bit 1 = Invalid sub-command id, Bit 2 = Invalid parameter, Bit 3 = 서브커맨드가 무효한 결과를 만들게 됨, Bit 4 = 기타 에러.

### F.58~F.59 Get Attribute Value

Working Set이 VT 내부 오브젝트의 현재 상태(속성값)를 조회한다(v4 이상, Macro 불가).

**command** (VT function = 185, 8바이트): Byte 2,3 = Object ID / Byte 4 = AID. **response**: Byte 2,3 = Object ID(에러 응답이면 FFFF₁₆), Byte 4 = AID. 에러가 없으면 Byte 5~8 = 속성 현재 값(데이터 타입별 크기, 리틀엔디언: Boolean 1바이트, Integer 1·2·4바이트, Float 4바이트, Bitmask 1바이트). 에러 응답이면 Byte 5,6 = Object ID, Byte 7 = Error Codes(Bit 0 = Invalid Object ID, Bit 1 = Invalid Attribute ID, Bit 4 = 기타 에러).

### F.60~F.61 Select Colour Map or Palette

표시 색상을 변경한다(v4 이상). 발행 Working Set의 <strong>모든 표시</strong>에 적용되며, 다른 Working Set 화면에 표시될 수 있는 오브젝트(예: Auxiliary Control Designator Type 2 Object Pointer로 다른 Working Set 마스크·VT 고유 화면에 표시되는 Auxiliary Control 오브젝트)에도 적용된다.

- v4 이상: 참조 Object ID는 Colour Map 오브젝트일 수 있다.
- v6 이상: Colour Palette 오브젝트도 가능하며, v6 호환 VT가 이 명령을 처리하면 Working Set Special Controls 오브젝트(B.29)를 참조 오브젝트에 맞게 갱신해야 한다.
- 이 명령은 실행에 오래 걸릴 수 있다.

**command** (VT function = 186, 8바이트, Macro 허용): Byte 2,3 = Colour Map 또는 Colour Palette Object ID, FFFF₁₆ = 기본 색상 매핑(A.3) 복원. **response**: Byte 4 Error Codes: Bit 0 = Invalid object id, Bit 1 = Invalid Colour Map or Palette, Bit 2 = 기타 에러.

### F.62~F.63 Execute Extended Macro

Macro를 실행한다(v5 이상). F.48과 달리 Macro Object ID를 <strong>2바이트</strong>로 지정하므로 255를 넘는 ID의 Macro도 실행할 수 있다. **command** (VT function = 188, 8바이트, Macro 허용): Byte 2,3 = Macro Object ID. **response**: Byte 4 Error Codes: Bit 0 = Object ID 없음, Bit 1 = Macro 오브젝트 아님, Bit 2 = 기타 에러.

### F.64~F.65 Select Active Working Set

<strong>현재 활성 Working Set</strong>이 VT에게 다른 Working Set을 활성으로 선택하라고 요청한다(v6 이상). 규칙:

- 활성이 아닌 Working Set이 보내면 VT는 요청을 무시하고 응답에 에러 코드를 세운다.
- 대상 Working Set 오브젝트의 Selectable 속성이 0이어도, Active mask 속성이 Data Mask를 가리키고 있으면 이 메시지로 활성화할 수 있다.
- 메시지가 전송 중인 사이에 활성 Working Set이 바뀔 수 있으므로, 이 메시지를 쓰는 Working Set은 응답을 확인해 성공 여부를 알아야 한다.

**command** (VT function = 144, <strong>9바이트</strong>, Macro 허용): Byte 2~9 = 활성화할 Working Set Master의 NAME(8바이트). **response**(8바이트): Byte 2 Error Codes(0 = 에러 없음, 해당 WS가 활성화됨): Bit 0 = 활성 WS가 보낸 명령이 아님, Bit 1 = 현재 활성 마스크가 Alarm Mask, Bit 2 = NAME이 WSM을 식별하지 못함, Bit 3 = NAME의 WSM이 이 VT에 오브젝트 풀이 없음, Bit 4 = NAME의 WSM에 활성 data mask가 없음, Bit 7 = 기타 에러. 에러 비트가 하나라도 세워지면 VT는 새 활성 Working Set을 선택하지 않는다.

## Annex G (normative) — Status 메시지

### G.1 일반

Status 메시지는 Working Set이 VT의 상태(health)와 작업 진행을 감시하고, 반대로 VT가 Working Set의 상태를 감시하게 해 준다. 오브젝트 풀의 일부가 아니며 Macro에서 사용할 수 없다.

### G.2 VT Status message

VT가 <strong>Global Address로</strong> 송신하여, 현재 표시 중이면서 입력 포커스를 가진(즉 VT를 "소유한") 활성 Working Set Master를 선언한다.

- 송신 조건: Byte 2~6 또는 Byte 7 bit 6 변경 시, 그리고 초당 1회. 최대 초당 5회.
- 초기화 후 VT가 VT Status message를 보내기 전까지 VT와의 데이터 통신을 시작해서는 안 된다(4.6.9).
- v4 이상의 Working Set Master는 이 메시지를 VT On User-Layout Hide/Show message(H.20)와 함께 청취하여 자신이 표시 중인지 판단해야 한다.

<strong>v6 이상 VT의 Byte 2 규칙</strong> (Data Mask 가림 상황 처리):

- Data Mask가 완전히 가려졌거나 전혀 보이지 않고(예: VT 고유 화면 표시 중), 가린 것이 해당 마스크의 입력 수단(팝업 에디터·키보드 등)이 아닌 경우: Byte 2를 FF₁₆, FE₁₆ 또는 VT 자신의 source address로 설정한다.
- Data Mask가 입력 수단이 아닌 다른 것으로 <strong>부분적으로</strong> 가려진 경우: Working Set이 v3 이하면 Byte 2에 활성 WS의 source address를 유지해 마스크가 계속 갱신되게 한다. Working Set이 v4 이상이면 VT는 둘 중 하나를 택한다 — (1) Byte 2로 "소유자 없음"을 표시하되 VT On User-Layout Hide/Show를 "Show"로 보내 WS가 활성 마스크를 계속 갱신하게 하거나, (2) Byte 2에 활성 WS 주소를 유지한다.
- Alarm Mask가 보이는 경우: Byte 2 = 보이는 Alarm Mask를 소유한 Working Set의 source address.
- 활성 WS의 마스크를 가리는 것이 활성 WS의 문맥 안에서 일어난 일이면(예: Input String 입력 다이얼로그) VT Status는 계속 그 WS를 소유자로 반영한다. 활성 WS 문맥 밖이면(예: 장시간 화면 대부분을 덮는 비디오 앱) VT 자신 주소·FE₁₆·FF₁₆로 소유자 변경을 반영해야 한다. 잠깐 나타나는 연결 안내 화면처럼 마스크를 완전히 덮지 않는 짧은 표시는 VT Status를 바꾸지 않는다.

**메시지 구조** (VT function = 254, 8바이트, VT to ECU)

| 바이트 | 내용 |
|---|---|
| 2 | 활성(=VT 소유) Working Set Master의 Source Address. 소유자 없으면 FF₁₆/FE₁₆/VT 자신 주소 중 하나(v6에서 명문화, 이전 버전에서도 사용 허용) |
| 3, 4 | 활성 WS의 표시 중 Data/Alarm Mask Object ID, 소유자 없으면 FFFF₁₆ |
| 5, 6 | 활성 WS의 표시 중 Soft Key Mask Object ID, 소유자 없거나 Soft Key Mask 미정의면 FFFF₁₆ |
| 7 | VT busy codes: Bit 0 = 표시 마스크 갱신 중, Bit 1 = 비휘발성 메모리 저장 중, Bit 2 = 명령 실행 중, Bit 3 = Macro 실행 중, Bit 4 = 오브젝트 풀 파싱 중(v3+), Bit 5 = Reserved, Bit 6 = Auxiliary controls learn mode 활성(v3+), Bit 7 = 메모리 부족 |
| 8 | 현재 실행 중인 명령의 VT function code(command/Macro busy 비트가 세워졌을 때만 유효), 실행 중인 것이 없으면 FF₁₆ |

### G.3 Working Set Maintenance message

각 Working Set Master가 VT로 <strong>초당 1회</strong> 주기 송신한다(4.6.9). Working Set 멤버는 자신의 버전을 따로 보고할 수단이 없으므로 모든 멤버는 Master가 보고한 버전을 준수해야 한다 — 예컨대 Master는 Working Set 안에서 가장 낮은 호환 버전을 보고할 수 있고, Master·멤버 간 호환성 판단은 고유(proprietary) 메시지로 할 수 있다.

**메시지 구조** (VT function = 255, 8바이트, ECU to VT, 초당 1회)

| 바이트 | 내용 |
|---|---|
| 2 | BitMask (v3 이상): Bit 0 = Initiating — 초기화 중 한 번만 세움. v2 이하: FF₁₆ |
| 3 | Version Number — 이 Working Set이 준수하는 ISO 11783-6 버전: 3/4/5/6 = 해당 VT Version 준수, FF₁₆ = v2 이하 준수, 나머지 Reserved |
| 4~8 | Reserved, FF₁₆ |

- Initiating 비트가 두 개 이상의 메시지에서 세워져 있으면 Working Set이 (정상 셧다운 없이) 초기화를 재시작했다는 뜻이며 unexpected shutdown으로 취급한다(4.6.9).
- 보고된 Version Number는 VT가 명령·메시지에 어떻게 응답할지를 결정한다(4.6.2).
- Version Number는 Working Set(Master와 멤버)이 <strong>설계된</strong> 표준 버전을 반영해야 하며, VT에 맞춘 런타임 적응 때문에 바뀌어서는 안 된다. 예: v4 Working Set이 v3 VT에 풀을 올리려 v3 동작으로 폴백해도 이 파라미터는 여전히 4를 보고한다. VT는 이를 진단용으로 쓸 수 있지만, 보고된 버전을 이유로 통신이나 풀을 거부해서는 안 된다.

### G.4 Unsupported VT Function message (WS→VT)

Working Set이 자신이 지원하지 않는 VT function을 담은 Destination-Specific VT→ECU 메시지를 받았음을 VT에 알린다. Global Address로 온 미지원 메시지에는 보내지 않고 그냥 무시한다. Byte 2의 미지원 VT function 값은 수신한 메시지의 Byte 1 값이다. 이 메시지에 대한 응답은 없다(VT Unsupported VT Function message에 대한 응답도 아니다). v5 이상을 지원하도록 설계된 Working Set에서 사용 가능.

구조 (VT function = 253, 8바이트, ECU to VT): Byte 2 = 미지원 VT function(Bits 7~4 Command, 3~0 Parameter), Byte 3~8 Reserved.

### G.5 VT Unsupported VT Function message (VT→WS)

대칭 메시지: VT가 지원하지 않는 VT function을 담은 Destination-Specific ECU→VT 메시지를 받았을 때 Working Set에 알린다. 역시 Global Address 수신분에는 보내지 않고 무시하며, 응답 없음, v5 이상. 구조는 G.4와 동일(VT function = 253, VT to ECU).

## Annex H (normative) — Activation 메시지

### H.1 일반 원칙과 TAN

VT가 Working Set Master에게 보내는 unsolicited 메시지들이다(PGN은 Annex C).

- v5 이하 호환 조합에서는 이 Annex의 response 메시지가 별도 명시가 없는 한 <strong>선택</strong>이다.
- v6 이상 호환 조합에서는 response가 <strong>200 ms 이내 필수</strong>다. 단일 activation 메시지에 대한 응답이 300 ms 안에 오지 않으면 VT는 최대 3회 재시도해야 한다(should). 자동으로 다시 보내게 되는 메시지의 경우 이전 상태·값을 반복하지 말고 <strong>현재</strong> 상태·값을 전달한다.
- <strong>TAN(Transaction Number)</strong>: 응답 짝맞춤이 중요한(빠르게 연속 발생할 수 있는) activation 메시지에 추가된 4비트 번호다. VT가 각 activation 메시지마다 고유 TAN을 생성하며(예: 증가), 데이터가 동일한 이전 메시지의 재시도일 때는 TAN을 바꾸지 않는다(예: 다음 button-held는 새 TAN, button-release 재시도는 이전 TAN 유지). Working Set의 응답에는 activation 메시지의 TAN이 포함되고, VT는 이것으로 겹칠 수 있는 메시지-응답 쌍을 정렬한다.
- 필수 응답이 300 ms 내에 오지 않으면 VT는 해당 WS의 unexpected shutdown이 발생한 것처럼 동작하며(4.6.9), Working Set Maintenance message에 대해 Acknowledgement:NACK(ISO 11783-3)를 보낸다.
- 재시도는 Working Set이 운전자의 의도와 다른 순서로 activation 메시지를 보는 상황을 만들 수 있다. 예: 라이브 편집 중 값 27의 VT Change Numeric Value에 200 ms 내 응답이 없는 사이 운전자가 값을 32로 바꾸면, 27 재전송 대신 새 TAN으로 32를 보낸다. 반대로 버튼 홀드 중 릴리스 메시지에 응답이 없으면 릴리스 상태를 이전 TAN 그대로 재시도한다.

### H.2~H.3 Soft Key Activation

운전자의 Soft Key 또는 alarm ACK 수단 활성화를 VT가 전달한다. 키가 홀드 상태에서 메시지 간격이 300 ms를 넘으면 Working Set은 키가 릴리스된 것으로 처리해야 한다(4.6.18). VT에 키 누름 중단(abort) 수단이 있으면(예: 터치스크린에서 버튼을 누른 채 손가락을 옆으로 빼는 경우) released 대신 aborted 코드를 보낸다.

**message** (VT function = 0, 8바이트, VT to ECU, 누름/뗌 시 + 홀드 중 200 ms마다)

| 바이트 | 내용 |
|---|---|
| 2 | Key activation code: 0 = released(상태 변화), 1 = pressed(상태 변화), 2 = still held, 3 = aborted(v4+) |
| 3, 4 | Key 오브젝트의 Object ID |
| 5, 6 | Parent Object ID: 표시 중인 Data Mask/Alarm Mask, Soft Key가 표시 중인 Key Group 안에 있으면 Key Group Object ID |
| 7 | Soft key code: 0 = alarm ACK, 1~255 = WSM이 부여한 키 코드 |
| 8 | v5 이하: FF₁₆ / v6 이상: Bits 7~4 = TAN, 3~0 = F₁₆ |

**response** (ECU to VT): 동일 필드 반향(Byte 2 activation code, 3~4 Object ID, 5~6 Parent, 7 key code, 8 TAN).

### H.4~H.5 Button Activation

Button 오브젝트 활성화 전달. 규칙은 Soft Key와 유사: 비래치(non-latchable) 버튼 홀드 중 간격이 300 ms를 넘으면 released로 처리, abort 수단이 있으면 aborted 코드 전송. 래치 버튼은 반복 전송하지 않는다.

**message** (VT function = 1, 8바이트, 누름/뗌 시 + 홀드 중 200 ms마다)

| 바이트 | 내용 |
|---|---|
| 2 | 0 = unlatched/released(상태 변화), 1 = "pressed"/latched(상태 변화), 2 = still held(래치 버튼은 반복 없음), 3 = aborted(v4+) |
| 3, 4 | Button Object ID |
| 5, 6 | Parent Object ID: 부모 Data Mask, 또는 Button이 표시 중인 Window Mask 안에 있으면 Window Mask Object ID |
| 7 | Button key code |
| 8 | v5 이하: FF₁₆ / v6 이상: Bits 7~4 = TAN |

**response**: 동일 필드 반향.

### H.6~H.7 Pointing Event

터치스크린·포인팅 디바이스 지원 VT에서 터치/클릭/드래그를 알린다. Data Mask와 Free Form Window Mask(type 0, v6+)에 대해서만 보고된다. 버튼이나 입력 오브젝트가 터치/클릭된 경우에는 쓰지 않는다 — 그때는 Button Activation 또는 VT Select Input Object message가 나간다.

v4 이상 추가 요구사항:

- 홀드 중 메시지 간격이 300 ms를 넘으면 released로 처리해야 한다.
- 드래그 지원 VT에서, 첫 누름이 버튼/입력 필드 위가 아니었다면 드래그가 버튼/입력 필드를 지나가도 이 메시지를 계속 보내되 그 버튼/입력 필드를 활성화하지 않는다.
- 드래그 지원 VT는 X, Y를 현재 좌표로 갱신한다(D.9). 감지 좌표가 Data Mask 범위를 벗어나면 마지막 유효 좌표 또는 범위로 제한한 좌표에서 release 이벤트를 보고한다.
- 드래그 중간 좌표를 지원하지 않는 VT는 홀드 중 좌표로 누름 위치를 반복한다. 누름 좌표만 감지 가능한 VT는 모든 상태에서 누름 좌표를 쓴다.

v6 이상 추가 요구사항: Data Mask의 유효 영역이 터치되고 Change Mask 명령으로 현재 Data Mask가 <strong>다른</strong> 마스크로 바뀌면 상태 "Released"의 Pointing Event를 보낸다. <strong>같은</strong> Data Mask로 바뀌면 상태 "Held"로 계속 보낸다.

**message** (VT function = 2, 8바이트, 누름/뗌 시 + 홀드 중 200 ms마다)

| 바이트 | 내용 |
|---|---|
| 2, 3 | X 위치(픽셀, Data Mask 영역 좌상단 기준, 0 ~ 폭−1) |
| 4, 5 | Y 위치(0 ~ 높이−1) |
| 6 | Signal — VT 버전에 따라 정의가 다름(아래 표) |
| 7, 8 | v5 이하: Reserved FF₁₆ / v6 이상: Parent Mask Object ID |

Signal 바이트 정의(VT 버전과 WS Version Number 기준):

| VT 버전 | 비트 | 의미 |
|---|---|---|
| v3 이하 | 7~0 | Reserved FF₁₆ (Pressed 이벤트로 간주) |
| v4~v5 | 7~0 | Touch State: 0 = Released, 1 = Pressed, 2 = Held |
| v6 이상 | 7~4 / 3~0 | TAN / Touch State(0 = Released, 1 = Pressed, 2 = Held) |

**response**: X·Y·Signal·Parent Mask Object ID 반향.

### H.8~H.9 VT Select Input Object message

운전자 조작 또는 ESC 명령의 결과로 입력 필드·Button·Key 오브젝트가 선택(포커스 획득)·선택 해제(포커스 상실)·편집 열림·편집 닫힘될 때마다 VT가 보낸다.

- 활성화가 원자적 트랜잭션으로 완결되는 입력 오브젝트(예: 활성화가 값을 바로 토글하는 Input Boolean, VT가 전용 +1/−1 증감 수단을 갖는 Input Number)에는 보내지 않을 수 있다.
- Working Set이 Select Input Object command(F.6)로 요청한 포커스 변경에는 보내지 않는다 — 운전자 상호작용의 결과일 때만 보낸다.
- v3 이하는 Button/Key 선택 보고를 지원하지 않는다. Button/Key가 선택 대상일 때 "편집 열림"으로는 보고되지 않는다.
- On Input Field Selection/Deselection 이벤트는 Byte 4가 바뀔 때만 트리거된다. 오브젝트가 반복적으로 편집 열림/닫힘되는 것(Byte 5 변화)으로는 트리거되지 않는다.

**message** (VT function = 3, 8바이트, 입력 오브젝트 선택 시)

| 바이트 | 내용 |
|---|---|
| 2, 3 | Object ID |
| 4 | Selection: 0 = 선택 해제, 1 = 선택(포커스) |
| 5 | v3 이하: FF₁₆ / v4 이상: Bitmask — Bit 0 = 데이터 입력용으로 열림(이때 Byte 4는 1이어야 함) |
| 6, 7 | Reserved, FF₁₆ |
| 8 | v5 이하: FF₁₆ / v6 이상: Bits 7~4 = TAN |

**response**: Object ID·Selection 반향, Byte 5는 v5 이상에서 open-for-input 비트마스크, Byte 8 TAN(v6+).

### H.10~H.11 VT ESC message

운전자가 ESC 수단을 누를 때마다, 그리고 VT가 비운전자 요인으로 열린 입력 오브젝트를 닫을 때(Table 5) VT가 보낸다.

**message** (VT function = 4, 8바이트): Byte 2,3 = 에러 없을 때 입력이 중단된 Object ID / Byte 4 Error Codes: Bit 0 = 열린 입력 필드 없음(VT에 상시(permanent) ESC 수단이 있을 때만 사용), Bit 4 = 기타 에러 / Byte 8 = TAN(v6+). **response**: Object ID 반향 + TAN.

### H.12~H.13 VT Change Numeric Value message

운전자가 입력 오브젝트·변수에 숫자 값을 입력할 때마다 — <strong>값이 실제로 바뀌었는지와 무관하게</strong> — VT가 보낸다. 입력이 중단된 경우에는 보내지 않는다(그때는 VT ESC message). 숫자 변수 참조를 가진 입력 오브젝트는 이 메시지에 <strong>변수 오브젝트의 Object ID</strong>를 쓴다. v4 이하에서 Byte 4는 정의되지 않았다.

**message** (VT function = 5, 8바이트, 숫자 오브젝트 값 변경 시)

| 바이트 | 내용 |
|---|---|
| 2, 3 | Object ID |
| 4 | v5 이하: FF₁₆ / v6 이상: Bits 7~4 = TAN |
| 5~8 | 값(타입별 크기, 리틀엔디언, 미사용 바이트 0): Input Boolean 1바이트, Input Number 4바이트, Input List 인덱스 1바이트, Number variable 4바이트 |

**response**: Object ID, TAN, 그리고 message의 값을 복사해 반향.

### H.14~H.15 VT Change Active Mask message

Data Mask·Alarm Mask·Window Mask·Key Group에서 누락된 오브젝트 참조나 에러가 감지되었을 때 VT가 보낸다.

- 에러 감지는 언제든 일어날 수 있으며, 최소한 오브젝트를 그리기 전에는 이루어진다. 부분적으로만 그려지는 화면을 만들 누락 참조·에러가 감지되면 VT는 <strong>풀 삭제</strong>를 알리는 이 메시지를 보내야 한다.
- 비치명적 그리기 에러(예: 미정의 option 비트가 세워짐)는 풀 삭제로 이어지지 않게 VT 설계자가 선택할 수 있다.
- 에러가 풀 삭제로 이어지면 VT는 해당 Working Set을 unexpected shutdown이 감지된 것처럼 취급한다(4.6.9).
- 이름이 비슷한 Change Active Mask response(F.35)는 명령 수신·처리 확인용일 뿐 용도가 다르다.

**message** (VT function = 6, 8바이트, On error)

| 바이트 | 내용 |
|---|---|
| 2, 3 | Active mask / Window Mask / Key Group Object ID |
| 4 | Error codes: Bit 2 = Missing objects, Bit 3 = 마스크 또는 child 오브젝트에 에러, Bit 4 = 기타 에러, Bit 5 = 풀 삭제 진행 중 |
| 5, 6 | 에러를 포함한 Object ID |
| 7, 8 | 에러 Object ID의 Parent Object ID |

**response** (H.15, ECU to VT): Byte 2,3 = Active mask Object ID, 나머지 Reserved.

### H.16~H.17 VT Change Soft Key Mask message

Soft Key Mask에서 누락 참조·에러가 감지되었을 때 VT가 보낸다. 풀 삭제 규칙은 H.14와 동일하다(부분 그리기를 유발하는 에러 → 풀 삭제 통지, 비치명적 에러는 VT 재량).

**message** (VT function = 7, 8바이트, On error): Byte 2,3 = Data/Alarm Mask Object ID / Byte 4,5 = Soft Key Mask Object ID / Byte 6 Error Codes: Bit 2 = Missing objects, Bit 3 = 마스크·child 오브젝트 에러, Bit 4 = 기타 에러, Bit 5 = 풀 삭제 중. **response**: Byte 2,3 = Data/Alarm Mask Object ID, Byte 4,5 = Soft Key Mask Object ID 반향.

### H.18~H.19 VT Change String Value message

Input String 오브젝트(또는 참조된 String Variable)에 입력된 문자열을 VT가 전달한다.

- VT는 선행 space를 제거해서는 안 되며, 풀에 정의된 크기까지 space 패딩은 할 수 있다.
- Input String이 String Variable을 참조하면 이 메시지에는 Input String이 아니라 <strong>String Variable의 Object ID</strong>가 쓰인다.
- 단일 패킷에 들어가면 transport protocol을 쓰지 않는다. 전송 문자열이 3바이트 이하면 남는 바이트는 FF₁₆.
- transport protocol로 새 값이 전달되는 동안 Working Set은 다른 메시지(입력 종료를 알리는 VT Select Input Object, Soft Key Activation 등)를 트랜잭션 완료 전에 받을 수 있다.

**message** (VT function = 8, 가변, Input String 값 변경 시): Byte 2,3 = Input String 또는 String Variable Object ID / Byte 4 = 전송 문자열 바이트 수 / Byte 5~n = 입력된 문자열. **response**: Byte 2,3 = Reserved(FF₁₆), Byte 4,5 = Object ID, 나머지 Reserved.

### H.20~H.21 VT On User-Layout Hide/Show message

v4 이상 VT가 Window Mask·Key Group 오브젝트의 표시/제거를 Working Set들에 통지한다. 방금 비활성화된 Working Set에게 "활성 Data Mask·Soft Key Mask가 여전히 보이는 상태"임을 알리는 데에도 쓴다.

- 한 메시지로 최대 두 개의 오브젝트 상태(Window Mask/Key Group 2개, 또는 Data Mask+Soft Key Mask)를 전달할 수 있다. 영향받는 오브젝트가 많으면 여러 패킷이 필요할 수 있다.
- 이 메시지에서 언급되지 않은 Window Mask·Key Group·Data Mask·Soft Key Mask는 마지막으로 알려진 가시성 상태를 유지하는 것으로 간주한다.
- 비활성이면서 보이는 Working Set을 활성으로 만들 준비가 되면, VT는 먼저 이 메시지로 그 WS의 보이는 Data/Soft Key Mask를 "hide"로 알린 뒤 VT Status message로 활성화를 표시해야 한다. 이렇게 하면 "마스크가 보이는 이유"가 비활성+가시(Hide/Show 메시지 기준)가 아니라 활성(VT Status 기준)임이 WS에 정확히 전달된다.

**message** (VT function = 9, 8바이트, Byte 2~7 변경 시, 마스크당 초당 최대 5회)

| 바이트 | 내용 |
|---|---|
| 2, 3 | Window Mask/Key Group/Data Mask/Soft Key Mask Object ID |
| 4 | Status: Bit 0 = State(0 = hidden, 1 = shown) |
| 5, 6 | 두 번째 오브젝트의 Object ID 또는 NULL Object ID |
| 7 | 두 번째 오브젝트의 Status(앞 필드가 NULL이면 0으로 설정) |
| 8 | v5 이하: FF₁₆ / v6 이상: Bits 7~4 = TAN |

**response**: 동일 필드 반향.

### H.22~H.23 VT Control Audio Signal Termination message

v4 이상 VT가 Control Audio Signal 명령을 완료 전에 종료시켰을 때 보낸다. 더 낮은 우선순위 Alarm Mask의 음향 신호를 종료할 때는 보내지 않는다.

**message** (VT function = 10, 8바이트, On event): Byte 2 = Termination Cause(Bit 0 = Audio was terminated — 항상 세움) / Byte 3 = v5 이하 FF₁₆, v6 이상 Bits 7~4 TAN. **response**(v6에서 신설, v5 이하에는 response 미정의): Termination Cause와 TAN 반향.

## Annex I (normative) — 기타 메시지

VT는 ISO 11783-7에 정의된 관련 메시지들도 지원·생성해야 한다. 대표적으로 <strong>Language command(PGN 65039)</strong> — 단위계(Units of Operation)와 날짜·시간 형식 파라미터를 담는다. 또한 VT와 Working Set은 Key switch 상태·트랙터 전원 유지 최대 시간 감시와 셧다운 관리를 위해 <strong>Wheel-based speed and distance(PGN 65096)</strong>와 <strong>Maintain power(PGN 65095)</strong>를 쓸 수 있다(4.6.7).

## Annex J (normative) — Auxiliary control

### J.1 개요

Auxiliary control은 운전자가 VT 화면(활성 마스크)과 무관하게 특정 기능을 물리 입력장치로 제어할 수 있게 하는 메커니즘이다. 구조:

- <strong>Auxiliary Input</strong>(키·스위치·다이얼·노브·슬라이더)은 하나 이상의 Working Set(또는 VT)이 제공하며, 일단 Auxiliary Function에 할당되면 활성 Data Mask·Soft Key Mask와 무관하게 항상 동작한다.
- <strong>Auxiliary Function</strong>(예: 올리기/내리기, 시작/정지, 위치 설정) 역시 하나 이상의 Working Set(또는 VT)이 제공한다.
- 운전자는 VT가 제공하는 고유(proprietary) 할당 화면에서 입력을 기능에 할당한다. 할당 후에는 활성 Working Set과 무관하게 해당 기능을 제어할 수 있다.

버전 이력: VT version 2의 Auxiliary Control 프로토콜은 이 Annex의 프로토콜로 대체되었다. v3 이상의 프로토콜·알고리즘은 v2 Working Set의 것과 <strong>호환되지 않는다</strong>. 호환성 유지를 위해 v2용과 v3용 오브젝트·메시지가 모두 정의되어 있으며, v2 전용 항목은 "Type 1", v3 이상 전용 항목은 "Type 2"로 지칭한다.

핵심 개념:

- <strong>Preferred assignment</strong>: 할당이 이루어지면 Type 2 Auxiliary Function을 제공하는 Working Set이 그 할당을 새로운 선호 할당으로 저장한다. 선호 할당은 기능을 제공하는 Working Set이 보관하므로, 공장 기본 할당으로 알려진 입력·기능 조합을 쉽게 통합할 수 있다. Working Set은 복수의 입력 장치 조합을 인식해 조합별 선호 할당 세트를 저장·제공하도록 설계할 수 있다. 이후 전원 사이클 등에서 선호 할당 세트가 VT로 전달되어 전체 시스템에 대해 검증된다.
- <strong>Assignment Restriction</strong>(과거 명칭 "Assignment Lock"): Type 2 Auxiliary Function의 옵션. 걸려 있으면 그 기능은 Preferred Assignment command에 지정된 대로만 할당될 수 있다. 이 제한이 있어도 운전자는 할당을 막거나 해제할 수는 있다.
- VT 할당 화면은 같은 Input Device에 할당되고 Assignment Restriction이 걸린 Auxiliary Function들을 그룹으로 다룰 수 있다(그룹 단위 전체 할당 또는 전체 미할당). 할당 화면은 할당 가능한 입력·기능만 보여주는 필터를 제공할 수 있다.
- <strong>입력 잠금(lock)</strong>: v6은 Auxiliary Input Type 2 Status message를 확장해 입력이 오조작 방지를 위해 "locked" 상태임을 표시할 수 있게 했다. 잠금 수단은 단일 신호용일 수도, 여러 신호를 동시에 잠글 수도 있다(예: 다기능 조이스틱의 모든 입력 신호를 잠그는 "lock" 스위치). 잠금 활성/해제 수단은 고유 설계이며, 현재 잠금 상태를 운전자가 볼 수 있게 표시할 것이 권장된다.

:::info 동작 예시
운전자가 VT의 표시 마스크와 무관하게 특정 작업기를 올리고 내리고 싶다. 작업기(Working Set)는 "raise/lower implement" Auxiliary Function을 제공하고, 트랙터 암레스트에는 이와 호환되는 2단 모멘터리 토글 스위치(Auxiliary Input)가 있다. 운전자가 VT 제공 화면에서 이 스위치를 그 기능에 할당하면, 이후 전원이 꺼질 때까지(또는 운전자가 바꿀 때까지) 그 스위치로 작업기를 올리고 내릴 수 있다.
:::

### J.2 Auxiliary Inputs

Auxiliary Input은 외부 유닛에 있을 수도, VT 자체에 있을 수도 있다. 물리적일 필요는 없지만 항상 운전자가 쓸 수 있어야 한다. 타입: Boolean(버튼·스위치), analogue(조이스틱·다이얼·노브), encoder, combinatorial(Table J.5).

- <strong>Boolean 입력</strong>: enabled/disabled 두 상태. latched와 non-latched 두 종류가 있고, non-latched(momentary)는 운전자가 누르고 있는 동안만 on/TRUE다.
- <strong>Analogue 입력</strong>: 항상 최대값 대비 퍼센트로 보고한다. output = (input − min) / (max − min) × 100.
- <strong>Encoder 입력</strong>: 항상 현재 인코더 카운트로 보고한다.

상태 보고 규칙: VT가 명시적으로 활성화하면 Auxiliary Input 유닛은 입력별로 초당 1회 Auxiliary Input status message를 보낸다. 값이 바뀌면 즉시 status message를 보내되, 특정 입력에 대한 메시지 간 최소 50 ms 간격을 지켜야 한다(입력당 최대 20 Hz). non-latched Boolean 입력은 홀드 중 200 ms마다 상태를 보낸다. 메시지는 모든 Working Set에 브로드캐스트되며 확인응답이 없다. 값이 전송 능력보다 빨리 바뀌거나 메시지가 유실되어 전이(transition)가 전달되지 않을 수 있으므로, Auxiliary Function 쪽 Working Set은 일부 타입에 있는 Number of Transitions 파라미터로 누락 전이를 판별할 책임이 있다.

### J.3 다중 VT 환경의 Auxiliary control

일반 규칙(네트워크에 VT가 하나뿐이어도 VT 부팅 시간 문제를 피하려 적용):

- Auxiliary 할당과 검증은 <strong>VT function instance 0</strong>에서만 수행한다. 운전자가 instance 0이 아닌 VT에서 할당 화면에 접근하려 하면 그 VT는 할당이 허용되지 않음을 알려야 한다.
- Instance 0이 아닌 VT도 Auxiliary Input/Function 오브젝트가 포함된 풀을 받을 수 있다. 이 오브젝트들은 파싱은 하되 할당 생성·검증에는 쓰지 않는다. 따라서 풀을 둘로 나눠야 할 수 있다: 예를 들어 instance 1 VT에 표시·기능을 두려면 전체 풀(Auxiliary 오브젝트 포함)을 instance 1에 올리고, 할당 제어를 위해 Auxiliary Input·Function을 담은 풀을 instance 0에도 올린다. Instance 0이 아닌 VT에 게시된 Auxiliary Control Designator Type 2 Object Pointer는 가능한 범위에서 표시를 시도해야 한다(J.4.7).
- Working Set이 Type 2 오브젝트를 instance 0이 아닌 VT에 게시하는 경우에도 instance 0에 게시할 의무는 없다.
- 두 VT를 쓰는 Working Set은 Working Set Maintenance message를 <strong>두 VT 모두에게</strong> 정규 주기로 보내야 한다. 통상의 연결 관리 규칙이 적용된다.

이 규칙들은 네트워크에 항상 function instance 0 VT가 존재해야 함을 함의한다. Primary VT 설정과 instance 0 해석 방법은 4.6.25 VT Number에 정의되어 있다.

### J.4 Auxiliary Input·Function의 정의

Auxiliary Input은 Auxiliary Input 오브젝트로, Auxiliary Function은 Auxiliary Function 오브젝트로, 각각 이를 제공하는 Working Set의 오브젝트 풀에 정의된다. 입력·기능은 자신의 타입을 나타내는 designator(라벨)와 소속 Working Set의 designator 조합으로 운전자에게 고유 식별된다. 입력만 제공하는 유닛(예: 스위치 박스)은 Working Set 오브젝트 + Auxiliary Input 오브젝트들로 구성된 최소 풀이면 된다. 풀 전송에는 transport protocol을 쓴다.

- Auxiliary Function을 제공하는 Working Set은 제공 기능 수만큼의 Auxiliary Input Device를 지원할 수 있어야 하며(should), 12개 초과 기능을 제공하면 <strong>최소 12개의 Auxiliary Input Device</strong>를 지원해야 한다(shall).
- 오브젝트 타입 29·30(Type 1 계열)은 v3 이상에서 obsolete다. 하위 호환을 위해 v3 이상 VT는 이들을 파싱·검증은 하되 할당에는 쓰지 않으며, v3 이상 Working Set은 타입 29·30을 사용해서는 안 된다.

#### J.4.2 Auxiliary Function Type 1 object (type 29, v2 전용)

Auxiliary Function의 속성과 designator를 정의한다. VT는 이 속성으로 입력-기능 할당 규칙을 강제한다(예: Boolean 기능은 호환 Boolean 입력에만 할당). designator는 Soft Key designator 영역에 맞아야 하며 벗어나는 부분은 클리핑된다. 허용 명령: Get Attribute Value뿐. 이벤트 없음.

**Table J.1 — Auxiliary Function Type 1 레코드**

| 속성 | 크기 | 값 | 설명 |
|---|---|---|---|
| Object ID | 2 | 0~65534 | 풀 내 고유 |
| Type | 1 | =29 | |
| Background colour | 1 | 0~255 | |
| Function type | 1 | 0/1/2 | 0 = Latching Boolean, 1 = Analogue, 2 = Non-latching Boolean |
| Number of objects to follow | 1 | 1~255 | designator 구성 오브젝트 수 |
| 반복: {Object ID, X, Y} | 2+2+2 | | designator를 이루는 picture graphic·output shape·output field와 상대 위치 |

(v3 이상 VT는 파싱·검증만 하고 할당에 사용하지 않음)

#### J.4.3 Auxiliary Function Type 2 object (type 31)

허용 명령: Change Background Colour, Change Child Location, Change Child Position, Change Attribute, Get Attribute Value. 이벤트 없음.

**Table J.2 — Auxiliary Function Type 2 레코드**

| 속성 | AID | 크기 | 값 | 설명 |
|---|---|---|---|---|
| Object ID | | 2 | 0~65534 | |
| Type | [0] | 1 | =31 | |
| Background colour | 1 | 1 | 0~255 | |
| Function attributes | [2] | 1 | 0~255 | Bits 0~4 = Auxiliary function type(Table J.5)<br>Bit 5 = Critical Control: 0 = 아무 호환 입력이나 제어 가능, 1 = critical Auxiliary Input(ISO 15077)만 제어 가능<br>Bit 6 = Assignment Restriction: 0 = 비제한(운전자 또는 Preferred Assignment command로 할당 가능, 운전자 할당 우선), 1 = 제한(할당된다면 Preferred Assignment command 지정대로만; 이 경우에도 미할당 전환은 가능)<br>Bit 7 = Single-assignment: 0 = 같은 입력에 다른 기능과 공동 할당 가능, 1 = 같은 입력에 다른 기능과 공동 할당 불가 |
| Number of objects to follow | | 1 | 1~255 | designator 구성 수. Soft Key designator 안에 맞아야 하고 벗어나면 클리핑 |
| 반복: {Object ID, X, Y} | | 2+2+2 | | designator 구성 오브젝트와 상대 위치 |

#### J.4.4 Auxiliary Input Type 1 object (type 30, v2 전용)

Auxiliary Input의 designator, 키/스위치/다이얼 번호, function type을 정의한다. 허용 명령: Change Child Location, Get Attribute Value. 이벤트 없음.

**Table J.3 — Auxiliary Input Type 1 레코드**

| 속성 | 크기 | 값 | 설명 |
|---|---|---|---|
| Object ID | 2 | 0~65534 | |
| Type | 1 | =30 | |
| Background colour | 1 | 0~255 | |
| Function type | 1 | 0/1/2 | 0 = Latching Boolean, 1 = Analogue, 2 = Non-latching Boolean |
| Input ID | 1 | 0~250 | 입력 식별 번호 — Auxiliary Input 유닛이 status message 송신 시 특정 입력을 식별하는 데 사용 |
| Number of objects to follow | 1 | 1~255 | designator 구성 수 |
| 반복: {Object ID, X, Y} | 2+2+2 | | designator 구성 오브젝트와 상대 위치 |

(v3 이상 VT는 파싱·검증만 하고 할당에 사용하지 않음)

#### J.4.5 Auxiliary Input Type 2 object (type 32)

허용 명령: Change Background Colour, Change Child Location, Change Child Position, Change Attribute, Get Attribute Value. 이벤트 없음.

**Table J.4 — Auxiliary Input Type 2 레코드**

| 속성 | AID | 크기 | 값 | 설명 |
|---|---|---|---|---|
| Object ID | | 2 | 0~65534 | |
| Type | [0] | 1 | =32 | |
| Background colour | 1 | 1 | 0~255 | |
| Function attributes | [2] | 1 | 0~255 | Bits 0~4 = Auxiliary function type(Table J.5)<br>Bit 5 = Critical Control: 0 = critical 기능 제어 불가(ISO 15077의 non-critical 조작구), 1 = critical 기능 제어 가능(critical 조작구)<br>Bit 6 = Reserved(0)<br>Bit 7 = Single-assignment: 0 = 여러 Auxiliary Function에 할당 가능, 1 = 단일 기능에만 할당 |
| Number of objects to follow | | 1 | 1~255 | designator 구성 수 |
| 반복: {Object ID, X, Y} | | 2+2+2 | | designator 구성 오브젝트와 상대 위치 |

#### J.4.6 Auxiliary Function Type 2 types (Table J.5)

기능·입력 오브젝트는 Table J.5의 타입 중 하나를 따라야 하며, 기능을 입력에 할당할 때 두 타입은 표의 요건대로 일치해야 한다. 표의 값들은 status message(J.7.9)로 전송된다. VT는 할당 주체가 운전자든 Working Set이든, 할당된 입력의 타입이 기능 타입과 <strong>정확히 일치</strong>함을 보장해야 한다. Auxiliary Input은 ISO 15077의 조작구 요건을 충족해야 한다.

| Type ID | 타입 | Status message 값 |
|---|---|---|
| 0 | Boolean — Latching(위치 유지) On/Off, 2단 스위치(SPDT) | Value 1: 0 = Off(뒤/아래/왼쪽/미누름), 1 = On(앞/위/오른쪽/누름). Value 2: 전원 인가 후 Off→On 전이 횟수(FFFF₁₆에서 0으로 오버플로) |
| 1 | Analogue(위치 유지) | Value 1: 0 %(뒤/아래/왼쪽/반시계) ~ 100 %(FAFF₁₆, 앞/위/오른쪽/시계). Value 2: Reserved FFFF₁₆ |
| 2 | Boolean — Non-Latching(momentary) 증가, 2단 스위치(momentary SPDT) | Value 1: 0 = Off, 1 = Momentary(작동), 2 = held. Value 2: Off→not Off 전이 횟수(Momentary→held는 미집계) |
| 3 | Analogue — 50 % 복귀(좌/우), 양방향 아날로그(중앙 복귀) | Value 1: 0~100 %. Value 2: Reserved FFFF₁₆ |
| 4 | Analogue — 0 % 복귀, 증가, 단방향 아날로그 | Value 1: 0~100 %. Value 2: Reserved FFFF₁₆ |
| 5 | Dual Boolean — 양쪽 Latching On/Off/On, 3단 스위치(전위치 래치, 중앙 Off) | Value 1: 0 = Off(중앙), 1 = On(앞/위/오른쪽), 4 = On(뒤/아래/왼쪽). Value 2: Off→On 전이 횟수 |
| 6 | Dual Boolean — 양쪽 Non-Latching(momentary), 증가/Off/감소·Raise/Off/Lower, 3단 스위치(중앙 복귀) | Value 1: 0 = Off, 1 = Momentary 앞/위/오른쪽, 2 = held 앞/위/오른쪽, 4 = Momentary 뒤/아래/왼쪽, 8 = held 뒤/아래/왼쪽. Value 2: Off→not Off 전이 횟수 |
| 7 | Dual Boolean — 위 Latching/아래 Momentary, 3단 스위치 | Value 1: 0 = Off(래치), 1 = On 앞/위/오른쪽(래치), 4 = On 뒤/아래/왼쪽(비래치), 8 = held 뒤/아래/왼쪽(비래치). Value 2: Off→not Off 전이 횟수(On→held 미집계) |
| 8 | Dual Boolean — 아래 Latching/위 Momentary, 3단 스위치 | Value 1: 0 = Off(래치), 1 = On 앞/위/오른쪽(비래치), 2 = held 앞/위/오른쪽(비래치), 4 = On 뒤/아래/왼쪽(래치). Value 2: 동일 규칙 |
| 9 | Combined Analogue — 50 % 복귀 + Dual Boolean Latching(0 %·100 % 위치에서 래치) | Value 1: 0~100 %, FB00₁₆ = Latched forward, FB01₁₆ = Latched backward. Value 2: 비래치→래치 전이 횟수 |
| 10 | Combined Analogue — 위치 유지 + Dual Boolean Latching(0 %·100 % 래치) | Value 1·2: Type 9와 동일 구성 |
| 11 | Quadrature Boolean — Non-Latching, 직교 장착 3단 스위치 2개(중앙 복귀) | Value 1: 비트쌍 — Bits 1~0 Forward/up, 3~2 Backward/down, 5~4 Right, 7~6 Left. 쌍별 값: 00 = Off, 01 = On(첫 작동), 10 = held, 11 = reserved. 비트 조합으로 held→held 전이 표현 가능(Figure J.2). Value 2: 임의 축의 Off→On 전이 횟수(On→held 미집계) |
| 12 | Quadrature Analogue — 위치 유지, 직교 아날로그 2축(각 축 중앙 = 50 %) | Value 1: 축 1 0~100 %(0 = 뒤/아래, FAFF₁₆ = 앞/위). Value 2: 축 2 0~100 %(0 = 왼쪽, FAFF₁₆ = 오른쪽) |
| 13 | Quadrature Analogue — 중앙(50 %) 복귀 | Value 1·2: Type 12와 동일 구성 |
| 14 | Bidirectional Encoder | "증가" 방향 회전 시 카운트 증가, 반대 방향 시 감소. Value 1: 현재 카운트(0~FFFF₁₆, 롤오버). Value 2: Calibration — 회전당 인코더 카운트(1~FFFF₁₆ 고정값) |
| 15~30 | Reserved | 향후 사용 |
| 31 | Reserved | Remove assignment command에 사용 |

:::details Figure J.2 — Quadrature Boolean 값 표현
Type 11에서 8방향 값은 4개 비트쌍의 조합으로 인코딩된다. 괄호 값은 held 상태, 괄호 없는 값은 상태 전이 시 보고 값이다. 예: 중앙→오른쪽 이동 = 16, 오른쪽 held = 32, 오른쪽→우하단 이동 = 36, 우하단 held = 40. 대각선은 두 축 비트의 합으로 표현된다(예: 앞+오른쪽 held = 34).
:::

#### J.4.7 Auxiliary Control Designator Type 2 Object Pointer (type 33)

Working Set이 Auxiliary Input Type 2·Auxiliary Function Type 2의 designator를 Data Mask의 원하는 좌표에 배치할 수 있게 하는 특수 포인터다. VT가 <strong>서로 다른 Working Set의 오브젝트를 하나의 표시로 결합</strong>할 수 있게 해 준다. NULL Object ID를 가리킬 수 있으며 이 경우 pointer type 2가 아니면 아무것도 그리지 않는다. 오브젝트 풀이 자기 Auxiliary Input과 이를 제어하는 Auxiliary Function(또는 그 반대)의 현재 할당 관계를 시각적으로 표시할 수 있게 한다. 묵시적 크기는 VT Soft Key designator 크기와 같다(4.5.3).

Input List 오브젝트와 유사하게 동작하되 다음이 다르다: 운전자·Working Set이 값을 선택할 수 없고, Change Numeric Value command가 절대 전송되지 않으며, disable/enable이 불가능하다. VT는 이 오브젝트를 확장(expand)해 연관된 Working Set designator + auxiliary object designator 세트를 보여주는 수단을 제공해야 하며, 확장 뷰의 형태는 VT 고유다.

Pointer Type별 동작:

- <strong>Type 0, 2</strong>: 같은 풀 안의 오브젝트를 가리킨다. Type 0 = 참조된 auxiliary 오브젝트의 designator를 표시, Type 2 = 이 포인터를 소유한 Working Set의 designator를 표시(이때 Auxiliary Object ID는 FFFF₁₆).
- <strong>Type 1, 3</strong>: 이 풀의 auxiliary 오브젝트에 <strong>할당 관계</strong>가 있는 상대편 오브젝트를 참조한다. Type 1 = 할당된 상대 auxiliary 오브젝트의 designator를 표시, Type 3 = 그 상대를 소유한 Working Set의 designator를 표시.
- <strong>Instance 0이 아닌 VT</strong>: 할당을 만들지 않고 할당 정보에도 접근할 수 없으므로, pointer type 1·3에 대해서는 "이 auxiliary 오브젝트에 할당이 있을 수 있으나 이 VT는 표시할 수 없음"을 고유 방식으로 표시해야 한다. designator는 Working Set의 Data Mask 위에 그려지므로, Working Set은 이 고유 표시를 피하려고 오브젝트를 숨기는 선택을 할 수 있다.
- 할당된 오브젝트가 없으면 VT는 고유 방식으로 "할당 없음"을 표시한다. 단일 할당이면 참조 오브젝트의 designator를 표시한다.
- <strong>복수 할당</strong>(하나의 Auxiliary Input에 여러 Auxiliary Function): 비확장 뷰에서는 복수 할당임을 고유 방식으로 표시하고, 선택 시 확장 뷰에 할당 목록을 표시한다. Type 1이면 확장 뷰에 할당된 Working Set designator + Auxiliary Function Type 2 designator 쌍을, Type 3이면 할당된 Working Set designator만 표시한다(같은 WS가 여러 번 할당되면 그 수만큼 반복 표시).

허용 명령: Change Attribute, Get Attribute Value. 이벤트 없음.

**Table J.6 — Auxiliary Control Designator Type 2 Object Pointer 레코드**

| 속성 | AID | 크기 | 값 | 설명 |
|---|---|---|---|---|
| Object ID | | 2 | 0~65534 | |
| Type | [0] | 1 | =33 | |
| Pointer Type | [1] | 1 | 0~3 | 0 = Byte 5~6의 auxiliary 오브젝트를 가리킴 / 1 = Byte 5~6의 오브젝트에 할당된 상대 Auxiliary Function(또는 Input) / 2 = 이 포인터 소유 WS의 Working Set 오브젝트(ID는 FFFF₁₆) / 3 = Byte 5~6 오브젝트에 할당된 상대를 소유한 WS의 Working Set 오브젝트 |
| Auxiliary Object ID | 2 | 2 | 0~65534, 65535 | 참조하는 Auxiliary Function/Input Object ID 또는 NULL |

**Table J.7 — 비확장 뷰에서 VT가 표시하는 내용** (AI1이 AF1에 할당되어 있다고 가정)

| Pointer Type | 풀 소유자 | Byte 5~6 참조 | 비확장 뷰 표시 |
|---|---|---|---|
| 0 | AF1 / AI1 | AF1 / AI1 | AF1의 기능 designator / AI1의 입력 designator |
| 1 | AF1 / AI1 | AF1 / AI1 | AF1에 할당된 AI1의 입력 designator / AI1에 할당된 AF1의 기능 designator |
| 2 | AF1 / AI1 | FFFF₁₆ | AF1 소유 WS designator / AI1 소유 WS designator |
| 3 | AF1 / AI1 | AF1 / AI1 | AI1 소유 WS designator(AF1에 할당) / AF1 소유 WS designator(AI1에 할당) |

### J.5 자동 Auxiliary Control 할당

할당 프로세스는 최초의 Preferred Assignment command로 시작되며, 이후 다음 경우에 반복된다: (a) 할당에 관여된 Auxiliary Input/Function 오브젝트를 할당이 무효가 되는 방식으로 바꾸는 추가 end of object pool 메시지 수신, (b) 할당을 바꾸는 유효한 Preferred Assignment command 수신, (c) 할당에 관여된 오브젝트 풀의 제거(의도적 삭제 또는 통신 상실).

- VT는 각 Preferred Assignment command를 검증하고 <strong>즉시</strong> Preferred Assignment response를 보내야 한다. 에러가 하나라도 있으면 명령 전체를 무시하고 응답에 에러 코드를 보고하며, 할당 프로세스를 수행하지 않는다(에러 예: 잘못된 NAME·Model Identification Code, 잘못된 Object ID 등).
- VT는 선호 할당을 운전자에게 알리고, 운전자가 할당을 바꾸거나 할당 프로세스의 전부/일부를 보류하게 허용할 수 있다. 프로세스 시작 전 운전자 확인을 요구할 수도 있다(ISO 15077).

<strong>Instance 0 VT의 할당 프로세스 단계</strong>:

1. Auxiliary Input을 제공하는 Working Set들을 파악한다(풀에 Auxiliary Input 오브젝트가 하나 이상 있으면 제공자).
2. 각 Auxiliary Input의 function type(Table J.5)과 designator, 소속 WS의 designator를 파악한다. VT 자신이 입력을 제공하면 자신·입력들의 designator를 스스로 정의한다.
3. Auxiliary Function을 제공하는 Working Set들을 파악한다.
4. 각 Auxiliary Function의 function type과 designator, 소속 WS designator를 파악한다. VT 자신이 기능을 제공하는 경우도 마찬가지.
5. Preferred Assignment command로 트리거된 경우: 명령에 할당이 명시된 기능은 그 기능에 대한 할당 명령으로, 명시되지 않은 기능은 <strong>할당 제거 명령</strong>으로 해석한다(J.7.7).
6. 선호 할당과 기존 할당을 검증해 충돌을 감지한다. 충돌 조건: (I) 할당의 "Auxiliary Function Type" 값 불일치, (II) 기능의 Single Assignment 비트 = 1인데 해당 입력이 복수 기능에 매핑됨/되게 됨, (III) 입력의 Single Assignment 비트 = 1인데 그 입력이 복수 기능에 매핑됨/되게 됨, (IV) 기능의 Assignment Restriction 비트 = 1인데 해당 입력이 선호 할당이 아님, (V) 입력의 Critical Control 비트 = 0인데 기능의 Critical Control 비트 = 1, (VI) 하나의 Auxiliary Function을 복수 입력에 할당하려 함, (VII) 할당된 입력·기능을 담은 풀이 제거됨.
7. 충돌 있는 각 할당에 대해: Auxiliary Function WS Master에 "remove assignment"(NULL)를 담은 Auxiliary Assignment Type 2 command를 보내고, 할당이 제거되었으며 VT의 고유 할당 화면에서 재할당해야 함을 운전자에게 알린다.
8. 충돌 없는 각 할당에 대해: (I) Auxiliary Input WS Master에 Auxiliary Input Status Type 2 Enable command를 보내 해당 입력의 status message를 활성화한다(이미 보냈으면 반복하지 않음). (II) Auxiliary Function WS Master에 Auxiliary Assignment Type 2 command를 보낸다 — Preferred Assignment 유래 할당이면 이미 보낸 명령은 반복하지 않고 "Preferred Assignment" 비트를 1(선호 할당으로 저장하지 말 것)로, 운전자 수정 유래 할당이면 이미 보냈어도 반복하고 비트를 0(선호 할당으로 저장)으로 설정한다.
9. 할당이 없는 각 Auxiliary Function에 대해 "remove assignment"(NULL) 명령을 보낸다. 운전자 조작으로 인한 제거이면 Preferred Assignment 비트 = 0.
10. 할당이 없는 각 Auxiliary Input에 대해 Enable command로 해당 status message를 비활성화한다.

할당·충돌 감지 순서는 VT 설계 사항이며 Object ID나 명령 내 순서로 가정할 수 없다. Auxiliary Function WS Master는 자기 기능들의 할당 상태를 감시해야 하며, "Working State"에 들어갔는데 정상 동작에 필요한 기능이 다 할당되지 않았으면 적절한 조치를 해야 한다(예: 운전자에게 VT 할당 화면에서 할당하라고 알림).

### J.6 수동 Auxiliary Control 할당

초기화 이후 언제든 운전자가 할당을 설정·변경할 수 있다. 절차는 VT 고유이며 instance 0 VT에만 적용된다. J.5와 기능적으로 동등하고 운전자 상호작용 방식만 다르다. 규칙:

1. 기능을 제공하는 Working Set으로부터 유효한 Preferred Assignment command를 받기 전에는 VT는 그 Auxiliary Function에 대한 수동 할당을 허용하지 않는다.
2. 하나의 Auxiliary Input은 하나 이상의 Auxiliary Function에 할당될 수 있다(1:N). 단 기능 또는 입력 오브젝트에 Single Assignment 비트가 세워져 있으면 1:1이 강제된다.
3. 하나의 Auxiliary Function은 복수 입력에 할당될 수 없다.
4. 기능은 유효한 Assignment Restriction을 위반하지 않는 호환 입력에만 할당할 수 있다.
5. 기능의 Critical Control 비트가 세워진 경우를 제외하면 아무 호환 입력에나 할당할 수 있다.
6. 입력은 <strong>같은 타입</strong>의 기능에만 할당한다(Table J.5).
7. 운전자가 할당을 선택하면: (I) 입력 측에 Auxiliary Input Status Type 2 Enable command로 status message를 활성화한다(각 메시지는 입력 WS의 확인응답 필요). (II) 그 입력에 (비충돌로) 할당된 각 기능에 대해, 아직 할당 안 된 경우 Auxiliary Assignment Type 2 command를 기능 WS Master로 보낸다(각 메시지는 기능 WS의 확인응답 필요).
8. 기능 WS Master는 할당을 새 선호 할당으로 저장한다. 다양한 입력 구성에 적응하기 위해 선호 할당용 추가 저장 공간을 둘 수 있다. (I) 현재 할당을 언제 선호 할당으로 확정할지는 WS 책임이다(할당 명령 수신 시, key off, 전원 상실, 고유 화면 버튼 등). (II) WS는 선호 할당을 파일 서버에 저장해 "Functionally Identical WS" 간 이전에 쓸 수 있다. (III) WS는 Model Identification Code가 같은, 이전에 할당됐던 유닛과 "Functionally Identical"인 대체 입력 유닛에 맞게 Preferred Assignment command를 적응시킬 수 있다.
9. 할당 취소는 세 방법 중 하나로 한다: 기능에 다른 입력을 할당(덮어쓰기), 기능에 NULL 할당(미할당 상태로 남김), Working Set 전원 차단. 앞의 두 경우: (I) VT는 기능 WS로 Auxiliary Assignment Type 2 command를 보내 변경·제거를 일으킨다(확인응답 필요). (II) 같은 입력에 다른 기능이 남아 있지 않으면 VT는 입력 WS Master로 Enable command를 보내 해당 status message를 비활성화한다(확인응답 필요).

Figure J.7은 전형적 시퀀스를 보여준다: 입력 유닛이 Maintenance(Status=0 Initializing) 브로드캐스트 → 풀 업로드 → Maintenance(Status=1 Ready) → 기능 WS가 Preferred Assignment 송신·응답 수신 → VT 할당 프로세스(Status Enable ↔ 응답, Assignment ↔ 응답) → 입력 status 브로드캐스트 시작 → 운전자가 할당 제거 시 Assignment(NULL) → Status Enable(Disable) → status 송신 종료.

### J.7 Auxiliary control 메시지

사용 메시지 목록: Auxiliary Assignment Type 1 command/response, Auxiliary Input Type 1 status(응답 없음), Auxiliary Assignment Type 2 command/response, Preferred Assignment command/response, Auxiliary Input Status Type 2 Enable command/response, Auxiliary Input Type 2 Status message(응답 없음), Auxiliary Input Type 2 Maintenance message(응답 없음).

#### J.7.2~J.7.4 Type 1 메시지 (v2 유산)

v2 메시지의 가시성 유지를 위해서만 존재한다. v3 이상 VT는 전송·활용하지 않으며, v3 이상 Working Set은 보내면 안 된다.

- **Auxiliary Assignment Type 1 command** (VT function = 32, 8바이트, VT to ECU): Byte 2 = 입력 장치의 SA / Byte 3 = Auxiliary Input number(0~250) 또는 FF₁₆("NULL", 미할당) / Byte 4,5 = Auxiliary Function Object ID.
- **response**: 동일 필드 반향.
- **Auxiliary Input Type 1 status** (VT function = 33, 8바이트, 입력 유닛이 Destination-Global 송신, 초당 1회 + 변경 시 최대 초당 5회): Byte 2 = Input Number(0~250) / Byte 3,4 = 아날로그 값(Boolean이면 FFFF₁₆) / Byte 5,6 = disabled→enabled 전이 횟수(전원 인가 후 누적, 아날로그면 0) / Byte 7 = 아날로그면 FF₁₆, 아니면 0 = Disabled, 1 = Enabled, 2 = non-latched Boolean held.

#### J.7.5 Auxiliary Assignment Type 2 command

VT가 Auxiliary Input을 Auxiliary Function에 할당·재할당·할당 제거할 때 쓴다. VT는 이 명령을 보낸 뒤 그 Working Set의 확인응답을 받기 전에는 같은 기능에 다른 입력을 할당해서는 안 된다. <strong>2 s</strong> 안에 확인응답이 없으면 재전송하고, 3회 실패하면 해당 Auxiliary Function을 쓸 수 없음을 운전자에게 알린다.

- 기능의 할당을 한 입력에서 다른 입력으로 바꿀 때 VT는 이전 입력의 할당을 먼저 제거해도 되고 새 입력으로 직접 할당해도 된다.
- Auxiliary Function 설계는 할당 명령 수신 시점의 입력 초기 상태를 고려해야 한다. 조작구의 상태가 제어 대상 기능의 상태와 동기화되어 있지 않을 수 있으며, 이 충돌 해소는 기능 쪽 책임이다. 예: 주차 브레이크 제어 기능이 할당될 때 입력 신호가 "해제" 상태라면, 할당 전에 "체결" 신호를 본 적이 없으므로 운전자 개입(Alarm Mask 표시, 입력을 체결 상태로 한 번 돌리게 요구 등)을 거친 뒤에야 해제 신호에 반응하도록 할 수 있다.
- VT의 고유 할당 화면은 "입력 타입은 같은 타입의 기능에만 할당 가능" 규칙을 강제해야 한다(Figure J.9는 예시 화면).
- Preferred Assignment 비트: 운전자가 Auxiliary Input Type 2를 Auxiliary Function Type 2에 할당하기로 선택한 경우에만 0(선호 할당으로 저장)으로 설정하고, 그 외 모든 상황에서는 1로 설정한다.

**구조** (VT function = 36, <strong>14바이트</strong>, VT to ECU)

| 바이트 | 내용 |
|---|---|
| 2~9 | Auxiliary Input Unit의 64-bit NAME, 또는 FFFFFFFFFFFFFFFF₁₆(할당 제거) |
| 10 | Flags — Bit 7 = Preferred Assignment(0 = 선호 할당으로 저장, 1 = 저장하지 말 것; 에러 상황(입력 유닛의 unexpected shutdown·통신 에러 등)에서는 반드시 1)<br>Bits 6~5 = Reserved(0)<br>Bits 4~0 = 할당된 입력의 Auxiliary function type, 또는 1F₁₆(할당 제거) |
| 11, 12 | Auxiliary Input Object ID, 또는 FFFF₁₆(현재 할당 제거) |
| 13, 14 | Auxiliary Function Object ID, 또는 FFFF₁₆(모든 할당된 기능에서 현재 할당 제거) |

허용되는 할당 제거 형태(Figure J.10):

| 형태 | NAME | Function type | Input Object ID | Function Object ID |
|---|---|---|---|---|
| (a) 특정 WS 특정 입력에 할당됐던 기능 하나의 할당 제거 | FFFFFFFFFFFFFFFF₁₆ | 1F₁₆ | FFFF₁₆ | 해당 기능 ID |
| (b) 한 Working Set의 현재 할당된 모든 입력 할당 제거 | FFFFFFFFFFFFFFFF₁₆ | 1F₁₆ | FFFF₁₆ | FFFF₁₆ |

#### J.7.6 Auxiliary Assignment Type 2 response

Working Set은 Auxiliary Assignment Type 2 command 수신 후 <strong>1 s 이내</strong>에 확인응답을 보내야 한다. Working Set이 할당을 거부하면 VT는 운전자에게 알리고, 그 입력이 다른 기능에 할당되어 있지 않으면 입력 status message를 비활성화할 수 있다.

**구조** (VT function = 36, 8바이트, ECU to VT): Byte 2,3 = Auxiliary Function Object ID / Byte 4 Error Codes: Bit 0 = 에러, 할당 거부. Bit 1은 v5 이하에서 "이미 같은 입력에 할당됨"이었으나 에러 상황 전달이 아니며 동작 변화를 일으키지 않아야 하고, v6 이상에서는 reserved(0)다.

#### J.7.7 Preferred Assignment command

v3 이상에서 사용 가능하며 Type 2 Auxiliary Function에만 적용된다. Auxiliary Input→Auxiliary Function의 사전 정의 할당을 지정한다.

- Assignment Restriction = 1인 기능에 대해서는 이 명령이 <strong>유일하게 허용되는 할당</strong>을 전달한다.
- 네트워크에 없는 Auxiliary Input 유닛에 대한 참조를 포함해서는 안 된다.
- Auxiliary Function을 제공하는 Working Set만 보낼 수 있다.
- 송신 후 VT의 확인응답을 받기 전에는 다른 명령을 보내지 않는다. 2 s 내 미수신 시 재전송, 3회 실패 시 운전자에게 기능 사용 불가를 알린다.
- 기능 WS는 선호 입력 유닛을 스스로 결정한다. 고려 요소: Model Identification Code, 64-bit NAME(Function Instance·Manufacturer Code 포함, Identity Number 제외). 이로써 "Functionally Identical"한 다른 입력 유닛(예: 같은 Function Instance·제조사 코드·Model ID의 조이스틱을 가진 다른 트랙터에 파종기를 연결)도 수용할 수 있다.
- 이 명령은 그 Working Set의 <strong>완전한 할당 세트</strong>를 나타낸다. 명령에 포함되지 않은 기능은 미할당 상태다(이거나 그렇게 되어야 한다).
- 풀 로드 후 다음 조건 중 하나로 <strong>한 번</strong> 송신해야 한다(VT가 이 메시지를 받기 전에는 수동 할당이 만들어질 수 없으므로): 선호 할당이 없는 경우 / 네트워크에서 선호 입력 유닛을 감지한 경우(이때 그 유닛의 Auxiliary Input Type 2 Maintenance message가 Status=Ready가 될 때까지 기다려야 하며, 안 기다리면 응답에 Input Object ID not valid 에러가 날 수 있다; 다른 선호 유닛 감지를 위해 더 지연할 수 있다) / 선호 입력 유닛이 감지되지 않은 경우(입력 유닛 감지를 위해 지연 가능).
- 최초 송신 이후 재송신 트리거: 이전에 감지되지 않았거나 재초기화된 선호 입력 유닛 감지(Ready 대기 규칙 동일) / 활성 할당이 있는 입력 유닛의 네트워크 이탈 또는 기존·대체 유닛으로의 재구성 필요 / (선택) 기능 제공 WS의 운전자 인터페이스에서 다른 선호 할당 세트 선택 / 기능 WS가 할당에 영향을 줄 수 있게 자기 풀을 수정한 경우. <strong>트리거 조건당 한 번만</strong> 보낸다.
- VT는 수신 시 J.5 자동 할당 프로세스에 따라 동작한다. 각 Auxiliary Function Type 2 Object ID가 메시지 안에 한 번만 나오게 하는 것은 WS 책임이다.

**구조** (VT function = 34, 가변 길이, ECU to VT): Byte 2 = 입력 유닛 수, 이후 유닛마다 반복 { 64-bit NAME(8바이트), Model Identification Code(2바이트), 이 유닛의 선호 기능 수(1바이트), 반복 { Auxiliary Function Object ID(2), Auxiliary Input Object ID(2) } }.

#### J.7.8 Preferred Assignment response

VT의 확인응답(8바이트): Byte 2 Error Codes: Bit 0 = 입력 유닛(NAME 또는 Model Identification Code) 무효, Bit 1 = Function Object ID 무효, Bit 2 = Input Object ID 무효, Bit 3 = Auxiliary Function Object ID 중복, Bit 4 = 기타 에러. Byte 3,4 = 문제가 된 할당의 Auxiliary Function Object ID(에러 없으면 NULL Object ID).

#### J.7.9 Auxiliary Input Type 2 Status message

초기화 시점부터 VT가 활성화하기 전까지 입력 유닛은 status message를 자동 송신해서는 안 된다. 활성화 후(또는 learn mode에서):

- 초당 1회 + 값 변경 시 즉시 송신. 특정 입력에 대해 메시지 간 최소 50 ms(최대 20 Hz). non-latched Boolean 홀드 중 200 ms마다 송신.
- 설계 주의: 여러 입력이 동시에 20 Hz로 전이를 보내면 이미 혼잡한 CAN 버스에 부담이 된다. 아날로그 입력의 노이즈로 평균값이 그대로인데 값이 오래 떨리는 경우 등에는 빈도를 제한해야 한다(should).
- non-latched Boolean 입력이 홀드 중인데 메시지 간격이 300 ms를 넘으면 기능 WS는 릴리스된 것으로 처리해야 한다.
- <strong>잠금 상태</strong>: 잠금 중 전달되는 "value"는 잠금 활성화 시점의 값을 반영한다. 잠긴 상태에서 조작구가 조작되면 값은 그대로 두고 Interaction Detected status를 1로 세운다. 잠금 해제 시 Interaction Detected는 0으로 리셋된다. 작업기 기능은 이 상태를 "잠금 시점에 활성이던 동작의 비활성화"에 쓸 수 있다.
- 입력이 무효 상태(스위치 고착, 단선 등)로 판정되면 Error Range 값으로 상태를 알리고, 추가로 연결된 VT에 Alarm Mask를 표시할 수 있다.
- 송신 방식: learn mode가 아니면 global address로 브로드캐스트(모든 WS가 수신, 무확인). learn mode에서는 NAME이 Function Instance 0을 가리키는 VT로 Destination-Specific 송신(무확인) — 작업기가 메시지를 명령으로 오해할 가능성을 최소화하고 VT 구현도 단순해진다.
- 권장 priority = 3 (제어 목적 메시지의 표준 권고와 일치하며 transport protocol·extended transport protocol 메시지에 막히지 않게 한다).

**구조** (VT function = 38, 8바이트)

| 바이트 | 내용 |
|---|---|
| 2, 3 | Auxiliary Input Object ID (0~65534) |
| 4, 5 | Value 1 (Table J.5). 아날로그: 분해능 0,001 556 29 %/bit, 오프셋 0, Valid 0000₁₆~FAFF₁₆, Reserved FB00₁₆~FDFF₁₆, Error FE00₁₆~FEFF₁₆, N/A FF00₁₆~FFFF₁₆. 디지털 카운트: 0000₁₆~FFFF₁₆ (범위 제약이 있는 타입은 그 제약이 Valid 범위이고 Reserved/Error/N/A는 아날로그와 동일 규칙) |
| 6, 7 | Value 2 (Table J.5). 인코딩 규칙 동일 |
| 8 | Operating State: Bit 0 = Learn mode 활성, Bit 1 = learn mode에서 입력 작동됨(bit 0이 1이어야 함), Bit 2 = Control is Locked(v6+), Bit 3 = 잠금 중 Interaction Detected(v6+), Bits 4~7 Reserved |

#### J.7.10 Auxiliary Input Type 2 Maintenance message

Auxiliary Input <strong>Working Set</strong>(개별 입력 조작구가 아니라)이 <strong>100 ms 주기(초당 10회)</strong>로 global address에 브로드캐스트한다(무확인, 권장 priority 3). VT와, 그 입력 유닛의 조작구에 할당된 모든 Auxiliary Function Working Set이 감시해야 한다.

**구조** (VT function = 35, 8바이트): Byte 2,3 = 입력 유닛의 Model Identification Code(제조사 정의, 0~FFFE₁₆) / Byte 4 = Status: 0 = Initializing(풀이 아직 할당에 사용 불가), 1 = Ready(풀이 VT에 로드되어 할당 가능).

동작 규칙:

- 기존 할당된 Auxiliary Input 오브젝트의 변경·삭제로 풀을 바꿔야 하는 입력 유닛의 절차: (1) 구성 변경 전에 status message가 활성화된 입력이 있었다면 Auxiliary Control이 사용 불가해질 수 있음을 운전자에게 알린다(v6에서 신설된 WS 측 의무 — 재구성 원인을 아는 쪽은 WS뿐이므로 WS에 책임을 두어 불필요한 이중 경고를 줄인다), (2) Maintenance message 송신을 <strong>500 ms 초과</strong> 중단, (3) Status = Initializing으로 송신 재개(이때 Model Identification Code는 개정된 구성을 반영해 바뀌어야 함), (4) 풀 갱신(기존 풀 삭제 또는 부분 업데이트 전송, Annex C), (5) VT로부터 에러 없는 End of Object Pool response를 받으면 Status = Ready로 표시. 이 절차가 시스템의 Working Set들이 기능-입력 연결을 안전하게 끊었다 다시 잇는 수단이 된다.
- 기능 WS가 이 메시지를 <strong>300 ms</strong> 동안 못 받으면 입력 WS의 unexpected shutdown 가능성을 가정하고 그 입력 유닛의 모든 기능 할당 제거를 포함한 조치를 해야 한다.
- VT가 300 ms 동안 못 받으면 마찬가지로 shutdown/재구성을 가정하고 모든 기능 할당을 제거하되, 제거 명령에서 "미할당을 새 선호 할당으로 저장하지 말 것"(Preferred Assignment 비트 = 1)을 지시해야 한다.
- 입력 WS는 4.6.9의 연결 관리 요건을 따라야 하므로 이 메시지와 <strong>별도로</strong> Working Set Maintenance message도 초당 1회 보낸다.
- Model Identification Code는 주어진 구성에서 런타임에 바뀌지 않으며, 재구성 시에만 바뀔 수 있다.
- Status는 할당 작업에 대한 입력 준비 상태를 나타낸다. 메시지 시작 시 Initializing으로 초기화하고, 에러 없는 End of Object Pool response 또는 에러 없는 Load Version response/Extended Load Version response 수신 시 Ready로 바꾼다. Auxiliary Function들은 Ready 표시를 Preferred Assignment command 송신 트리거로 쓴다. 입력 유닛이 런타임에 가용 입력을 바꿀 수 있는 사유(풀에 입력 추가, 기존 입력 오브젝트 재로드, 입력 제거)가 있으면 그동안 Status = Initializing으로 둔다.

#### J.7.11~J.7.12 Auxiliary Input Status Type 2 Enable command/response

VT가 Auxiliary Input status message를 활성화/비활성화한다. 목적은 둘이다: 불필요한 네트워크 메시징 감소, 그리고 Auxiliary Function이 <strong>미할당</strong> 입력에 반응할 가능성 감소. VT는 이 명령 송신 후 입력 측의 확인응답을 받기 전에는 그 입력에 기능을 할당하지 않는다. 2 s 내 미수신 시 재전송, 3회 실패 시 해당 Auxiliary Input 사용 불가를 운전자에게 알린다.

**command** (VT function = 37, 8바이트, VT to ECU): Byte 2,3 = Auxiliary Input Object ID — FFFF₁₆는 "모든 입력"을 의미하며 <strong>disable일 때만</strong> 사용 가능 / Byte 4 = Enable: 0 = 해당 입력의 status message 비활성화, 1 = 활성화.

**response** (ECU to VT): Byte 2,3 = 응답 대상 Object ID(또는 FFFF₁₆) / Byte 4 = Status: 0 = 비활성화됨, 1 = 활성화됨 / Byte 5 Error Codes(0 = 명령 수락): Bit 0 = Invalid Auxiliary Input Object ID, Bit 1 = 기타 에러.

#### J.7.13~J.7.14 Auxiliary Capabilities request/response

v5 이상, Type 2 auxiliary control 전용. 임의의 CF가 <strong>function instance 0 VT</strong>에게 Auxiliary Input 또는 Auxiliary Function을 지원하는 Working Set들의 능력을 조회할 수 있다. 보고 기준은 Working Set 오브젝트 풀 내의 <strong>존재 여부만</strong>이다(입력 상태·초기 선호 할당은 반영 안 됨). Auxiliary Function을 제공하는 Working Set은 이 요청으로 현재 시스템에 맞는 기능 제공 전략을 세우기 위해 입력 유닛들의 능력을 파악할 수 있다. 요청 전에 각 입력 유닛의 Maintenance message가 "Ready"인지 확인하는 선택을 할 수 있다(Auxiliary Function 쪽에는 동등한 "Ready" status가 없다).

**request** (VT function = 39, 8바이트, ECU to VT): Byte 2 = Request Type: 0 = Auxiliary Input Unit들의 능력 요청, 1 = Auxiliary Function Unit들의 능력 요청.

**response** (VT function = 39, 가변, VT to ECU): 풀을 VT에 성공적으로 올린 auxiliary 장치들의 전체 목록과 유닛별 Set Information을 담는다. Byte 2 = 해당 Request Type의 Auxiliary Unit 수(Request Type이 무효였으면 0), 이후 유닛마다 반복 { 64-bit NAME(8바이트), 이 유닛의 set 수(1바이트), 반복 { Set Information 3바이트 } }.

**Table J.8 — Set Information(3바이트)**

| 바이트 | 항목 | 내용 |
|---|---|---|
| 1 | Number of Instances | Function attribute와 Assigned attribute가 동일한 입력/기능 인스턴스 수 |
| 2 | Function attribute | Table J.2·J.4의 Function attributes 값 |
| 3 | Assigned attribute | Bit 0: 0 = auxiliary input, 1 = auxiliary function / Bit 1 = 1: 유효한 할당 존재(J.5·J.6의 할당 절차 기준) |

### J.8 Learn Mode

VT는 운전자가 <strong>해당 입력을 직접 눌러서</strong> Auxiliary Function을 Auxiliary Input에 할당하게 하는 "learn mode"를 제공할 수 있다. 이 기능은 VT의 auxiliary 할당 화면이 표시되어 있는 동안에만 활성이어야 한다. learn mode의 활성/비활성 방법은 VT 고유다.

- learn mode가 켜져 있는 동안 VT는 VT Status message에 이를 표시해야 한다(G.2의 busy code Bit 6).
- learn mode 활성 중: 모든 Auxiliary Input은 VT의 enable 여부와 무관하게 정상 주기로 Auxiliary Input status message를 보내야 한다(learn mode에서는 J.7.9대로 instance 0 VT로 Destination-Specific 송신). VT는 status message들을 감시해 실제 조작된 Auxiliary Input에 선택된 Auxiliary Function을 할당한다(기능 표시·선택 방법은 VT 고유). Auxiliary Function Working Set들은 VT Status message가 learn mode를 표시하는 동안에는 Auxiliary Input Status message로 인한 어떤 기능도 수행해서는 안 된다.
- learn mode 진입·이탈 시 조작구 상태가 제어 대상 기능 상태와 어긋날 수 있으며, 이 충돌 해소는 Auxiliary Function 책임이다. 예: 주차 브레이크 기능이 learn mode 이전에 체결 상태였는데, learn mode 종료 시 입력 신호가 해제 상태를 전달하고 있다면 — 기능은 체결 신호를 먼저 본 적이 없으므로 운전자 개입(Alarm Mask, 입력을 체결 상태로 한 번 돌리게 요구 등)을 거친 뒤에야 해제 신호에 따라 브레이크를 풀도록 할 수 있다.

## Annex K (normative) — Character sets

8-bit 문자열의 인코딩을 정의한다. 8-bit 문자열의 인코딩은 Font Attributes 오브젝트의 Font Type 값에 따라 결정된다.

**Table K.1 — Font Type 매핑**

| VT Font Type | 인코딩 |
|---|---|
| 0 | ISO 8859-1 (ISO Latin 1) |
| 1 | ISO 8859-15 (ISO Latin 9) |
| 2 | ISO 8859-2 (ISO Latin 2)* |
| 3 | Reserved |
| 4 | ISO 8859-4 (ISO Latin 4)* |
| 5 | ISO 8859-5 (Cyrillic)* |
| 6 | Reserved |
| 7 | ISO 8859-7 (Greek)* |
| 8~239 | Reserved |
| 240~254*, 255 | Proprietary (4.6.24) |

(* 표시 font type은 v3 이하 VT에서는 미정의)

이후의 문자표(Table K.2~K.7)는 참고용이며 정확한 문자 집합은 각 ISO 문서를 따른다. 공통 규칙:

- 제어 코드 영역(00₁₆~1F₁₆, 7F₁₆, 80₁₆~9F₁₆)은 표시해서는 안 된다. 예외적으로 0A₁₆(LF)·0D₁₆(CR)은 개행 처리 규칙(4.6.19.6)을 따른다.
- A0₁₆ = NBSP(non-breaking space) — word-wrap 규칙이 적용되지 않는다.
- 00₁₆는 문자열 표시를 종료(termination)시킨다.
- 각 표의 20₁₆~7E₁₆ 구간은 ASCII와 동일하고, A0₁₆~FF₁₆ 상위 구간이 문자셋별로 다르다: K.2 Latin 1(서유럽), K.3 Latin 9(Latin 1에서 €·Š·š·Ž·ž·Œ·œ·Ÿ 대체), K.4 Latin 2(중동부 유럽), K.5 Latin 4(북유럽·발트), K.6 Cyrillic, K.7 Greek. Latin 2·4·Cyrillic·Greek 표는 v4 이상에서 필수다.
- ISO 8859-15 표는 v2 이하 VT에 4개 문자 오류(A6₁₆, A8₁₆, B4₁₆, B8₁₆ 위치의 Š/š/Ž/ž)가 있었고 v3에서 수정되었다.

**Table K.8 — WideString 최소 문자 집합**: WideString(2바이트 문자)용으로 VT가 최소한 지원해야 하는 유니코드 문자 범위를 정의한다(v4 이상 필수). 포함 범위: U+0000~U+00FF(Latin-1 상당), U+0100~U+017F(Latin Extended-A), U+02C6~U+02DD 일부(수정 문자), U+0374~U+03CE(그리스), U+0401~U+045F(키릴), U+20AC(€). 규칙은 8-bit 표와 동일하되 0000₁₆이 문자열 표시를 종료하며, 빈 칸은 필수는 아니지만 표시할 수 있는 코드다.

## Bibliography (참고문헌)

참고문헌에는 SAE J1939-72(Virtual Terminal), DIN 9684-4(User terminal), ISO 7498(OSI 기본 참조 모델), ISO 11519-1, ISO 11898(CAN), ISO 639(언어 코드), ISO/IEC 8859 시리즈(1·2·4·5·7·15), ISO/IEC 10646(UCS), ISO 3166-1(국가 코드), PNG 사양(ISO/IEC 15948:2003), 그래픽 프로그래밍 관련 서적·기사 등이 올라 있다.

