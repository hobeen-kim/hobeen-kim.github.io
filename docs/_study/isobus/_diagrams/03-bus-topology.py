"""CH3 4절 선형 버스 토폴로지: 주선, 짧은 스텁, 양 끝 120Ω 종단 저항 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    ax = d.ax
    by = 27
    ax.plot([13, 87], [by, by], color=P["accent"], lw=3.4, zorder=0.5)
    d.text(50, by + 3, "주선 (Backbone)", size=10, color=P["dim"])
    for x in (7, 93):
        d.box(x - 6, by - 4.4, 12, 8.8, P["brown"], ec=P["orange"], lw=1.7)
        d.text(x, by + 1.6, "종단 저항", size=9.5)
        d.text(x, by - 1.9, "120Ω", size=10, weight="bold")
    ecus = [(22, "ECU A\n엔진"), (36, "ECU B\n변속기"), (50, "ECU C\n계기판"),
            (64, "ECU D\nABS"), (78, "ECU E\n작업기")]
    for x, name in ecus:
        ax.plot([x, x], [15, by], color=P["edge"], lw=1.8, zorder=0.5)
        d.text(x + 0.9, 20.6, "스텁\n≤0.3m", size=8.6, color=P["dim"], ha="left")
        d.box(x - 6, 6.5, 12, 8.5, P["blue"])
        d.text(x, 10.75, name, size=10)


diagram("03-bus-topology", draw, w=12, h=4.3, xmax=100, ymax=36)
