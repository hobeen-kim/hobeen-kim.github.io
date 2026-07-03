---
title: "관측성의 4대 신호"
description: "메트릭·로그·트레이스·프로파일 네 가지 신호가 각각 어떤 질문에 답하는지, 저장 비용과 카디널리티 제약이 어떻게 다른지 비교한다. 신호를 단독으로 쓸 때의 한계와, exemplar·상관관계로 신호를 엮었을 때 비로소 얻는 힘을 정리한다."
date: 2026-07-02
tags: [Observability, Metrics, Logs, Traces, Profiles]
prev: /study/observability/01-monitoring-to-observability
next: /study/observability/03-stack-overview
---

# 관측성의 4대 신호

::: info 학습 목표
- 메트릭이 무엇을 집계하고, 왜 저비용이면서도 카디널리티 제약을 갖는지 설명할 수 있다.
- 로그가 이산 이벤트를 어떻게 담고, 왜 고맥락·고비용 신호인지 이해한다.
- 트레이스가 요청의 전체 수명주기와 분산 인과관계를 어떻게 표현하는지 안다.
- 프로파일이 코드 레벨 리소스 소비를 드러내는 네 번째 신호로 자리 잡은 배경을 이해한다.
- 네 신호를 비용·카디널리티·질문 유형 축으로 비교할 수 있다.
- 신호가 개별로 존재할 때와 상관관계로 연결됐을 때의 가치 차이를 파악한다.
:::

## 1. 메트릭 — 집계 수치

<strong>메트릭</strong>은 시간에 따라 변하는 수치를 이름과 라벨(레이블) 집합으로 식별해 저장하는 신호다. `http_requests_total{method="GET", status="200"}` 같은 형태로, 특정 시점의 값이 아니라 <strong>시계열(time series)</strong>로 누적된다. Prometheus 데이터 모델을 기준으로 하면 하나의 시계열은 메트릭 이름 + 라벨 조합으로 유일하게 식별된다.

메트릭의 강점은 <strong>저비용</strong>이다. 이벤트 하나하나를 저장하는 대신 카운터·게이지·히스토그램으로 미리 집계하기 때문에, 저장 공간이 트래픽량이 아니라 시계열 개수에 비례한다. 요청이 초당 10건이든 10만 건이든, 라벨 조합이 고정돼 있으면 저장 비용은 거의 동일하다. 대신 이 구조가 곧 <strong>카디널리티 제약</strong>이 된다. 라벨에 `user_id`나 `request_id`처럼 유일값이 많은 차원을 넣으면 시계열 개수가 폭발하고, TSDB 메모리와 인덱스가 감당하지 못한다. "어떤 사용자가 느렸는가" 같은 개별 질문에는 메트릭이 원천적으로 약하다 — 이 한계가 로그·트레이스가 필요한 이유다. 카디널리티 폭발의 구조는 [4장](/study/observability/04-pull-push-cardinality)과 [34장](/study/observability/34-cardinality-cost)에서 자세히 다룬다.

```promql
# 5xx 에러율 (집계된 수치 — 어떤 요청이 실패했는지는 알 수 없다)
sum(rate(http_requests_total{status=~"5.."}[5m]))
  / sum(rate(http_requests_total[5m]))
```

## 2. 로그 — 이산 이벤트

<strong>로그</strong>는 특정 시점에 발생한 개별 이벤트를 텍스트나 구조화 데이터로 기록한 신호다. `2026-07-02T10:00:00Z level=error msg="payment failed" order_id=8231 user_id=552`처럼, 이벤트 하나에 임의의 개수·임의의 카디널리티 필드를 자유롭게 붙일 수 있다는 점이 메트릭과 결정적으로 다르다. 메트릭이 답하지 못하는 "이 특정 주문이 왜 실패했는가"는 로그가 답한다.

대신 로그는 <strong>고맥락(high-context)</strong>인 만큼 <strong>고비용</strong>이다. 요청량에 비례해 볼륨이 선형으로 늘고, 전문(full-text) 인덱싱을 하면 저장·질의 비용이 급격히 커진다. Loki는 이 문제를 라벨만 인덱싱하고 로그 본문은 압축해 오브젝트 스토리지에 넣는 방식으로 절충한다([16장](/study/observability/16-loki-architecture)). 구조화 로깅(JSON 등)과 적절한 샘플링·보존 정책 없이 로그를 무분별하게 쌓으면, 관측성 비용에서 가장 먼저 예산을 잡아먹는 신호가 로그다.

