"""CH18 SHAP 기여 분해 — 기준값 E[f(x)]에서 피처별 +/- 기여를 쌓아 예측 f(x)로 (light/dark PNG).

세로 waterfall: 각 행이 하나의 피처, 이전 누적에서 새 누적까지 막대가 뻗는다.
양의 기여는 brown(→ 오른쪽), 음의 기여는 blue(← 왼쪽).
"""
from _common import diagram


def draw(d):
    P = d.P

    def X(p):
        return 27 + p * 56  # 확률 0~1 → x 27~83

    base = 0.30
    steps = [
        ("소득 상위",       +0.15),
        ("연체 이력 없음",  +0.10),
        ("재직기간 짧음",   -0.08),
        ("부채비율 낮음",   +0.13),
    ]

    y0, dy, bh = 6.0, 6.5, 4.0

    # 기준값 마커
    d.text(24, y0 - 3.0, f"기준값 E[f(x)] = {base:.2f}", size=9,
           color=P["dim"], ha="right")
    d.arrow(X(base), y0 - 2.2, X(base), y0, color=P["edge"], lw=1.2, style="-")

    cum = base
    for i, (name, delta) in enumerate(steps):
        y = y0 + i * dy
        start, end = cum, cum + delta
        lo, hi = min(start, end), max(start, end)
        fc = P["brown"] if delta > 0 else P["blue"]
        d.box(X(lo), y, X(hi) - X(lo), bh, fc)
        # 피처 라벨(왼쪽)
        d.text(24, y + bh / 2, name, size=9, ha="right", color=P["text"])
        # 기여값 라벨(막대 오른쪽 바깥)
        sign = "+" if delta > 0 else "-"
        d.text(X(hi) + 1.5, y + bh / 2, f"{sign}{abs(delta):.2f}",
               size=8.5, ha="left",
               color=P["orange"] if delta > 0 else P["accent"])
        # 다음 막대로 이어지는 누적선
        d.arrow(X(end), y + bh, X(end), y + dy,
                color=P["edge"], lw=1.1, style="-", ls=(0, (3, 3)))
        cum = end

    # 최종 예측
    yf = y0 + len(steps) * dy
    d.box(X(cum) - 6, yf, 12, bh, P["gray"], ec=P["accent"], lw=1.8)
    d.text(X(cum), yf + bh / 2, f"f(x) = {cum:.2f}", size=9.5,
           weight="bold", color=P["accent"])


diagram("18-shap-attribution", draw, w=11, h=6.2, ymax=40)
