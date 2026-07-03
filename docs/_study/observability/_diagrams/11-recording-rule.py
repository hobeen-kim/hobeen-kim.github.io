"""CH11 Recording Rule — 사전 계산 흐름 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(2, 20, 20, 10, P["gray"])
    d.text(12, 26.4, "원본 메트릭", size=11, weight="bold")
    d.text(12, 22.8, "http_requests_total", size=8, color=P["dim"], style="italic")

    d.box(28, 20, 24, 10, P["green"], ec=P["accent"], lw=1.8)
    d.text(40, 26.4, "Recording Rule", size=11, weight="bold", color=P["accent"])
    d.text(40, 22.8, "job:http_requests:rate5m", size=8, color=P["dim"], style="italic")

    d.box(58, 20, 20, 10, P["blue"])
    d.text(68, 26.4, "TSDB 저장", size=11, weight="bold")
    d.text(68, 22.8, "새 시계열로 기록", size=8, color=P["dim"])

    d.box(82, 31, 16, 9, P["brown"])
    d.text(90, 36.2, "Grafana 대시보드", size=9, weight="bold")
    d.text(90, 33.2, "가벼운 조회", size=8, color=P["dim"])

    d.box(82, 10, 16, 9, P["brown"])
    d.text(90, 15.2, "Alerting Rule", size=9, weight="bold")
    d.text(90, 12.2, "재사용 가능", size=8, color=P["dim"])

    d.arrow(22, 25, 28, 25, color=P["orange"])
    d.text(25, 27.4, "매 30초 평가", size=7.8, color=P["orange"])
    d.arrow(52, 25, 58, 25, color=P["accent"])
    d.arrow(78, 26, 82, 35, color=P["accent"], rad=0.12)
    d.arrow(78, 24, 82, 15, color=P["accent"], rad=-0.12)


diagram("11-recording-rule", draw, w=13, h=5.8, ymax=44)
