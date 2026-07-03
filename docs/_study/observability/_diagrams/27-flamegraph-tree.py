"""CH27 플레임그래프 읽는 법 — 스택 + 값을 가로 막대 스택으로 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "플레임그래프 읽는 법 — x축 = 집계 비중, y축 = 스택 깊이", size=20, weight="bold")
text(50, 56.6, "각 프레임 너비는 전체 샘플 중 그 함수가 등장한 비율에 비례 (실행 순서와 무관)",
     size=12, color=C_DIM)

# ---- flamegraph geometry: root at bottom ----
X0, W100 = 6.0, 88.0          # x=6 → 0%, width for 100%
def X(pct):
    return X0 + pct * (W100 / 100.0)
BH = 7.0                       # bar height


def frame(start_pct, width_pct, level, label, pct, fc, ec=C_EDGE):
    y = 12 + level * (BH + 1.6)
    x = X(start_pct)
    w = width_pct * (W100 / 100.0)
    box(x, y, w, BH, fc, ec=ec, lw=1.4)
    cx = x + w / 2
    if width_pct >= 12:
        text(cx, y + BH * 0.60, label, size=10, weight="bold")
        text(cx, y + BH * 0.26, f"{pct}%", size=9, color=C_ACCENT)
    else:
        text(cx, y + BH * 0.60, label, size=8, weight="bold")
        text(cx, y + BH * 0.24, f"{pct}%", size=7.5, color=C_ACCENT)


# L0 root
frame(0, 100, 0, "main", 100, C_GRAY, ec=C_ACCENT)
# L1
frame(0, 95, 1, "handleRequest", 95, C_BLUE)
# L2
frame(0, 40, 2, "parseJSON", 40, C_GREEN)
frame(40, 50, 2, "dbQuery", 50, C_BROWN)
frame(90, 5, 2, "writeLog", 5, "#4a3d63")
# L3 (children of dbQuery: 40~90)
frame(40, 30, 3, "encodeRow", 30, C_ORANGE)
frame(70, 20, 3, "acquireConn", 20, "#4a3d63")

# depth axis marker
ax.annotate("", xy=(3.2, 12 + 3 * (BH + 1.6) + BH), xytext=(3.2, 12),
            arrowprops=dict(arrowstyle="-|>", color=C_DIM, lw=1.6), zorder=4)
ax.text(2.0, 12 + 2 * (BH + 1.6), "스택 깊이 (y축)", fontsize=9, color=C_DIM,
        rotation=90, ha="center", va="center", zorder=5)
text(50, 8.4, "◀  집계 비중 (x축) — 너비 넓을수록 리소스 소비 큼  ▶", size=9.5, color=C_DIM)

# bottom
text(50, 4.6, "가장 넓은 프레임을 root에서부터 추적하면 리소스를 가장 많이 소비하는 호출 경로를 바로 찾는다",
     size=10, color=C_ACCENT, weight="bold")
text(50, 2.2, "dbQuery(50%) 위에 encodeRow(30%)·acquireConn(20%)이 쌓이는 식 — 위 프레임은 자식 함수",
     size=9, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "27-flamegraph-tree.png")
