---
title: "VT 명령 세부와 공통 규칙"
description: "모든 VT 명령에 공통으로 걸리는 응답, 오류 코드, 대기 규칙을 익히고, 자주 쓰는 명령을 바이트로 읽은 뒤 나머지 명령의 세부를 기능별로 정리한다."
date: 2026-04-13
tags: [ISOBUS, VT, Commands, PGN, Error-Code, ISO-11783-6]
prev: /study/isobus/36-vt-commands-basics
next: /study/isobus/38-vt-macro-input
---

# VT 명령 세부와 공통 규칙

::: info 학습 목표
- 메시지 첫 바이트(VT function 코드)와 PGN을 함께 보고 그 프레임이 무엇인지 알아낼 수 있다.
- 응답 프레임에서 반향된 값과 오류 코드 바이트를 찾아 명령의 성공과 실패를 판단할 수 있다.
- 응답을 기다리는 시간, 재전송, 응답이 가는 곳의 규칙을 설명할 수 있다.
- 자주 쓰는 명령(Change Numeric Value, Change String Value, Change Active Mask, Hide/Show Object)을 바이트로 조립하고 읽을 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [36장 VT 명령어 기초](/study/isobus/36-vt-commands-basics), [31장 VT 연결 관리](/study/isobus/31-vt-connection), [33장 오브젝트 레코드](/study/isobus/33-vt-object-records)
- 이 장에서 처음 나오는 말
  - Working Set의 Master와 member: Working Set은 VT를 쓰는 작업기 쪽 ECU 묶음이다(36장에서 "작업기"라고 부른 쪽). 대표 ECU가 Master, 나머지가 member다. 이 장은 둘을 구별해야 해서 표준 이름 Working Set을 쓴다
  - 반향(echo): 응답이 받은 명령의 값을 그대로 되돌려 싣는 것
  - 오류 코드(Error Code): 응답에 실리는 1바이트 값. 0이면 성공이고, 켜진 비트가 실패 원인을 가리킨다
  - 비트마스크(bitmask): 한 바이트의 비트 8개에 서로 다른 뜻을 하나씩 붙여 쓰는 방식
  - busy 비트: VT가 지금 무엇 때문에 바쁜지 VT Status 메시지에 표시하는 비트
:::

36장에서 명령의 이름과 쓰임을 봤다. 실제로 VT와 통신하는 프로그램을 짜 보면 명령 하나하나보다 모든 명령에 공통으로 걸리는 규칙에서 먼저 틀리기 쉽다. 택배에 비유하면 물건마다 포장법은 달라도 송장 쓰는 법, 수령 확인, 반송 규칙은 모두 같다. 이 장은 그 공통 규칙을 먼저 잡고, 자주 쓰는 명령을 바이트로 읽은 다음, 나머지 명령의 세부를 기능별로 정리한다.

ISO 11783-6(VT를 정하는 표준 문서)의 2018년 판을 따른다. 메시지 전체의 바이트 표는 [ISO 11783-6 부록](/study/isobus/appendix-iso-part06)에 모아 두었고, 이 장은 학습 흐름과 구현 함정 위주로 본다.

## 1. 첫 바이트: 메시지 종류를 알리는 VT function 코드

받은 프레임을 처리하는 첫걸음은 "이것이 무슨 메시지인가"를 알아내는 일이다. 이 절은 그 열쇠인 첫 바이트를 보고, 첫 바이트만으로는 부족해서 PGN을 함께 봐야 한다는 점을 확인한다.

VT 메시지의 Byte 1은 항상 <strong>VT function</strong> 코드다. 표준 문서의 메시지 표는 이 바이트를 상위 4비트(Command)와 하위 4비트(Parameter)로 나눠 적는다. Change Numeric Value는 168 = `0xA8`, 즉 Command `1010`·Parameter `1000`이다. `0xA8`을 2진수로 쓰면 `1010 1000`이고, 앞 네 자리가 명령 묶음, 뒤 네 자리가 묶음 안의 번호다.

코드 공간은 대략 다음처럼 나뉜다. 표의 첫 칸은 Byte 1 값의 범위(16진수), 둘째 칸은 그 범위에 든 메시지 묶음, 셋째 칸은 이 블로그에서 그 묶음을 다루는 장이다.

| Byte 1 범위 | 메시지 묶음 | 다루는 장 |
|---|---|---|
| `00`~`0A` | VT가 먼저 보내는 activation 메시지와 그 응답 | [36장](/study/isobus/36-vt-commands-basics), [39장](/study/isobus/39-vt-alarm-activation) |
| `11`, `12` | Object pool transfer, End of Object Pool | [32장](/study/isobus/32-vt-object-pool-basics), [35장](/study/isobus/35-vt-pool-transfer-charset) |
| `20`~`27` | Auxiliary control | [40장](/study/isobus/40-vt-aux) |
| `60`~`7F` | 제조사 고유 명령(제조사가 다르면 쓰지 않도록 권고) | 다루지 않음 |
| `90`, `92`, `A0`~`BA`, `BC`~`BE` | Working Set이 보내는 명령과 그 응답 | 이 장 |
| `BB`, `C0`~`C7` | 기술 데이터 메시지(Identify VT 포함) | [30장](/study/isobus/30-vt-display-technical-data), [31장](/study/isobus/31-vt-connection) |
| `D0`~`D6`, `DF`, `E0` | 비휘발성 메모리 | [31장](/study/isobus/31-vt-connection) |
| `FD`~`FF` | 상태 메시지 | [31장](/study/isobus/31-vt-connection) |

표의 말을 풀면 이렇다. activation 메시지는 운전자 조작을 알리는 활성화 메시지([36장](/study/isobus/36-vt-commands-basics))다. Auxiliary control은 조이스틱 같은 보조 입력 장치를 다루는 메시지다. 비휘발성 메모리는 전원을 꺼도 지워지지 않는 저장소로, VT가 오브젝트 풀을 저장해 두는 곳이다.

같은 function 코드가 명령과 응답에 함께 쓰인다는 점이 중요하다. 아래의 ECU→VT, VT→ECU는 두 PGN의 표준 이름(ECU to VT, VT to ECU)을 딴 방향 표기이고, ECU는 Working Set 쪽을 뜻한다([36장](/study/isobus/36-vt-commands-basics)). `0xAD`는 Change Active Mask 명령(ECU→VT, PGN 59136(0xE700))이면서 그 응답(VT→ECU, PGN 58880(0xE600))이기도 하다. 그래서 수신 측은 Byte 1만 보고 분기하면 안 되고, <strong>PGN(방향)과 Byte 1을 함께</strong> 봐야 한다.

두 PGN은 Group Function 메시지다. Group Function은 PGN 하나에 여러 기능을 담고, 첫 데이터 바이트로 기능을 고르는 형식이다([10장](/study/isobus/10-j1939-request-ack)). 첫 바이트에 모르는 코드나 예약 코드가 오면, v5부터는 받은 쪽이 Unsupported VT Function 메시지(Working Set→VT)나 VT Unsupported VT Function 메시지(VT→Working Set)로 알려야 한다. v4 이하에서는 이 동작이 정의되지 않았다.

두 PGN의 기본 우선순위는 5이고, v5 이하 문서에는 7로 적혀 있었다. 우선순위는 CAN ID 맨 앞 3비트로, 값이 작을수록 버스를 먼저 차지한다([9장](/study/isobus/09-j1939-message)).

VT↔ECU 메시지 중 8바이트로 정의되지 않은 것은 모두 `FF`로 8바이트까지 채운다. 예를 들어 Change String Value로 "OK" 두 글자를 보내면 데이터가 7바이트뿐이라 마지막 바이트를 `FF`로 채운다(6절).

::: details 원문을 가진 독자를 위한 메모
위 코드 범위 표를 원문 정의 위치와 함께 적으면 다음과 같다. 코드 범위는 Table A.5, 비트 표기 예는 F.22를 따랐다.

| Byte 1 범위 | 메시지 묶음 | 정의 위치 |
|---|---|---|
| `00`~`0A` | VT가 먼저 보내는 activation 메시지와 그 응답 | Annex H |
| `11`, `12` | Object pool transfer, End of Object Pool | Annex C |
| `20`~`27` | Auxiliary control | Annex J |
| `60`~`7F` | 제조사 고유 명령(제조사가 다르면 쓰지 않도록 권고) | Table A.5 |
| `90`, `92`, `A0`~`BA`, `BC`~`BE` | Working Set이 보내는 명령과 그 응답 | Annex F |
| `BB`, `C0`~`C7` | 기술 데이터 메시지(Identify VT 포함) | Annex D |
| `D0`~`D6`, `DF`, `E0` | 비휘발성 메모리 | Annex E |
| `FD`~`FF` | 상태 메시지 | Annex G |

이 블로그에서 "명령"이라고 부르는 것은 대부분 Annex F의 command이고, "활성화 메시지"는 Annex H의 message다. Unsupported VT Function 메시지는 G.4(WS→VT), VT Unsupported VT Function 메시지는 G.5(VT→WS)이고, 우선순위와 Group Function 규정은 C.1, 패딩 규정은 4.6.26에 있다.
:::

<small>근거: ISO 11783-6 4.6.26, C.1, F.22, G.4, G.5, Table A.5</small>

## 2. 응답 읽기: 받은 명령을 비추고 오류를 알린다

이 절은 응답 프레임에서 무엇을 읽어야 하는지 본다. 결론은 두 가지다. 응답의 값 필드는 받은 명령을 되비출 뿐이고, 성공 여부는 오류 코드로 판단한다.

### 응답은 상태가 아니라 명령을 비춘다

명령에 공통으로 걸리는 규칙은 다음과 같다.

