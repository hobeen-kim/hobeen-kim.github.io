"""CH38 Prometheus OOM 대응 흐름 다이어그램 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "Prometheus OOM Kill — 진단에서 재발 방지까지", size=20, weight="bold")
text(50, 56.6, "head block 급증 여부를 먼저 확인 → 즉각 조치(임시)와 근본 조치(계측)를 분리",
     size=12, color=C_DIM)

def node(cx, cy, w, h, title, sub, fc, ec=C_EDGE, tsize=11):
    box(cx - w/2, cy - h/2, w, h, fc, ec=ec, lw=1.6)
    if sub:
        text(cx, cy + h*0.16, title, size=tsize, weight="bold")
        text(cx, cy - h*0.22, sub, size=8.2, color=C_DIM)
    else:
        text(cx, cy, title, size=tsize, weight="bold")

# 시작
node(50, 51, 34, 6.5, "Prometheus OOM Kill 발생", "process_resident_memory_bytes > limit", C_BROWN, ec=C_ORANGE)

# 진단
node(50, 41.5, 30, 6.5, "prometheus_tsdb_head_series 추세 확인", "현재 활성 시계열 수", C_GRAY, ec=C_ACCENT)

# 분기: 급증 / 완만
node(26, 31, 24, 6.5, "topk(job/metric)로 폭증 원인 좁히기", "어떤 job·메트릭이 시계열 폭증?", C_BLUE)
node(78, 31, 22, 6.5, "단순 용량 부족", "→ 리소스 증설 검토", C_GRAY)

# 즉각 조치
node(26, 22, 24, 6.0, "즉각 조치 (임시)", "metricRelabelings drop · labeldrop", C_GREEN)
# 재시작
node(26, 13.5, 24, 6.0, "Prometheus 재시작", "head block 초기화", C_GRAY)

# 근본 조치
node(63, 22, 26, 6.0, "근본 조치", "계측 코드에서 고유값 라벨 제거", C_GREEN, ec=C_ACCENT)
# 재발 방지
node(63, 13.5, 26, 6.0, "재발 방지", "sample_limit · label_limit 설정", C_BLUE)

# arrows
arrow(50, 47.75, 50, 44.75, color=C_ACCENT, lw=2.0)
arrow(43, 40, 30, 34.5, color=C_ORANGE, lw=1.9, rad=-0.05)
text(33, 38.2, "급증", size=8.5, color=C_ORANGE, weight="bold")
arrow(57, 40, 74, 34.5, color=C_DIM, lw=1.7, rad=0.05)
text(68, 38.2, "완만", size=8.5, color=C_DIM, weight="bold")

arrow(26, 27.75, 26, 25.0, color=C_ACCENT, lw=1.9)
arrow(26, 19.0, 26, 16.5, color=C_ACCENT, lw=1.9)
# 재시작 -> 근본조치
arrow(38, 22, 50, 22, color=C_ACCENT, lw=1.9)
text(44, 24.0, "이후", size=8, color=C_DIM)
arrow(63, 19.0, 63, 16.5, color=C_ACCENT, lw=1.9)

# bottom
text(50, 6.0, "Prometheus 쪽 완화(drop)는 항상 임시방편 — 근본은 계측 코드에서 고유값 라벨(Pod명·요청 ID·타임스탬프)을 없애는 것",
     size=10, color=C_ACCENT, weight="bold")
text(50, 2.6, "sample_limit / label_limit 을 ServiceMonitor·PodMonitor에 미리 걸면 타깃 하나의 폭주가 전체를 끌어내리는 사고 방지",
     size=9, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "38-oom-flow.png")
