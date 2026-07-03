"""CH18 해석 지도 — 전역(모델 전체) vs 국소(개별 예측) 방법 배치 (light/dark PNG).

학습된 모델을 사이에 두고, 왼쪽은 전역 해석 방법, 오른쪽은 국소 해석 방법.
SHAP은 두 세계를 잇는다. impurity importance는 편향 경고 표시.
"""
from _common import diagram


def draw(d):
    P = d.P

    # 가운데 모델
    d.box(41, 20, 18, 9, P["gray"], ec=P["accent"], lw=1.8)
    d.text(50, 24.5, "학습된 모델\nf(x)", size=10.5, weight="bold",
           color=P["accent"])

    # 전역 그룹
    d.box(2, 3, 36, 40, P["green"])
    d.text(20, 40, "전역 해석 (모델 전체 동작)", size=10.5, weight="bold")
    glob = [
        ("permutation importance", 33),
        ("PDP (부분 의존도)", 26.5),
        ("SHAP summary plot", 20),
        ("impurity importance (편향 주의)", 13.5),
    ]
    for label, y in glob:
        warn = "편향" in label
        d.box(5, y - 2.4, 30, 4.8, P["chip"],
              ec=P["orange"] if warn else P["edge"],
              lw=1.6 if warn else 1.0)
        d.text(20, y, label, size=8.8,
               color=P["orange"] if warn else P["text"])
    d.text(20, 7.5, "고카디널리티·train 기준 편향 → 12장 재방문",
           size=7.8, color=P["dim"])

    # 국소 그룹
    d.box(62, 3, 36, 40, P["blue"])
    d.text(80, 40, "국소 해석 (개별 예측 설명)", size=10.5, weight="bold")
    loc = [
        ("SHAP waterfall / force", 31),
        ("ICE (개별 조건부 기대)", 24),
        ("LIME (국소 근사)", 17),
    ]
    for label, y in loc:
        d.box(65, y - 2.4, 30, 4.8, P["chip"])
        d.text(80, y, label, size=8.8)

    # 모델 → 전역/국소
    d.arrow(41, 24.5, 38, 24.5, color=P["edge"])
    d.arrow(59, 24.5, 62, 24.5, color=P["edge"])
    # SHAP이 두 세계를 잇는다
    d.text(50, 14, "SHAP", size=9, weight="bold", color=P["violet"])
    d.arrow(43, 20, 22, 17.6, color=P["violet"], lw=1.4, rad=0.15)
    d.arrow(57, 20, 78, 28.6, color=P["violet"], lw=1.4, rad=-0.15)


diagram("18-interpretation-map", draw, w=12, h=5.6, ymax=45)
