"""CH22 §5 키 오프 시간 축: 5F·4F 요청과 PWR·ECU_PWR이 꺼지는 시각 (light/dark PNG)."""
from _common import diagram

T0, T1 = -1.5, 11.5
X0, X1 = 22.0, 98.0


def x(t):
    return X0 + (t - T0) * (X1 - X0) / (T1 - T0)


def bar(d, t1, t2, y, fc, label, h=4.0):
    d.box(x(t1), y - h / 2, x(t2) - x(t1), h, fc, r=0.01)
    d.text((x(t1) + x(t2)) / 2, y, label, size=8.6)


def off_line(d, t1, t2, y, label):
    P = d.P
    d.ax.plot([x(t1), x(t2)], [y, y], color=P["edge"], lw=1.4, ls="--", zorder=2)
    d.text(x(t1) + 1.0, y + 1.6, label, size=8.2, color=P["dim"], ha="left")


def span(d, t1, t2, y, label):
    P = d.P
    d.arrow(x(t1), y, x(t2), y, color=P["orange"], lw=1.3, style="<|-|>")
    d.text((x(t1) + x(t2)) / 2, y + 1.5, label, size=8.4, weight="bold", color=P["orange"])


def draw(d):
    P = d.P
    lanes = {"key": 38, "mp": 29, "pwr": 19.5, "ecu": 10}

    labels = [
        ("key", "키 스위치 상태", "TECU, 100 ms마다"),
        ("mp", "Maintain power", "CF, 1 s에 1회 이상"),
        ("pwr", "PWR", "액추에이터 전원"),
        ("ecu", "ECU_PWR", "ECU 전원"),
    ]
    for key, name, sub in labels:
        y = lanes[key]
        d.text(1.5, y + 1.2, name, size=9.5, weight="bold", ha="left")
        d.text(1.5, y - 1.6, sub, size=8, color=P["dim"], ha="left")

    d.ax.plot([x(0), x(0)], [4.5, 43], color=P["accent"], lw=1.2, ls=":", zorder=1)
    d.text(x(0), 44.3, "키 오프 (t = 0)", size=8.8, weight="bold", color=P["accent"])
    d.ax.plot([x(9.5), x(9.5)], [4.5, 41], color=P["edge"], lw=1.0, ls=":", zorder=1)
    d.text(x(9.5), 42.3, "마지막 off 송신", size=8.4, color=P["dim"])

    bar(d, T0, 0, lanes["key"], P["green"], "not off (01)")
    bar(d, 0, 9.5, lanes["key"], P["brown"], "off (00)")

    for t in (0.5, 1.5, 2.5, 3.5, 4.5):
        d.box(x(t) - 2.2, lanes["mp"] - 2, 4.4, 4, P["blue"], r=0.01)
        d.text(x(t), lanes["mp"], "5F", size=8.6, weight="bold")
    for t in (5.5, 6.5, 7.5):
        d.box(x(t) - 2.2, lanes["mp"] - 2, 4.4, 4, P["purple"], r=0.01)
        d.text(x(t), lanes["mp"], "4F", size=8.6, weight="bold")

    bar(d, T0, 6.5, lanes["pwr"], P["green"], "켜짐")
    off_line(d, 6.5, T1, lanes["pwr"], "꺼짐")
    span(d, 4.5, 6.5, lanes["pwr"] + 4.2, "2 s")

    bar(d, T0, 9.5, lanes["ecu"], P["green"], "켜짐")
    off_line(d, 9.5, T1, lanes["ecu"], "꺼짐 (100 ms 안)")
    span(d, 7.5, 9.5, lanes["ecu"] + 4.2, "2 s")

    ay = 3.2
    d.ax.plot([x(T0), x(T1)], [ay, ay], color=P["edge"], lw=1.2, zorder=2)
    for t in range(0, 12):
        d.ax.plot([x(t), x(t)], [ay - 0.6, ay + 0.6], color=P["edge"], lw=1.0, zorder=2)
        d.text(x(t), ay - 1.9, f"{t}", size=8, color=P["dim"])
    d.text(x(T1) - 0.3, ay - 1.9, "s", size=8, color=P["dim"], ha="right")


diagram("22-keyoff-timeline", draw, w=13, h=5.8, xmax=100, ymax=46)
