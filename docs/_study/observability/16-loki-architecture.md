---
title: "Loki 아키텍처와 라벨 철학"
description: "Grafana Loki가 왜 로그 전문(full-text)을 인덱싱하지 않고 라벨만 인덱싱하는지, ELK 대비 비용·운영 트레이드오프와 스트림·배포 모드·오브젝트 스토리지 구조를 다룬다."
date: 2026-07-02
tags: [Loki, Logs, Architecture]
prev: /study/observability/15-slo-sli-alerting
next: /study/observability/17-loki-read-write-path
---

# Loki 아키텍처와 라벨 철학

::: info 학습 목표
- Loki가 "Prometheus for logs"로 불리는 이유와 라벨 기반 인덱싱 철학을 이해한다.
- 전문 검색 인덱스를 만들지 않는 설계 결정의 비용·운영 트레이드오프를 ELK 스택과 비교해 설명할 수 있다.
- 라벨(인덱스)과 콘텐츠(청크)가 분리된 구조와 스트림 개념, 카디널리티 함정을 파악한다.
- monolithic·simple scalable·microservices 세 배포 모드의 차이와 선택 기준을 안다.
:::

## 1. Loki의 설계 철학 — "Prometheus for logs"

[Loki](https://grafana.com/docs/loki/latest/)는 스스로를 "Prometheus for logs"라고 소개한다. Prometheus가 시계열을 라벨로 식별하듯, Loki도 로그 스트림을 라벨 집합으로 식별한다. 결정적 차이는 인덱싱 대상이다. Prometheus는 숫자 값 자체가 데이터라서 라벨과 값을 함께 인덱싱하지만, Loki는 로그의 <strong>본문 텍스트는 인덱싱하지 않는다</strong>. 인덱스에 들어가는 건 오직 라벨 집합(스트림 식별자)뿐이고, 로그 라인 자체는 압축된 청크(chunk)로 오브젝트 스토리지에 그대로 쌓인다.

이 결정은 Loki 팀이 명시적으로 밝힌 목표에서 나온다. 풀텍스트 인덱스를 만드는 대신, 쿼리 시점에 라벨로 대상 스트림을 좁힌 뒤 해당 청크만 훑어(grep) 라인 필터를 적용한다. 즉 "인덱스로 찾고 스캔으로 거른다"가 아니라 "라벨로 좁히고 그 다음은 다 스캔한다"에 가깝다.

![Prometheus 모델은 숫자 값 자체를 인덱싱하고, Loki 모델은 labels만 인덱싱하며 log line은 압축 청크로 비인덱싱 저장하는 두 모델의 인덱싱 대상 비교](/images/study-observability/16-prom-vs-loki.png)

## 2. 왜 전문 검색 인덱스를 만들지 않는가

Elasticsearch(ELK)류 시스템은 모든 로그 라인의 모든 토큰을 역인덱스(inverted index)에 넣는다. 어떤 단어로든 즉시 검색할 수 있는 대신, 인덱스 크기가 원본 로그 크기와 비슷하거나 그 이상으로 커진다. 인덱싱 자체가 CPU를 많이 쓰고, 인덱스를 계속 리밸런싱·머지해야 하며, 샤드 운영 부담이 크다.

Loki는 이 비용을 의도적으로 포기한다. 인덱스에는 라벨만 들어가므로 인덱스 크기가 로그 볼륨과 거의 무관하게 작다. 대신 "특정 단어가 포함된 로그를 찾아줘" 같은 임의 전문 검색은 느리다 — 라벨로 좁힌 스트림 범위 안에서 청크를 순차적으로 훑어야 한다. 이 트레이드오프가 성립하는 이유는 실무에서 로그 조회가 대부분 "특정 서비스·특정 시간대·특정 레벨"처럼 라벨로 이미 좁혀진 상태에서 시작하기 때문이다. 좁혀진 범위 안에서의 순차 스캔은 병렬로 수행하면 충분히 빠르다.

| 항목 | Elasticsearch(ELK) | Loki |
|---|---|---|
| 인덱스 대상 | 모든 로그 토큰(전문) | 라벨 집합만 |
| 인덱스 크기 | 원본 로그와 비슷하거나 초과 | 로그 볼륨 대비 매우 작음 |
| 인제스트 비용 | 높음(토큰화·역인덱스 구성) | 낮음(라벨 파싱 + 압축) |
| 임의 텍스트 검색 | 빠름 | 라벨로 좁힌 뒤 스캔(상대적으로 느림) |
| 운영 복잡도 | 샤드·세그먼트 관리 부담 큼 | 스테이트리스 컴포넌트 + 오브젝트 스토리지 |
| 스토리지 비용 | 상대적으로 높음(로컬 디스크 중심) | 오브젝트 스토리지로 매우 저렴 |

결국 선택 기준은 명확하다. 로그 검색이 라벨(서비스, 네임스페이스, 레벨) 위주로 이뤄지고 비용·운영 단순성이 중요하면 Loki가 유리하고, 임의 자유 텍스트 검색이 핵심 요구사항이면 Elasticsearch류가 더 적합하다.

## 3. 라벨 vs 콘텐츠 — 인덱스는 라벨, 청크는 압축 로그

Loki 저장 구조는 두 계층으로 나뉜다.

- <strong>인덱스</strong>: 라벨 집합 → 청크 참조를 매핑하는 작은 테이블. 최신 Loki는 이를 [TSDB 인덱스](https://grafana.com/docs/loki/latest/operations/storage/tsdb/) 포맷으로 관리한다.
- <strong>청크(chunk)</strong>: 같은 라벨 집합을 가진 로그 라인들을 시간순으로 모아 gzip/snappy/zstd 등으로 압축한 블록. 실제 로그 본문이 여기 들어있다.

쿼리가 들어오면 먼저 라벨 매처로 인덱스를 조회해 대상 청크 목록을 얻고, 그 청크들만 오브젝트 스토리지에서 가져와 압축 해제한 뒤 라인 필터·파서를 적용한다. 라벨로 좁혀지지 않는 쿼리(예: 라벨 없이 전체 스트림 대상 검색)는 훑어야 할 청크 수가 폭증해 매우 느려진다 — Loki 운영에서 가장 흔한 성능 함정이다.

![LogQL 쿼리가 인덱스에서 라벨 매처로 청크 참조를 얻고, 대상 청크만 오브젝트 스토리지에서 로드해 라인 필터·파서를 적용하는 쿼리 흐름](/images/study-observability/16-query-index-chunk.png)

## 4. 스트림 개념 — label set = stream

Loki에서 <strong>스트림(stream)</strong>은 고유한 라벨 집합 하나에 해당하는 로그 시퀀스다. 예를 들어 `{app="checkout", env="prod", pod="checkout-7f9-abc"}`는 하나의 스트림이고, 같은 라벨 조합을 가진 로그 라인들이 시간순으로 그 스트림에 쌓인다. 라벨 값이 하나라도 다르면 별개의 스트림이 된다.

여기서 카디널리티 문제가 생긴다. 라벨 값의 조합 수가 곧 스트림 수이므로, 카디널리티가 높은 값(요청 ID, 사용자 ID, 세션 ID, 트레이스 ID 등)을 라벨로 넣으면 스트림이 기하급수적으로 늘어난다. 스트림이 많아지면 인덱스가 커지고, ingester가 관리해야 할 메모리 상태(청크 버퍼)가 늘고, 압축 효율도 떨어진다(스트림당 로그량이 적으면 청크가 작고 파편화된다). Loki의 인덱스가 작다는 장점 자체가 무너지는 셈이다.

![안전한 라벨 설계(app·env·namespace·level, 값 개수 적음 → 스트림 수백~수천)와 위험한 라벨 설계(request_id·user_id·trace_id, 값 무한대 → 스트림 무한 증가) 비교](/images/study-observability/16-cardinality.png)

고카디널리티 값은 라벨이 아니라 로그 라인 본문(JSON 필드 등)에 남기고, 필요하면 <strong>구조화 메타데이터(structured metadata)</strong>로 붙이는 방식이 정석이다. 이 부분은 [로그 파이프라인과 스토리지](/study/observability/19-log-pipeline-storage)에서 라벨 설계 원칙과 함께 더 자세히 다룬다.

## 5. 배포 모드 — monolithic / simple scalable / microservices

Loki는 하나의 바이너리 안에 모든 컴포넌트(distributor, ingester, querier, query-frontend, compactor 등)를 `-target` 플래그로 켜고 끌 수 있게 만들어져 있다. 덕분에 규모에 맞춰 세 가지 배포 모드를 선택할 수 있다.

- <strong>Monolithic</strong>: 단일 프로세스(또는 단일 프로세스의 다중 레플리카)에서 모든 컴포넌트가 함께 돈다. 설정이 단순하고 로컬/소규모 클러스터에 적합하지만, 읽기와 쓰기 부하를 독립적으로 스케일링할 수 없다.
- <strong>Simple scalable</strong>: 컴포넌트를 read 경로와 write 경로 두 타깃으로 분리한다(`-target=read`, `-target=write`, 그리고 backend 타깃으로 compactor·ruler 등을 분리). 대부분의 프로덕션 환경에 권장되는 기본 모드로, 운영 복잡도와 확장성 사이의 균형점이다.
- <strong>Microservices</strong>: distributor, ingester, querier, query-frontend, compactor, index-gateway 등 모든 컴포넌트를 각각 독립 배포로 분리한다. 컴포넌트별로 독립적인 오토스케일링이 가능해 초대형 멀티테넌시 환경에 적합하지만, 운영 부담이 가장 크다.

![Loki 세 배포 모드 비교 — monolithic(단일 프로세스), simple scalable(read·write·backend 타깃 분리), microservices(distributor·ingester·querier·query-frontend·compactor·index-gateway 개별 배포)](/images/study-observability/16-deployment-modes.png)

컴포넌트 각각의 역할은 [읽기/쓰기 경로와 구성요소](/study/observability/17-loki-read-write-path)에서 자세히 다룬다.

## 6. 오브젝트 스토리지 기반 저장

Loki는 인덱스와 청크를 모두 오브젝트 스토리지(S3, GCS, Azure Blob Storage, 개발용으로는 로컬 파일시스템)에 저장하도록 설계됐다. 이 선택 덕분에 ingester·querier 같은 컴포넌트를 스테이트리스에 가깝게 유지할 수 있고, 로컬 디스크 용량에 얽매이지 않고 수평 확장할 수 있다.

```yaml
schema_config:
  configs:
    - from: 2024-01-01
      store: tsdb
      object_store: s3
      schema: v13
      index:
        prefix: loki_index_
        period: 24h

storage_config:
  aws:
    s3: s3://us-east-1/my-loki-bucket
    s3forcepathstyle: false
  tsdb_shipper:
    active_index_directory: /loki/tsdb-index
    cache_location: /loki/tsdb-cache
```

`schema_config`는 시간 구간별로 인덱스 포맷(store)과 오브젝트 스토어를 지정한다. 스키마를 바꾸려면 새 `from` 날짜로 새 항목을 추가해야 하며, 과거 데이터는 이전 스키마 그대로 남는다 — Prometheus의 TSDB 블록처럼 스키마가 시간 구간에 못박힌다는 점을 기억해야 한다. 쿠버네티스 환경에서의 Loki 배포는 [Kubernetes 관측성](/study/kubernetes/41-logging-tracing) 챕터의 로깅 아키텍처 논의와도 이어진다.

::: tip 핵심 정리
- Loki는 로그 본문을 인덱싱하지 않고 라벨만 인덱싱하는 "Prometheus for logs" 철학을 따른다.
- 전문 검색 인덱스를 포기한 대가로 인제스트 비용과 운영 복잡도를 크게 낮추지만, 라벨 없는 임의 텍스트 검색은 느리다.
- 인덱스(라벨 → 청크 참조)와 청크(압축된 로그 본문)는 명확히 분리된 저장 계층이다.
- 고유 라벨 집합 = 스트림이며, 고카디널리티 라벨은 스트림 폭증과 인덱스 비대화를 부른다.
- monolithic·simple scalable·microservices 세 배포 모드는 같은 바이너리를 타깃 분리로 운영 규모에 맞춘 것이다.
- 인덱스와 청크 모두 오브젝트 스토리지에 저장돼 컴포넌트가 스테이트리스에 가깝게 수평 확장한다.
:::

## 다음 챕터

라벨 인덱스와 청크 구조를 이해했다면, 다음은 그 위에서 실제로 로그가 어떻게 쓰이고 읽히는지 볼 차례다. 다음 챕터 [읽기/쓰기 경로와 구성요소](/study/observability/17-loki-read-write-path)에서는 distributor·ingester·querier·query-frontend·compactor가 각각 어떤 역할을 맡아 쓰기 경로와 읽기 경로를 구성하는지 다룬다.
