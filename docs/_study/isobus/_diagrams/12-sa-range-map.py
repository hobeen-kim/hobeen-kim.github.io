"""CH12 SA 0~255 용도 지도: preferred, self-configurable, NULL, Global (light/dark PNG)."""
from _common import diagram

BLOCKS = [
    (4, 38, "blue", "0~127", "preferred", "기능별로 미리 배정"),
    (38, 74, "green", "128~247", "self-configurable", "주소를 스스로 고르는 CF가 사용"),
    (74, 87, "blue", "248~253", "preferred", "미리\n배정"),
    (87, 97.5, "brown", "254", "NULL", "소스\n전용"),
    (97.5, 108, "purple", "255", "Global", "목적지\n전용"),
]
IMPLEMENT_UPPER_SPLIT_X = 66


def draw(d):
    P = d.P
    y0, h = 11, 10
    for x0, x1, color, value_range, name, role in BLOCKS:
        d.box(x0 + 0.25, y0, x1 - x0 - 0.5, h, P[color], r=0.01)
        cx = (x0 + x1) / 2
        size = 8.6 if x1 - x0 < 14 else 9.6
        d.text(cx, y0 + h * 0.66, name, size=size, weight="bold")
        d.text(cx, y0 + h * 0.3, value_range, size=size)
        d.text(cx, y0 + h + 3.6, role, size=8.2, color=P["dim"])

    split = IMPLEMENT_UPPER_SPLIT_X
    d.ax.plot([split, split], [y0 + 0.3, y0 + h - 0.3], color=P["edge"],
              lw=1.0, ls=(0, (3, 2)), zorder=6)
    for a, b, label in ((38.4, split - 0.3, "128~237: 작업기 CF"),
                        (split + 0.3, 73.6, "238~247\n윗부분")):
        d.ax.plot([a, a, b, b], [y0 - 1.0, y0 - 2.0, y0 - 2.0, y0 - 1.0],
                  color=P["accent"], lw=1.3, zorder=3)
        d.text((a + b) / 2, y0 - 5.4, label, size=8.2, color=P["accent"])


diagram("12-sa-range-map", draw, w=12, h=2.8, xmax=112, ymax=28.5)
