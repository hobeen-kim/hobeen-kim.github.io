"""CH05 §3 생태계 — 계측·브릿지·배치·SD·알림 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 왼쪽 세 소스 그룹
    d.box(2, 33, 24, 9, P["green"])
    d.text(14, 37.5, "계측 (화이트박스)\nClient Library + 앱", size=10)
    d.box(2, 19.5, 24, 9, P["brown"])
    d.text(14, 24, "Exporter (브릿지)\nOS·DB 등 계측 불가 대상", size=10)
    d.box(2, 6, 24, 9, P["blue"])
    d.text(14, 10.5, "Pushgateway (배치)\n단명 배치 잡 결과 중계", size=10)

    # 중앙 Prometheus
    d.box(40, 21, 22, 13, P["gray"], ec=P["accent"], lw=1.8)
    d.text(51, 27.5, "Prometheus\n(단일 바이너리)", size=11, weight="bold",
           color=P["accent"])

    # 하단 Service Discovery
    d.box(40, 5, 22, 8, P["purple"])
    d.text(51, 9, "Service Discovery\nk8s·EC2·Consul·file", size=10)

    # 우측 Alertmanager
    d.box(76, 21, 22, 13, P["gray"], ec=P["orange"], lw=1.6)
    d.text(87, 27.5, "Alertmanager\n(분리된 별도 바이너리)", size=11, weight="bold",
           color=P["orange"])

    # 화살표 — pull 수집
    d.arrow(26, 37.5, 40, 30, color=P["accent"])
    d.arrow(26, 24, 40, 27.5, color=P["accent"])
    d.arrow(26, 10.5, 40, 24, color=P["accent"])
    d.text(33, 33, "pull /metrics", size=8, color=P["accent"])

    # SD → Prometheus
    d.arrow(51, 13, 51, 21, color=P["violet"])
    d.text(59, 17, "타깃 갱신", size=8, color=P["violet"])

    # Prometheus → Alertmanager
    d.arrow(62, 27.5, 76, 27.5, color=P["orange"])
    d.text(69, 29.3, "알림 전송", size=8, color=P["orange"])


diagram("05-ecosystem", draw, w=12, h=6, ymax=44)
