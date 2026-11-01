---
title: "DDOP 전송 명령과 설계 점검"
description: "Device descriptor 명령의 하위 명령 14개로 DDOP를 묻고 올리고 활성화하는 과정을 바이트로 따라가고, 런타임 변경 규칙과 설계 규칙 점검표로 7섹션 살포기의 DDOP를 점검해 고친다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, TaskController, TC, DDOP, SectionControl, ObjectPool]
prev: /study/isobus/49-ddop-bytes
next: /study/isobus/51-file-server-basics
---

# DDOP 전송 명령과 설계 점검

::: info 학습 목표
- Device descriptor 명령(Command 1)의 하위 명령 14개가 각각 무엇을 하는지 구분할 수 있다.
- 라벨 질의, 전송, 활성화로 이어지는 DDOP 업로드 흐름을 바이트로 따라갈 수 있다.
- Activate Response 8바이트를 읽고 활성화 실패 원인을 찾을 수 있다.
- DDOP를 다시 올리지 않고 바꿀 수 있는 것과 다시 올려야 하는 것을 구분할 수 있다.
- 설계 규칙으로 섹션 제어용 DDOP에서 빠진 오브젝트를 찾아 고칠 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [48장 DDOP 기초](/study/isobus/48-ddop-basics), [49장 DDOP 바이트 구성](/study/isobus/49-ddop-bytes), [43장 TC 연결 관리](/study/isobus/43-tc-connection)
- 이 장에서 처음 나오는 말
  - 하위 명령: Device descriptor 명령 안에서 할 일을 고르는 4비트 번호
  - 활성화(activate): 올라온 DDOP를 TC가 실제로 쓰기 시작하게 하는 일
  - 휘발성 메모리: 전원이 꺼지면 내용이 지워지는 메모리
  - FMIS: 사무실 컴퓨터에서 도는 농장 관리 프로그램. TC와 작업 데이터를 파일로 주고받는다
  - TC-SC: 섹션을 위치에 맞춰 자동으로 켜고 끄는 TC 기능
  - 런타임 변경: 연결이 이어진 상태에서 DDOP 내용을 바꾸는 일
:::

관공서 민원 창구를 떠올려 보자. "예전에 낸 서류 확인", "새 서류 접수", "접수한 서류로 처리 시작", "서류 폐기", "서류의 이름 고치기"처럼 창구마다 할 일이 정해져 있다. DDOP를 TC에 올리는 일도 이렇게 할 일이 나뉜 14개의 하위 명령으로 이루어진다. 이 장의 앞부분에서는 그 하위 명령들을 바이트로 따라가고, 뒷부분에서는 제출한 서류, 곧 DDOP가 규칙에 맞는지 점검표로 확인한다.

## 1. Device descriptor 하위 명령 한눈에

[48장 6절](/study/isobus/48-ddop-basics)에서는 하위 명령 3개(0000·0110·1000)만 봤다. Command 1의 하위 명령은 14개이고, 모두 기본 우선순위 5다. 우선순위는 CAN ID 맨 앞 3비트에 담기는 값으로, 숫자가 작을수록 버스에서 먼저 나간다([9장](/study/isobus/09-j1939-message)). C→T는 클라이언트 → TC/DL, T→C는 그 반대다. DL(Data Logger)은 기록만 맡는 TC 비슷한 장치다.

표 읽는 법은 다음과 같다.

- 하위 명령은 4비트 2진수다. Byte 1은 그 하위 명령 뒤에 Command 1(`0001`)을 이어 붙인 첫 바이트를 16진수로 쓴 것이다.
- 길이는 메시지 전체 바이트 수다. "8~40"처럼 범위로 적힌 메시지는 경우에 따라 길이가 다르고, 8바이트를 넘으면 TP로 보낸다.
- "나머지 바이트"는 Byte 2부터의 내용이다. `FF`는 쓰지 않는 바이트를 채우는 값이고, v4는 버전 4에서 생긴 내용이다. 버전은 TC 표준의 판에 따른 기능 수준이고, TC와 클라이언트는 연결할 때 서로의 버전을 확인한다([43장](/study/isobus/43-tc-connection)).

| 하위 명령 | Byte 1 | 메시지 | 방향 | 길이 | 나머지 바이트 |
|---|---|---|---|---|---|
| 0000 | `01` | Request Structure Label | C→T | 8~40 | 2~8 라벨(모두 `FF`면 최신 라벨 질의), 9~ extended(v4, TP) |
| 0001 | `11` | Structure Label | T→C | 8~40 | 2~8 라벨, 9~ extended. 없으면 7바이트 `FF` 단일 프레임 |
| 0010 | `21` | Request Localization Label | C→T | 8 | 2~8 라벨(모두 `FF`면 최신 질의) |
| 0011 | `31` | Localization Label | T→C | 8 | 2~8 라벨. 없으면 모두 `FF` |
| 0100 | `41` | Request Object-pool Transfer | C→T | 8 | 2~5 전송 크기(바이트), 6~8 `FF` |
| 0101 | `51` | Request Object-pool Transfer Response | T→C | 8 | 2 상태: 0 메모리가 충분할 수 있음, 1 부족(전송 금지). 3~8 `FF` |
| 0110 | `61` | Object-pool Transfer | C→T | 가변 | 2~n 오브젝트 레코드 |
| 0111 | `71` | Object-pool Transfer Response | T→C | 8 | 2 오류: 0 정상, 1 전송 중 메모리 소진, 2 기타. 3~6 받은 크기, 7~8 `FF` |
| 1000 | `81` | Object-pool Activate/Deactivate | C→T | 8 | 2: `FF` activate, `00` deactivate(v4). 3~8 `FF` |
| 1001 | `91` | Object-pool Activate/Deactivate Response | T→C | 8 | 아래 표 |
| 1010 | `A1` | Object-pool Delete | C→T | 8 | 2~8 `FF` |
| 1011 | `B1` | Object-pool Delete Response | T→C | 8 | 2 오류(0/1), 3 상세(v4): 0 태스크 데이터가 참조 중, 1 참조 확인 불가, `FF` 상세 없음. 4~8 `FF` |
| 1100 | `C1` | Change Designator | C→T | 가변 | 2~3 Object ID, 4 길이(0~128), 5~n UTF-8 |
| 1101 | `D1` | Change Designator Response | T→C | 8 | 2~3 Object ID, 4 오류(0/1), 5~8 `FF` |

하위 명령 1110과 1111은 표준에 정의돼 있지 않다.

한 행을 예로 읽어 보자. Request Object-pool Transfer(`41`)는 클라이언트가 보내는 8바이트 메시지다. Byte 2~5에 보낼 크기를 바이트 단위로 적고, Byte 6~8은 `FF`로 채운다. [49장 8절](/study/isobus/49-ddop-bytes)의 `41 A3 00 00 00 FF FF FF`가 바로 이 메시지다(크기 163바이트).

::: details 원문을 가진 독자를 위한 메모
B.6.13(Delete Response)의 원문 표는 "Bytes 2 to 8: Error code", "Byte 2: Error detail", "Byte 3: 0 = …" 순으로 적혀 한 줄씩 밀린 것처럼 보인다. 상세 바이트에 붙은 각주가 "버전 4에서 정의됐고 버전 3까지는 `FF`로 보냈다"고 말하므로, Byte 2를 오류 코드, Byte 3을 상세로 읽는 것이 맞다(추론). B.6.7도 상태 값 1 앞에 "Bytes 6 to 8"이 잘못 붙어 있는데, Byte 2 상태 값으로 읽는다. [Part 10 정리](/study/isobus/appendix-iso-part10)도 같은 해석이다. 이 장의 하위 명령 표는 이 해석을 따른다.
:::

