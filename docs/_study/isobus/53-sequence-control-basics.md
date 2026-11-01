---
title: "Sequence Control(SC) 기초"
description: "ISO 11783-14 Sequence Control이 운전자의 반복 조작을 기록했다가 버튼 하나로 재생하는 방식과 SCM·SCC의 역할, 메시지 구조, 상태 머신, 초기화 순서를 익힌다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, SequenceControl, Headland]
prev: /study/isobus/52-file-server-details
next: /study/isobus/54-sequence-control-details
---

# Sequence Control(SC) 기초

::: info 학습 목표
- Sequence Control이 운전자의 조작을 기록했다가 재생하는 기능이라는 것을 헤드랜드 회전 예로 설명할 수 있다.
- SCM(관리자)과 SCC(참여자)가 각각 무엇을 맡고, 어떤 메시지로 이야기하는지 설명할 수 있다.
- SC에는 PGN이 두 개뿐이고 메시지 종류는 첫 바이트의 메시지 코드로 가른다는 것, SCD와 TAN이 왜 필요한지 설명할 수 있다.
- SCM·SCC 상태 그림을 보고 어떤 일이 생기면 어느 상태로 가는지 읽을 수 있다.
- SCC가 SCM에 합류하는 초기화 순서(능력 확인 → 저장된 SCD 확인 → 업로드 또는 로드 → 활성화 → Enabled)를 차례대로 말할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [26장 ISOBUS 네트워크 관리와 Working Set](/study/isobus/26-isobus-network-mgmt), [29장 Virtual Terminal(VT) 기초](/study/isobus/29-vt-basics), [10장 요청과 응답](/study/isobus/10-j1939-request-ack)
- 이 장에서 처음 나오는 말
  - 헤드랜드(headland): 밭 양 끝에서 기계가 돌아 나가는 띠 모양의 구역이다. 여기서 회전할 때마다 같은 조작을 되풀이한다.
  - SCM(Sequence Control Master): 조작 순서를 기록하고 재생하는 관리자 역할의 장치다.
  - SCC(Sequence Control Client): 히치, PTO, 밸브처럼 실제로 움직이는 기능을 가진 참여자 장치다.
  - 시퀀스(sequence): 기록해 둔 조작들의 순서 묶음이다. 표준은 SCS(Sequence Control Sequence)라고 부른다.
  - SCD(Sequence Control Data): SCC가 "나는 이런 기능을 기록할 수 있다"고 SCM에 건네는 자기소개 자료다.
  - TAN(Transaction Number): 명령과 응답을 짝 맞추는 번호표다.
:::

트랙터로 밭에서 일하다 보면 밭 끝(헤드랜드)에 닿을 때마다 같은 동작을 되풀이한다. 살포를 멈추고, PTO(Power Take-Off, 트랙터 엔진의 회전력을 작업기로 넘겨 주는 축)를 끄고, 작업기를 들어 올린 뒤 돌아서고, 다시 작업기를 내리고 PTO를 켠다. Sequence Control(SC)은 이 동작들을 한 번 녹화해 두었다가 다음 헤드랜드부터는 버튼 하나로 똑같이 재생하게 해 주는 ISOBUS 기능이다. 컴퓨터의 매크로 녹화처럼, 사람이 한 조작을 순서와 간격까지 기억했다가 그대로 되풀이한다.

![첫 헤드랜드에서 운전자가 한 조작을 기록하고, 다음 헤드랜드부터 버튼 하나로 같은 순서와 간격으로 재생하는 모습](/images/study-isobus/53-headland-record-playback-light.png)
![첫 헤드랜드에서 운전자가 한 조작을 기록하고, 다음 헤드랜드부터 버튼 하나로 같은 순서와 간격으로 재생하는 모습](/images/study-isobus/53-headland-record-playback-dark.png)

## 1. Sequence Control이 푸는 문제: 기록했다가 재생한다

이 절에서는 SC가 무엇을 자동으로 해 주는지, 그 일을 어떤 장치들이 나눠 맡는지 본다.

헤드랜드에서 하는 조작은 매번 같지만 순서와 타이밍을 지켜야 한다. 살포를 너무 늦게 끄면 이미 뿌린 자리에 또 뿌리고, 작업기를 너무 일찍 내리면 회전하는 자리까지 땅을 갈게 된다. 운전자는 회전하면서 핸들도 돌려야 하니 실수하기 쉽다. SC는 이 반복 조작을 기계에 맡긴다.

<strong>Sequence Control(SC)</strong>은 ISO 11783-14(Sequence Control을 정하는 표준 문서)가 정한 기능으로, 운전자가 반복하는 일련의 조작을 <strong>한 번 기록해 두고, 이후 명령 한 번으로 재생</strong>한다. GPS 같은 외부 센서가 시퀀스를 알아서 실행하는 방식이 아니다. 운전자의 수동 조작을 기록(record)했다가, 운전자가 재생(play back)을 지시하면 그대로 되풀이하는 방식이다. 표준에서는 운전자를 오퍼레이터(operator)라고 부르는데, 이 장에서는 운전자로 쓴다.

가장 대표적인 활용이 <strong>헤드랜드 관리(Headland Management)</strong>다. 헤드랜드에서 회전할 때마다 반복하는 조작(살포 중지, PTO 정지, 작업기 상승, 회전 뒤 하강, 살포 재개)을 한 번 기록해 두면, 이후 헤드랜드에 닿을 때마다 운전자가 버튼 하나로 전체 시퀀스를 재생할 수 있다. 표준은 밭 가운데의 물길을 건널 때처럼 같은 조작을 되풀이하는 다른 장면도 예로 든다.

시스템은 두 가지 역할로 이루어진다. 오케스트라에 빗대면 SCM은 지휘자, SCC는 악기를 맡은 단원이다. 지휘자는 악보(기록된 시퀀스)를 들고 박자에 맞춰 신호를 주고, 단원은 신호를 받아 자기 악기를 연주한다.

| 역할 | 이름 | 맡는 일 |
|------|------|------|
| 관리자(마스터) | <strong>SCM</strong>(Sequence Control Master) | 기록과 재생을 이끈다. 기록 중에는 SCC가 알려 온 조작을 trigger(언제 실행할지 정하는 기준) 정보와 함께 저장하고, 재생 중에는 trigger point(그 기준으로 정한 실행 시점)에 이르면 그 조작을 SCC에 명령한다 |
| 참여자(클라이언트) | <strong>SCC</strong>(Sequence Control Client) | PTO, 히치, 밸브처럼 기록할 수 있는 기능(표준은 client function이라고 부른다)을 가진 ECU다. 기록 중에는 운전자의 조작을 SCM에 알리고, 재생 중에는 SCM의 명령을 운전자가 손으로 조작한 것과 같은 방식으로 실행한다 |

![SCM은 관리자로서 재생 때 SCC에 실행 명령을 보내고, 트랙터 ECU와 작업기 ECU 같은 SCC는 기록 때 조작을 SCM에 알린다. SCC끼리는 직접 통신하지 않는다](/images/study-isobus/53-sc-roles-light.png)
![SCM은 관리자로서 재생 때 SCC에 실행 명령을 보내고, 트랙터 ECU와 작업기 ECU 같은 SCC는 기록 때 조작을 SCM에 알린다. SCC끼리는 직접 통신하지 않는다](/images/study-isobus/53-sc-roles-dark.png)

몇 가지 규칙이 이 관계를 정한다.

