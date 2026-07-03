"""CH06 §4 Classic vs Native histogram — 카디널리티 대비 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_PURPLE, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "Classic vs Native Histogram — 카디널리티", size=19, weight="bold")
text(50, 56.6, "버킷마다 시계열이 쪼개지는 클래식 방식 vs 단일 시계열에 버킷 벡터를 압축하는 네이티브 방식",
     size=12, color=C_DIM)

# ================= left: Classic =================
box(4, 11, 44, 41, C_BROWN, ec=C_ORANGE, lw=1.8)
text(26, 48.8, "Classic Histogram", size=14, weight="bold", color=C_ORANGE)
text(26, 46.0, "버킷 경계마다 별도 시계열", size=9.5, color="#e0d4c8")

classic = ['le=0.1  →  시계열 1', 'le=0.5  →  시계열 2',
           'le=1  →  시계열 3', 'le=+Inf  →  시계열 4']
for i, t in enumerate(classic):
    yy = 38 - i * 6.2
    box(8, yy, 36, 4.6, "#241d1a")
    text(26, yy + 2.3, t, size=10)
text(26, 14.4, "… 버킷 수만큼 시계열이 배수로 증가", size=9, color=C_ORANGE, style="italic")

# ================= right: Native =================
box(52, 11, 44, 41, C_GREEN, ec=C_ACCENT, lw=2.0)
text(74, 48.8, "Native Histogram", size=14, weight="bold", color=C_ACCENT)
text(74, 46.0, "버킷 수와 무관하게 시계열 하나", size=9.5, color="#d4e0d4")

box(56, 32, 36, 10.5, "#1d2b24", ec=C_ACCENT, lw=1.5)
text(74, 39.0, "단일 시계열", size=13, weight="bold", color=C_ACCENT)
text(74, 35.6, "값 자체가 sparse 버킷 벡터", size=9, color="#d4e0d4")

box(56, 17, 36, 10.5, "#1d2b24")
text(74, 24.0, "지수 스킴 버킷", size=12, weight="bold")
text(74, 20.6, "자동 고해상도 · 연속에 가까운 분포", size=8.5, color=C_DIM)

arrow(74, 32, 74, 27.5, color=C_ACCENT, lw=2.0)

# bottom
text(50, 6.4, "카디널리티가 버킷 개수와 무관 · 해상도는 훨씬 높음 · histogram_quantile() 그대로 사용",
     size=10.5, color=C_ACCENT, weight="bold")
text(50, 3.4, "아직 진화 중 — 기능 플래그·클라이언트/remote_write/다운스트림 버전 지원 확인 필요",
     size=9.5, color=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "06-native-histogram.png")
