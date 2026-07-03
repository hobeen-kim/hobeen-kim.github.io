"""CH37 Prometheus Operator — CRD watch → 리소스 조정 다이어그램 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "Prometheus Operator — 선언적 CRD에서 실제 리소스로", size=20, weight="bold")
text(50, 56.6, "사용자가 만드는 CRD  →  Operator가 watch·reconcile  →  Prometheus가 읽는 설정·StatefulSet 생성",
     size=12, color=C_DIM)

# ================= left: user CRDs =================
box(2, 12, 26, 40, C_BLUE)
text(15, 49.4, "사용자가 선언하는 CRD", size=13, weight="bold")
text(15, 47.2, "kubectl apply 로 관리", size=9, color=C_ACCENT, style="italic")
crds = [
    ("Prometheus CR", "replicas · retention · selector"),
    ("ServiceMonitor", "Service 뒤 Pod 스크레이프 선언"),
    ("PodMonitor", "Pod 직접 스크레이프 선언"),
    ("PrometheusRule", "recording · alerting rule"),
]
for i, (t, d) in enumerate(crds):
    yy = 42.5 - i * 8.0
    box(4, yy - 3.0, 22, 6.0, "#1b232a")
    text(15, yy + 0.9, t, size=11, weight="bold")
    text(15, yy - 1.5, d, size=8, color=C_DIM)

# ================= center: operator =================
box(38, 26, 24, 14, C_GRAY, ec=C_ACCENT, lw=2.2)
text(50, 36.6, "Prometheus Operator", size=13.5, weight="bold", color=C_ACCENT)
text(50, 34.0, "(컨트롤러)", size=10, color=C_DIM)
text(50, 31.0, "CRD를 watch →\n변경 감지 시 reconcile", size=9.5, color=C_TEXT)

# left -> operator
for i in range(4):
    yy = 42.5 - i * 8.0
    lbl = "watch" if i == 0 else "watch · selector 매칭"
    arrow(28, yy, 38, 33 + (1.5 - i) * 2.2, color=C_ORANGE, lw=1.8, rad=0.05)
text(33, 45.2, "watch", size=8.5, color=C_ORANGE, weight="bold")
text(33, 15.5, "selector 라벨로\nCRD ↔ Prometheus 매칭", size=8, color=C_ORANGE)

# ================= right: generated resources =================
box(72, 12, 26, 40, C_GREEN)
text(85, 49.4, "Operator가 생성하는 리소스", size=12.5, weight="bold")
text(85, 47.2, "사용자가 직접 만들지 않음", size=9, color=C_ACCENT, style="italic")
gens = [
    ("Secret", "prometheus.yaml (scrape_configs)"),
    ("ConfigMap / Secret", "rule 파일"),
    ("StatefulSet", "Prometheus Pod"),
]
for i, (t, d) in enumerate(gens):
    yy = 43 - i * 7.2
    box(74, yy - 2.6, 22, 5.2, "#1d2b24")
    text(85, yy + 0.8, t, size=11, weight="bold")
    text(85, yy - 1.4, d, size=8, color=C_DIM)

# operator -> generated
arrow(62, 34, 74, 42.5, color=C_ACCENT, lw=2.0, rad=-0.08)
arrow(62, 33, 74, 35.3, color=C_ACCENT, lw=2.0)
arrow(62, 32, 74, 28.1, color=C_ACCENT, lw=2.0, rad=0.08)
text(68, 39.5, "생성", size=8.5, color=C_ACCENT, weight="bold")

# mount: Secret / rule -> StatefulSet (박스 우측 가장자리로 라우팅해 텍스트와 겹침 회피)
arrow(94.5, 40.4, 94.5, 30.6, color=C_VIOLET, lw=1.8, rad=0.3)
text(90, 27.5, "마운트", size=8, color=C_VIOLET, weight="bold")

# bottom
text(50, 7.0, "사용자는 relabel·scrape_configs 문법을 직접 다루지 않는다 — CR을 만들고 지우는 것만으로 스크레이프 대상·알림 규칙 관리",
     size=10, color=C_ACCENT, weight="bold")
text(50, 3.6, "Prometheus CR의 serviceMonitorSelector 라벨이 곧 '어느 Prometheus가 어느 팀 타깃을 스크레이프할지' 경계선",
     size=9, color=C_DIM, style="italic")

leg = [
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="CRD watch · selector 매칭"),
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="리소스 생성 (reconcile)"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, label="Pod에 마운트"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.11),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "37-operator-crd.png")
