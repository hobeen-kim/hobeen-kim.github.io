---
title: "Recording·Alerting Rule"
description: "비싼 쿼리를 사전 계산하는 Recording Rule의 명명 규칙, Alerting Rule의 expr/for/labels/annotations 구조, 룰 그룹의 순차 평가와 for의 pending/firing 상태 전이, 룰 성능 튜닝과 promtool을 이용한 룰 테스트를 다룬다."
date: 2026-07-02
tags: [Observability, Prometheus, Rules, Alerting]
prev: /study/observability/10-promql-advanced
next: /study/observability/12-tsdb-remote-write
---

# Recording·Alerting Rule

::: info 학습 목표
- Recording Rule로 비싼 쿼리를 사전 계산하고, `level:metric:operation` 명명 규칙을 적용한다.
- Alerting Rule의 `expr`/`for`/`labels`/`annotations` 구조와 각 필드의 역할을 이해한다.
- 룰 그룹의 평가 주기와 그룹 내 순차 평가 규칙을 파악한다.
- `for`가 만드는 pending → firing 상태 전이를 이해하고 오탐 억제에 활용한다.
- 룰 그룹 분할로 평가 비용을 관리하고, `promtool test rules`로 룰을 검증한다.
:::

## 1. Recording Rule — 사전 계산

Recording Rule은 PromQL 표현식의 결과를 <strong>새로운 시계열로 미리 계산해 저장</strong>하는 룰이다. 대시보드에서 매번 무거운 `rate` + `sum by` + `histogram_quantile` 조합을 즉석에서 돌리는 대신, 정해진 평가 주기마다 서버가 미리 계산해두고 대시보드는 그 결과 시계열만 가볍게 조회한다.

```yaml
groups:
  - name: api-recording-rules
    interval: 30s
    rules:
      - record: job:http_requests:rate5m
        expr: sum(rate(http_requests_total[5m])) by (job)

      - record: job_route:http_request_duration_seconds:p99
        expr: |
          histogram_quantile(
            0.99,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le, job, route)
          )
```

<strong>명명 규칙은 `level:metric:operation`</strong>을 따른다. `level`은 집계가 어떤 라벨 단위로 이뤄졌는지(`job`, `job_route`, `instance` 등 by 절의 라벨을 언더스코어로 나열), `metric`은 원본 메트릭 이름(단위 접미사는 유지), `operation`은 적용한 연산(`rate5m`, `p99`, `avg1h` 등)을 콜론(`:`)으로 구분해 붙인다. 이 규칙을 지키면 룰 이름만 보고도 "무엇을 어떤 단위로 어떻게 집계했는지"가 드러나고, Recording Rule을 다른 Recording Rule의 입력으로 체이닝할 때도 혼란이 줄어든다.

![Recording Rule — 원본 메트릭을 매 30초 평가해 job:http_requests:rate5m 같은 새 시계열로 TSDB에 저장하고, Grafana 대시보드와 Alerting Rule이 가볍게 재사용하는 흐름](/images/study-observability/11-recording-rule-light.png)
![Recording Rule — 원본 메트릭을 매 30초 평가해 job:http_requests:rate5m 같은 새 시계열로 TSDB에 저장하고, Grafana 대시보드와 Alerting Rule이 가볍게 재사용하는 흐름](/images/study-observability/11-recording-rule-dark.png)

Recording Rule의 결과는 다른 Recording Rule이나 Alerting Rule의 입력으로 재사용할 수 있다. 여러 알림이 같은 무거운 집계를 반복해서 계산하고 있다면, 그 집계를 Recording Rule로 한 번만 계산해두고 알림들이 그 결과를 참조하도록 리팩터링하는 게 일반적인 최적화다.

## 2. Alerting Rule — expr/for/labels/annotations

Alerting Rule은 조건식이 참인 시계열이 있으면 알림을 발화한다.

```yaml
groups:
  - name: api-alerts
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status_code=~"5.."}[5m])) by (job)
            / sum(rate(http_requests_total[5m])) by (job)
            > 0.05
        for: 10m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "{{ $labels.job }} 5xx 비율이 5%를 초과했다"
          description: "현재 5xx 비율: {{ $value | humanizePercentage }}"
          runbook_url: "https://runbooks.internal/high-error-rate"
```

- <strong>`expr`</strong>: 참이 되면 발화 조건이 되는 PromQL 표현식. 결과로 나온 각 시계열이 개별 알림 인스턴스가 된다.
- <strong>`for`</strong>: 조건이 이 기간 동안 <strong>연속으로</strong> 참이어야 실제로 발화(firing)한다. 생략하면 조건이 참이 되는 즉시 발화한다.
- <strong>`labels`</strong>: 알림에 붙는 라벨. Alertmanager의 라우팅·그룹핑·억제가 전부 이 라벨을 기준으로 동작하므로 `severity`, `team` 같은 라우팅 키를 여기 넣는다.
- <strong>`annotations`</strong>: 사람이 읽을 설명. `{{ $labels.xxx }}`, `{{ $value }}` 같은 Go 템플릿과 `humanize`/`humanizePercentage`/`humanizeDuration` 같은 템플릿 함수를 쓸 수 있다. 라우팅에는 쓰이지 않는다.

