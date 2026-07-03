"""CH37 Alloy DaemonSet — 노드별 로그·프로파일 수집 다이어그램 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "Alloy DaemonSet — 노드별 로그·프로파일 능동 수집", size=20, weight="bold")
text(50, 56.6, "모든 노드에 배치된 Alloy가 컨테이너 로그·eBPF 프로파일을 걷어 Loki·Pyroscope로 push",
     size=12, color=C_DIM)

# ================= node boxes (좌측, 수직 스택) =================
def node(y, label):
    box(3, y, 42, 18, C_GRAY)
    text(24, y + 15.2, label, size=12.5, weight="bold")
    # app pod
    box(6, y + 4.5, 15, 8, "#1b232a")
    text(13.5, y + 9.5, "애플리케이션 Pod", size=9.5)
    text(13.5, y + 6.8, "stdout/stderr · 실행 프로세스", size=7.4, color=C_DIM)
    # alloy
    box(26, y + 2.5, 16, 12, C_GREEN, ec=C_ACCENT, lw=1.8)
    text(34, y + 11.6, "Alloy", size=11.5, weight="bold", color=C_ACCENT)
    text(34, y + 9.4, "(DaemonSet)", size=8, color=C_DIM)
    text(34, y + 6.6, "discovery.kubernetes", size=7.8, color=C_TEXT)
    text(34, y + 4.5, "loki.source · pyroscope.ebpf", size=7.2, color=C_DIM)
    # app -> alloy (로그: 주황, 프로파일: 보라)
    arrow(21, y + 9.5, 26, y + 9.5, color=C_ORANGE, lw=1.7)
    arrow(21, y + 7.0, 26, y + 5.5, color=C_VIOLET, lw=1.7, rad=-0.08)
    text(23.5, y + 10.6, "로그", size=7.2, color=C_ORANGE, weight="bold")
    text(23.5, y + 4.0, "eBPF", size=7.2, color=C_VIOLET, weight="bold")

node(32, "노드 1")
node(9, "노드 2")

# ================= backends (우측) =================
box(72, 33, 24, 15, C_BLUE)
text(84, 44.2, "Loki", size=14, weight="bold")
text(84, 41.0, "로그 저장", size=9.5, color=C_DIM)
text(84, 37.0, "loki.write →\n/loki/api/v1/push", size=8.5, color=C_ACCENT, style="italic")

box(72, 12, 24, 15, C_BROWN)
text(84, 23.2, "Pyroscope", size=14, weight="bold")
text(84, 20.0, "연속 프로파일 저장", size=9.5, color=C_DIM)
text(84, 16.0, "pyroscope.write →\n:4040", size=8.5, color=C_ACCENT, style="italic")

# alloy -> backends
# node1 alloy (y=32, alloy 상단 y~46.5 center~40) -> Loki / Pyroscope
arrow(45, 43.5, 72, 42, color=C_ORANGE, lw=2.0, rad=-0.04)
arrow(45, 38.5, 72, 21, color=C_VIOLET, lw=2.0, rad=0.06)
# node2 alloy (y=9, center~17) -> Loki / Pyroscope
arrow(45, 20.5, 72, 37, color=C_ORANGE, lw=2.0, rad=-0.06)
arrow(45, 15.5, 72, 17, color=C_VIOLET, lw=2.0, rad=0.03)
text(60, 45.2, "loki.write", size=8.5, color=C_ORANGE, weight="bold")
text(60, 11.0, "pyroscope.write", size=8.5, color=C_VIOLET, weight="bold")

# bottom
text(50, 6.4, "메트릭은 Prometheus가 pull로 스크레이프하지만, 로그·프로파일은 노드마다 능동적으로 수집해 push하는 에이전트가 필요",
     size=10, color=C_TEXT, weight="bold")
text(50, 3.0, "pyroscope.ebpf는 코드 계측 없이 커널 레벨 CPU 프로파일 샘플링 (언어·런타임 무관) · eBPF는 커널 버전·권한 제약 → securityContext 필요",
     size=9, color=C_DIM, style="italic")

leg = [
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="컨테이너 로그 경로 (loki.write)"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, label="eBPF 프로파일 경로 (pyroscope.write)"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.10),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "37-alloy-daemonset.png")