<small>근거: ISO 11783-10 B.2, B.6</small>

## 2. 라벨 질의와 전송: 업로드 흐름 따라가기

이 절에서는 클라이언트가 라벨을 묻고 DDOP를 보내는 과정을 하위 명령 단위로 따라간다. 먼저 전체 흐름을 그림으로 본다.

![Device descriptor 하위 명령으로 본 DDOP 업로드 판단 흐름. Request Structure Label에 7 x FF가 오면 Request Object-pool Transfer로, 라벨이 맞으면 Localization Label을 확인하고, 그것도 맞으면 바로 Activate로 간다. 전송 경로는 상태 0일 때 Object-pool Transfer와 Transfer Response 0을 거쳐 Activate로 이어지고, Activate Response byte 2가 0이 아니면 TC가 풀을 지운다](/images/study-isobus/20-ddop-upload-flow-light.png)
![Device descriptor 하위 명령으로 본 DDOP 업로드 판단 흐름. Request Structure Label에 7 x FF가 오면 Request Object-pool Transfer로, 라벨이 맞으면 Localization Label을 확인하고, 그것도 맞으면 바로 Activate로 간다. 전송 경로는 상태 0일 때 Object-pool Transfer와 Transfer Response 0을 거쳐 Activate로 이어지고, Activate Response byte 2가 0이 아니면 TC가 풀을 지운다](/images/study-isobus/20-ddop-upload-flow-dark.png)

그림 읽는 법: 파란 상자는 클라이언트가 보내는 요청이고, 초록 상자는 TC의 응답이다. 상자 안 두 자리 16진수는 Byte 1이다. 화살표 옆 글자는 그 길로 가는 조건이다. 맨 위 줄이 라벨 질의, 가운데 줄이 전송, 맨 아래 줄이 활성화다.

### 라벨 질의: 무엇을 묻고 무엇을 고르나

- Request Structure Label의 바이트 2~8을 모두 `FF`로 보내면 "TC에 있는 최신 DDOP의 라벨"을 묻는다. 버전 3 이하의 방식이고 버전 4에서도 통한다.
- 특정 라벨을 넣어 보내면 그 라벨의 DDOP가 있는지 묻는다. 있으면 같은 라벨이, 없으면 `FF` 7바이트가 돌아온다. extended label까지 넣으면 8바이트를 넘으므로 TP를 쓴다.
- 업로드 없이 Activate를 보내면 TC는 마지막으로 성공 응답한 Structure Label 요청의 DDOP를 활성화한다. 구성이 여러 개인 장치는 라벨 질의로 "어느 구성을 쓸지"를 고르는 셈이다.
- 표준은 "DDOP가 이미 있는지 조회하라"고만 적는다. structure label이 맞은 뒤 localization label까지 확인하는 순서는 흔히 쓰는 구성일 뿐 표준이 강제하는 순서는 아니다(추론).

예를 들어 49장의 살포기가 자기 라벨 `SPRY3-V`가 TC에 있는지 물으면 `01 53 50 52 59 33 2D 56`을 보낸다. `01`이 Request Structure Label이고, 나머지 7바이트가 ASCII `SPRY3-V`다. TC에 없으면 `11 FF FF FF FF FF FF FF`가 돌아온다.

### 전송: 크기 확인, 분할, 응답

- Request Object-pool Transfer Response의 0은 "충분할 수도 있다"는 뜻이다. 오브젝트 저장 오버헤드(저장할 때 덧붙는 관리용 공간) 때문에 TC도 확답하지 못한다. 그래서 전송 도중 메모리가 바닥나는 경우(Transfer Response 1)가 따로 있다.
- Object-pool Transfer는 여러 메시지로 나눠도 되지만, 메시지 하나하나가 완전한 오브젝트 기술이어야 한다. 레코드 중간에서 자르면 안 된다.
- Transfer Response의 바이트 3~6(받은 크기)은 클라이언트가 보낸 크기와 맞춰 보는 데 쓴다.

49장 예제라면 정상 Transfer Response는 `71 00 A3 00 00 00 FF FF`다. 오류 0, 받은 크기 163(=`0xA3`)바이트라는 뜻이다.

<small>근거: ISO 11783-10 6.6.2 i, B.6.2, B.6.3, B.6.7, B.6.8, B.6.10</small>

## 3. 활성화 응답 읽기

이 절에서는 활성화를 요청했을 때 TC가 돌려주는 Activate Response를 읽는다. 활성화가 실패하면 그 원인이 모두 이 8바이트에 들어 있다.

표 읽는 법: Byte 2와 Byte 7은 비트셋이다. 비트 번호는 가장 낮은 자리가 bit 1이다([48장 5절](/study/isobus/48-ddop-basics)). Byte 3~4와 Byte 5~6은 Object ID를 리틀 엔디언으로 적은 칸이고, 오류가 없으면 NULL(`FF FF`)이 들어간다.

| 위치 | 내용 |
|---|---|
| Byte 2 | bit 1 = DDOP에 오류(Byte 3~7 참조), bit 2 = 활성화 중 메모리 부족, bit 3 = 기타 오류, bit 4 = 같은 structure label의 다른 DDOP가 이미 있어 활성화하지 않음(v4), bit 5~8 = 0 |
| Byte 3~4 | 오류 오브젝트의 부모 Object ID(오류 없으면 NULL) |
| Byte 5~6 | 오류 오브젝트의 Object ID(오류 없으면 NULL) |
| Byte 7 | bit 1 = TC/DL이 지원하지 않는 method·attribute, bit 2 = 모르는 오브젝트 참조(누락), bit 3 = 기타 오류, bit 4 = DDOP를 휘발성 메모리에서 삭제함, bit 5~8 = 0 |
| Byte 8 | `FF` |

![Activate Response 8바이트를 칸으로 그린 그림. Byte 1은 91, Byte 2는 오류 비트(bit 1 DDOP 오류, bit 2 메모리 부족, bit 3 기타, bit 4 같은 라벨의 다른 DDOP), Byte 3~4는 부모 Object ID, Byte 5~6은 오류 Object ID, Byte 7은 풀 오류 비트(bit 1 지원 안 하는 method·attribute, bit 2 모르는 오브젝트 참조, bit 3 기타, bit 4 휘발성 메모리에서 삭제), Byte 8은 FF다. 아래 줄에 정상 응답 91 00 FF FF FF FF 00 FF와 오류 예 91 01 03 00 08 00 09 FF를 칸마다 나란히 적었다](/images/study-isobus/50-activate-response-bytes-light.png)
![Activate Response 8바이트를 칸으로 그린 그림. Byte 1은 91, Byte 2는 오류 비트(bit 1 DDOP 오류, bit 2 메모리 부족, bit 3 기타, bit 4 같은 라벨의 다른 DDOP), Byte 3~4는 부모 Object ID, Byte 5~6은 오류 Object ID, Byte 7은 풀 오류 비트(bit 1 지원 안 하는 method·attribute, bit 2 모르는 오브젝트 참조, bit 3 기타, bit 4 휘발성 메모리에서 삭제), Byte 8은 FF다. 아래 줄에 정상 응답 91 00 FF FF FF FF 00 FF와 오류 예 91 01 03 00 08 00 09 FF를 칸마다 나란히 적었다](/images/study-isobus/50-activate-response-bytes-dark.png)

정상 응답은 `91 00 FF FF FF FF 00 FF`다. Byte 2가 `00`이라 오류 비트가 없고, Byte 3~6이 모두 `FF`라 오류 오브젝트도 없다. Byte 7도 `00`이다.

표준이 정한 동작은 네 가지다.

