---
title: "다중 TC, Data Logger, TC 기능성"
description: "TC가 여러 대일 때 번호를 매기고 고르는 법, 기록만 하는 Data Logger와 TC의 차이, 기능성과 Version 메시지로 자기 능력을 알리고 서로 맞추는 법을 익힌다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, TaskController, TC, DataLogger, TCFunctionality, AEF]
prev: /study/isobus/43-tc-connection
next: /study/isobus/45-tc-process-data-basics
---

# 다중 TC, Data Logger, TC 기능성

::: info 학습 목표
- TC 번호가 NAME의 function instance에서 어떻게 나오는지 계산할 수 있다.
- 클라이언트가 붙을 TC를 고르고 다른 TC로 옮겨 가는 순서를 말할 수 있다.
- Data Logger가 TC와 같은 점과 다른 점을 구분하고, 두 서버에 동시에 붙는 클라이언트가 지킬 규칙을 설명할 수 있다.
- TC 기능성(TC-BAS, TC-GEO, TC-SC, LOG)을 "내 기계가 무엇을 지원하는지 알리는 자기소개"로 읽고, 상대 능력에 맞춰 DDOP를 줄이는 방법을 설명할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [41장 TC 기초](/study/isobus/41-tc-basics)(6절 기능성), [43장 TC 연결 관리와 메시지 바이트](/study/isobus/43-tc-connection)(Version 메시지), [12장 주소와 NAME](/study/isobus/12-j1939-address-name)
- 이 장에서 처음 나오는 말
  - TC 번호(TC number): 오퍼레이터에게 보이는 TC의 번호. 1~32
  - function instance: 같은 기능을 하는 장치가 여럿일 때 NAME 안에 넣는 0부터의 번호
  - primary TC: function instance가 0인 기본 TC
  - DL(Data Logger): 작업기를 제어하지 않고 기록만 하는 장치 기능
  - 기능성(functionality): 제품이 할 수 있는 일을 묶어 부르는 이름. TC-BAS, TC-GEO, TC-SC, LOG가 있다
  - generation: 기능성 정의의 세대 번호. 지금은 모두 1이다
:::

한 현장에 감독이 여럿이면 작업자는 누구의 지시를 따를지 먼저 정해야 한다. 큰 농장의 트랙터에는 TC가 두 대 달려 있기도 하고, 기록만 하는 텔레매틱스 장치가 함께 있기도 하다. 이 장은 TC가 여럿일 때 번호를 매기고 고르는 법, 기록만 하는 Data Logger, 그리고 장치끼리 "나는 이런 일을 할 수 있다"고 자기소개하는 기능성과 Version 메시지를 본다.

## 1. TC가 여러 대일 때: TC 번호

TC가 둘 이상이면 오퍼레이터와 클라이언트가 "몇 번 TC"라고 부를 수 있어야 한다. 이 절은 그 번호가 어디서 나오는지 본다.

### TC 번호는 NAME의 function instance에서 나온다

TC 번호(TC number)는 TC의 function instance에서 유도한 식별 번호다. function instance는 NAME의 5비트 필드(NAME Byte 5 bits 8~4)라 0~31이고, 오퍼레이터에게는 <strong>TC 번호 = function instance + 1</strong>, 즉 1~32로 보인다. 0부터 세는 번호에 익숙하지 않은 오퍼레이터를 위한 오프셋이고, 모든 제조사의 TC가 같은 번호 체계를 보여 주게 하려는 것이다.

NAME은 장치마다 고유한 8바이트 이름이고, 주소 클레임 때 Address Claimed 메시지에 실려 버스에 알려진다([12장](/study/isobus/12-j1939-address-name)). 그 다섯 번째 바이트(Byte 5)의 위쪽 5비트가 function instance, 아래쪽 3비트가 ECU instance다.

예를 들어 어떤 TC가 보낸 Address Claimed(PGN 60928, `0xEE00`) 데이터의 Byte 5가 `0x08`이면 bits 8~4 = `00001`이다. `0x08 >> 3` = 1이 function instance이고(나머지 bits 3~1은 ECU instance 0), TC 번호는 2다.

단계별로 풀면 다음과 같다.

1. `0x08`을 2진수로 쓰면 `0000 1000`이다. 왼쪽 끝이 bit 8, 오른쪽 끝이 bit 1이다.
2. 위쪽 5비트(bits 8~4)는 `00001`, 아래쪽 3비트(bits 3~1)는 `000`이다.
3. 아래 3비트를 밀어내는 `>> 3` 연산을 하면 위쪽 5비트만 남아 1이 된다. 이것이 function instance다.
4. TC 번호는 1 + 1 = 2다.

| 규칙 |
|---|
| 네트워크에 TC가 있으면 function instance 0인 TC가 <strong>항상</strong> 있어야 한다 |
| TC는 공장 출하 때 function instance 0이고, 오퍼레이터가 설정한 값을 유지한다 |
| function instance를 바꾸는 proprietary 수단은 TC가 제공하고, TC끼리 중복이 생기지 않게 해야 한다 |
| 새로 설정한 값은 TC가 네트워크에 다시 접속한 뒤에야 쓴다 |
| function instance 0인 TC가 primary TC다. 0이 아닌 TC도 같은 연결 절차를 따른다 |
| 여러 CF를 품은 ECU 안의 TC라면 오퍼레이터가 TC CF를 켜고 끌 수 있게 하는 것이 권고다 |

