"""CH12 로컬 TSDB 쓰기 경로 — head block·WAL·mmap·block (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=14, h=8, ymax=54)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 50.5, "로컬 TSDB 쓰기 경로", size=20, weight="bold")
text(50, 47.5, "스크레이프 샘플  →  WAL(내구성) · Head Block(메모리)  →  mmap chunk · 불변 Block(디스크)",
     size=11.5, color=C_DIM)

# ---- 스크레이프 샘플 (top center) ----
box(38, 39, 24, 5.2, C_ORANGE)
text(50, 41.6, "스크레이프 샘플", size=13, weight="bold", color="#241a10")

# ---- WAL (left) ----
box(6, 26, 26, 8, C_BROWN)
text(19, 31.4, "WAL", size=14, weight="bold")
text(19, 28.6, "(디스크, append-only)", size=10, color=C_DIM)

# ---- Head Block (right of WAL) ----
box(52, 24, 30, 11, C_GREEN, ec=C_ACCENT, lw=2.0)
text(67, 32, "Head Block", size=14, weight="bold", color=C_ACCENT)
text(67, 29.2, "메모리 · 쓰기 가능", size=10.5)
text(67, 26.8, "최근 ~2h 범위", size=10, color=C_DIM)

# ---- mmap chunk (bottom right) ----
box(52, 8, 30, 9, C_GRAY)
text(67, 14.3, "mmap chunk", size=13, weight="bold")
text(67, 11.6, "디스크 매핑 · OS 페이지 캐시 활용", size=9.5, color=C_DIM)
text(67, 9.6, "chunk가 차면 → 프로세스 메모리 폭증 방지", size=8.8, color=C_ACCENT, style="italic")

# ---- 불변 Block (bottom left) ----
box(6, 8, 26, 9, C_BLUE)
text(19, 14.3, "불변 Block", size=13, weight="bold")
text(19, 11.8, "chunks + index + meta", size=9.8, color="#d4dae0")
text(19, 9.7, "2h 범위 완료 시 flush", size=8.8, color=C_ACCENT, style="italic")

# ---- arrows ----
# 샘플 -> WAL, 샘플 -> Head
arrow(43, 39, 26, 34, color=C_ORANGE, lw=2.2, rad=0.1)
text(30, 38, "append", size=9, color=C_ORANGE, weight="bold")
arrow(57, 39, 63, 35, color=C_ORANGE, lw=2.2, rad=-0.1)
text(64.5, 38, "append", size=9, color=C_ORANGE, weight="bold")

# Head -> mmap
arrow(67, 24, 67, 17, color=C_ACCENT, lw=2.2)
text(74.5, 20.5, "chunk가 차면", size=9, color=C_ACCENT, weight="bold")

# Head -> Block (flush)
arrow(52, 27, 32, 14, color=C_ACCENT, lw=2.2, rad=0.12)
text(41, 22.5, "2h 범위 완료 시\nflush", size=9, color=C_ACCENT, weight="bold", ha="center")

# WAL -> Head (replay)
arrow(19, 34, 52, 30, color=C_VIOLET, lw=2.2, rad=-0.18)
text(35, 36.3, "재시작 시 replay → 메모리 복구", size=9.5, color=C_VIOLET, weight="bold")

# ---- bottom summary ----
text(50, 3.6, "WAL이 없으면 크래시 시 head block의 최근 데이터가 전부 유실된다",
     size=10.5, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="샘플 append"),
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="디스크 flush / mmap"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, label="WAL replay (복구)"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.02),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "12-tsdb-write-path.png")
