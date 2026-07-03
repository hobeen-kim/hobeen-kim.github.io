"""CH25 Pyroscope 저장 구조 — 오브젝트 스토리지 · 심볼 DB (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "Pyroscope 저장 구조 — 블록 저장 + 심볼 DB", size=20, weight="bold")
text(50, 56.6, "ingester → 오브젝트 스토리지 → compactor 블록 파이프라인, 심볼 DB가 주소→함수명 변환을 캐싱",
     size=12, color=C_DIM)

def node(x, y, w, h, t, d, c, ec=C_EDGE, lw=1.4, tc=C_TEXT, ds=8.5):
    box(x, y, w, h, c, ec=ec, lw=lw)
    text(x + w / 2, y + h * 0.62, t, size=11, weight="bold", color=tc)
    if d:
        text(x + w / 2, y + h * 0.26, d, size=ds, color=C_DIM)

# distributor
node(6, 43, 20, 8, "distributor", "수집 경로에서 유입", C_GRAY, ec=C_ACCENT, lw=1.8)
# ingester
node(40, 43, 22, 8, "ingester", "메모리 버퍼", C_BLUE)
# object storage
node(72, 42, 24, 10, "오브젝트 스토리지", "S3 / GCS / Azure Blob\n블록(block) 저장", C_BROWN, ec=C_ORANGE, lw=1.6, ds=8.5)
# symbol DB
node(40, 27, 22, 8, "심볼 DB", "주소 → 함수명 캐시\nELF 심볼·디버그 정보", "#4a3d63", ec="#7a68a0", tc="#e7dcff")
# compactor
node(72, 27, 24, 8, "compactor", "블록 병합 · 보존정책 적용", C_GREEN)
# store-gateway
node(40, 12, 22, 8, "store-gateway", "블록 조회 게이트웨이", C_GRAY)
# querier
node(72, 12, 24, 8, "querier", "프로파일 병합 질의 응답", C_GRAY, ec=C_ACCENT, lw=1.8)

# arrows
arrow(26, 47, 40, 47, color=C_ACCENT, lw=2.2)
arrow(62, 46, 72, 46, color=C_ORANGE, lw=2.2)
text(67, 48.0, "블록 플러시", size=8.5, color=C_ORANGE, weight="bold")
# ingester -.-> symbol DB
arrow(51, 43, 51, 35, color=C_VIOLET, lw=2.0, ls=(0, (5, 3)))
text(55.5, 39, "심볼 정보", size=8.5, color=C_VIOLET, weight="bold", ha="left")
# object storage -> compactor
arrow(84, 42, 84, 35, color=C_GREEN, lw=2.2)
# object storage -> store-gateway
arrow(72, 44, 62, 18, color=C_EDGE, lw=2.0)
text(63.5, 30.5, "블록 로드", size=8.2, color=C_DIM, ha="right")
# store-gateway -> querier
arrow(62, 16, 72, 16, color=C_ACCENT, lw=2.2)
# symbol DB -> querier
arrow(51, 27, 78, 20, color=C_VIOLET, lw=2.0, ls=(0, (5, 3)))
text(66, 24.0, "심볼 주입", size=8.2, color=C_VIOLET, ha="center")

# bottom
text(50, 6.0, "심볼 DB 캐싱 덕에 매 질의마다 원본 바이너리를 다시 읽어 심볼을 재해석할 필요가 없다",
     size=10, color=C_ACCENT, weight="bold")
text(50, 3.0, "Mimir·Loki·Tempo와 동일한 오브젝트 스토리지 기반 블록 패턴 + 프로파일 고유의 심볼 DB",
     size=9, color=C_DIM, style="italic")

leg = [
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="블록 플러시·저장"),
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="질의 경로"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, ls="--", label="심볼 정보 (주소→함수명)"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.01),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "25-storage-architecture.png")
