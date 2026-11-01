---
title: "TC 연결 관리와 메시지 바이트"
description: "TC와 클라이언트가 연결을 맺고 유지하고 끊는 메시지 순서와 타이밍, 키를 끈 뒤의 셧다운 절차, Version·TC Status·Client Task·Deactivate 메시지의 바이트를 읽는 법을 익힌다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, TaskController, TC, Connection, TCStatus, ClientTask, Version]
prev: /study/isobus/42-tc-task
next: /study/isobus/44-tc-multi-dl-functionality
---

# TC 연결 관리와 메시지 바이트

::: info 학습 목표
- TC와 클라이언트가 연결을 맺는 메시지 순서를 시퀀스 그림으로 따라갈 수 있다.
- 200 ms·2 s·6 s 타이밍 규칙이 각각 무엇을 지키는지 설명할 수 있다.
- 키를 끈 뒤의 셧다운이 고장으로 인한 끊김과 어떻게 다른지, TC와 클라이언트가 각각 무엇을 해야 하는지 말할 수 있다.
- Version, TC Status, Client Task 메시지 8바이트를 읽고 상대의 버전·기능·Busy 상태를 알아낼 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [41장 TC 기초](/study/isobus/41-tc-basics)(특히 8절 클라이언트 초기화), [42장 태스크와 시간 기록](/study/isobus/42-tc-task), [9장 J1939 메시지 구조](/study/isobus/09-j1939-message)
- 이 장에서 처음 나오는 말
  - 시퀀스 그림: 두 장치 사이에 오가는 메시지를 시간 순서대로 위에서 아래로 그린 그림
  - 셧다운(shutdown): 키를 끈 뒤 전원이 완전히 꺼지기 전까지 하던 일을 정리하는 구간
  - Busy: TC가 무거운 일(DDOP 처리, 메모리 저장 등)을 하느라 바쁘다는 표시
  - Process Data 메시지(PGN 51968): TC와 클라이언트가 주고받는 메시지가 모두 쓰는 메시지 번호
  - Command: 그 메시지 안에서 "무슨 종류의 말인지"를 가리키는 4비트 값
:::

[41장 8절](/study/isobus/41-tc-basics)에서 클라이언트가 TC와 연결하는 9단계를 표로 봤다. 이 장은 그 표를 실제 메시지 흐름으로 펼친다. 전화에 비유하면 41장은 "전화를 걸고, 인사하고, 용건을 말한다"는 순서였고, 이 장은 말이 몇 초 간격으로 오가는지, 통화가 끊기면 어떻게 하는지, 수화기로 오가는 신호(바이트)가 어떻게 생겼는지 본다. 1~6절은 흐름과 규칙이고, 7절은 바이트를 읽기 위한 준비, 8~10절은 구현자를 위한 바이트 세부다.

## 1. 연결 시퀀스 한눈에 보기

연결 절차를 표로만 보면 어떤 메시지가 누구에게서 누구에게 가는지 감이 잘 오지 않는다. 이 절은 두 장치 사이에 오가는 메시지를 시간 순서대로 그린 시퀀스 그림으로 전체 흐름을 먼저 본다.

![TC 클라이언트와 TC/DL 사이의 연결 시퀀스: 양쪽이 주소 클레임 후 6 s를 기다리고, TC Status(2 s 주기)를 받은 클라이언트가 Working Set Master와 Client Task를 보낸 뒤 버전을 양방향으로 교환하고, DDOP를 활성화하는 동안 TC는 Busy 상태를 보내며, 어느 한쪽의 주기 메시지가 6 s 끊기면 각자 정리 동작을 한다](/images/study-isobus/18-connection-sequence-light.png)
![TC 클라이언트와 TC/DL 사이의 연결 시퀀스: 양쪽이 주소 클레임 후 6 s를 기다리고, TC Status(2 s 주기)를 받은 클라이언트가 Working Set Master와 Client Task를 보낸 뒤 버전을 양방향으로 교환하고, DDOP를 활성화하는 동안 TC는 Busy 상태를 보내며, 어느 한쪽의 주기 메시지가 6 s 끊기면 각자 정리 동작을 한다](/images/study-isobus/18-connection-sequence-dark.png)

그림은 왼쪽 세로줄이 클라이언트, 오른쪽 세로줄이 TC(또는 DL)이고, 위에서 아래로 시간이 흐른다. 화살표가 메시지 하나다. 위에서부터 읽으면 다음과 같다.

1. 양쪽이 각자 주소 클레임을 끝내고 6 s를 기다린다.
2. TC가 TC Status를 2 s 주기로, 버스 전체(전역)에 보내기 시작한다.
3. TC Status를 받은 클라이언트가 Working Set Master 메시지로 자신을 소개하고, Client Task를 2 s 주기로 보내기 시작한다.
4. 클라이언트가 Request Version으로 TC 버전을 묻고 Version으로 답을 받는다. 이어서 TC도 같은 방식으로 클라이언트 버전을 묻는다. 버전 4에서는 이 교환이 의무다.
5. (선택) 클라이언트가 언어 설정을 묻는다. 점선 화살표가 선택 단계다.
6. DDOP를 확인하고, 없으면 보내고, 활성화(Activate)한다. 그동안 TC는 Busy 표시를 단 TC Status를 보낸다.
7. TC가 활성화 결과(Activate Response)를 보내면, measurement 명령과 process data 값이 오가는 본 작업이 시작된다.
8. 맨 아래 두 상자는 어느 한쪽의 주기 메시지가 6 s 끊겼을 때 각자 하는 정리 동작이다.

그림에서 DDOP는 device descriptor object pool, 즉 작업기가 자기 구조를 알리는 설명서다. 줄여서 "풀(pool)"이라고도 부른다.

이 그림은 41장의 9단계 표에 없는 세부를 세 가지 더 보여 준다.

1. <strong>풀을 검증하는 동안에도 TC Status는 2 s 주기를 지킨다.</strong> 이때 TC Status는 Busy로 나간다. Byte 5 bit 4 = 1, Byte 6 = 처리 중인 클라이언트의 SA, Byte 7 = 실행 중인 device descriptor 명령의 Byte 1이다(아래 9절). Activate 응답을 기다리는 클라이언트는 이 바이트로 TC가 자기 풀을 처리 중인지 볼 수 있다(추론).
2. <strong>활성화가 끝나야 클라이언트가 태스크에 들어간다.</strong> Activate Response 뒤에 TC는 device description을 파일 세트에 추가하고, 태스크가 실행 중이면 그 태스크에 DeviceAllocation과 AllocationStamp를 추가한 다음 measurement를 시작한다.
3. <strong>끊김 처리가 대칭이다.</strong> Client Task가 6 s 끊기면 TC는 (태스크가 실행 중이면) 그 DeviceAllocation의 AllocationStamp를 닫는다. TC Status가 6 s 끊기면 클라이언트는 (measurement가 활성이면) process data 송신을 멈춘다.

위 세 항목에 나온 말을 풀면 다음과 같다.

- SA(Source Address)는 메시지를 보낸 장치의 주소다. device descriptor 명령은 DDOP를 올리고 활성화하는 명령 묶음이다.
- DeviceAllocation과 AllocationStamp는 "이 장치가 이 태스크에 언제부터 언제까지 붙어 있었나"를 적는 태스크 파일 요소다([42장 6절](/study/isobus/42-tc-task)).
- measurement 명령은 TC가 클라이언트에게 "이 값을 이런 조건으로 계속 보고하라"고 걸어 두는 명령이다([46장](/study/isobus/46-tc-commands-pdack)).

DDOP 단계 안에서도 메시지가 여러 번 오간다. Request Localization Label 단계는 Structure Label 응답이 "이 ECU의 device descriptor가 TC에 없다"고 알렸으면 건너뛴다. Structure Label과 Localization Label은 DDOP의 구조 버전과 언어 버전을 나타내는 이름표다. TC에 같은 이름표의 DDOP가 있으면 다시 보낼 필요가 없다. DDOP 쪽 메시지 순서는 [48장 DDOP 기초](/study/isobus/48-ddop-basics)와 [50장 DDOP 전송과 설계 점검](/study/isobus/50-ddop-commands-design)에서 다룬다.

