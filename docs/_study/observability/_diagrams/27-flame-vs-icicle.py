"""CH27 flame graph vs icicle — 방향만 반대인 동일 정보 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "flame graph vs icicle — 방향만 반대, 정보는 동일", size=20, weight="bold")
text(50, 56.6, "flame은 root가 맨 아래(위로 쌓임), icicle은 root가 맨 위(아래로 쌓임)",
     size=12, color=C_DIM)

stack = [("main", C_GRAY), ("handleRequest", C_BLUE), ("dbQuery", C_BROWN)]

# ================= left: flame graph (root bottom) =================
box(4, 10, 44, 42, C_GRAY, ec=C_EDGE, lw=1.4)
text(26, 49.4, "flame graph (전통 방향)", size=13, weight="bold", color=C_ORANGE)
text(26, 46.8, "Brendan Gregg 원형 · root가 맨 아래", size=9, color=C_DIM, style="italic")

for i, (t, c) in enumerate(stack):
    y = 15 + i * 9.5
    ec = C_ACCENT if i == 0 else C_EDGE
    box(9, y, 34, 7, c, ec=ec, lw=1.6 if i == 0 else 1.4)
    text(26, y + 3.5, t, size=11.5, weight="bold")
    if i < 2:
        arrow(26, y + 7, 26, y + 9.5, color=C_ORANGE, lw=2.0)
text(26, 12.2, "root", size=8.5, color=C_ACCENT, weight="bold")
ax.text(46, 43, "↑ 깊어짐", fontsize=9, color=C_DIM, rotation=90,
        ha="center", va="center", zorder=5)

# ================= right: icicle (root top) =================
box(52, 10, 44, 42, C_GRAY, ec=C_ACCENT, lw=1.6)
text(74, 49.4, "icicle (Pyroscope UI 기본)", size=13, weight="bold", color=C_ACCENT)
text(74, 46.8, "상하 반전 · root가 맨 위 (위→아래로 읽기)", size=9, color=C_DIM, style="italic")

for i, (t, c) in enumerate(stack):
    y = 36 - i * 9.5
    ec = C_ACCENT if i == 0 else C_EDGE
    box(57, y, 34, 7, c, ec=ec, lw=1.6 if i == 0 else 1.4)
    text(74, y + 3.5, t, size=11.5, weight="bold")
    if i < 2:
        arrow(74, y, 74, y - 2.5, color=C_ACCENT, lw=2.0)
text(74, 44.2, "root", size=8.5, color=C_ACCENT, weight="bold")
ax.text(94, 43, "↓ 깊어짐", fontsize=9, color=C_DIM, rotation=90,
        ha="center", va="center", zorder=5)

# bottom
text(50, 6.2, "담고 있는 정보는 완전히 동일 — 웹 UI는 위에서 아래로 읽는 icicle 방향을 기본값으로 채택하는 경우가 많다",
     size=10, color=C_ACCENT, weight="bold")
text(50, 3.2, "별도로 diff view는 두 시점/버전의 플레임그래프를 겹쳐 색으로 차이를 강조(늘면 빨강, 줄면 파랑/초록)",
     size=9, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "27-flame-vs-icicle.png")
