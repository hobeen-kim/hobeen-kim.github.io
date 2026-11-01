---
title: "트랙터-작업기 메시지 (1): 읽는 법과 시간·속도·위치"
description: "ISO 11783-7 메시지를 리틀 엔디언, 무효값, 분해능·오프셋, 상태 비트 순서로 읽는 법을 익히고 속도·거리, 시각, 기계 선택 속도, 항법 위치 메시지를 직접 풀어 본다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, Part7, TECU, PGN, 디코딩]
prev: /study/isobus/22-tractor-ecu
next: /study/isobus/24-hitch-pto-valve-control
---

# 트랙터-작업기 메시지 (1): 읽는 법과 시간·속도·위치

::: info 학습 목표
- ISO 11783-7이 무엇을 정하는 문서인지, 명령(command)과 측정값(measured)이 어떻게 다른지 설명할 수 있다.
- 원시 바이트를 리틀 엔디언으로 묶고 분해능·오프셋을 적용해 물리값으로 바꿀 수 있다.
- 1·2·4바이트 원시값에서 무효값(`FE`·`FF` 계열)을 가려내고, 2비트 상태값(00·01·10·11)의 뜻을 읽을 수 있다.
- Wheel-based speed and distance, Time/Date, Machine selected speed 프레임을 바이트 단위로 디코딩할 수 있다.
- 항법 위치 메시지가 ISOBUS의 TP가 아니라 NMEA fast packet으로 온다는 점을 수신 구현에 반영할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [9장 J1939 메시지 구조](/study/isobus/09-j1939-message), [22장 트랙터 ECU](/study/isobus/22-tractor-ecu)
- 이 장에서 처음 나오는 말
  - TECU(Tractor ECU): 트랙터의 속도, 히치, PTO 같은 정보를 작업기 쪽 버스로 내보내는 트랙터의 대표 ECU다.
  - 원시값(raw value): 바이트에 실제로 적힌 정수다. 단위를 붙이기 전의 숫자다.
  - 분해능(resolution): 원시값 1이 나타내는 물리량 크기다. 0.001 m/s/bit라면 원시값 2500이 2.5 m/s다.
  - 오프셋(offset): 원시값에 분해능을 곱한 뒤 더하는 값이다. 음수를 나타낼 때 쓴다.
  - 리틀 엔디언(little endian): 여러 바이트로 된 수를 낮은 자리 바이트부터 보내는 순서다.
  - 무효값: 진짜 값 대신 "오류"나 "값 없음"을 알리려고 남겨 둔 원시값이다. 1바이트라면 `FE`(오류)와 `FF`(값 없음)다.
:::

트랙터와 작업기는 한 팀으로 일한다. 트랙터는 "지금 초속 2.5 m로 전진 중"처럼 자기 상태를 알리고 작업기는 "후방 히치를 64 %까지 올려 달라"처럼 부탁하는데, 이 대화의 메시지와 바이트 배치를 정한 문서가 ISO 11783-7이다. 자의 눈금 수에 한 칸의 길이를 곱해야 길이가 나오듯, 바이트에 적힌 숫자도 정해진 규칙으로 바꿔야 실제 값이 된다. 이 장은 그 읽는 법을 익히고 시간·속도·위치 메시지에 적용해 본다.

## 1. ISO 11783-7: 트랙터와 작업기의 대화 규칙

이 절은 Part 7이 무엇을 정하는 문서인지, 메시지가 어떤 묶음으로 나뉘는지 본다. 이어서 모든 메시지를 읽을 때 전제가 되는 "명령과 측정값"의 구분을 익힌다.

[20장](/study/isobus/20-isobus-network-topology)의 메시지 흐름 설명은 정상 동작 단계를 "TECU가 속도·PTO·히치 정보를 주기적으로 보낸다"는 한 줄로 요약했다. 그 한 줄의 실체가 <strong>ISO 11783-7(Implement messages application layer)</strong>이다. 트랙터와 작업기 사이의 응용 메시지를 정하는 표준 문서이고, 이 장과 다음 두 장에서는 줄여서 Part 7이라고 부른다.

[20장](/study/isobus/20-isobus-network-topology)과 [22장](/study/isobus/22-tractor-ecu)에서 본 TECU 클래스는 트랙터가 어떤 메시지 묶음을 제공해야 하는지 정한다. Part 7은 그 메시지 하나하나의 PGN(Parameter Group Number, 메시지 종류 번호), 송신 주기, 바이트·비트 배치, 값의 의미를 정한다. 여기서는 현행 3판(ISO 11783-7:2015)과 2018년 개정(ISO 11783-7:2015/Amd.1:2018, 이하 Amd1)을 기준으로 구현자가 지켜야 하는 규칙을 따라간다. 파라미터 정의 전체는 [Part 7 부록](/study/isobus/appendix-iso-part07)에 있다.

Part 7은 본문이 몇 쪽뿐이고 실질 내용은 뒤쪽 부록에 있다. 한 부록은 파라미터 사전이다. 값 하나하나의 길이·분해능·오프셋·범위와 SPN(Suspect Parameter Number, 값 하나하나에 붙은 식별 번호)을 정한다. 다른 부록은 그 파라미터를 어떤 PGN의 몇 번째 바이트에 담는지 정한다. 나머지 두 부록은 참고 자료다. 문서 첫머리에는 이 파트의 메시지로 작업기를 자동 제어할 때 주의하라는 안전 경고가 있고, 안전 모드 동작은 ISO 11783-9(트랙터 ECU를 정하는 표준 문서)를 보라고 적혀 있다.

### 기능별 메시지 지도

Part 7 메시지는 하는 일에 따라 일곱 묶음으로 나눌 수 있다. 이 장은 시간·위치와 속도·거리 묶음을 다루고, 나머지는 24장과 25장이 다룬다.

| 묶음 | 대표 메시지 | 주로 보내는 쪽 | 다루는 장 |
|---|---|---|---|
| 시간·위치 | Time/Date, 항법 위치 | TECU, GNSS 수신기 | 이 장 |
| 속도·거리 | Ground-based·Wheel-based speed and distance, Machine selected speed | TECU | 이 장 |
| 히치·PTO | 히치·PTO 상태, Hitch and PTO commands | 상태는 트랙터, 명령은 작업기 | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 유압 밸브 | 보조 밸브, 범용 밸브 | 상태는 밸브 쪽, 명령은 작업기 | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 트랙터 제어 | 기능 확인, 가이던스, 속도 명령, 구동 전략 | 양방향 | [24장](/study/isobus/24-hitch-pto-valve-control) |
| 시스템 설정 | Language command, 가변 반복 주기 | VT·TECU·TC, 메시지 사용자 | [25장](/study/isobus/25-settings-safety-messages) |
| 안전 | 작업기 작동 상태, 전체 작업기 정지, Heartbeat, 운전자 상태(Amd1) | TECU, 정지 스위치 CF, 모든 CF | [25장](/study/isobus/25-settings-safety-messages) |

GNSS 수신기는 GPS 같은 위성 항법 신호로 위치를 구하는 장치다. VT(Virtual Terminal)는 운전석의 공용 화면이고, TC(Task Controller)는 작업 계획과 기록을 맡는 장치다.

