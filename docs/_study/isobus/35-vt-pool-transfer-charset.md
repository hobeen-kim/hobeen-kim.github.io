---
title: "오브젝트 풀 전송 심화와 문자 집합"
description: "오브젝트 풀을 여러 세션으로 나눠 보내고 End of Object Pool response로 오류를 진단하며 일부만 바꾸는 법과, VT가 여러 나라 글자를 표시하는 문자 집합 규칙을 익힌다."
date: 2026-04-13
tags: [ISOBUS, VT, Object Pool, WideString, ISO-11783-6]
prev: /study/isobus/34-vt-layout-color
next: /study/isobus/36-vt-commands-basics
---

# 오브젝트 풀 전송 심화와 문자 집합

::: info 학습 목표
- Object Pool Transfer에 응답이 없다는 점과 End of Object Pool이 왜 필요한지 설명할 수 있다.
- End of Object Pool response를 읽고 오류가 난 오브젝트와 원인을 찾을 수 있다.
- 풀을 올린 뒤 일부 오브젝트만 바꾸는 절차와 주의점을 말할 수 있다.
- VT가 문자열을 8비트 문자열과 WideString으로 나눠 읽는 이유와 방법을 설명할 수 있다.
- 한글 문구를 VT에 띄우기 전에 무엇을 확인해야 하는지 말할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [32장 VT 오브젝트 풀 기초](/study/isobus/32-vt-object-pool-basics), [33장 오브젝트 레코드](/study/isobus/33-vt-object-records), [15장 Transport Protocol 기초](/study/isobus/15-tp-bam-cmdt)
- 이 장에서 처음 나오는 말
  - 세션: 단일 패킷 하나, 또는 TP나 ETP 연결 하나로 데이터를 보내는 한 번의 전송
  - 부분 갱신: 풀 전체가 아니라 바꿀 오브젝트만 다시 보내는 것
  - 문자 집합(character set): 바이트 값마다 어떤 글자인지 정해 둔 표
  - 코드 페이지: 8비트(256칸)짜리 문자 집합 하나. ISO 8859-1 같은 표를 가리킨다
  - WideString: 유니코드(UTF-16)로 적은 VT 문자열
  - BOM(Byte Order Mark): WideString 맨 앞에 붙는 표시. 바이트로는 `FF FE`다
:::

이삿짐을 트럭 여러 대에 나눠 싣듯이, 큰 오브젝트 풀은 여러 번에 나눠 VT에 보낼 수 있다. 짐을 다 보낸 뒤에는 "이것이 전부다"라고 알리고 받는 쪽의 확인을 기다린다. 또 VT는 여러 나라에서 쓰이므로, 같은 바이트를 어느 나라 글자로 읽을지 정하는 약속도 필요하다. 이 장은 ISO 11783-6(VT를 정하는 표준 문서)에서 이 두 가지를 구현자 눈높이까지 따라간다.

## 1. 풀 전송 다시 보기: 응답 없는 Object Pool Transfer

이 절에서는 오브젝트 풀을 VT에 올리는 메시지 흐름을 다시 짚고, 구현할 때 먼저 알아야 할 성질을 본다. 전송 순서와 End of Object Pool response 대기 규칙은 [32장](/study/isobus/32-vt-object-pool-basics)에서 봤다. 기술 데이터 메시지(Get Memory 등)의 바이트 배치는 [30장](/study/isobus/30-vt-display-technical-data), 연결 초기화는 [31장](/study/isobus/31-vt-connection), 명령 메시지는 [36장](/study/isobus/36-vt-commands-basics)에서 다룬다.

![오브젝트 풀 전송 순서: WS가 Get Memory로 크기를 알리고 Get Memory response를 받은 뒤, 응답 없는 Object Pool Transfer(0x11 + 레코드)를 세션 1, 세션 2로 이어 보내고, End of Object Pool(12 FF FF FF FF FF FF FF)을 보내면 VT가 parsing 비트를 1로 둔 채 파싱한 다음 End of Object Pool response로 오류 코드와 결함 오브젝트 ID를 돌려주는 흐름](/images/study-isobus/35-pool-transfer-sequence-light.png)
![오브젝트 풀 전송 순서: WS가 Get Memory로 크기를 알리고 Get Memory response를 받은 뒤, 응답 없는 Object Pool Transfer(0x11 + 레코드)를 세션 1, 세션 2로 이어 보내고, End of Object Pool(12 FF FF FF FF FF FF FF)을 보내면 VT가 parsing 비트를 1로 둔 채 파싱한 다음 End of Object Pool response로 오류 코드와 결함 오브젝트 ID를 돌려주는 흐름](/images/study-isobus/35-pool-transfer-sequence-dark.png)

그림은 위에서 아래로 읽는다.

1. WS(Working Set, VT에 화면을 올리는 작업기 쪽 ECU 묶음)가 Get Memory로 보낼 풀의 크기를 알리고, VT 버전과 메모리 여유를 묻는다.
2. Object Pool Transfer 메시지로 레코드를 보낸다. 한 번에 다 보내도 되고 여러 세션으로 나눠도 된다(2절). 이 메시지에는 응답이 없다.
3. 다 보냈으면 End of Object Pool로 "이것이 전부다"라고 알린다.
4. VT는 파싱(받은 바이트를 레코드로 나눠 읽는 일)하는 동안 VT Status message의 parsing 비트를 1로 둔다. 다 끝나면 End of Object Pool response로 결과를 알린다(3절).

쉽게 말하면 상자 여러 개를 일반 우편으로 보내고, 마지막에 "모두 보냈으니 확인해 달라"는 편지를 따로 보내는 것과 같다. 상자 하나하나에는 수령 확인이 오지 않고, 마지막 편지의 답장으로 결과를 한꺼번에 듣는다.

### Object Pool Transfer 메시지의 성질

