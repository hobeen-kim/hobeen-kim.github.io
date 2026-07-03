"""CH32 신호 고립 vs 상관관계 연결 비교 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=14, h=8, ymax=50)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 47.4, "신호 고립 vs 상관관계 연결", size=20, weight="bold")
text(50, 44.4, "같은 세 신호라도 — 배선이 없으면 분리된 모니터링, 배선이 있으면 관측성",
     size=12, color=C_DIM)

# ================= top: isolated =================
box(4, 26, 92, 13, C_BROWN, ec="#8a6a52", lw=1.6)
text(9, 37, "신호가 고립된 경우", size=13, weight="bold", color=C_ORANGE, ha="left")

iso = [
    (20, "메트릭 이상 발견"),
    (52, "로그 확인"),
    (84, "트레이스 조회"),
]
for x, t in iso:
    box(x - 9, 28.5, 18, 5, "#241d1a")
    text(x, 31, t, size=11)

arrow(20 + 9, 31, 52 - 9, 31, color=C_ORANGE, lw=2.0)
text(36, 33.2, "수동으로 시간·서비스\n맞춰 로그 검색", size=8.5, color=C_ORANGE)
arrow(52 + 9, 31, 84 - 9, 31, color=C_ORANGE, lw=2.0)
text(68, 33.2, "수동으로\ntrace ID 복사", size=8.5, color=C_ORANGE)

# ================= bottom: correlated =================
box(4, 4, 92, 18.5, C_GREEN, ec=C_ACCENT, lw=1.8)
text(9, 20.4, "상관관계가 연결된 경우", size=13, weight="bold", color=C_ACCENT, ha="left")

# M2 -> T2
box(11, 11.5, 18, 5, "#1d2b24")
text(20, 14, "메트릭 이상 발견", size=11)
box(41, 11.5, 18, 5, "#1d2b24")
text(50, 14, "트레이스", size=11)
arrow(20 + 9, 14, 41 - 9, 14, color=C_ACCENT, lw=2.2)
text(35, 15.7, "exemplar 클릭", size=8.5, color=C_ACCENT, weight="bold")

# T2 -> L2 (logs) , T2 -> P2 (flamegraph)
box(72, 15.5, 20, 4.6, "#1d2b24")
text(82, 17.8, "로그", size=11)
box(72, 6.4, 20, 4.6, "#1d2b24")
text(82, 8.7, "플레임그래프", size=11)
arrow(59, 15, 72, 17.8, color=C_ACCENT, lw=2.2)
text(65, 18.6, "trace-to-logs", size=8.5, color=C_ACCENT, weight="bold")
arrow(59, 13, 72, 8.7, color=C_ACCENT, lw=2.2)
text(65, 10.2, "trace-to-profiles", size=8.5, color=C_ACCENT, weight="bold")

# bottom note
text(50, 1.6, "공통 식별자(trace ID·시간창·라벨)를 데이터소스에 등록 → 클릭 한 번으로 신호 간 점프",
     size=10, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "32-isolated-vs-correlated.png")
