"""CH31 Grafana 데이터소스 연결 — 5개 백엔드 → 패널 시스템 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 왼쪽: 데이터소스 그룹
    d.box(3, 4, 30, 37, P["gray"])
    d.text(18, 38.4, "Grafana 데이터소스", size=10.5, weight="bold", color=P["accent"])

    ds = [
        ("Prometheus", "type: prometheus", P["blue"]),
        ("Mimir", "Prometheus 호환 · 테넌트 헤더", P["blue"]),
        ("Loki", "type: loki · maxLines", P["green"]),
        ("Tempo", "type: tempo", P["brown"]),
        ("Pyroscope", "grafana-pyroscope-ds", P["purple"]),
    ]
    ys = []
    for i, (t, sub, col) in enumerate(ds):
        yc = 33 - i * 6.2
        ys.append(yc)
        d.box(5, yc - 2.6, 26, 5.2, col)
        d.text(18, yc + 0.5, t, size=9.5, weight="bold")
        d.text(18, yc - 1.5, sub, size=7.3, color=P["dim"])

    # 중앙: Grafana
    d.box(47, 13, 25, 17, P["green"], ec=P["accent"], lw=2.0)
    d.text(59.5, 26.8, "Grafana", size=12, weight="bold", color=P["accent"])
    d.box(49, 19.5, 21, 5, P["chip"])
    d.text(59.5, 22, "Query Editor", size=10, weight="bold")
    d.box(49, 14, 21, 5, P["chip"])
    d.text(59.5, 16.5, "패널 렌더링", size=10, weight="bold")
    d.arrow(59.5, 19.5, 59.5, 19, color=P["accent"], lw=1.8)

    for yc in ys:
        d.arrow(33, yc, 49, 22, color=P["accent"], lw=1.3, rad=0.03)

    # 오른쪽: 공유 시스템
    d.box(80, 16, 16, 10, P["blue"])
    d.text(88, 22.4, "동일 패널·변수", size=9, weight="bold")
    d.text(88, 19.4, "시스템 공유", size=8.3, color=P["dim"])
    d.arrow(72, 21, 80, 21, color=P["accent"], lw=1.8)


diagram("31-datasources", draw, w=13, h=6.2, ymax=43)
