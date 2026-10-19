"""README 전체 구조 — WebRTC 프로토콜 스택과 구성 요소 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    layers = [
        ("미디어 · SRTP", "RTP/RTCP, 코덱", P["green"]),
        ("DataChannel · SCTP", "제어 명령·메타데이터", P["green"]),
        ("DTLS", "핸드셰이크·키 교환", P["brown"]),
        ("ICE", "후보 수집·연결성 검사", P["purple"]),
        ("UDP", "(TCP/TLS 릴레이 폴백)", P["gray"]),
    ]

    def peer(x, title, sub):
        d.box(x, 1.5, 28, 40.5, P["blue"])
        d.text(x + 14, 39, title, size=12, weight="bold")
        d.text(x + 14, 36.2, sub, size=8, color=P["dim"])
        for i, (t, s, fc) in enumerate(layers):
            yy = 31 - i * 6.2
            d.box(x + 2, yy - 2.6, 24, 5.2, fc)
            d.text(x + 14, yy + 0.8, t, size=9.5, weight="bold")
            d.text(x + 14, yy - 1.2, s, size=7.6, color=P["dim"])

    peer(2, "브라우저 피어", "운영자 화면")
    peer(70, "디바이스 피어", "카메라 달린 농기계·로봇")

    # 시그널링 서버
    d.box(36, 41, 28, 9, P["brown"], ec=P["accent"], lw=1.8)
    d.text(50, 47.2, "시그널링 서버", size=11.5, weight="bold", color=P["accent"])
    d.text(50, 43.6, "WebSocket · SDP/ICE 교환", size=8, color=P["dim"])

    # STUN/TURN
    d.box(36, 4, 28, 12, P["purple"])
    d.text(50, 12.6, "STUN / TURN 서버", size=11.5, weight="bold")
    d.text(50, 8.6, "주소 발견 · 릴레이", size=8, color=P["dim"])

    # 시그널링 화살표
    d.arrow(30, 38, 36, 45, color=P["orange"], lw=1.8, style="<|-|>", rad=-0.1)
    d.arrow(70, 38, 64, 45, color=P["orange"], lw=1.8, style="<|-|>", rad=0.1)

    # STUN/TURN 화살표
    d.arrow(30, 12, 36, 11, color=P["violet"], lw=1.6, style="<|-|>")
    d.arrow(70, 12, 64, 11, color=P["violet"], lw=1.6, style="<|-|>")

    # 미디어 경로
    d.arrow(30, 27, 70, 27, color=P["accent"], lw=2.4, style="<|-|>")
    d.text(50, 29.4, "P2P 미디어 · 데이터", size=9.5, weight="bold", color=P["accent"])
    d.text(50, 24.6, "(암호화: DTLS-SRTP)", size=8, color=P["dim"])
    d.arrow(50, 16, 50, 22, color=P["violet"], lw=1.4, ls="--", style="-")
    d.text(58.5, 19, "직접 연결 실패 시 릴레이", size=7.8, color=P["violet"], weight="bold")

    d.legend([
        Line2D([0], [0], color=P["orange"], lw=2.5, label="시그널링 (SDP·후보)"),
        Line2D([0], [0], color=P["violet"], lw=2.5, label="STUN/TURN"),
        Line2D([0], [0], color=P["accent"], lw=2.5, label="미디어·데이터 경로"),
    ], loc="lower left", anchor=(0.36, 0.64), fontsize=7.5)


diagram("readme-overview", draw, w=14, h=7.5, ymax=51)
