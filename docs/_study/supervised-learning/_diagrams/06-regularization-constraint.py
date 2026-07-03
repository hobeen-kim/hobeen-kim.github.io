"""릿지(L2)와 라쏘(L1)의 제약 영역 — 라쏘는 모서리에서 만나 계수를 0으로 (light/dark PNG)."""
import numpy as np
from matplotlib.patches import Ellipse, Circle, Polygon
from _common import diagram

CY = 5.5   # 원점 세로 오프셋 (ylim 0..ymax)


def _panel(d, cx, title, kind):
    P = d.P
    ax = d.ax
    ols = (cx + 2.1, CY + 3.4)   # OLS 해 (제약 없는 최소)

    for r in (1.2, 2.2, 3.2, 4.2):
        ax.add_patch(Ellipse(ols, r * 2.4, r * 1.5, angle=25,
                     fill=False, edgecolor=P["edge"], lw=1.0, alpha=0.7))

    s = 1.9
    if kind == "l2":
        ax.add_patch(Circle((cx, CY), s, facecolor=P["blue"],
                     edgecolor=P["accent"], lw=1.8, alpha=0.85, zorder=3))
        sol = (cx + s * np.cos(0.62), CY + s * np.sin(0.62))
    else:
        dia = [(cx, CY + s), (cx + s, CY), (cx, CY - s), (cx - s, CY)]
        ax.add_patch(Polygon(dia, facecolor=P["green"],
                     edgecolor=P["accent"], lw=1.8, alpha=0.85, zorder=3))
        sol = (cx, CY + s)   # 꼭짓점 = w2 축 위 (다른 계수 0)

    ax.scatter(*ols, s=70, marker="x", color=P["violet"], linewidth=2.4, zorder=6)
    ax.scatter(*sol, s=90, color=P["orange"], edgecolor=P["text"],
               linewidth=1.0, zorder=6)

    d.text(cx, CY - 3.0, title, size=11, weight="bold")
    if kind == "l1":
        d.text(sol[0] + 0.3, sol[1] + 0.55, "w₁=0", size=9.5,
               color=P["orange"], ha="left")


def draw(d):
    _panel(d, 5.5, "릿지 (L2) — 원", "l2")
    _panel(d, 15.5, "라쏘 (L1) — 마름모", "l1")


diagram("06-regularization-constraint", draw, w=10, h=5.2, xmax=21, ymax=11)
