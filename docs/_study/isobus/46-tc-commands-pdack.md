---
title: "프로세스 데이터 명령: 니블, PDACK, 측정 명령"
description: "프로세스 데이터 메시지의 명령 니블 16가지를 구분하고, 확인 응답 PDACK와 측정 명령(measurement)을 바이트 단위로 읽는다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, TaskController, TC, ProcessData, PDACK, Measurement]
prev: /study/isobus/45-tc-process-data-basics
next: /study/isobus/47-tc-totals-logging-peer
---

# 프로세스 데이터 명령: 니블, PDACK, 측정 명령

::: info 학습 목표
- 가장 자주 쓰는 명령 세 가지(값 요청 2, 값 전달·설정 3, 측정 설정 4~8)를 바이트에서 알아볼 수 있다.
- 명령 니블(`0x0`~`0xF`)을 보고 나머지 바이트를 어떻게 읽어야 하는지 고를 수 있다.
- PDACK 8바이트를 풀어 어떤 명령에 대한 답인지, 수락인지 거부인지 판단할 수 있다.
- measurement 명령으로 "언제 값을 보낼지"를 설정하고, 트리거를 여러 개 걸었을 때의 동작을 설명할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [45장 TC 프로세스 데이터 기초](/study/isobus/45-tc-process-data-basics), [43장 TC 연결 관리](/study/isobus/43-tc-connection)
- 이 장에서 처음 나오는 말
  - 명령 니블(command nibble): Byte 1 아래 4비트에 든 명령 번호. 니블은 4비트, 즉 16진수 한 자리다.
  - PDACK(Process Data Acknowledge): 명령을 받아들였는지 거절했는지 알리는 확인 응답 메시지
  - 오류 비트: PDACK 안에서 거절 이유를 비트 하나에 하나씩 표시한 것
  - 트리거(trigger): 클라이언트가 측정값을 보내게 만드는 조건(시간 간격, 거리 간격, 임계값, 변화량)
  - 기본 우선순위: CAN ID 맨 앞 3비트에 넣는 값. 숫자가 작을수록 버스에서 먼저 나간다.
:::

은행 창구의 서식을 떠올려 보자. 같은 크기의 용지라도 맨 위 칸에 "입금", "조회", "해지" 중 무엇을 표시했느냐에 따라 아래 칸을 읽는 법이 달라진다. 프로세스 데이터 메시지도 같다. 45장에서 본 것처럼 Byte 1 아래 4비트가 명령이고, 이 명령에 따라 나머지 바이트의 뜻이 달라진다. 이 장은 가장 자주 쓰는 명령 세 가지를 먼저 익히고, 16가지 명령 전체 지도, 명령에 대한 답장인 PDACK, 측정을 거는 명령(measurement)의 세부를 차례로 본다.

이 장에서 TC(Task Controller)는 TC 서버를, 클라이언트는 TC에 연결해 일하는 작업기 쪽 ECU를 말한다.

## 1. 먼저 알아야 할 명령 세 가지

명령 값은 16가지지만 실제 버스 로그의 대부분은 세 가지다. 이 절은 그 셋을 예시 프레임과 함께 먼저 본다. 나머지는 2절의 지도에서 필요할 때 찾으면 된다. 예시는 모두 45장의 살포기에서 섹션 3(Element 3)을 대상으로 한다.

| 하고 싶은 일 | 명령 | 보내는 쪽 → 받는 쪽 | 예시 프레임 | 뜻 |
|---|---|---|---|---|
| 값 요청 | 2 Request value | TC → 클라이언트 | `32 00 02 00 00 00 00 00` | Element 3의 DDI 2(실제 살포량)를 알려 달라 |
| 값 전달·설정 | 3 Value command | TC → 클라이언트, 클라이언트 → TC | `33 00 01 00 80 84 1E 00` | Element 3의 DDI 1(목표 살포량)은 200 L/ha다 |
| 측정 설정 | 4~8 measurement | TC → 클라이언트 | `34 00 02 00 E8 03 00 00` | Element 3의 DDI 2를 1000 ms마다 보내라 |

세 프레임 모두 Byte 1의 위 4비트는 3(Element 3)이고 아래 4비트가 명령이다. 그래서 첫 바이트가 `32`, `33`, `34`로 끝자리만 다르다.

### 값 요청(2)과 그 답(3)

TC가 `32 00 02 00 00 00 00 00`을 보내면 클라이언트는 같은 Element와 DDI에 현재 값을 실어 Value command(3)로 답한다. 예를 들어 `33 00 02 00 60 36 1E 00`(198 L/ha)이다. 값 요청의 답이 3이라는 점이 처음에는 헷갈린다. 3은 "값을 담은 메시지"라는 뜻이라 설정에도 응답에도 쓴다(4절).

### 값 설정(3)

TC가 목표값을 내릴 때도 3을 쓴다. 클라이언트는 받아들이면 아무 답도 하지 않고, 거절할 때만 PDACK를 보낸다(5절). 성공까지 확인받고 싶으면 `0xA`(=10) Set Value and Acknowledge를 쓴다(4절).

### 측정 설정(4~8)

measurement 명령은 값을 나르지 않고 "언제 값을 보내라"를 설정한다. 4는 시간 간격(ms), 5는 거리 간격(mm), 6과 7은 임계값, 8은 변화량이다. 클라이언트는 수락하면 PDACK(오류 없음)와 함께 그 시점의 값을 한 번 보내고, 그 뒤로 조건이 될 때마다 Value command(3)로 값을 보낸다(7절).

::: tip 정리
- 2는 "알려 달라", 3은 "값은 이것이다(또는 이 값으로 맞춰라)", 4~8은 "이 조건마다 알려 달라"다.
- 3으로 설정하면 성공은 조용하고 실패만 PDACK로 온다.
:::

## 2. Command 니블 전체 지도: `0x0`부터 `0xF`까지

이 절은 16가지 명령 값 전체를 한 표로 본다. 받은 메시지를 해석하는 프로그램(파서)은 이 니블부터 보고 나머지 바이트를 읽는 방법을 고른다.

45장과 1절은 command 2·3·4~8·A·D만 다뤘다. Byte 1 하위 4비트(SPN 5199, 0~15)는 16개 값을 가질 수 있고, 값마다 나머지 바이트를 읽는 법이 다르다. SPN(Suspect Parameter Number)은 메시지 안의 값 하나하나에 붙인 번호다([9장](/study/isobus/09-j1939-message)). 수신 측 파서는 이 니블부터 분기해야 한다.

![명령 니블 16개 지도: 0x0과 0x1은 하위 명령형, 0x2~0x8과 0xA는 공통형, 0x9와 0xD는 전용형, 0xE와 0xF는 상태형, 0xB와 0xC는 예약이다. 처음 익힐 2, 3, 4~8은 굵은 테두리로 표시했다](/images/study-isobus/46-command-nibble-map-light.png)
![명령 니블 16개 지도: 0x0과 0x1은 하위 명령형, 0x2~0x8과 0xA는 공통형, 0x9와 0xD는 전용형, 0xE와 0xF는 상태형, 0xB와 0xC는 예약이다. 처음 익힐 2, 3, 4~8은 굵은 테두리로 표시했다](/images/study-isobus/46-command-nibble-map-dark.png)

