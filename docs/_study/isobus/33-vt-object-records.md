---
title: "오브젝트 레코드: 공통 구조와 자주 쓰는 오브젝트"
description: "모든 VT 오브젝트 레코드가 공유하는 뼈대를 익히고, 자주 쓰는 오브젝트 레코드를 바이트 단위로 읽으며 이벤트와 바꿀 수 있는 속성을 짚는다."
date: 2026-04-13
tags: [ISOBUS, VT, Object Pool, AID, Macro, ISO-11783-6]
prev: /study/isobus/32-vt-object-pool-basics
next: /study/isobus/34-vt-layout-color
---

# 오브젝트 레코드: 공통 구조와 자주 쓰는 오브젝트

::: info 학습 목표
- 모든 오브젝트 레코드가 공유하는 뼈대(머리, 고정 속성, 목록 개수, 목록)를 설명할 수 있다.
- 레코드에 길이 필드가 없는데도 다음 레코드가 어디서 시작하는지 계산할 수 있다.
- AID(속성 번호)의 대괄호 표시를 보고, Change Attribute로 바꿀 수 있는 속성과 전용 명령이 필요한 속성을 구분할 수 있다.
- Container, Key, Button, Input Number, Input List, Macro, Alarm Mask 같은 자주 쓰는 오브젝트의 레코드를 바이트 단위로 읽을 수 있다.
- 오브젝트마다 일어나는 이벤트와 거기에 매크로를 거는 방법을 설명할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [32장 VT 오브젝트 풀 기초](/study/isobus/32-vt-object-pool-basics)
- 이 장에서 처음 나오는 말
  - 고정 속성: 오브젝트 타입마다 자리와 크기가 정해진 속성.
  - AID(Attribute ID): 속성마다 붙은 번호. 명령으로 속성을 바꾸거나 읽을 때 이 번호로 가리킨다.
  - 가변 목록: 자식 목록이나 매크로 목록처럼 길이가 레코드마다 다른 부분.
  - 이벤트(event): 오브젝트에 생기는 일. 화면에 나타남, 값이 바뀜, 키가 눌림 같은 것이다.
  - 매크로(macro): 이벤트가 일어나면 VT가 스스로 실행하는 명령 묶음. Macro 오브젝트에 담는다.
:::

관공서 서류를 떠올려 보자. 어떤 서류든 맨 위에는 문서 번호와 문서 종류가 있고, 그 아래 칸은 문서 종류마다 정해져 있다. 칸의 순서를 알면 처음 보는 서류도 읽을 수 있다. VT(Virtual Terminal, 운전석의 공용 화면 단말) 오브젝트 레코드도 같다. 맨 앞 3바이트(Object ID와 타입)는 모든 레코드가 같고, 그 뒤 칸은 타입마다 정해져 있다.

비유가 맞지 않는 지점이 하나 있다. 서류에는 "전체 몇 쪽"이 적혀 있지만, 레코드에는 전체 길이가 적혀 있지 않다. 그래서 칸 순서를 정확히 알아야만 다음 레코드를 찾을 수 있다. 이 장에서는 모든 레코드에 공통인 뼈대를 먼저 익히고, 32장의 화면에 "살포 목표량 설정" 기능을 붙이며 자주 쓰는 레코드를 하나씩 바이트로 읽는다.

## 1. 레코드의 머리와 고정 속성

이 절에서는 모든 레코드의 앞부분, 곧 머리(Object ID와 Type)와 고정 속성을 본다. 이 부분을 알면 레코드 하나가 어디서 시작하고 어떤 규칙으로 읽히는지 안다.

[32장](/study/isobus/32-vt-object-pool-basics)에서 세 오브젝트를 바이트로 펼쳤다. VT 표준(ISO 11783-6)에는 이런 레코드 형식 표가 오브젝트마다 하나씩, 40개 넘게 있다. 표를 하나씩 외우기 전에 모든 레코드가 공유하는 뼈대를 잡아 두면 처음 보는 오브젝트도 같은 순서로 읽힌다.

![오브젝트 레코드 공통 구조: Object ID 2바이트와 Type 1바이트로 된 머리, AID가 붙은 고정 속성, 목록 개수 바이트 2개, 6바이트(Object ID·X·Y) 자식 항목, 2바이트 8비트 매크로 참조 또는 4바이트 16비트 매크로 참조(v5+), 위치 없는 2바이트 참조 목록](/images/study-isobus/16-record-anatomy-light.png)
![오브젝트 레코드 공통 구조: Object ID 2바이트와 Type 1바이트로 된 머리, AID가 붙은 고정 속성, 목록 개수 바이트 2개, 6바이트(Object ID·X·Y) 자식 항목, 2바이트 8비트 매크로 참조 또는 4바이트 16비트 매크로 참조(v5+), 위치 없는 2바이트 참조 목록](/images/study-isobus/16-record-anatomy-dark.png)

그림의 윗줄이 레코드 하나를 왼쪽부터 오른쪽으로 펼친 모습이다. 머리 3바이트, 타입마다 정해진 고정 속성, 목록 개수 바이트 2개, 자식 목록, 매크로 목록 순이다. 아랫줄은 목록 항목 하나를 확대한 것이다. 목록의 모양은 2절에서 자세히 본다.

### 머리: Object ID와 Type

- <strong>Object ID</strong>(2바이트)는 0~65534다. 65535(`FF FF`)는 NULL Object ID다. 풀 안에서 유일해야 한다.
- <strong>Type</strong>(1바이트)은 [32장 타입 표](/study/isobus/32-vt-object-pool-basics)의 타입 번호다. 0~48이 표준 오브젝트, 240~254가 제조사 정의 오브젝트이고 49~239와 255는 예약이다.
- 1바이트보다 큰 값은 모두 리틀엔디언으로 보낸다. 낮은 자리 바이트가 먼저 온다.
- 레코드에는 <strong>전체 길이 필드가 없다</strong>. 파서는 Type을 보고 그 타입의 표대로 필드를 읽어야 다음 레코드가 어디서 시작하는지 안다. 기능을 지원하지 않는 오브젝트도 VT가 반드시 파싱해야 한다는 규칙은 이 구조와 맞물린다. 한 레코드라도 못 읽으면 그 뒤 레코드 전체의 경계를 잃는다. 표준이 이 연결을 직접 적지는 않지만, Working Set Special Controls(타입 47)에 "Number of bytes to follow"를 둔 이유를 "모르는 확장 속성을 건너뛰고 다음 오브젝트를 찾게 하려는 것"이라고 밝힌 데서 같은 문제의식을 읽을 수 있다.

파서(parser)는 바이트를 규칙대로 읽어 의미를 꺼내는 프로그램이다. 아래 그림은 이 장 예제 풀의 앞부분을 파서가 읽어 나가는 모습이다.

![레코드 경계 찾기: 풀의 바이트가 Container 20(22바이트), Soft Key Mask 40(10바이트), Key 41(15바이트), Button 50(19바이트) 순으로 이어진다. 파서는 각 레코드의 세 번째 바이트(Type)를 읽고 그 타입의 길이 식에 목록 개수를 넣어 길이를 구한 뒤, 그만큼 건너뛰어 다음 레코드의 시작(오프셋 22, 32, 47, 66)을 찾는다. 규칙을 모르는 Type을 만나면 길이를 셀 수 없어 그 뒤 경계를 모두 잃는다](/images/study-isobus/33-record-boundaries-light.png)
![레코드 경계 찾기: 풀의 바이트가 Container 20(22바이트), Soft Key Mask 40(10바이트), Key 41(15바이트), Button 50(19바이트) 순으로 이어진다. 파서는 각 레코드의 세 번째 바이트(Type)를 읽고 그 타입의 길이 식에 목록 개수를 넣어 길이를 구한 뒤, 그만큼 건너뛰어 다음 레코드의 시작(오프셋 22, 32, 47, 66)을 찾는다. 규칙을 모르는 Type을 만나면 길이를 셀 수 없어 그 뒤 경계를 모두 잃는다](/images/study-isobus/33-record-boundaries-dark.png)

1. 오프셋 0에서 세 번째 바이트를 읽으니 Type 3(Container)이다. Container 규칙대로 자식 수 2, 매크로 수 0을 읽어 길이 22바이트를 얻는다.
2. 22바이트를 건너뛴 오프셋 22에서 Type 4(Soft Key Mask)를 읽고, 같은 방법으로 길이 10바이트를 얻는다.
3. 이렇게 "Type 읽기, 길이 계산, 건너뛰기"를 되풀이한다.
4. 규칙을 모르는 Type을 만나면 그 레코드의 길이를 알 수 없다. 그 뒤 레코드는 어디서 시작하는지 모르게 된다.

### 고정 속성과 AID

