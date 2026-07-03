"""CH27 span profiles — 트레이스↔프로파일 연계 시퀀스 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "span profiles — 프로파일 샘플에 span_id 태그 부착", size=20, weight="bold")
text(50, 56.6, "span이 시작~종료되는 구간 동안만 pprof 라벨에 span_id가 붙어, 그 스팬의 프로파일만 필터 가능",
     size=12, color=C_DIM)

# ---- lifelines ----
lanes = [
    (20, "OTel SDK", "트레이싱", C_GREEN),
    (50, "애플리케이션 코드", "비즈니스 로직", C_BLUE),
    (80, "Pyroscope SDK", "프로파일링", C_BROWN),
]
for x, t, d, c in lanes:
    box(x - 11, 49.5, 22, 4.6, c)
    text(x, 52.4, t, size=12, weight="bold")
    text(x, 50.6, d, size=8.5, color=C_DIM)
    ax.plot([x, x], [8, 49.5], color=C_EDGE, lw=1.2, ls=(0, (4, 3)), zorder=1)

# step 1: OTel -> App span 시작
arrow(20, 44, 50, 44, color=C_ACCENT, lw=2.2)
text(35, 45.6, "span 시작 (span_id=abc123)", size=9.5, color=C_ACCENT, weight="bold")

# active span band (highlight region)
box(9, 20, 82, 20, "#161c22", ec=C_ORANGE, lw=1.4)
text(14, 38.0, "span 활성 구간", size=10, color=C_ORANGE, weight="bold", ha="left")

# step 2: App -> Pyro 태그 부착
arrow(50, 34, 80, 34, color=C_ORANGE, lw=2.2)
text(65, 35.6, "실행 중 프로파일 샘플에\nspan_id=abc123 태그 부착", size=9, color=C_ORANGE, weight="bold")

# step 3: App self 비즈니스 로직 실행
box(38, 25.5, 24, 4.4, C_BLUE)
text(50, 27.7, "비즈니스 로직 실행", size=9.5, weight="bold")
arrow(50, 34, 50, 29.9, color=C_DIM, lw=1.8)

# note over Pyro
box(64, 22, 24, 4.2, "#241d1a", ec=C_BROWN)
text(76, 24.1, "이 구간 샘플만 span_id로 필터", size=8.3, color="#f0c99a")

# step 4: OTel -> App span 종료
arrow(20, 15.5, 50, 15.5, color=C_ACCENT, lw=2.2)
text(35, 17.1, "span 종료", size=9.5, color=C_ACCENT, weight="bold")

# bottom
text(50, 5.4, "Tempo에서 스팬을 열면 그 스팬의 실행 시간·span_id로 필터된 프로파일만 병합해 플레임그래프로 표시",
     size=10, color=C_ACCENT, weight="bold")
text(50, 2.6, "트레이스가 '이 스팬이 200ms 걸렸다'면, span profile은 그 200ms 안 어느 함수가 시간을 썼는지 답한다",
     size=9, color=C_DIM, style="italic")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="span 시작·종료 (OTel)"),
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="span_id 태그 부착 (Pyroscope)"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.005, 0.12),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "27-span-profiles-sequence.png")
