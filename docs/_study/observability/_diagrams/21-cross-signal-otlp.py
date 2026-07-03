"""CH21 교차 신호 — OTel SDK → OTLP → 신호별 백엔드 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig(ymax=56)
box, text, arrow = make_helpers(ax)


def cbox(cx, cy, bw, bh, fc, **kw):
    box(cx - bw / 2, cy - bh / 2, bw, bh, fc, **kw)


# ---- Title ----
text(50, 53.4, "OpenTelemetry — 교차 신호(Cross-Signal)와 단일 프로토콜 OTLP", size=18, weight="bold")
text(50, 50.4, "traces·metrics·logs 세 신호를 하나의 계측 라이브러리·리소스 모델·전송 프로토콜로 다룬다", size=11, color=C_DIM)

# ===== left: application (OTel SDK) =====
box(4, 8, 24, 38, C_GRAY, ec=C_ACCENT, lw=1.8)
text(16, 43, "애플리케이션 (OTel SDK)", size=12, weight="bold", color=C_ACCENT)
signals = [("Traces", C_BROWN, 34), ("Metrics", C_BLUE, 25), ("Logs", C_GREEN, 16)]
for name, c, cy in signals:
    cbox(16, cy, 18, 6, c)
    text(16, cy, name, size=11.5, weight="bold")

# ===== center: OTLP =====
box(38, 14, 24, 26, C_BROWN, ec=C_ORANGE, lw=1.8)
text(50, 37, "OTLP", size=13, weight="bold", color=C_ORANGE)
text(50, 34, "단일 프로토콜", size=9.5, color=C_DIM)
cbox(50, 25, 18, 8, "#241d1a")
text(50, 26.6, "gRPC / HTTP", size=11, weight="bold")
text(50, 23.6, "+ Protobuf", size=9, color=C_DIM)

# ===== right: backends =====
box(72, 8, 24, 38, C_GRAY)
text(84, 43, "백엔드 (신호별 저장소)", size=12, weight="bold")
backs = [("Tempo", C_BROWN, 34, "트레이스"), ("Prometheus / Mimir", C_BLUE, 25, "메트릭"),
         ("Loki", C_GREEN, 16, "로그")]
for name, c, cy, d in backs:
    cbox(84, cy, 18, 6, c)
    text(84, cy + 0.9, name, size=10.5, weight="bold")
    text(84, cy - 1.5, d, size=8.5, color=C_DIM)

# arrows: signals -> OTLP
for _, _, cy in signals:
    arrow(25, cy, 38, 25 + (cy - 25) * 0.15, color=C_ACCENT, lw=1.8, rad=0.0)
# OTLP -> backends
for _, _, cy, _ in backs:
    arrow(62, 25 + (cy - 25) * 0.15, 72, cy, color=C_ORANGE, lw=1.8)

# bottom
text(50, 4.4, "계측 코드를 한 번 작성하면 백엔드를 Tempo→다른 시스템, 온프레미스→SaaS로 바꿔도 코드 무수정",
     size=9.5, color=C_ACCENT, weight="bold")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.2, label="SDK → OTLP 내보내기"),
    Line2D([0], [0], color=C_ORANGE, lw=2.2, label="OTLP → 신호별 백엔드"),
]
ax.legend(handles=leg, loc="lower center", bbox_to_anchor=(0.5, 0.09),
          ncol=2, fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "21-cross-signal-otlp.png")
