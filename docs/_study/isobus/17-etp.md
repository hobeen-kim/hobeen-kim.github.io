---
title: "Extended Transport Protocol: 1,785바이트보다 큰 데이터"
description: "TP의 한계인 1,785바이트를 넘는 데이터를 ETP로 보내는 방법과, 패킷 번호를 이어 세는 DPO의 원리를 4000바이트 예제로 익힌다."
date: 2026-04-13
tags: [ISOBUS, J1939, Transport Protocol, ETP, DPO, VT]
prev: /study/isobus/16-tp-connection-rules
next: /study/isobus/18-isobus-overview
---

# Extended Transport Protocol: 1,785바이트보다 큰 데이터

::: info 학습 목표
- TP로는 1,785바이트까지만 보낼 수 있는 이유와 ETP가 필요한 상황을 설명할 수 있다.
- ETP와 TP의 공통점과 차이(PGN, 최대 크기, 1:1 연결 전용)를 비교할 수 있다.
- DPO가 오프셋을 알려 255를 넘는 패킷 번호를 세는 원리를 설명할 수 있다.
- ETP.CM 프레임을 바이트 단위로 읽고, ETP 로그에서 패킷 번호와 원본 바이트 위치를 계산할 수 있다.
- TP와 ETP의 Abort 사유 코드를 구별할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [15장 Transport Protocol 기초](/study/isobus/15-tp-bam-cmdt), [16장 TP 연결 규칙과 타이머](/study/isobus/16-tp-connection-rules)
- 이 장에서 처음 나오는 말
  - ETP(Extended Transport Protocol): 1,785바이트보다 긴 데이터를 보내는 TP의 확장판
  - ETP.CM, ETP.DT: ETP의 연결 관리 프레임과 데이터 프레임. TP.CM, TP.DT와 역할은 같고 PGN이 다르다
  - DPO(Data Packet Offset): 뒤따르는 데이터 패킷의 번호를 얼마부터 세는지 알려 주는 ETP.CM
  - 오프셋(offset): 기준점에서 얼마나 떨어져 있는지 나타내는 수
  - 오브젝트 풀: 작업기가 VT 화면에 띄울 화면 구성 전체를 담은 데이터
:::

번호표가 1번부터 255번까지만 있는 번호표 기계로 600명을 줄 세우려면 어떻게 할까? 255번까지 나눠 준 뒤 "이번 묶음은 번호에 255를 더해서 부릅니다"라고 알리고, 번호표를 1번부터 다시 쓰면 된다. TP는 시퀀스 번호가 1바이트(1~255)뿐이라 1,785바이트에서 멈추는데, ETP는 바로 이 방법으로 한계를 넘는다. 이 장은 ETP가 TP와 무엇이 같고 무엇이 다른지, 그리고 "더해서 읽을 값"을 알려 주는 DPO를 다룬다.

## 1. 왜 ETP가 필요한가

이 절에서는 TP의 크기 한계가 어디서 오는지, 그보다 큰 데이터는 무엇으로 보내는지 본다.

TP는 최대 **1785 바이트**(255 패킷 × 7 바이트)까지 전송할 수 있다. ISOBUS VT 오브젝트 풀처럼 더 큰 데이터를 전송하려면 <strong>ETP(Extended Transport Protocol)</strong>를 사용한다.

시퀀스 번호가 1바이트라 255까지만 셀 수 있고, 패킷 하나에 데이터가 7바이트씩 들어가기 때문이다([15장](/study/isobus/15-tp-bam-cmdt)). VT 오브젝트 풀은 작업기가 트랙터 화면(VT, Virtual Terminal)에 띄울 화면 구성 전체로, 수십 KB가 넘는 경우가 많다([32장](/study/isobus/32-vt-object-pool-basics)).

![데이터 크기에 따른 전송 방법. 0~8 byte는 CAN 프레임 1개(엔진 회전수 같은 값), 9~1,785 byte는 TP(BAM 또는 CMDT, 패킷 2~255개, DM1과 제품 식별 정보), 1,786~117,440,505 byte는 ETP(1:1 연결만, 패킷 256개 이상, VT 오브젝트 풀과 펌웨어)이며 경계는 8과 9, 1,785와 1,786 사이다](/images/study-isobus/17-size-map-light.png)
![데이터 크기에 따른 전송 방법. 0~8 byte는 CAN 프레임 1개(엔진 회전수 같은 값), 9~1,785 byte는 TP(BAM 또는 CMDT, 패킷 2~255개, DM1과 제품 식별 정보), 1,786~117,440,505 byte는 ETP(1:1 연결만, 패킷 256개 이상, VT 오브젝트 풀과 펌웨어)이며 경계는 8과 9, 1,785와 1,786 사이다](/images/study-isobus/17-size-map-dark.png)

그림은 데이터 크기에 따라 어떤 방법을 쓰는지 보여 준다. 띠의 길이는 실제 비율이 아니다. 8바이트 이하는 CAN 프레임 하나로, 9~1,785바이트는 TP(BAM 또는 CMDT)로, 1,786바이트부터는 ETP로 보낸다. ETP로 보낼 수 있는 최대 크기는 117,440,505바이트다.

