---
title: "트랙터-작업기 메시지 (3): 언어 설정, 안전 메시지, Part 7 요약"
description: "언어·단위 설정을 알리는 Language command, 메시지 주기를 바꾸는 요청, 작업기 전체 정지 스위치(ISB)와 Heartbeat 같은 안전 메시지를 읽고 검증하는 법을 익히고, Part 7 메시지를 한 표로 정리한다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, LanguageCommand, Heartbeat, ISB, OperatorStatus]
prev: /study/isobus/24-hitch-pto-valve-control
next: /study/isobus/26-isobus-network-mgmt
---

# 트랙터-작업기 메시지 (3): 언어 설정, 안전 메시지, Part 7 요약

::: info 학습 목표
- Language command 8바이트를 읽고 언어, 날짜·시간 형식, 단위를 풀어낼 수 있다.
- 언어 설정을 누가 보내고 누가 따르는지, 보내는 장치가 여럿일 때 어느 값을 써야 하는지 설명할 수 있다.
- 메시지 주기를 바꿔 달라는 요청과 응답, 250 ms 규칙을 설명할 수 있다.
- 작업기 전체 정지 스위치(ISB) 메시지의 상태와 전이 횟수로 놓친 정지를 알아내는 방법을 설명할 수 있다.
- Heartbeat 시퀀스 번호와 300 ms 간격 규칙으로 수신 측이 통신 오류를 판정하는 과정을 단계별로 따라갈 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [23장 트랙터-작업기 메시지 (1)](/study/isobus/23-implement-messages-basics), [22장 트랙터 ECU](/study/isobus/22-tractor-ecu), [10장 요청과 응답](/study/isobus/10-j1939-request-ack)
- 이 장에서 처음 나오는 말
  - Language command(언어 명령): 화면에 쓸 언어, 날짜·시간 형식, 단위를 버스 전체에 알리는 메시지
  - 반복 주기(repetition rate): 같은 메시지를 몇 ms마다 다시 보내는지를 나타내는 값
  - ISB(작업기 전체 정지 스위치): 운전자가 연결된 모든 작업기를 한 번에 멈추게 하는 스위치
  - Heartbeat(하트비트): 요청을 받으면 1바이트 일련번호를 100 ms마다 보내 "보내는 쪽이 지금도 정상"임을 알리는 메시지
  - 안전 상태(safe state): 오류를 알아챈 장치가 사람과 기계를 위험하게 하지 않도록 옮겨 가는 상태
  - Amd1: Part 7 2015년판을 고친 2018년 개정(Amendment 1)
:::

공장의 생산 라인을 떠올려 보자. 기계마다 화면이 있지만 모두 작업자가 고른 언어와 단위로 표시돼야 하고, 비상 정지 버튼을 누르면 라인 전체가 멈춰야 하며, 감독 장치는 각 기계가 아직 살아서 제대로 일하는지 계속 확인해야 한다. 트랙터에 여러 제조사의 작업기가 연결된 ISOBUS 시스템도 같은 일이 필요하다. 이 장은 ISO 11783-7(트랙터와 작업기가 주고받는 메시지를 정하는 표준 문서, 이하 Part 7) 가운데 이 세 가지 일을 맡는 메시지를 보고, 마지막에 23~25장에서 본 Part 7 메시지 전체를 한 표로 정리한다.

## 1. Language command: 언어, 날짜, 단위를 한 번에 알린다

이 절에서는 화면에 쓸 언어, 숫자·날짜·시간 형식, 측정 단위를 버스 전체에 알리는 메시지를 바이트 단위로 읽는다. 작업기 화면이 운전자가 고른 언어로 나올지, 살포량이 리터로 보일지 갤런으로 보일지가 이 메시지 하나로 정해진다.

ISOBUS에서는 여러 제조사의 작업기가 운전석의 화면 하나를 함께 쓴다. 작업기마다 언어와 단위를 따로 고르게 하면 운전자는 같은 설정을 기기마다 되풀이해야 하고, 한 화면 안에서 미터법과 영미식 단위가 섞일 수도 있다. 그래서 설정을 한곳에서 정하고 모두에게 알린다.

쉽게 말하면 스마트폰의 "언어 및 지역" 설정과 같다. 휴대폰에서 언어와 단위를 한 번 정하면 모든 앱이 그 설정을 따르듯, Language command는 연결된 모든 장치에 같은 설정을 알린다. 다른 점은 앱은 운영체제에 물어보지만, ISOBUS의 장치는 버스로 방송된 메시지를 받아서 안다는 것이다.

정확히 말하면 Language command는 PGN(Parameter Group Number, 메시지 종류를 가리키는 번호) 65039(`0xFE0F`), 우선순위 6(0이 가장 높고 7이 가장 낮다)의 방송 메시지다. 방송은 받는 쪽을 정하지 않고 버스의 모든 CF(Control Function, 버스에 주소 하나를 갖고 참여하는 기능 단위)에게 보낸다는 뜻이다. 연결된 시스템이 쓸 언어, 날짜·시간 형식, 측정 단위를 알리고, 시스템 초기화 때와 요청을 받았을 때 보낸다.

### 바이트 배치

그림과 목록을 읽는 법부터 정하자. 데이터 8바이트는 앞에서부터 Byte 1~8로 센다. 한 바이트 안의 비트는 가장 높은 자리가 bit 8, 가장 낮은 자리가 bit 1이다. 그래서 "bits 8,7"은 바이트를 2진수로 썼을 때 맨 왼쪽 두 자리다. 2비트 필드에서 `11`은 대부분 "조치 없음", 곧 지금 설정을 바꾸지 말라는 뜻이다. 예약(reserved)은 나중 판에서 쓰려고 비워 둔 자리이고, 보낼 때는 1로 채운다. 아래 그림은 미국 영어(en-US) 설정의 예다.

![Language command(PGN 65039) 바이트 배치: Byte 1~2 언어 코드 'en', Byte 3 소수점·시간 형식, Byte 4 날짜 형식, Byte 5~6 단위 2비트 필드 여덟 개, Byte 7~8 국가 코드 'US'](/images/study-isobus/13-p7-language-command-layout-light.png)
![Language command(PGN 65039) 바이트 배치: Byte 1~2 언어 코드 'en', Byte 3 소수점·시간 형식, Byte 4 날짜 형식, Byte 5~6 단위 2비트 필드 여덟 개, Byte 7~8 국가 코드 'US'](/images/study-isobus/13-p7-language-command-layout-dark.png)

- Bytes 1,2: 언어 코드. ISO 639(언어를 두 글자로 나타내는 국제 표준) 코드를 7비트 ISO Latin 1 문자(영문자 같은 기본 문자를 7비트 숫자로 나타내는 문자 코드)로 싣는다(예: nl 네덜란드어, fr 프랑스어, en 영어, de 독일어). Amd1은 소문자라고 못박았다. 문자열이므로 왼쪽 문자가 Byte 1이다. 'e'의 문자 코드는 `0x65`, 'n'은 `0x6E`이므로 영어는 `65 6E`다.
- Byte 3: bits 8,7 소수점 기호(00 쉼표, 01 마침표, 11 조치 없음), bits 6,5 시간 형식(00 24시간, 01 12시간 am/pm, 11 조치 없음), bits 4~1 예약. 두 필드 모두 10은 예약이다.
- Byte 4: 날짜 형식. 0 ddmmyyyy, 1 ddyyyymm, 2 mmyyyydd, 3 mmddyyyy, 4 yyyymmdd, 5 yyyyddmm, 6~250 예약. dd는 일, mm은 월, yyyy는 연도다.
- Byte 5: 거리·면적·부피·질량, Byte 6: 온도·압력·힘·단위계(units system). 각 2비트로 00 미터법, 11 조치 없음이다. 거리·면적·온도·압력·힘은 01이 Imperial/US 공통이고, 부피·질량·단위계만 01 Imperial과 10 US를 구분한다. 원문 값 설명이 Imperial gallon과 US gallon, long ton과 short ton을 나눠 적는다. 단위계는 앞의 일곱 항목에 없는 단위를 표시할 때 쓸 체계다.
- Bytes 7,8: Amd1이 예약 자리에 넣은 국가 코드. ISO 3166-1(나라를 두 글자로 나타내는 국제 표준) alpha-2 대문자이고, 두 문자 모두 전부 1이면 국가 코드 미지정이다. es-MX(멕시코 스페인어)·es-AR(아르헨티나 스페인어)처럼 같은 언어의 지역 방언을 구분할 때 쓴다.

Byte 5와 Byte 6은 2비트 필드 네 개씩이 한 바이트를 채운다. 어느 비트가 어느 단위인지와 값의 뜻을 표로 모으면 이렇다.

| 바이트 | bits 8,7 | bits 6,5 | bits 4,3 | bits 2,1 |
|---|---|---|---|---|
| Byte 5 | 거리 | 면적 | 부피 | 질량 |
| Byte 6 | 온도 | 압력 | 힘 | 단위계 |

| 값 | 거리·면적·온도·압력·힘 | 부피·질량·단위계 |
|---|---|---|
| 00 | 미터법(km, ha, °C, kPa, N) | 미터법(L, t) |
| 01 | Imperial/US 공통(마일, 에이커, °F, psi, 파운드힘) | Imperial(영국 갤런, long ton) |
| 10 | 예약 | US(미국 갤런, short ton) |
| 11 | 조치 없음 | 조치 없음 |

Imperial은 영국식 단위, US는 미국식 단위다. 마일, 에이커, 화씨처럼 두 나라가 같은 단위를 쓰는 항목은 01 하나로 묶는다. 이름이 같아도 양이 다른 갤런(영국 갤런이 미국 갤런보다 크다)과 톤(long ton이 short ton보다 무겁다)은 01과 10으로 나눈다.

국가 코드에는 숨은 장점이 하나 있다. Amd1 이전 판을 따르는 송신기는 Bytes 7,8에 예약값 `FF FF`(모든 비트가 1)를 채운다. 이 값이 그대로 "국가 코드 미지정"으로 읽히므로 옛 장치와 새 장치가 섞여도 문제가 없다. 표준이 이 효과를 따로 적지는 않았고, 값의 정의에서 따라 나오는 결과다.

### 코드로 만들어 보기

아래 코드는 이 배치대로 8바이트를 만드는 함수와 두 가지 예다. `build_language()`는 언어 코드, 소수점·시간 형식(2비트씩), 날짜 형식, Byte 5와 Byte 6에 들어갈 2비트 값 네 개씩, 국가 코드를 받는다. 독일(de-DE, 모두 미터법)과 미국(en-US) 설정을 만들어 결과 바이트를 확인한다.

