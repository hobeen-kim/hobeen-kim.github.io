"""CH31 Grafana 데이터소스 연결 — 5개 백엔드 → Query Editor → 패널 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_PURPLE)

fig, ax = new_fig(w=14, h=8.6, ymax=56)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 53.0, "Grafana 데이터소스 연결 — 5개 백엔드가 하나의 패널 시스템 공유", size=17.5, weight="bold")
text(50, 50.0, "프로토콜은 백엔드마다 다르지만 Grafana 안에서는 동일한 패널·변수 시스템으로 수렴",
     size=11, color=C_DIM)

# left group: datasources
box(4, 8, 34, 38, C_GRAY)
text(21, 43.4, "Grafana 데이터소스", size=12.5, weight="bold", color=C_ACCENT)

ds = [
    ("Prometheus", "type: prometheus", C_BLUE),
    ("Mimir", "Prometheus 호환 API · 테넌트 헤더", C_BLUE),
    ("Loki", "type: loki · maxLines", C_GREEN),
    ("Tempo", "type: tempo", C_BROWN),
    ("Pyroscope", "grafana-pyroscope-datasource", C_PURPLE),
]
for i, (t, d, col) in enumerate(ds):
    yy = 39.0 - i * 6.3
    box(6, yy - 2.5, 30, 5.0, col)
    text(21, yy + 0.5, t, size=10.5, weight="bold")
    text(21, yy - 1.5, d, size=8, color=C_DIM)

# center group: Grafana
box(52, 18, 26, 20, C_GREEN, ec=C_ACCENT, lw=2.0)
text(65, 35.4, "Grafana", size=13, weight="bold", color=C_ACCENT)
box(54, 26.5, 22, 5.5, "#1d2b24")
text(65, 29.2, "Query Editor", size=11, weight="bold")
box(54, 19.5, 22, 5.5, "#1d2b24")
text(65, 22.2, "패널 렌더링", size=11, weight="bold")
arrow(65, 26.5, 65, 25.0, color=C_ACCENT, lw=2.0)

# datasources -> query editor
for i in range(len(ds)):
    yy = 39.0 - i * 6.3
    arrow(38, yy, 54, 29.2, color=C_ACCENT, lw=1.5, rad=0.02)

# right note
box(84, 22, 13, 12, C_BLUE)
text(90.5, 30.0, "동일 UI", size=10.5, weight="bold")
text(90.5, 27.0, "패널 · 변수", size=8.5, color=C_DIM)
text(90.5, 24.6, "시스템 공유", size=8.5, color=C_DIM)
arrow(78, 28, 84, 28, color=C_ACCENT, lw=2.0)

# bottom
text(50, 4.5, "운영 환경에서는 UI 대신 provisioning YAML로 데이터소스를 파일 기반 관리하는 것이 표준",
     size=10, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "31-datasources.png")
