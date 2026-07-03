---
title: "플레임그래프와 트레이스 연계"
description: "플레임그래프의 x축·y축이 의미하는 바와 읽는 법, flame graph와 icicle·diff view의 차이, 핫패스·회귀를 진단하는 실전 방법, span profiles로 트레이스와 프로파일을 연결하는 구조, Grafana 통합 화면과 알림→트레이스→프로파일로 이어지는 실전 워크플로우까지 다룬다."
date: 2026-07-02
tags: [Pyroscope, Flamegraph, Profiling]
prev: /study/observability/26-profile-types-ebpf
next: /study/observability/28-alloy-overview
---

# 플레임그래프와 트레이스 연계

::: info 학습 목표
- 플레임그래프의 x축(집계 비중)과 y축(스택 깊이)이 각각 무엇을 의미하는지 정확히 읽는다.
- flame graph와 icicle view의 차이, diff view가 회귀 진단에 쓰이는 방식을 이해한다.
- 플레임그래프로 핫패스와 성능 회귀를 진단하는 실전 절차를 익힌다.
- span profiles가 트레이스의 특정 스팬과 프로파일 데이터를 어떻게 연결하는지 이해한다.
:::

## 1. 플레임그래프 읽는 법

<strong>플레임그래프(flame graph)</strong>는 [24장](/study/observability/24-continuous-profiling-basics)에서 만든 "스택 + 값" 집계 결과를 시각화한 것이다. 읽을 때 반드시 기억해야 할 두 축이 있다.

- <strong>x축은 시간 순서가 아니라 집계 비중이다.</strong> 각 프레임(사각형)의 너비는 전체 샘플 중 그 함수가 콜 스택에 등장한 비율에 비례한다. 너비가 넓을수록 리소스를 많이 소비했다는 뜻이며, 가로 위치는 실행 순서와 무관하다 — 같은 이름의 함수는 보통 알파벳 순 등으로 정렬돼 인접한 형제 프레임끼리 병합되므로, 왼쪽에 있다고 먼저 실행됐다는 뜻이 아니다.
- <strong>y축은 스택 깊이다.</strong> 맨 아래(또는 맨 위, 방향은 도구마다 다름)가 root 프레임이고, 위로(또는 아래로) 올라갈수록 더 깊이 호출된 함수다. 특정 프레임의 바로 위에 쌓인 프레임들은 그 함수가 호출한 자식 함수들이다.

![플레임그래프 예시: root인 main(100%) 위에 handleRequest(95%)가 쌓이고 그 위에 parseJSON(40%)·dbQuery(50%)·writeLog(5%)가 나란히, dbQuery 위에 다시 encodeRow(30%)·acquireConn(20%)이 쌓인 가로 막대 스택. x축은 집계 비중, y축은 스택 깊이](/images/study-observability/27-flamegraph-tree.png)

위 다이어그램을 실제 플레임그래프로 옮기면, `handleRequest` 프레임의 너비가 `main` 전체 너비의 95%를 차지하고, 그 위에 `parseJSON`(40%)과 `dbQuery`(50%)가 나란히 놓이며, `dbQuery` 위에 다시 `encodeRow`와 `acquireConn`이 쌓이는 식이다. 가장 넓은 프레임을 위에서 아래로(또는 root에서부터) 추적하면 리소스를 가장 많이 소비하는 호출 경로를 바로 찾을 수 있다.

## 2. flame graph vs icicle, diff view

전통적인 flame graph(Brendan Gregg가 고안한 원형)는 root가 <strong>맨 아래</strong>에 있고 위로 갈수록 깊은 호출을 쌓는다. <strong>icicle 그래프</strong>는 이를 상하로 뒤집은 형태로, root가 <strong>맨 위</strong>에 있고 아래로 갈수록 깊은 호출이 쌓인다. 담고 있는 정보는 동일하고 방향만 반대다. Pyroscope를 포함한 대부분의 웹 UI는 위에서 아래로 읽는 것이 자연스럽다는 이유로 icicle 방향을 기본값으로 채택하는 경우가 많다.

![flame graph는 root(main)가 맨 아래에 있고 handleRequest·dbQuery가 위로 쌓이는 전통 방향, icicle은 root가 맨 위에 있고 아래로 쌓이는 반전 방향으로, 담은 정보는 동일하고 Pyroscope UI는 보통 icicle을 기본으로 쓴다는 대비](/images/study-observability/27-flame-vs-icicle.png)

<strong>diff view</strong>는 두 시점(또는 두 버전)의 플레임그래프를 겹쳐서 비교한다. 동일한 콜 스택의 너비 차이를 색으로 표시해(보통 늘어난 프레임은 빨강, 줄어든 프레임은 파랑/초록 계열) 어느 함수가 새로 비싸졌는지 한눈에 드러낸다. 배포 전후 성능 회귀를 찾을 때, 두 개의 개별 플레임그래프를 눈으로 비교하는 것보다 diff view가 훨씬 빠르다.

## 3. 프로파일로 성능 진단 — 핫패스, 회귀

플레임그래프로 성능 문제를 진단하는 절차는 대체로 다음 순서를 따른다.

1. <strong>핫패스 찾기.</strong> 임의의 깊이에서 가장 넓은 프레임을 찾는다. 예상보다 비정상적으로 넓은 프레임이 있다면 그 함수가 리소스를 과도하게 소비하고 있다는 신호다.
2. <strong>형제 프레임 비교.</strong> 같은 부모 아래 있는 형제 프레임들의 너비를 비교해, 예상 밖으로 큰 비중을 차지하는 호출을 찾는다. 예를 들어 로깅 함수가 비즈니스 로직만큼 넓다면 로깅 오버헤드가 과도한 것이다.
3. <strong>버전 간 diff.</strong> `version` 라벨([26장](/study/observability/26-profile-types-ebpf) 태깅 참고)로 배포 전/후 프로파일을 구분해 diff view로 비교하면, 신규 배포가 만든 회귀를 정확히 특정할 수 있다.

