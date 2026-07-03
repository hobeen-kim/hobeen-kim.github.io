---
title: "TSDB와 remote_write"
description: "Prometheus 로컬 TSDB의 head block·WAL·chunk·mmap·block 구조와 compaction, retention의 한계를 짚고, WAL 기반 전송과 큐·샤드·재시도·백프레셔로 동작하는 remote_write 프로토콜, remote_read, 그리고 queue_config 튜닝을 상세히 다룬다."
date: 2026-07-02
tags: [Observability, Prometheus, TSDB, RemoteWrite]
prev: /study/observability/11-recording-alerting-rules
next: /study/observability/13-alertmanager-architecture
---

# TSDB와 remote_write

::: info 학습 목표
- head block·WAL·chunk·mmap·block로 이어지는 로컬 TSDB의 저장 구조를 이해한다.
- compaction이 2시간 블록을 어떻게 병합하고, 인덱스가 무엇을 위한 구조인지 파악한다.
- retention과 로컬 저장만으로는 한계가 있는 이유를 정리한다.
- WAL 기반 전송, 큐·샤드, 재시도·백프레셔로 구성된 remote_write 프로토콜의 동작을 상세히 이해한다.
- remote_read의 용도와 remote_write와의 차이를 안다.
- `queue_config` 튜닝 포인트와 Mimir로의 장기 저장 연동을 파악한다.
:::

## 1. TSDB 구조 — head block, WAL, chunks, mmap, blocks

Prometheus의 로컬 TSDB는 최근 데이터를 메모리 중심으로, 오래된 데이터를 디스크의 불변 블록으로 관리하는 구조다.

<strong>Head block</strong>은 현재 시각 기준 가장 최근 데이터(기본 2시간 범위)를 담는 메모리 상의 쓰기 가능한 블록이다. 모든 스크레이프 결과는 먼저 head block에 append된다.

<strong>WAL(Write-Ahead Log)</strong>은 head block에 쓰이는 모든 샘플을 디스크에 순차 기록하는 로그다. Prometheus가 비정상 종료돼도 재시작 시 WAL을 재생(replay)해서 head block의 메모리 상태를 복구할 수 있다. head block 자체는 메모리에만 있으므로 WAL이 없으면 크래시 시 최근 데이터가 전부 유실된다.

<strong>Chunk</strong>는 시계열별로 샘플을 압축해서 묶은 단위다(Gorilla 압축 계열 알고리즘 기반). head block 안의 chunk는 일정 크기가 차면 <strong>mmap</strong>(memory-mapped file)으로 디스크에 매핑돼, 전체를 메모리에 올리지 않고도 OS 페이지 캐시를 통해 접근할 수 있게 된다. 이 덕분에 head block이 커져도 프로세스 메모리 사용량이 선형으로 폭증하지 않는다.

<strong>Block</strong>은 head block이 일정 시간(기본 2시간) 범위를 다 채우면 디스크에 flush되어 만들어지는 <strong>불변(immutable)</strong> 디렉터리다. 블록 안에는 chunk 파일들과, 시계열을 라벨로 빠르게 찾기 위한 <strong>index</strong> 파일(라벨 → 시계열 ID 역인덱스), 메타데이터가 함께 들어간다.

![스크레이프 샘플이 WAL과 head block에 append되고, head block이 mmap chunk와 불변 block으로 이어지며 WAL replay로 복구되는 로컬 TSDB 쓰기 경로](/images/study-observability/12-tsdb-write-path.png)

## 2. 압축과 블록 — compaction, 2시간 블록, index

새로 flush된 블록은 처음엔 2시간 범위 하나짜리다. <strong>Compaction</strong>은 인접한 여러 블록을 더 큰 시간 범위로 병합하는 백그라운드 작업으로, 기본적으로 2h → 여러 개를 묶어 더 긴 범위(예: 수십 시간~수일 단위)로 단계적으로 합쳐 나간다. compaction의 목적은 두 가지다. 블록 개수를 줄여 쿼리가 열어야 할 파일 수를 줄이는 것, 그리고 삭제 표시(tombstone)된 데이터나 중복 데이터를 실제로 걷어내 디스크를 회수하는 것이다.

<strong>Index</strong>는 각 블록 안에서 라벨 매처를 시계열 ID 목록으로 빠르게 바꾸기 위한 역인덱스(inverted index)다. `{job="api", status_code="500"}` 같은 쿼리가 들어오면, Prometheus는 인덱스에서 `job=api`를 만족하는 시계열 ID 집합과 `status_code=500`을 만족하는 시계열 ID 집합을 각각 찾아 교집합을 구한 뒤, 그 ID들에 해당하는 chunk만 읽는다. 라벨 카디널리티가 높을수록 인덱스 자체의 크기와 조회 비용이 커지는 것이 카디널리티 문제의 근본 원인 중 하나다.

![PromQL 쿼리가 index 역인덱스에서 라벨별 시계열 ID 집합의 교집합을 구해 해당 ID의 chunk만 읽는 조회 경로](/images/study-observability/12-query-index.png)