- proprietary 수단은 제조사가 정한 자체 방법(설정 화면 등)이다. 번호를 바꾸는 방법까지 표준이 정하지는 않는다.
- 같은 연결 절차는 [41장 8절](/study/isobus/41-tc-basics)과 [43장](/study/isobus/43-tc-connection)에서 본 초기화·유지 절차를 말한다.
- 한 ECU 안에 TC와 다른 기능(예: VT)이 함께 들어 있으면, TC 기능만 끄고 켤 수 있어야 한 트랙터에 TC가 둘 생기는 상황을 오퍼레이터가 정리할 수 있다.

<small>근거: ISO 11783-10 3.18, 6.7, B.5.4. ISO 11783-5 Table 1</small>

## 2. 클라이언트는 어느 TC에 붙나

클라이언트는 한 번에 TC 하나에만 붙는다. 그러니 TC가 여럿이면 어느 TC에 붙을지, 다른 TC로 옮기려면 어떻게 할지가 정해져 있어야 한다.

- 기본은 function instance 0(TC 번호 1)인 TC다.
- "Move to another Task Controller" 기능(예: "Next Task Controller" 소프트키)을 가진 클라이언트는 function instance가 0보다 큰 TC에도 붙을 수 있다. 이 기능은 사용 가능한 TC들을 <strong>차례로 하나씩</strong> 옮겨 가게 해야 한다.
- 이 기능은 네트워크에서 TC를 2대 이상 감지했을 때만 켜진다.

소프트키는 화면 옆에 붙은 버튼으로, 화면에 따라 기능이 바뀐다([30장 VT 화면과 기술 데이터](/study/isobus/30-vt-display-technical-data)). 리모컨의 채널 버튼처럼 누를 때마다 다음 TC로 넘어간다고 생각하면 된다.

![TC 번호와 TC 옮기기: TC 번호 1(primary, function instance 0)에 연결된 클라이언트가 Next Task Controller로 TC 번호 2(function instance 1)로 옮긴다. 옮기는 순서는 1) 안전 상태로 전환, 2) 현재 TC에 Connection Deactivate를 보내고 최대 2 s 응답을 기다림, 3) 현재 TC로 보내던 Client Task 중단, 4) 새 TC와 초기화하고 preferred TC로 저장이다](/images/study-isobus/44-tc-switch-light.png)
![TC 번호와 TC 옮기기: TC 번호 1(primary, function instance 0)에 연결된 클라이언트가 Next Task Controller로 TC 번호 2(function instance 1)로 옮긴다. 옮기는 순서는 1) 안전 상태로 전환, 2) 현재 TC에 Connection Deactivate를 보내고 최대 2 s 응답을 기다림, 3) 현재 TC로 보내던 Client Task 중단, 4) 새 TC와 초기화하고 preferred TC로 저장이다](/images/study-isobus/44-tc-switch-dark.png)

옮겨 갈 때의 순서는 다음과 같다. 오른쪽 열의 이유는 표준이 적지 않은 해설이다(추론).

| 순서 | 동작 | 이유 |
|---|---|---|
| 1 | 안전 상태로 전환한다. 안전 상태가 아니면 이 기능 자체를 막는다 | 연결을 바꾸는 동안 섹션·rate 명령이 주인 없이 남지 않게 |
| 2 | 현재 TC에 Connection Deactivate(Byte 2 = 0)를 보내고 응답을 기다린다 | 현재 TC가 비정상 종료로 오인하지 않게. 응답은 최대 2 s |
| 3 | 현재 TC로 보내던 Client Task를 멈춘다 | 클라이언트당 TC 연결은 하나 |
| 4 | 다른 TC와 초기화를 시작한다 | |

- 안전 상태는 섹션을 끄고 살포를 멈춘 것처럼, 명령이 끊겨도 위험하지 않은 상태다.
- Connection Deactivate는 DDOP 활성화 명령의 Byte 2를 0으로 보낸 "의도적으로 연결을 끊는다"는 신호다. 바이트는 [43장 10절](/study/isobus/43-tc-connection)에서 봤다.
- 4단계의 초기화는 [41장 8절](/study/isobus/41-tc-basics)의 9단계를 새 TC와 처음부터 밟는 것이다.

옮긴 뒤와 다음 기동 때의 규칙은 다음과 같다.

- 새 TC는 다음 전원 사이클의 <strong>preferred TC</strong>로 저장한다. preferred TC는 "다음에 켤 때 먼저 찾을 TC"다.
- 기동 후 일정 시간 안에 preferred TC가 나타나지 않으면 다른 TC에 붙어도 된다. 기다릴 최대 시간은 오퍼레이터가 설정하게 하거나, preferred TC가 Version 메시지 Byte 3에 보고한 boot time에서 얻는다. 기동 직후에는 그 TC와 아직 버전을 교환하지 않았으므로, 지난 연결 때 받아 둔 boot time을 저장해 쓰는 셈이다(추론).
- 클라이언트는 동시에 TC 하나, DL 하나에만 연결할 수 있다. 여러 TC나 여러 DL에 동시에 붙는 것은 이 판에서 허용되지 않는다.

