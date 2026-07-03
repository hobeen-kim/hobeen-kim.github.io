---
title: "LogQL"
description: "Loki 쿼리 언어 LogQL의 스트림 셀렉터, 라인 필터, 파서(logfmt/json/pattern/regexp), 라벨 필터·포맷, 메트릭 쿼리와 성능 최적화 원칙을 다룬다."
date: 2026-07-02
tags: [Loki, LogQL]
prev: /study/observability/17-loki-read-write-path
next: /study/observability/19-log-pipeline-storage
---

# LogQL

::: info 학습 목표
- log stream selector로 대상 스트림을 좁히고 라인 필터(`|=`, `!=`, `|~`, `!~`)로 텍스트를 거르는 방법을 익힌다.
- logfmt, json, pattern, regexp 네 파서의 사용 시점과 차이를 구분한다.
- 파서 이후 label filter·line_format·label_format으로 구조화된 필드를 다루는 방법을 안다.
- rate, count_over_time, unwrap 기반 메트릭 쿼리로 로그에서 시계열을 뽑아내는 방법을 이해한다.
- 라벨 우선 필터링과 파서 비용을 고려한 LogQL 성능 튜닝 원칙을 적용할 수 있다.
:::

## 1. Log Stream Selector — 라벨 매처

모든 LogQL 쿼리는 <strong>스트림 셀렉터</strong>로 시작한다. 중괄호 안에 라벨 매처를 나열해 대상 스트림 집합을 지정한다.

```logql
{app="checkout", env="prod"}
{app="checkout", env=~"prod|staging"}
{app="checkout", env!="dev"}
{app=~"checkout.*"}
```

지원 연산자는 Prometheus 라벨 매처와 동일하다.

| 연산자 | 의미 |
|---|---|
| `=` | 정확히 일치 |
| `!=` | 불일치 |
| `=~` | 정규식 일치 |
| `!~` | 정규식 불일치 |

스트림 셀렉터는 인덱스만으로 해석되므로 비용이 거의 없다. 반대로 셀렉터가 스트림을 충분히 좁히지 못하면(예: 라벨 하나만 지정하고 값이 넓게 매칭됨) 뒤 단계에서 스캔해야 할 청크가 폭증한다. LogQL 성능의 첫 단추는 항상 스트림 셀렉터다.

## 2. 라인 필터 — `|=`, `!=`, `|~`, `!~`

스트림 셀렉터 뒤에 라인 필터를 체이닝해 로그 라인 텍스트 자체를 거른다.

```logql
{app="checkout"} |= "timeout"
{app="checkout"} != "healthcheck"
{app="checkout"} |~ "error|panic|fatal"
{app="checkout"} !~ "DEBUG.*"
```

| 연산자 | 의미 |
|---|---|
| `\|=` | 문자열 포함 |
| `!=` | 문자열 미포함 |
| `\|~` | 정규식 매치 |
| `!~` | 정규식 미매치 |

라인 필터는 여러 개를 체이닝할 수 있고(`{app="checkout"} |= "error" != "timeout" |~ "5\\d\\d"`), 왼쪽부터 순서대로 적용된다. `|=`/`!=`는 정규식 엔진을 거치지 않는 단순 바이트 비교라 `|~`/`!~`보다 훨씬 빠르다 — 가능하면 문자열 포함 필터를 먼저 배치해 후보 라인 수를 줄인 뒤 정규식 필터를 적용하는 순서가 유리하다.

## 3. 파서 — logfmt, json, pattern, regexp

라인 필터로 좁힌 뒤에는 파서로 로그 라인을 구조화된 필드(라벨처럼 다룰 수 있는 추출 값)로 분해한다.

![LogQL 파이프라인 흐름 — 스트림 셀렉터로 대상을 좁히고 라인 필터로 텍스트를 거른 뒤 파서(json 등)로 status·path·duration 같은 구조화된 필드를 추출](/images/study-observability/18-parser-pipeline-light.png)
![LogQL 파이프라인 흐름 — 스트림 셀렉터로 대상을 좁히고 라인 필터로 텍스트를 거른 뒤 파서(json 등)로 status·path·duration 같은 구조화된 필드를 추출](/images/study-observability/18-parser-pipeline-dark.png)

