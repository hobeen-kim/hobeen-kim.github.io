"""CH12 CAN ID 0x18EEFF80을 29비트로 펼쳐 필드별로 나누고 SA를 강조 (light/dark PNG)."""
from _common import diagram

CAN_ID = 0x18EEFF80
BITS_MSB_FIRST = format(CAN_ID, "029b")
FIELDS = [
    ("Priority", 3, "blue", "6", "우선순위"),
    ("R", 1, "green", "0", ""),
    ("DP", 1, "purple", "0", ""),
    ("PF", 8, "brown", "0xEE (238)", "Address Claimed"),
    ("PS", 8, "gray", "0xFF (255)", "목적지: 모두"),
    ("SA", 8, "accent", "0x80 (128)", "보낸 장치의 주소"),
]


def draw(d):
    P = d.P
    cw, x0, y0, ch = 2.95, 7.2, 11.5, 6.2

    d.text(x0, y0 + 18.8, f"CAN ID 0x{CAN_ID:08X}", size=10.5, ha="left", weight="bold")
    d.text(x0, y0 + 13.6, "MSB (bit 28)", size=8, ha="left", color=P["dim"])
    d.text(x0 + 29 * cw, y0 + 13.6, "LSB (bit 0)", size=8, ha="right", color=P["dim"])

    pos = 0
    for name, n_bits, color, value_label, meaning in FIELDS:
        gx0 = x0 + pos * cw
        gx1 = x0 + (pos + n_bits) * cw
        hot = color == "accent"
        for j in range(n_bits):
            i = pos + j
            d.box(x0 + i * cw + 0.12, y0, cw - 0.24, ch, P[color], lw=1.0, r=0.006)
            d.text(x0 + i * cw + cw / 2, y0 + ch / 2, BITS_MSB_FIRST[i], size=9.5,
                   color=P["bg"] if hot else P["text"], weight="bold" if hot else "normal")
        cx = (gx0 + gx1) / 2
        d.text(cx, y0 + ch + 2.4, name, size=9.5, weight="bold")
        d.ax.plot([gx0 + 0.3, gx0 + 0.3, gx1 - 0.3, gx1 - 0.3],
                  [y0 - 1.0, y0 - 1.8, y0 - 1.8, y0 - 1.0],
                  color=P["accent"] if hot else P["edge"], lw=1.3, zorder=3)
        d.text(cx, y0 - 4.2, value_label, size=9.2, weight="bold" if hot else "normal",
               color=P["accent"] if hot else P["text"])
        if meaning:
            d.text(cx, y0 - 7.6, meaning, size=8.5, color=P["accent"] if hot else P["dim"])
        pos += n_bits


diagram("12-can-id-sa", draw, w=12, h=3.3, xmax=100, ymax=33.5)
