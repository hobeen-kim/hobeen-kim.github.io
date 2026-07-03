"""경사하강법 갱신 경로 — 배치는 매끄럽게, SGD는 지그재그로 최소점에 수렴 (light/dark PNG)."""
import numpy as np
from matplotlib.patches import Ellipse
from matplotlib.lines import Line2D
from _common import diagram


def draw(d):
    P = d.P
    ax = d.ax
    center = (7.0, 5.0)

    for r in (1, 2, 3, 4, 5):
        ax.add_patch(Ellipse(center, r * 2.2, r * 1.3, angle=20,
                     fill=False, edgecolor=P["edge"], lw=1.0, alpha=0.6))
    ax.scatter(*center, s=120, marker="*", color=P["accent"],
               edgecolor=P["text"], linewidth=0.8, zorder=6)
    d.text(center[0] + 0.2, center[1] - 0.9, "최소점", size=9.5,
           color=P["accent"], ha="left")

    start = (1.2, 8.6)
    # 배치 GD — 매끄러운 경로
    t = np.linspace(0, 1, 40)
    bx = start[0] + (center[0] - start[0]) * t
    by = start[1] + (center[1] - start[1]) * t + 0.6 * np.sin(t * np.pi)
    ax.plot(bx, by, color=P["orange"], lw=2.2, zorder=5)

    # SGD — 지그재그 경로
    pts = [(1.2, 1.4), (3.0, 3.4), (2.6, 5.2), (4.4, 4.0),
           (4.0, 6.0), (5.6, 4.4), (5.4, 6.0), (6.6, 4.9), (7.0, 5.0)]
    zx = [p[0] for p in pts]
    zy = [p[1] for p in pts]
    ax.plot(zx, zy, color=P["violet"], lw=1.8, marker="o", markersize=3.5,
            zorder=5)

    d.legend([
        Line2D([0], [0], color=P["orange"], lw=2.2, label="배치 GD (전체 데이터)"),
        Line2D([0], [0], color=P["violet"], lw=1.8, marker="o",
               markersize=4, label="SGD (한 샘플씩)"),
    ], loc="upper right", anchor=(0.99, 0.99), fontsize=9)


diagram("06-gd-paths", draw, w=8.5, h=5.2, xmax=14, ymax=10)
