---
title: "읽기/쓰기 경로와 구성요소"
description: "Loki의 쓰기 경로(distributor→ingester→chunk→오브젝트 스토리지)와 읽기 경로(query-frontend→querier)를 구성하는 각 컴포넌트의 역할과 운영 포인트를 다룬다."
date: 2026-07-02
tags: [Loki, Logs, Architecture]
prev: /study/observability/16-loki-architecture
next: /study/observability/18-logql
---

# 읽기/쓰기 경로와 구성요소

::: info 학습 목표
- Loki 쓰기 경로가 distributor → ingester → chunk → 오브젝트 스토리지로 이어지는 전체 흐름을 설명할 수 있다.
- distributor의 해싱·검증·rate limit 책임과 ingester의 메모리 청크·WAL·flush 동작을 이해한다.
- 읽기 경로에서 query-frontend와 querier가 ingester(최신 데이터)와 스토리지(과거 데이터)를 어떻게 병합하는지 안다.
- query-frontend의 쿼리 분할·캐싱·병렬화 전략과 compactor의 TSDB 인덱스 관리 역할을 파악한다.
:::

## 1. 쓰기 경로 — distributor → ingester → chunk → 오브젝트 스토리지

로그 라인이 Loki에 도착하는 첫 관문은 <strong>distributor</strong>다. 클라이언트(Alloy, Promtail, Fluent Bit 등)가 gRPC 또는 HTTP(`/loki/api/v1/push`)로 로그 배치를 보내면, distributor가 검증·정규화한 뒤 라벨 집합을 해싱해 담당 <strong>ingester</strong>로 라우팅한다. ingester는 해당 스트림의 로그를 메모리 청크에 쌓다가, 일정 크기·시간 조건이 되면 청크를 압축해 오브젝트 스토리지로 flush한다.

![Loki 쓰기 경로 시퀀스 — 클라이언트가 distributor로 push하면 검증·라벨 해싱 후 ingester로 라우팅하고, ingester가 WAL 기록·메모리 청크 append 뒤 조건 충족 시 오브젝트 스토리지로 청크·인덱스를 flush](/images/study-observability/17-write-path.png)

## 2. Distributor — 해싱, 검증, rate limit

Distributor는 상태를 갖지 않는(stateless) 컴포넌트로, 수평 확장이 자유롭다. 핵심 책임은 세 가지다.

