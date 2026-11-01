---
title: "태스크와 시간 기록"
description: "TC가 다루는 작업 단위인 태스크의 상태와 기록 규칙, 다른 메시지 값 로깅, 언어·단위 설정, 작업 시간을 나눠 기록하는 방법을 익힌다."
date: 2026-04-13
tags: [ISOBUS, ISO11783, TaskController, TC, Task, TaskStatus, TimeLog, ISOXML]
prev: /study/isobus/41-tc-basics
next: /study/isobus/43-tc-connection
---

# 태스크와 시간 기록

::: info 학습 목표
- 태스크가 무엇이고 FMIS와 TC 사이를 어떻게 오가는지 설명할 수 있다.
- 표준이 정한 경계 두 곳(XML 파일 세트, 버스 메시지)과 제품마다 달라도 되는 부분을 구분할 수 있다.
- 태스크 상태 6가지와 상태가 바뀌는 길을 그림으로 따라갈 수 있다.
- "기록은 덧붙이기만 한다"는 원칙이 시간 기록과 자원 할당에 어떻게 적용되는지 말할 수 있다.
- Time 유형 코드와 Minimal·Intermediate 기록 수준의 차이를 예를 들어 설명할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [41장 TC 기초](/study/isobus/41-tc-basics), [12장 주소와 NAME](/study/isobus/12-j1939-address-name)
- 이 장에서 처음 나오는 말
  - 태스크(task): 한 밭에서 하는 작업 하나를 계획하고 기록하는 단위
  - MICS(Mobile Implement Control System): 트랙터와 작업기 쪽 시스템 전체. TC가 그 안에 있다
  - partfield: 작물 하나만 기르는 땅 구획. 태스크가 붙는 가장 작은 단위
  - coding data: 기계·작업자·약제 목록처럼 자주 바뀌지 않는 기준 데이터
  - Time 요소: 태스크 파일에 시간 구간 하나를 적는 XML 요소
  - TimeLog: 값을 시간 순서대로 많이 기록하는 파일
:::

[41장](/study/isobus/41-tc-basics)에서 TC를 작업 지시서를 받아 기계에 일을 시키는 현장 감독에 비유했다. 이 장은 그 작업 지시서와 작업 일지를 들여다본다. 작업 지시서 한 장이 태스크이고, 일지에는 언제 무슨 일이 있었는지를 덧붙여 적을 뿐 지난 기록을 고쳐 쓰지 않는다. 태스크가 어떤 상태를 거치는지, 시간과 위치를 어떻게 기록하는지, 작업 시간을 어떤 종류로 나누는지 차례로 본다.

## 1. 태스크: TC가 다루는 작업 단위

앞 장까지는 TC가 작업기를 어떻게 제어하고 연결을 유지하는지 봤다. 이 절은 TC가 실제로 관리하는 단위인 <strong>태스크(task)</strong>를 본다. Part 10(ISO 11783-10, TC를 정하는 표준 문서)은 태스크를 "한 고객(customer)의 한 partfield에서 농민이나 계약자가 계획했거나, 실행 중이거나, 이미 끝낸 작업"을 서로 구분하는 단위로 쓴다. FMIS 쪽에서 보면 태스크는 작업을 <strong>무엇을, 어디서, 어떻게, 누가, 언제</strong> 할지 정한 계획서다.

예를 들어 "김 농장(고객)의 북쪽 밀밭(partfield)에 6월 3일 질소 비료를 처방 맵대로 뿌린다"가 태스크 하나다. 같은 밭이라도 비료 살포와 수확은 서로 다른 태스크다.

처음 나오는 용어 세 가지를 먼저 정리한다.

- partfield: 작물 하나만 재배하는 땅 구획이다. 태스크가 할당되는 가장 작은 XML 요소이기도 하다.
- MICS(mobile implement control system): 트랙터·작업기 쪽 시스템 전체다. TC는 MICS 안에 있다.
- coding data: 기계·약제 데이터처럼 자주 바뀌지 않거나, 태스크를 행정적으로 할당하려고 참조하는 데이터다.

### 태스크 관리의 두 목적

| 목적 | 관리 대상 | 주로 오가는 데이터 |
|---|---|---|
| 농장 자원 관리 | 트랙터·작업기·센서 시스템·작업자·자재 | 자원 지정자(resource designator): coding data로 전송 |
| 농장 활동 관리 | 밭에서 하는 작업 | 태스크(task data) |

자원 지정자는 "트랙터 2호", "작업자 박 씨", "질소 비료 A"처럼 자원에 붙인 이름표다. 태스크는 이 이름표를 가리켜 "누가, 무엇으로" 일했는지 적는다.

### 데이터가 오가는 방향

데이터는 양방향으로 흐른다. 계획된 태스크는 FMIS에서 MICS의 TC로 내려가고, 작업 결과는 TC에서 FMIS로 올라간다. 태스크는 FMIS와 MICS 어느 쪽에서도 만들 수 있다.

FMIS가 무엇을 내려보내는지는 농장의 관리 방식이 정한다.

| 운용 방식 | FMIS → MICS | MICS → FMIS |
|---|---|---|
| 작업 일지만 남기는 농장 | coding data만 보낸다. 태스크는 MICS에서 자원을 골라 만든다 | 태스크가 담긴 파일 세트(태스크는 이 방향에만 있다) |
| FMIS에서 계획하는 농장 | coding data + 계획 태스크. 계획 태스크는 자원 할당만 있는 것부터 site-specific 작업용 지리 정보까지 다양하다 | 실행 결과가 반영된 파일 세트 |

- 첫 번째 농장은 사무실에서 계획하지 않는다. 운전자가 트랙터 단말기에서 "트랙터 2호로 북쪽 밭 살포"를 골라 태스크를 그 자리에서 만들고, 끝나면 기록만 사무실로 가져간다.
- 두 번째 농장은 사무실에서 태스크를 미리 만들어 내려보낸다. site-specific은 "위치마다 다르게"라는 뜻이고, 처방 맵이 들어간 태스크가 그 예다.

<small>근거: ISO 11783-10 3.2, 3.12, 5.1, 5.2</small>

## 2. 태스크가 오가는 길과 표준의 경계

