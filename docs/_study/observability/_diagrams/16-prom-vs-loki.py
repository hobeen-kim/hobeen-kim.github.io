"""CH16 Prometheus 모델 vs Loki 모델 — 인덱싱 철학 비교 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=14, h=7.4, ymax=50)
box, text, arrow = make_helpers(ax)

text(50, 46.5, "Prometheus 모델 vs Loki 모델", size=19, weight="bold")
text(50, 43.4, "\"Prometheus for logs\" — 라벨로 식별하는 철학은 공유, 인덱싱 대상은 다르다", size=11.5, color=C_DIM)

# Prometheus model (left)
box(5, 12, 36, 26, C_BLUE)
text(23, 34.5, "Prometheus 모델", size=14, weight="bold", color=C_ACCENT)
box(9, 20, 28, 10, "#1b2b38")
text(23, 26.5, "metric + labels", size=12, weight="bold")
text(23, 22.5, "숫자 값 자체를 인덱싱\n(라벨 + 값 함께)", size=9.5, color="#d4dae0")
text(23, 15.5, "값이 곧 데이터라서 함께 색인", size=9, color=C_DIM, style="italic")

# Loki model (right)
box(59, 12, 36, 26, C_GREEN, ec=C_ACCENT, lw=1.8)
text(77, 34.5, "Loki 모델", size=14, weight="bold", color=C_ACCENT)
box(63, 27, 28, 6.4, "#1d2b24")
text(77, 31.4, "labels", size=11.5, weight="bold")
text(77, 28.5, "인덱스 대상 (스트림 식별자)", size=9, color="#d4dae0")
box(63, 16, 28, 7.4, "#241d1a")
text(77, 21.0, "log line", size=11.5, weight="bold")
text(77, 18.2, "압축 청크로 저장 · 본문 비인덱싱", size=9, color="#d4dae0")
arrow(77, 27, 77, 23.4, color=C_ORANGE, lw=2.2)
text(88, 25.2, "스트림 식별", size=8.5, color=C_ORANGE)

# philosophy shared arrow (두 박스 사이 빈 공간)
arrow(41, 25, 59, 25, color=C_VIOLET, lw=2.0, ls="--", style="<|-|>")
text(50, 27.4, "철학 공유", size=9.5, color=C_VIOLET, weight="bold")
text(50, 22.6, "라벨로 식별", size=8.5, color=C_DIM, style="italic")

text(50, 6.5, "Loki는 본문 텍스트를 인덱싱하지 않는다 — 라벨로 스트림을 좁힌 뒤 청크만 훑어(grep) 라인 필터 적용",
     size=10, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "16-prom-vs-loki.png")
