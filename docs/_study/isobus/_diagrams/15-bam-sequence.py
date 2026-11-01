"""15장 3절: BAM 전송 순서와 대기 시간, 수신 측 타임아웃 (light/dark PNG)."""
from _common import diagram

XO, XR = 33, 72


def draw(d):
    P = d.P
    top, bottom = 62, 3

    for x, name in ((XO, "송신 ECU"), (XR, "CAN 버스\n(모든 수신 ECU)")):
        d.box(x - 10, top, 20, 6.5, P["blue"])
        d.text(x, top + 3.25, name, size=10)
        d.ax.plot([x, x], [bottom, top], color=P["edge"], lw=1.3)

    def msg(y, label, sub=None):
        d.arrow(XO, y, XR, y - 2.2, lw=1.6)
        d.text((XO + XR) / 2, y + 1.6, label, size=9)
        if sub:
            d.text((XO + XR) / 2, y - 3.8, sub, size=8.3, color=P["dim"])

    def wait(y_from, y_to, label="10~200 ms 대기"):
        x = XO - 3
        d.ax.plot([x, x], [y_to, y_from], color=P["violet"], lw=1.2)
        for y in (y_from, y_to):
            d.ax.plot([x - 0.7, x + 0.7], [y, y], color=P["violet"], lw=1.2)
        d.text(x - 1.2, (y_from + y_to) / 2, label, size=8.4, color=P["violet"], ha="right")

    msg(57, "TP.CM_BAM (PGN 60416)", "총 크기=200 byte, 패킷 수=29, PGN=정보 PGN")
    wait(56.7, 47.3)
    msg(47, "TP.DT #1 (Seq=1, 7 byte)")
    wait(46.7, 38.3)
    msg(38, "TP.DT #2 (Seq=2, 7 byte)")
    wait(37.7, 29.3)
    msg(29, "TP.DT #3 (Seq=3, 7 byte)")
    d.ax.plot([(XO + XR) / 2] * 3, [23.5, 21.5, 19.5], "o", ms=2.4, color=P["dim"])
    msg(14, "TP.DT #N (Seq=N, 나머지)", "마지막 패킷, 전송 완료")

    xr = XR + 3
    d.ax.plot([xr, xr], [38 - 2.2, 29 - 2.2], color=P["orange"], lw=1.2)
    for y in (38 - 2.2, 29 - 2.2):
        d.ax.plot([xr - 0.7, xr + 0.7], [y, y], color=P["orange"], lw=1.2)
    d.text(xr + 1.2, 31.3, "T1 750 ms\n이 안에 다음 패킷이\n안 오면 재조립 포기", size=8.4,
           color=P["orange"], ha="left")
    d.text(xr + 1.2, 11.8, "각 수신 ECU가\n따로 재조립\n(응답은 보내지 않음)", size=8.4,
           color=P["dim"], ha="left")


diagram("15-bam-sequence", draw, w=10, h=7.0, xmax=100, ymax=70)
