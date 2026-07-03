"""CH2 편향-분산 트레이드오프 — 모델 복잡도 대 오차 곡선 (light/dark PNG)."""
import numpy as np

from _common import diagram, Line2D


def draw(d):
    P = d.P

    x = np.linspace(12, 92, 200)
    t = (x - 12) / 80.0  # 0..1 복잡도

    bias2 = 34 * np.exp(-t * 3.2) + 2          # 편향^2: 복잡도↑ 감소
    variance = 2 + 33 * (t ** 2.3)             # 분산: 복잡도↑ 증가
    total = bias2 + variance                   # 검증 오차(총)
    train = 33 * np.exp(-t * 3.0) + 1.5        # 학습 오차: 단조 감소

    ax = d.ax
    ax.plot(x, bias2, color=P["violet"], lw=2.0, ls="--")
    ax.plot(x, variance, color=P["orange"], lw=2.0, ls="--")
    ax.plot(x, total, color=P["accent"], lw=2.6)
    ax.plot(x, train, color=P["dim"], lw=1.8, ls=":")

    # 최적점 표시
    i = int(np.argmin(total))
    ax.plot([x[i]], [total[i]], marker="o", color=P["accent"], ms=8, zorder=6)
    d.arrow(x[i], total[i] + 13, x[i], total[i] + 1.5, color=P["edge"], lw=1.2)
    d.text(x[i], total[i] + 15.5, "최적 복잡도", size=9, weight="bold")

    # 축
    d.arrow(10, 6, 96, 6, color=P["edge"], lw=1.4)
    d.arrow(10, 6, 10, 46, color=P["edge"], lw=1.4)
    d.text(53, 1.8, "모델 복잡도 →", size=9.5, color=P["dim"])
    ax.text(4.5, 26, "오차", fontsize=9.5, color=P["dim"], rotation=90,
            ha="center", va="center")

    # 영역 라벨
    d.text(20, 42, "과소적합\n(편향↑)", size=8.6, color=P["dim"])
    d.text(85, 42, "과적합\n(분산↑)", size=8.6, color=P["dim"])

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.6, label="검증 오차(총)"),
        Line2D([0], [0], color=P["dim"], lw=1.8, ls=":", label="학습 오차"),
        Line2D([0], [0], color=P["violet"], lw=2.0, ls="--", label="편향²"),
        Line2D([0], [0], color=P["orange"], lw=2.0, ls="--", label="분산"),
    ], loc="upper center", anchor=(0.5, 0.99), fontsize=8.5)


diagram("02-bias-variance", draw, w=12, h=6, ymax=48)
