---
title: "Kubernetes 배포"
description: "관측성 스택을 쿠버네티스에 올리는 표준 경로인 kube-prometheus-stack Helm 차트 구성, Prometheus Operator의 CRD 모델, ServiceMonitor/PodMonitor 스크레이프 선언, Alloy DaemonSet 기반 로그·프로파일 수집, Grafana Operator 대시보드 프로비저닝, 그리고 리소스·스토리지 사이징 실전 팁을 다룬다."
date: 2026-07-02
tags: [Kubernetes, Operator, Deployment, SRE]
prev: /study/observability/36-ha-multitenancy-federation
next: /study/observability/38-production-troubleshooting
---

# Kubernetes 배포

::: info 학습 목표
- kube-prometheus-stack Helm 차트가 번들링하는 컴포넌트 구성과 서브차트 구조를 이해한다.
- Prometheus Operator가 감시하는 CRD(Prometheus, ServiceMonitor, PodMonitor, PrometheusRule, Alertmanager)의 역할과 관계를 파악한다.
- ServiceMonitor/PodMonitor로 스크레이프 대상을 선언적으로 관리하는 실전 패턴을 익힌다.
- Alloy를 DaemonSet으로 배포해 로그·프로파일을 수집하는 구성을 다룬다.
- Grafana Operator로 대시보드를 GitOps 방식으로 프로비저닝하는 방법을 안다.
- 프로덕션 규모에 맞는 리소스·스토리지 사이징 기준과 운영 팁을 습득한다.
:::

## 1. kube-prometheus-stack

쿠버네티스 위에 Prometheus 생태계를 직접 하나씩 배포하는 방식은 CRD 등록 순서, RBAC, 서비스 계정, 웹훅 인증서 관리까지 손이 많이 간다. 실무에서는 사실상 표준으로 굳어진 [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack) Helm 차트를 쓴다. Helm 차트 자체의 구조와 배포 메커니즘은 [Helm](/study/kubernetes/43-helm) 챕터에서 다뤘으므로, 여기서는 이 차트가 무엇을 번들링하는지에 집중한다.

kube-prometheus-stack은 단일 컴포넌트가 아니라 여러 서브차트와 리소스 묶음이다.

