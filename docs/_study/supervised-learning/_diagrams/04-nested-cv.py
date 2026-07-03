"""CH4 중첩 교차 검증 — 바깥 루프(평가) 안에 안쪽 루프(튜닝) (light/dark PNG).

바깥 폴드는 모델을 '평가'하고, 각 바깥-train 안에서 안쪽 k-fold가
하이퍼파라미터를 '선택'한다. 두 역할을 분리해야 튜닝이 평가 점수를
낙관적으로 오염시키지 않는다.
"""
from _common import diagram, Line2D


def draw(d):
    P = d.P
    train, val = P["blue"], P["orange"]
    cw, chh, step = 7.0, 3.2, 7.6

    # --- 바깥 루프 ---
    d.text(2, 44, "바깥 루프 — 성능 평가", size=11, weight="bold", ha="left")
    x0 = 10
    n = 5
    for f in range(3):
        y = 40 - f * (chh + 1.0)
        d.text(x0 - 2, y + chh / 2, f"Outer {f+1}", size=8.5,
               color=P["dim"], ha="right")
        for i in range(n):
            c = val if i == f else train
            d.box(x0 + i * step, y, cw, chh, c, lw=0.8)

    # 강조: Outer 1 의 train 영역을 안쪽 루프로 확대
    d.text(x0 + 1.2 * step, 41.6, "이 train을 다시 쪼갬", size=8,
           color=P["accent"], ha="left")
    d.arrow(x0 + 4.6 * step, 39, 62, 34, color=P["accent"], rad=-0.2)

    # --- 안쪽 루프 ---
    d.text(58, 36, "안쪽 루프 — 하이퍼파라미터 선택", size=11,
           weight="bold", ha="left")
    ix0 = 62
    im = 4
    for f in range(3):
        y = 31 - f * (chh + 1.0)
        d.text(ix0 - 2, y + chh / 2, f"Inner {f+1}", size=8.5,
               color=P["dim"], ha="right")
        for i in range(im):
            c = val if i == f else train
            d.box(ix0 + i * step, y, cw, chh, c, lw=0.8)
    d.text(ix0, 12.5, "→ 각 후보 파라미터를 평가해\n   최적값 선택 후 바깥-train 전체로 재학습",
           size=8.5, color=P["dim"], ha="left")

    handles = [
        Line2D([0], [0], marker="s", linestyle="none", markersize=10,
               markerfacecolor=train, markeredgecolor=P["edge"], label="train"),
        Line2D([0], [0], marker="s", linestyle="none", markersize=10,
               markerfacecolor=val, markeredgecolor=P["edge"],
               label="검증 (바깥=test, 안쪽=valid)"),
    ]
    d.legend(handles, loc="lower left", anchor=(0.01, 0.02))


diagram("04-nested-cv", draw, w=12, h=6, ymax=48)
