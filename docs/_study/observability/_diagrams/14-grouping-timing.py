"""CH14 grouping 타이밍 — group_wait·group_interval·repeat_interval (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=9, ymax=60)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 57, "grouping 발송 타이밍", size=20, weight="bold")
text(50, 54, "group_wait(초기 대기) · group_interval(갱신 최소 간격) · repeat_interval(재알림 주기)",
     size=11.5, color=C_DIM)

# ---- lifelines ----
actors = [
    (14, "알림 발화", C_GRAY),
    (50, "그룹\n(alertname=DiskFull)", C_GREEN),
    (86, "알림 전송", C_BROWN),
]
for x, name, c in actors:
    box(x - 13, 47, 26, 3.8, c)
    text(x, 48.9, name, size=10.5, weight="bold")
    ax.plot([x, x], [5, 47], color=C_EDGE, lw=1.2, ls="--", zorder=1)

XA, XG, XN = 14, 50, 86

def ev(x1, x2, y, label, color=C_ACCENT):
    arrow(x1, y, x2, y, color=color, lw=2.0)

def tstamp(y, s):
    text(3, y, s, size=9, color=C_ORANGE, weight="bold", ha="left")

# t=0s 첫 알림 도착
tstamp(44, "t=0s")
ev(XA, XG, 44, "")
text(32, 45.3, "첫 알림 도착 (그룹 생성)", size=8.8, color=C_TEXT)

# group_wait note
box(37, 39, 26, 3.4, "#161c22", ec=C_VIOLET, lw=1.4)
text(50, 40.7, "group_wait=30s 대기", size=9, color=C_VIOLET, weight="bold")

# t=10s 추가 도착
tstamp(35, "t=10s")
ev(XA, XG, 35, "")
text(32, 36.3, "같은 그룹 알림 2개 추가 도착", size=8.8, color=C_TEXT)

# t=30s 1차 발송
tstamp(29, "t=30s")
ev(XG, XN, 29, "", color=C_GREEN)
text(68, 30.3, "3개 알림 묶어서 1차 발송", size=8.8, color=C_GREEN, weight="bold")

# t=45s 추가 도착
tstamp(23, "t=45s")
ev(XA, XG, 23, "")
text(32, 24.3, "같은 그룹 알림 1개 추가 도착", size=8.8, color=C_TEXT)

# group_interval note
box(37, 17.5, 26, 3.4, "#161c22", ec=C_ORANGE, lw=1.4)
text(50, 19.2, "group_interval=5m 대기 중\n→ 즉시 발송 안 함", size=8.3, color=C_ORANGE, weight="bold")

# t=5m30s 2차 발송
tstamp(13, "t=5m30s")
ev(XG, XN, 13, "", color=C_GREEN)
text(68, 14.3, "추가분 포함 2차 발송", size=8.8, color=C_GREEN, weight="bold")

# t=4h30s repeat
tstamp(8.5, "t=4h30s")
ev(XG, XN, 8.5, "", color=C_ORANGE)
text(68, 9.8, "repeat_interval 도달, 재알림", size=8.8, color=C_ORANGE, weight="bold")

# bottom
text(50, 4, "group_wait 짧으면 낱개 발송, 길면 급한 첫 알림 지연 · repeat_interval은 미해결 장애 리마인드",
     size=10, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="알림 도착 (그룹으로)"),
    Line2D([0], [0], color=C_GREEN, lw=2.5, label="그룹 발송"),
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="repeat 재알림"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.07),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "14-grouping-timing.png")
