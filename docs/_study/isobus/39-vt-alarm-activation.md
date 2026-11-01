---
title: "경보, 소리, 활성화 메시지"
description: "여러 Working Set의 경보가 겹칠 때 VT가 화면과 소리를 정하는 규칙과, VT가 먼저 보내는 활성화 메시지의 TAN, 응답, 오류 통지를 익힌다."
date: 2026-04-13
tags: [ISOBUS, VT, Alarm Mask, Activation, TAN, ISO-11783-6]
prev: /study/isobus/38-vt-macro-input
next: /study/isobus/40-vt-aux
---

# 경보, 소리, 활성화 메시지

::: info 학습 목표
- Alarm Mask의 Priority와 Acoustic signal 속성으로 VT가 경보를 고르는 규칙을 설명할 수 있다.
- 경보를 띄우고, 운전자가 확인(ACK)하고, 경보를 내리는 메시지 순서를 따라갈 수 있다.
- 여러 Working Set의 경보가 겹칠 때 화면과 경보음이 어떻게 바뀌는지 단계별로 추적할 수 있다.
- VT가 먼저 보내는 활성화 메시지마다 TAN의 위치와 응답 내용을 찾아 읽을 수 있다.
- VT Change Active Mask message 같은 오류 통지를 디코딩하고 Working Set이 할 일을 말할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [36장 VT 명령어 기초](/study/isobus/36-vt-commands-basics), [37장 VT 명령 세부와 공통 규칙](/study/isobus/37-vt-command-details), [38장 매크로와 운전자 입력 처리](/study/isobus/38-vt-macro-input)
- 이 장에서 처음 나오는 말
  - Alarm Mask(경보 화면): Working Set이 경보를 보여 줄 때 띄우는 화면 오브젝트. Data Mask 대신 화면을 차지한다.
  - Priority(우선순위): 경보가 얼마나 급한지를 나타내는 속성. 0(High)이 가장 급하다.
  - 활성화 메시지(activation message): 운전자 조작이나 화면 변화를 VT가 먼저 Working Set에 알리는 메시지. Soft Key Activation, VT Change Numeric Value 등이 있다.
  - TAN(Transaction Number): v6에서 활성화 메시지와 그 응답을 짝짓는 4비트 번호.
  - multisound: 여러 Working Set의 소리를 동시에 낼 수 있는 VT의 능력.
:::

병원 응급실은 환자가 온 순서가 아니라 위급한 정도로 진료 순서를 정한다. 트랙터의 VT 화면도 비슷하다. 파종기와 비료 살포기가 동시에 경보를 띄우면, VT는 더 급한 경보부터 보여 주고 소리도 그에 맞춰 정리한다. 이 장의 앞부분(1~4절)은 이 경보 규칙을 보고, 뒷부분(5~10절)은 VT가 먼저 보내는 활성화 메시지 전체를 TAN, 응답, 오류 통지라는 관점에서 정리한다.

## 1. Alarm Mask와 우선순위

36장의 Alarm Mask 예시는 Working Set 하나만 있는 경우였다. 실제 트랙터에는 여러 작업기가 동시에 연결되고, 경보가 겹친다. 이 절은 Alarm Mask가 가진 두 속성과, 여러 경보 가운데 VT가 하나를 고르는 규칙을 본다. VT의 동작 규칙을 정하는 표준 문서는 ISO 11783-6이고, 이 장에서는 줄여서 Part 6이라고 부른다.

Alarm Mask 오브젝트에는 경보 판단에 쓰는 속성이 두 개 있다.

| 속성 | 값 |
|---|---|
| Priority | 0 = High(운전자가 위험하거나 긴급한 기계 이상), 1 = Medium(일반 경보, 기계 이상), 2 = Low(정보) |
| Acoustic signal | 0 = 가장 높은 우선순위의 소리, 1 = 중간, 2 = 가장 낮음, 3 = 소리 없음(silent) |

숫자가 작을수록 우선순위가 높다. 여러 Working Set이 Alarm Mask를 활성화하면 VT는 다음 규칙으로 하나를 고른다. 아래에서 active Working Set은 지금 VT 화면을 차지하고 운전자 입력을 받는 Working Set을 말한다.

