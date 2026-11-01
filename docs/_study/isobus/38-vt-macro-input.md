---
title: "매크로와 운전자 입력 처리"
description: "매크로가 오브젝트 풀 안에 바이트로 저장되고 실행되는 규칙과, 운전자 입력과 Soft Key·Button 활성화가 화면 변화와 겹칠 때의 규칙을 익힌다."
date: 2026-04-13
tags: [ISOBUS, VT, Macro, Input, Soft Key, ISO-11783-6]
prev: /study/isobus/37-vt-command-details
next: /study/isobus/39-vt-alarm-activation
---

# 매크로와 운전자 입력 처리

::: info 학습 목표
- 매크로가 무엇이고 왜 쓰는지 "버튼에 묶어 둔 단축키"에 빗대어 설명할 수 있다.
- Macro 오브젝트 레코드와 이벤트-매크로 참조(8비트, 16비트)를 바이트로 읽고 쓸 수 있다.
- 매크로가 실행되는 때와 순서를 말하고, 매크로에 넣을 수 없는 명령을 구분할 수 있다.
- 운전자 입력이 Navigating과 Data input 두 상태를 오가는 흐름과, 입력 중에 화면이 바뀔 때 오는 메시지를 따라갈 수 있다.
- Soft Key·Button을 누르고 있는 동안 화면이 바뀌거나 응답이 유실될 때 VT가 보내는 메시지를 해석할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [36장 VT 명령어 기초](/study/isobus/36-vt-commands-basics), [37장 VT 명령 세부와 공통 규칙](/study/isobus/37-vt-command-details), [33장 오브젝트 레코드](/study/isobus/33-vt-object-records)
- 이 장에서 처음 나오는 말
  - 매크로(Macro): 오브젝트 풀 안에 미리 적어 둔 VT 명령 목록. 이벤트가 일어나면 VT가 스스로 실행한다.
  - 이벤트(Event): "눌렸다", "화면에 나타났다"처럼 매크로를 실행시키는 계기. Event ID라는 번호로 구분한다.
  - Navigating과 Data input: 운전자가 입력 필드 사이를 옮겨 다니는 상태와, 한 필드에 값을 넣고 있는 상태.
  - real-time editing(실시간 편집): 다이얼을 돌리는 동안 바뀐 값을 그때그때 작업기에 보내는 입력 방식.
  - momentary(비래치) 수단: 누르는 동안만 켜지고 손을 떼면 저절로 꺼지는 키·버튼.
  - 래칭(latching) 버튼: 한 번 누르면 눌린 상태로 남고, 다시 눌러야 풀리는 버튼.
:::

컴퓨터에서는 단축키 하나에 "복사, 새 창 열기, 붙여 넣기"를 묶어 한 번에 실행되게 만들 수 있다. VT의 매크로(Macro)도 버튼 하나에 여러 명령을 묶어 둔 단축키라서, 작업기 ECU가 버스로 명령을 하나씩 보내지 않아도 VT가 오브젝트 풀에 적힌 목록대로 스스로 화면을 바꾼다. 이 장의 앞부분(1~5절)은 이 단축키가 바이트로 어떻게 저장되고 어떤 순서로 실행되는지 본다. 뒷부분(6~10절)은 운전자가 값을 넣거나 키를 누르는 도중에 작업기의 명령이 끼어들 때 VT가 어떻게 움직이는지 본다.

## 1. 매크로 한눈에 보기: 버튼에 묶어 둔 단축키

36장에서 매크로를 XML 예시로 처음 봤다. 매크로 50은 Working Set `0x0000`의 Active Mask를 설정 화면 `0x0002`로 바꾸는 명령 하나를 담고 있었고, Button 20의 "On Key Press(눌림)" 이벤트에 연결되어 있었다. 이 절에서는 매크로를 쓰면 무엇이 달라지는지 그림으로 먼저 보고, 이 장에서 다룰 매크로 규칙의 큰 줄기를 정리한다.

VT의 동작 규칙을 정하는 표준 문서는 ISO 11783-6이다. 이 장에서는 줄여서 Part 6이라고 부른다.

![같은 버튼 누름을 매크로 없이 처리하면 Button Activation, Change Active Mask 명령, 응답이 버스를 오간 뒤 화면이 바뀌고, 매크로로 처리하면 VT가 매크로 50의 Change Active Mask를 스스로 실행해 화면을 바로 바꾸며 Button Activation은 알림으로만 가는 흐름 비교](/images/study-isobus/38-macro-shortcut-light.png)
![같은 버튼 누름을 매크로 없이 처리하면 Button Activation, Change Active Mask 명령, 응답이 버스를 오간 뒤 화면이 바뀌고, 매크로로 처리하면 VT가 매크로 50의 Change Active Mask를 스스로 실행해 화면을 바로 바꾸며 Button Activation은 알림으로만 가는 흐름 비교](/images/study-isobus/38-macro-shortcut-dark.png)

그림 위쪽은 매크로가 없을 때다. 버튼을 누른 결과가 화면에 나타나기까지 메시지가 버스를 세 번 지난다.

1. VT가 Button Activation으로 "버튼이 눌렸다"고 작업기에 알린다.
2. 작업기가 판단해서 Change Active Mask 명령을 보낸다.
3. VT가 명령을 처리하고 응답한 뒤 화면을 바꾼다.

그림 아래쪽은 매크로가 있을 때다. VT가 오브젝트 풀에서 그 버튼에 연결된 매크로 50을 찾아, 안에 적힌 Change Active Mask를 스스로 실행한다. 화면은 작업기의 판단을 기다리지 않고 바로 바뀐다. Part 6도 "눌림 이벤트에 매크로를 걸어 다른 마스크를 띄우는 식으로 운전자 화면의 반응을 좋게 할 수 있다"고 설명한다.

버튼이 눌렸다는 Button Activation은 매크로가 있든 없든 작업기에 그대로 간다. Part 6은 키가 눌리면 활성화 메시지를 보내고, 그 키에 매크로가 연결돼 있으면 매크로도 실행한다고 정한다. 그래서 작업기는 매크로가 화면을 바꾼 뒤에도 "버튼이 눌렸다"는 사실을 알 수 있다.

비유가 맞지 않는 점도 있다.

- 매크로에는 아무 명령이나 넣을 수 없다. 넣을 수 없는 명령은 2절에서 본다.
- 매크로 안에서 실행된 명령에는 응답이 나가지 않는다(4절).
- 매크로는 적힌 명령을 순서대로 실행하는 목록일 뿐이다. "값이 얼마 이상이면"처럼 조건을 따지는 판단은 작업기 쪽 프로그램이 해야 한다.

이 장에서 볼 매크로 규칙은 세 갈래다. 매크로가 풀 안에 어떤 바이트로 저장되는가(2절), 이벤트에 매크로를 어떻게 연결하는가(3절), 언제 어떤 순서로 실행되는가(4절)다. 매크로 번호를 넓힌 v5의 확장과 검산 코드는 5절에 모았다.

<small>근거: ISO 11783-6 4.6.11.4, 4.6.18, 4.6.22</small>

## 2. 매크로는 풀 안에 어떻게 저장되는가

36장의 XML은 사람이 읽기 좋게 쓴 표현이다. VT에 실제로 올라가는 것은 XML이 아니라 바이트다. 이 절은 매크로가 오브젝트 풀 안에서 어떤 바이트로 저장되는지, 그리고 매크로에 넣을 수 없는 명령은 무엇인지 본다. Macro 오브젝트 레코드의 전체 형식은 [33장](/study/isobus/33-vt-object-records)에 있다.

### Macro 오브젝트 안에서 명령은 어떻게 저장되는가

바이트를 읽기 전에 약속 세 가지를 확인한다.

