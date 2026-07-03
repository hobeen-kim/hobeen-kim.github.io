"""CH06 §4 Classic vs Native histogram — 카디널리티 대비 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 왼쪽: Classic
    d.box(3, 6, 44, 38, P["brown"], ec=P["orange"], lw=1.6)
    d.text(25, 40.5, "Classic — 버킷마다 별도 시계열", size=11, weight="bold",
           color=P["orange"])
    classic = ["le=0.1  →  시계열 1", "le=0.5  →  시계열 2",
               "le=1  →  시계열 3", "le=+Inf  →  시계열 4"]
    for i, t in enumerate(classic):
        yy = 33 - i * 6
        d.box(7, yy, 36, 4.6, P["chip"])
        d.text(25, yy + 2.3, t, size=10)
    d.text(25, 9, "버킷 수만큼 시계열이 배수로 증가", size=8.5,
           color=P["orange"], style="italic")

    # 오른쪽: Native
    d.box(53, 6, 44, 38, P["green"], ec=P["accent"], lw=1.8)
    d.text(75, 40.5, "Native — 버킷 수와 무관하게 시계열 하나", size=10.5,
           weight="bold", color=P["accent"])
    d.box(57, 27, 36, 9, P["chip"], ec=P["accent"], lw=1.4)
    d.text(75, 31.5, "단일 시계열\n값 자체가 sparse 버킷 벡터", size=9.5)
    d.arrow(75, 27, 75, 23, color=P["accent"])
    d.box(57, 13, 36, 9, P["chip"])
    d.text(75, 17.5, "지수 스킴 버킷\n자동 고해상도", size=9.5)


diagram("06-native-histogram", draw, w=13, h=6.2, ymax=46)
