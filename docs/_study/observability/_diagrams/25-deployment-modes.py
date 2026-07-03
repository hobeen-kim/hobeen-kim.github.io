"""CH25 Pyroscope 배포 모드 — monolithic / microservices (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # monolithic
    d.box(4, 10, 34, 34, P["gray"], ec=P["green"], lw=1.8)
    d.text(21, 40, "monolithic 모드", size=13, weight="bold", color=P["accent"])

    d.box(9, 18, 24, 16, P["green"])
    d.text(21, 29, "단일 프로세스", size=12, weight="bold")
    d.text(21, 24, "distributor · ingester\nquerier · compactor …", size=8.5,
           color=P["dim"])
    d.text(21, 13.5, "운영 부담↓ · 전체 함께 스케일", size=8, color=P["dim"],
           style="italic")

    # 전환 화살표
    d.arrow(38, 27, 50, 27, color=P["orange"], lw=2.6)
    d.text(44, 29.5, "트래픽 증가 시", size=8.5, color=P["orange"], weight="bold")

    # microservices
    d.box(50, 10, 46, 34, P["gray"], ec=P["accent"], lw=1.8)
    d.text(73, 40, "microservices 모드", size=13, weight="bold", color=P["accent"])

    cells = [
        (60, 30, "distributor", P["blue"]),
        (86, 30, "ingester", P["brown"]),
        (60, 19, "querier", P["green"]),
        (86, 19, "compactor", P["purple"]),
    ]
    for x, y, t, c in cells:
        d.box(x - 8, y - 4, 16, 8, c)
        d.text(x, y + 1.4, t, size=10, weight="bold")
        d.text(x, y - 1.8, "N개 복제", size=8, color=P["dim"])

    d.text(73, 13.5, "컴포넌트별 독립 수평 확장 · 운영 복잡도↑", size=8,
           color=P["dim"], style="italic")


diagram("25-deployment-modes", draw, w=13, h=7, ymax=50)
