---
title: "Collector vs Alloy"
description: "OpenTelemetry Collector와 Grafana Alloy가 대체 관계가 아니라 포함 관계임을 신호 지원·프로파일·clustering 기능 비교와 구성 방식 차이로 짚고, 벤더 중립성과 운영 조직 상황에 맞는 선택 기준·마이그레이션 경로를 정리한다."
date: 2026-07-02
tags: [Observability, Alloy, OpenTelemetry, Collector]
prev: /study/observability/29-alloy-pipelines
next: /study/observability/31-grafana-datasources-dashboards
---

# Collector vs Alloy

::: info 학습 목표
- OpenTelemetry Collector와 Alloy가 경쟁 관계가 아니라 포함 관계라는 점을 역사적 배경과 함께 이해한다.
- 신호 지원, 프로파일링, clustering 기능을 기준으로 두 도구를 비교할 수 있다.
- Collector의 YAML 파이프라인 구성과 Alloy의 컴포넌트 그래프 구성 차이를 안다.
- OTel Collector 생태계의 벤더 중립성이 갖는 실무적 의미를 파악한다.
- 조직 상황(Prometheus/Loki 의존도, 벤더 전략, 팀 숙련도)에 따른 선택 기준을 세운다.
- Collector에서 Alloy로, 혹은 그 반대로 마이그레이션할 때 고려할 점을 안다.
:::

## 1. 두 도구의 관계와 역사

<strong>OpenTelemetry Collector</strong>는 CNCF OpenTelemetry 프로젝트가 만든 벤더 중립 수집·가공·전달 파이프라인이다. 리시버(receiver)·프로세서(processor)·익스포터(exporter)를 YAML로 조합해 어떤 벤더의 백엔드로도 텔레메트리를 보낼 수 있게 설계됐다. <strong>Alloy</strong>는 Grafana Labs가 이 Collector 코드베이스를 임베드해 만든 배포판이다 — [1장](/study/observability/28-alloy-overview)에서 다뤘듯 `otelcol.*` 컴포넌트는 Collector의 리시버/프로세서/익스포터를 그대로 감싼 것이다.

역사적으로는 Prometheus Agent 모드와 Promtail을 통합한 Grafana Agent가 먼저 있었고, 이후 Grafana Agent Flow가 컴포넌트 그래프 모델을 도입했으며, 이 Flow 모델이 OTel Collector 엔진과 결합해 Alloy로 재탄생했다. 따라서 "Collector vs Alloy"는 상호 배타적인 두 제품을 고르는 문제가 아니라, <strong>순수 Collector를 쓸지, Collector를 감싼 Grafana 배포판을 쓸지</strong>를 고르는 문제에 가깝다.

![Collector와 Alloy의 포함 관계 — CNCF 벤더 중립 코드베이스인 OpenTelemetry Collector가 opentelemetry-collector-contrib(커뮤니티 리시버/프로세서/익스포터)로 파생되고 코드베이스 임베드로 Grafana Alloy(Collector 임베드 + Alloy 구문 + prometheus.*/loki.*/pyroscope.* 네이티브 컴포넌트)를 이루며, EOL된 Grafana Agent가 Alloy로 후속 이관](/images/study-observability/30-collector-alloy-relation-light.png)
![Collector와 Alloy의 포함 관계 — CNCF 벤더 중립 코드베이스인 OpenTelemetry Collector가 opentelemetry-collector-contrib(커뮤니티 리시버/프로세서/익스포터)로 파생되고 코드베이스 임베드로 Grafana Alloy(Collector 임베드 + Alloy 구문 + prometheus.*/loki.*/pyroscope.* 네이티브 컴포넌트)를 이루며, EOL된 Grafana Agent가 Alloy로 후속 이관](/images/study-observability/30-collector-alloy-relation-dark.png)

## 2. 기능 비교

두 도구는 신호 지원 범위와 운영 기능에서 뚜렷한 차이가 있다.

| 기준 | OpenTelemetry Collector | Grafana Alloy |
|---|---|---|
| 메트릭/로그/트레이스(OTLP) | 지원 | 지원 (`otelcol.*`) |
| Prometheus 네이티브 스크레이핑 | `prometheus` 리시버로 제한적 지원 | `prometheus.scrape`로 완전한 relabel/SD 지원 |
| Loki 네이티브 로그 처리 | 커뮤니티 익스포터 수준 | `loki.*`로 1급 지원 (stage 파이프라인) |
| 연속 프로파일링 | 실험적(profiles signal 표준화 진행 중) | `pyroscope.*`로 정식 지원 |
| clustering(타깃 자동 분배) | 없음 (별도 로드밸런서·오퍼레이터 필요) | 내장 (`alloy { clustering {} }`) |
| 구성 언어 | YAML | Alloy 구문(HCL 계열, 구 River) |
| 벤더 중립성 | 매우 높음 (CNCF 표준) | Grafana 생태계에 최적화, OTLP로 타 벤더도 가능 |
| 배포판 크기 | contrib 빌드는 매우 큼 (모든 컴포넌트 포함) | Grafana 관련 컴포넌트에 집중, 상대적으로 목적 지향적 |

