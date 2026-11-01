"""36장 1절: 작업기와 VT의 두 방향 대화. 명령·활성화 메시지와 각 응답의 PGN (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(2, 5, 22, 40, P["green"])
    d.text(13, 27.5, "작업기 ECU", size=13, weight="bold")
    d.text(13, 23, "(Working Set)", size=10, color=P["dim"])

    d.box(60, 5, 18, 40, P["blue"])
    d.text(69, 27.5, "VT", size=13, weight="bold")
    d.text(69, 23, "(디스플레이)", size=10, color=P["dim"])

    d.box(87, 19, 11, 12, P["brown"])
    d.text(92.5, 25, "운전자", size=11, weight="bold")

    def msg(y, x1, x2, top, bottom, color, ls="-"):
        d.arrow(x1, y, x2, y, color=color, ls=ls)
        d.text((x1 + x2) / 2, y + 1.9, top, size=9.6, color=color)
        d.text((x1 + x2) / 2, y - 1.9, bottom, size=8.4, color=P["dim"])

    L, R = 24.6, 59.4
    d.text(42, 46.2, "작업기가 먼저 말할 때", size=9, color=P["dim"], style="italic")
    msg(39, L, R, '명령: "살포량 칸을 120으로 바꿔라"',
        "Change Numeric Value (A8) · PGN 0xE700", P["accent"])
    msg(31, R, L, '응답: "바꿨다" (오류 코드 0)',
        "같은 첫 바이트 A8 · PGN 0xE600", P["dim"], ls="--")

    d.text(42, 25, "VT가 먼저 말할 때", size=9, color=P["dim"], style="italic")
    msg(18, R, L, '활성화 메시지: "버튼 20이 눌렸다"',
        "Button Activation (01) · PGN 0xE600", P["orange"])
    msg(10, L, R, '응답: "받았다" (받은 내용 반향)',
        "같은 첫 바이트 01 · PGN 0xE700", P["dim"], ls="--")

    d.arrow(86.6, 27.4, 78.4, 27.4, color=P["orange"], lw=1.5)
    d.text(82.5, 29.2, "누름", size=8.6, color=P["orange"])
    d.arrow(78.4, 22.6, 86.6, 22.6, color=P["accent"], lw=1.5)
    d.text(82.5, 20.8, "표시", size=8.6, color=P["accent"])


diagram("36-two-way-dialogue", draw, w=12, h=6, xmax=100, ymax=50)
