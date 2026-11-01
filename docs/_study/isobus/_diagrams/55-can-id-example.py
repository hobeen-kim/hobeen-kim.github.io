"""CH55 §1 로그 1행(0CF00400)과 2행(18EAFFFE)의 29비트 CAN ID 필드 분해 (light/dark PNG)."""
from _common import diagram

# (name, width)
FIELDS = [("우선순위", 10), ("R", 6), ("DP", 6), ("PF", 20), ("PS", 20), ("SA", 20)]

ROWS = [
    # (y, id text, row label, [(bits, value)], ps role, ps color key, conclusion)
    (31.0, "0x0CF00400", "로그 1행",
     [("011", "3"), ("0", "0"), ("0", "0"), ("1111 0000", "F0"), ("0000 0100", "04"), ("0000 0000", "00")],
     "PGN의 일부", "green",
     "PF F0 ≥ F0  →  PS가 PGN에 들어감  →  PGN 0xF004 (EEC1), 방송, SA 0x00 (엔진)"),
    (9.0, "0x18EAFFFE", "로그 2행",
     [("110", "6"), ("0", "0"), ("0", "0"), ("1110 1010", "EA"), ("1111 1111", "FF"), ("1111 1110", "FE")],
     "받는 주소 (DA)", "purple",
     "PF EA < F0  →  PS가 받는 주소  →  PGN 0xEA00 (Request), DA 0xFF (전체), SA 0xFE (주소 없음)"),
]


def draw(d):
    P = d.P
    x0 = 17.0
    for y, cid, label, vals, ps_role, ps_key, concl in ROWS:
        d.text(1.5, y + 6.2, cid, size=11, weight="bold", ha="left")
        d.text(1.5, y + 3.4, label, size=9, ha="left", color=P["dim"])
        x = x0
        for (name, w), (bits, val) in zip(FIELDS, vals):
            if name == "PF":
                fc = P["brown"]
            elif name == "PS":
                fc = P[ps_key]
            elif name == "SA":
                fc = P["blue"]
            else:
                fc = P["gray"]
            d.box(x + 0.3, y + 1.5, w - 0.6, 7.5, fc)
            d.text(x + w / 2, y + 10.3, name, size=9, color=P["dim"])
            d.text(x + w / 2, y + 6.6, bits, size=9.5)
            d.text(x + w / 2, y + 3.5, val, size=10, weight="bold")
            if name == "PS":
                d.text(x + w / 2, y - 0.4, ps_role, size=8.5, color=P["accent"], weight="bold")
            x += w
        d.text(x0, y - 3.4, concl, size=9.5, ha="left", color=P["orange"])


diagram("55-can-id-example", draw, w=12, h=5.4, xmax=100, ymax=46)
