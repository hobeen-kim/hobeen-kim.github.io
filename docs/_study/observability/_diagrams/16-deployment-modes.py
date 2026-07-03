"""CH16 Loki 배포 모드 — monolithic / simple scalable / microservices (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # Monolithic (좌)
    d.box(3, 8, 28, 38, P["gray"])
    d.text(17, 42.5, "Monolithic", size=13, weight="bold", color=P["accent"])
    d.text(17, 39.5, "단일 / 소규모", size=9, color=P["dim"])
    d.box(6, 22, 22, 12, P["chip"])
    d.text(17, 28, "단일 프로세스\n모든 컴포넌트 함께", size=10)

    # Simple Scalable (중앙)
    d.box(35, 8, 30, 38, P["green"], ec=P["accent"], lw=1.8)
    d.text(50, 42.5, "Simple Scalable", size=13, weight="bold", color=P["accent"])
    d.text(50, 39.5, "프로덕션 권장 기본", size=9, color=P["dim"])
    for i, (t, sub) in enumerate([
        ("read", "query-frontend · querier"),
        ("write", "distributor · ingester"),
        ("backend", "compactor · ruler · index-gateway"),
    ]):
        yy = 33 - i * 8
        d.box(37.5, yy - 3, 25, 6, P["chip"])
        d.text(50, yy + 0.4, t + " 타깃", size=10, weight="bold")
        d.text(50, yy - 1.8, sub, size=7.5, color=P["dim"])

    # Microservices (우)
    d.box(69, 8, 28, 38, P["brown"])
    d.text(83, 42.5, "Microservices", size=13, weight="bold", color=P["accent"])
    d.text(83, 39.5, "초대형 멀티테넌시", size=9, color=P["dim"])
    comps = ["distributor", "ingester", "querier",
             "query-frontend", "compactor", "index-gateway"]
    for i, c in enumerate(comps):
        col, row = i % 2, i // 2
        bx = 71 + col * 12.5
        by = 32 - row * 8
        d.box(bx, by - 2.6, 11.8, 5.2, P["chip"])
        d.text(bx + 5.9, by, c, size=7.3, weight="bold")
    d.text(83, 11.5, "컴포넌트별 독립 확장", size=8.5, color=P["dim"])


diagram("16-deployment-modes", draw, w=13, h=6, ymax=48)
