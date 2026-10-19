"""CH19 §1 KVS C SDK 계층 구조 — 앱 · SDK 라이브러리 · KVS 공통 · 서드파티 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 계층 라벨 (왼쪽)
    layers = [
        (44.5, "앱"),
        (32.5, "WebRTC SDK"),
        (19.5, "KVS 공통\n(CMake가 함께 빌드)"),
        (6.5, "서드파티"),
    ]
    for y, label in layers:
        d.text(9, y, label, size=9, color=P["dim"])

    # 앱
    d.box(19, 41, 79, 7, P["green"])
    d.text(58.5, 44.5, "애플리케이션  (samples/common · p2p · webrtcstorage 또는 직접 작성한 앱)",
           size=9.5)

    # SDK 라이브러리
    d.box(19, 27, 45, 11, P["blue"], ec=P["accent"], lw=1.6)
    d.text(41.5, 34.6, "kvsWebrtcClient", size=10.5, weight="bold")
    d.text(41.5, 30.2, "PeerConnection · ICE/STUN · SDP\nDTLS/SRTP · SCTP · RTP/RTCP",
           size=8.5, color=P["dim"])

    d.box(67, 27, 31, 11, P["blue"], ec=P["accent"], lw=1.6)
    d.text(82.5, 34.6, "kvsWebrtcSignalingClient", size=10, weight="bold")
    d.text(82.5, 30.2, "시그널링 상태 머신\nWSS · API 응답 캐시", size=8.5,
           color=P["dim"])

    # 공개 API 경계
    d.text(97.5, 39.5, "Include.h 공개 API", size=8, color=P["accent"],
           ha="right", style="italic")

    # KVS 공통
    d.box(19, 14, 45, 10, P["purple"])
    d.text(41.5, 20.6, "kvsCommonLws  (producer-c)", size=10, weight="bold")
    d.text(41.5, 16.6, "자격증명 provider · SigV4 · HTTPS/WSS", size=8.5,
           color=P["dim"])

    d.box(67, 14, 31, 10, P["purple"])
    d.text(82.5, 20.6, "kvspic  (PIC)", size=10, weight="bold")
    d.text(82.5, 16.6, "스레드 · 타이머 · 로깅", size=8.5, color=P["dim"])

    # 서드파티 칩
    chips = [
        (19, 17, "OpenSSL\n또는 mbedTLS"),
        (38, 13.5, "libsrtp2"),
        (53.5, 13.5, "usrsctp"),
        (69, 15, "libwebsockets"),
        (86, 12, "jsmn"),
    ]
    for x, w, label in chips:
        d.box(x, 2.5, w, 8, P["chip"], ec=P["edge"], lw=1.0)
        d.text(x + w / 2, 6.5, label, size=8.5)

    # 의존 화살표 (대표만)
    d.arrow(41.5, 41, 41.5, 38, color=P["edge"], lw=1.2)
    d.arrow(82.5, 41, 82.5, 38, color=P["edge"], lw=1.2)
    d.arrow(78, 27, 56, 24, color=P["orange"], lw=1.2)
    d.text(80, 25.5, "자격증명·서명", size=7.5, color=P["orange"], ha="left")


diagram("19-sdk-layers", draw, w=12, h=5.4, ymax=50)
