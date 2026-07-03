---
title: "데이터 모델과 시계열"
description: "metric name과 라벨 조합이 시계열을 식별하는 방식, Counter·Gauge·Histogram·Summary 네 메트릭 타입의 차이와 집계 가능성, native histogram과 노출 형식, 라벨 설계 원칙까지 Prometheus 데이터 모델을 정리한다."
date: 2026-07-02
tags: [Prometheus, Metrics, Histogram]
prev: /study/observability/05-prometheus-architecture
next: /study/observability/07-scraping-service-discovery
---

# 데이터 모델과 시계열

::: info 학습 목표
- metric name과 라벨 집합이 어떻게 하나의 시계열(sample stream)을 유일하게 식별하는지 이해한다.
- Counter·Gauge·Histogram·Summary 네 메트릭 타입의 동작 방식과 쓰임을 구분한다.
- Histogram과 Summary의 client-side/server-side 계산 차이와 집계 가능성 트레이드오프를 판단한다.
- Native histogram의 동작 원리와 기존 histogram 대비 카디널리티 이점을 안다.
- 노출 형식(text exposition, OpenMetrics)과 실전 라벨 설계 원칙을 익힌다.
:::

## 1. 시계열 데이터 모델

Prometheus에서 모든 데이터는 <strong>시계열(time series)</strong>로 저장된다. 하나의 시계열은 <strong>metric name과 라벨(label) 집합의 조합</strong>으로 유일하게 식별되고, 그 아래에 `(timestamp, float64 value)` 샘플이 시간순으로 쌓인다.

```
http_requests_total{method="GET", status="200", job="api", instance="10.0.0.5:8080"}
```

이 한 줄이 하나의 시계열 식별자다. `method`, `status`, `job`, `instance` 라벨 값 중 하나라도 다르면 완전히 별개의 시계열이 된다. 내부적으로는 metric name조차 `__name__`이라는 예약 라벨일 뿐이다. 즉 위 시계열은 실제로는 `{__name__="http_requests_total", method="GET", status="200", job="api", instance="10.0.0.5:8080"}`라는 순수한 라벨 집합으로 취급된다. `{__name__="http_requests_total"}`처럼 라벨 매처만으로 조회하는 것이 가능한 이유가 여기 있다.

![시계열 식별 구조 — metric name(__name__)과 method·status·job·instance 라벨들이 결합해 유일한 시계열 ID(라벨 집합 조합)를 이루고, 그 아래에 (t1,v1)(t2,v2)… 샘플 스트림이 append되는 관계](/images/study-observability/06-timeseries-id.png)

라벨 값을 하나 바꾸는 것은 새 시계열을 만드는 것과 같다. 예컨대 `status="200"`과 `status="404"`는 서로 다른 두 시계열이며, `method`, `status`의 카디널리티(가능한 값의 조합 수)만큼 시계열 개수가 곱셈으로 늘어난다. 이 폭발 메커니즘은 [04장](/study/observability/04-pull-push-cardinality)에서 다룬 카디널리티 문제의 근본 원인이다.

## 2. 메트릭 타입

Prometheus는 네 가지 메트릭 타입을 정의한다. 타입 정보는 클라이언트 라이브러리와 노출 형식(`# TYPE`)에만 존재하고, TSDB 저장 단계에서는 결국 모두 동일한 실수 시계열로 저장된다는 점이 중요하다 — 타입은 <strong>클라이언트의 계약이자 PromQL 함수 선택의 힌트</strong>이지, 저장 포맷 차이가 아니다.

- <strong>Counter</strong>는 단조 증가만 하는 누적 카운터다. 재시작하면 0으로 리셋된다. 값 자체를 보는 것이 아니라 항상 `rate()`나 `increase()`로 감싸서 증가율을 본다. Prometheus 클라이언트는 리셋을 자동 감지해 `rate()` 계산 시 보정한다.
  ```promql
  rate(http_requests_total{status="500"}[5m])
  ```
