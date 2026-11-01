"""39장: Working Set이 Alarm Mask를 띄우고, 운전자가 ACK하고, Working Set이 Data Mask로 경보를 내리는 메시지 순서 (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P
    WS, VT, OP = 14, 52, 88
    TOP = 63

    for x, name, col in [(WS, "작업기\n(Working Set)", P["green"]),
                         (VT, "VT", P["blue"]),
                         (OP, "운전자", P["gray"])]:
        d.box(x - 9, TOP, 18, 6, col, lw=1.4)
        d.text(x, TOP + 3, name, size=10, weight="bold")
        d.ax.plot([x, x], [1.5, TOP], color=P["edge"], ls=(0, (4, 3)), lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-"):
        d.arrow(x1, y, x2, y, color=color, ls=ls, lw=1.7)
        d.text((x1 + x2) / 2, y + 1.3, label, size=9, color=color)

    hop(WS, VT, 59, "Change Active Mask → Alarm Mask 0x0003", P["accent"])
    hop(VT, WS, 55, "Change Active Mask response", P["dim"], ls="--")
    d.box(VT - 13, 48.6, 26, 4, P["purple"], lw=1.1)
    d.text(VT, 50.6, "Alarm Mask 표시 + 경보음", size=9, weight="bold")
    hop(VT, WS, 45, "VT Status (전역): Alarm Mask 0x0003", P["violet"])
    d.text(VT + 2, 43.0, "버스 전체에 보냄", size=8.5, color=P["violet"], ha="left")
    hop(OP, VT, 39, "ACK 수단을 누름", P["dim"])
    hop(VT, WS, 35, "Soft Key Activation (key code 0)", P["accent"])
    d.box(WS - 12.5, 26.4, 25, 5.2, P["chip"], ec=P["orange"], lw=1.3)
    d.text(WS, 29.9, "ACK만으로는", size=8.8, color=P["orange"], weight="bold")
    d.text(WS, 27.7, "경보가 내려가지 않는다", size=8.8, color=P["orange"], weight="bold")
    hop(WS, VT, 21, "Change Active Mask → Data Mask", P["accent"])
    hop(VT, WS, 17, "Change Active Mask response", P["dim"], ls="--")
    d.box(VT - 13, 10.0, 26, 4, P["purple"], lw=1.1)
    d.text(VT, 12.0, "Data Mask 표시 (경보 내려감)", size=9, weight="bold")

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.2, label="명령·메시지"),
        Line2D([0], [0], color=P["dim"], lw=2.2, ls="--", label="응답"),
        Line2D([0], [0], color=P["violet"], lw=2.2, label="전역 브로드캐스트"),
    ], loc="lower right", anchor=(0.995, 0.005), fontsize=8.5)


diagram("39-alarm-sequence", draw, w=12.5, h=8.4, xmax=100, ymax=70)
