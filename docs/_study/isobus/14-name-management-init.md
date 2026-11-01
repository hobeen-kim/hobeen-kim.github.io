---
title: "NAME 관리와 네트워크 초기화"
description: "실행 중에 NAME의 필드를 바꾸는 NAME management의 순서와 메시지, 주소 위반 감지, 전원을 켠 CF가 주소를 얻기까지의 초기화 순서와 상태를 익힌다."
date: 2026-04-13
tags: [ISOBUS, J1939, CAN, NAME, 네트워크 관리]
prev: /study/isobus/13-j1939-address-claim
next: /study/isobus/15-tp-bam-cmdt
---

# NAME 관리와 네트워크 초기화

::: info 학습 목표
- NAME management가 무엇을 바꾸는 기능이고 언제 쓰는지 설명할 수 있다.
- Set Pending, ACK, Adopt, 재클레임으로 이어지는 NAME 변경 순서를 말할 수 있다.
- 주소 위반을 감지한 CF가 하는 두 가지 일과 그때 켜는 고장 코드를 설명할 수 있다.
- 전원을 켠 CF가 주소를 얻기까지 거치는 단계와 상태를 설명할 수 있다.
- (심화) NM 메시지 8바이트를 조립하고 읽을 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [12장 주소와 NAME](/study/isobus/12-j1939-address-name), [13장 주소 클레임](/study/isobus/13-j1939-address-claim)
- 이 장에서 처음 나오는 말
  - NAME management(NM): 실행 중인 CF의 NAME 필드를 바꾸는 방법. PGN 37632 메시지 하나로 한다.
  - current NAME과 pending NAME: 지금 쓰고 있는 NAME과, 바꾸려고 임시로 맡겨 둔 새 NAME.
  - commanding CF와 target CF: NAME 변경을 명령하는 쪽과 NAME이 바뀌는 쪽.
  - qualifier flag: NM 메시지에서 필드마다 "이 필드를 바꿀지" 같은 표시를 하는 비트.
  - 주소 위반(address violation): 두 CF가 같은 소스 주소를 쓰고 있는 상태.
  - DTC(Diagnostic Trouble Code, 진단 고장 코드): 어디에 어떤 고장이 났는지 알리는 번호. [28장](/study/isobus/28-diagnostics-dm-fmi)에서 자세히 본다.
:::

같은 모델의 파종기 두 대를 산 농가를 생각해 보자. 두 대가 공장 설정 그대로라면 NAME의 device class instance(같은 종류 장치 가운데 몇 번째인지)가 둘 다 0일 것이다. 둘째 기계를 "파종기 2"로 바꿔 줘야 시스템이 두 대를 첫째와 둘째로 나눠 다룰 수 있다. NAME management는 명함의 소속 칸을 고쳐 새로 찍어 주는 절차다. 이 장의 뒷부분은 주소가 겹쳤을 때의 경보와, 전원을 켠 순간부터 주소를 얻을 때까지 CF가 거치는 단계를 정리한다.

## 1. NAME management란

이 절은 NAME management가 무엇을 바꾸고, 누가 무엇을 주고받는지 큰 그림을 본다.

[13장](/study/isobus/13-j1939-address-claim)까지는 NAME이 고정되고 주소만 바뀌는 세계였다. <strong>NAME management(NM)</strong>는 반대로 실행 중에 NAME의 필드를 바꾸는 방법이다. 같은 모델의 파종기 컨트롤러 두 대를 연결해 놓고 둘째를 "파종기 2"로 만들고 싶을 때처럼, 주로 instance 필드를 설치 현장에서 정하는 데 쓴다.

명함을 고칠 때 바로 새 명함을 쓰지 않고, 먼저 시안을 받아 두었다가 "이제 새 명함을 쓰세요"라는 말을 들은 뒤에 바꾼다고 생각하면 된다. NM도 새 NAME을 먼저 맡겨 두고(pending NAME), 채택 명령을 받은 뒤에야 실제로 쓴다(current NAME).

![대상 CF 안의 두 NAME: 서비스 툴이 Set Pending으로 바꿀 필드를 보내면 pending NAME에 적히고 ACK로 답한다. Adopt가 오면 pending NAME이 current NAME이 되고, 새 NAME으로 Address Claimed를 보낸다](/images/study-isobus/14-nm-pending-current-light.png)
![대상 CF 안의 두 NAME: 서비스 툴이 Set Pending으로 바꿀 필드를 보내면 pending NAME에 적히고 ACK로 답한다. Adopt가 오면 pending NAME이 current NAME이 되고, 새 NAME으로 Address Claimed를 보낸다](/images/study-isobus/14-nm-pending-current-dark.png)

그림은 대상 CF 안에 NAME이 두 벌 있는 모습이다. 번호 순서로 읽는다.

1. 서비스 툴이 Set Pending으로 바꿀 필드(여기서는 device class instance를 1로)를 보낸다. 대상 CF는 이 값을 pending NAME에 적는다.
2. 대상 CF가 ACK로 "맡았다"고 답한다. 이때도 송신에는 current NAME을 쓴다.
3. 서비스 툴이 Adopt를 보내면 pending NAME이 current NAME이 된다.
4. 대상 CF가 새 current NAME으로 Address Claimed를 보내 주소 클레임을 다시 한다.

### current NAME과 pending NAME

| 용어 | 뜻 |
|---|---|
| current NAME | CF가 지금 Address Claimed로 내보내는 NAME |
| pending NAME | 자격 있는 발신자의 NM 메시지를 받아 임시로 보관한 NAME. 채택 명령이 오기 전에는 효력이 없다 |
| commanding CF | NM 명령을 보내는 쪽(서비스 툴, NIU 등) |
| target CF | NAME이 바뀌는 쪽 |

서비스 툴은 정비 기사가 쓰는 진단 장비이고, NIU(Network Interconnect Unit)는 네트워크와 네트워크를 잇는 장치다([21장](/study/isobus/21-niu-network-layer)).

용도는 네 가지다.

1. instance 필드 설정. 주 용도다.
2. 범용 ECU의 function 변경.
3. 다른 방법으로 CF를 유일하게 식별할 수 없을 때.
4. 수동 설정 단계나 Commanded Address와 함께 하는 네트워크 구성.

identity number를 뺀 모든 필드를 바꿀 수 있다.

지원 여부와 범위는 제조사 몫이다. NM 지원 자체가 선택(optional)이다. 지원하더라도 서비스 툴·NIU 외의 발신자를 거부하거나, 독자 보안 검증을 요구하거나, 바꿀 수 있는 필드를 instance 필드 등으로 제한할 수 있다. 다만 지원한다면 <strong>최소한 ECU instance와 function instance의 변경은 허용</strong>해야 한다. 명령은 SA를 향해 가므로, commanding CF는 명령 전에 대상 CF들의 SA를 정확히 파악해야 한다.

<small>근거: ISO 11783-5:2019 3.1, 3.2, 3.3, 4.4.3.1, 4.4.3.4.1, 4.4.3.4.5</small>

## 2. NM 메시지와 모드 아홉 가지

