---
title: "Transport Protocol 기초: 8바이트보다 긴 데이터 보내기"
description: "CAN 프레임 하나에 담기지 않는 긴 데이터를 7바이트씩 나누고 번호를 붙여 보내는 Transport Protocol과, 그 두 방식인 BAM과 CMDT를 익힌다."
date: 2026-04-13
tags: [ISOBUS, J1939, CAN, Transport Protocol, BAM, CMDT]
prev: /study/isobus/14-name-management-init
next: /study/isobus/16-tp-connection-rules
---

# Transport Protocol 기초: 8바이트보다 긴 데이터 보내기

::: info 학습 목표
- CAN 프레임 하나에 데이터를 8바이트까지만 실을 수 있어서 Transport Protocol이 필요하다는 것을 설명할 수 있다.
- 긴 데이터를 7바이트씩 나누고 번호를 붙여 보낸 뒤 다시 합치는 과정을 설명할 수 있다.
- BAM(모두에게 방송)과 CMDT(한 상대와 1:1 연결)의 차이와 쓰임새를 비교할 수 있다.
- TP.CM과 TP.DT 프레임의 8바이트를 읽고, 어떤 메시지이며 무엇을 나르는지 알아볼 수 있다.
- 연결이 중간에 끊기면 타임아웃과 Abort로 정리된다는 것을 설명할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [4장 CAN 데이터 프레임](/study/isobus/04-can-data-frame), [9장 J1939 메시지 구조](/study/isobus/09-j1939-message), [12장 주소와 NAME](/study/isobus/12-j1939-address-name)
- 이 장에서 처음 나오는 말
  - Transport Protocol(TP): 8바이트보다 긴 데이터를 여러 CAN 프레임에 나눠 보내고 다시 합치는 규칙
  - 패킷: 나눈 조각 하나를 실은 CAN 프레임
  - 시퀀스 번호: 패킷마다 붙이는 순서 번호(1~255)
  - BAM: 받는 쪽을 정하지 않고 버스 전체에 방송하듯 보내는 방식
  - CMDT: 받는 장치 하나와 연결을 맺고, 그 장치가 허락하는 만큼씩 보내는 방식
  - Control Byte: 연결 관리 프레임(TP.CM)의 첫 바이트로, 그 프레임이 어떤 메시지인지 알려 준다
:::

책 한 질을 택배로 보내는데 상자 하나에 다 들어가지 않으면, 여러 상자에 나눠 담고 상자마다 1번, 2번, 3번 번호를 붙인다. 받는 사람은 번호 순서대로 상자를 풀어 책장을 원래대로 채운다. CAN 프레임은 한 번에 데이터를 8바이트까지만 실을 수 있으므로, 그보다 긴 데이터도 이렇게 나눠 보낸다. 이 장은 J1939와 ISOBUS가 정한 이 "나눠 보내기 규칙", Transport Protocol을 다룬다.

## 1. 8바이트보다 긴 데이터는 어떻게 보내나

이 절에서는 CAN 프레임 하나로 왜 부족한지와, Transport Protocol이 그 문제를 푸는 방법의 큰 그림을 본다.

CAN 프레임의 데이터 필드는 <strong>최대 8바이트</strong>이다([4장](/study/isobus/04-can-data-frame) 참고). 단순한 센서 값이나 제어 신호는 8바이트 안에 담을 수 있지만, 다음과 같은 데이터는 그렇지 않다.

| 데이터 유형 | 일반 크기 |
|-------------|-----------|
| DM1 (진단 코드 목록) | 수십~수백 바이트 |
| VT 오브젝트 풀 (화면 정의) | 수십 KB ~ 수 MB |
| 소프트웨어 업데이트 펌웨어 | 수 KB ~ 수 MB |
| 제품 식별 정보(Product ID) | 수십 바이트 |

DM1은 지금 켜져 있는 고장 코드 목록을 알리는 진단 메시지다([28장](/study/isobus/28-diagnostics-dm-fmi)). VT 오브젝트 풀은 작업기가 트랙터 운전석 화면(VT, Virtual Terminal)에 띄울 화면 구성 전체를 담은 데이터다([32장](/study/isobus/32-vt-object-pool-basics)). KB는 약 1,000바이트, MB는 약 100만 바이트다.

### 쉽게 말하면: 상자에 나눠 담고 번호를 붙인다

긴 데이터는 여러 CAN 프레임으로 <strong>분할(segmentation)</strong>하여 순서대로 전송해야 한다. 수신 측은 조각들을 모아 <strong>재조립(reassembly)</strong>한다. 이 역할을 담당하는 것이 <strong>J1939 Transport Protocol(TP)</strong>이다. 택배와 견주면 다음과 같다.

| 택배 | Transport Protocol |
|---|---|
| 상자 하나에 다 안 들어가는 큰 짐 | 8바이트보다 긴 데이터 |
| 짐을 나눠 담은 상자 하나 | 패킷(CAN 프레임 하나) |
| 상자에 붙인 1번, 2번, 3번 번호표 | 시퀀스 번호(프레임의 첫 바이트) |
| 번호 순서대로 풀어 원래대로 정리 | 재조립 |

![200바이트 데이터를 TP가 7바이트씩 나눠 시퀀스 번호 1, 2, 3, N을 붙인 CAN 프레임으로 보내고, 수신 측이 번호 순서대로 재조립해 원본을 복원하는 흐름](/images/study-isobus/15-tp-parcel-split-light.png)
![200바이트 데이터를 TP가 7바이트씩 나눠 시퀀스 번호 1, 2, 3, N을 붙인 CAN 프레임으로 보내고, 수신 측이 번호 순서대로 재조립해 원본을 복원하는 흐름](/images/study-isobus/15-tp-parcel-split-dark.png)

그림은 200바이트짜리 데이터를 보내는 경우다. 송신 측은 데이터를 7바이트씩 잘라 CAN 프레임에 하나씩 싣고, 프레임마다 1부터 차례로 번호를 붙인다. 마지막 프레임에는 남은 바이트만 들어간다. 수신 측은 번호를 보고 조각을 제자리에 놓아 원래 200바이트를 되살린다.

비유가 어긋나는 점도 하나 있다. 택배 상자는 크기가 제각각일 수 있지만, TP의 패킷은 모두 CAN 프레임 하나(8바이트)로 크기가 같다. 그 8바이트 가운데 첫 바이트를 번호표로 쓰므로 실제 데이터는 패킷마다 7바이트씩만 들어간다.

### 정확히 말하면

