"""CH18 LogQL 성능 — 단계별 비용 순서 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE)

fig, ax = new_fig(w=15, h=6.2, ymax=42)
box, text, arrow = make_helpers(ax)

text(50, 38.0, "LogQL 성능 — 앞단에서 데이터를 줄일수록 저렴", size=18, weight="bold")
text(50, 34.8, "단계마다 비용이 크게 다르다 — 저렴한 단계로 먼저 후보를 줄인 뒤 비싼 단계 적용", size=10.5, color=C_DIM)

# color codes cost: green cheap → red expensive
stages = [
    ("1. Stream Selector", "인덱스 조회", "매우 저렴", "#2e5a3f"),
    ("2. Line Filter |= !=", "바이트 비교", "저렴", "#3a5a3f"),
    ("3. Line Filter |~ !~", "정규식", "중간", "#5a5638"),
    ("4. Parser", "json/logfmt/\npattern/regexp", "비쌈", "#5a4638"),
    ("5. Label Filter / 집계", "파싱 결과 위\n연산", "파싱 후", C_BLUE),
]
n = len(stages)
w = 16.5
gap = 2.0
total = n * w + (n - 1) * gap
x0 = (100 - total) / 2
for i, (t, d, cost, fc) in enumerate(stages):
    cx = x0 + i * (w + gap) + w / 2
    box(cx - w / 2, 12, w, 15, fc)
    text(cx, 24.2, t, size=10, weight="bold")
    text(cx, 20.0, d, size=8.6, color="#d4dae0")
    box(cx - 5, 13.2, 10, 3.2, "#0f1216")
    text(cx, 14.8, cost, size=8.6, color=C_ACCENT, weight="bold")
    if i < n - 1:
        ax_cx = cx + w / 2
        arrow(ax_cx + 0.2, 19.5, ax_cx + gap - 0.2, 19.5, color=C_ORANGE, lw=2.4)

text(50, 7.0, "파서보다 라인 필터를 먼저 · 스트림 셀렉터를 최대한 좁히기 · 정규식은 최후 수단",
     size=10, color=C_ACCENT, weight="bold")
text(50, 3.5, "왼쪽(저렴) → 오른쪽(비쌈) : 청크를 훑기 전에 후보 라인을 줄여야 전체 비용이 준다",
     size=9, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "18-performance-stages.png")