표 읽는 법은 다음과 같다.
- "길이"는 메시지의 바이트 수다. 8을 넘으면 여러 프레임으로 나눠 보낸다([15장](/study/isobus/15-tp-bam-cmdt)의 TP).
- "기본 우선순위"는 3절에서 보는 CAN 우선순위다.
- "나머지 바이트"는 명령 니블을 뺀 나머지를 어떻게 읽는지다. "공통 배치"는 45장에서 조립한 Element 12비트 + DDI 16비트 + 값 32비트 배치다.
- DL은 Data Logger(TC처럼 값을 기록하지만 제어는 하지 않는 장치, [44장](/study/isobus/44-tc-multi-dl-functionality)), CF는 Control Function(버스에서 주소 하나를 쓰는 제어 기능)이다.
- (v4)는 ISO 11783-10(TC를 정하는 표준 문서) 버전 4에서 생긴 명령이라는 표시다.

| Command | 이름 | 대표 흐름 | 길이 | 기본 우선순위 | 나머지 바이트 |
|---|---|---|---|---|---|
| `0x0` | Technical capabilities | TC ↔ 클라이언트 | 8 | 5 | 상위 니블 = 하위 명령(버전·기술 정보) |
| `0x1` | Device descriptor | 클라이언트 ↔ TC/DL | 8 이상 | 5 | 상위 니블 = 하위 명령(DDOP 관리) |
| `0x2` | Request value | TC → 클라이언트 | 8 | 5 | 공통 배치 |
| `0x3` | Value command | 양방향 | 8 | 3 | 공통 배치 |
| `0x4` | Measurement: time interval | TC/DL → 클라이언트 | 8 | 5 | 공통 배치, 값 = 주기(ms) |
| `0x5` | Measurement: distance interval | TC/DL → 클라이언트 | 8 | 5 | 공통 배치, 값 = 거리(mm) |
| `0x6` | Measurement: minimum threshold | TC/DL → 클라이언트 | 8 | 5 | 공통 배치, 값 = 하한 |
| `0x7` | Measurement: maximum threshold | TC/DL → 클라이언트 | 8 | 5 | 공통 배치, 값 = 상한 |
| `0x8` | Measurement: change threshold | TC/DL → 클라이언트 | 8 | 5 | 공통 배치, 값 = 변화량 |
| `0x9` | Peer control assignment (v4) | TC → CF, 응답 CF → TC | 14 / 8 | 5 | 전용 배치(47장) |
| `0xA` | Set Value and Acknowledge (v4) | TC → 클라이언트 | 8 | 3 | 공통 배치 |
| `0xB`, `0xC` | 예약 | - | - | - | - |
| `0xD` | PDACK | 양방향 | 8 | 4 | 전용 배치(5절) |
| `0xE` | Task Controller Status | TC/DL → 전역 | 8 | 3 | 상태 배치(43장) |
| `0xF` | Client Task | 클라이언트 → TC/DL | 8 | 3 | 상태 배치(43장) |

"예약"은 표준이 나중을 위해 비워 둔 값이다. 지금은 쓰지 않는다.

나머지 바이트를 읽는 법으로 묶으면 네 무리다.

- <strong>하위 명령형(`0x0`·`0x1`)</strong>: Byte 1 상위 니블이 element number가 아니라 하위 명령이다. `0x0`의 Version 계열은 [43장 TC 연결 관리](/study/isobus/43-tc-connection)에서, `0x1`의 DDOP 관리 명령은 [50장 DDOP 전송과 설계 점검](/study/isobus/50-ddop-commands-design)에서 다룬다.
- <strong>공통형(`0x2`~`0x8`, `0xA`)</strong>: 45장에서 조립한 Command 4비트 + Element 12비트 + DDI 16비트 + 값 32비트다.
- <strong>전용형(`0x9`, `0xD`)</strong>: 앞 4바이트는 공통형과 같고, 5바이트째부터 뜻이 달라진다.
- <strong>상태형(`0xE`, `0xF`)</strong>: element number와 DDI 자리를 not available(`FFF`, `FFFF`)로 채우고 Byte 5부터 상태 비트를 싣는다. not available은 "이 자리는 해당 없음"을 뜻하는 특수값으로, 모든 비트를 1로 채워 표시한다. 이 not available 표기는 버전 2에서 도입됐고, 받는 쪽은 이 필드를 무시해야 한다. 송신 주기와 연결 유지 규칙은 [43장 TC 연결 관리](/study/isobus/43-tc-connection)를 본다.

<small>근거: ISO 11783-10 B.1.1, Table B.1, B.3~B.8</small>

## 3. 기본 우선순위와 CAN ID (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절은 같은 PGN인데도 명령에 따라 CAN ID가 달라지는 이유를 본다. CAN 로그를 필터로 거를 때 꼭 필요한 내용이다.

### 기본 우선순위는 버전 4에서 세 단계가 됐다

Process Data 메시지의 PGN(Parameter Group Number, 메시지 종류 번호)은 51968(`0xCB00`), PDU format(PF, PGN 안에서 메시지 종류를 가르는 바이트)은 203이다. PF가 240보다 작은 PDU1 형식이라 PS 자리에 목적지 주소(DA, Destination Address)가 들어간다([9장](/study/isobus/09-j1939-message)). 데이터 길이는 가변이고 최소 8바이트다.

기본 우선순위는 command마다 다르다. 3·A·E·F는 3, D는 4, 나머지(0·1·2·4~9)는 5다. 버전 3까지는 모두 3이었다. 표준은 이렇게 나눈 이유를 "ISO 11783-3의 우선순위 권고에 맞춰, 제어·연결 유지 메시지를 요청·확인 메시지보다 높게 두기 위해서"라고 밝힌다. ISO 11783-3은 데이터 링크 계층(CAN 프레임으로 메시지를 주고받는 규칙)을 정하는 표준 문서다. 우선순위는 숫자가 작을수록 높다. 값 설정(3·A)과 상태(E·F)가 가장 높고, 확인(D)이 그다음, 요청과 측정 설정이 가장 낮다.

우선순위는 29비트 CAN ID의 맨 앞 3비트다. 그래서 PGN이 같아도 command에 따라 ID가 달라진다. TC의 SA(Source Address, 보낸 쪽 주소)를 `0xF7`(=247), 클라이언트 SA를 `0x80`(=128)으로 두면(예시 값) 다음과 같다.

