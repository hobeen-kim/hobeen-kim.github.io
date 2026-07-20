---
title: "CH2. ISOBUS 핵심 개념"
description: "CAN 프레임과 32비트 식별자, PGN·소스 주소·목적지 주소·우선순위, 그리고 1바이트 주소 체계"
date: 2026-07-20
tags: [AgIsoStack, ISOBUS, CAN, PGN, J1939]
---

# CH2. ISOBUS 핵심 개념

라이브러리를 쓰기 전에 알아야 할 ISOBUS 기본 개념을 정리한다. ISO 11783을 이미 안다고 해도 한 번은 훑고 가는 편이 좋다. AgIsoStack++의 API 이름과 인자가 전부 여기 나오는 용어를 그대로 쓰기 때문이다.

## 학습 목표

- ISOBUS 네트워크가 물리적으로 어떤 버스인지 안다
- CAN 프레임의 32비트 식별자에 무엇이 들어 있는지 네 가지로 나눠 설명할 수 있다
- PGN·소스 주소·목적지 주소·우선순위가 각각 무슨 역할인지 구분한다
- 1바이트 주소 공간에서 255(0xFF)와 254(0xFE)가 왜 특별한지 안다

## ISOBUS 네트워크

<strong>ISOBUS 네트워크는 AEF의 ISO 11783 통신 표준을 따르는 250000 baud CAN 버스</strong>다. 그리고 ISO 11783 자체는 SAE의 J1939를 기반으로 만들어졌다. ISOBUS 표준은 농업 차량과 임업 장비를 위해 설계됐다.

여기서 중요한 건 세 겹의 관계다.

- <strong>CAN</strong> — 전기 신호와 프레임 형식을 정의하는 바닥층
- <strong>J1939</strong> — CAN 위에서 메시지 의미와 주소 관리를 정의하는 중간층
- <strong>ISO 11783 (ISOBUS)</strong> — J1939를 농기계 용도로 확장한 최상층

속도가 250kbit/s로 고정돼 있다는 점은 실무에서 자주 체감하게 된다. 초당 올릴 수 있는 프레임 수가 정해져 있으므로, 큰 데이터를 자주 보내는 설계는 버스를 금방 포화시킨다.

::: info 관련 스터디
CAN 물리 계층과 비트레이트가 어떻게 정해지는지는 [ISOBUS CH3. CAN 물리 계층](/study/isobus/03-can-physical)에서, ISOBUS가 J1939와 어떻게 다른지는 [CH12. ISOBUS 개요](/study/isobus/12-isobus-overview)에서 다룬다.
:::

## CAN 프레임에 무엇이 담기는가

이 라이브러리 관점에서 <strong>CAN 프레임은 최대 8바이트의 데이터와 32비트 식별자로 이루어진다</strong>. 그리고 이 식별자 안에 중요한 정보들이 들어 있다.

![CAN 프레임 구조 — 32비트 식별자에 우선순위·PGN·소스 주소·목적지 주소가 들어 있고, 별도로 최대 8바이트 데이터 페이로드가 있으며, 이들이 250kbit/s ISOBUS CAN 버스 위에서 트랙터 ECU·Virtual Terminal·살포기 ECU·GPS 수신기 사이를 오간다](/images/study-agisostack/02-can-identifier-light.png)
![CAN 프레임 구조 — 32비트 식별자에 우선순위·PGN·소스 주소·목적지 주소가 들어 있고, 별도로 최대 8바이트 데이터 페이로드가 있으며, 이들이 250kbit/s ISOBUS CAN 버스 위에서 트랙터 ECU·Virtual Terminal·살포기 ECU·GPS 수신기 사이를 오간다](/images/study-agisostack/02-can-identifier-dark.png)

식별자에 담기는 것은 다음 네 가지다.

### Parameter Group Number (PGN)

PGN은 <strong>데이터 페이로드 안에 무엇이 들어 있는지를 식별</strong>한다. 이메일의 제목 줄에 해당한다고 생각하면 된다. 제목을 보고 본문에 무슨 얘기가 있을지 알 수 있듯, PGN을 보면 그 8바이트가 속도 값인지 살포량 명령인지 알 수 있다.

대부분의 장치와 통신하려면 <strong>PGN 몇 개는 알고 있어야 하고, 필요하면 직접 정의해서 쓰기도 한다</strong>. 표준으로 정해진 PGN 목록은 isobus.net에서 조회할 수 있다.

- PGN 조회: <https://www.isobus.net/isobus/pGNAndSPN/?type=PGN>

### 소스 주소 (Source Address)

<strong>누가 이 메시지를 보냈는지</strong>를 나타낸다. 우편물의 발신인 주소에 해당한다. 수신 측 콜백에서 "이 값이 내가 관심 있는 장치에서 온 것인가"를 판단할 때 쓰인다.

### 목적지 주소 (Destination Address)

일부 메시지는 <strong>목적지를 지정</strong>할 수 있다. 반면 어떤 메시지는 모두가 받도록 되어 있는데, 이것이 브로드캐스트다.