- 활성화 때 어떤 종류든 오류로 답하면 TC/DL은 그 DDOP를 휘발성 메모리에서 지운다. 사유는 운전자에게 알릴 수 있다.
- FMIS 파일 세트에 이미 있는 device descriptor를 클라이언트가 활성화하지 못하면 그 클라이언트와의 통신을 이어 가지 않는다.
- 오류가 있는 device descriptor는 MICS → FMIS 파일 세트에 쓰지 않는다. MICS(Mobile Implement Control System)는 트랙터와 작업기 쪽에서 TC를 포함해 작업을 수행하는 시스템이다.
- deactivate에 대한 정상 응답은 최대 2 s 안에 와야 한다.

예를 들어 `91 01 03 00 08 00 09 FF`(예시)는 "DET 3 아래의 DPD 8에 TC가 지원하지 않는 method·attribute가 있어 DDOP를 지웠다"로 읽는다. 단계별로 풀면 다음과 같다.

1. Byte 1 `91`: Activate/Deactivate Response다.
2. Byte 2 `01`: bit 1만 섰다. DDOP에 오류가 있으니 Byte 3~7을 보라는 뜻이다.
3. Byte 3~4 `03 00`: 오류 오브젝트의 부모는 Object 3(DET 3)이다.
4. Byte 5~6 `08 00`: 오류 오브젝트는 Object 8(DPD 8)이다.
5. Byte 7 `09`: 9 = 8 + 1이므로 bit 4와 bit 1이 섰다. TC가 지원하지 않는 method·attribute(오브젝트에 적힌 기능이나 속성)가 있었고(bit 1), 그래서 DDOP를 휘발성 메모리에서 지웠다(bit 4).

Byte 2 bit 4는 structure label 관리 실수를 잡는다. 구조를 바꾸고도 라벨을 그대로 두면 TC에 남아 있는 같은 라벨의 다른 DDOP 때문에 활성화가 거부된다. 표준은 structure label이 element·오브젝트 번호 체계까지 포함한 관계를 "영구히" 유일하게 기술하도록 하는 것을 클라이언트 책임으로 둔다.

<small>근거: ISO 11783-10 B.6.11, 8.7</small>

## 4. 삭제, 이름 바꾸기, TC 처리 표시 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

### 삭제와 designator 변경

- Delete는 그 클라이언트가 정의한 DDOP만 지운다. FMIS에서 받은 DDOP는 영향을 받지 않는다.
- 로그 데이터나 태스크 할당이 그 DDOP를 참조하면 TC가 지우지 못할 수 있다. 버전 3까지는 이때 Delete Response로 답할지 PDACK로 거부할지가 불분명했다. 버전 4부터는 모든 Delete에 Delete Response로 답해야 하고, 상세 바이트로 이유를 밝힌다.
- Change Designator는 Object ID와 새 designator(사람이 읽을 이름)를 보낸다. 길이 바이트는 UTF-8 바이트 수(0~128, 최대 32자)다. DET 3의 이름을 `좌측 섹션`으로 바꾸면 17바이트라 TP로 나간다.

```
C1 03 00 0D EC A2 8C EC B8 A1 20 EC 84 B9 EC 85 98   Change Designator, Object 3, 13 B
D1 03 00 00 FF FF FF FF                               Change Designator Response, 오류 0
```

Change Designator 17바이트를 풀면 다음과 같다.

1. `C1`: 하위 명령 `1100`과 Command 1을 이어 붙인 Change Designator다.
2. `03 00`: 이름을 바꿀 오브젝트는 Object 3이다.
3. `0D`: 새 이름은 13바이트다.
4. 나머지 13바이트는 `좌측 섹션`의 UTF-8이다. `EC A2 8C`가 좌, `EC B8 A1`이 측, `20`이 공백, `EC 84 B9`가 섹, `EC 85 98`이 션이다.

응답 `D1 03 00 00 FF FF FF FF`는 Object 3의 이름 변경에 오류가 없다(Byte 4가 0)는 뜻이다.

### TC가 처리 중임을 알리는 방법

TC는 Device descriptor 명령을 처리하는 동안 TC Status 메시지의 Byte 5 bit 4를 세우고, Byte 6에 대상 클라이언트 SA(Source Address, 보낸 장치의 버스 주소)를, Byte 7에 처리 중인 명령의 Byte 1을 싣는다. 클라이언트는 이 값으로 TC가 자기 DDOP를 처리하고 있는지 알 수 있다. TC Status의 나머지 필드와 주기는 [43장](/study/isobus/43-tc-connection)에서 다룬다.

::: details 파이썬으로 검산해 보기: 하위 명령과 Activate Response
`dd(sub)`는 하위 명령을 받아 Byte 1을 만든다. 코드는 하위 명령별 메시지를 만들어 바이트를 출력하고, `decode_activate_response`로 Activate Response를 풀어 본다.

```python
FF = lambda n: b"\xFF" * n
dd = lambda sub: bytes([(sub << 4) | 0x1])          # Command 1 + 하위 명령 니블
hexs = lambda b: b.hex(" ").upper()

LABEL, EXT = b"SPRY3-V", b"1.0"
LOC = bytes.fromhex("65 6E 00 00 00 00 FF")
POOL_SIZE = 163

msgs = {
    "Request Structure Label (최신)": dd(0x0) + FF(7),
    "Request Structure Label (특정, v3 호환)": dd(0x0) + LABEL,
    "Request Structure Label (확장 포함, v4, TP)": dd(0x0) + LABEL + EXT,
    "Structure Label (없음)": dd(0x1) + FF(7),
    "Request Localization Label": dd(0x2) + LOC,
    "Localization Label (있음)": dd(0x3) + LOC,
    "Request Object-pool Transfer": dd(0x4) + POOL_SIZE.to_bytes(4, "little") + FF(3),
    "Request Object-pool Transfer Response (0)": dd(0x5) + b"\x00" + FF(6),
    "Object-pool Transfer Response (0)": dd(0x7) + b"\x00" + POOL_SIZE.to_bytes(4, "little") + FF(2),
    "Object-pool Activate": dd(0x8) + b"\xFF" + FF(6),
    "Object-pool Deactivate": dd(0x8) + b"\x00" + FF(6),
    "Activate Response (정상)": dd(0x9) + b"\x00" + FF(4) + b"\x00" + FF(1),
    "Object-pool Delete": dd(0xA) + FF(7),
    "Object-pool Delete Response (참조 중)": dd(0xB) + b"\x01\x00" + FF(5),
}
name = "좌측 섹션".encode("utf-8")
msgs["Change Designator (DET 3)"] = dd(0xC) + (3).to_bytes(2, "little") + bytes([len(name)]) + name
msgs["Change Designator Response (0)"] = dd(0xD) + (3).to_bytes(2, "little") + b"\x00" + FF(4)

for k, v in msgs.items():
    print(f"{k:44s} {len(v):2d}B  {hexs(v)}")

assert hexs(msgs["Request Object-pool Transfer"]) == "41 A3 00 00 00 FF FF FF"
assert hexs(msgs["Activate Response (정상)"]) == "91 00 FF FF FF FF 00 FF"
assert hexs(msgs["Change Designator (DET 3)"]) == "C1 03 00 0D EC A2 8C EC B8 A1 20 EC 84 B9 EC 85 98"


def decode_activate_response(m):
    assert m[0] == 0x91
    b2 = ["pool에 오류(Byte 3~7 참조)", "활성화 중 메모리 부족", "기타 오류",
          "같은 structure label의 다른 DDOP가 이미 있음(v4)"]
    b7 = ["TC/DL이 지원하지 않는 method·attribute", "모르는 오브젝트 참조(누락)",
          "기타 오류", "풀을 휘발성 메모리에서 삭제함"]
    oid = lambda lo: int.from_bytes(m[lo:lo + 2], "little")
    return dict(errors=[t for i, t in enumerate(b2) if m[1] >> i & 1] or ["정상"],
                parent=oid(2), faulty=oid(4),
                pool_errors=[t for i, t in enumerate(b7) if m[6] >> i & 1])


print(decode_activate_response(bytes.fromhex("91 01 03 00 08 00 09 FF")))
print(decode_activate_response(bytes.fromhex("91 08 FF FF FF FF 00 FF")))
```
```
Request Structure Label (최신)                  8B  01 FF FF FF FF FF FF FF
Request Structure Label (특정, v3 호환)           8B  01 53 50 52 59 33 2D 56
Request Structure Label (확장 포함, v4, TP)      11B  01 53 50 52 59 33 2D 56 31 2E 30
Structure Label (없음)                          8B  11 FF FF FF FF FF FF FF
Request Localization Label                    8B  21 65 6E 00 00 00 00 FF
Localization Label (있음)                       8B  31 65 6E 00 00 00 00 FF
Request Object-pool Transfer                  8B  41 A3 00 00 00 FF FF FF
Request Object-pool Transfer Response (0)     8B  51 00 FF FF FF FF FF FF
Object-pool Transfer Response (0)             8B  71 00 A3 00 00 00 FF FF
Object-pool Activate                          8B  81 FF FF FF FF FF FF FF
Object-pool Deactivate                        8B  81 00 FF FF FF FF FF FF
Activate Response (정상)                        8B  91 00 FF FF FF FF 00 FF
Object-pool Delete                            8B  A1 FF FF FF FF FF FF FF
Object-pool Delete Response (참조 중)            8B  B1 01 00 FF FF FF FF FF
Change Designator (DET 3)                    17B  C1 03 00 0D EC A2 8C EC B8 A1 20 EC 84 B9 EC 85 98
Change Designator Response (0)                8B  D1 03 00 00 FF FF FF FF
{'errors': ['pool에 오류(Byte 3~7 참조)'], 'parent': 3, 'faulty': 8, 'pool_errors': ['TC/DL이 지원하지 않는 method·attribute', '풀을 휘발성 메모리에서 삭제함']}
{'errors': ['같은 structure label의 다른 DDOP가 이미 있음(v4)'], 'parent': 65535, 'faulty': 65535, 'pool_errors': []}
```

