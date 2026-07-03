"""CH15 multi-window multi-burn-rate — 긴/짧은 윈도 AND 로직 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=14, h=8.2, ymax=56)
box, text, arrow = make_helpers(ax)

text(50, 52.5, "multi-window multi-burn-rate 알림", size=19, weight="bold")
text(50, 49.4, "긴 윈도(지속성) AND 짧은 윈도(현재성) — 둘 다 참일 때만 발화", size=11.5, color=C_DIM)

# two conditions on left
box(4, 37, 34, 8.5, C_BLUE)
text(21, 43.0, "긴 윈도 조건", size=12.5, weight="bold")
text(21, 40.0, "rate[1h] > threshold\n일시적 튐이 아닌 진짜 추세 보장", size=9.5, color="#d4dae0")

box(4, 25, 34, 8.5, C_GREEN)
text(21, 31.0, "짧은 윈도 조건", size=12.5, weight="bold")
text(21, 28.0, "rate[5m] > threshold\n그 추세가 지금도 계속되는지 재확인", size=9.5, color="#d4dae0")

# AND gate (center)
box(46, 30, 15, 10, C_GRAY, ec=C_ACCENT, lw=2.0)
text(53.5, 36.5, "두 조건", size=12, weight="bold", color=C_ACCENT)
text(53.5, 33.0, "AND", size=16, weight="bold", color=C_ACCENT)

arrow(38, 41.2, 46, 37.5, color=C_ORANGE, lw=2.2)
arrow(38, 29.2, 46, 32.5, color=C_ORANGE, lw=2.2)

# outcomes (right)
box(70, 38, 26, 8, C_GREEN, ec=C_ACCENT, lw=1.8)
text(83, 43.4, "알림 발화", size=13, weight="bold", color=C_ACCENT)
text(83, 40.3, "둘 다 참", size=9.5, color=C_DIM)

box(70, 26, 26, 8, "#3a2a2a", ec=C_BROWN)
text(83, 31.4, "발화 안 함", size=13, weight="bold", color=C_ORANGE)
text(83, 28.3, "하나라도 거짓", size=9.5, color=C_DIM)

arrow(61, 36.5, 70, 41.5, color=C_ACCENT, lw=2.2)
arrow(61, 33.5, 70, 30.0, color=C_BROWN, lw=2.2)

# single-window pitfalls (bottom)
text(50, 20.0, "단일 윈도만 감시하면 생기는 문제", size=11.5, weight="bold", color=C_VIOLET)
box(6, 8, 42, 9, "#2a2440", ec="#7a68a0")
text(27, 14.2, "긴 윈도만 봤다면", size=11, weight="bold", color="#e7dcff")
text(27, 10.6, "장애가 터진 뒤 반응이 너무 늦다 (반응 지연)", size=9.3, color="#cbb8e6")

box(52, 8, 42, 9, "#2a2440", ec="#7a68a0")
text(73, 14.2, "짧은 윈도만 봤다면", size=11, weight="bold", color="#e7dcff")
text(73, 10.6, "순간 스파이크에도 알림 (오탐·노이즈)", size=9.3, color="#cbb8e6")

text(50, 4.0, "긴 윈도로 지속성 확인 + 짧은 윈도로 현재성 재확인 → 지연과 오탐을 동시에 줄인다",
     size=10, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "15-burn-rate-and.png")
