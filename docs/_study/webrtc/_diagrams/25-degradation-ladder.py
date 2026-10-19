"""CH25 §5 열화 대응 사다리 — 영상 단계와 원격 조작 권한 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    levels = [
        ("L0", "카메라 2대 · 720p30 + 360p15 (≈2.5 Mbps)"),
        ("L1", "카메라 1대 · 720p30 (≈2 Mbps)"),
        ("L2", "720p15 (≈1.2 Mbps)"),
        ("L3", "480p15 (≈600 kbps)"),
        ("L4", "360p10 (≈300 kbps)"),
        ("L5", "정지 화상 (MQTT 스냅샷, 수 초 간격)"),
        ("L6", "영상 없음 · 텔레메트리만"),
    ]
    top, step, h = 44.5, 6.2, 4.8
    for i, (lv, s) in enumerate(levels):
        y = top - i * step
        x = 20 + i * 2.2
        d.box(x, y, 40, h, P["chip"], lw=1.0)
        d.text(x + 1.4, y + h / 2, lv, size=9, weight="bold",
               color=P["accent"], ha="left")
        d.text(x + 5.5, y + h / 2, s, size=8.5, ha="left")

    # left: down fast / up slow
    d.arrow(2.5, 48.5, 2.5, 6, color=P["orange"], lw=2.0)
    d.text(3.6, 28, "손실 · RTT ·\n대역폭 악화\n→ 즉시 ↓", size=8.5,
           color=P["orange"], ha="left")
    d.arrow(14, 6, 14, 48.5, color=P["accent"], lw=1.6, ls="--")
    d.text(15.2, 6.8, "10초 이상 안정\n→ 한 단계 ↑", size=8.5,
           color=P["accent"], ha="left")

    # right: control permission bands
    def band(y0, y1, fc, label):
        d.box(77, y0, 21.5, y1 - y0, fc, lw=1.0)
        d.text(87.75, (y0 + y1) / 2, label, size=8.5)

    y_of = lambda i: top - i * step  # noqa: E731
    band(y_of(3), y_of(0) + h, P["green"], "원격 수동 조작 허용\n(DataChannel 50Hz)")
    band(y_of(4), y_of(4) + h, P["brown"], "저속 제한 조작")
    band(y_of(6), y_of(5) + h, P["purple"], "수동 조작 잠금\n(정지 명령만)")


diagram("25-degradation-ladder", draw, w=13, h=6.4, ymax=51)
