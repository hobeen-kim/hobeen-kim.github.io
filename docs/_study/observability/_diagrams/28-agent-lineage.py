"""CH28 Grafana 수집 에이전트의 계보 — 타임라인 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    y = 15
    d.arrow(5, y, 97, y, color=P["edge"], lw=2.0, style="-")

    events = [
        ("2020", "Prometheus\nAgent mode", "up", P["gray"], False),
        ("2021", "Grafana Agent", "down", P["blue"], False),
        ("2023", "Grafana\nAgent Flow", "up", P["brown"], False),
        ("2024", "Alloy 출시", "down", P["green"], True),
        ("2025", "Grafana\nAgent EOL", "up", P["purple"], False),
    ]
    xs = [12, 32, 52, 72, 90]
    bw, bh = 18, 7.5

    for (yr, name, side, col, hot), x in zip(events, xs):
        d.ax.plot([x], [y], "o", color=P["accent"], markersize=9, zorder=6)
        ec = P["accent"] if hot else P["edge"]
        lw = 1.9 if hot else 1.4
        if side == "up":
            by = 18.5
            d.arrow(x, y + 0.5, x, by, color=P["edge"], lw=1.3, style="-")
        else:
            by = 4.0
            d.arrow(x, y - 0.5, x, by + bh, color=P["edge"], lw=1.3, style="-")
        d.box(x - bw / 2, by, bw, bh, col, ec=ec, lw=lw)
        d.text(x, by + bh - 1.7, yr, size=12, weight="bold", color=P["orange"])
        d.text(x, by + 2.3, name, size=9.2,
               color=(P["accent"] if hot else P["text"]),
               weight=("bold" if hot else "normal"))


diagram("28-agent-lineage", draw, w=13, h=5.0, ymax=30)
