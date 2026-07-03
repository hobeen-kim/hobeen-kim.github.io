"""시그모이드 곡선 — 선형 출력 z를 0~1 확률로, 0.5에서 결정 경계 (light/dark PNG)."""
import numpy as np
from _common import diagram

XMAX, YMAX = 12.0, 1.15
Z0, ZSPAN = 6.0, 6.0   # z=0을 화면 중앙(6)에, ±6 범위를 매핑


def _zx(z):
    return Z0 + z / 6.0 * ZSPAN


def draw(d):
    P = d.P
    ax = d.ax

    z = np.linspace(-6, 6, 200)
    p = 1 / (1 + np.exp(-z))
    ax.plot(_zx(z), p, color=P["accent"], lw=2.6, zorder=5)

    # 0.5 수평선 · z=0 수직선 (결정 경계)
    ax.plot([0, XMAX], [0.5, 0.5], color=P["orange"], lw=1.3, ls="--", zorder=3)
    ax.plot([_zx(0), _zx(0)], [0, 1], color=P["violet"], lw=1.3, ls="--", zorder=3)

    # 축선
    ax.plot([0, XMAX], [0, 0], color=P["edge"], lw=1.2)
    ax.plot([_zx(-6), _zx(-6)], [0, 1.05], color=P["edge"], lw=1.2)

    d.text(_zx(0), 0.5, "•", size=16, color=P["violet"])
    d.text(_zx(0) + 0.2, 0.58, "결정 경계 (p=0.5)", size=9.5,
           color=P["violet"], ha="left")
    d.text(XMAX - 0.2, 0.93, "σ(z) → 1", size=10, color=P["accent"], ha="right")
    d.text(_zx(-6) + 0.2, 0.08, "σ(z) → 0", size=10, color=P["accent"], ha="left")
    d.text(XMAX - 0.2, 0.03, "z = w·x + b  (선형 출력)", size=9.5,
           color=P["dim"], ha="right")
    d.text(_zx(-6) - 0.15, 1.0, "확률 p", size=9.5, color=P["dim"], ha="right")


diagram("07-sigmoid", draw, w=8.5, h=4.6, xmax=XMAX, ymax=YMAX)