::: info 구현 관점: TC Status를 보낸 쪽이 누구인가
TC Status는 TC도 DL도 보낸다(상태 바이트 이름부터 "Actual TC / DL status"다). 그래서 클라이언트는 TC Status의 SA를 주소 클레임으로 모은 NAME 표에서 찾아 ① function이 TC인지 DL인지, ② function instance가 몇인지를 확인한 뒤에야 "내가 선택한 TC"인지 판단할 수 있다(추론). TC와 DL을 구분하는 function 값 자체는 Part 1이 isobus.net 데이터베이스로 넘긴다.
:::

위 상자의 Part 1(ISO 11783-1)은 ISOBUS 전체 개요와 공통 정의를 정하는 표준 문서이고, isobus.net은 function 값 같은 코드 목록을 공개하는 웹 데이터베이스다. SA(주소)만으로는 TC인지 DL인지 알 수 없으므로, 주소 클레임 때 받은 NAME을 함께 봐야 한다는 뜻이다.

<small>근거: ISO 11783-10 6.7, 6.7.1, 7.1, B.5.3, B.6.10, B.6.11, B.8.1. ISO 11783-1</small>

## 3. Data Logger: TC와 같은 점, 다른 점

작업을 제어하지 않고 기록만 하고 싶은 장치도 있다. 예를 들어 트랙터의 작업 기록을 인터넷으로 농장 사무실에 보내는 텔레매틱스 장치다. 이런 장치를 위해 버전 4에서 Data Logger가 생겼다.

DL(data logger)은 TC 클라이언트를 제어하지 않고 태스크와 무관한 로깅을 하려고 네트워크에 두는 CF다. 텔레매틱스 로거가 대표적이지만 텔레매틱스 환경에 한정되지 않는다. DL은 TC의 process data 프로토콜을 그대로 쓰며, device descriptor와 process data로 데이터를 모으는 데 더해 버스에 방송되거나 요청할 수 있는 다른 PG도 로깅할 수 있다. TC 기능의 부분집합이고 연결 메커니즘이 TC와 같으며, 버전 4에서 도입됐다.

41장의 비유로 말하면 DL은 지시는 하지 않고 일지만 쓰는 기록원이다. 같은 현장에 감독(TC)과 기록원(DL)이 함께 있을 수 있다.

| 항목 | TC | DL |
|---|---|---|
| 네트워크 식별 | TC function | 별도의 DL function |
| 도입 | 버전 1부터 | 버전 4 |
| 연결 절차 | 클라이언트 초기화·연결 유지 절차([41장 8절](/study/isobus/41-tc-basics)) | TC의 클라이언트 초기화 절차와 같다 |
| 주기 메시지 | TC Status 송신, Client Task 수신 | 같다 |
| function instance 0 | primary TC, 네트워크에 반드시 있다 | 다른 instance와 역할이 같다 |
| 여럿일 때 | TC 번호로 구분 | 유일한 function instance로 구분(설정은 proprietary) |
| 섹션 제어 | 한다 | <strong>금지</strong> |
| 위치 기반 제어 | 한다 | <strong>금지</strong> |
| peer control 할당 설정 | 한다 | <strong>금지</strong>. 단 peer control CF가 로깅용 값을 주려고 DL에 붙는 것은 가능 |
| 값 설정(set) 명령 | settable DDI에 보낸다 | task total DDI 외에는 보내지 않는다 |
| process data 요청·measurement·default logging·PG 로깅 요청 | 한다 | 한다 |
| task total 누적 제어 | TC Status bit 1 | 자기 TC Status bit 1로 DL용 세트를 제어 |
| TC 통신 규칙(대역폭 등) | 적용 | DL과 DL 클라이언트 사이에도 적용 |
| Version 메시지 boot time | 의미 있음 | 의미 있음 |

표를 한마디로 줄이면 "DL은 듣고 묻고 기록할 수는 있지만, 작업기를 움직이는 명령은 보내지 않는다"이다. 값 설정 명령도 task total(작업 합계)을 0으로 되돌리는 것 같은 기록용 값에만 쓴다.

- settable DDI는 TC가 값을 정해 줄 수 있는 항목(예: 목표 살포량)이다.
- default logging은 클라이언트가 미리 정해 둔 기본 기록 조건이다([47장](/study/isobus/47-tc-totals-logging-peer)).
- 대역폭 규칙은 메시지를 너무 자주 보내 버스를 독차지하지 않게 하는 규칙이다([45장](/study/isobus/45-tc-process-data-basics)).

클라이언트 쪽에서 달라지는 것은 다음과 같다.

- DDOP를 TC용과 DL용으로 따로 줄 수 있다. 같은 클라이언트라도 두 DDOP 내용이 다를 수 있고, 목적별로 최적화하는 것은 클라이언트 설계자 책임이다.
- TC와 DL에 동시에 붙으면 <strong>measurement 명령 세트를 서버별로 따로</strong> 유지해 병렬로 돌린다.
- task total도 <strong>서버별로 따로</strong> 누적한다. 각 세트는 해당 CF가 따로 set·reset·trigger할 수 있고 서로 간섭하면 안 된다. DL이 total을 자주 리셋하지 않더라도, 누적 시작점을 정하고 최대값에서 roll-over되는 것을 피하는 데 이 메커니즘을 쓸 수 있다.
- DL 클라이언트가 연결할 수 있는 DL은 최대 하나다(버전 4까지).

