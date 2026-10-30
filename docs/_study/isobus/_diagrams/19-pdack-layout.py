"""CH19 §10 PDACK(command D) 8바이트 배치와 Byte 5 오류 비트 (light/dark PNG)."""
from _common import diagram

W, GAP = 4.2, 0.4
X0 = 1.8
Y, H = 15.0, 4.6

# (라벨, 내용, 색상) — None이면 반쪽 박스 2개로 나눠 그린다
BYTES = [
    None,
    ("Element 상위 8비트", "N/A: FF", "green"),
    ("DDI LSB", "", "brown"),
    ("DDI MSB", "N/A: FFFF", "brown"),
    ("오류 코드", "0 = 정상", "purple"),
    None,
    ("예약", "FF", "gray"),
    ("예약", "FF", "gray"),
]

HALVES = {
    0: (("Element\n하위 4비트", "green"), ("1101\n(D)", "blue")),
    5: (("예약\nF", "gray"), ("응답 대상\n명령 (v4)", "blue")),
}

BITS = [
    (8, "운영 범위\n밖 (v4)"),
    (7, "DDI 정의\n위반 (v4)"),
    (6, "interval·\nthreshold 무효"),
    (5, "settable\n아님"),
    (4, "trigger\n미지원"),
    (3, "element의\nDDI 미지원"),
    (2, "잘못된\nelement"),
    (1, "명령\n미지원"),
]


def draw(d):
    P = d.P
    x = X0
    byte5_x = None
    for i, spec in enumerate(BYTES):
        d.text(x + W / 2, Y + H + 1.1, f"Byte {i + 1}", size=9, weight="bold")
        if spec is None:
            (l_txt, l_col), (r_txt, r_col) = HALVES[i]
            hw = W / 2 - 0.05
            d.box(x, Y, hw, H, P[l_col])
            d.box(x + W / 2 + 0.05, Y, hw, H, P[r_col])
            d.text(x + hw / 2, Y + H / 2, l_txt, size=7)
            d.text(x + W / 2 + 0.05 + hw / 2, Y + H / 2, r_txt, size=7)
            d.text(x + hw / 2, Y - 0.9, "bit 8~5", size=6.5, color=P["dim"])
            d.text(x + W / 2 + 0.05 + hw / 2, Y - 0.9, "bit 4~1", size=6.5, color=P["dim"])
        else:
            label, sub, color = spec
            d.box(x, Y, W, H, P[color], ec=P["accent"] if i == 4 else None,
                  lw=2.2 if i == 4 else 1.4)
            d.text(x + W / 2, Y + H / 2 + (0.8 if sub else 0), label, size=8, weight="bold")
            if sub:
                d.text(x + W / 2, Y + H / 2 - 1.0, sub, size=7.5, color=P["dim"])
        if i == 4:
            byte5_x = x
        x += W + GAP

    # Byte 5 -> 비트 전개
    bw, bgap = 4.2, 0.4
    bits_total = 8 * bw + 7 * bgap
    bx0 = X0 + (36.4 - bits_total) / 2
    by, bh = 4.4, 3.4
    d.arrow(byte5_x + W / 2, Y - 0.2, bx0 + bits_total / 2, by + bh + 1.6,
            color=P["dim"], lw=1.3)
    d.text(bx0 + bits_total / 2 + 3.6, (Y + by + bh) / 2 + 0.4, "Byte 5 비트 전개",
           size=8, color=P["dim"])
    for j, (bit, label) in enumerate(BITS):
        cx = bx0 + j * (bw + bgap)
        color = "brown" if bit >= 7 else "purple"
        d.box(cx, by, bw, bh, P[color])
        d.text(cx + bw / 2, by + bh / 2, f"bit {bit}", size=8.5, weight="bold")
        d.text(cx + bw / 2, by - 1.5, label, size=7, color=P["dim"])
        d.text(cx + bw / 2, by + bh + 0.7, f"0x{1 << (bit - 1):02X}", size=7.5,
               color=P["accent"])


diagram("19-pdack-layout", draw, w=12, h=6.2, xmax=40, ymax=21.5)
