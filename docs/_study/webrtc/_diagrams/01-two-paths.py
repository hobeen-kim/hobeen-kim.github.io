"""CH01 §3 시그널링 경로 vs 미디어 경로 분리 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 시그널링 그룹
    d.box(22, 34, 56, 13, P["chip"], ec=P["orange"], lw=1.2)
    d.text(24, 45.2, "시그널링 경로 — 앱이 정의", size=8.5, color=P["orange"],
           ha="left", style="italic")
    d.box(36, 36, 28, 7.5, P["brown"])
    d.text(50, 39.75, "시그널링 서버\n(WebSocket · HTTPS)", size=9.5)

    # 피어
    d.box(2, 18, 22, 10, P["blue"])
    d.text(13, 23, "농기계 디바이스\n(카메라 · 네이티브 WebRTC)", size=9.5)
    d.box(76, 18, 22, 10, P["green"])
    d.text(87, 23, "운영자 브라우저\n(RTCPeerConnection)", size=9.5)

    # 시그널링 화살표 (양방향)
    d.arrow(13, 28, 36, 38.5, color=P["orange"], style="<|-|>", ls="--")
    d.arrow(87, 28, 64, 38.5, color=P["orange"], style="<|-|>", ls="--")
    d.text(17.5, 34.6, "SDP · ICE 후보", size=8, color=P["orange"])
    d.text(82.5, 34.6, "SDP · ICE 후보", size=8, color=P["orange"])

    # 미디어 그룹
    d.box(2, 2, 96, 13, P["chip"], ec=P["accent"], lw=1.2)
    d.text(4, 13.2, "미디어 경로 — IETF 표준", size=8.5, color=P["accent"],
           ha="left", style="italic")

    # 직접 미디어
    d.arrow(24, 21, 76, 21, color=P["accent"], lw=2.4, style="<|-|>")
    d.text(50, 23.2, "직접 연결: SRTP(영상·음성) + SCTP/DTLS(DataChannel), UDP",
           size=8.5, color=P["accent"])

    # TURN 경유
    d.box(40, 4, 20, 7, P["gray"])
    d.text(50, 7.5, "STUN / TURN\n(NAT 통과 · 릴레이)", size=9)
    d.arrow(13, 18, 40, 8.5, color=P["violet"], ls=":", style="<|-|>")
    d.arrow(87, 18, 60, 8.5, color=P["violet"], ls=":", style="<|-|>")
    d.text(22, 10.6, "직접 실패 시 릴레이", size=8, color=P["violet"])
    d.text(78, 10.6, "직접 실패 시 릴레이", size=8, color=P["violet"])


diagram("01-two-paths", draw, w=12, h=6, ymax=48)
