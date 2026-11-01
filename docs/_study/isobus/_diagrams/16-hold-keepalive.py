"""16장 3절: hold(CTS(0))를 Th마다 반복하면 연결이 유지되고, 반복이 끊기면 T4 만료로 Abort되는 시간축 (light/dark PNG)."""
from _common import diagram

X0, X1, T_MAX = 20, 96, 2.2


def tx(t):
    return X0 + (X1 - X0) * t / T_MAX


def draw(d):
    P = d.P

    def lane(y, label):
        d.text(2, y, label, size=9.5, ha="left")
        d.ax.plot([tx(0) - 1, tx(T_MAX)], [y, y], color=P["edge"], lw=1.4)

    def cts(t, y, label="CTS(0)", color=None):
        c = color or P["orange"]
        d.ax.plot([tx(t), tx(t)], [y, y + 3], color=c, lw=2.0)
        d.text(tx(t), y + 4.6, label, size=8.6, color=c)

    def window(t0, t1, y, label, cut=None):
        d.box(tx(t0), y - 1.0, tx(t1) - tx(t0), 2.0, P["brown"], ec=P["orange"], lw=1.0, r=0.01)
        d.text(tx(t0) + 0.8, y - 3.2, label, size=8.4, color=P["orange"], ha="left")

    # 정상 hold
    ya = 33
    lane(ya, "정상 hold\n(Th마다 반복)")
    for t in (0, 0.5, 1.0, 1.5):
        cts(t, ya)
    cts(1.8, ya, "CTS(n)\n전송 재개", color=P["accent"])
    window(0, 1.05, ya - 3.4, "송신 측 T4 1.05 s")
    d.ax.plot([tx(0.5), tx(1.05)], [ya - 7.6, ya - 7.6], color=P["violet"], lw=1.2)
    for t in (0.5, 1.05):
        d.ax.plot([tx(t), tx(t)], [ya - 8.2, ya - 7.0], color=P["violet"], lw=1.2)
    d.text(tx(0.775), ya - 9.6, "여유 0.55 s", size=8.4, color=P["violet"])
    d.text(tx(1.32), ya - 3.4, "CTS(0)마다 T4를 다시 잰다", size=8.4,
           color=P["dim"], ha="left")

    # 반복이 끊김
    yb = 14
    lane(yb, "반복이 끊김")
    for t in (0, 0.5):
        cts(t, yb)
    d.ax.plot([tx(1.0), tx(1.0)], [yb, yb + 3], color=P["dim"], lw=1.4, ls=(0, (2, 2)))
    d.text(tx(1.0), yb + 4.6, "CTS(0) 없음", size=8.6, color=P["dim"])
    window(0.5, 1.55, yb - 3.4, "송신 측 T4 1.05 s")
    xe = tx(1.55)
    for dx, dy in ((1, 1), (1, -1)):
        d.ax.plot([xe - dx, xe + dx], [yb - dy, yb + dy], color=P["orange"], lw=2.2)
    d.text(xe + 1.8, yb + 3.6, "T4 만료: 송신 측이\nAbort(사유 3)를 보냄", size=8.6,
           color=P["orange"], ha="left")

    # 시간축
    ya_axis = 3.6
    d.ax.plot([tx(0), tx(2.0)], [ya_axis, ya_axis], color=P["dim"], lw=1.0)
    for t in (0, 0.5, 1.0, 1.5, 2.0):
        d.ax.plot([tx(t), tx(t)], [ya_axis, ya_axis + 0.8], color=P["dim"], lw=1.0)
        d.text(tx(t), ya_axis - 2.0, f"{t:g} s", size=8.2, color=P["dim"])


diagram("16-hold-keepalive", draw, w=12, h=5.0, xmax=100, ymax=44)
