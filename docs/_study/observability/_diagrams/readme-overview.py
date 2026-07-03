"""README 전체 아키텍처 — 신호 수집→저장→시각화 파이프라인 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "전체 아키텍처 — 신호 수집 → 저장 → 시각화", size=20, weight="bold")
text(50, 56.6, "4대 신호가 각 전용 백엔드로 흐르고 Grafana가 하나의 화면에서 상관관계로 엮는다 · 메트릭은 Prometheus→Mimir 2단 구조",
     size=11.5, color=C_DIM)

# ================= 수집 계층 =================
box(2, 6, 24, 47, C_GRAY)
text(14, 50.4, "수집 계층", size=13, weight="bold")
collect = [
    ("node-exporter", "노드 하드웨어"),
    ("kube-state-metrics", "오브젝트 상태"),
    ("cAdvisor", "컨테이너 사용량"),
    ("애플리케이션", "OTel SDK 계측"),
]
for i, (t, d) in enumerate(collect):
    yy = 46 - i * 5.4
    box(4, yy - 2.1, 20, 4.2, "#1b232a")
    text(14, yy + 0.5, t, size=9.8, weight="bold")
    text(14, yy - 1.2, d, size=7.8, color=C_DIM)
# Alloy
box(4, 10.5, 20, 8.5, C_GREEN, ec=C_ACCENT, lw=1.8)
text(14, 15.6, "Alloy /\nOTel Collector", size=10.5, weight="bold", color=C_ACCENT)
text(14, 12.0, "수집·라우팅 에이전트", size=8, color=C_DIM)

# ================= 저장/백엔드 계층 =================
box(35, 6, 30, 47, C_BLUE)
text(50, 50.4, "저장 / 백엔드 계층", size=13, weight="bold")
backends = [
    ("Prometheus", "메트릭 스크레이핑·TSDB", C_GREEN),
    ("Mimir", "메트릭 장기 저장", C_GREEN),
    ("Loki", "로그", C_BROWN),
    ("Tempo", "트레이스", C_BROWN),
    ("Pyroscope", "프로파일", C_BROWN),
]
for i, (t, d, fc) in enumerate(backends):
    yy = 46 - i * 7.2
    box(38, yy - 2.7, 24, 5.4, fc)
    text(50, yy + 0.6, t, size=10.5, weight="bold")
    text(50, yy - 1.5, d, size=8, color=C_DIM)

# ================= 알림 =================
box(72, 33, 24, 12, C_BROWN)
text(84, 41.4, "알림", size=12.5, weight="bold")
box(74, 34.5, 20, 5.0, "#241d1a")
text(84, 37.0, "Alertmanager", size=10.5, weight="bold")

# ================= 시각화 =================
box(72, 14, 24, 14, C_GRAY, ec=C_ACCENT, lw=2.0)
text(84, 24.4, "시각화", size=12.5, weight="bold")
box(74, 16, 20, 6.0, "#1d2b24", ec=C_ACCENT, lw=1.6)
text(84, 19.6, "Grafana", size=12, weight="bold", color=C_ACCENT)
text(84, 17.2, "4대 신호 상관관계", size=8, color=C_DIM)

# ---- arrows: 수집 -> 백엔드 ----
# node/ksm/cad -> prometheus (metric pull)
arrow(24, 44, 38, 44.5, color=C_ORANGE, lw=1.7, rad=-0.06)
arrow(24, 38.6, 38, 44.0, color=C_ORANGE, lw=1.7, rad=-0.03)
arrow(24, 33.2, 38, 43.5, color=C_ORANGE, lw=1.7, rad=0.03)
# app -> alloy
arrow(14, 27.6, 14, 19.0, color=C_ACCENT, lw=1.7)
text(20.5, 23.5, "OTLP", size=7.8, color=C_ACCENT, weight="bold")
# alloy -> backends (4 신호)
arrow(24, 15.5, 38, 43, color=C_ACCENT, lw=1.6, rad=-0.16)
arrow(24, 15.0, 38, 24.5, color=C_ACCENT, lw=1.6, rad=-0.08)
arrow(24, 14.0, 38, 17.5, color=C_ACCENT, lw=1.6, rad=0.05)
text(30, 27, "Alloy →\n각 백엔드", size=7.8, color=C_ACCENT, weight="bold")

# prometheus -> mimir (remote_write)
arrow(50, 43.3, 50, 41.5, color=C_VIOLET, lw=2.0)
text(63.5, 42.4, "remote_write", size=7.8, color=C_VIOLET, weight="bold")
# prometheus -> AM
arrow(62, 42, 72, 39.5, color=C_ORANGE, lw=1.7, rad=-0.08)
text(67, 44.0, "rule 평가", size=7.8, color=C_ORANGE, weight="bold")

# backends -> grafana
for yy in (43.3, 36.1, 28.9, 21.7, 14.5):
    arrow(62, yy, 74, 19.5, color=C_DIM, lw=1.2, rad=0.12)
# AM -> grafana
arrow(84, 33, 84, 28, color=C_DIM, lw=1.3)
text(50, 9.5, "모든 백엔드가 Grafana 데이터소스로 연결된다", size=8.5, color=C_DIM, ha="center")

# bottom
text(50, 3.4, "메트릭 Prometheus→Mimir 2단 저장 · 로그 Loki · 트레이스 Tempo · 프로파일 Pyroscope · 수집은 Alloy/OTel로 통일 · 시각화·상관관계는 Grafana",
     size=9.3, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="메트릭 pull / rule 평가"),
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="Alloy 수집·라우팅 (OTLP)"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, label="remote_write (장기 저장)"),
    Line2D([0], [0], color=C_DIM, lw=2.5, label="데이터소스 조회"),
]
ax.legend(handles=leg, loc="upper left", bbox_to_anchor=(0.685, 0.86),
          fontsize=8, framealpha=0.0, labelcolor=C_DIM, ncol=1)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "readme-overview.png")
