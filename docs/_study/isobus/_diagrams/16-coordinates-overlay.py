"""CH16 §9 좌표계·상대 위치(왼쪽)와 겹침 순서·클리핑(오른쪽) (light/dark PNG)."""
from _common import diagram

# 왼쪽 패널: 1 단위 = 5 px, Data Mask 200x200 px = 40x40 단위
OX, OY = 6, 44          # Data Mask 좌상단(그림 좌표)
U = 1 / 5


def px(x, y, w, h):
    """VT 좌표(px, y는 아래로 증가) → 그림 좌표 박스(x, y_bottom, w, h)."""
    return OX + x * U, OY - (y + h) * U, w * U, h * U


def draw(d):
    P = d.P
    # Data Mask
    x, y, w, h = px(0, 0, 200, 200)
    d.box(x, y, w, h, P["gray"], ec=P["accent"])
    d.text(x + 0.5, y + 1.5, "Data Mask (200x200)", size=9, weight="bold", ha="left")
    d.text(OX - 1.3, OY + 1.6, "(0, 0)", size=8.5, color=P["orange"], ha="left")
    d.arrow(OX + 4, OY + 1.0, OX + 13, OY + 1.0, color=P["orange"], lw=1.4)
    d.text(OX + 14, OY + 1.0, "x", size=9, color=P["orange"], ha="left")
    d.arrow(OX - 1.2, OY - 1, OX - 1.2, OY - 10, color=P["orange"], lw=1.4)
    d.text(OX - 1.2, OY - 11.3, "y", size=9, color=P["orange"])

    # Container: Data Mask 안 (20, 40), 120x60
    cx, cy, cw, ch = px(20, 40, 120, 60)
    d.box(cx, cy, cw, ch, P["blue"])
    d.text(cx + 0.4, cy + 1.3, "Container (20, 40)", size=8.5, ha="left")
    # Input Number: Container 안 (10, 5), 90x30 → 절대 (30, 45)
    ix, iy, iw, ih = px(30, 45, 90, 30)
    d.box(ix, iy, iw, ih, P["green"])
    d.text(ix + iw / 2, iy + ih / 2 + 0.6, "Input Number (10, 5)", size=8.5)
    d.text(ix + iw / 2, iy + ih / 2 - 1.3, "절대 (30, 45)", size=8, color=P["dim"])

    # 같은 Container를 다른 위치에 한 번 더 포함(위치는 부모 레코드에 있다)
    rx, ry, rw, rh = px(20, 120, 120, 60)
    d.box(rx, ry, rw, rh, P["blue"], alpha=0.55)
    d.text(rx + 0.4, ry + rh - 1.3, "같은 Container (20, 120)", size=8.5, ha="left")
    d.text(rx + rw / 2, ry + rh / 2 - 1.0, "자식 위치는 부모 레코드에", size=8, color=P["dim"])

    # 오른쪽 패널: 겹침 순서와 클리핑
    bx, by, bw, bh = 56, 6, 34, 34
    d.box(bx, by, bw, bh, P["gray"], ec=P["accent"])
    d.text(bx + 0.4, by + bh + 1.6, "부모 (Container, 120x120)", size=9, weight="bold", ha="left")

    d.box(60, 18, 18, 14, P["blue"])
    d.text(64, 29.5, "목록 1번", size=8.5)
    d.box(70, 11, 16, 13, P["green"])
    d.text(78, 14, "목록 2번", size=8.5)
    d.text(78, 12.3, "(위에 그림)", size=7.5, color=P["dim"])

    # 부모 밖으로 나간 자식: 안쪽만 그리고 바깥은 잘린다
    d.box(84, 30, bx + bw - 84, 6, P["brown"])
    d.box(bx + bw, 30, 8, 6, P["bg"], ec=P["orange"], lw=1.2)
    d.text(bx + bw + 4, 33, "잘림", size=8, color=P["orange"])
    d.text(86.5, 33, "목록 3번", size=8)


diagram("16-coordinates-overlay", draw, w=13, h=6.2, xmax=100, ymax=48)
