---
title: "종합 실습 (2): ISOXML 태스크 파일"
description: "FMIS와 TC가 주고받는 ISOXML 태스크 파일 세트의 이름 규칙, 루트 요소, ID 규칙, 요소 구성, 태스크 상태를 익히고 처방 태스크 파일과 작업 결과 파일을 직접 만들어 읽는다."
date: 2026-04-13
tags: [ISOBUS, ISOXML, TaskController, FMIS, XML, Python]
prev: /study/isobus/55-practice-log-vt-tc
next: /study/isobus/57-practice-binary-files
---

# 종합 실습 (2): ISOXML 태스크 파일

::: info 학습 목표
- 태스크 파일 세트가 어떤 파일로 이루어지고 이름을 어떻게 붙이는지 설명할 수 있다.
- 루트 요소와 ID 규칙을 보고 FMIS가 만든 파일과 TC가 만든 파일을 구별할 수 있다.
- TSK, TZN, PDV, DLT, GRD 같은 요소가 무엇을 담는지 읽을 수 있다.
- FMIS가 보내는 처방 태스크 파일과 TC가 돌려주는 결과 파일을 직접 써 보고 검사할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [55장 종합 실습 (1)](/study/isobus/55-practice-log-vt-tc), [42장 태스크와 시간 기록](/study/isobus/42-tc-task), [48장 DDOP 기초](/study/isobus/48-ddop-basics)
- 이 장에서 처음 나오는 말
  - FMIS: 사무실에서 농작업을 계획하고 결과를 관리하는 소프트웨어
  - MICS: TC가 들어 있는 차량 쪽 시스템
  - 태스크 파일 세트(ISOXML): FMIS와 MICS가 태스크를 주고받는 XML 파일과 바이너리 파일 묶음
  - 요소와 속성: XML에서 `<TSK ... />` 같은 꺾쇠 묶음이 요소, 그 안의 `A="TSK1"` 같은 이름과 값의 쌍이 속성
  - coding data: 고객, 농장, 제품처럼 자주 바뀌지 않는 기본 정보
  - ID와 IDREF: 요소마다 붙는 고유 번호(ID)와, 다른 요소의 ID를 가리키는 값(IDREF)
:::

사무실과 현장 사이에는 작업 지시서와 작업 일지가 오간다. 사무실은 "어느 밭에 무엇을 얼마나 뿌려라"라는 지시서를 쓰고, 현장은 일을 마친 뒤 같은 양식에 "언제 어디서 얼마나 뿌렸다"는 일지를 채워 돌려준다. ISOBUS에서 이 양식이 ISOXML 태스크 파일 세트다. 55장에서 "파일"이라고만 그렸던 처방 맵과 작업 기록을 이 장과 57장에서 직접 만들어 본다. 이 장은 XML 파일을, 57장은 바이너리 파일을 맡는다.

::: info 실습 전체 준비물
- XML을 볼 텍스트 편집기. 요소 이름에 색을 입혀 주는 편집기(예: VS Code)면 더 편하다.
- 7절의 검사 스크립트를 돌릴 파이썬 3. 기본 라이브러리만 쓴다.
- 본문의 "(추론)"은 표준 문서에 직접 적힌 규칙이 아니라 이 글이 다른 규칙에서 끌어낸 판단이라는 표시다.
:::

## 1. 파일 세트 한눈에 보기

[55장](/study/isobus/55-practice-log-vt-tc) 4절은 처방 맵과 As-Applied 로그를 "파일"이라고만 그렸다. 이 장과 57장에서는 그 파일을 ISO 11783-10(TC와 FMIS 사이의 데이터 교환을 정하는 표준 문서)의 규칙대로 직접 만들고 읽는다. FMIS(Farm Management Information System, 농장 관리 소프트웨어)와 MICS(Mobile Implement Control System, TC가 들어 있는 차량 쪽 시스템)는 CAN 메시지가 아니라 <strong>데이터 전송 파일 세트</strong>(data transfer file set)로 태스크를 주고받는다. FMIS가 계획한 태스크를 보내고, TC가 작업 결과를 같은 형식으로 돌려준다. 현장에서는 이 파일 세트를 흔히 ISOXML이라 부르지만 표준 본문에는 그 이름이 없다.

### 1.1 FMIS와 TC가 파일로 주고받는 흐름

![FMIS가 DataTransferOrigin 1, 태스크 상태 planned인 TASKDATA 파일 세트를 이동식 매체 등으로 MICS(TC)에 보내고, 작업을 마친 MICS가 DataTransferOrigin 2, 태스크 상태 completed에 장치 정보와 작업 기록 파일을 더한 같은 파일 세트를 FMIS로 돌려보내는 왕복 흐름](/images/study-isobus/56-fmis-tc-roundtrip-light.png)
![FMIS가 DataTransferOrigin 1, 태스크 상태 planned인 TASKDATA 파일 세트를 이동식 매체 등으로 MICS(TC)에 보내고, 작업을 마친 MICS가 DataTransferOrigin 2, 태스크 상태 completed에 장치 정보와 작업 기록 파일을 더한 같은 파일 세트를 FMIS로 돌려보내는 왕복 흐름](/images/study-isobus/56-fmis-tc-roundtrip-dark.png)

파일 세트는 한 번 가고 한 번 돌아온다. 가는 파일은 FMIS가 만든 계획이고(6절 실습), 돌아오는 파일은 TC가 같은 파일에 결과를 더한 것이다(7절 실습). 두 파일은 루트 요소의 `DataTransferOrigin` 값(1 = FMIS, 2 = MICS)으로 구별한다.

### 1.2 XML을 처음 본다면

파일 세트의 중심은 XML 파일이다. XML은 꺾쇠 괄호로 데이터를 묶어 적는 텍스트 형식이다. 아래 작은 예로 읽는 법만 익히자.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<TSK A="TSK1" G="1">
  <TZN A="0" B="Default rate"/>
