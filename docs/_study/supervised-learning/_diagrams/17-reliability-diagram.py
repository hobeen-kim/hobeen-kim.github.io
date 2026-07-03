"""CH17 신뢰도 곡선 — 완벽 보정 대각선과 과신/과소신 곡선 개념도 (light/dark PNG)."""
import numpy as np
from _common import diagram, Line2D


def draw(d):
    P = d.P
    ax = d.ax

    x = np.linspace(0, 1, 100)

    # 대각선(완벽 보정)
    ax.plot(x, x, color=P["dim"], lw=1.6, ls="--", zorder=2)

    # 과신: 예측 확률이 실제보다 높다 → 대각선 아래
    overconf = x ** 1.9
    ax.plot(x, overconf, color=P["orange"], lw=2.4, zorder=3)

    # 과소신: 예측 확률이 실제보다 낮다 → 대각선 위
    underconf = x ** 0.52
    ax.plot(x, underconf, color=P["violet"], lw=2.4, zorder=3)

    # 축 프레임
    ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], color=P["edge"], lw=1.2)
    ax.set_xlim(-0.08, 1.14)
    ax.set_ylim(-0.12, 1.12)

    d.text(0.5, -0.09, "예측 확률 (모델 출력)", size=9.5, color=P["dim"])
    ax.text(-0.06, 0.5, "실제 양성 비율", size=9.5, color=P["dim"],
            rotation=90, ha="center", va="center")

    d.text(0.83, 0.90, "완벽 보정", size=8.8, color=P["dim"], style="italic")
    d.text(0.72, 0.40, "과신\n(SVM·부스팅 경향)", size=8.6, color=P["orange"])
    d.text(0.30, 0.85, "과소신\n(NaiveBayes 경향)", size=8.6, color=P["violet"])


diagram("17-reliability-diagram", draw, w=6.4, h=5.4, xmax=1, ymax=1)
