"""34장 스케일링 예: 200x200 기준 풀을 480x480 VT에 2.4배로 맞추기 (light/dark PNG)."""
from matplotlib.patches import Rectangle

from _common import diagram

K = 0.1  # 그림 1단위 = 10 px, 두 마스크를 같은 축척으로 그린다


def box_px(ox, oy, x, y, w, h):
    """마스크 좌상단(ox, oy) 기준 VT 좌표(px, y는 아래로 증가) → 그림 좌표(x, y_bottom, w, h)."""
    return ox + x * K, oy - (y + h) * K, w * K, h * K


def draw(d):
    P = d.P

    # 왼쪽: 설계 기준 Data Mask 200 x 200
    lx, ly = 4, 52
    x, y, w, h = box_px(lx, ly, 0, 0, 200, 200)
    d.box(x, y, w, h, P["gray"], ec=P["accent"])
    d.text(lx - 0.2, ly + 1.6, "(0, 0)", size=8.5, color=P["orange"], ha="left")
    d.text(x + w / 2, y - 2.2, "설계 기준 Data Mask 200 x 200", size=9.5, weight="bold")

    ox_, oy_, ow, oh = box_px(lx, ly, 10, 20, 120, 30)
    d.box(ox_, oy_, ow, oh, P["blue"])
    d.text(ox_ + ow / 2, oy_ + oh / 2, "(10, 20)  120 x 30", size=8.5)

    fx, fy, fw, fh = box_px(lx, ly, 10, 100, 24, 32)
    d.box(fx, fy, fw, fh, P["green"])
    d.text(fx + fw + 0.8, fy + fh / 2, "글자 24 x 32", size=8.5, ha="left")

    # 배율 화살표
    d.arrow(26, 44, 38, 44)
    d.text(32, 46.2, "x 2.4", size=11, weight="bold", color=P["accent"])
    d.text(32, 41.6, "480 / 200", size=8.5, color=P["dim"])

    # 오른쪽: 실제 VT Data Mask 480 x 480 (같은 축척)
    rx, ry = 42, 52
    x, y, w, h = box_px(rx, ry, 0, 0, 480, 480)
    d.box(x, y, w, h, P["gray"], ec=P["accent"])
    d.text(rx - 0.2, ry + 1.6, "(0, 0)", size=8.5, color=P["orange"], ha="left")
    d.text(x + w / 2, y + 1.6, "실제 VT Data Mask 480 x 480", size=9.5, weight="bold")

    ox_, oy_, ow, oh = box_px(rx, ry, 24, 48, 288, 72)
    d.box(ox_, oy_, ow, oh, P["blue"])
    d.text(ox_ + ow / 2, oy_ + oh / 2, "(24, 48)  288 x 72", size=9)

    # 폰트: 늘어난 영역(점선) 안에 들어가는 가장 큰 지원 폰트
    ax_, ay_, aw, ah = box_px(rx, ry, 24, 240, 57.6, 76.8)
    d.ax.add_patch(Rectangle((ax_, ay_), aw, ah, fill=False, linestyle="--",
                             linewidth=1.3, edgecolor=P["orange"], zorder=3))
    fx, fy, fw, fh = box_px(rx, ry, 24, 240, 48, 64)
    d.box(fx, fy, fw, fh, P["green"])
    d.text(ax_ + aw + 1.0, ay_ + ah - 1.4, "늘어난 영역 57.6 x 76.8", size=8.5,
           color=P["orange"], ha="left")
    d.text(ax_ + aw + 1.0, ay_ + ah - 4.0, "고른 폰트 48 x 64 (Font size 9)", size=8.5, ha="left")


diagram("34-scaling-example", draw, w=12, h=6.72, xmax=100, ymax=56)