- <strong>Gauge</strong>는 오르내릴 수 있는 순간값이다. 현재 메모리 사용량, 큐 길이, 동시 연결 수처럼 "지금 값이 얼마인가"를 나타낸다. `rate()`를 쓰지 않고 값 자체나 `delta()`, `deriv()`를 쓴다.
- <strong>Histogram</strong>은 관측값을 미리 정의된 버킷(bucket)에 누적 카운트하는 타입이다. `_bucket{le="..."}`, `_sum`, `_count` 세 종류의 시계열을 함께 노출한다. 버킷 경계를 넘는 값의 누적 개수를 세는 방식이라 <strong>client-side에서는 버킷 카운팅만</strong> 하고, 분위수(quantile) 계산은 쿼리 시점에 PromQL의 `histogram_quantile()`이 담당한다.
- <strong>Summary</strong>는 분위수를 <strong>client-side에서 직접 계산</strong>해 φ-quantile로 노출한다(`{quantile="0.5"}`, `{quantile="0.9"}` 등). `_sum`, `_count`도 함께 노출하지만 `_bucket`은 없다.

## 3. Histogram vs Summary — client-side와 server-side, 그리고 집계 가능성

둘 다 분포와 지연시간류 지표를 다루지만, <strong>어디서 분위수를 계산하는가</strong>가 근본적인 차이를 만든다.

![Histogram vs Summary 비교 — Histogram은 클라이언트가 버킷 카운트만 누적하고 여러 인스턴스 버킷을 sum by (le)로 합산한 뒤 PromQL histogram_quantile()로 쿼리 시점에 분위수를 계산해 집계 가능하지만, Summary는 클라이언트가 분위수를 직접 계산해 노출하므로 인스턴스별 값이 확정되어 여러 인스턴스 quantile을 평균·합산해도 의미 없어 집계 불가](/images/study-observability/06-histogram-vs-summary.png)

| 구분 | Histogram | Summary |
|---|---|---|
| 분위수 계산 위치 | 서버(PromQL, 쿼리 시점) | 클라이언트(계측 시점) |
| 노출되는 것 | `_bucket{le}`, `_sum`, `_count` | `{quantile}`, `_sum`, `_count` |
| 다중 인스턴스 집계 | 가능 — 버킷을 `sum by (le)`로 합친 뒤 `histogram_quantile()` | 불가능 — quantile 값끼리 평균 내면 수학적으로 틀린다 |
| 정확도 | 버킷 경계 사이 선형 보간 → 근사치 | 스트리밍 알고리즘 기반 정확한 값(인스턴스 단위) |
| 버킷/분위수 설계 | 배포 전 버킷 경계를 미리 정해야 함(도메인 지식 필요) | 배포 시점에 원하는 quantile 목록 지정 |
| 클라이언트 비용 | 낮음(카운터 증가만) | 상대적으로 높음(슬라이딩 윈도 계산) |

<strong>집계 가능성</strong>이 실무에서 가장 크게 갈리는 지점이다. Kubernetes 환경처럼 Pod가 여러 개인 서비스의 p99 레이턴시를 보고 싶다면 Histogram을 써야 한다. 각 Pod가 노출한 `_bucket{le}` 시계열을 `sum by (le) (rate(...))`로 먼저 합산한 뒤 `histogram_quantile()`을 적용하면 서비스 전체의 분위수를 낼 수 있다.

```promql
histogram_quantile(0.99,
  sum by (le) (rate(http_request_duration_seconds_bucket[5m]))
)
```

Summary는 이 합산이 원천적으로 불가능하다. 인스턴스 A의 p99가 200ms, 인스턴스 B의 p99가 50ms라고 해서 전체 p99가 그 평균인 125ms가 되는 것이 아니다. 분위수는 분포 전체를 알아야 계산되는 값이라 사후에 합칠 수 없다. 이런 이유로 실무에서는 <strong>여러 인스턴스를 집계해야 하는 서비스 레벨 지표는 거의 항상 Histogram을 택한다.</strong> Summary는 인스턴스 단위로만 정확한 값이 필요하고 집계가 필요 없는 특수한 경우(예: 단일 프로세스 GC pause 시간)에 한정해 쓴다.

## 4. Native histograms

