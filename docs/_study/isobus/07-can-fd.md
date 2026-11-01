---
title: "CAN FD"
description: "CAN FD가 나온 배경과 프레임 구조, 데이터 구간만 빠르게 보내는 원리를 익히고, ISOBUS가 CAN FD를 쓰지 않는 이유와 대신 쓰는 방법을 확인한다."
date: 2026-04-13
tags: [isobus, can, can-fd, automotive]
prev: /study/isobus/06-can-error
next: /study/isobus/08-j1939-intro
---

# CAN FD

::: info 학습 목표
- CAN FD가 나온 이유(Classic CAN의 8바이트, 1 Mbps 한계)를 설명할 수 있다.
- FDF, BRS, ESI 비트가 각각 무엇을 알리는지 설명할 수 있다.
- 한 프레임 안에서 속도가 바뀌는 듀얼 비트레이트 동작을 설명하고, 같은 데이터를 보낼 때 몇 배 빨라지는지 계산할 수 있다.
- Classic CAN 노드와 CAN FD 노드가 한 버스에 있을 때 생기는 문제를 설명할 수 있다.
- ISOBUS가 CAN FD를 금지한다는 것과, 8바이트보다 긴 데이터를 대신 어떻게 보내는지 말할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [4장 CAN 데이터 프레임](/study/isobus/04-can-data-frame), [6장 CAN 에러 처리](/study/isobus/06-can-error)
- 앞 장에서 본 말: DLC(데이터 길이 코드)와 비트 스터핑은 4장, 에러 프레임과 Error Active·Error Passive는 6장에서 봤다.
- 이 장에서 처음 나오는 말
  - CAN FD(CAN with Flexible Data-rate): 한 프레임에 최대 64바이트를 싣고, 데이터 구간만 더 빠르게 보내는 CAN의 확장판
  - Classic CAN: CAN FD와 구분하려고 기존 CAN(CAN 2.0)을 부르는 이름
  - 페이로드(payload): 프레임에 실린 실제 데이터 부분
  - Arbitration phase와 Data phase: CAN FD 프레임에서 보통 속도로 보내는 구간과 빠르게 보내는 구간
  - Nominal Bit Rate와 Data Bit Rate: 위 두 구간의 속도
  - FD Tolerant와 FD Active: CAN FD 프레임을 무시만 할 수 있는 노드와 직접 주고받을 수 있는 노드
:::

고속도로 요금소를 떠올려 보자. 차들은 요금소를 지날 때 모두 같은 속도로 줄을 서지만, 통과하고 나면 각자 빠르게 달린다. CAN FD도 비슷하다. 누가 버스를 쓸지 정하는 앞부분(중재)은 모든 노드가 따라올 수 있게 예전 속도로 보내고, 승자가 정해진 뒤 데이터 부분만 빠르게 보낸다. 짐칸(페이로드)도 8바이트에서 64바이트로 커졌다. 비유와 다른 점은, CAN FD는 프레임 끝(ACK 부분)에서 다시 보통 속도로 돌아온다는 것이다. 이 장에서는 CAN FD의 구조와 이득을 직접 계산해 보고, 마지막에 ISOBUS가 왜 CAN FD를 쓰지 않는지 본다.

## 1. CAN FD가 나온 이유

이 절에서는 기존 CAN의 두 가지 한계와, 그것을 넘으려고 CAN FD가 무엇을 바꿨는지 숫자로 본다.

### 기존 CAN의 한계

1986년 Bosch가 발표한 Classic CAN은 자동차 네트워크의 표준으로 자리 잡았다. 그러나 자동차 전자화가 가속화되면서 두 가지 근본적인 한계에 부딪혔다. 표의 비트레이트(bit rate)는 1초에 보내는 비트 수이고, 1 Mbps는 1초에 100만 비트다.

| 항목 | Classic CAN (2.0B) | 요구 사항 |
|---|---|---|
| 최대 페이로드 | 8 바이트 | 수십~수백 바이트 |
| 최대 비트레이트 | 1 Mbps | 수 Mbps 이상 |

<strong>한계 1: 8바이트 페이로드 상한</strong>

ECU 소프트웨어 업데이트(OTA, 무선으로 소프트웨어를 내려받아 바꾸는 것), 레이더/카메라 데이터, 고정밀 센서 융합 등 현대 자동차 기능은 한 프레임에 훨씬 많은 데이터를 담아야 한다. 8바이트로는 여러 프레임으로 쪼개서 보내야 하고, 이는 오버헤드와 응답 지연을 유발한다. 오버헤드는 데이터가 아닌 부분(ID, CRC, EOF 같은 포장)이다. 쪼갤수록 포장이 프레임마다 반복된다.

<strong>한계 2: 1 Mbps 비트레이트 상한</strong>

버스 길이와 전파 지연 특성상 Classic CAN은 이론적으로 1 Mbps가 최대다. ADAS(첨단 운전자 보조 시스템), 자율주행처럼 실시간성이 요구되는 애플리케이션에서는 이 속도로는 대역폭이 부족하다.

Bosch는 이 두 한계를 모두 해결하기 위해 <strong>2012년 CAN FD(CAN with Flexible Data-rate)</strong> 규격을 발표했다.

| | Classic CAN | CAN FD | 개선 |
|---|---|---|---|
| 페이로드 | 최대 8 bytes | 최대 64 bytes | 8배 |
| 비트레이트 | 최대 1 Mbps | Data phase 최대 8 Mbps | 8배 |

정리하면, CAN FD는 짐칸을 8배로 키우고 데이터 구간의 속도를 최대 8배로 올려 Classic CAN의 두 한계를 넘는다.

## 2. CAN FD의 구조

이 절에서는 CAN FD 프레임이 Classic CAN 프레임과 무엇이 다른지 본다. 앞부분 모양은 거의 같고, 제어 필드의 비트 몇 개와 데이터 길이 규칙이 달라진다.

### 새로 추가된 제어 비트

