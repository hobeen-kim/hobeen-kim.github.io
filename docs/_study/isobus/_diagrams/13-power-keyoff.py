"""CH13 §11 키 오프 뒤 전원 유지 요청과 ECU_PWR·PWR 차단 시퀀스 (light/dark PNG)."""
from _common import diagram

XT, XC = 30, 74


def msg(d, x1, x2, y, label, color=None):
    d.arrow(x1, y, x2, y, color=color)
    d.text((x1 + x2) / 2, y + 1.2, label, size=9)


def bracket(d, x, y_top, y_bot, label, side="left"):
    P = d.P
    tick = 0.8 if side == "left" else -0.8
    d.arrow(x, y_top, x, y_bot, color=P["dim"], lw=1.1, style="-")
    d.arrow(x, y_top, x + tick, y_top, color=P["dim"], lw=1.1, style="-")
    d.arrow(x, y_bot, x + tick, y_bot, color=P["dim"], lw=1.1, style="-")
    lx = x - 1.0 if side == "left" else x + 1.0
    d.text(lx, (y_top + y_bot) / 2, label, size=8.5, color=P["dim"],
           ha="right" if side == "left" else "left")


def phase(d, y, label):
    P = d.P
    d.arrow(XT - 8, y, XC + 8, y, color=P["edge"], lw=1.0, style="-", ls=":")
    d.text((XT + XC) / 2, y + 1.1, label, size=8.5, color=P["dim"], weight="bold")


def event(d, y, label):
    P = d.P
    d.box(XT - 7, y - 1.4, 14, 2.8, P["brown"])
    d.text(XT, y, label, size=9, weight="bold")


def draw(d):
    P = d.P
    top = 56

    d.box(XT - 8, top - 2, 16, 4, P["blue"])
    d.text(XT, top, "TECU", size=10.5, weight="bold")
    d.box(XC - 10, top - 2, 20, 4, P["green"])
    d.text(XC, top, "전원 유지가 필요한 CF", size=10, weight="bold")
    for y1, y2 in ((top - 2.2, 23.6), (20.4, 10.6), (7.4, 4)):
        d.arrow(XT, y1, XT, y2, color=P["edge"], lw=1.0, style="-", ls="--")
    d.arrow(XC, top - 2.2, XC, 4, color=P["edge"], lw=1.0, style="-", ls="--")

    phase(d, 51.5, "Ignition On")
    msg(d, XT, XC, 48.5, "Key switch not off")
    d.text(XT - 2, 48.5, "100 ms 주기", size=8.5, color=P["dim"], ha="right")

    phase(d, 45, "Ignition Off")
    msg(d, XT, XC, 42, "Key switch off · Max time 3 min")
    d.text(XT - 2, 42, "100 ms 주기", size=8.5, color=P["dim"], ha="right")

    msg(d, XC, XT, 38, "Maintain power 5F  (ECU 01 · PWR 01)", color=P["violet"])
    msg(d, XC, XT, 34.5, "Maintain power 5F  (ECU 01 · PWR 01)", color=P["violet"])
    bracket(d, XC + 2.5, 38, 34.5, "1 s에 1회 이상", side="right")

    msg(d, XT, XC, 30.5, "Key switch off · Max time 2 min")
    d.text(XT - 2, 30.5, "1 min 경과", size=8.5, color=P["dim"], ha="right")

    msg(d, XC, XT, 26.5, "Maintain power 4F  (ECU 01 · PWR 00)", color=P["violet"])
    d.text(XC + 2.5, 26.5, "PWR 작업 끝", size=8.5, color=P["dim"], ha="left")

    event(d, 22, "PWR Off")
    bracket(d, XT - 9.5, 34.5, 22, ">= 2 s", side="left")

    msg(d, XC, XT, 18, "마지막 Maintain power 4F", color=P["violet"])

    msg(d, XT, XC, 13.5, "마지막 Key switch off")
    bracket(d, XT - 9.5, 18, 13.5, ">= 2 s", side="left")

    event(d, 9, "ECU_PWR Off")
    bracket(d, XT - 9.5, 13.5, 9, "< 100 ms", side="left")


diagram("13-power-keyoff", draw, w=12, h=8, xmax=100, ymax=60)
