---
title: "AEF 기능 카테고리"
description: "UT, AUX-N, TC-BAS/TC-GEO/TC-SC, TIM, ISB 등 AEF가 정의한 ISOBUS 기능 단위를 한자리에 정리한 참조 자료입니다."
date: 2026-04-13
tags: [ISOBUS, AEF, 부록]
---

# AEF 기능 카테고리

## 1. ISO 파트와 AEF 기능은 다른 축이다

ISO 11783은 <strong>프로토콜을 어떻게 구현하는가</strong>를 파트 번호로 나눈다. AEF 기능(functionality)은 <strong>이 장비가 실제로 무엇을 할 줄 아는가</strong>를 나눈다. 두 축은 1:1로 대응하지 않는다.

- ISO 11783-6 하나 안에 UT와 AUX-N이라는 서로 다른 두 기능이 들어 있다.
- 반대로 TC-SC 하나를 구현하려면 -10(프로세스 데이터)과 -11(DDI)을 함께 알아야 한다.

인증 마크, AEF Database 등록, Plugfest 테스트 매트릭스가 전부 이 기능 단위로 돌아간다. 그래서 현장 대화는 파트 번호가 아니라 약어로 이뤄진다. "Part 6 지원하나요"가 아니라 "UT 되나요, AUX-N도 되나요"로 묻는다.

## 2. 한눈에 보기

| 약어 | 정식 명칭 | 하는 일 | 주 근거 파트 |
|------|-----------|---------|--------------|
| **UT** | Universal Terminal | 작업기가 자기 조작 화면(오브젝트 풀)을 터미널에 올려 조작받는다. 예전 이름이 VT(Virtual Terminal)라 문서마다 두 표기가 섞인다 | ISO 11783-6 |
| **AUX-N** | Auxiliary Control (New) | 조이스틱·버튼 패드 같은 보조 조작기를 작업기 기능에 사용자가 직접 할당해 쓴다. 터미널 화면을 거치지 않는다 | ISO 11783-6 |
| **TC-BAS** | Task Controller basic | 작업 총계(task total) 기록. 위치와 무관한 작업량 문서화 | ISO 11783-10 |
| **TC-GEO** | Task Controller geo-based | 위치 기반 로깅과 처방 맵 기반 위치 제어 | ISO 11783-10 |
| **TC-SC** | Task Controller section control | 붐 섹션 자동 ON/OFF 제어. 중복 살포와 경계 이탈 방지 | ISO 11783-10 |
| **LOG** | Data logger (DL) | 로깅 전용 기능. 프로토콜 버전 4에서 별도 CF로 추가됐다 | ISO 11783-10 |
| **TECU** | Tractor ECU | 트랙터 정보(속도, 거리, PTO, 링크 위치 등)를 버스에 공급하는 게이트웨이 | ISO 11783-9 |
| **TIM** | Tractor Implement Management | 작업기가 트랙터를 제어한다. 속도·PTO·유압·후방 링크 등 | AEF 정의, ISO 11783-7 계열 |
| **ISB** | ISOBUS Shortcut Button | 버튼 하나로 모든 작업기 기능을 즉시 중지 | ISO 11783-7 |
| **FS** | File Server | 버스 상의 공용 파일 저장소 | ISO 11783-13 |

::: warning 목록은 고정된 것이 아니다
AEF 기능 목록은 계속 갱신된다. 실제 인증을 준비한다면 위 표가 아니라 AEF가 배포하는 현행 기능 목록과 테스트 매트릭스를 기준으로 삼아야 한다.
:::

## 3. TC 3형제는 계층이다

TC-BAS / TC-GEO / TC-SC는 나란히 놓인 별개 기능이 아니라 <strong>TC-BAS를 토대로 쌓인 구조</strong>다.

```
TC-BAS  (작업 총계 기록)          ← 토대
  ├─ TC-SC   = TC-BAS + 섹션 자동 개폐
  └─ TC-GEO  = TC-BAS + 위치 기반 가변 제어
```

TC-GEO 클라이언트는 TC-BAS도 함께 지원해야 한다는 것이 Part 10 Annex F.2의 명시적 요구다. 즉 TC-SC나 TC-GEO를 지원한다고 말하면 TC-BAS는 당연히 되는 것으로 읽힌다. 구현을 시작할 때 TC-BAS부터 잡아야 하는 이유이고, 기능별 최소 요건은 [CH18. TC 기초](/study/isobus/18-tc-basics)에 자세히 정리돼 있다.

LOG(Data Logger)는 이 계층 바깥에 있다. TC 기능의 부분집합으로 같은 연결 메커니즘을 쓰며, 클라이언트는 TC 1개와 DL 1개에 동시에 연결할 수 있다.

## 4. UT와 AUX-N은 목적이 다르다

둘 다 ISO 11783-6 안에 있지만 노리는 조작 방식이 다르고, 인증도 따로 받는다.

| | UT | AUX-N |
|---|---|---|
| 조작 방식 | 화면을 보고 터치·소프트키로 조작 | 조이스틱 버튼에 기능을 매핑해 손으로 직접 조작 |
| 화면 필요 | 필수 | 할당 화면 외에는 불필요 |
| 전형적 용도 | 설정, 상태 확인, 값 입력 | 작업 중 즉시 반응이 필요한 조작 |

::: warning AUX-N과 AUX-O는 호환되지 않는다
보조 제어에는 신형(AUX-N)과 구형(AUX-O)이 있고 둘은 서로 호환되지 않는다. 어느 쪽을 지원할지 처음부터 결정하고 들어가야 하며, 현장 비호환 사고가 자주 나는 지점이다. API 관점의 설명은 [AgIsoStack CH13. Virtual Terminal](/study/agisostack/13-virtual-terminal)에 있다.
:::

