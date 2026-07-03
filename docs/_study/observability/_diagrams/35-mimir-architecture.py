"""CH35 Mimir 마이크로서비스 아키텍처 — 쓰기·저장·압축·읽기 경로 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=9.2, ymax=62)
box, text, arrow = make_helpers(ax)

text(50, 59.4, "Mimir 마이크로서비스 아키텍처", size=20, weight="bold")
text(50, 56.6, "쓰기(distributor·ingester) · 오브젝트 스토리지 · 압축(compactor) · 읽기(query-frontend·querier·store-gateway)",
     size=10.5, color=C_DIM)

# ---- group backgrounds ----
box(3.5, 27.5, 23, 20.5, "#161d24", ec=C_EDGE, lw=1.0)
text(5, 46.3, "쓰기 경로", size=9.5, color=C_DIM, ha="left")
box(73.5, 15.5, 23, 32.5, "#161d24", ec=C_EDGE, lw=1.0)
text(75, 46.3, "읽기 경로", size=9.5, color=C_DIM, ha="left")
box(39.5, 22, 21, 10, "#1a1614", ec=C_EDGE, lw=1.0)
text(41, 30.5, "압축", size=9.5, color=C_DIM, ha="left")
box(39.5, 7.5, 21, 12, "#131c17", ec=C_EDGE, lw=1.0)
text(41, 18.0, "오브젝트 스토리지", size=9.5, color=C_DIM, ha="left")

# ---- write column ----
box(6, 50, 18, 5.6, C_GRAY)
text(15, 52.8, "Prometheus\n(remote_write)", size=9.5, weight="bold")
box(6, 39.5, 18, 6.2, C_BLUE)
text(15, 42.6, "distributor\n검증·limit·라우팅", size=9.3)
box(6, 29, 18, 6.2, C_BLUE)
text(15, 32.1, "ingester\n메모리 + WAL", size=9.3)

# ---- center ----
box(41, 23, 18, 6.2, C_BROWN)
text(50, 26.1, "compactor\n병합·dedup", size=9.3)
box(41, 9, 18, 7.2, C_GREEN)
text(50, 12.6, "S3 / GCS / Azure Blob\n(TSDB 블록)", size=9.3)

# ---- read column ----
box(76, 50, 18, 5.6, C_GRAY)
text(85, 52.8, "Grafana", size=10, weight="bold")
box(76, 39.5, 18, 6.2, "#4a3d63")
text(85, 42.6, "query-frontend\n분할·캐시", size=9.3)
box(76, 29, 18, 6.2, "#4a3d63")
text(85, 32.1, "querier", size=10)
box(76, 17, 18, 6.2, "#4a3d63")
text(85, 20.1, "store-gateway\n블록 인덱스 캐시", size=9.3)

# ---- write arrows ----
arrow(15, 50, 15, 45.7, color=C_ACCENT, lw=2.0)
text(28.5, 48, "remote_write", size=8.3, color=C_ACCENT)
arrow(15, 39.5, 15, 35.2, color=C_ACCENT, lw=2.0)
text(24.5, 37.5, "복제 (RF=3)", size=8.3, color=C_ACCENT)
# ingester -> OBJ (flush)
arrow(23, 30, 41, 14, color=C_ORANGE, lw=2.0)
text(31, 24.5, "블록 flush", size=8.3, color=C_ORANGE)

# ---- compact <-> storage ----
arrow(47.5, 23, 47.5, 16.2, color=C_ORANGE, lw=1.8)
text(40, 19.7, "병합·재작성", size=8.0, color=C_ORANGE, ha="right")
arrow(52.5, 16.2, 52.5, 23, color=C_ORANGE, lw=1.8)

# ---- read arrows ----
arrow(85, 50, 85, 45.7, color=C_VIOLET, lw=2.0)
text(85, 47.9, "PromQL", size=8.3, color=C_VIOLET)
arrow(85, 39.5, 85, 35.2, color=C_VIOLET, lw=2.0)
arrow(85, 29, 85, 23.2, color=C_VIOLET, lw=2.0)
text(96, 26, "과거 데이터", size=8.3, color=C_VIOLET, ha="right")
# querier -> ingester (최근)
arrow(76, 32.1, 24, 32.1, color=C_VIOLET, lw=1.8, rad=0.0)
text(50, 33.6, "최근 데이터", size=8.3, color=C_VIOLET)
# store-gateway -> OBJ
arrow(76, 19, 59, 13.5, color=C_VIOLET, lw=1.8)
text(69, 15.2, "블록 조회", size=8.0, color=C_VIOLET, ha="center")

text(50, 3.0, "컴포넌트별 독립 스케일링 · Mimir는 다운샘플링 대신 query-frontend 분할·캐시로 장기 쿼리 성능 확보",
     size=9.5, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.4, label="쓰기 경로 (수집)"),
    Line2D([0], [0], color=C_ORANGE, lw=2.4, label="블록 flush·압축"),
    Line2D([0], [0], color=C_VIOLET, lw=2.4, label="읽기 경로 (쿼리)"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.02),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "35-mimir-architecture.png")
