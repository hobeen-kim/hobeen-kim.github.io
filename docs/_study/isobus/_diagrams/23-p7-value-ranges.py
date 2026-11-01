"""CH23 1바이트·2바이트 원시값의 유효·예약·오류·사용 불가 구역 (light/dark PNG)."""
from _common import diagram

# (x0, x1, color key, 1-byte label, 2-byte label, meaning)
ZONES = [
    (13, 57, "green", "0x00~0xFA\n0~250", "0x0000~0xFAFF\n0~64 255", "유효값"),
    (57, 67, "gray", "0xFB\n251", "0xFBxx", "파라미터별"),
    (67, 77, "gray", "0xFC~0xFD\n252~253", "0xFC00~\n0xFDFF", "예약"),
    (77, 87, "brown", "0xFE\n254", "0xFExx", "오류"),
    (87, 97, "purple", "0xFF\n255", "0xFFxx", "값 없음"),
]


def draw(d):
    P = d.P
    y1, y2, h = 31, 13, 8
    for x0, x1, col, l1, l2, meaning in ZONES:
        d.box(x0, y1, x1 - x0, h, P[col], lw=1.1, r=0.005)
        d.text((x0 + x1) / 2, y1 + h / 2, l1, size=8.6)
        d.text((x0 + x1) / 2, y1 + h + 2.4, meaning, size=9.5, weight="bold")
        d.box(x0, y2, x1 - x0, h, P[col], lw=1.1, r=0.005)
        d.text((x0 + x1) / 2, y2 + h / 2, l2, size=8.6)
    d.text(1.5, y1 + h / 2, "1바이트", size=10.5, weight="bold", ha="left")
    d.text(1.5, y2 + h / 2 + 1.2, "2바이트", size=10.5, weight="bold", ha="left")
    d.text(1.5, y2 + h / 2 - 1.8, "최상위 바이트로", size=8, color=P["dim"], ha="left")

    # examples for 2-byte values (little endian bytes as received)
    ex = [
        (35, "C4 09 → 0x09C4", "유효 → 2.500 m/s", P["accent"]),
        (82, "12 FE → 0xFE12", "오류", P["orange"]),
        (92, "FF FF → 0xFFFF", "값 없음", P["violet"]),
    ]
    for x, raw, res, col in ex:
        d.arrow(x, 6.4, x, y2 - 0.3, color=col, lw=1.4)
    d.text(35, 3.6, "C4 09 → 0x09C4 (유효, 2.500 m/s)", size=9, color=P["accent"])
    d.text(70.5, 3.6, "12 FE → 0xFE12 (오류)", size=9, color=P["orange"])
    d.text(94.5, 3.6, "FF FF → 0xFFFF", size=9, color=P["violet"], ha="right")
    d.ax.plot([82, 74], [6.4, 5.2], color=P["orange"], lw=1.2)


diagram("23-p7-value-ranges", draw, w=12, h=5.4, xmax=100, ymax=45)
