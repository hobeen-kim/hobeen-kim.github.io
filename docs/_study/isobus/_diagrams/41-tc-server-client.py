"""41장 TC-Server(트랙터)와 TC-Client(작업기)의 위치와 주고받는 값 (light/dark PNG)."""
from _common import diagram


def group(d, x, y, w, h, label):
    P = d.P
    d.box(x, y, w, h, P["chip"], lw=1.2)
    d.text(x + 2, y + h - 2.6, label, size=11.5, weight="bold", ha="left")


def node(d, x, y, w, h, title, sub, color):
    d.box(x, y, w, h, d.P[color])
    if sub:
        d.text(x + w / 2, y + h / 2 + 1.5, title, size=11, weight="bold")
        d.text(x + w / 2, y + h / 2 - 1.7, sub, size=8.8)
    else:
        d.text(x + w / 2, y + h / 2, title, size=10.5, weight="bold")


def draw(d):
    P = d.P
    group(d, 2, 2, 35, 44, "트랙터")
    group(d, 63, 2, 35, 44, "작업기")

    node(d, 7.5, 31, 24, 7.5, "GNSS 수신기", "", "gray")
    node(d, 7.5, 15, 24, 10, "TC-Server", "(ISO 11783-10)", "green")

    node(d, 68.5, 15, 24, 10, "TC-Client", "(작업기 ECU)", "blue")
    node(d, 68.5, 31, 24, 7.5, "밸브 / 액추에이터", "", "gray")
    node(d, 68.5, 4.5, 24, 7, "유량 센서", "", "gray")

    d.arrow(19.5, 30.8, 19.5, 25.2)
    d.text(21, 28, "GPS 위치", size=9, color=P["accent"], ha="left")

    d.arrow(31.7, 22.5, 68.3, 22.5)
    d.text(50, 27.3, "Value Command", size=9.5, color=P["accent"], weight="bold")
    d.text(50, 25, "(Setpoint)", size=8.8)

    d.arrow(68.3, 17.5, 31.7, 17.5)
    d.text(50, 14.8, "Process Data Value", size=9.5, color=P["accent"], weight="bold")
    d.text(50, 12.5, "(Measurement)", size=8.8)

    d.arrow(80.5, 25.2, 80.5, 30.8)
    d.arrow(80.5, 11.7, 80.5, 14.8)


diagram("41-tc-server-client", draw, w=12, h=6, xmax=100, ymax=48)
