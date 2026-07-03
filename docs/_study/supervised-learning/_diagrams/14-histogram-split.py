"""정렬 기반 정확 분할 vs 히스토그램 기반 분할 — 분할 후보 수 축소 (light/dark PNG)."""
import numpy as np
from _common import diagram


def draw(d):
    P = d.P
    ax = d.ax

    xs = np.array([3, 7, 9, 12, 15, 18, 21, 24, 28, 31, 34, 38,
                   41, 45, 49, 53, 58, 63, 69, 76])
    y0 = 34

    # ── 위: exact greedy — 정렬된 모든 값 사이가 후보 ──
    d.text(50, 46, "정렬 기반 정확 분할 (exact)", size=11, weight="bold")
    ax.scatter(xs, [y0] * len(xs), s=26, color=P["blue"],
               edgecolor=P["edge"], linewidth=0.8, zorder=4)
    for i in range(len(xs) - 1):
        mid = (xs[i] + xs[i + 1]) / 2
        ax.plot([mid, mid], [y0 - 2.4, y0 + 2.4], color=P["orange"],
                lw=0.9, alpha=0.8, zorder=3)
    d.text(50, 40.5, "값 사이 모든 지점이 분할 후보 (n-1개) — 정확하지만 느림",
           size=9, color=P["dim"])

    # ── 아래: histogram — bin 경계만 후보 ──
    d.text(50, 24, "히스토그램 기반 분할 (LightGBM·XGBoost hist)",
           size=11, weight="bold")
    edges = np.linspace(0, 80, 9)
    counts, _ = np.histogram(xs, bins=edges)
    base = 4
    for i, c in enumerate(counts):
        left = edges[i]
        w = edges[i + 1] - edges[i]
        h = c * 2.4
        d.box(left + 1, base, w - 2, max(h, 0.6), P["green"],
              ec=P["accent"], lw=1.2, r=0.02)
    for e in edges[1:-1]:
        ax.plot([e, e], [base - 1.2, base + 14], color=P["orange"],
                lw=1.4, alpha=0.9, zorder=3)
    d.text(50, 1.2, "값을 bin으로 묶어 bin 경계만 후보 (max_bin개) — 메모리·속도 대폭 개선",
           size=9, color=P["dim"])


diagram("14-histogram-split", draw, w=12, h=5.6, xmax=100, ymax=48)
