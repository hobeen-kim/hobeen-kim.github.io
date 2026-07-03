"""CH38 Loki/Tempo 수집 병목 — distributor·ingester 흐름 다이어그램 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=8.2, ymax=52)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 49.0, "Loki / Tempo 수집 병목 — distributor·ingester 포화", size=20, weight="bold")
text(50, 45.8, "distributor가 한도 내 쓰기를 ingester로 라우팅 · ingester는 메모리 버퍼를 주기적으로 오브젝트 스토리지에 flush",
     size=11.5, color=C_DIM)

# client
box(3, 26, 18, 9, C_GRAY)
text(12, 32.2, "클라이언트", size=12, weight="bold")
text(12, 29.2, "로그 / 스팬 전송", size=9, color=C_DIM)

# distributor
box(29, 26, 18, 9, C_BLUE, ec=C_ACCENT, lw=1.8)
text(38, 32.2, "Distributor", size=12.5, weight="bold")
text(38, 29.2, "테넌트별 rate limit 판정", size=8.5, color=C_DIM)

# ingester
box(55, 26, 18, 9, C_GREEN)
text(64, 32.2, "Ingester", size=12.5, weight="bold")
text(64, 29.2, "메모리 버퍼", size=9, color=C_DIM)

# object storage
box(81, 26, 16, 9, C_BROWN)
text(89, 32.2, "오브젝트\n스토리지", size=12, weight="bold")

# reject
box(29, 8, 18, 8, "#241d1a", ec=C_ORANGE, lw=1.6)
text(38, 13.4, "429 응답", size=11.5, weight="bold", color=C_ORANGE)
text(38, 10.4, "+ discarded 카운터 증가", size=8, color=C_DIM)

# saturate
box(55, 8, 18, 8, "#3a3050", ec=C_VIOLET, lw=1.6)
text(64, 13.4, "메모리 포화", size=11.5, weight="bold", color="#e7dcff")
text(64, 10.4, "→ OOM 위험", size=8.5, color="#cbb8e6")

# arrows
arrow(21, 30.5, 29, 30.5, color=C_ACCENT, lw=2.2)
arrow(47, 30.5, 55, 30.5, color=C_GREEN, lw=2.2)
text(51, 32.6, "한도 이내", size=8.2, color=C_GREEN, weight="bold")
arrow(73, 30.5, 81, 30.5, color=C_ACCENT, lw=2.2)
text(77, 32.6, "flush 주기", size=8.2, color=C_ACCENT, weight="bold")

# distributor -> reject
arrow(38, 26, 38, 16, color=C_ORANGE, lw=2.0)
text(41.5, 21, "한도 초과", size=8.2, color=C_ORANGE, weight="bold", ha="left")

# ingester -> saturate
arrow(64, 26, 64, 16, color=C_VIOLET, lw=2.0, ls="--")
text(67.5, 21, "flush보다\n유입이 빠르면", size=8, color=C_VIOLET, weight="bold", ha="left")

# bottom
text(50, 4.2, "Loki: ingestion_rate_mb · max_streams_per_user / Tempo: ingestion_rate_limit_bytes — discarded 카운터로 원인(rate_limited·stream_limit) 추적",
     size=9.3, color=C_ACCENT, weight="bold")
text(50, 1.4, "스트림/트레이스 카디널리티 문제를 리밋 완화로만 덮으면 ingester 메모리가 결국 다시 포화 — 라벨 설계부터 고쳐야 한다",
     size=8.8, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "38-loki-tempo-bottleneck.png")
