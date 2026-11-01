"""CH7 4절 같은 버스에 붙은 세 종류 노드: FD Active, FD Tolerant, Classic CAN (light/dark PNG)."""
from _common import diagram

BUS_Y = 30
NODES = [
    (18, "CAN FD Active 노드", "CAN FD 프레임 송수신 가능", "green", "accent"),
    (50, "CAN FD Tolerant 노드", "CAN FD 프레임을 무시\n(에러 없이 수신)", "blue", "edge"),
    (82, "Classic CAN 노드", "CAN FD 프레임을\n에러로 인식", "brown", "orange"),
]
BW, BH = 27, 13


def draw(d):
    P = d.P
    ax = d.ax

    ax.plot([4, 96], [BUS_Y, BUS_Y], color=P["accent"], lw=3.0, zorder=3)
    d.text(50, BUS_Y + 3.2, "CAN 버스 (물리 계층 공유)", size=10, weight="bold")

    for x, title, desc, fc, ec in NODES:
        ax.plot([x, x], [BUS_Y, 4 + BH], color=P["edge"], lw=1.6, zorder=2)
        d.box(x - BW / 2, 4, BW, BH, P[fc], ec=P[ec], lw=1.8)
        d.text(x, 4 + BH * 0.72, title, size=9.8, weight="bold")
        d.text(x, 4 + BH * 0.32, desc, size=8.6)


diagram("07-fd-node-types", draw, w=11, h=3.6, xmax=100, ymax=36)
