"""15장 4절: CMDT 전송 순서. RTS, CTS로 5개씩 허락, TP.DT, EndOfMsgACK (light/dark PNG)."""
from _common import diagram

XO, XR = 32, 72


def draw(d):
    P = d.P
    top, bottom = 82, 3

    for x, name in ((XO, "송신 ECU\n(SA=0x23)"), (XR, "수신 ECU\n(SA=0x82)")):
        d.box(x - 10, top, 20, 7, P["blue"])
        d.text(x, top + 3.5, name, size=10)
        d.ax.plot([x, x], [bottom, top], color=P["edge"], lw=1.3)

    def msg(y, label, to_right=True, sub=None, color=None, size=9):
        x0, x1 = (XO, XR) if to_right else (XR, XO)
        d.arrow(x0, y, x1, y - 1.6, lw=1.6, color=color or P["accent"])
        d.text((XO + XR) / 2, y + 1.3, label, size=size, color=color)
        if sub:
            d.text((XO + XR) / 2, y - 3.1, sub, size=8.3, color=color or P["dim"])

    msg(77, "RTS (Request To Send)", sub="총 크기=200 byte, 패킷 수=29, PGN=정보 PGN")
    msg(68.5, "CTS (Clear To Send)", to_right=False, color=P["orange"],
        sub="허용 패킷 수=5, 시작 시퀀스=1")
    ys = [60, 55.5, 51, 46.5, 42]
    for i, y in enumerate(ys, start=1):
        msg(y, f"TP.DT #{i} (Seq={i})", size=8.6)
    xb = XR + 3
    d.ax.plot([xb, xb], [ys[0] - 1.6, ys[-1] - 1.6], color=P["violet"], lw=1.2)
    for y in (ys[0] - 1.6, ys[-1] - 1.6):
        d.ax.plot([xb - 0.7, xb + 0.7], [y, y], color=P["violet"], lw=1.2)
    d.text(xb + 1.2, (ys[0] + ys[-1]) / 2 - 1.6, "CTS가 허락한\n5개", size=8.4,
           color=P["violet"], ha="left")

    msg(35, "CTS (Clear To Send)", to_right=False, color=P["orange"],
        sub="허용 패킷 수=5, 시작 시퀀스=6")
    msg(26.5, "TP.DT #6 (Seq=6)", size=8.6)
    d.ax.plot([(XO + XR) / 2] * 3, [21.5, 19.7, 17.9], "o", ms=2.4, color=P["dim"])
    d.text((XO + XR) / 2 + 2, 19.7, "계속", size=8.3, color=P["dim"], ha="left")
    msg(14, "TP.DT #29 (Seq=29)", size=8.6)
    msg(7.5, "EndOfMsgACK (전송 완료 확인)", to_right=False, color=P["orange"])


diagram("15-cmdt-sequence", draw, w=10, h=8.6, xmax=100, ymax=90)
