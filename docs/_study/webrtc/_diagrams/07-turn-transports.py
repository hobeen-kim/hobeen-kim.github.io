"""CH07 §3 TURN 전송 방식별 방화벽 통과 — UDP/TCP 3478 차단, TLS 443 통과 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 사무실망 그룹
    d.box(2, 5, 30, 32, P["gray"], ec=P["edge"], lw=1.2)
    d.text(4, 34.5, "운영자 사무실망", size=9.5, color=P["dim"], ha="left")
    d.box(5, 10, 16, 22, P["blue"])
    d.text(13, 21, "운영자\n브라우저\n(ICE 에이전트)", size=9.5)

    # 방화벽
    d.box(36, 5, 6, 32, P["brown"])
    d.text(39, 21, "방\n화\n벽", size=10, weight="bold")
    d.text(39, 39.5, "egress: TCP 443만 허용", size=8.5, color=P["dim"])

    # 차단되는 시도
    d.arrow(21, 28, 35.5, 28, color=P["orange"])
    d.text(28.2, 29.8, "UDP 3478 — 차단", size=8.5, color=P["orange"])
    d.arrow(21, 22, 35.5, 22, color=P["orange"])
    d.text(28.2, 23.8, "TCP 3478 — 차단", size=8.5, color=P["orange"])

    # 통과하는 TLS 443
    d.arrow(21, 15, 58, 15, color=P["accent"], lw=2.2)
    d.text(28.2, 16.8, "TLS 443", size=8.5, color=P["accent"])
    d.text(50, 16.8, "turns:", size=8.5, color=P["accent"])
    d.text(50, 12.6, "HTTPS처럼 보임", size=8, color=P["dim"])

    # TURN 서버
    d.box(58, 9, 18, 14, P["purple"])
    d.text(67, 16, "TURN 서버\n(coturn)", size=10)

    # 디바이스
    d.box(84, 11, 14, 10, P["green"])
    d.text(91, 16, "농기계\n디바이스", size=9.5)

    # 릴레이 구간
    d.arrow(76, 16, 84, 16, color=P["violet"])
    d.text(80, 17.8, "UDP", size=8.5, color=P["violet"])
    d.text(80, 5.5, "relay ↔ 피어 구간은\n항상 UDP", size=8, color=P["violet"])


diagram("07-turn-transports", draw, w=12, h=4.4, ymax=42)
