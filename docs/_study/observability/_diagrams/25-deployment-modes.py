"""CH25 Pyroscope 배포 모드 — monolithic / microservices (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=8.6, ymax=58)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 55.0, "Pyroscope 배포 모드 — monolithic / microservices", size=20, weight="bold")
text(50, 51.8, "소규모는 단일 프로세스로 시작, 트래픽이 늘면 컴포넌트별 독립 스케일로 전환",
     size=12, color=C_DIM)

# ================= monolithic =================
box(4, 12, 34, 33, C_GRAY, ec=C_GREEN, lw=1.8)
text(21, 42.2, "monolithic 모드", size=14, weight="bold", color="#8fce9a")
text(21, 39.6, "소규모 팀 · PoC · 단일 노드", size=9, color=C_DIM, style="italic")

box(8, 18, 26, 17, C_GREEN)
text(21, 31.0, "단일 프로세스", size=13, weight="bold")
text(21, 27.6, "모든 컴포넌트 포함", size=10, color="#d4dae0")
text(21, 23.0, "distributor · ingester\nquerier · compactor …", size=9, color=C_DIM)

text(21, 15.0, "운영 부담↓  ·  일부만 부하 몰려도 전체 스케일", size=8.3, color=C_ORANGE, style="italic")

# ================= transition arrow =================
arrow(38, 28, 50, 28, color=C_ORANGE, lw=2.8)
text(44, 30.6, "트래픽 증가 시", size=9, color=C_ORANGE, weight="bold")
text(44, 25.4, "전환", size=9, color=C_ORANGE, weight="bold")

# ================= microservices =================
box(51, 12, 45, 33, C_GRAY, ec=C_ACCENT, lw=1.8)
text(73.5, 42.2, "microservices 모드", size=14, weight="bold", color=C_ACCENT)
text(73.5, 39.6, "대규모 트래픽 · 독립 스케일링 · 장애 격리", size=9, color=C_DIM, style="italic")

cells = [
    (60.5, 30.5, "distributor", C_BLUE),
    (86.0, 30.5, "ingester", C_BROWN),
    (60.5, 20.0, "querier", C_GREEN),
    (86.0, 20.0, "compactor", "#4a3d63"),
]
for x, y, t, c in cells:
    box(x - 8, y - 4, 16, 8, c)
    text(x, y + 1.4, t, size=10.5, weight="bold")
    text(x, y - 1.8, "N개 복제", size=8.5, color=C_DIM)

text(73.5, 15.0, "컴포넌트별 독립 수평 확장  ·  운영 복잡도↑", size=8.3, color=C_ACCENT, style="italic")

# bottom
text(50, 7.0, "Kubernetes에서는 보통 monolithic으로 시작해 트래픽이 늘면 microservices로 전환",
     size=10.5, color=C_ACCENT, weight="bold")
text(50, 4.0, "Mimir·Loki와 동일한 두 배포 모드 선택지 — 규모와 운영 여력에 맞춰 결정",
     size=9, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "25-deployment-modes.png")
