---
title: "요청과 응답: Request, ACK, Group function"
description: "장치가 다른 장치에게 데이터를 요청하는 Request, 받은 쪽이 ACK·NACK으로 답하는 Acknowledgement, PGN 하나에 여러 기능을 묶는 Group function과 제조사 독점 메시지의 규칙을 익힌다."
date: 2026-04-13
tags: [J1939, ISOBUS, Request, Acknowledgement, NACK]
prev: /study/isobus/09-j1939-message
next: /study/isobus/11-j1939-request2-timing
---

# 요청과 응답: Request, ACK, Group function

::: info 학습 목표
- J1939·ISOBUS 메시지의 다섯 가지 종류(명령, 요청, 방송·응답, 확인 응답, 그룹 기능)를 구분할 수 있다.
- Request(PGN 59904) 프레임을 바이트 단위로 만들고 읽을 수 있다.
- 요청이 전역인지 특정 장치 앞인지에 따라 응답을 누구에게, 어떤 방식으로 보내는지 설명할 수 있다.
- NACK을 꼭 보내야 할 때와 아무것도 보내면 안 될 때를 구분할 수 있다.
- Acknowledgement(PGN 59392) 프레임 8바이트를 읽고, 제조사 독점 메시지(Proprietary A·A2·B)의 자리를 말할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [9장 J1939 메시지 구조](/study/isobus/09-j1939-message), [6장 CAN 에러 처리](/study/isobus/06-can-error)
- 이 장에서 처음 나오는 말
  - Request(요청): "이 PGN의 데이터를 보내 달라"는 메시지다. PGN 59904를 쓴다.
  - 전역 요청, 특정 요청: 모두에게 묻는 요청(DA 255)과 한 장치에게만 묻는 요청이다.
  - ACK, NACK: "알았다, 처리했다"는 긍정 확인 응답과 "할 수 없다, 없다"는 부정 확인 응답이다.
  - Acknowledgement(확인 응답): ACK, NACK 등을 담아 보내는 메시지다. PGN 59392를 쓴다.
  - Group function(그룹 기능): PGN 하나에 여러 기능을 묶고, 데이터 첫 바이트로 기능을 고르는 방식이다.
  - TP(Transport Protocol): 8바이트보다 긴 데이터를 여러 프레임으로 나눠 보내는 방법이다. 모두에게 보내는 BAM과 한 장치에게 보내는 RTS/CTS 두 방식이 있다([15장](/study/isobus/15-tp-bam-cmdt)).
:::

식당에서 손님이 직원에게 "물 좀 주세요"라고 하면 직원은 물을 가져오거나 "지금 물이 없습니다"라고 답한다. 그런데 손님이 식당 전체에 "펜 가진 분 계세요?"라고 외쳤을 때 펜이 없는 사람까지 모두 "없어요"라고 답하면 시끄럽기만 하다. J1939의 요청과 응답 규칙이 바로 이 차이를 다룬다. 한 장치에게 물으면 반드시 답(없으면 NACK)이 오고, 모두에게 물으면 가진 장치만 답한다.

## 1. 메시지의 다섯 가지 종류

이 절에서는 버스에 오가는 메시지를 하는 일에 따라 다섯 종류로 나눠 본다. 나머지 절은 이 가운데 요청(Request), 확인 응답(Acknowledgement), 그룹 기능(Group Function)을 하나씩 자세히 본다.

ISO 11783-3(ISOBUS의 데이터 링크 계층을 정하는 표준 문서)은 현재 지원하는 메시지 타입을 다섯 가지로 든다. 타입은 할당된 PGN으로 구별한다.

| 타입 | 하는 일 |
|---|---|
| Command | 특정 또는 전역 목적지에 동작을 지시한다. PDU1·PDU2 모두 쓸 수 있다. 원문의 예는 Transmission Control, Address Request, Torque/Speed Control |
| Request | 특정 또는 전역 목적지에 정보를 요청한다(PGN 59904) |
| Broadcast/Response | 비요청 브로드캐스트, 또는 명령·요청에 대한 응답 |
| Acknowledgement | 특정 명령·요청에 대한 ACK·NACK 등(PGN 59392) |
| Group Function | 첫 데이터 바이트 등으로 하위 기능을 고르는 PG 묶음 |

Command(명령)는 "기어를 바꿔라", "토크를 줄여라"처럼 상대에게 무언가를 시키는 메시지다. 원문의 예는 변속기 제어(Transmission Control), 주소 요청(Address Request), 토크·속도 제어(Torque/Speed Control)다. Broadcast/Response(방송·응답)는 묻지 않아도 스스로 보내는 정보(비요청 브로드캐스트)이거나, 명령·요청에 대한 답이다. PG(Parameter Group)는 PGN 하나로 보내는 값의 묶음이다([9장](/study/isobus/09-j1939-message)).

ISO 11783-3은 여기에 Request2와 Transfer를 더 정의한다([11장](/study/isobus/11-j1939-request2-timing)). 리모트 프레임(RTR = 1)은 쓸 수 없고, 요청은 데이터 프레임인 Request PGN으로 한다. 리모트 프레임으로 요청하려면 요청자가 응답할 장치의 SA를 단 프레임을 보내야 하는데, 장치는 다른 장치의 SA로 메시지를 보낼 수 없기 때문이다. 자세한 이유는 [CAN 데이터 프레임](/study/isobus/04-can-data-frame) 챕터에서 봤다.

