"""CH20 분산 트레이싱 표준의 역사 — 타임라인 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    Y = 20
    d.ax.plot([6, 92], [Y, Y], color=P["edge"], lw=2.4, zorder=2)
    d.arrow(88, Y, 94, Y, color=P["edge"], lw=2.4)

    events = [
        (2010, "Google Dapper\n논문 발표", "blue", "up"),
        (2012, "Zipkin 오픈소스\n(Twitter)", "green", "down"),
        (2016, "OpenTracing\n(CNCF)", "brown", "up"),
        (2017, "OpenCensus\n(Google)", "violet", "down"),
        (2019, "OpenTracing·Census\n통합 발표", "orange", "up"),
        (2021, "OpenTelemetry\nTraces 1.0 GA", "accent", "down"),
    ]
    xs = [10, 26, 42, 58, 74, 90]
    for (yr, label, c, side), x in zip(events, xs):
        col = P[c]
        d.ax.plot([x], [Y], "o", color=col, markersize=12, zorder=3)
        if side == "up":
            d.ax.plot([x, x], [Y + 1.2, Y + 5.5], color=col, lw=1.4, zorder=2)
            d.box(x - 8, Y + 5.5, 16, 7, P["chip"], ec=col, lw=1.5)
            d.text(x, Y + 10.6, str(yr), size=11.5, weight="bold", color=col)
            d.text(x, Y + 7.4, label, size=8.4)
        else:
            d.ax.plot([x, x], [Y - 1.2, Y - 5.5], color=col, lw=1.4, zorder=2)
            d.box(x - 8, Y - 12.5, 16, 7, P["chip"], ec=col, lw=1.5)
            d.text(x, Y - 6.6, str(yr), size=11.5, weight="bold", color=col)
            d.text(x, Y - 9.8, label, size=8.4)


diagram("20-tracing-history", draw, w=15, h=6, ymax=40)
