"""CH09 §8 Acknowledgement(PGN 59392) 데이터 8바이트: 기본형과 확장 식별자형 (light/dark PNG)."""
from _common import diagram

X0, CW, GAP = 17, 9.7, 0.5


def bx(i):
    return X0 + (i - 1) * (CW + GAP)


ROWS = [
    ("기본형", "0~3", [((2, 2), "GF 값\n또는 FF", "brown"), ((3, 4), "FF FF", "gray")]),
    ("확장 1바이트", "128~131", [((2, 2), "확장 ID", "green"), ((3, 4), "FF FF", "gray")]),
    ("확장 2바이트", "144~147", [((2, 3), "확장 ID (LSB 먼저)", "green"), ((4, 4), "FF", "gray")]),
    ("확장 3바이트", "160~163", [((2, 4), "확장 ID (LSB 먼저)", "green")]),
]


def draw(d):
    P = d.P
    top, rh, rgap = 30, 5.6, 1.5
    for i in range(1, 9):
        d.text(bx(i) + CW / 2, top + 2, f"Byte {i}", size=9, weight="bold")
    for r, (name, cb, fields) in enumerate(ROWS):
        y = top - (r + 1) * (rh + rgap) + rgap
        d.text(X0 - 1.5, y + rh / 2, name, size=9.3, ha="right")
        d.box(bx(1), y, CW, rh, P["blue"])
        d.text(bx(1) + CW / 2, y + rh / 2, f"control\n{cb}", size=8.6)
        for (a, b), label, color in fields:
            x0, x1 = bx(a), bx(b) + CW
            d.box(x0, y, x1 - x0, rh, P[color])
            d.text((x0 + x1) / 2, y + rh / 2, label, size=8.6)
        d.box(bx(5), y, CW, rh, P["purple"])
        d.text(bx(5) + CW / 2, y + rh / 2, "응답받을\n주소", size=8.4)
        d.box(bx(6), y, bx(8) + CW - bx(6), rh, P["purple"])
        d.text((bx(6) + bx(8) + CW) / 2, y + rh / 2, "요청됐던 PGN (LSB 먼저)", size=8.6)


diagram("09-ack-layout", draw, w=12, h=3.4, xmax=100, ymax=33.5)
