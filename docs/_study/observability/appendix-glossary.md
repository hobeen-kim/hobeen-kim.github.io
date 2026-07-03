---
title: "용어집"
description: "관측성 스터디 전체에 등장한 핵심 용어를 카테고리별로 정리한 레퍼런스. 일반 개념부터 메트릭·로그·트레이스·프로파일 신호별 용어, Prometheus/Mimir/Loki/Tempo/Pyroscope/Alloy 등 컴포넌트 용어까지 표로 모았다."
date: 2026-07-02
tags: [Observability, Glossary]
prev: /study/observability/42-grafana-alerting-irm
next: /study/observability/appendix-cheatsheet
---

# 용어집

본문에 등장한 관측성 핵심 용어를 카테고리별로 한 줄씩 정리한다. 공식 정의가 필요하면 각 프로젝트 문서를 함께 참고한다. 기술 용어는 원문 표기를 유지한다.

## 일반

| 용어 | 설명 |
|---|---|
| 관측성(Observability) | 시스템 내부 상태를 외부에서 관측 가능한 신호로부터 추론할 수 있는 능력. 사전에 정의된 대시보드 없이도 예상치 못한 장애 원인을 파고들 수 있는 수준을 목표로 한다. |
| 모니터링(Monitoring) | 미리 정의한 지표·임계값을 지속 관찰해 "알려진 실패 모드"를 감지하는 활동. 관측성의 부분집합이다. |
| 카디널리티(Cardinality) | 라벨 조합이 만들어내는 고유 시계열/스트림의 수. 라벨 값의 종류가 늘어날수록 지수적으로 증가해 저장·질의 비용을 폭발시킬 수 있다. |
| SLI (Service Level Indicator) | 서비스 품질을 정량적으로 나타내는 실측 지표(예: 요청 성공률, p99 지연). |
| SLO (Service Level Objective) | SLI가 만족해야 할 목표 수준(예: "성공률 99.9%"). 알림·에러 버짓 계산의 기준이 된다. |
| SLA (Service Level Agreement) | SLO를 어겼을 때의 책임·보상까지 포함하는 대외 계약. SLO보다 상위 개념이다. |
| 에러 버짓(Error Budget) | SLO가 허용하는 실패의 총량. 소진 속도(burn rate)를 기준으로 알림을 설계하는 것이 SRE의 표준 패턴이다. |
| RED 메소드 | Rate(요청률)·Errors(에러율)·Duration(지연)으로 요청 기반 서비스를 관찰하는 방법론. Tom Wilkie가 제안했다. |
| USE 메소드 | Utilization(사용률)·Saturation(포화도)·Errors(에러)로 리소스(CPU, 디스크 등)를 관찰하는 방법론. Brendan Gregg가 제안했다. |
| 샘플링(Sampling) | 전체 데이터 중 일부만 수집·저장해 비용을 줄이는 기법. 트레이스의 head/tail sampling, 프로파일의 주기적 스택 샘플링 등이 대표적이다. |
| 4대 신호(Four Signals) | 관측성을 구성하는 메트릭·로그·트레이스·프로파일 네 가지 텔레메트리 유형. |
| 상관관계(Correlation) | 서로 다른 신호를 공통 식별자(trace ID, exemplar 등)로 연결해 하나의 조사 흐름으로 엮는 것. |
| LGTM+ 스택 | Loki·Grafana·Tempo·Mimir(+Pyroscope, Alloy)로 구성된 Grafana Labs의 관측성 스택 조합을 부르는 이름. |

## 메트릭

