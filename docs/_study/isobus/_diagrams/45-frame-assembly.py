"""CH45 §5 Process Data 8바이트 손조립: 33 00 01 00 80 84 1E 00과 값의 리틀 엔디언 배치 (light/dark PNG)."""
from _common import diagram

X0, W, GAP = 4, 10.5, 1.0
BY, BH = 24, 11

BYTES = [  # (큰 글자, 작은 설명, 색). None이면 Byte 1처럼 반으로 나눈다
    None,
    ("00", "Element\n상위 8비트", "green"),
    ("01", "DDI\n낮은 자리", "brown"),
    ("00", "DDI\n높은 자리", "brown"),
    ("80", "값\n가장 낮은 자리", "purple"),
    ("84", "값", "purple"),
    ("1E", "값", "purple"),
    ("00", "값\n가장 높은 자리", "purple"),
]
HALVES = (("3", "Element\n하위 4비트", "green"), ("3", "Command", "blue"))
VALUE_BE = ["00", "1E", "84", "80"]       # 높은 자리부터 쓴 2,000,000 = 0x001E8480
VY, VH = 4, 6


def bx(i):
    return X0 + i * (W + GAP)


def draw(d):
    P = d.P
    for i, spec in enumerate(BYTES):
        x = bx(i)
        d.text(x + W / 2, BY + BH + 1.6, f"Byte {i + 1}", size=9.5)
        if spec is None:
            hw = W / 2 - 0.1
            for k, (big, small, color) in enumerate(HALVES):
                hx = x + k * (hw + 0.2)
                d.box(hx, BY, hw, BH, P[color])
                d.text(hx + hw / 2, BY + BH - 3.0, big, size=14)
                d.text(hx + hw / 2, BY + 3.0, small, size=6.8, color=P["dim"])
            d.text(x + W / 2, BY - 1.7, "= 0x33", size=9, color=P["accent"])
            continue
        big, small, color = spec
        d.box(x, BY, W, BH, P[color])
        d.text(x + W / 2, BY + BH - 3.0, big, size=14)
        d.text(x + W / 2, BY + 3.0, small, size=7.2, color=P["dim"])

    for k, hexbyte in enumerate(VALUE_BE):
        x = bx(4 + k)
        d.box(x, VY, W, VH, P["chip"])
        d.text(x + W / 2, VY + VH / 2, hexbyte, size=12)
        target = bx(7 - k) + W / 2
        d.arrow(x + W / 2, VY + VH + 0.2, target, BY - 3.0, color=P["accent"], lw=1.5)
    d.text(bx(4) - 1.5, VY + VH / 2 + 1.3, "2,000,000 = 0x001E8480", size=9.5, ha="right")
    d.text(bx(4) - 1.5, VY + VH / 2 - 1.3, "높은 자리 바이트부터 쓴 값", size=8.5,
           color=P["dim"], ha="right")


diagram("45-frame-assembly", draw, w=12, h=5.2, xmax=100, ymax=43)
