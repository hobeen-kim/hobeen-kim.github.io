"""CH02 트레이스 — 하나의 trace_id로 묶인 span 시퀀스 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    actors = [
        (12, P["gray"], "Client"),
        (37, P["blue"], "API Gateway"),
        (62, P["green"], "Payment"),
        (87, P["brown"], "Inventory"),
    ]
    for x, fc, name in actors:
        d.box(x - 10, 44, 20, 5, fc)
        d.text(x, 46.5, name, size=10, weight="bold")
        d.ax.plot([x, x], [6, 44], color=P["edge"], lw=1.1,
                  ls=(0, (4, 3)), zorder=1)

    steps = [
        (39, 12, 37, "POST /checkout", "trace_id=abc123", P["accent"], "-"),
        (33, 37, 62, "charge() span", "", P["accent"], "-"),
        (27, 62, 87, "reserve_stock() span", "", P["accent"], "-"),
        (20, 87, 62, "300ms 소요", "", P["orange"], "-"),
        (14, 62, 37, "결제 완료", "", P["dim"], "--"),
        (9, 37, 12, "200 OK", "", P["dim"], "--"),
    ]
    for y, x1, x2, label, sub, color, ls in steps:
        d.arrow(x1, y, x2, y, color=color, ls=ls)
        midx = (x1 + x2) / 2
        d.text(midx, y + 1.4, label, size=9, color=color)
        if sub:
            d.text(midx, y - 1.4, sub, size=8, color=P["dim"])


diagram("02-trace-sequence", draw, w=13, h=6, ymax=50)
