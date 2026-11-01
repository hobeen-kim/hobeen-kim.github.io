"""CH3 6절 비트레이트와 최대 버스 길이: CAN 일반 기준 막대그래프 (light/dark PNG)."""
from _common import diagram

BARS = [("1 Mbps", 25), ("500 kbps", 100), ("250 kbps", 250), ("125 kbps", 500), ("50 kbps", 1000)]


def draw(d):
    P = d.P
    ax = d.ax
    base, top = 8, 40

    def h(m):
        return m / 1000 * (top - base)

    for m in (250, 500, 750, 1000):
        ax.plot([12, 96], [base + h(m), base + h(m)], color=P["edge"], lw=0.7, ls=":", zorder=0.5)
        d.text(11, base + h(m), f"{m} m", size=9, color=P["dim"], ha="right")
    ax.plot([12, 96], [base, base], color=P["edge"], lw=1.4, zorder=1)
    d.text(2, 44, "최대 버스 길이 (m)", size=9.5, color=P["dim"], ha="left")

    for i, (label, m) in enumerate(BARS):
        cx = 22 + i * 17
        isobus = label == "250 kbps"
        d.box(cx - 5, base, 10, max(h(m), 0.5), P["accent"] if isobus else P["blue"],
              ec=P["accent"] if isobus else P["edge"], r=0.005)
        d.text(cx, base + h(m) + 1.8, f"{m} m", size=10, weight="bold")
        d.text(cx, base - 2.4, label, size=10)
        if isobus:
            d.text(cx, base - 5.4, "ISOBUS 표준 속도", size=9, color=P["accent"])


diagram("03-bitrate-length", draw, w=11, h=5.15, xmax=100, ymax=47)
