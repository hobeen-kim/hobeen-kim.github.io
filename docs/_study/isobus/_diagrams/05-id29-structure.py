"""CH5 §3 29bit Extended ID 필드 구조 개요 (light/dark PNG)."""
from _common import diagram

# (필드명, 비트 범위 라벨, 비트 폭, 색상 키)
FIELDS = [
    ("P P P", "Priority[28:26]", 3, "blue"),
    ("R", "R[25]", 1, "green"),
    ("DP", "DP[24]", 1, "purple"),
    ("PF (8bit)", "[23:16]", 8, "brown"),
    ("PS (8bit)", "[15:8]", 8, "gray"),
    ("SA (8bit)", "[7:0]", 8, "orange"),
]


def draw(d):
    P = d.P
    total_bits = sum(f[2] for f in FIELDS)  # 29
    x0, total_w = 2, 28
    y, h = 7, 6
    scale = total_w / total_bits

    x = x0
    for label, rng, bits, color in FIELDS:
        w = bits * scale
        tcolor = P["bg"] if color == "orange" else None
        d.box(x, y, w, h, P[color])
        d.text(x + w / 2, y + h / 2, label, size=9.5, weight="bold", color=tcolor)
        d.text(x + w / 2, y - 2.2, rng, size=8, color=P["dim"])
        x += w

    d.text(x0, y + h + 2.4, "MSB (bit 28, Priority 최상위)", size=8.3, color=P["dim"], ha="left")
    d.text(x0 + total_w, y + h + 2.4, "LSB (bit 0, SA 최하위)", size=8.3, color=P["dim"], ha="right")
    d.text(x0 + total_w / 2, y - 5.0, "Priority(0~7, 낮을수록 우선순위 높음)", size=8.6, color=P["dim"])


diagram("05-id29-structure", draw, w=12, h=3.9, xmax=32, ymax=18)
