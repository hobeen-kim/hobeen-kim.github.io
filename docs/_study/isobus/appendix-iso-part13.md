---
title: "표준 정리: Part 13 — File server"
description: "ISO 11783-13(File server) — 파일 서버 프로토콜, 명령/응답 배치, 에러 처리를 정리한 표준 요약이다."
date: 2026-08-21
tags: [ISOBUS, ISO11783, 표준정리]
---

# ISO 11783-13: File server 정리

::: info 이 문서에 대해
ISO 11783-13 표준 원문을 학습 목적으로 재구성한 <strong>비공식 요약·해설</strong>이다. 규범적 판단이 필요할 때는 반드시 원문 표준을 확인해야 한다.
:::

## 개요

ISO 11783-13(2판, 2011-04-01)은 ISO 11783 시리즈 중 <strong>File Server(FS)</strong>를 정의하는 파트다. FS는 모바일 임플리먼트 버스(implement bus)에 붙는 독립적인 ECU로, 네트워크상의 모든 컨트롤러가 파일 기반 저장 장치에 데이터를 저장하거나 읽어올 수 있게 하는 저장소 서비스를 제공한다. 트랙터·자주식(self-propelled) 임플리먼트에서 사용하는 FS의 메시지 셋과 동작 규칙을 규정한다.

문서 구조는 본문(Scope~Requirements)이 5페이지 남짓으로 짧고, 실질적인 내용 대부분이 부속서에 있다.

| 구성 | 성격 | 내용 |
|------|------|------|
| Clause 1~4 | 본문 | 적용 범위, 인용 표준, 용어 정의, 개요 |
| Clause 5 | 본문 | 메시지 포맷, 데이터 형식, 전송 제어(TAN), 타임아웃, 멀티클라이언트, Handle, Volume |
| Annex A | normative | 문자 집합, 파일명·경로 문법 정의 |
| Annex B | normative | 파라미터 정의(커맨드 그룹, 상태, 에러 코드, 속성 등) |
| Annex C | normative | FS 메시지 정의(커맨드/응답 바이트 배치) |
| Annex D | informative | 일반적인 파일 시스템 예시 |

인용 표준(normative references)은 ISO 11783의 Part 1(일반), Part 3(Data link layer), Part 5(Network management), Part 6(Virtual terminal), Part 7(Implement messages application layer)이다. 특히 9바이트 이상 메시지 전송에 Part 3의 TP(Transport Protocol)와 Part 6의 ETP(Extended Transport Protocol)를 그대로 쓴다.

:::info 판 정보
2011년 2판은 2007년 초판을 대체하는 minor revision이다. ISO/TC 23/SC 19(Agricultural electronics)가 작성했다.
:::

## 용어 정의 (Clause 3)

| 용어 | 정의 |
|------|------|
| client | FS의 서비스를 사용하는 임플리먼트 버스상의 ECU |
| directory | 다른 파일들의 관리 정보를 저장하는 파일 |
| file | 저장 장치에 데이터를 저장하는 데이터 객체 |
| file attribute | 파일의 종류·특성을 정의하는 비트 코드 정보 |
| file server (FS) | 파일 저장소를 제공하고 파일 접근·조작 명령 셋을 제공하는 ECU |
| filename | 파일이나 디렉터리를 식별하는, 문자 집합 규칙(Annex A)을 따르는 이름 |
| Handle | 파일·디렉터리 접근에 사용하는 데이터 객체 |
| hidden attribute | 디렉터리 목록에 나타나지 않아야 함을 나타내는 파일 속성 |
| path | 디렉터리 이름을 포함할 수 있는 파일명 지정 |
| read-only attribute | 파일 쓰기·삭제를 방지하는 파일 속성 |
| volume | 특정 논리적·물리적 저장 단위(공간)를 가리키는 디렉터리 |

hidden·read-only 속성은 클라이언트가 FS 명령으로 설정한다. primary volume은 FS 기동 시 current volume으로 쓰이는 볼륨이다.

## 기본 요구사항 (Clause 5)

### 메시지 포맷과 데이터 형식

- 메시지는 PGN(parameter group number)을 라벨로 하는 파라미터 그룹으로 구성된다(파라미터 정의는 Annex B).
- 문자열은 왼쪽 문자부터, 수치 파라미터(2바이트 이상)는 <strong>LSB first</strong>로 전송한다.
- 가변 길이 메시지가 8바이트 이하면 단일 CAN 프레임으로, 9바이트 이상이면 TP(ISO 11783-3) 또는 ETP(ISO 11783-6)로 전송한다.
- 8바이트 미만 메시지의 미사용 바이트는 FF₁₆으로 채운다.

데이터 형식 규칙:

| 형식 | 규칙 |
|------|------|
| Data | 부호 없는 8비트 값 블록. 0~255 전 범위 허용, 제어 문자·EOL·EOF 등의 특수 처리 없음 |
| Bit group | 1~8비트는 1바이트(bit 7~0)에, 9~16비트는 2바이트(LSB 먼저, 그다음 MSB)에 패킹. 미사용 비트는 0 |
| Unsigned 8/16/32 bit | 각각 1/2/4바이트, LSB first |
| Signed 32 bit | 4바이트, LSB first, 2의 보수 |
| Character string | 바이트로 표현된 문자들. 길이는 별도의 string length 항목으로 지정 |

### 전송 제어와 TAN (5.3)