전원 유지 메시지와 조명 메시지는 [22장](/study/isobus/22-tractor-ecu)에서, Working Set 메시지는 [26장](/study/isobus/26-isobus-network-mgmt)에서, ISOBUS 적합성 인증 메시지는 [27장](/study/isobus/27-diagnostics-identification)에서 다룬다. PGN·우선순위·주기를 한데 모은 요약 표는 [25장](/study/isobus/25-settings-safety-messages)에 있다.

### 명령과 측정값: 명령은 부탁이다

Part 7의 파라미터는 모두 둘 중 하나로 분류된다. 이 구분을 알아야 "명령을 보냈는데 왜 그대로 안 됐지?"라는 질문에 답할 수 있다.

- <strong>명령(command)</strong>: 보내는 CF(Control Function, 네트워크에서 기능 하나를 맡은 주체)가 원하는 상태나 설정값이다. 표준은 명령이 수행됐다는 확인이 반드시 보장되지는 않는다고 적는다. 솔레노이드를 켜라고 명령해도 실제로 켜졌는지는 측정하지 않을 수 있다는 예를 든다. PTO 체결, 보조 밸브 extend, 후방 히치 이동 명령이 여기에 속한다.
- <strong>측정값(measured)</strong>: 보내는 CF가 측정하거나 관찰한 현재 값이다. 대지 속도, 히치 위치, PTO 체결 상태, 작업기의 작업 중 상태가 여기에 속한다.

트랙터는 받은 명령을 자동으로 실행하지 않는다. 제어 명령은 시스템에 운동이나 동력을 일으키고, 트랙터 안의 다른 시스템이 내는 명령과 동시에 들어올 수 있다. 그래서 각 명령은 다른 트랙터 제어·운전 조건과 함께 따져 보고, 트랙터 제어 시스템이 적절하다고 판단할 때만 실행한다. 식당 주문서가 주방에 들어가도 주방 사정에 따라 음식이 늦거나 안 나올 수 있는 것과 같다. 다만 트랙터는 못 들어준 이유를 상태 메시지에 적어 준다는 점이 주문서와 다르다(24장).

![작업기가 명령을 보내면 트랙터가 운전자 조작과 운전 조건을 따져 실행 여부를 정하고, 결과를 측정값 메시지로 알리는 고리](/images/study-isobus/23-p7-command-measured-light.png)
![작업기가 명령을 보내면 트랙터가 운전자 조작과 운전 조건을 따져 실행 여부를 정하고, 결과를 측정값 메시지로 알리는 고리](/images/study-isobus/23-p7-command-measured-dark.png)

구현 결론은 하나다. 작업기는 명령을 보낸 뒤 짝이 되는 측정값 메시지로 결과를 확인해야 한다. 히치 명령의 결과는 히치 상태 메시지에서, 밸브 명령의 결과는 밸브 유량 메시지에서 읽는다. 두 짝은 [24장](/study/isobus/24-hitch-pto-valve-control)에서 자세히 본다.

<small>근거: ISO 11783-7:2015 Safety precautions, 3.3.2</small>

## 2. 메시지를 읽는 네 단계

Part 7 메시지는 모두 같은 규칙으로 읽는다. 여러 바이트를 하나의 수로 묶고, 무효값인지 확인하고, 분해능과 오프셋으로 물리값을 만들고, 상태 비트를 꺼낸다. 이 네 단계를 익히면 이 장과 다음 두 장의 메시지를 모두 같은 방식으로 풀 수 있다.

### 바이트와 비트에 번호 붙이기

Part 7은 값의 자리를 "Byte 8 bits 2,1"처럼 부른다. 바이트는 데이터 필드의 첫 바이트를 Byte 1로 해서 Byte 8까지 센다. 비트는 바이트 하나 안에서 bit 1(가장 낮은 자리, 최하위)부터 bit 8(가장 높은 자리, 최상위)까지 센다. "Byte 8 bits 2,1"은 8번째 바이트의 최하위 2비트다. 예를 들어 Byte 8이 `0x15`(=21)이면 2진수로 `0001 0101`이고, bits 2,1은 맨 오른쪽 두 자리 `01`이다.

### 1단계: 여러 바이트를 하나의 수로 묶는다

2바이트 이상인 수치 파라미터는 <strong>하위 바이트(LSB, 가장 낮은 자리 바이트)부터</strong> 보내야 한다(shall). 리틀 엔디언이다. 사람은 높은 자리부터 쓰므로, 받은 바이트를 거꾸로 놓아야 우리가 아는 수가 된다. 속도가 담긴 Bytes 1,2가 `C4 09`로 왔다면 뒤의 `09`가 높은 자리다. 높은 자리부터 다시 쓰면 `0x09C4`이고, 10진수로 9 × 256 + 196 = 2500이다.

나머지 규칙은 두 가지다.

- 문자열은 왼쪽 문자부터 보낸다.
- 파라미터가 바이트 경계에 걸치면 하위 비트를 낮은 번호 바이트에 넣고, 남은 상위 비트를 다음 바이트의 bit 1부터 채운다.

아래 그림은 5비트 값이 두 바이트에 걸친 예다. 값의 아래 세 자리(`101`)가 Byte 7의 bits 8~6에, 위 두 자리(`10`)가 Byte 8의 bits 2,1에 들어 있다. 두 조각을 높은 자리부터 이어 붙이면 `10101`, 즉 21이다.

![바이트 안의 비트 번호(bit 8이 최상위, bit 1이 최하위)와, 5비트 값의 아래 세 비트가 Byte 7 bits 8~6에, 위 두 비트가 Byte 8 bits 2,1에 나뉘어 들어가는 모습](/images/study-isobus/23-p7-bit-numbering-light.png)
![바이트 안의 비트 번호(bit 8이 최상위, bit 1이 최하위)와, 5비트 값의 아래 세 비트가 Byte 7 bits 8~6에, 위 두 비트가 Byte 8 bits 2,1에 나뉘어 들어가는 모습](/images/study-isobus/23-p7-bit-numbering-dark.png)

이 규칙 덕분에 8바이트 데이터 필드 전체를 하나의 64비트 리틀 엔디언 정수로 보면, 어떤 필드든 시프트(비트를 옆으로 미는 연산)와 마스크(필요한 비트만 남기는 연산) 한 번으로 꺼낼 수 있다. 아래 `get_bits`가 그 도우미이고, 이 장과 다음 장의 예제는 모두 이 함수를 쓴다.

```python
def get_bits(data: bytes, byte_no: int, bit_no: int, length: int) -> int:
    """Byte n(1부터), bit m(1=최하위)에서 시작하는 length비트 값을 꺼낸다."""
    word = int.from_bytes(data, "little")
    shift = (byte_no - 1) * 8 + (bit_no - 1)
    return (word >> shift) & ((1 << length) - 1)


# Figure 1 a)처럼 5비트 값이 Byte 7 bits 8..6과 Byte 8 bits 2..1에 걸친 경우
frame = bytes([0, 0, 0, 0, 0, 0, 0b101_00000, 0b000000_10])
assert get_bits(frame, 7, 6, 5) == 0b10101
```

