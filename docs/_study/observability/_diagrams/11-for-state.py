"""CH11 for 상태 전이 — Inactive / Pending / Firing (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_TEXT, C_DIM, C_ACCENT, C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE)

fig, ax = new_fig(w=15, h=8.4, ymax=52)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 49.0, "for와 상태 전이 — Inactive → Pending → Firing", size=19, weight="bold")
text(50, 45.8, "for는 일시적 스파이크(flapping)로 인한 오탐을 걸러내는 장치",
     size=11.5, color=C_DIM)

# ---- states ----
states = [
    (17, C_GRAY, "Inactive", "조건 거짓 · 평상시"),
    (50, C_BLUE, "Pending", "조건 참 직후\nfor 타이머 · 미전송"),
    (83, C_BROWN, "Firing", "for 내내 참\nAlertmanager로 전송"),
]
for xc, fc, t, d in states:
    box(xc - 11, 28, 22, 11, fc, ec=C_ACCENT, lw=1.8)
    text(xc, 35.6, t, size=13, weight="bold", color=C_ACCENT)
    text(xc, 31.4, d, size=8.6, color=C_TEXT)

# start dot
ax.plot(4, 33.5, "o", color=C_ACCENT, markersize=9, zorder=6)
arrow(5, 33.5, 6, 33.5, color=C_ACCENT, lw=2.0)

# ---- forward transitions (top) ----
arrow(28, 34.5, 39, 34.5, color=C_ACCENT, lw=2.2)
text(33.5, 37.0, "expr 참", size=8.4, color=C_ACCENT, weight="bold")
arrow(61, 34.5, 72, 34.5, color=C_ACCENT, lw=2.2)
text(66.5, 37.0, "for 기간 연속 참", size=8.4, color=C_ACCENT, weight="bold")

# ---- self loop on Firing ----
arrow(80, 39, 86, 39, color=C_ORANGE, lw=2.0, rad=-1.0, style="-|>")
text(83, 45.4, "expr 계속 참 → AM으로 계속 전송", size=8.0, color=C_ORANGE, weight="bold")

# ---- backward transitions (bottom, curved) ----
arrow(45, 28, 22, 28, color="#c08a8a", lw=2.0, rad=-0.32)
text(33.5, 20.6, "for 전에 거짓", size=8.2, color="#c08a8a", weight="bold")
arrow(78, 28, 24, 28, color="#c08a8a", lw=2.0, rad=-0.24)
text(52, 13.8, "expr 거짓 → Inactive", size=8.6, color="#c08a8a", weight="bold")

# bottom
text(50, 6.2, "치명적 조건(up == 0 인프라 다운)은 for를 짧게/생략 · 노이즈 민감 조건(에러율 임계)은 for를 길게",
     size=9.8, color=C_ACCENT, weight="bold")
text(50, 3.4, "Firing에 도달해야 Alertmanager로 알림 전송 — Pending 동안은 for 타이머만 돌고 전송되지 않는다",
     size=8.8, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "11-for-state.png")
