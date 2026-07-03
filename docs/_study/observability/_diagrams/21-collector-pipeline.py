"""CH21 Collector 파이프라인 — receiver → processor → exporter (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(ymax=58)
box, text, arrow = make_helpers(ax)


def cbox(cx, cy, bw, bh, fc, **kw):
    box(cx - bw / 2, cy - bh / 2, bw, bh, fc, **kw)


def chip(cx, cy, t, d, c, bw=22, bh=7):
    cbox(cx, cy, bw, bh, c)
    text(cx, cy + 1.3, t, size=10.5, weight="bold")
    text(cx, cy - 1.6, d, size=8, color=C_DIM)


# ---- Title ----
text(50, 55.4, "OpenTelemetry Collector — receiver → processor → exporter 파이프라인", size=17, weight="bold")
text(50, 52.4, "신호별로 파이프라인을 구성하고 하나의 receiver를 여러 파이프라인이 공유할 수 있다", size=11, color=C_DIM)

# ===== group boxes =====
box(3, 6, 24, 43, C_GRAY)
text(15, 46, "Receivers", size=13, weight="bold", color=C_ACCENT)
box(37, 6, 26, 43, C_GRAY)
text(50, 46, "Processors  (적용 순서)", size=13, weight="bold", color=C_ORANGE)
box(73, 6, 24, 43, C_GRAY)
text(85, 46, "Exporters", size=13, weight="bold", color=C_GREEN)

# receivers
recv = [("otlp", "gRPC :4317 / HTTP :4318", 39), ("prometheus", "스크레이프", 29),
        ("filelog", "파일 tail", 19)]
for t, d, cy in recv:
    chip(15, cy, t, d, C_BLUE, bw=20)

# processors (flow order top→bottom)
proc = [("memory_limiter", "OOM 방지", 40), ("attributes", "속성 가공", 30),
        ("tail_sampling", "trace 단위 샘플링", 20), ("batch", "배치 전송", 10)]
for t, d, cy in proc:
    chip(50, cy, t, d, C_BROWN, bw=24)
# chain arrows
for i in range(len(proc) - 1):
    arrow(50, proc[i][2] - 3.5, 50, proc[i + 1][2] + 3.5, color=C_ORANGE, lw=2.0)

# exporters
exp = [("otlp", "Tempo", 39), ("prometheusremotewrite", "Mimir", 29), ("loki", "Loki", 19)]
for t, d, cy in exp:
    chip(85, cy, t, d, C_GREEN, bw=22)

# receivers -> memory_limiter (entry)
for _, _, cy in recv:
    arrow(25, cy, 38, 40, color=C_ACCENT, lw=1.7, rad=-0.12)

# batch -> exporters
for _, _, cy in exp:
    arrow(62, 10, 74, cy, color=C_GREEN, lw=1.7, rad=0.12)

# bottom
text(50, 2.4, "traces 예: otlp → memory_limiter → attributes → tail_sampling → batch → otlp/Tempo",
     size=9.5, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.2, label="수신 (receiver → 파이프라인)"),
    Line2D([0], [0], color=C_ORANGE, lw=2.2, label="가공 순서 (processor 체인)"),
    Line2D([0], [0], color=C_GREEN, lw=2.2, label="내보내기 (batch → exporter)"),
]
ax.legend(handles=leg, loc="lower center", bbox_to_anchor=(0.5, 0.055),
          ncol=3, fontsize=8, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "21-collector-pipeline.png")
