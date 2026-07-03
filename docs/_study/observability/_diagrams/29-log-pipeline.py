"""CH29 로그 파이프라인 — loki.source → process → write (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    yc = 15
    h = 11
    nodes = [
        (1, 17, "discovery.\nkubernetes", None, P["blue"]),
        (20, 17, "loki.source.\nkubernetes", None, P["green"]),
        (39, 22, "loki.process", "stage.json → labels\n→ drop", P["brown"]),
        (63, 14, "loki.write", None, P["purple"]),
    ]
    for x, w, t, sub, col in nodes:
        d.box(x, yc - h / 2, w, h, col)
        if sub:
            d.text(x + w / 2, yc + 1.6, t, size=9.2, weight="bold")
            d.text(x + w / 2, yc - 2.3, sub, size=7.6, color=P["dim"])
        else:
            d.text(x + w / 2, yc, t, size=9.2)

    d.box(79, yc - 4.5, 15, 9, P["gray"], ec=P["accent"], lw=1.8)
    d.text(86.5, yc, "Loki", size=12, weight="bold", color=P["accent"])

    for x1, x2 in [(18, 20), (37, 39), (61, 63), (77, 79)]:
        d.arrow(x1, yc, x2, yc, color=P["accent"], lw=2.0)


diagram("29-log-pipeline", draw, w=13, h=4.2, ymax=26)