```logql
{namespace="checkout"} |= "payment failed" | json | user_id="552"
```

## 3. 트레이스 — 요청 수명 전체

<strong>트레이스</strong>는 하나의 요청이 시스템을 가로지르는 전체 여정을 <strong>span</strong>의 트리 구조로 기록한다. 각 span은 시작·종료 시각, 소속 서비스, 부모-자식 관계, 속성(attribute)을 갖고, 이 span들을 trace ID로 묶으면 "이 요청이 어떤 서비스를 어떤 순서로, 각각 얼마나 걸려 통과했는가"가 그대로 드러난다.

트레이스의 본질은 <strong>분산 인과관계</strong>를 보존한다는 점이다. 메트릭은 "결제 서비스의 p99가 느리다"까지만 말하지만, 트레이스는 "이 특정 요청에서 결제 서비스가 느린 이유는 하위의 재고 서비스 호출이 300ms 걸렸기 때문"이라는 인과 사슬을 보여준다. 대신 트레이스도 요청량에 비례해 볼륨이 커지므로, 실무에서는 전수 수집 대신 <strong>샘플링</strong>(head-based/tail-based)으로 비용을 통제한다. 분산 트레이싱의 원리와 context propagation은 [20장](/study/observability/20-distributed-tracing-basics)에서 다룬다.

![Client가 API Gateway에 POST /checkout(trace_id=abc123)을 보내면 charge()·reserve_stock() span이 Payment·Inventory 서비스로 이어지고, 재고 호출이 300ms 걸린 인과 사슬이 하나의 trace_id로 묶인 4개 span 시퀀스](/images/study-observability/02-trace-sequence-light.png)
![Client가 API Gateway에 POST /checkout(trace_id=abc123)을 보내면 charge()·reserve_stock() span이 Payment·Inventory 서비스로 이어지고, 재고 호출이 300ms 걸린 인과 사슬이 하나의 trace_id로 묶인 4개 span 시퀀스](/images/study-observability/02-trace-sequence-dark.png)

## 4. 프로파일 — 코드 레벨 리소스 소비

<strong>프로파일</strong>은 CPU 사이클, 메모리 할당, 락 대기 시간 같은 리소스 소비를 <strong>함수 호출 스택 단위</strong>로 기록하는 신호다. "결제 서비스가 CPU를 많이 쓴다"(메트릭 수준)를 넘어 "그 CPU의 40%가 JSON 직렬화 함수에서 소모된다"(코드 라인 수준)까지 답할 수 있다는 점에서, 최근에는 메트릭·로그·트레이스에 이어 <strong>네 번째 신호</strong>로 꼽힌다.

전통적 프로파일링은 필요할 때 수동으로 붙여 몇 분 실행하고 떼는 방식이었지만, Pyroscope 같은 <strong>연속 프로파일링(continuous profiling)</strong> 도구는 낮은 오버헤드(대개 CPU 1~3% 수준)로 프로덕션에 상시 켜둘 수 있다. eBPF 기반 프로파일러는 애플리케이션 코드 변경 없이도 커널 레벨에서 스택을 샘플링한다. 프로파일은 [24장](/study/observability/24-continuous-profiling-basics)부터 본격적으로 다룬다.

## 5. 신호별 트레이드오프

네 신호는 비용·카디널리티·질문 유형이 뚜렷하게 갈린다. 어떤 신호를 어디에 먼저 투자할지 판단할 때 이 표가 기준이 된다.

| 신호 | 데이터 형태 | 저장 비용 | 카디널리티 허용치 | 답하는 질문 |
|---|---|---|---|---|
| 메트릭 | 집계 시계열 | 낮음 | 낮음 (라벨 조합 제한) | "얼마나 자주/많이?" |
| 로그 | 이산 이벤트 | 높음 | 높음 (필드 자유) | "정확히 무슨 일이?" |
| 트레이스 | span 트리 | 중간 (샘플링 의존) | 높음 (요청 단위) | "어디서, 왜 느렸나?" |
| 프로파일 | 스택 샘플 | 중간 (지속 수집 시) | 해당 없음 (코드 라인 축) | "무엇이 리소스를 쓰나?" |

