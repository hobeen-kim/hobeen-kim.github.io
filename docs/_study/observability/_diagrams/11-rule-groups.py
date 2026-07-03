"""CH11 룰 그룹 평가 — 그룹 내 순차 · 그룹 간 병렬 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_TEXT, C_DIM, C_ACCENT, C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE)

fig, ax = new_fig(w=15, h=8.6, ymax=54)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 51.0, "룰 그룹 평가 — 그룹 내 순차 · 그룹 간 병렬", size=19, weight="bold")
text(50, 47.8, "같은 그룹의 룰은 파일 순서대로 순차 평가 → 앞 룰 결과를 뒤 룰이 즉시 참조",
     size=11, color=C_DIM)

# ================= Group A =================
box(3, 30, 68, 14, C_GRAY, ec=C_ACCENT, lw=1.8)
text(9, 41.4, "그룹 A", size=12, weight="bold", color=C_ACCENT, ha="left")
text(24, 41.4, "interval: 30s · 순차 평가", size=9, color=C_DIM, ha="left")
rules_a = [
    (14, "rule 1", ""),
    (35, "rule 2", "rule 1 결과 참조 가능"),
    (56, "rule 3", ""),
]
for xc, t, d in rules_a:
    box(xc - 8, 32, 16, 6.2, C_GREEN)
    text(xc, 35.9 if d else 35.1, t, size=10, weight="bold")
    if d:
        text(xc, 33.2, d, size=7.2, color=C_DIM)
arrow(22, 35.1, 27, 35.1, color=C_ORANGE, lw=2.0)
arrow(43, 35.1, 48, 35.1, color=C_ORANGE, lw=2.0)

# ================= Group B =================
box(3, 10, 48, 14, C_GRAY, ec=C_ACCENT, lw=1.8)
text(9, 21.4, "그룹 B", size=12, weight="bold", color=C_ACCENT, ha="left")
text(24, 21.4, "interval: 1m · 순차 평가", size=9, color=C_DIM, ha="left")
rules_b = [(16, "rule 4"), (37, "rule 5")]
for xc, t in rules_b:
    box(xc - 8, 12, 16, 6.2, C_BLUE)
    text(xc, 15.1, t, size=10, weight="bold")
arrow(24, 15.1, 29, 15.1, color=C_ORANGE, lw=2.0)

# ---- independence note ----
box(58, 10, 38, 14, C_BROWN)
text(77, 20.4, "두 그룹은 독립적으로 병렬 평가", size=10.5, weight="bold", color=C_ACCENT)
text(77, 16.6, "서로 순서를 보장하지 않는다", size=9, color=C_TEXT)
text(77, 13.2, "B가 A의 결과에 의존하면\n반드시 같은 그룹에 A를 앞에 둔다", size=8.2, color=C_DIM)

# dashed independence connector
arrow(37, 30, 55, 24, color="#8a94a0", lw=1.8, ls="--", style="-")

# bottom
text(50, 5.4, "interval이 짧을수록 반응은 빠르지만 평가 비용 증가 — 대부분 전역 기본값(예: 1분), 민감한 그룹만 짧게",
     size=9.8, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="그룹 내 순차 평가"),
    Line2D([0], [0], color="#8a94a0", lw=2.5, ls="--", label="그룹 간 독립 · 병렬"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.03),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "11-rule-groups.png")
