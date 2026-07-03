"""CH10 결정 트리 구조 — 축 정렬 조건으로 재귀 분할, 리프에서 예측 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 루트
    d.box(38, 38, 24, 9, P["gray"], ec=P["accent"], lw=1.8)
    d.text(50, 42.5, "꽃잎 길이 < 2.5?", size=10, weight="bold", color=P["accent"])

    # 1단계 자식
    d.box(10, 22, 22, 9, P["green"])
    d.text(21, 26.5, "Setosa", size=10, weight="bold")

    d.box(62, 22, 26, 9, P["gray"])
    d.text(75, 26.5, "꽃잎 너비 < 1.8?", size=10, weight="bold")

    d.arrow(44, 38, 24, 31)
    d.text(31, 36, "예", size=9.5, color=P["accent"])
    d.arrow(56, 38, 75, 31)
    d.text(67, 36, "아니오", size=9.5, color=P["dim"])

    # 2단계 리프
    d.box(52, 6, 22, 9, P["blue"])
    d.text(63, 10.5, "Versicolor", size=10, weight="bold")

    d.box(78, 6, 20, 9, P["brown"])
    d.text(88, 10.5, "Virginica", size=10, weight="bold")

    d.arrow(70, 22, 64, 15)
    d.text(64, 19, "예", size=9.5, color=P["accent"])
    d.arrow(80, 22, 88, 15)
    d.text(86, 19, "아니오", size=9.5, color=P["dim"])

    d.text(21, 18.5, "리프 = 예측", size=8.5, color=P["dim"])


diagram("10-tree-structure", draw, w=11, h=5.2, xmax=100, ymax=50)
