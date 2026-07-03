"""CH20 context propagation — W3C traceparent 헤더 전파 시퀀스 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P
    lanes = [(18, "API Gateway", "blue"), (50, "Order Service", "green"),
             (82, "Payment Service", "brown")]

    TOP, BOT = 42, 6
    for x, name, c in lanes:
        d.box(x - 11, TOP, 22, 3.6, P[c])
        d.text(x, TOP + 1.8, name, size=10.5, weight="bold")
        d.ax.plot([x, x], [BOT, TOP], color=P["edge"], lw=1.2, ls=(0, (3, 3)), zorder=1)

    def msg(x1, x2, y, label, color, ls="-"):
        d.arrow(x1, y, x2, y, color=color, lw=2.0, ls=ls)
        d.text((x1 + x2) / 2, y + 1.2, label, size=8, color=color)

    msg(18, 50, 38, "POST /orders  (traceparent)", P["accent"])
    d.text(50, 33.5, "trace_id 유지 · 새 span_id", size=8, color=P["orange"], style="italic")
    msg(50, 82, 29, "POST /charge  (traceparent)", P["accent"])
    d.text(82, 24.5, "parent_id = Order span_id", size=8, color=P["orange"], style="italic")
    msg(82, 50, 19, "200 OK", P["dim"], ls=(0, (4, 3)))
    msg(50, 18, 14, "200 OK", P["dim"], ls=(0, (4, 3)))

    d.text(50, 8.4, "traceparent: 00-4bf92f35...4736-00f067aa0ba902b7-01",
           size=8.5, color=P["accent"])
    d.text(50, 6.2, "버전 - trace_id(32) - parent_id(16) - flags(01=샘플링)",
           size=8, color=P["dim"], style="italic")

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.2, label="요청 (traceparent 전파)"),
        Line2D([0], [0], color=P["dim"], lw=2.2, ls="--", label="응답"),
    ], loc="upper right", anchor=(0.99, 0.72))


diagram("20-context-propagation", draw, w=12, h=6, ymax=48)
