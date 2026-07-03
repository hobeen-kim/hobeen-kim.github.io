---
title: "Alloy 개요와 컴포넌트 모델"
description: "Grafana Agent의 후속인 Alloy가 OpenTelemetry Collector 배포판 위에 독자적인 Alloy 구문(구 River)을 얹은 구조임을 설명하고, 컴포넌트 그래프(DAG)·export/reference 연결 방식·배포 모드까지 수집 계층의 핵심 개념을 정리한다."
date: 2026-07-02
tags: [Observability, Alloy, Collector, Pipeline]
prev: /study/observability/27-flamegraph-trace-integration
next: /study/observability/29-alloy-pipelines
---

# Alloy 개요와 컴포넌트 모델

::: info 학습 목표
- Alloy가 Grafana Agent의 후속이며, OpenTelemetry Collector 배포판 위에 Alloy 구문을 얹은 구조라는 점을 이해한다.
- 컴포넌트 그래프(DAG)가 export/reference로 데이터 흐름을 표현하는 방식을 익힌다.
- HCL 계열의 Alloy 구문(구 River)을 읽고 쓸 수 있다.
- discovery.*, prometheus.*, loki.*, otelcol.*, pyroscope.* 컴포넌트 계열의 역할을 구분한다.
- otelcol.* 컴포넌트가 OpenTelemetry Collector 코드베이스 위에 구축돼 있다는 점을 명확히 안다.
- DaemonSet/StatefulSet 배포 모드와 clustering이 필요한 이유를 파악한다.
:::

## 1. Alloy란 무엇인가

