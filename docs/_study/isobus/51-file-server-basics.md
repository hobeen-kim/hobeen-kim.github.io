---
title: "File Server(FS) 기초"
description: "ISOBUS 버스 위의 공용 파일 창고인 File Server가 파일을 정리하는 방식과, 클라이언트가 파일을 열고 읽고 닫을 때 지키는 순서와 시간 규칙을 익힌다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, FileServer, TAN]
prev: /study/isobus/50-ddop-commands-design
next: /study/isobus/52-file-server-details
---

# File Server(FS) 기초

::: info 학습 목표
- File Server가 ISOBUS에서 맡는 일과, 파일을 볼륨·디렉터리·파일 3단계로 정리하는 방식을 설명할 수 있다.
- 클라이언트가 FS에 연결해 파일을 열고, 읽고, 닫기까지 주고받는 메시지 순서를 말할 수 있다.
- 메시지의 Byte 1(명령 그룹과 함수)과 Byte 2(TAN)를 읽고, Open File 요청과 응답을 바이트 단위로 풀어 읽을 수 있다.
- TAN이 응답을 잃었을 때 같은 명령이 두 번 실행되는 사고를 어떻게 막는지 설명할 수 있다.
- 2초 연결 유지, 600 ms 요청 타임아웃, 6초 연결 끊김 규칙으로 클라이언트의 재시도 동작을 정할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [9장 J1939 메시지 구조](/study/isobus/09-j1939-message), [15장 Transport Protocol 기초](/study/isobus/15-tp-bam-cmdt), [41장 TC 기초](/study/isobus/41-tc-basics)
- 이 장에서 처음 나오는 말
  - File Server(FS): 버스 위의 다른 장치에게 파일 저장 공간을 빌려주는 장치
  - 클라이언트: FS에 파일 작업을 요청하는 장치. TC, VT, 작업기 ECU 등 누구나 될 수 있다
  - 볼륨(Volume): FS 안의 저장 매체 하나에 붙은 이름. 컴퓨터의 C: 드라이브나 USB 드라이브에 해당한다
  - Handle: 파일을 열면 FS가 내주는 번호표. 이후 읽기, 쓰기, 닫기는 이 번호로 파일을 가리킨다
  - TAN(Transaction Number): 요청마다 붙이는 일련번호. 응답이 어느 요청의 것인지 맞추는 데 쓴다
:::

트랙터 운전석 단말기에 USB 메모리가 꽂혀 있다고 해 보자. 작업기 ECU에는 USB 단자가 없지만, 버스를 거쳐 그 메모리를 빌려 쓸 수 있다면 처방 맵을 받아 오거나 작업 기록을 남기기가 훨씬 쉬워진다. ISOBUS에서 이런 공용 파일 창고 역할을 하는 장치가 File Server(FS)다. [50장](/study/isobus/50-ddop-commands-design)까지 TC와 작업기가 메시지로 데이터를 주고받는 법을 봤다면, 이 장과 [52장](/study/isobus/52-file-server-details)에서는 데이터를 파일로 맡기고 꺼내는 법을 본다.

## 1. File Server란: 버스 위의 공용 파일 창고

이 절에서는 FS가 무엇이고 왜 필요한지, 버스에서 어떤 메시지 번호로 대화하는지 본다.

ECU(Electronic Control Unit, 전자 제어 장치)마다 저장 장치를 따로 달면 비용이 들고, 장치끼리 파일을 주고받기도 번거롭다. ISO 11783-13(File Server를 정하는 표준 문서)은 저장 공간을 한곳에 두고 버스로 빌려 주는 방법을 정한다.

<strong>File Server(FS)</strong>는 ISOBUS 네트워크 위에서 파일을 저장하고 공유하는 서비스를 제공하는 독립 ECU이다. ECU끼리 USB 메모리 같은 별도 물리 매체를 옮겨 꽂지 않고도 파일을 주고받을 수 있고, 자체 저장소가 없는 ECU도 네트워크 공용 저장소를 쓸 수 있다. FS에 파일 작업을 요청하는 쪽은 <strong>클라이언트</strong>라고 부른다.

::: info 비유가 맞지 않는 곳
도입의 "단말기에 꽂힌 USB 메모리"는 이해를 돕는 그림이다. 실제 표준과 다른 점이 두 가지 있다.
- FS가 꼭 운전석 단말기 안에 있을 필요는 없다. 표준은 FS를 버스 위의 독립 ECU로 정하고, 저장 매체도 USB에 한정하지 않는다. 내부 플래시, 이동식 매체, 견고형 디스크를 모두 쓸 수 있다.
- 클라이언트는 매체를 직접 읽지 않는다. "이 파일을 열어 달라", "여기서 100바이트 읽어 달라"는 요청 메시지를 FS에 보내고, FS가 처리한 결과를 응답 메시지로 받는다.
:::

주요 활용 사례:
- <strong>처방 맵(Prescription Map)</strong>: FMIS(Farm Management Information System, 사무실 PC에서 쓰는 영농 관리 프로그램)에서 생성한 처방 맵(구역마다 뿌릴 양을 정한 지도)을 TC로 전달
- <strong>작업 로그(Task Log / As-Applied Map)</strong>: TC가 기록한 실제 살포 데이터를 FMIS로 회수
- <strong>공용 저장소</strong>: 대용량 데이터를 다루는 ECU가 자체 저장 장치 없이 네트워크 저장소를 활용

![File Server 큰 그림: TC, VT, 작업기 ECU 같은 클라이언트가 PGN 0xAA00으로 요청하고 FS가 PGN 0xAB00으로 응답하며, FS는 File Server Status를 전역으로 방송하고, FS 안에는 내부 저장소 FLASH와 이동식 매체 VOL_B 볼륨이 있는 구조](/images/study-isobus/51-fs-overview-light.png)
![File Server 큰 그림: TC, VT, 작업기 ECU 같은 클라이언트가 PGN 0xAA00으로 요청하고 FS가 PGN 0xAB00으로 응답하며, FS는 File Server Status를 전역으로 방송하고, FS 안에는 내부 저장소 FLASH와 이동식 매체 VOL_B 볼륨이 있는 구조](/images/study-isobus/51-fs-overview-dark.png)

그림처럼 클라이언트와 FS는 방향마다 하나씩, PGN(Parameter Group Number, 메시지의 종류를 가리키는 번호) 2개로 대화한다. 통신에는 이 두 PGN이 예약되어 있다.

| PGN | 방향 |
|-----|------|
| 43520 (0xAA00) | Client → FS |
| 43776 (0xAB00) | FS → Client |

