---
title: "시그널 상관관계"
description: "메트릭·로그·트레이스·프로파일을 개별 도구가 아니라 하나의 관측성 시스템으로 만드는 상관관계 메커니즘을 다룬다. exemplar로 메트릭에서 트레이스로, derived field로 로그에서 트레이스로, span metrics로 트레이스에서 메트릭으로, span profiles로 트레이스에서 프로파일로 점프하는 Grafana의 통합 워크플로우를 정리한다."
date: 2026-07-02
tags: [Grafana, Correlation, Exemplar]
prev: /study/observability/31-grafana-datasources-dashboards
next: /study/observability/33-dashboard-as-code
---

# 시그널 상관관계

::: info 학습 목표
- 신호가 각각 고립돼 있으면 왜 관측성이 아니라 그냥 네 개의 모니터링 시스템에 불과한지 이해한다.
- exemplar로 메트릭 그래프에서 특정 요청의 트레이스로 점프하는 메커니즘을 익힌다.
- Tempo의 trace-to-logs 설정으로 트레이스에서 관련 로그로 이동하는 방법을 안다.
- trace-to-metrics와 logs-to-trace 양방향 연결 설정을 다룬다.
- span profiles로 특정 span 실행 구간의 플레임그래프를 바로 열람하는 trace-to-profiles를 이해한다.
- 이 모든 점프를 하나의 화면에서 이어가는 drill-down 워크플로우를 그릴 수 있다.
:::

## 1. 왜 상관관계가 관측성의 본질인가

[1장](/study/observability/01-monitoring-to-observability)에서 짚었듯, 메트릭·로그·트레이스를 각각 다른 도구에 다른 ID 체계로 쌓아두면 신호가 세 개 있어도 그냥 세 개의 분리된 모니터링 시스템이다. "에러율이 튄 시점의 원인 로그"를 찾으려면 사람이 타임스탬프를 손으로 맞추고, 서비스 이름으로 로그 저장소에 다시 검색을 걸어야 한다. 장애 대응 중 이 수작업 하나하나가 MTTR을 늘린다.

<strong>상관관계(correlation)</strong>는 이 수작업을 클릭 한 번으로 줄이는 메커니즘이다. Grafana는 이를 위해 신호 간 <strong>공통 식별자</strong>(trace ID, span ID, 시간 구간, 라벨)를 데이터소스 설정에 명시적으로 등록해두고, 패널에서 값을 클릭하면 그 식별자로 다른 데이터소스에 새 쿼리를 던지는 방식으로 점프를 구현한다.

![신호가 고립된 경우(메트릭→로그→트레이스를 수동으로 잇는 흐름)와 상관관계가 연결된 경우(메트릭에서 exemplar 클릭으로 트레이스, 다시 trace-to-logs·trace-to-profiles로 로그·플레임그래프로 점프하는 흐름)를 비교한 다이어그램](/images/study-observability/32-isolated-vs-correlated.png)

## 2. exemplar — 메트릭에서 트레이스로

