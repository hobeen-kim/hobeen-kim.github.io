"""CH14 §10 DM1 송신 시점 — 이벤트·1초 주기·간헐 고장 억제 (light/dark PNG)."""
from _common import diagram

X0, SCALE = 13, 12.4
ACTIVE = {
    "DTC A": ("blue", [(0.0, 3.3)]),
    "DTC B": ("green", [(2.4, 5.6)]),
    "DTC C": ("brown", [(4.2, 4.5), (4.6, 4.8)]),
}
SENT = [
    (0.0, "event", "{A}"), (1.0, "periodic", "{A}"), (2.0, "periodic", "{A}"),
    (2.4, "event", "{A,B}"), (3.0, "periodic", "{A,B}"), (3.3, "event", "{B}"),
    (4.0, "periodic", "{B}"), (4.2, "event", "{B,C}"), (5.0, "periodic", "{B}"),
    (5.6, "event", "{ }"),
]
SUPPRESSED = [4.5, 4.6, 4.8]


def tx(t):
    return X0 + t * SCALE


def draw(d):
    P = d.P
    rows = {"DTC A": 37, "DTC B": 31, "DTC C": 25}
    for name, y in rows.items():
        color, spans = ACTIVE[name]
        d.text(2, y, name, size=9.5, weight="bold", ha="left")
        for t1, t2 in spans:
            d.box(tx(t1), y - 1.4, tx(t2) - tx(t1), 2.8, P[color], lw=1.0, r=0.005)

    y_dm1 = 14
    d.text(2, y_dm1, "DM1 송신", size=9.5, weight="bold", ha="left")
    for t, kind, label in SENT:
        color = P["accent"] if kind == "event" else P["violet"]
        d.arrow(tx(t), y_dm1 - 2.2, tx(t), y_dm1 + 2.2, color=color, lw=2.4, style="-")
        ly = y_dm1 + 4.0 if kind == "event" else y_dm1 - 4.0
        d.text(tx(t), ly, label, size=8.5, color=color, weight="bold")
    for t in SUPPRESSED:
        d.text(tx(t), y_dm1, "x", size=11, color=P["orange"], weight="bold")
    d.arrow(tx(5.6), y_dm1, tx(6.6), y_dm1, color=P["dim"], lw=1.1, style="-", ls="--")
    d.text(tx(6.1), y_dm1 + 1.6, "요청 시에만", size=8, color=P["dim"])

    axis_y = 5.5
    d.arrow(tx(0), axis_y, tx(6.7), axis_y, color=P["edge"], lw=1.1)
    for s in range(7):
        d.arrow(tx(s), axis_y - 0.5, tx(s), axis_y + 0.5, color=P["edge"], lw=1.1, style="-")
        d.text(tx(s), axis_y - 2.0, f"{s} s", size=8.5, color=P["dim"])

    lx, ly = 72, 44
    for i, (color, label) in enumerate(((P["accent"], "이벤트 송신"),
                                        (P["violet"], "1초 주기 송신"))):
        d.arrow(lx + i * 9.5, ly - 1, lx + i * 9.5, ly + 1, color=color, lw=2.4, style="-")
        d.text(lx + i * 9.5 + 0.8, ly, label, size=8, color=color, ha="left")
    d.text(lx + 19, ly, "x", size=11, color=P["orange"], weight="bold")
    d.text(lx + 19.8, ly, "보고 미룸(1회/s 제한)", size=8, color=P["orange"], ha="left")


diagram("14-dm1-timeline", draw, w=14, h=6.4, xmax=100, ymax=47)