- 16진수 두 자리가 한 바이트다. 바이트 번호는 1부터 센다.
- 2바이트 이상인 수는 리틀 엔디언이다. 낮은 자리 바이트가 먼저 오므로 `32 00`은 `0x0032`(=50)이다.
- `FF`는 "여기는 쓰지 않는 자리"라는 뜻의 채움 값이다. 짧은 데이터를 정해진 길이에 맞출 때 남는 자리를 `FF`로 채운다.

이 장에서 "Working Set 명령"은 [37장](/study/isobus/37-vt-command-details)의 코드 범위 표에서 "Working Set이 보내는 명령"으로 묶인 것을 말한다. Change Numeric Value, Change Active Mask, Hide/Show Object처럼 Byte 1이 `90`, `92`, `A0`~`BA`, `BC`~`BE`인 명령들이다. 36장에서는 같은 것을 "작업기가 VT에게 보내는 명령"이라고 불렀다.

Macro 오브젝트(type 28)는 명령 패킷을 이어 붙인 목록이다. 레코드는 Object ID(2바이트), Type(`1C` = 28), 뒤따를 바이트 수(2바이트), 그리고 명령 패킷들로 이뤄진다. 각 명령 패킷은 <strong>Working Set 명령의 형식 그대로</strong>다. Byte 1이 VT function(명령의 종류를 나타내는 코드)이고, 그 뒤가 그 명령의 파라미터다. 패킷이 8바이트보다 짧으면 `FF`로 8바이트까지 채운다. Part 6은 2바이트 문자열을 보내는 Change String Value를 예로 든다. 이 명령은 7바이트이므로 `FF` 하나를 붙여 8바이트로 만든다.

![8비트 매크로 참조(Event ID 18, Macro ID 32)와 16비트 참조(FF, Macro ID 하위 2C, Event ID 18, Macro ID 상위 01), 그리고 Macro 오브젝트 레코드(Object ID 32 00, Type 1C, 바이트 수 08 00, Change Active Mask 명령 패킷 8바이트)의 바이트 배치](/images/study-isobus/17-macro-encoding-light.png)
![8비트 매크로 참조(Event ID 18, Macro ID 32)와 16비트 참조(FF, Macro ID 하위 2C, Event ID 18, Macro ID 상위 01), 그리고 Macro 오브젝트 레코드(Object ID 32 00, Type 1C, 바이트 수 08 00, Change Active Mask 명령 패킷 8바이트)의 바이트 배치](/images/study-isobus/17-macro-encoding-dark.png)

그림의 맨 아래 줄이 이 절에서 볼 Macro 오브젝트 레코드이고, 위 두 줄은 3절에서 볼 이벤트 참조다.

36장의 매크로 50(Working Set `0x0000`의 Active Mask를 `0x0002`로 바꿈)을 바이트로 쓰면 13바이트다.

```text
32 00 | 1C | 08 00 | AD 00 00 02 00 FF FF FF
 ID     Type  길이    Change Active Mask 패킷 (5바이트 + FF 3개)
```

앞에서부터 한 칸씩 읽어 보면 다음과 같다.

1. `32 00`: Object ID. 리틀 엔디언이므로 `0x0032` = 50, 곧 매크로 50이다.
2. `1C`: Type 28. 이 레코드가 Macro 오브젝트라는 뜻이다.
3. `08 00`: 뒤따를 바이트 수 8. 명령 패킷 하나(8바이트)가 이어진다.
4. `AD 00 00 02 00`: Change Active Mask(`AD`), Working Set `0x0000`, 새 Active Mask `0x0002`. 이 명령 자체는 5바이트다.
5. `FF FF FF`: 패킷을 8바이트로 맞추는 채움 값이다.

규칙을 정리하면 다음과 같다.

- 매크로에는 Working Set 명령만 담을 수 있다.
- Macro Object ID는 v4 이하에서 0~255, v5부터 0~65534다. v4, v5는 VT 버전이다([29장](/study/isobus/29-vt-basics) 참고).
- 매크로가 풀 안의 오브젝트와 어긋나지 않게(없는 오브젝트를 참조하지 않게) 하는 것은 Working Set의 책임이다.
- Part 6은 8바이트보다 <strong>짧은</strong> 패킷만 언급한다. Change Child Position(9바이트)이나 긴 Change String Value처럼 8바이트를 넘는 패킷을 어떻게 정렬하는지는 명시하지 않는다(확인 필요).

### 매크로로 실행할 수 없는 명령

Part 6의 명령 코드 표에는 명령마다 "매크로에 넣을 수 있는가"가 적혀 있다. 경계를 정리하면 다음과 같다.

| 구분 | Macro 허용 |
|---|---|
| Working Set 명령 대부분 | 허용 |
| ESC(`92`), Delete Object Pool(`B2`), Get Attribute Value(`B9`) | <strong>불가</strong> |
| 모든 응답(response) | 불가 |
| Working Set 명령이 아닌 VT 메시지 전부(풀 전송, Identify VT를 포함한 기술 데이터, 비휘발성 메모리, 상태, 활성화 메시지, AUX) | 불가 |

Part 6이 이유를 적지는 않는다. Get Attribute Value는 응답으로 값을 받는 것이 목적인데, Macro 안의 명령은 응답을 만들지 않으니(4절) 넣을 의미가 없다. Delete Object Pool은 실행 중인 매크로 자신을 담은 풀을 지우게 된다. 두 경우 모두 이런 이유로 보인다(추론). 상태 메시지(VT Status 같은 메시지)는 Part 6이 "오브젝트 풀의 일부가 아니며 Macro에 쓸 수 없다"고 직접 적어 두었다.

<small>근거: ISO 11783-6 4.6.11.4, B.16, Table A.5, G.1</small>

## 3. 이벤트에 매크로 연결하기

매크로는 혼자서는 실행되지 않는다. 어떤 오브젝트의 어떤 이벤트에 연결해 두어야 그 이벤트가 일어날 때 실행된다. 이 절은 그 연결을 오브젝트 레코드 안에 바이트로 적는 두 가지 형식을 본다.

많은 오브젝트가 "이벤트 + 매크로" 쌍의 목록을 선택적으로 가진다. 쌍의 인코딩은 버전에 따라 다르다.

| 형식 | 바이트 | 범위 |
|---|---|---|
| 8비트 참조(v4 이하, v5에서도 사용 가능) | Event ID, Macro ID | Event ID 0~254, Macro ID 0~255 |
| 16비트 참조(v5부터) | `FF`, Macro ID 하위, Event ID, Macro ID 상위 | Macro ID 0~65534 |

16비트 참조는 2바이트 쌍 두 개를 이어 붙인다. 첫 바이트의 Event ID 255는 실제 이벤트가 아니라 "확장 참조가 이어진다"는 표시다. Part 6의 이벤트 번호 표에서 255의 이름이 Use Extended Macro Reference(확장 매크로 참조 사용)다. 2바이트씩 끊어 읽는 구조가 v4 이하 형식과 같아 하위 호환이 된다.

자주 쓰는 Event ID만 골라 보면 다음과 같다.

| Event ID | 이벤트 | 일어나는 때 |
|---|---|---|
| 3 | On Show | 오브젝트가 화면에 보이게 될 때 |
| 4 | On Hide | 오브젝트가 화면에서 사라질 때 |
| 16 | On Change Value | Change Numeric Value나 Change String Value 명령을 받았을 때 |
| 19 | On Input Field Selection | 입력 필드·Key·Button이 포커스를 받을 때 |
| 20 | On Input Field Deselection | 입력 필드·Key·Button이 포커스를 잃을 때 |
| 24 | On Key Press | Soft Key나 Button이 눌릴 때 |
| 25 | On Key Release | Soft Key나 Button에서 손을 뗄 때 |
| 27, 28 | On pointing event press, release(v5부터) | 포인팅 이벤트를 만드는 영역을 누를 때와 뗄 때 |

