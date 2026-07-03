"""CH33 GitOps 대시보드 배포 파이프라인 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=8.4, ymax=56)
box, text, arrow = make_helpers(ax)

text(50, 53.4, "GitOps 대시보드 배포 파이프라인", size=20, weight="bold")
text(50, 50.4, "Git → CI(컴파일·매니페스트) → GitOps 컨트롤러 → ConfigMap + 사이드카 → Grafana",
     size=12, color=C_DIM)

# ---- Git ----
box(2, 20, 18, 20, C_GRAY)
text(11, 37.6, "Git 리포지토리", size=11.5, weight="bold")
box(4, 27, 14, 8, "#1b232a")
text(11, 31, "jsonnet\n대시보드 정의", size=10)

# ---- CI ----
box(23, 16, 20, 24, C_BLUE)
text(33, 37.6, "CI 파이프라인", size=11.5, weight="bold")
box(25, 29, 16, 6.5, "#1b232a")
text(33, 32.2, "jsonnet 컴파일\n→ JSON", size=9.5)
box(25, 20, 16, 6.5, "#1b232a")
text(33, 23.2, "ConfigMap\n매니페스트 생성", size=9.5)
arrow(33, 29, 33, 26.5, color=C_ACCENT, lw=1.8)

# ---- CD ----
box(46, 24, 18, 16, C_GREEN)
text(55, 37.6, "GitOps 컨트롤러", size=11, weight="bold")
text(55, 35.4, "ArgoCD / Flux", size=8.5, color=C_DIM)
box(48, 27, 14, 6, "#1d2b24")
text(55, 30, "클러스터에\n동기화", size=9.5)

# ---- Cluster ----
box(67, 6, 31, 34, C_BROWN, ec="#8a6a52", lw=1.6)
text(82.5, 37.6, "쿠버네티스 클러스터", size=11.5, weight="bold")
box(70, 28, 25, 6.5, "#241d1a")
text(82.5, 31.2, "ConfigMap  (label: grafana_dashboard=1)", size=8.8)
box(70, 18.5, 25, 6, "#241d1a")
text(82.5, 21.5, "k8s-sidecar", size=10)
box(70, 9, 25, 6, "#241d1a")
text(82.5, 12, "Grafana", size=10)
arrow(82.5, 28, 82.5, 24.5, color=C_ORANGE, lw=2.0)
text(89, 26.2, "watch", size=8.5, color=C_ORANGE)
arrow(82.5, 18.5, 82.5, 15, color=C_ORANGE, lw=2.0)
text(90, 16.7, "파일 동기화", size=8.5, color=C_ORANGE)

# ---- inter-group flow ----
arrow(20, 31, 23, 32, color=C_ACCENT, lw=2.2)
arrow(43, 23, 46, 30, color=C_ACCENT, lw=2.2)
arrow(64, 31, 70, 31.2, color=C_ACCENT, lw=2.2)

text(50, 2.6, "쿠버네티스 선언적 배포 원칙을 관측성 스택에 그대로 적용 — 롤백은 git revert",
     size=10, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.4, label="파이프라인 진행"),
    Line2D([0], [0], color=C_ORANGE, lw=2.4, label="클러스터 내부 watch·동기화"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.02),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "33-gitops-pipeline.png")
