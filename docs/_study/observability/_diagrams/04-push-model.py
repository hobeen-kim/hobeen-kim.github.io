"""CH04 Push 모델 — Pushgateway(단명 작업)와 OTLP(장기 서비스) (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=8.4, ymax=54)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 50.6, "Push 모델 — 메트릭을 만드는 쪽이 능동적으로 밀어보낸다", size=19, weight="bold")
text(50, 47.4, "pull이 구조적으로 못 하는 단명 작업·네트워크 경계를 커버", size=12, color=C_DIM)

# ================= 위 경로: 단명 배치 작업 → Pushgateway → Prometheus =================
box(3, 30, 26, 12, C_BROWN, ec=C_ORANGE, lw=1.6)
text(16, 38.4, "단명 배치 작업", size=12, weight="bold", color=C_ORANGE)
box(6, 31.5, 20, 4.6, "#241d1a")
text(16, 33.8, "Cron Job (몇 초 만에 종료)", size=8.8, color="#e4d3c2")

box(40, 30, 24, 12, C_GRAY)
text(52, 38.4, "Pushgateway", size=12.5, weight="bold")
text(52, 34.6, "마지막 값을 들고 있다가\nPrometheus 스크레이프에 응답", size=8.8, color=C_DIM)

box(74, 30, 23, 12, C_BLUE)
text(85.5, 38.4, "Prometheus", size=12.5, weight="bold")
text(85.5, 34.6, "pull로 수집", size=9, color=C_DIM)

arrow(29, 36, 40, 36, color=C_ORANGE, lw=2.4)
text(34.5, 38.2, "종료 직전 push", size=8.8, color=C_ORANGE, weight="bold")
arrow(64, 36, 74, 36, color=C_VIOLET, lw=2.4)
text(69, 38.2, "pull\n(계속 응답)", size=8.2, color=C_VIOLET, weight="bold")

# ================= 아래 경로: 장기 서비스 → Alloy/OTel → Mimir =================
box(3, 8, 26, 12, C_GREEN, ec=C_ACCENT, lw=1.6)
text(16, 16.4, "장기 실행 애플리케이션", size=11.5, weight="bold", color=C_ACCENT)
box(6, 9.5, 20, 4.6, "#1d2b24")
text(16, 11.8, "Service (OTel SDK)", size=9, color="#d4dae0")

box(40, 8, 24, 12, C_GRAY)
text(52, 16.4, "Alloy / OTel Collector", size=11, weight="bold")
text(52, 12.6, "OTLP 리시버", size=9, color=C_DIM)

box(74, 8, 23, 12, C_BLUE, ec=C_ACCENT, lw=1.5)
text(85.5, 14.0, "Mimir", size=13, weight="bold")

arrow(29, 14, 40, 14, color=C_ACCENT, lw=2.4)
text(34.5, 16.2, "OTLP push", size=8.8, color=C_ACCENT, weight="bold")
arrow(64, 14, 74, 14, color=C_ACCENT, lw=2.4)

# bottom
text(50, 3.4, "단명 작업은 Pushgateway로, 장기 서비스는 OTLP로 — Alloy가 pull·push를 한 파이프라인에서 혼합",
     size=10.5, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="종료 직전 push (단명 작업)"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, label="Prometheus pull"),
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="OTLP push (장기 서비스)"),
]
ax.legend(handles=leg, loc="center", bbox_to_anchor=(0.5, 0.45),
          ncol=3, fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

save(fig, "04-push-model.png")