| 메시지 | 우선순위 | DA | SA | 29비트 CAN ID |
|---|---|---|---|---|
| TC → 클라이언트 Value command(3) | 3 | `0x80` | `0xF7` | `0x0CCB80F7` |
| TC → 클라이언트 Request value(2) | 5 | `0x80` | `0xF7` | `0x14CB80F7` |
| 클라이언트 → TC PDACK(D) | 4 | `0xF7` | `0x80` | `0x10CBF780` |

첫 줄을 풀면 이렇다. 29비트 ID를 16진수 8자리로 적으면 맨 앞 `0C`에 우선순위 3비트(`011`)와 그 뒤 두 비트(EDP·DP, 모두 0)가 들어 있다. 이어서 PF `CB`, DA `80`, SA `F7`이 차례로 온다. 우선순위가 5인 둘째 줄은 맨 앞이 `14`, 4인 셋째 줄은 `10`으로 바뀐다.

::: warning 로그 필터는 우선순위 비트를 빼고 건다
CAN 로그에서 Process Data를 CAN ID 하나(`0x0CCB80F7` 같은)로 거르면 우선순위가 다른 Request value나 PDACK가 빠진다. 우선순위 3비트를 마스크하고 PGN·DA·SA만 비교해 거른다. 표준이 정한 것은 "기본(default)" 우선순위이고, 버전 3 장비는 모든 command를 3으로 보낸다는 점도 함께 고려한다.
:::

### 메시지 전체에 걸리는 규칙

그 밖에 메시지 전체에 걸리는 규칙은 다음과 같다.

- 전역 목적지(`0xFF`=255, 버스의 모든 장치)로도 보낼 수 있다. 다만 컨트롤러는 자기에게 주소 지정된 것으로 판단한 메시지만 처리한다.
- Process Data 메시지는 "Task totals active" 비트(태스크가 진행 중이라는 TC Status의 표시, 43장) 값과 무관하게 버스에 나타날 수 있고, TC·DL과 클라이언트 사이 통신 밖에서도 나타날 수 있다. 47장의 peer control에서 setpoint를 내는 쪽(source)이 받는 쪽(user)에게 직접 보내는 Value command가 그 예다.
- 독점(proprietary, 제조사가 자체로 정한) DDI를 담아도 메시지 형식은 이 장에서 보는 형식을 그대로 따른다. DDI 범위는 [47장](/study/isobus/47-tc-totals-logging-peer)에서 본다.
- 버전 4부터 TC 하나는 버스에서 CF 하나로 나타나야 하고, TC와의 통신은 Working Set Master만 한다. multi-member Working Set(여러 ECU가 모여 작업기 하나를 이루는 묶음, [26장](/study/isobus/26-isobus-network-mgmt))은 VT 연결용으로는 그대로 선언할 수 있지만, TC와는 Master만 말한다.

<small>근거: ISO 11783-10 B.1.1, B.2</small>

## 4. Value command(3)와 Set Value and Acknowledge(`0xA`)

이 절은 값을 설정하는 두 명령을 비교한다. 둘 다 같은 바이트 배치를 쓰지만, 성공했을 때 답이 오느냐가 다르다.

### Value command(3)는 응답이면서 설정이다

표준의 명령 정의는 Command 3을 "요청에 대한 값 응답"과 "값 설정"에 함께 쓴다고 정한다. 같은 `33 00 02 00 …`이라도 누가 누구에게 보냈느냐로 뜻이 갈린다.

| 방향 | 의미 | 더 보기 |
|---|---|---|
| 클라이언트 → TC | Request value 응답, measurement 트리거에 따른 보고, default logging 보고 | 45장 9절 |
| TC → 클라이언트 | settable DPD의 값 설정(setpoint, task total 복원) | 47장 1절 |
| source CF → user CF | peer control로 할당된 setpoint 직접 전달 | 47장 5절 |

"settable DPD"는 DDOP에서 TC가 값을 설정할 수 있다고 표시한 항목이다([48장](/study/isobus/48-ddop-basics)).

TC 입장에서 클라이언트가 보낸 Command 3은 자기가 요청한 측정의 결과다. 45장 9절의 규칙대로 클라이언트는 요청받은 값만 보내야 하고, 요청보다 많은 값이 오면 TC는 초과분을 무시한다.

### Set Value and Acknowledge(A): 성공을 확인받는 설정 명령

Command A는 값을 설정하면서 수신 확인을 요구한다(버전 4 도입). 응답은 PDACK(D)다. Command 3과의 차이는 "성공했을 때도 답이 오느냐"다. 표준은 오류 코드 0인 PDACK를 command 0·1·2·3·9·D·E·F에 대한 응답으로 보내지 말라고 정한다. 그래서 Command 3으로 setpoint를 보내면 성공은 침묵이고 실패만 PDACK로 돌아온다. Command A로 보내면 성공도 오류 코드 0인 PDACK로 돌아온다.

```
TC -> 클라이언트   3A 00 01 00 80 84 1E 00   Set Value and Acknowledge, Section 3, DDI 1, 200 L/ha
클라이언트 -> TC   3D 00 01 00 00 FA FF FF   PDACK: 오류 0, 응답 대상 command A
```

PDACK Byte 6의 `FA`는 하위 니블 `A`(응답 대상 command)와 예약된 상위 니블 `F`다. 이 필드는 5절에서 다시 본다.

A를 쓸 때 조심할 점은 세 가지다.

- 버전 4 명령이다. 클라이언트는 연결 초기화 때 Request Version(상대가 구현한 표준 버전을 묻는 메시지, 43장)으로 TC 버전을 확인하고 쓸 기능을 TC에 맞춘다. TC도 상대가 버전 3이면 Command 3을 쓰는 것이 안전하다(추론: 버전 3 클라이언트는 A를 모른다).
- 확인 응답만큼 메시지가 늘어난다. variable당 초당 10개 상한(45장 9절)을 생각하면 A는 빈번한 제어보다 한 번만 확실히 넣어야 하는 값에 어울린다(추론).
- 섹션 on/off는 다른 확인 방식을 쓴다. ISO 11783-10의 섹션 제어 구현 지침은 Setpoint Condensed Work State(DDI 290, 섹션 16개의 on/off 목표를 한 값에 담는 DDI)에 on change measurement를 걸어 두고, 명령마다 클라이언트가 갱신 값을 돌려보내게 하라고 권한다. 같은 지침의 섹션 제어 순서는 이 응답 메시지와, 상태 변화를 시작하자마자 보내는 actual 상태 갱신을 필수로 둔다.

<small>근거: ISO 11783-10 Table B.1, B.7, 6.6.2 f)·g), 6.8, 6.8.2, F.3.5.1, F.3.5.5</small>

::: tip 정리
- Command 니블이 메시지 구조를 정한다. `0x0`·`0x1`은 하위 명령형, `0x2`~`0x8`·`0xA`는 공통형, `0x9`·`0xD`는 전용형, `0xE`·`0xF`는 상태형이다.
- 기본 우선순위는 버전 4부터 3(3·A·E·F), 4(D), 5(나머지)로 나뉜다.
- Command 3은 응답과 설정을 겸한다. 설정의 성공 확인까지 필요하면 버전 4의 A를 쓴다.
:::

