"""README 학습 로드맵 — 기초 → 거리·선형 → 트리·앙상블 → 실전 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    stages = [
        ("기초 (01~04)", P["gray"],
         "지도 학습 개요\n일반화·과적합\n평가 지표\n교차 검증·튜닝"),
        ("거리·선형 모델 (05~09)", P["blue"],
         "kNN\n선형 회귀·정규화\n로지스틱 회귀\nSVM · 나이브 베이즈"),
        ("트리와 앙상블 (10~15)", P["green"],
         "결정 트리\n배깅·부스팅·스태킹\n랜덤 포레스트\nGB 원리 → XGB·LGBM·CatBoost\nGBDT 실전 튜닝"),
        ("실전 (16~19)", P["brown"],
         "피처 엔지니어링·파이프라인\n불균형·캘리브레이션\n모델 해석 (SHAP)\n모델 선택 가이드"),
    ]
    w, gap = 22, 3.2
    x0 = 1.5
    for i, (title, fc, items) in enumerate(stages):
        x = x0 + i * (w + gap)
        d.box(x, 3, w, 24, fc)
        d.text(x + w / 2, 24, title, size=10.5, weight="bold")
        d.text(x + w / 2, 13, items, size=8.8, color=P["dim"])
        if i:
            d.arrow(x - gap + 0.4, 15, x - 0.4, 15)


diagram("readme-roadmap", draw, w=13, h=3.9, ymax=30)