roll-over는 카운터가 최대값을 넘어 0으로 돌아가는 것이다. 자동차 주행거리계가 999999에서 000000으로 넘어가는 것과 같다.

네트워크 구성은 세 가지다.

| 구성 | 내용 | 도입 |
|---|---|---|
| a) TC + TC 클라이언트 | 모든 TC 클라이언트가 TC에 연결 | 버전 1 |
| b) DL + DL 클라이언트 | 모든 DL 클라이언트가 DL에 연결. 연결 방식은 a)와 같다 | 버전 4 |
| c) TC + DL + TC/DL 클라이언트 | 두 기능을 다 가진 CF가 TC와 DL 중 하나 또는 둘 다에 연결. 둘에 동시에 붙을 수 있다 | 버전 4 |

![TC·DL 네트워크 구성 세 가지: a) TC 하나에 클라이언트들이 연결(버전 1부터), b) DL 하나에 클라이언트들이 연결(버전 4), c) TC와 DL이 함께 있고 TC/DL 클라이언트가 둘 다에 연결하며 클라이언트 안에 TC용 total과 DL용 total을 따로 둔다(버전 4)](/images/study-isobus/44-tc-dl-configs-light.png)
![TC·DL 네트워크 구성 세 가지: a) TC 하나에 클라이언트들이 연결(버전 1부터), b) DL 하나에 클라이언트들이 연결(버전 4), c) TC와 DL이 함께 있고 TC/DL 클라이언트가 둘 다에 연결하며 클라이언트 안에 TC용 total과 DL용 total을 따로 둔다(버전 4)](/images/study-isobus/44-tc-dl-configs-dark.png)

::: warning 두 서버에 동시에 붙는 클라이언트의 함정
TC Status의 Task totals active가 0 → 1로 바뀌면 그 TC Status를 보낸 CF의 total 세트만 리셋해야 한다. TC가 태스크를 시작했다고 DL용 total까지 0으로 만들면 위의 "서로 간섭하면 안 된다"를 어긴다. Client Task·measurement·total 상태를 서버 SA별로 따로 들고 있어야 한다(추론).
:::

그림 c)의 클라이언트 안에 total 상자가 둘인 것이 이 규칙이다. 장부를 감독용과 기록원용으로 따로 두고, 각자 자기 장부만 0으로 되돌린다.

<small>근거: ISO 11783-10 5.6, 7.1, 7.2, 7.3, B.5.3, B.8. ISO 11783-1:2017 3.14</small>

## 4. TC 기능성: 내 기계의 자기소개

처음 만난 사람끼리 "저는 이런 일을 할 줄 압니다"라고 자기소개를 하듯, TC와 클라이언트도 연결할 때 서로 무엇을 할 수 있는지 알린다. 자기소개에 쓰는 말이 기능성 이름이고, 버스에서 주고받는 자기소개서가 [43장 8절](/study/isobus/43-tc-connection)의 Version 메시지다.

[41장 7절](/study/isobus/41-tc-basics)은 TC-BAS·TC-GEO의 최소 요건을 정리했다. 여기서는 네 기능성 전체를 다시 묶는다. DDOP를 기능성에 맞게 짜는 구조 규칙은 [50장 DDOP 전송과 설계 점검](/study/isobus/50-ddop-commands-design)에서 다룬다.

TC functionality는 제품이 시스템 안에서 올바르게 동작하려면 구현해야 할 기능 묶음이다. 앞으로의 발전과 제품의 기술적 제약을 함께 담으려고 <strong>generation 번호</strong>로 버전을 매기고, 일부에는 선택 기능(option)을 둔다. 이 정의와 예시는 AEF와 협력해 만들었고 적합성 시험의 바탕이 된다. 현재 정의된 기능성은 모두 generation 1이다. AEF 기능 단위 전체는 [AEF 기능 카테고리](/study/isobus/appendix-aef-functionalities)에 있다.

아래 표의 "게시 버전"은 자기소개서에 적어 넣는 TC 버전 번호다. Version 메시지 Byte 2와 파일 세트의 버전 칸에 이 숫자를 쓴다. "Version Byte 4"는 Version 메시지 네 번째 바이트에서 그 기능성을 표시하는 비트다.

| 기능성 | 한 줄 정의 | 위치 소스 | 게시 버전 | Version Byte 4 |
|---|---|---|---|---|
| TC-BAS (basic) | 태스크 기반 total 읽기·쓰기. 위치·시간 데이터가 필요 없다 | 불필요 | 3(파일 세트·Version) | bit 1 |
| TC-GEO (geo-based) | 위치에 따른 site-specific 값 처리. 제어 요소가 없는 클라이언트의 as-applied 매핑(콤바인 수확량, 플랜터 파종 밀도 등)도 포함한다 | GNSS 등 필요 | 3(파일 세트·Version) | bit 2(위치 기반 로깅) / bit 3(위치 기반 제어) |
| TC-SC (section control) | 위치에 따른 on/off 제어. 이미 작업한 영역이나 헤드랜드·필드 밖 같은 영역과 만나는지 판단해 중복과 누락을 줄인다 | 필요 | 3(Version만) | bit 5 |
| LOG (data logger) | lifetime total 읽기. 위치·시간 데이터가 필요 없다 | 불필요 | 4(파일 세트·Version) | 없음 |