- <strong>logfmt</strong>: `key=value key2="value 2"` 형식 로그를 파싱한다. `| logfmt`만 쓰면 전체 필드를 추출하고, `| logfmt status, path`처럼 필드를 지정할 수도 있다.
- <strong>json</strong>: JSON 로그 라인을 파싱한다. 중첩 필드는 `| json request_method="request.method"`처럼 JMESPath 유사 표기로 평탄화해 뽑는다.
- <strong>pattern</strong>: 사람이 읽기 쉬운 캡처 문법(`<필드명>`)으로 정형화되지 않은 텍스트를 파싱한다. 정규식보다 가독성이 좋다.
- <strong>regexp</strong>: 명명 캡처 그룹(`(?P<name>...)`)을 쓰는 정규식 파서. 가장 유연하지만 표현식 작성·유지보수 비용이 가장 크다.

```logql
{app="checkout"} | logfmt
{app="checkout"} | json
{app="nginx"}    | pattern "<ip> - - [<_>] \"<method> <path> <_>\" <status> <size>"
{app="nginx"}    | regexp "(?P<method>\\w+) (?P<path>\\S+) HTTP.*(?P<status>\\d{3})"
```

파서가 실패하면(예: JSON이 아닌 라인에 `| json` 적용) 해당 라인에 `__error__` 라벨이 붙는다. `| json | __error__=""`처럼 필터링해 파싱 실패 라인을 제외하거나, 반대로 `__error__!=""`로 파싱 실패 라인만 골라 원인을 조사할 수 있다.

## 4. Label Filter · line_format · label_format

파서로 필드를 추출한 다음에는 세 가지 후처리 연산을 쓴다.

<strong>label filter</strong>는 추출된 필드 값으로 라인을 다시 거른다. 문자열뿐 아니라 숫자·기간 비교도 지원한다.

```logql
{app="checkout"} | json | status_code >= 500
{app="checkout"} | json | duration > 5s
{app="checkout"} | logfmt | level="error" | status_code >= 500
```

<strong>line_format</strong>은 Go 템플릿 문법으로 출력 라인 자체를 재구성한다. 대시보드에 필요한 필드만 뽑아 읽기 쉬운 형태로 바꿀 때 쓴다.

```logql
{app="checkout"} | json | line_format "{{.status_code}} {{.method}} {{.path}} ({{.duration}})"
```

<strong>label_format</strong>은 추출된 필드나 기존 라벨의 이름을 바꾸거나 템플릿으로 값을 재계산해 결과 라벨로 승격한다. 뒤에 나올 메트릭 쿼리에서 `by (...)` 집계 기준으로 쓰려면 원하는 필드를 라벨 형태로 만들어둬야 한다.

```logql
{app="checkout"} | json | label_format http_status=status_code
```

::: warning label_format으로 만든 라벨도 카디널리티에 영향을 준다
label_format이 만드는 라벨은 인덱스에는 들어가지 않지만, 메트릭 쿼리의 `by ()` 집계 기준으로 쓰이면 결과 시계열 수를 그만큼 늘린다. `request_id`처럼 고카디널리티 필드를 그대로 `by ()`에 넣으면 집계 결과 자체가 폭발한다.
:::

## 5. 메트릭 쿼리 — rate, count_over_time, unwrap, 집계

LogQL은 로그 스트림에서 바로 시계열을 뽑아내는 <strong>메트릭 쿼리</strong>를 지원한다. 로그 라인의 존재 빈도를 세는 방식과, 라인에서 숫자 값을 추출해 집계하는 방식 두 가지가 있다.

라인 개수 기반 함수는 range vector(`[5m]` 같은 구간)를 받는다.

```logql
count_over_time({app="checkout"} |= "error" [5m])
rate({app="checkout"} |= "error" [5m])
bytes_over_time({app="checkout"} [5m])
```