태스크가 FMIS에서 작업기까지 갔다가 돌아오는 길에는 여러 단계가 있다. 그중 표준이 정한 곳과 제품마다 달라도 되는 곳을 가려 두면, 장비를 고르거나 만들 때 무엇을 꼭 맞춰야 하는지 알 수 있다.

![태스크가 오가는 길: FMIS, XML 파일 세트, 드라이버·전달 수단(USB 메모리, 무선 등), TC, 작업기 ECU가 차례로 이어진다. 표준이 정한 곳은 XML 파일 세트의 형식과 TC와 작업기 사이의 버스 통신 두 곳이고, FMIS 내부와 드라이버는 표준 밖이다. 계획 태스크는 FMIS에서 작업기 쪽으로, 작업 결과는 반대로 흐른다](/images/study-isobus/42-task-flow-boundary-light.png)
![태스크가 오가는 길: FMIS, XML 파일 세트, 드라이버·전달 수단(USB 메모리, 무선 등), TC, 작업기 ECU가 차례로 이어진다. 표준이 정한 곳은 XML 파일 세트의 형식과 TC와 작업기 사이의 버스 통신 두 곳이고, FMIS 내부와 드라이버는 표준 밖이다. 계획 태스크는 FMIS에서 작업기 쪽으로, 작업 결과는 반대로 흐른다](/images/study-isobus/42-task-flow-boundary-dark.png)

[41장 2절](/study/isobus/41-tc-basics)의 흐름을 ISO 11783-10은 여덟 단계(a~h)로 나눠 설명한다. 표의 "표준 범위" 열이 그 단계를 표준이 정하는지 보여 준다.

| 단계 | 하는 일 | 주체 | 표준 범위 |
|---|---|---|---|
| a | 필드 태스크 계획, coding data 관리 | FMIS | 표준 밖(FMIS 소프트웨어) |
| b | 태스크 데이터를 XML로 변환 | FMIS | <strong>XML 형식은 표준</strong>([56장](/study/isobus/56-practice-isoxml)) |
| c | (선택) 계획 태스크를 작업기·센서가 쓸 데이터에 할당 | 명시 없음 | - |
| d | FMIS에서 MICS의 TC로 전송 | TC 인터페이스 드라이버·데이터 캐리어 | <strong>표준 밖</strong> |
| e | 태스크 데이터로 작업기 ECU에 process data 메시지 송신 | TC | <strong>네트워크 통신은 표준</strong>([43장](/study/isobus/43-tc-connection), [45장](/study/isobus/45-tc-process-data-basics)) |
| f | 태스크의 DataLogTrigger에 따라 데이터 수집 | TC | 표준 |
| g | 수집 데이터를 FMIS로 전송. proprietary 형식이면 XML로 변환 | 명시 없음 | 형식만 표준 |
| h | XML을 읽어 FMIS 형식으로 저장·평가 | FMIS | 표준 밖 |

- 데이터 캐리어는 파일을 옮기는 매체(USB 메모리, 메모리 카드 등)다.
- process data 메시지는 TC와 작업기가 값을 주고받는 버스 메시지다([45장](/study/isobus/45-tc-process-data-basics)).
- DataLogTrigger는 "이 값을 이런 조건에서 기록하라"는 기록 조건이다.
- proprietary 형식은 제조사가 마음대로 정한 자체 형식이다. TC가 내부에서는 자체 형식으로 모아도 되지만, FMIS로 넘길 때는 표준 XML로 바꿔야 한다.

표준이 정한 경계는 두 곳이다. ① XML 데이터 전송 파일 세트, ② ISO 11783 네트워크 위의 TC와 CF 사이 통신이다. 위 그림의 초록 테두리 상자와 진한 화살표가 이 두 곳이다. 드라이버가 파일을 TC로 옮기는 방식(메모리 카드, 무선 링크 등)과 파일 내용을 네트워크 메시지로 바꾸는 절차는 표준화 대상이 아니다. 드라이버는 제조사가 제공한 device descriptor 데이터를 덧붙여 작업기별 setpoint 데이터를 만들 수도 있다.

택배에 비유하면 표준은 상자 규격(파일 형식)과 받는 사람과의 인수인계 방식(버스 통신)만 정하고, 트럭으로 옮기든 오토바이로 옮기든(드라이버)은 정하지 않는 셈이다.

::: tip 에뮬레이터를 만든다면
TC 서버를 에뮬레이션해 클라이언트를 검증할 때도 맞춰야 할 표준 인터페이스는 이 두 곳이다. 파일 세트를 TC에 어떻게 넣느냐(USB, 클라우드 동기화 등)는 제품마다 달라도 된다(추론). 파일 세트의 구조는 [56장 ISOXML 태스크 파일](/study/isobus/56-practice-isoxml)에서, 네트워크 메시지는 [43장](/study/isobus/43-tc-connection)과 [45장 TC 프로세스 데이터 기초](/study/isobus/45-tc-process-data-basics)에서 다룬다.
:::

<small>근거: ISO 11783-10 5.1(Figure 1), 5.4</small>

## 3. 장치 미리 고르기: NAME과 마스크

계획 단계에서 "이 태스크는 어떤 장치로 할지"를 정해 두면 현장에서 고를 일이 줄어든다. 이 절은 FMIS가 장치를 어떻게 가리키는지 본다.

FMIS는 계획 단계에서 "어떤 장치로 일할지"를 정할 수 있어야 한다. 그런데 이동 시스템의 클라이언트 장치를 유일하게 가리키는 수단은 <strong>CF NAME</strong>(Part 5의 8바이트 이름)뿐이다. Part 5는 주소 클레임과 NAME을 정하는 표준 문서(ISO 11783-5)다. 그래서 FMIS 관점에서 NAME은 전 세계에서 유일해야 하고, Identity Number와 NAME의 나머지 필드 조합이 유일하도록 보장할 책임은 장치 제조사에 있다. NAME 필드 구성은 [12장 주소와 NAME](/study/isobus/12-j1939-address-name)에서 다룬다.

주소(SA)는 전원을 켤 때마다 바뀔 수 있어서 장치를 가리키는 데 쓸 수 없다. 반면 NAME은 제조사 코드, 기능, 일련번호(Identity Number) 등을 묶은 고정된 이름이라 주민등록번호처럼 장치를 하나로 가리킨다.