- site-specific은 "위치마다 다르게", as-applied 매핑은 "실제로 한 일을 지도에 그리기"다. 콤바인이 위치별 수확량을 기록하는 것이 TC-GEO의 대표 예다.
- 헤드랜드(headland)는 밭 끝에서 트랙터가 방향을 돌리는 띠 모양 구역이다. 여기서는 겹쳐 뿌리기 쉬워 섹션 제어가 특히 쓸모 있다.
- lifetime total은 장치가 만들어진 뒤로 쌓인 평생 합계다. 태스크 하나의 합계인 task total과 다르다.

| 기능성 | 서버 요건 | 클라이언트 요건 |
|---|---|---|
| TC-BAS | Part 11의 total DDI 전부 | total 부분집합 가능. <strong>DDI 119(total time) 필수</strong>. rate DDI가 있으면 대응 total도 |
| TC-GEO | Part 11의 DDI 전부 + TC-BAS + Grid type 1·2(350행 × 350열 이상) + 위치 기반 제어 채널 1개 이상 | 자기가 제어·로깅하는 프로세스 관련 DDI 부분집합. rate 제어가 있으면 setpoint·actual rate 쌍 최소 1개 권고(작업 깊이 같은 다른 setpoint도 제어 가능). TC-BAS도 지원 |
| TC-SC | 붐 1개·섹션 3개 이상 지원, 필수 DDI(6절 표) | 붐 1개·섹션 1개부터 적합, 필수 DDI(6절 표) |
| LOG | Part 11의 total DDI 전부 | lifetime total 부분집합 가능. <strong>DDI 274(lifetime total time) 필수</strong>. rate DDI가 있으면 대응 lifetime total도 |

Part 11(ISO 11783-11)은 DDI 목록을 정하는 표준 문서다. 표의 원칙은 41장에서 본 것과 같다. 서버는 넓게 받아 주고, 클라이언트는 자기가 다루는 만큼만 말한다. 장치 클래스별 권장 DDI 표는 [Part 10 부록](/study/isobus/appendix-iso-part10)에 있다. peer control은 Version Byte 4 bit 4로 알리지만 네 기능성에는 들지 않는다. LOG에는 Version 옵션 비트가 없다. DL은 NAME의 function으로 식별된다.

자기소개서를 실제로 읽어 보자. [43장 8절](/study/isobus/43-tc-connection)의 TC가 보낸 Version `10 04 0A 1F 00 02 18 04`는 "버전 4이고, Byte 4가 `0x1F`라 TC-BAS·TC-GEO(로깅과 제어)·peer control·TC-SC를 모두 하며, 섹션 제어 붐 2개·섹션 24개·채널 4개까지 다룬다"는 자기소개다. 반대로 Byte 4가 `0x11`인 장치는 "TC-BAS와 TC-SC만 한다"고 말하는 것이다.

<small>근거: ISO 11783-10 Annex F(F.1, F.2.1~F.2.4), B.5.3, 7.1</small>

## 5. 옵션과 수치 맞추기

자기소개를 주고받았는데 상대가 나보다 작은 일만 할 수 있다면 어떻게 할까? 이 절은 클라이언트가 TC의 능력에 맞춰 자기를 줄이는 방법을 본다.

- TC-GEO의 polygon 처방 처리는 선택이다. 지원하면 Part 12의 Control function functionalities 메시지에 명시한다. 파일 세트 쪽 표시는 [43장 8절](/study/isobus/43-tc-connection)의 TaskControllerCapabilities 값 32다.
- 위치 기반 제어 채널 수(TC-GEO)와 붐·섹션 수(TC-SC)는 Control function functionalities 메시지와 Version 메시지 양쪽에 명시한다.
- 클라이언트는 TC가 Version 메시지로 보고한 수치에 맞춰 <strong>DDOP를 줄인다</strong>.
  - TC-GEO: DDOP에 보고하는 제어 채널 수를 TC가 보고한 채널 수 이하로 제한한다.
  - TC-SC: TC가 제어할 수 있는 붐·섹션 수가 클라이언트의 물리 능력보다 적으면, 물리적으로 제어 가능한 요소들을 <strong>묶어서</strong> 더 적은 수로 통신한다.
  - 그래도 클라이언트 자신의 Version 메시지에는 줄이기 전 능력을 보고한다.

Control function functionalities 메시지는 장치가 지원하는 기능성 목록을 진단 메시지로 알리는 것이다([28장](/study/isobus/28-diagnostics-dm-fmi)). polygon 처방은 41장에서 본 자유로운 모양의 구역으로 된 처방 맵이다.

예를 들어 물리 섹션 12개짜리 붐 1개 스프레이어가 Version Byte 6~7 = 1·6을 보고한 TC에 붙으면, DDOP에는 이웃한 물리 섹션을 2개씩 묶은 섹션 6개를 정의한다. 클라이언트의 Version 메시지는 여전히 Byte 6~7 = 1·12다. 묶은 섹션의 폭·오프셋을 어떻게 정의하는지는 [49장 DDOP 바이트 구성](/study/isobus/49-ddop-bytes)과 [50장 DDOP 전송과 설계 점검](/study/isobus/50-ddop-commands-design)의 범위다.

