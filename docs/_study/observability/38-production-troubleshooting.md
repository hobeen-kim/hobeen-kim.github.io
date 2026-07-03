---
title: "프로덕션 운영과 트러블슈팅"
description: "Prometheus OOM과 고카디널리티 대응, 스크레이프 실패·타깃 down 디버깅, remote_write 지연·큐 폭증, Loki/Tempo 수집 병목, 쿼리 성능·타임아웃 튜닝, 그리고 운영 체크리스트까지 관측성 스택을 실제로 운영하며 마주치는 장애 대응 실전을 다룬다."
date: 2026-07-02
tags: [Troubleshooting, SRE, Operations]
prev: /study/observability/37-kubernetes-deployment
next: /study/observability/39-beyla-autoinstrumentation
---

# 프로덕션 운영과 트러블슈팅

::: info 학습 목표
- Prometheus OOM의 근본 원인을 고카디널리티와 연결해 진단하고 즉각 조치·근본 조치를 구분한다.
- `up`, `scrape_duration_seconds` 등을 이용해 스크레이프 실패와 타깃 down을 체계적으로 디버깅한다.
- `prometheus_remote_storage_*` 메트릭으로 remote_write 지연과 큐 폭증을 탐지·완화한다.
- Loki/Tempo의 rate limit·ingester 포화로 인한 수집 병목을 식별하고 대응한다.
- PromQL/LogQL/TraceQL 쿼리 성능 저하와 타임아웃을 튜닝하는 방법을 익힌다.
- 프로덕션 운영 체크리스트와 프로파일링 오버헤드 점검 항목을 정리한다.
:::

## 1. Prometheus OOM·고카디널리티 대응

Prometheus OOM은 거의 항상 같은 뿌리에서 나온다. 메모리의 대부분은 head block(최근 2시간치 미압축 시계열)이 차지하는데, 시계열 수가 급증하면 head block이 그만큼 커진다. 배포 직후 라벨에 Pod 이름·요청 ID·타임스탬프 같은 고유값이 섞여 들어가면 시계열이 기하급수적으로 늘어나고, 결국 `process_resident_memory_bytes`가 컨테이너 limit을 넘어 OOM Kill로 이어진다.

진단은 `prometheus_tsdb_head_series`(현재 활성 시계열 수)와 `scrape_samples_scraped`(타깃별 샘플 수)부터 확인한다. 어떤 job/메트릭이 폭증을 일으켰는지는 `topk`로 좁힌다.

```promql
# 활성 시계열 상위 job
topk(10, count by (job) ({__name__=~".+"}))

# 특정 메트릭 이름의 라벨 조합 폭증 여부
topk(10, count by (__name__) ({__name__=~".+"}))

# 메모리 증가 추세
process_resident_memory_bytes{job="prometheus"}
```

즉각 조치는 문제 라벨을 `metricRelabelings`의 `action: drop` 또는 `labeldrop`으로 스크레이프 단계에서 잘라내는 것이다. 근본 조치는 애플리케이션 계측 코드에서 고유값 라벨 자체를 없애는 것이다 — Prometheus 쪽 완화는 항상 임시방편이라는 점을 인지해야 한다. 카디널리티 폭발의 근본 원인·탐지·차단 전략은 [카디널리티 관리와 비용](/study/observability/34-cardinality-cost)에서 이미 다뤘으므로, 여기서는 "이미 터진 상황"을 빠르게 수습하는 순서에 집중한다.

![Prometheus OOM Kill 진단 흐름 — head_series 추세 확인 후 급증이면 topk로 원인을 좁혀 즉각 조치(metricRelabelings drop)·재시작 후 근본 조치(계측 코드 라벨 제거)·재발 방지(sample_limit/label_limit), 완만하면 단순 리소스 증설](/images/study-observability/38-oom-flow.png)

`sample_limit`(스크레이프당 최대 샘플 수)과 `label_limit`(메트릭당 최대 라벨 수)을 ServiceMonitor/PodMonitor에 미리 걸어두면, 특정 타깃 하나의 폭주가 Prometheus 전체를 끌고 내려가는 사고를 막을 수 있다.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: order-service
spec:
  endpoints:
  - port: metrics
    sampleLimit: 20000     # 초과 시 해당 스크레이프 전체를 실패 처리
    labelLimit: 30
    labelNameLengthLimit: 200
    labelValueLengthLimit: 200
