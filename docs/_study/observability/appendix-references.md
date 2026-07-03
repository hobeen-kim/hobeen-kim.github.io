---
title: "참고 자료"
description: "관측성 학습을 이어갈 공식 문서와 표준, SRE·RED·USE 방법론 원출처, 심화 도서와 커뮤니티 큐레이션 링크 모음. Prometheus/Grafana/Loki/Tempo/Pyroscope/Mimir/Alloy 공식 docs와 OpenTelemetry, CNCF 자료를 카테고리별로 정리했다."
date: 2026-07-02
tags: [Observability, References]
prev: /study/observability/appendix-cheatsheet
next: false
---

# 참고 자료

스터디를 마친 뒤 더 깊이 파고들 수 있는 공식 문서·표준·심화 자료를 카테고리별로 모았다. 1차 출처는 언제나 공식 문서이므로 그것부터 둔다.

## Prometheus

- [Prometheus Documentation](https://prometheus.io/docs/introduction/overview/) — 전체 문서의 진입점
- [Querying (PromQL)](https://prometheus.io/docs/prometheus/latest/querying/basics/) — PromQL 문법·함수 레퍼런스
- [Metric and Label Naming](https://prometheus.io/docs/practices/naming/) — 메트릭·라벨 네이밍 모범 사례
- [Storage](https://prometheus.io/docs/prometheus/latest/storage/) — TSDB·WAL 내부 구조
- [Alerting Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/) — 룰 설정 레퍼런스
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/) — 라우팅·그룹핑·억제 설정

## Grafana

- [Grafana Documentation](https://grafana.com/docs/grafana/latest/) — 대시보드·데이터소스·Provisioning 전체 문서
- [Dashboard as Code (grafonnet)](https://grafana.github.io/grafonnet/) — jsonnet 기반 대시보드 정의
- [Grafana Operator](https://grafana.github.io/grafana-operator/) — Kubernetes CRD로 Grafana 리소스를 선언적으로 관리

## Loki

- [Loki Documentation](https://grafana.com/docs/loki/latest/) — 아키텍처·설치·운영 전체 문서
- [LogQL](https://grafana.com/docs/loki/latest/query/) — 로그·메트릭 쿼리 언어 레퍼런스
- [Loki Storage](https://grafana.com/docs/loki/latest/operations/storage/) — 오브젝트 스토리지 백엔드 구성

## Tempo

- [Tempo Documentation](https://grafana.com/docs/tempo/latest/) — 아키텍처·설치·운영 전체 문서
- [TraceQL](https://grafana.com/docs/tempo/latest/traceql/) — 트레이스 쿼리 언어 레퍼런스
- [Metrics-generator (span metrics)](https://grafana.com/docs/tempo/latest/metrics-generator/) — span으로부터 메트릭을 파생하는 컴포넌트

## Pyroscope

- [Pyroscope Documentation](https://grafana.com/docs/pyroscope/latest/) — 아키텍처·설치·운영 전체 문서
- [Continuous Profiling Concepts](https://grafana.com/docs/pyroscope/latest/introduction/) — 연속 프로파일링 기본 개념
- [eBPF Profiling](https://grafana.com/docs/pyroscope/latest/configure-client/grafana-agent/ebpf/) — 무계측 eBPF 프로파일링 설정

## Mimir

- [Mimir Documentation](https://grafana.com/docs/mimir/latest/) — 아키텍처·설치·운영 전체 문서
- [Mimir Architecture](https://grafana.com/docs/mimir/latest/references/architecture/) — 수평 확장 컴포넌트 구조
- [Configuring Tenants and Limits](https://grafana.com/docs/mimir/latest/configure/configure-tenant-ids/) — 멀티테넌시·리밋 설정

## Alloy

- [Alloy Documentation](https://grafana.com/docs/alloy/latest/) — 컴포넌트 모델·파이프라인 전체 문서
- [Alloy Component Reference](https://grafana.com/docs/alloy/latest/reference/components/) — 컴포넌트별 설정 레퍼런스
- [Migrate from Grafana Agent](https://grafana.com/docs/alloy/latest/set-up/migrate/) — River→Alloy 구문 마이그레이션 가이드

## 생태계 확장 — Beyla · Faro · k6 · Alerting

- [Beyla Documentation](https://grafana.com/docs/beyla/latest/) — eBPF 자동 계측 설정·배포 전체 문서
- [OpenTelemetry eBPF Instrumentation (OBI)](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation) — Beyla 코어가 기증된 OTel upstream 프로젝트
- [Faro Web SDK](https://grafana.com/docs/grafana-cloud/monitor-applications/frontend-observability/faro-web-sdk/) — 프런트엔드 관측성 SDK 문서
- [Alloy faro.receiver](https://grafana.com/docs/alloy/latest/reference/components/faro/faro.receiver/) — Faro 신호 수집 컴포넌트 레퍼런스
- [k6 Documentation](https://grafana.com/docs/k6/latest/) — 부하 테스트 시나리오·executor·thresholds 전체 문서
- [Grafana Synthetic Monitoring](https://grafana.com/docs/grafana-cloud/testing/synthetic-monitoring/) — 글로벌 프로브·check 유형 문서
- [Grafana Alerting](https://grafana.com/docs/grafana/latest/alerting/) — 통합 알림 룰·notification policy 문서
- [Grafana IRM](https://grafana.com/docs/grafana-cloud/alerting-and-irm/irm/) — 온콜·에스컬레이션·인시던트 대응 문서

## OpenTelemetry

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/) — SDK·Collector·계측 표준 전체 문서
- [OTel Collector](https://opentelemetry.io/docs/collector/) — Receiver/Processor/Exporter 파이프라인 구성
- [Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/) — 속성·메트릭 이름 표준화 스펙

## SRE·RED·USE 원출처

- [Site Reliability Engineering (Google SRE Book)](https://sre.google/sre-book/table-of-contents/) — SLI/SLO/에러 버짓 개념의 원전
- [The Site Reliability Workbook](https://sre.google/workbook/table-of-contents/) — SLO 실전 적용 사례집
- [The RED Method: key metrics for microservices](https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture/) — Tom Wilkie가 제안한 RED 메소드 원문
- [The USE Method](https://www.brendangregg.com/usemethod.html) — Brendan Gregg가 제안한 USE 메소드 원문

## CNCF·생태계

- [Cloud Native Computing Foundation](https://www.cncf.io/) — 클라우드 네이티브 생태계를 관장하는 재단
- [CNCF Landscape](https://landscape.cncf.io/) — 관측성 포함 클라우드 네이티브 도구 지도
- [OpenMetrics](https://openmetrics.io/) — Prometheus exposition format을 표준화한 CNCF 스펙

## 커뮤니티 큐레이션·심화 도서

- [Awesome Prometheus](https://github.com/roaldnefs/awesome-prometheus) — Exporter·도구·자료 큐레이션 리스트
- [Awesome Prometheus Alerts](https://samber.github.io/awesome-prometheus-alerts/) — 알림 규칙 예제 모음
- [PromLabs Blog](https://promlabs.com/blog/) — PromQL 심화·성능 관련 글
- [Prometheus: Up & Running (O'Reilly)](https://www.oreilly.com/library/view/prometheus-up/9781492034131/) — Prometheus 실전 운영서
- [Distributed Tracing in Practice (O'Reilly)](https://www.oreilly.com/library/view/distributed-tracing-in/9781492056621/) — 분산 트레이싱 설계·운영 심화서
- [Learning eBPF (O'Reilly)](https://www.oreilly.com/library/view/learning-ebpf/9781098135119/) — eBPF 기반 프로파일링·관측 심화서

이것으로 관측성 스터디 전체를 마친다. 4대 신호를 각각의 전용 백엔드로 다루는 법부터 Alloy로 파이프라인을 통합하고 Grafana로 상관관계를 엮는 법, 그리고 카디널리티·HA·멀티테넌시 같은 운영 심화 주제까지 훑었다. 본문으로 돌아가려면 [스터디 목차](/study/observability/)를 참고한다.