```python
def build_language(lang, dec, tfmt, datefmt, units5, units6, country=None) -> bytes:
    b3 = (dec << 6) | (tfmt << 4) | 0x0F                      # bits 4~1 예약 = 1
    b5 = (units5[0] << 6) | (units5[1] << 4) | (units5[2] << 2) | units5[3]
    b6 = (units6[0] << 6) | (units6[1] << 4) | (units6[2] << 2) | units6[3]
    cc = country.encode("ascii") if country else b"\xff\xff"
    return lang.encode("ascii") + bytes([b3, datefmt, b5, b6]) + cc


de_de = build_language("de", 0b00, 0b00, 0, (0, 0, 0, 0), (0, 0, 0, 0), "DE")
assert de_de.hex(" ").upper() == "64 65 0F 00 00 00 44 45"
en_us = build_language("en", 0b01, 0b01, 3, (0b01, 0b01, 0b10, 0b10), (0b01, 0b01, 0b01, 0b10), "US")
assert en_us.hex(" ").upper() == "65 6E 5F 03 5A 56 55 53"
assert get_bits(en_us, 5, 3, 2) == 0b10                       # 부피: US gallon
```

`assert` 줄은 결과가 기대한 값과 같은지 확인하는 검사다. 마지막 줄의 `get_bits(데이터, 바이트 번호, 시작 비트, 길이)`는 [23장](/study/isobus/23-implement-messages-basics)에서 만든 도우미로, 지정한 바이트의 시작 비트(가장 낮은 비트)부터 길이만큼 꺼낸다. 여기서는 Byte 5 bits 4,3(부피)이 `10`, 곧 US 갤런인지 본다.

en-US 설정 `65 6E 5F 03 5A 56 55 53`을 한 바이트씩 읽으면 다음과 같다.

1. `65 6E`: 'e', 'n'이므로 영어다.
2. `5F` = `01 01 1111`: 소수점은 마침표(01), 시간은 12시간 am/pm(01), 하위 4비트는 예약(1111)이다.
3. `03`: 날짜 형식 3, 곧 mmddyyyy(월, 일, 연도 순)다.
4. `5A` = `01 01 10 10`: 거리 01(마일), 면적 01(에이커), 부피 10(US 갤런), 질량 10(US short ton)이다.
5. `56` = `01 01 01 10`: 온도 01(화씨), 압력 01(psi), 힘 01(파운드힘), 단위계 10(US)이다.
6. `55 53`: 'U', 'S'이므로 미국이다.

<small>근거: ISO 11783-7 B.21, A.23.1~A.23.5, Amd1 A.23.1.1, A.23.1.2</small>

## 2. 언어 설정은 누가 보내고 누가 따르는가

1절에서 바이트 형식을 봤다. 그런데 형식만 알아서는 부족하다. 이 메시지를 보낼 수 있는 장치가 여럿이고, 받는 장치마다 따라야 할 값이 다르기 때문이다. 이 절은 VT, TECU, TC, 작업기가 언어 설정을 어떻게 나눠 맡는지 본다.

등장하는 장치는 넷이다. VT(Virtual Terminal)는 운전석에 놓인 공용 화면 단말이고, TECU(Tractor ECU)는 트랙터를 버스에 대표하는 ECU다. TC(Task Controller)는 작업 기록과 살포량 같은 공정 데이터를 관리하는 장치이고, Working Set은 작업기 하나를 이루는 CF 묶음이다.

![언어 설정이 흐르는 길: 운전자가 VT에서 고르고, 고른 적이 없으면 VT가 TECU에 기본 언어를 요청한다. VT의 Language command를 Working Set과 TC가 따르고, TC는 다시 TC 클라이언트에 알리며, TC 클라이언트는 Bytes 1~6을 복사해 Localization label을 만든다](/images/study-isobus/25-language-setup-flow-light.png)
![언어 설정이 흐르는 길: 운전자가 VT에서 고르고, 고른 적이 없으면 VT가 TECU에 기본 언어를 요청한다. VT의 Language command를 Working Set과 TC가 따르고, TC는 다시 TC 클라이언트에 알리며, TC 클라이언트는 Bytes 1~6을 복사해 Localization label을 만든다](/images/study-isobus/25-language-setup-flow-dark.png)

그림을 한 줄로 줄이면, 설정은 VT에서 출발한다. 작업기 화면은 자기를 띄운 VT를 따르고, TC는 VT에서 받은 설정을 다시 알리고, TC 클라이언트는 TC를 따른다.

### 기본 흐름

Part 7이 정한 기본 흐름은 다음 순서다.

1. 시스템이 전원 인가와 주소 클레임(버스에서 쓸 주소를 정하는 절차, [13장](/study/isobus/13-j1939-address-claim))을 마치면 <strong>VT가</strong> Language command를 보내야 한다.
2. TECU와 VT에는 기본 언어가 저장돼 있어야 한다. 작업기 CF가 원하는 언어를 지원하지 않을 때 쓴다.
3. VT는 운전자가 작업기(또는 작업기 묶음)의 지원 언어 목록을 보고 고를 방법을 제공해야 한다.
4. 공장 출하 상태처럼 운전자가 언어를 고른 적이 없으면, VT는 TECU에서 기본 언어를 요청해 자기 기본값으로 저장한다.
5. 운전자가 언어를 정한 뒤에는 VT의 Language command가 TECU 기본값보다 항상 우선한다.
6. 운전자의 선택은 다음 전원 인가 때 쓰도록 TECU나 VT(또는 둘 다)에 저장한다.

트랙터에 TECU가 여러 대면 Language command 응답은 function instance가 0인 TECU가 맡는다. function instance는 NAME(장치마다 붙는 64비트 이름표, [12장](/study/isobus/12-j1939-address-name))에 들어 있는 번호로, 같은 기능을 하는 장치가 여럿일 때 서로 구분한다. 여러 TECU의 역할 분담은 [22장](/study/isobus/22-tractor-ecu)에서 다룬다.

### 장치별 역할

각 표준 문서는 언어·형식·단위 설정 묶음을 "standard setups"라 부르고 역할을 나눈다. VT 쪽 규칙은 ISO 11783-6(VT를 정하는 표준 문서)에, TC 쪽 규칙은 ISO 11783-10(TC를 정하는 표준 문서)에 있다. 표에 나오는 낱말 몇 개를 먼저 풀어 둔다.

- 오브젝트 풀: 작업기가 VT 화면에 띄울 그림, 글자, 버튼 정의를 모은 데이터([32장](/study/isobus/32-vt-object-pool-basics))
- 비휘발성 메모리: 전원을 꺼도 지워지지 않는 저장 공간
- 전역 요청과 직접 요청: 버스 전체에 보내는 요청(Request)과 주소 하나를 정해 보내는 요청([10장](/study/isobus/10-j1939-request-ack))
- DDOP: 작업기가 TC에 자기 구조와 기능을 알리는 장치 설명 데이터([48장](/study/isobus/48-ddop-basics))
- TC 클라이언트: TC에 연결해 작업 데이터를 주고받는 작업기 쪽 CF

| 주체 | 규칙 |
|---|---|
| VT | standard setups 메시지를 보내야 한다. Working Set들이 알려 준 언어와 VT가 지원하는 관련 언어로 상위 목록(superset)을 만들되 비휘발성 메모리에 저장하지 않는다. 운전자가 고른 언어·형식·단위를 전원 인가 시와 바뀔 때마다 보고한다. 설정 자체는 비휘발성 메모리에 저장한다. 전역 요청과 자기에게 온 요청 모두에 응답한다. 언어 코드와 국가 코드를 함께 보내는 것이 권고다 |
| Working Set | 자기 오브젝트 풀을 올리는 VT의 standard setups에 맞춘다. VT가 둘이면 VT마다 다른 설정을 쓸 수 있다. 지원하지 않는 설정이면 자체 방법으로 적절한 기본값을 고른다 |
| TC | standard setups 메시지를 보내야 하고, 주 연결 VT(클라이언트 값을 표시하는 VT)에서 받은 설정을 쓴다. 설정을 비휘발성 메모리에 저장했다가 VT 연결 전 초기화 때 복원하고, VT 연결로 설정이 정해진 적이 없으면(공장 출하 상태) 제조사 기본값을 쓴다. 클라이언트 초기화 때와 설정이 바뀔 때 보고한다. 전역·직접 요청 응답은 TC 버전 4에서 추가된 요구다 |
| TC 클라이언트 | DDOP를 올리는 TC의 설정에 맞춘다(버전 4부터. 버전 3 이전 클라이언트는 VT나 TECU를 따랐다). 지원하지 않는 언어면 자기 기본 언어를 쓴다 |

표의 "상위 목록(superset)"은 Working Set들이 알려 준 언어와 VT가 지원하는 언어를 합친 목록이다. VT는 이 목록을 비휘발성 메모리에 저장하지 않지만, 운전자가 고른 설정 자체는 저장한다.

### DDOP의 Localization label

TC 쪽에는 바이트 수준의 연결점이 하나 더 있다. DDOP 안에는 Localization label이라는 7바이트 꼬리표가 있어, 그 DDOP가 어떤 언어·단위 설정에 맞춰 만들어졌는지 적어 둔다. Bytes 1~6이 Language command의 Bytes 1~6이고 Byte 7은 예약(`0xFF`)이다. 1절의 en-US 설정이라면 라벨은 `65 6E 5F 03 5A 56 FF`가 된다.

클라이언트는 받은 Language command 바이트를 그대로 복사해 라벨을 만들면 된다. 필드를 직접 다시 조립하면 예약 비트 값이 달라져 라벨이 어긋날 수 있다. 표준이 이 함정을 직접 적지는 않았지만, 라벨을 비교해 DDOP를 다시 보낼지 정하므로 바이트 하나만 달라도 결과가 달라진다. 라벨의 바이트 구조는 [49장](/study/isobus/49-ddop-bytes)에서, 클라이언트가 TC에 저장된 라벨과 비교해 DDOP를 다시 올릴지 정하는 흐름은 [50장](/study/isobus/50-ddop-commands-design)에서 다룬다.

::: warning 구현 함정: Language command를 보내는 CF는 여럿이다
VT, TC, TECU가 모두 Language command를 보낼 수 있으므로 전역 요청을 보내면 설정이 서로 다른 응답이 여러 개 올 수 있다. Amd1은 서비스를 받고 있는 CF에게 <strong>destination-specific 요청</strong>(목적지 지정 요청: 주소 하나에게만 보내는 요청)을 보내라고 권고한다. 그리고 Working Set이 VT를 여러 대 발견하면 자기 UI(화면 구성)를 올린 VT의 SA(Source Address, 보낸 쪽 주소)에서 온 Language command를 쓰라는 예를 든다. 수신 측은 "마지막으로 받은 Language command"가 아니라 "내가 연결한 VT의 SA가 보낸 Language command"를 저장해야 한다.
:::