- 한 네트워크에서 실제로 일하는(active) SCM은 동시에 하나뿐이다. 지휘자가 둘이면 단원이 누구를 따를지 모르기 때문이다.
- 트랙터는 SCC가 될 수도, SCM이 될 수도, 둘 다가 될 수도 있다. 트랙터 ECU가 자기 히치와 PTO를 가진 SCC이면서 동시에 SCM 역할을 맡는 식이다.
- SCC들은 서로 독립적이다. SCC끼리 직접 주고받는 메시지는 없고, 모든 대화는 SCM을 거친다.

<small>근거: ISO 11783-14 3.11, 3.14, 4.1</small>

## 2. 기록과 재생의 흐름, 그리고 두 장치의 상태

이 절에서는 기록 한 번과 재생 한 번이 어떤 순서로 흘러가는지 보고, 그 과정에서 SCM과 SCC가 어떤 상태를 거치는지 이름부터 익힌다.

![기록 단계에서 운전자의 조작이 SCC의 알림을 거쳐 SCM에 스텝으로 저장되고, 재생 단계에서 SCM의 실행 명령과 SCC의 상태 보고가 시퀀스가 끝날 때까지 되풀이되는 흐름](/images/study-isobus/53-sc-flow-light.png)
![기록 단계에서 운전자의 조작이 SCC의 알림을 거쳐 SCM에 스텝으로 저장되고, 재생 단계에서 SCM의 실행 명령과 SCC의 상태 보고가 시퀀스가 끝날 때까지 되풀이되는 흐름](/images/study-isobus/53-sc-flow-dark.png)

그림의 흐름을 순서대로 읽으면 다음과 같다.

<strong>기록</strong>
1. 운전자가 기록을 시작하면 SCM의 상태가 Recording(기록 중)으로 바뀌고, SCC들이 이 상태를 따라간다.
2. 운전자는 평소처럼 살포 중지, PTO 정지, 작업기 상승을 조작한다.
3. 조작할 때마다 SCC가 SCExecutionIndication(실행 알림) 메시지를 보낸다. 이 메시지에는 어떤 기능(기능 ID)을 어떤 상태(상태 ID)로 바꿨는지, 실행이 어디까지 왔는지(실행 상태)가 담긴다.
4. SCM은 알림을 trigger point와 함께 한 스텝으로 저장한다.
5. 운전자가 기록을 멈출 때까지 2~4를 되풀이한다. 기록을 멈추면 시퀀스가 저장되고 SCM은 Ready(대기)로 돌아간다.

<strong>재생</strong>
1. 헤드랜드에 닿아 운전자가 재생을 시작한다.
2. SCM은 스텝마다 trigger point에 이르면 SCMasterExecutionCommand(실행 명령)를 보낸다.
3. SCC는 기능을 실행하고 SCClientExecutionStatus(실행 상태 보고)로 시작과 완료를 알린다.
4. 시퀀스가 끝날 때까지 2~3을 되풀이하고, 끝나면 SCM은 Ready로 돌아간다.

각 스텝의 <strong>trigger</strong>는 시간 기반(두 기능 활성화 사이의 시간)이나 거리 기반(두 기능 활성화 사이의 주행 거리)으로 저장된다. 예를 들어 시간 기반이면 "살포를 끄고 1.5초 뒤 PTO를 끈다", 거리 기반이면 "살포를 끄고 4 m 더 간 뒤 PTO를 끈다"는 식이다. 거리 기반이면 재생할 때 트랙터가 더 빨리 달려도 같은 자리에서 동작한다.

재생 중 문제가 생기면 어떤 SCC든 <strong>SCClientAbort</strong>(재생 중단 요구) 메시지로 전체 재생을 즉시 멈출 수 있다. 이때 각 SCC는 SCM이 명령했던 자기 기능을 safe state(안전 상태: SCC 제조사가 미리 정해 둔, 멈춰도 위험하지 않은 상태)로 바꾼다.

SCM과 SCC는 각각 상태 머신(정해진 상태 가운데 하나에 머물다가, 정해진 일이 생길 때만 다른 상태로 넘어가는 동작 방식)으로 움직인다. 상태 목록은 다음과 같다.

| 구분 | 상태 |
|------|------|
| SCM | Inactive(시동 후 기본) · Ready · Recording · Recording Completion · Play Back · Abort |
| SCC | Disabled(시동 후 기본) · Ready · Recording · Play Back · Abort |

상태 이름의 뜻은 다음과 같다.

| 상태 | 쉽게 말하면 |
|---|---|
| Inactive | SCM이 꺼져 있다. 시동 직후 SCM은 이 상태다 |
| Disabled | SCC가 SC에 참여하지 않는다. 시동 직후 SCC는 이 상태다 |
| Ready | 대기 중이다. 기록이나 재생을 시작할 수 있다 |
| Recording | 기록 중이다 |
| Recording Completion | 기록을 멈췄지만, 아직 끝나지 않은 동작의 완료 보고를 기다리는 중이다(SCM에만 있다) |
| Play Back | 재생 중이다 |
| Abort | 재생을 중단하는 중이다 |

SCC의 Ready, Recording, Play Back, Abort를 묶어 enabled(참여 중) 상태라고 부른다. 기록된 시퀀스 하나는 SCS라고 부른다.

active SCM은 자기 상태를 <strong>SCMasterStatus</strong>(SCM 상태 알림) 메시지로 모두에게 방송(broadcast)하고, enabled SCC들은 이 상태를 따라간다. 지휘자의 손짓을 단원들이 보고 따라가는 것과 같다. SCC는 active SCM이 enable(참여)을 명령할 때만 Disabled에서 벗어날 수 있고, SCMasterStatus가 끊겨 일정 시간 안에 오지 않으면(timeout) 스스로 Disabled로 돌아간다. 반대로 SCM도 어떤 SCC의 상태 메시지가 timeout 되면 기록을 취소하거나 재생을 멈춘다. 이렇게 서로를 지켜보기 때문에 어느 한쪽이 사라져도 시스템 전체가 안전 상태로 모인다.

상태가 정확히 어떤 일로 바뀌는지는 아래 7절 "SCM과 SCC의 상태 머신"에서 그림과 표로 본다.

<small>근거: ISO 11783-14 3.17, 3.19, 4.1, 4.4.1, 4.4.7.3</small>

## 3. 메시지 구조: PGN 두 개와 메시지 코드

이 절에서는 SC 메시지가 CAN 버스 위에서 어떤 모양인지 본다. PGN(Parameter Group Number, 메시지 종류를 가리키는 번호)과 데이터 첫 바이트만 알면 어떤 SC 메시지인지 가릴 수 있다.

SC 메시지는 봉투가 두 종류뿐인 우편과 같다. SCM이 보내는 봉투와 SCC가 보내는 봉투가 있고, 봉투 안 첫 줄에 적힌 메시지 코드가 무슨 내용의 편지인지 알려 준다. SC 통신에는 PGN이 단 두 개 예약되어 있고, 메시지 종류는 데이터 <strong>Byte 1의 message code</strong>(메시지 코드)로 구분한다.

| PGN | 방향 | 특성 |
|-----|------|------|
| 36352 (0x8E00) | SCM → SCC | destination-specific, 우선순위 4 |
| 36096 (0x8D00) | SCC → SCM | destination-specific, 우선순위 4 |

destination-specific은 받는 장치의 주소를 지정해 보내는 메시지라는 뜻이다. 모두에게 보낼 때는 받는 주소 자리에 전역 주소 0xFF(=255)를 넣는다. 우선순위는 0~7이고 숫자가 작을수록 먼저 버스를 차지한다. ID 구조는 [9장 J1939 메시지 구조](/study/isobus/09-j1939-message)에서 다뤘다.

