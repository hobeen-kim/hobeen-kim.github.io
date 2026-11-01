---
title: "File Server 세부: 볼륨, 경로, 파라미터, 바이트 따라가기"
description: "이동식 볼륨을 안전하게 빼는 절차, 경로와 파일 이름 규칙, 플래그·속성·에러 코드를 익히고, 디렉터리 목록을 읽는 대화를 바이트 단위로 따라간다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, FileServer]
prev: /study/isobus/51-file-server-basics
next: /study/isobus/53-sequence-control-basics
---

# File Server 세부: 볼륨, 경로, 파라미터, 바이트 따라가기

::: info 학습 목표
- 볼륨이 무엇인지 설명하고, Volume Status 메시지로 이동식 매체를 안전하게 빼는 순서를 말할 수 있다.
- current directory를 기준으로 상대 경로, `..`, `~`, `\\`가 든 경로가 어디를 가리키는지 구할 수 있다.
- Open File의 Flags와 Attributes 바이트를 비트로 풀고, 명령마다 돌아올 수 있는 에러 코드를 찾을 수 있다.
- 디렉터리 목록을 읽는 요청과 응답을 바이트 단위로 따라가고, 디렉터리 엔트리의 이름·날짜·시간·크기를 풀어 읽을 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [51장 File Server(FS) 기초](/study/isobus/51-file-server-basics), [15장 Transport Protocol 기초](/study/isobus/15-tp-bam-cmdt)
- 이 장에서 처음 나오는 말
  - 이동식 매체: USB 메모리처럼 FS에 꽂았다 뺐다 할 수 있는 저장 매체
  - Volume Status: 볼륨의 상태(있음, 사용 중, 제거 준비 중, 제거됨)를 묻고 알리는 메시지
  - 8.3 이름: 이름 8자와 확장자 3자로 제한된 옛 파일 이름 방식. 예: `TASK0413.XML`
  - 와일드카드: 여러 이름에 한꺼번에 맞는 글자. `*`는 아무 글자 여러 개, `?`는 아무 글자 하나에 맞는다
  - 디렉터리 엔트리(Directory Entry): 디렉터리 목록에서 파일 하나를 설명하는 바이트 묶음. 이름, 속성, 날짜, 시간, 크기가 들어 있다
:::

컴퓨터에서 USB 메모리를 뽑을 때는 "안전하게 제거"를 먼저 누르고, 파일 경로에 `..`을 쓰면 한 단계 위 폴더로 간다. [51장](/study/isobus/51-file-server-basics)에서 본 FS에도 이런 세부 규칙이 있다. 이 장은 이동식 볼륨을 빼는 절차, 경로와 이름 규칙, Flags·Attributes 같은 바이트의 비트 뜻을 정리하고, 마지막에 디렉터리 목록 하나를 읽는 대화를 바이트 단위로 따라간다.

## 1. 볼륨: 저장 매체마다 붙는 이름

이 절에서는 볼륨이 정확히 무엇인지 정하고, 볼륨이 어떻게 생기는지 본다.

[51장](/study/isobus/51-file-server-basics)에서는 볼륨을 컴퓨터의 드라이브(C: 드라이브, USB 드라이브)에 비유했다. 표준의 정의로 볼륨은 특정 논리·물리 저장 단위를 가리키는 디렉터리다. FLASH, 이동식 매체, 견고형 디스크를 서로 다른 볼륨에 둘 수 있고, 초기화되지 않은 매체나 장치가 없어서 볼륨이 하나도 없는 FS도 있을 수 있다. 볼륨 목록 `\\`가 디렉터리 구조의 최상위다.

볼륨 이름은 FS가 정한다. 이 스터디의 예에서는 내부 플래시를 `FLASH`, 이동식 매체를 `VOL_B`라고 부른다. 볼륨을 새로 만들거나 지우고 다시 만드는 일은 서비스 툴(정비할 때 쓰는 전용 장비나 프로그램)이 Initialize Volume 명령으로 한다. 이 명령의 바이트 배치는 바로 아래 심화 소절에 있다.

정리하면 볼륨은 저장 매체 하나에 붙은 이름이자 맨 위의 디렉터리이고, 볼륨들의 목록이 `\\`다.

### 볼륨을 만드는 Initialize Volume (심화)

::: info 처음 읽는다면
이 소절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

볼륨 생성·초기화는 서비스 툴용 Initialize Volume(`0x40`, =64)이 맡고, 완료되면 볼륨의 데이터가 모두 사라진다. 요청의 Byte 1은 0x40, Byte 2는 TAN이고, 그 뒤는 Byte 3~6 Space(512바이트 단위), Byte 7 Volume Flags, Byte 8~9 이름 길이, Byte 10~ Volume Name이다. Space가 2 048이면 2 048 × 512 = 1 048 576바이트(1 MiB)라는 뜻이다.

Volume Flags의 bit 1은 0이면 가용 공간 전부, 1이면 지정한 공간을 쓰고, bit 0은 0이면 같은 볼륨이 있을 때 실패, 1이면 덮어쓴다. 잘못된 공간 요청에는 Invalid request length(42)가 돌아온다. 볼륨 이름은 FS가 정하지만 서비스 툴이 이름을 붙이게 허용할 수 있고, 목록에 없는 매체를 서비스 툴이 어떻게 고르는지는 정하지 않는다.

<small>근거: ISO 11783-13 3.11, 5.7, B.11, B.29, C.5.2</small>

## 2. 이동식 매체를 안전하게 빼기: Volume Status

이 절에서는 USB 메모리 같은 이동식 매체를 FS에서 뺄 때, 클라이언트들과 FS가 주고받는 메시지와 그 순서를 본다.

컴퓨터에서 USB 메모리를 그냥 뽑으면 쓰던 파일이 망가질 수 있어서 "안전하게 제거" 단계를 거친다. FS는 더 조심해야 한다. 여러 클라이언트가 같은 매체에 파일을 열어 두었을 수 있기 때문이다. 그래서 매체를 빼기 전에 모두에게 알리고, 파일을 닫을 시간을 준다.

Volume Status(`0x02`, =2)는 Version 3에서 생긴 메시지로, 이동식 매체를 안전하게 빼는 데 쓴다. Version 3은 ISO 11783-13 2판을 따르는 FS라는 뜻이다([51장](/study/isobus/51-file-server-basics) 5절 참고). 아래 표는 요청과 응답을 바이트 번호별로 나란히 놓은 것이다. 바이트 번호는 1부터 센다. Path Name Length처럼 2바이트를 차지하는 칸은 다음 줄에 〃(위와 같음)로 이어 적었고, 2바이트 값은 낮은 자리 바이트가 먼저 온다. 칸 안의 괄호 숫자(3~4, 5~6, 7~)는 그 값이 차지하는 바이트 번호다.

| 바이트 | Volume Status Request (클라이언트 → FS) | Volume Status Response (FS → 클라이언트 또는 전역) |
|---|---|---|
| 1 | 0x02 | 0x02 |
| 2 | Volume Mode: bit 1 = 제거 준비 요청, bit 0 = 1 사용 중 / 0 사용 안 함. 0x00이면 현재 상태 조회 | Volume Status: 0 Present, 1 In use, 2 Preparing for removal, 3 Removed |
| 3 | Path Name Length (3~4). 0이면 current directory의 볼륨 | Maximum Time Before Volume Removal (1 min/bit, 0~250) |
| 4 | 〃 | Error Code: 0, 1, 2, 4, 6, 43, 44 |
| 5 ~ | Volume Name | Path Name Length (5~6), Volume Name (7~) |

