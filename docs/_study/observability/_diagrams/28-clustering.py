"""CH28 Alloy Cluster — gossip + 컨시스턴트 해싱 타깃 분배 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_PURPLE)

fig, ax = new_fig(w=14, h=8.6, ymax=56)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 53.0, "Alloy Cluster — gossip + 컨시스턴트 해싱 타깃 분배", size=18, weight="bold")
text(50, 50.0, "StatefulSet 3 replica가 gossip으로 서로 발견 · 스크레이프 타깃을 자동 분배 · 장애 시 재조정",
     size=11, color=C_DIM)

# left: discovery targets
box(3, 20, 20, 14, C_BLUE)
text(13, 30.6, "discovery.kubernetes", size=11, weight="bold")
text(13, 27.8, "타깃 N개", size=10, color=C_DIM)
text(13, 24.0, "전체 목록을 모든\n레플리카에 동일 전달", size=8.3, color=C_ACCENT, style="italic")

# center: cluster box with 3 replicas
box(30, 10, 40, 34, C_GRAY, ec=C_ACCENT, lw=2.0)
text(50, 41.2, "Alloy Cluster (StatefulSet, 3 replica)", size=11.5, weight="bold", color=C_ACCENT)

reps = [
    (36, 30, "alloy-0"),
    (56, 30, "alloy-1"),
    (46, 15, "alloy-2"),
]
rw, rh = 13, 6.4
for x, y, name in reps:
    box(x, y, rw, rh, C_GREEN)
    text(x + rw / 2, y + rh / 2, name, size=11, weight="bold")

# gossip edges (bidirectional) — drawn only in gaps between boxes
gossip = [
    (49, 33.2, 56, 33.2),      # alloy-0 ↔ alloy-1 (horizontal gap)
    (43, 30.0, 49, 22.4),      # alloy-0 ↔ alloy-2
    (61, 30.0, 55, 22.4),      # alloy-1 ↔ alloy-2
]
for x1, y1, x2, y2 in gossip:
    arrow(x1, y1, x2, y2, color=C_ORANGE, lw=1.8, style="<|-|>")
text(52.5, 35.2, "gossip", size=8.8, color=C_ORANGE, weight="bold")

# discovery -> cluster
arrow(23, 27, 30, 27, color=C_ACCENT, lw=2.2)
text(26.5, 30.2, "컨시스턴트\n해싱 분배", size=8, color=C_ACCENT, weight="bold")

# right: backends
box(77, 20, 20, 14, C_BROWN)
text(87, 30.6, "Mimir / Loki / Tempo", size=10, weight="bold")
text(87, 27.4, "각 레플리카가", size=8.5, color=C_DIM)
text(87, 24.6, "자기 몫만 remote_write", size=8.5, color=C_DIM)

arrow(70, 27, 77, 27, color=C_ACCENT, lw=2.2)

# bottom
text(50, 5.6, "특정 인스턴스가 죽으면 나머지가 그 타깃을 흡수해 재조정 — 레플리카 수로 스크레이프 부하를 수평 확장",
     size=10, color=C_ACCENT, weight="bold")
text(50, 2.8, "DaemonSet 배치는 '이 노드는 이 인스턴스가 담당'이 곧 분배이므로 clustering이 필요 없음",
     size=9, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "28-clustering.png")
