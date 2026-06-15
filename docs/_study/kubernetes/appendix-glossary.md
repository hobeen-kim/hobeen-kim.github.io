---
title: "부록 B. 용어집"
description: "쿠버네티스와 컨테이너 핵심 용어를 한 줄 설명으로 정리한 레퍼런스. Pod·Node·Deployment·Service·Ingress·CNI·CSI·RBAC·CRD·Operator·etcd·kubelet 등 40여 개 용어를 카테고리별 표로 모았다."
date: 2026-06-15
tags: [Kubernetes, Glossary, Reference, Terminology]
prev: /study/kubernetes/appendix-kubectl-cheatsheet
next: /study/kubernetes/appendix-references
---

# 부록 B. 용어집

본문에 등장한 쿠버네티스·컨테이너 핵심 용어를 한 줄로 정리한다. 공식 정의는 [Kubernetes 표준 용어집](https://kubernetes.io/docs/reference/glossary/)을 함께 참고한다. 기술 용어는 원문 표기를 유지한다.

## 컨테이너 기반 기술

| 용어 | 한 줄 설명 |
|---|---|
| Container | 애플리케이션과 그 의존성을 격리해 실행하는 경량 실행 단위. 리눅스 namespace·cgroup으로 격리·자원 제한을 구현한다. |
| Image | 컨테이너를 실행하기 위한 읽기 전용 패키지. 레이어로 구성되며 레지스트리에 저장된다. |
| Dockerfile | 이미지를 빌드하기 위한 명령 절차를 적은 텍스트 파일. |
| Registry | 컨테이너 이미지를 저장·배포하는 저장소(예: Docker Hub, 사내 레지스트리). |
| OCI | Open Container Initiative. 이미지·런타임의 표준 스펙을 정의하는 단체이자 그 표준. |
| Container Runtime | 컨테이너를 실제로 실행하는 소프트웨어(예: containerd, CRI-O). |
| CRI | Container Runtime Interface. kubelet과 컨테이너 런타임 사이의 표준 인터페이스. |
| namespace (Linux) | 프로세스가 보는 시스템 자원(PID·네트워크·마운트 등)을 격리하는 커널 기능. 쿠버네티스 Namespace와 다름. |
| cgroup | 프로세스 그룹의 CPU·메모리 등 자원 사용을 제한·측정하는 커널 기능. |

## 클러스터 구성 요소

| 용어 | 한 줄 설명 |
|---|---|
| Cluster | 컨테이너화된 워크로드를 실행하는 노드의 집합. |
| Node | 워크로드(Pod)가 실제로 실행되는 워커 머신(가상/물리). |
| Control Plane | 클러스터의 상태를 관리·조율하는 구성 요소 묶음. |
| kube-apiserver | 모든 요청이 거치는 클러스터의 프런트엔드. REST API로 상태를 읽고 쓴다. |
| etcd | 클러스터의 모든 상태를 저장하는 분산 key-value 저장소. 사실상의 단일 진실 공급원. |
| kube-scheduler | 새 Pod를 어떤 노드에 배치할지 결정하는 구성 요소. |
| controller-manager | 컨트롤러들을 실행해 현재 상태를 원하는 상태로 수렴시키는 구성 요소. |
| kubelet | 각 노드에서 동작하며 할당된 Pod를 실제로 띄우고 상태를 보고하는 에이전트. |
| kube-proxy | 노드에서 Service의 가상 IP 라우팅·로드밸런싱을 처리하는 네트워크 프록시. |

## 워크로드 오브젝트

| 용어 | 한 줄 설명 |
|---|---|
| Pod | 하나 이상의 컨테이너를 묶은, 쿠버네티스에서 배포·스케줄링되는 최소 단위. |
| ReplicaSet | 지정한 수의 동일한 Pod가 항상 실행되도록 유지하는 컨트롤러. |
| Deployment | ReplicaSet 위에서 선언적 업데이트·롤백을 조율하는 stateless 워크로드 컨트롤러. |
| StatefulSet | 안정적인 식별자·순서·스토리지가 필요한 stateful 워크로드용 컨트롤러. |
| DaemonSet | 모든(또는 일부) 노드에 Pod를 하나씩 띄우는 컨트롤러. 로그·모니터링 에이전트에 쓴다. |
| Job | 한 번 실행되고 완료되면 끝나는 배치 작업용 오브젝트. |
| CronJob | 스케줄에 따라 Job을 반복 생성하는 오브젝트. |
| ReplicationController | ReplicaSet의 구형 버전. 현재는 Deployment/ReplicaSet 사용을 권장. |

## 설정 / 네트워킹 / 스토리지

| 용어 | 한 줄 설명 |
|---|---|
| Namespace (k8s) | 클러스터 안에서 리소스를 논리적으로 분리하는 가상 격리 단위. |
| ConfigMap | 비밀이 아닌 설정 데이터를 key-value로 저장하는 오브젝트. |
| Secret | 비밀번호·토큰 등 민감 데이터를 저장하는 오브젝트(base64 인코딩, 암호화 아님). |
| Service | 동적인 Pod 집합에 안정적인 단일 진입점(가상 IP)과 로드밸런싱을 제공하는 오브젝트. |
| Endpoints | Service가 트래픽을 보낼 실제 Pod IP·포트 목록. |
| Ingress | HTTP/HTTPS 트래픽을 호스트·경로 기준으로 Service에 라우팅하는 규칙. |
| Ingress Controller | Ingress 규칙을 실제로 처리하는 리버스 프록시(예: ingress-nginx). |
| CNI | Container Network Interface. Pod 네트워킹을 구현하는 플러그인 표준(예: Calico, Cilium). |
| Volume | Pod의 컨테이너가 마운트해 데이터를 저장하는 디렉터리. |
| PV (PersistentVolume) | 클러스터에 프로비저닝된 실제 스토리지 자원. |
| PVC (PersistentVolumeClaim) | 사용자가 스토리지를 요청하는 선언. PV에 바인딩된다. |
| StorageClass | 동적 PV 프로비저닝의 방식·파라미터를 정의하는 오브젝트. |
| CSI | Container Storage Interface. 외부 스토리지를 연결하는 플러그인 표준. |

## 보안 / 확장 / 운영

| 용어 | 한 줄 설명 |
|---|---|
| ServiceAccount | Pod 안 프로세스가 API 서버에 인증하는 데 쓰는 계정. |
| RBAC | Role-Based Access Control. Role/ClusterRole과 바인딩으로 권한을 부여하는 인가 모델. |
| Role / ClusterRole | 허용 동작(verb)과 대상 리소스를 정의하는 규칙 묶음. Role은 네임스페이스 범위, ClusterRole은 클러스터 범위. |
| RoleBinding | Role을 사용자·그룹·ServiceAccount에 연결하는 바인딩. |
| CRD | CustomResourceDefinition. 사용자가 새 리소스 종류를 API에 추가하는 정의. |
| Custom Resource | CRD로 추가된 사용자 정의 리소스의 인스턴스. |
| Operator | CRD와 컨트롤러를 결합해 특정 애플리케이션의 운영 지식을 코드로 자동화하는 패턴. |
| Controller | 현재 상태를 관찰해 원하는 상태로 맞추는 제어 루프. |
| Reconciliation | 컨트롤러가 현재 상태와 원하는 상태의 차이를 줄여 나가는 과정. |
| HPA | Horizontal Pod Autoscaler. 지표에 따라 Pod 수를 자동 조절하는 오브젝트. |
| Probe | 컨테이너 상태를 점검하는 진단(liveness·readiness·startup). |
| Taint / Toleration | 노드가 Pod를 밀어내는 표시(taint)와 그것을 견디는 Pod 설정(toleration). |
| Affinity | Pod를 특정 노드·Pod와 가깝게/멀게 배치하도록 유도하는 규칙. |
| Label / Selector | 리소스에 붙이는 key-value 메타데이터(label)와 그것으로 대상을 고르는 질의(selector). |
| Annotation | 식별·선택에 쓰지 않는 부가 메타데이터. 도구·라이브러리가 참조한다. |
| Manifest | 오브젝트의 원하는 상태를 기술한 YAML/JSON 파일. |
| Helm | 쿠버네티스 매니페스트를 템플릿화해 패키지(Chart)로 배포·관리하는 도구. |

다음 부록은 [참고 자료](/study/kubernetes/appendix-references)로, 공식 문서·표준·심화 학습 링크를 카테고리별로 모았다.
