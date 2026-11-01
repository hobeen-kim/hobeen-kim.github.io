"""25장: Heartbeat 시퀀스 번호 판정. 1개 유실은 허용, 같은 값 반복은 오류, 연속 8개 정상으로 복귀."""
from _common import diagram

X0, STEP = 15, 5.6
BOX_W, BOX_Y, BOX_H = 4.8, 27, 6
VERDICT_Y, BAND_Y, BAND_H, AXIS_Y = 21.5, 11.5, 5, 6

FRAMES = [
    (0, "251", True, "기준"),
    (100, "0", True, "정상"),
    (200, "1", True, "정상"),
    (300, "2", False, "못 받음"),
    (400, "3", True, "+2 허용"),
    (500, "3", True, "같은 값"),
    (600, "4", True, "1/8"),
    (700, "5", True, "2/8"),
    (800, "6", True, "3/8"),
    (900, "7", True, "4/8"),
    (1000, "8", True, "5/8"),
    (1100, "9", True, "6/8"),
    (1200, "10", True, "7/8"),
    (1300, "11", True, "8/8 복귀"),
    (1400, "12", True, "정상"),
]
STATES = [(0, 500, "Operational", "green"), (500, 1300, "Sequence Error", "brown"),
          (1300, 1400, "Operational", "green")]


def tx(t):
    return X0 + t / 100 * STEP


def draw(d):
    P = d.P
    d.text(0.5, BOX_Y + BOX_H / 2, "보낸 번호", size=10, ha="left")
    d.text(0.5, VERDICT_Y, "수신 측 판정", size=10, ha="left")
    d.text(0.5, BAND_Y + BAND_H / 2, "수신 측 상태", size=10, ha="left")

    for t, seq, received, verdict in FRAMES:
        x = tx(t)
        ec, lw = None, 1.4
        if verdict == "같은 값":
            ec, lw = P["orange"], 2.4
        elif verdict == "8/8 복귀":
            ec, lw = P["accent"], 2.4
        d.box(x - BOX_W / 2, BOX_Y, BOX_W, BOX_H, P["blue"], ec=ec, lw=lw,
              alpha=1.0 if received else 0.35)
        d.text(x, BOX_Y + BOX_H / 2, seq, size=10.5,
               color=P["text"] if received else P["dim"])
        color = P["text"]
        if not received or verdict == "같은 값":
            color = P["orange"]
        elif verdict in ("+2 허용", "8/8 복귀"):
            color = P["accent"]
        d.text(x, VERDICT_Y, verdict, size=9, color=color)

    left = tx(0) - BOX_W / 2
    right = tx(1400) + BOX_W / 2
    for start, end, name, key in STATES:
        x1 = left if start == 0 else tx(start)
        x2 = right if end == 1400 else tx(end)
        d.box(x1, BAND_Y, x2 - x1, BAND_H, P[key], r=0.01)
        d.text((x1 + x2) / 2, BAND_Y + BAND_H / 2, name, size=9.5)

    d.ax.plot([left, right], [AXIS_Y, AXIS_Y], color=P["edge"], lw=1.2)
    for t, *_ in FRAMES:
        d.ax.plot([tx(t), tx(t)], [AXIS_Y - 0.6, AXIS_Y + 0.6], color=P["edge"], lw=1.0)
        d.text(tx(t), AXIS_Y - 2.4, str(t), size=8, color=P["dim"])
    d.text(0.5, AXIS_Y - 2.4, "시각(ms)", size=9, color=P["dim"], ha="left")


diagram("25-heartbeat-timeline", draw, w=14, h=4.8, xmax=100, ymax=36)
