"""CH10 §2 64비트 NAME 필드 구성 (light/dark PNG)."""
from _common import diagram

# (라벨, 비트 범위(MSB 기준), 비트 폭, 색상 키, 라벨 위치 레벨 0/1)
FIELDS = [
    ("AAC", "63", 1, "accent", 1),
    ("IG", "62-60", 3, "blue", 0),
    ("VSI", "59-56", 4, "green", 1),
    ("VS", "55-49", 7, "purple", 0),
    ("Rsvd", "48", 1, "gray", 1),
    ("Function", "47-40", 8, "brown", 0),
    ("FI", "39-35", 5, "chip", 1),
    ("EI", "34-32", 3, "violet", 0),
    ("Manufacturer\nCode", "31-21", 11, "orange", 1),
    ("Identity\nNumber", "20-0", 21, "blue", 0),
]

assert sum(f[2] for f in FIELDS) == 64


def draw(d):
    P = d.P
    total_bits = 64
    x0, total_w = 4, 92
    y, h = 11, 7
    scale = total_w / total_bits

    x = x0
    for label, rng, bits, color, lvl in FIELDS:
        w = bits * scale
        d.box(x, y, w, h, P[color])
        ly = y + h + (1.4 if lvl == 0 else 4.0)
        d.text(x + w / 2, ly, label, size=9, weight="bold")
        d.text(x + w / 2, y - 2.2, rng, size=7.5, color=P["dim"])
        x += w

    d.text(x0, y + h + 6.6, "MSB (bit 63)", size=8.5, color=P["dim"], ha="left")
    d.text(x0 + total_w, y + h + 6.6, "LSB (bit 0)", size=8.5, color=P["dim"], ha="right")


diagram("10-name-fields", draw, w=13, h=4.2, xmax=100, ymax=27)
