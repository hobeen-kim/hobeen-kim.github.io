"""README Kubernetes 배포 토폴로지 다이어그램 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "Kubernetes 배포 토폴로지 — kube-prometheus-stack", size=20, weight="bold")
text(50, 56.6, "Operator가 ServiceMonitor/PodMonitor를 감시해 Prometheus 설정을 자동 생성 · 수집 에이전트는 모든 노드에 DaemonSet",
     size=11.5, color=C_DIM)

# ---- 클러스터 외곽 ----
box(2, 4, 96, 49.5, "#12181d", ec=C_EDGE, lw=1.6)
text(6, 51.0, "Kubernetes 클러스터", size=12, weight="bold", color=C_DIM, ha="left")

# ================= kube-prometheus-stack (monitoring ns) — 좌측 세로 =================
box(5, 9, 36, 39, C_BLUE)
text(23, 45.2, "kube-prometheus-stack (monitoring 네임스페이스)", size=10, weight="bold")
# Operator (상단 전폭)
box(8, 38, 30, 6.0, C_GRAY, ec=C_ACCENT, lw=1.6)
text(23, 41.0, "Prometheus Operator", size=11, weight="bold")
# Prometheus (중단 전폭)
box(8, 29.5, 30, 6.0, C_GREEN, ec=C_ACCENT, lw=1.6)
text(23, 32.5, "Prometheus (StatefulSet)", size=10.5, weight="bold")
# AM + Grafana (하단 2열)
box(8, 12, 14, 6.5, C_BROWN)
text(15, 15.9, "Alertmanager", size=9.8, weight="bold")
text(15, 13.6, "(StatefulSet)", size=8, color=C_DIM)
box(24, 12, 14, 6.5, C_GRAY, ec=C_ACCENT, lw=1.4)
text(31, 15.9, "Grafana", size=9.8, weight="bold")
text(31, 13.6, "(Deployment)", size=8, color=C_DIM)

# ================= 커스텀 리소스 =================
box(48, 32, 21, 15, C_GRAY, ec=C_ACCENT, lw=1.6)
text(58.5, 43.6, "커스텀 리소스", size=11, weight="bold")
box(50, 37.5, 17, 3.8, "#1d2b24")
text(58.5, 39.4, "ServiceMonitor", size=9.5, weight="bold")
box(50, 32.8, 17, 3.8, "#1d2b24")
text(58.5, 34.7, "PodMonitor", size=9.5, weight="bold")

# ================= kube-state-metrics =================
box(74, 32, 20, 15, C_GRAY)
text(84, 43.6, "Deployment", size=9.5, color=C_DIM, weight="bold")
box(76, 35, 16, 6.0, "#1b232a")
text(84, 38.0, "kube-state-metrics", size=9.3, weight="bold")

# ================= DaemonSet (모든 노드) =================
box(48, 8, 46, 20, C_GREEN)
text(71, 25.2, "DaemonSet (모든 노드)", size=11, weight="bold")
box(52, 12, 18, 9, "#1d2b24", ec=C_ACCENT, lw=1.4)
text(61, 17.5, "node-exporter", size=10, weight="bold")
text(61, 14.5, "노드 메트릭", size=8, color=C_DIM)
box(74, 12, 18, 9, "#1d2b24", ec=C_ACCENT, lw=1.4)
text(83, 17.5, "Alloy", size=11, weight="bold", color=C_ACCENT)
text(83, 14.5, "로그·프로파일 수집", size=8, color=C_DIM)

# ---- arrows ----
# Operator -> SM/PM (watch) : 같은 상단 높이에서 우측으로, Prometheus 위를 지나지 않음
arrow(38, 41.5, 50, 39.4, color=C_ORANGE, lw=1.8, rad=-0.05)
arrow(38, 40.5, 50, 34.7, color=C_ORANGE, lw=1.8, rad=0.05)
text(44, 43.0, "watch", size=8.2, color=C_ORANGE, weight="bold")
# Operator -> Prometheus (설정 생성)
arrow(23, 38, 23, 35.5, color=C_ACCENT, lw=2.0)
text(30.5, 36.7, "설정 생성", size=8, color=C_ACCENT, weight="bold")
# SM/PM -> Prometheus (스크레이프 대상 정의)
arrow(50, 38.0, 38, 33.5, color=C_VIOLET, lw=1.7, rad=0.12)
arrow(50, 33.8, 38, 32.0, color=C_VIOLET, lw=1.7, rad=0.06)
text(44, 30.3, "스크레이프\n대상 정의", size=7.8, color=C_VIOLET, weight="bold")
# node-exporter, alloy, ksm -> Prometheus (메트릭)
arrow(61, 21, 39, 30.5, color=C_DIM, lw=1.4, rad=0.14)
arrow(74, 16.5, 38, 30.0, color=C_DIM, lw=1.4, rad=0.2)
arrow(76, 36.5, 38, 32.5, color=C_DIM, lw=1.4, rad=0.1)
text(50, 24.5, "메트릭 → Prometheus", size=8, color=C_DIM, weight="bold")
# Prometheus -> AM (rule), Grafana
arrow(18, 29.5, 15, 18.5, color=C_ORANGE, lw=1.5, rad=0.08)
text(9.5, 24, "rule\n평가", size=7.6, color=C_ORANGE, weight="bold")
arrow(28, 29.5, 31, 18.5, color=C_DIM, lw=1.4, rad=-0.08)
text(37, 24, "조회", size=7.6, color=C_DIM, weight="bold")

# bottom
text(50, 1.7, "selector 라벨이 CR ↔ Prometheus 매칭의 경계선 · Operator가 CRD를 실제 StatefulSet·설정으로 조정하는 것이 kube-prometheus-stack의 핵심",
     size=9.2, color=C_ACCENT, weight="bold")

# 모든 엣지 유형이 인라인 라벨(watch·설정 생성·스크레이프 대상 정의·메트릭·rule·조회)로 표기돼 별도 범례 생략

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "readme-k8s-topology.png")
