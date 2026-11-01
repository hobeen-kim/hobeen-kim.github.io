---
title: "VT 연결 관리: 초기화, 감시, 셧다운"
description: "작업기가 VT에 붙는 초기화 순서와 저장된 풀을 다시 쓰는 비휘발성 메모리 명령, VT Status와 Working Set Maintenance로 연결을 지키고 끊김을 판정하는 법, 여러 VT 가운데 하나를 고르는 법을 익힌다."
date: 2026-04-13
tags: [ISOBUS, VT, Virtual Terminal, ISO-11783-6, VT Status, Working Set Maintenance]
prev: /study/isobus/30-vt-display-technical-data
next: /study/isobus/32-vt-object-pool-basics
---

# VT 연결 관리: 초기화, 감시, 셧다운

::: info 학습 목표
- 작업기가 VT에 붙을 때 밟는 초기화 단계를 순서대로 말하고, 상태 흐름 그림으로 설명할 수 있다.
- Store·Load·Delete Version으로 풀을 저장해 두고 다시 쓰는 방법과 버전 라벨 규칙을 설명할 수 있다.
- VT Status와 Working Set Maintenance 프레임을 바이트·비트 단위로 읽어 소유 Working Set(WS), busy 상태, WS 버전을 판정할 수 있다.
- 연결이 끊겼을 때 VT와 작업기가 각각 무엇을 판정하는지, VT가 경보를 띄워야 하는지 진단할 수 있다.
- 여러 VT가 있을 때 VT Number로 VT를 고르고 다른 VT로 옮기는 순서를 설명할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [29장 Virtual Terminal(VT) 기초](/study/isobus/29-vt-basics), [30장 VT 화면 구성과 기술 데이터](/study/isobus/30-vt-display-technical-data), [10장 요청과 응답](/study/isobus/10-j1939-request-ack)
- 이 장에서 처음 나오는 말
  - 초기화(initialization): 전원을 켠 뒤 서로를 찾고 풀을 올려 화면을 쓸 수 있게 되기까지의 절차.
  - 비휘발성 메모리(non-volatile memory): 전원이 꺼져도 내용이 남는 저장소. VT는 여기에 풀을 저장해 둘 수 있다.
  - 버전 라벨(version label): 저장해 둔 풀에 붙이는 7자 또는 32자 이름표.
  - Initiating 비트: Working Set Maintenance의 첫 메시지에만 1로 켜는 "지금 막 연결을 시작한다" 표시.
  - busy 비트: VT Status Byte 7에 담긴, VT가 지금 무슨 일로 바쁜지 알리는 비트들.
  - unexpected shutdown: 작업기가 정상 절차 없이 사라진 상황. VT는 운전자에게 경보한다.
:::

전화를 걸면 먼저 상대가 받는지 확인하고, 통화 중에는 상대 목소리로 연결이 살아 있음을 알며, 끝낼 때는 "끊는다"고 말하고 끊는다. VT(Virtual Terminal, 트랙터 운전석의 공용 화면)와 작업기의 연결도 같다. 이 장은 작업기가 VT에 붙는 초기화 순서, 저장해 둔 풀로 빠르게 다시 붙는 방법, 1초마다 오가는 두 주기 메시지로 연결을 지키는 법, 끊겼을 때와 키를 껐을 때의 처리, 여러 VT 가운데 하나를 고르는 방법을 차례로 본다.

## 1. 초기화 전체 흐름

이 절에서는 VT와 작업기가 전원을 켠 뒤 화면을 띄우기까지 각자 밟는 단계를 본다. [29장](/study/isobus/29-vt-basics) 7절은 "처음 연결 + 전체 업로드"의 최소 경로를 바이트로 따라갔다. 표준은 그 앞뒤까지 포함한 전체 절차를 VT 쪽 4단계, WS 쪽 10단계로 정한다. 이 절은 그 절차를 상태 흐름으로 정리하고, 4절에서 저장된 풀로 다시 붙는 두 번째 전원 사이클을 바이트로 따라간다.

### VT 쪽 초기화

1. ISO 11783-5(네트워크 관리를 정하는 표준 문서)에 따라 주소 클레임을 마치고, 글로벌 주소(255)로 address claim 요청도 보낸다. 주소 클레임은 장치가 쓸 주소를 버스에 선언해 확보하는 절차이고([13장](/study/isobus/13-j1939-address-claim)), address claim 요청은 "모두 자기 주소를 다시 알려 달라"는 요청이다.
2. VT Status 송신을 시작한다. 리셋·복구로 다시 시작할 때는 이전 마지막 VT Status와 새 첫 VT Status 사이에 <strong>3초 넘는</strong> 간격을 보장해야 한다. 표준이 이유를 적지는 않지만, WS들의 3초 타임아웃이 반드시 한 번 터지게 해서 이전 연결 상태를 버리고 처음부터 초기화하게 하려는 것으로 보인다.
3. 운전자가 언어를 고른 적이 없으면 TECU(트랙터의 전자 제어 장치, [22장](/study/isobus/22-tractor-ecu))에 기본 언어를 요청하거나 운전자에게 고르게 한다.
4. WS들이 초기화하고 풀을 올리게 한다.

### Working Set 쪽 초기화

표의 "수준" 칸에서 shall은 반드시 해야 하는 단계, can은 해도 되는 단계다. 메시지 칸의 Part 5는 ISO 11783-5이고, PGN(Parameter Group Number)은 메시지의 종류를 가리키는 번호다.

| 단계 | 할 일 | 수준 | 메시지 |
|---|---|---|---|
| 1 | 보조 입력 기능이 있으면 휘발성 메모리의 할당을 모두 지운다 | shall | - |
| 2 | Master·Member 주소 클레임 | shall | Address Claimed(Part 5) |
| 3 | VT가 VT Status를 보내기 시작할 때까지 기다린다 | shall | VT Status(`0xFE`) |
| 4 | 자신과 멤버를 VT에 알린다 | shall | PGN 65037(0xFE0D) Working Set Master, PGN 65036(0xFE0C) Working Set Member |
| 5 | Working Set Maintenance 주기 송신 시작, 첫 메시지만 Initiating | shall | Working Set Maintenance(`0xFF`) |
| 6 | 언어·형식 메시지를 아직 못 받았고 표현이 언어·단위에 의존하면 요청 | can | Request(요청 대상 PGN 65039) |
| 7 | VT 능력을 묻고, 그 결과에 맞춰 풀을 스케일·폰트·색에 맞게 조정 | 질의 can, 조정 shall | 기술 데이터 메시지([30장](/study/isobus/30-vt-display-technical-data)) |
| 8 | 자기 풀이 이미 비휘발성 메모리에 있는지 묻는다 | can | (Extended) Get Versions |
| 9 | 풀 전송을 시작해 끝낸다: 비휘발성 메모리에서 로드하거나 오브젝트 풀 전송 절차로 전송 | shall | Load Version 또는 Object Pool Transfer·End of Object Pool |
| 10 | 풀이 지원하는 언어를 알린다 | can | - |

몇 단계는 순서 자체가 규칙이다.

- <strong>3단계</strong>: VT Status가 오기 전에는 VT와 데이터 통신을 시작하면 안 된다.
- <strong>4단계</strong>: 단일 ECU WS라면 Working Set Master 메시지는 `01 FF FF FF FF FF FF FF`(Byte 1 = 멤버 수, Master 포함)이고 Member 메시지는 없다. 초기화 뒤에 멤버를 바꾸려면 두 메시지를 다시 보내면 되고 재초기화는 필요 없다. 29장 7절 타임라인은 이 단계를 생략했지만, 실제로는 첫 Working Set Maintenance 앞에 이 메시지가 나가야 한다.
- <strong>5단계의 NACK 해제 조건</strong>: VT가 이 WS의 셧다운을 감지해 Maintenance에 NACK(부정 응답)를 보내던 중이라면, 다음 두 경우에만 NACK를 멈춘다. (I) Maintenance가 version 3 이상 준수를 표시하고 Initiating 비트가 1이며, 직전 Maintenance 이후 Working Set Master 메시지를 받았을 때. (II) version 2 이하 준수를 표시하고, 직전 Maintenance 이후 Working Set Master 메시지를 받았을 때. 재접속하는 WS가 Working Set Master 메시지를 빼먹거나 Maintenance보다 늦게 보내면 VT는 계속 NACK를 보낸다(7절).
- <strong>7단계</strong>: 능력 질의는 선택(can)이지만, 그 결과에 따른 풀 조정은 의무(shall)다.

### 상태 흐름으로 보기

10단계를 WS 구현의 상태로 묶으면 아래와 같다. 상태(state)는 프로그램이 지금 어느 단계에 있는지를 나타내고, 화살표는 어떤 일이 생기면 다음 상태로 넘어가는지 보여 준다. 그림의 EOP는 End of Object Pool이다. Get Versions(저장된 풀 목록 묻기), Load Version(저장된 풀 불러오기), Store Version(지금 풀 저장하기)은 2절에서 자세히 본다.

그림에는 "연결 완료"에서만 VT Status 끊김을 그렸지만, 실제로는 3단계 이후 어느 상태에서든 VT Status가 3초 끊기면 안전 상태로 간다. 안전 상태(safe state)는 VT 화면이 없어도 사람과 기계가 위험하지 않은, 미리 정해 둔 상태다.

