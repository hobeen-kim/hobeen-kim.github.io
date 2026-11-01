---
title: "Virtual Terminal(VT) 기초"
description: "트랙터 운전석의 공용 화면에 작업기가 자기 화면을 띄우는 VT의 개념과 동작 순서, 버전, 보조 입력(AUX)을 익히고 첫 연결을 8바이트 프레임으로 따라간다."
date: 2026-04-13
tags: [ISOBUS, VT, Virtual Terminal, ISO-11783-6, AUX]
prev: /study/isobus/28-diagnostics-dm-fmi
next: /study/isobus/30-vt-display-technical-data
---

# Virtual Terminal(VT) 기초

::: info 학습 목표
- VT가 무엇이고 어떤 문제를 풀려고 생겼는지 설명할 수 있다.
- VT Server(화면을 가진 트랙터 쪽)와 VT Client(화면 내용을 정하는 작업기 쪽)가 각각 무엇을 맡는지 구분할 수 있다.
- 오브젝트 풀 전송, 화면 표시, 운전자 입력으로 이어지는 VT 동작 순서와 연결을 지키는 두 주기 메시지를 설명할 수 있다.
- VT 버전마다 쓸 수 있는 기능이 다르고, 작업기가 VT 버전에 맞춰 자기 쪽을 조정한다는 것을 설명할 수 있다.
- AUX(보조 입력)와 Preferred Assignment가 무엇인지 말하고, 첫 연결 로그의 8바이트 프레임을 읽을 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [18장 ISOBUS 개요](/study/isobus/18-isobus-overview), [26장 ISOBUS 네트워크 관리와 Working Set](/study/isobus/26-isobus-network-mgmt), [15장 Transport Protocol 기초](/study/isobus/15-tp-bam-cmdt)
- 이 장에서 처음 나오는 말
  - VT(Virtual Terminal): 트랙터 운전석에 있는 공용 화면. 연결된 여러 작업기가 함께 쓴다.
  - VT Server와 VT Client: 화면을 가진 쪽(트랙터의 VT)과 화면 내용을 정해 보내는 쪽(작업기의 ECU, 즉 전자 제어 장치).
  - 오브젝트 풀(object pool): 작업기가 VT에 보내는 화면 설계도 묶음. 글자, 숫자, 버튼, 화면 한 장 같은 "오브젝트"를 모은 것이다.
  - Working Set(WS): 작업기 하나를 이루는 제어 장치 묶음. VT 입장에서는 화면을 빌려 쓰는 손님 하나다.
  - 마스크(mask): VT에 뜨는 화면 한 장. 작업기 화면을 그리는 Data Mask와 소프트키 라벨을 그리는 Soft Key Mask가 있다.
  - AUX(Auxiliary Input, 보조 입력): 조이스틱처럼 VT 밖에 있는 입력 장치를 작업기 기능에 연결하는 구조.
:::

트랙터 운전석에는 화면이 하나 있다. 비료 살포기를 달면 그 화면에 살포기 화면이 뜨고, 파종기로 바꿔 달면 파종기 화면이 뜬다. 화면은 트랙터 것인데, 무엇을 보여 줄지는 작업기가 정한다. 이렇게 트랙터 운전석의 공용 모니터에 작업기가 자기 화면을 띄우는 구조가 Virtual Terminal(VT)이다.

이 장은 VT가 왜 생겼는지, 화면이 어떤 순서로 뜨는지, VT 버전과 보조 입력(AUX)이 무엇인지 본다. 마지막 절에서는 작업기가 VT에 처음 붙는 과정을 실제 8바이트 프레임으로 따라간다.

## 1. 왜 VT가 필요한가

이 절에서는 VT가 없던 시절에 무엇이 불편했는지 보고, VT가 그 불편을 어떻게 없앴는지 본다.

### VT 이전: 작업기마다 전용 디스플레이

VT 표준이 없던 시절, 각 작업기 제조사는 <strong>전용 디스플레이 패널</strong>을 함께 납품했다.

- 비료 살포기 → 비료 살포기 전용 컨트롤 박스
- 파종기 → 파종기 전용 모니터
- 스프레이어 → 스프레이어 전용 디스플레이

운전석에 작업기가 늘어날수록 디스플레이도 늘어났다. 배선은 복잡해지고, 운전자는 여러 개의 서로 다른 UI(User Interface, 사람이 보고 조작하는 화면과 버튼)를 익혀야 했다.

### VT 이후: 화면 하나를 함께 쓴다

VT가 이 문제를 푼 방식은 흔히 <strong>스마트폰 앱 스토어 모델</strong>에 빗대어 설명한다.

```
스마트폰(VT Server) = 하드웨어 플랫폼
앱(오브젝트 풀)     = 작업기 ECU가 제공하는 UI 정의
```

ECU(Electronic Control Unit)는 작업기 안에서 기계를 제어하는 전자 장치다. 하나의 VT 디스플레이에 어떤 제조사의 작업기를 연결해도, 작업기 ECU가 자신의 UI 정의를 VT로 전송하면 VT가 그 정의대로 화면을 그린다. 이렇게 받은 정의를 화면에 그리는 일을 렌더링(rendering)이라고 한다. 운전자는 <strong>하나의 디스플레이로 모든 작업기를 조작</strong>할 수 있다.

![VT 디스플레이 하나에 비료 살포기, 파종기, 스프레이어, 베일러 ECU가 각자 오브젝트 풀 A~D를 올리는 구조](/images/study-isobus/29-one-display-many-implements-light.png)
![VT 디스플레이 하나에 비료 살포기, 파종기, 스프레이어, 베일러 ECU가 각자 오브젝트 풀 A~D를 올리는 구조](/images/study-isobus/29-one-display-many-implements-dark.png)

앱 스토어 비유는 "하드웨어 하나에 여러 회사의 화면이 올라간다"는 점까지만 맞다. 두 가지가 다르다.

- 스마트폰 앱은 휴대폰 안에서 스스로 도는 프로그램이다. 오브젝트 풀은 화면 설계도이고, 기계를 실제로 움직이는 판단(살포량 계산 등)은 계속 작업기 ECU가 한다. 풀에는 버튼이 눌렸을 때처럼 정해 둔 일이 생기면 VT가 실행할 짧은 명령 목록(매크로) 정도만 들어간다.
- 앱은 사용자가 골라 설치하지만, 오브젝트 풀은 작업기를 연결하면 작업기가 알아서 VT에 올린다.

