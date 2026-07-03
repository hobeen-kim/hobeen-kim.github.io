"""CH03 수집 전략 결정 트리 — Exporter / OTel Collector / Alloy (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "수집 전략 결정 트리 — 언제 무엇을 쓰나", size=20, weight="bold")
text(50, 56.6, "핵심 질문은 \"저장 백엔드\"가 아니라 \"수집을 무엇으로 하느냐\"다", size=12, color=C_DIM)

# ---- 결정 노드 1: 수집 대상은? (다이아몬드 느낌 박스) ----
box(38, 47, 24, 7, C_GRAY, ec=C_ACCENT, lw=1.8, r=0.06)
text(50, 50.5, "수집 대상은?", size=13, weight="bold", color=C_ACCENT)

# ---- Exporter 경로 (왼쪽) ----
box(6, 33, 26, 8.5, C_BROWN)
text(19, 38.2, "Exporter", size=12.5, weight="bold")
text(19, 35.0, "node-exporter · mysqld-exporter …", size=8.2, color=C_DIM)
arrow(38, 49, 19, 41.5, color=C_ORANGE, lw=2.2, rad=0.1)
text(24, 46.5, "서드파티 / 레거시\n계측 불가", size=8.8, color=C_ORANGE, weight="bold")

box(6, 19, 26, 7.5, C_GRAY)
text(19, 22.7, "Prometheus가 스크레이프", size=10, weight="bold")
text(19, 20.3, "pull 모델", size=8.2, color=C_DIM, style="italic")
arrow(19, 33, 19, 26.5, color=C_ACCENT, lw=2.0)

# ---- 결정 노드 2: 벤더 중립성? (오른쪽) ----
box(64, 44, 30, 8, C_GRAY, ec=C_ACCENT, lw=1.8, r=0.06)
text(79, 49.0, "벤더 중립성이", size=11.5, weight="bold", color=C_ACCENT)
text(79, 46.2, "최우선인가?", size=11.5, weight="bold", color=C_ACCENT)
arrow(62, 49, 74, 49.5, color=C_ORANGE, lw=2.2)
text(68, 52.2, "직접 계측 가능한\n애플리케이션", size=8.8, color=C_ORANGE, weight="bold")

# OTel Collector (예)
box(52, 28, 24, 8.5, C_BLUE)
text(64, 33.2, "OpenTelemetry", size=11, weight="bold")
text(64, 30.4, "Collector", size=11, weight="bold")
arrow(74, 44, 65, 36.5, color=C_ACCENT, lw=2.0, rad=0.1)
text(65.5, 41.0, "예\n(멀티 벤더 전환 대비)", size=8.5, color=C_ACCENT, weight="bold")

box(52, 14, 24, 7.5, C_GRAY)
text(64, 17.7, "여러 벤더 백엔드로 라우팅", size=9.2, weight="bold")
arrow(64, 28, 64, 21.5, color=C_ACCENT, lw=2.0)

# Alloy (아니오)
box(80, 28, 17, 8.5, C_GREEN)
text(88.5, 33.2, "Alloy", size=12, weight="bold")
text(88.5, 30.2, "4대 신호\n통합 수집", size=8.2, color=C_DIM)
arrow(88, 44, 88.5, 36.5, color=C_ACCENT, lw=2.0)
text(93.5, 40.5, "아니오\n(Grafana\n스택 고정)", size=8.2, color=C_ACCENT, weight="bold")

box(80, 14, 17, 7.5, C_GRAY)
text(88.5, 18.7, "Mimir/Loki/", size=8.8, weight="bold")
text(88.5, 16.0, "Tempo/Pyroscope", size=8.8, weight="bold")
arrow(88.5, 28, 88.5, 21.5, color=C_ACCENT, lw=2.0)

# bottom
text(50, 8.0, "세 전략은 배타적이지 않다 — exporter를 Alloy가 스크레이프하면서 앱은 OTLP로 push하는 혼합 구성이 흔하다",
     size=10, color=C_DIM, style="italic")
text(50, 4.6, "Alloy는 OTLP 리시버를 내장해 OpenTelemetry Collector 역할까지 대신할 수 있다",
     size=10, color=C_ACCENT, weight="bold")

save(fig, "03-collection-decision.png")
