"""CH3 2절 Wired-AND로 중재 결과를 판단하는 흐름: 보낸 값과 버스 값을 비교 (light/dark PNG)."""
from matplotlib.patches import Polygon

from _common import diagram


def draw(d):
    P = d.P
    ax = d.ax

    # 송신 노드 두 개
    for x, label in ((28, "노드 A가 비트 전송"), (72, "노드 B가 비트 전송")):
        d.box(x - 14, 44, 28, 7, P["blue"])
        d.text(x, 47.5, label, size=11)
    d.arrow(28, 44, 46, 34.4, color=P["accent"])
    d.arrow(72, 44, 54, 34.4, color=P["accent"])

    # 판단 마름모
    cx, cy, hw, hh = 50, 29.5, 12, 6.8
    ax.add_patch(Polygon([(cx, cy + hh), (cx + hw, cy), (cx, cy - hh), (cx - hw, cy)],
                         closed=True, facecolor=P["purple"], edgecolor=P["edge"],
                         linewidth=1.4, zorder=2))
    d.text(cx, cy, "버스 읽기", size=11, weight="bold")

    # 두 갈래
    d.arrow(cx - hw, cy, 23, 15.4, color=P["accent"])
    d.text(20, 25.5, "내가 보낸 값 = 버스 값", size=10, color=P["accent"])
    d.box(9, 8, 28, 7.4, P["green"])
    d.text(23, 11.7, "계속 전송", size=11, weight="bold")

    d.arrow(cx + hw, cy, 77, 15.4, color=P["orange"])
    d.text(81, 25.5, "Recessive를 보냈는데\n버스는 Dominant", size=10, color=P["orange"])
    d.box(61, 6.5, 32, 8.9, P["brown"])
    d.text(77, 11, "중재 패배\n전송 중단 후 재시도", size=10.5, weight="bold")


diagram("03-wired-and-flow", draw, w=11, h=5.8, xmax=100, ymax=53)