</TSK>
```

- 첫 줄 `<?xml ... ?>`은 "이 파일은 XML 1.0이고 글자는 UTF-8로 적었다"는 선언이다.
- `<TSK ...>`로 시작해 `</TSK>`로 끝나는 덩어리가 <strong>요소</strong> 하나다. `TSK`가 요소 이름이다.
- 요소 이름 뒤의 `A="TSK1"`처럼 `이름="값"` 꼴로 붙는 것이 <strong>속성</strong>이다.
- `<TZN ... />`처럼 `/>`로 끝나는 요소는 안에 다른 것이 없는 요소다.
- 요소 안에 다른 요소를 넣을 수 있다. 위에서 TZN은 TSK의 <strong>자식 요소</strong>다.
- `<!-- ... -->`는 주석이다. 프로그램은 읽지 않는다.

XML 파일이 문법을 지키면(태그 짝이 맞고, 속성값이 따옴표로 묶이는 등) <strong>well-formed</strong>라고 한다. 여기에 더해 스키마(XSD, 어떤 요소와 속성을 어떤 순서와 형식으로 쓸지 적은 규칙 파일)까지 만족하면 <strong>valid</strong>라고 한다. 속성 형식에 나오는 `xs:decimal`(소수), `xs:ID`(문서 안에서 유일한 식별자), `xs:language`(`ko-KR` 같은 언어 코드) 같은 이름은 XML 스키마의 기본 자료형이다.

### 1.3 파일 세트의 모양과 이름 규칙

![TASKDATA 디렉터리 안에서 TASKDATA.XML의 PNT·GRD·TLG·XFR·AFE 요소가 각각 PNT00001.BIN, GRD00001.BIN, TLG00001.XML과 TLG00001.BIN, TSK00002.XML, LINKLIST.XML을 가리키는 관계](/images/study-isobus/22-taskdata-fileset-light.png)
![TASKDATA 디렉터리 안에서 TASKDATA.XML의 PNT·GRD·TLG·XFR·AFE 요소가 각각 PNT00001.BIN, GRD00001.BIN, TLG00001.XML과 TLG00001.BIN, TSK00002.XML, LINKLIST.XML을 가리키는 관계](/images/study-isobus/22-taskdata-fileset-dark.png)

그림처럼 `TASKDATA.XML` 하나가 중심이고, 그 안의 요소가 같은 디렉터리의 다른 파일을 이름으로 가리킨다. 화살표는 "이 요소가 이 파일을 가리킨다"는 뜻이다. 그림의 v4는 파일 세트 형식의 버전 4를 뜻하고, 이 장에서 "v4"라고 쓰면 그 버전에서 새로 들어온 기능이다. 이름 규칙은 다음 표와 같다.

| 규칙 | 내용 |
|---|---|
| 메인 파일 | 루트 요소 `ISO11783_TaskData`를 담은 `TASKDATA.XML` 하나 |
| 위치 | 이동식 매체면 매체 루트의 `TASKDATA` 디렉터리. 다른 전송 매체는 제조사 고유 |
| 이름 | 디렉터리·파일 이름은 대소문자를 구분하고 모두 대문자 |
| 디렉터리 | 바이너리 파일까지 모든 파일이 같은 디렉터리 |
| 인코딩 | XML 1.0, UTF-8, 텍스트 전용. 첫 줄은 `<?xml version="1.0" encoding="UTF-8"?>` |
| 표현 | 요소 안에 텍스트를 두지 않고 모든 정보를 속성으로 담는다. 요소·속성 이름은 약어(`WKR`, `A`, `B` …), 대소문자 구분, 속성값은 따옴표 |
| 유효성 | well-formed이면서 스키마 `ISO11783_TaskFile`로 valid해야 한다. 아니면 처리할 수 없다 |
| 바이너리 | grid 셀 값, 로그 데이터(둘 다 태스크 소속), Point 기하(v4) 세 종류 |

속성 이름을 `A`, `B`, `C`처럼 한 글자로 쓰는 이유를 표준은 메모리와 전송 대역폭 절약이라고 설명한다. 대신 같은 글자라도 요소마다 뜻이 다르다. TSK의 `G`는 태스크 상태이고 GRD의 `G`는 파일 이름이다. 파서(파일을 읽어 프로그램 안의 구조로 바꾸는 코드)를 만들 때 속성 사전을 요소별로 따로 두는 이유다.

받는 쪽은 coding data 요소를 요소 종류마다 최소 2,000개, 전체 최소 20,000개 처리할 수 있어야 한다. coding data는 "자주 바뀌지 않는 데이터나 태스크를 행정적으로 할당하려고 참조하는 데이터"다. 경계 점 같은 기하 요소는 coding data가 아니라 이 한도에 들지 않는다. 제조사 고유 요소·속성은 `P` + 십진 제조사 코드 + `_`로 시작하고(예: `P500_MyElement`), 다른 제조사 시스템은 그 내용을 무시한다. 전체 규칙은 [ISO 11783-10 부록](/study/isobus/appendix-iso-part10)에 정리돼 있다.

::: info 55장과 이어 읽을 때
- 55장 3.4절의 XML은 VT 오브젝트 풀을 사람이 읽기 쉽게 적은 도구별 표기다. ISO 11783-6에는 오브젝트 풀의 XML 형식이 없고, 풀은 바이너리 레코드로 전송된다. 이 장의 XML은 ISO 11783-10이 정한 규범 형식이다.
- 55장 4.1 그림의 `prescription_map.xml`, `task_log_20260413.xml`은 설명용 이름이다. 실제 파일 세트는 `TASKDATA.XML`, `GRD00001.BIN`, `TLG00001.XML`처럼 이름 규칙이 정해져 있다.
- 55장 4.1 그림의 "FMIS → TC: Task Start 명령"에 해당하는 메시지는 TC 메시지 정의에 없다. 태스크를 고르고 시작·정지하는 방법은 TC 설계자가 정한다. 버스에 드러나는 것은 TC가 Task Controller Status 메시지 Byte 5 bit 1(task totals active)로 태스크 시작·재개를 알리는 것이다([42장](/study/isobus/42-tc-task)).
:::

<small>근거: ISO 11783-10 3.2, 3.6, 5.1, 6.1, 8.1, 8.2, 8.4.1, 8.5, 8.6.1, B.8.1, D.27, D.49; ISO 11783-6 C.2</small>

## 2. 루트 요소 ISO11783_TaskData

루트 요소는 파일 세트의 맨 바깥 요소이고, 누가 어떤 버전으로 만든 파일인지 적는 표지다. 루트 요소의 속성만은 약어가 아니라 이름 그대로 쓴다. 표의 필수 열에서 r은 반드시 있어야 함(required), o는 있어도 되고 없어도 됨(optional), o/r은 상황에 따라 필수라는 뜻이다.

| 속성 | 필수 | 값과 규칙 |
|---|---|---|
| `VersionMajor` | r | 0~4. 2판(2015) FDIS 기준이 4다. 버전은 스키마 파일 이름에도 들어간다(`ISO11783_TaskFile_V4-0.xml` 식) |
| `VersionMinor` | r | 0~99. 같은 Major 안의 스키마 리비전 |
| `ManagementSoftwareManufacturer`, `ManagementSoftwareVersion` | o/r | FMIS 이름·버전, 최대 32자 |
| `TaskControllerManufacturer`, `TaskControllerVersion` | o/r | TC 이름·버전, 최대 32자. MICS가 만든 파일에서 필수, FMIS가 만든 파일에서는 쓰지 않는다 |
| `DataTransferOrigin` | r | 1 = FMIS, 2 = MICS. 파일 세트를 마지막으로 만든 쪽이다. 양쪽 모두 제대로 갱신해야 한다 |
| `lang` | o | DataTransferLanguage(v4). 파일 세트를 만든 시스템의 언어, `xs:language` |
| 자식 `TCC` | o/r | TaskControllerCapabilities(v4). MICS가 만든 파일에만, 최대 1개 |

FDIS(Final Draft International Standard)는 표준이 확정되기 직전의 최종 초안이다. 표준 문서가 보여 주는 루트 요소의 틀에는 스키마 검증용 `xmlns:xsi`와 `xsi:noNamespaceSchemaLocation` 속성도 들어 있다. 스키마에는 ISO 11783 전용 네임스페이스(요소 이름이 어느 규칙 집합에 속하는지 나타내는 접두어 체계)가 없다.

::: warning 표준의 표와 예제가 어긋나는 곳
표준의 루트 속성 표는 각주에서 o/r 네 속성이 FMIS가 만든 파일에서는 쓰이지 않는다고 적는다. 그런데 같은 곳의 예제는 `DataTransferOrigin="1"`(FMIS) 파일에 `TaskControllerManufacturer`까지 채워 넣는다. 또 각주가 붙은 `ManagementSoftware*`는 FMIS가 자기 이름을 적는 자리다. 그래서 각주는 TC 속성을 겨냥한 것으로 읽힌다. 받는 쪽은 네 속성이 있든 없든 파일을 거부하지 않는 편이 안전하다(추론).
:::

어떤 `VersionMajor`를 쓸지는 TC가 지원하는 기능(functionality)과 그 세대(generation)가 정한다. 기본 기능 TC-BAS와 위치 기반 제어 기능 TC-GEO의 1세대 구현은 TC 버전 3을, 장치의 누적 총량을 읽어 기록하는 LOG의 1세대 구현은 4를 파일 세트와 Version 메시지에 게시한다([41장](/study/isobus/41-tc-basics), [44장](/study/isobus/44-tc-multi-dl-functionality)). 아래 예제는 v4에서 들어온 `lang`, `TCC`, 시간대 표기를 쓰므로 4로 적는다.

::: details 원문을 가진 독자를 위한 메모
- 루트 속성 표와 o/r 각주, 각주와 어긋나는 예제는 모두 ISO 11783-10:2015 D.32에 있다.
- 기능 세대별 게시 버전은 F.2.1(TC-BAS), F.2.2(TC-GEO), F.2.4(LOG)에 있다.
:::

<small>근거: ISO 11783-10 8.4, 8.5, D.32, D.47, F.2.1, F.2.2, F.2.4</small>

## 3. ID 규칙

파일 세트 안의 요소는 서로를 ID로 가리킨다. 태스크가 "이 고객의 이 필지"를 가리키려면 고객과 필지에 번호가 있어야 하기 때문이다. 식별자(ID) 속성을 가진 요소를 엔티티라 부르고, 그 ID는 파일 세트 전체에서 유일해야 한다. 외부 파일로 나눠도 유일성 범위는 파일 세트 전체다.

- 형식은 네임스페이스 문자(요소 약어) + 십진수다. 예를 들면 `TSK1`, `CTR12`, `WKR-1`이다. 숫자는 선행 0(앞자리 0, 예: `TSK01`) 없이 최대 11자리이고 ID는 최소 4바이트다. 요소별 속성 정의는 ID 속성마다 `(TSK|TSK-)([0-9])+` 같은 형식과 4~14자 길이를 함께 적는다.
- 0과 −2147483648은 예약값이라 쓸 수 없다. 0은 버전 3에서 예약됐고, 그 전에는 FMIS가 만든 양수 ID처럼 해석됐다.
- MICS에서 새로 만든 엔티티는 음수를 쓴다(`WKR-1`). FMIS가 준 양수 ID와 섞이지 않게 하려는 규칙이고, 유일성은 만든 쪽이 책임진다.
- MICS는 coding data 요소를 바꾸거나 지울 수 없고 새 인스턴스를 추가만 할 수 있다. coding data 수정은 FMIS만 한다. coding data가 아닌 요소는 고칠 수 있다.
- IDREF 속성은 ID 하나만 담는다.
- 파일 이름 속성(GRD `G`, TLG `A`, XFR `A`, PNT `J`)은 `GRD00001`처럼 접두사 + 5자리 숫자이고 선행 0이 있다. 엔티티 ID와 형식이 다르지만 이 속성들도 `xs:ID` 타입이라 다른 ID와 겹치면 안 된다.

::: tip ID는 문자열로 다룬다
예약값 −2147483648이 int32(32비트 부호 있는 정수) 최솟값인 것으로 보아, 숫자 부분을 32비트 정수로 다루는 구현을 염두에 둔 규칙으로 보인다(추론). 하지만 표준이 허용하는 11자리 숫자(예: `TSK12345678901`)는 int32 범위를 넘는다. ID는 문자열 그대로 저장하고, 새 음수 ID를 만들 때만 숫자 부분을 계산하는 편이 안전하다(추론).
:::

<small>근거: ISO 11783-10 8.4, 8.5, D.27, D.38, D.46, D.49, D.55</small>

## 4. 요소 지도: 무엇이 어디에 들어가나

파일 세트의 요소 이름은 세 글자 약어다. 이 절은 실습에 나오는 요소를 지도처럼 펼쳐 놓는다. 먼저 약어의 원래 이름이다.

| 약어 | 원래 이름 | 약어 | 원래 이름 |
|---|---|---|---|
| TSK | Task(태스크) | CTR | Customer(고객) |
| TZN | TreatmentZone(처리 구역) | FRM | Farm(농장) |
| PDV | ProcessDataVariable(처리 값) | PFD | Partfield(필지) |
| GRD | Grid(격자) | PLN | Polygon(다각형) |
| DLT | DataLogTrigger(기록 조건) | LSG | LineString(선) |
| TLG | TimeLog(작업 기록 파일) | PNT | Point(점) |
| TIM | Time(시간 기록) | WKR | Worker(작업자) |
| PTN | Position(위치) | PDT | Product(제품) |
| DLV | DataLogValue(기록 값) | CPC | CulturalPractice(작업 종류) |
| DAN | DeviceAllocation(장치 할당) | OTP | OperTechPractice(작업 방법 참조) |
| ASP | AllocationStamp(할당 시각) | VPN | ValuePresentation(값 표시 방법) |
| DVC | Device(장치) | DET | DeviceElement(장치 요소) |

![루트 바로 아래의 CTR·FRM·PDT·VPN·WKR·CPC·PFD·DVC와 그 하위 요소, TSK 아래의 TZN·TIM·OTP·DAN·DLT·TLG·GRD와 PDV·PTN·DLV·ASP 계층, coding data 여부를 색으로 구분하고 주요 IDREF를 적은 그림](/images/study-isobus/22-isoxml-element-tree-light.png)
![루트 바로 아래의 CTR·FRM·PDT·VPN·WKR·CPC·PFD·DVC와 그 하위 요소, TSK 아래의 TZN·TIM·OTP·DAN·DLT·TLG·GRD와 PDV·PTN·DLV·ASP 계층, coding data 여부를 색으로 구분하고 주요 IDREF를 적은 그림](/images/study-isobus/22-isoxml-element-tree-dark.png)

그림의 왼쪽은 루트 바로 아래의 요소, 오른쪽은 TSK와 그 아래 요소다. 상자 색은 왼쪽 아래 범례대로 coding data와 그 밖의 데이터(task data)를 구분한다. 오른쪽 아래 주황색 글자는 어느 요소의 어느 속성이 어느 요소를 가리키는지(IDREF)를 적은 것이다.

루트 바로 아래에는 coding data 요소와 TSK가 함께 온다. PFD 안의 PLN·LSG·PNT는 coding data 요소 안에 들어 있지만 표준의 요소 분류에서 coding data가 아니다(그림에서 범례의 "그 밖" 색 상자). 그래서 필지 경계 점이 아무리 많아도 1.3절의 2,000개 한도에 들지 않는다. TSK 안의 요소는 IDREF로 coding data를 가리킨다.

| 요소 | 역할 | 이 실습에서 쓰는 속성 |
|---|---|---|
| TSK | 태스크. 파일 세트의 중심 요소 | `A` ID, `C`·`D`·`E` 고객·농장·필지, `F` 책임 작업자, `G` 상태, `H`·`I`·`J` 기본·측위 상실·필드 밖 TZN 코드 |
| TZN | 같은 DDI를 같은 값으로 처리할 구역 | `A` 코드(0~254, 태스크 안에서 유일), `B` 이름, `C` 색 |
| PDV | TZN 안의 DDI와 값 | `A` DDI(4자리 hex), `B` 값(int32), `C` 제품, `D` 장치 요소, `E` 표시 방법 |
| GRD | 격자 정의, 태스크당 최대 1개 | 57장 1절 |
| DLT | 무엇을 어떤 조건으로 기록할지 | `A` DDI, `B` 방법 비트, `D` 시간 간격(ms), `G` 변화 임계값, `H` 장치 요소 |
| TLG | 바이너리 로그 파일 참조 | 57장 2절 |
| TIM | 시간 기록. PTN·DLV를 담는다 | `A` 시작, `B` 끝, `C` 기간(초), `D` 유형 |
| ASP | 할당 이벤트의 시각 | `A` 시작, `B` 끝, `C` 기간, `D` 유형(1 planned, 4 effective) |
| DAN | 장치 할당 | `A` 클라이언트 NAME, `B` NAME 마스크, `C` DVC |
| PFD, PLN, LSG, PNT | 필지와 경계 기하 | PFD `C` 이름, `D` 면적(m²) / PLN `A` 1 = 필지 경계 / LSG `A` 1 = 외곽 경계 / PNT `C` 위도, `D` 경도 |
| CTR, FRM, WKR, PDT, CPC | 고객·농장·작업자·제품·작업 종류(coding data) | `A` ID, `B` 이름. FRM `I` → CTR |
| VPN | 정수값 표시 방법(coding data) | `B` Offset, `C` Scale, `D` 소수 자릿수, `E` 단위. 표시값 = (정수 + Offset) × Scale |

DDI(Data Dictionary Identifier)는 값의 종류와 단위를 정한 번호다([45장](/study/isobus/45-tc-process-data-basics)). XML에서는 4자리 16진수로 적는다(`0006` = 6, `0077` = 119).

TZN에는 특별한 쓰임이 셋 있다. TSK `H`가 가리키는 기본 TZN은 태스크 전체에 적용되고, TC가 태스크를 시작·재개할 때 그 안의 PDV 값을 해당하는 모든 클라이언트에 보낸다. `I`가 가리키는 측위 상실 TZN은 위치를 알 수 없게 됐을 때, `J`가 가리키는 필드 밖 TZN은 클라이언트(의 일부)가 필드 경계 폴리곤을 벗어났을 때 보낸다. 폴리곤으로 기하를 정한 TZN은 PDV를 하나만 담아야 하고(v4에서 목록이 하나로 바뀜), 기하가 없는 TZN(grid 템플릿이나 TSK 속성이 가리키는 것)은 PDV 목록을 가질 수 있다. 요소별 속성 전체는 [ISO 11783-10 부록](/study/isobus/appendix-iso-part10)에 정리돼 있다.

<small>근거: ISO 11783-10 8.5, D.2, D.17, D.20, D.27, D.32, D.33, D.37~D.39, D.41, D.46, D.48~D.51</small>

## 5. 태스크 상태와 시간 기록

태스크에는 "계획됨", "진행 중" 같은 상태가 있다. TSK의 `G` 속성이 그 상태이고, 값은 1~6이다. 5와 6은 v4에서 추가됐다. 상태가 바뀌는 흐름은 [42장](/study/isobus/42-tc-task)에서 다뤘다. 상태별 의미는 다음과 같다.

| G | 상태 | 의미와 규칙 |
|---|---|---|
| 1 | planned | FMIS나 MICS에서 준비됐지만 아직 MICS에서 처리하지 않았다 |
| 2 | running | MICS가 처리 중이다. TC 하나에서 동시에 하나만 활성일 수 있다 |
| 3 | paused | 실행했다가 멈췄고 아직 끝나지 않았다. TC 입장에서는 최종 상태일 수 있고, MICS가 보낸 파일의 paused 태스크는 FMIS가 처리해야 한다 |
| 4 | completed | 끝났다. 운전자만 설정할 수 있고 MICS가 자동으로 설정할 수 없다. 선택 기능이라 지원하지 않는 TC도 있다 |
| 5 | template | 시작하면 복사본이 새 태스크로 만들어져 시작된다. FMIS가 정의한 템플릿은 MICS가 수정하지 않는다 |
| 6 | canceled | 태스크를 철회한다. FMIS와 MICS가 서로에게 철회를 알리는 데 쓴다 |

상태가 바뀔 때는 시간 기록 규칙이 따라온다.

- TIM은 태스크 상태 변화, 자원 할당 변화(제품 할당 포함), TC 시작·종료 때만 추가하고, 이미 기록한 TIM은 고치지 않는다.
- MICS가 태스크를 시작했고 네트워크에 시간 정보가 있으면 TIM을 최소 1개 추가해야 한다.
- FMIS가 주는 TIM은 모두 type 1(planned)이고 태스크당 최대 1개다. MICS가 세부 유형(2, 5~8)을 구분하지 않으면 MICS가 쓰는 TIM은 모두 type 4(effective)다. 세부 유형의 뜻은 [42장](/study/isobus/42-tc-task)에서 다뤘다.
- v4부터 TIM·ASP 시각에 시간대를 붙일 수 있다. 시간대를 알면 `Z`(UTC)나 `+09:00` 같은 오프셋을 붙여야 하고, 모르면 표기 없이 로컬 시간으로 쓴다.

<small>근거: ISO 11783-10 6.1, 6.2, D.1, D.46, D.48, Annex G</small>

## 6. 실습 ①: FMIS가 보내는 TASKDATA.XML

::: info 실습 안내
- 목표: 55장 시뮬레이터의 처방을 FMIS가 보내는 `TASKDATA.XML`로 옮기고, 요소 하나하나의 뜻을 읽는다.
- 필요한 지식: 이 장 1~5절, [55장](/study/isobus/55-practice-log-vt-tc) 4절의 시뮬레이터, [45장](/study/isobus/45-tc-process-data-basics)(DDI)
- 준비물: 텍스트 편집기. 6.2절의 XML을 `fmis/TASKDATA.XML`로 저장해 둔다(7절 검사에 다시 쓴다).
:::

### 6.1 처방을 파일 요소로 옮기기

55장 4.2절 시뮬레이터의 처방을 그대로 파일로 옮긴다. 시뮬레이터의 각 동작이 파일 세트의 어느 요소가 되는지 먼저 짝을 지어 본다.

| 55장 시뮬레이터 | 파일 세트 |
|---|---|
| 2×2 격자, 셀마다 150·200·100·180 | GRD type 2 + 템플릿 TZN 1 + `GRD00001.BIN`(57장 1절) |
| 격자 밖이면 목표 0, 섹션 끔 | 필지 경계 PLN(격자와 같은 사각형) + TSK `J` → TZN 9(값 0) |
| 위치를 모를 때 | TSK `I` → TZN 0(기본값 150) |
| 시작·재개 때 보낼 기본값 | TSK `H` → TZN 0 |
| As-Applied 기록 | DLT 두 개. TLG는 TC가 만든다(57장 2절) |

단위는 하나 바꾼다. 55장은 L/ha로 적었지만, 이 실습은 DDI 6(Setpoint Mass Per Area Application Rate, 면적당 질량 살포량 설정값)을 쓴다. DDI 6을 고른 이유는 단위와 분해능이 표준 문서의 예제로 확정되기 때문이다. 표준 문서의 PDV 예제는 DDI 6 값 15000 mg/m²를 150 kg/ha로 적고, VPN `C="0.01"`로 kg/ha 표시를 한다. 1 kg/ha = 100 mg/m²이므로 150·200·100·180 kg/ha는 15000·20000·10000·18000이 된다. 액체를 L/ha로 처방하면 DDI 1을 쓰고 환산 계수만 달라진다. DDI 1의 단위·분해능은 ISO 11783-11이 가리키는 ISOBUS Data Dictionary에서 확인한다([DDI 부록](/study/isobus/appendix-ddi)). 표준은 비료 장치(Fertilizers)와 살포기(Sprayers)의 권장 살포량 DDI로 똑같이 1·2·6·7을 든다.

### 6.2 완성한 TASKDATA.XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ISO11783_TaskData VersionMajor="4" VersionMinor="0"
    ManagementSoftwareManufacturer="StudyFMIS" ManagementSoftwareVersion="1.0"
    DataTransferOrigin="1" lang="ko-KR">
  <CPC A="CPC1" B="fertilization"/>
  <CTR A="CTR1" B="Kim"/>
  <FRM A="FRM1" B="Study Farm" I="CTR1"/>
  <PFD A="PFD1" C="North Field" D="39256" E="CTR1" F="FRM1">
    <PLN A="1" B="Field boundary">
      <LSG A="1">
        <PNT A="2" C="37.500" D="127.000"/>
        <PNT A="2" C="37.500" D="127.002"/>
        <PNT A="2" C="37.502" D="127.002"/>
        <PNT A="2" C="37.502" D="127.000"/>
        <PNT A="2" C="37.500" D="127.000"/>
      </LSG>
    </PLN>
  </PFD>
  <PDT A="PDT1" B="Liquid Fertilizer"/>
  <TSK A="TSK1" B="VRA North Field" C="CTR1" D="FRM1" E="PFD1" F="WKR1"
       G="1" H="0" I="0" J="9">
    <TZN A="0" B="Default rate">
      <PDV A="0006" B="15000" C="PDT1" E="VPN1"/>
    </TZN>
    <TZN A="1" B="Grid template">
      <PDV A="0006" B="0" C="PDT1" E="VPN1"/>
    </TZN>
    <TZN A="9" B="Out of field">
      <PDV A="0006" B="0" C="PDT1" E="VPN1"/>
    </TZN>
    <OTP A="CPC1"/>
    <DLT A="0006" B="8" G="1"/>
    <DLT A="0007" B="9" D="10000" G="100"/>
    <GRD A="37.500" B="127.000" C="0.001" D="0.001" E="2" F="2"
         G="GRD00001" H="16" I="2" J="1"/>
  </TSK>
  <VPN A="VPN1" B="0" C="0.01" D="0" E="kg/ha"/>
  <WKR A="WKR1" B="Kim"/>
</ISO11783_TaskData>
```