- Byte 1은 `0x11`(=17)이다. VT 메시지의 첫 바이트(VT function)는 위쪽 4비트가 Command, 아래쪽 4비트가 Parameter인데, `0x11`은 Command `0001`(2진수) = Object Pool Transfer, Parameter `0001` = Object Pool Transfer다. Byte 2부터 레코드가 이어진다.
- 이 메시지에는 <strong>응답이 없다</strong>. 그래서 단일 패킷에 들어가는 작은 오브젝트 하나라도 단일 패킷으로 보내지 않는 것이 권고다(should). 단일 패킷은 CAN 프레임 하나(데이터 8바이트)로 끝나는 전송이다.
  - Object Pointer(5바이트)나 Number Variable(7바이트)은 `0x11`과 합쳐도 8바이트 안에 들어가지만, 그렇게 보내면 VT가 받았는지 알 길이 없다.
  - 8바이트보다 긴 데이터는 TP(Transport Protocol, 긴 데이터를 여러 프레임으로 나눠 보내는 규칙)나 ETP(Extended TP, 1785바이트보다 큰 데이터용)로 보낸다([15장](/study/isobus/15-tp-bam-cmdt), [17장](/study/isobus/17-etp)).
- 풀 전송 메시지는 Working Set Master(WS를 대표해 VT와 통신하는 ECU)만 보낼 수 있다(Member 불가). Member는 같은 WS에 속한 나머지 ECU다([26장](/study/isobus/26-isobus-network-mgmt)).
- 보낸 Master는 응답을 받기 전에는 다음 풀 전송 명령을 보내지 않는다. Object Pool Transfer처럼 응답이 없는 메시지는 End of Object Pool 전까지 이어 보낸다(2절).
- VT는 파싱하다가 이미 있는 Object ID를 다시 만나면 새 레코드를 <strong>교체</strong>로 받아들인다. 같은 전송 안에서도 뒤에 온 레코드가 이긴다.

정리하면, Object Pool Transfer는 보내기만 하는 메시지다. 풀이 제대로 들어갔는지는 마지막의 End of Object Pool과 그 응답으로만 안다.

<small>근거: ISO 11783-6 C.1, C.2.1, C.2.2, C.2.3</small>

## 2. 여러 세션으로 나눠 보내기 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

풀 하나를 꼭 한 세션으로 보낼 필요는 없다. 아래 그림은 레코드 6개짜리 풀을 TP 세션 두 개로 나눈 예와, ETP 한 세션으로 보낸 예를 비교한다.

![세션 나누기 예: 700, 650, 500, 400, 350, 400바이트 레코드 6개(합계 3000바이트)를 쪼개지 않고 0x11을 앞에 붙여 TP 세션 1(700, 650: 1351바이트, TP.DT 193패킷)과 세션 2(500, 400, 350, 400: 1651바이트, 236패킷)로 나눠 TP 한계 1785바이트 안에 넣고, ETP 한 세션이면 3001바이트 429패킷이 되는 모습](/images/study-isobus/35-pool-session-split-light.png)
![세션 나누기 예: 700, 650, 500, 400, 350, 400바이트 레코드 6개(합계 3000바이트)를 쪼개지 않고 0x11을 앞에 붙여 TP 세션 1(700, 650: 1351바이트, TP.DT 193패킷)과 세션 2(500, 400, 350, 400: 1651바이트, 236패킷)로 나눠 TP 한계 1785바이트 안에 넣고, ETP 한 세션이면 3001바이트 429패킷이 되는 모습](/images/study-isobus/35-pool-session-split-dark.png)

- 단일 패킷, TP, ETP 세션을 몇 개든, 섞어서 보낼 수 있다. End of Object Pool을 보내기 전까지 계속 이어 보내면 된다. 세션 하나하나가 Object Pool Transfer 메시지이므로 각 세션은 `0x11`로 시작한다.
- 각 세션 안의 레코드는 <strong>완결돼야 한다</strong>. 레코드 하나를 두 세션에 걸쳐 쪼개면 안 되고, 레코드가 하나도 없는 세션도 안 된다.
- 나누는 이유는 WS의 버퍼 크기, 그리고 전송 전에 스케일과 조정을 해야 하는 경우다.
- 예: 레코드 6개, 합계 3000바이트(예시 값)를 TP(세션당 최대 1785바이트)로 보내면 `0x11` 1바이트를 더해 [700, 650] → 1351바이트(TP.DT 193패킷), [500, 400, 350, 400] → 1651바이트(236패킷) 두 세션이 된다. ETP 한 세션이면 3001바이트(429패킷)다.
  - 세 번째 레코드(500)까지 첫 세션에 넣으면 1 + 700 + 650 + 500 = 1851바이트라 TP 한계를 넘는다. 그래서 둘째 세션으로 넘긴다.
  - TP.DT(TP의 데이터 패킷) 하나는 7바이트를 싣는다. 1351 ÷ 7 = 193, 1651 ÷ 7 = 235.9…를 올림해 236, 3001 ÷ 7 = 428.7…을 올림해 429다.
- 레코드 하나가 1784바이트를 넘으면(큰 Picture Graphic 등) 쪼갤 수 없으므로 그 레코드는 ETP 세션으로 보내야 한다. 1784는 TP 한계 1785에서 `0x11` 1바이트를 뺀 값이다. 표준이 직접 적은 문장은 아니고, "쪼개기 금지"와 TP 한계에서 따라 나오는 결론이다.
- 다른 풀을 받는 중인 VT는 CTS(수신 측이 "이만큼 보내라"고 알리는 TP 제어 메시지)의 패킷 수를 0으로 보내 오래 기다리게 할 수 있다. 이것을 TP 타임아웃이나 연결 실패로 오판하지 않아야 한다(CTS(0)로 연결을 붙잡아 두는 hold 동작은 [16장](/study/isobus/16-tp-connection-rules)).