- DeviceAllocation 요소가 계획된 장치 할당을 담는다. 지정 수준은 특정 장치 하나부터 "이런 종류의 장치"처럼 느슨한 것까지 고를 수 있다.
- ClientNAMEValue는 8바이트 NAME이고, ClientNAMEMask는 그중 장치 선택에 쓸 비트를 고르는 마스크다. 마스크 비트 1은 "이 비트가 유효", 0은 "무시"다. 즉 후보 NAME과 ClientNAMEValue를 각각 마스크와 AND해 결과가 같으면 후보가 조건을 만족한다.
- 실제로 쓴 장치는 DeviceIdRef 속성에 기록한다. FMIS가 넣은 사전 선택 정보는 MICS가 덮어쓰지 않는다.

마스크 비교를 바이트 하나로 줄여서 따라가 보자. AND는 두 비트가 모두 1일 때만 1이 되는 연산이라, 마스크의 0 자리는 무조건 0이 되어 비교에서 빠진다.

1. ClientNAMEValue의 어떤 바이트가 `0x88`, 마스크의 같은 바이트가 `0xF0`(위쪽 4비트만 1)이다. `0x88 AND 0xF0 = 0x80`이다.
2. 후보 장치 NAME의 그 바이트가 `0x8B`면 `0x8B AND 0xF0 = 0x80`이다. 결과가 같으니 이 바이트는 조건을 만족한다.
3. 후보가 `0x9B`면 `0x9B AND 0xF0 = 0x90`이다. 결과가 다르니 탈락이다.

8바이트 모두에서 이렇게 비교해 전부 같아야 그 장치가 계획에 맞는 장치다. 마스크가 전부 `FF`면 특정 장치 하나만, 일부 필드만 1이면 "이 제조사의 이런 종류 장치면 아무거나"처럼 넓게 고르게 된다.

<small>근거: ISO 11783-10 5.3, D.20</small>

## 4. TC 사용자 인터페이스

태스크를 고르고 시작하고 멈추는 일은 오퍼레이터(트랙터를 운전하며 단말기를 조작하는 사람)가 한다. 표준은 그 화면을 어디까지 정할까?

TC는 VT나 다른 인터페이스로 오퍼레이터와 상호작용할 수 있다. 태스크 하나를 자동으로 돌리는 단순한 TC는 UI가 없어도 되고, 고급 TC는 태스크 목록 선택, start/stop/resume/complete, 태스크 수정·생성, coding data 추가 같은 기능을 제공한다. 표준이 강제하는 것은 "태스크 <strong>실행</strong> 메커니즘은 반드시 있어야 한다(shall)"는 것뿐이고, 선택 메커니즘은 있어도 되는(can) 기능이다. 선택·시작·정지 방법 자체는 TC 설계자에게 맡긴다.

- VT(Virtual Terminal)는 트랙터 안의 공용 화면이다([29장](/study/isobus/29-vt-basics)).
- 표준 문서에서 shall은 "반드시 해야 한다", can은 "해도 된다"는 뜻이다. 그래서 같은 TC라도 제품마다 화면과 조작 방법이 크게 다를 수 있다.

<small>근거: ISO 11783-10 5.5, 6.1</small>

## 5. 태스크 상태와 전이

TC가 태스크를 시작하고 멈추고 끝낼 때마다 태스크의 상태가 바뀐다. 상태가 바뀌면 버스 메시지와 파일 양쪽에 흔적이 남으므로, 상태를 알아야 두 곳의 기록을 읽을 수 있다.

작업 지시서에 "계획", "진행 중", "보류", "완료" 도장을 찍는다고 생각하면 쉽다. 여기에 복사해서 쓰는 견본 양식(Template)과 "이 지시서는 거둬들인다"는 취소 도장(Canceled)이 더해진다.

태스크 상태는 ISO 11783-10이 6가지로 정의하고, 파일에서는 Task 요소의 TaskStatus 속성 값(1~6)으로 기록한다.

![태스크 상태 전이: Planned(1)를 시작하면 Running(2)이 되고, Running과 Paused(3)는 일시정지·재개로 오가며, 둘 다 오퍼레이터만 Completed(4)로 보낼 수 있다. Template(5)은 시작하면 복사본이 새 태스크로 실행되고, Canceled(6)는 FMIS와 MICS 사이의 철회 신호다](/images/study-isobus/18-task-state-machine-light.png)
![태스크 상태 전이: Planned(1)를 시작하면 Running(2)이 되고, Running과 Paused(3)는 일시정지·재개로 오가며, 둘 다 오퍼레이터만 Completed(4)로 보낼 수 있다. Template(5)은 시작하면 복사본이 새 태스크로 실행되고, Canceled(6)는 FMIS와 MICS 사이의 철회 신호다](/images/study-isobus/18-task-state-machine-dark.png)

그림은 가운데 줄부터 읽는다. Planned(1)를 시작하면 Running(2)이 되고, Running과 Paused(3)는 일시정지와 재개로 오간다. 일을 끝내면 Completed(4)로 간다. 위쪽 Template(5)과 아래쪽 Canceled(6)는 버전 4에서 생긴 특별한 상태다. 표의 "도입" 열에 v4라고 적힌 것이 버전 4에서 새로 생겼다는 뜻이다.

| 상태 | 값 | 의미와 규칙 | 도입 |
|---|---|---|---|
| Planned | 1 | FMIS나 MICS에서 준비했지만 MICS에서 아직 처리하지 않은 태스크 | |
| Running | 2 | MICS에서 처리 중. <strong>TC 하나에 동시에 하나만</strong> active일 수 있다 | |
| Paused | 3 | 실행됐다가 멈췄고 아직 완료되지 않았다. TC 입장에서는 이것이 최종 상태일 수 있다. MICS에서 만든 파일 세트에 이 상태로 실린 태스크는 FMIS가 처리해야 한다 | |
| Completed | 4 | 끝난 태스크. <strong>오퍼레이터만</strong> 설정할 수 있고 MICS가 자동으로 설정하지 못한다. 지원은 선택이라 이 상태가 없는 TC도 있다. MICS에서 온 이 상태의 태스크도 FMIS가 처리해야 한다 | |
| Template | 5 | 시작하면 복사본을 만들어 그 복사본을 새 태스크로 시작한다. FMIS가 정의한 템플릿은 MICS가 고칠 수 없다. MICS가 만든 템플릿은 파일 세트에 새 태스크로 표시하고, 한 번 일반 태스크로 실체화된 뒤에는 고칠 수 없다 | v4 |
| Canceled | 6 | 태스크를 거둬들이기 위한 상태. FMIS나 MICS가 상대에게 "이 태스크를 철회하라"고 알릴 때 쓴다 | v4 |