- 1차 기준은 Priority 속성, 2차 기준은 활성화된 시간 순서다. 같은 Priority면 VT가 먼저 처리한 쪽이 active mask가 된다.
- 가장 높은 우선순위의 경보는 그 경보를 가진 Working Set이 active mask를 바꿀 때까지 계속 표시된다. 그 Working Set이 더 낮은 경보나 Data Mask로 바꾸면 다음 순위의 Alarm Mask를 처리한다.
- Working Set당 active Alarm Mask는 하나뿐이다.
- v6 조합에서는 선택할 수 없는(Selectable = 0) Working Set도 Change Active Mask로 Alarm Mask를 띄울 수 있다. Selectable은 운전자가 Working Set 전환 수단으로 그 Working Set을 고를 수 있는지를 정하는 속성이다. 이런 Working Set이 경보를 내리려면 Data Mask를 활성화한다. 일반 경보 규칙이 그대로 적용된다.
- 경보 때문에 끊긴 운전자 입력은 모든 Alarm Mask가 확인된 뒤 이어서 할 수 있게 보존해도 된다.
- Alarm Mask에는 속성으로 Soft Key Mask가 연결되고, 경보가 보이는 동안 함께 표시된다.

응급실 비유와 다른 점도 있다. 응급실은 의사가 진료를 마치면 다음 환자로 넘어가지만, VT는 경보를 스스로 내리지 않는다. 경보를 띄운 Working Set이 Change Active Mask로 화면을 바꿔야 다음 경보로 넘어간다(2절).

<small>근거: ISO 11783-6 4.3, 4.6.14, B.3</small>

## 2. 경보를 띄우고 내리는 순서

경보 하나가 처음부터 끝까지 어떤 메시지로 오가는지 본다. 결론부터 말하면, 운전자의 확인(ACK)은 알림일 뿐이고 경보를 내리는 것은 Working Set의 Change Active Mask다.

![작업기 Working Set이 Change Active Mask로 Alarm Mask 0x0003을 띄우고 응답을 받은 뒤, VT가 Alarm Mask와 경보음을 내고 VT Status를 전역으로 보내며, 운전자가 ACK 수단을 누르면 VT가 key code 0인 Soft Key Activation을 보내고, ACK만으로는 경보가 내려가지 않아 Working Set이 Change Active Mask로 Data Mask를 활성화해 경보를 내리는 순서](/images/study-isobus/39-alarm-sequence-light.png)
![작업기 Working Set이 Change Active Mask로 Alarm Mask 0x0003을 띄우고 응답을 받은 뒤, VT가 Alarm Mask와 경보음을 내고 VT Status를 전역으로 보내며, 운전자가 ACK 수단을 누르면 VT가 key code 0인 Soft Key Activation을 보내고, ACK만으로는 경보가 내려가지 않아 Working Set이 Change Active Mask로 Data Mask를 활성화해 경보를 내리는 순서](/images/study-isobus/39-alarm-sequence-dark.png)

그림은 운전자가 ACK한 뒤 Working Set이 Data Mask로 경보를 내리는 가장 흔한 경우다. Part 6이 정한 절차를 그대로 옮기면 다음과 같다. SA(Source Address)는 메시지를 보낸 장치의 주소다.

1. Working Set Master가 Change Active Mask로 Alarm Mask를 활성화한다.
2. VT가 Change Active Mask response로 응답한다.
3. VT가 우선순위에 따라 언젠가 Alarm Mask와 그 Soft Key Mask를 표시한다. 마스크 전환으로 Alarm Mask가 나타나거나 <strong>다시 나타날 때</strong>마다 그 경보의 소리를 낸다. 소리 정리 규칙은 4절에서 본다.
4. VT가 전역 주소로 VT Status message를 보낸다. Alarm Mask가 보이면 Byte 2는 그 Alarm Mask를 가진 Working Set의 SA다.
5. 운전자가 VT 고유의 ACK 수단으로 경보를 확인하면, VT는 key code 0인 Soft Key Activation message를 그 Working Set에 보낸다. 또는 Working Set이 자기 로직에 따라 Change Active Mask로 Data Mask를 활성화해 경보를 내릴 수 있다.
6. ACK가 허용되지 않는 경보라면 Working Set은 ACK를 무시해도 된다. Change Active Mask로 다른 Alarm Mask나 Data Mask로 바꿀 수도 있다.
7. VT가 Change Active Mask response로 응답하고, 3절에서 볼 마스크 전환 규칙에 따라 새 마스크를 표시한다.

Working Set `0x0000`이 Alarm Mask `0x0003`(Soft Key Mask `0x0011`)을 띄우면 다음 세 프레임이 오간다. 표의 ECU는 작업기 Working Set이다.

| 방향 | 데이터 | 의미 |
|---|---|---|
| ECU→VT | `AD 00 00 03 00 FF FF FF` | Change Active Mask → Alarm Mask `0x0003` |
| VT→ECU | `AD 03 00 00 FF FF FF FF` | 응답, 오류 0 |
| VT→전역 | `FE 81 03 00 11 00 00 FF` | VT Status: 소유자 `0x81`, Alarm Mask `0x0003`, Soft Key Mask `0x0011` |

세 번째 줄을 한 바이트씩 풀면 다음과 같다. 2바이트 값은 리틀 엔디언(낮은 자리 바이트가 먼저)이다.