- Working Set Master뿐 아니라 member도 명령을 보낼 수 있다. 반면 오브젝트 풀 전송 명령([32장](/study/isobus/32-vt-object-pool-basics))은 Master만 보낼 수 있다.
- VT는 그 Working Set의 오브젝트 풀이 아직 로드되지 않았어도 명령에 응답해야 한다.
- 응답에 명령과 같은 필드가 있으면 그 값은 <strong>명령에서 받은 값 그대로</strong> 돌려준다. 응답은 오브젝트의 현재 상태가 아니라 받은 명령을 비춘다.

식당에서 직원이 "김치찌개 2인분 주문 받았습니다"라고 복창해도, 김치찌개가 실제로 나왔다는 뜻은 아니다. VT 응답의 반향도 같다. 성공했는지는 따로 붙는 오류 코드가 알려 준다.

표준이 드는 예가 이 규칙을 잘 보여 준다. disable할 수 없는 상태의 오브젝트에 Enable/Disable Object(disable)를 보내면 오브젝트는 enabled로 남는다. 그래도 응답 Byte 4는 0(disable)이고, Error Code가 실패 원인을 알린다.

::: warning 응답 값으로 화면 상태를 미러링하지 않는다
미러링은 상대의 상태를 내 쪽에 복사해 두는 것이다. 응답의 값 필드를 그대로 받아 내부 상태를 갱신하면, 실패한 명령도 성공한 것처럼 반영된다. 상태는 Error Code가 0일 때만 반영한다. 지금 값이 정말 필요하면 v4부터 있는 Get Attribute Value(7절)로 묻는다.
:::

### 오류 코드 바이트 읽는 법

명령을 실행하다 오류를 찾으면, VT는 응답에 해당하는 오류 코드를 최소 1개 실어야 한다(shall). 오류를 여러 개 찾았으면 전부 싣는 것이 권고다(should). 표준 문장에서 shall은 반드시 지킬 의무, should는 권고를 뜻한다.

오류 코드는 응답의 한 바이트에 비트마스크로 실리고, 0이면 오류가 없다는 뜻이다. 비트 번호는 표준 표기대로 0부터 센다. Bit 0이 가장 낮은 자리(값 1), Bit 7이 가장 높은 자리(값 128)다. 예를 들어 오류 바이트가 `0x02`(2진수 `0000 0010`)면 Bit 1만 켜진 것이고, `0x12`(`0001 0010`)면 Bit 1과 Bit 4가 함께 켜진 것이다.

구현에서 걸리는 지점은 두 가지다. 첫째, 오류 바이트의 <strong>위치</strong>가 명령마다 다르다. 응답이 반향하는 필드 바로 뒤에 오기 때문이다. 둘째, "기타 오류(Any other error)" 비트가 대부분 Bit 4지만 예외가 많다.

![명령과 응답 프레임 비교: Change Numeric Value는 명령의 Byte 4 예약 FF 자리에 응답 오류 코드가 들어가고 나머지 값은 반향된다. Change String Value 응답은 Byte 2~3이 예약 FF FF로 바뀌고 Object ID가 Byte 4~5로 옮겨 가며 오류 코드는 Byte 6에 실린다](/images/study-isobus/37-response-anatomy-light.png)
![명령과 응답 프레임 비교: Change Numeric Value는 명령의 Byte 4 예약 FF 자리에 응답 오류 코드가 들어가고 나머지 값은 반향된다. Change String Value 응답은 Byte 2~3이 예약 FF FF로 바뀌고 Object ID가 Byte 4~5로 옮겨 가며 오류 코드는 Byte 6에 실린다](/images/study-isobus/37-response-anatomy-dark.png)

그림 위쪽 Change Numeric Value는 명령의 Byte 4(예약 `FF`) 자리에 응답의 오류 코드가 들어가고, 나머지는 그대로 반향된다. 아래쪽 Change String Value는 응답에서 Object ID가 Byte 4~5로 옮겨 가고 오류 코드가 Byte 6에 실린다. 두 응답의 오류 코드 위치가 다르다.

아래 표는 명령별로 오류 바이트 위치와 기타 오류 비트를 모은 것이다. 첫 칸은 명령 이름과 function 코드, 둘째 칸은 응답에서 오류 코드가 실리는 바이트 번호(1부터 셈), 셋째 칸은 "기타 오류"를 뜻하는 비트 번호다. 굵게 쓴 값은 특히 헷갈리기 쉬운 예외다.

| 명령(코드) | 오류 바이트 | 기타 오류 비트 | 비고 |
|---|---|---|---|
| Hide/Show Object(`A0`), Enable/Disable Object(`A1`), Select Input Object(`A2`) | Byte 5 | Bit 4 | |
| Change Numeric Value(`A8`), Change Size(`A6`), Change Active Mask(`AD`) | Byte 4 | Bit 4 | |
| Change Font Attributes(`AA`) | Byte 4 | <strong>Bit 5</strong> | Bit 4는 Invalid style |
| Change String Value(`B3`) | <strong>Byte 6</strong> | <strong>Bit 3</strong> | Bit 4는 예약 |
| Change List Item(`B1`) | Byte 7 | Bit 4 | |
| Change Polygon Scale(`B7`) | Byte 8 | Bit 4 | |
| Execute Macro(`BE`) | Byte 3 | <strong>Bit 2</strong> | Execute Extended Macro는 Byte 4 |
| Lock/Unlock Mask(`BD`) | Byte 3 | <strong>Bit 7</strong> | Bit 4~6은 unsolicited 해제 사유 |
| Select Active Working Set(`90`) | Byte 2 | <strong>Bit 7</strong> | |

그래서 오류 해석은 "Byte 4를 읽는다" 같은 고정 규칙이 아니라 function 코드별 표로 구현해야 한다. 7절 끝의 Python 예제가 그 형태다.

예를 들어 Change Numeric Value 응답 `A8 0B 00 01 96 00 00 00`을 받았다고 하자. 한 단계씩 읽으면 다음과 같다.

1. Byte 1이 `A8`이고 PGN이 VT→ECU이므로 Change Numeric Value 명령의 응답이다.
2. 표에서 `A8`의 오류 바이트는 Byte 4다. 값은 `0x01`이다.
3. `0x01`은 2진수 `0000 0001`이므로 Bit 0만 켜졌다. Change Numeric Value의 Bit 0은 Invalid Object ID(그런 오브젝트가 없음)다.
4. Byte 5~8의 `96 00 00 00`(150)은 보낸 값의 반향일 뿐이다. 화면 값은 바뀌지 않았다.

v4·v5에서 "값 사용 중(입력 열림)"을 뜻하던 비트는 v6에서 deprecated(더 이상 쓰지 않도록 폐기)되어 예약(0)이 되었다. Change Numeric Value의 Bit 2, Change String Value의 Bit 4, Change Attribute와 Change List Item의 Bit 3이 그렇다. v6 Working Set이라도 v5 이하 VT와 붙으면 이 비트를 받을 수 있으니, 이 비트가 서 있으면 실패로 처리한다.

VT가 지원하지 않는 오브젝트로 명령을 보내도 0이 아닌 오류 코드가 돌아온다. 이때 어느 비트를 세울지는 VT 설계에 달렸다. 표준이 드는 예는 Graphics Context 오브젝트(그림을 그리는 캔버스 오브젝트)를 지원하지 않는 VT에 그 오브젝트로 Change Background Colour를 보내는 경우다.

<small>근거: ISO 11783-6 4.6.10.2, 4.6.28, 4.6.29, C.1, F.1, F.23, F.25, F.39, F.43</small>

## 3. 기다림과 재전송

명령을 보냈는데 응답이 오지 않으면 언제까지 기다리고, 다시 보내도 되는가? 이 절은 그 규칙을 Working Set이 보내는 명령과 VT가 먼저 보내는 활성화 메시지로 나눠 본다.

![Working Set 명령은 응답을 받은 뒤 다음 명령을 보내고 1.5 s 동안 응답이 없으면 다음 명령을 허용하는 반면, v6 활성화 메시지는 200 ms 안에 응답해야 하고 300 ms 동안 없으면 같은 TAN으로 최대 3회 재시도한 뒤 unexpected shutdown으로 처리하는 흐름을 나란히 비교한 그림](/images/study-isobus/17-response-timing-light.png)
![Working Set 명령은 응답을 받은 뒤 다음 명령을 보내고 1.5 s 동안 응답이 없으면 다음 명령을 허용하는 반면, v6 활성화 메시지는 200 ms 안에 응답해야 하고 300 ms 동안 없으면 같은 TAN으로 최대 3회 재시도한 뒤 unexpected shutdown으로 처리하는 흐름을 나란히 비교한 그림](/images/study-isobus/17-response-timing-dark.png)

그림 왼쪽 패널은 Working Set이 보내는 명령, 오른쪽 패널은 VT가 먼저 보내는 활성화 메시지다.

명령을 보낸 쪽은 응답을 받은 뒤에 다음 명령을 보내야 한다(shall). 따로 정하지 않은 한 <strong>1.5 s</strong> 안에 응답이 없으면 다음 명령을 보낼 수 있다. 이전 명령은 재전송해도 되고 보통 3회를 넘기지 않는다. 다만 재전송이 누적 효과를 내는 명령은 조심해야 한다. 표준이 직접 드는 예가 Change Child Location이다. 상대 이동이라 같은 명령이 두 번 처리되면 두 번 움직인다.

말로 치면 "창문을 닫아라"는 두 번 말해도 결과가 같지만, "한 칸 오른쪽으로 옮겨라"는 두 번 말하면 두 칸 옮겨진다. 응답만 늦었을 뿐 첫 명령이 이미 처리됐을 수도 있다. 그래서 재전송은 몇 번 처리돼도 결과가 같은 명령에만 안전하다.

VT 쪽 설계 권고도 있다. VT가 응답 생성을 화면 갱신과 묶어 두면 그리기가 느릴 때 Working Set에서 응답 타임아웃이 난다. 그래서 둘을 분리(decouple)할 수 있는데, 그러면 Working Set이 응답을 받은 시점과 화면에 실제로 반영된 시점이 어긋날 수 있다. 화면 반영 완료를 확실히 알아야 하는 경우를 위해 Lock/Unlock Mask(7절)가 있다.