<small>근거: ISO 11783-10 6.6.3(Figure 2)</small>

## 2. 초기화 단계마다 덧붙는 조건 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

[41장 8절](/study/isobus/41-tc-basics)의 9단계 표는 요약이다. 표준은 단계마다 조건과 버전별 차이를 덧붙인다. 같은 단계 번호로 덧붙는 내용만 모으면 다음과 같다.

| 단계 | 표준이 덧붙이는 조건 | 버전 차이 |
|---|---|---|
| 1 | Part 5 절차로 주소 클레임을 끝내고 6 s 기다린다. Part 5도 클레임에 성공한 CF가 250 ms 동안은 (address claimed 요청 응답 말고는) 송신을 시작하지 못하게 한다 | |
| 2 | <strong>선택한</strong> TC가 TC Status를 보내기 시작할 때까지 기다린다. 어느 TC를 선택하는지는 [44장](/study/isobus/44-tc-multi-dl-functionality) | |
| 3 | Working Set Master·Working Set Member 메시지(Part 7, PGN 65037 `0xFE0D` / PGN 65036 `0xFE0C`)로 자신이 Working Set Master임을 밝힌다. 같은 메시지를 VT 초기화 같은 다른 용도로 보내도 된다 | 버전 3 이전에는 TC가 WS 전체와 통신할 수 있었다. 버전 4부터는 WSM 메시지로 식별은 하되 TC와의 통신은 WSM CF 하나로 한정한다 |
| 4 | Client Task 송신 시작. 주소 클레임이 끝나고 최소 6 s가 지난 뒤여야 한다 | |
| 5 | Request Version으로 TC 버전을 묻는다. TC가 필요한 버전·기능을 지원하지 않으면 자기 버전·기능을 TC 수준으로 낮춘다 | 버전 4부터 의무. 이전에는 버전 3 이상 기능을 쓰려 할 때의 권고였다 |
| 6 | 버전 4 TC가 보내는 Request Version을 기다렸다가 응답한다. TC가 클라이언트 정보를 올바르게 처리하기 위해서다 | 버전 4 |
| 7 | 언어·형식 메시지 요청(선택) | |
| 8 | 자기 DDOP가 TC에 이미 있는지 묻는다 | |
| 9 | 있으면 activate, 없으면 device descriptor 메시지와 TP 또는 ETP(Part 3)로 전송한 뒤 activate. TP와 ETP는 DDOP 크기로 고른다 | |

표의 낯선 말을 풀면 다음과 같다.

- Part 5(ISO 11783-5)는 주소 클레임을 정하는 표준 문서다. 250 ms 규칙은 주소를 막 정한 장치가 곧바로 다른 메시지를 보내지 않고, 같은 주소를 원하는 장치가 경합 클레임을 낼 시간을 두는 것이다. 이 250 ms 동안 경합이 없어야 클레임이 성공한다([13장](/study/isobus/13-j1939-address-claim)).
- WS(Working Set)는 한 기계를 이루는 ECU 묶음이고, WSM(Working Set Master)은 그 대표다. PGN 65037(=`0xFE0D`)이 Working Set Master, PGN 65036(=`0xFE0C`)이 Working Set Member 메시지다([26장](/study/isobus/26-isobus-network-mgmt)).
- Part 3(ISO 11783-3)은 데이터 링크 계층을 정하는 표준 문서다. TP는 최대 1,785바이트까지, ETP는 그보다 큰 데이터를 나눠 보낸다([15장](/study/isobus/15-tp-bam-cmdt), [17장](/study/isobus/17-etp)).

TC 쪽 다섯 단계는 41장 표와 그대로 대응한다. 두 가지만 덧붙인다.

- 1단계의 "전역(255)으로 address claimed 요청 송신"은 표준이 이유를 적지 않는다. 다만 이 요청으로 TC가 이미 버스에 있는 CF들의 NAME과 SA 대응을 처음부터 모을 수 있다. 클라이언트는 NAME으로만 유일하게 구분되기 때문이다(추론).
- 5단계는 "클라이언트가 TC 버전을 요청한 <strong>뒤에</strong>" TC가 클라이언트 버전을 요청한다는 순서 규정이다. 버전 4에서 추가됐고, 그 전의 TC는 클라이언트 버전을 물을 의무가 없었다.

::: details 원문을 가진 독자를 위한 메모
- 41장 8절의 클라이언트 9단계와 ISO 11783-10:2015 6.6.2의 대응: 1 = a)+b), 2 = c), 3 = d), 4 = e), 5 = f), 6 = g), 7 = h), 8 = i), 9 = j). 원문은 a)~j) 10개 항목으로 적고, 41장 표의 1단계가 a)와 b)를 합친 것이다.
- TC 5단계는 6.6.1 a)~e)와 1:1로 대응한다.
- 단계 1의 250 ms 규칙: ISO 11783-5:2019 4.5.2 d). 단계 3의 메시지: ISO 11783-7 B.23. 단계 4의 6 s 조건: 6.6.3. 단계 5의 Request Version: B.5.2. 단계 9의 전송 메시지: Annex B.
- 1단계 해설의 "클라이언트는 NAME으로만 유일하게 구분된다"는 5.3에 근거한다.
:::

<small>근거: ISO 11783-10 5.3, 6.6.1, 6.6.2, 6.6.3</small>

## 3. 타이밍 규칙 한눈에

연결을 유지하는 규칙은 대부분 시간 값이다. 값이 여러 개라 헷갈리기 쉬우니 이 절에서 한 표로 모은다.

| 값 | 무엇 | 규칙 |
|---|---|---|
| 6 s | 주소 클레임 후 대기 | TC는 TC Status 전, 클라이언트는 Client Task 전에 최소 6 s |
| 2 s | TC Status 주기 | 주기 송신 + 태스크 상태나 메시지의 <strong>어느 바이트든</strong> 바뀌면 즉시 송신 |
| 200 ms | TC Status 최소 간격 | 즉시 송신도 이 간격을 지킨다(최대 5 Hz) |
| 2 s | Client Task 주기 | 주기 송신 + 태스크 상태가 바뀔 때마다. 최소 간격 200 ms |
| 6 s | 양방향 타임아웃 | 상대의 주기 메시지를 최소 6 s 못 받으면 비정상 종료 가능성으로 본다 |
| 2 s | Deactivate 응답 | 정상 deactivate 응답의 최대 응답 시간 |
| 2 s | 셧다운 중 서비스 유지 | 활성 DDOP를 가진 클라이언트의 마지막 Maintain Power 이후 최소 2 s |
| 3 s | TC 번호 표시 | Request Identify Task Controller를 받은 TC가 TC 번호를 보여 주는 시간 |

- 5 Hz는 1초에 5번이라는 뜻이다. 200 ms마다 한 번이 최대이므로 1초에 5번을 넘지 못한다.
- Deactivate와 Maintain Power는 5절에서, TC 번호는 8절과 [44장](/study/isobus/44-tc-multi-dl-functionality)에서 다룬다.

::: warning "바뀌면 즉시"와 200 ms를 같이 지켜야 한다
상태 비트가 짧은 시간에 여러 번 바뀌는 구간(예: DDOP 활성화로 Busy가 켜졌다 꺼질 때)에서 "바뀔 때마다 즉시 송신"만 구현하면 200 ms보다 짧은 간격으로 연달아 나간다. 바뀐 값을 모아 두었다가 직전 송신 + 200 ms 시점에 한 번에 보내야 한다. 표준은 200 ms·2 s·6 s가 구현에 그대로 써야 하는 값이고, 정확도는 AEF 시험 요구사항의 대상이라고 못 박는다.
:::

규칙 두 개를 함께 지키는 모습을 예로 보자. 아래 코드는 TC Status를 언제 보내야 하는지 계산한다.

::: details 파이썬으로 검산해 보기: TC Status 송신 시각
즉시 송신 뒤 2 s 주기를 그 시점부터 다시 세는 방식으로 짠 예다. 주기를 다시 셀지 고정 격자로 둘지는 표준이 정하지 않는다. 어느 쪽이든 "주기 간격 2 s 이하, 송신 간격 200 ms 이상"을 지키면 된다(추론).