`count_over_time`은 구간 내 매칭된 라인 수, `rate`는 초당 라인 발생률(구간 내 라인 수를 초로 나눈 값)이다. Prometheus의 `rate()`와 이름은 같지만 카운터 증가율이 아니라 로그 라인 발생률이라는 점이 다르다.

숫자 값 자체를 집계하려면 <strong>unwrap</strong>으로 필드를 숫자 값으로 변환한 뒤 range vector 함수를 적용한다.

```logql
sum by (path) (
  sum_over_time({app="checkout"} | json | unwrap duration_ms [5m])
)

quantile_over_time(0.99,
  {app="checkout"} | json | unwrap duration_ms [5m]
) by (path)
```

`unwrap`은 라인 수가 아니라 추출된 필드 값(예: 응답 시간 `duration_ms`)을 시계열 샘플로 취급한다. 이후 `sum_over_time`, `avg_over_time`, `max_over_time`, `min_over_time`, `quantile_over_time`, `rate` 등을 적용해 실제 수치 기반 집계를 계산한다.

바깥쪽에는 Prometheus와 동일한 집계 연산자(`sum`, `avg`, `max`, `min`, `count`, `topk`, `bottomk`)를 `by (...)`/`without (...)`와 함께 쓸 수 있다.

```logql
topk(5,
  sum by (path) (rate({app="checkout"} | json | status_code >= 500 [5m]))
)
```

## 6. 성능 — 라벨로 먼저 좁히기, 파서 비용

LogQL 성능은 파이프라인 앞단에서 데이터를 얼마나 줄이느냐에 좌우된다. 각 단계의 비용이 크게 다르기 때문이다.

![LogQL 성능 단계별 비용 — 스트림 셀렉터(매우 저렴) → 라인 필터 |= !=(저렴) → 라인 필터 |~ !~(중간) → 파서(비쌈) → 라벨 필터·집계 순으로 갈수록 비용이 커지므로 저렴한 단계로 먼저 후보를 줄인다](/images/study-observability/18-performance-stages-light.png)
![LogQL 성능 단계별 비용 — 스트림 셀렉터(매우 저렴) → 라인 필터 |= !=(저렴) → 라인 필터 |~ !~(중간) → 파서(비쌈) → 라벨 필터·집계 순으로 갈수록 비용이 커지므로 저렴한 단계로 먼저 후보를 줄인다](/images/study-observability/18-performance-stages-dark.png)

원칙은 단순하다.

- <strong>스트림 셀렉터를 최대한 좁힌다.</strong> 라벨로 스트림 수를 줄이지 못하면 뒤 단계가 다뤄야 할 청크 자체가 많아 어떤 최적화도 소용없다.
- <strong>파서보다 라인 필터를 먼저 적용한다.</strong> `{app="checkout"} | json | message |= "timeout"`보다 `{app="checkout"} |= "timeout" | json`이 훨씬 빠르다 — 전자는 모든 라인을 JSON 파싱한 뒤 거르지만, 후자는 문자열 필터로 후보를 줄인 뒤에만 파싱한다.
- <strong>필요한 필드만 파싱한다.</strong> `| logfmt`로 전체 필드를 뽑기보다 `| logfmt status, path`처럼 필요한 필드만 지정하면 파싱 비용이 줄어든다.
- <strong>정규식은 최후 수단으로.</strong> `pattern`이나 `logfmt`/`json`으로 표현 가능하면 `regexp`보다 그쪽이 낫다. 정규식은 백트래킹 패턴에 따라 비용이 예측하기 어렵게 커질 수 있다.

## 다음 챕터

LogQL로 쿼리하는 법을 익혔다면, 이제 그 로그가 애초에 어떻게 수집·라벨링돼 Loki까지 도달하는지 볼 차례다. 다음 챕터 [로그 파이프라인과 스토리지](/study/observability/19-log-pipeline-storage)에서는 Alloy/Promtail 수집 에이전트, 파이프라인 스테이지, 구조화 메타데이터, 라벨 설계, 오브젝트 스토리지 운영을 다룬다.
