"""CH30 Get Hardware response `C7 1E 02 31 E0 01 E0 01`의 바이트 배치와 Byte 4 비트 (light/dark PNG)."""
from _common import diagram

BYTES = [
    ("C7", "Get Hardware", "blue"),
    ("1E", "Boot time\n30초", "green"),
    ("02", "Graphic Type\n256색", "green"),
    ("31", "Hardware\n비트 8개", "gray"),
    ("E0", "X 낮은 자리", "brown"),
    ("01", "X 높은 자리", "brown"),
    ("E0", "Y 낮은 자리", "purple"),
    ("01", "Y 높은 자리", "purple"),
]

BITS = [
    (7, 0, "드래그 중간\n좌표 보고"),
    (6, 0, "드래그를\nPointing Event로"),
    (5, 1, "Button\n동시 활성"),
    (4, 1, "물리 Soft Key\n동시 활성"),
    (3, 0, "음량 조절\n오디오"),
    (2, 0, "다중 주파수\n오디오"),
    (1, 0, "포인팅 장치"),
    (0, 1, "터치스크린"),
]

BW, GAP, X0 = 10.6, 1.4, 3.0


def bx(i):
    return X0 + i * (BW + GAP)


def draw(d):
    P = d.P
    top_y, top_h = 30, 9
    for i, (val, label, color) in enumerate(BYTES):
        x = bx(i)
        d.text(x + BW / 2, top_y + top_h + 1.6, f"Byte {i + 1}", size=9.5)
        d.box(x, top_y, BW, top_h, P[color], ec=P["accent"] if i == 3 else None)
        d.text(x + BW / 2, top_y + 6.4, val, size=12, weight="bold")
        d.text(x + BW / 2, top_y + 2.6, label, size=8.2, color=P["dim"])

    for i0, label in [(4, "X-Pixels = 0x01E0 = 480"), (6, "Y-Pixels = 480 (항상 X와 같다)")]:
        x1, x2 = bx(i0) + 0.3, bx(i0 + 1) + BW - 0.3
        yb = top_y + top_h + 4.6
        d.ax.plot([x1, x1, x2, x2], [yb - 0.6, yb, yb, yb - 0.6], color=P["edge"], lw=1.4)
        d.text((x1 + x2) / 2, yb + 1.8, label, size=8.8, color=P["dim"])

    low_y, low_h = 8, 9
    for j, (bit, val, label) in enumerate(BITS):
        x = bx(j)
        on = val == 1
        d.box(x, low_y, BW, low_h, P["green"] if on else P["chip"], ec=P["accent"] if on else None)
        d.text(x + BW / 2, low_y + 6.3, str(val), size=12, weight="bold",
               color=P["text"] if on else P["dim"])
        d.text(x + BW / 2, low_y + 2.6, label, size=7.8, color=P["text"] if on else P["dim"])
        d.text(x + BW / 2, low_y - 2.2, f"bit {bit}", size=8.6, color=P["dim"])

    c = bx(3)
    d.ax.plot([c, bx(0)], [top_y, low_y + low_h], color=P["edge"], ls="--", lw=1.1, zorder=1)
    d.ax.plot([c + BW, bx(7) + BW], [top_y, low_y + low_h], color=P["edge"], ls="--", lw=1.1, zorder=1)
    d.text(bx(3) + BW + 1.0, 22.0, "0x31 = 0011 0001", size=9, color=P["accent"], ha="left")


diagram("30-get-hardware-response", draw, w=13, h=6.0, xmax=100, ymax=50)