이 절은 NM이 쓰는 메시지 하나와, 그 메시지가 맡는 아홉 가지 역할(모드)을 본다.

NM은 메시지 하나, PGN 37632(`0x9300`)로 모든 일을 한다. 데이터 Byte 3의 아래쪽 4비트에 적는 모드 번호(NM Control Mode Indicator)가 그 메시지의 역할을 정한다. 같은 양식의 서류에 "신청", "접수 확인", "반려" 도장을 찍어 용도를 나누는 것과 비슷하다. 바이트 배치 전체는 4절(심화)에서 본다.

### 모드 9종 (Byte 3 하위 4비트)

표 읽는 법: "보내는 쪽" 열의 commanding은 명령하는 쪽, target은 NAME이 바뀌는 쪽이다. "유효 필드"는 그 모드에서 뜻이 있는 칸이고, commanded 필드는 NM 메시지에 실어 보내는 NAME 필드 값이다.

| 모드 | 이름 | 보내는 쪽 | 유효 필드 | 요점 |
|---|---|---|---|---|
| 0 | Set Pending NAME | commanding | 전부 | flag가 0인 필드를 commanded 값으로 바꿔 pending NAME을 만든다. Byte 1에 target의 원래 NAME checksum |
| 1 | Pending NAME | target | commanded 필드 | pending NAME 조회에 대한 응답. pending NAME이 없거나 무효면 대신 Mode 4 |
| 2 | Current NAME | target | commanded 필드 | current NAME 조회에 대한 응답 |
| 3 | NAME ACK | target | commanded 필드 | 가장 최근 Set Pending을 수행했다는 응답. pending NAME을 싣는다 |
| 4 | NAME NACK | target | mode, error code, qualifier flag | 가장 최근 Set Pending 또는 Request Pending이 실패 |
| 5 | Request Pending NAME | commanding | mode만 | pending NAME을 보내 달라 |
| 6 | Request Current NAME | commanding | mode만 | current NAME을 보내 달라 |
| 7 | Adopt Pending NAME | commanding | mode만 | pending NAME을 current로 채택하고 그 NAME으로 주소 클레임을 다시 시작하라는 트리거. Global로 보내면 pending NAME을 가진 모든 CF가 대상 |
| 8 | Request NAME Address Claim | commanding | commanded 필드, qualifier flag | SA를 모르는 CF를 NAME 일부로 찾는다. Global 전용 |
| 9~15 | 예약 | - | - | - |

쓰지 않는 필드는 전부 1로 채운다. 그래서 Mode 1~3 응답의 Byte 1·2(checksum, qualifier flag 자리)는 `FF FF`다.

역할로 묶으면 단순하다. 명령하는 쪽은 0(바꿀 내용 맡기기), 5·6(맡긴 NAME이나 쓰는 NAME 묻기), 7(맡긴 NAME 채택하기), 8(NAME 일부로 CF 찾기)을 보낸다. 대상 쪽은 1·2(물음에 대한 답), 3(맡기기 성공), 4(실패)로 답한다.

<small>근거: ISO 11783-5:2019 4.4.3.2, 4.4.3.3.3.2~4.4.3.3.3.11</small>

## 3. NAME을 바꾸는 순서: 지원 확인부터 새 NAME 클레임까지

이 절은 서비스 툴이 대상 CF의 NAME을 바꾸는 전체 순서를 본다.

![NAME management 절차: 서비스 툴이 Request로 지원을 확인하고, Set Pending과 ACK를 주고받은 뒤, Adopt를 Global로 보내면 대상 CF가 새 NAME으로 Address Claimed를 보내고 250 ms 뒤 송신을 재개한다](/images/study-isobus/10-nm-sequence-light.png)
![NAME management 절차: 서비스 툴이 Request로 지원을 확인하고, Set Pending과 ACK를 주고받은 뒤, Adopt를 Global로 보내면 대상 CF가 새 NAME으로 Address Claimed를 보내고 250 ms 뒤 송신을 재개한다](/images/study-isobus/10-nm-sequence-dark.png)

그림 읽는 법: 세로 점선이 각 장치이고, 위에서 아래로 시간이 흐른다. 번호가 붙은 화살표가 메시지이며, 점선 화살표는 서비스 툴의 물음과 명령에 대한 대상 CF의 응답이다.

1. <strong>지원 확인</strong>: commanding CF는 NM 메시지(PGN 37632)에 대한 Request PGN을 target에게 보낼 수 있다. 지원하지 않는 CF는 [10장](/study/isobus/10-j1939-request-ack)에서 본 Acknowledgement(PGN 59392)의 NACK(부정 응답)으로 답한다. 지원하는 CF는 NM 메시지로 답하는데, 유효한 pending NAME이 있으면 Mode 1(Pending NAME), 없으면 Mode 2(Current NAME)로 Byte 3~8에 그 NAME을 싣는다. 지원 여부와 현재 NAME을 한 번에 알아내는 방법이다.
2. <strong>Set Pending</strong>: Mode 0을 target의 SA로 보낸다. target은 바꾸라고 표시된 필드마다 그 동작을 실제로 할 수 있는지 확인한 뒤에만 받아들여야 한다. 받아들이면 바뀐 필드와 그대로인 필드를 합쳐 pending NAME을 만들고, Mode 3(ACK)에 pending NAME을 실어 commanding CF의 SA로 보낸다. 이때 발신 주소는 마지막으로 클레임에 성공한 자기 current SA다. 거부하면 Mode 4(NACK)에 error code를 싣는다.
3. <strong>pending 상태</strong>: ACK를 보낸 뒤에도 target은 current NAME으로 계속 송신할 수 있다. pending NAME은 채택 명령이 오기 전에는 효력이 없다.
4. <strong>Adopt</strong>: commanding CF가 필요한 Set Pending을 모두 마친 뒤 Mode 7을 보낸다. target은 pending NAME을 채택하고 필요한 "reset"을 하는데, 새 NAME으로 Address Claimed를 보내는 일이 여기에 들어간다. Mode 7은 Global로 보낼 수 있으므로 여러 CF를 하나씩 설정해 두었다가 한 번에 활성화할 수 있다.
5. <strong>재클레임</strong>: target은 새 NAME으로 주소 클레임에 성공한 뒤에야 송신을 시작·재개한다. 일반 클레임처럼 250 ms 규칙이 적용된다.

맡기기(Set Pending)와 채택(Adopt)을 두 단계로 나눈 덕분에, 여러 CF의 NAME을 하나씩 준비해 두었다가 4단계의 Global Adopt 한 번으로 함께 바꿀 수 있다.

target 쪽 검증 규칙이 하나 더 있다. Set Pending은 아무 CF에게서나 받아들여도 되지만, <strong>Adopt를 보낸 CF가 자기가 마지막으로 받아들인 Set Pending을 보낸 CF와 같은지</strong>는 확인해야 한다. 4절에서 볼 error code 0의 정의가 바로 이 경우다.

<small>근거: ISO 11783-5:2019 4.4.3.4.1~4.4.3.4.5, 4.5.2</small>

