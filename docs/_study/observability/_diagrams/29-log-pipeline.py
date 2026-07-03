"""CH29 로그 파이프라인 — loki.source → process → write (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_PURPLE)

fig, ax = new_fig(w=15, h=6.6, ymax=44)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 41.0, "로그 파이프라인 — loki.source → loki.process → loki.write", size=18, weight="bold")
text(50, 38.0, "쿠버네티스 Pod 로그를 받아 파싱·라벨링·필터링 후 Loki로 내보내는 컴포넌트 체인",
     size=11, color=C_DIM)

nodes = [
    (2.0, 15.5, "discovery.kubernetes", "Pod 로그 소스", C_BLUE),
    (19.5, 15.5, "loki.source.kubernetes", "원본 라인 수집", C_GREEN),
    (37.0, 24.0, "loki.process", "stage.json → stage.labels\n→ stage.drop", C_BROWN),
    (63.0, 15.5, "loki.write", "내보내기", C_PURPLE),
    (81.5, 13.5, "Loki", "저장·인덱스", C_GRAY),
]
ycen = 22
for x, w, t, d, col in nodes:
    ec = C_ACCENT if col == C_GRAY else C_EDGE
    lw = 1.8 if col == C_GRAY else 1.4
    box(x, ycen - 5.2, w, 10.4, col, ec=ec, lw=lw)
    text(x + w / 2, ycen + 1.9,
         t, size=(13 if col == C_GRAY else 9.6), weight="bold",
         color=(C_ACCENT if col == C_GRAY else C_TEXT))
    text(x + w / 2, ycen - 2.0, d, size=8.2, color=C_DIM)

# arrows between
pairs = [(2.0 + 15.5, 19.5), (19.5 + 15.5, 37.0),
         (37.0 + 24.0, 63.0), (63.0 + 15.5, 81.5)]
for x1, x2 in pairs:
    arrow(x1, ycen, x2, ycen, color=C_ACCENT, lw=2.2)

# bottom
text(50, 6.2, "message처럼 카디널리티 높은 필드는 라벨로 승격하지 않고 로그 본문에 유지 — 인덱스 비용 관리",
     size=10, color=C_ACCENT, weight="bold")
text(50, 3.2, "stage.drop으로 debug 등 노이즈 로그를 파이프라인 단계에서 제거해 Loki 도달 볼륨·저장 비용 절감",
     size=9, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "29-log-pipeline.png")
