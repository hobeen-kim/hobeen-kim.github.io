"""CH04 Pull 모델 — Prometheus 스크레이프와 up 메트릭 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "Pull 모델 — Prometheus가 능동적으로 스크레이프", size=20, weight="bold")
text(50, 56.6, "서비스 디스커버리로 타깃을 찾고, 스크레이프 성공·실패가 곧 헬스 신호(up)", size=12, color=C_DIM)

# ================= 라이프라인 =================
actors = [
    (16, C_BLUE, "Prometheus"),
    (50, C_GREEN, "서비스 디스커버리"),
    (84, C_BROWN, "타깃 (/metrics)"),
]
for x, fc, name in actors:
    box(x - 12, 47.5, 24, 5.5, fc)
    text(x, 50.2, name, size=11.5, weight="bold")
    ax.plot([x, x], [7, 47.5], color=C_EDGE, lw=1.2, ls=(0, (4, 3)), zorder=1)

# ---- SD 질의 ----
arrow(16, 43, 50, 43, color=C_ACCENT, lw=2.2)
text(33, 44.6, "타깃 목록 질의", size=9.5, color=C_ACCENT, weight="bold")
arrow(50, 39, 16, 39, color=C_VIOLET, lw=2.2, style="-|>", ls="--")
text(33, 40.6, "타깃 주소 목록", size=9.5, color=C_VIOLET, weight="bold")

# ---- loop 박스 ----
box(9, 11, 82, 24, "#161c22", ec=C_ORANGE, lw=1.6)
text(14.5, 32.3, "loop", size=9, color=C_ORANGE, weight="bold", style="italic")
text(30, 32.3, "scrape_interval 마다", size=9, color=C_ORANGE, style="italic")

# GET /metrics
arrow(16, 28, 84, 28, color=C_ACCENT, lw=2.2)
text(50, 29.6, "GET /metrics", size=9.5, color=C_ACCENT, weight="bold")

# alt: 정상 응답
box(12, 19.5, 76, 6.5, C_GRAY)
text(17, 24.2, "alt", size=8.5, color=C_DIM, weight="bold", style="italic")
text(33, 24.2, "정상 응답", size=8.5, color=C_GREEN, style="italic")
arrow(84, 22, 16, 22, color=C_GREEN, lw=2.0, style="-|>", ls="--")
text(50, 23.4, "메트릭 텍스트", size=9, color=C_GREEN, weight="bold")
text(50, 20.6, "up{job=...} = 1", size=8.5, color=C_ACCENT, weight="bold")

# else: 타임아웃/거부
box(12, 12.5, 76, 5.8, "#241d1a")
text(17, 16.8, "else", size=8.5, color=C_DIM, weight="bold", style="italic")
text(35, 16.8, "타임아웃 / 거부", size=8.5, color=C_ORANGE, style="italic")
text(50, 14.0, "up{job=...} = 0  (타깃 다운 신호)", size=9.5, color=C_ORANGE, weight="bold")

# bottom
text(50, 5.2, "수집 메커니즘 자체가 가용성 신호를 겸한다 — 별도 헬스체크 시스템 불필요",
     size=10.5, color=C_ACCENT, weight="bold")
text(50, 2.6, "단점: NAT/방화벽 너머 타깃, 스크레이프 전에 끝나는 단명 작업은 pull로 잡지 못한다",
     size=9, color=C_DIM, style="italic")

save(fig, "04-pull-model.png")
