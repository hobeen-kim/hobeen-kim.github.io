"""CH32 exemplar — 메트릭에서 트레이스로 점프하는 순서 흐름 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=8.6, ymax=58)
box, text, arrow = make_helpers(ax)

text(50, 55.4, "exemplar — 메트릭에서 트레이스로", size=20, weight="bold")
text(50, 52.4, "히스토그램 관측값에 trace ID를 붙여 저장 → 그래프의 점을 클릭하면 원시 트레이스로 점프",
     size=12, color=C_DIM)

# ---- lifelines ----
lanes = [
    (13, "애플리케이션", C_GRAY),
    (38, "Prometheus", C_BROWN),
    (63, "Grafana", C_BLUE),
    (88, "Tempo", C_GREEN),
]
top_y, bot_y = 46.5, 5
for x, name, fc in lanes:
    box(x - 9, 47, 18, 4.2, fc)
    text(x, 49.1, name, size=11.5, weight="bold")
    ax.plot([x, x], [bot_y, top_y], color=C_EDGE, lw=1.1, ls="--", zorder=1)

X = {n: x for x, n, _ in lanes}


def msg(y, a, b, label, dashed=False, color=C_ACCENT):
    ls = "--" if dashed else "-"
    x1, x2 = X[a], X[b]
    arrow(x1, y, x2, y, color=color, lw=2.0, ls=ls)
    mid = (x1 + x2) / 2
    text(mid, y + 1.4, label, size=9, color=C_TEXT)


def note(y, lane, label, w=22):
    x = X[lane]
    box(x - w / 2, y - 1.8, w, 3.6, "#2a2320", ec=C_ORANGE, lw=1.2)
    text(x, y, label, size=8.8, color=C_ORANGE)


msg(43, "애플리케이션", "Prometheus", "히스토그램 관측값 + exemplar(trace_id)", color=C_ORANGE)
note(38, "Prometheus", "exemplar-storage에\n별도 보관")
msg(32, "Grafana", "Prometheus", "PromQL 쿼리", color=C_BLUE.replace(C_BLUE, "#7fa8c9"))
msg(27, "Prometheus", "Grafana", "시계열 + exemplar 포인트", dashed=True, color=C_DIM)
note(21.5, "Grafana", "그래프 위\n작은 점으로 렌더링")
msg(15.5, "Grafana", "Tempo", "사용자가 점 클릭 → trace_id로 조회", color=C_ACCENT)
msg(10.5, "Tempo", "Grafana", "트레이스 반환", dashed=True, color=C_DIM)

text(50, 2.4, "exemplar는 스크레이프당 버킷별 최대 1개 — 느린 요청의 대표 표본이지 전수가 아니다",
     size=9.5, color=C_ACCENT, style="italic")

leg = [
    Line2D([0], [0], color=C_ORANGE, lw=2.4, label="exemplar 저장 경로"),
    Line2D([0], [0], color=C_ACCENT, lw=2.4, label="클릭 → 트레이스 점프"),
    Line2D([0], [0], color=C_DIM, lw=2.4, ls="--", label="응답(반환)"),
]
ax.legend(handles=leg, loc="lower right", bbox_to_anchor=(0.995, 0.02),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "32-exemplar-flow.png")
