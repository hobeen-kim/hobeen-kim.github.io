"""CH09 Counter 다루기 — rate / irate / increase (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_TEXT, C_DIM, C_ACCENT, C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE)

fig, ax = new_fig(w=15, h=9.0, ymax=58)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 55.0, "Counter 다루기 — rate · irate · increase", size=20, weight="bold")
text(50, 52.0, "counter 원시값은 거의 의미 없다 — 항상 변화율로 바꿔서 본다",
     size=12, color=C_DIM)

# ---- counter source ----
box(35, 43, 30, 8, C_GRAY, ec=C_ACCENT, lw=2.0)
text(50, 48.0, "Counter 원시값", size=13, weight="bold", color=C_ACCENT)
text(50, 45.2, "단조 증가 · 리셋(재시작·재배포) 가능", size=9, color=C_DIM)

# ---- middle: three functions ----
mids = [
    (19, C_GREEN, "rate()", "구간 평균 초당 증가율\n리셋 보정"),
    (50, C_BROWN, "irate()", "마지막 2개 샘플\n순간 변화율"),
    (81, C_BLUE, "increase()", "구간 총 증가량\n= rate × 구간초"),
]
for xc, fc, t, d in mids:
    box(xc - 13, 26, 26, 11, fc)
    text(xc, 34.2, t, size=13, weight="bold", color=C_ACCENT)
    text(xc, 30.0, d, size=9, color=C_TEXT)
    arrow(50, 43, xc, 37, color=C_ORANGE, lw=2.0, rad=0.04)

# ---- bottom: usage ----
downs = [
    (19, C_GREEN, "대시보드 / 알림", "권장", C_ACCENT),
    (50, C_BROWN, "순간 스파이크 관찰", "알림 비권장", C_ORANGE),
    (81, C_BLUE, "절대 증가량 확인", '"5분간 몇 건"', C_DIM),
]
for xc, fc, t, d, dc in downs:
    box(xc - 13, 8, 26, 9, fc, alpha=0.55)
    text(xc, 13.4, t, size=10.5, weight="bold")
    text(xc, 10.2, d, size=8.6, color=dc, style="italic")
    arrow(xc, 26, xc, 17, color=C_ACCENT, lw=1.8)

# bottom
text(50, 3.2, "rate 전에 집계 금지 — 항상 sum(rate(x[5m]))처럼 rate를 먼저, 집계를 나중에 · gauge에는 rate 대신 deriv/delta",
     size=9.5, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "09-counter-functions.png")
