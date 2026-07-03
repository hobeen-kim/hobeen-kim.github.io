"""CH03 수집 전략 결정 트리 — Exporter / OTel Collector / Alloy (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 결정 노드 1
    d.box(37, 44, 26, 7, P["gray"], ec=P["accent"], lw=1.8, r=0.06)
    d.text(50, 47.5, "수집 대상은?", size=12, weight="bold", color=P["accent"])

    # Exporter 경로 (왼쪽)
    d.box(6, 31, 26, 8, P["brown"])
    d.text(19, 36.4, "Exporter", size=11, weight="bold")
    d.text(19, 33.2, "node · mysqld exporter", size=8, color=P["dim"])
    d.arrow(37, 46, 19, 39, color=P["orange"], rad=0.1)
    d.text(23, 43, "서드파티·레거시\n계측 불가", size=8, color=P["orange"])
    d.box(6, 19, 26, 7, P["chip"])
    d.text(19, 22.5, "Prometheus 스크레이프 (pull)", size=8.5, weight="bold")
    d.arrow(19, 31, 19, 26, color=P["accent"])

    # 결정 노드 2 (오른쪽)
    d.box(65, 43, 30, 8, P["gray"], ec=P["accent"], lw=1.8, r=0.06)
    d.text(80, 47, "벤더 중립성이 최우선?", size=10, weight="bold", color=P["accent"])
    d.arrow(63, 47, 65, 47, color=P["orange"])
    d.text(64, 53.5, "직접 계측 가능", size=8, color=P["orange"])

    # OTel Collector (예)
    d.box(52, 30, 24, 8, P["blue"])
    d.text(64, 34, "OpenTelemetry\nCollector", size=10, weight="bold")
    d.arrow(74, 43, 66, 38, color=P["accent"], rad=0.1)
    d.text(65, 41, "예", size=8, color=P["accent"])
    d.box(52, 18, 24, 7, P["chip"])
    d.text(64, 21.5, "여러 벤더 백엔드로 라우팅", size=8, weight="bold")
    d.arrow(64, 30, 64, 25, color=P["accent"])

    # Alloy (아니오)
    d.box(80, 30, 17, 8, P["green"])
    d.text(88.5, 34, "Alloy", size=11, weight="bold")
    d.arrow(88, 43, 88.5, 38, color=P["accent"])
    d.text(93.5, 41, "아니오", size=8, color=P["accent"])
    d.box(80, 18, 17, 7, P["chip"])
    d.text(88.5, 21.5, "Mimir/Loki/\nTempo/Pyroscope", size=8, weight="bold")
    d.arrow(88.5, 30, 88.5, 25, color=P["accent"])


diagram("03-collection-decision", draw, w=13, h=6.6, ymax=56)
