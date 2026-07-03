"""early stopping — train loss는 계속 감소, valid loss는 반등하는 지점에서 정지 (light/dark PNG)."""
import numpy as np
from _common import diagram


def draw(d):
    P = d.P
    ax = d.ax

    n = np.linspace(1, 100, 100)
    train = 0.9 * np.exp(-n / 22) + 0.04
    valid = 0.9 * np.exp(-n / 20) + 0.12 + 0.0016 * np.maximum(0, n - 42)

    best = int(np.argmin(valid))          # valid 최소 지점
    stop = best + 20                       # patience 후 정지

    sx, sy = 6, 6      # 축 원점(데이터 좌표 → 그림 좌표 매핑용)
    kx, ky = 0.86, 34  # x, y 스케일

    def X(v):
        return sx + v * kx

    def Y(v):
        return sy + v * ky

    # 곡선
    ax.plot(X(n), Y(train), color=P["accent"], lw=2.0, zorder=4)
    ax.plot(X(n), Y(valid), color=P["orange"], lw=2.0, zorder=4)
    d.text(X(92), Y(train[-1]) - 1.4, "train", size=9.5, color=P["accent"], ha="left")
    d.text(X(92), Y(valid[-1]) + 1.0, "valid", size=9.5, color=P["orange"], ha="left")

    # best iteration 세로선
    ax.plot([X(n[best]), X(n[best])], [Y(0), Y(valid[best])],
            color=P["violet"], lw=1.4, ls="--", zorder=3)
    ax.scatter([X(n[best])], [Y(valid[best])], s=60, color=P["violet"],
               edgecolor=P["text"], linewidth=0.8, zorder=6)
    d.text(X(n[best]), Y(valid[best]) + 4.2, "best_iteration\n(best_score)",
           size=8.6, color=P["violet"])

    # stop 지점 (patience 소진)
    ax.plot([X(n[stop]), X(n[stop])], [Y(0), Y(valid[stop])],
            color=P["dim"], lw=1.2, ls=":", zorder=3)
    d.text(X(n[stop]) + 0.5, Y(valid[stop]) + 5.5,
           "여기서 정지\n(patience 소진)", size=8.4, color=P["dim"], ha="left")

    # 과적합 구간 음영
    ax.axvspan(X(n[best]), X(n[-1]), Y(0) / 44, 0.999,
               color=P["orange"], alpha=0.06, zorder=1)
    d.text(X((n[best] + 96) / 2), Y(0.14), "과적합 시작 구간",
           size=8.6, color=P["dim"])

    # 축
    ax.plot([X(0), X(102)], [Y(0), Y(0)], color=P["edge"], lw=1.2)
    ax.plot([X(0), X(0)], [Y(0), Y(1.02)], color=P["edge"], lw=1.2)
    d.text(X(52), Y(-0.08), "부스팅 라운드 (n_estimators)", size=9.5, color=P["dim"])
    ax.text(X(-4), Y(0.5), "검증 손실", fontsize=9.5, color=P["dim"],
            rotation=90, ha="center", va="center")


diagram("15-early-stopping", draw, w=11, h=5.4, xmax=100, ymax=44)
