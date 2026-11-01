---
title: "네트워크 계층과 NIU: 버스와 버스를 잇는 장치"
description: "나뉜 CAN 버스를 잇는 NIU가 하는 네 가지 일과 repeater, bridge, router, gateway의 차이를 익히고, NIU를 설정하는 network message와 다른 주소 공간의 CF와 대화하는 connection을 읽는다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, NIU, NetworkLayer, Bridge, Router, Gateway]
prev: /study/isobus/20-isobus-network-topology
next: /study/isobus/22-tractor-ecu
---

# 네트워크 계층과 NIU: 버스와 버스를 잇는 장치

::: info 학습 목표
- NIU가 왜 필요한지, NIU가 하는 네 가지 일(전달, 거르기, 주소 변환, 재포장)을 설명할 수 있다.
- repeater, bridge, router, gateway, TECU를 "주소 공간을 나누는가"와 "무엇을 거르는가"로 구분할 수 있다.
- NIU가 메시지를 받은 순서가 아니라 우선순위 순서로 넘겨야 하는 이유를 설명할 수 있다.
- network message(PGN 60672) 프레임에서 function code, port pair, PGN 엔트리를 찾아 읽을 수 있다.
- 주소 공간이 다른 세그먼트의 CF와 connection과 virtual CF로 대화하는 순서를 설명할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [20장 ISOBUS 네트워크 구성](/study/isobus/20-isobus-network-topology), [13장 주소 클레임](/study/isobus/13-j1939-address-claim), [15장 TP 기초](/study/isobus/15-tp-bam-cmdt)
- 이 장에서 처음 나오는 말
  - 세그먼트(segment): 양 끝에 종단 회로가 달린 CAN 버스 한 토막. 같은 세그먼트의 ECU는 같은 전선을 함께 쓴다.
  - NIU(Network Interconnection Unit): 세그먼트와 세그먼트를 잇는 장치. 이 장의 주인공이다.
  - 포트(port): NIU가 세그먼트 하나에 붙는 연결구. NIU는 포트를 2개 이상 가진다.
  - 주소 공간(address space): 같은 주소(SA) 번호 체계를 함께 쓰는 범위. 주소 공간이 같으면 두 CF가 같은 SA를 쓸 수 없다.
  - filter database: NIU가 어떤 메시지를 통과시키고 어떤 메시지를 막을지 적어 둔 표.
  - virtual CF: NIU가 다른 세그먼트에 있는 CF를 대신해 이쪽 세그먼트에 세워 두는 대역 CF.
:::

두 마을을 잇는 다리 입구에 검문소가 있다고 해 보자. 검문소는 차를 그냥 통과시키기도 하고, 통행 목록에 있는 차만 들여보내기도 하고, 번호판을 건너편 것으로 바꿔 달아 주기도 하고, 짐을 풀어 새 상자에 다시 꾸려 보내기도 한다. ISOBUS에서 이 검문소 노릇을 하는 장치가 NIU다. 이 장은 NIU가 하는 일과 종류를 먼저 보고, 이어서 NIU를 설정하고 상태를 읽는 메시지와 주소 체계가 다른 건너편 장치와 대화하는 방법을 차례로 본다.

## 1. NIU란: 버스와 버스를 잇는 검문소

[20장](/study/isobus/20-isobus-network-topology)에서 ISOBUS 네트워크가 트랙터 버스와 작업기 버스(implement bus)라는 두 세그먼트로 나뉘고, 그 사이를 TECU(Tractor ECU, 트랙터 ECU)가 잇는다는 것을 봤다. 이 절은 이렇게 나뉜 세그먼트를 잇는 장치인 NIU가 무엇이고 왜 필요한지 본다.

버스를 나누는 이유는 격리다. 작업기 쪽에서 전기 고장이 나거나 메시지가 폭주해도 트랙터 구동계 버스까지 번지지 않게 하려는 것이다. 그래도 나뉜 버스 사이로 필요한 메시지는 오가야 한다. 필요한 것만 골라 오가게 하는 일을 NIU가 맡는다.

ISO 11783-4(ISOBUS의 네트워크 계층을 정하는 표준 문서)는 세그먼트가 여럿인 네트워크에서 세그먼트 사이의 메시지 전달을 관리하는 층을 네트워크 계층이라 부르고, 그 일을 하는 장치를 NIU라 한다. 검문소 비유로 보면 NIU의 종류는 할 수 있는 일의 수로 갈린다. 아래 그림은 대표적인 네 유형이 무엇을 하는지 한눈에 보여 준다.

![NIU 네 유형을 검문소에 비유한 표: repeater는 전달만, bridge는 전달과 거르기, router는 주소 변환까지, gateway는 재포장까지 하며, repeater와 bridge는 주소 공간을 공유하고 router와 gateway는 나눈다](/images/study-isobus/21-niu-checkpoint-light.png)
![NIU 네 유형을 검문소에 비유한 표: repeater는 전달만, bridge는 전달과 거르기, router는 주소 변환까지, gateway는 재포장까지 하며, repeater와 bridge는 주소 공간을 공유하고 router와 gateway는 나눈다](/images/study-isobus/21-niu-checkpoint-dark.png)

- Repeater(리피터): 모든 차를 그대로 통과시킨다. 약해진 신호를 다시 만들어 건너편으로 내보낼 뿐이다.
- Bridge(브리지): 통행 목록을 보고 골라서 통과시킨다. 번호판(보낸 쪽 주소 SA)은 그대로다.
- Router(라우터): 번호판을 건너편 체계에 맞게 바꿔 단다. 그래서 양쪽의 주소 공간이 따로다.
- Gateway(게이트웨이): 짐(값)을 풀어 새 상자(새 메시지)에 다시 꾸려 보낸다.

아래로 갈수록 할 수 있는 일이 하나씩 늘어난다. bridge는 repeater의 일에 거르기를, router는 주소 변환을, gateway는 재포장을 더한다. 다섯 번째 유형인 TECU는 트랙터 버스와 작업기 버스를 잇는 전용 NIU다. 4절과 [22장](/study/isobus/22-tractor-ecu)에서 자세히 본다.

비유가 맞지 않는 점도 있다. 실제 검문소는 차를 세웠다가 보내지만, repeater는 프레임을 붙잡아 두지 않고 비트 단위로 거의 동시에 흘려보낸다. 붙잡아 두었다가 보내는 것은 bridge부터다.

### 용어 정리

ISO 11783-4가 쓰는 용어를 정리한다. CF(Control Function)는 ECU 안에서 주소 하나를 갖고 통신하는 기능 단위다. ECU 하나에 CF가 여럿 들어 있을 수도 있다.

| 용어 | 뜻 |
|---|---|
| NIU(Network Interconnection Unit) | 네트워크나 네트워크 세그먼트를 서로 잇는 ECU |
| port | NIU가 세그먼트에 붙는 인터페이스. NIU는 서로 다른 세그먼트에 붙은 포트를 2개 이상 가진다 |
| port pair | 포트 2개를 묶어 "어느 세그먼트에서 어느 세그먼트로" 흐르는지 나타낸 것 |
| virtual CF / actual CF | NIU가 다른 세그먼트의 실제 CF와 같은 NAME으로 세워 주는 겉보기 CF / ECU가 그 세그먼트에 직접 세운 CF |
| transparent | 서비스를 받는 CF가 그 서비스의 출처(중간의 NIU)를 몰라도 되는 상태 |

transparent(투명하다)는 유리창 너머가 그대로 보이듯, CF가 중간에 NIU가 있다는 것을 몰라도 건너편과 통신할 수 있다는 뜻이다. NAME은 장치마다 고유한 64비트 이름이다([12장](/study/isobus/12-j1939-address-name)).

### NIU가 하는 네 가지 일

NIU는 유형에 따라 다음 네 가지 일 가운데 하나 이상을 한다. 어떤 일을 하느냐가 4절의 유형을 가른다. 표의 PGN(Parameter Group Number)은 메시지의 종류를 가리키는 번호다.

| 일 | 하는 일 | 자세히 |
|---|---|---|
| 전달(forwarding) | 한 포트에서 받은 프레임을 다른 포트로 내보낸다 | 3절 |
| 거르기(filtering) | filter database에 따라 PGN 단위로 통과·차단한다 | 3절 |
| 주소 변환(address translation) | look-up table(대응표)로 주소를 바꿔, 세그먼트 하나를 주소 하나로 보이게 한다 | 3절 |
| 재포장(repackaging) | 여러 메시지의 파라미터를 꺼내 새 메시지로 다시 묶는다 | 3절 |

NIU는 내부 데이터베이스(filter database 같은 설정 표)를 읽고 고치는 기능(database management)도 가질 수 있다. 이 기능은 5~7절에서 본다.

### 주소 공간: 하나의 네트워크인가, 둘인가

NIU를 이해하는 데 가장 중요한 말이 주소 공간이다. 표준이 드는 예가 이 개념을 잘 보여 준다. bridge는 전선(매체)과 트래픽을 두 세그먼트로 나누지만, 주소와 식별자로 보면 여전히 <strong>하나의 네트워크</strong>다. 양쪽 CF가 같은 주소 번호 체계를 나눠 쓰므로 한쪽에서 쓰는 SA를 다른 쪽에서 쓸 수 없다.

반대로 NIU가 주소 공간까지 나누면 양쪽 세그먼트에서 같은 주소를 서로 다른 CF가 써도 된다. 서로 다른 도시에 같은 번지수가 있어도 되는 것과 같다.