출력 위쪽은 하위 명령별 메시지와 길이다. 마지막 두 줄은 3절의 오류 예 `91 01 03 00 08 00 09 FF`와, Byte 2 bit 4만 선 `91 08 FF FF FF FF 00 FF`를 푼 결과다.
:::

<small>근거: ISO 11783-10 B.6.12~B.6.15, B.8.1</small>

## 5. 런타임 변경: 무엇을 바꿀 수 있고 무엇은 다시 올려야 하나

이 절에서는 연결이 이어진 상태에서 DDOP 내용을 바꾸고 싶을 때 무엇을 해야 하는지 본다. 바꾸려는 것이 무엇이냐에 따라 방법이 다섯 가지로 갈린다. 주민등록 정보에 빗대면, 이름 표기를 고치는 것은 정정 신청 한 번이면 되지만 가족 구성이 바뀌면 서류를 새로 내야 하는 것과 같다.

| 바꾸려는 것 | 방법 |
|---|---|
| 오브젝트 이름(designator) | Change Designator |
| 언어·측정 단위 | DVC(structure label 그대로, localization label만 갱신)와 DVP 오브젝트만 다시 전송 |
| DPD로 정의한 값(오프셋·지연 등) | Process Data 메시지로 변경. 연결 중·태스크 중에도 가능 |
| DPT로 정의한 값 | 새 device descriptor 업로드 |
| 그 밖의 구조(element·DPD 추가, DDI 변경 등) | deactivate → 새 structure label로 DDOP 전체 전송 → activate |

예를 들어 운전자가 측정 단위를 미터법에서 다른 단위계로 바꾸면, 클라이언트는 structure label은 그대로 두고 localization label만 새 값으로 바꾼 DVC와, 새 단위를 담은 DVP들만 다시 보낸다. 버스로 오가는 원시값은 바뀌지 않는다([49장 7절](/study/isobus/49-ddop-bytes)).

- 런타임 갱신 시점에 제한은 없지만, 태스크가 active인 동안은 최대한 피해야 한다.
- 갱신 중 오류가 나면 TC는 Activate Response에 오류를 표시하고, 갱신 이전 것까지 포함해 DDOP 전체를 휘발성 메모리에서 지운다. 알람 같은 방식으로 운전자에게 알릴 수 있다.
- 같은 DDI를 한 element에 DPT와 DPD로 동시에 넣으면 안 된다. 오프셋·시간 지연·용량 같은 파라미터는 둘 중 하나로만 정의한다.
- 클라이언트는 내부 값을 올바른 운영값으로 초기화한 뒤에 DDOP를 활성화해야 한다. 활성화 직후 TC가 지오메트리(위치와 크기 값)를 물을 수 있기 때문이다. [45장](/study/isobus/45-tc-process-data-basics)에서 다뤘다.

DPT와 DPD의 선택은 이 표로 정해진다. 기계 수명 동안 안 변하는 값(connector type 등)은 DPT, 구성 변경으로 바뀔 수 있는 지오메트리는 DPD가 낫다. DPT로 둔 값을 바꾸려면 structure label을 바꿔 전체를 다시 올려야 하기 때문이다.

::: details 원문을 가진 독자를 위한 메모
이 절 표의 근거 조항이다.

| 바꾸려는 것 | 방법 | 근거 |
|---|---|---|
| 오브젝트 이름(designator) | Change Designator | 8.7, B.6.14 |
| 언어·측정 단위 | DVC(structure label 그대로, localization label만 갱신)와 DVP 오브젝트만 다시 전송 | 8.7 |
| DPD로 정의한 값(오프셋·지연 등) | Process Data 메시지로 변경. 연결 중·태스크 중에도 가능 | 8.7 |
| DPT로 정의한 값 | 새 device descriptor 업로드 | 8.7 |
| 그 밖의 구조(element·DPD 추가, DDI 변경 등) | deactivate → 새 structure label로 DDOP 전체 전송 → activate | 8.7 |
:::

<small>근거: ISO 11783-10 8.7, B.6.14, 6.8, F.3.4.2</small>

## 6. DDOP 설계 규칙 점검표 (심화)

::: info 처음 읽는다면
이 절은 직접 DDOP를 설계할 때 필요한 규칙 전체다. 처음에는 건너뛰고 7절로 가도 된다. 7절에서 7섹션 살포기에 걸리는 규칙만 골라 풀어 본다.
:::

표준 여러 곳에 흩어진 설계 규칙을 한곳에 모은다. 표준은 예시 DDOP와 함께 설계 규칙을 정의하고, 예시를 변형해 구현할 때도 이 규칙을 따라야 한다고 못 박는다. 여러 기능성을 지원하는 장치는 각 기능성 예시의 속성을 합친 집합을 담아야 한다.

기능성 이름은 다음과 같다. TC-BAS는 작업 총계를 기록하는 기본 기능, TC-GEO는 위치에 따라 처방 맵의 값을 보내는 기능, TC-SC는 섹션을 위치에 맞춰 켜고 끄는 기능이다. TC 기능성 자체의 정의와 서버 요건은 [41장](/study/isobus/41-tc-basics)과 [44장](/study/isobus/44-tc-multi-dl-functionality)에서 다룬다. 규칙마다 7절에서 부를 번호를 붙였다.

### 구조

