"""CH1 2절 아날로그 신호와 디지털 신호: 같은 노이즈가 섞였을 때의 차이 (light/dark PNG)."""
import numpy as np

from _common import diagram


def vy(v):
    # 전압 0~5V를 y 9~30 좌표로 옮긴다
    return 9 + v * 4.2


def draw(d):
    P = d.P
    ax = d.ax
    rng = np.random.default_rng(7)

    def panel(x0, title):
        d.box(x0, 2, 45, 37, P["gray"])
        d.text(x0 + 2, 36.4, title, size=11, weight="bold", ha="left")

    def volt_axis(x_left, x_right, levels):
        for v in levels:
            ax.plot([x_left, x_right], [vy(v), vy(v)], color=P["edge"], lw=0.7, ls=":", zorder=1)
            d.text(x_left - 0.8, vy(v), f"{v}V", size=9, color=P["dim"], ha="right")

    # 왼쪽: 아날로그
    panel(2, "아날로그")
    volt_axis(10, 45, (0, 5))
    xs = np.linspace(10, 45, 500)
    clean = 2.5 + 1.7 * np.sin((xs - 10) / 35 * 2 * np.pi * 1.25)
    noisy = clean + rng.normal(0, 0.16, xs.size)
    ax.plot(xs, vy(noisy), color=P["accent"], lw=1.4, zorder=3)
    ax.plot(xs, vy(clean), color=P["orange"], lw=1.6, ls="--", zorder=4)
    d.text(10, 5, "점선: 원래 값", size=9.5, color=P["orange"], ha="left")
    d.text(24, 5, "실선: 노이즈가 섞인 값", size=9.5, color=P["accent"], ha="left")

    # 오른쪽: 디지털
    panel(53, "디지털")
    volt_axis(61, 96, (0, 2.5, 5))
    bits = [1, 0, 1, 1, 0, 1]
    seg = 35 / len(bits)
    xs_all, vs_all = [], []
    for i, b in enumerate(bits):
        x0 = 61 + i * seg
        xs_seg = np.linspace(x0, x0 + seg, 80)
        vs_seg = 5.0 * b + rng.normal(0, 0.22, xs_seg.size)
        xs_all.extend(xs_seg)
        vs_all.extend(vs_seg)
        d.text(x0 + seg / 2, vy(5) + 3.2, str(b), size=12, weight="bold", color=P["accent"])
    ax.plot(xs_all, [vy(v) for v in vs_all], color=P["accent"], lw=1.4, zorder=3)
    ax.plot([61, 96], [vy(2.5), vy(2.5)], color=P["orange"], lw=1.4, ls="--", zorder=2)
    d.text(61, 5, "점선: 기준 2.5V", size=9.5, color=P["orange"], ha="left")


diagram("01-analog-vs-digital", draw, w=12, h=4.9, xmax=100, ymax=41)
