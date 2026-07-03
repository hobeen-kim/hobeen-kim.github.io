"""CH1 fit/predict 계약 — 학습 데이터(X,y)로 f를 학습하고 새 입력에 예측 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 학습 단계 (윗줄)
    d.box(2, 30, 20, 14, P["blue"])
    d.text(12, 41, "학습 데이터", size=10.5, weight="bold")
    d.text(12, 36.5, "X (특징 행렬)\ny (정답 레이블)", size=9.2, color=P["dim"])

    d.box(40, 31, 20, 12, P["gray"], ec=P["accent"], lw=1.8)
    d.text(50, 39.5, "모델 f", size=11, weight="bold", color=P["accent"])
    d.text(50, 35, "파라미터 학습", size=9, color=P["dim"])

    d.arrow(22, 37, 40, 37)
    d.text(31, 39, "fit(X, y)", size=9.5, color=P["accent"])

    # 예측 단계 (아랫줄)
    d.box(2, 5, 20, 12, P["green"])
    d.text(12, 13.5, "새 입력", size=10.5, weight="bold")
    d.text(12, 9.5, "X_new\n(정답 없음)", size=9.2, color=P["dim"])

    d.box(78, 5, 20, 12, P["brown"])
    d.text(88, 13.5, "예측 y_hat", size=10.5, weight="bold")
    d.text(88, 9.5, "회귀: 실수\n분류: 클래스", size=9.2, color=P["dim"])

    # 학습된 모델을 예측에 재사용
    d.arrow(50, 31, 50, 11, color=P["orange"], ls="--")
    d.text(58, 22, "학습된 f 고정", size=8.8, color=P["orange"])

    d.arrow(22, 11, 40, 11)
    d.arrow(60, 11, 78, 11)
    d.text(50, 8.5, "predict(X_new)", size=9.5, color=P["accent"])
    d.box(40, 6, 20, 10, P["gray"], ec=P["edge"], lw=1.2, alpha=0.5)


diagram("01-fit-predict", draw, w=12, h=5.6, ymax=48)