<small>근거: ISO 11783-3 5.4.1~5.4.6</small>

## 2. Request: 데이터를 보내 달라는 메시지 (PGN 59904)

필요한 데이터가 주기적으로 오지 않거나 지금 당장 필요할 때, 장치는 그 데이터를 가진 장치에게 Request를 보낸다. 이 절에서는 Request 프레임의 모양을 본다.

| 항목 | 값 |
|---|---|
| PF / PS | 234(`0xEA`) / DA (전역 또는 특정) |
| 데이터 길이 | 3바이트. 이 PG의 프레임은 DLC를 3으로 해야 한다(shall) |
| 기본 Priority | 6 |
| Byte 1~3 | 요청하는 PGN (LSB 먼저) |
| 송신 빈도 | 사용자 요구에 따르되 초당 2~3회 이하를 권장 |

표 읽는 법: PF 234는 240보다 작으므로 Request는 PDU1이고, PS 칸에 받는 장치의 주소를 적는다. 255를 적으면 모두에게 묻는 전역 요청이 된다. DLC(Data Length Code)는 프레임의 데이터 바이트 수를 적는 칸이다([4장](/study/isobus/04-can-data-frame)). Request는 데이터가 3바이트뿐이므로 DLC도 8이 아니라 3이다. shall은 반드시 지켜야 하는 요구라는 뜻이다.

예를 들어 VT(SA `0x26`)가 네트워크의 모든 CF에게 Address Claimed(PGN 60928 = `0x00EE00`)를 요청하는 전역 요청은 `18EAFF26#00EE00`이다. Priority 6, PF `0xEA`, DA `0xFF`, SA `0x26`이고 데이터는 PGN을 LSB부터 적은 `00 EE 00`이다.

한 단계씩 읽으면 다음과 같다.

1. ID `18EAFF26`을 두 자리씩 끊는다: `18 | EA | FF | 26`.
2. `18`은 Priority 6, EDP 0, DP 0이다([9장](/study/isobus/09-j1939-message)의 지름길). PF `EA`(234)는 Request다.
3. PS `FF`는 DA 255, 즉 모두에게 묻는 전역 요청이다. SA `26`은 요청한 장치다.
4. 데이터 `00 EE 00`은 3바이트 PGN을 낮은 자리부터 적은 것이다. 거꾸로 붙이면 `0x00EE00` = 60928이다.

VT(Virtual Terminal)는 운전석에서 작업기를 조작하는 화면 장치이고([29장](/study/isobus/29-vt-basics)), Address Claimed는 "이 주소를 내가 쓴다"고 알리는 메시지다([13장](/study/isobus/13-j1939-address-claim)). CF(Control Function)는 버스에서 주소 하나를 쓰는 기능 단위다([8장](/study/isobus/08-j1939-intro)).

<small>근거: ISO 11783-3 5.2.8.1, 5.4.3</small>

## 3. 응답은 누구에게, 어떻게 보내나

요청을 받은 장치는 응답을 누구에게 보낼지(모두에게 또는 요청자에게), 8바이트가 넘으면 어떻게 나눠 보낼지(어느 TP) 정해야 한다. ISO 11783-3은 PDU 형식, 데이터 길이, 요청 방식의 조합마다 답을 표 하나로 정리한다. 그 표를 옮기면 다음과 같다.

| PDU 형식 | 데이터 길이 | 받은 요청(PGN 59904) | 응답 목적지 | 쓰는 TP |
|---|---|---|---|---|
| PDU1 | 8바이트 이하 | 특정 | 특정 | 쓰지 않음 |
| PDU1 | 8바이트 이하 | 전역 | 전역 | 쓰지 않음 |
| PDU1 | 8바이트 이하 | 없음(주기·비요청 송신) | 전역 또는 특정 | 쓰지 않음 |
| PDU1 | 8바이트 초과 | 특정 | 특정 | RTS/CTS |
| PDU1 | 8바이트 초과 | 전역 | 전역 | BAM |
| PDU1 | 8바이트 초과 | 없음(주기·비요청 송신) | 전역 또는 특정 | 전역이면 BAM, 특정이면 RTS/CTS |
| PDU2 | 8바이트 이하 | 특정 | <strong>전역</strong> | 쓰지 않음 |
| PDU2 | 8바이트 이하 | 전역 | 전역 | 쓰지 않음 |
| PDU2 | 8바이트 이하 | 없음(주기·비요청 송신) | 전역만 | 쓰지 않음 |
| PDU2 | 8바이트 초과 | 특정 | 특정 | RTS/CTS |
| PDU2 | 8바이트 초과 | 전역 | 전역 | BAM |
| PDU2 | 8바이트 초과 | 없음(주기·비요청 송신) | 전역 또는 특정 | 전역이면 BAM, 특정이면 RTS/CTS |