## 4. NM 메시지의 바이트 배치 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

### 메시지 형식: PGN 37632(0x9300)

| 항목 | 값 |
|---|---|
| PGN | 37632 (`0x009300`) |
| PF | 147 (`0x93`). PDU1이라 PS가 목적지 주소다 |
| 데이터 길이 | 8바이트 |
| 기본 우선순위 | 6 → CAN ID가 `0x1893`으로 시작 |
| 송신 주기 | 필요할 때 |
| 예약·미사용 비트 | 모두 1 |

PDU1은 PF가 240보다 작아 PS 칸을 목적지 주소로 쓰는 형식이다([9장](/study/isobus/09-j1939-message)). PS(목적지)는 모드에 따라 정해진다.

| 모드 | PS(DA) |
|---|---|
| 0 | target CF의 SA |
| 1~4 (target이 보내는 응답) | commanding CF의 SA |
| 5~7 | target CF의 SA 또는 Global(`0xFF`) |
| 8 | Global(`0xFF`) |

데이터 8바이트는 NAME과 거의 같은 자리를 쓴다. 아래 그림처럼 Byte 8~4는 NAME과 비트 자리가 똑같은 commanded 필드이고, identity number가 있던 Byte 3 하위 5비트·Byte 2·Byte 1 자리에 제어 정보가 들어간다. identity number를 실을 자리가 아예 없으니 NM으로 바꿀 수 없다는 규칙과도 맞아떨어진다.

![NAME(Address Claimed 데이터)과 NM 메시지(PGN 37632)의 바이트 비교: Byte 8~4는 같은 비트 자리, Byte 3 하위 5비트는 Reserved와 Mode, Byte 2는 qualifier flags, Byte 1은 checksum 또는 error code](/images/study-isobus/10-nm-byte-layout-light.png)
![NAME(Address Claimed 데이터)과 NM 메시지(PGN 37632)의 바이트 비교: Byte 8~4는 같은 비트 자리, Byte 3 하위 5비트는 Reserved와 Mode, Byte 2는 qualifier flags, Byte 1은 checksum 또는 error code](/images/study-isobus/10-nm-byte-layout-dark.png)

그림 읽는 법: 위 줄이 Address Claimed에 싣는 NAME, 아래 줄이 NM 메시지다. 칸마다 필드 약어와 비트 수를 적었다(MC는 manufacturer code, ID는 identity number). 위아래 화살표로 이어진 Byte 8~4는 두 메시지에서 같은 비트 자리다. 아래 표의 bit 8은 그 바이트의 최상위 비트, bit 1은 최하위 비트다.

| 위치 | 내용 | 쓰는 모드 |
|---|---|---|
| Byte 8~4 | commanded self-configurable address·industry group·device class instance·device class·function·function instance·ECU instance·manufacturer code 상위 8비트 | 0, 1, 2, 3, 8 |
| Byte 7 bit 1 | Reserved. NM 메시지에서는 1 | - |
| Byte 3 bit 8~6 | commanded manufacturer code 하위 3비트 | 0, 1, 2, 3, 8 |
| Byte 3 bit 5 | Reserved (1) | - |
| Byte 3 bit 4~1 | NM Control Mode Indicator (0~15) | 전 모드 |
| Byte 2 | qualifier flag 8개: bit 8 self-configurable address, 7 industry group, 6 device class instance, 5 device class, 4 function, 3 function instance, 2 ECU instance, 1 manufacturer code | 0, 4, 8 |
| Byte 1 | Mode 0에서는 NAME checksum, Mode 4에서는 error code | 0, 4 |

::: warning Reserved 비트가 NAME과 반대다
NAME의 Reserved(Byte 7 bit 1)는 0이어야 하지만, NM 메시지에서는 같은 자리가 "예약·미사용 비트는 모두 1"이라는 규칙을 따른다. 그래서 같은 NAME을 실어도 Address Claimed에서는 Byte 7이 `08`, NM 메시지에서는 `09`가 된다. NM 메시지의 Byte 3~8을 그대로 복사해 NAME을 만들면 Reserved가 1인 잘못된 NAME이 생긴다. NM → NAME으로 바꿀 때는 Reserved를 0으로 되돌리고, Byte 3 하위 5비트를 자기 identity number로 다시 채워야 한다.
:::

### qualifier flag, checksum, error code

<strong>qualifier flag</strong>(Byte 2의 비트 8개)는 모드마다 뜻이 다르다.

| 모드 | flag = 0 | flag = 1 |
|---|---|---|
| 0 Set Pending | 그 필드를 commanded 값으로 바꾼다 | 바꾸지 않는다. commanding CF는 해당 commanded 필드를 모두 1로 채운다 |
| 4 NACK (error 1·2) | 그 필드는 오류 원인이 아니다 | 그 필드가 오류를 일으켰다(바꿀 수 없다) |
| 4 NACK (그 밖의 error) | - | 모두 1 |
| 8 Request NAME Address Claim | 그 필드를 current NAME 매칭에 쓴다 | 매칭에서 뺀다. 해당 commanded 필드는 모두 1 |
| 그 밖의 모드 | - | 모두 1 |

표준이 이유를 적지는 않지만, flag가 따로 있는 것은 commanded 필드 값만으로는 "바꾸지 않음"을 나타낼 수 없기 때문으로 보인다. commanded industry group의 범위는 0~7이라 모두 1인 값 7도 정상 값이고, manufacturer code(0~2047)·function instance(0~31)·ECU instance(0~7)도 마찬가지다. 범위에서 모두 1인 값을 뺀 필드는 device class(0~126)와 function(0~254)뿐이다.

<strong>NAME checksum</strong>(Mode 0의 Byte 1)은 target CF의 <strong>원래 NAME 8바이트를 산술 합산해 하위 8비트만 남긴 값</strong>이다. 8바이트를 더한 합을 256으로 나눈 나머지와 같다. commanding CF가 NAME 변경을 시작한 뒤 주소 중재로 target의 SA가 다른 CF에게 넘어갈 수 있는데, 그 SA로 간 명령을 엉뚱한 CF가 받아들이지 않게 하는 안전장치다. 다만 8비트 합이라 서로 다른 NAME의 checksum이 우연히 같을 수 있어 완전한 보장은 아니다(추론). 그래서 표준은 명령 전에 대상 CF의 신원과 SA부터 검증하라고 요구한다.

<strong>error code</strong>(Mode 4의 Byte 1)는 다음과 같다.

| 코드 | 뜻 | qualifier flag |
|---|---|---|
| 0 | 보안 불충족. Adopt를 보낸 SA가 Set Pending을 보낸 SA와 다르다 | 모두 1 |
| 1 | 바꿀 수 없는 항목이 있다 | 원인 필드만 1 |
| 2 | 항목 충돌. 지정된 function을 수행할 수 없거나 self-configurable로 동작할 수 없는 등 | 원인 필드만 1 |
| 3 | checksum 불일치 | 모두 1 |
| 4 | pending NAME이 설정되지 않음 | 모두 1 |
| 5 | 기타 | 모두 1 |
| 6~254 | 예약 | - |
| 255 | 사용 불가(not available) | - |