| # | 규칙 |
|---|---|
| S1 | DVC는 정확히 1개, Object ID 0 |
| S2 | type 1(device) DET는 정확히 1개, element number 0, 부모는 DVC(0) |
| S3 | Object ID는 풀 전체에서 유일, 참조 없음은 `0xFFFF` |
| S4 | DET가 참조하는 것은 DPD·DPT뿐. DET 계층은 자식의 Parent ObjectId로 만든다 |
| S5 | DPD·DPT는 여러 DET가, DVP는 여러 DPD·DPT가 함께 참조할 수 있다 |
| S6 | 한 element에 같은 DDI를 DPT와 DPD로 동시에 넣지 않는다 |
| S7 | ClientNAME은 그 CF의 address claim NAME과 같다 |

### element 번호와 지오메트리

| # | 규칙 |
|---|---|
| G1 | 같은 타입·같은 계층의 element 번호는 좌→우, 앞→뒤, 위→아래 오름차순. 행렬 배치는 좌→우부터 센다 |
| G2 | 위치 기반 제어에서는 element 오프셋·치수 값이 번호보다 우선한다 |
| G3 | 좌표는 DRP(0,0,0) 기준 오른손 좌표계: x는 주행 방향, y는 오른쪽, z는 아래(지면 쪽)가 양수 |
| G4 | DRP는 트랙터면 뒷차축 중심, 바퀴 달린 작업기면 앞차축 중심, 그 밖에는 자유 |
| G5 | connector는 DRP와 같은 위치(0,0,0)라도 x·y·z 지오메트리를 DPD나 DPT로 제공한다 |
| G6 | navigation reference도 x·y·z 위치를 제공한다 |
| G7 | connector·navigation element는 루트(DET-0) 바로 아래에만 두고 X·Y 오프셋과 connector type 정의를 갖는다(표준은 두 element를 한 문장에 함께 묶어 적는다) |

DRP(Device Reference Point)는 장치의 위치를 잴 때 기준이 되는 점이다. G1의 행렬 배치는 섹션이 앞뒤 여러 줄로 놓인 경우를 말한다.

### 섹션 제어(TC-SC)용 붐

| # | 규칙 |
|---|---|
| C1 | 붐은 Function 또는 루트(Device) 타입 element이고, 붐 하나가 커버리지 레이어 하나다 |
| C2 | 붐에 141 Actual Work State. on change와 time interval 지원 필수(TC-GEO는 Change Threshold 지원 요구) |
| C3 | 섹션 작업 상태는 161·290(Condensed)으로만 다룬다. Section element 안에 141·289를 두지 않는다 |
| C4 | 161은 on change·time interval 필수, 290은 on change 권장 |
| C5 | 160 Section Control State는 290과 같은 레벨에 settable + on change로 둔다. TC-SC가 불가능한 붐에는 두지 않는다 |
| C6 | 붐에 Offset X·Y와 working width. 붐 지오메트리를 섹션에서 유도하지 않는다 |
| C7 | Section마다 working width를 최소 1종 둔다. 여럿이면 67 → 70 → 68 순으로 쓴다 |
| C8 | Section의 67은 그 섹션 상태와 무관하고, 붐 레벨 67은 On인 섹션 폭의 합이다 |
| C9 | 한 붐의 Section은 겹침·틈 없이 정확히 한 줄로 놓인다 |
| C10 | 부모가 Offset X를 가지면 Section은 Offset X를 생략할 수 있다(유일한 예외) |
| C11 | 신규 설계는 붐에 205·206(SC Turn On/Off Time)을 settable + on change로 둔다 |
| C12 | 지오메트리 DPD에는 on change 권장, TC는 기동 때 지오메트리를 질의한다 |

커버리지 레이어는 "이미 뿌린 곳"을 지도에 칠하는 층이다. 붐 하나마다 따로 칠한다. Change Threshold는 값이 정한 만큼 바뀌었을 때 보고하는 트리거, 곧 on change의 다른 이름이다.

### rate 제어와 총계

| # | 규칙 |
|---|---|
| R1 | 루트에 119 Total Time(TC-BAS 필수) |
| R2 | rate DDI가 있으면 대응 total DDI도 제공하고, total은 actual rate와 같은 element에 둔다 |
| R3 | 같은 rate DDI를 루트와 Bin에, Function과 Bin에, 루트와 붐 Function에 동시에 두지 않는다 |
| R4 | 붐에 setpoint가 있으면 같은 레벨에 158(settable + on change)과 대응하는 actual을 둔다 |
| R5 | Function이 붐이면 actual·setpoint·Offset X·Y·최대 폭·158을 모두 그 Function에 둔다. 루트에는 actual work state 말고는 actual·setpoint 값을 두지 않는다 |
| R6 | 붐이 여럿이면 179 Actual Cultural Practice를 붐 Function이나 그 아래 Bin에 둔다 |
| R7 | 178 Element Type Instance는 Bin 안에 둔다 |
| R8 | 같은 DDI의 setpoint source와 user를 한 장치가 겸하면 element를 둘로 나눈다 |

rate는 단위 면적이나 단위 시간당 뿌리는 양(살포량)이다. setpoint source와 user는 Peer Control에서 값을 대 주는 쪽과 받는 쪽이다([47장](/study/isobus/47-tc-totals-logging-peer)).

::: details 원문을 가진 독자를 위한 메모
위 점검표의 규칙별 근거 조항이다. 표마다 위에서부터 S1~S7, G1~G7, C1~C12, R1~R8 순서다.

| 규칙 | 근거 |
|---|---|
| DVC는 정확히 1개, Object ID 0 | A.2, A.7 |
| type 1(device) DET는 정확히 1개, element number 0, 부모는 DVC(0) | A.3.1, 8.7 |
| Object ID는 풀 전체에서 유일, 참조 없음은 `0xFFFF` | A.1 |
| DET가 참조하는 것은 DPD·DPT뿐. DET 계층은 자식의 Parent ObjectId로 만든다 | A.3 |
| DPD·DPT는 여러 DET가, DVP는 여러 DPD·DPT가 함께 참조할 수 있다 | A.7 |
| 한 element에 같은 DDI를 DPT와 DPD로 동시에 넣지 않는다 | 8.7 |
| ClientNAME은 그 CF의 address claim NAME과 같다 | A.2 |

| 규칙 | 근거 |
|---|---|
| 같은 타입·같은 계층의 element 번호는 좌→우, 앞→뒤, 위→아래 오름차순. 행렬 배치는 좌→우부터 센다 | B.3.2 |
| 위치 기반 제어에서는 element 오프셋·치수 값이 번호보다 우선한다 | B.3.2, F.3.5.2 |
| 좌표는 DRP(0,0,0) 기준 오른손 좌표계: x는 주행 방향, y는 오른쪽, z는 아래(지면 쪽)가 양수 | 8.7 |
| DRP는 트랙터면 뒷차축 중심, 바퀴 달린 작업기면 앞차축 중심, 그 밖에는 자유 | 8.7 |
| connector는 DRP와 같은 위치(0,0,0)라도 x·y·z 지오메트리를 DPD나 DPT로 제공한다 | A.3.6 |
| navigation reference도 x·y·z 위치를 제공한다 | A.3.7 |
| connector·navigation element는 루트(DET-0) 바로 아래에만 두고 X·Y 오프셋과 connector type 정의를 갖는다(원문은 둘을 함께 묶어 적는다) | F.3.4.2, F.3.5.4 |

