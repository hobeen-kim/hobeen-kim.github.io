"""15장 5절: RTS 뒤 CMDT 연결의 세 가지 결말. 정상, 수신 측 Abort, 송신 측 타임아웃 Abort (light/dark PNG)."""
from _common import diagram

PANEL_W = 31.5
PANELS = [1.0, 34.25, 67.5]


def draw(d):
    P = d.P
    top, bottom = 47, 3
    titles = ["정상 흐름", "수신 측 오류 (버퍼 부족 등)", "타임아웃 (CTS가 오지 않음)"]

    for px, title in zip(PANELS, titles):
        d.box(px, 1.5, PANEL_W, 56, P["chip"])
        d.text(px + 1.5, 54.6, title, size=10, weight="bold", ha="left")
        xo, xr = px + 7.5, px + PANEL_W - 7.5
        for x, name in ((xo, "송신 ECU"), (xr, "수신 ECU")):
            d.box(x - 5.5, top, 11, 4.6, P["blue"])
            d.text(x, top + 2.3, name, size=8.8)
            d.ax.plot([x, x], [bottom, top], color=P["edge"], lw=1.2)

    def lanes(i):
        px = PANELS[i]
        return px + 7.5, px + PANEL_W - 7.5

    def msg(i, y, label, to_right=True, color=None, size=8.4):
        xo, xr = lanes(i)
        x0, x1 = (xo, xr) if to_right else (xr, xo)
        d.arrow(x0, y, x1, y - 1.4, lw=1.5, color=color or P["accent"])
        d.text((xo + xr) / 2, y + 1.3, label, size=size, color=color)

    # 1. 정상 흐름
    xo, xr = lanes(0)
    msg(0, 42, "RTS (총 크기, 패킷 수, PGN)")
    msg(0, 35.5, "CTS (허용 N, 시작 시퀀스 1)", to_right=False, color=P["orange"])
    msg(0, 28.5, "TP.DT #1 ~ #N")
    msg(0, 21.5, "CTS (다음 묶음)", to_right=False, color=P["orange"])
    lx = xo - 2.6
    d.ax.plot([lx, lx], [30.2, 19.4], color=P["violet"], lw=1.2)
    for y in (30.2, 19.4):
        d.ax.plot([lx - 0.6, lx + 0.6], [y, y], color=P["violet"], lw=1.2)
    d.text(lx - 0.6, 15.6, "N 패킷씩\n반복", size=8, color=P["violet"])
    msg(0, 9, "EndOfMsgACK", to_right=False, color=P["orange"])

    # 2. 수신 측 오류
    xo, xr = lanes(1)
    msg(1, 42, "RTS (총 크기, 패킷 수, PGN)")
    msg(1, 33, "Abort (오류 코드)", to_right=False, color=P["orange"])
    d.box(xo + 1.5, 15, xr - xo - 3, 9, P["gray"])
    d.text((xo + xr) / 2, 19.5, "연결 종료\n송신 측은 재시도 여부를 정함", size=8.3)

    # 3. 타임아웃
    xo, xr = lanes(2)
    msg(2, 42, "RTS (총 크기, 패킷 수, PGN)")
    sx = xo - 2.6
    d.ax.plot([sx, sx], [42, 18], color=P["violet"], lw=1.2)
    for y in (42, 18):
        d.ax.plot([sx - 0.6, sx + 0.6], [y, y], color=P["violet"], lw=1.2)
    d.text((xo + xr) / 2, 30, "1250 ms 안에\nCTS가 오지 않음", size=8.3, color=P["violet"])
    msg(2, 18, "Abort (타임아웃)", color=P["orange"])


diagram("15-cmdt-endings", draw, w=13, h=6.0, xmax=100, ymax=60)
