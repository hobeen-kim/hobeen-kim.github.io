"""CH10 성능 안티패턴 — 느린 쿼리 진단 결정 트리 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # 시작
    d.box(15, 51, 24, 6, P["gray"], ec=P["accent"], lw=1.8)
    d.text(27, 54, "느린 / 비싼 쿼리", size=11, weight="bold", color=P["accent"])

    decisions = [
        (44, "고카디널리티 라벨 매칭?", "값이 무한한 라벨에 와일드카드",
         "계측 단계 라벨 설계 재검토"),
        (31, "rate 전에 집계했나?", "sum 먼저, rate 나중",
         "sum(rate(x[5m])) 순서로 재배치"),
        (18, "무거운 집계를 반복 조회?", "대시보드가 매번 재계산",
         "Recording Rule로 사전 계산"),
    ]
    for yc, q, qd, a in decisions:
        d.box(11, yc - 3.5, 32, 7, P["brown"])
        d.text(27, yc + 1, q, size=9.5, weight="bold")
        d.text(27, yc - 1.8, qd, size=7.5, color=P["dim"])
        d.box(58, yc - 3.5, 32, 7, P["green"])
        d.text(74, yc, a, size=9.5, weight="bold", color=P["accent"])
        d.arrow(43, yc, 58, yc, color=P["accent"])
        d.text(50.5, yc + 1.6, "Yes", size=8, color=P["accent"], weight="bold")

    # 최종 폴백
    d.box(11, 3.5, 32, 7, P["blue"])
    d.text(27, 7, "스크레이프 간격 · 타임아웃 점검", size=9, weight="bold")

    segs = [(51, 47.5), (40.5, 34.5), (27.5, 21.5), (14.5, 10.5)]
    for y1, y2 in segs:
        d.arrow(27, y1, 27, y2, color=P["dim"])
    for y in [37.5, 24.5, 12.5]:
        d.text(30.5, y, "No", size=8, color=P["dim"], weight="bold")

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.5, label="Yes → 해결책"),
        Line2D([0], [0], color=P["dim"], lw=2.5, label="No → 다음 항목"),
    ])


diagram("10-antipattern-decision", draw, w=13, h=7.2, ymax=59)
