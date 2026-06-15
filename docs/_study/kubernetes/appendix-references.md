---
title: "부록 C. 참고 자료"
description: "쿠버네티스·컨테이너 학습을 이어갈 공식 문서, 표준 스펙, 심화 자료 링크 모음. 쿠버네티스 공식 docs 주요 섹션, Docker, CNCF, OCI 스펙, Helm/Argo CD/Istio, 주요 KEP·블로그를 카테고리별로 정리했다."
date: 2026-06-15
tags: [Kubernetes, References, Documentation, Links]
prev: /study/kubernetes/appendix-glossary
next: false
---

# 부록 C. 참고 자료

스터디를 마친 뒤 더 깊이 파고들 수 있는 공식 문서·표준·심화 자료를 카테고리별로 모았다. 1차 출처는 언제나 공식 문서이므로 그것부터 둔다.

## 쿠버네티스 공식 문서 — 주요 섹션

- [Kubernetes Documentation (홈)](https://kubernetes.io/docs/home/) — 전체 문서의 진입점
- [Concepts](https://kubernetes.io/docs/concepts/) — 아키텍처·오브젝트·동작 원리 개념 전반
- [Workloads](https://kubernetes.io/docs/concepts/workloads/) — Pod와 워크로드 컨트롤러
- [Services, Load Balancing, and Networking](https://kubernetes.io/docs/concepts/services-networking/) — Service·Ingress·네트워크 정책
- [Storage](https://kubernetes.io/docs/concepts/storage/) — Volume·PV·PVC·StorageClass·CSI
- [Configuration](https://kubernetes.io/docs/concepts/configuration/) — ConfigMap·Secret·리소스 관리
- [Security](https://kubernetes.io/docs/concepts/security/) — 보안 개념 전반
- [Authentication / Authorization (RBAC)](https://kubernetes.io/docs/reference/access-authn-authz/) — 인증·인가·RBAC
- [Scheduling, Preemption and Eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/) — 스케줄러·affinity·taint
- [Extending Kubernetes (CRD/Operator)](https://kubernetes.io/docs/concepts/extend-kubernetes/) — CRD·API 확장·Operator
- [Tasks](https://kubernetes.io/docs/tasks/) — 목적별 실습 가이드 모음
- [Debug Application / Cluster](https://kubernetes.io/docs/tasks/debug/) — 트러블슈팅 절차
- [Reference (API / kubectl)](https://kubernetes.io/docs/reference/) — API 레퍼런스와 kubectl 명령어
- [kubectl Cheatsheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/) — 공식 kubectl 치트시트
- [Standardized Glossary](https://kubernetes.io/docs/reference/glossary/) — 공식 용어집
- [Production-Grade Container Orchestration](https://kubernetes.io/) — 프로젝트 메인

## 컨테이너 / Docker

- [Docker Documentation](https://docs.docker.com/) — Docker 전체 문서
- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/) — Dockerfile 명령어 레퍼런스
- [Building best practices](https://docs.docker.com/build/building/best-practices/) — 이미지 빌드 모범 사례
- [Docker Compose](https://docs.docker.com/compose/) — 로컬 멀티 컨테이너 구성
- [containerd](https://containerd.io/docs/) — 대표적인 컨테이너 런타임
- [CRI-O](https://cri-o.io/) — 쿠버네티스 전용 경량 런타임

## 표준 / 스펙

- [OCI (Open Container Initiative)](https://opencontainers.org/) — 컨테이너 표준화 단체
- [OCI Image Spec](https://github.com/opencontainers/image-spec) — 이미지 포맷 표준
- [OCI Runtime Spec](https://github.com/opencontainers/runtime-spec) — 런타임 표준
- [CNI (Container Network Interface)](https://github.com/containernetworking/cni) — 네트워크 플러그인 표준
- [CSI (Container Storage Interface)](https://github.com/container-storage-interface/spec) — 스토리지 플러그인 표준
- [Kubernetes API Reference](https://kubernetes.io/docs/reference/kubernetes-api/) — 모든 API 오브젝트 스펙

## CNCF / 생태계

- [Cloud Native Computing Foundation](https://www.cncf.io/) — 클라우드 네이티브 생태계를 관장하는 재단
- [CNCF Landscape](https://landscape.cncf.io/) — 클라우드 네이티브 도구 지도
- [CNCF Projects](https://www.cncf.io/projects/) — 졸업·인큐베이팅 프로젝트 목록
- [12-Factor App](https://12factor.net/) — 클라우드 네이티브 애플리케이션 설계 원칙

## 패키징 / GitOps / 서비스 메시

- [Helm](https://helm.sh/docs/) — 쿠버네티스 패키지 매니저
- [Kustomize](https://kustomize.io/) — 매니페스트 오버레이 기반 커스터마이징
- [Argo CD](https://argo-cd.readthedocs.io/) — 선언적 GitOps 지속적 배포
- [Argo Workflows](https://argo-workflows.readthedocs.io/) — 쿠버네티스 네이티브 워크플로 엔진
- [Istio](https://istio.io/latest/docs/) — 대표적인 서비스 메시
- [Cilium](https://docs.cilium.io/) — eBPF 기반 CNI·네트워크 보안
- [cert-manager](https://cert-manager.io/docs/) — 인증서 자동 발급·갱신
- [Prometheus](https://prometheus.io/docs/) — 모니터링·알림 표준 도구

## 심화 — KEP / 블로그 / 학습 자료

- [Kubernetes Enhancement Proposals (KEP)](https://github.com/kubernetes/enhancements/tree/master/keps) — 기능 제안·설계 문서 저장소
- [Kubernetes Blog](https://kubernetes.io/blog/) — 릴리스 노트·심화 글
- [Kubernetes Community](https://github.com/kubernetes/community) — SIG·기여 가이드
- [The Kubernetes Book / Resources 모음 (CNCF)](https://www.cncf.io/online-programs/) — CNCF 온라인 프로그램·웨비나
- [Kubernetes the Hard Way](https://github.com/kelseyhightower/kubernetes-the-hard-way) — 클러스터를 수작업으로 구성하며 내부를 이해하는 실습 자료
- [Kubernetes Failure Stories](https://k8s.af/) — 실제 장애 사례 모음. 트러블슈팅 학습에 유용

이것으로 부록과 스터디 전체를 마친다. 본문으로 돌아가려면 [스터디 목차](/study/kubernetes/)를 참고한다.
