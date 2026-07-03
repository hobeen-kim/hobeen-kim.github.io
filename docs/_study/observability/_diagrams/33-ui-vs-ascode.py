"""CH33 UI 전용 관리 vs as-code 관리 비교 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=14, h=8, ymax=50)
box, text, arrow = make_helpers(ax)

text(50, 47.4, "UI 전용 관리 vs as-code 관리", size=20, weight="bold")
text(50, 44.4, "대시보드를 애플리케이션 코드와 동일한 신뢰 수준(리뷰·diff·롤백)으로",
     size=12, color=C_DIM)

# ---- top: UI only ----
box(4, 27, 92, 12, C_BROWN, ec="#8a6a52", lw=1.6)
text(9, 37.4, "UI 전용 관리", size=13, weight="bold", color=C_ORANGE, ha="left")
ui = [
    (26, "클릭으로 패널 수정"),
    (50, "변경 이력 없음"),
    (74, "재현 불가"),
]
for x, t in ui:
    box(x - 10, 29.5, 20, 4.6, "#241d1a")
    text(x, 31.8, t, size=10.5)
arrow(26 + 10, 31.8, 50 - 10, 31.8, color=C_ORANGE, lw=2.0)
arrow(50 + 10, 31.8, 74 - 10, 31.8, color=C_ORANGE, lw=2.0)

# ---- bottom: as-code ----
box(4, 6, 92, 15, C_GREEN, ec=C_ACCENT, lw=1.8)
text(9, 19.4, "as-code 관리", size=13, weight="bold", color=C_ACCENT, ha="left")
code = [
    (18, "jsonnet/JSON\n수정"),
    (40, "Git PR 리뷰"),
    (62, "CI가 Grafana에\n반영"),
    (84, "롤백 = git revert"),
]
for x, t in code:
    box(x - 9.5, 9.5, 19, 5.2, "#1d2b24")
    text(x, 12.1, t, size=10)
for i in range(len(code) - 1):
    x1 = code[i][0] + 9.5
    x2 = code[i + 1][0] - 9.5
    arrow(x1, 12.1, x2, 12.1, color=C_ACCENT, lw=2.2)

text(50, 2.6, "대시보드·데이터소스 정의를 텍스트로 리포지토리에 두고 CI/CD가 Grafana에 반영",
     size=10, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "33-ui-vs-ascode.png")