기존 Histogram의 가장 큰 실무 약점은 <strong>카디널리티</strong>다. 버킷 경계마다 별도 시계열이 생기므로 `le` 값이 10개면 시계열도 10배가 된다. 여기에 다른 라벨(엔드포인트, 상태 코드 등)까지 곱해지면 카디널리티가 빠르게 불어난다.

<strong>Native histogram</strong>(최신 Prometheus 기준 기능)은 이 문제를 근본적으로 다르게 푼다. 버킷 경계를 사용자가 미리 정의하는 대신, <strong>지수적으로 증가하는 버킷 스킴</strong>을 자동 적용하고 그 버킷 카운트 전체를 <strong>하나의 시계열 안에 sparse 표현으로 압축</strong>해 저장한다. 즉 `le`별로 시계열을 쪼개지 않고, 단일 시계열의 값 자체가 "버킷 카운트 벡터"를 담는다.

![Classic vs Native Histogram 카디널리티 비교 — Classic은 le=0.1·0.5·1·+Inf 버킷 경계마다 별도 시계열이 생겨 버킷 수만큼 시계열이 배수로 증가하지만, Native는 값 자체가 sparse 버킷 벡터인 단일 시계열에 지수 스킴 버킷을 담아 버킷 수와 무관하게 시계열 하나로 고해상도를 유지](/images/study-observability/06-native-histogram.png)

이점은 두 가지다. 첫째, <strong>카디널리티가 버킷 개수와 무관</strong>해진다 — 버킷이 몇 개든 시계열은 여전히 하나다. 둘째, <strong>해상도가 훨씬 높다.</strong> 클래식 히스토그램은 배포 전에 정한 소수의 버킷 경계에 갇히지만, native histogram은 지수 스킴 덕분에 사실상 연속에 가까운 해상도로 분포를 표현한다. PromQL 쪽에서는 `histogram_quantile()`을 그대로 쓸 수 있어 마이그레이션 부담이 적다.

다만 아직 진화 중인 기능이라 주의가 필요하다. 서버에서 `--enable-feature=native-histograms` 같은 기능 플래그가 필요하고, 클라이언트 라이브러리도 native histogram을 지원하는 버전이어야 한다. 원격 저장(remote_write) 프로토콜과 다운스트림(Grafana, Mimir 등) 지원 범위도 계속 확장 중이므로, 도입 전 각 컴포넌트의 버전과 지원 상태를 확인해야 한다.

## 5. 노출 형식 — text exposition과 OpenMetrics

Prometheus가 스크레이프하는 `/metrics` 응답은 사람이 읽을 수 있는 텍스트 형식이다.

```text
# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",status="200"} 27364
http_requests_total{method="POST",status="500"} 12

# HELP http_request_duration_seconds Request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 24054
http_request_duration_seconds_bucket{le="0.5"} 27301
http_request_duration_seconds_bucket{le="1"} 27350
http_request_duration_seconds_bucket{le="+Inf"} 27376
http_request_duration_seconds_sum 8734.2
http_request_duration_seconds_count 27376
```

`# HELP`로 설명, `# TYPE`으로 타입을 선언하고, 이후 라인이 실제 샘플이다. 이 포맷을 Prometheus 진영에서는 <strong>text-based exposition format</strong>이라 부른다.

<strong>OpenMetrics</strong>는 이 포맷을 CNCF 표준으로 정식화한 상위 호환 규격이다. 몇 가지가 다르다.

- 응답 끝에 `# EOF` 라인을 강제해 응답이 잘리지 않았음을 보장한다.
- <strong>Exemplar</strong>를 지원한다. 히스토그램 버킷 라인 끝에 `# {trace_id="..."} 값 타임스탬프` 형태로 특정 관측값을 만든 트레이스를 매달 수 있어, 메트릭에서 트레이스로 바로 점프하는 상관관계([32장](/study/observability/32-signal-correlation) 참고)의 기반이 된다.
- Counter에 `_total` 접미사를 명세 차원에서 강제한다.