화면이 뜬 뒤에 작업기가 "오브젝트 50의 3번 속성을 이 값으로 바꿔라"처럼 명령하려면 속성마다 번호가 있어야 한다. 그 번호가 AID다.

- <strong>AID</strong>(Attribute ID)는 속성 번호다. 1바이트이고 255는 NULL AID다. AID 0은 언제나 Type이다.
- VT 표준의 레코드 정의 표에서 AID가 `[n]`처럼 대괄호로 싸여 있으면 읽기 전용이라 Get Attribute Value(속성 값을 묻는 명령)로만 읽는다. 대괄호가 없으면 Change Attribute(속성 값을 바꾸는 명령)로 바꿀 수 있다. 이 장의 표도 같은 표기를 쓴다.
- AID가 아예 없는 필드(목록 개수, Length, 문자열 Value, 비트맵 데이터)는 Change Attribute로 바꿀 수 없다. 문자열은 Change String Value, 목록 항목은 Change List Item 같은 전용 명령을 쓰거나 레코드를 다시 보낸다([35장](/study/isobus/35-vt-pool-transfer-charset)). Change Attribute는 문자열에 쓸 수 없다.
- <strong>AID 번호와 바이트 순서는 다르다</strong>. Output Number의 Value는 AID `[12]`인데 바이트로는 Offset(AID 7)보다 앞인 Byte 14~17에 있다. AID를 레코드 오프셋으로 착각하면 엉뚱한 바이트를 고친다.
- 버전에 따라 늘어난 AID도 있다. Button의 Options(AID 6)는 v4부터 있다. v4는 VT 버전 4를 뜻한다.

명령의 바이트 배치는 [37장](/study/isobus/37-vt-command-details)에서 다룬다. 정리하면, 머리 3바이트가 "누구이고 무엇인지"를 알려 주고, 그 뒤 고정 속성은 타입이 정한 순서대로 놓이며, 바꿀 수 있는 속성에만 대괄호 없는 AID가 붙는다.

<small>근거: ISO 11783-6 3.3, 3.4, 4.6.28, A.1.1, A.1.2, Table A.1, B.7, B.9.3, B.29, C.2.1, F.38</small>

## 2. 가변 목록과 레코드 길이

고정 속성 뒤에는 개수가 레코드마다 다른 목록이 붙는다. 이 절에서는 목록의 세 가지 모양과, 목록 때문에 레코드 길이가 어떻게 달라지는지 본다.

### 가변 목록 세 가지

| 목록 | 항목 크기 | 쓰는 오브젝트 |
|---|---|---|
| 위치 있는 자식 목록 | 6바이트: Object ID + X(signed) + Y(signed) | Working Set, Data Mask, Alarm Mask, Container, Key, Button, Window Mask(free form) |
| 위치 없는 참조 목록 | 2바이트: Object ID | Soft Key Mask(나열 순서가 곧 키 배치), Input List·Output List(목록 항목), Key Group, Window Mask(type 1 이상의 필수 참조) |
| 매크로 목록 | 2바이트: Event ID + Macro ID | 마스크·키·입출력 필드·Attribute 오브젝트·Picture Graphic 등 대부분 |

- 위치 있는 자식 목록: 자식 하나마다 Object ID와 X, Y 좌표를 적는다. 좌표는 부모 왼쪽 위 모서리 기준이고, signed(부호 있는 수)라 음수도 된다.
- 위치 없는 참조 목록: Object ID만 늘어놓는다. 위치는 나열 순서나 VT가 정한다.
- 매크로 목록: "어떤 이벤트(Event ID)가 일어나면 어떤 매크로(Macro ID)를 실행할지"를 쌍으로 적는다. 이벤트 번호와 이름의 대응은 [38장](/study/isobus/38-vt-macro-input)에서 다룬다.

매크로 참조에는 두 형식이 있다.

- <strong>8비트 참조</strong>: `Event ID, Macro ID`. v4 이하 VT에서 Macro Object ID는 0~255뿐이다.
- <strong>16비트 참조</strong>(v5+): `FF, Macro ID 하위, Event ID, Macro ID 상위`. 2바이트 그룹 두 개를 이어 쓴다. Event ID 255는 이벤트가 아니라 "Use Extended Macro Reference" 표지다. 이 4바이트는 "Number of macros to follow"에서 <strong>2개로 센다</strong>.

16비트 참조의 예를 하나 들면, On Show(이벤트 3)에 Macro 7000(0x1B58)을 거는 참조는 `FF 58 03 1B`다. `FF`가 "16비트 참조"라는 표지, `58`이 7000의 낮은 바이트, `03`이 이벤트, `1B`가 7000의 높은 바이트다. 이 바이트는 7절의 Alarm Mask 레코드에 그대로 나온다.

배치 순서와 위치에도 함정이 있다.

- 자식(또는 참조) 목록을 모두 나열한 뒤 매크로를 나열한다. Working Set은 그 뒤에 언어 코드(2바이트씩)가 더 이어진다.
- 개수 바이트 두 개(objects, macros)는 보통 고정 속성 끝에 나란히 있다. 예외가 둘이다. Output String은 가변 길이 Value <strong>뒤에</strong> 매크로 개수가 온다. [32장](/study/isobus/32-vt-object-pool-basics) Output String 표의 맨 끝 바이트(오프셋 30)가 이것이다. Picture Graphic은 매크로 개수가 Byte 17에 고정돼 있지만 매크로 쌍은 비트맵 데이터 뒤에 온다.
- 매크로 목록이 아예 없는 오브젝트도 있다. Number Variable, String Variable, Object Pointer, Macro, Colour Map, Colour Palette, Working Set Special Controls다. 이들의 이벤트에는 매크로를 걸 수 없다.

정리하면, 목록은 "위치 있는 자식(6바이트)", "위치 없는 참조(2바이트)", "매크로(2바이트, 16비트 참조는 4바이트)" 세 가지이고, 레코드 길이는 고정 부분에 목록 항목 크기를 항목 수만큼 더한 값이다.

### 자주 쓰는 레코드의 길이 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

VT 표준의 레코드 정의에서 유도한 식이다. n은 자식·항목 수, m은 매크로 개수 바이트 값, L은 문자열 바이트 수, D는 비트맵 데이터 바이트 수, r은 참조 수다.

| 오브젝트(Type) | 길이(바이트) | 오브젝트(Type) | 길이(바이트) |
|---|---|---|---|
| Working Set(0) | 10 + 6n + 2m + 2·언어 수 | Output String(11) | 16 + L + 1 + 2m |
| Data Mask(1) | 8 + 6n + 2m | Output Number(12) | 29 + 2m |
| Alarm Mask(2) | 10 + 6n + 2m | Picture Graphic(20) | 17 + D + 2m |
| Container(3) | 10 + 6n + 2m | Number Variable(21) | 7 |
| Soft Key Mask(4) | 6 + 2n + 2m | String Variable(22) | 5 + L |
| Key(5) | 7 + 6n + 2m | Font·Line·Fill Attributes(23~25) | 8 + 2m |
| Button(6) | 13 + 6n + 2m | Object Pointer(27) | 5 |
| Input Number(9) | 38 + 2m | Macro(28) | 5 + 명령 바이트 수 |
| Input List(10) | 13 + 2n + 2m | Colour Map(39) | 5 + 2·16·256 중 하나 |
| Window Mask(34) | 17 + 2r + 6n + 2m | Colour Palette(45) | 6 + 4·색 수 |
| Key Group(35) | 10 + 2n + 2m | Working Set Special Controls(47) | 5 + Number of bytes to follow |

식에 값을 넣어 보면 32장 예제와 맞는다. 32장의 Output String은 L = 14, m = 0이라 16 + 14 + 1 + 0 = 31바이트이고, Data Mask는 n = 2, m = 0이라 8 + 12 + 0 = 20바이트다. 이 장 4절의 Container 20은 n = 2, m = 0이라 10 + 12 + 0 = 22바이트다.

<small>근거: ISO 11783-6 4.6.11.4, 4.6.22.3, Table A.3, Annex B(B.1, B.9.2, B.12.1, B.13, B.15~B.17, B.26, B.29)</small>

## 3. 예제 풀과 표 읽는 법

공통 뼈대를 실제 레코드에 적용해 본다. 이 절에서는 4~7절에서 쓸 예제 풀과 바이트 표 읽는 법을 정한다.

[32장](/study/isobus/32-vt-object-pool-basics) 5절 화면에 "살포 목표량 설정" 기능을 붙인다고 가정하고 자주 쓰는 오브젝트 레코드를 바이트로 만든다. 살포는 비료나 농약을 밭에 뿌리는 일이고, 목표량은 일정 면적에 뿌릴 양이다. 오브젝트끼리는 아래 ID로 서로 참조한다. 레코드에 등장하는 Output String(24, 25, 43, 51, 71)은 풀 어딘가에 있다고 보고 생략한다. 표의 Byte 번호는 1부터 센다(32장 표의 오프셋은 0부터였다).