정리하면, 풀은 여러 세션으로 나눠도 되지만 레코드는 쪼개지 않는다. TP 한 세션에 들어가지 않는 큰 레코드는 ETP로 보낸다.

<small>근거: ISO 11783-6 C.2.2</small>

## 3. End of Object Pool response 읽기

이 절에서는 VT가 풀을 받아들였는지, 거절했다면 어느 오브젝트가 왜 문제인지 알려 주는 응답을 읽는다. 풀 전송이 실패했을 때 가장 먼저 볼 메시지다.

End of Object Pool은 `12 FF FF FF FF FF FF FF`다. 첫 바이트 `0x12`(=18)는 Command `0001` = Object Pool Transfer, Parameter `0010` = Object Pool Ready라는 뜻이고, 응답도 같은 첫 바이트를 쓴다. 최초 전송 뒤뿐 아니라 운영 중에 오브젝트를 바꾸거나 더한 뒤에도 보낸다. VT의 응답은 파싱이 끝날 때까지 미뤄지고, 아래 표와 같은 바이트 배치로 온다.

표 읽는 법은 다음과 같다. Byte 번호는 1부터 센다. Byte 2와 Byte 7은 비트마다 뜻이 있는 오류 비트 묶음이고, bit 0이 가장 낮은 자리다. Object ID는 2바이트 리틀 엔디언(낮은 자리 바이트가 먼저)이다. `FF FF`(=65535)는 "해당 없음"을 뜻하는 값이고, 예약 바이트 `FF`는 나중 버전을 위해 비워 둔 자리다.

| Byte | 내용 |
|---|---|
| 1 | `0x12` |
| 2 | Error Codes(0 = 오류 없음). bit 0 = 풀에 오류가 있다(Byte 3~8 참조), bit 1 = 전송 중 VT 메모리 부족, bit 4 = 기타 오류. bit 2·3·5~7은 예약(0) |
| 3~4 | 결함 오브젝트의 <strong>부모</strong> Object ID. 풀 오류가 없으면 `FF FF` |
| 5~6 | 결함 오브젝트의 Object ID. 풀 오류가 없으면 `FF FF` |
| 7 | Object Pool Error Codes(0 = 오류 없음). bit 0 = VT가 지원하지 않는 방법·속성, bit 1 = 알 수 없는 오브젝트 참조(없는 오브젝트), bit 2 = 기타 오류, bit 3 = 풀을 휘발성 메모리에서 지웠음. bit 4~7은 예약 |
| 8 | 예약(`FF`) |

휘발성 메모리는 전원이 꺼지면 내용이 지워지는 작업용 메모리다. 디코딩 예는 다음과 같다.

- `12 00 FF FF FF FF 00 FF`: 오류 없음. [29장](/study/isobus/29-vt-basics)의 VT 연결 타임라인에 나오는 정상 응답이다.
- `12 01 01 00 0B 00 0A FF`: Byte 2 bit 0, 즉 풀 오류다. 부모는 Data Mask 1, 결함 오브젝트는 Output Number 11이다. Byte 7 = `0A`는 bit 1(알 수 없는 참조)과 bit 3(풀 삭제)이다. [32장](/study/isobus/32-vt-object-pool-basics)의 "엔진 온도" 예제 풀이라면 Output Number 11이 참조하는 Font Attributes 30이 빠졌다고 의심할 수 있다. 예를 들어 세션을 나누다 그 레코드를 빠뜨린 경우다.
  - 한 바이트씩 풀면 `12` = End of Object Pool response, `01` = 0000 0001이라 bit 0, `01 00` = 부모 ID 1, `0B 00` = 결함 오브젝트 ID 11, `0A` = 0000 1010이라 bit 1과 bit 3, 마지막 `FF` = 예약이다.
- `12 02 FF FF FF FF 00 FF`: 전송 중 메모리 부족이다. 더 작은 축소 기능 풀로 Get Memory부터 다시 하는 것이 표준이 드는 대응이다.

오류 응답을 받았을 때의 동작은 수준이 다르다.

- VT는 어떤 오류든 응답에 담았다면 풀을 휘발성 메모리에서 지우고, 알람 방식으로 WS가 중단됐다는 것과 그 이유를 운전자에게 알리는 것이 권고다(should).
- 응답을 받은 책임 ECU는 장치 전체를 안전하게 끄는 절차를 제공하는 fail-safe 모드(고장이 나도 안전한 쪽으로 멈추는 동작)로 들어가는 것이 권고다(should). VT가 무효 풀로 계속 가기로 해도 WS는 오류 표시를 받으면 안전 상태로 갈 수 있다.
- VT는 무효 풀을 바로 알리지 않고 나중에, 예를 들어 무효 참조를 담은 Data Mask를 활성화할 때 VT Change Active Mask message의 오류로 알려도 된다([39장](/study/isobus/39-vt-alarm-activation)). 응답이 `00`이었다고 끝까지 안심할 수는 없다는 뜻이다.

정리하면, Byte 2로 오류 종류를, Byte 3~6으로 문제의 오브젝트를, Byte 7로 원인을 짚는다. 오류 없음 응답도 나중의 오류 통지까지 막아 주지는 않는다.

<small>근거: ISO 11783-6 C.2.1, C.2.2, C.2.4, C.2.5</small>

## 4. 풀을 올린 뒤 일부만 바꾸기: 부분 갱신

이 절에서는 풀을 올린 뒤 오브젝트 몇 개만 바꾸거나 더하는 방법을 본다. 문구 하나를 고치려고 풀 전체를 다시 올리면 시간이 오래 걸리기 때문이다. 초기 업로드와 같은 메시지와 절차를 쓴다.

쉽게 말하면 책 전체를 다시 찍지 않고, 고친 쪽만 새로 인쇄해 같은 쪽 번호 자리에 갈아 끼우는 것과 같다. 쪽 번호(Object ID)가 같으면 교체, 새 번호면 추가다. 책과 다른 점도 있다. 쪽 하나만 빼는(삭제하는) 방법은 없다.