1. `FE`: VT Status message
2. `81`: 지금 보이는 마스크를 가진 Working Set의 SA `0x81`
3. `03 00`: 보이는 마스크 `0x0003`(Alarm Mask)
4. `11 00`: 함께 보이는 Soft Key Mask `0x0011`
5. `00 FF`: 바쁨 표시(busy 비트) 없음, 실행 중인 명령 없음(37장의 VT Status 설명 참고)

::: info ACK 수단과 Working Set이 정의한 "확인" 키
표준의 ACK는 VT가 제공하는 Control 수단이다. ACK는 Soft Key Activation의 Byte 7(key code) = 0으로 구분되고, Byte 5~6에는 보이는 Alarm Mask의 ID가 실린다. 36장 경보 예시의 "확인" 소프트키는 이와 다르다. 그것은 Working Set이 Alarm Mask의 Soft Key Mask에 직접 정의한 Key이고, 1~255 사이의 key code를 가진다. 두 방식 모두 가능하다. 다만 어느 쪽이든 ACK 메시지만으로 경보가 내려가지는 않는다. Working Set이 Change Active Mask로 Data Mask를 활성화해야 경보가 내려간다.
:::

<small>근거: ISO 11783-6 4.2, 4.6.14, G.2, H.2</small>

## 3. 여러 Working Set의 경보가 겹칠 때

마스크가 바뀔 때 VT가 하는 일은 두 가지로 정해진다. "바뀐 방향(Data↔Alarm)"과 "요청한 Working Set이 현재 active인가"다. Part 6은 이 조합마다 VT가 할 일을 마스크 전환 규칙 표로 정리했다. 전체 표는 [ISO 11783-6 정리 부록](/study/isobus/appendix-iso-part06)의 알람 처리 항목에 있다.

Working Set A·B 두 개로 따라가 보자. 처음에는 A가 active이고 A의 Data Mask가 보인다.

| 단계 | 사건 | 적용되는 규칙(바뀐 방향, 요청자) | 결과 |
|---|---|---|---|
| 1 | B(inactive)가 Medium(1) 경보를 띄움 | Data → Alarm, 요청자 ≠ active | 가장 높은 경보이므로 A를 비활성화하고 B를 활성화한다. B의 경보가 보인다 |
| 2 | A(이제 inactive)가 High(0) 경보를 띄움 | Data → Alarm, 요청자 ≠ active | A의 경보가 더 높으므로 B를 비활성화하고 A를 활성화한다. B의 경보음은 끊긴다 |
| 3 | A가 Data Mask로 돌아감 | Alarm → Data, 요청자 = active | 다른 Working Set(B)에 경보가 있으므로 A를 비활성화하고 B를 활성화한다. B의 경보가 <strong>다시 나타나므로 소리도 다시 난다</strong> |
| 4 | B가 Data Mask로 돌아감 | Alarm → Data, 요청자 = active | 남은 경보가 없다. 마지막으로 보인 Data Mask는 A의 것이므로 B를 비활성화하고 A를 활성화한다 |

![Working Set A와 B의 active mask, VT 화면, 경보음을 단계별로 나란히 보인 그림: 처음 A의 Data Mask, 1단계 B의 Medium 경보(B 경보음), 2단계 A의 High 경보(A 경보음, B 소리 끊김), 3단계 B의 경보가 다시 보임(B 경보음 다시), 4단계 A의 Data Mask로 돌아감](/images/study-isobus/39-alarm-overlap-light.png)
![Working Set A와 B의 active mask, VT 화면, 경보음을 단계별로 나란히 보인 그림: 처음 A의 Data Mask, 1단계 B의 Medium 경보(B 경보음), 2단계 A의 High 경보(A 경보음, B 소리 끊김), 3단계 B의 경보가 다시 보임(B 경보음 다시), 4단계 A의 Data Mask로 돌아감](/images/study-isobus/39-alarm-overlap-dark.png)

그림의 위 두 줄은 Working Set마다 자기 active mask가 무엇인지, 맨 아래 줄은 VT 화면에 실제로 보이는 것이다. 주황 테두리가 경보다. B는 1~3단계 내내 경보를 유지하지만, 화면에 보이는 것은 2단계에서 잠시 A의 더 높은 경보로 바뀐다.

4단계 결과가 직관과 다를 수 있다. 경보를 내린 B가 화면을 차지하는 것이 아니라, 경보 전에 보이던 A의 Data Mask로 돌아간다. 마지막으로 보인 Data Mask를 가진 Working Set이 없으면, VT는 표시할 마스크가 없을 때와 같은 화면을 보여 준다. Working Set이 active일 때 Data Mask끼리 바꾸면 그냥 바뀌고, inactive일 때 바꾸면 화면에 변화가 없다(단일 표시 VT 기준). inactive Working Set이 Alarm → Data로 바꿔도 화면 변화는 없다.

