"""CH03 §2 시그널링 메시지 시퀀스 — 디바이스·서버·뷰어 (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P
    D, S, V = 14, 50, 86

    for x, name, col in ((D, "농기계 디바이스\n(role: device)", P["blue"]),
                         (S, "시그널링 서버", P["brown"]),
                         (V, "운영자 브라우저\n(role: viewer)", P["green"])):
        d.box(x - 10, 54, 20, 7, col)
        d.text(x, 57.5, name, size=9.5, weight="bold")
        d.ax.plot([x, x], [3, 54], color=P["edge"], ls=(0, (4, 3)), lw=1.0,
                  zorder=1)

    def hop(x1, x2, y, label, color, ls="-"):
        d.arrow(x1, y, x2, y, color=color, ls=ls)
        d.text((x1 + x2) / 2, y + 1.2, label, size=7.8, color=color)

    acc, dim = P["accent"], P["dim"]

    # 디바이스 대기
    hop(D, S, 50.5, "join (room, device)", acc)
    hop(S, D, 47.5, "joined (peers: [])", dim, "--")

    # 뷰어 입장
    hop(V, S, 43.5, "join (room, viewer)", acc)
    hop(S, V, 40.5, "joined (peers: [device])", dim, "--")
    hop(S, D, 38.5, "peer-joined (viewer)", dim, "--")

    # offer / answer
    hop(V, S, 35.5, "offer (to: device)", acc)
    hop(S, D, 32.5, "offer (from: viewer)", acc)
    hop(D, S, 28.5, "answer (to: viewer)", acc)
    hop(S, V, 25.5, "answer (from: device)", acc)

    # trickle ICE
    d.arrow(D, 21, S - 0.4, 21, color=P["orange"], ls="--", style="<|-|>")
    d.arrow(S + 0.4, 21, V, 21, color=P["orange"], ls="--", style="<|-|>")
    d.text(32, 22.2, "candidate (trickle)", size=7.8, color=P["orange"])
    d.text(68, 22.2, "candidate (trickle)", size=7.8, color=P["orange"])

    # 미디어
    d.box(S - 9, 13.2, 18, 4.2, P["bg"], ec=P["bg"], lw=0)
    d.arrow(D, 15.5, V, 15.5, color=P["violet"], lw=2.6, style="<|-|>")
    d.text(S, 17.0, "미디어 · DataChannel (서버를 거치지 않음)", size=7.8,
           color=P["violet"])

    # 퇴장
    hop(V, S, 9.5, "leave / 소켓 끊김", acc)
    hop(S, D, 6.5, "peer-left (viewer)", dim, "--")
    d.text(D + 1.5, 3.6, "PeerConnection close", size=7.8, color=P["dim"],
           ha="left")

    d.legend([
        Line2D([0], [0], color=acc, lw=2.2, label="클라이언트 요청 / 중계"),
        Line2D([0], [0], color=dim, lw=2.2, ls="--", label="서버 알림"),
    ], loc="lower left", anchor=(0.6, 0.005))


diagram("03-signaling-sequence", draw, w=12, h=7.6, ymax=62)
