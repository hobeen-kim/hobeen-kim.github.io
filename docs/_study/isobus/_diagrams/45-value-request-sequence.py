"""CH45 §4 Value command·Value·Value Request 교환 순서 (light/dark PNG)."""
from _common import diagram

TC_X, CL_X = 26, 74
TOP = 44

# (종류, 라벨): "tc": TC->클라이언트 실선, "cl": 클라이언트->TC 점선, "note": 양쪽에 걸친 메모
ROWS = [
    ("note", "작업 시작 후 TC가 Setpoint 전달"),
    ("tc", "Value Command (3)   [DDI=1, Element=3, Value=200]\n섹션 3 목표 살포량 200 L/ha"),
    ("cl", "Process Data Value (3)   [DDI=2, Element=3, Value=198]\n섹션 3 실제 살포량 198 L/ha"),
    ("note", "TC가 특정 값을 명시적으로 요청"),
    ("tc", "Value Request (2)   [DDI=37, Element=1]\n펌프 실제 유량 요청"),
    ("cl", "Process Data Value (3)   [DDI=37, Element=1, Value=15]\n펌프 실제 유량 15 L/min"),
]
HEIGHT = {"note": 4.4, "tc": 6.4, "cl": 6.4}


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
            continue
        ay = y - 1.6
        if kind == "tc":
            d.arrow(TC_X, ay, CL_X, ay, color=P["accent"])
        else:
            d.arrow(CL_X, ay, TC_X, ay, color=P["orange"], ls="--")
        d.text((TC_X + CL_X) / 2, ay + 2.3, label, size=8.6)


diagram("45-value-request-sequence", draw, w=12, h=5.2, xmax=100, ymax=44)