그래서 다음 절에서는 더 가까운 비유인 웹 브라우저로 VT를 다시 본다.

::: tip 정리
- VT 이전에는 작업기마다 전용 화면이 운전석에 붙었다.
- VT 이후에는 트랙터의 화면 하나에 작업기들이 각자 화면 설계도(오브젝트 풀)를 올려 함께 쓴다.
:::

## 2. VT란 무엇인가

이 절에서는 VT를 이루는 두 주체와 화면 구성을 정의하고, 웹 브라우저 비유가 어디까지 맞는지 정리한다.

### 정의와 두 주체

<strong>Virtual Terminal(VT)</strong>은 ISO 11783-6(ISOBUS의 VT를 정하는 표준 문서)에 정의된 표준 사용자 인터페이스 시스템이다. 트랙터 운전석에 장착된 디스플레이에 <strong>작업기의 UI를 표시하고 사용자 입력을 받는</strong> 인터페이스 역할을 한다.

VT 시스템은 두 주체로 구성된다.

| 역할 | 장치 | 담당 |
|------|------|------|
| **VT Server** | 트랙터 캐빈 디스플레이 | 화면 렌더링, 입력 처리 |
| **VT Client** | 작업기 ECU | 화면 내용(오브젝트 풀) 정의, 데이터 갱신 |

Server와 Client는 컴퓨터 네트워크에서 흔히 쓰는 말이다. 서비스를 내주는 쪽이 Server, 받아 쓰는 쪽이 Client다. 여기서는 화면을 내주는 VT가 Server이고, 그 화면을 빌려 쓰는 작업기 ECU가 Client다.

즉, <strong>디스플레이 하드웨어는 트랙터가 제공</strong>하고, <strong>화면에 무엇을 보여줄지는 작업기 ECU가 결정</strong>한다. 트랙터와 작업기의 역할이 명확히 분리되어 있는 것이 핵심이다.

![트랙터 안의 VT Server(CAN 주소 0x26)가 디스플레이 하드웨어를 맡고, 작업기 ECU(VT Client)가 오브젝트 풀을 보내며 VT로부터 사용자 입력 이벤트를 받는 구조](/images/study-isobus/29-vt-server-client-light.png)
![트랙터 안의 VT Server(CAN 주소 0x26)가 디스플레이 하드웨어를 맡고, 작업기 ECU(VT Client)가 오브젝트 풀을 보내며 VT로부터 사용자 입력 이벤트를 받는 구조](/images/study-isobus/29-vt-server-client-dark.png)

그림의 `0x26`(=38)은 VT의 CAN 주소 예다. 주소(SA, Source Address)는 CAN 버스에서 메시지를 보낸 장치를 가리키는 1바이트 번호다([12장](/study/isobus/12-j1939-address-name)). 이 장과 다음 두 장의 예에서는 VT 주소를 `0x26`으로 둔다.

### 화면은 두 영역으로 나뉜다

VT 화면은 <strong>Data Mask 영역</strong>(작업기 UI가 표시되는 정사각형 영역, 최소 200 × 200 픽셀, version 6부터 최소 480 × 480)과 <strong>Soft Key Mask 영역</strong>(소프트키 라벨 영역, version 6부터 키당 최소 60 × 60 픽셀)으로 구성된다.

소프트키(soft key)는 화면 옆이나 아래에 붙은 버튼인데, 무슨 일을 하는지는 버튼 옆 화면에 뜬 라벨이 정한다. 작업기가 바뀌면 같은 버튼의 뜻도 바뀐다. 두 영역의 크기와 배치 규칙은 [30장](/study/isobus/30-vt-display-technical-data)에서 자세히 본다.

### 웹 브라우저 비유: 맞는 점과 틀어지는 점

VT는 웹 브라우저와 웹 페이지의 관계에 빗대면 쉽게 그려진다.

| 웹 | VT |
|---|---|
| 브라우저: 어느 사이트의 페이지든 받아서 그린다 | VT(VT Server): 어느 제조사의 작업기 화면이든 받아서 그린다 |
| 웹 페이지(HTML): 무엇을 어디에 둘지 적은 문서 | 오브젝트 풀: 무엇을 어디에 둘지 적은 오브젝트 묶음 |
| 웹 서버: 페이지를 보내고 클릭을 받아 처리한다 | 작업기 ECU(VT Client): 풀을 보내고 운전자 입력을 받아 처리한다 |
| 클릭 이벤트 | 버튼·소프트키가 눌렸음을 알리는 활성화 메시지 |

<strong>맞는 점</strong>

- 화면을 그리는 쪽과 화면 내용을 정하는 쪽이 다르다. 사이트마다 브라우저를 따로 깔지 않듯, 작업기마다 화면을 따로 달지 않는다.
- 같은 페이지가 여러 브라우저에서 열리듯, 같은 오브젝트 풀은 제조사가 다른 VT에서도 뜬다. 어떤 오브젝트를 어떻게 그릴지 표준이 정해 두었기 때문이다.
- 운전자가 화면의 버튼을 누르면 그 사실이 화면 주인(작업기)에게 전달되고, 무엇을 할지는 작업기가 정한다.

<strong>틀어지는 점</strong>

- <strong>화면 설계도를 미리 통째로 올린다.</strong> 웹 브라우저는 보통 페이지가 필요할 때마다 서버에서 받아 온다. VT에서는 작업기가 연결할 때 모든 화면이 든 오브젝트 풀을 한 번에 VT로 올리고, 그 뒤로는 "이 숫자를 85로 바꿔라" 같은 짧은 명령만 보낸다.
- <strong>화면을 바꾸는 쪽이 작업기다.</strong> 웹 페이지는 사용자가 링크를 눌러 넘어간다. VT에서는 운전자 입력을 받은 작업기가 명령을 보내 화면을 바꾸고, 경고가 생기면 작업기가 먼저 알람 화면을 띄운다.
- <strong>화면 쪽에 프로그램이 없다.</strong> 웹 페이지는 자바스크립트로 스스로 계산할 수 있지만, 오브젝트 풀에는 그런 프로그램이 없고 짧은 명령 목록(매크로) 정도만 담긴다. 계산과 판단은 작업기 ECU가 한다.
- <strong>서로 살아 있는지 계속 확인한다.</strong> 웹 서버가 꺼져도 이미 연 페이지는 화면에 남는다. VT는 작업기가 3초 동안 신호를 보내지 않으면 운전자에게 경보하고 그 작업기의 화면을 지운다(3절).
- <strong>모르는 기능이 든 풀은 받지 않는다.</strong> 브라우저는 모르는 태그를 건너뛰고 나머지를 그린다. VT는 자기 버전보다 높은 버전의 기능처럼 지원하지 않는 기능이 든 풀을 거부한다. 그래서 작업기가 VT 버전과 능력을 먼저 확인하고 자기 풀을 거기에 맞춘다(4절).