![능력 맞추기: TC는 Version 메시지로 섹션 제어 붐 1·섹션 6을, 클라이언트는 붐 1·섹션 12를 줄이기 전 능력 그대로 알린다. 클라이언트는 TC가 다룰 수 있는 6개에 맞춰 물리 섹션 1~12를 이웃한 두 개씩 묶어 DDOP 섹션 1~6으로 보고한다](/images/study-isobus/44-capability-matching-light.png)
![능력 맞추기: TC는 Version 메시지로 섹션 제어 붐 1·섹션 6을, 클라이언트는 붐 1·섹션 12를 줄이기 전 능력 그대로 알린다. 클라이언트는 TC가 다룰 수 있는 6개에 맞춰 물리 섹션 1~12를 이웃한 두 개씩 묶어 DDOP 섹션 1~6으로 보고한다](/images/study-isobus/44-capability-matching-dark.png)

리모컨 버튼이 6개뿐인데 조명이 12개라면 이웃한 조명 두 개씩을 한 버튼에 묶는 것과 같다. 대신 묶인 두 섹션은 늘 함께 켜지고 꺼지므로 섹션 제어가 조금 거칠어진다. 겹쳐 뿌리는 면적이 묶지 않았을 때보다 약간 늘 수 있다.

"줄이기 전 능력을 그대로 보고한다"는 규칙은 자기소개서에는 원래 실력을 적고, 실제 일은 상대에 맞춰 한다는 뜻이다. 나중에 더 큰 TC를 만나면 같은 작업기가 12개 섹션을 모두 따로 쓸 수 있다.

<small>근거: ISO 11783-10 F.2.2, F.2.3, B.5.3, D.47</small>

## 6. 파일 세트 하한과 TC-SC의 독립성 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

기능성마다 파일을 얼마나 크게 다뤄야 하는지, TC-SC만 따로 지원해도 되는지, TC-SC가 반드시 다룰 값은 무엇인지를 모았다.

- TC-BAS·LOG: FMIS와 TC(LOG 서버)는 서로의 한계를 고려해야 하고, 임베디드 쪽은 큰 파일 세트를 만들지 않아야 한다. 최소한 <strong>XML 요소 총 20,000개, 요소 타입당 2,000개</strong>짜리 파일 세트는 FMIS와 TC(LOG 서버) 구현 모두 처리해야 한다.
- TC-BAS 구현은 OperationTechnique, OperationTechniqueReference, CodedCommentGroup, Connection, 모든 기하·지리 참조 요소를 처리하지 않아도 된다. 건너뛰어도 되지만 나머지 내용은 읽어야 하고 파일 세트를 거부하면 안 된다.
- TC-SC는 TC-BAS·TC-GEO와 <strong>독립</strong>이다. 둘 중 무엇과도 함께 지원할 필요가 없고, TC-SC만 제공하는 제품은 파일 세트 처리나 FMIS-TC 연결을 지원하지 않아도 된다. 게시 버전도 Version 메시지에만 쓰도록 정해져 있다.

위 항목을 풀어 보면 다음과 같다.

- 임베디드 쪽은 트랙터 단말기처럼 메모리와 처리 능력이 작은 장치를 말한다. 사무실 컴퓨터(FMIS)가 수십만 개 요소의 파일을 만들면 단말기가 못 읽을 수 있으므로, 양쪽이 지킬 하한을 정해 둔 것이다.
- TC-SC가 독립이라는 말은 "작업 기록은 못 해도 겹쳐 뿌리기 방지만 하는 단말기"도 TC-SC 제품이 될 수 있다는 뜻이다.

TC-SC 필수 DDI를 역할별로 묶으면 다음과 같다. 이름은 표준 본문·그림 표기를 따랐다.

| 역할 | DDI |
|---|---|
| 기하 | 67 Actual Working Width, 70 Maximum Working Width, 134 Offset X, 135 Offset Y |
| 작업 상태 | 141 Actual Work State, 161~176 Actual Condensed Work State, 290~305 Setpoint Condensed Work State |
| 제어 상태 | 160 Section Control State |
| 지연 보정 | 142 Physical Setpoint Time Latency, 143 Physical Actual Time Latency, 205 SC Turn On Time, 206 SC Turn Off Time |

- 기하: 섹션의 폭과 위치(기준점에서 앞뒤 Offset X, 좌우 Offset Y)다. TC가 GPS 위치에서 각 섹션이 땅의 어디에 있는지 계산하는 데 쓴다.
- 작업 상태: 섹션이 지금 작업 중인지다. Condensed Work State는 섹션 여러 개의 켜짐·꺼짐을 한 값에 몰아 담은 것이다.
- 제어 상태: 섹션 제어를 자동으로 할지 수동으로 할지다.
- 지연 보정: 밸브를 연 뒤 실제로 약이 나오기까지 걸리는 시간이다. 트랙터가 움직이는 동안 이 시간만큼 미리 켜고 꺼야 경계에 정확히 맞는다.

