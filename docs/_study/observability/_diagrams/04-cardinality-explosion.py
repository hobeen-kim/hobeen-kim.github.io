"""CH04 카디널리티 폭발 — 유한 라벨 vs 무한 라벨(user_id)의 결과 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "카디널리티 폭발 — 라벨 하나가 시계열을 곱으로 늘린다", size=20, weight="bold")
text(50, 56.6, "카디널리티 = 메트릭 이름 + 라벨 값 조합의 유일한 시계열 개수", size=12, color=C_DIM)

# ================= 정상 범위 (왼쪽 위) =================
box(4, 38, 44, 13, C_GREEN, ec=C_ACCENT, lw=1.6)
text(26, 47.4, "유한 라벨", size=12.5, weight="bold", color=C_ACCENT)
text(26, 43.4, "method(2) × status(3)  =  시계열 6개", size=11, color="#dfe4e8")
text(26, 40.2, "경우의 수가 수십~수백 이내", size=8.8, color=C_DIM, style="italic")

box(52, 40, 20, 8.5, C_GRAY)
text(62, 44.2, "정상 범위", size=12, weight="bold", color=C_ACCENT)
arrow(48, 44.5, 52, 44.5, color=C_ACCENT, lw=2.2)

# ================= 폭발 (왼쪽 아래) =================
box(4, 20, 44, 14, C_BROWN, ec=C_ORANGE, lw=1.8)
text(26, 30.4, "무한 라벨", size=12.5, weight="bold", color=C_ORANGE)
text(26, 26.4, "method(2) × status(3) × user_id(무한)", size=10.5, color="#e4d3c2")
text(26, 23.0, "= 시계열 사실상 무한", size=11, color=C_ORANGE, weight="bold")

box(52, 22, 20, 9, "#241d1a", ec=C_ORANGE, lw=1.6)
text(62, 27.0, "메모리 폭증", size=11.5, weight="bold", color=C_ORANGE)
text(62, 24.0, "→ OOM 위험", size=10, color="#e4d3c2")
arrow(48, 26.5, 52, 26.5, color=C_ORANGE, lw=2.4)

# ================= 영향 (오른쪽) =================
box(76, 18, 21, 32, C_GRAY, ec=C_ORANGE, lw=1.4)
text(86.5, 46.4, "연쇄 영향", size=12, weight="bold", color=C_ORANGE)
for i, t in enumerate([
    "remote_write\n대역폭 증가",
    "쿼리 지연 증가",
    "멀티테넌시\nnoisy neighbor",
]):
    yy = 39 - i * 8.5
    box(78, yy - 3.2, 18, 6.4, "#241d1a")
    text(87, yy, t, size=9, color="#e4d3c2")
arrow(72, 26.5, 76, 30, color=C_ORANGE, lw=2.4, rad=0.1)

# bottom
text(50, 11.5, "TSDB는 활성 시계열마다 메모리에 인덱스·청크 헤더를 유지 — 시계열이 수백만이면 동시에 악화",
     size=10, color=C_DIM, style="italic")
text(50, 7.6, "\"누가·어떤 요청이\" 같은 고카디널리티 질문은 메트릭 라벨이 아니라 로그·트레이스·exemplar로 답한다",
     size=10.5, color=C_ACCENT, weight="bold")
text(50, 3.8, "user_id 는 로그 필드·트레이스 span 속성으로는 자유롭게 넣어도 된다",
     size=9.5, color=C_DIM, style="italic")

save(fig, "04-cardinality-explosion.png")
