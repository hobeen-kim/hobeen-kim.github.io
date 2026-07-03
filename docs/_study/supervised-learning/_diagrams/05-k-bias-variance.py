"""CH5 k와 편향-분산 — 작은 k는 과적합, 큰 k는 과평활 (light/dark PNG).

같은 데이터에 k=1과 k=25로 kNN 결정 경계를 그린다. k=1은 경계가
들쭉날쭉(고분산), k가 크면 매끈(고편향)해진다.
"""
import numpy as np
from _common import diagram


def draw(d):
    P = d.P
    fig = d.fig
    d.ax.axis("off")

    rng = np.random.default_rng(1)
    a = rng.normal([3.5, 6.3], 1.5, (30, 2))
    b = rng.normal([6.5, 4.0], 1.5, (30, 2))
    X = np.vstack([a, b])
    y = np.array([0] * 30 + [1] * 30)

    gx, gy = np.meshgrid(np.linspace(0, 10, 160), np.linspace(0, 10, 160))
    grid = np.c_[gx.ravel(), gy.ravel()]

    def knn_predict(k):
        out = np.empty(len(grid), dtype=int)
        for i, p in enumerate(grid):
            dd = np.sum((X - p) ** 2, axis=1)
            nn = np.argsort(dd)[:k]
            out[i] = int(y[nn].mean() >= 0.5)
        return out.reshape(gx.shape)

    from matplotlib.colors import ListedColormap
    cmap = ListedColormap([P["blue"], P["orange"]])

    def panel(rect, k, title):
        ax = fig.add_axes(rect)
        ax.set_facecolor(P["bg"])
        for s in ax.spines.values():
            s.set_color(P["edge"])
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_title(title, fontsize=10.5, color=P["text"], pad=8)
        Z = knn_predict(k)
        ax.contourf(gx, gy, Z, levels=[-0.5, 0.5, 1.5], cmap=cmap, alpha=0.35)
        ax.scatter(a[:, 0], a[:, 1], s=32, color=P["blue"],
                   edgecolor=P["edge"], linewidth=0.5, zorder=3)
        ax.scatter(b[:, 0], b[:, 1], s=32, color=P["orange"],
                   edgecolor=P["edge"], linewidth=0.5, zorder=3)

    panel([0.05, 0.08, 0.42, 0.82], 1, "k=1 — 들쭉날쭉 (고분산·과적합)")
    panel([0.55, 0.08, 0.42, 0.82], 25, "k=25 — 매끈 (고편향·과평활)")


diagram("05-k-bias-variance", draw, w=12, h=5.4, ymax=50)