표 읽는 법: 앞의 세 열이 상황이고, 뒤의 두 열이 할 일이다. "특정"은 한 장치, "전역"은 모두(DA 255)를 뜻한다. 굵게 표시한 칸이 요청 방식과 응답 방식이 어긋나는 유일한 곳이다. ISO 11783-3 전체 정리는 [Part 3 정리 부록](/study/isobus/appendix-iso-part03)에 있다.

구현할 규칙으로 줄이면 다음과 같다.

1. 요청이 전역이면 응답도 전역이다. 8바이트를 넘으면 BAM으로 보낸다.
2. 요청이 특정 목적지면 응답도 그 요청자에게 보낸다. 8바이트를 넘으면 RTS/CTS로 보낸다.
3. 예외: PDU2 PGN이고 8바이트 이하면 DA 칸이 없으므로 특정 요청에도 전역으로 답한다.
4. 예외: Address Claim은 특정 요청을 받아도 전역으로 답한다(ISO 11783-5).
5. 요청 없이 보내는 주기·비요청 메시지는 송신자가 목적지를 고른다. PDU2 8바이트 이하는 전역만 가능하다.

규칙 4의 Address Claim은 주소를 정하는 메시지이고, ISO 11783-5(주소와 네트워크 관리를 정하는 표준 문서)가 따로 정한다([13장](/study/isobus/13-j1939-address-claim)).

8바이트는 프레임 하나에 다 들어가므로 TP가 필요 없다. 그래서 TP를 쓰는 기준은 "8바이트 초과"다. 표준 본문 한 곳은 이 기준을 "8바이트 이상"이라고 적지만, TP는 9바이트 이상에만 쓰고 위 표도 "8바이트 초과"로 나누므로 "8바이트 초과"로 읽는 것이 일관된다.

아래 함수는 위 표에서 요청이 있는 여덟 행을 코드로 옮긴 것이다. `rows`의 각 줄이 표의 한 행이고, `assert`로 함수가 표와 같은 답을 내는지 확인한다.

::: details 파이썬: 응답 규칙 표를 함수로
```python
GLOBAL = 0xFF


def response_plan(pdu, length, request_da):
    """(PDU 형식, 데이터 길이, 요청 DA) -> (응답 목적지, TP). Address Claim 예외는 제외."""
    if request_da == GLOBAL:
        return ("global", "BAM" if length > 8 else None)
    if pdu == 2 and length <= 8:
        return ("global", None)              # PDU2 단일 프레임에는 DA 칸이 없다
    return ("specific", "RTS/CTS" if length > 8 else None)


rows = [
    (1, 8, 0x00, ("specific", None)), (1, 8, GLOBAL, ("global", None)),
    (1, 9, 0x00, ("specific", "RTS/CTS")), (1, 9, GLOBAL, ("global", "BAM")),
    (2, 8, 0x00, ("global", None)), (2, 8, GLOBAL, ("global", None)),
    (2, 9, 0x00, ("specific", "RTS/CTS")), (2, 9, GLOBAL, ("global", "BAM")),
]
for pdu, length, da, expected in rows:
    assert response_plan(pdu, length, da) == expected
```
:::

::: details 원문을 가진 독자를 위한 메모
- 위 표는 ISO 11783-3 Table 5를 옮긴 것이고, 다섯 규칙은 5.4.3의 a)~d)를 줄인 것이다.
- Part 3 5.4.3 본문은 규칙 2를 "데이터 길이가 8바이트 이상이면 특정 주소 응답에 RTS/CTS를 써야 한다"고 적는다. 그러나 TP는 9바이트 이상에 쓰는 것이고(5.10.6.3) Table 5도 "8바이트 초과"로 나누므로, "8바이트 초과"로 읽는 것이 일관된다.
:::

<small>근거: ISO 11783-3 5.4.3, 5.10.6.3, Table 5</small>

## 4. NACK을 보낼 때와 침묵할 때

요청을 받았는데 그 데이터를 갖고 있지 않으면 어떻게 할까? 답은 요청 방식에 따라 정반대다. 이 절은 도입의 식당 비유를 규칙으로 옮긴 것이다.

요청을 받은 CF가 그 PG를 지원하지 않을 때의 동작은 요청 형식에 따라 정반대다.

| 받은 요청 | PGN 지원 | 응답 |
|---|---|---|
| 특정 목적지 | 지원 | 요청된 데이터. Acknowledgement가 적절한 PG면 control 0(ACK), 2(Access Denied), 3(Cannot Respond) 중 하나 |
| 특정 목적지 | 미지원 | NACK(control 1) 필수 |
| 전역 | 지원 | 요청된 데이터를 전역으로. 이 PG를 쓰는 모든 CF가, 요청자 자신까지 응답 |
| 전역 | 미지원 | 침묵. 전역 요청에 NACK을 보내면 안 되고, Acknowledgement 자체가 허용되지 않음 |

표의 control은 확인 응답 메시지(Acknowledgement)의 첫 바이트로, 응답의 종류를 숫자로 나타낸다. 0은 ACK(처리함), 1은 NACK(못 함, 없음), 2는 Access Denied(있지만 보안상 거부), 3은 Cannot Respond(있지만 지금은 바빠서 못 함)다. 바이트 배치는 6절에서 본다.

