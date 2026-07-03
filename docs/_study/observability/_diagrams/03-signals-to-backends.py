"""CH03 신호별 전담 백엔드와 Grafana 통합 (LGTM+ 스택) (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "Grafana LGTM+ 스택 — 신호 → 전담 백엔드 → 통합", size=20, weight="bold")
text(50, 56.6, "신호마다 전담 백엔드가 있고, Grafana가 이들을 하나의 화면에서 묶는다", size=12, color=C_DIM)

# ================= 왼쪽: 신호 =================
box(3, 8, 18, 44, C_GRAY)
text(12, 49.4, "신호", size=13, weight="bold")
signals = [("메트릭", 41), ("로그", 31), ("트레이스", 21), ("프로파일", 11)]
sig_colors = [C_BLUE, C_GREEN, C_BROWN, "#4a3d63"]
for (name, yy), c in zip(signals, sig_colors):
    box(5, yy - 2.6, 14, 5.2, c)
    text(12, yy, name, size=11, weight="bold",
         color="#e7dcff" if c == "#4a3d63" else C_TEXT)

# ================= 가운데: 백엔드 =================
box(30, 8, 40, 44, C_GRAY)
text(50, 49.4, "백엔드", size=13, weight="bold")

# Prometheus + Mimir (메트릭 2단)
box(32.5, 40.5, 16, 6.5, C_BLUE)
text(40.5, 44.6, "Prometheus", size=10, weight="bold")
text(40.5, 42.0, "스크레이프+룰 평가", size=7.8, color=C_DIM)
box(51.5, 40.5, 16, 6.5, C_BLUE, ec=C_ACCENT, lw=1.5)
text(59.5, 44.6, "Mimir", size=10, weight="bold")
text(59.5, 42.0, "장기 저장·수평 확장", size=7.8, color=C_DIM)
arrow(48.5, 43.7, 51.5, 43.7, color=C_ORANGE, lw=2.0)
text(50, 48.2, "remote_write", size=7.2, color=C_ORANGE, weight="bold")

# Loki, Tempo, Pyroscope
for name, yy, c, dim in [
    ("Loki", 30.5, C_GREEN, "라벨 인덱싱 로그"),
    ("Tempo", 21.5, C_BROWN, "트레이스 저장"),
    ("Pyroscope", 12.5, "#4a3d63", "연속 프로파일"),
]:
    box(42, yy - 2.8, 26, 5.6, c)
    tc = "#e7dcff" if c == "#4a3d63" else C_TEXT
    text(50, yy + 0.6, name, size=10.5, weight="bold", color=tc)
    text(50, yy - 1.4, dim, size=8, color=C_DIM)

# 신호 -> 백엔드 화살표
arrow(21, 41, 32.5, 43.7, color=C_ACCENT, lw=1.8)          # 메트릭 -> Prometheus
arrow(21, 31, 42, 30.5, color=C_ACCENT, lw=1.8)            # 로그 -> Loki
arrow(21, 21, 42, 21.5, color=C_ACCENT, lw=1.8)            # 트레이스 -> Tempo
arrow(21, 11, 42, 12.5, color=C_ACCENT, lw=1.8)            # 프로파일 -> Pyroscope

# ================= 오른쪽: Grafana =================
box(78, 20, 19, 20, C_GRAY, ec=C_ACCENT, lw=2.0)
text(87.5, 35.4, "Grafana", size=13.5, weight="bold", color=C_ACCENT)
text(87.5, 30.2, "질의\n시각화\n상관관계", size=10.5, color="#d4dae0")

# 백엔드 -> Grafana
for yy in (43.7, 30.5, 21.5, 12.5):
    src = 67.5 if yy == 43.7 else 68
    arrow(src, yy, 78, 30, color=C_VIOLET, lw=1.6, rad=0.05)

# bottom
text(50, 4.4, "Prometheus(스크레이프·룰) + Mimir(장기 저장) 2단 구조  ·  Loki·Tempo·Mimir는 동일 오브젝트 스토리지 아키텍처 공유",
     size=9.5, color=C_DIM, style="italic")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="신호 → 백엔드 수집"),
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="remote_write (Prometheus → Mimir)"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, label="백엔드 → Grafana 질의"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.005),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

save(fig, "03-signals-to-backends.png")
