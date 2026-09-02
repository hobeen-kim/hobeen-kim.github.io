"""CH10 §2 NAME 예시(0x2000000000000000) 분해 (light/dark PNG)."""
from _common import diagram

NAME_HEX = "0x2000000000000000"
BYTES = ["20", "00", "00", "00", "00", "00", "00", "00"]
TOP_BITS = "00100000"  # 0x20


def draw(d):
    P = d.P

    # --- 위: 64비트 NAME을 8바이트로 표시, Byte1(최상위) 강조 ---
    x0, gap, bw, by, bh = 6, 0.6, 10.2, 19, 6
    x = x0
    for i, hx in enumerate(BYTES):
        color = P["accent"] if i == 0 else P["chip"]
        d.box(x, by, bw, bh, color)
        tc = P["bg"] if i == 0 else P["text"]
        d.text(x + bw / 2, by + bh / 2, hx, size=12, weight="bold", color=tc)
        d.text(x + bw / 2, by + bh + 1.6, f"Byte {i + 1}", size=8, color=P["dim"])
        x += bw + gap
    d.text(x0, by + bh + 4.2, f"NAME = {NAME_HEX}", size=10, ha="left", color=P["text"])

    # --- 아래: Byte1(0x20)을 8비트로 분해, AAC(1)/IG(3)/VSI(4) ---
    sub_groups = [("AAC", 1, "accent"), ("IG", 3, "blue"), ("VSI", 4, "green")]
    cw = 3.4
    sx0 = x0
    sy, sh = 6.5, 5.5

    # 강조 화살표: Byte1 -> 아래 비트 분해로 연결
    x_byte1_c = x0 + bw / 2
    d.arrow(x_byte1_c, by - 0.6, x_byte1_c, sy + sh + 0.4, color=P["accent"], lw=1.6)

    pos = 0
    for label, n, color in sub_groups:
        gx0 = sx0 + pos * cw
        for j in range(n):
            i = pos + j
            d.box(sx0 + i * cw, sy, cw * 0.9, sh, P[color])
            tc = P["bg"] if color == "accent" else P["text"]
            d.text(sx0 + i * cw + cw * 0.45, sy + sh / 2, TOP_BITS[i], size=10, color=tc)
        gx1 = sx0 + (pos + n) * cw - cw * 0.1
        d.text((gx0 + gx1) / 2, sy - 2.0, label, size=8.5, weight="bold", color=P["dim"])
        pos += n

    d.text(sx0, sy - 4.6, "Byte 1 = 0x20 -> AAC=0, IG=010(2), VSI=0000(0)",
           size=9, ha="left", color=P["dim"])


diagram("10-name-example", draw, w=13, h=4.6, xmax=100, ymax=32)
