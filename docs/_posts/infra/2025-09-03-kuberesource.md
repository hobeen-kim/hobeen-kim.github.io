---
title: "쿠버네티스 운영 환경 준비 하기 - 파드 리소스 할당"
date: 2025-09-04
tags:
  - kubenetes
  - resources
  - pod
description: "파드 리소스 사용량 제한 확인하기"

---

<Header />

[[toc]]

쿠버네티스로 배포된 서버를 운영하기 위한 마지막 단계 중 하나는 실제 부하를 테스트해보는 것이다. 테스트를 하기 전에 우선 파드별로 할당된 리소스가 적절한지 확인하려고 했다. 그리고 테스트 이후에 다시 평가할 예정이다.

파드별로 cpu, memory 리소스가 필요한만큼 제대로 분배되지 못하면 노드의 리소스는 남음에도 파드의 리소스 제한으로 인해 남은 노드의 리소스를 모두 못쓰거나, 과도한 오버커밋때문에 중요한 파드가 꺼질 수도 있다.

# 컨테이너와 파드 사용량 제한: Limits, requests

## Limits 와 Requests

쿠버네티스는 limits 키워드를 통해 자원 사용량의 최대치를 제한시키고, requests 로 자원의 최소치를 보장한다.

```yaml
apiVerision: v1
kind: Pod
metadata:
	name: limited-pod
spec:
	containers:
	- name: nginx
	  image: nginx
	  resources:
	    limits:
	      cpu: 1000m
	      memory: 512MiB
      requests:
	      cpu: 100m
	      memory: 128MiB
```

쿠버네티스는 컨테이너의 자원활용률을 높이기 위해 **오버커밋**을 사용한다. 오버커밋이란 한정된 컴퓨팅 자원을 효율적으로 사용하기 위한 방법으로 사용할 수 있는 자원보다 더 많은 양을 VM 또는 컨테이너에게 할당하는 것이다.

예를 들어 아래처럼 메모리가 1GiB 인 노드에 각각 requests, limits 가 400MiB, 700MiB 인 컨테이너(파드)가 2개 있다고 가정하자.

![image-20250904205438084](../../.vuepress/public/images/2025-09-03-kuberesource/image-20250904205438084.png)

물리적인 메모리는 1GiB 지만 A, B 각각에게 할당된 메모리의 합은 대략 **1.4GiB** 이다. 이처럼 유휴 자원이 남을 때 오버커밋을 통해 자원이 유동적으로 분배된다.

하지만 위와 같은 상황에서 A 컨테이너가 자신의 request 만큼 사용해야 한다면(자원의 경합) 어떤 일이 벌어질까?

## QoS 클래스

메모리는 압축불가능한(Incompressible) 자원으로 취급되기 때문에 메모리 사용량에 경합이 발생하면 우선순위가 낮은 파드를 강제 종료시킨다. 

여기서 중요한 부분은 **'메모리 자원 부족 시 어떤 파드가 먼저 종료돼야 하는가'**이다. 쿠버네티스는 Limits 와 Requests 값에 따라 우선순위를 정하는데 특히 3가지 종류의 QoS (Quality Of Service) 클래스가 파드별로 설정되어 활용된다.

> 쿠버네티스의 파드 Eviction 과 노드의 oom_killer 의 동작은 다르다. 파드 Eviction 시 QoS 는 고려되지 않는다.

### Guaranteed 클래스

### BestEffort 클래스

### Burstable 클래스



**복잡성을 늘리지 말자**

observability 에는 ResourceQuota 을 할당하지 않음 -> 노드가 늘어날 수록 생기는 daemonset 이 있기 떄문

---

### 안정적으로 B가 800MiB까지 쓰게 하려면

- B를 **Guaranteed QoS**로: `requests.memory = limits.memory = 800MiB`
- 또는 **PriorityClass**로 우선순위 부여(필요 시 preemption 허용)
- **노드 용량 증설**/전용 노드 배치(taint/toleration, nodeSelector)
- 네임스페이스에 **ResourceQuota**로 총합 가드, **LimitRange**로 기본값/상하한 정렬
   (과도한 overcommit 방지)



### 축출 

