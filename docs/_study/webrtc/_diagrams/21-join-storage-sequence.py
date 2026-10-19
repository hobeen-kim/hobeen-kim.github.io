"""CH21 §3 JoinStorageSession / AsViewer 흐름 — storage 세션이 offer를 보내는 시퀀스 (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P

    actors = [
        (9, "디바이스\n(master)", P["green"]),
        (29, "시그널링\n(WSS 엔드포인트)", P["purple"]),
        (50, "storage 세션\n(WEBRTC 엔드포인트)", P["gray"]),
        (71, "운영자 브라우저\n(viewer)", P["blue"]),
        (91, "Video Stream", P["brown"]),
    ]
    for x, name, col in actors:
        d.box(x - 8, 75, 16, 7, col)
        d.text(x, 78.5, name, size=8.8, weight="bold")
        d.ax.plot([x, x], [2, 75], color=P["edge"], ls=(0, (4, 3)), lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-", lw=1.6, lx=None, style="-|>"):
        d.arrow(x1, y, x2, y, color=color, ls=ls, lw=lw, style=style)
        d.text(lx if lx is not None else (x1 + x2) / 2, y + 1.3, label, size=7.8, color=color)

    # 1) master 참여
    d.box(2, 45.5, 96, 28, P["chip"], ec=P["accent"], lw=1.0)
    d.text(3.5, 72, "① master 참여", size=8.3, color=P["accent"], ha="left", style="italic")
    hop(9, 29, 68.5, "ConnectAsMaster", P["accent"])
    hop(9, 50, 64.5, "JoinStorageSession(channelArn)", P["accent"], lx=36)
    hop(50, 29, 60.3, "", P["orange"])
    hop(29, 9, 60.3, "", P["orange"])
    d.text(29.5, 61.6, "SDP_OFFER (senderClientId 없음)", size=7.8, color=P["orange"])
    hop(9, 29, 56, "", P["dim"], ls="--")
    hop(29, 50, 56, "", P["dim"], ls="--")
    d.text(29.5, 57.3, "SDP_ANSWER + correlationId", size=7.8, color=P["dim"])
    hop(9, 50, 51.5, "ICE_CANDIDATE trickle (storage 쪽은 relay만)", P["violet"],
        ls="--", lw=1.3, style="<|-|>", lx=29.5)
    hop(9, 50, 47.6, "SRTP: H.264 sendonly + Opus", P["accent"], lw=2.6, lx=29.5)
    hop(50, 91, 47.6, "H.264 + AAC 저장", P["violet"], lx=80)

    # 2) viewer 참여
    d.box(2, 17, 96, 25, P["chip"], ec=P["violet"], lw=1.0)
    d.text(3.5, 40.5, "② viewer 참여 (최대 3명)", size=8.3, color=P["violet"], ha="left",
           style="italic")
    hop(71, 29, 36.5, "ConnectAsViewer(clientId)", P["accent"], lx=50)
    hop(71, 50, 32, "JoinStorageSessionAsViewer(channelArn, clientId)", P["accent"], lx=60.5)
    hop(50, 71, 28.6, "SDP_OFFER (시그널링 경유)", P["orange"])
    hop(71, 50, 25.0, "SDP_ANSWER (video recvonly)", P["dim"], ls="--")
    hop(50, 71, 21.5, "영상 + 믹싱 오디오", P["accent"], lw=2.2, lx=58)
    hop(71, 50, 19.0, "", P["violet"], ls="--", lw=1.2)
    d.text(73, 19.0, "오디오(선택, Opus)", size=7.6, color=P["violet"], ha="left")

    # 3) 세션 종료와 재참여
    d.box(2, 3, 96, 12, P["chip"], ec=P["orange"], lw=1.0)
    d.text(3.5, 13.5, "③ 세션 한도(1시간) 도달", size=8.3, color=P["orange"], ha="left",
           style="italic")
    hop(50, 9, 10, "세션 종료", P["orange"], ls="--", lx=29.5)
    hop(9, 50, 5.5, "시그널링 재연결 → JoinStorageSession 재호출", P["accent"], lx=29.5)

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.0, label="요청 / 미디어"),
        Line2D([0], [0], color=P["dim"], lw=2.0, ls="--", label="응답"),
    ], loc="lower right", anchor=(0.995, 0.035))


diagram("21-join-storage-sequence", draw, w=13, h=9.2, ymax=83)
