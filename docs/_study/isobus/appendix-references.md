---
title: "참고 자료 / 링크"
description: "ISOBUS/CAN 스터디에 유용한 표준 문서, 도구, 오픈소스, 학습 자료를 정리한 참조 자료입니다."
date: 2026-04-13
tags: [ISOBUS, 부록]
---

# 참고 자료 / 링크

---

## ISO 표준 (ISO 11783 시리즈)

ISO 11783은 ISOBUS의 공식 표준으로, 농업 기계의 전자 통신을 정의한다.

| 파트 | 제목 | 주요 내용 |
|------|------|----------|
| ISO 11783-1 | General Standard for Mobile Data Communication | 전체 시리즈 개요 및 용어 정의 |
| ISO 11783-2 | Physical Layer | 버스 전기적 특성, 커넥터, 케이블 규격 (250 kbps, 차동 신호) |
| ISO 11783-3 | Data Link Layer | CAN 2.0B 29비트 ID 기반 데이터 링크 계층 |
| ISO 11783-4 | Network Layer | 주소 할당, 네트워크 관리 |
| ISO 11783-5 | Network Management | 주소 획득 절차, Working Set 관리 |
| ISO 11783-6 | Virtual Terminal | VT 오브젝트 풀, UI 표시, 입력 처리 규격 |
| ISO 11783-7 | Implement Messages Application Layer | TECU 메시지 정의 (차속, PTO 등) |
| ISO 11783-8 | Power Train Messages | 엔진, 변속기 메시지 (J1939 연계) |
| ISO 11783-9 | Tractor ECU | 트랙터 ECU 기능 요구사항 |
| ISO 11783-10 | Task Controller and Management Computer | TC, FMIS, DDOP, Section Control 정의 |
| ISO 11783-11 | Mobile Data Element Dictionary | DDI 데이터 사전 전체 목록 |
| ISO 11783-12 | Diagnostics Services | 진단 서비스, DM 메시지 |
| ISO 11783-13 | File Server | 파일 서버 서비스 (SD 카드 접근 등) |
| ISO 11783-14 | Sequence Control | 시퀀스 제어 서비스 |

