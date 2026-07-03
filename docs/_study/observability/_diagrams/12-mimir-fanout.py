"""CH12 여러 Prometheus → Mimir 장기 저장·전역 쿼리 연동 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=14, h=6.6, ymax=44)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 40.5, "여러 Prometheus → Mimir 장기 저장·전역 쿼리", size=19, weight="bold")
text(50, 37.5, "remote_write로 중앙 집중  →  오브젝트 스토리지 장기 블록 + 전역 쿼리 → Grafana",
     size=11, color=C_DIM)

# ---- left: Prometheus instances ----
for i, name in enumerate(["Prometheus #1", "Prometheus #2", "Prometheus #N"]):
    yy = 28 - i * 8.5
    box(3, yy - 3, 20, 6, C_GRAY)
    text(13, yy, name, size=11, weight="bold")

# ---- center: Mimir ----
box(33, 8, 26, 26, C_GREEN, ec=C_ACCENT, lw=2.0)
text(46, 30.5, "Mimir", size=15, weight="bold", color=C_ACCENT)
text(46, 27, "distributor → ingester", size=10.5)
text(46, 23.5, "수평 확장 가능한\n저장·질의 계층", size=9.5, color=C_DIM)
box(35, 12, 22, 8, "#1d2b24")
text(46, 17, "단일 노드·짧은 retention", size=9.5, color="#d4dae0")
text(46, 14, "한계를 넘어선다", size=9.5, color="#d4dae0")

# ---- right top: Object storage ----
box(66, 24, 30, 10, C_BROWN)
text(81, 30.5, "오브젝트 스토리지", size=12.5, weight="bold")
text(81, 27, "장기 블록 저장", size=10, color=C_DIM)

# ---- right mid: Query Frontend ----
box(66, 12, 20, 9, C_BLUE)
text(76, 18, "Query Frontend", size=11, weight="bold")
text(76, 14.6, "전역 쿼리", size=9.5, color=C_DIM)

# ---- right: Grafana ----
box(89, 12, 8, 9, C_ORANGE)
text(93, 16.5, "Grafana", size=10, weight="bold", color="#241a10", ha="center")

# arrows: prometheus -> mimir
for i in range(3):
    yy = 28 - i * 8.5
    arrow(23, yy, 33, 21, color=C_ACCENT, lw=2.0, rad=0.0)
text(27, 26.5, "remote_write", size=9, color=C_ACCENT, weight="bold")

# mimir -> obj / QF
arrow(59, 24, 66, 28, color=C_VIOLET, lw=2.0)
arrow(59, 17, 66, 16.5, color=C_ACCENT, lw=2.0)
# QF -> grafana
arrow(86, 16.5, 89, 16.5, color=C_ACCENT, lw=2.0)

# bottom
text(50, 4, "여러 인스턴스가 하나의 Mimir로 remote_write → 로컬 TSDB의 단일 노드·짧은 retention 한계 극복",
     size=10.5, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="remote_write / 쿼리 경로"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, label="장기 블록 저장"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.02),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "12-mimir-fanout.png")