| 규칙 | 근거 |
|---|---|
| 붐은 Function 또는 루트(Device) 타입 element이고, 붐 하나가 커버리지 레이어 하나다 | F.3.1 |
| 붐에 141 Actual Work State. on change와 time interval 지원 필수(TC-GEO는 Change Threshold 지원 요구) | F.3.5.1, F.3.4.1 |
| 섹션 작업 상태는 161·290(Condensed)으로만 다룬다. Section element 안에 141·289를 두지 않는다 | F.3.5.1 |
| 161은 on change·time interval 필수, 290은 on change 권장 | F.3.5.1 |
| 160 Section Control State는 290과 같은 레벨에 settable + on change로 둔다. TC-SC가 불가능한 붐에는 두지 않는다 | F.3.5.3 |
| 붐에 Offset X·Y와 working width. 붐 지오메트리를 섹션에서 유도하지 않는다 | F.3.4.2, F.3.5.4 |
| Section마다 working width를 최소 1종 둔다. 여럿이면 67 → 70 → 68 순으로 쓴다 | F.3.5.2 |
| Section의 67은 그 섹션 상태와 무관하고, 붐 레벨 67은 On인 섹션 폭의 합이다 | F.3.5.2 |
| 한 붐의 Section은 겹침·틈 없이 정확히 한 줄로 놓인다 | F.3.5.2 |
| 부모가 Offset X를 가지면 Section은 Offset X를 생략할 수 있다(유일한 예외) | F.3.5.4 |
| 신규 설계는 붐에 205·206(SC Turn On/Off Time)을 settable + on change로 둔다 | F.3.5.5 |
| 지오메트리 DPD에는 on change 권장, TC는 기동 때 지오메트리를 질의한다 | F.3.4.2, F.3.5.4 |

| 규칙 | 근거 |
|---|---|
| 루트에 119 Total Time(TC-BAS 필수) | F.2.1, F.3.3 |
| rate DDI가 있으면 대응 total DDI도 제공하고, total은 actual rate와 같은 element에 둔다 | F.3.3 |
| 같은 rate DDI를 루트와 Bin에, Function과 Bin에, 루트와 붐 Function에 동시에 두지 않는다 | F.3.3 |
| 붐에 setpoint가 있으면 같은 레벨에 158(settable + on change)과 대응하는 actual을 둔다 | F.3.4.4 |
| Function이 붐이면 actual·setpoint·Offset X·Y·최대 폭·158을 모두 그 Function에 둔다. 루트에는 actual work state 말고는 actual·setpoint 값을 두지 않는다 | F.3.4.5 |
| 붐이 여럿이면 179 Actual Cultural Practice를 붐 Function이나 그 아래 Bin에 둔다 | F.3.3 |
| 178 Element Type Instance는 Bin 안에 둔다 | F.3.3 |
| 같은 DDI의 setpoint source와 user를 한 장치가 겸하면 element를 둘로 나눈다 | F.3.3 |

점검표는 8.7, Annex A, Annex F.3에 흩어진 규칙을 모은 것이다. Annex F.3은 예시 풀과 함께 설계 규칙을 정의하고, 변형을 구현할 때도 이 규칙을 따라야 한다고 적는다. 여러 기능성의 속성 집합을 합쳐야 한다는 규칙도 F.3에 있다.
:::

<small>근거: ISO 11783-10 8.7, Annex A, Annex F.2~F.3, B.3.2</small>

## 7. 49장의 7섹션 DDOP를 규칙으로 점검하고 고치기

이 절에서는 6절의 점검표로 [49장 1절](/study/isobus/49-ddop-bytes)의 7섹션 살포기 설계를 검사한다. 걸리는 곳은 일곱 군데다. 49장 설계는 총계(TC-BAS)·섹션 제어(TC-SC)·지오메트리를 목표로 했다. 그런데 붐에 setpoint rate(DDI 1)를 두었으니 처방 맵 rate 제어(TC-GEO) 규칙도 함께 적용된다. 여러 기능성을 지원하면 속성 집합을 합쳐야 하기 때문이다.

| # | 걸린 규칙 | 49장 설계의 상태 | 고칠 내용 |
|---|---|---|---|
| 1~3 | connector는 X·Y 오프셋과 connector type을 갖는다(G5, G7) | Element 1에 속성 없음 | DPT 134·135·157 추가 |
| 4~5 | 붐은 Offset X·Y를 갖고, 지오메트리를 섹션에서 유도하지 않는다(C6, R5) | 붐(Element 3)의 지오메트리 속성은 70뿐 | 붐에 DPT 134·135 추가 |
| 6 | setpoint가 있는 붐은 같은 레벨에 158을 둔다(R4) | 158 없음 | DPD 158(settable, on change) 추가 |
| 7 | rate DDI의 total은 actual rate와 같은 element에(R2) | 2(actual rate)는 붐에, total은 루트의 116·117·119뿐 | 붐에 rate 총계 DPD 추가 |

쉬운 말로 풀면 다음과 같다.

- 1~3: 작업기를 트랙터에 매다는 지점(connector)이 어디에 있고 어떤 종류의 연결인지 알려야 TC가 작업기 위치를 계산할 수 있다.
- 4~5: 붐 자체의 앞뒤 위치(X)와 좌우 위치(Y)를 붐에 직접 적어야 한다. 섹션 위치로부터 TC가 거꾸로 짐작하게 두면 안 된다.
- 6: 158(Prescription Control State)은 처방에 따른 살포량 제어를 켜고 끄는 스위치다. TC는 살포량 명령을 보내기 전에 이 스위치를 켠다([47장](/study/isobus/47-tc-totals-logging-peer)).
- 7: 살포량(rate)을 다루는 element는 그 누적 총량(total)도 함께 알려야 한다.

7번에는 표준이 살포기(Sprayers) 분류에 권장하는 총계(80·116·117·119) 가운데 아직 없는 DDI 80을 붙였다. DDI 80의 이름과 단위는 ISO 11783-10에도, 이 블로그의 [DDI 부록](/study/isobus/appendix-ddi)에도 없어서 ISOBUS 온라인 데이터 사전에서 확인해야 한다(확인 필요). 총계이고 TC가 시작값을 정해야 하므로 settable + total로 둔다([47장](/study/isobus/47-tc-totals-logging-peer)).

권장 사항 두 가지도 반영한다.

- <strong>섹션 on/off 지연</strong>: 신규 설계는 붐에 205·206을 settable + on change로 둔다(C11). 섹션을 켜고 끄라는 명령이 실제로 반영되기까지는 시간(제어 지연)이 걸린다. 그래서 TC-SC 서버는 이 시간만큼 섹션 on/off 명령을 앞당겨 보낸다. 클라이언트는 보고한 시간과 다르게 타이밍을 바꾸면 안 된다. 켜는 시간과 끄는 시간은 달라도 된다. 섹션에 142(Physical Setpoint Time Latency, 명령이 실제로 반영되기까지 걸리는 시간)만 있는 옛 방식이면 서버가 142로 앞당기되 on/off 지연을 구분하지 못한다. 205·206과 142가 함께 있으면 섹션 제어 명령에서는 142를 무시한다.
- <strong>섹션 오브젝트 줄이기</strong>: 붐이 Offset X를 가지면 섹션은 Offset X를 생략할 수 있다(C10). 섹션 폭 1,714 mm는 일곱 섹션이 같으므로 DPT 하나를 일곱 DET가 함께 참조한다(S5). Offset Z(136)는 TC-SC 최소 지오메트리(Offset X·Y·폭)에 들지 않아 이 예에서는 뺐다.

![규칙을 반영해 고친 7섹션 DDOP. 루트(element 0)에 총계 119·116·117, connector(element 1)에 DPT 134·135·157, bin(element 2), Function 붐(element 3)에 DPD 1·2·158·141·161·290·160·205·206·80과 DPT 70·134·135, 섹션 7개(element 11~17)에 DPT 70·135가 붙는다](/images/study-isobus/20-sc-ddop-tree-light.png)
![규칙을 반영해 고친 7섹션 DDOP. 루트(element 0)에 총계 119·116·117, connector(element 1)에 DPT 134·135·157, bin(element 2), Function 붐(element 3)에 DPD 1·2·158·141·161·290·160·205·206·80과 DPT 70·134·135, 섹션 7개(element 11~17)에 DPT 70·135가 붙는다](/images/study-isobus/20-sc-ddop-tree-dark.png)

