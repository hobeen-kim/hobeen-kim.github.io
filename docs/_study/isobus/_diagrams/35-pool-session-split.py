"""35장 레코드를 쪼개지 않고 TP 세션에 나눠 담는 예와 ETP 한 세션 비교 (light/dark PNG)."""
from matplotlib.lines import Line2D

from _common import diagram

K = 0.025          # 1바이트 = 0.025 단위
X0 = 17            # 막대 시작
HEAD = 2.5         # 0x11 한 바이트는 보이도록 넓혀 그린다
BAR_H = 4.5
COLORS = ["blue", "green", "purple", "brown", "gray", "blue"]
RECORDS = [700, 650, 500, 400, 350, 400]


def bar(d, y, sizes, start_index, with_head=True):
    P = d.P
    x = X0
    if with_head:
        d.box(x, y, HEAD, BAR_H, P["chip"], ec=P["accent"])
        d.text(x + HEAD / 2, y + BAR_H / 2, "0x11", size=6.5, color=P["accent"])
        x += HEAD
    for i, size in enumerate(sizes):
        w = size * K
        d.box(x, y, w, BAR_H, P[COLORS[(start_index + i) % len(COLORS)]])
        d.text(x + w / 2, y + BAR_H / 2, str(size), size=8.5)
        x += w
    return x


def draw(d):
    P = d.P
    rows = [
        ("풀의 레코드 6개", 33, RECORDS, 0, False),
        ("세션 1 (TP)", 23, RECORDS[:2], 0, True),
        ("세션 2 (TP)", 15, RECORDS[2:], 2, True),
        ("ETP 한 세션", 4, RECORDS, 0, True),
    ]
    ends = []
    for label, y, sizes, idx, head in rows:
        d.text(1, y + BAR_H / 2, label, size=9, ha="left")
        ends.append(bar(d, y, sizes, idx, head))

    d.text(ends[0], 33 + BAR_H + 1.6, "합계 3000바이트", size=8.5, color=P["dim"], ha="right")
    d.text(68, 23 + BAR_H / 2, "1351바이트, TP.DT 193패킷", size=8.5, ha="left")
    d.text(68, 15 + BAR_H / 2, "1651바이트, 236패킷", size=8.5, ha="left")
    d.text(ends[3], 4 + BAR_H + 1.6, "3001바이트, 429패킷", size=8.5, ha="right")

    # TP 한 세션의 한계(0x11 포함 1785바이트)
    limit_x = X0 + HEAD + 1784 * K
    d.ax.add_line(Line2D([limit_x, limit_x], [13.5, 29.5], color=P["orange"], lw=1.5, ls="--", zorder=4))
    d.text(limit_x, 30.8, "TP 한계 1785바이트", size=8.5, color=P["orange"])


diagram("35-pool-session-split", draw, w=12, h=4.8, xmax=100, ymax=40)