정리하면 VT는 "서버가 화면 설계도를 미리 통째로 올려 두고, 짧은 명령으로 화면을 계속 바꾸는 브라우저"에 가깝다.

::: tip 정리
- VT는 ISO 11783-6이 정한 표준 화면 시스템이다. 화면은 트랙터(VT Server)가, 화면 내용은 작업기 ECU(VT Client)가 맡는다.
- VT 화면은 작업기 화면을 그리는 Data Mask 영역과 소프트키 라벨을 그리는 Soft Key Mask 영역으로 나뉜다.
- 웹 브라우저 비유는 "그리는 쪽과 내용을 정하는 쪽이 다르다"까지 맞다. 풀을 미리 통째로 올리고, 작업기가 화면을 바꾸며, 서로 살아 있는지 계속 확인한다는 점이 다르다.
:::

<small>근거: ISO 11783-6 4.6.24</small>

## 3. VT 동작 원리

이 절에서는 작업기가 VT에 붙어서 화면을 띄우고 운전자 입력을 주고받기까지의 큰 흐름을 본다.

VT와 작업기 ECU 사이의 동작은 크게 세 단계로 나뉜다.

1. <strong>오브젝트 풀 전송</strong>: 작업기 ECU가 화면 정의 데이터를 VT로 업로드
2. <strong>렌더링</strong>: VT가 오브젝트 풀을 해석해 화면에 표시
3. <strong>상호작용</strong>: 사용자 입력 → VT → ECU, ECU 데이터 갱신 → VT 화면 업데이트

아래 그림은 세 단계를 메시지 순서로 펼친 것이다. 세로 점선은 각 장치이고 시간은 위에서 아래로 흐른다. 가로 화살표가 메시지다.

![작업기 ECU, VT Server, 운전자 사이의 메시지 순서. 연결 확인 단계에서 VT Status와 Working Set Maintenance가 1초 주기로 오가고 Get Memory 요청과 응답이 오간다. 풀 전송 단계에서 Object Pool Transfer와 End of Object Pool 뒤 VT가 파싱하고 End of Object Pool Response로 답한다. 입력 단계에서 운전자 입력이 Button Activation으로 ECU에 가고 ECU가 Change Numeric Value로 화면 값을 바꾼다](/images/study-isobus/29-vt-operation-sequence-light.png)
![작업기 ECU, VT Server, 운전자 사이의 메시지 순서. 연결 확인 단계에서 VT Status와 Working Set Maintenance가 1초 주기로 오가고 Get Memory 요청과 응답이 오간다. 풀 전송 단계에서 Object Pool Transfer와 End of Object Pool 뒤 VT가 파싱하고 End of Object Pool Response로 답한다. 입력 단계에서 운전자 입력이 Button Activation으로 ECU에 가고 ECU가 Change Numeric Value로 화면 값을 바꾼다](/images/study-isobus/29-vt-operation-sequence-dark.png)

그림을 위에서부터 읽으면 다음과 같다.

1. <strong>연결 확인</strong>: VT는 VT Status 메시지를 1초마다 버스 전체에 브로드캐스트(broadcast, 특정 상대 없이 모두에게 보내기)한다. 작업기는 이 메시지로 VT가 있다는 것을 안 뒤, 자기도 Working Set Maintenance 메시지를 1초마다 보내기 시작한다. 이어서 Get Memory 같은 기술 데이터 요청으로 VT의 버전과 메모리 상태를 묻는다.
2. <strong>풀 전송과 표시</strong>: 작업기가 Object Pool Transfer로 화면 정의를 보내고 End of Object Pool로 끝을 알린다. VT는 받은 바이트를 해석해 오브젝트로 만들고(파싱, parsing) 화면을 그린 뒤, End of Object Pool Response로 오류가 있었는지 알린다.
3. <strong>입력과 갱신</strong>: 운전자가 버튼이나 소프트키를 누르면 VT가 Button Activation 같은 활성화 메시지로 작업기에 알린다. 작업기는 입력을 처리하고(예: 살포량 변경) Change Numeric Value 같은 명령으로 화면의 값을 바꾼다.

### 연결을 지키는 두 주기 메시지

연결 유지는 두 주기 메시지가 담당한다. VT는 <strong>VT Status message</strong>를 1초 주기로 전체 브로드캐스트하고(요청-응답이 아니다), 각 WS는 <strong>Working Set Maintenance message</strong>를 1초 주기로 VT에 보낸다. 어느 쪽이든 <strong>3초간</strong> 끊기면 상대의 셧다운(shutdown, 꺼짐)으로 판정한다.

- 작업기 ECU는 안전 상태(safe state)로 진입한다. 안전 상태는 VT 화면이 없어도 사람과 기계가 위험하지 않은, 미리 정해 둔 상태다.
- VT는 unexpected shutdown(예기치 않은 종료)을 운전자에게 경보한 뒤 해당 풀을 휘발성 메모리(전원이 꺼지면 내용이 사라지는 메모리)에서 삭제한다.

무전기로 1초마다 "여기 있다"고 말을 주고받다가, 3초 동안 아무 말이 없으면 상대가 사라졌다고 보는 것과 같다. 경보를 띄우지 않는 예외, 메시지의 바이트, 키를 껐을 때의 처리는 [31장](/study/isobus/31-vt-connection)에서 본다.

::: tip 정리
- 동작 순서는 오브젝트 풀 전송 → 렌더링 → 상호작용이다.
- VT Status(VT → 모두)와 Working Set Maintenance(작업기 → VT)가 1초마다 오가며 연결을 지킨다. 3초 끊기면 상대가 꺼진 것으로 본다.
:::

## 4. VT 버전

이 절에서는 VT 버전이 무엇이고, 버전이 다른 VT와 작업기가 어떻게 함께 동작하는지 본다.

ISO 11783-6은 지속적으로 개정되어 왔으며, VT Server와 Client가 지원하는 <strong>버전(Version)</strong>에 따라 사용 가능한 기능이 달라진다. 판(edition)은 표준 문서가 다시 발행된 차례이고, VT 버전은 VT와 작업기가 지원하는 기능 수준을 나타내는 번호다. 아래 표처럼 한 판에서 버전이 둘 나오기도 해서 둘은 1:1로 맞지 않는다.

