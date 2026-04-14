---
title: "모니터링 지표"
description: "QPS, Latency p99, Connection Usage 등 핵심 DB 메트릭을 정의하고, Prometheus Exporter와 Grafana로 시각화·알림을 구성하는 방법을 학습한다."
date: 2026-04-14
tags: [DB최적화, 모니터링, Grafana, Prometheus, QPS]
prev: /study/db-optimization/09-migration
next: /study/db-optimization/11-postgresql
---

# 모니터링 지표

::: info 학습 목표
- DB 운영에서 반드시 추적해야 할 핵심 메트릭 5가지를 이해한다.
- Prometheus Exporter를 설치하고 메트릭을 수집하는 방법을 익힌다.
- Grafana 대시보드로 시각화하고 커스텀 PromQL 쿼리를 작성한다.
- 알림 피로 없이 실효성 있는 알림 규칙을 설계한다.
:::

---

## 1. 핵심 메트릭 5가지

효과적인 DB 모니터링은 수십 개의 지표를 보는 것이 아니라 소수의 핵심 지표를 정확히 이해하는 것에서 시작한다.

| 메트릭 | 설명 | 권장 임계값 | 초과 시 징후 |
|--------|------|-------------|--------------|
| QPS (Queries Per Second) | 초당 처리 쿼리 수 | 기준선 대비 2배 초과 | 트래픽 급증, 쿼리 폭풍 |
| Latency p99 | 상위 1% 쿼리의 응답시간 | 500ms 이상 경고 | 슬로우 쿼리, 락 경합 |
| Connection Usage | 활성 커넥션 / 최대 커넥션 비율 | 80% 이상 경고 | 커넥션 풀 고갈 위험 |
| Replication Lag | 레플리카가 마스터보다 뒤처진 시간(초) | 10초 이상 경고 | 레플리카 읽기 신뢰 불가 |
| Buffer Pool Hit Rate | 메모리에서 데이터 조회 비율 | 99% 미만 경고 | 디스크 I/O 병목, 메모리 부족 |

### QPS

QPS 자체의 절대값보다 평소 기준선(baseline) 대비 변화율이 더 중요하다. 평소 500 QPS 서비스에서 갑자기 2,000 QPS가 발생하면 비정상적인 쿼리 패턴이나 장애 상황을 의심해야 한다.

```sql
-- MySQL: 누적 QPS 확인
SHOW GLOBAL STATUS LIKE 'Questions';
SHOW GLOBAL STATUS LIKE 'Queries';

-- PostgreSQL: 초당 쿼리 수 (pg_stat_database)
SELECT datname,
       xact_commit + xact_rollback AS total_tx,
       blks_read, blks_hit
FROM pg_stat_database
WHERE datname = 'mydb';
```

### Latency p99

평균 레이턴시는 이상값에 둔감하다. p99는 100명 중 가장 느린 1명의 응답시간으로, 실제 사용자 경험과 더 가깝다. p99가 높으면 특정 쿼리 패턴이나 데이터 분포 편향을 의심한다.

### Connection Usage

```sql
-- MySQL: 현재 커넥션 상태
SHOW STATUS LIKE 'Threads_connected';
SHOW VARIABLES LIKE 'max_connections';

-- PostgreSQL: 커넥션 사용률
SELECT count(*) AS active,
       (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') AS max_conn,
       round(count(*) * 100.0 /
             (SELECT setting::int FROM pg_settings WHERE name = 'max_connections'), 2) AS usage_pct
FROM pg_stat_activity
WHERE state != 'idle';
```

### Replication Lag

레플리카에서 읽기 분산을 구성한 경우 Replication Lag이 커지면 오래된 데이터를 읽게 된다. 금융이나 재고 데이터는 레플리카 읽기를 사용하지 않거나 Lag 임계값을 엄격하게 설정해야 한다.

### Buffer Pool Hit Rate

```sql
-- MySQL InnoDB Buffer Pool Hit Rate
SELECT
    (1 - (
        (SELECT variable_value FROM performance_schema.global_status
         WHERE variable_name = 'Innodb_buffer_pool_reads') /
        (SELECT variable_value FROM performance_schema.global_status
         WHERE variable_name = 'Innodb_buffer_pool_read_requests')
    )) * 100 AS hit_rate_pct;

-- PostgreSQL Buffer Hit Rate
SELECT
    sum(blks_hit) * 100.0 / (sum(blks_hit) + sum(blks_read)) AS hit_rate_pct
FROM pg_stat_database;
```

---

## 2. Prometheus Exporter

### Exporter 종류