<small>근거: ISO 11783-5:2019 4.3.2, 4.4.3.2, 4.4.3.3.1, 4.4.3.3.2, 4.4.3.3.4, 4.4.3.4.4, Table 3, Figure 3</small>

## 5. 바이트로 따라가기: 블루팜 컨트롤러를 "파종기 2"로 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

[13장](/study/isobus/13-j1939-address-claim) 시나리오의 CF B(블루팜 파종기 컨트롤러, SA 0x81, NAME_B = `0xA00882002803D090`)의 device class instance를 1로 바꿔 [12장](/study/isobus/12-j1939-address-name) NAME 조립 예 A.3의 "파종기 2"로 만든다. 서비스 툴의 SA는 0x9A(예시 값)다.

표 읽는 법: 방향 열의 "툴"은 서비스 툴(SA 0x9A), "B"는 CF B(SA 0x81)다. CAN ID `0x18939A81`은 우선순위 6(`18`), PF `93`(NM), 목적지 `9A`, 보낸 쪽 `81`로 끊어 읽는다. 데이터는 Byte 1부터 적었다.

| 단계 | 방향 | CAN ID | 데이터 | 해설 |
|---|---|---|---|---|
| 1 | 툴 → B | `0x18EA819A` | `00 93 00` | Request(DLC 3), 요청 PGN 37632 |
| 2 | B → 툴 | `0x18939A81` | `FF FF 12 28 00 82 09 A0` | Mode 2. pending이 없어 current NAME을 싣는다. Byte 3 `12` = MC 하위 3비트 `000` + Reserved 1 + Mode 2 |
| 3 | 툴 → B | `0x1893819A` | `B5 DF F0 FF FF FF FF F1` | Mode 0. checksum `B5`, flag `DF`(DCI만 0), Byte 8 `F1` = 바꾸지 않는 AAC·IG는 1로 채우고 DCI=1 |
| 4 | B → 툴 | `0x18939A81` | `FF FF 13 28 00 82 09 A1` | Mode 3 ACK. pending NAME의 Byte 8 = `A1` |
| 5 | 툴 → 전체 | `0x1893FF9A` | `FF FF F7 FF FF FF FF FF` | Mode 7 Adopt, Global |
| 6 | B → 전체 | `0x18EEFF81` | `90 D0 03 28 00 82 08 A1` | 새 NAME `0xA10882002803D090`으로 Address Claimed. 250 ms 뒤 송신 재개 |

checksum은 NAME_B의 8바이트 `A0 08 82 00 28 03 D0 90`을 더한 693(`0x2B5`)의 하위 8비트 `B5`다. 만약 2단계와 3단계 사이에 주소 중재가 일어나 SA 0x81을 그린텍 컨트롤러(NAME_A, checksum `1F`)가 차지했다면, 그 CF는 3단계 명령을 받아도 checksum이 맞지 않아 Mode 4, error code 3으로 거부한다. 그 응답 데이터는 `03 FF F4 FF FF FF FF FF`다.

3단계의 flag `DF`를 2진수로 쓰면 `1101 1111`이다. bit 6(device class instance)만 0이라 "device class instance만 바꾼다"는 뜻이 된다.

target이 device class 변경은 허용하지 않는 제품인데 Set Pending이 device class를 바꾸라고 했다면, NACK은 error code 1에 device class flag(bit 5)만 1로 세운 `01 10 F4 FF FF FF FF FF`가 된다. Byte 2 `10`은 2진수 `0001 0000`이라 bit 5만 1이다.

Mode 8은 SA를 모를 때 쓴다. 예를 들어 "function이 130이고 device class instance가 1인 CF는 Address Claimed를 보내라"는 요청은 CAN ID `0x1893FF9A`, 데이터 `FF D7 F8 FF FF 82 FF F1`이다. flag `D7`은 device class instance(bit 6)와 function(bit 4)만 0이다. 조건에 맞는 CF는 current NAME으로 Address Claimed를 보내고, 맞지 않는 CF는 Address Claimed도 NACK도 보내지 않는다.

다음 코드는 위 표의 NM 프레임 데이터를 필드 값에서 직접 만들어 하나씩 맞춰 본다.

::: details 파이썬으로 NM 프레임 검산
```python
def name_fields(name):
    out, shift = {}, 64
    for key, bits in [("aac", 1), ("ig", 3), ("dci", 4), ("dc", 7), ("rsvd", 1),
                      ("func", 8), ("fi", 5), ("ei", 3), ("mfg", 11), ("ident", 21)]:
        shift -= bits
        out[key] = (name >> shift) & ((1 << bits) - 1)
    return out


def nm_frame(mode, cmd=None, flags=0xFF, byte1=0xFF):
    """cmd에 없는 commanded 필드는 모두 1로 채운다(4.4.3.2)."""
    cmd = cmd or {}

    def f(key, bits):
        return cmd.get(key, (1 << bits) - 1)

    mfg = f("mfg", 11)
    return bytes([
        byte1,                                                 # Byte 1: checksum / error
        flags,                                                 # Byte 2: qualifier flag
        ((mfg & 0x7) << 5) | (1 << 4) | (mode & 0xF),          # Byte 3: MC 하위3 | R=1 | mode
        mfg >> 3,                                              # Byte 4: MC 상위 8
        (f("fi", 5) << 3) | f("ei", 3),                        # Byte 5
        f("func", 8),                                          # Byte 6
        (f("dc", 7) << 1) | 1,                                 # Byte 7: DC | R=1
        (f("aac", 1) << 7) | (f("ig", 3) << 4) | f("dci", 4),  # Byte 8
    ])


def hx(bs):
    return " ".join(f"{b:02X}" for b in bs)


NAME_B = 0xA00882002803D090
checksum = sum(NAME_B.to_bytes(8, "big")) & 0xFF
assert checksum == 0xB5

current = {k: v for k, v in name_fields(NAME_B).items() if k not in ("rsvd", "ident")}
pending = dict(current, dci=1)
DCI_ONLY = 0xFF & ~(1 << 5)            # bit 6(DCI)만 0 -> 0xDF

assert hx(nm_frame(2, current)) == "FF FF 12 28 00 82 09 A0"
assert hx(nm_frame(0, {"dci": 1}, DCI_ONLY, checksum)) == "B5 DF F0 FF FF FF FF F1"
assert hx(nm_frame(3, pending)) == "FF FF 13 28 00 82 09 A1"
assert hx(nm_frame(7)) == "FF FF F7 FF FF FF FF FF"
assert hx(nm_frame(4, flags=0x10, byte1=1)) == "01 10 F4 FF FF FF FF FF"
assert hx(nm_frame(4, byte1=3)) == "03 FF F4 FF FF FF FF FF"
assert hx(nm_frame(8, {"func": 130, "dci": 1}, 0xD7)) == "FF D7 F8 FF FF 82 FF F1"

NEW_NAME = NAME_B | (1 << 56)          # DCI 필드(bit 59~56)의 최하위 비트
assert hx(NEW_NAME.to_bytes(8, "little")) == "90 D0 03 28 00 82 08 A1"
print("모든 NM 프레임 검산 통과")
```
:::