![Working Set 초기화 상태 흐름: 주소 클레임, VT Status 대기, WS 식별, Maintenance 시작, 기술 데이터·저장 버전 조회를 거쳐 맞는 라벨이 있으면 Load Version, 없으면 전체 업로드와 선택적 Store Version으로 연결 완료에 이르고, EOP 오류나 VT Status 3초 끊김이면 안전 상태로 가는 흐름](/images/study-isobus/15-client-init-state-light.png)
![Working Set 초기화 상태 흐름: 주소 클레임, VT Status 대기, WS 식별, Maintenance 시작, 기술 데이터·저장 버전 조회를 거쳐 맞는 라벨이 있으면 Load Version, 없으면 전체 업로드와 선택적 Store Version으로 연결 완료에 이르고, EOP 오류나 VT Status 3초 끊김이면 안전 상태로 가는 흐름](/images/study-isobus/15-client-init-state-dark.png)

갈림길이 있는 상태만 표로 정리하면 다음과 같다. 표의 〃는 "위와 같음"이다.

| 상태 | 나가는 조건 | 다음 상태 |
|---|---|---|
| 기술 데이터·저장 버전 조회 | Get Versions 응답에 맞는 라벨이 있음 | Load Version |
| 〃 | 라벨이 없음(N = 0) 또는 저장 기능을 쓰지 않음 | 전체 업로드 |
| Load Version | 응답 Error Codes = 0 | 연결 완료 |
| 〃 | 오류 응답, 또는 parsing = 0인 VT Status 3연속 동안 무응답 | 전체 업로드(또는 Load 재시도) |
| 전체 업로드 | Get Memory Status = 1 | 기능을 줄인 풀 크기로 다시 질의 |
| 〃 | End of Object Pool 무응답 | End of Object Pool 최대 3회 재시도 뒤 VT 셧다운으로 처리 |
| 〃 | End of Object Pool response 오류 없음 | Store Version(선택) → 연결 완료 |
| 〃 | End of Object Pool response 오류 | 안전 상태. 풀이 지워졌다면 기능을 줄인 풀로 재시도할 수 있다 |
| 연결 완료 | VT Status 3초 끊김 | 안전 상태 → 재연결하는 설계면 초기화 재시작 |

이 장에서 "원문"은 ISO 11783-6(VT를 정하는 표준 문서) 자체를 말한다. Load 실패 뒤 전체 업로드로 가는 넘어감은 원문이 직접 적은 것이 아니다. 9단계("비휘발성 메모리에서 로드하거나 오브젝트 풀 전송 절차로 전송해 풀 전송을 끝낸다")를 다른 방법으로 마치는 것이다.

::: tip 정리
- VT는 주소 클레임 뒤 VT Status 송신을 시작하고, WS는 VT Status를 본 뒤에야 VT와 통신을 시작한다.
- WS는 자신과 멤버를 알리고(Working Set Master), Maintenance를 시작하고, VT 능력을 물은 뒤, 저장된 풀을 Load하거나 전체를 업로드한다.
- VT Status를 처음 받은 뒤(3단계 이후)에는 어느 단계에서든 VT Status가 3초 끊기면 안전 상태로 간다.
:::

<small>근거: ISO 11783-6 4.6.6, 4.6.9, C.2.2, C.2.5, G.2, ISO 11783-7 B.23</small>

## 2. 비휘발성 메모리: 저장해 둔 풀로 빨리 붙기

이 절에서는 VT가 풀을 저장해 두었다가 다음 연결 때 메시지 하나로 복원하는 방법과 그 규칙을 본다.

풀이 크면 업로드에 오래 걸린다. 8바이트보다 긴 데이터를 여러 프레임으로 나눠 보내는 TP·ETP([15장](/study/isobus/15-tp-bam-cmdt), [17장](/study/isobus/17-etp))로 보내야 하고, 다른 풀을 받는 중인 VT는 CTS의 패킷 수를 0으로 보내 오래 기다리게 할 수도 있다. CTS(Clear To Send)는 TP 연결에서 받는 쪽이 "이만큼 보내라"고 알리는 메시지이고, 패킷 수 0은 "잠깐 기다려라"는 뜻이다([15장](/study/isobus/15-tp-bam-cmdt)). 그래서 표준은 VT가 풀을 비휘발성 저장소에 저장해 두었다가 다음 연결에서 메시지 하나로 복원하게 한다.

보관함에 짐을 맡기며 이름표를 붙여 두면, 다음에는 이름표만 말하고 찾아갈 수 있다. 버전 라벨이 그 이름표이고, Store Version이 맡기기, Load Version이 찾기, Delete Version이 버리기다.

### 공통 규칙

- 저장·복원 단위는 WS의 풀 전체다(모든 오브젝트 정의 포함).
- WS는 <strong>WS Master의 NAME 전체</strong>로 식별되고, VT는 저장 풀을 특정 WS에 유일하게 묶는 방법을 가져야 한다. SA(Source Address, 장치가 버스에서 쓰는 1바이트 주소)가 아니라 NAME(장치를 식별하는 64비트 이름)이 기준이므로 다음 전원 사이클에 SA가 바뀌어도 같은 WS로 인식된다. 반대로 Identity Number가 다른 교체 ECU는 이전 풀을 찾지 못한다(추론). Identity Number는 제조사가 장치마다 다르게 매기는 NAME 안의 고유 번호다([12장](/study/isobus/12-j1939-address-name)).
- 각 WS Master는 <strong>자기 버전만</strong> 다룰 수 있고, 이 명령들은 <strong>Master만</strong> 보낼 수 있다(Member 불가). 매크로 안에서도 쓸 수 없다.
- 기술 데이터로 보고하는 특성(예: Data Mask 크기, [30장](/study/isobus/30-vt-display-technical-data))을 바꿀 수 있는 VT는 저장 풀을 특성 묶음과 연결하거나 저장 풀을 지우는 내부 방법을 가져야 한다.
- WS당 풀을 하나만 관리하는 VT도, 여러 개를 관리하는 VT도 있다. 각 풀은 version label로 구분한다(should, 권장).
- 비휘발성 연산은 얼마나 걸릴지 알 수 없어 응답이 늦어질 수 있다. 그동안 VT Status가 바쁨을 반영하고, VT는 연산을 마친 뒤에만 응답한다.
- WS는 저장된 버전을 조회해, 자기 현재 소프트웨어 버전에 맞는 것이 있는지 확인한 뒤에 복사를 요청해야 한다(shall).

### 버전 라벨 형식

| VT 버전 | 라벨 | 쓰는 메시지 |
|---|---|---|
| 4 이하 | 7자 8-bit string만 | Get Versions·Store·Load·Delete Version |
| 5 이상 | 7자 또는 32자 | 7자는 위 메시지, 32자는 Extended 계열 |

8-bit string은 한 글자를 1바이트로 적는 문자열이다.

- 라벨은 운전자에게 표시되거나 파일 이름으로 쓰일 수 있다. 그래서 font type 0(ISO 8859-1 Latin 1)의 보이는 문자로만 만들고, 정해진 길이까지 뒤를 공백(`0x20`)으로 채운다. font type 0은 영문과 서유럽 문자를 1바이트로 담는 VT의 기본 문자 집합이다.
- 다음 11개 문자는 쓸 수 없다: `\`(`0x5C`) `"`(`0x22`) `'`(`0x27`) `` ` ``(`0x60`) `/`(`0x2F`) `:`(`0x3A`) `*`(`0x2A`) `<`(`0x3C`) `>`(`0x3E`) `|`(`0x7C`) `?`(`0x3F`).
- 특수 라벨이 둘 있다. <strong>전부 공백</strong>이면 "마지막으로 저장한 버전"이다. Store는 그것을 덮어쓰고(저장된 것이 없으면 오류), Load는 그것을 읽고, Delete는 그것을 지운다(반복하면 직전 것부터 차례로 지운다). <strong>`*` + 공백</strong>(7자면 공백 6개, 32자면 31개)은 Delete에서 와일드카드로, 요청한 WS 소유의 같은 길이 라벨 풀을 전부 지운다(version 6 이상). `*`가 라벨 금지 문자라 실제 라벨과 겹칠 일이 없다(추론). 와일드카드(wildcard)는 "아무것이나"를 뜻하는 표시다.

### 명령별 동작

- <strong>Store</strong>: 언제든 보낼 수 있고, 같은 라벨이 있으면 덮어쓴다. 모든 오브젝트를 <strong>현재 상태 그대로</strong>(현재 속성·입력값 포함) 저장하므로, 운용 중 값이 바뀐 뒤 저장하면 그 값이 다음 Load 때의 초깃값이 된다. 처리 중에는 VT Status Byte 7 bit 1(비휘발성 메모리에 저장 중)이 이름 그대로 대응한다. bit 2(명령 실행 중)와 Byte 8을 함께 쓰는지는 원문이 정하지 않았다(확인 필요).
- <strong>Load</strong>: 이미 로드된 풀이 있으면 덮어쓴다. 긍정 응답을 받으면 WS는 "모든 오브젝트를 정상 전송한 것처럼" 진행해도 된다. End of Object Pool을 따로 보내지 않는다. VT는 Load를 받은 때부터 파싱을 마치고 응답을 보낼 때까지 VT Status Byte 7 <strong>bit 4(parsing)를 1</strong>로 둔다. WS Master는 parsing = 0인 VT Status를 <strong>연속 3번</strong> 받을 때까지 응답을 기다리고, 그때도 응답이 없으면 명령이 VT에 닿지 않았다고 본다. 3번을 기다리는 이유는 이미 송신 큐에 들어 있던 VT Status가 파싱 상태를 잘못 반영하는 경쟁 상태를 피하려는 것이다([29장](/study/isobus/29-vt-basics) 7절). Extended Load도 같다.
- <strong>Delete</strong>: 비휘발성 저장소에만 작용한다. 같은 버전이 휘발성 메모리에 올라가 있어도 그쪽은 남는다. 휘발성 풀을 지우는 것은 Delete Object Pool(`0xB2`, [37장](/study/isobus/37-vt-command-details))이다.

