---
title: "PromQL/LogQL/TraceQL 치트시트"
description: "Prometheus PromQL, Loki LogQL, Tempo TraceQL에서 실무에 자주 쓰는 쿼리 패턴을 언어별로 코드 예제와 함께 정리한 레퍼런스. rate·histogram_quantile·burn rate부터 로그 파싱, 트레이스 구조 연산자까지 다룬다."
date: 2026-07-02
tags: [PromQL, LogQL, TraceQL, Cheatsheet]
prev: /study/observability/appendix-glossary
next: /study/observability/appendix-references
---

# PromQL/LogQL/TraceQL 치트시트

메트릭·로그·트레이스 각 신호를 실전에서 조사할 때 손에 익혀두면 시간을 아끼는 쿼리 패턴을 모았다. 문법 세부는 [PromQL 기초](/study/observability/09-promql-basics), [LogQL](/study/observability/18-logql), [TraceQL과 span metrics](/study/observability/23-traceql-spanmetrics)에서 더 깊이 다룬다.

## PromQL — rate와 increase

Counter의 증가율을 볼 때는 항상 `rate`를 쓴다. 순간값이 아니라 구간 평균 증가율이므로 재시작으로 인한 카운터 리셋을 자동 보정한다.

```promql
rate(http_requests_total[5m])
```

특정 구간 동안의 총 증가량(예: 지난 1시간 동안 발생한 요청 수)이 필요하면 `increase`를 쓴다.

```promql
increase(http_requests_total[1h])
```

## PromQL — histogram_quantile로 p99 계산

히스토그램 버킷을 `le` 라벨 기준으로 집계한 뒤 분위수를 추정한다. `by`에 `le`를 반드시 남겨야 한다.

```promql
histogram_quantile(
  0.99,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, job)
)
```

## PromQL — 집계 연산자 (by / without)

`by`는 지정한 라벨만 남기고, `without`은 지정한 라벨만 버린다. 카디널리티가 높은 `instance`를 뺄 때는 `without`이, 소수의 관심 라벨만 남길 때는 `by`가 편하다.

```promql
sum(rate(http_requests_total[5m])) by (job, status_code)

sum(rate(http_requests_total[5m])) without (instance, pod)
```

## PromQL — 벡터 매칭 (on / ignoring, group_left)

서로 다른 메트릭을 라벨로 join할 때는 `on`/`ignoring`으로 매칭 라벨을 명시하고, 카디널리티가 다른 쪽(1:N)에는 `group_left`/`group_right`를 붙인다.

```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) by (job)
/ on(job)
sum(rate(http_requests_total[5m])) by (job)

kube_pod_info * on(node) group_left(instance_type)
  kube_node_labels
```

## PromQL — SLO burn rate

에러 버짓 소진 속도를 짧은 창(fast burn)과 긴 창(slow burn)으로 동시에 관찰하는 multi-window burn rate 패턴이다.

```promql
(
  sum(rate(http_requests_total{status=~"5.."}[5m]))
  /
  sum(rate(http_requests_total[5m]))
) > (14.4 * (1 - 0.999))
```

## PromQL — up (타겟 상태)

`up`은 Prometheus가 자동으로 노출하는 메트릭으로, 스크레이프 성공 여부(1/0)를 나타낸다. 타겟 다운을 감지하는 가장 기본적인 신호다.

```promql
up{job="node-exporter"} == 0
```

## LogQL — 스트림 셀렉터

중괄호 안의 라벨 매처로 로그 스트림을 먼저 좁힌 뒤, 라인 필터(`|=`, `!=`, `|~`, `!~`)로 본문을 필터링한다.

```logql
{namespace="checkout", app="api"} |= "timeout" != "healthcheck"
```

## LogQL — json 파서

로그 라인이 JSON이면 `| json`으로 필드를 라벨처럼 추출해 이후 필터·집계에 쓸 수 있다.

```logql
{app="api"}
  | json
  | status_code = `500`
  | line_format "{{.msg}}"
```

## LogQL — rate와 count_over_time

로그 스트림을 메트릭으로 변환하는 함수들이다. `count_over_time`은 구간 내 로그 라인 수, `rate`는 초당 라인 수를 계산한다.

```logql
sum(rate({app="api"} |= "error" [5m])) by (namespace)

sum(count_over_time({app="api"}[1h])) by (pod)
```

## LogQL — unwrap

로그 라인 안의 숫자 값(예: 응답 시간)을 추출해 히스토그램·평균 같은 메트릭 함수에 넣을 때 `unwrap`을 쓴다.

```logql
quantile_over_time(0.99,
  {app="api"} | json | unwrap duration_ms [5m]
) by (route)
```

## TraceQL — 속성 필터

span 속성(리소스 속성 포함)을 key-value로 필터링한다. `resource.`와 span 속성은 동일한 문법으로 조회한다.

```traceql
{ span.http.status_code = 500 && resource.service.name = "checkout" }
```

## TraceQL — duration 필터

특정 지연 이상의 span 또는 트레이스를 찾을 때 `duration`을 쓴다.

```traceql
{ span.http.method = "POST" && duration > 500ms }
```

## TraceQL — 구조 연산자

부모-자식, 후손 관계 같은 span 간 구조를 화살표 연산자로 표현한다. `>>`는 후손(descendant), `>`는 직계 자식을 뜻한다.

```traceql
{ resource.service.name = "gateway" } >> { span.http.status_code = 500 }
```

## TraceQL — 집계

트레이스/span 집합에 대해 `count`, `avg`, `sum` 같은 집계 함수를 적용해 span metrics 스타일 결과를 뽑는다.

```traceql
{ resource.service.name = "checkout" } | count() by (span.http.status_code)
```

이어지는 [참고 자료](/study/observability/appendix-references)에서는 여기 정리한 쿼리 문법의 공식 레퍼런스와 더 깊이 파고들 자료를 모았다.
