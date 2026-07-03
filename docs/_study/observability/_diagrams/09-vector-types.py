"""CH09 Instant Vector vs Range Vector — 변환 흐름 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 분기점: 메트릭 이름
    d.box(3, 24, 18, 9, P["gray"])
    d.text(12, 30, "메트릭 이름", size=11, weight="bold")
    d.text(12, 26.6, "http_requests_total", size=8.4, color=P["dim"], style="italic")

    # 위 경로: 바로 instant vector
    d.box(70, 30, 26, 9, P["green"], ec=P["accent"], lw=1.8)
    d.text(83, 36, "Instant Vector", size=11.5, weight="bold", color=P["accent"])
    d.text(83, 32.6, "시점 t 값 1개 · 그래프 가능", size=8.5)
    d.arrow(21, 30, 70, 35, color=P["accent"], rad=-0.08)
    d.text(45, 35, "이름만 쓰면 바로", size=8, color=P["accent"])

    # 아래 경로
    d.box(26, 8, 18, 8, P["blue"])
    d.text(35, 13, "Range Selector", size=10, weight="bold")
    d.text(35, 10, "[5m]", size=9, color=P["accent"], style="italic")

    d.box(50, 8, 18, 8, P["blue"])
    d.text(59, 13, "Range Vector", size=10, weight="bold")
    d.text(59, 10, "구간 내 샘플 목록", size=8, color=P["dim"])

    d.box(74, 8, 22, 8, P["green"], ec=P["accent"], lw=1.8)
    d.text(85, 13, "Instant Vector", size=10, weight="bold", color=P["accent"])
    d.text(85, 10, "변환된 결과", size=8, color=P["dim"])

    d.arrow(15, 24, 34, 16, color=P["orange"], rad=-0.1)
    d.arrow(44, 12, 50, 12, color=P["orange"])
    d.arrow(68, 12, 74, 12, color=P["accent"])
    d.text(71, 18.5, "rate() · increase()\navg_over_time()", size=8, color=P["accent"])


diagram("09-vector-types", draw, w=13, h=6, ymax=42)