| 버전 | 주요 특징 |
|------|-----------|
| **Version 2** | 초판(2004) 기준 기본 기능: 기본 오브젝트 타입, 256색 표준 팔레트, 구형 AUX(Type 1) |
| **Version 3** | 2판(2010): 새 AUX 프로토콜(Type 2, AUX-N) 도입, initiating bit 등 연결 관리 보강 |
| **Version 4** | 2판(2010): Window Mask·Key Group(여러 Working Set 동시 표시), Graphics Context, 커맨드 응답을 발신자에게 직접 전송 |
| **Version 5** | 3판(2014): Animation, External Object(Working Set 간 오브젝트 참조), Extended Version 명령, Auxiliary Capabilities, Unsupported VT Function message |
| **Version 6** | 4판(2018): Data Mask 최소 480×480·소프트키 최소 60×60, Colour Palette·Graphic Data·Scaled Graphic 오브젝트, AUX 입력 잠금(lock) 상태 |

표의 낯선 이름은 뒤 장에서 하나씩 나온다. 지금은 "버전이 올라갈수록 쓸 수 있는 오브젝트와 명령이 늘었다"는 것만 기억하면 된다.

VT Server와 Client가 서로 다른 버전을 지원할 경우 별도의 협상 절차는 없다. 협상(negotiation)은 양쪽이 주고받으며 쓸 버전을 정하는 절차인데, VT에는 이런 절차가 없다. 클라이언트가 <strong>Get Memory response 등 기술 데이터 메시지</strong>로 VT의 버전을 확인한 뒤, 자신이 VT 버전에 맞춰 오브젝트 풀과 사용 커맨드를 조정하는 <strong>일방향 적응</strong>이다.

- 낮은 버전 VT에 높은 버전 메시지를 보내서는 안 된다.
- 반대로 VT가 더 높은 버전이면 하위 호환으로 그대로 동작한다. 하위 호환(backward compatibility)은 새 버전이 옛 버전의 동작을 그대로 지원한다는 뜻이다.
- Working Set Maintenance message에 보고하는 버전은 WS가 설계된 버전이며, VT에 맞춘 런타임 적응 때문에 바뀌지 않는다.

예를 들어 version 5로 설계한 작업기가 version 4 VT를 만나면 아래처럼 된다.

![VT가 Get Memory response로 버전 4를 보고하고, Version 5로 설계한 ECU가 풀과 커맨드를 v4에 맞게 조정해 Version 4 기능 범위로 동작하는 흐름](/images/study-isobus/29-version-adaptation-light.png)
![VT가 Get Memory response로 버전 4를 보고하고, Version 5로 설계한 ECU가 풀과 커맨드를 v4에 맞게 조정해 Version 4 기능 범위로 동작하는 흐름](/images/study-isobus/29-version-adaptation-dark.png)

작업기는 version 5에서 생긴 기능(예: Animation)을 빼고 동작한다. 그래도 Working Set Maintenance에는 자기 설계 버전인 5를 계속 보고한다.

::: tip 정리
- VT 버전은 2~6이 있고, 버전마다 쓸 수 있는 오브젝트와 메시지가 다르다.
- 버전 협상은 없다. 작업기가 VT 버전을 읽고 자기 풀과 명령을 거기에 맞춘다(일방향 적응).
- 작업기가 보고하는 자기 버전은 설계된 버전이고, VT에 맞춰 바꾸지 않는다.
:::

## 5. 버전 번호를 바이트로 읽기 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절에서는 버전 번호가 실제 메시지의 어느 바이트에 어떤 값으로 실리는지, 메시지마다 언제 도입됐는지, version 6 VT가 무엇을 보고해야 하는지 본다. 이 장에서 "원문"은 ISO 11783-6 표준 문서 자체를 말한다.

### 버전 번호가 오가는 두 필드

VT 버전과 WS 버전은 서로 다른 메시지로, 서로 다른 인코딩으로 오간다. 둘을 같은 정수로 다루면 버그가 난다. 표의 "Byte 2"는 8바이트 메시지의 두 번째 바이트다. 바이트 번호는 1부터 센다.

| 방향 | 필드 | 값 |
|---|---|---|
| VT → WS | Get Memory response Byte 2 | 0 = Hannover Agritechnica 2001 한정 기능판, 1 = 2002 FDIS, 2 = 2004 초판, 3·4 = 2010 2판, 5 = 2014 3판, 6 = 2018 4판 |
| WS → VT | Working Set Maintenance Byte 3 | 3~6 = 해당 버전 준수, `FF` = version 2 이하 준수, 0~2·7~`FE` = 예약 |

0은 2001년 하노버 농기계 박람회(Agritechnica)용으로 기능을 줄여 만든 판이고, FDIS(Final Draft International Standard)는 정식 발행 직전의 최종 초안이다. 예약(reserved)은 지금은 뜻이 없고 나중을 위해 비워 둔 값이다.

- 3과 4는 같은 2판(2010)에서 함께 도입됐다. 판(edition)과 버전 번호가 1:1이 아니다.
- WS 쪽에는 "2"라는 값이 없다. version 2 이하 WS는 `FF`(=255)를 보낸다. `FF`는 "이 칸에 줄 값이 없다"는 뜻으로 자주 쓰는 특수값이고, 여기서는 버전 칸이 없던 시절의 WS를 뜻한다. VT가 이 바이트를 그대로 정수 비교하면 v2 WS를 "버전 255", 즉 가장 새로운 WS로 오판한다.
- 버전은 하위 호환이라 버전 N용 WS가 N보다 높은 VT를 따로 다룰 필요는 없다. 원문은 낮은 버전을 구현하더라도 최신 판 문서를 기준으로 삼으라고 권한다.

### 메시지마다 도입된 버전

VT 메시지는 첫 바이트(Byte 1)의 VT function 코드로 종류를 가린다. 메시지마다 처음 도입된 VT 버전이 정해져 있다(뒤 판에서 내용이 바뀐 메시지도 있다). WS는 Get Memory response로 읽은 VT 버전보다 높은 버전의 메시지를 보내면 안 된다.

아래 표는 이 장과 [30장](/study/isobus/30-vt-display-technical-data), [31장](/study/isobus/31-vt-connection)에서 쓰는 기술 데이터·비휘발성 메모리·상태 메시지만 골랐다. 코드는 16진수다. 예를 들어 `0xC0`은 10진수 192, `0xFE`는 254, `0xFF`는 255다.