`get_bits(데이터, 바이트 번호, 시작 비트 번호, 비트 수)` 형태로 부른다. 시작 비트는 그 필드의 가장 낮은 자리 비트다. 마지막 줄은 위 그림의 예를 확인한다. Byte 7 bit 6에서 시작하는 5비트를 꺼내면 `0b10101`(=21)이 나온다. 코드 주석의 그림 번호는 표준 문서에 실린 같은 예를 가리킨다.

### 2단계: 무효값인지 먼저 본다

센서가 고장 나거나 트랙터에 그 기능이 없어도 메시지의 자리는 채워서 보내야 한다. 그래서 Part 7은 원시값 범위의 맨 윗부분을 "진짜 값이 아님"을 알리는 신호로 남겨 두었다. 수신 측은 숫자를 물리값으로 바꾸기 전에 그 값이 유효 범위인지부터 봐야 한다. 1바이트 `0xFF`(=255)에 분해능 1 min/bit를 곱해 "남은 전원 시간 255분"으로 읽으면 틀린다. `0xFF`는 "이 값을 제공하지 않는다"는 뜻이다.

범위는 1·2·4바이트 파라미터의 최상위 바이트 하나로 가른다. 최상위 바이트가 `0xFA`(=250) 이하면 유효값이다. 표의 `xx`는 아래 자리에 어떤 값이 와도 된다는 뜻이다.

| 최상위 바이트 | 1 byte | 2 bytes | 4 bytes | 의미 |
|---|---|---|---|---|
| 0x00~0xFA | 0~250 | 0~64 255 | 0~4 211 081 215 | 유효 신호 |
| 0xFB | 251 | 64 256~64 511 | 0xFBxxxxxx | 파라미터별 지시값 |
| 0xFC~0xFD | 252~253 | 64 512~65 023 | 0xFCxxxxxx~0xFDxxxxxx | 향후 지시값용 예약 |
| 0xFE | 254 | 65 024~65 279 | 0xFExxxxxx | 오류 지시(error indicator) |
| 0xFF | 255 | 65 280~65 535 | 0xFFxxxxxx | 사용 불가·미설치·미요청·조치 없음 |

파라미터별 지시값은 파라미터 정의가 따로 뜻을 정해 쓰는 특수값이고, 예약 구역은 앞으로 쓰려고 비워 둔 자리다. 2바이트 값이라면 리틀 엔디언으로 묶은 수의 높은 자리 바이트, 즉 메시지에서는 뒤에 오는 바이트를 본다. 속도 `C4 09`는 최상위 바이트가 `09`라서 유효값이다. 속도 자리에 `FF FF`가 왔다면 "속도를 제공하지 않음"이고, `12 FE`가 왔다면 최상위 바이트가 `FE`라서 "속도 센서 오류"다.

![1바이트 값 0~255를 유효값(0~250), 파라미터별 지시값(251), 예약(252~253), 오류(254), 사용 불가(255) 구역으로 나누고, 2바이트 값은 최상위 바이트로 같은 구역을 판정하는 모습](/images/study-isobus/23-p7-value-ranges-light.png)
![1바이트 값 0~255를 유효값(0~250), 파라미터별 지시값(251), 예약(252~253), 오류(254), 사용 불가(255) 구역으로 나누고, 2바이트 값은 최상위 바이트로 같은 구역을 판정하는 모습](/images/study-isobus/23-p7-value-ranges-dark.png)

ASCII 문자 파라미터만 규칙이 다르다. 1~254가 유효 문자이고 0이 오류, 255가 사용 불가다.

아래 `classify`는 위 표를 그대로 코드로 옮긴 것이다. 최상위 바이트를 꺼내 `0xFA` 이하인지 보고, 넘으면 어느 구역인지 돌려준다.

```python
def classify(raw: int, nbytes: int) -> str:
    """Part 7 Table 1 기준으로 1·2·4바이트 원시값을 분류한다."""
    top = raw >> (8 * (nbytes - 1))
    if top <= 0xFA:
        return "valid"
    return {0xFB: "parameter-specific", 0xFC: "reserved", 0xFD: "reserved",
            0xFE: "error", 0xFF: "not available"}[top]


assert classify(0xFA, 1) == "valid"              # 히치 위치 100 %
assert classify(0xFAFF, 2) == "valid"            # 속도 64.255 m/s
assert classify(0xFE12, 2) == "error"
assert classify(0xFFFF, 2) == "not available"
assert classify(0xFAFFFFFF, 4) == "valid"        # 거리 4 211 081.215 m
```

`0xFAFF`처럼 최상위 바이트가 `FA`면 아래 바이트가 무엇이든 유효값이다. 그래서 2바이트 속도의 최댓값은 `0xFAFF`(=64 255), 즉 64.255 m/s다. 4바이트 거리의 최댓값은 `0xFAFFFFFF`(=4 211 081 215), 즉 4 211 081.215 m다.

### 3단계: 분해능과 오프셋으로 물리값을 만든다

유효값이라고 확인했으면 단위가 있는 물리값으로 바꾼다. 식은 하나다.

<strong>물리값 = 원시값 × 분해능 + 오프셋</strong>

분해능은 원시값 1이 나타내는 크기이고, 오프셋은 음수까지 나타내려고 더하는 값이다. 원시값은 0 이상인 정수뿐이므로, 음수 오프셋을 더해 0 아래 값을 만든다. 예를 들어 지역 시 오프셋은 1 h/bit, −125 h 오프셋이라 원시값 134(`0x86`)가 134 × 1 − 125 = +9시간이다. 이 장과 다음 장에 나오는 대표 파라미터로 연습하면 다음과 같다.

| 파라미터 | 길이 | 분해능 | 오프셋 | 원시 바이트 | 계산 | 물리값 |
|---|---|---|---|---|---|---|
| 차속 | 2바이트 | 0.001 m/s/bit | 0 | `C4 09` | 2500 × 0.001 | 2.500 m/s |
| 주행 거리 | 4바이트 | 0.001 m/bit | 0 | `4E 61 BC 00` | 12 345 678 × 0.001 | 12 345.678 m |
| 지역 시 오프셋 | 1바이트 | 1 h/bit | −125 h | `86` | 134 × 1 − 125 | +9 h |
| 후방 히치 위치 | 1바이트 | 0.4 %/bit | 0 % | `A0` | 160 × 0.4 | 64 % |
| 견인력(draft) | 2바이트 | 10 N/bit | −320 000 N | `40 7E` | 32 320 × 10 − 320 000 | 3 200 N |

상위 바이트만으로 어림하는 법도 알아 두면 좋다. 2바이트 속도에서 상위 바이트 1은 256 × 0.001 = 0.256 m/s다. `C4 09`라면 상위 바이트 `09`만 보고도 9 × 0.256 = 2.304 m/s 근처라는 것을 바로 안다.

### 4단계: 상태 비트를 꺼낸다

켜짐·꺼짐처럼 상태를 나타내는 파라미터는 2비트에 담긴다. 2비트면 00, 01, 10, 11 네 값을 쓸 수 있어서, 두 상태(꺼짐·켜짐)에 오류와 "값 없음"을 하나씩 더할 수 있다. 측정값과 명령은 같은 값에 다른 뜻을 붙인다.

| 값 | 측정값(measured) | 명령(command) |
|---|---|---|
| 00 | 비활성(Off, passive) | 끄기 명령 |
| 01 | 활성(On, active) | 켜기 명령 |
| 10 | 오류 지시 | 예약(보내지 않는다) |
| 11 | 사용 불가·미설치 | 상관없음(현재 상태 유지) |

