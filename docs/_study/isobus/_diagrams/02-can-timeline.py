"""CH2 1절 CAN 기술 발전사: 1986~2012 주요 사건을 실제 연도 간격으로 배치 (light/dark PNG)."""
from _common import diagram

EVENTS = [
    (1986, "Bosch가\nCAN 프로토콜 발표", 1),
    (1991, "Mercedes-Benz S-Class에\n최초 양산 적용", -1),
    (1993, "ISO 11898로\n국제 표준화", 1),
    (2003, "J1939 기반 ISOBUS\n(ISO 11783) 완성", -1),
    (2012, "Bosch가\nCAN FD 규격 발표", 1),
]


def x_of(year):
    return 9 + (year - 1984) / 30 * 82


def draw(d):
    P = d.P
    ax = d.ax
    ly = 17
    ax.plot([4, 96], [ly, ly], color=P["edge"], lw=2.2, zorder=0.5)
    for year, label, side in EVENTS:
        x = x_of(year)
        ax.plot([x, x], [ly, ly + side * 3.2], color=P["edge"], lw=1.2, zorder=0.5)
        ax.plot([x], [ly], marker="o", ms=10, color=P["accent"], zorder=3)
        d.text(x, ly + side * 4.8, str(year), size=11.5, weight="bold", color=P["accent"])
        d.text(x, ly + side * 10.2, label, size=10)


diagram("02-can-timeline", draw, w=12, h=4.1, xmax=100, ymax=34)