36장 XML의 Button 20은 On Key Press 이벤트(Event ID 24 = `0x18`)에 매크로 50을 걸었다. 이것을 8비트 참조로 쓰면 `18 32`다. Macro ID가 300(`0x012C`)이면 255를 넘으므로 16비트 참조가 필요하고, `FF 2C 18 01`이 된다. 2절 그림의 위쪽 두 줄이 이 두 형식이다. 16비트 참조를 한 바이트씩 읽으면 다음과 같다.

1. `FF`: 확장 참조 표시(Use Extended Macro Reference)
2. `2C`: Macro ID 하위 바이트
3. `18`: Event ID 24(On Key Press)
4. `01`: Macro ID 상위 바이트. 하위 바이트와 합치면 `0x012C` = 300이다.

구현할 때 두 가지를 조심해야 한다.

- 오브젝트 레코드의 "Number of macros to follow(뒤따르는 매크로 참조 수)" 필드에서 16비트 참조 하나는 <strong>참조 2개로 센다</strong>. 2바이트 쌍 두 개로 이뤄졌기 때문이다. [33장](/study/isobus/33-vt-object-records)의 Alarm Mask 레코드 예가 이 경우다. 개수를 "매크로 수"로 세면 레코드 길이 계산이 어긋나 풀 파싱이 실패한다.
- 같은 이벤트를 목록에 여러 번 나열해도 된다. VT는 목록에 나온 순서대로 실행한다. Part 6의 예처럼 Soft Key 하나가 마스크 전환 매크로와 소리 매크로를 함께 부를 수 있다.

Event ID 중 On pointing event press(27)·release(28)는 v5부터 정의된다. v4 이하에서는 27~239가 예약, 240~254가 제조사 고유, 255가 예약이다. v5부터는 29~239가 예약이고 255가 확장 참조 표시다. 예약은 "나중을 위해 비워 둔 번호"라서 지금은 쓰면 안 된다는 뜻이다. 제조사 고유 이벤트는 제조사가 다른 ECU와 VT 사이에서 쓰지 않는 것이 권고다. 전체 Event ID 표는 [ISO 11783-6 정리 부록](/study/isobus/appendix-iso-part06)의 이벤트 타입 항목에 있다.

<small>근거: ISO 11783-6 4.6.22.1~4.6.22.3, Table A.3, Table B.6</small>

## 4. 매크로가 실행되는 규칙

매크로를 걸어 두었다면 언제, 어떤 순서로 실행되는지 알아야 화면이 예상대로 움직인다. 이 절은 실행 시점과 실행 순서를 보고, 매크로와 Working Set이 같은 오브젝트를 바꿀 때 생기는 문제를 본다.

### 언제 실행되는가

매크로는 "값이 바뀌었을 때"가 아니라 <strong>명령이 유효한 명령으로 받아들여졌을 때</strong> 실행된다. 그래서 직관과 다른 경우가 생긴다. Part 6이 예로 든 경우는 다음과 같다.

- 이미 같은 값인 오브젝트에 같은 값으로 Change Numeric Value를 보내도 On Change Value 매크로가 실행된다.
- 이미 숨겨진 Container에 Hide를 보내도 On Hide 매크로가 실행된다.
- 무효 값을 담은 명령은 거부되고 매크로도 실행되지 않는다.

### 어떤 순서로 실행되는가

실행 순서 규칙은 다음과 같다. 아래에서 이벤트 큐는 처리할 일을 들어온 순서대로 줄 세워 두는 대기열을 말한다.

- 매크로가 일으킨 이벤트가 다른 매크로를 부르면, 지금 매크로를 끝까지 실행한 뒤에 다음 매크로를 시작한다. 매크로는 트리거된 순서대로 실행된다.
- 예외는 Execute Macro·Execute Extended Macro다. 매크로 안에서 이 명령을 만나면 그 매크로를 <strong>함수 호출처럼 즉시</strong> 실행하고, 끝나면 남은 명령을 이어 간다. 프로그램에서 함수를 부르면 그 함수를 끝까지 실행한 뒤 부른 자리로 돌아오는 것과 같다. 이벤트 큐 뒤에 붙이면 잘못된 구현이다.
- 명령 실행으로 트리거된 매크로는 다음 버스 명령을 시작하기 전에 끝나야 한다. 매크로가 길면 그만큼 다음 명령의 응답이 늦어진다(추론).
- 매크로 안의 명령에는 응답을 보내지 않는다. 다만 명령의 효과로 생기는 다른 메시지는 나간다. 매크로 안의 Change Active Mask는 Change Active Mask response 없이 VT Status만 보낸다.
- 순환 참조는 금지다. 매크로가 자기를 다시 부르는 이벤트를 일으키면 무한 루프가 되어 모든 Working Set에 대해 VT가 멈출 수 있다.

즉시 실행 규칙은 결과로 차이가 드러난다. Input Number `0x0028`에 대해 매크로 A = [Execute Macro B, Change Numeric Value(`0x0028`) = 4], 매크로 B = [Change Numeric Value(`0x0028`) = 2]라고 하자. 올바른 VT는 B를 먼저 끝내므로 2 → 4 순서가 되어 최종값이 <strong>4</strong>다. B를 큐 뒤에 붙이는 잘못된 VT는 4 → 2 순서가 되어 최종값이 2다. VT 에뮬레이터(실제 VT 대신 PC에서 VT처럼 동작하는 프로그램)를 검증할 때 쓰기 좋은 테스트다.

![매크로 A가 Execute Macro B를 만났을 때, 올바른 VT는 B를 그 자리에서 실행해 값이 2를 거쳐 최종 4가 되고, 잘못된 VT는 B를 큐 뒤에 붙여 값이 4를 거쳐 최종 2가 되는 과정 비교](/images/study-isobus/38-macro-call-order-light.png)
![매크로 A가 Execute Macro B를 만났을 때, 올바른 VT는 B를 그 자리에서 실행해 값이 2를 거쳐 최종 4가 되고, 잘못된 VT는 B를 큐 뒤에 붙여 값이 4를 거쳐 최종 2가 되는 과정 비교](/images/study-isobus/38-macro-call-order-dark.png)

::: warning 같은 오브젝트를 매크로와 Working Set이 함께 바꾸지 않는다
Part 6은 Working Set과 매크로가 같은 오브젝트를 바꾸면 경합이 생길 수 있다고 경고하고 두 예를 든다. 경합(race condition)은 두 쪽이 같은 대상을 거의 동시에 바꿔서, 어느 쪽이 나중에 처리되느냐에 따라 결과가 달라지는 상황이다.

- Input String에 "On Input Field Deselection 때 값을 지우는" 매크로가 있다. 길이가 긴 Input String에 운전자가 값을 넣고 ENTER를 누르면 VT는 값을 TP(8바이트보다 긴 데이터를 여러 프레임으로 나눠 보내는 방식, [15장](/study/isobus/15-tp-bam-cmdt))로 보낸다. 그 직후 운전자가 다른 필드로 이동하면 매크로가 값을 지운다. Working Set은 TP 데이터와 Deselect 메시지를 비동기로 받으므로 결과가 타이밍에 따라 달라진다.
- Button의 On Key Press 매크로가 Data Mask를 바꾸고, 새 마스크의 On Show 매크로가 Input List 값을 초기화한다. 한편 Working Set도 Button Activation을 받고 같은 Input List에 Change Numeric Value를 보낸다. 최종값은 어느 쪽이 나중에 처리되느냐에 달린다.

오브젝트마다 값을 쓰는 주체를 하나(매크로 또는 Working Set)로 정해 두는 것이 가장 단순한 회피책이다(추론).
:::

