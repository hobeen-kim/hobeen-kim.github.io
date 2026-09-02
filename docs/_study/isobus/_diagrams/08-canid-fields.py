"""CH8 §4 29비트 CAN ID 필드 구조 (light/dark PNG)."""
from _common import diagram

# (필드명, 표시 라벨, packet-beta 비트 범위, 비트 폭, 색상 키)
FIELDS = [
    ("Priority", "Priority\n(3 bit)", "0-2", 3, "blue"),
    ("EDP", "EDP\n(1 bit)", "3-3", 1, "green"),
    ("DP", "DP\n(1 bit)", "4-4", 1, "purple"),
    ("PF", "PF: PDU Format\n(8 bit)", "5-12", 8, "brown"),
    ("PS", "PS: PDU Specific\n(8 bit)", "13-20", 8, "gray"),
    ("SA", "SA: Source Address\n(8 bit)", "21-28", 8, "orange"),
]


def draw(d):
    P = d.P
    total_bits = sum(f[3] for f in FIELDS)  # 29
    x0, total_w = 3, 88
    y, h = 6, 6
    scale = total_w / total_bits

    x = x0
    for _, label, rng, bits, color in FIELDS:
        w = bits * scale
        d.box(x, y, w, h, P[color])
        d.text(x + w / 2, y + h + 2.2, label, size=9.5, weight="bold")
        d.text(x + w / 2, y - 2.6, rng, size=8.5, color=P["dim"])
        x += w


diagram("08-canid-fields", draw, w=13, h=4.2, xmax=94, ymax=18)
