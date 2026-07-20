---
title: "부록 B. 참고 자료"
description: "AgIsoStack++ 공식 문서·저장소, Open-Agriculture 프로젝트 목록, isobus.net과 ISO 11783 표준, 커뮤니티, 그리고 스터디 전체 챕터 인덱스."
date: 2026-07-20
tags: [AgIsoStack, ISOBUS, 참고자료]
---

# 부록 B. 참고 자료

## 공식 문서와 저장소

| 자료 | 주소 | 무엇인가 |
| --- | --- | --- |
| 공식 문서 사이트 | `https://isobus-plus-plus.readthedocs.io/en/latest/` | 이 스터디의 기반이 된 Sphinx 문서. 개념·설치·튜토리얼·API |
| 문서 대체 주소 | `https://agisostack-plus-plus.readthedocs.io/en/latest/` | 저장소 README가 안내하는 같은 문서의 다른 도메인 |
| Doxygen (미리 빌드) | `https://delgrossoengineering.com/isobus-docs/index.html` | 내부 API까지 포함한 자동 생성 레퍼런스 |
| GitHub 저장소 | `https://github.com/Open-Agriculture/AgIsoStack-plus-plus` | 소스, 예제, 이슈, 논의 |
| 예제 코드 | `https://github.com/Open-Agriculture/AgIsoStack-plus-plus/tree/main/examples` | Hello World, VT, TC 클라이언트/서버, 가이던스, seeder 예제 등 |
| 이슈 트래커 | `https://github.com/Open-Agriculture/AgIsoStack-plus-plus/issues` | 버그 제보와 기능 제안 창구 |
| Discussions | `https://github.com/Open-Agriculture/AgIsoStack-plus-plus/discussions` | 질문과 사용 사례 공유 |
| 기여 가이드 | `https://github.com/Open-Agriculture/AgIsoStack-plus-plus/blob/main/CONTRIBUTING.md` | [CH6](/study/agisostack/06-developer-guide)에서 다룬 기여 절차 |

## Open-Agriculture 조직의 프로젝트들

AgIsoStack++는 GitHub의 <strong>Open-Agriculture</strong> 조직에 속해 있고, 주변에 서로 물려 돌아가는 프로젝트들이 있다. 라이선스가 저장소마다 다르니 상용 제품에 끌어다 쓸 때는 반드시 확인해야 한다.

| 저장소 | 언어 | 라이선스 | 용도 |
| --- | --- | --- | --- |
| `AgIsoStack-plus-plus` | C++ | MIT | 이 스터디의 주인공. C++ ISOBUS / J1939 스택 |
| `AgIsoStack-Arduino` | C++ | MIT | Arduino Library Manager에 맞게 수정된 배포판. 저장소의 `generateArduinoLibrary.py`로 생성된다 |
| `AgIsoStack-rs` | Rust | MIT | ISO 11783 / J1939의 Rust 구현 |
| `AgIsoVirtualTerminal` | C++ | GPL-3.0 | AgIsoStack++ 기반의 실험적 ISO 11783-6 <strong>VT 서버 GUI</strong>. PC에서 오브젝트 풀을 실제로 띄워 보는 데 쓴다 |
| `AgIsoTerminalDesigner` | Rust | GPL-3.0 | VT 오브젝트 풀을 설계·수정하는 실험적 GUI |
| `AgIsoDDOPGenerator` | C++ | MIT | ISO 11783 <strong>DDOP 편집기</strong>. AgIsoStack++ 기반 |
| `AgIsoDevelopmentTools` | C++ | MIT | 프로젝트 개발용 도구 모음. 표준 기본 타입에 `std::` 접두사를 강제하는 clang-tidy 플러그인 등 |

::: warning 라이선스 차이에 주의
스택 본체(`AgIsoStack-plus-plus`)는 MIT라 상용 제품에 붙이기 쉽지만, `AgIsoVirtualTerminal`과 `AgIsoTerminalDesigner`는 <strong>GPL-3.0</strong>이다. 이 둘은 개발·테스트용 도구로 쓰는 것과, 코드를 제품에 통합하는 것이 법적으로 완전히 다른 얘기다. 도구로 쓰는 건 문제없지만 코드를 가져다 쓸 생각이라면 GPL 조항을 먼저 확인해야 한다.
:::

## isobus.net

ISOBUS 관련 정보를 조회하는 공식 데이터베이스다. 개발 중에 가장 자주 열게 되는 사이트다.