일반적인 운영 원칙은 <strong>메트릭으로 이상을 감지하고, 트레이스로 어느 구간인지 좁히고, 로그로 정확한 원인을 확인하고, 프로파일로 코드 레벨 병목을 잡는다</strong>는 흐름이다. 각 신호를 단독으로 최대치까지 수집하려 하기보다, 이 역할 분담에 맞춰 예산을 배분하는 편이 비용 대비 효과가 높다.

## 6. 신호는 연결될 때 강력하다

네 신호를 아무리 잘 골라도, 서로 다른 시스템에 서로 다른 ID로 흩어져 있으면 장애 대응자는 여전히 수동으로 신호를 오간다. 이 문제를 푸는 핵심 메커니즘이 <strong>exemplar</strong>다. Prometheus 히스토그램 메트릭에 trace ID를 exemplar로 붙여두면, Grafana 대시보드에서 레이턴시 스파이크 지점을 클릭해 바로 그 요청의 트레이스로 이동할 수 있다. 트레이스에서는 span에 붙은 로그 라벨(예: `trace_id`, `span_id`)로 Loki의 관련 로그를 곧바로 조회하고, span의 서비스·시간 범위로 Pyroscope 프로파일까지 이어갈 수 있다.

![메트릭에서 레이턴시 스파이크를 감지하면 exemplar로 트레이스의 느린 span을 특정하고, trace_id 라벨로 로그의 에러 상세를, span 시간·서비스로 프로파일의 코드 레벨 병목을 확인하는 상관관계 흐름](/images/study-observability/02-signal-correlation-light.png)
![메트릭에서 레이턴시 스파이크를 감지하면 exemplar로 트레이스의 느린 span을 특정하고, trace_id 라벨로 로그의 에러 상세를, span 시간·서비스로 프로파일의 코드 레벨 병목을 확인하는 상관관계 흐름](/images/study-observability/02-signal-correlation-dark.png)

이 상관관계 흐름을 실제로 Grafana에서 구성하는 방법(derived field, exemplar 설정, TraceQL 연동)은 [32장 시그널 상관관계](/study/observability/32-signal-correlation)에서 설정 예제와 함께 다룬다. 지금 단계에서 기억할 것은 하나다 — <strong>신호 수집 자체는 관측성의 절반일 뿐이고, 나머지 절반은 신호를 잇는 배선</strong>이라는 점이다.

::: tip 핵심 정리
- 메트릭은 저비용 집계 신호지만 카디널리티 제약으로 "얼마나"만 답하고 "누가/왜"는 답하지 못한다.
- 로그는 임의 필드를 담는 고맥락 신호인 만큼 볼륨과 비용이 요청량에 비례해 커진다.
- 트레이스는 요청의 분산 인과관계를 span 트리로 보존하며, 샘플링으로 비용을 통제한다.
- 프로파일은 리소스 소비를 함수 호출 스택 단위까지 좁히는 네 번째 신호로, 연속 프로파일링이 상시 운영을 가능하게 한다.
- 네 신호는 비용·카디널리티·질문 유형이 다르므로 역할 분담(감지→좁히기→원인 확인→코드 레벨 확인)에 맞춰 예산을 배분한다.
- exemplar·trace ID·span 라벨로 신호를 상관관계로 엮어야 비로소 관측성이라는 이름에 걸맞은 힘이 나온다.
:::

## 다음 챕터

네 신호가 각각 무엇을 답하는지 봤으니, 이제 이 신호들을 실제로 어떤 오픈소스 컴포넌트가 수집·저장·질의하는지 볼 차례다. [Grafana 관측성 스택 개요](/study/observability/03-stack-overview)에서는 LGTM+ 스택의 구성과, exporter·OpenTelemetry Collector·Alloy 중 무엇을 언제 써야 하는지 다룬다.
