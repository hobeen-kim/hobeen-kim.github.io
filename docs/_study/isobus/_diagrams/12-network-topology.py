"""CH12 §8 전형적 ISO 11783 토폴로지와 CF 주소: Part 1 Figure 3 재구성 (light/dark PNG)."""
from _common import diagram


def node(d, x, y):
    P = d.P
    d.ax.plot([x], [y], marker="o", markersize=6, color=P["text"], zorder=6)


def link(d, x1, x2, y):
    d.ax.plot([x1, x2], [y, y], color=d.P["edge"], lw=1.2, zorder=2)


def draw(d):
    P = d.P
    tbus, ibus = 34, 70

    # 트랙터(장치) 그룹: CF 6개가 트랙터 네트워크에 연결
    d.box(2, 16, 26, 58, P["gray"], ec=P["edge"])
    d.text(15, 70.5, "트랙터", size=10, weight="bold")
    for i, addr in enumerate(["35", "7", "30", "31", "3", "0"]):
        y = 61 - i * 8.6
        d.box(6, y, 18, 6, P["blue"])
        d.text(15, y + 3, f"CF 주소 {addr}", size=8.6)
        link(d, 24, tbus, y + 3)
        node(d, tbus, y + 3)

    # 버스 2개
    d.ax.plot([tbus, tbus], [6, 70], color=P["accent"], lw=2.6, zorder=2)
    d.ax.plot([ibus, ibus], [6, 79], color=P["accent"], lw=2.6, zorder=2)
    d.text(tbus, 74, "트랙터\n네트워크", size=9, weight="bold", color=P["accent"])
    d.text(ibus - 2, 79, "작업기 네트워크", size=9, weight="bold", color=P["accent"], ha="right")

    # TECU: 두 네트워크를 잇는다
    d.box(40, 3, 24, 11, P["brown"], ec=P["accent"], lw=1.6)
    d.text(52, 8.5, "TECU\nECU 7 / 주소 240", size=8.8, weight="bold")
    link(d, tbus, 40, 8.5)
    link(d, 64, ibus, 8.5)
    node(d, tbus, 8.5)
    node(d, ibus, 8.5)

    # VT + 관리 컴퓨터 게이트웨이: 한 ECU에 CF 2개
    d.box(76, 11, 50, 13, P["gray"], ec=P["edge"])
    d.text(101, 21.4, "ECU 6 (트랙터 탑재)", size=8.5, color=P["dim"])
    d.box(79, 13, 21, 6, P["purple"])
    d.text(89.5, 16, "VT 38", size=8.8)
    d.box(102, 13, 21, 6, P["purple"])
    d.text(112.5, 16, "관리 GW 37", size=8.8)
    link(d, ibus, 76, 17.5)
    node(d, ibus, 17.5)

    # TC
    d.box(76, 28, 30, 7, P["purple"])
    d.text(91, 31.5, "TC 247 (ECU 5)", size=8.8)
    link(d, ibus, 76, 31.5)
    node(d, ibus, 31.5)

    # 작업기 1: ECU 3개
    d.box(76, 39, 50, 15, P["gray"], ec=P["edge"])
    d.text(101, 51, "작업기 1", size=9, weight="bold")
    for i, a in enumerate(["a2", "a3", "a4"]):
        x = 79 + i * 15.5
        d.box(x, 41.5, 13, 6, P["green"])
        d.text(x + 6.5, 44.5, a, size=9)
    link(d, ibus, 76, 46.5)
    node(d, ibus, 46.5)

    # 작업기 2: ECU 1개
    d.box(76, 58, 50, 15, P["gray"], ec=P["edge"])
    d.text(101, 70, "작업기 2", size=9, weight="bold")
    d.box(79, 60.5, 13, 6, P["green"])
    d.text(85.5, 63.5, "a1", size=9)
    link(d, ibus, 76, 65.5)
    node(d, ibus, 65.5)

    d.text(110, 63.5, "a1~a4: self-configurable\n(128~237)", size=8, color=P["dim"])


diagram("12-network-topology", draw, w=13, h=8.2, xmax=130, ymax=82)
