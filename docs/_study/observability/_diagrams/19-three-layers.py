"""CH19 Loki 3계층 — 라벨 / 구조화 메타데이터 / 로그 본문 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE)

fig, ax = new_fig(w=14, h=7.2, ymax=48)
box, text, arrow = make_helpers(ax)

text(50, 44.5, "Loki의 세 저장 계층", size=19, weight="bold")
text(50, 41.4, "구조화 메타데이터 = 라벨(인덱스)과 로그 본문(파서 필요) 사이의 절충안", size=11, color=C_DIM)

# stream node (center top)
box(38, 33, 24, 5.6, C_GRAY, ec=C_ACCENT, lw=1.8)
text(50, 35.8, "스트림", size=13, weight="bold", color=C_ACCENT)

# label (left) identifies stream
box(4, 33, 28, 5.6, C_GREEN)
text(18, 36.5, "라벨", size=11.5, weight="bold")
text(18, 34.0, "인덱스 · 저카디널리티", size=8.8, color=C_DIM)
arrow(32, 35.8, 38, 35.8, color=C_ACCENT, lw=2.0, ls="--")
text(35, 37.4, "스트림 식별", size=7.8, color=C_ACCENT)

# two content layers below
box(10, 18, 38, 10, C_BLUE, ec=C_ACCENT, lw=1.6)
text(29, 25.0, "구조화 메타데이터", size=12, weight="bold", color=C_ACCENT)
text(29, 21.8, "비인덱스 · 고카디널리티 허용\n파서 불필요, key-value로 필터링", size=9.3, color="#d4dae0")

box(52, 18, 38, 10, C_BROWN)
text(71, 25.0, "로그 본문", size=12, weight="bold")
text(71, 21.8, "비인덱스 · 파서 필요\n매 쿼리마다 파싱해야 필터 가능", size=9.3, color="#d4dae0")

arrow(46, 33, 33, 28, color=C_ORANGE, lw=2.0)
arrow(54, 33, 67, 28, color=C_ORANGE, lw=2.0)

# examples
box(10, 10, 38, 5.2, "#1b2b38")
text(29, 12.6, "trace_id · user_id · request_id", size=9.5, color=C_ACCENT)
box(52, 10, 38, 5.2, "#241d1a")
text(71, 12.6, "JSON 필드 · 원문 메시지", size=9.5, color=C_DIM)

text(50, 4.5, "고카디널리티 필드를 스트림 폭증 없이 청크 안에 별도 key-value로 저장 → 파서 없이 필터링",
     size=10, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "19-three-layers.png")
