"""CH03 §8 트랙터·작업기 네트워크의 물리 구성: ISO 11783-1 Figure 2 단순화 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def chip(x, y, w, h, label, fc=None, size=8.4):
        d.box(x, y, w, h, fc or P["chip"])
        d.text(x + w / 2, y + h / 2, label, size=size)

    def tbc(x, y):
        d.box(x - 2, y - 1.6, 4, 3.2, P["brown"], ec=P["orange"], lw=1.6)
        d.text(x, y, "TBC", size=7.6)

    def bus(x0, x1, y, color=None):
        d.ax.plot([x0, x1], [y, y], color=color or P["accent"], lw=2.6)

    def lead(x, y0, y1):
        d.ax.plot([x, x], [y0, y1], color=P["edge"], lw=1.4)

    # 컨테이너
    d.box(2, 3, 57, 45, P["gray"], ec=P["edge"])
    d.text(4, 45.5, "트랙터", size=10, weight="bold", ha="left")
    d.box(66, 2, 33, 31, P["gray"], ec=P["edge"])
    d.text(68, 30.5, "견인 작업기", size=10, weight="bold", ha="left")

    # 트랙터 네트워크
    ty = 36
    bus(8, 50, ty)
    tbc(6, ty)
    tbc(52, ty)
    d.text(8, ty - 2.6, "트랙터 네트워크", size=8.4, color=P["dim"], ha="left")
    for x, name in ((13, "엔진"), (23, "변속기"), (33, "브레이크"), (43, "히치\n제어기")):
        chip(x - 4, 39.5, 8, 4.6, name, P["blue"])
        lead(x, ty, 39.5)

    # Tractor ECU
    chip(24, 25, 12, 5, "Tractor ECU", P["purple"], size=8.6)
    lead(30, 30, ty)
    lead(30, 18, 25)

    # 작업기 네트워크 (트랙터 안 -> 분리 커넥터 -> 견인 작업기)
    iy = 18
    bus(8, 93, iy)
    tbc(6, iy)
    tbc(95, iy)
    d.text(8, iy - 2.6, "작업기 네트워크", size=8.4, color=P["dim"], ha="left")
    chip(11, 21, 10, 3.6, "진단 커넥터")
    lead(16, iy, 21)
    chip(42, 21, 14, 3.6, "버스 연장 커넥터")
    lead(49, iy, 21)
    for x, name in ((14, "VT"), (24, "TC"), (44, "ECU")):
        chip(x - 4, 8, 8, 4.4, name, P["blue"])
        lead(x, 12.4, iy)
    d.box(57.5, 15.5, 6, 5, P["brown"])
    d.text(60.5, 13.2, "분리 커넥터", size=7.8, color=P["dim"])

    # 견인 작업기
    for x in (72, 82):
        chip(x - 4, 22, 8, 4.4, "ECU", P["blue"])
        lead(x, iy, 22)
    chip(70, 9, 10, 4.4, "NIU", P["purple"])
    lead(75, 13.4, iy)
    iy2 = 5
    bus(71, 93, iy2, color=P["violet"])
    tbc(69, iy2)
    tbc(95, iy2)
    lead(75, iy2, 9)
    chip(84, 7.4, 8, 3.4, "ECU", P["blue"])
    lead(88, iy2, 7.4)
    d.text(88, 13, "내부 네트워크", size=8, color=P["dim"])


diagram("03-isobus-network-structure", draw, w=12, h=5.6, xmax=100, ymax=50)
