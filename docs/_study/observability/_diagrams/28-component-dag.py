"""CH28 컴포넌트 그래프(DAG) — export/reference 연결 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_PURPLE)

fig, ax = new_fig(w=15, h=7.0, ymax=46)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 43.0, "컴포넌트 그래프(DAG) — export를 참조로 직접 연결", size=19, weight="bold")
text(50, 40.0, "각 컴포넌트가 앞 컴포넌트의 export를 직접 가리켜 데이터 흐름이 설정 파일에 그대로 드러남",
     size=11, color=C_DIM)

nodes = [
    (2.0, "discovery.kubernetes.pods", "Pod 목록 export", C_BLUE),
    (21.5, "discovery.relabel.filter", "relabel 후 output export", C_GREEN),
    (41.0, "prometheus.scrape.app", "scrape 후 targets 소비", C_BROWN),
    (60.5, "prometheus.remote_write.mimir", "receiver export", C_PURPLE),
]
w = 17.5
ycen = 24
for x, t, d, col in nodes:
    box(x, ycen - 5.0, w, 10.0, col)
    text(x + w / 2, ycen + 1.7, t, size=9.5, weight="bold")
    text(x + w / 2, ycen - 1.8, d, size=8.2, color=C_DIM)

# Mimir sink
box(82.0, ycen - 4.2, 14.0, 8.4, C_GRAY, ec=C_ACCENT, lw=1.8)
text(89.0, ycen, "Mimir", size=13, weight="bold", color=C_ACCENT)

# arrows with labels
edges = [
    (19.5, 21.5, "targets"),
    (39.0, 41.0, "output"),
    (58.5, 60.5, "forward_to"),
    (78.0, 82.0, "remote_write"),
]
for x1, x2, lab in edges:
    arrow(x1, ycen, x2, ycen, color=C_ACCENT, lw=2.2)
    text((x1 + x2) / 2, ycen + 6.4, lab, size=8.5, color=C_ORANGE, weight="bold")

# bottom
text(50, 6.0, "노드 하나가 죽거나 설정이 바뀌면 그 노드에 의존하는 하위 그래프만 재평가 — 전체 재시작 불필요",
     size=10.5, color=C_ACCENT, weight="bold")
text(50, 3.0, "참조 관계가 방향성 비순환 그래프(DAG)를 자동 형성하고 Alloy 런타임이 이 그래프를 따라 데이터를 흘려보냄",
     size=9, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "28-component-dag.png")