- Paused가 "최종 상태일 수 있다"는 말은, 예를 들어 Completed를 지원하지 않는 TC에서는 일을 다 끝낸 태스크도 Paused로 남는다는 뜻으로 읽힌다(추론).
- Template은 같은 작업을 자주 되풀이하는 농장에 쓸모가 있다. 견본을 시작할 때마다 새 태스크가 하나씩 생긴다.

표준은 상태 사이를 오가는 그림을 따로 싣지 않는다. 위 그림은 상태 정의, TC 조작 목록(start/stop/resume/complete), "시작·재개할 때 effective Time 요소를 추가한다"는 기록 규칙을 엮어 이 스터디가 그린 것이다. 특히 Canceled로 들어가는 출발 상태는 표준이 제한하지 않는다. 그림은 가장 흔한 경우인 "아직 실행하지 않은 Planned 태스크의 철회"만 그렸다.

### 상태가 바뀌면 남는 흔적

상태 전이는 버스와 파일에 각각 흔적을 남긴다.

- 버스: TC Status 메시지 Byte 5 bit 1(Task totals active)은 "태스크가 시작되거나 재개돼 total이 누적될 수 있다"는 뜻이다. 이 비트가 0 → 1이 되면 클라이언트는 내부 task total을 0으로 리셋하고 세기 시작하며, 1 → 0이 되면 세기를 멈춘다. 멈춘 값은 TC가 Request Value로 읽어 갈 수 있다. 수거·복원 규칙은 [47장 Totals, 로깅, Peer Control](/study/isobus/47-tc-totals-logging-peer)에서 다룬다.
- 파일: Time 요소는 <strong>태스크 상태가 바뀔 때, 자원 할당이 바뀔 때, TC가 기동·종료할 때만</strong> Task에 추가하고, 이미 기록한 Time은 고치지 않는다. MICS가 태스크를 시작했고 네트워크에 시간 정보가 있으면 Time 요소가 적어도 하나는 있어야 한다.

첫 항목의 "Byte 5 bit 1"은 TC Status 메시지 8바이트 중 다섯 번째 바이트의 가장 낮은 비트를 말한다. 이 비트는 태스크가 돌고 있는지(Running)를 작업기에 알리는 스위치와 같다. 작업기는 이 스위치가 켜지는 순간 "이번 작업" 합계를 0부터 다시 세고, 꺼지면 세기를 멈춘다. 메시지 전체 구성은 [43장](/study/isobus/43-tc-connection)에서 본다. Request Value는 TC가 작업기에 "이 값을 알려 달라"고 묻는 명령이다.

::: warning 상태 머신 구현 함정
- Completed를 "작업기 섹션이 모두 꺼졌다" 같은 조건으로 자동 설정하면 안 된다. 오퍼레이터만 설정할 수 있는 상태다.
- 새 태스크를 Running으로 올리기 전에 기존 Running 태스크를 내려야 한다. TC 하나에 active 태스크는 하나뿐이다.
- Template 태스크 자체를 Running으로 바꾸면 안 된다. 복사본을 만들어 그 복사본을 시작한다.
- FMIS는 MICS에서 온 Paused 태스크도 처리해야 한다. FMIS 쪽 구현이 Completed만 집계하면 Paused로 끝난 작업 기록이 빠진다(추론).
:::

<small>근거: ISO 11783-10 5.5, 6.1(Table 1), 6.2, B.8.1, D.46</small>

## 6. 시간·위치·이벤트 기록 규칙

작업 일지는 나중에 비용을 계산하고 작업을 평가하는 근거가 된다. 그래서 무엇을, 언제, 어떻게 적는지가 정해져 있다.

태스크를 실행하는 동안 일어난 일에는 날짜·시간·GPS 위치를 붙일 수 있다. 위치가 있는 코멘트를 붙이거나 작업자를 교대하는 것처럼 XML 요소끼리 연결되는 이벤트도 있고, 클라이언트에서 받은 process data 값을 로깅하는 이벤트도 있다. 후자에는 날짜·시간·위치를 반드시 붙여야 한다.

| 규칙 | 내용 |
|---|---|
| 시간을 담는 요소 | AllocationStamp와 Time. 계획(planned)인지 실제(effective)인지 구분한다. 준비·비유효·수리·정리 같은 세부 시간 유형은 Task 수준의 Time에만 있다(아래 9절) |
| 시간대 | 버전 3까지는 현지 날짜·시각만 썼다. 버전 4부터 시간대 정보를 붙이거나 UTC("Z")로 기록할 수 있다 |
| 위치 | AllocationStamp·Time에 GNSS 위치(Position) 요소를 최대 2개 넣는다. 첫 번째는 요소를 만들 때, 두 번째는 끝낼 때다. 하나만 있으면 시작 위치다. 연속 코멘트의 중간 위치는 TimeLog 바이너리 파일에 남긴다 |
| Task 안의 값 | Time 안에 DataLogValue를 여러 개 넣을 수 있지만 total이나 단일 인스턴스 값으로 제한한다. 값이 많으면 TimeLog를 쓴다 |
| TimeLog 파일 | TimeLog 하나가 파일 2개를 만든다. 바이너리 데이터(.bin)와 그 구조를 정의하는 XML 헤더(.xml)다. 파일명 프리픽스의 유일성은 TC가 보장한다 |
| 자원 할당 | WorkerAllocation, DeviceAllocation, ProductAllocation, CommentAllocation, GuidanceAllocation, ControlAssignment가 같은 할당 패턴을 쓴다. 한 태스크에 같은 자원의 할당이 여러 번 나올 수 있다(계획 할당이 시작과 함께 실제가 될 때, 실행 중 자원을 뗐다 다시 붙일 때). 이미 기록한 할당은 고치지 않고 새 할당을 추가한다 |

표에 나온 요소 이름을 풀면 다음과 같다.

