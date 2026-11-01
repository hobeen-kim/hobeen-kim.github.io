"""18장 1절: ISOBUS 이전(같은 프로토콜끼리만 연결)과 이후(ISOBUS 장비끼리 모두 연결) 비교 (light/dark PNG)."""
from _common import diagram, Line2D

NODE_W, NODE_H = 15, 8
ROWS = (35, 16)


def node(d, x, y, title, sub, fc):
    d.box(x - NODE_W / 2, y - NODE_H / 2, NODE_W, NODE_H, fc)
    d.text(x, y + 1.5, title, size=10.5, weight="bold")
    d.text(x, y - 1.9, sub, size=9, color=d.P["dim"])


def link(d, x1, y1, x2, y2, ok):
    P = d.P
    if ok:
        d.ax.plot([x1, x2], [y1, y2], color=P["accent"], lw=2.2, zorder=3)
    else:
        d.ax.plot([x1, x2], [y1, y2], color=P["orange"], lw=1.8, ls=(0, (4, 3)), zorder=3)


def panel(d, x0, title, tractors, implements, pairs):
    P = d.P
    d.box(x0, 7, 47, 41, P["gray"], ec=P["edge"])
    d.text(x0 + 23.5, 45, title, size=11.5, weight="bold")
    left, right = x0 + 10, x0 + 37
    for (t, s), y in zip(tractors, ROWS):
        node(d, left, y, t, s, P["blue"])
    for (t, s), y in zip(implements, ROWS):
        node(d, right, y, t, s, P["green"])
    for i, j, ok in pairs:
        link(d, left + NODE_W / 2, ROWS[i], right - NODE_W / 2, ROWS[j], ok)


def draw(d):
    P = d.P
    panel(d, 2, "ISOBUS 이전",
          [("트랙터 A", "Proto-A"), ("트랙터 B", "Proto-B")],
          [("작업기 A", "Proto-A"), ("작업기 B", "Proto-B")],
          [(0, 0, True), (1, 1, True), (0, 1, False), (1, 0, False)])
    panel(d, 51, "ISOBUS 이후",
          [("트랙터 A", "ISOBUS"), ("트랙터 B", "ISOBUS")],
          [("작업기 B", "ISOBUS"), ("작업기 C", "ISOBUS")],
          [(0, 0, True), (1, 1, True), (0, 1, True), (1, 0, True)])
    d.legend([Line2D([], [], color=P["accent"], lw=2.2, label="연결 가능"),
              Line2D([], [], color=P["orange"], lw=1.8, ls=(0, (4, 3)), label="연결 불가")],
             loc="lower center", anchor=(0.5, 0.0), fontsize=9.5)


diagram("18-isobus-before-after", draw, w=12, h=5.4, xmax=100, ymax=50)
