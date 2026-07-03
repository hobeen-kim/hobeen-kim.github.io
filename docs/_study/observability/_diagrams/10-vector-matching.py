"""CH10 벡터 매칭 — on/ignoring + group_left/right (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(3, 26, 26, 10, P["blue"], ec=P["accent"], lw=1.8)
    d.text(16, 32.2, "왼쪽 벡터 (one 쪽)", size=11, weight="bold", color=P["accent"])
    d.text(16, 28.6, "매칭 키당 시계열 1개 · 값", size=8.5, color=P["dim"])

    d.box(3, 8, 26, 10, P["green"])
    d.text(16, 14.2, "오른쪽 벡터 (many 쪽)", size=11, weight="bold", color=P["accent"])
    d.text(16, 10.6, "info 메트릭 · extra 라벨", size=8.5, color=P["dim"])

    d.box(50, 14, 46, 16, P["gray"], ec=P["accent"], lw=1.8)
    d.text(73, 25, "결과 벡터", size=12, weight="bold", color=P["accent"])
    d.text(73, 21, "왼쪽(one) 값 기준", size=9.5)
    d.text(73, 17.5, "many 쪽의 extra 라벨을 끌어와 덧붙임", size=9.5)

    d.arrow(29, 31, 50, 25, color=P["orange"], rad=0.06)
    d.text(39, 31, "on(label)\ngroup_left(extra)", size=8, color=P["orange"])
    d.arrow(29, 13, 50, 19, color=P["accent"], rad=-0.06)


diagram("10-vector-matching", draw, w=12.5, h=5.6, ymax=40)