그림 읽는 법: 큰 상자는 DET이고, 상자 안 작은 칩은 그 DET가 참조하는 DPD·DPT다. 칩 위 숫자가 DDI다. 칩 색은 왼쪽 아래 범례대로 settable DPD, 읽기 전용 DPD, DPT를 나타낸다.

고친 풀은 DVC 1 + DET 11 + DPD 13 + DPT 14 + DVP 2 = 41개 오브젝트다. 49장의 52개보다 11개 적다. DPT가 29개에서 14개로 줄어든 덕분이다. 섹션 DPT는 공유하는 70 하나와 섹션마다 다른 135 일곱 개다. 개수를 나눠 세면 다음과 같다.

| 종류 | 개수 | 내역 |
|---|---|---|
| DPD | 13 | 루트 3(119·116·117) + 붐 10(1·2·158·141·161·290·160·205·206·80) |
| DPT | 14 | connector 3(134·135·157) + 붐 3(70·134·135) + 섹션 8(공유 70 1개 + 135 7개) |

::: details 파이썬으로 검산해 보기: 규칙 점검기
아래 코드는 DDOP를 "element 번호 → (type, 부모, DDI 목록)" 사전으로 적고, 점검표 규칙 몇 가지를 검사하는 `check` 함수를 돌린다. 49장 설계(`original`)에서는 일곱 개가 걸리고, 고친 설계(`fixed`)에서는 하나도 걸리지 않는지 확인한다. 코드 안 괄호 속 조항 번호는 표준 문서의 위치다.

```python
# element number -> (type, parent element, {DDI: "S" settable DPD | "R" 읽기 전용 DPD | "P" DPT})
DEVICE, FUNCTION, BIN, SECTION, CONNECTOR = 1, 2, 3, 4, 6
WIDTH = {67, 70, 68}
TOTAL_OF_RATE = {2: 80}      # Table F.1 Sprayers 권장 총계 80 (DDI 이름은 온라인 사전에서 확인)


def check(ddop, boom):
    errs = []
    root = [n for n, (t, _, _) in ddop.items() if t == DEVICE]
    if root != [0]:
        errs.append("type 1(device) element는 정확히 1개, number 0 (A.3.1)")
    if 119 not in ddop[0][2]:
        errs.append("루트에 DDI 119 total time 필요 (F.2.1)")
    for n, (t, parent, a) in ddop.items():
        if t == CONNECTOR:
            if parent != 0:
                errs.append(f"el {n}: connector는 루트 바로 아래 (F.3.4.2)")
            for ddi in (134, 135, 157):
                if ddi not in a:
                    errs.append(f"el {n}: connector에 {ddi} 없음 (F.3.4.2·F.3.5.4)")
        if t == SECTION:
            for ddi in (141, 289):
                if ddi in a:
                    errs.append(f"el {n}: section 안의 개별 work state {ddi} 금지 (F.3.5.1)")
            if not WIDTH & a.keys():
                errs.append(f"el {n}: section에 working width 없음 (F.3.5.2)")
            if 135 not in a or (134 not in a and 134 not in ddop[parent][2]):
                errs.append(f"el {n}: section offset 부족 (F.3.5.4)")
    _, _, b = ddop[boom]
    for ddi in (134, 135):
        if ddi not in b:
            errs.append(f"붐 el {boom}: offset {ddi} 없음 (F.3.4.2)")
    if not WIDTH & b.keys():
        errs.append(f"붐 el {boom}: working width 없음 (F.3.4.2)")
    if 1 in b and 158 not in b:
        errs.append(f"붐 el {boom}: setpoint rate가 있으면 158 필요 (F.3.4.4)")
    for rate, total in TOTAL_OF_RATE.items():
        if rate in b and total not in b:
            errs.append(f"붐 el {boom}: rate {rate}의 총계 DDI {total}이 같은 element에 없음 (F.3.3)")
    for ddi in (160, 161, 290):
        if ddi not in b:
            errs.append(f"붐 el {boom}: TC-SC 붐에 {ddi} 없음 (F.3.5.1·F.3.5.3)")
    return errs


sections = {10 + i: (SECTION, 3, {70: "P", 134: "P", 135: "P", 136: "P"}) for i in range(1, 8)}
original = {
    0: (DEVICE, None, {119: "S", 116: "S", 117: "S"}),
    1: (CONNECTOR, 0, {}),
    2: (BIN, 0, {}),
    3: (FUNCTION, 0, {1: "S", 2: "R", 141: "R", 161: "R", 290: "S", 160: "S", 70: "P"}),
    **sections,
}
fixed = dict(original)
fixed[1] = (CONNECTOR, 0, {134: "P", 135: "P", 157: "P"})
fixed[3] = (FUNCTION, 0, {**original[3][2], 158: "S", 205: "S", 206: "S", 80: "S",
                          134: "P", 135: "P"})
for n in range(11, 18):
    fixed[n] = (SECTION, 3, {70: "P", 135: "P"})

for e in check(original, boom=3):
    print("-", e)
assert len(check(original, boom=3)) == 7
assert check(fixed, boom=3) == []

# 오브젝트 수: 같은 값의 DPT는 여러 element가 한 오브젝트를 참조할 수 있다(A.7)
dpd = sum(v == "S" or v == "R" for _, _, a in fixed.values() for v in a.values())
section_dpt = 1 + 7                      # 공유 70(1,714 mm) 1개 + 섹션마다 다른 135 7개
dpt = 3 + 3 + section_dpt                # connector 3 + 붐 3
total = 1 + len(fixed) + dpd + dpt + 2   # DVC + DET + DPD + DPT + DVP
print("objects:", total, "(DET", len(fixed), "DPD", dpd, "DPT", dpt, ")")
assert total == 41
```
```
- el 1: connector에 134 없음 (F.3.4.2·F.3.5.4)
- el 1: connector에 135 없음 (F.3.4.2·F.3.5.4)
- el 1: connector에 157 없음 (F.3.4.2·F.3.5.4)
- 붐 el 3: offset 134 없음 (F.3.4.2)
- 붐 el 3: offset 135 없음 (F.3.4.2)
- 붐 el 3: setpoint rate가 있으면 158 필요 (F.3.4.4)
- 붐 el 3: rate 2의 총계 DDI 80이 같은 element에 없음 (F.3.3)
objects: 41 (DET 11 DPD 13 DPT 14 )
```

출력 일곱 줄이 위 표의 1~7번이고, 마지막 줄이 고친 풀의 오브젝트 수 41이다.
:::

### 이 DDOP로 오가는 섹션 제어 메시지

고친 DDOP가 활성화되면 TC-SC 서버와 클라이언트는 대략 다음 순서로 움직인다(측정을 거는 순서는 예시). 메시지 바이트 배치는 [45장](/study/isobus/45-tc-process-data-basics)과 같다.

1. 지오메트리를 DPD로 정의했다면 TC는 기동 때 그 값을 질의한다. 이 DDOP처럼 지오메트리가 모두 DPT면 질의나 변화 감시가 필요 없다.
2. TC가 160(Section Control State)에 on change measurement를 걸고, 161에 on change·time interval, 290에 on change를 건다.
3. TC가 160을 ENABLED/ON으로 설정한다. 클라이언트는 대응 work state를 안전 상태 값으로 리셋한다.
4. TC가 위치를 보고 205·206만큼 앞당겨 290(Setpoint Condensed Work State)을 element 3으로 보낸다.
5. 클라이언트는 290 갱신(on change 응답)과 161 갱신을 섹션 상태 변화가 시작되는 즉시 보낸다. 이 두 응답은 필수다.
6. 태스크가 멈추면 클라이언트는 스스로 160을 DISABLED/OFF로 둔다.

