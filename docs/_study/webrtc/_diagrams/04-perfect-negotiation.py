"""CH04 §6 Perfect Negotiation — glare 발생 시 polite/impolite 처리 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    for x, name, col in [(20, "Polite 피어", P["blue"]),
                         (80, "Impolite 피어", P["brown"])]:
        d.box(x - 11, 53, 22, 5.5, col)
        d.text(x, 55.75, name, size=10, weight="bold")
        d.ax.plot([x, x], [2, 53], color=P["edge"], ls=(0, (4, 3)),
                  lw=1.0, zorder=1)

    def note(x, y, s, h=4.6, w=32, ec=None):
        d.box(x - w / 2, y - h / 2, w, h, P["chip"], ec=ec or P["edge"], lw=1.0)
        d.text(x, y, s, size=8.5)

    note(20, 47.5, "negotiationneeded\nmakingOffer = true → offer A 전송")
    note(80, 47.5, "negotiationneeded\nmakingOffer = true → offer B 전송")

    # crossing offers (glare)
    d.arrow(20, 43.5, 80, 35.5, color=P["accent"])
    d.text(34, 43.2, "offer A", size=9, color=P["accent"])
    d.arrow(80, 43.5, 20, 35.5, color=P["orange"])
    d.text(66, 43.2, "offer B", size=9, color=P["orange"])
    d.text(50, 36.6, "glare", size=9.5, color=P["dim"], style="italic")

    note(80, 30.5, "offer A 충돌 → ignoreOffer = true\n무시하고 내 offer 유지",
         ec=P["accent"])
    note(20, 30.5, "offer B 충돌 → 양보\nsetRemoteDescription(B) (implicit rollback)",
         w=36, ec=P["orange"])
    note(20, 23.5, "setLocalDescription() → answer B", h=3.6)

    d.arrow(20, 20, 80, 14, color=P["orange"])
    d.text(50, 18.8, "answer B", size=9, color=P["orange"])

    note(80, 10.5, "setRemoteDescription(answer B)\n→ stable", h=4.6)
    note(20, 7, "stable 복귀 → 남은 변경이 있으면\nnegotiationneeded 재발생 → 다시 offer",
         h=5, w=36)


diagram("04-perfect-negotiation", draw, w=12, h=7.2, ymax=60)