<small>근거: ISO 11783-6 4.6.14</small>

## 4. 경보음과 Control Audio Signal

Working Set은 Alarm Mask가 아니어도 Control Audio Signal 명령(37장)으로 비프음을 낼 수 있다. 이 절은 경보 소리와 이 비프음이 부딪힐 때의 규칙을 본다.

- 더 높은 경보가 나타나면 VT는 진행 중인 더 낮은 경보의 소리를 끊는다. 높은 쪽 경보가 소리 없음(silent)이어도 끊는다.
- multisound를 지원하지 않는 VT는 경보 소리가 silent가 아니면 진행 중인 Control Audio Signal 소리도 끊는다. v4부터는 이때 소리를 낸 Working Set에 VT Control Audio Signal Termination message(`0A`)를 보낸다. 반면 낮은 경보의 소리를 끊을 때는 이 메시지를 보내지 않는다.
- multisound VT는 각 Working Set의 소리를 끊지 않고 겹쳐 낸다.
- 경보 소리가 끝나거나 silent로 설정되어 있으면 VT는 다시 Control Audio Signal 명령을 받는다.
- Set Audio Volume은 Alarm Mask의 음량에 영향을 주지 않는다.

따라서 Working Set이 Control Audio Signal로 낸 경고음은 다른 Working Set의 경보에 끊길 수 있다. 안전에 관련된 경고는 Alarm Mask로 띄우고, 비프음은 보조 수단으로 쓰는 편이 맞다. Termination message를 받으면 필요할 때 소리를 다시 요청한다(추론).

<small>근거: ISO 11783-6 4.6.14, F.10, F.12, H.22</small>

## 5. VT가 먼저 보내는 활성화 메시지 정리

36장에서 VT→ECU 메시지의 트리거와 주요 데이터를 표로 봤다. 이 메시지들은 운전자 조작이나 화면 변화를 VT가 먼저 알리고 Working Set이 응답하는 구조라서 활성화 메시지(activation message)라고 부른다. 여기서는 구현자가 메시지마다 확인해야 할 세 가지를 정리한다. TAN이 어디에 실리는가, 응답을 꼭 보내야 하는가, 응답에 무엇을 담는가다.

표를 읽기 전에 두 낱말을 짚는다. 니블(nibble)은 4비트, 곧 16진수 한 자리다. 한 바이트는 상위 니블(Bits 7~4)과 하위 니블(Bits 3~0)로 나뉜다. 예를 들어 `6F`의 상위 니블은 `6`, 하위 니블은 `F`다. "반향"은 받은 값을 그대로 돌려준다는 뜻이다.

| 메시지(코드) | 보내는 때 | TAN 위치(v6부터) | 응답 내용 |
|---|---|---|---|
| Soft Key Activation(`00`) | 누름·뗌, 누르는 동안 200 ms마다 | Byte 8 상위 니블(하위 `F`) | 같은 필드 반향 |
| Button Activation(`01`) | 누름·뗌, 누르는 동안 200 ms마다(래치 버튼은 반복 없음) | Byte 8 상위 니블(하위 `F`) | 같은 필드 반향 |
| Pointing Event(`02`) | 누름·뗌, 누르는 동안 200 ms마다 | Byte 6 상위 니블(하위는 Touch State) | X·Y·Signal·Parent Mask 반향 |
| VT Select Input Object(`03`) | 운전자 조작이나 ESC 명령으로 포커스·열림이 바뀔 때 | Byte 8 상위 니블(하위 `F`) | Object ID·Selection·Bitmask·TAN |
| VT ESC(`04`) | 운전자 ESC, 또는 VT가 운전자 외 이유로 입력을 닫을 때 | Byte 8 상위 니블(하위 `F`) | Object ID·TAN |
| VT Change Numeric Value(`05`) | 운전자가 숫자 값을 입력할 때(값이 같아도) | Byte 4 상위 니블(하위 `F`) | Object ID·TAN·값 복사 |
| VT Change Active Mask(`06`) | 마스크·Window Mask·Key Group에서 누락 참조나 오류 발견 | 없음 | Byte 2~3 마스크 ID |
| VT Change Soft Key Mask(`07`) | Soft Key Mask에서 누락 참조나 오류 발견 | 없음 | 마스크 ID, Soft Key Mask ID |
| VT Change String Value(`08`) | Input String 입력 완료 | 없음 | Byte 4~5 Object ID(Byte 2~3은 `FF`) |
| VT On User-Layout Hide/Show(`09`, v4부터) | Window Mask·Key Group 표시 변화 등 | Byte 8 상위 니블 | 같은 필드 반향 |
| VT Control Audio Signal Termination(`0A`, v4부터) | VT가 Control Audio Signal 소리를 일찍 끊을 때 | Byte 3 상위 니블 | Termination Cause·TAN(v6에서 신설) |