### 6.3 읽는 요령

위에서부터 차례로 읽는다.

- 루트는 `DataTransferOrigin="1"`이고 TC 속성이 없다. coding data와 TSK가 루트 바로 아래에 있다.
- 자식 요소 순서는 표준의 속성 표에 나열된 순서를 따랐다. XSD는 자식 요소의 순서까지 정할 수 있으므로 순서 제약은 배포된 스키마로 검증한다.
- PFD `D="39256"`은 필지 면적(m²)이고 계산은 [57장](/study/isobus/57-practice-binary-files) 1.3절에서 한다. PLN `A="1"`은 필지 경계, LSG `A="1"`은 외곽 경계다. v4부터 외곽·내부 경계 LineString은 첫 점을 마지막에 한 번 더 적어 닫는다. 그래서 PNT가 다섯 개이고 첫 점과 마지막 점이 같다. 버전 2·3은 마지막 점에서 첫 점으로 선을 긋는 방식이었다.
- TSK의 `C`·`D`·`E`·`F`는 고객 CTR1, 농장 FRM1, 필지 PFD1, 작업자 WKR1을 가리키는 IDREF다. `G="1"`은 planned, `H="0"`·`I="0"`·`J="9"`는 기본, 측위 상실, 필드 밖에 쓸 TZN 코드다.
- TZN 1의 PDV `B="0"`은 자리만 채운 값이고 실제 값은 grid 바이너리에 있다. 표준 문서의 grid 예제는 같은 자리를 `B=""`로 비워 두지만, 속성 정의에서 `B`는 반드시 있어야 하는 정수(`xs:long`)다. 쓸 때는 0을 넣고, 읽을 때는 둘 다 받아들이는 편이 안전하다(추론).
- DLT `B`는 방법 비트 조합이다. 1 시간 간격, 2 거리 간격, 4 임계 범위, 8 변화 시, 16 total이다. `B="8" G="1"`은 설정값이 바뀔 때마다, `B="9" D="10000" G="100"`은 10초마다 또는 값이 100(= 1 kg/ha) 이상 바뀔 때 기록하라는 뜻이다. 9는 1(시간 간격)과 8(변화 시)을 더한 값이다. 시간·거리·변화 방법은 먼저 일어난 이벤트가 기록을 일으키고 셋 다 다시 시작한다. 시간 간격의 최솟값은 100 ms다.
- DLT에 `H`(장치 요소)가 없으면 TC는 그 DDI를 줄 수 있는 모든 장치 요소에서 기록한다. FMIS가 `H`를 채우면 특정 장치를 계획한 것이고, 비워 두면 MICS가 장치를 할당한 뒤 채울 수 있다. PDV `D`도 비웠다. TC는 일치하는 DDI를 setpoint로 받을 수 있는 연결된 클라이언트에 PDV를 할당할 수 있어야 한다.
- DDI 7은 실제 살포량(질량/면적)이다. 이름과 단위는 [DDI 부록](/study/isobus/appendix-ddi) 기준이다.