라벨과 annotation을 혼동하지 않는 것이 중요하다. Alertmanager는 <strong>labels</strong>만 보고 그룹핑·라우팅·억제를 결정한다. annotation은 순수하게 사람이 보는 텍스트다. 이 흐름은 [Alertmanager 아키텍처](/study/observability/13-alertmanager-architecture)에서 이어서 다룬다.

## 3. 룰 평가 — rule group, interval, 순차 평가

룰은 반드시 하나 이상의 <strong>그룹(group)</strong>에 속한다. 그룹 단위로 평가 주기(`interval`)를 지정하며, 생략하면 전역 `evaluation_interval`을 따른다.

![룰 그룹 평가 — 그룹 A(interval 30s)의 rule 1→2→3은 순차 평가되어 앞 룰 결과를 뒤 룰이 참조하고, 그룹 B(interval 1m)와는 독립적으로 병렬 평가된다](/images/study-observability/11-rule-groups-light.png)
![룰 그룹 평가 — 그룹 A(interval 30s)의 rule 1→2→3은 순차 평가되어 앞 룰 결과를 뒤 룰이 참조하고, 그룹 B(interval 1m)와는 독립적으로 병렬 평가된다](/images/study-observability/11-rule-groups-dark.png)

핵심은 <strong>같은 그룹 안의 룰은 파일에 나열된 순서대로 순차 평가</strong>된다는 점이다. 앞선 Recording Rule이 만든 시계열을 뒤에 나오는 룰이 즉시 참조할 수 있다는 뜻이다. 반대로 <strong>서로 다른 그룹은 원칙적으로 독립적으로, 병렬로</strong> 평가되므로 순서를 보장하지 않는다. 룰 B가 룰 A의 결과에 의존한다면 반드시 같은 그룹 안에, A를 B보다 앞에 둬야 한다.

`interval`이 짧을수록 알림 반응은 빨라지지만 평가 비용이 늘어난다. 대부분의 경우 전역 기본값(예: 1분)으로 충분하고, 특히 민감한 알림 그룹에만 더 짧은 interval을 별도로 준다.

## 4. for와 pending/firing 상태 전이

`for`가 있는 Alerting Rule은 세 가지 상태를 오간다.

![for 상태 전이 — expr가 참이 되면 Inactive에서 Pending으로, for 기간 내내 연속으로 참이면 Firing으로 전이하며, for 기간 전에 거짓이 되면 Inactive로 되돌아가 오탐을 걸러낸다](/images/study-observability/11-for-state-light.png)
![for 상태 전이 — expr가 참이 되면 Inactive에서 Pending으로, for 기간 내내 연속으로 참이면 Firing으로 전이하며, for 기간 전에 거짓이 되면 Inactive로 되돌아가 오탐을 걸러낸다](/images/study-observability/11-for-state-dark.png)

- <strong>Inactive</strong>: 조건이 거짓. 평상시 상태.
- <strong>Pending</strong>: 조건이 참이 된 직후. `for` 타이머가 돌아가는 중이며, 아직 Alertmanager로 전송되지 않는다.
- <strong>Firing</strong>: `for` 기간 내내 조건이 끊기지 않고 참이었을 때만 도달한다. 이 시점부터 Alertmanager로 알림이 전송된다.

`for`는 일시적인 스파이크로 인한 오탐(flapping)을 걸러내는 장치다. 예를 들어 `for: 10m`인 알림은 조건이 3분만 참이었다가 다시 거짓이 되면 Pending에서 Inactive로 되돌아가고, 실제로 알림이 나가는 일은 없다. 값이 하나라도 튀면 바로 알림을 원하는 치명적인 조건(예: `up == 0` 인프라 다운)에는 `for`를 짧게 두거나 생략하고, 노이즈에 민감한 조건(예: 에러율 임계값)에는 `for`를 길게 잡는 식으로 알림 성격에 맞춰 조정한다.

## 5. 룰 성능·부하

룰 그룹 하나의 평가 비용은 그룹 안의 모든 룰이 <strong>매 interval마다 순차적으로</strong> 실행되는 총 시간이다. 그룹의 평가 시간이 그룹의 `interval`을 넘기면 다음 평가가 밀리기 시작하고, 이는 Prometheus의 `prometheus_rule_group_last_duration_seconds`와 `prometheus_rule_group_iterations_missed_total` 메트릭으로 관측할 수 있다.

