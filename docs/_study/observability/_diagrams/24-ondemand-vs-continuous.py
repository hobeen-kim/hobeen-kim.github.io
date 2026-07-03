"""CH24 온디맨드 vs 연속 프로파일링 — 사후 분석 가능 여부 대비 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "온디맨드 vs 연속(continuous) 프로파일링", size=20, weight="bold")
text(50, 56.6, "핵심 차이는 '과거를 프로파일링할 수 있는가' — 사후 분석(post-hoc analysis) 가능 여부",
     size=12, color=C_DIM)

C_RED = "#5a3838"

# ================= left: on-demand =================
box(3, 8, 44, 45, C_GRAY, ec="#8a5a5a", lw=1.8)
text(25, 50.4, "온디맨드 프로파일링", size=14, weight="bold", color="#e6a3a3")
text(25, 48.0, "문제가 의심될 때만 수동으로 짧게 캡처", size=9.5, color=C_DIM, style="italic")

steps_l = [
    ("장애 발생", "새벽 지연 스파이크 등", C_RED),
    ("원인 의심 후\n수동으로 프로파일러 트리거", "그제서야 프로파일러 켬", C_BROWN),
    ("이미 상황 종료\n원인 재현 불가", "그 순간의 스택은 영원히 소실", C_RED),
]
for i, (t, d, c) in enumerate(steps_l):
    yy = 41 - i * 12.5
    box(8, yy - 4.4, 34, 8.0, c)
    text(25, yy + 0.4, t, size=11, weight="bold")
    text(25, yy - 3.0, d, size=8.3, color=C_DIM)
    if i < 2:
        arrow(25, yy - 4.4, 25, yy - 8.1, color="#c08080", lw=2.2)

# ================= right: continuous =================
box(53, 8, 44, 45, C_GRAY, ec=C_ACCENT, lw=1.8)
text(75, 50.4, "연속 프로파일링", size=14, weight="bold", color=C_ACCENT)
text(75, 48.0, "낮은 오버헤드 에이전트를 프로덕션에 상시 구동", size=9.5, color=C_DIM, style="italic")

steps_r = [
    ("24/7 상시 샘플링", "메트릭 스크레이핑하듯 계속 수집", C_GREEN),
    ("타임스탬프와 함께\n지속 저장", "시점별 프로파일 축적", C_BLUE),
    ("장애 발생", "이후에도 그 시각을 그대로 보유", C_BROWN),
    ("과거 시점 프로파일 조회\n(사후 분석)", "미리 질문을 준비하지 않아도 됨", C_GREEN),
]
for i, (t, d, c) in enumerate(steps_r):
    yy = 42.5 - i * 9.3
    box(58, yy - 3.3, 34, 6.2, c)
    text(75, yy + 0.4, t, size=10.5, weight="bold")
    text(75, yy - 2.2, d, size=8.3, color=C_DIM)
    if i < 3:
        arrow(75, yy - 3.3, 75, yy - 6.1, color=C_ACCENT, lw=2.2)

# bottom
text(50, 4.6, "known-unknowns의 한계: 예상해서 켜둬야만 답이 나온다  vs  사후에도 그 시각을 그대로 조회",
     size=10, color=C_ACCENT, weight="bold")
text(50, 2.2, "연속 프로파일링은 '미리 질문을 준비하지 않아도 되는' 관측성의 핵심 가치와 같은 구조다",
     size=9, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "24-ondemand-vs-continuous.png")