CAN FD는 Classic CAN 프레임의 제어 필드에 새 뜻을 가진 비트 세 개를 둔다. FDF는 Classic CAN에서 예약 비트(r1)였던 자리를 쓰고, BRS와 ESI는 새로 더해진다. 앞부분 구조가 그대로라 FD를 지원하는 컨트롤러는 Classic CAN 프레임도 그대로 주고받을 수 있다(하위 호환).

| 비트 | 이름 | 역할 |
|---|---|---|
| **FDF** | FD Format | 이 프레임이 CAN FD임을 표시 (FDF=1이면 CAN FD) |
| **BRS** | Bit Rate Switch | Data phase에서 비트레이트를 전환할지 결정 |
| **ESI** | Error State Indicator | 송신 노드의 에러 상태를 표시 (Error Active=0, Error Passive=1) |

쉽게 말하면 FDF는 "이건 CAN FD 프레임이다"라는 표시, BRS는 "지금부터 속도를 올린다"는 신호, ESI는 "나는 지금 Error Passive 상태다"라는 자기 신고다. Error Active와 Error Passive는 [6장](/study/isobus/06-can-error)에서 본 노드 상태다.

### CAN FD 프레임 구조

아래 그림은 CAN FD 프레임의 필드를 앞에서부터 늘어놓은 것이다. res는 예약 비트다.

![CAN FD 프레임 구조 개요: SOF+Arbitration ID(11/29bit), Control(IDE·FDF·res·BRS·ESI·DLC), Data(0~64byte), CRC(17 or 21bit), CRC Del+ACK, ACK Del+EOF](/images/study-isobus/07-canfd-frame-light.png)
![CAN FD 프레임 구조 개요: SOF+Arbitration ID(11/29bit), Control(IDE·FDF·res·BRS·ESI·DLC), Data(0~64byte), CRC(17 or 21bit), CRC Del+ACK, ACK Del+EOF](/images/study-isobus/07-canfd-frame-dark.png)

참고로 CAN FD의 CRC는 페이로드 길이에 따라 17비트(0~16바이트) 또는 21비트(20~64바이트)로 확장된다. 데이터가 길어지면 오류를 잡는 검사 값도 길어진다.

### 프레임 흐름

아래 그림은 송신 노드가 CAN FD 프레임 하나를 보내는 순서를 위에서 아래로 그린 것이다. 배경색은 그 순간의 속도 구간이다.

![CAN FD 프레임 흐름: 송신 노드가 SOF와 Arbitration ID를 표준 속도로 보내고(Arbitration phase, 모든 노드 같은 속도), FDF=1과 BRS=1로 CAN FD와 비트레이트 전환을 알린다. BRS 이후 고속으로 바뀌어 ESI, DLC, 64바이트 Data, 17/21비트 CRC를 보내고(Data phase), ACK와 EOF에서 표준 속도로 돌아온 뒤 수신 노드가 수신을 마친다](/images/study-isobus/07-canfd-frame-flow-light.png)
![CAN FD 프레임 흐름: 송신 노드가 SOF와 Arbitration ID를 표준 속도로 보내고(Arbitration phase, 모든 노드 같은 속도), FDF=1과 BRS=1로 CAN FD와 비트레이트 전환을 알린다. BRS 이후 고속으로 바뀌어 ESI, DLC, 64바이트 Data, 17/21비트 CRC를 보내고(Data phase), ACK와 EOF에서 표준 속도로 돌아온 뒤 수신 노드가 수신을 마친다](/images/study-isobus/07-canfd-frame-flow-dark.png)

1. SOF와 Arbitration ID를 표준 속도로 보낸다. 이 구간은 중재가 일어나는 곳이라 모든 노드가 같은 속도로 따라와야 한다.
2. FDF=1로 CAN FD 프레임임을, BRS=1로 속도 전환을 알린다.
3. BRS 다음부터 고속으로 바뀌어 ESI, DLC, Data, CRC를 보낸다.
4. ACK와 EOF는 다시 표준 속도로 보낸다. 여러 노드가 동시에 ACK를 써 넣어야 하기 때문이다.

### 최대 64바이트 페이로드

DLC(Data Length Code) 값과 실제 데이터 길이의 매핑이 CAN FD에서 확장되었다.

| DLC | 데이터 길이 |
|---|---|
| 0~8 | 0~8 bytes (Classic CAN과 동일) |
| 9 | 12 bytes |
| 10 | 16 bytes |
| 11 | 20 bytes |
| 12 | 24 bytes |
| 13 | 32 bytes |
| 14 | 48 bytes |
| 15 | 64 bytes |

DLC는 4비트라 0~15만 적을 수 있다. 그래서 9~15는 숫자 그대로의 길이가 아니라 정해진 길이(12~64바이트)를 가리킨다. 이 때문에 CAN FD 프레임의 데이터 길이는 표에 있는 값 가운데 하나여야 한다. 예를 들어 30바이트를 보내려면 32바이트 칸(DLC 13)을 쓰고 남는 2바이트를 채운다.

정리하면, CAN FD 프레임은 제어 비트 세 개(FDF, BRS, ESI)로 자기 형식과 속도 전환을 알리고, DLC 9~15로 최대 64바이트까지 싣는다.

## 3. 듀얼 비트레이트

이 절에서는 한 프레임 안에서 속도가 어떻게 바뀌는지 본다. 듀얼 비트레이트는 "한 프레임에 속도가 두 가지"라는 뜻이다.

### 두 개의 Phase

CAN FD 프레임은 <strong>두 개의 비트레이트 구간</strong>으로 나뉜다. 아래 그림은 각 구간에 어떤 필드가 들어가는지를 시간 순서로 그린 것이다.