- 패킷 하나는 CAN 프레임 하나다. 데이터 8바이트 중 Byte 1은 시퀀스 번호, Byte 2~8의 7바이트는 원래 데이터의 조각이다.
- 시퀀스 번호는 1부터 255까지 쓴다(0은 쓰지 않는다). 그래서 TP로 보낼 수 있는 가장 긴 데이터는 255 패킷 × 7바이트 = 1,785바이트다.
- 패킷은 1번부터 오름차순으로 보낸다. 수신 측은 시퀀스 번호 순서대로 이어 붙여 원래 데이터로 되돌린다.
- TP는 9바이트 이상인 데이터에만 쓴다. 8바이트 이하라면 CAN 프레임 하나로 보낸다.
- 1,785바이트보다 긴 데이터는 확장판인 ETP(Extended Transport Protocol)로 보낸다([17장](/study/isobus/17-etp)).

### 두 가지 보내는 방식: BAM과 CMDT

TP는 두 가지 모드를 제공한다.

- **BAM (Broadcast Announce Message)**: 1:N 브로드캐스트 전송
- **CMDT (Connection Mode Data Transfer)**: 1:1 연결 기반 전송 (흐름 제어 포함)

BAM은 안내 방송과 같다. "지금부터 이런 데이터를 몇 조각으로 나눠 보낸다"고 버스 전체에 알린 뒤 조각을 차례로 흘려보낸다. 필요한 장치는 누구나 받아 가고, 받은 쪽은 아무 대답도 하지 않는다. CMDT는 상대 한 명과 통화하는 것과 같다. "보내도 될까?"라고 묻고, 상대가 "5개까지 보내"라고 허락한 만큼씩 보낸다. 다 받으면 상대가 "잘 받았다"고 알려 준다. 받는 쪽이 감당할 수 있는 만큼만 보내도록 속도를 맞추는 이 장치를 흐름 제어(flow control)라고 한다.

![BAM에서는 송신 ECU가 TP.CM_BAM과 TP.DT를 버스에 내보내면 수신 ECU A, B, C가 모두 받고 응답하지 않으며 DA는 255(전체)다. CMDT에서는 송신 ECU와 수신 ECU 하나만 RTS·TP.DT와 CTS·EndOfMsgACK를 주고받고 다른 ECU는 관여하지 않는다](/images/study-isobus/15-bam-vs-cmdt-light.png)
![BAM에서는 송신 ECU가 TP.CM_BAM과 TP.DT를 버스에 내보내면 수신 ECU A, B, C가 모두 받고 응답하지 않으며 DA는 255(전체)다. CMDT에서는 송신 ECU와 수신 ECU 하나만 RTS·TP.DT와 CTS·EndOfMsgACK를 주고받고 다른 ECU는 관여하지 않는다](/images/study-isobus/15-bam-vs-cmdt-dark.png)

ECU(Electronic Control Unit)는 전자 제어 장치다. 왼쪽 BAM에서는 화살표가 송신 ECU에서 모든 수신 ECU로 한 방향으로만 간다. 오른쪽 CMDT에서는 송신 ECU와 수신 ECU 하나가 양방향으로 주고받는다. 같은 버스에 붙은 다른 ECU도 프레임을 볼 수는 있지만 이 대화에 끼지 않는다. 그림의 DA(Destination Address)는 CAN ID에 든 받는 쪽 주소이고, 255는 "모두"를 뜻하는 전체 주소다([12장](/study/isobus/12-j1939-address-name)).

정리하면 TP는 긴 데이터를 7바이트씩 번호 붙은 패킷으로 나눠 보내는 규칙이고, 모두에게 알리는 BAM과 한 상대와 주고받는 CMDT 두 방식이 있다.

<small>근거: ISO 11783-3 5.10.1, 5.10.2, 5.10.3.1, 5.10.6.3</small>

## 2. 연락용 프레임과 짐 나르는 프레임: TP.CM과 TP.DT

이 절에서는 TP가 쓰는 두 종류의 프레임을 구별하는 법을 본다. BAM이든 CMDT든 TP가 버스에 내보내는 프레임은 이 두 종류뿐이다.

Transport Protocol은 <strong>두 가지 PGN</strong>으로 동작한다. PGN(Parameter Group Number)은 CAN ID 안에 들어 있는, 메시지의 종류를 가리키는 번호다([9장](/study/isobus/09-j1939-message)). 택배에 견주면 하나는 송장과 전화 연락이고, 다른 하나는 번호 붙은 상자다.

| 프레임 | PGN | 하는 일 |
|---|---|---|
| TP.CM | 60416 (`0xEC00`) | 연결 관리: 보내겠다는 알림, 허락, 완료 확인, 중단 |
| TP.DT | 60160 (`0xEB00`) | 데이터 전송: 나눈 조각을 실제로 나른다 |

`0xEC00`처럼 앞에 `0x`가 붙은 수는 16진수다. `0xEC00`은 10진수로 60416, `0xEB00`은 60160이다.

### TP.CM (PGN 60416, 0xEC00): 연결 관리(Connection Management)

연결 관리를 담당한다. BAM 공지, RTS/CTS 흐름 제어, EndOfMsg, Abort 메시지가 모두 이 PGN을 사용하며, <strong>Control Byte(Byte 1)</strong>로 메시지 종류를 구분한다.

아래 그림처럼 TP 프레임의 데이터 8바이트는 Byte 1부터 Byte 8까지 번호를 붙여 부른다. 바이트 번호는 0이 아니라 1부터 센다.

![TP.CM 메시지(8 byte) 바이트 레이아웃. Byte 1이 Control Byte이고 Byte 2~8은 메시지 종류에 따라 해석이 다르며, Control Byte 0x20은 BAM, 0x10은 RTS, 0x11은 CTS, 0x13은 EndOfMsg, 0xFF는 Abort다](/images/study-isobus/11-tpcm-layout-light.png)
![TP.CM 메시지(8 byte) 바이트 레이아웃. Byte 1이 Control Byte이고 Byte 2~8은 메시지 종류에 따라 해석이 다르며, Control Byte 0x20은 BAM, 0x10은 RTS, 0x11은 CTS, 0x13은 EndOfMsg, 0xFF는 Abort다](/images/study-isobus/11-tpcm-layout-dark.png)

Control Byte 값과 메시지는 다음과 같이 짝지어진다.

| Control Byte | 메시지 | 쓰는 방식 |
|---|---|---|
| `0x20` (=32) | BAM: 방송을 시작한다는 알림 | BAM |
| `0x10` (=16) | RTS(Request To Send): 보내도 되는지 묻기 | CMDT |
| `0x11` (=17) | CTS(Clear To Send): 보내도 좋다는 허락 | CMDT |
| `0x13` (=19) | EndOfMsgACK: 다 받았다는 확인 | CMDT |
| `0xFF` (=255) | Abort: 연결을 중간에 끊는다는 통보 | CMDT |

