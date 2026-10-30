"""CH14 §6 Working Set 정의 누락 -> 재요청 -> 재정의 시퀀스 (light/dark PNG)."""
from _common import diagram

M_X, SP_X = 24, 76
LOST_END = 62


def message(d, y, x1, x2, label, color=None, ls="-"):
    d.arrow(x1, y, x2, y, color=color, ls=ls)
    d.text((M_X + SP_X) / 2, y + 1.7, label, size=9.5)


def note(d, y, label):
    d.box(SP_X - 15, y - 2.4, 30, 4.8, d.P["chip"], ec=d.P["accent"])
    d.text(SP_X, y, label, size=9)


def gap_label(d, y1, y2, label):
    x = 9
    d.arrow(x, y1, x, y2, color=d.P["dim"], lw=1.1, style="<->")
    d.text(x + 1.2, (y1 + y2) / 2, label, size=8.5, color=d.P["dim"], ha="left")


def draw(d):
    P = d.P
    lifelines = {M_X: [(57, 2)], SP_X: [(57, 36.6), (31.4, 6.6)]}
    for x, label in ((M_X, "Working Set Master\n(SA 0x90)"),
                     (SP_X, "Service provider\n(VT, SA 0x26)")):
        d.box(x - 13, 57, 26, 6, P["blue"])
        d.text(x, 60, label, size=10, weight="bold")
        for y1, y2 in lifelines[x]:
            d.arrow(x, y1, x, y2, color=P["edge"], lw=1.1, style="-", ls="--")

    message(d, 52, M_X, SP_X, "WS Master (65037)  멤버 수 = 3")
    message(d, 46, M_X, LOST_END, "WS Member (65036)  NAME_L", color=P["orange"], ls="--")
    d.text(LOST_END + 2.2, 46, "x  수신 실패", size=9.5, color=P["orange"], ha="left")
    message(d, 40, M_X, SP_X, "WS Member (65036)  NAME_R")
    gap_label(d, 46, 40, "100 ms")
    note(d, 34, "350 ms 경과: member 1개 < 2개")

    message(d, 27, SP_X, M_X, "Request (59904)  PGN 65037, DA 0x90")
    message(d, 21, M_X, SP_X, "WS Master (65037)  멤버 수 = 3")
    gap_label(d, 27, 21, "<= 200 ms (Tr)")
    message(d, 15, M_X, SP_X, "WS Member (65036)  NAME_L")
    message(d, 9, M_X, SP_X, "WS Member (65036)  NAME_R")
    gap_label(d, 15, 9, "100 ms")
    note(d, 4, "350 ms 경과: 2개 = 3 - 1, 정의 완료")


diagram("14-ws-sequence", draw, w=12, h=7.6, xmax=100, ymax=64)
