"""CH11 §12 ETP.CM 메시지 5종의 바이트 배치 (light/dark PNG)."""
from _common import diagram

X0, CW, GAP = 16, 10.0, 0.5          # Byte 1 시작 x, 바이트 칸 폭, 칸 사이
ROWS = [
    ("ETP.CM_RTS", "20", [((2, 5), "보낼 바이트 수 (4 byte, LSB 먼저)", "green")]),
    ("ETP.CM_CTS", "21", [((2, 2), "패킷 수\n0~255", "brown"),
                          ((3, 5), "다음 패킷 번호 (3 byte)", "green")]),
    ("ETP.CM_DPO", "22", [((2, 2), "패킷 수\n1~255", "brown"),
                          ((3, 5), "오프셋 (3 byte)\n= CTS 다음 번호 - 1", "green")]),
    ("ETP.CM_EOMA", "23", [((2, 5), "받은 바이트 수 (4 byte)", "green")]),
    ("ETP.Conn_Abort", "255", [((2, 2), "사유", "brown"),
                               ((3, 5), "FF FF FF", "gray")]),
]


def bx(i):
    return X0 + (i - 1) * (CW + GAP)


def draw(d):
    P = d.P
    top, rh, rgap = 39, 6.2, 1.6

    for i in range(1, 9):
        d.text(bx(i) + CW / 2, top + 2.2, f"Byte {i}", size=9, weight="bold")

    for r, (name, cb, fields) in enumerate(ROWS):
        y = top - (r + 1) * (rh + rgap) + rgap
        d.text(X0 - 1.5, y + rh / 2, name, size=9.3, ha="right")
        d.box(bx(1), y, CW, rh, P["blue"])
        d.text(bx(1) + CW / 2, y + rh / 2, cb, size=10, weight="bold")
        for (a, b), label, color in fields:
            x0, x1 = bx(a), bx(b) + CW
            d.box(x0, y, x1 - x0, rh, P[color])
            d.text((x0 + x1) / 2, y + rh / 2, label, size=8.6)
        d.box(bx(6), y, bx(8) + CW - bx(6), rh, P["purple"])
        d.text((bx(6) + bx(8) + CW) / 2, y + rh / 2, "운반하는 PGN (3 byte)", size=8.6)


diagram("11-etp-cm-layout", draw, w=12, h=4.7, xmax=100, ymax=43)
