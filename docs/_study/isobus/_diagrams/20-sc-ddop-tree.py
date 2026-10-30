"""CH20 §11 Annex F 규칙을 반영해 고친 7섹션 붐 살포기 DDOP 트리 (light/dark PNG)."""
from _common import diagram

SET, RO, PROP = "blue", "chip", "brown"

ROOT_CHIPS = [("119", "Total Time", SET), ("116", "Total Area", SET), ("117", "Total Distance", SET)]
CNN_CHIPS = [("134", "Offset X", PROP), ("135", "Offset Y", PROP), ("157", "Connector Type", PROP)]
BOOM_ROWS = [
    [("1", "Setpoint\nVolume/Area", SET), ("2", "Actual\nVolume/Area", RO),
     ("158", "Prescription\nControl State", SET), ("141", "Actual\nWork State", RO),
     ("161", "Actual\nCondensed WS", RO), ("290", "Setpoint\nCondensed WS", SET),
     ("160", "Section\nControl State", SET)],
    [("205", "SC Turn\nOn Time", SET), ("206", "SC Turn\nOff Time", SET),
     ("80", "rate의\n총계", SET), ("70", "Maximum\nWorking Width", PROP),
     ("134", "Offset X", PROP), ("135", "Offset Y", PROP)],
]


def chip(d, x, y, w, h, ddi, name, color, size=6.6):
    P = d.P
    d.box(x, y, w, h, P[color], lw=1.0)
    d.text(x + w / 2, y + h - 1.0, ddi, size=size + 0.6, weight="bold")
    d.text(x + w / 2, y + (h - 1.6) / 2, name, size=size)


def draw(d):
    P = d.P
    # DVC
    d.box(1, 55.5, 17, 5, P["gray"], ec=P["accent"])
    d.text(9.5, 58, "DVC  object 0", size=9, weight="bold")
    # 루트 DET
    d.box(1, 30.5, 22, 19.5, P["gray"])
    d.text(12, 47.6, "Device (루트)\nelement 0", size=8.6, weight="bold")
    for i, (ddi, name, color) in enumerate(ROOT_CHIPS):
        chip(d, 3, 40.2 - i * 4.6, 18, 4.0, ddi, name, color)
    d.arrow(9.5, 55.4, 9.5, 50.1, color=P["dim"], lw=1.3)

    # 루트 -> 자식 버스
    bus_x = 26.5
    d.arrow(23, 40, bus_x, 40, color=P["dim"], lw=1.3, style="-")
    d.arrow(bus_x, 57.2, bus_x, 30.5, color=P["dim"], lw=1.3, style="-")

    # Connector
    d.box(30, 53.6, 40, 7.2, P["gray"])
    d.text(36, 57.2, "Connector\nelement 1", size=8, weight="bold")
    for i, (ddi, name, color) in enumerate(CNN_CHIPS):
        chip(d, 42.5 + i * 9.0, 54.6, 8.4, 5.2, ddi, name, color, size=6.2)
    d.arrow(bus_x, 57.2, 30, 57.2, color=P["dim"], lw=1.3)

    # Bin
    d.box(30, 45.2, 40, 6.0, P["gray"])
    d.text(50, 48.2, "Bin  element 2  (제품 용기, 선택 속성)", size=8, weight="bold")
    d.arrow(bus_x, 48.2, 30, 48.2, color=P["dim"], lw=1.3)

    # Boom (Function)
    bx, by, bw, bh = 30, 18.6, 68.5, 21.0
    d.box(bx, by, bw, bh, P["gray"], ec=P["accent"], lw=1.8)
    d.text(bx + 1.5, by + bh - 1.8, "Function (붐)  element 3", size=8.8,
           weight="bold", ha="left")
    cw, ch, cg = 9.0, 6.6, 0.55
    for r, row in enumerate(BOOM_ROWS):
        for i, (ddi, name, color) in enumerate(row):
            chip(d, bx + 1.2 + i * (cw + cg), by + bh - 11.0 - r * (ch + 1.2), cw, ch,
                 ddi, name, color, size=6.2)
    d.arrow(bus_x, 30.5, 30, 30.5, color=P["dim"], lw=1.3)

    # Sections
    sx0, sw, sg, sy, sh = 30, 9.0, 0.92, 2.2, 9.6
    d.arrow(bx + bw / 2, by, bx + bw / 2, 14.0, color=P["dim"], lw=1.3, style="-")
    d.arrow(sx0 + sw / 2, 14.0, sx0 + 6 * (sw + sg) + sw / 2, 14.0, color=P["dim"], lw=1.3, style="-")
    for i in range(7):
        x = sx0 + i * (sw + sg)
        d.arrow(x + sw / 2, 14.0, x + sw / 2, sy + sh, color=P["dim"], lw=1.3)
        d.box(x, sy, sw, sh, P["gray"])
        d.text(x + sw / 2, sy + sh - 1.9, f"Section {i + 1}\nel. {11 + i}", size=6.6, weight="bold")
        for j, ddi in enumerate(("70", "135")):
            cx = x + 0.45 + j * 4.15
            d.box(cx, sy + 0.6, 3.9, 2.8, P[PROP], lw=0.9)
            d.text(cx + 1.95, sy + 2.0, ddi, size=6.6, weight="bold")

    # 범례
    for i, (color, label) in enumerate(((SET, "DPD settable"), (RO, "DPD 읽기 전용"),
                                        (PROP, "DPT (property)"))):
        y = 22.5 - i * 4.2
        d.box(2, y - 1.0, 3.2, 2.0, P[color], lw=1.0)
        d.text(6.2, y, label, size=7.6, ha="left", color=P["dim"])


diagram("20-sc-ddop-tree", draw, w=13, h=8.0, xmax=100, ymax=61.5)
