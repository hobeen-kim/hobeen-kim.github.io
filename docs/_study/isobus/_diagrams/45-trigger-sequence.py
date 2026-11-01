"""CH45 §7 Measurement 명령으로 트리거를 거는 흐름: time interval, distance interval (light/dark PNG)."""
from _common import diagram

TC_X, CL_X = 26, 74
TOP = 55

# (종류, 라벨): "tc": TC->클라이언트, "cl": 클라이언트->TC, "note": 메모, "loop": 반복 구간 안의 클라이언트->TC
ROWS = [
    ("note", "TC가 100 ms 주기 보고를 건다"),
    ("tc", "Measurement (4) time interval\n[DDI=37, Element=1, 100 ms]"),
    ("cl", "PDACK (수락, 버전 4)"),
    ("loop", ("100 ms마다", "Process Data Value (3)   [DDI=37, Element=1, 현재 유량]")),
    ("note", "다른 값(DDI 2, Element 3)에는 거리 간격 보고를 건다"),
    ("tc", "Measurement (5) distance interval\n[DDI=2, Element=3, 1 m]"),
    ("cl", "PDACK (수락, 버전 4)"),
    ("loop", ("1 m 이동마다", "Process Data Value (3)   [DDI=2, Element=3, 실제 살포량]")),
]
HEIGHT = {"note": 4.4, "tc": 6.2, "cl": 4.4, "loop": 8.0}


def layout():
    ys, y = [], TOP - 7.0
    for kind, _ in ROWS:
        h = HEIGHT[kind]
        ys.append(y - h / 2)
        y -= h
    return ys, y


def draw(d):
    P = d.P
    ys, bottom = layout()
    for x, name in ((TC_X, "TC"), (CL_X, "클라이언트 (작업기 ECU)")):
        d.box(x - 11, TOP - 5.0, 22, 4.2, P["blue"])
        d.text(x, TOP - 2.9, name, size=10.5)
        d.arrow(x, TOP - 5.2, x, bottom, color=P["edge"], lw=1.1, style="-", ls="--")

    for (kind, label), y in zip(ROWS, ys):
        if kind == "note":
            d.box(TC_X - 6, y - 1.4, CL_X - TC_X + 12, 2.8, P["green"], lw=1.0)
            d.text((TC_X + CL_X) / 2, y, label, size=9)
        elif kind == "tc":
            ay = y - 1.5
            d.arrow(TC_X, ay, CL_X, ay, color=P["accent"])
            d.text((TC_X + CL_X) / 2, ay + 2.2, label, size=8.6)
        elif kind == "cl":
            ay = y - 0.8
            d.arrow(CL_X, ay, TC_X, ay, color=P["orange"], ls="--")
            d.text((TC_X + CL_X) / 2, ay + 1.4, label, size=8.6)
        else:
            title, msg = label
            d.box(TC_X - 8, y - 3.5, CL_X - TC_X + 16, 7.0, "none", ec=P["violet"], lw=1.2)
            d.text(TC_X + 1.5, y + 2.4, "반복: " + title, size=8.6, color=P["violet"], ha="left")
            ay = y - 1.6
            d.arrow(CL_X, ay, TC_X, ay, color=P["orange"], ls="--")
            d.text((TC_X + CL_X) / 2, ay + 1.4, msg, size=8.6)


diagram("45-trigger-sequence", draw, w=12, h=6.6, xmax=100, ymax=55)
