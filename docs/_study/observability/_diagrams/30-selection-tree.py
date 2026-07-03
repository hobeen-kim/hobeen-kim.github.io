"""CH30 수집 계층 선택 — 의사결정 트리 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def decision(x, y, w, h, label):
        d.box(x - w / 2, y - h / 2, w, h, P["gray"], ec=P["orange"], lw=1.5)
        d.text(x, y, label, size=9, weight="bold")

    def result(x, y, w, h, label, col, sub=None):
        d.box(x - w / 2, y - h / 2, w, h, col, ec=P["accent"], lw=1.5)
        if sub:
            d.text(x, y + 1.2, label, size=9.5, weight="bold")
            d.text(x, y - 1.6, sub, size=7.8, color=P["dim"])
        else:
            d.text(x, y, label, size=9.5, weight="bold")

    # start
    d.box(31, 43, 22, 5, P["blue"], ec=P["accent"], lw=1.5)
    d.text(42, 45.5, "수집 계층 선택", size=10.5, weight="bold", color=P["accent"])

    # Q1
    decision(42, 37, 28, 5.5, "백엔드가 Grafana LGTM+ 스택?")
    d.arrow(42, 43, 42, 39.8, color=P["edge"], lw=1.5)

    result(82, 37, 24, 6.4, "OTel Collector", P["brown"], sub="순수 · 벤더 중립")
    d.arrow(56, 37, 70, 37, color=P["accent"], lw=1.9)
    d.text(63, 38.6, "No", size=8.5, color=P["orange"], weight="bold")

    # Q2
    decision(42, 28, 28, 5.5, "벤더 락인 회피가 최우선?")
    d.arrow(42, 34.2, 42, 30.8, color=P["accent"], lw=1.9)
    d.text(45, 32.5, "Yes", size=8.5, color=P["orange"], weight="bold")

    result(82, 28, 24, 6.4, "OTel Collector", P["brown"], sub="+ Grafana OTLP 익스포터")
    d.arrow(56, 28, 70, 28, color=P["accent"], lw=1.9)
    d.text(63, 29.6, "Yes", size=8.5, color=P["orange"], weight="bold")

    # Q3
    decision(42, 19, 28, 6, "clustering · 프로파일\n네이티브 지원 필요?")
    d.arrow(42, 25.2, 42, 22.0, color=P["accent"], lw=1.9)
    d.text(45, 23.6, "No", size=8.5, color=P["orange"], weight="bold")

    result(15, 19, 20, 6.4, "Alloy", P["green"])
    d.arrow(28, 19, 25, 19, color=P["accent"], lw=1.9)
    d.text(26.5, 20.8, "Yes", size=8.5, color=P["orange"], weight="bold")

    result(42, 9, 30, 6.4, "둘 다 가능", P["purple"], sub="팀 숙련도로 결정")
    d.arrow(42, 16, 42, 12.2, color=P["accent"], lw=1.9)
    d.text(45, 14, "No", size=8.5, color=P["orange"], weight="bold")


diagram("30-selection-tree", draw, w=13, h=6.8, ymax=48)
