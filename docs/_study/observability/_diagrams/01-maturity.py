"""CH01 관측성 성숙도 모델 Reactive → Diagnostic → Proactive (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BROWN, C_BLUE, C_GREEN, C_GRAY, C_ORANGE)

fig, ax = new_fig(w=15, h=6.8, ymax=44)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 40.8, "관측성 성숙도 — Reactive → Diagnostic → Proactive", size=19, weight="bold")
text(50, 37.4, "도구 도입만으로 완성되지 않고, 조직 관행이 정착돼야 다음 단계로 넘어간다", size=11.5, color=C_DIM)

stages = [
    (5, C_BROWN, C_ORANGE, "Reactive",
     "장애 발생 후 대응",
     "흩어진 로그 grep\n수동 대시보드 확인"),
    (37, C_BLUE, C_ACCENT, "Diagnostic",
     "신호 연결로 진단",
     "메트릭·로그·트레이스 연결\n근본 원인 추적(MTTR) 단축"),
    (69, C_GREEN, C_ACCENT, "Proactive",
     "사전 포착",
     "SLO·에러 버짓 기반 알림\n이상 징후 사전 포착"),
]
for x, fc, ac, name, sub, body in stages:
    box(x, 10, 26, 22, fc)
    text(x + 13, 28.5, name, size=15, weight="bold", color=ac)
    text(x + 13, 25.3, sub, size=9.5, color=ac, style="italic")
    text(x + 13, 18.5, body, size=10, color="#dfe4e8")

# start marker
text(2.0, 21, "●", size=14, color=C_DIM)
arrow(3.2, 21, 5, 21, color=C_DIM, lw=2.0)

# transitions
arrow(31, 21, 37, 21, color=C_ACCENT, lw=2.6)
text(34, 24.0, "신호 통합\n시작", size=8.5, color=C_ACCENT, weight="bold")
arrow(63, 21, 69, 21, color=C_ACCENT, lw=2.6)
text(66, 24.0, "SLO·상관관계\n정착", size=8.5, color=C_ACCENT, weight="bold")

# end marker
arrow(95, 21, 96.8, 21, color=C_DIM, lw=2.0)
text(98.0, 21, "◉", size=14, color=C_DIM)

# bottom
text(50, 5.0, "대부분의 조직은 Reactive에서 출발 → 도구를 갖추며 Diagnostic → 문화·프로세스가 정착돼야 Proactive",
     size=10, color=C_DIM, style="italic")

save(fig, "01-maturity.png")
