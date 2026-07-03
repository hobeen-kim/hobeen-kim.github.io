---
title: "OpenTelemetry"
description: "벤더 중립 관측성 표준인 OpenTelemetry의 API/SDK/Collector 구조와 OTLP 프로토콜, 자동·수동 계측 방식, 시맨틱 컨벤션과 리소스 모델, 그리고 head-based·tail-based 샘플링 전략의 실전 트레이드오프까지 다룬다."
date: 2026-07-02
tags: [OpenTelemetry, OTLP, Tracing, Sampling]
prev: /study/observability/20-distributed-tracing-basics
next: /study/observability/22-tempo-architecture
---

# OpenTelemetry

::: info 학습 목표
- OpenTelemetry가 트레이스뿐 아니라 메트릭·로그·프로파일까지 아우르는 교차 신호 표준임을 이해한다.
- API/SDK/Collector/OTLP로 이어지는 구성 요소의 역할 분담을 안다.
- 자동 계측과 수동 계측의 차이, 언어별 SDK 특성을 파악한다.
- Collector의 receiver → processor → exporter 파이프라인 구조와 head-based·tail-based 샘플링 트레이드오프를 익힌다.
:::

## 1. OpenTelemetry란 — 벤더 중립 표준이자 교차 신호

<strong>OpenTelemetry(OTel)</strong>는 CNCF가 주관하는 관측성 계측 표준으로, 애플리케이션에서 텔레메트리 데이터를 생성·수집·내보내는 API·SDK·프로토콜·도구 일체를 가리킨다. 앞 챕터에서 본 대로 OpenTracing과 OpenCensus의 분절을 해소하며 등장했고, 지금은 트레이스에 국한되지 않는다.

OpenTelemetry의 핵심 가치는 <strong>교차 신호(Cross-Signal)</strong>다. traces·metrics·logs 세 신호(profiles는 아직 실험 단계)를 하나의 계측 라이브러리, 하나의 리소스 모델, 하나의 전송 프로토콜(OTLP)로 다룬다. 이 스터디에서 지금까지 다룬 Prometheus(메트릭)와 Loki(로그)도 OTLP를 직접 수신할 수 있고, Alloy 같은 수집기는 세 신호를 하나의 파이프라인에서 함께 처리한다.

![OTel SDK의 Traces·Metrics·Logs 세 신호가 단일 프로토콜 OTLP(gRPC/HTTP)를 거쳐 Tempo·Prometheus/Mimir·Loki 신호별 백엔드로 전달되는 교차 신호 구조](/images/study-observability/21-cross-signal-otlp.png)

