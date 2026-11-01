"""44장 TC·DL 네트워크 구성 세 가지: a) TC + TC 클라이언트, b) DL + DL 클라이언트, c) TC + DL + TC/DL 클라이언트 (light/dark PNG)."""
from _common import diagram


def server(d, x, y, label, color):
    d.box(x, y, 12, 6, d.P[color])
    d.text(x + 6, y + 3, label, size=10.5, weight="bold")


def client(d, x, y, label, w=12, h=6):
    d.box(x, y, w, h, d.P["blue"])
    d.text(x + w / 2, y + h / 2, label, size=8.8)


def line(d, x1, y1, x2, y2, color=None):
    d.ax.plot([x1, x2], [y1, y2], color=color or d.P["accent"], lw=1.8, zorder=3)


def panel(d, x0, title, version):
    P = d.P
    d.box(x0, 1, 31, 40, P["chip"], lw=1.1)
    d.text(x0 + 15.5, 37.6, title, size=9.8, weight="bold")
    d.text(x0 + 15.5, 34.6, version, size=8.4, color=P["dim"])


def draw(d):
    P = d.P
    panel(d, 1, "a) TC + TC 클라이언트", "버전 1부터")
    server(d, 10.5, 24, "TC", "green")
    client(d, 3, 6, "클라이언트")
    client(d, 18, 6, "클라이언트")
    line(d, 16.5, 24, 9, 12)
    line(d, 16.5, 24, 24, 12)

    panel(d, 34.5, "b) DL + DL 클라이언트", "버전 4")
    server(d, 44, 24, "DL", "purple")
    client(d, 36.5, 6, "클라이언트")
    client(d, 51.5, 6, "클라이언트")
    line(d, 50, 24, 42.5, 12, P["violet"])
    line(d, 50, 24, 57.5, 12, P["violet"])

    panel(d, 68, "c) TC + DL + TC/DL 클라이언트", "버전 4")
    server(d, 70.5, 24, "TC", "green")
    server(d, 85.5, 24, "DL", "purple")
    d.box(72, 3.5, 24, 11, P["blue"])
    d.text(84, 12, "TC/DL 클라이언트", size=8.8)
    d.box(73.2, 4.6, 10.4, 4.6, P["green"])
    d.text(78.4, 6.9, "TC용 total", size=7.8)
    d.box(84.4, 4.6, 10.4, 4.6, P["purple"])
    d.text(89.6, 6.9, "DL용 total", size=7.8)
    line(d, 76.5, 24, 79, 14.5)
    line(d, 91.5, 24, 89, 14.5, P["violet"])


diagram("44-tc-dl-configs", draw, w=12, h=4.9, xmax=100, ymax=42)
