"""CH10 이진 분류 불순도 곡선 — p에 따른 지니/엔트로피/오분류율 (light/dark PNG)."""
import math

from _common import diagram, Line2D


def draw(d):
    P = d.P

    n = 101
    ps = [i / (n - 1) for i in range(n)]

    def gini(p):
        return 2 * p * (1 - p)

    def entropy(p):
        if p in (0.0, 1.0):
            return 0.0
        # 최대값 1로 맞추기 위해 밑 2 로그 사용
        return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))

    def miscls(p):
        return 1 - max(p, 1 - p)

    d.ax.plot(ps, [entropy(p) for p in ps], color=P["accent"], lw=2.2,
              label="엔트로피")
    d.ax.plot(ps, [gini(p) for p in ps], color=P["orange"], lw=2.2,
              label="지니")
    d.ax.plot(ps, [miscls(p) for p in ps], color=P["violet"], lw=2.0,
              ls="--", label="오분류율")

    # 축 안내
    d.ax.plot([0, 1], [0, 0], color=P["edge"], lw=1.0)
    d.text(0.5, -0.09, "클래스 1의 비율 p", size=9.5, color=P["dim"])
    d.text(0.5, 1.08, "불순도(값이 클수록 섞여 있음)", size=9.5, color=P["dim"])
    d.text(0.5, 0.52, "p=0.5 에서 최대", size=8.8, color=P["dim"])

    d.ax.set_xlim(-0.02, 1.02)
    d.ax.set_ylim(-0.15, 1.15)
    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.2, label="엔트로피"),
        Line2D([0], [0], color=P["orange"], lw=2.2, label="지니"),
        Line2D([0], [0], color=P["violet"], lw=2.0, ls="--", label="오분류율"),
    ], loc="upper right", anchor=(0.99, 0.99))


diagram("10-impurity", draw, w=7.5, h=5.2, xmax=1, ymax=1)
