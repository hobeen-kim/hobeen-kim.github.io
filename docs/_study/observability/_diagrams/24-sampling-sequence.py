"""CH24 샘플링 기반 프로파일링 — 타이머 인터럽트 시퀀스 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "샘플링 기반 프로파일링 — 타이머 인터럽트 루프", size=20, weight="bold")
text(50, 56.6, "주기적 인터럽트로 콜 스택만 캡처  →  동일 스택 빈도 누적  →  통계적 프로파일 생성",
     size=12, color=C_DIM)

# ---- lifelines ----
lanes = [
    (20, "샘플링 타이머", "예: 100Hz", C_BROWN),
    (50, "애플리케이션 런타임", "실행 중 프로세스", C_BLUE),
    (80, "프로파일러", "스택 집계기", C_GREEN),
]
for x, t, d, c in lanes:
    box(x - 10, 49.5, 20, 4.6, c)
    text(x, 52.4, t, size=12, weight="bold")
    text(x, 50.6, d, size=8.5, color=C_DIM)
    ax.plot([x, x], [8, 49.5], color=C_EDGE, lw=1.2, ls=(0, (4, 3)), zorder=1)

# ---- loop box (10ms 마다) ----
box(9, 20, 82, 26.5, "#161c22", ec=C_ACCENT, lw=1.6)
text(15.5, 44.6, "loop  10ms 마다", size=10.5, color=C_ACCENT, weight="bold", ha="left")

# step 1: Timer -> Runtime 인터럽트
arrow(20, 40, 50, 40, color=C_ORANGE, lw=2.2)
text(35, 41.6, "인터럽트 발생", size=9.5, color=C_ORANGE, weight="bold")

# step 2: Runtime --> Profiler 콜 스택 캡처 (return-ish, dashed)
arrow(50, 33.5, 80, 33.5, color=C_ACCENT, lw=2.0, ls=(0, (5, 3)))
text(65, 35.1, "현재 콜 스택 캡처", size=9.5, color=C_ACCENT, weight="bold")

# step 3: Profiler self-action 카운트 누적
box(63, 23.4, 20, 4.2, "#1d2b24")
text(73, 25.5, "동일 스택 카운트 누적", size=9, color=C_TEXT)
arrow(80, 30, 80, 27.6, color=C_VIOLET, lw=2.0)

# ---- after loop: aggregate ----
box(60, 11.5, 36, 5.4, C_GREEN, ec=C_ACCENT, lw=1.6)
text(78, 14.9, "스택별 빈도를 집계해 프로파일 생성", size=10.5, weight="bold")
text(78, 12.9, "\"스택 + 빈도\" = 플레임그래프의 원재료", size=8.5, color=C_ACCENT, style="italic")
arrow(80, 20, 80, 16.9, color=C_GREEN, lw=2.2)

# bottom
text(50, 5.4, "특정 함수가 리소스를 많이 쓸수록 더 많은 샘플에 등장  →  충분한 샘플이면 실제 소비 비중에 수렴",
     size=10, color=C_ACCENT, weight="bold")
text(50, 2.6, "계측 기반과 달리 함수 진입·종료마다 코드를 삽입하지 않아 오버헤드가 낮다",
     size=9, color=C_DIM, style="italic")

leg = [
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="타이머 인터럽트"),
    Line2D([0], [0], color=C_ACCENT, lw=2.5, ls="--", label="콜 스택 캡처"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, label="스택 카운트 누적"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.14),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "24-sampling-sequence.png")
