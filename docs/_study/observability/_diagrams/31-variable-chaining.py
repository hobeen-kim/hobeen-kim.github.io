"""CH31 변수 체이닝과 rate_interval — 템플릿 흐름 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_PURPLE)

fig, ax = new_fig(w=14, h=6.6, ymax=44)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 41.0, "변수 체이닝과 $__rate_interval — 재사용 가능한 템플릿", size=18, weight="bold")
text(50, 38.0, "상위 변수 선택이 하위 변수 후보를 좁히고, 자동 계산 변수가 rate 구간을 안전하게 채움",
     size=11, color=C_DIM)

# $namespace
box(6, 24, 24, 8.5, C_BLUE)
text(18, 29.6, "$namespace", size=12, weight="bold", color=C_ACCENT)
text(18, 26.6, "query variable", size=9, color=C_DIM)

# $pod
box(40, 24, 24, 8.5, C_GREEN)
text(52, 29.6, "$pod", size=12, weight="bold", color=C_ACCENT)
text(52, 26.6, "namespace로 필터링된 체이닝", size=8.2, color=C_DIM)

# $__rate_interval
box(6, 8, 24, 8.5, C_BROWN)
text(18, 13.6, "$__rate_interval", size=11.5, weight="bold", color=C_ACCENT)
text(18, 10.6, "자동 계산", size=9, color=C_DIM)

# PromQL panel query
box(72, 15.5, 24, 13, C_PURPLE, ec=C_ACCENT, lw=1.8)
text(84, 24.6, "PromQL 패널 쿼리", size=11, weight="bold")
text(84, 21.4, "namespace=~ $namespace", size=8.3, color=C_TEXT)
text(84, 19.2, "pod=~ $pod", size=8.3, color=C_TEXT)
text(84, 17.0, "[$__rate_interval]", size=8.3, color=C_TEXT)

# arrows
arrow(30, 28.25, 40, 28.25, color=C_ACCENT, lw=2.2)
text(35, 30.4, "필터링", size=8.5, color=C_ORANGE, weight="bold")
arrow(64, 28.25, 72, 24.0, color=C_ACCENT, lw=2.2)
arrow(30, 12.25, 72, 18.5, color=C_ACCENT, lw=2.0, rad=-0.05)

# bottom
text(50, 4.2, "하드코딩된 [5m] 대신 $__rate_interval — 스크레이프 주기·패널 확대에 맞춰 항상 최소 4개 샘플 포함 보장",
     size=9.5, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "31-variable-chaining.png")