- Burstable 내에서는 요청(request)을 얼마나 초과해서 쓰는지가 큰 파드부터 우선 퇴출됩니다. (usage − request가 큰 순)
- Guaranteed는 가장 마지막에 퇴출 대상이지만, 노드가 심하게 부족하면 결국 퇴출될 수도 있습니다.
- **컨테이너 한도 초과(OOMKilled)**는 별개입니다. 컨테이너가 자신의 limit을 넘으면 QoS와 무관하게 즉시 OOMKilled 됩니다.
- PriorityClass가 설정돼 있으면, 우선 낮은 우선순위의 파드가 먼저 고려되고, 같은 우선순위끼리일 때 QoS 순서가 적용됩니다.



좋아요. kubelet이 **메모리 압박(eviction)** 때 파드 축출 대상을 고를 때, 보통 아래 **우선 기준(순서)**로 판단합니다:

1. “요청(request)을 초과해서 쓰는가?”
2. “파드 우선순위(PriorityClass)는 낮은가?”
3. “요청 대비 초과 사용량(usage − request)은 큰가?”

각 단계마다 **작동 예시**를 들어볼게요. (단위는 메모리)

------

## 1) 요청 초과 여부로 1차 후보군을 가른다

노드 용량: **1 GiB**

| Pod  | QoS        | request | 사용량(usage) | 비고                                                         |
| ---- | ---------- | ------- | ------------- | ------------------------------------------------------------ |
| A    | Burstable  | 200Mi   | 150Mi         | **요청 이하**                                                |
| B    | Burstable  | 300Mi   | 700Mi         | **요청 초과 (+400Mi)**                                       |
| C    | BestEffort | 0       | 80Mi          | **요청 초과(+80Mi)** ← request=0이면 사용>0 즉시 초과로 간주 |

- 메모리 압박이 오면 kubelet은 **요청을 넘겨 쓰는 파드(B, C)**를 먼저 후보로 묶습니다.
- 요청 이하로 쓰는 A는 **후순위**(보통 마지막까지 남음).

------

## 2) 같은 “요청 초과” 그룹 안에서는 **PriorityClass**가 낮은 것부터

위 표에서 B와 C가 후보라고 가정하고, 우선순위를 이렇게 둡니다:

| Pod  | PriorityClass | 설명                  |
| ---- | ------------- | --------------------- |
| B    | 1000          | 일반 업무 파드        |
| C    | 0             | 우선순위 미설정(기본) |

- 두 파드 모두 “요청 초과”라면, **우선순위가 더 낮은 C(0)**가 **먼저 축출 후보**가 됩니다.
- 만약 C가 더 높은 우선순위(예: 10000)를 갖고, B가 낮다면 **B가 먼저** 나갑니다.

> 요약: 같은 그룹(요청 초과) 안에서는 **낮은 Priority → 먼저 축출**.

------

## 3) 우선순위까지 같다면, **(usage − request)**가 큰 것부터

두 파드의 Priority가 같다고 가정:

| Pod  | request | usage | usage − request |
| ---- | ------- | ----- | --------------- |
| B    | 300Mi   | 700Mi | **+400Mi**      |
| C    | 0       | 80Mi  | **+80Mi**       |

- 둘 다 요청 초과 + 동일 Priority라면, **초과량이 더 큰 B(+400Mi)**가 **먼저 축출** 후보가 됩니다.
- 이 때문에 상황에 따라 **BestEffort(C)**보다 **Burstable(B)**이 먼저 나가는 **‘역전’**이 실제로 발생할 수 있습니다. (BestEffort가 항상 먼저인 건 아님)

------

### 추가 메모

- **Guaranteed**(request=limit)은 보통 **가장 마지막**에 축출됩니다.
- **OS 레벨 OOM Killer**가 개입하는 진짜 OOM 상황에서는 `oom_score_adj`(QoS/우선순위에 따라 다름)와 실제 사용량이 함께 작용해, **많이 쓰는 컨테이너**가 더 불리합니다.
- **CPU 부족**은 파드 축출 사유가 아니라 스로틀링으로 처리되는 점(주로 eviction은 메모리/디스크 압박)도 참고하세요.

**정리:** 우선순위가 낮아도 “요청 이하”이면 *덜 위험*할 뿐, **상황이 심하면 축출될 수 있습니다.**
 진짜 보호가 필요하면 `requests≈피크 사용`으로 잡아 **Guaranteed QoS**에 가깝게 하고, 필요한 경우 **PriorityClass**와 전용 노드(taints/tolerations)까지 고려하세요.