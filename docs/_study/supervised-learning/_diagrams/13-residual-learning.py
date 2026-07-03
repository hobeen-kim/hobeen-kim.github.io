"""CH13 잔차 학습 흐름 — 예측 → 잔차 → 다음 트리가 잔차를 학습 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    stages = [
        ("F0\n초기 예측\n(평균)", P["gray"]),
        ("잔차 r1\n= y - F0", P["chip"]),
        ("트리 h1\nr1 근사", P["green"]),
        ("잔차 r2\n= y - F1", P["chip"]),
        ("트리 h2\nr2 근사", P["green"]),
    ]
    w, gap = 16, 3
    x0 = 2
    for i, (lab, fc) in enumerate(stages):
        x = x0 + i * (w + gap)
        ec = P["orange"] if "잔차" in lab else P["edge"]
        d.box(x, 26, w, 12, fc, ec=ec, lw=1.6 if "잔차" in lab else 1.4)
        d.text(x + w / 2, 32, lab, size=8.8,
               color=P["orange"] if "잔차" in lab else P["text"])
        if i:
            d.arrow(x - gap + 0.3, 32, x - 0.3, 32, color=P["edge"], lw=1.5)

    # 학습률로 조금씩 더한다
    d.text(50, 20, "각 트리는 학습률 η만큼만 더해진다:  "
           r"$F_m = F_{m-1} + \eta\,h_m$", size=9.5, color=P["dim"])

    # 누적 예측 개선
    d.box(28, 6, 44, 8, P["blue"])
    d.text(50, 10, "F0 + η·h1 + η·h2 + …  →  틀린 만큼만 계속 메운다",
           size=9)
    d.arrow(10, 26, 40, 14, color=P["accent"], lw=1.3, rad=-0.1)
    d.arrow(66, 26, 60, 14, color=P["accent"], lw=1.3, rad=0.1)


diagram("13-residual-learning", draw, w=13, h=4.6, ymax=42)