<small>근거: ISO 11783-6 4.6.11.4, 4.6.22.1</small>

## 5. 매크로 번호 넓히기: Extended Macro (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

v5는 매크로 공간을 16비트로 넓혔다. 묶어 보면 세 가지가 함께 바뀌었다.

- Macro Object ID: 0~255 → 0~65534
- 이벤트 참조: 16비트 참조 형식 추가(3절)
- 직접 실행: Execute Extended Macro(`BC`, Macro ID 2바이트) 추가

Execute Macro(`BE`)는 v5 이후에도 ID가 1바이트라서 255를 넘는 매크로는 부를 수 없다. VT 버전보다 높은 버전에서 생긴 메시지는 그 VT에 보내면 안 된다. 그러므로 v4 VT에서도 돌아가야 하는 풀은 Macro ID를 255 이하로 유지하고 8비트 참조만 쓰는 편이 안전하다(추론).

아래 코드는 2~3절의 바이트를 직접 만들어 보고 맞는지 확인한다. 주석의 B.16, 4.6.22.1 같은 번호는 Part 6의 조항 번호라서 읽지 않아도 된다. 주석의 "§3의 매크로 50"은 36장에서 본 매크로 50이다.

::: details 매크로 레코드·참조 인코딩 검산 (Python)
```python
def le(v, n):
    return list(v.to_bytes(n, "little"))

def hx(b):
    return " ".join(f"{x:02X}" for x in b)

def packet(cmd):
    assert len(cmd) <= 8
    return cmd + [0xFF] * (8 - len(cmd))       # B.16: 8바이트보다 짧으면 FF로 채운다

def macro_record(macro_id, commands):
    body = [b for c in commands for b in packet(c)]
    return le(macro_id, 2) + [28] + le(len(body), 2) + body

# §3의 매크로 50: Change Active Mask(WS 0 -> Data Mask 2)
m50 = macro_record(50, [[0xAD] + le(0, 2) + le(2, 2)])
assert hx(m50) == "32 00 1C 08 00 AD 00 00 02 00 FF FF FF"

# 짧은 Change String Value("OK")도 패킷 하나는 8바이트다
m60 = macro_record(60, [[0xB3] + le(0x0014, 2) + le(2, 2) + list(b"OK"),
                        [0xA0] + le(0x003C, 2) + [1]])
assert len(m60) == 5 + 16 and m60[3:5] == [16, 0]

def macro_refs(refs, version):
    out = []
    for event_id, macro_id in refs:
        if macro_id <= 255:
            out += [event_id, macro_id]                                   # 8비트 참조
        else:
            assert version >= 5, "v4 이하는 Macro ID 0~255만 쓸 수 있다"
            out += [0xFF, macro_id & 0xFF, event_id, macro_id >> 8]       # 16비트 참조
    return out

ON_KEY_PRESS, ON_HIDE = 24, 4
assert hx(macro_refs([(ON_KEY_PRESS, 50)], 4)) == "18 32"
assert hx(macro_refs([(ON_KEY_PRESS, 300)], 5)) == "FF 2C 18 01"
# 같은 이벤트를 두 번 나열해도 된다(4.6.22.1 NOTE). 순서대로 실행된다
assert hx(macro_refs([(ON_KEY_PRESS, 50), (ON_KEY_PRESS, 300)], 5)) == "18 32 FF 2C 18 01"

def parse_refs(data):
    i, out = 0, []
    while i < len(data):
        if data[i] == 0xFF:
            out.append((data[i + 2], data[i + 1] | data[i + 3] << 8))
            i += 4
        else:
            out.append((data[i], data[i + 1]))
            i += 2
    return out

assert parse_refs([0x18, 0x32, 0xFF, 0x2C, 0x18, 0x01]) == [(24, 50), (24, 300)]
print("block B: OK")
```
:::

실행하면 모든 `assert`가 통과하고 마지막 줄에 `block B: OK`가 찍힌다. `macro_record`는 명령마다 `FF`를 채워 8바이트 패킷으로 만든 뒤 머리(ID, Type, 바이트 수)를 붙인다. `m60`처럼 명령이 두 개면 뒤따를 바이트 수가 16이 된다. `macro_refs`는 Macro ID가 255 이하면 8비트 참조, 넘으면 16비트 참조를 만들고, `parse_refs`는 첫 바이트가 `FF`인지 보고 4바이트 또는 2바이트씩 끊어 읽는다.

<small>근거: ISO 11783-6 4.6.2, 4.6.11.4, 4.6.22.3, F.62</small>

## 6. 운전자 입력 수단과 두 가지 편집 방식

이제 매크로에서 운전자 입력으로 넘어간다. 36장의 "운전자 조작 따라가기"에서 입력 필드 하나를 열고, 값을 넣고, 닫는 흐름을 봤다. 6~8절은 그 뒤에 있는 규칙을 본다. VT가 어떤 입력 수단을 갖추는지, 입력 중에는 어떤 상태에 있는지, Working Set의 명령이 운전자 입력과 겹치면 어떻게 되는지다.

### 다섯 가지 입력 수단과 버스에 보이는 것

VT는 다섯 가지 입력·제어 수단을 갖춰야 한다. 구현자에게 중요한 것은 "어느 수단이 버스에 무엇을 남기는가"다. 작업기는 버스에 나타나는 메시지만 볼 수 있기 때문이다.

| 수단 | 하는 일 | 버스에 보이는 것 |
|---|---|---|
| Soft | Soft Key Mask에 따라 라벨이 바뀌는 키 | Soft Key Activation |
| Navigation | active Data Mask 안에서 입력 필드·Button 선택 | 키 자체는 안 보인다. 결과만 VT Select Input Object로 나간다 |
| Data Input | 입력 필드 값 입력·편집 | 키 자체는 안 보인다. 결과만 VT Change Numeric/String Value, VT ESC로 나간다 |
| Control | Working Set 전환, 알람 확인(ACK) | Working Set 전환은 VT Status 변화로, ACK는 key code 0의 Soft Key Activation으로 |
| Auxiliary Input | AUX 입력으로 기능 제어 | AUX 전용 메시지([40장](/study/isobus/40-vt-aux)) |

Navigation·Data Input 키는 VT 고유 영역(VT 제조사가 알아서 정하는 영역)이라 키 활성화 정보를 Working Set에 보내지 않는다. Control 수단 중에서도 ACK(Acknowledge, 운전자가 경보를 확인했다는 표시)만 키 정보를 보낸다. Working Set 선택 수단은 둥근 화살표 세 개 같은 그림으로 표시하는 것이 권고다.

### editing과 real-time editing

Data Input에는 두 방식이 있다. 계산기에서 숫자를 다 누른 뒤 "="를 눌러야 결과가 나오는 것이 editing이고, 볼륨 다이얼을 돌리는 대로 소리가 바로 바뀌는 것이 real-time editing이다.

<strong>Editing</strong>은 운전자가 VT 고유 방식(팝업 키패드 등)으로 새 값을 조합하는 동안 Working Set에 아무것도 알리지 않는 방식이다. ENTER 수단과 ESC 수단을 반드시 제공해야 한다. 두 수단은 상시 키여도 되고 입력 중에만 나타나도 된다. ENTER면 값 메시지가 나가고, ESC면 VT ESC message가 나간다. Working Set이 ESC 명령을 보낸 경우에는 ESC response로 답한다.

<strong>Real-time editing</strong>은 Input Number·Input List가 포커스를 가진 채 열려 있는 동안 값이 바뀔 때마다 주기적으로 Working Set에 보내는 방식이다. Input Number의 Options 2 속성, Input List의 Options 속성에 있는 Bit 1(real time editing, v4부터)로 켠다. 규칙은 다음과 같다.