## 5. PDACK: 명령에 대한 확인 응답

명령을 보낸 쪽은 상대가 받아들였는지 알아야 다음 일을 할 수 있다. PDACK는 그 답장이다. 택배의 배송 완료 문자와 반송 안내를 합친 것과 비슷하다. 어느 택배(명령)에 대한 알림인지, 잘 받았는지, 못 받았다면 왜인지를 함께 적는다.

PDACK(Process Data Acknowledge)는 클라이언트(Working Set Master)나 TC/DL이 명령 또는 process data를 수락·거부할 때 보내는 응답이다. 45장 4절에서는 오류 코드의 이름만 나열했다. 여기서는 바이트 단위로 연다.

![PDACK 8바이트 배치: Byte 1 하위 니블 1101(D)과 element 하위 니블, Byte 2 element 상위 8비트, Byte 3~4 DDI, Byte 5 오류 코드 8비트, Byte 6 하위 니블의 응답 대상 command(v4), Byte 7~8 예약 FF](/images/study-isobus/19-pdack-layout-light.png)
![PDACK 8바이트 배치: Byte 1 하위 니블 1101(D)과 element 하위 니블, Byte 2 element 상위 8비트, Byte 3~4 DDI, Byte 5 오류 코드 8비트, Byte 6 하위 니블의 응답 대상 command(v4), Byte 7~8 예약 FF](/images/study-isobus/19-pdack-layout-dark.png)

표 읽는 법: 바이트 번호는 1부터, 한 바이트의 비트는 가장 낮은 자리가 bit 1이다. "해당 없음일 때" 칸은 그 필드가 이번 응답과 관계없을 때 채우는 not available 값이다. 예약 자리는 표준이 나중을 위해 비워 둔 곳이라 모든 비트를 1로 채워 보낸다.

| 위치 | 내용 | 해당 없음일 때 |
|---|---|---|
| Byte 1 bit 4~1 | `1101` (PDACK) | - |
| Byte 1 bit 8~5, Byte 2 | 대상 element number(12비트) | `FFF` |
| Byte 3~4 | 대상 DDI(LSB, MSB) | `FFFF` |
| Byte 5 | Process Data 오류 코드(0 = 오류 없음) | - |
| Byte 6 bit 4~1 | 이 PDACK가 응답하는 command(버전 4) | `F` |
| Byte 6 bit 8~5 | 예약 | `F` |
| Byte 7~8 | 예약 | `FF FF` |

예시 하나를 단계별로 풀어 보자. 4절에서 본 `3D 00 01 00 00 FA FF FF`다.

1. Byte 1 `3D` = `0011 1101`이다. 아래 4비트 `1101`은 D, 즉 PDACK다. 위 4비트 `0011`은 Element 번호의 아래 4비트 3이다.
2. Byte 2 `00`은 Element 번호의 위 8비트 0이다. 합치면 Element 3이다.
3. Byte 3~4 `01 00`은 DDI 1이다(낮은 자리 바이트가 먼저).
4. Byte 5 `00`은 오류 없음이다.
5. Byte 6 `FA`의 아래 4비트 `A`는 이 PDACK가 Set Value and Acknowledge에 대한 답이라는 뜻이다. 위 4비트 `F`는 예약이다.
6. Byte 7~8 `FF FF`는 예약이다.

결론은 "Element 3의 DDI 1에 보낸 `0xA` 명령을 문제없이 받아들였다"이다.

오류가 특정 element나 DDI와 관계없으면 그 자리를 not available로 채운다. 버전 4 이전 장비는 Byte 6 하위 니블도 `F`로 보낸다. 그래서 Byte 6이 `FF`인 PDACK는 "상대가 버전 3 이하이거나, 응답 대상 명령을 특정할 수 없는 오류"로 읽는다.

### 수락 응답은 command마다 다르다

오류 코드 0인 PDACK는 command 0·1·2·3·9·D·E·F에 대한 응답으로 보내지 않는다. 남는 것은 measurement(4~8)와 A다. measurement는 버전 4부터 수락이든 거부든 PDACK로 답해야 한다.

| 받은 command | 수락하면 | 거부하면 |
|---|---|---|
| 2 Request value | Value command(3)로 값 회신 | PDACK(오류 비트) |
| 3 Value command | 회신 없음 | PDACK(오류 비트) |
| 4~8 measurement | PDACK(오류 0) + 측정 시작 시점 값(v4) | PDACK(오류 비트) |
| 9 peer control assignment | 같은 메시지를 Ack 모드로 회신(47장) | PDACK(오류 비트) |
| A Set Value and Acknowledge | PDACK(오류 0) | PDACK(오류 비트) |
| 0, 1 하위 명령 | 각 하위 명령의 응답 메시지 | 응답 메시지의 오류 필드 |

::: warning PDACK가 오지 않아도 정상일 수 있다
Command 3으로 setpoint를 보내고 PDACK를 기다리는 TC 서버는 영원히 기다린다. 수락은 침묵이 규칙이다. 반대로 measurement 명령에 PDACK가 오지 않으면 버전 4 기준으로 클라이언트 쪽 위반이다. 응답 대기 시간과 재시도는 ISO 11783-3의 PGN 응답 규칙을 따른다.
:::

<small>근거: ISO 11783-10 B.7, 6.8 c)·d)</small>

## 6. PDACK 오류 비트 읽기 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절은 Byte 5의 오류 비트 8개를 하나씩 보고, 실제 PDACK 세 개를 풀어 본다.

### 오류 비트 8개

Byte 5는 비트마다 거절 이유 하나가 배정된 비트 필드다. 받은 값에서 1인 비트를 모두 찾아 읽는다. "마스크"는 그 비트만 1인 값이다. `Byte 5 & 마스크`가 0이 아니면 그 이유에 해당한다.

| 비트 | 마스크 | 의미 | 점검할 곳 |
|---|---|---|---|
| 1 | `0x01` | Process Data command 미지원 | 상대가 모르는 command(예: 버전 3 장비에 A·9) |
| 2 | `0x02` | element number가 잘못됨 | DDOP에 없는 element number |
| 3 | `0x04` | 그 element가 DDI를 지원하지 않음 | element는 있지만 그 DET가 해당 DDI의 DPD·DPT를 참조하지 않음 |
| 4 | `0x08` | trigger method 미지원 | DPD trigger 비트에 없는 measurement 명령 |
| 5 | `0x10` | process data가 settable이 아님 | DPD properties의 settable 비트가 0 |
| 6 | `0x20` | interval·threshold가 무효이거나 미지원 | 장비가 지원하지 않는 주기·간격, 범위 밖 임계값 |
| 7 | `0x40` | 값이 DDI 정의에 맞지 않음(버전 4) | DDI 범위를 벗어난 값, 정의되지 않은 코드 |
| 8 | `0x80` | 값이 이 장치의 운영 범위 밖(버전 4) | DDI 범위 안이지만 이 기계가 낼 수 없는 값 |

