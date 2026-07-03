"""CH26 eBPF 무계측 프로파일링 — 노드 단위 수집 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "eBPF 무계측 프로파일링 — 노드 단위 수집", size=20, weight="bold")
text(50, 56.6, "커널 eBPF가 노드의 모든 프로세스 콜 스택을 직접 캡처  →  Alloy DaemonSet이 한 번에 수집",
     size=12, color=C_DIM)

# ================= 쿠버네티스 노드 =================
box(4, 12, 70, 41, C_GRAY, ec=C_EDGE, lw=1.6)
text(9, 50.4, "쿠버네티스 노드", size=13, weight="bold", ha="left")

# processes (top row)
procs = [
    (16, "Go 서비스", C_BLUE),
    (32, "Java 서비스", C_BROWN),
    (48, "Python 서비스", C_GREEN),
    (65, "서드파티 바이너리", "#4a3d63"),
]
for x, t, c in procs:
    box(x - 7.5, 42, 15, 6.2, c)
    text(x, 45.6, t, size=9.5, weight="bold")
    if t == "서드파티 바이너리":
        text(x, 43.4, "소스 없음", size=8, color=C_DIM)
    else:
        text(x, 43.4, "애플리케이션", size=8, color=C_DIM)

# kernel space box
box(9, 28, 60, 8, C_BROWN, ec=C_ORANGE, lw=1.6)
text(14, 34.4, "커널 공간", size=11, weight="bold", ha="left", color="#f0c99a")
box(28, 29, 22, 4.6, "#241d1a")
text(39, 31.3, "eBPF 프로그램 (perf_event 기반 샘플러)", size=9.5, color=C_TEXT)

# processes -.-> eBPF (커널이 스택 직접 캡처)
for x, t, c in procs:
    arrow(x, 42, 39, 36, color=C_VIOLET, lw=1.6, ls=(0, (4, 3)))
text(56, 39.4, "커널이 스택을 직접 캡처", size=8.5, color=C_VIOLET, weight="bold")

# Alloy
box(24, 16, 30, 7.5, C_GREEN, ec=C_ACCENT, lw=1.8)
text(39, 21.0, "Alloy", size=13, weight="bold", color=C_ACCENT)
text(39, 18.4, "pyroscope.ebpf · DaemonSet", size=9, color=C_DIM)

arrow(39, 28, 39, 23.5, color=C_ORANGE, lw=2.4)
text(43.5, 25.6, "eBPF 이벤트", size=8.5, color=C_ORANGE, weight="bold", ha="left")

# ================= Pyroscope (노드 밖) =================
box(80, 26, 17, 14, C_GRAY, ec=C_ACCENT, lw=2.0)
text(88.5, 35.4, "Pyroscope", size=13, weight="bold", color=C_ACCENT)
text(88.5, 31.6, "노드별 수집 결과를\n중앙 집계", size=9, color=C_DIM)

arrow(54, 19.8, 88.5, 26, color=C_ORANGE, lw=2.4)
text(72, 25.0, "push", size=9, color=C_ORANGE, weight="bold")

# bottom
text(50, 7.4, "언어 무관(language-agnostic) · 시스템 전체(system-wide) — 코드 한 줄, 소스 없는 바이너리까지 프로파일",
     size=10, color=C_ACCENT, weight="bold")
text(50, 4.4, "호스트에서 실행되는 모든 컨테이너의 프로파일을 노드 단위 DaemonSet으로 한 번에 수집",
     size=9, color=C_DIM, style="italic")

leg = [
    Line2D([0], [0], color=C_VIOLET, lw=2.5, ls="--", label="프로세스 → 커널 스택 캡처"),
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="eBPF 이벤트 → Alloy → Pyroscope"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.01),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "26-ebpf-node.png")