- VT Change Numeric Value message는 <strong>5 Hz</strong>로 제한된다. 초당 5번, 곧 200 ms에 한 번까지라는 뜻이다.
- 보낸 값 하나하나가 ENTER를 누른 것과 같은 완결 트랜잭션이다. ESC로 되돌릴 수 없다.
- 증가 단위가 균일할 필요는 없지만 어떤 값이든 설정할 수 있어야 한다. 빠르게 넓은 범위를 움직인 뒤 미세 조정하는 방식도 된다.
- real-time editing 중에 ESC를 누르면, VT는 화면 값이 마지막으로 보낸 값과 같도록 보장해야 한다. 동기화를 위해 VT ESC message나 ESC response 전에 최종 값을 한 번 더 보낼 수 있다.
- ISO 15077(농업용 트랙터와 자주식 기계의 조작 장치가 지켜야 할 조작력, 움직임, 위치를 정한 표준)의 조작 장치 요구사항을 만족해야 한다.

예를 들어 운전자가 다이얼로 목표 살포량을 100에서 140으로 1초에 걸쳐 돌리면, 5 Hz 제한 때문에 5개 안팎의 값(예: 108, 116, 125, 133, 140)이 각각 확정값으로 들어온다. 이어서 ESC를 눌러도 값은 100으로 돌아가지 않고 140으로 남는다. 그래서 Working Set은 real-time 값을 "미리보기"가 아니라 "적용할 값"으로 다뤄야 한다. 데이터 입력 중에도 VT Status는 active Working Set과, 입력 중인 오브젝트를 담은 active mask를 계속 가리킨다.

두 방식을 나란히 놓으면 다음과 같다.

| 구분 | editing | real-time editing |
|---|---|---|
| 값이 Working Set에 가는 때 | ENTER를 누를 때 한 번 | 값이 바뀔 때마다(최대 5 Hz) |
| ESC를 누르면 | 입력이 취소되고 VT ESC message가 간다 | 이미 보낸 값은 그대로 남는다 |
| 켜는 방법 | 따로 켜지 않아도 되는 기본 방식 | Options 속성의 Bit 1(v4부터) |

<small>근거: ISO 11783-6 4.2, B.8.4, B.8.5</small>

## 7. 입력 상태 기계: Navigating과 Data input

VT가 입력을 처리하는 방식은 "지금 어떤 상태인가"와 "무엇을 받으면 어느 상태로 가는가"로 정리할 수 있다. 이런 정리를 상태 기계(state machine)라고 한다. 이 절은 VT 입력의 두 상태와, 입력 중에 Working Set이 화면을 바꿀 때 오가는 메시지를 본다.

서류 양식을 채우는 사람에 빗대면, Navigating은 펜을 들고 어느 칸을 채울지 고르는 중이고 Data input은 한 칸에 글씨를 쓰는 중이다. enabled이면서 보이는 입력 오브젝트나 Button이 있는 Data Mask를 표시하는 동안, VT는 항상 <strong>Navigating</strong>과 <strong>Data input</strong> 중 한 상태에 있다. Button이 포커스를 가진 동안은 Data input이 될 수 없다.

운전자가 포커스를 옮기거나 입력을 열고 닫으면, VT는 VT Select Input Object 메시지(`03`)로 Working Set에 알린다. 36장에서 본 대로 이 메시지는 Byte 2~3에 Object ID, Byte 4에 선택 여부(1 = 선택, 0 = 해제), Byte 5 Bit 0에 "입력용으로 열림" 여부를 싣는다. Working Set이 Select Input Object 명령으로 직접 바꾼 포커스는 이 메시지로 알리지 않으므로, 그 경우는 명령의 응답으로 상태를 파악한다(37장).

![운전자 입력 상태 기계: Navigating에서 입력용으로 열기나 Select Input Object(Byte 4 = 00)로 Data input에 들어가고, ENTER·ESC·Change Active Mask·Select Active Working Set·부모 Container 숨김·Pool 갱신·Pointer 변경으로 Navigating에 돌아오며, 각 상태 안에서 처리되는 명령과 오류 응답을 함께 보인 그림](/images/study-isobus/17-input-state-machine-light.png)
![운전자 입력 상태 기계: Navigating에서 입력용으로 열기나 Select Input Object(Byte 4 = 00)로 Data input에 들어가고, ENTER·ESC·Change Active Mask·Select Active Working Set·부모 Container 숨김·Pool 갱신·Pointer 변경으로 Navigating에 돌아오며, 각 상태 안에서 처리되는 명령과 오류 응답을 함께 보인 그림](/images/study-isobus/17-input-state-machine-dark.png)

그림 읽는 법: 가운데 두 상자가 상태다. 청록 화살표는 Navigating에서 Data input으로 들어가는 길이고, 주황 화살표는 Data input에서 Navigating으로 돌아오는 길이다. 위쪽 상자 두 개는 상태가 바뀌지 않고 그 자리에서 처리되는 일이고, 왼쪽 아래 회색 화살표는 새 active Data Mask가 선택되면 Navigating으로 돌아간다는 뜻이다. 청록 화살표의 "Select Input Object(Byte 4 = 00)"는 Working Set이 보내는 명령으로, Byte 4가 `00`이면 "입력용으로 열기"다(37장). 그림의 WS는 Working Set의 줄임이다.

그림은 Part 6의 입력 상태 표(상태와 받은 명령의 조합마다 VT가 할 일과 보낼 메시지를 적은 큰 표)를 상태 기계로 줄인 것이다. 전체 표는 [ISO 11783-6 정리 부록](/study/isobus/appendix-iso-part06)의 운전자 입력 항목에 있다. 구현자가 알아야 할 규칙을 덧붙인다.

- 입력 상태 표가 나열한 응답 메시지의 <strong>순서는 요구사항이 아니다</strong>. Working Set Master는 어떤 순서로 와도 처리하도록 설계해야 한다.
- 새 active Data Mask가 선택되면 상태는 Navigating으로 리셋된다. Alarm Mask로 바뀔 때는 VT가 입력 상태를 기억했다가 같은 Data Mask로 돌아오면 복원할 수 있다. 이렇게 구현했는데 다른 Data Mask로 돌아오면, 일반적인 마스크 변경처럼 해당 메시지를 보내야 한다.
- 처음 포커스를 둘 곳과 탭 순서(다음 칸으로 옮겨 가는 순서)는 VT 고유다. 다만 부모 안에서 입력 오브젝트를 정의한 순서가 탭 순서가 될 수 있다는 점을 Working Set이 알아 둬야 한다.
- 로터리 다이얼처럼 포커스가 빠르게 지나가면, VT는 지나친 오브젝트마다 VT Select Input Object를 보내지 않아도 된다. 포커스를 잃은 오브젝트와 최종적으로 얻은 오브젝트에만 보내도 된다.
- 폭·높이가 0이거나, 다른 오브젝트에 완전히 덮였거나, 부모의 클리핑 영역 밖에 있는 입력 오브젝트도 "보이는" 것으로 간주한다. 이런 배치는 터치로 활성화할 수 없을 수 있어 권고하지 않는다. 필요할 때 enable/disable하는 편이 탐색 동작을 예측하기 쉽다.
- disabled 입력 오브젝트는 표시해야 한다. 표시 방법은 VT 고유지만 오브젝트의 폭·높이를 벗어나면 안 되고 내용은 읽을 수 있어야 한다.
- Data input 중에 그 오브젝트의 속성이 바뀌어도 입력 중인 값에는 영향을 주지 않아야 한다. 예를 들어 Input Number의 Scale을 바꿔도 입력 중에 보이는 값이 바뀌면 안 된다.
- v3 이하 VT는 VT Select Input Object로 Button·Key 선택을 알리지 않는다.
- On Input Field Selection·Deselection 이벤트는 VT Select Input Object 메시지의 Byte 4(선택 여부)가 바뀔 때만 일어난다. 이미 포커스를 가진 오브젝트를 열고 닫는 것(Byte 5 변화)으로는 일어나지 않는다.