```

## 2. 스크레이프 실패·타깃 down 디버깅

가장 먼저 확인할 신호는 `up`이다. `up == 0`이면 Prometheus가 마지막 스크레이프에서 타깃에 도달하지 못했다는 뜻이고, 원인은 대부분 네트워크·인증·타임아웃 셋 중 하나다.

```promql
# 현재 down 상태인 타깃
up == 0

# 스크레이프는 성공하지만 점점 느려지는 타깃 (타임아웃 임박 신호)
scrape_duration_seconds > 5

# 스크레이프 제한에 걸려 샘플이 잘린 타깃
scrape_samples_scraped > 0 and prometheus_target_scrapes_exceeded_sample_limit_total > 0
```

![up==0 스크레이프 실패 디버깅 경로 — Grafana Targets에서 타깃이 목록에 보이는지부터 나눠, 목록에 없으면 ServiceMonitor selector 라벨 매칭을 확인하고, 에러 메시지가 있으면 유형(connection refused·context deadline exceeded·x509·403/401)별로 조치한 뒤 다음 scrape_interval 대기](/images/study-observability/38-scrape-debug.png)

흔히 놓치는 지점은 ServiceMonitor의 `selector.matchLabels`가 실제 Service 라벨과 미묘하게 다른 경우다(오타, 대소문자, 릴리스 라벨 누락). Prometheus UI의 Status → Targets가 아니라 Status → Service Discovery 화면에서 "Discovered Labels"까지 내려가면, relabel 단계에서 어떤 라벨 매칭이 실패해 타깃이 아예 drop됐는지 확인할 수 있다. `up == 0`인데 타깃이 Targets 화면에 보이는 경우와, 애초에 타깃 목록에 없는 경우는 원인이 완전히 다르므로 이 둘을 먼저 구분해야 한다.

## 3. remote_write 지연·큐 폭증

`remote_write`는 로컬 head block에서 샘플을 읽어 원격 저장소(Mimir 등)로 비동기 전송하는 큐 기반 파이프라인이다. 원격 저장소가 느려지거나 네트워크가 불안정해지면 큐가 쌓이고, 결국 로컬 메모리 압박(전송 대기 샘플이 메모리에 머무름)으로 번진다.

![remote_write 큐 기반 비동기 전송 시퀀스 — WAL이 큐에 샘플을 append하고 샤드가 원격 저장소로 배치 전송하다가, 원격 저장소 지연으로 5xx/timeout이 나면 지수 백오프 재시도로 큐가 적체(samples_pending 증가)되고 결국 WAL 삭제 지연·디스크 압박으로 전파](/images/study-observability/38-remote-write.png)

핵심 지표는 세 가지다.

```promql
# 전송 대기 중인 샘플 수 (계속 증가하면 원격 저장소가 처리 속도를 못 따라감)
prometheus_remote_storage_samples_pending

# 전송 실패 샘플 (재시도로 흡수되지 않는 영구 실패)
rate(prometheus_remote_storage_samples_failed_total[5m])

# 전송 지연(초): 로컬에서 가장 최신 샘플의 타임스탬프와
# 실제로 원격에 전달 완료된 최신 타임스탬프의 차이
(
  prometheus_remote_storage_highest_timestamp_in_seconds
  - prometheus_remote_storage_queue_highest_sent_timestamp_seconds
)
```

지연이 계속 커지면 우선 `queue_config`의 샤드 상한을 조정해 병렬 전송량을 늘릴 수 있는지 확인한다. 다만 샤드를 무한정 늘리는 것은 원격 저장소 쪽 수신 용량이 받쳐줄 때만 유효하다 — 원격 저장소가 이미 포화 상태라면 샤드를 늘려도 5xx만 늘어난다.

```yaml
remote_write:
- url: "https://mimir.example.com/api/v1/push"
  queue_config:
    capacity: 10000          # 샤드당 큐 용량
    max_shards: 50           # 최대 병렬 전송 샤드 수
    min_shards: 4
    max_samples_per_send: 2000
    batch_send_deadline: 5s
    min_backoff: 30ms
    max_backoff: 5s
