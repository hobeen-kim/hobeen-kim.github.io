"""CH30 VT 화면 영역: 정사각형 Data Mask, Soft Key designator 번호 매기기(세로·가로 배치) (light/dark PNG)."""
from _common import diagram

KEY_W, KEY_H, STEP = 5.0, 4.4, 5.0


def key(d, x, y_top, n, first=False):
    P = d.P
    d.box(x, y_top - KEY_H, KEY_W, KEY_H, P["chip"], ec=P["accent"] if first else None, lw=1.2)
    d.text(x + KEY_W / 2, y_top - KEY_H / 2, str(n), size=9.5, weight="bold" if first else "normal")


def draw(d):
    P = d.P

    d.text(3, 46.5, "세로 배치", size=11, weight="bold", ha="left")
    d.box(2, 2.5, 52, 40.5, P["gray"], lw=1.2)
    d.box(5, 9, 30, 30, P["blue"], ec=P["accent"])
    d.text(20, 24, "Data Mask 영역\n(정사각형)\n\n최소 200×200\nversion 6: 최소 480×480", size=9.5)
    for i in range(6):
        key(d, 43.5, 39 - i * STEP, i + 1, first=(i == 0))
        key(d, 37.0, 39 - i * STEP, i + 7)
    d.ax.plot([50.6, 50.6], [9.6, 39], color=P["edge"], lw=1.4, zorder=2)
    d.ax.text(52.3, 24.3, "Soft Key Mask 영역", rotation=90, fontsize=8.8, color=P["dim"],
              ha="center", va="center", zorder=5)
    d.box(5, 3.8, 43.5, 3.6, P["brown"], lw=1.0)
    d.text(26.75, 5.6, "남는 화면: VT 독자 정보(차량 데이터 등)", size=8.6)
    d.text(53, 46.5, "칸 하나 = Soft Key designator", size=9, color=P["accent"], ha="right")
    d.arrow(46, 45.2, 46, 39.4, color=P["accent"], lw=1.3)

    d.text(59, 46.5, "가로 배치", size=11, weight="bold", ha="left")
    d.box(58, 2.5, 52, 40.5, P["gray"], lw=1.2)
    d.box(70.5, 14.5, 27, 27, P["blue"], ec=P["accent"])
    d.text(84, 28, "Data Mask 영역\n(정사각형)", size=9.5)
    x0 = 67.0
    for i in range(6):
        key(d, x0 + i * (KEY_W + 0.8), 13.4, i + 1, first=(i == 0))
        key(d, x0 + i * (KEY_W + 0.8), 8.4, i + 7)

    d.text(66.0, 11.2, "1행", size=8.5, color=P["dim"], ha="right")
    d.text(66.0, 6.2, "2행", size=8.5, color=P["dim"], ha="right")


diagram("30-vt-screen-areas", draw, w=14, h=6.2, xmax=112, ymax=50)