표의 DET(DeviceElement)는 DDOP의 Element 오브젝트, DPD(DeviceProcessData)는 "이 Element가 이 DDI를 다룬다"고 밝히는 오브젝트, DPT(DeviceProperty)는 바뀌지 않는 고정값을 밝히는 오브젝트다([48장](/study/isobus/48-ddop-basics)).

"점검할 곳"은 각 비트의 의미에서 바로 따라 나오는 대응이다. 비트 2와 3을 구별해 두면 진단이 빨라진다. 2는 번호 자체가 DDOP에 없고, 3은 번호는 있는데 그 element에 그 DDI가 없다. 비트 7과 8도 짝이다. 7은 사전(DDE, DDI 사전의 항목 하나, 47장) 기준 위반이고, 8은 사전 범위 안이지만 기계 한계를 넘은 값이다.

### 디코딩 예

| 수신 바이트 | element | DDI | 오류 | 응답 대상 | 해석 |
|---|---|---|---|---|---|
| `3D 00 02 00 10 FA FF FF` | 3 | 2 | bit 5 | A | Actual Volume Per Area에 값을 설정하려 했다. 읽기 전용이다 |
| `BD 00 01 00 04 F3 FF FF` | 11 | 1 | bit 3 | 3 | 섹션(element 11)에 DDI 1이 없다. [49장의 7섹션 붐 예시](/study/isobus/49-ddop-bytes) 설계에서 섹션에 살포량을 명령한 경우다 |
| `FD FF FF FF 01 FF FF FF` | 해당 없음 | 해당 없음 | bit 1 | `F` | 상대가 command 자체를 모른다. Byte 6이 `FF`라 버전 3 이하 장비일 가능성이 크다 |

둘째 줄을 풀면 이렇다. Byte 1 `BD`의 위 4비트 `B`(=11)와 Byte 2 `00`을 합쳐 element 11이다. Byte 5 `04`는 bit 3(마스크 `0x04`)이고, Byte 6 `F3`의 아래 4비트 3은 Value command에 대한 답이라는 뜻이다.

아래 코드는 3절의 CAN ID 계산과 이 절의 PDACK 조립·해석을 함수로 옮기고 `assert`(값이 다르면 멈추는 검사)로 검산한다. 주석의 "20장 §6"은 이 블로그를 장 단위로 나누기 전의 번호이고, 지금의 49장 7섹션 붐 예시를 가리킨다.

::: details 파이썬으로 검산해 보기: CAN ID와 PDACK
```python
def can_id(priority, pgn, da, sa):
    pf = (pgn >> 8) & 0xFF
    assert pf < 240                      # PDU1: PS 자리가 목적지 주소
    return (priority << 26) | ((pgn & 0x30000) << 8) | (pf << 16) | (da << 8) | sa


def build_frame(command, element, ddi, value):
    byte1 = ((element & 0xF) << 4) | (command & 0xF)
    return (bytes([byte1, element >> 4]) + ddi.to_bytes(2, "little")
            + value.to_bytes(4, "little", signed=True))


def build_pdack(element, ddi, error_bits, acked_command):
    byte1 = ((element & 0xF) << 4) | 0xD
    byte6 = 0xF0 | (acked_command & 0xF)   # bit 8~5 예약 = F
    return (bytes([byte1, element >> 4]) + ddi.to_bytes(2, "little")
            + bytes([error_bits, byte6, 0xFF, 0xFF]))


ERRORS = ["명령 미지원", "잘못된 element", "element의 DDI 미지원", "trigger 미지원",
          "settable 아님", "interval·threshold 무효", "DDI 정의 위반", "운영 범위 밖"]


def parse_pdack(frame):
    assert frame[0] & 0x0F == 0xD
    element = (frame[0] >> 4) | (frame[1] << 4)
    ddi = frame[2] | (frame[3] << 8)
    reasons = [ERRORS[b] for b in range(8) if frame[4] >> b & 1]
    return element, ddi, reasons or ["정상"], frame[5] & 0x0F


# 기본 우선순위: 3(3·A·E·F), 4(D), 5(나머지). SA는 예시 값(TC 0xF7, 클라이언트 0x80)
assert can_id(3, 0xCB00, da=0x80, sa=0xF7) == 0x0CCB80F7   # TC -> 클라이언트, Value command
assert can_id(5, 0xCB00, da=0x80, sa=0xF7) == 0x14CB80F7   # TC -> 클라이언트, Request value
assert can_id(4, 0xCB00, da=0xF7, sa=0x80) == 0x10CBF780   # 클라이언트 -> TC, PDACK

# Set Value and Acknowledge(A) -> 수락 PDACK
cmd = build_frame(0xA, element=3, ddi=1, value=2_000_000)
ack = build_pdack(element=3, ddi=1, error_bits=0x00, acked_command=0xA)
assert cmd.hex(" ").upper() == "3A 00 01 00 80 84 1E 00"
assert ack.hex(" ").upper() == "3D 00 01 00 00 FA FF FF"

# 읽기 전용 DDI 2에 A를 보냈을 때 -> bit 5
nak = build_pdack(element=3, ddi=2, error_bits=1 << 4, acked_command=0xA)
assert nak.hex(" ").upper() == "3D 00 02 00 10 FA FF FF"

# 20장 §6 설계에서 섹션(element 11)에 DDI 1 Value command -> bit 3
nak2 = build_pdack(element=11, ddi=1, error_bits=1 << 2, acked_command=0x3)
assert nak2.hex(" ").upper() == "BD 00 01 00 04 F3 FF FF"

print(parse_pdack(bytes.fromhex("3D 00 02 00 10 FA FF FF")))
print(parse_pdack(bytes.fromhex("BD 00 01 00 04 F3 FF FF")))
print(parse_pdack(bytes.fromhex("FD FF FF FF 01 FF FF FF")))
```
```
(3, 2, ['settable 아님'], 10)
(11, 1, ['element의 DDI 미지원'], 3)
(4095, 65535, ['명령 미지원'], 15)
```
:::

출력 한 줄은 (element, DDI, 거절 이유, 응답 대상 명령) 순서다. 마지막 숫자 10은 `0xA`, 3은 Value command, 15는 `F`(해당 없음)다. 셋째 줄의 4095와 65535는 not available `FFF`와 `FFFF`를 10진수로 적은 것이다.

<small>근거: ISO 11783-10 B.7</small>

## 7. Measurement 명령: 언제 값을 보낼지 정하기

이 절은 measurement 명령 하나하나가 Value 자리에 무엇을 싣는지, 실제 프레임이 어떻게 생겼는지 본다.

measurement 명령(4~8)은 값을 나르는 메시지가 아니라 "언제 값을 보내라"는 설정이다. Value 자리의 숫자가 트리거 파라미터다.

