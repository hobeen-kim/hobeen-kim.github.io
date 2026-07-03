"""CH42 Grafana Alerting — 통합 알림 파이프라인 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # 왼쪽 위: Grafana-managed rule
    d.box(2, 26, 26, 18, P["blue"])
    d.text(15, 41.5, "Grafana-managed rule", size=11, weight="bold")
    d.text(15, 39, "(서버가 직접 평가)", size=8.5, color=P["dim"])
    for i, t in enumerate([
        "멀티 데이터소스 질의",
        "expression 파이프라인",
    ]):
        yy = 35.5 - i * 5
        d.box(4, yy - 2, 22, 4, P["chip"])
        d.text(15, yy, t, size=9.5)

    # 왼쪽 아래: datasource-managed rule
    d.box(2, 3, 26, 19, P["green"])
    d.text(15, 19, "datasource-managed rule", size=11, weight="bold")
    d.text(15, 16.7, "(백엔드 ruler 위임)", size=8.5, color=P["dim"])
    for i, t in enumerate([
        "Prometheus / Mimir ruler",
        "Loki ruler",
    ]):
        yy = 12.5 - i * 5
        d.box(4, yy - 2, 22, 4, P["chip"])
        d.text(15, yy, t, size=9.5)

    # 중앙: 내장 Alertmanager
    d.box(34, 6, 28, 38, P["gray"], ec=P["accent"], lw=1.8)
    d.text(48, 41.5, "Grafana 내장 Alertmanager", size=11, weight="bold", color=P["accent"])
    d.text(48, 39, "(Prometheus AM 임베드)", size=8.5, color=P["dim"])
    for i, t in enumerate([
        "notification policy 트리",
        "grouping",
        "mute timing · silence",
        "외부 Alertmanager 전달",
    ]):
        yy = 33 - i * 7
        d.box(36, yy - 2.5, 24, 5, P["chip"])
        d.text(48, yy, t, size=9.5)

    # 오른쪽 위: contact point
    d.box(70, 28, 26, 16, P["brown"])
    d.text(83, 41.5, "contact point", size=11, weight="bold")
    for i, t in enumerate([
        "Slack · Teams · Email",
        "webhook · PagerDuty",
    ]):
        yy = 37 - i * 4.6
        d.box(72, yy - 1.9, 22, 3.8, P["chip"])
        d.text(83, yy, t, size=9.5)

    # 오른쪽 아래: Grafana IRM
    d.box(70, 4, 26, 21, P["purple"])
    d.text(83, 22, "Grafana IRM", size=11, weight="bold")
    d.text(83, 19.7, "(알림 이후 대응)", size=8.5, color=P["dim"])
    for i, t in enumerate([
        "온콜 스케줄",
        "에스컬레이션 체인",
        "인시던트 관리",
    ]):
        yy = 15.5 - i * 4.3
        d.box(72, yy - 1.8, 22, 3.6, P["chip"])
        d.text(83, yy, t, size=9)

    # 흐름 화살표
    d.arrow(28, 35, 34, 33, color=P["orange"])
    d.text(31, 36.4, "firing", size=8, color=P["orange"])
    d.arrow(28, 12, 34, 17, color=P["orange"])
    d.arrow(62, 35, 70, 35, color=P["accent"])
    d.text(66, 37, "라우팅", size=8, color=P["accent"])
    d.arrow(83, 28, 83, 25, color=P["violet"])
    d.text(87.5, 26.5, "escalate", size=8, color=P["violet"])

    d.legend([
        Line2D([0], [0], color=P["orange"], lw=2.5, label="룰 평가 → firing"),
        Line2D([0], [0], color=P["accent"], lw=2.5, label="라우팅 → 알림 채널"),
        Line2D([0], [0], color=P["violet"], lw=2.5, label="IRM 에스컬레이션"),
    ])


diagram("42-grafana-alerting", draw, w=13, h=6.4, ymax=48)
