---
title: "Prometheus 아키텍처"
description: "SoundCloud에서 태어난 Prometheus의 pull 기반·단일 바이너리 설계 철학과 retrieval·TSDB·PromQL 엔진·rule manager 내부 구조, 그리고 단일 노드가 갖는 한계와 확장 경로를 다룬다."
date: 2026-07-02
tags: [Prometheus, Architecture]
prev: /study/observability/04-pull-push-cardinality
next: /study/observability/06-data-model
---

# Prometheus 아키텍처

::: info 학습 목표
- Prometheus가 SoundCloud에서 탄생한 배경과 pull 기반·단일 바이너리 설계 철학을 이해한다.
- retrieval, TSDB, HTTP API/PromQL 엔진, rule manager 등 핵심 컴포넌트의 역할을 파악한다.
- client 라이브러리·Exporter·Pushgateway·Alertmanager·서비스 디스커버리로 이어지는 생태계 구조를 안다.
- scrape → WAL → head → query로 이어지는 데이터 흐름과 단일 노드의 한계·확장 경로를 이해한다.
:::

## 1. 설계 철학

<strong>Prometheus</strong>는 2012년 SoundCloud에서 시작된 프로젝트다. 구글 내부의 모니터링 시스템인 Borgmon의 설계를 계승했고, 2016년 CNCF에 두 번째 프로젝트로 합류(쿠버네티스 다음)하며 사실상 클라우드 네이티브 모니터링의 표준이 됐다. 설계 철학을 이해하면 이후 등장하는 "왜 이렇게 만들어졌나"류의 의문 대부분이 풀린다.

<strong>Pull 모델을 기본으로 택한 이유</strong>가 핵심이다. Prometheus 서버가 타깃의 `/metrics` HTTP 엔드포인트를 주기적으로 긁어온다. 이 선택에는 세 가지 실용적 이유가 있다.

- <strong>타깃의 생사 자체가 신호가 된다.</strong> 스크레이프가 실패하면 `up{job="..."} == 0`으로 즉시 드러난다. Push 모델에서는 "얼마 동안 데이터가 안 왔다"는 것이 다운인지 네트워크 문제인지 애매하지만, pull은 실패 자체를 1급 시그널로 취급한다.
- <strong>디버깅이 curl 한 줄로 끝난다.</strong> 운영자가 `curl target:9100/metrics`만 치면 Prometheus가 보는 것과 동일한 데이터를 그대로 볼 수 있다. 별도 프로토콜이나 수신 서버 상태를 조회할 필요가 없다.
- <strong>중앙에서 스크레이프 빈도·타임아웃을 통제한다.</strong> 수천 개 타깃이 제각각 push 주기를 정하면 서버 쪽 부하 예측이 불가능하다. Pull은 서버가 언제·얼마나 자주 당길지 결정하므로 용량 계획이 쉬워진다.

물론 pull이 만능은 아니다. 방화벽 뒤에 있거나 NAT 너머의 타깃, 초 단위보다 짧은 생명주기의 배치 잡은 pull로 잡아내기 어렵다. 이 트레이드오프는 [04장](/study/observability/04-pull-push-cardinality)에서 이미 다뤘다.

<strong>단일 바이너리(single binary) 설계</strong>도 의도적인 선택이다. 스크레이핑·저장·질의·룰 평가가 하나의 프로세스 안에서 돈다. Zookeeper나 별도 메타데이터 스토어, 외부 데이터베이스 같은 의존성이 없다. 로컬 디스크만 있으면 뜬다. 이 단순함은 배포·운영 부담을 크게 줄이지만, 동시에 <strong>단일 노드 확장 한계</strong>라는 대가를 남긴다 — 이 주제는 6절에서 다룬다.

<strong>신뢰성 우선(reliability first)</strong> 원칙은 Prometheus 문서 전반에 명시적으로 등장한다. "Prometheus 서버는 인프라의 다른 부분이 무너진 상황에서도 시스템 상태를 즉시 확인할 수 있는 독립적인 시스템으로 설계됐다"는 문장이 대표적이다. 알림 평가에 필요한 모든 계산(recording rule, alerting rule)이 로컬에서 끝나며, 외부 서비스에 대한 런타임 의존이 없다. 대신 이 신뢰성은 장기 저장이나 전역적으로 100% 정확한 데이터를 포기하는 대가로 얻어진다 — CAP 정리에서 굳이 고르자면 Prometheus는 파티션 상황에서도 가용성(A)을 우선하고, 강한 일관성이나 완전성은 다음 순위로 미룬다.

## 2. 핵심 컴포넌트

단일 바이너리 안에는 역할이 분명히 나뉜 서브시스템 네 개가 협업한다.

