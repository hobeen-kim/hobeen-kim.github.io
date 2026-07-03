---
title: "Beyla — eBPF 자동 계측"
description: "코드 한 줄 수정 없이 트레이스와 RED 메트릭을 얻는 Grafana Beyla의 eBPF 자동 계측 원리를 다룬다. kprobe/uprobe로 프로토콜 이벤트를 포착하는 커널 수준 동작, TLS 평문 캡처, K8s DaemonSet 배포, OpenTelemetry eBPF Instrumentation(OBI) 기증까지 정리한다."
date: 2026-07-03
tags: [Observability, Beyla, eBPF, OpenTelemetry]
prev: /study/observability/38-production-troubleshooting
next: /study/observability/40-faro-frontend-observability
---

# Beyla — eBPF 자동 계측

::: info 학습 목표
- SDK 계측이 불가능한 워크로드(레거시, 서드파티 바이너리)에서 트레이스·메트릭을 얻는 방법을 이해한다.
- Beyla가 kprobe/uprobe/socket filter로 프로토콜 이벤트를 포착하는 커널 수준 동작 원리를 안다.
- Beyla가 만들어내는 RED 메트릭·span의 범위와, SDK 계측 대비 한계를 구분할 수 있다.
- Kubernetes DaemonSet 배포와 디스커버리 설정을 작성할 수 있다.
- Beyla 코어가 OpenTelemetry eBPF Instrumentation(OBI)으로 기증된 구도를 이해한다.
:::

## 1. 계측의 마지막 사각지대

[OpenTelemetry](/study/observability/21-opentelemetry)에서 다뤘듯 트레이스를 얻는 정석은 애플리케이션에 OTel SDK를 넣는 것이다. 하지만 현실에는 SDK를 넣을 수 없는 워크로드가 반드시 남는다.

- <strong>소스를 통제할 수 없는 바이너리</strong> — 벤더 제공 서비스, 사내에서 빌드 파이프라인이 끊긴 레거시.
- <strong>재배포 비용이 큰 서비스</strong> — 계측 하나 넣자고 릴리즈 사이클을 태우기 어려운 코어 시스템.
- <strong>폴리글랏 조직</strong> — Go·Java·Python·Node가 섞여 있으면 언어별 SDK 도입·유지보수가 언어 수만큼 늘어난다.

[Exporter와 애플리케이션 계측](/study/observability/08-exporters-instrumentation)에서 "소스를 통제할 수 없으면 Exporter"라는 원칙을 세웠지만, Exporter는 메트릭까지만 해결한다. 요청 단위의 트레이스는 지금까지 SDK 없이는 얻을 수 없었다. <strong>Beyla</strong>는 이 간극을 eBPF로 메운다 — 커널이 어차피 모든 네트워크 트래픽을 지나 보내는 길목이라는 점을 이용해, 애플리케이션을 전혀 건드리지 않고 요청·응답을 관찰한다.

::: info Pyroscope eBPF와의 차이
[프로파일 타입과 eBPF](/study/observability/26-profile-types-ebpf)의 eBPF 프로파일링은 <strong>스택 샘플링</strong>으로 "CPU가 어느 함수에서 소비되는가"(프로파일 신호)를 얻는다. Beyla는 <strong>네트워크 이벤트 관찰</strong>로 "어떤 요청이 얼마나 걸렸는가"(트레이스·메트릭 신호)를 얻는다. 같은 eBPF 기술이지만 만들어내는 신호가 다르다.
:::

## 2. 동작 원리 — 커널에서 프로토콜 이벤트를 포착한다

Beyla는 사용자 공간 데몬이 커널에 eBPF 프로그램을 심고, 커널이 포착한 이벤트를 ring buffer로 받아 프로토콜 수준의 요청/응답으로 조립하는 구조다.

![Beyla eBPF 자동 계측 구조 — 무수정 애플리케이션, 커널 eBPF probe, Beyla 사용자 공간 데몬, LGTM 백엔드로 이어지는 흐름](/images/study-observability/39-beyla-architecture.png)

커널 쪽에서 쓰는 hook은 세 종류다.