| ID | 오브젝트 | ID | 오브젝트 |
|---|---|---|---|
| 20 | Container(설정 묶음) | 31, 32 | Line·Fill Attributes |
| 21 | Input Number(목표량) | 40, 41 | Soft Key Mask, Key("설정") |
| 22 | Input List(살포 모드) | 50 | Button |
| 23 | Number Variable(목표량 원시값) | 60 | Macro |
| 26 | Object Pointer | 70 | Alarm Mask |
| 80 | Picture Graphic | 100, 120 | Window Mask, Key Group([34장](/study/isobus/34-vt-layout-color)) |

각 오브젝트마다 <strong>이벤트</strong>와 <strong>Change Attribute로 바꿀 수 있는 AID</strong>를 함께 적는다. 이벤트 이름과 Event ID의 대응, 매크로 실행 규칙은 [38장](/study/isobus/38-vt-macro-input)에서 다룬다.

바이트 표는 이렇게 읽는다.

- <strong>Byte</strong>: 레코드 첫 바이트를 1로 놓고 센 위치다. "4~7"처럼 범위면 여러 바이트를 한 칸에 묶은 것이다. 32장의 오프셋 0이 여기서는 Byte 1이다.
- <strong>hex</strong>: 그 칸의 실제 바이트(16진수)다. 2바이트 이상인 값은 리틀 엔디언이라 거꾸로 붙여 읽는다. `C8 00`은 0x00C8 = 200이다.
- <strong>필드</strong>: 속성 이름이다. 괄호 안 숫자가 AID이고, `[1]`처럼 대괄호면 읽기 전용이다. 숫자가 없는 칸은 AID가 없는 필드다(Type의 AID는 언제나 0이라 따로 적지 않았다).
- <strong>값</strong>: 바이트를 읽은 결과다.

표 아래 목록의 "이벤트"는 그 오브젝트에 일어날 수 있는 일이고, "AID"는 Change Attribute로 바꿀 수 있는 속성이다. 이벤트 이름은 대부분 "On + 일어나는 일" 꼴이다. 예를 들어 On Show는 화면에 나타날 때, On Change Size는 크기 바꾸기 명령을 받았을 때다.

<small>근거: ISO 11783-6 Annex B</small>

## 4. 묶음과 키: Container, Soft Key Mask, Key, Button

화면 속 부품을 묶는 Container와, 운전자가 누르는 Key·Button부터 본다. 첫 레코드인 Container는 바이트를 하나씩 따라 읽는다.

### Container(Type 3): 22바이트

Container는 여러 오브젝트를 한꺼번에 보이거나 숨기려고 묶는 보이지 않는 상자다. 여기서는 목표량 입력칸(Input Number 21)과 살포 모드 목록(Input List 22)을 한 묶음으로 만든다.

| Byte | hex | 필드 | 값 |
|---|---|---|---|
| 1~3 | `14 00 03` | Object ID, Type | 20, Container |
| 4~7 | `C8 00 3C 00` | Width `[1]`, Height `[2]` | 200 × 60 |
| 8 | `00` | Hidden `[3]` | 0 = 보임 |
| 9~10 | `02 00` | 자식 수, 매크로 수 | 2, 0 |
| 11~16 | `15 00 0A 00 05 00` | 자식 1 | Input Number 21 @ (10, 5) |
| 17~22 | `16 00 6E 00 05 00` | 자식 2 | Input List 22 @ (110, 5) |

앞에서부터 따라 읽는다.

1. `14 00`: Object ID 0x0014 = 20이다.
2. `03`: Type 3, Container다. 이제부터 Container 규칙으로 읽는다.
3. `C8 00` `3C 00`: 폭 0x00C8 = 200픽셀, 높이 0x003C = 60픽셀이다.
4. `00`: Hidden 0, 곧 보이는 상태다.
5. `02` `00`: 자식 2개, 매크로 0개다. 따라서 뒤에 6바이트짜리 자식 항목이 2개 온다.
6. `15 00 0A 00 05 00`: 첫 자식이다. Object ID 0x0015 = 21(Input Number), X = 10, Y = 5다. Container 왼쪽 위에서 오른쪽으로 10, 아래로 5픽셀 떨어진 곳에 놓인다.
7. `16 00 6E 00 05 00`: 둘째 자식이다. Object ID 22(Input List), X = 0x006E = 110, Y = 5다.

길이는 2절 식대로 10 + 6 × 2 + 2 × 0 = 22바이트다.

- 이벤트: On Show, On Hide, On Refresh, On Change Child Location, On Change Child Position, On Change Size. On Show·On Hide는 이미 그 상태여도 Hide/Show 명령이 오면 발생하고, Hide/Show response는 명령으로 일어났을 때만 나간다. On Refresh는 이미 보이는 오브젝트를 다시 그릴 때, On Change Child Location·Position은 자식 위치를 바꾸는 명령을 받았을 때다.
- AID: Width `[1]`, Height `[2]`, Hidden `[3]`. 모두 읽기 전용이고, Container의 허용 명령 목록에는 Change Attribute가 없다. 표시는 Hide/Show Object, 크기는 Change Size로 바꾼다.
- Container는 그려지지 않는 논리 묶음이다. Width·Height는 겹침 판정과 클리핑(경계 밖을 잘라 내기) 경계로만 쓰인다. 숨기면 VT는 그 영역을 마스크 배경색으로 다시 그린다.
- 입력 필드에는 숨김 속성이 없다. 입력 필드를 숨기려면 Container나 Object Pointer에 담는다.

### Soft Key Mask(Type 4) 10바이트와 Key(Type 5) 15바이트

Soft Key Mask는 화면 옆 소프트키 줄 전체이고, Key는 그 안의 키 하나다. 여기서는 키 두 개(41, 42)짜리 줄을 만들고, Key 41에 "설정"이라는 글자와 매크로를 붙인다.

| Byte | hex | 필드 | 값 |
|---|---|---|---|
| 1~3 | `28 00 04` | Object ID, Type | 40, Soft Key Mask |
| 4 | `07` | Background colour(AID 1) | 7 = Silver |
| 5~6 | `02 00` | 객체 수, 매크로 수 | 2, 0 |
| 7~10 | `29 00 2A 00` | Key 목록(위치 없음) | Key 41, Key 42 |

| Byte | hex | 필드 | 값 |
|---|---|---|---|
| 1~3 | `29 00 05` | Object ID, Type | 41, Key |
| 4 | `07` | Background colour(AID 1) | 7 |
| 5 | `01` | Key code(AID 2) | 1 |
| 6~7 | `01 01` | 자식 수, 매크로 수 | 1, 1 |
| 8~13 | `2B 00 04 00 08 00` | 자식 | Output String 43 @ (4, 8) |
| 14~15 | `18 3C` | 매크로 | On Key Press(24) → Macro 60 |

Key 레코드의 새로운 부분만 따라 읽는다.

1. `01`(Byte 5): Key code 1이다. 키가 눌리면 VT는 이 번호를 작업기에 알린다.
2. `01 01`: 자식 1개, 매크로 1개다.
3. `2B 00 04 00 08 00`: 자식 Output String 0x002B = 43("설정" 글자)을 키 영역 왼쪽 위에서 (4, 8)에 그린다.
4. `18 3C`: 매크로 참조다. 이벤트 0x18 = 24(On Key Press, 키가 눌림)가 일어나면 Macro 0x3C = 60을 실행한다.

- 이벤트: Soft Key Mask는 On Show, On Hide, On Change Background Colour, On Change Attribute. Key는 On Key Press·On Key Release(Soft Key Activation message가 나간다), On Change Background Colour, On Change Child Location·Position, On Change Attribute, On Input Field Selection·De-selection.
- AID: Soft Key Mask는 Background colour(1). Key는 Background colour(1), Key code(2).
- Key에 좌표가 없는 이유는 <strong>나열 순서대로 물리 Soft Key에 배정</strong>되기 때문이다. NULL을 가리키는 Object Pointer는 자리를 예약해 뒤의 Key가 당겨지지 않게 하고, 목록 끝의 NULL 포인터는 표시도 페이징 계산도 하지 않는다. 페이징은 키가 물리 키보다 많을 때 여러 쪽으로 나눠 보여 주는 것이다([30장](/study/isobus/30-vt-display-technical-data)).
- Key code 0은 ACK 수단용으로 예약돼 있어 1~255만 쓴다. ACK 수단은 운전자가 경보를 확인했다고 알리는 키다. Key의 자식 좌표는 Soft Key designator(소프트키 하나에 그려지는 그림 영역) 좌상단 기준이고 designator 밖은 잘린다. Key의 배경색이 Soft Key Mask 배경색보다 우선한다.

### Button(Type 6): 19바이트

