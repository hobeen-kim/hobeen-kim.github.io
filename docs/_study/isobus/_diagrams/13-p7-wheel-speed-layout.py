"""CH13 Part 7 B.3 Wheel-based speed and distance(PGN 65096) 바이트 배치 (light/dark PNG)."""
from _common import diagram

BYTES = [
    ("Byte 1", "C4", "blue"),
    ("Byte 2", "09", "blue"),
    ("Byte 3", "4E", "green"),
    ("Byte 4", "61", "green"),
    ("Byte 5", "BC", "green"),
    ("Byte 6", "00", "green"),
    ("Byte 7", "FF", "brown"),
    ("Byte 8", "15", "purple"),
]

FIELDS = [
    ("bits 8,7", "00", "운전석 반전\nNot reversed"),
    ("bits 6,5", "01", "Start/Stop\nStart"),
    ("bits 4,3", "01", "Key switch\nnot Off"),
    ("bits 2,1", "01", "주행 방향\nForward"),
]


def draw(d):
    P = d.P
    x0, w, gap = 3, 10.6, 1.2
    y, h = 32, 7
    xs = []
    for i, (name, val, col) in enumerate(BYTES):
        x = x0 + i * (w + gap)
        xs.append(x)
        d.box(x, y, w, h, P[col])
        d.text(x + w / 2, y + h + 1.7, name, size=9, weight="bold")
        d.text(x + w / 2, y + h / 2 + (1.3 if i == 6 else 0), val, size=12, weight="bold")
    d.text(xs[6] + w / 2, y + 1.9, "남은 전원 시간\nN/A", size=7.8, color=P["dim"])

    def bracket(xa, xb, yb, label):
        d.arrow(xa, yb, xb, yb, color=P["dim"], lw=1.2, style="-")
        d.arrow(xa, yb, xa, yb + 0.9, color=P["dim"], lw=1.2, style="-")
        d.arrow(xb, yb, xb, yb + 0.9, color=P["dim"], lw=1.2, style="-")
        d.text((xa + xb) / 2, yb - 2.6, label, size=8.5, color=P["dim"])

    by = y - 1.4
    bracket(xs[0], xs[1] + w, by, "Wheel-based speed (LE)\n0x09C4 = 2.500 m/s")
    bracket(xs[2], xs[5] + w, by, "Wheel-based distance (LE)\n0x00BC614E = 12 345.678 m")

    # Byte 8 확대
    fw, fgap, fy, fh = 13.4, 0.8, 4, 10
    fx0 = 100 - 2.4 - (4 * fw + 3 * fgap)
    for i, (bits, val, name) in enumerate(FIELDS):
        fx = fx0 + i * (fw + fgap)
        d.box(fx, fy, fw, fh, P["purple"])
        d.text(fx + fw / 2, fy + fh - 1.6, bits, size=8, color=P["dim"])
        d.text(fx + fw / 2, fy + fh / 2 + 0.4, val, size=11, weight="bold")
        d.text(fx + fw / 2, fy + 2.2, name, size=7.8)
    fx_end = fx0 + 4 * fw + 3 * fgap
    d.arrow(xs[7], y, fx0, fy + fh, color=P["dim"], lw=1.0, style="-", ls="--")
    d.arrow(xs[7] + w, y, fx_end, fy + fh, color=P["dim"], lw=1.0, style="-", ls="--")
    d.text(fx0 - 1.2, fy + fh / 2, "Byte 8 = 0x15\n= 00 01 01 01", size=8.5,
           color=P["dim"], ha="right")


diagram("13-p7-wheel-speed-layout", draw, w=13, h=6.5, xmax=100, ymax=46)
