"""CH30 Collector와 Alloy의 관계 — 포함 관계 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_PURPLE, C_VIOLET)

fig, ax = new_fig(w=14, h=8.6, ymax=56)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 53.0, "Collector와 Alloy — 대체가 아니라 포함 관계", size=19, weight="bold")
text(50, 50.0, "Alloy는 CNCF OTel Collector 코드베이스를 임베드한 Grafana 배포판",
     size=11, color=C_DIM)

# OTEL (top center)
box(30, 38, 40, 8.5, C_BLUE, ec=C_ACCENT, lw=1.8)
text(50, 43.6, "OpenTelemetry Collector", size=13, weight="bold", color=C_ACCENT)
text(50, 40.4, "CNCF · 벤더 중립 코드베이스", size=9.5, color=C_DIM)

# CONTRIB (bottom left)
box(6, 20, 34, 9.5, C_GRAY)
text(23, 25.9, "opentelemetry-collector-contrib", size=10.5, weight="bold")
text(23, 22.6, "커뮤니티 리시버 / 프로세서 / 익스포터", size=8.8, color=C_DIM)

# ALLOY (bottom right)
box(56, 17.5, 38, 15.5, C_GREEN, ec=C_ACCENT, lw=1.8)
text(75, 30.0, "Grafana Alloy", size=13, weight="bold", color=C_ACCENT)
text(75, 26.8, "Collector 임베드 + Alloy 구문", size=9.2, color=C_DIM)
text(75, 23.8, "+ prometheus.* / loki.* / pyroscope.*", size=9, color=C_TEXT)
text(75, 20.8, "네이티브 컴포넌트", size=9, color=C_TEXT)

# AGENT (far bottom)
box(56, 4.5, 38, 8.0, C_BROWN)
text(75, 9.9, "Grafana Agent", size=11.5, weight="bold")
text(75, 6.8, "EOL · Alloy로 이관 완료", size=9, color=C_DIM)

# edges
arrow(38, 38, 27, 29.5, color=C_ACCENT, lw=2.0)      # OTEL -> CONTRIB
arrow(62, 38, 72, 33.0, color=C_ACCENT, lw=2.4)      # OTEL -> ALLOY
text(70, 36.6, "코드베이스 임베드", size=9, color=C_ORANGE, weight="bold")
arrow(75, 12.5, 75, 17.5, color=C_PURPLE, lw=2.0, style="-|>", ls=(0, (4, 3)))
text(83.5, 15.0, "후속", size=9, color=C_VIOLET, weight="bold")

# bottom summary
text(50, 1.6, "\"Collector vs Alloy\"는 배타적 선택이 아니라 순수 Collector냐, Collector를 감싼 Grafana 배포판이냐의 문제",
     size=9.5, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="파생 · 임베드"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, ls="--", label="후속 이관"),
]
ax.legend(handles=leg, loc="upper left", bbox_to_anchor=(0.02, 0.62),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "30-collector-alloy-relation.png")
