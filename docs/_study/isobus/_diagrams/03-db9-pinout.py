"""CH3 §7 DB9 Female 커넥터 핀아웃 (light/dark PNG)."""
from _common import diagram

# 핀 번호 -> (신호명, 색 키)
PINS = {
    1: ("NC", "edge"),
    2: ("CAN_L", "orange"),
    3: ("GND", "dim"),
    4: ("NC", "edge"),
    5: ("CAN_SHLD", "violet"),
    6: ("GND", "dim"),
    7: ("CAN_H", "accent"),
    8: ("NC", "edge"),
    9: ("CAN_V+", "text"),
}

TOP_ROW = [1, 2, 3, 4, 5]     # 상단 5핀
BOTTOM_ROW = [6, 7, 8, 9]     # 하단 4핀


def draw(d):
    P = d.P
    ax = d.ax

    body_x, body_y, body_w, body_h = 15, 20, 70, 18
    d.box(body_x, body_y, body_w, body_h, P["gray"], ec=P["edge"])
    d.text(body_x + body_w / 2, body_y + body_h + 3, "DB9 Female (장비 측)", size=10.5, color=P["text"])

    top_y = body_y + body_h * 0.68
    bot_y = body_y + body_h * 0.32

    top_xs = [body_x + body_w * (i + 1) / (len(TOP_ROW) + 1) for i in range(len(TOP_ROW))]
    bot_xs = [body_x + body_w * (i + 1) / (len(BOTTOM_ROW) + 1) for i in range(len(BOTTOM_ROW))]

    for pin, x in zip(TOP_ROW, top_xs):
        name, ck = PINS[pin]
        tc = P["dim"] if name == "NC" else P[ck]
        ax.plot([x], [top_y], marker="o", ms=11, mfc=P["bg"], mec=P[ck], mew=2, zorder=5)
        d.text(x, top_y, str(pin), size=8, color=P["text"], weight="bold")
        d.text(x, top_y + 5, name, size=8.5, color=tc)

    for pin, x in zip(BOTTOM_ROW, bot_xs):
        name, ck = PINS[pin]
        tc = P["dim"] if name == "NC" else P[ck]
        ax.plot([x], [bot_y], marker="o", ms=11, mfc=P["bg"], mec=P[ck], mew=2, zorder=5)
        d.text(x, bot_y, str(pin), size=8, color=P["text"], weight="bold")
        d.text(x, bot_y - 5, name, size=8.5, color=tc)

    # 범례
    legend_items = [
        ("CAN_H", "accent"),
        ("CAN_L", "orange"),
        ("GND", "dim"),
        ("CAN_SHLD", "violet"),
        ("CAN_V+", "text"),
        ("NC", "edge"),
    ]
    lx = 12
    ly = body_y - 8
    step = 14.5
    for i, (label, ck) in enumerate(legend_items):
        cx = lx + i * step
        ax.plot([cx], [ly], marker="o", ms=8, mfc=P["bg"], mec=P[ck], mew=2, zorder=5)
        d.text(cx + 2.5, ly, label, size=7.5, color=P["dim"], ha="left")


diagram("03-db9-pinout", draw, w=12, h=6, xmax=100, ymax=50)