- <strong>Prometheus Operator</strong>: CRD를 등록하고 감시하는 컨트롤러. 차트의 핵심이며 나머지 컴포넌트를 CR로 선언할 수 있게 만든다.
- <strong>kube-state-metrics</strong>: 쿠버네티스 오브젝트 상태를 메트릭으로 변환하는 서브차트.
- <strong>prometheus-node-exporter</strong>: 노드 하드웨어 메트릭을 노출하는 DaemonSet 서브차트.
- <strong>Grafana</strong>: `grafana/grafana` 서브차트를 포함하며, Prometheus/Alertmanager 데이터소스가 기본 프로비저닝된다.
- <strong>기본 알림 규칙·대시보드</strong>: [kubernetes-mixin](https://github.com/kubernetes-monitoring/kubernetes-mixin) 기반의 `PrometheusRule`과 대시보드 JSON이 함께 설치돼, 별도 작성 없이 클러스터 기본 알림·대시보드를 갖춘다.

```yaml
# values.yaml (발췌)
prometheus:
  prometheusSpec:
    retention: 15d
    scrapeInterval: 30s
    serviceMonitorSelectorNilUsesHelmValues: false   # 모든 네임스페이스의 ServiceMonitor 허용
    podMonitorSelectorNilUsesHelmValues: false
    resources:
      requests: { cpu: 500m, memory: 2Gi }
      limits: { memory: 4Gi }

grafana:
  adminPassword: "changeme"
  persistence:
    enabled: true
    size: 10Gi

alertmanager:
  alertmanagerSpec:
    replicas: 3
```

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  -f values.yaml
```

::: warning serviceMonitorSelectorNilUsesHelmValues 함정
기본값은 `true`다. 이 경우 Prometheus는 차트가 설치한 `release: kube-prometheus-stack` 라벨이 붙은 ServiceMonitor만 인식하고, 사용자가 임의로 만든 ServiceMonitor는 무시한다. 모든 네임스페이스의 ServiceMonitor를 받으려면 `false`로 바꾸거나, 반대로 라벨 규칙을 팀 전체에 강제해 무분별한 스크레이프 대상 추가를 막을 수도 있다. 어느 쪽이든 팀 컨벤션으로 명시해야 한다.
:::

## 2. Prometheus Operator와 CRD

[Prometheus Operator](/study/kubernetes/38-operator)는 쿠버네티스 컨트롤러 패턴을 그대로 따른다. CRD를 watch하다가 변경을 감지하면 실제 리소스(StatefulSet, Secret, ConfigMap)를 조정(reconcile)한다. 등록하는 주요 CRD는 다섯 가지다.

| CRD | 역할 |
|---|---|
| `Prometheus` | Prometheus 서버 자체를 선언. replicas, retention, storage, 어떤 ServiceMonitor/PodMonitor/PrometheusRule을 선택할지(selector)를 정의 |
| `ServiceMonitor` | Service 뒤의 Pod를 스크레이프 대상으로 선언 |
| `PodMonitor` | Service 없이 Pod를 직접 스크레이프 대상으로 선언 |
| `PrometheusRule` | Recording rule·Alerting rule을 선언 |
| `Alertmanager` | Alertmanager 클러스터 자체를 선언 |

Operator는 이 CRD들을 조합해 Prometheus가 실제로 읽는 설정 파일(`prometheus.yaml`)과 룰 파일을 생성하고, Secret으로 만들어 Prometheus Pod에 마운트한다. 사용자는 `scrape_configs`의 relabel 문법을 직접 다루지 않고, CR을 만들고 지우는 것만으로 스크레이프 대상과 알림 규칙을 관리한다.

![Prometheus Operator가 사용자 선언 CRD(Prometheus·ServiceMonitor·PodMonitor·PrometheusRule)를 watch·reconcile해 Secret·ConfigMap·StatefulSet을 생성하고 Prometheus Pod에 마운트하는 구조](/images/study-observability/37-operator-crd-light.png)
![Prometheus Operator가 사용자 선언 CRD(Prometheus·ServiceMonitor·PodMonitor·PrometheusRule)를 watch·reconcile해 Secret·ConfigMap·StatefulSet을 생성하고 Prometheus Pod에 마운트하는 구조](/images/study-observability/37-operator-crd-dark.png)

CR 사이의 매칭은 라벨 selector로 이뤄진다는 점이 핵심이다. `Prometheus` CR의 `serviceMonitorSelector`가 특정 라벨을 요구하면, 그 라벨이 없는 ServiceMonitor는 아무리 클러스터에 존재해도 무시된다. 멀티테넌시 환경에서 Prometheus 인스턴스를 여러 개 운영할 때(예: 팀별 분리), 이 selector가 곧 "어느 Prometheus가 어느 팀의 타깃을 스크레이프할지"를 가르는 경계선이 된다. HA·멀티테넌시 전략 자체는 [HA·멀티테넌시·페더레이션](/study/observability/36-ha-multitenancy-federation)에서 다룬 내용과 이어진다.

## 3. ServiceMonitor·PodMonitor로 스크레이프 선언

`ServiceMonitor`는 Service를 매개로 Endpoint(Pod)를 찾는다. Service가 존재하지 않는 워크로드(예: 헤드리스가 아닌 Job, 사이드카 전용 메트릭 포트)는 `PodMonitor`로 Pod를 직접 대상으로 삼는다.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: order-service
  namespace: prod
  labels:
    release: kube-prometheus-stack   # Prometheus CR의 selector와 매칭
spec:
  namespaceSelector:
    matchNames: ["prod"]
  selector:
    matchLabels:
      app.kubernetes.io/name: order-service
  endpoints:
  - port: metrics
    path: /metrics
    interval: 30s
    scrapeTimeout: 10s
    relabelings:
    - sourceLabels: [__meta_kubernetes_pod_name]
      targetLabel: pod
    metricRelabelings:
    - sourceLabels: [__name__]
      regex: 'go_gc_duration_seconds.*'
      action: drop   # 고카디널리티 불필요 메트릭 사전 차단
```

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: batch-worker
  namespace: prod
  labels:
    release: kube-prometheus-stack
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: batch-worker
  podMetricsEndpoints:
  - port: metrics
    interval: 60s   # 배치 워크로드는 스크레이프 주기를 완화해 리소스 절약
```

`relabelings`는 스크레이프 <strong>대상 자체</strong>(어떤 Pod의 어떤 포트를 긁을지)를 조정하고, `metricRelabelings`는 스크레이프해서 <strong>가져온 이후의 메트릭</strong>을 필터링한다. 카디널리티가 큰 메트릭을 소스 단에서 `action: drop`으로 걷어내는 것이 [카디널리티 관리와 비용](/study/observability/34-cardinality-cost)에서 다룬 사전 차단 전략의 실제 적용 지점이다.

## 4. Alloy DaemonSet 배포

메트릭 스크레이핑은 Prometheus가 Pull로 직접 수행하지만, 로그와 프로파일은 각 노드에서 능동적으로 수집해 밀어 넣는(push) 에이전트가 필요하다. [Alloy](https://grafana.com/docs/alloy/latest/)를 DaemonSet으로 배포해 모든 노드에서 컨테이너 로그와 eBPF 프로파일을 걷어 올린다.

```yaml
# alloy values.yaml (발췌)
controller:
  type: daemonset

alloy:
  configMap:
    content: |
      discovery.kubernetes "pods" {
        role = "pod"
      }

      loki.source.kubernetes "containers" {
        targets    = discovery.kubernetes.pods.targets
        forward_to = [loki.write.default.receiver]
      }

      loki.write "default" {
        endpoint {
          url = "http://loki-gateway.monitoring.svc:3100/loki/api/v1/push"
        }
      }

      pyroscope.ebpf "profiles" {
        forward_to = [pyroscope.write.default.receiver]
      }

      pyroscope.write "default" {
        endpoint {
          url = "http://pyroscope.monitoring.svc:4040"
        }
      }
  mounts:
    varlog: true
    dockercontainers: true

rbac:
  create: true   # discovery.kubernetes가 apiserver를 조회하려면 필요
```

![모든 노드에 DaemonSet으로 배치된 Alloy가 각 노드의 애플리케이션 Pod에서 stdout/stderr 로그와 eBPF 프로파일을 수집해 Loki(loki.write)와 Pyroscope(pyroscope.write)로 push하는 구조](/images/study-observability/37-alloy-daemonset-light.png)
![모든 노드에 DaemonSet으로 배치된 Alloy가 각 노드의 애플리케이션 Pod에서 stdout/stderr 로그와 eBPF 프로파일을 수집해 Loki(loki.write)와 Pyroscope(pyroscope.write)로 push하는 구조](/images/study-observability/37-alloy-daemonset-dark.png)

`pyroscope.ebpf`는 애플리케이션 코드 계측 없이 커널 레벨에서 CPU 프로파일을 샘플링하므로, 언어·런타임에 무관하게 클러스터 전역 프로파일 커버리지를 확보할 수 있다는 장점이 있다. 다만 eBPF는 커널 버전·권한(`privileged` 또는 특정 capability) 제약이 있어, DaemonSet에 `securityContext`로 필요한 권한을 명시적으로 부여해야 한다. Alloy 컴포넌트 문법과 파이프라인 설계 일반론은 별도 챕터에서 더 깊게 다룬다.

## 5. Grafana Operator와 대시보드 프로비저닝

kube-prometheus-stack의 Grafana 서브차트는 `dashboardProviders`로 ConfigMap 기반 대시보드를 붙일 수 있지만, 대시보드 CR 자체를 선언적으로 관리하고 싶다면 별도의 [Grafana Operator](https://grafana.github.io/grafana-operator/)를 쓴다. Grafana Operator는 `Grafana`, `GrafanaDashboard`, `GrafanaDataSource`, `GrafanaFolder` 같은 CRD를 제공해, 대시보드 JSON을 Git 저장소에 두고 GitOps 파이프라인(ArgoCD/Flux)으로 자동 반영할 수 있게 만든다.

```yaml
apiVersion: grafana.integreatly.org/v1beta1
kind: GrafanaDashboard
metadata:
  name: order-service-overview
  namespace: monitoring
spec:
  instanceSelector:
    matchLabels:
      dashboards: "grafana"
  folder: "Services"
  json: |
    {
      "title": "Order Service Overview",
      "panels": [ ... ]
    }
```

```yaml
apiVersion: grafana.integreatly.org/v1beta1
kind: GrafanaDataSource
metadata:
  name: prometheus
  namespace: monitoring
spec:
  instanceSelector:
    matchLabels:
      dashboards: "grafana"
  datasource:
    name: Prometheus
    type: prometheus
    url: http://kube-prometheus-stack-prometheus.monitoring.svc:9090
    isDefault: true
```

`GrafanaDashboard` CR을 배포 파이프라인의 매니페스트 일부로 커밋하면, 애플리케이션 배포와 대시보드 배포가 같은 리뷰·승인 흐름을 탄다. 대시보드를 Grafana UI에서 수동으로 수정하고 잊어버리는 "드리프트" 문제를 근본적으로 없애는 방식이며, [대시보드 as-code](/study/observability/33-dashboard-as-code)에서 다룬 jsonnet/grafonnet 워크플로와 결합하면 대시보드 소스 자체도 코드로 생성해 CR에 주입할 수 있다.

## 6. 리소스·스토리지 사이징과 운영 팁

Prometheus 리소스 요구량은 시계열 개수와 스크레이프 주기에 선형으로 비례한다. 대략적인 산정 공식은 다음과 같다.

```text
메모리(대략) ≈ 시계열 수 × 스크레이프당 샘플 크기(약 2~3KB, head block 기준) × 1.5(오버헤드)
디스크(대략) ≈ 시계열 수 × 샘플 수/초 × 압축 후 바이트(약 1~2바이트) × 보존 기간(초)
```

| 규모 | 활성 시계열 | 권장 메모리 | 권장 CPU | 스토리지(15일 보존 기준) |
|---|---|---|---|---|
| 소규모 클러스터 | ~50만 | 4~8Gi | 1~2 core | 20~50Gi |
| 중규모 클러스터 | ~200만 | 16~32Gi | 4 core | 100~200Gi |
| 대규모 클러스터 | 500만+ | 64Gi+ | 8 core+ | 샤딩 또는 [Mimir 장기 저장](/study/observability/35-mimir-longterm-storage)로 오프로드 권장 |

단일 Prometheus 인스턴스가 처리 가능한 시계열 수는 결국 메모리 한계에 부딪힌다. 이 한계를 넘어서면 두 가지 선택지가 있다. 하나는 기능/팀 축으로 Prometheus를 샤딩해 인스턴스를 늘리는 것이고, 다른 하나는 `remote_write`로 Mimir에 넘겨 로컬 TSDB는 짧은 보존 기간(수 시간~수 일)만 유지하는 것이다. 실무에서는 후자가 압도적으로 많이 쓰인다 — 로컬 Prometheus는 최근 데이터의 빠른 질의와 룰 평가만 담당하고, 장기 보존과 대규모 질의는 Mimir가 맡는 역할 분리다.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: main
spec:
  retention: 6h              # 로컬은 짧게, 장기 보존은 remote_write 대상에 위임
  retentionSize: 40GiB
  storage:
    volumeClaimTemplate:
      spec:
        storageClassName: fast-ssd
        resources:
          requests:
            storage: 50Gi
  resources:
    requests: { cpu: "2", memory: 16Gi }
    limits: { memory: 20Gi }
```

::: tip 운영 팁
- <strong>StorageClass는 반드시 SSD 계열</strong>을 쓴다. TSDB는 WAL·compaction으로 랜덤 I/O가 잦아, 네트워크 스토리지나 HDD 기반 StorageClass는 compaction 지연과 스크레이프 실패를 유발한다.
- <strong>`retentionSize`를 `storage` 요청량보다 여유 있게 낮춰</strong> 잡는다. 디스크가 꽉 차기 직전에 compaction이 실패하면 Prometheus가 크래시 루프에 빠질 수 있다.
- <strong>limits.memory는 requests보다 과도하게 높이지 않는다.</strong> OOM Kill이 나더라도 예측 가능한 지점에서 나야 디버깅이 쉽다. 무제한에 가까운 limit은 노드 전체의 메모리 압박으로 번진다.
- Alloy DaemonSet은 노드당 리소스이므로, `resources.requests`를 노드 크기 대비 과소 설정하면 노드 스케줄링 여유가 갑자기 줄어든다. 노드풀 크기 변경 시 재계산이 필요하다.
:::

::: tip 핵심 정리
- kube-prometheus-stack은 Prometheus Operator·Prometheus·Alertmanager·Grafana·kube-state-metrics·node-exporter를 한 번에 배포하는 표준 Helm 차트다.
- Prometheus Operator는 Prometheus/ServiceMonitor/PodMonitor/PrometheusRule/Alertmanager CRD를 watch해 실제 설정 파일과 StatefulSet을 조정한다.
- ServiceMonitor는 Service 경유, PodMonitor는 Pod 직접 대상이며, selector 라벨이 CR 간 매칭의 경계선이다.
- Alloy는 DaemonSet으로 배포해 노드별 로그·eBPF 프로파일을 능동적으로 수집해 Loki·Pyroscope로 push한다.
- Grafana Operator의 GrafanaDashboard/GrafanaDataSource CRD로 대시보드를 GitOps 파이프라인에 편입시킬 수 있다.
- Prometheus 리소스는 시계열 수에 선형 비례하며, 대규모에서는 로컬 보존을 짧게 두고 Mimir로 오프로드하는 구성이 표준이다.
:::

## 다음 챕터

배포가 끝났다고 관측성 스택이 저절로 안정적으로 굴러가지는 않는다. 다음 챕터 [프로덕션 운영과 트러블슈팅](/study/observability/38-production-troubleshooting)에서는 Prometheus OOM·고카디널리티 대응, 스크레이프 실패 디버깅, remote_write 큐 폭증, Loki/Tempo 수집 병목, 쿼리 성능 튜닝, 그리고 운영 체크리스트까지 실전 트러블슈팅을 다룬다.