<small>근거: ISO 11783-10 F.2.1, F.2.3, F.2.4(Table F.3)</small>

## 7. 버전 3과 버전 4 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

자기소개서의 버전 번호가 서로 다를 때 무엇이 달라지는지 모았다. 41~44장에 흩어져 나온 버전 4의 변화를 한곳에서 볼 수 있다.

표준은 기능성마다 게시할 버전 번호를 정한다. TC-BAS·TC-GEO·TC-SC generation 1은 <strong>3</strong>, LOG generation 1은 <strong>4</strong>다. 표준이 이유를 적지는 않지만, LOG가 4인 것은 DL 자체가 버전 4 기능이기 때문으로 보인다(추론).

TC 연결 계층에서 버전 4가 바꾼 것을 41~44장의 범위에서 모으면 다음과 같다. 마지막 열은 이 스터디에서 그 내용을 다룬 곳이다.

| 항목 | 버전 3 이하 | 버전 4 | 다룬 곳 |
|---|---|---|---|
| 클라이언트의 Request Version | 버전 3 기능을 쓰려면 권고 | 의무 | [43장 2절](/study/isobus/43-tc-connection) |
| TC의 클라이언트 버전 요청 | 의무 없음 | 클라이언트가 요청한 뒤 의무 | [43장 2절](/study/isobus/43-tc-connection) |
| TC가 보낸 Request Version에 응답 | - | 클라이언트 의무 | [43장 2절](/study/isobus/43-tc-connection) |
| TC와 통신하는 CF | (버전 3 이전) WS 전체 가능 | WSM 하나 | [43장 2절](/study/isobus/43-tc-connection) |
| Process Data 우선순위 | 모두 3 | Command별 3·4·5 | [43장 7절](/study/isobus/43-tc-connection) |
| 셧다운 절차 | 버전 2 미정의, 버전 3 비의무 | 의무 | [43장 5절](/study/isobus/43-tc-connection) |
| Object-pool Deactivate(Connection Deactivate) | 없음 | 있음 | [43장 10절](/study/isobus/43-tc-connection) |
| Request Identify Task Controller | 없음 | 있음 | [43장 8절](/study/isobus/43-tc-connection) |
| Language Command 응답(전역·직접) | 의무 없음 | 의무 | [42장 8절](/study/isobus/42-tc-task) |
| 클라이언트 standard setup 기준 | VT·TECU | 게시 대상 TC | [42장 8절](/study/isobus/42-tc-task) |
| Data Logger | 없음 | 있음 | 이 장 3절 |
| 태스크 상태 Template·Canceled | 없음 | 있음 | [42장 5절](/study/isobus/42-tc-task) |
| Time의 시간대, Type 8 Powered Down | 현지 시각만 | 시간대·UTC, Type 8 추가(Type 3 폐기) | [42장 6절, 9절](/study/isobus/42-tc-task) |
| TaskControllerCapabilities 요소 | 없음 | 있음 | [43장 8절](/study/isobus/43-tc-connection) |

Version 메시지 Byte 3~8(boot time·옵션·붐·섹션·채널)은 그보다 앞선 버전 3에서 생겼다. 버전 2 이하 상대는 이 바이트를 `FF`로 보낸다.

버전이 다른 TC와 클라이언트가 만나면 낮추는 쪽은 클라이언트다. TC가 필요한 버전·기능을 지원하지 않으면 클라이언트가 자기 버전·기능을 TC 수준으로 제한한다. 버전 4 클라이언트가 버전 3 TC를 만나면 Deactivate·Identify TC·peer control 같은 버전 4 기능에 기대면 안 되고, 버전 3 TC는 클라이언트 버전을 물을 의무가 없으므로 그 요청을 기다리며 멈춰서도 안 된다. process data 쪽 버전 차이는 [45장 TC 프로세스 데이터 기초](/study/isobus/45-tc-process-data-basics)와 [46장 명령 니블과 PDACK](/study/isobus/46-tc-commands-pdack)에서 다룬다.

신형 휴대폰이 구형 무선 이어폰과 연결할 때 구형이 지원하는 방식으로 맞춰 주는 것과 같다. 맞춰 주는 쪽은 늘 새것(클라이언트)이고, 구형이 모르는 기능을 기다리며 멈추면 연결이 성립하지 않는다.

::: warning 확인 필요: 버전 4 제품이 TC-BAS에 게시할 번호
기능성 정의 문구대로면 TC-BAS·TC-GEO·TC-SC gen 1 구현은 Version 메시지와 파일 세트에 3을 게시해야 한다. 그런데 버전 질의·응답 의무, 셧다운 절차, Connection Deactivate 같은 버전 4 의무를 모두 구현한 제품이 TC-BAS 적합을 위해 3을 게시해야 하는지, 4를 게시해도 되는지는 기능성 정의만으로 판단이 서지 않는다. 제품 설계 전에 AEF 적합성 시험 기준을 확인해야 한다.
:::

