"""CH14 §10 DM1/DM2 DTC 4바이트 비트 배치 — 예: 60 08 1F 01 (light/dark PNG)."""
from _common import diagram

EXAMPLE = [0x60, 0x08, 0x1F, 0x01]
FIELDS = [
    ["blue"] * 8,
    ["blue"] * 8,
    ["blue"] * 3 + ["green"] * 5,
    ["brown"] + ["purple"] * 7,
]
CELL, GAP = 2.3, 1.2


def bracket(d, x1, x2, y, label):
    P = d.P
    d.arrow(x1, y, x2, y, color=P["dim"], lw=1.1, style="-")
    d.arrow(x1, y, x1, y + 0.8, color=P["dim"], lw=1.1, style="-")
    d.arrow(x2, y, x2, y + 0.8, color=P["dim"], lw=1.1, style="-")
    d.text((x1 + x2) / 2, y - 1.6, label, size=8.5)


def draw(d):
    P = d.P
    y, h = 17, 7
    for i, x in enumerate((2, 10.5)):
        d.box(x, y, 7, h, P["gray"])
        d.text(x + 3.5, y + h + 2.6, f"Byte {i + 1}", size=9.5, weight="bold")
        d.text(x + 3.5, y + h / 2 + 1, "FF", size=10, weight="bold")
        d.text(x + 3.5, y + h / 2 - 1.4, "Reserved", size=7.5, color=P["dim"])

    x0 = 20
    starts = []
    for b, (value, colors) in enumerate(zip(EXAMPLE, FIELDS)):
        bx = x0 + b * (8 * CELL + GAP)
        starts.append(bx)
        d.text(bx + 4 * CELL, y + h + 2.6, f"Byte {b + 3}", size=9.5, weight="bold")
        for bit in range(8):
            cx = bx + bit * CELL
            d.box(cx, y, CELL, h, P[colors[bit]], lw=1.0, r=0.005)
            d.text(cx + CELL / 2, y + h + 0.9, str(8 - bit), size=7, color=P["dim"])
            d.text(cx + CELL / 2, y + h / 2, str(value >> (7 - bit) & 1), size=10, weight="bold")
        d.text(bx + 4 * CELL, y - 1.8, f"0x{value:02X}", size=9, color=P["accent"], weight="bold")

    by = 11.5
    bracket(d, starts[0] + 0.2, starts[0] + 8 * CELL - 0.2, by, "SPN 비트 1~8")
    bracket(d, starts[1] + 0.2, starts[1] + 8 * CELL - 0.2, by, "SPN 비트 9~16")
    bracket(d, starts[2] + 0.2, starts[2] + 3 * CELL - 0.2, by, "SPN 17~19")
    bracket(d, starts[2] + 3 * CELL + 0.2, starts[2] + 8 * CELL - 0.2, by, "FMI (5 bit)")
    bracket(d, starts[3] + 0.2, starts[3] + CELL - 0.2, by, "CM")
    bracket(d, starts[3] + CELL + 0.2, starts[3] + 8 * CELL - 0.2, by, "OC (7 bit)")
    d.text(60, 5.6, "60 08 1F 01  ->  SPN 2144 (0x860), FMI 31, CM 0, OC 1", size=9.5, color=P["dim"])


diagram("14-dtc-layout", draw, w=13, h=4.3, xmax=100, ymax=28.5)
