"""CH08 USE 방법론 — 리소스 기반 계측 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_TEXT, C_DIM, C_ACCENT, C_BROWN, C_BLUE, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=8.0, ymax=50)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 47.0, "USE 방법론 — 리소스 기반(resource-driven) 자원", size=19, weight="bold")
text(50, 43.8, "유한한 용량을 가진 자원을 세 지표로 본다 — Utilization · Saturation · Errors",
     size=11.5, color=C_DIM)

# ---- resource ----
box(4, 18, 22, 12, C_BROWN, ec=C_VIOLET, lw=1.8)
text(15, 26.2, "리소스", size=14, weight="bold", color="#e7dcff")
text(15, 22.6, "CPU · 메모리 · 디스크\n네트워크 · 커넥션 풀", size=9.5, color="#d4dae0")

# ---- three outputs ----
outs = [
    (36, "Utilization", "사용 중인 시간의 비율", 'rate(node_cpu_seconds_total{mode!="idle"}[5m])'),
    (24, "Saturation", "처리 못해 쌓인 초과 작업량", "node_load1 · 커넥션 풀 대기 요청 수"),
    (12, "Errors", "자원 자체의 에러", "디스크 I/O 에러 · OOM kill · 커넥션 거부"),
]
for yc, t, d, q in outs:
    box(56, yc - 5, 40, 10, C_BLUE)
    text(58.5, yc + 2.6, t, size=13, weight="bold", color=C_ACCENT, ha="left")
    text(58.5, yc - 0.1, d, size=9.5, color=C_TEXT, ha="left")
    text(58.5, yc - 3.0, q, size=8.2, color=C_DIM, ha="left", style="italic")
    arrow(26, 24, 56, yc, color=C_ORANGE, lw=2.0, rad=0.05)

# bottom
text(50, 4.4, "RED와 대체재가 아니다 — 요청 처리 계층은 RED로, 그 서비스가 소비하는 인프라 자원은 USE로 본다",
     size=11, color=C_ACCENT, weight="bold")
text(50, 1.8, "Four Golden Signals(Latency·Traffic·Errors·Saturation) = RED + USE의 통합 상위 개념",
     size=8.8, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "08-use-method.png")