| 용어 | 설명 |
|---|---|
| 시계열(Time Series) | 동일한 메트릭 이름과 라벨 집합에 대해 시간순으로 기록된 (timestamp, value) 샘플의 나열. |
| Counter | 단조 증가만 하는 누적 카운터 메트릭 타입. 재시작 시 0으로 리셋될 수 있어 `rate`/`increase`로 다뤄야 한다. |
| Gauge | 오르내릴 수 있는 순간값 메트릭 타입(예: 메모리 사용량, 큐 길이). |
| Histogram | 값을 버킷(bucket)으로 나눠 분포를 근사하는 메트릭 타입. `_bucket`/`_sum`/`_count` 시계열 세트로 노출되며 `histogram_quantile`로 분위수를 추정한다. |
| Summary | 클라이언트 사이드에서 분위수를 직접 계산해 노출하는 메트릭 타입. 서버 사이드 집계(join)가 불가능해 Histogram보다 활용도가 낮다. |
| Native Histogram | 버킷 경계를 클라이언트가 고정하지 않고 스파스(sparse) 스키마로 자동 조정하는 신형 히스토그램. 기존 클래식 히스토그램보다 정밀도와 저장 효율이 높다. |
| Exemplar | 히스토그램 샘플에 trace ID 같은 부가 정보를 덧붙인 데이터 포인트. 메트릭 그래프에서 특정 트레이스로 바로 점프하는 상관관계의 핵심 장치다. |
| remote_write | Prometheus가 수집한 샘플을 실시간으로 원격 스토리지(Mimir, Thanos 등)에 스트리밍하는 프로토콜. |
| WAL (Write-Ahead Log) | 샘플을 디스크 블록으로 압축하기 전에 먼저 append-only로 기록하는 로그. 크래시 후 재생(replay)으로 메모리 상태를 복구하는 durability 장치다. |
| TSDB | Time Series Database. Prometheus의 로컬 저장 엔진으로, WAL·head 블록·디스크 블록으로 구성된다. |
| 레이블(Label) | 메트릭에 붙는 key-value 메타데이터. 라벨 값의 조합이 시계열의 고유 식별자를 이룬다. |
| 스크레이핑(Scraping) | Prometheus가 타겟의 `/metrics` 엔드포인트를 주기적으로 HTTP GET해 샘플을 가져오는 pull 방식 수집. |
| Recording Rule | 자주 쓰는 쿼리 결과를 미리 계산해 새 시계열로 저장하는 규칙. 대시보드·알림의 질의 비용을 낮춘다. |
| Alerting Rule | PromQL 조건이 일정 기간(`for`) 참이면 알림을 발생시키는 규칙. |
| 서비스 디스커버리(Service Discovery) | 스크레이프 대상을 정적 목록이 아니라 Kubernetes, Consul 등 외부 시스템으로부터 동적으로 찾아내는 메커니즘. |
| Relabeling | 스크레이프 전/후 라벨을 조작(추가·삭제·변환)하는 규칙. 타겟 필터링과 라벨 정규화에 쓴다. |

## 로그

| 용어 | 설명 |
|---|---|
| 로그 스트림(Log Stream) | Loki에서 동일한 라벨 집합을 공유하는 로그 라인의 묶음. 인덱스의 최소 단위다. |
| Structured Metadata | 로그 라인 본문을 라벨로 승격하지 않고도 검색 가능한 구조화 필드로 붙이는 Loki 기능. 카디널리티 폭발 없이 고유값이 많은 필드를 다룰 수 있다. |
| LogQL | Loki의 질의 언어. 스트림 셀렉터, 라인/라벨 필터, 파서, 메트릭 함수로 구성된다. |
| 라벨 인덱스(Label Index) | Loki가 로그 본문 전체가 아니라 라벨 조합만 인덱싱하는 설계. 인덱스 크기를 작게 유지하는 대신 본문 검색은 청크를 순차 스캔한다. |
| Chunk | 동일 스트림의 로그 라인을 압축해 오브젝트 스토리지에 저장하는 단위. |
| Ingester | Loki에서 들어오는 로그를 받아 청크로 모아 오브젝트 스토리지에 flush하는 컴포넌트. |

## 트레이스

