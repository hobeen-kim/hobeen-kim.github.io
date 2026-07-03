"""CH5 kNN 다수결 — 질의점 주변 k개 이웃의 투표 (light/dark PNG).

두 클래스의 점 산포 위에 질의점(★)을 놓고, 가장 가까운 k개를 원으로
감싸 다수결로 클래스를 정하는 과정을 보여준다.
"""
import numpy as np
from _common import diagram, Line2D
from matplotlib.patches import Circle


def draw(d):
    P = d.P
    fig = d.fig
    d.ax.axis("off")
    ax = fig.add_axes([0.04, 0.06, 0.92, 0.9])
    ax.set_facecolor(P["bg"])
    for s in ax.spines.values():
        s.set_color(P["edge"])
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    rng = np.random.default_rng(3)
    a = rng.normal([3.6, 6.2], 1.3, (14, 2))
    b = rng.normal([6.6, 4.0], 1.3, (14, 2))
    ax.scatter(a[:, 0], a[:, 1], s=70, color=P["blue"],
               edgecolor=P["edge"], linewidth=0.6, zorder=3, label="클래스 A")
    ax.scatter(b[:, 0], b[:, 1], s=70, color=P["orange"],
               edgecolor=P["edge"], linewidth=0.6, zorder=3, label="클래스 B")

    q = np.array([5.2, 5.4])
    pts = np.vstack([a, b])
    lab = np.array([0] * len(a) + [1] * len(b))
    dist = np.linalg.norm(pts - q, axis=1)
    idx = np.argsort(dist)[:5]
    r = dist[idx].max() * 1.05

    ax.add_patch(Circle(q, r, fill=False, linestyle="--",
                        edgecolor=P["accent"], linewidth=1.6, zorder=2))
    for i in idx:
        ax.plot([q[0], pts[i, 0]], [q[1], pts[i, 1]], color=P["accent"],
                linewidth=1.0, alpha=0.5, zorder=2)
    ax.scatter([q[0]], [q[1]], marker="*", s=360, color=P["accent"],
               edgecolor=P["bg"], linewidth=0.8, zorder=5)

    nA = int((lab[idx] == 0).sum())
    ax.text(q[0] + 0.4, q[1] + 2.1, f"k=5 → A {nA} : B {5-nA}  → A 예측",
            fontsize=9.5, color=P["text"], zorder=6, ha="left", va="bottom")

    handles = [
        Line2D([0], [0], marker="o", linestyle="none", markersize=9,
               markerfacecolor=P["blue"], markeredgecolor=P["edge"], label="클래스 A"),
        Line2D([0], [0], marker="o", linestyle="none", markersize=9,
               markerfacecolor=P["orange"], markeredgecolor=P["edge"], label="클래스 B"),
        Line2D([0], [0], marker="*", linestyle="none", markersize=15,
               markerfacecolor=P["accent"], markeredgecolor=P["bg"], label="질의점"),
    ]
    ax.legend(handles=handles, loc="lower right", fontsize=8.5,
              framealpha=0.0, labelcolor=P["dim"])


diagram("05-knn-decision", draw, w=7, h=6, ymax=50)
