"""CH26 SDK vs eBPF 선택 결정 트리 (matplotlib → PNG)."""
from matplotlib.patches import Polygon
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)


def diamond(cx, cy, w, h, fc, ec=C_ORANGE, lw=1.8):
    pts = [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=fc, edgecolor=ec,
                         linewidth=lw, zorder=3))


# ---- Title ----
text(50, 59.4, "SDK vs eBPF — 계층적 조합 선택 기준", size=20, weight="bold")
text(50, 56.6, "eBPF로 전역 기본 커버리지 확보  →  세밀한 태깅·메모리/락 프로파일이 필요한 서비스에만 SDK 추가",
     size=12, color=C_DIM)

# ---- Q1 ----
diamond(30, 46, 34, 14, C_BROWN)
text(30, 46, "모든 워크로드에 대한\n기본 CPU 가시성이\n필요한가", size=10, weight="bold")

# ---- eBPF (Q1 예) ----
box(60, 41, 30, 10, "#4a3d63", ec="#7a68a0", lw=1.8)
text(75, 47.4, "eBPF (DaemonSet)", size=12, weight="bold", color="#e7dcff")
text(75, 43.8, "전역 기본 커버리지", size=9.5, color="#cbb8e6")

arrow(47, 46, 60, 46, color=C_GREEN, lw=2.4)
text(53.5, 47.8, "예", size=10, color=C_GREEN, weight="bold")

# ---- Q2 ----
diamond(30, 25, 34, 14, C_BROWN)
text(30, 25, "메모리/lock 프로파일이나\n요청 단위 태깅이\n필요한가", size=10, weight="bold")

# Q1 아니오 -> Q2
arrow(30, 39, 30, 32, color=C_DIM, lw=2.2)
text(33.5, 35.5, "아니오", size=9.5, color=C_DIM, weight="bold", ha="left")
# eBPF -> Q2 (계층 조합)
arrow(75, 41, 47, 27, color="#b9a3e0", lw=2.0, ls=(0, (5, 3)))
text(62, 36.0, "그 위에 추가 판단", size=8.5, color="#b9a3e0", style="italic")

# ---- SDK 추가 (Q2 예) ----
box(60, 20, 30, 9, C_GREEN, ec=C_ACCENT, lw=1.8)
text(75, 25.6, "언어별 SDK 추가", size=12, weight="bold")
text(75, 22.4, "요청 단위 태깅 · 풍부한 타입", size=9, color=C_DIM)

arrow(47, 25, 60, 25, color=C_GREEN, lw=2.4)
text(53.5, 26.8, "예", size=10, color=C_GREEN, weight="bold")

# ---- eBPF만으로 충분 (Q2 아니오) ----
box(15, 8, 30, 8, C_GRAY, ec=C_EDGE, lw=1.4)
text(30, 12.8, "eBPF만으로 충분", size=11, weight="bold")
text(30, 10.0, "추가 계측 불필요", size=8.5, color=C_DIM)

arrow(30, 18, 30, 16, color=C_DIM, lw=2.2)
text(33.5, 17.4, "아니오", size=9.5, color=C_DIM, weight="bold", ha="left")

# ---- eBPF + SDK 조합 (최종) ----
box(60, 8, 30, 8, C_GRAY, ec=C_ACCENT, lw=2.0)
text(75, 12.8, "eBPF + SDK 조합", size=11.5, weight="bold", color=C_ACCENT)
text(75, 10.0, "전역 커버리지 + 핵심 서비스 심층 계측", size=8.3, color=C_DIM)

arrow(75, 20, 75, 16, color=C_ACCENT, lw=2.2)

# bottom
text(50, 4.2, "두 방식은 배타적 선택이 아니라 계층적 조합 — eBPF 기본선 위에 필요한 서비스만 SDK를 얹는다",
     size=10, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "26-sdk-vs-ebpf-decision.png")
