"""CH10 성능 안티패턴 — 느린 쿼리 진단 결정 트리 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_TEXT, C_DIM, C_ACCENT, C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "느린/비싼 쿼리 진단 — 성능 안티패턴 결정 트리", size=19, weight="bold")
text(50, 56.6, "위에서부터 순서대로 짚어 원인을 좁힌다", size=12, color=C_DIM)

SPINE = 27   # decision column center
ACT = 74     # action column center

# ---- start ----
box(15, 50.5, 24, 6, C_GRAY, ec=C_ACCENT, lw=2.0)
text(27, 53.5, "느린 / 비싼 쿼리", size=12, weight="bold", color=C_ACCENT)

# ---- decision nodes (spine) + action nodes (right) ----
decisions = [
    (44, "고카디널리티 라벨 매칭인가?", "요청 ID·사용자 ID 등 값이 무한한 라벨에 와일드카드",
     "계측 단계에서 라벨 설계 재검토", "값이 무한한 라벨은 애초에 붙이지 않는다"),
    (31, "rate 전에 집계했는가?", "sum 등으로 먼저 합산한 뒤 rate 적용",
     "rate를 안쪽으로, 집계를 바깥으로 재배치", "sum(rate(x[5m])) 순서 준수"),
    (18, "반복 조회되는 무거운 집계/quantile인가?", "긴 range·짧은 step으로 대시보드가 매번 재계산",
     "Recording Rule로 사전 계산", "자주 쓰는 무거운 쿼리를 미리 저장"),
]
for yc, q, qd, a, ad in decisions:
    box(11, yc - 3.5, 32, 7, C_BROWN)
    text(27, yc + 1.3, q, size=9.8, weight="bold")
    text(27, yc - 1.7, qd, size=7.4, color=C_DIM)
    box(58, yc - 3.5, 32, 7, C_GREEN)
    text(74, yc + 1.3, a, size=9.6, weight="bold", color=C_ACCENT)
    text(74, yc - 1.7, ad, size=7.4, color=C_DIM)
    # Yes arrow to action
    arrow(43, yc, 58, yc, color=C_ACCENT, lw=2.0)
    text(50.5, yc + 1.6, "Yes", size=8.2, color=C_ACCENT, weight="bold")

# ---- final fallback ----
box(11, 3.5, 32, 7, C_BLUE)
text(27, 8.3, "쿼리 자체보다", size=9.6, weight="bold")
text(27, 5.4, "스크레이프 간격 · 타임아웃 점검", size=9.0, color=C_TEXT)

# ---- down arrows (No path) : start->C1, C1->C2, C2->C3, C3->fallback ----
segs = [(50.5, 47.6), (40.5, 34.6), (27.5, 21.6), (14.5, 10.6)]
for y1, y2 in segs:
    arrow(27, y1, 27, y2, color="#8a94a0", lw=2.0)
for y in [37.5, 24.5, 12.5]:
    text(30.5, y, "No", size=8.0, color=C_DIM, weight="bold")

# bottom
text(50, 1.8, "불필요한 정규식 매처(=로 충분한 곳의 =~)도 매 쿼리 오버헤드 — 값 고정 매칭은 항상 = / != 우선",
     size=9.5, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="Yes → 해결책"),
    Line2D([0], [0], color="#8a94a0", lw=2.5, label="No → 다음 항목"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.05),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "10-antipattern-decision.png")
