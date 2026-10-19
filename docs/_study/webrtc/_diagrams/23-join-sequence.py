"""CH23 §3 온디맨드 미팅 참가 시퀀스 — 운영자 요청 → 미팅·참석자 생성 → MQTT로 디바이스 호출 → 미디어 서비스 접속 (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P

    actors = [
        (9, "운영자\n브라우저", P["blue"]),
        (26, "백엔드", P["green"]),
        (43, "Chime\n컨트롤 플레인", P["purple"]),
        (60, "AWS IoT Core\n(MQTT)", P["gray"]),
        (76.5, "농기계\n디바이스", P["brown"]),
        (92, "Chime\n미디어 서비스", P["purple"]),
    ]
    for x, name, col in actors:
        d.box(x - 7, 59, 14, 6.4, col, lw=1.5)
        d.text(x, 62.2, name, size=9.2, weight="bold")
        d.ax.plot([x, x], [5, 59], color=P["edge"], ls=(0, (4, 3)),
                  lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-", lw=1.8, lx=None):
        d.arrow(x1, y, x2, y, color=color, ls=ls, lw=lw)
        d.ax.text(lx if lx is not None else (x1 + x2) / 2, y + 1.3, label,
                  fontsize=8.3, color=color, ha="center", va="center",
                  zorder=5, bbox=dict(facecolor=P["bg"], edgecolor="none",
                                      pad=1.2))

    hop(9, 26, 55.5, "POST /machines/tractor-07/live", P["accent"])
    hop(26, 43, 51.5, "CreateMeeting(MediaRegion)", P["accent"])
    hop(43, 26, 47.5, "Meeting(MediaPlacement)", P["dim"], ls="--")
    hop(26, 43, 43.5, "CreateAttendee × 2", P["accent"])
    hop(43, 26, 39.5, "Attendee(JoinToken)", P["dim"], ls="--")
    hop(26, 60, 35.5, "MQTT publish: join 명령", P["violet"])
    hop(60, 76.5, 35.5, "구독 전달", P["violet"])
    hop(26, 9, 31.5, "Meeting + 운영자 Attendee", P["dim"], ls="--")
    hop(76.5, 92, 27.5, "join (WSS·JoinToken)", P["accent"])
    hop(76.5, 92, 23.5, "비디오 publish", P["orange"], lw=3.0)
    hop(9, 92, 19.5, "join (WSS·JoinToken) + 비디오 subscribe", P["accent"],
        lx=34)
    hop(92, 9, 15.5, "비디오 타일 (SRTP, SFU 전달)", P["orange"], lw=3.0, lx=34)
    hop(43, 26, 11.5, "이벤트: AttendeeJoined", P["violet"], ls="--")
    hop(26, 43, 7.5, "DeleteMeeting (시청 종료)", P["accent"])

    d.ax.legend(handles=[
        Line2D([0], [0], color=P["accent"], lw=2.4, label="API·시그널링 요청"),
        Line2D([0], [0], color=P["dim"], lw=2.4, ls="--", label="응답"),
        Line2D([0], [0], color=P["violet"], lw=2.4, label="MQTT·이벤트"),
        Line2D([0], [0], color=P["orange"], lw=3.0, label="미디어 (DTLS-SRTP)"),
    ], loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=4, fontsize=8.5,
        framealpha=0.0, labelcolor=P["dim"])


diagram("23-join-sequence", draw, w=14, h=8.2, ymax=66)
