"""CH20 분산 트레이싱 표준의 역사 — 타임라인 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=8, ymax=48)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 45, "분산 트레이싱 표준의 역사", size=20, weight="bold")
text(50, 41.6, "벤더별 분절 → OpenTracing·OpenCensus 경쟁 → OpenTelemetry 통합", size=12, color=C_DIM)

# timeline axis
Y = 22
ax.plot([6, 94], [Y, Y], color=C_EDGE, lw=2.4, zorder=2)
arrow(90, Y, 95, Y, color=C_EDGE, lw=2.4)

events = [
    (2010, "Google Dapper\n논문 발표", C_BLUE, "up"),
    (2012, "Zipkin 오픈소스\n공개 (Twitter)", C_GREEN, "down"),
    (2016, "OpenTracing 시작\n(CNCF · API 표준화)", C_BROWN, "up"),
    (2017, "OpenCensus 발표\n(Google · API+SDK)", C_VIOLET, "down"),
    (2019, "OpenTracing·OpenCensus\n통합 발표", C_ORANGE, "up"),
    (2021, "OpenTelemetry\nTraces 1.0 GA", C_ACCENT, "down"),
]
xs = [10, 26, 42, 58, 74, 90]
for (yr, label, c, side), x in zip(events, xs):
    ax.plot([x], [Y], "o", color=c, markersize=13, zorder=3)
    if side == "up":
        ax.plot([x, x], [Y + 1.4, Y + 6], color=c, lw=1.4, zorder=2)
        box(x - 8, Y + 6, 16, 7.2, C_GRAY, ec=c, lw=1.5)
        text(x, Y + 11.4, str(yr), size=12, weight="bold", color=c)
        text(x, Y + 8, label, size=8.6, color=C_TEXT)
    else:
        ax.plot([x, x], [Y - 1.4, Y - 6], color=c, lw=1.4, zorder=2)
        box(x - 8, Y - 13.2, 16, 7.2, C_GRAY, ec=c, lw=1.5)
        text(x, Y - 7.2, str(yr), size=12, weight="bold", color=c)
        text(x, Y - 10.6, label, size=8.6, color=C_TEXT)

# bottom
text(50, 2.2, "OpenTelemetry는 트레이스·메트릭·로그를 아우르는 교차 신호 표준으로 확장 — 현재 CNCF 2위 프로젝트",
     size=10, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "20-tracing-history.png")