### 라벨 설계 예

라벨에 "이 풀이 어느 소프트웨어 버전·화면 조건에서 만든 것인가"를 넣어 두면, 초기화 8단계의 "맞는 버전 확인"을 문자열 비교로 끝낼 수 있다. 아래는 설계 예이며 표준이 정한 형식이 아니다.

- 7자: `P` + 풀 CRC 앞 6자리 16진수. 예: `P3A9F1C`. CRC는 데이터가 바뀌면 함께 바뀌는 검사값이다.
- 32자: 장비·풀 버전·Data Mask 크기·언어. 예: `SPRAYER-UI-2.3.1-480-de` 뒤를 공백으로 채움.

Data Mask 크기를 넣는 이유는 WS가 VT 크기에 맞춰 풀을 스케일해 올리기 때문이다([30장](/study/isobus/30-vt-display-technical-data) 1절). 다른 크기 조건에서 저장한 풀은 맞지 않는다. 언어를 넣으면 언어별 풀을 따로 저장해 두고 Language command에 맞는 것을 고를 수 있다([30장](/study/isobus/30-vt-display-technical-data) 6절).

::: tip 정리
- VT는 풀을 버전 라벨과 함께 비휘발성 메모리에 저장해 두고, 다음 연결 때 Load Version 하나로 복원할 수 있다.
- 7자 라벨은 모든 버전, 32자 라벨(Extended)은 version 5 이상이다. 와일드카드 삭제는 version 6 이상이다.
- Load는 parsing 비트와 "parsing = 0 연속 3번" 규칙으로 기다린다. Store는 현재 값까지 저장한다.
:::

<small>근거: ISO 11783-6 Annex E(E.1, E.1.2, E.1.3, E.6, E.14), C.2.2, F.44</small>

## 3. 비휘발성 메모리 명령의 바이트 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절에서는 2절의 명령들이 실제로 어떤 바이트로 오가는지, 오류 코드를 어떻게 읽는지 본다.

### 메시지와 바이트

| 코드 | 방향 | 메시지 | 데이터 |
|---|---|---|---|
| `0xDF` | WS→VT | Get Versions | Byte 2~8 `FF` |
| `0xE0` | VT→WS | Get Versions response | Byte 2 = 라벨 수 N, Byte 3~ = 7바이트 라벨 N개. 없으면 N = 0, 나머지 `FF` |
| `0xD0`·`0xD1`·`0xD2` | WS→VT | Store·Load·Delete Version | Byte 2~8 = 7자 라벨 |
| `0xD3` | 양방향 | Extended Get Versions·response | 요청 Byte 2~8 `FF`. 응답 Byte 2 = N, Byte 3~ = 32바이트 라벨 N개 |
| `0xD4`·`0xD5`·`0xD6` | WS→VT | Extended Store·Load·Delete Version | 33바이트: Byte 1 + 32자 라벨 |
| `0xD0`~`0xD6` | VT→WS | 각 명령의 response | 8바이트: Byte 2~5 `FF`, Byte 6 Error Codes, Byte 7~8 `FF` |

::: warning 구현 함정 두 가지
- <strong>Get Versions만 응답 코드가 다르다.</strong> 요청은 `0xDF`, 응답은 `0xE0`이다. 나머지 비휘발성 명령은 요청·응답 코드가 같고, Extended Get Versions도 `0xD3`으로 같다. "응답 코드 = 요청 코드"로 짝을 맞추는 파서는 Get Versions 응답을 놓친다.
- <strong>8바이트를 넘는 경우.</strong> 7자 명령은 1 + 7 = 8바이트라 단일 프레임이지만, Extended 명령은 33바이트라 TP(CMDT)로 보내야 한다. CMDT는 상대 하나와 연결을 맺고 보내는 TP 방식이다([15장](/study/isobus/15-tp-bam-cmdt)). Get Versions 응답도 라벨이 하나만 있어도 2 + 7 = 9바이트라 TP로 온다. 라벨이 없을 때만 `E0 00 FF FF FF FF FF FF` 한 프레임이다.
:::

### 오류 코드(response Byte 6)

Byte 6의 비트 하나하나가 오류 하나를 뜻한다. 비트 번호는 0부터 센다.

| bit | Store(`0xD0`·`0xD4`) | Load(`0xD1`·`0xD5`) | Delete(`0xD2`·`0xD6`) |
|---|---|---|---|
| 0 | 예약 | 파일 시스템 오류·풀 데이터 손상(7자 Load는 version 4 이상) | 예약 |
| 1 | 라벨이 올바르지 않음 | 라벨이 올바르지 않거나 모르는 라벨 | 라벨이 올바르지 않거나 모르는 라벨 |
| 2 | 메모리 부족 | 메모리 부족 | 예약 |
| 3 | 기타 오류 | 기타 오류 | 기타 오류 |

값 0은 성공이다. Delete는 와일드카드 삭제를 수행했을 때도 0이다. 예를 들어 Load 응답 Byte 6이 `02`(=`0000 0010`)이면 bit 1, 즉 "라벨이 올바르지 않거나 모르는 라벨"이다.

### busy 비트에 대해 원문이 정하지 않은 것

원문이 명령별 busy 비트를 명시한 것은 Load의 parsing 비트뿐이고, Delete·Get Versions 처리 중 어느 비트를 켤지는 정해져 있지 않다. 또 Byte 7에서 즉시 송신을 일으키는 것은 bit 6뿐이므로(6절), WS는 busy 비트 변화를 다음 주기 메시지에서야 볼 수도 있다.

::: details 라벨 만들기·검사 코드
아래 코드는 라벨 규칙(길이, 금지 문자, 공백 채움)을 지키는 라벨을 만들고, Store·Extended Store·와일드카드 Delete 프레임을 조립해 확인한다.

```python
FORBIDDEN = set('\\"\'`/:*<>|?')


def version_label(text: str, size: int = 7) -> bytes:
    if len(text) > size:
        raise ValueError("라벨이 너무 길다")
    for c in text:
        if c in FORBIDDEN or not 0x21 <= ord(c) <= 0x7E:
            raise ValueError(f"쓸 수 없는 문자: {c!r}")
    return text.ljust(size).encode("latin-1")


store = bytes([0xD0]) + version_label("TEMP_V1")
assert store.hex(" ").upper() == "D0 54 45 4D 50 5F 56 31"

ext_store = bytes([0xD4]) + version_label("SPRAYER-UI-2.3.1-480-de", 32)
assert len(ext_store) == 33                         # 8바이트 초과 → TP(CMDT)

wildcard7 = bytes([0xD2]) + b"*" + b" " * 6         # v6 이상: 7자 라벨 풀 전부 삭제
assert wildcard7.hex(" ").upper() == "D2 2A 20 20 20 20 20 20"

for bad in ("V1/2", "A:B", "X*"):
    try:
        version_label(bad)
    except ValueError:
        continue
    raise AssertionError(f"금지 문자를 통과시켰다: {bad}")