- <strong>kprobe · tracepoint</strong> — 소켓 연결 수립, `sys_accept`/`sys_connect` 같은 syscall 수준 이벤트를 잡아 "어느 프로세스가 어느 피어와 통신하는가"의 골격을 만든다.
- <strong>socket filter / sockops</strong> — 소켓을 지나는 바이트 스트림에서 HTTP/1.1, HTTP/2, gRPC 프레임을 파싱해 메서드·경로·상태코드·소요시간을 추출한다.
- <strong>uprobe</strong> — 사용자 공간 함수에 거는 probe다. TLS 트래픽은 소켓에서 암호문으로만 보이므로, OpenSSL의 `SSL_read`/`SSL_write`나 Go `crypto/tls` 함수에 uprobe를 걸어 <strong>암호화 전/복호화 후의 평문</strong>을 캡처한다. HTTPS 트래픽도 계측 없이 관찰 가능한 이유가 이것이다.

이 방식이 성립하려면 커널 지원이 필요하다. 최소 <strong>커널 4.18 이상</strong>(주요 기능은 5.8+에서 안정), eBPF 프로그램이 커널 구조체 오프셋을 읽기 위한 <strong>BTF(BPF Type Format)</strong>가 활성화된 커널이어야 한다. 또 eBPF 프로그램 로드 권한이 필요해 컨테이너에 `privileged: true` 또는 `CAP_BPF`·`CAP_SYS_PTRACE` 같은 세분화된 capability를 부여해야 한다 — 보안 검토 시 반드시 짚어야 할 지점이다.

## 3. 무엇을 만들어내나 — RED 메트릭과 트레이스

Beyla가 파싱한 요청/응답 이벤트는 두 가지 신호로 변환된다.

- <strong>RED 메트릭</strong> — `http.server.request.duration`, `rpc.server.duration` 같은 [OTel semantic conventions](/study/observability/21-opentelemetry) 이름의 히스토그램. 서비스별 Rate·Errors·Duration이 계측 없이 바로 나온다. [Tempo의 metrics-generator](/study/observability/22-tempo-architecture)가 "트레이스가 있으면 RED 메트릭은 공짜"였다면, Beyla는 한 단계 더 나아가 "트래픽이 있으면 트레이스도 RED도 공짜"로 만든다.
- <strong>트레이스(span)</strong> — 요청 단위 span을 생성하고, HTTP 요청에는 W3C `traceparent` 헤더를 읽고 이어붙여 SDK 계측된 서비스와 <strong>같은 trace에 합류</strong>할 수 있다.

한계도 명확하다. Beyla가 보는 것은 네트워크 경계이므로, <strong>프로세스 내부의 논리 단계</strong>(비즈니스 로직 함수, 캐시 히트 여부, 내부 큐 대기)는 span으로 쪼개지지 않는다. SDK 계측이 만드는 풍부한 내부 span·커스텀 속성·baggage는 흉내낼 수 없다. 그래서 Beyla의 포지션은 "SDK의 대체"가 아니라 <strong>커버리지의 바닥을 깔아주는 안전망</strong>이다 — 전 서비스에 Beyla로 기본 트레이스·RED를 확보하고, 핵심 서비스에는 SDK 계측을 더해 깊이를 얻는 조합이 실무 정석이다.

## 4. 배포와 디스커버리 설정

Kubernetes에서는 노드마다 하나씩 띄우는 <strong>DaemonSet</strong>이 기본 패턴이다. Beyla 하나가 해당 노드의 모든 대상 프로세스를 계측한다.

```yaml
# beyla-config.yaml — 어떤 프로세스를 계측할지 선택
discovery:
  instrument:
    - k8s_namespace: production        # 네임스페이스 단위 선택
    - k8s_deployment_name: "checkout-*" # 와일드카드 매칭
    - open_ports: 8080-8089            # 포트 기준 선택도 가능

attributes:
  kubernetes:
    enable: true    # namespace·pod·service 라벨을 신호에 부착

otel_traces_export:
  endpoint: http://alloy:4317   # OTLP로 Alloy/Collector에 전송
prometheus_export:
  port: 9400                    # 또는 /metrics로 노출해 스크레이프
```

