"""CH19 모델 선택 결정 트리 — 데이터 타입·요구사항으로 갈라지는 선택 경로 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 루트
    d.box(38, 41, 24, 7, P["gray"], ec=P["accent"], lw=1.8)
    d.text(50, 44.5, "데이터가 어떤 형태?", size=10, weight="bold",
           color=P["accent"])

    # 1차 분기: 비정형 → 딥러닝
    d.box(70, 41, 26, 7, P["purple"])
    d.text(83, 44.5, "이미지·텍스트·음성\n→ 딥러닝(표현 학습)", size=8.8)
    d.arrow(62, 44.5, 70, 44.5, color=P["edge"])

    # 1차 분기: tabular
    d.box(38, 30, 24, 7, P["blue"])
    d.text(50, 33.5, "정형(tabular)\n무엇이 우선?", size=9, weight="bold")
    d.arrow(50, 41, 50, 37, color=P["edge"])

    # tabular 하위 분기 4갈래
    leaves = [
        (4,  "빠른 베이스라인", "로지스틱 회귀 · kNN", P["green"]),
        (28, "최고 예측 성능", "GBDT\n(XGBoost·LightGBM·CatBoost)", P["brown"]),
        (52, "강한 해석성·선형 관계", "규제 선형 · 얕은 트리", P["green"]),
        (76, "고차원 희소(BoW)", "선형 SVM · 나이브 베이즈", P["gray"]),
    ]
    for x, q, model, fc in leaves:
        d.box(x, 15, 20, 7, P["chip"])
        d.text(x + 10, 18.5, q, size=8.5)
        d.box(x, 3, 20, 8, fc)
        d.text(x + 10, 7, model, size=8.6)
        d.arrow(x + 10, 15, x + 10, 11, color=P["edge"])
        # 중앙 tabular 노드에서 각 질문으로
        d.arrow(50, 30, x + 10, 22, color=P["edge"], lw=1.2,
                rad=0.0 if abs(x + 10 - 50) < 3 else (0.1 if x < 50 else -0.1))


diagram("19-model-selection-tree", draw, w=12.5, h=6.0, ymax=50)