measurement 명령은 TC가 "이 조건이 되면 값을 보내라"고 거는 명령이다([46장](/study/isobus/46-tc-commands-pdack)). ENABLED/ON 같은 상태가 어떤 정수인지는 ISOBUS 데이터 사전이 정한다.

작업 상태는 element 계층을 따라 합쳐서 판정한다. 상위 element의 141이 Off면 섹션이 On이어도 TC-SC 서버는 Off로 처리한다. 붐의 141이 그 작업의 마스터 작업 스위치다.

::: details 원문을 가진 독자를 위한 메모
이 절 표의 근거 조항이다.

| # | 걸린 규칙 | 49장 설계의 상태 | 고칠 내용 | 근거 |
|---|---|---|---|---|
| 1~3 | connector는 X·Y 오프셋과 connector type을 갖는다 | Element 1에 속성 없음 | DPT 134·135·157 추가 | F.3.4.2, F.3.5.4, A.3.6 |
| 4~5 | 붐은 Offset X·Y를 갖고, 지오메트리를 섹션에서 유도하지 않는다 | 붐(Element 3)의 지오메트리 속성은 70뿐 | 붐에 DPT 134·135 추가 | F.3.4.2, F.3.4.5 |
| 6 | setpoint가 있는 붐은 같은 레벨에 158을 둔다 | 158 없음 | DPD 158(settable, on change) 추가 | F.3.4.4 |
| 7 | rate DDI의 total은 actual rate와 같은 element에 | 2(actual rate)는 붐에, total은 루트의 116·117·119뿐 | 붐에 rate 총계 DPD 추가 | F.3.3, Table F.1 |

DDI 80은 Table F.1의 Sprayers 행에서 왔고, settable + total은 6.8.3을 따랐다. 섹션 on/off 지연은 F.3.5.5, 섹션 Offset X 생략은 F.3.5.4, DPT 공유는 A.7이다. 메시지 순서는 F.3.5.1·F.3.5.3·F.3.5.5, 지오메트리 질의는 F.3.5.4와 F.3.5, 계층 판정은 F.3.5.1이다.
:::

<small>근거: ISO 11783-10 F.3, F.3.3, F.3.4.2~F.3.4.5, F.3.5.1~F.3.5.5, Table F.1, A.3.6, A.7, 6.8.3</small>

::: tip 핵심 정리
- DDOP 관리는 Process Data 메시지의 Command 1 아래 하위 명령 14개로 이루어진다. Byte 1의 앞자리 16진수가 하위 명령, 뒷자리 1이 Command다.
- 클라이언트는 라벨을 물어 TC에 같은 DDOP가 있는지 확인하고, 없으면 크기를 알린 뒤 레코드를 보내고, 마지막에 Activate로 활성화한다.
- Activate Response의 Byte 2·Byte 7 비트와 부모·오류 Object ID로 실패 원인을 찾는다. 활성화 오류가 나면 TC는 그 DDOP를 지운다.
- 이름은 Change Designator로, 언어·단위는 DVC와 DVP 재전송으로, DPD 값은 Process Data로 바꾼다. DPT 값이나 구조를 바꾸려면 다시 올려야 한다.
- 섹션 제어용 DDOP는 붐에 Condensed Work State(161·290), Section Control State(160), 오프셋과 폭을 두고, connector에 위치와 종류를 둔다.
:::

::: details 확인 문제
1. (개념) Request Object-pool Transfer Response의 상태 0은 "메모리가 충분하다"는 확답인가? 그렇게 보는 이유는 무엇인가?
2. (구분) 다음을 바꾸려면 어떻게 해야 하나? (a) DET 3의 이름 (b) 표시 단위 (c) 섹션 폭을 담은 DPT 값 (d) 섹션 하나 추가
3. (읽기) Activate 뒤에 `91 08 FF FF FF FF 00 FF`가 돌아왔다. 무슨 뜻이고, 클라이언트는 무엇을 고쳐야 하나?
4. (디코딩) DDOP를 올리고 Activate를 보냈더니 `91 01 05 00 0C 00 02 FF`가 돌아왔다. 무엇이 문제이고, 지금 TC 메모리에는 무엇이 남아 있나? 다음에 무엇을 보내야 하나?
5. (버전 협상) 버전 4 클라이언트가 structure label `AB12CD3`, extended structure label `2026-10`을 쓴다. 버전 3 TC와 버전 4 TC에 보낼 Request Structure Label 바이트를 각각 적고, DVC 레코드의 끝이 어떻게 달라지는지 설명하라.
6. (설계) 48장 4절의 설계(섹션마다 DDI 289)를 TC-SC용으로 고치려 한다. 무엇을 빼고, 무엇을 어느 element에 더하는가?

**답 가이드**
1. 아니다. 0은 "충분할 수도 있다"는 뜻이다. 오브젝트를 저장할 때 덧붙는 관리 공간 때문에 TC도 확답하지 못한다. 그래서 전송 도중 메모리가 바닥났다는 Transfer Response 1이 따로 있다.
2. (a) Change Designator (b) structure label은 그대로 두고 localization label만 바꾼 DVC와 DVP만 다시 보낸다 (c) 새 device descriptor를 올린다 (d) deactivate → 새 structure label로 DDOP 전체 전송 → activate
3. Byte 2가 `08`, 곧 bit 4만 섰다. 같은 structure label의 다른 DDOP가 TC에 이미 있어 활성화하지 않았다는 뜻이다(버전 4). 오류 오브젝트는 없다(NULL). 구조를 바꿨는데 라벨을 그대로 둔 경우이므로, 바뀐 구조에 새 structure label을 붙여 다시 올린다.
4. Byte 2 bit 1(DDOP에 오류), 부모 Object 5, 오류 오브젝트 12, Byte 7 bit 2(모르는 오브젝트 참조, 누락)다. 오브젝트 12가 풀에 없는 DPD·DPT·DVP를 참조한다. 활성화 오류이므로 TC는 이 DDOP를 휘발성 메모리에서 지웠다(3절). 참조를 고치거나 빠진 오브젝트를 넣고, 바꾼 구조에 맞는 새 structure label로 Request Object-pool Transfer → Object-pool Transfer → Activate를 다시 진행한다.
5. 버전 3 TC에는 `01 41 42 31 32 43 44 33`(8바이트)을 보내고, DVC 레코드는 localization label에서 끝난다(extended 바이트 수·라벨 없음). 버전 4 TC에는 `01 41 42 31 32 43 44 33 32 30 32 36 2D 31 30`(15바이트, TP)을 보내고, DVC 레코드 끝에 `07 32 30 32 36 2D 31 30`이 붙는다([49장 5절](/study/isobus/49-ddop-bytes), 이 장 2절). 버전 3 TC와는 7바이트 라벨만으로 구성을 구별해야 한다.
6. 섹션에서 289(와 141)를 뺀다. 붐 역할인 루트(48장 4절의 DET 2)에 141(on change·time interval), 161(on change·time interval), 290(on change 권장), 160(settable·on change)을 더한다. 붐에 Offset X·Y와 폭, 섹션마다 폭(67·70·68 중 하나)과 Offset Y를 두고, 붐에 Offset X가 있으면 섹션의 Offset X는 생략해도 된다. 루트 바로 아래 connector element에 134·135·157을 두고, 신규 설계라면 205·206도 붐에 둔다.
:::

## 다음 챕터

- 다음: [51장 File Server(FS) 기초](/study/isobus/51-file-server-basics)
