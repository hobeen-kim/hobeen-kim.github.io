"""CH23 위에서 본 트랙터와 작업기의 기준점 DRP·CRP·NRP·ERP (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    cy = 26

    # tractor (front faces right)
    d.box(60, 17, 30, 18, P["blue"])
    d.text(75, 38.4, "트랙터", size=10.5, weight="bold")
    for ax_x, wl in ((65, 6.5), (85, 4.5)):
        d.ax.plot([ax_x, ax_x], [cy - 12, cy + 12], color=P["edge"], lw=2.2, zorder=3)
        for wy in (cy - 12, cy + 12):
            d.box(ax_x - wl / 2, wy - 2.2, wl, 4.4, P["gray"], lw=1.0, r=0.005)

    # hitch link and implement
    d.ax.plot([57, 60], [cy, cy], color=P["edge"], lw=2.6, zorder=3)
    d.ax.plot([40, 57], [cy, cy], color=P["edge"], lw=2.0, zorder=3)
    d.box(22, 18, 20, 16, P["green"])
    d.text(30, 31, "작업기", size=10.5, weight="bold")
    d.ax.plot([38, 38], [cy - 11, cy + 11], color=P["edge"], lw=2.2, zorder=3)
    for wy in (cy - 11, cy + 11):
        d.box(35.5, wy - 2, 5, 4, P["gray"], lw=1.0, r=0.005)
    d.box(15, 3, 4, 44, P["brown"], lw=1.1, r=0.005)
    d.text(13.5, 44, "붐", size=9.5, color=P["dim"], ha="right")

    pts = [
        (65, cy, "DRP", "뒤 차축 중심", 4.8, -5.5, "center"),
        (75, cy, "NRP", "항법 안테나", 0, 5.2, "center"),
        (57, cy, "CRP", "하부 링크 중심", -1.0, -5.5, "center"),
        (38, cy, "DRP", "앞 차축 중심", -5.0, -5.5, "center"),
        (17, cy, "ERP", "붐 중심", -3.2, 0, "right"),
    ]
    for x, y, name, desc, dx, dy, ha in pts:
        d.ax.plot([x], [y], marker="o", ms=8, color=P["accent"], zorder=6)
        d.text(x + dx, y + dy + 1.2, name, size=9.5, weight="bold", color=P["accent"], ha=ha)
        d.text(x + dx, y + dy - 1.3, desc, size=8.2, color=P["dim"], ha=ha)

    # axes
    ox, oy = 45, 9
    d.arrow(ox, oy, ox + 11, oy, color=P["orange"], lw=1.6)
    d.text(ox + 5.5, oy + 1.9, "x: 주행 방향", size=8.5, color=P["orange"])
    d.arrow(ox, oy, ox, oy - 7.5, color=P["violet"], lw=1.6)
    d.text(ox + 1.4, oy - 6.2, "y: 오른쪽", size=8.5, color=P["violet"], ha="left")
    d.text(ox + 1.4, oy - 3.2, "z: 지면 쪽(종이 안쪽)", size=8, color=P["dim"], ha="left")


diagram("23-p7-reference-points", draw, w=12, h=6, xmax=100, ymax=50)