- 두 PGN은 모두 destination-specific(받는 쪽 주소를 하나 정해 보내는) 메시지다. J1939 용어로는 PDU1 형식이라 CAN ID 안에 받는 쪽 주소가 들어간다([9장](/study/isobus/09-j1939-message) 참고).
- 기본 우선순위는 7이다. 우선순위는 0이 가장 높고 7이 가장 낮으므로, FS 메시지는 버스에서 가장 낮은 우선순위로 다닌다.
- CAN 프레임 하나에는 데이터가 8바이트까지 들어간다. 파일 경로가 든 요청이나 파일 데이터가 든 응답처럼 9바이트 이상인 메시지는 TP(Transport Protocol, 긴 데이터를 여러 프레임으로 나눠 보내는 규칙, [15장](/study/isobus/15-tp-bam-cmdt))나 ETP(Extended Transport Protocol, 1 785바이트보다 큰 데이터용, [17장](/study/isobus/17-etp))로 전송한다.

실제 CAN ID로 보면 어떻게 생겼는지 확인해 두자. 클라이언트 주소가 0x80(=128), FS 주소가 0x3A(=58)라고 하자(예시 주소). 요청은 `0x1CAA3A80`, 응답은 `0x1CAB803A`, File Server Status는 받는 쪽 주소(DA, Destination Address)가 전역 주소 0xFF(=255, 모든 장치)라 `0x1CABFF3A`다. 29비트 CAN ID를 16진수 8자리로 적으면, 앞에서부터 두 자리씩 끊어 읽을 수 있다.

| 메시지 | CAN ID | 끊어 읽기 |
|---|---|---|
| 요청 (클라이언트 → FS) | `0x1CAA3A80` | `1C` 우선순위 7(과 데이터 페이지 0), `AA` PGN 0xAA00, `3A` 받는 쪽 FS, `80` 보낸 쪽 클라이언트 |
| 응답 (FS → 클라이언트) | `0x1CAB803A` | `1C` 우선순위 7, `AB` PGN 0xAB00, `80` 받는 쪽 클라이언트, `3A` 보낸 쪽 FS |
| File Server Status (FS → 전역) | `0x1CABFF3A` | `1C` 우선순위 7, `AB` PGN 0xAB00, `FF` 받는 쪽 전체, `3A` 보낸 쪽 FS |

정리하면 FS는 버스 위의 공용 파일 창고이고, 클라이언트는 0xAA00으로 요청을 보내고 0xAB00으로 응답을 받는다.

::: details 원문을 가진 독자를 위한 메모
Part 13(2011)은 ETP를 ISO 11783-6 소관으로 인용하지만, 이 스터디가 근거로 쓴 판에서 ETP는 ISO 11783-3:2018 5.11에 정의돼 있다([19장](/study/isobus/19-isobus-part1-requirements)의 ETP 소관 차이 참고). Part 13의 5.1, 5.3.3, C.1.1에 나오는 "ISO 11783-6의 ETP" 인용이 모두 이 경우다.
:::

<small>근거: ISO 11783-13 4, 5.1, C.1.1</small>

## 2. 파일 계층 구조: 볼륨, 디렉터리, 파일

FS 안의 파일은 컴퓨터의 폴더처럼 층층이 정리된다. 이 절에서는 그 층의 이름과, 파일 위치를 경로로 적는 법을 본다.

쉽게 말하면 볼륨은 컴퓨터의 C: 드라이브나 USB 드라이브, 디렉터리는 폴더, 파일은 파일이다. File Server는 <strong>Volume → Directory → File</strong> 3단계 계층으로 파일을 관리한다.

- 볼륨(Volume): 저장 매체 하나(내부 플래시, 이동식 매체 등)에 붙은 이름이다. 볼륨도 맨 위의 디렉터리처럼 쓰인다.
- 디렉터리(Directory): 파일을 묶어 두는 폴더다. 디렉터리 안에 디렉터리를 또 둘 수 있다.
- 파일(File): 실제 데이터가 든 단위다.

경로 구분자는 `\`(백슬래시)이고, 최상위의 볼륨 목록은 `\\`로 지정한다. 윈도우 탐색기의 "내 PC"를 열면 드라이브 목록이 보이듯, `\\`를 열면 FS가 가진 볼륨들이 보인다. 아래 트리는 FLASH 볼륨 하나만 펼쳐 본 예다.

```
\\ (볼륨 목록, 최상위)
└── FLASH (Volume)
    ├── prescriptions (Directory)
    │   ├── prescription_map_2026.xml
    │   └── field_boundary.shp
    └── logs (Directory)
        ├── task_log_20260413.xml
        └── as_applied_20260413.bin