```python
MIN_GAP_MS, PERIOD_MS = 200, 2000


def tc_status_send_times(change_times_ms, until_ms):
    pending, sent, last = sorted(change_times_ms), [], None
    while True:
        if last is not None:
            pending = [t for t in pending if t > last]
        periodic = 0 if last is None else last + PERIOD_MS
        on_change = max(pending[0], last + MIN_GAP_MS) if pending and last is not None else None
        nxt = periodic if on_change is None else min(periodic, on_change)
        if nxt > until_ms:
            return sent
        sent.append(nxt)
        last = nxt


times = tc_status_send_times([2500, 2550, 6100], until_ms=9000)
print(times)
assert times == [0, 2000, 2500, 2700, 4700, 6100, 8100]
gaps = [b - a for a, b in zip(times, times[1:])]
assert min(gaps) >= MIN_GAP_MS and max(gaps) <= PERIOD_MS
```

```
[0, 2000, 2500, 2700, 4700, 6100, 8100]
```

2500 ms와 2550 ms의 변화 두 번은 2500 ms 송신과 2700 ms 송신으로 나뉜다. 2550 ms 변화는 200 ms 간격을 채운 2700 ms에 나간다.

결과를 시간 순서로 풀면 다음과 같다.

1. 0 ms에 첫 송신, 2000 ms에 주기 송신을 한다.
2. 2500 ms에 상태가 바뀌었다. 직전 송신(2000 ms)에서 500 ms가 지났으니 바로 보낸다.
3. 2550 ms에 또 바뀌었다. 직전 송신(2500 ms)에서 50 ms밖에 안 지났으므로 2700 ms까지 기다렸다가 보낸다.
4. 다음 주기 송신은 2700 ms에서 2 s 뒤인 4700 ms다.
5. 6100 ms의 변화는 직전 송신에서 1400 ms가 지났으니 바로 보내고, 2 s 뒤 8100 ms에 주기 송신을 한다.
:::

<small>근거: ISO 11783-10 6.6.1, 6.6.2, 6.6.3, 6.6.4.1, B.5.4, B.6.11, B.8.1, B.8.2</small>

## 4. 클라이언트 연결 상태 머신

구현할 때는 절차를 "지금 어느 상태에 있고, 무슨 일이 생기면 어느 상태로 가는가"로 정리하면 편하다. 이런 정리를 상태 머신이라고 한다. 신호등이 초록, 노랑, 빨강 상태를 정해진 조건에 따라 오가는 것과 같다.

[41장 8절](/study/isobus/41-tc-basics)의 초기화 절차와 이 장의 셧다운 규칙을 구현 단위로 묶으면 다음 상태가 나온다. 상태 이름은 표준 용어가 아니라 정리용이다.

![TC 클라이언트 연결 상태: 주소 확보, 대기(6 s), TC 탐색, 연결 수립, DDOP를 차례로 지나 운용 상태가 된다. 운용 중 TC Status가 6 s 끊기면 TC 탐색으로 돌아가고, Key Switch Off면 셧다운으로 가며, 셧다운에서 Key Switch가 Not Off로 돌아오면 다시 초기화한다](/images/study-isobus/43-client-connection-states-light.png)
![TC 클라이언트 연결 상태: 주소 확보, 대기(6 s), TC 탐색, 연결 수립, DDOP를 차례로 지나 운용 상태가 된다. 운용 중 TC Status가 6 s 끊기면 TC 탐색으로 돌아가고, Key Switch Off면 셧다운으로 가며, 셧다운에서 Key Switch가 Not Off로 돌아오면 다시 초기화한다](/images/study-isobus/43-client-connection-states-dark.png)

| 상태 | 하는 일 | 다음 상태로 가는 조건 |
|---|---|---|
| 주소 확보 | Part 5 주소 클레임 | 클레임 완료 → 대기 |
| 대기 | 6 s 타이머 | 6 s 경과 → TC 탐색 |
| TC 탐색 | 선택한 TC의 TC Status를 기다린다 | TC Status 수신 → 연결 수립 |
| 연결 수립 | WSM(+Member) 송신, Client Task 2 s 주기 시작, Request Version, TC의 Request Version에 응답, (선택) 언어 요청 | 버전 확인 → DDOP |
| DDOP | Structure Label 질의 → (필요하면) 전송 → Activate | 오류 없는 Activate Response → 운용 |
| 운용 | measurement 명령에 응답, process data 송신, Client Task 유지 | TC Status 6 s 미수신 → Client Task 중단 후 재초기화 / Key Switch Off → 셧다운 |
| 셧다운 | Maintain Power, Connection Deactivate | Key Switch Not Off → 재초기화 |

- Activate Response가 오류면 TC/DL은 그 풀을 휘발성 메모리에서 지운다. 다시 활성화하려면 풀을 다시 전송해야 한다. 휘발성 메모리는 전원이 꺼지면 내용이 사라지는 메모리다.
- TC Status가 끊긴 뒤의 재초기화를 표준은 "초기화 절차를 다시 시작한다"고만 적는다. 이미 주소를 가진 클라이언트라면 TC 탐색부터 다시 밟는 구현이 자연스럽다(추론). 그림의 주황 점선 화살표가 이 추론을 따른 것이다.
- 단, 셧다운 중의 TC Status 끊김은 예외다. 아래 5절 표의 클라이언트 규칙 d)에 따라 비정상 종료로 보지 않는다.

<small>근거: ISO 11783-10 6.6.2~6.6.4, B.6.11</small>

## 5. 셧다운: 키를 끈 뒤

키를 끄는 순간 모든 장치가 한꺼번에 꺼지지는 않는다. 어떤 작업기는 바로 꺼지고, 어떤 작업기는 몇 초 더 일하며 기록을 마무리한다. 이 구간을 고장으로 인한 통신 끊김으로 오해하지 않게 하는 규칙이 셧다운 절차다.

[41장 8절](/study/isobus/41-tc-basics)의 "연결 종료"를 자세히 풀면 다음과 같다. 시스템 셧다운은 <strong>Key Switch 상태가 Off인데 ECU Power는 아직 켜져 있는 구간</strong>이다. Actuator Power는 함께 켜져 있을 수도, 아닐 수도 있다. 아래 절차는 버전 4에서 도입돼 버전 4 구현에는 의무다.

- ECU Power는 제어 컴퓨터(ECU)에 들어가는 전원이고, Actuator Power는 밸브·모터 같은 구동 장치에 들어가는 전원이다. 트랙터는 이 둘을 따로 관리한다([22장 트랙터 ECU](/study/isobus/22-tractor-ecu)).
- 그래서 키를 끈 뒤에도 ECU는 잠시 살아 있고, 그동안 마지막 기록을 저장하거나 작별 인사를 보낼 수 있다.

Key Switch 상태는 Wheel-based speed and distance(PGN 65096) Byte 8 bits 4~3에 실린다. `00` Off, `01` not Off, `10` error, `11` not available이다. 같은 메시지 Byte 7은 Maximum time of tractor power(남은 전원 시간, 1 min/bit, 0~250)다. TECU의 전원 관리는 [22장 트랙터 ECU](/study/isobus/22-tractor-ecu)에서 다룬다.

- 2비트 값 네 가지 중 `10`(error)과 `11`(not available)은 특수값이다. 센서가 고장 났거나 그 값을 보낼 수 없는 장치도 메시지 형식은 맞춰 보내야 하므로, "값이 없다"를 나타내는 자리를 따로 둔 것이다.
- 비트 위치를 실제 프레임에서 읽는 예는 [42장 7절](/study/isobus/42-tc-task)에 있다. 클라이언트는 이 2비트가 `01`에서 `00`으로 바뀌는 순간을 셧다운 시작으로 본다.