Button은 마스크 화면 안에 놓이는 버튼이다. 소프트키와 달리 화면 안의 위치와 크기를 직접 정한다.

| Byte | hex | 필드 | 값 |
|---|---|---|---|
| 1~3 | `32 00 06` | Object ID, Type | 50, Button |
| 4~7 | `64 00 28 00` | Width(1), Height(2) | 100 × 40 |
| 8~9 | `07 08` | Background colour(3), Border colour(4) | Silver, Grey |
| 10 | `02` | Key code(5) | 2 |
| 11 | `01` | Options(6, v4+) | bit 0 = latchable |
| 12~13 | `01 00` | 자식 수, 매크로 수 | 1, 0 |
| 14~19 | `33 00 00 00 00 00` | 자식 | Output String 51 @ (0, 0) |

Options 비트는 0 latchable(런타임에 바꾸려 하면 VT가 무시), 1 현재 latch 상태, 2 Suppress border, 3 Transparent background, 4 Disabled, 5 No border이고 6~7은 예약이다.

latchable은 한 번 누르면 눌린 상태로 남고 다시 눌러야 풀리는 버튼(토글 스위치 같은 것)이라는 뜻이다. 이 버튼의 Options `01`은 bit 0만 켜져 있으므로 latchable 버튼이다.

- 이벤트: On Enable·On Disable, On Input Field Selection·De-selection, On Key Press·On Key Release, On Change Background Colour, On Change Size, On Change Child Location·Position, On Change Attribute. Button Activation message는 운전자가 누르고 뗄 때만 나간다. latchable Button의 상태를 Change Attribute로 바꿔도 On Key Press·Release 이벤트(즉 매크로)는 일어나지만 메시지는 없다.
- AID: Width(1), Height(2), Background colour(3), Border colour(4), Key code(5), Options(6, v4+). 모두 쓰기 가능하다.
- 자식이 놓이는 곳은 Button Area가 아니라 <strong>Button Face</strong>다. Face는 Area보다 가로·세로 8픽셀 작고, Face의 오프셋은 (0, 0)~(8, 8) 사이에서 VT가 정한다. 자식 좌표는 Face 좌상단 기준이고 Face 밖은 잘린다. No border(bit 5)를 켜야 Face = Area, 오프셋 (0, 0)이 된다. 위 100 × 40 버튼에서 확실히 그려지는 영역은 92 × 32뿐이다. 픽셀 단위로 배치해야 하면 No border를 쓴다.
- momentary Button에 bit 2·3·5를 조합하고 외형을 실시간으로 바꾸면 라디오 버튼처럼 쓸 수 있다. momentary는 누르는 동안만 눌린 상태인 버튼이다.

Button Area는 테두리를 포함한 버튼 전체 영역이고, Button Face는 테두리 안쪽 면이다. Face가 Area 안 어디서 시작하는지(오프셋)는 VT가 정하므로, 작업기는 자식이 화면 어디에 그려질지 픽셀 단위로 맞출 수 없다. 자식은 Face 크기(위 예에서 92 × 32) 안에 들어가도록 배치한다.

정리하면, Container는 보이지 않는 묶음이라 속성을 전용 명령으로만 바꾸고, Key는 좌표 없이 나열 순서로 자리가 정해지며, Button은 테두리 때문에 자식이 그려지는 영역이 실제 크기보다 작다.

<small>근거: ISO 11783-6 B.4~B.7, B.8.1, Table B.7, B.9, B.11, B.13</small>

## 5. 입력 필드: Input Number, Number Variable, Input List

운전자가 값을 넣는 오브젝트를 본다. 숫자는 정수 원시값과 화면 표시값이 다르게 움직이므로, 두 값을 바꾸는 식을 함께 익힌다.

### Input Number(Type 9) 38바이트와 Number Variable(Type 21) 7바이트

Input Number는 운전자가 숫자를 넣는 칸이다. 여기서는 목표량을 0.00~50.00 범위로 받고, 실제 값은 Number Variable 23에 정수로 보관한다.

| Byte | hex | 필드 | 값 |
|---|---|---|---|
| 1~3 | `15 00 09` | Object ID, Type | 21, Input Number |
| 4~7 | `5A 00 1E 00` | Width(1), Height(2) | 90 × 30 |
| 8 | `01` | Background colour(3) | White |
| 9~10 | `1E 00` | Font attributes(4) | Font Attributes 30 |
| 11 | `00` | Options(5) | 불투명, 선행 0 없음, 0 표시, 반올림 |
| 12~13 | `17 00` | Variable reference(6) | Number Variable 23 |
| 14~17 | `00 00 00 00` | Value `[14]` | 참조가 있으므로 쓰지 않는다 |
| 18~21 | `00 00 00 00` | Min value(7) | 0 |
| 22~25 | `88 13 00 00` | Max value(8) | 5000 |
| 26~29 | `00 00 00 00` | Offset(9) | 0 |
| 30~33 | `0A D7 23 3C` | Scale(10) | 0.01(float) |
| 34~35 | `02 00` | Number of decimals(11), Format(12) | 2자리, 고정소수 |
| 36 | `06` | Justification(13) | 수평 오른쪽(2) + 수직 가운데(1 × 4), 수직은 v4+ |
| 37 | `01` | Options 2 `[15]` | Enabled, 실시간 편집 꺼짐 |
| 38 | `00` | 매크로 수 | 0 |

Number Variable 23은 `17 00 15 C4 09 00 00`이다. Object ID 23, Type 21, Value `[1]` = 2500이고 매크로 목록이 없다.

몇 칸만 따라 읽는다.

1. `17 00`(Byte 12~13): 변수 참조가 Number Variable 0x0017 = 23이다. 값은 이 변수에서 가져온다.
2. `88 13 00 00`(Byte 22~25): Max value다. 4바이트 리틀 엔디언이라 0x00001388 = 5000이다.
3. `0A D7 23 3C`(Byte 30~33): Scale이다. 거꾸로 붙인 0x3C23D70A가 단정밀도 부동소수(float) 0.01이다.
4. Number Variable의 `C4 09 00 00`: 0x000009C4 = 2500이 지금 값이다.

표시값과 입력 판정은 다음 식을 따른다.

- 표시값 = (Value + Offset) × Scale = (2500 + 0) × 0.01 = 25.00. 변수 참조가 NULL이 아니면 레코드의 Value 대신 Number Variable의 값을 쓴다.
- 운전자가 Enter를 누르면 (Min + Offset) × Scale ≤ 입력값 ≤ (Max + Offset) × Scale, 즉 0 ≤ 입력값 ≤ 50일 때만 받는다. 범위 밖이면 Enter를 무시하고 입력 상태를 유지한다.
- 받은 값은 입력값 ÷ Scale − Offset으로 되돌려 저장한다. 32.5를 입력하면 3250이 Number Variable 23에 들어가고, VT는 이 원시값을 Working Set(VT를 쓰는 작업기 쪽 제어 장치(ECU) 묶음)에 보고한다.
- Working Set은 풀 업로드나 Change Numeric Value로 Min·Max 밖의 값도 넣을 수 있다. 범위 제한은 운전자 입력에만 걸린다.

![Input Number 값 변환: 위쪽 표시 흐름은 Number Variable 23의 원시값 2500에 (Value + Offset) × Scale을 적용해 화면에 25.00을 보여 준다. 아래쪽 입력 흐름은 운전자가 넣은 32.5가 0 이상 50 이하인지 확인한 뒤 입력값 ÷ Scale − Offset으로 3250을 만들어 Number Variable 23에 저장하고 Working Set에 보고한다](/images/study-isobus/33-input-number-scaling-light.png)
![Input Number 값 변환: 위쪽 표시 흐름은 Number Variable 23의 원시값 2500에 (Value + Offset) × Scale을 적용해 화면에 25.00을 보여 준다. 아래쪽 입력 흐름은 운전자가 넣은 32.5가 0 이상 50 이하인지 확인한 뒤 입력값 ÷ Scale − Offset으로 3250을 만들어 Number Variable 23에 저장하고 Working Set에 보고한다](/images/study-isobus/33-input-number-scaling-dark.png)

- 이벤트: On Refresh, On Enable·On Disable, On Input Field Selection·De-selection, On ESC, On Change Background Colour, On Change Value, On Entry of Value(Enter, 값이 같아도), On Entry of New Value(값이 바뀌었을 때. 알림 메시지는 On Entry of Value 쪽에서 이미 나갔다), On Change Attribute, On Change Size.
- AID: Width(1)부터 Justification(13)까지 13개가 쓰기 가능하다. Value `[14]`와 Options 2 `[15]`는 읽기 전용이라 값은 Change Numeric Value로, Enabled 비트는 Enable/Disable Object로 바꾼다. Number Variable의 Value `[1]`도 Change Numeric Value로만 바꾼다.
- Number Variable을 Output Meter와 Output Number가 함께 참조하면 Change Numeric Value 한 번으로 둘 다 갱신된다. 변수의 On Change Value가 참조하는 표시 오브젝트를 모두 다시 그리기 때문이다.