### 6.4 결과 확인

1. 저장한 파일이 XML 문법을 지키는지 본다. `python3 -c "import xml.etree.ElementTree as ET; ET.parse('fmis/TASKDATA.XML')"`가 아무 출력 없이 끝나면 well-formed다. 오류가 나면 메시지에 나온 줄 번호 근처의 태그 짝과 따옴표를 확인한다.
2. 아래 질문에 파일만 보고 답할 수 있으면 실습을 제대로 한 것이다.
   - 이 태스크의 고객 이름은? TSK `C="CTR1"`을 따라가면 CTR `B="Kim"`이다.
   - 위치를 모를 때 TC가 보낼 값은? TSK `I="0"` → TZN 0 → PDV `B="15000"` → 15000 mg/m² = 150 kg/ha다.
   - 필지 밖에서 보낼 값은? TSK `J="9"` → TZN 9 → 0이다.
   - 격자 칸마다의 값은 어디에 있나? GRD `G="GRD00001"`이 가리키는 `GRD00001.BIN`에 있다. 이 파일은 57장에서 만든다.

::: details 원문을 가진 독자를 위한 메모
- "DDI 6 값 15000 = 150 kg/ha" 예제는 D.41 예1이다. `B=""`로 비운 grid 템플릿 예제는 D.41 예4이고, 같은 절의 표가 `B`를 필수 `xs:long`으로 정한다.
- 권장 rate DDI 1·2·6·7은 F.2.2 Table F.2에 있다.
:::