같은 11이라도 측정값에서는 "그 기능이 없다", 명령에서는 "이 기능은 건드리지 마라"다. 한 메시지에 명령 필드가 여럿 들어 있는 Hitch and PTO commands([24장](/study/isobus/24-hitch-pto-valve-control)) 같은 메시지에서 이 차이가 사고를 막는다. 건드리지 않을 필드를 11로 채우면 트랙터가 그 기능을 그대로 두기 때문이다.

Part 7에는 3비트 limit status, 6비트 exit/reason code처럼 더 긴 상태 필드도 있다. 읽는 법은 같다. `get_bits`로 꺼낸 뒤 그 파라미터의 값 표에서 뜻을 찾는다. 이 필드들은 24장에서 다룬다.

<small>근거: ISO 11783-7:2015 3.3.1, 3.3.3</small>

## 3. 속도와 거리 메시지: Ground-based와 Wheel-based

작업기가 가장 자주 쓰는 트랙터 정보는 속도다. 면적당 뿌리는 양을 맞추는 작업기는 속도가 바뀌면 토출량도 바꿔야 한다. 트랙터는 속도를 두 가지 방법으로 재서 두 메시지로 보낸다.

둘 다 TECU가 100 ms마다 우선순위 3으로 방송한다. PGN은 Ground-based가 65097(`0xFE49`), Wheel-based가 65096(`0xFE48`)이다.

- <strong>Ground-based(대지 속도)</strong>: 휠 슬립(바퀴가 헛도는 것)의 영향을 받지 않는 센서로 잰 실제 대지 속도다. Amd1은 그 예로 레이더, GPS, LIDAR(레이저로 거리를 재는 센서), 고정 물체 추적을 든다(2015년판 본문은 "레이더 같은 센서"였다).
- <strong>Wheel-based(바퀴 기준 속도)</strong>: 바퀴나 테일샤프트(바퀴 쪽으로 동력을 보내는 축) 회전수로 계산한 값이다.

바퀴가 진흙에서 헛돌면 바퀴는 빨리 돌아도 트랙터는 덜 나아간다. 그래서 두 값의 차이는 주로 휠 슬립을 반영한다(추론).

| 항목 | Ground-based | Wheel-based |
|---|---|---|
| Bytes 1,2 | 속도, 0.001 m/s/bit | 같음 |
| Bytes 3~6 | 거리, 0.001 m/bit | 같음 |
| Byte 7 | 예약 | 남은 트랙터 전원 시간(1 min/bit, 0~250) |
| Byte 8 | bits 2,1 방향, 나머지 예약 | 운전석 반전·Start/Stop·Key switch·방향 |
| 정지 중 방향 | 다른 방향이 감지될 때까지 마지막 방향 유지 | 다른 방향이 감지되거나 선택·체결될 때까지 유지 |

- 속도 범위는 0~64.255 m/s이고, 상위 바이트만 놓고 보면 1이 0.256 m/s다. 거리는 4 211 081.215 m를 넘으면 0으로 돌아가 다시 누적한다.
- 방향은 섀시(차체) 기준이다. 운전석을 뒤로 돌려도 Forward·Reverse가 바뀌지 않는다. 운전자 관점에서 반전됐는지는 Wheel-based 메시지의 Byte 8 bits 8,7(Operator direction reversed)이 따로 알려 준다.
- wheel-based 방향은 "선택·체결"로도 바뀐다. 정지한 채 후진을 넣고 체결하면 속도 0에서 방향이 Reverse로 바뀔 수 있다는 뜻으로 읽힌다.
- 두 속도 모두 저속에서 정확도가 떨어지고, wheel-based는 저속에서 100 ms마다 갱신되지 않을 수 있다. 저속에서 같은 값이 몇 번 반복된다고 센서 고장으로 단정하면 안 된다.
- Byte 7(남은 전원 시간)과 Byte 8 bits 4,3(Key switch state)의 의미, 키를 끈 뒤 이 메시지를 2 s 더 보내는 규칙과 전원 유지 요청 메시지는 [22장](/study/isobus/22-tractor-ecu)에서 다뤘다.

트랙터가 두 메시지를 모두 보내면 작업기는 같은 순간의 두 속도로 슬립을 어림할 수 있다. wheel-based 2.500 m/s, ground-based 2.430 m/s라면 (2.500 − 2.430) / 2.500 = 2.8 %다. 이 계산식은 표준이 정한 것이 아니라 응용이다.

<small>근거: ISO 11783-7:2015 B.2, B.3, A.5~A.12, A.31; Amd1 A.5</small>

## 4. 예제 하나로 끝까지: Wheel-based 프레임 손계산

2절의 네 단계를 실제 프레임 하나에 끝까지 적용해 보자. TECU(SA는 예로 `0xF0`(=240))가 보낸 CAN ID `0x0CFE48F0`, 데이터 `C4 09 4E 61 BC 00 FF 15` 프레임이다.

먼저 ID를 읽는다. 29비트 ID를 [9장](/study/isobus/09-j1939-message)의 방법으로 나누면 우선순위 3, PGN `0xFE48`(=65096), SA(Source Address, 보낸 쪽 주소) `0xF0`이다. PGN 65096이 Wheel-based speed and distance다. 이 메시지의 바이트 배치는 아래 그림과 같다.

![Wheel-based speed and distance(PGN 65096) 바이트 배치: Byte 1~2 속도 0x09C4, Byte 3~6 거리 0x00BC614E, Byte 7 남은 전원 시간 FF, Byte 8의 2비트 필드 네 개](/images/study-isobus/13-p7-wheel-speed-layout-light.png)
![Wheel-based speed and distance(PGN 65096) 바이트 배치: Byte 1~2 속도 0x09C4, Byte 3~6 거리 0x00BC614E, Byte 7 남은 전원 시간 FF, Byte 8의 2비트 필드 네 개](/images/study-isobus/13-p7-wheel-speed-layout-dark.png)

이제 필드마다 네 단계를 차례로 적용한다.

1. <strong>Bytes 1,2 = `C4 09`(속도)</strong>
   - 묶기: 뒤 바이트가 높은 자리라서 `0x09C4` = 2500이다.
   - 무효값 확인: 최상위 바이트 `09`가 `FA` 이하라서 유효하다.
   - 물리값: 2500 × 0.001 + 0 = 2.500 m/s(9.0 km/h)다. 상위 바이트 0x09만 봐도 9 × 0.256 = 2.304 m/s라서 어림 검산이 된다.
2. <strong>Bytes 3~6 = `4E 61 BC 00`(거리)</strong>
   - 묶기: 거꾸로 놓으면 `0x00BC614E` = 12 345 678이다.
   - 무효값 확인: 최상위 바이트 `00`이라서 유효하다.
   - 물리값: 12 345 678 × 0.001 = 12 345.678 m다.
3. <strong>Byte 7 = `FF`(남은 전원 시간)</strong>
   - 무효값 확인: Byte 7 = 0xFF는 1바이트의 사용 불가 값이다. 이 트랙터는 남은 전원 시간을 제공하지 않는다. 분해능을 곱하지 않고 여기서 멈춘다.