> ISO 표준 문서는 [ISO 공식 사이트](https://www.iso.org)에서 유료로 구매할 수 있다.

---

## SAE 표준 (J1939 시리즈)

J1939은 ISOBUS의 기반이 되는 SAE 상용차 통신 표준이다.

| 문서 | 제목 | 주요 내용 |
|------|------|----------|
| SAE J1939 | Recommended Practice for Serial Control and Communications Heavy Duty Vehicle Networks | J1939 전체 개요 |
| SAE J1939/11 | Physical Layer - 250K bits/s, Shielded Twisted Pair (STP) | 물리 계층 (차폐 꼬임선) |
| SAE J1939/15 | Physical Layer - 250K bits/s, Un-Shielded Twisted Pair (UTP) | 물리 계층 (비차폐 꼬임선) |
| SAE J1939/21 | Data Link Layer | CAN 29비트 ID 구조, TP, ETP 정의 |
| SAE J1939/31 | Network Layer | 라우터, 브리지 기능 |
| SAE J1939/71 | Vehicle Application Layer | PGN, SPN 정의 |
| SAE J1939/73 | Application Layer - Diagnostics | DM1~DM31 진단 메시지 정의 |
| SAE J1939/81 | Network Management | 주소 협상(Address Claiming) 절차 |

> SAE 문서는 [SAE International](https://www.sae.org)에서 유료로 구매할 수 있다.

---

## AEF (Agricultural Industry Electronics Foundation)

| 자료 | 링크 | 설명 |
|------|------|------|
| AEF 공식 사이트 | [isobus.net](https://www.isobus.net) | ISOBUS 인증, 상호운용성 테스트, DDI 검색 도구 제공 |
| AEF DDI 검색 | [isobus.net/isobus/ddi](https://www.isobus.net/isobus/ddi) | DDI 번호별 이름, 단위, 설명 검색 |
| AEF 인증 목록 | AEF 사이트 내 Certified Products 메뉴 | ISOBUS 인증을 받은 제품 목록 |
| AEF Conformance Test | AEF 사이트 내 Conformance Testing 메뉴 | ISOBUS 준수 테스트 절차 및 테스트 케이스 |

---

## 분석 및 개발 도구

| 도구 | 종류 | 설명 |
|------|------|------|
| **PCAN-View** | GUI 분석기 | PEAK System의 무료 CAN 모니터링 도구. PCAN-USB 하드웨어와 함께 사용. Windows 전용. |
| **SavvyCAN** | GUI 분석기 | 오픈소스 CAN 버스 분석 도구. 다양한 어댑터 지원, DBC 파일 디코딩, 크로스플랫폼. |
| **CANoe** | 전문 분석기 | Vector Informatik의 전문 CAN/ISOBUS 시뮬레이션 및 분석 도구. 유료. |
| **CANalyzer** | 전문 분석기 | Vector의 CAN 버스 분석 도구. CANoe의 분석 특화 버전. 유료. |
| **python-can** | 라이브러리 | Python용 오픈소스 CAN 라이브러리. 다양한 CAN 어댑터 지원. 스크립트 기반 자동화에 유용. |
| **can-utils** | CLI 도구 | Linux SocketCAN 기반 CAN 도구 모음. `candump`, `cansend`, `cansniffer` 등 포함. |
| **BUSMASTER** | GUI 분석기 | Robert Bosch의 오픈소스 CAN 분석 도구. DBC 지원, 시뮬레이션 기능 포함. |
| **PEAK PCAN-USB** | 하드웨어 | 저가형 USB-CAN 어댑터. PCAN-View 및 python-can과 함께 많이 사용. |

---

## 오픈소스 ISOBUS 스택

| 프로젝트 | 언어 | 설명 |
|----------|------|------|
| **AgIsoStack++** | C++ | Open-Agriculture 재단의 오픈소스 ISOBUS 스택. VT Client, TC Client, DDOP 생성 등 ISOBUS 상위 레이어를 구현한다. [GitHub](https://github.com/Open-Agriculture/AgIsoStack-plus-plus) |
| **AgIsoStack for .NET** | C# | AgIsoStack의 .NET 포팅 버전. [GitHub](https://github.com/Open-Agriculture/AgIsoStack.NET) |
| **isobus-cpp** | C++ | 또 다른 오픈소스 ISOBUS C++ 구현체. |
| **python-isobus** | Python | Python 기반 경량 ISOBUS 구현. 프로토타이핑 및 테스트 용도에 적합. |
| **can-utils (SocketCAN)** | C | Linux 커널 내장 CAN 드라이버 및 유틸리티. J1939 소켓 API 포함. |

---

## 학습 자료

### 서적

| 제목 | 저자 | 내용 |
|------|------|------|
| *A Comprehensible Guide to J1939* | Wilfried Voss | J1939 프로토콜을 체계적으로 설명하는 입문서. PGN, SPN, TP, 주소 협상 등을 다룬다. |
| *Controller Area Network (CAN) Essentials* | Wilfried Voss | CAN 프로토콜 기초부터 심화까지 다루는 책. |
| *CAN System Engineering* | Wolfhard Lawrenz | CAN 네트워크 설계 및 엔지니어링 관점의 심화서. |

### 온라인 강좌 및 문서

| 자료 | 제공처 | 설명 |
|------|--------|------|
| CSS Electronics CAN 가이드 | [csselectronics.com](https://www.csselectronics.com/pages/can-bus-simple-intro-tutorialf) | CAN, J1939, OBD2를 쉽게 설명하는 무료 온라인 가이드. |
| Kvaser CAN 교육 자료 | [kvaser.com](https://www.kvaser.com/can-protocol-tutorial/) | CAN 프로토콜 튜토리얼 및 기술 문서. |
| ISOBUS 입문 (AEF) | isobus.net 내 교육 자료 | AEF에서 제공하는 ISOBUS 소개 자료. |
| Vector 기술 블로그 | [vector.com](https://www.vector.com/int/en/know-how/) | CAN/ISOBUS 관련 기술 아티클 및 백서. |
| SocketCAN 문서 | Linux Kernel Documentation | Linux CAN 드라이버 및 J1939 소켓 API 사용법. |

### 커뮤니티

| 커뮤니티 | 링크 | 설명 |
|----------|------|------|
| Stack Overflow | stackoverflow.com | CAN, J1939, ISOBUS 관련 Q&A |
| GitHub Open-Agriculture | github.com/Open-Agriculture | AgIsoStack 관련 이슈 및 토론 |
| Reddit r/embedded | reddit.com/r/embedded | 임베디드 시스템 및 CAN 관련 토론 |
