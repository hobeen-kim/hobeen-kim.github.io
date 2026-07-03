"""CH3 ROC vs PR 곡선 — 불균형 데이터에서의 관점 차이 (light/dark PNG)."""
import numpy as np

from _common import diagram, Line2D


def draw(d):
    P = d.P
    ax = d.ax

    # 좌: ROC (x=FPR, y=TPR), 우: PR (x=Recall, y=Precision)
    def axes(ox, title, xlab, ylab):
        d.arrow(ox, 6, ox + 34, 6, color=P["edge"], lw=1.3)
        d.arrow(ox, 6, ox, 40, color=P["edge"], lw=1.3)
        d.text(ox + 16, 39, title, size=10, weight="bold")
        d.text(ox + 16, 2, xlab, size=8.4, color=P["dim"])
        ax.text(ox - 2.5, 23, ylab, fontsize=8.4, color=P["dim"],
                rotation=90, ha="center", va="center")

    # ROC (왼쪽)
    ox = 8
    axes(ox, "ROC 곡선", "FPR (거짓 양성률)", "TPR (재현율)")
    t = np.linspace(0, 1, 100)
    roc = 1 - (1 - t) ** 2.6                     # 좋은 분류기
    ax.plot(ox + t * 32, 6 + roc * 30, color=P["accent"], lw=2.4)
    ax.plot([ox, ox + 32], [6, 36], color=P["dim"], lw=1.2, ls="--")  # 무작위
    d.text(ox + 24, 14, "무작위", size=7.6, color=P["dim"], style="italic")

    # PR (오른쪽)
    ox = 58
    axes(ox, "PR 곡선", "Recall (재현율)", "Precision")
    prec = 0.9 - 0.75 * t ** 2.2                 # recall↑ 시 precision↓
    ax.plot(ox + t * 32, 6 + prec * 30, color=P["accent"], lw=2.4)
    base = 0.1                                    # 양성 비율 10% → PR 기준선
    ax.plot([ox, ox + 32], [6 + base * 30, 6 + base * 30],
            color=P["dim"], lw=1.2, ls="--")
    d.text(ox + 22, 6 + base * 30 + 2.5, "기준선(양성 비율)", size=7.4,
           color=P["dim"], style="italic")

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.4, label="분류기 성능"),
        Line2D([0], [0], color=P["dim"], lw=1.2, ls="--", label="기준(무작위/양성 비율)"),
    ], loc="lower center", anchor=(0.5, 0.0), fontsize=8.2)


diagram("03-roc-pr", draw, w=13, h=5.6, ymax=44)