print("라벨 검증 통과")
```
`0x21`~`0x7E`로 제한한 것은 설계 선택이다. 원문은 font type 0의 보이는 문자를 허용하므로 Latin-1 상위 문자도 쓸 수 있지만, 파일 이름 호환을 생각하면 ASCII가 무난하다. 실행하면 `라벨 검증 통과`가 출력된다.
:::

::: tip 정리
- Get Versions 응답만 코드가 `0xE0`으로 다르다. Extended 명령과 라벨이 있는 Get Versions 응답은 TP로 오간다.
- 각 응답의 Byte 6이 오류 비트다. 0이면 성공이다.
:::

<small>근거: ISO 11783-6 E.2~E.14, Table A.5, G.2</small>

## 4. 두 번째 전원 사이클을 바이트로 따라가기

이 절에서는 1~3절의 내용이 실제 버스에서 어떤 순서와 바이트로 보이는지 시간 축 위에서 따라간다.

[29장](/study/isobus/29-vt-basics) 7절의 ECU(SA `0x81`)가 첫 연결을 마친 직후 풀을 저장하고, 다음 전원 사이클에 Load Version으로 다시 붙는 흐름이다. 라벨은 "TEMP_V1"(`54 45 4D 50 5F 56 31`), VT는 version 4다. 라벨 바이트는 각 글자의 ASCII 코드다(T = `54`, E = `45`, M = `4D`, P = `50`, _ = `5F`, V = `56`, 1 = `31`). 시각은 29장처럼 설명용 예시값이다.

표 읽는 법은 29장 7절과 같다. VT→ECU는 PGN 58880(0xE600), ECU→VT는 PGN 59136(0xE700)이고, 데이터는 Byte 1부터 Byte 8까지 16진수다. "VT→전체"는 글로벌로 보낸 메시지다.

<strong>첫 사이클 끝: 저장</strong>(29장 7절의 t=3.920s 화면 표시 직후)

| 시각 | 방향 | PGN | 데이터(hex) | 의미 |
|---|---|---|---|---|
| t=3.930s | ECU→VT | 0xE700 | `D0 54 45 4D 50 5F 56 31` | Store Version "TEMP_V1" |
| t=4.920s | VT→전체 | 0xE600 | `FE 81 01 00 FF FF 02 FF` | 주기 VT Status: Byte 7 bit 1(비휘발성 메모리 저장 중) = 1 |
| t=5.300s | VT→ECU | 0xE600 | `D0 FF FF FF FF 00 FF FF` | Store Version response: Byte 6 = 0, 저장 성공 |
| t=5.920s | VT→전체 | 0xE600 | `FE 81 01 00 FF FF 00 FF` | 주기 VT Status: busy 비트 모두 0 |

bit 6을 뺀 busy 비트의 변화는 즉시 송신 조건이 아니다(6절). 그래서 이 예에서는 bit 1이 켜진 것이 다음 주기(t=4.920s)에야 보인다.

<strong>다음 사이클: 저장된 풀로 연결</strong>

| 시각 | 방향 | PGN | 데이터(hex) | 의미 |
|---|---|---|---|---|
| t=0.000s | VT→전체 | 0xE600 | `FE FF FF FF FF FF 00 FF` | VT Status: 소유 WS 없음 |
| t=0.010s | ECU→전체 | 0xFE0D | `01 FF FF FF FF FF FF FF` | Working Set Master: 멤버 1(자신) |
| t=0.020s | ECU→VT | 0xE700 | `FF 01 04 FF FF FF FF FF` | Working Set Maintenance: Initiating = 1, Version 4 |
| t=0.030s | ECU→VT | 0xE700 | `C0 FF 00 00 00 00 FF FF` | Get Memory: Memory Required = 0, 버전만 확인 |
| t=0.040s | VT→ECU | 0xE600 | `C0 04 00 FF FF FF FF FF` | Get Memory response: Version 4, Status 0 |
| t=0.050s | ECU→VT | 0xE700 | `C7 FF FF FF FF FF FF FF` | Get Hardware |
| t=0.060s | VT→ECU | 0xE600 | `C7 1E 02 31 E0 01 E0 01` | Get Hardware response: 30장 8절의 480 × 480 VT |
| t=0.070s | ECU→VT | 0xE700 | `DF FF FF FF FF FF FF FF` | Get Versions |
| t=0.080s~ | VT→ECU | 0xE600 | TP 9바이트 `E0 01 54 45 4D 50 5F 56 31` | Get Versions response: 라벨 1개 "TEMP_V1" |
| t=0.200s | ECU→VT | 0xE700 | `D1 54 45 4D 50 5F 56 31` | Load Version "TEMP_V1" |
| t=1.000s | VT→전체 | 0xE600 | `FE FF FF FF FF FF 10 FF` | 주기 VT Status: parsing = 1 |
| t=1.020s | ECU→VT | 0xE700 | `FF 00 04 FF FF FF FF FF` | 두 번째 Maintenance: Initiating = 0 |
| t=1.300s | VT→ECU | 0xE600 | `D1 FF FF FF FF 00 FF FF` | Load Version response: 성공 |
| t=1.310s | VT→전체 | 0xE600 | `FE 81 01 00 FF FF 00 FF` | VT Status: `0x81` 소유, Data Mask 1. Byte 2~4가 바뀌어 즉시 송신 |

이 흐름을 1절의 상태 흐름에 맞춰 읽으면 다음과 같다.

1. t=0.000s: VT Status를 받아 "VT Status 대기"를 벗어난다.
2. t=0.010s~0.020s: Working Set Master로 자신을 알리고(WS 식별), 첫 Maintenance를 Initiating = 1로 보낸다.
3. t=0.030s~0.080s: 기술 데이터(Get Memory, Get Hardware)와 저장 버전(Get Versions)을 조회한다. 응답에 맞는 라벨 "TEMP_V1"이 있다.
4. t=0.200s~1.300s: Load Version을 보내고 parsing 비트를 지켜보다가 성공 응답을 받는다.
5. t=1.310s: VT Status Byte 2가 `0x81`로 바뀐다. 연결 완료다. 첫 사이클의 전체 업로드(29장 7절, 약 3.9초)보다 훨씬 빨리 화면이 뜬다.

- 두 번째 Maintenance의 Initiating은 0이다. 1을 또 보내면 VT는 이를 WS 재시작, 즉 unexpected shutdown으로 판정한다(6절).
- Get Memory를 Memory Required = 0으로 보낸 것은 버전만 확인하려는 것이다. Load가 실패해 전체 업로드로 넘어가면 그때 실제 크기로 다시 묻는다.
- Load가 실패하면 응답은 예를 들어 `D1 FF FF FF FF 02 FF FF`(bit 1, 모르는 라벨)로 온다. 상태 흐름대로 전체 업로드로 넘어가 29장 7절의 흐름을 밟는다. bit 0(파일 시스템 오류·데이터 손상)이었다면 업로드 뒤 같은 라벨로 Store해 손상된 사본을 덮어쓰는 것이 자연스럽다(추론).

::: details 두 경로의 프레임 검산
아래 코드는 두 표의 프레임을 조립해 같은 바이트가 나오는지 확인한다.

```python
def le(v, n):
    return v.to_bytes(n, "little")


label = "TEMP_V1".ljust(7).encode("latin-1")
frames = {
    "store": bytes([0xD0]) + label,
    "status_saving": bytes([0xFE, 0x81]) + le(1, 2) + le(0xFFFF, 2) + bytes([0b0000_0010, 0xFF]),
    "store_resp": bytes([0xD0]) + b"\xFF" * 4 + bytes([0x00]) + b"\xFF" * 2,
    "ws_master": bytes([0x01]) + b"\xFF" * 7,
    "wsm_first": bytes([0xFF, 0x01, 0x04]) + b"\xFF" * 5,
    "wsm_next": bytes([0xFF, 0x00, 0x04]) + b"\xFF" * 5,
    "get_memory_ver": bytes([0xC0, 0xFF]) + le(0, 4) + b"\xFF\xFF",
    "get_versions": bytes([0xDF]) + b"\xFF" * 7,
    "get_versions_resp": bytes([0xE0, 0x01]) + label,
    "load": bytes([0xD1]) + label,
    "status_parsing": bytes([0xFE, 0xFF]) + b"\xFF" * 4 + bytes([0b0001_0000, 0xFF]),
    "load_resp": bytes([0xD1]) + b"\xFF" * 4 + bytes([0x00]) + b"\xFF" * 2,
}
expect = {
    "store": "D0 54 45 4D 50 5F 56 31",
    "status_saving": "FE 81 01 00 FF FF 02 FF",
    "store_resp": "D0 FF FF FF FF 00 FF FF",
    "ws_master": "01 FF FF FF FF FF FF FF",
    "wsm_first": "FF 01 04 FF FF FF FF FF",
    "wsm_next": "FF 00 04 FF FF FF FF FF",
    "get_memory_ver": "C0 FF 00 00 00 00 FF FF",
    "get_versions": "DF FF FF FF FF FF FF FF",
    "get_versions_resp": "E0 01 54 45 4D 50 5F 56 31",
    "load": "D1 54 45 4D 50 5F 56 31",
    "status_parsing": "FE FF FF FF FF FF 10 FF",
    "load_resp": "D1 FF FF FF FF 00 FF FF",
}
for name, hexstr in expect.items():
    assert frames[name].hex(" ").upper() == hexstr, name