![v6 활성화 메시지에서 TAN이 실리는 위치: Soft Key Activation, Button Activation, VT Select Input Object, VT ESC는 Byte 8 상위 니블(하위 F), VT Change Numeric Value는 Byte 4(하위 F), Pointing Event는 Byte 6(하위 Touch State), VT On User-Layout Hide/Show는 Byte 8, VT Control Audio Signal Termination은 Byte 3(두 메시지 모두 하위 니블 미정)](/images/study-isobus/39-tan-position-light.png)
![v6 활성화 메시지에서 TAN이 실리는 위치: Soft Key Activation, Button Activation, VT Select Input Object, VT ESC는 Byte 8 상위 니블(하위 F), VT Change Numeric Value는 Byte 4(하위 F), Pointing Event는 Byte 6(하위 Touch State), VT On User-Layout Hide/Show는 Byte 8, VT Control Audio Signal Termination은 Byte 3(두 메시지 모두 하위 니블 미정)](/images/study-isobus/39-tan-position-dark.png)

응답 의무는 모든 행에 같은 규칙이 적용된다. Working Set과 VT가 모두 v5 이하와 호환되는 조합이면 응답은 선택이다. 둘 다 v6 이상과 호환되는 조합이면 200 ms 안에 응답해야 한다. 예외가 하나 있다. Control Audio Signal Termination의 응답은 v6에서 새로 생겼고, v5 이하에는 응답이 정의되지 않았다. 응답은 모두 ECU→VT 방향의 PGN(Parameter Group Number, 메시지 종류를 가리키는 번호) 59136(0xE700)으로, 받을 VT의 주소를 지정해(목적지 지정) 보낸다.

TAN 바이트의 하위 니블은 Soft Key·Button·VT Select Input Object·VT ESC·VT Change Numeric Value에서 `F`로 정해져 있다. Pointing Event에서는 하위 니블이 Touch State다. VT On User-Layout Hide/Show와 Control Audio Signal Termination은 Part 6이 "Bits 7~4 TAN"만 적고 하위 니블을 정하지 않는다(그림의 "미정"). 그래서 TAN을 꺼낼 때는 항상 상위 니블만 보고(`b >> 4`), 하위 니블을 검증 조건에 넣지 않는 편이 안전하다. `b >> 4`는 바이트 `b`를 오른쪽으로 4비트 밀어 상위 니블만 남기는 계산이다.

<small>근거: ISO 11783-6 H.1~H.23</small>

## 6. Pointing Event 세부 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

VT는 터치스크린이나 포인팅 장치(마우스·조이스틱)를 선택적으로 지원할 수 있다. Working Set은 Get Hardware response Byte 4로 확인한다. Get Hardware는 VT의 하드웨어 능력을 묻는 기술 데이터 메시지다([30장](/study/isobus/30-vt-display-technical-data)). Bit 0은 터치스크린, Bit 1은 포인팅 장치, Bit 6은 드래그 보고, Bit 7은 드래그 중간 좌표 지원이다. Pointing Event는 Button이나 입력 오브젝트와 연결되지 않은 영역을 터치했을 때만 나간다. 그 영역은 Data Mask, 그리고 v6부터 Free Form Window Mask(type 0)다. v4·v5는 Alarm Mask도 포함했지만 v6에서 deprecated(더 이상 쓰지 않기로 함)되었다.

| 바이트 | 내용 |
|---|---|
| 2, 3 | X 위치(Data Mask 좌상단 기준, 0 ~ 폭 − 1) |
| 4, 5 | Y 위치(0 ~ 높이 − 1) |
| 6 | Signal: v3 이하 `FF`(Pressed로 간주), v4~v5 Touch State(0 Released, 1 Pressed, 2 Held), v6부터 상위 니블 TAN·하위 니블 Touch State |
| 7, 8 | v5 이하 `FF FF`, v6부터 Parent Mask Object ID |

`02 F0 00 78 00 11 01 00`은 X = 240, Y = 120, TAN 1, Pressed, Parent Mask `0x0001`이다. 한 칸씩 읽으면 `02`는 Pointing Event, `F0 00`은 X = `0x00F0` = 240, `78 00`은 Y = `0x0078` = 120이다. `11`은 상위 니블 1(TAN 1)과 하위 니블 1(Pressed)이고, `01 00`은 Parent Mask `0x0001`이다.

Signal 형식은 VT 버전(Get Memory response로 알린 값)과 Working Set 버전(Working Set Maintenance로 알린 값)을 함께 보고 정한다는 각주가 있다. 두 버전이 다를 때 어느 쪽을 따르는지는 Part 6이 명시하지 않는다(확인 필요).

