"""CH10 §8 NAME(PGN 60928)과 NAME management(PGN 37632) 데이터 바이트 비교 (light/dark PNG)."""
from _common import diagram

# 왼쪽이 Byte 8(최상위), 오른쪽이 Byte 1: Part 5 Figure 1·3과 같은 방향
NAME_ROW = [
    ("Byte 8", "AAC 1\nIG 3\nDCI 4", "blue"),
    ("Byte 7", "DC 7\nR 1 (=0)", "blue"),
    ("Byte 6", "Function 8", "blue"),
    ("Byte 5", "FI 5\nEI 3", "blue"),
    ("Byte 4", "MC\n상위 8", "blue"),
    ("Byte 3", "MC 하위 3\nID 상위 5", "green"),
    ("Byte 2", "ID\n중간 8", "green"),
    ("Byte 1", "ID\n하위 8", "green"),
]

NM_ROW = [
    ("Byte 8", "AAC 1\nIG 3\nDCI 4", "blue"),
    ("Byte 7", "DC 7\nR 1 (=1)", "blue"),
    ("Byte 6", "Function 8", "blue"),
    ("Byte 5", "FI 5\nEI 3", "blue"),
    ("Byte 4", "MC\n상위 8", "blue"),
    ("Byte 3", "MC 하위 3\nR 1 (=1)\nMode 4", "brown"),
    ("Byte 2", "Qualifier\nflags 8", "purple"),
    ("Byte 1", "Checksum\n/ Error", "purple"),
]


def row(d, y, cells, label):
    P = d.P
    x0, w, gap, h = 17, 14.2, 0.8, 11
    d.text(x0 - 1.5, y + h / 2, label, size=9.5, weight="bold", ha="right")
    for i, (byte, field, color) in enumerate(cells):
        x = x0 + i * (w + gap)
        d.box(x, y, w, h, P[color])
        d.text(x + w / 2, y + h / 2, field, size=8.6)
        d.text(x + w / 2, y + h + 1.6, byte, size=8, color=P["dim"])
    return x0, w, gap


def draw(d):
    P = d.P
    x0, w, gap = row(d, 33, NAME_ROW, "NAME\n(Address\nClaimed)")
    row(d, 13, NM_ROW, "NM 메시지\n(PGN 37632)")

    # Byte 8~4: 같은 비트 자리
    for i in range(5):
        cx = x0 + i * (w + gap) + w / 2
        d.arrow(cx, 32.4, cx, 27.0, color=P["accent"], lw=1.2, style="<|-|>")
    xb = x0 + 5 * (w + gap)
    d.text(xb + 1.0, 29.7, "<- Byte 8~4는 같은 비트 자리 (Cmd 필드)", size=8.5,
           color=P["accent"], ha="left")

    # 전송 순서: Byte 1 먼저
    y = 6.5
    x_right = x0 + 8 * (w + gap) - gap
    d.arrow(x_right, y, x0, y, color=P["orange"], lw=1.6)
    d.text((x0 + x_right) / 2, y - 2.4, "CAN 데이터 필드 전송 순서: Byte 1 -> Byte 8", size=8.5,
           color=P["orange"])
    d.text(x0, 48.8, "MSB", size=8, color=P["dim"], ha="left")
    d.text(x_right, 48.8, "LSB", size=8, color=P["dim"], ha="right")


diagram("10-nm-byte-layout", draw, w=13, h=5.2, xmax=140, ymax=52)