ISO 11783-3(ISOBUS의 데이터 링크 계층을 정한 표준 문서, 이하 Part 3)은 TP를 SAE J1939와 똑같이 맞춰 두었지만, ETP는 J1939와 맞춘 기능이 아니라고 밝힌다. ETP는 J1939가 아니라 ISO 11783 쪽에서 정한 기능이라는 뜻이다.

### ETP vs TP 비교

| 항목 | TP | ETP |
|------|----|-----|
| CM PGN | TP.CM 60416 (0xEC00) | ETP.CM 51200 (0xC800) |
| DT PGN | TP.DT 60160 (0xEB00) | ETP.DT 50944 (0xC700) |
| 최대 데이터 크기 | 1785 byte | 117 440 505 byte ≒ 112 MB ((2^24 − 1) 패킷 × 7 byte) |
| 패킷당 데이터 | 7 byte | 7 byte |
| 연결 방식 | BAM 또는 CMDT | CMDT 전용 |

CM은 연결 관리(Connection Management), DT는 데이터 전송(Data Transfer) 프레임이다. ETP.CM의 PGN `0xC800`은 10진수로 51200, ETP.DT의 `0xC700`은 50944다. 2^24 − 1 = 16,777,215는 3바이트로 셀 수 있는 가장 큰 수이고, ETP는 패킷 번호를 3바이트로 센다. ≒는 "거의 같다"는 뜻이다.

ETP는 <strong>CMDT 전용</strong>이다. BAM 방식의 ETP는 존재하지 않는다. 이는 대용량 데이터 전송 시 흐름 제어 없이는 수신 버퍼 오버플로가 발생할 수 있기 때문이다.

정리하면 TP의 한계는 1바이트 시퀀스 번호에서 오고, 그보다 큰 데이터는 1:1 연결만 쓰는 ETP로 보낸다.

<small>근거: ISO 11783-3 5.10.1, 5.10.2.2, 5.11.2, 5.11.3, 5.11.5.2, 5.11.6</small>

## 2. ETP의 흐름

이 절에서는 ETP로 큰 데이터를 보낼 때 프레임이 오가는 순서를 본다. TP의 CMDT와 거의 같고, CTS와 데이터 사이에 DPO가 하나 끼어든다는 점만 다르다.

### ETP CMDT 흐름

