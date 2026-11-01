"""CH3 7절 농기계 9핀 커넥터 핀 배치 예시: 핀 번호와 신호를 용도별 색으로 구분 (light/dark PNG)."""
from matplotlib.patches import Circle, Patch

from _common import diagram

PINS = [
    (1, "Battery(+12V)", "brown"), (2, "Ignition(+12V)", "brown"), (3, "GND", "green"),
    (4, "ECU_GND", "green"), (5, "CAN_H (ISOBUS)", "blue"), (6, "CAN_L (ISOBUS)", "blue"),
    (7, "LIN Bus", "purple"), (8, "Reserved", "purple"), (9, "CAN_H (진단 전용)", "blue"),
]


def draw(d):
    P = d.P
    ax = d.ax
    cw, chh = 29, 9
    for i, (no, label, key) in enumerate(PINS):
        col, row = i % 3, i // 3
        x = 4 + col * (cw + 3)
        y = 27 - row * (chh + 3)
        d.box(x, y, cw, chh, P[key])
        ax.add_patch(Circle((x + 5, y + chh / 2), 2.9, facecolor=P["bg"],
                            edgecolor=P["edge"], linewidth=1.3, zorder=3))
        d.text(x + 5, y + chh / 2, str(no), size=11, weight="bold")
        d.text(x + 10, y + chh / 2, label, size=10.5, ha="left")

    handles = [Patch(facecolor=P[k], edgecolor=P["edge"], label=t)
               for k, t in (("brown", "전원"), ("green", "접지"), ("blue", "CAN"), ("purple", "기타"))]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.03, 1.0), ncol=4,
              fontsize=10, framealpha=0.0, labelcolor=P["dim"], handlelength=1.4)


diagram("03-ag-connector-pins", draw, w=11, h=4.6, xmax=100, ymax=42)
