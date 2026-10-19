"""CH09 §1·§5 손실 복구 시퀀스 — NACK/RTX 성공 vs 실패 시 PLI → IDR (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P
    xs, xr = 30, 76

    for x, name, col in ((xs, "디바이스 (송신·인코더)", P["blue"]),
                         (xr, "브라우저 (수신·디코더)", P["green"])):
        d.box(x - 11, 50, 22, 5, col, lw=1.5)
        d.text(x, 52.5, name, size=9.5, weight="bold")
        d.ax.plot([x, x], [2, 50], color=P["edge"], ls=(0, (4, 3)), lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-", lw=1.8, dy=1.3):
        d.arrow(x1, y, x2, y, color=color, ls=ls, lw=lw)
        d.text((x1 + x2) / 2, y + dy, label, size=8, color=color)

    # 정상 흐름
    hop(xs, xr, 46, "P 프레임 #100", P["accent"])
    # 손실
    d.arrow(xs, 42, 55, 42, color=P["orange"])
    d.text(56.2, 42, "×", size=15, color=P["orange"], weight="bold")
    d.text(43, 43.3, "P 프레임 #101 일부 패킷 손실", size=8, color=P["orange"])

    # 케이스 A: NACK → RTX 성공
    d.box(3, 29, 95, 10.5, P["chip"], ec=P["accent"], lw=1.0, alpha=0.6)
    d.text(4.2, 38.4, "A. 재전송이 제때 도착", size=8.4, color=P["accent"],
           ha="left", style="italic")
    hop(xr, xs, 36, "NACK (RTCP RTPFB FMT=1, 빠진 seq)", P["violet"])
    hop(xs, xr, 31.5, "RTX 재전송 (원래 seq 포함)", P["accent"], ls="--")
    d.text(xr + 2, 31.5, "지터 버퍼 기한 안 → 정상 재생", size=8, color=P["dim"],
           ha="left")
    d.text(xs - 2, 34, "추가 지연 ≈ 1 RTT", size=8, color=P["dim"], ha="right")

    # 케이스 B: 재전송 실패 → PLI → IDR
    d.box(3, 3, 95, 24.5, P["chip"], ec=P["orange"], lw=1.0, alpha=0.6)
    d.text(4.2, 26.4, "B. 재전송도 실패 · 기한 초과", size=8.4, color=P["orange"],
           ha="left", style="italic")
    # 프리즈 구간
    d.box(xr - 1, 6, 2, 17.5, P["brown"], ec=P["orange"], lw=1.4, r=0.01)
    d.text(xr + 2, 21.5, "#101 디코딩 불가\n이후 P 프레임 참조 깨짐", size=8,
           color=P["orange"], ha="left")
    d.text(xr + 2, 14.2, "화면 정지 구간\n≈ 감지 + RTT\n+ IDR 인코딩·전송", size=8,
           color=P["orange"], ha="left", weight="bold")
    hop(xr, xs, 21, "PLI (RTCP PSFB FMT=1)", P["violet"])
    d.box(xs - 18, 15.5, 16, 4, P["blue"], lw=1.1)
    d.text(xs - 10, 17.5, "IDR 강제 생성", size=8.4)
    d.arrow(xs - 2, 17.5, xs, 17.5, color=P["dim"], lw=1.2)
    # IDR 버스트
    for i, y in enumerate((14, 12.5, 11, 9.5)):
        d.arrow(xs, y, xr - 1.2, y - 1.2, color=P["accent"], lw=1.3 if i else 2.0)
    d.text(53, 7.0, "IDR = P 프레임 수 배 크기 → FU-A 패킷 버스트", size=8,
           color=P["accent"])
    d.text(xr + 2, 6.5, "디코딩 재개", size=8.4, color=P["accent"], ha="left",
           weight="bold")

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.4, label="RTP 미디어"),
        Line2D([0], [0], color=P["violet"], lw=2.4, label="RTCP 피드백"),
    ], loc="lower left", anchor=(0.045, 0.075))


diagram("09-pli-recovery", draw, w=12.5, h=7.2, ymax=56)
