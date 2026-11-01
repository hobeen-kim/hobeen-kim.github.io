"""CH31 연결 감시 시간 축: 1초 주기 메시지, 3초 타임아웃, Initiating 재수신 (light/dark PNG)."""
from _common import diagram

X0, SCALE = 22, 9.4


def tx(t):
    return X0 + t * SCALE


def draw(d):
    P = d.P
    lanes = {
        "status": (41, "VT Status\n(VT → 모두)"),
        "case1": (27, "Maintenance\n경우 1: 통신 끊김"),
        "case2": (13, "Maintenance\n경우 2: 재부팅"),
    }
    for y, label in lanes.values():
        d.text(1.5, y, label, size=9.2, weight="bold", ha="left")
        d.ax.plot([tx(0) - 1.5, tx(8) + 1.5], [y, y], color=P["edge"], lw=0.8, ls=":", zorder=1)

    def tick(t, y, color, tall=False):
        h = 3.2 if tall else 2.2
        d.arrow(tx(t), y - h, tx(t), y + h, color=color, lw=2.6 if tall else 2.0, style="-")

    y = lanes["status"][0]
    for t in range(9):
        tick(t, y, P["violet"])

    y = lanes["case1"][0]
    tick(0, y, P["orange"], tall=True)
    d.text(tx(0), y + 4.6, "Initiating=1", size=8, color=P["orange"])
    for t in (1, 2, 3):
        tick(t, y, P["accent"])
    d.ax.plot([tx(3), tx(3), tx(6), tx(6)], [y - 3.6, y - 4.4, y - 4.4, y - 3.6],
              color=P["dim"], lw=1.3)
    d.text((tx(3) + tx(6)) / 2, y - 6.0, "3초 동안 없음", size=8.6, color=P["dim"])
    d.text(tx(6), y, "×", size=16, color=P["orange"], weight="bold")
    d.text(tx(6) + 1.6, y + 3.4, "unexpected shutdown 판정", size=8.6, color=P["orange"], ha="left")

    y = lanes["case2"][0]
    tick(0, y, P["orange"], tall=True)
    d.text(tx(0), y + 4.6, "Initiating=1", size=8, color=P["orange"])
    for t in (1, 2, 3):
        tick(t, y, P["accent"])
    d.text(tx(3.5), y - 4.2, "재부팅", size=8.4, color=P["dim"])
    tick(4.0, y, P["orange"], tall=True)
    d.text(tx(4.0), y + 4.6, "Initiating=1 (두 번째)", size=8, color=P["orange"])
    d.text(tx(4.0) + 1.4, y - 0.1, "×", size=16, color=P["orange"], weight="bold", ha="left")
    d.text(tx(4.0) + 4.4, y - 4.2, "3초를 기다리지 않고 바로 판정", size=8.6, color=P["orange"], ha="left")

    axis_y = 3.0
    d.arrow(tx(0) - 1.5, axis_y, tx(8) + 3.0, axis_y, color=P["edge"], lw=1.1)
    for s in range(9):
        d.arrow(tx(s), axis_y - 0.5, tx(s), axis_y + 0.5, color=P["edge"], lw=1.1, style="-")
        d.text(tx(s), axis_y - 2.0, f"{s} s", size=8.4, color=P["dim"])


diagram("31-heartbeat-timeline", draw, w=13, h=5.6, xmax=100, ymax=48)
