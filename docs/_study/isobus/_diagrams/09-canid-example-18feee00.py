"""CH9 §1,§5 예시 0x18FEEE00 → 필드 분해 (light/dark PNG)."""
from _common import diagram

# (필드명, 이진값, 결과 라벨, 비트 폭, 색상 키)
FIELDS = [
    ("Priority", "110", "6", 3, "blue"),
    ("EDP", "0", "0", 1, "green"),
    ("DP", "0", "0", 1, "purple"),
    ("PF", "1111 1110", "0xFE=254", 8, "brown"),
    ("PS", "1110 1110", "0xEE=238", 8, "gray"),
    ("SA", "0000 0000", "0x00\n엔진 ECU", 8, "orange"),
]


def draw(d):
    P = d.P
    total_bits = sum(f[3] for f in FIELDS)  # 29
    x0, total_w = 3, 88
    y, h = 10, 7
    scale = total_w / total_bits

    d.text(x0, y + h + 6.4, "0x18FEEE00", size=11, weight="bold", ha="left", color=P["accent"])

    x = x0
    for name, bits_str, result, bits, color in FIELDS:
        w = bits * scale
        d.box(x, y, w, h, P[color])
        in_box_color = P["bg"] if color in ("orange", "accent") else None
        d.text(x + w / 2, y + h + 2.4, name, size=9, weight="bold")
        d.text(x + w / 2, y + h / 2, bits_str, size=8 if bits > 1 else 9, color=in_box_color)
        d.text(x + w / 2, y - 3.0, result, size=8, color=P["dim"])
        x += w


diagram("09-canid-example-18feee00", draw, w=13, h=4.6, xmax=94, ymax=24)