"지원하지 않는다"는 "그 PG를 송신하지 않는다"는 뜻이다. 요청으로는 상대가 그 PG를 받았을 때 동작하는지(수신 기능)를 알 수 없다. PGN은 인식하지만 파라미터 값을 줄 수 없으면 NACK이 아니라 해당 데이터 값을 255(FF)로 채운 정상 응답을 보낸다. 255(FF)는 [9장](/study/isobus/09-j1939-message)에서 본 "값 없음" 표시다. 명령이나 요청의 PGN을 목적지가 아예 인식하지 못해도 NACK을 보내는 것이 맞다.

전역 요청에서 요청자가 자신에게도 답해야 하는 이유는 표준이 이렇게 적는다. 모든 CF가 응답하리라고 기대되는 상황에서 요청자가 답하지 않으면, 다른 CF들이 요청된 정보에 대해 잘못된 결론을 내릴 수 있다. 원문이 드는 예는 주소 요청이다. 요청자의 Address Claimed가 빠지면 다른 CF들은 그 주소를 쓰는 CF가 없다고 판단할 수 있다(추론).

식당 비유가 어긋나는 점이 여기 있다. 식당에서 "펜 가진 분?"이라고 외친 손님은 자기 펜 이야기를 하지 않는다. 하지만 J1939에서는 전역 요청을 보낸 장치도 그 PG를 갖고 있으면 자기 데이터를 함께 보내야 한다.

3절과 이 절의 규칙을 요청을 받은 장치의 판단 순서로 묶으면 다음 그림이 된다.

![요청을 받은 장치가 요청된 PGN을 보내지 않으면 전역 요청일 때 침묵하고 특정 요청일 때 NACK(control 1)을 보내며, 보내는 PGN이면 전역 요청일 때 전역으로 응답(8바이트 초과면 BAM), 특정 요청이라도 PDU2이고 8바이트 이하면 전역으로 응답, 그 밖에는 요청자에게 응답(8바이트 초과면 RTS/CTS)하는 판단 흐름](/images/study-isobus/10-request-handling-flow-light.png)
![요청을 받은 장치가 요청된 PGN을 보내지 않으면 전역 요청일 때 침묵하고 특정 요청일 때 NACK(control 1)을 보내며, 보내는 PGN이면 전역 요청일 때 전역으로 응답(8바이트 초과면 BAM), 특정 요청이라도 PDU2이고 8바이트 이하면 전역으로 응답, 그 밖에는 요청자에게 응답(8바이트 초과면 RTS/CTS)하는 판단 흐름](/images/study-isobus/10-request-handling-flow-dark.png)

그림 읽는 법: 맨 위 "요청을 받음"에서 출발해 질문마다 예·아니오를 따라간다. 왼쪽 갈래는 그 PGN을 보내지 않는 장치, 가운데와 오른쪽은 보내는 장치의 길이다. Address Claim 예외(3절 규칙 4)는 그림에서 뺐다.

<small>근거: ISO 11783-3 5.4.3, 5.13.4, Annex C</small>

## 5. 장면으로 보는 요청과 응답

이제 규칙이 실제 프레임으로 어떻게 보이는지 장면별로 본다. ISO 11783-3에는 엔진(SA `0x00`)을 예로 메시지 종류의 쓰임을 보여 주는 사례가 실려 있다. 요청자는 SA `0x03`, 명령자는 SA `0xF0`(240)이다. 엔진에게 묻는 데이터는 Component ID(Component Identification, PGN 65259)로, 원문은 엔진의 일련번호를 보내는 메시지로 소개한다.

![요청자 SA 0x03이 엔진 SA 0x00에게 특정 요청을 보내면 엔진이 데이터나 NACK으로 답하고, 요청자가 전역 요청을 보내면 엔진이 모두에게 답하거나 미지원이면 침묵하며, 명령자 SA 0xF0이 엔진에게 명령을 보내면 엔진이 ACK이나 NACK으로 답하는 세 장면](/images/study-isobus/10-request-ack-scenes-light.png)
![요청자 SA 0x03이 엔진 SA 0x00에게 특정 요청을 보내면 엔진이 데이터나 NACK으로 답하고, 요청자가 전역 요청을 보내면 엔진이 모두에게 답하거나 미지원이면 침묵하며, 명령자 SA 0xF0이 엔진에게 명령을 보내면 엔진이 ACK이나 NACK으로 답하는 세 장면](/images/study-isobus/10-request-ack-scenes-dark.png)

그림 읽는 법: 세로선 하나가 장치 하나이고, 위에서 아래로 시간이 흐른다. 화살표가 프레임 하나다. 점선 화살표는 상황에 따라 둘 중 하나만 오는 응답이다. 원문의 숫자를 CAN 프레임으로 옮기면 다음과 같다.

