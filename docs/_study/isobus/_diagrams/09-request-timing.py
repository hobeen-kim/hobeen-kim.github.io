"""CH09 §12 요청 응답 시간(Tr)·대기(T3)·재시도와 T3 산정 (light/dark PNG)."""
from _common import diagram

XL, XR, TMAX = 20, 96, 4.0


def tx(t):
    return XL + (XR - XL) * t / TMAX


def draw(d):
    P = d.P

    # 시간 축
    axis_y = 4
    d.ax.plot([tx(0), tx(TMAX)], [axis_y, axis_y], color=P["edge"], lw=1.2)
    for t in (0, 0.5, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 3.5, 3.75, 4.0):
        d.ax.plot([tx(t), tx(t)], [axis_y - 0.6, axis_y + 0.6], color=P["edge"], lw=1.0)
    for t, s in ((0, "0"), (1.25, "1.25 s"), (2.5, "2.5 s"), (3.75, "3.75 s")):
        d.text(tx(t), axis_y - 2.2, s, size=8.4, color=P["dim"])

    # 행 1: 정상 응답
    y1 = 36
    d.text(2, y1, "정상 응답", size=9.5, ha="left", weight="bold")
    d.ax.plot([tx(0), tx(TMAX)], [y1, y1], color=P["edge"], lw=0.8, ls=":")
    d.box(tx(0) - 0.6, y1 - 1.6, 1.2, 3.2, P["blue"])
    d.text(tx(0), y1 + 3.2, "요청", size=8.4)
    d.box(tx(0.15) - 0.6, y1 - 1.6, 1.2, 3.2, P["green"])
    d.text(tx(0.15) + 1.5, y1 + 3.2, "응답", size=8.4, ha="left")
    d.ax.plot([tx(0), tx(0.2)], [y1 - 3.2, y1 - 3.2], color=P["violet"], lw=1.4)
    d.text(tx(0.2) + 1.0, y1 - 3.2, "Tr ≤ 200 ms (응답 측 의무)", size=8.4, color=P["violet"], ha="left")

    # 행 2: 무응답 -> 재시도 2회 -> 포기
    y2 = 22
    d.text(2, y2, "무응답", size=9.5, ha="left", weight="bold")
    d.ax.plot([tx(0), tx(TMAX)], [y2, y2], color=P["edge"], lw=0.8, ls=":")
    for i, t in enumerate((0, 1.25, 2.5)):
        d.box(tx(t) - 0.6, y2 - 1.6, 1.2, 3.2, P["blue"])
        d.text(tx(t), y2 + 3.2, f"요청 {i + 1}", size=8.4)
        d.ax.plot([tx(t) + 0.8, tx(t + 1.25) - 0.4], [y2 - 3.2, y2 - 3.2], color=P["dim"], lw=1.3)
        d.text(tx(t + 0.625), y2 - 5.0, "T3 ≥ 1.25 s", size=8.2, color=P["dim"])
    d.box(tx(3.75) - 0.6, y2 - 1.6, 1.2, 3.2, P["brown"])
    d.text(tx(3.75), y2 + 3.2, "포기", size=8.4, color=P["orange"])

    # 행 3: T3 산정 (브리지 10개)
    y3 = 11
    d.text(2, y3, "T3 산정", size=9.5, ha="left", weight="bold")
    segs = [(0, 0.5, "요청 편도 500 ms\n(브리지 10개 x 50 ms)", "blue"),
            (0.5, 0.7, "Tr", "purple"),
            (0.7, 1.2, "응답 편도 500 ms", "green"),
            (1.2, 1.25, "", "brown")]
    for a, b, s, c in segs:
        d.box(tx(a), y3 - 2.2, tx(b) - tx(a), 4.4, P[c])
        if s:
            d.text((tx(a) + tx(b)) / 2, y3, s, size=7.8)
    d.text(tx(1.25) + 1.2, y3 + 1.2, "마진 50 ms", size=8.2, color=P["dim"], ha="left")
    d.text(tx(1.25) + 1.2, y3 - 1.4, "합계 1250 ms", size=8.2, color=P["accent"], ha="left")


diagram("09-request-timing", draw, w=12, h=4.8, xmax=100, ymax=42)
