"""CH30 수집 계층 선택 기준 — 의사결정 트리 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_PURPLE)

fig, ax = new_fig(w=15, h=9.2, ymax=62)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "수집 계층 선택 기준 — Collector vs Alloy 의사결정 트리", size=19, weight="bold")
text(50, 56.6, "백엔드 · 벤더 락인 정책 · clustering/프로파일 필요 여부로 갈라지는 분기",
     size=12, color=C_DIM)

def decision(x, y, w, h, label):
    box(x - w / 2, y - h / 2, w, h, C_GRAY, ec=C_ORANGE, lw=1.6)
    text(x, y, label, size=9.8, weight="bold", color=C_TEXT)

def result(x, y, w, h, label, col, sub=None):
    box(x - w / 2, y - h / 2, w, h, col, ec=C_ACCENT, lw=1.6)
    if sub:
        text(x, y + 1.2, label, size=9.8, weight="bold")
        text(x, y - 1.6, sub, size=8.2, color=C_DIM)
    else:
        text(x, y, label, size=9.8, weight="bold")

# start
box(38, 49.5, 24, 5.0, C_BLUE, ec=C_ACCENT, lw=1.6)
text(50, 52.0, "수집 계층 선택", size=11.5, weight="bold", color=C_ACCENT)

# Q1
decision(50, 42.5, 28, 5.2, "백엔드가 Grafana LGTM+ 스택?")
arrow(50, 47.0, 50, 45.1, color=C_EDGE, lw=1.6)

# Q1 No -> Collector1 (right)
result(84, 42.5, 24, 6.4, "OTel Collector", C_BROWN, sub="순수 · 벤더 중립")
arrow(64, 42.5, 72, 42.5, color=C_ACCENT, lw=2.0)
text(68, 44.3, "No", size=9, color=C_ORANGE, weight="bold")

# Q1 Yes -> Q2
decision(50, 33.0, 28, 5.2, "벤더 락인 회피가 최우선 정책?")
arrow(50, 39.9, 50, 35.6, color=C_ACCENT, lw=2.0)
text(53.2, 37.8, "Yes", size=9, color=C_ORANGE, weight="bold")

# Q2 Yes -> Collector2 (right)
result(84, 33.0, 24, 6.4, "OTel Collector", C_BROWN,
       sub="+ Grafana OTLP 익스포터")
arrow(64, 33.0, 72, 33.0, color=C_ACCENT, lw=2.0)
text(68, 34.8, "Yes", size=9, color=C_ORANGE, weight="bold")

# Q2 No -> Q3
decision(50, 23.5, 28, 5.4, "clustering·프로파일\n네이티브 지원 필요?")
arrow(50, 30.4, 50, 26.2, color=C_ACCENT, lw=2.0)
text(53.2, 28.3, "No", size=9, color=C_ORANGE, weight="bold")

# Q3 Yes -> Alloy (left)
result(19, 23.5, 22, 6.4, "Alloy", C_GREEN)
arrow(36, 23.5, 30, 23.5, color=C_ACCENT, lw=2.0)
text(33, 25.3, "Yes", size=9, color=C_ORANGE, weight="bold")

# Q3 No -> Either (down)
result(50, 13.5, 30, 6.4, "둘 다 가능", C_PURPLE, sub="팀 숙련도로 결정")
arrow(50, 20.8, 50, 16.7, color=C_ACCENT, lw=2.0)
text(53.2, 18.8, "No", size=9, color=C_ORANGE, weight="bold")

# bottom
text(50, 6.0, "Grafana 스택 + clustering/프로파일 → Alloy  ·  멀티 벤더·락인 회피 → 순수 Collector",
     size=10.5, color=C_ACCENT, weight="bold")
text(50, 3.0, "정답이 하나로 갈리지 않으면 팀이 이미 익숙한 구성 언어(YAML vs Alloy 구문)로 판단",
     size=9, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "30-selection-tree.png")