```

다음 그림은 이동식 매체 볼륨 VOL_B까지 함께 그린 전체 모습이다. 왼쪽에서 오른쪽으로 갈수록 한 층씩 내려간다.

![FS 파일 계층: File Server 아래에 내부 저장소 볼륨 FLASH와 이동식 매체 볼륨 VOL_B가 있고, FLASH 아래 prescriptions와 logs 디렉터리, 그 아래 처방 맵, 경계 파일, 작업 로그, 살포 기록 파일이 있는 트리](/images/study-isobus/51-fs-hierarchy-light.png)
![FS 파일 계층: File Server 아래에 내부 저장소 볼륨 FLASH와 이동식 매체 볼륨 VOL_B가 있고, FLASH 아래 prescriptions와 logs 디렉터리, 그 아래 처방 맵, 경계 파일, 작업 로그, 살포 기록 파일이 있는 트리](/images/study-isobus/51-fs-hierarchy-dark.png)

경로를 해석할 때 기준이 되는 말 세 가지를 먼저 정해 두자.

- <strong>current directory</strong>: FS가 클라이언트마다 기억해 두는 "지금 있는 디렉터리"다. 명령 창에서 `cd`로 옮겨 다니는 위치와 같다.
- current volume: current directory가 들어 있는 볼륨이다.
- primary volume: FS가 시작할 때 current volume으로 쓰는 기본 볼륨이다.

볼륨까지 포함한 절대 경로는 `\\FLASH\logs\task_log_20260413.xml` 형태다. 볼륨 이름 없이 쓴 경로는 클라이언트별 current directory 기준 상대 경로로 처리되고, `\` 하나로 시작하면 current volume의 루트 기준으로 처리된다. current directory가 `\\FLASH\logs\`일 때를 예로 들면 다음과 같다.

| 쓰는 법 | 기준 | 요청 경로 예 | FS가 찾는 위치 |
|---|---|---|---|
| `\\`와 볼륨 이름으로 시작 | 볼륨 목록(절대 경로) | `\\FLASH\logs\task_log_20260413.xml` | 적힌 그대로 |
| 볼륨 이름 없이 시작 | current directory | `task_log_20260413.xml` | `\\FLASH\logs\task_log_20260413.xml` |
| `\` 하나로 시작 | current volume의 루트 | `\prescriptions\prescription_map_2026.xml` | `\\FLASH\prescriptions\prescription_map_2026.xml` |

클라이언트가 연결되면 FS는 current directory를 primary volume의 루트로 초기화한다. 이름에 쓸 수 있는 글자, `..`과 `~` 같은 특수 이름은 [52장](/study/isobus/52-file-server-details)에서 본다.

정리하면 FS의 파일은 볼륨, 디렉터리, 파일 3층이고, 경로는 `\`로 층을 나누며 `\\`가 맨 위의 볼륨 목록이다.

<small>근거: ISO 11783-13 3.11, 5.5, 5.7, A.2.3.1</small>

## 3. 파일에 접근하는 흐름

클라이언트가 FS의 파일 하나를 읽거나 쓰려면 정해진 순서를 밟는다. 이 절에서는 그 순서를 처음부터 끝까지 따라가고, 순서마다 지켜야 할 규칙을 본다. 각 메시지의 바이트는 4절과 [52장](/study/isobus/52-file-server-details)에서 자세히 본다.

쉽게 말하면 도서관 이용과 비슷하다. 입구의 "운영 중" 안내판으로 도서관이 열려 있는지 보고, 이용 안내를 받고, 열람실에 있는 동안 주기적으로 출입증을 찍는다. 책을 대출하면 대출 번호(Handle)를 받고, 읽은 뒤 반납한다. 비유와 다른 점도 있다. 파일은 FS 밖으로 나가지 않고, 클라이언트는 "몇 바이트 읽어 달라"고 요청해 내용을 조금씩 받아 갈 뿐이다.

클라이언트(TC, VT 등)가 File Server에 접근하는 순서는 다음과 같다.

1. FS는 File Server Status를 모든 장치에 주기적으로 방송한다. 평소에는 2 s마다, 요청을 처리하느라 바쁠 때(busy)는 200 ms마다 보낸다. 클라이언트는 이 방송으로 FS가 살아 있는지, 바쁜지 안다.
2. 클라이언트가 Get File Server Properties를 보내면, FS가 버전, 최대 동시 열기 파일 수, 다중 볼륨 지원 여부를 답한다. Get File Server Properties는 연결 유지를 시작하기 전에도 보낼 수 있다.
3. 클라이언트는 FS와 일하는 동안 Client Connection Maintenance를 2 s 주기로 보낸다.
4. Open File 요청에 TAN, Flags(여는 방식), 경로를 담아 보낸다. 응답에는 TAN, 에러 코드(Error Code, 성공이면 0인 결과 번호), Handle, 속성(Attributes)이 온다.
5. Read File이나 Write File을 필요한 만큼 반복한다. 요청에는 TAN, Handle, 바이트 수가 들어가고, 응답에는 TAN, 에러 코드, 읽은 데이터나 실제로 처리한 바이트 수가 들어간다.
6. Close File 요청(TAN, Handle)으로 파일을 닫고, 응답(TAN, 에러 코드)으로 결과를 받는다.

![FS 접근 순서: FS가 File Server Status를 주기 방송하는 가운데, 클라이언트가 Get File Server Properties로 FS 정보를 받고, 2 s마다 Client Connection Maintenance를 보내며, Open File로 Handle을 받은 뒤 Read/Write File을 반복하고 Close File로 마무리하는 시퀀스](/images/study-isobus/51-fs-access-sequence-light.png)
![FS 접근 순서: FS가 File Server Status를 주기 방송하는 가운데, 클라이언트가 Get File Server Properties로 FS 정보를 받고, 2 s마다 Client Connection Maintenance를 보내며, Open File로 Handle을 받은 뒤 Read/Write File을 반복하고 Close File로 마무리하는 시퀀스](/images/study-isobus/51-fs-access-sequence-dark.png)

핵심 규칙:

- 클라이언트는 FS와 상호작용하는 동안 <strong>Client Connection Maintenance</strong> 메시지를 2 000 ms 주기로 보낸다. FS가 이 메시지를 <strong>6초</strong>간 못 받으면 그 클라이언트의 열린 파일을 모두 닫고 Handle을 무효화한다. 클라이언트가 정리 없이 버스에서 이탈해도(전원이 꺼지거나 커넥터가 빠져도) FS가 리소스를 회수하는 장치다.
- Read/Write 요청에는 오프셋(파일 안의 위치)이 없다. FS는 열린 파일마다 다음에 읽거나 쓸 위치인 <strong>파일 포인터</strong>를 기억하고, 읽거나 쓴 만큼 저절로 앞으로 옮긴다. 책갈피와 같다. 파일 내 위치 이동은 별도의 <strong>Seek File</strong> 명령으로 수행한다.
- 클라이언트는 응답을 받기 전에 다음 명령을 보내면 안 된다. File Server Status가 busy를 표시하지 않는데 600 ms 안에 응답이 없으면 실패로 간주하고 <strong>같은 TAN으로</strong> 재요청한다.
- FS는 클라이언트별 마지막 응답을 기억한다. 같은 TAN의 요청이 다시 오면 재전송으로 간주해 <strong>실행 없이</strong> 이전 응답만 다시 보낸다. 응답 유실 시 Read File 같은 명령이 두 번 실행되어 파일 포인터가 밀리는 사고를 막는 장치다. 이 동작은 5절에서 그림과 코드로 다시 본다.

정리하면 파일 하나를 다루는 흐름은 "상태 확인 → FS 정보 조회 → 연결 유지 시작 → Open → Read/Write → Close"이고, 그동안 요청은 한 번에 하나씩만 보낸다.

<small>근거: ISO 11783-13 5.3, C.1.1~C.1.5, C.3</small>

## 4. 메시지 한 개 읽기: Byte 1, TAN, Open File

FS 메시지는 모두 같은 틀로 시작한다. 이 절에서는 그 틀을 익히고, 파일을 여는 Open File 요청과 응답을 바이트 단위로 읽는다.

쉽게 말하면 Byte 1은 "부서 번호 + 업무 번호"다. ISO 11783-13 명령의 Byte 1은 상위 4비트가 커맨드 그룹(부서), 하위 4비트가 함수(그 부서의 업무)다. 그룹은 다섯 가지다.

| 상위 4비트 | 그룹 | 하는 일 |
|---|---|---|
| 0000 | Connection Management | FS 상태 방송, 연결 유지, FS 정보 조회, 볼륨 상태 |
| 0001 | Directory Handling | current directory 조회와 변경 |
| 0010 | File Access | 파일 열기, 위치 이동, 읽기, 쓰기, 닫기 |
| 0011 | File Handling | 파일 이동·복사, 삭제, 파일 속성 조회·변경, 날짜·시간 조회 |
| 0100 | Volume Handling | 볼륨 초기화 |

예를 들어 0x22(=34)는 2진수로 0010 0010이다. 상위 4비트 0010은 File Access 그룹, 하위 4비트 0010은 그 그룹의 2번 함수인 Read File이다. 모든 그룹의 함수 목록은 6절에 있다.

File Access 그룹(0010)의 함수 코드는 다음과 같고, <strong>요청과 응답이 같은 코드를 쓰며 방향(PGN)으로 구분</strong>된다. 이 그룹에서는 Byte 2에 항상 TAN이 들어간다. 표의 "요청 배치"와 "응답 배치"는 Byte 2부터 차례로 무엇이 오는지 적은 것이다. `(2B)`는 2바이트, `(4B)`는 4바이트를 차지한다는 뜻이고, 2바이트 이상인 수는 낮은 자리 바이트(LSB, Least Significant Byte)부터 보낸다.

| 명령 | Byte 1 | 요청 배치 (Byte 2~) | 응답 배치 (Byte 2~) |
|------|--------|--------------------|--------------------|
| Open File | 0x20 (32) | TAN, Flags, 경로 길이(2B), 경로 | TAN, 에러 코드, Handle, Attributes |
| Seek File | 0x21 (33) | TAN, Handle, Position Mode, Offset(4B) | TAN, 에러 코드, 예약(FF), 새 Position(4B) |
| Read File | 0x22 (34) | TAN, Handle, Count(2B) | TAN, 에러 코드, Count, Data |
| Write File | 0x23 (35) | TAN, Handle, Count(2B), Data | TAN, 에러 코드, 실제 쓴 Count |
| Close File | 0x24 (36) | TAN, Handle | TAN, 에러 코드 |

표에 나온 항목의 뜻은 다음과 같다.

- TAN: 0~255 범위의 1바이트 번호다. 클라이언트는 요청마다 직전 TAN에 1을 더해 붙이고, FS는 응답에 같은 TAN을 돌려준다.
- Flags: 파일을 여는 방식(읽기 전용, 쓰기 전용, 읽기·쓰기, 디렉터리 열기)과 옵션(없으면 만들기, 끝에 이어 쓰기, 혼자 열기)을 비트로 담은 1바이트다. 아래 코드의 `FLAG_` 상수가 그 비트들이다.
- Handle: FS가 열린 파일에 붙여 주는 번호(0~254)다. 255는 "Handle을 배정하지 못했다"는 뜻의 특수값이다.
- 에러 코드: 0이면 성공이다. 나머지 값의 뜻은 아래 코드의 `ERROR_CODES`에 있다.
- Attributes: 열린 대상의 성질(디렉터리인지, 읽기 전용인지, 볼륨이 긴 파일 이름을 지원하는지 등)을 비트로 담은 1바이트다.
- Count: 읽거나 쓸 바이트 수다. Position Mode와 Offset은 Seek File에서 "어디를 기준으로 몇 바이트 옮길지"를 정한다.

표는 핵심 자리만 추렸다. 예를 들어 Read File 요청에는 숨김 파일을 목록에 넣을지 정하는 Byte 6도 있는데, 디렉터리를 읽을 때 쓰는 자리라 [52장](/study/isobus/52-file-server-details)에서 본다.

아래는 Open File 요청 생성과 응답 파싱의 Python 예시이다. 요청을 바이트로 만드는 `build_open_file_request`와, 받은 응답 8바이트를 뜻으로 풀어내는 `parse_open_file_response`가 핵심이다. 파이썬의 `data[0]`이 표준의 Byte 1이다. 파이썬은 0부터 세고 표준은 1부터 센다는 점만 주의하면 된다.

```python
import struct

