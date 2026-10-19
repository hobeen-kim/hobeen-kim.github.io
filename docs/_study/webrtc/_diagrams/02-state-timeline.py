"""CH02 §2 offerer 쪽 RTCPeerConnection 상태 값 변화 타임라인 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    cols = [
        "생성 직후",
        "setLocal\n(offer)",
        "setRemote(answer)\n+ 원격 후보",
        "후보 쌍\n연결 성공",
        "DTLS\n완료",
        "네트워크\n끊김",
        "close()",
    ]
    rows = [
        ("signalingState",
         ["stable", "have-local-offer", "stable", "stable", "stable", "stable", "closed"]),
        ("iceGatheringState",
         ["new", "gathering", "gathering", "gathering", "complete", "complete", "—"]),
        ("iceConnectionState",
         ["new", "new", "checking", "connected", "connected", "disconnected", "closed"]),
        ("connectionState",
         ["new", "new", "connecting", "connecting", "connected", "disconnected", "closed"]),
    ]

    tone = {
        "new": P["gray"], "stable": P["gray"],
        "have-local-offer": P["blue"], "gathering": P["brown"],
        "checking": P["brown"], "connecting": P["brown"],
        "complete": P["green"], "connected": P["green"],
        "disconnected": P["purple"], "closed": P["chip"], "—": None,
    }

    X0, CW, CH = 22, 11, 7.2
    top = 38

    for i, c in enumerate(cols):
        d.text(X0 + CW * i + CW / 2, top + 4.2, c, size=8.2, color=P["dim"])

    for r, (name, vals) in enumerate(rows):
        y = top - (r + 1) * (CH + 1.2)
        d.text(1.5, y + CH / 2, name, size=9, weight="bold", ha="left")
        for i, v in enumerate(vals):
            x = X0 + CW * i
            if tone[v] is None:
                d.text(x + CW / 2, y + CH / 2, "(변화 없음)", size=7.5,
                       color=P["dim"])
                continue
            d.box(x + 0.4, y, CW - 0.8, CH, tone[v])
            size = 7.4 if len(v) > 10 else 8.2
            d.text(x + CW / 2, y + CH / 2, v, size=size)

    # 시간 축
    d.arrow(X0, 2.2, X0 + CW * len(cols), 2.2, color=P["edge"], lw=1.2)
    d.text(X0 + CW * len(cols), 0.6, "시간", size=8, color=P["dim"], ha="right")


diagram("02-state-timeline", draw, w=12.5, h=5.4, ymax=46)
