"""CH11 룰 성능 — 평가 지연 관측과 튜닝 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_TEXT, C_DIM, C_ACCENT, C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE)

fig, ax = new_fig(w=15, h=8.6, ymax=52)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 49.0, "룰 성능 — 평가 지연을 관측하고 튜닝한다", size=19, weight="bold")
text(50, 45.8, "그룹 평가 시간이 interval을 넘으면 다음 평가가 밀린다",
     size=11.5, color=C_DIM)

# ================= symptom chain (top row) =================
box(3, 32.5, 26, 10, C_BROWN)
text(16, 39.4, "평가 시간 ≥ interval", size=11, weight="bold", color=C_ACCENT)
text(16, 35.4, "prometheus_rule_group_\nlast_duration_seconds", size=8.0, color=C_DIM, style="italic")

box(34, 34, 15, 7, C_GRAY)
text(41.5, 38.4, "평가 지연", size=10.5, weight="bold")
text(41.5, 35.4, "발생", size=9, color=C_DIM)

box(54, 32.5, 28, 10, C_BLUE)
text(68, 39.4, "누락 카운터 증가", size=11, weight="bold", color=C_ACCENT)
text(68, 35.4, "prometheus_rule_group_\niterations_missed_total ↑", size=8.0, color=C_DIM, style="italic")

arrow(29, 37.5, 34, 37.5, color=C_ORANGE, lw=2.2)
arrow(49, 37.5, 54, 37.5, color=C_ORANGE, lw=2.2)

# ================= remediations (bottom row) =================
fixes = [
    (18, "그룹 분할", "순서 의존 없는 룰을\n별도 그룹으로 → 병렬 평가"),
    (50, "Recording Rule 사전 계산", "여러 알림이 참조하는\n무거운 집계를 한 번만"),
    (82, "고카디널리티 expr 제거", "매 interval 반복 실행이라\n영향이 더 크다"),
]
for xc, t, d in fixes:
    box(xc - 14, 9, 28, 12, C_GREEN)
    text(xc, 17.5, t, size=10.5, weight="bold", color=C_ACCENT)
    text(xc, 13.2, d, size=8.6, color=C_TEXT)
    arrow(68, 32.5, xc, 21, color=C_ACCENT, lw=2.0, rad=0.05)

# bottom
text(50, 5.0, "interval을 필요 이상으로 짧게 잡지 않는다 — 반응 속도가 정말 중요한 그룹에만 짧은 interval",
     size=9.8, color=C_ACCENT, weight="bold")
text(50, 2.4, "룰 파일은 배포 전 promtool test rules로 발화 조건·라벨·annotation을 검증한다",
     size=8.8, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "11-rule-performance.png")
