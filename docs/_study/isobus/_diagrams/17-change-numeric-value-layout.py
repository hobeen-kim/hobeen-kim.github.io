"""CH17 §2 Change Numeric Value 메시지(8 byte) 바이트 레이아웃 (light/dark PNG)."""
from _common import diagram

BYTES = [
    ("Byte 1", "0xA8", "Command Byte", "blue"),
    ("Byte 2", "LSB", "Object ID", "green"),
    ("Byte 3", "MSB", "Object ID", "green"),
    ("Byte 4", "0xFF", "예약", "gray"),
    ("Byte 5", "", "", "brown"),
    ("Byte 6", "", "", "brown"),
    ("Byte 7", "", "", "brown"),
    ("Byte 8", "", "", "brown"),
]


def draw(d):
    P = d.P
    n = 8
    x0, gap = 2, 0.4
    w = 3.2
    y, h = 8, 5

    x = x0
    value_x0 = None
    for i, (bname, val, sub, color) in enumerate(BYTES):
        d.box(x, y, w, h, P[color])
        d.text(x + w / 2, y + h + 1.2, bname, size=9, weight="bold")
        if val:
            d.text(x + w / 2, y + h / 2 + 1.1, val, size=9.5, weight="bold")
            d.text(x + w / 2, y + h / 2 - 1.1, sub, size=7.5, color=P["dim"])
        if i == 4:
            value_x0 = x
        x += w + gap
    x_end = x - gap
    d.text((value_x0 + x_end) / 2, y + h / 2, "새 값", size=9.5, weight="bold")

    # Object ID (Byte 2~3) 묶음
    x2, x3 = x0 + (w + gap), x0 + (w + gap) * 3 - gap
    bracket_y = y - 1.4
    d.arrow(x2, bracket_y, x3, bracket_y, color=P["dim"], lw=1.2, style="-")
    d.arrow(x2, bracket_y, x2, bracket_y + 0.6, color=P["dim"], lw=1.2, style="-")
    d.arrow(x3, bracket_y, x3, bracket_y + 0.6, color=P["dim"], lw=1.2, style="-")
    d.text((x2 + x3) / 2, bracket_y - 1.5, "Object ID (16bit, LE)", size=8.5, color=P["dim"])

    # 새 값 (Byte 5~8) 묶음
    x4 = x0 + (w + gap) * 4
    bracket_y2 = y - 1.4
    d.arrow(x4, bracket_y2, x_end, bracket_y2, color=P["dim"], lw=1.2, style="-")
    d.arrow(x4, bracket_y2, x4, bracket_y2 + 0.6, color=P["dim"], lw=1.2, style="-")
    d.arrow(x_end, bracket_y2, x_end, bracket_y2 + 0.6, color=P["dim"], lw=1.2, style="-")
    d.text((x4 + x_end) / 2, bracket_y2 - 1.5, "새 값 (32bit unsigned, LE)", size=8.5, color=P["dim"])


diagram("17-change-numeric-value-layout", draw, w=12, h=6, xmax=32, ymax=16)