::: warning 먼저 알아 둘 표기 세 가지
- SC의 message code는 16진수다. 표준 문서는 `30₁₆`, `95₁₆`처럼 아래 첨자 16을 붙여 적는다. SCMasterStatus의 Byte 1은 10진수 95가 아니라 `0x95`(10진수 149)다. 반대로 File Server 표준(ISO 11783-13)은 함수 코드를 `32₁₀`처럼 10진수로 적는다.
- 메시지 안의 비트는 1~8로 센다(Bit 1 = 최하위 비트). "Bits 7-8"은 상위 2비트, 곧 `(b >> 6) & 0x03`이다. 같은 SC 표준이라도 SCD 레코드 안의 Bitmask(비트 묶음 필드)는 Bit 0부터 센다. File Server 표준도 0부터 센다.
- SC 표준은 여러 바이트로 된 값의 바이트 순서를 따로 적지 않는다. 이 장과 [54장](/study/isobus/54-sequence-control-details)의 예제는 ISOBUS의 다른 부분(ISO 11783-7과 File Server 표준)이 정한 LSB 우선(little-endian: 낮은 자리 바이트가 먼저 온다)을 가정한다.
:::

주요 message code는 다음과 같다.

| code | 메시지 | 방향 | 역할 |
|------|--------|------|------|
| 0x32 | SCExecutionIndication / Response | SCC → SCM / SCM → SCC | 기록 중 "이 기능을 조작했다" 알림과 저장 확인 |
| 0x33 | SCMasterExecutionCommand | SCM → SCC | 재생 중 trigger point 도달 시 실행 명령 |
| 0x34 | SCClientExecutionStatus / Acknowledgement | SCC → SCM / SCM → SCC | 명령 실행의 시작·완료 보고와 확인 |
| 0x31 | SCClientAbort | SCC → 전역 | 재생 즉시 중단 요구 |
| 0x95 | SCMasterStatus | SCM → 전체 | SCM 상태 broadcast (Ready 1 Hz, 활동 상태 5 Hz) |
| 0x96 | SCClientStatus | SCC → SCM | SCC 상태 보고 (주기 동일) |

표를 읽는 법을 덧붙인다.

- 코드는 16진수다. 0x31~0x34는 10진수 49~52, 0x95와 0x96은 149와 150이다.
- "/"로 나뉜 칸은 같은 코드를 요청과 응답이 함께 쓴다는 뜻이다. 앞쪽이 요청, 뒤쪽이 응답이다. 방향이 다르므로 PGN으로 둘을 가른다.
- 1 Hz는 초당 1번, 5 Hz는 초당 5번이다. 활동 상태는 Recording, Recording Completion, Play Back, Abort를 말한다. 일이 진행되는 동안에는 상태를 더 자주 알린다.

명령과 요청은 응답을 받을 때까지 최소 100 ms 간격으로 반복하고, 1.6 s까지 응답이 없으면 무응답으로 처리한다. 반복 규칙의 세부는 [54장](/study/isobus/54-sequence-control-details)에서 본다.

다음은 C 언어로 작성한 SCMasterExecutionCommand(재생 중 실행 명령) 전송 예시다. SCM이 8바이트 데이터를 채우고 29비트 CAN ID를 만들어 보내는 과정을 보여 준다.

```c
#include <stdint.h>

/* ISO 11783-14 message codes (data Byte 1) */
#define SC_MSG_CLIENT_ABORT        0x31
#define SC_MSG_EXEC_INDICATION     0x32
#define SC_MSG_MASTER_EXEC_CMD     0x33
#define SC_MSG_CLIENT_EXEC_STATUS  0x34

/* Build and send an SCMasterExecutionCommand (playback trigger) */
int scm_send_execution_command(uint8_t function_id, uint8_t state_id,
                               uint8_t tan, uint32_t function_value,
                               uint8_t da, uint8_t sa,
                               void (*can_send)(uint32_t id, const uint8_t *data, uint8_t len))
{
    uint8_t frame[8];

    frame[0] = SC_MSG_MASTER_EXEC_CMD;      /* message code 0x33 */
    frame[1] = function_id;                 /* SCD function object의 function ID */
    frame[2] = state_id & 0x3F;             /* bits 1-6 = state ID, 상위 2비트 예약(0) */
    frame[3] = tan;                         /* transaction number */
    frame[4] = (uint8_t)(function_value);   /* 기록 시 저장된 function value, LSB first */
    frame[5] = (uint8_t)(function_value >> 8);
    frame[6] = (uint8_t)(function_value >> 16);
    frame[7] = (uint8_t)(function_value >> 24);

    /* priority 4, PGN 36352 (0x8E00), PDU specific = destination address */
    uint32_t can_id = (4UL << 26) | (0x8EUL << 16) | ((uint32_t)da << 8) | sa;
    can_send(can_id, frame, sizeof(frame));
    return 0;
}
```

핵심 줄은 다음과 같다.

- `frame[0]`: 메시지 코드 0x33(=51)이다. 받는 쪽은 이 바이트로 실행 명령임을 안다.
- `frame[2] = state_id & 0x3F`: 0x3F(=63, 2진수 `0011 1111`)와 AND해서 아래 6비트만 남긴다. 상태 ID는 6비트이고, 위 2비트는 이 메시지에서 쓰지 않으므로 0이다.
- `frame[3]`: TAN이다. 응답이 어느 명령에 대한 것인지 맞춰 보는 번호다(4절).
- `frame[4]`~`frame[7]`: 기록할 때 저장한 function value(기능 값, 예를 들어 히치가 멈춘 높이)를 낮은 자리 바이트부터 넣는다.
- `can_id`: 우선순위 4를 26번 비트 자리부터, PGN의 앞 바이트 0x8E를 16번 비트 자리부터, 받는 주소(da)를 8번 비트 자리부터, 보내는 주소(sa)를 맨 아래에 놓는다.

SCC는 이 명령에 <strong>SCClientExecutionStatus</strong>(code 0x34)로 응답하며, 응답에는 명령과 같은 TAN을 실어 어느 명령에 대한 응답인지 밝힌다.

<small>근거: ISO 11783-14 B.1~B.3, E.1, E.6, F.2, F.3</small>

## 4. SCD와 TAN: 미리 건네는 자기소개와 명령 번호표

이 절에서는 기록과 재생이 성립하려면 미리 갖춰야 하는 두 가지를 본다. SCM이 SCC의 기능을 알게 해 주는 SCD, 그리고 명령과 응답이 뒤섞이지 않게 해 주는 TAN이다.

<strong>SCD는 SCC의 자기소개서다.</strong> 기록과 재생이 성립하려면 SCM이 각 SCC가 어떤 기능을 갖고 있는지 알아야 한다. 이를 위해 SCC는 초기화 때 <strong>SCD</strong>(Sequence Control Data)라는 오브젝트 풀(정해진 형식의 데이터 묶음)을 SCM에 올린다(업로드).

- SCD는 basic object(SCC 식별) → function object(기록 가능한 기능, 최대 255개) → state object(기능별 상태, 최대 64개)의 계층 구조다. 예를 들어 "3점 히치"가 function object이고, "상승"과 "하강"이 그 아래 state object다.
- 각 오브젝트는 SCC가 VT(Virtual Terminal, 운전석의 공용 화면 단말)에 올린 그림·글자 오브젝트의 ID를 가리킨다. SCM은 External Object Pointer(다른 장치의 오브젝트를 가리켜 자기 화면에 보여 주는 VT 오브젝트)로 이 그림과 글자를 자기 화면 안에 표시한다. 그래서 SCM과 SCC 모두 function instance 0인 VT(같은 종류의 VT가 여러 대일 때 순번이 0인 VT)에 접속한다.
- SCM은 SCC당 SCD 하나를 비휘발성 메모리(전원이 꺼져도 남는 메모리)에 저장할 수 있다. 그래서 매번 시동할 때마다 SCD를 다시 올리지 않아도 된다.