| Command | Value 자리의 뜻 | 단위 | 클라이언트가 값을 보내는 때 |
|---|---|---|---|
| 4 time interval | 송신 주기 | ms | 그 주기마다 |
| 5 distance interval | 송신 거리 간격 | mm | 그 거리를 지날 때마다 |
| 6 minimum threshold | 하한 임계값 | DDI 단위 | 값이 임계값보다 클 때 |
| 7 maximum threshold | 상한 임계값 | DDI 단위 | 값이 임계값보다 작을 때 |
| 8 change threshold | 변화량 임계값 | DDI 단위 | 마지막 송신 뒤 변화량이 임계값 이상일 때 |

"DDI 단위"는 그 DDI의 원시값 단위라는 뜻이다. 예를 들어 DDI 2에 변화량 임계값 10 L/ha를 걸려면 45장의 분해능대로 원시값 100,000을 싣는다.

Command 8의 비교는 버전 3에서 "초과"가 "이상"으로 바뀌었다. 태스크 파일의 기록 조건 정의(DataLogTrigger)와 맞추기 위해서다. DataLogTrigger는 FMIS(농장 관리 소프트웨어)가 태스크 파일에 "이 DDI를 이런 조건으로 기록하라"고 적는 요소다([56장](/study/isobus/56-practice-isoxml)). 버전 2 이하 장비는 변화량이 임계값과 정확히 같을 때 보내지 않는다는 뜻이다.

### 바이트로 보기

Section 3(element 3)의 DDI 2(Actual Volume Per Area)에 각 명령을 건 예다. 임계값은 45장 5절과 같은 분해능(1 L/ha = 원시값 10,000)으로 바꿨다.

| 설정 | 프레임 |
|---|---|
| time interval 1000 ms | `34 00 02 00 E8 03 00 00` |
| distance interval 10 m | `35 00 02 00 10 27 00 00` |
| minimum threshold 150 L/ha | `36 00 02 00 60 E3 16 00` |
| maximum threshold 250 L/ha | `37 00 02 00 A0 25 26 00` |
| change threshold 10 L/ha | `38 00 02 00 A0 86 01 00` |

첫 줄을 단계별로 풀면 다음과 같다.

1. Byte 1 `34`: 아래 4비트 4는 time interval, 위 4비트 3은 element 3이다.
2. Byte 3~4 `02 00`: DDI 2다.
3. Byte 5~8 `E8 03 00 00`: 높은 자리부터 다시 놓으면 `0x000003E8` = 1000이다. 주기 1000 ms다.

distance interval 10 m는 mm 단위로 10,000(`0x2710`)이라 `10 27 00 00`이 된다.

명령마다 PDACK를 받아야 다음 명령을 보낼 수 있다. 위 다섯 개를 거는 데 왕복 다섯 번이 든다. time interval을 수락한 클라이언트는 PDACK `3D 00 02 00 00 F4 FF FF`(Byte 6 하위 니블 4)와 측정 시작 시점의 값(`33 00 02 00 60 36 1E 00` 같은 Value command)을 보낸다. 둘의 순서는 표준이 정하지 않는다.

<small>근거: ISO 11783-10 Table B.1, 6.8 c)</small>

## 8. 트리거 여러 개 함께 걸기

이 절은 같은 값에 measurement를 여러 개 걸었을 때 클라이언트가 언제 값을 보내는지 본다. "변하면 바로, 안 변해도 가끔은" 같은 조합이 실제로 가장 많이 쓰인다.

같은 DDI에 measurement를 여러 개 걸 수 있다. 조합의 의미는 태스크 파일의 기록 조건(DataLogTrigger)이 정한다. TC는 DataLogTrigger를 measurement 명령으로 바꿔 보내므로 이 규칙이 곧 명령 조합의 의미다.

- 시간 간격·거리 간격·on change는 어떤 조합이든 쓸 수 있다. 셋 중 먼저 일어난 사건이 송신을 일으키고, 그 순간 켜져 있는 트리거가 모두 다시 시작한다.
- threshold limits는 위 조합에 "문"을 하나 더한다. 값이 임계 범위 안에 들어오면 기록이 시작되고, 범위 안에 있는 동안만 기록한다.
- 최소 임계값이 최대 임계값보다 작으면 둘 사이(띠 안)가 기록 구간이다. 최소가 최대보다 크면 최소보다 크거나 최대보다 작은 값(띠 밖)이 기록 구간이다.
- total은 다른 방법과 독립이고 어떤 조합과도 함께 쓸 수 있다. total 값은 태스크의 Time 요소(태스크 파일에서 작업 구간 하나를 적는 요소, [42장](/study/isobus/42-tc-task))마다 한 번 저장한다.

예를 들어 시간 간격 5 s와 on change 10 L/ha를 함께 걸면, 값이 10 L/ha 이상 바뀔 때 즉시 한 번 보내고 5 s 타이머도 그 시점부터 다시 센다. 값이 거의 안 변하면 5 s마다 한 번씩만 나간다. 표준이 권하는 "on change를 주 트리거로, 긴 시간 간격을 대체 수단으로" 쓰는 조합이 이 형태다(5 s는 예시 값).

![시간 간격 5 s와 on change 10 L/ha를 함께 건 경우의 송신 시점: 0 s에 측정 시작 값, 5 s에 시간 간격으로 보낸다. 8 s에 값이 200에서 212 L/ha로 12 바뀌어 on change로 바로 보내고 타이머가 다시 시작해 13 s에 보낸다. 16 s에 206 L/ha로 6만 바뀐 것은 보내지 않고 18 s에 시간 간격으로 보낸다](/images/study-isobus/46-trigger-combination-light.png)
![시간 간격 5 s와 on change 10 L/ha를 함께 건 경우의 송신 시점: 0 s에 측정 시작 값, 5 s에 시간 간격으로 보낸다. 8 s에 값이 200에서 212 L/ha로 12 바뀌어 on change로 바로 보내고 타이머가 다시 시작해 13 s에 보낸다. 16 s에 206 L/ha로 6만 바뀐 것은 보내지 않고 18 s에 시간 간격으로 보낸다](/images/study-isobus/46-trigger-combination-dark.png)

그림을 시간 순서로 읽으면 다음과 같다(값과 시각은 설명용 예시다).

1. 0 s: 측정을 시작하며 첫 값 200 L/ha를 보낸다.
2. 5 s: 값이 그대로라 시간 간격 트리거로 보낸다.
3. 8 s: 값이 212 L/ha로 12 바뀌었다. 10 이상이라 on change로 바로 보내고, 5 s 타이머도 여기서 다시 센다.
4. 13 s: 다시 센 타이머가 5 s를 채워 보낸다. 원래 주기대로라면 10 s였을 송신이 13 s로 밀렸다.
5. 16 s: 값이 206 L/ha로 6만 바뀌어 보내지 않는다. 변화량은 마지막으로 보낸 212를 기준으로 잰다.
6. 18 s: 시간 간격 트리거로 보낸다.

