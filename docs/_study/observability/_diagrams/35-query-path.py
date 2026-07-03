"""CH35 Mimir 쿼리 경로 — query-frontend 분할·캐시부터 결과 병합까지 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=10, ymax=66)
box, text, arrow = make_helpers(ax)

text(50, 63.4, "Mimir 쿼리 경로", size=20, weight="bold")
text(50, 60.6, "query-frontend가 긴 범위 쿼리를 분할·캐시 → querier가 ingester·store-gateway에서 병합",
     size=11, color=C_DIM)

lanes = [
    (8, "Grafana", C_GRAY),
    (25, "query-\nfrontend", "#4a3d63"),
    (43, "querier", "#4a3d63"),
    (61, "ingester", C_BLUE),
    (78, "store-\ngateway", C_GREEN),
    (93, "오브젝트\n스토리지", C_BROWN),
]
top_y, bot_y = 53.5, 7
for x, name, fc in lanes:
    box(x - 7, 53.5, 14, 4.6, fc)
    text(x, 55.8, name, size=9.5, weight="bold")
    ax.plot([x, x], [bot_y, top_y], color=C_EDGE, lw=1.1, ls="--", zorder=1)

X = {n: x for x, n, _ in lanes}


def msg(y, a, b, label, dashed=False, color=C_ACCENT, up=True):
    ls = "--" if dashed else "-"
    x1, x2 = X[a], X[b]
    arrow(x1, y, x2, y, color=color, lw=1.9, ls=ls)
    text((x1 + x2) / 2, y + (1.2 if up else -1.6), label, size=8.5, color=C_TEXT)


def selfmsg(y, lane, label):
    x = X[lane]
    box(x - 8, y - 1.6, 24, 3.2, "#2a2320", ec=C_ORANGE, lw=1.1)
    text(x + 4, y, label, size=8.3, color=C_ORANGE)


msg(50, "Grafana", "query-\nfrontend", "PromQL 쿼리 (최근 30일)", color=C_VIOLET)
selfmsg(45.5, "query-\nfrontend", "일 단위로 분할 · 캐시 확인")
msg(40.5, "query-\nfrontend", "querier", "캐시 미스 구간만 병렬 전달", color=C_VIOLET)
msg(35.5, "querier", "ingester", "최근 데이터 조회", color=C_ACCENT)
msg(30.5, "querier", "store-\ngateway", "과거 데이터 조회", color=C_ACCENT)
msg(25.5, "store-\ngateway", "오브젝트\n스토리지", "필요한 청크만 lazy load", color=C_ACCENT)
msg(20.5, "오브젝트\n스토리지", "store-\ngateway", "청크 반환", dashed=True, color=C_DIM, up=False)
msg(16.5, "store-\ngateway", "querier", "결과 반환", dashed=True, color=C_DIM, up=False)
msg(12.5, "ingester", "querier", "결과 반환", dashed=True, color=C_DIM, up=False)
msg(8.5, "querier", "query-\nfrontend", "병합된 결과", dashed=True, color=C_DIM, up=False)

text(50, 3.2, "QF→G: 최종 결과 반환 후 results cache에 저장 — 반복·겹치는 시간 범위 쿼리는 캐시 재사용",
     size=9.5, color=C_ACCENT, style="italic")

leg = [
    Line2D([0], [0], color=C_VIOLET, lw=2.4, label="분할·분배"),
    Line2D([0], [0], color=C_ACCENT, lw=2.4, label="데이터 조회"),
    Line2D([0], [0], color=C_DIM, lw=2.4, ls="--", label="결과 반환"),
]
ax.legend(handles=leg, loc="lower right", bbox_to_anchor=(0.995, 0.015),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "35-query-path.png")