| TC | 클라이언트 |
|---|---|
| a) "예상치 못한 클라이언트 종료 감지 로직"을 끈다. 한 클라이언트는 바로 꺼지고 다른 클라이언트는 ECU Power를 붙잡고 있을 때, 평소의 6 s 타임아웃 때문에 오퍼레이터에게 쓸데없는 알림이 가지 않게 하려는 것이다 | a) Maintain Power 메시지(Part 7, PGN 65095 `0xFE47`)를 보내 자기 상태를 알리고, 필요하면 이 메시지로 ECU Power·Actuator Power 유지를 요청한다 |
| b) 활성 DDOP를 가진 클라이언트들의 마지막 Maintain Power 요청 이후 최소 2 s 동안 서비스를 유지한다. 셧다운 중 수집하던 데이터를 올바르게 마무리하기 위해서다 | b) Maximum time of tractor power를 감시해 자기 전원 관리에 쓴다 |
| c) Key Switch를 계속 감시하다가 Off → Not Off로 돌아오면 TC Status를 끊고 표준 초기화를 다시 한다 | c) TC에 Connection Deactivate를 보내 "예상치 못한 종료"로 보이지 않게 한다 |
| | d) TC Status나 다른 TC 메시지가 끊겨도 TC의 비정상 종료로 보지 않는다. 따라서 <strong>다른 TC로 연결을 시도하지 않는다</strong> |
| | e) Key Switch를 계속 감시하다가 Off → Not Off로 돌아오면 재초기화한다 |

표를 시간 순서로 엮어 보면 이렇다.

1. 오퍼레이터가 키를 끈다. Key Switch 상태가 `01`에서 `00`이 된다.
2. 클라이언트는 Maintain Power로 "아직 정리 중이니 전원을 잠시 유지해 달라"고 요청하고, 남은 전원 시간을 지켜본다.
3. 클라이언트는 Connection Deactivate로 TC에 작별 인사를 한다.
4. TC는 이 구간의 끊김을 고장으로 보지 않고, 마지막 Maintain Power 이후 최소 2 s 동안 서비스를 유지하며 데이터를 마무리한다.
5. 키가 다시 켜지면(Not Off) 양쪽 모두 처음부터 초기화한다.

구버전과 섞인 네트워크에서는 다음을 감안해야 한다.

- 버전 2는 셧다운 동작을 정의하지 않았고 버전 3은 의무로 정하지 않았다. 그래서 버전 3 이하 TC는 TC Status를 포함한 모든 통신을 그냥 끊을 수 있다.
- 버전 3 이하 클라이언트도 경고 없이 통신을 끊을 수 있다. 일부 구버전 클라이언트는 Key Switch를 아예 보지 않고 전원이 끊길 때까지 평소처럼 동작한다.

::: warning 셧다운을 끊김으로 오해하는 구현
키를 끄자마자 클라이언트가 "TC 연결 끊김" 경고를 띄우거나 TC 번호 2로 갈아타면 위 표의 클라이언트 d) 위반이다. 반대로 TC가 키 오프 직후 클라이언트들의 Client Task 끊김마다 경고를 띄우면 TC a) 위반이다. 양쪽 모두 Key Switch Off 이후의 끊김을 정상으로 다뤄야 한다.
:::

<small>근거: ISO 11783-10 6.6.4, 6.6.4.1, 6.6.4.2, B.6.10. ISO 11783-7 A.11, A.12, B.4</small>

## 6. 전원 사이클 뒤 태스크 재개

키를 껐다 켜거나 전원이 잠깐 끊겼다 돌아오는 것을 전원 사이클이라고 한다. 작업 도중 이런 일이 생기면 하던 태스크를 어떻게 이어 갈지가 이 절의 주제다.

전원이 다시 들어오면 TC는 다음 규칙을 따른다.

- TC는 전원 사이클 전의 태스크 상태를 복원해야 한다(shall). 모든 TC 기능을 재개하는 것이 권고다.
- 전원이 꺼지기 전에 데이터 로깅이나 위치 기반 제어가 켜져 있었다면, 자동으로 다시 켜거나 오퍼레이터에게 계속할지 확인을 받아야 한다.
- 자동 재개를 못 하는 구현은 "전원이 꺼지기 전에 태스크 기능이 활성이었고 재활성화가 필요하다"고 오퍼레이터에게 알려야 한다.
- 제어 명령을 실제로 실행할지 말지는 클라이언트 책임이다.

[42장 5절](/study/isobus/42-tc-task)의 태스크 상태로 보면, Running이던 태스크는 전원 사이클 뒤에도 Running으로 복원되고, TC Status의 Task totals active와 measurement를 다시 세워야 한다는 뜻이다(추론). 점심시간에 시동을 껐다 켜도 작업 일지가 이어지는 것과 같다.

<small>근거: ISO 11783-10 6.6.3, 6.6.4.3</small>

::: tip 정리
- 초기화에서 버전 4가 바꾼 것은 버전 질의·응답 의무와 WSM 한정이다.
- 활성화 중에도 TC Status는 2 s 주기와 200 ms 간격을 지키며 Busy를 보고한다. 6 s 끊김 처리는 TC와 클라이언트가 대칭이다.
- Key Switch Off 이후의 끊김은 정상 셧다운이다. 클라이언트는 Maintain Power와 Deactivate를 보내고 다른 TC로 옮기지 않는다.
:::

## 7. 연결 메시지의 공통 틀: PGN 51968

이제 메시지 바이트를 읽을 차례다. TC와 클라이언트가 주고받는 메시지는 모두 같은 틀을 쓰므로, 이 틀을 먼저 알면 뒤의 메시지들이 쉽게 읽힌다.

TC 관련 메시지는 모두 Process Data PG 하나를 쓴다. Data page 0, PDU format 203(`0xCB`), PDU specific = 목적지 주소이고, 길이는 가변이되 최소 8바이트다. Byte 1의 하위 니블(bits 4~1)이 Command다. 이 장에서 다루는 연결용 Command는 넷이다. 나머지 Command(값 요청·설정, measurement, PDACK)는 [46장 명령 니블과 PDACK](/study/isobus/46-tc-commands-pdack)의 범위다.

- 이 메시지의 PGN은 51968(=`0xCB00`)이다. Data page, PDU format, PDU specific은 29비트 CAN ID 안에서 PGN을 이루는 칸들이다([9장](/study/isobus/09-j1939-message)). PDU specific 칸에 목적지 주소가 들어가므로 특정 상대에게 보낼 수 있다.
- 니블(nibble)은 4비트, 즉 바이트의 절반이다. Byte 1의 아래쪽 절반(bits 4~1)이 Command다.

우체국 봉투 하나(PGN 51968)에 여러 종류의 서류를 넣고, 서류 첫 칸(Byte 1 아래쪽 4비트)에 서류 종류를 적는 방식이라고 생각하면 된다. 받는 쪽은 봉투 번호가 아니라 첫 칸을 보고 서류를 나눈다.

| Command | 메시지 | 기본 우선순위 | 목적지 |
|---|---|---|---|
| `0x0` | Technical data: Request Version, Version, Request Identify TC, Identify TC response | 5 | 지정(Request Identify TC는 보통 전역) |
| `0x1` | Device descriptor: Structure Label부터 Object-pool Activate/Deactivate까지 | 5 | 지정 |
| `0xE` | Task Controller Status | 3 | 전역 |
| `0xF` | Client Task | 3 | 지정 |

Command에 따라 우선순위를 3·4·5로 나눈 것은 버전 4다. 버전 3까지는 모든 Process Data 메시지가 3이었다. 제어·연결 유지 메시지를 요청·ACK 메시지보다 높게 둬 Part 3의 우선순위 권고에 맞춘 것이다. 그래서 버스 중재에서 TC Status·Client Task(3)가 Version(5)보다 앞선다.

- 우선순위는 숫자가 작을수록 높다. 두 장치가 동시에 말하면 우선순위가 높은(숫자가 작은) 메시지가 버스를 먼저 쓴다([5장 CAN 중재](/study/isobus/05-can-arbitration)).
- 표의 "전역"은 버스의 모두에게(목적지 주소 255), "지정"은 특정 상대 하나에게 보낸다는 뜻이다.

29비트 CAN ID는 `우선순위 << 26 | 0xCB << 16 | DA << 8 | SA`다. ID 구조는 [9장 J1939 메시지 구조](/study/isobus/09-j1939-message)에서 다룬다. 아래 예제는 클라이언트 SA를 `0x80`, TC SA를 `0xF7`로 둔 <strong>예시 값</strong>이다.

