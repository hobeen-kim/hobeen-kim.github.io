"""CH20 context propagation — W3C traceparent 헤더 전파 시퀀스 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(ymax=62)
box, text, arrow = make_helpers(ax)

lanes = [(18, "API Gateway", C_BLUE), (50, "Order Service", C_GREEN),
         (82, "Payment Service", C_BROWN)]

# ---- Title ----
text(50, 59.4, "context propagation — traceparent 헤더로 trace 이어붙이기", size=19, weight="bold")
text(50, 56.6, "trace_id는 유지, 매 홉마다 새 span_id 생성 · parent_id는 직전 홉의 span_id", size=11.5, color=C_DIM)

# lifelines
TOP, BOT = 50.5, 6
for x, name, c in lanes:
    box(x - 11, TOP, 22, 3.6, c)
    text(x, TOP + 1.8, name, size=11, weight="bold")
    ax.plot([x, x], [BOT, TOP], color=C_EDGE, lw=1.2, ls=(0, (3, 3)), zorder=1)

# helper for message arrows
def msg(x1, x2, y, label, color=C_ACCENT, ls="-"):
    arrow(x1, y, x2, y, color=color, lw=2.0, ls=ls)
    text((x1 + x2) / 2, y + 1.3, label, size=9, color=color)


def note(x, y, s, w=24):
    box(x - w / 2, y - 2.2, w, 4.4, C_GRAY, ec=C_ORANGE, lw=1.3)
    text(x, y, s, size=8.5, color="#f0d9b8")


# request path (solid)
msg(18, 50, 47, "POST /orders  (traceparent 전파)")
note(50, 41.5, "같은 trace_id 유지\n새 span_id 생성", w=26)
msg(50, 82, 35, "POST /charge  (traceparent 전파)")
note(82, 29.5, "같은 trace_id 유지\nparent_id = Order의 span_id", w=30)
# response path (dashed)
msg(82, 50, 22, "200 OK", color=C_DIM, ls=(0, (4, 3)))
msg(50, 18, 15, "200 OK", color=C_DIM, ls=(0, (4, 3)))

# header sample
text(50, 9.6, "traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
     size=9, color=C_ACCENT)
text(50, 7.2, "버전 - trace_id(32 hex) - parent_id(16 hex) - trace_flags(01=샘플링 대상)",
     size=8.5, color=C_DIM, style="italic")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.2, label="요청 (traceparent 전파)"),
    Line2D([0], [0], color=C_DIM, lw=2.2, ls="--", label="응답"),
]
ax.legend(handles=leg, loc="upper right", bbox_to_anchor=(0.99, 0.90),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "20-context-propagation.png")
