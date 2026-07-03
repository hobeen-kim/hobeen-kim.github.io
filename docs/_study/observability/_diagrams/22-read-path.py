"""CH22 읽기 경로 — trace by ID 조회 시퀀스 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_PURPLE, C_VIOLET)

fig, ax = new_fig(ymax=62)
box, text, arrow = make_helpers(ax)

lanes = [(10, "Grafana", C_BLUE), (31, "Query Frontend", C_GREEN),
         (52, "Querier", C_ORANGE), (72, "Ingester", C_BROWN),
         (91, "오브젝트 스토리지", C_PURPLE)]

# ---- Title ----
text(50, 59.4, "Tempo 읽기 경로 — trace by ID 조회", size=19, weight="bold")
text(50, 56.6, "ingester(메모리 최근 데이터)와 스토리지(bloom filter로 블록 선별)를 함께 조회해 trace 병합",
     size=11, color=C_DIM)

TOP, BOT = 51, 5
for x, name, c in lanes:
    box(x - 9.5, TOP, 19, 3.6, c)
    text(x, TOP + 1.8, name, size=10, weight="bold")
    ax.plot([x, x], [BOT, TOP], color=C_EDGE, lw=1.2, ls=(0, (3, 3)), zorder=1)


def msg(x1, x2, y, label, color=C_ACCENT, ls="-"):
    arrow(x1, y, x2, y, color=color, lw=1.9, ls=ls)
    d = 1 if x2 > x1 else -1
    text((x1 + x2) / 2, y + 1.2, label, size=8.5, color=color)


X = {n[1]: n[0] for n in lanes}
# request path
msg(X["Grafana"], X["Query Frontend"], 46, "trace_id 조회")
msg(X["Query Frontend"], X["Querier"], 42, "조회 위임")
msg(X["Querier"], X["Ingester"], 38, "최근 데이터 질의 (메모리)")
msg(X["Querier"], X["오브젝트 스토리지"], 34, "블록별 bloom filter 확인")
# note
box(52, 26.5, 40, 4.6, C_GRAY, ec=C_ORANGE, lw=1.3)
text(72, 28.8, "bloom filter가 존재 가능성을 가리키는 블록만 다운로드", size=8.4, color="#f0d9b8")
# response path (dashed)
msg(X["오브젝트 스토리지"], X["Querier"], 22, "해당 블록 parquet 데이터", color=C_DIM, ls=(0, (4, 3)))
msg(X["Ingester"], X["Querier"], 18, "최근 span", color=C_DIM, ls=(0, (4, 3)))
msg(X["Querier"], X["Query Frontend"], 14, "trace 조립 결과 병합", color=C_DIM, ls=(0, (4, 3)))
msg(X["Query Frontend"], X["Grafana"], 10, "완성된 trace", color=C_DIM, ls=(0, (4, 3)))

# bottom
text(50, 5.0, "bloom filter는 false negative가 없어, 실제로 없는 블록은 다운로드 자체를 건너뛴다",
     size=9.5, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.0, label="조회 요청"),
    Line2D([0], [0], color=C_DIM, lw=2.0, ls="--", label="응답 · 병합"),
]
ax.legend(handles=leg, loc="center left", bbox_to_anchor=(0.03, 0.42),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "22-read-path.png")
