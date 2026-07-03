"""CH10 벡터 매칭 — group_left / group_right (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_TEXT, C_DIM, C_ACCENT, C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE)

fig, ax = new_fig(w=15, h=7.8, ymax=48)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 45.2, "벡터 매칭 — on / ignoring + group_left / group_right", size=18.5, weight="bold")
text(50, 42.0, "라벨 스키마가 다른 두 메트릭을 조인 · many-to-one 방향을 group_left/right로 명시",
     size=11, color=C_DIM)

# ---- left (one) ----
box(4, 27, 26, 10, C_BLUE, ec=C_ACCENT, lw=1.8)
text(17, 33.4, "왼쪽 벡터 (one 쪽)", size=11.5, weight="bold", color=C_ACCENT)
text(17, 29.8, "매칭 키당 시계열 1개 · 값 기준", size=8.6, color=C_DIM)

# ---- right (many) ----
box(4, 9, 26, 10, C_GREEN)
text(17, 15.4, "오른쪽 벡터 (many 쪽)", size=11.5, weight="bold", color=C_ACCENT)
text(17, 11.8, "info 메트릭 등 · extra 라벨 보유", size=8.6, color=C_DIM)

# ---- result ----
box(52, 15, 44, 16, C_GRAY, ec=C_ACCENT, lw=2.0)
text(74, 27.0, "결과 벡터", size=13, weight="bold", color=C_ACCENT)
text(74, 23.2, "왼쪽(one) 값을 기준으로", size=9.8, color=C_TEXT)
text(74, 20.2, "many 쪽의 extra 라벨을 끌어와 덧붙임", size=9.8, color=C_TEXT)
text(74, 17.0, "예: 사용량 × on(namespace) group_left(team) kube_namespace_labels", size=8.0,
     color=C_DIM, style="italic")

arrow(30, 32, 52, 26, color=C_ORANGE, lw=2.2, rad=0.06)
text(41, 32.2, "on(label)\ngroup_left(extra)", size=8.4, color=C_ORANGE, weight="bold")
arrow(30, 14, 52, 20, color=C_ACCENT, lw=2.2, rad=-0.06)

# bottom
text(50, 5.4, "group_left = 왼쪽이 one·오른쪽이 many · group_right는 반대 · 괄호 안엔 many 쪽에서 끌어올 추가 라벨",
     size=9.8, color=C_ACCENT, weight="bold")
text(50, 2.6, "many-to-many는 벡터 매칭으로 표현 불가 — 먼저 sum by(...)로 한쪽을 one으로 만든 뒤 조인한다",
     size=8.8, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "10-vector-matching.png")