`nm_frame()`은 Byte 1부터 Byte 8까지를 차례로 조립한다. 넘기지 않은 commanded 필드는 모두 1로 채우므로 Mode 7처럼 모드만 쓰는 메시지는 `FF FF F7 FF FF FF FF FF`가 된다. `assert`가 모두 통과하면 마지막 줄이 출력된다. `nm_frame(4, flags=0x10, byte1=1)`의 `0x10`이 위 문단의 device class flag(bit 5)다.

<small>근거: ISO 11783-5:2019 4.4.3.3.1, 4.4.3.3.3.10, 4.4.3.4, Table 3</small>

## 6. 주소 위반: 같은 주소를 두 CF가 쓸 때

이 절은 자기 주소를 다른 CF가 쓰고 있다는 것을 알아챘을 때 CF가 할 일을 본다.

<strong>네트워크 오류 관리</strong>는 주소와 관련된 특정 오류를 감지하는 일이다. ISO 11783-5(ISOBUS의 네트워크 관리 표준)가 CF에게 직접 요구하는 것은 두 가지다.

| 오류 | 정의 | CF가 할 일 |
|---|---|---|
| 주소 확보 실패 (unable to claim) | SA 클레임에 실패 | Cannot Claim Address를 보내고 [13장](/study/isobus/13-j1939-address-claim)의 "주소를 못 얻은 CF" 규칙대로 동작 |
| 주소 위반 (address violation) | 두 CF가 같은 SA를 쓰고 있음 | 아래 두 가지를 모두 한다 |

자기 SA를 소스로 쓰는 메시지를 받았는데 그것이 Address Claimed가 아니라면, 그 CF는

1. Global 주소로 Address Claimed를 보내야 하고,
2. <strong>SPN = 2000 + SA, FMI = 31</strong>인 진단 고장 코드(DTC)를 활성화해야 한다.

SPN(Suspect Parameter Number)은 [9장](/study/isobus/09-j1939-message)에서 본 값 번호로, 고장 코드에서는 "어디가 문제인가"를 가리킨다. FMI(Failure Mode Indicator)는 "어떤 식으로 문제인가"를 0~31의 번호로 나타낸다. 주소 위반의 SPN은 문제가 된 주소에 2000을 더한 값이다. 그래서 고장 코드만 보고도 어느 주소가 겹쳤는지 알 수 있다.

이 요구사항은 2판(ISO 11783-5:2011)에서 추가되었다. FMI 31은 ISO 11783-12(ISOBUS 진단을 정하는 표준 문서)의 "Condition exists"로, 적용할 다른 FMI가 없을 때 SPN이 가리키는 상황이 존재한다는 뜻이다. 중복 클레임이나 중복 NAME 같은 그 밖의 주소 오류는 진단 툴이 Request for Address Claimed로 찾아낸다.

표준이 이유를 적지는 않지만, 1번은 상대를 주소 중재로 끌어들이는 효과가 있어 보인다. 상대가 규정대로 구현된 CF라면 자기 SA를 클레임하는 Address Claimed를 보고 NAME을 비교해 진 쪽이 물러난다. 상대가 클레임 없이 주소를 박아 쓰는 장비라면 중재가 일어나지 않으므로, 2번의 DTC가 운전자와 서비스 툴에게 문제를 알리는 통로가 된다.

### 예: SA 0x81에서 주소 위반 감지 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

CF B(SA 0x81 = 129)가 소스 주소가 0x81인 일반 메시지를 받았다면 DTC의 SPN은 2000 + 129 = <strong>2129</strong>(`0x851`), FMI는 31이다. DM1(지금 켜져 있는 고장 코드를 알리는 진단 메시지)에서 DTC가 차지하는 4바이트(Byte 3~6)에 넣으면 다음과 같다(발생 횟수는 1로 가정).

| DM1 바이트 | 값 | 내용 |
|---|---|---|
| Byte 3 | `51` | SPN 하위 8비트 |
| Byte 4 | `08` | SPN 둘째 바이트 |
| Byte 5 | `1F` | SPN 상위 3비트 `000` + FMI `11111`(31) |
| Byte 6 | `01` | SPN 변환 방법 0 + 발생 횟수 1 |

표 읽는 법: SPN은 19비트라 낮은 자리부터 8비트, 8비트, 3비트로 나눠 Byte 3, Byte 4, Byte 5의 위쪽 3비트에 담는다. `0x851`의 낮은 8비트가 `51`, 그다음 8비트가 `08`, 남은 위쪽 3비트가 `000`이다. Byte 5의 아래쪽 5비트에는 FMI 31(`11111`)이 들어가 `000 11111` = `1F`가 된다.

DM1 메시지 전체의 구성과 송신 주기는 [28장](/study/isobus/28-diagnostics-dm-fmi)에서 다룬다.

::: warning 자기 프레임을 남의 프레임으로 오인하지 않기
표준은 CF가 다른 CF가 보낸 Address Claimed와 자기가 보낸 것을 구분해야 한다고 요구한다. 송신 프레임을 수신 큐로 되돌려 주는(에코) CAN 드라이버 설정에서 이 구분을 빠뜨리면, 자기 프레임을 보고 주소 위반이나 주소 경합으로 오판할 수 있다. 수신 경로에서 자기 송신 에코를 걸러 내는지 먼저 확인한다.
:::

<small>근거: ISO 11783-5:2019 4.4.2.3, 4.4.4.1~4.4.4.3, 4.5.2 c), 4.5.5, ISO 11783-12:2019 B.6, E.3.22</small>

## 7. 네트워크 초기화: 전원을 켠 뒤 주소를 얻기까지

[13장](/study/isobus/13-j1939-address-claim)은 초기화를 "조회 → 대기 → 클레임 → 250 ms"로 요약했다. 이 절은 전원을 켠 CF가 주소를 얻기까지의 상태 흐름을 먼저 그림으로 보고, 표준이 정한 두 가지 주소 획득 방식과 그 둘레의 규칙을 본다. 클레임 요구사항과 경합 유형별 해결 순서는 8절(심화)에서 본다.

![주소 획득 상태 흐름: 미시도에서 Request를 보내면 조회 대기, 250 ms + RTxD 뒤 Address Claimed를 보내면 클레임 중, 250 ms 무경합이면 정상. 경합에서 지면 self-configurable은 다른 주소로 다시 클레임 중, 그 밖은 주소 없음. 주소 없음은 Commanded Address 수락으로 클레임 중, 전원 재인가로 미시도로 돌아간다](/images/study-isobus/14-address-state-machine-light.png)
![주소 획득 상태 흐름: 미시도에서 Request를 보내면 조회 대기, 250 ms + RTxD 뒤 Address Claimed를 보내면 클레임 중, 250 ms 무경합이면 정상. 경합에서 지면 self-configurable은 다른 주소로 다시 클레임 중, 그 밖은 주소 없음. 주소 없음은 Commanded Address 수락으로 클레임 중, 전원 재인가로 미시도로 돌아간다](/images/study-isobus/14-address-state-machine-dark.png)

