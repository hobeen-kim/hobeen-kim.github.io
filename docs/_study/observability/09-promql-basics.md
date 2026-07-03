---
title: "PromQL 기초"
description: "PromQL의 두 가지 벡터 타입, 셀렉터와 매처, counter를 다루는 rate/irate/increase의 함정, 집계 연산자와 by/without, 연산자 우선순위, histogram_quantile 같은 필수 함수를 실전 예제로 정리한다."
date: 2026-07-02
tags: [Observability, Prometheus, PromQL]
prev: /study/observability/08-exporters-instrumentation
next: /study/observability/10-promql-advanced
---

# PromQL 기초

::: info 학습 목표
- instant vector와 range vector의 차이를 이해하고 언제 range selector `[5m]`가 필요한지 판단한다.
- 라벨 매처(`=`, `!=`, `=~`, `!~`)로 원하는 시계열만 정확히 골라낸다.
- counter 타입에 `rate`/`irate`/`increase`를 써야 하는 이유와 rate의 흔한 함정을 파악한다.
- `sum`/`avg`/`max` 같은 집계 연산자를 `by`/`without`으로 원하는 카디널리티로 줄인다.
- 산술·비교·논리 연산자와 `histogram_quantile` 등 실무에서 자주 쓰는 함수를 익힌다.
:::

## 1. Instant Vector와 Range Vector

PromQL이 다루는 데이터 타입은 크게 네 가지(scalar, string, instant vector, range vector)지만, 실무에서 매일 쓰는 건 사실상 두 가지다.

<strong>Instant vector</strong>는 특정 시점(기본은 쿼리 실행 시각) 기준으로, 라벨 집합이 같은 시계열마다 값 하나씩을 가진 벡터다. `http_requests_total`처럼 메트릭 이름만 쓰면 instant vector가 나온다.

<strong>Range vector</strong>는 각 시계열에 대해 특정 구간의 샘플 목록을 통째로 담는다. 메트릭 이름 뒤에 `[5m]` 같은 range selector를 붙이면 만들어지며, `rate()`·`increase()`처럼 구간 전체를 입력으로 받는 함수의 재료로만 쓰인다. range vector 자체는 그래프로 그릴 수 없고, 반드시 range-to-instant 함수를 거쳐야 instant vector로 돌아온다.

```promql
# instant vector — 현재 시점의 값 하나
http_requests_total{job="api"}

# range vector — 최근 5분간의 샘플들 (그 자체로는 그래프 불가)
http_requests_total{job="api"}[5m]

# range vector를 rate()에 넣어야 instant vector가 된다
rate(http_requests_total{job="api"}[5m])
```

![메트릭 이름은 바로 Instant Vector가 되고, Range Selector [5m]를 붙이면 Range Vector가 되며 rate·increase 같은 함수를 거쳐야 다시 Instant Vector로 변환된다](/images/study-observability/09-vector-types-light.png)
![메트릭 이름은 바로 Instant Vector가 되고, Range Selector [5m]를 붙이면 Range Vector가 되며 rate·increase 같은 함수를 거쳐야 다시 Instant Vector로 변환된다](/images/study-observability/09-vector-types-dark.png)

range selector의 길이는 스크레이프 간격의 최소 2~4배로 잡는 게 안전하다. 스크레이프 주기가 15초인데 `[15s]`로 잡으면 스크레이프가 한 번이라도 밀리는 순간 구간 안에 샘플이 0~1개만 남아 `rate()`가 결측(gap)을 뱉는다.

## 2. 셀렉터와 매처

메트릭 이름 뒤 중괄호 안에 라벨 매처를 넣어 시계열을 좁힌다. 매처는 네 종류다.

