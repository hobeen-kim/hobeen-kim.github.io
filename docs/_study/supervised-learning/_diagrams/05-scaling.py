"""CH5 스케일링의 필요성 — 단위가 다르면 거리가 왜곡된다 (light/dark PNG).

왼쪽: 나이(0~60)와 연봉(0~1억)을 원단위로 두면 거리가 사실상 연봉
한 축에 지배당해 엉뚱한 이웃이 잡힌다. 오른쪽: 표준화하면 두 축이
동등해져 이웃이 바뀐다.
"""
import numpy as np
from _common import diagram


def draw(d):
    P = d.P
    fig = d.fig
    d.ax.axis("off")

    # 공통 데이터 (나이, 연봉만원)
    age = np.array([28, 45, 33, 52, 24, 40, 30, 48])
    pay = np.array([3200, 3400, 8600, 3100, 8900, 8700, 3300, 8500])
    q = np.array([31, 8800.0])  # 질의점: 젊고 고연봉

    def panel(rect, X, Y, qx, qy, title, xlab, ylab):
        ax = fig.add_axes(rect)
        ax.set_facecolor(P["bg"])
        for s in ax.spines.values():
            s.set_color(P["edge"])
        ax.tick_params(colors=P["dim"], labelsize=7.5, length=0)
        ax.set_title(title, fontsize=10.5, color=P["text"], pad=8)
        ax.set_xlabel(xlab, fontsize=8.5, color=P["dim"])
        ax.set_ylabel(ylab, fontsize=8.5, color=P["dim"])
        d2 = (X - qx) ** 2 + (Y - qy) ** 2
        nn = int(np.argmin(d2))
        ax.scatter(X, Y, s=70, color=P["blue"], edgecolor=P["edge"],
                   linewidth=0.6, zorder=3)
        ax.scatter([X[nn]], [Y[nn]], s=140, color=P["green"],
                   edgecolor=P["accent"], linewidth=1.6, zorder=4)
        ax.plot([qx, X[nn]], [qy, Y[nn]], color=P["accent"], linewidth=1.3,
                linestyle="--", zorder=2)
        ax.scatter([qx], [qy], marker="*", s=300, color=P["orange"],
                   edgecolor=P["bg"], linewidth=0.8, zorder=5)
        return nn

    # 왼쪽: 원단위 — 연봉 축이 거리를 지배
    n1 = panel([0.08, 0.14, 0.38, 0.72], age, pay, q[0], q[1],
               "표준화 전 — 연봉이 거리를 지배", "나이", "연봉(만원)")

    # 오른쪽: 표준화
    az = (age - age.mean()) / age.std()
    pz = (pay - pay.mean()) / pay.std()
    qz = np.array([(q[0] - age.mean()) / age.std(),
                   (q[1] - pay.mean()) / pay.std()])
    n2 = panel([0.58, 0.14, 0.38, 0.72], az, pz, qz[0], qz[1],
               "표준화 후 — 두 축이 동등", "나이(z)", "연봉(z)")

    d.text(50, 2.2,
           "같은 질의점인데 최근접 이웃(초록 테두리)이 바뀐다",
           size=9, color=P["dim"], ha="center")


diagram("05-scaling", draw, w=12, h=5, ymax=50)
