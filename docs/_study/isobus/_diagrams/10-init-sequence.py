"""CH10 §10 네트워크 초기화 시퀀스 3종: Part 5 Figure 4·5·10 (light/dark PNG)."""
from _common import diagram


def lifeline(d, x, top, bottom, name):
    P = d.P
    d.box(x - 6.5, top, 13, 4.6, P["gray"], ec=P["edge"])
    d.text(x, top + 2.3, name, size=9, weight="bold")
    d.ax.plot([x, x], [bottom, top], color=P["edge"], ls=(0, (4, 3)), lw=1.0, zorder=1)


def msg(d, x1, x2, y, label, color=None, above=True, size=8):
    P = d.P
    color = color or P["accent"]
    d.arrow(x1, y, x2, y, color=color)
    ly = y + 1.9 if above else y - 1.9
    d.text((x1 + x2) / 2, ly, label, size=size, color=P["text"])


def bracket(d, x, y_top, y_bot, label, side="left"):
    P = d.P
    tick = 1.2 if side == "left" else -1.2
    d.ax.plot([x, x], [y_bot, y_top], color=P["orange"], lw=1.4, zorder=3)
    d.ax.plot([x, x + tick], [y_top, y_top], color=P["orange"], lw=1.4, zorder=3)
    d.ax.plot([x, x + tick], [y_bot, y_bot], color=P["orange"], lw=1.4, zorder=3)
    tx = x - 1.0 if side == "left" else x + 1.0
    d.text(tx, (y_top + y_bot) / 2, label, size=8, color=P["orange"],
           ha="right" if side == "left" else "left")


def draw(d):
    P = d.P
    top, bottom = 56, 8

    # a) 경합 없음 (Figure 4)
    cf, bus = 20, 40
    d.text(30, 64, "a) 경합 없음", size=10, weight="bold", color=P["accent"])
    lifeline(d, cf, top, bottom, "CF (X)")
    lifeline(d, bus, top, bottom, "버스")
    msg(d, cf, bus, 50, "Request for AC\nSA=254, DA=255/X")
    bracket(d, cf - 1.5, 50, 34, "250 ms\n+ RTxD")
    msg(d, cf, bus, 34, "Address Claimed\nSA=X")
    bracket(d, cf - 1.5, 34, 21, "250 ms")
    for y in (21, 19, 17):
        d.arrow(cf, y, bus, y, color=P["dim"])
    d.text(30, 13.5, "일반 메시지 SA=X", size=8, color=P["dim"])

    # b) X 사용 중 -> Q (Figure 5)
    cf, bus = 67, 87
    d.text(77, 64, "b) X 사용 중 -> Q 선택", size=10, weight="bold", color=P["accent"])
    lifeline(d, cf, top, bottom, "CF (X)")
    lifeline(d, bus, top, bottom, "버스")
    msg(d, cf, bus, 50, "Request for AC\nSA=254, DA=255")
    for y in (43, 41.5, 40):
        d.arrow(bus, y, cf, y, color=P["violet"])
    d.text(77, 45.5, "AC: SA=X, Y, Z", size=8, color=P["violet"])
    bracket(d, cf - 1.5, 50, 34, "250 ms\n+ RTxD")
    d.text(77, 36.5, "새 initial address Q", size=8, color=P["orange"])
    msg(d, cf, bus, 31, "Address Claimed\nSA=Q")
    bracket(d, cf - 1.5, 31, 18, "250 ms")
    for y in (18, 16, 14):
        d.arrow(cf, y, bus, y, color=P["dim"])
    d.text(77, 10.5, "일반 메시지 SA=Q", size=8, color=P["dim"])

    # c) non-configurable, 주소 없음 (Figure 10)
    cf, bus = 114, 134
    d.text(124, 64, "c) non-configurable: 주소 없음", size=10, weight="bold", color=P["accent"])
    lifeline(d, cf, top, bottom, "CF (X)")
    lifeline(d, bus, top, bottom, "버스")
    msg(d, bus, cf, 50, "Request for AC\nSA=254, DA=255", color=P["violet"])
    for y in (43, 41.5, 40):
        d.arrow(bus, y, cf, y, color=P["violet"])
    d.text(124, 45.5, "AC: SA=X, Y, Z", size=8, color=P["violet"])
    bracket(d, cf - 1.5, 40, 28, "RTxD")
    msg(d, cf, bus, 28, "Cannot Claim\nSA=254, NAME", color=P["orange"])
    d.text(124, 20, "이후: 요청 응답·\ncommanded-address\n응답만 송신", size=8, color=P["dim"])


diagram("10-init-sequence", draw, w=14, h=6.5, xmax=142, ymax=68)