표에서 처음 보는 값을 풀면 다음과 같다.

- Volume Mode(요청 Byte 2): 비트 두 개를 쓴다. bit 1이 1이면 "이 볼륨을 뺄 준비를 해 달라"는 요청이다. bit 0은 이 클라이언트가 볼륨을 쓰고 있는지(1) 쓰지 않는지(0) 보고한다. 0x00은 현재 상태를 묻는 값인데, 비트로 보면 "사용 안 함" 보고와 같은 값이다. 0x01은 "쓰고 있으니 붙잡아 달라"는 Maintain 요청, 0x02는 제거 준비 요청이다.
- Volume Status(응답 Byte 2): 볼륨의 현재 상태다. 0 Present(있음), 1 In use(사용 중), 2 Preparing for removal(제거 준비 중), 3 Removed(제거됨)이다.
- Maximum Time Before Volume Removal(응답 Byte 3): 값 1이 1분이다. 0~250이므로 최대 250분까지 나타낸다. FS가 볼륨을 붙잡아 둘 수 있는 최대 시간이다.
- 에러 코드(Error Code, 응답 Byte 4): 0이면 성공이다. 이 메시지에 올 수 있는 값은 0, 1, 2, 4, 6, 43, 44다.

제거 절차는 다음과 같다. 아래 그림은 클라이언트 A가 매체를 빼려 하고, 클라이언트 B가 그 매체의 파일을 쓰고 있던 경우다. 주황색 점선은 모든 장치에 보내는 전역 통지다.

![이동식 볼륨 제거 절차: FS가 Present를 전역으로 알리고, 클라이언트 A의 제거 준비 요청 뒤 Preparing for removal을 전역 통지하며, 파일을 쓰던 클라이언트 B가 Maintain을 보내다가 파일을 닫고 사용 안 함을 보고하면 Removed를 전역 통지하는 흐름](/images/study-isobus/21-fs-volume-removal-light.png)
![이동식 볼륨 제거 절차: FS가 Present를 전역으로 알리고, 클라이언트 A의 제거 준비 요청 뒤 Preparing for removal을 전역 통지하며, 파일을 쓰던 클라이언트 B가 Maintain을 보내다가 파일을 닫고 사용 안 함을 보고하면 Removed를 전역 통지하는 흐름](/images/study-isobus/21-fs-volume-removal-dark.png)

1. FS가 이동식 볼륨을 감지하면 Present를 알린다.
2. 어떤 클라이언트가 제거 준비(Volume Mode bit 1)를 요청하면 FS는 Preparing for removal을 알리고, 모든 클라이언트는 그 볼륨의 파일·디렉터리를 닫아야 한다.
3. 볼륨을 붙잡아 두려는 클라이언트는 "사용 중"(bit 0 = 1) 요청, 곧 Maintain을 계속 보내야 한다. FS는 마지막 Maintain 뒤 2 s 동안 볼륨을 유지하되 Maximum Time Before Volume Removal을 넘기지 않는다.
4. 모든 클라이언트가 파일을 닫으면 FS는 Removed를 모든 클라이언트에 알린다. 모든 클라이언트가 사용 안 함을 보고하면 바로 제거해도 된다.

이 절차에 딸린 규칙은 다음과 같다.

- 상태 변화는 전역 주소(DA 0xFF)로 알린다. 클라이언트 요청 때문에 바뀐 경우에도 전역으로 보낸다. 그 볼륨을 쓰는 클라이언트가 모두 알아야 하기 때문이다. 전역 응답은 상태가 바뀌었다는 뜻이라 에러 코드가 Success이고, 실패 응답은 요청자에게만 보낸다. Volume Name이 `\\`이면 모든 볼륨의 상태 변화를 뜻한다.
- 상태를 물었을 때 그 볼륨에 열린 파일·디렉터리가 있거나, Preparing for removal 중 Maintain을 받았다면 In use로 답한다.
- 이동식이 아닌 볼륨에 제거 준비를 요청하거나, Path Name Length가 0인데 current directory가 없으면 Invalid Access(2)다.
- Maximum Time Before Volume Removal은 FS가 정한다. 매체를 꺼낼 때 사용자에게 보여 주는 시간일 수도, 전원이 꺼질 때 FS가 버틸 수 있는 시간일 수도 있다.

current directory의 볼륨을 대상으로 한 요청은 상태 조회 `02 00 00 00 FF FF FF FF`, Maintain `02 01 00 00 FF FF FF FF`, 제거 준비 요청 `02 02 00 00 FF FF FF FF`다. 첫 요청을 끊어 읽으면 Byte 1 `02`(Volume Status), Byte 2 `00`(Volume Mode), Byte 3~4 `00 00`(Path Name Length 0, 곧 current directory의 볼륨), 나머지는 쓰지 않는 자리라 0xFF로 채운 것이다. 나머지 두 요청은 Byte 2만 다르다.

특정 볼륨을 지정할 때 Volume Name에 `\\VOL_B`처럼 볼륨 목록 표시를 붙이는지, `VOL_B`만 쓰는지는 표준에 예가 없어 확인이 필요하다.

::: warning Version 2 FS와 Volume Status
Volume Status는 Version 3 이상 FS에만 적용된다. 그런데 표준이 "미지원 함수에는 error 12로 답하라"고 정한 그룹 목록에 Connection Management가 빠져 있어서([51장](/study/isobus/51-file-server-basics) 6절 참고), Version 2 FS가 이 요청에 어떻게 반응할지는 표준만으로 알 수 없다. 표준에 적힌 방법은 아니지만, Get File Server Properties 응답의 Version Number가 3 이상인지 먼저 확인하고 쓰는 편이 안전하다.
:::

정리하면 이동식 볼륨은 Present → Preparing for removal → Removed 순서로 상태가 바뀌고, 상태가 바뀔 때마다 FS가 모든 장치에 알린다. 클라이언트는 제거 준비 통지를 받으면 파일을 닫고, 더 써야 하면 Maintain으로 시간을 번다.

::: details 원문을 가진 독자를 위한 메모
- C.1.6(Volume Status Request)의 Byte 1 함수 이름은 "Removable Media Status"로, C.1.7(Volume Status Response)은 "Volume Status"로 적혀 있다. 같은 함수(0x02)다.
- Volume Name 표기가 불확실한 이유: C.1.6은 B.34(볼륨·경로·파일·와일드카드 이름)를 참조하고, B.33의 VolumeName 문법에는 `\`가 없어 확인 필요다.
- Version 2 경고의 근거: Volume Status가 Version 3 이상에만 적용된다는 문장은 B.30과 C.1.6에, error 12로 답할 그룹 목록은 C.1.1에 있다.
:::

<small>근거: ISO 11783-13 5.7, B.30~B.32, C.1.1, C.1.6, C.1.7</small>

## 3. 경로 문법과 특수 이름

이 절에서는 파일 이름에 쓸 수 있는 글자와 길이, 그리고 `..`, `~`, `\\`, 와일드카드 같은 특수 표기가 어떻게 해석되는지 본다.

FS는 서로 다른 회사가 만든 여러 클라이언트가 함께 쓴다. 한 클라이언트가 만든 이름을 FS 안의 파일 시스템이나 다른 클라이언트가 다루지 못하면 곤란하므로, 쓸 수 있는 글자와 길이를 미리 정해 둔다.

- <strong>8.3 이름과 긴 이름.</strong> 긴 파일 이름을 지원하지 않는 FS는 이름 최대 8자에 점과 확장자 최대 3자를 쓴다. 이때 쓸 수 있는 문자(ShortNameChar)는 숫자, 대문자, 기호 `- ! # $ % & ' ( ) @ ^ _`와 백틱, `{ } ~`, 0xA1~0xFF이고, 소문자와 공백은 없다. 0xA1~0xFF(161~255)는 ISO/IEC 8859-1(서유럽 문자를 담는 1바이트 문자 집합)에서 기호와 악센트 붙은 글자가 있는 영역이다. 대소문자를 구분하지 않는 FS는 소문자(0x61~0x7A, 곧 a~z)를 대문자(0x41~0x5A, 곧 A~Z)로 바꾼다. 긴 이름은 1~254자이고 NUL(값 0인 문자), `\`, `*`, `?`만 빼고 쓸 수 있다.
- <strong>길이 필드.</strong> Filename Length는 8.3 FS에서 최대 12(이름 8 + 점 1 + 확장자 3), 긴 이름 FS에서 최대 254다. Version 2 이하는 31자였다.

