"""CH13 학습률·트리 수 트레이드오프와 부스팅 과적합 — 검증 오차 곡선 (light/dark PNG)."""
import numpy as np

from _common import diagram


def draw(d):
    P = d.P

    x = np.linspace(0, 100, 400)

    # 큰 학습률: 빠르게 내려가지만 일찍 과적합(다시 상승)
    big = 0.28 + 0.62 * np.exp(-x / 9) + 0.0016 * np.clip(x - 35, 0, None)
    # 작은 학습률: 천천히 내려가 더 낮은 바닥, 아직 과적합 전
    small = 0.24 + 0.66 * np.exp(-x / 32)

    ax = d.ax
    ax.set_axis_on()
    ax.plot(x, big, color=P["orange"], lw=2.4, label="큰 학습률 (η 큼)")
    ax.plot(x, small, color=P["accent"], lw=2.4, label="작은 학습률 (η 작음)")

    # 큰 학습률의 최적 지점(과적합 시작) 표시
    imin = int(np.argmin(big))
    ax.plot(x[imin], big[imin], "o", color=P["orange"], ms=7)
    ax.annotate("early stopping\n(과적합 시작)",
                xy=(x[imin], big[imin]), xytext=(x[imin] + 8, big[imin] + 0.22),
                fontsize=8.5, color=P["dim"],
                arrowprops=dict(arrowstyle="->", color=P["edge"]))

    ax.set_xlim(0, 100)
    ax.set_ylim(0.13, 1.0)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(P["edge"])

    # 축 라벨을 플롯 내부에 배치 (헬퍼가 바깥 여백을 잘라내므로)
    ax.text(96, 0.155, "트리 수 (부스팅 반복) →", fontsize=9,
            color=P["dim"], ha="right", va="bottom")
    ax.text(1.5, 0.97, "검증 오차 ↑", fontsize=9, color=P["dim"],
            ha="left", va="top")

    ax.legend(fontsize=9, framealpha=0.0, labelcolor=P["dim"], loc="upper right")
    ax.text(50, 0.9, "배깅과 달리 트리를 더 쌓으면 과적합할 수 있다",
            fontsize=9, color=P["dim"], style="italic", ha="center")


diagram("13-lr-trees-tradeoff", draw, w=11, h=5.4, xmax=100, ymax=1.0)
