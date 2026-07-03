"""CH18 LogQL 파이프라인 — 셀렉터 → 라인 필터 → 파서 → 추출 필드 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE)

fig, ax = new_fig(w=14, h=5.6, ymax=38)
box, text, arrow = make_helpers(ax)

text(50, 34.5, "LogQL 파서 파이프라인", size=18, weight="bold")
text(50, 31.2, "스트림을 좁히고 라인을 거른 뒤, 파서로 구조화된 필드로 분해", size=11, color=C_DIM)

stages = [
    (13, C_BLUE, "Stream Selector", '{app="checkout"}', "대상 스트림 지정"),
    (37, C_GREEN, "Line Filter", '|= "error"', "텍스트로 라인 거름"),
    (61, C_GRAY, "Parser", "| json", "필드로 분해"),
    (85, C_BROWN, "추출된 필드", "status, path,\nduration ...", "라벨처럼 다룸"),
]
for cx, fc, t, code, desc in stages:
    box(cx - 10.5, 11, 21, 13, fc, ec=(C_ACCENT if t == "Parser" else C_EDGE),
        lw=(1.8 if t == "Parser" else 1.4))
    text(cx, 21.5, t, size=11, weight="bold")
    text(cx, 17.8, code, size=9, color=C_ACCENT)
    text(cx, 13.5, desc, size=8.3, color=C_DIM)

for cx in (25, 49, 73):
    arrow(cx - 1.5, 17.5, cx + 1.5, 17.5, color=C_ORANGE, lw=2.4)

text(50, 5.5, "파서 실패 라인엔 __error__ 라벨 — `| json | __error__=\"\"`로 제외하거나 골라낼 수 있다",
     size=9.5, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "18-parser-pipeline.png")
