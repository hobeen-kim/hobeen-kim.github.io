"""CH27 flame graph vs icicle — 방향만 반대인 동일 정보 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    stack = [("main", P["gray"]), ("handleRequest", P["blue"]), ("dbQuery", P["brown"])]

    # 좌: flame graph (root 맨 아래)
    d.box(4, 8, 44, 40, P["chip"], ec=P["edge"], lw=1.4)
    d.text(26, 45, "flame graph (전통 방향)", size=12, weight="bold", color=P["orange"])
    d.text(26, 42, "root가 맨 아래 · 위로 쌓임", size=8.5, color=P["dim"], style="italic")

    for i, (t, c) in enumerate(stack):
        y = 13 + i * 9
        ec = P["accent"] if i == 0 else P["edge"]
        d.box(9, y, 34, 7, c, ec=ec, lw=1.6 if i == 0 else 1.4)
        d.text(26, y + 3.5, t, size=11, weight="bold")
        if i < 2:
            d.arrow(26, y + 7, 26, y + 9, color=P["orange"], lw=2.0)
    d.text(26, 11, "root", size=8.5, color=P["accent"], weight="bold")
    d.ax.text(46, 39, "↑ 깊어짐", fontsize=9, color=P["dim"], rotation=90,
              ha="center", va="center", zorder=5)

    # 우: icicle (root 맨 위)
    d.box(52, 8, 44, 40, P["chip"], ec=P["accent"], lw=1.6)
    d.text(74, 45, "icicle (Pyroscope UI 기본)", size=12, weight="bold", color=P["accent"])
    d.text(74, 42, "root가 맨 위 · 아래로 쌓임", size=8.5, color=P["dim"], style="italic")

    for i, (t, c) in enumerate(stack):
        y = 33 - i * 9
        ec = P["accent"] if i == 0 else P["edge"]
        d.box(57, y, 34, 7, c, ec=ec, lw=1.6 if i == 0 else 1.4)
        d.text(74, y + 3.5, t, size=11, weight="bold")
        if i < 2:
            d.arrow(74, y, 74, y - 2, color=P["accent"], lw=2.0)
    d.ax.text(94, 39, "↓ 깊어짐", fontsize=9, color=P["dim"], rotation=90,
              ha="center", va="center", zorder=5)


diagram("27-flame-vs-icicle", draw, w=12, h=6, ymax=50)