| 장면 | ID | 데이터 | 해설 |
|---|---|---|---|
| 특정 요청 | `0x18EA0003` | `EB FE 00` | 엔진에게 Component ID(65259) 요청 |
| 응답 | 길이에 따라 다름 | Component ID 데이터 | Component ID 데이터. 8바이트를 넘으면 SA 3에게 RTS/CTS |
| 또는 NACK | `0x18E80300` | `01 FF FF FF 03 EB FE 00` | control 1, 주소 3, PGN 65259 |
| 전역 요청 | `0x18EAFF03` | `EB FE 00` | 응답은 전역(8바이트 초과면 BAM). 미지원이면 침묵 |
| 명령에 대한 ACK | `0x18E8F000` | `00 FF FF FF F0` + 명령 PGN | 명령 완료 |
| 명령에 대한 NACK | `0x18E8F000` | `01 FF FF FF F0` + 명령 PGN | 명령 수행 불가 |

ID를 두 자리씩 끊어 읽어 보자.

- `0x18EA0003` = `18 | EA | 00 | 03`: Priority 6, PF 234(Request), DA `0x00`(엔진), SA `0x03`(요청자)이다. 데이터 `EB FE 00`을 거꾸로 붙이면 `0x00FEEB` = 65259다.
- `0x18E80300` = `18 | E8 | 03 | 00`: PF `0xE8`(232)는 Acknowledgement다. 엔진(SA `0x00`)이 요청자(DA `0x03`)에게 보냈다. 데이터 첫 바이트 `01`은 NACK, 다섯째 바이트 `03`은 요청자 주소, 마지막 세 바이트는 PGN 65259다.
- `0x18E8F000` = `18 | E8 | F0 | 00`: 엔진이 명령자(DA `0xF0`)에게 보낸 Acknowledgement다. 첫 바이트가 `00`이면 ACK, `01`이면 NACK이다.

원문은 응답 행을 PF 254·GE 235의 PDU2 한 프레임으로 그린다. 메시지 종류를 보여 주려는 단순화로 보이고, Component ID가 8바이트를 넘는다면 3절의 표에 따라 특정 요청에는 RTS/CTS로 SA 3에게, 전역 요청에는 BAM으로 보내야 한다(추론).

명령에 대한 ACK은 필수가 아니다. 명령은 늘 성공 여부를 확인할 수단을 갖고 있고, 다른 수단이 있으면 ACK을 생략해 버스 트래픽을 줄인다. 원문의 예는 엔진 토크 명령이다. 엔진이 내보내는 토크 모드 비트와 토크 값으로 결과를 확인할 수 있다.

<small>근거: ISO 11783-3 Annex C</small>

## 6. Acknowledgement: 확인 응답 메시지 (PGN 59392)

4·5절에 나온 ACK과 NACK을 실어 나르는 메시지가 Acknowledgement다. 이 절에서는 그 8바이트를 한 바이트씩 읽는다.

### 정의와 바이트 배치

| 항목 | 값 |
|---|---|
| PF / PS | 232(`0xE8`) / DA |
| 데이터 길이 | 8바이트 |
| 기본 Priority | 6 |
| 송신 시점 | 이 형태의 확인 응답을 요구하는 PGN을 받았을 때 |

PF 232는 240보다 작으므로 Acknowledgement는 PDU1이고, PS(DA)에 응답받을 장치의 주소를 적는다. "이 형태의 확인 응답을 요구하는 PGN"은 정의에 "답할 때 Acknowledgement를 쓴다"고 적힌 메시지를 말한다.

![Acknowledgement 8바이트 배치: Byte 1 control, Byte 2~4는 기본형이면 Group Function 값과 FF FF, 확장 1·2·3바이트형이면 그 길이만큼 확장 식별자와 나머지 FF, Byte 5 응답받을 주소, Byte 6~8 요청됐던 PGN](/images/study-isobus/09-ack-layout-light.png)
![Acknowledgement 8바이트 배치: Byte 1 control, Byte 2~4는 기본형이면 Group Function 값과 FF FF, 확장 1·2·3바이트형이면 그 길이만큼 확장 식별자와 나머지 FF, Byte 5 응답받을 주소, Byte 6~8 요청됐던 PGN](/images/study-isobus/09-ack-layout-dark.png)

그림 읽는 법: 가로 한 줄이 Acknowledgement의 한 가지 형태이고, 세로 칸이 Byte 1~8이다. 바이트는 1부터 센다. 맨 위 기본형이 흔히 쓰는 형태이고, 아래 세 줄은 [11장](/study/isobus/11-j1939-request2-timing)의 Request2에 답할 때만 쓰는 확장형이다. 네 형태 모두 Byte 5는 응답받을 주소, Byte 6~8은 요청됐던 PGN(LSB 먼저)으로 같다. 다른 것은 Byte 1의 control 값과 Byte 2~4의 쓰임뿐이다.

CAN 프레임의 ACK 슬롯이 "적어도 한 노드가 받았다"만 알려 준다면, 이 PG는 특정 명령·요청에 대해 응용 계층이 답하는 확인 응답이다. 두 형식의 차이는 [CAN 에러 처리](/study/isobus/06-can-error) 챕터에서 다뤘다.

### Control byte 읽는 법

정의된 control byte는 16개다. 기본형 0~3과, Request2가 확장 식별자를 쓸 때만 쓰는 128~131, 144~147, 160~163이다. 값을 늘어놓으면 규칙성이 보인다.

