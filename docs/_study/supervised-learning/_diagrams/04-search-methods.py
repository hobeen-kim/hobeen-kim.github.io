"""CH4 탐색 전략 — grid vs random vs bayesian 샘플 분포 (light/dark PNG).

두 하이퍼파라미터 공간에서 각 전략이 어디를 시험하는지 점으로 보여준다.
별(★)은 진짜 최적점. grid는 격자에 갇히고, random은 넓게 흩뿌리며,
bayesian은 좋은 영역으로 점점 몰린다.
"""
import numpy as np
from _common import diagram


def draw(d):
    P = d.P
    fig = d.fig
    d.ax.axis("off")

    rng = np.random.default_rng(7)
    opt = (0.68, 0.72)  # 진짜 최적점

    def style(ax, title):
        ax.set_facecolor(P["bg"])
        for s in ax.spines.values():
            s.set_color(P["edge"])
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel("하이퍼파라미터 1", fontsize=8.5, color=P["dim"])
        ax.set_ylabel("하이퍼파라미터 2", fontsize=8.5, color=P["dim"])
        ax.set_title(title, fontsize=11, color=P["text"], pad=8)
        ax.scatter([opt[0]], [opt[1]], marker="*", s=260,
                   color=P["accent"], zorder=5, edgecolor=P["bg"], linewidth=0.6)

    w, h, b = 0.265, 0.62, 0.055
    axes = [fig.add_axes([0.045 + i * (w + b), 0.16, w, h]) for i in range(3)]

    # grid
    g = np.linspace(0.12, 0.88, 5)
    gx, gy = np.meshgrid(g, g)
    axes[0].scatter(gx, gy, s=34, color=P["blue"], edgecolor=P["edge"],
                    linewidth=0.5, zorder=3)
    style(axes[0], "Grid Search")

    # random
    rx, ry = rng.uniform(0.05, 0.95, 25), rng.uniform(0.05, 0.95, 25)
    axes[1].scatter(rx, ry, s=34, color=P["green"], edgecolor=P["edge"],
                    linewidth=0.5, zorder=3)
    style(axes[1], "Random Search")

    # bayesian: 초반 탐색 후 최적점 근방으로 수렴
    bx = np.concatenate([rng.uniform(0.05, 0.95, 8),
                         rng.normal(opt[0], 0.09, 17)])
    by = np.concatenate([rng.uniform(0.05, 0.95, 8),
                         rng.normal(opt[1], 0.09, 17)])
    bx, by = np.clip(bx, 0.03, 0.97), np.clip(by, 0.03, 0.97)
    axes[2].scatter(bx, by, s=34, color=P["purple"], edgecolor=P["edge"],
                    linewidth=0.5, zorder=3)
    style(axes[2], "Bayesian (Optuna 등)")


diagram("04-search-methods", draw, w=12, h=4.4)
