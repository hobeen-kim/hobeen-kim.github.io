"""CH17 §3 KVS WebRTC 연결 수립 시퀀스 — 엔드포인트 조회부터 P2P/TURN 미디어까지 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    M, API, HTTPS, WSS, V = 8, 30, 50, 70, 92
    actors = [
        (M, "디바이스\n(Master)", P["green"]),
        (API, "KVS API\n(kinesisvideo)", P["gray"]),
        (HTTPS, "채널 HTTPS\n엔드포인트", P["purple"]),
        (WSS, "채널 WSS\n엔드포인트", P["purple"]),
        (V, "브라우저\n(Viewer)", P["blue"]),
    ]
    top = 76
    for x, name, col in actors:
        d.box(x - 7.5, top, 15, 7, col, lw=1.5)
        d.text(x, top + 3.5, name, size=9, weight="bold")
        d.ax.plot([x, x], [4, top], color=P["edge"], ls=(0, (4, 3)),
                  lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-", style="-|>", lw=1.6,
            above=True, size=8):
        d.arrow(x1, y, x2, y, color=color, ls=ls, style=style, lw=lw)
        d.ax.text((x1 + x2) / 2, y + (1.3 if above else -1.3), label,
                  fontsize=size, color=color, ha="center", va="center",
                  zorder=5, bbox=dict(facecolor=P["bg"], edgecolor="none",
                                      pad=1.2))

    def step(y, n):
        d.text(1.2, y, n, size=8, color=P["dim"], ha="left")

    # ── Master 준비 ──
    y = 71
    step(y, "①")
    hop(M, API, y, "GetSignalingChannelEndpoint (MASTER)", P["accent"])
    hop(API, M, y - 3.2, "WSS·HTTPS 엔드포인트", P["dim"], ls="--")
    y = 63
    step(y, "②")
    hop(M, HTTPS, y, "GetIceServerConfig", P["accent"])
    hop(HTTPS, M, y - 3.2, "TURN URI·자격증명 (TTL 300초)", P["dim"],
        ls="--")
    y = 55
    step(y, "③")
    hop(M, WSS, y, "ConnectAsMaster (SigV4 서명 URL)", P["violet"])

    # ── Viewer 준비 ──
    y = 49
    step(y, "④")
    hop(V, API, y, "GetSignalingChannelEndpoint (VIEWER)", P["accent"])
    y = 44
    hop(V, HTTPS, y, "GetIceServerConfig", P["accent"])
    y = 39
    step(y, "⑤")
    hop(V, WSS, y, "ConnectAsViewer (ClientId)", P["violet"])

    # ── SDP / ICE 중계 ──
    y = 32.5
    step(y, "⑥")
    hop(V, WSS, y, "SDP_OFFER", P["violet"])
    hop(WSS, M, y - 2.6, "SDP_OFFER (senderClientId)", P["violet"],
        above=False)
    y = 24.5
    step(y, "⑦")
    hop(M, WSS, y, "SDP_ANSWER (recipientClientId)", P["violet"])
    hop(WSS, V, y - 2.6, "SDP_ANSWER", P["violet"], above=False)
    y = 16.5
    step(y, "⑧")
    hop(M, V, y, "ICE_CANDIDATE 양방향 (Trickle, 채널 경유)", P["violet"],
        style="<|-|>", ls="--")

    # ── 미디어 ──
    y = 9
    step(y, "⑨")
    hop(M, V, y, "ICE 연결 확인 → DTLS → SRTP 미디어 (직결, 실패 시 TURN relay)",
        P["orange"], style="<|-|>", lw=3.0)

    d.ax.legend(handles=[
        Line2D([0], [0], color=P["accent"], lw=2.2, label="HTTPS API"),
        Line2D([0], [0], color=P["violet"], lw=2.2, label="WSS 시그널링"),
        Line2D([0], [0], color=P["orange"], lw=2.6, label="UDP 미디어 경로"),
    ], loc="lower center", bbox_to_anchor=(0.5, -0.005), ncol=3, fontsize=8,
        framealpha=0.0, labelcolor=P["dim"])


diagram("17-connection-sequence", draw, w=13.5, h=9.2, ymax=84)