::: warning 경계값 해석이 두 정의에서 다르다
태스크 파일의 기록 조건 정의(DataLogTrigger)는 최소·최대 임계값 자체를 기록 범위에 포함한다고 적는다. 메시지 명령 정의는 command 6을 "임계값보다 클 때", 7을 "작을 때"로 적는다. command 8은 버전 3에서 기록 조건 정의에 맞춰 "이상"으로 고쳤지만 6·7은 그대로다. 값이 임계값과 정확히 같을 때의 동작은 장비마다 다를 수 있으니, TC 서버는 경계값에서 한 번 더 오거나 덜 오는 경우를 오류로 보지 않는 편이 안전하다(추론).
:::

<small>근거: ISO 11783-10 6.8, 6.8.2, D.17, Table B.1</small>

## 9. trigger 비트, 값의 범위, 멈추는 값 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절은 DDOP가 밝히는 트리거 지원 여부, 명령 값의 허용 범위, 걸어 둔 측정을 멈추는 값을 본다.

### DDOP trigger 비트와 명령의 대응

DDOP의 DPD는 받을 수 있는 트리거를 trigger 비트로 밝힌다([48장](/study/isobus/48-ddop-basics)). TC는 비트가 선 트리거만 명령해야 하고, 서 있지 않은 트리거를 명령하면 PDACK bit 4가 돌아온다.

| DPD trigger 비트 | 값 | 대응 명령 |
|---|---|---|
| bit 1 time interval | `0x01` | 4 |
| bit 2 distance interval | `0x02` | 5 |
| bit 3 threshold limits | `0x04` | 6, 7 |
| bit 4 on change | `0x08` | 8 |
| bit 5 total | `0x10` | 없음: 이 DPD가 총계라는 표시(47장) |

표준에는 이 대응을 표 하나로 묶어 둔 곳이 없다. DDOP의 trigger 비트 값과 태스크 파일 기록 조건(DataLogTrigger)의 기록 방법 비트 값이 1·2·4·8·16으로 같고, 기록 조건의 속성(시간 간격·거리 간격·최소·최대·변화 임계값)이 명령 4~8의 값과 하나씩 맞물리는 데서 읽어 낸 대응이다. 표준의 기능별 DDOP 지침이 DPD에 "Change Threshold 트리거를 지원하라"고 쓸 때도 on change 비트를 가리키는 것으로 읽힌다. total 비트에는 대응 명령이 없다. 총계 값은 Request value나 시간·거리 간격 measurement로 받는다.

### 값의 범위와 멈추는 값

2절의 명령 표에는 측정을 끄는 명령이 따로 없다. 끄는 방법은 "멈추는 값"이다. 태스크 파일의 기록 조건 정의(DataLogTrigger)는 각 속성의 범위와 "측정을 멈추는 값"을 정한다. 메시지 명령 정의에는 멈추는 값이 따로 없다. TC가 DataLogTrigger를 그대로 명령으로 옮기므로 같은 값을 명령에 쓰는 것으로 읽는다(추론).

| 명령 | 범위 | 멈추는 값 | 비고 |
|---|---|---|---|
| 4 time interval | 0~60,000 ms | 0 | 최소 간격 100 ms |
| 5 distance interval | 0~1,000,000 mm | 0 | |
| 6 minimum threshold | −2³¹+1 ~ 2³¹−1 | 2³¹−1 (`0x7FFFFFFF`) | |
| 7 maximum threshold | −2³¹+1 ~ 2³¹−1 | −2³¹+1 (`0x80000001`) | |
| 8 change threshold | −2³¹+1 ~ 2³¹−1 | 0 | 1이면 모든 변화를 기록 |

2³¹−1은 2,147,483,647로, 32비트 부호 있는 정수의 최댓값이다. 6·7의 멈추는 값은 "어떤 값도 조건을 만족할 수 없게" 만드는 값이다. 최소 임계값을 정수 최댓값으로 두면 어떤 값도 그보다 클 수 없다. 시간 간격의 100 ms 하한은 variable당 초당 10개 상한(45장 9절)과 맞아떨어진다(추론).

멈추는 값을 실은 프레임은 다음과 같다. 7절과 같은 element 3, DDI 2다.

| 설정 | 프레임 |
|---|---|
| time interval 정지 | `34 00 02 00 00 00 00 00` |
| minimum threshold 정지 | `36 00 02 00 FF FF FF 7F` |
| maximum threshold 정지 | `37 00 02 00 01 00 00 80` |

`FF FF FF 7F`는 낮은 자리부터 실은 `0x7FFFFFFF`이고, `01 00 00 80`은 `0x80000001`(= −2,147,483,647)이다.

아래 코드는 7절의 다섯 프레임, 이 절의 멈추는 값, 8절의 임계 범위 규칙을 검산한다. 주석의 D.17은 표준 원문에서 기록 조건(DataLogTrigger)을 정의한 조항 번호다.

::: details 파이썬으로 검산해 보기: measurement 명령
```python
def build_frame(command, element, ddi, value):
    byte1 = ((element & 0xF) << 4) | (command & 0xF)
    return (bytes([byte1, element >> 4]) + ddi.to_bytes(2, "little")
            + value.to_bytes(4, "little", signed=True))


def lha_to_raw(lha):                  # DDI 1·2: 1 L/ha = 100 mm3/m2, 분해능 0.01
    return round(lha * 100 / 0.01)


hexs = lambda f: f.hex(" ").upper()
E, DDI = 3, 2                         # Section 3의 Actual Volume Per Area

cmds = {
    "time interval 1000 ms": build_frame(4, E, DDI, 1000),
    "distance interval 10 m": build_frame(5, E, DDI, 10_000),
    "minimum threshold 150 L/ha": build_frame(6, E, DDI, lha_to_raw(150)),
    "maximum threshold 250 L/ha": build_frame(7, E, DDI, lha_to_raw(250)),
    "change threshold 10 L/ha": build_frame(8, E, DDI, lha_to_raw(10)),
}
expected = {
    "time interval 1000 ms": "34 00 02 00 E8 03 00 00",
    "distance interval 10 m": "35 00 02 00 10 27 00 00",
    "minimum threshold 150 L/ha": "36 00 02 00 60 E3 16 00",
    "maximum threshold 250 L/ha": "37 00 02 00 A0 25 26 00",
    "change threshold 10 L/ha": "38 00 02 00 A0 86 01 00",
}
for name, frame in cmds.items():
    assert hexs(frame) == expected[name], (name, hexs(frame))
    print(f"{name:28s} {hexs(frame)}")

# 수락 PDACK: Byte 6 하위 니블에 응답 대상 command
ack_time = bytes([0x3D, 0x00, 0x02, 0x00, 0x00, 0xF0 | 4, 0xFF, 0xFF])
assert hexs(ack_time) == "3D 00 02 00 00 F4 FF FF"
assert hexs(build_frame(4, E, DDI, 5_000)) == "34 00 02 00 88 13 00 00"

# 측정을 멈추는 값(D.17 DataLogTrigger 정의)
stops = {
    "time interval": build_frame(4, E, DDI, 0),
    "distance interval": build_frame(5, E, DDI, 0),
    "minimum threshold": build_frame(6, E, DDI, 2**31 - 1),
    "maximum threshold": build_frame(7, E, DDI, -2**31 + 1),
    "change threshold": build_frame(8, E, DDI, 0),
}
assert hexs(stops["minimum threshold"]) == "36 00 02 00 FF FF FF 7F"
assert hexs(stops["maximum threshold"]) == "37 00 02 00 01 00 00 80"
for name, frame in stops.items():
    print(f"stop {name:23s} {hexs(frame)}")

# min/max 조합으로 값이 기록되는 구간(D.17)
def logging_enabled(value, tmin, tmax):
    if tmin < tmax:
        return tmin <= value <= tmax
    return value >= tmin or value <= tmax

assert logging_enabled(200, 150, 250) and not logging_enabled(100, 150, 250)
assert logging_enabled(300, 250, 150) and not logging_enabled(200, 250, 150)
```
:::