![Prometheus 단일 프로세스 내부의 Retrieval·TSDB·HTTP Server(PromQL 엔진)·Rule Manager 네 컴포넌트가 Service Discovery·스크레이프 타깃·사용자 조회를 받아 협업하고 Rule Manager가 Alertmanager로 알림을 보내는 구조](/images/study-observability/05-core-components-light.png)
![Prometheus 단일 프로세스 내부의 Retrieval·TSDB·HTTP Server(PromQL 엔진)·Rule Manager 네 컴포넌트가 Service Discovery·스크레이프 타깃·사용자 조회를 받아 협업하고 Rule Manager가 Alertmanager로 알림을 보내는 구조](/images/study-observability/05-core-components-dark.png)

- <strong>Retrieval(스크레이프 매니저)</strong>은 서비스 디스커버리로부터 타깃 목록을 받아 `scrape_interval`마다 각 타깃의 `/metrics`를 HTTP GET으로 당겨온다. relabeling도 이 단계에서 적용된다.
- <strong>TSDB(시계열 데이터베이스)</strong>는 긁어온 샘플을 WAL(Write-Ahead Log)에 먼저 쓰고, 메모리의 head 블록에 append한 뒤 주기적으로 디스크 블록으로 압축한다. 자세한 내부 구조는 4절에서 다룬다.
- <strong>HTTP Server / PromQL 엔진</strong>은 `/api/v1/query`, `/api/v1/query_range` 같은 REST 엔드포인트를 노출하고, PromQL 표현식을 파싱·평가해 TSDB에서 결과를 뽑아낸다. Grafana를 비롯한 모든 외부 조회는 이 엔진을 거친다.
- <strong>Rule Manager</strong>는 `rule_files`에 정의된 recording rule과 alerting rule을 `evaluation_interval`마다 PromQL로 평가한다. Recording rule은 결과를 새 시계열로 TSDB에 다시 써넣고, alerting rule은 조건 충족 시 Alertmanager로 알림을 HTTP push한다. 즉 Prometheus 서버 자신도 PromQL 엔진의 소비자다.

네 컴포넌트 모두 하나의 프로세스, 하나의 Go 런타임 안에서 함께 돈다는 점이 단일 바이너리 설계의 실체다.

## 3. 생태계

Prometheus 서버 자체는 작지만, 주변 생태계가 실제 운영을 완성한다.

![Prometheus 생태계 — 화이트박스 계측(Client Library+애플리케이션), 브릿지(Exporter+계측 불가 대상), 배치(단명 배치 잡+Pushgateway) 세 소스가 모두 /metrics pull로 Prometheus에 수집되고 Service Discovery가 타깃을 갱신하며 Prometheus가 Alertmanager로 알림을 전송하는 구조](/images/study-observability/05-ecosystem-light.png)
![Prometheus 생태계 — 화이트박스 계측(Client Library+애플리케이션), 브릿지(Exporter+계측 불가 대상), 배치(단명 배치 잡+Pushgateway) 세 소스가 모두 /metrics pull로 Prometheus에 수집되고 Service Discovery가 타깃을 갱신하며 Prometheus가 Alertmanager로 알림을 전송하는 구조](/images/study-observability/05-ecosystem-dark.png)

- <strong>클라이언트 라이브러리</strong>는 Go, Java, Python, Rust, Ruby 등 주요 언어를 공식 지원한다. 애플리케이션 코드 안에서 Counter·Gauge·Histogram 같은 메트릭을 직접 만들고 노출하는 화이트박스 계측(white-box instrumentation)의 기반이다. 자세한 내용은 [08장](/study/observability/08-exporters-instrumentation)에서 다룬다.
- <strong>Exporter</strong>는 애플리케이션을 직접 고칠 수 없거나 계측 자체가 불가능한 대상(운영체제, DB, 하드웨어, 서드파티 서비스)을 위한 브릿지다. node_exporter, mysqld_exporter, blackbox_exporter가 대표적이며, 대상 시스템의 상태를 대신 읽어 Prometheus 노출 형식으로 변환해준다.
- <strong>Pushgateway</strong>는 pull 모델의 예외 케이스, 즉 스크레이프 사이 살아있지 않은 단명 배치 잡을 위한 중계소다. 잡이 끝나기 직전 결과를 Pushgateway에 push하면 Prometheus는 평소처럼 Pushgateway를 pull한다. 다만 남용하면 위험하다 — Pushgateway는 push된 메트릭을 <strong>영구적으로</strong> 들고 있으므로, 잡을 지우지 않으면 이미 끝난 작업의 오래된 값이 계속 노출되고(staleness 문제), 여러 인스턴스의 배치 잡이 같은 메트릭 이름으로 push하면 값을 서로 덮어쓴다. 공식 문서도 "일반적인 서비스 메트릭에는 쓰지 말라"고 명시한다.
- <strong>Alertmanager</strong>는 Prometheus 서버와 완전히 분리된 별도 바이너리다. Rule Manager가 발화(firing)시킨 알림을 받아 그룹핑·중복 제거·억제(inhibition)·라우팅을 처리한다. 이 분리 덕분에 알림 로직을 서버 재시작과 무관하게 독립적으로 운영할 수 있다. [13장](/study/observability/13-alertmanager-architecture)에서 자세히 다룬다.
- <strong>서비스 디스커버리(SD)</strong>는 `kubernetes_sd_configs`, `ec2_sd_configs`, `consul_sd_configs`, `file_sd_configs` 등으로 동적인 타깃 목록을 Retrieval에 공급한다. [07장](/study/observability/07-scraping-service-discovery)의 주제다.