assert len(frames["get_versions_resp"]) == 9          # 8바이트 초과 → TP
print("초기화 프레임 검증 통과")
```
실행하면 `초기화 프레임 검증 통과`가 출력된다. 마지막 줄은 라벨 하나짜리 Get Versions 응답이 9바이트라 TP로 가야 한다는 것을 확인한다.
:::

<small>근거: ISO 11783-6 C.2.2, G.2, G.3</small>

## 5. 연결 감시: 1초마다 오가는 두 메시지

이 절에서는 연결이 살아 있는지 확인하는 두 주기 메시지를 시간 축 위에서 보고, 끊겼을 때 누가 무엇을 판정하는지 큰 그림을 잡는다. 메시지의 바이트는 6절, 경보 규칙은 7절에서 본다.

- <strong>VT Status</strong>(VT → 모두): VT가 1초마다 보낸다. 내용이 바뀌면 바로 한 번 더 보낸다(6절).
- <strong>Working Set Maintenance</strong>(WS → VT): 각 WS가 1초마다 보낸다. 첫 메시지만 Initiating 비트가 1이다.

두 메시지는 서로 묻고 답하는 관계가 아니다. 각자 1초마다 "나 여기 있다"고 알리는 신호이고, 받는 쪽은 그 신호가 끊기는지 지켜본다.

![시간 축 위의 연결 감시. VT Status는 0초부터 8초까지 1초마다 보인다. 경우 1에서는 Maintenance가 0초(Initiating=1)와 1·2·3초에 오고 끊기며, 마지막 메시지 뒤 3초가 지난 6초에 VT가 unexpected shutdown으로 판정한다. 경우 2에서는 3초 뒤 재부팅한 WS가 4초에 Initiating=1을 다시 보내고, VT가 3초를 기다리지 않고 바로 판정한다](/images/study-isobus/31-heartbeat-timeline-light.png)
![시간 축 위의 연결 감시. VT Status는 0초부터 8초까지 1초마다 보인다. 경우 1에서는 Maintenance가 0초(Initiating=1)와 1·2·3초에 오고 끊기며, 마지막 메시지 뒤 3초가 지난 6초에 VT가 unexpected shutdown으로 판정한다. 경우 2에서는 3초 뒤 재부팅한 WS가 4초에 Initiating=1을 다시 보내고, VT가 3초를 기다리지 않고 바로 판정한다](/images/study-isobus/31-heartbeat-timeline-dark.png)

그림은 VT가 WS의 사라짐을 알아채는 두 경우다.

1. <strong>경우 1: 통신이 끊긴다.</strong> 마지막 Maintenance가 3초에 왔고 그 뒤로 없다. VT는 3초를 더 기다린 6초에 unexpected shutdown으로 판정한다.
2. <strong>경우 2: WS가 재부팅한다.</strong> WS가 3초 직후 리셋되어 처음부터 다시 초기화하면, 4초에 Initiating = 1인 Maintenance가 또 온다. Initiating은 "지금 막 시작했다"는 표시이므로 두 번째로 보이면 정상 종료 없이 다시 시작했다는 증거다. VT는 3초를 기다리지 않고 바로 판정한다.

반대 방향도 같다. WS는 VT Status를 3초 동안 못 받으면 VT가 꺼진 것으로 보고 안전 상태로 간다.

::: tip 정리
- VT Status(VT → 모두)와 Working Set Maintenance(WS → VT)는 각자 1초마다 나가는 생존 신호다.
- 3초 동안 신호가 없으면 상대가 꺼진 것으로 본다. VT는 Initiating 비트를 두 번 보면 3초를 기다리지 않고 판정한다.
:::

<small>근거: ISO 11783-6 4.6.9, G.2, G.3</small>

## 6. VT Status와 Working Set Maintenance 바이트 읽기

이 절에서는 두 주기 메시지의 바이트 전체와, 모르는 메시지를 받았을 때 쓰는 Unsupported VT Function 메시지를 본다. 비트 번호는 0부터 센다(bit 7이 최상위).

### VT Status 메시지

![VT Status 메시지 8바이트 배치: Byte 1 0xFE, Byte 2 소유 WS Master SA, Byte 3·4 Data/Alarm Mask ID, Byte 5·6 Soft Key Mask ID, Byte 7 busy 비트, Byte 8 실행 중 VT function, 그리고 Byte 7을 bit 7 메모리 부족부터 bit 0 마스크 갱신 중까지 펼친 모습](/images/study-isobus/15-vt-status-layout-light.png)
![VT Status 메시지 8바이트 배치: Byte 1 0xFE, Byte 2 소유 WS Master SA, Byte 3·4 Data/Alarm Mask ID, Byte 5·6 Soft Key Mask ID, Byte 7 busy 비트, Byte 8 실행 중 VT function, 그리고 Byte 7을 bit 7 메모리 부족부터 bit 0 마스크 갱신 중까지 펼친 모습](/images/study-isobus/15-vt-status-layout-dark.png)

| Byte | 내용 |
|---|---|
| 1 | `0xFE`(VT function 254) |
| 2 | VT를 "소유"한(화면에 보이면서 입력 포커스도 가진) active WS Master의 SA. 소유자가 없으면 `FF`·`FE`·VT 자신의 SA 중 하나 |
| 3~4 | active WS의 보이는 Data/Alarm Mask Object ID(LE). 소유자가 없으면 `FFFF` |
| 5~6 | 보이는 Soft Key Mask Object ID. 소유자가 없거나 Soft Key Mask가 없으면 `FFFF` |
| 7 | busy 비트: bit 0 보이는 마스크 갱신 중, bit 1 비휘발성 메모리에 저장 중, bit 2 명령 실행 중, bit 3 매크로 실행 중, bit 4 풀 파싱 중(v3 이상), bit 5 예약(0), bit 6 보조 입력 learn 모드(v3 이상), bit 7 메모리 부족 |
| 8 | 실행 중인 명령의 VT function 코드. bit 2나 bit 3이 1일 때만 유효하고, 실행 중인 것이 없으면 `FF` |

입력 포커스는 운전자 입력을 받는 자리라는 뜻이다. learn 모드는 운전자가 보조 입력(AUX)과 기능을 짝짓는 화면에 있는 상태다([40장](/study/isobus/40-vt-aux)).

- 소유자 없음 값(`FF`·`FE`·VT SA)과 빈칸 채움값(`FF`·`FFFF`)은 version 6에서 명문화됐지만 이전 버전 VT도 써도 된다.
- <strong>송신 시점</strong>: Byte 2~6 또는 Byte 7 bit 6이 바뀌면 즉시, 그리고 초당 1회 보낸다. 최대 초당 5회다. 다른 busy 비트의 변화는 즉시 송신 조건이 아니다.
- <strong>목적지</strong>: 글로벌 주소(255)로 보낸다. 구현은 DA(Destination Address, 목적지 주소) = `0xFF`로 보낸다.
- VT를 소유하는 것과 연결이 살아 있는 것은 다르다. Byte 2가 자기 SA가 아니어도 VT Status가 계속 오는 한 연결은 살아 있다.

| 프레임 | 해석 |
|---|---|
| `FE 81 05 00 10 00 04 A8` | `0x81`이 소유, Data Mask 5, Soft Key Mask 16. bit 2 = 명령 실행 중이고, 실행 중인 명령은 `0xA8`(Change Numeric Value) |
| `FE 26 FF FF FF FF 40 FF` | VT 자신(`0x26`)이 "소유" = WS 소유자 없음. bit 6 = 보조 입력 learn 모드(이 비트가 바뀌어 즉시 송신됐다) |
| `FE FE FF FF FF FF 80 FF` | 소유자 없음(`FE`), bit 7 = VT 메모리 부족. 지금 풀을 올리면 실패할 가능성이 크다(추론) |

첫 프레임을 바이트 단위로 읽으면 다음과 같다.

1. Byte 1 `FE`: VT Status다.
2. Byte 2 `81`: `0x81` WS가 화면과 입력을 갖고 있다.
3. Byte 3~4 `05 00`: 리틀 엔디언으로 `0x0005`, 보이는 Data Mask는 5번이다.
4. Byte 5~6 `10 00`: `0x0010` = 16, 보이는 Soft Key Mask는 16번이다.
5. Byte 7 `04` = `0000 0100`: bit 2만 1, 명령 실행 중이다.
6. Byte 8 `A8`: bit 2가 1이므로 유효하다. 실행 중인 명령은 `0xA8`(=168) Change Numeric Value다.

::: details 원문을 가진 독자를 위한 메모
VT Status의 목적지는 본문(G.2, 4.6.8 Table 2·3)이 글로벌 주소(255)로 보내라고 하는데, G.2 메시지 정의 표의 Parameter group number 칸만 "Destination-Specific"으로 적혀 있다. 본문은 본문 규정을 따라 DA = `0xFF`로 적었다. 소유자 없음 값에 대한 설명은 G.2 각주에 있다.
:::

### Byte 2의 version 6 규칙 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

마스크가 다른 것에 가려질 때 Byte 2(소유자)를 어떻게 쓸지에 대한 version 6 규칙이다.

- Data Mask가 완전히 가려졌거나 아예 안 보이면(예: VT 독자 화면) Byte 2를 `FF`·`FE`·VT SA로 바꾼다. 가린 것이 그 마스크의 입력 수단(팝업 편집기·키보드)이면 예외다.
- <strong>일부만</strong> 가려졌다면 WS 버전에 따라 다르다. version 3 이하 WS에는 SA를 유지해 계속 갱신하게 한다. version 4 이상 WS에는 (1) "소유자 없음"으로 바꾸되 VT On User-Layout Hide/Show(Shown)를 보내 계속 갱신하게 하거나, (2) SA를 유지한다.
- Alarm Mask가 보이면 Byte 2는 그 Alarm Mask를 가진 WS의 SA다. 가린 것이 active WS의 문맥 안이면(예: Input String 입력 대화상자) 소유자는 그대로고, 문맥 밖이면(예: 화면 대부분을 오래 덮는 비디오 앱) 바꿔야 한다. 새 WS 연결을 잠깐 알리는 작은 표시는 바꾸지 않는다.

VT On User-Layout Hide/Show는 VT가 WS에게 "네 창이 지금 보인다(Shown) 또는 안 보인다(Hidden)"고 알리는 메시지다(9절).

### Working Set Maintenance 메시지

| Byte | 내용 |
|---|---|
| 1 | `0xFF`(VT function 255) |
| 2 | version 3 이상: bit 0 = Initiating(초기화 중 한 번만 1), bit 1~7 = 0. version 2 이하: `FF` |
| 3 | WS가 준수하는 버전: 3~6, `FF` = version 2 이하, 0~2·7~`FE` 예약 |
| 4~8 | `FF` |

version 6 WS라면 첫 메시지는 `FF 01 06 FF FF FF FF FF`, 이후 매초 `FF 00 06 FF FF FF FF FF`다. version 2 WS는 처음부터 끝까지 `FF FF FF FF FF FF FF FF`다.

- Initiating 비트가 두 메시지 이상에서 보이면 WS가 정상 셧다운 없이 초기화를 다시 시작했다는 뜻이고, VT는 unexpected shutdown으로 처리한다(5절 그림의 경우 2).
- 보고하는 버전은 WS(Master와 멤버)가 <strong>설계된</strong> 버전이다. 낮은 VT에 맞춰 동작을 낮춰도 바꾸지 않는다. VT는 이 값을 진단용으로 보여 줄 수 있지만, 이를 이유로 통신이나 풀을 거부하면 안 된다.
- Member는 자기 버전을 알릴 수단이 없으므로 모든 멤버가 Master가 보고한 버전을 따라야 한다. Master는 예컨대 WS 안에서 가장 낮은 장치의 버전을 보고하고, 서로의 호환성은 독점 메시지(제조사가 따로 정한 메시지)로 확인할 수 있다.

::: warning VT 구현 함정: version 2 WS의 Byte 2
version 2 WS의 Byte 2는 `FF`라서 bit 0도 1이다. Byte 3을 보지 않고 "Byte 2 bit 0 = Initiating"으로 읽으면 v2 WS가 매초 Initiating을 보내는 것으로 보이고, 두 번째 메시지부터 unexpected shutdown이 난다. Byte 3이 `FF`인지 먼저 확인한다.
:::

### Unsupported VT Function(version 5 이상)

<strong>Unsupported VT Function</strong>은 모르는 VT function을 받은 쪽이 "지원하지 않는다"고 알리는 메시지다. WS→VT와 VT→WS가 같은 형식이다. Byte 1 = `0xFD`(253), Byte 2 = 받은 메시지의 Byte 1, Byte 3~8 = `FF`. destination-specific으로 받은 메시지에만 보내고, 글로벌로 온 모르는 메시지는 조용히 무시한다. 이 메시지에는 응답이 없고 두 메시지는 서로의 응답도 아니다. 예를 들어 version 5 VT가 version 6 명령인 Screen Capture(`0xC6`)를 받으면 `FD C6 FF FF FF FF FF FF`로 답한다.

::: tip 정리
- VT Status는 소유 WS(Byte 2), 보이는 마스크(Byte 3~6), busy 비트(Byte 7), 실행 중 명령(Byte 8)을 담는다. 내용이 바뀌면 즉시, 아니면 초당 1회 보낸다.
- Working Set Maintenance는 Initiating 비트(Byte 2 bit 0)와 WS 버전(Byte 3)을 담는다. Byte 3이 `FF`면 version 2 이하이고 Byte 2를 Initiating으로 읽으면 안 된다.
:::

<small>근거: ISO 11783-6 G.2~G.5, 4.6.8</small>

## 7. 끊김 판정과 경보

이 절에서는 5절의 "3초 규칙"이 실제로 어떤 판정과 경보로 이어지는지 본다.

<strong>WS 쪽</strong>은 VT Status를 3초 동안 못 받으면 VT 셧다운으로 판정하고 <strong>안전 상태</strong>에 들어가야 한다. 안전 상태는 VT 인터페이스에 의존하는 모든 기능이 운전자와 기계를 위험에 빠뜨리지 않는 알려진 상태다. 다시 연결하도록 설계된 WS는 초기화 절차를 처음부터 다시 밟는다.

<strong>VT 쪽</strong>은 Working Set Maintenance를 3초 동안 못 받거나, Initiating 비트가 켜진 메시지를 두 번째로 받으면 WS Master의 unexpected shutdown으로 판정한다. 두 경우가 있다. WS가 Maintenance 타임아웃 안에 재부팅해 Initiating 비트를 다시 켜는 경우(풀은 아직 VT 휘발성 메모리에 있다)와, WS가 통신을 그냥 끊는 경우다. 앞의 경우를 3초를 기다리지 않고 잡아내는 장치가 Initiating 비트다(5절 그림). 판정 뒤 경보 여부는 아래 흐름으로 가린다.

![Working Set Maintenance가 끊겼을 때 VT의 판정 흐름: Delete Object Pool 뒤의 이탈, 키 off 감지, 휘발성 메모리에 풀이 없는 경우는 경보 없음, 그 밖에는 운전자 경보 후 풀 삭제·보조 입력 할당 제거·VT Status 갱신, 이후 Initiating 없는 Maintenance에는 NACK](/images/study-isobus/15-shutdown-alert-light.png)
![Working Set Maintenance가 끊겼을 때 VT의 판정 흐름: Delete Object Pool 뒤의 이탈, 키 off 감지, 휘발성 메모리에 풀이 없는 경우는 경보 없음, 그 밖에는 운전자 경보 후 풀 삭제·보조 입력 할당 제거·VT Status 갱신, 이후 Initiating 없는 Maintenance에는 NACK](/images/study-isobus/15-shutdown-alert-dark.png)

- 경보하지 않는 경우는 셋이다. WS가 Delete Object Pool로 풀을 지우게 한 뒤 Maintenance를 멈춘 경우(WS가 조용히 빠지는 정상 방법), VT가 키 상태를 알 수 있고 키가 off로 보고된 경우, 그 WS가 휘발성 메모리에 올린 풀이 없는 경우다.
- 그 밖에는 운전자에게 경보하고(방식은 VT 독자) 그 WS의 풀을 휘발성 메모리에서 지운다. 보이던 WS라면 그 WS의 모든 표시(Data Mask, Window Mask 등)가 사라지고, active Alarm Mask는 VT가 자동으로 해제한다. VT는 다른 WS나 VT 독자 화면에 제어를 넘길 수 있고 VT Status를 갱신해야 한다. 그 WS에 묶인 보조 입력 할당도 지운다.
- unexpected shutdown을 감지한 WS에서 Initiating이 없는 Maintenance가 오면 VT는 그 WS Master에게 PGN 59392(0xE800) Acknowledgement(NACK)를 보낸다. WS `0x81`이면 `01 FF FF FF 81 00 E7 00`이다. NACK가 멈추는 조건은 1절의 5단계 설명과 같다.

NACK 프레임 `01 FF FF FF 81 00 E7 00`을 바이트 단위로 읽으면 다음과 같다([10장](/study/isobus/10-j1939-request-ack)).

1. Byte 1 `01`: Control byte 1 = NACK(부정 응답)다.
2. Byte 2 `FF`: Group Function Value. 해당 없으면 `FF`이고, Maintenance의 VT function도 `0xFF`라 어느 쪽이든 `FF`다.
3. Byte 3~4 `FF FF`: 예약.
4. Byte 5 `81`: NACK 대상, 즉 원래 메시지를 보낸 CF(Control Function, 주소 하나를 갖는 기능 단위)의 SA다.
5. Byte 6~8 `00 E7 00`: 그 메시지의 PGN 59136(0xE700)을 리틀 엔디언 3바이트로 적은 것이다.

::: tip 정리
- WS는 VT Status가 3초 끊기면 안전 상태로 간다.
- VT는 Maintenance가 3초 끊기거나 Initiating을 두 번 보면 unexpected shutdown으로 판정한다. Delete Object Pool 뒤 이탈, 키 off, 올린 풀 없음이면 경보하지 않는다.
- 그 밖에는 경보하고 풀과 보조 입력 할당을 지우며, 이후 Initiating 없는 Maintenance에는 NACK로 답한다.
:::

<small>근거: ISO 11783-6 4.6.9, Figure 6, ISO 11783-3 5.4.5</small>

## 8. 키 off와 시스템 셧다운

이 절에서는 운전자가 키를 껐을 때 VT와 WS가 쓸데없는 경보 없이 정돈되게 끝내는 방법을 본다.

"System Shutdown"은 키 스위치는 off인데 ECU 전원은 아직 살아 있는 기간이다(액추에이터 전원은 살아 있을 수도, 아닐 수도 있다). 액추에이터(actuator)는 밸브나 모터처럼 실제로 움직이는 장치다. 장치마다 반응이 다르다. 즉시 통신을 끊는 장치, 정돈된 종료를 위해 전원 유지를 요청하는 장치, 키 상태를 무시하고 전원이 끊길 때까지 도는 장치가 섞여 있다. 그래서 표준은 이 부분을 권장 관행으로 적었다.

키 상태는 PGN 65096(0xFE48) Wheel-based speed and distance의 Byte 8 bit 4·3(00 = Key switch Off, 01 = not Off, 10 = 오류, 11 = 정보 없음)으로, 남은 트랙터 전원 시간은 같은 메시지 Byte 7(1분/bit, 0~250)로 읽는다. 전원 유지 요청은 PGN 65095(0xFE47) Maintain power다. 메시지 상세는 [22장](/study/isobus/22-tractor-ecu)에 있다. 이 두 메시지는 ISO 11783-7 메시지라 비트 번호를 1부터 센다.

| 주체 | 키가 "not Off → Off"로 바뀔 때 권장 동작 |
|---|---|
| VT | ① unexpected shutdown 감지를 끈다. 어떤 앱은 바로 꺼지고 다른 앱은 3초 넘게 ECU 전원을 붙잡을 수 있어, 쓸데없는 경보를 막으려는 것이다. ② 키 off 동안, 그리고 휘발성 메모리에 풀을 올린 ECU들의 마지막 "Maintain ECU Power" 요청 뒤 최소 2초간 서비스를 유지한다. ③ 키가 다시 켜지면 재초기화하고, VT Status를 멈췄었다면 표준 초기화(1절)를 밟는다 |
| WS | ① Maintain Power 메시지로 자기 상태를 알리고, 필요하면 전원 유지를 요청한다. ② "Maximum time of tractor power"를 전원 관리에 쓴다. ③ Delete Object Pool을 보내 unexpected shutdown 경보 가능성을 없앤다. ④ VT Status가 끊겨도 VT의 unexpected shutdown으로 보지 않고, 다른 VT로 연결을 시도하지도 않는다. ⑤ 키가 다시 켜지면 재초기화한다 |

version 3 이하 VT는 셧다운 동작이 규정되지 않아 VT Status를 포함한 모든 통신을 끊을 수 있다. WS ④는 다중 VT 환경에서 특히 중요하다. "다른 VT로 넘어가기" 로직(10절)을 키 상태와 묶지 않으면, 주 VT가 먼저 꺼지는 순간 WS가 아직 살아 있는 다른 VT로 풀을 옮기게 된다.

::: tip 정리
- 키 off는 Wheel-based speed and distance(PGN 65096)의 Key switch state로 안다.
- 키가 꺼지면 VT는 unexpected shutdown 감지를 끄고, WS는 Delete Object Pool로 정돈되게 빠진다. VT Status가 끊겨도 다른 VT로 옮기지 않는다.
:::

<small>근거: ISO 11783-6 4.6.7, 4.6.7.2, Annex I, ISO 11783-7 B.3, B.4, A.11, A.12</small>

## 9. active·inactive Working Set과 active mask (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절에서는 여러 WS가 한 VT를 함께 쓸 때 어느 WS가 화면과 입력을 갖는지, 그 변화를 WS가 어떻게 아는지 본다.

- 초기 풀에서 각 WS Master는 Working Set object를 <strong>정확히 하나</strong> 제공해 descriptor, active mask, 지원 언어를 정한다. descriptor는 Soft Key designator 크기 안에 들어가야 하고 밖으로 나간 부분은 잘린다. active mask는 그 WS가 보일 때 띄울 마스크다.
- <strong>active</strong> WS는 입력 포커스를 독점하고 화면에 보인다. <strong>inactive</strong> WS도 보일 수는 있지만 포커스가 없다. active는 한 번에 하나뿐이고, 고르는 수단은 VT가 운전자에게 준다.
- WS는 자기가 안 보일 때 자기 마스크를 억지로 띄울 수 없고, 다른 WS가 active일 때 자신을 active로 만들 수 없다. 예외는 active mask를 <strong>Alarm Mask</strong>로 바꾸는 경우로, 이러면 그 WS가 active가 된다. 단 현재 active WS의 active mask가 같거나 더 높은 우선순위의 Alarm Mask면 예외가 적용되지 않는다(알람 처리는 [39장](/study/isobus/39-vt-alarm-activation)).
- inactive 상태에서도 Change Active Mask로 active mask를 바꿀 수 있다. 나중에 보이게 될 때 알맞은 마스크가 뜨게 하려는 것이다.

version 4 이상 VT는 inactive WS를 함께 보여 줄 수 있다. 이때 WS는 VT Status만으로는 자기가 보이는지 알 수 없으므로 VT On User-Layout Hide/Show 메시지를 함께 본다. 전이마다 WS가 받는 신호는 다음과 같다. 전이(transition)는 한 상태에서 다른 상태로 바뀌는 것이다.

| 전이 | WS가 받는 것 |
|---|---|
| active → inactive(보임) | VT Status(소유자 변경) + Hide/Show(Shown) |
| inactive(보임) → active | Hide/Show(Hidden, 이 전이 전용의 특수한 쓰임) → VT Status(소유자 = 자신) |
| hidden ↔ active | VT Status |
| inactive(보임) ↔ hidden | Hide/Show(Hidden / Shown) |

한 WS가 active가 되면서 다른 WS가 inactive가 될 때 VT Status는 두 번이 아니라 <strong>한 번만</strong>, 새 active WS를 담아 보낸다. inactive이면서 보이는 마스크에 대해 WS가 Hidden으로 응답하면, VT는 그 WS가 이 기능을 지원하지 않는다고 보고 표시가 갱신되지 않을 수 있다고 운전자에게 알린다.

::: details VT Status·Maintenance·NACK 디코딩 검산
아래 코드는 6~9절의 해석 규칙을 함수로 옮기고, 본문의 예제 프레임으로 확인한다. `display_state`는 VT Status와 Hide/Show로 자기 표시 상태를 판정한다.

```python
BUSY = ["마스크 갱신", "NVM 저장", "명령 실행", "매크로 실행", "풀 파싱", "예약", "AUX learn", "메모리 부족"]


