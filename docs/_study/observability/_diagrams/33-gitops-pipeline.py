"""CH33 GitOps 대시보드 배포 파이프라인 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # ---- Git ----
    d.box(2, 20, 18, 20, P["gray"])
    d.text(11, 37.6, "Git 리포지토리", size=11, weight="bold")
    d.box(4, 27, 14, 8, P["chip"])
    d.text(11, 31, "jsonnet\n대시보드 정의", size=9.5)

    # ---- CI ----
    d.box(23, 16, 20, 24, P["blue"])
    d.text(33, 37.6, "CI 파이프라인", size=11, weight="bold")
    d.box(25, 29, 16, 6.5, P["chip"])
    d.text(33, 32.2, "jsonnet 컴파일 → JSON", size=9)
    d.box(25, 20, 16, 6.5, P["chip"])
    d.text(33, 23.2, "ConfigMap\n매니페스트 생성", size=9)
    d.arrow(33, 29, 33, 26.5, color=P["accent"], lw=1.8)

    # ---- CD ----
    d.box(46, 24, 18, 16, P["green"])
    d.text(55, 37.6, "GitOps 컨트롤러", size=10.5, weight="bold")
    d.text(55, 35.4, "ArgoCD / Flux", size=8.5, color=P["dim"])
    d.box(48, 27, 14, 6, P["chip"])
    d.text(55, 30, "클러스터에\n동기화", size=9)

    # ---- Cluster ----
    d.box(67, 6, 31, 34, P["brown"], ec=P["orange"], lw=1.6)
    d.text(82.5, 37.6, "쿠버네티스 클러스터", size=11, weight="bold")
    d.box(70, 28, 25, 6.5, P["chip"])
    d.text(82.5, 31.2, "ConfigMap\n(grafana_dashboard=1)", size=8.5)
    d.box(70, 18.5, 25, 6, P["chip"])
    d.text(82.5, 21.5, "k8s-sidecar", size=10)
    d.box(70, 9, 25, 6, P["chip"])
    d.text(82.5, 12, "Grafana", size=10)
    d.arrow(82.5, 28, 82.5, 24.5, color=P["orange"], lw=2.0)
    d.text(88.5, 26.2, "watch", size=8, color=P["orange"])
    d.arrow(82.5, 18.5, 82.5, 15, color=P["orange"], lw=2.0)
    d.text(89.5, 16.7, "파일 동기화", size=8, color=P["orange"])

    # ---- inter-group flow ----
    d.arrow(20, 31, 23, 32, color=P["accent"], lw=2.2)
    d.arrow(43, 23, 46, 30, color=P["accent"], lw=2.2)
    d.arrow(64, 31, 70, 31.2, color=P["accent"], lw=2.2)

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.4, label="파이프라인 진행"),
        Line2D([0], [0], color=P["orange"], lw=2.4, label="클러스터 내부 watch·동기화"),
    ], loc="lower left", anchor=(0.005, 0.02))


diagram("33-gitops-pipeline", draw, w=14, h=7, ymax=42)
