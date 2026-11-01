"""20장 1절: 트랙터 버스와 작업기 버스, 둘을 잇는 TECU, IBBC 너머의 작업기 (light/dark PNG)."""
from _common import diagram

T_BUS, I_BUS = 35, 15


def bus(d, x1, x2, y):
    d.ax.plot([x1, x2], [y, y], color=d.P["accent"], lw=2.8, zorder=2)


def unit(d, x, y, w, h, label, fc, ec=None, lw=1.4, size=9.5):
    d.box(x, y, w, h, fc, ec=ec, lw=lw)
    d.text(x + w / 2, y + h / 2, label, size=size)


def draw(d):
    P = d.P
    d.box(2, 2, 58, 52, P["gray"], ec=P["edge"])
    d.text(5, 50.5, "트랙터", size=11, weight="bold", ha="left")
    d.box(67, 2, 31, 52, P["gray"], ec=P["edge"])
    d.text(70, 50.5, "작업기", size=11, weight="bold", ha="left")

    for x, label in ((6, "엔진 ECU"), (23, "변속기 ECU"), (40, "히치 ECU")):
        unit(d, x, 40, 14, 6.5, label, P["brown"])
        d.ax.plot([x + 7, x + 7], [40, T_BUS], color=P["edge"], lw=1.4, zorder=2)
        d.ax.plot([x + 7], [T_BUS], marker="o", markersize=6, color=P["text"], zorder=6)
    bus(d, 5, 57, T_BUS)
    d.text(5, 32.6, "트랙터 버스", size=9.5, weight="bold", color=P["accent"], ha="left")

    unit(d, 29, 21.5, 18, 8, "TECU\n(게이트웨이 NIU)", P["purple"], ec=P["accent"], lw=1.8, size=10)
    d.ax.plot([38, 38], [T_BUS, 29.5], color=P["edge"], lw=1.4, zorder=2)
    d.ax.plot([38, 38], [21.5, I_BUS], color=P["edge"], lw=1.4, zorder=2)
    d.ax.plot([38], [T_BUS], marker="o", markersize=6, color=P["text"], zorder=6)
    d.ax.plot([38], [I_BUS], marker="o", markersize=6, color=P["text"], zorder=6)

    bus(d, 5, 96, I_BUS)
    d.text(5, 17.4, "작업기 버스 (250 kbit/s CAN)", size=9.5, weight="bold", color=P["accent"],
           ha="left")

    for x, label in ((8, "VT\n(운전석)"), (43, "TC\n(운전석)")):
        unit(d, x, 4, 15, 7, label, P["blue"])
        d.ax.plot([x + 7.5, x + 7.5], [11, I_BUS], color=P["edge"], lw=1.4, zorder=2)
        d.ax.plot([x + 7.5], [I_BUS], marker="o", markersize=6, color=P["text"], zorder=6)

    unit(d, 58, 11.5, 10.5, 7, "IBBC\n9핀 커넥터", P["chip"], ec=P["accent"], lw=1.8, size=9)
    d.ax.patches[-1].set_zorder(3)

    unit(d, 74, 24, 22, 7, "Working Set Master", P["green"])
    d.ax.plot([85, 85], [24, I_BUS], color=P["edge"], lw=1.4, zorder=2)
    d.ax.plot([85], [I_BUS], marker="o", markersize=6, color=P["text"], zorder=6)
    for x, label in ((70, "Working Set\nMember 1"), (84, "Working Set\nMember 2")):
        unit(d, x, 4, 13, 7.5, label, P["green"], size=9)
        d.ax.plot([x + 6.5, x + 6.5], [11.5, I_BUS], color=P["edge"], lw=1.4, zorder=2)
        d.ax.plot([x + 6.5], [I_BUS], marker="o", markersize=6, color=P["text"], zorder=6)
    d.text(71, 17.4, "버스 연장", size=9, color=P["dim"], ha="left")


diagram("20-two-bus-topology", draw, w=13, h=6.8, xmax=100, ymax=56)