NIU는 서브네트워크(NIU 뒤에 따로 붙은 작은 네트워크)의 CF를 대신해 address claim(이 주소를 쓰겠다고 알리는 절차, [13장](/study/isobus/13-j1939-address-claim))에 참여할 수도 있다. 다만 제조사 고유(proprietary) 서브네트워크에 붙는 router·gateway는 응용마다 달라서 ISO 11783이 정의하지 않는다. 부품 제조사나 OEM(완성 장비 제조사)이 정한다.

### 전형적인 배치와 포트 번호

표준이 드는 전형적인 배치는 아래 그림과 같다. TECU는 P2 포트로 트랙터 네트워크(엔진·변속기·브레이크·히치 컨트롤러)에, P1 포트로 작업기 네트워크에 붙는다. 작업기 안에서는 또 다른 NIU가 P1으로 작업기 버스에, P2·P3로 "ISO 11783 또는 다른 규격" 서브네트워크(예: 조명 컨트롤러가 붙은 서브버스)에 붙는다. 네트워크 전체 요구를 정하는 ISO 11783-1도 ECU가 여러 개인 작업기는 NIU로 추가 ECU를 작업기 네트워크에서 격리할 수 있다고 적는다.

![전형적인 NIU 배치: TECU가 P2로 트랙터 네트워크, P1로 작업기 네트워크에 붙고, 작업기 NIU가 P1로 작업기 네트워크, P2와 P3로 서브네트워크에 붙는다. TECU에서 트랙터에서 작업기로 가는 방향은 port pair 0x21, 반대는 0x12다](/images/study-isobus/21-niu-ports-light.png)
![전형적인 NIU 배치: TECU가 P2로 트랙터 네트워크, P1로 작업기 네트워크에 붙고, 작업기 NIU가 P1로 작업기 네트워크, P2와 P3로 서브네트워크에 붙는다. TECU에서 트랙터에서 작업기로 가는 방향은 port pair 0x21, 반대는 0x12다](/images/study-isobus/21-niu-ports-dark.png)

TECU의 포트 번호는 정해져 있다. port 1이 작업기 버스, port 2가 트랙터 버스다. 그림 아래쪽 화살표의 `0x21`과 `0x12`는 "어느 포트에서 어느 포트로"를 한 바이트에 담은 port pair 값이다. 읽는 법은 5절에서 본다.

<small>근거: ISO 11783-4 3, 4.1, 4.2, Figure 1, ISO 11783-1 6.6.4, ISO 11783-9 4.1.2</small>

## 2. NIU의 기본 규칙: 속도, 순서, 경로

NIU는 메시지를 넘겨주는 장치라서 얼마나 빨리, 어떤 순서로 넘기는지가 중요하다. 이 절은 NIU를 고르는 성능 기준과 NIU가 지켜야 할 규칙을 본다.

### 성능 기준 세 가지

어떤 NIU가 응용에 맞는지는 세 가지 성능 기준으로 판단한다. transit delay는 메시지가 NIU를 지나가는 데 걸리는 시간이다.

- 초당 forwarding 보장 메시지 수: 평균·피크 버스 부하가 이를 넘으면 메시지가 유실될 수 있다.
- 초당 filtering 보장 메시지 수: DB 엔트리가 많아 이를 넘으면 메시지가 과도하게 지연될 수 있다.
- 최대 transit delay: 한 CF가 보낸 메시지가 다른 세그먼트의 CF에 닿기까지의 최악 지연이다.

이 세 값은 NIU에게 직접 물어 읽을 수 있다(7절의 parametric 5·6·7). 고를 때 보는 기준과 동작 중에 확인하는 수단이 짝을 이루는 셈이다.

### 요구사항: shall과 should

표준 문서는 반드시 지켜야 하는 요구를 shall로, 지키기를 권하는 요구를 should로 적는다. NIU 일반 요구사항에는 둘이 섞여 있다.

| 수준 | 요구 |
|---|---|
| shall | filtering·forwarding 보장 속도를 제공한다 |
| shall | 최대 transit delay 값을 넘지 않는다 |
| shall | 한 포트에서 받아 다른 포트로 내보내는 순서는 메시지 우선순위를 따른다. 높은 우선순위를 먼저 보낸다 |
| shall | 같은 우선순위 안에서는 받은 순서대로 보낸다 |
| shall | 단순 FIFO 큐를 쓰지 않는다 |
| should | filter database를 읽고 고치는 기능을 제공한다 |
| should | bridge·router·gateway 관리를 위한 forwarding·filtering·주소 변환·재포장 설정에 표준 접근(database management)을 제공한다 |
| should | 동작 중에는 네트워크의 모든 CF에 transparent하다 |

우선순위는 CAN ID 맨 앞 3비트에 담긴 0~7 값이고, 숫자가 작을수록 높다([9장](/study/isobus/09-j1939-message)). FIFO(First In First Out)는 먼저 들어온 것을 먼저 내보내는 줄 서기 방식이다.

### 왜 FIFO를 쓰면 안 되나

FIFO를 금지하는 이유는 head-of-line blocking(줄 맨 앞이 막혀 뒤가 모두 기다리는 현상)이다. 응급차가 와도 앞에 선 차가 다 빠질 때까지 기다려야 하는 1차로 도로를 떠올리면 된다.

큰 데이터를 나눠 보내는 TP.DT 패킷은 기본 우선순위가 7이다([15장](/study/isobus/15-tp-bam-cmdt)). 이 패킷이 큐에 줄지어 있을 때 우선순위 3인 Lighting command(조명 명령, [22장](/study/isobus/22-tractor-ecu))가 들어오면, FIFO는 앞의 TP.DT를 다 보낸 뒤에야 조명 명령을 보낸다. 표준은 이를 "특정 포트로 가는 메시지 전체가 과도하게 지연될 수 있다"고 표현한다.

구현에서는 큐에서 무엇을 먼저 꺼낼지 정하는 기준값(정렬 키)을 잘 골라야 한다.

::: warning 정렬 키를 식별자 전체로 잡으면 안 된다
요구사항을 문자 그대로 만족하려면 정렬 키는 (priority, 수신 순번)이어야 한다. 29비트 식별자 전체로 정렬하면 같은 priority 안에서 PGN·SA가 작은 프레임이 먼저 나가 "같은 우선순위는 받은 순서대로"를 어긴다. CAN 컨트롤러의 송신 버퍼를 여러 개 쓰면 컨트롤러가 버퍼 사이를 식별자 순으로 중재해 같은 문제가 생길 수 있다. 표준이 다루지 않는 구현 주의점이다(해석).
:::

아래 코드는 (우선순위, 받은 순번) 순서로 꺼내는 큐를 파이썬 `heapq`(가장 작은 값을 먼저 꺼내는 자료 구조)로 만들고, 예제 프레임 다섯 개가 나가는 순서를 확인한다.

::: details 우선순위 forwarding 큐 검산 (Python)
```python
import heapq

def forward_order(frames):
    queue = []
    for seq, (priority, name) in enumerate(frames):
        heapq.heappush(queue, (priority, seq, name))
    return [heapq.heappop(queue)[2] for _ in range(len(queue))]

arrived = [(7, "TP.DT #1"), (7, "TP.DT #2"), (6, "Maintain power"),
           (3, "Lighting command"), (7, "TP.DT #3")]
assert forward_order(arrived) == [
    "Lighting command", "Maintain power", "TP.DT #1", "TP.DT #2", "TP.DT #3"]
```
:::

