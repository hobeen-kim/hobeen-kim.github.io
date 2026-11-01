"""CH6 5절 Bus Off 복구 전략 선택: 일반 시스템은 자동 복구, 안전 필수 시스템은 수동 복구 (light/dark PNG)."""
from matplotlib.patches import Polygon

from _common import diagram


def diamond(d, cx, cy, w, h, s, fc):
    P = d.P
    d.ax.add_patch(Polygon([(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)],
                           closed=True, facecolor=fc, edgecolor=P["edge"], linewidth=1.4, zorder=2))
    d.text(cx, cy, s, size=9.2, weight="bold")


def node(d, cx, cy, w, h, s, fc, size=9.2):
    d.box(cx - w / 2, cy - h / 2, w, h, fc)
    d.text(cx, cy, s, size=size)


def draw(d):
    P = d.P
    LX, RX = 26, 72

    node(d, 50, 78, 22, 6, "Bus Off 발생", P["purple"], size=9.6)
    d.arrow(50, 74.6, 50, 70.2, color=P["edge"], lw=1.4)
    diamond(d, 50, 64, 30, 11, "시스템 안전 요구사항", P["chip"])

    d.arrow(35.5, 64, LX, 54.6, color=P["accent"], lw=1.5)
    d.text(28, 61.2, "일반 시스템", size=8.6, color=P["accent"])
    d.arrow(64.5, 64, RX, 54.6, color=P["orange"], lw=1.5)
    d.text(74, 61.2, "안전 필수 시스템", size=8.6, color=P["orange"])

    node(d, LX, 51, 24, 6, "자동 복구 활성화", P["green"])
    d.arrow(LX, 47.6, LX, 41.6, color=P["edge"], lw=1.4)
    node(d, LX, 36, 30, 9, "11개 연속 recessive를 128번 감지한 뒤\n자동으로 Error Active 복귀", P["green"],
         size=8.6)

    node(d, RX, 51, 24, 6, "수동 복구 선택", P["brown"])
    d.arrow(RX, 47.6, RX, 43.2, color=P["edge"], lw=1.4)
    node(d, RX, 39, 28, 7, "애플리케이션이\n오류 원인 분석", P["brown"], size=8.8)
    d.arrow(RX, 35.2, RX, 30.6, color=P["edge"], lw=1.4)
    diamond(d, RX, 25, 24, 10, "원인 해결됨?", P["chip"])

    d.arrow(RX - 12, 25, 55, 14.4, color=P["accent"], lw=1.4)
    d.text(55.0, 21.5, "예", size=8.8, color=P["accent"])
    d.arrow(RX + 12, 25, 89, 14.4, color=P["orange"], lw=1.4)
    d.text(90.5, 22.0, "아니오", size=8.8, color=P["orange"])
    node(d, 55, 10, 26, 8, "소프트웨어에서\n수동 복구 명령", P["green"], size=8.8)
    node(d, 87, 10, 24, 8, "유지보수 요청 또는\n안전 모드 유지", P["gray"], size=8.8)


diagram("06-busoff-recovery-choice", draw, w=11, h=7.4, xmax=100, ymax=84)
