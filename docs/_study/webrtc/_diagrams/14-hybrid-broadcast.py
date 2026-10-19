"""CH14 §6 하이브리드 1:N 방송 — WHIP 인제스트 → SFU → WHEP 저지연 + HLS 대규모 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def label(x, y, s, color, size=8.5, ha="center", bg=None):
        d.ax.text(x, y, s, fontsize=size, color=color, ha=ha, va="center",
                  zorder=6, bbox=dict(facecolor=bg or P["bg"],
                                      edgecolor="none", pad=1.2))

    # 그룹
    d.box(1, 7, 24, 44, P["chip"], ec=P["edge"], lw=1.1)
    d.text(13, 48.5, "인제스트", size=10, weight="bold", color=P["dim"])
    d.box(62, 31.5, 37, 21.5, P["chip"], ec=P["accent"], lw=1.2)
    d.text(64, 50.8, "저지연 계층 (WebRTC · 0.5초 미만)", size=9,
           weight="bold", color=P["accent"], ha="left")
    d.box(29, 1, 70, 19, P["chip"], ec=P["orange"], lw=1.2)
    d.text(48, 17.6, "대규모 계층 (HTTP · LL-HLS 2~5초 · HLS 6~30초)",
           size=9, weight="bold", color=P["orange"], ha="left")

    # 인제스트 소스
    d.box(3, 36, 20, 8.5, P["green"])
    d.text(13, 40.25, "OBS Studio\n(WHIP 출력)", size=9.5)
    d.box(3, 23.5, 20, 8.5, P["green"])
    d.text(13, 27.75, "농기계 카메라\n(whipclientsink)", size=9.5)
    d.box(3, 11, 20, 8.5, P["gray"])
    d.text(13, 15.25, "레거시 인코더\n(RTMP)", size=9.5)

    # 미디어 서버
    d.box(33, 24, 24, 15, P["blue"], ec=P["accent"], lw=1.8)
    d.text(45, 31.5, "미디어 서버 · SFU\n(WHIP 수신 · 팬아웃)", size=10,
           weight="bold")

    # 저지연 시청자
    d.box(72, 41.5, 24, 6.8, P["purple"])
    d.text(84, 44.9, "운영자 콘솔 (WHEP)", size=9.5)
    d.box(72, 33.5, 24, 6.8, P["purple"])
    d.text(84, 36.9, "관제 화면 (WHEP)", size=9.5)

    # 대규모 경로
    d.box(33, 3.5, 24, 10.5, P["brown"])
    d.text(45, 8.75, "패키저 · 트랜스코더\n(Opus→AAC · 세그먼트)", size=9.5)
    d.box(63, 3.5, 14, 10.5, P["gray"])
    d.text(70, 8.75, "CDN\n(HTTP 캐시)", size=9.5)
    d.box(83, 3.5, 14.5, 10.5, P["gray"])
    d.text(90.25, 8.75, "다수 시청자\n(HLS 플레이어)", size=9.5)

    # 화살표: 인제스트 → 서버
    d.arrow(23, 40, 33, 35, color=P["accent"])
    label(28, 39.4, "WHIP", P["accent"])
    d.arrow(23, 27.75, 33, 30.5, color=P["accent"])
    label(28, 30.6, "WHIP", P["accent"])
    d.arrow(23, 17, 33, 26.5, color=P["dim"], ls="--")
    label(31.4, 22.2, "RTMP", P["dim"])

    # 서버 → 저지연
    d.arrow(57, 36.5, 72, 44.9, color=P["accent"])
    d.arrow(57, 33.5, 72, 36.9, color=P["accent"])
    label(66.5, 43.6, "WHEP", P["accent"], bg=P["chip"])

    # 서버 → 대규모
    d.arrow(45, 24, 45, 14, color=P["orange"])
    label(50, 21.5, "RTP 내부 전달", P["orange"], bg=P["bg"])
    d.arrow(57, 8.75, 63, 8.75, color=P["orange"])
    d.arrow(77, 8.75, 83, 8.75, color=P["orange"])
    label(80, 11.6, "HTTP", P["orange"], size=8, bg=P["chip"])
    label(60, 11.6, "세그먼트", P["orange"], size=8, bg=P["chip"])


diagram("14-hybrid-broadcast", draw, w=13, h=7.0, ymax=54)
