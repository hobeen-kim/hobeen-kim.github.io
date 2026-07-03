"""CH13 Prometheus와 Alertmanager 역할 분리 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=14, h=7, ymax=46)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 42.5, "Prometheus와 Alertmanager의 역할 분리", size=19, weight="bold")
text(50, 39.5, "Prometheus는 룰 평가·firing까지  →  Alertmanager는 라우팅·중복 제거·전달",
     size=11, color=C_DIM)

# ---- left group: Prometheus ----
box(3, 10, 26, 24, C_GRAY)
text(16, 31.5, "Prometheus", size=13.5, weight="bold")
box(6, 22, 20, 6, C_BLUE)
text(16, 25.6, "Alerting Rule", size=10.5, weight="bold")
text(16, 23.4, "PromQL 조건", size=9, color=C_DIM)
box(6, 12.5, 20, 6, C_BLUE)
text(16, 16.1, "룰 평가 엔진", size=10.5, weight="bold")
text(16, 13.9, "evaluation_interval", size=9, color=C_DIM)
arrow(16, 22, 16, 18.5, color=C_ACCENT, lw=2.0)

# ---- center group: Alertmanager ----
box(37, 10, 30, 24, C_GREEN, ec=C_ACCENT, lw=2.0)
text(52, 31.5, "Alertmanager", size=13.5, weight="bold", color=C_ACCENT)
for i, (t, d) in enumerate([
    ("알림 수신", ""),
    ("파이프라인", "dedup / group / inhibit\n/ silence / route"),
    ("Notifier", ""),
]):
    yy = 27.5 - i * 6.0
    h = 4.6 if d else 3.4
    box(39, yy - h / 2, 26, h, "#1d2b24")
    if d:
        text(52, yy + 0.9, t, size=10, weight="bold")
        text(52, yy - 0.9, d, size=8, color=C_DIM)
    else:
        text(52, yy, t, size=10.5, weight="bold")
arrow(52, 25.2, 52, 21.9, color=C_ACCENT, lw=1.8)
arrow(52, 15.2, 52, 13.4, color=C_ACCENT, lw=1.8)

# ---- right: channels ----
for i, (name, c) in enumerate([("Slack", C_BROWN), ("PagerDuty", C_BROWN), ("Webhook", C_BROWN)]):
    yy = 29 - i * 7
    box(75, yy - 2.6, 20, 5.2, c)
    text(85, yy, name, size=11, weight="bold")

# arrows: Prometheus -> Alertmanager
arrow(29, 15.5, 37, 27, color=C_ORANGE, lw=2.4, rad=-0.1)
text(33, 24, "HTTP POST\n/api/v2/alerts\n(firing 상태)", size=8.5, color=C_ORANGE, weight="bold")

# Notifier -> channels
for i in range(3):
    yy = 29 - i * 7
    arrow(67, 12.5, 75, yy, color=C_ACCENT, lw=1.8, rad=0.0)

# bottom
text(50, 5, "Prometheus는 pending·firing 상태만 관리하고, firing이 된 알림만 Alertmanager로 전송한다",
     size=10.5, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="firing 알림 전송"),
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="내부 처리 / 채널 전달"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.02),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "13-role-split.png")
