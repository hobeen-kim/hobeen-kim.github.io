---
title: "Exporter와 애플리케이션 계측"
description: "node-exporter 같은 Exporter 패턴과 브릿지 개념, Go/Java/Python 클라이언트 라이브러리로 Counter·Gauge·Histogram을 직접 계측하는 방법, 그리고 RED·USE 방법론으로 무엇을 계측할지 결정하는 기준을 다룬다."
date: 2026-07-02
tags: [Prometheus, Instrumentation, RED, USE]
prev: /study/observability/07-scraping-service-discovery
next: /study/observability/09-promql-basics
---

# Exporter와 애플리케이션 계측

::: info 학습 목표
- Exporter가 왜 필요한지, bridge 패턴과 대표 Exporter(node-exporter, blackbox_exporter, mysqld_exporter)의 역할을 이해한다.
- Go/Java/Python 클라이언트 라이브러리로 Counter·Gauge·Histogram을 직접 코드에 계측하는 방법을 익힌다.
- 라벨 최소화, base unit, `_total` 접미사 등 계측 베스트 프랙티스를 실전 기준으로 적용한다.
- RED(Rate/Errors/Duration)와 USE(Utilization/Saturation/Errors) 방법론의 차이와 적용 대상을 구분한다.
- 서비스와 인프라 각각에 무엇을 계측할지 실전 기준으로 결정한다.
:::

## 1. Exporter 패턴

Prometheus는 pull 기반이라 타깃이 `/metrics`를 노출해야 한다. 그런데 세상의 모든 시스템이 Prometheus 포맷으로 메트릭을 직접 뱉어주진 않는다. 리눅스 커널, MySQL, 레거시 애플리케이션, 서드파티 하드웨어가 대표적이다. <strong>Exporter</strong>는 이런 대상과 Prometheus 사이의 <strong>브릿지(bridge)</strong>다 — 대상 시스템의 상태를 대신 읽어(파일, API, 프로토콜 등) Prometheus 노출 형식으로 번역해주는 별도 프로세스다.

![계측 불가능한 대상(OS·MySQL·HTTP 엔드포인트)을 node-exporter·mysqld_exporter·blackbox_exporter가 대신 읽어 /metrics로 번역하고 Prometheus가 스크레이프하는 브릿지 구조](/images/study-observability/08-exporter-pattern-light.png)
![계측 불가능한 대상(OS·MySQL·HTTP 엔드포인트)을 node-exporter·mysqld_exporter·blackbox_exporter가 대신 읽어 /metrics로 번역하고 Prometheus가 스크레이프하는 브릿지 구조](/images/study-observability/08-exporter-pattern-dark.png)

- <strong>node-exporter</strong>는 리눅스/유닉스 호스트의 하드웨어·OS 지표(`/proc`, `/sys` 파싱)를 노출한다. CPU, 메모리, 디스크, 네트워크, 파일시스템 사용량이 대표 메트릭이다. 거의 모든 Prometheus 배포에 DaemonSet 형태로 함께 깔린다.
- <strong>blackbox_exporter</strong>는 조금 다른 패턴이다. 자체 메트릭을 노출하는 게 아니라, `/probe?target=https://example.com`처럼 <strong>요청 시점에 지정된 대상</strong>을 HTTP/TCP/ICMP/DNS로 프로빙해서 그 결과(성공 여부, 응답 시간, TLS 만료일 등)를 메트릭으로 변환한다. 외부에서 보이는 가용성(블랙박스 관점)을 측정할 때 쓴다.
- <strong>mysqld_exporter</strong>는 MySQL에 접속해 `SHOW GLOBAL STATUS`, `SHOW GLOBAL VARIABLES`, `performance_schema` 등을 질의하고 그 결과를 메트릭으로 변환한다. DB 자체를 고칠 수 없어도 상태를 관측할 수 있게 해주는 전형적인 패턴이다. [10장 — DB 모니터링](/study/db-optimization/10-monitoring)에서 DB 관측성을 별도로 더 깊게 다룬다.

