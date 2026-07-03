"""CH32 통합 drill-down 워크플로우 — 한 화면에서 대시보드→트레이스→로그→프로파일 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=9.8, ymax=64)
box, text, arrow = make_helpers(ax)

text(50, 61.2, "통합 drill-down 워크플로우", size=20, weight="bold")
text(50, 58.2, "SRE가 도구를 옮기지도, ID를 손으로 복사하지도 않고 원인을 좁혀간다",
     size=12, color=C_DIM)

lanes = [
    (10, "SRE", C_GRAY),
    (31, "RED 대시보드", C_BLUE),
    (52, "Tempo", C_GREEN),
    (73, "Loki", C_BROWN),
    (92, "Pyroscope", "#4a3d63"),
]
top_y, bot_y = 52.5, 8
for x, name, fc in lanes:
    box(x - 9, 53, 18, 4.0, fc)
    text(x, 55.0, name, size=11, weight="bold")
    ax.plot([x, x], [bot_y, top_y], color=C_EDGE, lw=1.1, ls="--", zorder=1)

X = {n: x for x, n, _ in lanes}


def msg(y, a, b, label, dashed=False, color=C_ACCENT):
    ls = "--" if dashed else "-"
    x1, x2 = X[a], X[b]
    arrow(x1, y, x2, y, color=color, lw=2.0, ls=ls)
    text((x1 + x2) / 2, y + 1.3, label, size=8.8, color=C_TEXT)


msg(49, "SRE", "RED 대시보드", "p99 레이턴시 스파이크 확인", color=C_BLUE.replace(C_BLUE, "#7fa8c9"))
msg(45, "RED 대시보드", "SRE", "exemplar 점 표시", dashed=True, color=C_DIM)
msg(40.5, "SRE", "Tempo", "exemplar 클릭 → 트레이스 조회", color=C_ACCENT)
msg(36.5, "Tempo", "SRE", "느린 span 확인 (특정 DB 호출)", dashed=True, color=C_DIM)
msg(32, "SRE", "Loki", '"Logs for this span" 클릭', color=C_ACCENT)
msg(28, "Loki", "SRE", "에러 로그 없음 (정상 응답, 단순 지연)", dashed=True, color=C_DIM)
msg(23.5, "SRE", "Pyroscope", '"Profiles for this span" 클릭', color=C_ACCENT)
msg(19.5, "Pyroscope", "SRE", "플레임그래프에서 GC 시간 비중 급증", dashed=True, color=C_DIM)

# conclusion note over SRE
box(X["SRE"] - 12, 11.5, 30, 4.4, "#1d2b24", ec=C_ACCENT, lw=1.4)
text(X["SRE"] + 3, 13.7, "근본 원인 = GC 압박, 애플리케이션 버그 아님", size=9.5,
     color=C_ACCENT, weight="bold")

text(50, 3.0, "각 단계가 이전 단계의 컨텍스트(시간창·서비스·span)를 물려받아 다음 쿼리를 자동 구성",
     size=9.5, color=C_ACCENT, style="italic")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.4, label="클릭 → 다음 신호로 점프"),
    Line2D([0], [0], color=C_DIM, lw=2.4, ls="--", label="결과 반환"),
]
ax.legend(handles=leg, loc="lower right", bbox_to_anchor=(0.995, 0.02),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "32-drilldown-workflow.png")
