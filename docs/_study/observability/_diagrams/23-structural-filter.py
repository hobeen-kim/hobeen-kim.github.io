"""CH23 구조 필터 — descendant vs child 연산자 예시 트리 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    def node(cx, cy, title, meta, ec=None, lw=1.4, bw=28, bh=6.6):
        d.box(cx - bw / 2, cy - bh / 2, bw, bh, P["gray"], ec=ec, lw=lw)
        d.text(cx, cy + (1.1 if meta else 0), title, size=10.5, weight="bold")
        if meta:
            d.text(cx, cy - 1.6, meta, size=8, color=P["accent"])

    # 강조(매치 대상): accent 테두리
    node(50, 44, "gateway span", "", ec=P["accent"], lw=2.6, bw=26)
    node(50, 33, "order-service span", "", bw=28)
    node(28, 22, "payment-service span", "", bw=26)
    node(72, 22, "inventory-service span", "", bw=26)
    node(28, 11, "DB Query span", "db.system=postgresql", ec=P["accent"], lw=2.6, bw=26)

    d.arrow(50, 40.7, 50, 36.3, color=P["dim"])
    d.arrow(44, 29.7, 33, 25.3, color=P["dim"])
    d.arrow(56, 29.7, 66, 25.3, color=P["dim"])
    d.arrow(28, 18.7, 28, 14.3, color=P["dim"])

    # 매치 판정
    d.box(58, 2, 39, 13, P["chip"])
    d.text(77.5, 11.6, '{ …"gateway" } >> { …postgresql }', size=8.5, color=P["accent"], weight="bold")
    d.text(77.5, 8.9, "→ 매치 (descendant)", size=8, color=P["accent"])
    d.text(77.5, 6.1, '{ …"gateway" } > { …postgresql }', size=8.5, color=P["violet"], weight="bold")
    d.text(77.5, 3.4, "→ 불일치 (사이에 span 존재)", size=8, color=P["orange"])

    d.text(30, 6, ">> descendant · > child\n<< ancestor · < parent · ~ sibling",
           size=8.5, color=P["dim"])

    d.legend([
        Line2D([0], [0], marker="s", color=P["bg"], markerfacecolor=P["gray"],
               markeredgecolor=P["accent"], markeredgewidth=2, markersize=12, lw=0,
               label="셀렉터 매치 대상 span"),
    ], loc="upper left", anchor=(0.02, 0.28))


diagram("23-structural-filter", draw, w=13, h=6.2, ymax=50)
