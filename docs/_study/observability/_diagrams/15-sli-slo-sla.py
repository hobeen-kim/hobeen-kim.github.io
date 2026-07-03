"""CH15 SLI → SLO → SLA 층위 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    cols = [
        (18, P["blue"], "SLI", "측정값", "성공 요청 비율"),
        (50, P["green"], "SLO", "내부 목표", "30일 롤링 99.9%"),
        (82, P["brown"], "SLA", "고객 계약", "99.5% (위반 시 페널티)"),
    ]
    for cx, fc, t, sub, val in cols:
        d.box(cx - 15, 10, 30, 22, fc)
        d.text(cx, 27, t, size=16, weight="bold", color=P["accent"])
        d.text(cx, 22.5, sub, size=10, color=P["dim"])
        d.box(cx - 12.5, 13.5, 25, 4.6, P["chip"])
        d.text(cx, 15.8, val, size=9.5)

    d.arrow(33, 21, 35, 21, color=P["orange"])
    d.arrow(65, 21, 67, 21, color=P["orange"])


diagram("15-sli-slo-sla", draw, w=11, h=4.6, ymax=40)
