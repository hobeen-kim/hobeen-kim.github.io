"""CH08 §5 J1939 버스 토폴로지 예시: 종단 저항과 ECU 다섯 개 (light/dark PNG)."""
from _common import diagram

NODES = [
    ("엔진 ECU\nSA=0x00", "blue"),
    ("변속기 ECU\nSA=0x03", "blue"),
    ("계기판\nSA=0x17", "green"),
    ("캡 디스플레이\nSA=0x28", "green"),
    ("진단 도구\nSA=0xF9", "purple"),
]


def draw(d):
    P = d.P
    bus_y = 10

    d.box(1, bus_y - 4, 10, 8, P["brown"])
    d.text(6, bus_y, "종단 저항\n120Ω", size=8.8)
    d.box(89, bus_y - 4, 10, 8, P["brown"])
    d.text(94, bus_y, "종단 저항\n120Ω", size=8.8)

    d.ax.plot([11, 89], [bus_y + 0.7, bus_y + 0.7], color=P["accent"], lw=2.4)
    d.ax.plot([11, 89], [bus_y - 0.7, bus_y - 0.7], color=P["accent"], lw=2.4)
    d.text(50, bus_y - 3.4, "J1939 버스 (CAN_H / CAN_L 두 선)", size=8.6, color=P["dim"])

    w, top_y, hh = 13, 21, 9
    xs = [15, 30, 45, 60, 75]
    for x, (label, color) in zip(xs, NODES):
        d.box(x, top_y, w, hh, P[color])
        d.text(x + w / 2, top_y + hh / 2, label, size=9.0)
        d.ax.plot([x + w / 2, x + w / 2], [top_y, bus_y + 0.7], color=P["edge"], lw=1.6)


diagram("08-bus-topology", draw, w=10.5, h=3.4, xmax=100, ymax=32)