def parse_vt_status(f: bytes, vt_sa: int):
    assert f[0] == 0xFE
    return {
        "owner": None if f[1] in (0xFF, 0xFE, vt_sa) else f[1],
        "mask": int.from_bytes(f[2:4], "little"),
        "soft_key_mask": int.from_bytes(f[4:6], "little"),
        "busy": [n for i, n in enumerate(BUSY) if f[6] >> i & 1],
        "running": f[7] if f[6] & 0b0000_1100 else None,   # bit 2·3일 때만 유효
    }


def parse_wsm(f: bytes):
    assert f[0] == 0xFF
    version = 2 if f[2] == 0xFF else f[2]
    return version, version >= 3 and bool(f[1] & 0x01)


def display_state(vt_status: bytes, my_sa: int, shown_by_hide_show: bool) -> str:
    if vt_status[1] == my_sa:
        return "active"
    return "inactive+visible" if shown_by_hide_show else "hidden"


s = parse_vt_status(bytes.fromhex("FE 81 05 00 10 00 04 A8"), vt_sa=0x26)
assert s == {"owner": 0x81, "mask": 5, "soft_key_mask": 16, "busy": ["명령 실행"], "running": 0xA8}
s = parse_vt_status(bytes.fromhex("FE 26 FF FF FF FF 40 FF"), vt_sa=0x26)
assert s["owner"] is None and s["busy"] == ["AUX learn"] and s["running"] is None
s = parse_vt_status(bytes.fromhex("FE FE FF FF FF FF 80 FF"), vt_sa=0x26)
assert s["owner"] is None and s["busy"] == ["메모리 부족"]

