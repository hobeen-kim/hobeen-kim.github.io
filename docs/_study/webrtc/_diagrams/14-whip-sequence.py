"""CH14 §2 WHIP 요청/응답 시퀀스 — POST·201·PATCH·DELETE (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P

    actors = [
        (10, "WHIP 클라이언트\n(OBS·디바이스)", P["green"]),
        (38, "WHIP 엔드포인트\n(/whip/live)", P["blue"]),
        (64, "WHIP 세션 리소스\n(/whip/session/abc)", P["purple"]),
        (89, "미디어 서버\n(SFU)", P["brown"]),
    ]

    # 선택 구간: Trickle ICE
    d.box(2, 25.2, 70, 9.6, P["chip"], ec=P["accent"], lw=1.1)
    d.text(3.2, 33.6, "선택: Trickle ICE", size=8.5, color=P["accent"],
           ha="left", style="italic")

    for x, name, col in actors:
        d.box(x - 9, 48.5, 18, 6.6, col, lw=1.5)
        d.text(x, 51.8, name, size=9.5, weight="bold")
        d.ax.plot([x, x], [5, 48.5], color=P["edge"], ls=(0, (4, 3)),
                  lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-", style="-|>", lw=1.8,
            bg=None):
        d.arrow(x1, y, x2, y, color=color, ls=ls, style=style, lw=lw)
        d.ax.text((x1 + x2) / 2, y + 1.3, label, fontsize=8.5, color=color,
                  ha="center", va="center", zorder=5,
                  bbox=dict(facecolor=bg or P["bg"], edgecolor="none",
                            pad=1.5))

    hop(10, 38, 45, "POST application/sdp (offer) + Bearer 토큰", P["accent"])
    hop(38, 89, 41.5, "세션 생성 (내부 API)", P["violet"], ls="--")
    hop(38, 10, 37.5, "201 Created (SDP answer)", P["dim"], ls="--")
    d.ax.text(24, 36, "Location · ETag · Link: ice-server", fontsize=8,
              color=P["dim"], ha="center", va="center", zorder=5,
              bbox=dict(facecolor=P["bg"], edgecolor="none", pad=1.5))

    hop(10, 64, 30.5, "PATCH trickle-ice-sdpfrag (If-Match: ETag)",
        P["accent"], bg=P["chip"])
    hop(64, 10, 27, "204 No Content", P["dim"], ls="--", bg=P["chip"])

    hop(10, 89, 21.5, "ICE 연결 확인 · DTLS 핸드셰이크", P["orange"],
        style="<|-|>")
    hop(10, 89, 17, "SRTP 미디어 (sendonly → recvonly)", P["orange"],
        lw=3.2)

    hop(10, 64, 12, "DELETE /whip/session/abc", P["accent"])
    hop(64, 10, 8, "200 OK", P["dim"], ls="--")
    hop(64, 89, 8, "세션 해제", P["violet"], ls="--")

    d.ax.legend(handles=[
        Line2D([0], [0], color=P["accent"], lw=2.4, label="HTTP 요청"),
        Line2D([0], [0], color=P["dim"], lw=2.4, ls="--", label="HTTP 응답"),
        Line2D([0], [0], color=P["orange"], lw=2.4, label="UDP (ICE·DTLS·SRTP)"),
    ], loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=3, fontsize=8.5,
        framealpha=0.0, labelcolor=P["dim"])


diagram("14-whip-sequence", draw, w=13, h=7.4, ymax=56)