클라이언트-FS 간 모든 트랜잭션은 클라이언트의 요청(request)으로 시작해 FS의 응답(response)으로 끝난다. 통신 장애 시 안전한 재시도를 위해 <strong>TAN(Transaction Number)</strong> 메커니즘을 사용한다.

문제 상황은 이렇다. 클라이언트가 요청을 보냈는데 응답이 없으면, (a) FS가 요청을 못 받았는지 (b) 응답이 유실됐는지 구분할 수 없다. 단순히 재요청하면 (b)의 경우 Read File 같은 명령이 두 번 실행되어 파일 포인터가 다음 데이터로 넘어가 버린다.

TAN 규칙:

- 각 클라이언트는 자체 TAN 카운터를 유지하며 전원 인가 후 0에서 시작, 요청마다 증가시킨다.
- 클라이언트는 수신한 응답의 TAN이 요청의 TAN과 같은지 확인해 명령 유실 여부를 검증한다.
- FS는 클라이언트별로 마지막 처리 명령과 응답 메시지를 기억한다.
- FS는 새 요청의 TAN을 직전 요청과 비교한다. TAN이 다르면 → 새 요청으로 간주하고 실행 후 응답. TAN이 같으면 → 재전송 요청으로 간주하고 <strong>실행 없이</strong> 이전 응답을 그대로 재전송.

이렇게 하면 (a)의 경우 FS가 처음 받는 요청이므로 정상 실행되고, (b)의 경우 중복 실행 없이 이전 응답만 다시 받는다.

### 타임아웃 (5.3.3)

| 항목 | 값 |
|------|-----|
| TP/ETP 타임아웃 | ISO 11783-3(TP), ISO 11783-6(ETP) 규정을 따름 |
| FS busy 상태 통지 | 요청 완료가 200 ms를 넘기면 FS는 busy 상태를 나타내는 status 메시지를 전송 |
| 요청 타임아웃 | FS status가 busy를 표시하지 않으면 600 ms |

타임아웃이 만료되면 요청이 실패한 것으로 간주하고, 클라이언트는 <strong>같은 TAN으로</strong> 재요청한다.

### 날짜·시간 지원 (5.4)

여러 FS 명령이 파일 날짜·시간을 요구하며 UTC를 사용한다. FS는 자체 실시간 정보를 유지하거나 ISO 11783-7의 Time/Date 파라미터 그룹으로 시각을 요청해 구현할 수 있다. 파일의 날짜·시간은 <strong>실제 수정된</strong> 최종 시각이다. read/write로 열었더라도 쓰기가 없었으면 시각을 갱신하지 않는다.

### 멀티클라이언트 지원 (5.5)

FS는 하나 이상의 클라이언트를 지원해야 하며, 동시에 여러 클라이언트가 연결되어도 각 클라이언트에게는 자신이 유일한 클라이언트인 것처럼 동작해야 한다. 클라이언트 간 명령 처리에 간섭이 없어야 한다.

클라이언트 연결 시 FS는 해당 클라이언트의 current directory를 primary volume의 루트 디렉터리로 초기화한다. 볼륨이 없으면 볼륨 목록 `\\`으로 설정한다. 여러 클라이언트가 공용 파일에 접근해야 하는 경우 디렉터리·파일 명명 규칙 동기화는 클라이언트들의 책임이다.

:::tip 제조사 전용 디렉터리 (MCMC0000)
제조사 독점 파일에 대한 의도치 않은 접근을 막기 위해 예약 디렉터리 명명 규칙이 있다. `MCMC0000` 형태로, 0000 자리에 ISO 11783-5의 제조사 코드를 4자리 십진수(leading zero 포함)로 넣는다.

- 클라이언트는 자기 NAME 필드의 manufacturer code와 다른 코드의 디렉터리 이름을 사용해서는 안 된다.
- 다른 제조사의 전용 디렉터리 안 파일을 열려고 하면 FS는 접근을 차단하고 "access denied" 에러 코드를 반환한다.
- 제조사 전용 디렉터리 생성은 클라이언트 책임이며, 각 볼륨의 <strong>루트에만</strong> 둘 수 있다.
:::

### File Handle과 Volume (5.6, 5.7)

- FS는 다수의 파일 Handle을 지원할 수 있다. Handle을 쓰지 않고 폴더·파일명만 쓰는 명령도 있는데, 이 처리를 위해 FS가 내부적으로 Handle을 만들었다면 open file 수에 반영해야 한다.
- 서로 다른 매체(FLASH, 이동식 매체, 러기다이즈드 디스크 등)는 서로 다른 볼륨으로 배정할 수 있다.
- FS는 여러 볼륨을 지원할 수 있고, 초기화되지 않은 매체·장치 없음 등의 이유로 볼륨이 하나도 없을 수도 있다.
- 볼륨 목록은 `\\`로 지정하며 디렉터리 구조의 최상위 계층이다.
- 볼륨 생성은 전용 서비스 툴이 Initialize Volume Request(Annex C의 C.5.2.2)로 수행할 수 있다. 볼륨 이름은 FS가 정하지만, 서비스 툴이 명명하도록 허용할 수도 있다.

## Annex A — 문자 집합과 이름·경로 문법 (normative)

### 유효 문자

파일명·경로의 모든 문자는 ISO/IEC 8859-1(ISO Latin 1) 기반 문자 집합의 적절한 부분집합으로 FS가 검증한다.

