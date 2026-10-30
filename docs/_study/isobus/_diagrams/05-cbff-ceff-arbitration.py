"""CH05 §7 CBFF(P6, SA 0x00)와 CEFF(0x18FEEE00)의 비트 단위 중재 (light/dark PNG)."""
from _common import diagram

BITS = list(range(2, 15))           # 프레임 비트 2~14
CBFF_NAMES = ["P3", "P2", "P1", "SA8", "SA7", "SA6", "SA5", "SA4", "SA3", "SA2", "SA1", "RTR", "IDE"]
CEFF_NAMES = ["P3", "P2", "P1", "EDP", "DP", "PF8", "PF7", "PF6", "PF5", "PF4", "PF3", "SRR", "IDE"]
CBFF_VAL = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
CEFF_VAL = [1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
DECIDE = 7                          # 처음 갈리는 프레임 비트
X0, CW = 22, 5.6


def draw(d):
    P = d.P
    rows = [(25, "CBFF\nP6, SA 0x00", CBFF_NAMES, CBFF_VAL, True),
            (12, "CEFF\n0x18FEEE00", CEFF_NAMES, CEFF_VAL, False)]
    for i, b in enumerate(BITS):
        d.text(X0 + i * CW + CW / 2, 35.5, str(b), size=8.4, color=P["dim"])
    d.text(X0 - 2, 35.5, "프레임 비트", size=8.4, color=P["dim"], ha="right")
    for y, title, names, vals, winner in rows:
        d.text(2, y + 2.6, title, size=9, ha="left")
        for i, (b, n, v) in enumerate(zip(BITS, names, vals)):
            lost = (not winner) and b > DECIDE
            fc = P["gray"] if lost else (P["blue"] if v == 0 else P["chip"])
            ec = P["accent"] if b == DECIDE else None
            d.box(X0 + i * CW, y, CW - 0.4, 5.2, fc, ec=ec, lw=2.2 if ec else 1.2)
            d.text(X0 + i * CW + (CW - 0.4) / 2, y + 2.6, str(v), size=10,
                   color=P["dim"] if lost else P["text"], weight="bold")
            d.text(X0 + i * CW + (CW - 0.4) / 2, y + (6.6 if winner else -1.5), n,
                   size=7.2, color=P["dim"])
    # 버스(wired-AND)
    y = 2
    d.text(2, y + 2.3, "버스", size=9, ha="left")
    for i, (a, c, b) in enumerate(zip(CBFF_VAL, CEFF_VAL, BITS)):
        v = min(a, c) if b <= DECIDE else a
        d.box(X0 + i * CW, y, CW - 0.4, 4.6, P["green"] if v == 0 else P["chip"])
        d.text(X0 + i * CW + (CW - 0.4) / 2, y + 2.3, str(v), size=9.6)
    xd = X0 + (DECIDE - 2) * CW + (CW - 0.4) / 2
    d.text(xd + 4.0, 21.8, "CEFF가 1을 보냈는데 0을 읽음", size=8, color=P["accent"], ha="left")


diagram("05-cbff-ceff-arbitration", draw, w=12, h=4.2, xmax=100, ymax=38)