| 종류 | 기본형 | 확장 1바이트 | 확장 2바이트 | 확장 3바이트 |
|---|---|---|---|---|
| ACK (Positive Acknowledgement) | 0 | 128 | 144 | 160 |
| NACK (Negative Acknowledgement) | 1 | 129 | 145 | 161 |
| Access Denied (지원하지만 보안상 거부) | 2 | 130 | 146 | 162 |
| Cannot Respond (지원하지만 바쁨, 나중에 다시 요청) | 3 | 131 | 147 | 163 |

이진수로 보면 Bit 8은 확장 식별자 사용 여부, Bit 6~5는 확장 식별자 길이에서 1을 뺀 값, Bit 2~1은 응답 종류다. 원문이 이렇게 설명하지는 않으므로 해석 코드를 짤 때의 관찰로만 쓴다. 나머지 값(4~127, 132~143, 148~159, 164~255)은 장래 표준을 위한 예약이다.

바이트 안의 비트 번호는 오른쪽(가장 낮은 자리)이 Bit 1, 왼쪽(가장 높은 자리)이 Bit 8이다([4장](/study/isobus/04-can-data-frame)). 예를 들어 129를 이진수로 쓰면 `1000 0001`이다.

- Bit 8 = 1: 확장 식별자를 쓴다.
- Bit 6~5 = `00`: 길이 - 1 = 0이므로 확장 식별자는 1바이트다.
- Bit 2~1 = `01`: 응답 종류 1, 즉 NACK이다.

같은 방법으로 145 = `1001 0001`은 Bit 6~5가 `01`이라 2바이트형 NACK, 161 = `1010 0001`은 `10`이라 3바이트형 NACK이다.

- Byte 2의 Group Function Value는 Group Function PG의 어느 하위 기능에 대한 응답인지 알려 준다. 값은 PG마다 고유하며 0~250을 쓰는 것이 바람직하고, 251~255는 ISO 11783-7(트랙터·작업기 메시지를 정하는 표준 문서)의 관례를 따른다. 해당 사항이 없으면 FF다. Group Function은 7절에서 본다.
- Byte 5는 확인 응답을 받을 원래 요청자의 SA이고, PS(DA) 필드의 복제다. 원문은 SAE J1939와의 최대 호환을 위해서라고만 적는다. 데이터 필드만 남는 로그에서도 누구의 요청에 대한 응답인지 알 수 있다는 실용적 이점이 있다(추론).
- 예약 바이트(기본형의 Byte 3~4)는 FF로 보낸다. 예약은 나중에 쓰려고 비워 둔 칸이라는 뜻이다.

### 해석 예제

로그 `18E82680#01FFFFFF26EBFE00`을 읽어 보자. ID는 두 자리씩 `18 | E8 | 26 | 80`으로 끊는다.

- ID: Priority 6, PF `0xE8`(Acknowledgement), DA `0x26`, SA `0x80`
- Byte 1 `01`: NACK, 기본형
- Byte 2~4 `FF FF FF`: Group Function Value 없음, 예약
- Byte 5 `26`: SA `0x26`의 요청에 대한 응답 (DA와 같다)
- Byte 6~8 `EB FE 00`: PGN 65259

결론: SA `0x80`은 SA `0x26`이 특정 요청한 Component Identification(65259)을 송신하지 않는다.

확장형 예로 데이터 `81 12 FF FF 26 00 EF 00`은 control 129(NACK, 확장 1바이트), 확장 식별자 `0x12`, PGN 61184(Proprietary A)다. "첫 데이터 바이트가 `0x12`인 Proprietary A 메시지는 보내지 않는다"는 뜻이다. 이런 요청을 만드는 Request2는 [11장](/study/isobus/11-j1939-request2-timing)에서, Proprietary A는 7절에서 본다.

아래 함수는 control byte의 규칙성을 써서 Acknowledgement 8바이트를 푼다. `cb & 0xFC`는 아래 두 비트를 지워 형태(기본형, 확장 1·2·3바이트형)만 남기고, `cb & 0x03`은 아래 두 비트만 남겨 응답 종류를 얻는다. 마지막 두 `assert`가 위 해석 예제 두 개와 같은 결과를 확인한다.

::: details 파이썬: Acknowledgement 해석기
```python
KIND = {0: "ACK", 1: "NACK", 2: "Access Denied", 3: "Cannot Respond"}
EXT_LEN = {0: 0, 128: 1, 144: 2, 160: 3}      # control byte 기준값 -> 확장 식별자 바이트 수


def decode_ack(data):
    cb = data[0]
    base = cb & 0xFC
    if base not in EXT_LEN:
        return {"control": cb, "kind": "reserved"}
    n = EXT_LEN[base]
    return {
        "kind": KIND[cb & 0x03],
        "group_function_value": None if n or data[1] == 0xFF else data[1],
        "extended_identifier": int.from_bytes(bytes(data[1:1 + n]), "little") if n else None,
        "address": data[4],
        "pgn": data[5] | (data[6] << 8) | (data[7] << 16),
    }


defined = [0, 1, 2, 3, 128, 129, 130, 131, 144, 145, 146, 147, 160, 161, 162, 163]
for cb in range(256):                           # 정의된 16개만 해석되고 나머지는 예약
    r = decode_ack([cb, 0xFF, 0xFF, 0xFF, 0x26, 0xEB, 0xFE, 0x00])
    assert (r["kind"] != "reserved") == (cb in defined)

r = decode_ack([0x01, 0xFF, 0xFF, 0xFF, 0x26, 0xEB, 0xFE, 0x00])
assert (r["kind"], r["address"], r["pgn"]) == ("NACK", 0x26, 65259)
r = decode_ack([0x81, 0x12, 0xFF, 0xFF, 0x26, 0x00, 0xEF, 0x00])
assert (r["kind"], r["extended_identifier"], r["pgn"]) == ("NACK", 0x12, 61184)
```
:::

