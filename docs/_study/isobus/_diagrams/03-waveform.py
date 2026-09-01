"""CH3 §3 이상적인 CAN 파형 — CAN_H / CAN_L(반전) / Diff(차동 전압) (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    ax = d.ax

    # 펄스 패턴: 0(low)과 1(high)이 번갈아 나오는 구형파, 구간 폭 10, 6구간
    seg_w = 10
    x0 = 8
    n_segs = 6
    pattern = [0, 1, 0, 1, 0, 1]  # 1 = 신호 high 구간

    def steps(base_y, high_y, low_y):
        xs, ys = [], []
        x = x0
        prev = None
        for v in pattern:
            y = high_y if v else low_y
            if prev is not None and prev != y:
                xs.append(x); ys.append(prev)
                xs.append(x); ys.append(y)
            xs.append(x); ys.append(y)
            xs.append(x + seg_w); ys.append(y)
            prev = y
            x += seg_w
        return xs, ys

    row_h = 14
    y_h = 38   # CAN_H row baseline(top)
    y_l = 22   # CAN_L row baseline
    y_d = 6    # Diff row baseline

    # CAN_H: high=+row_h/2, low=0 (기준선 대비)
    hi, lo = row_h * 0.6, 0
    xs, ys = steps(y_h, y_h + hi, y_h + lo)
    ax.plot(xs, ys, color=P["accent"], lw=2.2)
    ax.plot([x0, x0 + seg_w * n_segs], [y_h, y_h], color=P["dim"], lw=0.5, ls=":", zorder=1)
    d.text(x0 - 4, y_h + hi / 2, "CAN_H", size=11, color=P["accent"], weight="bold", ha="right")

    # CAN_L: CAN_H의 반전
    pattern_inv = [1 - v for v in pattern]

    def steps_inv(base_y, high_y, low_y):
        xs, ys = [], []
        x = x0
        prev = None
        for v in pattern_inv:
            y = high_y if v else low_y
            if prev is not None and prev != y:
                xs.append(x); ys.append(prev)
                xs.append(x); ys.append(y)
            xs.append(x); ys.append(y)
            xs.append(x + seg_w); ys.append(y)
            prev = y
            x += seg_w
        return xs, ys

    xs, ys = steps_inv(y_l, y_l + hi, y_l + lo)
    ax.plot(xs, ys, color=P["orange"], lw=2.2)
    ax.plot([x0, x0 + seg_w * n_segs], [y_l, y_l], color=P["dim"], lw=0.5, ls=":", zorder=1)
    d.text(x0 - 4, y_l + hi / 2, "CAN_L", size=11, color=P["orange"], weight="bold", ha="right")
    d.text(x0 + seg_w * n_segs + 2, y_l + hi + 1, "반전\n(CAN_H와 대칭)", size=8, color=P["dim"], ha="left", va="bottom")

    # Diff = CAN_H - CAN_L : pattern이 1일 때 high(차동 전압 발생), 0일 때 0V
    xs, ys = steps(y_d, y_d + hi, y_d + lo)
    ax.plot(xs, ys, color=P["violet"], lw=2.2)
    ax.plot([x0, x0 + seg_w * n_segs], [y_d, y_d], color=P["dim"], lw=0.5, ls=":", zorder=1)
    d.text(x0 - 4, y_d + hi / 2, "Diff", size=11, color=P["violet"], weight="bold", ha="right")
    d.text(x0 - 4, y_d + lo - 3, "0V", size=8, color=P["dim"], ha="right")
    d.text(x0 + seg_w * n_segs + 2, y_d + hi / 2, "CAN_H - CAN_L\n(차동 전압)", size=8, color=P["dim"], ha="left", va="center")

    # 세로 점선으로 세 파형을 정렬해서 보여준다
    for i in range(n_segs + 1):
        xb = x0 + seg_w * i
        ax.plot([xb, xb], [2, 46], color=P["dim"], lw=0.4, ls=":", alpha=0.4, zorder=0)


diagram("03-waveform", draw, w=13, h=6, xmax=100, ymax=50)
