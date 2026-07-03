"""CH20 trace tree — root span과 parent/child 구조 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=14, h=9, ymax=60)
box, text, arrow = make_helpers(ax)


def node(cx, cy, title, meta, fc, bw=30, bh=6.4):
    box(cx - bw / 2, cy - bh / 2, bw, bh, fc)
    text(cx, cy + 1.2, title, size=11, weight="bold")
    text(cx, cy - 1.5, meta, size=8.5, color=C_ACCENT)


# ---- Title ----
text(50, 57, "trace tree — 같은 trace_id를 공유하는 span들의 parent/child 트리", size=17, weight="bold")
text(50, 53.6, "root span 아래로 호출된 span이 parent_span_id로 연결되며 트리를 이룬다", size=11, color=C_DIM)

# nodes
node(50, 46, "root span: API Gateway", "trace_id=abc123 · span_id=a1", C_BLUE, bw=40, bh=7)
node(50, 34, "span: Order Service", "parent=a1 · span_id=b2", C_GREEN, bw=34)
node(28, 21, "span: Payment Service", "parent=b2 · span_id=c3", C_BROWN)
node(72, 21, "span: Inventory Service", "parent=b2 · span_id=d4", C_BROWN)
node(28, 9, "span: DB Query (SELECT)", "parent=c3 · span_id=e5", C_GRAY)

# edges
arrow(50, 42.4, 50, 37.3, color=C_ACCENT, lw=2.2)
arrow(44, 30.6, 32, 24.3, color=C_ACCENT, lw=2.2)
arrow(56, 30.6, 68, 24.3, color=C_ACCENT, lw=2.2)
arrow(28, 17.7, 28, 12.3, color=C_ACCENT, lw=2.2)

# side note
text(88, 40, "child span 구간이\nparent 구간을 벗어나면\n계측 오류·시계 어긋남", size=8.5,
     color=C_DIM, style="italic", ha="center")

# bottom
text(50, 2.4, "시간축에 나열하면 Gantt 형태의 waterfall 뷰 — Grafana에서 Tempo trace를 열었을 때 보이는 화면",
     size=9.5, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "20-trace-tree.png")