```

`prometheus_remote_storage_samples_failed_total`이 5xx 응답과 함께 증가한다면 원격 저장소(Mimir distributor/ingester)의 수신 한도(`-distributor.ingestion-rate-limit`)에 걸렸을 가능성이 크다. 이 경우 Prometheus 쪽 튜닝이 아니라 수신 측 한도 조정이나 테넌트 분리가 근본 해법이다.

## 4. Loki/Tempo 수집 병목

Loki와 Tempo는 구조가 비슷해 병목 패턴도 유사하다. 둘 다 <strong>distributor</strong>가 들어오는 쓰기를 받아 <strong>ingester</strong>로 라우팅하는데, ingester는 메모리에 최근 데이터를 들고 있다가 주기적으로 오브젝트 스토리지에 flush한다. 이 flush 속도보다 유입 속도가 빠르면 ingester 메모리가 포화되고, 결국 distributor가 요청을 거부(429)하기 시작한다.

Loki는 테넌트별 rate limit을 `limits_config`로 강제한다.

```yaml
limits_config:
  ingestion_rate_mb: 10          # 초당 인제스트 허용량(MB)
  ingestion_burst_size_mb: 20
  max_streams_per_user: 10000    # 테넌트당 활성 스트림 상한
  max_line_size: 256000
```

한도를 초과하면 클라이언트는 429를 받고, Loki 쪽에서는 `loki_discarded_samples_total{reason=...}`로 원인이 남는다.

```logql
# 어떤 이유로 로그가 버려지고 있는지 (rate_limited, stream_limit, line_too_long 등)
sum by (reason) (rate(loki_discarded_samples_total[5m]))
```

대응은 두 갈래다. 실제로 로그량이 정상적으로 늘어난 것이라면 `ingestion_rate_mb`와 ingester 리소스를 같이 올려야 하고, 특정 애플리케이션의 라벨 설계 실수(예: 요청마다 바뀌는 라벨로 스트림이 무한히 늘어나는 경우)라면 `max_streams_per_user`에 걸리는 즉시 라벨 설계부터 고쳐야 한다. 스트림 카디널리티 문제를 리밋 완화로만 덮으면 ingester 메모리가 결국 다시 포화된다.

Tempo도 동일한 축을 가진다. `overrides`의 `ingestion_rate_limit_bytes`/`ingestion_burst_size_bytes`로 테넌트별 수집 한도를 걸고, `tempo_discarded_spans_total`로 거부된 스팬을 추적한다. ingester 포화는 `tempo_ingester_live_traces`(현재 메모리에 들고 있는 트레이스 수)가 계속 우상향하는 패턴으로 먼저 나타난다.

![Loki/Tempo 수집 병목 구조 — 클라이언트 쓰기를 Distributor가 받아 한도 이내면 Ingester 메모리 버퍼로 라우팅하고 주기적으로 오브젝트 스토리지에 flush, 한도 초과면 429 응답과 discarded 카운터 증가, flush보다 유입이 빠르면 ingester 메모리가 포화돼 OOM 위험](/images/study-observability/38-loki-tempo-bottleneck.png)

## 5. 쿼리 성능·타임아웃 튜닝

세 언어 모두 "얼마나 많은 원시 데이터를 훑는가"가 성능을 좌우한다. PromQL은 시계열 수 × 스텝 수, LogQL은 스캔해야 하는 청크 바이트, TraceQL은 스캔 대상 블록 수가 각각의 비용 축이다.

<strong>PromQL</strong>: 넓은 range와 고카디널리티 셀렉터를 함께 쓰면 `--query.max-samples`(기본 5천만) 한도에 걸려 쿼리가 거부된다. 대시보드에서 자주 도는 무거운 표현식은 [Recording Rule](/study/observability/11-recording-alerting-rules)로 사전 계산해 질의 시점 비용을 낮춘다.

```yaml
# prometheus 실행 플래그
--query.timeout=2m
--query.max-concurrency=20
--query.max-samples=50000000
```

<strong>LogQL</strong>: 라벨 필터를 먼저 좁히지 않고 파이프라인 필터(`|= "text"`)부터 넓은 시간 범위에 돌리면 querier가 대량의 청크를 순차 스캔한다. 쿼리 병렬화(`split_queries_by_interval`)와 querier 레플리카 수를 늘려 시간 구간별 분산 처리량을 확보한다.

```yaml
# loki 쿼리 프론트엔드 설정
query_range:
  split_queries_by_interval: 15m   # 긴 range 쿼리를 구간 단위로 쪼개 병렬 처리
  align_queries_with_step: true
  cache_results: true
```

```logql
# 나쁜 예: 넓은 range에서 라벨 없이 전체 스캔
{cluster="prod"} |= "timeout"