Exporter를 쓸지, 직접 계측할지는 명확한 기준이 있다. <strong>내가 소스 코드를 통제할 수 있는 애플리케이션이면 직접 계측(화이트박스)</strong>이 항상 우선이다. Exporter는 소스를 건드릴 수 없는 시스템, 혹은 애플리케이션 <strong>외부에서</strong> 관측해야 하는 것(blackbox_exporter의 가용성 체크처럼)에 쓴다.

## 2. 클라이언트 라이브러리 계측

애플리케이션 코드 안에서 직접 메트릭을 만드는 것이 <strong>화이트박스 계측</strong>이다. Prometheus는 Go, Java(simpleclient/Micrometer), Python 등 주요 언어의 공식 클라이언트 라이브러리를 제공한다. 세 언어로 HTTP 요청 수(Counter)와 지연시간(Histogram)을 계측하는 최소 예제다.

::: tabs
@tab Go
```go
var (
    httpRequestsTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total number of HTTP requests",
        },
        []string{"method", "status"},
    )
    httpRequestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "http_request_duration_seconds",
            Help:    "HTTP request latency",
            Buckets: prometheus.DefBuckets,
        },
        []string{"method"},
    )
)

func init() {
    prometheus.MustRegister(httpRequestsTotal, httpRequestDuration)
}

func handler(w http.ResponseWriter, r *http.Request) {
    timer := prometheus.NewTimer(httpRequestDuration.WithLabelValues(r.Method))
    defer timer.ObserveDuration()

    status := process(w, r)
    httpRequestsTotal.WithLabelValues(r.Method, status).Inc()
}
```
@tab Java
```java
static final Counter httpRequestsTotal = Counter.build()
    .name("http_requests_total")
    .help("Total number of HTTP requests")
    .labelNames("method", "status")
    .register();

static final Histogram httpRequestDuration = Histogram.build()
    .name("http_request_duration_seconds")
    .help("HTTP request latency")
    .labelNames("method")
    .register();

public void handle(HttpServletRequest req, HttpServletResponse res) {
    Histogram.Timer timer = httpRequestDuration
        .labels(req.getMethod())
        .startTimer();
    try {
        String status = process(req, res);
        httpRequestsTotal.labels(req.getMethod(), status).inc();
    } finally {
        timer.observeDuration();
    }
}
```
@tab Python
```python
from prometheus_client import Counter, Histogram

http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "status"],
)
http_request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method"],
)

@http_request_duration.labels(method="GET").time()
def handler(request):
    status = process(request)
    http_requests_total.labels(method="GET", status=status).inc()
    return status
```
:::

세 언어 모두 패턴이 동일하다. <strong>부팅 시점에 메트릭을 등록</strong>하고(라벨 이름까지 함께 선언), <strong>요청 처리 경로에서 값만 갱신</strong>한다. `Gauge`는 `.Set()`/`.set()`으로 순간값을 직접 지정하거나 `.Inc()`/`.Dec()`로 증감시킨다.

## 3. 계측 베스트 프랙티스

계측을 코드에 심는 순간부터 그 메트릭 이름과 라벨은 사실상 API 계약이 된다. 나중에 바꾸면 대시보드와 알림이 함께 깨진다. 실전에서 반복적으로 문제가 되는 지점들이다.