| 도입 버전 | 기술 데이터·비휘발성 메모리·상태 메시지(VT function) |
|---|---|
| 2 | Get Memory(`0xC0`), Get Number of Soft Keys(`0xC2`), Get Text Font Data(`0xC3`), Get Hardware(`0xC7`), Get Versions(`0xDF`, 응답 `0xE0`), Store·Load·Delete Version(`0xD0`~`0xD2`), VT Status(`0xFE`), Working Set Maintenance(`0xFF`) |
| 4 | Get Supported Widechars(`0xC1`), Get Window Mask Data(`0xC4`), Get Supported Objects(`0xC5`), Identify VT(`0xBB`) |
| 5 | Extended Get·Store·Load·Delete Version(`0xD3`~`0xD6`), Unsupported VT Function·VT Unsupported VT Function(`0xFD`) |
| 6 | Screen Capture(`0xC6`) |

### version 6가 하드웨어에 요구하는 것

원문은 version 6 VT에 하드웨어와 파싱 요구를 따로 건다. VT의 특성은 기술 데이터 메시지(작업기가 VT의 능력을 묻는 메시지)의 응답으로 드러난다. 그래서 요구를 "어느 응답의 어느 바이트에 무엇이 보여야 하는가"로 바꿔 읽으면 VT 서버 에뮬레이터의 점검표가 된다. 에뮬레이터(emulator)는 PC에서 VT처럼 동작하는 시험용 프로그램이다. 각 응답의 바이트 배치는 [30장](/study/isobus/30-vt-display-technical-data)에서 본다.

| version 6 요구 | 드러나는 곳 | v6 VT가 보고할 값 |
|---|---|---|
| 물리 Soft Key 최소 60 × 60(정사각형 권장) | Get Number of Soft Keys response Byte 5·6 | 둘 다 60(`0x3C`) 이상 |
| small·large 폰트 크기 전부 | Get Text Font Data response Byte 6·7 | 각각 `0x7F`(bit 0~6 전부, bit 7은 예약) |
| font style 전부 | 같은 응답 Byte 8 | bit 0~6 전부 1. bit 7(비례 폰트 렌더링)이 "모든 font style"에 들어가는지는 원문이 따로 밝히지 않는다(확인 필요) |
| 최소 256색, 16bit 이상 권장 | Get Hardware response Byte 3 | 2(256 colour). 16bit 하드웨어인지는 이 필드로 드러나지 않는다. VT는 하드웨어에 맞춰 표현을 낮출 수 있다(예: 24bit PNG를 16bit로) |
| Data Mask 최소 480 × 480 | Get Hardware response Byte 5~8 | X·Y 모두 480(`E0 01`) 이상 |
| Window Mask·Key Group: 완전 파싱, 표시는 선택 | Get Supported Objects 목록 | 목록에 없어도 파싱은 해야 한다 |
| Graphics Context: 표시까지 완전 지원 | Get Supported Objects 목록 | 표시를 지원해야 하므로 목록에 type 36이 들어가는 것이 자연스럽다(추론) |

표를 읽는 데 필요한 것 네 가지만 덧붙인다.

- 비례 폰트(proportional font)는 글자마다 폭이 다른 글꼴이다. 예를 들어 i는 좁고 W는 넓게 그린다.
- `0x7F`는 2진수 `0111 1111`이다. bit 0~6이 모두 1이므로 "크기 7가지를 모두 지원한다"는 뜻이다. 비트 번호는 오른쪽 끝(가장 낮은 자리)이 bit 0이다.
- `E0 01`은 두 바이트 숫자를 낮은 자리 바이트부터 적은 것(리틀 엔디언)이다. 뒤집으면 `0x01E0` = 480이다.
- type 36은 Graphics Context 오브젝트의 종류 번호다. 오브젝트 종류 번호는 [32장](/study/isobus/32-vt-object-pool-basics)에서 표로 본다.

<small>근거: ISO 11783-6 4.1.1, 4.6.2, 4.6.28, D.3, G.3, Table A.5</small>

## 6. AUX: 보조 입력

이 절에서는 화면 밖의 조이스틱이나 버튼을 작업기 기능에 연결하는 AUX의 개념을 본다. 메시지와 바이트의 세부는 [40장](/study/isobus/40-vt-aux)에서 다룬다.

<strong>AUX(Auxiliary Input)</strong>는 조이스틱, 추가 버튼 패드, 풋 페달 등 VT 디스플레이 외부의 보조 입력 장치를 ISOBUS에 통합하는 메커니즘이다. ISO 11783-6에 정의되어 있다.

예를 들어 운전자가 조이스틱의 3번 버튼을 스프레이어의 "붐 접기"에 쓰고 싶다고 하자. 조이스틱 제조사와 스프레이어 제조사가 달라도, 둘 다 AUX 규칙을 따르면 VT 화면에서 "3번 버튼 = 붐 접기"로 이어 줄 수 있다.

현재 표준에서 사용되는 버전은 <strong>AUX-N</strong>(New AUX, 표준의 Type 2, version 3 이상)으로, 기존 AUX-O(Old AUX, Type 1, version 2)를 대체했다. 두 프로토콜은 서로 호환되지 않는다.

### AUX 구성 요소

| 구성 요소 | 설명 |
|-----------|------|
| **AUX Input Unit** | 물리적 입력 장치 (조이스틱, 버튼 등) |
| **AUX Function** | 작업기 ECU가 정의하는 논리적 기능 (예: "살포 시작") |
| **Assignment** | 입력 유닛의 특정 입력과 ECU 기능을 연결하는 매핑 |

매핑(mapping)은 "이 입력은 이 기능"이라고 짝을 지어 둔 것이다. 이 짝을 할당(assignment)이라고 부른다.

### Preferred Assignment: 지난번 짝을 기억해 두기

AUX의 핵심 개념 중 하나는 <strong>Preferred Assignment</strong>(선호 할당)이다. 사용자가 한 번 입력 장치와 기능의 매핑을 설정하면, <strong>기능을 제공하는 WS(작업기 ECU)</strong>가 그 할당을 선호 할당으로 저장한다. 다음에 같은 작업기를 연결하면 WS가 Preferred Assignment command로 저장된 할당을 VT에 전달하고, VT가 이를 검증한 뒤 적용해 <strong>이전 매핑이 자동으로 복원</strong>된다.