## 5. 클라이언트와 서버는 따로 인증된다

같은 기능 이름이라도 <strong>제공하는 쪽과 사용하는 쪽의 요구사항이 다르고 인증도 별개</strong>다. 이 구분을 놓치면 "우리는 UT 지원"이라는 말이 어느 쪽을 뜻하는지 서로 다르게 알아듣는다.

| 기능 | 서버 (제공) | 클라이언트 (사용) |
|------|-------------|-------------------|
| UT | 터미널 | 작업기 ECU |
| AUX-N | 터미널 + 입력 장치 | 작업기 ECU |
| TC-BAS / TC-GEO / TC-SC | Task Controller | 작업기 ECU |
| FS | File Server | 파일을 읽고 쓰는 CF |

부담의 비대칭도 있다. TC 서버는 해당 기능성과 관련해 ISO 11783-11에 정의된 DDI를 전부 지원해야 하지만, TC 클라이언트는 자신이 실제로 다루는 부분집합만 제공하면 된다.

## 6. 버스에서 기능을 선언하는 방법

각 CF는 자신이 가진 기능을 <strong>control function functionalities</strong> 메시지로 알린다.

| 항목 | 값 |
|---|---|
| PGN | 64654 (0x00FC8E) |
| 전송 주기 | On request |
| 데이터 길이 | 가변, 최소 8 bytes |
| 기본 우선순위 | 6 |

메시지에는 기능 식별자와 함께 generation, functionality option이 실린다. 기능 식별자 값 자체는 표준 문서가 아니라 ISOBUS 온라인 데이터베이스(ISOBUS.net)에서 관리된다.

보고 범위에 규칙이 있다(Part 12 6.5).

- 구현돼 있으나 <strong>비활성</strong>인 기능 → 보고 대상이 아니다
- ECU에 있으나 <strong>시스템 구성상 현재 사용 불가</strong>한 기능 → 보고한다
- ECU에 있으나 <strong>CF에서 현재 비활성화</strong>된 기능 → 보고하지 않는다

예를 들어 작업기 ECU가 TC-GEO와 TC-SC를 가졌는데 TC-SC 서버가 없는 트랙터에 연결되면, TC-SC는 "존재하지만 시스템에서 사용 불가" 상태이므로 <strong>여전히 보고한다</strong>.

::: warning 진단 전용이다
이 메시지는 진단 목적 전용이며, CF가 런타임 동작을 구성하는 데 사용해서는 안 된다. 상대가 무슨 기능을 가졌는지 보고 동작을 바꾸고 싶다면 각 프로토콜이 정한 고유의 버전·능력 협상(예: TC의 Version 메시지)을 써야 한다.
:::

## 7. Conformance Test와 Plugfest는 다르다

둘 다 AEF가 주관하지만 성격이 정반대다. 헷갈리기 쉬운 지점이다.

| | Plugfest | Conformance Test |
|---|---|---|
| 목적 | 개발 중 상호운용성 확인 | 공식 적합성 인증 |
| 방식 | 제조사들이 모여 장비를 서로 바꿔 물려본다 | 정해진 테스트 케이스를 시험소에서 실행 |
| 결과 | 비공개, 인증 효력 없음 | 인증 마크 발급, AEF Database 등재 |
| 부담 | 개발 중인 물건을 들고 가도 된다 | 제품 수준의 완성도 필요 |

Plugfest는 "표준 문서만 보고 구현했는데 남의 장비와 실제로 붙는가"를 싸게 확인하는 자리다. 표준 해석 차이에서 오는 비호환을 조기에 발견하는 것이 목적이므로, 결과가 공개되지 않는다는 점이 오히려 참가 문턱을 낮춘다. 인증 절차 전반은 [스마트농업 CH14. 생태계와 표준화](/study/smart-agriculture/14-ecosystem)를 참고한다.

## 8. 구현 우선순위

기능을 처음부터 다 지원할 필요는 없다. 실제 수요와 검증 효율을 기준으로 하면 순서가 비교적 분명하다.

| 순위 | 기능 | 이유 |
|------|------|------|
| 1 | **UT** | 가장 많이 붙여보게 되고, 이것이 안 되면 다른 검증을 시작할 수 없다 |
| 2 | **TC-BAS** | 두 번째로 수요가 많고 TC 계열 전체의 토대다 |
| 3 | TC-SC → TC-GEO | TC-BAS가 선 다음에 의미가 있다 |
| 4 | AUX-N | 조작 편의 기능이라 뒤로 미뤄도 된다 |
| 후순위 | TIM | 트랙터를 제어하므로 안전 요구와 인증 부담이 다른 차원이다 |

## 9. 관련 문서

| 주제 | 문서 |
|------|------|
| TC 기능성 구분과 최소 요건 | [CH18. TC 기초](/study/isobus/18-tc-basics) |
| AEF와 적합성 인증 개요 | [CH12. ISOBUS 개요](/study/isobus/12-isobus-overview) |
| 인증 프로세스와 생태계 | [스마트농업 CH14. 생태계와 표준화](/study/smart-agriculture/14-ecosystem) |
| 기능 선언 메시지 원문 정리 | [Part 12. Diagnostics services](/study/isobus/appendix-iso-part12) |
| TIM으로의 이관 예고 | [Part 7. Implement messages](/study/isobus/appendix-iso-part07) |
| AUX-N API와 VT 서버 구현 | [AgIsoStack CH13. Virtual Terminal](/study/agisostack/13-virtual-terminal) |
| 용어 정의 | [용어집](/study/isobus/appendix-glossary) |
