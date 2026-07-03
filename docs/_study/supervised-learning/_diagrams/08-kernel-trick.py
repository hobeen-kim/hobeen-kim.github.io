"""CH8 커널 트릭 — 저차원에서 못 나누는 데이터를 고차원 매핑으로 선형 분리 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # 원 x 값 (중심 0): 안쪽 = 클래스 B, 바깥쪽 = 클래스 A
    a_orig = [-4, -3, 3, 4]
    b_orig = [-1, 0, 1]

    # 왼쪽: 1D 원 공간 (직선 하나로 못 나눔)
    d.text(5, 9.2, "원 공간 (1D)", size=10.5, weight="bold", color=P["accent"])
    d.ax.plot([2, 8], [5, 5], color=P["edge"], lw=1.2, zorder=1)
    for x in a_orig:
        d.ax.scatter([5 + x * 0.5], [5], s=80, color=P["orange"], zorder=5)
    for x in b_orig:
        d.ax.scatter([5 + x * 0.5], [5], s=80, color=P["accent"], zorder=5)
    d.text(5, 3.4, "직선 하나로 못 나눔", size=9, color=P["dim"])

    # 매핑 화살표
    d.arrow(9, 5, 11, 5, color=P["violet"])
    d.text(10, 6.1, "φ(x)=(x, x²)", size=9.5, color=P["violet"])

    # 오른쪽: 2D 특징 공간 (선형 초평면으로 분리)
    d.text(15, 9.2, "특징 공간 (2D)", size=10.5, weight="bold", color=P["accent"])
    for x in a_orig:
        d.ax.scatter([15 + x * 0.5], [1 + (x * x) / 16 * 7], s=80,
                     color=P["orange"], zorder=5)
    for x in b_orig:
        d.ax.scatter([15 + x * 0.5], [1 + (x * x) / 16 * 7], s=80,
                     color=P["accent"], zorder=5)
    d.ax.plot([12, 18], [3.5, 3.5], color=P["text"], lw=2.0, ls="--", zorder=3)
    d.text(18, 3.5, "초평면", size=9.5, color=P["text"], ha="left")

    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=P["orange"],
               markersize=9, label="클래스 A (바깥)"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=P["accent"],
               markersize=9, label="클래스 B (안쪽)"),
    ]
    d.legend(handles, loc="lower center", anchor=(0.5, 0.0))


diagram("08-kernel-trick", draw, w=11, h=5, xmax=20, ymax=10)
