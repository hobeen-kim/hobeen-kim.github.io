"""25장: 전체 작업기 정지 스위치(ISB)의 상태·전이 횟수와 놓친 정지를 찾는 과정."""
from _common import diagram, Line2D

X0, SCALE = 22, 34
HI, LO = 43, 38
FRAME_Y, FRAME_H, FRAME_W = 26.5, 6, 8.4
VERDICT_Y, AXIS_Y = 20, 9.5

FRAMES = [
    (0.0, "01 / 3", "periodic", True, "추적 시작"),
    (0.4, "00 / 4", "change", True, "정상"),
    (0.7, "01 / 4", "change", True, "정상"),
    (1.0, "01 / 4", "periodic", True, "정상"),
    (1.3, "00 / 5", "change", False, "못 받음"),
    (1.6, "01 / 5", "change", False, "못 받음"),
    (2.0, "01 / 5", "periodic", True, "오류"),
]
SWITCH_EDGES = [(0.4, LO), (0.7, HI), (1.3, LO), (1.6, HI)]


def tx(t):
    return X0 + t * SCALE


def draw(d):
    P = d.P
    d.text(1, 40.5, "스위치", size=10, ha="left")
    d.text(1, FRAME_Y + FRAME_H / 2, "버스의 ISB 메시지\n(상태 / 전이 횟수)", size=10, ha="left")
    d.text(1, VERDICT_Y, "작업기의 판정", size=10, ha="left")

    d.text(tx(0) - 1.5, HI, "Permit(01)", size=8.5, color=P["dim"], ha="right")
    d.text(tx(0) - 1.5, LO, "Stop(00)", size=8.5, color=P["dim"], ha="right")
    xs, ys, level = [tx(0)], [HI], HI
    for t, new_level in SWITCH_EDGES:
        xs += [tx(t), tx(t)]
        ys += [level, new_level]
        level = new_level
    xs.append(tx(2.25))
    ys.append(level)
    d.ax.plot(xs, ys, color=P["accent"], lw=2.2, zorder=4)

    for t, _ in SWITCH_EDGES:
        d.ax.plot([tx(t), tx(t)], [LO - 0.5, FRAME_Y + FRAME_H + 0.3],
                  color=P["edge"], lw=0.9, ls=":", zorder=1)

    for t, label, kind, received, verdict in FRAMES:
        x = tx(t)
        fc = P["blue"] if kind == "periodic" else P["purple"]
        d.box(x - FRAME_W / 2, FRAME_Y, FRAME_W, FRAME_H, fc,
              alpha=1.0 if received else 0.4)
        d.text(x, FRAME_Y + FRAME_H / 2, label, size=10,
               color=P["text"] if received else P["dim"])
        color = P["text"] if received else P["orange"]
        weight = "normal"
        if verdict == "오류":
            color, weight = P["orange"], "bold"
        d.text(x, VERDICT_Y, verdict, size=10, color=color, weight=weight)

    d.text(tx(2.0), VERDICT_Y - 4, "Stop을 못 봤는데\n횟수만 4 → 5", size=8.5, color=P["orange"])

    d.ax.plot([tx(0), tx(2.25)], [AXIS_Y, AXIS_Y], color=P["edge"], lw=1.2)
    for s in (0, 1, 2):
        d.ax.plot([tx(s), tx(s)], [AXIS_Y - 0.7, AXIS_Y + 0.7], color=P["edge"], lw=1.2)
        d.text(tx(s), AXIS_Y - 2.4, f"{s} s", size=9, color=P["dim"])

    d.legend([
        Line2D([], [], marker="s", ls="", markersize=10, color=P["blue"],
               markeredgecolor=P["edge"], label="주기 메시지(1 s마다)"),
        Line2D([], [], marker="s", ls="", markersize=10, color=P["purple"],
               markeredgecolor=P["edge"], label="변화 시 메시지"),
    ], loc="lower left", anchor=(0.0, 0.0), fontsize=9)


diagram("25-isb-transition-timeline", draw, w=12, h=5.6, xmax=100, ymax=48)
