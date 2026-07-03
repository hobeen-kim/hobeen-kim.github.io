"""CH19 실무 워크플로우 체인 — 문제 정의부터 배포·감시까지, 감시에서 관측성으로 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    steps = [
        ("문제 정의", "지표·제약 확정", P["gray"]),
        ("데이터 분할", "leakage 차단", P["blue"]),
        ("베이스라인", "로지스틱→GBDT", P["green"]),
        ("피처 엔지니어링", "Pipeline 내부", P["green"]),
        ("튜닝", "CV·early stop", P["brown"]),
        ("해석", "permutation·SHAP", P["purple"]),
        ("배포·감시", "드리프트 추적", P["gray"]),
    ]

    w, gap = 11.5, 1.7
    x0 = 1.5
    y = 20
    for i, (title, sub, fc) in enumerate(steps):
        x = x0 + i * (w + gap)
        d.box(x, y, w, 9, fc)
        d.text(x + w / 2, y + 6.0, title, size=9, weight="bold")
        d.text(x + w / 2, y + 2.6, sub, size=7.6, color=P["dim"])
        if i:
            d.arrow(x - gap + 0.2, y + 4.5, x - 0.2, y + 4.5, color=P["edge"])

    # 배포·감시 → 관측성 스터디로 곁가지
    xl = x0 + 6 * (w + gap)
    d.box(xl - 2, 5, w + 4, 7, P["chip"], ec=P["accent"], lw=1.5)
    d.text(xl + w / 2 - 2, 8.5, "→ 관측성 스터디", size=8.2, color=P["accent"])
    d.arrow(xl + w / 2, y, xl + w / 2, 12, color=P["accent"], lw=1.3,
            ls=(0, (3, 3)))

    # 튜닝↔해석↔피처 반복 루프 힌트
    d.arrow(x0 + 5 * (w + gap) + w / 2, y, x0 + 3 * (w + gap) + w / 2, y,
            color=P["orange"], lw=1.2, rad=0.25, ls=(0, (2, 2)))
    d.text(x0 + 4 * (w + gap) + w / 2, y - 4.5, "반복", size=7.8,
           color=P["orange"])


diagram("19-workflow-chain", draw, w=13.5, h=4.2, ymax=32)