<small>근거: ISO 11783-10 8.3, 8.6.2, D.17, D.33, D.41, F.2.2; ISO 11783-11 4.1</small>

## 7. 실습 ②: TC가 돌려주는 TASKDATA.XML

::: info 실습 안내
- 목표: 작업을 마친 TC가 고쳐서 돌려준 파일에서 무엇이 바뀌었는지 찾고, 검사 스크립트로 ID 규칙을 지켰는지 확인한다.
- 필요한 지식: 이 장 2~5절, [48장 DDOP 기초](/study/isobus/48-ddop-basics)(장치 기술)
- 준비물: 6절의 `fmis/TASKDATA.XML`, 아래 XML의 주석 자리를 FMIS 파일 내용으로 채워 저장할 `tc/TASKDATA.XML`, 파이썬 3
:::

### 7.1 돌려받은 파일

작업을 마친 TC는 같은 파일 세트를 고쳐 FMIS로 돌려준다. coding data는 그대로 두고, 새로 생긴 것을 더하고, TSK 안을 갱신한다. 바뀐 부분만 보인다.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ISO11783_TaskData VersionMajor="4" VersionMinor="0"
    ManagementSoftwareManufacturer="StudyFMIS" ManagementSoftwareVersion="1.0"
    TaskControllerManufacturer="StudyTC" TaskControllerVersion="1.0"
    DataTransferOrigin="2" lang="ko-KR">
  <CPC A="CPC1" B="fertilization"/>
  <CTR A="CTR1" B="Kim"/>
  <DVC A="DVC-1" B="Sprayer" C="1.0" D="A00C84000B20408B"
       F="30353035344042" G="FF000000006F6B">
    <DET A="DET-1" B="1" C="1" D="Sprayer" E="0" F="0">
      <DOR A="20"/>
    </DET>
    <DET A="DET-2" B="2" C="2" D="Rate control" E="1" F="1">
      <DOR A="21"/>
      <DOR A="22"/>
    </DET>
    <DPD A="20" B="0077" C="1" D="16" E="Effective Total Time"/>
    <DPD A="21" B="0006" C="2" D="8" E="Setpoint Rate" F="40"/>
    <DPD A="22" B="0007" C="1" D="9" E="Actual Rate" F="40"/>
    <DVP A="40" B="0" C="0.01" D="0" E="kg/ha"/>
  </DVC>
  <!-- FRM, PFD, PDT: FMIS 파일과 같다 -->
  <TSK A="TSK1" B="VRA North Field" C="CTR1" D="FRM1" E="PFD1" F="WKR1"
       G="4" H="0" I="0" J="9">
    <TZN A="0" B="Default rate">
      <PDV A="0006" B="15000" C="PDT1" D="DET-2" E="VPN1"/>
    </TZN>
    <TZN A="1" B="Grid template">
      <PDV A="0006" B="0" C="PDT1" D="DET-2" E="VPN1"/>
    </TZN>
    <TZN A="9" B="Out of field">
      <PDV A="0006" B="0" C="PDT1" D="DET-2" E="VPN1"/>
    </TZN>
    <TIM A="2026-04-13T09:30:00+09:00" B="2026-04-13T09:30:40+09:00" D="4"/>
    <OTP A="CPC1"/>
    <DAN A="A00C84000B20408B" C="DVC-1">
      <ASP A="2026-04-13T09:30:00+09:00" B="2026-04-13T09:30:40+09:00" D="4"/>
    </DAN>
    <DLT A="0006" B="8" G="1"/>
    <DLT A="0007" B="9" D="10000" G="100"/>
    <TLG A="TLG00001" C="1"/>
    <GRD A="37.500" B="127.000" C="0.001" D="0.001" E="2" F="2"
         G="GRD00001" H="16" I="2" J="1"/>
  </TSK>
  <TCC A="A00082000A20001B" B="Study TC" C="4" D="5" E="0" F="0" G="1"/>
  <!-- VPN, WKR: FMIS 파일과 같다 -->