- <strong>검증</strong>: 타임스탬프 순서, 라벨 형식, 라인 크기 제한 등을 확인해 잘못된 데이터가 뒤 단계로 넘어가지 않게 막는다. out-of-order 로그(타임스탬프가 이전보다 과거로 튀는 경우)는 설정에 따라 거부되거나 허용된다.
- <strong>일관 해싱(consistent hashing)</strong>: 각 스트림의 라벨 집합을 해싱해 [ring](https://grafana.com/docs/loki/latest/get-started/architecture/#the-hash-ring)에서 담당 ingester를 결정한다. 복제 계수(`replication_factor`, 기본 3)만큼 여러 ingester에 동시에 쓴다.
- <strong>rate limit</strong>: 테넌트별 인제스트 속도(`ingestion_rate_mb`)와 버스트(`ingestion_burst_size_mb`)를 제한해 한 테넌트가 클러스터 전체를 압도하지 못하게 막는다. 한도를 넘으면 `429 Too Many Requests`로 거부한다.

```yaml
limits_config:
  ingestion_rate_mb: 16
  ingestion_burst_size_mb: 32
  max_streams_per_user: 10000
  max_line_size: 256000
```

## 3. Ingester — 메모리 청크, WAL, flush

Ingester는 Loki에서 가장 상태가 무거운 컴포넌트다. 각 스트림에 대해 <strong>메모리 청크(in-memory chunk)</strong>를 유지하며 도착하는 로그 라인을 순서대로 append한다. 청크가 다음 조건 중 하나를 만족하면 압축·직렬화해 오브젝트 스토리지로 flush한다.

- 청크 크기가 `chunk_target_size`(기본 약 1.5MB 압축 기준)에 도달
- 청크가 `max_chunk_age`(기본 2시간) 이상 열려 있음
- 스트림이 `chunk_idle_period` 동안 새 로그를 받지 못함(idle)

메모리에만 두면 ingester가 죽었을 때 데이터가 유실되므로, 모든 쓰기는 먼저 로컬 디스크의 <strong>WAL(Write-Ahead Log)</strong>에 기록된다. ingester가 재시작하면 WAL을 재생(replay)해 flush 전 상태를 복구한다. WAL이 없으면 재시작·롤링 업데이트마다 flush 안 된 최근 로그가 통째로 사라진다.

```yaml
ingester:
  wal:
    enabled: true
    dir: /loki/wal
    flush_on_shutdown: true
  chunk_idle_period: 30m
  chunk_target_size: 1572864
  max_chunk_age: 2h
```

::: warning ingester 롤링 업데이트는 신중히
ingester는 최근 미flush 데이터를 들고 있는 상태 저장 컴포넌트다. 여러 ingester를 동시에 재시작하면 복제 계수를 넘는 손실이 생길 수 있다. `flush_on_shutdown`을 켜고 롤링 업데이트 시 한 번에 하나씩만 내리는 전략이 안전하다.
:::

## 4. 읽기 경로 — query-frontend → querier → ingester + storage

읽기 요청은 <strong>query-frontend</strong>가 먼저 받는다. query-frontend는 쿼리를 분할·큐잉한 뒤 <strong>querier</strong>에게 나눠 보낸다. querier는 각 서브쿼리에 대해 두 곳을 동시에 조회한다.

- 아직 flush되지 않은 <strong>최신 데이터</strong>는 ingester에 직접 gRPC로 질의한다.
- flush돼 오브젝트 스토리지에 저장된 <strong>과거 데이터</strong>는 인덱스로 청크 위치를 찾은 뒤 스토리지에서 읽는다.

두 결과를 시간순으로 병합해 최종 결과를 만든다. 이 이중 조회 덕분에 방금 들어온 로그도 flush를 기다리지 않고 즉시 쿼리에 잡힌다.

![Loki 읽기 경로 — query-frontend가 쿼리를 분할·캐싱해 querier로 넘기고, querier가 ingester(미flush 최신)와 index·오브젝트 스토리지(과거 청크)를 동시 조회해 시간순 병합 후 사용자에게 반환](/images/study-observability/17-read-path.png)

## 5. Query-Frontend — 쿼리 분할, 캐싱, 병렬

Query-frontend는 querier 앞단에서 세 가지로 쿼리 성능을 끌어올린다.

- <strong>쿼리 분할(splitting)</strong>: 넓은 시간 범위 쿼리를 작은 시간 구간(기본 24시간 단위)으로 쪼개 여러 querier에 병렬로 분배한다. 예를 들어 7일치 쿼리는 7개의 하위 쿼리로 나뉘어 동시에 처리된다.
- <strong>캐싱</strong>: 이미 계산된 구간의 결과를 결과 캐시(results cache)에 저장해 같은 쿼리가 반복되거나 시간 범위가 겹칠 때 재계산을 피한다. 메트릭 쿼리는 구간별 캐시가 특히 잘 맞는다.
- <strong>병렬 실행</strong>: 분할된 서브쿼리를 큐에 쌓고 여러 querier 인스턴스가 동시에 소비하게 해 응답 시간을 단축한다.

```yaml
query_range:
  split_queries_by_interval: 24h
  align_queries_with_step: true
  cache_results: true
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 500
```

쿼리 분할은 [LogQL](/study/observability/18-logql)에서 다룰 라벨 매처가 얼마나 정밀한지에 따라 효과가 크게 갈린다 — 라벨로 스트림 수를 줄이지 못한 채 넓은 시간 범위를 조회하면, 분할·병렬화를 해도 querier가 훑어야 할 청크 총량 자체가 줄지 않는다.

## 6. Compactor와 인덱스 관리 — Loki TSDB Index

<strong>Compactor</strong>는 두 가지 백그라운드 작업을 담당하는 단일 인스턴스 컴포넌트다.

- <strong>인덱스 압축(compaction)</strong>: 각 ingester가 개별적으로 업로드한 작은 인덱스 파일들을 주기적으로 병합해 더 크고 효율적인 인덱스 파일로 만든다. 인덱스 파일 수가 계속 늘어나면 쿼리 시 열어야 할 파일 수가 늘어 조회 성능이 떨어지므로 압축이 필수다.
- <strong>보존 정책(retention) 적용</strong>: 테넌트별 `retention_period`를 넘긴 청크와 인덱스 항목을 오브젝트 스토리지에서 실제로 삭제한다.

최신 Loki는 인덱스 스토어로 [TSDB 포맷](https://grafana.com/docs/loki/latest/operations/storage/tsdb/)을 기본으로 쓴다. 과거의 `boltdb-shipper`보다 인덱스 조회가 빠르고 압축 효율이 높다. TSDB 인덱스는 시간 구간(period, 기본 24h)별로 파일이 나뉘며, ingester는 로컬에 만든 인덱스를 주기적으로 오브젝트 스토리지에 shipping하고 compactor가 이를 병합한다.

```yaml
compactor:
  working_directory: /loki/compactor
  compaction_interval: 10m
  retention_enabled: true
  delete_request_store: s3

limits_config:
  retention_period: 744h  # 31일
```

::: tip 핵심 정리
- 쓰기 경로는 distributor(해싱·검증·rate limit) → ingester(메모리 청크·WAL) → 오브젝트 스토리지(flush) 순으로 흐른다.
- distributor는 스테이트리스, ingester는 WAL을 갖는 상태 저장 컴포넌트라는 차이가 운영 방식을 가른다.
- 읽기 경로는 query-frontend가 쿼리를 분할·캐싱하고, querier가 ingester(최신)와 스토리지(과거)를 동시에 조회해 병합한다.
- query-frontend의 시간 구간 분할과 결과 캐싱이 대규모 시간 범위 쿼리의 체감 성능을 좌우한다.
- compactor는 단일 인스턴스로 인덱스 병합과 retention 삭제를 전담하며, 최신 Loki는 TSDB 인덱스 포맷을 쓴다.
:::

## 다음 챕터

컴포넌트 구조를 이해했다면, 이제 실제로 로그를 어떻게 질의하는지 볼 차례다. 다음 챕터 [LogQL](/study/observability/18-logql)에서는 로그 스트림 셀렉터, 라인 필터, 파서, 메트릭 쿼리와 성능 튜닝 원칙을 다룬다.
