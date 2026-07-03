---
title: "k6와 Synthetic Monitoring"
description: "트래픽이 없어도, 사용자가 겪기 전에 문제를 발견하는 능동적 관측을 다룬다. k6의 시나리오·VU·thresholds로 SLO를 배포 전에 코드로 검증하고, Grafana Synthetic Monitoring의 글로벌 프로브·browser check로 상시 가용성을 감시하며, 결과를 Prometheus·Loki에 적재해 기존 알림 체계에 통합한다."
date: 2026-07-03
tags: [Observability, k6, Synthetic Monitoring, Load Testing]
prev: /study/observability/40-faro-frontend-observability
next: /study/observability/42-grafana-alerting-irm
---

# k6와 Synthetic Monitoring

::: info 학습 목표
- 수동적(passive) 관측과 능동적(active) 관측의 차이, 그리고 합성 모니터링이 필요한 상황을 이해한다.
- k6의 시나리오·VU·checks·thresholds로 부하 테스트를 코드로 작성할 수 있다.
- k6 결과를 Prometheus remote write로 LGTM 스택에 적재해 대시보드·알림에 연결할 수 있다.
- Grafana Synthetic Monitoring의 check 유형과 blackbox_exporter 대비 포지션을 안다.
- 합성 신호로 uptime SLI를 만들어 기존 SLO 알림 체계에 통합하는 방법을 이해한다.
:::

## 1. 능동적 관측 — 기다리지 않고 직접 두드린다

지금까지 다룬 신호는 전부 <strong>수동적(passive)</strong>이다 — 실제 트래픽이 만들어낸 메트릭·로그·트레이스, 실제 사용자가 만들어낸 [RUM](/study/observability/40-faro-frontend-observability)을 기록한다. 이 방식의 구조적 한계는 두 가지다. <strong>트래픽이 없으면 신호도 없다</strong>(새벽의 결제 API가 죽어 있어도 첫 사용자가 올 때까지 모른다), 그리고 <strong>문제는 사용자가 겪은 뒤에야 보인다</strong>.

<strong>능동적(active) 관측</strong>, 즉 합성 모니터링(synthetic monitoring)은 반대로 접근한다 — 가짜 트래픽을 직접 만들어 시스템을 두드려보고 그 결과를 기록한다. [blackbox_exporter](/study/observability/08-exporters-instrumentation)에서 이미 이 관점(외부에서 보이는 가용성)을 만났다. 이 챕터는 그 연장선에서 Grafana 생태계의 두 도구를 다룬다 — 부하를 걸어보는 <strong>k6</strong>, 상시 프로브를 돌리는 <strong>Synthetic Monitoring</strong>.

![k6와 Synthetic Monitoring — k6 부하 주입과 글로벌 프로브가 대상 시스템을 두드리고 결과를 LGTM 스택에 적재하는 능동적 관측 구조](/images/study-observability/41-k6-synthetic-light.png)
![k6와 Synthetic Monitoring — k6 부하 주입과 글로벌 프로브가 대상 시스템을 두드리고 결과를 LGTM 스택에 적재하는 능동적 관측 구조](/images/study-observability/41-k6-synthetic-dark.png)

## 2. k6 — 부하 테스트를 코드로

<strong>k6</strong>는 Grafana Labs의 오픈소스 부하 테스트 도구다. 테스트 시나리오를 JavaScript로 쓰고, Go로 구현된 엔진이 이를 수천 개의 <strong>VU(virtual user)</strong>로 실행한다.

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  scenarios: {
    checkout_peak: {
      executor: 'ramping-vus',          // 점진적 램프업
      stages: [
        { duration: '2m', target: 200 }, // 2분 동안 200 VU까지
        { duration: '5m', target: 200 }, // 5분 유지
        { duration: '1m', target: 0 },
      ],
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<300'],     // p95 < 300ms 아니면 실패
    http_req_failed: ['rate<0.01'],       // 에러율 < 1%
  },
};

