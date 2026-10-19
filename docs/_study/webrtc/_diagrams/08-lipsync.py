"""CH08 §5 립싱크 — RTCP SR의 NTP↔RTP timestamp 매핑으로 오디오·비디오 정렬 (light/dark PNG)."""
from _common import diagram


def X(t):
    return 30 + t * 420


def draw(d):
    P = d.P
    ya, yn, yv = 40, 25, 10

    lines = ((ya, "오디오 RTP timestamp\n(48kHz, 20ms=960)", P["green"]),
             (yn, "송신측 기준 시계\n(NTP 벽시계)", P["accent"]),
             (yv, "비디오 RTP timestamp\n(90kHz, 1프레임=3000)", P["blue"]))
    for y, lab, _ in lines:
        d.ax.plot([X(-0.01), X(0.16)], [y, y], color=P["edge"], lw=1.3, zorder=1)
        d.text(X(-0.01) - 1.5, y, lab, size=8.6, ha="right", weight="bold")

    # 오디오 패킷 눈금 (20ms 간격)
    for k in range(0, 8):
        t = k * 0.02
        d.box(X(t) - 0.9, ya - 1.3, 1.8, 2.6, P["green"], lw=0.9, r=0.01)
    # 비디오 프레임 눈금 (33.3ms 간격)
    for k in range(1, 5):
        t = k / 30
        d.box(X(t) - 1.3, yv - 1.6, 2.6, 3.2, P["blue"], lw=0.9, r=0.01)
    # NTP 축 눈금
    for k in range(0, 9):
        t = k * 0.02
        d.ax.plot([X(t), X(t)], [yn - 0.8, yn + 0.8], color=P["edge"], lw=1.0)

    # SR 매핑 (보라 점선)
    d.arrow(X(0), ya - 1.4, X(0), yn + 1.0, color=P["violet"], lw=1.4, ls="--")
    d.text(X(0) + 1.2, 33, "오디오 SR\nNTP T0 ↔ RTP 160000", size=8,
           color=P["violet"], ha="left")
    d.arrow(X(1 / 30), yv + 1.7, X(1 / 30), yn - 1.0, color=P["violet"], lw=1.4, ls="--")
    d.text(X(1 / 30) + 1.2, 17, "비디오 SR\nNTP T0+33ms ↔ RTP 900000", size=8,
           color=P["violet"], ha="left")

    # 특정 패킷 → 같은 NTP 시각
    t = 0.1
    d.arrow(X(t), ya - 1.4, X(t), yn + 1.0, color=P["orange"], lw=1.8)
    d.arrow(X(t), yv + 1.7, X(t), yn - 1.0, color=P["orange"], lw=1.8)
    d.text(X(t), ya + 3.6, "RTP 164800  (= T0 + 4800/48000)", size=8, color=P["orange"])
    d.text(X(t), yv - 4.4, "RTP 906000  (= T0+33ms + 6000/90000)", size=8, color=P["orange"])
    d.box(X(t) - 1.2, yn - 1.2, 2.4, 2.4, P["brown"], ec=P["orange"], lw=1.6, r=0.01)
    d.text(X(t) + 2.4, yn + 2.6, "T0+100ms → 같은 캡처 시각, 함께 재생", size=8.2,
           color=P["orange"], ha="left", weight="bold")


diagram("08-lipsync", draw, w=12.5, h=5.6, ymax=48)
