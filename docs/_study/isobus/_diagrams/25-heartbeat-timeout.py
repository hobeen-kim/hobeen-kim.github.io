"""25장: Heartbeat가 연속 3개 빠질 때 300 ms 감시 타이머가 시퀀스 규칙보다 먼저 오류를 잡는 과정."""
from _common import diagram

X0, STEP = 18, 10.5
BOX_W, BOX_Y, BOX_H = 8, 30, 6
TIMER_Y, VERDICT_Y, BAND_Y, BAND_H, AXIS_Y = 24, 17.5, 8.5, 5, 4
TIMEOUT_T = 501

FRAMES = [
    (0, "7", True, "정상"),
    (100, "8", True, "정상"),
    (200, "9", True, "정상"),
    (300, "10", False, "못 받음"),
    (400, "11", False, "못 받음"),
    (500, "12", False, "못 받음"),
    (600, "13", True, "+4 오류"),
    (700, "14", True, "1/8"),
]


def tx(t):
    return X0 + t / 100 * STEP


def draw(d):
    P = d.P
    d.text(0.5, BOX_Y + BOX_H / 2, "보낸 번호", size=10, ha="left")
    d.text(0.5, TIMER_Y, "감시 타이머", size=10, ha="left")
    d.text(0.5, VERDICT_Y, "수신 측 판정", size=10, ha="left")
    d.text(0.5, BAND_Y + BAND_H / 2, "수신 측 상태", size=10, ha="left")

    for t, seq, received, verdict in FRAMES:
        x = tx(t)
        d.box(x - BOX_W / 2, BOX_Y, BOX_W, BOX_H, P["blue"],
              alpha=1.0 if received else 0.35)
        d.text(x, BOX_Y + BOX_H / 2, seq, size=10.5,
               color=P["text"] if received else P["dim"])
        color = P["orange"] if verdict in ("못 받음", "+4 오류") else P["text"]
        d.text(x, VERDICT_Y, verdict, size=9.5, color=color)

    x_last, x_fire = tx(200), tx(TIMEOUT_T)
    d.ax.plot([x_last, x_last, x_fire, x_fire],
              [TIMER_Y - 0.8, TIMER_Y, TIMER_Y, TIMER_Y - 0.8],
              color=P["violet"], lw=1.6)
    d.text((x_last + x_fire) / 2, TIMER_Y + 1.6, "마지막 수신 뒤 300 ms", size=9,
           color=P["violet"])
    for y_low, y_high in ((VERDICT_Y + 1.8, TIMER_Y), (BAND_Y + BAND_H + 0.6, VERDICT_Y - 1.8)):
        d.ax.plot([x_fire, x_fire], [y_low, y_high], color=P["orange"], lw=1.6, ls="--")
    d.text(x_fire + 1.2, TIMER_Y - 2.2, "시간 초과:\n오류 감지", size=9,
           color=P["orange"], ha="left")

    left = tx(0) - BOX_W / 2
    right = tx(700) + BOX_W / 2
    d.box(left, BAND_Y, x_fire - left, BAND_H, P["green"], r=0.01)
    d.text((left + x_fire) / 2, BAND_Y + BAND_H / 2, "Operational", size=9.5)
    d.box(x_fire, BAND_Y, right - x_fire, BAND_H, P["brown"], r=0.01)
    d.text((x_fire + right) / 2, BAND_Y + BAND_H / 2, "Sequence Error", size=9.5)

    d.ax.plot([left, right], [AXIS_Y, AXIS_Y], color=P["edge"], lw=1.2)
    for t, *_ in FRAMES:
        d.ax.plot([tx(t), tx(t)], [AXIS_Y - 0.6, AXIS_Y + 0.6], color=P["edge"], lw=1.0)
        d.text(tx(t), AXIS_Y - 2.2, str(t), size=8.5, color=P["dim"])
    d.text(0.5, AXIS_Y - 2.2, "시각(ms)", size=9, color=P["dim"], ha="left")


diagram("25-heartbeat-timeout", draw, w=12, h=5, xmax=100, ymax=38)
