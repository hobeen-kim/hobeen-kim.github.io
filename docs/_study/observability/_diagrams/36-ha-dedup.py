"""CH36 Prometheus HA — 독립 레플리카와 다운스트림 중복 제거 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=8.8, ymax=58)
box, text, arrow = make_helpers(ax)

text(50, 55.4, "Prometheus HA — 독립 레플리카와 중복 제거", size=20, weight="bold")
text(50, 52.4, "같은 스크레이프 쌍을 완전히 독립 운영 → Alertmanager gossip · Mimir replica 라벨로 dedup",
     size=10.5, color=C_DIM)

lanes = [
    (13, "Prometheus A\n(replica=a)", C_BLUE),
    (38, "Prometheus B\n(replica=b)", C_GREEN),
    (65, "Alertmanager\n클러스터", C_BROWN),
    (90, "Mimir\n(dedup 쿼리)", "#4a3d63"),
]
top_y, bot_y = 45.5, 5
for x, name, fc in lanes:
    box(x - 9, 46, 18, 4.6, fc)
    text(x, 48.3, name, size=9.8, weight="bold")
    ax.plot([x, x], [bot_y, top_y], color=C_EDGE, lw=1.1, ls="--", zorder=1)

X = {n: x for x, n, _ in lanes}


def msg(y, a, b, label, dashed=False, color=C_ACCENT):
    ls = "--" if dashed else "-"
    x1, x2 = X[a], X[b]
    arrow(x1, y, x2, y, color=color, lw=2.0, ls=ls)
    text((x1 + x2) / 2, y + 1.3, label, size=8.6, color=C_TEXT)


def note(y, lane, label, w=22):
    x = X[lane]
    box(x - w / 2, y - 1.9, w, 3.8, "#2a2320", ec=C_ORANGE, lw=1.2)
    text(x, y, label, size=8.5, color=C_ORANGE)


# par block: independent scrape + rule eval
box(4, 37, 43, 6.5, "#141a20", ec=C_ACCENT, lw=1.2)
text(6, 42.2, "par  독립적으로 스크레이프 · 룰 평가", size=8.6, color=C_ACCENT, ha="left")
box(X["Prometheus A\n(replica=a)"] - 8.5, 37.7, 17, 3.2, "#1b232a")
text(13, 39.3, "타깃 스크레이프 + 룰 평가", size=7.6)
box(X["Prometheus B\n(replica=b)"] - 8.5, 37.7, 17, 3.2, "#1d2b24")
text(38, 39.3, "타깃 스크레이프 + 룰 평가", size=7.6)

msg(33, "Prometheus A\n(replica=a)", "Alertmanager\n클러스터", "Alert 발화", color=C_ORANGE)
msg(28.5, "Prometheus B\n(replica=b)", "Alertmanager\n클러스터", "동일 Alert 발화 (fingerprint 동일)", color=C_ORANGE)
note(23, "Alertmanager\n클러스터", "gossip으로 중복 인지\n1건만 발송")

msg(16.5, "Prometheus A\n(replica=a)", "Mimir\n(dedup 쿼리)", "remote_write (replica=a)", dashed=True, color=C_VIOLET)
msg(12, "Prometheus B\n(replica=b)", "Mimir\n(dedup 쿼리)", "remote_write (replica=b)", dashed=True, color=C_VIOLET)
note(6.5, "Mimir\n(dedup 쿼리)", "쿼리 시 replica\n라벨 기준 dedup")

text(50, 2.0, "레플리카는 서로 다른 가용영역(AZ)에 배치 — 같은 랙·전원 계통에 두면 HA 의미가 없다",
     size=9.5, color=C_ACCENT, style="italic")

leg = [
    Line2D([0], [0], color=C_ORANGE, lw=2.4, label="알림 발화 → gossip dedup"),
    Line2D([0], [0], color=C_VIOLET, lw=2.4, ls="--", label="remote_write → replica dedup"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.02),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "36-ha-dedup.png")