<small>근거: ISO 11783-7 B.21, Amd1 B.21, ISO 11783-6:2018 4.6.5, ISO 11783-10:2015 6.5와 Table D.19, ISO 11783-9 4.4.2.1</small>

## 3. 가변 반복 주기: 메시지 주기를 바꿔 달라고 요청하기

주기적으로 나가는 메시지는 버스 대역폭(일정 시간 동안 버스가 실어 나를 수 있는 데이터 양)을 계속 차지한다. 어떤 메시지는 더 자주 받고 싶은 수신자가 있고, 어떤 메시지는 기본 주기만큼 자주 볼 필요가 없을 수 있다. 가변 반복 주기는 메시지를 쓰는 쪽이 필요에 맞게 버스 대역폭을 조정하는 장치다. 특정 PGN을 쓰는 쪽이 원하는 송신 주기를 요청하면, 그 PGN을 보내는 쪽이 가능할 때 요청을 따른다. 5절의 Heartbeat도 이 요청으로 켠다.

신문 보급소에 배달 횟수를 바꿔 달라고 전화하는 것과 비슷하다. 보급소가 받아들이면 확인 연락을 주고 조금 뒤부터 새 주기로 배달한다. 확인 연락이 없으면 요청이 거절된 것으로 본다. 다른 점은 확인 연락(응답)이 방송으로 나간다는 것이다. 바꾼 메시지가 방송이라면 새 주기는 그 메시지를 받는 모든 CF에게 똑같이 적용된다.

### 요청과 응답 메시지

- <strong>Request for repetition rate</strong>: PGN 52224(`0xCC00`), PF 204인 PDU1, 우선순위 6. Bytes 1~3은 주기를 요청할 PGN(하위 바이트부터), Bytes 4,5는 원하는 주기(1 ms/bit, 0~64 255), Bytes 6~8은 예약이다. 주기 0은 기본 주기 요청, 65 535는 변경 요청 없음이다.
- <strong>Response for repetition rate</strong>: PGN 65038(`0xFE0E`), 방송, 우선순위 6. 데이터 구조는 요청과 같고 Bytes 4,5에 송신자의 <strong>실제</strong> 주기가 실린다.

PF(PDU Format)는 PGN의 가운데 바이트다. PF가 240보다 작은 PDU1 형식은 그다음 바이트(PS) 자리에 받는 쪽 주소(DA, Destination Address)를 싣는다([9장](/study/isobus/09-j1939-message)). 그래서 요청은 주기를 바꿔 줄 송신자 하나에게 보내고, 응답은 모두에게 방송한다.

두 메시지의 데이터 8바이트는 같은 모양이다. 오른쪽 열은 Heartbeat(PGN 61668)를 100 ms로 요청하는 예다.

| 바이트 | 내용 | 예: Heartbeat를 100 ms로 요청 |
|---|---|---|
| 1~3 | 주기를 바꿀 PGN, 하위 바이트부터 | `E4 F0 00` = 61668 |
| 4~5 | 요청은 원하는 주기, 응답은 실제 주기. 1 ms/bit, 하위 바이트부터 | `64 00` = 100 ms |
| 6~8 | 예약 | `FF FF FF` |

"1 ms/bit"는 원시값 1이 1 ms라는 뜻이다. 100 ms면 원시값 100(`0x0064`)을 하위 바이트부터 `64 00`으로 싣는다.

### 타이밍 규칙

타이밍 규칙은 네 가지다.

1. CF는 이 메시지를 감시할 의무가 없다. 고정 타이밍 제어 루프처럼 요청 주기를 쓸 수 없거나 쓰고 싶지 않은 CF는 무시해도 된다. 고정 타이밍 제어 루프는 정해진 주기로 계산과 출력을 되풀이하도록 짜인 제어 프로그램이다.
2. 요청자는 요청을 보낸 뒤 250 ms 안에 응답이 없으면 요청이 거절됐다고 간주해야 한다.
3. 새 주기를 받아들인 송신자는 응답을 보내고 250 ms를 기다린 뒤 새 주기로 바꿔야 한다.
4. 다른 주기 요청을 받은 뒤 250 ms 안에 기본 주기(0x0000) 요청도 받으면 기본 주기를 써야 한다.

규칙 4는 서로 다른 요청이 거의 동시에 오면 기본 주기 쪽을 따르라는 뜻이다. 아래 그림의 왼쪽은 송신자가 요청을 따르는 경우, 오른쪽은 따를 수 없어 응답하지 않는 경우다.

![반복 주기 변경 요청: 송신자가 따르면 250 ms 안에 Response for repetition rate를 방송하고 250 ms 뒤 새 주기로 보낸다. 따를 수 없으면 응답하지 않고, 요청자는 250 ms 동안 응답이 없으면 거절로 간주한다](/images/study-isobus/25-repetition-rate-exchange-light.png)
![반복 주기 변경 요청: 송신자가 따르면 250 ms 안에 Response for repetition rate를 방송하고 250 ms 뒤 새 주기로 보낸다. 따를 수 없으면 응답하지 않고, 요청자는 250 ms 동안 응답이 없으면 거절로 간주한다](/images/study-isobus/25-repetition-rate-exchange-dark.png)

### 코드로 보기

5절에서 볼 Heartbeat가 이 메시지로 켜진다. CF `0x81`(=129)이 CF `0x80`(=128)에게 Heartbeat(PGN 61668)를 100 ms 주기로 요청하고, `0x80`이 받아들이는 교환은 다음과 같다.

```python
def rep_rate_request(pgn: int, rate_ms: int) -> bytes:
    return pgn.to_bytes(3, "little") + rate_ms.to_bytes(2, "little") + b"\xff\xff\xff"


req = rep_rate_request(61668, 100)
assert req.hex(" ").upper() == "E4 F0 00 64 00 FF FF FF"
assert (6 << 26) | (0xCC << 16) | (0x80 << 8) | 0x81 == 0x18CC8081   # 요청 CAN ID
assert (6 << 26) | (0xFE0E << 8) | 0x80 == 0x18FE0E80                 # 응답 CAN ID
assert rep_rate_request(65096, 0)[3:5] == b"\x00\x00"                 # 기본 주기로 되돌리기
```

첫 `assert`는 요청 데이터 8바이트를 확인한다. 다음 두 줄은 29비트 CAN ID를 계산한다. CAN ID는 우선순위(3비트), PGN(18비트), 보낸 쪽 주소(8비트)를 이어 붙인 값이다([9장](/study/isobus/09-j1939-message)). 요청은 PDU1이라 PGN 아래 바이트에 받는 쪽 주소 `0x80`이 들어가 `0x18CC8081`이 되고, 응답은 방송이라 `0x18FE0E80`이 된다. 마지막 줄은 Wheel-based speed and distance(PGN 65096)의 주기를 기본값으로 되돌리는 요청으로, Bytes 4,5가 `00 00`이다.

<small>근거: ISO 11783-7 B.22.1, B.22.2, A.23.6, A.23.7</small>

## 4. 작업기 운용 상태와 전체 정지 스위치(ISB)

여기부터는 안전과 관련된 메시지를 본다. 이 장에서 다루는 안전 관련 메시지는 세 묶음이다.

| 메시지 | 지키려는 것 | 다루는 절 |
|---|---|---|
| Implement operating state command, All implements stop operations switch state(ISB) | 트랙터의 운용 지시와 운전자의 정지 의도가 모든 작업기에 전해지는 것 | 4절 |
| Heartbeat | 데이터를 보내는 CF가 지금도 정상으로 동작하는지 받는 쪽이 아는 것 | 5~6절 |
| Operator status | 운전자가 제자리에 있고 주의를 기울이고 있는지 알리는 것 | 7절 |

### 작업기 운용 상태 명령

트랙터가 작업기에게 "지금은 작업 상태로", "지금은 운반 상태로" 하고 운용 상태를 지시하는 메시지다. TECU가 작업기 버스로 보내며, 현재 명령된 작업기 운용 상태를 싣는다. PGN 64771(`0xFD03`), 우선순위 3이고 1 s마다와 상태가 바뀔 때 보낸다.

| 위치 | 내용 |
|---|---|
| Bytes 1~7 | 예약 |
| Byte 8 bits 8~3 | 예약 |
| Byte 8 bits 2,1 | 운용 상태 명령: 00 field working(밭 작업) 상태로, 01 transport(운반) 상태로, 10 park(주차) 상태로, 11 조치 없음 |

예를 들어 트랙터가 운반 상태를 명령하면 예약 자리는 모두 1이므로 데이터는 `FF FF FF FF FF FF FF FD`다. 마지막 바이트 `FD` = `1111 1101`에서 bits 2,1이 `01`이다.

이 메시지는 지시일 뿐이다. 작업기가 실제로 어떤 상태인지(운반 가능, 분리 가능, 작업 준비, 작업 중)는 작업기가 Maintain power 메시지(PGN 65095)의 Byte 2로 보고한다([22장](/study/isobus/22-tractor-ecu)).

### 전체 정지 스위치(ISB)

밭에서 작업하다 보면 운전자가 연결된 작업기를 즉시 모두 멈추고 싶은 순간이 온다. 작업기마다 VT 화면을 넘겨 가며 정지 버튼을 찾을 여유는 없다. 그래서 운전자가 연결된 모든 작업기를 한 번에 멈추는 스위치를 두고, 그 상태를 버스에 방송한다. 공장 라인의 비상 정지 버튼처럼 버튼 하나가 모든 작업기에 "멈춰라"를 알린다고 보면 된다. 비유와 다른 점도 있다. 이 메시지는 전원을 끊는 장치가 아니라, 각 작업기가 failsafe 상태를 거쳐 스스로 멈추는 절차를 시작하라는 신호다.

원문은 이 메시지를 보내는 CF를 'ISB server'라 부르는데, ISB라는 약어의 풀이는 Part 7에 없다. AgIsoStack(공개된 ISOBUS 소프트웨어 라이브러리) 같은 구현은 ISOBUS Shortcut Button이라는 이름을 쓴다. 이 장에서는 이 스위치를 ISB, 이 메시지를 보내는 CF를 ISB 서버라 부른다.

메시지는 PGN 64770(`0xFD02`), 우선순위 3이고 1 s마다와 상태가 바뀔 때 보내며, 작업기 버스의 어떤 CF든 보낼 수 있다. Byte 7이 전이 횟수, Byte 8 bits 2,1이 스위치 상태(00 Stop implement operations, 01 Permit all implements to operation ON)다.

| 위치 | 내용 |
|---|---|
| Bytes 1~6 | 예약 |
| Byte 7 | 전이 횟수(0~255): 전원 인가 뒤 Permit에서 Stop으로 바뀐 횟수 |
| Byte 8 bits 8~3 | 예약 |
| Byte 8 bits 2,1 | 스위치 상태: 00 작업 정지(Stop), 01 작업 허용(Permit), 10 오류, 11 사용 불가 |