![ETP 흐름. 송신 ECU가 ETP.CM_RTS(PGN 51200, 총 크기 50000 byte, 오브젝트 풀 PGN)를 보내고 수신 ECU가 ETP.CM_CTS(허용 패킷 수 255, 시작 패킷 1)로 답한다. 255 패킷씩 반복하는 구간에서는 ETP.CM_DPO로 기준 오프셋을 선언한 뒤 ETP.DT #1, #2부터 #255(PGN 50944)를 보내고, 수신 ECU가 ETP.CM_CTS(허용 패킷 수 255, 시작 패킷 256)로 다음 구간을 허락한다. 끝나면 수신 ECU가 ETP.CM_EndOfMsgACK(PGN 51200)를 보낸다](/images/study-isobus/17-etp-flow-light.png)
![ETP 흐름. 송신 ECU가 ETP.CM_RTS(PGN 51200, 총 크기 50000 byte, 오브젝트 풀 PGN)를 보내고 수신 ECU가 ETP.CM_CTS(허용 패킷 수 255, 시작 패킷 1)로 답한다. 255 패킷씩 반복하는 구간에서는 ETP.CM_DPO로 기준 오프셋을 선언한 뒤 ETP.DT #1, #2부터 #255(PGN 50944)를 보내고, 수신 ECU가 ETP.CM_CTS(허용 패킷 수 255, 시작 패킷 256)로 다음 구간을 허락한다. 끝나면 수신 ECU가 ETP.CM_EndOfMsgACK(PGN 51200)를 보낸다](/images/study-isobus/17-etp-flow-dark.png)

1. 송신 ECU가 ETP.CM_RTS로 "50000바이트를 보내고 싶다"고 묻는다. ECU(Electronic Control Unit)는 전자 제어 장치다.
2. 수신 ECU가 ETP.CM_CTS로 "1번 패킷부터 255개"를 허락한다.
3. 송신 ECU는 ETP.CM_DPO로 이번 묶음의 기준 오프셋을 먼저 알리고, ETP.DT를 시퀀스 번호 1부터 255까지 보낸다.
4. 수신 ECU가 다음 CTS로 "256번 패킷부터 255개"를 허락하면, 송신 ECU는 다시 DPO와 ETP.DT를 보낸다. 데이터가 끝날 때까지 되풀이한다.
5. 다 받으면 수신 ECU가 ETP.CM_EndOfMsgACK로 완료를 알린다.

ETP는 제어 메시지가 하나 더 있다. <strong>ETP.CM_DPO(Data Packet Offset, Control Byte 22)</strong>다. ETP.DT의 시퀀스 번호는 TP와 같은 1바이트(1~255)뿐이므로, 송신 측이 CTS 묶음마다 DPO로 <strong>기준 오프셋</strong>을 먼저 선언하고 그 뒤 ETP.DT를 보낸다. 실제 패킷 번호는 `DPO 오프셋 + ETP.DT 시퀀스 번호`로 계산되며, DPO 다음의 첫 ETP.DT는 항상 시퀀스 번호 1이다. 참고로 수신 측이 CTS(0)(hold)를 보낸 경우에는 DPO로 응답하지 않는다.

### ISOBUS VT 오브젝트 풀 전송

VT(Virtual Terminal)에 화면을 표시하려면 오브젝트 풀을 전송해야 한다. 오브젝트 풀은 수십 KB를 초과하는 경우가 많으므로 ETP를 통해 전송된다.

```
작업기 ECU → VT:
  ETP.CM_RTS (오브젝트 풀 PGN, 총 크기)
  → ETP.CM_CTS
  → ETP.CM_DPO + ETP.DT × N (CTS 묶음마다 반복)
  → ETP.CM_EndOfMsgACK
  → End of Object Pool 메시지 (ISO 11783-6:2018 C.2.4)
```

위 순서에서 ETP가 맡는 부분은 RTS부터 EndOfMsgACK까지다. 마지막 End of Object Pool은 ETP 메시지가 아니라 VT 쪽 메시지로, 오브젝트 풀을 다 보냈다고 VT에 알린다. 풀 전송 과정은 [32장](/study/isobus/32-vt-object-pool-basics)에서, 이 메시지에 대한 VT의 응답을 읽는 법은 [35장](/study/isobus/35-vt-pool-transfer-charset)에서 다룬다. ISO 11783-6은 VT를 정한 표준 문서다.

정리하면 ETP는 RTS, CTS, (DPO와 데이터) 반복, EndOfMsgACK 순서로 흐르고, 묶음마다 DPO가 먼저 나간다.

<small>근거: ISO 11783-3 5.11.4.1, 5.11.5.4, 5.11.6; ISO 11783-6 C.2.4</small>

## 3. ETP가 TP에서 물려받은 것과 달라진 것

이 절에서는 ETP의 규칙이 TP와 어떻게 이어지는지와, ETP.CM 프레임의 바이트 배치를 본다.

### ETP는 TP를 기반으로 한다

Part 3은 TP 규칙이 ETP 요구사항의 기반이라고 밝힌다. TP의 규칙은 ETP에도 그대로 적용되고 ETP 메시지로 구현한다. 예를 들어 TP.CM_CTS에 대한 요구는 ETP.CM_CTS에 대한 요구다. 타이밍도 TP와 같다. 그래서 [16장](/study/isobus/16-tp-connection-rules)의 성립·hold·닫힘·재전송 규칙과 타이머는 ETP에도 적용된다. 모든 ETP.CM 메시지는 특정 목적지 메시지이고 BAM 형태는 없다.

### ETP.CM 바이트 배치

ETP.CM은 PGN 51200(`0x00C800`), PF 200, 기본 Priority 7이고, ETP.DT는 PGN 50944(`0x00C700`), PF 199, 기본 Priority 7이다. PF(PDU Format)는 CAN ID 안에서 메시지 종류를 가르는 바이트이고, Priority는 여러 장치가 동시에 보낼 때 누가 먼저 버스를 쓸지 정하는 우선순위(0이 가장 높다)다([9장](/study/isobus/09-j1939-message)).

![ETP.CM 5종의 8바이트 배치: RTS(20)는 Byte 2~5 보낼 바이트 수, CTS(21)는 Byte 2 패킷 수 0~255와 Byte 3~5 다음 패킷 번호, DPO(22)는 Byte 2 패킷 수 1~255와 Byte 3~5 오프셋(CTS 다음 번호 - 1), EOMA(23)는 Byte 2~5 받은 바이트 수, Abort(255)는 Byte 2 사유와 Byte 3~5 FF, 모두 Byte 6~8은 운반하는 PGN](/images/study-isobus/11-etp-cm-layout-light.png)
![ETP.CM 5종의 8바이트 배치: RTS(20)는 Byte 2~5 보낼 바이트 수, CTS(21)는 Byte 2 패킷 수 0~255와 Byte 3~5 다음 패킷 번호, DPO(22)는 Byte 2 패킷 수 1~255와 Byte 3~5 오프셋(CTS 다음 번호 - 1), EOMA(23)는 Byte 2~5 받은 바이트 수, Abort(255)는 Byte 2 사유와 Byte 3~5 FF, 모두 Byte 6~8은 운반하는 PGN](/images/study-isobus/11-etp-cm-layout-dark.png)

그림의 한 줄이 메시지 하나이고, 칸은 Byte 1부터 Byte 8까지다. 맨 앞 숫자는 Control Byte다. 여러 바이트를 차지하는 값은 TP처럼 리틀 엔디언(낮은 자리 바이트가 먼저)으로 적는다. 예를 들어 RTS의 Byte 2~5가 `A0 0F 00 00`이면 `0x00000FA0` = 4000바이트다. EOMA는 EndOfMsgACK의 ETP 쪽 이름이다.

TP.CM과 비교하면 차이가 분명하다.

- <strong>RTS에 패킷 수 필드가 없다.</strong> TP.CM_RTS는 총 패킷 수(Byte 4)와 CTS당 최대 패킷 수(Byte 5)를 갖지만, ETP.CM_RTS는 Byte 2~5 전부가 바이트 수다. 송신 측이 CTS 크기를 제한하는 장치가 없으므로 CTS의 패킷 수(0~255)는 수신 측이 정한다.
- <strong>CTS의 다음 패킷 번호가 3바이트다.</strong> 패킷 번호는 1 ~ 16 777 215(2²⁴ − 1)까지 갈 수 있다. 다만 CTS의 패킷 수 + 다음 패킷 번호 − 1이 16 777 215를 넘으면 안 된다.
- <strong>DPO(Data Packet Offset)가 새로 있다.</strong> 시퀀스 번호는 TP.DT와 같은 1바이트(1~255)이므로, 송신 측은 CTS 구간마다 DPO로 기준 오프셋을 먼저 알린다.

최대 메시지 크기는 (2²⁴ − 1) 패킷 × 7바이트 = 117 440 505바이트다. 십진 접두어로 약 117 MB, 이진 단위로 약 112 MiB다. 십진 접두어 M은 100만(10⁶), 이진 단위 Mi는 1,048,576(2²⁰)을 뜻한다. ISO 11783-1(ISOBUS 전체의 공통 사항을 정한 표준 문서)이 "117 Megabyte"라고 쓰고 1절 표가 "≒ 112 MB"라고 쓴 것은 같은 값을 다른 단위로 적은 것이다.

::: warning 표준 안의 차이: ETP.CM의 값 범위 목록
Part 3의 ETP.CM 값 범위 목록은 "Number of packets that can be sent"(보낼 수 있는 패킷 수)를 256 ~ 16 777 215(3바이트, 0~255 불허)로, "Total number of packets"(총 패킷 수)도 같은 범위로 적는다. 그런데 바로 아래 ETP.CM_CTS 배치는 패킷 수를 Byte 2 하나(0 또는 1~255)로 정의하고, ETP.CM_RTS에는 총 패킷 수 필드가 아예 없다. 구현은 메시지 배치(Byte 2 = 0~255)를 따라야 한다. 값 범위 목록을 그대로 검사 코드로 옮기면 정상적인 CTS를 전부 거절하게 된다.
:::

::: details 원문을 가진 독자를 위한 메모
- ETP.CM의 값 범위 목록과 다섯 메시지의 배치는 둘 다 ISO 11783-3:2018 5.11.5.2에 있다. 패킷 수 + 다음 패킷 번호 − 1의 상한은 그 절의 NOTE 1이다.
- "117 Megabyte" 표기는 ISO 11783-1 6.3에 있다.
:::

정리하면 ETP는 TP의 규칙과 타이밍을 그대로 쓰되, 패킷 번호를 3바이트로 늘리고 DPO를 더했다.

<small>근거: ISO 11783-3 5.11.1, 5.11.3, 5.11.4.1, 5.11.5.2, 5.11.6; ISO 11783-1 6.3</small>

## 4. DPO: 255를 넘는 패킷 번호 세기

이 절에서는 ETP의 핵심인 DPO가 패킷 번호를 어떻게 이어 세는지 본다.

쉽게 말하면 DPO는 도입에서 본 "이번 묶음은 번호에 255를 더해서 부릅니다"라는 안내다. ETP.DT의 시퀀스 번호는 CTS 묶음마다 1부터 다시 시작하고, 실제 패킷 번호는 DPO가 알려 준 오프셋에 시퀀스 번호를 더해 얻는다. 예를 들어 오프셋이 255이고 시퀀스 번호가 1이면 실제로는 256번 패킷이다. n번 패킷은 원본의 (n − 1) × 7 + 1번째 바이트부터 담으므로, 256번 패킷은 원본의 1786번째 바이트부터 7바이트를 담는다.

### DPO의 동작

- DPO는 한 CTS 구간 안에서 패킷 번호가 매겨지는 기준을 정한다. 실제 패킷 번호 = DPO의 오프셋 + ETP.DT의 시퀀스 번호다.
- DPO 다음의 첫 ETP.DT는 언제나 시퀀스 번호 1이다.
- DPO의 오프셋은 대응하는 CTS의 다음 패킷 번호보다 항상 1 작다. 오프셋 + 시퀀스 번호는 16 777 215를 넘으면 안 된다.
- DPO의 패킷 수(Byte 2)는 CTS의 Byte 2 이하여야 한다(shall, 반드시 지켜야 하는 규칙). 더 작으면 수신 측은 DPO가 정의한 데이터 블록과 뒤따르는 ETP.DT를 받도록 세션을 조정해야 한다.
- CTS(0)에는 DPO로 답하지 않는다.
- 수신 측은 ETP.CM_RTS를 받으면 자원을 판단해 패킷 수 0의 CTS로 연결을 연 채 기다리게 하거나, Abort로 닫을 수 있다.

오프셋이 "CTS의 다음 패킷 번호 − 1"인 것은 시퀀스 번호가 1부터 시작하기 때문이다. CTS가 "256번부터"를 허락하면 DPO 오프셋은 255이고, 첫 ETP.DT의 시퀀스 번호 1을 더하면 정확히 256번이 된다.

정리하면 DPO 오프셋 + 시퀀스 번호가 실제 패킷 번호이고, 수신 측이 DPO를 놓치면 패킷을 엉뚱한 자리에 놓게 된다(6절에서 실제 바이트로 확인한다).

<small>근거: ISO 11783-3 5.11.4.1, 5.11.5.2, 5.11.5.4, 5.11.5.5, 5.11.5.7, 5.11.6</small>

## 5. ETP의 Abort 사유

이 절에서는 ETP의 Abort 사유 코드를 본다. 숫자가 TP와 겹치지만 9번부터는 뜻이 다르므로 로그를 읽을 때 주의해야 한다.

### ETP의 Abort 사유

ETP의 Abort는 ETP 전용 사유 표를 쓴다. 1~8은 TP와 같지만 <strong>9부터는 의미가 다르다</strong>.

| 코드 | 의미 |
|---|---|
| 1~8 | TP의 사유 표([16장](/study/isobus/16-tp-connection-rules))와 같다 |
| 9 | 예기치 않은 EDPO(DPO) 패킷 |
| 10 | DPO의 PGN이 잘못됨 |
| 11 | DPO의 패킷 수가 CTS보다 큼 |
| 12 | 잘못된 DPO 오프셋 |
| 13 | 폐기(deprecated). 대신 250 사용 |
| 14 | CTS의 PGN이 잘못됨 |
| 15 | CTS가 요청한 패킷이 메시지 크기를 넘음 |
| 250 | 그 밖의 사유 |
| 251~255 | ISO 11783-7 정의를 따름 |

EDPO(Extended Data Packet Offset)는 표준이 DPO를 부르는 다른 이름이다. ISO 11783-7은 트랙터와 작업기 사이의 응용 메시지를 정한 표준 문서다.

0과 16~249는 예약이다. TP의 사유 9(총 크기 1785 초과)는 ETP에 대응 코드가 없고, 같은 숫자 9가 ETP에서는 "예기치 않은 DPO"다. 그래서 Abort 해석기는 사유 코드를 보기 전에 그 Abort가 TP.CM(60416)으로 왔는지 ETP.CM(51200)으로 왔는지 먼저 갈라야 한다.

::: warning 표준 안의 차이: "표에 없는 사유"의 코드
Part 3 본문은 ETP 사유 표에 없는 사유면 코드 254를 쓰라고 적는다. 그런데 사유 표 자체는 250을 "그 밖의 사유"로 정의하고, 13번도 "250을 쓰라"고 안내한다. 254는 표에서 251~255(ISO 11783-7 정의) 범위에 든다. 표 쪽(250)이 TP의 사유 표와도 일관되므로 송신은 250으로 하고, 수신 측은 254도 "그 밖의 사유"로 받아들이는 편이 안전하다(추론).
:::

::: details 원문을 가진 독자를 위한 메모
- ETP 사유 표는 ISO 11783-3:2018 Table 9, TP 사유 표는 Table 8이다.
- 코드 254를 쓰라는 문장은 5.11.5.7 본문에 있다.
:::

정리하면 ETP의 Abort 사유는 8번까지만 TP와 같다. 사유 숫자를 읽기 전에 TP.CM인지 ETP.CM인지부터 확인한다.

<small>근거: ISO 11783-3 5.11.5.7, Table 8, Table 9</small>

## 6. 4000바이트를 ETP로 보내 보기

이 절에서는 4000바이트 오브젝트 풀을 실제로 ETP로 보낼 때 버스에 흐르는 프레임을 바이트 단위로 따라간다.

[15장](/study/isobus/15-tp-bam-cmdt)에서 20바이트를 BAM과 CMDT로 보낸 작업기 ECU(SA `0x23`, 10진수 35)가 이번에는 4000바이트짜리 오브젝트 풀을 VT로 보낸다. VT의 주소는 `0x26`(=38)이라고 가정한다. SA(Source Address)는 보내는 쪽 주소, DA(Destination Address)는 받는 쪽 주소다.

### 설정

- 운반할 PGN: ECU to VT(PGN 59136 = `0x00E700`). ISO 11783-6은 오브젝트 풀 전송에 특정 목적지 메시지와 연결 관리를 쓰고, 1785바이트를 넘으면 Part 3의 ETP를 쓰라고 정한다.
- 데이터 Byte 1: `0x11`(=17, Object pool transfer). 나머지 3999바이트는 검산용 패턴이다. n번째 바이트(1부터 셈)의 값을 (n − 1)의 하위 8비트, 즉 (n − 1)을 256으로 나눈 나머지로 채워, 바이트 값만 보고도 원본 위치를 되짚을 수 있게 했다.
- 패킷 수: ceil(4000 ÷ 7) = 572개. ceil은 올림이다. 마지막 패킷은 3바이트와 FF 4개다.
- ID: ETP.CM은 Priority 7, PF `0xC8`(=200)이므로 ECU → VT가 `0x1CC82623`, VT → ECU가 `0x1CC82326`이다. ETP.DT는 `0x1CC72623`이다. ECU to VT 메시지의 기본 Priority는 5지만, 전송 프레임에는 ETP의 Priority 7이 붙는다.

ID `0x1CC82623`을 나눠 읽으면, 맨 앞 `1C`에 Priority 7이 들어 있고 `C8`은 PF(ETP.CM), `26`은 받는 쪽 주소(DA, VT), `23`은 보내는 쪽 주소(SA, ECU)다([9장](/study/isobus/09-j1939-message)).

VT는 CTS 하나에 255패킷씩 받기로 하고, 첫 구간 뒤에 객체를 해석하느라 한 번 hold한다.

![4000바이트 572패킷이 CTS 창 세 개(패킷 1~255는 CTS(255,1)·DPO(255,0), 256~510은 CTS(255,256)·DPO(255,255), 511~572는 CTS(62,511)·DPO(62,510))로 나뉘고 각 창에서 seq 1부터 다시 세며 실제 패킷은 오프셋 + seq, 첫 창 뒤에 CTS(0) hold가 있고 바이트 경계는 1785|1786, 3570|3571, 4000인 그림](/images/study-isobus/11-etp-dpo-windows-light.png)
![4000바이트 572패킷이 CTS 창 세 개(패킷 1~255는 CTS(255,1)·DPO(255,0), 256~510은 CTS(255,256)·DPO(255,255), 511~572는 CTS(62,511)·DPO(62,510))로 나뉘고 각 창에서 seq 1부터 다시 세며 실제 패킷은 오프셋 + seq, 첫 창 뒤에 CTS(0) hold가 있고 바이트 경계는 1785|1786, 3570|3571, 4000인 그림](/images/study-isobus/11-etp-dpo-windows-dark.png)

띠 하나가 CTS 구간(창) 하나다. 띠 위의 글자는 그 구간을 연 CTS와 DPO의 (패킷 수, 번호) 값이고, 띠 아래 글자는 시퀀스 번호의 범위와 실제 패킷 번호를 구하는 식이다. 맨 아래 눈금은 구간 경계에 해당하는 원본 바이트 위치다.

### 바이트로 따라가기

표의 #은 프레임 순서, ID는 29비트 CAN ID, 데이터는 8바이트다. "…" 줄은 같은 형식의 프레임을 생략한 것이다.

| # | ID | 데이터 | 해석 |
|---|---|---|---|
| 1 | `1CC82623` | `14 A0 0F 00 00 00 E7 00` | ETP.CM_RTS. control 20, 크기 `A0 0F 00 00` = 4000, PGN 59136 |
| 2 | `1CC82326` | `15 FF 01 00 00 00 E7 00` | ETP.CM_CTS. 255패킷, 다음 패킷 1 |
| 3 | `1CC82623` | `16 FF 00 00 00 00 E7 00` | ETP.CM_DPO. 255패킷, 오프셋 0 |
| 4 | `1CC72623` | `01 11 01 02 03 04 05 06` | DT seq 1 = 패킷 1 (원본 1~7바이트) |
| | | … | DT seq 2~254 |
| 5 | `1CC72623` | `FF F2 F3 F4 F5 F6 F7 F8` | DT seq 255 = 패킷 255 (원본 1779~1785바이트) |
| 6 | `1CC82326` | `15 00 FF FF FF 00 E7 00` | CTS(0) hold. 나머지 필드는 FF |
| 7 | `1CC82326` | `15 FF 00 01 00 00 E7 00` | CTS. 255패킷, 다음 패킷 `00 01 00` = 256 |
| 8 | `1CC82623` | `16 FF FF 00 00 00 E7 00` | DPO. 오프셋 `FF 00 00` = 255 |
| 9 | `1CC72623` | `01 F9 FA FB FC FD FE FF` | DT seq 1 = 패킷 256 (원본 1786~1792바이트) |
| | | … | DT seq 2~254 |
| 10 | `1CC72623` | `FF EB EC ED EE EF F0 F1` | DT seq 255 = 패킷 510 (원본 3564~3570바이트) |
| 11 | `1CC82326` | `15 3E FF 01 00 00 E7 00` | CTS. 62패킷, 다음 패킷 `FF 01 00` = 511 |
| 12 | `1CC82623` | `16 3E FE 01 00 00 E7 00` | DPO. 62패킷, 오프셋 `FE 01 00` = 510 |
| 13 | `1CC72623` | `01 F2 F3 F4 F5 F6 F7 F8` | DT seq 1 = 패킷 511 (원본 3571~3577바이트) |
| | | … | DT seq 2~61 |
| 14 | `1CC72623` | `3E 9D 9E 9F FF FF FF FF` | DT seq 62 = 패킷 572 (원본 3998~4000바이트 + FF) |
| 15 | `1CC82326` | `17 A0 0F 00 00 00 E7 00` | ETP.CM_EOMA. 받은 바이트 4000 |

12번 행의 DPO `16 3E FE 01 00 00 E7 00`을 바이트별로 읽어 보자.

1. Byte 1 `16` = 22: DPO다.
2. Byte 2 `3E` = 62: 이 오프셋을 적용할 패킷이 62개다.
3. Byte 3~5 `FE 01 00`: 리틀 엔디언이므로 `0x0001FE` = 510이 오프셋이다.
4. Byte 6~8 `00 E7 00`: `0x00E700` = 59136, 나르는 PGN(ECU to VT)이다.

짚어 볼 점은 다음과 같다.

- 9번 행의 데이터 `F9 FA …`는 패턴상 원본 1786번째 바이트부터다. 시퀀스 번호는 다시 1이지만 DPO 오프셋 255를 더해 패킷 256이 되고, 바이트 위치는 (256 − 1) × 7 + 1 = 1786이다. 수신 측이 DPO를 놓치면 이 프레임을 패킷 1 자리에 덮어써 데이터가 조용히 깨진다.
- 마지막 CTS는 255가 아니라 남은 62패킷만 요청한다. 255를 요청하면 메시지 크기를 넘는 요청이 되고, 송신 측은 사유 15(CTS가 요청한 패킷이 메시지 크기 초과)로 Abort할 수 있다.
- hold 뒤의 CTS(7번 행)에는 DPO가 따르지만 hold 자체(6번 행)에는 따르지 않는다. hold가 0.5 s를 넘게 이어지면 VT는 Th마다 CTS(0)를 다시 보내야 하고, ECU는 T4(1.05 s) 안에 다음 CTS가 없으면 닫는다(TP 규칙이 그대로 적용된다).
- 전체 프레임은 581개(CM 9개 + DT 572개)다. 16장에서 본 표준 권고(CTS당 16패킷)대로 CTS당 16패킷을 쓰면 CTS 구간이 36개로 늘어 CM 프레임이 74개(RTS 1 + CTS 36 + DPO 36 + EOMA 1, hold 제외)가 된다. 오버헤드는 늘지만 재전송 단위와 한 번에 버스를 붙잡는 시간이 줄어든다.
- 시퀀스 번호 20, 21, 22, 23은 ETP.CM의 control byte(RTS 20, CTS 21, DPO 22, EOMA 23)와 같은 값이다. 이 예제에서만 그런 DT가 12개 나온다. 수신 측은 첫 바이트가 아니라 PGN(PF `0xC8` 대 `0xC7`(=199))으로 CM과 DT를 갈라야 한다.

::: details 파이썬으로 검산: 4000바이트 ETP 송신과 DPO 재조립
위 표의 프레임을 모두 만들고(송신), 다시 DPO 규칙대로 조립해(수신) 원본과 같은지 확인하는 코드다. 수신 쪽 assert 옆 주석은 그 검사가 깨질 때 보낼 ETP Abort 사유다.

```python
import math

PGN, SIZE = 59136, 4000                        # ECU to VT (ISO 11783-6), 4000바이트
CM_TO_VT, CM_TO_ECU, DT_TO_VT = 0x1CC82623, 0x1CC82326, 0x1CC72623


def le(v, n):
    return [(v >> (8 * i)) & 0xFF for i in range(n)]


# 원본: Byte 1 = 0x11(Object pool transfer), 나머지는 "위치 - 1"의 하위 8비트
data = bytes([0x11] + [i & 0xFF for i in range(1, SIZE)])
packets = math.ceil(SIZE / 7)
assert packets == 572

P = le(PGN, 3)
rts = [20] + le(SIZE, 4) + P
cts = lambda n, nxt: [21, n] + le(nxt, 3) + P
dpo = lambda n, off: [22, n] + le(off, 3) + P
hold = [21, 0, 0xFF, 0xFF, 0xFF] + P
eoma = [23] + le(SIZE, 4) + P


def dt(seq, pkt):
    chunk = list(data[(pkt - 1) * 7: pkt * 7])
    return [seq] + chunk + [0xFF] * (7 - len(chunk))


frames = [(CM_TO_VT, rts), (CM_TO_ECU, cts(255, 1))]
for i, (n, nxt) in enumerate([(255, 1), (255, 256), (62, 511)]):
    if i == 1:
        frames.append((CM_TO_ECU, hold))
    if i:
        frames.append((CM_TO_ECU, cts(n, nxt)))
    frames.append((CM_TO_VT, dpo(n, nxt - 1)))
    frames += [(DT_TO_VT, dt(s, nxt - 1 + s)) for s in range(1, n + 1)]
frames.append((CM_TO_ECU, eoma))

# 수신 측(VT): CM과 DT는 첫 바이트가 아니라 PGN(PF)으로 가른다
got, cts_n, cts_next, off, want = {}, 0, 0, 0, 1
for cid, d in frames:
    pf = (cid >> 16) & 0xFF
    if pf == 0xC8 and d[0] == 21 and d[1]:
        cts_n, cts_next = d[1], d[2] | d[3] << 8 | d[4] << 16
        assert cts_next - 1 + cts_n <= packets          # 넘으면 Abort 15
    elif pf == 0xC8 and d[0] == 22:
        assert d[1] <= cts_n                            # 넘으면 Abort 11
        off = d[2] | d[3] << 8 | d[4] << 16
        assert off == cts_next - 1                      # 어긋나면 Abort 12
        want = 1
    elif pf == 0xC7:
        assert d[0] == want                             # 어긋나면 Abort 7 / 8
        got[off + d[0]] = bytes(d[1:])
        want += 1
assert b"".join(got[k] for k in sorted(got))[:SIZE] == data

assert len(frames) == 581
assert sum(1 for c, d in frames if (c >> 16) & 0xFF == 0xC7 and d[0] in (20, 21, 22, 23)) == 12
assert 1 + 2 * math.ceil(packets / 16) + 1 == 74          # CTS당 16패킷일 때 CM 프레임 수
print(" ".join(f"{b:02X}" for b in frames[0][1]))         # RTS
```

마지막 줄은 RTS인 `14 A0 0F 00 00 00 E7 00`을 출력한다. 수신 쪽 반복문에서 `got[off + d[0]]`이 "오프셋 + 시퀀스 번호 = 실제 패킷 번호" 규칙이고, 그 아래 assert들이 "전체 581프레임", "CM과 첫 바이트가 같은 DT 12개", "CTS당 16패킷이면 CM 74개"라는 위의 숫자를 확인한다.
:::

<small>근거: ISO 11783-3 5.11.5.2, 5.11.5.4, 5.11.6, 5.13.6; ISO 11783-6 C.1, C.2.1, C.2.3</small>

::: tip 핵심 정리
- TP는 시퀀스 번호가 1~255라 1,785바이트까지만 보낸다. 더 큰 데이터는 ETP(최대 117,440,505바이트)로 보낸다.
- ETP는 PGN 51200(ETP.CM, 0xC800)과 50944(ETP.DT, 0xC700)를 쓰는 CMDT 전용 방식이다. BAM 형태는 없고, 성립·hold·재전송 규칙과 타이밍은 TP와 같다.
- ETP는 TP 규칙을 따르되 RTS에 패킷 수가 없고, CTS 구간마다 DPO로 오프셋을 알린다. 실제 패킷 번호 = 오프셋 + 시퀀스 번호다.
- 수신 측은 CM과 DT를 첫 바이트가 아니라 PGN(PF)으로 가른다.
- Abort 사유 9 이상은 TP와 ETP가 다르다. 해석 전에 TP.CM인지 ETP.CM인지 먼저 가른다.
:::

::: details 확인 문제
1. (개념) 1,500바이트와 3,000바이트 데이터는 각각 TP와 ETP 중 무엇으로 보내는가?
2. (개념) ETP.CM_DPO의 오프셋이 510이고 ETP.DT의 시퀀스 번호가 3이면 실제 패킷 번호는 몇인가? 그 패킷은 원본 몇 번째 바이트부터 담는가?
3. (개념) ETP로 BAM처럼 버스의 모든 장치에게 한꺼번에 보낼 수 있는가?
4. (디코딩) ETP 세션 중 송신 측에게서 데이터가 `16 3E FE 01 00 00 E7 00`인 ETP.CM을 받았다. 다음에 오는 시퀀스 번호 1의 ETP.DT 7바이트는 원본 몇 번째 바이트부터인가? 이 DPO 직전에 수신 측이 보낸 CTS의 Byte 2~5는 어떤 값이어야 하는가(메시지 크기는 4000바이트)?

**답 가이드**
1. 1,500바이트는 1,785바이트 이하이므로 TP(BAM 또는 CMDT)로, 3,000바이트는 1,785바이트를 넘으므로 ETP로 보낸다.
2. 510 + 3 = 513번 패킷이다. (513 − 1) × 7 + 1 = 3585번째 바이트부터 담는다.
3. 보낼 수 없다. ETP는 CMDT 전용이고, 모든 ETP.CM 메시지는 특정 목적지 메시지다.
4. 오프셋은 `FE 01 00` = 510이므로 시퀀스 번호 1은 패킷 511이고, 원본 (511 − 1) × 7 + 1 = 3571번째 바이트부터 3577번째까지다. 직전 CTS의 다음 패킷 번호는 오프셋 + 1 = 511(`FF 01 00`)이어야 하고, 패킷 수는 DPO의 62 이상이면서 남은 패킷 62를 넘을 수 없으므로 62(`3E`)다. 즉 Byte 2~5는 `3E FF 01 00`이다(남은 패킷보다 많이 요청하면 ETP Abort 사유 15).
:::

## 다음 챕터

- 다음: [18장 ISOBUS 개요](/study/isobus/18-isobus-overview)
