"""CH10 §1 하나의 UDP 5-tuple 위 첫 바이트 demux (RFC 7983/9443) — (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 수신 소켓
    d.box(2, 18, 20, 14, P["gray"], ec=P["accent"], lw=1.8)
    d.text(12, 27.5, "UDP 소켓", size=11.5, weight="bold")
    d.text(12, 23.3, "(ICE가 고른 후보 쌍\n하나의 5-tuple)", size=8.5, color=P["dim"])

    # 첫 바이트 판정
    d.box(30, 19.5, 18, 11, P["brown"])
    d.text(39, 26.6, "첫 바이트 검사", size=10.5, weight="bold")
    d.text(39, 22.6, "(RFC 7983 / 9443)", size=8.5, color=P["dim"])
    d.arrow(22, 25, 30, 25)
    d.text(26, 26.6, "datagram", size=8, color=P["dim"])

    rows = [
        (43.5, "0 – 3", "STUN", "ICE 연결성 검사 · consent", P["purple"]),
        (34.5, "20 – 63", "DTLS", "핸드셰이크 · SCTP(DataChannel)", P["brown"]),
        (25.5, "64 – 79", "TURN ChannelData", "TURN 서버에서 온 경우만", P["gray"]),
        (16.5, "128 – 191", "RTP / RTCP", "SRTP · SRTCP로 복호화", P["green"]),
        (7.5, "그 외", "폐기", "(80–127 · 192–255는 QUIC 예약)", P["chip"]),
    ]
    for y, rng, name, sub, fc in rows:
        d.arrow(48, 25, 58, y, color=P["edge"], lw=1.3)
        d.box(58, y - 3.6, 12, 7.2, P["chip"])
        d.text(64, y, rng, size=9.5, weight="bold", color=P["accent"])
        d.box(72, y - 3.6, 26, 7.2, fc)
        d.text(85, y + 1.3, name, size=10, weight="bold")
        d.text(85, y - 1.7, sub, size=7.8, color=P["dim"])


diagram("10-demux", draw, w=12.5, h=6, ymax=49)