- `<<`는 비트를 왼쪽으로 미는 연산, `|`는 비트를 합치는 연산(OR)이다. 즉 우선순위, PDU format, 목적지(DA), 출발지(SA)를 각자 자리에 놓고 합친다.
- DA(Destination Address)는 받는 쪽 주소, SA(Source Address)는 보내는 쪽 주소다.

| 메시지 | 방향 | CAN ID |
|---|---|---|
| Request Version | 클라이언트 → TC | `0x14CBF780` |
| Version | TC → 클라이언트 | `0x14CB80F7` |
| TC Status | TC → 전역(255) | `0x0CCBFFF7` |
| Client Task | 클라이언트 → TC | `0x0CCBF780` |

첫 줄 Request Version을 직접 조립해 보자.

1. 우선순위 5를 26비트 밀면 `0x14000000`이다.
2. `0xCB`를 16비트 밀면 `0x00CB0000`이다.
3. 목적지는 TC라 `0xF7`을 8비트 밀어 `0x0000F700`이다.
4. 출발지는 클라이언트 `0x80`이다.
5. 넷을 합치면 `0x14CBF780`이다. TC Status는 우선순위 3(`0x0C000000`)에 목적지 255(`0xFF`)라서 `0x0CCBFFF7`이 된다.

이 장에서 볼 세 메시지의 8바이트 배치를 한 그림에 모았다. 칸마다 위 글자가 값이나 이름, 아래 글자가 짧은 설명이다. N/A(not available)는 "이 칸은 해당 없음"을 뜻하는 특수값 `FF`다.

![Version, TC Status, Client Task 세 메시지의 8바이트 배치 비교: Version은 Byte 1 0x10 뒤에 버전·부팅 시간·옵션 2바이트·붐·섹션·채널 수가 오고, TC Status는 0xFE와 not available FF 세 바이트 뒤에 상태 비트·클라이언트 SA·처리 중인 명령·예약이 오며, Client Task는 0xFF와 FF 세 바이트 뒤에 Task totals active를 되돌리는 상태 바이트와 0으로 채운 예약 바이트가 온다](/images/study-isobus/18-connection-messages-layout-light.png)
![Version, TC Status, Client Task 세 메시지의 8바이트 배치 비교: Version은 Byte 1 0x10 뒤에 버전·부팅 시간·옵션 2바이트·붐·섹션·채널 수가 오고, TC Status는 0xFE와 not available FF 세 바이트 뒤에 상태 비트·클라이언트 SA·처리 중인 명령·예약이 오며, Client Task는 0xFF와 FF 세 바이트 뒤에 Task totals active를 되돌리는 상태 바이트와 0으로 채운 예약 바이트가 온다](/images/study-isobus/18-connection-messages-layout-dark.png)

<small>근거: ISO 11783-10 B.1.1, B.2</small>

## 8. Version 메시지: 버전과 능력 알리기 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

연결 초기에 TC와 클라이언트는 서로 "몇 버전이고, 무엇을 할 수 있는지"를 묻고 답한다. 이 절은 그 질문과 답의 바이트를 읽는다. 이 절의 바이트 표는 모두 같은 방식으로 읽는다. Byte 번호는 1부터 세고, "bit 1"은 그 바이트의 가장 낮은 자리 비트, "bits 8~5"는 위쪽 4비트다.

### Request Version과 Version

TC·DL·클라이언트 누구나 상대가 구현한 ISO 11783-10 버전을 물을 수 있다. Request Version은 Byte 1 = `0x00`(bits 4~1 = 0000 technical data, bits 8~5 = 0000 Request Version), Byte 2~8 = `FF`인 8바이트이고, 목적지를 지정해 필요할 때만 보낸다.

```
00 FF FF FF FF FF FF FF
```

Byte 1의 아래 4비트(0000)가 Command "technical data"이고, 위 4비트(0000)가 그 안의 세부 종류 "Request Version"이다. 나머지 7바이트는 쓰지 않는 칸이라 `FF`로 채운다.

Version은 그 응답이다. Byte 1 = `0x10`(bits 8~5 = 0001 Version)이다.

| Byte | 필드 | 값과 규칙 | 정의된 버전 |
|---|---|---|---|
| 1 | Command·파라미터 | `0x10` | |
| 2 | 버전 번호 | 0 = DIS, 1 = FDIS.1, 2 = FDIS.2·초판 IS, 3 = 2판 DIS(E2.DIS), 4 = 2판 FDIS·IS(E2.FDIS/E2.IS) | |
| 3 | Boot time | 전원 사이클부터 첫 TC Status 송신까지 걸리는 최대 초. 정보가 없으면 `FF`. TC·DL만 의미 있는 값을 넣고 <strong>클라이언트는 `FF`</strong> | v3 |
| 4 | Provided options | bit 1 TC-BAS(documentation, task total을 어느 수준에서든 처리), bit 2 위치 기반 제어 없는 TC-GEO(위치 기반 로깅), bit 3 위치 기반 제어 있는 TC-GEO, bit 4 peer control assignment, bit 5 TC-SC, bits 6~8 = 0(예약) | v3 |
| 5 | Provided options byte 2 | 전부 0(예약) | v3 |
| 6 | 섹션 제어 붐 수 | TC는 지원하는 최대치, 클라이언트는 제어할 수 있는 수. 섹션 제어 붐 = Section Control State DDI(160)를 참조하는 DPD를 가진 DeviceElement | v3 |
| 7 | 섹션 수 | 모든 붐의 섹션 합. TC는 최대치, 클라이언트는 제어 가능한 수 | v3 |
| 8 | 위치 기반 제어 채널 수 | TC는 최대치, 클라이언트는 제어 가능한 수. 채널 = Prescription Control State DDI(158)를 참조하는 DPD를 가진 DeviceElement | v3 |

표의 낯선 말을 풀면 다음과 같다.

- DIS, FDIS, IS는 국제 표준이 만들어지는 단계 이름이다. DIS(Draft International Standard)는 초안, FDIS(Final DIS)는 최종 초안, IS는 발행된 표준이다. E2는 2판(Edition 2)이다. 현재 판(2015년 2판)이 버전 4다.
- Boot time은 "전원을 켜고 몇 초 안에 TC Status를 보내기 시작하는가"다. 클라이언트가 TC를 얼마나 기다릴지 정할 때 쓴다([44장](/study/isobus/44-tc-multi-dl-functionality)).
- TC-BAS, TC-GEO, TC-SC는 [41장 6절](/study/isobus/41-tc-basics)에서 본 기능성이다. peer control assignment는 작업기끼리 값을 직접 주고받게 하는 기능이다([47장](/study/isobus/47-tc-totals-logging-peer)).
- 붐(boom)은 살포기의 긴 팔이고, 섹션은 그 팔을 나눈 구획이다. DPD(DeviceProcessData)와 DeviceElement는 DDOP 안의 오브젝트로, [48장](/study/isobus/48-ddop-basics)에서 본다.

"v3" 표시 바이트는 버전 3에서 정의됐다. 버전 2 이하 구현은 그 바이트를 `FF`로 보낸다.

::: warning Version 메시지 디코딩 함정 세 가지
- <strong>버전 바이트를 먼저 본다.</strong> 버전 2 이하 상대는 Byte 3~8을 `FF`로 보낸다. 옵션 바이트 `0xFF`를 비트 그대로 읽으면 "TC-BAS·TC-GEO·peer control·TC-SC를 모두 지원하는 TC"가 돼 버린다. 버전이 2 이하면 Byte 3~8을 "정보 없음"으로 다뤄야 한다(추론).
- <strong>예약 비트는 0이다.</strong> Byte 4 bits 6~8과 Byte 5는 "0 = 예약"으로 정의된다. 예약을 1(`FF`)로 채우는 습관대로 보내면 수신 측이 정의되지 않은 옵션으로 읽을 수 있다(추론).
- <strong>클라이언트의 붐·섹션·채널 수는 조정 전 값이다.</strong> 클라이언트는 TC 능력에 맞춰 DDOP를 줄여야 하지만, Version 메시지에는 줄인 값이 아니라 자기 능력을 그대로 보고한다.
:::

TC와 클라이언트가 주고받은 Version 예제를 읽어 보자.

```
TC → 클라이언트:  10 04 0A 1F 00 02 18 04
클라이언트 → TC:  10 04 FF 11 00 01 07 00
```

