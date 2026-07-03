"""CH20 트레이싱 없이 vs 트레이싱으로 — 인과관계 재구성 비교 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)


def cbox(cx, cy, bw, bh, fc, **kw):
    box(cx - bw / 2, cy - bh / 2, bw, bh, fc, **kw)


# ---- Title ----
text(50, 59.4, "분산 트레이싱 — 요청 인과관계의 재구성", size=20, weight="bold")
text(50, 56.6, "서비스별 독립 로그로는 같은 요청을 이을 수 없다  →  공통 trace_id로 parent/child 경로를 복원",
     size=12, color=C_DIM)

# ================= left: without tracing =================
box(3, 8, 44, 44, C_GRAY)
text(25, 49.4, "트레이싱 없이", size=15, weight="bold", color=C_ORANGE)
text(25, 46.8, "서비스마다 제각각인 로그 — 요청 단위 연결 고리 없음", size=9.5, color=C_DIM)

logs = [(25, 40, "Gateway 로그"), (25, 30, "Order 로그"),
        (14, 19, "Payment 로그"), (36, 19, "Inventory 로그")]
for cx, cy, t in logs:
    cbox(cx, cy, 18, 5.2, C_BROWN)
    text(cx, cy, t, size=10.5)

arrow(25, 37.4, 25, 32.6, color=C_DIM, lw=1.8, style="-|>", ls=(0, (4, 3)))
text(38, 35, "같은 요청인지\n추론 불가", size=8.5, color=C_ORANGE, style="italic")
arrow(21, 27.6, 15.5, 21.6, color=C_DIM, lw=1.8, ls=(0, (4, 3)))
arrow(29, 27.6, 34.5, 21.6, color=C_DIM, lw=1.8, ls=(0, (4, 3)))

# ================= right: with tracing =================
box(53, 8, 44, 44, C_GRAY, ec=C_ACCENT, lw=2.0)
text(75, 49.4, "트레이싱으로", size=15, weight="bold", color=C_ACCENT)
text(75, 46.8, "모든 span이 같은 trace_id=X 를 공유 — parent/child 트리로 복원", size=9.5, color=C_DIM)

spans = [(75, 40, "Gateway span"), (75, 30, "Order span"),
         (64, 19, "Payment span"), (86, 19, "Inventory span")]
for cx, cy, t in spans:
    cbox(cx, cy, 18, 5.2, C_GREEN)
    text(cx, cy + 0.9, t, size=10.5)
    text(cx, cy - 1.4, "trace_id=X", size=8.5, color=C_ACCENT)

arrow(75, 37.4, 75, 32.6, color=C_ACCENT, lw=2.2)
arrow(71, 27.6, 65.5, 21.6, color=C_ACCENT, lw=2.2)
arrow(79, 27.6, 84.5, 21.6, color=C_ACCENT, lw=2.2)

# bottom
text(50, 4.6, "메트릭='무엇이 얼마나' · 로그='무슨 일이' 에 더해, 트레이싱은 '어느 구간에서 느렸고/실패했는가'를 답한다",
     size=10, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_DIM, lw=2.2, ls="--", label="연결 추론 불가 (독립 로그)"),
    Line2D([0], [0], color=C_ACCENT, lw=2.4, label="parent → child (trace tree)"),
]
ax.legend(handles=leg, loc="lower center", bbox_to_anchor=(0.5, 0.075),
          ncol=2, fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "20-tracing-vs-nothing.png")
