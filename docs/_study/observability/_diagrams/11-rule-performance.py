"""CH11 룰 성능 — 평가 지연 관측과 튜닝 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 증상 체인 (상단)
    d.box(3, 32, 26, 10, P["brown"])
    d.text(16, 38.4, "평가 시간 ≥ interval", size=10.5, weight="bold", color=P["accent"])
    d.text(16, 34.4, "rule_group_last_duration", size=8, color=P["dim"], style="italic")

    d.box(34, 33.5, 15, 7, P["gray"])
    d.text(41.5, 37, "평가 지연", size=10, weight="bold")

    d.box(54, 32, 28, 10, P["blue"])
    d.text(68, 38.4, "누락 카운터 증가", size=10.5, weight="bold", color=P["accent"])
    d.text(68, 34.4, "iterations_missed_total ↑", size=8, color=P["dim"], style="italic")

    d.arrow(29, 37, 34, 37, color=P["orange"])
    d.arrow(49, 37, 54, 37, color=P["orange"])

    # 해결책 (하단)
    fixes = [
        (18, "그룹 분할", "순서 의존 없는 룰을\n별도 그룹 → 병렬"),
        (50, "Recording Rule", "무거운 집계를\n한 번만 계산"),
        (82, "고카디널리티 제거", "매 interval 반복이라\n영향이 크다"),
    ]
    for xc, t, sub in fixes:
        d.box(xc - 14, 8, 28, 12, P["green"])
        d.text(xc, 16.5, t, size=10.5, weight="bold", color=P["accent"])
        d.text(xc, 12.2, sub, size=8.5)
        d.arrow(68, 32, xc, 20, color=P["accent"], rad=0.05)


diagram("11-rule-performance", draw, w=13, h=6, ymax=46)
