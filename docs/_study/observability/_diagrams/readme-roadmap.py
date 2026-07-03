"""README 학습 로드맵 — S1~S10 단계 체인 다이어그램 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET, C_PURPLE)

fig, ax = new_fig(w=15, h=10.5, ymax=70)
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 67.2, "학습 로드맵 — 기초에서 생태계 확장까지", size=20, weight="bold")
text(50, 64.4, "관측성 기초 → 4대 신호(메트릭·알림·로그·트레이스·프로파일) → 수집·통합 → 운영 심화(SRE) → LGTM 너머 생태계",
     size=11.5, color=C_DIM)

stages = [
    ("S1", "관측성 기초 (01~04)",
     ["모니터링 vs 관측성", "4대 신호", "Grafana 스택 개요", "Pull/Push·카디널리티"], C_GRAY),
    ("S2", "메트릭 — Prometheus (05~12)",
     ["아키텍처", "데이터 모델", "스크레이핑·SD", "Exporter·계측", "PromQL", "TSDB·remote_write"], C_GREEN),
    ("S3", "알림 — Alertmanager (13~15)",
     ["아키텍처·라우팅", "SLO/SLI 알림 설계"], C_BROWN),
    ("S4", "로그 — Loki (16~19)",
     ["아키텍처·라벨 철학", "읽기/쓰기 경로", "LogQL·파이프라인"], C_BLUE),
    ("S5", "트레이스 — Tempo & OTel (20~23)",
     ["분산 트레이싱 기초", "OpenTelemetry", "Tempo·TraceQL"], C_GREEN),
    ("S6", "프로파일 — Pyroscope (24~27)",
     ["연속 프로파일링", "Pyroscope·eBPF", "플레임그래프"], C_BROWN),
    ("S7", "수집 파이프라인 — Alloy (28~30)",
     ["컴포넌트 모델·파이프라인", "Collector vs Alloy"], C_BLUE),
    ("S8", "통합 — Grafana (31~33)",
     ["데이터소스·대시보드", "상관관계·as-code"], C_GRAY),
    ("S9", "운영 심화 — SRE (34~38)",
     ["카디널리티·비용", "Mimir 장기저장", "HA·멀티테넌시", "K8s 배포·트러블슈팅"], C_PURPLE),
    ("S10", "생태계 확장 (39~42)",
     ["Beyla eBPF 자동 계측", "Faro 프런트엔드 RUM", "k6·Synthetic", "Grafana Alerting·IRM"], C_GREEN),
]

# 2열 x 5행 (좌→우 순차, 행마다 아래로)
col_x = [27, 73]          # 좌/우 열 중심
row_cy = [55, 43.5, 32, 20.5, 9]
BW, BH = 42, 9.2

def wrap_chain(steps):
    """스텝을 → 로 이어붙이되 한 줄이 너무 길면 두 줄로 나눔."""
    if len(steps) <= 3:
        return "  →  ".join(steps)
    mid = (len(steps) + 1) // 2
    return "  →  ".join(steps[:mid]) + "  →\n" + "  →  ".join(steps[mid:])

positions = []
for i, (tag, title, steps, fc) in enumerate(stages):
    row, col = i // 2, i % 2
    cx, cy = col_x[col], row_cy[row]
    positions.append((cx, cy))
    ec = C_ACCENT if tag == "S10" else C_EDGE
    lw = 2.2 if tag == "S10" else 1.5
    box(cx - BW/2, cy - BH/2, BW, BH, fc, ec=ec, lw=lw)
    # 태그 배지
    box(cx - BW/2 + 1.2, cy + BH/2 - 3.4, 6.5, 2.6, "#0b0e11", ec=ec, lw=1.2, r=0.02)
    text(cx - BW/2 + 4.45, cy + BH/2 - 2.1, tag, size=9.5, weight="bold",
         color=C_ACCENT if tag == "S10" else C_TEXT)
    text(cx + 3, cy + BH/2 - 2.1, title, size=10.5, weight="bold")
    text(cx, cy - 1.3, wrap_chain(steps), size=8.3, color=C_DIM)

# ---- 순차 화살표 (boustrophedon) ----
for i in range(len(stages) - 1):
    x1, y1 = positions[i]
    x2, y2 = positions[i + 1]
    col = i % 2
    if col == 0:
        # 좌 -> 우 (같은 행)
        arrow(x1 + BW/2, y1, x2 - BW/2, y2, color=C_ACCENT, lw=2.0)
    else:
        # 우 -> 아래 좌 (다음 행)
        arrow(x1, y1 - BH/2, x2, y2 + BH/2, color=C_ACCENT, lw=2.0, rad=0.0)

# bottom
text(50, 2.4, "S10 생태계 확장(39~42)까지 마치면 SDK를 넣을 수 없는 워크로드·브라우저·무트래픽 시간대 등 LGTM 스택의 사각지대까지 커버",
     size=9.5, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "readme-roadmap.png")
