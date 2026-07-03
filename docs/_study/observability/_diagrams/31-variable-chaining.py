"""CH31 변수 체이닝과 $__rate_interval — 템플릿 흐름 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(4, 17, 22, 7, P["blue"])
    d.text(15, 21.4, "$namespace", size=11, weight="bold", color=P["accent"])
    d.text(15, 18.6, "query variable", size=8, color=P["dim"])

    d.box(34, 17, 22, 7, P["green"])
    d.text(45, 21.4, "$pod", size=11, weight="bold", color=P["accent"])
    d.text(45, 18.6, "namespace로 좁힌 체이닝", size=7.6, color=P["dim"])

    d.box(4, 5, 22, 7, P["brown"])
    d.text(15, 9.4, "$__rate_interval", size=10, weight="bold", color=P["accent"])
    d.text(15, 6.6, "자동 계산", size=8, color=P["dim"])

    d.box(66, 8.5, 30, 13, P["purple"], ec=P["accent"], lw=1.8)
    d.text(81, 18.4, "PromQL 패널 쿼리", size=10, weight="bold")
    d.text(81, 15.2, "namespace=~ $namespace", size=8, color=P["text"])
    d.text(81, 13.0, "pod=~ $pod", size=8, color=P["text"])
    d.text(81, 10.8, "[$__rate_interval]", size=8, color=P["text"])

    d.arrow(26, 20.5, 34, 20.5, color=P["accent"], lw=2.0)
    d.text(30, 22.3, "필터링", size=8, color=P["orange"], weight="bold")
    d.arrow(56, 20.5, 66, 17.0, color=P["accent"], lw=2.0)
    d.arrow(26, 8.5, 66, 12.5, color=P["accent"], lw=1.8, rad=-0.06)


diagram("31-variable-chaining", draw, w=13, h=4.0, ymax=26)