![SC 시스템 안에서 SCM은 PGN 36352로 각 SCC에 실행 명령을 보내고, SCC는 PGN 36096으로 조작 알림과 상태를 보낸다. SCM은 자기 화면을, SCC는 그림과 글자를 function instance 0 VT에 올린다](/images/study-isobus/53-sc-system-vt-light.png)
![SC 시스템 안에서 SCM은 PGN 36352로 각 SCC에 실행 명령을 보내고, SCC는 PGN 36096으로 조작 알림과 상태를 보낸다. SCM은 자기 화면을, SCC는 그림과 글자를 function instance 0 VT에 올린다](/images/study-isobus/53-sc-system-vt-dark.png)

<strong>TAN은 명령 번호표다.</strong> 식당에서 주문할 때마다 주문 번호를 붙이면, 같은 음식이 두 번 나와도 어느 주문의 것인지 헷갈리지 않는다. <strong>TAN</strong>(Transaction Number)이 바로 그 번호다.

- 보내는 쪽은 새 명령마다 자기 TAN 카운터를 1 올린다.
- 같은 명령을 다시 보낼(반복 송신) 때는 같은 TAN을 그대로 쓴다.
- 받는 쪽은 받은 TAN을 응답에 그대로 되돌려 보낸다.

받는 쪽은 TAN, function ID, state ID가 모두 맞을 때만 응답을 처리한다. 그래서 반복 송신한 명령과 늦게 도착한 응답이 섞여도 헷갈리지 않고, 한 SCC가 여러 명령을 동시에 걸어 둘 수도 있다. TAN은 File Server에서도 같은 목적으로 쓴다([51장 File Server(FS) 기초](/study/isobus/51-file-server-basics)).

::: tip 1~4절 정리
- ISO 11783-14는 운전자의 조작을 기록(recording)했다가 재생(playback)하는 표준이다. GPS가 알아서 실행하는 방식이 아니다.
- SCM이 기록과 재생을 이끌고, SCC가 기능을 갖고 실행한다. active SCM은 동시에 하나뿐이다.
- PGN은 2개(SCM→SCC 36352, SCC→SCM 36096)이고, 데이터 Byte 1의 message code로 메시지를 가른다.
- trigger는 시간 기반이나 거리 기반으로 저장되고, 재생이 중단(Abort)되면 SCC는 자기 기능을 안전 상태로 바꾼다.
:::

<small>근거: ISO 11783-14 4.2, 4.4, 4.6, Annex A</small>

## 5. SCM이 갖춰야 할 기능

1~4절이 큰 그림이었다면, 5절부터는 SCM이나 SCC를 직접 만들 때 지켜야 하는 규칙을 본다. 내용은 ISO 11783-14:2013(1판)을 기준으로 했다. 메시지와 오브젝트별 전체 표는 [표준 정리: Part 14](/study/isobus/appendix-iso-part14)에 있다. 이 절에서는 먼저 SCM이 반드시 해야 하는 일과 해도 되는 일을 가른다.

<strong>SCM의 필수 기능과 선택 기능.</strong> SCM은 시퀀스를 만드는 수단(RECORD 또는 EDIT)을 최소 하나, 선택한 시퀀스를 재생하는 수단(PLAY BACK)을 반드시 제공한다. SCM 구성(CONFIG), 인식한 SCC와 그 기능·선호 trigger의 표시, SCC enable/disable은 선택이다.

| 기능 | 필수 여부 | 하는 일 |
|---|---|---|
| RECORD 또는 EDIT | 둘 중 하나 이상 필수 | 시퀀스를 만든다. RECORD는 운전자의 조작을 기록하고, EDIT는 화면에서 직접 만들거나 고친다 |
| PLAY BACK | 필수 | 선택한 시퀀스를 재생한다 |
| CONFIG | 선택 | SCM 자체를 설정한다 |
| SCC와 기능 표시 | 선택 | 인식한 SCC, 그 기능, 선호 trigger를 운전자에게 보여 준다 |
| SCC enable/disable | 선택 | 특정 SCC를 시퀀스 관리에 넣거나 뺀다 |

enable/disable은 기록·편집 때 시스템 구성을 단순하게 하고 버스 부하를 줄이는 용도다. SCM은 enabled SCC만 시퀀스 관리에 넣는다.

시퀀스를 다루는 규칙은 다음과 같다.

- 운용 중 활성화될 수 있는 모든 시퀀스에는 서로 다른 시퀀스 번호를 준다. 입력 4개로 시퀀스 4개를 부르는 SCM이라면 번호 4개가 모두 달라야 한다. 표준은 헤드랜드에 들어갈 때 쓰는 시퀀스를 1번, 나올 때 쓰는 시퀀스를 2번으로 두는 예를 든다.
- 기록된 시퀀스는 SCM마다 따로 저장하고 관리한다. 시퀀스를 다른 SCM이나 PC로 옮기는 표준 방법은 없다.
- SCM은 비휘발성 메모리에 SCC당 SCD를 하나만 보관한다.

<small>근거: ISO 11783-14 3.20, 4.1, 4.4, 4.4.5</small>

## 6. SCM 화면에 SCC의 그림과 글자를 띄우는 법 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

SCM이 시퀀스 내용을 화면에 보여 주려면 "히치 상승" 같은 기능 이름과 아이콘이 필요하다. 그런데 이 그림과 글자는 SCC가 갖고 있다. 이 절에서는 SCM이 그림을 직접 받지 않고도 화면에 띄우는 방법을 본다.

<strong>화면 연결: External Object Pointer.</strong> SCM 화면은 액자 틀만 걸어 둔 벽과 같다. 그림은 각 SCC가 VT에 걸어 두고, SCM은 "저 그림을 여기에 보여 줘"라는 가리킴만 둔다. 구체적으로는 SCC(또는 그 Working Set Master)가 자기 오브젝트 풀인 SCCOP(SCC Object Pool)에 그림·텍스트를 담아 VT에 올리고, SCM은 SCD에 적힌 object ID만 받아 자기 오브젝트 풀인 SCMOP(SCM Object Pool)의 External Object Pointer로 가리킨다.

External Object Pointer는 VT version 5에서 도입된 오브젝트로, SCM이 SCC마다 큰 그래픽이나 언어 갱신을 떠안지 않게 하려고 쓴다. 같은 VT를 써야 참조가 성립하므로 SCM과 SCC의 Working Set Master는 모두 function instance 0인 VT에 접속한다. SCC의 주 화면이 다른 VT(function instance > 0)에 있다면 SCC working set은 VT 연결 두 개를 동시에 유지해야 할 수 있다. VT 오브젝트 풀 자체는 [32장 VT 오브젝트 풀 기초](/study/isobus/32-vt-object-pool-basics)에서 다뤘다.

연결에는 VT 오브젝트 세 종류가 쓰인다.

- External Reference NAME: 참조할 상대 장치의 NAME(장치마다 고유한 64비트 이름, [12장](/study/isobus/12-j1939-address-name))을 담는다. SCM 쪽에 있다.
- External Object Definition: "이 NAME의 장치에게는 내 오브젝트 가운데 이것들을 보여 줘도 된다"는 허용 목록이다. SCC 쪽에 있다.
- External Object Pointer: 화면에서 남의 오브젝트를 보여 줄 자리다. SCM 쪽에 있다.

연결은 NAME을 기준으로 4단계를 거친다. 표준 문서의 예시 그림에 나오는 오브젝트 ID를 그대로 따라가면 다음과 같다. SCM 쪽 오브젝트는 0x2A~0x2C, SCC 쪽 오브젝트는 0x3A~0x3C다.

