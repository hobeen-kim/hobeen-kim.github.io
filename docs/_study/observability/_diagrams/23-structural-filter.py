"""CH23 구조 필터 — descendant vs child 연산자 예시 트리 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(ymax=60)
box, text, arrow = make_helpers(ax)


def node(cx, cy, title, meta, fc, ec=C_EDGE, lw=1.4, bw=28, bh=6.6):
    box(cx - bw / 2, cy - bh / 2, bw, bh, fc, ec=ec, lw=lw)
    text(cx, cy + (1.1 if meta else 0), title, size=10.5, weight="bold")
    if meta:
        text(cx, cy - 1.6, meta, size=8.3, color=C_ACCENT)


# ---- Title ----
text(50, 57, "TraceQL 구조 필터 — descendant(>>) vs child(>)", size=18, weight="bold")
text(50, 53.6, "두 span 셀렉터를 구조적 연산자로 묶어 span 사이의 위치 관계까지 조건화", size=11, color=C_DIM)

# tree nodes  (A와 E는 강조 = 매치 대상: teal 테두리)
node(50, 46, "gateway span", "", C_GRAY, ec=C_ACCENT, lw=2.6, bw=26)
node(50, 35, "order-service span", "", C_GRAY, bw=28)
node(28, 24, "payment-service span", "", C_GRAY, bw=26)
node(72, 24, "inventory-service span", "", C_GRAY, bw=26)
node(28, 12, "DB Query span", "db.system=postgresql", C_GRAY, ec=C_ACCENT, lw=2.6, bw=26)

# edges
arrow(50, 42.7, 50, 38.3, color=C_DIM, lw=2.0)
arrow(44, 31.7, 32, 27.3, color=C_DIM, lw=2.0)
arrow(56, 31.7, 68, 27.3, color=C_DIM, lw=2.0)
arrow(28, 20.7, 28, 15.3, color=C_DIM, lw=2.0)

# match annotations
box(60, 8, 37, 12, C_GRAY, ec=C_EDGE, lw=1.3)
text(78.5, 17.4, "{ … \"gateway\" } >> { … postgresql }", size=9, color=C_ACCENT, weight="bold")
text(78.5, 14.6, "→ 매치 (A·E가 같은 trace 안 descendant)", size=8.4, color=C_GREEN)
text(78.5, 11.8, "{ … \"gateway\" } > { … postgresql }", size=9, color=C_VIOLET, weight="bold")
text(78.5, 9.2, "→ 불일치 (사이에 order·payment span 존재)", size=8.4, color=C_ORANGE)

# bottom
text(50, 3.2, "연산자: >> descendant · > child · << ancestor · < parent · ~ sibling · && 같은 trace 내 모두 · || 하나라도",
     size=9.3, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], marker="s", color=C_BG, markerfacecolor=C_GRAY,
           markeredgecolor=C_ACCENT, markeredgewidth=2, markersize=13, lw=0,
           label="셀렉터 매치 대상 span (teal 테두리)"),
]
ax.legend(handles=leg, loc="upper left", bbox_to_anchor=(0.02, 0.30),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "23-structural-filter.png")
