"""CH21 교차 신호 — OTel SDK → OTLP → 신호별 백엔드 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    def cbox(cx, cy, w, h, fc, **kw):
        d.box(cx - w / 2, cy - h / 2, w, h, fc, **kw)

    # 왼쪽: 애플리케이션 (OTel SDK)
    d.box(4, 6, 24, 36, P["gray"], ec=P["accent"], lw=1.8)
    d.text(16, 39, "애플리케이션 (OTel SDK)", size=11, weight="bold", color=P["accent"])
    signals = [("Traces", "brown", 31), ("Metrics", "blue", 22), ("Logs", "green", 13)]
    for name, c, cy in signals:
        cbox(16, cy, 18, 6, P[c])
        d.text(16, cy, name, size=11, weight="bold")

    # 가운데: OTLP
    d.box(38, 12, 24, 24, P["brown"], ec=P["orange"], lw=1.8)
    d.text(50, 33, "OTLP", size=12, weight="bold", color=P["orange"])
    cbox(50, 22, 18, 8, P["chip"])
    d.text(50, 23.6, "gRPC / HTTP", size=10.5, weight="bold")
    d.text(50, 20.6, "+ Protobuf", size=8.5, color=P["dim"])

    # 오른쪽: 백엔드
    d.box(72, 6, 24, 36, P["gray"])
    d.text(84, 39, "백엔드 (신호별 저장소)", size=11, weight="bold")
    backs = [("Tempo", "brown", 31, "트레이스"), ("Prometheus / Mimir", "blue", 22, "메트릭"),
             ("Loki", "green", 13, "로그")]
    for name, c, cy, sub in backs:
        cbox(84, cy, 18, 6, P[c])
        d.text(84, cy + 0.9, name, size=10, weight="bold")
        d.text(84, cy - 1.5, sub, size=8, color=P["dim"])

    for _, _, cy in signals:
        d.arrow(25, cy, 38, 22 + (cy - 22) * 0.15, color=P["accent"])
    for _, _, cy, _ in backs:
        d.arrow(62, 22 + (cy - 22) * 0.15, 72, cy, color=P["orange"])

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.2, label="SDK → OTLP"),
        Line2D([0], [0], color=P["orange"], lw=2.2, label="OTLP → 백엔드"),
    ])


diagram("21-cross-signal-otlp", draw, w=12, h=5.8, ymax=44)