그림의 상자 다섯 개가 CF의 상태이고, 화살표 옆 글이 상태가 바뀌는 조건이다.

- 미시도: 전원을 막 켜서 아직 주소를 시도하지 않은 상태. Request for Address Claimed만 보낼 수 있다.
- 조회 대기: Request를 보내고 250 ms + RTxD를 기다리는 상태. 남의 Request에도 응답하지 않는다.
- 클레임 중: Address Claimed를 보내고 250 ms 동안 경합이 없는지 지켜보는 상태.
- 정상: 주소를 얻어 모든 메시지를 보낼 수 있는 상태.
- 주소 없음: 주소를 얻지 못하고 Cannot Claim을 보낸 상태.

상태 이름은 이 스터디가 붙인 것이다. 각 상태에서 보낼 수 있는 메시지의 전체 목록은 9절(심화)의 상태 표에 있다. 그림은 non-configurable CF만 쓰는 두 경로를 생략했다. 미시도에서 Request 없이 곧바로 클레임 중으로 가는 경로와, 정상에서 더 작은 NAME에 져서 곧바로 주소 없음으로 가는 경로다.

### 두 가지 주소 획득 방식

전원을 켠 뒤 다른 어떤 통신보다 먼저, CF는 네트워크에서 유일한 주소를 얻어야 한다. self-configurable CF는 다음 둘 중 하나를 쓴다.

| 방식 | 순서 | 특징 |
|---|---|---|
| a) 주소 표 만들기 | ① Request for Address Claimed를 Global로 보낸다 ② 최소 250 ms + RTxD 기다린다 ③ 그동안 받은 Address Claimed의 SA를 모두 저장한다 ④ 빈 주소를 클레임한다. initial address가 비어 있으면 그것을, 차 있으면 다른 빈 주소를 | 클레임한 모든 CF가 응답하므로 사용 중인 주소를 한 번에 파악한다 |
| b) 한 주소만 묻기 | ① initial address를 목적지로 Request를 보낸다 ② 최소 250 ms + RTxD 기다린다. 그 사이 initial address를 클레임하는 Address Claimed가 오면 새 initial address를 골라 ①로 돌아간다 ③ initial address를 클레임한다 | 그 주소를 가진 CF만 응답한다 |

a)는 회의실 전체에 "각자 자리 번호를 말해 주세요"라고 묻는 방식이고, b)는 "3번 자리에 누구 있나요?"라고 한 자리만 묻는 방식이다.

시퀀스를 둘러싼 규칙은 다음과 같다.

- 이 획득 시퀀스는 2판(2011)에서 추가되었다.
- 이 시퀀스는 두 CF가 같은 주소를 클레임할 위험을 줄일 뿐 없애지는 못한다. 유효한 주소만 쓰이도록 보장하는 것은 8절의 클레임 요구사항과 13장의 응답 규칙이다.
- 1판(2001)은 250 ms 대신 <strong>1.25 s</strong>를 기다리게 했다. 부팅 시간이 중요하지 않다면 250 ms보다 길게 기다리는 것이 좋은 관행으로 여겨진다.
- self-configurable이 아닌 CF는 Request를 생략해도 되지만, 다른 통신 전에 Address Claimed는 반드시 보내야 한다. 그래도 클레임 전에 항상 Request를 보내는 것이 권장된다.
- 클레임에 성공한 주소는 이후 모든 전원 인가의 initial address로 저장한다. preferred address를 배정받은 CF도 같다.

RTxD는 0~255 × 0.6 ms라 최대 153 ms다. 대기 시간은 CF마다 250~403 ms 사이로 흩어진다. 표준은 RTxD를 정의하면서, 난수의 씨앗(seed, 난수 생성기의 출발값)으로 NAME의 identity number 같은 CF 고유 정보를 쓸 수 있다고 덧붙인다. 같은 펌웨어를 실은 CF들이 전원을 동시에 받아도 RTxD가 갈리게 하려면 이 권고를 따르는 편이 낫다(해석).

### 세 가지 기본 흐름

![초기화 시퀀스 3종: a) 경합이 없으면 Request 후 250 ms + RTxD를 기다리고 Address Claimed를 보낸 뒤 250 ms가 지나면 일반 메시지를 보낸다, b) initial address X가 이미 쓰이면 새 주소 Q를 골라 클레임한다, c) non-configurable CF는 자기 주소가 쓰이는 것을 보고 RTxD 뒤 Cannot Claim을 보낸다](/images/study-isobus/10-init-sequence-light.png)
![초기화 시퀀스 3종: a) 경합이 없으면 Request 후 250 ms + RTxD를 기다리고 Address Claimed를 보낸 뒤 250 ms가 지나면 일반 메시지를 보낸다, b) initial address X가 이미 쓰이면 새 주소 Q를 골라 클레임한다, c) non-configurable CF는 자기 주소가 쓰이는 것을 보고 RTxD 뒤 Cannot Claim을 보낸다](/images/study-isobus/10-init-sequence-dark.png)

그림 읽는 법: 세 칸이 각각 한 가지 흐름이고, 위에서 아래로 시간이 흐른다. AC는 Address Claimed를 줄인 것이고, 왼쪽 주황 괄호가 기다리는 시간이다.

- a)는 경합이 없을 때다. Request 뒤 250 ms + RTxD를 기다리고 Address Claimed를 보낸 다음, 250 ms가 지나면 일반 메시지를 보낸다.
- b)는 initial address X를 다른 CF가 이미 쓰고 있을 때다. 대기 중에 받은 응답에서 X가 쓰이는 것을 보고 새 주소 Q를 골라 클레임한다.
- c)는 non-configurable CF가 주소를 얻지 못할 때다. CF는 다른 CF가 보낸 Request에 이어지는 응답들 속에서 자기 initial address X가 이미 클레임된 것을 본다. non-configurable이라 다른 주소를 고를 수 없으므로 RTxD 뒤 Cannot Claim(SA=254, 자기 NAME)을 보낸다.

<small>근거: ISO 11783-5:2019 3.4, 4.5.1, 4.5.4, 4.5.5</small>

## 8. 클레임 요구사항과 경합 해결 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

### 클레임 요구사항 4가지

1. 초기화할 때, 그리고 NAME이나 주소를 바꾸라는 명령에 응답할 때(Commanded Address 수락 확인 포함) 자기 주소를 클레임한다. 각 CF가 유효한 주소 확보를 스스로 책임지고, 자기 클레임을 다른 CF가 아직 못 받았을 때의 중재까지 하게 하려는 것이다.
2. Address Claimed의 목적지는 Global(255)이다. ISO 11783-3(메시지 형식과 요청·응답 규칙을 정하는 표준) 요구사항의 예외다([13장](/study/isobus/13-j1939-address-claim)).
3. 다른 CF가 보낸 Address Claimed와 자기가 보낸 것을 구분한다.
4. 주소 클레임에 성공한 뒤 250 ms가 지나기 전에는 송신을 시작·재개하지 않는다. Request for Address Claimed에 대한 응답만 예외다.

