"""CH6 6절 에러 카운터 따라가기: 이벤트마다 TEC와 REC가 움직이는 모습과 상태 경계 (light/dark PNG)."""
from matplotlib.lines import Line2D

from _common import diagram

TEC = [0, 8, 16, 24, 24, 128, 127, 135, 135, 255, 263]
REC = [0, 0, 0, 0, 1, 1, 1, 1, 9, 9, 9]
X0, DX = 14, 8.0
Y0, SY = 8, 0.165


def px(i):
    return X0 + i * DX


def py(v):
    return Y0 + v * SY


def draw(d):
    P = d.P
    ax = d.ax
    x_end = px(len(TEC) - 1) + 4

    bands = ((0, 128, P["green"], "Error Active"), (128, 256, P["brown"], "Error Passive"),
             (256, 290, P["purple"], "Bus Off"))
    for lo, hi, fc, name in bands:
        d.box(X0 - 4, py(lo), x_end - X0 + 4, py(hi) - py(lo), fc, ec=fc, lw=0.5, r=0.0, alpha=0.55)
        d.text(x_end + 1.2, (py(lo) + py(hi)) / 2, name, size=8.8, ha="left", weight="bold")

    for v, label in ((128, "128"), (255, "255")):
        ax.plot([X0 - 4, x_end], [py(v), py(v)], color=P["edge"], lw=1.0, ls=(0, (4, 3)), zorder=3)
        d.text(X0 - 5, py(v), label, size=8.2, ha="right", color=P["dim"])
    d.text(X0 - 5, py(0), "0", size=8.2, ha="right", color=P["dim"])

    xs = [px(i) for i in range(len(TEC))]
    ax.step(xs, [py(v) for v in TEC], where="post", color=P["accent"], lw=2.0, zorder=4)
    ax.plot(xs, [py(v) for v in TEC], "o", color=P["accent"], ms=4.5, zorder=5)
    ax.step(xs, [py(v) for v in REC], where="post", color=P["violet"], lw=1.6, zorder=4)

    for i, v in enumerate(TEC):
        if i in (0, 4, 8):
            continue
        dy = 2.2 if i not in (6,) else -2.6
        d.text(px(i), py(v) + dy, str(v), size=8.2, color=P["accent"], weight="bold")
    d.text(px(10), py(9) + 2.0, "REC 9", size=8.2, color=P["violet"])

    for i in range(len(TEC)):
        d.text(px(i), Y0 - 3.2, str(i), size=8.2, color=P["dim"])

    d.legend([Line2D([0], [0], color=P["accent"], lw=2.0, label="TEC"),
              Line2D([0], [0], color=P["violet"], lw=1.6, label="REC")],
             loc="upper left", anchor=(0.02, 0.98), fontsize=8.8)


diagram("06-tec-timeline", draw, w=11, h=5.4, xmax=112, ymax=60)
