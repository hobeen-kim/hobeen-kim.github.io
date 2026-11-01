"""27장 2절 진단 체계가 지원해야 하는 네트워크 구성 예 (light/dark PNG)."""
from _common import diagram

TRACTOR_BUS_Y = 47
ISO_BUS_Y = 17


def wire(d, xs, ys, lw=1.3, color=None):
    d.ax.plot(xs, ys, color=color or d.P["edge"], lw=lw, zorder=2)


def bus(d, x1, x2, y, label, color):
    d.ax.plot([x1, x2], [y, y], color=color, lw=3.2, zorder=2, solid_capstyle="round")
    d.text(x1 + 0.8, y + 1.7, label, size=8.6, color=color, ha="left", weight="bold")


def draw(d):
    P = d.P
    d.box(21, 9, 56, 52, P["chip"], ec=P["accent"], lw=1.5)
    d.text(23, 58.3, "제품 1: 트랙터 또는 자주식 작업기", size=9.4, weight="bold",
           color=P["accent"], ha="left")

    bus(d, 30, 75, TRACTOR_BUS_Y, "tractor bus (트랙터 버스)", P["violet"])
    bus(d, 30, 109, ISO_BUS_Y, "ISO 11783 bus", P["orange"])

    d.box(23, 27, 10, 11, P["purple"])
    d.text(28, 32.5, "진단\n커넥터", size=8.8, weight="bold")
    wire(d, [28, 28, 30], [38, TRACTOR_BUS_Y, TRACTOR_BUS_Y], color=P["violet"], lw=2.2)
    wire(d, [28, 28, 30], [27, ISO_BUS_Y, ISO_BUS_Y], color=P["orange"], lw=2.2)

    d.box(2, 41, 14, 8, P["gray"])
    d.text(9, 45, "진단 툴", size=9)
    d.box(2, 28, 14, 8, P["gray"])
    d.text(9, 32, "툴 인터페이스", size=8.6)
    d.arrow(9, 41, 9, 36.4, color=P["edge"], lw=1.3, style="-")
    d.arrow(16, 32, 22.6, 32.5, color=P["edge"], lw=1.3, style="-")

    for x, label in ((47, "ECU 1"), (58, "ECU 2"), (69, "ECU n")):
        d.box(x - 4.5, 50, 9, 6, P["gray"])
        d.text(x, 53, label, size=8.6)
        wire(d, [x, x], [50, TRACTOR_BUS_Y])

    d.box(36, 26, 13, 12, P["blue"])
    d.text(42.5, 32, "tractor\nECU CF", size=8.8)
    wire(d, [42.5, 42.5], [38, TRACTOR_BUS_Y])
    wire(d, [42.5, 42.5], [26, ISO_BUS_Y])

    d.box(53, 23, 21, 16, P["blue"])
    d.text(63.5, 35.5, "OEM 설치 ECU", size=8.8, weight="bold")
    for x, label in ((58, "CF1"), (69, "CF2")):
        d.box(x - 3.8, 25.5, 7.6, 6, P["chip"])
        d.text(x, 28.5, label, size=8.4)
    wire(d, [63.5, 63.5], [23, ISO_BUS_Y])

    d.box(80, 26, 16, 13, P["green"])
    d.text(88, 35.6, "제품 2:\n애프터마켓 ECU", size=8.4, weight="bold")
    d.box(84, 27.5, 8, 4.6, P["chip"])
    d.text(88, 29.8, "CF n", size=8.4)
    wire(d, [88, 88], [26, ISO_BUS_Y])

    d.box(97.6, ISO_BUS_Y - 2.4, 2.6, 4.8, P["gray"], r=0.005)
    d.text(98.9, ISO_BUS_Y - 5.6, "작업기 연결\n커넥터", size=8, color=P["dim"])
    d.box(101.5, 22, 9, 8, P["brown"])
    d.text(106, 26, "작업기\nCF", size=8.6)
    wire(d, [106, 106], [22, ISO_BUS_Y])


diagram("27-diagnostic-network", draw, w=13, h=7.2, xmax=111, ymax=63)
