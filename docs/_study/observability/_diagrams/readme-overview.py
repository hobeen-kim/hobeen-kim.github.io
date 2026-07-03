"""README 전체 아키텍처 — 신호 수집 → 저장 → 시각화 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # 수집 계층
    d.box(2, 6, 24, 46, P["gray"])
    d.text(14, 49.4, "수집 계층", size=12, weight="bold")
    collect = [
        ("node-exporter", "노드 하드웨어"),
        ("kube-state-metrics", "오브젝트 상태"),
        ("cAdvisor", "컨테이너 사용량"),
        ("애플리케이션", "OTel SDK 계측"),
    ]
    for i, (t, s) in enumerate(collect):
        yy = 45 - i * 5.3
        d.box(4, yy - 2.1, 20, 4.2, P["chip"])
        d.text(14, yy + 0.5, t, size=9.5, weight="bold")
        d.text(14, yy - 1.3, s, size=7.6, color=P["dim"])
    d.box(4, 10, 20, 8.5, P["green"], ec=P["accent"], lw=1.8)
    d.text(14, 15.1, "Alloy /\nOTel Collector", size=10, weight="bold", color=P["accent"])
    d.text(14, 11.5, "수집·라우팅 에이전트", size=7.8, color=P["dim"])

    # 저장 / 백엔드 계층
    d.box(35, 6, 30, 46, P["blue"])
    d.text(50, 49.4, "저장 / 백엔드 계층", size=12, weight="bold")
    backends = [
        ("Prometheus", "메트릭 스크레이핑·TSDB", P["green"]),
        ("Mimir", "메트릭 장기 저장", P["green"]),
        ("Loki", "로그", P["brown"]),
        ("Tempo", "트레이스", P["brown"]),
        ("Pyroscope", "프로파일", P["brown"]),
    ]
    for i, (t, s, fc) in enumerate(backends):
        yy = 45 - i * 7.1
        d.box(38, yy - 2.7, 24, 5.4, fc)
        d.text(50, yy + 0.6, t, size=10, weight="bold")
        d.text(50, yy - 1.5, s, size=7.8, color=P["dim"])

    # 알림
    d.box(72, 33, 24, 12, P["brown"])
    d.text(84, 41.4, "알림", size=12, weight="bold")
    d.box(74, 34.5, 20, 5, P["chip"])
    d.text(84, 37, "Alertmanager", size=10, weight="bold")

    # 시각화
    d.box(72, 13, 24, 14, P["gray"], ec=P["accent"], lw=2.0)
    d.text(84, 23.4, "시각화", size=12, weight="bold")
    d.box(74, 15, 20, 6, P["chip"], ec=P["accent"], lw=1.6)
    d.text(84, 18.6, "Grafana", size=11.5, weight="bold", color=P["accent"])
    d.text(84, 16.2, "4대 신호 상관관계", size=7.8, color=P["dim"])

    # 수집 → 백엔드
    d.arrow(24, 43, 38, 44.5, color=P["orange"], lw=1.6, rad=-0.06)
    d.arrow(24, 37.7, 38, 44.0, color=P["orange"], lw=1.6, rad=-0.03)
    d.arrow(24, 32.4, 38, 43.5, color=P["orange"], lw=1.6, rad=0.03)
    d.arrow(14, 27.5, 14, 18.5, color=P["accent"], lw=1.6)
    d.text(20.5, 23, "OTLP", size=7.8, color=P["accent"], weight="bold")
    d.arrow(24, 15, 38, 43, color=P["accent"], lw=1.5, rad=-0.16)
    d.arrow(24, 14.5, 38, 23.5, color=P["accent"], lw=1.5, rad=-0.08)
    d.arrow(24, 13.5, 38, 16.5, color=P["accent"], lw=1.5, rad=0.05)
    d.text(30, 26, "Alloy →\n각 백엔드", size=7.8, color=P["accent"], weight="bold")

    # prometheus → mimir
    d.arrow(50, 42.3, 50, 40.5, color=P["violet"], lw=2.0)
    d.text(62, 41.4, "remote_write", size=7.8, color=P["violet"], weight="bold")
    # prometheus → AM
    d.arrow(62, 41, 72, 39, color=P["orange"], lw=1.6, rad=-0.08)
    d.text(67, 43, "rule 평가", size=7.8, color=P["orange"], weight="bold")

    # 백엔드 → grafana
    for yy in (42.3, 35.2, 28.1, 21.0, 13.9):
        d.arrow(62, yy, 74, 18.5, color=P["dim"], lw=1.1, rad=0.12)
    d.arrow(84, 33, 84, 27, color=P["dim"], lw=1.2)

    d.legend([
        Line2D([0], [0], color=P["orange"], lw=2.5, label="메트릭 pull / rule 평가"),
        Line2D([0], [0], color=P["accent"], lw=2.5, label="Alloy 수집·라우팅 (OTLP)"),
        Line2D([0], [0], color=P["violet"], lw=2.5, label="remote_write (장기 저장)"),
        Line2D([0], [0], color=P["dim"], lw=2.5, label="데이터소스 조회"),
    ], loc="lower left", anchor=(0.685, 0.02))


diagram("readme-overview", draw, w=14, h=7, ymax=53)