결과를 보면 우선순위 3인 Lighting command가 맨 먼저, 6인 Maintain power가 다음으로 나간다. 우선순위 7인 TP.DT 세 개는 받은 순서(#1, #2, #3)대로 나간다. 튜플 `(priority, seq, name)`의 두 번째 값 `seq`가 같은 우선순위 안의 순서를 지켜 준다.

### 경로는 하나만, 주소는 254개까지

토폴로지(장치들이 이어진 모양) 요구는 한 줄이다. 두 CF 사이 경로는 <strong>단 하나</strong>여야 한다. 경로가 둘이면 같은 메시지가 고리(루프)를 돌며 끝없이 복제될 수 있다. 표준은 루프 감지나 메시지의 무한 복제 방지를 요구하지 않으며, 루프가 없게 만드는 것은 OEM 책임이다. 고장에 대비한 중복 세그먼트(내결함성)는 써도 되지만, 경로를 감지·선택·자동 재구성하는 장치는 NIU 공급자가 책임진다.

주소는 8비트라 256개(0~255)다. 이 가운데 254(null, 주소를 아직 얻지 못한 CF가 쓰는 값)와 255(global, "모두에게"를 뜻하는 목적지 값)를 빼면 이론상 254개다([12장](/study/isobus/12-j1939-address-name)). 실제로는 ECU마다 버스에 주는 전기 부하가 노드 수를 먼저 제한한다.

그런데 같은 ISO 11783-4가 connection 규칙(9절 규칙 3)에서는 "세그먼트당 253개 CF 주소"라고 적어 두 수치가 1 다르다. 표준이 차이를 설명하지 않으므로 설계 한계는 보수적으로 작은 쪽을 잡는 편이 안전하다.

<small>근거: ISO 11783-4 4.1.1.3, 5.1~5.3, 6.1, 6.9.4, ISO 11783-3 5.10.5</small>

## 3. NIU가 하는 일 자세히: 전달, 거르기, 주소 변환, 재포장

1절에서 본 네 가지 일을 하나씩 자세히 본다. 전달은 모든 NIU가, 거르기는 bridge부터 하는 기본 동작이고, 주소 변환과 재포장은 router와 gateway의 몫이다.

### 전달: 같은 주소 공간이면 원래 SA 그대로

repeater·bridge처럼 같은 주소 공간으로 내보낼 때 NIU는 <strong>원 발신자와 같은 주소</strong>로 프레임을 내보낸다. NIU는 메시지가 들어온 세그먼트로 되돌려 보내지 않고, ISO 11783 네트워크 안에서 주소는 유일하므로 보통 중재 문제가 생기지 않는다. 중재(arbitration)는 여러 ECU가 동시에 보내려 할 때 CAN ID를 비트 단위로 비교해 하나만 남기는 절차다([5장](/study/isobus/05-can-arbitration)).

유일한 예외는 address claim이다. NIU가 넘긴 address claim과, 건너편 세그먼트에서 다른 CF가 같은 주소로 동시에 보낸 claim이 부딪히는 경우다. 두 프레임은 식별자가 같고(같은 PGN 60928, 같은 SA) 데이터(NAME)만 다르므로 CAN 중재로 가려지지 않고 데이터 필드에서 비트 에러가 난다([CAN 중재와 우선순위](/study/isobus/05-can-arbitration), [CAN 에러 처리](/study/isobus/06-can-error)).

컨트롤러가 자동 재전송을 계속하면 충돌이 되풀이돼 NIU가 bus off(에러가 쌓여 CAN 컨트롤러가 버스에서 스스로 빠지는 상태)에 빠지고, 복구될 때까지 다른 모든 forwarding이 멈춘다. 그래서 표준은 이 낮은 확률의 상황에서 NIU가 CAN 칩의 자동 재전송을 멈추라고 권고한다(should).

나머지 규칙 두 가지:

- 주소 변환을 하지 않는 단순 repeater·bridge는 자기 주소를 claim하기 전에도 forwarding을 시작해도 된다. 반대로 주소 변환을 하려면 먼저 유효한 claimed address가 있어야 한다(아래 주소 변환 참고).
- NIU가 power-up 시퀀스를 끝내기 전에는 그 뒤의 서브네트워크 CF들이 다른 메시지를 받지 못한다. NIU가 늦게 깨어나면 서브네트워크 CF는 그 사이의 메시지를 놓친다.

### 거르기: block 모드와 pass 모드

거르기는 filter database에 적힌 PGN을 보고 메시지를 통과시키거나 막는 일이다. 방식은 두 가지다. block 모드는 "출입 금지 명단"에 있는 것만 막고 나머지는 다 들여보낸다. pass 모드는 "출입 허가 명단"에 있는 것만 들여보낸다.

| 항목 | Block mode (0) | Pass mode (1) |
|---|---|---|
| 기본 동작 | 전부 forwarding | 전부 차단 |
| DB 엔트리의 뜻 | 막을 PGN | 통과시킬 PGN |
| 쓰임 | 세그먼트별 트래픽 감소. ISO 11783 bridge의 <strong>권장 모드</strong> | 특정 기능을 하는 서브네트워크를 잇는 포트. router·gateway의 전형적 설정 |
| 엔트리 관리 | 보통 조립·초기 설정 때 넣고 비휘발성 메모리에 둔다 | 네트워크 전체 CF·기능을 미리 알거나 CF가 엔트리를 추가할 수 있어야 한다. DB가 크면 메모리·처리 능력이 더 든다 |
| 주의 | 세그먼트마다 트래픽이 늘 수 있지만, 허용 범위 안이면 필터링 알고리즘이 아예 필요 없다 | network management, 진단, global request는 항상 통과하도록 일부 엔트리를 영구로 둬야 한다 |

표준이 드는 TECU 필터 예가 전형적이다. TECU는 엔진 데이터가 작업기 세그먼트로 나가지 않게 막으면서, 작업기 세그먼트에서 오는 request는 트랙터 쪽으로 넘긴다. 방향마다 다른 규칙을 거는 것이 port pair의 존재 이유다.

8바이트보다 긴 데이터를 여러 프레임에 나눠 보내는 메시지는 거르기가 까다롭다. TP·ETP와 Fast Packet(GPS 위치 같은 항법 메시지를 나눠 보내는 NMEA 2000 방식)이 그렇다. 이런 패킷화 메시지는 <strong>안에 담긴 메시지의 PGN</strong>으로 필터링해야 한다(shall).

문제는 조각마다 PGN이 붙어 있지 않다는 점이다. TP에서 전송을 여는 TP.CM(RTS·CTS·BAM 등)은 Byte 6~8에 담긴 메시지의 PGN을 싣지만 데이터 조각인 TP.DT에는 PGN이 없다. 그러니 NIU는 TP.CM으로 열린 세션(SA·DA 쌍)을 기억해 뒤따르는 TP.DT가 어느 PGN 소속인지 판단해야 한다(구현상 귀결, 해석). TP 구조는 [15장 TP 기초](/study/isobus/15-tp-bam-cmdt)를 참고한다.

### 주소 변환과 재포장

<strong>Address translation</strong>(주소 변환)은 한 세그먼트(작업기)를 주소 하나로 참조하게 해 준다. 작업기 안 조명 기능의 주소를 몰라도 작업기의 대표 주소 하나로 보내면 된다. 회사 대표 번호로 전화하면 교환원이 내선으로 돌려 주는 것과 같다. 이를 위해 대응하는 SA·DA를 찾는 look-up table인 address translation database가 있어야 하고(shall), NIU는 이 서비스를 하기 전에 유효한 claimed address를 가져야 한다. DA(Destination Address)는 받는 쪽 주소다.

<strong>Message repackaging</strong>(재포장)은 세그먼트를 건널 때 메시지를 다시 묶는다. 메시지당 쓸모 있는 파라미터를 늘려 버스 트래픽을 줄이고, 특정 CF가 받아야 하는 메시지 종류 수도 줄인다. 어떻게 묶을지 정하는 DB나 처리 루틴이 있는 것이 좋다(should).

[22장](/study/isobus/22-tractor-ecu)에서 볼 TECU가 바로 이 일을 한다. 트랙터 버스의 여러 메시지에서 값을 모아 ISO 11783-7(트랙터·작업기 메시지를 정하는 표준 문서)이 정한 메시지로 다시 만들고, 자기 SA로 작업기 버스에 보낸다.

::: tip 1~3절 정리
- NIU의 일은 forwarding·filtering·주소 변환·재포장 네 가지이고, 성능은 forwarding·filtering 처리량과 최대 transit delay로 판단한다.
- 큐는 (priority, 수신 순번)으로 정렬한다. 단순 FIFO는 shall not이다.
- 패킷화 메시지는 안에 담긴 PGN으로 필터링한다. bridge는 block 모드, router·gateway는 pass 모드가 전형이다.
:::

<small>근거: ISO 11783-4 6.1~6.4, 6.2.1, 6.6.2.1, ISO 11783-3 5.10.4.1, ISO 11783-9 4.2.2</small>

## 4. NIU 유형 비교: repeater부터 TECU까지

1절의 검문소 그림에서 네 유형을 할 수 있는 일로 나눠 봤다. 이 절은 TECU까지 다섯 유형을 주소 공간, 지연, filter mode로 더 자세히 비교한다. 아래 그림은 세그먼트 1에서 보낸 프레임이 각 NIU를 지나 세그먼트 2에 어떤 모습으로 나타나는지 보여 준다.

![NIU 유형별 비교: repeater와 bridge는 원래 SA를 유지해 주소 공간을 공유하고, router·gateway·Tractor ECU는 자기 주소로 다시 내보내 주소 공간을 나눈다](/images/study-isobus/13-niu-types-light.png)
![NIU 유형별 비교: repeater와 bridge는 원래 SA를 유지해 주소 공간을 공유하고, router·gateway·Tractor ECU는 자기 주소로 다시 내보내 주소 공간을 나눈다](/images/study-isobus/13-niu-types-dark.png)

그림 왼쪽이 세그먼트 1에서 보낸 프레임, 가운데가 NIU, 오른쪽이 세그먼트 2에 나타나는 프레임이다. repeater와 bridge를 지나면 SA `0x80`(=128)이 그대로 보이고, router·gateway·TECU를 지나면 SA가 NIU 자신의 주소로 바뀐다.

아래 표에 나오는 말을 먼저 풀어 둔다.

- sub-bit-time: 비트 하나가 버스에 머무는 시간(bit time)보다 짧은 간격. 250 kbit/s에서 bit time은 4 µs다.
- anti-loopback/lockout: 내보낸 신호가 되돌아와 다시 중계되는 고리를 막는 장치.
- filter mode: 3절의 block(0)·pass(1) 모드.
- DB 관리: filter database 같은 설정 표를 표준 메시지로 읽고 고치는 기능(5~7절).
- NIU Type 값: NIU가 자기 유형을 알릴 때 쓰는 번호(7절의 parametric 16).

| 유형 | 하는 작업 | 주소 공간·address claim | 지연 기준 | filter mode | DB 관리 | NIU Type 값 |
|---|---|---|---|---|---|---|
| Repeater | forwarding만. 같은 데이터 속도의 세그먼트 사이에서 신호를 sub-bit-time 간격으로 재생, anti-loopback/lockout | 공유. 모든 메시지가 지나간다 | bit time의 10% 미만 권장(250 kbit/s에서 400 ns) | 필터 불가 | 정의 없음 | 1 |
| Bridge | forwarding + filtering. 메시지를 저장했다 내보낸다 | 공유. address claim이 양쪽에 다 보인다 | 최대 10 ms 권장 | block(0) 권장 | should | 2 |
| Router | + 주소 재매핑 | 분리. <strong>address claim이 통과하지 않는다</strong> | 명시 없음(변환·전달 지연이 있다) | pass(1) 전형 | 필수 아님, should | 3 |
| Gateway | router 기능 + 파라미터 재포장 | 분리 | 명시 없음(변환·재포장·전달 지연) | pass(1) 전형 | 필수 아님, should | 4 |
| Tractor ECU | 트랙터 버스와 작업기 버스를 잇는 특수 NIU. 트랙터 네트워크를 격리·보호(shall) | 트랙터 버스 정보를 자기 SA로 다시 보낸다 | ISO 11783-4에 명시 없음 | 예: 엔진 데이터 차단 | 명시 없음 | 5 |

NIU Type 값에는 0과 250도 있다. 0은 "그 port pair에 상호작용 없음", 250은 port pair마다 유형이 다른 NIU가 general parametric에 쓰는 "Multiple"이다. Repeater·Bridge 값은 그 장치가 통신용 주소를 claim했을 때만 쓸 수 있다. 원래 transparent한 장치라 다른 CF가 존재 자체를 모를 수 있기 때문이다.

::: info 동작 계층은 해석이다
표준은 NIU 유형에 OSI 계층(통신 기능을 물리 계층부터 응용 계층까지 일곱 층으로 나눈 참조 모델, [8장](/study/isobus/08-j1939-intro))을 지정하지 않는다. 동작 방식으로 대응시키면 repeater는 비트 신호를 재생하므로 물리 계층, bridge는 프레임을 저장해 PGN으로 거르므로 데이터 링크 계층, router는 주소를 바꾸므로 네트워크 계층, gateway는 파라미터를 다시 묶으므로 응용 계층에 가깝다. TECU는 TECU를 정하는 ISO 11783-9가 말하듯 연결된 네트워크에 따라 gateway 또는 router처럼 동작한다.
:::

유형을 고를 때 볼 점:

- <strong>repeater의 10% 규칙</strong>: CAN 중재는 비트 단위로 일어나므로, 지연이 비트 시간의 일부에 그쳐야 repeater 양쪽 노드가 같은 중재에 참여할 수 있다([5장](/study/isobus/05-can-arbitration)). 지연이 큰 물리 계층은 repeater를 지원하지 못한다. fault isolation(고장 격리)을 제공한다면 세그먼트 버스 고장 때 해당 송신기를 끌 수 있다.
- <strong>bridge의 10 ms</strong>: 데이터 링크 계층을 정하는 ISO 11783-3은 응답 대기 시간 T3 = 1.25 s([11장](/study/isobus/11-j1939-request2-timing))가 브리지를 거친 지연에도 불필요한 타임아웃이 나지 않게 하는 값이라고 설명하며, 브리지 10개(대당 최대 50 ms, 한 방향 500 ms)를 예로 든다. ISO 11783-4 권장치 10 ms의 bridge라면 같은 10단에서도 100 ms라 여유가 크다.
- <strong>router 너머의 CF</strong>: address claim이 넘어오지 않으니 router 뒤 CF는 보이지 않는다. 그 CF와 직접 대화하려면 router의 주소 변환에 맡기거나, 8절의 connection으로 virtual CF를 세운다.

<small>근거: ISO 11783-4 5.1.3, 6.7.2.1, 6.6.2.1, 7.1~7.5, Table 7, ISO 11783-3 5.13.3, ISO 11783-9 4.2.1, 4.2.2</small>

## 5. Network message: NIU에게 말을 거는 메시지

NIU의 설정표를 읽거나 고치고, 건너편 목록과 상태를 물을 때는 NIU에게 직접 메시지를 보낸다. 이 절은 그 메시지의 형식과 방향 표기(port pair)를 보고, 짧은 프레임 하나를 끝까지 읽어 본다.

### PGN 하나, function code 네 묶음

NIU의 parametric(상태·통계 값), DB, 토폴로지, connection은 모두 network message <strong>PGN 60672(0xED00)</strong> 하나로 다룬다. PF(PGN 가운데 바이트, PDU Format)가 237(`0xED`)로 240보다 작으므로 PDU1, 즉 받는 쪽을 지정하는 메시지이고 PS 자리에 DA가 들어간다([9장](/study/isobus/09-j1939-message)). 기본 우선순위가 6이라 CAN ID는 `0x18ED<DA><SA>` 꼴이 된다. 데이터 길이는 가변이고 반복 전송은 초당 5회를 넘으면 안 된다.

동작 규칙:

- 특정 목적지로 보낸 request·command에는 응답이 반드시 와야 한다. 지원하지 않거나 수행할 수 없으면 그렇다는 acknowledgement라도 보낸다.
- CF는 응답이나 "no response" 타임아웃을 기다린 뒤에 다음 request·command를 보낸다. 응답하는 쪽은 Tr = 200 ms 안에 답하고, 기다리는 쪽은 T3 = 1.25 s까지 기다린다([11장](/study/isobus/11-j1939-request2-timing)).
- 8바이트보다 짧으면 남는 바이트를 `FF`로 채우고, 8바이트를 넘으면 TP를 쓴다. `FF` 채움은 "이 자리에는 값이 없다"는 표시다.

데이터 Byte 1은 function code, 즉 NIU에게 무슨 일을 하라는지 가리키는 번호다. 번호는 기능군마다 64개 단위 블록을 차지한다.

| function code 범위 | 기능군 | 정의된 코드 | 상위 2비트 |
|---|---|---|---|
| 0~63 | filter database | 0~4, 6, 7 (5는 폐기) | `00` |
| 64~127 | 네트워크 토폴로지 | 64~67 | `01` |
| 128~191 | parametrics | 128~133 | `10` |
| 192~255 | connection | 192~195 | `11` |

상위 2비트로 기능군을 먼저 가르고 하위 비트로 세부 기능을 고르는 디스패치가 자연스럽다(표준이 이렇게 해석하라고 정하지는 않는다). 이 장에서 쓰는 코드는 다음과 같다. 코드 전체 목록은 [부록 Part 4](/study/isobus/appendix-iso-part04)에도 있다.

| code | 메시지 | 방향 | 하는 일 |
|---|---|---|---|
| 0 / 1 | N.MFDB_Request / N.MFDB_Response | CF → NIU / NIU → CF | filter database 사본 요청과 응답 |
| 2 | N.MFDB_Add | CF → NIU | 엔트리 추가 |
| 3 | N.MFDB_Delete | CF → NIU | 엔트리 삭제 |
| 4 | N.MFDB_Clear | CF → NIU | port pair의 DB 비우기 |
| 6 | N.MFDB_Create_Entry | CF → NIU | filter mode를 담아 엔트리 만들기 |
| 7 | N.MFDBNQ_Add | CF → NIU | NAME으로 거르는 엔트리 추가 |
| 64 / 65 | N.NT_Request / N.NT_Response | CF → NIU / NIU → CF | 포트별 SA 목록 요청과 응답 |
| 66 / 67 | N.NTX_Request / N.NTX_Response | CF → NIU / NIU → CF | 포트별 SA·NAME 목록 요청과 응답 |
| 128 / 129 | N.GP_Request / N.GP_Response | CF → NIU / NIU → CF | NIU 전체 parametric 요청과 응답 |
| 130 | N.GP_Reset_Statistics | CF → NIU | NIU 전체 통계 리셋 |
| 131 / 132 | N.SP_Request / N.SP_Response | CF → NIU / NIU → CF | port pair별 parametric 요청과 응답 |
| 133 | N.SP_Reset_Statistics | CF → NIU | port pair별 통계 리셋 |
| 192~195 | N.OC_Request·N.OC_Response(열기), N.CC_Request·N.CC_Response(닫기) | 요청은 CF → NIU, 응답은 NIU → CF | connection 열기와 닫기. 네 메시지에 192~195를 배정한 순서가 표준 안 두 곳에서 다르다(9절) |

### 포트 번호와 port pair 바이트

포트 번호는 니블(4비트) 하나다. 0은 local(메시지를 받은 그 포트), 1~14는 할당용, 15는 global(모든 포트)이다. local은 CF가 자기 쪽 포트 번호를 모를 때, global은 NIU의 포트 수를 모를 때 쓴다. port pair가 필요한 기능에서는 Byte 2의 상위 니블(bits 7~4)이 From, 하위 니블(bits 3~0)이 To다. 어느 한쪽이라도 global이면 NIU가 port pair마다 응답을 여러 개 보낼 수 있다.

ISO 11783-4는 이 대목에서 비트를 0부터 센다(가장 낮은 비트가 bit 0). 다른 장처럼 1부터 8까지 세면 상위 니블은 bits 8~5, 하위 니블은 bits 4~1이다. 어느 쪽으로 세든 가리키는 비트는 같다.

16진수 한 자리가 니블 하나이므로 port pair 바이트는 두 자리를 따로 읽으면 된다. 앞자리가 From, 뒷자리가 To다.

TECU는 포트 번호가 고정돼 있다. port 1이 작업기 버스, port 2가 트랙터 버스다(shall). 따라서 트랙터 → 작업기 방향은 `0x21`, 작업기 → 트랙터 방향은 `0x12`다.

::: warning 표준 문서의 예 하나는 방향을 반대로 적었다
ISO 11783-4에 실린 filter database 예는 "작업기로 가는 방향(port 1 → port 2)"이라며 port pair `0x12`를 쓰고, 그 방향에서 engine configuration(PGN 65251(0xFEE3))을 막고 있다고 해석한다. 그런데 TECU 포트 규칙(port 1 = 작업기, port 2 = 트랙터)과 같은 문서의 배치 그림(TECU의 P1이 작업기 쪽, P2가 트랙터 쪽)을 따르면 `0x12`는 작업기 → 트랙터 방향이다. 트랙터 데이터를 작업기 쪽으로 막는 필터라면 `0x21`이 맞다. 예가 포트 번호 규칙과 어긋나므로, TECU를 구현할 때는 포트 규칙을 따르고 진단 도구와 방향 해석을 맞춰야 한다.
:::

### 바이트 예제: TECU의 filter database 조회

표준 문서의 예를 프레임으로 옮긴다. 오프보드 진단 도구(SA 249 = `0xF9`)가 TECU(SA 240 = `0xF0`)에 filter database 사본을 요청한다.

```text
N.MFDB_Request   ID 0x18EDF0F9   00 12 FF FF FF FF FF FF
N.MFDB_Response  ID 0x18EDF9F0   01 12 00 E3 FE 00 FF FF
```

CAN ID부터 읽는다. `0x18EDF0F9`를 두 자리씩 나누면 `18`(우선순위 6이 들어 있는 앞부분), `ED`(PF 237, network message), `F0`(DA, 받는 쪽 TECU), `F9`(SA, 보내는 쪽 진단 도구)다. 응답 `0x18EDF9F0`은 DA와 SA가 서로 바뀌어 TECU가 진단 도구에게 보낸 것이다.

데이터 표 읽는 법: 바이트 번호는 1부터 센다. Byte 1이 데이터 필드의 첫 바이트다. PGN처럼 여러 바이트에 걸친 숫자는 낮은 자리 바이트가 먼저 온다(리틀 엔디언). 아래 표는 응답 프레임의 데이터다.

| 바이트 | 값 | 해석 |
|---|---|---|
| Byte 1 | `01` | function 1 = N.MFDB_Response |
| Byte 2 | `12` | From 1, To 2 |
| Byte 3 | `00` | filter mode 0 = block(기본은 전부 통과) |
| Byte 4~6 | `E3 FE 00` | PGN 엔트리 `0x00FEE3` = 65251. 데이터 필드 안의 PGN은 LSB부터 보낸다 |
| Byte 7~8 | `FF FF` | 채움 |

단계별로 읽으면 이렇다.

1. Byte 1 `01`: function code 1이므로 filter database 사본 응답이다.
2. Byte 2 `12`: 앞자리 1이 From, 뒷자리 2가 To다. port 1에서 port 2로 가는 방향의 표다.
3. Byte 3 `00`: block 모드다. 기본은 전부 통과이고, 표에 적힌 PGN만 막는다.
4. Byte 4~6 `E3 FE 00`: 낮은 자리부터 왔으므로 거꾸로 붙이면 `00 FE E3`, 즉 `0x00FEE3` = 65251(engine configuration, 엔진 구성 정보)이다.
5. Byte 7~8 `FF FF`: 엔트리가 더 없어서 채운 자리다.

이 방향에서는 engine configuration 하나만 막고 나머지는 모두 통과시킨다는 뜻이다.

아래 코드는 위 단계를 그대로 함수로 옮긴 것이다. CAN ID에서 PF가 `0xED`인지 확인하고, DA·SA·function·port pair·mode를 꺼낸 뒤 Byte 4부터 3바이트씩 PGN을 읽는다.

::: details 디코딩 검산 (Python)
```python
def decode_mfdb_response(can_id, data):
    assert (can_id >> 16) & 0xFF == 0xED
    pgns, i = [], 3
    while i + 3 <= len(data) and data[i:i + 3] != b"\xff\xff\xff":
        pgns.append(int.from_bytes(data[i:i + 3], "little"))
        i += 3
    return {
        "da": (can_id >> 8) & 0xFF, "sa": can_id & 0xFF,
        "function": data[0], "from": data[1] >> 4, "to": data[1] & 0x0F,
        "mode": data[2], "pgns": pgns,
    }

frame = decode_mfdb_response(0x18EDF9F0, bytes.fromhex("011200E3FE00FFFF"))
assert frame == {"da": 0xF9, "sa": 0xF0, "function": 1, "from": 1, "to": 2,
                 "mode": 0, "pgns": [65251]}
```
:::

마지막 `assert`가 통과하면 응답이 "TECU(`0xF0`)가 진단 도구(`0xF9`)에게, port 1 → 2 방향 block 모드 표에 PGN 65251 하나가 있다고 알렸다"로 해석된다는 뜻이다.

::: details 원문을 가진 독자를 위한 메모
- 위 경고의 예는 ISO 11783-4:2011 Table 5의 EXAMPLE이다. 포트 규칙의 근거는 ISO 11783-9:2012 4.1.2와 ISO 11783-4 Figure 1이다.
- network message의 정의는 Table 1(6.5.1), function code 목록은 Table 2(6.5.2), 포트 번호는 Table 3(6.5.3)에 있다.
:::

<small>근거: ISO 11783-4 6.5, ISO 11783-9 4.1.2, ISO 11783-3 5.1.3, 5.13.3</small>

## 6. filter database 읽고 고치기 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

5절에서 filter database를 읽는 법을 봤다. 이 절은 엔트리를 넣고 지우는 명령과, PGN에 더해 보낸 쪽 NAME으로 거르는 엔트리를 본다.

### 설정하는 방법과 명령 세 가지

filter database는 세 방법으로 설정할 수 있다.

1. 공급자가 고정 DB를 넣어 출고한다. 이후 네트워크 변경은 서비스 중 재설정 없이는 반영할 수 없다.
2. 서비스 절차에서 진단 도구로 설정한다.
3. 네트워크의 아무 CF나 언제든 설정한다. 보안 절차가 따로 필요할 수 있다.

DB 값은 전원이 꺼져도 남도록 비휘발성 메모리에 두는 것이 좋다. 전원 상실 때 지워지는 별도 동적 DB는 표준이 정의하지 않는다.

엔트리 하나는 PGN, 통과·차단 구분, port pair(방향)로 이루어진다. 명령 사이의 차이가 구현 함정이다.

| 명령 | code | filter mode 포함 | 규칙 |
|---|---|---|---|
| N.MFDB_Add | 2 | 없음 | 보내는 CF가 그 port pair의 filter mode를 미리 알아야 한다. mode는 그 port pair의 DB를 clear하고 다시 만들지 않으면 바꿀 수 없다 |
| N.MFDB_Delete | 3 | 없음 | 엔트리를 지운다 |
| N.MFDB_Clear | 4 | 없음 | 지정한 port pair·방향의 DB를 비운다 |
| N.MFDB_Create_Entry | 6 | 있음 | 포함된 mode로 기존 port pair의 mode를 바꿀 수 없다. clear되지 않은 DB에 보내면 오류를 돌려주는 것이 권장이다. 만든 CF의 NAME이 엔트리에 붙고 같은 NAME만 지울 수 있다(진단 도구용 예외 수단은 둔다) |

function code 5는 "폐기됨(Obsolete)"으로 비어 있다. 표준은 mode를 바꾸던 Set_Mode 명령을 없앴다고 적는데, 옛 판에서 이 명령이 5번이었던 것으로 보인다(추론). mode를 바꾸는 명령을 없애 한 DB에 서로 다른 mode의 엔트리가 섞일 여지를 없앤 것이다.

명령에 대한 확인은 Acknowledgement(PGN 59392(0xE800))로 온다. Acknowledgement는 요청을 받았는지 알려 주는 공용 메시지다([10장](/study/isobus/10-j1939-request-ack)). Byte 1이 control byte(0 ACK, 1 NACK, 2 Access Denied, 3 Cannot Respond), Byte 5가 요청자 주소, Byte 6~8이 확인 대상 PGN이다. ACK는 수락, NACK는 거절, Access Denied는 권한이 없어 거부, Cannot Respond는 지금 응답할 수 없다는 뜻이다. 진단 도구가 TECU의 트랙터 → 작업기 방향을 block 모드로 다시 만드는 순서는 다음과 같다.

```text
1) N.MFDB_Clear         ID 0x18EDF0F9  04 21 FF FF FF FF FF FF
   Acknowledgement      ID 0x18E8F9F0  00 xx FF FF F9 00 ED 00
2) N.MFDB_Create_Entry  ID 0x18EDF0F9  06 21 00 E3 FE 00 FF FF
   Acknowledgement      ID 0x18E8F9F0  00 xx FF FF F9 00 ED 00
3) 이후 엔트리 추가      N.MFDB_Add      02 21 + PGN 3바이트씩
```

1)의 `04 21`은 function 4(Clear)와 port pair `0x21`(트랙터 → 작업기)이다. 2)의 `06 21 00 E3 FE 00`은 Create_Entry, 같은 방향, mode 0(block), PGN 65251이다. 확인 프레임 `00 xx FF FF F9 00 ED 00`은 control byte 0(ACK), Byte 5 = 요청자 `F9`, Byte 6~8 = `00 ED 00`(거꾸로 붙이면 `0x00ED00` = 60672, network message)이다.