4. <strong>Byte 8 = `15`(상태 비트 네 개)</strong>
   - 상태 비트: Byte 8 = 0x15 = 00 01 01 01이다. 왼쪽부터 bits 8,7 / 6,5 / 4,3 / 2,1이다.

| 비트 | 값 | 파라미터 | 뜻 |
|---|---|---|---|
| 8,7 | 00 | Operator direction reversed(운전석 반전) | 반전 아님 |
| 6,5 | 01 | Start/Stop state(작업기 작동 스위치) | Start: 작업기 작동 허용 |
| 4,3 | 01 | Key switch state(키 스위치) | Off가 아님(키 ON) |
| 2,1 | 01 | Wheel-based machine direction(주행 방향) | Forward(전진) |

정리하면 이 프레임은 "운전석 반전 아님, Start(작업기 작동 허용), 키 ON(not Off), 전진, 2.500 m/s, 누적 12 345.678 m, 남은 전원 시간은 제공 안 함"이다. 이 메시지의 필드는 오프셋이 모두 0이라 더할 값이 없다. 오프셋이 있는 예는 5절 Time/Date의 지역 시 오프셋에서 본다.

같은 계산을 코드로 옮기면 다음과 같다. `classify`로 무효값을 먼저 거르고, 유효할 때만 분해능을 곱한다.

```python
def decode_wheel_speed(d: bytes) -> dict:
    spd = int.from_bytes(d[0:2], "little")
    dist = int.from_bytes(d[2:6], "little")
    return {
        "speed_mps": spd * 0.001 if classify(spd, 2) == "valid" else classify(spd, 2),
        "distance_m": dist * 0.001 if classify(dist, 4) == "valid" else classify(dist, 4),
        "max_power_min": d[6] if classify(d[6], 1) == "valid" else classify(d[6], 1),
        "operator_reversed": get_bits(d, 8, 7, 2),
        "start_stop": get_bits(d, 8, 5, 2),
        "key_switch": get_bits(d, 8, 3, 2),
        "direction": get_bits(d, 8, 1, 2),
    }


r = decode_wheel_speed(bytes.fromhex("C4094E61BC00FF15"))
assert abs(r["speed_mps"] - 2.5) < 1e-9
assert abs(r["distance_m"] - 12345.678) < 1e-6
assert r["max_power_min"] == "not available"
assert (r["operator_reversed"], r["start_stop"], r["key_switch"], r["direction"]) == (0, 1, 1, 1)


def distance_delta_m(prev_raw: int, cur_raw: int) -> float:
    """거리 카운터는 0xFAFFFFFF 다음에 0으로 돌아간다(A.9). 구간 거리는 모듈로로 구한다."""
    return ((cur_raw - prev_raw) % (0xFAFFFFFF + 1)) * 0.001


assert abs(distance_delta_m(0xFAFFFFF0, 0x00000010) - 0.032) < 1e-9
```

파이썬 인덱스는 0부터 세므로 `d[0:2]`가 Bytes 1,2이고 `d[6]`이 Byte 7이다. 아래쪽 `distance_delta_m`은 두 시점 사이에 간 거리를 구한다. 거리 카운터는 최댓값 `0xFAFFFFFF` 다음에 0으로 돌아가므로, 단순 뺄셈 대신 나머지 연산(모듈로)을 쓴다. 예에서는 카운터가 `0xFAFFFFF0`에서 0을 지나 `0x00000010`이 된 구간을 0.032 m로 바르게 계산한다.

## 5. Time/Date: 요청해야 받는 시각 메시지

작업 기록에 시각을 찍으려면 현재 날짜와 시각이 필요하다. Time/Date 메시지가 그 값을 준다. 속도 메시지와 가장 큰 차이는 주기적으로 오지 않는다는 점이다.

PGN 65254(`0xFEE6`)는 기본 우선순위 6이고 <strong>요청 시에만</strong> 보낸다. 100 ms마다 들어오는 속도 메시지와 달리, 시각이 필요한 CF가 Request(PGN 59904, 특정 PGN을 보내 달라고 요청하는 메시지, [10장](/study/isobus/10-j1939-request-ack))로 요청해야 받을 수 있다. Byte 1~3은 UTC 시각(초는 0.25 s/bit, 분, 시), Byte 4~6은 날짜(월, 일, 1985년 기준 연도), Byte 7·8은 지역 시각 오프셋(분, 시)이다. UTC(협정 세계시)는 영국 그리니치를 기준으로 한 세계 공통 시각이다. 두 오프셋은 모두 −125 오프셋이다.

| 바이트 | 내용 | 분해능 | 오프셋 |
|---|---|---|---|
| Byte 1 | 초 | 0.25 s/bit | 0 |
| Byte 2 | 분 | 1 min/bit | 0 |
| Byte 3 | 시 | 1 h/bit | 0 |
| Byte 4 | 월 | 1 month/bit | 0 |
| Byte 5 | 일 | 0.25 d/bit | 0 |
| Byte 6 | 연도 | 1 y/bit | 1985년 |
| Byte 7 | 지역 분 오프셋(Local minute offset) | 1 min/bit | −125 min |
| Byte 8 | 지역 시 오프셋(Local hour offset) | 1 h/bit | −125 h |

구현에서 틀리기 쉬운 곳은 네 군데다.

- 일(Byte 5)은 0.25일 단위다. 1~4가 첫째 날, 5~8이 둘째 날이고, 0은 null(값 없음)이다. 월 0도 null, 연도 0은 1985년이다. 날짜는 원시값을 4로 나눠 올림한다.
- Byte 8(Local hour offset)의 물리값 125, 즉 원시값 0xFA이면 Byte 1~6이 UTC가 아니라 <strong>지역 시각</strong>이다. 물리값 124(0xF9)는 UTC이지만 오프셋 미제공, −23~23(0x66~0x94, 10진수 102~148)은 UTC + 지역 오프셋, 나머지 값은 시간 기준을 알 수 없다는 뜻이다. 전체 구역은 아래 표와 같다.
- Local minute offset은 시각이 UTC로 보고될 때만 의미가 있다.
- 두 오프셋은 2004-10-15 기술 정오표로 SAE(J1939를 만든 미국 자동차 공학회)와 정의를 맞췄다. 그 전에는 분 오프셋이 0 오프셋(0~59 min), 시 오프셋이 −24 오프셋이었다. 오래된 장비가 섞인 시스템에서 시각이 몇 시간씩 어긋나면 이 차이를 먼저 의심한다.

| Byte 8 원시값 | 물리값 | Byte 1~6의 시각·날짜 | 지역 오프셋 |
|---|---|---|---|
| `0x00`~`0x65` | −125~−24 | 시간 기준 알 수 없음 | 알 수 없음 |
| `0x66`~`0x94` | −23~23 | UTC | Byte 7·8이 지역 오프셋 |
| `0x95`~`0xF8` | 24~123 | 시간 기준 알 수 없음 | 알 수 없음 |
| `0xF9` | 124 | UTC | 제공 안 함 |
| `0xFA` | 125 | 지역 시각 | 제공 안 함 |
| `0xFB`~`0xFF` | 126~130 | 시간 기준 알 수 없음 | 알 수 없음 |

