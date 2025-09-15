---
title: "쿠버네티스에서 리소스 경합에 의한 Eviction 과 oom_killer 차이"
date: 2025-09-05
tags:
  - kubenetes
  - eviction
  - oom_killer
description: "두 파드 간에 메모리 등 리소스가 경합할 때 어떤 파드가 어떻게 꺼지고 축출되는지 알아보자"
---

<Header />

[[toc]]

클러스터의 리소스를 효율적으로 운영할수록 자원이 부족할 때 어떻게 행동할지가 중요해진다. 쿠버네티스는 **kubelet의 Node-pressure eviction**으로 노드 안정성을 지키고, **스케줄러의 파드 우선순위/선점(Pod priority & preemption)**으로 리소스가 부족해도 중요한 워크로드를 밀어 넣을 수 있게 한다. 두 메커니즘은 서로 맞물려 동작하므로, 함께 이해해야 운영 품질이 올라갈 수 있다.

# 노드-압박 축출(Node-pressure Eviction)

노드의 메모리/디스크/PID 등이 임계치에 다다르면, kubelet이 파드를 능동적으로 종료해 자원을 회수하고 노드 정체(Starvation)를 막는다. 이때 축출된 파드의 phase는 Failed로 바뀌며, PDB 나 terminationGracePeriodSeconds 를 존중하지 않을 수 있다.

## 의사결정의 입력값 - **축출 신호 & 임계값**

- 대표 신호 :  `memory.available`, `nodefs.available / inodesFree`, `imagefs.available / inodesFree`, (분리 구성 시) `containerfs.available / inodesFree`, `pid.available`
- **하드 임계값 기본값**(일부 OS별 상이) :  `memory.available<100Mi`(리눅스), `nodefs.available<10%`, `imagefs.available<15%`, `nodefs.inodesFree<5%`, `imagefs.inodesFree<5%`
- **소프트 임계값**은 **grace period**와 함께 지정하며, `eviction-soft`, `eviction-soft-grace-period`, `eviction-max-pod-grace-period`로 제어
- kubelet은 housekeeping-interval에 설정된 시간 간격(기본값: 10s)마다 축출 임계값을 확인한다. 노드 컨디션 토글 튐 방지는 `eviction-pressure-transition-period`(기본 `5m`)

> **PDB**
>
> PDB는 **Pod Disruption Budget**의 약자로, 쿠버네티스에서 자발적(Voluntary) 중단이 일어날 때, 한 번에 중단될 수 있는 파드 수를 제한해서 **가용성을 최소 보장**하는 정책이다.

**먼저 하는 일: 노드 레벨 회수 → 그래도 안 되면 파드 축출**

디스크 압박 시에는 죽은 파드/컨테이너부터 GC 을 진행하고, 사용하지 않는 이미지 삭제 순으로 정리한다.(파일시스템 구성이 nodefs / imagefs / containerfs냐에 따라 순서가 달라짐)

## 축출 순서

kubelet은 아래 기준으로 **순위를 매겨 축출**한다.

1. **요청치(request)를 초과**해서 리소스를 쓰는가
2. **파드 Priority**
3. **요청 대비 사용량 초과 정도**
    정리하면, **요청을 넘겨 쓰는 `BestEffort`/`Burstable` → (마지막) `Guaranteed`/요청 이내 `Burstable`** 순으로, 같은 급에서는 **Priority가 낮을수록 먼저** 나갑니다. QoS 클래스는 **순위 계산의 직접 입력은 아니지만**, 메모리 압박 상황에서 **예상 순서를 가늠하는 지표**가 됩니다. [Kubernetes](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)

> 주의: 시스템 데몬(`kubelet`, `journald`)이 예약치를 넘겨 쓰고, 남은 파드가 모두 `Guaranteed`/요청 이하라 해도 **노드 안정성**을 위해 **Priority가 가장 낮은 파드부터 축출**될 수 있다. 또한 **정적 파드**는 `priorityClassName`이 아닌 `priority` 필드를 직접 지정해야 한다.

### 축출 예시

1) **요청 초과 여부로 1차 후보군을 가른다**

노드 용량: **1 GiB**

| Pod  | QoS        | request | 사용량(usage) | 비고                                                         |
| ---- | ---------- | ------- | ------------- | ------------------------------------------------------------ |
| A    | Burstable  | 200Mi   | 150Mi         | **요청 이하**                                                |
| B    | Burstable  | 300Mi   | 700Mi         | **요청 초과 (+400Mi)**                                       |
| C    | BestEffort | 0       | 80Mi          | **요청 초과(+80Mi)** ← request=0이면 사용>0 즉시 초과로 간주 |