## 3. Retention과 로컬 저장의 한계

Prometheus는 `--storage.tsdb.retention.time`(기본 15일)과 `--storage.tsdb.retention.size`로 로컬에 보관할 데이터 범위를 제한한다. 두 조건 중 먼저 도달하는 쪽이 오래된 블록을 삭제한다.

로컬 TSDB만으로는 다음 한계에 부딪힌다.

- <strong>장기 보관 불가.</strong> 몇 주 이상의 추이 분석, 연간 비교, 규정 준수를 위한 장기 보관이 로컬 디스크 용량에 그대로 종속된다.
- <strong>단일 노드 한계.</strong> 로컬 TSDB는 수평 확장이 안 된다. 하나의 Prometheus 프로세스가 감당할 수 있는 시계열 수·쿼리 부하에 물리적 한계가 있다.
- <strong>고가용성 부재.</strong> 인스턴스가 죽으면 그 인스턴스가 갖고 있던 최근 미압축 데이터(head block)까지 함께 위험해진다. HA 페어를 둬도 각자 독립된 로컬 저장소를 가질 뿐 데이터가 공유되지 않는다.
- <strong>글로벌 뷰 부재.</strong> 여러 Prometheus 인스턴스(리전별, 클러스터별)의 데이터를 하나의 쿼리로 묶어보기 어렵다.

이 한계를 넘기 위한 표준 해법이 <strong>`remote_write`</strong>로 데이터를 중앙 장기 저장소(Mimir, Thanos, Cortex 등)로 흘려보내는 아키텍처다.

## 4. remote_write 프로토콜

`remote_write`는 Prometheus가 로컬에 쓰는 것과 별도로, 같은 샘플을 원격 저장소로 지속적으로 전송하는 기능이다. 핵심은 <strong>전송 소스가 head block이 아니라 WAL이라는 점</strong>이다. Prometheus는 WAL을 실시간으로 tail하는 "WAL watcher"를 두고, 새 샘플이 WAL에 append되는 즉시 이를 읽어 전송 파이프라인에 넣는다. 이 방식 덕분에 프로세스가 재시작돼도 WAL에 남아있는 미전송 샘플을 다시 읽어 전송을 이어갈 수 있다 — 전송 상태(어디까지 보냈는지)는 WAL 세그먼트 오프셋 기반으로 추적된다.

![WAL watcher가 WAL을 tail해 샤드 큐에 분배하고, 큐가 배치 단위로 원격 저장소에 HTTP POST하며 성공 ACK·재시도·drop으로 분기하는 remote_write 전송 파이프라인 시퀀스](/images/study-observability/12-remote-write-seq.png)

전송은 여러 <strong>샤드(shard)</strong>로 병렬화된다. 각 샤드는 독립적인 큐를 갖고 배치 단위(`max_samples_per_send`)나 타임아웃(`batch_send_deadline`) 중 먼저 도달하는 조건에 맞춰 원격 엔드포인트로 HTTP 요청을 보낸다. 요청 본문은 Protobuf로 직렬화되고 snappy로 압축된다. 원격 저장소가 처리 속도를 못 따라가면 큐가 쌓이기 시작하고, Prometheus는 <strong>샤드 수를 동적으로 늘려(`max_shards` 한도까지)</strong> 처리량을 확보하려 한다.

<strong>재시도와 백프레셔.</strong> 원격 저장소가 `5xx`나 `429`(Too Many Requests)를 반환하면 재시도 가능한 오류로 간주해 지수 백오프(`min_backoff`~`max_backoff`)로 재전송한다. `429`에 대한 재시도 여부는 `retry_on_http_429`로 제어한다. 이 재시도 동안 큐가 계속 쌓이면 Prometheus는 신규 샘플의 큐 투입 속도를 늦추는 방식으로 <strong>백프레셔</strong>를 건다 — 즉 원격 저장소가 느리면 전송 파이프라인 전체가 느려지도록 설계되어, 무한정 큐가 커져 메모리를 고갈시키는 상황을 막는다. 반대로 재시도 불가능한 `4xx`(429 제외, 예: `400 Bad Request`)는 즉시 샘플을 버리고 `prometheus_remote_storage_samples_dropped_total` 같은 메트릭으로 집계한다.

```yaml
remote_write:
  - url: "https://mimir.internal/api/v1/push"
    queue_config:
      capacity: 10000
      max_shards: 50
      min_shards: 1
      max_samples_per_send: 2000
      batch_send_deadline: 5s
      min_backoff: 30ms
      max_backoff: 5s
      retry_on_http_429: true
    metadata_config:
      send: true
      send_interval: 1m
```

## 5. remote_read

`remote_read`는 방향이 반대다. PromQL 쿼리 실행 시, 로컬 TSDB에 없는(예: retention이 지나 삭제된) 구간의 데이터를 remote_read 엔드포인트에서 읽어와 로컬 데이터와 병합해서 응답한다.