alloc/inuse 메모리 프로파일에도 같은 방법론이 그대로 적용된다. inuse 프로파일에서 넓은 프레임은 "지금 메모리를 물고 있는" 코드 경로이므로, 메모리 누수를 의심할 때 가장 먼저 봐야 할 곳이다.

## 4. span profiles — 트레이스↔프로파일 연계

메트릭과 트레이스가 exemplar로 연결되듯([32장](/study/observability/32-signal-correlation) 참고), 트레이스와 프로파일은 <strong>span profiles</strong>로 연결된다. 핵심 아이디어는 프로파일 샘플에 현재 실행 중인 span의 `span_id`/`trace_id`를 동적 태그로 함께 기록하는 것이다. Go SDK 기준으로는 OpenTelemetry span이 시작되고 끝나는 구간 동안만 pprof 라벨에 `span_id`가 붙는다.

![span profiles 시퀀스: OTel SDK가 span을 시작(span_id=abc123)하면 span 활성 구간 동안 애플리케이션 코드가 실행 중 프로파일 샘플에 span_id를 태그로 부착하고, span 종료 후 그 구간의 샘플만 span_id로 필터해 Pyroscope에서 조회 가능한 흐름](/images/study-observability/27-span-profiles-sequence.png)

이렇게 되면 Tempo에서 특정 스팬을 열었을 때, 그 스팬이 정확히 실행된 시간 구간과 `span_id`로 필터링된 프로파일만 병합해 플레임그래프로 보여줄 수 있다. 트레이스가 "이 스팬이 200ms 걸렸다"를 알려줬다면, span profile은 그 200ms 안에서 정확히 어느 함수가 시간을 소비했는지 답한다 — [1장](/study/observability/01-monitoring-to-observability)에서 강조한 "신호는 연결될 때 가치가 생긴다"는 원칙의 실제 구현이다.

## 5. Grafana에서 통합 보기

Grafana는 Tempo의 트레이스 뷰 안에 <strong>"Profiles for this span"</strong> 같은 연계 링크를 제공해, 스팬을 클릭하면 그 스팬에 해당하는 span profile을 Pyroscope 패널에서 바로 열 수 있게 한다. 메트릭 exemplar에서 트레이스로 넘어가는 것과 동일한 UX 패턴이 트레이스에서 프로파일로 한 단계 더 이어지는 것이다.

Grafana Explore의 <strong>Explore Profiles</strong> 앱은 Pyroscope 데이터소스를 라벨·시간 범위로 탐색하며 플레임그래프·diff view를 그리는 전용 화면을 제공한다. 대시보드 패널로도 플레임그래프를 임베드할 수 있어, 서비스별 대시보드에 "현재 CPU 핫패스" 패널을 상시 배치하는 구성도 가능하다.

## 6. 실전 워크플로우

네 가지 신호가 실제로 맞물리는 흐름은 다음과 같다.

![실전 워크플로우: Alertmanager 알림 발화(p99 레이턴시 SLO 위반) → Tempo에서 느린 트레이스 조회(exemplar 진입) → 느린 스팬 특정 → Pyroscope span profile 조회 → 플레임그래프에서 핫패스 함수 특정 → 코드 수정·재배포 → diff view로 개선 확인으로 이어지는 근본 원인 추적 흐름](/images/study-observability/27-workflow.png)

알림이 "무엇이 잘못됐는가"를 알려주면, 트레이스가 "어느 요청·어느 스팬에서"로 좁히고, span profile이 "정확히 어느 함수 때문에"로 마무리 짓는다. 이 상관관계의 전체 그림은 [32장 시그널 상관관계](/study/observability/32-signal-correlation)에서 exemplar·derived field까지 포함해 종합적으로 다룬다. 지금까지는 각 신호가 개별적으로 무엇을 수집하고 어떻게 저장·질의되는지 다뤘다면, 다음은 이 모든 신호를 실제로 수집해 나르는 파이프라인 계층을 볼 차례다.

::: tip 핵심 정리
- 플레임그래프의 x축은 시간 순서가 아니라 샘플 집계 비중, y축은 스택 깊이(root에서 leaf까지)를 의미한다.
- flame graph와 icicle은 방향만 반대인 동일한 정보이며, Pyroscope UI는 보통 icicle 방향을 기본으로 쓴다.
- diff view는 두 시점/버전의 플레임그래프를 겹쳐 색으로 차이를 강조해 회귀를 빠르게 찾아낸다.
- 성능 진단은 핫패스(가장 넓은 프레임) 찾기 → 형제 프레임 비교 → 버전 간 diff의 순서로 진행한다.
- span profiles는 프로파일 샘플에 `span_id`를 동적 태그로 붙여, 트레이스의 특정 스팬과 정확히 대응하는 플레임그래프를 만들어낸다.
- 알림 → 트레이스 → span profile로 이어지는 흐름이 근본 원인을 함수 단위까지 좁히는 실전 상관관계 워크플로우다.
:::

## 다음 챕터

지금까지 메트릭·로그·트레이스·프로파일 네 신호 각각의 원리와 백엔드를 다뤘다. 이 신호들이 실제로 어떻게 수집돼 각 백엔드로 흘러 들어가는지는 아직 다루지 않았다. [Alloy 개요와 컴포넌트 모델](/study/observability/28-alloy-overview)에서는 Grafana Agent의 후속으로 등장한 Alloy가 네 신호를 하나의 통합 수집 파이프라인으로 어떻게 구성하는지 다룬다.
