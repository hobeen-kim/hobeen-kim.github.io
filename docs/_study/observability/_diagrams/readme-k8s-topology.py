"""README Kubernetes 배포 토폴로지 — kube-prometheus-stack (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 클러스터 외곽
    d.box(2, 4, 96, 49.5, P["chip"], ec=P["edge"], lw=1.6)
    d.text(6, 51, "Kubernetes 클러스터", size=11, weight="bold", color=P["dim"], ha="left")

    # kube-prometheus-stack (monitoring ns)
    d.box(5, 9, 36, 39, P["blue"])
    d.text(23, 45.2, "kube-prometheus-stack (monitoring ns)", size=9.5, weight="bold")
    d.box(8, 38, 30, 6, P["gray"], ec=P["accent"], lw=1.6)
    d.text(23, 41, "Prometheus Operator", size=10.5, weight="bold")
    d.box(8, 29.5, 30, 6, P["green"], ec=P["accent"], lw=1.6)
    d.text(23, 32.5, "Prometheus (StatefulSet)", size=10, weight="bold")
    d.box(8, 12, 14, 6.5, P["brown"])
    d.text(15, 15.9, "Alertmanager", size=9.5, weight="bold")
    d.text(15, 13.6, "(StatefulSet)", size=7.8, color=P["dim"])
    d.box(24, 12, 14, 6.5, P["gray"], ec=P["accent"], lw=1.4)
    d.text(31, 15.9, "Grafana", size=9.5, weight="bold")
    d.text(31, 13.6, "(Deployment)", size=7.8, color=P["dim"])

    # 커스텀 리소스
    d.box(48, 32, 21, 15, P["gray"], ec=P["accent"], lw=1.6)
    d.text(58.5, 43.6, "커스텀 리소스", size=10.5, weight="bold")
    d.box(50, 37.5, 17, 3.8, P["chip"])
    d.text(58.5, 39.4, "ServiceMonitor", size=9.2, weight="bold")
    d.box(50, 32.8, 17, 3.8, P["chip"])
    d.text(58.5, 34.7, "PodMonitor", size=9.2, weight="bold")

    # kube-state-metrics
    d.box(74, 32, 20, 15, P["gray"])
    d.text(84, 43.6, "Deployment", size=9, color=P["dim"], weight="bold")
    d.box(76, 35, 16, 6, P["chip"])
    d.text(84, 38, "kube-state-metrics", size=9, weight="bold")

    # DaemonSet
    d.box(48, 8, 46, 20, P["green"])
    d.text(71, 25.2, "DaemonSet (모든 노드)", size=10.5, weight="bold")
    d.box(52, 12, 18, 9, P["chip"], ec=P["accent"], lw=1.4)
    d.text(61, 17.5, "node-exporter", size=9.8, weight="bold")
    d.text(61, 14.5, "노드 메트릭", size=7.8, color=P["dim"])
    d.box(74, 12, 18, 9, P["chip"], ec=P["accent"], lw=1.4)
    d.text(83, 17.5, "Alloy", size=10.5, weight="bold", color=P["accent"])
    d.text(83, 14.5, "로그·프로파일", size=7.8, color=P["dim"])

    # Operator → SM/PM (watch)
    d.arrow(38, 41.5, 50, 39.4, color=P["orange"], lw=1.7, rad=-0.05)
    d.arrow(38, 40.5, 50, 34.7, color=P["orange"], lw=1.7, rad=0.05)
    d.text(44, 43, "watch", size=8, color=P["orange"], weight="bold")
    # Operator → Prometheus
    d.arrow(23, 38, 23, 35.5, color=P["accent"], lw=1.9)
    d.text(31, 36.7, "설정 생성", size=7.8, color=P["accent"], weight="bold")
    # SM/PM → Prometheus
    d.arrow(50, 38, 38, 33.5, color=P["violet"], lw=1.6, rad=0.12)
    d.arrow(50, 33.8, 38, 32, color=P["violet"], lw=1.6, rad=0.06)
    d.text(44, 29.8, "스크레이프\n대상 정의", size=7.6, color=P["violet"], weight="bold")
    # 수집원 → Prometheus (메트릭)
    d.arrow(61, 21, 39, 30.5, color=P["dim"], lw=1.3, rad=0.14)
    d.arrow(74, 16.5, 38, 30, color=P["dim"], lw=1.3, rad=0.2)
    d.arrow(76, 36.5, 38, 32.5, color=P["dim"], lw=1.3, rad=0.1)
    d.text(50, 24.5, "메트릭 → Prometheus", size=8, color=P["dim"], weight="bold")
    # Prometheus → AM / Grafana
    d.arrow(18, 29.5, 15, 18.5, color=P["orange"], lw=1.5, rad=0.08)
    d.text(9.5, 24, "rule\n평가", size=7.4, color=P["orange"], weight="bold")
    d.arrow(28, 29.5, 31, 18.5, color=P["dim"], lw=1.3, rad=-0.08)
    d.text(37, 24, "조회", size=7.4, color=P["dim"], weight="bold")


diagram("readme-k8s-topology", draw, w=14, h=7.5, ymax=54)
