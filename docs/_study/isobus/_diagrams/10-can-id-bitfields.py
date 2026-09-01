"""CH10 §1 29비트 CAN Identifier 비트 필드 배치 (light/dark PNG)."""
from _common import diagram

# (필드명, 표시용 라벨, 비트 범위 라벨, 비트 폭, 색상 키)
FIELDS = [
    ("Priority", "Priority", "[28:26]", 3, "blue"),
    ("R", "R", "[25]", 1, "green"),
    ("DP", "DP", "[24]", 1, "purple"),
    ("PF", "PF", "[23:16]", 8, "brown"),
    ("PS", "PS\n(DA/GE)", "[15:8]", 8, "gray"),
    ("SA", "SA", "[7:0]", 8, "orange"),
]


def draw(d):
    P = d.P
    total_bits = sum(f[3] for f in FIELDS)  # 29
    x0, total_w = 2, 28
    y, h = 5, 5
    scale = total_w / total_bits

    x = x0
    for _, label, rng, bits, color in FIELDS:
        w = bits * scale
        d.box(x, y, w, h, P[color])
        d.text(x + w / 2, y + h + 1.3, label, size=10.5, weight="bold")
        d.text(x + w / 2, y - 2.4, rng, size=8.5, color=P["dim"])
        x += w

    d.text(x0, y + h + 3.5, "MSB (bit 28)", size=8.5, color=P["dim"], ha="left")
    d.text(x0 + total_w, y + h + 3.5, "LSB (bit 0)", size=8.5, color=P["dim"], ha="right")


diagram("10-can-id-bitfields", draw, w=12, h=6, xmax=32, ymax=16)
