"""CH24 온디맨드 vs 연속 프로파일링 — 사후 분석 가능 여부 대비 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # ===== 좌: 온디맨드 =====
    d.box(3, 5, 44, 40, P["gray"], ec=P["edge"], lw=1.6)
    d.text(25, 42, "온디맨드 프로파일링", size=12, weight="bold", color=P["dim"])

    steps_l = [
        ("장애 발생", P["brown"]),
        ("원인 의심 후\n수동으로 프로파일러 트리거", P["chip"]),
        ("이미 상황 종료\n원인 재현 불가", P["brown"]),
    ]
    for i, (t, c) in enumerate(steps_l):
        yy = 35 - i * 11
        d.box(9, yy - 3.5, 32, 7, c)
        d.text(25, yy, t, size=10, weight="bold")
        if i < 2:
            d.arrow(25, yy - 3.5, 25, yy - 7, color=P["dim"], lw=1.8)

    # ===== 우: 연속 =====
    d.box(53, 5, 44, 40, P["gray"], ec=P["accent"], lw=1.8)
    d.text(75, 42, "연속(continuous) 프로파일링", size=12, weight="bold",
           color=P["accent"])

    steps_r = [
        ("24/7 상시 샘플링", P["green"]),
        ("타임스탬프와 함께 지속 저장", P["blue"]),
        ("장애 발생", P["brown"]),
        ("과거 시점 프로파일 조회\n(사후 분석)", P["green"]),
    ]
    for i, (t, c) in enumerate(steps_r):
        yy = 37 - i * 8.3
        d.box(58, yy - 2.8, 34, 5.6, c)
        d.text(75, yy, t, size=9.5, weight="bold")
        if i < 3:
            d.arrow(75, yy - 2.8, 75, yy - 5.5, color=P["accent"], lw=1.8)


diagram("24-ondemand-vs-continuous", draw, w=12, h=6, ymax=48)
