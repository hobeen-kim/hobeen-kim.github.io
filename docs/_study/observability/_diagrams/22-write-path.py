"""CH22 쓰기 경로 — distributor → ingester → blocks (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_PURPLE, C_VIOLET)

fig, ax = new_fig(ymax=56)
box, text, arrow = make_helpers(ax)


def cbox(cx, cy, bw, bh, fc, **kw):
    box(cx - bw / 2, cy - bh / 2, bw, bh, fc, **kw)


def node(cx, cy, t, d, c, bw=16, bh=7):
    cbox(cx, cy, bw, bh, c)
    text(cx, cy + 1.3, t, size=10, weight="bold")
    text(cx, cy - 1.6, d, size=7.8, color=C_DIM)


# ---- Title ----
text(50, 53.4, "Tempo 쓰기 경로 — distributor → ingester → 오브젝트 스토리지", size=18, weight="bold")
text(50, 50.4, "같은 trace의 span은 trace_id 해싱으로 항상 같은 ingester로 라우팅 → 온전히 조립", size=11, color=C_DIM)

# nodes
node(9, 30, "애플리케이션", "/ Collector (OTLP)", C_BLUE, bw=15)
node(26, 30, "Distributor", "trace_id 기준 해싱", C_GREEN, bw=17)
node(44, 42, "Ingester 1", "", C_BROWN, bw=15, bh=5.5)
node(44, 30, "Ingester 2", "", C_ORANGE, bw=15, bh=5.5)
node(44, 18, "Ingester 3", "", C_BROWN, bw=15, bh=5.5)

# ING2 internals
node(64, 40, "WAL", "로컬 디스크 · 재시작 유실 방지", C_GRAY, bw=18)
node(64, 27, "Head Block", "메모리", C_PURPLE, bw=15)
node(82, 27, "Complete Block", "잘라내기(cut)", C_GREEN, bw=16)
node(82, 13, "오브젝트 스토리지", "S3 / GCS / Azure", C_BLUE, bw=18)

# arrows
arrow(16.5, 30, 17.5, 30, color=C_ACCENT, lw=2.0)
for cy in (42, 30, 18):
    arrow(34.5, 30, 36.5, cy, color=C_ACCENT, lw=1.8, rad=0.0)
arrow(51.5, 30, 55, 39, color=C_ORANGE, lw=1.8)
arrow(51.5, 30, 56.5, 27.6, color=C_ORANGE, lw=1.8)
arrow(71.5, 27, 74, 27, color=C_ACCENT, lw=1.9)
text(76.5, 30, "cut 주기 도래", size=8, color=C_ACCENT)
arrow(82, 23.5, 82, 16.5, color=C_ACCENT, lw=1.9)
text(88, 20, "flush", size=8.5, color=C_ACCENT, weight="bold")

# bottom
text(50, 4.2, "최근 trace는 아직 스토리지에 없고 ingester 메모리에만 존재 — 읽기 경로가 ingester와 스토리지 양쪽을 조회하는 이유",
     size=9.5, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "22-write-path.png")