실행하면 7절의 다섯 프레임과 멈추는 프레임 다섯 개가 출력되고, 모든 `assert`를 통과한다. 마지막 함수 `logging_enabled`는 8절의 "띠 안·띠 밖" 규칙을 그대로 옮긴 것이다.

<small>근거: ISO 11783-10 A.4, D.17, D.23, Table B.1, F.3.4.1, 6.8.3.1 d)</small>

::: details 원문을 가진 독자를 위한 메모
- trigger 비트 대응은 DPD trigger 비트(D.23)와 DataLogTrigger의 DataLogMethod 비트(D.17)가 같은 값이고, D.17의 속성이 Table B.1의 명령 4~8 값과 맞물리는 데서 읽었다. F.3.4.1의 "Change Threshold 트리거 지원" 요구도 on change 비트로 읽었다.
- 8절의 경계값 차이는 D.17(임계값을 기록 범위에 포함)과 Table B.1(command 6은 "greater than", 7은 "less than")의 표현 차이다.
- 멈추는 값은 D.17에만 있고 Annex B의 명령 표에는 없다.
:::

::: tip 정리
- measurement 명령의 Value는 트리거 파라미터다. 단위는 4가 ms, 5가 mm, 6~8이 DDI 단위다.
- 시간·거리·on change는 먼저 일어난 쪽이 보내고 모두 다시 시작한다. threshold는 기록 구간을 정하는 문이다.
- 멈추는 값은 4·5·8이 0, 6이 2³¹−1, 7이 −2³¹+1이다.
:::

::: tip 핵심 정리
- 명령 니블 하나가 메시지 종류와 나머지 바이트 읽는 법을 정한다. 가장 흔한 것은 2(값 요청), 3(값 전달·설정), 4~8(측정 설정)이다.
- Command 3으로 설정하면 성공은 조용하고 실패만 PDACK로 온다. 성공까지 확인하려면 버전 4의 `0xA`를 쓴다.
- PDACK는 Byte 5 오류 비트로 거절 이유를, Byte 6 아래 4비트로 어떤 명령에 대한 답인지를 알린다.
- measurement 명령의 값은 "언제 보낼지"다. 명령마다 PDACK를 받은 뒤에 다음 명령을 보낸다.
- 시간·거리·변화 트리거는 먼저 일어난 쪽이 보내고 함께 다시 시작한다.
:::

::: details 확인 문제
1. `32 00 02 00 00 00 00 00`은 무슨 명령이고, 클라이언트는 어떤 명령으로 답하는가?
2. TC가 Command 3으로 setpoint를 보냈는데 PDACK가 오지 않았다. 문제가 있는 것인가?
3. measurement 명령 `35 00 02 00 10 27 00 00`의 뜻을 풀어라.
4. (디코딩) TC 서버 로그에 `FD FF FF FF 01 FF FF FF`가 찍혔다. 직전에 TC가 같은 클라이언트로 `3A 00 01 00 80 84 1E 00`을 보냈다. 이 PDACK를 필드별로 풀고 원인과 대응을 설명하라.
5. (설계) Section 3(element 3)의 Actual Volume Per Area(DDI 2)를 "10 L/ha 이상 바뀔 때마다, 그리고 적어도 5초에 한 번" 받고 싶다. TC가 보낼 프레임과 순서, 클라이언트가 돌려줄 메시지를 적어라.

<strong>답 가이드</strong>

1. 아래 4비트 2는 Request value다. 위 4비트 3과 Byte 2 `00`을 합치면 element 3, Byte 3~4는 DDI 2다. "element 3의 실제 살포량을 알려 달라"는 요청이다. 클라이언트는 같은 element·DDI에 값을 실은 Value command(3)로 답한다. 예: `33 00 02 00 60 36 1E 00`.
2. 아니다. Command 3에 대한 수락은 침묵이 규칙이라 오류 코드 0인 PDACK는 보내지 않는다. PDACK가 왔다면 거절이다. 성공 확인이 필요하면 `0xA`를 쓰거나 Request value로 값을 다시 읽는다.
3. 아래 4비트 5는 distance interval, 위 4비트 3은 element 3, Byte 3~4는 DDI 2다. 값 `10 27 00 00`은 `0x2710` = 10,000 mm = 10 m다. "element 3의 실제 살포량을 10 m 갈 때마다 보내라"는 설정이다.
4. element `FFF`와 DDI `FFFF`는 해당 없음, Byte 5 `0x01`은 bit 1(command 미지원), Byte 6 `FF`는 응답 대상 command를 `F`로 적은 것이다. 버전 4 이전 장비의 표기다. 버전 3 클라이언트가 버전 4 명령 A를 모른다는 뜻이다. Request Version으로 상대 버전을 확인하고([43장](/study/isobus/43-tc-connection)) Command 3으로 다시 보낸다. 성공 확인이 필요하면 Request value로 값을 다시 읽는다.
5. `38 00 02 00 A0 86 01 00`(change threshold 100,000 = 10 L/ha) → 클라이언트 PDACK `3D 00 02 00 00 F8 FF FF`와 시작 시점 값(Value command) → `34 00 02 00 88 13 00 00`(time interval 5,000 ms) → PDACK `3D 00 02 00 00 F4 FF FF`와 시작 시점 값. 각 PDACK를 받은 뒤에야 다음 명령을 보낸다. 두 트리거는 먼저 일어난 쪽이 송신하고 둘 다 다시 시작한다. DPD trigger 비트에 on change(`0x08`)와 time interval(`0x01`)이 서 있어야 하고, 없으면 PDACK bit 4가 온다.
:::

## 다음 챕터

- 다음: [47장 Totals, 로깅, Peer Control](/study/isobus/47-tc-totals-logging-peer)
