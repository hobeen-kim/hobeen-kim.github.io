"""CH13 gossip HA 클러스터링 — 중복 알림 억제 시퀀스 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=9, ymax=60)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 57, "gossip HA 클러스터링 — 중복 알림 억제", size=20, weight="bold")
text(50, 54, "Prometheus는 모든 AM에 전송 → AM끼리 notification log를 gossip 전파 → 1회만 통지",
     size=11.5, color=C_DIM)

# ---- lifelines ----
actors = [
    (10, "Prometheus", C_GRAY),
    (32, "Alertmanager-1", C_GREEN),
    (54, "Alertmanager-2", C_BLUE),
    (76, "Alertmanager-3", C_BLUE),
    (93, "Slack", C_BROWN),
]
for x, name, c in actors:
    box(x - 8.5, 47, 17, 3.6, c)
    text(x, 48.8, name, size=9.8, weight="bold")
    ax.plot([x, x], [5, 47], color=C_EDGE, lw=1.2, ls="--", zorder=1)

XP, X1, X2, X3, XS = 10, 32, 54, 76, 93

# ---- P -> all AM: 알림 전송 ----
for xt in (X1, X2, X3):
    arrow(XP, 44, xt, 44, color=C_ACCENT, lw=1.8)
text(43, 45.4, "동일 알림을 전체 인스턴스에 전송", size=9, color=C_ACCENT, weight="bold")

# ---- gossip cluster note ----
box(24, 37, 60, 3.4, "#161c22", ec=C_ORANGE, lw=1.4)
text(54, 38.7, "gossip 클러스터 (--cluster.peer · memberlist · 포트 9094)", size=9.5, color=C_ORANGE, weight="bold")

# ---- notification log 전파 ----
arrow(X1, 33, X2, 33, color=C_VIOLET, lw=1.8, ls="--")
arrow(X1, 30, X3, 30, color=C_VIOLET, lw=1.8, ls="--")
text(64, 34.2, "notification log 전파 (P2P)", size=9, color=C_VIOLET, weight="bold")

# ---- self checks ----
def selfnote(x, y, s, color):
    box(x - 11, y - 1.8, 22, 3.6, "#1b232a", ec=color, lw=1.2)
    text(x, y, s, size=8.3, color=C_TEXT)

selfnote(X1, 25, "이미 통지한 알림인지 확인", C_GREEN)
selfnote(X2, 25, "A1이 이미 보냈음 인지\n→ 통지 생략", C_VIOLET)
selfnote(X3, 25, "A1이 이미 보냈음 인지\n→ 통지 생략", C_VIOLET)

# ---- A1 -> Slack (1회만) ----
arrow(X1, 20, XS, 11.5, color=C_ORANGE, lw=2.2, rad=-0.06)
text(58, 17, "A1이 알림 전송 (1회만)", size=10, color=C_ORANGE, weight="bold")

# bottom
text(50, 5.4, "중복 전송은 Prometheus가, 중복 억제는 AM 클러스터 내부 gossip이 담당 — 별도 저장소(etcd 등) 불필요",
     size=10, color=C_ACCENT, weight="bold")
text(50, 2.6, "gossip은 최종 일관성 — 네트워크 파티션 시 짧게 중복 발송 가능, \"중복보다 유실이 나쁘다\" 전제",
     size=9, color=C_DIM, style="italic")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="알림 전송"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, ls="--", label="notification log gossip"),
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="채널로 1회 통지"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.11),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "13-gossip-ha.png")
