"""CH12 PromQL 쿼리 — index 역인덱스 조회 경로 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=14, h=5.6, ymax=38)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 34.5, "PromQL 쿼리의 index 조회 경로", size=19, weight="bold")
text(50, 31.2, "라벨 매처  →  역인덱스로 시계열 ID 교집합  →  해당 ID의 chunk만 읽기",
     size=11, color=C_DIM)

# ---- 4 columns ----
yc = 16
# 1. Query
box(2, 8, 22, 16, C_BLUE)
text(13, 21, "PromQL 쿼리", size=12.5, weight="bold")
text(13, 16.5, '{job="api",\nstatus_code="500"}', size=10.5, color="#d4dae0")

# 2. Index
box(28, 8, 22, 16, C_GRAY, ec=C_ACCENT, lw=1.8)
text(39, 21, "Index", size=12.5, weight="bold", color=C_ACCENT)
text(39, 16.5, "역인덱스\n(라벨 → 시계열 ID)", size=10.5)

# 3. IDs
box(54, 8, 20, 16, C_GREEN)
text(64, 21, "매칭 시계열 ID", size=12, weight="bold")
text(64, 16.5, "job=api 집합\n∩ status=500 집합", size=10, color="#d4dae0")

# 4. Chunks
box(78, 8, 20, 16, C_BROWN)
text(88, 21, "Chunk 읽기", size=12, weight="bold")
text(88, 16.5, "매칭 ID의\nchunk만 스캔", size=10, color=C_DIM)

# arrows
arrow(24, 16, 28, 16, color=C_ACCENT, lw=2.2)
arrow(50, 16, 54, 16, color=C_ACCENT, lw=2.2)
text(52, 18.5, "교집합", size=9, color=C_ACCENT, weight="bold")
arrow(74, 16, 78, 16, color=C_ACCENT, lw=2.2)

# bottom
text(50, 4.2, "라벨 카디널리티가 높을수록 index 크기·조회 비용이 커지는 것이 카디널리티 문제의 근원",
     size=10.5, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "12-query-index.png")