## 4. 데이터 흐름 — scrape → WAL → head → query

샘플 하나가 타깃에서 나와 질의 결과로 잡히기까지의 경로를 추적하면 TSDB 내부 동작이 분명해진다.

![샘플 하나의 여정 시퀀스 — scrape_interval마다 Retrieval이 타깃에서 GET /metrics로 샘플을 받아 WAL에 append(durability)하고 동시에 Head Block 메모리 청크에 append하며, 기본 2시간 주기로 Head를 디스크 블록으로 flush하고 대응 WAL 세그먼트를 truncate, PromQL 엔진이 최근·과거 데이터를 조회해 병합하는 흐름](/images/study-observability/05-data-flow-light.png)
![샘플 하나의 여정 시퀀스 — scrape_interval마다 Retrieval이 타깃에서 GET /metrics로 샘플을 받아 WAL에 append(durability)하고 동시에 Head Block 메모리 청크에 append하며, 기본 2시간 주기로 Head를 디스크 블록으로 flush하고 대응 WAL 세그먼트를 truncate, PromQL 엔진이 최근·과거 데이터를 조회해 병합하는 흐름](/images/study-observability/05-data-flow-dark.png)

- 스크레이프된 샘플은 <strong>먼저 WAL에 기록</strong>된다. WAL은 append-only 로그이며, Prometheus가 크래시해도 재시작 시 WAL을 재생(replay)해서 메모리 상태를 복구할 수 있게 해준다. durability의 핵심 장치다.
- 동시에 샘플은 <strong>head 블록</strong>이라는 메모리 상의 구조에 청크(chunk) 형태로 쌓인다. 최근 데이터(기본 설정 기준 최근 몇 시간)에 대한 질의는 이 head 블록에서 바로 응답한다.
- head 블록은 <strong>기본 2시간 주기</strong>로 불변(immutable) 디스크 블록으로 compaction된다. 이후 백그라운드에서 인접한 작은 블록들을 더 큰 블록으로 재차 압축(merge compaction)해 블록 개수와 인덱스 오버헤드를 줄인다.
- 디스크 블록이 만들어지면 대응하는 WAL 세그먼트는 더 이상 필요 없으므로 truncate된다. WAL은 "아직 블록화되지 않은 최근 데이터의 안전망" 역할만 한다.
- PromQL 엔진은 질의 시점 범위에 따라 head와 여러 디스크 블록을 <strong>투명하게 병합</strong>해서 하나의 연속된 시계열 뷰를 반환한다. 사용자는 데이터가 메모리에 있는지 디스크에 있는지 알 필요가 없다.

이 구조는 [12장](/study/observability/12-tsdb-remote-write)에서 블록 포맷과 인덱스 구조까지 더 깊게 다룬다.

## 5. Prometheus가 하지 않는 것

Prometheus 문서는 스스로 "무엇을 하지 않는지"를 명시적으로 밝힌다. 이 경계를 모르면 운영 중 잘못된 기대를 하게 된다.

- <strong>장기 저장을 하지 않는다.</strong> 로컬 TSDB는 기본 retention이 15일이고, 로컬 디스크 용량에 의존한다. 수 개월~수 년 단위의 과거 데이터 보관은 설계 범위 밖이다. 억지로 retention을 늘리면 디스크 I/O와 압축 부하가 선형 이상으로 증가한다.
- <strong>수평 확장이 안 된다.</strong> 하나의 Prometheus 서버는 하나의 프로세스, 하나의 로컬 디스크에서만 동작한다. 네이티브 샤딩이나 클러스터링 기능이 없다. 데이터 볼륨이 한 서버 용량을 넘으면 job/target 단위로 여러 서버에 수동 분산시키는 것이 유일한 native 대응책이다.
- <strong>100% 정확도를 보장하지 않는다.</strong> Pull 모델의 특성상 스크레이프 실패, 타이밍 지연, 재시작 중 유실 등으로 일부 샘플이 빠질 수 있다. Prometheus 공식 문서도 "Prometheus의 신뢰성은 극도로 정확한 데이터보다 가용성을 우선한다"고 말한다. 과금이나 정산처럼 샘플 하나도 놓치면 안 되는 워크로드에는 애초에 적합하지 않은 도구다.

