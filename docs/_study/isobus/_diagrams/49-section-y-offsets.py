"""49장 1절: 7섹션 붐을 위에서 본 모습과 섹션별 Y 오프셋 (light/dark PNG)."""
from _common import diagram

WIDTH_MM = 1714
X0, SW = 8.0, 12.0
BY, BH = 19.0, 6.5


def draw(d):
    P = d.P
    # 좌표축
    ox, oy = 4.0, 33.0
    d.arrow(ox, oy, ox, oy + 8.0, color=P["dim"], lw=1.3)
    d.text(ox + 1.2, oy + 7.0, "x (주행 방향)", size=7.4, color=P["dim"], ha="left")
    d.arrow(ox, oy, ox + 9.0, oy, color=P["dim"], lw=1.3)
    d.text(ox + 9.8, oy, "y (오른쪽 +)", size=7.4, color=P["dim"], ha="left")

    # 트랙터와 연결
    d.box(44, 33.5, 12, 7.0, P["gray"])
    d.text(50, 37.0, "트랙터", size=8.2)
    d.ax.plot([50, 50], [BY + BH, 33.5], color=P["accent"], lw=1.3, ls="--", zorder=3)
    d.text(51.0, BY + BH + 3.6, "y = 0 (붐 가운데)", size=7.6, color=P["accent"], ha="left")

    # 섹션 7개
    for i in range(7):
        x = X0 + i * SW
        y_mm = (i - 3) * WIDTH_MM
        d.box(x + 0.2, BY, SW - 0.4, BH, P["blue"], lw=1.1)
        d.text(x + SW / 2, BY + BH / 2, f"Section {i + 1}\nEl {11 + i}", size=7.2)
        sign = "+" if y_mm > 0 else ""
        label = "0" if y_mm == 0 else f"{sign}{y_mm:,}"
        d.text(x + SW / 2, BY - 2.6, label, size=8.2, weight="bold",
               color=P["accent"] if y_mm == 0 else None)
    d.text(X0 - 0.6, BY - 2.6, "Y(mm)", size=7.2, color=P["dim"], ha="right")

    # 섹션 하나 폭과 붐 전체 폭
    x7 = X0 + 6 * SW
    d.arrow(x7 + 0.2, 11.0, x7 + SW - 0.2, 11.0, color=P["orange"], lw=1.2, style="<|-|>")
    d.text(x7 + SW / 2, 8.6, "1,714 mm", size=7.6, color=P["orange"])
    d.arrow(X0 + 0.2, 5.0, X0 + 7 * SW - 0.2, 5.0, color=P["dim"], lw=1.2, style="<|-|>")
    d.text(50, 2.4, "붐 전체 7 x 1,714 = 11,998 mm", size=7.6, color=P["dim"])
    d.text(X0 + 0.4, BY + BH + 1.6, "왼쪽 (-)", size=7.2, color=P["dim"], ha="left")
    d.text(X0 + 7 * SW - 0.4, BY + BH + 1.6, "오른쪽 (+)", size=7.2, color=P["dim"], ha="right")


diagram("49-section-y-offsets", draw, w=12, h=5.2, xmax=100, ymax=43)
