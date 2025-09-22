---
title: "쿠버네티스 무중단 RollingUpdate"
date: 2025-09-22
tags:
  - kubenetes
  - update
description: "쿠버네티스 무중단 배포"
---

<Header/>

[[toc]]

RollingUpdate 는 하나씩 파드를 교체하는 작업이다. 쿠버네티스 Deployment 리소스에서 다음과 같은 설정으로 RollingUpdate 를 할 수 있다.

```yaml
spec:
  selector:
    matchLabels:
      app: my-app
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: "1" # 롤링 업데이트 중 동시에 “사용 불가” 상태가 될 수 있는 파드의 최대치
      maxSurge: "1" # 롤링 업데이트 중 원하는 레플리카 수보다 “추가로” 생성될 수 있는 파드의 최대치
```

# 문제 상황

쿠버네티스에서 Deployment를 RollingUpdate 방식으로 업데이트하면 다음 순서로 진행된다.

1. 기존 Pod에 **SIGTERM** 신호가 전달된다.
2. Pod는 종료 절차를 밟는다.
3. 하지만 이 시점에도 로드밸런서(ALB)는 헬스체크가 200 ok 이므로 해당 Pod로 트래픽을 보낼 수 있다.
4. 결과적으로 종료 중인 Pod에 들어간 요청이 실패하면서 에러가 발생한다.

> 헬스체크가 200 ok 인 이유는 ALB 가 10초 동안 2번의 health check 를 실패해야 파드를 대상에서 제외하기 때문이다. 10초, 2번은 커스텀한 설정이다.

# 해결 전략

## Deployment Pod 의 종료 절차 순서

우선 Pod 의 종료 절차를 확인해보자.

1. **쿠버네티스가 Pod 종료 결정**

   - `kubectl delete pod`, `RollingUpdate`, Scale-in 등

2. **preStop hook 실행 (있다면)**

   - 먼저 정의된 `preStop` hook 실행

   - 이 hook이 끝날 때까지 **grace period 타이머도 함께 흐름**

3. **컨테이너에 SIGTERM 전달**

   - kubelet이 각 컨테이너 프로세스에 `SIGTERM` 시그널 전달

   - 이때 애플리케이션은 shutdown hook, `@PreDestroy`, Spring Boot의 `ContextClosedEvent` 등을 활용해 정리 로직 수행 가능

4. **grace period 대기 (`terminationGracePeriodSeconds`)**

   - Pod는 `Terminating` 상태로 바뀜

   - 설정한 초 수 만큼 애플리케이션이 정상적으로 종료할 시간을 줌

5. **시간 내 종료하지 않으면 SIGKILL**
   - `terminationGracePeriodSeconds` 안에 프로세스가 종료되지 않으면 kubelet이 `SIGKILL` 보내서 강제 종료

## 해결 방법

따라서 Pod 종료 시점에 다음 단계를 밟도록 한다.

1. **SIGTERM 전달 이후 Readiness 상태를 DOWN으로 변경**  
   - Pod가 더 이상 트래픽을 받지 않도록 한다.
2. **로드밸런서에서 Pod를 제거**  
   - readinessProbe 실패를 감지한 LB가 해당 Pod를 라우팅 대상에서 제외한다.
3. **진행 중인 요청은 마저 처리**  
   - `terminationGracePeriodSeconds` 동안 기존 요청을 안전하게 끝낸다.
4. **Pod 종료**  

## Spring Boot 3.5: ReadinessState 활용

Spring Boot 에서 `ReadinessState`, `LivenessState`를 기반으로 쿠버네티스와 잘 통합할 수 있다. 종료 이벤트 시 `ReadinessState.REFUSING_TRAFFIC` 으로 상태를 바꾸면 `/actuator/health/readiness`가 **DOWN** 을 반환한다.

> 아래 설정을 위해서 actuator 디펜던시를 추가해야 한다.

### 코드 예시

```java
import org.springframework.boot.availability.AvailabilityChangeEvent;
import org.springframework.boot.availability.ReadinessState;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;
import org.springframework.context.event.ContextClosedEvent;

@Component
public class ShutdownReadinessListener {

    @EventListener
    public void onShutdown(ContextClosedEvent event) {
        // Pod 종료 이벤트 시 readiness를 REFUSING_TRAFFIC으로 변경
        AvailabilityChangeEvent.publish(event.getApplicationContext(), ReadinessState.REFUSING_TRAFFIC);
        System.out.println(">>> Readiness set to REFUSING_TRAFFIC (Pod removed from LB)");
    }
}
```

### Spring Boot yml 설정

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health, readiness, liveness
  server:
    port: 9404
  endpoint:
    health:
      probes:
        enabled: true
```

## 쿠버네티스 설정

### deployment.yaml 설정

```yaml
...
spec:
  ...
      terminationGracePeriodSeconds: 20 # Pod가 종료될 때 컨테이너가 정상적으로 종료할 수 있도록 기다려주는 시간(초), SIGTERM 이후
      containers:
        - name: my-app
          ...
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 9404
            initialDelaySeconds: 45
            periodSeconds: 5
            timeoutSeconds: 5
            successThreshold: 1
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 9404
            initialDelaySeconds: 45
            periodSeconds: 5
            timeoutSeconds: 5
            successThreshold: 1
            failureThreshold: 3
      ...
```

### Service.yaml 설정

해당 service 는 ingress (ALB) 가 라우팅한다. 여기서  ALB 의 health path 를 정할 수 있다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
  annotations:
    alb.ingress.kubernetes.io/healthcheck-path: /actuator/health
  labels:
    app: my-app
spec:
  selector:
    app: my-app
  ports:
    - port: 8080
      targetPort: 8080
      protocol: TCP
  type: CluterIP

```



## 전체 흐름

1. RollingUpdate 시작 → 기존 Pod에 SIGTERM 전달
2. Spring Boot가 `ReadinessState`를 `REFUSING_TRAFFIC` 으로 변경
3. `/actuator/health/readiness` → DOWN 반환
4. readinessProbe 실패 → LB가 Pod를 트래픽 대상에서 제외
5. 진행 중이던 요청 처리 완료
6. Pod 종료

<Footer/>
