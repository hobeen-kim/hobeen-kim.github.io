"""CH16 라벨 카디널리티 — 안전한 설계 vs 위험한 설계 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE)

fig, ax = new_fig(w=14, h=7.0, ymax=48)
box, text, arrow = make_helpers(ax)

text(50, 44.5, "스트림 = 라벨 집합 — 카디널리티 함정", size=19, weight="bold")
text(50, 41.4, "라벨 값 조합 수가 곧 스트림 수 — 고카디널리티 값을 라벨로 넣으면 스트림 폭증", size=11, color=C_DIM)

# Good design (left)
box(5, 9, 42, 27, C_GREEN, ec=C_ACCENT, lw=1.8)
text(26, 32.5, "안전한 라벨 설계", size=13.5, weight="bold", color=C_ACCENT)
box(9, 23, 34, 6.4, "#1d2b24")
text(26, 27.2, "app · env · namespace · level", size=10.5, weight="bold")
text(26, 24.4, "값 개수 적음 (수십~수백)", size=9, color=C_DIM)
arrow(26, 23, 26, 20, color=C_ACCENT, lw=2.2)
box(9, 12.5, 34, 6.4, "#1b232a")
text(26, 16.7, "스트림 수: 수백~수천", size=11, weight="bold", color=C_ACCENT)
text(26, 13.9, "인덱스 작게 유지 · 압축 효율 높음", size=8.8, color=C_DIM)

# Bad design (right)
box(53, 9, 42, 27, "#3a2a2a", ec=C_BROWN)
text(74, 32.5, "위험한 라벨 설계", size=13.5, weight="bold", color=C_ORANGE)
box(57, 23, 34, 6.4, "#241d1a")
text(74, 27.2, "request_id · user_id · trace_id", size=10.5, weight="bold")
text(74, 24.4, "값 개수 사실상 무한대", size=9, color=C_DIM)
arrow(74, 23, 74, 20, color=C_ORANGE, lw=2.2)
box(57, 12.5, 34, 6.4, "#2a1d1d")
text(74, 16.7, "스트림 수: 무한 증가", size=11, weight="bold", color=C_ORANGE)
text(74, 13.9, "인덱스 비대화 · ingester 메모리 폭증", size=8.8, color=C_DIM)

text(50, 4.5, "고카디널리티 값은 라벨이 아니라 로그 본문 또는 구조화 메타데이터로 — 19장 라벨 설계 참고",
     size=10, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "16-cardinality.png")