여기서 헷갈리기 쉬운 부분이 하나 있다. <strong>어떤 메시지가 브로드캐스트인지 특정 주소로 가는지는 PGN이 결정한다.</strong> 보내는 쪽이 임의로 고르는 게 아니라, PGN마다 어느 형식인지 정해져 있다.

### 우선순위 (Priority)

버스에서 메시지가 충돌했을 때 <strong>어느 쪽이 이기고 어느 쪽이 나중에 다시 보내야 하는지</strong>를 결정한다.

우선순위는 <strong>일반적으로 소프트웨어가 아니라 하드웨어가 처리</strong>한다. 그래서 실무에서는 메시지를 보낼 때만 신경 쓰고, 받을 때는 거의 신경 쓸 일이 없다.

::: info 관련 스터디
충돌이 났을 때 우선순위 비트로 승자가 결정되는 원리(비트 단위 중재)는 [ISOBUS CH5. CAN 중재](/study/isobus/05-can-arbitration)에서, PGN이 식별자의 어느 비트에 어떻게 들어가는지는 [CH9. J1939 메시지 구조](/study/isobus/09-j1939-message)에서 자세히 다룬다.
:::

## 주소 체계

J1939 버스나 ISOBUS에서 메시지를 보내려면 <strong>버스 상에서 나를 식별하는 1바이트 주소</strong>가 필요하다. 마찬가지로, 브로드캐스트가 아닌 메시지를 보내려면 <strong>받는 쪽의 주소</strong>도 알아야 한다.

1바이트이므로 값의 범위는 0부터 255까지인데, 그중 끝의 두 개는 특별한 의미를 갖는다.

![1바이트 주소 공간 — 0~253은 제어 장치가 실제로 점유하는 주소이고 주소 클레임으로 확보하며 언제든 바뀔 수 있다. 254(0xFE)는 주소가 아직 없을 때 쓰는 NULL 주소, 255(0xFF)는 모두에게 보낼 때 쓰는 브로드캐스트 주소다](/images/study-agisostack/02-address-space-light.png)
![1바이트 주소 공간 — 0~253은 제어 장치가 실제로 점유하는 주소이고 주소 클레임으로 확보하며 언제든 바뀔 수 있다. 254(0xFE)는 주소가 아직 없을 때 쓰는 NULL 주소, 255(0xFF)는 모두에게 보낼 때 쓰는 브로드캐스트 주소다](/images/study-agisostack/02-address-space-dark.png)

| 주소 | 값 | 의미 |
|------|-----|------|
| 일반 주소 | 0 ~ 253 | 제어 장치가 주소 클레임으로 확보해 점유하는 주소 |
| <strong>NULL 주소</strong> | 254 (0xFE) | 주소가 없을 때, 또는 주소를 확보하는 중일 때 쓰는 주소 |
| <strong>브로드캐스트 주소</strong> | 255 (0xFF) | 모두에게 보내는 메시지의 목적지 주소 |

브로드캐스트는 <strong>항상 브로드캐스트 주소인 255(0xFF)로 전송</strong>된다.

NULL 주소는 <strong>내가 아직 주소를 갖고 있지 않을 때 쓰는 주소</strong>다. 부팅 직후 주소 클레임을 진행하는 동안이 여기에 해당한다. 다만 이 과정은 <strong>스택이 전부 자동으로 처리</strong>하므로, 애플리케이션 코드에서 NULL 주소를 직접 다룰 일은 거의 없다.

::: warning 주소를 신뢰하지 마라
주소는 프레임을 만들고 해석하는 데는 필요하지만, 장치를 식별하는 수단으로는 부적절하다. J1939와 ISOBUS 장치는 <strong>언제든 주소를 바꿀 수 있기 때문</strong>이다. 그래서 표준은 주소 대신 NAME이라는 별도의 식별자를 정의한다. 이 이야기는 다음 챕터에서 이어진다.
:::

::: tip 핵심 정리
- ISOBUS 네트워크는 ISO 11783을 따르는 250000 baud CAN 버스이고, ISO 11783은 SAE J1939를 기반으로 한다.
- 이 라이브러리 관점에서 CAN 프레임은 최대 8바이트 데이터 + 32비트 식별자다.
- 식별자에는 PGN(메시지 내용 식별, 메일 제목), 소스 주소(발신자), 목적지 주소(수신자, PGN이 브로드캐스트 여부를 결정), 우선순위(충돌 시 승자, 보통 하드웨어가 처리)가 들어 있다.
- 주소는 1바이트이며 255(0xFF)는 브로드캐스트, 254(0xFE)는 NULL 주소로 예약돼 있다.
:::

## 원문 출처

- [AgIsoStack++ Documentation — Concepts: The Basics](https://isobus-plus-plus.readthedocs.io/en/latest/Concepts.html#the-basics)

## 다음 챕터

[CH3. Control Function과 NAME](/study/agisostack/03-control-function-name)으로 이어진다.
