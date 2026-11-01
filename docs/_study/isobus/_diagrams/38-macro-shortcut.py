"""38장: 매크로 없이 버튼을 처리할 때와 매크로로 처리할 때의 메시지 흐름 비교 (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P
    OP, VT, EC = 12, 50, 86
    TOP = 50

    for x, name, col in [(OP, "운전자", P["gray"]),
                         (VT, "VT", P["blue"]),
                         (EC, "작업기\n(Working Set)", P["green"])]:
        d.box(x - 9, TOP, 18, 6, col, lw=1.4)
        d.text(x, TOP + 3, name, size=10.5, weight="bold")
        d.ax.plot([x, x], [1.5, TOP], color=P["edge"], ls=(0, (4, 3)), lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-"):
        d.arrow(x1, y, x2, y, color=color, ls=ls, lw=1.7)
        d.text((x1 + x2) / 2, y + 1.3, label, size=9, color=color)

    d.text(1.5, 46, "매크로 없이", size=10.5, weight="bold", ha="left", color=P["orange"])
    hop(OP, VT, 43, "버튼 누름", P["dim"])
    hop(VT, EC, 39, "Button Activation", P["accent"])
    d.text(EC + 1.5, 35.6, "작업기가 판단", size=8.8, color=P["dim"], ha="left")
    hop(EC, VT, 32, "Change Active Mask (명령)", P["accent"])
    hop(VT, EC, 28.5, "응답", P["dim"], ls="--")
    d.box(VT - 8, 24.0, 16, 3.2, P["purple"], lw=1.1)
    d.text(VT, 25.6, "화면 전환", size=9, weight="bold")

    d.ax.plot([1, 99], [21.5, 21.5], color=P["edge"], ls=(0, (2, 3)), lw=1.0)

    d.text(1.5, 18.5, "매크로로", size=10.5, weight="bold", ha="left", color=P["violet"])
    hop(OP, VT, 15.5, "버튼 누름", P["dim"])
    d.box(VT - 12, 8.4, 24, 5.2, P["purple"], lw=1.1)
    d.text(VT, 12.1, "매크로 50 실행", size=9, weight="bold")
    d.text(VT, 9.8, "Change Active Mask", size=8.6)
    d.box(VT - 8, 3.0, 16, 3.2, P["purple"], lw=1.1)
    d.text(VT, 4.6, "화면 전환", size=9, weight="bold")
    d.arrow(VT, 8.2, VT, 6.4, color=P["violet"], lw=1.4)
    hop(VT + 12.3, EC, 11.0, "Button Activation (알림)", P["dim"], ls=":")

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.2, label="명령·메시지"),
        Line2D([0], [0], color=P["dim"], lw=2.2, ls="--", label="응답"),
        Line2D([0], [0], color=P["dim"], lw=2.2, ls=":", label="알림"),
    ], loc="lower left", anchor=(0.14, 0.005), fontsize=8.5)


diagram("38-macro-shortcut", draw, w=12.5, h=7.4, xmax=100, ymax=57)