반대 방향인 활성화 메시지의 규칙은 [36장](/study/isobus/36-vt-commands-basics)에서 본 대로다. v6 조합에서는 200 ms 안에 응답해야 하고, 300 ms 안에 응답이 없으면 VT가 같은 데이터·같은 TAN으로 최대 3회 재시도한다. 두 규칙의 차이를 그림 하나로 비교하면 위와 같고, 표로 정리하면 다음과 같다.

| 구분 | Working Set이 보내는 명령 | VT가 보내는 활성화 메시지(v6 이상) |
|---|---|---|
| 응답 대기 | 1.5 s 동안 응답이 없으면 다음 명령을 보낼 수 있다 | 200 ms 안에 응답해야 한다 |
| 재전송 | 보내는 쪽 재량, 보통 3회 이하 | 300 ms 동안 응답이 없으면 같은 데이터·같은 TAN으로 최대 3회 |
| 재전송 뒤에도 응답이 없으면 | 이 규칙에서 따로 정하지 않는다 | VT가 그 Working Set이 예기치 않게 꺼진 것(unexpected shutdown)으로 처리 |

<small>근거: ISO 11783-6 F.1, H.1</small>

## 4. 응답 목적지와 VT의 busy 표시 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절은 두 가지를 본다. 명령을 member가 보냈을 때 응답이 누구에게 가는지, 그리고 VT가 느릴 때 그 이유를 어디서 읽는지다.

### 응답은 누구에게 가는가: 버전 조합별 목적지

명령은 Working Set member도 보낼 수 있다. 그러면 응답은 명령을 보낸 member에게 가야 할까, Master에게 가야 할까? 표준은 이를 Working Set 버전과 VT 버전의 조합으로 정한다. Working Set 버전은 Working Set Maintenance message로, VT 버전은 Get Memory response로 알린다([29장](/study/isobus/29-vt-basics) 참고).

아래 표의 CF(Control Function)는 버스에서 주소 하나를 가진 기능 단위, 곧 명령을 보낸 ECU다.

| 구성 | Working Set 버전 | VT 버전 | VT 응답이 가는 곳 |
|---|---|---|---|
| 1 | 3 이하 | 3 이하 | Working Set Master |
| 2 | 3 이하 | 4 이상 | Working Set Master |
| 3 | 4 이상 | 3 이하 | Working Set Master |
| 4 | 4 이상 | 4 이상 | 명령을 보낸 CF(originator) |

![응답 목적지 비교: 구성 1~3에서는 member가 보낸 명령의 응답이 Master 주소로 가서 member가 엿들어야 하고, Working Set과 VT가 모두 버전 4 이상인 구성 4에서는 응답이 명령을 보낸 member에게 바로 간다](/images/study-isobus/37-response-destination-light.png)
![응답 목적지 비교: 구성 1~3에서는 member가 보낸 명령의 응답이 Master 주소로 가서 member가 엿들어야 하고, Working Set과 VT가 모두 버전 4 이상인 구성 4에서는 응답이 명령을 보낸 member에게 바로 간다](/images/study-isobus/37-response-destination-dark.png)

구성 1~3에서는 member가 Master 앞으로 가는 목적지 지정 VT 메시지를 전부 엿들어야 자기 명령의 응답을 찾을 수 있다. Master는 member가 보낸 명령의 응답을 요청한 적 없이 받게 되고, 자기 명령과 짝을 맞출 수 없다. 둘 다 4 이상인 구성 4에서야 응답이 보낸 노드로 바로 가고, TP로 오는 응답(예: Get Supported WideChars response)도 쓸 수 있다. TP(Transport Protocol)는 8바이트보다 긴 데이터를 여러 프레임으로 나눠 보내는 방법이다([15장](/study/isobus/15-tp-bam-cmdt)).

반면 운전자 입력은 버전과 무관하게 항상 Master로 간다. 입력 필드에 들어온 값은 언제나 Working Set Master로 전송되고, 활성화 메시지도 Master에게 간다. Master 전용 명령을 member가 보내면 VT는 Acknowledgement:NACK로 응답한다. NACK는 "요청을 처리할 수 없다"는 J1939 공통 부정 응답이다([10장](/study/isobus/10-j1939-request-ack)).

::: tip SIL 에뮬레이터에서 확인할 점
SIL(Software-in-the-Loop)은 실제 장비 대신 소프트웨어로 상대 장치를 흉내 내 시험하는 방식이다. VT Server를 에뮬레이션할 때는 응답을 보내기 전에 "이 Working Set의 Maintenance 버전"과 "내가 Get Memory response로 알린 버전"을 함께 보고 목적지를 정해야 한다. 구성 4만 구현해 두면 v3 이하 Working Set의 가정이 깨진다. 그런 Working Set의 member는 Master 주소로 오는 응답을 엿듣도록 만들어졌으므로, 응답을 member 주소로 보내면 그 경로로 응답을 찾지 못할 수 있다.
:::

### VT Status의 busy 표시

VT가 지금 무엇을 하고 있는지는 VT Status message의 Byte 7(busy codes)과 Byte 8에 나온다. VT Status는 VT가 모든 장치에 주기적으로 보내는 상태 메시지다([31장](/study/isobus/31-vt-connection)). 아래 표의 도입 칸은 그 비트가 처음 생긴 VT 버전이고, 비어 있으면 처음부터 있던 비트다.

| Byte 7 비트 | 의미 | 도입 |
|---|---|---|
| Bit 0 | 표시 중인 마스크 갱신 중 | |
| Bit 1 | 비휘발성 메모리에 저장 중 | |
| Bit 2 | 명령 실행 중 | |
| Bit 3 | Macro 실행 중 | |
| Bit 4 | 오브젝트 풀 파싱 중 | v3 |
| Bit 6 | Auxiliary controls learn mode 활성 | v3 |
| Bit 7 | 메모리 부족 | |

Byte 8에는 지금 실행 중인 명령의 function 코드가 실린다. 이 값은 Bit 2나 Bit 3이 서 있을 때만 유효하고, 실행 중인 것이 없으면 `FF`다. 예를 들어 `FE 81 01 00 10 00 04 A8`은 "SA(소스 주소, 메시지를 보낸 ECU의 주소) `0x81`의 Working Set이 VT를 소유하고, Data Mask `0x0001`과 Soft Key Mask `0x0010`이 보이며, 지금 Change Numeric Value(`A8`)를 실행 중"이라는 뜻이다. 바이트별로 읽으면 다음과 같다.

| 바이트 | 값 | 뜻 |
|---|---|---|
| 1 | `FE` | VT Status 메시지 |
| 2 | `81` | VT를 차지한(active) Working Set Master의 소스 주소(SA) `0x81` |
| 3~4 | `01 00` | 보이는 Data Mask `0x0001` |
| 5~6 | `10 00` | 보이는 Soft Key Mask `0x0010` |
| 7 | `04` | 2진수 `0000 0100`, Bit 2(명령 실행 중) |
| 8 | `A8` | 실행 중인 명령: Change Numeric Value |

여기서 전송 조건을 같이 봐야 한다. VT Status는 Byte 2~6이 바뀌거나 <strong>Byte 7의 Bit 6</strong>이 바뀔 때, 그리고 초당 1회 보낸다. 최대 빈도는 초당 5회다. 다른 busy 비트가 바뀌는 것으로는 즉시 전송되지 않는다. 그래서 Working Set이 보는 busy 비트는 1초 간격의 표본일 뿐이다. 흐름 제어(상대가 처리할 수 있는 속도에 맞춰 보내는 일)는 busy 비트가 아니라 응답으로 해야 하고, busy 비트는 "VT가 왜 느린가"를 진단하는 단서로 쓴다.

Bit 6만 즉시 전송 조건에 들어간 이유는 표준에 적혀 있지 않다. AUX learn mode(운전자가 조이스틱 같은 실제 조작구를 움직여 보조 입력을 작업기 기능에 지정하는 할당 방식, [40장](/study/isobus/40-vt-aux))에서 기능 Working Set들이 이 비트를 보고 동작을 멈춰야 하기 때문으로 보인다.

<small>근거: ISO 11783-6 4.6.2, G.2, H.1</small>

## 5. 화면 갱신의 원칙

이 절은 명령을 얼마나 자주, 어떤 방식으로 보내야 하는지에 대한 권고를 본다. 결론은 보이는 변화가 있을 때만 보내고, 오브젝트는 같은 타입으로만 바꾸며, 지울 때는 풀 전체를 지운다는 것이다.

CAN 대역폭과 VT의 처리 능력은 모든 Working Set이 나눠 쓰는 자원이다. 그래서 표준은 다음을 권고한다(should).

- active Working Set, 또는 inactive지만 보이는 Working Set은 운전자에게 보이는 변화가 있을 때만 명령을 보낸다.
- 표시 중인 Data Mask·Soft Key Mask가 없는 inactive Working Set은 갱신 빈도를 줄이거나 갱신을 멈춘다.

active Working Set은 지금 VT 주 화면을 차지한 Working Set이고, 나머지는 inactive다. inactive라도 User-Layout 창([34장](/study/isobus/34-vt-layout-color))처럼 화면 한쪽에 보일 수 있다.

[36장](/study/isobus/36-vt-commands-basics) 5절 그림의 "100 ms 주기 갱신"은 예시일 뿐이고, 값이 바뀌지 않았으면 보내지 않는 편이 권고에 맞다. 그 밖의 규칙은 다음과 같다.

