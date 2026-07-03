"""CH18 LogQL 파서 파이프라인 — 셀렉터 → 필터 → 파서 → 필드 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    stages = [
        (13, P["blue"], "Stream Selector", '{app="checkout"}'),
        (37, P["green"], "Line Filter", '|= "error"'),
        (61, P["gray"], "Parser", "| json"),
        (85, P["brown"], "추출된 필드", "status · path\nduration"),
    ]
    for cx, fc, t, code in stages:
        is_parser = t == "Parser"
        d.box(cx - 10.5, 9, 21, 12, fc,
              ec=(P["accent"] if is_parser else P["edge"]),
              lw=(1.8 if is_parser else 1.4))
        d.text(cx, 17.5, t, size=10.5, weight="bold")
        d.text(cx, 13, code, size=9, color=P["accent"])

    for cx in (25, 49, 73):
        d.arrow(cx - 1.5, 15, cx + 1.5, 15, color=P["orange"])


diagram("18-parser-pipeline", draw, w=13, h=3.4, ymax=28)