| 단계 | 주체 | 하는 일 | 예(표준 예시의 오브젝트 ID) |
|---|---|---|---|
| 1 | SCM | SCMOP를 올릴 때 External Reference NAME 오브젝트는 disabled, External Object Pointer는 NULL(0xFFFF)로 둔다 | 0x2A disabled, 0x2B·0x2C = 0xFFFF |
| 2 | SCC | active SCM의 NAME을 확인하고, 자기 External Object Definition 오브젝트의 NAME을 SCM NAME으로 바꿔 enable한다(Change Attribute) | 0x3A = SCM NAME, 목록 0x3C·0x3B |
| 3 | SCM | SCC NAME을 확인하고 External Reference NAME 오브젝트에 SCC NAME을 넣어 enable한다 | 0x2A = SCC NAME |
| 4 | SCM | SCD의 object ID로 External Object Pointer마다 External Reference NAME ID와 External Object ID를 설정한다 | 0x2B → (0x2A, 그림 0x3C), 0x2C → (0x2A, 텍스트 0x3B) |

NULL(0xFFFF, 10진수 65535)은 "아직 가리키는 대상이 없다"는 특수값이다. 1단계에서 포인터를 비워 두는 이유는 상대 장치가 아직 정해지지 않았기 때문이다.

SCM과 VT가 주고받는 메시지에는 8바이트 NAME 대신 External Reference NAME 오브젝트의 2바이트 object ID가 실린다. 참조를 바꿀 때마다 NAME 전체를 보내지 않으려는 설계다. 포인터 하나를 채우려면 속성 두 개를 바꾼다: External Reference NAME ID(속성 번호 2)와 External Object ID(속성 번호 3)다. VT 표준은 External Object Pointer에 Change Attribute와 Change Numeric Value 명령을 모두 허용한다.

::: warning 화면 연결에서 생기는 구현 함정
- SCM은 SCD에 적힌 object ID의 오브젝트 종류를 확인할 수단이 없다. 텍스트 자리에 그림 ID를 넣는 실수를 막는 책임은 SCC에 있고, SCM은 VT가 참조를 거부하는 경우에 대비해야 한다.
- SCC의 External Object Definition 목록에 오른 오브젝트만 참조할 수 있다. VT는 그리기 전에 참조가 유효한지 확인한다. External Reference NAME이 enabled인지, 참조 대상 풀이 VT에 올라와 있는지, 그 풀에 참조자 NAME을 담은 enabled External Object Definition이 있는지, 대상 ID가 그 목록에 있는지를 보고, 하나라도 어긋나면 Default Object ID의 오브젝트(대신 보여 줄 기본 오브젝트)를 그린다.
:::

<strong>Working Set master와 member.</strong> 여러 ECU가 한 덩어리로 동작하는 묶음을 Working Set이라 하고, 그 대표를 Working Set Master, 나머지를 member라고 한다([26장](/study/isobus/26-isobus-network-mgmt)). SCC가 Working Set member이면 VT 연결과 SCCOP는 Working Set Master가, SCM 연결(SCD 업로드 포함)은 SCC 자신이 맡는다. 이때 SCD basic object의 SCCWS Master NAME에는 SCC가 아닌 Working Set Master의 NAME을 넣는다. member가 master 오브젝트 풀의 object ID를 어떻게 알아내는지는 SC 표준의 범위 밖이다.

::: details 원문을 가진 독자를 위한 메모
- 4.2.1 본문은 포인터 하나에 Change Attribute가 두 번 든다고 쓰는데, 초기화 흐름도(Figure 8)는 Change Numeric Value로 그린다. Part 6 B.24는 External Object Pointer에 두 명령을 모두 허용하고, 4.2.1이 말하는 두 속성은 Part 6 Table B.70의 AID 2(External Reference NAME ID)와 AID 3(External Object ID)이다.
- 4단계 표의 오브젝트 ID는 Part 14 Figure 2·3의 예다. VT의 참조 유효성 검사는 ISO 11783-6:2018 4.6.11.6에 있다.
:::

<small>근거: ISO 11783-14 4.2, 4.2.1, 4.3.2</small>

## 7. SCM과 SCC의 상태 머신

2절에서 상태 이름을 익혔다. 이 절에서는 어떤 일이 생기면 어느 상태로 넘어가는지 그림과 표로 본다. 두 장치가 같은 단계에 있어야 기록과 재생이 맞물리기 때문에, 상태가 바뀌는 조건이 SC의 뼈대다.

그림의 상자는 상태, 화살표는 상태가 바뀌는 길이다. 화살표 옆의 `SCM_A`, `SCC_B` 같은 이름은 표준이 각 조건에 붙인 이름이고, 아래 표에서 뜻을 풀어 쓴다. `*`가 붙은 조건은 표준이 선택(optional)으로 둔 것이라 구현하지 않아도 된다.

### SCM의 상태

![SCM 상태 머신: 시동 후 Inactive, Master ON으로 Ready, Ready에서 Recording과 Play Back으로 갈라지고 Recording Completion과 Abort를 거쳐 Ready로 돌아오는 천이와 조건 코드](/images/study-isobus/21-scm-state-machine-light.png)
![SCM 상태 머신: 시동 후 Inactive, Master ON으로 Ready, Ready에서 Recording과 Play Back으로 갈라지고 Recording Completion과 Abort를 거쳐 Ready로 돌아오는 천이와 조건 코드](/images/study-isobus/21-scm-state-machine-dark.png)

SCM은 시동하면 Initialization(시동했다는 알림)을 한 번 보내고 Inactive에서 시작한다. 그 뒤로는 다음 표대로 움직인다. 실행 상태 10(완료)과 11(실행 중 오류)은 SCC가 기능 실행이 어디까지 왔는지 알리는 2비트 값이다. 00은 시작과 완료가 동시, 01은 시작을 뜻한다. 바이트 위치는 [54장](/study/isobus/54-sequence-control-details)에서 본다.

| 지금 상태 | 이런 일이 생기면 | 다음 상태 | 조건 |
|---|---|---|---|
| Inactive | 운전자가 SC를 켠다(Master ON) | Ready | SCM_A |
| Ready | 운전자가 SC를 끈다(Master OFF) | Inactive | SCM_B |
| Ready | 운전자가 기록을 시작한다(Start Recording) | Recording | SCM_C |
| Recording | 운전자가 기록을 멈췄는데, 기록한 기능 가운데 아직 10이나 11을 보내지 않은 것이 있다(Stop Recording) | Recording Completion | SCM_G |
| Recording | 운전자가 기록을 멈췄고, 기록한 모든 기능이 10(완료) 또는 11(오류)을 보냈다 | Ready | SCM_D |
| Recording Completion | 남은 기능이 모두 10이나 11을 보냈다 | Ready | SCM_H |
| Recording, Recording Completion | SCM 내부의 취소 조건이 생겼다 | Ready | SCM_I |
| Recording, Recording Completion | 운전자가 기록을 취소한다(Cancel Record) | Ready | SCM_E* |
| Recording, Recording Completion | SCExecutionIndication에 실행 상태 11이 왔다 | Ready | SCM_F* |
| Ready | 운전자가 재생을 시작한다(Start Play Back) | Play Back | SCM_K |
| Play Back | 시퀀스가 정상으로 끝났다 | Ready | SCM_L |
| Play Back | SCC가 SCClientAbort를 보냈다 | Abort | SCM_M |
| Play Back | 운전자가 재생을 중단한다(Abort) | Abort | SCM_N |
| Play Back | SCM 내부의 중단 조건이 생겼다 | Abort | SCM_R* |
| Play Back | SCClientExecutionStatus에 실행 상태 11이 왔다 | Abort | SCM_P* |
| Play Back | SCExecutionIndication에 실행 상태 11이 왔다 | Abort | SCM_F* |
| Abort | 모든 enabled SCC가 Abort를 반영했다 | Ready | SCM_T |