![CAN FD 듀얼 비트레이트 구간: Arbitration phase(SOF + ID + Control, FDF/BRS 포함)는 Nominal Bit Rate(표준 속도), Data phase(ESI + DLC + Data + CRC)는 Data Bit Rate(고속), 마지막 복귀 구간(CRC Del + ACK + EOF)은 다시 Nominal Bit Rate다](/images/study-isobus/07-dual-bitrate-phases-light.png)
![CAN FD 듀얼 비트레이트 구간: Arbitration phase(SOF + ID + Control, FDF/BRS 포함)는 Nominal Bit Rate(표준 속도), Data phase(ESI + DLC + Data + CRC)는 Data Bit Rate(고속), 마지막 복귀 구간(CRC Del + ACK + EOF)은 다시 Nominal Bit Rate다](/images/study-isobus/07-dual-bitrate-phases-dark.png)

| 구간 | 포함 필드 | 속도 |
|---|---|---|
| **Arbitration phase** | SOF, ID, Control (FDF까지) | Nominal Bit Rate (통상 500 kbps) |
| **Data phase** | BRS 이후 ~ CRC | Data Bit Rate (2 ~ 8 Mbps) |

### BRS 비트가 전환 신호

`BRS=1`이면 BRS 비트 직후부터 Data phase 비트레이트로 전환된다. `BRS=0`이면 Data phase도 동일한 Nominal Bit Rate로 전송된다(속도 이점 없음). BRS=0이어도 64바이트까지 싣는 이점은 그대로 남는다.

![BRS 비트를 기점으로 Arbitration phase(500kbps)에서 Data phase(2~8Mbps)로 전환됐다가 EOF에서 500kbps로 복귀하는 타임라인](/images/study-isobus/07-brs-bitrate-switch-light.png)
![BRS 비트를 기점으로 Arbitration phase(500kbps)에서 Data phase(2~8Mbps)로 전환됐다가 EOF에서 500kbps로 복귀하는 타임라인](/images/study-isobus/07-brs-bitrate-switch-dark.png)

### 실제 처리량 비교 예시

아래는 두 방식의 유효 처리량(1초에 실제 데이터를 얼마나 나르는가)을 어림한 계산이다.

```
Classic CAN (8바이트, 1 Mbps):
  유효 데이터 처리량 ≈ 8 byte / ~130 bit(프레임 오버헤드) ≈ 492 kbps

CAN FD (64바이트, 4 Mbps Data phase):
  Arbitration phase: ~80 bit @ 500 kbps = 160 µs
  Data phase:        ~600 bit @ 4 Mbps  = 150 µs
  총 전송 시간 ≈ 310 µs → 약 2 Mbps 유효 처리량
```

첫 줄은 약 130비트짜리 프레임에 데이터 64비트(8바이트)를 실어 1 Mbps로 보내면 데이터만 따져 약 492 kbps가 나온다는 뜻이다. 이 블록의 비트 수와 처리량은 감을 잡기 위한 대략값이다. 예를 들어 64바이트(512비트)를 310 µs에 보내면 정확히는 약 1.65 Mbps다. 5절에서 필드를 하나씩 세어 정확히 다시 계산한다.

정리하면, CAN FD는 중재가 필요한 앞부분만 느리게 보내고 데이터는 빠르게 보내므로, 같은 시간에 훨씬 많은 데이터를 나른다.

## 4. CAN 2.0과의 호환성

이 절에서는 CAN FD 노드와 기존 Classic CAN 노드를 한 버스에 함께 연결할 수 있는지 본다. 결론부터 말하면, 전선은 같이 쓸 수 있지만 Classic CAN 노드가 CAN FD 프레임을 오류로 본다는 문제가 있다.

### 같은 버스에서 공존할 수 있는가?

CAN FD 노드와 Classic CAN 노드는 <strong>버스를 물리적으로 공유</strong>할 수 있다. 다만 CAN FD 프레임을 어떻게 다루느냐에 따라 노드는 세 종류로 나뉜다.

![같은 CAN 버스(물리 계층 공유)에 붙은 세 종류 노드: CAN FD Active 노드는 CAN FD 프레임을 송수신할 수 있고, CAN FD Tolerant 노드는 CAN FD 프레임을 에러 없이 무시하며, Classic CAN 노드는 CAN FD 프레임을 에러로 인식한다](/images/study-isobus/07-fd-node-types-light.png)
![같은 CAN 버스(물리 계층 공유)에 붙은 세 종류 노드: CAN FD Active 노드는 CAN FD 프레임을 송수신할 수 있고, CAN FD Tolerant 노드는 CAN FD 프레임을 에러 없이 무시하며, Classic CAN 노드는 CAN FD 프레임을 에러로 인식한다](/images/study-isobus/07-fd-node-types-dark.png)

| 노드 종류 | CAN FD 프레임 수신 | 에러 발생 |
|---|---|---|
| **FD Active** | 정상 처리 | 없음 |
| **FD Tolerant** | 무시(수신 후 폐기) | 없음 |
| **Classic CAN** | 인식 불가 | 에러 프레임 발생 |

Classic CAN 노드는 FD 프레임의 뒷부분(빨라진 속도, 늘어난 데이터와 CRC)을 해석하지 못해 오류로 판단하고 에러 프레임을 보낸다. 에러 프레임은 [6장](/study/isobus/06-can-error)에서 본 것처럼 그 프레임을 무효로 만든다.

::: warning 혼합 네트워크
Classic CAN 노드가 같은 버스에 존재하면 CAN FD 프레임 전송 시 에러 프레임을 생성한다. 따라서 <strong>혼합 네트워크</strong>에서는 CAN FD를 사용하지 않거나, 게이트웨이로 분리해야 한다.
:::

### ISOBUS와 CAN FD

현재 <strong>ISOBUS(ISO 11783)는 CAN 2.0B(29비트 확장 ID) 기반</strong>이다. 250 kbps의 비트레이트를 사용하며, CAN FD를 공식 채택하지 않았다. 아래는 ISOBUS 표준이 계층별로 어떻게 나뉘는지와 CAN FD를 둘러싼 업계 동향을 적은 것이다.

