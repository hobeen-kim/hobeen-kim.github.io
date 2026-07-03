"""CH11 Recording Rule — 사전 계산 흐름 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_TEXT, C_DIM, C_ACCENT, C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE)

fig, ax = new_fig(w=15, h=8.0, ymax=50)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 47.0, "Recording Rule — 무거운 쿼리를 미리 계산해 저장", size=19, weight="bold")
text(50, 43.8, "정해진 평가 주기마다 서버가 계산해 새 시계열로 저장 → 대시보드·알림은 가볍게 재사용",
     size=11, color=C_DIM)

# ---- raw metric ----
box(2, 21, 20, 10, C_GRAY)
text(12, 27.4, "원본 메트릭", size=11.5, weight="bold")
text(12, 23.8, "http_requests_total", size=8.4, color=C_DIM, style="italic")

# ---- recording rule ----
box(28, 21, 24, 10, C_GREEN, ec=C_ACCENT, lw=2.0)
text(40, 27.4, "Recording Rule", size=11.5, weight="bold", color=C_ACCENT)
text(40, 23.8, "job:http_requests:rate5m", size=8.4, color=C_DIM, style="italic")

# ---- tsdb ----
box(58, 21, 20, 10, C_BLUE)
text(68, 27.4, "TSDB 저장", size=11.5, weight="bold")
text(68, 23.8, "새 시계열로 기록", size=8.4, color=C_DIM)

# ---- outputs ----
box(82, 31, 16, 9, C_BROWN)
text(90, 36.4, "Grafana 대시보드", size=9.6, weight="bold")
text(90, 33.2, "가벼운 조회", size=8.0, color=C_DIM)

box(82, 11, 16, 9, C_BROWN)
text(90, 16.4, "Alerting Rule", size=9.6, weight="bold")
text(90, 13.2, "재사용 가능", size=8.0, color=C_DIM)

# ---- arrows ----
arrow(22, 26, 28, 26, color=C_ORANGE, lw=2.2)
text(25, 28.4, "매 30초 평가", size=7.8, color=C_ORANGE, weight="bold")
arrow(52, 26, 58, 26, color=C_ACCENT, lw=2.2)
arrow(78, 27, 82, 35, color=C_ACCENT, lw=2.0, rad=0.1)
arrow(78, 25, 82, 16, color=C_ACCENT, lw=2.0, rad=-0.1)

# bottom
text(50, 6.4, "명명 규칙  level : metric : operation  —  by 라벨 단위 : 원본 메트릭명 : 적용 연산(rate5m·p99 등)",
     size=10, color=C_ACCENT, weight="bold")
text(50, 3.2, "여러 알림이 같은 무거운 집계를 반복 계산한다면, Recording Rule로 한 번만 계산해 참조하도록 리팩터링",
     size=8.8, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "11-recording-rule.png")
