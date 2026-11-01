"""CH47 §5 Peer Control의 세 역할: TC가 source와 user를 짝짓고 source가 user에 직접 보낸다 (light/dark PNG)."""
from _common import diagram


def node(d, x, y, w, h, color, label, size=9.5):
    d.box(x, y, w, h, d.P[color])
    d.text(x + w / 2, y + h / 2, label, size=size)


def draw(d):
    P = d.P
    node(d, 38, 32, 24, 9, "blue", "TC\n짝짓기와 기록", size=10)
    node(d, 4, 3, 30, 12.5, "brown",
         "setpoint value source\n작물 센서 CF\nDDI 1: control source")
    node(d, 66, 3, 30, 12.5, "green",
         "setpoint value user\n살포기 rate controller\nDDI 1: settable")

    d.arrow(41, 31.8, 20, 15.8, color=P["accent"])
    d.text(27.5, 25.5, "Assign Transmitter\n(mode 3)", size=8.5, ha="right")
    d.arrow(26, 15.8, 45, 31.8, color=P["orange"], ls="--")
    d.text(35.5, 21, "Transmitter Ack\n(mode 5)", size=8.5, ha="left")

    d.arrow(59, 31.8, 80, 15.8, color=P["accent"])
    d.text(72.5, 25.5, "Assign Receiver\n(mode 0)", size=8.5, ha="left")
    d.arrow(74, 15.8, 55, 31.8, color=P["orange"], ls="--")
    d.text(64.5, 21, "Receiver Ack\n(mode 2)", size=8.5, ha="right")

    d.arrow(34.3, 9.2, 65.7, 9.2, color=P["violet"], lw=2.0)
    d.text(50, 12.0, "Value command (3): setpoint 직접 전달", size=8.5)
    d.text(50, 6.3, "1초 주기 + 변화 시(최대 5 Hz)", size=8.5, color=P["dim"])


diagram("47-peer-control-roles", draw, w=12, h=5.2, xmax=100, ymax=43)
