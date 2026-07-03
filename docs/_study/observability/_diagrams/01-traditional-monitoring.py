"""CH01 전통적 모니터링 — known-unknowns 흐름과 대응 불가 영역 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 전통적 모니터링 그룹
    d.box(4, 8, 62, 24, P["gray"], ec=P["accent"], lw=1.8)
    d.text(35, 28.6, "전통적 모니터링", size=11, weight="bold", color=P["accent"])

    chips = [
        (15, "known-unknowns", "정의된 실패 모드"),
        (35, "고정 대시보드", "겪은 장애 재확인"),
        (55, "정적 임계치 알림", "cpu > 90% 식 규칙"),
    ]
    for cx, t, sub in chips:
        d.box(cx - 9, 13.5, 18, 9.5, P["chip"])
        d.text(cx, 19.4, t, size=10, weight="bold")
        d.text(cx, 16.0, sub, size=8, color=P["dim"])
    d.arrow(24.5, 18.3, 26, 18.3)
    d.arrow(44.5, 18.3, 46, 18.3)

    # 대응 불가 영역 (unknown-unknowns)
    d.box(74, 11, 22, 17, P["brown"], ec=P["orange"], lw=1.8)
    d.text(85, 23.5, "대응 불가 영역", size=10.5, weight="bold", color=P["orange"])
    d.text(85, 18.5, "unknown-unknowns\n처음 보는 장애", size=9, color=P["dim"])

    d.arrow(64, 18.3, 74, 19.5, color=P["orange"])
    d.text(69.5, 22.2, "처음 보는\n장애?", size=8, color=P["orange"])


diagram("01-traditional-monitoring", draw, w=12, h=4.6, ymax=36)
