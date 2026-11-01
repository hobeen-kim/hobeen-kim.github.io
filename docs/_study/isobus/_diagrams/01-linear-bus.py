"""CH1 4절 선형 버스: ECU A~D가 선로 하나에 붙고 양 끝에 120Ω 종단 저항 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    ax = d.ax
    by = 9
    ax.plot([13, 87], [by, by], color=P["accent"], lw=3.2, zorder=0.5)
    for x in (7, 93):
        d.box(x - 6, by - 4.2, 12, 8.4, P["brown"], ec=P["orange"], lw=1.7)
        d.text(x, by + 1.6, "종단 저항", size=9.5)
        d.text(x, by - 1.8, "120Ω", size=10, weight="bold")
    for x, name in ((25, "ECU A"), (41.7, "ECU B"), (58.3, "ECU C"), (75, "ECU D")):
        d.box(x - 6.5, 17, 13, 6.4, P["blue"])
        d.text(x, 20.2, name, size=10.5)
        ax.plot([x, x], [by, 17], color=P["edge"], lw=1.6, zorder=0.5)
    d.text(50, by - 4, "버스 선로", size=9.5, color=P["dim"])


diagram("01-linear-bus", draw, w=12, h=3.2, xmax=100, ymax=27)