내보내기는 두 경로를 지원한다. <strong>OTLP push</strong>로 [Alloy](/study/observability/28-alloy-overview)나 OTel Collector에 보내는 경로가 표준이고, `/metrics` 엔드포인트를 노출해 Prometheus가 [스크레이프](/study/observability/07-scraping-service-discovery)하는 <strong>pull 경로</strong>도 지원해 기존 Prometheus 파이프라인에 그대로 얹을 수 있다.

::: warning 카디널리티 주의
Beyla는 기본적으로 HTTP 경로를 라우트 패턴(`/users/{id}`)으로 정규화하려 시도하지만, 정규화가 실패하면 raw 경로가 메트릭 라벨로 새어 나가 [카디널리티 폭발](/study/observability/34-cardinality-cost)을 일으킬 수 있다. `routes` 설정으로 경로 패턴을 명시하고, 배포 초기에 `http.route` 라벨의 유니크 값 수를 반드시 확인한다.
:::

## 5. OBI — OpenTelemetry로의 기증

2025년 Grafana Labs는 Beyla의 eBPF 코어를 OpenTelemetry 프로젝트에 기증했고, 이것이 <strong>OBI(OpenTelemetry eBPF Instrumentation)</strong>가 됐다. 이후 구도는 [Collector vs Alloy](/study/observability/30-collector-vs-alloy)와 정확히 같은 모양이다 — OBI가 벤더 중립 코어(upstream)이고, Beyla는 OBI를 임베드해 Grafana 스택 연동·배포 편의를 더한 <strong>배포판(distribution)</strong>으로 유지된다. 벤더 중립성이 최우선이면 OBI를 직접, Grafana 스택이 주력이면 Beyla를 쓰는 선택 기준도 동일하게 적용된다.

## 6. SDK 계측 vs Beyla

| 기준 | OTel SDK 계측 | Beyla (eBPF) |
|---|---|---|
| 코드 수정 | 필요 (초기화 + 자동/수동 계측) | 불필요 |
| 내부 span (함수·캐시·큐) | 가능 | 불가 — 네트워크 경계만 |
| 커스텀 속성·baggage | 가능 | 불가 |
| 언어 커버리지 | 언어별 SDK 필요 | 언어 무관 (컴파일 언어 포함) |
| TLS 트래픽 | 애플리케이션 내부라 문제없음 | uprobe로 평문 캡처 (라이브러리별 지원 확인 필요) |
| 배포 위치 | 애플리케이션에 내장 | 노드 DaemonSet (privileged 필요) |
| 적합한 역할 | 핵심 서비스의 깊은 가시성 | 전체 서비스의 기본 커버리지 안전망 |

::: tip 핵심 정리
- Beyla는 eBPF로 커널에서 프로토콜 이벤트를 포착해, 코드 수정 없이 트레이스와 RED 메트릭을 만들어낸다.
- kprobe/tracepoint가 연결 골격을, socket filter가 HTTP/gRPC 파싱을, uprobe가 TLS 평문 캡처를 맡는다.
- 커널 4.18+/BTF와 privileged(또는 CAP_BPF) 권한이 필요하며, 보안 검토 대상이다.
- 네트워크 경계만 보이므로 내부 span·커스텀 속성은 불가 — SDK 계측의 대체가 아니라 커버리지 안전망이다.
- 코어는 OTel에 기증되어 OBI가 됐고, Beyla는 OBI를 임베드한 Grafana 배포판이다 (Collector↔Alloy와 같은 구도).
- HTTP 경로 정규화 실패로 인한 카디널리티 폭발을 배포 초기에 반드시 점검한다.
:::

## 다음 챕터

Beyla가 서버 쪽 계측의 사각지대를 메웠다면, 아직 한 곳이 남았다 — 사용자의 브라우저다. [Faro — 프런트엔드 관측성(RUM)](/study/observability/40-faro-frontend-observability)에서는 백엔드가 전부 정상이어도 사용자는 느릴 수 있다는 문제를, 브라우저에서 직접 신호를 수집하는 Real User Monitoring으로 해결한다.