4번의 250 ms와 "250 ms 동안 경합 클레임이 없어야 성공"이라는 규칙(13장)은 표준의 시퀀스 그림에서 하나의 구간으로 그려진다. 7절 그림 a)의 둘째 괄호가 그 구간이다. Address Claimed를 보낸 시점부터 250 ms를 세고, 그 구간이 경합 없이 끝나면 곧바로 일반 메시지를 보낸다. [13장](/study/isobus/13-j1939-address-claim)의 타임라인이 332.2 ms 클레임 → 582.2 ms 송신 시작으로 계산한 것이 이 해석이다.

### 경합이 생기는 경우와 푸는 순서

두 self-configurable CF의 initial address가 같으면 초기화 중 세 경우가 생긴다. 표의 "그림"은 7절의 초기화 흐름 그림을 가리킨다.

| 경우 | 상황 | 해결 |
|---|---|---|
| a | 한쪽이 250 ms + RTxD를 먼저 마친다 | 경합 없이 풀린다. 늦은 쪽은 대기 중에 먼저 온 클레임을 보고 다른 주소를 고른다(그림의 b 흐름) |
| b | 동시에 마쳤지만 클레임 송신이 조금 어긋난다 | 주소 클레임 우선순위 판정(NAME 비교)으로 풀린다. 13장 4절의 시나리오가 이 경우다 |
| c | 동시에 마치고 클레임도 동시에 보낸다 | 네트워크 오류가 날 수 있다. 아래 "동일 식별자 충돌"의 절차로 푼다 |

경합 상대의 주소 구성 능력에 따라 해결 시퀀스도 달라진다.

| 조합 | 시퀀스 |
|---|---|
| self-configurable 2대 | 둘 다 SA=X를 클레임 → NAME이 작은 A는 SA=X로 다시 클레임하고 통신, B는 SA=Y를 클레임하고 250 ms 뒤 통신 |
| non-configurable A + self-configurable B | B가 SA=X를 먼저 클레임해 쓰고 있어도, 초기화를 마친 A가 SA=X를 클레임하면 B가 SA=Y로 옮긴다. A의 NAME이 언제나 작기 때문이다 |
| non-configurable 2대 | 늦게 들어온 B가 SA=X를 클레임했을 때 A의 NAME이 더 작으면 A가 다시 클레임하고 B가 RTxD 뒤 Cannot Claim을 보낸다. B의 NAME이 더 작으면 먼저 쓰던 A가 RTxD 뒤 Cannot Claim을 보내고 물러난다 |

### 동일 식별자 충돌

Request for Address Claimed, Address Claimed, Cannot Claim은 서로 다른 CF가 <strong>CAN ID가 똑같은 프레임</strong>을 만들 수 있는 메시지다.

- 두 CF가 NULL 주소로 동시에 보내는 Request는 데이터(`00 EE 00`)까지 같아서 문제가 없다. 비트가 끝까지 같으니 버스에는 한 프레임으로 보인다(해설).
- 같은 주소를 다투는 CF들이 Address Claimed를 동시에 보내면 ID는 같은데 데이터(NAME)가 달라서 네트워크 오류가 날 수 있다. CAN 중재(동시에 송신을 시작한 노드 가운데 ID 비트로 한 노드만 남기는 과정)는 ID에서 끝나므로, ID가 같으면 송신자가 갈리지 않은 채 데이터 필드까지 가기 때문이다([5장](/study/isobus/05-can-arbitration), [6장](/study/isobus/06-can-error)). NULL 주소에서 동시에 나가는 Cannot Claim도 같은 이유로 오류를 낼 수 있다.
- 데이터 링크 계층이 이런 오류를 감지·보고할 수 있다면, Address Claimed를 보낸 CF는 오류 정보를 지켜보다가 네트워크 오류가 나면 RTxD 뒤로 클레임 재송신을 미룬다. 표준은 동기화된 클레임이 거듭 충돌해 장치들이 Bus OFF(오류가 쌓인 노드가 스스로 버스에서 빠지는 상태, 6장)까지 가는 상황과, 그 뒤 RTxD로 재송신 시점이 갈려 A는 SA=X, B는 SA=Y를 얻는 흐름을 그림으로 보여 준다.
- Cannot Claim끼리 충돌한 경우에도 같은 절차를 쓴다.

이 절차를 구현하려면 CAN 컨트롤러의 송신 오류 정보(비트 오류 등)가 네트워크 관리 계층까지 올라와야 한다. 드라이버가 송신 실패를 자동 재전송만 하고 위로 알리지 않으면, 같은 ID·다른 데이터의 재충돌이 반복될 수 있다(해석).

<small>근거: ISO 11783-5:2019 4.4.2.3, 4.5.2, 4.5.4.1~4.5.4.3, 4.5.5, Figure 4, Figure 6~9</small>

## 9. 구현용 상태 표 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

13장과 이 장에서 본 요구를 상태 기계(state machine, 장치가 지금 어느 단계에 있는지와 단계가 바뀌는 조건을 정리한 모형)로 옮기면 다음과 같다. 7절의 상태 그림을 표로 자세히 적은 것이다. 표준이 상태 이름을 정하지는 않으므로 아래 이름은 이 스터디가 붙인 것이다.

| 상태 | 들어오는 조건 | 보낼 수 있는 것 | 나가는 조건 |
|---|---|---|---|
| 미시도 | 전원 인가 | Request for Address Claimed만 | Request 송신 → 조회 대기. non-configurable은 바로 클레임 중으로 갈 수 있다 |
| 조회 대기 | Request 송신 | 없음. 남의 Request에도 응답하지 않는다 | 250 ms + RTxD 경과 → 빈 주소로 Address Claimed 송신, 클레임 중 |
| 클레임 중 | Address Claimed 송신 | Request에 대한 응답, 경합 시 재클레임 | 250 ms 무경합 → 정상. 경합에서 지면 self-configurable은 다른 주소로 다시 클레임 중, 그 밖은 주소 없음 |
| 정상 | 클레임 성공 + 250 ms | 모든 메시지 | 자기 SA로 더 작은 NAME의 클레임 수신 → 클레임 중 또는 주소 없음. Commanded Address 수락·NM Adopt → 클레임 중. 주소 위반 감지 시 Address Claimed 재송신과 DTC(6절) |
| 주소 없음 | Cannot Claim 송신 | Request에 대한 응답으로서의 Cannot Claim(RTxD 후), Request for Address Claimed, Commanded Address에 대한 응답 | Commanded Address 수락 → 클레임 중. 전원 재인가 → 미시도 |

