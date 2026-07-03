"""CH22 metrics-generator — trace에서 span/service graph 메트릭 파생 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_PURPLE, C_VIOLET)

fig, ax = new_fig(w=14, h=7, ymax=46)
box, text, arrow = make_helpers(ax)


def node(cx, cy, t, d, c, bw=20, bh=8):
    box(cx - bw / 2, cy - bh / 2, bw, bh, c)
    text(cx, cy + 1.4, t, size=10.5, weight="bold")
    if d:
        text(cx, cy - 1.7, d, size=8.2, color=C_DIM)


# ---- Title ----
text(50, 43, "metrics-generator — trace 데이터로부터 메트릭 실시간 파생", size=17, weight="bold")
text(50, 39.6, "별도 exporter 계측 없이 span 스트림만 관찰해 RED 메트릭과 서비스 그래프를 생성", size=10.5, color=C_DIM)

# nodes
node(11, 22, "Ingester", "span 스트림", C_BROWN, bw=16)
node(30, 22, "metrics-generator", "", C_ORANGE, bw=18, bh=7)
node(56, 30, "span metrics", "traces_spanmetrics_*", C_BLUE, bw=24, bh=8)
node(56, 13, "service graph metrics", "traces_service_graph_*", C_GREEN, bw=24, bh=8)
node(85, 22, "Mimir / Prometheus", "remote_write", C_PURPLE, bw=18, bh=8)

# arrows
arrow(19.2, 22, 20.8, 22, color=C_ACCENT, lw=2.0)
arrow(39.2, 22, 43, 29, color=C_ACCENT, lw=1.9)
arrow(39.2, 22, 43.5, 14.5, color=C_ACCENT, lw=1.9)
arrow(68.2, 30, 76.5, 24, color=C_ORANGE, lw=1.9)
arrow(68.2, 13, 76.5, 20, color=C_ORANGE, lw=1.9)

# bottom
text(50, 3.4, "트레이스만 계측돼 있으면 RED 메트릭과 서비스 의존 그래프를 공짜로 얻는다 — metrics-generator의 실질 가치",
     size=9.5, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "22-metrics-generator.png")
