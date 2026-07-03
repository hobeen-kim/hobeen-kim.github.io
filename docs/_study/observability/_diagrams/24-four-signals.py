"""CH24 관측성 4대 신호 — 프로파일의 자리 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=8.6, ymax=58)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 55.0, "관측성 4대 신호 — 4번째 신호로서의 프로파일", size=20, weight="bold")
text(50, 51.8, "메트릭·로그·트레이스가 채우지 못한 '함수·라인 단위' 공백을 프로파일이 메운다",
     size=12, color=C_DIM)

# ---- hub ----
box(37, 40, 26, 6.5, C_GRAY, ec=C_ACCENT, lw=2.0)
text(50, 43.2, "관측성 4대 신호", size=14, weight="bold", color=C_ACCENT)

signals = [
    (14, "메트릭", "무엇이 얼마나", C_BLUE),
    (38, "로그", "무슨 일이 있었나", C_BROWN),
    (62, "트레이스", "서비스·스팬 단위로\n어디서 시간을 썼나", C_GREEN),
    (86, "프로파일", "함수·라인 단위로\n어디서 시간을 썼나", C_VIOLET.replace("#b9a3e0", "#4a3d63")),
]
for x, t, d, c in signals:
    ec = "#7a68a0" if t == "프로파일" else C_EDGE
    lw = 2.0 if t == "프로파일" else 1.4
    box(x - 11, 16, 22, 12, c, ec=ec, lw=lw)
    tc = "#e7dcff" if t == "프로파일" else C_TEXT
    text(x, 24.5, t, size=13, weight="bold", color=tc)
    text(x, 20.5, d, size=9, color=C_DIM)
    arrow(50, 40, x, 28.2, color=C_EDGE, lw=1.8, style="-|>")

# ---- 프로파일 강조 배지 ----
text(86, 30.6, "4번째 신호", size=8.5, color="#b9a3e0", weight="bold", style="italic")

# ---- dashed: 트레이스 -> 프로파일 (span profiles) ----
ax.annotate("", xy=(80, 16), xytext=(68, 16),
            arrowprops=dict(arrowstyle="-|>", color=C_ORANGE, lw=2.4,
                            linestyle=(0, (5, 3)),
                            connectionstyle="arc3,rad=-0.5"), zorder=6)
text(74, 10.6, "span profiles", size=10, color=C_ORANGE, weight="bold")

# bottom
text(50, 8.4, "메트릭 스파이크가 알림  →  트레이스가 느린 스팬 지목  →  프로파일이 그 안의 원인 함수를 짚는다",
     size=10.5, color=C_ACCENT, weight="bold")
text(50, 5.2, "코드 라인 단위까지 파고드는 리소스 소비 정보는 다른 세 신호가 채울 수 없는 공백을 메운다",
     size=9, color=C_DIM, style="italic")

leg = [
    Line2D([0], [0], color=C_EDGE, lw=2.2, label="4대 신호 구성"),
    Line2D([0], [0], color=C_ORANGE, lw=2.2, ls="--", label="span profiles (트레이스↔프로파일)"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.01),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "24-four-signals.png")