각 DB는 전용 Exporter를 통해 Prometheus 메트릭을 노출한다.

| Exporter | 대상 DB | 주요 메트릭 |
|----------|---------|-------------|
| postgres_exporter | PostgreSQL | pg_stat_user_tables, pg_stat_bgwriter, replication lag |
| mysqld_exporter | MySQL / MariaDB | innodb_buffer_pool, slow_queries, replication_lag |
| redis_exporter | Redis | connected_clients, used_memory, keyspace_hits |

### postgres_exporter 설정

```bash
# Docker로 실행
docker run -d \
  --name postgres_exporter \
  -p 9187:9187 \
  -e DATA_SOURCE_NAME="postgresql://monitor_user:secret@localhost:5432/mydb?sslmode=disable" \
  quay.io/prometheuscommunity/postgres-exporter
```

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'postgresql'
    static_configs:
      - targets: ['localhost:9187']
    scrape_interval: 15s
```

모니터링 전용 계정 생성 (최소 권한):

```sql
CREATE USER monitor_user WITH PASSWORD 'secret';
GRANT pg_monitor TO monitor_user;  -- PostgreSQL 10+
```

### mysqld_exporter 설정

```bash
# MySQL 모니터링 계정 생성
CREATE USER 'exporter'@'localhost' IDENTIFIED BY 'secret';
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'exporter'@'localhost';
FLUSH PRIVILEGES;
```

```bash
# Docker로 실행
docker run -d \
  --name mysqld_exporter \
  -p 9104:9104 \
  -e DATA_SOURCE_NAME="exporter:secret@(localhost:3306)/" \
  prom/mysqld-exporter \
  --collect.global_status \
  --collect.info_schema.innodb_metrics \
  --collect.slave_status
```

### redis_exporter 설정

```bash
docker run -d \
  --name redis_exporter \
  -p 9121:9121 \
  -e REDIS_ADDR="redis://localhost:6379" \
  oliver006/redis_exporter
```

---

## 3. Grafana 대시보드

### 추천 공식 대시보드

Grafana.com의 공개 대시보드를 Import ID로 즉시 불러올 수 있다.

| Dashboard ID | 대상 | 주요 패널 |
|-------------|------|-----------|
| 9628 | PostgreSQL | Transaction rate, Tuple stats, Dead tuples, Cache hit ratio |
| 7362 | MySQL | QPS, InnoDB buffer pool, Replication lag, Slow queries |
| 763 | Redis | Memory usage, Connected clients, Keyspace hits/misses |

Import 방법: Grafana UI → Dashboards → Import → ID 입력 → Prometheus datasource 선택

### 커스텀 메트릭: Dead Tuple 비율

Dead Tuple이 많으면 테이블 스캔이 느려지고 VACUUM이 필요하다는 신호다.

```promql
# Dead Tuple 비율 (%) - PromQL
100 * pg_stat_user_tables_n_dead_tup
  / (pg_stat_user_tables_n_live_tup + pg_stat_user_tables_n_dead_tup + 1)
```

Grafana 패널 설정:

```
- Visualization: Bar gauge 또는 Table
- Thresholds: 10% 이상 yellow, 20% 이상 red
- Legend: {{relname}} (테이블명별 구분)
```

### 커스텀 메트릭: Lock Wait 시간

```promql
# Lock Wait 쿼리 수
pg_locks_count{mode="ExclusiveLock", granted="false"}

# Lock Wait 지속 시간 상위 쿼리 (pg_stat_activity 필요)
# postgres_exporter custom query 등록 필요
```

커스텀 쿼리 등록 (`queries.yaml`):

```yaml
pg_lock_waits:
  query: |
    SELECT
      count(*) AS wait_count,
      max(extract(epoch FROM (now() - query_start))) AS max_wait_seconds
    FROM pg_stat_activity
    WHERE wait_event_type = 'Lock'
  metrics:
    - wait_count:
        usage: "GAUGE"
        description: "Number of queries waiting for locks"
    - max_wait_seconds:
        usage: "GAUGE"
        description: "Maximum lock wait duration in seconds"
```

```mermaid
graph LR
    A[PostgreSQL] -->|메트릭 노출| B[postgres_exporter :9187]
    C[MySQL] -->|메트릭 노출| D[mysqld_exporter :9104]
    B -->|스크래핑| E[Prometheus]
    D -->|스크래핑| E
    E -->|쿼리| F[Grafana]
    F -->|시각화| G[대시보드]
    E -->|알림 규칙| H[AlertManager]
    H -->|알림 전송| I[Slack / PagerDuty]
