"""CH45 §6 Setpoint·Measurement와 제어 오차: 처방 맵, 유량 센서, 작업기 ECU (light/dark PNG)."""
from _common import diagram


def node(d, x, y, w, h, color, label, size=10):
    d.box(x, y, w, h, d.P[color])
    d.text(x + w / 2, y + h / 2, label, size=size)


def draw(d):
    P = d.P
    node(d, 3, 33, 17, 8, "gray", "처방 맵")
    node(d, 3, 6, 17, 8, "gray", "유량 센서")
    node(d, 33, 32, 24, 10, "blue", "Setpoint\nDDI 1 = 200 L/ha")
    node(d, 33, 5, 24, 10, "brown", "Measurement\nDDI 2 = 198 L/ha")
    node(d, 35, 19, 20, 8, "purple", "제어 오차\n200 - 198 = 2 L/ha", size=9.5)
    node(d, 77, 18.5, 20, 9, "green", "작업기 ECU")

    d.arrow(20.2, 37, 32.8, 37, color=P["accent"])
    d.text(26.5, 39.3, "목표값 조회", size=9, color=P["dim"])
    d.arrow(20.2, 10, 32.8, 10, color=P["accent"])
    d.text(26.5, 12.3, "실제값 측정", size=9, color=P["dim"])

    d.arrow(57.2, 37, 77, 26.5, color=P["accent"])
    d.text(70, 35, "Value Command", size=9, color=P["dim"])
    d.arrow(77, 20.5, 57.2, 10, color=P["orange"], ls="--")
    d.text(71.5, 12.2, "Process Data Value", size=9, color=P["dim"])

    d.arrow(45, 31.8, 45, 27.2, color=P["edge"], style="-", lw=1.4)
    d.arrow(45, 15.2, 45, 18.8, color=P["edge"], style="-", lw=1.4)


diagram("45-setpoint-measurement", draw, w=12, h=5.6, xmax=100, ymax=47)
