"""CH45 §1 작업기를 표로 본 비유: 행 = Element, 열 = DDI, 칸 = 값 (light/dark PNG)."""
from _common import diagram

LX, LW = 4, 22            # 행 라벨 열
CW = 15                   # DDI 열 너비
HEAD_Y, HEAD_H = 37, 8
ROW_H = 8

COLS = ["DDI 1\n목표 살포량", "DDI 2\n실제 살포량", "DDI 37\n실제 유량"]
ROWS = [
    ("Element 1\n펌프", [None, None, "15 L/min"]),
    ("Element 2\n섹션 2", ["200 L/ha", "201 L/ha", None]),
    ("Element 3\n섹션 3", ["200 L/ha", "198 L/ha", None]),
]
HIGHLIGHT = (2, 0)

MSG = [  # (라벨, 너비, 색)
    ("명령 3", 10, "purple"),
    ("Element 3", 11, "green"),
    ("DDI 1", 13, "brown"),
    ("값 2,000,000", 21, "blue"),
]
MSG_Y, MSG_H = 2.5, 6


def col_x(j):
    return LX + LW + j * CW


def row_y(i):
    return HEAD_Y - (i + 1) * ROW_H


def draw(d):
    P = d.P
    d.box(LX, HEAD_Y, LW, HEAD_H, P["gray"], lw=1.0)
    d.text(LX + LW / 2, HEAD_Y + HEAD_H / 2, "Element \\ DDI", size=9, color=P["dim"])
    for j, name in enumerate(COLS):
        d.box(col_x(j), HEAD_Y, CW, HEAD_H, P["gray"], lw=1.0)
        d.text(col_x(j) + CW / 2, HEAD_Y + HEAD_H / 2, name, size=9.5, weight="bold")

    for i, (name, cells) in enumerate(ROWS):
        y = row_y(i)
        d.box(LX, y, LW, ROW_H, P["green"], lw=1.0)
        d.text(LX + LW / 2, y + ROW_H / 2, name, size=9.5, weight="bold")
        for j, cell in enumerate(cells):
            x = col_x(j)
            if (i, j) == HIGHLIGHT:
                d.box(x, y, CW, ROW_H, P["blue"], ec=P["accent"], lw=2.6)
                d.text(x + CW / 2, y + ROW_H / 2, cell, size=10, weight="bold")
            elif cell is None:
                d.box(x, y, CW, ROW_H, P["gray"], lw=1.0)
                d.text(x + CW / 2, y + ROW_H / 2, "없음", size=9, color=P["dim"])
            else:
                d.box(x, y, CW, ROW_H, P["chip"], lw=1.0)
                d.text(x + CW / 2, y + ROW_H / 2, cell, size=10)

    x = LX
    centers = []
    for text, w, color in MSG:
        d.box(x, MSG_Y, w, MSG_H, P[color], lw=1.2)
        d.text(x + w / 2, MSG_Y + MSG_H / 2, text, size=9.5, weight="bold")
        centers.append(x + w / 2)
        x += w + 1
    d.text(x + 1, MSG_Y + MSG_H / 2, "메시지 하나 (8바이트)", size=9, color=P["dim"], ha="left")

    bottom = row_y(len(ROWS) - 1)
    hx = col_x(HIGHLIGHT[1])
    d.arrow(centers[1], MSG_Y + MSG_H + 0.2, LX + LW / 2 + 4, bottom - 0.2, color=P["accent"])
    d.arrow(centers[2], MSG_Y + MSG_H + 0.2, hx + CW / 2 - 2, bottom - 0.2, color=P["accent"])
    d.arrow(centers[3], MSG_Y + MSG_H + 0.2, hx + CW - 1.5, bottom - 0.2, color=P["accent"])

    lx = col_x(len(COLS)) + 4
    for k, line in enumerate(["행 = Element (어느 부분)", "열 = DDI (값의 종류)",
                              "칸 = 값 (숫자)", "명령 = 그 칸으로 할 일"]):
        d.text(lx, 38 - k * 5, line, size=10, ha="left")


diagram("45-process-data-table", draw, w=12, h=6, xmax=100, ymax=50)
