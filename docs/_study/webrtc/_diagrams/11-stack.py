"""CH11 §1 DataChannel 프로토콜 스택 — SCTP / DTLS / ICE / UDP (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def layer(x, y, w, h, fc, title, sub, ec=None):
        d.box(x, y, w, h, fc, ec=ec)
        d.text(x + w / 2, y + h / 2 + 1.3, title, size=10, weight="bold")
        d.text(x + w / 2, y + h / 2 - 1.6, sub, size=7.8, color=P["dim"])

    # 미디어 열
    d.text(22, 55.5, "미디어", size=10, weight="bold", color=P["dim"])
    layer(6, 45, 32, 8, P["blue"], "MediaStreamTrack", "(카메라 · 마이크)")
    layer(6, 35, 32, 8, P["green"], "RTP / RTCP", "(08장 · 09장)")
    layer(6, 25, 32, 8, P["green"], "SRTP / SRTCP", "(헤더 평문 · 페이로드 암호화)")

    # 데이터 열
    d.text(64, 55.5, "데이터", size=10, weight="bold", color=P["dim"])
    layer(46, 45, 36, 8, P["blue"], "RTCDataChannel API", "(send · onmessage · bufferedAmount)")
    layer(46, 35, 17, 8, P["purple"], "DCEP", "(PPID 50)")
    layer(65, 35, 17, 8, P["purple"], "사용자 메시지", "(PPID 51 · 53)")
    layer(46, 25, 36, 8, P["brown"], "SCTP", "(스트림 · 부분 신뢰성 · 혼잡 제어)")
    layer(46, 15, 36, 8, P["brown"], "DTLS", "(1.2 이상 · 레코드 계층 암호화)")

    # 공통
    layer(6, 5.5, 76, 7.5, P["gray"], "ICE  →  UDP", "(후보 쌍 하나 · 5-tuple 하나 · 첫 바이트 demux)", ec=P["accent"])

    # 키 도출
    d.arrow(46, 19, 30, 25, color=P["orange"], lw=1.6, rad=-0.2)
    d.text(31, 18.3, "키 도출 (exporter)", size=8, color=P["orange"])

    # 하강 화살표
    d.arrow(22, 25, 22, 13, color=P["accent"], lw=1.4)
    d.arrow(64, 15, 64, 13, color=P["accent"], lw=1.4)

    # 오른쪽 주석 칩
    d.box(86, 33, 13, 12, P["chip"])
    d.text(92.5, 39, "RFC 8831\n8832 · 8261\n8841", size=7.8, color=P["dim"])


diagram("11-stack", draw, w=12, h=6.2, ymax=58)