| 바이트 | TC | 클라이언트 |
|---|---|---|
| 2 버전 | 4 | 4 |
| 3 Boot time | `0x0A` = 10 s | `FF`(클라이언트는 항상 `FF`) |
| 4 옵션 | `0x1F` = bit 1~5 모두 | `0x11` = bit 1(TC-BAS) + bit 5(TC-SC) |
| 5 옵션 2 | 0 | 0 |
| 6 붐 | 2 | 1 |
| 7 섹션 | 24(`0x18`) | 7 |
| 8 채널 | 4 | 0 |

옵션 바이트를 비트로 풀어 보면 다음과 같다.

1. `0x1F`는 2진수로 `0001 1111`이다. 오른쪽 끝부터 bit 1, 2, 3, 4, 5가 모두 1이므로 TC-BAS, 위치 기반 로깅, 위치 기반 제어, peer control, TC-SC를 모두 지원한다. bits 6~8은 0이라 예약 규칙도 지켰다.
2. `0x11`은 `0001 0001`이다. bit 1(TC-BAS)과 bit 5(TC-SC)만 1이다.
3. `0x18`은 16 + 8 = 24다.

이 TC는 섹션 제어 붐 2개·섹션 24개·채널 4개까지 다루므로, 붐 1개·섹션 7개짜리 클라이언트는 DDOP를 줄일 필요가 없다. TC가 클라이언트보다 작은 경우는 [44장](/study/isobus/44-tc-multi-dl-functionality)에서 본다. 참고로 위치 기반 제어를 지원하는 TC가 bit 2(위치 기반 로깅)도 함께 세워야 하는지는 표준이 말하지 않는다. 이 예제는 모든 옵션을 지원하는 TC라 두 비트를 다 세웠다.

::: details 파이썬으로 검산해 보기
```python
PROCESS_DATA_PF = 0xCB


def can_id(priority, da, sa):
    return (priority << 26) | (PROCESS_DATA_PF << 16) | (da << 8) | sa


OPTION_BITS = {
    0x01: "TC-BAS",
    0x02: "TC-GEO (위치 기반 제어 없음)",
    0x04: "TC-GEO (위치 기반 제어 포함)",
    0x08: "peer control",
    0x10: "TC-SC",
}


def decode_version(data):
    assert len(data) == 8
    command, parameter = data[0] & 0x0F, data[0] >> 4
    assert (command, parameter) == (0x0, 0x1), "Version 메시지가 아니다"
    return {
        "version": data[1],
        "boot_time_s": None if data[2] == 0xFF else data[2],
        "options": [name for bit, name in OPTION_BITS.items() if data[3] & bit],
        "reserved_bits_ok": data[3] & 0xE0 == 0 and data[4] == 0,
        "booms": data[5],
        "sections": data[6],
        "channels": data[7],
    }


tc_version = decode_version(bytes.fromhex("10 04 0A 1F 00 02 18 04"))
client_version = decode_version(bytes.fromhex("10 04 FF 11 00 01 07 00"))
print(tc_version)
print(client_version)

assert tc_version["version"] == 4 and tc_version["boot_time_s"] == 10
assert len(tc_version["options"]) == 5 and tc_version["reserved_bits_ok"]
assert (tc_version["booms"], tc_version["sections"], tc_version["channels"]) == (2, 24, 4)

assert client_version["boot_time_s"] is None
assert client_version["options"] == ["TC-BAS", "TC-SC"]
assert (client_version["booms"], client_version["sections"], client_version["channels"]) == (1, 7, 0)

CLIENT_SA, TC_SA = 0x80, 0xF7
assert can_id(5, TC_SA, CLIENT_SA) == 0x14CBF780
assert can_id(5, CLIENT_SA, TC_SA) == 0x14CB80F7
```

```
{'version': 4, 'boot_time_s': 10, 'options': ['TC-BAS', 'TC-GEO (위치 기반 제어 없음)', 'TC-GEO (위치 기반 제어 포함)', 'peer control', 'TC-SC'], 'reserved_bits_ok': True, 'booms': 2, 'sections': 24, 'channels': 4}
{'version': 4, 'boot_time_s': None, 'options': ['TC-BAS', 'TC-SC'], 'reserved_bits_ok': True, 'booms': 1, 'sections': 7, 'channels': 0}
```

`decode_version`은 Byte 1의 아래 4비트(`data[0] & 0x0F`)와 위 4비트(`data[0] >> 4`)를 나눠 Version 메시지인지 확인한 뒤, 나머지 바이트를 표대로 읽는다. 마지막 두 줄은 7절의 CAN ID 표를 계산으로 확인한다.
:::

### 파일 쪽 짝: TaskControllerCapabilities

버스로 주고받는 Version 메시지와 같은 정보를 파일에도 남긴다. 버전 4부터 MICS가 만든 파일 세트에는 그 파일을 만든 TC의 능력을 TaskControllerCapabilities(TCC) 요소로 최대 하나 넣는다. TC의 NAME, 제품명, VersionNumber(0~4), ProvidedCapabilities, 붐·섹션·채널의 최대 수(0~254, 지원하지 않으면 0)를 담는다.

ProvidedCapabilities 값 1·2·4·8·16은 Version 메시지 Byte 4의 bit 1~5와 같은 뜻이다. 그런데 <strong>32(polygon 처방 맵 지원)는 Version 메시지에 없다</strong>. 버스에서 polygon 지원은 Part 12의 Control function functionalities 메시지로 알린다. 그 메시지는 [28장 진단 (2)](/study/isobus/28-diagnostics-dm-fmi)에서 다룬다.

값 1·2·4·8·16·32는 각각 한 비트(bit 1~6)에 해당하므로 더해서 함께 표시한다. 예를 들어 TC-BAS(1)와 TC-SC(16)를 지원하면 17이다. Part 12(ISO 11783-12)는 진단 서비스를 정하는 표준 문서다.

### Request Identify Task Controller

오퍼레이터가 "지금 이 TC가 몇 번인가"를 확인할 때 쓰는 버전 4 메시지다. 클라이언트도 TC도 보낼 수 있고, 보통 전역으로 보내지만 목적지를 지정해도 된다. 받은 TC는 자기 TC 번호를 <strong>3 s 동안</strong> 표시해야 한다. 표시 방식은 TC 고유이고, DL에도 유효하다.

```
20 FF FF FF FF FF FF FF
```

목적지 지정으로 받았을 때만 TC가 Identify Task Controller response로 답한다. 이 응답도 Byte 1 bits 8~5 = 0010, Byte 2~8 = `FF`라 요청과 바이트가 똑같다. 그래서 수신 측은 내용이 아니라 "그 SA에 보낸 요청이 대기 중인가"로 응답을 가려야 한다(추론). GUI가 없는 TC는 번호를 표시하지 못할 수 있다.

- Byte 1 `0x20`은 아래 4비트가 0(technical data), 위 4비트가 2(Identify TC)다.
- TC가 여러 대인 트랙터에서 오퍼레이터가 이 요청을 전역으로 보내면, 각 TC가 3초 동안 자기 번호를 보여 줘 "어느 장치가 몇 번 TC인가"를 한눈에 확인할 수 있다. TC 번호는 [44장](/study/isobus/44-tc-multi-dl-functionality)에서 다룬다.

<small>근거: ISO 11783-10 B.5.2, B.5.3, B.5.4, B.5.5, D.47, F.2.2</small>

## 9. TC Status와 Client Task (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

2 s마다 오가는 두 주기 메시지의 바이트를 읽는다. TC Status는 TC의 상태 보고, Client Task는 클라이언트의 생존 신고다.

### Task Controller Status

TC(DL)가 자기 상태를 알리는 메시지다. 전역으로, 2 s 주기 + 어느 바이트든 바뀌면 즉시 보내고, 메시지 사이에는 최소 200 ms를 둔다.

| Byte | 내용 |
|---|---|
| 1 | `0xFE`: bits 4~1 = 1110(TC Status), bits 8~5 = 1111(element number 하위 니블, not available) |
| 2 | `FF`: element number, not available |
| 3~4 | `FF FF`: DDI, not available |
| 5 | 실제 TC/DL 상태(아래 비트) |
| 6 | device descriptor 명령을 처리 중인 클라이언트의 SA. Byte 5 bit 4가 1일 때만 유효하고, 아니면 0 |
| 7 | 처리 중인 device descriptor 명령의 Byte 1. Byte 5 bit 4가 1일 때만 유효하고, 아니면 0 |
| 8 | 예약 |