![AUX Input Unit(조이스틱)과 작업기 ECU가 각자 오브젝트 풀을 VT에 올린 뒤, 작업기가 Preferred Assignment command로 저장해 둔 할당을 전달하고, VT가 할당을 검증해 입력 유닛에는 AUX Input Status Enable을, 작업기에는 AUX Assignment command를 보낸다. 매핑이 끝나면 입력 유닛의 AUX Input Type 2 Status가 VT를 거치지 않고 작업기로 브로드캐스트된다](/images/study-isobus/29-aux-preferred-assignment-light.png)
![AUX Input Unit(조이스틱)과 작업기 ECU가 각자 오브젝트 풀을 VT에 올린 뒤, 작업기가 Preferred Assignment command로 저장해 둔 할당을 전달하고, VT가 할당을 검증해 입력 유닛에는 AUX Input Status Enable을, 작업기에는 AUX Assignment command를 보낸다. 매핑이 끝나면 입력 유닛의 AUX Input Type 2 Status가 VT를 거치지 않고 작업기로 브로드캐스트된다](/images/study-isobus/29-aux-preferred-assignment-dark.png)

그림의 순서는 다음과 같다.

1. 입력 장치와 작업기가 각자 오브젝트 풀을 VT에 올린다. 입력 장치의 풀에는 "나는 이런 입력을 갖고 있다"(AUX Input 오브젝트)가, 작업기의 풀에는 "나는 이런 기능을 갖고 있다"(AUX Function 오브젝트)가 들어 있다.
2. 작업기가 저장해 둔 짝을 Preferred Assignment command로 VT에 건넨다.
3. VT가 기능과 입력의 종류가 맞는지, 다른 할당과 부딪히지 않는지 검증한다.
4. VT가 입력 장치에는 상태 전송을 켜라고 알리고(AUX Input Status Enable), 작업기에는 할당이 확정됐다고 알린다(AUX Assignment command).
5. 그 뒤 조이스틱을 움직이면 입력 장치가 상태를 브로드캐스트하고, 작업기가 직접 받아 기능을 실행한다.

할당이 완료되면 입력값은 VT를 거치지 않는다. AUX Input Unit이 <strong>Auxiliary Input Type 2 Status message</strong>를 초당 1회(값 변경 시 즉시, 최대 20 Hz)로 전체 브로드캐스트하면, 할당된 기능의 WS가 이를 직접 수신해 실행한다. 20 Hz는 1초에 20번이다.

입력 유닛은 별도로 Auxiliary Input Type 2 Maintenance message를 100 ms 주기로 브로드캐스트하며, 300 ms 동안 끊기면 VT와 기능 측 WS가 그 유닛의 할당을 제거한다. 다중 VT 환경에서 할당·검증은 <strong>function instance 0 VT</strong>만 수행한다. function instance 0 VT는 네트워크에 VT가 여럿일 때 번호가 0인 VT, 즉 [31장](/study/isobus/31-vt-connection)에서 볼 primary VT다.

::: tip 정리
- AUX는 조이스틱 같은 화면 밖 입력 장치를 작업기 기능에 연결한다. 지금 쓰는 방식은 AUX-N(Type 2)이다.
- 짝(할당)은 기능을 가진 WS가 Preferred Assignment로 저장했다가 다음 연결 때 VT에 건네 복원한다.
- 할당이 끝나면 입력값은 VT를 거치지 않고 브로드캐스트되어 작업기가 직접 받는다.
:::

<small>근거: ISO 11783-6 Annex J</small>

## 7. VT 연결 따라가기

3절과 4절에서는 절차를 그림으로만 봤다. 여기서는 그 흐름을 <strong>메시지 단위로 실제 바이트까지</strong> 따라간다. 예제로 쓰는 오브젝트 풀은 [32장](/study/isobus/32-vt-object-pool-basics)의 "엔진 온도: 85°C" 화면이다. 그 풀을 이루는 5개 오브젝트(Working Set·Data Mask·Font Attributes·Output String·Output Number)의 바이트 구성도 32장에서 계산한다. 여기서는 그 결과(총 98바이트)가 VT에 오르기까지의 <strong>메시지 흐름</strong>만 본다.

### 표 읽는 법

- 방향 표기: VT→ECU 메시지는 <strong>PGN 58880(0xE600)</strong>, ECU→VT 메시지는 <strong>PGN 59136(0xE700)</strong>으로 오간다. PGN(Parameter Group Number)은 CAN 프레임에 실린 메시지의 종류를 가리키는 번호다([9장](/study/isobus/09-j1939-message)).
- 데이터 칸은 CAN 프레임에 실린 8바이트를 16진수로 적은 것이다. 왼쪽부터 Byte 1, Byte 2, …, Byte 8이다. Byte 1은 VT function 코드로, 어떤 VT 메시지인지 가린다(`FE` = VT Status, `FF` = Working Set Maintenance, `C0` = Get Memory 등).
- 두 바이트 이상으로 된 숫자는 리틀 엔디언(little endian)으로 적는다. 낮은 자리 바이트가 먼저 온다. 예를 들어 `62 00 00 00`은 `0x00000062` = 98이다.
- 예약 바이트는 지금은 쓰지 않고 나중을 위해 비워 둔 자리다. VT 메시지는 이 자리를 `FF`로 채운다.
- 8바이트보다 긴 데이터는 TP(Transport Protocol, 긴 데이터를 여러 프레임으로 나눠 보내는 규칙)로 보낸다. 아주 큰 데이터에는 확장판인 ETP를 쓴다.
- 시각은 설명 편의상 붙인 예시값이며 표준이 규정하는 절대 시각이 아니다(주기·타임아웃 규정 자체는 3절에 정리돼 있다). ECU(작업기) 소스 주소는 예시로 `0x81`을 쓴다.

### 타임라인

