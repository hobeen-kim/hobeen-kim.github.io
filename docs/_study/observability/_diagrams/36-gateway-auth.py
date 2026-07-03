"""CH36 게이트웨이 인증·인가와 컴포넌트 간 mTLS (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=8.6, ymax=56)
box, text, arrow = make_helpers(ax)

text(50, 53.4, "게이트웨이 인증·인가와 mTLS", size=20, weight="bold")
text(50, 50.4, "X-Scope-OrgID는 인증 수단이 아니다 — 게이트웨이가 실제 인증 후 신뢰된 값으로 주입",
     size=11, color=C_DIM)

# ---- client ----
box(3, 28, 18, 11, C_GRAY)
text(12, 35.5, "Prometheus /\nGrafana", size=11, weight="bold")
text(12, 31.0, "(클라이언트)", size=9, color=C_DIM)

# ---- gateway ----
box(26, 26, 20, 15, C_BROWN, ec=C_ORANGE, lw=1.8)
text(36, 37.6, "Gateway", size=13, weight="bold", color=C_ORANGE)
text(36, 33.4, "OAuth2 / JWT 검증", size=9.2, color="#e6d6c4")
text(36, 30.4, "X-Scope-OrgID 주입", size=9.2, color="#e6d6c4")

# ---- internal network group ----
box(51, 8, 47, 40, "#141a20", ec=C_ACCENT, lw=1.4)
text(74.5, 45.4, "내부 네트워크 (mTLS)", size=11.5, weight="bold", color=C_ACCENT)

box(55, 34, 18, 6.5, C_BLUE)
text(64, 37.25, "Mimir\ndistributor", size=9.8)
box(77, 34, 18, 6.5, "#4a3d63")
text(86, 37.25, "Mimir\nquery-frontend", size=9.5)
box(55, 15, 18, 6.5, C_BLUE)
text(64, 18.25, "ingester", size=10)
box(77, 15, 18, 6.5, "#4a3d63")
text(86, 18.25, "store-gateway", size=9.8)

# ---- arrows ----
arrow(21, 33, 26, 33, color=C_ACCENT, lw=2.2)
text(23.5, 35.0, "mTLS +\nBearer Token", size=8.2, color=C_ACCENT)

arrow(46, 35, 55, 37, color=C_ORANGE, lw=2.0)
arrow(46, 32, 77, 36, color=C_ORANGE, lw=2.0)
text(51.5, 39.0, "X-Scope-OrgID 주입", size=8.2, color=C_ORANGE)

arrow(64, 34, 64, 21.5, color=C_VIOLET, lw=1.8, ls="--")
text(60.5, 27.5, "mTLS", size=8.3, color=C_VIOLET, ha="right")
arrow(86, 34, 86, 21.5, color=C_VIOLET, lw=1.8, ls="--")
text(89.5, 27.5, "mTLS", size=8.3, color=C_VIOLET, ha="left")

text(50, 3.4, "백엔드는 게이트웨이를 거친 요청만 신뢰 — 네트워크 정책으로 직접 접근 차단, 컴포넌트 간 mTLS 강제",
     size=9.5, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.4, label="클라이언트 인증(mTLS+토큰)"),
    Line2D([0], [0], color=C_ORANGE, lw=2.4, label="검증 후 테넌트 헤더 주입"),
    Line2D([0], [0], color=C_VIOLET, lw=2.4, ls="--", label="컴포넌트 간 mTLS"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.02),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "36-gateway-auth.png")