### 예: 입력 중에 Working Set이 마스크를 바꾸면

36장의 설정 화면(Data Mask `0x0002`)에서 운전자가 Input Number `0x0028`을 편집하고 있다. 이때 작업기가 자기 로직에 따라 작업 화면(Data Mask `0x0001`)으로 돌아가는 Change Active Mask를 보낸다고 하자. 입력 상태 표에서 "Data input 상태에서 Change Active Mask를 받은 경우"를 보면, VT는 입력을 중단하고 Navigating으로 돌아간다.

Working Set과 VT가 모두 v6인 조합이라고 하자. TAN(Transaction Number, 활성화 메시지와 그 응답을 짝짓는 4비트 번호)은 36장 예에서 5까지 썼으니 6부터 이어 쓴다. Data Mask `0x0001`의 Soft Key Mask는 `0x0010`이라고 가정한다. 표의 ECU는 작업기 Working Set이고, "VT→전역"은 특정 상대가 아니라 버스 전체에 보낸다는 뜻이다.

| 순서 | 방향 | 데이터 | 의미 |
|---|---|---|---|
| 1 | ECU→VT | `AD 00 00 01 00 FF FF FF` | Change Active Mask → `0x0001` |
| 2 | VT→ECU | `04 28 00 00 FF FF FF 6F` | VT ESC: `0x0028` 입력 중단, 오류 0, TAN 6 |
| 3 | ECU→VT | `04 28 00 FF FF FF FF 6F` | VT ESC response(Byte 4~7 예약, TAN 반향) |
| 4 | VT→ECU | `03 28 00 00 00 FF FF 7F` | VT Select Input Object: 선택 해제, TAN 7 |
| 5 | ECU→VT | `03 28 00 00 00 FF FF 7F` | 응답 |
| 6 | VT→ECU | `AD 01 00 00 FF FF FF FF` | Change Active Mask response: 새 마스크 `0x0001`, 오류 0 |
| 7 | VT→전역 | `FE 81 01 00 10 00 00 FF` | VT Status: Data Mask `0x0001`, Soft Key Mask `0x0010` |

두 줄을 바이트 단위로 풀어 본다. 니블(nibble)은 4비트, 곧 16진수 한 자리다.

- 2번 `04 28 00 00 FF FF FF 6F`: `04`는 VT ESC message, `28 00`은 Object ID `0x0028`, 다음 `00`은 오류 코드 0이다. `FF FF FF`는 채움이고, 마지막 `6F`의 상위 니블 `6`이 TAN 6, 하위 니블 `F`는 채움이다.
- 7번 `FE 81 01 00 10 00 00 FF`: `FE`는 VT Status, `81`은 VT를 지금 차지한 Working Set의 주소다. `01 00`은 보이는 Data Mask `0x0001`, `10 00`은 Soft Key Mask `0x0010`이다. 그다음 `00`은 바쁨 표시(busy 비트)가 모두 0이라는 뜻이고, `FF`는 실행 중인 명령이 없다는 뜻이다(VT Status의 구성은 37장 참고).

새 마스크에 포커스를 받을 오브젝트가 있으면 VT Select Input Object(선택)가 하나 더 붙는다. 2~7의 순서는 VT마다 다를 수 있다.

이 흐름에서 운전자가 입력하던 값은 VT ESC와 함께 버려지고, VT Change Numeric Value는 오지 않는다. 운전자 입력을 존중하려면 Working Set은 VT Select Input Object 메시지의 Byte 5 Bit 0(입력용으로 열림)을 추적하다가, 입력이 열려 있는 동안에는 마스크 전환을 미루는 편이 낫다(추론). 같은 결과는 부모 Container가 숨겨지거나, Pool Update가 그 오브젝트를 바꾸거나, 그 오브젝트를 가리키던 Object Pointer가 다른 것을 가리키게 될 때도 생긴다.

<small>근거: ISO 11783-6 4.6.17, H.8, H.10</small>

## 8. 운전자와 Working Set이 같은 오브젝트를 바꿀 때 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

운전자와 Working Set이 같은 오브젝트를 동시에 바꾸면 경합(race condition)이 생긴다. Working Set은 VT Select Input Object 메시지로 오브젝트가 입력용으로 열렸는지 알 수 있다. 하지만 송수신 FIFO(먼저 들어온 메시지를 먼저 내보내는 대기열) 같은 처리 지연 때문에, 운전자가 막 입력을 시작한 순간에 명령이 도착할 수 있다. VT에서 온 값을 검증하는 것은 Working Set의 책임이다.

v5 이하는 요구사항이 일관되지 않아, 일부 명령이 "object in use(오브젝트 사용 중)" 오류를 돌려줬다. v6에서 이 오류는 deprecated(더 이상 쓰지 않기로 하고 예약으로 돌림)되었다. v6부터는 오브젝트가 사용 중이어도 속성을 바꿀 수 있고, VT는 바로 적용하거나 적용할 수 있을 때까지 캐시해 둔다. Part 6에 예가 있다. 팝업 키패드로 편집 중인 Input Number의 배경색을 Working Set이 바꾸면, VT는 오류 없이 받아야 한다. 편집이 끝나 Input Number가 다시 보일 때 바뀐 색이 보이면 된다.

허용은 되지만 사용 중에는 바꾸지 않는 것이 권고인 속성도 있다.

- Key·Button의 Key code
- 입력 필드의 Value와 Variable 참조
- Input String의 Input attributes·Extended Input attributes, 그리고 Input String이 참조하는 String Variable
- Input Number의 Minimum·Maximum·Offset·Scale
- 입력 오브젝트가 참조하는 Font Attributes의 font type
- Input Number·Input List가 참조하는 Number Variable

팝업 다이얼로그처럼 원자적이지 않은(편집이 한 번에 끝나지 않고 여러 단계에 걸치는) 편집 수단을 쓰는 VT는 이 속성들을 편집 시작 시점에 한 묶음으로 편집 수단에 넘기고, 런타임 변경은 편집이 끝날 때 적용해야 한다. Part 6의 각주는 또 v5 이하에서는 VT Change Numeric Value의 응답이 선택이라, VT 화면과 Working Set 내부 값이 어긋나는 경합이 생길 수 있었다고 설명한다. v6가 응답을 필수로 바꾼 배경 중 하나로 볼 수 있다(추론).

<small>근거: ISO 11783-6 4.6.10.2, H.8</small>

## 9. Soft Key·Button을 누르고 있는 동안

36장에서 활성화 코드(0 released, 1 pressed, 2 held, 3 aborted)와 TAN의 기본을 봤다. 이 절은 그 위에서 경계 조건을 본다. 키를 누르고 있는 동안 화면이 바뀌면 어떻게 되는지, 응답이 유실되면 어떻게 되는지다.

### momentary 수단의 공통 규칙

Button, Key, 터치, AUX 입력처럼 운전자가 누르는 동안만 ON이고 놓으면 저절로 OFF로 돌아가는 수단을 Part 6은 momentary(비래치) 수단이라 부른다. 초인종 버튼처럼 손을 떼면 바로 꺼지는 수단이다. 공통 규칙은 세 가지다.

1. 누르면 OFF→ON 전이를 보고한다.
2. 계속 누르고 있으면 Held를 보고하고, 놓을 때까지 반복한다.
3. 놓으면 ON/Held→OFF 전이를 보고한다.

