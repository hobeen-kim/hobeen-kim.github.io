---
title: "스크레이핑과 서비스 디스커버리"
description: "scrape_interval·staleness 같은 스크레이프 동작 원리부터 scrape_config 구조, kubernetes_sd를 비롯한 서비스 디스커버리, 그리고 relabeling으로 타깃과 라벨을 정교하게 통제하는 방법까지 다룬다."
date: 2026-07-02
tags: [Prometheus, ServiceDiscovery, Relabeling]
prev: /study/observability/06-data-model
next: /study/observability/08-exporters-instrumentation
---

# 스크레이핑과 서비스 디스커버리

::: info 학습 목표
- scrape_interval·scrape_timeout·staleness 등 스크레이프 동작의 실전 의미를 이해한다.
- scrape_config의 실제 구조와 주요 필드를 파악한다.
- kubernetes_sd·ec2_sd·consul_sd·file_sd 등 서비스 디스커버리 메커니즘의 차이를 안다.
- relabel_configs로 타깃을 필터링하고 `__meta_*` 라벨을 활용하는 방법을 실전 예제로 익힌다.
- metric_relabel_configs로 수집 후 카디널리티를 통제하고, honor_labels·target label·up 메트릭의 동작을 이해한다.
:::

## 1. 스크레이프 동작

각 타깃은 `scrape_interval`마다 독립적으로 스크레이프된다. <strong>전역적으로 동시에</strong> 당기는 것이 아니라, Prometheus는 타깃별로 해시 기반 오프셋을 계산해 스크레이프 시점을 고르게 분산시킨다. 수천 개 타깃이 한 프로세스에서 스크레이프 부하를 만들 때, 이 분산이 없으면 매 인터벌마다 CPU·네트워크 스파이크가 생긴다.

![스크레이프 동작과 up 메트릭 시퀀스 — scrape_interval 15초·scrape_timeout 10초 설정에서 t=0s 스크레이프 성공 시 up=1, t=15s 타임아웃(응답 없음)으로 up=0 기록, t=30s 복구로 다시 up=1이 되는 흐름](/images/study-observability/07-scrape-behavior.png)

- `scrape_timeout`은 반드시 `scrape_interval` 이하여야 한다. 타임아웃이 인터벌을 넘으면 스크레이프가 겹쳐 큐가 밀린다.
- 기본 스크레이프 경로는 `/metrics`이지만 `metrics_path`로 바꿀 수 있다.
- <strong>Staleness</strong>는 실무에서 자주 놓치는 부분이다. 어떤 시계열이 더 이상 스크레이프되지 않거나(타깃 다운, relabel로 제외) 애플리케이션이 특정 라벨 조합의 메트릭을 더는 노출하지 않으면, Prometheus는 그 시계열의 마지막 샘플 이후 <strong>기본 5분(staleness window)</strong>이 지난 시점에 내부적으로 "stale marker"(특수 NaN)를 찍는다. 이 마커 이후 해당 시계열은 쿼리에서 사라진다. 즉 사라진 Pod의 그래프가 영원히 마지막 값에 멈춰 있는 게 아니라, 5분 뒤 자연스럽게 no-data 처리된다 — alert 룰에서 "값이 없으면 알림 안 감" 같은 함정을 만들 수 있으므로 `absent()` 계열 함수와 함께 설계해야 한다.

## 2. scrape_config 구조

`prometheus.yml`의 `scrape_configs`는 job 단위 배열이다. 하나의 job은 보통 같은 종류의 타깃 집합을 가리킨다.

```yaml
scrape_configs:
  - job_name: "payment-api"
    scrape_interval: 15s
    scrape_timeout: 10s
    metrics_path: /actuator/prometheus
    scheme: https
    tls_config:
      ca_file: /etc/prometheus/certs/ca.pem
      insecure_skip_verify: false
    basic_auth:
      username: prom
      password_file: /etc/prometheus/secrets/scrape_password
    params:
      format: ["prometheus"]
    static_configs:
      - targets: ["payment-api-1:9100", "payment-api-2:9100"]
        labels:
          env: production
          team: payments
```

