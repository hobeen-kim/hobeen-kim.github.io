"""CH05 §2 핵심 컴포넌트 — 단일 바이너리 내부 서브시스템 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_PURPLE, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "Prometheus 핵심 컴포넌트", size=20, weight="bold")
text(50, 56.6, "단일 프로세스 안에서 Retrieval · TSDB · PromQL 엔진 · Rule Manager 네 서브시스템이 협업",
     size=12, color=C_DIM)

# ================= left: external sources =================
box(2, 42, 22, 8, C_GRAY)
text(13, 47.4, "Service Discovery", size=11, weight="bold")
text(13, 44.6, "동적 타깃 목록 공급", size=8.5, color=C_DIM)

box(2, 29, 22, 8, C_GRAY)
text(13, 34.4, "스크레이프 타깃", size=11, weight="bold")
text(13, 31.6, "/metrics 노출", size=8.5, color=C_DIM)

box(2, 12, 22, 8, C_GRAY)
text(13, 17.4, "사용자 / Grafana", size=11, weight="bold")
text(13, 14.6, "PromQL 조회", size=8.5, color=C_DIM)

# ================= center: Prometheus single process =================
box(28, 8, 47, 44, "#161d24", ec=C_ACCENT, lw=2.0)
text(51.5, 49.3, "Prometheus 서버 (단일 프로세스 · 하나의 Go 런타임)", size=12.5,
     weight="bold", color=C_ACCENT)

box(31, 33, 18, 9, C_BLUE)
text(40, 38.9, "Retrieval", size=12, weight="bold")
text(40, 36.4, "scrape manager · relabeling", size=8, color="#d4dae0")

box(53, 33, 19, 9, C_BROWN)
text(62.5, 38.9, "TSDB", size=12, weight="bold")
text(62.5, 36.4, "WAL + 블록 스토리지", size=8, color="#e0d4c8")

box(31, 14, 18, 9, C_GREEN)
text(40, 19.9, "HTTP Server", size=12, weight="bold")
text(40, 17.4, "PromQL 엔진 · REST API", size=8, color="#d4e0d4")

box(53, 14, 19, 9, C_PURPLE)
text(62.5, 19.9, "Rule Manager", size=12, weight="bold")
text(62.5, 17.4, "recording · alerting", size=8, color="#ddd0ee")

# ================= right: Alertmanager =================
box(80, 14, 18, 9, C_GRAY, ec=C_ORANGE, lw=1.8)
text(89, 19.9, "Alertmanager", size=12, weight="bold", color=C_ORANGE)
text(89, 17.4, "분리된 별도 바이너리", size=8, color=C_DIM)

# ---- arrows ----
arrow(24, 45.5, 31, 39.5, color=C_ACCENT, lw=2.0)
text(27.5, 44.0, "타깃 목록", size=8, color=C_ACCENT)
arrow(24, 32.5, 31, 36.0, color=C_ORANGE, lw=2.2)
text(26.5, 35.4, "pull", size=8.5, color=C_ORANGE, weight="bold")
arrow(24, 15.5, 31, 17.5, color=C_VIOLET, lw=2.0)
text(26.5, 13.6, "PromQL", size=8, color=C_VIOLET)

arrow(49, 37.5, 53, 37.5, color=C_ACCENT, lw=2.2)
text(51, 39.6, "append", size=8, color=C_ACCENT, weight="bold")
arrow(44, 23, 59, 33, color=C_GREEN, lw=2.0)
text(48.5, 29.0, "질의", size=8.5, color="#7fbf87")
arrow(62.5, 23, 62.5, 33, color=C_PURPLE, lw=2.0)
text(70.5, 28, "PromQL 평가", size=8, color=C_VIOLET)
arrow(72, 18.5, 80, 18.5, color=C_ORANGE, lw=2.2)
text(76, 20.6, "알림 전송", size=8, color=C_ORANGE, weight="bold")

# bottom
text(50, 4.6, "네 컴포넌트가 하나의 프로세스에서 협업 — Rule Manager 자신도 PromQL 엔진의 소비자다",
     size=10.5, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "05-core-components.png")
