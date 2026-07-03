"""CH06 §3 Histogram vs Summary — 분위수 계산 위치와 집계 가능성 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_PURPLE, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "Histogram vs Summary — 어디서 분위수를 계산하는가", size=19, weight="bold")
text(50, 56.6, "서버(쿼리 시점) 계산이냐 클라이언트(계측 시점) 계산이냐가 집계 가능성을 가른다",
     size=12, color=C_DIM)

# ================= left: Histogram =================
box(4, 11, 44, 41, C_GREEN, ec=C_ACCENT, lw=2.0)
text(26, 48.8, "Histogram", size=15, weight="bold", color=C_ACCENT)
text(26, 46.0, "서버 계산 · 집계 가능", size=9.5, color="#d4e0d4")

hsteps = [
    ("클라이언트: 버킷 카운트만 누적", "le = 0.1 · 0.5 · 1 · +Inf"),
    ("여러 인스턴스 버킷 합산 가능", "sum by (le)"),
    ("PromQL: histogram_quantile()", "쿼리 시점에 분위수 계산"),
]
for i, (t, d) in enumerate(hsteps):
    yy = 37 - i * 9.5
    box(7, yy, 38, 7.3, "#1d2b24")
    text(26, yy + 4.7, t, size=10)
    text(26, yy + 2.1, d, size=8, color=C_DIM)
    if i < 2:
        arrow(26, yy, 26, yy - 2.2, color=C_ACCENT, lw=2.0)

# ================= right: Summary =================
box(52, 11, 44, 41, C_BROWN, ec=C_ORANGE, lw=1.8)
text(74, 48.8, "Summary", size=15, weight="bold", color=C_ORANGE)
text(74, 46.0, "클라이언트 계산 · 집계 불가", size=9.5, color="#e0d4c8")

ssteps = [
    ("클라이언트: 분위수 직접 계산해 노출", "{quantile=\"0.5\"} …"),
    ("인스턴스별 값이 이미 확정", "재계산 불가"),
    ("여러 인스턴스 quantile 평균/합산", "수학적으로 의미 없음"),
]
for i, (t, d) in enumerate(ssteps):
    yy = 37 - i * 9.5
    box(55, yy, 38, 7.3, "#241d1a")
    text(74, yy + 4.7, t, size=9.5)
    text(74, yy + 2.1, d, size=8, color=C_DIM)
    if i < 2:
        arrow(74, yy, 74, yy - 2.2, color=C_ORANGE, lw=2.0)

# bottom
text(50, 6.4, "다중 인스턴스(Pod) 서비스의 p99가 필요하면 Histogram — 버킷을 먼저 합산한 뒤 분위수를 낸다",
     size=10.5, color=C_ACCENT, weight="bold")
text(50, 3.4, "Summary의 quantile은 사후 집계가 원천 불가 — 집계 불필요한 단일 프로세스 지표에 한정",
     size=9.5, color=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "06-histogram-vs-summary.png")
