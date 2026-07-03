"""CH05 §6 단일 노드 한계와 확장 경로 — federation / remote_write (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_PURPLE, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "단일 노드 한계를 넘는 두 확장 경로", size=20, weight="bold")
text(50, 56.6, "federation — 선택적 재수집(요약 메트릭)  ·  remote_write — 실시간 스트리밍(장기 저장·수평 확장)",
     size=12, color=C_DIM)

# ================= left: leaf Prometheus servers =================
box(2, 9, 24, 42, C_GRAY)
text(14, 48.4, "리프 Prometheus 서버들", size=11.5, weight="bold")
for i, t in enumerate(["팀 A", "팀 B", "팀 C"]):
    yy = 40 - i * 12
    box(4, yy, 20, 8, C_BLUE)
    text(14, yy + 5.0, "Prometheus", size=11, weight="bold")
    text(14, yy + 2.4, t, size=9, color="#d4dae0")

# ================= federation path (top) =================
box(46, 37, 24, 12, C_PURPLE)
text(58, 45.4, "글로벌 Prometheus", size=12, weight="bold")
text(58, 42.6, "federation 계층", size=9.5, color="#ddd0ee")
text(58, 39.6, "요약 메트릭만 재수집", size=8.3, color=C_DIM)

box(76, 37, 22, 12, C_GRAY, ec=C_VIOLET, lw=1.6)
text(87, 45.0, "전역 알림 / 대시보드", size=11.5, weight="bold", color="#ddd0ee")
text(87, 41.6, "조직 계층별 통합 뷰", size=8.5, color=C_DIM)

# ================= remote_write path (bottom) =================
box(46, 12, 24, 16, C_GREEN, ec=C_ACCENT, lw=1.8)
text(58, 24.4, "Mimir / Thanos", size=13, weight="bold", color=C_ACCENT)
text(58, 21.2, "장기 저장 + 수평 확장", size=9.5, color="#d4e0d4")
text(58, 18.2, "오브젝트 스토리지 · 멀티테넌시", size=8.3, color=C_DIM)
text(58, 15.2, "업계 표준 확장 패턴", size=8.5, color=C_ACCENT, style="italic")

box(76, 13, 22, 14, C_GRAY, ec=C_ACCENT, lw=1.6)
text(87, 22.4, "전역 질의", size=11.5, weight="bold", color=C_ACCENT)
text(87, 19.0, "모든 팀 데이터를", size=8.5, color=C_DIM)
text(87, 16.6, "하나의 뷰로 조회", size=8.5, color=C_DIM)

# ---- federation arrows (violet) ----
arrow(24, 43, 46, 44, color=C_VIOLET, lw=2.0, rad=0.06)
text(35, 46.4, "federation (/federate)", size=8, color=C_VIOLET, weight="bold")
arrow(24, 31, 46, 40, color=C_VIOLET, lw=2.0, rad=0.10)
text(33, 35.5, "federation", size=7.6, color=C_VIOLET)
arrow(70, 43, 76, 43, color=C_VIOLET, lw=2.0)

# ---- remote_write arrows (accent) ----
arrow(24, 37.5, 46, 24, color=C_ACCENT, lw=2.0, rad=-0.08)
arrow(24, 29, 46, 21, color=C_ACCENT, lw=2.0, rad=-0.05)
arrow(24, 16, 46, 18, color=C_ACCENT, lw=2.0, rad=0.06)
text(36, 25.8, "remote_write", size=8.5, color=C_ACCENT, weight="bold")
arrow(70, 20, 76, 20, color=C_ACCENT, lw=2.0)

# bottom
text(50, 5.0, "federation은 진짜 샤딩이 아닌 선택적 재수집 · 표준은 remote_write로 Mimir/Thanos 계층에 확장을 위임",
     size=10, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_VIOLET, lw=2.5, label="federation (요약 메트릭 pull)"),
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="remote_write (실시간 스트리밍)"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.02),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "05-scaling-paths.png")
