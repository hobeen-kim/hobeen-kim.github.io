"""CH05 §4 데이터 흐름 — scrape → WAL → head → query 시퀀스 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_PURPLE, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "샘플 하나의 여정 — scrape → WAL → head → query", size=19, weight="bold")
text(50, 56.6, "타깃에서 나온 샘플이 durability를 거쳐 저장되고 질의 결과로 병합되기까지",
     size=12, color=C_DIM)

# ---- lifelines ----
actors = [
    (10,  "타깃",        "/metrics",        C_GREEN),
    (27,  "Retrieval",   "scrape",          C_BLUE),
    (44,  "WAL",         "append-only 로그", C_BROWN),
    (61,  "Head Block",  "메모리",          C_PURPLE),
    (78,  "영속 블록",   "디스크",          C_GRAY),
    (94,  "PromQL 엔진", "query",           "#5a4020"),
]
for x, name, sub, col in actors:
    ec = C_ORANGE if col == "#5a4020" else C_EDGE
    box(x - 7.5, 50.5, 15, 5.2, col, ec=ec, lw=1.6)
    text(x, 53.7, name, size=10, weight="bold")
    text(x, 51.7, sub, size=7.6, color=C_DIM)
    ax.plot([x, x], [7, 50.5], color=C_EDGE, ls=(0, (4, 3)), lw=1.0, zorder=1)

def hop(x1, x2, y, label, color=C_ACCENT, ls="-", lblcol=None):
    arrow(x1, y, x2, y, color=color, lw=2.0, ls=ls)
    text((x1 + x2) / 2, y + 1.5, label, size=8, color=lblcol or color,
         weight="bold" if ls == "-" else "normal")

# ---- loop box (scrape_interval) ----
box(4, 32.5, 64, 16.5, "#141b20", ec=C_ACCENT, lw=1.4)
text(9.5, 47.4, "loop  scrape_interval 마다", size=9, color=C_ACCENT, ha="left", style="italic")

hop(27, 10, 44.5, "GET /metrics", color=C_BLUE, lblcol="#8fb4cf")
hop(10, 27, 40.5, "텍스트 노출 형식 샘플", color=C_GREEN, ls="--", lblcol="#7fbf87")
hop(27, 44, 36.5, "샘플 append (durability)", color=C_BROWN, lblcol="#d2b48c")
arrow(27, 34.2, 61, 34.2, color=C_PURPLE, lw=2.0)
text(44, 35.6, "동시에 in-memory 청크 append", size=8, color=C_VIOLET, weight="bold")

# ---- compaction note ----
box(48.5, 26, 42, 4.4, "#241d1a", ec=C_ORANGE, lw=1.3)
text(69.5, 28.2, "기본 2시간 주기로 compaction", size=9, color=C_ORANGE, weight="bold")

hop(61, 78, 23, "head → 디스크 블록 flush", color=C_ORANGE, lblcol=C_ORANGE)

# ---- WAL truncate note ----
box(31, 17, 26, 4.2, "#241d1a", ec=C_BROWN, lw=1.3)
text(44, 19.1, "대응 WAL 세그먼트 truncate", size=8.5, color="#d2b48c")

# ---- query hops ----
hop(94, 61, 13.5, "최근 데이터 조회", color=C_ORANGE, lblcol=C_ORANGE)
hop(94, 78, 10.0, "과거 데이터 조회", color=C_ORANGE, lblcol=C_ORANGE)

# bottom
text(50, 4.4, "WAL(durability) → head(메모리) → 디스크 블록(압축) · PromQL 엔진은 head+블록을 투명하게 병합해 응답",
     size=10, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="동기 호출 (append/flush)"),
    Line2D([0], [0], color=C_GREEN, lw=2.5, ls="--", label="응답 반환"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.02),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "05-data-flow.png")
