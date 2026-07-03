"""CH28 Alloy 프로세스 내부 구조 — 구문 + 실행 엔진 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_PURPLE)

fig, ax = new_fig(w=14, h=8.6, ymax=56)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 53.0, "Alloy 프로세스 — 하나의 바이너리 안의 구성", size=19, weight="bold")
text(50, 50.0, "Alloy 구문이 OTel Collector 엔진 + Prometheus/Loki/Pyroscope 클라이언트를 한 프로세스에 묶음",
     size=11, color=C_DIM)

# outer Alloy process box
box(6, 6, 88, 39, "#141a1f", ec=C_ACCENT, lw=2.0)
text(50, 42.2, "Alloy 프로세스", size=14, weight="bold", color=C_ACCENT)

# Alloy syntax box (top)
box(30, 33.5, 40, 6.4, C_PURPLE)
text(50, 37.7, "Alloy 구문", size=12, weight="bold")
text(50, 35.0, "구 River · 컴포넌트 그래프", size=8.8, color=C_DIM)

# Core engine group
box(9, 10.5, 82, 18.0, C_GRAY)
text(50, 26.4, "실행 엔진", size=12, weight="bold", color=C_TEXT)

cores = [
    ("OpenTelemetry\nCollector 코드베이스", "otelcol.*", C_BLUE),
    ("Prometheus\n클라이언트", "prometheus.*", C_GREEN),
    ("Loki\n클라이언트", "loki.*", C_BROWN),
    ("Pyroscope\n클라이언트", "pyroscope.*", "#3d3a5a"),
]
cw = 18.5
xs = [11.5, 31.5, 51.5, 71.5]
for (t, pre, col), x in zip(cores, xs):
    box(x, 12.0, cw, 11.5, col)
    text(x + cw / 2, 19.7, t, size=9.3, weight="bold")
    text(x + cw / 2, 15.6, pre, size=9, color=C_ACCENT, style="italic")

# syntax -> each core
for x in xs:
    arrow(50, 33.5, x + cw / 2, 23.5, color=C_ORANGE, lw=1.8, rad=0.0)

# bottom
text(50, 3.0, "Alloy = Collector를 대체하는 다른 제품이 아니라, Collector 위에 네이티브 지원과 통합 구문을 얹은 상위 계층",
     size=9.5, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "28-alloy-process.png")