예를 들어 `FF FF FF FF FF FF 04 FC`를 받았다면 Byte 7 = 4이므로 전원 인가 뒤 Permit → Stop 전이가 네 번 있었다. Byte 8 = `1111 1100`에서 bits 2,1 = `00`이므로 지금은 Stop이다.

표준이 정한 의무 규칙은 이렇다.

- 연결된 시스템의 <strong>운전자 위치마다</strong> 이 스위치가 최소 하나 있어야 하고, 운전자가 언제든 쓸 수 있어야 한다. 위치와 조작 방식은 ISO 15077(농업 기계의 운전자 조작 장치 위치와 조작 방식을 정한 표준)을 따른다.
- 어떤 CF에서든 Stop 값을 받으면 모든 작업기는 전체 동작을 멈추는 절차를 시작해야 한다. 동작을 끄기 전에 failsafe 상태(고장이 나도 위험하지 않도록 정해 둔 상태)를 취해야 하고, PTO(트랙터 동력을 작업기에 전하는 회전축)·보조 밸브·트랙터 이동 같은 자동화 모드로 동작 중이라면 TECU에 자동화 종료를 요청하기 전에 failsafe 상태로 들어갈 수 있다.
- 멈춘 뒤 Working Set Master(작업기를 대표해 VT와 통신하는 CF)는 이 스위치 때문에 멈췄다고 운전자에게 알려야 하고, 이 기능을 지원하면 홈 화면에 아이콘이나 기능 이름 같은 표시를 둬야 한다.
- 다시 Permit이 돼도 작업기가 <strong>바로 재시작하지 않는다</strong>. 재시작은 start/stop("Master ON/OFF") 스위치 같은 별도 수단으로만 한다. 이 Start/Stop 상태는 Wheel-based speed and distance 메시지(PGN 65096)의 Byte 8 bits 6,5로 방송된다([23장](/study/isobus/23-implement-messages-basics)).
- 작업기는 정지를 이 입력에만 의존하면 안 되고, 전용 start/stop 스위치, VT 소프트키(VT 화면 옆의 기능 버튼), 정지 기능을 할당한 보조 입력(조이스틱 같은 별도 입력 장치, [40장](/study/isobus/40-vt-aux)) 같은 정상 정지 수단을 따로 제공해야 한다.

여기서 멈출 "모든 동작"은 운전자 조작이나 VT, 보조 입력, TECU, TC, Sequence Control 마스터([53장](/study/isobus/53-sequence-control-basics))의 명령으로 켜진 기능 전부다.

### 전이 횟수로 놓친 정지 찾기

전이 횟수는 전원 인가 이후 Permit(01) → Stop(00) 전이가 일어난 횟수이고, 최댓값 255를 보고한 다음 전이에서 0으로 돌아간다. Working Set은 ISB 서버마다 첫 메시지를 받은 시점부터 이 횟수를 추적해야 한다. 해당하는 상태 전이를 보지 못했는데 횟수만 늘었다면 오류로 보고 대응해야 한다. 구체적인 대응 방법은 표준이 정하지 않는다.

상태만 보면 무엇이 문제일까? 표준이 이유를 적지는 않았지만, 다음 상황을 보면 횟수가 필요한 까닭이 드러난다. 운전자가 정지 버튼을 짧게 눌렀다 뗐다고 하자. 버스에는 Stop과 Permit을 알리는 변화 시 메시지가 잇달아 나간다. 어떤 작업기가 이 두 프레임을 놓치면, 다음 1 s 주기 메시지에서 보는 상태는 여전히 Permit이다. 상태만 보는 작업기는 정지 명령이 있었다는 사실 자체를 모른다. 횟수는 이 공백을 메운다.

1초마다 사진을 찍는 감시 카메라는 그 사이에 문이 잠깐 열렸다 닫힌 일을 놓칠 수 있다. 문에 "열린 횟수" 계수기가 달려 있으면 사진 두 장의 계수기 값만 비교해도 놓친 일이 있었음을 안다. 전이 횟수가 이 계수기 역할을 한다.

![ISB 전이 횟수 시간 축: 첫 메시지 01/3으로 추적을 시작하고 00/4와 01/4는 정상이다. 두 번째 짧은 정지의 변화 시 메시지 00/5와 01/5를 놓치면, 2 s의 주기 메시지 01/5에서 상태는 그대로인데 횟수만 늘어 오류로 판정한다](/images/study-isobus/25-isb-transition-timeline-light.png)
![ISB 전이 횟수 시간 축: 첫 메시지 01/3으로 추적을 시작하고 00/4와 01/4는 정상이다. 두 번째 짧은 정지의 변화 시 메시지 00/5와 01/5를 놓치면, 2 s의 주기 메시지 01/5에서 상태는 그대로인데 횟수만 늘어 오류로 판정한다](/images/study-isobus/25-isb-transition-timeline-dark.png)

그림에서 작업기가 받은 메시지만 순서대로 판정하면 다음과 같다. 상태는 01(Permit)과 00(Stop)으로 적는다.

| 받은 메시지(상태 / 횟수) | 직전 기록 | 횟수 변화 | 판정 | 이유 |
|---|---|---|---|---|
| 01 / 3 | 없음 | 해당 없음 | 추적 시작 | 이 ISB 서버의 첫 메시지라 기준으로 삼는다 |
| 00 / 4 | 01 / 3 | +1 | 정상 | Permit → Stop 전이를 직접 봤고 횟수도 1 늘었다 |
| 01 / 4 | 00 / 4 | 0 | 정상 | Stop → Permit은 세지 않는 전이다 |
| 01 / 4 | 01 / 4 | 0 | 정상 | 바뀐 것이 없다(1 s 주기 메시지) |
| 01 / 5 | 01 / 4 | +1 | 오류 | 상태는 계속 Permit인데 횟수만 늘었다. 그 사이의 정지를 놓쳤다 |

아래 `IsbTracker`는 이 판정을 코드로 옮긴 것이다. ISB 서버는 운전자 위치마다 있을 수 있으므로, 보낸 쪽 주소(SA)마다 마지막 상태와 횟수를 따로 기억한다. `(count - p_count) % 256`은 255 다음에 0으로 돌아가는 경우까지 한 번에 계산한다. 코드 안 문서 문자열에 적힌 절 번호는 원문 대조용이니 건너뛰어도 된다.

```python
class IsbTracker:
    """B.30 전이 횟수 추적: ISB 서버(SA)별로 마지막 (상태, 횟수)를 기억한다."""

    def __init__(self):
        self.last = {}

    def feed(self, sa: int, state: int, count: int) -> str:
        prev = self.last.get(sa)
        self.last[sa] = (state, count)
        if prev is None:
            return "init"                       # 첫 메시지 기준으로 추적 시작
        p_state, p_count = prev
        step = (count - p_count) % 256
        if step == 0:
            return "ok"
        if step == 1 and p_state == 0b01 and state == 0b00:
            return "ok"                         # 관찰한 Permit -> Stop 전이와 일치
        return "error"                          # 놓친 정지 이벤트


t = IsbTracker()
assert t.feed(0x2A, 0b01, 3) == "init"
assert t.feed(0x2A, 0b00, 4) == "ok"
assert t.feed(0x2A, 0b01, 4) == "ok"
assert t.feed(0x2A, 0b01, 5) == "error"         # Stop을 못 봤는데 횟수가 늘었다
t.feed(0x2B, 0b01, 255)
assert t.feed(0x2B, 0b00, 0) == "ok"            # 255 다음은 0
```

처음 네 검사는 위 표에서 1 s 주기 메시지 한 줄(01 / 4 반복)을 뺀 순서와 같다. 마지막 두 줄은 다른 ISB 서버(SA `0x2B`, =43)에서 횟수가 255에서 0으로 넘어간 경우다. 라이브러리 수준의 ISB 송수신은 [AgIsoStack 스터디의 작업기 메시지 챕터](/study/agisostack/16-implement-messages)에 있다.

<small>근거: ISO 11783-7 B.29, B.30, A.25.1~A.25.4</small>

## 5. Heartbeat: 보내는 쪽이 살아 있는지 확인하기

안전에 중요한 기능은 받은 데이터가 맞는지뿐 아니라, 데이터를 보내는 쪽이 지금도 정상인지 알아야 한다. 예를 들어 작업기가 트랙터의 속도 값을 받아 동작을 정한다고 하자. 트랙터 쪽 프로그램이 멈춰 같은 프레임만 되풀이해 보내거나, 아예 아무것도 보내지 않게 되면 작업기는 그 사실을 알아채야 한다. CAN은 프레임이 깨지지 않고 도착했는지는 검사하지만([6장](/study/isobus/06-can-error)), 보낸 쪽 프로그램이 정상인지는 알려 주지 않는다. Heartbeat는 이 빈틈을 메우는 메시지다.

멀리 사는 친구가 매일 번호를 붙여 편지를 보낸다고 하자. 편지가 너무 오래 오지 않거나(시간 초과), 어제와 같은 번호가 또 오거나(같은 값 반복), 번호가 여러 개 건너뛰면(증가폭 초과) 중간에 무슨 일이 생긴 것이다. Heartbeat는 이 번호만 담은 편지다. 실제 데이터는 다른 메시지로 오고, Heartbeat는 "보내는 쪽이 지금도 정상"이라는 신호만 준다.

### 표준이 요구하는 것

Heartbeat는 ISO 25119(농업 기계 제어 시스템의 기능 안전을 정한 표준)에 적합한 시스템을 ISO 11783 프로토콜 위에 구현할 수 있도록 정의된 메시지다. ISO 25119는 하드웨어 구조를 카테고리로 나누고, 위험한 고장 가운데 진단으로 찾아내는 비율을 진단 커버리지(DC, Diagnostic Coverage)라 부른다. Heartbeat는 시퀀스 번호로 하드웨어 카테고리 2 시스템에서 중간 수준 진단 커버리지(DC medium)를 충족한다. 두 가지 성질이 있다.

- 데이터 출처에서 소비자까지 중간에 다른 컨트롤러가 끼어도 끝에서 끝까지(end-to-end) 검증한다.
- 출처 CF 하나의 Heartbeat를 여러 소비 CF가 함께 쓸 수 있다. Heartbeat는 방송이라 받는 쪽이 여럿이어도 보내는 CF는 하나만 보내면 된다.

구현 요구는 다섯 가지다.