주요 튜닝 포인트는 다음과 같다.

- <strong>그룹 분할.</strong> 룰이 많고 무거운 그룹은 여러 그룹으로 쪼갠다. 서로 다른 그룹은 병렬로 평가되므로, 순서 의존성이 없는 룰들은 별도 그룹으로 분리해 전체 평가 시간을 줄인다.
- <strong>고카디널리티 expr 피하기.</strong> [PromQL 심화](/study/observability/10-promql-advanced)에서 다룬 안티패턴이 룰에서는 매 interval마다 반복 실행되므로 영향이 더 크다.
- <strong>Recording Rule 체이닝.</strong> 여러 알림이 참조하는 무거운 집계는 별도 Recording Rule로 한 번만 계산해서 재사용한다.
- <strong>`interval`을 필요 이상으로 짧게 잡지 않는다.</strong> 반응 속도가 정말 중요한 그룹에만 짧은 interval을 준다.

![룰 성능 — 평가 시간이 interval을 넘으면(last_duration_seconds) 평가 지연이 발생하고 iterations_missed_total이 증가하며, 그룹 분할·Recording Rule 사전 계산·고카디널리티 expr 제거로 튜닝한다](/images/study-observability/11-rule-performance-light.png)
![룰 성능 — 평가 시간이 interval을 넘으면(last_duration_seconds) 평가 지연이 발생하고 iterations_missed_total이 증가하며, 그룹 분할·Recording Rule 사전 계산·고카디널리티 expr 제거로 튜닝한다](/images/study-observability/11-rule-performance-dark.png)

## 6. 룰 테스트 — promtool test rules

룰 파일은 배포 전에 `promtool`로 단위 테스트할 수 있다. 테스트 YAML에 가상의 시계열 입력과 특정 평가 시점에서 기대하는 알림 상태를 기술한다.

```yaml
# rules_test.yml
rule_files:
  - api_alerts.yml

evaluation_interval: 1m

tests:
  - interval: 1m
    input_series:
      - series: 'http_requests_total{job="api", status_code="500"}'
        values: "0+10x20"
      - series: 'http_requests_total{job="api", status_code="200"}'
        values: "0+90x20"

    alert_rule_test:
      - eval_time: 15m
        alertname: HighErrorRate
        exp_alerts:
          - exp_labels:
              severity: warning
              team: backend
              job: api
            exp_annotations:
              summary: "api 5xx 비율이 5%를 초과했다"
```

```bash
promtool test rules rules_test.yml
```

`input_series`의 `values`는 `0+10x20` 같은 축약 표기로, "시작값 0에서 매 스텝(interval)마다 10씩 증가하며 총 20 스텝"을 뜻한다. `alert_rule_test`는 특정 `eval_time`(룰 파일 로드 시점 기준 경과 시간)에 해당 알림이 정확히 어떤 라벨·annotation으로 발화해야 하는지 검증한다. `for` 기간을 감안해 `eval_time`을 충분히 뒤로 잡지 않으면 아직 Pending 상태라 테스트가 실패한다는 점도 놓치기 쉬운 포인트다. CI 파이프라인에 `promtool test rules`를 넣어두면 룰 변경이 배포되기 전에 발화 조건 실수를 잡아낼 수 있다.

::: tip 핵심 정리
- Recording Rule은 비싼 쿼리를 사전 계산해 저장하며, `level:metric:operation` 명명 규칙으로 무엇을 어떻게 집계했는지 이름만으로 드러낸다.
- Alerting Rule은 `expr`(조건)·`for`(지속 시간)·`labels`(라우팅용)·`annotations`(설명용)로 구성되며, 라우팅은 오직 labels만 본다.
- 같은 룰 그룹 안의 룰은 순차 평가되어 앞 룰의 결과를 뒤 룰이 참조할 수 있지만, 서로 다른 그룹은 독립적으로 병렬 평가된다.
- `for`는 Inactive → Pending → Firing 상태 전이를 만들어 일시적 스파이크로 인한 오탐을 걸러낸다.
- 그룹 평가 시간이 interval을 넘기면 평가가 밀린다 — 그룹 분할과 Recording Rule 체이닝으로 비용을 관리한다.
- `promtool test rules`로 발화 조건과 라벨·annotation을 배포 전에 검증한다.
:::

## 다음 챕터

발화한 알림은 그대로 방치하면 중복·노이즈로 무의미해진다. 알림이 실제로 어떻게 그룹핑되고 라우팅되어 사람에게 도달하는지는 [Alertmanager 아키텍처](/study/observability/13-alertmanager-architecture)에서 다룬다. 다음 챕터에서는 먼저 Prometheus 내부로 돌아가, 룰이 참조하는 시계열이 실제로 어떻게 저장되는지 — TSDB의 구조와 `remote_write`를 통한 장기 저장 연동을 살펴본다.
