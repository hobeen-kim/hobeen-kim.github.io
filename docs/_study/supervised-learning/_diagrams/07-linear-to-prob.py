"""로지스틱 회귀 파이프라인 — 선형 출력 → 시그모이드 → 확률 → 임계값 → 클래스 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    steps = [
        ("특징 x", P["gray"], "x₁, x₂, …"),
        ("선형 결합 z", P["blue"], "z = w·x + b\n(-∞ ~ +∞)"),
        ("시그모이드 σ", P["purple"], "σ(z) = 1 / (1 + e^-z)"),
        ("확률 p", P["green"], "0 ~ 1"),
        ("임계값 판정", P["brown"], "p ≥ 0.5 → 1\np < 0.5 → 0"),
    ]
    w, gap = 16, 3.4
    x0 = 1.5
    y = 6
    for i, (title, fc, sub) in enumerate(steps):
        x = x0 + i * (w + gap)
        d.box(x, y - 4, w, 8, fc)
        d.text(x + w / 2, y + 1.6, title, size=10.5, weight="bold")
        d.text(x + w / 2, y - 1.8, sub, size=9, color=P["dim"])
        if i:
            d.arrow(x - gap + 0.3, y, x - 0.3, y, color=P["accent"])


diagram("07-linear-to-prob", draw, w=13.5, h=3.4, xmax=100, ymax=13)
