"""CH01 세 개의 기둥 신화 vs 상관관계로 연결된 실제 관측성 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "세 개의 기둥(three pillars) 신화 vs 실제 관측성", size=20, weight="bold")
text(50, 56.6, "신호는 독립적으로 서 있을 때가 아니라 상관관계(correlation)로 연결될 때 관측성이 된다",
     size=12, color=C_DIM)

# ================= 왼쪽: 세 개의 기둥 (오해) =================
box(3, 16, 40, 34, C_GRAY)
text(23, 47.2, "세 개의 기둥 (오해)", size=13.5, weight="bold")
text(23, 44.6, "각 신호가 서로 다른 도구·ID로 고립", size=9, color=C_DIM, style="italic")
for i, (t, c) in enumerate([("메트릭", C_BLUE), ("로그", C_GREEN), ("트레이스", C_BROWN)]):
    yy = 38 - i * 7.5
    box(9, yy - 3.0, 28, 6.0, c)
    text(23, yy, t, size=12, weight="bold")

# Myth -> Isolated
arrow(23, 16, 23, 12, color=C_DIM, lw=2.0, ls="--")
box(6, 4.5, 34, 6.5, "#241d1a", ec=C_ORANGE, lw=1.6)
text(23, 9.2, "각자 고립", size=9, color=C_ORANGE, style="italic")
text(23, 6.6, "원인 추적에 수동 작업 필요", size=10.5, color="#e4d3c2", weight="bold")

# ================= 오른쪽: 실제 관측성 =================
box(52, 16, 45, 34, C_GRAY, ec=C_ACCENT, lw=2.0)
text(74.5, 47.2, "실제 관측성", size=13.5, weight="bold", color=C_ACCENT)
text(74.5, 44.6, "exemplar · trace ID · span 으로 상호 연결", size=9, color=C_DIM, style="italic")

# 노드 배치: 메트릭(좌상) - 트레이스(중앙) - 로그(우상) - 프로파일(하)
box(56, 37, 16, 5.5, C_BLUE);   text(64, 39.8, "메트릭", size=11, weight="bold")
box(77, 37, 16, 5.5, C_BROWN);  text(85, 39.8, "로그", size=11, weight="bold")
box(66.5, 28, 16, 5.5, C_GREEN, ec=C_ACCENT, lw=1.6); text(74.5, 30.8, "트레이스", size=11, weight="bold")
box(66.5, 19.5, 16, 5.5, C_VIOLET.replace("#b9a3e0", "#4a3d63") if False else "#4a3d63", ec="#7a68a0", lw=1.4)
text(74.5, 22.3, "프로파일", size=11, weight="bold", color="#e7dcff")

# 양방향 연결 (라벨)
arrow(66.5, 31, 68, 36.8, color=C_ACCENT, lw=1.8, style="<|-|>", rad=-0.15)
text(60.5, 34.6, "exemplar", size=8, color=C_ACCENT, weight="bold")
arrow(81, 36.8, 82.5, 31, color=C_ACCENT, lw=1.8, style="<|-|>", rad=-0.15)
text(88, 34.6, "trace ID", size=8, color=C_ACCENT, weight="bold")
arrow(74.5, 28, 74.5, 25, color=C_ACCENT, lw=1.8, style="<|-|>")
text(79.5, 26.5, "span", size=8, color=C_ACCENT, weight="bold")

# Reality -> Fast
arrow(74.5, 16, 74.5, 12, color=C_ACCENT, lw=2.0, ls="--")
box(57, 4.5, 35, 6.5, "#1d2b24", ec=C_ACCENT, lw=1.6)
text(74.5, 9.2, "상관관계", size=9, color=C_ACCENT, style="italic")
text(74.5, 6.6, "클릭 한 번으로 근본 원인 추적", size=10.5, color=C_ACCENT, weight="bold")

# 중앙 대비 구분선 느낌
text(47.5, 33, "vs", size=15, color=C_DIM, weight="bold")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="상관관계 링크 (exemplar / trace ID / span)"),
    Line2D([0], [0], color=C_DIM, lw=2.5, ls="--", label="귀결"),
]
ax.legend(handles=leg, loc="lower center", bbox_to_anchor=(0.5, -0.02),
          ncol=2, fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

save(fig, "01-three-pillars-vs-observability.png")
