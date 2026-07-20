---
title: "CH1. AgIsoStack++ 개요"
description: "AgIsoStack++가 무엇이고, ISOBUS 스택을 직접 짜는 대신 이 라이브러리를 쓰면 무엇이 해결되는가"
date: 2026-07-20
tags: [AgIsoStack, ISOBUS, J1939, C++, 오픈소스]
---

# CH1. AgIsoStack++ 개요

## 학습 목표

- AgIsoStack++가 어떤 라이브러리이고 어떤 표준을 다루는지 설명할 수 있다
- ISOBUS 스택을 직접 구현할 때 드는 비용과, 라이브러리가 대신 처리해 주는 영역을 구분할 수 있다
- Open-Agriculture 생태계의 주변 프로젝트들이 각각 어떤 역할인지 안다
- MIT 라이선스의 의미와, 프로젝트가 명시한 특허 관련 주의사항을 이해한다

## AgIsoStack++는 무엇인가

한 문장으로 정리하면 이렇다.

::: tip 한 줄 정의
<strong>AgIsoStack++는 C++로 ISO 11783과 J1939 CAN 통신을 쉽고 견고하게 다루게 해 주는 무료 오픈소스 라이브러리다.</strong>
:::

ISOBUS는 트랙터와 작업기가 제조사에 상관없이 서로 통신하도록 규정한 표준이다. 그 아래에는 SAE J1939가 있고, 다시 그 아래에는 CAN 버스가 있다. AgIsoStack++는 이 계층 중 <strong>J1939와 ISO 11783에 해당하는 소프트웨어 계층</strong>을 담당한다. 아래로는 CAN 드라이버에 프레임을 넘기고, 위로는 애플리케이션에 "누가 무슨 메시지를 보냈다" 수준의 정보를 올려 준다.

![AgIsoStack++의 위치 — 위에는 내 애플리케이션(살포량 계산·화면 로직·작업 기록), 가운데 AgIsoStack++가 주소 클레임·전송 프로토콜·VT 클라이언트·TC 클라이언트를 담당하고, 아래에는 HardwareInterface를 통해 SocketCAN·TWAI·PEAK 등 CAN 드라이버가 연결된 3계층 구조](/images/study-agisostack/01-stack-responsibility-light.png)
![AgIsoStack++의 위치 — 위에는 내 애플리케이션(살포량 계산·화면 로직·작업 기록), 가운데 AgIsoStack++가 주소 클레임·전송 프로토콜·VT 클라이언트·TC 클라이언트를 담당하고, 아래에는 HardwareInterface를 통해 SocketCAN·TWAI·PEAK 등 CAN 드라이버가 연결된 3계층 구조](/images/study-agisostack/01-stack-responsibility-dark.png)

## 왜 라이브러리가 필요한가

CAN 컨트롤러 드라이버만 있으면 프레임 하나 보내는 건 어렵지 않다. 문제는 ISOBUS가 "프레임 하나"로 끝나는 표준이 아니라는 데 있다. 직접 스택을 짜기로 하면 최소한 다음을 전부 구현해야 한다.

- <strong>주소 클레임과 중재</strong> — 버스에 올라온 다른 장치들과 주소를 두고 협상하고, 충돌하면 다시 시도하고, 상대가 주소를 바꾸면 추적해야 한다.
- <strong>전송 프로토콜 4종</strong> — 8바이트를 넘는 데이터를 보내려면 BAM·TP·ETP·Fast Packet 중 하나를 골라 분할·재조립하고, 타임아웃과 abort를 처리해야 한다.
- <strong>Virtual Terminal 클라이언트</strong> — 오브젝트 풀 업로드, 버전 관리, 화면 이벤트 수신, VT 상태 추적까지 상태 기계 하나가 통째로 필요하다.
- <strong>Task Controller 클라이언트</strong> — DDOP를 만들어 올리고, 프로세스 데이터 값을 주기적으로 주고받아야 한다.
- <strong>각종 작업기 메시지</strong> — 속도·거리, 가이던스, 하트비트, ISOBUS Shortcut Button 같은 표준 메시지들.