반복 주기는 수단마다 정의에 있다. 같은 틀이 메시지마다 다른 이름으로 나타난다. 표의 "끊김 판정"은 반복되던 held 메시지가 끊겼을 때 받는 쪽이 "손을 뗐다"고 간주하는 기준이다. shall은 반드시 지켜야 하는 규칙, should는 지키기를 권하는 규칙이다.

| 수단 | ON | Held(반복 주기) | OFF | 끊김 판정 |
|---|---|---|---|---|
| Soft Key Activation | 1 pressed | 2 still held(200 ms) | 0 released, 3 aborted(v4부터) | 간격 300 ms 초과 시 released로 처리(should) |
| Button Activation | 1 pressed/latched | 2 still held(200 ms, 래치 버튼은 반복 없음) | 0 released/unlatched, 3 aborted(v4부터) | 비래치 버튼만 300 ms 규칙 |
| Pointing Event | 1 Pressed | 2 Held(200 ms) | 0 Released | 300 ms(v4부터, should) |
| AUX Type 2 non-latching Boolean | 1 Momentary | 2 held(200 ms) | 0 Off | 300 ms 초과 시 released로 처리(shall) |

예를 들어 200 ms마다 오던 still held가 300 ms 넘게 오지 않으면, Working Set은 운전자가 손을 뗀 것으로 처리한다. AUX(보조 입력)는 [40장](/study/isobus/40-vt-aux)에서 본다.

### 키가 화면에서 사라질 때

키를 누르고 있는 동안 화면이 바뀌는 경우를 Part 6은 자세히 정한다.

- Key나 비래치 Button이 활성 상태에서 화면에서 지워지면(Change Active Mask, Change Soft Key Mask, Hide/Show 등), VT는 그 오브젝트에 대해 released를 보낸다. 그 뒤 운전자가 물리적으로 손을 뗄 때까지 그 키를 무시한다.
- 보이는 Data Mask가 바뀌면 이전 마스크에서 눌려 있던 오브젝트에 released를 보내고, 새 마스크에 대해서는 활성화 메시지(Soft Key Activation)를 보내지 않는다.
- Soft Key Mask는 Data/Alarm Mask의 자식으로 간주한다. active Data/Alarm Mask가 바뀌면 새 마스크가 <strong>같은 Soft Key Mask를 쓰더라도</strong> Soft Key Mask가 바뀐 것으로 처리한다. 눌린 Soft Key에 released를 보내고 뗄 때까지 무시하며, Soft Key Mask의 On Hide·On Show 매크로도 실행한다.
- Change Active Mask나 Change Soft Key Mask가 결과적으로 현재 마스크를 바꾸지 않으면, pressed/held/released 상태도 바뀌지 않고 On Hide·On Show 매크로도 실행되지 않는다. v5 이하에서는 이 부분이 잘 정의되지 않아 구현마다 달랐다.
- 눌린 Button이 active mask 안에서 다른 위치로 옮겨지면 활성화 방식에 따라 다르다. 물리 키로 눌렀으면 pressed가 유지된다. 터치나 포인팅으로 눌렀는데 터치 지점에서 벗어나면 released를 보내고, 손을 뗄 때까지 무시한다.
- 터치스크린에서 누른 채 손가락을 오브젝트 밖으로 미끄러뜨리면, 손가락을 추적할 수 있는 VT는 aborted를 보낸다. 이동과 미끄러짐이 겹치면 먼저 일어난 쪽이 우선한다.
- v5부터 ACK 키도 Key·Button과 같은 방식(pressed, held, released)으로 메시지를 보낸다. v4 이하는 정의가 모호해 구현마다 달랐다.
- 전원을 켤 때 이미 눌려 있던 Key·Button은 held로 보고하지 않는다. 운전자에게 진단 메시지를 띄울 이유는 될 수 있다.

Working Set 쪽 함의가 하나 있다. VT가 화면 변화 때문에 만든 released와 운전자가 손을 떼서 나온 released는 코드가 같다(둘 다 0). "뗄 때 실행"하는 기능이 안전에 관련되면, released 직전에 마스크 변화(VT Status, 직전에 보낸 Change Active Mask 응답)가 있었는지를 함께 보고 판단하는 편이 낫다(추론). 운전자가 의도적으로 취소한 경우는 aborted(3)로 구분된다.

### 예: 버튼 홀드와 TAN 재시도

Button `0x0014`(Data Mask `0x0001` 위, key code 1)를 520 ms 동안 눌렀다 뗐다. v6 조합이고, 뗌 메시지의 응답만 유실됐다. 각 메시지의 응답은 5 ms 뒤에 같은 바이트로 오므로 표에서 생략했다.

| 시각 | 데이터(VT→ECU) | 의미 |
|---|---|---|
| 0 ms | `01 01 14 00 01 00 01 1F` | pressed, TAN 1 |
| 200 ms | `01 02 14 00 01 00 01 2F` | still held, TAN 2 |
| 400 ms | `01 02 14 00 01 00 01 3F` | still held, TAN 3 |
| 520 ms | `01 00 14 00 01 00 01 4F` | released, TAN 4 → 응답 유실 |
| 820 ms | `01 00 14 00 01 00 01 4F` | 재시도: 데이터와 TAN 그대로 |

520 ms의 `01 00 14 00 01 00 01 4F`를 풀면 `01`은 Button Activation, `00`은 released, `14 00`은 Button `0x0014`, `01 00`은 부모 Data Mask `0x0001`, `01`은 key code 1이다. 마지막 `4F`의 상위 니블 4가 TAN 4다.

![Button을 520 ms 누르는 동안 0 ms pressed(TAN 1), 200 ms와 400 ms still held(TAN 2, 3), 520 ms released(TAN 4)가 나가고, released의 응답이 유실되어 300 ms 뒤인 820 ms에 같은 데이터와 같은 TAN 4로 재시도하는 시간축](/images/study-isobus/38-button-hold-timeline-light.png)
![Button을 520 ms 누르는 동안 0 ms pressed(TAN 1), 200 ms와 400 ms still held(TAN 2, 3), 520 ms released(TAN 4)가 나가고, released의 응답이 유실되어 300 ms 뒤인 820 ms에 같은 데이터와 같은 TAN 4로 재시도하는 시간축](/images/study-isobus/38-button-hold-timeline-dark.png)

held 메시지는 매번 새 TAN을 받는다. 반면 응답이 없어 다시 보내는 released는 이전 TAN 4를 유지한다. 이 차이가 Working Set에 중요하다. 같은 TAN의 메시지가 또 오면 그것은 새 이벤트가 아니라 재시도다. 응답은 다시 보내되 "뗐을 때의 동작"을 두 번 실행하면 안 된다(추론). Part 6은 TAN을 VT가 메시지-응답 쌍을 맞추는 용도로 설명하지만, Working Set 쪽 중복 제거에도 같은 값을 쓸 수 있다.

<small>근거: ISO 11783-6 4.6.18, 4.6.27, H.1~H.6, J.7.9</small>

## 10. 래칭 버튼과 여러 키 동시 누름

9절의 규칙은 누르는 동안만 켜지는 키에 대한 것이었다. 이 절은 규칙이 달라지는 두 경우를 본다. 눌린 상태로 남는 래칭 버튼과, 여러 키를 한꺼번에 누르는 경우다.

### 래칭 버튼

래칭 버튼은 벽의 전등 스위치처럼 한 번 누르면 켜진 채로 있고, 다시 누르면 꺼진다. Button 오브젝트의 Options 속성에서 Bit 0이 "latchable"이다. 이 속성에 AID 6이 붙어 Change Attribute·Get Attribute Value로 다룰 수 있게 된 것은 v4부터다. AID(Attribute ID)는 속성마다 붙은 번호다([33장](/study/isobus/33-vt-object-records)). 이 비트가 1이면 Button은 다음 활성화까지 눌린 상태로 남는다. Bit 0은 런타임에 Change Attribute로 바꿀 수 없고, 바꾸려 해도 VT가 무시한다. Bit 1은 래치 버튼의 현재 상태(0 = released, 1 = latched)다.

