"""17장 2절: ETP 전송 순서. RTS, CTS, CTS 묶음마다 DPO와 ETP.DT 반복, EndOfMsgACK (light/dark PNG)."""
from _common import diagram

XO, XR = 30, 70


def draw(d):
    P = d.P
    top, bottom = 86, 3

    for x, name in ((XO, "송신 ECU"), (XR, "수신 ECU")):
        d.box(x - 9, top, 18, 6, P["blue"])
        d.text(x, top + 3, name, size=10)
        d.ax.plot([x, x], [bottom, top], color=P["edge"], lw=1.3)

    def msg(y, label, to_right=True, sub=None, size=9):
        x0, x1 = (XO, XR) if to_right else (XR, XO)
        c = P["accent"] if to_right else P["orange"]
        d.arrow(x0, y, x1, y - 1.6, lw=1.6, color=c)
        d.text((XO + XR) / 2, y + 1.3, label, size=size, color=None if to_right else P["orange"])
        if sub:
            d.text((XO + XR) / 2, y - 3.1, sub, size=8.3, color=P["dim"] if to_right else P["orange"])

    msg(81, "ETP.CM_RTS (PGN 51200)", sub="총 크기=50000 byte, PGN=오브젝트 풀 PGN")
    msg(72, "ETP.CM_CTS (PGN 51200)", to_right=False, sub="허용 패킷 수=255, 시작 패킷=1")

    d.box(XO - 14, 15.5, XR - XO + 30, 48, P["chip"], lw=1.2)
    d.text(XO - 12.5, 61.2, "255 패킷씩 반복", size=8.8, weight="bold", ha="left", color=P["violet"])

    msg(57, "ETP.CM_DPO (PGN 51200)", sub="기준 오프셋 선언")
    msg(48, "ETP.DT #1 (PGN 50944)", size=8.6)
    msg(43, "ETP.DT #2 (PGN 50944)", size=8.6)
    d.ax.plot([(XO + XR) / 2] * 3, [37.8, 36.0, 34.2], "o", ms=2.4, color=P["dim"])
    d.text((XO + XR) / 2 + 2, 36.0, "255 패킷", size=8.3, color=P["dim"], ha="left")
    msg(30, "ETP.DT #255 (PGN 50944)", size=8.6)
    msg(23, "ETP.CM_CTS", to_right=False, sub="허용 패킷 수=255, 시작 패킷=256")

    msg(9, "ETP.CM_EndOfMsgACK (PGN 51200)", to_right=False)


diagram("17-etp-flow", draw, w=10, h=8.0, xmax=100, ymax=94)