`xx`는 group function value 자리다. group function은 PGN 하나 안에서 Byte 1 같은 기능 번호로 여러 일을 나누는 방식이다([10장](/study/isobus/10-j1939-request-ack)). 데이터 링크 계층 규칙(ISO 11783-3)은 group function PG면 그 값을, 아니면 `FF`를 넣으라고 한다. 하지만 ISO 11783-4는 network message의 ACK에 function code를 넣을지 정하지 않는다. 수신 측은 Byte 1과 Byte 6~8로 판단하는 편이 안전하다(해석).

### NAME으로 거르는 엔트리: N.MFDBNQ_Add

function 7은 PGN에 더해 <strong>보낸 쪽 NAME</strong>으로 거르는 엔트리를 만든다. 요청자가 64비트 desired NAME(찾는 NAME)과 64비트 qualifier mask(비교할 비트를 고르는 마스크)를 주면, NIU가 자기 SA·NAME 표에서 그 정체성에 맞는 SA를 찾아 연결한다. mask 비트 1은 "NAME의 그 비트가 일치해야 함", 0은 "상관없음"이다. SA는 address claim으로 바뀔 수 있지만 NAME은 장치의 정체성이므로, NAME 기준 필터는 주소가 바뀌어도 의미를 유지한다(해석). PDU2 메시지(받는 쪽 없이 모두에게 보내는 메시지)와 global로 보낸 PDU1 메시지를 bridge 너머로 거르는 데 쓴다.

