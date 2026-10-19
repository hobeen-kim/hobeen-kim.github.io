"""CH18 §4 백엔드가 SigV4 서명 URL을 발급하는 뷰어 접속 흐름 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    B, BE, API, WSS = 10, 38, 66, 90
    actors = [
        (B, "운영자 브라우저", P["blue"]),
        (BE, "백엔드\n(AWS 자격증명 보유)", P["green"]),
        (API, "KVS API · 채널 HTTPS", P["gray"]),
        (WSS, "채널 WSS\n엔드포인트", P["purple"]),
    ]
    top = 50
    for x, name, col in actors:
        d.box(x - 9, top, 18, 6.5, col, lw=1.5)
        d.text(x, top + 3.25, name, size=9, weight="bold")
        d.ax.plot([x, x], [4, top], color=P["edge"], ls=(0, (4, 3)),
                  lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-", lw=1.7, style="-|>"):
        d.arrow(x1, y, x2, y, color=color, ls=ls, lw=lw, style=style)
        d.ax.text((x1 + x2) / 2, y + 1.3, label, fontsize=8, color=color,
                  ha="center", va="center", zorder=5,
                  bbox=dict(facecolor=P["bg"], edgecolor="none", pad=1.2))

    hop(B, BE, 46, "POST /viewer-sessions (앱 로그인 토큰)", P["accent"])
    d.box(BE - 1, 33.5, 2, 9.5, P["chip"], ec=P["edge"], lw=1.0, r=0.005)
    d.text(BE - 2, 41.5, "권한 확인\n(운영자 ↔ 기계)", size=7.5,
           color=P["dim"], ha="right")
    hop(BE, API, 39, "GetSignalingChannelEndpoint (VIEWER)", P["accent"])
    hop(BE, API, 35, "GetIceServerConfig", P["accent"])
    hop(API, BE, 31, "WSS 엔드포인트 · TURN 자격증명", P["dim"], ls="--")
    d.text(BE + 2, 27.5, "ClientId 생성 · SigV4 서명\n(X-Amz-Expires 299초)",
           size=7.5, color=P["dim"], ha="left")
    hop(BE, B, 22, "{ signedUrl, iceServers, clientId }", P["dim"], ls="--")
    hop(B, WSS, 15, "WebSocket 연결 (서명 URL 그대로)", P["violet"])
    hop(WSS, B, 11, "101 Switching Protocols → 시그널링 시작", P["violet"],
        ls="--")
    d.text(50, 6.5, "브라우저에는 AWS 자격증명이 없다", size=8,
           color=P["orange"])

    d.ax.legend(handles=[
        Line2D([0], [0], color=P["accent"], lw=2.2, label="HTTPS 요청"),
        Line2D([0], [0], color=P["dim"], lw=2.2, ls="--", label="응답"),
        Line2D([0], [0], color=P["violet"], lw=2.2, label="WSS"),
    ], loc="lower center", bbox_to_anchor=(0.5, -0.01), ncol=3, fontsize=8,
        framealpha=0.0, labelcolor=P["dim"])


diagram("18-presign-flow", draw, w=12.5, h=6.6, ymax=58)
