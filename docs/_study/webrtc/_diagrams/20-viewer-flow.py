"""CH20 §1 브라우저 뷰어 연결 시퀀스 — 백엔드 세션 → 엔드포인트 → ICE → SignalingClient → ontrack (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P

    actors = [
        (9, "브라우저\n(viewer)", P["brown"]),
        (29, "앱 백엔드", P["green"]),
        (50, "KVS API\n(HTTPS)", P["blue"]),
        (71, "KVS 시그널링\n(WSS)", P["purple"]),
        (91.5, "디바이스\n(master)", P["green"]),
    ]
    for x, name, col in actors:
        d.box(x - 8, 61, 16, 6.4, col, lw=1.5)
        d.text(x, 64.2, name, size=9.5, weight="bold")
        d.ax.plot([x, x], [3, 61], color=P["edge"], ls=(0, (4, 3)),
                  lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-", style="-|>", lw=1.8):
        d.arrow(x1, y, x2, y, color=color, ls=ls, style=style, lw=lw)
        if label:
            d.ax.text((x1 + x2) / 2, y + 1.3, label, fontsize=8.2,
                      color=color, ha="center", va="center", zorder=5,
                      bbox=dict(facecolor=P["bg"], edgecolor="none", pad=1.2))

    hop(9, 29, 56.5, "① POST /viewer-session", P["accent"])
    hop(29, 9, 52, "② 채널 ARN · ClientId · 임시 자격증명", P["dim"], ls="--")

    hop(9, 50, 46.5, "③ GetSignalingChannelEndpoint (VIEWER, WSS·HTTPS)",
        P["accent"])
    hop(9, 50, 41, "④ GetIceServerConfig → TURN uris·username·password",
        P["accent"])

    hop(9, 71, 35, "⑤ open() → ConnectAsViewer (X-Amz-ClientId)",
        P["accent"])
    hop(9, 71, 29.5, "⑥ 'open' → createOffer → sendSdpOffer", P["violet"])
    hop(71, 91.5, 29.5, "", P["violet"])
    hop(91.5, 71, 24, "", P["violet"])
    hop(71, 9, 24, "⑦ 'sdpAnswer' → setRemoteDescription", P["violet"])

    hop(9, 91.5, 18.5, "⑧ 'iceCandidate' ↔ sendIceCandidate (Trickle)",
        P["dim"], ls="--", style="<|-|>")
    hop(9, 91.5, 12.5, "⑨ ICE · DTLS (P2P 또는 KVS TURN)", P["orange"],
        style="<|-|>")
    hop(91.5, 9, 7, "⑩ SRTP → ontrack → video.srcObject", P["orange"],
        lw=3.0)

    d.ax.legend(handles=[
        Line2D([0], [0], color=P["accent"], lw=2.4, label="HTTPS·WSS 요청"),
        Line2D([0], [0], color=P["violet"], lw=2.4, label="시그널링 메시지"),
        Line2D([0], [0], color=P["orange"], lw=2.4, label="미디어 경로"),
    ], loc="lower center", bbox_to_anchor=(0.5, -0.005), ncol=3, fontsize=8.5,
        framealpha=0.0, labelcolor=P["dim"])


diagram("20-viewer-flow", draw, w=13.5, h=7.6, ymax=69)
