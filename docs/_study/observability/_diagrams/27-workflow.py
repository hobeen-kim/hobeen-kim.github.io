"""CH27 실전 워크플로우 — 알림→트레이스→프로파일→개선 확인 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "실전 워크플로우 — 알림 → 트레이스 → 프로파일 → 개선 확인", size=20, weight="bold")
text(50, 56.6, "네 신호가 맞물려 근본 원인을 함수 단위까지 좁히는 상관관계 흐름",
     size=12, color=C_DIM)

C_RED = "#5a3838"
C_PUR = "#4a3d63"

def step(cx, cy, w, h, n, title, desc, c, ec=C_EDGE, tc=C_TEXT):
    box(cx - w / 2, cy - h / 2, w, h, c, ec=ec, lw=1.6)
    text(cx - w / 2 + 3.2, cy + h / 2 - 2.4, str(n), size=12, weight="bold", color=C_ACCENT)
    text(cx, cy + 1.2, title, size=10.5, weight="bold", color=tc)
    text(cx, cy - 2.6, desc, size=8.2, color=C_DIM)

W, H = 21, 11
TOP, BOT = 40, 18

# top row: 1 2 3 4
step(14, TOP, W, H, 1, "Alertmanager", "알림 발화\n(p99 레이턴시 SLO 위반)", C_RED, ec="#8a5a5a")
step(38, TOP, W, H, 2, "Tempo", "느린 트레이스 조회\n(exemplar로 진입)", C_GREEN)
step(62, TOP, W, H, 3, "느린 스팬 특정", "어느 요청·어느 스팬에서", C_GREEN)
step(86, TOP, W, H, 4, "Pyroscope", "span profile 조회", C_PUR, ec="#7a68a0", tc="#e7dcff")

# bottom row (snake back): 5 6 7
step(86, BOT, W, H, 5, "핫패스 함수 특정", "플레임그래프에서\n가장 넓은 프레임", C_PUR, ec="#7a68a0", tc="#e7dcff")
step(50, BOT, W, H, 6, "코드 수정 → 재배포", "원인 함수 최적화", C_BLUE)
step(14, BOT, W, H, 7, "diff view", "개선 확인\n(배포 전/후 비교)", C_BROWN, ec=C_ORANGE)

# arrows top row
arrow(24.5, TOP, 27.5, TOP, color=C_ACCENT, lw=2.2)
arrow(48.5, TOP, 51.5, TOP, color=C_ACCENT, lw=2.2)
arrow(72.5, TOP, 75.5, TOP, color=C_ACCENT, lw=2.2)
# 4 -> 5 (down)
arrow(86, TOP - H / 2, 86, BOT + H / 2, color=C_ORANGE, lw=2.4)
# bottom row (right to left)
arrow(75.5, BOT, 60.5, BOT, color=C_ACCENT, lw=2.2)
arrow(39.5, BOT, 24.5, BOT, color=C_ACCENT, lw=2.2)

# stage labels
text(31, TOP + 7.2, "무엇이 잘못됐는가", size=8.5, color=C_DIM, style="italic")
text(62, TOP + 7.2, "어느 요청·스팬에서", size=8.5, color=C_DIM, style="italic")
text(92.5, 29, "정확히 어느\n함수 때문에", size=8.5, color=C_ORANGE, style="italic", ha="right")

# bottom
text(50, 6.2, "알림이 '무엇이', 트레이스가 '어느 스팬에서', span profile이 '어느 함수 때문에'로 마무리 짓는다",
     size=10, color=C_ACCENT, weight="bold")
text(50, 3.2, "각 신호는 개별로도 유용하지만, 연결될 때 근본 원인 추적이라는 가치가 생긴다",
     size=9, color=C_DIM, style="italic")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="신호 간 이동(drill-down)"),
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="트레이스 → 프로파일 진입"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.01),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "27-workflow.png")