표에 다 넣지 못한 구현 메모는 다음과 같다.

- Inactive → Ready(SCM_A): 다른 SCM이 active인 동안 inactive SCM은 상태를 바꾸지 못하고, 운전자에게 기존 SCM을 먼저 끄라고 알린다.
- Ready → Inactive(SCM_B): 비활성화는 Ready에서만 가능하다.
- Ready → Recording(SCM_C): 모든 enabled SCC가 Ready를 보고할 때만 들어간다.
- Recording → Recording Completion(SCM_G): 이 상태에서 새로 보고된 기능 시작은 무시한다.
- SCM_I와 SCM_R*의 예: SCC 메시지 타임아웃, SCC가 갑자기 disabled로 떨어짐.
- Ready → Play Back(SCM_K): 선택한 시퀀스의 모든 SCC가 Ready를 보고할 때만 들어간다.

읽을 때 놓치기 쉬운 점이 셋 있다.

- <strong>SCM_F*는 두 곳에 있다.</strong> 기록 중 SCExecutionIndication의 실행 상태 11(실행 중 오류)은 기록 취소(Ready)로, 재생 중 11은 Abort로 이어진다. 재생 중의 11은 "운전자가 손으로 기능을 조작했다"는 뜻이다. 둘 다 선택 요구사항이라 SCM이 그 기능만 빼고 계속 진행해도 된다.
- <strong>Abort는 Play Back에서만 들어간다.</strong> SCM은 Play Back 상태에서만 SCClientAbort를 받아들인다. 기록 중의 문제는 abort(중단)가 아니라 cancel(취소)이고, 결과는 Ready다.
- <strong>active SCM은 기록·재생 중 자기 상태를 바꾸지 못하게 해야 한다.</strong> 운전자가 Master OFF를 눌러도 Ready로 돌아온 다음에 처리한다.

### SCC의 상태

![SCC 상태 머신: 시동 후 Disabled, SCStateCommand Enabled로 Ready, SCM 상태를 따라 Recording·Play Back·Abort로 움직이고 어느 enabled 상태에서든 Disabled로 떨어지는 천이와 조건 코드](/images/study-isobus/21-scc-state-machine-light.png)
![SCC 상태 머신: 시동 후 Disabled, SCStateCommand Enabled로 Ready, SCM 상태를 따라 Recording·Play Back·Abort로 움직이고 어느 enabled 상태에서든 Disabled로 떨어지는 천이와 조건 코드](/images/study-isobus/21-scc-state-machine-dark.png)

SCC는 대부분 SCM의 상태를 보고 따라 움직인다. 표에서 "SCM 상태가 ~"는 SCMasterStatus에 실린 상태를 말한다. SCStateCommand(SCM이 SCC에게 참여 여부를 명령하는 메시지)와 NACK(Negative Acknowledgement, "받았지만 처리하지 않는다"는 거절 응답, [10장](/study/isobus/10-j1939-request-ack))도 상태를 바꾼다.

| 지금 상태 | 이런 일이 생기면 | 다음 상태 | 조건 |
|---|---|---|---|
| 시동 직후 | active SCM의 상태를 받았다. 첫 SCClientStatus는 Initialization 1회 | Disabled | SCC_A |
| Disabled | SCStateCommand로 Enabled 명령을 받았다 | Ready | SCC_B |
| enabled 상태 어디서나 | SCStateCommand로 Disabled 명령을 받았다 | Disabled | SCC_C |
| enabled 상태 어디서나 | SCMasterStatus 타임아웃 | Disabled | SCC_D |
| enabled 상태 어디서나 | 운전자가 이 SCC를 SC에 참여하지 않게 설정했다 | Disabled | SCC_E |
| enabled 상태 어디서나 | SCC 내부의 치명적 조건 | Disabled | SCC_F* |
| enabled 상태 어디서나 | SCM이 SCC 메시지에 NACK을 보냈다 | Disabled | SCC_G |
| Ready | SCM 상태가 Recording | Recording | SCC_K |
| Recording | SCM 상태가 Ready | Ready | SCC_L |
| Recording | SCM 상태가 Recording Completion이고 이 SCC의 기능 실행이 모두 끝났다 | Ready | SCC_M |
| Ready | SCM 상태가 Play Back | Play Back | SCC_N |
| Ready | SCMasterExecutionCommand를 받았다 | Play Back | SCC_O |
| Play Back | SCM 상태가 Abort | Abort | SCC_R |
| Play Back | 다른 SCC의 SCClientAbort를 받았다 | Abort | SCC_S |
| Play Back | SCS를 멈춰야 하는 내부 조건 | Abort | SCC_T* |
| Play Back, Abort | SCM 상태가 Ready | Ready | SCC_L |

SCC는 Ready, Recording, Play Back에는 SCM 명령으로만 들어간다. Abort만 예외로, SCM 명령, 다른 SCC의 전역 SCClientAbort, 자기 판단 가운데 무엇으로도 들어갈 수 있다. SCC_O 덕분에 SCM 상태 변화를 놓친 SCC도 첫 실행 명령을 받으면 Play Back으로 넘어가 명령을 수행한다.

::: details 원문을 가진 독자를 위한 메모
SCC_E는 Figure 5(SCC 상태 그림)에는 `SCC_E *`(선택)로, 바로 아래 조건 목록에는 `*` 없이 적혀 있다. 이 블로그의 SCC 상태 그림은 Figure 5를 따라 `E*`로, 위 표는 조건 목록을 따라 `SCC_E`로 적었다.
:::

### 상태 메시지에 싣는 값과 SCM 쪽 규칙 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

enabled SCC가 SCClientStatus(SCC 상태 보고) Byte 4(sequence state, 시퀀스 상태)에 싣는 값은 SCM 상태에 따라 정해진다. 왼쪽 칸은 SCM이 SCMasterStatus Byte 4로 알리는 값이고, 오른쪽 칸은 그때 SCC가 실어야 하는 값이다.

| SCM이 알리는 상태 (SCMasterStatus Byte 4) | SCC가 싣는 값 (SCClientStatus Byte 4) |
|---|---|
| Ready `0x01` | Ready `0x01` |
| Recording `0x02` | Recording `0x02` |
| Recording completion `0x03` | 기능 실행이 남았으면 Recording `0x02`, 끝났으면 Ready `0x01`. SCC에는 `0x03` 값이 없다 |
| Play back `0x04` | Play back `0x04`. 재생을 멈춰야 하면 Abort `0x05` |
| Abort `0x05` | Abort `0x05` |

기능 일부가 고장이어도 SCC는 SCM과 같은 값을 싣는다. 고장은 Byte 5의 ClientFunctionErrorState로 따로 알린다([54장](/study/isobus/54-sequence-control-details)의 오류 처리). SCM 쪽 규칙도 짝으로 기억해 둔다.

- client command(기능 실행 명령)는 SCClientStatus가 Play Back이나 Ready인 SCC에만 보낸다. 기록 중에는 Recording을 반영한 enabled SCC의 command만 저장한다.
- SCC가 SCClientStatus 타임아웃(활동 상태 600 ms, Ready 3 s) 안에 SCM 상태를 따라오지 않으면, SCM은 그 SCC의 SCD를 휘발성 메모리(전원이 꺼지면 지워지는 작업용 메모리)에서 지우고 이후 메시지를 NACK해 재연결을 강제한다. 예외는 SCC 상태가 일부러 달라지는 Recording Completion뿐이다.
- 빠른 반응을 위해 SCM은 이전 재생이 끝나기 전에 다음 재생을 시작할 수 있다. 이때 첫 시퀀스의 명령 송신을 멈추고 SCMasterStatus의 시퀀스 번호를 먼저 바꾼 뒤 다음 시퀀스 명령을 보낸다. 활성 시퀀스는 한 번에 하나뿐이고, 이전 시퀀스 명령을 마무리하는 SCC의 피드백을 fault(고장)로 보면 안 된다.