| 연산자 | 의미 | 예시 |
|---|---|---|
| `=` | 라벨 값이 정확히 일치 | `{job="api"}` |
| `!=` | 라벨 값이 불일치 | `{job!="api"}` |
| `=~` | 정규식 매치(RE2, 전체 문자열 anchor) | `{status_code=~"5.."}` |
| `!~` | 정규식 불일치 | `{status_code!~"2..\|3.."}` |

```promql
# job이 api 또는 web인 시계열
http_requests_total{job=~"api|web"}

# 5xx 응답만
http_requests_total{status_code=~"5.."}

# 메트릭 이름 자체도 정규식으로 매칭 가능
{__name__=~"http_requests_.*"}
```

::: warning 정규식은 전체 문자열에 anchor된다
`=~"api"`는 `job="api-gateway"`에도 매치된다. `.*`가 암묵적으로 앞뒤에 붙지 않고 <strong>부분 문자열이 아니라 전체 매치</strong>를 시도하지만, `api`라는 패턴 자체가 `api-gateway` 전체와 매치되는 게 아니라 정규식 엔진이 문자열 전체를 이 패턴으로 설명할 수 있는지 본다. `job="api"`처럼 완전히 같은 값이 아니면 `=~"^api$"`처럼 명시적으로 anchor를 걸어야 원하는 결과를 얻는다.
:::

빈 값 매처(`{label=""}`)는 그 라벨이 없는 시계열도 포함한다는 점도 기억해 둘 만하다. 반대로 `{label!=""}`는 해당 라벨이 존재하고 비어있지 않은 시계열만 남긴다.

## 3. Counter 다루기 — rate, irate, increase

Prometheus의 counter는 단조 증가만 하는 누적값이다. 프로세스 재시작이나 pod 재배포로 값이 0으로 리셋될 수 있으므로, counter의 raw 값 자체는 거의 의미가 없고 항상 변화율로 바꿔서 본다.

<strong>`rate(v[t])`</strong>는 구간 `[t]` 동안의 초당 평균 증가율을 계산한다. 내부적으로 구간의 첫 샘플과 마지막 샘플 차이를 시간으로 나누되, counter reset을 감지하면 리셋 전후 값을 보정해서 합산한다. 대시보드·알림에는 거의 항상 `rate`를 쓴다.

```promql
# 초당 요청 수 (5분 평균)
rate(http_requests_total[5m])

# 5분간 총 증가량 (rate * 구간초)
increase(http_requests_total[5m])
```

<strong>`irate(v[t])`</strong>는 구간 내 마지막 두 샘플만으로 순간 변화율을 계산한다. 급격한 스파이크를 더 민감하게 보여주지만, 노이즈가 심해 대시보드에서 지그재그가 심하다. 알림 조건에는 부적합하고, 짧은 구간의 순간 변화를 눈으로 확인할 때만 제한적으로 쓴다.

<strong>`increase(v[t])`</strong>는 `rate(v[t]) * t`와 사실상 동일하다. "5분간 몇 건 늘었나"처럼 절대량이 궁금할 때 쓴다.

![Counter 원시값을 rate(구간 평균 초당 증가율·리셋 보정)·irate(마지막 2개 샘플 순간 변화율)·increase(구간 총 증가량)로 변환해 각각 대시보드·순간 스파이크 관찰·절대 증가량 확인에 쓰는 흐름](/images/study-observability/09-counter-functions-light.png)
![Counter 원시값을 rate(구간 평균 초당 증가율·리셋 보정)·irate(마지막 2개 샘플 순간 변화율)·increase(구간 총 증가량)로 변환해 각각 대시보드·순간 스파이크 관찰·절대 증가량 확인에 쓰는 흐름](/images/study-observability/09-counter-functions-dark.png)