선택 기능으로 data rate reduction(넘겨 주는 속도 줄이기)이 있다. 원래 네트워크의 갱신 속도와 상관없이 넘겨 줄 최대 갱신 속도를 정하고, 넘길 때는 가장 최근 데이터를 써야 한다(shall). 예를 들어 100 ms(10회/s)로 오는 메시지를 서브버스에 2회/s로만 넘기려면 (t)를 2로 준다.

아래 표의 (t)(p)(d)(n)은 엔트리 하나를 이루는 네 칸의 이름이다.

| 바이트 | 내용 |
|---|---|
| 1 | function = 7 |
| 2 | port pair |
| 3 | filter mode |
| 4 | 예약 |
| (t) 5 | 최대 전송 속도: 0 예약, 1~250 초당 메시지 수, 251~254 ISO 용도, 255 제한 없음 |
| (p) 6~8 | PGN |
| (d) 9~16 | desired source NAME |
| (n) 17~24 | NAME qualifier mask |

(t)(p)(d)(n) 20바이트 묶음이 엔트리 수만큼 반복되므로 길이는 4 + 20k바이트다(k = 엔트리 수). 엔트리 하나만 넣어도 24바이트라 이 명령은 항상 TP로 간다. 주소 공간이 다른 세그먼트에서 넘겨줄 때는, open connection이 없으면 NIU 자신의 주소를, 있으면 virtual CF의 SA를 SA로 쓴다.