- AllocationStamp: 할당(누가, 무엇을 붙였나)에 찍는 시간·위치 도장이다.
- UTC("Z"): 세계 표준시다. 시각 끝에 Z를 붙여 표시한다. 시간대가 다른 곳의 기록을 합칠 때 헷갈리지 않는다.
- DataLogValue: 기록한 값 하나다. 여기서 "단일 인스턴스 값"은 한 번만 기록하는 값을 말한다.
- WorkerAllocation, DeviceAllocation, ProductAllocation: 각각 작업자, 장치, 자재(비료·약제 등)를 태스크에 붙인 기록이다. CommentAllocation은 코멘트, GuidanceAllocation은 자동 조향 경로, ControlAssignment는 제어 대상 연결을 붙인 기록이다.

"기록은 덧붙이기만 한다"가 이 규칙들을 관통하는 원칙이다. 태스크 파일은 실행 이력을 쌓는 로그처럼 다뤄야 하고, Time이나 할당을 고쳐 쓰는 구현은 FMIS가 받는 이력을 실제 실행과 어긋나게 만든다(추론). 회계 장부가 틀린 줄을 지우지 않고 정정하는 줄을 새로 적는 것과 같은 이치다. XML 요소 자체의 속성은 [56장 ISOXML 태스크 파일](/study/isobus/56-practice-isoxml)과 [Part 10 부록](/study/isobus/appendix-iso-part10)에 있고, TimeLog 바이너리는 [57장](/study/isobus/57-practice-binary-files)에서 직접 만들어 본다.

<small>근거: ISO 11783-10 6.2, 6.4, D.48</small>

## 7. 다른 메시지 값 로깅 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

TC는 작업기가 보고하는 값만 기록하지 않는다. 트랙터 속도나 키 상태처럼 버스에 원래 흐르는 메시지의 값도 기록해 두면 나중에 작업 상황을 더 잘 알 수 있다. 이 절은 그런 값을 메시지에서 어떻게 꺼내 기록하는지 본다.

TC는 process data뿐 아니라 버스에 흐르는 다른 PG의 값도 로깅할 수 있다. PG(Parameter Group)는 메시지 하나에 담긴 값 묶음이고, PGN은 그 묶음의 번호다([9장](/study/isobus/09-j1939-message)). 로깅 대상은 DataLogTrigger·DataLogValue의 선택 속성으로 지정한다.

| 속성 | 값 |
|---|---|
| DataLogDDI | `0xDFFE`(ParameterGroupNumberValue, PGN log value)로 고정 |
| DataLogPGN | 값을 꺼낼 PGN(0 ~ 2^18 - 1) |
| DataLogPGNStartBit | 데이터 필드의 비트 위치를 0부터 센다. 0은 Byte 1의 최하위 비트다. 시작 비트가 값의 LSB가 된다 |
| DataLogPGNStopBit | 끝 비트(포함). 값의 MSB가 된다. 값 크기는 최대 32비트다 |

- DataLogDDI는 원래 "어떤 종류의 값을 기록하나"를 DDI 번호로 적는 칸이다. 다른 메시지의 값을 기록할 때는 특별한 번호 `0xDFFE`(=57342)를 넣어 "이건 PGN에서 꺼낸 값"이라고 표시한다.
- 2^18 - 1은 262143이다. PGN이 18비트 번호라서 이 범위가 된다.
- LSB(Least Significant Bit)는 값의 가장 낮은 자리 비트, MSB(Most Significant Bit)는 가장 높은 자리 비트다.

PG에서 꺼낸 값도 어느 DeviceElement의 값인지 참조가 필요하다. ClientNAME 속성을 채운 Device 요소와 그 Device를 가리키는 DeviceElement를 TC가 만들거나 FMIS가 공급한다. DeviceElement는 장치 안의 한 부분(붐, 섹션 등)을 가리키는 요소다([48장](/study/isobus/48-ddop-basics)). 메시지를 보낸 트랙터도 이렇게 "장치"로 등록해 두어야 기록한 값의 주인이 분명해진다.

### 예: 휠 속도 메시지에서 값 꺼내기

예를 들어 Wheel-based speed and distance(PGN 65096, `0xFE48`)를 보자. Byte 1~2가 차속(0.001 m/s/bit), Byte 7이 Maximum time of tractor power(1 min/bit), Byte 8 bits 4~3이 Key switch state다. 메시지의 바이트 구성은 [23장](/study/isobus/23-implement-messages-basics)에서 본다.

표준 문서가 위치를 적는 방식과 DataLogPGNStartBit가 세는 방식이 다르다는 점을 먼저 알아 둔다.

- 표준의 "Byte n, bit m"은 둘 다 1부터 센다. bit 1이 그 바이트의 가장 낮은 자리, bit 8이 가장 높은 자리다.
- 여러 바이트에 걸친 값은 낮은 자리 바이트가 먼저 온다(리틀 엔디언). 그래서 Byte 1~2의 차속은 Byte 1이 낮은 자리다.
- DataLogPGNStartBit는 데이터 전체를 한 줄로 늘어놓고 0부터 센다.

그래서 변환이 필요하다. Byte 8 bit 3은 (8 - 1) × 8 + (3 - 1) = 58이다. 앞의 7바이트(56비트)를 건너뛰고, 그 바이트 안에서 두 칸을 더 간 자리라는 뜻이다.

| 로깅할 값 | DataLogPGN | StartBit | StopBit |
|---|---|---|---|
| 차속(Byte 1~2) | 65096 | 0 | 15 |
| Maximum time of tractor power(Byte 7) | 65096 | 48 | 55 |
| Key switch state(Byte 8 bits 4~3) | 65096 | 58 | 59 |

- 차속: Byte 1 bit 1이 0번, Byte 2 bit 8이 15번이다. 16비트 값이다.
- Maximum time of tractor power: Byte 7 bit 1은 (7 - 1) × 8 + 0 = 48번, bit 8은 55번이다. 트랙터가 지금 부하로 전기를 몇 분 더 공급할 수 있는지(남은 전원 시간) 나타낸다.
- Key switch state: Byte 8 bit 3이 58번, bit 4가 59번이다. 2비트 값으로 `00`이 Off, `01`이 not Off다.

::: details 파이썬으로 검산해 보기
Byte 8의 나머지 2비트 필드는 `11`로 채운 예시 프레임이다.

