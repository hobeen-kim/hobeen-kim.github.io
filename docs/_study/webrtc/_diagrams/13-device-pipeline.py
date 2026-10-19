"""CH13 §3 디바이스 미디어 파이프라인 — 카메라 → HW 인코더 → RTP → WebRTC (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(2, 2, 82, 35, P["gray"])
    d.text(4, 34.6, "디바이스 (Jetson / Raspberry Pi)", size=10, weight="bold", ha="left")

    stages = [
        (4, 12, "카메라\n(V4L2 /dev/video0\n또는 CSI)", P["blue"]),
        (18, 11, "변환·스케일\n(nvvidconv)", P["blue"]),
        (31, 14, "HW 인코더\n(nvv4l2h264enc /\nv4l2h264enc)", P["green"]),
        (47, 10, "h264parse\n(AU 정렬·\nSPS/PPS)", P["blue"]),
        (59, 10, "RTP 패킷화\n(FU-A·\nSTAP-A)", P["blue"]),
    ]
    for x, w, lbl, fc in stages:
        d.box(x, 17, w, 12, fc)
        d.text(x + w / 2, 23, lbl, size=8.4)

    d.box(71, 15, 11.5, 16, P["purple"], ec=P["accent"], lw=1.6)
    d.text(76.75, 23, "WebRTC\n스택\n(ICE·\nDTLS-SRTP)", size=8.4, weight="bold")

    gaps = [(16, 18, "raw\nYUY2/NV12"), (29, 31, "NVMM\nNV12"),
            (45, 47, "H.264\nAnnex-B"), (57, 59, "AU"), (69, 71, "RTP")]
    for x1, x2, lbl in gaps:
        d.arrow(x1, 23, x2, 23, color=P["accent"])
        d.text((x1 + x2) / 2, 31.8, lbl, size=7.4, color=P["dim"])

    # 브라우저
    d.box(88, 18, 10, 10, P["chip"])
    d.text(93, 23, "운영자\n브라우저", size=8.6)
    d.arrow(82.5, 25, 88, 25, color=P["accent"], lw=1.8)
    d.text(85.2, 26.6, "SRTP", size=7.4, color=P["dim"])
    d.arrow(88, 21, 82.5, 21, color=P["orange"], lw=1.4, ls="--")
    d.text(85.2, 18.6, "RTCP", size=7.4, color=P["orange"])

    # 피드백 루프
    d.arrow(76.75, 15, 38, 17, color=P["orange"], lw=1.5, ls="--", rad=-0.3)
    d.text(57, 5, "PLI/FIR → 키프레임 강제 · REMB/TWCC 추정 → 비트레이트 조정",
           size=8, color=P["orange"])


diagram("13-device-pipeline", draw, w=13.5, h=5.2, ymax=39)
