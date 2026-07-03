"""CH02 트레이스 — 하나의 trace_id로 묶인 요청 여정(span 트리) (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "트레이스 — 요청의 전체 여정을 span 트리로 기록", size=20, weight="bold")
text(50, 56.6, "하나의 trace_id=abc123 으로 4개 span이 분산 인과관계로 연결됨", size=12, color=C_DIM)

# ================= 라이프라인 (세로) =================
actors = [
    (12, C_GRAY, "Client"),
    (37, C_BLUE, "API Gateway"),
    (62, C_GREEN, "Payment Service"),
    (87, C_BROWN, "Inventory Service"),
]
for x, fc, name in actors:
    box(x - 9, 47, 18, 5, fc)
    text(x, 49.5, name, size=11, weight="bold")
    # lifeline
    ax.plot([x, x], [8, 47], color=C_EDGE, lw=1.2, ls=(0, (4, 3)), zorder=1)

# ================= 순서 화살표 (위에서 아래로) =================
steps = [
    (42, 12, 37, "POST /checkout", "trace_id=abc123", C_ACCENT, "-|>"),
    (37, 37, 62, "charge() [span]", "", C_ACCENT, "-|>"),
    (32, 62, 87, "reserve_stock() [span]", "", C_ACCENT, "-|>"),
    (26, 87, 62, "300ms 소요", "", C_ORANGE, "-|>"),
    (20, 62, 37, "결제 완료", "", C_GREEN, "-|>"),
    (14, 37, 12, "200 OK", "", C_GREEN, "-|>"),
]
for y, x1, x2, label, sub, color, style in steps:
    dashed = "--" if color == C_GREEN else "-"
    arrow(x1, y, x2, y, color=color, lw=2.2, style=style, ls=dashed)
    midx = (x1 + x2) / 2
    text(midx, y + 1.5, label, size=9.5, color=color, weight="bold")
    if sub:
        text(midx, y - 1.5, sub, size=8, color=C_DIM, style="italic")

# span 구간 강조 (Payment span, Inventory span)
box(60.5, 18.5, 3, 6, C_GREEN, ec=C_ACCENT, lw=1.0, alpha=0.9)  # payment active bar
box(85.5, 24.5, 3, 2.6, C_BROWN, ec=C_ORANGE, lw=1.0, alpha=0.9)  # inventory active bar

# 방향 범례 텍스트
text(12, 44.5, "요청 →", size=8, color=C_DIM)

# bottom note
box(8, 3.2, 84, 4.4, C_GRAY, ec=C_ACCENT, lw=1.6)
text(50, 5.4, "하나의 trace_id로 4개 span이 인과관계로 연결됨 — "
     "\"결제가 느린 이유는 하위 재고 서비스 호출이 300ms 걸렸기 때문\"",
     size=10, color=C_ACCENT, weight="bold")

save(fig, "02-trace-sequence.png")
