"""CH12 §1 Ground-Based Speed 메시지(CAN ID + 8바이트 데이터) 분해 (light/dark PNG)."""
from _common import diagram

CAN_ID_PARTS = [
    ("Priority", "3", "blue"),
    ("PGN", "65097 (0xFE49)", "purple"),
    ("SA", "0x0E", "orange"),
]

DATA = ["A0", "0F", "00", "00", "FF", "FF", "FF", "FF"]


def draw(d):
    P = d.P

    # --- 위: CAN ID 구성 요소 (칩 3개) ---
    top_y, h = 24, 5.5
    x0 = 6
    widths = [16, 34, 16]
    gap = 2.0
    d.text(x0, top_y + h + 2.0, "CAN ID = 0x0CFE490E", size=10, ha="left", color=P["text"])
    x = x0
    for (label, value, color), w in zip(CAN_ID_PARTS, widths):
        d.box(x, top_y, w, h, P[color])
        tc = P["bg"] if color == "orange" else P["text"]
        d.text(x + w / 2, top_y + h / 2 + 1.0, label, size=9, weight="bold", color=tc)
        d.text(x + w / 2, top_y + h / 2 - 1.4, value, size=8.5, color=tc)
        x += w + gap

    # --- 아래: 8바이트 데이터, Byte1~2 강조 ---
    cw, gap2 = 9.0, 0.8
    dy, dh = 9, 5.5
    dw_total = 8 * cw + 7 * gap2
    dx0 = (100 - dw_total) / 2
    x = dx0
    for i, hx in enumerate(DATA):
        color = P["accent"] if i < 2 else P["chip"]
        d.box(x, dy, cw, dh, color)
        tc = P["bg"] if i < 2 else P["text"]
        d.text(x + cw / 2, dy + dh / 2, hx, size=11, weight="bold", color=tc)
        d.text(x + cw / 2, dy + dh + 1.3, f"Byte {i + 1}", size=7.5, color=P["dim"])
        x += cw + gap2
    d.text(dx0, dy + dh + 3.6, "Data (8 byte)", size=9.5, ha="left", color=P["dim"])

    # Byte1~2 강조 브래킷 + 해석 값 (박스 아래쪽)
    bx0, bx1 = dx0, dx0 + 2 * cw + gap2 - gap2
    by = dy - 1.6
    d.arrow(bx0, by, bx1, by, color=P["accent"], lw=1.2, style="-")
    d.arrow(bx0, by, bx0, by - 0.8, color=P["accent"], lw=1.2, style="-")
    d.arrow(bx1, by, bx1, by - 0.8, color=P["accent"], lw=1.2, style="-")
    d.text((bx0 + bx1) / 2, by - 2.6,
           "0x0FA0 = 4000 -> 4.0 m/s", size=9, color=P["accent"], weight="bold")


diagram("12-speed-message", draw, w=13, h=4.6, xmax=100, ymax=32)