| 시각 | 방향 | PGN | 데이터(hex) | 의미 |
|---|---|---|---|---|
| t=0.000s | VT→ECU | 0xE600 | `FE FF FF FF FF FF 00 FF` | VT Status: 소유 WS 없음(Byte2=FF), busy 없음. 요청 없이 매초 브로드캐스트 |
| t=0.000s | ECU→VT | 0xE700 | `FF 01 04 FF FF FF FF FF` | Working Set Maintenance 최초 전송: Byte2 bit0=Initiating(1), Byte3=Version 4 |
| t=0.050s | ECU→VT | 0xE700 | `C0 FF 62 00 00 00 FF FF` | Get Memory: Memory Required = 98(0x62)바이트(풀 전체 크기), Byte1=함수코드 0xC0 |
| t=0.060s | VT→ECU | 0xE600 | `C0 04 00 FF FF FF FF FF` | Get Memory response: Version=4, Status=0(메모리 가능) |
| t=0.070s~ | ECU→VT | 0xE700 | (TP 다중 프레임, 총 99바이트: 함수코드 `11` + 오브젝트 레코드 98바이트) | Object Pool Transfer: 5개 오브젝트 레코드 전송(TP/ETP 분해는 [15장](/study/isobus/15-tp-bam-cmdt)과 [17장](/study/isobus/17-etp) 참고) |
| t=0.900s | ECU→VT | 0xE700 | `12 FF FF FF FF FF FF FF` | End of Object Pool: 전송 완료 통지 |
| t=0.901s | VT→ECU | 0xE600 | `FE FF FF FF FF FF 10 FF` | VT Status: Byte7 bit4(parsing)=1, 파싱 중 |
| t=1.9~3.9s | VT→ECU | 0xE600 | `FE FF FF FF FF FF 10 FF` ×3(매초) | 파싱이 끝나지 않아 parsing 비트 1 유지: VT는 End of Object Pool response를 보낼 때까지 이 비트를 1로 둔다 |
| t=3.910s | VT→ECU | 0xE600 | `12 00 FF FF FF FF 00 FF` | End of Object Pool response: Byte2 Error Codes=0(오류 없음), 결함 오브젝트 없음(FFFF) |
| t=3.920s | VT→ECU | 0xE600 | `FE 81 01 00 FF FF 00 FF` | VT Status: Byte2=0x81(ECU가 소유), Byte3,4=Data Mask ID 1, Byte5,6=Soft Key Mask 없음(FFFF, 이 풀은 `soft_key_mask="65535"`). 화면 표시 완료 |

Working Set Maintenance는 표에는 최초 1회만 적었지만 연결 내내 1초 주기로 계속 나간다. Get Memory 메시지의 Byte2·7~8과 응답의 Byte4~8은 표준 원문(ISO 11783-6)이 예약(Reserved)으로 정하고 `FF`로 채우게 한 바이트라 `FF`로 채웠다.

### 프레임 두 개를 바이트 단위로 읽기

<strong>Get Memory `C0 FF 62 00 00 00 FF FF`</strong>

1. Byte 1 `C0`: VT function 192(`0xC0`), Get Memory다.
2. Byte 2 `FF`: 예약.
3. Byte 3~6 `62 00 00 00`: Memory Required. 리틀 엔디언이므로 뒤집어 `00 00 00 62`로 읽으면 `0x62` = 98바이트다. 올릴 풀의 크기다.
4. Byte 7~8 `FF FF`: 예약.

<strong>마지막 VT Status `FE 81 01 00 FF FF 00 FF`</strong>

1. Byte 1 `FE`: VT Status다.
2. Byte 2 `81`: 지금 VT를 "소유"한 WS, 즉 화면에 보이면서 입력도 받는 WS의 주소다. 우리 작업기(`0x81`)다.
3. Byte 3~4 `01 00`: 보이는 Data Mask의 Object ID(오브젝트 번호) = 1이다.
4. Byte 5~6 `FF FF`: 보이는 Soft Key Mask가 없다. `0xFFFF`는 "가리키는 오브젝트 없음"을 뜻하는 특수 번호(NULL)다.
5. Byte 7 `00`: VT가 바쁜 일을 표시하는 busy 비트가 모두 0이다.
6. Byte 8 `FF`: 실행 중인 명령이 없다.

### 왜 이 순서인가

- <strong>VT Status는 요청-응답이 아니다.</strong> 타임라인 첫 줄부터 VT가 먼저 말을 걸고, ECU가 아직 아무것도 안 보냈는데도 계속 브로드캐스트된다. ECU 입장에서는 이 메시지의 존재 자체가 "VT가 살아 있다"는 유일한 신호다.
- Get Memory로 <strong>버전과 메모리 여유를 먼저 확인</strong>한 뒤에야 풀을 올린다. 무효 풀을 먼저 보내고 나중에 고치는 방식은 허용되지 않는다([32장](/study/isobus/32-vt-object-pool-basics)의 "전송 완료 대기와 오류 처리" 참고).
- End of Object Pool 이후의 대기는 <strong>폴링이 아니라 패턴 관찰</strong>이다. 폴링(polling)은 "끝났어?"라고 계속 묻는 방식이다. 여기서는 묻지 않고 VT Status의 parsing 비트를 지켜본다. parsing 비트가 0인 상태가 연속 3번 나온 뒤에도 response가 없어야 "메시지가 VT에 안 갔다"고 확정한다.
- 3번을 기다리는 이유는 경쟁 상태(race condition)를 피하려는 것이다. 경쟁 상태는 두 일이 거의 같은 때 일어나 순서에 따라 결과가 달라지는 상황이다. 여기서는 VT가 파싱을 시작하기 전에 송신 큐에 넣어 둔 VT Status가 늦게 나가서, 파싱 중인데도 parsing = 0으로 보이는 경우다.
- 마지막 VT Status는 이전 상태들과 <strong>Byte2~6이 다르다</strong>. 이 변화(소유자·활성 마스크 지정)가 바로 "화면이 떴다"는 것을 ECU가 확인하는 방법이다.

::: tip 정리
- VT Status·Working Set Maintenance는 연결 전 과정에서 요청 없이 계속 흐르는 <strong>배경 신호</strong>다. Object Pool Transfer·Get Memory 같은 "용건이 있는" 메시지들은 이 배경 신호 위에 얹혀 지나갈 뿐이다.
- End of Object Pool response를 기다리는 조건은 <strong>"parsing=0 상태가 연속 3번"</strong>이지 "N초가 지났다"가 아니다. 파싱이 오래 걸리는 큰 풀일수록 이 규칙의 의미가 커진다.
:::

::: details 파이썬으로 바이트 구성 검산해 보기
아래 코드는 타임라인의 프레임을 직접 조립해, 표와 같은 바이트가 나오는지 `assert`로 확인한다.

