"""CH14 inhibition — source/target/equal 기반 억제 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=14, h=6.6, ymax=44)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 40.5, "inhibition — 인과관계 기반 억제", size=19, weight="bold")
text(50, 37.5, "더 심각한 source 알림이 firing이면 equal 라벨이 같은 target 알림을 억제",
     size=11, color=C_DIM)

# ---- source: ClusterDown ----
box(4, 24, 24, 8, "#5a3838", ec="#c96f5a", lw=1.8)
text(16, 29.5, "ClusterDown", size=12.5, weight="bold")
text(16, 26.6, "firing · source", size=9.5, color="#e0a89b")

# ---- target: PodDown x40 ----
box(4, 9, 24, 8, C_GRAY)
text(16, 14.5, "PodDown x40", size=12.5, weight="bold")
text(16, 11.6, "같은 cluster · target", size=9.5, color=C_DIM)

# ---- inhibit rule (center) ----
box(38, 15, 24, 12, C_BROWN, ec=C_ORANGE, lw=1.8)
text(50, 23, "inhibit_rule", size=13, weight="bold", color=C_ORANGE)
text(50, 19.8, "equal: cluster", size=10.5)
text(50, 17, "source firing 시\ntarget 억제", size=9, color=C_DIM)

# ---- right top: notify ClusterDown ----
box(72, 24, 24, 8, C_GREEN, ec=C_ACCENT, lw=1.6)
text(84, 29.5, "Slack / PagerDuty", size=11.5, weight="bold")
text(84, 26.6, "ClusterDown 통지됨", size=9.5, color=C_ACCENT)

# ---- right bottom: suppressed ----
box(72, 9, 24, 8, "#26313a")
text(84, 14.5, "표시는 되지만", size=11, weight="bold", color=C_DIM)
text(84, 11.6, "알림 발송 안 됨 (suppressed)", size=9.2, color=C_DIM)

# arrows
arrow(28, 28, 38, 24, color="#c96f5a", lw=2.2, rad=-0.08)
text(33, 27.5, "source", size=8.8, color="#c96f5a", weight="bold")
arrow(28, 13, 38, 17, color=C_GRAY.replace("#26313a", "#8a9199"), lw=2.0, rad=0.08)
text(33, 12.3, "target", size=8.8, color=C_DIM, weight="bold")

# clusterdown -> notify
arrow(28, 30, 72, 28, color=C_ACCENT, lw=2.0, rad=-0.06)
text(50, 32.2, "통지됨", size=9, color=C_ACCENT, weight="bold")

# inhibit -> suppressed
arrow(56, 15, 72, 13, color=C_ORANGE, lw=2.2, rad=-0.06)
text(66, 14.9, "억제됨, 통지 안 됨", size=8.8, color=C_ORANGE, weight="bold")

# bottom
text(50, 4, "억제된 알림은 UI/API 상 여전히 firing으로 보이지만 notification pipeline에서 발송만 막힌다",
     size=10.5, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color="#c96f5a", lw=2.5, label="source (억제 유발)"),
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="통지"),
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="억제 (발송 차단)"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.02),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "14-inhibition.png")