- 속성에는 AID(Attribute ID)가 붙어 있다. 읽기 전용이 아니면 Change Attribute로 바꿀 수 있고, 효율을 위해 여러 속성을 한 번에 바꾸는 전용 명령(Change Font Attributes 등)도 있다.
- 해당 Data Mask가 보이지 않아도 속성과 값은 바꿀 수 있다. 나중에 마스크가 활성화될 때 최신 데이터가 준비되어 있게 하려는 것이다.
- 런타임(풀을 올린 뒤 동작하는 중)에 오브젝트를 교체할 수 있지만 <strong>같은 타입</strong>으로만 바꿀 수 있다. 이미 있는 Object ID로 오브젝트를 TP로 보내면 기존 것이 교체되고, VT는 소스 주소로 소유자를 판단한다. 크기가 바뀌는 교체도 허용되지만 VT 메모리가 부족해질 수 있다.
- 오브젝트 하나만 지우는 명령은 없다. Delete Object Pool로 풀 전체를 지운 뒤, 그 오브젝트를 뺀 풀을 다시 올려야 한다.

<small>근거: ISO 11783-6 4.6.10.1, 4.6.10.2, 4.6.10.3</small>

## 6. 자주 쓰는 명령을 바이트로 읽기

이제 명령 하나하나로 내려간다. 이 절은 Working Set 프로그램에서 가장 자주 쓰는 명령을 골라 바이트로 조립하고 응답을 읽는다. 나머지 명령은 7절에서 기능별로 정리한다.

예시 Object ID는 [36장](/study/isobus/36-vt-commands-basics) 6절과 같은 풀(Working Set `0x0000`, Data Mask `0x0001`·`0x0002`, Output Number `0x000B`, Input Number `0x0028`)을 이어 쓴다. 모든 명령은 ECU→VT(PGN 59136(0xE700)), 응답은 VT→ECU(PGN 58880(0xE600))이다.

이 절과 7절의 바이트 표기는 같은 규칙을 따른다.

- 바이트 번호는 1부터 센다.
- 2바이트 이상 값은 리틀 엔디언이라 낮은 자리 바이트가 먼저 온다. `0x0028`은 `28 00`으로 실린다.
- 쓰지 않는 바이트와 예약 바이트는 `FF`로 채운다.
- 오류 비트는 Bit 0(가장 낮은 자리)부터 센다.

### 값 바꾸기: Change Numeric Value

<strong>Change Numeric Value(`A8`)</strong>의 바이트 배치는 [36장](/study/isobus/36-vt-commands-basics) 3절에서 봤다. Byte 2~3이 Object ID, Byte 4가 예약(`FF`), Byte 5~8이 새 값이다. 응답은 Byte 4 자리에 오류 코드를 넣는다.

Byte 5~8 값 크기는 대상 타입에 따라 다르다. 리틀 엔디언이고, 쓰지 않는 바이트는 0으로 채운다. 아래 표의 왼쪽은 실제로 쓰는 크기, 오른쪽은 그 크기를 쓰는 오브젝트다. 1바이트면 Byte 5만, 2바이트면 Byte 5~6만 쓰고 나머지는 `00`이다.

| 값 크기 | 대상 오브젝트 |
|---|---|
| 1바이트 | Input Boolean(TRUE/FALSE), Input List·Output List(v4부터)·Animation(v5부터)의 리스트 인덱스 |
| 2바이트 | Output Meter, Output Linear Bar Graph, Output Arched Bar Graph(정수), Object Pointer·Scaled Graphic(v6부터)의 Object ID |
| 4바이트 | Input Number, Output Number, Number Variable(정수) |
| 2 + 2바이트 | External Object Pointer(v5부터): Byte 5~6 External Reference NAME Object ID, Byte 7~8 참조 대상 Object ID |

예를 들어 Output Number `0x000B`에 150을 쓰는 4바이트 예는 `A8 0B 00 FF 96 00 00 00`이다. 1바이트 오브젝트인 Input List(예: `0x0030`)의 선택을 인덱스 2로 바꾸면 Byte 5에만 `02`를 넣어 `A8 30 00 FF 02 00 00 00`이 된다.

이 명령은 지정한 오브젝트의 value 속성만 바꾸고, 그 오브젝트가 참조하는 변수는 바꾸지 않는다. 그런데 Output Number는 Variable reference가 NULL이 아니면 값을 변수에서 읽는다. Variable reference는 "값을 이 Number Variable 오브젝트에서 가져오라"는 연결 속성이고, NULL(`0xFFFF`, 연결 없음)이면 자기 value 속성을 쓴다([33장](/study/isobus/33-vt-object-records)).

두 규정을 합치면 함정이 하나 나온다. <strong>변수를 참조하는 Output Number에 Change Numeric Value를 보내면, 화면에 보이는 값은 여전히 변수에서 오므로 바뀌지 않는다.</strong> 응답에 오류가 없어도 마찬가지다. 이때는 Number Variable 오브젝트의 ID로 보내야 하고, 그러면 그 변수를 참조하는 모든 오브젝트가 한 번에 갱신된다.

응답 Byte 4 Bit 1(Invalid value)은 포인터 값을 없는 오브젝트로 바꾸려 할 때만 선다. 포인터 값은 Object Pointer처럼 값이 다른 오브젝트의 ID인 경우다. 반면 무효 값을 담은 Change Numeric Value는 거부되고 매크로도 실행되지 않는다. 그러니 그 밖의 값 오류가 어느 비트로 표시될지는 표준이 정하지 않은 셈이다. Bit 1이 0이라고 값이 받아들여졌다고 단정하지 말고, Error Code 전체가 0인지를 본다. 업데이트 빈도는 Working Set 재량이지만 5절의 대역폭 권고를 고려하라고 표준이 덧붙인다.

### 값 바꾸기: Change String Value

<strong>Change String Value(`B3`)</strong>는 길이 규칙이 핵심이다. 명령의 바이트 배치는 다음과 같다. 여기서 대상 `0x0014`(20)는 문자열 오브젝트(예: Output String)라고 가정한다. 36장 5절의 버튼 ID와는 별개의 예시다.

| 바이트 | 내용 | "OK"를 보낼 때 |
|---|---|---|
| 1 | VT function 코드 `B3` | `B3` |
| 2~3 | 대상 오브젝트의 Object ID | `14 00` → `0x0014` |
| 4~5 | 보낼 문자열의 바이트 수(2바이트) | `02 00` → 2 |
| 6~ | 문자열 | `4F 4B` = "O", "K" |
| 남는 자리 | `FF`로 채움 | `FF` |

- Byte 4~5가 보낼 문자열의 바이트 수(2바이트)이고, Byte 6부터 문자열이 온다.
- 한 패킷에 들어가면 TP를 쓰면 안 된다. 헤더(function 코드, Object ID, 길이)가 5바이트이므로 문자열이 3바이트 이하일 때 한 프레임에 들어가고, 남는 바이트는 `FF`로 채운다. "OK"면 `B3 14 00 02 00 4F 4B FF`, "ABC"면 `B3 14 00 03 00 41 42 43`이다. "HELLO"는 10바이트가 되므로 TP로 간다.
- 보내는 문자열은 대상의 length 속성보다 짧아도 된다. 이때 VT가 나머지를 space로 채운다. 길이 속성보다 길게 보내면 안 된다. 이 명령으로 문자열 길이를 늘릴 수는 없다.

응답은 형식이 다르다. Byte 2~3이 Reserved `FF FF`이고 Object ID는 <strong>Byte 4~5</strong>, 오류는 Byte 6이다. 성공하면 `B3 FF FF 14 00 00 FF FF`, 길이 초과면 Byte 6 Bit 2(String too long)가 서서 `B3 FF FF 14 00 04 FF FF`가 된다. 다른 응답처럼 Byte 2~3에서 Object ID를 읽는 파서(받은 바이트를 해석하는 코드)는 여기서 틀린다.

또 하나의 함정은 길이 필드 크기다. 이 명령의 길이 필드는 2바이트지만, 반대 방향인 VT Change String Value message의 길이 필드는 1바이트다([39장](/study/isobus/39-vt-alarm-activation)).

### 화면 바꾸기: Change Active Mask, Change Soft Key Mask

<strong>Change Active Mask(`AD`)</strong>의 바이트는 [36장](/study/isobus/36-vt-commands-basics) 6절에서 봤다. 명령 `AD 00 00 02 00 FF FF FF`는 Byte 2~3에 Working Set 오브젝트 `0x0000`, Byte 4~5에 새 마스크 `0x0002`를 싣는다. 응답 `AD 02 00 00 FF FF FF FF`에는 Working Set Object ID가 반향되지 않고, Byte 2~3에 <strong>새 Active Mask ID</strong>가 실린다는 점만 기억하면 된다. 오류 코드는 Byte 4다.

inactive Working Set도 이 명령으로 자기 active mask를 바꿀 수 있다. 다음에 보이게 될 때 알맞은 마스크가 뜨게 하려는 것이다. Macro 안에서 실행하면 Change Active Mask response는 없지만, 화면이 바뀌므로 VT Status message는 나간다.

<strong>Change Soft Key Mask(`AE`)</strong>는 Byte 2의 Mask Type(1 = Data, 2 = Alarm), Byte 3~4의 마스크 ID, Byte 5~6의 새 Soft Key Mask ID로 이뤄진다. `AE 01 01 00 10 00 FF FF`는 Data Mask `0x0001`의 Soft Key Mask를 `0x0010`으로 바꾼다. 한 바이트씩 읽으면 Byte 2 `01`(Data Mask), Byte 3~4 `01 00`(`0x0001`), Byte 5~6 `10 00`(`0x0010`), Byte 7~8 `FF FF`(예약)다.

응답 Byte 6의 Bit 2(Missing Objects)와 Bit 3(마스크 또는 child 오류)은 새 Soft Key Mask 안의 참조 문제를 알린다. child는 마스크 안에 든 자식 오브젝트다. 눌려 있던 Soft Key가 이 명령으로 지워질 때의 처리는 [38장](/study/isobus/38-vt-macro-input)에서 본다.

