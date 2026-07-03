"""CH18 LogQL 성능 — 단계별 비용 순서 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    stages = [
        ("Stream Selector", "인덱스 조회", "매우 저렴", P["green"]),
        ("Line Filter |= !=", "바이트 비교", "저렴", P["green"]),
        ("Line Filter |~ !~", "정규식", "중간", P["gray"]),
        ("Parser", "json/logfmt\n/regexp", "비쌈", P["brown"]),
        ("Label Filter / 집계", "파싱 결과 위\n연산", "파싱 후", P["blue"]),
    ]
    n = len(stages)
    w, gap = 16.5, 2.0
    total = n * w + (n - 1) * gap
    x0 = (100 - total) / 2
    for i, (t, sub, cost, fc) in enumerate(stages):
        cx = x0 + i * (w + gap) + w / 2
        d.box(cx - w / 2, 10, w, 15, fc)
        d.text(cx, 22, t, size=9.5, weight="bold")
        d.text(cx, 18, sub, size=8, color=P["dim"])
        d.box(cx - 5.5, 11, 11, 3.4, P["chip"])
        d.text(cx, 12.7, cost, size=8.5, color=P["accent"], weight="bold")
        if i < n - 1:
            edge = cx + w / 2
            d.arrow(edge + 0.2, 17.5, edge + gap - 0.2, 17.5, color=P["orange"])


diagram("18-performance-stages", draw, w=14, h=3.4, ymax=30)