assert parse_wsm(bytes.fromhex("FF 01 06 FF FF FF FF FF")) == (6, True)
assert parse_wsm(bytes.fromhex("FF 00 06 FF FF FF FF FF")) == (6, False)
assert parse_wsm(bytes.fromhex("FF FF FF FF FF FF FF FF")) == (2, False)   # bit 0이 1이어도 Initiating 아님

assert display_state(bytes.fromhex("FE 81 01 00 FF FF 00 FF"), 0x81, False) == "active"
assert display_state(bytes.fromhex("FE 90 07 00 FF FF 00 FF"), 0x81, True) == "inactive+visible"

nack = bytes([0x01, 0xFF, 0xFF, 0xFF, 0x81]) + (59136).to_bytes(3, "little")
assert nack.hex(" ").upper() == "01 FF FF FF 81 00 E7 00"
print("상태 메시지 검증 통과")
```
실행하면 `상태 메시지 검증 통과`가 출력된다. `parse_wsm`이 Byte 3을 먼저 보고 `FF`면 버전 2로 읽기 때문에, version 2 WS의 Byte 2 `FF`를 Initiating으로 잘못 읽지 않는다.
:::

<small>근거: ISO 11783-6 4.6.8, Table 2, Table 3, G.2</small>

## 10. 다중 VT: VT Number와 VT 옮기기

이 절에서는 네트워크에 VT가 둘 이상일 때 운전자와 WS가 VT를 구분하고 고르는 방법을 본다.

### VT Number와 primary VT

- VT는 공장 출하 때 Function Instance 0이고, 운전자가 바꾼 값은 유지한다. Function Instance는 같은 기능을 하는 장치 가운데 몇 번째인지 나타내는 NAME 안의 번호다([12장](/study/isobus/12-j1939-address-name)).
- 같은 instance의 VT가 둘 이상이거나 instance 0인 VT가 없는 충돌을 풀려고, VT는 디스플레이에서 instance를 바꾸는 독자 수단을 제공해야 한다. 이 수단은 VT끼리 instance가 겹치지 않게 보장해야 하고, 새 instance는 VT를 재초기화한 뒤에만 쓴다.
- instance 0인 VT가 <strong>primary VT</strong>다.
- 운전자에게는 instance가 아니라 <strong>VT Number</strong>로 보인다. VT Number = Function Instance + 1이고 범위는 1~32(instance 0~31)다. +1은 0부터 세는 데 익숙지 않은 운전자를 위한 것이다. 제조사가 달라도 번호 체계가 같아야 운전자가 primary·secondary VT를 일관되게 고른다.

<strong>Identify VT(`0xBB`, version 4 이상)</strong>는 `BB FF FF FF FF FF FF FF`다. 받은 VT는 Alarm Mask가 active가 아닐 때만 VT Number를 3초 동안 표시한다. 글로벌 전송을 의도한 메시지라 한 번에 모든 VT가 번호를 띄우고, destination-specific으로 받았을 때만 같은 모양의 응답(`BB FF FF FF FF FF FF FF`)을 보낸다. 매크로에서는 쓸 수 없다.

### WS가 VT를 고르고 옮기는 법

네트워크에 VT가 둘 이상이면 WS Master는 "다른 VT로 옮기기"(Move to another VT) 기능을 가져야 한다. 예를 들어 "Next VT" Soft Key나 Button을 Identify VT와 함께 쓴다. 이 기능은 VT를 둘 이상 감지했을 때만 켜지고, 누르면 다음 순서를 밟는다.

1. 안전 상태로 들어간다. 또는 안전 상태가 아닐 때는 이 기능이 켜지지 않게 막는다.
2. 지금 VT에 Delete Object Pool(`B2 FF FF FF FF FF FF FF`)을 보내고 응답(Byte 2 Error Codes = 0이면 삭제 성공)을 기다린다.
3. 그 VT로 Working Set Maintenance를 멈춘다.
4. 다른 VT와 초기화를 시작한다.
5. 새 VT를 다음 전원 사이클의 <strong>선호 VT</strong>로 저장한다.

2·3단계의 순서가 7절의 "경보하지 않는 경우"와 맞물린다. 풀을 지운 뒤 Maintenance를 멈추면 이전 VT는 unexpected shutdown 경보를 띄우지 않는다.

다음 전원 사이클에는 선호 VT를 먼저 기다리고, 일정 시간 안에 나타나지 않으면 다른 VT와 연결해도 된다. 기다릴 시간은 운전자가 정하게 하거나 선호 VT의 Get Hardware response Byte 2(boot time, [30장](/study/isobus/30-vt-display-technical-data) 8절)에서 얻는다. 그 VT가 아직 켜지지 않은 시점이므로 이전 연결 때 받아 둔 값을 쓰게 된다(추론). VT 후보의 instance는 address claim으로 받은 NAME의 Byte 5 bit 8~4에서 읽는다([30장](/study/isobus/30-vt-display-technical-data) 5절). 보조 입력 오브젝트는 Function Instance 0 VT에, 나머지 풀은 다른 VT에 게시하는 식으로 VT를 나눠 쓰는 구성도 가능하다.

::: tip 정리
- 운전자는 VT Number(= Function Instance + 1)로 VT를 고르고, Identify VT(`0xBB`)를 보내면 모든 VT가 번호를 3초간 띄운다.
- VT를 옮길 때는 안전 상태 → Delete Object Pool → Maintenance 중단 → 새 VT 초기화 → 선호 VT 저장 순서다.
:::

<small>근거: ISO 11783-6 4.6.5, 4.6.6.3, 4.6.25, D.18</small>

## 11. 독점 수단과 패킷 패딩 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절에서는 제조사끼리만 통하는 독점 수단을 쓸 때의 규칙과, 8바이트보다 짧은 VT 메시지를 `FF`로 채우는 규칙을 본다.

### 독점 수단

독점 수단(proprietary means)은 표준이 아니라 제조사가 따로 정한 오브젝트, 이벤트, 색, 명령, 폰트를 말한다. VT는 독점 오브젝트(타입 240~254), 독점 이벤트(240~254), 독점 색(232~255), 독점 명령(VT function 96~127, `0x60`~`0x7F`), 독점 폰트를 지원할 수 있다.

- WS와 VT의 제조사가 다르면 쓰지 말라고 권한다. 독점 항목은 제조사가 공지 없이 바꿀 수 있다. 제조사 코드는 NAME에 있으므로, VT NAME의 Manufacturer code가 자기와 같을 때만 독점 명령을 쓰게 구현할 수 있다.
- 정의를 모르는 독점 오브젝트는 파싱할 수 없어 VT가 풀 전체를 거부할 수 있다.
- 낮은 버전 VT·WS가 높은 버전에서 표준화된 기능을 주고받는 것은 표준 위반이 아니다(예: version 2 VT가 version 4에서 표준화된 Font type 5 Cyrillic 지원). 하지만 낮은 버전 입장에서는 정의가 없으므로 <strong>독점 수단으로 본다</strong>. 상대가 지원하는지는 독점 수단으로 확인해야 하고, 지원한다고 가정하면 안 된다.
- VT는 풀에 지원하지 않는 기능이 있으면 풀을 거부해야 하고(shall), 표시와 메시지 동작을 모두 완전히 지원할 때만 받아들일 수 있다.

### 패킷 패딩

패딩(padding)은 빈자리를 정해진 값으로 채우는 것이다. 정확히 8데이터 바이트로 정의되지 않은 VT↔ECU 메시지는 모두 `FF`로 8바이트 경계까지 채워야 한다.

- 짧은 가변 길이 메시지는 8바이트까지 `FF`로 채운다. 라벨이 없는 Get Versions response `E0 00 FF FF FF FF FF FF`가 그 모양이다. Get Versions response의 정의도 이 채움을 따로 적어 둔다.
- 8바이트를 넘어 TP로 가는 메시지는 마지막 TP.DT 패킷의 빈 바이트를 `FF`로 채운다. TP.DT는 TP에서 실제 데이터를 7바이트씩 나르는 패킷이다([15장](/study/isobus/15-tp-bam-cmdt)). TP 메시지 크기 자체를 8의 배수로 늘릴 필요는 없다. 오브젝트 풀 전송 절차의 규칙도 같은 내용을 "계산한 데이터 길이가 8바이트 미만인 메시지를 8바이트까지 `FF`로 채운다"로 적기 때문이다.
- 패딩 `FF`는 파서와도 맞물린다. Get Supported Objects는 `FF`를 목록 끝으로 읽으므로 패딩이 곧 종결자다([30장](/study/isobus/30-vt-display-technical-data) 8절). 수신 측은 프레임 길이가 아니라 메시지 안의 길이 필드(바이트 수, 라벨 수, 범위 수)로 내용을 자른다.
- VT↔ECU PGN이 아닌 메시지는 이 규칙의 대상이 아니다. 예를 들어 Request(PGN 59904)는 ISO 11783-3(데이터 링크 계층을 정하는 문서)이 DLC를 3으로 정한다([30장](/study/isobus/30-vt-display-technical-data) 6절).

::: tip 정리
- 독점 수단은 같은 제조사끼리만 쓰고, 상대가 지원하는지는 가정하지 말고 확인한다.
- 짧은 VT 메시지는 `FF`로 8바이트를 채운다. TP 메시지는 마지막 패킷의 빈 바이트만 `FF`로 채운다.
:::

<small>근거: ISO 11783-6 4.6.24, 4.6.26, Annex A, Table A.5, C.1, E.3, ISO 11783-3 5.10.5</small>

::: tip 핵심 정리
- 작업기는 VT Status를 본 뒤에야 통신을 시작하고, 자신을 알리고 Maintenance를 시작한 다음, VT 능력을 묻고 풀을 Load하거나 전체 업로드한다.
- VT는 풀을 버전 라벨과 함께 비휘발성 메모리에 저장해 두고, 다음 연결 때 Load Version 하나로 복원할 수 있다.
- VT Status와 Working Set Maintenance가 각자 1초마다 생존을 알린다. 3초 끊기면 상대가 꺼진 것으로 보고, VT는 Initiating을 두 번 보면 바로 unexpected shutdown으로 판정한다.
- 경보는 Delete Object Pool 뒤 이탈, 키 off, 올린 풀 없음일 때는 띄우지 않는다. 키 off 때 WS는 Delete Object Pool로 정돈되게 빠진다.
- 운전자는 VT Number(= Function Instance + 1)로 VT를 고르고, VT를 옮길 때는 안전 상태 → Delete Object Pool → Maintenance 중단 → 새 VT 초기화 → 선호 VT 저장 순서를 밟는다.
- 독점 수단은 같은 제조사끼리만 쓰고, 짧은 VT 메시지는 `FF`로 8바이트를 채운다.
:::

::: details 확인 문제
1. 작업기가 VT Status를 받기 전에 Get Memory를 보내도 되는가? 초기화 순서로 설명하라.
2. 작업기가 지난 전원 사이클에 저장해 둔 풀로 빨리 붙으려 한다. 어떤 메시지들을 어떤 순서로 보내는가?
3. VT가 Working Set Maintenance를 3초 동안 받지 못했다. VT가 운전자에게 경보하지 않아도 되는 경우 세 가지를 들어라.
4. (디코딩) `FE 81 05 00 10 00 04 A8`에서 VT를 소유한 WS, 보이는 Data Mask, busy 상태, 실행 중인 명령을 읽어라.
5. (진단) VT 에뮬레이터 로그에 Working Set Maintenance `FF FF FF FF FF FF FF FF`가 매초 들어오는데, VT가 두 번째 메시지부터 unexpected shutdown 경보를 띄운다. 무엇이 잘못됐고 어떻게 고치는가?
6. (디코딩·진단) 저장된 풀로 붙는 WS가 Load Version을 보냈다. 그 뒤 `FE FF FF FF FF FF 00 FF`가 세 번 연속 왔는데 응답이 없다. WS는 무엇을 해야 하고, 이 프레임의 Byte 8은 판단에 쓸 수 있는가?

**답 가이드**
1. 안 된다. 3단계에서 VT Status가 오기 전에는 VT와 데이터 통신을 시작하면 안 된다. 순서는 주소 클레임 → VT Status 대기 → Working Set Master로 자신 알리기 → Maintenance 시작(첫 메시지만 Initiating) → 기술 데이터 질의(Get Memory 등)다.
2. Working Set Master → Working Set Maintenance(Initiating = 1) → Get Memory(버전 확인, Memory Required = 0으로 보내도 된다)와 필요한 기술 데이터 → Get Versions로 저장된 라벨 확인 → 맞는 라벨이 있으면 Load Version을 보내고 응답을 기다린다. 응답이 성공이면 End of Object Pool 없이 연결 완료로 진행한다.
3. WS가 Delete Object Pool로 풀을 지우게 한 뒤 Maintenance를 멈춘 경우, VT가 키 상태를 알 수 있고 키가 off로 보고된 경우, 그 WS가 휘발성 메모리에 올린 풀이 없는 경우다.
4. Byte 2 `81`이므로 `0x81` WS가 소유한다. Byte 3~4 `05 00`은 Data Mask 5, Byte 5~6 `10 00`은 Soft Key Mask 16이다. Byte 7 `04`는 bit 2 = 명령 실행 중이고, 그래서 Byte 8 `A8`이 유효하다. 실행 중인 명령은 `0xA8` Change Numeric Value다.
5. Byte 3이 `FF`이면 version 2 이하 WS이고, 이때 Byte 2(`FF`)는 Initiating 비트마스크가 아니다. 에뮬레이터가 Byte 3을 보지 않고 bit 0을 Initiating으로 읽어 "Initiating 재수신 = unexpected shutdown"으로 판정한 것이다. Byte 3이 `FF`면 Initiating 판정을 하지 않게 고친다(6절).
6. parsing 비트(Byte 7 bit 4)가 0인 VT Status가 세 번 연속 왔으므로 Load 명령이 VT에 닿지 않은 것으로 본다. Load를 다시 보내거나, 9단계를 전체 업로드(오브젝트 풀 전송)로 끝낸다(1절 상태 흐름). Byte 8은 bit 2(명령)나 bit 3(매크로)이 1일 때만 유효한데 이 프레임은 Byte 7이 0이므로 쓸 수 없다.
:::

## 다음 챕터

- 다음: [32장 VT 오브젝트 풀 기초](/study/isobus/32-vt-object-pool-basics)