- <strong>라벨은 최소한으로.</strong> 라벨 하나를 추가할 때마다 "이 값의 가능한 조합 수가 몇 개인가"를 먼저 따진다. `user_id`, `request_id`, 원본 URL 전체처럼 사실상 무한한 값은 라벨에 넣지 않는다. [04장](/study/observability/04-pull-push-cardinality)에서 다룬 카디널리티 폭발은 대부분 계측 시점의 라벨 설계 실수에서 시작된다.
- <strong>base unit을 쓴다.</strong> 밀리초·마이크로초가 아니라 초(seconds), 킬로바이트가 아니라 바이트(bytes)로 통일한다. PromQL은 단위를 모르므로, 어떤 메트릭은 ms, 어떤 메트릭은 s면 쿼리 작성자가 반드시 실수한다. 메트릭 이름 끝에 단위를 명시(`_seconds`, `_bytes`)해 혼동을 원천 차단한다.
- <strong>Counter에는 `_total` 접미사.</strong> 이름만 보고 타입을 유추할 수 있게 한다. `rate()`를 적용해야 하는 메트릭인지 즉시 알 수 있다.
- <strong>Histogram 버킷 경계는 실제 분포에 맞춘다.</strong> 기본 버킷(`prometheus.DefBuckets`, 0.005~10초)이 대부분의 웹 요청엔 맞지만, 배치 작업이나 매우 빠른 내부 RPC라면 도메인에 맞는 버킷을 직접 정의해야 유의미한 `histogram_quantile()` 결과가 나온다.
- <strong>등록은 한 번, 갱신은 핫패스에서.</strong> 메트릭 객체를 요청마다 새로 만들면(`NewCounterVec`을 매 요청 호출) 등록 충돌이나 메모리 누수로 이어진다. 반드시 부팅 시점에 한 번만 등록하고 참조를 재사용한다.

## 4. RED 방법론

<strong>RED</strong>는 Weaveworks의 Tom Wilkie가 제안한, <strong>요청 기반(request-driven)</strong> 서비스를 위한 계측 프레임워크다. 마이크로서비스처럼 "요청을 받아 응답하는" 컴포넌트에 적용한다.

![RED 방법론 — 들어오는 요청을 받는 서비스를 Rate(초당 요청 수)·Errors(초당 실패 요청 수)·Duration(요청 처리 시간 분포) 세 지표로 요약](/images/study-observability/08-red-method-light.png)
![RED 방법론 — 들어오는 요청을 받는 서비스를 Rate(초당 요청 수)·Errors(초당 실패 요청 수)·Duration(요청 처리 시간 분포) 세 지표로 요약](/images/study-observability/08-red-method-dark.png)

- <strong>Rate</strong> — 초당 처리하는 요청 수. `rate(http_requests_total[5m])`
- <strong>Errors</strong> — 초당 실패한 요청 수(비율로 보는 것이 더 유용할 때가 많다). `rate(http_requests_total{status=~"5.."}[5m])`
- <strong>Duration</strong> — 요청 처리에 걸리는 시간의 분포. Histogram으로 계측해 `histogram_quantile()`로 p50/p95/p99를 뽑는다.

세 지표는 대부분 앞서 만든 Counter 하나(`http_requests_total`)와 Histogram 하나(`http_request_duration_seconds`)만으로 커버된다. RED가 강력한 이유는 <strong>서비스 종류가 무엇이든 동일한 세 질문("얼마나 자주, 얼마나 실패, 얼마나 느린가")으로 상태를 요약</strong>할 수 있어서다. 신규 서비스를 온보딩할 때 "이 세 메트릭만은 반드시 있어야 한다"는 최소 기준으로 쓰기 좋다.

## 5. USE 방법론

<strong>USE</strong>는 Netflix의 Brendan Gregg가 제안한, <strong>리소스 기반(resource-driven)</strong> 계측 프레임워크다. CPU, 메모리, 디스크, 네트워크 인터페이스, 커넥션 풀처럼 <strong>유한한 용량을 가진 자원</strong>에 적용한다.

![USE 방법론 — 리소스(CPU·메모리·디스크·커넥션 풀)를 Utilization(사용 중 비율)·Saturation(대기 큐 깊이)·Errors(자원 관련 에러) 세 지표로 관측](/images/study-observability/08-use-method-light.png)
![USE 방법론 — 리소스(CPU·메모리·디스크·커넥션 풀)를 Utilization(사용 중 비율)·Saturation(대기 큐 깊이)·Errors(자원 관련 에러) 세 지표로 관측](/images/study-observability/08-use-method-dark.png)