```
현재 ISOBUS 스택
  물리 계층: ISO 11783-2 (버스 전기 특성 등), 250 kbps
  데이터 링크: ISO 11783-3 (CAN 2.0B = Classical Extended Frame Format)
  상위 계층: ISO 11783-4~14

CAN FD 채택 동향
  - 농기계 데이터량 증가(정밀농업, 자율주행)로 수요 증가
  - ISO TC23/SC19 WG1에서 CAN FD 확장 검토 중
  - 일부 제조사는 자체 게이트웨이로 내부 CAN FD 망 구성
```

ISO TC23/SC19는 ISO 11783을 만든 곳(농업·임업 기계 기술위원회 TC23 아래의 농업 전자 분과위원회 SC19)이고, WG1은 그 아래 작업반이다. 다만 위 동향은 이 스터디의 원문으로 확인한 내용이 아니다(6절 참고). 6절에서 보듯 현재 판의 ISO 11783은 CAN FD를 채택하지 않은 정도가 아니라 쓰지 말라고 정한다.

::: tip 여기까지 정리 (1~4절)
- CAN FD는 2012년 Bosch가 발표, <strong>64바이트 페이로드</strong>와 <strong>최대 8 Mbps Data phase</strong>가 핵심 개선점이다.
- <strong>FDF</strong> 비트로 CAN FD 프레임임을 표시하고, <strong>BRS</strong> 비트로 Data phase 고속 전환, <strong>ESI</strong> 비트로 에러 상태를 나타낸다.
- Arbitration phase는 기존 속도(Nominal), Data phase만 고속(Data Bit Rate)으로 동작한다.
- Classic CAN 노드가 혼재하면 CAN FD 프레임을 에러로 처리하므로 혼합 네트워크는 격리가 필요하다.
- ISOBUS는 CAN 2.0B 기반이다. 업계에서 CAN FD 채택을 검토한다는 이야기가 있지만, 현재 판의 ISO 11783은 CAN FD를 쓰지 말라고 정한다(6절).
:::

## 5. 실제로 얼마나 빨라지나

앞 절까지는 CAN FD의 구조와 듀얼 비트레이트 원리를 개념으로 다뤘다. 여기서는 <strong>같은 64바이트 데이터</strong>를 Classic CAN과 CAN FD로 보낼 때 프레임 비트 수와 전송 시간을 끝까지 계산해 몇 배 차이가 나는지 확인한다.

### 1단계: 시나리오

이 단계에서는 무엇을 비교할지 정한다. 64바이트 데이터를 보내야 한다고 하자.

| 방식 | 처리 |
|---|---|
| Classic CAN | 최대 페이로드가 8바이트이므로 8바이트씩 <strong>8개 프레임</strong>으로 쪼갠다 |
| CAN FD | DLC 15가 64바이트에 대응하므로(2절의 DLC 표 참고) <strong>1개 프레임</strong>에 담긴다 |

ID는 두 방식 모두 ISOBUS 기준인 29비트 Extended ID를 쓴다고 가정한다.

### 2단계: Classic CAN 프레임의 비트 수 (8바이트 프레임 1개)

이 단계에서는 Classic CAN 프레임 하나가 몇 비트인지 필드별로 더한다. 필드별 비트 수는 [4장](/study/isobus/04-can-data-frame)의 Extended(29bit) 프레임 필드 표를 그대로 쓴다.

| 필드 | 비트 수 |
|---|---|
| SOF | 1 |
| Base ID | 11 |
| SRR | 1 |
| IDE | 1 |
| Extended ID | 18 |
| RTR | 1 |
| r1 | 1 |
| r0 | 1 |
| DLC | 4 |
| Data (8byte) | 64 |
| CRC | 15 |
| CRC 구분자 | 1 |
| ACK 슬롯 | 1 |
| ACK 구분자 | 1 |
| EOF | 7 |
| **합계** | **128** |

8바이트 프레임 1개가 128비트다. 8개 프레임을 보내야 하므로 <strong>128 × 8 = 1024비트</strong>가 필요하다.

### 3단계: CAN FD 프레임의 비트 수 (64바이트 프레임 1개)

이 단계에서는 CAN FD 프레임 하나의 비트를 세되, 어느 속도 구간에 속하는지까지 나눠서 센다. CAN FD 프레임은 Classic CAN 프레임의 r1 자리를 FDF로 쓰고, BRS·ESI 2비트가 더해진다(2절의 새로 추가된 제어 비트 표). Arbitration phase(SOF~BRS)와 Data phase(ESI~CRC)를 분리해야 다음 단계의 시간 계산이 맞는다.

| 구간 | 필드 | 비트 수 |
|---|---|---|
| Arbitration phase | SOF | 1 |
| Arbitration phase | Base ID | 11 |
| Arbitration phase | SRR | 1 |
| Arbitration phase | IDE | 1 |
| Arbitration phase | Extended ID | 18 |
| Arbitration phase | RTR 위치 비트 | 1 |
| Arbitration phase | FDF | 1 |
| Arbitration phase | r0 | 1 |
| Arbitration phase | BRS | 1 |
| **Arbitration phase 소계** | | **36** |
| Data phase | ESI | 1 |
| Data phase | DLC | 4 |
| Data phase | Data (64byte) | 512 |
| Data phase | CRC | 21 |
| **Data phase 소계** | | **538** |
| 복귀(Nominal) | CRC 구분자 | 1 |
| 복귀(Nominal) | ACK 슬롯 | 1 |
| 복귀(Nominal) | ACK 구분자 | 1 |
| 복귀(Nominal) | EOF | 7 |
| **복귀 소계** | | **10** |
| **전체 합계** | | **584** |

Classic CAN 표의 RTR, r1, r0 세 비트가 CAN FD에서는 RTR 위치 비트, FDF, r0이 된다. FDF가 r1 자리에 들어가므로 따로 세지 않는다.

CRC를 21비트로 잡은 이유는 페이로드가 64바이트라서다. <strong>0~16바이트는 17비트, 20~64바이트는 21비트</strong>라는 규칙이 2절에 이미 나와 있고, 64바이트는 후자에 속한다.