<small>근거: ISO 11783-14 4.4.1, 4.4.3, 4.4.4.1, 4.4.5.2, 4.4.7.1, 4.4.7.2, 4.5.3.4, F.2, F.3</small>

## 8. 초기화: SCC가 SCM에 합류하는 순서

이 절에서는 전원을 켠 뒤 SCC가 SCM과 연결되어 기록·재생에 참여할 수 있게 되기까지의 순서를 본다. 새로 들어온 직원이 출근 첫날 인사하고, 자기소개서를 내고, 승인을 받은 뒤에야 일을 시작하는 것과 비슷하다.

시동 직후 모든 SCM은 inactive, 모든 SCC는 disabled다. 둘 다 상태 메시지 Byte 2에 Initialization(`0x02`)을 한 번 실어 "방금 켜졌다"고 알린다. 상대가 예기치 않은 리셋을 알아채게 하려는 장치다. 주소 클레임(네트워크 주소를 정하는 절차)은 [13장 주소 클레임](/study/isobus/13-j1939-address-claim)의 절차를 그대로 따른다. 큰 흐름은 다섯 단계다.

1. SCM이 VT에 자기 화면을 올리고, 운전자가 이 SCM을 고르면 SCMasterStatus를 계속 보내기 시작한다.
2. SCC는 SCMasterStatus를 들은 뒤에 자기 상태 보고(SCClientStatus)를 시작한다.
3. SCC는 SCM의 능력(그림 크기, 글자 수 등)을 묻고, 거기에 맞춘 그림과 글자를 VT에 올린다.
4. SCC는 SCM에 자기 SCD가 이미 저장돼 있는지 확인한다. 없거나 맞지 않으면 SCD를 올리고(업로드), 맞으면 저장된 것을 불러오게(로드) 한다.
5. SCM이 SCD를 검사해 활성화하고, SCStateCommand로 SCC를 Enabled로 만들면 합류가 끝난다.

![SC 초기화 메시지 흐름: SCM이 VT에 SCMOP를 올리고 SCMasterStatus를 보내면, SCC가 상태 보고, capability 확인, SCCOP 업로드, SCD 버전과 구성 레이블 확인, 메모리 확인을 거쳐 SCDTransfer 또는 SCDLoadCommand 뒤 SCDActivationCommand로 활성화하고 SCStateCommand Enabled를 받는 순서](/images/study-isobus/21-sc-init-sequence-light.png)
![SC 초기화 메시지 흐름: SCM이 VT에 SCMOP를 올리고 SCMasterStatus를 보내면, SCC가 상태 보고, capability 확인, SCCOP 업로드, SCD 버전과 구성 레이블 확인, 메모리 확인을 거쳐 SCDTransfer 또는 SCDLoadCommand 뒤 SCDActivationCommand로 활성화하고 SCStateCommand Enabled를 받는 순서](/images/study-isobus/21-sc-init-sequence-dark.png)

그림의 실선은 요청, 명령, 상태 알림이고 점선은 그에 대한 응답이다. 가운데 주황 테두리 상자는 둘 가운데 하나만 일어나는 갈림길(alt)이다.

### 단계별 세부 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

괄호 안의 16진수는 그 단계에서 쓰는 message code다.

1. <strong>SCM 준비</strong>: SCM은 function instance 0인 VT에 SCMOP를 올린다. External Object Pointer는 모두 비활성(0xFFFF)이다. 운전자가 고를 때까지 inactive로 있다가, 선택되면 SCMasterStatus를 연속 송신한다.
2. <strong>SCM의 SCD 초기화</strong>: active가 된 SCM은 휘발성 메모리의 SCD를 모두 지우고, SCC가 Initialization을 알리기 전까지 그 밖의 SCClientStatus를 NACK한다. SCMasterStatus 주기 안에서 quick reset(아주 짧은 재시작)한 경우만 예외다.
3. <strong>SCC 상태 보고</strong>: SCC는 active SCM의 SCMasterStatus를 받은 뒤에 SCClientStatus를 시작한다. SCM보다 먼저 부팅해도 기다린다. 첫 메시지는 Initialization, 이후 Disabled 연속이다.
4. <strong>capability 확인</strong> (`0x90`, 10진수 144): SCC가 자기 SC 표준 버전을 보내면, SCM이 10바이트 응답으로 버전, 그래픽 크기(Byte 3·4, 최소 32픽셀), designator(기능 이름 같은 표시용 글자) 최대 표시 문자 수(Byte 5·6, 최소 32), 폰트 색·크기·종류·스타일(Byte 7~10)을 알린다. 10바이트는 CAN 프레임 하나(8바이트)에 들어가지 않으므로 TP(Transport Protocol, 긴 데이터를 여러 프레임으로 나눠 보내는 규칙, [15장](/study/isobus/15-tp-bam-cmdt))가 필요하다. 그래픽 크기로는 사용 중인 VT의 soft key(화면 옆 기능 버튼) 크기를 보고해야 한다. SCC는 이 값에 맞춰 SCCOP 오브젝트를 다듬는다. 정의보다 큰 오브젝트는 VT에서 중요한 정보가 잘릴 수 있기 때문이다.
5. <strong>SCCOP 업로드</strong>: SCC의 Working Set Master가 function instance 0 VT에 접속해, 색·언어 같은 VT capability에 맞춘 풀을 올린다. 자기 화면을 이 VT에 띄우지 않더라도 SCMOP가 참조할 텍스트·그래픽을 담은 SCCOP만큼은 반드시 올린다.
6. <strong>저장된 SCD 확인</strong> (`0x01`, `0x02`): SCDVersionRequest·SCDConfigurationLabelRequest로 SCM에 자기 SCD가 있는지, 버전과 기계 구성이 맞는지 본다. SCM은 SCD basic object의 NAME Mask(NAME의 어느 비트를 비교할지 정하는 마스크, [54장](/study/isobus/54-sequence-control-details))로 저장된 SCD와 SCC를 맞춘다. 응답 Byte 2는 00(레이블 첨부), 01(일치하는 SCD 없음), FF(기타 오류)이고, 오류면 Byte 4~8을 FF로 채운 8바이트다. 레이블 내용은 SCC 제조사 고유이고, SCC 소프트웨어 갱신으로 저장된 SCD가 무효가 될 수 있다.
7. <strong>메모리 확인</strong> (`0x91`, 10진수 145): SCMasterMemoryRequest Byte 2~5에 올리거나 불러올 SCD의 바이트 수를 싣는다. 응답 Byte 2가 00이면 진행하되, "충분할 수도 있다"는 뜻일 뿐이다. 오브젝트 저장 오버헤드 때문에 확답할 수 없어서다. 01이면 전송도 로드도 하면 안 된다.
8. <strong>업로드 또는 로드</strong>: SCD가 없거나 맞지 않으면 SCDTransfer(`0x03`)로 올린다. TP가 필요하고, 1,785바이트를 넘으면 ETP(Extended Transport Protocol, 더 큰 데이터용 전송 규칙, [17장](/study/isobus/17-etp))를 쓴다. 응답 Byte 2는 00(정상 수신), 01(전송 중 오류), FF다. 저장된 SCD를 쓰기로 했으면 SCDLoadCommand(`0x07`)로 비휘발성 메모리에서 휘발성 메모리로 불러온다. 응답은 00 성공, 01 없음, 02 파일 시스템 오류·데이터 손상, 03 휘발성 메모리 부족, FF다.
9. <strong>활성화</strong> (`0x04`): SCDActivationCommand를 받은 SCM은 SCD 무결성을 파싱(내용을 읽어 검사)하면서 SCMasterStatus Byte 5의 bit 2(SCD 파싱 중)를 켠다. 결과는 SCDActivationResponse Byte 2의 오류 코드와 Byte 3~4의 첫 결함 object ID(정상이면 0xFFFF)로 온다. 오류 코드가 0이 아니면 그 SCD는 쓸 수 없다. SCC는 긍정 응답을 받기 전까지 SCClientStatus 외의 SC 통신을 이어 가면 안 된다.
10. <strong>저장(선택)</strong> (`0x06`): 다음 시동에 다시 올리지 않으려면 SCDStoreCommand로 파싱이 끝난 SCD를 비휘발성 메모리에 저장시킨다. SCM은 NAME Mask로 SCC당 하나만 남기고 이전 버전을 덮어쓴다. 응답 01(파싱 미완료)이나 02(비휘발성 메모리 부족)로 실패해도 휘발성 메모리의 SCD는 계속 쓸 수 있고, 다음 시동에 다시 올리면 된다.
11. <strong>Enabled 대기</strong>: 초기화가 끝나도 SCC는 SCStateCommand(`0x30`, 10진수 48) Enabled를 받을 때까지 Disabled다. SCM은 받은 SCD로 External Object Pointer를 채운다.

