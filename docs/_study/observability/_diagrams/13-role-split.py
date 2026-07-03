"""CH13 Prometheus와 Alertmanager 역할 분리 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # left group: Prometheus
    d.box(3, 10, 26, 24, P["gray"])
    d.text(16, 31.5, "Prometheus", size=12, weight="bold")
    d.box(6, 22, 20, 6, P["blue"])
    d.text(16, 25.6, "Alerting Rule", size=10, weight="bold")
    d.text(16, 23.4, "(PromQL 조건)", size=8.5, color=P["dim"])
    d.box(6, 12.5, 20, 6, P["blue"])
    d.text(16, 16.1, "룰 평가 엔진", size=10, weight="bold")
    d.text(16, 13.9, "(evaluation_interval)", size=8.5, color=P["dim"])
    d.arrow(16, 22, 16, 18.5, color=P["accent"])

    # center group: Alertmanager
    d.box(37, 10, 30, 24, P["green"], ec=P["accent"], lw=1.8)
    d.text(52, 31.5, "Alertmanager", size=12, weight="bold", color=P["accent"])
    for i, (t, sub) in enumerate([
        ("알림 수신", ""),
        ("파이프라인", "dedup / group / inhibit\n/ silence / route"),
        ("Notifier", ""),
    ]):
        yy = 27.5 - i * 6.0
        h = 4.8 if sub else 3.4
        d.box(39, yy - h / 2, 26, h, P["chip"])
        if sub:
            d.text(52, yy + 1.0, t, size=9.5, weight="bold")
            d.text(52, yy - 1.0, sub, size=7.8, color=P["dim"])
        else:
            d.text(52, yy, t, size=10, weight="bold")
    d.arrow(52, 25.2, 52, 21.9, color=P["accent"])
    d.arrow(52, 15.2, 52, 13.4, color=P["accent"])

    # right: channels
    for i, name in enumerate(["Slack", "PagerDuty", "Webhook"]):
        yy = 29 - i * 7
        d.box(75, yy - 2.6, 20, 5.2, P["brown"])
        d.text(85, yy, name, size=10, weight="bold")

    # Prometheus -> Alertmanager
    d.arrow(29, 14.5, 37, 26, color=P["orange"], rad=-0.28)
    d.text(30.5, 20.5, "HTTP POST\n/api/v2/alerts\n(firing)", size=8, color=P["orange"],
           ha="left")

    # Notifier -> channels
    for i in range(3):
        yy = 29 - i * 7
        d.arrow(67, 12.5, 75, yy, color=P["accent"])

    d.legend([
        Line2D([0], [0], color=P["orange"], lw=2.5, label="firing 알림 전송"),
        Line2D([0], [0], color=P["accent"], lw=2.5, label="내부 처리 / 채널 전달"),
    ])


diagram("13-role-split", draw, w=13, h=6.2, ymax=40)