</ISO11783_TaskData>
```

### 7.2 새로 나온 요소

6절 파일에 없던 요소가 여럿 생겼다.

- <strong>DVC(Device)</strong>: 작업에 쓴 작업기 하나. 작업기가 버스로 보낸 장치 기술(DDOP, 장치가 자기 구성을 TC에 알리는 데이터)을 XML로 옮긴 것이다. 안의 DET(DeviceElement)는 장치를 이루는 부분(장치 전체, 기능 등), DOR(DeviceObjectReference)은 그 부분에 딸린 값 정의를 가리키는 참조, DPD(DeviceProcessData)는 장치가 주고받는 값 하나, DVP(DeviceValuePresentation)는 그 값을 사람에게 보여 주는 방법(오프셋, 배율, 단위)이다.
- <strong>TIM</strong>: 실제로 일한 시간 기록이다. 09:30:00부터 09:30:40까지 40초 일했다.
- <strong>DAN과 ASP</strong>: 이 태스크에 실제로 쓴 장치(NAME과 DVC)와 그 할당 시각이다.
- <strong>TLG</strong>: 작업 기록 바이너리 파일을 가리킨다. 파일 내용은 [57장](/study/isobus/57-practice-binary-files) 2절에서 만든다.
- <strong>TCC</strong>: TC가 무엇을 할 수 있는지 적은 능력표다.

### 7.3 바뀐 곳 정리

| 바뀐 곳 | 내용 |
|---|---|
| 루트 | `DataTransferOrigin="2"`, TC 이름·버전 필수 |
| TCC | v4 MICS 출처 파일에 최대 1개. `D="5"` = 1(문서화) + 4(위치 기반 제어가 있는 TC-GEO), `E`·`F` = 0(섹션 제어 없음), `G="1"`(제어 채널 1개). NAME은 예시 값 |
| DVC-1, DET-1, DET-2 | TC가 버스로 받은 DDOP를 XML로 바꿔 저장했다. MICS에서 생긴 엔티티라 음수 ID다. coding data지만 새 인스턴스 추가는 허용된다. ClientNAME은 표준 문서의 DAN 예제 값 |
| TSK `G="4"` | 운전자가 완료 처리했다. completed는 MICS가 자동으로 설정할 수 없다 |
| TIM | type 4(effective), 시간대 `+09:00` 포함 |
| DAN | 실제로 쓴 클라이언트의 NAME + DVC 참조 + effective ASP. 표준 문서의 DAN 예제와 같은 모양 |
| PDV `D="DET-2"` | 실제 기계가 정해진 뒤 할당을 PDV에 기록할 수 있다 |
| TLG | `A="TLG00001"`, `C="1"`(binary timelog type 1). 선택 속성 `B`(파일 길이)는 생략 |

DDOP 쪽에서는 DET-1(device, element number 0)에 DDI 119(`0077`, Effective Total Time)를 달았다. TC-BAS 클라이언트는 최소 DDI 119를 제공해야 하고, rate DDI가 있으면 그에 대응하는 total도 제공해야 한다. 예제는 지면 때문에 rate total을 뺐다. DLT `B`도 DPD `D`가 밝힌 트리거 안에서 골랐다. DPD `D`는 그 DDI에 쓸 수 있는 트리거 방법이다. 실제 DDOP 설계는 [48장](/study/isobus/48-ddop-basics)과 [50장](/study/isobus/50-ddop-commands-design)에서 다룬다.

### 7.4 검사 스크립트로 결과 확인

두 파일이 3절의 ID 규칙과 coding data 규칙을 지켰는지 스크립트로 확인한다. 스크립트가 하는 일은 셋이다.

1. `check`: 엔티티 ID마다 형식(약어 + 선택적 `-` + 0으로 시작하지 않는 1~11자리 숫자)과 길이(4~14자), 중복 여부를 본다. 이어서 IDREF가 가리키는 ID가 실제로 있고 종류가 맞는지 본다.
2. `coding`: 루트 바로 아래 coding data 요소를 하나씩 문자열로 바꿔 집합으로 만든다.
3. FMIS 파일의 coding data 집합에서 TC 파일의 집합을 뺀 결과가 비어 있어야 한다. 비어 있지 않으면 TC가 FMIS의 coding data를 바꾸거나 지운 것이다.

::: details check_ids.py: ID·IDREF·coding data 규칙 검사 (실행 검증)
SIL(Software-in-the-Loop, 실제 장비 대신 소프트웨어로 시험하는 환경)에서 TC 서버 에뮬레이터가 내놓는 파일을 회귀 테스트할 때도 쓸 수 있다.

```python
"""Check ISOXML ID rules (ISO 11783-10 8.4, 8.5) between an FMIS file and the TC's returned file."""
import re
import sys
import xml.etree.ElementTree as ET