::: tip 핵심 통찰: 왜 phase를 나눠 세야 하나
CAN FD 프레임은 <strong>하나의 프레임 안에 두 개의 속도 구간</strong>이 있다. Arbitration phase(36비트)는 Nominal Bit Rate로, Data phase(538비트)는 Data Bit Rate로 흐른다. 이 둘을 합쳐서 "584비트를 한 속도로 나눴다"고 계산하면 틀린다. BRS 비트를 기점으로 <strong>구간별로 시간을 따로 구해 더해야</strong> 실제 전송 시간이 나온다.
:::

### 비트 스터핑을 어떻게 다뤘나 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

비트 스터핑은 데이터 값에 따라 늘었다 줄었다 하므로([4장의 비트 스터핑](/study/isobus/04-can-data-frame) 참고) 정확한 값은 실제 비트 패턴 없이는 알 수 없다. 이 절의 표와 시간 계산은 <strong>스터핑을 제외한 필드 비트 수(위 표의 128비트 / 584비트)</strong>를 기준으로 삼는다.

참고로 같은 비트가 계속 이어질 때(예: 전부 0)를 4장의 규칙 그대로 시뮬레이션하면, 같은 값이 5개 연속될 때마다 반대 비트가 하나씩 들어가 8바이트 프레임 1개에서 23비트, 64바이트 FD 프레임 1개에서 114비트(Arbitration 7 + Data 107)가 추가로 붙는다. 이 값도 8배(FD ≈ 4.86배) 수준으로 <strong>비율은 비슷하게 늘어나므로 아래 배수 비교의 결론은 크게 달라지지 않는다</strong>.

이 경우가 최악은 아니다. 끼워 넣은 스터프 비트도 다음 연속 비트 수에 함께 세어지므로, 비트 패턴에 따라 스터프 비트가 약 4비트마다 하나씩 들어갈 수 있다. 고전 CAN 8바이트 프레임의 최악 길이는 프레임 사이 쉬는 3비트를 포함해 표준 ID 135비트, 확장 ID 160비트로 알려져 있다(Davis 외, 2007년 CAN 응답 시간 분석 논문). 확장 ID 프레임이면 스터프 비트가 최대 29비트라는 뜻이다(160 = 128 + 29 + 3).

다만 CAN FD는 실제로는 Data phase에서 고정 스터핑(fixed stuff bit) 방식을 쓰는데, 이는 ISO 11898-1(CAN 자체를 정하는 국제 표준) 소관이라 이 스터디가 참고한 원문 묶음에 없어 정확한 규칙을 단정하지 않는다. 위 FD 수치는 4장의 동적 스터핑 규칙을 Data phase에도 동일하게 적용했다는 가정 하의 근사치일 뿐이다.

### 4단계: 전송 시간 계산

이 단계에서는 2·3단계의 비트 수를 각 구간의 속도로 나눠 시간을 구한다. Classic CAN은 500 kbps 단일 속도, CAN FD는 Arbitration phase 500 kbps + Data phase 2 Mbps로 계산한다. 500 kbps에서는 비트 하나가 2 µs, 2 Mbps에서는 0.5 µs다.

| 방식 | 구간 | 비트 수 | 속도 | 시간 |
|---|---|---|---|---|
| Classic CAN | 8프레임 전체 | 1024 | 500 kbps | 2048 µs |
| CAN FD | Arbitration phase | 36 | 500 kbps | 72 µs |
| CAN FD | Data phase | 538 | 2 Mbps | 269 µs |
| CAN FD | 복귀(Nominal) | 10 | 500 kbps | 20 µs |
| **CAN FD 합계** | | 584 | - | **361 µs** |

2048 µs ÷ 361 µs ≈ <strong>5.67배</strong> 빠르다. 아래 그림은 두 방식의 전송 시간을 같은 눈금에 그린 것이다.

![64바이트 전송 시간 비교: Classic CAN은 500 kbps로 8프레임을 보내 2048 µs가 걸리고, CAN FD는 500 kbps와 2 Mbps로 1프레임을 보내 중재 72 µs, 데이터 269 µs, 복귀 20 µs를 더한 361 µs가 걸린다](/images/study-isobus/07-64byte-time-compare-light.png)
![64바이트 전송 시간 비교: Classic CAN은 500 kbps로 8프레임을 보내 2048 µs가 걸리고, CAN FD는 500 kbps와 2 Mbps로 1프레임을 보내 중재 72 µs, 데이터 269 µs, 복귀 20 µs를 더한 361 µs가 걸린다](/images/study-isobus/07-64byte-time-compare-dark.png)

### 5단계: 결론, 몇 배 빨라지고 왜 payload가 클수록 유리한가

이 단계에서는 배수가 왜 속도 차이(4배)보다 큰지 오버헤드로 설명한다.

같은 64바이트를 보낼 때 CAN FD는 Classic CAN보다 <strong>약 5.67배</strong> 빠르다. 속도 자체는 Data phase에서 최대 4배(2 Mbps ÷ 500 kbps) 빨라졌을 뿐인데 배수가 이보다 큰 이유는, <strong>Classic CAN이 8프레임으로 쪼개지면서 SOF·ID·CRC·EOF 같은 오버헤드 비트를 8번 반복</strong>하기 때문이다.

오버헤드 비율로 보면 차이가 분명해진다. 오버헤드 비율은 프레임 전체 비트 가운데 데이터가 아닌 비트의 비율이다.

| 방식 | 페이로드 | 프레임 전체 비트 | 오버헤드 비율 |
|---|---|---|---|
| Classic CAN (8byte, 1프레임) | 64 bit | 128 bit | 50.0% |
| CAN FD (8byte, 1프레임) | 64 bit | 132 bit | 51.5% |
| CAN FD (64byte, 1프레임) | 512 bit | 584 bit | 12.3% |