<strong>Exemplar</strong>는 히스토그램/카운터의 특정 관측값에 trace ID를 붙여 저장하는 Prometheus 기능이다([OpenMetrics exemplar 스펙](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#exemplars) 기반). Prometheus 서버에서 `--enable-feature=exemplar-storage` 플래그로 활성화하며, 클라이언트 라이브러리가 요청 처리 시점에 현재 활성 span의 trace ID를 히스토그램 관측값과 함께 노출해야 한다.

```go
// Go 클라이언트 라이브러리 예시 — ExemplarObserver
histogram.(prometheus.ExemplarObserver).ObserveWithExemplar(
    duration.Seconds(),
    prometheus.Labels{"trace_id": span.SpanContext().TraceID().String()},
)
```

Grafana 쪽에서는 Prometheus 데이터소스 설정에 exemplar 대상을 등록한다.

```yaml
jsonData:
  exemplarTraceIdDestinations:
    - name: trace_id       # exemplar 라벨 이름
      datasourceUid: tempo-uid
```

이렇게 연결하면 Time series 패널에서 exemplar는 그래프 위에 작은 점으로 표시되고, 점을 클릭하면 해당 trace ID로 Tempo 데이터소스에 바로 쿼리가 나간다. 즉 "이 레이턴시 스파이크를 만든 실제 요청 하나"를 히스토그램 집계값에서 원시 트레이스로 곧장 파고들 수 있다.

![애플리케이션이 히스토그램 관측값에 exemplar(trace_id)를 붙여 Prometheus로 보내 exemplar-storage에 별도 보관하고, Grafana가 PromQL 쿼리로 시계열과 exemplar 포인트를 받아 그래프 위 점으로 렌더링한 뒤, 사용자가 점을 클릭하면 trace_id로 Tempo에서 트레이스를 조회해 반환하는 순서 다이어그램](/images/study-observability/32-exemplar-flow.png)

::: warning exemplar는 표본이지 전수가 아니다
Prometheus는 스크레이프당 히스토그램 버킷별로 최대 1개의 exemplar만 보관한다. 즉 exemplar는 "느린 요청의 대표 사례"이지 모든 느린 요청을 담지 못한다. 특정 요청을 반드시 추적해야 한다면 로그나 트레이스 자체의 검색 기능([18장 LogQL](/study/observability/18-logql), [23장 TraceQL](/study/observability/23-traceql-spanmetrics))에 의존해야 한다.
:::

## 3. trace-to-logs — Tempo에서 Loki로

트레이스를 열람하다 특정 span에서 무슨 로그가 찍혔는지 보고 싶을 때, Tempo 데이터소스의 <strong>Trace to logs</strong> 설정이 이 점프를 만든다.

```yaml
jsonData:
  tracesToLogsV2:
    datasourceUid: loki-uid
    spanStartTimeShift: '-1m'
    spanEndTimeShift: '1m'
    tags:
      - key: service.name
        value: service_name
      - key: k8s.pod.name
        value: pod
    filterByTraceID: true
    filterBySpanID: false
```

핵심은 두 가지다. 첫째, <strong>tags</strong>로 span의 어떤 속성(예: `service.name`)을 Loki 쿼리의 어떤 라벨(`service_name`)에 매핑할지 지정한다. span 속성과 로그 라벨의 이름이 다른 경우가 많으므로 이 매핑이 필수다. 둘째, <strong>spanStartTimeShift/spanEndTimeShift</strong>로 검색 시간창을 span 구간보다 앞뒤로 넓힌다. 로그의 타임스탬프가 span 시작·종료와 정확히 일치하지 않는 경우(비동기 로깅, 버퍼링)가 흔하기 때문이다. `filterByTraceID`/`filterBySpanID`를 켜면 derived field 대신 원문에서 ID로 직접 필터링한다.

이 설정이 있으면 트레이스 뷰에서 span을 우클릭해 "Logs for this span"을 선택하는 것만으로 해당 서비스·시간창·trace ID 조건이 자동으로 채워진 Loki 쿼리가 열린다.

## 4. trace-to-metrics · logs-to-trace

<strong>Trace-to-metrics</strong>는 span에서 관련 메트릭 쿼리로 점프하는 기능이다. Tempo 설정에서 Prometheus/Mimir 데이터소스를 지정하고, span의 서비스명·오퍼레이션명을 메트릭 쿼리의 라벨로 매핑한다. 이 기능은 [23장 TraceQL과 span metrics](/study/observability/23-traceql-spanmetrics)에서 다루는 Tempo의 <strong>metrics-generator</strong>가 만들어내는 `traces_spanmetrics_latency`, `traces_spanmetrics_calls_total` 같은 파생 메트릭과 함께 쓸 때 특히 유용하다. 트레이스 하나를 보다가 "이 오퍼레이션의 전체 트래픽 대비 레이턴시 추이"로 바로 확대해볼 수 있다.

```yaml
jsonData:
  tracesToMetrics:
    datasourceUid: prometheus-uid
    queries:
      - name: 'span 오퍼레이션 요청률'
        query: 'sum(rate(traces_spanmetrics_calls_total{$__tags}[$__rate_interval]))'
```

<strong>Logs-to-trace</strong>는 반대 방향으로, Loki 데이터소스에 <strong>derived field</strong>를 설정해 로그 라인에서 정규식으로 trace ID를 추출하고 이를 Tempo 링크로 바꾼다.

```yaml
jsonData:
  derivedFields:
    - datasourceUid: tempo-uid
      matcherRegex: 'trace_id=(\w+)'
      name: TraceID
      url: '$${__value.raw}'
```

로그 패널에서 `trace_id=4bf92f...` 같은 문자열이 매칭되면 해당 부분이 클릭 가능한 링크로 렌더링되고, 클릭하면 Tempo에서 그 트레이스를 바로 연다. exemplar가 "메트릭 → 트레이스"였다면, derived field는 "로그 → 트레이스"로 대칭을 이루는 셈이다.

## 5. trace-to-profiles — span profiles

가장 최근에 자리 잡은 연결이 <strong>trace-to-profiles</strong>다. Pyroscope의 언어별 SDK(Go, Java 등)는 span이 실행되는 동안 `pyroscope.profile.id` 같은 span 속성을 태깅해, "이 span이 실행된 정확한 시간 구간의 CPU 프로파일"을 조회할 수 있게 한다. 이를 <strong>span profiles</strong>라 부른다.

```yaml
jsonData:
  tracesToProfiles:
    datasourceUid: pyroscope-uid
    tags: ['service.name', 'k8s.pod.name']
    profileTypeId: 'process_cpu:cpu:nanoseconds:cpu:nanoseconds'
```

트레이스 뷰에서 특정 span을 선택하면 해당 서비스·시간창으로 좁혀진 Pyroscope 쿼리가 실행되고, 그 span이 실행되는 동안 CPU를 가장 많이 소비한 함수가 무엇인지 플레임그래프로 바로 보여준다. 이는 "레이턴시가 느린 span"에서 "느린 이유가 된 함수"까지 계측 코드 추가 없이 파고드는 마지막 연결 고리다. 플레임그래프 해석과 span 연계의 세부 내용은 [27장 플레임그래프와 트레이스 연계](/study/observability/27-flamegraph-trace-integration)에서 이어간다.

## 6. 통합 워크플로우 — 하나의 화면에서 drill-down

지금까지 다룬 네 가지 연결(exemplar, trace-to-logs, trace-to-metrics, trace-to-profiles)을 모두 설정해두면, 장애 대응자는 대시보드를 벗어나지 않고 원인을 좁혀갈 수 있다.

![SRE가 RED 대시보드에서 p99 레이턴시 스파이크와 exemplar 점을 확인하고, exemplar 클릭으로 Tempo에서 느린 span(특정 DB 호출)을 찾은 뒤, Logs for this span으로 Loki에서 에러 로그 없음을 확인하고, Profiles for this span으로 Pyroscope 플레임그래프에서 GC 시간 비중 급증을 발견해 근본 원인이 GC 압박임을 결론 내리는 drill-down 순서 다이어그램](/images/study-observability/32-drilldown-workflow.png)

이 흐름에서 SRE는 별도 도구를 열지도, ID를 손으로 복사하지도 않았다. 대시보드 → 트레이스 → 로그 → 프로파일로 이어지는 각 단계가 이전 단계의 컨텍스트(시간창, 서비스, span)를 그대로 물려받아 다음 쿼리를 자동 구성했기 때문이다. 이것이 "세 개의 기둥"이 아니라 진짜 관측성이 작동하는 방식이다 — 신호 각각의 존재가 아니라, 신호 사이를 잇는 배선이 가치를 만든다.

::: tip 핵심 정리
- 신호가 서로 연결돼 있지 않으면 관측성이 아니라 분리된 모니터링 시스템의 합에 불과하다.
- Exemplar는 히스토그램 관측값에 trace ID를 붙여 메트릭 그래프에서 트레이스로 점프하게 하지만, 전수가 아니라 표본이라는 한계가 있다.
- Trace-to-logs는 span 속성을 로그 라벨에 매핑하고 시간창을 앞뒤로 넓혀 관련 로그를 찾는다.
- Trace-to-metrics·logs-to-trace는 span metrics와 derived field로 각각 반대 방향 점프를 완성한다.
- Trace-to-profiles(span profiles)는 span 실행 구간에 정확히 맞춘 플레임그래프를 열어 코드 라인 수준까지 근본 원인을 좁힌다.
- 네 연결을 모두 설정하면 대시보드-트레이스-로그-프로파일을 한 화면 흐름으로 drill-down할 수 있다.
:::

## 다음 챕터

지금까지 만든 대시보드와 데이터소스 연결, 상관관계 설정은 대부분 UI로 클릭해 구성했다. 하지만 이런 설정을 UI에만 의존하면 재현이 불가능하고 버전 관리도 안 된다. 다음 챕터 [대시보드 as-code](/study/observability/33-dashboard-as-code)에서는 jsonnet/grafonnet, provisioning, Terraform provider로 이 모든 설정을 코드로 관리하는 방법을 다룬다.
