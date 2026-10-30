"""CH18 §9 TC 연결 초기화·유지·끊김 시퀀스 (Part 10 Figure 2 재구성, light/dark PNG)."""
from _common import diagram

CX, TX = 24, 78


def msg(d, y, label, to_tc=True, color=None, ls="-"):
    x1, x2 = (CX, TX) if to_tc else (TX, CX)
    d.arrow(x1, y, x2, y, color=color or d.P["accent"], ls=ls)
    d.text((CX + TX) / 2, y + 1.1, label, size=8.8)


def side(d, x, y, label, color, w=17, h=2.6):
    d.box(x - w / 2, y - h / 2, w, h, d.P[color])
    d.text(x, y, label, size=8.4)


def bracket(d, x, y1, y2, label):
    P = d.P
    d.arrow(x, y1, x, y2, color=P["dim"], lw=1.2, style="-")
    d.arrow(x, y1, x + 1.2, y1, color=P["dim"], lw=1.2, style="-")
    d.arrow(x, y2, x + 1.2, y2, color=P["dim"], lw=1.2, style="-")
    d.text(x - 4.6, (y1 + y2) / 2, label, size=8.4, color=P["dim"])


def draw(d):
    P = d.P
    for x in (CX, TX):
        d.ax.plot([x, x], [66, 3], color=P["edge"], lw=1.0, zorder=0.5)

    d.box(CX - 11, 66, 22, 4.4, P["blue"])
    d.text(CX, 68.2, "TC 클라이언트", size=11, weight="bold")
    d.box(TX - 11, 66, 22, 4.4, P["green"])
    d.text(TX, 68.2, "TC / DL", size=11, weight="bold")

    side(d, CX, 62.5, "Address Claim 완료", "gray")
    side(d, TX, 62.5, "Address Claim 완료", "gray")
    side(d, CX, 59, "6 s 대기", "chip")
    side(d, TX, 59, "6 s 대기", "chip")

    msg(d, 55, "TC Status (2 s 주기, 전역)", to_tc=False)
    msg(d, 51.5, "Working Set Master (+Member)")
    msg(d, 48, "Client Task (2 s 주기 시작)")
    msg(d, 44.5, "Request Version")
    msg(d, 41.5, "Version", to_tc=False)
    msg(d, 38, "Request Version", to_tc=False)
    msg(d, 35, "Version")
    bracket(d, 12, 34, 45.5, "버전 교환\n(v4 의무)")
    msg(d, 31.5, "(선택) Language 요청", color=P["violet"], ls="--")
    msg(d, 28.5, "Language", to_tc=False, color=P["violet"], ls="--")

    d.box(CX + 3, 21.5, TX - CX - 6, 5, P["purple"])
    d.text((CX + TX) / 2, 24, "DDOP 확인 · 전송 · Activate  (20장)", size=9)
    side(d, TX + 11, 24, "TC Status [Busy]", "brown", w=16)
    msg(d, 19, "Object-pool Activate Response", to_tc=False)
    msg(d, 15, "measurement 명령", to_tc=False)
    msg(d, 11.5, "process data 값")

    side(d, TX, 6.5, "Client Task 6 s 끊김\nDeviceAllocation 닫음", "brown", w=22, h=4.4)
    side(d, CX, 6.5, "TC Status 6 s 끊김\nprocess data 송신 중단", "brown", w=22, h=4.4)


diagram("18-connection-sequence", draw, w=12, h=9.5, xmax=100, ymax=72)
