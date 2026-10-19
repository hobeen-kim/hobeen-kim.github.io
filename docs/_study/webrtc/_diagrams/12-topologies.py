"""CH12 §1 세 토폴로지 — Mesh / SFU / MCU 연결 구조 비교 (light/dark PNG)."""
import math

from _common import diagram, Line2D


def draw(d):
    P = d.P
    Y0 = 5  # 패널 하단

    def panel(x, title, sub):
        d.box(x, Y0, 31, 37, P["gray"])
        d.text(x + 15.5, Y0 + 34.4, title, size=11, weight="bold")
        d.text(x + 15.5, Y0 + 31.6, sub, size=8, color=P["dim"])

    def peer(cx, cy, label="피어"):
        d.box(cx - 4, cy - 2.4, 8, 4.8, P["blue"])
        d.text(cx, cy, label, size=9)

    def pair(x1, y1, x2, y2, gap=0.9):
        """x1,y1 → x2,y2 방향 업링크(accent)와 역방향 다운링크(orange)를 평행하게."""
        dx, dy = x2 - x1, y2 - y1
        n = math.hypot(dx, dy)
        ox, oy = -dy / n * gap, dx / n * gap
        d.arrow(x1 + ox, y1 + oy, x2 + ox, y2 + oy, color=P["accent"], lw=1.5)
        d.arrow(x2 - ox, y2 - oy, x1 - ox, y1 - oy, color=P["orange"], lw=1.5)

    # Mesh — 화살표는 박스 가장자리끼리 잇는다
    panel(1, "Mesh", "모든 피어가 서로 직접 연결")
    top, bot = Y0 + 23, Y0 + 7
    for (x, y) in [(8, top), (25, top), (8, bot), (25, bot)]:
        peer(x, y)
    both = dict(color=P["accent"], lw=1.3, style="<|-|>")
    d.arrow(12, top, 21, top, **both)
    d.arrow(12, bot, 21, bot, **both)
    d.arrow(8, top - 2.4, 8, bot + 2.4, **both)
    d.arrow(25, top - 2.4, 25, bot + 2.4, **both)
    d.arrow(12, top - 2.4, 21, bot + 2.4, **both)
    d.arrow(21, top - 2.4, 12, bot + 2.4, **both)
    d.text(16.5, Y0 + 2.2, "피어당 업 N-1 · 다운 N-1", size=8, color=P["dim"])

    def hub(cx, label, fc, xs):
        d.box(cx - 5.5, Y0 + 12.5, 11, 6, fc, ec=P["accent"], lw=1.6)
        d.text(cx, Y0 + 15.5, label, size=9.5, weight="bold")
        for x in xs:
            for y in (Y0 + 25, Y0 + 6):
                peer(x, y)
                tx = cx - 3.5 if x < cx else cx + 3.5
                ty = Y0 + 18.5 if y > Y0 + 15 else Y0 + 12.5
                pair(x, y + (-2.4 if y > Y0 + 15 else 2.4), tx, ty)

    panel(34.5, "SFU", "서버가 패킷을 골라 전달")
    hub(50, "SFU", P["purple"], (40.5, 59.5))
    d.text(50, Y0 + 2.2, "피어당 업 1 · 다운 N-1", size=8, color=P["dim"])

    panel(68, "MCU", "서버가 디코드·합성·재인코드")
    hub(83.5, "MCU\n(합성)", P["brown"], (74, 93))
    d.text(83.5, Y0 + 2.2, "피어당 업 1 · 다운 1(합성본)", size=8, color=P["dim"])

    d.ax.legend(handles=[
        Line2D([0], [0], color=P["accent"], lw=2.2, label="업링크(송신)"),
        Line2D([0], [0], color=P["orange"], lw=2.2, label="다운링크(수신)"),
    ], loc="lower center", bbox_to_anchor=(0.5, -0.01), ncol=2, fontsize=8,
        framealpha=0.0, labelcolor=P["dim"])


diagram("12-topologies", draw, w=14, h=5.8, ymax=43)