Prometheus는 스크레이프 시 타깃이 `Content-Type: application/openmetrics-text`로 응답하면 OpenMetrics로 파싱하고, 그렇지 않으면 기존 text 포맷으로 처리한다. 최신 클라이언트 라이브러리는 대부분 OpenMetrics 노출도 지원한다. 공식 스펙은 [OpenMetrics 프로젝트](https://openmetrics.io/)에 정리돼 있다.

## 6. 라벨 설계 원칙

라벨 설계는 나중에 바꾸기 어렵다. 대시보드·알림 규칙·다른 팀의 쿼리가 라벨 이름에 의존하기 시작하면 변경 비용이 눈덩이처럼 불어난다. [Prometheus 네이밍 가이드](https://prometheus.io/docs/practices/naming/)가 정리한 원칙을 실전 기준으로 요약한다.

- <strong>metric name은 `snake_case`, base unit, `_total` 접미사</strong> 세 가지를 지킨다. `http_request_duration_seconds`처럼 밀리초가 아닌 초 단위(base unit)를 쓰고, Counter에는 `_total`을 붙인다(`http_requests_total`). 단위를 이름 끝에 명시하면(`_bytes`, `_seconds`) 쿼리 작성자가 변환 실수를 하지 않는다.
- <strong>`__`(더블 언더스코어)로 시작하는 라벨은 Prometheus 내부 예약</strong>이다. `__name__`, `__address__`, 그리고 relabeling 단계에서만 보이는 `__meta_*` 라벨들이 여기 속한다. 사용자가 직접 이 네임스페이스에 라벨을 만들면 안 된다 — 실제로 만들어도 최종 relabel 단계에서 `__`로 시작하는 라벨은 자동으로 버려진다(내부용이므로).
- <strong>`job`과 `instance`는 Prometheus가 자동으로 붙이는 예약 라벨</strong>이다. `job`은 `scrape_config`의 `job_name`, 즉 "무슨 서비스인가"를 나타낸다. `instance`는 `__address__`(보통 `host:port`), 즉 "그 서비스의 어느 개별 타깃인가"를 나타낸다. 이 둘의 조합이 사실상 "어떤 프로세스에서 온 데이터인가"를 결정한다.
- <strong>카디널리티가 무한할 수 있는 값은 라벨로 쓰지 않는다.</strong> 사용자 ID, 이메일, 요청 URL의 쿼리 파라미터, 타임스탬프 등을 라벨에 넣으면 시계열이 무한 증식한다. 이 값들이 필요하면 로그([16장](/study/observability/16-loki-architecture) 이후) 쪽에 남기는 것이 맞다. 04장에서 다룬 카디널리티 폭발의 실제 진입점이 바로 이 실수다.
- 라벨은 <strong>측정 대상을 분해하는 차원(dimension)</strong>이어야 한다. `status`, `method`, `region`처럼 값의 종류가 유한하고 예측 가능한 것만 라벨로 승격시킨다.

::: tip 핵심 정리
- 시계열은 metric name(`__name__`)과 라벨 집합의 조합으로 유일하게 식별되며, 라벨 값 하나가 바뀌면 새 시계열이 된다.
- Counter는 `rate()`로, Gauge는 값 자체로, Histogram은 버킷 카운트로, Summary는 client-side 분위수로 다룬다.
- Histogram은 버킷을 서버(PromQL)에서 집계·계산하므로 다중 인스턴스 합산이 가능하지만, Summary의 quantile은 사후 집계가 불가능하다.
- Native histogram은 지수 버킷과 sparse 표현으로 버킷 수와 무관하게 카디널리티를 낮게 유지하면서 해상도를 높인다.
- OpenMetrics는 text exposition format의 CNCF 표준화 버전으로, EOF 마커와 exemplar를 추가로 지원한다.
- 라벨 설계는 base unit·`_total` 접미사·예약 네임스페이스(`__`)·유한한 카디널리티 원칙을 지켜야 나중에 비용이 커지지 않는다.
:::

## 다음 챕터

[스크레이핑과 서비스 디스커버리](/study/observability/07-scraping-service-discovery)에서는 scrape_config의 실제 구조, kubernetes_sd를 비롯한 서비스 디스커버리 메커니즘, 그리고 relabeling으로 타깃과 라벨을 정교하게 통제하는 방법을 다룬다.