1. Get Memory를 보낸다. Memory Required는 원래 풀에 갱신분을 더한 값이 아니라 <strong>이번 갱신분 크기</strong>다.
2. 바꿀 레코드만 Object Pool Transfer로 보낸다. 같은 ID면 교체, 새 ID면 추가다. 나머지 오브젝트는 VT 메모리에 그대로 있다.
3. End of Object Pool을 보내고, 응답은 최초 전송과 같은 규칙으로 기다린다. parsing 비트가 0인 VT Status message를 연속 3번 받을 때까지 기다리는 규칙이다([32장](/study/isobus/32-vt-object-pool-basics)).

예: [32장](/study/isobus/32-vt-object-pool-basics)의 Output String 10("엔진 온도:")을 "엔진 냉각수 온도:"로 늘리고 폭을 200으로 넓힌다. Value가 22바이트(BOM 2 + 10글자 × 2)라 레코드는 16 + 22 + 1 = 39바이트다. Get Memory는 `C0 FF 27 00 00 00 FF FF`, Object Pool Transfer는 `0x11`을 더해 40바이트라 TP로 가고, 이어서 `12 FF FF FF FF FF FF FF`를 보낸다.

- "엔진 냉각수 온도:"는 공백 두 개와 콜론을 포함해 10글자다. WideString은 글자마다 2바이트이고 앞에 BOM 2바이트가 붙어 22바이트다.
- Output String 레코드는 Value 앞의 고정 부분이 16바이트(32장 표에서 Value가 오프셋 16부터 시작한다), Value 뒤의 매크로 수가 1바이트다. 그래서 16 + 22 + 1 = 39다.
- Get Memory `C0 FF 27 00 00 00 FF FF`는 `C0`(=192) = Get Memory, `FF` = 예약, `27 00 00 00` = Memory Required 0x00000027 = 39(4바이트 리틀 엔디언), 끝의 `FF FF` = 예약이다.
- 40바이트는 단일 패킷(8바이트)에 들어가지 않으므로 TP로 간다.

지켜야 할 규칙은 다음과 같다.

- 교체는 <strong>같은 타입끼리만</strong> 된다. Output String을 Output Number로 바꿀 수는 없다.
- 오브젝트 하나만 지우는 방법은 없다. Delete Object Pool로 풀 전체를 지우고 그 오브젝트를 뺀 풀을 다시 올려야 한다([37장](/study/isobus/37-vt-command-details)).
- 크기를 키우면 VT 메모리가 모자랄 수 있다. 크기나 값만 바꿀 거라면 명령 메시지가 더 빠르다. 예를 들어 Change Size가 새 크기의 레코드를 다시 올리는 것보다 빠르다([37장](/study/isobus/37-vt-command-details)).
- VT는 End of Object Pool을 받을 때까지 새 오브젝트를 원래 풀과 따로 두었다가, 응답을 보내기 전에 합친다. End of Object Pool을 보낸 뒤 응답을 받기 전에 새 오브젝트를 건드리는 명령을 보내면 원래 풀과 갱신된 풀 중 어느 쪽에 적용될지 알 수 없다. 응답을 받은 뒤 보내는 것이 권고다.
- 갱신 중에도 VT는 그 WS의 명령과 매크로를 처리한다. 운전자가 갱신 중에 Soft Key를 누르면 갱신 완료를 기다리지 않고 바로 실행한다.

::: warning 부분 갱신이 실패하면 원래 풀까지 지워진다
갱신에 오류가 있으면 VT는 갱신분만이 아니라 <strong>갱신 전 원래 풀까지</strong> 휘발성 메모리에서 지운다. 부분 갱신이 실패하면 처음부터 다시 올려야 한다.
:::

### 버전에 따라 따라붙는 조건 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

- 갱신으로 보내는 오브젝트도 Get Memory response가 보고한 VT 버전과 호환돼야 한다.
- v4+(VT 버전 4 이상) Window Mask·Key Group을 교체하면 VT가 [34장](/study/isobus/34-vt-layout-color)에서 본 교체 규칙대로 매핑과 화면을 고친다.
- v6 Colour Palette를 교체하면 VT는 팔레트를 표준으로 되돌린 뒤 새 값을 적용한다.
- Store Version(풀을 VT의 비휘발성 메모리에 이름표를 붙여 저장하는 명령)은 명령을 받은 시점의 풀을 현재 속성과 입력값까지 그대로 저장한다. 따라서 부분 갱신을 다음 Load Version(저장한 풀을 불러오는 명령)에도 반영하려면 갱신 뒤 Store Version을 다시 보내야 한다. 표준이 직접 적은 문장은 아니고 앞 문장에서 따라 나오는 추론이다. 버전 라벨 규칙은 [31장](/study/isobus/31-vt-connection)에서 다룬다.

::: details 파이썬으로 세션 분할·응답 디코딩·갱신 크기 검산해 보기
2~4절의 세션 나누기, End of Object Pool response 해석, 부분 갱신 크기를 검산하는 코드다. `split_sessions`는 레코드를 쪼개지 않고 1785바이트 한계 안에서 세션을 나눈다.

