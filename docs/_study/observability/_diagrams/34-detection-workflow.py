"""CH34 카디널리티 탐지 워크플로우 — 급증 알림부터 통제까지 (matplotlib → PNG)."""
from matplotlib.patches import Polygon
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=9.2, ymax=62)
box, text, arrow = make_helpers(ax)


def diamond(cx, cy, w, h, fc, ec=C_ORANGE, lw=1.6):
    pts = [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=fc, edgecolor=ec,
                         linewidth=lw, zorder=3))


text(50, 59.6, "카디널리티 탐지 워크플로우", size=20, weight="bold")
text(50, 56.8, "급증 알림 → status page → 상위 메트릭 → (오프라인 분석 분기) → 원인 라벨 특정 → 통제",
     size=11.5, color=C_DIM)

# A
box(32, 49.5, 36, 5.5, C_BLUE)
text(50, 52.25, "prometheus_tsdb_head_series 급증 알림", size=11, weight="bold")
# B decision
diamond(50, 44.5, 34, 7.5, C_BROWN)
text(50, 44.5, "TSDB status page 확인", size=10)
# C
box(33, 33, 34, 5.5, C_GRAY)
text(50, 35.75, "seriesCountByMetricName\n상위 메트릭 확인", size=9.8)
# D decision
diamond(50, 26, 32, 8, C_BROWN)
text(50, 26, "오프라인 블록\n분석 필요?", size=10)
# E (yes, left) / F (no, right)
box(8, 14, 32, 6.5, C_GREEN)
text(24, 17.25, "promtool tsdb analyze", size=10.5)
box(60, 14, 34, 6.5, C_GREEN)
text(77, 18.0, "topk(count by (__name__))", size=9.8)
text(77, 15.4, "PromQL로 실시간 확인", size=9, color=C_DIM)
# G
box(33, 6, 34, 5, C_GRAY, ec=C_ACCENT, lw=1.4)
text(50, 8.5, "원인 라벨 특정", size=11, weight="bold")
# H
box(28, 0.3, 44, 4.6, C_BROWN, ec=C_ORANGE, lw=1.6)
text(50, 2.6, "metric_relabel_configs로 통제", size=11, weight="bold", color=C_ORANGE)

# arrows
arrow(50, 49.5, 50, 48.25, color=C_ACCENT, lw=2.0)
arrow(50, 40.75, 50, 38.5, color=C_ACCENT, lw=2.0)
arrow(50, 33, 50, 30, color=C_ACCENT, lw=2.0)
# D -> E (yes)
arrow(34, 26, 24, 20.5, color=C_ACCENT, lw=2.0)
text(26, 24, "예", size=9.5, color=C_ACCENT, weight="bold")
# D -> F (no)
arrow(66, 26, 77, 20.5, color=C_ACCENT, lw=2.0)
text(73, 24, "아니오", size=9.5, color=C_ACCENT, weight="bold")
# E -> G , F -> G
arrow(24, 14, 40, 11, color=C_ACCENT, lw=2.0)
arrow(77, 14, 60, 11, color=C_ACCENT, lw=2.0)
# G -> H
arrow(50, 6, 50, 4.9, color=C_ORANGE, lw=2.2)

leg = [
    Line2D([0], [0], marker="D", color="none", markerfacecolor=C_BROWN,
           markeredgecolor=C_ORANGE, markersize=11, label="판단(분기) 노드"),
]
ax.legend(handles=leg, loc="lower right", bbox_to_anchor=(0.995, 0.02),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.985, bottom=0.02)
save(fig, "34-detection-workflow.png")