가장 큰 차이는 <strong>프로파일 신호</strong>와 <strong>clustering</strong>이다. OTel 진영은 아직 프로파일을 정식 signal로 완전히 표준화하는 중이고([OpenTelemetry Profiling](https://opentelemetry.io/docs/specs/otel/profiles/) 참고), Alloy는 Pyroscope 인수 이후 프로파일을 메트릭·로그·트레이스와 동급으로 다룬다. clustering도 Collector 자체에는 없는 기능으로, Collector로 동등한 걸 하려면 오퍼레이터(Target Allocator)나 별도 로드밸런서를 조합해야 한다.

## 3. 구성 방식 — YAML 파이프라인 vs 컴포넌트 그래프

같은 목적(OTLP 트레이스를 받아 배치 후 내보내기)의 설정을 나란히 비교하면 구성 철학의 차이가 뚜렷하다.

::: tabs
@tab Collector (YAML)
```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  batch:
    timeout: 5s
    send_batch_size: 1024

exporters:
  otlp:
    endpoint: tempo.example.com:4317
    tls:
      insecure: false

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp]
```
@tab Alloy (Alloy 구문)
```alloy
otelcol.receiver.otlp "default" {
  grpc {
    endpoint = "0.0.0.0:4317"
  }
  output {
    traces = [otelcol.processor.batch.default.input]
  }
}

otelcol.processor.batch "default" {
  timeout          = "5s"
  send_batch_size  = 1024
  output {
    traces = [otelcol.exporter.otlp.tempo.input]
  }
}

otelcol.exporter.otlp "tempo" {
  client {
    endpoint = "tempo.example.com:4317"
    tls {
      insecure = false
    }
  }
}
```
:::

Collector YAML은 `receivers`/`processors`/`exporters`를 각각 이름으로 선언하고 `service.pipelines`에서 그 이름들을 나열해 묶는 <strong>간접 참조</strong> 방식이다. 파이프라인이 여러 개고 컴포넌트를 공유하기 시작하면, 어떤 리시버가 어떤 익스포터로 실제로 이어지는지 `service.pipelines` 블록을 계속 오가며 추적해야 한다. Alloy는 `output { traces = [...] }`로 다음 컴포넌트를 <strong>직접 참조</strong>하므로 파일 하나만 봐도 데이터 흐름이 드러난다. 대신 Alloy 구문 자체를 새로 익혀야 하고, YAML 대비 도구·린터·자동완성 생태계는 아직 더 작다.

## 4. 생태계·벤더 중립성

OTel Collector의 가장 큰 무기는 <strong>벤더 중립성</strong>이다. CNCF 프로젝트로서 Datadog, New Relic, AWS, Grafana 등 사실상 모든 관측성 벤더가 Collector용 익스포터를 유지보수하고, `opentelemetry-collector-contrib` 저장소에는 수백 개의 리시버·프로세서·익스포터가 커뮤니티 기여로 쌓여 있다. 특정 벤더에 락인(lock-in)되지 않고 싶은 조직, 혹은 멀티 벤더 전략을 쓰는 조직에게는 이 점이 결정적이다.

Alloy도 OTLP 익스포터를 통해 임의의 OTel 호환 백엔드로 데이터를 보낼 수 있어 완전히 락인되는 것은 아니지만, `prometheus.*`/`loki.*`/`pyroscope.*` 네이티브 컴포넌트의 존재 자체가 Grafana 스택을 최적 경로로 상정하고 설계됐다는 신호다. 즉 Alloy를 고르는 것은 "Grafana LGTM+ 스택을 주력 백엔드로 쓰겠다"는 암묵적 결정과 맞닿아 있다.

## 5. 선택 기준

몇 가지 축으로 판단하면 결정이 쉬워진다.

- <strong>백엔드가 Grafana 스택(Mimir/Loki/Tempo/Pyroscope)인가</strong> — 그렇다면 Alloy가 네이티브 컴포넌트와 clustering을 제공해 운영 부담이 적다.
- <strong>멀티 벤더 전략을 쓰거나 벤더 락인을 피해야 하는가</strong> — 순수 OTel Collector가 안전한 선택이다. 어떤 벤더의 계약이 바뀌어도 익스포터만 교체하면 된다.
- <strong>연속 프로파일링이 핵심 요구사항인가</strong> — Alloy의 `pyroscope.*`가 현재로선 가장 성숙한 경로다.
- <strong>스크레이프 타깃이 매우 많아 수평 확장·자동 분배가 필요한가</strong> — Alloy clustering이 없으면 Collector에서는 Target Allocator나 별도 샤딩 전략을 직접 구성해야 한다.
- <strong>팀이 이미 OTel Collector YAML에 익숙하고 다른 신호는 별도 도구(Fluent Bit, Prometheus)로 운영 중인가</strong> — 굳이 전면 전환할 필요 없이 Collector를 트레이스 전용으로 유지하고 나머지는 기존 도구를 쓰는 혼합 구성도 합리적이다.

![수집 계층 선택 의사결정 트리 — '백엔드가 Grafana LGTM+ 스택?'에서 No면 순수 벤더 중립 OTel Collector, Yes면 '벤더 락인 회피가 최우선 정책?'으로 가서 Yes면 OTel Collector + Grafana OTLP 익스포터, No면 'clustering·프로파일 네이티브 지원 필요?'로 가서 Yes면 Alloy, No면 둘 다 가능하니 팀 숙련도로 결정](/images/study-observability/30-selection-tree-light.png)
![수집 계층 선택 의사결정 트리 — '백엔드가 Grafana LGTM+ 스택?'에서 No면 순수 벤더 중립 OTel Collector, Yes면 '벤더 락인 회피가 최우선 정책?'으로 가서 Yes면 OTel Collector + Grafana OTLP 익스포터, No면 'clustering·프로파일 네이티브 지원 필요?'로 가서 Yes면 Alloy, No면 둘 다 가능하니 팀 숙련도로 결정](/images/study-observability/30-selection-tree-dark.png)

## 6. 마이그레이션

Grafana Agent를 여전히 쓰고 있다면 EOL이 지난 시점이므로 Alloy로의 이관이 사실상 필수다. Grafana는 `river-to-alloy`와 동일한 구성 파일을 대부분 그대로 인식하도록 하위 호환을 유지했고, `metrics`/`logs`/`traces` 블록 기반의 구(舊) Grafana Agent Static 모드 설정은 공식 변환 가이드를 따라 컴포넌트 그래프 형태로 재작성해야 한다.

순수 OTel Collector에서 Alloy로 옮기는 경우, YAML의 `receivers`/`processors`/`exporters`/`service.pipelines` 구조를 컴포넌트 블록과 `output`/`input` 참조로 기계적으로 변환할 수 있다 — 리시버는 파이프라인의 시작 컴포넌트가 되고, `service.pipelines`의 순서가 그대로 `output { ... }` 참조 체인이 된다. 반대로 Alloy에서 순수 Collector로 되돌아가는 경우는 `prometheus.*`/`loki.*`/`pyroscope.*` 네이티브 컴포넌트를 OTLP 리시버 기반으로 다시 설계해야 하므로 상대적으로 손이 많이 간다. 두 방향 모두 실제 전환 전에는 스테이징 환경에서 동일 트래픽을 병행 수집해 메트릭 이름·라벨·트레이스 구조가 동일하게 나오는지 검증하는 절차를 거치는 것이 안전하다.

::: tip 핵심 정리
- Alloy는 OTel Collector와 경쟁하는 별도 제품이 아니라, Collector 코드베이스를 임베드한 Grafana 배포판이다.
- 신호 지원은 대부분 겹치지만, 연속 프로파일링과 clustering은 현재 Alloy가 더 성숙하게 지원한다.
- Collector는 YAML의 간접 참조(`service.pipelines`)로, Alloy는 컴포넌트 그래프의 직접 참조(`output`/`input`)로 파이프라인을 구성한다.
- OTel Collector의 벤더 중립성과 거대한 contrib 생태계는 멀티 벤더 전략에서 여전히 강점이다.
- 선택 기준은 백엔드가 Grafana 스택인지, 벤더 락인 회피가 우선인지, clustering·프로파일이 필요한지로 정리된다.
- Grafana Agent는 EOL이므로 Alloy 이관이 사실상 필수이며, Collector↔Alloy 간 전환은 병행 수집으로 검증 후 진행한다.
:::

## 다음 챕터

수집 계층에서 어떤 도구를 쓰든, 결국 데이터는 Grafana에서 하나로 모여야 값어치가 생긴다. [데이터소스와 대시보드](/study/observability/31-grafana-datasources-dashboards)에서는 Prometheus/Mimir·Loki·Tempo·Pyroscope를 Grafana 데이터소스로 연결하는 방법과, 패널·변수 설계의 실전 패턴을 다룬다.
