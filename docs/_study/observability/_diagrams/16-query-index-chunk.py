"""CH16 쿼리 흐름 — 인덱스로 좁히고 청크만 로드 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE)

fig, ax = new_fig(w=14, h=8.0, ymax=54)
box, text, arrow = make_helpers(ax)

text(50, 50.5, "Loki 쿼리 흐름 — 라벨로 좁히고 청크만 로드", size=18, weight="bold")
text(50, 47.4, "인덱스는 라벨→청크 참조만, 실제 로그는 오브젝트 스토리지의 압축 청크", size=11, color=C_DIM)

# Query
box(30, 38, 40, 6.5, C_BLUE)
text(50, 42.4, "LogQL 쿼리", size=12, weight="bold")
text(50, 39.6, '{app="checkout"} |= "timeout"', size=10, color=C_ACCENT)

# Index
box(30, 27, 40, 6.5, C_GRAY, ec=C_ACCENT, lw=1.8)
text(50, 31.4, "인덱스 (TSDB)", size=12, weight="bold", color=C_ACCENT)
text(50, 28.6, "라벨 → 청크 참조 매핑 (작은 테이블)", size=9.5, color=C_DIM)

# Chunks
box(30, 16, 40, 6.5, C_GREEN)
text(50, 20.4, "대상 청크만 로드", size=12, weight="bold")
text(50, 17.6, "라벨 매처로 좁혀진 청크 목록만", size=9.5, color=C_DIM)

# Object storage (right side)
box(76, 15, 21, 20, C_BROWN)
text(86.5, 31.5, "오브젝트\n스토리지", size=12, weight="bold")
text(86.5, 24.5, "압축된\n로그 청크\n(S3/GCS)", size=9.5, color=C_DIM)

# Filter + result
box(30, 5, 40, 6.5, C_BLUE)
text(50, 9.4, "라인 필터 / 파서 적용 → 결과 반환", size=11.5, weight="bold")

arrow(50, 38, 50, 33.5, color=C_ORANGE, lw=2.4)
text(64, 35.8, "1. 라벨 매처로 조회", size=9, color=C_ORANGE)
arrow(50, 27, 50, 22.5, color=C_ORANGE, lw=2.4)
text(64, 24.8, "2. 청크 참조 목록", size=9, color=C_ORANGE)
arrow(70, 19.2, 76, 22, color=C_ORANGE, lw=2.2)
text(73.5, 16.5, "3. 실제 데이터 fetch", size=8.5, color=C_ORANGE)
arrow(50, 16, 50, 11.5, color=C_ACCENT, lw=2.4)

text(50, 1.8, "라벨로 좁혀지지 않는 쿼리는 훑어야 할 청크 수가 폭증 — Loki 운영의 가장 흔한 성능 함정",
     size=10, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "16-query-index-chunk.png")