<small>근거: ISO 11783-3 5.4.5</small>

## 7. Group function과 제조사 독점 메시지

Group function은 기능마다 PGN을 따로 받지 않고, PGN 하나 안에서 첫 데이터 바이트로 기능을 고르는 방식이다. 식당 메뉴판에 비유하면 PGN은 "이 식당", 첫 데이터 바이트는 "메뉴 번호"다. 이 절에서는 Group function의 규칙과, 그 대표 사례인 제조사 독점 메시지를 본다.

### Group function

Group function은 PGN 하나에 여러 기능을 묶는 메시지 타입이다. 그룹은 PGN으로, 그룹 안의 기능은 데이터 구조(보통 데이터 필드의 첫 바이트)로 구별한다. ISO 11783-3은 이를 쓰는 곳으로 제조사 독점 기능, multi-packet 전송 기능, 네트워크 관리(ISO 11783-5), VT(ISO 11783-6), TC(ISO 11783-10), FS(ISO 11783-13), SC(ISO 11783-14)를 든다. TP.CM의 control byte(RTS 16, CTS 17 …)도, VT 명령의 첫 바이트도 같은 원리다.

이름을 풀면 이렇다. multi-packet 전송 기능은 긴 데이터를 나눠 보내는 TP다([15장](/study/isobus/15-tp-bam-cmdt)). TP.CM은 TP의 연결 관리 메시지이고, 첫 바이트가 16이면 RTS, 17이면 CTS다. 네트워크 관리는 주소와 이름표(NAME)를 다루는 일이다([14장](/study/isobus/14-name-management-init)). VT는 작업기 조작 화면([29장](/study/isobus/29-vt-basics)), TC(Task Controller)는 작업 지시와 기록을 맡는 장치([41장](/study/isobus/41-tc-basics)), FS(File Server)는 파일을 저장해 주는 장치([51장](/study/isobus/51-file-server-basics)), SC(Sequence Control)는 운전자가 한 작업 순서를 기록했다가 다시 실행하는 기능([53장](/study/isobus/53-sequence-control-basics))이다.

구현에 필요한 규칙은 세 가지다.

- 같은 group function PG는 CAN ID가 같으므로 데이터 길이를 하나로 고정한다.
- Group function은 ISO 11783-3의 Request·ACK·NACK이 부족하면 자체 요청·확인 메커니즘을 둘 수 있다. VT·TC가 자기 응답 메시지를 갖는 이유다.
- Request(59904)로 group function PG의 지원 여부를 물을 수 있다. 지원하면 Acknowledgement control 0(또는 2, 3), 지원하지 않으면 control 1이다. 여기서도 "지원하지 않음"은 송신하지 않는다는 뜻이고, 상대가 그 PG를 받아 동작하는지는 알 수 없다.

### Proprietary A·A2·B

제조사가 자기 장치끼리만 쓰는 메시지를 독점(proprietary) 메시지라고 한다. 독점 메시지에도 PGN 자리가 정해져 있다. [8장](/study/isobus/08-j1939-intro)의 PGN 지도에서 PF 239와 PF 255 칸이 그 자리다.

| 이름 | PGN | 형식 | ID 예 (SA `0x80` → `0x81`) |
|---|---|---|---|
| Proprietary A | 61184 (`0x00EF00`) | PDU1, DP 0, PS = DA | `0x18EF8180` |
| Proprietary A2 | 126720 (`0x01EF00`) | PDU1, DP 1, PS = DA | `0x19EF8180` |
| Proprietary B | 65280 ~ 65535 (`0x00FF00` ~ `0x00FFFF`) | PDU2, PS = 제조사가 정하는 GE | `0x18FF1280` (GE `0x12`, 전역) |

ID 예를 [9장](/study/isobus/09-j1939-message)의 지름길로 읽으면 다음과 같다.

- `0x18EF8180` = `18 | EF | 81 | 80`: Priority 6, DP 0, PF 239(Proprietary A), DA `0x81`, SA `0x80`이다.
- `0x19EF8180`: 첫 바이트 `19`는 DP 1이므로 같은 PF 239라도 페이지 1의 PGN 126720(Proprietary A2)이다.
- `0x18FF1280`: PF 255라서 PDU2이고, PS `0x12`는 제조사가 정한 GE다. PGN은 65280 + 18 = 65298이다.