- 대소문자 무시(case-insensitive) 파일 시스템에서는 FS가 소문자(61₁₆~7A₁₆)를 대문자(41₁₆~5A₁₆)로 변환한다.
- 긴 파일명(long filename)을 지원하지 않는 FS는 <strong>8.3 표기</strong>를 사용한다: 이름 최대 8자 + 단일 점(2E₁₆)으로 시작하는 최대 3자 확장자.
- 긴 파일명을 지원하는 FS는 A.2의 정의를 따른다.

### 이름 정의

이름 길이는 1~254자다. 주요 문법 요소(BNF식 정의를 요약):

| 요소 | 정의 |
|------|------|
| ShortNameChar | `0-9`, `A-Z`, `-`, `!`, `#`, `$`, `%`, `&`, `'`, `(`, `)`, `@`, `^`, `_`, `` ` ``, `{`, `}`, `~`, `\xA1`~`\xFF` 중 1자 |
| LongNameChar | NUL, `\`, `*`, `?`를 제외한 Unicode/ISO/IEC 10646 문자 |
| WildCardChar | `*` 또는 `?` |
| PathSeparatorChar | `\` 1개 |
| VolumeListIndicator | `\\` (백슬래시 2개) |
| ParentFolderIndicator | `..` |
| CurrentFolderIndicator | `.` |
| MfgSpecificFolderIndicator | `~` |
| ShortName | ShortNameChar 1~8자 + (`.` + ShortNameChar 0~3자) 옵션 |
| LongName | LongNameChar 1~254자 |
| VolumeName | LongName 형식 (예: `VOL_B`, `Flash Volume`) |

### 경로 규칙

- `\\` 경로의 디렉터리 목록을 요청하면 FS는 <strong>볼륨 목록</strong>을 반환한다. 볼륨이 하나뿐이어도 모든 FS는 `\\`를 지원해야 한다(이동식 매체 조회 목적).
- `.`(현재 디렉터리)과 `..`(상위 디렉터리)은 경로에 쓸 수 있지만 디렉터리 목록에는 나타나지 않아야 한다.
- `~`(tilde)는 클라이언트의 제조사 전용 디렉터리의 자리표시자다. 경로 맨 앞 또는 볼륨명 뒤에만 올 수 있고, FS가 current volume의 제조사 전용 디렉터리 이름으로 치환한다. current volume이 없으면 primary volume을 쓴다. 예: `~\file1.txt` → `MCMC0000\file1.txt`.

경로 표현 예시:

| 형태 | 예시 |
|------|------|
| 현재 디렉터리 기준 상대 경로 | `.\`, `..\path\`, `Level1\Level2\`, `path\Test.txt` |
| current volume 루트 기준 | `\Path\`, `\Level1\Level2\`, `\path\Test` |
| 볼륨 포함 절대 경로 | `\\VOL_B\path\`, `\\VOL_B\Level1\Level2\Test` |
| 제조사 전용 폴더 사용 | `~\`, `~\Path\`, `\\VOL_B\~\Level1\Level2\` |

### 와일드카드 (A.2.3.3)

- `*`: 파일명·폴더명의 0개 이상 문자에 매칭
- `?`: 정확히 1개 문자에 매칭
- 와일드카드는 <strong>디렉터리 목록 조회에서만</strong> 사용해야 한다.

예: `\\VOL_B\path\Test*.txt`, `\\VOL_B\Level1\Level2\T?st.txt`, `~\path\*`.

전체 구조 예시(Figure A.1 취지): 최상위에 볼륨들(`\\Flash`, `\\VOL_B`, …)이 있고, 각 볼륨 루트에 제조사 전용 디렉터리(`MCMC0000`)와 일반 디렉터리 트리가 있으며, 말단에 파일이 위치한다. 예시 경로는 `\\Flash\MCMC0000\DirectoryA1\...\DirectoryBn\File123` 형태다.

## Annex B — 파라미터 정의 (normative)

FS 명령의 바이트 1은 상위 4비트가 <strong>커맨드 그룹</strong>(B.1), 하위 4비트가 그룹 내 <strong>함수</strong>(B.2)다.

| 커맨드 그룹 값 | 의미 |
|---------------|------|
| 0000 | Connection Management |
| 0001 | Directory Handling |
| 0010 | File Access |
| 0011 | File Handling |
| 0100 | Volume Handling |

### 주요 파라미터 요약

| 파라미터 | 크기 | 요점 |
|----------|------|------|
| File Server Status (B.3) | 1바이트 | bit 1 = busy writing, bit 0 = busy reading, 나머지 예약(0) |
| Number of Open Files (B.4) | 1바이트 | 현재 FS에서 열려 있는 파일 수 (0~255) |
| Version Number (B.5) | 1바이트 | 0=draft, 1=final draft, 2=초판(2007), 3=2판(2011), 255=Version 2 이하 호환(클라이언트 전용) |
| Max Number of Simultaneously Open Files (B.6) | 1바이트 | 동시에 열 수 있는 최대 파일 수 |
| File Server Capabilities (B.7) | 1바이트 | bit 0 = 다중 볼륨 지원 여부, 나머지 예약 |
| Transaction Number (B.8) | 1바이트 | TAN, 0~255 |
| Error Code (B.9) | 1바이트 | 아래 표 참조 |
| Handle (B.10) | 1바이트 | 0~254 = FS가 배정한 Handle 값, 255 = Handle 배정 실패 |
| Space (B.11) | 4바이트 | 512바이트 단위 공간 크기 |
| Path Name Length (B.12) | 2바이트 | 경로 문자열 길이 |
| Position Mode (B.17) | 1바이트 | 0=파일 시작 기준, 1=현재 포인터 기준, 2=파일 끝 기준 |
| Offset (B.18) | 4바이트 | signed 32비트 오프셋 |
| Position (B.19) | 4바이트 | 파일 포인터 위치 (unsigned 32비트) |
| Count (B.20) | 2바이트 | 읽기/쓰기 바이트 수 또는 디렉터리 엔트리 수 |
| Filename Length (B.22) | 1바이트 | 8.3 FS는 최대 12자, long filename FS는 최대 254자(Version 2 이하는 31자였음) |
| Size (B.26) | 4바이트 | 파일 크기(바이트) |

:::info Version Number의 의미
클라이언트가 보고하는 Version Number는 그 클라이언트가 <strong>설계된 기준 판</strong>을 나타내며, 상대 FS에 맞춰 런타임에 바꾸면 안 된다. Version 3 클라이언트가 Version 2 FS와 통신하려고 Version 2 동작으로 폴백하더라도 파라미터로는 Version 3을 보고한다. FS는 보고된 Version Number를 이유로 통신·요청을 거부해서는 안 된다.
:::

### 에러 코드 (B.9)

응답 메시지의 에러 코드가 0("Success")이 아니면, 에러 코드 뒤에 오는 나머지 파라미터는 부정확할 수 있으므로 클라이언트는 무시해야 한다. (이 에러 코드 체계는 Version 3 이후 FS가 지원한다.)

| 값 | 의미 |
|-----|------|
| 0 | Success |
| 1 | Access Denied |
| 2 | Invalid Access |
| 3 | Too many files open |
| 4 | File, path or volume not found |
| 5 | Invalid Handle |
| 6 | Invalid given source name |
| 7 | Invalid given destination name |
| 8 | Volume out of free space |
| 9 | Failure during a write operation |
| 10 | Media is not present (Version 2 FS에서는 13번 코드가 이 의미였음) |
| 11 | Failure during a read operation |
| 12 | Function not supported |
| 13 | Volume is possibly not initialized |
| 14~41 | Reserved |
| 42 | Invalid request length (파일 포인터가 파일 시작/끝에 걸리거나 볼륨 공간 요청이 잘못된 경우) |
| 43 | Out of memory (FS 리소스 부족으로 요청을 완료할 수 없음) |
| 44 | Any other error |
| 45 | File pointer at end of file |
| 46~255 | Reserved |

### Flags — 파일 열기 모드 (B.14)

Open File 요청에서 접근 방식을 지정하는 1바이트 비트 필드다.

| 비트 | 값 | 의미 |
|------|-----|------|
| 7~5 | 000 | Reserved |
| 4 | 0 / 1 | 0 = 공유 읽기 접근으로 열기 / 1 = 배타적 접근으로 열기(이미 열려 있으면 실패) |
| 3 | 0 / 1 | 0 = 랜덤 액세스(포인터를 파일 시작으로) / 1 = append 모드(포인터를 파일 끝으로) |
| 2 | 0 / 1 | 0 = 기존 파일만 열기(없으면 실패) / 1 = 없으면 파일·디렉터리 생성 |
| 1,0 | 00 / 01 / 10 / 11 | 읽기 전용 / 쓰기 전용 / 읽기+쓰기 / <strong>디렉터리 열기</strong> |

bit 1,0 = 11("Open directory")일 때 bit 3은 무시되고 read-only로 취급된다(디렉터리 내용 조회 목적이므로). 디렉터리 경로 생성은 "Open directory" + "없으면 생성" 플래그 조합으로 수행한다.

### Attributes — 파일·볼륨 속성 (B.15)

FS가 파일을 클라이언트에게 기술할 때 쓰는 1바이트다.

| 비트 | 의미 (1일 때) |
|------|---------------|
| 7 | 볼륨이 case-sensitive (Version 3 이후 지원) |
| 6 | 볼륨이 이동식이 아님 |
| 5 | 볼륨이 long filename 지원 |
| 4 | Handle이 디렉터리를 가리킴 |
| 3 | Handle이 볼륨을 가리킴 |
| 2 | 볼륨이 hidden 속성 지원 (Version 3 이후 지원) |
| 1 | hidden 속성 설정됨 (볼륨이 hidden 속성을 지원할 때만 유효) |
| 0 | read-only 속성 설정됨 |

### Set Attributes Command (B.16)

속성 설정·해제 명령의 1바이트. 2비트씩 짝을 지어 "clear(00) / set(01) / 유지(11)" 3상태를 표현한다.

| 비트 | 대상 |
|------|------|
| 7,6 / 5,4 | Reserved (11로 전송) |
| 3,2 | hidden 속성: 00=해제, 01=설정, 11=현상 유지 |
| 1,0 | read-only 속성: 00=해제, 01=설정, 11=현상 유지 |

### Directory Entry 구조 (B.21)

디렉터리 읽기 응답에서 엔트리 하나의 배치는 다음과 같다(가변 길이).

| 바이트 | 필드 |
|--------|------|
| 1 | Filename Length (B.22) |
| 2~n | Filename (B.23) |
| n+1 | Attributes (B.15) |
| n+2, n+3 | File Date (B.24) |
| n+4, n+5 | File Time (B.25) |
| n+6~n+9 | Size (B.26) |

File Date/Time 인코딩(각 2바이트 비트 그룹):

| 필드 | 비트 | 범위 |
|------|------|------|
| Year − 1980 | Date bits 15~9 | 0~127 |
| Month | Date bits 8~5 | 1~12 |
| Day | Date bits 4~0 | 1~31 |
| Hours | Time bits 15~11 | 0~23 |
| Minutes | Time bits 10~5 | 0~59 |
| Seconds (2초 단위) | Time bits 4~0 | 1~29 |

날짜·시간을 지원하지 않는 구현은 모든 비트를 0으로 채워 "1980-00-00", "00-00-00"이 된다.

### 파일·볼륨 조작 모드 파라미터

<strong>File Handling Mode (B.27)</strong> — Move/Delete 등 파일 조작 명령의 동작 방식:

| 비트 | 의미 (1일 때) |
|------|---------------|
| 2 | Recursive 모드 |
| 1 | Force 모드 |
| 0 | Copy 모드 |

<strong>Report Hidden Files (B.28)</strong> — 디렉터리 목록에 hidden 파일 포함 여부: 0=미포함, 1=포함, 255=파라미터 없음(미포함으로 처리).

<strong>Volume Flags (B.29)</strong> — 볼륨 생성 시: bit 1(0=가용 공간 전체 사용, 1=지정 공간 사용), bit 0(0=기존 볼륨 있으면 실패, 1=기존 볼륨 덮어쓰기).

<strong>Volume Mode (B.30)</strong> — 볼륨 접근 모드(Version 3 이후). 00000000이면 현재 상태 요청: bit 1(1=볼륨 제거 준비 요청), bit 0(1=클라이언트가 볼륨 사용 중 보고, 0=미사용 보고).

<strong>Volume Status (B.31)</strong> — 볼륨 현재 상태(Version 3 이후): 0=Present, 1=In use, 2=Preparing for removal, 3=Removed.

<strong>Maximum Time before Volume Removal (B.32)</strong> — 볼륨 제거를 지연시킬 수 있는 최대 시간. 1바이트, 1 min/bit, 0~250.

## Annex C — File Server 메시지 정의 (normative)

### PGN과 데이터 전송 (C.1.1)

FS 메시지 프로토콜에는 PGN 2개가 예약되어 있다. 둘 다 destination-specific이며 기본 우선순위 7, Data Page 0이다.

| 방향 | PDU Format | PGN |
|------|-----------|-----|
| FS → Client | 171 | 43776 (AB00₁₆) |
| Client → FS | 170 | 43520 (AA00₁₆) |

- 클라이언트는 연결 유지를 시작하기 전에 이 PGN으로 FS의 능력 정보를 얻을 수 있다.
- 같은 PGN으로 TP(ISO 11783-3)·ETP(ISO 11783-6)를 통해 데이터를 주고받는다. destination-specific 메시지와 connection management를 사용해야 한다.
- 클라이언트는 응답을 받기 전에 다음 명령을 보내면 안 된다. 명령마다 응답 시간이 크게 다르므로 고정 타임아웃 대신 File Server Status 메시지로 처리 상태를 모니터링한다.
- 모든 FS는 전체 함수 집합을 구현해야 하지만, 이후 개정판에서 추가된 함수를 지원하지 않는 구버전 기반 FS도 있을 수 있다. 지원하지 않는 함수 요청에는 에러 코드 12("Function not supported")로 응답해야 한다.

### Connection Management (커맨드 그룹 0000)

<strong>File Server Status (C.1.2)</strong> — FS가 주기 송신하는 상태 메시지. 이 메시지가 6초간 끊기면 FS 셧다운 가능성으로 보고 클라이언트는 통신 리소스를 해제할 수 있다.

| 항목 | 내용 |
|------|------|
| 송신 주기 | busy 아닐 때 2 000 ms, busy reading/writing일 때 200 ms, byte 2 변경 시 초당 최대 5회 |
| 방향/주소 | FS → client, global address(FF₁₆) 사용 |
| 배치 | Byte 1 = 00₁₆(function 0), Byte 2 = File Server Status, Byte 3 = Number of Open Files, Byte 4~8 = FF₁₆ |

<strong>Client Connection Maintenance (C.1.3)</strong> — 클라이언트가 연결 유지를 위해 2 000 ms 주기로 보내는 메시지. FS와 활발히 상호작용하는 동안 전송한다. FS가 이 메시지를 <strong>6초</strong>간 못 받으면 그 클라이언트의 열린 파일을 모두 닫고 모든 Handle을 무효화하며 working directory도 기본값으로 되돌린다. 클라이언트가 Handle을 정리하지 못하고 버스에서 이탈해도 FS가 리소스를 회수할 수 있게 하는 장치다. Byte 2에 Version Number를 담는다.

<strong>Get File Server Properties / Response (C.1.4, C.1.5)</strong> — 클라이언트가 FS 속성을 요청. 응답(function 1)의 배치: Byte 2 = Version Number, Byte 3 = Maximum Number of Simultaneously Open Files, Byte 4 = File Server Capabilities.

:::tip Connection Management에는 TAN이 없다
Get Current Directory 이후의 명령·응답 메시지는 Byte 2에 TAN을 싣지만, File Server Status·Client Connection Maintenance·Get File Server Properties는 상태성 메시지라 TAN을 쓰지 않는다.
:::

<strong>Volume Status Request / Response (C.1.6, C.1.7)</strong> — Version 3 이후 적용. 이동식 매체의 안전한 제거를 위한 메커니즘이다.

- 요청(function 2): Byte 2 = Volume Mode, Byte 3,4 = Path Name Length, Byte 5~n = Volume Name. Path Name Length가 0이면 클라이언트 current directory의 볼륨 상태를 요청하는 것이다.
- 응답: Byte 2 = Volume Status, Byte 3 = Maximum Time Before Volume Removal, Byte 4 = Error Code, Byte 5,6 = Path Name Length, Byte 7~n = Volume Name.
- 볼륨 상태가 <strong>변경</strong>되면 FS는 응답을 global address로 보내 모든 클라이언트에게 알린다(이 경우 에러 코드는 Success일 수밖에 없고, 실패 응답은 요청자에게만 보낸다). Volume Name `\\`는 모든 볼륨의 상태 변경을 의미한다.

볼륨 제거 흐름:

| 단계 | 동작 |
|------|------|
| 1 | FS가 이동식 볼륨 감지 → "Present" 보고 |
| 2 | 어떤 클라이언트가 "Request volume to prepare for removal" 전송 → FS가 "Preparing for removal"을 전파, 모든 클라이언트는 해당 볼륨의 파일·디렉터리를 닫아야 함 |
| 3 | 제거를 지연하려는 클라이언트는 Volume Status Request로 "in use" 보고(Maintain)를 계속 보내야 함. FS는 마지막 Maintain 후 2초, 최대 Maximum Time Before Volume Removal까지 볼륨을 유지 |
| 4 | 모든 클라이언트가 파일을 닫으면 "Removed" 상태를 전 클라이언트에 전파. 모두가 미사용을 보고하면 즉시 제거 가능 |

이동식이 아닌 볼륨에 제거 준비를 요청하거나, Path Name Length 0인데 current directory가 없으면 "Invalid Access" 에러를 반환한다. 볼륨에 열린 파일·디렉터리가 있거나 "Preparing for removal"에 Maintain 요청이 있었던 경우 상태 조회에는 "In use"로 보고한다.

### Directory Handling (커맨드 그룹 0001)

current directory를 조회·변경하는 명령이다. 경로 인자에 디렉터리가 지정되지 않은 요청은 current directory 기준으로 처리된다.

| 명령 | function | 요청 배치 | 응답 배치 |
|------|----------|-----------|-----------|
| Get Current Directory (C.2.2) | 16₁₀ | Byte 2 = TAN | Byte 2 = TAN, Byte 3 = Error Code, Byte 4~7 = Total Space, Byte 8~11 = Free Space(둘 다 512바이트 단위), Byte 12,13 = Path Name Length, Byte 14~n = Path Name |
| Change Current Directory (C.2.3) | 17₁₀ | Byte 2 = TAN, Byte 3,4 = Path Name Length, Byte 5~n = Path Name | Byte 2 = TAN, Byte 3 = Error Code |

Get Current Directory는 성공 시 `\\VOL\DIR\SUBDIR` 형태의 전체 경로를 반환한다.

### File Access (커맨드 그룹 0010)

파일 열기·닫기, 파일 내 이동, 읽기·쓰기 명령이다. 별도의 Create File 명령은 없고, Open File에 "생성" 플래그를 세워 파일을 만든다(C.3.2).

<strong>Open File (C.3.3, function 32₁₀)</strong>

| 방향 | 배치 |
|------|------|
| 요청 | Byte 2 = TAN, Byte 3 = Flags(B.14), Byte 4,5 = Path Name Length, Byte 6~n = Volume/Path/File/Wildcard Name |
| 응답 | Byte 2 = TAN, Byte 3 = Error Code, Byte 4 = Handle, Byte 5 = Attributes |

성공 시 반환된 Handle을 이후 모든 파일 연산에 사용한다.

<strong>Seek File (C.3.4, function 33₁₀)</strong> — 다음 접근을 위한 파일 포인터 설정.

| 방향 | 배치 |
|------|------|
| 요청 | Byte 2 = TAN, Byte 3 = Handle, Byte 4 = Position Mode, Byte 5~8 = Offset |
| 응답 | Byte 2 = TAN, Byte 3 = Error Code, Byte 4 = FF₁₆, Byte 5~8 = Position(새 위치) |

새 위치 계산: mode 0 → 파일 시작 + offset(양수·0만), mode 1 → 현재 위치 + offset(양·음수 가능), mode 2 → 파일 끝 + offset(음수·0만). Handle이 파일이면 바이트 단위, 디렉터리면 Directory Entry 단위다. 포인터가 이미 EOF인데 EOF 너머로 이동을 요청하면 "File pointer at end of file"(45) 에러를 반환한다.

<strong>Read File (C.3.5, function 34₁₀)</strong> — Handle이 가리키는 파일 또는 디렉터리 읽기.

| 방향 | 배치 |
|------|------|
| 요청 | Byte 2 = TAN, Byte 3 = Handle, Byte 4,5 = Count, Byte 6 = Report Hidden Files |
| 응답(파일) | Byte 2 = TAN, Byte 3 = Error Code, Byte 4,5 = Count, Byte 6~n = Data |
| 응답(디렉터리) | Byte 2 = TAN, Byte 3 = Error Code, Byte 4,5 = Count(엔트리 수), Byte 6~n = Directory Entries(B.21) |

- 응답 데이터(파라미터 제외)는 TP 사용 시 최대 <strong>1 780바이트</strong>, ETP 사용 시 최대 <strong>65 530바이트</strong>.
- EOF에 도달하면 요청보다 적게 읽힐 수 있다.
- Handle이 디렉터리면 Count는 읽을 디렉터리 엔트리 수이고, Report Hidden Files가 hidden 파일 포함 여부를 결정한다.
- 포인터가 EOF인데 그 너머 읽기를 요청하면 "File pointer at end of file" 에러.

<strong>Write File (C.3.6, function 35₁₀)</strong> — Handle이 가리키는 열린 파일에 데이터 쓰기.

| 방향 | 배치 |
|------|------|
| 요청 | Byte 2 = TAN, Byte 3 = Handle, Byte 4,5 = Count, Byte 6~n = Data |
| 응답 | Byte 2 = TAN, Byte 3 = Error Code, Byte 4,5 = Count(실제 쓴 수) |

쓰기 데이터도 TP 최대 1 780바이트, ETP 최대 65 530바이트. 디렉터리를 가리키는 Handle에는 Write File을 쓸 수 없다.

<strong>Close File (C.3.7, function 36₁₀)</strong> — Handle이 가리키는 파일 닫기. 내부 버퍼를 모두 기록하고 디렉터리 엔트리를 갱신한다. Close File Response 이후 그 Handle은 무효다.

| 방향 | 배치 |
|------|------|
| 요청 | Byte 2 = TAN, Byte 3 = Handle |
| 응답 | Byte 2 = TAN, Byte 3 = Error Code |

Close File의 주요 에러 코드: Access denied(1), Invalid Handle(5), Volume out of free space(8), Failure during a write operation(9), Out of memory(43), Any other error(44). 버퍼 플러시가 닫기 시점에 일어나므로 쓰기·공간 관련 에러가 여기서도 발생할 수 있다.

### File Handling (커맨드 그룹 0011)

파일 이동·복사·삭제, 속성 조회·설정, 날짜·시간 조회 명령이다. Handle이 아니라 <strong>경로 문자열</strong>로 대상을 지정한다는 점이 File Access 그룹과 다르다.

<strong>Move File (C.4.2, function 48₁₀)</strong> — 파일을 이동·복사·이름 변경하는 통합 명령이다. 동작은 File Handling Mode(B.27)와 목적지 지정에 따라 결정된다.

| 조건 | 동작 |
|------|------|
| 목적지 파일명이 현재 이름과 다름 | 이름 변경(rename) |
| 목적지 경로가 소스 경로와 다름 | 이동(move) |
| 목적지 경로에 없는 디렉터리 포함 | 해당 디렉터리 생성 |
| Copy 모드 설정 | 복사(copy) |

규칙:

- 목적지에 같은 디렉터리·파일이 이미 있으면 <strong>force 모드가 아닌 한</strong> "Access denied"를 반환한다.
- 하위 디렉터리·파일을 포함한 디렉터리를 이동·복사하려면 <strong>recursive 모드</strong>가 필요하다. 없으면 "Access denied".
- recursive 이동·복사의 목적지가 소스 경로 안(자기 자신 또는 하위 폴더)이면 "Access denied".
- 디렉터리를 지정할 때는 경로 끝에 `\`를 붙여 디렉터리임을 표시한다.

| 방향 | 배치 |
|------|------|
| 요청 | Byte 2 = TAN, Byte 3 = File Handling Mode, Byte 4,5 = Source Path Name Length, Byte 6,7 = Destination Path Name Length, Byte 8~n = Source 경로, Byte (n+1)~m = Destination 경로 |
| 응답 | Byte 2 = TAN, Byte 3 = Error Code |

<strong>Delete File (C.4.3, function 49₁₀)</strong> — 파일 삭제. 동작 방식은 File Handling Mode로 지정한다.

- write-protected 파일이거나 write-protected 파일을 포함한 디렉터리면 <strong>force 모드</strong>가 없는 한 "Access Denied".
- 파일이 들어 있는 디렉터리면 <strong>recursive 모드</strong>가 없는 한 "Access Denied".
- write-protected 파일을 하나라도 포함한 디렉터리를 지우려면 force + recursive 둘 다 필요하다.

| 방향 | 배치 |
|------|------|
| 요청 | Byte 2 = TAN, Byte 3 = File Handling Mode, Byte 4,5 = Path Name Length, Byte 6~n = 경로 |
| 응답 | Byte 2 = TAN, Byte 3 = Error Code |

<strong>Get File Attributes (C.4.4, function 50₁₀)</strong> — 경로로 지정한 파일·디렉터리의 속성 조회.

| 방향 | 배치 |
|------|------|
| 요청 | Byte 2 = TAN, Byte 3,4 = Path Name Length, Byte 5~n = 경로(와일드카드 불가, B.35) |
| 응답 | Byte 2 = TAN, Byte 3 = Error Code, Byte 4 = Attributes(B.15), Byte 5~8 = Size |

<strong>Set File Attributes (C.4.5, function 51₁₀)</strong> — 경로로 지정한 파일·디렉터리의 속성 비트를 설정·해제.

| 방향 | 배치 |
|------|------|
| 요청 | Byte 2 = TAN, Byte 3 = Set Attributes Command(B.16), Byte 4,5 = Path Name Length, Byte 6~n = 경로(와일드카드 가능, B.34) |
| 응답 | Byte 2 = TAN, Byte 3 = Error Code |

<strong>Get File Date & Time (C.4.6, function 52₁₀)</strong> — 경로로 지정한 파일·디렉터리의 날짜·시간 조회.

| 방향 | 배치 |
|------|------|
| 요청 | Byte 2 = TAN, Byte 3,4 = Path Name Length, Byte 5~n = 경로(B.35) |
| 응답 | Byte 2 = TAN, Byte 3 = Error Code, Byte 4,5 = File Date(B.24), Byte 6,7 = File Time(B.25) |

### Volume Access (커맨드 그룹 0100)

볼륨을 파일·디렉터리 구조를 담을 수 있게 준비·복구하는 명령이다. 초기 설정 용도로 제한될 수 있으며, <strong>서비스 툴 클라이언트 전용</strong>으로 의도된 명령이다.

<strong>Initialize Volume (C.5.2, function 64₁₀)</strong> — 볼륨을 초기화해 파일·디렉터리를 받을 수 있게 만든다.

:::warning 데이터 전체 소실
Initialize Volume이 완료되면 볼륨의 모든 데이터가 유실된다. 일반 클라이언트가 아닌 서비스 툴이 쓰는 명령이다.
:::

| 방향 | 배치 |
|------|------|
| 요청 | Byte 2 = TAN, Byte 3~6 = Space(512바이트 단위), Byte 7 = Volume Flags(B.29), Byte 8,9 = Path Name Length, Byte 10~n = Volume Name |
| 응답 | Byte 2 = TAN, Byte 3 = Error Code, Byte 4 = Attributes(B.15) |

Volume Flags로 "가용 공간 전체/지정 공간", "기존 볼륨 있으면 실패/덮어쓰기"를 조합한다. 응답 에러 코드에는 Invalid request length(42, 잘못된 공간 요청)도 포함된다.

## Annex D — 일반 파일 시스템 예시 (informative)

FS 구현에 흔히 쓰이는 파일 시스템별 파일명 제약을 참고용으로 정리한 표다(ISO의 제품 보증 아님).

| 파일 시스템 | 최대 길이 | 최대 바이트 | 허용 문자 | 대소문자 구분 |
|-------------|-----------|-------------|-----------|----------------|
| Microsoft FAT-12/16/32 (8.3) | 8.3, 1바이트 문자 | 12 | 제어문자(0~31), 127, 소문자 a~z, `\ / : * ? " < >` 제외한 ASCII. CON, PRN, AUX, NUL, COM1~9, LPT1~9 이름 금지 | 아니오 |
| Microsoft FAT-32 (LFN) | 255자(2바이트 문자) | 510 | NUL, `\ / : * ? " < > \|` 제외한 ASCII/UTF-16. 예약 이름 동일 금지 | 아니오 |
| Microsoft NTFS | 255자(2바이트 문자) | 510 | FAT-32 LFN과 동일 | 아니오 |
| Linux ext2/ext3/ext4 | 255바이트 | 255 | NUL, `/` 제외한 ASCII/UTF-16 | 예 |
| Macintosh/iPod HFS | 255자(2바이트 문자) | 510 | NUL 포함 모든 ASCII/UTF-16 (Apple 변형 Unicode NFD로 정규화) | — |

