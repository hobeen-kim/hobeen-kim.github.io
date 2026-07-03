"""CH11 룰 그룹 평가 — 그룹 내 순차 · 그룹 간 병렬 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # 그룹 A
    d.box(3, 28, 68, 14, P["gray"], ec=P["accent"], lw=1.8)
    d.text(9, 39, "그룹 A", size=11, weight="bold", color=P["accent"], ha="left")
    d.text(23, 39, "interval 30s · 순차 평가", size=8.5, color=P["dim"], ha="left")
    rules_a = [(14, "rule 1", ""), (35, "rule 2", "rule 1 결과 참조"), (56, "rule 3", "")]
    for xc, t, sub in rules_a:
        d.box(xc - 8, 30, 16, 6.5, P["green"])
        d.text(xc, 34 if sub else 33.2, t, size=9.5, weight="bold")
        if sub:
            d.text(xc, 31.2, sub, size=7, color=P["dim"])
    d.arrow(22, 33.2, 27, 33.2, color=P["orange"])
    d.arrow(43, 33.2, 48, 33.2, color=P["orange"])

    # 그룹 B
    d.box(3, 9, 48, 14, P["gray"], ec=P["accent"], lw=1.8)
    d.text(9, 20, "그룹 B", size=11, weight="bold", color=P["accent"], ha="left")
    d.text(23, 20, "interval 1m · 순차 평가", size=8.5, color=P["dim"], ha="left")
    for xc, t in [(16, "rule 4"), (37, "rule 5")]:
        d.box(xc - 8, 11, 16, 6.5, P["blue"])
        d.text(xc, 14.2, t, size=9.5, weight="bold")
    d.arrow(24, 14.2, 29, 14.2, color=P["orange"])

    # 독립성 노트
    d.box(58, 9, 38, 14, P["brown"])
    d.text(77, 19, "두 그룹은 독립 · 병렬 평가", size=10, weight="bold", color=P["accent"])
    d.text(77, 14.5, "B가 A 결과에 의존하면\n같은 그룹에 A를 앞에 둔다", size=8.2)

    d.arrow(37, 28, 55, 23, color=P["dim"], ls="--", style="-")

    d.legend([
        Line2D([0], [0], color=P["orange"], lw=2.5, label="그룹 내 순차 평가"),
        Line2D([0], [0], color=P["dim"], lw=2.5, ls="--", label="그룹 간 독립 · 병렬"),
    ])


diagram("11-rule-groups", draw, w=13, h=6.4, ymax=46)