Byte 1~4는 Process Data 메시지가 평소에 element number(값의 주인인 DDOP 부분 번호)와 DDI(값 종류 번호)를 담는 자리다. TC Status는 특정 값을 다루지 않으므로 이 자리를 not available(전부 1)로 채운다. 그래서 Byte 1의 위 4비트도 1111이 되어 Byte 1이 `0xFE`(아래 4비트 1110 = Command E)가 된다.

| Byte 5 비트 | 뜻 |
|---|---|
| bit 1 | Task totals active: 태스크가 시작·재개돼 total이 누적될 수 있다. 0 → 1이면 클라이언트 내부 task total을 0으로 리셋하고 세기 시작, 1 → 0이면 세기를 멈추고 TC/DL이 Request Value로 읽어 갈 수 있다 |
| bit 2 | 비휘발성 메모리에 저장 중(busy) |
| bit 3 | 비휘발성 메모리에서 읽는 중(busy) |
| bit 4 | device descriptor 명령 실행 중(busy) |
| bits 5~7 | 0, 예약 |
| bit 8 | 메모리 부족 |

- element number·DDI의 not available 값은 버전 2에서 도입됐고, 클라이언트는 TC Status를 처리할 때 이 필드를 무시해야 한다.
- Byte 8은 "예약"이라고만 적혀 있고 채움 값이 없다. 아래 예제는 `FF`로 둔 가정이고, 수신 측은 Byte 8 값에 의존하지 않는 편이 안전하다(추론).

| 바이트 열 | 해석 |
|---|---|
| `FE FF FF FF 01 00 00 FF` | bit 1만 1: 태스크 실행 중, Busy 아님 |
| `FE FF FF FF 09 80 81 FF` | bit 1 + bit 4: 태스크 실행 중이면서 SA `0x80` 클라이언트의 device descriptor 명령 `0x81`(Object-pool Activate/Deactivate)을 처리 중 |

두 번째 줄을 한 바이트씩 읽어 보자.

1. Byte 1 `FE`: TC Status 메시지다.
2. Byte 2~4 `FF FF FF`: 쓰지 않는 칸이다.
3. Byte 5 `09`는 2진수 `0000 1001`이다. bit 1(Task totals active)과 bit 4(device descriptor 명령 처리 중)가 1이다.
4. Byte 6 `80`: 처리 중인 상대는 SA `0x80` 클라이언트다.
5. Byte 7 `81`: 처리 중인 명령의 Byte 1이 `0x81`, 즉 Object-pool Activate/Deactivate다(아래 10절).
6. Byte 8 `FF`: 예약이다.

### Client Task

연결을 유지하는 모든 클라이언트가 TC/DL에 보내는 생존·상태 메시지다. 목적지를 지정하고, 2 s 주기 + 태스크 상태가 바뀔 때마다 보내며, 메시지 사이에는 최소 200 ms를 둔다.

| Byte | 내용 |
|---|---|
| 1 | `0xFF`: bits 4~1 = 1111(Client Task), bits 8~5 = 1111(element number, not available) |
| 2 | `FF` |
| 3~4 | `FF FF` |
| 5~8 | 32비트 필드. bit 1 = TC Status Byte 5 bit 1에서 받은 Task totals active 값을 그대로 되돌린다. bits 2~32 = 0(예약) |

```
FF FF FF FF 01 00 00 00
```

TC/DL은 이 메시지의 element·DDI 필드를 무시한다. bit 1을 되돌려 받으므로 TC는 각 클라이언트가 최신 Task totals active 상태를 받았는지 확인할 수 있다(추론).

- Byte 5~8은 4바이트를 묶은 하나의 32비트 값이고, 낮은 자리 바이트(Byte 5)가 먼저 온다. 그래서 bit 1은 Byte 5의 가장 낮은 비트다.
- 위 예에서 Byte 5가 `01`이면 "Task totals active = 1을 받았다"는 뜻이다. 태스크가 멈춰 TC Status bit 1이 0이 되면 Client Task도 `FF FF FF FF 00 00 00 00`으로 바뀐다.
- 메아리처럼 들은 말을 되돌려주는 방식이다. TC는 메아리를 듣고 상대가 자기 말을 제대로 받았는지 안다.

<small>근거: ISO 11783-10 B.8.1, B.8.2</small>

## 10. Connection Deactivate의 실체 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

셧다운(5절)과 다른 TC로 옮기기([44장](/study/isobus/44-tc-multi-dl-functionality))에서 "Connection Deactivate를 보낸다"고 했다. 이 절은 그 메시지가 실제로 어떻게 생겼는지 본다.

셧다운과 TC 옮기기에서 말하는 Connection Deactivate는 별도 메시지가 아니다. DDOP를 활성화할 때 쓰는 Object-pool Activate/Deactivate 명령의 Byte 2를 0으로 보낸 것이다. Byte 2가 `FF`면 activate, 0이면 deactivate이고, deactivate는 "클라이언트가 의도적으로 연결을 끊는다"는 뜻이다. Byte 2 = 0의 정의는 버전 4에서 들어왔다.

```
81 00 FF FF FF FF FF FF    Object-pool Deactivate (클라이언트 → TC)
91 00 FF FF FF FF 00 FF    Object-pool Activate/Deactivate Response, 오류 없음 (TC → 클라이언트)
```

응답의 Byte 2 = 0은 오류 없음, Byte 3~4와 5~6은 오류 객체의 부모 ID와 객체 ID인데 오류가 없으면 NULL object ID(65535, `0xFFFF`)를 넣는다. 정상 deactivate에 대한 TC/DL의 최대 응답 시간은 2 s다. Deactivate가 버전 4 정의이므로, 버전 3 이하 TC에는 이 의미가 통하지 않을 수 있다. 버전 교환 결과를 보고 판단해야 한다(추론). DDOP 쪽 device descriptor 메시지 전체는 [50장 DDOP 전송과 설계 점검](/study/isobus/50-ddop-commands-design)에 있다.

두 줄을 바이트 단위로 읽으면 다음과 같다.

1. 요청 Byte 1 `81`은 `1000 0001`이다. 아래 4비트 1은 Command "device descriptor", 위 4비트 8은 Object-pool Activate/Deactivate다.
2. 요청 Byte 2 `00`이 deactivate를 뜻한다. `FF`였다면 activate다. 나머지는 `FF`로 채운다.
3. 응답 Byte 1 `91`은 위 4비트가 9로 바뀐 것이다. 9가 "Activate/Deactivate에 대한 응답"이다.
4. 응답 Byte 2 `00`은 오류 없음이다.
5. 응답 Byte 3~6 `FF FF FF FF`는 오류 객체 ID 두 개가 모두 NULL(65535)이라는 뜻이다. 여러 바이트 값은 낮은 자리 바이트가 먼저 오지만 `FF FF`는 어느 쪽으로 읽어도 `0xFFFF`다.
6. 응답 Byte 7 `00`은 오브젝트 풀 오류 코드가 없다는 뜻이고, Byte 8 `FF`는 예약이다.

