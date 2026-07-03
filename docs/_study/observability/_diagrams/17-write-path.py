"""CH17 쓰기 경로 시퀀스 — distributor → ingester → 오브젝트 스토리지 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

text(50, 59.0, "Loki 쓰기 경로 (write path)", size=20, weight="bold")
text(50, 56.0, "클라이언트 → Distributor → Ingester → 오브젝트 스토리지", size=12, color=C_DIM)

# lifelines
actors = [
    (13, "클라이언트", "Alloy / Promtail", C_BLUE),
    (39, "Distributor", "stateless", C_GRAY),
    (65, "Ingester", "stateful · WAL", C_GREEN),
    (90, "오브젝트\n스토리지", "S3 / GCS", C_BROWN),
]
for x, name, sub, fc in actors:
    box(x - 9, 49, 18, 5.4, fc, ec=C_ACCENT, lw=1.5)
    text(x, 52.0, name, size=11, weight="bold")
    text(x, 49.9, sub, size=8, color=C_DIM)
    ax.plot([x, x], [7, 49], color=C_EDGE, lw=1.2, ls="--", zorder=1)

def hmsg(x1, x2, y, label, color=C_ACCENT):
    arrow(x1, y, x2, y, color=color, lw=2.0)
    text((x1 + x2) / 2, y + 1.4, label, size=8.8, color=color)

def selfmsg(x, y, label, color=C_ORANGE):
    box(x + 1.5, y - 1.5, 22, 3.0, "#26313a", ec=color, lw=1.2)
    text(x + 12.5, y, label, size=8.6, color=C_TEXT)

# time-ordered steps (top → bottom)
hmsg(13, 39, 45.5, "POST /loki/api/v1/push (로그 배치)", "#7fb0c8")
selfmsg(39, 41.0, "검증 + rate limit 체크")
selfmsg(39, 37.0, "라벨 해싱 → 담당 ingester 결정")
hmsg(39, 65, 32.5, "스트림 라우팅 (복제 factor만큼)", C_ORANGE)
selfmsg(65, 28.0, "WAL에 기록")
selfmsg(65, 24.0, "메모리 청크에 append")

# note over ingester
box(51, 16.2, 28, 5.4, "#3a3320", ec=C_ORANGE, lw=1.3)
text(65, 20.0, "청크가 가득 차거나", size=8.8, color="#f0d9a8")
text(65, 17.6, "유휴 시간 초과 시", size=8.8, color="#f0d9a8")

hmsg(65, 90, 13.0, "압축된 청크 flush", C_ACCENT)
hmsg(65, 90, 9.0, "인덱스 항목 업로드", C_ACCENT)

text(50, 3.5, "distributor는 스테이트리스, ingester는 WAL을 갖는 상태 저장 컴포넌트 — 이 차이가 운영 방식을 가른다",
     size=10, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "17-write-path.png")
