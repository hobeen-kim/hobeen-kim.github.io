"""CH07 §1 스크레이프 동작 — up 메트릭과 타임아웃 시퀀스 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_PURPLE, C_ORANGE, C_VIOLET)

C_RED = "#c0524a"

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "스크레이프 동작과 up 메트릭", size=20, weight="bold")
text(50, 56.6, "스크레이프 성공/실패 자체가 up{instance} 값으로 기록된다 — 타깃의 생사가 곧 신호",
     size=12, color=C_DIM)

# ---- lifelines ----
PX, TX = 34, 74
box(26.5, 50.5, 15, 5.2, C_GRAY, ec=C_ACCENT, lw=1.6)
text(34, 53.1, "Prometheus", size=11, weight="bold", color=C_ACCENT)
box(66.5, 50.5, 15, 5.2, C_BROWN)
text(74, 53.1, "타깃", size=11, weight="bold")
for x in (PX, TX):
    ax.plot([x, x], [7, 50.5], color=C_EDGE, ls=(0, (4, 3)), lw=1.0, zorder=1)

# ---- config note ----
box(30, 44.3, 48, 4.4, "#141b20", ec=C_ACCENT, lw=1.3)
text(54, 46.5, "scrape_interval = 15s     ·     scrape_timeout = 10s (≤ interval)",
     size=9.5, color=C_ACCENT, weight="bold")

def req(y, tlabel):
    arrow(PX, y, TX, y, color=C_BLUE, lw=2.0)
    text((PX + TX) / 2, y + 1.4, "GET /metrics", size=8.5, color="#8fb4cf", weight="bold")
    text(PX - 8, y, tlabel, size=8.5, color=C_DIM, weight="bold")

# t = 0s : 성공
req(41, "t=0s")
arrow(TX, 37, PX, 37, color=C_GREEN, lw=2.0, ls="--")
text(54, 38.4, "200 OK (본문)", size=8.5, color="#7fbf87")
box(4, 34.8, 19, 4.6, "#1d2b24", ec=C_GREEN, lw=1.4)
text(13.5, 37.1, "up{instance} = 1", size=9, weight="bold", color="#7fbf87")

# t = 15s : 타임아웃
req(30, "t=15s")
arrow(TX, 26, PX + 8, 26, color=C_RED, lw=2.0, ls="--", style="-")
text(PX + 7.2, 26, "X", size=12, color=C_RED, weight="bold")
text(56, 27.4, "타임아웃 (10s 초과 · 응답 없음)", size=8.5, color=C_RED)
box(4, 23.7, 19, 4.6, "#2a1a18", ec=C_RED, lw=1.4)
text(13.5, 26.0, "up{instance} = 0 기록", size=9, weight="bold", color="#e0928a")

# t = 30s : 복구
req(19, "t=30s")
arrow(TX, 15, PX, 15, color=C_GREEN, lw=2.0, ls="--")
text(54, 16.4, "200 OK (복구)", size=8.5, color="#7fbf87")
box(4, 12.7, 19, 4.6, "#1d2b24", ec=C_GREEN, lw=1.4)
text(13.5, 15.0, "up{instance} = 1", size=9, weight="bold", color="#7fbf87")

# bottom
text(50, 4.6, "타깃은 해시 오프셋으로 분산 스크레이프 · up == 0 은 가장 기본적이면서 중요한 알림 조건",
     size=10.5, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_BLUE, lw=2.5, label="스크레이프 요청"),
    Line2D([0], [0], color=C_GREEN, lw=2.5, ls="--", label="성공 응답 → up=1"),
    Line2D([0], [0], color=C_RED, lw=2.5, ls="--", label="타임아웃 → up=0"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.02),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "07-scrape-behavior.png")
