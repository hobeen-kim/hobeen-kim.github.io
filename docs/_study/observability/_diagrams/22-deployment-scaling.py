"""CH22 배포·스케일링 — stateless/stateful 컴포넌트와 hash ring (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    def chip(cx, cy, t, c, bw=18, bh=6):
        d.box(cx - bw / 2, cy - bh / 2, bw, bh, P[c])
        d.text(cx, cy, t, size=10.5, weight="bold")

    # Stateless 그룹
    d.box(4, 18, 42, 26, P["gray"])
    d.text(25, 41, "Stateless (수평 확장 쉬움)", size=11.5, weight="bold", color=P["accent"])
    chip(25, 36, "Distributor", "blue", bw=20)
    chip(15, 26, "Query Frontend", "green", bw=18)
    chip(35, 26, "Querier", "green", bw=16)

    # Stateful 그룹
    d.box(54, 18, 42, 26, P["gray"], ec=P["orange"], lw=1.8)
    d.text(75, 41, "Stateful (샤딩·리텐션 관리)", size=11.5, weight="bold", color=P["orange"])
    chip(75, 36, "Ingester", "brown", bw=20)
    chip(75, 26, "Compactor", "brown", bw=20)

    # Hash Ring
    d.box(38, 5, 24, 8, P["purple"])
    d.text(50, 10, "Hash Ring", size=11, weight="bold")
    d.text(50, 7, "memberlist gossip", size=8.5, color=P["dim"])

    d.arrow(35, 36, 65, 36, color=P["accent"])
    d.arrow(24, 26, 27, 26, color=P["accent"])
    d.arrow(40, 27, 66, 34.5, color=P["accent"])

    d.arrow(23, 33, 42, 13.2, color=P["dim"], ls=(0, (4, 3)))
    d.text(29, 22, "링 조회", size=8, color=P["dim"], style="italic")
    d.arrow(75, 33, 58, 13.2, color=P["dim"], ls=(0, (4, 3)))
    d.text(69, 22, "링 등록", size=8, color=P["dim"], style="italic")

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.0, label="데이터 흐름"),
        Line2D([0], [0], color=P["dim"], lw=2.0, ls="--", label="hash ring 조회·등록"),
    ])


diagram("22-deployment-scaling", draw, w=13, h=6, ymax=46)
