"""CH04 카디널리티 폭발 — 유한 라벨 vs 무한 라벨(user_id) (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 유한 라벨 (정상)
    d.box(4, 36, 46, 12, P["green"], ec=P["accent"], lw=1.6)
    d.text(27, 44, "유한 라벨", size=11, weight="bold", color=P["accent"])
    d.text(27, 39.5, "method(2) × status(3) = 시계열 6개", size=9.5, color=P["dim"])

    d.box(56, 37.5, 18, 9, P["chip"])
    d.text(65, 42, "정상 범위", size=10.5, weight="bold", color=P["accent"])
    d.arrow(50, 42, 56, 42, color=P["accent"])

    # 무한 라벨 (폭발)
    d.box(4, 18, 46, 13, P["brown"], ec=P["orange"], lw=1.8)
    d.text(27, 27, "무한 라벨", size=11, weight="bold", color=P["orange"])
    d.text(27, 23, "× user_id(무한) = 시계열 사실상 무한", size=9.5, color=P["dim"])

    d.box(56, 19.5, 18, 10, P["chip"], ec=P["orange"], lw=1.6)
    d.text(65, 26, "메모리 폭증", size=10.5, weight="bold", color=P["orange"])
    d.text(65, 22.5, "→ OOM 위험", size=9, color=P["dim"])
    d.arrow(50, 24.5, 56, 24.5, color=P["orange"])

    # 연쇄 영향 (오른쪽)
    d.box(78, 15, 19, 33, P["gray"], ec=P["orange"], lw=1.4)
    d.text(87.5, 44.5, "연쇄 영향", size=10.5, weight="bold", color=P["orange"])
    for i, t in enumerate(["remote_write\n대역폭 증가",
                           "쿼리 지연 증가",
                           "멀티테넌시\nnoisy neighbor"]):
        yy = 37 - i * 8.5
        d.box(80, yy - 3.2, 15, 6.4, P["chip"])
        d.text(87.5, yy, t, size=8.5, color=P["dim"])
    d.arrow(74, 24.5, 78, 28, color=P["orange"], rad=0.1)


diagram("04-cardinality-explosion", draw, w=13, h=6, ymax=50)