```yaml
remote_read:
  - url: "https://mimir.internal/prometheus/api/v1/read"
    read_recent: false
```

`read_recent: false`(기본값)면 로컬에 있는 최근 데이터는 로컬에서만 읽고, 로컬에 없는 과거 구간만 원격에서 채운다. `read_recent: true`로 두면 모든 쿼리가 원격 저장소도 함께 조회해 병합하므로 정확도는 올라가지만 쿼리 레이턴시가 늘어난다. 실무에서는 remote_read를 직접 켜서 Prometheus가 원격 데이터를 병합하게 하기보다, Mimir·Thanos의 querier가 자체적으로 여러 Prometheus의 블록과 장기 저장소를 통합 조회하는 아키텍처를 쓰는 경우가 많다. 이 경우 사용자는 Prometheus가 아니라 Mimir/Thanos의 쿼리 엔드포인트를 직접 바라본다.

## 6. remote_write 운영 튜닝과 Mimir 연결

`queue_config`의 주요 파라미터를 실제 운영 관점에서 정리하면 다음과 같다.

| 파라미터 | 역할 | 튜닝 방향 |
|---|---|---|
| `capacity` | 샤드별 큐가 버퍼링할 최대 샘플 수 | 원격 저장소 순간 지연을 흡수할 만큼 여유 있게 |
| `max_shards` / `min_shards` | 병렬 전송 샤드 수 범위 | 처리량 부족 시 `max_shards` 상향, 과도한 커넥션 수 방지 위해 상한 필요 |
| `max_samples_per_send` | 배치 하나에 담을 샘플 수 | 크면 처리량↑ 지연↑, 작으면 반대 |
| `batch_send_deadline` | 배치가 안 차도 강제 전송하는 시간 | 너무 길면 신선도 저하, 너무 짧으면 배치 효율 저하 |
| `min_backoff` / `max_backoff` | 재시도 백오프 범위 | 원격 저장소 장애 시 폭주(retry storm) 방지 |
| `retry_on_http_429` | 429 응답 재시도 여부 | 원격 저장소가 유량 제어를 429로 표현하면 true 유지 |

튜닝의 실무 신호는 `prometheus_remote_storage_queue_highest_sent_timestamp_seconds`와 `prometheus_remote_storage_samples_pending`이다. pending이 계속 쌓이거나 전송 타임스탬프가 현재 시각보다 뒤처지기 시작하면 샤드가 부족하거나 원격 저장소 자체가 병목이라는 신호다. 이때는 `max_shards`를 올리기 전에 원격 저장소(Mimir) 쪽의 ingester 처리량부터 확인하는 것이 순서다.

![여러 Prometheus 인스턴스가 하나의 Mimir로 remote_write하고, Mimir가 오브젝트 스토리지에 장기 블록을 저장하며 Query Frontend를 통해 Grafana에 전역 쿼리를 제공하는 구조](/images/study-observability/12-mimir-fanout.png)

여러 Prometheus 인스턴스가 하나의 Mimir로 `remote_write`하면, Mimir가 수평 확장 가능한 저장·질의 계층을 제공해 로컬 TSDB의 단일 노드·짧은 retention 한계를 넘어선다. Mimir의 내부 아키텍처(distributor, ingester, compactor, 블록 스토리지 구조)는 [장기 저장 — Mimir](/study/observability/35-mimir-longterm-storage)에서 자세히 다룬다.

::: tip 핵심 정리
- 로컬 TSDB는 WAL(내구성) + head block(메모리, 최근 ~2h) + mmap chunk + 불변 block(디스크)으로 구성된다.
- compaction은 블록을 병합해 파일 수를 줄이고 삭제 데이터를 회수하며, index는 라벨 매처를 시계열 ID로 빠르게 바꾸는 역인덱스다.
- retention은 로컬 디스크 용량에 종속되고, 로컬 TSDB는 수평 확장·HA·글로벌 뷰를 제공하지 못한다.
- `remote_write`는 head block이 아니라 WAL을 tail해서 전송하므로 재시작에도 이어서 보낼 수 있고, 샤드 병렬 전송 + 지수 백오프 재시도 + 백프레셔로 원격 장애를 흡수한다.
- `remote_read`는 로컬에 없는 과거 데이터를 원격에서 병합 조회하는 용도지만, 실무에서는 Mimir/Thanos querier가 이 역할을 대체하는 경우가 많다.
- `queue_config`의 샤드·배치·백오프 파라미터를 pending 샘플 수와 전송 타임스탬프 지표로 관측하며 튜닝한다.
:::

## 다음 챕터

메트릭 수집·질의·저장까지 다뤘으니, 이제 발화된 알림이 실제로 사람에게 도달하는 경로를 볼 차례다. [Alertmanager 아키텍처](/study/observability/13-alertmanager-architecture)에서는 Alertmanager의 클러스터링과 gossip 프로토콜, 그리고 Prometheus가 발화한 알림이 그룹핑·라우팅되는 파이프라인을 다룬다.