### 숨기기와 켜고 끄기: Hide/Show Object, Enable/Disable Object

<strong>Hide/Show Object(`A0`)</strong>는 Container 오브젝트만 대상으로 한다. 가시성뿐 아니라 Container가 기억하는 hidden/shown 상태도 바꾼다. 명령은 Byte 2~3에 Container의 Object ID, Byte 4에 0(Hide) 또는 1(Show)을 싣는다. 응답은 Byte 2~4를 반향하고 Byte 5에 오류 코드를 싣는다. 아래 표는 명령 하나와 그 응답 두 가지(성공, 실패)를 나란히 놓았다.

| 프레임 | 바이트 | 의미 |
|---|---|---|
| 명령 | `A0 64 00 00 FF FF FF FF` | Container `0x0064`를 Hide(Byte 4 = 0) |
| 응답(성공) | `A0 64 00 00 00 FF FF FF` | Byte 2~4 반향, Byte 5 = 0 |
| 응답(실패) | `A0 64 00 00 02 FF FF FF` | Byte 5 Bit 1 = Invalid Object ID |

실패 응답의 Byte 5 `02`는 2진수 `0000 0010`이므로 Bit 1, 곧 Invalid Object ID(그런 오브젝트가 없음)다.

오류 Bit 0(누락된 child 참조)은 VT가 바로 보고해도 되고, Container가 실제로 보일 때까지 검사를 미뤘다가 VT Change Active Mask message로 보고해도 된다. Working Set은 두 경로를 모두 처리해야 한다. 이미 숨겨진 Container에 Hide를 다시 보내도 유효한 명령이므로 On Hide 매크로가 실행된다.

<strong>Enable/Disable Object(`A1`)</strong>는 입력 필드와 Button, 그리고 Animation 오브젝트에 쓴다. Button의 enable/disable은 v4부터다. 바이트 배치는 Hide/Show와 같은 꼴이다. Byte 4가 0이면 Disable, 1이면 Enable이고, 응답의 오류 코드는 Byte 5다. 예를 들어 Input Number `0x0028`을 disable하는 명령은 `A1 28 00 00 FF FF FF FF`다.

이미 enabled인 오브젝트를 다시 enable해도 응답은 "no errors"이고 매크로도 실행된다. 응답 Byte 5 Bit 3(완료 불가)은 그 입력 오브젝트를 운전자가 지금 편집 중이라는 뜻이다. [38장](/study/isobus/38-vt-macro-input)의 입력 상태 기계에서 "Data input 중 포커스 오브젝트 disable"이 이 경우다.

::: details 원문을 가진 독자를 위한 메모
- 원문 표의 오타: F.5(Enable/Disable Object response) 표는 Byte 1을 "VT function = 160"으로 인쇄했다. 그러나 같은 표의 비트 값(`1010`/`0001`)과 Table A.5는 161(`0xA1`)이다. 160은 Hide/Show의 코드이므로 구현은 `0xA1`을 따른다.
- 원문 F.22 표에서 Animation과 Scaled Graphic의 값 크기는 해당 오브젝트 정의와 대조해 읽어야 한다. Animation의 Value 속성은 1바이트 리스트 인덱스이고, Scaled Graphic의 Value 속성은 2바이트 Object ID다(B.25·B.28). 위 값 크기 표는 이 대조 결과를 따랐다.
- 이 절의 근거 조항: Change Numeric Value는 F.22~F.23(Bit 1은 F.23 각주, 변수 규칙은 B.9.3과 4.6.11.3, 무효 값 거부는 4.6.22.1 EXAMPLE 3), Change String Value는 F.24~F.25(반대 방향 메시지는 H.18), Change Active Mask는 F.34~F.35(4.6.8, 4.6.11.4), Change Soft Key Mask는 F.36~F.37, Hide/Show Object는 F.2~F.3(Bit 0 보고 시점은 F.3 각주, 다시 숨김은 4.6.22.1 EXAMPLE 4), Enable/Disable Object는 F.4~F.5다.
:::

<small>근거: ISO 11783-6 F.2~F.5, F.22~F.25, F.34~F.37</small>

## 7. 명령 세부: 기능별로 묶어 보기 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 장 끝의 핵심 정리로 가도 된다.
:::

이 절은 6절에서 다루지 않은 명령의 바이트 배치·오류 비트·구현 함정을 기능별로 묶었다. 필요한 명령만 골라 읽으면 된다. 예시 Object ID와 바이트 표기 규칙은 6절과 같다.

### 입력 포커스: Select Input Object, ESC

<strong>Select Input Object(`A2`)</strong>는 Working Set이 포커스를 강제로 옮기는 명령이다. 설정 마법사처럼 운전자의 주의를 특정 필드로 끌 때 쓴다. 아래 표는 바이트마다 명령과 응답의 내용을 나란히 적었다.

| 바이트 | 명령 | 응답 |
|---|---|---|
| 2, 3 | Object ID. NULL이면 포커스 제거(이때 Byte 4는 `FF`) | 반향 |
| 4 | Option: `FF` = 포커스만 설정, `00` = 데이터 입력용으로 열기(v4부터. Button·Key에는 무효) | Response: 0 = 선택 안 됨(NULL이거나 오류), 1 = 선택됨, 2 = 편집용으로 열림(v4부터) |
| 5 | Reserved `FF` | 오류: Bit 0 disabled, Bit 1 Invalid Object ID, Bit 2 활성 마스크에 없거나 숨긴 Container 안, Bit 3 다른 필드 입력 중이거나 Button·Soft Key가 눌린 채 유지 중, Bit 4 기타, Bit 5 Invalid Option(v4부터) |

Input Number `0x0028`을 열려면 `A2 28 00 00 FF FF FF FF`를 보낸다. 성공하면 `A2 28 00 02 00 FF FF FF`(Byte 4 = 2, 열림)가 오고, 운전자가 다른 필드를 편집 중이면 `A2 28 00 00 08 FF FF FF`(Byte 5 Bit 3)가 온다. 구현에서 조심할 점은 세 가지다.

- 입력용으로 열어도 값은 바뀌지 않는다. Input Boolean도 토글되지 않는다.
- Working Set이 이 명령으로 바꾼 포커스는 VT Select Input Object message로 통지되지 않는다. 포커스 상태는 이 응답으로 직접 갱신해야 한다.
- 화면 밖에 있거나 폭·높이가 0인 오브젝트도, enabled이고 숨긴 Container 안이 아니면 선택·열기가 모두 가능하다. 오류가 아니다. 같은 오브젝트가 한 마스크에 여러 번 들어 있으면 어느 인스턴스가 선택될지는 VT 재량이다.

<strong>ESC(`92`)</strong>는 Working Set이 운전자 입력을 강제로 중단시키는 명령이다. 명령은 `92 FF FF FF FF FF FF FF`로 파라미터가 없다. 응답 Byte 2~3에는 입력이 중단된 Object ID가 실리고(예: `92 28 00 00 FF FF FF FF`), 열려 있는 입력이 없으면 Byte 4 Bit 0이 선다. ESC는 Macro 안에서 쓸 수 없는 몇 안 되는 명령이다.

### 마스크 잠금: Lock/Unlock Mask

<strong>Lock/Unlock Mask(`BD`, v4부터)</strong>는 여러 변경을 운전자에게 한 번에 보이게 하는 장치다. 잠근다고 그리기가 멈추는 것은 아니다. 잠금이 풀릴 때까지 변경이 화면에 드러나지 않을 뿐이다. 아래 표에서 unsolicited는 "요청받지 않은", 곧 Working Set이 보내지 않았는데 VT가 먼저 보내는 응답을 뜻한다.

| 바이트 | 명령 | 응답 |
|---|---|---|
| 2 | 0 = Unlock, 1 = Lock | 반향 |
| 3, 4 | 대상 Data Mask 또는 User-Layout Data Mask ID. 보이는 마스크와 다르면 실패 | (Byte 3) 오류: Bit 0 무시(보이는 마스크 없음·ID 불일치), Bit 1 이미 잠김, Bit 2 잠기지 않음, Bit 3 Alarm Mask 활성으로 Lock 거부, Bit 4 unsolicited 해제(타임아웃), Bit 5 unsolicited 해제(마스크 숨겨짐), Bit 6 unsolicited 해제(운전자 등), Bit 7 기타 |
| 5, 6 | Lock timeout(ms), 0 = 무제한. Unlock에는 적용 안 됨 | |

Data Mask `0x0001`을 500 ms 타임아웃으로 잠그려면 `BD 01 01 00 F4 01 FF FF`를 보낸다. Byte 2 `01`이 Lock, Byte 3~4 `01 00`이 Data Mask `0x0001`, Byte 5~6 `F4 01`이 `0x01F4`, 곧 500 ms다. 표준이 권하는 쓰임은 "잠금 → 변경 명령들 → 잠금 해제 → 응답 대기"다. 잠금 시간은 밀리초 단위로 짧게 유지하라고 권고한다. Output Polygon의 점을 여러 개 바꿀 때 매번 다시 그려지지 않게 하는 데도 쓴다.

응답 시점이 비대칭이라는 점이 핵심이다. Lock에는 VT가 최대한 빨리 응답한다. Unlock에는 마스크가 보이는 경우 <strong>잠금 중 변경이 화면에 모두 반영된 뒤에야</strong> 응답한다. 그래서 Unlock 응답은 "화면 반영 완료" 확인으로 쓸 수 있다. 마스크가 숨겨진 상태(홈 화면·설정 화면 표시 중)면 즉시 Bit 0을 세워 응답한다.

