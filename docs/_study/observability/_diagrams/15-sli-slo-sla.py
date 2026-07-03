"""CH15 SLI → SLO → SLA 층위 다이어그램 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_ORANGE)

fig, ax = new_fig(w=14, h=6.6, ymax=44)
box, text, arrow = make_helpers(ax)

text(50, 40.5, "SLI · SLO · SLA — 같은 가용성의 세 층위", size=19, weight="bold")
text(50, 37.2, "측정값(SLI)  →  내부 목표(SLO)  →  고객 계약(SLA)", size=11.5, color=C_DIM)

# three columns
cols = [
    (16, C_BLUE, "SLI", "측정값", "성공 요청 비율", "PromQL 비율(ratio) 쿼리", C_TEXT),
    (50, C_GREEN, "SLO", "내부 목표", "30일 롤링 99.9%", "조직 내부 목표 · 위반해도\n즉시 계약 위반은 아님", C_TEXT),
    (84, C_BROWN, "SLA", "고객 계약", "99.5% (위반 시 페널티)", "SLO보다 느슨하게 설정\n환불·페널티 등 비즈니스 결과", C_TEXT),
]
for cx, fc, t, sub, val, desc, tc in cols:
    box(cx - 15, 8, 30, 24, fc)
    text(cx, 28.5, t, size=17, weight="bold", color=C_ACCENT)
    text(cx, 24.8, sub, size=11, color=C_DIM)
    box(cx - 12.5, 18.2, 25, 4.4, "#1b232a")
    text(cx, 20.4, val, size=10, weight="bold")
    text(cx, 13.5, desc, size=9, color=C_DIM)

arrow(31, 22, 35, 22, color=C_ORANGE, lw=2.4)
arrow(65, 22, 69, 22, color=C_ORANGE, lw=2.4)

text(50, 4.0, "내부 SLO(99.9%)를 어겨도 바로 SLA(99.5%) 위반이 되지 않도록 SLA에 여유를 둔다",
     size=10, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "15-sli-slo-sla.png")
