"""GBDT 하이퍼파라미터 역할군 지도 — 4개 축과 대표 파라미터 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    groups = [
        ("구조 (복잡도)", P["blue"],
         "max_depth\nnum_leaves\nmin_child_weight\nmin_child_samples"),
        ("샘플링 (다양성)", P["green"],
         "subsample\ncolsample_bytree\ncolsample_bylevel"),
        ("정규화 (벌점)", P["purple"],
         "reg_lambda (L2)\nreg_alpha (L1)\nmin_split_gain"),
        ("속도-품질 (수렴)", P["brown"],
         "learning_rate\nn_estimators\nearly_stopping"),
    ]
    w, gap = 21, 3
    x0 = 2
    for i, (title, fc, items) in enumerate(groups):
        x = x0 + i * (w + gap)
        d.box(x, 4, w, 30, fc)
        d.text(x + w / 2, 30, title, size=10.5, weight="bold")
        d.text(x + w / 2, 16, items, size=9.2, color=P["dim"])

    # 과적합 ↔ 과소적합 방향축
    d.arrow(3, 39, 45, 39, color=P["accent"], lw=1.6)
    d.text(4, 41, "복잡도 ↑ · 규제 ↓ → 과적합", size=9, color=P["accent"], ha="left")
    d.arrow(95, 39, 53, 39, color=P["orange"], lw=1.6)
    d.text(96, 41, "규제 ↑ · 복잡도 ↓ → 과소적합", size=9, color=P["orange"], ha="right")


diagram("15-param-groups", draw, w=12.5, h=4.6, xmax=100, ymax=44)
