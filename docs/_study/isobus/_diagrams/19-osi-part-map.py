"""19장 2절: OSI 7계층과 ISO 11783 파트의 대응. 4계층의 일(TP·ETP)은 Part 3에 규정 (light/dark PNG)."""
from _common import diagram

ROW_H, STEP, BASE = 7, 8.2, 3
LEFT_X, LEFT_W = 3, 30
RIGHT_X, RIGHT_W = 45, 38

LAYERS = {
    7: ("7  응용 (Application)", "Part 6~14의 응용 메시지\n(VT, TECU, TC, 진단 등)", "purple"),
    6: ("6  표현 (Presentation)", "배정 없음", None),
    5: ("5  세션 (Session)", "배정 없음", None),
    4: ("4  전송 (Transport)", "TP·ETP\n(큰 메시지 분할·재조립)", "brown"),
    3: ("3  네트워크 (Network)", "Part 4 (NIU)", "blue"),
    2: ("2  데이터 링크 (Data link)", "Part 3", "blue"),
    1: ("1  물리 (Physical)", "Part 2", "blue"),
}


def y0(n):
    return BASE + (n - 1) * STEP


def draw(d):
    P = d.P
    for n, (name, part, key) in LAYERS.items():
        y = y0(n)
        mid = y + ROW_H / 2
        d.box(LEFT_X, y, LEFT_W, ROW_H, P["gray"])
        d.text(LEFT_X + LEFT_W / 2, mid, name, size=10)
        if key:
            d.box(RIGHT_X, y, RIGHT_W, ROW_H, P[key])
            d.text(RIGHT_X + RIGHT_W / 2, mid, part, size=10)
            d.ax.plot([LEFT_X + LEFT_W, RIGHT_X], [mid, mid], color=P["edge"], lw=1.3, zorder=2)
        else:
            d.text(RIGHT_X + RIGHT_W / 2, mid, part, size=10, color=P["dim"])
            d.ax.plot([LEFT_X + LEFT_W, RIGHT_X], [mid, mid], color=P["edge"], lw=1.0,
                      ls=(0, (2, 3)), zorder=2)

    x = RIGHT_X + RIGHT_W
    d.arrow(x, y0(4) + ROW_H / 2, x, y0(2) + ROW_H / 2, color=P["orange"], lw=1.8,
            ls="--", rad=-0.55)
    d.text(x + 10.5, y0(3) + ROW_H / 2, "규정 위치는\nPart 3", size=9.5, color=P["orange"])


diagram("19-osi-part-map", draw, w=12, h=6.6, xmax=100, ymax=63)
