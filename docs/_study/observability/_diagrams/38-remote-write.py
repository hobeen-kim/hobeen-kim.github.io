"""CH38 remote_write 큐 파이프라인 시퀀스 다이어그램 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "remote_write — 큐 기반 비동기 전송과 적체 전파", size=20, weight="bold")
text(50, 56.6, "원격 저장소 지연 → 샤드 재시도 → 큐 적체(samples_pending) → WAL 삭제 지연 → 디스크 압박",
     size=12, color=C_DIM)

# ---- lifelines ----
actors = [
    (13, "WAL / Head Block", C_BROWN),
    (38, "remote_write Queue", C_BLUE),
    (62, "Shard (N개·오토스케일)", C_GREEN),
    (87, "원격 저장소 (Mimir)", C_GRAY),
]
TOP = 51.5
BOT = 8.5
for x, name, fc in actors:
    box(x - 10, TOP, 20, 4.2, fc, ec=C_ACCENT, lw=1.4)
    text(x, TOP + 2.1, name, size=10, weight="bold")
    ax.plot([x, x], [BOT, TOP], color=C_EDGE, lw=1.0, ls=(0, (4, 3)), zorder=1)

def msg(x1, x2, y, label, color=C_ACCENT, style="-|>", lw=1.9, up=True):
    arrow(x1, y, x2, y, color=color, lw=lw, style=style)
    mx = (x1 + x2) / 2
    text(mx, y + (1.2 if up else -1.2), label, size=8.2,
         color=color, weight="bold", va="bottom" if up else "top")

# 1. WAL -> Q
msg(13, 38, 49, "샘플 append", C_ACCENT)

# loop 정상 상태 박스
box(26.5, 37.5, 62, 9.5, "#151b21", ec=C_GREEN, lw=1.2)
text(29, 45.4, "loop  정상 상태", size=8.5, color=C_GREEN, weight="bold", ha="left")
msg(38, 62, 44, "배치 분배", C_GREEN)
msg(62, 87, 41, "HTTP POST (batch)", C_GREEN)
msg(87, 62, 38.3, "200 OK", C_GREEN, style="-|>", lw=1.6, up=False)

# Note: 원격 저장소 지연
box(76, 32.2, 22, 3.4, C_BROWN, ec=C_ORANGE, lw=1.4)
text(87, 33.9, "원격 저장소 지연 발생", size=8.5, color=C_ORANGE, weight="bold")

# 지연 구간
msg(62, 87, 29.5, "HTTP POST (batch)", C_ORANGE)
msg(87, 62, 26.8, "5xx / timeout", C_ORANGE, style="-|>", lw=1.6, up=False)

# self retry on shard
arrow(62, 24.5, 70, 24.5, color=C_ORANGE, lw=1.6)
arrow(70, 24.5, 70, 22.5, color=C_ORANGE, lw=1.6)
arrow(70, 22.5, 62, 22.5, color=C_ORANGE, lw=1.6, style="-|>")
text(72.5, 23.5, "지수 백오프 재시도", size=8, color=C_ORANGE, weight="bold", ha="left")

# Note over Q, SHARD: 큐 적체
box(30, 16.5, 42, 3.6, "#3a3050", ec=C_VIOLET, lw=1.4)
text(51, 18.3, "큐 적체 → prometheus_remote_storage_samples_pending 증가", size=8.3,
     color="#e7dcff", weight="bold")

# Note over Q: WAL 삭제 지연
box(20, 11.5, 44, 3.6, "#241d1a", ec=C_ORANGE, lw=1.4)
text(42, 13.3, "큐가 계속 쌓이면 WAL 삭제 지연 → 로컬 디스크 압박", size=8.3,
     color=C_ORANGE, weight="bold")

# bottom
text(50, 5.4, "지연이 커지면 queue_config의 max_shards로 병렬 전송량을 늘린다 — 단, 원격 저장소 수신 용량이 받쳐줄 때만 유효",
     size=9.5, color=C_ACCENT, weight="bold")
text(50, 2.4, "samples_failed_total이 5xx와 함께 증가하면 Mimir distributor/ingester 수신 한도 문제 — Prometheus 튜닝이 아닌 수신 측 조정이 근본 해법",
     size=8.5, color=C_DIM, style="italic")

leg = [
    Line2D([0], [0], color=C_GREEN, lw=2.5, label="정상 전송"),
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="지연·실패·재시도"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, label="적체 상태"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.10),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "38-remote-write.png")