| 조회 대상 | 주소 | 언제 쓰나 |
| --- | --- | --- |
| 사이트 메인 | `https://www.isobus.net` | 전반 진입점 |
| PGN / SPN 검색 | `https://www.isobus.net/isobus/pGNAndSPN/` | 처리할 메시지의 PGN 번호, 데이터 필드 정의를 확인할 때 |
| 제조사 코드 | `https://www.isobus.net/isobus/manufacturerCode/` | NAME의 Manufacturer Code 필드 값을 찾을 때 |
| NAME Function | `https://www.isobus.net/isobus/nameFunction/` | 내 장치가 어떤 Function 값을 써야 하는지 정할 때 |
| DDI (데이터 사전) | `https://www.isobus.net/isobus/dDEntity/` | DDOP를 만들 때 각 프로세스 데이터의 DDI를 찾을 때 |

::: tip PGN을 찾는 요령
[CH16](/study/agisostack/16-implement-messages)에서 본 ISB처럼, 규격 문서 없이도 PGN 검색으로 상당 부분을 알아낼 수 있다. 예를 들어 ISB는 PGN 검색에서 "All implements stop operations switch state"로 찾으면 정의가 나온다. 스택 코드에서 PGN 상수를 만나면 `can_general_parameter_group_numbers.hpp`의 이름을 그대로 isobus.net에서 검색하는 게 가장 빠르다.
:::

## AEF (Agricultural Industry Electronics Foundation)

ISOBUS 적합성 인증과 상호운용성 가이드라인을 만드는 산업 단체다.

| 자료 | 주소 |
| --- | --- |
| AEF 공식 사이트 | `https://www.aef-online.org` |
| AEF One Pager (ISB 등 요약) | `https://www.aef-online.org/fileadmin/user_upload/Content/pdfs/AEF_One_Pager.pdf` |

::: warning 인증에 대한 오해 금지
AgIsoStack++ 프로젝트는 <strong>AEF와 무관하며 AEF의 승인을 받은 적이 없다.</strong> 이 라이브러리를 썼다는 사실만으로 AEF 인증 제품이 되는 것이 아니다. 상용 제품이라면 인증 절차를 별도로 밟아야 한다. 원문 문서 곳곳에 이 취지의 문장이 반복해서 등장한다.
:::

기능 단위로는 AEF Guideline 004(ISB)처럼 개별 가이드라인이 별도로 존재한다. AgIsoStack++가 구현하는 ISB 인터페이스도 이 가이드라인을 따른다.

## ISO 11783 표준

ISOBUS의 본체다. 여러 파트로 나뉘어 있고, 각 파트가 스택의 어느 부분에 대응하는지 알아 두면 문서와 코드를 오가기 편하다.

| 파트 | 다루는 내용 | 이 스터디에서 |
| --- | --- | --- |
| Part 1 | 이동형 데이터 통신 일반 규격 | [CH2](/study/agisostack/02-isobus-concepts) |
| Part 2 | 물리 계층 | [CH2](/study/agisostack/02-isobus-concepts) |
| Part 3 | 데이터 링크 계층 (TP·ETP 포함) | [CH4](/study/agisostack/04-transport-concepts), [CH10](/study/agisostack/10-transport-layer) |
| Part 4 | 네트워크 계층 | [CH2](/study/agisostack/02-isobus-concepts) |
| Part 5 | 네트워크 관리 (주소 클레임·NAME) | [CH3](/study/agisostack/03-control-function-name) |
| Part 6 | Virtual Terminal | [CH13](/study/agisostack/13-virtual-terminal) |
| Part 7 | 작업기 메시지 응용 계층 | [CH16](/study/agisostack/16-implement-messages) |
| Part 8 | 동력 전달계(power train) 메시지 | — |
| Part 9 | 트랙터 ECU (TECU) | [CH16](/study/agisostack/16-implement-messages) |
| Part 10 | Task Controller 및 관리 정보 시스템 데이터 교환 | [CH14](/study/agisostack/14-tc-ddop), [CH15](/study/agisostack/15-tc-client) |
| Part 11 | 이동형 데이터 요소 사전 (DDI) | [CH14](/study/agisostack/14-tc-ddop) |
| Part 12 | 진단 서비스 | — |
| Part 13 | 파일 서버 | — |
| Part 14 | 시퀀스 제어 | — |

::: info 표준 문서는 유료다
ISO 11783 원문은 ISO(`https://www.iso.org`)에서 파트별로 구매해야 한다. 라이브러리가 무료라고 표준이 무료인 것은 아니다. 다만 PGN·SPN·DDI 같은 <strong>식별자 수준</strong>의 정보는 isobus.net에서 무료로 조회할 수 있어서, 학습과 상당수의 실무는 그것만으로도 진행된다.
:::

관련 표준으로 SAE J1939가 있다. ISO 11783은 J1939를 기반으로 농업 기계용으로 확장한 규격이라, J1939 문서가 도움이 되는 경우가 많다. NMEA 2000도 같은 계열이고, AgIsoStack++는 Fast Packet Protocol과 NMEA 2000 메시지 정의를 함께 지원한다.

