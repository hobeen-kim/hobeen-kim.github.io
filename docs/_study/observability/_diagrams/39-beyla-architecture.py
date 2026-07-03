"""CH39 Beyla — eBPF 자동 계측 구조 다이어그램 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "Beyla — eBPF 제로코드 자동 계측", size=20, weight="bold")
text(50, 56.6, "애플리케이션(무수정)  →  커널 eBPF probe  →  Beyla 사용자 공간  →  LGTM 백엔드",
     size=12, color=C_DIM)

# ================= left: application + kernel =================
box(2, 30, 26, 22, C_GRAY)
text(15, 49.6, "애플리케이션 프로세스", size=13, weight="bold")
text(15, 47.4, "코드 수정 · SDK · 재배포 없음", size=9.5, color=C_ACCENT, style="italic")
for i, (t, d) in enumerate([
    ("HTTP/gRPC 서버", "Go · Java · Python · Node · Rust …"),
    ("TLS 암호화 트래픽", "OpenSSL · Go crypto/tls"),
    ("DB·메시징 클라이언트", "SQL · Redis · Kafka"),
]):
    yy = 43 - i * 4.6
    box(4, yy - 1.9, 22, 3.8, "#1b232a")
    text(15, yy + 0.6, t, size=10)
    text(15, yy - 1.0, d, size=8, color=C_DIM)

box(2, 6.9, 26, 19.1, C_BROWN)
text(15, 23.6, "커널 공간 (eBPF)", size=13, weight="bold")
text(15, 21.4, "커널 4.18+ · BTF 필요", size=9, color=C_DIM)
for i, (t, d) in enumerate([
    ("kprobe · tracepoint", "소켓 연결 · syscall 수준 이벤트"),
    ("uprobe", "SSL_read/write 후킹 → 평문 캡처"),
    ("socket filter", "HTTP/1.1 · HTTP/2 · gRPC 파싱 원천"),
]):
    yy = 18 - i * 4.4
    box(4, yy - 1.8, 22, 3.6, "#241d1a")
    text(15, yy + 0.6, t, size=10)
    text(15, yy - 1.0, d, size=8, color=C_DIM)

# app -> kernel (관측 대상)
arrow(15, 30, 15, 26, color=C_ORANGE, lw=2.2)
text(19.5, 28, "트래픽 관측", size=8.5, color=C_ORANGE)

# ================= center: Beyla userspace =================
box(36, 8, 30, 44, C_GREEN, ec=C_ACCENT, lw=2.0)
text(51, 49.4, "Beyla (사용자 공간 데몬)", size=13.5, weight="bold", color=C_ACCENT)
text(51, 47.2, "DaemonSet · 사이드카 · 단독 프로세스", size=9, color=C_DIM)
for i, (t, d) in enumerate([
    ("프로세스 디스커버리", "실행 파일·포트·K8s 메타데이터로 대상 선택"),
    ("프로토콜 파싱", "HTTP/1.1 · HTTP/2 · gRPC · SQL · Redis · Kafka"),
    ("RED 메트릭 생성", "http.server.request.duration 등 OTel semconv"),
    ("트레이스/span 조립", "요청 단위 span + traceparent 전파"),
    ("K8s 데코레이션", "namespace · pod · service 라벨 부착"),
]):
    yy = 42.5 - i * 6.4
    box(38, yy - 2.5, 26, 5.0, "#1d2b24")
    text(51, yy + 0.5, t, size=10.5)
    text(51, yy - 1.4, d, size=8, color=C_DIM)

# kernel -> Beyla
arrow(28, 17, 36, 17, color=C_ORANGE, lw=2.2)
text(32, 19.2, "ringbuf\n이벤트", size=8, color=C_ORANGE, weight="bold")

# ================= right: backends =================
box(74, 30, 24, 22, C_GRAY)
text(86, 49.6, "내보내기 (OTLP)", size=13, weight="bold")
for i, (t, d) in enumerate([
    ("Alloy / OTel Collector", "otelcol.receiver.otlp"),
    ("Tempo", "트레이스 저장 · TraceQL"),
    ("Mimir / Prometheus", "RED 메트릭 (remote_write)"),
]):
    yy = 45 - i * 5.4
    box(76, yy - 2.2, 20, 4.4, "#1b232a")
    text(86, yy + 0.6, t, size=10)
    text(86, yy - 1.2, d, size=8, color=C_DIM)

box(74, 8, 24, 18, C_BLUE)
text(86, 23.6, "Prometheus 노출 모드", size=13, weight="bold")
text(86, 21.0, "/metrics 엔드포인트를 직접 노출해\nPrometheus가 스크레이프하는\npull 경로도 지원", size=9.5, color="#d4dae0")
text(86, 12.5, "OTLP push / Prometheus pull\n둘 중 환경에 맞는 쪽 선택", size=8.5,
     color=C_ACCENT, style="italic")

# Beyla -> backends
arrow(66, 41, 74, 41, color=C_ACCENT, lw=2.2)
text(70, 43.2, "OTLP", size=8.5, color=C_ACCENT, weight="bold")
arrow(66, 17, 74, 17, color=C_VIOLET, lw=2.2)
text(70, 19.2, "/metrics", size=8.5, color=C_VIOLET, weight="bold")

# bottom
text(50, 4.8, "코드 무수정 애플리케이션  →  커널 eBPF 이벤트  →  프로토콜 파싱  →  RED 메트릭 + 트레이스",
     size=10, color=C_ACCENT, weight="bold")
text(50, 2.4, "Beyla 코어는 OpenTelemetry eBPF Instrumentation(OBI)으로 기증 — Beyla는 OBI를 임베드한 Grafana 배포판",
     size=9, color=C_DIM, style="italic")

leg = [
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="커널 → 사용자 공간 이벤트"),
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="OTLP push 경로"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, label="Prometheus pull 경로"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.005),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "39-beyla-architecture.png")