<strong>Alloy</strong>는 Grafana Labs가 만든 통합 수집 에이전트로, 메트릭·로그·트레이스·프로파일 네 신호를 한 바이너리로 수집·가공·전달한다. 역사적으로는 <strong>Grafana Agent</strong>(Prometheus Agent 모드 + Promtail 통합 프로젝트)의 후속으로 등장했고, Grafana Agent가 2024년 사실상 End-of-Life를 선언하면서 Alloy가 그 자리를 이어받았다. 자세한 이관 배경은 [공식 마이그레이션 가이드](https://grafana.com/docs/alloy/latest/set-up/migrate/)에 정리돼 있다.

Alloy를 이해하는 데 가장 중요한 사실은 두 가지가 합쳐진 결과물이라는 점이다. 하나는 <strong>OpenTelemetry Collector의 배포판(distribution)</strong>이라는 정체성이다. Alloy는 OTel Collector 코드베이스를 그대로 임베드하고, 그 리시버·프로세서·익스포터를 `otelcol.*`라는 이름의 컴포넌트로 노출한다. 다른 하나는 Grafana Agent 시절부터 이어온 <strong>구성 구문(Alloy 구문, 구 River)</strong>이다. YAML 대신 HCL에 가까운 선언형 구문으로 수집 파이프라인을 컴포넌트 그래프로 표현한다. 즉 "OTel Collector 엔진 + Grafana 자체 구문 + Prometheus/Loki/Pyroscope 네이티브 컴포넌트"를 한 프로세스에 묶은 것이 Alloy다.

![Grafana 수집 에이전트의 계보 타임라인 — 2020 Prometheus Agent mode, 2021 Grafana Agent 출시, 2023 Grafana Agent Flow, 2024 Alloy 출시와 River를 Alloy 구문으로 개명, 2025 Grafana Agent EOL과 Alloy로 완전 이관](/images/study-observability/28-agent-lineage-light.png)
![Grafana 수집 에이전트의 계보 타임라인 — 2020 Prometheus Agent mode, 2021 Grafana Agent 출시, 2023 Grafana Agent Flow, 2024 Alloy 출시와 River를 Alloy 구문으로 개명, 2025 Grafana Agent EOL과 Alloy로 완전 이관](/images/study-observability/28-agent-lineage-dark.png)

## 2. 컴포넌트 모델 — 그래프(DAG)로 파이프라인을 표현한다

Alloy 설정의 핵심 단위는 <strong>컴포넌트(component)</strong>다. 각 컴포넌트는 인자(arguments)를 받아 동작하고, 결과를 <strong>export</strong>로 노출한다. 다른 컴포넌트는 이 export를 참조(reference)해서 자신의 인자로 사용한다. 이 참조 관계가 자동으로 <strong>방향성 비순환 그래프(DAG)</strong>를 만들고, Alloy 런타임은 이 그래프를 따라 데이터를 흘려보낸다. 노드 하나가 죽거나 설정이 바뀌면 그 노드에 의존하는 하위 그래프만 재평가되므로, 대형 파이프라인도 전체 재시작 없이 부분 갱신이 가능하다.

![컴포넌트 그래프(DAG) — discovery.kubernetes.pods가 targets를 discovery.relabel.filter로, output을 prometheus.scrape.app로, forward_to로 prometheus.remote_write.mimir로, 마지막에 remote_write로 Mimir에 전달하며 각 컴포넌트가 앞 컴포넌트의 export를 직접 참조](/images/study-observability/28-component-dag-light.png)
![컴포넌트 그래프(DAG) — discovery.kubernetes.pods가 targets를 discovery.relabel.filter로, output을 prometheus.scrape.app로, forward_to로 prometheus.remote_write.mimir로, 마지막에 remote_write로 Mimir에 전달하며 각 컴포넌트가 앞 컴포넌트의 export를 직접 참조](/images/study-observability/28-component-dag-dark.png)

이 그래프 구조는 YAML 기반의 OTel Collector 설정과 결이 다르다. Collector YAML은 `receivers`/`processors`/`exporters`를 각각 선언하고 `service.pipelines`에서 이름으로 묶는 간접 참조 방식인 반면, Alloy는 컴포넌트가 서로를 직접 가리키므로 데이터가 어디서 와서 어디로 가는지 설정 파일만 보고 즉시 추적할 수 있다.

## 3. Alloy 구문 — HCL 계열, 구 River

Alloy 구문은 HashiCorp의 HCL과 유사한 블록 구조를 쓴다. Grafana Agent Flow 시절에는 이 구문을 <strong>River</strong>라고 불렀고, Alloy로 개명되면서 구문 이름도 "Alloy 구문(Alloy syntax)"으로 통일됐다. 기능은 거의 동일하며, 블록·속성·표현식·참조라는 네 요소로 구성된다.

```alloy
// 블록 형태: component_type "label" { ... }
prometheus.scrape "app" {
  targets = discovery.relabel.filter.output
  forward_to = [prometheus.remote_write.mimir.receiver]

  scrape_interval = "30s"
  job_name        = "app-metrics"
}

// export를 참조하는 방식: <component_type>.<label>.<export_name>
prometheus.remote_write "mimir" {
  endpoint {
    url = "https://mimir.example.com/api/v1/push"

    basic_auth {
      username = "tenant-1"
      password = env("MIMIR_PASSWORD")
    }
  }
}
```

`component_type.label.export_name` 형태로 다른 컴포넌트의 export를 참조하고, `env()`·`sys.env()` 같은 내장 함수로 환경변수를 읽는다. 문자열 보간(`"${...}"`), 리스트·맵 리터럴, 조건식도 지원해 YAML보다 표현력이 높다. 다만 이 표현력이 늘어난 복잡도이기도 해서, 팀에 River/Alloy 구문 학습 곡선이 생긴다는 점은 감안해야 한다 — 이 트레이드오프는 [Collector vs Alloy](/study/observability/30-collector-vs-alloy)에서 더 다룬다.

## 4. 컴포넌트 종류

Alloy 컴포넌트는 이름의 접두사로 소속 생태계를 알 수 있다.

| 접두사 | 담당 신호/역할 | 대표 컴포넌트 |
|---|---|---|
| `discovery.*` | 서비스 디스커버리 | `discovery.kubernetes`, `discovery.relabel`, `discovery.dns` |
| `prometheus.*` | 메트릭 | `prometheus.scrape`, `prometheus.relabel`, `prometheus.remote_write` |
| `loki.*` | 로그 | `loki.source.file`, `loki.source.kubernetes`, `loki.process`, `loki.write` |
| `otelcol.*` | OTel 기반 범용(주로 트레이스) | `otelcol.receiver.otlp`, `otelcol.processor.batch`, `otelcol.exporter.otlp` |
| `pyroscope.*` | 프로파일 | `pyroscope.scrape`, `pyroscope.ebpf`, `pyroscope.write` |
| `local.*`, `remote.*` | 파일·시크릿 읽기 | `local.file`, `remote.s3` |

`discovery.*`는 어떤 신호든 공통으로 쓰는 타깃 발견 계층이다. 쿠버네티스에서는 `discovery.kubernetes`로 Pod·Service·Endpoint를 질의하고, `discovery.relabel`로 라벨을 다듬어 `prometheus.scrape`나 `loki.source.kubernetes`, `pyroscope.scrape`에 동시에 넘길 수 있다 — 즉 하나의 디스커버리 결과를 여러 신호 파이프라인이 재사용하는 구조가 자연스럽게 나온다.

## 5. OTel Collector와의 관계

`otelcol.*` 컴포넌트는 새로 구현된 게 아니라 <strong>OpenTelemetry Collector 코드베이스를 그대로 감싼(wrap) 것</strong>이다. `otelcol.receiver.otlp`는 OTel Collector의 OTLP 리시버를, `otelcol.processor.batch`는 배치 프로세서를 Alloy 구문으로 노출할 뿐 내부 구현은 동일하다. 이 때문에 Alloy 공식 문서는 스스로를 "OpenTelemetry Collector distribution(배포판)"이라고 명시한다. 즉 Alloy는 Collector를 대체하는 완전히 다른 제품이 아니라, <strong>Collector 위에 Prometheus/Loki/Pyroscope 네이티브 지원과 통합 구성 구문을 얹은 상위 계층</strong>이다.

![Alloy 프로세스 내부 구조 — Alloy 구문(구 River, 컴포넌트 그래프)이 실행 엔진의 OpenTelemetry Collector 코드베이스(otelcol.*)·Prometheus 클라이언트(prometheus.*)·Loki 클라이언트(loki.*)·Pyroscope 클라이언트(pyroscope.*)를 한 프로세스에 묶은 구성](/images/study-observability/28-alloy-process-light.png)
![Alloy 프로세스 내부 구조 — Alloy 구문(구 River, 컴포넌트 그래프)이 실행 엔진의 OpenTelemetry Collector 코드베이스(otelcol.*)·Prometheus 클라이언트(prometheus.*)·Loki 클라이언트(loki.*)·Pyroscope 클라이언트(pyroscope.*)를 한 프로세스에 묶은 구성](/images/study-observability/28-alloy-process-dark.png)

실무적으로는 "OTLP를 받아서 처리하는 표준 파이프라인이 필요하다"면 `otelcol.*`를, "Prometheus 생태계와의 호환성(relabel_configs, ServiceMonitor 스타일 스크레이핑)이 중요하다"면 `prometheus.*`를 고르는 식으로 두 계열을 섞어 쓴다. 이 선택 기준은 [Collector vs Alloy 4장](/study/observability/30-collector-vs-alloy)에서 더 구체적으로 다룬다.

## 6. 배포 모드 — DaemonSet, StatefulSet, clustering

Alloy는 역할에 따라 배포 형태가 갈린다. 노드 로컬 데이터(호스트 로그 파일, cAdvisor, eBPF 프로파일링)를 다뤄야 하면 <strong>DaemonSet</strong>으로 모든 노드에 배치한다. 애플리케이션의 OTLP 트레이스를 중앙에서 받아 배치·샘플링 후 백엔드로 내보내는 게이트웨이 역할이면 <strong>Deployment/StatefulSet</strong>으로 몇 개의 레플리카만 둔다.

문제는 스크레이프 대상을 여러 레플리카가 나눠 맡아야 할 때다. Alloy는 <strong>clustering</strong> 기능으로 이를 해결한다. 여러 Alloy 인스턴스가 gossip 프로토콜로 서로를 발견하고, 컨시스턴트 해싱으로 스크레이프 타깃을 자동 분배한다. 특정 인스턴스가 죽으면 나머지가 그 타깃을 흡수해 재조정한다.

![Alloy Cluster 구조 — discovery.kubernetes가 발견한 타깃 N개를 컨시스턴트 해싱으로 3개 레플리카(alloy-0/1/2)에 분배하고, 레플리카들은 gossip 프로토콜로 서로 발견하며 각자 자기 몫만 Mimir/Loki/Tempo로 내보내는 StatefulSet 배치](/images/study-observability/28-clustering-light.png)
![Alloy Cluster 구조 — discovery.kubernetes가 발견한 타깃 N개를 컨시스턴트 해싱으로 3개 레플리카(alloy-0/1/2)에 분배하고, 레플리카들은 gossip 프로토콜로 서로 발견하며 각자 자기 몫만 Mimir/Loki/Tempo로 내보내는 StatefulSet 배치](/images/study-observability/28-clustering-dark.png)

```alloy
alloy {
  clustering {
    enabled = true
  }
}
```

clustering을 켜면 각 인스턴스가 전체 타깃 목록 중 자신이 담당할 몫만 실제로 스크레이프하므로, 레플리카 수를 늘려 스크레이프 부하를 수평 확장할 수 있다. DaemonSet에는 보통 clustering이 필요 없다 — 이미 "이 노드는 이 인스턴스가 담당한다"는 배치 자체가 분배 역할을 하기 때문이다. clustering은 주로 중앙 게이트웨이형 StatefulSet 배포에서 타깃을 여러 레플리카에 나눌 때 쓴다. 타깃 분배의 구체적인 동작은 [다음 챕터 6절](/study/observability/29-alloy-pipelines)에서 파이프라인 예제와 함께 다룬다.

::: tip 핵심 정리
- Alloy는 Grafana Agent의 후속이며, OpenTelemetry Collector 배포판 위에 Alloy 구문(구 River)과 Prometheus/Loki/Pyroscope 네이티브 컴포넌트를 얹은 통합 에이전트다.
- 설정은 컴포넌트 간 export/reference로 이어지는 DAG로 표현되며, 데이터 흐름이 설정 파일에서 바로 드러난다.
- Alloy 구문은 HCL 계열로, `component_type.label.export_name` 참조와 내장 함수를 지원한다.
- `discovery.*`/`prometheus.*`/`loki.*`/`otelcol.*`/`pyroscope.*` 접두사로 컴포넌트 소속 생태계를 구분한다.
- `otelcol.*` 컴포넌트는 신규 구현이 아니라 OpenTelemetry Collector 코드베이스를 그대로 감싼 것이다.
- DaemonSet은 노드 로컬 신호에, StatefulSet + clustering은 중앙 집중형 타깃 분배에 적합하다.
:::

## 다음 챕터

컴포넌트 모델의 원리를 익혔다면, 다음은 실제로 신호별 파이프라인을 조립할 차례다. [Alloy 파이프라인 구성](/study/observability/29-alloy-pipelines)에서는 메트릭·로그·트레이스·프로파일 각각의 구체적인 컴포넌트 체인과, tail sampling·clustering을 실전 설정으로 다룬다.