current directory가 `\\VOL_B\LOGS\`이고 클라이언트의 제조사 코드가 123(예시)일 때, FS가 경로를 해석하는 방식은 다음과 같다. `MCMC0123`은 제조사마다 쓰는 전용 디렉터리 이름이다([51장](/study/isobus/51-file-server-basics) 7절 참고).

| 요청 경로 | FS가 해석한 위치 | 규칙 |
|---|---|---|
| `TASK.XML` | `\\VOL_B\LOGS\TASK.XML` | current directory 기준 |
| `..\CFG\A.TXT` | `\\VOL_B\CFG\A.TXT` | `..`은 상위 디렉터리 |
| `\CFG\A.TXT` | `\\VOL_B\CFG\A.TXT` | `\` 하나로 시작하면 current volume 루트 기준 |
| `~\A.TXT` | `\\VOL_B\MCMC0123\A.TXT` | `~`는 current volume의 전용 디렉터리 |
| `\\FLASH\~\A.TXT` | `\\FLASH\MCMC0123\A.TXT` | 볼륨 이름 뒤의 `~` |
| `\\` | 볼륨 목록 | 디렉터리 목록을 요청하면 볼륨을 나열한다 |

같은 표를 트리로 그리면 다음과 같다. 오른쪽의 요청 경로가 왼쪽 트리의 어느 칸을 가리키는지 화살표로 이었다.

![경로 해석: current directory가 VOL_B 아래 LOGS일 때 요청 경로 여섯 개가 가리키는 위치를 화살표로 이은 트리. TASK.XML은 LOGS 안의 파일, 상위 이동 경로와 볼륨 루트 기준 경로는 둘 다 VOL_B 아래 CFG의 A.TXT, 물결표 경로는 VOL_B와 FLASH 각각의 MCMC0123 안의 A.TXT, 볼륨 목록 표시는 맨 위의 볼륨 목록을 가리킨다](/images/study-isobus/52-fs-path-resolution-light.png)
![경로 해석: current directory가 VOL_B 아래 LOGS일 때 요청 경로 여섯 개가 가리키는 위치를 화살표로 이은 트리. TASK.XML은 LOGS 안의 파일, 상위 이동 경로와 볼륨 루트 기준 경로는 둘 다 VOL_B 아래 CFG의 A.TXT, 물결표 경로는 VOL_B와 FLASH 각각의 MCMC0123 안의 A.TXT, 볼륨 목록 표시는 맨 위의 볼륨 목록을 가리킨다](/images/study-isobus/52-fs-path-resolution-dark.png)

- `.`과 `..`은 경로에 쓸 수 있지만 디렉터리 목록에는 나오지 않는다. `.`은 지금 디렉터리, `..`은 한 단계 위 디렉터리다. 볼륨이 하나뿐인 FS도 `\\` 목록을 지원해야 한다. 클라이언트가 이동식 매체를 조회할 수 있게 하려는 것이다.
- Move·Copy에서 디렉터리를 가리킬 때는 경로 끝에 `\`를 붙인다.
- <strong>와일드카드.</strong> `*`는 0자 이상, `?`는 정확히 1자에 맞고, 디렉터리 목록에만 써야 한다. Open File의 경로 필드는 와일드카드 이름까지 받도록 정의돼 있으므로, 걸러진 목록이 필요하면 `\\VOL_B\LOGS\*.XML`을 디렉터리로 열고(Flags 0x03) Read File로 읽는 식이 된다. 표준에 이 예가 직접 있지는 않고, 정의에서 끌어낸 추론이다. Move·Delete·Set File Attributes의 경로 필드도 정의상 와일드카드 이름을 받지만, 이름 규칙이 와일드카드를 디렉터리 목록에 한정하므로 일괄 처리를 와일드카드에 기대지 않는 편이 안전하다(이것도 추론이다). Get File Attributes와 Get File Date & Time의 경로 필드는 처음부터 와일드카드를 받지 않는다.
- <strong>문자 인코딩.</strong> 길이 필드(Path Name Length, Filename Length)는 바이트 수가 아니라 "문자 수"다. 긴 이름은 Unicode 문자(세계의 여러 문자를 한 체계로 모은 문자 집합)를 허용하지만, 그 문자를 바이트로 어떻게 인코딩하는지는 표준에 없다. 한글처럼 ISO/IEC 8859-1 범위 밖 문자는 확인 필요다.

표준의 참고 부록은 FS 구현에 흔히 쓰는 파일 시스템의 이름 제약을 든다. FAT(8.3)는 소문자를 쓸 수 없고 CON·PRN·AUX·NUL·COM1~9·LPT1~9 같은 이름을 막으며, ext2~4는 대소문자를 구분한다. FAT은 USB 메모리에 흔히 쓰는 파일 시스템이고, ext2~4는 리눅스의 파일 시스템이다. FS의 이름 규칙은 이런 파일 시스템에서 기능 손실이 적도록 정한 것이다. 볼륨의 대소문자 구분 여부는 Attributes bit 7로 알린다(Version 3 이상).

정리하면 경로는 current directory를 기준으로 읽고, `\`로 시작하면 current volume의 루트, `..`은 상위, `~`는 제조사 전용 디렉터리, `\\`는 볼륨 목록이다. 이름은 8.3이면 12자, 긴 이름이면 254자까지다.

::: details 원문을 가진 독자를 위한 메모
- 이름 문자 규정은 A.1과 A.2.2.1, 길이 필드는 B.12와 B.22, 경로 해석은 A.2.3과 A.2.3.1, 와일드카드를 목록에 한정하는 규정은 A.2.3.3, Move·Copy의 끝 `\` 규칙은 C.4.2.1이다.
- 경로 필드의 참조: Open File·Move·Delete·Set File Attributes는 B.34(볼륨·경로·파일·와일드카드 이름)를, Get File Attributes와 Get File Date & Time은 와일드카드가 없는 B.35를 쓴다.
- 파일 시스템 이름 제약 예시는 Annex D(참고)이고, 대소문자 구분 비트는 B.15다.
:::

<small>근거: ISO 11783-13 A.1, A.2.2.1, A.2.3, B.12, B.15, B.22, B.34, B.35, C.4.2.1, Annex D</small>

## 4. 파라미터 세부: 플래그, 속성, 에러 코드 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절은 Open File의 Flags, 응답의 Attributes, 파일을 다루는 명령의 모드 바이트, 명령별 에러 코드를 모은 참고 자료다. 비트 번호는 가장 낮은 비트를 bit 0, 가장 높은 비트를 bit 7로 센다.

<strong>Flags.</strong> Open File의 Flags 한 바이트는 다음과 같이 나뉜다.

- bit 1·0: 접근 방식. 00 읽기 전용, 01 쓰기 전용, 10 읽기·쓰기, 11 디렉터리 열기
- bit 2: 1이면 없을 때 파일·디렉터리를 만든다. 0이면 있는 파일만 연다(없으면 실패)
- bit 3: 1이면 파일 포인터를 파일 끝에 둔다(append, 이어 쓰기). 0이면 처음에 둔다
- bit 4: 1이면 배타적으로 연다(이미 열려 있으면 실패). 0이면 공유 읽기로 연다
- bit 7~5: 예약, 000으로 보낸다

예를 들어 0x0D는 2진수 0000 1101이다. bit 1·0이 01(쓰기 전용), bit 2가 1(생성), bit 3이 1(append)이므로 "없으면 만들고, 있으면 끝에 이어 쓴다"가 된다. Open File의 Flags는 다음 조합을 자주 쓴다.

| Flags | 비트 해석 | 쓰임 |
|---|---|---|
| 0x00 | 읽기 전용, 공유, 포인터 처음, 기존 파일만 | 처방 맵 읽기 |
| 0x05 | 쓰기 전용, 없으면 생성 | 새 로그 파일 |
| 0x0D | 쓰기 전용, 생성, append(포인터 끝) | 기존 로그 뒤에 이어 쓰기 |
| 0x16 | 읽기·쓰기, 생성, 배타적(이미 열려 있으면 실패) | 다른 클라이언트와의 동시 수정 방지 |
| 0x03 | 디렉터리 열기 (bit 3 무시, read-only 취급) | 디렉터리 목록 |
| 0x07 | 디렉터리 열기, 생성 | 디렉터리 경로 만들기 |

디렉터리 열기(11)에서 bit 3을 무시하고 읽기 전용으로 다루는 것은, 디렉터리를 열어 하는 일이 목록 보기뿐이기 때문이다.

<strong>Attributes.</strong> Attributes 한 바이트에는 볼륨(bit 7 대소문자 구분, bit 6 이동식 아님, bit 5 긴 이름 지원, bit 2 hidden 지원), Handle(bit 4 디렉터리, bit 3 볼륨), 파일(bit 1 hidden, bit 0 read-only)의 속성이 섞여 있다. bit 7과 bit 2는 Version 3 이상에서만 의미가 있다. 예를 들어 0x70은 고정 볼륨, 긴 이름 지원, 디렉터리를 가리키는 Handle이다. 비트마다 1일 때와 0일 때의 뜻을 표로 펼치면 다음과 같다.

| 비트 | 무엇의 속성 | 1이면 | 0이면 |
|---|---|---|---|
| 7 | 볼륨 | 대소문자를 구분한다(Version 3 이상) | 구분하지 않는다 |
| 6 | 볼륨 | 이동식이 아니다(고정) | 이동식이다 |
| 5 | 볼륨 | 긴 파일 이름을 지원한다 | 지원하지 않는다(8.3 이름) |
| 4 | Handle | 디렉터리를 가리킨다 | 디렉터리가 아니다 |
| 3 | Handle | 볼륨을 가리킨다 | 볼륨이 아니다 |
| 2 | 볼륨 | hidden 속성을 지원한다(Version 3 이상) | 지원하지 않는다 |
| 1 | 파일 | hidden 속성이 켜져 있다 | 꺼져 있다 |
| 0 | 파일 | read-only 속성이 켜져 있다 | 꺼져 있다 |

0x70을 표로 확인하면 0111 0000이라 bit 6(고정 볼륨), bit 5(긴 이름 지원), bit 4(디렉터리)가 1이다.

<strong>Set Attributes.</strong> Set Attributes Command는 2비트씩 00 해제, 01 설정, 11 그대로이고, bit 7~4는 11로 보낸다. 그래서 read-only 설정은 0xFD, 해제는 0xFC, hidden 설정은 0xF7, 해제는 0xF3이다. hidden은 볼륨이 hidden을 지원할 때만 의미가 있다. 예를 들어 0xFD는 1111 1101이다. bit 7~4는 1111(예약), bit 3·2는 11(hidden 그대로), bit 1·0은 01(read-only 설정)이다.

<strong>File Handling Mode.</strong> Move File과 Delete File의 File Handling Mode는 bit 0 copy, bit 1 force, bit 2 recursive다. 0x00은 이동·이름 변경, 0x01은 복사, 0x05는 디렉터리 재귀 복사, 0x06은 read-only 파일이 든 디렉터리 삭제(force와 recursive)다. force는 목적지에 같은 이름이 있거나 read-only 파일이 있어도 진행하라는 표시이고, recursive는 하위 항목까지 통째로 처리하라는 표시다. 두 비트가 무엇을 허락하는지는 Access Denied(1)가 돌아오는 아래 네 경우를 보면 알 수 있다.

1. 목적지에 같은 이름이 이미 있는데 force가 없을 때
2. 하위 항목이 있는 디렉터리를 recursive 없이 옮기거나 지울 때
3. recursive 이동·복사의 목적지가 원본 경로 안일 때
4. 쓰기 보호(read-only) 파일이나 그런 파일이 든 디렉터리를 force 없이 지울 때

<strong>Seek File.</strong> Seek File의 Position Mode는 0이면 파일 처음 + Offset(0 이상), 1이면 현재 위치 + Offset(양·음), 2이면 파일 끝 + Offset(0 이하)이다. Handle이 디렉터리면 단위가 바이트가 아니라 Directory Entry다. 이미 EOF(End Of File, 파일 끝)인 포인터를 EOF 너머로 옮기려 하면 File pointer at end of file(45)이 오고, 표준의 에러 코드 정의는 42(Invalid request length)를 포인터가 파일 처음에 부딪치거나 볼륨 공간 요청이 잘못됐을 때 쓴다고 설명한다.

<strong>명령별 에러 코드.</strong> 명령마다 돌아올 수 있는 에러 코드는 표준의 응답 정의에 따로 나열돼 있다. 클라이언트의 에러 처리 분기를 짤 때 쓰도록 한 표로 모은다. 코드 번호의 뜻은 [51장](/study/isobus/51-file-server-basics) 4절 예제의 `ERROR_CODES`에 있다.

| 명령 | 응답에 올 수 있는 Error Code |
|---|---|
| Volume Status | 0, 1, 2, 4, 6, 43, 44 |
| Get Current Directory | 0, 10, 13, 43, 44 |
| Change Current Directory | 0, 1, 2, 4, 7, 10, 13, 43, 44 |
| Open File | 0, 1, 2, 3, 4, 6, 8, 10, 13, 43, 44 |
| Seek File | 0, 5, 11, 42, 43, 44, 45 |
| Read File (파일) | 0, 1, 5, 11, 42, 43, 44, 45 |
| Read File (디렉터리) | 0, 5, 11, 42, 43, 44, 45 |
| Write File | 0, 1, 5, 8, 9, 42, 43, 44 |
| Close File | 0, 1, 5, 8, 9, 43, 44 |
| Move File | 0, 1, 3, 4, 6, 7, 8, 9, 10, 11, 13, 43, 44 |
| Delete File | 0, 1, 4, 6, 9, 10, 11, 13, 43, 44 |
| Get File Attributes | 0, 1, 3, 4, 6, 10, 11, 13, 43, 44 |
| Set File Attributes | 0, 1, 3, 4, 6, 8, 9, 10, 11, 13, 43, 44 |
| Get File Date & Time | 0, 1, 3, 4, 6, 10, 11, 13, 43, 44 |
| Initialize Volume | 0, 1, 4, 6, 8, 9, 10, 11, 13, 42, 43, 44 |

- 이 표 밖에, 미지원 함수에는 그룹 공통으로 12(Function not supported)가 온다.
- Close File이 8(공간 부족)·9(쓰기 실패)를 돌려줄 수 있는 것은 닫을 때 내부 버퍼를 기록하고 디렉터리 엔트리를 갱신하기 때문이다. Close 응답의 성공을 확인하기 전에는 기록이 끝났다고 보면 안 된다.
- 에러 코드 체계는 Version 3 이상 FS가 지원한다. 표준의 에러 코드 정의는 값 10(Media is not present)에 "Version 2 FS에서는 아래 13번 오류의 코드였다"는 주석을 단다. 글자 그대로 읽으면 Version 2 FS가 보내는 10은 지금의 13(Volume is possibly not initialized)에 해당한다. 이것은 주석을 글자 그대로 읽은 해석이다.

정리하면 Flags와 Attributes, 모드 바이트는 비트마다 뜻이 정해져 있고, 명령마다 돌아올 수 있는 에러 코드가 정해져 있다. 에러 처리는 이 표를 기준으로 분기하면 된다.

::: details 원문을 가진 독자를 위한 메모
- 정의 위치: Flags B.14, Attributes B.15, Set Attributes Command B.16, Position Mode B.17, Offset B.18, File Handling Mode B.27, Seek File C.3.4, 에러 코드 정의 B.9.
- 명령별 에러 코드 표는 Annex C의 각 응답 정의(C.1.7, C.2.2~C.5.2)를 모은 것이다. Access Denied 네 경우는 C.4.2와 C.4.3, Close File의 8·9 설명은 C.3.7, error 12 규정은 C.1.1에 있다.
- B.9의 값 10 주석 원문: "formerly the code for error 13, below, in Version 2 FSs (see B.5)".
:::

<small>근거: ISO 11783-13 B.9, B.14~B.18, B.27, C.1.1, C.3.4, C.3.7, C.4.2, C.4.3</small>

## 5. 바이트로 따라가는 디렉터리 읽기

이 절에서는 클라이언트가 FS에 연결해 디렉터리 목록 하나를 읽고 닫기까지 주고받는 메시지 12개를 바이트 단위로 따라간다. [51장](/study/isobus/51-file-server-basics)과 이 장에서 본 규칙이 실제 바이트에서 어떻게 보이는지 확인하는 절이다.

클라이언트 0x80(=128)이 FS 0x3A(=58)에 연결해 `\\VOL_B\LOGS\`의 목록을 읽는 과정이다(두 주소는 예시). 요청은 PGN 0xAA00(=43520), 응답은 0xAB00(=43776)으로 간다. 표의 "데이터"는 CAN 데이터 바이트를 16진수로 적은 것이고, 맨 앞이 Byte 1이다.

| # | 방향 | 데이터 | 뜻 |
|---|---|---|---|
| 1 | FS → 전역 | `00 00 00 FF FF FF FF FF` | File Server Status: busy 아님, 열린 파일 0 (2 s마다) |
| 2 | C → FS | `01 FF FF FF FF FF FF FF` | Get File Server Properties |
| 3 | FS → C | `01 03 08 01 FF FF FF FF` | Version 3, 동시 열기 최대 8, 다중 볼륨 지원 |
| 4 | C → FS | `00 03 FF FF FF FF FF FF` | Client Connection Maintenance, 클라이언트 Version 3 (이후 2 s마다) |
| 5 | C → FS | `20 0A 03 0D 00 5C 5C 56 4F 4C 5F 42 5C 4C 4F 47 53 5C` | Open File, TAN 0x0A, Flags 0x03(디렉터리), 경로 13자. 18바이트라 TP |
| 6 | FS → C | `20 0A 00 02 10 FF FF FF` | 성공, Handle 0x02, Attributes 0x10(디렉터리) |
| 7 | C → FS | `22 0B 02 0A 00 00 FF FF` | Read File, TAN 0x0B, Handle 0x02, 엔트리 10개, hidden 제외 |
| 8 | FS → C | `22 0B 00 02 00` + 엔트리 39바이트 | 성공, 실제로 읽은 엔트리 2개. 전체 44바이트라 TP |
| 9 | C → FS | `22 0C 02 0A 00 00 FF FF` | 다음 묶음 요청 |
| 10 | FS → C | `22 0C 2D …` | 45(File pointer at end of file), 목록 끝 |
| 11 | C → FS | `24 0D 02 FF FF FF FF FF` | Close File, Handle 0x02 |
| 12 | FS → C | `24 0D 00 FF FF FF FF FF` | 성공 |

표의 주요 줄을 하나씩 풀어 보자.

1. 1번 `00 00 00 FF …`: Byte 1 `00`은 FS가 보낸 0x00이라 File Server Status다. Byte 2 `00`은 busy 비트가 모두 0, Byte 3 `00`은 열린 파일 0개다. 나머지는 0xFF로 채운 자리다.
2. 3번 `01 03 08 01 …`: Get File Server Properties의 응답이다. Byte 2 `03`은 Version 3, Byte 3 `08`은 동시에 열 수 있는 파일 최대 8개, Byte 4 `01`은 bit 0이 1이라 다중 볼륨 지원이다.
3. 4번 `00 03 …`: 클라이언트가 보낸 0x00이라 Client Connection Maintenance다. Byte 2 `03`은 클라이언트가 따르는 Version 3이다. 이때부터 2 s마다 보낸다.
4. 5번: Open File, TAN 0x0A(=10), Flags 0x03(디렉터리 열기), 경로 길이 `0D 00` = 13이다. 이어지는 13바이트 `5C 5C 56 4F 4C 5F 42 5C 4C 4F 47 53 5C`가 `\\VOL_B\LOGS\`다. `5C`는 `\`, `56 4F 4C`는 `VOL`, `5F`는 `_`, `42`는 `B`, `4C 4F 47 53`은 `LOGS`다. 5 + 13 = 18바이트라 TP로 간다.
5. 6번: 성공, Handle 0x02, Attributes 0x10이다. 0x10은 bit 4만 1이라 "디렉터리를 가리키는 Handle"이다.
6. 7번: Read File, TAN 0x0B, Handle 0x02, Count `0A 00` = 10(엔트리 10개까지), Byte 6 `00`(hidden 파일 제외)이다. 마지막 두 바이트는 예약이라 0xFF다.
7. 8번: 성공, Count `02 00` = 2이고 엔트리 두 개(39바이트)가 이어진다. 5 + 39 = 44바이트라 TP로 간다.
8. 10번: 에러 코드 0x2D = 45(File pointer at end of file)다. 목록을 다 읽었다는 뜻이다.
9. 11~12번: Close File로 Handle 0x02를 닫고 성공 응답을 받는다. TAN은 요청마다 0x0A, 0x0B, 0x0C, 0x0D로 1씩 늘었다.

Handle이 디렉터리면 Count는 읽을 엔트리 수이고, Report Hidden Files(Byte 6)가 0이면 hidden 파일을 뺀다. 255(파라미터 없음)도 빼는 것으로 처리하므로, Byte 6을 0xFF로 채운 요청도 hidden 파일을 받지 않는다. 목록 끝에 이르면 요청보다 적게 돌아오고, 이미 끝에 있는 포인터로 더 읽으면 45가 온다. 10번 응답처럼 에러 코드가 0이 아니면 뒤의 바이트는 해석하지 않는다.

8번 응답의 엔트리 부분은 Directory Entry가 Count만큼 이어 붙은 것이다. 아래 그림의 맨 윗줄은 응답 전체, 가운데 줄은 엔트리 하나, 아랫줄은 File Date와 File Time 2바이트 안의 비트 배치다.

![Read Directory Response와 Directory Entry 바이트 배치: 응답 헤더 5바이트 뒤에 엔트리가 Count만큼 이어지고, 엔트리는 이름 길이·이름·Attributes·File Date·File Time·Size로 이뤄지며, File Date와 File Time은 16비트 비트 그룹으로 연·월·일과 시·분·초를 담는 구조](/images/study-isobus/21-fs-directory-entry-layout-light.png)
![Read Directory Response와 Directory Entry 바이트 배치: 응답 헤더 5바이트 뒤에 엔트리가 Count만큼 이어지고, 엔트리는 이름 길이·이름·Attributes·File Date·File Time·Size로 이뤄지며, File Date와 File Time은 16비트 비트 그룹으로 연·월·일과 시·분·초를 담는 구조](/images/study-isobus/21-fs-directory-entry-layout-dark.png)

엔트리 하나의 길이는 이름 길이 L에 10을 더한 값이다. 그림의 n은 L + 1이다(이름 길이 1바이트 + 이름 L바이트). 첫 엔트리를 풀어 보면 다음과 같다.

```
0C                                    Filename Length = 12
54 41 53 4B 30 34 31 33 2E 58 4D 4C   "TASK0413.XML"
01                                    Attributes: read-only
8D 5C                                 File Date 0x5C8D: 46 + 1980 = 2026년, 4월, 13일
05 74                                 File Time 0x7405: 14시 32분, 5 x 2 = 10초
00 48 00 00                           Size 0x00004800 = 18 432바이트
```

File Date와 File Time은 2바이트 안에 여러 값을 비트로 나눠 담는다. 첫 엔트리의 날짜 `8D 5C`를 단계별로 풀면 다음과 같다.

1. 낮은 바이트가 먼저 오므로 값은 0x5C8D다.
2. 2진수로 쓰면 `0101 1100 1000 1101`이다.
3. bit 15~9(앞 7비트) `0101110` = 46이다. 연도는 1980년을 0으로 세므로 1980 + 46 = 2026년이다.
4. bit 8~5(다음 4비트) `0100` = 4, 곧 4월이다.
5. bit 4~0(끝 5비트) `01101` = 13, 곧 13일이다.

시간 `05 74`도 같은 방법으로 푼다. 값은 0x7405 = `0111 0100 0000 0101`이고, bit 15~11 `01110` = 14시, bit 10~5 `100000` = 32분, bit 4~0 `00101` = 5다. 초 칸은 2초 단위라 5 × 2 = 10초다. 그래서 홀수 초는 담을 수 없다. Size `00 48 00 00`은 낮은 바이트부터 오는 4바이트 수라 0x00004800 = 18 432바이트다.

둘째 엔트리 `07 41 52 43 48 49 56 45 10 81 5C 00 40 00 00 00 00`은 이름 "ARCHIVE", Attributes 0x10(디렉터리), 2026-04-01 08:00:00, 크기 0이다. 이름 길이 7이므로 엔트리 길이는 7 + 10 = 17바이트이고, 첫 엔트리 22바이트(12 + 10)와 합치면 8번 응답의 엔트리 39바이트가 된다.

아래 코드는 이 과정을 그대로 옮긴 것이다. 요청을 만드는 함수(`build_open_directory`, `build_read`), 시험용 엔트리를 만드는 함수(`build_entry`), 응답을 엔트리 단위로 푸는 함수(`parse_read_directory_response`)로 나뉜다. `assert` 줄은 위 표와 풀이의 바이트가 코드 결과와 같은지 확인한다.

::: details Python으로 디렉터리 읽기 응답 파싱 (51장 Open File 예제에 이어서)
[51장](/study/isobus/51-file-server-basics)의 Open File 파서와 같은 방식으로, 디렉터리 열기 요청과 Read File 요청을 만들고 Read Directory Response를 엔트리 단위로 풀어낸다. 날짜·시간은 위 그림의 비트 배치를 그대로 옮겼다.

```python
import struct
from datetime import datetime