::: warning rate의 흔한 함정
- **range가 너무 짧으면 결측이 생긴다.** 스크레이프 간격 15초에 `rate(v[15s])`를 쓰면 구간에 샘플이 1개뿐일 때가 있어 `rate`가 값을 못 낸다. 최소 스크레이프 간격의 4배(`[1m]` 이상) 권장.
- **`rate` 전에 집계하지 않는다.** `rate(sum(x)[5m])`처럼 먼저 합산한 뒤 rate를 걸면 개별 시계열의 counter reset이 뭉개져 잘못된 값이 나온다. 항상 `sum(rate(x[5m]))`처럼 rate를 먼저, 집계를 나중에 한다.
- **`rate`는 extrapolation(외삽)을 한다.** 구간 경계와 실제 샘플 시각이 정확히 안 맞으면 Prometheus가 값을 추정해서 채운다. 짧은 구간일수록 추정 오차 비율이 커진다.
- **gauge에는 `rate`를 쓰지 않는다.** gauge는 증가·감소가 자유로운 값이라 `rate`의 counter reset 보정 로직이 의미를 갖지 못한다. gauge의 변화율이 필요하면 `deriv()`나 `delta()`를 쓴다.
:::

## 4. 집계 연산자 — sum, avg, max와 by/without

집계 연산자는 여러 시계열을 라벨 기준으로 묶어 값을 하나로 합친다. 자주 쓰는 것만 추리면 `sum`, `avg`, `min`, `max`, `count`, `topk`, `bottomk`, `stddev`, `quantile` 정도다.

```promql
# job별 요청 처리율 합계
sum(rate(http_requests_total[5m])) by (job)

# instance 라벨만 빼고 나머지 라벨은 유지
sum(rate(http_requests_total[5m])) without (instance)

# job, status_code 조합별 상위 5개
topk(5, sum(rate(http_requests_total[5m])) by (job, status_code))
```

`by (labels...)`는 지정한 라벨만 남기고 나머지는 버린 뒤 그룹핑한다. `without (labels...)`는 반대로 지정한 라벨만 버리고 나머지는 전부 유지한다. 결과에 남는 라벨 집합이 다르므로 둘은 대칭이 아니다. `instance`처럼 카디널리티가 높고 관심 없는 라벨을 뺄 때는 `without`이, `job`처럼 소수의 관심 라벨만 남기고 싶을 때는 `by`가 편하다.

::: warning 집계 후 라벨이 사라지면 join이 끊긴다
`sum by (job)`를 거친 결과는 `job` 라벨만 남는다. 이후 다른 메트릭과 라벨 매칭 연산(10장에서 다룰 `on`/`ignoring`)을 하려면 필요한 라벨을 미리 `by`에 포함해 둬야 한다. 집계에서 라벨을 지워버리면 되돌릴 방법이 없다.
:::

## 5. 산술·비교·논리 연산자

PromQL은 벡터끼리, 벡터와 스칼라 사이의 산술·비교·논리 연산을 지원한다.

```promql
# 산술: 메모리 사용률(%)
100 * container_memory_working_set_bytes / container_spec_memory_limit_bytes

# 비교: 임계값을 넘는 시계열만 필터 (필터 목적으로는 bool 없이)
node_load1 > 4

# 비교 + bool: 조건 결과를 1/0으로 (알림식 안에서 산술에 쓸 때)
(node_load1 > bool 4)

# 논리: and, or, unless (벡터 간 집합 연산)
up{job="api"} == 0
  and on(instance) node_load1 > 4
```

비교 연산자(`==`, `!=`, `>`, `<`, `>=`, `<=`)를 벡터에 그냥 쓰면 조건을 만족하는 시계열만 필터링해서 반환하고, 값 자체는 원래 값을 유지한다. `bool` modifier를 붙이면 필터링 대신 조건 결과를 `1`(참)/`0`(거짓)으로 바꿔서 모든 시계열을 그대로 반환한다. 알림 룰에서는 필터링 동작을 그대로 쓰고, 스코어링처럼 산술에 결과를 활용할 때만 `bool`을 붙인다.

