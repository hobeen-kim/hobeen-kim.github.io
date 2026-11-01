"""CH09 §1 16진수 ID를 두 자리씩 끊고 첫 바이트만 비트로 푸는 지름길 (light/dark PNG)."""
from _common import diagram

FIRST_BITS = "00011000"
GROUPS = [  # (시작 비트, 개수, 라벨, 색)
    (0, 3, "버림\n(29비트 밖)", "chip"),
    (3, 3, "Priority\n110 = 6", "blue"),
    (6, 1, "EDP\n0", "green"),
    (7, 1, "DP\n0", "purple"),
]
REST = [  # (x, 16진수, 2진수, 결과 라벨, 색)
    (58, "FE", "1111 1110", "PF\n0xFE = 254", "brown"),
    (79, "EE", "1110 1110", "PS\n0xEE = 238", "gray"),
    (100, "00", "0000 0000", "SA\n0x00 = 0", "chip"),
]


def draw(d):
    P = d.P
    ya, yb, yc = 40, 26, 7
    ha, hb, hc = 7, 7, 11
    fx, fw = 14, 40
    bw = 18

    d.text(6, ya + ha / 2, "16진수", size=9.4, color=P["dim"])
    d.text(6, yb + hb / 2, "2진수", size=9.4, color=P["dim"])
    d.text(6, yc + hc / 2, "칸과 값", size=9.4, color=P["dim"])

    d.box(fx, ya, fw, ha, P["chip"], ec=P["accent"], lw=1.8)
    d.text(fx + fw / 2, ya + ha / 2, "18", size=12, weight="bold")
    cw = fw / 8
    for i, bit in enumerate(FIRST_BITS):
        d.box(fx + i * cw, yb, cw, hb, P["chip"], r=0.01)
        d.text(fx + i * cw + cw / 2, yb + hb / 2, bit, size=10.5)
    d.arrow(fx + fw / 2, ya, fx + fw / 2, yb + hb + 0.4)
    for start, n, label, color in GROUPS:
        x = fx + start * cw
        d.box(x, yc, n * cw, hc, P[color], r=0.01)
        d.text(x + n * cw / 2, yc + hc / 2, label, size=8.6)
        d.arrow(x + n * cw / 2, yb, x + n * cw / 2, yc + hc + 0.4, color=P["dim"], lw=1.3)

    for x, hx, bits, label, color in REST:
        d.box(x, ya, bw, ha, P["chip"])
        d.text(x + bw / 2, ya + ha / 2, hx, size=12, weight="bold")
        d.box(x, yb, bw, hb, P["chip"])
        d.text(x + bw / 2, yb + hb / 2, bits, size=9.6)
        d.box(x, yc, bw, hc, P[color])
        d.text(x + bw / 2, yc + hc / 2, label, size=9.0)
        d.arrow(x + bw / 2, ya, x + bw / 2, yb + hb + 0.4)
        d.arrow(x + bw / 2, yb, x + bw / 2, yc + hc + 0.4)


diagram("09-id-byte-shortcut", draw, w=12, h=4.4, xmax=121, ymax=50)
