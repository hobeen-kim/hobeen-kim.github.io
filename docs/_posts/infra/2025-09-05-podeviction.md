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

먼저 하는 일: 노드 레벨 회수 → 그래도 안 되면 파드 축출

디스크 압박 시: 죽은 파드/컨테이너 GC → 사용하지 않는 이미지 삭제 순으로 정리(파일시스템 구성이 nodefs / imagefs / containerfs냐에 따라 순서가 달라짐)

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

<Footer/>