이 세 가지는 결함이 아니라 <strong>의도된 스코프 제한</strong>이다. 단일 바이너리로 단순함과 신뢰성을 얻는 대신, 확장성과 완전성은 다른 컴포넌트에 위임한다.

## 6. 단일 노드 한계와 확장 경로

단일 노드 한계를 실제로 넘어서야 할 때 쓰는 경로는 크게 세 가지다.

![단일 노드 한계를 넘는 두 확장 경로 — 리프 Prometheus 서버들(팀 A·B·C)이 federation(/federate)으로 글로벌 Prometheus에 요약 메트릭만 재수집해 전역 알림/대시보드를 만들거나, remote_write로 Mimir/Thanos에 실시간 스트리밍해 장기 저장·수평 확장과 전역 질의를 위임하는 구조](/images/study-observability/05-scaling-paths-light.png)
![단일 노드 한계를 넘는 두 확장 경로 — 리프 Prometheus 서버들(팀 A·B·C)이 federation(/federate)으로 글로벌 Prometheus에 요약 메트릭만 재수집해 전역 알림/대시보드를 만들거나, remote_write로 Mimir/Thanos에 실시간 스트리밍해 장기 저장·수평 확장과 전역 질의를 위임하는 구조](/images/study-observability/05-scaling-paths-dark.png)

- <strong>Federation</strong>은 상위 Prometheus 서버가 하위 서버들의 `/federate` 엔드포인트를 스크레이프해서 요약된 메트릭만 끌어올리는 방식이다. 조직 계층별로 대시보드를 합치는 용도에는 쓸 만하지만, federation 자체도 pull이라 전체 raw 데이터를 옮기기엔 대역폭·카디널리티 부담이 크고, 진짜 샤딩이 아니라 "선택적 재수집"에 가깝다는 한계가 있다.
- <strong>remote_write</strong>는 Prometheus가 수집한 샘플을 실시간으로 원격 스토리지에 스트리밍하는 프로토콜이다. 로컬 TSDB는 여전히 단기 버퍼 역할을 하고, 진짜 장기 저장·전역 질의는 remote_write 수신 측이 담당한다.
  ```yaml
  remote_write:
    - url: "https://mimir.internal:9009/api/v1/push"
      queue_config:
        max_samples_per_send: 2000
        max_shards: 30
  ```
- 이 remote_write를 받는 대표적인 수평 확장 백엔드가 <strong>Mimir</strong>(Grafana Labs)와 <strong>Thanos</strong>다. 둘 다 여러 Prometheus 서버로부터 데이터를 모아 하나의 전역 뷰로 질의할 수 있게 해주고, 오브젝트 스토리지 기반으로 사실상 무제한에 가까운 장기 보관을 제공하며, 멀티테넌시를 지원한다. Prometheus 서버 자체는 여전히 "수집 에이전트+단기 캐시"로 남고, 확장성 문제는 이 계층에 위임하는 것이 현재 업계 표준 패턴이다. 자세한 아키텍처는 [35장 — 장기 저장 Mimir](/study/observability/35-mimir-longterm-storage)에서 다룬다.

::: tip 핵심 정리
- Prometheus는 SoundCloud/Borgmon 계보의 pull 기반·단일 바이너리 시스템으로, 단순함과 신뢰성을 최우선 가치로 설계됐다.
- Retrieval·TSDB·PromQL 엔진·Rule Manager 네 컴포넌트가 하나의 프로세스 안에서 협업하며, 외부 의존성 없이 스스로 완결된다.
- 생태계는 client 라이브러리(화이트박스 계측)·Exporter(브릿지)·Pushgateway(예외적 배치 케이스)·Alertmanager(분리된 알림 처리)·서비스 디스커버리로 확장된다.
- 샘플은 WAL(durability) → head 블록(메모리) → 디스크 블록(압축) 순으로 흐르며, PromQL 엔진은 이를 투명하게 병합해 질의에 응답한다.
- 장기 저장·수평 확장·100% 정확도는 의도적으로 스코프 밖이며, federation·remote_write를 거쳐 Mimir/Thanos 같은 별도 계층에 위임하는 것이 표준 확장 경로다.
:::

## 다음 챕터

[데이터 모델과 시계열](/study/observability/06-data-model)에서는 metric name과 라벨이 어떻게 시계열을 식별하는지, Counter·Gauge·Histogram·Summary 네 메트릭 타입의 차이와 최근 등장한 native histogram, 그리고 라벨 설계 원칙을 다룬다.