Byte 2~8의 뜻은 메시지마다 다르다. 다만 다섯 메시지 모두 Byte 6~8에 지금 나르는 데이터의 PGN을 넣는다. CAN ID에 든 PGN 60416은 "TP 연락 프레임"이라는 뜻일 뿐이고, 무슨 데이터를 나르는지는 Byte 6~8이 알려 준다. 송장에 "내용물: 제품 식별 정보"라고 적는 것과 같다.

### TP.DT (PGN 60160, 0xEB00): 데이터 전송(Data Transfer)

실제 데이터를 7바이트씩 분할하여 전송한다. **Byte 1은 시퀀스 번호(1~255)**, Byte 2~8이 페이로드이다. 마지막 패킷의 남는 바이트는 0xFF로 채운다. 페이로드(payload)는 프레임에 실린 실제 데이터 부분을 말한다.

![TP.DT 메시지(8 byte) 바이트 레이아웃. Byte 1은 시퀀스 번호(1~255), Byte 2~8은 페이로드 7바이트이고, 마지막 패킷의 남는 자리는 0xFF로 패딩한다](/images/study-isobus/11-tpdt-layout-light.png)
![TP.DT 메시지(8 byte) 바이트 레이아웃. Byte 1은 시퀀스 번호(1~255), Byte 2~8은 페이로드 7바이트이고, 마지막 패킷의 남는 자리는 0xFF로 패딩한다](/images/study-isobus/11-tpdt-layout-dark.png)

TP.DT의 CAN ID에는 PGN 60160만 있고, 어떤 데이터의 조각인지는 들어 있지 않다. 수신 측은 앞서 받은 TP.CM(BAM이나 RTS)의 Byte 6~8을 보고 어떤 데이터의 조각인지 안다. 이 점은 4절의 "연결 제약"에서 다시 중요해진다.

마지막 패킷을 `FF`로 채우는 것은 TP.DT의 데이터를 언제나 8바이트로 맞추기 때문이다. 수신 측은 BAM이나 RTS에서 총 크기를 미리 들었으므로, 총 크기만큼만 데이터로 쓰고 나머지 `FF`는 버린다.

<strong>예시: 16바이트 데이터 전송</strong>

16바이트를 7바이트씩 자르면 7 + 7 + 2바이트가 되어 패킷 3개가 필요하다. 그림에서는 원본 바이트를 A1~A7, B1~B7, C1~C2로 표시했다.

![16바이트 원본 데이터를 7바이트씩 3개의 TP.DT 패킷으로 나누고, 마지막 패킷은 남는 자리를 FF로 패딩한 그림](/images/study-isobus/11-tpdt-segmentation-light.png)
![16바이트 원본 데이터를 7바이트씩 3개의 TP.DT 패킷으로 나누고, 마지막 패킷은 남는 자리를 FF로 패딩한 그림](/images/study-isobus/11-tpdt-segmentation-dark.png)

세 번째 패킷을 바이트 순서대로 읽어 보면 다음과 같다.

1. Byte 1 = `03`: 시퀀스 번호 3, 세 번째 조각이다.
2. Byte 2~3 = C1, C2: 원본의 15, 16번째 바이트다. n번 패킷은 원본의 (n − 1) × 7 + 1번째 바이트부터 담으므로 3번 패킷은 15번째부터다.
3. Byte 4~8 = `FF` 다섯 개: 원본이 16바이트에서 끝나므로 남는 다섯 자리를 `FF`로 채웠다.

정리하면 TP.CM은 "무엇을 얼마나 보낼지"를 주고받는 연락용 프레임이고, TP.DT는 시퀀스 번호와 데이터 7바이트를 싣는 운반용 프레임이다.

<small>근거: ISO 11783-3 5.10.2.4, 5.10.3.4.1, 5.10.4.1, 5.10.5, Annex B</small>

## 3. BAM: 버스 전체에 방송하듯 보내기

이 절에서는 받는 쪽을 정하지 않고 보내는 BAM의 순서와 규칙을 본다. 여러 장치가 같은 정보를 받아야 할 때 쓰는 방식이다.

BAM은 특정 수신자를 지정하지 않고 <strong>버스 전체에 브로드캐스트</strong>하는 방식이다. 흐름 제어가 없으므로 수신자는 확인 응답(ACK)을 보내지 않는다. 구현이 단순하지만 재전송이 불가능하다.

쉽게 말하면 "지금부터 200바이트짜리 자료를 29조각으로 나눠 보낸다"고 안내 방송(TP.CM_BAM)을 한 다음, 조각(TP.DT)을 일정한 간격으로 흘려보내는 방식이다. 듣는 쪽은 필요하면 받아 적는다. 한 조각을 놓쳐도 다시 들려 달라고 할 방법이 없다.

### BAM 흐름