1. 안전 핵심 경로(safety critical path: 안전 관련 기능이 쓰는 데이터가 출처 CF에서 받는 CF까지 지나가는 길)의 각 서브시스템은 수신 측이 watchdog(반복 주기 기준 타임아웃 감시)을 할 수 있게 안전 관련 메시지를 보낸다.
2. 각 서브시스템은 요청을 받으면 시퀀스 번호가 든 Heartbeat를 보낸다.
3. 각 수신 시스템은 해당 데이터 출처의 Heartbeat를 검사한다.
4. 검사에 실패하면 수신 시스템은 안전 상태(safe state)에 도달해야 한다.
5. Heartbeat의 샘플 주기는 안전 관련 CAN 메시지의 샘플 주기 이상이어야 한다.

watchdog은 메시지가 정해진 시간 안에 오는지 지켜보는 감시 타이머다. 어떤 메시지든 안전 핵심 경로의 일부가 될 수 있으므로 <strong>네트워크의 모든 CF는 요청을 받으면 Heartbeat를 보낼 수 있어야 한다</strong>. 무엇이 안전 핵심 경로인지는 AEF(ISOBUS 인증과 가이드라인을 만드는 업계 단체) 가이드라인이 정한다. 표준은 Heartbeat가 정해진 간격으로 오고 번호가 유효 범위 안에서 늘어나는 동안에는, 보내는 CF가 정상 동작하며 모든 메시지에 올바른 데이터를 싣고 있다고 본다.

### 메시지 정의와 켜는 법

메시지 정의는 단순하다. PGN 61668(`0xF0E4`), PF 240인 방송 메시지이고, 우선순위 3, 주기 100 ms, <strong>데이터 길이 1 byte</strong>다. Byte 1이 시퀀스 번호다.

기본적으로 CF는 대역폭을 아끼려고 Heartbeat를 보내지 않는다. 켜는 순서는 3절의 반복 주기 요청을 그대로 쓴다.

1. 소비 CF(A)가 제공 CF(B)에게 Request for repetition rate로 Heartbeat를 100 ms 주기로 요청한다.
2. B가 요청을 따르면 Heartbeat 송신을 시작하고, A는 검증을 시작한다.
3. B가 요청을 따를 수 없으면 응답하지 않는다. A는 250 ms 안에 응답이 없으면 거절로 보고 위험도 평가에 따라 대응한다. 위험도 평가는 기능이 고장 날 때의 위험을 따져 대응을 미리 정해 두는 일이다.
4. 이미 Heartbeat를 보내고 있는 CF에게는 다시 요청하지 않는다.

::: warning 구현 함정: DLC 1 프레임
ISO 11783-3(데이터 링크 계층을 정하는 표준 문서)은 데이터 길이가 8 바이트 이하인 메시지의 CAN DLC(Data Length Code, 프레임에 실린 데이터 바이트 수, [4장](/study/isobus/04-can-data-frame))를 정의된 데이터 길이로 설정하라고 정한다. Heartbeat는 DLC 1인 프레임으로 온다. DLC 8 프레임만 받도록 필터를 짠 수신기는 Heartbeat를 통째로 놓친다.
:::

### 시퀀스 번호 규칙

CF가 초기화될 때(전원 인가, 리셋, VT status 메시지 송신 시작 등) 시퀀스 번호를 한 번 251로 둔다. VT status 메시지는 VT가 살아 있음을 알리려고 주기적으로 보내는 메시지다. 이후 송신할 때마다 1씩 올려 0~250을 돌고, 250 다음은 0이다. 값마다 뜻을 정리하면 이렇다.

| 값 | 뜻 |
|---|---|
| 0~250 | 정상 번호. 보낼 때마다 1씩 올리고, 250 다음은 0이다 |
| 251 | 초기화. 전원 인가, 리셋, VT status 메시지 송신 시작 직후에 한 번 쓴다 |
| 252~253 | 예약. 받으면 무시한다 |
| 254 | 송신 측 오류 |
| 255 | 사용 불가. 송신 CF가 shutdown 상태로 네트워크를 정상 이탈할 때 쓴다 |

### 수신 측 판정 규칙

수신 측은 이전 번호를 기억했다가 이번 번호가 1 늘었는지 비교한다. 이전 값이 250이나 251(초기화)이면 현재 값은 0이어야 한다. 실제 판정은 아래 일곱 규칙을 따르고, 규칙 6 덕분에 메시지 몇 개가 빠지는 것까지는 허용된다.

판정 결과는 네 가지 상태로 나타낸다. Operational은 정상 상태, Sequence Error는 번호나 간격이 어긋난 상태, Transmission Error는 송신 측이 오류를 알린 상태, Graceful Shutdown은 송신 측이 정상 이탈을 알린 상태다.

| # | 조건 | 판정 |
|---|---|---|
| 1 | 현재 값이 이전 값과 같고 255가 아님 | Sequence Error |
| 2 | 현재 값이 252~253 | 메시지 무시 |
| 3 | 현재 값이 254 | Transmission Error |
| 4 | 현재 값이 251 | 송신 CF 리셋으로 보고 자기 기준값을 동기화 |
| 5 | 현재 값이 255이고 이전 값이 255가 아님 | Graceful Shutdown 시작 |
| 6 | 250에서 0으로 넘어가는 것을 감안해 증가폭이 3보다 큼 | Sequence Error |
| 7 | Sequence Error에 들어간 뒤 | 연속 8개의 올바른 순차 값을 받아야 정상 복귀 |

규칙을 쉬운 말로 풀면 이렇다.

- 규칙 1: 번호가 그대로면 송신 측이 새 메시지를 만들지 못하고 같은 것을 되풀이하고 있을 수 있다.
- 규칙 2: 252·253은 앞으로 쓰려고 남겨 둔 값이라 지금은 무시한다.
- 규칙 3: 254는 송신 측이 스스로 오류를 알리는 값이다. 수신 측은 송신 측이 오류 상태라고 보고 위험도 평가에 따라 대응한다.
- 규칙 4: 251은 송신 측이 다시 시작했다는 뜻이다. 수신 측은 기준을 251로 맞추고 다음에 0이 오기를 기다린다.
- 규칙 5: 255는 송신 측이 정상적으로 네트워크를 떠난다는 뜻이다. 수신 측은 운전자에게 알리고 안전 상태로 갈 수 있다.
- 규칙 6: 메시지 몇 개가 빠지는 것은 봐주지만, 번호가 너무 많이 건너뛰면 오류다.
- 규칙 7: 오류 상태에서 벗어나려면 올바른 번호를 8번 연속 받아야 한다.

여기에 타이밍 검증이 더해진다. 수신 간격이 300 ms를 넘으면 통신 오류다. 오류를 감지하면 위험도 평가에 따라 대응하며, 안전 상태 진입과 운전자 통지가 예로 나온다. 이 규칙들을 수신 측 상태로 그리면 다음과 같다.

![Heartbeat 수신 측 상태: Operational과 Sequence Error 사이 전이(같은 값 반복·증가폭 3 초과·간격 300 ms 초과 / 연속 8개 정상), 254 수신 시 Transmission Error, 255 수신 시 Graceful Shutdown, 252·253 무시](/images/study-isobus/13-p7-heartbeat-states-light.png)
![Heartbeat 수신 측 상태: Operational과 Sequence Error 사이 전이(같은 값 반복·증가폭 3 초과·간격 300 ms 초과 / 연속 8개 정상), 254 수신 시 Transmission Error, 255 수신 시 Graceful Shutdown, 252·253 무시](/images/study-isobus/13-p7-heartbeat-states-dark.png)

### 시간 축으로 따라가기

첫 번째 예는 1개 유실, 같은 값 반복, 복귀를 한 번에 보여 준다. 송신 측은 100 ms마다 보내고, 수신 측은 받을 때마다 판정한다.

![Heartbeat 시간 축 예: 251, 0, 1을 받고 2를 놓친 뒤 3은 허용, 3이 한 번 더 오면 Sequence Error, 4부터 11까지 연속 8개를 받아 Operational로 복귀한다](/images/study-isobus/25-heartbeat-timeline-light.png)
![Heartbeat 시간 축 예: 251, 0, 1을 받고 2를 놓친 뒤 3은 허용, 3이 한 번 더 오면 Sequence Error, 4부터 11까지 연속 8개를 받아 Operational로 복귀한다](/images/study-isobus/25-heartbeat-timeline-dark.png)

| 시각(ms) | 받은 번호 | 직전 번호 | 판정 | 상태 |
|---|---|---|---|---|
| 0 | 251 | 없음 | 송신 측 초기화. 기준을 맞춘다(규칙 4) | Operational |
| 100 | 0 | 251 | 초기화 다음은 0이어야 하고, 맞다 | Operational |
| 200 | 1 | 0 | +1, 정상 | Operational |
| 300 | 받지 못함(송신 측은 2를 보냄) | 1 | 받은 것이 없어 판정하지 않는다 | Operational |
| 400 | 3 | 1 | +2, 간격 200 ms. 1개 유실은 허용한다(규칙 6) | Operational |
| 500 | 3 | 3 | 같은 값 반복(규칙 1) | Sequence Error |
| 600~1200 | 4~10 | 각각 1 작은 값(3~9) | 올바른 순차 값 1~7번째 | Sequence Error |
| 1300 | 11 | 10 | 8번째 연속 정상. 복귀한다(규칙 7) | Operational |
| 1400 | 12 | 11 | +1, 정상 | Operational |

두 번째 예는 메시지가 연속으로 빠질 때다. 이번에는 이미 정상 흐름 중인 송신 측이 7, 8, 9를 보낸 뒤 세 개가 빠진다.

![Heartbeat 연속 유실 예: 9를 받은 200 ms 뒤 10, 11, 12가 빠지면 마지막 수신 뒤 300 ms가 지나는 순간 감시 타이머가 먼저 오류를 잡고, 600 ms에 온 13은 증가폭 4로 시퀀스 규칙에도 걸린다](/images/study-isobus/25-heartbeat-timeout-light.png)
![Heartbeat 연속 유실 예: 9를 받은 200 ms 뒤 10, 11, 12가 빠지면 마지막 수신 뒤 300 ms가 지나는 순간 감시 타이머가 먼저 오류를 잡고, 600 ms에 온 13은 증가폭 4로 시퀀스 규칙에도 걸린다](/images/study-isobus/25-heartbeat-timeout-dark.png)

1. 0, 100, 200 ms에 7, 8, 9를 받는다. 모두 +1이라 정상이다.
2. 300, 400, 500 ms의 10, 11, 12가 연속으로 빠진다. 받은 것이 없으니 시퀀스 규칙은 판정할 거리가 없다.
3. 마지막 수신(200 ms) 뒤 300 ms를 넘기는 순간 감시 타이머가 통신 오류를 잡는다. 이 장의 검증기는 이 오류를 Sequence Error 상태로 묶는다(6절).
4. 600 ms에 13이 도착한다. 증가폭이 4라 시퀀스 규칙(규칙 6)으로도 오류이고, 간격도 400 ms다.
5. 700 ms의 14부터 올바른 순차 값을 다시 세어, 8개를 채우면 복귀한다.

