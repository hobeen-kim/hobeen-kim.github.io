"""CH08 §4 H.264 RTP 패킷화 (RFC 6184) — Single NAL·STAP-A·FU-A (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 상단: 인코더 출력 (Access Unit 단위 NAL 시퀀스)
    d.text(3, 50.5, "인코더 출력 (Annex-B 바이트 스트림)", size=9.5,
           color=P["accent"], weight="bold", ha="left")
    d.box(3, 40, 9, 6, P["purple"])
    d.text(7.5, 43, "SPS", size=9.5, weight="bold")
    d.box(13, 40, 9, 6, P["purple"])
    d.text(17.5, 43, "PPS", size=9.5, weight="bold")
    d.box(23, 40, 44, 6, P["brown"])
    d.text(45, 43, "IDR 슬라이스 (키프레임, 수십 KB)", size=9.5, weight="bold")
    d.box(75, 40, 16, 6, P["blue"])
    d.text(83, 43, "P 슬라이스 (수 KB 이하)", size=8.6, weight="bold")
    d.text(35, 47.4, "AU 1 (키프레임)", size=8, color=P["dim"])
    d.text(83, 47.4, "AU 2", size=8, color=P["dim"])

    # 중단 좌: STAP-A
    xs = 3
    for w, lab, fc in ((7, "RTP\n헤더", P["gray"]), (6, "STAP-A\n헤더", P["chip"]),
                       (4, "크기", P["chip"]), (7, "SPS", P["purple"]),
                       (4, "크기", P["chip"]), (7, "PPS", P["purple"])):
        d.box(xs, 29, w, 6, fc, lw=1.1, r=0.01)
        d.text(xs + w / 2, 32, lab, size=7.8)
        xs += w
    d.text(3, 26.4, "STAP-A (type 24) — 작은 NAL 여러 개를 한 패킷에", size=8.8,
           color=P["orange"], weight="bold", ha="left")

    # 중단 우: Single NAL
    d.box(62, 29, 8, 6, P["gray"], lw=1.1, r=0.01)
    d.text(66, 32, "RTP 헤더\nM=1", size=7.8)
    d.box(70, 29, 21, 6, P["blue"], lw=1.1, r=0.01)
    d.text(80.5, 32, "NAL 헤더 + P 슬라이스", size=8.2)
    d.text(62, 26.4, "Single NAL (type 1~23) — NAL 하나 = 패킷 하나", size=8.8,
           color=P["orange"], weight="bold", ha="left")

    # 하단: FU-A
    d.text(3, 20, "FU-A (type 28) — 큰 NAL을 MTU(약 1,200B) 이하 조각으로", size=8.8,
           color=P["orange"], weight="bold", ha="left")
    pk = [(3, "S=1", "조각 1", "M=0"), (34, "S=0 E=0", "조각 2 …", "M=0"),
          (65, "E=1", "마지막 조각", "M=1")]
    for x, fh, frag, m in pk:
        d.box(x, 10, 7, 7, P["gray"], lw=1.1, r=0.01)
        d.text(x + 3.5, 13.5, f"RTP\n{m}", size=7.8)
        d.box(x + 7, 10, 5, 7, P["chip"], lw=1.1, r=0.01)
        d.text(x + 9.5, 13.5, "FU\n지시자", size=7.4)
        d.box(x + 12, 10, 6, 7, P["chip"], lw=1.1, r=0.01)
        d.text(x + 15, 13.5, f"FU 헤더\n{fh}", size=7.2)
        d.box(x + 18, 10, 9, 7, P["brown"], lw=1.1, r=0.01)
        d.text(x + 22.5, 13.5, frag, size=8)

    # IDR 하나 → FU-A 패킷 N개 묶음 표시
    d.ax.plot([3, 92], [8.4, 8.4], color=P["dim"], lw=1.2)
    d.ax.plot([3, 3], [8.4, 9.2], color=P["dim"], lw=1.2)
    d.ax.plot([92, 92], [8.4, 9.2], color=P["dim"], lw=1.2)
    d.text(47.5, 6.6, "같은 RTP timestamp · 마지막 패킷만 M=1", size=8, color=P["dim"])
    d.text(3, 2.4, "FU 지시자 = F · NRI · Type(28)      FU 헤더 = S(시작) · E(끝) · R · 원래 NAL Type(5=IDR)",
           size=8, color=P["dim"], ha="left")

    # 화살표 (가운데 빈 공간으로만 통과)
    d.arrow(15, 40, 23.5, 35.2, color=P["accent"])
    d.arrow(49, 40, 47.5, 17.2, color=P["accent"])
    d.arrow(83, 40, 80.5, 35.2, color=P["accent"])


diagram("08-h264-packetization", draw, w=13, h=6.8, ymax=52)