::: warning 구현 함정: float Scale 0.01
Scale은 32비트 float라 0.01을 정확히 담지 못한다(실제 값 0.009999999776…). 그래서 원시값 2500의 표시값은 24.9999994…가 된다. 반올림(Options bit 3 = 0)이면 "25.00"이지만 Truncate(bit 3 = 1)를 켜면 <strong>"24.99"</strong>가 보인다. 최대값 판정의 (5000 + 0) × Scale도 50이 아니라 49.9999988…이라, VT가 이 값을 그대로 비교하면 운전자가 넣은 "50.00"이 범위 밖으로 거부된다. 표준은 계산식과 "배정밀도로 계산하라"는 권고(should)만 두고 비교 정밀도는 정하지 않는다. 다음은 추론에 따른 구현 조언이다. Working Set은 0.5·0.25·0.125처럼 2진수로 정확한 Scale을 쓰거나 Truncate를 피하고, VT는 Number of decimals 자릿수로 맞춘 값끼리 비교하는 편이 안전하다.
:::

Truncate는 반올림하지 않고 남는 자리를 잘라 버리는 것이다. 배정밀도는 소수를 8바이트(64비트)로 더 정밀하게 다루는 방식이다.

### Input List(Type 10): 19바이트

Input List는 미리 정한 항목 중 하나를 고르는 칸이다. 여기서는 살포 모드를 항목 3칸(Output String 24, 25, NULL)에서 고른다.

| Byte | hex | 필드 | 값 |
|---|---|---|---|
| 1~3 | `16 00 0A` | Object ID, Type | 22, Input List |
| 4~7 | `50 00 1E 00` | Width(1), Height(2) | 80 × 30 |
| 8~9 | `FF FF` | Variable reference(3) | NULL → Value 사용 |
| 10 | `00` | Value `[4]` | 0번 항목 선택 |
| 11 | `03` | Number of list items | 3(런타임에 바꿀 수 없다) |
| 12 | `01` | Options `[5]` | Enabled |
| 13 | `00` | 매크로 수 | 0 |
| 14~19 | `18 00 19 00 FF FF` | 항목 | Output String 24, 25, NULL |

- Value는 0~254가 항목 인덱스, 255가 "선택 없음"이다. 운전자는 255나 범위 밖 인덱스를 고를 수 없다. 다만 Number Variable을 다른 입력과 공유하면 범위 밖 값이 들어올 수 있다.
- 빈 항목은 두 종류다. 항목 ID 자체가 NULL이면(위 예의 2번 항목, 곧 세 번째 칸) 보이지도 선택되지도 않지만 인덱스 번호는 차지한다. NULL을 가리키는 Object Pointer나 숨긴 Container는 목록에 자리를 차지하고 선택도 되지만 내용이 안 보인다.
- 인덱스가 255이거나 범위 밖이거나, 선택된 항목이 NULL·NULL 포인터·숨긴 Container면 VT는 아무것도 그리지 않는다.
- 이벤트: Input Number와 같은 목록에서 On Change Background Colour만 빠진다. Input List는 Change Background Colour 명령 대상이 아니다.
- AID: Width(1), Height(2), Variable reference(3). Value `[4]`·Options `[5]`는 읽기 전용이다. 인덱스는 Change Numeric Value, 항목 교체는 Change List Item으로 바꾼다.

인덱스(index)는 목록에서 몇 번째 항목인지를 0부터 센 번호다. 위 레코드는 Value가 0이므로 첫 항목(Output String 24)이 선택되어 화면에 보인다.

정리하면, 숫자 입력은 "원시값을 Offset·Scale로 바꿔 보여 주고, 입력은 거꾸로 바꿔 저장"하며, 목록 입력은 0부터 센 인덱스로 고르고 255는 "선택 없음"이다.

<small>근거: ISO 11783-6 4.6.11.3, B.8.4, B.8.5, B.13.2, Table B.15, B.19, B.42</small>

## 6. 참조와 매크로: Object Pointer, String Variable, Macro

다른 오브젝트를 가리키는 포인터, 문자열을 보관하는 변수, 명령을 담아 두는 매크로를 본다. 셋 다 화면에 직접 그려지지 않고 다른 오브젝트를 돕는다.

### Object Pointer(Type 27) 5바이트와 String Variable(Type 22)

Object Pointer는 "지금 이 자리에 어떤 오브젝트를 보여 줄지"를 가리키는 바늘이다. 가리키는 대상만 바꾸면 화면의 한 자리를 다른 내용으로 갈아 끼울 수 있다.

Object Pointer 26은 `1A 00 1B 14 00`이다. Object ID 26, Type 27, Value `[1]` = 20(Container 20)이다.

- 이벤트: On Change Value 하나다. 이전 오브젝트를 숨기고 새 오브젝트를 그린 뒤 부모를 refresh한다.
- AID: Value `[1]`이 읽기 전용이라 가리키는 대상은 Change Numeric Value로 바꾼다.
- 가리킬 수 있는 타입은 부모에 따라 다르며, 포인터를 거쳐도 부모의 포함 규칙을 어길 수 없다. 포함 규칙은 부모 종류마다 담을 수 있는 자식 종류를 정한 표다(요지는 [ISO 11783-6 정리 부록](/study/isobus/appendix-iso-part06)). 다른 Object Pointer를 가리킬 수 있고, NULL을 가리키면 아무것도 그리지 않는다.
- 런타임에 잘못된 대상을 가리키게 하면 VT는 즉시 Change Numeric Value response에 "invalid value"를 담아 알리거나, 그 포인터를 담은 마스크를 활성화할 때 Change Active Mask response(또는 VT Change Active Mask message)로 알리고 풀을 지울 수 있다. 어느 쪽인지는 VT마다 다르다.

String Variable은 `ID(2) + Type 22 + Length(2) + Value(Length바이트)`로 끝나고 매크로 목록이 없다. Length는 정의한 뒤 바꿀 수 없고 짧은 문자열은 공백으로 채운다. 값은 Change String Value로 바꾸며 Working Set이 8비트 문자열과 WideString을 오갈 수 있다.

### Macro(Type 28): 21바이트

Macro는 VT 명령을 미리 적어 둔 묶음이다. 이벤트에 걸어 두면 작업기가 버스로 명령을 보내지 않아도 VT가 스스로 실행한다. 여기서는 4절의 Key 41이 눌리면(On Key Press) 실행되는 Macro 60을 만든다.

| Byte | hex | 필드 | 값 |
|---|---|---|---|
| 1~3 | `3C 00 1C` | Object ID, Type | 60, Macro |
| 4~5 | `10 00` | Number of bytes to follow | 16 |
| 6~13 | `A0 14 00 01 FF FF FF FF` | 명령 1 | Hide/Show Object: Container 20 보이기 |
| 14~21 | `AF 20 00 02 0E 00 00 00` | 명령 2 | Change Attribute: Fill Attributes 32의 AID 2(Fill colour) = 14(Yellow) |

명령 두 개를 따라 읽는다.

1. `10 00`: 뒤따르는 명령 바이트가 0x0010 = 16바이트다. 8바이트 명령 두 개다.
2. `A0`: 명령 코드 0xA0 = 160, Hide/Show Object다. `14 00` = 대상 Object ID 20, `01` = 보이기, `FF FF FF FF` = 8바이트를 채우는 빈 바이트다.
3. `AF`: 명령 코드 0xAF = 175, Change Attribute다. `20 00` = 대상 Object ID 32, `02` = AID 2(Fill colour), `0E 00 00 00` = 새 값 14(노랑)다.

- 명령은 VT 명령 메시지([37장](/study/isobus/37-vt-command-details))와 같은 형식으로 8바이트 단위로 넣는다. 8바이트보다 짧은 명령은 `FF`로 채운다. VT 명령 가운데 매크로에서 써도 된다고 표준이 표시한 명령만 넣을 수 있다. 기술 데이터 메시지([30장](/study/isobus/30-vt-display-technical-data))와 비휘발성 메모리 명령([31장](/study/isobus/31-vt-connection))은 매크로에 넣을 수 없다.
- Object ID 범위는 v4 이하 0~255, v5+ 0~65534다. 8비트 참조로 걸 수 있는 매크로는 0~255뿐이므로 256 이상이면 2절의 16비트 참조를 쓴다.
- 매크로 안 명령에는 응답 메시지가 나가지 않는다. 예를 들어 매크로의 Change Active Mask는 VT Status message는 일으키지만 Change Active Mask response는 보내지 않는다. 순환 참조는 금지다. 순환 참조는 매크로가 자기 자신을 다시 실행하게 만드는 고리를 말한다.
- AID는 Type `[0]`뿐이고, 허용 명령은 Execute Macro, Execute Extended Macro, Get Attribute Value다. 매크로가 실행되기 전에 풀과 맞는지(없는 오브젝트를 참조하지 않는지) 확인하는 것은 Working Set 책임이다.