```python
import math

TP_MAX = 1785                      # TP 한 세션의 최대 데이터 바이트


def split_sessions(record_sizes, limit=TP_MAX):
    """레코드를 쪼개지 않고 TP 세션에 담는다. 세션마다 맨 앞에 0x11 1바이트."""
    sessions, cur = [], []
    for size in record_sizes:
        if size + 1 > limit:
            raise ValueError("이 레코드는 TP에 안 들어간다. ETP 세션으로 보낸다")
        if cur and 1 + sum(cur) + size > limit:
            sessions.append(cur)
            cur = []
        cur.append(size)
    if cur:
        sessions.append(cur)
    return sessions


records = [700, 650, 500, 400, 350, 400]          # 합계 3000바이트(예시 값)
s = split_sessions(records)
assert s == [[700, 650], [500, 400, 350, 400]]
lengths = [1 + sum(x) for x in s]
assert lengths == [1351, 1651]
assert [math.ceil(n / 7) for n in lengths] == [193, 236]   # TP.DT 패킷 수
assert math.ceil((1 + sum(records)) / 7) == 429            # ETP 한 세션이면


def decode_eop_response(frame):
    b = bytes.fromhex(frame)
    assert b[0] == 0x12
    err = b[1]
    out = {
        "pool_error": bool(err & 0x01),
        "out_of_memory": bool(err & 0x02),
        "other_error": bool(err & 0x10),
        "parent_id": int.from_bytes(b[2:4], "little"),
        "object_id": int.from_bytes(b[4:6], "little"),
    }
    pe = b[6]
    out["pool_codes"] = [name for bit, name in [
        (0, "method/attribute not supported"), (1, "unknown object reference"),
        (2, "any other error"), (3, "pool deleted")] if pe >> bit & 1]
    return out


ok = decode_eop_response("12 00 FF FF FF FF 00 FF")
assert not (ok["pool_error"] or ok["out_of_memory"] or ok["other_error"])
assert ok["parent_id"] == ok["object_id"] == 0xFFFF

bad = decode_eop_response("12 01 01 00 0B 00 0A FF")
assert bad["pool_error"] and (bad["parent_id"], bad["object_id"]) == (1, 11)
assert bad["pool_codes"] == ["unknown object reference", "pool deleted"]

oom = decode_eop_response("12 02 FF FF FF FF 00 FF")
assert oom["out_of_memory"] and not oom["pool_error"]


# C.2.6 런타임 갱신: Output String 10을 더 긴 글자로 교체(같은 타입, 폭 200)
le = lambda v, n: v.to_bytes(n, "little")
value = b"\xFF\xFE" + "엔진 냉각수 온도:".encode("utf-16-le")
new_os = (le(10, 2) + bytes([11]) + le(200, 2) + le(30, 2) + bytes([1]) + le(30, 2)
          + bytes([0]) + le(0xFFFF, 2) + bytes([0]) + le(len(value), 2) + value + bytes([0]))
assert len(value) == 22 and len(new_os) == 39
get_memory = bytes([0xC0, 0xFF]) + le(len(new_os), 4) + b"\xFF\xFF"
assert get_memory.hex(" ").upper() == "C0 FF 27 00 00 00 FF FF"   # 갱신분 크기만
assert len(bytes([0x11]) + new_os) == 40                          # 8바이트를 넘어 TP로
print("전송 계산 검산 통과")
```

실행하면 `전송 계산 검산 통과`가 출력된다. `split_sessions`의 결과가 2절 그림과 같은 [700, 650], [500, 400, 350, 400]이 되는지, 세 응답 예가 3절의 해석과 같은지를 확인한다.
:::

정리하면, 부분 갱신은 바꿀 레코드만 같은 순서(Get Memory, Object Pool Transfer, End of Object Pool)로 보내는 일이다. 같은 타입끼리만 교체되고, 실패하면 원래 풀까지 사라진다.

<small>근거: ISO 11783-6 4.6.10.3, 4.6.28, 4.7.16, B.26, C.2.2, C.2.6, E.4</small>

## 5. 글자 집합 규칙이 왜 필요한가

이 절에서는 VT가 문자열 바이트를 글자로 바꾸는 큰 그림을 본다. 바이트는 숫자일 뿐이라, 같은 바이트를 어느 나라 글자로 읽을지 약속이 없으면 화면에 엉뚱한 글자가 나온다.

예를 들어 바이트 `A4`(=164)는 ISO 8859-1(서유럽 글자 표)로 읽으면 `¤`(일반 통화 기호)이고, ISO 8859-15로 읽으면 `€`(유로 기호)다. VT는 유럽, 러시아, 그리스 등 여러 나라에서 쓰이므로, 문자열마다 어느 표로 읽을지 알려 줘야 한다. 한글처럼 8비트 표에 아예 없는 글자는 유니코드로 적어야 한다.

쉽게 말하면 암호표와 같다. 같은 숫자 열도 어떤 암호표로 푸느냐에 따라 다른 글자가 된다. 8비트 문자열은 256칸짜리 작은 표 여러 개 가운데 하나를 골라 쓰고, WideString은 세계 거의 모든 글자를 담은 큰 표(유니코드)를 쓴다. 256칸짜리 표 하나를 흔히 코드 페이지라고 부른다.

VT 문자열은 다음 두 갈래로 해석된다.

| 갈래 | 한 글자 크기 | 어느 표로 읽나 | 쓸 수 있는 VT |
|---|---|---|---|
| 8비트 문자열 | 1바이트 | 그 문자열이 쓰는 Font Attributes의 Font type이 고른 ISO 8859 계열 표 | 모든 버전 |
| WideString | 2바이트(U+FFFF를 넘는 글자는 4바이트) | 유니코드(UTF-16 리틀 엔디언) | v4 이상 |

![문자열 해석 흐름: 문자열 바이트의 첫 두 바이트가 FF FE이면 WideString(UTF-16 리틀 엔디언, Font type은 무시)으로 읽어 지원하는 글자는 그대로, 지원하지 않는 글자는 대체 문자로 표시하고, 아니면 8비트 문자열로 읽어 Font type이 고른 ISO 8859-1, -15, -2, -4, -5, -7 표로 해석하는 흐름](/images/study-isobus/35-string-decode-flow-light.png)
![문자열 해석 흐름: 문자열 바이트의 첫 두 바이트가 FF FE이면 WideString(UTF-16 리틀 엔디언, Font type은 무시)으로 읽어 지원하는 글자는 그대로, 지원하지 않는 글자는 대체 문자로 표시하고, 아니면 8비트 문자열로 읽어 Font type이 고른 ISO 8859-1, -15, -2, -4, -5, -7 표로 해석하는 흐름](/images/study-isobus/35-string-decode-flow-dark.png)