래치 버튼은 메시지 패턴이 다르다.

- 운전자가 누를 때마다 상태가 토글되고, Byte 2가 1(latched) 또는 0(unlatched)으로 온다.
- 반복 전송이 없다. still held(2)가 오지 않으므로 300 ms 끊김 판정도 적용하지 않는다. Part 6은 그 규칙을 비래치 버튼에만 적용한다.
- "활성 상태에서 화면에서 지워지면 released를 보낸다"는 규칙의 대상은 Key와 <strong>비래치</strong> Button뿐이다. 래치 버튼은 숨겨져도 released가 오지 않으므로 래치 상태가 그대로 유지된다고 보는 것이 자연스럽다(Part 6이 직접 적지는 않는다).

Working Set은 Change Attribute로 Options의 Bit 1을 바꿔 래치 상태를 직접 설정할 수 있다. 이때 On Key Press·On Key Release 이벤트(매크로)는 일어나지만, Button Activation message는 운전자가 조작했을 때만 나간다. 현재 래치 상태는 Get Attribute Value(AID 6)로 읽는다.

### 동시 활성화

여러 키를 동시에 누를 수 있는지는 Get Hardware response Byte 4로 알린다. Get Hardware는 VT의 하드웨어 능력을 묻는 기술 데이터 메시지다([30장](/study/isobus/30-vt-display-technical-data)). Bit 4는 물리 Soft Key, Bit 5는 Button의 동시 활성화 지원이다(v4부터).

- 비트가 0이면 VT는 한 번에 하나만, `<no Keys pressed>:<Key pressed>:[<Key held>]:<Key released>:<no Keys pressed>` 순서로만 지원한다. 첫 키가 pressed/held인 동안 눌린 두 번째 키는 무시한다.
- 비트가 1이면 메시지가 겹쳐 나온다. 예: `<Key 1 pressed>:[<Key 1 held>]:<Key 2 pressed>:<Key 1 released>:<Key 2 released>`.

위 순서 표기에서 `:`는 "다음에"를, 대괄호 `[ ]`는 "있을 수도 있음"을 뜻한다. 그래서 Working Set은 "지금 눌린 키 하나"라는 전역 변수 대신 Object ID별 상태 기계로 구현하는 편이 안전하다. 양손 조작 같은 조합 입력이 필요하면 Get Hardware response의 이 비트를 먼저 확인해야 한다(추론).

<small>근거: ISO 11783-6 4.6.18, B.7, D.9, H.4</small>

::: details 원문을 가진 독자를 위한 메모
- 이 장의 "명령 코드 표"는 Part 6 Table A.5(매크로 허용 여부 열 포함), "이벤트 번호 표"는 Table A.3, "입력 상태 표"는 4.6.17의 Table 5다.
- "Working Set 명령"은 Annex F 명령, VT Select Input Object와 VT ESC 같은 활성화 메시지는 Annex H 메시지, AUX 전용 메시지는 Annex J 메시지다.
- 3절의 "Number of macros to follow" 규칙은 각 오브젝트 표(예: Table B.6 Alarm Mask)의 설명에 있다. 4절의 실행 시점 예는 4.6.22.1 EXAMPLE 3·4, 실행 순서 규칙은 4.6.11.4, 경합 경고는 4.6.11.4 CAUTION이다.
:::

::: tip 핵심 정리
- 매크로는 버튼 같은 이벤트에 묶어 둔 VT 명령 목록이다. VT가 작업기를 거치지 않고 바로 실행하므로 화면이 빨리 바뀌고, 매크로 안의 명령에는 응답이 나가지 않는다.
- Macro 레코드는 명령 패킷(8바이트 단위, 짧으면 `FF` 채움)의 목록이다. 이벤트 참조는 8비트(`Event ID, Macro ID`)와 16비트(`FF` 표시로 시작하는 4바이트, 참조 2개로 셈) 두 형식이 있다.
- 매크로는 값이 바뀔 때가 아니라 유효한 명령이 받아들여질 때 실행된다. 매크로 안의 Execute Macro는 그 자리에서 함수처럼 실행된다.
- 입력은 Navigating과 Data input 두 상태로 움직인다. 입력 중 마스크 전환은 VT ESC로 입력을 버린다. real-time editing 값은 ESC로 되돌릴 수 없다.
- 누르고 있는 키는 200 ms마다 held를 보내고, 화면에서 사라지면 VT가 released를 만든다. 응답이 없어 다시 보낸 메시지는 TAN이 같으므로, 같은 TAN이면 재시도로 보고 동작을 두 번 하지 않는다.
:::

::: details 확인 문제
1. (개념) 버튼을 눌러 화면을 바꿀 때, 매크로를 쓰지 않는 경우와 쓰는 경우에 버스를 오가는 메시지는 어떻게 다른가?
2. (인코딩) Macro ID 300을 On Key Press(Event ID 24) 이벤트에 거는 참조 바이트를 쓰라. 이 참조는 레코드의 "Number of macros to follow"에서 몇 개로 세는가?
3. (개념) v6 조합에서 Working Set이 Button Activation `01 00 14 00 01 00 01 4F`를 받고 응답했다. 300 ms 뒤 똑같은 바이트가 다시 왔다. 무슨 일이 일어난 것이고, Working Set은 무엇을 해야 하는가?
4. (장애 진단) 운전자가 설정 화면에서 Input Number를 편집하던 중 작업기가 Change Active Mask를 보냈다. 그 뒤 VT ESC message가 오고, 운전자가 입력하던 값이 사라졌다. 표준상 정상 동작인가? 재발을 막으려면 Working Set을 어떻게 고쳐야 하는가?

**답 가이드**
1. 매크로가 없으면 VT가 Button Activation을 보내고, 작업기가 Change Active Mask 명령을 보내고, VT가 응답한다. 화면은 작업기의 명령이 도착해야 바뀐다. 매크로가 있으면 VT가 매크로 안의 Change Active Mask를 스스로 실행하므로 이 명령과 응답은 버스를 지나지 않고 화면이 바로 바뀐다. Button Activation은 두 경우 모두 작업기에 간다.
2. 300 = `0x012C`이므로 `FF 2C 18 01`이다(`FF` 확장 참조 표시, `2C` Macro ID 하위, `18` Event ID 24, `01` Macro ID 상위). 2바이트 쌍 두 개로 이뤄져 참조 2개로 센다. v5 이상 VT에서만 쓸 수 있다.
3. 같은 데이터가 같은 TAN(4)으로 다시 왔으므로 새 이벤트가 아니라 재시도다. 첫 응답이 VT에 닿지 않아 VT가 300 ms 뒤 다시 보낸 것이다. Working Set은 응답을 다시 보내되, "뗐을 때의 동작"은 다시 실행하지 않는다.
4. 정상 동작이다. 입력 상태 표(7절)에서 Data input 상태의 Change Active Mask는 VT ESC message, VT Select Input Object(해제), Change Active Mask response, VT Status를 거쳐 Navigating으로 돌아가고, 입력 중이던 값은 버려진다. Working Set은 VT Select Input Object의 Byte 5 Bit 0(입력용으로 열림)을 추적해, 입력이 열려 있는 동안 마스크 전환을 미뤄야 한다. 꼭 바꿔야 한다면 입력이 취소된다는 것을 전제로 설계한다.
:::

## 다음 챕터

- 다음: [39장 경보, 소리, 활성화 메시지](/study/isobus/39-vt-alarm-activation)
