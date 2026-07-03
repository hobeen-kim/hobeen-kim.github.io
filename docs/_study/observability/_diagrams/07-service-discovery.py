"""CH07 §3 서비스 디스커버리 — SD 소스 → Discovery Manager → Retrieval (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_PURPLE, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "서비스 디스커버리 — 동적 타깃 목록 갱신", size=20, weight="bold")
text(50, 56.6, "각 SD 소스가 타깃과 __meta_* 메타 라벨을 만들어 Discovery Manager로 공급한다",
     size=12, color=C_DIM)

# ================= top: SD sources =================
sds = [
    (C_BLUE,   "kubernetes_sd_configs", "apiserver watch",
     "Pod·Service·Endpoint", "__meta_kubernetes_*"),
    (C_GREEN,  "ec2_sd_configs", "AWS API",
     "리전 내 인스턴스 목록", "__meta_ec2_*"),
    (C_BROWN,  "consul_sd_configs", "Consul 카탈로그",
     "서비스 카탈로그 조회", "__meta_consul_*"),
    (C_PURPLE, "file_sd_configs", "JSON/YAML 파일",
     "외부 생성 목록 재읽기", "GitOps 친화적"),
]
xs = [2.5, 27, 51.5, 76]
for x, (col, title, mech, out, meta) in zip(xs, sds):
    box(x, 39, 21.5, 13, col)
    cx = x + 10.75
    text(cx, 49.6, title, size=9.8, weight="bold")
    text(cx, 47.0, mech, size=8, color=C_DIM, style="italic")
    text(cx, 44.2, out, size=8.3, color="#e6e8eb")
    text(cx, 41.4, meta, size=7.8, color=C_ACCENT)

# ================= center: Discovery Manager =================
box(31, 22, 38, 10, C_GRAY, ec=C_ACCENT, lw=2.0)
text(50, 28.4, "Discovery Manager", size=14, weight="bold", color=C_ACCENT)
text(50, 25.0, "모든 SD 소스의 타깃 목록을 통합 관리", size=9, color=C_DIM)

# ================= bottom: Retrieval =================
box(37, 8, 26, 8, C_ORANGE.replace("#e0a86b", "#5a4020"), ec=C_ORANGE, lw=1.6)
text(50, 13.4, "Retrieval", size=13, weight="bold", color=C_ORANGE)
text(50, 10.6, "relabel 적용 후 스크레이프", size=8.5, color="#e0c8a0")

# ---- arrows ----
for x in xs:
    cx = x + 10.75
    tx = 50 + (cx - 50) * 0.42
    arrow(cx, 39, tx, 32, color=C_ACCENT, lw=1.8)
arrow(50, 22, 50, 16, color=C_ORANGE, lw=2.2)
text(58.5, 19, "relabel 적용", size=8.5, color=C_ORANGE, weight="bold")

# bottom
text(50, 4.4, "컨테이너·VM이 끊임없이 뜨고 사라지는 환경에서 타깃 목록을 자동 갱신 — 손으로 관리 불가",
     size=10.5, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "07-service-discovery.png")