```python
def pg_value(data, start_bit, stop_bit):
    width = stop_bit - start_bit + 1
    assert 1 <= width <= 32
    return (int.from_bytes(data, "little") >> start_bit) & ((1 << width) - 1)


def zero_based_bit(byte_no, bit_no):
    return (byte_no - 1) * 8 + (bit_no - 1)


frame = bytes.fromhex("E8 03 00 00 00 00 05 F7")

speed_raw = pg_value(frame, 0, 15)
assert speed_raw == 1000
print("speed", speed_raw * 0.001, "m/s")

key_start, key_stop = zero_based_bit(8, 3), zero_based_bit(8, 4)
assert (key_start, key_stop) == (58, 59)
assert pg_value(frame, key_start, key_stop) == 0b01

power_start, power_stop = zero_based_bit(7, 1), zero_based_bit(7, 8)
assert (power_start, power_stop) == (48, 55)
assert pg_value(frame, power_start, power_stop) == 5

key_off_frame = bytes.fromhex("E8 03 00 00 00 00 05 F3")
assert pg_value(key_off_frame, key_start, key_stop) == 0b00
```

```
speed 1.0 m/s
```

차속 raw 1000 × 0.001 = 1.0 m/s, 남은 전원 시간 5분, Key switch state `01`(not Off)이다. 마지막 프레임은 Byte 8만 `F3`으로 바꿔 Key switch state가 `00`(Off)이 된 경우다. 이 비트가 [43장](/study/isobus/43-tc-connection) 셧다운 절차의 출발 신호다.

바이트를 직접 읽어 보면 다음과 같다.

1. Byte 1~2는 `E8 03`이다. 낮은 자리 바이트가 먼저 오므로 값은 `0x03E8` = 1000이다.
2. Byte 7은 `05` = 5이고, 1 min/bit이므로 5분이다.
3. Byte 8 `F7`을 2진수로 쓰면 `1111 0111`이다. 오른쪽 끝이 bit 1이므로 bits 4~3은 `01`이다.
4. `F3`은 `1111 0011`이라 bits 4~3이 `00`이 된다.
:::

<small>근거: ISO 11783-10 6.3, D.17. ISO 11783-7 B.3, A.8, A.11, A.12</small>

## 8. 언어·형식·단위 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

한 트랙터 안에서도 화면마다 언어와 단위 설정이 다를 수 있다. 작업기가 TC 화면에 이름과 값을 보여 줄 때 어느 설정을 따라야 하는지가 이 절의 주제다.

VT가 쓰는 언어·형식·단위와 TC/DL의 로캘 설정은 다를 수 있다. 클라이언트는 TC/DL에 standard setup을 물어 device descriptor의 텍스트와 DeviceValuePresentation(DVP)을 TC/DL 화면에 맞게 바꿔야 한다. standard setup은 Part 7이 정의한 언어·형식·단위 메시지 묶음이고, 그중 Language command가 PGN 65039(`0xFE0F`)다. 메시지 바이트는 [25장](/study/isobus/25-settings-safety-messages)에서 본다.

- 로캘(locale)은 언어, 날짜·숫자 형식, 단위계(미터법, 야드파운드법)를 묶은 지역 설정이다.
- DVP(DeviceValuePresentation)는 값을 화면에 어떻게 보여 줄지(배율, 소수 자리, 단위 이름)를 정한 DDOP 오브젝트다. 같은 살포량이라도 미터법이면 L/ha, 야드파운드법이면 gal/ac로 보이게 하는 데 쓴다.

| 주체 | 요구사항 | 도입 |
|---|---|---|
| TC(VT가 있는 네트워크) | standard setup을 송신하고, 주 연결 VT(클라이언트 값을 표시할 VT)의 설정을 따른다. VT와 연결된 적 없는 공장 출하 상태면 제조사 기본값을 쓴다 | |
| TC | 클라이언트 초기화 때와 설정이 바뀔 때마다 standard setup을 보고한다. 오퍼레이터가 VT 설정을 바꾸거나 TC가 다른 VT에 붙은 경우가 해당한다 | |
| TC | standard setup을 비휘발성 메모리에 저장했다가 VT 연결 전 초기화 때 복원한다. VT와 연결되면 그 VT를 따른다 | |
| TC | 전역 주소로 온 Language Command 요청에 응답한다 | v4 |
| TC | TC에 직접 온 Language Command 요청에 응답한다 | v4 |
| TC(VT를 안 쓰는) | 언어·단위를 설정하는 proprietary 수단을 제공한다 | |
| 클라이언트 | device descriptor를 게시하는 <strong>그 TC</strong>의 setup을 따른다. 버전 3까지는 VT나 TECU 설정을 따랐다 | v4 |
| 클라이언트 | 선택된 언어를 지원하지 않으면 자기 기본 언어를 쓴다 | |

- 비휘발성 메모리는 전원을 꺼도 내용이 남는 저장 공간이다.
- TECU는 트랙터 ECU다([22장](/study/isobus/22-tractor-ecu)).
- 버전 4에서 클라이언트의 기준이 "자기 DDOP를 보여 줄 그 TC"로 바뀐 것이 핵심이다. 값을 보여 주는 화면의 설정을 따라야 단위가 어긋나지 않기 때문으로 보인다(추론).

설정이 바뀌면 클라이언트는 표준 device descriptor 수정 방법으로 텍스트와 DVP를 고친다. 수정 메시지는 [50장 DDOP 전송과 설계 점검](/study/isobus/50-ddop-commands-design)에서 다룬다.

<small>근거: ISO 11783-10 6.5. ISO 11783-7 B.21</small>

::: tip 정리
- 태스크는 FMIS와 MICS 사이를 오가는 작업 단위다. 표준이 정한 경계는 XML 파일 세트와 버스 메시지 두 곳뿐이다.
- 상태 값은 1~6이다. Running은 TC당 하나, Completed는 오퍼레이터만 설정하고, Template·Canceled는 버전 4에서 생겼다.
- 태스크 기록은 덧붙이기만 한다. Time과 할당은 상태·자원이 바뀔 때만 추가하고 고치지 않는다.
:::

## 9. 태스크 시간 기록: 두 수준