![BAM 흐름. 송신 ECU가 TP.CM_BAM(PGN 60416, 총 크기 200 byte, 패킷 수 29)을 보내고 10~200 ms 대기 뒤 TP.DT #1, #2, #3부터 #N까지 10~200 ms 간격으로 보낸다. 수신 측은 T1 750 ms 안에 다음 패킷이 오지 않으면 재조립을 포기하고, 각 수신 ECU가 응답 없이 따로 재조립한다](/images/study-isobus/15-bam-sequence-light.png)
![BAM 흐름. 송신 ECU가 TP.CM_BAM(PGN 60416, 총 크기 200 byte, 패킷 수 29)을 보내고 10~200 ms 대기 뒤 TP.DT #1, #2, #3부터 #N까지 10~200 ms 간격으로 보낸다. 수신 측은 T1 750 ms 안에 다음 패킷이 오지 않으면 재조립을 포기하고, 각 수신 ECU가 응답 없이 따로 재조립한다](/images/study-isobus/15-bam-sequence-dark.png)

1. 송신 ECU가 TP.CM_BAM을 보낸다. DA는 전체 주소 255이고, 데이터에는 총 크기(200바이트), 총 패킷 수(29개), 나를 데이터의 PGN이 들어 있다.
2. 10~200 ms 기다린 뒤 TP.DT 1번을 보낸다. ms(밀리초)는 1/1000초다.
3. 패킷 사이마다 10~200 ms 간격을 두고 마지막 N번 패킷까지 보낸다. 200바이트라면 N은 29다(200 ÷ 7을 올림).
4. 수신 ECU는 저마다 따로 재조립하고, 응답은 보내지 않는다. 다음 패킷이 750 ms 안에 오지 않으면 재조립을 포기한다.

### TP.CM_BAM 메시지 구조 (8바이트)

표를 읽는 법부터 보자. 바이트 번호는 1부터 센다. 2바이트 이상을 차지하는 값은 리틀 엔디언(Little-Endian)으로 적는데, 낮은 자리 바이트를 먼저 쓴다는 뜻이다. 예를 들어 크기 200은 16진수로 `0x00C8`이다. 프레임에는 낮은 자리 `C8`이 먼저, 높은 자리 `00`이 나중에 와서 `C8 00`이 된다.

| Byte | 내용 |
|------|------|
| Byte 1 | Control Byte = `0x20` (BAM 식별자) |
| Byte 2~3 | 총 데이터 크기 (Little-Endian, 9 ~ 1785 byte) |
| Byte 4 | 총 패킷 수 (2~255) |
| Byte 5 | `0xFF` (예약) |
| Byte 6~8 | 전송할 PGN (24bit, Little-Endian) |

(전체 8바이트 안에서 Control Byte가 차지하는 위치는 2절의 TP.CM 바이트 레이아웃 그림 참고)

예약(reserved)은 나중에 표준을 고칠 때 쓰려고 비워 둔 자리다. 지금은 아무 뜻이 없으므로 정해진 값 `FF`로 채워 보낸다. 총 크기가 9바이트부터인 것은 8바이트 이하라면 TP 없이 프레임 하나로 보내기 때문이다. 총 패킷 수가 2부터인 것도 같은 이유다. 9바이트만 돼도 7 + 2바이트로 패킷 2개가 필요하다.

6절에서 볼 BAM 프레임 `20 14 00 03 FF EB FE 00`을 이 표대로 읽어 보자.

1. Byte 1 = `20`: Control Byte가 `0x20`이므로 BAM이다.
2. Byte 2~3 = `14 00`: 리틀 엔디언이므로 `0x0014`, 즉 20바이트다.
3. Byte 4 = `03`: 패킷 3개로 나눠 보낸다. 20 ÷ 7을 올림하면 3이다.
4. Byte 5 = `FF`: 예약 자리다.
5. Byte 6~8 = `EB FE 00`: 거꾸로 읽으면 `0x00FEEB` = 65259다. 나르는 데이터는 PGN 65259(제품 식별 정보)다.

### 타이밍 규칙

| 항목 | 값 |
|------|----|
| BAM 후 첫 TP.DT까지 대기 | 10ms ~ 200ms |
| TP.DT 패킷 간 간격 | 10ms ~ 200ms (최소 10ms는 수신 측이 CAN 하드웨어에서 메시지를 꺼낼 시간 보장) |
| 수신 측 타임아웃 | 750ms (패킷 미수신 시 재조립 포기) |

BAM에는 수신 측이 속도를 조절할 수단(흐름 제어)이 없다. 그래서 간격에 하한 10 ms를 두어, 수신 측이 CAN 하드웨어에서 메시지를 꺼낼 시간을 보장한다. 상한 200 ms와 수신 측 타임아웃 750 ms는 짝을 이룬다. 750 ms는 최대 간격 200 ms보다 넉넉히 길어서, 송신 측이 규칙을 지키는 한 수신 측이 재조립을 포기할 일은 없다. [16장](/study/isobus/16-tp-connection-rules)에서 이 750 ms에 T1이라는 이름을 붙여 다시 다룬다.

BAM에는 닫기 절차도 없다. 송신 측은 마지막 패킷을 보냈을 때, 수신 측은 마지막 패킷을 받았거나 750 ms가 지났을 때 전송이 끝난 것으로 본다. BAM 수신 측은 Abort(중단 통보)도 보낼 수 없다.

정리하면 BAM은 알림 한 번과 데이터 조각들로 끝난다. 받는 쪽은 대답하지 않고, 놓친 조각을 되찾을 수 없다.

<small>근거: ISO 11783-3 5.10.3.2, 5.10.3.5, 5.10.4.1, 5.10.4.6, 5.13.3</small>

## 4. CMDT: 한 상대와 연결을 맺고 허락받으며 보내기

이 절에서는 받는 장치 하나와 연결을 맺고 보내는 CMDT를 본다. 받는 쪽이 속도를 조절하고 다 받았는지 확인해 주므로 BAM보다 믿을 만하다.

CMDT는 **특정 수신자와 1:1 연결을 맺고** 흐름 제어를 포함한 데이터 전송을 수행한다. 수신자가 처리 가능한 패킷 수를 제어(CTS)할 수 있어 버퍼 오버플로를 방지한다.

버퍼(buffer)는 받은 데이터를 잠시 담아 두는 메모리이고, 버퍼 오버플로(overflow)는 이 공간이 넘쳐 데이터를 잃는 일이다. 쉽게 말하면 전화로 긴 주소를 불러 주는 상황이다. 받아 적는 사람이 "다섯 글자씩 불러 줘"라고 하면 다섯 글자를 부르고 기다렸다가, "다음"이라고 하면 이어서 부른다. 다 적으면 "다 받았어"라고 말하고 끊는다.

### CMDT 흐름

![CMDT 흐름. 송신 ECU(SA=0x23)가 RTS(총 크기 200 byte, 패킷 수 29)를 보내고, 수신 ECU(SA=0x82)가 CTS(허용 패킷 수 5, 시작 시퀀스 1)로 답하면 TP.DT #1~#5를 보낸다. 다시 CTS(허용 패킷 수 5, 시작 시퀀스 6)를 받아 TP.DT #6부터 #29까지 보낸 뒤 수신 ECU가 EndOfMsgACK로 완료를 확인한다](/images/study-isobus/15-cmdt-sequence-light.png)
![CMDT 흐름. 송신 ECU(SA=0x23)가 RTS(총 크기 200 byte, 패킷 수 29)를 보내고, 수신 ECU(SA=0x82)가 CTS(허용 패킷 수 5, 시작 시퀀스 1)로 답하면 TP.DT #1~#5를 보낸다. 다시 CTS(허용 패킷 수 5, 시작 시퀀스 6)를 받아 TP.DT #6부터 #29까지 보낸 뒤 수신 ECU가 EndOfMsgACK로 완료를 확인한다](/images/study-isobus/15-cmdt-sequence-dark.png)

SA(Source Address)는 프레임을 보낸 쪽의 주소다. 그림에서 송신 ECU는 `0x23`(=35), 수신 ECU는 `0x82`(=130)이다.

1. 송신 ECU가 RTS를 보낸다: "200바이트를 29패킷으로 보내고 싶다."
2. 수신 ECU가 CTS로 답한다: "1번부터 5개 보내라." 이 CTS가 오가면서 연결이 맺어진다. 양쪽이 각자 언제 연결이 맺어졌다고 보는지는 16장에서 자세히 본다.
3. 송신 ECU는 1~5번 TP.DT를 보내고, 다음 허락을 기다린다.
4. 수신 ECU가 다음 CTS로 "6번부터 5개"를 허락한다. 이를 29번까지 되풀이한다.
5. 29번까지 다 받으면 수신 ECU가 EndOfMsgACK를 보내고 연결이 닫힌다.

### CMDT 제어 메시지 Control Byte 값

| 메시지 | Control Byte | 설명 |
|--------|-------------|------|
| RTS | 0x10 | 전송 요청 (총 크기, 패킷 수, CTS당 최대 패킷 수, PGN 포함) |
| CTS | 0x11 | 수신 준비 (허용 패킷 수, 시작 시퀀스 번호) |
| EndOfMsgACK | 0x13 | 전체 전송 완료 확인 |
| Abort | 0xFF | 연결 중단 (사유 코드 포함) |

네 메시지의 8바이트 배치는 다음과 같다. 칸은 Byte 1부터 센 위치이고, 총 크기는 2바이트 리틀 엔디언이다. 예약 자리는 `FF`로 채운다.

| Byte | RTS (16) | CTS (17) | EndOfMsgACK (19) | Abort (255) |
|---|---|---|---|---|
| 1 | Control Byte 16 | Control Byte 17 | Control Byte 19 | Control Byte 255 |
| 2 | 총 크기 (낮은 자리) | 보내도 되는 패킷 수 | 총 크기 (낮은 자리) | 중단 사유 코드 |
| 3 | 총 크기 (높은 자리) | 다음에 보낼 패킷 번호 | 총 크기 (높은 자리) | 예약 (FF) |
| 4 | 총 패킷 수 | 예약 (FF) | 총 패킷 수 | 예약 (FF) |
| 5 | CTS 하나가 허락할 수 있는 최대 패킷 수 (FF = 제한 없음) | 예약 (FF) | 예약 (FF) | 예약 (FF) |
| 6~8 | 나르는 데이터의 PGN | 나르는 데이터의 PGN | 나르는 데이터의 PGN | 나르는 데이터의 PGN |

6절에서 볼 CTS `11 03 01 FF FF EB FE 00`을 읽어 보면, Byte 1 `11`(=17)은 CTS, Byte 2 `03`은 "3개를 보내도 된다", Byte 3 `01`은 "1번부터", Byte 4~5 `FF FF`는 예약, Byte 6~8 `EB FE 00`은 PGN 65259다.

몇 가지 세부 규칙이 있다.

- <strong>RTS Byte 5</strong>는 CTS 하나가 지정할 수 있는 최대 패킷 수의 제한이다(0xFF면 제한 없음). CTS의 허용 패킷 수는 RTS의 총 패킷 수(Byte 4)와 이 제한(Byte 5) 중 <strong>작은 값을 넘을 수 없다.</strong> 수신 측이 이 제한을 지키면 송신 측은 놓친 패킷을 항상 재전송할 수 있음이 보장된다.
- <strong>CTS(0)</strong>: 허용 패킷 수 0의 CTS는 연결을 유지한 채 흐름을 잠시 멈추는 hold다. 수 초간 멈춰야 하면 연결이 끊기지 않도록 <strong>Th(500 ms)마다 CTS(0)를 반복 송신</strong>해야 하고, 송신 측은 CTS(0) 후 <strong>T4(1050 ms)</strong> 안에 다음 CTS가 오지 않으면 연결을 닫는다.

Th와 T4는 표준이 기다림과 반복의 시간 한도마다 붙인 이름이다. 5절에서 한 표로 모아 보고, 16장에서 자세히 다룬다. RTS Byte 5가 재전송을 보장하는 이유도 16장에서 설명한다.

### 연결 제약

- 하나의 송신 장치는 <strong>특정 목적지당 동시에 1개의 CMDT 연결</strong>만 시작할 수 있다. TP.DT에는 SA·DA만 있고 전송 중인 데이터의 PGN 정보가 없기 때문이다.
- 하나의 송신 장치는 <strong>동시에 1개의 BAM</strong>만 보낼 수 있다. 같은 상대에 대한 CMDT 1개 + BAM 1개는 DA(특정/Global)로 구분되므로 병행할 수 있다.

TP.DT에는 "어느 연결의 조각인지" 적는 칸이 없다. 같은 상대에게 연결 두 개를 동시에 열면, 수신 측은 도착한 조각이 어느 연결의 것인지 가릴 수 없다. 그래서 한 상대와는 한 번에 연결 하나만 연다. BAM의 DA는 255(Global, 전체)이고 CMDT의 DA는 특정 주소이므로, 이 둘은 섞여 와도 DA로 구별된다.

### Connection Abort 주요 사유 코드

Abort(Connection Abort)는 연결을 끝까지 마치지 못하고 끊을 때 보내는 TP.CM이다. Byte 2에 왜 끊는지 사유 코드를 넣고, 송신 측과 수신 측 모두 보낼 수 있다.

| 코드 | 의미 |
|------|------|
| 1 | 이미 다른 세션 진행 중이라 추가 세션 불가 |
| 2 | 시스템 자원이 다른 작업에 필요해 세션 종료 |
| 3 | 타임아웃 발생 |
| 4 | 데이터 전송 중 CTS 수신 |
| 5 | 최대 재전송 요구 한도 도달 |
| 6~9 | 예기치 않은 패킷, 잘못된/중복 시퀀스 번호, 크기 초과 등 |

세션(session)은 연결 하나가 열려서 닫힐 때까지의 전송 한 번을 말한다. 사유 코드 전체와 각 코드가 나오는 상황은 16장에서 다룬다.

### BAM vs CMDT 비교

| 항목 | BAM | CMDT |
|------|-----|------|
| 수신 대상 | 브로드캐스트 (전체) | 특정 장치 (1:1) |
| 흐름 제어 | 없음 | 있음 (CTS) |
| 완료 확인 | 없음 | EndOfMsgACK |
| 재전송 | 불가 | 가능 (CTS로 누락 패킷부터 재요청, 2회 이하 권장) |
| 최대 크기 | 1785 byte | 1785 byte |

정리하면 CMDT는 RTS로 묻고, CTS로 허락받은 만큼 TP.DT를 보내고, EndOfMsgACK로 끝난다. 한 상대와는 한 번에 연결 하나만 연다.

<small>근거: ISO 11783-3 5.10.3.3, 5.10.3.4.2, 5.10.4.1~5.10.4.5, 5.10.6.2</small>

## 5. 중간에 끊기면 어떻게 되나: 타임아웃과 Abort

이 절에서는 CMDT 연결이 정상으로 끝나지 못하는 경우를 본다. 상대가 갑자기 꺼지거나 프레임이 사라져도 양쪽이 끝없이 기다리지 않게 해 주는 장치가 타임아웃과 Abort다.

타임아웃(timeout)은 "이 시간 안에 다음 프레임이 오지 않으면 끊긴 것으로 본다"는 기다림의 한도다. 전화 통화에서 상대가 한참 아무 말이 없으면 끊긴 줄 알고 전화를 내려놓는 것과 같다. 다만 TP는 그냥 내려놓지 않고, Abort를 보내 "이 연결은 끝났다"고 상대에게 알린다.

### 세 가지 결말

![RTS 뒤 CMDT 연결의 세 가지 결말. 정상 흐름은 CTS(허용 N, 시작 시퀀스 1), TP.DT #1~#N, 다음 묶음 CTS를 N 패킷씩 반복한 뒤 EndOfMsgACK로 끝난다. 수신 측 오류(버퍼 부족 등)는 수신 ECU가 Abort(오류 코드)를 보내 연결이 끝나고 송신 측이 재시도 여부를 정한다. 타임아웃은 1250 ms 안에 CTS가 오지 않아 송신 ECU가 Abort(타임아웃)를 보낸다](/images/study-isobus/15-cmdt-endings-light.png)
![RTS 뒤 CMDT 연결의 세 가지 결말. 정상 흐름은 CTS(허용 N, 시작 시퀀스 1), TP.DT #1~#N, 다음 묶음 CTS를 N 패킷씩 반복한 뒤 EndOfMsgACK로 끝난다. 수신 측 오류(버퍼 부족 등)는 수신 ECU가 Abort(오류 코드)를 보내 연결이 끝나고 송신 측이 재시도 여부를 정한다. 타임아웃은 1250 ms 안에 CTS가 오지 않아 송신 ECU가 Abort(타임아웃)를 보낸다](/images/study-isobus/15-cmdt-endings-dark.png)

1. 정상 흐름: 수신 측이 CTS(허용 패킷 수 N, 시작 시퀀스 1)로 답하고, 송신 측은 N개씩 보낸다. 다음 묶음의 CTS를 되풀이하다가 EndOfMsgACK로 끝난다.
2. 수신 측 오류(버퍼 부족 등): 수신 측이 Abort(오류 코드)를 보내 연결을 끝낸다. 송신 측은 다시 시도할지 스스로 정한다.
3. 타임아웃(수신 측이 CTS를 보내지 않음): 송신 측이 RTS를 보낸 뒤 1250 ms 안에 CTS를 받지 못하면 Abort(타임아웃)를 보낸다.

### 타임아웃 규칙 요약

| 상황 | 타임아웃 값 | 처리 |
|------|------------|------|
| RTS 후 CTS 대기 | 1250ms (T3) | 송신 측 Abort |
| CTS 후 첫 TP.DT 대기 | 1250ms (T2) | 수신 측 Abort |
| TP.DT 패킷 간 간격 | 750ms (T1) | 수신 측 Abort |
| 마지막 패킷 송신 후 CTS/EndOfMsgACK 대기 | 1250ms (T3) | 송신 측 Abort |
| CTS(0) 후 다음 CTS 대기 | 1050ms (T4) | 송신 측 Abort |
| CTS(0) hold 반복 주기 | 500ms (Th) | 수신 측이 이 주기로 CTS(0) 재송신 |
| BAM TP.DT 패킷 간 | 750ms (T1) | 수신 측 재조립 포기 |

표에서 T1~T4는 기다림의 한도이고, Th는 hold 중인 수신 측이 CTS(0)를 되풀이하는 주기다. 송신 측이 재는 한도(T3, T4)와 수신 측이 재는 한도(T1, T2)가 나뉜다. CMDT에서는 어느 쪽이든 한도를 넘겨 연결을 닫을 때 Abort를 보내고, 사유 코드는 3(타임아웃)이다. BAM 수신 측은 Abort 없이 재조립만 포기한다. 각 타이머가 정확히 언제 시작하고 끝나는지는 [16장](/study/isobus/16-tp-connection-rules)에서 그림과 함께 본다.

정리하면 TP의 모든 기다림에는 한도가 있고, 한도를 넘기면 Abort로 연결을 정리한다. 그래서 상대가 사라져도 연결이 영원히 열린 채로 남지 않는다.

<small>근거: ISO 11783-3 5.10.3.5, 5.10.4.5, 5.13.3</small>

## 6. 20바이트를 직접 쪼개 보기

앞 절들이 BAM·CMDT의 흐름과 필드 정의를 그림과 표로 다뤘다면, 여기서는 <strong>20바이트짜리 데이터 하나를 BAM과 CMDT 두 방식으로 전송할 때 버스에 실제로 흐르는 모든 프레임의 8바이트</strong>를 끝까지 나열한다.

### 공통 설정: 보낼 데이터와 목적 PGN

전송할 데이터는 Component Identification(<strong>PGN 65259</strong>, `0x00FEEB`) 20바이트로 정한다. Component Identification은 부품의 제조사(Make), 모델(Model), 일련번호(Serial), 장치 번호(Unit)를 알리는 메시지다. ISO 11783-3(ISOBUS의 데이터 링크 계층을 정한 표준 문서)도 오류 없는 TP 전송 예제와 방송·응답 예제에 이 PGN을 쓴다([Part 3 정리 부록](/study/isobus/appendix-iso-part03)). Make·Model·Serial·Unit을 `*`로 구분한 ASCII 문자열을 데이터로 쓴다. ASCII는 글자 하나를 1바이트 숫자로 나타내는 약속이다. 예를 들어 `A`는 `0x41`(=65), `*`는 `0x2A`(=42), `0`은 `0x30`(=48)이다.

```
원본 문자열: "AGMO*TP100*SN0007*01"   (Make=AGMO, Model=TP100, Serial=SN0007, Unit=01)

hex(20 byte):
41 47 4D 4F 2A 54 50 31 30 30 2A 53 4E 30 30 30 37 2A 30 31
```

### 패킷 수 계산

TP.DT는 Byte 1이 시퀀스 번호이므로 <strong>페이로드는 프레임당 7바이트</strong>다(2절 TP.CM과 TP.DT 참고). 20바이트를 7바이트씩 나누면 다음과 같다.

```
20 byte ÷ 7 byte/packet = 2.86... → 올림하면 3 packet

Packet #1 (Seq=1): 7 byte 실데이터
Packet #2 (Seq=2): 7 byte 실데이터
Packet #3 (Seq=3): 6 byte 실데이터 + FF 1byte 패딩   ← 20 − 7×2 = 6 byte
```

<strong>총 패킷 수 = 3</strong>이며, 마지막 패킷은 남는 1바이트를 `FF`로 채운다.

### BAM 시퀀스: 프레임 4개

목적지는 Global(브로드캐스트, DA 255)이다. TP.CM_BAM(Control Byte `0x20`) 1프레임과 TP.DT 3프레임, 총 4프레임이 순서대로 나간다. 표의 "8바이트 hex"는 프레임 데이터 8바이트를 Byte 1부터 차례로 적은 것이고, LE는 리틀 엔디언의 줄임말이다.

| 순번 | PGN | 8바이트 hex | 의미 |
|---|---|---|---|
| 1 | TP.CM (60416) | `20 14 00 03 FF EB FE 00` | BAM 공지. Control=`0x20`, 총 크기=`14 00`(LE, 20byte), 총 패킷수=`03`, 예약=`FF`, 대상 PGN=`EB FE 00`(LE, 65259) |
| 2 | TP.DT (60160) | `01 41 47 4D 4F 2A 54 50` | Seq=`01`, 데이터 `"AGMO*TP"` |
| 3 | TP.DT (60160) | `02 31 30 30 2A 53 4E 30` | Seq=`02`, 데이터 `"100*SN0"` |
| 4 | TP.DT (60160) | `03 30 30 37 2A 30 31 FF` | Seq=`03`, 데이터 `"007*01"`(6byte) + `FF` 패딩 |

BAM 후 첫 TP.DT까지, 그리고 TP.DT 패킷 사이는 각각 <strong>10~200ms</strong> 대기해야 한다. 수신 측은 확인 응답을 보내지 않는다.

TP.DT 2번 프레임 `02 31 30 30 2A 53 4E 30`을 풀어 읽으면, Byte 1 `02`는 시퀀스 번호 2이고 Byte 2~8은 ASCII로 `1`, `0`, `0`, `*`, `S`, `N`, `0`이다. 2번 패킷은 원본의 (2 − 1) × 7 + 1 = 8번째 글자부터 담으므로, 원본의 8~14번째 글자 `"100*SN0"`과 같다.

### CMDT 시퀀스: 프레임 6개

목적지는 특정 CF다(예: 송신 SA=`0x23`, 수신 SA=`0x82`, 4절 CMDT 흐름의 예시와 동일). CF(Control Function)는 네트워크에서 주소 하나를 갖고 통신하는 기능 단위로, 여기서는 ECU 하나로 생각해도 된다. RTS → CTS → TP.DT 3프레임 → EndOfMsgACK, 총 6프레임이 오간다. 20바이트·3패킷 정도는 CTS 한 번으로 전부 허용해도 되므로 CTS 묶음은 1회만 등장한다.

| 순번 | 메시지 (PGN) | 8바이트 hex | 의미 |
|---|---|---|---|
| 1 | RTS · TP.CM (60416) | `10 14 00 03 FF EB FE 00` | Control=`0x10`, 총 크기=`14 00`(20byte), 총 패킷수=`03`, CTS당 최대 패킷수=`FF`(제한 없음), 대상 PGN=65259 |
| 2 | CTS · TP.CM (60416) | `11 03 01 FF FF EB FE 00` | Control=`0x11`, 허용 패킷수=`03`, 시작 시퀀스=`01`, Byte4~5 예약=`FF FF`, 대상 PGN=65259 |
| 3 | TP.DT (60160) | `01 41 47 4D 4F 2A 54 50` | Seq=`01`, 데이터 `"AGMO*TP"` |
| 4 | TP.DT (60160) | `02 31 30 30 2A 53 4E 30` | Seq=`02`, 데이터 `"100*SN0"` |
| 5 | TP.DT (60160) | `03 30 30 37 2A 30 31 FF` | Seq=`03`, 데이터 `"007*01"`(6byte) + `FF` 패딩 |
| 6 | EndOfMsgACK · TP.CM (60416) | `13 14 00 03 FF EB FE 00` | Control=`0x13`, 총 크기=`14 00`(20byte), 총 패킷수=`03`, 예약=`FF`, 대상 PGN=65259. 수신 완료 확인 |

CTS의 Byte 2(`03`)는 RTS의 Byte 4(총 패킷수 `03`)와 Byte 5(`FF`=제한 없음) 중 <strong>작은 값을 넘지 않는다</strong>는 규칙을 그대로 지킨 값이다.

### 두 방식 비교

| 항목 | BAM | CMDT |
|---|---|---|
| 총 프레임 수 | 4 (BAM 1 + DT 3) | 6 (RTS 1 + CTS 1 + DT 3 + EndOfMsgACK 1) |
| 목적지 | Global(브로드캐스트) | 특정 CF(destination-specific) |
| 패킷 간격 규정 | BAM→DT1, DT1→DT2, DT2→DT3 각각 10~200ms(3구간) | DT1→DT2, DT2→DT3 최대 200ms·최소 규정 없음(2구간) |
| 대략적 소요 시간(간격만) | 최소 30ms ~ 최대 600ms | 최소 0ms대 ~ 최대 약 400ms(+ RTS→CTS·EndOfMsgACK 응답 시간) |
| 완료 확인 | 없음 | EndOfMsgACK로 확인 |
| 재전송 | 불가 | 가능: CTS로 누락 시퀀스부터 재요청 |

소요 시간 줄은 간격 규정에서 바로 나온다. BAM은 3구간이 모두 10~200 ms이므로 간격만 30~600 ms다. CMDT는 패킷 사이 간격에 하한이 없어 연달아 보낼 수 있고, 2구간이 최대 200 ms씩이다. 대신 CMDT에는 RTS에 대한 CTS, 마지막 패킷에 대한 EndOfMsgACK를 기다리는 시간이 더 붙는다.

::: tip 핵심 통찰
같은 20바이트라도 <strong>CMDT가 프레임 수는 더 많다</strong>(6개 vs 4개). RTS·CTS·EndOfMsgACK라는 제어 오버헤드 3프레임이 붙기 때문이다. 대신 CMDT는 목적지가 명확하고 흐름 제어·재전송이 가능해 신뢰성이 필요한 1:1 전송에 쓰이고, BAM은 오버헤드 없이 여러 수신자에게 한 번에 뿌려야 할 때(Component ID 공지 등) 쓰인다. 어느 쪽이 항상 빠르거나 우월한 게 아니라, <strong>신뢰성이 필요한가 vs 여러 수신자에게 동시에 알려야 하는가</strong>가 선택 기준이다.
:::

::: details 파이썬으로 검산해 보기
앞의 두 표를 손으로 만들지 않고 코드로 다시 계산해 보는 검산이다. 7바이트씩 잘라 번호를 붙이는 함수 하나로 BAM과 CMDT의 모든 프레임을 만든다.

```python
def tp_dt_frames(data: bytes):
    """7바이트씩 잘라 시퀀스 번호를 붙이고 마지막 패킷은 FF로 패딩한다."""
    frames = []
    for i in range(0, len(data), 7):
        chunk = data[i:i + 7]
        seq = i // 7 + 1
        payload = list(chunk) + [0xFF] * (7 - len(chunk))
        frames.append([seq] + payload)
    return frames


DATA = b"AGMO*TP100*SN0007*01"
PGN = 65259                      # Component Identification

assert len(DATA) == 20

total_size = len(DATA)
size_lo, size_hi = total_size & 0xFF, (total_size >> 8) & 0xFF
pgn_lo  = PGN & 0xFF
pgn_mid = (PGN >> 8) & 0xFF
pgn_hi  = (PGN >> 16) & 0xFF

dt_frames = tp_dt_frames(DATA)
num_packets = len(dt_frames)
assert num_packets == 3

bam = [0x20, size_lo, size_hi, num_packets, 0xFF, pgn_lo, pgn_mid, pgn_hi]
rts = [0x10, size_lo, size_hi, num_packets, 0xFF, pgn_lo, pgn_mid, pgn_hi]
cts = [0x11, num_packets, 1, 0xFF, 0xFF, pgn_lo, pgn_mid, pgn_hi]
eom = [0x13, size_lo, size_hi, num_packets, 0xFF, pgn_lo, pgn_mid, pgn_hi]

def show(label, frame):
    print(f"{label:14s}", ' '.join(f'{b:02X}' for b in frame))

show("TP.CM_BAM", bam)
for f in dt_frames:
    show(f"TP.DT#{f[0]}", f)

print()
show("RTS", rts)
show("CTS", cts)
for f in dt_frames:
    show(f"TP.DT#{f[0]}", f)
show("EndOfMsgACK", eom)

# BAM 프레임 4개, CMDT 프레임 6개인지 검산
assert 1 + len(dt_frames) == 4
assert 3 + len(dt_frames) == 6
```

실행 결과:
```
TP.CM_BAM      20 14 00 03 FF EB FE 00
TP.DT#1        01 41 47 4D 4F 2A 54 50
TP.DT#2        02 31 30 30 2A 53 4E 30
TP.DT#3        03 30 30 37 2A 30 31 FF

RTS            10 14 00 03 FF EB FE 00
CTS            11 03 01 FF FF EB FE 00
TP.DT#1        01 41 47 4D 4F 2A 54 50
TP.DT#2        02 31 30 30 2A 53 4E 30
TP.DT#3        03 30 30 37 2A 30 31 FF
EndOfMsgACK    13 14 00 03 FF EB FE 00
```

출력의 각 줄이 앞의 두 표의 "8바이트 hex" 칸과 같다. `size_lo`, `size_hi`와 `pgn_lo`, `pgn_mid`, `pgn_hi`가 리틀 엔디언으로 낮은 자리부터 나누는 부분이고, 마지막 두 assert는 BAM 4프레임, CMDT 6프레임이라는 비교 표의 숫자를 확인한다.
:::

<small>근거: ISO 11783-3 5.10.2.4, 5.10.4.1, 5.13.3, Annex B, Annex C</small>

::: tip 핵심 정리
- CAN 프레임은 데이터를 최대 8바이트까지만 싣는다. 9바이트 이상은 Transport Protocol로 7바이트씩 나눠 보내고, TP로 보낼 수 있는 최대 크기는 1,785바이트(255 × 7)다.
- TP 프레임은 두 종류다. 연락용 TP.CM(PGN 60416)은 Byte 1의 Control Byte로 종류를 가른다. 운반용 TP.DT(PGN 60160)는 Byte 1이 시퀀스 번호(1~255), 나머지 7바이트가 데이터이고, 마지막 패킷의 빈자리는 0xFF로 채운다.
- BAM은 버스 전체에 방송하는 방식이다. TP.CM_BAM → TP.DT 순서로 보내고, 패킷 간격은 10~200 ms이며, 응답과 재전송이 없다.
- CMDT는 한 상대와의 1:1 연결이다. RTS → CTS → TP.DT → EndOfMsgACK 순서이고, CTS로 흐름을 조절하며 놓친 패킷을 다시 받을 수 있다.
- 기다림이 한도를 넘거나 문제가 생기면 Abort(Control Byte 0xFF)를 사유 코드와 함께 보내 연결을 끝낸다.
:::

::: details 확인 문제
1. (개념) 30바이트짜리 데이터를 TP로 보내면 TP.DT 패킷은 몇 개가 필요한가? 마지막 패킷에는 실제 데이터가 몇 바이트, `FF`가 몇 개 들어가는가?
2. (개념) 어떤 장치가 버스에 있는 모든 장치에게 자기 제품 정보를 알리려 한다. BAM과 CMDT 중 무엇이 알맞은가? 그때 받는 쪽은 무엇을 보내는가?
3. (개념) TP.DT 프레임만 보고는 어떤 PGN의 데이터인지 알 수 없다. 수신 측은 어디를 보고 그 PGN을 아는가?
4. (디코딩) TP.CM 프레임의 데이터가 `10 2C 00 07 05 DA FE 00`이다. 어떤 메시지이고, 총 크기, 총 패킷 수, CTS 하나가 허락할 수 있는 최대 패킷 수, 나르는 PGN은 각각 얼마인가? 이 RTS에 대한 첫 CTS의 패킷 수는 최대 몇인가?
5. (적용) CMDT에서 송신 측이 RTS를 보냈는데 수신 측이 아무 대답도 하지 않는다. 송신 측은 얼마나 기다린 뒤 무엇을 보내는가?

**답 가이드**
1. 30 ÷ 7 = 4.28…을 올림해 5개다. 앞의 4개에 7바이트씩 28바이트가 들어가므로, 마지막 패킷에는 데이터 2바이트와 `FF` 5개가 들어간다.
2. BAM이다. 받는 쪽은 아무것도 보내지 않는다(확인 응답 없음).
3. 그 전에 받은 TP.CM(BAM 또는 RTS)의 Byte 6~8이다. 이 PGN이 뒤따르는 TP.DT 조각들의 PGN이다.
4. Control Byte `0x10`(=16)이므로 RTS다. 총 크기 `2C 00` = 44바이트, 총 패킷 수 `07` = 7개(44 ÷ 7을 올림), CTS당 최대 패킷 수 `05` = 5개, PGN `DA FE 00` = `0x00FEDA` = 65242(Software identification, 소프트웨어 식별 정보)다. 첫 CTS의 패킷 수는 7과 5 중 작은 값인 5를 넘을 수 없다.
5. 1250 ms(T3)를 기다린 뒤 Abort를 보낸다. 사유 코드는 3(타임아웃)이다.
:::

## 다음 챕터

- 다음: [16장 TP 연결 규칙과 타이머](/study/isobus/16-tp-connection-rules)