<small>근거: ISO 11783-4 6.6, Table 2, ISO 11783-3 5.4.5</small>

## 7. 토폴로지 조회와 상태 읽기 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

NIU에게 "건너편에 누가 있나"와 "지금 얼마나 바쁜가"를 묻는 메시지를 본다.

### 토폴로지 조회: N.NT와 N.NTX

이 표준을 따르는 NIU는 모두 transparent해야 하므로, CF는 보통 건너편에 누가 있는지 알 필요가 없다. 그런데 DB를 제대로 설정하려면 토폴로지를 알아야 할 수 있어서, 빠진 정보를 얻는 메시지가 따로 있다.

| 메시지 | code | 언제 | 비고 |
|---|---|---|---|
| N.NT_Request / Response | 64 / 65 | port pair가 <strong>같은 주소 공간</strong>일 때(bridge). 어느 포트가 어느 세그먼트인지 알아낸다 | 신규 설계 비권장 |
| N.NTX_Request / Response | 66 / 67 | 조회할 세그먼트가 <strong>다른 주소 공간</strong>일 때(router). 요청자는 그쪽 address claim을 본 적이 없다 | global 포트로는 요청할 수 없다(0~14만) |

N.NTX_Response는 Byte 3에 쌍의 개수 n을 두고, 그 뒤로 SA 1바이트 + NAME 8바이트 = 9바이트 묶음을 n번 싣는다. 길이가 3 + 9n바이트라 CF가 하나만 있어도 12바이트로 TP가 필요하다. 응답에는 <strong>그 세그먼트에서 NIU 자신이 claim한 주소와 NAME도</strong> 들어간다(9절 connection 규칙 11과 같은 내용이다).

NIU가 여러 개면 응답 하나로는 어떤 SA가 어느 로컬 세그먼트에 있는지 확정할 수 없다. 그 SA가 원격 세그먼트에 있을 수 있으므로 NIU마다의 응답을 비교해 판별해야 한다. NIU는 먼저 request for address claim(모두에게 address claim을 다시 보내 달라는 요청)을 보내 포트별 SA 목록을 만든다(shall). 이때 응답 대기 시간으로 300 ms(NIU 1단 지연 + CF 응답 시간)를 쓴다.

### Parametrics: NIU 상태·통계 읽기

NIU 전체에 적용되는 값은 general parametric(code 128~130)으로, 특정 port pair의 값은 specific parametric(code 131~133, Byte 2에 port pair)으로 읽는다. parametric마다 1바이트 번호가 붙어 있다. 번호와 뜻은 다음과 같다.

| 번호 | 뜻 | 길이 | 리셋 |
|---|---|---|---|
| 0 | 전체 목록을 번호 순으로 요청할 때 쓰는 번호(응답에는 없다) | - | - |
| 1 | 버퍼 크기(바이트) | 2바이트 | |
| 2 | filter database 최대 크기(바이트) | 2바이트 | |
| 3 | filter database 엔트리 수 | 2바이트 | |
| 4 | 초당 최대 수신 메시지 수 | 2바이트 | |
| 5 | 초당 최대 forwarding 메시지 수 | 2바이트 | |
| 6 | 초당 최대 filtering 메시지 수 | 2바이트 | |
| 7 | 최대 transit delay(ms) | 2바이트 | |
| 8 | 평균 transit delay(ms) | 2바이트 | 가능 |
| 9 | 버퍼가 넘쳐 잃은 메시지 수 | 2바이트 | 가능 |
| 10 | transit delay를 넘긴 메시지 수 | 2바이트 | 가능 |
| 11 | 초당 평균 수신 메시지 수 | 2바이트 | 가능 |
| 12 | 초당 평균 forwarding 메시지 수 | 2바이트 | 가능 |
| 13 | 초당 평균 filtering 메시지 수 | 2바이트 | 가능 |
| 14 | 마지막 power-on reset 이후 가동 시간(s) | 4바이트 | |
| 15 | 포트 수(2~14) | 1바이트 | |
| 16 | NIU Type(4절 표의 값) | 1바이트 | |

규칙은 다음과 같다.

- 요청에 parametric 식별자(각 1바이트)를 오름차순으로 나열한다. 응답은 요청 순서대로 값을 담고, 길이가 고정이라 구분자가 없다.
- 한 주소에는 응답을 받은 뒤에 다음 요청을 보낸다. 요청 하나에 여러 parametric을 물을 수는 있다.
- <strong>parametric 0으로 요청하는 것이 권장</strong>이다. 전체 목록이 번호 순으로 온다.
- 응답 목록이 기대보다 짧으면 NIU가 목록에 나중에 추가된 항목을 모르고 아는 데까지만 보냈다는 뜻이다.
- 통계 리셋(code 130, 133)은 리셋 가능 항목(8~13)만 지우고 PGN 59392로 확인한다.

값의 길이는 parametric 1~13이 2바이트, 14(마지막 power-on reset 이후 uptime, 초)가 4바이트, 15(포트 수, 2~14)와 16(NIU Type)이 1바이트다. 2바이트 범위 0~64 255와 4바이트 범위 0~4 211 081 215가 어중간해 보이는 이유는 ISO 11783-7이 정한 유효 신호 범위(`0xFAFF`, `0xFAFFFFFF`)를 따르기 때문이다. 그 위 값은 오류·not available(값을 줄 수 없음) 표시로 예약돼 있다([23장](/study/isobus/23-implement-messages-basics)). 바이트 순서도 같은 규칙대로 LSB(가장 낮은 자리 바이트)가 먼저다. parametric 14는 이전 판(2001)과 정의가 달라져 SAE J1939-31(J1939의 네트워크 계층 문서)과 맞춘 항목이다.

아래는 parametric 7과 16을 묻는 요청과 그 응답이다.

```text
N.GP_Request   80 07 10 FF FF FF FF FF    parametric 7, 16 요청
N.GP_Response  81 0A 00 05 FF FF FF FF    7 = 0x000A → 최대 transit delay 10 ms, 16 = 5 → Tractor ECU
```

요청 `80 07 10`은 function 128(`0x80`, N.GP_Request), parametric 7, parametric 16(`0x10`)이다. 응답은 function 129(`0x81`) 뒤에 parametric 7의 2바이트 값 `0A 00`(낮은 자리 먼저, `0x000A` = 10 ms)과 parametric 16의 1바이트 값 `05`(Tractor ECU)가 요청 순서대로 붙는다. 나머지 `FF`는 채움이다.

parametric 0으로 전체를 요청하면 응답 길이는 1 + 13×2 + 4 + 1 + 1 = 33바이트이고(specific은 port pair 1바이트가 더해져 34바이트) TP로 온다.

아래 코드는 parametric 번호별 길이 표(`SIZES`)로 응답을 차례로 잘라 읽는 파서다. 위 응답을 넣어 `{7: 10, 16: 5}`가 나오는지, 전체 응답 길이가 33바이트인지, 유효 범위 상한이 10진수로 얼마인지 확인한다.

::: details parametric 응답 파서 검산 (Python)
```python
SIZES = {**{pid: 2 for pid in range(1, 14)}, 14: 4, 15: 1, 16: 1}

def parse_parametrics(payload, ids, start=1):
    values, i = {}, start
    for pid in ids:
        size = SIZES[pid]
        if i + size > len(payload):
            break
        values[pid] = int.from_bytes(payload[i:i + size], "little")
        i += size
    return values

response = bytes.fromhex("810A0005FFFFFFFF")
assert parse_parametrics(response, [7, 16]) == {7: 10, 16: 5}
assert 1 + sum(SIZES.values()) == 33
assert (0xFAFF, 0xFAFFFFFF) == (64255, 4211081215)
```
:::