::: details 파이썬으로 검산해 보기
```python
PROCESS_DATA_PF = 0xCB


def can_id(priority, da, sa):
    return (priority << 26) | (PROCESS_DATA_PF << 16) | (da << 8) | sa


def tc_status(totals_active, saving=False, reading=False, busy_client=None, out_of_memory=False):
    busy = busy_client is not None
    status = (int(totals_active) | int(saving) << 1 | int(reading) << 2
              | int(busy) << 3 | int(out_of_memory) << 7)
    client_sa, b6_byte1 = busy_client if busy else (0x00, 0x00)
    return bytes([0xFE, 0xFF, 0xFF, 0xFF, status, client_sa, b6_byte1, 0xFF])


def client_task(totals_active_echo):
    return bytes([0xFF, 0xFF, 0xFF, 0xFF]) + int(totals_active_echo).to_bytes(4, "little")


CLIENT_SA, TC_SA = 0x80, 0xF7
OBJECT_POOL_ACTIVATE_BYTE1 = 0x81

assert tc_status(True).hex(" ").upper() == "FE FF FF FF 01 00 00 FF"
activating = tc_status(True, busy_client=(CLIENT_SA, OBJECT_POOL_ACTIVATE_BYTE1))
assert activating.hex(" ").upper() == "FE FF FF FF 09 80 81 FF"

assert client_task(True).hex(" ").upper() == "FF FF FF FF 01 00 00 00"
assert client_task(False).hex(" ").upper() == "FF FF FF FF 00 00 00 00"

deactivate = bytes.fromhex("81 00 FF FF FF FF FF FF")
deactivate_ok = bytes.fromhex("91 00 FF FF FF FF 00 FF")
assert deactivate[0] & 0x0F == 0x1 and deactivate[0] >> 4 == 0b1000 and deactivate[1] == 0x00
assert deactivate_ok[0] >> 4 == 0b1001 and deactivate_ok[1] == 0x00
assert int.from_bytes(deactivate_ok[2:4], "little") == 0xFFFF == int.from_bytes(deactivate_ok[4:6], "little")

assert can_id(3, 0xFF, TC_SA) == 0x0CCBFFF7
assert can_id(3, TC_SA, CLIENT_SA) == 0x0CCBF780
print("OK")
```

```
OK
```

`tc_status`는 Byte 5의 각 비트를 자리에 맞게 밀어(`<<`) 합치고, Busy일 때만 Byte 6·7에 클라이언트 SA와 명령 Byte 1을 넣는다. 코드 안의 `b6_byte1`은 "처리 중인 device descriptor 명령의 Byte 1"을 뜻하는 변수 이름이다. assert 줄들은 9절과 10절의 바이트 열, 7절의 CAN ID 표를 그대로 다시 만들어 확인한다.
:::

<small>근거: ISO 11783-10 6.6.4.2, 6.7.1, A.1, B.6.10, B.6.11</small>

::: tip 핵심 정리
- 연결 순서는 주소 클레임과 6 s 대기 → TC Status → Working Set Master와 Client Task → 버전 교환 → DDOP 확인·전송·활성화 → 본 작업이다. DDOP를 처리하는 동안 TC는 Busy를 단 TC Status를 계속 보낸다.
- TC Status와 Client Task는 2 s 주기, 변화 시 즉시 송신, 최소 간격 200 ms를 지킨다. 6 s 끊기면 비정상 종료로 보고, 처리는 양쪽이 대칭이다.
- Key Switch Off 이후의 끊김은 정상 셧다운이다. 클라이언트는 Maintain Power와 Connection Deactivate를 보내고 다른 TC로 옮기지 않으며, TC는 마지막 Maintain Power 이후 최소 2 s 서비스를 유지한다.
- 연결 메시지는 모두 PGN 51968을 쓰고 Byte 1 하위 니블이 Command다. Version(0)·Deactivate(1)·TC Status(E)·Client Task(F)로 갈린다.
- Version은 버전 바이트부터 읽는다. 옵션의 예약 비트는 0이고, 클라이언트가 보고하는 수치는 조정 전 능력이다. TC Status의 Busy(bit 4)는 Byte 6·7과 짝이고, Client Task는 Task totals active를 되돌려 보낸다.
:::

::: details 확인 문제
1. (개념) 시퀀스 그림에서 클라이언트가 처음으로 보내는 메시지는 무엇인가? 그 전에 클라이언트는 무엇을 기다리는가?
2. (개념) 클라이언트가 TC Status를 6초 동안 받지 못했다. 평소 작업 중이라면 무엇을 하고, 오퍼레이터가 방금 키를 끈 상황이라면 무엇이 달라지는가?
3. (디코딩) TC Status `FE FF FF FF 09 80 81 FF`에서 Byte 5 `09`를 비트로 풀고, Byte 6·7과 함께 무슨 뜻인지 말하라.
4. (장애 진단) 버전 4 TC와 버전 4 클라이언트가 작업하던 중 오퍼레이터가 키를 껐다. 클라이언트는 "TC 연결 끊김" 경고를 띄우고 TC 번호 2에 연결을 시도했고, TC는 "클라이언트 응답 없음" 알림을 띄웠다. 양쪽 구현에서 빠진 것은 무엇인가? 클라이언트는 어떤 바이트를 보고 셧다운을 알아챘어야 하는가?
5. (설계) SIL(Software-in-the-Loop, 실제 장비 대신 소프트웨어로 상대를 흉내 내 시험하는 방식) 검증용 TC 서버 에뮬레이터의 TC Status 송신부를 설계하라. 송신 시작 시점, 주기와 간격 규칙, Byte 5~7을 언제 어떻게 채우는지, [42장 5절](/study/isobus/42-tc-task)의 태스크 상태와 어떻게 연결되는지를 포함한다.

**답 가이드**

1. Working Set Master 메시지다(Member 메시지가 함께 갈 수 있다). 그 전에 주소 클레임을 끝내고 6 s를 기다린 뒤, 선택한 TC가 보내는 TC Status를 받을 때까지 기다린다.
2. 평소라면 TC의 비정상 종료로 보고 Client Task 송신을 멈춘 뒤 초기화를 다시 시작한다(measurement가 활성이었다면 process data 송신도 멈춘다). 키를 끈 직후라면 정상 셧다운이므로 끊김을 고장으로 보지 않고, 경고를 띄우거나 다른 TC로 옮기지 않는다.
3. `09` = `0000 1001`이라 bit 1(Task totals active)과 bit 4(device descriptor 명령 처리 중)가 1이다. Byte 6 `80`은 처리 중인 클라이언트의 SA, Byte 7 `81`은 처리 중인 명령의 Byte 1(Object-pool Activate/Deactivate)이다. 즉 태스크가 돌고 있고, TC가 SA `0x80` 클라이언트의 DDOP 활성화를 처리하느라 바쁘다.
4. 셧다운은 Wheel-based speed and distance(PGN 65096) Byte 8 bits 4~3이 `01`(not Off)에서 `00`(Off)으로 바뀌는 것으로 알아챈다. 클라이언트는 Maintain Power(PGN 65095)를 보내고, Maximum time of tractor power(같은 메시지 Byte 7)를 감시하고, Connection Deactivate(`81 00 FF FF FF FF FF FF`)를 보내야 했다. 또 TC Status 끊김을 비정상 종료로 보지 말고 다른 TC로 옮기지 말아야 했다(5절 표의 클라이언트 d). TC는 예상치 못한 클라이언트 종료 감지 로직을 끄고(TC a), 활성 DDOP를 가진 클라이언트의 마지막 Maintain Power 이후 최소 2 s 동안 서비스를 유지해야 했다(TC b). 키가 다시 Not Off가 되면 양쪽 모두 재초기화한다.
5. 시작: 주소 클레임과 전역 address claimed 요청을 마치고 6 s 뒤. 형식: PGN 51968, 우선순위 3, DA 255, Byte 1 `0xFE`, Byte 2~4 `FF`. 주기: 2 s + 어느 바이트든 바뀌면 즉시, 단 송신 간격 200 ms 이상(바뀐 값을 모아서 보낸다). Byte 5 bit 1은 태스크가 Running(시작·재개)이면 1, Paused·Completed로 가면 0이고, 이 전이가 클라이언트 task total의 리셋·정지 신호다. bit 4는 DDOP 전송·활성화 같은 device descriptor 명령을 처리하는 동안 1로 두고 Byte 6에 그 클라이언트 SA, Byte 7에 그 명령의 Byte 1을 넣으며, 아니면 Byte 6·7은 0이다. bit 2·3은 비휘발성 메모리 쓰기·읽기 중, bit 8은 메모리 부족이다. 짝이 되는 수신부는 클라이언트별 Client Task를 6 s 감시해 끊기면 (태스크 실행 중일 때) DeviceAllocation을 닫고, Key Switch Off 뒤에는 이 감시를 끈다. 전원 사이클 뒤에는 이전 태스크 상태를 복원한다(6절).
:::

## 다음 챕터

- 다음: [44장 다중 TC, Data Logger, TC 기능성](/study/isobus/44-tc-multi-dl-functionality)