같은 8바이트를 CAN FD로 보내면(DLC=8, 프레임 나눌 필요 없이 CRC만 17비트로 계산) 오버헤드 비율이 Classic CAN과 거의 같아서(51.5% vs 50.0%) 속도 이득이 <strong>약 1.90배</strong>에 그친다. 반면 페이로드가 64바이트로 커지면 오버헤드 비트 수(SOF~DLC, CRC, ACK, EOF 등)는 거의 그대로인데 페이로드가 512비트로 늘어나 오버헤드 비율이 12.3%까지 떨어진다. <strong>페이로드가 클수록 고정 오버헤드가 희석되면서 이득이 커지는 것</strong>이 CAN FD가 대용량 전송에서 특히 유리한 이유다.

아래 코드는 위 표들의 비트 수와 시간을 필드 상수로 다시 계산한다. 앞부분의 `same_bit_stuff_bits()`는 "비트 스터핑을 어떻게 다뤘나"에서 쓴, 같은 비트가 이어질 때의 스터프 비트 계산이다(최악의 경우가 아니다).

:::details 파이썬으로 검산해 보기
```python
def same_bit_stuff_bits(L):
    """CH4 §4 규칙(5비트 연속 시 반대 비트 삽입)을 같은 비트가 계속 이어지는 입력에 적용한 시뮬레이션(최악 케이스는 아니다)."""
    bits = []
    original_sent = 0
    stuff_count = 0
    cur = 0
    while original_sent < L:
        bits.append(cur)
        original_sent += 1
        if len(bits) >= 5 and len(set(bits[-5:])) == 1:
            stuff_val = 1 - bits[-1]
            bits.append(stuff_val)
            stuff_count += 1
    return stuff_count


# --- Classic CAN, Extended(29bit) ID, 8byte 프레임 1개 ---
SOF, BASE_ID, SRR, IDE, EXT_ID = 1, 11, 1, 1, 18
RTR, R1, R0, DLC = 1, 1, 1, 4
CTRL_AREA = SOF + BASE_ID + SRR + IDE + EXT_ID + RTR + R1 + R0 + DLC   # 39
CRC, CRC_DEL, ACK_SLOT, ACK_DEL, EOF = 15, 1, 1, 1, 7

DATA_BITS_CLASSIC = 8 * 8
classic_frame = CTRL_AREA + DATA_BITS_CLASSIC + CRC + CRC_DEL + ACK_SLOT + ACK_DEL + EOF
assert classic_frame == 128

n_frames = 8
classic_total_bits = classic_frame * n_frames                # 1024
classic_time_us = classic_total_bits * (1 / 500_000) * 1e6   # 2048.0

# --- CAN FD, Extended(29bit) ID, 64byte 프레임 1개 ---
FDF, BRS, ESI = 1, 1, 1
arb_bits = SOF + BASE_ID + SRR + IDE + EXT_ID + RTR + FDF + R0 + BRS   # 36 (FDF가 r1 자리를 쓴다)
DATA_BITS_FD = 64 * 8
CRC_FD = 21   # 20~64바이트 구간
data_phase_bits = ESI + DLC + DATA_BITS_FD + CRC_FD                        # 538
tail_bits = CRC_DEL + ACK_SLOT + ACK_DEL + EOF                             # 10

fd_frame = arb_bits + data_phase_bits + tail_bits
assert fd_frame == 584

arb_time_us = arb_bits * (1 / 500_000) * 1e6          # 72.0
data_time_us = data_phase_bits * (1 / 2_000_000) * 1e6  # 269.0
tail_time_us = tail_bits * (1 / 500_000) * 1e6         # 20.0
fd_time_us = arb_time_us + data_time_us + tail_time_us  # 361.0

print(classic_total_bits, classic_time_us)   # 1024 2048.0
print(fd_frame, fd_time_us)                  # 584 361.0
print(classic_time_us / fd_time_us)          # 5.6731...

# 오버헤드 비율 비교 (8byte 페이로드일 때는 이득이 왜 작은지)
data_phase_bits_8b = ESI + DLC + DATA_BITS_CLASSIC + 17   # CRC 17bit (0~16byte 구간)
fd_frame_8b = arb_bits + data_phase_bits_8b + tail_bits
print(fd_frame_8b)  # 132
print((classic_frame - DATA_BITS_CLASSIC) / classic_frame)   # 0.50  (Classic 8B 오버헤드 비율)
print((fd_frame_8b - DATA_BITS_CLASSIC) / fd_frame_8b)        # 0.515 (FD 8B 오버헤드 비율)
print((fd_frame - DATA_BITS_FD) / fd_frame)                   # 0.123 (FD 64B 오버헤드 비율)

# 8byte를 보낼 때의 시간 비교 (Classic 256 µs 대 FD)
fd_time_8b_us = (arb_bits + tail_bits) * (1 / 500_000) * 1e6 + data_phase_bits_8b * (1 / 2_000_000) * 1e6
print(fd_time_8b_us, classic_frame * (1 / 500_000) * 1e6 / fd_time_8b_us)   # 135.0 1.896...

# 같은 비트가 이어질 때의 스터프 비트 수: Classic 8B(SOF~CRC 118비트), FD 64B(중재, 데이터 구간)
print(same_bit_stuff_bits(CTRL_AREA + DATA_BITS_CLASSIC + CRC))                      # 23
print(same_bit_stuff_bits(arb_bits), same_bit_stuff_bits(data_phase_bits))        # 7 107
```

출력의 각 줄은 주석의 값과 같다. 특히 둘째 줄 `584 361.0`과 셋째 줄 `5.673...`이 위 표의 전체 비트 수, 전송 시간, 배수다.
:::

정리하면, 같은 64바이트를 보낼 때 CAN FD는 약 5.67배 빠르다. 속도 차이보다 배수가 큰 것은 Classic CAN이 프레임을 8번 나눠 보내며 포장(오버헤드)을 8번 반복하기 때문이다.

## 6. ISOBUS는 CAN FD를 쓰지 않는다

