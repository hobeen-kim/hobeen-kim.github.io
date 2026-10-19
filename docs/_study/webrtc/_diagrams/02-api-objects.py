"""CH02 §3 API 객체 관계 — MediaStream·Track·PeerConnection·Transceiver (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # getUserMedia → MediaStream
    d.box(2, 41, 20, 6, P["brown"])
    d.text(12, 44, "getUserMedia()", size=9.5)
    d.arrow(12, 41, 12, 37.6, color=P["dim"])

    d.box(2, 16, 20, 21, P["chip"], ec=P["edge"])
    d.text(12, 34.8, "MediaStream", size=9.5, weight="bold")
    d.box(4, 25.5, 16, 6.5, P["blue"])
    d.text(12, 28.75, "MediaStreamTrack\n(video)", size=8.5)
    d.box(4, 17.5, 16, 6.5, P["blue"])
    d.text(12, 20.75, "MediaStreamTrack\n(audio)", size=8.5)

    # RTCPeerConnection
    d.box(30, 3, 46, 44, P["gray"], ec=P["accent"], lw=1.8)
    d.text(53, 44.6, "RTCPeerConnection", size=10.5, weight="bold",
           color=P["accent"])

    for y0, label in ((29.5, "RTCRtpTransceiver  (mid 0 · video)"),
                      (16.5, "RTCRtpTransceiver  (mid 1 · audio)")):
        d.box(32, y0, 42, 11.5, P["chip"])
        d.text(34, y0 + 9.6, label, size=8.5, color=P["dim"], ha="left")
        d.box(34, y0 + 1.2, 18, 6.6, P["green"])
        d.text(43, y0 + 4.5, "RTCRtpSender\n(보낼 track)", size=8.5)
        d.box(54, y0 + 1.2, 18, 6.6, P["purple"])
        d.text(63, y0 + 4.5, "RTCRtpReceiver\n(받은 track → ontrack)", size=8.5)

    d.box(32, 10, 42, 5, P["brown"])
    d.text(53, 12.5, "RTCDataChannel  ('control')", size=9)
    d.box(32, 4.5, 42, 4.5, P["chip"])
    d.text(53, 6.75, "ICE · DTLS 전송 (BUNDLE로 하나를 공유)", size=8.5,
           color=P["dim"])

    # track → sender
    d.arrow(20, 28.75, 34, 34.2, color=P["accent"])
    d.text(26.2, 33.4, "addTrack()", size=8, color=P["accent"])
    d.arrow(20, 20.75, 34, 21.2, color=P["accent"])

    # 원격 피어
    d.box(82, 16, 16, 21, P["blue"])
    d.text(90, 26.5, "원격 피어\n(브라우저 ·\n디바이스)", size=9.5)
    d.arrow(76, 30, 82, 30, color=P["orange"], style="<|-|>")
    d.text(79, 32, "SRTP", size=8, color=P["orange"])
    d.arrow(76, 12.5, 90, 16, color=P["violet"], style="<|-|>")
    d.text(84.5, 12, "SCTP/DTLS", size=8, color=P["violet"])


diagram("02-api-objects", draw, w=12.5, h=6.2, ymax=49)
