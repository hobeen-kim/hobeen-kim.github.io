"""54장 1절: SCD 오브젝트 계층 (basic → function → state, light/dark PNG)."""
from _common import diagram


def node(d, cx, cy, w, h, label, fc, size=9.5):
    d.box(cx - w / 2, cy - h / 2, w, h, fc)
    d.text(cx, cy, label, size=size)


def link(d, x1, y1, x2, y2):
    d.ax.plot([x1, x1, x2, x2], [y1, (y1 + y2) / 2, (y1 + y2) / 2, y2],
              color=d.P["edge"], lw=1.4, zorder=2)


def draw(d):
    P = d.P

    node(d, 50, 43, 30, 8, "basic object\nObject ID 0 · SCD당 1개", P["blue"], size=10)

    node(d, 26, 26, 30, 8, "function object\n3점 히치 (Function ID 0x05)", P["green"])
    node(d, 74, 26, 30, 8, "function object\nPTO", P["green"])
    link(d, 50, 39, 26, 30)
    link(d, 50, 39, 74, 30)
    d.text(50, 33.4, "1~255개", size=8.5, color=P["dim"])

    node(d, 14, 8, 21, 8, "state object\n하강 (State ID 1)", P["brown"], size=9)
    node(d, 38, 8, 21, 8, "state object\n상승 (State ID 2)", P["brown"], size=9)
    node(d, 62, 8, 21, 8, "state object\n꺼짐", P["brown"], size=9)
    node(d, 86, 8, 21, 8, "state object\n켜짐", P["brown"], size=9)
    link(d, 26, 22, 14, 12)
    link(d, 26, 22, 38, 12)
    link(d, 74, 22, 62, 12)
    link(d, 74, 22, 86, 12)
    d.text(50, 17.6, "기능마다 0~64개", size=8.5, color=P["dim"])


diagram("54-scd-object-tree", draw, w=12, h=5.6, xmax=100, ymax=50)