ID_ATTR = {"CTR": "A", "FRM": "A", "PFD": "A", "PDT": "A", "CPC": "A", "VPN": "A",
           "WKR": "A", "TSK": "A", "DVC": "A", "DET": "A"}
REFS = {"FRM": {"I": "CTR"}, "PFD": {"E": "CTR", "F": "FRM"},
        "TSK": {"C": "CTR", "D": "FRM", "E": "PFD", "F": "WKR"},
        "PDV": {"C": "PDT", "D": "DET", "E": "VPN"}, "OTP": {"A": "CPC"},
        "DAN": {"C": "DVC"}, "DLT": {"H": "DET"}, "DLV": {"C": "DET"}}
CODING = {"CPC", "CTR", "FRM", "PFD", "PDT", "VPN", "WKR", "DVC"}


def check(path):
    root = ET.parse(path).getroot()
    ids = {}
    for el in root.iter():
        if el.tag in ID_ATTR:
            v = el.get(ID_ATTR[el.tag])
            assert re.fullmatch(rf"{el.tag}-?[1-9][0-9]{{0,10}}", v), f"bad ID {v}"
            assert 4 <= len(v) <= 14 and v not in ids, f"length/duplicate {v}"
            ids[v] = el.tag
    for el in root.iter():
        for attr, target in REFS.get(el.tag, {}).items():
            v = el.get(attr)
            assert v is None or ids.get(v) == target, f"{el.tag} {attr}={v} -> no {target}"
    return root, ids


def coding(root):
    return {ET.tostring(c) for c in root if c.tag in CODING}


if __name__ == "__main__":
    fmis, _ = check(sys.argv[1])
    mics, ids = check(sys.argv[2])
    assert not coding(fmis) - coding(mics), "MICS changed or deleted FMIS coding data"
    print("added by MICS:", sorted(ET.fromstring(x).get("A") for x in coding(mics) - coding(fmis)))
    print("negative IDs:", sorted(i for i in ids if "-" in i))
    print("all checks passed")
```
:::

실행 순서는 다음과 같다.

1. 위 코드를 `check_ids.py`로 저장한다.
2. 7.1절 XML의 두 주석 자리(`FRM, PFD, PDT`와 `VPN, WKR`)를 6절 파일의 해당 요소로 채워 `tc/TASKDATA.XML`로 저장한다.
3. `python3 check_ids.py fmis/TASKDATA.XML tc/TASKDATA.XML`을 실행한다.

6절 파일과 7절 파일(주석 자리를 FMIS 파일 내용으로 채운 전체본)로 돌린 결과다. TC가 WKR1의 이름을 바꾼 파일을 넣으면 `AssertionError: MICS changed or deleted FMIS coding data`로 멈춘다.

```
added by MICS: ['DVC-1']
negative IDs: ['DET-1', 'DET-2', 'DVC-1']
all checks passed
```

첫 줄은 TC가 새로 더한 coding data가 DVC-1 하나라는 뜻이다. 둘째 줄은 MICS가 만든 엔티티 셋이 모두 음수 ID를 받았다는 뜻이다. 마지막 줄이 나오면 모든 검사를 통과한 것이다. 검사가 실패하면 `AssertionError` 뒤의 메시지(`bad ID ...`, `length/duplicate ...`, `PDV D=... -> no DET` 등)가 어느 규칙을 어겼는지 알려 준다.

::: details 원문을 가진 독자를 위한 메모
- ClientNAME `A00C84000B20408B`와 DAN의 모양은 D.20의 예제(예3)를 따랐다.
- TC-BAS 클라이언트의 DDI 119 요건은 F.2.1, DPD 트리거 속성은 D.23에 있다.
:::

<small>근거: ISO 11783-10 5.1, 6.1, 8.1, 8.4, 8.5, A.1, D.20, D.23, D.32, D.41, D.47~D.49, F.2.1</small>

## 8. 더 알아보기: 외부 파일과 DVC 변환 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 핵심 정리로 가도 된다.
:::

### 8.1 외부 파일 XFR과 XFC

메인 파일이 커지면 최상위 요소를 다른 XML 파일로 뺄 수 있다. 메인 파일에는 XFR(ExternalFileReference, 외부 파일 참조)을 두고, 빼낸 파일의 루트는 XFC(ExternalFileContents, 외부 파일 내용)로 쓴다.

- 메인 파일 `TASKDATA.XML`만 XFR을 가질 수 있다. 참조는 중첩되지 않는다. XFR도, XFC도 재귀로 쓸 수 없다.
- 외부 파일의 루트는 XFC다. 외부 파일도 XML 선언으로 시작하는 well-formed 파일이어야 한다.
- 외부 파일 하나에는 한 종류의 최상위 요소만 넣는다. 고객 파일에 필지를 섞을 수 없다. 같은 종류의 최상위 요소가 메인 파일과 외부 파일 양쪽에 있는 것은 괜찮다.
- XFR `A`는 `(CCG|CCT|CLD|CPC|CTP|CTR|DVC|FRM|OTQ|PDT|PFD|PGP|TSK|VPN|WKR)[0-9]{5}` 형식의 8자이고 확장자를 넣지 않는다. `B`는 1(XML)뿐이다.
- TC와 FMIS는 단일 파일과 파일 세트를 모두 받을 준비가 돼 있어야 하고, 둘 다 바이너리 파일을 참조할 수 있다.

`TASKDATA.XML` 쪽:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ISO11783_TaskData VersionMajor="4" VersionMinor="0" DataTransferOrigin="1">
  <CTR A="CTR1" B="Kim"/>
  <XFR A="TSK00002" B="1"/>
</ISO11783_TaskData>
```

`TSK00002.XML` 쪽:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<XFC>
  <TSK A="TSK2" G="1"/>