`if i + size > len(payload): break`가 "응답이 기대보다 짧으면 아는 데까지만 읽는다"는 규칙을 그대로 옮긴 줄이다.

<small>근거: ISO 11783-4 6.7, 6.8, Table 6, Table 7, ISO 11783-7 3.3.1, 3.3.3</small>

## 8. Connection과 virtual CF: 건너편 CF에게 말 걸기

router 너머의 CF는 address claim이 넘어오지 않아 보이지 않는다. 이 절은 그런 CF와 대화하는 방법인 connection을 본다. NIU가 각 세그먼트에 상대의 대역(virtual CF)을 세워 두어, 양쪽 CF가 마치 같은 세그먼트에 있는 것처럼 대화하게 해 주는 방식이다.

### 왜 connection이 필요한가

gateway나 router로 작업기 서브네트워크를 붙이면, 서브네트워크는 메인 작업기 네트워크와 <strong>분리된 주소 공간</strong>을 가진다. 그곳에는 센서·액추에이터·저성능 컨트롤러처럼 메인 세그먼트와 통신이 적은 CF가 놓인다. 그래도 서비스 도구가 한 연결점에서 여러 세그먼트를 진단하거나, 소프트웨어·캘리브레이션을 내려받거나, 서브네트워크의 CF가 메인 네트워크의 VT(Virtual Terminal, 운전석 화면 장치)와 대화해야 할 때가 있다.

전형적 router는 address translation DB로 이 문제를 푼다. ISO 11783-4는 다른 방법도 정의한다. CF가 발견한 토폴로지와 NAME을 근거로 NIU에 <strong>connection</strong>을 동적으로 여는 router다. connection이 열리면 NIU가 메시지 전달을 알아서 처리하므로, 참여 CF는 초기 토폴로지 발견과 connection 열기 외에는 기존 단일·멀티패킷 destination-specific(받는 쪽을 지정한) 메시지 코드를 바꿀 필요가 없다.

### 연결 수립 순서

![NIU connection 수립: CF A가 N.NTX로 network 2의 NAME 목록을 얻고 N.OC_Request로 CF C와의 connection을 요청하면, NIU가 network 1에 virtual CF C^, network 2에 A^를 claim하고 이후 요청과 응답의 주소를 바꿔 전달한다](/images/study-isobus/13-niu-connection-light.png)
![NIU connection 수립: CF A가 N.NTX로 network 2의 NAME 목록을 얻고 N.OC_Request로 CF C와의 connection을 요청하면, NIU가 network 1에 virtual CF C^, network 2에 A^를 claim하고 이후 요청과 응답의 주소를 바꿔 전달한다](/images/study-isobus/13-niu-connection-dark.png)

그림의 주소는 예시 값이다. 이름 뒤의 `^`는 "NIU가 세운 대역"이라는 표시다. C^는 network 1에 세운 C의 대역, A^는 network 2에 세운 A의 대역이다.

1. CF A가 NIU B에 N.NTX_Request를 보내 network 2의 NAME 목록을 받는다. 목록에는 NIU B 자신과 C, D가 있다.
2. A가 C의 NAME을 담아 N.OC_Request를 보낸다.
3. NIU B는 전달 정보를 기록하고, network 1에 C의 NAME으로 주소를 claim해 virtual CF <strong>C^</strong>를 만든다. 이 주소는 C가 network 2에서 쓰는 주소와 같을 필요가 없고, network 1에서 비어 있는 self-configurable 주소 중에서 고른다.
4. NIU B는 network 2에도 A의 NAME으로 <strong>A^</strong>를 claim한다.
5. A는 C^의 address claim이 성공한 것을 보고, 자기 세그먼트의 여느 CF에게 하듯 C^로 destination-specific 메시지를 보낸다.
6. NIU B는 DA가 C^인 메시지를 받으면 network 2에 SA = A^, DA = C로 바꿔 다시 보낸다.
7. C는 A^가 보낸 메시지로 받아 평소대로 처리한다. 보안 접근 권한 평가, 하드웨어 동작, 응답·ACK·NACK이 모두 평소와 같다.

self-configurable 주소는 주소를 스스로 골라 claim할 수 있는 CF가 쓰는 128~247 범위다([12장](/study/isobus/12-j1939-address-name)). 그림의 응답 DM2(PGN 65227(0xFECB))는 이전에 생겼던 고장 코드를 알려 주는 진단 메시지다([28장](/study/isobus/28-diagnostics-dm-fmi)). DM2는 PF가 254인 PDU2 메시지라 DA가 없어 그림에 SA만 표시했다. N.OC_Response와 C^ claim의 선후는 표준이 정하지 않는다. A는 C^의 claim 성공을 확인한 뒤에 보내기 시작한다.

### 여러 connection 다루기

connection을 연 CF는, 다른 CF가 그 connection을 붙들고 있지 않으면 닫을 수 있다. 한 CF가 같은 connection을 여러 번 열어도 connection은 하나로 치고 close 한 번으로 닫힌다. 다중 connection은 이렇게 다룬다.

- A가 network 2의 D에도 연결하면 이미 있는 A^를 재사용하고 network 1에 D^만 새로 claim한다.
- network 1의 다른 CF F가 connection 없이 C^로 보내면 Access Denied로 거절된다. F가 C와 connection을 열면 network 2에 F^가 생기고 network 1의 C^는 재사용된다.
- 이미 claim된 주소는 connection을 추가로 열 때 다시 claim하지 않는다.
- 이 과정을 되풀이하면 network 2에 있는 또 다른 NIU 너머까지, 네트워크의 가장 먼 세그먼트까지 찾아갈 수 있다. 예를 들어 network 3의 G는 network 2에 G^로, 다시 network 1에 G^^로 나타나고, A는 network 3에 A^^로 나타난다. `^`가 하나 늘 때마다 NIU를 하나 더 건넌 대역이다.

<small>근거: ISO 11783-4 6.9.1~6.9.3, Figure 4, Figure 5, ISO 11783-12 B.7, ISO 11783-5 4.2.3</small>

## 9. Connection 규칙과 메시지 바이트 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

connection을 구현하는 NIU가 지켜야 할 규칙, connection 없이 말을 건 CF를 거절하는 프레임, connection 메시지의 바이트 배치를 본다.

### NIU가 지켜야 할 connection 규칙

| 주제 | 규칙 | 번호 |
|---|---|---|
| 수명 | 한 번 열린 connection은 현재 power cycle 동안, 또는 연 CF가 닫을 때까지 유지된다 | 1 |
| TP | TP가 필요한 메시지도 보낼 수 있다. NIU는 TP 세션 타이밍을 지킬 만큼 작은 지연으로 재전송한다(shall) | 2 |
| 개수·주소 범위 | NIU의 유지 능력과 세그먼트당 253개 CF 주소로만 제한된다. virtual CF에 쓸 self-configurable 주소는 128~247뿐이다 | 3 |
| virtual SA | virtual CF는 원본과 같은 NAME을 쓰되 SA는 같아도 달라도 된다 | 4 |
| 주소 변경 | 참여 CF의 주소가 어떤 이유로든 바뀌면 NIU가 추적해 connection 정보를 갱신한다 | 5 |
| NAME 변경 | 참여 CF가 NAME을 조금이라도 바꾸려면 먼저 자기 connection을 모두 닫는다. 안 닫으면 NIU가 예측 불가능하게 동작할 수 있다. 새 NAME·주소로 다시 연다 | 6 |
| claim 재송신 | 참여 CF가 address claim을 다시 보내면 NIU도 virtual CF 쪽 서브네트워크에 그 주소로 claim을 보낸다 | 7 |
| cannot claim | 참여 CF가 주소를 못 얻어 CANNOT claim을 보내면 NIU는 connection을 닫고 virtual 쪽에도 CANNOT claim을 보낸다 | 8 |
| 유일성 | 한 세그먼트에 한 CF의 virtual 표현은 하나뿐이다. 그 virtual CF가 여러 connection에 걸릴 수는 있다 | 9 |
| 해제 | connection을 닫아도 virtual CF는 바로 사라지지 않는다. 걸린 connection이 모두 닫힐 때까지 남는다 | 10 |
| 보고 | 다른 세그먼트의 NAME·주소 표를 보고할 때 그 세그먼트에서의 NIU 자신도 넣는다 | 11 |

규칙 3의 128~247은 8절에서 본 self-configurable 주소 범위와 같다. 규칙 2는 TP 타이머(Tr = 200 ms, T1 = 750 ms 등, [16장](/study/isobus/16-tp-connection-rules))에 NIU 지연을 얹어도 넘지 않아야 한다는 뜻이다. power cycle은 전원이 켜져서 꺼질 때까지의 한 주기다.

### 거절 프레임: Access Denied

virtual CF는 다른 CF에게 보통 CF처럼 보이므로, connection을 열지 않은 actual CF도 말을 걸 수 있다. NIU는 그 virtual CF에 대한 open connection이 없는 CF가 보낸 메시지를 NACK해야 한다(shall). Acknowledgement의 control byte는 2(Access Denied)이고, Address Acknowledged(ADD_NACK) 자리에 virtual CF의 주소를 넣는다.

F(`0x88`=136)가 connection 없이 C^(`0x90`=144)에 DM2를 요청한 경우다.

