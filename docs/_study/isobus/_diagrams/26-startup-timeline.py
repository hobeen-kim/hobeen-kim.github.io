"""26장 3절 전원 ON부터 정상 동작까지의 타임라인, 1.6~6.4 s 구간은 접어서 그린다 (light/dark PNG)."""
from _common import diagram

X0, SCALE = 20, 36.0
CUT_FROM, CUT_TO, CUT_W = 1.6, 6.4, 6


def tx(t):
    if t <= CUT_FROM:
        return X0 + t * SCALE
    if t >= CUT_TO:
        return X0 + CUT_FROM * SCALE + CUT_W + (t - CUT_TO) * SCALE
    return X0 + CUT_FROM * SCALE + CUT_W * (t - CUT_FROM) / (CUT_TO - CUT_FROM)


ROWS = [
    ("전원", 52),
    ("주소 정하기", 43),
    ("VT 확인·화면", 34),
    ("Working Set\n선언", 25),
    ("TC 연결", 16),
]


def bar(d, t1, t2, y, label, fc, ls="-", above=True):
    P = d.P
    d.box(tx(t1), y - 1.6, tx(t2) - tx(t1), 3.2, fc, lw=1.0, r=0.005)
    if ls != "-":
        d.ax.plot([tx(t1), tx(t2)], [y, y], color=P["dim"], ls=(0, (3, 3)), lw=1.0, zorder=3)
    ly = y + 3.0 if above else y - 3.0
    d.text((tx(t1) + tx(t2)) / 2, ly, label, size=8.2)


def milestone(d, t, y, label, ha="left", dx=1.3):
    P = d.P
    d.ax.plot([tx(t)], [y], marker="D", markersize=7, color=P["accent"], zorder=6)
    d.text(tx(t) + (dx if ha == "left" else -dx), y, label, size=8.2,
           color=P["accent"], weight="bold", ha=ha)


def draw(d):
    P = d.P
    for name, y in ROWS:
        d.text(2, y, name, size=9.4, weight="bold", ha="left")
        d.ax.plot([X0 - 1, tx(7.25)], [y, y], color=P["edge"], lw=0.5, alpha=0.5, zorder=1)

    bar(d, 0.0, 0.05, 52, "", P["gray"])
    d.text(tx(0.05) + 1.2, 52, "전원 ON, 버스 안정화 (0~50 ms)", size=8.2, ha="left")

    bar(d, 0.05, 0.30, 43, "Request 후 대기\n250 ms + RTxD", P["blue"])
    milestone(d, 0.30, 43, "", ha="left")
    d.text(tx(0.30), 39.6, "Address Claimed 송신 (~300 ms)", size=8.2, color=P["accent"])
    bar(d, 0.30, 0.55, 43, "경합 감시\n250 ms", P["blue"])
    milestone(d, 0.55, 43, "주소 확정 (~550 ms)")

    bar(d, 0.55, 0.60, 34, "", P["purple"])
    d.text(tx(0.575), 37.2, "VT Status 수신\n(master가 먼저 기다림)", size=8.2)
    bar(d, 1.20, 1.50, 34, "Object Pool\n전송", P["purple"])
    milestone(d, 1.50, 34, "화면 표시 (~1.5 s)", ha="left")

    bar(d, 0.60, 0.65, 25, "", P["green"])
    d.text(tx(0.55), 21.3, "Master 메시지\n(PGN 65037)", size=8.2)
    bar(d, 0.65, 0.95, 25, "Member 메시지\n(PGN 65036, 100 ms 간격)", P["green"])
    milestone(d, 1.00, 25, "구성 완료 (~1 s)")

    bar(d, 0.55, 6.55, 16, "", P["chip"], ls="--")
    d.text(tx(1.05), 12.6, "주소 클레임 뒤 6 s 대기", size=8.2, color=P["dim"])
    bar(d, 6.55, 7.00, 16, "Device Descriptor\n교환", P["brown"], above=False)
    milestone(d, 7.00, 16, "정상 동작\n(~7 s)", ha="left")

    axis_y = 6
    d.ax.plot([tx(0), tx(CUT_FROM)], [axis_y, axis_y], color=P["edge"], lw=1.1)
    d.arrow(tx(CUT_TO), axis_y, tx(7.3), axis_y, color=P["edge"], lw=1.1)
    for x in (tx(CUT_FROM) + 1.6, tx(CUT_TO) - 1.6):
        d.ax.plot([x - 0.8, x + 0.8], [axis_y - 1.0, axis_y + 1.0], color=P["edge"], lw=1.1)
    d.text((tx(CUT_FROM) + tx(CUT_TO)) / 2, axis_y, "...", size=9, color=P["dim"])
    for t in (0, 0.5, 1.0, 1.5, 6.5, 7.0):
        d.ax.plot([tx(t), tx(t)], [axis_y - 0.6, axis_y + 0.6], color=P["edge"], lw=1.1)
        d.text(tx(t), axis_y - 2.4, f"{t:g} s", size=8.2, color=P["dim"])


diagram("26-startup-timeline", draw, w=14, h=6.4, xmax=126, ymax=57)
