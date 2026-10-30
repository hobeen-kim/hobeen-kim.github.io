"""CH13 Part 7 B.33.3 Heartbeat 수신 측 상태 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    # 시퀀스 검증 그룹
    d.box(6, 17, 88, 22, P["chip"], ec=P["accent"], lw=1.2)
    d.text(8.5, 37, "시퀀스·타이밍 검증", size=8.5, color=P["accent"], ha="left")

    d.box(13, 23, 28, 9, P["green"])
    d.text(27, 27.5, "Operational", size=11, weight="bold")
    d.box(59, 23, 28, 9, P["brown"])
    d.text(73, 27.5, "Sequence Error", size=11, weight="bold")

    d.arrow(41, 30, 59, 30, color=P["orange"])
    d.text(50, 35.4, "같은 값 반복", size=8, color=P["orange"])
    d.text(50, 32.6, "증가폭 > 3 · 간격 > 300 ms", size=8, color=P["orange"])
    d.arrow(59, 25, 41, 25, color=P["accent"])
    d.text(50, 21.6, "연속 8개 정상", size=8, color=P["accent"])

    d.arrow(27, 45, 27, 32, color=P["accent"])
    d.text(28.5, 43.2, "첫 수신 / 251 수신 (재동기화)", size=8, color=P["dim"], ha="left")
    d.text(92, 43.2, "252·253: 메시지 무시", size=8, color=P["dim"], ha="right")

    d.box(13, 3, 28, 8, P["gray"])
    d.text(27, 7, "Transmission Error", size=10, weight="bold")
    d.box(59, 3, 28, 8, P["gray"])
    d.text(73, 7, "Graceful Shutdown", size=10, weight="bold")
    d.arrow(27, 17, 27, 11, color=P["violet"])
    d.text(29, 14, "254 수신", size=8, color=P["violet"], ha="left")
    d.arrow(73, 17, 73, 11, color=P["violet"])
    d.text(75, 14, "255 수신 (직전 값 255 아님)", size=8, color=P["violet"], ha="left")


diagram("13-p7-heartbeat-states", draw, w=11, h=5.2, xmax=100, ymax=48)