```text
F → C^   Request(PGN 59904)  ID 0x18EA9088   CB FE 00
C^ → F   Acknowledgement     ID 0x18E88890   02 FF FF FF 90 CB FE 00
```

Request(PGN 59904)는 다른 CF에게 어떤 PGN을 보내 달라고 요청하는 메시지다([10장](/study/isobus/10-j1939-request-ack)). Request는 데이터 길이(DLC) 3바이트에 요청 PGN 65227을 LSB부터 싣는다. `CB FE 00`을 거꾸로 붙이면 `0x00FECB` = 65227이다. 거절 프레임은 control byte `02`(Access Denied), Byte 5 `90`(virtual CF C^의 주소), Byte 6~8 `CB FE 00`(거절된 PGN)이다. 거절 프레임을 NIU가 어떤 SA로 보내는지는 표준에 없어 virtual CF 주소로 가정했다.

::: warning Byte 5에 넣는 주소가 두 규칙에서 다르다
데이터 링크 계층 규칙(ISO 11783-3)은 Acknowledgement의 Byte 5에 <strong>요청을 보낸 CF의 주소</strong>(PS 필드의 복사)를 넣는다고 정한다. 위 예라면 `0x88`이다. connection 규칙(ISO 11783-4)은 같은 자리에 <strong>virtual CF의 주소</strong>(`0x90`)를 넣으라고 한다. 수신 측은 Byte 5만 보고 판단하지 말고 control byte와 Byte 6~8의 PGN으로 어떤 요청이 거절됐는지 가려야 한다(해석).
:::

### Connection 메시지 바이트

| 메시지 | 길이 | Byte 2(port pair) | 나머지 |
|---|---|---|---|
| N.OC_Request(열기 요청) | 10바이트, TP | To = 대상 CF 쪽 포트, From = 요청자 쪽 포트(local 0 권장) | Byte 3~10 = 연결할 CF의 NAME |
| N.CC_Request(닫기 요청) | 10바이트, TP | 위와 같다 | Byte 3~10 = 끊을 CF의 NAME. 연 CF만, 열 때와 같은 NAME으로 닫는다 |
| N.OC_Response / N.CC_Response | 8바이트 | To = 요청자 쪽(local 0), From = 대상 쪽 | Byte 3 bits 1~2 = 성공 01·실패 00, Byte 4 = 실패 사유, Byte 5~8 = `FF` |

실패 사유 코드는 0(그 NAME의 CF 없음), 1(그 NAME의 connection 수 초과), 2(NIU의 connection 수 초과), 3(Busy), 4(지원하지 않는 요청), 255(Not available)이다. 요청 CF는 N.NTX_Request로 대상 세그먼트의 CF를 먼저 파악해 고르는 것이 좋다. 이미 활성인 connection과 정확히 같은 열기 요청이 오면 응답은 평소대로 보내고 상태는 바꾸지 않는다.

예를 들어 network 2가 포트 2에 붙어 있으면 N.OC_Request는 `C0 02` 뒤에 C의 NAME 8바이트가 붙고, 10바이트라 TP.DT 2개(7바이트씩)로 간다. `C0`은 192(열기 요청), `02`는 From 0(local, 요청자 쪽)과 To 2(대상 쪽)다. 응답은 `C2 20 01 FF FF FF FF FF` 꼴이 된다. `C2`는 194, `20`은 From 2(대상 쪽)와 To 0(요청자 쪽), `01`은 성공이다. 코드 194는 connection 메시지를 하나씩 정의한 부분의 번호 배정을 따랐고(아래 경고 참고), 성공일 때 Byte 4 값은 표준이 정하지 않아 255로 가정했다.

::: warning function code가 두 곳에서 다르다
표준 문서 안에서 connection 메시지의 번호가 두 곳에서 다르게 적혀 있다. function code 목록 표는 192 열기 요청, 193 열기 응답, 194 닫기 요청, 195 닫기 응답이다. 메시지를 하나씩 정의한 부분은 192 N.OC_Request, 193 N.CC_Request, 194 N.OC_Response, 195 N.CC_Response다. 193과 194의 뜻이 서로 바뀌어 있다. 견고하게 받으려면 방향(CF → NIU면 요청, NIU → CF면 응답)과 길이(10바이트면 요청, 8바이트면 응답)로 먼저 가르는 방법이 있다(해석). Byte 3도 예약 비트(3~8)를 어떻게 채울지 표준이 정하지 않으므로, ISO 11783-7 관례대로 1로 채우면 성공이 `FD`가 된다. 비교는 `status & 0x03`으로 한다.
:::

::: details 원문을 가진 독자를 위한 메모
- function code 목록 표는 ISO 11783-4:2011 Table 2(6.5.2)이고, 메시지를 하나씩 정의한 부분은 6.9.5.1~6.9.5.4다. 6.9.5.2가 N.CC_Request(193), 6.9.5.3이 N.OC_Response(194)라서 Table 2와 엇갈린다. 위 응답 예의 194는 6.9.5.3 기준이다.
- Acknowledgement의 Byte 5 규칙은 ISO 11783-3:2018 5.4.5, Access Denied 때 virtual CF 주소를 넣으라는 규칙은 ISO 11783-4 6.9.4다.
- 2절에서 본 "주소 254개"는 5.3, "세그먼트당 253개"는 6.9.4 3)이다.
:::

<small>근거: ISO 11783-4 6.9.4, 6.9.5, Table 2, ISO 11783-3 5.4.3, 5.4.5, 5.13.3, ISO 11783-5 4.2.3</small>

::: tip 핵심 정리
- NIU는 나뉜 세그먼트를 잇는 검문소다. 하는 일은 전달, 거르기, 주소 변환, 재포장 네 가지이고, repeater, bridge, router, gateway 순으로 하나씩 늘어난다.
- repeater와 bridge는 원래 SA를 그대로 넘겨 주소 공간을 공유하고, router와 gateway는 주소 공간을 나눈다. router 너머로는 address claim이 넘어가지 않는다.
- NIU는 (우선순위, 받은 순번) 순서로 메시지를 넘긴다. 단순 FIFO는 금지다.
- NIU 설정과 조회는 network message(PGN 60672) 하나로 한다. Byte 1 function code가 할 일을, Byte 2 port pair가 방향을 정한다. TECU는 port 1이 작업기, port 2가 트랙터다.
- 다른 주소 공간의 CF와 대화하려면 N.NTX로 NAME을 찾고 N.OC로 connection을 연다. NIU가 양쪽에 virtual CF를 세워 주소를 바꿔 전달한다.
:::

::: details 확인 문제
1. (개념) 검문소 비유로 bridge와 router의 차이를 한 문장씩 말하라. 둘 중 address claim이 건너편 세그먼트에 그대로 보이는 쪽은 어느 것인가?
2. (개념) NIU의 큐에 우선순위 7인 TP.DT 세 개가 기다리는데 우선순위 3인 Lighting command가 들어왔다. FIFO 큐라면, 그리고 표준이 요구하는 큐라면 Lighting command는 각각 몇 번째로 나가는가?
3. (순서) 메인 작업기 버스의 진단 도구가 router 너머 서브네트워크에 있는 CF C에게 DM2를 요청하려 한다. 어떤 메시지를 어떤 순서로 보내야 하는가?
4. (디코딩) 진단 도구(SA `0xF9`)가 `ID 0x18EDF9F0`, 데이터 `01 21 00 E3 FE 00 FF FF`를 받았다. 어떤 NIU의 무엇을 알려 주는 응답이며, TECU 포트 규칙으로 보면 어느 방향의 필터인가?

**답 가이드**
1. bridge는 통행 목록(filter database)을 보고 골라 통과시키지만 번호판(SA)은 그대로 둔다. router는 번호판을 건너편 체계에 맞게 바꿔 단다. bridge는 주소 공간을 공유하므로 address claim이 양쪽에 다 보이고, router는 address claim을 넘기지 않는다.
2. FIFO 큐라면 앞의 TP.DT 세 개가 다 나간 뒤 네 번째로 나간다. 표준이 요구하는 큐라면 우선순위가 가장 높으므로(숫자 3이 7보다 작다) 첫 번째로 나가고, 그 뒤 TP.DT #1, #2, #3이 받은 순서대로 나간다.
3. 먼저 NIU에 N.NTX_Request를 보내 서브네트워크의 SA·NAME 목록을 받는다. 목록에서 C의 NAME을 골라 N.OC_Request로 connection을 연다. NIU가 메인 버스에 C의 대역 C^를, 서브네트워크에 진단 도구의 대역을 claim하면, 진단 도구는 C^에게 평소처럼 Request(DM2)를 보낸다. NIU는 SA를 진단 도구의 대역 주소로, DA를 C로 바꿔 전달하고, C가 보낸 DM2는 메인 버스에서 C^의 SA로 나타난다. connection 없이 C^에게 바로 보내면 Access Denied로 거절된다.
4. PF `0xED`라 network message(PGN 60672)이고, SA `0xF0`의 NIU가 DA `0xF9`에 보냈다. Byte 1 = 1은 N.MFDB_Response, Byte 2 = `0x21`은 From 2 → To 1, Byte 3 = 0은 block 모드(기본 전부 통과), 엔트리 `E3 FE 00`은 PGN 65251(engine configuration)이다. TECU라면 port 2가 트랙터 버스, port 1이 작업기 버스이므로 트랙터 → 작업기 방향에서 engine configuration만 막는 필터다.
:::

## 다음 챕터

- 다음: [22장 트랙터 ECU: 클래스, 조명, 전원, Safe mode](/study/isobus/22-tractor-ecu)