VT가 두 갈래를 구분하는 법은 간단하다. 문자열의 첫 두 바이트가 `FF FE`(BOM)이면 WideString, 아니면 8비트 문자열이다. [32장](/study/isobus/32-vt-object-pool-basics)의 Output String "엔진 온도:"가 WideString이 된 것도 한글 때문이다. 한글은 어떤 ISO 8859 표에도 없다.

정리하면, 8비트 문자열은 짧지만 고른 표 하나에 든 글자만 쓸 수 있고, WideString은 길지만 거의 모든 글자를 적을 수 있다. 다만 VT가 그 글자를 실제로 그릴 수 있는지는 따로 확인해야 한다(8절).

<small>근거: ISO 11783-6 4.6.19.7, Annex K</small>

## 6. 8비트 문자열과 Font type (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

8비트 문자열의 인코딩은 그 문자열이 쓰는 Font Attributes의 Font type이 정한다. 값별 문자 표는 다음과 같다.

| Font type | 문자 표 | 주로 쓰는 글자 |
|---|---|---|
| 0 | ISO 8859-1(Latin 1) | 서유럽 |
| 1 | ISO 8859-15(Latin 9) | 서유럽(유로 기호 포함) |
| 2 | ISO 8859-2(Latin 2) | 중유럽 |
| 4 | ISO 8859-4(Latin 4) | 북유럽·발트 |
| 5 | ISO 8859-5 | 키릴 문자 |
| 7 | ISO 8859-7 | 그리스 문자 |
| 3, 6, 8~239 | 예약 | |
| 240~255 | 제조사 고유 | |

- v3 이하 VT에는 2·4·5·7과 240~254가 정의돼 있지 않았다. Font type으로 쓸 수 있는 값은 0, 1, 255뿐이었다.
- Latin 1과 Latin 9는 8칸만 다르다. 8비트 문자열에 유로 기호가 필요하면 Font type 1을 쓴다.

| 바이트 | Latin 1(Font type 0) | Latin 9(Font type 1) |
|---|---|---|
| `A4` | ¤ | € |
| `A6` | ¦ | Š |
| `A8` | ¨ | š |
| `B4` | ´ | Ž |
| `B8` | ¸ | ž |
| `BC` | ¼ | Œ |
| `BD` | ½ | œ |
| `BE` | ¾ | Ÿ |

- v2 이하 VT의 ISO 8859-15 표에는 `A6`·`A8`·`B4`·`B8` 네 칸에 오류가 있었고 v3에서 고쳐졌다.
- 두 표 공통으로 LF(`0x0A`(=10), 다음 줄로)와 CR(`0x0D`(=13), 줄 처음으로)은 [34장](/study/isobus/34-vt-layout-color) 3절의 줄 끝 규칙을 따르고, `0x00`은 표시를 끝내며, 그 밖의 제어 코드는 표시하지 않는다. NBSP(`0xA0`(=160), 줄을 나누지 않는 공백)에는 줄바꿈 규칙이 적용되지 않는다.

<small>근거: ISO 11783-6 B.14.2, Annex K(Table K.1~K.3)</small>

## 7. WideString: 유니코드 문자열 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

- v4+에서 쓸 수 있다. UTF-16 <strong>리틀엔디언</strong>이고 항상 BOM(U+FEFF)으로 시작하므로 바이트로는 `FF FE`로 시작한다. BOM은 표시되는 글자가 아니고 문자열에 포함되지도 않는다.
  - UTF-16은 유니코드 글자 하나를 2바이트(일부는 4바이트)로 적는 방식이다. "U+"로 시작하는 표기는 유니코드 글자 번호(16진수)다.
  - U+FEFF를 리틀 엔디언으로 적으면 낮은 자리 바이트 `FF`가 먼저라 `FF FE`가 된다.
- VT는 첫 두 바이트가 `FF FE`이면 WideString, 아니면 8비트 문자열로 판별한다. WideString에는 Font type이 무시된다.
- Length 속성은 언제나 바이트 수다. 글자 수 = Length ÷ 2 − 서로게이트 쌍 수 − 1(BOM)이다. "엔진 온도:"는 Length 14라 14 ÷ 2 − 0 − 1 = 6글자다. Length가 홀수면 마지막 바이트는 무시한다.
- U+FFFF를 넘는 글자는 32비트 서로게이트 쌍으로 쓴다. 서로게이트 쌍은 2바이트 단위 두 개를 짝지어 글자 하나를 나타내는 방식이다. S = 코드 − `0x10000`(=65,536), 상위 = `0xD800`(=55,296) + (S >> 10), 하위 = `0xDC00`(=56,320) + (S의 하위 10비트)다. `>> 10`은 오른쪽으로 10비트 밀기, 즉 1,024로 나눈 몫이다.
  - U+1F69C(트랙터 그림 문자)는 `D83D DE9C`라 BOM을 포함한 바이트열이 `FF FE 3D D8 9C DE`가 된다.
  - 계산을 따라가면 S = `0x1F69C` − `0x10000` = `0xF69C`다. 상위는 `0xD800` + (`0xF69C` >> 10) = `0xD800` + `0x3D` = `0xD83D`, 하위는 `0xDC00` + `0x29C` = `0xDE9C`다(`0x29C`는 `0xF69C`의 하위 10비트). 두 값을 각각 리틀 엔디언으로 적으면 `3D D8`, `9C DE`다.
  - 유니코드 최댓값 U+10FFFF는 `DBFF DFFF`다.
