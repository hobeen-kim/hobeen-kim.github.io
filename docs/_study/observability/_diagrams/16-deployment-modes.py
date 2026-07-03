"""CH16 Loki 배포 모드 — monolithic / simple scalable / microservices (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

text(50, 59.0, "Loki 배포 모드 — 같은 바이너리, -target 분리", size=20, weight="bold")
text(50, 56.0, "규모에 맞춰 컴포넌트를 얼마나 쪼개느냐의 선택", size=12, color=C_DIM)

# Monolithic (left)
box(3, 12, 28, 40, C_GRAY)
text(17, 49.0, "Monolithic", size=14, weight="bold", color=C_ACCENT)
text(17, 46.4, "단일/소규모", size=9.5, color=C_DIM)
box(6, 28, 22, 14, "#1b232a")
text(17, 37.5, "단일 프로세스", size=12, weight="bold")
text(17, 33.5, "모든 컴포넌트\n함께 실행", size=10, color=C_DIM)
text(17, 21.0, "설정 단순 · 로컬/소규모\n읽기·쓰기 독립 스케일 불가",
     size=9, color="#d4dae0")

# Simple Scalable (center)
box(35, 12, 30, 40, C_GREEN, ec=C_ACCENT, lw=1.8)
text(50, 49.0, "Simple Scalable", size=14, weight="bold", color=C_ACCENT)
text(50, 46.4, "프로덕션 권장 기본", size=9.5, color=C_DIM)
for i, (t, d) in enumerate([
    ("read 타깃", "query-frontend + querier"),
    ("write 타깃", "distributor + ingester"),
    ("backend 타깃", "compactor + ruler + index-gateway"),
]):
    yy = 41.5 - i * 6.2
    box(37.5, yy - 2.4, 25, 4.8, "#1d2b24")
    text(50, yy + 0.6, t, size=10.5, weight="bold")
    text(50, yy - 1.3, d, size=8.3, color=C_DIM)
text(50, 16.5, "운영 복잡도와 확장성의 균형점", size=9, color="#d4dae0")

# Microservices (right)
box(69, 12, 28, 40, C_BROWN)
text(83, 49.0, "Microservices", size=14, weight="bold", color=C_ACCENT)
text(83, 46.4, "초대형 멀티테넌시", size=9.5, color=C_DIM)
comps = ["distributor", "ingester", "querier",
         "query-frontend", "compactor", "index-gateway"]
for i, c in enumerate(comps):
    col = i % 2
    row = i // 2
    bx = 71.5 + col * 12.3
    by = 39.0 - row * 6.0
    box(bx, by - 2.1, 11.5, 4.2, "#241d1a")
    text(bx + 5.75, by, c, size=8.3, weight="bold")
text(83, 20.5, "컴포넌트별 독립 오토스케일\n운영 부담 가장 큼", size=9, color="#d4dae0")

text(50, 7.5, "monolithic → simple scalable → microservices : 규모가 커질수록 더 잘게 분리하고 독립 확장",
     size=10.5, color=C_ACCENT, weight="bold")
text(50, 4.2, "세 모드 모두 동일한 Loki 바이너리를 -target 플래그로 컴포넌트를 켜고 끈 것",
     size=9.5, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "16-deployment-modes.png")