이 목록은 전부 표준 문서를 정확히 읽어야만 제대로 구현되는 것들이고, 하나라도 틀리면 다른 제조사 장비 앞에서 조용히 동작하지 않는다. AgIsoStack++는 이 영역을 통째로 가져간다. 애플리케이션이 남기는 일은 <strong>NAME을 채워 넣고, 필요한 클라이언트 객체를 만들고, 콜백에서 값을 처리하는 것</strong> 정도다.

::: info 관련 스터디
여기서 나열한 항목이 표준상 정확히 무엇을 요구하는지는 이론 스터디에서 다룬다.
[ISOBUS CH10. J1939 주소 체계](/study/isobus/10-j1939-address) · [CH11. J1939 Transport Protocol](/study/isobus/11-j1939-transport) · [CH14. ISOBUS 네트워크 관리](/study/isobus/14-isobus-network-mgmt) · [CH15. VT 기초](/study/isobus/15-vt-basics) · [CH18. TC 기초](/study/isobus/18-tc-basics)
:::

## 프로젝트 생태계

AgIsoStack++는 GitHub의 <strong>Open-Agriculture</strong> 조직에서 관리한다. 이 조직에는 스택 하나만 있는 게 아니라, 스택으로 개발할 때 함께 쓰는 도구들이 모여 있다.

![Open-Agriculture 생태계 — 중심에 AgIsoStack++(C++ ISO 11783/J1939 스택)가 있고, 주변에 AgIsoVirtualTerminal(PC용 VT 서버), AgIsoDDOPGenerator(DDOP 저작 도구), AgIsoStack-rs(Rust 바인딩·포팅), 예제·문서·튜토리얼이 연결된 구조](/images/study-agisostack/01-ecosystem-light.png)
![Open-Agriculture 생태계 — 중심에 AgIsoStack++(C++ ISO 11783/J1939 스택)가 있고, 주변에 AgIsoVirtualTerminal(PC용 VT 서버), AgIsoDDOPGenerator(DDOP 저작 도구), AgIsoStack-rs(Rust 바인딩·포팅), 예제·문서·튜토리얼이 연결된 구조](/images/study-agisostack/01-ecosystem-dark.png)

| 프로젝트 | 역할 |
|----------|------|
| <strong>AgIsoStack-plus-plus</strong> | 본체. C++ ISOBUS/J1939 스택 |
| <strong>AgIsoVirtualTerminal</strong> | PC에서 돌릴 수 있는 Virtual Terminal 서버. 실제 트랙터 디스플레이 없이 VT 클라이언트를 테스트할 때 쓴다 |
| <strong>AgIsoDDOPGenerator</strong> | Task Controller용 장치 기술서(DDOP)를 GUI로 만들고 검사하는 도구 |
| <strong>AgIsoStack-rs</strong> | 같은 개념을 Rust로 옮긴 프로젝트 |

개발 초기에 특히 유용한 건 <strong>AgIsoVirtualTerminal</strong>이다. VT 클라이언트를 붙이는 작업은 실제 디스플레이 장비가 있어야 확인 가능한데, 이걸 PC에서 대체할 수 있으면 반복 주기가 크게 줄어든다.

- 스택 저장소: <https://github.com/Open-Agriculture/AgIsoStack-plus-plus>
- 조직 전체: <https://github.com/Open-Agriculture>

## 라이선스

AgIsoStack++는 <strong>MIT 라이선스</strong>다. 저작권 표기는 `Copyright (c) 2022-2024 The Open-Agriculture Developers`이며, 라이선스 전문은 다음과 같다.

