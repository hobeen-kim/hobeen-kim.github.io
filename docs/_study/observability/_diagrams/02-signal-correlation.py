"""CH02 exemplar·라벨로 신호를 잇는 상관관계 흐름 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=7.6, ymax=50)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 46.6, "신호는 연결될 때 강력하다 — exemplar 상관관계 흐름", size=19, weight="bold")
text(50, 43.2, "메트릭에서 감지 → 트레이스로 좁히고 → 로그·프로파일로 확인", size=12, color=C_DIM)

# 노드: 메트릭 → 트레이스 → (로그, 프로파일)
box(3, 20, 22, 12, C_BLUE)
text(14, 28.4, "메트릭", size=13, weight="bold")
text(14, 24.6, "레이턴시 스파이크\n감지", size=9.5, color="#d4dae0")

box(39, 20, 22, 12, C_GREEN, ec=C_ACCENT, lw=1.8)
text(50, 28.4, "트레이스", size=13, weight="bold", color=C_ACCENT)
text(50, 24.6, "느린 span 특정", size=9.5, color="#d4dae0")

box(75, 30, 22, 12, C_BROWN)
text(86, 38.4, "로그", size=13, weight="bold")
text(86, 34.6, "에러 상세 확인", size=9.5, color="#e4d3c2")

box(75, 8, 22, 12, "#4a3d63", ec="#7a68a0", lw=1.4)
text(86, 16.4, "프로파일", size=13, weight="bold", color="#e7dcff")
text(86, 12.6, "코드 레벨 병목 확인", size=9.5, color="#cbb8e6")

# 화살표 + 라벨
arrow(25, 26, 39, 26, color=C_ORANGE, lw=2.4)
text(32, 28.4, "exemplar", size=9, color=C_ORANGE, weight="bold")

arrow(61, 27.5, 75, 34, color=C_ACCENT, lw=2.2, rad=0.12)
text(68.5, 33.4, "trace_id 라벨", size=8.8, color=C_ACCENT, weight="bold")

arrow(61, 24.5, 75, 15, color=C_VIOLET, lw=2.2, rad=-0.12)
text(67.5, 17.6, "span 시간·서비스", size=8.8, color=C_VIOLET, weight="bold")

# bottom
text(50, 3.6, "신호 수집은 관측성의 절반일 뿐 — 나머지 절반은 신호를 잇는 배선(exemplar · trace ID · span 라벨)",
     size=10.5, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="exemplar (메트릭 → 트레이스)"),
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="trace_id 라벨 (트레이스 → 로그)"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, label="span 컨텍스트 (트레이스 → 프로파일)"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.02, 0.16),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

save(fig, "02-signal-correlation.png")
