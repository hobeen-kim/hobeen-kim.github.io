"""CH24 §5 IVS WHIP 퍼블리시 — 글로벌 엔드포인트 307 리다이렉트, 참가자 토큰을 Bearer로 사용 (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P

    actors = [
        (11, "WHIP 클라이언트\n(OBS · GStreamer)", P["brown"]),
        (39, "global.whip.live-video.net", P["blue"]),
        (65, "리다이렉트된\nWHIP 엔드포인트", P["blue"]),
        (89, "Stage\n(운영자 구독)", P["purple"]),
    ]
    for x, name, col in actors:
        d.box(x - 10, 45, 20, 6.6, col, lw=1.5)
        d.text(x, 48.3, name, size=9.2, weight="bold")
        d.ax.plot([x, x], [5, 45], color=P["edge"], ls=(0, (4, 3)),
                  lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-", style="-|>", lw=1.8):
        d.arrow(x1, y, x2, y, color=color, ls=ls, style=style, lw=lw)
        d.ax.text((x1 + x2) / 2, y + 1.3, label, fontsize=8.3, color=color,
                  ha="center", va="center", zorder=5,
                  bbox=dict(facecolor=P["bg"], edgecolor="none", pad=1.2))

    hop(11, 39, 41, "POST SDP offer + Bearer 참가자 토큰", P["accent"])
    hop(39, 11, 37, "307 Temporary Redirect (Location)", P["dim"], ls="--")
    hop(11, 65, 32.5, "같은 헤더 · 본문으로 다시 POST", P["accent"])
    hop(65, 11, 28.5, "201 Created (SDP answer)", P["dim"], ls="--")
    hop(11, 65, 23.5, "ICE 연결 확인 · DTLS 핸드셰이크", P["orange"],
        style="<|-|>")
    hop(11, 65, 19, "SRTP: H.264 Baseline(B-frame 0) + Opus", P["orange"],
        lw=3.0)
    hop(65, 89, 14.5, "publisher로 합류", P["violet"], ls="--")
    d.ax.text(89, 9.5, "이벤트: Participant Published\n(EventBridge, best-effort)",
              fontsize=8.0, color=P["violet"], ha="center", va="center",
              zorder=5, bbox=dict(facecolor=P["bg"], edgecolor="none", pad=1.2))

    d.ax.legend(handles=[
        Line2D([0], [0], color=P["accent"], lw=2.4, label="HTTP 요청"),
        Line2D([0], [0], color=P["dim"], lw=2.4, ls="--", label="HTTP 응답"),
        Line2D([0], [0], color=P["orange"], lw=2.4, label="UDP (ICE·DTLS·SRTP)"),
        Line2D([0], [0], color=P["violet"], lw=2.4, ls="--", label="IVS 내부·이벤트"),
    ], loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=4, fontsize=8.5,
        framealpha=0.0, labelcolor=P["dim"])


diagram("24-whip-publish", draw, w=13, h=6.6, ymax=53)
