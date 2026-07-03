"""CH19 수집 파이프라인 스테이지 — tail → ... → Loki push (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE)

fig, ax = new_fig(w=15, h=6.4, ymax=42)
box, text, arrow = make_helpers(ax)

text(50, 38.0, "수집 에이전트 pipeline stage", size=18, weight="bold")
text(50, 34.8, "Alloy/Promtail이 로그를 Loki로 보내기 전에 가공하는 단계 흐름", size=10.5, color=C_DIM)

stages = [
    ("tail", "파일 읽기", C_BLUE),
    ("multiline", "여러 줄 →\n한 이벤트", C_GRAY),
    ("json/regex/\nlogfmt", "파싱", C_GRAY),
    ("labels/\nrelabel", "라벨 부여", C_GREEN),
    ("drop", "불필요\n라인 제거", C_BROWN),
    ("structured_\nmetadata", "고카디널리티\n필드 분리", C_GREEN),
    ("Loki push", "distributor로", C_BLUE),
]
n = len(stages)
w = 11.6
gap = 1.6
total = n * w + (n - 1) * gap
x0 = (100 - total) / 2
for i, (t, d, fc) in enumerate(stages):
    cx = x0 + i * (w + gap) + w / 2
    ec = C_ACCENT if t in ("tail", "Loki push") else C_EDGE
    box(cx - w / 2, 13, w, 13.5, fc, ec=ec, lw=(1.7 if ec == C_ACCENT else 1.3))
    text(cx, 22.0, t, size=9.3, weight="bold")
    text(cx, 16.8, d, size=8.0, color=C_DIM)
    if i < n - 1:
        edge = cx + w / 2
        arrow(edge + 0.1, 19.7, edge + gap - 0.1, 19.7, color=C_ORANGE, lw=2.2)

text(50, 8.0, "multiline(스택 트레이스 병합) · relabel(K8s 메타 승격) · drop(헬스체크 사전 제거)",
     size=9.5, color=C_ACCENT, weight="bold")
text(50, 4.5, "drop으로 저장할 가치 없는 라인을 인제스트 전에 걸러 스토리지·인제스트 비용을 줄인다",
     size=9, color=C_DIM, style="italic")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "19-pipeline-stages.png")
