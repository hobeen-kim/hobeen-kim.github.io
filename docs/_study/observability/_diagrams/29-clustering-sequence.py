"""CH29 clustering 타깃 분배 — 시퀀스 다이어그램 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_PURPLE)

fig, ax = new_fig(w=15, h=9.2, ymax=62)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "clustering 타깃 분배 — 컨시스턴트 해싱 흐름", size=20, weight="bold")
text(50, 56.6, "discovery가 발견한 타깃을 3개 레플리카가 나눠 스크레이프하고 각자 자기 몫만 remote_write",
     size=12, color=C_DIM)

# lifelines
actors = [
    (16, "discovery.kubernetes", C_BLUE),
    (50, "Alloy Cluster (3 replica)", C_GREEN),
    (86, "Mimir", C_BROWN),
]
top = 50.5
bot = 6.0
for x, name, col in actors:
    box(x - 12, top, 24, 4.6, col, ec=C_ACCENT, lw=1.6)
    text(x, top + 2.3, name, size=11, weight="bold")
    ax.plot([x, x], [bot, top], color=C_EDGE, lw=1.4, ls=(0, (4, 3)), zorder=1)

xDK, xC, xM = 16, 50, 86

def msg(y, x1, x2, label, color=C_ACCENT, rad=0.0):
    arrow(x1, y, x2, y, color=color, lw=2.0)
    mx = (x1 + x2) / 2
    text(mx, y + 1.5, label, size=9, color=C_TEXT, weight="bold")

def note(y, x, w, label, col=C_GRAY):
    box(x - w / 2, y - 2.2, w, 4.4, col, ec=C_ORANGE, lw=1.4)
    text(x, y, label, size=8.8, color=C_ORANGE, weight="bold")

def selfmsg(y, x, label):
    # self-loop on cluster lifeline
    ax.add_patch(__import__("matplotlib").patches.FancyArrowPatch(
        (x, y + 1.1), (x, y - 1.1), arrowstyle="-|>", mutation_scale=13,
        linewidth=1.8, color=C_VIOLET_LOCAL,
        connectionstyle="arc3,rad=-1.6", zorder=4))
    text(x + 15.5, y, label, size=9, color=C_TEXT, ha="center")

C_VIOLET_LOCAL = "#b9a3e0"

# 1. DK -> C
msg(47.0, xDK, xC, "타깃 200개 발견", color=C_ACCENT)

# 2. note over C
note(41.5, xC, 40, "컨시스턴트 해싱으로 타깃을 레플리카별 소유권 분배")

# 3-5 self messages (replica ownership)
selfs = [
    (35.5, "alloy-0: 타깃 1~67 스크레이프"),
    (30.0, "alloy-1: 타깃 68~134 스크레이프"),
    (24.5, "alloy-2: 타깃 135~200 스크레이프"),
]
for y, lab in selfs:
    selfmsg(y, xC, lab)

# 6. C -> M
msg(18.0, xC, xM, "각 레플리카가 자기 몫만 remote_write", color=C_ACCENT)

# 7. note over C: failure
note(11.5, xC, 40, "alloy-1 다운 시 나머지가 재해싱해 흡수", col="#2a1f1a")

# bottom
text(50, 3.0, "각 레플리카는 전체 목록을 동일하게 받지만 '내 몫이 아니다' 판단 시 스킵 — 중복 스크레이프 없이 부하 분산",
     size=9.5, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "29-clustering-sequence.png")
