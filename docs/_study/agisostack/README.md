---
title: "AgIsoStack++ 실전 가이드"
description: "오픈소스 C++ ISOBUS 라이브러리 AgIsoStack++로 농기계 CAN 통신 구현하기"
date: 2026-07-20
tags: [ISOBUS, AgIsoStack, C++, CAN, 스마트농업]
---

# AgIsoStack++ 실전 가이드

## 스터디 소개

<strong>AgIsoStack++</strong>는 ISO 11783(ISOBUS)과 J1939 CAN 통신을 C++로 다룰 수 있게 해 주는 무료 오픈소스 라이브러리다. 트랙터와 작업기가 주고받는 메시지를 직접 CAN 프레임 단위로 짜는 대신, 주소 클레임·전송 프로토콜·Virtual Terminal·Task Controller 같은 무거운 부분을 라이브러리에 맡기고 애플리케이션 로직에 집중할 수 있다.

이 스터디는 AgIsoStack++ 공식 문서를 뼈대로, 라이브러리를 처음 붙이는 사람이 <strong>설치 → 첫 메시지 송신 → 수신 → 전송 계층 → VT/TC 클라이언트 → 임베디드 이식</strong>까지 순서대로 밟을 수 있게 재구성한 것이다.

### 누구를 위한 것인가

- 농기계·작업기 ECU에 ISOBUS 통신을 붙여야 하는 <strong>임베디드·백엔드 개발자</strong>
- ISOBUS 표준 문서를 읽어 봤지만 실제 코드로 어떻게 옮기는지 막막한 사람
- 트랙터 디스플레이(VT)에 화면을 띄우거나 Task Controller와 작업 데이터를 주고받아야 하는 사람
- SocketCAN·ESP32 같은 환경에서 동작하는 <strong>C++ CAN 스택</strong>을 찾고 있는 사람

CAN 버스가 무엇인지 정도는 알고 있다고 가정한다. CAN 자체가 낯설다면 아래의 기존 ISOBUS 스터디를 먼저 훑고 오는 편이 빠르다.

::: info 관련 스터디
프로토콜 이론은 [ISOBUS 스터디](/study/isobus/)에서 다룬다. 그쪽이 <strong>표준이 무엇을 규정하는가</strong>를 다룬다면, 이 스터디는 <strong>그 표준을 라이브러리로 어떻게 구현하는가</strong>를 다룬다. 두 스터디는 짝을 이루므로, 개념이 헷갈릴 때마다 해당 챕터로 건너뛰어 확인하면 좋다.

- [CH2. CAN 통신 입문](/study/isobus/02-can-intro)
- [CH9. J1939 메시지 구조](/study/isobus/09-j1939-message)
- [CH10. J1939 주소 체계](/study/isobus/10-j1939-address)
- [CH11. J1939 Transport Protocol](/study/isobus/11-j1939-transport)
- [CH12. ISOBUS 개요](/study/isobus/12-isobus-overview)
:::

## 원문 출처