# 좋은 예: 라벨로 먼저 좁힌 뒤 필터
{cluster="prod", namespace="checkout", app="order-service"} |= "timeout"
```

<strong>TraceQL</strong>: 트레이스 ID로 직접 조회하면 블록 인덱스로 바로 찾아가지만, 속성 조건 검색(`{ span.http.status_code = 500 }`)은 시간 범위 내 블록을 훑어야 한다. 조회 시간 범위를 최소화하고, 자주 쓰는 조건은 [span metrics](/study/observability/23-traceql-spanmetrics)로 미리 메트릭화해 TraceQL 스캔 없이 PromQL로 대체하는 것이 근본적인 성능 해법이다.

## 6. 운영 체크리스트와 프로파일 오버헤드 점검

::: details 프로덕션 운영 체크리스트
- [ ] `up == 0`, `scrape_duration_seconds` 임계치 초과에 대한 알림이 구성돼 있다.
- [ ] `prometheus_tsdb_head_series` 추세 대시보드와 카디널리티 예산(팀별/서비스별) 상한 알림이 있다.
- [ ] `prometheus_remote_storage_samples_pending`, 전송 지연 지표에 대한 알림이 있다.
- [ ] Loki/Tempo의 `discarded` 계열 카운터가 대시보드에 노출돼 있다.
- [ ] TSDB `retentionSize`가 실제 PVC 용량보다 여유 있게 낮게 설정돼 있다.
- [ ] ServiceMonitor/PodMonitor에 `sampleLimit`/`labelLimit`이 기본값으로 강제돼 있다.
- [ ] 자주 쓰는 무거운 PromQL/LogQL이 Recording Rule/사전 집계로 전환돼 있다.
- [ ] Grafana 대시보드가 코드(as-code)로 버전 관리되고 있다.
- [ ] 알림 규칙마다 runbook 링크가 annotation으로 달려 있다.
:::

프로파일링은 다른 신호와 달리 <strong>수집 자체가 대상 워크로드의 CPU를 소비</strong>한다는 특성이 있다. eBPF 기반 연속 프로파일링은 보통 샘플링 주파수 100Hz 기준 CPU 오버헤드가 수 퍼센트 이내로 설계돼 있지만, 샘플링 주파수를 무분별하게 올리거나 대상 프로세스 수가 많은 노드에서는 누적 오버헤드가 무시할 수 없는 수준이 된다.

```promql
# Alloy pyroscope.ebpf 컴포넌트 자체의 리소스 사용량 추이
rate(container_cpu_usage_seconds_total{pod=~"alloy-.*"}[5m])
```

프로파일링 오버헤드가 의심되면 샘플링 주파수를 낮추거나(`sample_rate` 조정), eBPF 대신 애플리케이션 계측 기반 프로파일링으로 대상 워크로드를 좁히는 것을 우선 검토한다. 관측성 도구가 관측 대상의 성능에 영향을 주는 순간, 그 도구는 더 이상 "관측만" 하는 것이 아니라는 점을 항상 염두에 둬야 한다.

::: tip 핵심 정리
- Prometheus OOM은 고카디널리티가 근본 원인인 경우가 대부분이며, `sample_limit`/`label_limit`으로 재발을 막는다.
- `up == 0`은 네트워크·인증·타임아웃 세 갈래로 원인을 나눠 디버깅하고, Service Discovery 화면에서 relabel 실패 여부를 먼저 구분한다.
- `prometheus_remote_storage_samples_pending`과 전송 지연이 커지면 샤드 확장보다 원격 저장소 수신 한도를 먼저 의심한다.
- Loki/Tempo의 429·discarded 카운터는 실제 트래픽 증가와 라벨/스트림 설계 실수를 구분해서 대응해야 한다.
- PromQL/LogQL/TraceQL 모두 "스캔량을 줄이는 것"이 성능 튜닝의 본질이며, Recording Rule과 span metrics가 근본 해법이다.
- 프로파일링은 수집 자체가 오버헤드를 유발하므로 샘플링 주파수와 대상 범위를 지속적으로 점검해야 한다.
:::

## 다음 챕터

여기까지 LGTM 스택 본체의 기초부터 운영 심화까지를 다뤘다. 남은 것은 스택의 경계 바깥이다 — SDK를 넣을 수 없는 워크로드, 사용자의 브라우저, 트래픽이 없는 시간대. [Beyla — eBPF 자동 계측](/study/observability/39-beyla-autoinstrumentation)부터 이어지는 생태계 확장 챕터에서 이 사각지대들을 하나씩 메운다.