2026-10-30 14:25:30 UTC, 지역 오프셋 +09:00을 담은 프레임 `78 19 0E 0A 78 29 7D 86`을 손으로 풀면 다음과 같다. 오프셋이 있는 필드(Byte 7·8)는 원시값에서 125를 뺀다.

| 바이트 | 원시값 | 계산 | 결과 |
|---|---|---|---|
| Byte 1 | `0x78` = 120 | 120 × 0.25 | 30.00 s |
| Byte 2 | `0x19` = 25 | 25 × 1 | 25 min |
| Byte 3 | `0x0E` = 14 | 14 × 1 | 14 h |
| Byte 4 | `0x0A` = 10 | 10 × 1 | 10월 |
| Byte 5 | `0x78` = 120 | 120 ÷ 4 = 30, 올림해도 30 | 30일 |
| Byte 6 | `0x29` = 41 | 41 + 1985 | 2026년 |
| Byte 7 | `0x7D` = 125 | 125 − 125 | 0 min |
| Byte 8 | `0x86` = 134 | 134 − 125 | +9 h(UTC 기준, 지역 오프셋 있음) |

시각은 2026-10-30 14:25:30 UTC이고, 9시간을 더한 지역 시각은 같은 날 23:25:30이다. 아래 코드는 같은 계산을 한다. Byte 8로 시간 기준(`basis`)을 먼저 가르고, 지역 오프셋이 유효한 범위일 때만 분 단위 오프셋을 계산한다. 파이썬 인덱스는 0부터 세므로 `d[0]`이 Byte 1, `d[7]`이 Byte 8이다.

```python
import math


def decode_time_date(d: bytes) -> dict:
    hour_raw, minute_raw = d[7], d[6]
    if hour_raw == 0xFA:
        basis = "local"                     # Byte 1~6이 지역 시각
    elif hour_raw == 0xF9 or 0x66 <= hour_raw <= 0x94:
        basis = "utc"
    else:
        basis = "unknown"
    offset_min = None
    if 0x66 <= hour_raw <= 0x94:
        offset_min = (hour_raw - 125) * 60 + (minute_raw - 125)
    return {
        "date": f"{d[5] + 1985:04d}-{d[3]:02d}-{math.ceil(d[4] / 4):02d}",
        "time": f"{d[2]:02d}:{d[1]:02d}:{d[0] * 0.25:05.2f}",
        "basis": basis,
        "offset_min": offset_min,
    }


# 2026-10-30 14:25:30 UTC, 지역 오프셋 +09:00
r = decode_time_date(bytes.fromhex("78190E0A78297D86"))
assert r == {"date": "2026-10-30", "time": "14:25:30.00", "basis": "utc", "offset_min": 540}
```

`offset_min`은 (134 − 125) × 60 + (125 − 125) = 540분, 즉 +9시간이다.

<small>근거: ISO 11783-7:2015 B.1, A.1~A.4; ISO 11783-3:2018 5.4.3</small>

## 6. Machine selected speed: 기계가 고른 속도 하나

속도원이 여럿이면 작업기는 어느 값을 믿어야 할지 고민하게 된다. Machine selected speed는 그 선택을 트랙터가 대신 해서 보내는 메시지다.

PGN 61474(`0xF022`)는 100 ms마다 우선순위 3으로 나간다. 기계가 wheel·ground·navigation 기반 속도 가운데 지금 기계 속도를 가장 잘 나타낸다고 판단한 값 하나를 보낸다. 속도·거리 스케일은 Ground-based·Wheel-based 메시지와 같고, Byte 7 bits 6~1에 exit/reason code, Byte 8에 limit status(bits 8~6), 속도원(bits 5~3), 방향(bits 2,1)이 들어간다. exit/reason code는 원격 명령을 받을 수 없는 이유를, limit status는 명령에 걸린 제한을 알리는 필드이고 [24장](/study/isobus/24-hitch-pto-valve-control)에서 자세히 본다.

| 속도원 값 | 뜻 |
|---|---|
| 000 | Wheel-based(바퀴 기준) |
| 001 | Ground-based(대지 속도) |
| 010 | Navigation-based(항법) |
| 011 | Blended(혼합) |
| 100 | Simulated(모의 속도) |
| 101·110 | 예약 |
| 111 | 사용 불가 |

Blended는 운전자나 제조사가 정한 논리로 여러 실제 속도원을 섞은 값이다. 표준은 ground 기반 속도가 0.5 m/s 미만이면 wheel 속도로 바꿔 보내는 예를 든다. Simulated는 기계가 실제로 움직이지 않을 때 작업기를 동작시키려고 시스템이 만든 속도다. 면적당 살포량을 속도로 계산하는 작업기라면 simulated를 받으면 정지 상태에서도 토출하게 되므로, 속도원 필드를 보고 동작을 정해야 한다(추론).

속도 제어에 쓰는 속도원에 관한 Part 9 규칙은 [22장](/study/isobus/22-tractor-ecu)의 TECU 클래스 표기('P') 설명에서 다뤘다.

예로 `DC 05 10 27 00 00 C0 05`를 손으로 풀면 다음과 같다.

- Bytes 1,2 = `DC 05` → `0x05DC` = 1500 → 1.500 m/s
- Bytes 3~6 = `10 27 00 00` → `0x00002710` = 10 000 → 10.000 m
- Byte 7 = `0xC0` = `11 000000` → bits 8,7은 예약(1로 채움), bits 6~1 = 000000은 exit/reason "사유 없음(all clear)"
- Byte 8 = `0x05` = `000 001 01` → limit status 000(제한 없음), 속도원 001(ground-based), 방향 01(전진)

```python
ms = bytes.fromhex("DC0510270000C005")
assert int.from_bytes(ms[0:2], "little") * 0.001 == 1.5     # 1.500 m/s
assert int.from_bytes(ms[2:6], "little") * 0.001 == 10.0    # 10.000 m
assert get_bits(ms, 7, 1, 6) == 0b000000                    # exit/reason: all clear
assert get_bits(ms, 8, 6, 3) == 0b000                       # limit status: not limited
assert get_bits(ms, 8, 3, 3) == 0b001                       # 속도원: ground-based
assert get_bits(ms, 8, 1, 2) == 0b01                        # 방향: forward
```

<small>근거: ISO 11783-7:2015 B.28.1, A.30.1~A.30.4, A.30.9; ISO 11783-9:2012 4.4.2.8</small>

## 7. 항법 위치 메시지: NMEA 2000을 빌려 쓴다

작업기가 위치에 맞춰 구획별로 살포를 끄고 켜려면 위치 정보가 필요하다. 그런데 Part 7은 항법 위치 메시지를 직접 정의하지 않는다. 이미 널리 쓰이는 선박용 표준을 그대로 가져다 쓴다.

ISO 11783 네트워크는 IEC 61162-3(NMEA 2000, 선박 전자 장비를 CAN으로 잇는 표준)의 항법 메시지를 써야 한다. 권장(최소) 메시지는 네 가지다.

| 메시지 | 담는 내용 |
|---|---|
| GNSS position data | 위도·경도·고도를 포함한 위치 전체 |
| Position delta, high precision rapid update | 기준 시점 이후 위치 변화를 짧은 주기로 |
| COG & SOG, rapid update | 대지 기준 진행 방향(COG)과 대지 속도(SOG) |
| GNSS pseudo-range noise statistics | 위치 오차 통계 |