</XFC>
```

메인 파일의 XFR `A="TSK00002"`에 확장자 `.XML`을 붙인 이름의 파일을 같은 디렉터리에서 찾는다. 그 파일의 XFC 안에 TSK가 들어 있으므로 받는 쪽은 TSK2를 메인 파일에 있던 것처럼 다룬다.

### 8.2 XML 장치 기술(DVC)과 DDOP의 대응

7절의 DVC는 클라이언트가 버스로 보낸 DDOP를 옮긴 것이다. DDOP의 바이너리 객체는 XML 요소를 객체로 정의한 것이어서 둘은 거의 1:1로 대응한다. 객체별 바이트 배치는 [49장 DDOP 바이트 구성](/study/isobus/49-ddop-bytes)에서 다루고, 여기서는 XML로 옮길 때의 대응만 정리한다.

| XML | DDOP 객체·필드 | 옮길 때의 규칙 |
|---|---|---|
| DVC | DeviceObject, Table ID `DVC`, Object ID 0 고정 | 풀마다 정확히 1개 |
| DVC `A` (`DVC-1`) | 없음 | 파일 세트용 ID. TC가 변환할 때 만든다 |
| DVC `B`, `C`, `E` | designator, software version, serial number | UTF-8, BOM 없음. 바이트 수(N) + 문자열 |
| DVC `D` | ClientNAME 8바이트 | CF의 주소 클레임 NAME과 같아야 한다 |
| DVC `F` | structure label 7바이트 + extended structure label 0~32바이트(v4) | XML hexBinary는 배열 바이트 1이 문자열 끝이다 |
| DVC `G` | localization label 7바이트 | 바이트 1~6은 language command 정의, 바이트 7은 FF |
| DET | DeviceElementObject, Table ID `DET` | |
| DET `A` (`DET-2`) | 없음 | PDV `D`, DLV `C`, DLT `H`, CNN이 이 ID로 참조한다 |
| DET `B` | Object ID(1~65534) | 풀 안에서 유일 |
| DET `C` | DeviceElementType(1 device, 2 function, 3 bin, 4 section, 5 unit, 6 connector, 7 navigation) | device 타입은 풀에 하나, element number 0 |
| DET `E` | DeviceElementNumber(0~4095) | 프로세스 데이터 메시지에 실리는 element number |
| DET `F` | Parent ObjectId | 0이면 DeviceObject를 가리킨다 |
| DET 안의 DOR `A` | Number of objects to follow + ObjectId 목록 | XML은 자식 요소, 바이너리는 개수 + 2바이트 ID 나열 |
| DPD `A`~`F` | Object ID, DDI 2바이트, properties 비트, trigger 비트, designator, DVP Object ID | 참조가 없으면 바이너리는 NULL Object ID 65535(FFFF₁₆), XML은 `F`를 생략 |
| DPT `A`~`E` | Object ID, DDI, value(int32), designator, DVP Object ID | |
| DVP `A`~`E` | Object ID, offset(int32), scale(4바이트 float), decimals, unit designator | XML의 scale은 `xs:decimal` |

표에서 CF(Control Function)는 버스에 주소를 가진 기능 단위이고, BOM은 UTF-8 파일 맨 앞에 붙기도 하는 표시 바이트다. 옮길 때 챙길 곳은 다섯 군데다.

- <strong>ID가 두 벌이다.</strong> DET `B`·DPD `A`·DOR `A`는 클라이언트가 정한 DDOP 객체 ID로, 한 풀 안에서만 유일하다. DVC·DET의 `A`는 파일 세트 전체에서 유일한 XML ID다. 7절의 DOR `A="21"`은 객체 ID를, PDV `D="DET-2"`는 XML ID를 가리킨다.
- <strong>버스에는 element number가 실린다.</strong> TC가 받은 측정값에는 element number와 DDI가 있고, DLV는 DET의 XML ID를 요구한다. 따라서 TC는 (클라이언트, element number)로 그 클라이언트 DVC 안의 DET를 찾아 `DET-2`를 채워야 한다. 메시지 바이트는 [45장](/study/isobus/45-tc-process-data-basics)에 있다.
- <strong>라벨 바이트 순서가 반대다.</strong> XML `F="30353035344042"`는 버스에서 `42 40 34 35 30 35 30` 순으로 나간다. `G="FF000000006F6B"`는 버스 순서로 `6B 6F 00 00 00 00 FF`이고, 첫 두 바이트가 언어 코드 `ko`다(표준 문서의 DVC 예제와 같은 규칙).
- <strong>문자열 길이 단위가 다르다.</strong> XML designator는 최대 32자이고, 바이너리는 UTF-8 문자당 최대 4바이트라 바이트 길이를 최대 128까지 쓴다. 이 상한은 v4에서 32에서 128로 늘었다.
- <strong>같은 장치가 이미 있으면</strong> TC는 structure label을 비교해 기존 정의를 갱신하거나 새 DVC로 저장한다. 어느 쪽인지는 MICS 재량이다.

아래는 라벨 바이트 순서를 파이썬 대화형 셸에서 확인한 것이다. `[::-1]`은 바이트 순서를 뒤집는다.

```python
>>> bytes.fromhex("30353035344042")[::-1].hex(" ").upper()
'42 40 34 35 30 35 30'
>>> bytes.fromhex("FF000000006F6B")[::-1][:2].decode()
'ko'
```

::: details 원문을 가진 독자를 위한 메모
- ISO 11783-10:2015의 Figure 9는 외부 파일을 `TSK00001.xml`처럼 소문자 확장자로 적는다. 파일 이름을 모두 대문자로 쓰라는 8.5의 규칙과 다르다.
- 라벨 바이트 역순 규칙의 예제는 D.19 예1이다.
:::

<small>근거: ISO 11783-10 8.5, A.1~A.3, D.18, D.19, D.54, D.55, Annex B</small>

::: tip 핵심 정리
- 파일 세트는 `TASKDATA` 디렉터리의 대문자 고정 이름 파일들이고, 루트는 `ISO11783_TaskData` 하나다.
- ID는 접두사 + 선행 0 없는 숫자이고, MICS가 만든 엔티티는 음수다. MICS는 coding data를 추가만 한다.
- FMIS가 보내는 파일은 출처 1, 상태 planned인 TSK와 처방 TZN·PDV·GRD·DLT를 담는다.
- TC가 돌려주는 파일은 출처 2, TC 속성·TCC, 음수 ID의 DVC, effective TIM·DAN, TLG가 더해진 같은 파일 세트다.
- DVC를 XML로 옮길 때는 ID 두 벌(DDOP 객체 ID와 XML ID), element number, 라벨 바이트 역순을 챙긴다.
:::

::: details 확인 문제
1. (개념) `DataTransferOrigin`이 1인 파일과 2인 파일은 각각 누가 만들었나? `TaskControllerManufacturer`는 어느 쪽 파일에서 필수인가?
2. (개념) TC가 작업 중에 새 작업자 요소를 만들었다. ID로 알맞은 것은? `WKR0`, `WKR01`, `WKR-2`, `WKR2`
3. (개념) MICS가 태스크 상태를 completed(4)로 자동으로 바꿀 수 있나?
4. (읽기) 6절 파일에서 GPS 위치를 잃었을 때 TC가 보내는 살포량 설정값은 얼마인가? 어느 속성을 따라가면 알 수 있나?
5. (검사) TC가 돌려준 파일에서 FMIS가 준 `<WKR A="WKR1" B="Kim"/>`의 이름을 `Lee`로 바꿨다. check_ids.py는 어떻게 반응하고, 어느 규칙을 어긴 것인가?
6. (심화) DVC `F="30353035344042"`는 버스에서 어떤 바이트 순서로 나가나?

**답 가이드**
1. 1은 FMIS가, 2는 MICS(TC 쪽)가 마지막으로 만든 파일이다. `TaskControllerManufacturer`와 `TaskControllerVersion`은 MICS가 만든 파일에서 필수다.
2. `WKR-2`. MICS가 만든 엔티티는 음수 ID를 쓴다. `WKR0`은 0이 예약값이라 안 되고, `WKR01`은 선행 0이 있어 형식에 어긋나며, `WKR2`는 FMIS가 쓰는 양수 ID라서 MICS가 새로 만들 때는 쓰지 않는다.
3. 없다. completed는 운전자만 설정할 수 있다.
4. TSK `I="0"` → TZN `A="0"` → PDV `A="0006" B="15000"`을 따라가면 15000 mg/m², 곧 150 kg/ha다.
5. `AssertionError: MICS changed or deleted FMIS coding data`로 멈춘다. MICS는 coding data를 바꾸거나 지울 수 없고 새 인스턴스를 추가만 할 수 있다는 규칙을 어겼다.
6. 바이트 순서를 뒤집어 `42 40 34 35 30 35 30` 순으로 나간다.
:::

## 다음 챕터

- 다음: [57장 종합 실습 (3): grid, TimeLog, Point 바이너리](/study/isobus/57-practice-binary-files)
