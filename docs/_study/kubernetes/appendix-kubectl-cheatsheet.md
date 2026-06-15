---
title: "부록 A. kubectl 치트시트"
description: "자주 쓰는 kubectl 명령을 조회·생성/적용·디버깅·컨텍스트·리소스 관리·출력 포맷·JSONPath 카테고리별 표로 정리한다. 실무에서 바로 꺼내 쓰는 레퍼런스."
date: 2026-06-15
tags: [Kubernetes, kubectl, Cheatsheet, Reference]
prev: /study/kubernetes/47-practice
next: /study/kubernetes/appendix-glossary
---

# 부록 A. kubectl 치트시트

실무에서 자주 쓰는 `kubectl` 명령을 카테고리별로 정리한다. 공식 레퍼런스는 [kubectl 명령어 레퍼런스](https://kubernetes.io/docs/reference/kubectl/)와 [kubectl 치트시트](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)에 있다.

## 자동완성과 별칭 설정

먼저 이걸 깔아두면 모든 명령이 빨라진다.

```bash
# bash 자동완성
source <(kubectl completion bash)
echo 'source <(kubectl completion bash)' >> ~/.bashrc

# zsh 자동완성
source <(kubectl completion zsh)

# 별칭 — k 로 줄여 쓰고 자동완성도 연결
alias k=kubectl
complete -o default -F __start_kubectl k
```

## 조회 (get / describe)

| 작업 | 명령 |
|---|---|
| 모든 Pod 조회 | `kubectl get pods` |
| 전체 네임스페이스의 Pod | `kubectl get pods -A` |
| 특정 네임스페이스 | `kubectl get pods -n <ns>` |
| 넓은 출력(노드·IP 포함) | `kubectl get pods -o wide` |
| 라벨까지 표시 | `kubectl get pods --show-labels` |
| 라벨 셀렉터로 필터 | `kubectl get pods -l app=web` |
| 여러 리소스 한 번에 | `kubectl get deploy,svc,pod -n <ns>` |
| 한 리소스 상세(이벤트 포함) | `kubectl describe pod <pod>` |
| 변경 실시간 감시 | `kubectl get pods -w` |
| 정렬 | `kubectl get pods --sort-by=.metadata.creationTimestamp` |
| 노드 목록 | `kubectl get nodes -o wide` |
| 이벤트 시간순 | `kubectl get events --sort-by=.lastTimestamp` |
| API 리소스 종류 일람 | `kubectl api-resources` |

## 생성 / 적용 (apply / create)

| 작업 | 명령 |
|---|---|
| 매니페스트 적용(선언적) | `kubectl apply -f app.yaml` |
| 디렉터리 전체 적용 | `kubectl apply -f ./manifests/` |
| URL에서 적용 | `kubectl apply -f https://example.com/app.yaml` |
| 표준입력으로 적용 | `cat app.yaml \| kubectl apply -f -` |
| 네임스페이스 생성 | `kubectl create namespace <ns>` |
| Deployment 생성(명령형) | `kubectl create deployment web --image=nginx` |
| ConfigMap 생성 | `kubectl create configmap cfg --from-literal=key=val` |
| Secret 생성 | `kubectl create secret generic s --from-literal=pw=1234` |
| 적용될 변경 미리보기 | `kubectl diff -f app.yaml` |
| 실제 적용 없이 검증(서버) | `kubectl apply -f app.yaml --dry-run=server` |
| 매니페스트 골격 생성 | `kubectl create deployment web --image=nginx --dry-run=client -o yaml` |

`--dry-run=client -o yaml`은 매니페스트 초안을 손으로 짜지 않고 뽑아내는 데 가장 자주 쓴다.

## 수정 / 스케일 / 롤아웃

| 작업 | 명령 |
|---|---|
| 이미지 교체(롤링 업데이트) | `kubectl set image deploy/web web=nginx:1.27` |
| 레플리카 수 변경 | `kubectl scale deploy/web --replicas=5` |
| 에디터로 직접 수정 | `kubectl edit deploy/web` |
| 라벨 추가 | `kubectl label pod <pod> tier=frontend` |
| 어노테이션 추가 | `kubectl annotate pod <pod> note=demo` |
| JSON 패치 | `kubectl patch deploy/web -p '{"spec":{"replicas":3}}'` |
| 롤아웃 상태 확인 | `kubectl rollout status deploy/web` |
| 롤아웃 이력 | `kubectl rollout history deploy/web` |
| 롤백 | `kubectl rollout undo deploy/web` |
| 특정 리비전으로 롤백 | `kubectl rollout undo deploy/web --to-revision=2` |
| 롤아웃 재시작(Pod 재생성) | `kubectl rollout restart deploy/web` |

## 디버깅

| 작업 | 명령 |
|---|---|
| 로그 보기 | `kubectl logs <pod>` |
| 멀티 컨테이너 중 하나 | `kubectl logs <pod> -c <container>` |
| 실시간 follow | `kubectl logs -f <pod>` |
| 크래시 직전 로그 | `kubectl logs <pod> --previous` |
| 라벨로 여러 Pod 로그 | `kubectl logs -l app=web --tail=100` |
| 컨테이너 안에서 셸 | `kubectl exec -it <pod> -- sh` |
| 단일 명령 실행 | `kubectl exec <pod> -- env` |
| 임시 디버그 Pod | `kubectl run tmp --rm -it --image=busybox -- sh` |
| 디버그 컨테이너 주입 | `kubectl debug <pod> -it --image=busybox` |
| 로컬 포트 포워딩 | `kubectl port-forward svc/web 8080:80` |
| 파일 복사 | `kubectl cp <pod>:/path/file ./file` |
| 자원 사용량(metrics-server 필요) | `kubectl top pod` / `kubectl top node` |
| 권한 확인 | `kubectl auth can-i create pods -n <ns>` |

## 삭제 / 정리

| 작업 | 명령 |
|---|---|
| 리소스 삭제 | `kubectl delete pod <pod>` |
| 매니페스트로 삭제 | `kubectl delete -f app.yaml` |
| 라벨로 일괄 삭제 | `kubectl delete pods -l app=web` |
| 네임스페이스 통째 삭제 | `kubectl delete namespace <ns>` |
| 즉시 강제 삭제 | `kubectl delete pod <pod> --grace-period=0 --force` |

`--force`는 정상 종료 절차를 건너뛰므로 멈춘 Pod 정리 등 최후 수단으로만 쓴다.

## 컨텍스트 / 네임스페이스 전환

| 작업 | 명령 |
|---|---|
| 컨텍스트 목록 | `kubectl config get-contexts` |
| 현재 컨텍스트 | `kubectl config current-context` |
| 컨텍스트 전환 | `kubectl config use-context <ctx>` |
| 기본 네임스페이스 변경 | `kubectl config set-context --current --namespace=<ns>` |
| 클러스터 정보 | `kubectl cluster-info` |
| kubeconfig 경로 지정 | `kubectl --kubeconfig=/path/config get pods` |

매번 `-n`을 붙이기 번거로우면 `set-context --current --namespace`로 기본 네임스페이스를 바꿔두는 편이 낫다.

## 출력 포맷

| 포맷 | 명령 |
|---|---|
| YAML 전체 | `kubectl get pod <pod> -o yaml` |
| JSON 전체 | `kubectl get pod <pod> -o json` |
| 특정 필드만(컬럼) | `kubectl get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase` |
| 이름만 | `kubectl get pods -o name` |
| Go 템플릿 | `kubectl get pods -o go-template='{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}'` |

## JSONPath

복잡한 필드를 스크립트로 뽑을 때 쓴다. 자세한 문법은 [JSONPath 지원 문서](https://kubernetes.io/docs/reference/kubectl/jsonpath/)에 있다.

| 목적 | 명령 |
|---|---|
| 모든 Pod 이름 | `kubectl get pods -o jsonpath='{.items[*].metadata.name}'` |
| 각 Pod 이름 줄바꿈 | `kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}'` |
| 노드의 InternalIP | `kubectl get nodes -o jsonpath='{.items[*].status.addresses[?(@.type=="InternalIP")].address}'` |
| 컨테이너 이미지 목록 | `kubectl get pods -o jsonpath='{.items[*].spec.containers[*].image}'` |
| Secret 값 디코드 | `kubectl get secret s -o jsonpath='{.data.pw}' \| base64 -d` |
| 특정 라벨 값 | `kubectl get pods -o jsonpath='{.items[*].metadata.labels.app}'` |

## 자주 쓰는 진단 원라이너

```bash
# 네임스페이스 내 모든 리소스 한눈에
kubectl get all -n <ns>

# Pending/실패 Pod만 추려보기
kubectl get pods -A --field-selector=status.phase!=Running

# 이미지 버전 한 번에 점검
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].image}{"\n"}{end}'

# Service가 어떤 Pod를 잡고 있는지(엔드포인트)
kubectl get endpoints <svc> -n <ns>

# 노드별 자원 사용량 상위 정렬
kubectl top nodes --sort-by=cpu
```

다음 부록은 [용어집](/study/kubernetes/appendix-glossary)으로, 본문에 등장한 쿠버네티스·컨테이너 핵심 용어를 한 줄 설명으로 정리한다.