여러 프레임이 필요한 메시지는 ISO 11783-3의 TP(Transport Protocol, 8바이트보다 긴 데이터를 나눠 보내는 규칙)가 아니라 <strong>NMEA fast packet</strong> 프로토콜을 써야 한다. fast packet은 NMEA 2000의 다중 프레임 방식으로, 연결을 맺거나 공지 메시지를 먼저 보내지 않고 같은 PGN의 프레임을 순서 번호를 붙여 연달아 보낸다.

::: warning 구현 함정: 항법 메시지는 TP로 오지 않는다
ISOBUS 스택의 TP·ETP(Extended TP, 더 긴 데이터를 위한 확장 TP) 재조립기([15장](/study/isobus/15-tp-bam-cmdt), [17장](/study/isobus/17-etp))는 fast packet을 풀지 못한다. GNSS position data처럼 긴 메시지를 받으려면 fast packet 디코더가 따로 있어야 한다. 각 메시지의 PGN과 필드 정의는 IEC 61162-3에 있고, 이 스터디가 근거로 삼은 ISO 11783 원문 묶음에는 없다. 트랙터가 항법 정보를 제공하면 TECU 클래스에 'N'을 붙인다([22장](/study/isobus/22-tractor-ecu)).
:::

항법 메시지가 알리는 위치가 트랙터의 어느 점인지는 9절에서 본다.

<small>근거: ISO 11783-7:2015 B.5; ISO 11783-9:2012 4.4.2.5</small>

## 8. 보내는 쪽이 지킬 값 규칙 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

2절은 받는 쪽에서 무효값을 가려내는 법을 봤다. 이 절은 보내는 쪽이 언제 오류값을 넣고, 예약 비트를 무엇으로 채우고, 값을 얼마나 신선하게 보내야 하는지 정리한다.

오류 지시값을 쓰는 규칙은 세 줄이다.

1. CF 고장으로 유효 데이터를 보낼 수 없으면, 그 파라미터 자리에 오류 지시값을 넣어야 한다.
2. 측정·계산 값이 유효하지만 정의된 범위를 넘으면 오류 지시값을 쓰면 안 된다. 최솟값이나 최댓값으로 잘라서 보낸다. 예를 들어 히치 위치가 계산상 101 %로 나오면 0xFE가 아니라 최댓값 0xFA(100 %)를 보낸다.
3. 센서가 값이 유효한지 판단할 수 없으면 오류 지시값을 보낸다.

예약 비트는 향후 호환을 위해 원칙적으로 모두 1(Not Available)로 채운다. 예외는 기능 지원 여부를 1비트씩 나열하는 Part 7 고유의 메시지다. 이런 메시지는 예약 자리를 0("지원 안 함")으로 두는 것이 기본값일 수 있으므로 메시지 정의를 따로 확인해야 한다. 대표 예가 [24장](/study/isobus/24-hitch-pto-valve-control)에서 볼 Tractor facility response다.

정의되지 않은 바이트는 나중에 새 파라미터로 바뀔 수 있다. 실제로 Amd1이 보조 밸브 추정 유량·명령, Language command, 범용 밸브 추정 유량, 가이던스 기계 상태 메시지의 예약 자리를 새 파라미터로 채웠다. 그러니 수신 측이 예약 바이트가 0xFF가 아니라는 이유로 프레임을 버리면, 신판 송신기와 붙였을 때 정상 메시지를 잃게 된다(추론).

신호의 물리적 취득부터 송신까지 걸리는 시간은 그 데이터 반복 주기의 2배를 넘지 않는 것이 권고된다. 100 ms 주기 메시지라면 실려 가는 값이 200 ms보다 오래되지 않아야 한다는 뜻이다. SIL(Software-in-the-Loop, 실제 장비 대신 소프트웨어 모델로 시험하는 방식) 환경에서 센서 값을 재생하는 에뮬레이터도 같은 지연 예산을 잡으면 된다.

<small>근거: ISO 11783-7:2015 3.2, 3.3.3, 3.3.4; ISO 11783-7:2015/Amd.1:2018</small>

## 9. 작업기 구성 오프셋과 기준점 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 핵심 정리로 가도 된다.
:::

작업기가 위치에 맞춰 일하려면 GNSS 안테나가 트랙터의 어디에 있고, 작업기의 붐이 연결점에서 몇 m 떨어져 있는지 알아야 한다. Part 7은 이 문제를 한 문단으로만 다룬다. 트랙터·작업기의 연결 구성과 기준점 사이 오프셋은 항법 파라미터와 프로세스 데이터의 작업기 구성에 쓰이며, 자세한 것은 ISO 11783-10(TC와 작업 데이터 교환을 정하는 표준 문서)을 보라는 내용이다. Part 10은 기준점을 네 가지로 정의한다.

| 기준점 | 정의 |
|---|---|
| DRP(DeviceReferencePoint) | 장치 좌표계의 원점(0,0,0). 트랙터는 뒤 차축 중심, 바퀴 달린 작업기는 앞 차축 중심이고, 그 밖에는 자유롭게 정한다 |
| CRP(ConnectorReferencePoint) | 연결 장치(전·후방 3점 히치, 드로바 등)의 위치. 3점 히치는 하부 링크 연결점의 중심이다 |
| NRP(NavigationReferencePoint) | 항법 장치(타입이 Navigation인 DeviceElement)의 위치 |
| ERP(DeviceElementReferencePoint) | 장치 요소 하나(또는 묶음)의 중심. 예: 붐 중심 |

![위에서 본 트랙터와 바퀴 달린 작업기: 트랙터 DRP는 뒤 차축 중심, NRP는 항법 안테나, CRP는 후방 히치 하부 링크 중심, 작업기 DRP는 앞 차축 중심, ERP는 붐 중심이고 x축은 주행 방향, y축은 오른쪽](/images/study-isobus/23-p7-reference-points-light.png)
![위에서 본 트랙터와 바퀴 달린 작업기: 트랙터 DRP는 뒤 차축 중심, NRP는 항법 안테나, CRP는 후방 히치 하부 링크 중심, 작업기 DRP는 앞 차축 중심, ERP는 붐 중심이고 x축은 주행 방향, y축은 오른쪽](/images/study-isobus/23-p7-reference-points-dark.png)

좌표계는 오른손 좌표계로, x축은 정상 주행 방향, y축은 주행 방향 기준 오른쪽, z축은 지면을 향한 아래쪽이 양수다. 오프셋은 ISO 11783-11 데이터 사전의 DDI(Data Dictionary Identifier, 데이터 항목 번호)로 정의된 값을 DeviceProperty나 DeviceProcessData로 TC에 알린다. DeviceElement는 작업기 안의 부품 하나(붐, 구획 등)를 나타내는 항목이다. DeviceProperty에 담은 값은 장치 설명을 다시 올려야 바뀌고, DeviceProcessData로 알린 값은 TC와 연결된 중에도 바꿀 수 있다. 조향 차축처럼 기하가 바뀌는 장치는 새 DRP·CRP를 직접 계산해 동적 데이터로 보내야 한다.

