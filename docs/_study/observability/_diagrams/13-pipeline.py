"""CH13 Alertmanager 알림 파이프라인 단계 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(w=13, h=8.6, ymax=58)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 54.5, "Alertmanager 알림 파이프라인", size=19, weight="bold")
text(50, 51.3, "수신 → dedup → group → inhibit → silence → route → notify 순으로 필터 통과",
     size=11, color=C_DIM)

# ---- stages top to bottom ----
stages = [
    ("Prometheus로부터 알림 수신", "", C_GRAY, C_EDGE),
    ("Deduplicate", "동일 fingerprint 알림 병합", C_BLUE, C_ACCENT),
    ("Group", "group_by 라벨 기준 묶음", C_BLUE, C_ACCENT),
    ("Inhibit", "더 심각한 알림이 있으면 하위 알림 억제", "#5a3838", "#c96f5a"),
    ("Silence", "matcher에 걸리면 완전 차단", "#5a3838", "#c96f5a"),
    ("Route", "route 트리 따라 receiver 결정", C_GREEN, C_ACCENT),
    ("Notify", "receiver별 채널로 전송, 실패 시 재시도", C_GREEN, C_ACCENT),
]
n = len(stages)
top = 47
gap = 6.4
bw, bh = 52, 4.4
for i, (t, d, fc, ec) in enumerate(stages):
    yc = top - i * gap
    box(50 - bw / 2, yc - bh / 2, bw, bh, fc, ec=ec, lw=1.6)
    if d:
        text(38, yc, t, size=11, weight="bold", ha="left")
        text(90, yc, d, size=8.8, color=C_DIM, ha="right")
    else:
        text(50, yc, t, size=11, weight="bold")
    if i < n - 1:
        arrow(50, yc - bh / 2, 50, yc - gap + bh / 2, color=C_ACCENT, lw=2.0)

# right-side group labels
text(88, 47 - 1.5 * gap, "중복 제거·묶음", size=9, color=C_ACCENT, weight="bold", ha="left")
text(88, 47 - 3.5 * gap, "억제·차단", size=9, color="#c96f5a", weight="bold", ha="left")
text(88, 47 - 5.5 * gap, "라우팅·전송", size=9, color=C_GREEN, weight="bold", ha="left")

# bottom
text(50, 3.4, "각 단계는 서로 다른 목적을 가진 필터 — 순차 통과 뒤에야 실제 채널로 나간다",
     size=10.5, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "13-pipeline.png")
