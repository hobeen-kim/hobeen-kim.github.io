"""CH28 컴포넌트 그래프(DAG) — export/reference 직접 연결 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    yc = 14
    h = 11
    nodes = [
        (1, 17, "discovery.\nkubernetes.pods", P["blue"]),
        (21, 17, "discovery.\nrelabel.filter", P["green"]),
        (41, 17, "prometheus.\nscrape.app", P["brown"]),
        (61, 17, "prometheus.\nremote_write.mimir", P["purple"]),
    ]
    for x, w, t, col in nodes:
        d.box(x, yc - h / 2, w, h, col)
        d.text(x + w / 2, yc, t, size=9)

    d.box(84, yc - 4.5, 14, 9, P["gray"], ec=P["accent"], lw=1.8)
    d.text(91, yc, "Mimir", size=12, weight="bold", color=P["accent"])

    edges = [(18, 21, "targets"), (38, 41, "output"),
             (58, 61, "forward_to"), (78, 84, "remote_write")]
    for x1, x2, lab in edges:
        d.arrow(x1, yc, x2, yc, color=P["accent"], lw=2.0)
        d.text((x1 + x2) / 2, yc + 4.2, lab, size=8,
               color=P["orange"], weight="bold")


diagram("28-component-dag", draw, w=13, h=4.2, ymax=26)
