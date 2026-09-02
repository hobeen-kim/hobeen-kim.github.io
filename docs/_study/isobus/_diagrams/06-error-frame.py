"""CH6 §2 Error Frame 구조 — Active Error Flag + Error Delimiter (light/dark PNG)."""
from _common import diagram

FIELDS = [
    ("Active Error Flag\n(6bit Dominant)", 6, "orange"),
    ("Error Delimiter\n(8bit Recessive)", 8, "gray"),
]


def draw(d):
    P = d.P
    total_bits = sum(n for _, n, _ in FIELDS)
    x0, total_w = 4, 92
    y, h = 8, 9
    scale = total_w / total_bits

    x = x0
    for label, bits, color in FIELDS:
        w = bits * scale
        tcolor = P["bg"] if color == "orange" else None
        d.box(x, y, w, h, P[color])
        d.text(x + w / 2, y + h / 2, label, size=11, weight="bold", color=tcolor)
        d.text(x + w / 2, y - 2.6, f"{bits}bit", size=9, color=P["dim"])
        x += w

    d.text(x0, y + h + 2.6, "오류 감지 직후", size=9, color=P["dim"], ha="left")
    d.text(x0 + total_w, y + h + 2.6, "정상 프레임 재개 가능", size=9, color=P["dim"], ha="right")


diagram("06-error-frame", draw, w=11, h=3.6, xmax=100, ymax=24)
