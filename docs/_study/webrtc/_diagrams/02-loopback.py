"""CH02 §5 같은 페이지 안 두 PeerConnection loopback 시퀀스 (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P
    A, B = 30, 70

    # 페이지 그룹
    d.box(1, 1, 98, 47, P["chip"], ec=P["edge"], lw=1.0)
    d.text(3, 46.2, "같은 페이지의 JavaScript (시그널링 서버 대신 직접 전달)",
           size=8.5, color=P["dim"], ha="left", style="italic")

    for x, name, col in ((A, "pc1 (offerer)", P["blue"]),
                         (B, "pc2 (answerer)", P["green"])):
        d.box(x - 8, 38.5, 16, 5, col)
        d.text(x, 41, name, size=9.5, weight="bold")
        d.ax.plot([x, x], [3, 38.5], color=P["edge"], ls=(0, (4, 3)), lw=1.0,
                  zorder=1)

    def left(y, s):
        d.text(A - 1.5, y, s, size=8.2, ha="right")

    def right(y, s):
        d.text(B + 1.5, y, s, size=8.2, ha="left")

    left(35, "① addTrack · createDataChannel")
    left(31.5, "② createOffer → setLocalDescription")
    d.arrow(A, 28, B, 28, color=P["accent"])
    d.text(50, 29.3, "offer (SDP)", size=8.2, color=P["accent"])
    right(28, "③ setRemoteDescription")
    right(24.5, "④ createAnswer → setLocalDescription")
    d.arrow(B, 21, A, 21, color=P["accent"])
    d.text(50, 22.3, "answer (SDP)", size=8.2, color=P["accent"])
    left(21, "⑤ setRemoteDescription")

    d.arrow(A, 16.5, B, 16.5, color=P["orange"], ls="--", style="<|-|>")
    d.text(50, 17.8, "ICE 후보: onicecandidate → addIceCandidate", size=8.2,
           color=P["orange"])

    d.arrow(A, 11, B, 11, color=P["violet"], lw=2.6, style="<|-|>")
    d.text(50, 12.4, "ICE 점검 → DTLS → SRTP · SCTP", size=8.2,
           color=P["violet"])
    right(6, "⑥ ontrack → remoteVideo\n    datachannel → ping/pong")

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.2, label="SDP 전달"),
        Line2D([0], [0], color=P["orange"], lw=2.2, ls="--", label="후보 전달"),
        Line2D([0], [0], color=P["violet"], lw=2.6, label="미디어 경로"),
    ], anchor=(0.01, 0.03))


diagram("02-loopback", draw, w=12, h=6.2, ymax=49)
