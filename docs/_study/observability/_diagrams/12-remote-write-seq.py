"""CH12 remote_write 전송 파이프라인 시퀀스 — WAL watcher·샤드 큐·재시도 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=15, h=9.2, ymax=62)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "remote_write 전송 파이프라인", size=20, weight="bold")
text(50, 56.6, "WAL을 tail → 샤드 큐에 분배 → 배치 단위로 원격 저장소에 HTTP POST → 재시도·drop",
     size=11.5, color=C_DIM)

# ---- lifelines ----
actors = [
    (12, "WAL", C_BROWN),
    (35, "WAL Watcher", C_GRAY),
    (58, "Shard Queue(s)", C_GREEN),
    (85, "Remote Storage\n(Mimir 등)", C_BLUE),
]
for x, name, c in actors:
    box(x - 9, 50, 18, 3.6, c)
    text(x, 51.8, name, size=10.5, weight="bold")
    ax.plot([x, x], [6, 50], color=C_EDGE, lw=1.2, ls="--", zorder=1)

X_WAL, X_W, X_Q, X_R = 12, 35, 58, 85

# ---- sequence steps (top to bottom) ----
def msg(x1, x2, y, label, color=C_ACCENT, rad=0.0, ls="-"):
    arrow(x1, y, x2, y, color=color, lw=2.0, rad=rad, ls=ls)

# WAL -> Watcher
msg(X_WAL, X_W, 46, "")
text(23.5, 47.4, "새 샘플 append 감지 (tail)", size=9, color=C_TEXT)

# Watcher -> Queue
msg(X_W, X_Q, 42, "")
text(46.5, 43.4, "샘플을 샤드에 분배", size=9, color=C_TEXT)

# loop box
box(48, 10, 46, 28, "#161c22", ec=C_ORANGE, lw=1.6)
text(52.5, 36.3, "loop", size=9, color=C_ORANGE, weight="bold")
text(71, 36.3, "배치가 차거나 batch_send_deadline 타임아웃", size=8.8, color=C_ORANGE, style="italic")

# Queue -> Remote
msg(X_Q, X_R, 32, "", color=C_ORANGE)
text(71.5, 33.4, "HTTP POST (Protobuf · snappy 압축)", size=8.6, color=C_ORANGE, weight="bold")

# alt: success
text(52, 28.2, "성공 2xx", size=8.5, color=C_GREEN, weight="bold", ha="left")
msg(X_R, X_Q, 25.5, "", color=C_GREEN, ls="--")
text(71.5, 26.8, "ACK", size=8.6, color=C_GREEN)

# alt: retryable
text(52, 22, "재시도 가능 5xx · 429", size=8.5, color=C_VIOLET, weight="bold", ha="left")
msg(X_R, X_Q, 19.5, "", color=C_VIOLET, ls="--")
# self loop on queue
ax.add_patch(__import__("matplotlib").patches.FancyArrowPatch(
    (X_Q + 1, 18.5), (X_Q + 1, 16), arrowstyle="-|>", mutation_scale=13,
    lw=1.8, color=C_VIOLET, connectionstyle="arc3,rad=-1.4", zorder=4))
text(63, 16.8, "지수 백오프 후 재시도", size=8.5, color=C_VIOLET, ha="left")

# alt: non-retryable
text(52, 13.5, "재시도 불가 4xx (429 제외)", size=8.5, color=C_ORANGE, weight="bold", ha="left")
ax.add_patch(__import__("matplotlib").patches.FancyArrowPatch(
    (X_Q + 1, 12.5), (X_Q + 1, 11), arrowstyle="-|>", mutation_scale=13,
    lw=1.8, color="#c96f5a", connectionstyle="arc3,rad=-1.4", zorder=4))
text(63, 11.3, "샘플 drop + 카운터 증가", size=8.5, color="#c96f5a", ha="left")

# bottom
text(50, 6.6, "전송 소스는 head block이 아니라 WAL — 재시작해도 WAL 오프셋 기준으로 미전송분을 이어서 보낸다",
     size=10, color=C_ACCENT, weight="bold")
text(50, 3.4, "원격이 느리면 큐가 쌓이고 백프레셔로 신규 샘플 투입을 늦춰 메모리 고갈을 막는다 · 처리량 부족 시 샤드 동적 증가(max_shards)",
     size=9, color=C_DIM, style="italic")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="정상 흐름"),
    Line2D([0], [0], color=C_GREEN, lw=2.5, label="성공 ACK"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, label="재시도 (백오프)"),
    Line2D([0], [0], color="#c96f5a", lw=2.5, label="drop (재시도 불가)"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.13),
          fontsize=8, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "12-remote-write-seq.png")