::: details 원문을 가진 독자를 위한 메모
- 위 "확인 필요"는 ISO 11783-10:2015 Annex F.2.1~F.2.4의 게시 버전 문구(TC-BAS·TC-GEO·TC-SC는 3, LOG는 4)와 6.6.2 f)~g), 6.6.4, B.6.10 같은 버전 4 의무가 만나는 지점이다.
- 버전 비교 표 각 행의 근거 조항: Request Version 6.6.2 f, TC의 클라이언트 버전 요청 6.6.1 e, Request Version 응답 6.6.2 g, WSM 한정 6.6.2 d와 B.2, 우선순위 B.2, 셧다운 6.6.4, Deactivate B.6.10, Identify TC B.5.4, Language Command와 standard setup 6.5, Data Logger 5.6과 7.2, 태스크 상태 6.1, Time 6.2와 D.48, TaskControllerCapabilities D.47.
:::

<small>근거: ISO 11783-10 5.6, 6.6.1, 6.6.2, F.2.1~F.2.4, B.5.3</small>

::: tip 핵심 정리
- TC 번호는 NAME의 function instance + 1(1~32)이다. function instance 0인 primary TC가 네트워크에 늘 있어야 하고, 클라이언트는 기본으로 여기에 붙는다.
- 다른 TC로 옮길 때는 안전 상태 → Connection Deactivate → Client Task 중단 → 새 TC와 초기화 순서를 밟고, 새 TC를 preferred TC로 저장한다.
- DL은 기록만 하는 TC의 부분집합이다. 섹션 제어·위치 기반 제어·peer control 할당은 금지이고, TC와 DL에 함께 붙은 클라이언트는 measurement와 total을 서버별로 따로 관리한다.
- 기능성은 TC-BAS·TC-GEO·TC-SC·LOG 넷이고 모두 generation 1이다. TC-GEO는 TC-BAS를 함께 요구하지만 TC-SC는 독립이다. 게시 버전은 BAS·GEO·SC가 3, LOG가 4다.
- 붐·섹션·채널 수는 서버가 Version 메시지로 자기소개하고 클라이언트가 DDOP를 줄여 맞춘다. 클라이언트의 Version 메시지에는 줄이기 전 원래 능력을 적는다.
:::

::: details 확인 문제
1. (계산) 어떤 TC의 Address Claimed 데이터 Byte 5가 `0x10`이다. function instance와 TC 번호는 각각 얼마인가?
2. (개념) DL이 TC와 같은 점 두 가지, 다른 점 두 가지를 들어 보라.
3. (개념) 클라이언트가 TC 1에서 TC 2로 옮길 때 왜 먼저 안전 상태로 가고 Connection Deactivate를 보내는가?
4. (디코딩) 붐 1개·물리 섹션 7개·위치 기반 제어 채널 1개를 가진 버전 4 클라이언트가 TC-BAS·TC-GEO(위치 기반 제어)·TC-SC를 지원한다. 이 클라이언트가 TC에게서 Version 응답 `10 03 FF 11 00 01 05 00`을 받았다. TC에 대해 무엇을 알 수 있고, 클라이언트는 DDOP와 동작을 어떻게 바꿔야 하는가? 클라이언트 자신의 Version 메시지 Byte 6~8에는 무엇을 넣는가?

**답 가이드**

1. `0x10`은 `0001 0000`이다. 위쪽 5비트(bits 8~4)는 `00010`이므로 `0x10 >> 3` = 2가 function instance이고, 아래 3비트는 ECU instance 0이다. TC 번호는 2 + 1 = 3이다.
2. 같은 점: TC의 process data 프로토콜과 연결 절차를 그대로 쓴다. TC Status를 보내고 Client Task를 받는다. Version 메시지의 boot time도 의미 있다. 다른 점: DL은 섹션 제어와 위치 기반 제어, peer control 할당을 하지 않는다. 값 설정 명령은 task total DDI에만 보낸다. 버전 4에서 생겼고, function instance 0이 특별하지 않다.
3. 연결을 바꾸는 동안 섹션·rate 명령이 주인 없이 남지 않도록 먼저 안전 상태로 간다. Connection Deactivate는 현재 TC가 이 끊김을 비정상 종료로 오인해 경고를 띄우지 않도록 "의도적으로 끊는다"고 알리는 것이다. 응답은 최대 2 s 기다린다(이 두 이유는 표준이 적지 않은 해설이다).
4. Byte 2 = 3이므로 2판 DIS(버전 3) TC다. Byte 3 = `FF`는 boot time 정보 없음이고, Byte 4 = `0x11`은 TC-BAS(bit 1) + TC-SC(bit 5)라 TC-GEO는 지원하지 않는다(bit 2·3 = 0). Byte 6~8 = 1·5·0은 섹션 제어 붐 1개, 섹션 5개, 위치 기반 제어 채널 0개다. 클라이언트는 물리 섹션 7개를 묶어 DDOP에 섹션 5개 이하로 보고하고, DDOP의 위치 기반 제어 채널 수를 0으로 제한한다(5절). TC가 버전 3이므로 기능도 버전 3 수준으로 낮춰 Deactivate·Identify TC·peer control에 기대지 않고, TC의 Request Version을 기다리며 멈추지 않는다(7절). 자기 Version Byte 6~8에는 조정 전 능력인 `01 07 01`을 넣는다(5절).
:::

## 다음 챕터

- 다음: [45장 TC 프로세스 데이터 기초](/study/isobus/45-tc-process-data-basics)
