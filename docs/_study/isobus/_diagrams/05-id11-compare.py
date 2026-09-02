"""CH5 §2 11bit ID 이진수 비교 — 노드A(0x100) vs 노드B(0x200) (light/dark PNG)."""
from _common import diagram

ROWS = [
    ("노드A", "0x100", "00010000000"),
    ("노드B", "0x200", "00100000000"),
]

LABEL_X, LABEL_W = 2, 16
CW = 6.6
BIT_X0 = LABEL_X + LABEL_W + 3
ROW_H, GAP = 8, 3
Y_TOP = 20


def draw(d):
    P = d.P

    for i in range(11):
        d.text(BIT_X0 + i * CW + CW / 2, Y_TOP + ROW_H + 1.6, str(10 - i),
               size=7.5, color=P["dim"])
    d.text(BIT_X0 + CW / 2, Y_TOP + ROW_H + 4.2, "MSB(bit10)", size=8, color=P["dim"])
    d.text(BIT_X0 + 10 * CW + CW / 2, Y_TOP + ROW_H + 4.2, "LSB(bit0)", size=8, color=P["dim"])

    for r, (name, hx, bits) in enumerate(ROWS):
        y = Y_TOP - r * (ROW_H + GAP)
        d.box(LABEL_X, y, LABEL_W, ROW_H, P["chip"], ec=P["edge"], lw=1.0)
        d.text(LABEL_X + LABEL_W / 2, y + ROW_H * 0.62, name, size=10, weight="bold")
        d.text(LABEL_X + LABEL_W / 2, y + ROW_H * 0.26, hx, size=8.3, color=P["dim"])

        for i, b in enumerate(bits):
            color = P["blue"] if r == 0 else P["purple"]
            d.box(BIT_X0 + i * CW, y, CW * 0.9, ROW_H, color, ec=P["edge"], lw=1.0)
            d.text(BIT_X0 + i * CW + CW * 0.45, y + ROW_H / 2, b, size=10)


diagram("05-id11-compare", draw, w=11, h=4.4, xmax=100, ymax=35)