# ISO 11783-13 File Access group (command group 0b0010, Annex C)
# 요청과 응답은 같은 함수 코드를 쓰고, 방향(PGN)으로 구분한다.
FS_FUNC_OPEN_FILE  = 0x20  # 32: Open File
FS_FUNC_SEEK_FILE  = 0x21  # 33: Seek File
FS_FUNC_READ_FILE  = 0x22  # 34: Read File
FS_FUNC_WRITE_FILE = 0x23  # 35: Write File
FS_FUNC_CLOSE_FILE = 0x24  # 36: Close File

# Open File Flags (ISO 11783-13 B.14)
FLAG_READ_ONLY  = 0x00  # bits 1,0 = 00
FLAG_WRITE_ONLY = 0x01  # bits 1,0 = 01
FLAG_READ_WRITE = 0x02  # bits 1,0 = 10
FLAG_DIRECTORY  = 0x03  # bits 1,0 = 11 (디렉터리 열기)
FLAG_CREATE     = 0x04  # bit 2: 없으면 파일·디렉터리 생성
FLAG_APPEND     = 0x08  # bit 3: 파일 포인터를 파일 끝으로
FLAG_EXCLUSIVE  = 0x10  # bit 4: 배타적 접근 (이미 열려 있으면 실패)

# Error Codes (ISO 11783-13 B.9)
ERROR_CODES = {
    0:  "Success",
    1:  "Access Denied",
    2:  "Invalid Access",
    3:  "Too many files open",
    4:  "File, path or volume not found",
    5:  "Invalid Handle",
    6:  "Invalid given source name",
    7:  "Invalid given destination name",
    8:  "Volume out of free space",
    9:  "Failure during a write operation",
    10: "Media is not present",
    11: "Failure during a read operation",
    12: "Function not supported",
    13: "Volume is possibly not initialized",
    42: "Invalid request length",
    43: "Out of memory",
    44: "Any other error",
    45: "File pointer at end of file",
}


def parse_open_file_response(data: bytes) -> dict:
    """
    Parse an Open File Response (Byte 1 = 0x20, 8 bytes).
    Layout: [0]=FuncCode, [1]=TAN, [2]=ErrorCode, [3]=Handle,
            [4]=Attributes, [5..7]=reserved (0xFF)
    """
    if len(data) < 5:
        raise ValueError(f"Frame too short: {len(data)} bytes")

    func_code, tan, error_code, handle, attributes = data[:5]

    if func_code != FS_FUNC_OPEN_FILE:
        raise ValueError(f"Unexpected function code: 0x{func_code:02X}")

    success = error_code == 0 and handle != 0xFF  # Handle 255 = 배정 실패
    return {
        "function":   "Open File Response",
        "tan":        tan,
        "error":      ERROR_CODES.get(error_code, f"Reserved({error_code})"),
        "handle":     handle if success else None,
        "attributes": attributes,
        "success":    success,
    }


def build_open_file_request(tan: int, path: str, flags: int = FLAG_READ_ONLY) -> bytes:
    """
    Build an Open File Request (Byte 1 = 0x20).
    Layout: [0]=FuncCode, [1]=TAN, [2]=Flags,
            [3,4]=Path Name Length (LSB first), [5..n]=Path
    """
    path_bytes = path.encode("latin-1")  # ISO/IEC 8859-1 문자 집합
    header = bytes([FS_FUNC_OPEN_FILE, tan, flags])
    return header + struct.pack("<H", len(path_bytes)) + path_bytes


