"""CH19 §2 kvsWebrtcClientMaster 흐름 — 자격증명 → 시그널링 → 오퍼 → PeerConnection → writeFrame (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P

    actors = [
        (11, "디바이스 (master)\nKVS C SDK", P["green"]),
        (40, "KVS API\n(HTTPS)", P["blue"]),
        (65, "KVS 시그널링\n(WSS)", P["purple"]),
        (90, "브라우저\n(viewer)", P["brown"]),
    ]
    for x, name, col in actors:
        d.box(x - 9, 59, 18, 6.4, col, lw=1.5)
        d.text(x, 62.2, name, size=9.5, weight="bold")
        d.ax.plot([x, x], [3, 59], color=P["edge"], ls=(0, (4, 3)),
                  lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-", style="-|>", lw=1.8):
        d.arrow(x1, y, x2, y, color=color, ls=ls, style=style, lw=lw)
        d.ax.text((x1 + x2) / 2, y + 1.3, label, fontsize=8.3, color=color,
                  ha="center", va="center", zorder=5,
                  bbox=dict(facecolor=P["bg"], edgecolor="none", pad=1.2))

    def note(x, y, w, h, label, ec):
        d.box(x, y, w, h, P["chip"], ec=ec, lw=1.0)
        d.text(x + w / 2, y + h / 2, label, size=8.2, color=ec)

    # ① 자격증명
    note(2.5, 52.5, 17, 4.6, "① 자격증명 provider\n(IoT 인증서 / 정적 키)", P["dim"])

    # ② fetch
    hop(11, 40, 49, "② Describe(→Create) · GetEndpoint · GetIceServerConfig",
        P["accent"])
    d.text(25.5, 46.2, "createSignalingClientSync → signalingClientFetchSync",
           size=7.8, color=P["dim"])

    # ③ connect
    hop(11, 65, 41.5, "③ ConnectAsMaster  (signalingClientConnectSync)",
        P["accent"])

    # ④ viewer offer
    hop(90, 65, 36, "ConnectAsViewer · SDP_OFFER", P["violet"])
    hop(65, 11, 32, "④ SDP_OFFER  (messageReceivedFn)", P["violet"])

    # ⑤ PeerConnection 생성
    note(1.5, 21.5, 26, 7.6,
         "⑤ createPeerConnection\naddTransceiver · setRemoteDescription\ncreateAnswer",
         P["accent"])

    # ⑥ answer
    hop(11, 65, 18, "⑥ SDP_ANSWER  (signalingClientSendMessageSync)",
        P["violet"])
    hop(65, 90, 18, "", P["violet"])

    # ⑦ trickle
    hop(11, 90, 13.2, "⑦ ICE_CANDIDATE 교환 (Trickle)", P["dim"], ls="--",
        style="<|-|>")

    # ⑧ media
    hop(11, 90, 7.6, "⑧ ICE·DTLS → writeFrame → SRTP (P2P 또는 TURN)",
        P["orange"], lw=3.0)

    d.ax.legend(handles=[
        Line2D([0], [0], color=P["accent"], lw=2.4, label="API 호출 (SigV4)"),
        Line2D([0], [0], color=P["violet"], lw=2.4, label="시그널링 메시지"),
        Line2D([0], [0], color=P["orange"], lw=2.4, label="미디어 (UDP)"),
    ], loc="lower center", bbox_to_anchor=(0.5, -0.005), ncol=3, fontsize=8.5,
        framealpha=0.0, labelcolor=P["dim"])


diagram("19-master-flow", draw, w=13, h=7.6, ymax=67)
