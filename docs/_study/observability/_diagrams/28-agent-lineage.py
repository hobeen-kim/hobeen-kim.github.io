"""CH28 Grafana 수집 에이전트의 계보 — 타임라인 다이어그램 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_PURPLE)

fig, ax = new_fig(w=15, h=8.2, ymax=54)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 51.0, "Grafana 수집 에이전트의 계보", size=20, weight="bold")
text(50, 47.8, "Prometheus Agent → Grafana Agent → Flow → Alloy  ·  River를 Alloy 구문으로 개명",
     size=12, color=C_DIM)

# ---- timeline axis ----
ax.plot([6, 94], [24, 24], color=C_EDGE, lw=2.4, zorder=2)

events = [
    ("2020", "Prometheus Agent\nmode 등장", "원격 쓰기 전용 경량 수집 모드", C_GRAY, "up"),
    ("2021", "Grafana Agent 출시", "Prometheus + Promtail 통합", C_BLUE, "down"),
    ("2023", "Grafana Agent Flow", "컴포넌트 그래프(DAG) 도입", C_BROWN, "up"),
    ("2024", "Alloy 출시", "River를 Alloy 구문으로 개명", C_GREEN, "down"),
    ("2025", "Grafana Agent EOL", "Alloy로 완전 이관", C_ACCENT, "up"),
]

xs = [12, 32, 51, 70, 88]
for (yr, title, desc, col, side), x in zip(events, xs):
    # node on axis
    ax.plot([x], [24], "o", color=C_ACCENT, markersize=11, zorder=5)
    text(x, 24, "", size=1)
    if side == "up":
        by = 30.0
        arrow(x, 34.5, x, 25.6, color=C_EDGE, lw=1.4, style="-")
        yr_y = 21.2
    else:
        by = 12.5
        arrow(x, 22.4, x, 17.5, color=C_EDGE, lw=1.4, style="-")
        yr_y = 26.8
    ec = col if col != C_ACCENT else C_ACCENT
    box(x - 8.4, by, 16.8, 6.4,
        col if col != C_ACCENT else "#1d2b28",
        ec=(C_ACCENT if col == C_ACCENT else C_EDGE),
        lw=(2.0 if col == C_ACCENT else 1.4))
    text(x, by + 4.4, title, size=10.5, weight="bold",
         color=(C_ACCENT if col == C_ACCENT else C_TEXT))
    text(x, by + 1.7, desc, size=8, color=C_DIM)
    text(x, yr_y, yr, size=13, weight="bold", color=C_ORANGE)

# bottom summary
text(50, 5.6, "한 갈래의 진화선 — 각 단계가 다음 단계의 토대가 되어 Alloy로 수렴",
     size=11, color=C_ACCENT, weight="bold")
text(50, 2.8, "Alloy = OTel Collector 엔진 + Grafana 자체 구문(구 River) + Prometheus/Loki/Pyroscope 네이티브 컴포넌트",
     size=9, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "28-agent-lineage.png")