SCD를 지울 때는 SCDDeleteCommand(`0x05`)를 쓴다. Byte 2가 00이면 휘발성, 01이면 비휘발성 메모리의 SCD를 지운다. 메모리 제약으로 연결이 끊겨 일부만 전송된 SCD를 치울 때도 쓴다.

::: tip SCD 메시지에는 응답 타임아웃이 없다
SCD를 다루는 메시지(코드 0x01~0x07)는 응답별 타임아웃을 정하지 않는다. SCM의 메모리 처리 시간이 SCD 크기 등에 크게 좌우되기 때문이다. 대신 SCC는 타임아웃을 잴 때 SCMasterStatus의 busy flag(SCM이 바쁘다는 표시)를 존중해야 하고, flag(bit 1 비휘발성 메모리 접근 중, bit 2 SCD 파싱 중)가 켜진 동안에는 SCM에 대한 미결 응답의 타임아웃 측정을 멈춘다.
:::

::: warning 레이블 길이 64자와 63자
SCD의 정의는 SCD Version Label과 Configuration Label의 길이를 각각 1~64로 정한다. 그런데 SCDVersionResponse·SCDConfigurationLabelResponse의 길이 필드는 Byte 3의 Bits 1-6(6비트)이라 최대 63이다. SCDActivationResponse의 오류 코드 09·0B도 "0 또는 63바이트 초과"를 길이 오류로 본다. 표준 안에서 값이 엇갈리고 이유는 적혀 있지 않으므로, 레이블은 63자 이하로 만드는 편이 안전해 보인다(추론).
:::

<small>근거: ISO 11783-14 4.4.2, A.3, C.2~C.5, D.1~D.15, F.2</small>

::: tip 핵심 정리
- SC는 운전자가 헤드랜드에서 하던 조작을 한 번 기록해 두고, 다음부터 버튼 하나로 같은 순서와 간격으로 재생하는 기능이다.
- SCM(관리자)이 기록과 재생을 이끌고, SCC(참여자)가 히치, PTO, 밸브 같은 기능을 실행한다. active SCM은 하나뿐이고 SCC끼리는 직접 대화하지 않는다.
- PGN은 SCM→SCC 36352(0x8E00)와 SCC→SCM 36096(0x8D00) 두 개이고, 데이터 첫 바이트의 16진수 message code로 메시지를 가른다.
- SCC는 SCD로 자기 기능을 소개하고, 명령과 응답은 TAN으로 짝을 맞춘다.
- SCM과 SCC는 상태 머신으로 움직인다. SCC는 SCM 상태를 따라가고, 상태 메시지가 끊기면 양쪽 모두 안전한 쪽으로 물러난다.
- SCC는 능력 확인 → 저장된 SCD 확인 → 업로드 또는 로드 → 활성화를 거친 뒤 SCStateCommand Enabled를 받아야 참여한다.
:::

::: details 확인 문제
1. (개념) SC는 GPS가 헤드랜드를 알아채 자동으로 시퀀스를 실행하는 기능인가?
2. (개념) 트랙터 ECU는 히치와 PTO를 가진 SCC이고, 작업기 ECU는 밸브를 가진 SCC다. 재생 중 작업기 ECU가 트랙터 ECU에게 "PTO를 꺼라"라고 직접 보낼 수 있는가?
3. (메시지) PGN 0x8D00으로 Byte 1이 0x34인 메시지를 받았다. 누가 누구에게 보낸 무슨 메시지인가? 같은 0x34가 PGN 0x8E00으로 오면 무슨 메시지인가?
4. (상태) SCM이 Recording 상태일 때 운전자가 기록을 멈췄다. 그런데 히치를 올리는 기능이 아직 완료(10)를 보내지 않았다. SCM은 어느 상태로 가고, 그다음에는 무엇을 기다리는가? 그동안 새로 들어온 기능 시작 보고는 어떻게 되는가?
5. (초기화) SCM에 저장된 SCD가 없는 SCC가 시동 뒤 Enabled가 되기까지 쓰는 message code를 순서대로 적어라.

<strong>답 가이드</strong>
1. 아니다. SC는 운전자의 수동 조작을 기록했다가 운전자의 재생 지시로 되풀이한다. 재생을 시작하는 것도 운전자다.
2. 아니다. SCC끼리는 직접 통신하지 않는다. PTO를 끄는 명령은 SCM이 트랙터 ECU에 SCMasterExecutionCommand(`0x33`)로 보낸다. 다만 재생을 멈추는 SCClientAbort(`0x31`)는 전역 메시지라 다른 SCC도 받고, 받은 SCC는 Abort로 간다(SCC_S).
3. PGN 0x8D00은 SCC→SCM 방향이므로 SCC가 보낸 SCClientExecutionStatus(실행 시작·완료 보고)다. 같은 0x34가 PGN 0x8E00(SCM→SCC)으로 오면 SCM이 보낸 SCClientExecutionAcknowledgement(보고를 받았다는 확인)다. 요청과 응답이 같은 코드를 쓰므로 방향은 PGN으로 가른다.
4. Recording Completion으로 간다(SCM_G). 남은 기능이 모두 10(완료)이나 11(오류)을 보내면 Ready로 돌아간다(SCM_H). Recording Completion에서 새로 보고된 기능 시작은 무시한다.
5. SCClientStatus(`0x96`)로 Initialization을 한 번 알린 뒤 Disabled를 계속 보낸다 → SCMasterCapabilityRequest(`0x90`) → (VT에 SCCOP 업로드) → SCDVersionRequest(`0x01`), SCDConfigurationLabelRequest(`0x02`) → SCMasterMemoryRequest(`0x91`) → SCDTransfer(`0x03`) → SCDActivationCommand(`0x04`) → (선택: SCDStoreCommand `0x06`) → SCM이 보내는 SCStateCommand(`0x30`) Enabled를 받는다.
:::

## 다음 챕터

- 다음: [54장 Sequence Control 세부: SCD 바이트, 메시지, 오류 처리](/study/isobus/54-sequence-control-details)
