"""CH31 RED/USE 대시보드 구성 — drill-down 구조 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_PURPLE)

fig, ax = new_fig(w=14, h=8.6, ymax=56)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 53.0, "RED / USE 대시보드 — drill-down 구조", size=19, weight="bold")
text(50, 50.0, "서비스(RED)와 리소스(USE)를 한 화면에 배치해 이상 → 원인으로 시선만 옮겨 좁혀감",
     size=11, color=C_DIM)

# RED group (left)
box(4, 26, 40, 18, C_BLUE)
text(24, 41.4, "RED 대시보드 (서비스)", size=12, weight="bold", color=C_ACCENT)
red = [("Rate", "요청/초"), ("Errors", "에러율"), ("Duration", "p50 / p95 / p99")]
for i, (t, d) in enumerate(red):
    xx = 8.5 + i * 12
    box(xx, 28.5, 10.5, 8.5, "#1d2733")
    text(xx + 5.25, 34.4, t, size=9.8, weight="bold")
    text(xx + 5.25, 31.4, d, size=7.6, color=C_DIM)

# USE group (right)
box(56, 26, 40, 18, C_GREEN)
text(76, 41.4, "USE 대시보드 (리소스)", size=12, weight="bold", color=C_ACCENT)
use = [("Utilization", "사용률"), ("Saturation", "대기열 / 큐"), ("Errors", "리소스 에러")]
for i, (t, d) in enumerate(use):
    xx = 60.5 + i * 12
    box(xx, 28.5, 10.5, 8.5, "#1d2b24")
    text(xx + 5.25, 34.4, t, size=9.5, weight="bold")
    text(xx + 5.25, 31.4, d, size=7.6, color=C_DIM)

# DRILL box (center-lower)
box(35, 12, 30, 7.5, C_BROWN, ec=C_ORANGE, lw=1.8)
text(50, 15.7, "원인 조사", size=12, weight="bold")

# TRACE box (bottom)
box(35, 2.5, 30, 6.5, C_PURPLE, ec=C_ACCENT, lw=1.6)
text(50, 5.75, "트레이스·프로파일로 drill-down", size=10.5, weight="bold")

# arrows
arrow(24, 26, 40, 19.5, color=C_ACCENT, lw=2.0)
text(28, 22.6, "에러율 급증", size=8.5, color=C_ORANGE, weight="bold")
arrow(76, 26, 60, 19.5, color=C_ACCENT, lw=2.0)
text(72, 22.6, "포화도 급증", size=8.5, color=C_ORANGE, weight="bold")
arrow(50, 12, 50, 9.0, color=C_ACCENT, lw=2.2)

# side note
text(50, 47.0, "상단 RED(요청이 느려졌다) → 하단 USE(왜) → 트레이스/프로파일(어디서)",
     size=9.5, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "31-red-use-dashboard.png")
