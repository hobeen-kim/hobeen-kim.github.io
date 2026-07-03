"""CH12 여러 Prometheus → Mimir 장기 저장·전역 쿼리 연동 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # left: Prometheus instances
    for i, name in enumerate(["Prometheus #1", "Prometheus #2", "Prometheus #N"]):
        yy = 30 - i * 9
        d.box(3, yy - 3, 20, 6, P["gray"])
        d.text(13, yy, name, size=10, weight="bold")

    # center: Mimir
    d.box(33, 9, 26, 25, P["green"], ec=P["accent"], lw=1.8)
    d.text(46, 30, "Mimir", size=13, weight="bold", color=P["accent"])
    d.text(46, 26, "distributor → ingester", size=9.5)
    d.text(46, 22, "(수평 확장 저장·질의 계층)", size=9, color=P["dim"])
    d.box(35, 12, 22, 6, P["chip"])
    d.text(46, 15, "단일 노드·짧은 retention 극복", size=8.5, color=P["dim"])

    # right top: Object storage
    d.box(66, 24, 30, 9, P["brown"])
    d.text(81, 30, "오브젝트 스토리지", size=11, weight="bold")
    d.text(81, 26.7, "(장기 블록 저장)", size=9, color=P["dim"])

    # right mid: Query Frontend
    d.box(66, 12, 20, 9, P["blue"])
    d.text(76, 17.5, "Query Frontend", size=10, weight="bold")
    d.text(76, 14.3, "(전역 쿼리)", size=9, color=P["dim"])

    # right: Grafana
    d.box(89, 12, 8, 9, P["orange"])
    d.text(93, 16.5, "Grafana", size=9, weight="bold")

    # arrows: prometheus -> mimir
    for i in range(3):
        yy = 30 - i * 9
        d.arrow(23, yy, 33, 21, color=P["accent"])
    d.text(27, 27, "remote_write", size=8, color=P["accent"])

    # mimir -> obj / QF
    d.arrow(59, 24, 66, 28, color=P["violet"])
    d.arrow(59, 17, 66, 16.5, color=P["accent"])
    # QF -> grafana
    d.arrow(86, 16.5, 89, 16.5, color=P["accent"])

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.5, label="remote_write / 쿼리 경로"),
        Line2D([0], [0], color=P["violet"], lw=2.5, label="장기 블록 저장"),
    ])


diagram("12-mimir-fanout", draw, w=13, h=6, ymax=38)