정리하면, Object Pointer는 대상 Object ID 하나만 담은 5바이트 레코드이고, Macro는 8바이트 명령을 이어 붙인 레코드다. 둘 다 바꿀 때는 Change Attribute가 아니라 전용 명령을 쓴다.

<small>근거: ISO 11783-6 4.6.11.4, 4.6.11.5, A.1.3, Table A.2, B.13.3, B.15, B.16, D.1, E.1, Table B.54</small>

## 7. 경보 화면과 그리기: Alarm Mask, Line·Fill Attributes, Picture Graphic

마지막으로 경보 전용 화면, 선과 채우기 설정, 비트맵 그림을 본다. Alarm Mask에서는 2절의 16비트 매크로 참조가 실제로 쓰인다.

### Alarm Mask(Type 2): 20바이트, 16비트 매크로 참조 포함

Alarm Mask는 경고를 보여 주는 전용 화면이다. 우선순위에 따라 일반 화면(Data Mask) 위에 뜬다.

| Byte | hex | 필드 | 값 |
|---|---|---|---|
| 1~3 | `46 00 02` | Object ID, Type | 70, Alarm Mask |
| 4 | `0C` | Background colour(1) | 12 = Red |
| 5~6 | `FF FF` | Soft Key Mask(2) | NULL → designator를 비우는 것이 권고 |
| 7 | `00` | Priority(3) | 0 = High(운전자 위험·긴급 고장) |
| 8 | `00` | Acoustic signal(4) | 0 = 최고 우선순위 음 |
| 9~10 | `01 02` | 자식 수, 매크로 수 | 1, 2(16비트 참조 하나를 2로 센다) |
| 11~16 | `47 00 0A 00 50 00` | 자식 | Output String 71 @ (10, 80) |
| 17~20 | `FF 58 03 1B` | 매크로(v5+) | On Show(3) → Macro 7000(0x1B58) |

마지막 4바이트 `FF 58 03 1B`는 2절에서 본 16비트 참조다. `FF` 표지, Macro ID 낮은 바이트 `58`, 이벤트 `03`(On Show), Macro ID 높은 바이트 `1B`이므로 "화면에 나타나면 Macro 0x1B58 = 7000 실행"이다. 매크로 수 바이트가 1이 아니라 2인 것도 이 참조 하나를 2로 세기 때문이다.

- Priority는 0 High, 1 Medium(일반 알람·기계 고장), 2 Low(정보)이고 Acoustic signal은 0~2가 우선순위 음, 3이 무음이다.
- 이벤트: On Show(배경색 → 자식 순서대로 그리기 → 연결된 Soft Key Mask 표시, VT Status message), On Hide, On Refresh, On Change Background Colour, On Change Child Location·Position, On Change Priority, On Change Soft Key Mask, On Change Attribute. On Change Priority에서 VT는 Working Set 사이의 알람 우선순위를 다시 평가한다.
- AID: Background colour(1), Soft Key Mask(2), Priority(3), Acoustic signal(4). 모두 쓰기 가능하다. 알람 처리 흐름은 [39장](/study/isobus/39-vt-alarm-activation)에서 다룬다.

### Line Attributes(Type 24)·Fill Attributes(Type 25): 각 8바이트

선과 도형 채우기 설정을 담는 속성 오브젝트다. 32장의 Font Attributes처럼 여러 오브젝트가 함께 가리켜 쓴다.

- Line Attributes 31: `1F 00 18 00 02 FF FF 00` → Line colour(1) = 0(Black), Line width(2) = 2픽셀, Line art(3) = `0xFFFF`(실선), 매크로 0.
- Fill Attributes 32: `20 00 19 02 07 FF FF 00` → Fill type(1) = 2(Fill colour로 채움), Fill colour(2) = 7(Silver), Fill pattern(3) = NULL, 매크로 0.

- Line art는 16비트 패턴이다. 1 비트는 선 색으로 칠하고 0 비트는 건너뛰며, 비트 하나가 붓 한 칸 크기다. Line width가 0인 선은 그리지 않는다. `0xFFFF`는 16비트가 모두 1이라 끊김 없는 실선이다.
- Fill type은 0 없음, 1 선 색, 2 Fill colour, 3 패턴(Picture Graphic)이다.
- Fill type을 3으로 바꿀 때는 <strong>Fill pattern을 먼저, Fill type을 나중에</strong> 바꿔야 한다. 순서를 어기면 VT 동작은 예측할 수 없다. Fill type 3인데 패턴이 NULL이면 채우지 않는다.
- 패턴용 Picture Graphic은 남는 비트가 없어야 한다. 단색이면 폭이 8의 배수, 16색이면 2의 배수여야 하고, 어기면 End of Object Pool response나 VT Change Active Mask message로 오류가 온다.
- 이벤트: On Change Line(Fill) Attributes, On Change Attribute. 이 속성을 참조하며 화면에 있는 오브젝트를 모두 다시 그린다.
- AID: Line은 Line colour(1), Line width(2), Line art(3). Fill은 Fill type(1), Fill colour(2), Fill pattern(3).
- [32장](/study/isobus/32-vt-object-pool-basics)의 Font Attributes도 같은 계열이다. AID는 Font colour(1), Font size(2), Font type(3), Font style(4)이다. 다만 Change Attribute로 크기·스타일을 VT가 지원하지 않는 조합으로 바꾸면 풀이 무효가 될 수 있다. 크기·스타일을 한 번에 바꾸는 Change Font Attributes 명령을 쓰면 이 문제를 피할 수 있다.

### Picture Graphic(Type 20): raw 25바이트, RLE 19바이트

Picture Graphic은 비트맵 그림이다. 픽셀 데이터를 그대로 담을 수도 있고(raw), RLE(Run-Length Encoding)로 줄여 담을 수도 있다. RLE는 같은 값이 여러 번 이어지면 "반복 횟수, 값" 두 바이트로 줄여 적는 압축 방식이다.

16 × 4 단색 그림(모든 픽셀이 색 1)을 목표 폭 32로 표시한다. 두 값이 있는 칸은 raw / RLE 순이다.

| Byte | hex | 필드 | 값 |
|---|---|---|---|
| 1~3 | `50 00 14` | Object ID, Type | 80, Picture Graphic |
| 4~5 | `20 00` | Width(1) | 목표 폭 32 → 높이는 VT가 비율로 계산(8) |
| 6~9 | `10 00 04 00` | Actual width `[4]`, Actual height `[5]` | 16 × 4 |
| 10 | `00` | Format `[6]` | 0 = 단색(1비트/픽셀) |
| 11 | `00` / `04` | Options(2) | raw / bit 2 = RLE |
| 12 | `01` | Transparency colour(3) | 1(Options bit 0이 1일 때만 쓰인다) |
| 13~16 | `08 00 00 00` / `02 00 00 00` | 데이터 바이트 수 | 8 / 2 |
| 17 | `00` | 매크로 수 | 0 |
| 18~ | `FF FF FF FF FF FF FF FF` / `08 FF` | 데이터 | raw 8바이트 / (8회, `FF`) |

데이터 부분을 따라 읽는다. 단색은 1바이트에 8픽셀이므로 폭 16픽셀 한 줄은 2바이트다. 4줄이면 8바이트이고, 모든 픽셀이 1이므로 8바이트가 모두 `FF`다. RLE로 줄이면 "`FF`가 8번"이라 `08 FF` 2바이트가 된다.

- 픽셀은 줄 단위로 왼쪽에서 오른쪽, 위에서 아래로 놓인다. 단색은 1바이트에 8픽셀(MSB가 왼쪽), 4비트 색은 2픽셀(상위 니블이 왼쪽), 8비트 색은 1픽셀이다. 줄 끝의 남는 비트는 0으로 채우고 VT는 무시한다. 10 × 2 흰색 단색이면 `FF C0 FF C0`이다. MSB는 바이트의 가장 높은 비트, 니블은 반 바이트(4비트)다.
- 데이터가 모자라면 VT는 End of Object Pool response나 VT Change Active Mask message로 오류를 알리고, 남으면 무시한다.
- RLE는 (반복 횟수, 값) 바이트 쌍이다. 표준에 실린 예는 `00 00 00 00 00 00 03 03 03 01 01 02` → `06 00 03 03 02 01 01 02`이고, 횟수가 0인 쌍의 값은 무시한다. 복잡한 그림은 오히려 커진다. 위 10 × 2 예를 RLE로 바꾸면 4바이트가 `01 FF 01 C0 01 FF 01 C0` 8바이트가 된다. 그럴 땐 raw를 쓰라고 권한다.
- RLE일 때 Byte 13~16에 압축 전·후 어느 길이를 넣는지 표준은 따로 밝히지 않는다(속성 이름은 "Number of bytes in raw data"). 레코드에 실제로 실린 바이트 수여야 그 뒤 매크로 쌍의 위치를 찾을 수 있으므로 위 예에서는 압축 후 길이 2로 적었다(추론, 확인 필요).
- 스케일은 VT가 Width(목표 폭) 기준으로 하고 높이는 비율로 계산한다. 픽셀 단위 정확도가 필요하면 Width = Actual width로 둬 스케일을 막는다. 채우기 패턴으로 쓸 때는 Width와 무관하게 원본 그대로 쓴다.
- 이벤트: On Refresh(불투명·투명, 깜빡임 옵션 비트가 바뀔 때 등), On Change Attribute.
- AID: Width(1), Options(2), Transparency colour(3). Options bit 2(RLE)는 런타임에 바꿔도 VT가 무시한다. Actual width `[4]`, Actual height `[5]`, Format `[6]`은 읽기 전용이다.

