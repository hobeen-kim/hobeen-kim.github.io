"""CH13 §4 webrtcbin 협상 시퀀스 — 시그널·액션 시그널과 시그널링 서버 왕복 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    actors = [
        (10, "webrtcbin", P["green"]),
        (36, "앱 코드 (C)", P["blue"]),
        (64, "시그널링 서버", P["brown"]),
        (90, "브라우저", P["chip"]),
    ]
    for x, name, col in actors:
        d.box(x - 8, 54, 16, 5, col)
        d.text(x, 56.5, name, size=9.5, weight="bold")
        d.ax.plot([x, x], [6, 54], color=P["edge"], ls=(0, (4, 3)), lw=1.0, zorder=1)

    W, A, S, B = 10, 36, 64, 90

    def hop(x1, x2, y, label, color, ls="-"):
        d.arrow(x1, y, x2, y, color=color, ls=ls, lw=1.5)
        d.text((x1 + x2) / 2, y + 1.2, label, size=7.8, color=color)

    sig, act, net = P["violet"], P["accent"], P["orange"]
    hop(W, A, 50.5, "on-negotiation-needed", sig)
    hop(A, W, 47, "create-offer (GstPromise)", act)
    hop(W, A, 43.5, "promise reply: offer", sig, ls="--")
    hop(A, W, 40, "set-local-description", act)
    hop(A, S, 40, "offer", net)
    hop(S, B, 40, "offer", net)
    hop(W, A, 36.5, "on-ice-candidate (반복)", sig)
    hop(A, S, 36.5, "candidate", net)
    hop(S, B, 36.5, "candidate", net)
    hop(B, S, 32, "answer", net)
    hop(S, A, 32, "answer", net)
    hop(A, W, 28.5, "set-remote-description", act)
    hop(B, S, 24.5, "candidate", net)
    hop(S, A, 24.5, "candidate", net)
    hop(A, W, 21, "add-ice-candidate", act)

    d.arrow(W, 13, B, 13, color=P["accent"], lw=2.6, style="<|-|>")
    d.text(50, 15, "ICE 연결 확인 → DTLS 핸드셰이크 → SRTP 미디어", size=8.6,
           color=P["accent"], weight="bold")

    d.legend([
        Line2D([0], [0], color=sig, lw=2.2, label="webrtcbin 시그널(콜백)"),
        Line2D([0], [0], color=act, lw=2.2, label="액션 시그널(호출)"),
        Line2D([0], [0], color=net, lw=2.2, label="시그널링 메시지"),
    ], loc="lower left", anchor=(0.005, 0.0), fontsize=7.5)


diagram("13-webrtcbin-sequence", draw, w=13, h=7.6, ymax=60)
