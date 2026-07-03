"""CH01 전통적 모니터링의 known-unknowns 모델과 대응 불가 영역 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_BROWN, C_GRAY, C_ORANGE)

fig, ax = new_fig(w=14, h=7.2, ymax=48)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 45.0, "전통적 모니터링 — known-unknowns 모델의 한계", size=19, weight="bold")
text(50, 41.6, "미리 정의한 실패 모드만 감지  →  처음 보는 장애 앞에서 무력", size=12, color=C_DIM)

# ================= 전통적 모니터링 그룹 =================
box(4, 10, 62, 24, C_BLUE, ec=C_ACCENT, lw=1.8)
text(35, 30.6, "전통적 모니터링", size=13.5, weight="bold", color=C_ACCENT)

# 3개 칩: KU → DASH → THRESH
chips = [
    (13, "known-unknowns", "미리 정의한 실패 모드"),
    (35, "고정 대시보드", "이미 겪은 장애 재확인"),
    (57, "정적 임계치 알림", "cpu > 90% 식 고정 규칙"),
]
for cx, t, d in chips:
    box(cx - 9.5, 15.5, 19, 8, C_GRAY)
    text(cx, 21.0, t, size=10.5, weight="bold")
    text(cx, 18.0, d, size=8.2, color=C_DIM)

arrow(23.5, 19.5, 25.5, 19.5, color=C_ACCENT, lw=2.0)
arrow(45.5, 19.5, 47.5, 19.5, color=C_ACCENT, lw=2.0)

# ================= 대응 불가 영역 =================
box(74, 13, 22, 18, C_BROWN, ec=C_ORANGE, lw=1.8)
text(85, 27.8, "대응 불가 영역", size=12.5, weight="bold", color=C_ORANGE)
text(85, 24.6, "unknown-unknowns", size=10.5, color=C_ORANGE, style="italic")
text(85, 20.0, "처음 보는 장애는\n대시보드로 미리\n그려둘 수 없다", size=9.5, color="#e4d3c2")

# THRESH -> GAP
arrow(66, 19.5, 74, 21, color=C_ORANGE, lw=2.4)
text(70, 24.0, "처음 보는\n장애?", size=8.5, color=C_ORANGE, weight="bold")

# bottom
text(50, 6.0, "실패 모드의 조합 폭발  ·  정적 임계치의 오탐·미탐  →  알림 피로(alert fatigue)",
     size=10.5, color=C_ACCENT, weight="bold")
text(50, 3.0, "known-unknowns는 빠르게 재확인하지만, unknown-unknowns의 원인 추적에는 무력하다",
     size=9, color=C_DIM, style="italic")

save(fig, "01-traditional-monitoring.png")
