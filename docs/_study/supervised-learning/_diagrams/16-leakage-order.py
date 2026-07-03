"""CH16 전처리 leakage — 전체에 fit(누출) vs split 후 train에만 fit(올바름) (light/dark PNG)."""
from _common import diagram


def _row(d, y, title, steps, bad):
    P = d.P
    warn = P["orange"]
    d.text(2, y + 6.5, title, size=10, weight="bold",
           color=warn if bad else P["accent"], ha="left")
    x = 2
    for i, (label, fc) in enumerate(steps):
        w = 19
        d.box(x, y, w, 5.5, fc)
        d.text(x + w / 2, y + 2.75, label, size=8.8)
        if i < len(steps) - 1:
            d.arrow(x + w, y + 2.75, x + w + 5, y + 2.75,
                    color=warn if bad else P["accent"], lw=1.6)
        x += w + 5


def draw(d):
    P = d.P
    bad_fit = P["brown"]
    good_fit = P["blue"]

    # 잘못된 순서: 전체 데이터에 fit → 그 다음 split
    _row(d, 20, "누출: 전체 데이터에 fit 먼저", [
        ("전체 fit_transform\n(scaler·encoder)", bad_fit),
        ("train / test\nsplit", P["gray"]),
        ("모델 학습·평가", P["gray"]),
    ], bad=True)
    d.text(2, 16.5, "test의 통계(평균·분산·타깃)가 전처리에 새어 들어감 → 낙관적 점수",
           size=8.4, color=P["orange"], ha="left", style="italic")

    # 올바른 순서: split 먼저 → train에만 fit
    _row(d, 5, "올바름: split 후 train에만 fit", [
        ("train / test\nsplit", P["gray"]),
        ("train에만 fit\n(Pipeline)", good_fit),
        ("test는 transform만", P["green"]),
    ], bad=False)


diagram("16-leakage-order", draw, w=12, h=4.4, ymax=30)