잠금은 다음 경우에 자동으로 풀린다. 타임아웃, 그 마스크의 입력 오브젝트나 Button으로 이동하거나 활성화, 마스크가 숨겨짐, 풀 삭제, VT 고유 사유(입력 다이얼로그가 닫힘 등)다. 타임아웃이나 숨김으로 풀리면 VT는 요청받지 않은(unsolicited) Lock/Unlock Mask response를 보낸다. 따라서 Working Set은 자기가 보내지 않은 응답도 받을 준비를 해야 한다. 잠금 중에도 CAN 명령, 키·버튼 입력, 이벤트, 매크로는 정상 처리된다. Soft Key Mask와 Alarm Mask는 잠금과 무관하게 항상 표시된다. Lock을 받는 시점에 어느 Working Set이든 같은 표시 영역에 Alarm Mask가 활성이면 Lock은 거부된다.

### 소리: Control Audio Signal, Set Audio Volume

VT는 반드시 음향 경보 수단을 갖춰야 한다. 단순 on/off 부저여도 되고, 주파수와 음량을 바꿀 수 있는 부품이어도 된다. 어느 쪽인지는 Get Hardware response의 Byte 4로 알 수 있다. Bit 2가 다중 주파수, Bit 3이 음량 조절 지원이다([30장](/study/isobus/30-vt-display-technical-data)).

<strong>Control Audio Signal(`A3`)</strong>의 구조는 다음과 같다.

| 바이트 | 내용 |
|---|---|
| 2 | Activations: 0 = 이 Working Set이 낸 소리를 멈춤(주파수·시간 무시), 1~255 = 울림 횟수 |
| 3, 4 | 주파수(Hz). VT가 낼 수 없는 범위면 VT가 가능한 범위로 제한 |
| 5, 6 | On-time(ms). 0이 아니면서 VT 분해능보다 짧으면 VT의 최소 단위로 맞춤 |
| 7, 8 | Off-time(ms). On-time이 0이면 무시하고 0을 씀 |

2000 Hz로 100 ms 울리고 100 ms 쉬기를 3번 하려면 `A3 03 D0 07 64 00 64 00`이다. Byte 2 `03`이 3회, Byte 3~4 `D0 07`이 `0x07D0`(2000 Hz), Byte 5~6과 Byte 7~8의 `64 00`이 각각 `0x0064`(100 ms)다. 동작 규칙은 다음과 같다.

- 같은 Working Set이 낸 소리가 진행 중이면 새 명령이 그것을 끊고 대체한다. 끊길 때 소리가 잠깐 멈출 수 있다. Alarm Mask에 연결된 소리에는 이 대체 규칙이 적용되지 않는다.
- 연속음은 권고하지 않지만, 255회 × 65 535 ms로 약 278분 동안 울릴 수 있다. 더 길게 필요하면 끝나기 전에 명령을 다시 보낸다.
- 한 번에 한 Working Set의 소리만 낼 수 있는 VT가 다른 Working Set의 소리를 내는 중이면 응답 Byte 2 Bit 0(Audio device busy)을 세운다. 여러 Working Set의 소리를 동시에 낼 수 있는("multisound") VT는 능력 한도까지 받는다.
- 이 명령의 소리는 일반 메시지 처리 지연 이상으로 큐에 쌓이거나 늦춰지면 안 된다.
- active Working Set과 무관하게 동작한다. inactive Working Set도 소리를 낼 수 있다.

<strong>Set Audio Volume(`A4`)</strong>은 Byte 2에 운전자가 설정한 최대 음량 대비 퍼센트(0~100 %)를 싣는다. 50 %면 `A4 32 FF FF FF FF FF FF`이다. 보낸 Working Set의 이후 Control Audio Signal에 적용되고, 지금 울리는 소리에도 적용하는 것이 권고다(should). 지금 소리의 음량을 못 바꾸는 VT는 응답에 busy 비트를 세운다. 다른 Working Set의 음량과 Alarm Mask의 음량에는 영향을 주지 않는다.

기본 음량은 v4 이하에서 정의되지 않았고, v5부터 운전자 설정 최대 음량의 100 %다. 표준이 요구하는 것은 아니지만, v4 이하 VT에서도 일정한 음량을 원하면 이 명령을 먼저 보내 두는 편이 안전하다. 응답 Bit 1(명령 미지원)은 v5부터 정의된다.

### 위치·크기·색: Change Child Location/Position, Change Size, Change Background Colour, Change End Point

<strong>Change Child Location(`A5`)</strong>은 현재 위치에서 상대적으로 옮긴다. 한 오브젝트가 여러 부모에 들어갈 수 있으므로 부모 Object ID를 함께 준다. 이동량은 −127 오프셋으로 인코딩한다. 실제 이동량에 127을 더한 값을 한 바이트에 싣는 방식이다. 원시값 0이 −127픽셀, 127이 이동 없음, 255가 +128픽셀이다. 양수는 오른쪽(X)·아래(Y)다.

Data Mask `0x0001` 안의 `0x000B`를 오른쪽으로 10픽셀, 위로 5픽셀 옮기면 X = 127 + 10 = `0x89`, Y = 127 − 5 = `0x7A`이므로 `A5 01 00 0B 00 89 7A FF`가 된다. 응답 Byte 6의 Bit 0은 부모가 없거나 대상의 부모가 아님을, Bit 1은 대상이 없거나 이 명령을 쓸 수 없는 오브젝트임을 뜻한다.

상대 이동이라 메시지가 유실되면 위치가 틀어진 채 남고, 재전송하면 이중으로 움직인다. 정확한 위치가 필요하면 절대 좌표를 쓰는 Change Child Position을 쓰라고 표준이 권고한다. 부모가 같은 child를 여러 번 포함하면 모든 인스턴스가 함께 움직이고, 부모는 다시 그려진다.

<strong>Change Child Position(`B4`)</strong>은 부모 좌상단 기준 절대 좌표를 부호 있는 16비트로 준다. X = 200, Y = −10이면 `B4 01 00 0B 00 C8 00 F6 FF`인데, 길이가 <strong>9바이트</strong>다. CAN 데이터 프레임 하나(8바이트)에 들어가지 않으므로 목적지 지정 TP(CMDT)로 보내야 한다([15장](/study/isobus/15-tp-bam-cmdt)). 응답은 8바이트이고 오류 비트 구성은 Change Child Location과 같다.

<strong>Change Size(`A6`)</strong>는 `A6 0B 00 78 00 28 00 FF`처럼 Object ID, 폭, 높이를 준다(예: 120×40). 폭이나 높이가 0이면 크기 0으로 취급되어 그려지지 않는다. 응답 오류는 Byte 4 Bit 0(Invalid Object ID)과 Bit 4(기타)뿐이다.

<strong>Change Background Colour(`A7`)</strong>는 `A7 01 00 0C FF FF FF FF`처럼 Object ID와 색 인덱스를 준다. 색 인덱스는 VT 표준 팔레트의 번호다([34장](/study/isobus/34-vt-layout-color)). 인덱스 12는 표준 팔레트의 Red다. 응답 Byte 5 Bit 1은 Invalid colour code다.

<strong>Change End Point(`A9`)</strong>는 Output Line의 끝점을 폭·높이·Line Direction으로 바꾼다. Byte 2~3이 Object ID, 4~5가 폭, 6~7이 높이, 8이 Line Direction이다. 응답 Byte 4 Bit 1은 Invalid Line Direction이다.

### 속성 바꾸기: Change Font/Line/Fill Attributes, Change Attribute, Change Priority, Change List Item

<strong>Change Font·Line·Fill Attributes(`AA`·`AB`·`AC`)</strong>는 Attribute 오브젝트의 속성을 한 번에 바꾼다. 하나의 Attribute 오브젝트를 여러 오브젝트가 참조하므로, 명령 하나로 그 오브젝트들의 모양이 함께 바뀐다. 아래 표의 각 줄은 명령 하나이고, 가운데 세 칸은 명령의 Byte 4, 5, 6~7에 싣는 속성, 마지막 칸은 응답 오류 코드(Byte 4)의 비트 뜻이다.

| 명령 | Byte 4 | Byte 5 | Byte 6~7 | 응답 오류(Byte 4) |
|---|---|---|---|---|
| Change Font Attributes | Font colour | Font size | Byte 6 Font type, Byte 7 Font style | Bit 0 ID, 1 colour, 2 size, 3 type, 4 style, <strong>5 기타</strong> |
| Change Line Attributes | Line colour | Line width | Line Art(16비트 패턴) | Bit 0 ID, 1 colour, 2 width, 4 기타 |
| Change Fill Attributes | Fill type | Fill colour | Fill pattern Object ID | Bit 0 ID, 1 type, 2 colour, 3 pattern ID, 4 기타 |

<strong>Change Attribute(`AF`)</strong>는 AID가 붙은 속성을 범용으로 바꾼다. 문자열은 바꿀 수 없다. [33장](/study/isobus/33-vt-object-records)의 AID 표에서 대괄호로 둘러싼 속성(예: Output Number의 Value `[12]`)은 읽기 전용이다. 이런 속성은 Get Attribute Value로 읽을 수만 있고 Change Attribute로 쓸 수 없다. Output Number의 값을 바꾸려면 Change Attribute가 아니라 Change Numeric Value를 써야 하는 이유가 이것이다.

값 크기는 데이터 타입을 따른다. Boolean과 Bitmask는 1바이트, Integer는 오브젝트 표에 정한 1·2·4바이트, Float는 4바이트(IEEE 754 단정밀도, 소수를 32비트로 나타내는 국제 표준 형식)다. 리틀 엔디언으로 보내고 남는 바이트는 0으로 채운다. Output Number `0x000B`의 Scale(AID 8)을 0.1로 바꾸면 0.1의 단정밀도 표현이 `0x3DCCCCCD`이므로 `AF 0B 00 08 CD CC CC 3D`가 된다. Byte 4 `08`이 AID 8이고, Byte 5~8은 `0x3DCCCCCD`를 리틀 엔디언으로 쓴 것이다. 응답 Byte 5의 Bit 1은 Invalid Attribute ID, Bit 2는 Invalid value다.