- VT는 지원하지 않는 글자가 섞여 있어도 WideString을 표시해야 하며, 그 글자는 표시 가능한 대체 문자로 바꾼다. 대체 문자의 모양은 VT가 정한다.
- Input String(운전자가 글자를 입력하는 칸)이 WideString을 담고 있으면 VT가 보내는 VT Change String Value message도 WideString이어야 한다. VT는 문자열 형식을 바꾸지 않는다. 반면 WS는 8비트와 WideString을 오갈 수 있다. Input Attributes(8비트)와 Extended Input Attributes(WideString)도 값과 형식이 맞아야 입력 검증이 일어난다. 두 오브젝트는 입력 칸에 넣을 수 있는 글자를 제한한다.
- WideString의 배치는 유니코드 렌더링 엔진에 맡겨지므로 [34장](/study/isobus/34-vt-layout-color) 3절의 줄바꿈·비인쇄 문자 규칙과 다를 수 있다. 정렬은 유지될 것으로 기대한다. 유니코드 제어 코드가 오브젝트 속성과 충돌하면 (지원하는 경우) 제어 코드가 이긴다.

<small>근거: ISO 11783-6 3.12, 4.6.19.1, 4.6.19.7, B.8.3</small>

## 8. 한글을 띄우려면: 최소 문자 집합과 Get Supported WideChars

이 절에서는 한국어 화면을 만들 때 실제로 무엇을 확인해야 하는지 본다. WideString으로 한글을 적을 수는 있어도, VT가 한글을 그리지 못하면 대체 문자로 보인다.

v4+ VT가 WideString에서 반드시 표시해야 하는 글자는 표준이 정한 최소 집합이다. 표준이 Get Supported WideChars 응답 예로 든 범위가 그 집합을 보여 준다.

- 기본 라틴(U+0020~007E)
- 라틴-1 보충과 라틴 확장-A(U+00A0~017E)
- 발음 구별 기호류(U+02C6~02DD 중 일부)
- 그리스 문자(U+037E~03CE 중 일부)
- 키릴 문자(U+0401~045F 중 일부)
- 유로 기호(U+20AC)

<strong>한글 음절(U+AC00~D7A3)은 최소 집합에 없다.</strong> [32장](/study/isobus/32-vt-object-pool-basics)의 "엔진 온도:"는 한글을 지원하지 않는 VT에서 대체 문자로 보인다. 한국어 화면을 만드는 WS는 다음 순서로 대응한다.

1. Get Supported WideChars(v4+)로 묻는다. 요청 하나는 코드 플레인 하나의 범위만 다룬다. 코드 플레인은 유니코드 글자를 65,536자씩 나눈 구역이고, 한글 음절은 0번 플레인에 있다. 한글 음절이면 코드 플레인 0, U+AC00~U+D7A3이라 `C1 00 00 AC A3 D7 FF FF`다. 응답은 (첫 글자, 끝 글자) 범위의 배열이고, 하위 범위가 255개를 넘으면 "Too many ranges" 오류가 오므로 범위를 나눠 다시 묻는다. 응답 바이트 배치는 [30장](/study/isobus/30-vt-display-technical-data)에서 다룬다.
   - 요청을 풀면 `C1`(=193) = Get Supported WideChars, `00` = 코드 플레인 0, `00 AC` = 첫 글자 U+AC00(리틀 엔디언), `A3 D7` = 끝 글자 U+D7A3, `FF FF` = 예약이다.
2. 지원하지 않으면 다른 언어나 인코딩으로 보내거나, 글자를 Picture Graphic(비트맵 그림)으로 그린다. 표준이 직접 드는 대안이다.
3. 지원하더라도 작은 폰트에서는 획이 많은 글자가 뭉개져 읽히지 않을 수 있다. 표준은 고해상도 표의문자(한자처럼 획이 많은 글자)를 예로 들어 이 점을 경고한다.

이 질의는 의무가 아니다. VT가 지원하지 않는 글자가 섞인 WideString도 대체 문자로 표시하기 때문이다. 다만 운전자가 읽어야 하는 경고 문구라면 확인하지 않고 보내는 것은 위험하다.

::: details 원문을 가진 독자를 위한 메모
- 최소 문자 집합은 Annex K의 Table K.8에 있다. 위 범위 목록은 D.11의 예시 응답에서 옮겼다.
- 작은 폰트에서 고해상도 표의문자가 뭉개지는 예는 4.6.19.1 Figure 16이다.
- "ABC" 예(검산 코드의 `3.12의 예`)는 3.12의 WideString 용어 정의에 있고, 글자 수 식은 4.6.19.7에 있다.
:::

::: details 파이썬으로 Latin 1/9 차이·WideString 길이·서로게이트 쌍 검산해 보기
6~8절의 Latin 1/9 차이, WideString 글자 수 계산, 서로게이트 쌍, Get Supported WideChars 요청을 검산하는 코드다. `wide`는 BOM을 붙인 UTF-16LE 바이트열을 만든다.

