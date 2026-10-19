"""CH17 §1 시그널링 채널 모델 — Master 1 · Viewer N, 시그널링 경로와 미디어 경로 분리 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # 시그널링 채널 (위)
    d.box(32, 44, 26, 8, P["chip"], ec=P["violet"], lw=1.5)
    d.text(45, 48, "시그널링 채널\n(KVS 관리형, SINGLE_MASTER)", size=9,
           weight="bold")
    # STUN/TURN (아래)
    d.box(36, 2, 18, 7, P["brown"])
    d.text(45, 5.5, "STUN / TURN\n(KVS 관리형)", size=8.5)

    # Master
    d.box(3, 19, 19, 10, P["green"])
    d.text(12.5, 24, "디바이스\nMaster (채널당 1)", size=9.5, weight="bold")

    # Viewers
    vs = [(40, "op-1042-a7f3"), (27, "op-2077-c91e"), (14, "op-1042-0d2b")]
    for y, cid in vs:
        d.box(76, y - 3.8, 21, 7.6, P["blue"])
        d.text(86.5, y + 1.2, "브라우저 Viewer", size=8.5, weight="bold")
        d.text(86.5, y - 1.7, f"ClientId {cid}", size=7.5, color=P["dim"])

    # 시그널링 경로: Master ↔ 채널, 채널 ↔ 버스 ↔ Viewer
    sig = dict(color=P["violet"], lw=1.3, ls="--")
    d.arrow(12.5, 29, 32, 47, style="<|-|>", **sig)
    d.ax.plot([58, 70], [48, 48], color=P["violet"], lw=1.3, ls="--",
              zorder=4)
    d.ax.plot([70, 70], [48, 15.5], color=P["violet"], lw=1.3, ls="--",
              zorder=4)
    for y, _ in vs:
        d.arrow(70, y + 1.5, 76, y + 1.5, style="<|-|>", **sig)

    # 미디어 직결 (뷰어 1, 2)
    d.arrow(22, 26.5, 76, 38.5, color=P["accent"], lw=2.0, style="<|-|>")
    d.arrow(22, 24.5, 76, 25.5, color=P["accent"], lw=2.0, style="<|-|>")
    # TURN 경유 (뷰어 3)
    d.arrow(15, 19, 36, 6, color=P["orange"], lw=1.7, ls=":", style="<|-")
    d.arrow(54, 6, 76, 12.5, color=P["orange"], lw=1.7, ls=":")
    d.text(25, 9, "직결 실패 시\nTURN relay", size=8, color=P["orange"])

    d.text(86.5, 6.5, "Viewer끼리는 서로\n발견·통신 불가", size=8,
           color=P["dim"])

    d.ax.legend(handles=[
        Line2D([0], [0], color=P["violet"], lw=1.6, ls="--",
               label="시그널링 (WSS, SDP·ICE 메타데이터)"),
        Line2D([0], [0], color=P["accent"], lw=2.2, label="미디어 P2P (SRTP)"),
        Line2D([0], [0], color=P["orange"], lw=2.0, ls=":",
               label="미디어 relay (TURN)"),
    ], loc="upper left", bbox_to_anchor=(0.0, 1.0), fontsize=8,
        framealpha=0.0, labelcolor=P["dim"])


diagram("17-channel-model", draw, w=13, h=6.2, ymax=54)