작업 시간은 인건비와 기계 사용료를 계산하고 작업 효율을 따지는 기본 자료다. 그런데 "작업 시간"이라고 해도 밭까지 이동한 시간, 실제로 뿌린 시간, 고장 수리한 시간은 성격이 다르다. 이 절은 시간을 어떤 단위로 나눠 기록하는지 본다.

Part 10은 시간 기록을 두 수준으로 나눈다.

| 수준 | 무엇을 기록하나 | 수단 |
|---|---|---|
| 태스크 수준 | 태스크가 거치는 시간 유형(준비·유효 작업·비유효·수리 등)의 시작·기간·끝 | Task 안의 Time 요소 |
| 장치 수준 | 각 장치가 TC/DL에 보고하는 상태(작업 중, 이동 중 등)와 그 변화 | 장치 데이터 로깅(DDI 119·120 같은 total, PG 로깅, TimeLog) |

태스크 수준은 "이 작업 전체가 어떻게 흘러갔나"를, 장치 수준은 "기계 하나하나가 언제 일했나"를 본다.

### Time 유형 코드

Time 요소의 Type 속성 값이다. 마지막 열은 그 유형을 따로 기록할 수 없는 시스템이 대신 쓰는 유형이다.

| Type | 이름 | 정의 | 기록할 수 없으면 |
|---|---|---|---|
| 1 | Planned | 태스크의 계획 시작·정지·기간. 계획·일정 용도로만 쓰고 태스크당 최대 1개 | - |
| 2 | Preliminary | 농장에서 준비, 밭으로 이동, 밭에서 준비하는 시간. 태스크가 활성화되면 시작해 Effective나 다른 유형이 시작되면 끝난다 | Ineffective |
| 3 | (Preparation) | 버전 4에서 폐기. Preliminary보다 나은 정보를 주지 못했다 | - |
| 4 | Effective | 작업 과정에 절대적·직접적으로 필요한 활동. 태스크의 주 작업이 시작되면 시작한다. <strong>MICS가 제공해야 하는 최소 요건</strong>이다 | - |
| 5 | Ineffective | 주 작업이 활성이 아닌 시간. Effective 구간 사이에 쓴다 | - |
| 6 | Repair | 태스크 중 수리에 쓴 시간 | Ineffective |
| 7 | Clearing | 태스크 중 Effective가 마지막으로 멈춘 뒤부터 태스크가 멈출 때까지 | Ineffective |
| 8 | Powered Down | 시간 기록이 돌아가는 기계의 전원이 꺼진 때부터. 버전 4 도입 | Ineffective |

비료 살포 하루로 바꿔 보면 이렇다. 창고에서 비료를 싣고 밭으로 가는 시간이 Preliminary(2), 실제로 뿌리는 시간이 Effective(4), 비료를 다시 채우려고 멈춘 시간이 Ineffective(5), 노즐이 막혀 고친 시간이 Repair(6), 마지막으로 뿌린 뒤 정리하는 시간이 Clearing(7)이다. 점심시간에 시동을 껐다면 그 시간은 Powered Down(8)이다.

표준은 규칙 두 가지를 더 정한다. FMIS가 주는 Time은 모두 Planned여야 한다. MICS가 Type 2~8을 써서 세부 구분을 하지 않는다면 MICS가 주는 Time은 모두 Effective(4)여야 하며, 이때 Effective 합계가 총 작업 시간이고 더 쪼갤 수 없다.

### Minimal과 Intermediate

같은 태스크를 얼마나 잘게 나눠 기록하는지에 따라 두 수준이 있다.

![태스크 시간 기록 수준 비교: Minimal은 태스크 시작부터 정지까지를 Effective(4) 하나로 기록하고, Intermediate는 같은 구간을 Preliminary(2), Effective(4), Ineffective(5), Effective(4), Ineffective(5), Effective(4), Clearing(7)로 나눠 기록한다](/images/study-isobus/18-time-registration-levels-light.png)
![태스크 시간 기록 수준 비교: Minimal은 태스크 시작부터 정지까지를 Effective(4) 하나로 기록하고, Intermediate는 같은 구간을 Preliminary(2), Effective(4), Ineffective(5), Effective(4), Ineffective(5), Effective(4), Clearing(7)로 나눠 기록한다](/images/study-isobus/18-time-registration-levels-dark.png)

| 수준 | MICS가 쓰는 Type | 설명 |
|---|---|---|
| 1. Minimal | 4 | 태스크의 시간을 Effective 하나로만 남긴다. 태스크 안 모든 Effective Time의 합이 그 태스크의 총 작업 시간이다 |
| 2. Intermediate | 2, 4, 5, 6, 7, 8 | 주 작업을 감지하면 2·4·5·7을 자동으로 기록할 수 있다. 감지에는 태스크에 할당된 장치들의 작업 상태(work status) 정보를 쓸 수 있다. 6(Repair)은 오퍼레이터 입력이 필요할 수 있고, 8(Powered Down)은 implement bus에 방송되는 정보로 자동 기록할 수 있다 |

implement bus는 트랙터와 작업기를 잇는 ISOBUS 버스를 말한다. 키 상태처럼 버스에 방송되는 정보를 보면 전원이 꺼진 때를 사람이 입력하지 않아도 알 수 있다.

구현으로 옮기면 할당 장치의 Actual Work State(DDI 141)를 받아 Effective와 Ineffective의 경계를 정하고, 7절에서 본 Key switch state로 Powered Down을 정하는 식이 된다(추론). Actual Work State는 작업기가 "지금 작업 중인가"를 알리는 값이다.

같은 태스크라도 수준에 따라 "Effective"가 덮는 범위가 다르다는 점이 함정이다. 위 그림에서 Minimal의 Effective는 태스크 시작부터 정지까지 전체(총 작업 시간)를 덮지만, Intermediate의 Effective는 주 작업 구간뿐이다. 그래서 FMIS가 서로 다른 수준의 TC에서 온 Effective 합계를 그대로 비교하면 안 된다(추론).

::: details 파이썬으로 검산해 보기
구간 길이(초)는 예시 값이다.

```python
intermediate = [(2, 600), (4, 3600), (5, 300), (4, 2400), (5, 900), (4, 1800), (7, 300)]
task_span_s = sum(duration for _, duration in intermediate)
minimal = [(4, task_span_s)]


def effective_total(times):
    return sum(duration for time_type, duration in times if time_type == 4)


assert task_span_s == 9900
assert effective_total(minimal) == 9900
assert effective_total(intermediate) == 7800
print(effective_total(minimal) / 3600, effective_total(intermediate) / 3600)
```

