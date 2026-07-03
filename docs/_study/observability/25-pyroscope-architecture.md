---
title: "Pyroscope 아키텍처"
description: "Grafana Phlare와 Pyroscope의 병합 역사, push/pull 수집 경로와 SDK·Alloy의 역할, 오브젝트 스토리지·심볼 DB 기반 저장 구조, 프로파일 병합 질의 방식, monolithic/microservices 배포 모드와 카디널리티·비용 관리까지 Pyroscope의 구조를 다룬다."
date: 2026-07-02
tags: [Pyroscope, Profiling, Architecture]
prev: /study/observability/24-continuous-profiling-basics
next: /study/observability/26-profile-types-ebpf
---

# Pyroscope 아키텍처

::: info 학습 목표
- Pyroscope와 Grafana Phlare가 병합된 배경과 그 결과로 만들어진 현재 아키텍처를 이해한다.
- 프로파일 수집이 push 중심이면서도 Alloy를 통해 pull(스크레이핑) 방식도 지원하는 구조를 안다.
- 오브젝트 스토리지와 심볼 DB를 활용한 저장 구조를 파악한다.
- 프로파일 질의가 "시간 범위 내 프로파일 병합"이라는 점과, monolithic/microservices 배포 모드의 차이를 이해한다.
:::

## 1. Pyroscope 개요 — Grafana Phlare 병합 역사

<strong>Pyroscope</strong>는 원래 독립 오픈소스 프로젝트로 시작된 연속 프로파일링 도구다. 로컬 스토리지(Badger 기반) 위에서 동작하며 다양한 언어 SDK와 직관적인 플레임그래프 UI로 초기 사용자를 확보했다. 한편 Grafana Labs는 2022년 자체적으로 <strong>Phlare</strong>라는 프로파일링 백엔드를 개발했는데, 이는 Mimir·Loki·Tempo와 동일한 설계 철학 — 오브젝트 스토리지 기반, ingester/querier/compactor로 구성된 수평 확장 가능한 마이크로서비스 아키텍처 — 을 프로파일 데이터에 적용한 것이었다.