정리하면 100 ms 주기에서 연속 3개가 빠지면 시퀀스 규칙보다 타이밍 규칙이 먼저 걸린다. 시퀀스 규칙은 다음 메시지가 도착해야 판정할 수 있기 때문이다.

<small>근거: ISO 11783-7 B.33, B.33.1, B.33.2, B.33.3.1~B.33.3.5, A.34, ISO 11783-3:2018 5.2.8.1</small>

## 6. Heartbeat 수신 측 검증기 만들기 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

5절의 규칙을 코드로 옮기면 표준 문장만으로는 정해지지 않는 부분이 나온다. 먼저 함정을 보고, 이어서 검증기 코드를 본다.

::: warning 구현 함정: 유실 허용 개수와 빠진 규칙
- 규칙 6의 문장은 "증가폭이 3보다 크면 오류"인데, 바로 뒤 해설은 "최대 3개 유실을 허용한다"고 적는다. 3개를 잃으면 증가폭이 4이므로 두 문장이 한 칸 어긋난다. 그런데 100 ms 주기에서 연속 3개를 잃으면 수신 간격이 약 400 ms라 300 ms 타이밍 규칙에 먼저 걸린다(5절의 두 번째 시간 축 그림). 실질 허용치는 연속 2개 유실(증가폭 3, 간격 약 300 ms)이고, 이 경우도 간격이 300 ms 경계에 붙으므로 지터(jitter: 메시지 간격이 조금씩 흔들리는 현상)에 따라 타이밍 오류가 날 수 있다. 이 허용치는 표준에 적힌 값이 아니라 두 규칙의 수치로 계산한 결과다. 상대 구현과 시험 케이스로 맞춰 두는 것이 안전하다.
- 원문은 Transmission Error와 Graceful Shutdown 상태에서 빠져나오는 조건을 적지 않는다.
- VT는 VT status 송신을 시작할 때마다 시퀀스가 251로 초기화된다. VT 서버를 재시작하는 에뮬레이터(VT를 흉내 내는 시험용 프로그램)라면 이 초기화를 빼먹기 쉽다.
:::

아래 `HeartbeatMonitor`는 5절 표의 규칙 1~7과 300 ms 타이밍 규칙을 구현한 수신 측 검증기다. 문서 문자열의 "규칙 1~7"은 5절 표의 번호이고, 함께 적힌 절 번호는 원문 대조용이다. `feed()`는 Heartbeat를 받을 때마다 번호와 수신 시각(ms)을 넣어 부르고, `poll()`은 메시지가 오지 않아도 타이머로 주기적으로 부른다.

```python
class HeartbeatMonitor:
    """B.33.3.3 규칙 1~7과 B.33.3.4 타이밍(300 ms)을 구현한 수신 측 검증기."""

    def __init__(self):
        self.prev, self.state, self.good, self.last_t = None, "init", 0, None

    def feed(self, seq: int, t_ms: int) -> str:
        if seq in (252, 253):                            # 규칙 2
            return self.state
        late = self.last_t is not None and t_ms - self.last_t > 300
        self.last_t = t_ms
        prev, self.prev = self.prev, seq
        if seq == 254:                                   # 규칙 3
            self.state = "transmission_error"
        elif seq == 255:                                 # 규칙 5
            if prev != 255:
                self.state = "graceful_shutdown"
        elif seq == 251 or prev is None:                 # 규칙 4, 첫 수신
            self.state, self.good = "operational", 0
        else:
            if prev == 251:
                step = 1 if seq == 0 else 99             # 초기화 다음은 0이어야 한다
            elif prev > 250:
                step = 99
            else:
                step = (seq - prev) % 251                # 250 -> 0 롤오버
            if step == 0 or step > 3 or late:            # 규칙 1, 6, 타이밍
                self.state, self.good = "sequence_error", 0
            elif self.state == "sequence_error":         # 규칙 7
                self.good = self.good + 1 if step == 1 else 0
                if self.good >= 8:
                    self.state = "operational"
            else:
                self.state = "operational"
        return self.state

    def poll(self, now_ms: int) -> str:
        """메시지가 아예 끊기면 feed()가 불리지 않으므로 타이머로 따로 감시한다."""
        timed_out = self.last_t is not None and now_ms - self.last_t > 300
        if timed_out and self.state not in ("transmission_error", "graceful_shutdown"):
            self.state, self.good = "sequence_error", 0
        return self.state


m = HeartbeatMonitor()
for i, s in enumerate([251, 0, 1, 2]):
    assert m.feed(s, i * 100) == "operational"
assert m.feed(2, 400) == "sequence_error"                # 같은 값 반복
states = [m.feed(s, 500 + k * 100) for k, s in enumerate(range(3, 11))]
assert states[-1] == "operational" and states[-2] == "sequence_error"   # 8개째 복귀
assert m.feed(13, 1400) == "operational"                 # 2개 유실: 증가폭 3, 간격 200 ms
assert m.feed(17, 1500) == "sequence_error"              # 증가폭 4

m2 = HeartbeatMonitor()
m2.feed(249, 0)
assert m2.feed(250, 100) == "operational"
assert m2.feed(0, 200) == "operational"                  # 250 -> 0
assert m2.feed(1, 600) == "sequence_error"               # 간격 400 ms
assert m2.feed(254, 700) == "transmission_error"
assert m2.feed(255, 800) == "graceful_shutdown"

m3 = HeartbeatMonitor()
m3.feed(251, 0)
m3.feed(0, 100)
assert m3.poll(350) == "operational"                      # 마지막 수신 후 250 ms
assert m3.poll(401) == "sequence_error"                   # 301 ms 동안 수신 없음
```

아래쪽 검사 세 묶음은 이렇게 읽는다.

- `m`: 251 → 0 → 1 → 2로 정상이다. 2가 한 번 더 오면 같은 값 반복으로 Sequence Error가 되고, 3~10의 여덟 개를 받으면 복귀한다. 이어 13(2개 유실, 증가폭 3)은 허용되고, 17(증가폭 4)은 오류다.
- `m2`: 249 → 250 → 0 롤오버(250 다음 0)는 정상이다. 간격 400 ms는 타이밍 오류이고, 254는 송신 측 오류, 255는 Graceful Shutdown이다.
- `m3`: 마지막 수신 뒤 250 ms까지는 정상이고, 301 ms 동안 아무것도 오지 않으면 `poll()`이 오류를 잡는다.

5절의 상태 그림과 시간 축 그림, 그리고 이 코드는 타이밍 오류도 Sequence Error와 같은 상태로 묶고, 연속 8개 정상 수신으로 복귀시킨다. 원문은 타이밍 위반을 "통신 오류 감지"라고만 적고 별도 상태 이름이나 복귀 조건을 두지 않으므로, 이 묶음은 구현 선택이다. 또 표준의 구현 요구가 수신 측에 watchdog(반복 주기 기준 타임아웃 감시)을 요구하므로, 간격 검사는 메시지가 도착할 때만이 아니라 `poll()`처럼 타이머로도 해야 한다. 그래야 송신이 완전히 멈춘 경우를 잡는다.

오류를 진단 메시지로 알릴 수도 있다. Heartbeat 시퀀스 번호(SPN 7345)의 진단에는 FMI 10(Abnormal Rate of Change, 비정상적인 변화율), 11(Root Cause not Known, 원인 불명), 12(Bad Intelligent Device or Component, 지능형 장치나 부품 불량), 19(Received Network Data in Error, 받은 네트워크 데이터 오류)를 쓸 수 있다. 송신 측과 수신 측 모두 이 FMI로 오류 상태나 기능 저하의 이유를 표시할 수 있다. SPN(Suspect Parameter Number)은 값 하나하나에 붙은 번호이고, FMI(Failure Mode Indicator)는 고장의 종류를 나타내는 번호다. 진단 메시지 자체는 [27장](/study/isobus/27-diagnostics-identification)과 [28장](/study/isobus/28-diagnostics-dm-fmi)에서 다룬다.

<small>근거: ISO 11783-7 B.33.1, B.33.3.2~B.33.3.4, A.34</small>

## 7. Operator status: 운전자 재석과 주의 상태 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

자동화 기능은 운전자가 자리에 없거나 주의를 기울이지 못할 때 계속 동작하면 위험하다. 그래서 Amd1은 Heartbeat 절 뒤에 운전자의 재석(presence)과 주의(awareness) 상태를 방송하는 메시지를 더했다. 재석은 운전자가 기계를 조작하기에 올바른 위치에 있는 상태, 주의는 운전자가 기계를 안전하게 조작하는 데 필요한 일을 지금 할 수 있는 상태(깨어 있고 집중함)다. 받는 쪽은 이 정보로 시스템이 어떤 기능을 허용할지 정할 수 있다.

히치·PTO·밸브·가이던스의 exit/reason code 000001(요구 수준의 운전자 재석·주의 미감지)이 이 정보와 짝을 이룬다. exit/reason code는 트랙터가 작업기의 원격 명령을 받을 수 없는 이유를 알리는 6비트 코드다([24장](/study/isobus/24-hitch-pto-valve-control)).

| 항목 | 값 |
|---|---|
| PGN | 64388(0xFB84), PF 251(방송), 우선순위 3 |
| 주기 | 1 000 ms마다, 그리고 재석·주의 상태가 바뀔 때. 단 200 ms보다 빠르게 보내지 않는다 |
| Byte 1 | Operator status sequence counter |
| Byte 2 | bits 8~5 예약(1), bits 4,3 주의 상태, bits 2,1 재석 상태(00 아님, 01 맞음, 10 오류, 11 사용 불가) |
| Bytes 3~7 | 예약 |
| Byte 8 | 앞 56비트(Byte 1~7)의 CRC-8 체크섬 |

Byte 1의 Operator status sequence counter는 순서 카운터다. Byte 8의 CRC-8 체크섬은 데이터가 깨졌는지 확인하려고 앞 7바이트로 계산해 붙이는 8비트 값이다.

시퀀스 카운터는 Heartbeat와 같은 골격이다. 리셋 후 251(0xFB)로 시작해 0~250을 돌고, 252~253은 예약(수신 무시), 254는 송신 측 오류, 255는 이 메시지의 다른 SPN도 모두 사용 불가라는 뜻이다. 수신 측 규칙도 같은 값 반복, 254, 251, 255, 증가폭 3 초과, 연속 8개 복귀까지 Heartbeat의 1~7과 같다. 카운터는 송신자마다 독립이고, 수신 측은 처음 받은 값을 초깃값으로 삼는다.

