"""CH09 §2 GCC 개념 — 지연 기반 + 손실 기반 추정 → min → 인코더·페이서 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 송신측 그룹
    d.box(2, 3, 59, 45, P["gray"], ec=P["accent"], lw=1.6)
    d.text(4, 50, "송신측 (디바이스 또는 브라우저)", size=10, weight="bold",
           color=P["accent"], ha="left")
    # 수신측 그룹
    d.box(77, 3, 21, 45, P["gray"], ec=P["edge"], lw=1.4)
    d.text(87.5, 50, "수신측 (브라우저)", size=10, weight="bold", color=P["text"])

    # 미디어 경로
    d.box(4, 38, 14, 8, P["blue"])
    d.text(11, 42, "인코더\n(목표 비트레이트)", size=9)
    d.box(22, 38, 14, 8, P["blue"])
    d.text(29, 42, "페이서\n(전송 간격 평탄화)", size=9)
    d.box(63, 37, 12, 9, P["chip"])
    d.text(69, 41.5, "네트워크\n(큐·손실)", size=9)
    d.box(79, 37, 17, 9, P["chip"])
    d.text(87.5, 41.5, "도착 시각 기록\n(transport-wide seq)", size=8.6)

    d.arrow(18, 42, 22, 42)
    d.arrow(36, 42, 63, 42)
    d.text(49.5, 43.6, "RTP (transport-cc 확장)", size=8, color=P["dim"])
    d.arrow(75, 41.5, 79, 41.5)

    # 지연 기반 추정기
    d.box(4, 19.5, 40, 13, P["chip"], ec=P["edge"], lw=1.2)
    d.text(6, 30.6, "지연 기반 추정기 → A", size=9, weight="bold",
           color=P["orange"], ha="left")
    chips = [(5, "도착 시간 필터\n(지연 변화 추정)"), (18, "과사용 감지\n(적응 임계값)"),
             (31, "레이트 제어\n(증가·유지·감소)")]
    for x, lab in chips:
        d.box(x, 21, 12, 7.5, P["purple"], lw=1.1)
        d.text(x + 6, 24.75, lab, size=8.2)
    d.arrow(17, 24.75, 18, 24.75, lw=1.4)
    d.arrow(30, 24.75, 31, 24.75, lw=1.4)

    # 손실 기반 추정기
    d.box(4, 5, 40, 10, P["brown"])
    d.text(24, 11.6, "손실 기반 추정기 → As", size=9, weight="bold")
    d.text(24, 7.6, "손실 <2%: ×1.05 · 2~10%: 유지 · >10%: ×(1-0.5p)",
           size=8.2, color=P["dim"])

    # min
    d.box(47, 12.5, 12, 10, P["green"], ec=P["accent"], lw=1.6)
    d.text(53, 17.5, "min(A, As)\n= 목표 비트레이트", size=8.6, weight="bold")
    d.arrow(44, 24, 47, 20)
    d.arrow(44, 10, 47, 15)

    # 목표 비트레이트 버스 → 인코더·페이서
    d.ax.plot([53, 53], [22.5, 34.5], color=P["accent"], lw=1.8)
    d.ax.plot([11, 53], [34.5, 34.5], color=P["accent"], lw=1.8)
    d.arrow(11, 34.4, 11, 37.9)
    d.arrow(29, 34.4, 29, 37.9)
    d.text(41, 35.9, "목표 비트레이트 적용", size=8, color=P["accent"])

    # 수신측 피드백
    d.box(79, 21, 17, 9, P["purple"])
    d.text(87.5, 25.5, "TWCC 피드백\n(RTCP RTPFB FMT=15)", size=8.6)
    d.box(79, 5, 17, 9, P["brown"])
    d.text(87.5, 9.5, "수신 보고(RR)\n(fraction lost)", size=8.6)
    d.arrow(87.5, 37, 87.5, 30)

    d.arrow(79, 26.5, 44.2, 26.5, color=P["orange"])
    d.text(69.5, 28, "패킷별 도착 시각", size=8, color=P["orange"])
    d.arrow(79, 9.5, 44.2, 9.5, color=P["violet"])
    d.text(69.5, 11, "손실률", size=8, color=P["violet"])


diagram("09-gcc", draw, w=13, h=6.8, ymax=52)