드래그 규칙도 있다(v4부터). 처음 누른 곳이 Button이나 입력 필드가 아니었다면, 드래그가 그 위를 지나가도 Pointing Event를 계속 보내고 그 오브젝트를 활성화하지 않는다. 드래그 중 좌표가 Data Mask 밖으로 나가면 마지막 유효 좌표나 범위 안으로 제한한 좌표에서 Released를 보고한다. 중간 좌표를 못 내는 VT는 누른 좌표를 반복한다. v6부터는 누르는 동안 Change Active Mask로 다른 마스크로 바뀌면 Released를 보내고, 같은 마스크로 바뀌면 Held를 계속 보낸다. v5부터는 On pointing event press(27)·release(28) 이벤트로 매크로를 걸 수도 있다([38장](/study/isobus/38-vt-macro-input)).

<small>근거: ISO 11783-6 4.6.23, D.9, H.6~H.7, Table A.3</small>

## 7. VT Change String Value: 운전자가 넣은 문자열

운전자가 Input String에 입력한 문자열을 Working Set에 전달하는 메시지다. 숫자를 전달하는 VT Change Numeric Value와 짝을 이루지만, 길이 필드와 응답 형식이 달라 따로 본다.

- 구조는 Byte 2~3 Object ID, Byte 4 문자열 바이트 수(<strong>1바이트</strong>), Byte 5부터 문자열이다. 명령인 Change String Value의 길이 필드는 2바이트였다.
- 헤더가 4바이트라 문자열이 4바이트 이하면 한 프레임에 들어가고, TP를 쓰면 안 된다. TP(Transport Protocol)는 8바이트보다 긴 데이터를 여러 프레임으로 나눠 보내는 방식이다([15장](/study/isobus/15-tp-bam-cmdt)). 3바이트 이하면 남는 바이트를 `FF`로 채운다. "AB12"를 입력하면 `08 30 00 04 41 42 31 32`로 정확히 8바이트다.
- VT는 앞쪽 공백을 지우면 안 된다. 풀에 정의된 길이까지 공백으로 채우는 것은 허용된다.
- Input String이 String Variable을 참조하면 String Variable의 Object ID가 실린다. VT Change Numeric Value에서 Number Variable의 ID가 실리는 것과 같은 규칙이다.
- 응답은 Byte 2~3이 `FF FF`이고 Object ID가 Byte 4~5에 온다. 예: `08 FF FF 30 00 FF FF FF`.

"AB12"의 예를 풀면 `08`은 VT Change String Value, `30 00`은 Object ID `0x0030`, `04`는 문자열 길이 4바이트, `41 42 31 32`는 문자 A, B, 1, 2의 코드다.

TP로 긴 문자열이 오는 동안 Working Set은 다른 메시지를 먼저 받을 수 있다. 입력이 닫혔음을 알리는 VT Select Input Object나 Soft Key Activation이 TP 전송 완료보다 먼저 올 수 있다. "Deselect를 받았으니 입력이 끝났다"고 보고 값을 처리하면 아직 도착하지 않은 문자열을 놓친다. Object ID별로 TP 수신 완료를 따로 추적해야 한다(추론).

<small>근거: ISO 11783-6 H.18~H.19</small>

## 8. 오류 통지: VT Change Active Mask, VT Change Soft Key Mask

이름이 비슷하지만 Change Active Mask <strong>response</strong>와 VT Change Active Mask <strong>message</strong>는 용도가 다르다. 앞의 것은 명령을 받아 처리했다는 확인이고, 뒤의 것은 VT가 마스크를 그리려다 발견한 오류의 통지다. 이 절은 뒤의 것을 읽는 법을 본다.

| 바이트 | VT Change Active Mask message(`06`) |
|---|---|
| 2, 3 | Active mask, Window Mask, 또는 Key Group의 Object ID |
| 4 | 오류: Bit 2 Missing objects, Bit 3 마스크·child 오류, Bit 4 기타, Bit 5 <strong>풀 삭제 중</strong>(Bit 0·1 예약) |
| 5, 6 | 오류가 있는 오브젝트의 ID |
| 7, 8 | 그 오브젝트의 부모 ID |

오류 검사는 언제든 할 수 있지만 늦어도 그리기 전에는 해야 한다. 그대로 그리면 화면 일부만 그려질 누락 참조나 오류가 발견되면, VT는 풀 삭제를 알리는 이 메시지를 보낸다. 정의되지 않은 옵션 비트처럼 치명적이지 않은 오류는 풀을 지우지 않도록 VT 설계자가 정할 수 있다. 풀이 지워지면 VT는 그 Working Set의 unexpected shutdown을 감지한 것처럼 동작한다. unexpected shutdown은 Working Set이 예고 없이 사라졌을 때 VT가 하는 처리다([31장](/study/isobus/31-vt-connection)).