이 카운터로 송신자가 유효한 네트워크 연결을 유지하는지, 그 SA로 이 메시지를 보내는 CF가 하나뿐인지 판단한다. 두 CF가 같은 주소로 보내면 번호 두 줄이 섞여 들어오므로 수신 규칙에 걸리게 된다. 체크섬이 틀린 메시지는 시퀀스 오류로 취급하고, 재석·주의 상태를 값 2(오류 지시)를 받은 것처럼 처리한다. 이때도 연속 8개 정상 메시지를 받아야 복귀한다.

::: warning 원문이 덜 정한 부분: 카운터 증가 조건과 CRC 파라미터
- 카운터는 "갱신된 데이터를 담은 메시지마다" 1씩 올린다고 적혀 있다. 그런데 수신 규칙은 같은 값이 두 번 오면 오류로 본다. 상태가 그대로인 1 s 주기 메시지에서도 카운터를 올려야 수신 측 오류를 피할 수 있다고 읽는 것이 안전하다. 표준의 두 문장을 맞춰 본 해석이다.
- 원문은 CRC-8-CCITT 다항식(0x07, 반사 표기 0xE0, Koopman 표기 0x83)만 밝히고 초깃값·반사 여부·최종 XOR은 적지 않는다. CRC 결과는 다항식 말고도 시작값(초깃값), 비트 순서를 뒤집는지(반사), 마지막에 XOR하는 값에 따라 달라진다. 송수신 양쪽이 같은 파라미터를 쓰는지 시험 벡터(정해 둔 입력과 기대 출력의 쌍)로 맞춰야 한다.
:::

<small>근거: ISO 11783-7 Amd1 B.33.3.6, A.35.1~A.35.4</small>

## 8. Part 7 메시지 한눈에 보기와 Amd1 변경점

이 절은 23~25장에서 본 Part 7 메시지를 한 표에 모으고, 2018년 개정(Amd1)이 바꾼 점을 정리한다. 구현하다가 메시지 이름이나 PGN으로 빠르게 찾아보는 용도다.

### 메시지 요약 표

방향은 원문 설명을 기준으로 적었고, 원문이 송신 주체를 밝히지 않은 경우에는 기능 비트와 메시지 성격으로 판단했다. 기능 비트는 트랙터가 어떤 원격 제어 기능을 지원하는지 알리는 facility 비트다([24장](/study/isobus/24-hitch-pto-valve-control)). PDU1은 PS가 목적지 주소인 메시지이고, WSM은 Working Set Master의 약어다. "자세히" 열은 그 메시지를 설명한 블로그 장이고, "근거" 열은 표준 원문의 절 번호다. 근거 열은 원문과 대조할 때만 보면 된다.

| 메시지 | PGN | 우선순위 | 주기 | 방향 | 자세히 | 근거 |
|---|---|---|---|---|---|---|
| Time/Date | 65254(0xFEE6) | 6 | 요청 시 | 트랙터 → 작업기 | [23장](/study/isobus/23-implement-messages-basics) | B.1 |
| Ground-based speed and distance | 65097(0xFE49) | 3 | 100 ms | 트랙터 → 작업기 | [23장](/study/isobus/23-implement-messages-basics) | B.2 |
| Wheel-based speed and distance | 65096(0xFE48) | 3 | 100 ms | 트랙터 → 작업기 | [23장](/study/isobus/23-implement-messages-basics) | B.3 |
| Maintain power | 65095(0xFE47) | 6 | 키 OFF 후 필요 시, 상태 변화 시 | 작업기 → 트랙터 | [22장](/study/isobus/22-tractor-ecu) | B.4 |
| Secondary or front hitch status | 65094(0xFE46) | 3 | 100 ms | 트랙터 → 작업기 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.6 |
| Primary or rear hitch status | 65093(0xFE45) | 3 | 100 ms | 트랙터 → 작업기 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.7 |
| Secondary or front PTO output shaft | 65092(0xFE44) | 3 | 체결 시 100 ms, 그 외 요청 시 | 트랙터 → 작업기 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.8 |
| Primary or rear PTO output shaft | 65091(0xFE43) | 3 | 체결 시 100 ms, 그 외 요청 시 | 트랙터 → 작업기 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.9 |
| Hitch and PTO commands | 65090(0xFE42) | 3 | 활성 시 100 ms | 작업기 → 트랙터 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.10 |
| Auxiliary valve n estimated flow | 65040+n(0xFE10+n) | 3 | 100 ms | 트랙터 → 작업기 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.11·B.15 |
| Auxiliary valve n measured flow | 65056+n(0xFE20+n) | 3 | 100 ms | 트랙터 → 작업기 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.12·B.16 |
| Auxiliary valve n command | 65072+n(0xFE30+n) | 3 | 활성 시 100 ms | 작업기 → 트랙터 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.13·B.17 |
| Lighting command | 65089(0xFE41) | 3 | 램프 상태 변화 시, 최대 1 s 간격 | 트랙터 → 조명 컨트롤러 | [22장](/study/isobus/22-tractor-ecu) | B.18 |
| Lighting data | 65088(0xFE40) | 6 | 요청 시 | 조명 컨트롤러 → 트랙터 | [22장](/study/isobus/22-tractor-ecu) | B.19 |
| Background lighting level command | 53248(0xD000), PDU1 | 3 | 변화 시, 최대 5 s 간격 | 지정 대상(DA)으로 | [22장](/study/isobus/22-tractor-ecu) | B.20 |
| Language command | 65039(0xFE0F) | 6 | 초기화 시, 요청 시 | VT(·TECU·TC) → 전체 | 이 장 1~2절 | B.21 |
| Request for repetition rate | 52224(0xCC00), PDU1 | 6 | 요청 시 | 메시지 사용자 → 송신자 | 이 장 3절 | B.22.1 |
| Response for repetition rate | 65038(0xFE0E) | 6 | 요청 시 | 송신자 → 전체 | 이 장 3절 | B.22.2 |
| Working Set Master | 65037(0xFE0D) | 7 | 필요 시 | 작업기(WSM) → 전체 | [26장](/study/isobus/26-isobus-network-mgmt) | B.23.2 |
| Working Set Member | 65036(0xFE0C) | 7 | 필요 시 | 작업기(WSM) → 전체 | [26장](/study/isobus/26-isobus-network-mgmt) | B.23.3 |
| Tractor control mode command (폐기) | 65035(0xFE0B) | 3 | 기본 100 ms | 작업기 → 트랙터 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.24.1 |
| Tractor control command tractor response (폐기) | 65034(0xFE0A) | 3 | 명령마다 | 트랙터 → 작업기 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.24.2 |
| Tractor facility response | 65033(0xFE09) | 3 | 전원 인가 시, 요청 시 | 트랙터 → 작업기 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.24.3 |
| Required tractor facilities | 65032(0xFE08) | 3 | 요청 시 | 작업기 → 트랙터 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.24.4 |
| General-purpose valve estimated flow | 50688(0xC600), PDU1 | 3 | 100 ms | 밸브 → 지정 대상 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.25.2 |
| General-purpose valve measured flow | 50432(0xC500), PDU1 | 3 | 100 ms | 밸브 → 지정 대상 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.25.3 |
| General-purpose valve command | 50176(0xC400), PDU1 | 3 | 활성 시 100 ms | 제어 CF → 밸브 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.25.4 |
| General-purpose valve load sense pressure | 1792(0x0700), PDU1 | 6 | 활성 시 100 ms | 밸브 → 지정 대상 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.25.5 |
| Guidance system command | 44288(0xAD00), PDU1 | 3 | 100 ms | 가이던스 → 조향 시스템(TECU) | [24장](/study/isobus/24-hitch-pto-valve-control) | B.26.1 |
| Guidance machine status | 44032(0xAC00), PDU1 | 3 | 100 ms | 조향 시스템(TECU) → 가이던스 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.26.2 |
| ISOBUS compliance certification | 64834(0xFD42) | 6 | 요청 시 | 각 CF → 요청자 | [27장](/study/isobus/27-diagnostics-identification) | B.27 |
| Machine selected speed | 61474(0xF022) | 3 | 100 ms | 트랙터 → 작업기 | [23장](/study/isobus/23-implement-messages-basics) | B.28.1 |
| Machine selected speed command | 64835(0xFD43) | 3 | 100 ms | 작업기 → 트랙터 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.28.2 |
| Implement operating state command | 64771(0xFD03) | 3 | 1 s, 상태 변화 시 | 트랙터 → 작업기 | 이 장 4절 | B.29 |
| All implements stop operations switch state | 64770(0xFD02) | 3 | 1 s, 상태 변화 시 | 정지 스위치 CF → 전체 | 이 장 4절 | B.30 |
| Drive strategy status | 64717(0xFCCD) | 6 | 500 ms | 트랙터 → 작업기 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.31 |
| Drive strategy command | 64718(0xFCCE) | 3 | 500 ms, 변화 시(100 ms 이상 간격) | 작업기 → 트랙터 | [24장](/study/isobus/24-hitch-pto-valve-control) | B.32 |
| Heartbeat | 61668(0xF0E4) | 3 | 요청받으면 100 ms | 각 CF → 소비 CF | 이 장 5~6절 | B.33.2 |
| Front·rear hitch roll and pitch | 61695(0xF0FF)·61697(0xF101) | 3 | 100 ms | 트랙터 → 작업기 | [24장](/study/isobus/24-hitch-pto-valve-control) | Amd1 B.6.2·B.7.2 |
| Front·rear hitch roll and pitch sensitivity | 64527(0xFC0F)·64526(0xFC0E) | 6 | 변화 시 100 ms, 무변화 시 1 s | 트랙터 → 작업기 | [24장](/study/isobus/24-hitch-pto-valve-control) | Amd1 B.6.3·B.7.3 |
| Front·rear hitch roll and pitch command | 61696(0xF100)·61698(0xF102) | 3 | 100 ms | 작업기 → 트랙터 | [24장](/study/isobus/24-hitch-pto-valve-control) | Amd1 B.6.4·B.7.4 |
| Front·rear hitch yaw | 64387(0xFB83)·64386(0xFB82) | 3 | 100 ms | 트랙터 → 작업기 | [24장](/study/isobus/24-hitch-pto-valve-control) | Amd1 B.6.5·B.7.5 |
| Front·rear hitch yaw command | 61758(0xF13E)·61759(0xF13F) | 3 | 100 ms | 작업기 → 트랙터 | [24장](/study/isobus/24-hitch-pto-valve-control) | Amd1 B.6.6·B.7.6 |
| Operator status | 64388(0xFB84) | 3 | 1 s, 상태 변화 시(200 ms 이상 간격) | 운전자 감지 CF → 전체 | 이 장 7절 | Amd1 B.33.3.6 |

### Amd1(2018)의 주요 변경