4절의 "ISOBUS와 CAN FD"는 ISOBUS가 CAN FD를 "공식 채택하지 않았다"고 적었다. 원문은 이보다 강하다. 채택하지 않은 정도가 아니라 <strong>쓰지 말라고 명시</strong>한다. 이 절에서는 그 내용과, 개발할 때 무엇을 확인해야 하는지 본다.

### 표준이 정한 내용

ISOBUS 표준 묶음(ISO 11783) 가운데 두 문서가 CAN FD를 금지한다. ISO 11783-1은 ISOBUS 네트워크 전체에 대한 공통 요구사항을 정하는 문서이고, ISO 11783-3은 CAN 프레임을 어떻게 쓰고 메시지를 어떻게 주고받는지 정하는 문서(데이터 링크 계층)다. 표의 shall은 반드시 지켜야 하는 규칙, shall not은 해서는 안 되는 일이다.

| 문서 | 정한 내용 |
|---|---|
| ISO 11783-1 | ISO 11783을 따르는 ECU는 ISO 11898-1:2015의 CAN Classical Extended Frame Format을 써야 한다(shall). CAN FD 프레임 형식은 쓰면 안 된다(shall not) |
| ISO 11783-3 | 어떤 FD 프레임 형식도 ISO 11783 네트워크에서 쓰면 안 된다(shall not). ISO 11783 컨트롤러는 CEFF를 써야 한다 |
| ISO 11783-3의 프레임 비트 표 | 프레임 비트 표의 ISO 11783 열에서 FDF 비트를 dominant(d)로 고정한다 |

CAN Classical Extended Frame Format(CEFF)은 29비트 ID를 쓰는 고전(Classic) CAN 프레임의 정식 이름이다. FDF는 2절 표의 FD Format 비트다. FDF가 1이어야 FD 프레임이므로, dominant(0) 고정은 고전 CAN 프레임만 쓴다는 뜻이다. FDF가 프레임의 어디에 있는지는 [4장 CAN 데이터 프레임](/study/isobus/04-can-data-frame)의 프레임 비트 그림(29비트 ID 기준 프레임 비트 34)에서 볼 수 있다.

### 왜 굳이 금지 문장을 넣었나

표준은 이유를 직접 적지 않는다. 다만 정황은 있다. ISOBUS가 따르는 CAN 규격(ISO 11898-1)의 최신판에는 고전 형식과 FD 형식이 함께 들어 있다. 그래서 "ISO 11898-1을 따른다"는 문장만으로는 FD 형식이 빠지지 않는다. ISOBUS 표준이 "FD 형식은 쓰지 않는다"를 따로 적은 것은 이 틈을 막으려는 것으로 보인다(추론). 판마다 달라진 문구는 이 절 끝의 메모에 적었다.

::: info 4절의 "CAN FD 채택 동향"에 대해
4절 코드 블록의 "ISO TC23/SC19 WG1에서 CAN FD 확장 검토 중" 같은 동향은 이 스터디의 원문 묶음(ISO 11783 각 파트)으로는 확인하지 못했다. 이 원문들이 말하는 것은 "현재 판의 ISO 11783 네트워크에서는 FD 형식을 쓰지 않는다"까지다.
:::

### 구현할 때 확인할 것 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

- <strong>FD 지원 CAN 컨트롤러의 모드</strong>: 요즘 SoC(프로세서와 주변 장치를 칩 하나에 담은 부품)의 CAN 컨트롤러는 FD를 지원하는 경우가 많다. ISOBUS 포트는 고전(Classical) 모드로 설정해 FDF가 recessive로 나가는 프레임을 만들지 않게 한다. 위 조항에서 바로 나오는 요구다.
- <strong>버스에 붙는 진단·로깅 도구</strong>: 도구도 ISOBUS 버스의 노드다. 4절 표처럼 고전 CAN 노드는 FD 프레임을 에러로 처리하므로, 도구의 FD 송신 기능은 꺼 둔다.
- <strong>8바이트를 넘는 데이터</strong>: FD의 64바이트 프레임 대신 TP(최대 1785바이트)와 ETP(최대 117 440 505바이트)로 나눠 보낸다. TP(Transport Protocol)와 ETP(Extended Transport Protocol)는 긴 데이터를 8바이트 프레임 여러 개로 나눠 보내는 방법이다. 지금 판 기준으로 둘 다 ISO 11783-3에서 정의를 찾으면 된다(문서마다 적힌 위치가 다른 점은 아래 메모 참고). 자세한 내용은 [15장 TP 기초](/study/isobus/15-tp-bam-cmdt)와 [17장 ETP](/study/isobus/17-etp)에서 다룬다.

정리하면, ISOBUS 장치는 CAN FD를 쓰면 안 된다. FD를 지원하는 컨트롤러도 고전 모드로 두고, 8바이트보다 긴 데이터는 TP와 ETP로 나눠 보낸다.

::: details 원문을 가진 독자를 위한 메모
위 "표준이 정한 내용" 표를 조항 번호와 함께 다시 적으면 다음과 같다. 마지막 줄은 본문 표에서 뺀 머리말 내용이다.

| 문서 | 조항 |
|---|---|
| ISO 11783-1:2017 6.3 | ISO 11783을 따르는 ECU는 ISO 11898-1:2015의 CAN Classical Extended Frame Format을 써야 한다(shall). CAN FD 프레임 형식은 쓰면 안 된다(shall not) |
| ISO 11783-3:2018 5.1.1 | 어떤 FD 프레임 형식도 ISO 11783 네트워크에서 쓰면 안 된다(shall not). ISO 11783 컨트롤러는 CEFF를 써야 한다 |
| ISO 11783-3:2018 Table 1 | 프레임 비트 표의 ISO 11783 열에서 FDF 비트를 dominant(d)로 고정한다 |
| ISO 11783-3:2018 머리말 | 4판의 주요 변경점으로 "ISO 11898-1 관련 문구 갱신(CAN Flexible Data Rate 사용 배제)"을 든다 |

