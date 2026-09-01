"""CH3 §1 CAN_H/CAN_L 전압 레벨 — Dominant/Recessive (light/dark PNG)."""
from _common import diagram


def v_to_y(v):
    # 전압(1.0~4.5V 근사)을 y축(0~50) 좌표로 매핑
    return 12 + (v - 1.0) * 8


def draw(d):
    P = d.P
    ax = d.ax

    seg_w = 20
    x0 = 5
    # 4구간: Dominant(bit0) / Recessive(bit1) 반복
    segs = ["dom", "rec", "dom", "rec"]
    labels = [("Dominant", "bit 0"), ("Recessive", "bit 1"), ("Dominant", "bit 0"), ("Recessive", "bit 1")]

    # 기준 전압 점선
    for v in (1.5, 2.5, 3.5):
        ax.plot([x0, x0 + seg_w * len(segs)], [v_to_y(v), v_to_y(v)],
                color=P["dim"], lw=0.6, ls=":", zorder=1)

    # CAN_H / CAN_L 계단파 (수평 구간 + 구간 경계 수직선)
    x = x0
    for i, seg in enumerate(segs):
        vh = 3.5 if seg == "dom" else 2.5
        vl = 1.5 if seg == "dom" else 2.5
        ax.plot([x, x + seg_w], [v_to_y(vh), v_to_y(vh)], color=P["accent"], lw=2.4)
        ax.plot([x, x + seg_w], [v_to_y(vl), v_to_y(vl)], color=P["orange"], lw=2.4)
        if i > 0:
            vh_prev = 3.5 if segs[i - 1] == "dom" else 2.5
            vl_prev = 1.5 if segs[i - 1] == "dom" else 2.5
            ax.plot([x, x], [v_to_y(vh_prev), v_to_y(vh)], color=P["accent"], lw=2.4)
            ax.plot([x, x], [v_to_y(vl_prev), v_to_y(vl)], color=P["orange"], lw=2.4)
        x += seg_w

    # y축 전압 라벨
    d.text(x0 - 2, v_to_y(3.5), "3.5V", size=9, color=P["dim"], ha="right")
    d.text(x0 - 2, v_to_y(2.5), "2.5V", size=9, color=P["dim"], ha="right")
    d.text(x0 - 2, v_to_y(1.5), "1.5V", size=9, color=P["dim"], ha="right")

    # 선 라벨
    d.text(x0 + seg_w * len(segs) + 4, v_to_y(3.5) + 2.5, "CAN_H", size=11, color=P["accent"], weight="bold", ha="left")
    d.text(x0 + seg_w * len(segs) + 4, v_to_y(1.5) - 2.5, "CAN_L", size=11, color=P["orange"], weight="bold", ha="left")

    # 구간별 상태/비트 라벨 + 구분 점선
    x = x0
    for (name, bit) in labels:
        cx = x + seg_w / 2
        d.text(cx, 8, name, size=9.5, color=P["text"])
        d.text(cx, 4, bit, size=9, color=P["dim"])
        x += seg_w
    for i in range(len(segs) + 1):
        xb = x0 + seg_w * i
        ax.plot([xb, xb], [10, 44], color=P["dim"], lw=0.5, ls=":", alpha=0.5, zorder=1)


diagram("03-voltage-levels", draw, w=12, h=6, ymax=50)
