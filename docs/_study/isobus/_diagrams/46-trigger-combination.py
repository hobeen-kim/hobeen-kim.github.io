"""CH46 §8 시간 간격 5 s + on change 10 L/ha를 함께 건 경우의 송신 시점 (light/dark PNG)."""
from _common import diagram

TX0, TX1 = 12, 94           # 0 s ~ 20 s
VY0, VY1 = 14, 38           # 196 ~ 216 L/ha
VMIN, VMAX = 196, 216

STEPS = [(0, 200), (8, 212), (16, 206), (20, 206)]
SENDS = [  # (시각, 종류, 라벨)
    (0, "start", "시작 값"),
    (5, "time", "시간 5 s"),
    (8, "change", "변화 12\n(10 이상)"),
    (13, "time", "시간 5 s"),
    (18, "time", "시간 5 s"),
]
SKIP = (16, "변화 6\n(10 미만)\n안 보냄")
TIMERS = [(0, 5, "5 s"), (8, 13, "5 s"), (13, 18, "5 s")]


def tx(t):
    return TX0 + (TX1 - TX0) * t / 20


def vy(v):
    return VY0 + (VY1 - VY0) * (v - VMIN) / (VMAX - VMIN)


def value_at(t):
    v = STEPS[0][1]
    for st, sv in STEPS:
        if t >= st:
            v = sv
    return v


def draw(d):
    P = d.P
    d.arrow(TX0, VY0 - 2, TX1 + 3, VY0 - 2, color=P["edge"], lw=1.2)
    d.arrow(TX0, VY0 - 2, TX0, VY1 + 4, color=P["edge"], lw=1.2)
    for t in (0, 5, 10, 15, 20):
        d.arrow(tx(t), VY0 - 2.6, tx(t), VY0 - 1.4, color=P["edge"], lw=1.0, style="-")
        d.text(tx(t), VY0 - 4.2, f"{t} s", size=8.5, color=P["dim"])
    d.text(TX1 + 4, VY0 - 4.2, "시간", size=8.5, color=P["dim"], ha="left")
    for v in (200, 206, 212):
        d.text(TX0 - 1.2, vy(v), str(v), size=8.5, color=P["dim"], ha="right")
    d.text(TX0 - 1.2, VY1 + 5.5, "값 (L/ha)", size=8.5, color=P["dim"], ha="left")

    xs, ys = [], []
    for (t0, v), (t1, _) in zip(STEPS, STEPS[1:]):
        xs += [tx(t0), tx(t1)]
        ys += [vy(v), vy(v)]
    d.ax.plot(xs, ys, color=P["text"], lw=1.8, zorder=3)

    color = {"start": P["violet"], "time": P["accent"], "change": P["orange"]}
    for t, kind, label in SENDS:
        x, y = tx(t), vy(value_at(t))
        d.ax.plot([x], [y], marker="o", markersize=10, color=color[kind], zorder=6)
        if t == 0:
            d.text(x + 1.4, y + 3.0, label, size=8.5, color=color[kind], ha="left")
        else:
            d.text(x, y + 3.6, label, size=8.5, color=color[kind])
    t, label = SKIP
    x, y = tx(t), vy(value_at(t))
    d.ax.plot([x], [y], marker="x", markersize=9, mew=2, color=P["dim"], zorder=6)
    d.text(x - 1.4, vy(209), label, size=8, color=P["dim"], ha="right")

    by = 4.0
    for t0, t1, label in TIMERS:
        d.arrow(tx(t0) + 0.3, by, tx(t1) - 0.3, by, color=P["accent"], lw=1.3, style="<|-|>")
        d.text((tx(t0) + tx(t1)) / 2, by + 1.6, label, size=8, color=P["accent"])
    d.arrow(tx(5) + 0.3, by, tx(8) - 0.3, by, color=P["dim"], lw=1.2, style="-", ls="--")
    d.text((tx(5) + tx(8)) / 2, by - 1.9, "8 s에 타이머 다시 시작", size=8, color=P["dim"])


diagram("46-trigger-combination", draw, w=12, h=5.4, xmax=100, ymax=45)
