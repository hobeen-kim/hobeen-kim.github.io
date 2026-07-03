"""CH17 읽기 경로 — query-frontend → querier → ingester + storage 병합 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

text(50, 59.0, "Loki 읽기 경로 (read path)", size=20, weight="bold")
text(50, 56.0, "querier가 ingester(최신)와 스토리지(과거)를 동시에 조회해 시간순 병합", size=12, color=C_DIM)

# user
box(36, 47, 28, 6.5, C_BLUE)
text(50, 51.4, "사용자 / Grafana", size=12.5, weight="bold")

# query-frontend
box(34, 37, 32, 6.5, C_GRAY, ec=C_ACCENT, lw=1.8)
text(50, 41.4, "Query-Frontend", size=12.5, weight="bold", color=C_ACCENT)
text(50, 38.5, "쿼리 분할 + 캐싱", size=9.5, color=C_DIM)

# querier
box(38, 27, 24, 6.5, C_GREEN)
text(50, 31.4, "Querier", size=12.5, weight="bold")
text(50, 28.6, "서브쿼리 실행", size=9.5, color=C_DIM)

# three sources
box(4, 13, 26, 8, C_GREEN, ec=C_ACCENT, lw=1.5)
text(17, 18.2, "Ingester", size=11.5, weight="bold")
text(17, 15.2, "미flush 최신 데이터", size=9, color=C_DIM)

box(37, 13, 26, 8, C_GRAY)
text(50, 18.2, "Index (TSDB)", size=11.5, weight="bold")
text(50, 15.2, "청크 위치 조회", size=9, color=C_DIM)

box(70, 13, 26, 8, C_BROWN)
text(83, 18.2, "오브젝트 스토리지", size=11.5, weight="bold")
text(83, 15.2, "flush된 과거 청크", size=9, color=C_DIM)

# merge
box(30, 3.5, 40, 6.0, C_BLUE, ec=C_ACCENT, lw=1.6)
text(50, 6.5, "시간순 병합 → 사용자에게 결과 반환", size=12, weight="bold")

# arrows
arrow(50, 47, 50, 43.5, color=C_ACCENT, lw=2.2)
arrow(50, 37, 50, 33.5, color=C_ACCENT, lw=2.2)
arrow(45, 27, 17, 21, color=C_ORANGE, lw=2.0)
text(27, 25.0, "최신 데이터", size=8.5, color=C_ORANGE)
arrow(50, 27, 50, 21, color=C_ORANGE, lw=2.0)
text(58.5, 24.0, "청크 위치 조회", size=8.5, color=C_ORANGE)
arrow(55, 27, 83, 21, color=C_ORANGE, lw=2.0)
text(74, 25.0, "과거 청크 fetch", size=8.5, color=C_ORANGE)
arrow(17, 13, 34, 9.0, color=C_ACCENT, lw=2.0)
arrow(83, 13, 66, 9.0, color=C_ACCENT, lw=2.0)

# index → storage relation
arrow(63, 16.5, 70, 16.5, color=C_DIM, lw=1.5, ls="--")

text(50, 0.6, "방금 들어온 로그도 flush를 기다리지 않고 즉시 쿼리에 잡힌다 — 이중 조회의 이점",
     size=10, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "17-read-path.png")