::: details 원문을 가진 독자를 위한 메모
- 7절 초기화 흐름 그림의 a)는 ISO 11783-5:2019 Figure 4, b)는 Figure 5, c)는 Figure 10을 옮긴 것이다.
- 경합 상대 조합별 시퀀스 표의 세 줄은 차례로 Figure 6, Figure 7, Figure 8이고, 동일 식별자 충돌의 Bus OFF 흐름은 Figure 9다.
- 획득 시퀀스가 2판에서 추가되었다는 설명은 4.5.1 NOTE 1, 위험을 줄일 뿐이라는 설명은 NOTE 2, 1판의 1.25 s는 NOTE 3이다.
- 주소 위반 요구가 2판에서 추가되었다는 설명은 4.4.4.3 NOTE, FMI 31의 정의는 ISO 11783-12:2019 E.3.22, DM1의 DTC 배치는 B.6이다.
- 난수 씨앗 권고는 3.4의 Note 1이다.
- 두 250 ms를 한 구간으로 본 해석의 근거는 4.4.2.3과 4.5.2 d), 그리고 Figure 4다.
:::

<small>근거: ISO 11783-5:2019 4.4.2, 4.5</small>

::: tip 핵심 정리
- NAME management(PGN 37632)는 Set Pending(Mode 0) → ACK(Mode 3) → Adopt(Mode 7) → 새 NAME으로 재클레임 순서로 NAME 필드를 바꾼다. identity number는 바꿀 수 없다.
- pending NAME은 Adopt가 오기 전까지 효력이 없다. target은 Adopt를 보낸 CF가 Set Pending을 보낸 CF와 같은지 확인한다.
- checksum은 원래 NAME 8바이트 합의 하위 8비트이고, NM 메시지의 Reserved 비트와 쓰지 않는 칸은 1이다.
- 자기 SA를 쓰는 남의 메시지를 받으면 Address Claimed를 Global로 다시 보내고 SPN 2000+SA, FMI 31 DTC를 켠다.
- 전원을 켠 CF는 미시도 → 조회 대기 → 클레임 중 → 정상(또는 주소 없음) 순서로 상태를 옮긴다. 대기 시간은 CF마다 250~403 ms다.
:::

::: details 확인 문제
1. (개념) NAME management로 바꿀 수 없는 필드는 무엇인가? NM 메시지의 바이트 배치에서 그 이유를 어떻게 확인할 수 있는가?
2. (개념) Set Pending을 받아 ACK를 보낸 target CF는 그 순간부터 새 NAME을 쓰는가?
3. (개념) 전원을 켜고 Request for Address Claimed를 보낸 뒤 250 ms + RTxD를 기다리는 CF가, 다른 CF의 Request for Address Claimed를 받았다. 응답해야 하는가?
4. (계산형) self-configurable CF B(NAME `0xA00882002803D090`, SA 0x81)의 function instance를 3으로 바꾸려 한다. 서비스 툴(SA 0x9A)이 보낼 Set Pending NAME 프레임의 CAN ID와 데이터 8바이트를 쓰라.
5. (디코딩형) 버스에서 `0x18939A81  FF FF 13 28 00 82 09 A1`을 잡았다. 누가 누구에게 보낸 어떤 메시지이고, 담긴 NAME 필드는 무엇인가? 이 데이터의 Byte 3~8을 그대로 Address Claimed의 Byte 3~8에 옮기면 어디가 틀리는가?
6. (진단형) 작업기를 연결한 뒤 VT 화면에서 작업기 UI가 몇 초마다 사라졌다 나타난다. 버스 로그에는 SA 0x85의 Address Claimed가 서로 다른 NAME 두 개로 번갈아 보이고, 작업기의 DM1에는 SPN 2133·FMI 31이 떠 있다. 무엇이 일어나고 있고, 무엇부터 확인하는가?

**답 가이드**
1. identity number다. NM 메시지에는 identity number를 실을 자리가 없다. NAME에서 identity number가 있던 Byte 3 아래쪽 5비트, Byte 2, Byte 1 자리를 Reserved·모드 번호, qualifier flag, checksum(또는 error code)이 차지한다.
2. 아니다. pending NAME은 Adopt(Mode 7)가 오기 전까지 효력이 없고, target은 그동안 current NAME으로 송신한다. Adopt 뒤에도 새 NAME으로 주소 클레임에 성공해야 송신을 재개한다.
3. 응답하지 않는다. 아직 클레임을 시도한 적 없는 CF(조회 대기 상태)는 어떤 Request에도 응답하지 않는다. 대기를 마친 뒤 Address Claimed를 보낸다.
4. CAN ID는 `0x1893819A`(우선순위 6, PF 0x93, DA=target 0x81, SA=툴 0x9A)다. checksum은 NAME 8바이트 합 693의 하위 8비트 `B5`, qualifier flag는 function instance(bit 3)만 0이라 `FB`다. Byte 3은 manufacturer code를 바꾸지 않으므로 `111` + Reserved 1 + Mode 0 = `F0`, Byte 5는 FI=3(`00011`)과 바꾸지 않는 EI의 `111`을 붙인 `1F`다. 나머지 commanded 필드는 모두 1이다. 답은 `B5 FB F0 FF 1F FF FF FF`.
5. PF `0x93`이므로 NAME management(PGN 37632)이고, Byte 3 하위 4비트가 3이라 Mode 3 NAME ACK다. target CF(SA 0x81)가 commanding CF(SA 0x9A)에게 보낸 것이다. pending NAME은 self-configurable 1, IG 2, DCI 1, device class 4, function 130, FI 0, EI 0, manufacturer code 320(`0x28 << 3`)이다. 그대로 옮기면 Byte 7이 `09`가 되어 Reserved가 1이 되고(NAME에서는 0이어야 하므로 `08`), Byte 3 하위 5비트에 identity number 대신 Reserved+Mode(`1 0011`)가 들어간다. identity number는 NM 메시지에 없으므로 자기 값을 다시 채워야 한다.
6. SPN 2133 = 2000 + 0x85(133), FMI 31이므로 SA 0x85에서 주소 위반이 감지된 것이다. 같은 SA에 서로 다른 NAME의 클레임이 번갈아 나온다면 두 CF가 0x85를 놓고 반복해서 다투고 있다. [13장](/study/isobus/13-j1939-address-claim)의 응답 규칙에 따르면 NAME이 큰 쪽은 그 주소를 그만 쓰고 다른 주소를 클레임하거나 Cannot Claim을 보내야 한다. 따라서 ① 두 NAME을 리틀 엔디언 정수로 비교해 진 쪽을 찾고, ② 진 쪽이 다른 주소로 옮기는지 아니면 0x85로 계속 송신하는지 보고, ③ 진 쪽이 새 주소를 initial address로 저장하지 않아 재시작할 때마다 0x85로 돌아오는지 확인한다. UI가 사라지는 것은 VT가 SA 0x85의 NAME이 바뀌는 것을 보고 Working Set(VT 화면을 함께 쓰는 작업기 CF 묶음, [26장](/study/isobus/26-isobus-network-mgmt))이 사라진 것으로 처리하기 때문으로 볼 수 있다(13장 "주소-NAME 대응표" 상자의 disabled 감지, 추론).
:::

## 다음 챕터

- 다음: [15장 Transport Protocol 기초: 8바이트보다 긴 데이터 보내기](/study/isobus/15-tp-bam-cmdt)