```
2.75 2.1666666666666665
```

같은 2시간 45분짜리 태스크가 Minimal에서는 Effective 2.75 h, Intermediate에서는 약 2.17 h로 기록된다.

`intermediate`의 각 항목은 (Type, 초)다. Effective(4) 구간만 더하면 3600 + 2400 + 1800 = 7800초이고, 전체 구간은 9900초다. Minimal은 전체 9900초를 Effective 하나로 적으므로 두 값이 2100초(35분) 차이 난다.
:::

### 장치 수준 시간: DDI 119와 120

장치 수준에서는 장치가 스스로 "일한 시간"과 "일하지 않은 시간"의 합계를 센다.

| DDI | 이름 | 정의 | 단위 |
|---|---|---|---|
| 119 | Effective Total Time | 작업 위치에 있고 (거의 모든 필드 작업에서) 전진 속도가 있는 누적 시간. 관개 펌프를 돌리는 트랙터는 전진 없이 effective인 예다 | s |
| 120 | Ineffective Total Time | 작업 위치 밖이거나 정지 상태인 누적 시간 | s |

쟁기가 작업 위치에 있어도 트랙터가 서 있으면 그 시간은 Effective가 아니라 Ineffective다. 이 두 정의로 장치(또는 장치의 일부)가 Effective·Ineffective 상태였던 총 시간을 로깅할 수 있다. Part 7과 SAE J1939의 Wheel-based speed and distance, Implement operating state command 같은 PG도 시간 기록에 쓸 수 있다.

"작업 위치"는 쟁기를 땅에 내리거나 살포기 붐을 펼친 것처럼 작업할 수 있는 자세를 말한다. 자세만으로는 부족하고 대개 앞으로 움직이고 있어야 Effective다.

DDI 119는 TC-BAS 클라이언트가 조건 없이 제공해야 하는 최소 DDI이기도 하다([41장 7절](/study/isobus/41-tc-basics)). "TC-BAS를 지원한다"는 말은 최소한 작업 위치와 전진 조건으로 유효 시간을 셀 줄 안다는 뜻이 된다(추론).

<small>근거: ISO 11783-10 Annex G(G.1~G.3), D.48, F.2.1</small>

::: tip 핵심 정리
- 태스크는 한 고객의 한 partfield에서 하는 작업 하나다. FMIS와 MICS 어느 쪽에서도 만들 수 있고, 표준은 XML 파일 세트와 버스 통신 두 경계만 정한다.
- FMIS는 NAME과 마스크로 장치를 미리 고를 수 있고, 실제로 쓴 장치는 따로 기록한다.
- 태스크 상태는 Planned(1)·Running(2)·Paused(3)·Completed(4)·Template(5)·Canceled(6)다. Running은 TC당 하나, Completed는 오퍼레이터만 정한다.
- 기록은 덧붙이기만 한다. 상태나 자원이 바뀔 때 Time과 할당을 새로 추가하고, 지난 기록은 고치지 않는다.
- 작업 시간은 Time 유형(Planned, Preliminary, Effective, Ineffective, Repair, Clearing, Powered Down)으로 나눈다. Minimal은 Effective 하나만, Intermediate는 세부 유형까지 기록하므로 둘의 Effective 합계를 그대로 비교하면 안 된다.
:::

::: details 확인 문제
1. (개념) 표준이 정하는 곳과 정하지 않는 곳을 하나씩 들어 보라. 태스크 파일을 USB 메모리로 옮기는 제품과 무선으로 옮기는 제품은 둘 다 표준에 맞는가?
2. (개념) TC가 태스크를 Running에서 Paused로 바꿨다. 버스 메시지와 태스크 파일에는 각각 어떤 변화가 생기는가?
3. (개념) 작업기 섹션이 모두 꺼진 것을 보고 TC가 태스크를 자동으로 Completed로 바꾸도록 구현했다. 무엇이 문제인가?
4. (계산) 휠 속도 메시지(PGN 65096) Byte 7(Maximum time of tractor power)을 로깅하려 한다. DataLogPGNStartBit와 StopBit는 각각 얼마인가? 이 바이트가 `0A`라면 값은 무엇을 뜻하는가?
5. (응용) 한 TC는 Minimal로, 다른 TC는 Intermediate로 시간을 기록한다. 같은 길이의 작업인데 Effective 합계가 다르게 나왔다. 어느 쪽이 틀렸는가?

**답 가이드**
1. 표준은 XML 파일 세트의 형식과 TC와 작업기 사이의 버스 통신을 정한다. FMIS 안의 계획·평가 방법과 파일을 TC로 옮기는 방법은 정하지 않는다. 그래서 USB 메모리로 옮기든 무선으로 옮기든 파일 형식만 맞으면 둘 다 표준에 맞는다.
2. 버스: TC Status Byte 5 bit 1(Task totals active)이 1에서 0으로 바뀌고, 클라이언트는 task total 세기를 멈춘다. 파일: 상태가 바뀌었으므로 Task에 Time 요소가 새로 추가된다. 이미 기록한 Time은 고치지 않는다.
3. Completed는 오퍼레이터만 설정할 수 있고 MICS가 자동으로 설정하지 못한다. 섹션이 꺼진 것은 잠시 멈춘 것일 수도 있으므로 상태를 자동으로 끝내면 안 된다.
4. Byte 7 bit 1은 (7 - 1) × 8 + (1 - 1) = 48, bit 8은 (7 - 1) × 8 + (8 - 1) = 55다. 따라서 StartBit 48, StopBit 55다. `0A`는 10이고 단위가 1 min/bit이므로, 트랙터가 지금 부하로 전기를 최대 10분 더 공급할 수 있다는 뜻이다.
5. 어느 쪽도 틀리지 않았다. Minimal은 태스크 시작부터 정지까지 전체를 Effective로 적고, Intermediate는 주 작업 구간만 Effective로 적는다. 서로 다른 수준의 Effective 합계는 그대로 비교하면 안 된다.
:::

## 다음 챕터

- 다음: [43장 TC 연결 관리와 메시지 바이트](/study/isobus/43-tc-connection)
