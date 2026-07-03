"""CH10 회귀 트리 — 분산(MSE) 감소로 구간을 나누고 리프의 평균값을 예측 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # 리프 4개: 임계값 2.5 / 5 / 8 로 x를 나눈 뒤 각 구간 평균을 예측
    leaves = [
        ([(0.5, 1.8), (1, 2.2), (1.5, 1.9), (2, 2.3)], 0.0, 2.5, 2.05),
        ([(3, 4.7), (3.5, 5.2), (4, 4.9), (4.5, 5.3)], 2.5, 5.0, 5.02),
        ([(6, 3.7), (6.5, 4.2), (7, 3.9), (7.5, 4.1)], 5.0, 8.0, 3.98),
        ([(8.5, 6.7), (9, 7.2), (9.5, 7.0)], 8.0, 10.0, 6.97),
    ]

    # 점들
    xs = [p[0] for lv in leaves for p in lv[0]]
    ys = [p[1] for lv in leaves for p in lv[0]]
    d.ax.scatter(xs, ys, s=55, color=P["accent"], zorder=5)

    # 리프별 평균값 예측 (계단)
    for pts, xl, xr, mean in leaves:
        d.ax.plot([xl, xr], [mean, mean], color=P["orange"], lw=2.6, zorder=4)

    # 분할 경계 (임계값)
    for thr in (2.5, 5.0, 8.0):
        d.ax.plot([thr, thr], [0, 8], color=P["dim"], lw=1.1, ls="--", zorder=2)
        d.text(thr, 0.3, f"x<{thr}", size=8, color=P["dim"])

    d.ax.plot([0, 10], [0, 0], color=P["edge"], lw=1.0)
    d.text(5, -0.7, "특징 x", size=9.5, color=P["dim"])
    d.text(0.2, 7.6, "예측값 (리프의 평균)", size=9.5, color=P["dim"], ha="left")

    d.ax.set_xlim(-0.2, 10.5)
    d.ax.set_ylim(-1.1, 8.2)
    d.legend([
        Line2D([0], [0], marker="o", color="none", markerfacecolor=P["accent"],
               markersize=8, label="데이터"),
        Line2D([0], [0], color=P["orange"], lw=2.6, label="리프 평균 예측"),
    ], loc="lower right", anchor=(0.99, 0.02))


diagram("10-regression-tree", draw, w=8, h=5, xmax=10, ymax=8)
