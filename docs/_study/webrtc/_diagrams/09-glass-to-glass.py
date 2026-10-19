"""CH09 §4 glass-to-glass 지연 분해 — 단계별 대략 범위와 예시 합계 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    stages = [
        ("캡처", "센서 노출·ISP\n드라이버 버퍼", "15~50ms", 30, P["blue"]),
        ("인코딩", "HW 인코더\n(SW는 더 김)", "5~30ms", 15, P["blue"]),
        ("패킷화·페이싱", "FU-A 분할\n페이서 대기", "1~20ms", 5, P["blue"]),
        ("네트워크", "LTE 업링크·인터넷\n(TURN 경유 시 +)", "30~150ms", 60, P["purple"]),
        ("지터 버퍼", "도착 흔들림 흡수\nNACK 대기 포함", "20~200ms", 50, P["green"]),
        ("디코딩", "HW/SW 디코더", "5~30ms", 10, P["green"]),
        ("렌더", "합성·vsync\n디스플레이", "15~50ms", 30, P["green"]),
    ]

    # 단계 상자
    x0, w, gap = 3, 12.2, 1.6
    for i, (name, sub, rng, _, fc) in enumerate(stages):
        x = x0 + i * (w + gap)
        d.box(x, 25, w, 14, fc)
        d.text(x + w / 2, 36.2, name, size=9.6, weight="bold")
        d.text(x + w / 2, 31.6, sub, size=7.6, color=P["dim"])
        d.text(x + w / 2, 27.2, rng, size=9, weight="bold", color=P["orange"])
        if i < len(stages) - 1:
            d.arrow(x + w + 0.1, 32, x + w + gap - 0.1, 32, lw=1.2)

    # 그룹 라벨
    def group(i0, i1, label, color):
        xa = x0 + i0 * (w + gap)
        xb = x0 + i1 * (w + gap) + w
        d.ax.plot([xa, xb], [41.5, 41.5], color=color, lw=1.8)
        d.ax.plot([xa, xa], [40.6, 41.5], color=color, lw=1.8)
        d.ax.plot([xb, xb], [40.6, 41.5], color=color, lw=1.8)
        d.text((xa + xb) / 2, 43.6, label, size=9.6, weight="bold", color=color)

    group(0, 2, "디바이스", P["accent"])
    group(3, 3, "망", P["violet"])
    group(4, 6, "브라우저", P["accent"])

    # 예시 비례 막대
    total = sum(s[3] for s in stages)
    bx0, bx1 = 3, 95
    scale = (bx1 - bx0) / total
    x = bx0
    d.text(bx0, 18.4, "예시 (720p30 · LTE · HW 인코더)", size=8.6, color=P["dim"],
           ha="left")
    d.text(bx1, 18.4, f"합계 ≈ {total}ms", size=9, color=P["orange"], ha="right",
           weight="bold")
    for name, _, _, typ, fc in stages:
        ww = typ * scale
        d.box(x, 10, ww, 6, fc, lw=1.0, r=0.005)
        if ww > 4:
            d.text(x + ww / 2, 13, f"{typ}", size=8.4)
        x += ww
    # 눈금
    for ms in range(0, total + 1, 50):
        xx = bx0 + ms * scale
        d.ax.plot([xx, xx], [8.6, 10], color=P["edge"], lw=1.0)
        d.text(xx, 6.6, f"{ms}ms", size=7.8, color=P["dim"])


diagram("09-glass-to-glass", draw, w=13, h=5.6, ymax=47)
