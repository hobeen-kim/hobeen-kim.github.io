---
title: "CH3. Control Function과 NAME"
description: "주소가 아닌 NAME으로 장치를 식별하는 이유와, 64비트 NAME의 9가지 구성요소"
date: 2026-07-20
tags: [AgIsoStack, ISOBUS, NAME, ControlFunction, AddressClaiming]
---

# CH3. Control Function과 NAME

## 학습 목표

- 주소만으로 장치를 식별하면 안 되는 이유를 설명할 수 있다
- Control Function이 무엇이고 NAME과 어떤 관계인지 안다
- 64비트 NAME을 구성하는 9가지 요소가 각각 무엇을 의미하는지 구분한다
- 주소 클레임이 NAME과 주소를 어떻게 묶는지 이해한다

## 주소만으로는 부족하다

앞 챕터에서 1바이트 주소를 살펴봤다. 그런데 <strong>현실적으로 주소는 CAN 프레임을 채우거나 해석하는 것 말고는 거의 쓸모가 없다.</strong>

주소는 그 장치에 대해 아무것도 말해 주지 않는다.

- 그 장치의 <strong>정체</strong>가 무엇인지
- <strong>무슨 일</strong>을 하는 장치인지
- <strong>누가 만들었는지</strong>
- 심지어 <strong>내가 말을 걸어도 되는 상대인지</strong>

게다가 메시지를 보내는 수단으로도 신뢰할 수 없다. <strong>J1939와 ISOBUS 장치는 언제든 주소를 바꿀 수 있기 때문</strong>이다. 어제 0x26이었던 살포기가 오늘도 0x26이라는 보장이 없다.

## Control Function

그래서 J1939와 ISO 11783은 CAN 네트워크의 기본 구성 단위를 <strong>Control Function(제어 기능, 줄여서 CF)</strong>으로 정의한다.

::: tip Control Function의 정의
Control Function은 주소를 갖지만, <strong>무엇보다 먼저 NAME으로 식별된다</strong>. 그리고 그 주소는 주소 클레임과 중재라는 과정을 통해 <strong>언제든 바뀔 수 있다</strong>.
:::

AgIsoStack++에서 이 개념은 그대로 클래스 이름이 된다. 내 장치를 나타내는 `InternalControlFunction`, 상대 장치를 나타내는 `PartneredControlFunction` 같은 타입들이 전부 이 정의를 따른다. 애플리케이션은 주소 값이 아니라 <strong>Control Function 객체를 붙잡고 통신</strong>하고, 그 뒤에서 주소가 바뀌는 것은 스택이 알아서 따라간다.

## NAME

<strong>NAME은 네트워크 상에서 Control Function을 유일하게 식별하는 64비트 값</strong>이다. 주소가 임시 번호라면 NAME은 주민등록번호에 가깝다.

NAME은 다음 요소들로 구성된다.

![NAME 64비트 구성 — Identity Number(21비트), Manufacturer Code(11비트), ECU Instance(3비트), Function(8비트), Function Instance(5비트), Device Class(7비트), Device Class Instance(4비트), Industry Group(3비트), Arbitrary Address Capable(1비트) 9개 필드와 예약 1비트](/images/study-agisostack/03-name-fields-light.png)
![NAME 64비트 구성 — Identity Number(21비트), Manufacturer Code(11비트), ECU Instance(3비트), Function(8비트), Function Instance(5비트), Device Class(7비트), Device Class Instance(4비트), Industry Group(3비트), Arbitrary Address Capable(1비트) 9개 필드와 예약 1비트](/images/study-agisostack/03-name-fields-dark.png)

### Identity Number

<strong>보통 Control Function의 일련번호</strong>다. NAME의 나머지 값이 전부 같은 Control Function들 사이에서 <strong>서로 구별되도록</strong> 유일한 값이어야 한다.

같은 모델 트랙터 두 대가 같은 버스에 붙는 상황을 생각하면 이해가 쉽다. 제조사도 기능도 장치 종류도 같으니, 결국 이 값으로 갈린다.

### Manufacturer Code

<strong>누가 이 Control Function을 만들었는지</strong>를 식별한다. 값은 임의로 정하는 게 아니라 등록된 목록에서 가져온다.

- 제조사 코드 목록: <https://www.isobus.net/isobus/manufacturerCode>

### ECU Instance

<strong>비슷한 NAME을 가진 Control Function들 사이에서 NAME 순서대로 증가하는 값</strong>이다. 이름이 비슷한 장치가 여러 개 있을 때, ISO NAME 안에서 <strong>서열을 세우는 데</strong> 쓴다.

### Function

<strong>이 Control Function이 무슨 일을 하는지</strong>를 나타낸다. ISO 11783은 여기에 들어갈 수 있는 기능 목록을 정의해 두었고, 그 종류가 상당히 많다.

- 기능 목록: <https://www.isobus.net/isobus/nameFunction>

### Function Instance

<strong>해당 ECU의 기능 인스턴스</strong>다. Virtual Terminal 번호와 비슷한 개념이라고 보면 된다. 같은 기능을 하는 장치가 여럿일 때 몇 번째인지를 나타낸다.

### Device Class

