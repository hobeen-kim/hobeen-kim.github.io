"""CH13 Part 7 B.21 Language command(PGN 65039) 바이트 배치: en-US 예 (light/dark PNG)."""
from _common import diagram

BYTES = [
    ("Byte 1", "65", "", "blue"),
    ("Byte 2", "6E", "", "blue"),
    ("Byte 3", "5F", "숫자 형식", "purple"),
    ("Byte 4", "03", "날짜: mmddyyyy", "brown"),
    ("Byte 5", "5A", "단위 1", "green"),
    ("Byte 6", "56", "단위 2", "green"),
    ("Byte 7", "55", "", "gray"),
    ("Byte 8", "53", "", "gray"),
]

GROUPS = [
    (2, "Byte 3 = 0x5F", "purple", [
        ("8,7", "01", "소수점: 점"),
        ("6,5", "01", "시간: 12 h"),
        ("4-1", "1111", "예약"),
    ]),
    (4, "Byte 5 = 0x5A", "green", [
        ("8,7", "01", "거리"),
        ("6,5", "01", "면적"),
        ("4,3", "10", "부피: US"),
        ("2,1", "10", "질량: US"),
    ]),
    (5, "Byte 6 = 0x56", "green", [
        ("8,7", "01", "온도"),
        ("6,5", "01", "압력"),
        ("4,3", "01", "힘"),
        ("2,1", "10", "단위계: US"),
    ]),
]


def draw(d):
    P = d.P
    x0, w, gap = 2.5, 10.8, 1.2
    y, h = 31, 7.5
    xs = []
    for i, (name, val, sub, col) in enumerate(BYTES):
        x = x0 + i * (w + gap)
        xs.append(x)
        d.box(x, y, w, h, P[col])
        d.text(x + w / 2, y + h + 1.6, name, size=9, weight="bold")
        d.text(x + w / 2, y + h / 2 + (0.9 if sub else 0), val, size=12, weight="bold")
        if sub:
            d.text(x + w / 2, y + 1.6, sub, size=7.8, color=P["dim"])

    def top_bracket(xa, xb, label):
        yb = y + h + 4.0
        d.arrow(xa, yb, xb, yb, color=P["dim"], lw=1.2, style="-")
        d.arrow(xa, yb, xa, yb - 0.9, color=P["dim"], lw=1.2, style="-")
        d.arrow(xb, yb, xb, yb - 0.9, color=P["dim"], lw=1.2, style="-")
        d.text((xa + xb) / 2, yb + 1.8, label, size=8.5, color=P["dim"])

    top_bracket(xs[0], xs[1] + w, "Language code 'en' (ISO 639, 소문자)")
    top_bracket(xs[6], xs[7] + w, "Country code 'US' (Amd1, ISO 3166-1)")

    fw, fgap, ggap = 8.2, 0.5, 2.0
    fy, fh = 6, 11
    gx = 1.0
    for byte_idx, caption, col, fields in GROUPS:
        gw = len(fields) * fw + (len(fields) - 1) * fgap
        for j, (bits, val, name) in enumerate(fields):
            fx = gx + j * (fw + fgap)
            d.box(fx, fy, fw, fh, P[col])
            d.text(fx + fw / 2, fy + fh - 1.7, bits, size=7.6, color=P["dim"])
            d.text(fx + fw / 2, fy + fh / 2, val, size=10, weight="bold")
            d.text(fx + fw / 2, fy + 1.9, name, size=7.6)
        bx = xs[byte_idx]
        d.arrow(bx, y, gx, fy + fh, color=P["dim"], lw=1.0, style="-", ls="--")
        d.arrow(bx + w, y, gx + gw, fy + fh, color=P["dim"], lw=1.0, style="-", ls="--")
        d.text(gx + gw / 2, fy - 2.2, caption, size=8.5, color=P["dim"])
        gx += gw + ggap


diagram("13-p7-language-command-layout", draw, w=14, h=5.9, xmax=100, ymax=49)