# Example usage
if __name__ == "__main__":
    # Simulate received Open File Response frame
    raw = bytes([0x20, 0x07, 0x00, 0x03, 0x20, 0xFF, 0xFF, 0xFF])
    result = parse_open_file_response(raw)
    print(f"Result : {result['error']} (TAN {result['tan']})")
    print(f"Handle : {result['handle']}")

    # Build a read-only open request (경로 구분자는 백슬래시)
    req = build_open_file_request(7, r"\\FLASH\prescriptions\prescription_map_2026.xml")
    print(f"Request: {req.hex()}")
```

실행하면 다음이 출력된다.

```text
Result : Success (TAN 7)
Handle : 3
Request: 2007002f005c5c464c4153485c707265736372697074696f6e735c707265736372697074696f6e5f6d61705f323032362e786d6c
```

응답 쪽부터 읽어 보자. 코드가 받은 응답 프레임 `20 07 00 03 20 FF FF FF`는 파서를 시험하려고 만든 예시 값이다. 바이트마다 풀면 다음과 같다.

| 바이트 | 값 | 뜻 |
|---|---|---|
| 1 | `20` | 0010 0000. File Access 그룹의 0번 함수, Open File의 응답이다 |
| 2 | `07` | TAN 7. 요청에 붙인 TAN과 같아야 한다 |
| 3 | `00` | 에러 코드 0, 성공 |
| 4 | `03` | Handle 3. 이후 Read File과 Close File에서 이 번호로 파일을 가리킨다 |
| 5 | `20` | Attributes 0x20(=0010 0000). bit 5만 1이고, 볼륨이 긴 파일 이름을 지원한다는 뜻이다. bit 4가 0이므로 디렉터리가 아닌 파일이다 |
| 6~8 | `FF FF FF` | 쓰지 않는 자리다. 8바이트보다 짧은 메시지는 남는 바이트를 0xFF로 채운다 |

Attributes의 비트는 1만 뜻이 있는 것이 아니다. 예를 들어 bit 6이 0이면 "이동식 볼륨"이라는 뜻이다. 비트 전체는 [52장](/study/isobus/52-file-server-details)의 파라미터 세부에 있다.

요청 쪽 출력 `2007002f00 5c5c...`는 앞에서부터 이렇게 끊어 읽는다.

1. `20`: Open File
2. `07`: TAN 7
3. `00`: Flags 0x00, 읽기 전용
4. `2f 00`: 경로 길이. 낮은 바이트가 먼저 오므로 0x002F = 47글자다
5. 나머지 47바이트: 경로 글자다. `5c`가 `\`, `46`이 `F`, `4c`가 `L`이다. 예제는 경로 글자를 1바이트 문자 집합인 ISO/IEC 8859-1(latin-1)로 바꾼다

이 Open File 요청은 8바이트를 넘으므로(5 + 47 = 52바이트) 단일 CAN 프레임이 아니라 TP로 전송된다.
클라이언트는 응답의 TAN이 요청의 TAN과 같은지 확인해 명령 유실 여부를 검증하고, 에러 코드가 0이 아니면 그 뒤의 파라미터(Handle 등)는 무시해야 한다. 실패한 응답의 Handle 자리에는 엉뚱한 값이 들어 있을 수 있기 때문이다.

정리하면 Byte 1로 무슨 명령인지, Byte 2의 TAN으로 어느 요청의 응답인지, 에러 코드로 성공 여부를 판단하고, 성공했을 때만 그 뒤의 값을 믿는다.

<small>근거: ISO 11783-13 B.1, B.2, B.8~B.10, B.14, B.15, C.3.3</small>

## 5. 전송 제어: 요청은 한 번에 하나, 타이밍은 여섯 가지

1~4절이 FS와 대화하는 큰 그림이었다면, 5~7절은 FS 클라이언트나 FS 에뮬레이터(시험할 때 FS를 흉내 내는 프로그램)를 만들 때 필요한 세부다. 그중 이 절은 요청을 언제 다시 보내고 연결을 어떻게 유지하는지 정하는 시간 규칙을 본다. 이 규칙을 놓치면 클라이언트가 응답을 끝없이 기다리거나, FS가 같은 명령을 두 번 실행하게 만들 수 있다.

::: info 이 장이 기준으로 삼는 판
이 스터디는 ISO 11783-13의 2011년판(2판) 원문을 기준으로 정리한다. 2판은 2007년 초판의 minor revision(작은 개정)이다. Version Number는 초안 0, 최종 초안 1, 초판 2, 2판 3 순서로 매기므로, 2판을 따르는 FS와 클라이언트는 Version Number 3을 보고한다. 파라미터 표 전체는 [표준 정리: Part 13](/study/isobus/appendix-iso-part13)에 있다.
:::

쉽게 말하면 FS와의 대화는 전화 상담과 비슷하다. 한 번에 질문 하나만 하고, 상담원이 "확인 중입니다"라고 말하는 동안은 기다린다. 아무 말 없이 정해진 시간이 지나면 같은 질문 번호로 다시 묻는다. 여기서 "확인 중입니다"가 File Server Status의 busy 표시이고, 질문 번호가 TAN이다.

시간 규칙은 여섯 가지다. 표의 "감시하는 쪽"은 그 시간을 재는 쪽이고, "만료되면"은 시간이 지났을 때 할 일이다.

| 타이밍 | 값 | 감시하는 쪽 | 만료되면 |
|---|---|---|---|
| File Server Status 송신 | busy가 아니면 2 000 ms, busy reading·writing이면 200 ms. Byte 2가 바뀌면 초당 최대 5회 | 클라이언트 | 해당 없음(보내는 주기) |
| File Server Status 부재 | 6 s | 클라이언트 | FS가 꺼졌을 수 있으므로 FS 통신 자원을 해제해도 된다 |
| Client Connection Maintenance | 2 000 ms. FS와 활발히 상호작용하는 동안 보낸다 | FS | 6 s 동안 못 받으면 그 클라이언트의 열린 파일을 닫고, 모든 Handle을 무효로 하고, current directory를 기본값으로 되돌린다 |
| busy 통지 | 요청 완료 뒤 응답이 200 ms보다 오래 걸리면 FS가 busy를 표시한 File Server Status를 보낸다 | FS | 해당 없음 |
| 요청 타임아웃 | File Server Status가 busy를 보이지 않으면 600 ms | 클라이언트 | 실패로 보고 같은 TAN으로 재요청 |
| TP·ETP | TP·ETP 타임아웃 준수 | 양쪽 | TP·ETP 규칙대로 처리 |

명령마다 처리 시간이 크게 달라 고정 응답 타임아웃을 줄 수 없으므로, 클라이언트는 File Server Status로 처리 상태를 지켜본다. File Server Status의 Byte 2가 busy 표시다. bit 0이 1이면 읽는 중(busy reading), bit 1이 1이면 쓰는 중(busy writing)이다. 이를 클라이언트 동작으로 옮기면 다음과 같다. 각 규칙은 표준에 있는 것이고, 순서로 엮은 것은 이 글의 정리다.

1. 직전 TAN에 1을 더해 요청을 보낸다. 응답이 오기 전에는 다음 명령을 보내지 않는다.
2. 요청 전송이 끝난 시점부터 시간을 잰다. File Server Status Byte 2에 busy(bit 0 reading, bit 1 writing)가 보이면 계속 기다린다.
3. busy 표시 없이 600 ms가 지나면 같은 TAN으로 다시 보낸다.
4. 응답이 오면 Byte 1(함수)과 TAN을 확인하고, 에러 코드가 0이 아니면 그 뒤의 파라미터를 버린다.
5. 상호작용하는 동안 Client Connection Maintenance를 2 s마다 보낸다. File Server Status가 6 s 동안 오지 않으면 FS가 사라진 것으로 보고 Handle을 버린다.

아래 그림은 3번 규칙이 실제로 어떻게 돌아가는지 보여 준다. 첫 응답이 버스에서 사라졌지만, 클라이언트가 같은 TAN으로 다시 묻자 FS는 명령을 다시 실행하지 않고 기억해 둔 응답을 보낸다. 그래서 클라이언트는 데이터를 빠짐없이 받는다.

![응답 유실과 같은 TAN 재요청: 클라이언트가 Read File TAN 5를 보내고 FS가 실행했지만 응답이 버스에서 유실되고, busy 없이 600 ms가 지나 클라이언트가 같은 TAN 5로 다시 요청하자 FS는 실행하지 않고 기억한 응답을 재전송하며, 이어서 TAN 6 요청은 새로 실행되어 클라이언트가 ABCD와 EFGH를 모두 받는 흐름](/images/study-isobus/51-fs-tan-retry-light.png)
![응답 유실과 같은 TAN 재요청: 클라이언트가 Read File TAN 5를 보내고 FS가 실행했지만 응답이 버스에서 유실되고, busy 없이 600 ms가 지나 클라이언트가 같은 TAN 5로 다시 요청하자 FS는 실행하지 않고 기억한 응답을 재전송하며, 이어서 TAN 6 요청은 새로 실행되어 클라이언트가 ABCD와 EFGH를 모두 받는 흐름](/images/study-isobus/51-fs-tan-retry-dark.png)

표준은 200 ms busy 규칙에서 600 ms 타임아웃을 끌어낸다. 이유가 따로 적혀 있지는 않지만, busy를 표시한 File Server Status가 200 ms 주기로 오므로 600 ms 동안 한 번도 보이지 않았다면 FS가 그 요청을 처리하고 있지 않다고 판단하는 셈으로 보인다.

::: warning 연결 유지와 TAN에서 생기는 함정
- Client Connection Maintenance는 "FS와 활발히 상호작용하는 동안" 보낸다. 로그 파일을 열어 두고 한참 쓰지 않는 클라이언트도 이 메시지를 멈추면 6 s 뒤 Handle이 무효가 되고, 다음 Write는 Invalid Handle(5)로 실패한다.
- FS는 클라이언트별로 <strong>직전</strong> 요청 하나의 TAN과 응답만 기억하고, 새 요청의 TAN이 그것과 같으면 실행하지 않는다. 재요청하면서 TAN을 바꾸면 FS는 새 요청으로 실행해 Read File의 파일 포인터가 한 번 더 움직인다.
- TAN 카운터는 전원 인가 뒤 0부터 시작하는 것이 권고(should, 꼭 지킬 의무는 아닌 권장 사항)다. 클라이언트가 빠르게 재시작해 6 s 타임아웃 전에 다시 요청하면, 새 첫 요청의 TAN이 FS가 기억하는 직전 TAN과 우연히 같을 때 재전송으로 오인될 수 있다. 표준은 이 경우를 따로 다루지 않으며, 이 함정은 규칙에서 끌어낸 추론이다.
:::

TAN 재전송 규칙을 코드로 확인해 보자. `FileServer.read`가 FS 역할을 하고, `use_tan=True`이면 클라이언트 주소(SA)별로 직전 TAN과 응답을 `self.last`에 기억한다. `client_reads`는 첫 응답을 잃은 클라이언트가 같은 TAN 5로 다시 묻고, 이어서 TAN 6으로 다음 4바이트를 읽는 상황을 흉내 낸다. 위 그림과 같은 상황이다.

::: details Python으로 TAN 재전송 처리 확인하기
FS가 TAN을 기억할 때와 기억하지 않을 때, 응답 하나가 유실된 상황에서 클라이언트가 받는 데이터를 비교한다.

```python
class FileServer:
    """5.3.2: remember the last request TAN and response per client."""

    def __init__(self, data: bytes, use_tan: bool = True):
        self.data, self.pos, self.use_tan = data, 0, use_tan
        self.last = {}                       # client SA -> (tan, response)

    def read(self, client: int, tan: int, count: int) -> bytes:
        if self.use_tan and client in self.last and self.last[client][0] == tan:
            return self.last[client][1]      # same TAN: do not execute, resend
        chunk = self.data[self.pos:self.pos + count]
        self.pos += len(chunk)               # Read File advances the file pointer
        self.last[client] = (tan, chunk)
        return chunk


