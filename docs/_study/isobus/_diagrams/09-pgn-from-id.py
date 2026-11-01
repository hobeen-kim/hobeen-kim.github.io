"""CH09 §3 29비트 ID에서 PGN을 만드는 법: PDU2와 PDU1 비교 (light/dark PNG)."""
from _common import diagram

FIELDS = [  # (이름, x, 폭)
    ("Priority", 22, 11),
    ("EDP", 34, 6),
    ("DP", 41, 6),
    ("PF", 48, 15),
    ("PS", 64, 15),
    ("SA", 80, 15),
]

EXAMPLES = [
    # (y 기준, 왼쪽 라벨, 칸 값, PDU1 여부, PGN 칸 값, 결과)
    (31, "PDU2 예\n0x18FEEE00",
     {"Priority": "6", "EDP": "0", "DP": "0", "PF": "FE", "PS": "EE\n(GE)", "SA": "00"},
     False, ("0", "FE", "EE"), "= 0x0FEEE\n= 65262"),
    (3, "PDU1 예\n0x18EAFF26",
     {"Priority": "6", "EDP": "0", "DP": "0", "PF": "EA", "PS": "FF\n(DA)", "SA": "26"},
     True, ("0", "EA", "00"), "= 0x0EA00\n= 59904"),
]


def draw(d):
    P = d.P
    x_of = {n: (x, w) for n, x, w in FIELDS}

    for y0, left, vals, pdu1, pgn_vals, result in EXAMPLES:
        id_y, pgn_y, h = y0 + 15, y0 + 1, 8
        d.text(10, id_y + h / 2, left, size=9.2)
        d.text(10, pgn_y + h / 2, "PGN", size=9.6, color=P["accent"], weight="bold")
        for name, x, w in FIELDS:
            out = name in ("Priority", "SA") or (pdu1 and name == "PS")
            fc = P["gray"] if out else P["blue"]
            d.box(x, id_y, w, h, fc)
            label = f"{name}\n{vals[name]}" if name not in ("PS",) else f"PS {vals[name]}"
            d.text(x + w / 2, id_y + h / 2, label, size=8.4,
                   color=P["dim"] if out else P["text"])

        ex, ew = x_of["EDP"][0], x_of["DP"][0] + x_of["DP"][1] - x_of["EDP"][0]
        cells = [(ex, ew, pgn_vals[0], "EDP·DP"),
                 (x_of["PF"][0], x_of["PF"][1], pgn_vals[1], "PF"),
                 (x_of["PS"][0], x_of["PS"][1], pgn_vals[2], "PS" if not pdu1 else "00")]
        for x, w, v, _ in cells:
            d.box(x, pgn_y, w, h, P["green"])
            d.text(x + w / 2, pgn_y + h / 2, v, size=10.5, weight="bold")

        d.arrow(ex + ew / 2, id_y, ex + ew / 2, pgn_y + h + 0.3)
        d.arrow(x_of["PF"][0] + x_of["PF"][1] / 2, id_y,
                x_of["PF"][0] + x_of["PF"][1] / 2, pgn_y + h + 0.3)
        psx = x_of["PS"][0] + x_of["PS"][1] / 2
        if pdu1:
            d.text(psx + 9.2, (id_y + pgn_y + h) / 2, "주소라서\n00으로 바꿈", size=8.0,
                   color=P["orange"], ha="left")
            d.ax.plot([psx - 1.6, psx + 1.6], [(id_y + pgn_y + h) / 2 - 1.6, (id_y + pgn_y + h) / 2 + 1.6],
                      color=P["orange"], lw=1.6)
            d.ax.plot([psx - 1.6, psx + 1.6], [(id_y + pgn_y + h) / 2 + 1.6, (id_y + pgn_y + h) / 2 - 1.6],
                      color=P["orange"], lw=1.6)
        else:
            d.arrow(psx, id_y, psx, pgn_y + h + 0.3)
        d.text(87, pgn_y + h / 2, result, size=9.6, color=P["accent"])


diagram("09-pgn-from-id", draw, w=11.5, h=5.6, xmax=100, ymax=58)
