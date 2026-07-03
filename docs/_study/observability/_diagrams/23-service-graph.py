"""CH23 service graph metrics — processor → 메트릭 → Node Graph 패널 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def node(cx, cy, t, sub, c, bw=20, bh=7):
        d.box(cx - bw / 2, cy - bh / 2, bw, bh, P[c])
        d.text(cx, cy + (1.2 if sub else 0), t, size=10, weight="bold")
        if sub:
            d.text(cx, cy - 1.6, sub, size=8, color=P["dim"])

    node(10, 22, "Ingester", "span 스트림", "brown", bw=15)
    node(27, 22, "service_graphs", "processor", "orange", bw=16)

    metrics = [
        (57, 32, "traces_service_graph_request_total"),
        (57, 22, "…_request_failed_total"),
        (57, 12, "…_request_server_seconds_bucket"),
    ]
    for cx, cy, t in metrics:
        node(cx, cy, t, "", "blue", bw=32, bh=5.6)

    node(84, 22, "Mimir", "", "purple", bw=13, bh=6)
    node(84, 9, "Grafana", "Node Graph", "green", bw=15, bh=7)

    d.arrow(17.5, 22, 18.8, 22, color=P["accent"])
    d.arrow(35, 24, 40.5, 31.5, color=P["accent"])
    d.arrow(35, 22, 40.5, 22, color=P["accent"])
    d.arrow(35, 20, 40.5, 12.5, color=P["accent"])
    d.arrow(73.5, 32, 78, 24, color=P["violet"])
    d.arrow(73.5, 22, 77.5, 22, color=P["violet"])
    d.arrow(73.5, 12, 78, 20, color=P["violet"])
    d.arrow(84, 18.8, 84, 12.6, color=P["accent"])


diagram("23-service-graph", draw, w=15, h=6, ymax=40)
