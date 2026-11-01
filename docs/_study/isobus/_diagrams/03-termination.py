"""CH3 5절 종단 저항: CAN_H와 CAN_L 사이 양 끝 120Ω 두 개가 병렬로 보여 합성 60Ω (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    ax = d.ax
    yh, yl = 27, 12
    ax.plot([14, 86], [yh, yh], color=P["accent"], lw=3, zorder=0.5)
    ax.plot([14, 86], [yl, yl], color=P["orange"], lw=3, zorder=0.5)
    d.text(88, yh, "CAN_H", size=10.5, weight="bold", color=P["accent"], ha="left")
    d.text(88, yl, "CAN_L", size=10.5, weight="bold", color=P["orange"], ha="left")

    for x in (14, 86):
        ax.plot([x, x], [yl, yh], color=P["edge"], lw=1.6, zorder=0.5)
        d.box(x - 4, 15.8, 8, 7.4, P["brown"], ec=P["orange"], lw=1.7)
        d.text(x, 19.5, "120Ω", size=10, weight="bold")

    for x in (36, 50, 64):
        ax.plot([x, x], [yl, yh], color=P["edge"], lw=1.4, zorder=0.5)
        d.box(x - 5, 16.2, 10, 6.6, P["blue"])
        d.text(x, 19.5, "ECU", size=10)

    ax.plot([14, 14, 86, 86], [7.5, 5.5, 5.5, 7.5], color=P["dim"], lw=1.2)
    d.text(50, 3, "양 끝 120Ω 병렬 = 합성 저항 60Ω", size=10.5, color=P["text"])


diagram("03-termination", draw, w=12, h=3.85, xmax=100, ymax=32)
