"""CH25 Pyroscope 수집 경로 — push / pull / eBPF (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "Pyroscope 수집 경로 — push · pull · eBPF", size=20, weight="bold")
text(50, 56.6, "기본은 SDK push, Alloy가 pprof 엔드포인트 pull과 eBPF 무계측 수집 경로도 담당",
     size=12, color=C_DIM)

# ================= push 경로 =================
box(3, 40, 44, 13, C_GRAY, ec=C_GREEN, lw=1.6)
text(9, 50.6, "push 경로 (기본)", size=12, weight="bold", color="#8fce9a", ha="left")
box(6, 42, 20, 6.2, C_GREEN)
text(16, 46.0, "언어별 SDK", size=11, weight="bold")
text(16, 43.8, "Go / Java / Python / …", size=8.3, color=C_DIM)

# ================= pull 경로 =================
box(3, 22, 44, 15, C_GRAY, ec=C_BLUE.replace("#2e4a5a", "#5a8aa8"), lw=1.6)
text(9, 34.6, "pull 경로 (스크레이핑)", size=12, weight="bold", color="#7fb8d8", ha="left")
box(6, 27.5, 18, 5.6, C_BLUE)
text(15, 31.1, "/debug/pprof", size=10.5, weight="bold")
text(15, 29.0, "표준 pprof 엔드포인트", size=8, color=C_DIM)

# ================= eBPF 경로 =================
box(3, 8, 44, 12, C_GRAY, ec=C_VIOLET, lw=1.6)
text(9, 17.6, "eBPF 경로 (무계측)", size=12, weight="bold", color=C_VIOLET, ha="left")
box(6, 9.6, 18, 5.6, "#4a3d63", ec="#7a68a0")
text(15, 13.2, "pyroscope.ebpf", size=10.5, weight="bold", color="#e7dcff")
text(15, 11.1, "언어 SDK 없이 프로세스 프로파일", size=7.6, color="#cbb8e6")

# ================= Alloy (pull+ebpf 경유) =================
box(53, 11, 18, 24, C_BROWN, ec=C_ORANGE, lw=1.8)
text(62, 31.8, "Alloy", size=14, weight="bold", color=C_ORANGE)
text(62, 22.5, "pyroscope.scrape\n(pull 수집)", size=9, color="#f0c99a")
text(62, 16.0, "pyroscope.write\n(전달)", size=9, color="#f0c99a")

arrow(24, 30.3, 53, 27, color="#7fb8d8", lw=2.2)
text(40, 31.6, "pyroscope.scrape", size=8.5, color="#7fb8d8", weight="bold")
arrow(24, 12.4, 53, 16, color=C_VIOLET, lw=2.2)
text(40, 12.0, "무계측 수집", size=8.5, color=C_VIOLET, weight="bold")

# ================= distributor =================
box(78, 33, 19, 14, C_GRAY, ec=C_ACCENT, lw=2.0)
text(87.5, 42.4, "Pyroscope", size=13, weight="bold", color=C_ACCENT)
text(87.5, 39.6, "distributor", size=12, weight="bold", color=C_ACCENT)
text(87.5, 36.4, "세 경로의 프로파일을\n하나의 수신 지점으로", size=8.5, color=C_DIM)

# push SDK -> distributor (한 줄로)
arrow(26, 45.1, 78, 43.5, color=C_GREEN, lw=2.4)
text(50, 47.0, "주기적 HTTP push (10~15초)", size=9, color="#8fce9a", weight="bold")
# Alloy -> distributor
arrow(71, 24, 78, 35, color=C_ORANGE, lw=2.4)
text(77.5, 29.0, "pyroscope.write", size=8.5, color=C_ORANGE, weight="bold", ha="right")

# bottom
text(50, 4.6, "이미 pprof 엔드포인트를 노출 중이면 SDK 없이 Alloy만으로도 수집 파이프라인 구성 가능",
     size=10, color=C_ACCENT, weight="bold")
text(50, 2.2, "Loki의 로그 push와 같은 패턴 — Prometheus의 pull 모델과 대비된다",
     size=9, color=C_DIM, style="italic")

leg = [
    Line2D([0], [0], color=C_GREEN, lw=2.5, label="push (SDK → distributor)"),
    Line2D([0], [0], color="#7fb8d8", lw=2.5, label="pull (scrape → Alloy)"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, label="eBPF 무계측 → Alloy"),
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="Alloy → distributor"),
]
ax.legend(handles=leg, loc="lower right", bbox_to_anchor=(0.995, 0.01),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "25-push-pull-collection.png")
