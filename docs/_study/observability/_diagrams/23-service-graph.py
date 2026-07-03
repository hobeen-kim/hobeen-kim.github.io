"""CH23 service graph metrics — processor → 메트릭 → Node Graph 패널 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_PURPLE, C_VIOLET)

fig, ax = new_fig(w=15, h=8, ymax=48)
box, text, arrow = make_helpers(ax)


def node(cx, cy, t, d, c, bw=20, bh=7, dcolor=C_DIM):
    box(cx - bw / 2, cy - bh / 2, bw, bh, c)
    text(cx, cy + (1.2 if d else 0), t, size=10, weight="bold")
    if d:
        text(cx, cy - 1.6, d, size=8, color=dcolor)


# ---- Title ----
text(50, 45, "service graph metrics — 서비스 간 호출 관계를 메트릭으로", size=17, weight="bold")
text(50, 41.6, "span의 CLIENT/SERVER kind와 parent/child 관계를 분석해 엣지(client·server 라벨)를 생성", size=10.5, color=C_DIM)

# nodes
node(10, 24, "Ingester", "span 스트림", C_BROWN, bw=15)
node(27, 24, "service_graphs", "processor", C_ORANGE, bw=16, dcolor="#3a2a12")

metrics = [
    (57, 34, "traces_service_graph_request_total"),
    (57, 24, "traces_service_graph_request_failed_total"),
    (57, 14, "…_request_server_seconds_bucket"),
]
for cx, cy, t in metrics:
    node(cx, cy, t, "", C_BLUE, bw=30, bh=5.6)

node(83, 24, "Mimir", "", C_PURPLE, bw=13, bh=6)
node(83, 10, "Grafana", "Node Graph 패널", C_GREEN, bw=15, bh=7)

# arrows: Ingester -> processor
arrow(17.5, 24, 18.8, 24, color=C_ACCENT, lw=1.9)
# processor -> 3 metrics (source spread to avoid overlap)
arrow(34, 26.5, 41.5, 33.5, color=C_ACCENT, lw=1.7)
arrow(35, 24, 41.5, 24, color=C_ACCENT, lw=1.7)
arrow(34, 21.5, 41.5, 14.5, color=C_ACCENT, lw=1.7)
# 3 metrics -> Mimir
arrow(72, 34, 77, 26, color=C_VIOLET, lw=1.6)
arrow(72, 24, 76.5, 24, color=C_VIOLET, lw=1.6)
arrow(72, 14, 77, 22, color=C_VIOLET, lw=1.6)
# Mimir -> Grafana
arrow(83, 20.8, 83, 13.6, color=C_GREEN, lw=1.9)

# bottom
text(50, 3.2, "별도 서비스 맵 도구 없이 트레이스 계측만으로 실시간 아키텍처 다이어그램(노드-엣지 그래프)을 얻는다",
     size=9.5, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "23-service-graph.png")
