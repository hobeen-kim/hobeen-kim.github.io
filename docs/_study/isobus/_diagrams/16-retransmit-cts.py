"""16장 4절: 패킷 2가 깨졌을 때 수신 측이 CTS로 2번만 다시 요청하고 이어 받는 순서 (light/dark PNG)."""
from _common import diagram

XO, XR = 30, 70


def draw(d):
    P = d.P
    top, bottom = 76, 3

    for x, name in ((XO, "송신 측"), (XR, "수신 측")):
        d.box(x - 9, top, 18, 6, P["blue"])
        d.text(x, top + 3, name, size=10)
        d.ax.plot([x, x], [bottom, top], color=P["edge"], lw=1.3)

    def msg(y, label, to_right=True, color=None, note=None, note_color=None, broken=False):
        x0, x1 = (XO, XR) if to_right else (XR, XO)
        c = color or (P["accent"] if to_right else P["orange"])
        d.arrow(x0, y, x1, y - 1.6, lw=1.6, color=c, ls=(0, (4, 3)) if broken else "-")
        d.text((XO + XR) / 2, y + 1.3, label, size=9, color=None if to_right else P["orange"])
        if broken:
            xm, ym = XR - 4, y - 1.45
            for dy in (1.3, -1.3):
                d.ax.plot([xm - 1.3, xm + 1.3], [ym - dy, ym + dy], color=P["orange"], lw=2.2)
        if note:
            d.text(XR + 3.5, y - 0.8, note, size=8.4, color=note_color or P["dim"], ha="left")

    msg(71, "RTS (23 byte, 4 패킷)")
    msg(64, "CTS (2, 1)", to_right=False, note="2개 보내라, 1번부터")
    msg(57, "DT 1")
    msg(52, "DT 2", broken=True, note="2번이 깨짐", note_color=P["orange"])
    msg(44, "CTS (1, 2)", to_right=False, note="2번만 다시", note_color=P["violet"])
    msg(37, "DT 2 (다시)")
    msg(29, "CTS (2, 3)", to_right=False,
        note="3번부터 2개\n= 1·2번은 잘 받았다는 확인", note_color=P["violet"])
    msg(21, "DT 3")
    msg(16, "DT 4 (마지막)")
    msg(8, "EndOfMsgACK (23 byte, 4 패킷)", to_right=False, note="다 받았다")


diagram("16-retransmit-cts", draw, w=10, h=7.4, xmax=100, ymax=84)