<strong>Change Priority(`B0`)</strong>는 Alarm Mask의 priority 속성(0 = High, 1 = Medium, 2 = Low)을 바꾼다. 받으면 VT는 활성 마스크 전체의 우선순위를 다시 평가하고, 그 결과로 화면이 다른 Working Set으로 넘어갈 수 있다. 응답 Byte 5 Bit 1은 Invalid priority다. 우선순위 규칙은 [39장](/study/isobus/39-vt-alarm-activation)에서 본다.

<strong>Change List Item(`B1`)</strong>은 Input List, Output List(v4부터), Animation과 External Object Definition(v5부터)의 리스트 항목을 바꾼다. Byte 4가 0부터 시작하는 인덱스, Byte 5~6이 새 Object ID다. `FFFF`를 주면 그 자리를 빈 항목으로 만든다. Input List `0x0030`의 2번 항목을 `0x0045`로 바꾸면 `B1 30 00 02 45 00 FF FF`, 비우면 `B1 30 00 02 FF FF FF FF`다. 응답 오류는 Byte 7에 있다. Bit 0은 리스트 오브젝트 ID, Bit 1은 인덱스, Bit 2는 새 항목 ID가 잘못됐다는 뜻이다.

### 그 밖의 명령

- <strong>Execute Macro(`BE`)·Execute Extended Macro(`BC`)</strong>: 매크로를 직접 실행한다. Execute Macro는 Byte 2 한 바이트에 Macro ID를 실으므로 ID 255 이하만 실행할 수 있다(`BE 32 FF FF FF FF FF FF`). v5의 Execute Extended Macro는 Byte 2~3에 2바이트 ID를 싣는다(`BC 2C 01 FF FF FF FF FF` = Macro 300). 응답 오류 비트는 Bit 0 = ID 없음, Bit 1 = Macro 오브젝트 아님, Bit 2 = 기타다. 매크로 규칙은 [38장](/study/isobus/38-vt-macro-input)에서 본다.
- <strong>Change Object Label(`B5`, v4부터)</strong>: Byte 2~3은 라벨을 붙일 오브젝트, 4~5는 라벨 문자열(최대 32자)을 담은 String Variable(없으면 `FFFF`), 6은 Font type, 7~8은 라벨 그래픽으로 쓸 오브젝트(없으면 `FFFF`)다. Font type은 String Variable이 NULL이거나 WideString이면 무시된다. 그래픽은 Soft Key designator 크기로 잘린다. 응답 Byte 2의 Bit 0은 대상이 Object Label Reference List에 없음, Bit 3은 풀에 그 리스트 자체가 없음, Bit 5는 기타다.
- <strong>Change Polygon Point(`B6`)·Change Polygon Scale(`B7`, v4부터)</strong>: Point는 0부터 세는 점 인덱스와 폴리곤 좌상단 기준 새 X·Y를 준다. Scale은 폭과 높이를 바꾸면서 모든 점을 32비트 부호 없는 정수 연산 `new_x = (old_x × new_width + old_width / 2) / old_width`로 다시 계산한다. 구현 간 결과를 맞추려고 표준이 식을 고정했다. 폭 100을 150으로 키우면 x = 33은 50, x = 67은 101이 된다. 정수 연산이라 키웠다 줄이기를 반복하면 반올림 오차가 점 좌표에 쌓인다. 표준에 적힌 권고는 아니지만, 원래 크기로 정확히 돌아가야 하면 Change Polygon Point로 원래 점을 다시 넣는 편이 안전하다.
- <strong>Graphics Context(`B8`, v4부터)</strong>: Byte 2~3이 Graphics Context 오브젝트, Byte 4가 서브커맨드 ID, Byte 5부터 파라미터다. 8바이트보다 길면 TP로, 짧으면 `FF`로 채운다. 커서에서 (+40, −20) 떨어진 점까지 선을 긋는 Draw Line(서브커맨드 9)은 `B8 50 00 09 28 00 EC FF`다. 응답 Byte 5의 Bit 3은 "서브커맨드가 무효한 결과를 낸다"는 뜻이다. 서브커맨드 21종 목록은 [ISO 11783-6 부록](/study/isobus/appendix-iso-part06)에 있다.
- <strong>Get Attribute Value(`B9`, v4부터)</strong>: 명령이 아니라 질의 메시지라 Macro에서 쓸 수 없다. `B9 0B 00 08 FF FF FF FF`(Output Number의 Scale 요청)를 보내면, 성공 응답의 Byte 5~8에 현재 값이 온다. 오류 응답은 형식이 바뀐다. Byte 2~3이 `FFFF`가 되고 Object ID는 Byte 5~6으로, 오류는 Byte 7로 옮겨 간다. 없는 AID `0x20`을 물으면 `B9 FF FF 20 0B 00 02 FF`(Bit 1 Invalid Attribute ID)가 온다. 그래서 이 응답의 파서는 Byte 2~3이 `FFFF`인지부터 확인해야 한다.
- <strong>Select Colour Map or Palette(`BA`, v4부터)</strong>: Byte 2~3에 Colour Map(v6부터 Colour Palette도 가능) Object ID를 주고, `FFFF`면 기본 색 매핑(표준 팔레트, [34장](/study/isobus/34-vt-layout-color))으로 돌아간다. 보낸 Working Set의 <strong>모든 표시</strong>에 적용되며, 다른 Working Set 화면에 나타나는 자기 오브젝트(예: Auxiliary Control Designator로 표시되는 AUX 오브젝트)도 포함된다. 실행에 오래 걸릴 수 있다고 표준이 명시한다.
- <strong>Select Active Working Set(`90`, v6부터)</strong>: <strong>현재 active Working Set</strong>만 보낼 수 있고, 다른 Working Set Master의 NAME(ECU마다 고유한 64비트 이름, [12장](/study/isobus/12-j1939-address-name))을 Byte 2~9에 실어 그쪽으로 화면을 넘긴다. 대상의 Selectable 속성이 0이어도 active mask가 Data Mask면 활성화할 수 있다. 메시지가 가는 사이에 active Working Set이 바뀔 수 있으므로 반드시 응답으로 성공 여부를 확인해야 한다. 응답 Byte 2의 Bit 0은 active Working Set이 보낸 것이 아님, Bit 1은 현재 active mask가 Alarm Mask, Bit 2는 NAME이 WSM(Working Set Master)이 아님, Bit 3은 그 WSM의 풀이 없음, Bit 4는 active Data Mask 없음, Bit 7은 기타다. 오류 비트가 하나라도 서면 화면은 바뀌지 않는다. 명령은 Byte 1과 NAME 8바이트를 합쳐 9바이트라 한 CAN 프레임에 들어가지 않는다. 그래서 Change Child Position처럼 TP로 보내야 한다고 보는 것이 자연스럽지만, 표준 표의 길이 표기가 이와 어긋나 확인이 필요하다(아래 메모). 응답은 8바이트다.
- <strong>Delete Object Pool(`B2`)</strong>: 휘발성 메모리의 풀 전체를 지운다. Macro에서 쓸 수 없다. 비휘발성 메모리에 저장한 버전은 Delete Version으로 지운다([31장](/study/isobus/31-vt-connection)).
- <strong>Identify VT(`BB`, v4부터)</strong>: 보통 전역 주소로 보낸다. 받은 VT는 Alarm Mask가 활성이 아닐 때만 3초 동안 VT Number(function instance + 1, 1~32)를 화면에 띄운다. 응답은 목적지 지정으로 받았을 때만 보낸다. Macro에서 쓸 수 없다. 기술 데이터 메시지는 [30장](/study/isobus/30-vt-display-technical-data)에서, VT Number는 [31장](/study/isobus/31-vt-connection)에서 다룬다.

::: details 원문을 가진 독자를 위한 메모
- 원문 표기 불일치(Select Active Working Set의 길이): F.64 표는 Data length를 "8 bytes"로 적었다. 그런데 Byte 1(function)과 Byte 2~9(NAME 8바이트)를 합치면 9바이트다. 한 CAN 프레임에 들어가지 않으므로 Change Child Position처럼 TP로 보내야 한다고 읽는 것이 자연스럽다(확인 필요). 응답은 8바이트다.
- 이 절의 근거 조항: Select Input Object F.6~F.7(쓰임은 4.6.17, 값 불변은 F.6 NOTE 1, 통지 없음은 H.8 NOTE 1, 화면 밖 선택은 F.7 NOTE), ESC F.8~F.9(Macro 불가는 Table A.5), Lock/Unlock Mask F.46~F.47(Polygon 용도는 F.52 NOTE 2), 음향 수단 4.3과 Get Hardware D.9, Control Audio Signal F.10~F.11, Set Audio Volume F.12~F.13, Change Child Location F.14~F.15, Change Child Position F.16~F.17, Change Size F.18~F.19, Change Background Colour F.20~F.21(표준 팔레트 A.3), Change End Point F.26~F.27, Font·Line·Fill Attributes F.28~F.33(4.6.11.2), Change Attribute F.38~F.39(읽기 전용 표기 A.1.2), Change Priority F.40~F.41, Change List Item F.42~F.43, Delete Object Pool F.44~F.45(Delete Version E.8), Execute Macro F.48~F.49, Change Object Label F.50~F.51, Change Polygon Point·Scale F.52~F.55(식은 F.54), Graphics Context F.56~F.57, Get Attribute Value F.58~F.59, Select Colour Map or Palette F.60~F.61, Execute Extended Macro F.62~F.63, Select Active Working Set F.64~F.65, Identify VT D.18.
:::

아래 코드는 이 장에서 다룬 오류 코드 해석과 명령 조립을 파이썬으로 검산한다. `ERR` 표는 2절의 오류 바이트 위치 표를 코드로 옮긴 것이고, `decode_error()`는 응답의 function 코드로 오류 바이트를 찾아 켜진 비트의 이름을 돌려준다. 주석 괄호 속의 영문자·숫자 번호는 표준 문서의 절 번호라서 몰라도 코드를 읽는 데 지장이 없다.