Amd1이 바꾼 점과 구현에 주는 영향은 다음과 같다. TIM(Tractor-Implement Management)은 AEF가 정의하고 있는 트랙터-작업기 관리 기능이고, GNSS는 GPS 같은 위성 측위 시스템을 통틀어 부르는 말이다.

| 영역 | 변경 | 구현 영향 | 자세히 | 근거 |
|---|---|---|---|---|
| 속도 정의 | ground-based 센서 예에 GPS·LIDAR·고정 물체 추적 추가 | 레이더가 없는 트랙터도 GNSS 기반 값을 ground-based로 보낼 수 있다 | [23장](/study/isobus/23-implement-messages-basics) | Amd1 A.5·A.6 |
| draft(견인력) 부호 | "heading 반대" → "전진 주행 방향 반대", 운전석 반전과 무관하다는 NOTE | 운전석 반전 트랙터에서 부호를 뒤집지 않는다 | [24장](/study/isobus/24-hitch-pto-valve-control) | Amd1 A.19.7~A.19.9 |
| 히치 자세 | 전·후방 roll·pitch·yaw 측정·명령·감도 메시지 신설 | 새 PGN 10개 | [24장](/study/isobus/24-hitch-pto-valve-control) | Amd1 A.19.15~A.19.50, B.6.2~B.7.6 |
| 고분해능 유량 | 보조 밸브 0·15번과 범용 밸브에 2바이트 유량 추가 | 저분해능 필드도 계속 채워야 한다 | [24장](/study/isobus/24-hitch-pto-valve-control) | Amd1 A.21.51~A.21.60 |
| 언어 | 국가 코드(Bytes 7,8) 추가, destination-specific 요청 권고 | 예약 FF FF가 곧 "국가 미지정" | 이 장 1~2절 | Amd1 A.23.1, B.21 |
| 가이던스 | 원격 engage 스위치 상태(Byte 5 bits 8,7) | 차량이 가이던스 engage 스위치를 직접 제공할 수 있다 | [24장](/study/isobus/24-hitch-pto-valve-control) | Amd1 A.28.10, B.26.2 |
| 운전자 상태 | Operator status 메시지 신설, 카운터와 CRC-8 | Heartbeat와 같은 검증 로직을 재사용한다 | 이 장 7절 | Amd1 A.35, B.33.3.6 |
| 조명 | 형식승인 조명은 7핀 커넥터로 제어하고 Lighting command에 의존하면 안 된다는 문단 추가 | Lighting command는 형식승인 대상이 아닌 조명의 제어와 진단에 쓴다 | [22장](/study/isobus/22-tractor-ecu) | Amd1 B.18 |
| TIM 예고 | TIM 예고와 영향받을 메시지 목록 | 명령 계열 메시지의 장기 대체 가능성 | [24장](/study/isobus/24-hitch-pto-valve-control) | Amd1 Annex D |

세부 SPN과 비트 배치는 [Part 7 부록](/study/isobus/appendix-iso-part07)의 Amendment 1 절에 정리돼 있다.

::: details 원문을 가진 독자를 위한 메모
원문을 옆에 두고 구현할 때 혼란을 주는 참조 오기와 누락이다. 모두 원문 자체의 문제이므로 메시지 이름과 SPN으로 대조하면 된다.

| 위치 | 원문 표기 | 실제로 맞는 참조 |
|---|---|---|
| B.15 Byte 4 | Auxiliary valve 15 estimated limit status (see A.21.49) | A.21.31(SPN 5191). A.21.49는 범용 밸브 파라미터다 |
| B.25.3 Byte 1 | General-purpose valve extend port measured flow (see A.21.18) | A.21.33. A.21.18은 보조 밸브 15번 파라미터다 |
| B.25.4 Byte 3 | fail safe mode (see A.21.44), state (see A.21.37) | 명령 메시지이므로 A.21.43·A.21.42가 맞다. 원문은 측정 파라미터를 가리킨다 |
| B.26.2 Byte 3 | bits 4,3 표기 없음 | Steering system readiness(A.28.6)의 자리로 보인다(확인 필요) |
| A.27.6 | Data length 2 bits | B.24.3은 Byte 8 bit 1 한 비트에 배치한다 |
| Amd1 B.21 | Country code (see A.23.1.1) | A.23.1.2. A.23.1.1은 언어 코드다 |
| Amd1 B.6.2 | Front hitch pitch angle (see A.19.19) | A.19.21. A.19.19는 roll 명령이다 |
| Amd1 A.19.32 | yaw 명령의 Type: Measured | 이름과 설명은 명령이다 |
| Amd1 Annex D | TIM 목록의 절 번호(B.9, B.13, B.16 …) | 2015년판 번호와 맞지 않아 메시지 이름으로 대조한다 |
:::

<small>근거: ISO 11783-7:2015 Annex B, ISO 11783-7:2015/Amd.1:2018</small>

::: tip 핵심 정리
- Language command(PGN 65039) 8바이트에는 언어 코드, 소수점·시간·날짜 형식, 단위 여덟 개, 국가 코드가 들어간다. 2비트 값 `11`은 "조치 없음"이다.
- 언어 설정은 VT에서 출발한다. Language command는 연결한 VT의 SA 기준으로 쓰고, TC 클라이언트는 TC의 값을 따르며, DDOP Localization label은 그 Bytes 1~6을 복사해 만든다.
- 메시지 주기는 Request for repetition rate로 바꿔 달라고 할 수 있다. 250 ms 안에 응답이 없으면 거절이고, 받아들인 송신자는 응답 후 250 ms 뒤에 주기를 바꾼다.
- ISB는 상태와 전이 횟수를 함께 본다. 횟수만 늘었다면 정지를 놓친 것이고, Permit이 돼도 작업기는 스스로 재시작하지 않는다.
- 안전 경로의 수신 측은 Heartbeat 시퀀스(증가폭·반복·254·255)와 300 ms 간격을 함께 검증하고, 간격은 메시지가 끊겨도 잡히도록 타이머로 감시한다.
:::

::: details 확인 문제
1. (개념) Language command의 Byte 3이 `0xFF`라면 소수점 기호와 시간 형식은 어떻게 하라는 뜻인가?
2. (개념) ISB 메시지의 스위치 상태가 Stop(00)에서 Permit(01)으로 바뀌었다. 작업기는 곧바로 작업을 다시 시작해도 되는가? 이때 전이 횟수는 어떻게 되는가?
3. (개념) Heartbeat를 보내지 않는 CF에게서 100 ms 주기 Heartbeat를 받으려면 무엇을 보내야 하는가? 250 ms 동안 응답이 없으면 어떻게 판단하는가?
4. (디코딩) VT(SA `0x26`, =38)가 보낸 Language command `65 6E 4F 00 40 10 47 42`를 받았다. 언어·국가, 소수점·시간·날짜 형식, 거리·부피·압력 단위를 디코딩하라. 이 VT에 오브젝트 풀을 올린 Working Set과, 같은 설정을 따르는 TC 클라이언트는 이 값을 각각 어떻게 써야 하는가? TC 클라이언트의 DDOP Localization label 7바이트는 무엇인가?
5. (설계) Heartbeat를 100 ms로 요청한 소비 CF가 시각 0, 100, 200, 400, 800 ms에 시퀀스 번호 249, 250, 0, 2, 6을 받았다. 각 수신 시점의 판정은 무엇인가? 제공 CF의 메시지가 연속 3개 빠지면 시퀀스 번호 규칙과 300 ms 타이밍 규칙 중 무엇에 먼저 걸리는가?

**답 가이드**
1. `0xFF` = `11 11 1111`이다. bits 8,7(소수점 기호)이 11, bits 6,5(시간 형식)가 11이므로 둘 다 "조치 없음", 곧 지금 설정을 바꾸지 말라는 뜻이다. bits 4~1은 예약이다.
2. 아니다. Permit으로 돌아와도 작업기는 바로 재시작하지 않는다. 운전자가 start/stop(Master ON/OFF) 스위치 같은 별도 수단으로 다시 켜야 한다. 전이 횟수는 Permit → Stop 때만 늘므로 Stop → Permit에서는 그대로다.
3. 그 CF의 주소로 Request for repetition rate(PGN 52224)를 보내, PGN 61668(Heartbeat)을 100 ms 주기로 요청한다. 데이터는 `E4 F0 00 64 00 FF FF FF`다. 250 ms 안에 Response for repetition rate(PGN 65038)가 오지 않으면 요청이 거절됐다고 보고, 위험도 평가에 따라 대응한다.
4. Bytes 1,2 = 'e','n' → 영어, Bytes 7,8 = 'G','B' → 영국(Amd1 국가 코드)이다. Byte 3 = 0x4F = 01 00 1111 → 소수점은 마침표, 시간은 24시간, 하위 4비트는 예약이다. Byte 4 = 0 → ddmmyyyy다. Byte 5 = 0x40 = 01 00 00 00 → 거리만 Imperial/US(마일)이고 면적·부피·질량은 미터법이다. Byte 6 = 0x10 = 00 01 00 00 → 압력만 Imperial/US(psi)이고 온도·힘·단위계는 미터법이다. Working Set은 자기 풀을 올린 VT(SA 0x26)의 설정에 맞춰 문자열·단위·스케일을 바꾸고, 지원하지 않는 설정이면 자체 기본값을 쓴다. TC 클라이언트는 TC가 알리는 설정을 따르고, Localization label은 Bytes 1~6에 Byte 7 = 0xFF를 붙인 `65 6E 4F 00 40 10 FF`다. 전역 요청으로 받은 다른 CF의 Language command가 아니라 연결한 VT의 SA에서 온 값을 써야 한다.
5. 249 → 첫 수신(기준값). 250 → +1로 정상. 0 → 250 다음 0이라 정상. 2 → 증가폭 2(1개 유실), 간격 200 ms로 정상. 6 → 증가폭 4(3개 유실)로 규칙 6의 Sequence Error이고, 간격 400 ms라 타이밍 오류이기도 하다. 이후 연속 8개의 올바른 값을 받아야 복귀한다. 연속 3개가 빠질 때 수신 간격을 타이머로 감시하면 마지막 정상 수신 후 300 ms가 지나는 순간 타이밍 규칙이 먼저 걸린다. 시퀀스 규칙은 다음 메시지가 도착해야 판정할 수 있기 때문이다. 도착 시점에만 간격을 재는 구현은 두 규칙이 동시에 걸리고, 송신이 완전히 멈추면 아예 오류를 못 잡는다. 표준의 구현 요구가 수신 측에 watchdog을 요구하는 이유다. 표준 본문의 "최대 3개 유실 허용" 해설과 규칙 6 문장이 한 칸 어긋난다는 점도 함께 짚는다.
:::

## 다음 챕터

- 다음: [26장 ISOBUS 네트워크 관리와 Working Set](/study/isobus/26-isobus-network-mgmt)
