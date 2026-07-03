"""CH09 Counter 다루기 — rate · irate · increase (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(35, 40, 30, 8, P["gray"], ec=P["accent"], lw=1.8)
    d.text(50, 45.5, "Counter 원시값", size=12, weight="bold", color=P["accent"])
    d.text(50, 42.3, "단조 증가 · 리셋 가능", size=8.5, color=P["dim"])

    mids = [
        (19, P["green"], "rate()", "구간 평균 초당 증가율\n리셋 보정"),
        (50, P["brown"], "irate()", "마지막 2개 샘플\n순간 변화율"),
        (81, P["blue"], "increase()", "구간 총 증가량\n= rate × 구간초"),
    ]
    for xc, fc, t, sub in mids:
        d.box(xc - 13, 24, 26, 11, fc)
        d.text(xc, 32, t, size=12, weight="bold", color=P["accent"])
        d.text(xc, 27.8, sub, size=8.5)
        d.arrow(50, 40, xc, 35, color=P["orange"], rad=0.04)

    downs = [
        (19, "대시보드 / 알림", "권장", P["accent"]),
        (50, "순간 스파이크 관찰", "알림 비권장", P["orange"]),
        (81, "절대 증가량 확인", '"5분간 몇 건"', P["dim"]),
    ]
    for xc, t, sub, sc in downs:
        d.box(xc - 13, 6, 26, 8, P["chip"])
        d.text(xc, 11, t, size=9.5, weight="bold")
        d.text(xc, 8, sub, size=8, color=sc, style="italic")
        d.arrow(xc, 24, xc, 14, color=P["dim"])


diagram("09-counter-functions", draw, w=13, h=6.4, ymax=50)
