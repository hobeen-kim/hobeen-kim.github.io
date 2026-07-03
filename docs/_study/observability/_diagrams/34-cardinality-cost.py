"""CH34 카디널리티가 세 축(메모리·저장·쿼리)을 동시에 압박해 비용을 지배 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=8, ymax=52)
box, text, arrow = make_helpers(ax)

text(50, 49.4, "카디널리티가 운영 비용을 지배한다", size=20, weight="bold")
text(50, 46.4, "라벨 조합 증가 → 카디널리티 폭발 → 메모리·저장·쿼리를 동시에 압박",
     size=12, color=C_DIM)

# ---- LABEL ----
box(2, 24, 18, 11, C_GRAY)
text(11, 31.5, "라벨 조합 증가", size=11, weight="bold")
text(11, 28.2, "user_id · pod_uid\ntrace_id …", size=9, color=C_DIM)

# ---- CARD ----
box(24, 24, 18, 11, C_BROWN, ec=C_ORANGE, lw=1.8)
text(33, 31.0, "카디널리티\n폭발", size=13, weight="bold", color=C_ORANGE)
text(33, 26.6, "고유 시계열 수 ↑↑", size=8.8, color=C_DIM)

arrow(20, 29.5, 24, 29.5, color=C_ORANGE, lw=2.2)

# ---- three axes ----
axes = [
    (41, C_BLUE, "메모리", "head 블록 · OOM 위험 · churn"),
    (29.5, C_GREEN, "저장", "인덱스 크기 · 압축(compaction) 비용"),
    (18, C_PURPLE if False else "#4a3d63", "쿼리", "스캔 시계열 수 ↑ · 지연 ↑"),
]
for y, fc, t, d in axes:
    box(50, y - 4, 30, 8, fc)
    text(56, y + 1.4, t, size=12, weight="bold", ha="left")
    text(56, y - 1.8, d, size=8.8, color=C_DIM, ha="left")
    arrow(42, 29.5, 50, y, color=C_ORANGE, lw=2.0)

# ---- COST ----
box(84, 24, 14, 11, C_GRAY, ec=C_ACCENT, lw=1.8)
text(91, 29.5, "운영 비용", size=13, weight="bold", color=C_ACCENT)
for y, *_ in axes:
    arrow(80, y, 84, 29.5, color=C_DIM, lw=1.6)

text(50, 2.6, "라벨 하나가 늘면 카디널리티는 곱셈으로 증가 — 무한 카디널리티 라벨은 수백만 시계열로 폭발",
     size=10, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "34-cardinality-cost.png")
