"""15장 1절: BAM(1:N 방송)과 CMDT(1:1 연결)에서 누가 누구와 주고받는지 비교 (light/dark PNG)."""
from _common import diagram

BUS_Y = 22
BOX_W, BOX_H = 12, 6.5


def ecu(d, x, y, label, fc, color=None):
    d.box(x, y, BOX_W, BOX_H, fc)
    d.text(x + BOX_W / 2, y + BOX_H / 2, label, size=9.5, color=color)


def stub(d, x, y0, y1, color):
    d.ax.plot([x, x], [y0, y1], color=color, lw=1.4, zorder=2)


def draw(d):
    P = d.P

    # BAM panel
    d.box(1, 2, 47.5, 46, P["chip"])
    d.text(3, 45, "BAM (1:N 방송)", size=10.5, weight="bold", ha="left")
    d.ax.plot([4, 46], [BUS_Y, BUS_Y], color=P["edge"], lw=3.2, zorder=2)
    d.text(4, BUS_Y + 1.6, "CAN 버스", size=8.5, color=P["dim"], ha="left")
    ecu(d, 18.75, 33, "송신 ECU", P["blue"])
    d.arrow(24.75, 32.8, 24.75, BUS_Y + 0.5, lw=2.0)
    d.text(26.2, 28.6, "TP.CM_BAM\nTP.DT × N", size=8.8, ha="left")
    for x, name in ((4.5, "수신 ECU A"), (18.75, "수신 ECU B"), (33, "수신 ECU C")):
        d.arrow(x + BOX_W / 2, BUS_Y - 0.5, x + BOX_W / 2, 13.7, lw=1.6)
        ecu(d, x, 7, name, P["green"])
    d.text(24.75, 4.2, "받는 쪽은 응답 없음 · DA 255(전체)", size=8.6, color=P["dim"])

    # CMDT panel
    d.box(51.5, 2, 47.5, 46, P["chip"])
    d.text(53.5, 45, "CMDT (1:1 연결)", size=10.5, weight="bold", ha="left")
    d.ax.plot([54.5, 96.5], [BUS_Y, BUS_Y], color=P["edge"], lw=3.2, zorder=2)
    d.text(54.5, BUS_Y + 1.6, "CAN 버스", size=8.5, color=P["dim"], ha="left")
    tx_x, rx_x = 55, 83.5
    ecu(d, tx_x, 33, "송신 ECU", P["blue"])
    ecu(d, rx_x, 33, "수신 ECU", P["green"])
    stub(d, tx_x + BOX_W / 2, 33, BUS_Y, P["edge"])
    stub(d, rx_x + BOX_W / 2, 33, BUS_Y, P["edge"])
    d.arrow(tx_x + BOX_W + 0.3, 37.9, rx_x - 0.3, 37.9, lw=1.8)
    d.text((tx_x + BOX_W + rx_x) / 2, 40.2, "RTS, TP.DT", size=8.6)
    d.arrow(rx_x - 0.3, 35.0, tx_x + BOX_W + 0.3, 35.0, lw=1.8, color=P["orange"])
    d.text((tx_x + BOX_W + rx_x) / 2, 31.9, "CTS, EndOfMsgACK", size=8.6, color=P["orange"])
    for x in (62.5, 76.5):
        stub(d, x + BOX_W / 2, BUS_Y, 13.5, P["edge"])
        ecu(d, x, 7, "다른 ECU", P["gray"], color=P["dim"])
    d.text(75.25, 4.2, "상대 하나만 대화 · DA = 상대 주소", size=8.6, color=P["dim"])


diagram("15-bam-vs-cmdt", draw, w=13, h=5.4, xmax=100, ymax=50)