<strong>왜 2018년판에서 문구를 고쳤나</strong>: Part 1(2017)이 인용하는 ISO 11898-1은 2015판이고, Part 3(2018)은 고전 CAN 형식을 CBFF·CEFF라고 부르면서 "어떤 FD 프레임 형식"도 금지한다. ISO 11898-1이 고전 형식과 FD 형식을 함께 담고 있다면 "ISO 11898-1을 따른다"는 문장만으로는 FD 형식이 배제되지 않는다. 2018년판이 문구를 고쳐 FD를 명시적으로 뺀 것은 이 틈을 막으려는 것으로 보인다(추론). Part 3 2018년판(4판)이 대체한 이전 판은 ISO 11783-3:2014다.

<strong>ETP 정의 위치</strong>: Part 1 6.3은 1785바이트까지의 TP를 Part 3이, 1786바이트부터 117 MB까지의 두 번째 전송 프로토콜을 Part 6이 정한다고 적는다. 그러나 2018년판 Part 3은 ETP를 5.11에 직접 정의하고, ISO 11783-6:2018 C.2.1도 1785바이트를 넘는 오브젝트 풀은 "ISO 11783-3에 정의된 ETP"로 보내라고 한다. 지금 기준으로 ETP의 정의는 Part 3에서 찾으면 된다.

5절 CAN FD 비트 수 표에서 FDF를 r1 자리로 본 근거는 Part 3 Table 1이다. 29비트 프레임의 비트 33이 RTR, 34가 FDF, 35가 r0이고 별도의 r1은 없다.
:::

<small>근거: ISO 11783-1 6.3, ISO 11783-3 머리말·5.1.1·5.11·Table 1, ISO 11783-6 C.2.1</small>

::: tip 핵심 정리
- CAN FD는 Classic CAN의 두 한계(한 프레임 8바이트, 최대 1 Mbps)를 넘으려고 나왔다. 한 프레임에 최대 64바이트를 싣고, 데이터 구간만 더 빠르게 보낸다.
- FDF는 "CAN FD 프레임"이라는 표시, BRS는 "데이터 구간에서 속도를 올린다"는 신호, ESI는 보낸 노드의 에러 상태다.
- 중재 구간과 끝부분(ACK, EOF)은 모든 노드가 따라올 수 있는 보통 속도로, 데이터 구간만 빠른 속도로 보낸다.
- 같은 64바이트를 보낼 때 CAN FD는 Classic CAN보다 약 5.67배 빠르다(500 kbps와 2 Mbps 기준). 페이로드가 클수록 오버헤드가 희석되어 이득이 커진다.
- Classic CAN 노드는 CAN FD 프레임을 오류로 처리하므로, 섞어 쓰려면 CAN FD를 쓰지 않거나 버스를 나눠야 한다.
- ISOBUS(ISO 11783)는 CAN FD를 쓰지 말라고 정한다. FD 지원 컨트롤러도 고전 모드로 두고, 8바이트를 넘는 데이터는 TP와 ETP로 나눠 보낸다.
:::

::: details 확인 문제
1. (개념) CAN FD 프레임의 FDF, BRS, ESI는 각각 무엇을 알리는가?
2. (계산) DLC가 13인 CAN FD 프레임에는 데이터가 몇 바이트 실리는가? 40바이트를 한 프레임에 보내려면 DLC를 얼마로 해야 하는가?
3. (개념) Classic CAN 노드가 섞인 버스에 CAN FD 프레임을 보내면 어떤 일이 생기는가?
4. (설명형) ISO 11783-1과 ISO 11783-3이 각각 CAN FD에 대해 무엇을 규정하는지, 그리고 ISO 11783-3의 프레임 비트 표가 이를 어떤 비트로 표현하는지 설명하라.
5. (설계형) SeamOS 단말에 쓸 SoC의 CAN 드라이버가 기본으로 FD 모드(데이터 구간 2 Mbps)를 켠다. ISOBUS 포트에 연결하기 전에 무엇을 바꿔야 하고, 4000바이트짜리 오브젝트 풀(VT 화면을 정의하는 데이터 묶음, [32장](/study/isobus/32-vt-object-pool-basics))은 어떤 방식으로 보내야 하는가?

**답 가이드**
1. FDF는 이 프레임이 CAN FD 형식이라는 표시(1이면 CAN FD)다. BRS는 데이터 구간에서 비트레이트를 올릴지 정한다(1이면 전환). ESI는 보낸 노드의 에러 상태(Error Active=0, Error Passive=1)를 알린다.
2. DLC 13은 32바이트다. 40바이트는 32바이트 칸에 들어가지 않으므로 DLC 14(48바이트)를 쓰고, 남는 8바이트는 채움 바이트가 된다.
3. Classic CAN 노드는 FD 프레임을 해석하지 못해 에러 프레임을 생성하고, FD 프레임은 무효가 된다. 따라서 혼합 네트워크에서는 CAN FD를 사용하지 않거나 게이트웨이로 분리해야 한다.
4. ISO 11783-1은 ECU가 ISO 11898-1:2015의 CEFF를 써야 하고 CAN FD 프레임 형식은 쓰면 안 된다고 정한다. ISO 11783-3은 어떤 FD 프레임 형식도 ISO 11783 네트워크에서 쓰면 안 된다고 정한다. 프레임 비트 표는 ISO 11783 열에서 FDF 비트를 dominant로 고정해 고전 프레임만 허용함을 나타낸다.
5. 드라이버를 고전 CAN 모드로 바꿔 FD 프레임을 송신하지 않게 한다(6절의 금지 조항). 4000바이트는 TP 한도 1785바이트를 넘으므로 ETP로 보낸다. 순서는 RTS(보내도 되는지 묻기) → CTS(보내라는 허락) → DPO(데이터 위치 알림)와 ETP.DT(데이터) 반복 → EOMA(끝 확인)다([17장](/study/isobus/17-etp)).
:::

## 다음 챕터

- 다음: [8장 SAE J1939 입문](/study/isobus/08-j1939-intro)
