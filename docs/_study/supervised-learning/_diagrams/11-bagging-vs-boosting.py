"""CH11 배깅 vs 부스팅 구조 비교 — 병렬 독립 트리 vs 순차 보정 체인 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # ── 왼쪽: 배깅 (병렬 독립 학습 → 집계)
    d.box(2, 4, 44, 40, P["gray"], ec=P["green"], lw=1.8)
    d.text(24, 41, "배깅 — 병렬 · 독립", size=11, weight="bold", color=P["green"])

    # 부트스트랩 표본 → 트리 (3개 병렬)
    ys = [30, 21, 12]
    for i, y in enumerate(ys):
        d.box(5, y, 12, 6, P["chip"])
        d.text(11, y + 3, f"표본 {i+1}", size=8.5, color=P["dim"])
        d.box(21, y, 10, 6, P["green"])
        d.text(26, y + 3, f"트리 {i+1}", size=9)
        d.arrow(17, y + 3, 21, y + 3, color=P["edge"], lw=1.4)
    # 집계
    d.box(35, 18, 8, 10, P["blue"])
    d.text(39, 23, "집계\n(평균/\n투표)", size=8.2)
    for y in ys:
        d.arrow(31, y + 3, 35, 23, color=P["edge"], lw=1.2, rad=0.05)
    d.text(24, 7.5, "표본끼리 서로 모른다 → 분산 감소", size=8.4,
           color=P["dim"], style="italic")

    # ── 오른쪽: 부스팅 (순차 오류 보정 체인)
    d.box(54, 4, 44, 40, P["gray"], ec=P["brown"], lw=1.8)
    d.text(76, 41, "부스팅 — 순차 · 보정", size=11, weight="bold", color=P["brown"])

    xs = [58, 74, 90]
    for i, x in enumerate(xs):
        d.box(x - 5, 24, 10, 8, P["brown"])
        d.text(x, 28, f"트리 {i+1}", size=9)
        if i:
            d.arrow(xs[i-1] + 5, 28, x - 5, 28, color=P["orange"], lw=1.6)
            d.text((xs[i-1] + x) / 2, 30.5, "오류", size=7.6, color=P["orange"])
    # 최종 합
    d.box(70, 10, 12, 7, P["blue"])
    d.text(76, 13.5, "가중 합", size=9)
    for x in xs:
        d.arrow(x, 24, 76, 17, color=P["edge"], lw=1.2, rad=0.04)
    d.text(76, 7, "다음 트리가 앞 트리의 오차를 배운다 → 편향 감소",
           size=8.4, color=P["dim"], style="italic")


diagram("11-bagging-vs-boosting", draw, w=13, h=5.4, ymax=46)