논리 연산자 `and`/`or`/`unless`는 라벨 집합이 일치하는 시계열끼리 집합 연산을 한다. `and`는 양쪽 다 존재하는 시계열만, `unless`는 왼쪽에서 오른쪽에 없는 시계열만 남긴다. 연산자 우선순위는 `^` > `*, /, %, atan2` > `+, -` > 비교 연산자 > `and, unless` > `or` 순이며, 헷갈리면 괄호로 명시하는 편이 안전하다.

## 6. 자주 쓰는 함수

<strong>`histogram_quantile(φ, b)`</strong>는 히스토그램의 `_bucket` 시계열로부터 분위수를 추정한다. 자세한 버킷 집계 순서와 함정은 [PromQL 심화](/study/observability/10-promql-advanced)에서 다루지만, 기본형은 다음과 같다.

```promql
# p99 레이턴시 (le 라벨 기준 버킷 사용)
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
```

<strong>`absent(v)`</strong>는 벡터 `v`에 시계열이 하나도 없으면 값 `1`짜리 벡터를, 하나라도 있으면 빈 벡터를 반환한다. "타깃이 사라졌다"류의 알림에 필수다.

```promql
# job=api의 up 시계열이 아예 없으면(스크레이프 자체가 안 됨) 알림
absent(up{job="api"})
```

<strong>`clamp(v, min, max)`</strong>는 값을 `[min, max]` 범위로 자른다(구버전의 `clamp_min`/`clamp_max`를 통합). 이상치를 시각화에서 눌러줄 때 쓴다.

```promql
clamp(node_load1, 0, 10)
```

<strong>`label_replace(v, dst, replacement, src, regex)`</strong>는 라벨 값에 정규식을 적용해 새 라벨을 만들거나 기존 라벨을 바꾼다. 서로 다른 메트릭의 라벨 스키마를 맞춰 join하기 전 전처리로 자주 쓴다.

```promql
# instance="10.0.1.5:9100" 에서 IP만 뽑아 host 라벨로 추가
label_replace(node_load1, "host", "$1", "instance", "([^:]+):.*")
```

이 밖에 `abs`, `round`, `sort_desc`, `changes`, `resets`, `delta`, `deriv`, `predict_linear`도 운영 대시보드·알림에서 자주 등장하므로 [PromQL 함수 레퍼런스](https://prometheus.io/docs/prometheus/latest/querying/functions/)를 한 번 훑어두면 좋다.

::: tip 핵심 정리
- instant vector는 시점 값, range vector는 구간 샘플 모음이며 range vector는 반드시 함수를 거쳐야 그래프로 그릴 수 있다.
- 라벨 매처는 `=`/`!=`/`=~`/`!~` 네 가지이고, 정규식은 전체 문자열 매치이므로 부분 매치가 필요하면 명시적으로 설계한다.
- counter는 항상 `rate`로 변화율을 본다. `rate` 전에 집계하면 counter reset 보정이 깨지므로 순서를 지킨다.
- `by`는 지정 라벨만 남기고, `without`은 지정 라벨만 버린다 — 결과 라벨 집합이 다르므로 이후 join 가능 여부에 영향을 준다.
- 비교 연산자는 기본적으로 필터링이고, `bool` modifier를 붙여야 1/0 값으로 바뀐다.
- `histogram_quantile`, `absent`, `clamp`, `label_replace`는 실무 대시보드·알림에서 매일 쓰는 함수다.
:::

## 다음 챕터

기초 셀렉터와 함수를 익혔다면, 다음은 서로 다른 메트릭을 엮는 벡터 매칭과 히스토그램 쿼리의 세부 함정이다. [PromQL 심화](/study/observability/10-promql-advanced)에서는 `on`/`ignoring`과 `group_left`/`group_right`를 이용한 join 패턴, 서브쿼리, native histogram 쿼리, `offset`과 `@` modifier, 그리고 고카디널리티 쿼리 같은 성능 안티패턴을 다룬다.
