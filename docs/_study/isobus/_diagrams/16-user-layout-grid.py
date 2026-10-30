"""CH16 §10 User-Layout Data Mask(2x6 Window Cell)와 User-Layout Soft Key Mask의 Key Group 배치 (light/dark PNG)."""
from _common import diagram

X0, Y0, S = 12, 6, 48          # 정사각형 User-Layout Data Mask
CW, CH = S / 2, S / 6          # Window Cell 한 칸


def cell_box(col, row, cols, rows):
    """col/row는 0부터, row 0이 맨 위."""
    x = X0 + col * CW
    y = Y0 + S - (row + rows) * CH
    return x, y, cols * CW, rows * CH


WINDOWS = [
    (0, 0, 2, 1, "blue", "2x1"),
    (0, 1, 1, 2, "green", "1x2"),
    (1, 1, 1, 1, "brown", "1x1"),
    (1, 2, 1, 1, "brown", "1x1"),
    (0, 3, 2, 2, "purple", "2x2"),
    (0, 5, 1, 1, "brown", "1x1"),
]


def draw(d):
    P = d.P
    d.box(X0, Y0, S, S, P["gray"], ec=P["accent"])
    d.text(X0 + S / 2, Y0 + S + 2.0, "User-Layout Data Mask (2 x 6 Window Cell)", size=9.5,
           weight="bold")
    for col, row, cols, rows, color, label in WINDOWS:
        x, y, w, h = cell_box(col, row, cols, rows)
        d.box(x + 0.4, y + 0.4, w - 0.8, h - 0.8, P[color])
        d.text(x + w / 2, y + h / 2, "Window Mask " + label, size=9)
    x, y, w, h = cell_box(1, 5, 1, 1)
    d.box(x + 0.4, y + 0.4, w - 0.8, h - 0.8, P["bg"], ec=P["edge"], lw=1.0)
    d.text(x + w / 2, y + h / 2, "빈 셀(배경색)", size=8.5, color=P["dim"])

    # 셀 크기 치수
    d.arrow(X0, Y0 - 1.6, X0 + CW, Y0 - 1.6, color=P["orange"], lw=1.2, style="<|-|>")
    d.text(X0 + CW / 2, Y0 - 3.2, "폭 = W/2 (내림)", size=8, color=P["orange"])
    d.arrow(X0 - 1.6, Y0 + S, X0 - 1.6, Y0 + S - CH, color=P["orange"], lw=1.2, style="<|-|>")
    d.text(X0 - 2.4, Y0 + S - CH / 2, "높이 =\nH/6\n(내림)", size=8, color=P["orange"], ha="right")

    # User-Layout Soft Key Mask: Key Cell 6칸, Key Group 3개
    kx, kw, kh, gap = 70, 14, 7, 0.9
    top = Y0 + S
    d.text(kx + kw / 2, top + 2.0, "User-Layout Soft Key Mask", size=9.5, weight="bold")
    groups = [(1, "Key Group\n(Key 1개)"), (2, "Key Group\n(Key 2개)"), (3, "Key Group\n(Key 3개)")]
    y = top
    for n, label in groups:
        gh = n * kh + (n - 1) * gap
        y -= gh
        d.box(kx - 0.8, y - 0.5, kw + 1.6, gh + 1.0, P["chip"], ec=P["accent"])
        for i in range(n):
            ky = y + gh - (i + 1) * kh - i * gap
            d.box(kx, ky, kw, kh, P["blue"])
            d.text(kx + kw / 2, ky + kh / 2, "Key", size=8.5)
        d.text(kx + kw + 2.4, y + gh / 2, label, size=8.5, color=P["dim"], ha="left")
        y -= gap + 1.4


diagram("16-user-layout-grid", draw, w=12.5, h=7.2, xmax=100, ymax=58)