```python
# Annex K: Font type 0(ISO 8859-1)과 1(ISO 8859-15)이 다른 칸
diff = [b for b in range(0xA0, 0x100)
        if bytes([b]).decode("latin-1") != bytes([b]).decode("iso8859-15")]
assert [hex(b) for b in diff] == ["0xa4", "0xa6", "0xa8", "0xb4", "0xb8", "0xbc", "0xbd", "0xbe"]
assert bytes([0xA4]).decode("iso8859-15") == "€"      # 유로 기호
assert "1.000 €".encode("iso8859-15") == b"1.000 \xa4"


def wide(text):
    """4.6.19.7 WideString: BOM(FEFF)을 리틀엔디언으로 붙인 UTF-16LE"""
    return b"\xFF\xFE" + text.encode("utf-16-le")


def wide_char_count(data):
    length = len(data) - len(data) % 2           # 홀수 길이면 마지막 바이트는 버린다
    units = [int.from_bytes(data[i:i + 2], "little") for i in range(0, length, 2)]
    pairs = sum(1 for u in units if 0xD800 <= u <= 0xDBFF)
    return length // 2 - pairs - 1               # number of WideChar = length/2 - 서로게이트 쌍 - 1


assert wide_char_count(wide("엔진 온도:")) == 6
assert wide_char_count(wide("ABC")) == 3 and len(wide("ABC")) == 8   # 3.12의 예


def surrogate(cp):
    s = cp - 0x10000
    return 0xD800 + (s >> 10), 0xDC00 + (s & 0x3FF)


assert surrogate(0x1F69C) == (0xD83D, 0xDE9C)               # U+1F69C(트랙터 그림 문자)
assert surrogate(0x10FFFF) == (0xDBFF, 0xDFFF)              # 최댓값
tractor = wide(chr(0x1F69C))
assert tractor.hex(" ").upper() == "FF FE 3D D8 9C DE"
assert wide_char_count(tractor) == 1

# 8비트 문자열과 구분: 첫 두 바이트가 FF FE인가
assert wide("A")[:2] == b"\xFF\xFE" and b"Speed"[:2] != b"\xFF\xFE"

# Get Supported WideChars(D.10)로 한글 음절(U+AC00~U+D7A3) 지원 여부를 묻는 요청
req = bytes([0xC1, 0x00]) + (0xAC00).to_bytes(2, "little") + (0xD7A3).to_bytes(2, "little") + b"\xFF\xFF"
assert req.hex(" ").upper() == "C1 00 00 AC A3 D7 FF FF"
print("문자 집합 검산 통과")
```

실행하면 `문자 집합 검산 통과`가 출력된다. `diff` 목록이 6절 표의 여덟 칸과 같고, 트랙터 그림 문자의 바이트열이 7절의 `FF FE 3D D8 9C DE`와 같은지 확인한다.
:::

정리하면, 한글은 VT가 반드시 갖춰야 하는 글자에 들어 있지 않다. 한국어 문구를 쓰려면 Get Supported WideChars로 먼저 확인하고, 지원하지 않으면 그림 같은 대안을 쓴다.

<small>근거: ISO 11783-6 4.6.19.1, D.10, D.11, Annex K(Table K.8)</small>

::: tip 핵심 정리
- Object Pool Transfer(`0x11`)에는 응답이 없다. 다 보낸 뒤 End of Object Pool(`0x12`)을 보내고, 그 응답으로 풀이 제대로 들어갔는지 듣는다.
- 풀은 여러 세션으로 나눠 보낼 수 있지만, 레코드 하나를 두 세션에 쪼개 실으면 안 된다.
- End of Object Pool response는 Byte 2(오류 종류), Byte 3~6(부모와 결함 오브젝트 ID), Byte 7(풀 오류 원인)로 원인을 짚는다. 부분 갱신이 실패하면 원래 풀까지 지워진다.
- 문자열 첫 두 바이트가 `FF FE`이면 WideString(UTF-16), 아니면 Font type이 고른 8비트 문자 표로 읽는다.
- 한글은 WideString 최소 집합 밖이다. Get Supported WideChars로 확인하고, 없으면 Picture Graphic 같은 대안을 쓴다.
:::

::: details 확인 문제
1. Object Pool Transfer 메시지에 응답이 없다면, WS는 VT가 풀을 다 받아들였는지 어떻게 아는가?
2. 1000바이트와 900바이트짜리 레코드 두 개를 TP로 보내려 한다. TP 세션이 몇 개 필요하고, 각 세션의 길이는 몇 바이트인가?
3. 어떤 문자열 바이트가 `FF FE 41 00`이다. VT는 이 문자열을 어떻게 해석하는가? `41 42`라면 어떻게 해석하는가?
4. (장애 진단) [33장](/study/isobus/33-vt-object-records)의 예제 풀(Container 20 안에 Input Number 21이 있고, Input Number 21은 Number Variable 23과 Font Attributes 30을 참조한다)을 올렸더니 End of Object Pool response가 `12 01 14 00 15 00 02 FF`로 왔다. 무엇이 문제이고 어디부터 확인하는가? 풀은 VT에 남아 있는가?

**답 가이드**
1. 레코드를 다 보낸 뒤 End of Object Pool(`12 FF FF FF FF FF FF FF`)을 보내고, VT가 파싱을 마친 뒤 보내는 End of Object Pool response를 읽는다. Byte 2가 0이면 오류 없음이다.
2. 두 세션이다. 1 + 1000 + 900 = 1901바이트라 TP 한계 1785바이트를 넘고, 레코드는 쪼갤 수 없기 때문이다. 세션마다 `0x11`이 붙어 1001바이트와 901바이트가 된다.
3. `FF FE 41 00`은 첫 두 바이트가 BOM이라 WideString이다. 뒤의 `41 00`은 U+0041, 즉 "A" 한 글자다. `41 42`는 8비트 문자열이라 그 문자열의 Font type이 고른 표로 읽는다. ISO 8859 계열 표는 이 범위가 모두 같아 "AB"다.
4. Byte 2 bit 0 = 풀 오류다. 부모 = `14 00` = Container 20, 결함 오브젝트 = `15 00` = Input Number 21이다. Byte 7 = `02` = bit 1, 알 수 없는 오브젝트 참조다. Input Number 21이 참조하는 Number Variable 23이나 Font Attributes 30의 레코드가 어느 세션에서도 전송되지 않았는지(또는 ID가 어긋났는지) 먼저 확인한다. Byte 7 bit 3이 0이므로 VT가 풀을 지웠다고 알린 것은 아니다. 그래도 WS는 오류를 받은 이상 안전 상태로 갈 수 있고, 고친 풀을 다시 올려야 한다.
:::

## 다음 챕터

- 다음: [36장 VT 명령어 기초](/study/isobus/36-vt-commands-basics)
