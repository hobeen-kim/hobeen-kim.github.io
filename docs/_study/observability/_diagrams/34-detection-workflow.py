"""CH34 카디널리티 탐지 워크플로우 — 급증 알림부터 통제까지 (light/dark PNG)."""
from matplotlib.patches import Polygon
from _common import diagram, Line2D


def draw(d):
    P = d.P

    def diamond(cx, cy, w, h, fc):
        pts = [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)]
        d.ax.add_patch(Polygon(pts, closed=True, facecolor=fc,
                               edgecolor=P["orange"], linewidth=1.6, zorder=3))

    # A
    d.box(32, 49.5, 36, 5.5, P["blue"])
    d.text(50, 52.25, "head_series 급증 알림", size=10.5, weight="bold")
    # B
    diamond(50, 44.5, 34, 7.5, P["brown"])
    d.text(50, 44.5, "TSDB status page 확인", size=9.5)
    # C
    d.box(33, 33, 34, 5.5, P["gray"])
    d.text(50, 35.75, "seriesCountByMetricName\n상위 메트릭 확인", size=9)
    # D
    diamond(50, 26, 32, 8, P["brown"])
    d.text(50, 26, "오프라인 블록\n분석 필요?", size=9.5)
    # E / F
    d.box(8, 14, 32, 6.5, P["green"])
    d.text(24, 17.25, "promtool tsdb analyze", size=10)
    d.box(60, 14, 34, 6.5, P["green"])
    d.text(77, 18.0, "topk(count by (__name__))", size=9.3)
    d.text(77, 15.4, "PromQL로 실시간 확인", size=8.5, color=P["dim"])
    # G
    d.box(33, 6, 34, 5, P["gray"], ec=P["accent"], lw=1.4)
    d.text(50, 8.5, "원인 라벨 특정", size=10.5, weight="bold")
    # H
    d.box(28, 0.3, 44, 4.6, P["brown"], ec=P["orange"], lw=1.6)
    d.text(50, 2.6, "metric_relabel_configs로 통제", size=10.5, weight="bold", color=P["orange"])

    # arrows
    d.arrow(50, 49.5, 50, 48.25, color=P["accent"], lw=2.0)
    d.arrow(50, 40.75, 50, 38.5, color=P["accent"], lw=2.0)
    d.arrow(50, 33, 50, 30, color=P["accent"], lw=2.0)
    d.arrow(34, 26, 24, 20.5, color=P["accent"], lw=2.0)
    d.text(26, 24, "예", size=9, color=P["accent"], weight="bold")
    d.arrow(66, 26, 77, 20.5, color=P["accent"], lw=2.0)
    d.text(73, 24, "아니오", size=9, color=P["accent"], weight="bold")
    d.arrow(24, 14, 40, 11, color=P["accent"], lw=2.0)
    d.arrow(77, 14, 60, 11, color=P["accent"], lw=2.0)
    d.arrow(50, 6, 50, 4.9, color=P["orange"], lw=2.2)

    d.legend([
        Line2D([0], [0], marker="D", color="none", markerfacecolor=P["brown"],
               markeredgecolor=P["orange"], markersize=11, label="판단(분기) 노드"),
    ], loc="lower right", anchor=(0.995, 0.02))


diagram("34-detection-workflow", draw, w=13, h=8.4, ymax=57)
