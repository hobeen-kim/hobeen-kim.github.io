"""CH08 Exporter 패턴 — 브릿지 구조 다이어그램 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "Exporter 패턴 — 계측 불가능한 대상의 브릿지", size=20, weight="bold")
text(50, 56.6, "대상 시스템  →  Exporter(브릿지)가 대신 읽어 /metrics로 번역  →  Prometheus가 스크레이프",
     size=12, color=C_DIM)

# ================= left: targets =================
box(4, 8, 26, 44, C_GRAY)
text(17, 49.4, "계측 불가능한 대상", size=13, weight="bold")
text(17, 47.2, "소스 수정 불가 · 외부 관측 대상", size=9, color=C_DIM, style="italic")
targets = [
    ("OS / 커널", "/proc · /sys 파싱"),
    ("MySQL", "DB 서버 상태"),
    ("HTTP 엔드포인트", "외부 서비스 (블랙박스)"),
]
rows = [42, 30, 18]
for (t, d), yc in zip(targets, rows):
    box(6, yc - 3, 22, 6, "#1b232a")
    text(17, yc + 0.9, t, size=10.5)
    text(17, yc - 1.4, d, size=8, color=C_DIM)

# ================= center: exporters =================
box(38, 8, 26, 44, C_GREEN, ec=C_ACCENT, lw=2.0)
text(51, 49.4, "Exporter (브릿지)", size=13, weight="bold", color=C_ACCENT)
text(51, 47.2, "대상을 읽어 Prometheus 형식으로 번역", size=9, color=C_DIM, style="italic")
exporters = [
    ("node-exporter", "CPU·메모리·디스크·네트워크"),
    ("mysqld_exporter", "SHOW GLOBAL STATUS 질의"),
    ("blackbox_exporter", "요청 시점 대상 프로빙"),
]
for (t, d), yc in zip(exporters, rows):
    box(40, yc - 3, 22, 6, "#1d2b24")
    text(51, yc + 0.9, t, size=10.5)
    text(51, yc - 1.4, d, size=8, color=C_DIM)

# ================= right: prometheus =================
box(72, 20, 24, 22, C_BLUE)
text(84, 37.4, "Prometheus", size=15, weight="bold")
text(84, 33.8, "pull 기반 수집", size=9.5, color=C_DIM)
text(84, 27.5, "세 Exporter의\n/metrics · /probe 를\n주기적으로 스크레이프", size=9, color="#d4dae0")

# ---- arrows: target -> exporter ----
labels_te = ["", "SQL 질의", "probe (HTTP/TCP/ICMP)"]
for yc, lbl in zip(rows, labels_te):
    arrow(28, yc, 40, yc, color=C_ORANGE, lw=2.2)
    if lbl:
        text(34, yc + 1.7, lbl, size=7.6, color=C_ORANGE)

# ---- arrows: exporter -> prometheus ----
endpts = [(42, "/metrics"), (30, "/metrics"), (18, "/probe")]
for yc, lbl in endpts:
    ty = 34 if yc == 42 else (30 if yc == 30 else 26)
    arrow(64, yc, 72, ty, color=C_ACCENT, lw=2.0, rad=0.06)
    text(68, (yc + ty) / 2 + 1.6, lbl, size=7.6, color=C_ACCENT, weight="bold")

# bottom
text(50, 4.8, "소스 코드를 통제할 수 있으면 직접 계측(화이트박스)이 항상 우선 — Exporter는 못 고치는 시스템·외부 관측용",
     size=10, color=C_ACCENT, weight="bold")
text(50, 2.4, "node-exporter는 DaemonSet 상시 배포 · blackbox는 자체 메트릭 없이 지정 대상을 요청 시점에 프로빙",
     size=9, color=C_DIM, style="italic")

leg = [
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="대상 → Exporter 읽기"),
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="Exporter → Prometheus 스크레이프"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.06),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "08-exporter-pattern.png")