`06 02 00 24 28 00 02 00`을 디코딩하면 다음과 같다. 마스크 `0x0002`를 그리려다 오브젝트 `0x0028`(부모 `0x0002`)에서 누락 참조를 찾았다. 오류 바이트 `0x24`는 2진수로 `0010 0100`이라 Bit 2(Missing objects)와 Bit 5(풀 삭제 중)가 1이다. Working Set은 풀을 고쳐 초기화부터 다시 해야 한다([31장](/study/isobus/31-vt-connection)). 이 메시지는 Hide/Show의 누락 child 검사를 Container가 보일 때까지 미룬 경우에도 나오고, Object Pointer의 잘못된 참조를 마스크 활성화 시점까지 미룬 경우에도 나온다. 이 메시지에 대한 Working Set의 응답은 Byte 2~3에 마스크 ID를 담고 나머지는 `FF`다.

VT Change Soft Key Mask message(`07`)는 같은 규칙을 Soft Key Mask에 적용한다. Byte 2~3은 Data/Alarm Mask ID, 4~5는 Soft Key Mask ID, 6은 같은 구성의 오류 비트다.

<small>근거: ISO 11783-6 4.6.9, 4.6.11.5, F.3, F.35, H.14~H.17</small>

## 9. VT On User-Layout Hide/Show (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

User-Layout은 여러 Working Set의 작은 창(Window Mask)과 키 묶음(Key Group)을 VT가 한 화면에 모아 보여 주는 방식이다. 이 메시지(v4부터)는 User-Layout 화면에서 Window Mask나 Key Group이 나타나거나 사라질 때 Working Set에 알린다. User-Layout과 Window Mask 자체는 [34장](/study/isobus/34-vt-layout-color)에서 다룬다. 이 메시지는 방금 inactive가 됐지만 Data Mask와 Soft Key Mask가 여전히 보이는 Working Set에 "아직 보인다"고 알리는 데도 쓴다.

- 한 메시지에 오브젝트 두 개의 상태를 담는다(Byte 2~4, Byte 5~7). 두 번째가 없으면 NULL ID를 쓰고 그 상태 비트는 0이다. 언급되지 않은 오브젝트는 마지막으로 알려진 상태를 유지한다고 본다.
- Byte 2~7이 바뀔 때 보내고, 마스크당 초당 최대 5회다.
- inactive이면서 보이는 Working Set을 active로 바꿀 때는, 먼저 이 메시지로 그 Working Set의 Data/Soft Key Mask를 "hide"로 알린 뒤 VT Status로 활성화를 알린다.

마지막 순서 규칙의 의도는 이렇다. Working Set은 "VT Status가 나를 active라고 한다" 또는 "이 메시지가 내 마스크를 shown이라고 한다" 중 하나라도 참이면 자기 화면이 보인다고 판단한다. active가 되는 순간 두 신호가 동시에 참이 되지 않게, 보이는 이유를 VT Status 쪽으로 깔끔하게 넘기는 것이다.

<small>근거: ISO 11783-6 G.2, H.20~H.21</small>

## 10. 응답 타임아웃을 읽는 두 가지 방법 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

Part 6에는 활성화 메시지의 응답 타임아웃에 관한 문장이 두 개 있다. 하나는 "응답이 300 ms 안에 오지 않으면 VT는 최대 3회 재시도해야 한다(should)"이다. 다른 하나는 "필수 응답이 300 ms 안에 오지 않으면 VT는 Working Set의 unexpected shutdown처럼 동작하고, Working Set Maintenance에 Acknowledgement:NACK를 보내야 한다(shall)"이다. should는 지키기를 권하는 규칙, shall은 반드시 지켜야 하는 규칙이다. Acknowledgement:NACK는 요청을 받아들이지 않았다는 부정 응답이다([10장](/study/isobus/10-j1939-request-ack)).

두 문장의 선후 관계를 Part 6이 명시하지 않는다. 36장의 설명과 37장의 그림은 "재시도한 뒤에도 응답이 없으면 shutdown"으로 읽었다. 하지만 VT 구현에 따라 첫 300 ms만으로 shutdown 처리할 가능성도 배제할 수 없다.

Working Set 쪽 대책은 하나다. v6 조합에서는 모든 activation 메시지에 200 ms 안에 응답한다. 재시도에 기대지 않는다. VT를 에뮬레이션하는 SIL 환경(실제 장비 대신 소프트웨어로 상대를 흉내 내어 시험하는 환경)이라면 두 해석을 설정으로 바꿔 가며 Working Set을 시험하는 편이 좋다(추론). 이 규칙은 Working Set과 VT가 <strong>모두</strong> v6 이상과 호환될 때만 적용된다는 점도 기억한다. Working Set Maintenance로 버전 5를 보고한 Working Set에는 응답이 선택이다.

