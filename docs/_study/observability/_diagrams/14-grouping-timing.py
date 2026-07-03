"""CH14 grouping 타이밍 — group_wait·group_interval·repeat_interval (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    actors = [
        (14, "알림 발화", P["gray"]),
        (50, "그룹\n(alertname=DiskFull)", P["green"]),
        (86, "알림 전송", P["brown"]),
    ]
    for x, name, c in actors:
        d.box(x - 13, 47, 26, 4, c)
        d.text(x, 49, name, size=9.5, weight="bold")
        d.ax.plot([x, x], [5, 47], color=P["edge"], lw=1.1, ls="--", zorder=1)

    XA, XG, XN = 14, 50, 86

    def tstamp(y, s):
        d.text(3, y, s, size=8.5, color=P["orange"], weight="bold", ha="left")

    # t=0s
    tstamp(44, "t=0s")
    d.arrow(XA, 44, XG, 44, color=P["dim"])
    d.text(32, 45.3, "첫 알림 도착 (그룹 생성)", size=8, color=P["text"])

    # group_wait note
    d.box(37, 39, 26, 3.6, P["chip"], ec=P["violet"], lw=1.4)
    d.text(50, 40.8, "group_wait=30s 대기", size=8.5, color=P["violet"])

    # t=10s
    tstamp(35, "t=10s")
    d.arrow(XA, 35, XG, 35, color=P["dim"])
    d.text(32, 36.3, "같은 그룹 알림 2개 추가 도착", size=8, color=P["text"])

    # t=30s 1차 발송
    tstamp(29, "t=30s")
    d.arrow(XG, 29, XN, 29, color=P["accent"])
    d.text(68, 30.3, "3개 알림 묶어 1차 발송", size=8, color=P["accent"])

    # t=45s
    tstamp(23, "t=45s")
    d.arrow(XA, 23, XG, 23, color=P["dim"])
    d.text(32, 24.3, "같은 그룹 알림 1개 추가 도착", size=8, color=P["text"])

    # group_interval note
    d.box(37, 17.2, 26, 3.6, P["chip"], ec=P["orange"], lw=1.4)
    d.text(50, 19.0, "group_interval=5m 대기\n→ 즉시 발송 안 함", size=7.8, color=P["orange"])

    # t=5m30s 2차 발송
    tstamp(13, "t=5m30s")
    d.arrow(XG, 13, XN, 13, color=P["accent"])
    d.text(68, 14.3, "추가분 포함 2차 발송", size=8, color=P["accent"])

    # t=4h30s repeat
    tstamp(8.5, "t=4h30s")
    d.arrow(XG, 8.5, XN, 8.5, color=P["orange"])
    d.text(68, 9.8, "repeat_interval 도달, 재알림", size=8, color=P["orange"])

    d.legend([
        Line2D([0], [0], color=P["dim"], lw=2.5, label="알림 도착 (그룹으로)"),
        Line2D([0], [0], color=P["accent"], lw=2.5, label="그룹 발송"),
        Line2D([0], [0], color=P["orange"], lw=2.5, label="repeat 재알림"),
    ])


diagram("14-grouping-timing", draw, w=14, h=7.5, ymax=53)