- `job_name`은 `job` 라벨 값으로 모든 샘플에 자동 부여된다.
- `static_configs`는 가장 단순한 타깃 소스로, 타깃 목록을 직접 나열한다. `labels`는 이 그룹의 모든 타깃에 공통으로 붙는 <strong>target label</strong>이다(6절 참고).
- `scheme: https`, `tls_config`, `basic_auth`, `params`는 실제 운영에서 인증서 검증이나 인증이 필요한 타깃에 흔히 쓰인다.
- 정적 타깃 대신 동적 타깃이 필요하면 `static_configs` 자리에 `kubernetes_sd_configs` 같은 SD 설정을 넣는다 — 다음 절에서 다룬다.

## 3. 서비스 디스커버리

컨테이너·VM이 끊임없이 뜨고 사라지는 환경에서 타깃 목록을 손으로 관리하는 것은 불가능하다. Prometheus는 다양한 SD 메커니즘을 지원해 이 목록을 자동으로 갱신한다.

![서비스 디스커버리 구조 — kubernetes_sd_configs(apiserver watch·__meta_kubernetes_*), ec2_sd_configs(AWS API·__meta_ec2_*), consul_sd_configs(Consul 카탈로그·__meta_consul_*), file_sd_configs(JSON/YAML 파일·GitOps) 네 SD 소스가 각각 타깃과 메타 라벨을 만들어 Discovery Manager로 공급하고, relabel 적용 후 Retrieval로 넘기는 흐름](/images/study-observability/07-service-discovery.png)

- <strong>kubernetes_sd_configs</strong>는 apiserver를 watch해서 `role: node | pod | service | endpoints | endpointslice | ingress` 단위로 타깃을 만든다. 클러스터 안에서 가장 널리 쓰이는 SD다. role마다 붙는 메타 라벨 집합이 다르다(예: `role: pod`는 `__meta_kubernetes_pod_*`, `role: endpoints`는 컨테이너 포트까지 포함).
- <strong>ec2_sd_configs</strong>는 AWS API로 리전 내 EC2 인스턴스 목록을 가져온다. 태그가 `__meta_ec2_tag_*` 메타 라벨로 노출돼 relabel의 원재료가 된다.
- <strong>consul_sd_configs</strong>는 Consul의 서비스 카탈로그를 조회한다. VM 기반 인프라에서 컨테이너 오케스트레이터 없이 서비스 레지스트리를 쓰는 조직에 적합하다.
- <strong>file_sd_configs</strong>는 로컬 JSON/YAML 파일을 주기적으로 다시 읽는다. 외부 시스템(CMDB, 사내 인벤토리, Terraform 출력)이 타깃 목록을 파일로 떨궈주는 GitOps 파이프라인과 잘 맞고, Prometheus가 직접 지원하지 않는 SD 소스를 우회하는 범용 탈출구이기도 하다.

```yaml
kubernetes_sd_configs:
  - role: pod
    namespaces:
      names: ["default", "payments"]
```

## 4. Relabeling — 타깃 통제의 핵심

<strong>relabel_configs</strong>는 SD가 만들어낸 타깃 목록에 대해, 실제 스크레이프가 일어나기 <strong>전</strong>에 라벨을 필터링·재작성하는 파이프라인이다. Prometheus 운영에서 가장 강력하면서도 가장 헷갈리는 부분이다.