<small>근거: ISO 11783-6 H.1</small>

::: details 원문을 가진 독자를 위한 메모
- 1~4절의 경보 규칙은 4.6.14(절차 a~h 포함), 3절의 "마스크 전환 규칙 표"는 4.6.14의 Table 4다. 1절의 Alarm Mask 속성은 B.3이다.
- 5~10절의 "활성화 메시지"는 Annex H 메시지다. 6절 Pointing Event는 H.6, 7절은 H.18~H.19, 8절은 H.14~H.17, 9절은 H.20~H.21, 10절의 두 타임아웃 문장은 H.1이다.
- 2절 정보 상자의 ACK 수단은 4.2 d), ACK의 key code 0 규칙은 H.2다. 4절의 multisound 동작은 F.10 Figure F.2, Termination message는 H.22다.
:::

::: tip 핵심 정리
- 경보는 Priority(0 High, 1 Medium, 2 Low)로 먼저 고르고, 같으면 먼저 처리한 순서로 고른다. 가장 높은 경보는 그 Working Set이 마스크를 바꿀 때까지 화면에 남는다.
- 운전자의 ACK는 key code 0의 Soft Key Activation일 뿐이다. 경보를 내리는 것은 Working Set의 Change Active Mask다.
- 경보는 화면에 다시 나타날 때마다 소리를 다시 낸다. 높은 경보는 낮은 경보의 소리를 끊고, multisound가 아닌 VT는 Control Audio Signal 소리도 끊는다.
- 활성화 메시지의 TAN은 대부분 Byte 8 상위 니블에 실리지만, VT Change Numeric Value는 Byte 4, Pointing Event는 Byte 6, Audio Signal Termination은 Byte 3이다. TAN은 상위 니블만 읽는다.
- v6 조합에서는 모든 활성화 메시지에 200 ms 안에 응답한다. VT Change Active Mask message는 마스크 오류 통지이고, Bit 5가 서 있으면 풀이 지워진다.
:::

::: details 확인 문제
1. (개념) Working Set A의 Medium 경보가 보이는 중에 Working Set B도 Medium 경보를 띄웠다. 화면에는 누구의 경보가 보이는가? B의 경보는 언제 보이게 되는가?
2. (개념) 운전자가 ACK 수단을 눌렀는데 경보 화면이 사라지지 않는다. VT가 고장 난 것인가?
3. (디코딩) v6 조합에서 VT로부터 `02 F0 00 78 00 22 01 00`이 왔다. 무엇을 뜻하는가?
4. (장애 진단) 작업기가 Change Active Mask로 Data Mask `0x0002`를 띄운 직후 VT에서 `06 02 00 24 28 00 02 00`이 왔고, 그 뒤 작업기 화면이 VT에서 사라졌다. 무엇이 잘못됐고 Working Set은 무엇을 해야 하는가?

**답 가이드**
1. A의 경보가 보인다. 1차 기준인 Priority가 같으므로 2차 기준인 시간 순서에 따라 먼저 처리된 A가 active mask가 된다. A가 Data Mask나 더 낮은 경보로 바꾸면 그때 B의 경보가 나타나고, 나타나는 순간 B의 경보음도 난다.
2. 아니다. ACK는 key code 0인 Soft Key Activation으로 Working Set에 알려질 뿐이다. Working Set이 Change Active Mask로 Data Mask를 활성화해야 경보가 내려간다. ACK를 허용하지 않는 경보라면 Working Set이 일부러 무시했을 수도 있다.
3. Pointing Event(`02`)다. X = `0x00F0` = 240, Y = `0x0078` = 120이고, Byte 6 `22`의 상위 니블 2가 TAN 2, 하위 니블 2가 Touch State Held(누르고 있는 중)다. Byte 7~8 `01 00`은 Parent Mask `0x0001`이다. Working Set은 200 ms 안에 X·Y·Signal·Parent Mask를 반향해 응답한다.
4. VT Change Active Mask message(`06`)다. 마스크 `0x0002`를 그리려다 오브젝트 `0x0028`(부모 `0x0002`)에서 누락 참조를 찾았다. 오류 바이트 `0x24`는 Bit 2(Missing objects)와 Bit 5(풀 삭제 중)이므로 VT가 풀을 지우고 unexpected shutdown처럼 처리했다. 그래서 화면이 사라졌다. Working Set은 오류를 담은 오브젝트 `0x0028`이 참조하는 오브젝트가 풀에 모두 들어 있는지 확인해 풀을 고친 뒤, 초기화부터 다시 해야 한다.
:::

## 다음 챕터

- 다음: [40장 보조 입력(AUX): 조이스틱을 기능에 연결하기](/study/isobus/40-vt-aux)
