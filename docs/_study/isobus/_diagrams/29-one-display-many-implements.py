"""CH29 VT 디스플레이 하나에 여러 작업기가 각자 오브젝트 풀을 올리는 구조 (light/dark PNG)."""
from _common import diagram

ECUS = [
    (14, "비료 살포기 ECU", "brown", "오브젝트 풀 A"),
    (38, "파종기 ECU", "green", "오브젝트 풀 B"),
    (62, "스프레이어 ECU", "purple", "오브젝트 풀 C"),
    (86, "베일러 ECU", "chip", "오브젝트 풀 D"),
]


def draw(d):
    P = d.P
    d.box(4, 30, 92, 10, P["blue"], ec=P["accent"])
    d.text(50, 35, "VT 디스플레이 (하나의 통합 인터페이스)", size=11.5)

    for x, name, color, pool in ECUS:
        d.box(x - 10, 3, 20, 7.5, P[color])
        d.text(x, 6.75, name, size=10)
        d.arrow(x, 10.5, x, 30, color=P["accent"])
        d.text(x + 1.2, 20.2, pool, size=9, color=P["accent"], ha="left")


diagram("29-one-display-many-implements", draw, w=11, h=4.4, xmax=100, ymax=43)
