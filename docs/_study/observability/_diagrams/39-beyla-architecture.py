"""CH39 Beyla — eBPF 자동 계측 구조 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # 왼쪽: 애플리케이션(무수정) + 커널 eBPF
    d.box(2, 27, 22, 17, P["gray"])
    d.text(13, 41, "애플리케이션 프로세스", size=11, weight="bold")
    d.text(13, 38.5, "(Go·Java·Python·Node — 무수정)", size=8.5, color=P["dim"])
    d.box(4, 29.5, 18, 6.5, P["chip"])
    d.text(13, 33.3, "HTTP / gRPC 서버", size=9.5)
    d.text(13, 31.2, "TLS 암호화 트래픽", size=9.5)

    d.box(2, 4, 22, 18, P["brown"])
    d.text(13, 19, "커널 공간 (eBPF)", size=11, weight="bold")
    d.box(4, 11.5, 18, 4.4, P["chip"])
    d.text(13, 13.7, "uprobe · kprobe · tracepoint", size=9)
    d.box(4, 6, 18, 4.4, P["chip"])
    d.text(13, 8.2, "socket filter (HTTP/2·gRPC)", size=9)

    # 중앙: Beyla 데몬
    d.box(30, 4, 34, 40, P["green"], ec=P["accent"], lw=1.8)
    d.text(47, 41, "Beyla (사용자 공간 데몬)", size=11.5, weight="bold", color=P["accent"])
    for i, t in enumerate([
        "프로세스 디스커버리",
        "프로토콜 파싱 (HTTP·gRPC·SQL·Redis)",
        "RED 메트릭 생성 (OTel semconv)",
        "트레이스 / span 조립",
    ]):
        yy = 34 - i * 7
        d.box(32, yy - 2.6, 30, 5.2, P["chip"])
        d.text(47, yy, t, size=9.5)

    # 오른쪽: 백엔드 내보내기
    d.box(74, 26, 24, 18, P["gray"])
    d.text(86, 41, "내보내기 (OTLP)", size=11, weight="bold")
    for i, t in enumerate([
        "Alloy / OTel Collector",
        "Tempo (트레이스)",
        "Mimir / Prometheus (메트릭)",
    ]):
        yy = 37 - i * 4.4
        d.box(76, yy - 1.8, 20, 3.6, P["chip"])
        d.text(86, yy, t, size=9)

    d.box(74, 6, 24, 15, P["blue"])
    d.text(86, 16.5, "Prometheus 노출 모드", size=11, weight="bold")
    d.text(86, 12.5, "/metrics 직접 노출 → pull", size=9, color=P["dim"])

    # 흐름 화살표
    d.arrow(13, 27, 13, 22, color=P["orange"])
    d.text(16.8, 24.5, "관측", size=8, color=P["orange"])
    d.arrow(24, 12, 30, 16, color=P["orange"])
    d.text(27, 19.5, "ringbuf 이벤트", size=8, color=P["orange"])
    d.arrow(64, 32, 74, 35, color=P["accent"])
    d.text(69, 36.4, "OTLP push", size=8, color=P["accent"])
    d.arrow(64, 15, 74, 13, color=P["violet"])
    d.text(69, 10.6, "/metrics pull", size=8, color=P["violet"])

    d.legend([
        Line2D([0], [0], color=P["orange"], lw=2.5, label="커널 → 사용자 공간 이벤트"),
        Line2D([0], [0], color=P["accent"], lw=2.5, label="OTLP push 경로"),
        Line2D([0], [0], color=P["violet"], lw=2.5, label="Prometheus pull 경로"),
    ])


diagram("39-beyla-architecture", draw, w=13, h=6.4, ymax=48)
