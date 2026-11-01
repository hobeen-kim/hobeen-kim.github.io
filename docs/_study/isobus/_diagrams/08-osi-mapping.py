"""CH08 §6 ISO 11783가 쓰는 OSI 계층: Part 3 Figure 2 재구성 (light/dark PNG)."""
from _common import diagram

ROWS = [  # (y, 계층 이름)
    (52, "데이터"),
    (44, "7 응용"),
    (36.5, "6 표현"),
    (29.5, "5 세션"),
    (22, "4 전송"),
    (15, "3 네트워크"),
    (8, "2 데이터 링크"),
    (1, "1 물리"),
]
TX, RX, CW, RH = 28, 64, 28, 5.2


def draw(d):
    P = d.P
    for y, name in ROWS:
        d.box(2, y, 20, RH, P["gray"])
        d.text(12, y + RH / 2, name, size=9.2)

    d.text(TX + CW / 2, 60, "송신 CF", size=10, weight="bold")
    d.text(RX + CW / 2, 60, "수신 CF", size=10, weight="bold")

    for x in (TX, RX):
        d.box(x, 52, CW, RH, P["chip"])
        d.text(x + CW / 2, 52 + RH / 2, "Priority · PG · SP", size=9)
        d.box(x, 44, CW, RH, P["blue"])
        d.text(x + CW / 2, 44 + RH / 2, "PDU (P, EDP, DP, PF, PS, SA, 데이터)", size=8.2)
        d.box(x + 8, 22, CW - 8, RH, P["purple"])
        d.text(x + 8 + (CW - 8) / 2, 22 + RH / 2, "BAM · TP · ETP", size=9)
        d.box(x, 8, CW, RH, P["green"])
        d.text(x + CW / 2, 8 + RH / 2, "CEFF 데이터 프레임", size=9)

    d.box(TX, 1, RX + CW - TX, RH, P["brown"])
    d.text((TX + RX + CW) / 2, 1 + RH / 2, "ISO 11783-2 신호·네트워크 부품", size=9)

    # 송신: 아래로
    d.arrow(TX + CW / 2, 52, TX + CW / 2, 49.4)
    d.arrow(TX + 3, 44, TX + 3, 13.4)
    d.text(TX + 3.8, 35, "8바이트\n이하", size=8, color=P["dim"], ha="left")
    d.arrow(TX + 20, 44, TX + 20, 27.4)
    d.text(TX + 20.8, 35, "9바이트\n이상", size=8, color=P["dim"], ha="left")
    for k in (12, 18, 24):
        d.arrow(TX + k, 22, TX + k, 13.4)
    d.arrow(TX + CW / 2, 8, TX + CW / 2, 6.4)

    # 수신: 위로
    d.arrow(RX + CW / 2, 6.4, RX + CW / 2, 8)
    d.arrow(RX + 3, 13.4, RX + 3, 44)
    for k in (12, 18, 24):
        d.arrow(RX + k, 13.4, RX + k, 22)
    d.arrow(RX + 20, 27.4, RX + 20, 44)
    d.arrow(RX + CW / 2, 49.4, RX + CW / 2, 52)


diagram("08-osi-mapping", draw, w=11, h=6.4, xmax=96, ymax=63)
