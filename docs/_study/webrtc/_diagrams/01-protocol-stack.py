"""CH01 §3 WebRTC 프로토콜 스택 — 시그널링 스택 vs 미디어 스택 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    H = 5.4      # 계층 높이
    G = 0.8      # 계층 간격

    def y(level):
        return 3 + level * (H + G)

    # ── 시그널링 스택 (왼쪽) ──
    d.text(15, y(6) + 2.2, "시그널링 (앱 정의)", size=10, weight="bold",
           color=P["orange"])
    left = [
        (0, "IP", P["gray"]),
        (1, "TCP", P["gray"]),
        (2, "TLS", P["brown"]),
        (3, "WebSocket / HTTPS", P["brown"]),
        (4, "앱 메시지 (JSON)\nSDP · ICE 후보 · 방 입퇴장", P["chip"]),
    ]
    for lv, label, col in left:
        h = H if lv < 4 else H * 2 + G
        d.box(2, y(lv), 26, h, col)
        d.text(15, y(lv) + h / 2, label, size=9)

    # ── 미디어 스택 (오른쪽) ──
    d.text(63, y(6) + 2.2, "미디어 (IETF 표준)", size=10, weight="bold",
           color=P["accent"])
    X0, X1 = 38, 88
    SL, SR = 38, 56      # SRTP 열
    DL, DR = 64, 88      # DTLS·SCTP 열
    d.box(X0, y(0), X1 - X0, H, P["gray"])
    d.text((X0 + X1) / 2, y(0) + H / 2, "IP", size=9)
    d.box(X0, y(1), X1 - X0, H, P["gray"])
    d.text((X0 + X1) / 2, y(1) + H / 2, "UDP  (BUNDLE: 한 포트로 다중화)", size=9)
    d.box(X0, y(2), X1 - X0, H, P["blue"])
    d.text((X0 + X1) / 2, y(2) + H / 2, "ICE  (STUN · TURN)", size=9)

    # SRTP: 레벨 3~4 를 세로로 차지 (DTLS 위가 아니라 ICE 위에 바로 얹힘)
    d.box(SL, y(3), SR - SL, H * 2 + G, P["green"])
    d.text((SL + SR) / 2, y(3) + (H * 2 + G) / 2, "SRTP / SRTCP\n(RTP 미디어)", size=9)
    d.box(DL, y(3), DR - DL, H, P["purple"])
    d.text((DL + DR) / 2, y(3) + H / 2, "DTLS", size=9)
    d.box(DL, y(4), DR - DL, H, P["purple"])
    d.text((DL + DR) / 2, y(4) + H / 2, "SCTP", size=9)

    d.box(SL, y(5), SR - SL, H, P["chip"])
    d.text((SL + SR) / 2, y(5) + H / 2, "오디오 · 비디오 트랙", size=9)
    d.box(DL, y(5), DR - DL, H, P["chip"])
    d.text((DL + DR) / 2, y(5) + H / 2, "DataChannel", size=9)

    # DTLS → SRTP 키 도출
    d.arrow(DL, y(3) + H / 2, SR, y(3) + H / 2, color=P["violet"], lw=1.5)
    d.text((SR + DL) / 2, y(3) + H / 2 + 2.0, "키 도출", size=7.5, color=P["violet"])

    # 장 번호 주석
    notes = [
        (y(2) + H / 2, "05~07장"),
        (y(3) + H / 2, "10장"),
        (y(4) + H / 2, "11장"),
        (y(5) + H / 2, "08 · 11장"),
    ]
    for yy, s in notes:
        d.text(X1 + 1.5, yy, s, size=8, color=P["dim"], ha="left")


diagram("01-protocol-stack", draw, w=11, h=6.4, ymax=48)
