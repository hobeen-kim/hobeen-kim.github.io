"""CH04 §5 JSEP 시그널링 상태 머신 — stable/offer/pranswer와 rollback (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P

    def state(cx, cy, label, col, w=24, h=7, ec=None, lw=1.4):
        d.box(cx - w / 2, cy - h / 2, w, h, col, ec=ec, lw=lw)
        d.text(cx, cy, label, size=10, weight="bold")

    state(32, 42, "have-remote-offer", P["blue"])
    state(32, 25, "stable", P["green"], w=20, ec=P["accent"], lw=2.0)
    state(32, 8, "have-local-offer", P["blue"])
    state(78, 42, "have-local-pranswer", P["purple"])
    state(78, 8, "have-remote-pranswer", P["purple"])

    lab = 8.5
    # stable <-> have-remote-offer
    d.arrow(29, 28.5, 29, 38.5)
    d.text(28, 33.5, "setRemote(offer)", size=lab, ha="right")
    d.arrow(35, 38.5, 35, 28.5)
    d.text(36, 33.5, "setLocal(answer)", size=lab, ha="left")

    # stable <-> have-local-offer
    d.arrow(35, 21.5, 35, 11.5)
    d.text(36, 16.5, "setLocal(offer)", size=lab, ha="left")
    d.arrow(29, 11.5, 29, 21.5)
    d.text(28, 16.5, "setRemote(answer)", size=lab, ha="right")

    # pranswer branches
    d.arrow(44, 42, 66, 42, color=P["violet"])
    d.text(55, 43.6, "setLocal(pranswer)", size=lab, color=P["violet"])
    d.arrow(44, 8, 66, 8, color=P["violet"])
    d.text(55, 9.6, "setRemote(pranswer)", size=lab, color=P["violet"])

    # pranswer -> stable (elbow)
    d.ax.plot([78, 78, 58], [38.5, 27, 27], color=P["violet"], lw=1.8, zorder=4)
    d.arrow(58, 27, 42, 27, color=P["violet"])
    d.text(60, 28.4, "setLocal(answer)", size=lab, color=P["violet"])
    d.ax.plot([78, 78, 58], [11.5, 23, 23], color=P["violet"], lw=1.8, zorder=4)
    d.arrow(58, 23, 42, 23, color=P["violet"])
    d.text(60, 21.4, "setRemote(answer)", size=lab, color=P["violet"])

    # rollback (dashed, left side)
    d.arrow(20, 40, 22, 27, color=P["orange"], ls="--", rad=0.8)
    d.arrow(20, 10, 22, 23, color=P["orange"], ls="--", rad=-0.8)
    d.text(14.6, 33.5, "rollback", size=lab, color=P["orange"], ha="right")
    d.text(14.6, 16.5, "rollback", size=lab, color=P["orange"], ha="right")

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.2, label="offer/answer"),
        Line2D([0], [0], color=P["violet"], lw=2.2, label="provisional answer 경로"),
        Line2D([0], [0], color=P["orange"], lw=2.2, ls="--", label="rollback → stable"),
    ], loc="lower right", anchor=(0.995, 0.36))


diagram("04-signaling-states", draw, w=12, h=6.2, ymax=50)