```python
def le(v, n):
    return v.to_bytes(n, "little")


# VT Status: 소유 WS 없음
vt_status_idle = bytes([0xFE, 0xFF]) + b"\xFF" * 4 + bytes([0x00, 0xFF])
assert vt_status_idle.hex(" ").upper() == "FE FF FF FF FF FF 00 FF"

# Working Set Maintenance: 최초 전송(Initiating=1), Version 4
wsm_first = bytes([0xFF, 0b00000001, 4]) + b"\xFF" * 5
assert wsm_first.hex(" ").upper() == "FF 01 04 FF FF FF FF FF"

# Get Memory: Memory Required = CH16 §6에서 계산한 풀 전체 크기
memory_required = 10 + 20 + 8 + 31 + 29  # Working Set + Data Mask + Font Attr + Output String + Output Number
assert memory_required == 98
get_memory = bytes([0xC0, 0xFF]) + le(memory_required, 4) + b"\xFF\xFF"
assert get_memory.hex(" ").upper() == "C0 FF 62 00 00 00 FF FF"

# VT Status: parsing 비트(Byte7 bit4) = 1
vt_status_parsing = bytes([0xFE, 0xFF]) + b"\xFF" * 4 + bytes([0b00010000, 0xFF])
assert vt_status_parsing.hex(" ").upper() == "FE FF FF FF FF FF 10 FF"

# End of Object Pool response: 오류 없음
eop_resp = bytes([0x12, 0x00]) + b"\xFF\xFF\xFF\xFF" + bytes([0x00, 0xFF])
assert eop_resp.hex(" ").upper() == "12 00 FF FF FF FF 00 FF"

# VT Status: 연결 완료, ECU(0x81)가 소유, Data Mask ID=1, Soft Key Mask 없음
vt_status_final = bytes([0xFE, 0x81]) + le(1, 2) + le(0xFFFF, 2) + bytes([0x00, 0xFF])
assert vt_status_final.hex(" ").upper() == "FE 81 01 00 FF FF 00 FF"

print("모든 프레임 검증 통과")
```

실행하면 `모든 프레임 검증 통과`가 출력된다. 주석의 "CH16 §6"은 옛 장 번호로, 지금의 [32장](/study/isobus/32-vt-object-pool-basics)에서 오브젝트 레코드 크기를 계산하는 부분을 가리킨다. `le()`는 숫자를 리틀 엔디언 바이트로 바꾸는 도우미 함수다.
:::

<small>근거: ISO 11783-6 C.2.2, D.2, D.3</small>

::: tip 핵심 정리
- VT는 트랙터 운전석의 공용 화면이다. 화면 하드웨어는 트랙터(VT Server)가, 화면 내용은 작업기 ECU(VT Client)가 오브젝트 풀로 정한다.
- 작업기는 연결할 때 오브젝트 풀을 VT에 통째로 올리고, 그 뒤로는 짧은 명령으로 화면 값을 바꾼다. 운전자 입력은 VT가 작업기에 알린다.
- 연결은 VT Status와 Working Set Maintenance가 각각 1초마다 오가며 유지된다. 3초 끊기면 상대가 꺼진 것으로 본다.
- VT 버전(2~6)마다 쓸 수 있는 기능이 다르고, 작업기가 VT 버전을 확인해 자기 쪽을 맞춘다(일방향 적응).
- AUX-N은 조이스틱 같은 보조 입력을 작업기 기능에 연결한다. 할당은 기능을 가진 WS가 Preferred Assignment로 저장했다가 복원하고, 입력값은 VT를 거치지 않고 브로드캐스트된다.
:::

::: details 확인 문제
1. VT Server와 VT Client는 각각 어느 장치이고 무엇을 맡는가?
2. 웹 브라우저 비유에서 오브젝트 풀은 무엇에 해당하는가? 이 비유가 VT와 맞지 않는 점을 두 가지 들어라.
3. 작업기 ECU가 VT Status를 3초 동안 받지 못하면 무엇을 해야 하는가? 반대로 VT가 Working Set Maintenance를 3초 동안 받지 못하면 무엇을 하는가?
4. version 5로 설계한 작업기가 Get Memory response로 VT 버전 4를 읽었다. 작업기는 무엇을 하고, Working Set Maintenance Byte 3에는 몇을 보내는가?
5. (디코딩) VT가 보낸 `C0 04 00 FF FF FF FF FF`를 읽어라. 어떤 메시지이고, VT 버전과 메모리 상태는 무엇인가?
6. (심화) Working Set Maintenance Byte 3이 `FF`인 WS를 VT가 "버전 255"로 읽으면 어떤 문제가 생기는가?

**답 가이드**
1. VT Server는 트랙터 운전석의 디스플레이로, 화면을 그리고 운전자 입력을 받는다. VT Client는 작업기 ECU로, 화면 내용(오브젝트 풀)을 정해 보내고 값을 갱신한다.
2. 웹 페이지(HTML)에 해당한다. 맞지 않는 점은 다음 가운데 두 가지를 들면 된다. 풀은 연결할 때 통째로 미리 올리고 그 뒤로는 짧은 명령만 오간다. 화면을 바꾸는 쪽이 작업기다. 풀에는 계산하는 프로그램이 없다. 서로 1초마다 살아 있음을 알리고 3초 끊기면 VT가 경보하고 화면을 지운다. VT는 지원하지 않는 기능이 든 풀을 거부한다.
3. 작업기는 VT가 꺼진 것으로 보고 안전 상태에 들어간다. VT는 작업기의 unexpected shutdown으로 보고 운전자에게 경보한 뒤 그 풀을 휘발성 메모리에서 지운다. 경보하지 않는 예외는 [31장](/study/isobus/31-vt-connection)에서 본다.
4. 풀과 명령을 version 4 기능 범위로 맞춰 동작한다(일방향 적응). Working Set Maintenance Byte 3에는 설계 버전인 5(`05`)를 그대로 보낸다.
5. Byte 1 `C0`이므로 Get Memory response다(VT→ECU, PGN 58880). Byte 2 `04`는 VT 버전 4, Byte 3 `00`은 Status 0, 즉 메모리가 충분할 수 있어 풀을 보내도 된다는 뜻이다. 나머지는 예약 `FF`다.
6. version 2 이하 WS가 가장 새로운 WS로 오판된다. 그러면 VT가 그 WS에 높은 버전 메시지를 보내거나, 버전 조합으로 정하는 응답 목적지를 잘못 고를 수 있다([30장](/study/isobus/30-vt-display-technical-data)). Byte 3이 `FF`면 "version 2 이하"로 읽어야 한다.
:::

## 다음 챕터

- 다음: [30장 VT 화면 구성과 기술 데이터](/study/isobus/30-vt-display-technical-data)