## 커뮤니티

| 채널 | 주소 | 용도 |
| --- | --- | --- |
| Discord | `https://discord.gg/uU2XMVUD4b` | 지원 요청, 프로젝트 자랑, 잡담. 프로젝트가 가장 먼저 안내하는 채널이다 |
| Telegram | `https://t.me/+kzd4-9Je5bo1ZDg6` | Discord 대신 쓸 수 있는 채널 |
| GitHub Discussions | `https://github.com/Open-Agriculture/AgIsoStack-plus-plus/discussions` | 기록으로 남길 만한 질문·논의 |
| GitHub Issues | `https://github.com/Open-Agriculture/AgIsoStack-plus-plus/issues` | 버그·기능 요청 |

## 이 블로그의 관련 스터디

AgIsoStack++는 이 라이브러리 하나만 봐서는 배경이 부족하다. 아래 스터디들과 함께 보면 훨씬 잘 붙는다.

| 스터디 | 링크 | 이 스터디와의 관계 |
| --- | --- | --- |
| ISOBUS | [/study/isobus/](/study/isobus/) | CAN 기초부터 J1939, ISOBUS VT·TC까지 <strong>규격 자체</strong>를 다룬다. AgIsoStack++가 구현하는 대상이 여기 있다 |
| CAN 통신 | [/study/can/](/study/can/) | 물리 계층, 프레임, 에러 처리, SocketCAN, 진단 프로토콜 등 <strong>CAN 자체</strong>를 깊게 다룬다. 버스가 이상할 때 돌아올 곳 |
| 스마트 농업 | [/study/smart-agriculture/](/study/smart-agriculture/) | 정밀 농업의 큰 그림. ISOBUS가 왜 필요한지, TC가 무엇을 위한 것인지의 배경 |

## 이 스터디 전체 챕터 인덱스

### 시작하기

| 챕터 | 제목 |
| --- | --- |
| — | [스터디 소개](/study/agisostack/) |
| CH1 | [AgIsoStack++ 개요](/study/agisostack/01-overview) |
| CH2 | [ISOBUS 핵심 개념](/study/agisostack/02-isobus-concepts) |
| CH3 | [Control Function과 NAME](/study/agisostack/03-control-function-name) |
| CH4 | [전송 계층 개념](/study/agisostack/04-transport-concepts) |

### 설치와 빌드

| 챕터 | 제목 |
| --- | --- |
| CH5 | [설치와 프로젝트 통합](/study/agisostack/05-installation) |
| CH6 | [개발자 가이드](/study/agisostack/06-developer-guide) |

### 기본 통신

| 챕터 | 제목 |
| --- | --- |
| CH7 | [ISOBUS Hello World](/study/agisostack/07-hello-world) |
| CH8 | [메시지 수신](/study/agisostack/08-receiving-messages) |
| CH9 | [목적지 지정 통신](/study/agisostack/09-adding-destination) |
| CH10 | [전송 계층 사용하기](/study/agisostack/10-transport-layer) |
| CH11 | [PGN 요청](/study/agisostack/11-pgn-requests) |
| CH12 | [디버그 로깅](/study/agisostack/12-debug-logging) |

### 애플리케이션 계층

| 챕터 | 제목 |
| --- | --- |
| CH13 | [Virtual Terminal 클라이언트](/study/agisostack/13-virtual-terminal) |
| CH14 | [Task Controller와 DDOP](/study/agisostack/14-tc-ddop) |
| CH15 | [Task Controller 클라이언트](/study/agisostack/15-tc-client) |
| CH16 | [작업기 메시지와 ISB](/study/agisostack/16-implement-messages) |

### 하드웨어와 이식

| 챕터 | 제목 |
| --- | --- |
| CH17 | [HardwareInterface](/study/agisostack/17-hardware-interface) |
| CH18 | [ESP32와 PlatformIO](/study/agisostack/18-esp32-platformio) |

### 레퍼런스

| 챕터 | 제목 |
| --- | --- |
| CH19 | [API 구조 훑어보기](/study/agisostack/19-api-reference) |
| 부록 A | [FAQ·릴리스·라이선스](/study/agisostack/appendix-faq) |
| 부록 B | 참고 자료 (이 문서) |

## 출처

이 스터디는 AgIsoStack++ 공식 문서(MIT 라이선스)의 Sphinx 소스를 기반으로, 기술적 내용을 한국어 학습 자료로 재구성한 것이다. 원문은 `https://isobus-plus-plus.readthedocs.io/en/latest/` 에서 볼 수 있다. 저작권은 The Open-Agriculture Developers에 있다.
