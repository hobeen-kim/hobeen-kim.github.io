"""CH11 for와 상태 전이 — Inactive → Pending → Firing (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    states = [
        (17, P["gray"], "Inactive", "조건 거짓 · 평상시"),
        (50, P["blue"], "Pending", "조건 참 직후\nfor 타이머 · 미전송"),
        (83, P["brown"], "Firing", "for 내내 참\nAlertmanager 전송"),
    ]
    for xc, fc, t, sub in states:
        d.box(xc - 11, 24, 22, 11, fc, ec=P["accent"], lw=1.8)
        d.text(xc, 31.6, t, size=12.5, weight="bold", color=P["accent"])
        d.text(xc, 27.4, sub, size=8.5)

    # 정방향
    d.arrow(28, 30.5, 39, 30.5, color=P["accent"])
    d.text(33.5, 32.8, "expr 참", size=8, color=P["accent"], weight="bold")
    d.arrow(61, 30.5, 72, 30.5, color=P["accent"])
    d.text(66.5, 32.8, "for 기간 연속 참", size=8, color=P["accent"], weight="bold")

    # Firing 자기 루프
    d.arrow(80, 35, 86, 35, color=P["orange"], rad=-1.0)
    d.text(83, 40.5, "계속 참 → 계속 전송", size=7.8, color=P["orange"], weight="bold")

    # 역방향
    d.arrow(45, 24, 22, 24, color=P["dim"], rad=-0.32)
    d.text(33.5, 17, "for 전에 거짓", size=8, color=P["dim"], weight="bold")
    d.arrow(78, 24, 24, 24, color=P["dim"], rad=-0.24)
    d.text(52, 13.8, "expr 거짓 → Inactive", size=8, color=P["dim"], weight="bold")


diagram("11-for-state", draw, w=13, h=6, ymax=44)
