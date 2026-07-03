"""CH01 세 개의 기둥(고립) vs 상관관계로 연결된 관측성 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # ---- 왼쪽: 세 개의 기둥 (고립) ----
    d.box(3, 8, 38, 36, P["gray"])
    d.text(22, 40.2, "세 개의 기둥 (오해)", size=11, weight="bold")
    for i, (t, c) in enumerate([("메트릭", P["blue"]),
                                ("로그", P["green"]),
                                ("트레이스", P["brown"])]):
        yy = 32 - i * 8
        d.box(11, yy - 3, 22, 6, c)
        d.text(22, yy, t, size=11, weight="bold")
    d.text(22, 10.5, "서로 다른 도구·ID로 고립", size=8, color=P["dim"])

    d.text(45.5, 26, "vs", size=14, color=P["dim"], weight="bold")

    # ---- 오른쪽: 실제 관측성 (상호 연결) ----
    d.box(50, 8, 47, 36, P["gray"], ec=P["accent"], lw=2.0)
    d.text(73.5, 40.2, "실제 관측성", size=11, weight="bold", color=P["accent"])

    d.box(55, 30, 16, 6, P["blue"]);  d.text(63, 33, "메트릭", size=10, weight="bold")
    d.box(78, 30, 16, 6, P["brown"]); d.text(86, 33, "로그", size=10, weight="bold")
    d.box(65.5, 21, 16, 6, P["green"], ec=P["accent"], lw=1.6)
    d.text(73.5, 24, "트레이스", size=10, weight="bold")
    d.box(65.5, 12, 16, 6, P["purple"])
    d.text(73.5, 15, "프로파일", size=10, weight="bold")

    d.arrow(65.5, 24, 66, 30, color=P["accent"], style="<|-|>", rad=-0.15)
    d.text(59, 27.4, "exemplar", size=8, color=P["accent"])
    d.arrow(86, 30, 81.5, 24, color=P["accent"], style="<|-|>", rad=-0.15)
    d.text(90, 27.4, "trace ID", size=8, color=P["accent"])
    d.arrow(73.5, 21, 73.5, 18, color=P["accent"], style="<|-|>")
    d.text(78, 19.5, "span", size=8, color=P["accent"])


diagram("01-three-pillars-vs-observability", draw, w=13, h=6, ymax=46)