![Relabeling 파이프라인 — SD가 만든 타깃(+__meta_* 라벨)이 relabel_config #1·#2·#N을 순차로 거쳐(source_labels → separator → regex → action) 최종 타깃(라벨+__address__ 확정)이 되고, drop된 타깃은 제외된 채 keep된 타깃만 스크레이프 실행되며, keep/drop·replace·labelmap·labeldrop/labelkeep·hashmod 액션과 __로 시작하는 라벨의 target_label 승격 원리를 함께 보여주는 그림](/images/study-observability/07-relabeling.png)

동작 순서는 항상 `source_labels`로 값을 뽑고 → `separator`로 이어붙이고 → `regex`로 매치하고 → `action`으로 keep/drop/replace 등을 실행한다. 자주 쓰는 action은 다음과 같다.

- `keep` — regex에 매치하는 타깃만 유지, 나머지는 버림
- `drop` — regex에 매치하는 타깃을 버림
- `replace`(기본값) — 매치 결과를 `target_label`에 기록
- `labelmap` — 정규식에 매치한 소스 라벨 이름들을 규칙에 따라 새 라벨명으로 복사
- `labeldrop` / `labelkeep` — 라벨 이름 자체를 기준으로 제거/유지
- `hashmod` — 값을 해시해 샤딩(다중 Prometheus 인스턴스 간 타깃 분할)에 사용

가장 흔한 실전 패턴 — 어노테이션으로 스크레이프 여부와 포트를 제어하는 kubernetes_sd 예제다.

```yaml
relabel_configs:
  # prometheus.io/scrape: "true" 어노테이션이 붙은 Pod만 유지
  - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
    action: keep
    regex: "true"

  # 어노테이션에 지정된 경로가 있으면 __metrics_path__ 덮어쓰기
  - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
    action: replace
    target_label: __metrics_path__
    regex: (.+)

  # 어노테이션에 지정된 포트로 __address__ 재작성
  - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
    action: replace
    target_label: __address__
    regex: ([^:]+)(?::\d+)?;(\d+)
    replacement: $1:$2

  # Pod의 namespace, pod name을 실제 라벨로 승격
  - source_labels: [__meta_kubernetes_namespace]
    action: replace
    target_label: namespace
  - source_labels: [__meta_kubernetes_pod_name]
    action: replace
    target_label: pod
```

`__meta_kubernetes_*`처럼 <strong>`__`로 시작하는 라벨은 relabel 단계에서만 보이고, 최종적으로 남지 않는다.</strong> 즉 이 예제의 4번째 규칙처럼 `target_label`로 명시적으로 복사하지 않으면 그 메타데이터는 스크레이프 이후 영영 사라진다. relabel_configs를 쓰는 이유의 8할은 이 임시 메타데이터를 영구 라벨로 "승격"시키는 데 있다.

## 5. metric_relabel_configs — 수집 후 카디널리티 통제

`relabel_configs`가 <strong>스크레이프 대상을 정하는 단계</strong>에서 동작한다면, `metric_relabel_configs`는 완전히 다른 시점 — <strong>스크레이프로 실제 샘플을 받아온 직후, TSDB에 쓰기 직전</strong>에 동작한다. 사용하는 문법과 action 종류는 relabel_configs와 동일하지만, 이번엔 `source_labels`에 `__name__`을 비롯해 실제 메트릭 라벨을 넣을 수 있다는 점이 다르다.

가장 흔한 용도는 카디널리티가 큰 메트릭을 <strong>수집 자체를 막아 저장 비용을 줄이는 것</strong>이다.

```yaml
metric_relabel_configs:
  # 특정 고카디널리티 메트릭 자체를 드롭
  - source_labels: [__name__]
    action: drop
    regex: "go_gc_duration_seconds.*"

  # 특정 라벨 값을 가진 샘플만 드롭 (예: 디버그 엔드포인트 노이즈)
  - source_labels: [__name__, path]
    separator: ";"
    action: drop
    regex: "http_requests_total;/debug/.*"

  # 불필요한 고카디널리티 라벨 자체를 제거 (시계열은 유지, 차원만 축소)
  - action: labeldrop
    regex: "pod_template_hash"
```

주의할 점은 `metric_relabel_configs`로 드롭해도 <strong>스크레이프 자체(네트워크 요청, 파싱)는 이미 끝난 뒤</strong>라는 것이다. 즉 스크레이프 부하 자체를 줄이려면 relabel_configs로 타깃/경로를 걸러야 하고, TSDB 저장 부담(디스크·메모리·카디널리티)만 줄이려면 metric_relabel_configs면 충분하다. 이 구분을 모르면 "메트릭을 drop했는데 왜 네트워크 부하가 그대로냐"는 혼란을 겪는다. 카디널리티 관리 전략은 [34장](/study/observability/34-cardinality-cost)에서 더 깊게 다룬다.

## 6. honor_labels·target label·up 메트릭

- <strong>honor_labels</strong>는 타깃이 노출한 라벨과 Prometheus가 붙이려는 라벨(주로 job/instance, 혹은 static_configs의 target label)이 충돌할 때의 우선순위를 정한다. 기본값 `honor_labels: false`에서는 <strong>Prometheus가 부여하는 라벨이 우선</strong>하고, 타깃이 노출한 동일 이름의 라벨은 `exported_<라벨명>`으로 이름이 바뀌어 보존된다. `honor_labels: true`로 켜면 반대로 <strong>타깃이 노출한 라벨이 그대로 유지</strong>된다. 대표적인 사용처가 federation이다 — 상위 Prometheus가 하위 Prometheus의 `/federate`를 스크레이프할 때, 원본 `job`/`instance`를 보존해야 어떤 하위 서버에서 왔는지 구분되므로 `honor_labels: true`를 쓴다.
- <strong>Target label</strong>은 `static_configs.labels`나 SD의 relabel 결과로 그 타깃 그룹 전체에 붙는 라벨이다(2절 예제의 `env: production`, `team: payments`). 메트릭 자체가 원래 갖고 있던 라벨이 아니라 스크레이프 설정 쪽에서 주입한다는 점에서 애플리케이션 라벨과 구분된다.
- <strong>`up` 메트릭</strong>은 Prometheus가 각 타깃마다 자동으로 만들어내는 합성 메트릭이다. 스크레이프가 성공하면 `1`, 실패(타임아웃·커넥션 실패·5xx 등)하면 `0`이다. 이와 함께 `scrape_duration_seconds`, `scrape_samples_scraped`, `scrape_samples_post_metric_relabeling` 같은 메타 메트릭도 자동 생성된다. `up == 0`은 가장 기본적이면서도 가장 중요한 알림 조건 중 하나다 — 애플리케이션 로직과 무관하게 "이 타깃에 대체 접근이 되는가"를 알려주기 때문이다.

```promql
# 5분 넘게 다운된 타깃 찾기
up == 0
```

::: tip 핵심 정리
- 타깃은 인터벌마다 독립적으로 분산 스크레이프되며, staleness window(기본 5분)가 지나야 사라진 시계열이 쿼리에서 실제로 없어진다.
- scrape_config는 job 단위로 경로·인증·타깃 소스를 정의하고, 정적 목록 대신 SD 설정을 꽂아 동적 타깃을 받는다.
- kubernetes_sd/ec2_sd/consul_sd/file_sd는 각각 다른 방식으로 타깃과 `__meta_*` 메타 라벨을 만들어낸다.
- relabel_configs는 스크레이프 전에 타깃을 필터링·재작성하는 파이프라인이고, `__meta_*` 라벨은 명시적으로 target_label로 승격하지 않으면 사라진다.
- metric_relabel_configs는 스크레이프 후 저장 전 단계에서 카디널리티를 통제하며, 네트워크 부하까지 줄이려면 relabel_configs 단계에서 걸러야 한다.
- honor_labels·target label·up 메트릭은 각각 라벨 충돌 우선순위, 스크레이프 설정 유래 라벨, 타깃 가용성 신호를 담당한다.
:::

## 다음 챕터

[Exporter와 애플리케이션 계측](/study/observability/08-exporters-instrumentation)에서는 node-exporter 같은 Exporter 패턴과 클라이언트 라이브러리를 이용한 직접 계측, 그리고 RED·USE 방법론으로 "무엇을 계측할 것인가"를 결정하는 방법을 다룬다.
