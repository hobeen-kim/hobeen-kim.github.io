"""CH04 Push 모델 — Pushgateway(단명 작업)와 OTLP(장기 서비스) (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 위 경로: 단명 배치 작업 → Pushgateway → Prometheus
    d.box(3, 28, 26, 11, P["brown"], ec=P["orange"], lw=1.6)
    d.text(16, 35, "단명 배치 작업", size=11, weight="bold", color=P["orange"])
    d.text(16, 31, "Cron Job", size=8.5, color=P["dim"])

    d.box(40, 28, 24, 11, P["gray"])
    d.text(52, 35, "Pushgateway", size=11, weight="bold")
    d.text(52, 31, "마지막 값 보관", size=8.5, color=P["dim"])

    d.box(74, 28, 23, 11, P["blue"])
    d.text(85.5, 35, "Prometheus", size=11, weight="bold")
    d.text(85.5, 31, "pull로 수집", size=8.5, color=P["dim"])

    d.arrow(29, 33.5, 40, 33.5, color=P["orange"])
    d.text(34.5, 35.4, "종료 직전 push", size=8, color=P["orange"])
    d.arrow(64, 33.5, 74, 33.5, color=P["violet"])
    d.text(69, 35.4, "pull", size=8, color=P["violet"])

    # 아래 경로: 장기 서비스 → Alloy/OTel → Mimir
    d.box(3, 8, 26, 11, P["green"], ec=P["accent"], lw=1.6)
    d.text(16, 15, "장기 실행 서비스", size=11, weight="bold", color=P["accent"])
    d.text(16, 11, "OTel SDK", size=8.5, color=P["dim"])

    d.box(40, 8, 24, 11, P["gray"])
    d.text(52, 15, "Alloy / OTel", size=10.5, weight="bold")
    d.text(52, 11, "OTLP 리시버", size=8.5, color=P["dim"])

    d.box(74, 8, 23, 11, P["blue"], ec=P["accent"], lw=1.5)
    d.text(85.5, 13.5, "Mimir", size=12, weight="bold")

    d.arrow(29, 13.5, 40, 13.5, color=P["accent"])
    d.text(34.5, 15.4, "OTLP push", size=8, color=P["accent"])
    d.arrow(64, 13.5, 74, 13.5, color=P["accent"])


diagram("04-push-model", draw, w=13, h=5.2, ymax=44)
