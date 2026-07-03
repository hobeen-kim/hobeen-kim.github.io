"""CH25 Pyroscope + Grafana Phlare 병합 역사 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=7.2, ymax=48)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 44.6, "Grafana Pyroscope — Phlare 병합 역사 (2023)", size=20, weight="bold")
text(50, 41.4, "Pyroscope의 이름·SDK·UX  +  Phlare의 오브젝트 스토리지 아키텍처  =  현재의 Grafana Pyroscope",
     size=12, color=C_DIM)

# ---- left: two sources ----
box(3, 26, 28, 9, C_BLUE)
text(17, 32.0, "Pyroscope", size=13, weight="bold")
text(17, 29.4, "오픈소스 · 언어별 SDK · 직관적 UX\n로컬 스토리지(Badger)", size=9, color=C_DIM)

box(3, 11, 28, 9, C_GREEN)
text(17, 17.0, "Grafana Phlare", size=13, weight="bold")
text(17, 14.4, "오브젝트 스토리지 아키텍처\ningester·querier·compactor (2022)", size=9, color=C_DIM)

# ---- center: merge ----
box(40, 18, 18, 10, C_BROWN, ec=C_ORANGE, lw=1.8)
text(49, 24.4, "병합", size=14, weight="bold", color=C_ORANGE)
text(49, 21.2, "2023\n두 프로젝트 통합", size=9.5, color=C_DIM)

arrow(31, 30.5, 40, 25.5, color=C_ACCENT, lw=2.2)
arrow(31, 15.5, 40, 20.5, color=C_ACCENT, lw=2.2)

# ---- right: result ----
box(66, 15.5, 31, 15, C_GRAY, ec=C_ACCENT, lw=2.0)
text(81.5, 26.6, "Grafana Pyroscope", size=14, weight="bold", color=C_ACCENT)
text(81.5, 23.4, "Pyroscope 이름 + Phlare 아키텍처", size=9.5, color="#d4dae0")
text(81.5, 20.0, "distributor · ingester · querier\nstore-gateway · compactor", size=9, color=C_DIM)
text(81.5, 16.9, "Mimir/Loki/Tempo와 같은 계열 구성", size=8.5, color=C_ACCENT, style="italic")

arrow(58, 23, 66, 23, color=C_ORANGE, lw=2.4)

# bottom
text(50, 6.0, "사용자 친화 SDK·UX 자산은 계승하되, 내부 저장 엔진은 확장 가능한 Phlare 구조로 교체",
     size=10, color=C_ACCENT, weight="bold")
text(50, 3.0, "LGTM+ 스택 중 가장 뒤늦게 정착했지만 가장 일관된 설계를 갖춘 컴포넌트",
     size=9, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "25-phlare-merge.png")
