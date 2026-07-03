"""CH22 배포·스케일링 — stateless/stateful 컴포넌트와 hash ring (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_PURPLE, C_VIOLET)

fig, ax = new_fig(ymax=58)
box, text, arrow = make_helpers(ax)


def chip(cx, cy, t, c, bw=18, bh=6):
    box(cx - bw / 2, cy - bh / 2, bw, bh, c)
    text(cx, cy, t, size=11, weight="bold")


# ---- Title ----
text(50, 55.4, "Tempo 배포·스케일링 — 마이크로서비스 모드의 컴포넌트 분리", size=17, weight="bold")
text(50, 52.4, "상태 없는 컴포넌트는 자유롭게 수평 확장 · ingester는 상태 저장이라 스케일 시 데이터 이관 고려", size=11, color=C_DIM)

# ===== stateless group =====
box(4, 20, 42, 28, C_GRAY)
text(25, 44.5, "Stateless (수평 확장 쉬움)", size=12, weight="bold", color=C_GREEN)
chip(25, 39, "Distributor", C_BLUE, bw=20)
chip(15, 29, "Query Frontend", C_GREEN, bw=18)
chip(35, 29, "Querier", C_GREEN, bw=16)

# ===== stateful group =====
box(54, 20, 42, 28, C_GRAY, ec=C_ORANGE, lw=1.8)
text(75, 44.5, "Stateful (샤딩·리텐션 관리 필요)", size=12, weight="bold", color=C_ORANGE)
chip(75, 39, "Ingester", C_BROWN, bw=20)
chip(75, 29, "Compactor", C_BROWN, bw=20)

# ===== hash ring =====
box(38, 6, 24, 8, C_PURPLE)
text(50, 11, "Hash Ring", size=11.5, weight="bold")
text(50, 8, "memberlist gossip", size=8.8, color=C_DIM)

# solid edges
arrow(35, 39, 65, 39, color=C_ACCENT, lw=1.9)
arrow(24, 29, 27, 29, color=C_ACCENT, lw=1.9)
arrow(40, 30, 66, 37.5, color=C_ACCENT, lw=1.8)

# dashed ring edges
arrow(23, 36, 42, 14.2, color=C_DIM, lw=1.6, ls=(0, (4, 3)))
text(28, 24, "링 조회", size=8.5, color=C_DIM, style="italic")
arrow(75, 36, 58, 14.2, color=C_DIM, lw=1.6, ls=(0, (4, 3)))
text(70, 24, "링 등록", size=8.5, color=C_DIM, style="italic")

# bottom
text(50, 2.2, "컴포넌트 간 멤버십·해시 링 정보는 memberlist gossip으로 공유 — Mimir·Loki와 동일한 방식",
     size=9.5, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.0, label="데이터 흐름"),
    Line2D([0], [0], color=C_DIM, lw=2.0, ls="--", label="hash ring 조회·등록"),
]
ax.legend(handles=leg, loc="lower center", bbox_to_anchor=(0.5, 0.055),
          ncol=2, fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "22-deployment-scaling.png")
