"""CH22 Tempo 설계 — 전통적 인덱스 백엔드 vs 오브젝트 스토리지 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_PURPLE, C_VIOLET)

fig, ax = new_fig(ymax=58)
box, text, arrow = make_helpers(ax)


def cbox(cx, cy, bw, bh, fc, **kw):
    box(cx - bw / 2, cy - bh / 2, bw, bh, fc, **kw)


# ---- Title ----
text(50, 55.4, "Tempo 설계 — 전용 검색 인덱스를 버리고 오브젝트 스토리지만 사용", size=17, weight="bold")
text(50, 52.4, "trace ID 조회를 최우선 패턴으로 최적화 · 속성 검색(TraceQL)은 블록 스캔 비용을 감수", size=11, color=C_DIM)

# ===== left: traditional =====
box(4, 8, 40, 40, C_GRAY)
text(24, 44.5, "전통적 트레이싱 백엔드", size=13, weight="bold", color=C_ORANGE)
cbox(24, 37, 26, 6, C_BLUE)
text(24, 37, "Trace 데이터", size=11, weight="bold")
cbox(24, 26, 30, 7, C_BROWN)
text(24, 27.4, "전용 검색 인덱스", size=11, weight="bold")
text(24, 24.6, "Elasticsearch 등 — 인덱스 비대화·운영 복잡", size=8, color=C_DIM)
cbox(24, 15, 22, 6, C_GREEN)
text(24, 15, "쿼리", size=11, weight="bold")
arrow(24, 34, 24, 29.5, color=C_ORANGE, lw=2.0)
arrow(24, 22.5, 24, 18, color=C_ORANGE, lw=2.0)

# ===== right: Tempo =====
box(56, 8, 40, 40, C_GRAY, ec=C_ACCENT, lw=2.0)
text(76, 44.5, "Tempo", size=13, weight="bold", color=C_ACCENT)
cbox(76, 37, 26, 6, C_BLUE)
text(76, 37, "Trace 데이터", size=11, weight="bold")
cbox(76, 27, 30, 6.5, C_BROWN)
text(76, 27, "블록 (오브젝트 스토리지)", size=11, weight="bold")
# two branches
cbox(66, 17.5, 18, 7, C_GREEN)
text(66, 18.9, "블록별 Bloom filter", size=8.6, weight="bold")
text(66, 16.4, "trace ID 존재 여부만", size=7.6, color=C_DIM)
cbox(87, 17.5, 16, 7, C_PURPLE)
text(87, 18.9, "TraceQL 검색", size=9, weight="bold")
text(87, 16.4, "블록 스캔", size=8, color=C_DIM)
arrow(76, 34, 76, 30.5, color=C_ACCENT, lw=2.0)
arrow(72, 23.5, 68, 21.3, color=C_ACCENT, lw=2.0)
arrow(80, 23.5, 85, 21.3, color=C_ACCENT, lw=2.0)
text(66, 11.4, "→ trace ID 조회 (빠름 · 주 경로)", size=8.2, color=C_ACCENT)
text(87, 11.4, "→ 속성 검색 (드묾 · 스캔)", size=8.2, color=C_VIOLET)

# bottom
text(50, 4.2, "Loki와 같은 철학 — 인덱스 최소화로 운영 복잡도·카디널리티 문제를 원천 회피, 저렴한 스토리지에 무제한 축적",
     size=9.5, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "22-tempo-design.png")
