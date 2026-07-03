"""CH42 Grafana Alerting — 통합 알림 구조 다이어그램 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "Grafana Alerting — 통합 알림 파이프라인", size=20, weight="bold")
text(50, 56.6, "룰 평가 (Grafana-managed / datasource-managed)  →  내장 Alertmanager  →  contact point  →  IRM",
     size=12, color=C_DIM)

# ================= left: rule sources =================
box(2, 32, 28, 20, C_BLUE)
text(16, 49.6, "Grafana-managed rule", size=12.5, weight="bold")
text(16, 47.4, "Grafana 서버가 직접 평가", size=9, color=C_DIM)
for i, (t, d) in enumerate([
    ("멀티 데이터소스 질의", "Prometheus · Loki · SQL · CloudWatch …"),
    ("expression 파이프라인", "reduce → math → threshold 조합"),
    ("데이터소스 간 조건 결합", "메트릭 AND 로그 같은 복합 조건"),
]):
    yy = 44 - i * 4.2
    box(4, yy - 1.7, 24, 3.4, "#1b232a")
    text(16, yy + 0.5, t, size=9.5)
    text(16, yy - 1.0, d, size=7.8, color=C_DIM)

box(2, 10, 28, 19, C_GREEN)
text(16, 26.6, "datasource-managed rule", size=12.5, weight="bold")
text(16, 24.4, "백엔드 ruler에 위임 평가", size=9, color=C_DIM)
for i, (t, d) in enumerate([
    ("Prometheus / Mimir ruler", "PromQL 룰 — 11장과 동일 개념"),
    ("Loki ruler", "LogQL 룰 — 로그 기반 알림"),
    ("대량 룰에 유리", "백엔드와 함께 수평 확장"),
]):
    yy = 21.5 - i * 4.0
    box(4, yy - 1.6, 24, 3.2, "#1d2b24")
    text(16, yy + 0.5, t, size=9.5)
    text(16, yy - 0.9, d, size=7.8, color=C_DIM)

# ================= center: embedded Alertmanager =================
box(38, 14, 28, 38, C_GRAY, ec=C_ACCENT, lw=2.0)
text(52, 49.6, "Grafana 내장 Alertmanager", size=13, weight="bold", color=C_ACCENT)
text(52, 47.4, "Prometheus Alertmanager 코드 임베드", size=9, color=C_DIM)
for i, (t, d) in enumerate([
    ("notification policy 트리", "라벨 매칭 라우팅 — 14장 route 트리와 동일"),
    ("grouping", "같은 장애의 알림 묶음"),
    ("mute timing · silence", "점검 시간대 억제 · 임시 무음"),
    ("외부 Alertmanager 전달", "기존 AM 클러스터로 위임 가능"),
]):
    yy = 43 - i * 6.4
    box(40, yy - 2.5, 24, 5.0, "#1b232a")
    text(52, yy + 0.6, t, size=10)
    text(52, yy - 1.3, d, size=8, color=C_DIM)

arrow(30, 42, 38, 40, color=C_ORANGE, lw=2.2)
arrow(30, 20, 38, 26, color=C_ORANGE, lw=2.2)
text(34, 43.8, "firing 알림", size=8.5, color=C_ORANGE, weight="bold")

# ================= right: contact points + IRM =================
box(74, 34, 24, 18, C_BROWN)
text(86, 49.6, "contact point", size=13, weight="bold")
for i, t in enumerate(["Slack · Teams · Email", "webhook · PagerDuty", "Grafana IRM / OnCall"]):
    yy = 45.5 - i * 3.6
    box(76, yy - 1.5, 20, 3.0, "#241d1a")
    text(86, yy, t, size=9.5)

box(74, 10, 24, 20, C_VIOLET.replace("#b9a3e0", "#4a3d63") if False else "#4a3d63", ec="#7a68a0", lw=1.6)
text(86, 27.6, "Grafana IRM", size=13, weight="bold", color="#e7dcff")
text(86, 25.4, "알림 이후의 대응 체계 (Cloud)", size=9, color=C_DIM)
for i, (t, d) in enumerate([
    ("온콜 스케줄", "로테이션 · 캘린더 연동"),
    ("에스컬레이션 체인", "미응답 시 다음 담당자 호출"),
    ("인시던트 관리", "선언 · 타임라인 · 회고"),
]):
    yy = 22 - i * 4.0
    box(76, yy - 1.6, 20, 3.2, "#3a3050")
    text(86, yy + 0.5, t, size=9.5, color="#e7dcff")
    text(86, yy - 0.9, d, size=7.8, color="#cbb8e6")

arrow(66, 42, 74, 43, color=C_ACCENT, lw=2.2)
arrow(86, 34, 86, 30, color="#b9a3e0", lw=2.0)
text(90.5, 32, "escalate", size=8, color="#b9a3e0")

# bottom
text(50, 6.2, "Prometheus 스택 중심 조직 → Alertmanager 직접 운영(13~15장)  ·  Grafana 중심 멀티 데이터소스 → Grafana Alerting",
     size=9.5, color="#d4dae0")
text(50, 3.2, "두 시스템 혼용 시 같은 장애에 알림이 두 번 온다 — 알림 소유권을 한쪽으로 정한다",
     size=10, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="룰 평가 → firing"),
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="라우팅 → 알림 채널"),
    Line2D([0], [0], color="#b9a3e0", lw=2.5, label="IRM 에스컬레이션"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.005),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "42-grafana-alerting.png")
