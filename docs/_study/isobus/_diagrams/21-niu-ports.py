"""CH21 §1 전형적 NIU 배치와 포트 번호, TECU의 port pair 방향 (light/dark PNG)."""
from _common import diagram


def line(d, x1, y1, x2, y2, lw=1.2, color=None):
    d.ax.plot([x1, x2], [y1, y2], color=color or d.P["edge"], lw=lw, zorder=2)


def dot(d, x, y):
    d.ax.plot([x], [y], marker="o", markersize=5, color=d.P["text"], zorder=6)


def port(d, x, y, label):
    d.text(x, y + 1.4, label, size=8.5, weight="bold", color=d.P["orange"])


def draw(d):
    P = d.P
    tbus, ibus = 19, 55

    d.ax.plot([tbus, tbus], [6, 45], color=P["accent"], lw=2.6, zorder=2)
    d.ax.plot([ibus, ibus], [4, 45], color=P["accent"], lw=2.6, zorder=2)
    d.text(tbus, 47.5, "트랙터 네트워크", size=9.5, weight="bold", color=P["accent"])
    d.text(ibus, 47.5, "작업기 네트워크", size=9.5, weight="bold", color=P["accent"])

    for i, name in enumerate(["엔진", "변속기", "브레이크", "히치 컨트롤러"]):
        y = 38 - i * 8.5
        d.box(1.5, y - 2.5, 12.5, 5, P["blue"])
        d.text(7.75, y, name, size=8.8)
        line(d, 14, y, tbus, y)
        dot(d, tbus, y)

    d.box(26, 20, 21, 10, P["purple"], ec=P["accent"], lw=1.6)
    d.text(36.5, 26.2, "TECU", size=10.5, weight="bold")
    d.text(36.5, 23.2, "트랙터 ECU", size=8.5, color=P["dim"])
    line(d, tbus, 25, 26, 25)
    line(d, 47, 25, ibus, 25)
    dot(d, tbus, 25)
    dot(d, ibus, 25)
    port(d, 22.5, 25, "P2")
    port(d, 51, 25, "P1")

    d.arrow(28, 15.5, 45, 15.5, color=P["accent"])
    d.text(36.5, 17.3, "port pair 0x21 (From 2, To 1)", size=8.3)
    d.text(36.5, 13.6, "트랙터 → 작업기", size=8.3, color=P["dim"])
    d.arrow(45, 8.5, 28, 8.5, color=P["violet"])
    d.text(36.5, 10.3, "port pair 0x12 (From 1, To 2)", size=8.3)
    d.text(36.5, 6.6, "작업기 → 트랙터", size=8.3, color=P["dim"])

    for y, name in ((40, "VT"), (32.5, "TC"), (19.5, "작업기 ECU")):
        d.box(60, y - 2.5, 14, 5, P["green"])
        d.text(67, y, name, size=8.8)
        line(d, ibus, y, 60, y)
        dot(d, ibus, y)

    d.box(60, 5, 14, 10, P["brown"], ec=P["accent"], lw=1.6)
    d.text(67, 11.2, "작업기 NIU", size=9.5, weight="bold")
    d.text(67, 8.2, "router·gateway", size=8, color=P["dim"])
    line(d, ibus, 10, 60, 10)
    dot(d, ibus, 10)
    port(d, 57.5, 10, "P1")

    line(d, 74, 12.5, 79, 12.5)
    port(d, 76.5, 12.5, "P2")
    d.box(79, 9.8, 19.5, 5.4, P["gray"])
    d.text(88.75, 12.5, "서브네트워크\n(조명 컨트롤러 등)", size=8)

    line(d, 74, 7, 79, 7)
    port(d, 76.5, 7, "P3")
    d.box(79, 3.6, 19.5, 5.0, P["gray"])
    d.text(88.75, 6.1, "다른 규격 네트워크", size=8)


diagram("21-niu-ports", draw, w=13, h=6.3, xmax=100, ymax=50)
