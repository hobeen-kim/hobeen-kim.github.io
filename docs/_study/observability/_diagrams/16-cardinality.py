"""CH16 라벨 카디널리티 — 안전 vs 위험 설계 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 안전 (좌)
    d.box(5, 8, 42, 28, P["green"], ec=P["accent"], lw=1.8)
    d.text(26, 32.5, "안전한 라벨 설계", size=13, weight="bold", color=P["accent"])
    d.box(9, 23, 34, 6.6, P["chip"])
    d.text(26, 27.5, "app · env · namespace · level", size=10, weight="bold")
    d.text(26, 24.6, "값 개수 적음 (수십~수백)", size=8.5, color=P["dim"])
    d.arrow(26, 23, 26, 19.5, color=P["accent"])
    d.box(9, 12.5, 34, 6.6, P["chip"])
    d.text(26, 15.8, "스트림 수: 수백~수천", size=11, weight="bold", color=P["accent"])

    # 위험 (우)
    d.box(53, 8, 42, 28, P["brown"])
    d.text(74, 32.5, "위험한 라벨 설계", size=13, weight="bold", color=P["orange"])
    d.box(57, 23, 34, 6.6, P["chip"])
    d.text(74, 27.5, "request_id · user_id · trace_id", size=10, weight="bold")
    d.text(74, 24.6, "값 개수 사실상 무한대", size=8.5, color=P["dim"])
    d.arrow(74, 23, 74, 19.5, color=P["orange"])
    d.box(57, 12.5, 34, 6.6, P["chip"])
    d.text(74, 15.8, "스트림 수: 무한 증가", size=11, weight="bold", color=P["orange"])


diagram("16-cardinality", draw, w=12, h=5.2, ymax=40)