FS_FUNC_OPEN_FILE, FS_FUNC_READ_FILE, FS_FUNC_CLOSE_FILE = 0x20, 0x22, 0x24
FLAG_DIRECTORY = 0x03
ATTR_BITS = {7: "case-sensitive", 6: "not-removable", 5: "long-filenames",
             4: "directory", 3: "volume", 2: "hidden-supported", 1: "hidden", 0: "read-only"}


def encode_date(dt: datetime) -> int:
    return ((dt.year - 1980) << 9) | (dt.month << 5) | dt.day           # B.24


def encode_time(dt: datetime) -> int:
    return (dt.hour << 11) | (dt.minute << 5) | (dt.second // 2)        # B.25


def decode_date_time(date: int, time: int) -> str:
    y, mo, d = (date >> 9) + 1980, (date >> 5) & 0x0F, date & 0x1F
    h, mi, s = time >> 11, (time >> 5) & 0x3F, (time & 0x1F) * 2
    return f"{y:04d}-{mo:02d}-{d:02d} {h:02d}:{mi:02d}:{s:02d}"


def decode_attributes(a: int) -> list:
    return [name for bit, name in ATTR_BITS.items() if a & (1 << bit)]


def build_open_directory(tan: int, path: str) -> bytes:
    p = path.encode("latin-1")
    return bytes([FS_FUNC_OPEN_FILE, tan, FLAG_DIRECTORY]) + struct.pack("<H", len(p)) + p


def build_read(tan: int, handle: int, count: int, report_hidden: int = 0) -> bytes:
    # C.3.5.2: Byte 6 = Report Hidden Files, Bytes 7-8 reserved
    return bytes([FS_FUNC_READ_FILE, tan, handle]) + struct.pack("<H", count) + bytes([report_hidden, 0xFF, 0xFF])


def build_entry(name: str, attr: int, dt: datetime, size: int) -> bytes:
    n = name.encode("latin-1")
    return bytes([len(n)]) + n + struct.pack("<BHHI", attr, encode_date(dt), encode_time(dt), size)


def parse_read_directory_response(data: bytes) -> dict:
    """C.3.5.4: [0]=0x22 [1]=TAN [2]=Error [3,4]=Count [5..]=Directory Entries (B.21)."""
    func, tan, err = data[0], data[1], data[2]
    assert func == FS_FUNC_READ_FILE
    if err != 0:                       # B.9: ignore every parameter after the error code
        return {"tan": tan, "error": err, "entries": []}
    count = struct.unpack_from("<H", data, 3)[0]
    entries, pos = [], 5
    for _ in range(count):
        length = data[pos]
        name = data[pos + 1:pos + 1 + length].decode("latin-1")
        attr, date, time, size = struct.unpack_from("<BHHI", data, pos + 1 + length)
        entries.append({"name": name, "attributes": decode_attributes(attr),
                        "modified": decode_date_time(date, time), "size": size})
        pos += 1 + length + 9           # one entry = Filename Length + 10 bytes
    assert pos == len(data), "trailing bytes after the last entry"
    return {"tan": tan, "error": 0, "entries": entries}


if __name__ == "__main__":
    req = build_open_directory(0x0A, "\\\\VOL_B\\LOGS\\")
    assert req.hex(" ").upper() == "20 0A 03 0D 00 5C 5C 56 4F 4C 5F 42 5C 4C 4F 47 53 5C"
    assert len(req) == 18                                   # > 8 bytes -> TP

    assert build_read(0x0B, 0x02, 10).hex(" ").upper() == "22 0B 02 0A 00 00 FF FF"

    e1 = build_entry("TASK0413.XML", 0x01, datetime(2026, 4, 13, 14, 32, 10), 18432)
    e2 = build_entry("ARCHIVE", 0x10, datetime(2026, 4, 1, 8, 0, 0), 0)
    assert e1.hex(" ").upper() == ("0C 54 41 53 4B 30 34 31 33 2E 58 4D 4C "
                                   "01 8D 5C 05 74 00 48 00 00")
    assert e2.hex(" ").upper() == "07 41 52 43 48 49 56 45 10 81 5C 00 40 00 00 00 00"

    resp = bytes([FS_FUNC_READ_FILE, 0x0B, 0x00]) + struct.pack("<H", 2) + e1 + e2
    assert len(resp) == 44
    parsed = parse_read_directory_response(resp)
    assert parsed["entries"][0] == {"name": "TASK0413.XML", "attributes": ["read-only"],
                                    "modified": "2026-04-13 14:32:10", "size": 18432}
    assert parsed["entries"][1]["attributes"] == ["directory"]

    eof = parse_read_directory_response(bytes([0x22, 0x0C, 45, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]))
    assert eof["error"] == 45 and eof["entries"] == []

    assert decode_date_time(0x5C8D, 0x7405) == "2026-04-13 14:32:10"
    assert decode_attributes(0x70) == ["not-removable", "long-filenames", "directory"]
    for e in parsed["entries"]:
        print(e)
    print("all asserts passed")
```
:::

실행하면 두 엔트리를 풀어낸 결과와 확인 메시지가 출력된다.

```text
{'name': 'TASK0413.XML', 'attributes': ['read-only'], 'modified': '2026-04-13 14:32:10', 'size': 18432}
{'name': 'ARCHIVE', 'attributes': ['directory'], 'modified': '2026-04-01 08:00:00', 'size': 0}
all asserts passed
```

핵심은 `parse_read_directory_response`의 반복문이다. 엔트리마다 첫 바이트(이름 길이)를 읽어 이름을 잘라 내고, 그 뒤 9바이트(Attributes 1 + 날짜 2 + 시간 2 + 크기 4)를 한 번에 푼 다음, 이름 길이 + 10바이트만큼 앞으로 간다. 에러 코드가 0이 아니면 뒤를 읽지 않고 바로 돌아가는 줄은 "실패 응답의 뒤 바이트는 버린다"는 규칙을 옮긴 것이다.

정리하면 디렉터리 목록은 Flags 0x03으로 열고, Read File로 엔트리를 원하는 개수만큼 읽고, 45가 오면 Close File로 닫는다. 엔트리 하나는 이름 길이 + 10바이트다.

::: details 원문을 가진 독자를 위한 메모
- 정의 위치: Directory Entry B.21(그림의 n), Filename Length B.22, File Date B.24, File Time B.25, Size B.26, Report Hidden Files B.28, Read Directory Response C.3.5.4, 목록 끝과 45 규정 C.3.5.1, 255 처리 B.28.
- B.25는 초 칸의 범위를 "1 … 29"로 적는다. 이 절의 둘째 엔트리(08:00:00)처럼 0초를 담으려면 값 0이 필요하므로, 범위 표기가 "0 … 29"의 오기일 가능성이 있다(의심). 같은 비트 배치를 쓰는 FAT 시간 형식은 0부터 센다.
:::

<small>근거: ISO 11783-13 B.9, B.20~B.26, B.28, C.1.2~C.1.5, C.3.3, C.3.5, C.3.7</small>

## 6. 나머지 명령의 바이트 예 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절은 디렉터리 읽기에 쓰지 않은 나머지 명령의 바이트 예를 모은 참고 자료다. 나머지 명령도 같은 틀이라 대표 바이트만 모아 둔다. TAN은 앞 표에 이어 0x0E(=14)부터 붙였다.

| 명령 | 요청 예 | 응답 예와 메모 |
|---|---|---|
| Get Current Directory | `10 0E FF FF FF FF FF FF` | `10 0E 00` + Total Space(4) + Free Space(4) + 경로 길이(2) + 경로. 공간 단위는 512바이트이고 경로는 `\\VOL\DIR\SUBDIR` 형태다 |
| Change Current Directory | `11 0F` + 경로 길이(2) + 경로 | `11 0F 00 FF FF FF FF FF` |
| Seek File (끝에서 100바이트 앞, Handle 0x01) | `21 10 01 02 9C FF FF FF` | `21 10 00 FF` + 새 Position(4). Offset −100은 0xFFFFFF9C다 |
| Write File (Handle 0x01) | `23 11 01` + Count(2) + Data | `23 11 00` + 실제로 쓴 Count(2) + `FF FF FF` |
| Delete File (read-only 파일이 든 디렉터리) | `31 12 06` + 경로 길이(2) + `…\OLD\` | `31 12 00 FF FF FF FF FF` |
| Get File Date & Time | `34 13` + 경로 길이(2) + 경로 | `34 13 00 8D 5C 05 74 FF`, 곧 2026-04-13 14:32:10 |

표의 값 가운데 풀어 볼 만한 것을 짚는다.

- Get Current Directory 응답의 Total Space와 Free Space는 512바이트 단위다. 예를 들어 Free Space가 2 048이면 1 MiB가 남았다는 뜻이다.
- Seek File 요청 `21 10 01 02 9C FF FF FF`는 Byte 2 TAN 0x10, Byte 3 Handle 0x01, Byte 4 Position Mode 2(파일 끝 기준), Byte 5~8 Offset이다. Offset `9C FF FF FF`는 낮은 바이트부터 읽어 0xFFFFFF9C다. Offset은 2의 보수 signed 32비트다. 맨 앞 비트가 1이면 음수이고, 그 크기는 0x100000000에서 값을 뺀 만큼이다. 0x100000000 − 0xFFFFFF9C = 0x64 = 100이므로 Offset은 −100이다. 파일 끝에서 100바이트 앞으로 포인터를 옮기라는 요청이다.
- Delete File 요청의 `06`은 File Handling Mode 0x06(force와 recursive)이다. read-only 파일이 든 디렉터리를 통째로 지울 때 쓴다(4절 참고). 경로 끝의 `\`는 디렉터리를 가리킨다는 표시다.
- Get File Date & Time 응답의 `8D 5C 05 74`는 5절의 첫 엔트리와 같은 날짜·시간이다.

Read·Write 한 번에 오가는 데이터는 TP로 최대 1 780바이트, ETP로 최대 65 530바이트다. 표준에 계산식이 적혀 있지는 않지만, TP 최대 1 785바이트에서 함수·TAN·Handle(또는 에러 코드)·Count 2바이트의 앞부분 5바이트를 뺀 값으로 보인다. 65 530에 5를 더하면 16비트 최대값 65 535가 된다. 디렉터리를 가리키는 Handle에는 Write File을 쓸 수 없다.

정리하면 모든 명령은 "Byte 1 함수, Byte 2 TAN, 그 뒤 파라미터"의 같은 틀이고, 한 번에 읽고 쓰는 데이터는 TP로 1 780바이트, ETP로 65 530바이트까지다.

::: details 원문을 가진 독자를 위한 메모
- 명령별 정의 위치: Get Current Directory C.2.2, Change Current Directory C.2.3, Seek File C.3.4, Write File C.3.6, Delete File C.4.3, Get File Date & Time C.4.6. 나머지 명령 전체는 C.2~C.5다.
- 1 780바이트와 65 530바이트 상한은 C.3.5.1과 C.3.6.1, 디렉터리 Handle에 Write File을 쓸 수 없다는 규정은 C.3.6.1에 있다.
:::

<small>근거: ISO 11783-13 B.11, B.17, B.18, B.27, C.2~C.5</small>

## 7. 정리: FS 클라이언트 체크리스트

이 절은 [51장](/study/isobus/51-file-server-basics)과 이 장에서 본 규칙을, FS 클라이언트를 만들 때 확인할 항목으로 모은다. 항목마다 자세한 설명이 있는 곳을 함께 적었다.

::: tip FS 클라이언트 체크리스트
- Byte 1은 그룹(상위 4비트)과 함수(하위 4비트)다. Connection Management(0x00~0x02)만 TAN이 없고, 나머지는 Byte 2가 TAN이다. (51장 4절, 6절)
- 요청은 한 번에 하나다. busy 표시 없이 600 ms가 지나면 같은 TAN으로 재요청한다. (51장 5절)
- 상호작용하는 동안 Client Connection Maintenance를 2 s마다 보낸다. 6 s 끊기면 FS가 그 클라이언트의 Handle을 모두 닫는다. 반대로 File Server Status가 6 s 끊기면 FS가 사라진 것으로 본다. (51장 5절)
- 에러 코드가 0이 아니면 뒤 파라미터는 버린다. Close File의 성공까지 확인해야 기록이 끝난 것이다. (이 장 4절)
- 이동식 볼륨에 Preparing for removal이 오면 파일을 닫는다. 볼륨을 붙잡아야 한다면 Maintain을 2 s보다 짧은 주기로 보낸다. 표준이 주기를 정하지는 않았고, FS가 마지막 Maintain 뒤 2 s 동안만 볼륨을 유지한다는 규칙에서 끌어낸 값이다. (이 장 2절)
:::

FS는 여기까지다. [53장](/study/isobus/53-sequence-control-basics)부터는 밭 끝에서 돌 때(헤드랜드) 운전자가 하던 작업기 조작을 기록해 두었다가 다음 회전에서 그대로 재생하는 Sequence Control(SC)을 본다.

::: tip 핵심 정리
- 볼륨은 저장 매체 하나에 붙은 이름이고 `\\`가 볼륨 목록이다. 이동식 볼륨은 Volume Status로 Present → Preparing for removal → Removed 순서를 전역에 알린다.
- 제거 준비가 알려지면 모든 클라이언트는 그 볼륨의 파일을 닫는다. 더 써야 하는 클라이언트는 Maintain을 보내 시간을 번다.
- 경로는 current directory 기준이고, `\`로 시작하면 current volume 루트, `..`은 상위, `~`는 제조사 전용 디렉터리, `\\`는 볼륨 목록이다.
- Flags·Attributes는 비트마다 뜻이 있고, 명령마다 돌아올 수 있는 에러 코드가 정해져 있다. 에러 코드가 0이 아니면 뒤 바이트는 버린다.
- 디렉터리는 Flags 0x03으로 열고 Read File로 엔트리를 읽는다. 엔트리 하나는 이름 길이 + 10바이트이고, 목록 끝에서는 45가 온다.
:::

::: details 확인 문제
1. (개념) 이동식 볼륨을 빼려 할 때 Volume Status가 거치는 상태를 순서대로 쓰고, 상태가 바뀐 응답을 요청자에게만 보내지 않고 전역 주소로 보내는 이유를 설명하라.
2. (개념) current directory가 `\\VOL_B\LOGS\`이고 클라이언트의 제조사 코드가 123이다. `..\CFG\A.TXT`와 `~\A.TXT`는 각각 FS의 어느 위치를 가리키는가?
3. (디코딩) Open File 응답의 Attributes가 0x70이다. 이 바이트에서 알 수 있는 것을 모두 쓰라.
4. (디코딩) 디렉터리 엔트리 `07 41 52 43 48 49 56 45 10 81 5C 00 40 00 00 00 00`의 이름, 속성, 날짜·시간, 크기를 구하라.
5. (판단) 클라이언트가 Read File `22 0C 02 0A 00 00 FF FF`를 보냈더니 `22 0C 2D …`가 왔다. 이 응답은 무슨 뜻이고, 클라이언트는 다음에 무엇을 해야 하는가?

**답 가이드**
1. Present → Preparing for removal → Removed 순서다. 그 볼륨에 파일을 열어 둔 클라이언트가 요청자 말고도 있을 수 있고, 모두 파일을 닫아야 하므로 상태 변화는 클라이언트 요청 때문에 바뀐 경우에도 전역(DA 0xFF)으로 알린다. 전역 응답은 상태 변화 통지라 에러 코드가 Success이고, 실패 응답만 요청자에게 보낸다.
2. `..\CFG\A.TXT`는 LOGS의 상위인 VOL_B로 올라가 `\\VOL_B\CFG\A.TXT`를 가리킨다. `~\A.TXT`는 current volume(VOL_B)의 전용 디렉터리라 `\\VOL_B\MCMC0123\A.TXT`다.
3. 0x70은 0111 0000이다. bit 6이 1이라 이동식이 아닌 고정 볼륨이고, bit 5가 1이라 볼륨이 긴 파일 이름을 지원하며, bit 4가 1이라 Handle이 디렉터리를 가리킨다. bit 1과 bit 0이 0이므로 hidden과 read-only 속성은 꺼져 있다.
4. 첫 바이트 `07`이 이름 길이 7이고, `41 52 43 48 49 56 45`가 "ARCHIVE"다. Attributes `10`은 디렉터리다. File Date `81 5C`는 0x5C81이라 연 46(2026년), 월 4, 일 1이다. File Time `00 40`은 0x4000이라 8시 0분 0초다. Size `00 00 00 00`은 0이다. 곧 2026-04-01 08:00:00에 수정된 크기 0의 디렉터리 ARCHIVE다.
5. 에러 코드 0x2D = 45(File pointer at end of file)로, 디렉터리 목록을 끝까지 읽었다는 뜻이다. 에러 코드가 0이 아니므로 뒤 바이트는 해석하지 않는다. 클라이언트는 Close File(`24 0D 02 FF FF FF FF FF`)로 디렉터리 Handle 0x02를 닫는다.
:::

## 다음 챕터

- 다음: [53장 Sequence Control(SC) 기초](/study/isobus/53-sequence-control-basics)
