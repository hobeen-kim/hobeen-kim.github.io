"""CH07 §4 Relabeling 파이프라인 — 스크레이프 전 타깃 필터링·재작성 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_PURPLE, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "Relabeling — 스크레이프 전 타깃 통제 파이프라인", size=19, weight="bold")
text(50, 56.6, "SD가 만든 타깃 목록을 실제 스크레이프가 일어나기 전에 순차 규칙으로 필터링·재작성한다",
     size=12, color=C_DIM)

# ================= pipeline row =================
box(2, 34, 16, 13, C_GRAY)
text(10, 43.4, "SD가 만든 타깃", size=10, weight="bold")
text(10, 40.6, "+ __meta_* 라벨", size=8.5, color=C_ACCENT)
text(10, 37.6, "(임시 메타데이터)", size=8, color=C_DIM)

for i, label in enumerate(["relabel_config #1", "relabel_config #2", "relabel_config #N"]):
    x = 23 + i * 20
    box(x, 35, 15, 11, C_BLUE)
    text(x + 7.5, 42.6, label, size=9.5, weight="bold")
    text(x + 7.5, 39.8, "source_labels", size=7.6, color="#8fb4cf")
    text(x + 7.5, 37.6, "→ regex → action", size=7.6, color="#8fb4cf")

box(84, 34, 14, 13, C_GREEN, ec=C_ACCENT, lw=1.8)
text(91, 43.4, "최종 타깃", size=10.5, weight="bold", color=C_ACCENT)
text(91, 40.6, "라벨 +", size=8.5, color="#d4e0d4")
text(91, 38.0, "__address__ 확정", size=8.3, color="#d4e0d4")

# arrows across pipeline
for x1, x2 in [(18, 23), (38, 43), (58, 63), (78, 84)]:
    arrow(x1, 40.5, x2, 40.5, color=C_ACCENT, lw=2.0)

# ================= scrape (below final) =================
box(80, 26, 18, 6.5, C_ORANGE.replace("#e0a86b", "#5a4020"), ec=C_ORANGE, lw=1.6)
text(89, 30.3, "스크레이프 실행", size=10.5, weight="bold", color=C_ORANGE)
text(89, 27.8, "keep된 타깃만 GET", size=8, color="#e0c8a0")
arrow(91, 34, 89, 32.6, color=C_ORANGE, lw=2.2)
text(79, 30.5, "drop된 타깃\n여기서 제외", size=8, color=C_ORANGE, ha="right")

# ================= mechanism + actions =================
box(3, 3, 58, 19, "#141b20", ec=C_EDGE, lw=1.2)
text(32, 19.4, "동작 순서", size=10, weight="bold", color=C_ACCENT)
text(32, 16.6, "source_labels 값 추출 → separator 결합 → regex 매치 → action 실행",
     size=8.6, color=C_TEXT)
actions = [
    ("keep / drop", "매치 타깃 유지 / 제거"),
    ("replace", "매치 결과를 target_label에 기록 (기본값)"),
    ("labelmap", "소스 라벨명을 새 라벨명으로 복사"),
    ("labeldrop / labelkeep", "라벨 이름 기준 제거 / 유지"),
    ("hashmod", "해시 기반 샤딩(인스턴스 간 타깃 분할)"),
]
for i, (a, d) in enumerate(actions):
    yy = 13.4 - i * 2.2
    text(7, yy, a, size=8.3, color=C_ORANGE, ha="left", weight="bold")
    text(26, yy, d, size=8, color=C_DIM, ha="left")

# ---- key takeaway box (right) ----
box(65, 3, 33, 19, C_PURPLE)
text(81.5, 19.4, "핵심 원리", size=10.5, weight="bold", color="#ddd0ee")
text(81.5, 14.6, "__ 로 시작하는 라벨은 relabel\n단계에서만 보이고 사라진다", size=8.6,
     color="#e6e8eb")
text(81.5, 8.4, "target_label로 명시 승격해야\n영구 라벨로 남는다", size=8.6,
     color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "07-relabeling.png")
