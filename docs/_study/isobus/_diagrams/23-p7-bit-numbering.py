"""CH23 바이트 안의 비트 번호와 바이트 경계에 걸친 5비트 값 (light/dark PNG)."""
from _common import diagram

BYTE7 = [1, 0, 1, 0, 0, 0, 0, 0]   # bit 8 .. bit 1 (0xA0)
BYTE8 = [0, 0, 0, 0, 0, 0, 1, 0]   # bit 8 .. bit 1 (0x02)


def draw(d):
    P = d.P
    cw, ch = 5.0, 6.0
    y = 30
    x7 = 7
    x8 = x7 + 8 * cw + 6

    def byte_row(x0, bits, hi_cols, hi_color, name):
        for i, b in enumerate(bits):
            fc = hi_color if i in hi_cols else P["chip"]
            d.box(x0 + i * cw, y, cw, ch, fc, lw=1.1, r=0.005)
            d.text(x0 + i * cw + cw / 2, y + ch / 2, str(b), size=11,
                   weight="bold" if i in hi_cols else "normal",
                   color=P["text"] if i in hi_cols else P["dim"])
            d.text(x0 + i * cw + cw / 2, y + ch + 1.6, str(8 - i), size=8.5,
                   color=P["dim"])
        d.text(x0 + 4 * cw, y + ch + 5.4, name, size=11, weight="bold")

    byte_row(x7, BYTE7, {0, 1, 2}, P["green"], "Byte 7 = 0xA0")
    byte_row(x8, BYTE8, {6, 7}, P["purple"], "Byte 8 = 0x02")
    d.text(x7 - 1.2, y + ch + 1.6, "bit", size=8.5, color=P["dim"], ha="right")
    d.text(x7, y - 2.6, "bit 8 (최상위)", size=8.5, color=P["dim"], ha="left")
    d.text(x7 + 8 * cw, y - 2.6, "bit 1 (최하위)", size=8.5, color=P["dim"], ha="right")

    d.text(x7 + 1.5 * cw, y - 6.6, "값의 아래 세 자리", size=9.5, color=P["dim"])
    d.text(x8 + 7 * cw, y - 6.6, "값의 위 두 자리", size=9.5, color=P["dim"])

    # assembled value
    vx, vy = 31, 4
    vals = [(1, P["purple"]), (0, P["purple"]), (1, P["green"]), (0, P["green"]), (1, P["green"])]
    for i, (b, col) in enumerate(vals):
        d.box(vx + i * cw, vy, cw, ch, col, lw=1.1, r=0.005)
        d.text(vx + i * cw + cw / 2, vy + ch / 2, str(b), size=12, weight="bold")
    d.text(vx + 5 * cw + 2, vy + ch / 2, "= 10101(2) = 21", size=11.5, ha="left", weight="bold")
    d.text(vx - 2, vy + ch / 2, "5비트 값", size=10.5, ha="right")

    d.arrow(x8 + 7 * cw, y - 8.6, vx + 1 * cw, vy + ch + 1.0, color=P["violet"])
    d.arrow(x7 + 1.5 * cw, y - 8.6, vx + 3.5 * cw, vy + ch + 1.0, color=P["accent"])


diagram("23-p7-bit-numbering", draw, w=12, h=5.6, xmax=100, ymax=46)
