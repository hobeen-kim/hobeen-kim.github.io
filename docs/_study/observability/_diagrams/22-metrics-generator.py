"""CH22 metrics-generator — trace에서 span/service graph 메트릭 파생 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def node(cx, cy, t, sub, c, bw=20, bh=8):
        d.box(cx - bw / 2, cy - bh / 2, bw, bh, P[c])
        d.text(cx, cy + (1.4 if sub else 0), t, size=10, weight="bold")
        if sub:
            d.text(cx, cy - 1.7, sub, size=8, color=P["dim"])

    node(11, 20, "Ingester", "span 스트림", "brown", bw=16)
    node(30, 20, "metrics-generator", "", "orange", bw=18, bh=7)
    node(56, 29, "span metrics", "traces_spanmetrics_*", "blue", bw=26, bh=8)
    node(56, 11, "service graph metrics", "traces_service_graph_*", "green", bw=26, bh=8)
    node(85, 20, "Mimir / Prometheus", "remote_write", "purple", bw=18, bh=8)

    d.arrow(19.2, 20, 20.8, 20, color=P["accent"])
    d.arrow(39.2, 20, 43, 27, color=P["accent"])
    d.arrow(39.2, 20, 43, 13, color=P["accent"])
    d.arrow(69.2, 29, 76.5, 22.5, color=P["orange"])
    d.arrow(69.2, 11, 76.5, 17.5, color=P["orange"])


diagram("22-metrics-generator", draw, w=14, h=5.4, ymax=40)
