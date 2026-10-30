"""CH22 §7 TimeLog 헤더가 정하는 바이너리 레코드 배치 (light/dark PNG)."""
from _common import diagram

RECORD0 = "C0 D9 09 02 08 42 48 1F 5A 16 08 BD B2 4B 04 40 77 1B 00 08 42 02 00 98 3A 00 00 01 E4 39 00 00".split()

FIELDS = [  # (offset, size, label, palette key)
    (0, 4, "TimeStart  ms\nu32", "blue"),
    (4, 2, "TimeStart\n날짜 u16", "blue"),
    (6, 4, "PositionNorth\ni32", "green"),
    (10, 4, "PositionEast\ni32", "green"),
    (14, 1, "Status\nu8", "green"),
    (15, 4, "GpsUtcTime\nu32", "green"),
    (19, 2, "GpsUtcDate\nu16", "green"),
    (21, 1, "#DLV\nu8", "brown"),
    (22, 1, "DLVn\nu8", "purple"),
    (23, 4, "PDV (DLV0)\ni32", "purple"),
    (27, 1, "DLVn\nu8", "purple"),
    (28, 4, "PDV (DLV1)\ni32", "purple"),
]

HEADER = [  # (x, w, text, palette key)
    (3, 17, '<TIM A="" D="4">', "blue"),
    (22, 31, '<PTN A="" B="" D="" H="" I=""/>', "green"),
    (55, 20.5, '<DLV A="0006" B="" .../>', "purple"),
    (77, 20.5, '<DLV A="0007" B="" .../>', "purple"),
]


def draw(d):
    P = d.P
    d.text(3, 45.3, "TLG00001.XML", size=10, weight="bold", ha="left")
    for x, w, text, key in HEADER:
        d.box(x, 38.2, w, 4.4, P[key])
        d.text(x + w / 2, 40.4, text, size=8.5)

    d.text(3, 33.6, "TLG00001.BIN  레코드 0", size=10, weight="bold", ha="left")
    cw, x0 = 4.0, 6.0
    rows = [(0, 22, 21.0), (22, 32, 6.0)]
    for start, end, y in rows:
        for off in range(start, end):
            x = x0 + (off - start) * cw
            key = next(k for o, s, _, k in FIELDS if o <= off < o + s)
            d.box(x + 0.15, y, cw - 0.3, 4.2, P[key], r=0.005)
            d.text(x + cw / 2, y + 2.1, RECORD0[off], size=8.5)
        for o, s, label, _ in FIELDS:
            if start <= o < end:
                x = x0 + (o - start) * cw
                d.text(x + s * cw / 2, y + 7.4, label, size=7.6)
                d.text(x + 0.3, y - 1.4, str(o), size=7.5, color=P["dim"], ha="left")


diagram("22-timelog-record", draw, w=14, h=6.6, xmax=100, ymax=48)