export default function () {
  const res = http.post('https://api.example.com/checkout', payload());
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(1);
}
```

핵심은 <strong>thresholds</strong>다. [SLO/SLI와 알림 설계](/study/observability/15-slo-sli-alerting)에서 "p95 레이턴시 300ms"를 프로덕션 알림으로 지켰다면, thresholds는 <strong>같은 기준을 배포 전에 검증</strong>한다. threshold 위반 시 k6 프로세스가 비제로 exit code로 끝나므로 CI 파이프라인에 넣으면 "SLO를 깨는 릴리즈는 머지 불가"가 된다 — SLO가 운영 시점의 감시 기준을 넘어 배포 게이트가 되는 것이다.

<strong>k6 browser</strong> 모듈은 헤드리스 브라우저를 띄워 실제 렌더링 기준으로 시나리오를 실행한다. 프로토콜 수준 VU가 못 보는 Web Vitals(LCP·CLS 등)를 측정할 수 있어, [Faro](/study/observability/40-faro-frontend-observability)가 수집하는 실사용자 지표를 배포 전에 미리 확인하는 용도로 짝을 이룬다.

## 3. k6 결과를 LGTM 스택으로

k6는 실행 결과를 콘솔 요약으로만 남기지 않고 <strong>Prometheus remote write output</strong>으로 실시간 스트리밍할 수 있다.

```bash
K6_PROMETHEUS_RW_SERVER_URL=http://mimir:9009/api/v1/push \
k6 run -o experimental-prometheus-rw checkout-test.js
```

`k6_http_req_duration_p95` 같은 시계열이 [Mimir](/study/observability/35-mimir-longterm-storage)에 쌓이면, 부하 테스트 중의 k6 지표(클라이언트 관점)와 애플리케이션 메트릭·트레이스·프로파일(서버 관점)을 <strong>같은 Grafana 시간축</strong>에서 겹쳐볼 수 있다. "p95가 튀는 순간 서버에서 무슨 일이 있었나"를 [시그널 상관관계](/study/observability/32-signal-correlation)로 바로 파고들 수 있다는 뜻이다 — 부하 테스트가 별도 도구의 리포트가 아니라 관측성 스택의 신호 하나가 된다.

## 4. Grafana Synthetic Monitoring — 상시 프로브

k6가 "필요할 때 실행하는 부하 테스트"라면, <strong>Synthetic Monitoring</strong>은 "항상 돌아가는 정기 프로브"다. Grafana Cloud 서비스로, 전 세계 여러 <strong>프로브 위치</strong>에서 대상을 주기적으로 검사하고 결과를 Prometheus 메트릭·Loki 로그로 적재한다.

check 유형은 단계적으로 깊어진다.

| check 유형 | 검사 내용 |
|---|---|
| ping / DNS / TCP | 기본 도달성, DNS 응답, 포트 오픈 |
| HTTP | 상태코드·응답시간·본문 매칭·TLS 인증서 만료일 |
| traceroute | 네트워크 경로·홉별 지연 진단 |
| browser | 헤드리스 브라우저로 페이지 로드, Web Vitals 측정 |
| scripted | k6 스크립트로 다단계 사용자 여정(로그인→장바구니→결제) 검증 |

scripted check가 k6 스크립트를 그대로 쓴다는 점이 이 생태계의 결합 지점이다 — 부하 테스트용으로 작성한 시나리오를 강도만 낮춰 상시 가용성 프로브로 재사용할 수 있다. 방화벽 안쪽 내부 서비스는 <strong>private probe</strong>(자체 인프라에 프로브 에이전트 설치)로 같은 방식으로 검사한다.

::: info blackbox_exporter와의 선택
[8장](/study/observability/08-exporters-instrumentation)의 blackbox_exporter는 클러스터 안에서 직접 운영하는 셀프호스팅 프로브다(HTTP/TCP/ICMP/DNS). 내부 서비스의 단순 가용성 체크라면 blackbox_exporter로 충분하고 비용도 없다. Synthetic Monitoring이 값어치를 하는 지점은 <strong>사용자 관점</strong>이 필요할 때다 — 여러 대륙에서의 응답시간, 실제 브라우저 렌더링, 다단계 여정 검증은 blackbox_exporter가 못 하는 영역이다.
:::

## 5. 알림 연계 — 합성 신호도 결국 메트릭이다

Synthetic Monitoring의 결과는 `probe_success`, `probe_duration_seconds` 같은 평범한 Prometheus 메트릭이므로, 기존 알림 체계가 그대로 적용된다. 지역별 uptime SLI를 만들고:

```promql
# 지난 5분간 프로브 성공률 (지역별)
sum by (probe) (rate(probe_success{job="checkout-http"}[5m]))
```

이를 [multi-window burn rate](/study/observability/15-slo-sli-alerting) 알림에 넣으면, 실사용자 트래픽 기반 SLI와 합성 프로브 기반 SLI가 같은 에러 버짓 프레임워크 안에서 관리된다. 새벽처럼 실트래픽이 희박한 시간대는 합성 신호가 SLI의 공백을 메워주는 역할도 한다 — 트래픽이 적을수록 실사용자 SLI는 통계적으로 불안정해지는데, 프로브는 일정한 주기로 계속 표본을 만들어주기 때문이다.

::: tip 핵심 정리
- 수동적 관측은 트래픽이 없으면 침묵하고 사용자가 겪은 뒤에야 보인다 — 능동적(합성) 관측이 이 공백을 메운다.
- k6는 부하 테스트를 JS 코드로 작성하고, thresholds로 SLO를 배포 게이트로 만든다 (threshold 위반 = CI 실패).
- k6 결과를 Prometheus remote write로 Mimir에 적재하면 부하 테스트가 관측성 스택의 신호 하나로 통합된다.
- Synthetic Monitoring은 글로벌 프로브 위치에서 ping/HTTP/browser/scripted check를 상시 실행한다 — scripted check는 k6 스크립트를 재사용한다.
- 내부 단순 가용성은 blackbox_exporter로 충분하고, 사용자 관점·다지역·다단계 여정이 필요할 때 Synthetic Monitoring을 쓴다.
- 합성 신호도 평범한 메트릭이므로 uptime SLI로 만들어 기존 burn rate 알림 체계에 통합한다.
:::

## 다음 챕터

신호는 이제 4대 신호 + RUM + 합성까지 갖춰졌고, 문제를 발견하면 알림이 날아간다. 그런데 이 스터디에서 알림은 [Alertmanager](/study/observability/13-alertmanager-architecture) 기준으로 다뤘다 — Grafana에는 별도의 알림 시스템이 하나 더 있다. [Grafana Alerting과 IRM](/study/observability/42-grafana-alerting-irm)에서는 두 알림 시스템의 관계와 선택 기준, 그리고 알림 이후의 대응 체계(온콜·에스컬레이션·인시던트)까지 다루며 스터디를 마무리한다.