```

---

## 4. 알림 설계

### p50/p95/p99를 함께 봐야 하는 이유

단일 백분위수만 보면 문제를 놓칠 수 있다.

| 시나리오 | p50 | p95 | p99 | 해석 |
|----------|-----|-----|-----|------|
| 정상 | 20ms | 80ms | 150ms | 건강한 상태 |
| 소수 슬로우 쿼리 | 20ms | 100ms | 2000ms | p99 급등, 특정 쿼리 문제 |
| 전반적 성능 저하 | 200ms | 500ms | 1500ms | DB 전체 부하 증가 |
| 디스크 I/O 포화 | 500ms | 2000ms | 5000ms | 인프라 문제 의심 |

```promql
# Grafana PromQL: p50/p95/p99 함께 표시 (histogram 기반)
histogram_quantile(0.50, sum(rate(db_query_duration_seconds_bucket[5m])) by (le))
histogram_quantile(0.95, sum(rate(db_query_duration_seconds_bucket[5m])) by (le))
histogram_quantile(0.99, sum(rate(db_query_duration_seconds_bucket[5m])) by (le))
```

### Replication Lag: replay_lsn vs sent_lsn

PostgreSQL의 Replication Lag은 두 가지 방식으로 측정한다.

```sql
-- 마스터에서: 각 레플리카의 Lag 확인
SELECT
    client_addr,
    state,
    sent_lsn,
    replay_lsn,
    (sent_lsn - replay_lsn) AS lag_bytes,
    write_lag,
    flush_lag,
    replay_lag
FROM pg_stat_replication;
```

- `sent_lsn - write_lsn`: 네트워크 버퍼에서 대기 중인 바이트
- `write_lsn - flush_lsn`: 디스크에 쓰였지만 fsync 미완료
- `flush_lsn - replay_lsn`: fsync 완료 후 적용 대기 중인 바이트

```promql
# PromQL: 레플리카 Lag 바이트 수
pg_replication_slots_pg_wal_lsn_diff
# 또는 postgres_exporter의 pg_stat_replication 메트릭 활용
```

### 알림 피로 방지

알림이 너무 자주 발생하면 팀이 알림을 무시하게 된다(경보 피로, Alert Fatigue). 효과적인 알림 설계 원칙은 다음과 같다.

```mermaid
graph TD
    A[알림 발생] --> B{긴급도 분류}
    B -->|Critical| C[즉시 호출\nPagerDuty + SMS]
    B -->|Warning| D[업무 시간 내 처리\nSlack 채널]
    B -->|Info| E[대시보드 표시만\n알림 전송 없음]
    C --> F[5분 이내 응답]
    D --> G[1시간 이내 확인]
```

알림 규칙 예시 (Prometheus AlertManager):

```yaml
groups:
  - name: db_alerts
    rules:
      - alert: HighReplicationLag
        expr: pg_replication_lag_seconds > 10
        for: 2m          # 2분 이상 지속될 때만 발화
        labels:
          severity: warning
        annotations:
          summary: "Replication lag is {{ $value }}s"

      - alert: LowBufferPoolHitRate
        expr: pg_buffer_hit_rate < 0.99
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Buffer pool hit rate dropped to {{ $value | humanizePercentage }}"

      - alert: ConnectionUsageHigh
        expr: pg_connection_usage_ratio > 0.80
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "DB connection usage at {{ $value | humanizePercentage }}"
```

알림 피로 방지 체크리스트:
- `for` 조건으로 일시적 스파이크는 알림 제외
- 동일 알림 반복 전송은 `repeat_interval`로 억제
- 야간 Warning 알림은 업무 시간으로 라우팅
- 월 1회 알림 리뷰: 실제로 대응한 알림 vs 노이즈 구분

::: tip 핵심 정리
- 핵심 메트릭은 QPS, Latency p99, Connection Usage, Replication Lag, Buffer Pool Hit Rate 5가지다.
- Exporter는 postgres_exporter(9187), mysqld_exporter(9104), redis_exporter(9121)를 사용한다.
- Grafana 공식 대시보드 ID 9628(PostgreSQL), 7362(MySQL)을 기반으로 시작한다.
- p50/p95/p99를 함께 추적해야 문제 유형을 정확히 진단할 수 있다.
- 알림은 긴급도별로 분류하고 `for` 조건으로 일시적 스파이크를 필터링한다.
:::

## 다음 챕터

다음 챕터에서는 PostgreSQL 특유의 MVCC 구조와 Dead Tuple 문제, Autovacuum 튜닝, Transaction ID Wraparound 위험을 학습한다.

[PostgreSQL 운영](/study/db-optimization/11-postgresql)
