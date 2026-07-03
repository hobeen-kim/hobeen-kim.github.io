"""CH08 Exporter 패턴 — 브릿지 구조 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # 좌: 계측 불가능한 대상
    d.box(2, 3, 24, 38, P["gray"])
    d.text(14, 38.4, "계측 불가능한 대상", size=11, weight="bold", color=P["dim"])
    # 중앙: Exporter
    d.box(37, 3, 24, 38, P["green"], ec=P["accent"], lw=1.8)
    d.text(49, 38.4, "Exporter (브릿지)", size=11, weight="bold", color=P["accent"])

    targets = [
        (31, "OS / 커널", "/proc · /sys"),
        (20, "MySQL", "DB 서버 상태"),
        (9, "HTTP 엔드포인트", "외부 서비스"),
    ]
    exporters = [
        (31, "node-exporter"),
        (20, "mysqld_exporter"),
        (9, "blackbox_exporter"),
    ]
    for yc, t, sub in targets:
        d.box(4, yc - 4, 20, 8, P["chip"])
        d.text(14, yc + 1, t, size=9.5)
        d.text(14, yc - 1.8, sub, size=8, color=P["dim"])
    for yc, t in exporters:
        d.box(39, yc - 4, 20, 8, P["chip"])
        d.text(49, yc, t, size=9.5)

    # 우: Prometheus
    d.box(76, 15, 22, 14, P["blue"])
    d.text(87, 24, "Prometheus", size=12, weight="bold")
    d.text(87, 20.5, "pull 스크레이프", size=8.5, color=P["dim"])

    # 대상 → Exporter
    te_labels = ["", "SQL 질의", "probe"]
    for (yc, *_), lbl in zip(targets, te_labels):
        d.arrow(24, yc, 39, yc, color=P["orange"])
        if lbl:
            d.text(31.5, yc + 1.8, lbl, size=8, color=P["orange"])
    # Exporter → Prometheus
    ep = [(31, 26, "/metrics"), (20, 22, "/metrics"), (9, 18, "/probe")]
    for yc, ty, lbl in ep:
        d.arrow(59, yc, 76, ty, color=P["accent"], rad=0.06)
        d.text(68, (yc + ty) / 2 + 1.6, lbl, size=8, color=P["accent"])

    d.legend([
        Line2D([0], [0], color=P["orange"], lw=2.5, label="대상 → Exporter 읽기"),
        Line2D([0], [0], color=P["accent"], lw=2.5, label="Exporter → Prometheus 스크레이프"),
    ])


diagram("08-exporter-pattern", draw, w=12.5, h=6.4, ymax=44)