::: details 오류 코드 해석과 명령 조립 검산 (Python)
```python
import struct

def le(v, n):
    return list(v.to_bytes(n, "little"))

def pad8(b):
    return b + [0xFF] * (8 - len(b))

def hx(b):
    return " ".join(f"{x:02X}" for x in b)

# 응답 오류 코드 바이트 위치와 비트 이름 (Part 6 Annex F, 일부)
ERR = {
    0xA0: (5, {0: "누락 child 참조", 1: "Invalid Object ID", 2: "Command error", 4: "기타"}),
    0xA2: (5, {0: "disabled", 1: "Invalid Object ID", 2: "활성 마스크에 없음/숨김",
               3: "다른 입력 진행 중", 4: "기타", 5: "Invalid Option"}),
    0xA8: (4, {0: "Invalid Object ID", 1: "Invalid value(포인터)", 4: "기타"}),
    0xAA: (4, {0: "Invalid Object ID", 1: "colour", 2: "size", 3: "type", 4: "style", 5: "기타"}),
    0xB3: (6, {1: "Invalid Object ID", 2: "String too long", 3: "기타"}),
    0xBD: (3, {0: "무시: 마스크 불일치", 1: "이미 잠김", 2: "잠기지 않음", 3: "Alarm 활성",
               4: "unsolicited: timeout", 5: "unsolicited: 숨겨짐", 6: "unsolicited: 운전자 등", 7: "기타"}),
}

def decode_error(frame):
    pos, names = ERR[frame[0]]
    code = frame[pos - 1]
    return [names.get(b, f"bit{b}") for b in range(8) if code >> b & 1]

# 1) 응답 해석
assert decode_error([0xA0, 0x64, 0x00, 0x00, 0x02, 0xFF, 0xFF, 0xFF]) == ["Invalid Object ID"]
assert decode_error([0xA2, 0x28, 0x00, 0x00, 0x08, 0xFF, 0xFF, 0xFF]) == ["다른 입력 진행 중"]
assert decode_error([0xB3, 0xFF, 0xFF, 0x14, 0x00, 0x04, 0xFF, 0xFF]) == ["String too long"]
assert decode_error([0xAA, 0x1E, 0x00, 0x20, 0xFF, 0xFF, 0xFF, 0xFF]) == ["기타"]   # Font: 기타는 Bit 5

# 2) 명령 조립
assert hx(pad8([0xA0] + le(0x64, 2) + [0])) == "A0 64 00 00 FF FF FF FF"          # Hide
assert hx(pad8([0xA2] + le(0x28, 2) + [0x00])) == "A2 28 00 00 FF FF FF FF"        # Select(열기)
assert hx([0xA3, 3] + le(2000, 2) + le(100, 2) + le(100, 2)) == "A3 03 D0 07 64 00 64 00"
assert 255 * 65535 / 60000 > 278                                                   # 약 278.5분
ccl = [0xA5] + le(0x0001, 2) + le(0x000B, 2) + [127 + 10, 127 - 5, 0xFF]
assert hx(ccl) == "A5 01 00 0B 00 89 7A FF"                                        # +10, -5 px
ccp = [0xB4] + le(0x0001, 2) + le(0x000B, 2) + list(struct.pack("<hh", 200, -10))
assert len(ccp) == 9 and hx(ccp) == "B4 01 00 0B 00 C8 00 F6 FF"                    # 9바이트 -> TP
csv = [0xB3] + le(0x0014, 2) + le(2, 2) + list(b"OK")
assert hx(pad8(csv)) == "B3 14 00 02 00 4F 4B FF"
assert len([0xB3] + le(0x0014, 2) + le(5, 2) + list(b"HELLO")) == 10              # 10바이트 -> TP
attr = [0xAF] + le(0x000B, 2) + [8] + list(struct.pack("<f", 0.1))
assert hx(attr) == "AF 0B 00 08 CD CC CC 3D"                                       # Scale(AID 8) = 0.1
assert hx(pad8([0xBD, 1] + le(0x0001, 2) + le(500, 2))) == "BD 01 01 00 F4 01 FF FF"
assert hx(pad8([0xBC] + le(300, 2))) == "BC 2C 01 FF FF FF FF FF"
gc = [0xB8] + le(0x0050, 2) + [9] + list(struct.pack("<hh", 40, -20))
assert hx(gc) == "B8 50 00 09 28 00 EC FF"                                         # Draw Line
assert hx([0xB9, 0xFF, 0xFF, 0x20] + le(0x000B, 2) + [0x02, 0xFF]) == "B9 FF FF 20 0B 00 02 FF"

# 3) Change Polygon Scale (F.54, 32비트 부호 없는 정수 연산)
def poly_scale(old, old_w, new_w):
    return (old * new_w + old_w // 2) // old_w

assert [poly_scale(x, 100, 150) for x in (0, 33, 67, 100)] == [0, 50, 101, 150]

# 4) 버튼 홀드와 TAN 재시도 (H.4, H.1): 38장 9절 표
def button(code, tan):
    return [0x01, code] + le(0x0014, 2) + le(0x0001, 2) + [0x01, tan << 4 | 0xF]

seq = [button(1, 1), button(2, 2), button(2, 3), button(0, 4), button(0, 4)]
assert hx(seq[0]) == "01 01 14 00 01 00 01 1F"
assert seq[3] == seq[4]                      # 뗌 재시도는 TAN을 바꾸지 않는다
print("block A: OK")
```
모든 `assert`가 통과하면 마지막 줄 `block A: OK`가 출력된다. 1번 묶음은 응답 해석, 2번은 명령 조립, 3번은 Change Polygon Scale 식을 검산한다. 4번 묶음은 [38장](/study/isobus/38-vt-macro-input)의 "버튼 홀드와 TAN 재시도" 예제 표에 나오는 프레임을 만든다.
:::

<small>근거: ISO 11783-6 4.3, 4.6.17, D.9, D.18, E.8, F.6~F.21, F.26~F.33, F.38~F.65, H.1, H.4, Table A.5</small>

::: tip 핵심 정리
- VT 메시지는 첫 바이트(VT function 코드)와 PGN을 함께 봐야 정체를 안다. 명령과 그 응답은 같은 코드를 쓴다.
- 응답은 받은 명령을 비춘다. 성공 여부는 반향된 값이 아니라 오류 코드로 판단하고, 오류 바이트의 위치와 "기타 오류" 비트는 명령마다 다르다.
- 명령은 응답을 받은 뒤 다음 것을 보내고, 1.5 s 동안 응답이 없으면 다음 명령을 보낼 수 있다. 상대 이동처럼 누적되는 명령은 재전송을 조심한다.
- 응답은 Working Set과 VT가 모두 v4 이상일 때만 명령을 보낸 CF로 가고, 다른 조합에서는 Master로 간다. 운전자 입력은 언제나 Master로 간다.
- 보이는 변화가 있을 때만 명령을 보내고, 오브젝트 교체는 같은 타입으로만, 삭제는 풀 전체로만 한다.
- Change String Value 응답과 Get Attribute Value의 오류 응답은 Object ID 자리가 옮겨 가므로 따로 파싱한다.
:::

::: details 확인 문제
1. PGN `0xE600`에 실린 프레임 `A8 0B 00 00 78 00 00 00`을 받았다. 무슨 프레임이고, 명령은 성공했는가?
2. 응답에 실린 값이 보낸 명령의 값과 같다. 오브젝트가 그 값으로 바뀌었다고 봐도 되는가?
3. Change Child Location 명령의 응답이 1.5 s 동안 오지 않았다. 같은 명령을 그대로 다시 보내도 괜찮은가?
4. (심화) Working Set 버전 3인 작업기의 member가 버전 4 VT에 명령을 보냈다. 응답은 누구에게 가는가? member는 응답을 어떻게 찾아야 하는가?
5. (디코딩) Change String Value를 보냈더니 VT에서 `B3 FF FF 14 00 04 FF FF`가 돌아왔다. 어느 오브젝트에서 무엇이 실패했는가? Working Set은 무엇을 고쳐야 하는가?

**답 가이드**
1. Byte 1이 `A8`이고 VT→ECU 방향이므로 Change Numeric Value 명령에 대한 VT의 응답이다. 오류 바이트(Byte 4)가 `00`이므로 성공이다. Object ID `0x000B`와 값 120(`78 00 00 00`)은 보낸 명령의 반향이다.
2. 아니다. 응답은 받은 명령을 비출 뿐 오브젝트의 현재 상태를 알려 주지 않는다. 오류 코드가 0일 때만 반영된 것으로 본다. 지금 값이 필요하면 Get Attribute Value로 묻는다.
3. 조심해야 한다. 응답만 늦었고 첫 명령이 이미 처리됐다면, 상대 이동이 두 번 적용되어 두 번 움직인다. 정확한 위치가 필요하면 절대 좌표를 쓰는 Change Child Position을 쓴다.
4. 구성 2(Working Set 3 이하, VT 4 이상)이므로 응답은 Working Set Master로 간다. member는 Master 주소로 가는 목적지 지정 VT 메시지를 엿들어 자기 명령의 응답을 찾아야 한다.
5. Byte 1 `B3`은 Change String Value response다. 이 응답은 Object ID가 Byte 4~5에 있으므로 대상은 `0x0014`다. Byte 6 = `0x04`는 Bit 2(String too long)다. 보낸 바이트 수가 대상의 length 속성을 넘었다. 이 명령으로는 문자열 길이를 늘릴 수 없으므로(6절), 문자열을 줄이거나 더 긴 length로 정의한 같은 타입의 오브젝트를 다시 올려야 한다(5절의 오브젝트 교체 규칙).
:::

## 다음 챕터

- 다음: [38장 매크로와 운전자 입력 처리](/study/isobus/38-vt-macro-input)