- 메모리 압박이 오면 kubelet은 **요청을 넘겨 쓰는 파드(B, C)**를 먼저 후보로 묶는다.
- 요청 이하로 쓰는 A는 **후순위**(보통 마지막까지 남음).

2) **같은 “요청 초과” 그룹 안에서는 PriorityClass가 낮은 것부터**

위 표에서 B와 C가 후보라고 가정하고, 우선순위를 이렇게 두게 된다.

| Pod  | PriorityClass | 설명                  |
| ---- | ------------- | --------------------- |
| B    | 1000          | 일반 업무 파드        |
| C    | 0             | 우선순위 미설정(기본) |

- 두 파드 모두 “요청 초과”라면, **우선순위가 더 낮은 C(0)**가 **먼저 축출 후보**가 된다.
- 만약 C가 더 높은 우선순위(예: 10000)를 갖고, B가 낮다면 **B가 먼저** 나간다.

> 요약: 같은 그룹(요청 초과) 안에서는 **낮은 Priority → 먼저 축출**.

3) **우선순위까지 같다면, (usage − request)가 큰 것부터**

두 파드의 Priority가 같다고 가정

| Pod  | request | usage | usage − request |
| ---- | ------- | ----- | --------------- |
| B    | 300Mi   | 700Mi | **+400Mi**      |
| C    | 0       | 80Mi  | **+80Mi**       |

- 둘 다 요청 초과 + 동일 Priority라면, **초과량이 더 큰 B(+400Mi)**가 **먼저 축출** 후보가 된다.
- 이 때문에 상황에 따라 **BestEffort(C)**보다 **Burstable(B)**이 먼저 나가는 **‘역전’**이 실제로 발생할 수 있다. (BestEffort가 항상 먼저인 건 아님)

## 파드 우선순위(Priority)와 선점(Preemption)

리소스가 모자라 **대기 중인 파드**가 생기면, 스케줄러는 **Priority가 더 낮은 파드들을 축출(선점)**해 **대기 중인 고 우선순위 파드**가 들어갈 공간을 만든다. 이를 쓰려면 먼저 `PriorityClass`를 만들고, 파드에 `priorityClassName`을 지정하면 된다. 쿠버네티스는 기본으로 `system-cluster-critical`, `system-node-critical` 클래스를 제공한다.

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 1000000
globalDefault: false
description: "핵심 서비스용"
```

> **선점하지 않는 우선순위**
>  `preemptionPolicy: Never`를 갖는 **Non-preempting PriorityClass**를 쓰면, **큐에서는 우선 배치되지만** 다른 파드를 밀어내지는 않는다. 긴 연산(job) 등에서 유용하다.

### 스케줄 순서와 선점 동작

- **대기 큐**는 Priority 높은 파드가 앞서고, 스케줄 요건을 만족하면 먼저 배치한다. 만족 못하면 다음 파드로 넘어간다.
- 선점이 트리거되면 스케줄러는 **한 노드에서 낮은 Priority 파드들을 골라 축출**해, 대기 파드가 들어갈 여지를 만든다. 이때 대기 파드의 `status.nominatedNodeName`이 표시될 수 있으나, 최종 스케줄 노드와 다를 수 있다.

### 한계와 주의점

- **유예 종료 시간**: 희생 파드는 **graceful termination**을 받고, 그 시간 동안은 자리 확보가 지연된다. 지나치게 길면 선점 효과가 약해진다.
- **PDB는 최대한 존중**: 스케줄러는 가능한 PDB를 침해하지 않으려 하지만, 불가피하면 PDB를 어기고서라도 선점할 수 있다.
- **크로스 노드 선점 없음**: 어떤 파드의 anti-affinity 때문에 **다른 노드의 파드**를 치워야만 스케줄 가능한 상황이라면, 현행 스케줄러는 그런 교차 노드 선점을 하지 않는다.

### QoS와의 관계

Priority와 QoS는 직교(orthogonal) 합니다. 선점 시 스케줄러는 QoS를 고려하지 않고 Priority만 보고 희생자를 고르지만, 노드-압박 축출에서는 Priority가 순위에 영향을 주며 QoS는 **예상 지표**로 볼 수 있다.

<Footer/>

# Ref.

- [노드-압박 축출](https://kubernetes.io/ko/docs/concepts/scheduling-eviction/node-pressure-eviction/)
- [파드 우선순위(priority)와 선점(preemption)](https://kubernetes.io/ko/docs/concepts/scheduling-eviction/pod-priority-preemption/)