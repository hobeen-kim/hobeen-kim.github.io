"""CH20 트레이싱 없이 vs 트레이싱으로 — 인과관계 재구성 비교 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    def cbox(cx, cy, w, h, fc, **kw):
        d.box(cx - w / 2, cy - h / 2, w, h, fc, **kw)

    # ===== 왼쪽: 트레이싱 없이 =====
    d.box(3, 4, 44, 40, P["gray"])
    d.text(25, 41, "트레이싱 없이", size=12, weight="bold", color=P["orange"])
    logs = [(25, 33), (25, 24), (15, 13), (35, 13)]
    names = ["Gateway 로그", "Order 로그", "Payment 로그", "Inventory 로그"]
    for (cx, cy), t in zip(logs, names):
        cbox(cx, cy, 18, 5, P["brown"])
        d.text(cx, cy, t, size=10)
    d.arrow(25, 30.5, 25, 26.5, color=P["dim"], ls=(0, (4, 3)))
    d.arrow(21, 21.5, 16, 15.5, color=P["dim"], ls=(0, (4, 3)))
    d.arrow(29, 21.5, 34, 15.5, color=P["dim"], ls=(0, (4, 3)))
    d.text(38, 28, "같은 요청인지\n추론 불가", size=8, color=P["orange"], style="italic")

    # ===== 오른쪽: 트레이싱으로 =====
    d.box(53, 4, 44, 40, P["gray"], ec=P["accent"], lw=1.8)
    d.text(75, 41, "트레이싱으로", size=12, weight="bold", color=P["accent"])
    spans = [(75, 33), (75, 24), (65, 13), (85, 13)]
    snames = ["Gateway span", "Order span", "Payment span", "Inventory span"]
    for (cx, cy), t in zip(spans, snames):
        cbox(cx, cy, 18, 5.4, P["green"])
        d.text(cx, cy + 0.9, t, size=10)
        d.text(cx, cy - 1.4, "trace_id=X", size=8, color=P["accent"])
    d.arrow(75, 30.3, 75, 26.7, color=P["accent"])
    d.arrow(71, 21.3, 66, 15.7, color=P["accent"])
    d.arrow(79, 21.3, 84, 15.7, color=P["accent"])

    d.legend([
        Line2D([0], [0], color=P["dim"], lw=2.0, ls="--", label="연결 추론 불가"),
        Line2D([0], [0], color=P["accent"], lw=2.2, label="parent → child"),
    ])


diagram("20-tracing-vs-nothing", draw, w=12, h=5.6, ymax=46)
