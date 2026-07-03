"""CH14 route 트리 — matcher 분기와 상속 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=14, h=8.4, ymax=56)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 52.5, "route 트리 — matcher 분기와 상속", size=19, weight="bold")
text(50, 49.5, "루트부터 깊이 우선 탐색 · matcher 일치 시 하위 route로 · 명시 안 한 설정은 부모 상속",
     size=11, color=C_DIM)

def cond(x, y, w, h, s, size=10):
    # decision (diamond-ish rounded box)
    box(x - w / 2, y - h / 2, w, h, C_GRAY, ec=C_ORANGE, lw=1.6)
    text(x, y, s, size=size, weight="bold", color=C_ORANGE)

def recv(x, y, w, h, title, sub="", fc=C_GREEN):
    box(x - w / 2, y - h / 2, w, h, fc)
    if sub:
        text(x, y + 0.9, title, size=9.8, weight="bold")
        text(x, y - 1.1, sub, size=8, color=C_DIM)
    else:
        text(x, y, title, size=9.8, weight="bold")

# ---- Root ----
box(32, 42, 36, 5.4, C_BLUE, ec=C_ACCENT, lw=1.8)
text(50, 44.9, "Root route", size=11.5, weight="bold", color=C_ACCENT)
text(50, 42.4, "receiver: default-slack · group_by: [alertname, cluster]", size=8.6, color="#d4dae0")

# ---- Level 1: severity=critical ? ----
cond(28, 34, 26, 5, 'severity="critical" ?')
arrow(45, 42, 30, 36.5, color=C_EDGE, lw=1.6)

# critical Yes -> pagerduty
recv(78, 34, 22, 5, "pagerduty-oncall", fc=C_BROWN)
arrow(41, 34, 67, 34, color=C_GREEN, lw=2.0)
text(54, 35.6, "Yes · continue=false", size=8.5, color=C_GREEN, weight="bold")

# critical No -> team=payments ?
cond(28, 24, 26, 5, 'team="payments" ?')
arrow(28, 31.5, 28, 26.5, color="#c96f5a", lw=1.8)
text(35.5, 29, "No", size=8.5, color="#c96f5a", weight="bold")

# payments No -> default-slack (루트 receiver)
recv(78, 24, 26, 5, "default-slack", "루트 receiver", fc=C_GRAY)
arrow(41, 24, 65, 24, color="#c96f5a", lw=1.8)
text(53, 25.6, "No", size=8.5, color="#c96f5a", weight="bold")

# payments Yes -> severity=warning ? (payments 하위)
cond(28, 14, 30, 5, 'severity="warning" ?  (payments 하위)', size=9)
arrow(28, 21.5, 28, 16.5, color=C_GREEN, lw=1.8)
text(34.5, 19, "Yes", size=8.5, color=C_GREEN, weight="bold")

# warning Yes -> slack-payments-warning
recv(78, 17, 26, 5, "slack-payments-warning", fc=C_GREEN)
arrow(43, 14.5, 65, 17, color=C_GREEN, lw=2.0, rad=-0.1)
text(54, 17.5, "Yes", size=8.5, color=C_GREEN, weight="bold")

# warning No -> slack-payments (부모 receiver 상속)
recv(78, 10, 26, 5, "slack-payments", "부모 receiver 상속", fc=C_VIOLET.replace("#b9a3e0", "#4a3d63"))
arrow(43, 13.5, 65, 10, color=C_VIOLET, lw=2.0, rad=0.1)
text(54, 10.8, "No · 상속", size=8.5, color=C_VIOLET, weight="bold")

# bottom
text(50, 4, "가장 구체적인 route가 마지막에 이긴다 — 넓은 조건을 앞에, 좁은 조건을 뒤에 두는 실수를 피한다",
     size=10.5, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_GREEN, lw=2.5, label="matcher 일치 (Yes)"),
    Line2D([0], [0], color="#c96f5a", lw=2.5, label="불일치 (No)"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, label="부모 설정 상속"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.02),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "14-route-tree.png")
