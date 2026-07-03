"""CH03 신호 → 전담 백엔드 → Grafana 통합 (LGTM+ 스택) (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # ---- 왼쪽: 신호 ----
    d.box(3, 6, 17, 44, P["gray"])
    d.text(11.5, 47, "신호", size=11, weight="bold")
    signals = [("메트릭", 39, P["blue"]), ("로그", 29, P["green"]),
               ("트레이스", 19, P["brown"]), ("프로파일", 9, P["purple"])]
    for name, yy, c in signals:
        d.box(5, yy - 3, 13, 6, c)
        d.text(11.5, yy, name, size=10, weight="bold")

    # ---- 가운데: 백엔드 ----
    d.box(28, 6, 42, 44, P["gray"])
    d.text(49, 47, "백엔드", size=11, weight="bold")

    d.box(31, 37, 16, 6.5, P["blue"])
    d.text(39, 40.2, "Prometheus", size=9.5, weight="bold")
    d.box(52, 37, 16, 6.5, P["blue"], ec=P["accent"], lw=1.5)
    d.text(60, 40.2, "Mimir", size=9.5, weight="bold")
    d.arrow(47, 40.2, 52, 40.2, color=P["orange"])
    d.text(49.5, 44.2, "remote_write", size=7.5, color=P["orange"])

    for name, yy, c in [("Loki", 28, P["green"]),
                        ("Tempo", 19, P["brown"]),
                        ("Pyroscope", 10, P["purple"])]:
        d.box(41, yy - 3, 26, 6, c)
        d.text(54, yy, name, size=10, weight="bold")

    # 신호 → 백엔드
    d.arrow(20, 39, 31, 40.2, color=P["accent"])
    d.arrow(20, 29, 41, 28, color=P["accent"])
    d.arrow(20, 19, 41, 19, color=P["accent"])
    d.arrow(20, 9, 41, 10, color=P["accent"])

    # ---- 오른쪽: Grafana ----
    d.box(78, 18, 19, 20, P["gray"], ec=P["accent"], lw=2.0)
    d.text(87.5, 31, "Grafana", size=12, weight="bold", color=P["accent"])
    d.text(87.5, 25, "질의·시각화\n상관관계", size=9, color=P["dim"])

    for yy in (40.2, 28, 19, 10):
        d.arrow(68, yy, 78, 28, color=P["violet"], rad=0.05)


diagram("03-signals-to-backends", draw, w=13, h=6.4, ymax=52)