정리하면, Alarm Mask는 우선순위와 경보음을 속성으로 갖는 경보 화면이고, Line·Fill Attributes는 선과 채우기 설정 묶음이며, Picture Graphic은 비트맵을 raw나 RLE로 담는다. Picture Graphic은 데이터 길이에 따라 매크로 목록 위치가 움직인다.

<small>근거: ISO 11783-6 4.6.16.4, 4.6.20, 4.6.21, B.3, B.10.1, B.12.2, B.14.2~B.14.4, Table B.5, B.40, B.47, B.49</small>

## 8. AID 요약과 레코드 경계 검산 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

### AID 요약

32장과 이 장의 오브젝트를 한 표로 모은다. "전용 명령"은 AID가 없거나 읽기 전용인 값을 바꾸는 수단이다(명령 바이트 배치는 [37장](/study/isobus/37-vt-command-details)). "없음"은 해당하는 것이 없다는 뜻이다.

| 오브젝트(Type) | Change Attribute로 바꿀 수 있는 AID | 읽기 전용 AID | 전용 명령 |
|---|---|---|---|
| Working Set(0) | 없음 | Background colour `[1]`, Selectable `[2]`, Active mask `[3]` | Change Active Mask, Change Background Colour |
| Data Mask(1) | Background colour 1, Soft Key Mask 2 | 없음 | Change Soft Key Mask |
| Alarm Mask(2) | 1~4(배경색, Soft Key Mask, Priority, Acoustic) | 없음 | Change Priority |
| Container(3) | 없음(Change Attribute 미허용) | Width `[1]`, Height `[2]`, Hidden `[3]` | Hide/Show Object, Change Size |
| Soft Key Mask(4) | Background colour 1 | 없음 | 없음 |
| Key(5) | Background colour 1, Key code 2 | 없음 | 없음 |
| Button(6) | Width 1 ~ Options 6 | 없음 | Enable/Disable Object(v4+) |
| Input Number(9) | 1~13 | Value `[14]`, Options 2 `[15]` | Change Numeric Value, Enable/Disable Object |
| Input List(10) | Width 1, Height 2, Variable reference 3 | Value `[4]`, Options `[5]` | Change Numeric Value, Change List Item |
| Output String(11) | 1~7(Width ~ Justification) | 없음 | Change String Value |
| Output Number(12) | 1~11(Width ~ Justification) | Value `[12]` | Change Numeric Value |
| Picture Graphic(20) | Width 1, Options 2, Transparency colour 3 | Actual width `[4]`, Actual height `[5]`, Format `[6]` | 없음 |
| Number Variable(21) | 없음 | Value `[1]` | Change Numeric Value |
| Font Attributes(23) | 1~4 | 없음 | Change Font Attributes |
| Line·Fill Attributes(24·25) | 1~3 | 없음 | Change Line·Fill Attributes |
| Object Pointer(27) | 없음 | Value `[1]` | Change Numeric Value |

32장의 Output String·Output Number 이벤트는 On Refresh, On Change Background Colour, On Change Value, On Change Attribute, On Change Size이고, Font Attributes는 On Change Font Attributes, On Change Attribute다.

### 파이썬으로 경계 검산하기

아래 코드는 이 장의 레코드를 모두 바이트로 만들어 표의 hex와 같은지 확인한다. Window Mask 100과 Key Group 120 레코드도 함께 만드는데, 두 오브젝트는 [34장](/study/isobus/34-vt-layout-color)에서 다룬다. 마지막에는 레코드를 이어 붙인 풀을 1절의 방법(Type 읽기, 길이 계산, 건너뛰기)으로 처음부터 끝까지 읽는다.

::: details 파이썬으로 이 장의 레코드와 레코드 경계 검산해 보기
```python
import struct

NULL = 0xFFFF
u8 = lambda v: bytes([v])
u16 = lambda v: v.to_bytes(2, "little")
s16 = lambda v: v.to_bytes(2, "little", signed=True)
u32 = lambda v: v.to_bytes(4, "little")
hx = lambda b: b.hex(" ").upper()
head = lambda oid, otype: u16(oid) + u8(otype)
children = lambda items: b"".join(u16(i) + s16(x) + s16(y) for i, x, y in items)
refs = lambda ids: b"".join(u16(i) for i in ids)
macro8 = lambda event, mid: u8(event) + u8(mid)
macro16 = lambda event, mid: u8(0xFF) + u8(mid & 0xFF) + u8(event) + u8(mid >> 8)

container = head(20, 3) + u16(200) + u16(60) + u8(0) + u8(2) + u8(0) \
    + children([(21, 10, 5), (22, 110, 5)])
skm = head(40, 4) + u8(7) + u8(2) + u8(0) + refs([41, 42])
key = head(41, 5) + u8(7) + u8(1) + u8(1) + u8(1) + children([(43, 4, 8)]) + macro8(24, 60)
button = head(50, 6) + u16(100) + u16(40) + u8(7) + u8(8) + u8(2) + u8(0x01) \
    + u8(1) + u8(0) + children([(51, 0, 0)])
input_number = head(21, 9) + u16(90) + u16(30) + u8(1) + u16(30) + u8(0) + u16(23) \
    + u32(0) + u32(0) + u32(5000) + (0).to_bytes(4, "little", signed=True) \
    + struct.pack("<f", 0.01) + u8(2) + u8(0) + u8(0x06) + u8(0x01) + u8(0)
num_var = head(23, 21) + u32(2500)
input_list = head(22, 10) + u16(80) + u16(30) + u16(NULL) + u8(0) + u8(3) + u8(0x01) \
    + u8(0) + refs([24, 25, NULL])
obj_ptr = head(26, 27) + u16(20)
cmds = bytes([0xA0]) + u16(20) + u8(1) + b"\xFF" * 4 \
    + bytes([0xAF]) + u16(32) + u8(2) + u32(14)
macro = head(60, 28) + u16(len(cmds)) + cmds
alarm = head(70, 2) + u8(12) + u16(NULL) + u8(0) + u8(0) + u8(1) + u8(2) \
    + children([(71, 10, 80)]) + macro16(3, 7000)
line_attr = head(31, 24) + u8(0) + u8(2) + u16(0xFFFF) + u8(0)
fill_attr = head(32, 25) + u8(2) + u8(7) + u16(NULL) + u8(0)


def rle(data):
    out, i = bytearray(), 0
    while i < len(data):
        n = 1
        while i + n < len(data) and data[i + n] == data[i] and n < 255:
            n += 1
        out += bytes([n, data[i]])
        i += n
    return bytes(out)


def picture(oid, width, aw, ah, fmt, options, data):
    # 매크로 개수(Byte 17)는 데이터 앞, 매크로 쌍은 데이터 뒤에 온다
    return head(oid, 20) + u16(width) + u16(aw) + u16(ah) + u8(fmt) + u8(options) \
        + u8(1) + u32(len(data)) + u8(0) + data


raw = bytes([0xFF] * 8)                          # 16x4 단색, 한 줄 2바이트
pg_raw = picture(80, 32, 16, 4, 0, 0x00, raw)
pg_rle = picture(80, 32, 16, 4, 0, 0x04, rle(raw))
window = head(100, 34) + u8(1) + u8(1) + u8(1) + u8(0) + u8(0x01) \
    + u16(101) + u16(102) + u16(103) + u8(2) + u8(0) + u8(0) + refs([104, 105])
key_group = head(120, 35) + u8(0x03) + u16(121) + u16(NULL) + u8(1) + u8(0) + refs([122])

assert hx(container) == "14 00 03 C8 00 3C 00 00 02 00 15 00 0A 00 05 00 16 00 6E 00 05 00"
assert hx(skm) == "28 00 04 07 02 00 29 00 2A 00"
assert hx(key) == "29 00 05 07 01 01 01 2B 00 04 00 08 00 18 3C"
assert hx(button) == "32 00 06 64 00 28 00 07 08 02 01 01 00 33 00 00 00 00 00"
assert len(input_number) == 38 and hx(input_number[29:33]) == "0A D7 23 3C"
assert hx(num_var) == "17 00 15 C4 09 00 00"
assert hx(input_list) == "16 00 0A 50 00 1E 00 FF FF 00 03 01 00 18 00 19 00 FF FF"
assert hx(obj_ptr) == "1A 00 1B 14 00"
assert hx(macro) == "3C 00 1C 10 00 A0 14 00 01 FF FF FF FF AF 20 00 02 0E 00 00 00"
assert hx(alarm) == "46 00 02 0C FF FF 00 00 01 02 47 00 0A 00 50 00 FF 58 03 1B"
assert hx(line_attr) == "1F 00 18 00 02 FF FF 00" and hx(fill_attr) == "20 00 19 02 07 FF FF 00"
assert hx(pg_rle) == "50 00 14 20 00 10 00 04 00 00 04 01 02 00 00 00 00 08 FF"
assert len(pg_raw) == 25 and len(pg_rle) == 19
assert rle(bytes([0, 0, 0, 0, 0, 0, 3, 3, 3, 1, 1, 2])) == bytes([6, 0, 3, 3, 2, 1, 1, 2])
assert rle(bytes.fromhex("FF C0 FF C0")) == bytes.fromhex("01 FF 01 C0 01 FF 01 C0")
assert hx(window) == "64 00 22 01 01 01 00 01 65 00 66 00 67 00 02 00 00 68 00 69 00"
assert hx(key_group) == "78 00 23 03 79 00 FF FF 01 00 7A 00"

# 레코드에는 전체 길이 필드가 없다. Type별 규칙을 알아야 다음 레코드를 찾는다
LENGTH = {
    2: lambda r: 10 + 6 * r[8] + 2 * r[9],       # Alarm Mask
    3: lambda r: 10 + 6 * r[8] + 2 * r[9],       # Container
    4: lambda r: 6 + 2 * r[4] + 2 * r[5],        # Soft Key Mask
    5: lambda r: 7 + 6 * r[5] + 2 * r[6],        # Key
    6: lambda r: 13 + 6 * r[11] + 2 * r[12],     # Button
    9: lambda r: 38 + 2 * r[37],                 # Input Number
    10: lambda r: 13 + 2 * r[10] + 2 * r[12],    # Input List
    20: lambda r: 17 + int.from_bytes(r[12:16], "little") + 2 * r[16],  # Picture Graphic
    21: lambda r: 7,                             # Number Variable
    24: lambda r: 8 + 2 * r[7],                  # Line Attributes
    25: lambda r: 8 + 2 * r[7],                  # Fill Attributes
    27: lambda r: 5,                             # Object Pointer
    28: lambda r: 5 + int.from_bytes(r[3:5], "little"),                 # Macro
    34: lambda r: 17 + 2 * r[14] + 6 * r[15] + 2 * r[16],              # Window Mask
    35: lambda r: 10 + 2 * r[8] + 2 * r[9],      # Key Group
}

pool = b"".join([container, skm, key, button, input_number, num_var, input_list, obj_ptr,
                 macro, alarm, line_attr, fill_attr, pg_raw, window, key_group])
pos, ids = 0, []
while pos < len(pool):
    rec = pool[pos:]
    ids.append(int.from_bytes(rec[:2], "little"))
    pos += LENGTH[rec[2]](rec)                   # 모르는 Type이면 KeyError: 더 못 읽는다
assert ids == [20, 40, 41, 50, 21, 23, 22, 26, 60, 70, 31, 32, 80, 100, 120]
assert pos == len(pool)
print("레코드", len(ids), "개,", len(pool), "바이트, 경계 검산 통과")
```
:::