- <strong>Utilization</strong> — 자원이 바쁜 시간의 비율. `rate(node_cpu_seconds_total{mode!="idle"}[5m])`
- <strong>Saturation</strong> — 자원이 처리하지 못해 쌓인 초과 작업량(큐 깊이, 대기 스레드 수). `node_load1`이나 커넥션 풀의 대기 중 요청 수가 대표적이다.
- <strong>Errors</strong> — 자원 자체에서 발생한 에러(디스크 I/O 에러, OOM kill, 커넥션 거부 수).

RED와 USE는 서로 대체재가 아니라 <strong>관찰 대상의 성격이 다르다.</strong> 요청을 처리하는 서비스 계층은 RED로, 그 서비스가 소비하는 인프라 자원은 USE로 본다. 예를 들어 API 서버 자체는 RED(요청 수·에러율·지연시간)로 보고, 그 API 서버가 쓰는 커넥션 풀·CPU·디스크는 USE(사용률·포화도·에러)로 본다.

## 6. 무엇을 계측할 것인가

두 방법론을 실제 계측 설계에 매핑하면 아래처럼 나뉜다.

| 대상 | 방법론 | 예시 메트릭 |
|---|---|---|
| API 서버, gRPC 서비스 | RED | `http_requests_total`, `http_request_duration_seconds` |
| 메시지 큐 컨슈머 | RED(처리량 관점) + USE(큐 자체) | `messages_consumed_total`, `queue_depth` |
| DB 커넥션 풀 | USE | `db_pool_active_connections`, `db_pool_wait_seconds` |
| 노드 CPU/메모리/디스크 | USE | `node_cpu_seconds_total`, `node_memory_*`, `node_disk_io_time_seconds_total` |
| 배치 잡 | 커스텀(성공/실패/소요시간) | `batch_job_duration_seconds`, `batch_job_last_success_timestamp` |

Google SRE 책이 제안한 <strong>Four Golden Signals</strong>(Latency, Traffic, Errors, Saturation)는 RED와 USE를 사실상 통합한 상위 개념으로 볼 수 있다 — Traffic/Errors/Latency는 RED와 거의 대응하고, Saturation은 USE의 핵심 축이다. 실무에서는 "이 컴포넌트가 요청을 처리하는가, 자원을 소비하는가"를 먼저 구분하고 RED 또는 USE 중 맞는 틀을 적용한 뒤, 필요하면 Saturation 관점을 더해 Golden Signals로 완성하는 순서가 실용적이다.

계측된 메트릭이 실제로 가치를 가지려면 결국 대시보드와 알림으로 이어져야 한다. Grafana 데이터소스 연결과 대시보드 설계는 [31장](/study/observability/31-grafana-datasources-dashboards)에서 다룬다.

::: tip 핵심 정리
- Exporter는 계측할 수 없는 시스템을 위한 브릿지이고, 소스 코드를 통제할 수 있으면 직접 계측(화이트박스)이 항상 우선이다.
- Go/Java/Python 클라이언트 라이브러리는 부팅 시점 등록 + 핫패스 갱신이라는 동일한 패턴을 공유한다.
- 라벨 최소화, base unit 통일, `_total` 접미사, 실제 분포에 맞는 히스토그램 버킷이 계측 품질을 좌우한다.
- RED(Rate/Errors/Duration)는 요청 기반 서비스, USE(Utilization/Saturation/Errors)는 유한 용량 자원에 적용하는 서로 다른 렌즈다.
- 실전에서는 컴포넌트 성격에 따라 RED/USE를 구분 적용하고, Four Golden Signals로 종합해 계측 최소 기준을 세운다.
:::

## 다음 챕터

[PromQL 기초](/study/observability/09-promql-basics)에서는 instant vector와 range vector, 셀렉터와 매처, rate/irate/increase의 함정, 집계 연산자와 by/without, histogram_quantile 같은 필수 함수를 실전 예제로 다룬다.
