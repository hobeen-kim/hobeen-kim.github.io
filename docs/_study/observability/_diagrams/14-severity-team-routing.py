"""CH14 severity×team 2축 라우팅 트리 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=8.6, ymax=58)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 54.5, "severity × team 2축 라우팅 설계", size=19, weight="bold")
text(50, 51.5, "severity로 채널 긴급도를, team으로 수신 대상을 정한다 · 라벨 누락은 fallback으로 방어",
     size=11, color=C_DIM)

# ---- Root ----
box(36, 44, 28, 5.4, C_BLUE, ec=C_ACCENT, lw=1.8)
text(50, 46.9, "Root", size=11.5, weight="bold", color=C_ACCENT)
text(50, 44.4, "default: slack-platform-general", size=8.8, color="#d4dae0")

# ---- severity decision ----
box(42, 36, 16, 4.6, C_GRAY, ec=C_ORANGE, lw=1.6)
text(50, 38.3, "severity", size=11, weight="bold", color=C_ORANGE)
arrow(50, 44, 50, 40.6, color=C_EDGE, lw=1.6)

# ---- critical branch (left) ----
box(6, 27, 20, 4.6, C_GRAY, ec="#c96f5a", lw=1.6)
text(16, 29.3, "team (critical)", size=10, weight="bold", color="#c96f5a")
arrow(44, 36, 20, 31.6, color="#c96f5a", lw=1.8)
text(28, 34.5, "critical", size=9, color="#c96f5a", weight="bold")

# critical -> pagerduty receivers (세로 체인)
crit = [
    ("payments", "pagerduty-payments"),
    ("infra", "pagerduty-infra"),
    ("기타/미지정 (fallback)", "pagerduty-platform-oncall"),
]
prev_y = 27
for i, (cond, recv) in enumerate(crit):
    yy = 21 - i * 6
    box(2, yy - 2.3, 30, 4.6, C_BROWN)
    text(17, yy + 0.5, recv, size=9.5, weight="bold")
    text(17, yy - 1.3, cond, size=8, color=C_ORANGE)
    arrow(16, prev_y - (0 if i == 0 else 2.3), 16, yy + 2.3, color="#c96f5a", lw=1.4)
    prev_y = yy

# ---- warning branch (center) ----
box(40, 27, 20, 4.6, C_GRAY, ec=C_ORANGE, lw=1.6)
text(50, 29.3, "team (warning)", size=10, weight="bold", color=C_ORANGE)
arrow(50, 36, 50, 31.6, color=C_ORANGE, lw=1.8)
text(56, 34, "warning", size=9, color=C_ORANGE, weight="bold")

warn = [
    ("payments", "slack-payments"),
    ("infra", "slack-infra"),
]
for i, (cond, recv) in enumerate(warn):
    yy = 21 - i * 6
    box(37, yy - 2.3, 26, 4.6, C_GREEN)
    text(50, yy + 0.5, recv, size=9.5, weight="bold")
    text(50, yy - 1.3, cond, size=8, color=C_ACCENT)
    arrow(50, 27, 50, yy + 2.3, color=C_ORANGE, lw=1.4)

# ---- info branch (right) ----
box(70, 27, 26, 4.6, C_GRAY, ec=C_VIOLET, lw=1.6)
text(83, 29.3, "info", size=10, weight="bold", color=C_VIOLET)
arrow(58, 37, 74, 31.6, color=C_VIOLET, lw=1.8, rad=-0.1)
text(66, 34.5, "info", size=9, color=C_VIOLET, weight="bold")

box(70, 18, 26, 5.4, C_VIOLET.replace("#b9a3e0", "#4a3d63"))
text(83, 20.7, "slack-info-log", size=10, weight="bold")
text(83, 18.4, "채널만, 조용히 기록", size=8.2, color="#cbb8e6")
arrow(83, 27, 83, 23.4, color=C_VIOLET, lw=1.4)

# bottom
text(50, 8, "critical → 사람을 깨우는 채널(PagerDuty), warning → 확인만 하는 채널(Slack)로 분리",
     size=10.5, color=C_ACCENT, weight="bold")
text(50, 4.6, "모든 룰에 severity·team 라벨을 강제하고, 누락 시 fallback receiver로 흘려 알림 유실을 방어 · group_by에 team 포함",
     size=9, color=C_DIM, style="italic")

leg = [
    Line2D([0], [0], color="#c96f5a", lw=2.5, label="critical (PagerDuty)"),
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="warning (Slack)"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, label="info (기록)"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.7, 0.02),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "14-severity-team-routing.png")
