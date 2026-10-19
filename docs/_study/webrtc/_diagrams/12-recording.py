"""CH12 §5 녹화 아키텍처 — SFU에서 평문 RTP를 포크해 세그먼트 컨테이너로 저장 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 실시간 경로
    d.box(3, 29, 15, 8, P["blue"])
    d.text(10.5, 33, "송신자\n(카메라)", size=9)
    d.box(32, 26, 16, 14, P["purple"], ec=P["accent"], lw=1.6)
    d.text(40, 33, "SFU\n(SRTP 복호 후\n평문 RTP 보유)", size=9, weight="bold")
    d.box(66, 30, 18, 6.5, P["chip"])
    d.text(75, 33.25, "운영자 뷰어", size=9)
    d.arrow(18, 33, 32, 33, color=P["accent"])
    d.text(25, 34.6, "SRTP", size=8, color=P["dim"])
    d.arrow(48, 33.25, 66, 33.25, color=P["accent"])
    d.text(57, 34.8, "SRTP", size=8, color=P["dim"])

    # 녹화기
    d.box(20, 2, 60, 17, P["gray"])
    d.text(78, 16.8, "녹화기 (GStreamer / FFmpeg)", size=9.5, weight="bold", ha="right")
    stages = [(23, "지터 버퍼\n(rtpjitterbuffer)"),
              (41, "depay · parse\n(rtph264depay)"),
              (59, "세그먼트 mux\n(splitmuxsink)")]
    for x, lbl in stages:
        d.box(x, 4, 16, 9, P["blue"])
        d.text(x + 8, 8.5, lbl, size=8.6)
    d.arrow(39, 8.5, 41, 8.5, color=P["accent"])
    d.arrow(57, 8.5, 59, 8.5, color=P["accent"])

    d.box(84, 4, 14, 9, P["brown"])
    d.text(91, 8.5, "오브젝트\n스토리지", size=8.8)
    d.arrow(75, 8.5, 84, 8.5, color=P["orange"])
    d.text(79.6, 11.6, "MP4/WebM\n세그먼트", size=7.6, color=P["orange"])

    # RTP 포크
    d.arrow(38, 26, 31, 13, color=P["accent"], lw=2.0)
    d.text(26.5, 22.5, "평문 RTP 포크\n(PlainTransport 등)", size=8, color=P["accent"])
    # 키프레임 요청
    d.arrow(45, 13, 44, 26, color=P["violet"], lw=1.3, ls="--")
    d.arrow(32, 30, 18, 30, color=P["violet"], lw=1.3, ls="--")
    d.text(25, 28.4, "PLI 전달", size=8, color=P["violet"])
    d.text(54.5, 21.5, "녹화 시작 시\nPLI(키프레임 요청)", size=8, color=P["violet"])


diagram("12-recording", draw, w=13, h=5.6, ymax=41)
