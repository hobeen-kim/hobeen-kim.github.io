"""CH8 SVM 마진 최대화 — 서포트 벡터가 결정 경계와 마진을 정한다 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # 두 클래스 (선형 분리 가능). 합 x+y 로 배치.
    class_a = [(1, 2), (2, 2), (1, 4), (3, 3), (2, 5)]   # x+y <= 8
    class_b = [(8, 6), (6, 8), (9, 7), (7, 9)]           # x+y >= 12
    sv_a = [(4, 4), (2, 6)]                               # x+y = 8  (마진 위)
    sv_b = [(6, 6), (8, 4)]                               # x+y = 12 (마진 위)

    ax_a = [p[0] for p in class_a]; ay_a = [p[1] for p in class_a]
    ax_b = [p[0] for p in class_b]; ay_b = [p[1] for p in class_b]
    d.ax.scatter(ax_a, ay_a, s=70, color=P["accent"], zorder=5)
    d.ax.scatter(ax_b, ay_b, s=70, color=P["orange"], zorder=5)

    # 서포트 벡터: 같은 색 + 굵은 테두리 링
    for (x, y) in sv_a:
        d.ax.scatter([x], [y], s=150, color=P["accent"],
                     edgecolors=P["text"], linewidths=2.0, zorder=6)
    for (x, y) in sv_b:
        d.ax.scatter([x], [y], s=150, color=P["orange"],
                     edgecolors=P["text"], linewidths=2.0, zorder=6)

    # 결정 경계 x+y=10, 마진 경계 x+y=8 / x+y=12
    d.ax.plot([0.5, 9.5], [9.5, 0.5], color=P["text"], lw=2.0, zorder=3)
    d.ax.plot([0.5, 7.5], [7.5, 0.5], color=P["dim"], lw=1.3, ls="--", zorder=2)
    d.ax.plot([2.5, 9.5], [9.5, 2.5], color=P["dim"], lw=1.3, ls="--", zorder=2)

    d.text(8.4, 9.0, "결정 경계", size=10, color=P["text"], weight="bold")
    d.text(1.4, 6.4, "마진", size=9.5, color=P["dim"])
    d.text(9.0, 4.2, "마진", size=9.5, color=P["dim"])
    d.text(4.6, 4.4, "서포트 벡터", size=8.8, color=P["dim"], ha="left")

    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=P["accent"],
               markersize=9, label="클래스 A"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=P["orange"],
               markersize=9, label="클래스 B"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=P["dim"],
               markeredgecolor=P["text"], markeredgewidth=2, markersize=11,
               label="서포트 벡터"),
    ]
    d.legend(handles, loc="upper left", anchor=(0.01, 0.99))


diagram("08-margin", draw, w=7.5, h=6, xmax=10, ymax=10)