| 용어 | 설명 |
|---|---|
| Span | 트레이스를 구성하는 최소 작업 단위. 시작·종료 시각, 속성(attribute), 상태를 가진다. |
| Trace | 하나의 요청이 여러 서비스를 거치며 생성한 span들의 트리(부모-자식 관계) 전체. |
| Trace Context Propagation | 서비스 경계를 넘어 trace ID/span ID를 전파하는 표준(W3C Trace Context 등). 분산 트레이싱이 성립하는 전제 조건이다. |
| Head-based Sampling | 트레이스 시작 시점에 샘플링 여부를 결정하는 방식. 구현이 단순하지만 희귀한 에러 트레이스를 놓칠 수 있다. |
| Tail-based Sampling | 트레이스가 완전히 끝난 뒤 전체를 보고 샘플링 여부를 결정하는 방식. 에러·고지연 트레이스를 우선 보존할 수 있지만 버퍼링 비용이 든다. |
| TraceQL | Tempo의 트레이스 질의 언어. span 속성, duration, 구조적 관계(descendant, child 등)로 필터링한다. |
| Span Metrics | span 데이터로부터 RED 스타일 메트릭(요청률, 에러율, 지연 히스토그램)을 자동 파생하는 기능. |
| Baggage | trace context와 함께 서비스 경계를 넘어 전파되는 임의의 key-value 데이터. |

## 프로파일

| 용어 | 설명 |
|---|---|
| pprof | Go 생태계에서 시작된 프로파일 데이터 포맷/도구 모음. CPU·메모리 프로파일의 사실상 표준 포맷이다. |
| 플레임그래프(Flame Graph) | 스택 트레이스 샘플을 함수 호출 계층으로 시각화한 그래프. 너비가 곧 리소스 소비 비중을 나타낸다. |
| eBPF | 커널을 재컴파일하지 않고 커널 내부에서 안전하게 코드를 실행하는 리눅스 기술. 무계측(zero-instrumentation) 프로파일링·네트워킹·보안 관측에 쓰인다. |
| 연속 프로파일링(Continuous Profiling) | 특정 시점의 스냅샷이 아니라 상시 낮은 오버헤드로 프로파일을 수집·저장해 시계열처럼 조회하는 방식. |

## 컴포넌트

| 용어 | 설명 |
|---|---|
| Prometheus | 메트릭을 pull 방식으로 스크레이핑하고 PromQL로 질의하는 오픈소스 모니터링 시스템. LGTM+ 스택의 메트릭 수집 계층이다. |
| Mimir | Prometheus `remote_write`를 수신해 메트릭을 수평 확장·장기 저장하는 Grafana Labs의 백엔드. |
| Loki | 라벨 인덱스만 저장해 저비용으로 로그를 다루는 Grafana Labs의 로그 백엔드. |
| Tempo | 오브젝트 스토리지 기반으로 트레이스를 저장하고 TraceQL로 질의하는 Grafana Labs의 트레이스 백엔드. |
| Pyroscope | 연속 프로파일 데이터를 수집·저장·조회하는 Grafana Labs의 프로파일 백엔드. |
| Alloy | Grafana Agent의 후속 수집 에이전트. 컴포넌트 그래프 기반 파이프라인으로 메트릭·로그·트레이스·프로파일을 한 번에 수집·라우팅한다. |
| OTel Collector | OpenTelemetry Collector. 벤더 중립적인 프로토콜(OTLP)로 텔레메트리를 수집·가공·내보내는 파이프라인 컴포넌트. |
| Alertmanager | Prometheus 룰 평가 결과를 라우팅·그룹핑·억제한 뒤 알림 채널로 전달하는 컴포넌트. |
| Grafana Operator | Kubernetes CRD로 Grafana 인스턴스·데이터소스·대시보드·알림 규칙을 선언적으로 관리하는 Operator 패턴 구현체. |

[PromQL/LogQL/TraceQL 치트시트](/study/observability/appendix-cheatsheet)에서는 여기 정리한 용어가 실제 쿼리로 어떻게 쓰이는지 이어서 다룬다.
