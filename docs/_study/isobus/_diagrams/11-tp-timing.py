"""CH11 §8 RTS/CTS 세션의 타이머 배치: Part 3 Figure B.1 재구성 (light/dark PNG)."""
from _common import diagram

XO, XR = 34, 70          # 송신 측 / 수신 측 생명선 x


def draw(d):
    P = d.P
    top, bottom = 57, 4

    for x, name in ((XO, "송신 측\n(originating CF)"), (XR, "수신 측\n(receiving CF)")):
        d.box(x - 9, top, 18, 6, P["blue"])
        d.text(x, top + 3, name, size=10)
        d.ax.plot([x, x], [bottom, top], color=P["edge"], lw=1.3)

    def msg(y0, y1, left_to_right, label, color=None):
        x0, x1 = (XO, XR) if left_to_right else (XR, XO)
        d.arrow(x0, y0, x1, y1, color=color or P["accent"], lw=1.6)
        d.text((XO + XR) / 2, (y0 + y1) / 2 + 1.5, label, size=8.6)

    msg(53, 50, True, "RTS (16, 23, 4, 255, PGN)")
    msg(48, 45, False, "CTS (17, 2, 1, ...)")
    msg(42, 39.5, True, "DT 1")
    msg(38, 35.5, True, "DT 2")
    msg(32, 29.5, False, "CTS (17, 0, ...) hold", color=P["orange"])
    msg(26, 23.5, False, "CTS (17, 2, 3, ...)")
    msg(20, 17.5, True, "DT 3")
    msg(16, 13.5, True, "DT 4 (마지막)")
    msg(9, 6.5, False, "EoMA (19, 23, 4, 255, PGN)")

    def span(x, y_from, y_to, label, side, color=None):
        c = color or P["dim"]
        d.ax.plot([x, x], [y_to, y_from], color=c, lw=1.2)
        for y in (y_from, y_to):
            d.ax.plot([x - 0.7, x + 0.7], [y, y], color=c, lw=1.2)
        if side == "left":
            d.text(x - 1.2, (y_from + y_to) / 2, label, size=8.2, color=c, ha="right")
        else:
            d.text(x + 1.2, (y_from + y_to) / 2, label, size=8.2, color=c, ha="left")

    # 송신 측 타이머 (왼쪽)
    span(XO - 3, 53, 45, "T3 1250 ms\n(CTS 대기)", "left")
    span(XO - 3, 45, 42, "Tr ≤ 200 ms", "left", P["violet"])
    span(XO - 3, 38, 29.5, "T3 1250 ms", "left")
    span(XO - 3, 29.5, 23.5, "T4 ≤ 1050 ms\n(hold 뒤)", "left", P["orange"])
    span(XO - 3, 16, 6.5, "T3 1250 ms\n(EoMA 대기)", "left")

    # 수신 측 타이머 (오른쪽)
    span(XR + 3, 50, 48, "Tr ≤ 200 ms", "right", P["violet"])
    span(XR + 3, 48, 39.5, "T2 1250 ms\n(첫 DT 대기)", "right")
    span(XR + 3, 39.5, 35.5, "T1 750 ms", "right")
    span(XR + 3, 32, 26, "Th ≤ 500 ms\n(hold 반복)", "right", P["orange"])
    span(XR + 3, 26, 17.5, "T2 1250 ms", "right")
    span(XR + 3, 13.5, 9, "Tr ≤ 200 ms", "right", P["violet"])


diagram("11-tp-timing", draw, w=10, h=7.6, xmax=100, ymax=65)
