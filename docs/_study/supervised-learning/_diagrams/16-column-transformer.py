"""CH16 ColumnTransformer 분기 — 컬럼 타입별 전처리가 갈라졌다 다시 합쳐져 모델로 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # ColumnTransformer 그룹 박스
    d.box(27, 7, 30, 37, P["gray"], ec=P["accent"], lw=1.6)
    d.text(42, 41.5, "ColumnTransformer", size=11, weight="bold", color=P["accent"])

    # 입력 데이터프레임
    d.box(2, 21, 16, 9, P["chip"], ec=P["edge"], lw=1.6)
    d.text(10, 25.5, "원본 DataFrame\n(수치+범주+결측)", size=9.2, weight="bold")

    # 세 갈래 전처리 브랜치
    branches = [
        (32, P["blue"], "수치형 컬럼",
         "SimpleImputer(median)\n→ StandardScaler"),
        (21.5, P["green"], "범주형 컬럼",
         "SimpleImputer(상수)\n→ OneHotEncoder"),
        (11, P["brown"], "고카디널리티",
         "TargetEncoder\n(fold 안에서만 fit)"),
    ]
    for y, fc, head, body in branches:
        d.box(29, y, 23, 8, fc)
        d.text(40.5, y + 5.6, head, size=9.2, weight="bold")
        d.text(40.5, y + 2.5, body, size=8.2, color=P["dim"])
        d.arrow(18, 25.5, 29, y + 4, color=P["edge"], lw=1.2)

    # 결합
    d.box(60, 21, 15, 9, P["purple"])
    d.text(67.5, 25.5, "hstack\n피처 결합", size=9.2, weight="bold")
    for y, *_ in branches:
        d.arrow(52, y + 4, 60, 25.5, color=P["edge"], lw=1.2)

    # 최종 estimator
    d.box(80, 21, 17, 9, P["chip"], ec=P["accent"], lw=1.8)
    d.text(88.5, 25.5, "Estimator\n.fit / .predict", size=9.2, weight="bold")
    d.arrow(75, 25.5, 80, 25.5, color=P["accent"], lw=1.8)


diagram("16-column-transformer", draw, w=12.5, h=5.6, ymax=46)
