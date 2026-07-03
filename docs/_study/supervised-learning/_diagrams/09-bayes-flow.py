"""CH9 나이브 베이즈 분류 흐름 — 사전확률 × 우도 → 사후확률 → argmax (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 입력
    d.box(1, 18, 16, 12, P["blue"])
    d.text(9, 26, "입력 특징 x", size=10.5, weight="bold")
    d.text(9, 21.5, "예: 문서의 단어들\n(x1, x2, …, xn)", size=9, color=P["dim"])

    # 사전확률 + 우도
    d.box(23, 30, 28, 12, P["gray"])
    d.text(37, 38, "사전확률 P(c)", size=10, weight="bold")
    d.text(37, 33.5, "클래스가 나타날 기본 비율", size=8.8, color=P["dim"])

    d.box(23, 6, 28, 16, P["gray"])
    d.text(37, 18.5, "우도  ∏ P(xi | c)", size=10, weight="bold")
    d.text(37, 12.5, "조건부 독립 가정으로\n각 특징 확률을 곱한다", size=8.8, color=P["dim"])

    d.arrow(17, 27, 23, 35)
    d.arrow(17, 21, 23, 15)

    # 사후확률
    d.box(57, 18, 24, 14, P["purple"])
    d.text(69, 28, "사후확률", size=10.5, weight="bold")
    d.text(69, 22.5, "P(c | x) ∝\nP(c)·∏ P(xi|c)", size=9, color=P["dim"])

    d.arrow(51, 34, 60, 30, color=P["orange"])
    d.arrow(51, 13, 60, 20, color=P["orange"])

    # argmax → 예측
    d.box(87, 18, 12, 14, P["green"], ec=P["accent"], lw=1.8)
    d.text(93, 28, "argmax_c", size=10, weight="bold", color=P["accent"])
    d.text(93, 22.5, "가장 큰\n클래스 선택", size=8.8, color=P["dim"])

    d.arrow(81, 25, 87, 25)


diagram("09-bayes-flow", draw, w=13, h=5.4, xmax=100, ymax=46)
