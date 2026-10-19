"""CH19 §3 GStreamer appsink → writeFrame 팬아웃 구조 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # GStreamer 파이프라인 그룹
    d.box(1.5, 35, 97, 15, P["gray"], ec=P["edge"], lw=1.0)
    d.text(3, 48, "GStreamer 파이프라인 (gst_parse_launch)", size=8.5,
           color=P["dim"], ha="left", style="italic")

    stages = [
        (3.5, 13, "v4l2src\n(카메라)", P["chip"]),
        (20, 15, "v4l2convert\n(색공간·크기)", P["chip"]),
        (38.5, 17, "HW 인코더\n(v4l2h264enc 등)", P["green"]),
        (59, 17, "h264parse\nconfig-interval=-1", P["chip"]),
        (80, 16.5, "appsink\nemit-signals=TRUE", P["blue"]),
    ]
    for x, w, label, col in stages:
        d.box(x, 37.5, w, 8, col)
        d.text(x + w / 2, 41.5, label, size=8.5)
    for (x1, w1, *_), (x2, *_r) in zip(stages, stages[1:]):
        d.arrow(x1 + w1, 41.5, x2, 41.5, color=P["edge"], lw=1.4)

    # caps 칩
    d.text(68, 33.3, "caps: byte-stream · alignment=au · profile=baseline",
           size=8, color=P["dim"])

    # 콜백
    d.box(55, 19.5, 43, 9.5, P["purple"], ec=P["accent"], lw=1.5)
    d.text(76.5, 24.2, "on_new_sample()\npull_sample → Frame(flags·PTS) → 세션 루프",
           size=8.5)
    d.arrow(88, 37.5, 88, 29, color=P["accent"])
    d.text(89, 33.3, '"new-sample"', size=8, color=P["accent"], ha="left")

    # 세션들
    sessions = [(9, "세션 1 → 운영자 A"), (30, "세션 2 → 운영자 B"),
                (51, "세션 N → 운영자 N")]
    for x, label in sessions:
        d.box(x, 3, 19, 8.5, P["brown"])
        d.text(x + 9.5, 7.25, label + "\n(PeerConnection)", size=8.3)
    d.text(49.8, 7.25, "…", size=12, color=P["dim"])

    for x, _ in sessions:
        d.arrow(60, 19.5, x + 9.5, 11.5, color=P["orange"], lw=1.5)
    d.text(85, 13.5, "writeFrame() × N\n(패킷화 · SRTP 암호화 · 송신)",
           size=8.3, color=P["orange"])

    # TWCC 피드백 (왼쪽으로 우회)
    d.ax.plot([9, 5, 5], [7.25, 7.25, 30], color=P["violet"], lw=1.3,
              ls="--", zorder=4)
    d.arrow(5, 30, 40, 37.5, color=P["violet"], ls="--", lw=1.3)
    d.text(6.5, 23.5, "TWCC 추정 → encoder bitrate\n(인코더 1개를 N 세션이 공유)",
           size=8, color=P["violet"], ha="left")


diagram("19-gst-appsink", draw, w=12.5, h=6, ymax=51)
