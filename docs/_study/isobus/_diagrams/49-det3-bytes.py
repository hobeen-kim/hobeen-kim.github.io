"""49장 8절: DET 3 레코드 26바이트를 필드별로 나눈 바이트 띠 (light/dark PNG)."""
from _common import diagram

RECORD = bytes.fromhex("44 45 54 03 00 04 09 53 65 63 74 69 6F 6E 20 31 01 00 02 00 02 00 07 00 08 00")
HEAD, FIX, CNT, STR = "blue", "green", "gray", "brown"

# (첫 바이트 번호, 끝 바이트 번호, 색, 필드 라벨)
FIELDS = [
    (1, 3, HEAD, "Table ID\n'DET'"),
    (4, 5, HEAD, "Object ID\n3"),
    (6, 6, FIX, "type\n4"),
    (7, 7, CNT, "N\n9"),
    (8, 16, STR, "designator\n'Section 1'"),
    (17, 18, FIX, "element\nnumber 1"),
    (19, 20, FIX, "부모\nObject ID 2"),
    (21, 22, CNT, "참조\n개수 2"),
    (23, 24, FIX, "참조\nDPD 7"),
    (25, 26, FIX, "참조\nDPD 8"),
]
X0, CW, GAP = 1.6, 3.62, 0.12
SY, SH = 12.6, 6.0


def cell_x(n):
    return X0 + (n - 1) * (CW + GAP)


def draw(d):
    P = d.P
    color_of = {}
    for a, b, color, _ in FIELDS:
        for n in range(a, b + 1):
            color_of[n] = color
    for n, value in enumerate(RECORD, 1):
        x = cell_x(n)
        d.box(x, SY, CW, SH, P[color_of[n]], lw=0.9)
        d.text(x + CW / 2, SY + SH / 2, f"{value:02X}", size=8.0, weight="bold")
        d.text(x + CW / 2, SY + SH + 1.6, str(n), size=6.4, color=P["dim"])
        if n <= 3 or color_of[n] == STR:
            ch = chr(value) if value != 0x20 else "공백"
            d.text(x + CW / 2, SY - 1.6, ch, size=6.6 if value == 0x20 else 7.4,
                   color=P["dim"])
    d.text(X0, SY + SH + 3.6, "바이트 번호", size=6.8, color=P["dim"], ha="left")

    for a, b, _, label in FIELDS:
        x1, x2 = cell_x(a) + 0.2, cell_x(b) + CW - 0.2
        yb = SY - 4.0
        d.ax.plot([x1, x1, x2, x2], [yb + 0.8, yb, yb, yb + 0.8], color=P["edge"], lw=1.0)
        d.text((x1 + x2) / 2, yb - 3.4, label, size=6.8)


diagram("49-det3-bytes", draw, w=14, h=3.5, xmax=100, ymax=25.0)