실행하면 모든 `assert`가 통과하고 "레코드 15 개, 250 바이트, 경계 검산 통과"가 출력된다. `LENGTH` 사전이 2절의 길이 식을 코드로 옮긴 것이다. 사전에 없는 Type을 만나면 `KeyError`로 멈춘다. 1절에서 말한 "규칙을 모르는 타입을 만나면 그 뒤 경계를 잃는다"가 코드에서는 이렇게 드러난다.

<small>근거: ISO 11783-6 Annex B(Table B.21, B.45)</small>

::: tip 핵심 정리
- 모든 레코드는 Object ID(2) + Type(1) + 고정 속성 + 목록 개수 + 목록 순이고, 전체 길이 필드가 없어 Type별 규칙으로만 끝을 찾는다. 그래서 VT는 기능을 지원하지 않는 오브젝트도 파싱할 수 있어야 한다.
- AID는 속성 번호다. 대괄호가 붙은 속성은 읽기 전용이라 Change Numeric Value, Hide/Show Object, Enable/Disable Object 같은 전용 명령으로 바꾼다. AID 번호는 바이트 순서와 다르다.
- 목록은 위치 있는 자식(6바이트), 위치 없는 참조(2바이트), 매크로(2바이트) 세 가지다. 16비트 매크로 참조 하나는 매크로 개수에서 2로 센다.
- Output String·Picture Graphic은 매크로 목록 위치가 가변 데이터에 따라 움직인다.
- 숫자 입력은 원시값을 Offset·Scale로 바꿔 보여 주고, 운전자 입력은 거꾸로 바꿔 저장한다. 범위 제한은 운전자 입력에만 걸린다.
:::

::: details 확인 문제
1. 레코드에 전체 길이 필드가 없다. VT는 다음 레코드가 어디서 시작하는지 어떻게 아는가? 규칙을 모르는 타입이 섞여 있으면 어떻게 되는가?
2. 레코드 정의에서 Container의 Hidden 속성은 AID `[3]`처럼 대괄호로 싸여 있다. 이 속성을 Change Attribute로 바꿀 수 있는가? Container를 숨기려면 어떤 명령을 쓰는가?
3. Alarm Mask 레코드의 매크로 수 바이트가 `02`인데, 매크로 목록은 `FF 58 03 1B` 4바이트 하나뿐이다. 왜 2인가?
4. Input Number의 Scale이 0.01, Offset이 0이다. Number Variable에 1234가 들어 있으면 화면에 무엇이 보이는가(소수 2자리)? 운전자가 12.5를 넣으면 변수에는 무엇이 저장되는가?
5. (디코딩) 다음 레코드는 무엇이고 화면에는 무엇이 보이는가? 운전자가 고를 수 있는 항목은 몇 개인가?
   `16 00 0A 50 00 1E 00 FF FF FF 03 01 00 18 00 19 00 FF FF`

**답 가이드**
1. 레코드의 세 번째 바이트(Type)를 읽고, 그 타입의 레코드 규칙대로 필드와 목록 개수를 읽어 길이를 계산한 뒤 그만큼 건너뛴다. 규칙을 모르는 타입이 있으면 그 레코드의 끝을 알 수 없어 뒤 레코드 전체의 경계를 잃는다. 그래서 VT는 기능을 지원하지 않는 오브젝트도 파싱할 수 있어야 한다.
2. 바꿀 수 없다. 대괄호는 읽기 전용 표시라 Get Attribute Value로 읽기만 하고, Container는 허용 명령 목록에 Change Attribute가 아예 없다. 숨기거나 보이려면 Hide/Show Object 명령을 쓴다.
3. 16비트 매크로 참조(v5+)는 2바이트 그룹 두 개(4바이트)로 이루어지고, "Number of macros to follow"에서 2개로 센다. `FF`는 이벤트가 아니라 16비트 참조 표지다.
4. 반올림 표시(Options bit 3 = 0)라면 (1234 + 0) × 0.01 = 12.34가 보인다. 다만 float 0.01은 실제로 0.00999999977…이라 계산값이 12.3399997…이므로, Truncate(bit 3 = 1)를 켜면 12.33이 보인다(5절 경고 상자). 입력 12.5는 0~50 범위 안이므로 받아서 12.5 ÷ 0.01 − 0 = 1250으로 저장한다.
5. Type `0A` = Input List(ID 22), 80 × 30, 변수 참조 NULL이라 레코드의 Value를 쓴다. Value가 `FF`(255) = "선택 없음"이라 화면에는 아무것도 그리지 않는다. 항목은 3개로 세지만 세 번째가 NULL 자리표시자라 보이지도 선택되지도 않는다. 운전자가 고를 수 있는 것은 0번(Output String 24)과 1번(Output String 25) 두 개이고, 255는 운전자가 고를 수 없다. Options `01`이라 활성 상태다.
:::

## 다음 챕터

- 다음: [34장 VT 화면 배치, User-Layout, 색](/study/isobus/34-vt-layout-color)