Part 7 쪽 규칙도 하나 있다. 항법 메시지가 보고하는 위치는 NRP 기준이다. GNSS 수신기만 있으면 NRP가 안테나 위치일 수 있고, roll·pitch(좌우·앞뒤 기울기) 보정을 했다면 그 아래 지면에 투영한 점일 수도 있다. DDOP(작업기가 자기 구성을 TC에 알리는 장치 설명 데이터)에 오프셋을 적는 방법은 [48장 DDOP 기초](/study/isobus/48-ddop-basics)와 [49장 DDOP 바이트 구성](/study/isobus/49-ddop-bytes)의 붐 살포기 예시에서 다룬다.

<small>근거: ISO 11783-7:2015 3.4, A.18; ISO 11783-10:2015 8.7</small>

::: details 원문을 가진 독자를 위한 메모
- 원문 구성: Annex A(규범)는 파라미터마다 길이·분해능·오프셋·범위와 SPN을 정하고, Annex B(규범)는 그 파라미터를 담는 PGN과 바이트 배치를 정한다. Annex C와 D는 참고(informative)다.
- 이 장의 표·그림과 원문 번호: 무효값 구역 표는 Part 7 Table 1, 2비트 상태값 표는 Table 2(measured)와 Table 3(command), 지역 시 오프셋 해석 표는 Table A.1, 바이트 경계 그림은 Figure 1 a), 기준점 정의는 Part 10 8.7과 Figure 13에 해당한다. 코드 주석의 "Table 1", "Figure 1 a)", "A.9"도 같은 대상이다.
- 원문 Figure 1은 높은 번호 바이트를 왼쪽에 그리고 'Big Endian'이라는 라벨을 달았는데, 이것은 그림을 그린 방향이다. 비트를 채우는 규칙은 본문 그대로 하위 비트가 낮은 바이트로 가는 방식이다.
- 8절의 "Amd1이 예약 자리를 채운 메시지"는 B.11·B.13·B.21·B.25.2·B.26.2다.
- Request의 정의는 ISO 11783-3:2018 5.4.3, 'N'·'P' 클래스 표기는 ISO 11783-9:2012 4.4.2.5와 4.4.2.8이다.
- 메시지와 원문 절 대조표:

| 묶음 | 메시지(Annex B 절) | 주로 보내는 쪽 |
|---|---|---|
| 시간·위치 | Time/Date(B.1), 항법 위치(B.5) | TECU, GNSS 수신기 |
| 속도·거리 | Ground-based·Wheel-based speed and distance(B.2·B.3), Machine selected speed(B.28.1) | TECU |
| 히치·PTO | 상태(B.6~B.9), 명령(B.10) | 상태는 트랙터, 명령은 작업기 |
| 유압 밸브 | 보조 밸브(B.11~B.17), 범용 밸브(B.25) | 상태는 밸브 쪽, 명령은 작업기 |
| 트랙터 제어 | 기능 확인(B.24.3·B.24.4), 가이던스(B.26), 속도 명령(B.28.2), 구동 전략(B.31·B.32) | 양방향 |
| 시스템 설정 | Language command(B.21), 가변 반복 주기(B.22) | VT·TECU·TC, 메시지 사용자 |
| 안전 | 작업기 작동 상태(B.29), 전체 작업기 정지(B.30), Heartbeat(B.33), 운전자 상태(Amd1) | TECU, 정지 스위치 CF, 모든 CF |

전원 유지는 B.4, 조명은 B.18~B.20, Working set 메시지는 B.23, 적합성 인증 메시지는 B.27이다.
:::

::: tip 핵심 정리
- Part 7은 트랙터와 작업기가 주고받는 메시지의 PGN, 주기, 바이트·비트 배치, 값의 뜻을 정한다.
- 명령은 부탁이다. 결과는 짝이 되는 측정값 메시지로 확인한다.
- 읽는 순서는 넷이다. 리틀 엔디언으로 묶고, 최상위 바이트가 `0xFA` 이하인지 보고, 분해능을 곱하고 오프셋을 더한 뒤, 상태 비트를 꺼낸다.
- `FE` 계열은 오류, `FF` 계열은 값 없음이다. 2비트 필드의 11은 측정값에서 "기능 없음", 명령에서 "그대로 두라"다.
- 속도는 Ground-based, Wheel-based, Machine selected 세 가지로 오고, Time/Date는 요청해야 받으며, 항법 위치는 NMEA 2000 메시지가 fast packet으로 온다.
:::

::: details 확인 문제
1. (개념) 작업기가 후방 히치를 64 %로 올리라는 명령을 보냈다. 히치가 실제로 64 %가 됐는지는 어떻게 알 수 있나?
2. (개념) 1바이트 파라미터의 원시값이 `0xFA`, `0xFE`, `0xFF`일 때 각각 무슨 뜻인가? 2바이트 파라미터라면 `FF FE`는 어떻게 읽나?
3. (계산) Ground-based speed and distance의 Bytes 1,2가 `10 0E`다. 속도는 몇 m/s이고 몇 km/h인가? 상위 바이트만으로 어림하면 얼마인가?
4. (디코딩) Wheel-based speed and distance의 Byte 8이 `0x44`다. 네 2비트 필드를 풀고, 운전자에게는 어느 쪽으로 움직이는 것처럼 느껴지는지 말하라.
5. (디코딩) Time/Date 응답의 Byte 8이 `0xFA`라면 Bytes 1~6을 어떻게 해석해야 하나? Byte 8이 `0x7D`라면?

**답 가이드**
1. 명령만으로는 알 수 없다. 명령은 부탁이라서 트랙터가 운전자 조작과 운전 조건을 따져 실행 여부를 정한다. 짝이 되는 측정값 메시지인 후방 히치 상태 메시지의 위치(Byte 1)와 limit status를 읽어 확인한다(24장).
2. `0xFA`(=250)는 유효값의 최댓값이다. `0xFE`는 오류 지시, `0xFF`는 사용 불가·미설치(값 없음)다. 2바이트 `FF FE`는 리틀 엔디언으로 묶으면 `0xFEFF`이고 최상위 바이트가 `FE`라서 오류 지시다.
3. `0x0E10` = 3600 → 3600 × 0.001 = 3.600 m/s = 12.96 km/h다. 상위 바이트 `0E`(=14)만 보면 14 × 0.256 = 3.584 m/s로 어림된다.
4. `0x44` = 01 00 01 00이다. bits 8,7 = 01은 운전석 반전(Reversed), bits 6,5 = 00은 Stop(작업기 작동 정지), bits 4,3 = 01은 키 ON(not Off), bits 2,1 = 00은 Reverse(후진)다. 방향은 섀시 기준이라 차체는 후진 중이지만, 운전석이 뒤로 돌아가 있으므로 운전자에게는 앞으로 가는 것처럼 느껴진다.
5. `0xFA`(물리값 125)면 Bytes 1~6이 UTC가 아닌 지역 시각·날짜이고 지역 오프셋은 제공되지 않는다. `0x7D`(=125, 물리값 0)는 −23~23 구역이므로 Bytes 1~6은 UTC이고 지역 시 오프셋은 0시간이다. 이때 지역 분 오프셋(Byte 7)도 함께 더해 지역 시각을 구한다.
:::

## 다음 챕터

- 다음: [24장 트랙터-작업기 메시지 (2): 히치·PTO·밸브와 작업기의 트랙터 제어](/study/isobus/24-hitch-pto-valve-control)
