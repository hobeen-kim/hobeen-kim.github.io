"""CH04 §1 Offer/Answer 흐름 — JSEP API 호출과 시그널링 상태 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    actors = [
        (14, "운영자 브라우저\n(offerer)", P["blue"]),
        (50, "시그널링 서버", P["gray"]),
        (86, "로봇·농기계\n(answerer)", P["green"]),
    ]
    for x, name, col in actors:
        d.box(x - 11, 53, 22, 6.5, col)
        d.text(x, 56.25, name, size=9.5, weight="bold")
        d.ax.plot([x, x], [2, 53], color=P["edge"], ls=(0, (4, 3)),
                  lw=1.0, zorder=1)

    def note(x, y, s, h=4.2, w=25):
        d.box(x - w / 2, y - h / 2, w, h, P["chip"], lw=1.0)
        d.text(x, y, s, size=8.5)

    def state(x, y, s):
        if x < 50:
            d.text(x + 1.2, y, s, size=8.5, color=P["accent"], style="italic", ha="left")
        else:
            d.text(x - 1.2, y, s, size=8.5, color=P["accent"], style="italic", ha="right")

    def hop(x1, x2, y, label, color, ls="-"):
        d.arrow(x1, y, x2, y, color=color, ls=ls)
        d.text((x1 + x2) / 2, y + 1.4, label, size=8.5, color=color)

    # offerer
    note(14, 48, "createOffer()\nsetLocalDescription(offer)", h=5.6)
    state(14, 44.2, "→ have-local-offer")
    hop(14, 50, 40.5, "offer SDP", P["accent"])
    hop(50, 86, 38.5, "offer 중계", P["accent"])

    # answerer
    note(86, 34, "setRemoteDescription(offer)")
    state(86, 31, "→ have-remote-offer")
    note(86, 26, "createAnswer()\nsetLocalDescription(answer)", h=5.6)
    state(86, 22, "→ stable")
    hop(86, 50, 18.5, "answer SDP", P["orange"])
    hop(50, 14, 16.5, "answer 중계", P["orange"])

    # offerer completes
    note(14, 12.5, "setRemoteDescription(answer)")
    state(14, 9.5, "→ stable")

    # trickle ICE and media
    d.arrow(14, 6, 50, 6, color=P["violet"], ls="--", style="<|-|>")
    d.arrow(50, 6, 86, 6, color=P["violet"], ls="--", style="<|-|>")
    d.text(50, 7.6, "ICE candidate (trickle, setLocalDescription 이후 계속)",
           size=8.5, color=P["violet"])
    d.ax.plot([14, 86], [2.6, 2.6], color=P["dim"], lw=3.2, zorder=3,
              solid_capstyle="round")
    d.text(68, 3.9, "DTLS-SRTP 미디어는 피어끼리 직접", size=8.5,
           color=P["dim"])


diagram("04-offer-answer-flow", draw, w=12.5, h=7.4, ymax=60)
