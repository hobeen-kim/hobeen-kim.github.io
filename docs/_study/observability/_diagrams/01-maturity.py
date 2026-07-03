"""CH01 관측성 성숙도 — Reactive → Diagnostic → Proactive (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    stages = [
        (4, P["brown"], P["orange"], "Reactive",
         "장애 후 로그 grep\n수동 대시보드"),
        (37, P["blue"], P["accent"], "Diagnostic",
         "메트릭·로그·트레이스 연결\nMTTR 단축"),
        (70, P["green"], P["accent"], "Proactive",
         "SLO 기반 알림\n이상 징후 사전 포착"),
    ]
    for x, fc, ac, name, body in stages:
        d.box(x, 8, 26, 16, fc)
        d.text(x + 13, 20, name, size=13, weight="bold", color=ac)
        d.text(x + 13, 14, body, size=9, color=P["dim"])

    d.arrow(30, 16, 37, 16, color=P["accent"])
    d.text(33.5, 18.6, "신호 통합", size=8, color=P["accent"])
    d.arrow(63, 16, 70, 16, color=P["accent"])
    d.text(66.5, 18.6, "SLO·상관관계", size=8, color=P["accent"])


diagram("01-maturity", draw, w=13, h=4.4, ymax=30)
