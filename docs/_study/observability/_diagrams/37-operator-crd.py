"""CH37 Prometheus Operator — 선언적 CRD → Operator watch·reconcile → 생성 리소스 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # 좌: 사용자 선언 CRD
    d.box(2, 5, 26, 40, P["blue"])
    d.text(15, 42.4, "사용자 선언 CRD", size=11, weight="bold")
    crds = [
        ("Prometheus CR", "replicas·retention·selector"),
        ("ServiceMonitor", "Service 뒤 Pod 스크레이프"),
        ("PodMonitor", "Pod 직접 스크레이프"),
        ("PrometheusRule", "recording·alerting rule"),
    ]
    for i, (t, s) in enumerate(crds):
        yy = 37 - i * 7.5
        d.box(4, yy - 3, 22, 6, P["chip"])
        d.text(15, yy + 0.5, t, size=9.5, weight="bold")
        d.text(15, yy - 1.7, s, size=8, color=P["dim"])

    # 중앙: Operator
    d.box(38, 20, 24, 12, P["gray"], ec=P["accent"], lw=1.8)
    d.text(50, 27, "Prometheus Operator", size=11.5, weight="bold", color=P["accent"])
    d.text(50, 23.5, "(컨트롤러)", size=9, color=P["dim"])

    # 우: 생성 리소스
    d.box(72, 5, 26, 40, P["green"])
    d.text(85, 42.4, "Operator가 생성", size=11, weight="bold")
    gens = [
        ("Secret", "prometheus.yaml"),
        ("ConfigMap / Secret", "rule 파일"),
        ("StatefulSet", "Prometheus Pod"),
    ]
    for i, (t, s) in enumerate(gens):
        yy = 36 - i * 9.5
        d.box(74, yy - 3, 22, 6, P["chip"])
        d.text(85, yy + 0.5, t, size=9.5, weight="bold")
        d.text(85, yy - 1.7, s, size=8, color=P["dim"])

    # CRD → Operator (watch)
    for yy in (37, 30, 22.5, 15):
        d.arrow(28, yy, 38, 26, color=P["orange"], lw=1.5, rad=0.04)
    d.text(33, 33.5, "watch", size=8, color=P["orange"], weight="bold")

    # Operator → 생성 리소스
    for yy in (36, 26.5, 16):
        d.arrow(62, 26, 74, yy, color=P["accent"], lw=1.6)
    d.text(68, 30.5, "생성", size=8, color=P["accent"], weight="bold")

    # Secret / rule → StatefulSet (마운트)
    d.arrow(94.5, 30, 94.5, 19, color=P["violet"], lw=1.6, rad=0.35)
    d.text(90, 12.5, "마운트", size=8, color=P["violet"], weight="bold")

    d.legend([
        Line2D([0], [0], color=P["orange"], lw=2.5, label="watch · selector 매칭"),
        Line2D([0], [0], color=P["accent"], lw=2.5, label="리소스 생성 (reconcile)"),
        Line2D([0], [0], color=P["violet"], lw=2.5, label="Pod에 마운트"),
    ], anchor=(0.33, 0.02))


diagram("37-operator-crd", draw, w=12, h=6, ymax=48)
