"""CH08 RED 방법론 — 요청 기반 서비스 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(3, 16, 16, 8, P["chip"])
    d.text(11, 20, "들어오는 요청", size=10.5)

    d.box(26, 16, 14, 8, P["blue"], ec=P["accent"], lw=1.8)
    d.text(33, 20, "서비스", size=12, weight="bold", color=P["accent"])
    d.arrow(19, 20, 26, 20, color=P["accent"])

    outs = [
        (32, "Rate", "초당 요청 수"),
        (20, "Errors", "초당 실패 요청 수"),
        (8, "Duration", "요청 처리 시간 분포 (p50·p95·p99)"),
    ]
    for yc, t, sub in outs:
        d.box(52, yc - 4.5, 44, 9, P["green"])
        d.text(55, yc + 1.4, t, size=12, weight="bold", color=P["accent"], ha="left")
        d.text(55, yc - 1.8, sub, size=9, color=P["text"], ha="left")
        d.arrow(40, 20, 52, yc, color=P["orange"], rad=0.05)


diagram("08-red-method", draw, w=12, h=5.6, ymax=40)