<strong>J1939에서 "vehicle system"이라고 부르던 것</strong>과 같다. "Sprayers(살포기)"나 "Backhoe(백호)"처럼 <strong>ECU의 일반적인 종류</strong>를 나타낸다.

### Device Class Instance

<strong>이 장치 종류의 인스턴스 번호</strong>다. ECU Instance와 비슷하게, 필요할 때 <strong>비슷한 NAME들 사이의 서열</strong>을 세우는 데 쓴다.

### Industry Group

<strong>이 ECU가 속한 산업 그룹</strong>이다. "agricultural(농업)" 같은 값이 들어간다.

- 참고: <https://www.isobus.net/isobus/nameFunction>

### Arbitrary Address Capability

<strong>이 ECU가 주소 중재(address arbitration)를 지원하는지</strong>를 나타낸다. 1비트짜리 플래그다.

이 값이 참이면, 원하던 주소를 다른 장치에 뺏겼을 때 다른 주소를 찾아 다시 시도할 수 있다. 거짓이면 정해진 주소를 쓰지 못할 경우 통신을 포기하게 된다.

## Address Claiming

J1939와 ISOBUS는 <strong>address claiming(주소 클레임)</strong>이라는 과정을 정의한다. 이 과정은 <strong>Control Function의 NAME을 기준으로 매우 결정론적으로 주소를 할당</strong>한다.

![주소 클레임 흐름 — NAME 준비(제조사·기능·시리얼로 64비트 구성) → 희망 주소 클레임(NULL 0xFE에서 출발해 원하는 주소를 브로드캐스트) → 충돌 중재(같은 주소를 원하면 NAME 값이 작은 쪽이 승리) → 주소 확정(진 CF는 다른 주소 재시도). 전 과정을 라이브러리가 자동 처리한다](/images/study-agisostack/03-address-claiming-light.png)
![주소 클레임 흐름 — NAME 준비(제조사·기능·시리얼로 64비트 구성) → 희망 주소 클레임(NULL 0xFE에서 출발해 원하는 주소를 브로드캐스트) → 충돌 중재(같은 주소를 원하면 NAME 값이 작은 쪽이 승리) → 주소 확정(진 CF는 다른 주소 재시도). 전 과정을 라이브러리가 자동 처리한다](/images/study-agisostack/03-address-claiming-dark.png)

<strong>라이브러리가 이 과정을 전부 대신 처리해 준다.</strong> 그래도 이 과정이 존재한다는 사실은 알아 둘 필요가 있다. <strong>NAME을 주소에 묶어 주는 것이 바로 이 과정</strong>이기 때문이다.

실제 코드에서 애플리케이션이 하는 일은 NAME 필드를 채워 넣고 희망 주소를 하나 지정하는 것까지다. 그 뒤로 클레임 메시지를 언제 보내고, 충돌이 나면 어떻게 재시도하고, 상대 장치의 주소 변화를 어떻게 추적할지는 스택의 몫이다.

::: info 관련 스터디
주소 클레임 메시지의 실제 형식과 중재 규칙, 그리고 Cannot Claim Address 같은 예외 흐름은 [ISOBUS CH10. J1939 주소 체계](/study/isobus/10-j1939-address)와 [CH14. ISOBUS 네트워크 관리](/study/isobus/14-isobus-network-mgmt)에서 다룬다.
:::

## 정리

지금까지의 관계를 한 줄로 이으면 이렇게 된다.

1. Control Function은 <strong>NAME에 의해 영구적으로 식별</strong>된다.
2. 이 NAME은 <strong>주소 클레임 과정에서 Control Function에 주소를 할당</strong>하는 데 쓰인다.
3. 이 주소는 <strong>영구적이지 않으며</strong>, 어떤 이유로든 주소 클레임이 다시 일어나면 언제든 바뀔 수 있다.

여기까지 이해했다면 첫 Control Function을 만들어 기본 메시지를 보내 볼 준비가 된 것이다. 바로 실습으로 넘어가고 싶다면 [CH7. ISOBUS Hello World](/study/agisostack/07-hello-world)로 건너뛰어도 되고, 개념을 더 쌓고 싶다면 다음 챕터로 계속 읽으면 된다.

::: tip 핵심 정리
- 주소는 프레임을 채우고 해석하는 용도 외에는 쓸모가 없다. 장치의 정체·기능·제조사를 알려 주지 않고, 언제든 바뀔 수 있다.
- 그래서 J1939와 ISO 11783은 네트워크의 기본 단위를 Control Function으로 정의하고, NAME으로 식별한다.
- NAME은 64비트이며 Identity Number, Manufacturer Code, ECU Instance, Function, Function Instance, Device Class, Device Class Instance, Industry Group, Arbitrary Address Capability로 구성된다.
- 주소 클레임은 NAME을 기준으로 결정론적으로 주소를 할당하며, 라이브러리가 전 과정을 자동 처리한다.
:::

## 원문 출처

- [AgIsoStack++ Documentation — Concepts: Control Functions](https://isobus-plus-plus.readthedocs.io/en/latest/Concepts.html#control-functions)

## 다음 챕터

[CH4. 전송 계층 개념](/study/agisostack/04-transport-concepts)으로 이어진다.
