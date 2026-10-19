"""CH04 §2 SDP 구조 — 세션 섹션 + m-section 3개가 BUNDLE로 전송 하나를 공유 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # session section
    d.box(2, 39, 50, 8.5, P["gray"], ec=P["accent"], lw=1.6)
    d.text(4, 45.2, "세션 섹션", size=10, ha="left", color=P["accent"])
    d.text(4, 41.4, "v= · o= · s= · t= · a=group:BUNDLE 0 1 2", size=9.3, ha="left")

    sections = [
        (26.5, P["blue"], "m=audio  (mid:0)", "opus · red · G722 · PCMU …  /  sendrecv"),
        (14.5, P["purple"], "m=video  (mid:1)", "VP8 · VP9 · H264 · AV1 + rtx  /  recvonly"),
        (2.5, P["brown"], "m=application  (mid:2)", "UDP/DTLS/SCTP  webrtc-datachannel"),
    ]
    for y, col, head, body in sections:
        d.box(2, y, 50, 9, col)
        d.text(4, y + 6.2, head, size=9.8, ha="left")
        d.text(4, y + 2.6, body, size=9.3, ha="left")

    d.text(27, 37.1, "m-section마다: ice-ufrag/pwd · fingerprint · setup · rtcp-mux",
           size=8.5, color=P["dim"])

    # one shared transport
    d.box(68, 13, 26, 24, P["green"], ec=P["accent"], lw=1.6)
    d.text(81, 29, "전송 1개", size=11)
    d.text(81, 21.5, "ICE + DTLS\n(5-tuple 하나)", size=9.5)

    for y, ty in ((31, 31), (19, 25), (7, 15)):
        d.arrow(52, y, 68, ty, color=P["accent"], lw=1.5)
    d.text(60, 34.2, "BUNDLE", size=9.5, color=P["accent"])
    d.text(81, 8.5, "mid 헤더 확장 · SSRC · PT로\nm-section 구분", size=8.6,
           color=P["dim"])


diagram("04-sdp-structure", draw, w=11, h=5.6, ymax=49)