벤더 중립성이 갖는 실질적 이점은 계측 코드를 한 번 작성하면 백엔드를 Tempo에서 다른 트레이싱 시스템으로, 또는 온프레미스에서 SaaS로 바꿔도 애플리케이션 코드를 건드리지 않아도 된다는 점이다. 자세한 개요는 [OpenTelemetry 공식 문서](https://opentelemetry.io/docs/)를 참고한다.

## 2. 구성요소 — API, SDK, Collector, OTLP protocol

OpenTelemetry는 네 계층으로 나뉜다.

| 구성요소 | 역할 |
|---|---|
| API | 계측 코드가 호출하는 인터페이스(span 생성, 메트릭 기록 등). 구현체 없이 인터페이스만 정의 |
| SDK | API의 실제 구현. 샘플러, 프로세서, exporter 설정을 갖는다 |
| Collector | 애플리케이션과 별도 프로세스로 동작하는 수집·가공·전달 파이프라인 |
| OTLP | Collector와 백엔드, 또는 SDK와 Collector 사이의 표준 전송 프로토콜(gRPC/HTTP + Protobuf) |

애플리케이션 라이브러리는 API에만 의존하는 것이 이상적이다. SDK를 초기화하지 않으면 API 호출은 no-op(아무 일도 하지 않음)으로 동작하므로, 라이브러리 개발자가 계측 코드를 심어도 최종 사용자가 OTel을 쓰지 않으면 비용이 없다.

Collector는 애플리케이션 프로세스 밖에서 동작하는 독립 실행 파일로, 사이드카·데몬셋·게이트웨이 등 다양한 형태로 배포할 수 있다. Collector 없이 SDK가 백엔드로 직접 내보낼 수도 있지만, 실무에서는 배치·재시도·필터링·샘플링을 SDK 밖으로 빼내기 위해 Collector를 거치는 구성이 표준이다.

```yaml
# SDK 설정 예시 (환경변수 기반, 언어 공통)
OTEL_SERVICE_NAME=order-service
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
OTEL_EXPORTER_OTLP_PROTOCOL=grpc
OTEL_TRACES_SAMPLER=parentbased_traceidratio
OTEL_TRACES_SAMPLER_ARG=0.1
```

## 3. 계측 — auto vs manual instrumentation

계측(Instrumentation)은 애플리케이션 코드에 span·메트릭 생성 로직을 심는 작업이다. 두 방식이 있다.

<strong>자동 계측(Auto Instrumentation)</strong>은 애플리케이션 코드를 수정하지 않고 프레임워크·라이브러리 수준에서 span을 자동 생성한다. Java는 javaagent를 프로세스에 attach해 바이트코드를 조작하고, Python은 `opentelemetry-instrument` 래퍼로 알려진 라이브러리(Flask, requests, psycopg2 등)를 monkey-patch한다. HTTP 서버 진입, DB 쿼리, 외부 API 호출 같은 흔한 패턴은 자동 계측만으로 상당 부분 커버된다.

```bash
# Java: javaagent로 자동 계측
java -javaagent:opentelemetry-javaagent.jar \
     -Dotel.service.name=order-service \
     -Dotel.exporter.otlp.endpoint=http://otel-collector:4317 \
     -jar order-service.jar
```

<strong>수동 계측(Manual Instrumentation)</strong>은 비즈니스 로직 안에서 의미 있는 구간에 직접 span을 만든다. 자동 계측이 잡아내지 못하는 도메인 특화 작업(예: "재고 예약 알고리즘 실행")을 세밀하게 추적하려면 수동 계측이 필요하다.

::: tabs
@tab Go
```go
tracer := otel.Tracer("order-service")

func ReserveInventory(ctx context.Context, sku string) error {
    ctx, span := tracer.Start(ctx, "ReserveInventory",
        trace.WithAttributes(attribute.String("sku", sku)))
    defer span.End()

    if err := reserve(ctx, sku); err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, "reservation failed")
        return err
    }
    return nil
}
```
@tab Java
```java
Tracer tracer = openTelemetry.getTracer("order-service");

public void reserveInventory(String sku) {
    Span span = tracer.spanBuilder("ReserveInventory")
        .setAttribute("sku", sku)
        .startSpan();
    try (Scope scope = span.makeCurrent()) {
        reserve(sku);
    } catch (Exception e) {
        span.recordException(e);
        span.setStatus(StatusCode.ERROR, "reservation failed");
        throw e;
    } finally {
        span.end();
    }
}
```
@tab Python
```python
tracer = trace.get_tracer("order-service")

def reserve_inventory(sku: str):
    with tracer.start_as_current_span("ReserveInventory") as span:
        span.set_attribute("sku", sku)
        try:
            reserve(sku)
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, "reservation failed"))
            raise
```
:::

실무에서는 자동 계측으로 골격(HTTP/DB 경계)을 잡고, 비즈니스 크리티컬 구간만 수동 계측으로 보강하는 조합이 일반적이다. 자동 계측만으로는 "왜 느린가"의 세부 원인까지 파고들기 어렵기 때문이다.

## 4. 시맨틱 컨벤션과 리소스

span·메트릭에 붙이는 attribute 이름이 계측 라이브러리마다 제각각이면 쿼리와 대시보드를 재사용할 수 없다. <strong>시맨틱 컨벤션(Semantic Conventions)</strong>은 이 이름과 값의 형식을 표준화한다. 예를 들어 HTTP 서버 span은 `http.request.method`, `http.response.status_code`, `url.path` 같은 고정된 키를 쓰도록 규정한다. DB 호출은 `db.system.name`, `db.query.text` 같은 컨벤션을 따른다.

::: warning 시맨틱 컨벤션은 버전마다 이름이 바뀐다
초기 스펙의 `http.method`가 이후 `http.request.method`로, `net.peer.name`이 `server.address`로 바뀌는 등 안정화 과정에서 속성 이름이 변경돼 왔다. 대시보드·알림·TraceQL 쿼리를 작성할 때는 사용 중인 계측 라이브러리 버전이 따르는 시맨틱 컨벤션 버전을 확인해야 한다. [시맨틱 컨벤션 문서](https://opentelemetry.io/docs/specs/semconv/)에서 최신 안정화 상태를 확인한다.
:::

<strong>리소스(Resource)</strong>는 span·메트릭·로그를 생성한 주체(서비스, 프로세스, 호스트, 클라우드 환경)를 나타내는 속성 집합이다. 개별 span attribute와 달리 한 프로세스에서 나오는 모든 텔레메트리에 공통으로 붙는다.

```yaml
# 리소스 속성 예시
resource:
  service.name: order-service
  service.namespace: checkout
  service.version: 1.4.2
  deployment.environment.name: production
  k8s.pod.name: order-service-7f9c8-x2k1p
  k8s.namespace.name: checkout
```

`service.name`은 사실상 필수 리소스 속성이다. Tempo·Prometheus·Loki 어느 백엔드에서든 "어느 서비스에서 온 데이터인가"를 구분하는 1차 기준이 이 값이기 때문이다.

## 5. Collector 아키텍처 — receiver → processor → exporter

<strong>OpenTelemetry Collector</strong>는 세 단계 파이프라인으로 동작한다. receiver가 데이터를 받아들이고, processor가 가공하며, exporter가 백엔드로 내보낸다.

![Collector가 otlp·prometheus·filelog receiver로 받아 memory_limiter→attributes→tail_sampling→batch processor 체인으로 가공한 뒤 otlp/Tempo·prometheusremotewrite/Mimir·loki exporter로 내보내는 파이프라인](/images/study-observability/21-collector-pipeline.png)

파이프라인은 신호별(traces/metrics/logs)로 따로 구성하며, 하나의 receiver를 여러 파이프라인이 공유할 수도 있다.

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  memory_limiter:
    check_interval: 1s
    limit_mib: 512
  batch:
    timeout: 5s
    send_batch_size: 1024

exporters:
  otlp/tempo:
    endpoint: tempo:4317
    tls:
      insecure: true
  prometheusremotewrite:
    endpoint: http://mimir:9009/api/v1/push

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [otlp/tempo]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheusremotewrite]
```

Collector는 애플리케이션과 같은 노드에 사이드카/데몬셋으로 두는 <strong>에이전트 모드</strong>와, 여러 에이전트의 데이터를 중앙에서 모아 처리하는 <strong>게이트웨이 모드</strong>를 조합해 배포하는 것이 일반적이다. 게이트웨이 계층에 tail sampling처럼 전체 trace를 봐야 하는 processor를 두고, 에이전트 계층은 가벼운 배치·필터링만 담당하는 식이다.

## 6. 샘플링 전략 — head-based vs tail-based 트레이드오프

앞 챕터에서 미리 본 head-based·tail-based 샘플링을 실제 구현 관점에서 비교한다.

<strong>head-based 샘플링</strong>은 SDK 레벨에서 trace 시작 시점에 결정된다. 대표적으로 `parentbased_traceidratio` 샘플러는 trace_id를 해시해 설정된 비율(예: 10%)만 샘플링하고, 상위 span의 샘플링 결정을 하위 span이 그대로 따른다(parent-based). 구현이 단순하고 SDK 단계에서 버려지는 span은 아예 생성 비용도 최소화할 수 있다는 장점이 있지만, 에러 trace나 느린 trace를 우선적으로 잡아내지는 못한다.

<strong>tail-based 샘플링</strong>은 Collector의 `tail_sampling` processor가 담당한다. 하나의 trace에 속한 모든 span이 도착할 때까지 기다린 뒤, 정책에 따라 수집 여부를 결정한다.

```yaml
processors:
  tail_sampling:
    decision_wait: 10s
    policies:
      - name: errors-policy
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: slow-traces-policy
        type: latency
        latency: { threshold_ms: 1000 }
      - name: baseline-sample
        type: probabilistic
        probabilistic: { sampling_percentage: 5 }
```

이 설정은 "에러가 있으면 무조건 수집, 1초 넘게 걸리면 무조건 수집, 나머지는 5%만 확률적으로 수집"하는 정책이다. tail sampling은 모든 span이 같은 Collector 인스턴스로 모여야 정확한 판단이 가능하므로, 여러 게이트웨이 인스턴스를 둘 경우 trace_id 기준 로드밸런싱(consistent hashing)이 앞단에 필요하다.

::: warning tail sampling은 공짜가 아니다
`decision_wait` 동안 모든 span을 메모리에 버퍼링해야 하므로, 트래픽이 큰 서비스에서는 Collector 메모리 사용량이 급격히 늘어난다. 요청량이 많고 trace당 span 수가 많을수록 게이트웨이 인스턴스 수와 메모리 예산을 함께 늘려야 한다.
:::

Grafana Alloy에서도 동일한 개념의 컴포넌트로 tail sampling을 구성할 수 있으며, 실제 파이프라인 작성법은 [Alloy 파이프라인 구성](/study/observability/29-alloy-pipelines) 챕터에서 다룬다.

::: tip 핵심 정리
- OpenTelemetry는 traces·metrics·logs를 하나의 계측 표준·프로토콜(OTLP)로 다루는 교차 신호 표준이다.
- API(인터페이스)·SDK(구현)·Collector(독립 파이프라인)·OTLP(전송 프로토콜) 네 계층으로 구성된다.
- 자동 계측은 코드 수정 없이 프레임워크 경계를 커버하고, 수동 계측은 비즈니스 로직의 세밀한 구간을 보강한다.
- 시맨틱 컨벤션은 속성 이름을 표준화하지만 버전에 따라 바뀌므로 계측 버전을 확인해야 하며, 리소스는 프로세스 단위 공통 메타데이터다.
- Collector는 receiver → processor → exporter 파이프라인으로 동작하며, 에이전트·게이트웨이 모드를 조합해 배포한다.
- head-based 샘플링은 가볍지만 확률적이고, tail-based 샘플링(Collector의 tail_sampling processor)은 에러·지연 trace를 정확히 잡아내는 대신 버퍼링 메모리 비용이 크다.
:::

## 다음 챕터

[Tempo 아키텍처](/study/observability/22-tempo-architecture)에서는 OpenTelemetry가 내보낸 trace 데이터를 실제로 저장·질의하는 백엔드인 Tempo를 다룬다. 검색 인덱스 없이 오브젝트 스토리지만으로 동작하는 설계 철학, distributor→ingester로 이어지는 쓰기 경로, 그리고 metrics-generator까지 살펴본다.
