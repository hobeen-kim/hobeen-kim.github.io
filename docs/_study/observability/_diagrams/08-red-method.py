"""CH08 RED 방법론 — 요청 기반 서비스 계측 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_TEXT, C_DIM, C_ACCENT, C_BLUE, C_GREEN, C_ORANGE)

fig, ax = new_fig(w=15, h=8.0, ymax=50)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 47.0, "RED 방법론 — 요청 기반(request-driven) 서비스", size=19, weight="bold")
text(50, 43.8, "요청을 받아 응답하는 컴포넌트를 세 지표로 요약 — Rate · Errors · Duration",
     size=11.5, color=C_DIM)

# ---- request -> service ----
box(4, 20, 18, 8, "#26313a")
text(13, 24, "들어오는 요청", size=12, weight="bold")

box(30, 20, 16, 8, C_BLUE, ec=C_ACCENT, lw=2.0)
text(38, 24, "서비스", size=13, weight="bold", color=C_ACCENT)

arrow(22, 24, 30, 24, color=C_ACCENT, lw=2.4)

# ---- three outputs ----
outs = [
    (36, "Rate", "초당 요청 수", "rate(http_requests_total[5m])"),
    (24, "Errors", "초당 실패 요청 수", 'rate(http_requests_total{status=~"5.."}[5m])'),
    (12, "Duration", "요청 처리 시간 분포", "histogram_quantile → p50 / p95 / p99"),
]
for yc, t, d, q in outs:
    box(58, yc - 5, 38, 10, C_GREEN)
    text(60.5, yc + 2.6, t, size=13, weight="bold", color=C_ACCENT, ha="left")
    text(60.5, yc - 0.1, d, size=9.5, color=C_TEXT, ha="left")
    text(60.5, yc - 3.0, q, size=8.2, color=C_DIM, ha="left", style="italic")
    arrow(46, 24, 58, yc, color=C_ORANGE, lw=2.0, rad=0.05)

# bottom
text(50, 4.4, "서비스 종류가 무엇이든 같은 세 질문 — 얼마나 자주 · 얼마나 실패 · 얼마나 느린가",
     size=11, color=C_ACCENT, weight="bold")
text(50, 1.8, "Counter 하나(http_requests_total) + Histogram 하나(http_request_duration_seconds)로 대부분 커버 · 신규 서비스 최소 계측 기준",
     size=8.8, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "08-red-method.png")
