"""CH13 §2 디바이스 WebRTC 스택 선택 흐름 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    qs = [
        (40, "AWS KVS 시그널링·TURN을\n그대로 쓰는가?"),
        (30, "양방향 오디오(에코 캔슬)가\n핵심 요구인가?"),
        (20, "보드 HW 인코더가\nGStreamer 요소로 제공되는가?"),
        (10, "PoC·테스트 클라이언트인가?"),
    ]
    ans = [
        ("KVS WebRTC C SDK (19장)", P["brown"]),
        ("libwebrtc (네이티브 API)", P["purple"]),
        ("GStreamer webrtcbin\n(또는 webrtcsink)", P["green"]),
        ("aiortc (Python)", P["blue"]),
    ]
    for (y, q), (a, fc) in zip(qs, ans):
        d.box(4, y - 3.3, 32, 6.6, P["gray"], ec=P["accent"], lw=1.3)
        d.text(20, y, q, size=8.8)
        d.arrow(36, y, 52, y, color=P["accent"], lw=1.6)
        d.text(44, y + 1.2, "예", size=8.2, color=P["accent"], weight="bold")
        d.box(52, y - 3.3, 30, 6.6, fc)
        d.text(67, y, a, size=9)
    for (y1, _), (y2, _) in zip(qs, qs[1:]):
        d.arrow(20, y1 - 3.3, 20, y2 + 3.3, color=P["orange"], lw=1.5)
        d.text(21.2, (y1 + y2) / 2, "아니오", size=8, color=P["orange"], ha="left")

    d.arrow(20, 6.7, 20, 3.9, color=P["orange"], lw=1.5)
    d.text(21.2, 5.3, "아니오", size=8, color=P["orange"], ha="left")
    d.box(4, 0.6, 32, 3.3, P["blue"])
    d.text(20, 2.25, "Pion(Go) / libdatachannel(C++) + 외부 인코더", size=8.4)

    d.text(84, 20, "Go 팀이면\nPion + appsink도 대안", size=8, color=P["dim"], ha="left")


diagram("13-stack-choice", draw, w=12, h=6, ymax=45)