Annex A의 이름 규칙(ShortNameChar에서 소문자·`/`·`:` 등 제외, 254자 제한)은 이들 파일 시스템에서 기능 손실을 최소화하도록 설계된 것이다.

## 정리

Part 13은 ISO 11783 네트워크에서 파일 저장이라는 인프라 기능을 담당한다. 핵심 골격은 다음과 같다.

- <strong>연결 모델</strong>: 클라이언트가 Client Connection Maintenance를 2초 주기로 보내 연결을 유지하고, FS는 File Server Status를 방송한다. 어느 쪽이든 6초간 끊기면 상대 리소스를 정리한다.
- <strong>신뢰성</strong>: 요청-응답 쌍에 TAN을 붙여 재시도 시 중복 실행을 막는다. FS는 클라이언트별 마지막 응답을 캐시해 같은 TAN 요청에 재전송으로 답한다.
- <strong>명령 체계</strong>: 바이트 1 하나에 커맨드 그룹(상위 4비트) + 함수(하위 4비트)를 인코딩한다. Connection Management(0), Directory Handling(1), File Access(2), File Handling(3), Volume Handling(4)의 5개 그룹이다.
- <strong>데이터 전송</strong>: PGN 2개(AA00₁₆ 클라이언트→FS, AB00₁₆ FS→클라이언트)로 모든 메시지를 실어 나르며, 큰 데이터는 TP(최대 1 780바이트)·ETP(최대 65 530바이트)를 쓴다.
- <strong>파일 시스템 추상화</strong>: 볼륨 목록 `\\` 최상위, 8.3/long filename 이중 지원, 제조사 전용 디렉터리(`MCMC0000`, `~` 단축)와 접근 통제, 이동식 매체의 안전 제거 프로토콜(Version 3 신설)까지 포함한다.

Task Controller(Part 10)의 로그 데이터 저장 등 대용량 데이터를 다루는 ECU가 자체 저장소 없이 네트워크 공용 저장소를 쓸 수 있게 하는 것이 이 파트의 실용적 의의다.

