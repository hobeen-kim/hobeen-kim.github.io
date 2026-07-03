"""CH06 §1 시계열 식별 — metric name + 라벨 집합 = 유일 ID (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_PURPLE, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=14, h=7.6, ymax=50)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 47.6, "시계열은 어떻게 유일하게 식별되는가", size=18, weight="bold")
text(50, 44.9, "metric name(__name__)과 라벨 집합의 조합이 하나의 시계열을 유일하게 식별한다",
     size=11, color=C_DIM)

# ================= left: name + labels =================
box(3, 37, 25, 5.5, C_ACCENT.replace("#4fd1c5", "#1f4a45"), ec=C_ACCENT, lw=1.8)
text(15.5, 40.4, "metric name", size=10.5, weight="bold", color=C_ACCENT)
text(15.5, 38.2, "__name__ = http_requests_total", size=7.8, color="#bfe8e2")

labels = [
    ('method="GET"',                 C_BLUE),
    ('status="200"',                 C_GREEN),
    ('job="api"',                    C_BROWN),
    ('instance="10.0.0.5:8080"',     C_PURPLE),
]
for i, (t, col) in enumerate(labels):
    yy = 30 - i * 6.5
    box(3, yy, 25, 5, col)
    text(15.5, yy + 2.5, t, size=10)

# ================= center: key =================
box(41, 18, 26, 15, C_GRAY, ec=C_ACCENT, lw=2.0)
text(54, 28.4, "라벨 집합 조합", size=13, weight="bold", color=C_ACCENT)
text(54, 24.6, "= 유일한 시계열 ID", size=11.5, weight="bold")
text(54, 21.0, "라벨 값 하나만 바뀌어도\n완전히 별개의 시계열", size=8.5, color=C_DIM)

# ================= right: sample stream =================
box(77, 19, 21, 13, C_BROWN)
text(87.5, 28.4, "샘플 스트림", size=12, weight="bold")
text(87.5, 24.6, "(t1, v1)  (t2, v2)", size=9, color="#e0d4c8")
text(87.5, 22.0, "(t3, v3)  ...", size=9, color="#e0d4c8")

# ---- arrows ----
for (yy, ty) in [(39.75, 30), (32.5, 28), (26, 25.5), (19.5, 23), (13, 21)]:
    arrow(28, yy, 41, ty, color=C_DIM, lw=1.6)
arrow(67, 25.5, 77, 25.5, color=C_ACCENT, lw=2.4)
text(72, 27.6, "append", size=8, color=C_ACCENT, weight="bold")

# bottom
text(50, 3.0, "내부적으로 metric name도 __name__ 예약 라벨일 뿐 — 순수한 라벨 집합으로 취급된다",
     size=10, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "06-timeseries-id.png")