이 스터디는 AgIsoStack++ 공식 문서(<https://isobus-plus-plus.readthedocs.io/en/latest/>)의 Sphinx 소스를 기반으로 한다. 라이브러리와 문서 모두 <strong>MIT 라이선스</strong>이므로 코드 예제 인용과 번역·재배포가 허용된다. 각 챕터 하단에 해당 원문 페이지 링크를 남겨 두었으니, 원문과 대조하며 읽어도 좋다.

- 라이브러리: <https://github.com/Open-Agriculture/AgIsoStack-plus-plus>
- 공식 문서: <https://isobus-plus-plus.readthedocs.io/en/latest/>

## 학습 로드맵

전체 19챕터와 부록 2개는 6개 묶음으로 이어진다. 개념을 먼저 잡고, 빌드 환경을 갖춘 뒤, 기본 송수신을 손에 익히고, 그 위에 VT·TC 같은 애플리케이션 계층을 올린 다음, 마지막으로 실제 하드웨어에 이식하는 순서다.

![AgIsoStack++ 학습 로드맵 — 시작하기(CH1~4) → 설치와 빌드(CH5~6) → 기본 통신(CH7~12) → 애플리케이션 계층(CH13~16) → 하드웨어와 이식(CH17~18) → 레퍼런스(CH19·부록) 순서로 이어지는 6단계 흐름](/images/study-agisostack/00-roadmap-light.png)
![AgIsoStack++ 학습 로드맵 — 시작하기(CH1~4) → 설치와 빌드(CH5~6) → 기본 통신(CH7~12) → 애플리케이션 계층(CH13~16) → 하드웨어와 이식(CH17~18) → 레퍼런스(CH19·부록) 순서로 이어지는 6단계 흐름](/images/study-agisostack/00-roadmap-dark.png)

기본은 CH1부터 순서대로 읽는 것이다. 다만 상황에 따라 지름길도 있다.

- <strong>ISOBUS를 이미 잘 안다면</strong> — CH1을 훑고 CH5(설치)로 바로 넘어가도 된다. 다만 CH3(NAME)과 CH4(전송 계층)는 라이브러리 API가 그대로 반영하는 개념이라 한 번은 읽어 두는 편이 좋다.
- <strong>일단 돌려 보고 싶다면</strong> — CH5(설치) → CH7(Hello World) → CH8(수신) 세 챕터면 CAN 버스에 메시지를 올리고 받는 코드가 완성된다.
- <strong>VT 화면이 목표라면</strong> — CH5 → CH7 → CH13(Virtual Terminal) 경로가 최단이다.
- <strong>TC 연동이 목표라면</strong> — CH5 → CH7 → CH14(DDOP) → CH15(TC 클라이언트) 순으로 간다.
- <strong>ESP32 같은 MCU에 올린다면</strong> — CH17(HardwareInterface)과 CH18(ESP32/PlatformIO)을 먼저 봐도 좋다.

## 전체 목차

### 시작하기 (CH1~4)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 01 | [AgIsoStack++ 개요](/study/agisostack/01-overview) | 라이브러리가 무엇을 대신해 주는가, 생태계, MIT 라이선스와 법적 주의사항 |
| 02 | [ISOBUS 핵심 개념](/study/agisostack/02-isobus-concepts) | CAN 프레임, 32비트 식별자(PGN·주소·우선순위), 250kbit/s 네트워크, 주소 체계 |
| 03 | [Control Function과 NAME](/study/agisostack/03-control-function-name) | 주소가 아닌 NAME으로 식별하기, 64비트 NAME 구성, 주소 클레임 |
| 04 | [전송 계층 개념](/study/agisostack/04-transport-concepts) | BAM·TP·ETP·Fast Packet의 크기 한계와 제약, 자동 프로토콜 선택 |

### 설치와 빌드 (CH5~6)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 05 | [설치와 프로젝트 통합](/study/agisostack/05-installation) | CMake 통합, FetchContent, 플랫폼별 빌드 |
| 06 | [개발자 가이드](/study/agisostack/06-developer-guide) | 코드 구조와 기여 규칙, 개발 환경 |

### 기본 통신 (CH7~12)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 07 | [ISOBUS Hello World](/study/agisostack/07-hello-world) | 첫 Control Function 생성과 메시지 송신 |
| 08 | [메시지 수신](/study/agisostack/08-receiving-messages) | 콜백 등록과 PGN 필터링 |
| 09 | [목적지 지정 통신](/study/agisostack/09-adding-destination) | Partnered Control Function과 목적지 지정 송신 |
| 10 | [전송 계층 사용하기](/study/agisostack/10-transport-layer) | 8바이트 초과 데이터 송수신 |
| 11 | [PGN 요청](/study/agisostack/11-pgn-requests) | 요청 프로토콜과 응답 처리 |
| 12 | [디버그 로깅](/study/agisostack/12-debug-logging) | 로거 연결과 로그 레벨 |

### 애플리케이션 계층 (CH13~16)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 13 | [Virtual Terminal 클라이언트](/study/agisostack/13-virtual-terminal) | 오브젝트 풀 업로드와 화면 이벤트 처리 |
| 14 | [Task Controller와 DDOP](/study/agisostack/14-tc-ddop) | 장치 기술서(DDOP) 작성과 구조 |
| 15 | [Task Controller 클라이언트](/study/agisostack/15-tc-client) | 프로세스 데이터 송수신과 TC 연동 |
| 16 | [작업기 메시지와 ISB](/study/agisostack/16-implement-messages) | 속도·거리, 가이던스, 하트비트, ISOBUS Shortcut Button |

### 하드웨어와 이식 (CH17~18)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 17 | [HardwareInterface](/study/agisostack/17-hardware-interface) | CAN 드라이버 플러그인 구조와 직접 구현 |
| 18 | [ESP32와 PlatformIO](/study/agisostack/18-esp32-platformio) | MCU 환경 빌드와 TWAI 드라이버 |

### 레퍼런스 (CH19·부록)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 19 | [API 구조 훑어보기](/study/agisostack/19-api-reference) | 네트워크·VT·TC·하드웨어 API 지도 |
| 부록 | [FAQ·릴리스·라이선스](/study/agisostack/appendix-faq) | 자주 묻는 질문, 릴리스 정책, 라이선스 정리 |
| 부록 | [참고 자료](/study/agisostack/appendix-references) | 표준 문서, 도구, 커뮤니티 링크 |

## 시작하기

[CH1. AgIsoStack++ 개요](/study/agisostack/01-overview)에서 라이브러리가 정확히 무엇을 대신해 주는지부터 확인한다.