def client_reads(fs: FileServer) -> bytes:
    got = b""
    fs.read(0x80, tan=5, count=4)            # response lost on the bus
    got += fs.read(0x80, tan=5, count=4)     # timeout -> repeat with the SAME TAN
    got += fs.read(0x80, tan=6, count=4)     # next request -> new TAN
    return got


if __name__ == "__main__":
    assert client_reads(FileServer(b"ABCDEFGHIJKL")) == b"ABCDEFGH"
    assert client_reads(FileServer(b"ABCDEFGHIJKL", use_tan=False)) == b"EFGHIJKL"  # "ABCD" lost
    print("all asserts passed")
```

FS가 TAN을 기억하면 응답을 한 번 잃어도 클라이언트는 `ABCDEFGH`를 빠짐없이 받는다. TAN 비교가 없으면 재요청이 새 읽기로 실행돼 `ABCD`가 사라진다.
:::

예제를 실행하면 두 `assert`가 모두 통과해 `all asserts passed`가 출력된다. 두 번째 `assert`가 핵심이다. TAN 비교가 없는 FS에서는 재요청이 `EFGH`를 읽어 버려, 첫 4바이트 `ABCD`는 클라이언트에 영영 도착하지 않는다.

정리하면 클라이언트는 한 번에 요청 하나만 보내고, busy 표시 없이 600 ms가 지나면 같은 TAN으로 다시 묻는다. 연결 유지 메시지는 2 s마다 보내고, 6 s 끊기면 양쪽 모두 상대가 사라진 것으로 본다.

<small>근거: ISO 11783-13 5.3.2, 5.3.3, B.3, B.5, C.1.1~C.1.3</small>

## 6. 메시지 공통 형식과 명령 바이트 지도 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절은 모든 FS 메시지에 공통인 형식 규칙과, Byte 1 값마다 어떤 명령인지 한눈에 보는 지도다. 구현할 때 옆에 두고 찾아보는 용도로 쓴다.

공통 규칙은 다음과 같다.

- 문자열은 왼쪽 문자부터, 2바이트 이상 수치는 LSB부터 보낸다. 예를 들어 경로 길이 47(0x002F)은 `2F 00` 순서로 간다.
- 8바이트 이하 메시지는 CAN 프레임 하나로, 9바이트 이상은 TP 또는 ETP로 보낸다. 8바이트보다 짧으면 남는 바이트를 0xFF로 채운다. TP는 [15장](/study/isobus/15-tp-bam-cmdt), ETP는 [17장](/study/isobus/17-etp)에서 다뤘다.
- 파일 데이터는 0x00~0xFF를 그대로 다룬다. 제어 문자·줄 끝·파일 끝 표시를 특별 취급하지 않는다. FS에게는 텍스트 파일도 바이트 묶음이다.
- 9~16비트 비트 그룹(File Date·File Time처럼 여러 값을 비트 단위로 붙여 담은 2바이트 칸)은 하위 바이트(bit 7…0) 다음 상위 바이트(bit 15…8) 순서다. Seek의 Offset만 2의 보수 signed 32비트(음수도 담는 정수)이고, 나머지 수치는 unsigned(0 이상만 담는 정수)다.

Byte 1은 상위 4비트가 command group, 하위 4비트가 function이다. 함수 전체를 한 표로 모으면 다음과 같다. "TAN" 열은 Byte 2가 TAN인지를 뜻한다. "요청 / 응답 길이"의 8은 CAN 프레임 하나에 들어가는 고정 8바이트, "가변"은 경로나 데이터 길이에 따라 달라져 TP로 갈 수 있다는 뜻이다. 길이가 하나만 적힌 줄은 응답이 없는 방송이나 연결 유지 메시지다.

| Byte 1 | 그룹 | 함수 | TAN | 요청 / 응답 길이 |
|---|---|---|---|---|
| 0x00 | Connection Management | File Server Status (FS → 전역) | 없음 | 8 |
| 0x00 | Connection Management | Client Connection Maintenance (클라이언트 → FS) | 없음 | 8 |
| 0x01 | Connection Management | Get File Server Properties | 없음 | 8 / 8 |
| 0x02 | Connection Management | Volume Status | 없음 | 가변 / 가변 |
| 0x10 | Directory Handling | Get Current Directory | 있음 | 8 / 가변 |
| 0x11 | Directory Handling | Change Current Directory | 있음 | 가변 / 8 |
| 0x20 | File Access | Open File | 있음 | 가변 / 8 |
| 0x21 | File Access | Seek File | 있음 | 8 / 8 |
| 0x22 | File Access | Read File | 있음 | 8 / 가변 |
| 0x23 | File Access | Write File | 있음 | 가변 / 8 |
| 0x24 | File Access | Close File | 있음 | 8 / 8 |
| 0x30 | File Handling | Move File | 있음 | 가변 / 8 |
| 0x31 | File Handling | Delete File | 있음 | 가변 / 8 |
| 0x32 | File Handling | Get File Attributes | 있음 | 가변 / 8 |
| 0x33 | File Handling | Set File Attributes | 있음 | 가변 / 8 |
| 0x34 | File Handling | Get File Date & Time | 있음 | 가변 / 8 |
| 0x40 | Volume Access | Initialize Volume | 있음 | 가변 / 8 |

- 0x00은 File Server Status와 Client Connection Maintenance가 함께 쓴다. 방향(PGN 0xAB00 / 0xAA00)으로 가른다.
- Connection Management(0x00~0x02)에는 TAN이 없고, Byte 2에 상태·버전·Volume Mode가 온다. 나머지 명령은 모두 Byte 2가 TAN이다.
- 모든 FS는 함수 전체를 구현해야 하지만, 이후 개정에서 추가된 함수를 모르는 구판 기반 FS도 있을 수 있다. 그래서 Directory Handling·File Access·File Handling·Volume Handling 그룹의 미지원 함수에는 error 12(Function not supported)로 답해야 한다. 이 목록에 Connection Management는 없다.
- 표준은 0100 그룹을 한 곳에서는 Volume Handling, 다른 곳에서는 Volume Access라고 부른다. 같은 그룹이다.
- 이 메시지들이 실제 CAN ID로 어떻게 보이는지는 1절의 CAN ID 표에 있다.

::: details 원문을 가진 독자를 위한 메모
- 원문은 Byte 1 값을 `32₁₀`처럼 10진수로 적는다.
- 위 표의 함수별 원문 위치: File Server Status C.1.2, Client Connection Maintenance C.1.3, Get File Server Properties C.1.4·C.1.5, Volume Status C.1.6·C.1.7, Get Current Directory C.2.2, Change Current Directory C.2.3, Open File C.3.3, Seek File C.3.4, Read File C.3.5, Write File C.3.6, Close File C.3.7, Move File C.4.2, Delete File C.4.3, Get File Attributes C.4.4, Set File Attributes C.4.5, Get File Date & Time C.4.6, Initialize Volume C.5.2.
- B.1은 0100 그룹을 Volume Handling, C.5는 Volume Access라고 부른다.
- 미지원 함수에 error 12로 답하는 그룹 목록과 우선순위·PDU1 규정은 C.1.1에 있다. ETP 인용(5.1)에 대해서는 1절의 메모를 참고한다.
:::

<small>근거: ISO 11783-13 5.1, 5.2, B.1, B.2, C.1.1</small>

## 7. 날짜·시간, 여러 클라이언트, 파일 Handle (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절은 FS가 파일 시각을 어떻게 기록하는지, 여러 클라이언트를 어떻게 나눠 대하는지, 열린 파일 수를 어떻게 세는지 정리한다.

<strong>날짜·시간.</strong> 파일 날짜·시간은 UTC(협정 세계시, 나라별 시차를 빼고 쓰는 기준 시각)다. FS는 자체 실시간 시계를 두거나 ISO 11783-7(트랙터와 작업기가 주고받는 공통 메시지를 정한 표준 문서)의 Time/Date 파라미터 그룹으로 시각을 얻는다(Time/Date 메시지는 [23장](/study/isobus/23-implement-messages-basics) 참고). 기록되는 시각은 실제로 수정된 마지막 시각이라, read/write로 열었어도 쓰지 않았다면 시각을 갱신하면 안 된다. 날짜·시간을 지원하지 않는 FS는 모든 비트를 0으로 보내므로 "1980-00-00", "00-00-00"이 된다. 날짜 칸의 연도는 1980년을 0으로 세기 때문이다. 날짜와 시간을 비트로 담는 방법은 [52장](/study/isobus/52-file-server-details)의 디렉터리 엔트리 풀이에 있다.

<strong>다중 클라이언트.</strong> FS는 클라이언트를 하나 이상 지원하고, 여럿이 동시에 연결돼도 각자에게 자기만 있는 것처럼 동작해야 한다. 클라이언트 사이에 간섭이 없어야 한다. 클라이언트가 연결되면 FS는 그 클라이언트의 current directory를 primary volume의 루트로, 볼륨이 없으면 볼륨 목록 `\\`로 초기화한다. 공용 파일을 같이 쓰는 클라이언트끼리 디렉터리·파일 이름을 맞추는 일은 클라이언트 책임이다.

<strong>제조사 전용 디렉터리.</strong> 다른 회사의 파일을 실수로 건드리지 않도록 제조사마다 쓰는 전용 디렉터리 이름이 정해져 있다. 이름은 `MCMC` 뒤에 ISO 11783-5(주소와 NAME을 정하는 표준 문서) 제조사 코드를 앞자리 0을 채운 10진 4자리로 붙인다. 제조사 코드가 123이라면 `MCMC0123`이다(예시). NAME의 제조사 코드 필드는 11비트(0~2047)라 4자리로 충분하다(NAME의 필드는 [12장](/study/isobus/12-j1939-address-name) 참고).

- 클라이언트는 자기 NAME과 다른 제조사 코드로 이 이름을 쓰면 안 된다. 다른 제조사의 전용 디렉터리 안 파일을 열려 하면 FS는 Access Denied(1)를 돌려준다.
- 전용 디렉터리는 각 볼륨의 루트에만 둘 수 있고, 만드는 일은 클라이언트 책임이다.
- 경로 맨 앞이나 볼륨 이름 바로 뒤의 `~`는 current volume의 전용 디렉터리로 바뀐다. current volume이 없으면 primary volume을 쓴다. `~`는 이름 안에 써도 되지만, `~` 한 글자만으로 된 이름은 전용 디렉터리로 해석된다. 실제 해석 예는 [52장](/study/isobus/52-file-server-details)의 경로 해석 표에 있다.

<strong>파일 Handle.</strong> Move나 Delete처럼 경로만 받는 명령을 처리하려고 FS가 내부에서 Handle을 만들면 그것도 열린 파일 수에 더한다. 이 수가 File Server Status Byte 3(Number of Open Files)이다. 그래서 Move File·Get/Set File Attributes·Get File Date & Time도 Too many files open(3)으로 실패할 수 있고, 실제로 이들의 응답 에러 코드 목록에 3이 있다([52장](/study/isobus/52-file-server-details)의 명령별 에러 코드 표 참고). 클라이언트가 연 파일이 적어도 생길 수 있는 오류다.

정리하면 파일 시각은 실제로 고친 마지막 UTC 시각이고, 클라이언트마다 current directory와 Handle이 따로 관리되며, FS가 속으로 쓰는 Handle도 열린 파일 수에 들어간다.

<small>근거: ISO 11783-13 5.4~5.6, A.2.3.1, B.24, B.25, C.4; ISO 11783-5 Table 1</small>

::: tip 핵심 정리
- File Server(FS)는 ISOBUS 네트워크에서 USB 없이 파일을 공유하는 독립 ECU다. 클라이언트는 PGN 0xAA00으로 요청하고 0xAB00으로 응답을 받는다.
- 파일은 Volume → Directory → File 계층으로 정리되고, 경로 구분자는 `\`, 최상위 볼륨 목록은 `\\`다.
- 클라이언트는 Client Connection Maintenance(2 s 주기)로 연결을 유지하고, Open → Seek/Read/Write → Close 순서로 파일에 접근한다. 6 s 끊기면 FS가 그 클라이언트의 Handle을 모두 닫는다.
- Byte 1은 명령 그룹(상위 4비트)과 함수(하위 4비트)이고, 연결 관리 메시지를 뺀 모든 명령·응답은 Byte 2의 TAN으로 짝을 맞춘다.
- 요청은 한 번에 하나다. busy 표시 없이 600 ms가 지나면 같은 TAN으로 다시 보내고, FS는 같은 TAN의 재요청에 실행 없이 이전 응답을 재전송해 중복 실행을 막는다.
:::

::: details 확인 문제
1. (개념) FS의 파일 계층 3단계를 위에서부터 쓰고, 볼륨 목록과 경로 구분자를 나타내는 기호를 각각 쓰라.
2. (개념) Byte 1이 0x24(=36)인 메시지는 어느 명령 그룹의 어떤 함수인가? 이 메시지의 Byte 2에는 무엇이 들어가는가?
3. (개념) 로그 파일을 열어 둔 클라이언트가 10초 동안 Client Connection Maintenance를 보내지 않다가 Write File을 보냈다. 어떤 결과를 받게 되고, 왜 그런가?
4. (장애 진단) FS 클라이언트가 Read File(TAN 0x21)을 보냈는데 응답이 없다. 그동안 File Server Status는 `00 00 01 FF FF FF FF FF`만 2 s 주기로 온다. 700 ms가 지났을 때 클라이언트는 무엇을 해야 하는가? 재요청에서 실수로 TAN 0x22를 쓰면 어떤 일이 생기는가?

**답 가이드**
1. 볼륨(Volume) → 디렉터리(Directory) → 파일(File)이다. 볼륨 목록은 `\\`, 경로 구분자는 `\`(백슬래시)다.
2. 0x24는 2진수로 0010 0100이다. 상위 4비트 0010은 File Access 그룹, 하위 4비트 0100은 그 그룹의 4번 함수인 Close File이다. File Access 그룹이므로 Byte 2는 TAN이다. Close File 요청이라면 그 뒤 Byte 3에 닫을 Handle이 온다.
3. Invalid Handle(5)로 실패한다. FS는 Client Connection Maintenance를 6 s 동안 못 받으면 그 클라이언트의 열린 파일을 닫고 모든 Handle을 무효로 한다. 파일을 열어 두기만 하는 동안에도 연결 유지 메시지는 계속 보내야 한다.
4. Byte 2가 0x00이라 busy 표시가 없으므로, 600 ms가 지난 시점에 요청을 실패로 보고 같은 TAN 0x21로 다시 보낸다. FS가 첫 요청을 이미 실행하고 응답만 잃었다면 같은 TAN을 알아보고 실행 없이 이전 응답을 다시 보낸다. TAN 0x22를 쓰면 FS는 새 요청으로 실행해 파일 포인터가 한 번 더 움직이고, 첫 응답의 데이터는 영영 받지 못한다. Byte 3의 0x01은 FS에 열린 파일이 하나라는 뜻이다.
:::

## 다음 챕터

- 다음: [52장 File Server 세부: 볼륨, 경로, 파라미터, 바이트 따라가기](/study/isobus/52-file-server-details)
