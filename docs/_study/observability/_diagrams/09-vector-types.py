"""CH09 Instant Vector와 Range Vector — 변환 흐름 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_TEXT, C_DIM, C_ACCENT, C_BLUE, C_GREEN, C_GRAY, C_ORANGE)

fig, ax = new_fig(w=15, h=8.4, ymax=52)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 49.0, "Instant Vector vs Range Vector — PromQL 데이터 타입", size=19, weight="bold")
text(50, 45.8, "range vector는 그 자체로 그래프 불가 — 반드시 range→instant 함수를 거쳐야 한다",
     size=11.5, color=C_DIM)

# ---- metric name (branch point) ----
box(3, 22, 17, 10, C_GRAY)
text(11.5, 28.4, "메트릭 이름", size=12, weight="bold")
text(11.5, 25.0, "http_requests_total", size=8.6, color=C_DIM, style="italic")

# ---- top path: instant vector ----
box(70, 33, 26, 10, C_GREEN, ec=C_ACCENT, lw=1.8)
text(83, 39.6, "Instant Vector", size=12.5, weight="bold", color=C_ACCENT)
text(83, 36.2, "시점 t 기준 값 1개 · 그래프 가능", size=8.8, color=C_TEXT)
arrow(20, 29, 70, 38, color=C_ACCENT, lw=2.2, rad=-0.08)
text(43, 36.6, "이름만 쓰면 바로 instant vector", size=8.4, color=C_ACCENT)

# ---- bottom path ----
box(26, 11, 18, 9, C_BLUE)
text(35, 16.9, "Range Selector", size=11, weight="bold")
text(35, 13.6, "[5m]", size=9.5, color=C_ACCENT, style="italic")

box(50, 11, 18, 9, C_BLUE)
text(59, 16.9, "Range Vector", size=11, weight="bold")
text(59, 13.6, "구간 내 샘플 목록", size=8.4, color=C_DIM)

box(74, 11, 22, 9, C_GREEN, ec=C_ACCENT, lw=1.8)
text(85, 16.9, "Instant Vector", size=11, weight="bold", color=C_ACCENT)
text(85, 13.6, "변환된 결과", size=8.4, color=C_DIM)

arrow(15, 22, 34, 20, color=C_ORANGE, lw=2.2, rad=-0.1)
arrow(44, 15.5, 50, 15.5, color=C_ORANGE, lw=2.2)
arrow(68, 15.5, 74, 15.5, color=C_ACCENT, lw=2.2)
text(71, 22.2, "rate() · increase()\navg_over_time() 등", size=8.2, color=C_ACCENT, weight="bold")

# bottom
text(50, 5.2, "range selector 길이는 스크레이프 간격의 최소 2~4배 — 15초 주기에 [15s]면 샘플 부족으로 rate가 결측(gap)",
     size=10, color=C_ACCENT, weight="bold")
text(50, 2.4, "range vector는 rate·increase 같은 구간 입력 함수의 재료로만 쓰이고, 함수를 거쳐야 다시 instant vector로 돌아온다",
     size=8.8, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "09-vector-types.png")
