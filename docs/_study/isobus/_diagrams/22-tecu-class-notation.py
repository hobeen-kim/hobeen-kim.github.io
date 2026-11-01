"""CH22 §2 TECU 클래스 표기 읽기: class 2GP = 기본 클래스 숫자 + 기능 묶음 문자 (light/dark PNG)."""
from _common import diagram

CLASSES = [
    ("Class 1", "속도, 엔진 회전수, 리어 히치 위치, 리어 PTO 회전수", "blue"),
    ("Class 2", "Class 1 + 시간·날짜, 주행 거리·방향, 견인력, 밸브 유량, 조명", "blue"),
    ("Class 3", "Class 2 + 리어 히치·PTO·보조 밸브 명령을 받는다", "green"),
]

LETTERS = [
    ("M", "발진: 전진·후진 (v2)"),
    ("P", "속도·주행 전략 (v2)"),
    ("G", "조향 (v2)"),
    ("F", "전방 히치·PTO"),
    ("N", "항법(GPS) 메시지"),
]


def draw(d):
    P = d.P

    d.text(41.5, 46, "class", size=12, color=P["dim"], ha="right")
    chips = {}
    for x, ch, color in ((45, "2", "blue"), (52, "G", "purple"), (59, "P", "purple")):
        d.box(x - 2.8, 43.2, 5.6, 5.6, P[color], ec=P["accent"], lw=1.6)
        d.text(x, 46, ch, size=14, weight="bold")
        chips[ch] = x

    d.text(22, 39.5, "숫자: 기본 클래스 (위로 쌓인다)", size=9.5, weight="bold", color=P["dim"])
    d.text(82, 39.5, "문자: 덧붙는 기능 묶음 (위로 읽는다)", size=9.5, weight="bold", color=P["dim"])

    box_y = {}
    for i, (name, desc, color) in enumerate(CLASSES):
        y = 3 + i * 11.5
        d.box(4, y, 36, 9, P[color])
        d.text(22, y + 6.2, name, size=10.5, weight="bold")
        d.text(22, y + 2.6, desc, size=8.2, color=P["dim"])
        box_y[name] = y + 4.5
    d.arrow(1.8, 4, 1.8, 35, color=P["dim"], lw=1.2)

    letter_y = {}
    for i, (ch, desc) in enumerate(LETTERS):
        y = 31 - i * 7
        d.box(66, y, 32, 5.4, P["purple"])
        d.text(69.5, y + 2.7, ch, size=11, weight="bold")
        d.text(74, y + 2.7, desc, size=9, ha="left")
        letter_y[ch] = y + 2.7

    d.arrow(chips["2"] - 1, 43, 40.6, box_y["Class 2"] + 2, color=P["accent"])
    d.arrow(chips["G"] + 1, 43, 65.5, letter_y["G"], color=P["violet"])
    d.arrow(chips["P"] + 1.5, 43, 65.5, letter_y["P"], color=P["violet"])


diagram("22-tecu-class-notation", draw, w=12.5, h=6.2, xmax=100, ymax=50)
