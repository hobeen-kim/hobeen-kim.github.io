"""CH5 3절 11비트 ID 값과 우선순위: 0x000(최고)에서 0x7FF(최저)까지 (light/dark PNG)."""
from _common import diagram

IDS = [0x000, 0x001, 0x100, 0x600, 0x700, 0x7FF]
BOX_W, BOX_H = 12, 7
X0, STEP = 4, 16
Y = 12


def draw(d):
    P = d.P

    groups = ((0, 3, "높은 우선순위", P["orange"]), (3, 6, "낮은 우선순위", P["violet"]))
    for i0, i1, title, color in groups:
        gx = X0 + i0 * STEP - 1.5
        gw = (i1 - i0 - 1) * STEP + BOX_W + 3
        d.box(gx, Y - 9, gw, BOX_H + 17, P["chip"], ec=color, lw=1.4)
        d.text(gx + gw / 2, Y + BOX_H + 5.2, title, size=10, weight="bold", color=color)

    for i, v in enumerate(IDS):
        x = X0 + i * STEP
        fc = P["blue"] if i < 3 else P["purple"]
        d.box(x, Y, BOX_W, BOX_H, fc)
        d.text(x + BOX_W / 2, Y + BOX_H / 2, f"0x{v:03X}", size=10.5, weight="bold")
        b = format(v, "011b")
        d.text(x + BOX_W / 2, Y - 3.0, f"{b[:3]} {b[3:7]} {b[7:]}", size=8.2, color=P["dim"])
        if i < len(IDS) - 1:
            d.arrow(x + BOX_W + 0.3, Y + BOX_H / 2, x + STEP - 0.3, Y + BOX_H / 2,
                    color=P["edge"], lw=1.4)

    d.text(X0 + BOX_W / 2, Y - 6.4, "최고 우선순위", size=8.6, color=P["orange"], weight="bold")
    d.text(X0 + 5 * STEP + BOX_W / 2, Y - 6.4, "최저 우선순위", size=8.6,
           color=P["violet"], weight="bold")


diagram("05-id-priority-scale", draw, w=12, h=3.4, xmax=100, ymax=30)
