"""CH9 §1 29비트 CAN ID 필드 구조 + 비트 번호 (light/dark PNG)."""
from _common import diagram

# (필드명, 표시 라벨, 비트 폭, 색상 키)
FIELDS = [
    ("Priority", "Priority\n(3 bit)", 3, "blue"),
    ("EDP", "EDP", 1, "green"),
    ("DP", "DP", 1, "purple"),
    ("PF", "PF (PDU Format)\n(8 bit)", 8, "brown"),
    ("PS", "PS (PDU Specific)\n(8 bit)", 8, "gray"),
    ("SA", "SA (Source Address)\n(8 bit)", 8, "orange"),
]


def draw(d):
    P = d.P
    total_bits = sum(f[2] for f in FIELDS)  # 29
    x0, total_w = 3, 90
    y, h = 12, 7
    scale = total_w / total_bits

    x = x0
    pos = 0
    for name, label, bits, color in FIELDS:
        w = bits * scale
        d.box(x, y, w, h, P[color])
        d.text(x + w / 2, y + h + 2.4, label, size=9, weight="bold")
        # 비트 번호 눈금 (bit 28이 맨 왼쪽, bit 0이 맨 오른쪽)
        for j in range(bits):
            bx = x + (j + 0.5) * scale
            bit_num = 28 - (pos + j)
            d.ax.plot([bx, bx], [y - 0.4, y], color=P["edge"], lw=0.8)
            d.text(bx, y - 2.2, str(bit_num), size=6.3, color=P["dim"])
        x += w
        pos += bits


diagram("09-canid-fields", draw, w=13.5, h=4.6, xmax=96, ymax=24)