세 PG 모두 기본 Priority 6이고, 데이터 길이는 0~1785바이트로 multi-packet을 지원한다. 데이터 필드를 어떻게 쓸지, 독점 메시지를 쓸지 말지는 제조사가 정한다.

::: warning 같은 PGN, 다른 의미
Proprietary 메시지의 데이터 길이는 제조사마다 다르다. 두 제조사가 같은 GE 값을 쓰면서 DLC가 다를 수 있고, 수신 측은 두 제조사를 구별해야 한다. Proprietary B는 여러 SA가 같은 PGN 값을 서로 다른 목적으로 쓸 수 있어 특히 주의해야 한다. 구별 방법은 원문에 없다. 실무에서는 SA로 상대를 고르되, SA는 주소 클레임 결과에 따라 바뀔 수 있으므로 그 SA가 주소 클레임 때 보낸 NAME의 제조사 코드로 확인하는 편이 안전하다(추론, NAME은 [12장 주소와 NAME](/study/isobus/12-j1939-address-name) 참고).
:::

ISO 11783-3은 정상 운용 중 독점 메시지 사용을 최소화하고, CF당 Proprietary A·A2·B의 합이 네트워크 용량의 2%를 넘지 않게 하라고 권한다. 계산 방법은 [8장 SAE J1939 입문](/study/isobus/08-j1939-intro)의 버스 대역폭 절에 있다.

<small>근거: ISO 11783-3 5.2.8.1, 5.3.2, 5.3.3, 5.4.6.1~5.4.6.4</small>

::: tip 핵심 정리
- 메시지는 명령, 요청, 방송·응답, 확인 응답, 그룹 기능의 다섯 종류이고, PGN으로 구별한다. 요청은 리모트 프레임이 아니라 Request(PGN 59904, 데이터 3바이트)로 한다.
- 응답 목적지는 요청을 따른다. 전역 요청에는 전역(8바이트 초과면 BAM), 특정 요청에는 특정(8바이트 초과면 RTS/CTS)으로 답한다. PDU2 8바이트 이하와 Address Claim은 예외로 전역이다.
- 특정 요청에 미지원이면 NACK이 필수이고, 전역 요청에는 NACK·ACK을 보내지 않는다. 전역 요청을 보낸 장치도 그 데이터가 있으면 응답한다.
- Acknowledgement는 Byte 1 control, Byte 5 요청자 주소, Byte 6~8 PGN이다. control 0~3이 기본형이고, 128~163은 Request2의 확장 식별자용이다.
- Group function은 PGN 하나 안에서 첫 바이트로 기능을 고른다. 제조사 독점 메시지는 Proprietary A(61184)·A2(126720)·B(65280~65535)를 쓰고, 버스 용량의 2% 이하로 유지한다.
:::

::: details 확인 문제
1. (개념) 전역 요청과 특정 요청을 받았을 때, 그 PGN을 지원하지 않는 장치는 각각 무엇을 보내야 하는가?
2. (만들기) VT(SA `0x26`)가 SA `0x80`인 장치에게 Component Identification(PGN 65259)을 요청하는 프레임을 `ID#데이터` 형식으로 써라.
3. (개념) PDU2이고 8바이트 이하인 PGN을 특정 요청으로 받았다. 응답은 누구에게 보내는가? 이유는 무엇인가?
4. (디코딩) 로그 `18E82680#01FFFFFF26EBFE00`을 해석하라. 누가 누구에게, 무엇에 대해, 어떤 응답을 보냈는가?
5. (디코딩) Acknowledgement의 control byte가 131이다. 어떤 응답이고, 확장 식별자는 몇 바이트인가?

**답 가이드**
1. 특정 요청이면 NACK(control 1)을 반드시 보낸다. 전역 요청이면 아무것도 보내지 않는다(침묵). 전역 요청에는 ACK·NACK이 허용되지 않는다.
2. Request는 Priority 6, PF `0xEA`이므로 ID는 `18 | EA | 80 | 26`, 즉 `18EA8026`이다. 데이터는 PGN 65259 = `0x00FEEB`를 LSB부터 적은 `EB FE 00`이다. 답은 `18EA8026#EBFE00`이다.
3. 모두에게(전역) 보낸다. PDU2 형식에는 받는 주소를 적을 칸(DA)이 없기 때문이다.
4. SA `0x80`이 SA `0x26`에게 보낸 Acknowledgement다. control 1 = NACK, Byte 5 `0x26`은 요청자 주소(DA와 같음), Byte 6~8은 PGN 65259다. `0x80`은 Component Identification을 송신하지 않는다는 뜻이다.
5. 131 = `1000 0011`이다. Bit 8이 1이므로 확장형이고, Bit 6~5가 `00`이므로 확장 식별자는 1바이트다. Bit 2~1이 `11`이므로 응답 종류 3, 즉 Cannot Respond(지원하지만 지금은 바빠서 응답할 수 없으니 나중에 다시 요청하라)다.
:::

## 다음 챕터

- 다음: [11장 Request2, Transfer와 수신·응답 규칙](/study/isobus/11-j1939-request2-timing)