```text
MIT License

Copyright (c) 2022-2024 The Open-Agriculture Developers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

실무적으로 보면 상업 제품에 넣어도 되고, 수정해서 배포해도 되고, 소스를 공개할 의무도 없다. 지켜야 할 건 저작권 표기와 라이선스 전문을 배포물에 포함하는 것 하나뿐이다. 그리고 마지막 문단이 말하듯 <strong>어떤 보증도 없다</strong>. 이 스택을 실제 농기계에 올린 결과에 대한 책임은 사용자 몫이다.

### 특허에 대한 주의사항

원문 License 페이지에는 "Other Legal Stuff"라는 별도 절이 있다. 요지는 세 가지다.

::: warning 프로젝트가 밝힌 법적 입장
- ISO 11783을 준수하는 것은 이 프로젝트와 ISO 11783/J1939 표준 전반에서 언급되는 <strong>CAN 프로토콜 관련 특허의 사용을 수반할 수 있다</strong>고 알려져 있다.
- Adrian Del Grosso를 비롯한 이 프로젝트의 어떤 기여자도 그 특허의 <strong>증거·유효성·권리 범위에 대해 어떠한 입장도 취하지 않는다</strong>.
- ISO 11783과 J1939의 일부 요소는 위에서 언급한 것 외의 <strong>다른 특허권의 대상일 수 있으며</strong>, 그러한 특허권을 식별할 책임은 이 프로젝트의 어느 구성원에게도 없다.
:::

즉 MIT 라이선스는 <strong>이 코드에 대한 권리</strong>만 다룬다. 표준 자체를 구현하는 과정에서 발생할 수 있는 특허 문제는 라이선스가 보증해 주는 범위 밖이다.

### 실무에서 함께 알아둘 것

아래는 원문 문서에 적힌 내용은 아니지만, 상용 제품을 목표로 한다면 라이선스와 별개로 반드시 고려해야 하는 부분이다.

- <strong>표준 문서는 별도로 구해야 한다</strong> — ISO 11783 각 파트는 유료 표준 문서다. 라이브러리가 오픈소스라고 해서 표준 원문이 딸려 오지는 않는다. PGN·DDI 같은 식별자 목록은 [isobus.net](https://www.isobus.net)에서 무료로 조회할 수 있지만, 프로토콜 규정 자체를 정확히 확인하려면 표준 문서가 필요하다.
- <strong>인증(certification)과 라이브러리 사용은 별개다</strong> — AEF 인증 마크를 붙이려면 정해진 시험 절차와 인증 기관을 거쳐야 한다. 이 라이브러리를 썼다는 사실이 인증을 대신하지 않는다. 반대로, 인증 없이 사내 장비끼리만 통신하는 용도라면 인증 절차 없이도 얼마든지 쓸 수 있다.

## 학습 경로

이 스터디는 다음 순서를 전제로 쓰여 있다.

1. <strong>개념</strong>(CH2~4) — CAN 프레임과 주소, Control Function과 NAME, 전송 계층. 라이브러리 API 이름이 전부 이 개념에서 나오므로 먼저 잡고 간다.
2. <strong>환경</strong>(CH5~6) — CMake로 프로젝트에 붙이고 빌드를 통과시킨다.
3. <strong>기본 통신</strong>(CH7~12) — 송신, 수신, 목적지 지정, 전송 계층, PGN 요청, 로깅. 여기까지 오면 임의의 ISOBUS 메시지를 다룰 수 있다.
4. <strong>애플리케이션 계층</strong>(CH13~16) — VT와 TC. 실제 제품에서 가장 많은 시간이 들어가는 부분이다.
5. <strong>이식</strong>(CH17~18) — 내 하드웨어의 CAN 드라이버에 연결한다.

::: tip 핵심 정리
- AgIsoStack++는 ISO 11783/J1939 통신을 C++로 다루는 MIT 라이선스 오픈소스 라이브러리다.
- 주소 클레임, 전송 프로토콜 선택, VT·TC 클라이언트처럼 직접 구현하면 오래 걸리는 부분을 라이브러리가 가져간다.
- Open-Agriculture 조직에는 스택 외에 PC용 VT 서버(AgIsoVirtualTerminal), DDOP 생성기(AgIsoDDOPGenerator), Rust 포팅(AgIsoStack-rs)이 함께 있다.
- MIT 라이선스는 코드 사용을 자유롭게 허용하지만 보증은 없고, 프로젝트는 CAN 관련 특허에 대해 어떠한 입장도 취하지 않는다고 명시한다.
:::

## 원문 출처

- [AgIsoStack++ Documentation — Overview](https://isobus-plus-plus.readthedocs.io/en/latest/)
- [AgIsoStack++ Documentation — License](https://isobus-plus-plus.readthedocs.io/en/latest/License.html)

## 다음 챕터

[CH2. ISOBUS 핵심 개념](/study/agisostack/02-isobus-concepts)으로 이어진다.
