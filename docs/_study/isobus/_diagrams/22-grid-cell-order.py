"""CH22 §6 grid 셀 순서와 type 1·2 바이너리 배치 (light/dark PNG)."""
from _common import diagram

CELLS = [  # (index, row, col, kg/ha, TZN code, type 2 bytes)
    (0, 0, 0, 150, "01", ["98", "3A", "00", "00"]),
    (1, 0, 1, 200, "02", ["20", "4E", "00", "00"]),
    (2, 1, 0, 100, "03", ["10", "27", "00", "00"]),
    (3, 1, 1, 180, "04", ["50", "46", "00", "00"]),
]


def draw(d):
    P = d.P
    gx, gy, cs = 9, 9, 15
    for idx, row, col, rate, _, _ in CELLS:
        x, y = gx + col * cs, gy + row * cs
        d.box(x, y, cs, cs, P["green"] if idx % 2 == 0 else P["blue"], r=0.005)
        d.text(x + cs / 2, y + cs / 2 + 2.2, f"셀 {idx}", size=10, weight="bold")
        d.text(x + cs / 2, y + cs / 2 - 0.4, f"row {row}, col {col}", size=8.5)
        d.text(x + cs / 2, y + cs / 2 - 3.0, f"{rate} kg/ha", size=8.5)

    d.arrow(gx + 9, gy + 1.8, gx + cs + 5.5, gy + 1.8, color=P["orange"], lw=1.5)
    d.arrow(gx + cs + 5.5, gy + 1.8, gx + 2.5, gy + cs + 1.8, color=P["orange"], lw=1.3, ls="--")
    d.arrow(gx + 2.5, gy + cs + 1.8, gx + cs + 5.5, gy + cs + 1.8, color=P["orange"], lw=1.5)

    d.text(gx, gy - 2.2, "(A, B) = (37.500, 127.000)", size=8.5, ha="left", color=P["dim"])
    d.arrow(gx, gy - 4.6, gx + 2 * cs + 3, gy - 4.6, color=P["dim"], lw=1.2)
    d.text(gx + 2 * cs + 3.6, gy - 4.6, "E (동)", size=8.5, ha="left", color=P["dim"])
    d.arrow(gx - 3, gy, gx - 3, gy + 2 * cs + 3, color=P["dim"], lw=1.2)
    d.text(gx - 3, gy + 2 * cs + 4.6, "N (북)", size=8.5, color=P["dim"])
    d.text(gx + cs / 2, gy + 2 * cs + 1.6, "D = 0.001°", size=8, color=P["dim"])
    d.text(gx + 2 * cs + 1.2, gy + cs / 2, "C = 0.001°", size=8, ha="left", color=P["dim"])

    bx, bw, gap = 50, 2.6, 0.18
    d.text(bx, 42.5, "type 1   I=\"1\"   셀당 u8 TZN 코드   (4바이트)", size=9, ha="left")
    for idx, _, _, _, code, _ in CELLS:
        x = bx + idx * (bw + gap)
        d.box(x, 35.2, bw, 4.2, P["green"] if idx % 2 == 0 else P["blue"], r=0.005)
        d.text(x + bw / 2, 37.3, code, size=8.5)
        d.text(x + bw / 2, 33.4, f"셀{idx}", size=7.5, color=P["dim"])

    d.text(bx, 25.5, "type 2   I=\"2\" J=\"1\"   셀당 int32 리틀 엔디언 x PDV 수   (16바이트)", size=9, ha="left")
    for idx, _, _, rate, _, raw in CELLS:
        for k, b in enumerate(raw):
            x = bx + (idx * 4 + k) * (bw + gap)
            d.box(x, 18.2, bw, 4.2, P["green"] if idx % 2 == 0 else P["blue"], r=0.005)
            d.text(x + bw / 2, 20.3, b, size=8.5)
        cx = bx + idx * 4 * (bw + gap) + (4 * bw + 3 * gap) / 2
        d.text(cx, 16.3, f"셀 {idx}", size=8, color=P["dim"])
        d.text(cx, 13.9, f"{rate * 100}", size=8, color=P["dim"])
    d.text(bx, 10.2, "값 = DDI 0006 (mg/m², 150 kg/ha = 15000)", size=8.5, ha="left", color=P["dim"])


diagram("22-grid-cell-order", draw, w=13, h=6, xmax=100, ymax=48)
