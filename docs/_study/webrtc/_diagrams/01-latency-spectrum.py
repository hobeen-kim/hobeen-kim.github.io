"""CH01 §2 전송 방식별 지연 범위 — 로그 스케일 막대 (light/dark PNG)."""
import math

from _common import diagram

T_MIN, T_MAX = 0.05, 60.0
X0, X1 = 20, 96


def tx(t):
    """초 단위 지연 → x 좌표 (로그 스케일)."""
    r = (math.log10(t) - math.log10(T_MIN)) / (math.log10(T_MAX) - math.log10(T_MIN))
    return X0 + r * (X1 - X0)


def draw(d):
    P = d.P

    rows = [
        (36, "WebRTC", "(UDP · SRTP)", 0.1, 0.5, P["green"]),
        (28, "RTMP", "(TCP · 송출 구간)", 1.0, 5.0, P["brown"]),
        (20, "LL-HLS", "(HTTP · partial segment)", 2.0, 5.0, P["blue"]),
        (12, "HLS", "(HTTP · 6초 세그먼트)", 10.0, 30.0, P["purple"]),
    ]

    # 기준선: G.114 대화 지연
    for t, label in ((0.15, "150 ms"), (0.4, "400 ms")):
        x = tx(t)
        d.ax.plot([x, x], [7, 42], color=P["orange"], ls=(0, (3, 3)), lw=1.1, zorder=1)
        d.text(x, 43.6, label, size=8, color=P["orange"])
    d.text((tx(0.15) + tx(0.4)) / 2, 46.4, "대화 지연 기준 (G.114)", size=8,
           color=P["orange"])

    for y, name, sub, t0, t1, col in rows:
        d.text(2, y + 0.9, name, size=10.5, weight="bold", ha="left")
        d.text(2, y - 1.6, sub, size=8, color=P["dim"], ha="left")
        d.box(tx(t0), y - 2.2, tx(t1) - tx(t0), 4.4, col)
        lo = f"{t0:g}" if t0 >= 1 else f"{int(t0 * 1000)} ms"
        hi = f"{t1:g} s" if t1 >= 1 else f"{int(t1 * 1000)} ms"
        if t0 < 1 and t1 < 1:
            span = f"{int(t0 * 1000)}~{int(t1 * 1000)} ms"
        else:
            span = f"{lo}~{hi}"
        d.text(tx(t1) + 1.2, y, span, size=8.5, color=P["dim"], ha="left")

    # x축
    d.ax.plot([X0, X1], [6, 6], color=P["edge"], lw=1.2)
    for t, label in ((0.1, "0.1 s"), (0.3, "0.3 s"), (1, "1 s"), (3, "3 s"),
                     (10, "10 s"), (30, "30 s")):
        x = tx(t)
        d.ax.plot([x, x], [5.3, 6.7], color=P["edge"], lw=1.2)
        d.text(x, 3.4, label, size=8.5, color=P["dim"])
    d.text(X1, 1.0, "지연 (로그 스케일)", size=8, color=P["dim"], ha="right")


diagram("01-latency-spectrum", draw, w=12, h=5.2, ymax=48)