2023년, Grafana Labs는 Pyroscope 팀과 합류해 두 프로젝트를 하나로 통합했다. 결과물은 <strong>Pyroscope라는 이름</strong>을 유지하되(사용자 친화적인 SDK·UX 자산을 계승), <strong>내부 저장 엔진은 Phlare의 확장 가능한 아키텍처</strong>를 물려받은 형태다. 그래서 지금의 [Grafana Pyroscope](https://grafana.com/docs/pyroscope/latest/)는 Mimir/Loki/Tempo와 같은 계열의 컴포넌트 구성(distributor, ingester, querier, store-gateway, compactor)을 갖는다 — LGTM+ 스택 안에서 아키텍처적으로 가장 뒤늦게 정착했지만 가장 일관된 설계를 갖춘 컴포넌트인 셈이다.

![오픈소스 Pyroscope의 SDK·UX와 Grafana Phlare의 오브젝트 스토리지 아키텍처가 2023년 병합돼 Pyroscope 이름에 Phlare 아키텍처를 물려받은 Grafana Pyroscope가 된 역사](/images/study-observability/25-phlare-merge.png)

## 2. 수집 — push vs pull, SDK, Alloy

Pyroscope의 기본 수집 모델은 <strong>push</strong>다. 애플리케이션에 언어별 SDK(Go `pyroscope-go`, Java 에이전트, Python `pyroscope_io`, Ruby, .NET, Rust 등)를 붙이면, SDK가 주기적으로(기본 10~15초 간격) 프로파일을 pprof 포맷으로 직렬화해 Pyroscope 서버의 HTTP 수신 엔드포인트로 밀어 넣는다. 이는 Loki가 로그를 push로 받는 것과 같은 패턴이며, Prometheus의 pull 모델과 대비된다([04장](/study/observability/04-pull-push-cardinality) 참고).

동시에 <strong>Alloy</strong>는 pull(스크레이핑) 경로도 지원한다. `pyroscope.scrape` 컴포넌트는 Go의 `net/http/pprof` 같은 표준 pprof 엔드포인트를 Prometheus 스크레이핑처럼 주기적으로 긁어와 Pyroscope로 전달할 수 있다. 즉 애플리케이션이 이미 pprof 엔드포인트를 노출하고 있다면 SDK 없이도 Alloy만으로 수집 파이프라인을 구성할 수 있다.

![Pyroscope의 세 수집 경로: 언어별 SDK가 주기적 HTTP push로 distributor에 직접 보내는 push 경로, /debug/pprof 엔드포인트를 pyroscope.scrape로 긁어 Alloy가 pyroscope.write로 전달하는 pull 경로, eBPF 무계측 수집이 Alloy를 경유하는 경로](/images/study-observability/25-push-pull-collection.png)

eBPF 기반 무계측 수집(`pyroscope.ebpf`)도 Alloy를 경유하는 세 번째 경로인데, 이는 언어 SDK 계측 없이 시스템 전체 프로세스를 프로파일링하는 방식으로 [26장](/study/observability/26-profile-types-ebpf)에서 자세히 다룬다. Alloy의 컴포넌트 그래프 개념 자체는 [28장](/study/observability/28-alloy-overview)에서 다룬다.

## 3. 저장 구조 — 오브젝트 스토리지, 심볼 DB

Phlare 병합 이후 Pyroscope의 저장 구조는 다른 Grafana 백엔드와 동일한 패턴을 따른다. <strong>ingester</strong>가 들어온 프로파일을 메모리에 임시 보관하다 블록(block) 단위로 플러시하고, 이 블록을 <strong>오브젝트 스토리지</strong>(S3, GCS, Azure Blob 등)에 업로드한다. <strong>compactor</strong>는 작은 블록들을 주기적으로 병합해 조회 효율을 높이고 오래된 데이터를 보존 정책에 따라 정리한다.

프로파일 고유의 저장 컴포넌트로 <strong>심볼 DB(symbol database)</strong>가 있다. 특히 eBPF 기반 프로파일처럼 바이너리 주소만 캡처되고 함수 이름이 즉시 붙지 않는 경우, 주소를 함수 이름·소스 라인으로 변환하는 심볼라이제이션 정보(ELF 심볼 테이블, 디버그 정보)를 별도로 캐싱해둔다. 이렇게 하면 매 질의마다 원본 바이너리를 다시 읽어 심볼을 재해석할 필요가 없어 질의 지연을 크게 줄인다.

![distributor에서 ingester(메모리 버퍼)로 유입된 프로파일이 블록으로 오브젝트 스토리지에 플러시되고 compactor가 병합·정리하며, store-gateway를 거쳐 querier가 질의하고 ingester가 심볼 DB에 심볼 정보를 저장해 querier 질의 시 주소를 함수명으로 변환하는 저장 구조](/images/study-observability/25-storage-architecture.png)

## 4. 질의 — 프로파일 병합, 시간 범위

프로파일 질의는 메트릭의 시계열 질의나 트레이스의 단건 조회와 결이 다르다. 사용자가 요청하는 것은 대개 "이 서비스의, 이 시간 범위 동안의 CPU 프로파일 하나"이고, 그 응답을 만들려면 <strong>해당 시간 범위에 속하는 수백~수천 개의 개별 프로파일 샘플을 하나로 병합(merge)</strong>해야 한다. 동일한 콜 스택을 가진 샘플들의 값을 합산하면서, 시간 범위 전체를 대표하는 단일 집계 프로파일이 만들어진다. 이 병합된 결과가 UI에서 플레임그래프로 렌더링될 "flamebearer" 데이터가 된다.

라벨(예: `service_name`, `env`, `version`)로 프로파일 시리즈를 선택하고, 시간 범위와 프로파일 타입(`process_cpu`, `memory:alloc_space` 등)을 지정하는 질의 형태는 Prometheus의 라벨 매처와 유사하다. 두 시점의 프로파일을 각각 병합한 뒤 나란히 비교하는 diff 질의도 지원하는데, 이는 [27장](/study/observability/27-flamegraph-trace-integration)에서 회귀 진단 워크플로우로 다룬다.

## 5. 배포 모드 — monolithic / microservices

Pyroscope는 Mimir·Loki와 마찬가지로 두 가지 배포 모드를 제공한다.

| 모드 | 구성 | 적합한 규모 |
|---|---|---|
| monolithic | 모든 컴포넌트(distributor, ingester, querier, compactor 등)가 단일 바이너리/프로세스로 실행 | 소규모 팀, PoC, 단일 노드 운영 |
| microservices | 컴포넌트별로 별도 프로세스/파드로 분리 배포, 각각 독립적으로 스케일 | 대규모 트래픽, 컴포넌트별 독립 스케일링·장애 격리가 필요한 프로덕션 |

monolithic 모드는 운영 부담이 적어 시작하기 쉽지만, 특정 컴포넌트(예: ingester)만 부하가 몰려도 전체 프로세스를 함께 스케일해야 하는 비효율이 있다. microservices 모드는 컴포넌트를 독립적으로 수평 확장할 수 있어 대규모 환경에 적합하지만, 운영 복잡도(컴포넌트 간 네트워킹, 각각의 리소스 튜닝)가 늘어난다. Kubernetes 환경에서는 보통 monolithic으로 시작해 트래픽이 늘어나면 microservices로 전환하는 경로를 택한다.

![monolithic 모드는 모든 컴포넌트를 단일 프로세스로 실행하고, 트래픽이 늘면 distributor·ingester·querier·compactor를 각각 N개로 복제해 독립 스케일하는 microservices 모드로 전환하는 두 배포 모드 대비](/images/study-observability/25-deployment-modes.png)

## 6. 카디널리티·비용 관리

프로파일도 메트릭과 마찬가지로 <strong>라벨 카디널리티</strong>가 비용의 핵심 변수다. `service_name`, `env`처럼 값의 종류가 적은 라벨은 안전하지만, 요청 ID·사용자 ID처럼 유일값이 많은 값을 라벨로 붙이면 프로파일 시리즈 수가 폭발해 저장·질의 비용이 급격히 늘어난다. 이 문제의 일반론은 [4장](/study/observability/04-pull-push-cardinality)과 [34장 카디널리티 관리와 비용](/study/observability/34-cardinality-cost)에서 다룬다.

프로파일 특유의 비용 변수도 있다. 샘플링 주기가 촘촘할수록([24장](/study/observability/24-continuous-profiling-basics) 참고) 수집되는 데이터 양이 늘고, 프로파일 타입을 여러 개(CPU, alloc, inuse, goroutine 등) 동시에 수집하면 그만큼 저장량이 배로 늘어난다. 실무에서는 서비스 중요도에 따라 수집할 프로파일 타입을 선별하고, 보존 기간을 메트릭보다 짧게(예: 수 주 단위) 설정해 비용을 통제하는 것이 일반적이다.

::: tip 핵심 정리
- 현재의 Grafana Pyroscope는 오픈소스 Pyroscope의 이름과 SDK·UX를, Grafana Phlare의 오브젝트 스토리지 기반 아키텍처를 물려받아 2023년 병합된 결과물이다.
- 수집은 SDK를 통한 push가 기본이지만, Alloy의 `pyroscope.scrape`로 pprof 엔드포인트를 pull(스크레이핑)하거나 `pyroscope.ebpf`로 무계측 수집도 가능하다.
- 저장은 ingester → 오브젝트 스토리지 → compactor로 이어지는 블록 구조이며, 심볼 DB가 주소-함수명 변환을 캐싱해 질의 지연을 줄인다.
- 질의는 시간 범위 내 프로파일들을 하나로 병합하는 연산이며, 두 시점을 비교하는 diff 질의도 지원한다.
- 소규모는 monolithic, 대규모·독립 스케일링이 필요하면 microservices 배포 모드를 선택한다.
- 프로파일 카디널리티는 라벨 설계뿐 아니라 샘플링 주기·수집 프로파일 타입 개수에도 좌우되므로 함께 관리해야 한다.
:::

## 다음 챕터

Pyroscope의 전체 구조를 이해했다면, 다음은 실제로 어떤 종류의 프로파일을 어떻게 수집하는지 볼 차례다. [프로파일 타입과 eBPF](/study/observability/26-profile-types-ebpf)에서는 CPU/메모리/goroutine/lock 프로파일 타입, 언어별 SDK 계측 방식, 그리고 eBPF 기반 무계측 프로파일링의 원리와 한계를 다룬다.
