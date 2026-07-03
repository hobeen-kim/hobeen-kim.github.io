"""OLS — 잔차 제곱합 최소화: 회귀 직선과 잔차(세로선) (light/dark PNG)."""
import numpy as np
from _common import diagram


def draw(d):
    P = d.P
    ax = d.ax

    xs = np.array([0.8, 1.7, 2.6, 3.4, 4.1, 5.0, 5.9, 6.7, 7.6, 8.5, 9.2])
    ys = np.array([1.6, 2.9, 2.4, 4.1, 3.6, 5.3, 4.7, 6.4, 6.0, 7.6, 7.1])

    a, b = np.polyfit(xs, ys, 1)
    line_x = np.array([0.2, 9.8])
    line_y = a * line_x + b

    # 잔차 세로선
    for x, y in zip(xs, ys):
        yhat = a * x + b
        ax.plot([x, x], [y, yhat], color=P["orange"], lw=1.6, zorder=3)

    ax.plot(line_x, line_y, color=P["accent"], lw=2.4, zorder=4)
    ax.scatter(xs, ys, s=60, color=P["violet"], edgecolor=P["edge"],
               linewidth=1.0, zorder=5)

    # 라벨: 예측 직선, 잔차
    d.text(8.7, a * 8.7 + b + 0.9, "회귀 직선  y = w·x + b",
           size=10.5, color=P["accent"], ha="right")
    ri = 5
    d.text(xs[ri] + 0.35, (ys[ri] + a * xs[ri] + b) / 2,
           "잔차", size=10, color=P["orange"], ha="left")


diagram("06-ols-residuals", draw, w=8.5, h=5.0, xmax=10, ymax=9)
