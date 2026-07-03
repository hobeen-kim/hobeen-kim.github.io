"""CH31 RED / USE 대시보드 — drill-down 구조 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # RED 그룹 (좌)
    d.box(4, 24, 40, 15, P["blue"])
    d.text(24, 36.2, "RED 대시보드 (서비스)", size=10.5, weight="bold", color=P["accent"])
    for i, (t, sub) in enumerate([("Rate", "요청/초"), ("Errors", "에러율"),
                                  ("Duration", "p50/p95/p99")]):
        x = 6.5 + i * 12.3
        d.box(x, 26, 11, 8, P["chip"])
        d.text(x + 5.5, 31, t, size=9, weight="bold")
        d.text(x + 5.5, 28, sub, size=7.2, color=P["dim"])

    # USE 그룹 (우)
    d.box(56, 24, 40, 15, P["green"])
    d.text(76, 36.2, "USE 대시보드 (리소스)", size=10.5, weight="bold", color=P["accent"])
    for i, (t, sub) in enumerate([("Utilization", "사용률"), ("Saturation", "대기열/큐"),
                                  ("Errors", "리소스 에러")]):
        x = 58.5 + i * 12.3
        d.box(x, 26, 11, 8, P["chip"])
        d.text(x + 5.5, 31, t, size=8.6, weight="bold")
        d.text(x + 5.5, 28, sub, size=7.2, color=P["dim"])

    # 원인 조사
    d.box(35, 12, 30, 6.5, P["brown"], ec=P["orange"], lw=1.6)
    d.text(50, 15.25, "원인 조사", size=11, weight="bold")

    # 트레이스/프로파일
    d.box(35, 3, 30, 6, P["purple"], ec=P["accent"], lw=1.5)
    d.text(50, 6, "트레이스·프로파일로 drill-down", size=9.5, weight="bold")

    d.arrow(22, 24, 40, 18.5, color=P["accent"], lw=1.9)
    d.text(26, 21.4, "에러율 급증", size=8, color=P["orange"], weight="bold")
    d.arrow(78, 24, 60, 18.5, color=P["accent"], lw=1.9)
    d.text(74, 21.4, "포화도 급증", size=8, color=P["orange"], weight="bold")
    d.arrow(50, 12, 50, 9, color=P["accent"], lw=2.1)


diagram("31-red-use-dashboard", draw, w=13, h=6.2, ymax=42)
