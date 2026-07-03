"""CH05 §3 생태계 — 계측·브릿지·배치·SD·알림 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_PURPLE, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "Prometheus 생태계", size=20, weight="bold")
text(50, 56.6, "계측(화이트박스) · Exporter(브릿지) · Pushgateway(배치) · SD · Alertmanager로 운영을 완성",
     size=12, color=C_DIM)

# ================= left column: three source groups =================
# 계측
box(2, 39, 30, 13, C_GREEN)
text(17, 49.4, "계측 (화이트박스)", size=12, weight="bold")
box(4, 40.5, 12.5, 6.6, "#1d2b24")
text(10.25, 45.3, "Client Library", size=9.5)
text(10.25, 42.7, "Go·Java·Python…", size=7.8, color=C_DIM)
box(18.5, 40.5, 11.5, 6.6, "#1d2b24")
text(24.25, 45.3, "애플리케이션", size=9.5)
text(24.25, 42.7, "메트릭 직접 노출", size=7.8, color=C_DIM)
arrow(18.5, 43.8, 16.5, 43.8, color=C_DIM, lw=1.6, style="-|>")

# 브릿지
box(2, 24, 30, 13, C_BROWN)
text(17, 34.4, "브릿지 (Exporter)", size=12, weight="bold")
box(4, 25.5, 13.5, 6.6, "#241d1a")
text(10.75, 30.3, "계측 불가 대상", size=9.5)
text(10.75, 27.7, "OS·DB·하드웨어", size=7.8, color=C_DIM)
box(19.5, 25.5, 10.5, 6.6, "#241d1a")
text(24.75, 30.3, "Exporter", size=9.5)
text(24.75, 27.7, "node_exporter", size=7.6, color=C_DIM)
arrow(17.5, 28.8, 19.5, 28.8, color=C_ORANGE, lw=1.8)

# 배치
box(2, 9, 30, 13, C_BLUE)
text(17, 19.4, "배치 (Pushgateway)", size=12, weight="bold")
box(4, 10.5, 12.5, 6.6, "#1b232a")
text(10.25, 15.3, "단명 배치 잡", size=9.5)
text(10.25, 12.7, "스크레이프 전 종료", size=7.6, color=C_DIM)
box(18.5, 10.5, 11.5, 6.6, "#1b232a")
text(24.25, 15.3, "Pushgateway", size=9.3)
text(24.25, 12.7, "결과 중계 보관", size=7.6, color=C_DIM)
arrow(16.5, 13.8, 18.5, 13.8, color=C_ORANGE, lw=1.8, style="-|>")
text(17.5, 15.8, "push", size=7, color=C_ORANGE)

# ================= center: Prometheus =================
box(44, 22, 20, 18, C_GRAY, ec=C_ACCENT, lw=2.0)
text(54, 34.5, "Prometheus", size=15, weight="bold", color=C_ACCENT)
text(54, 31.0, "모든 소스를\npull(/metrics)로 수집", size=9.5, color="#d4dae0")
text(54, 25.5, "단일 바이너리", size=9, color=C_ACCENT, style="italic")

# ================= service discovery (bottom center) =================
box(40, 6, 28, 10, C_PURPLE)
text(54, 13.2, "Service Discovery", size=11.5, weight="bold")
text(54, 10.4, "k8s · EC2 · Consul · file", size=9, color="#ddd0ee")
text(54, 8.0, "동적 타깃 목록 갱신", size=8, color=C_DIM)

# ================= right: Alertmanager =================
box(74, 26, 24, 14, C_GRAY, ec=C_ORANGE, lw=1.8)
text(86, 36.4, "Alertmanager", size=13, weight="bold", color=C_ORANGE)
text(86, 32.5, "완전 분리된 별도 바이너리", size=8.5, color=C_DIM)
text(86, 29.5, "그룹핑 · 중복 제거\n억제 · 라우팅", size=9, color="#e0d4c8")

# ---- arrows into Prometheus ----
arrow(32, 45, 44, 37, color=C_ACCENT, lw=2.0)
text(38, 43.0, "/metrics", size=8, color=C_ACCENT, weight="bold")
arrow(32, 30, 44, 32, color=C_ACCENT, lw=2.0)
text(38, 33.0, "/metrics", size=8, color=C_ACCENT, weight="bold")
arrow(32, 15, 44, 26, color=C_ACCENT, lw=2.0)
text(37.5, 22.5, "/metrics (pull)", size=8, color=C_ACCENT, weight="bold")
arrow(54, 16, 54, 22, color=C_VIOLET, lw=2.0)
text(61.5, 19, "타깃 갱신", size=8, color=C_VIOLET)
arrow(64, 33, 74, 33, color=C_ORANGE, lw=2.2)
text(69, 35.2, "알림", size=8.5, color=C_ORANGE, weight="bold")

# bottom
text(50, 2.6, "화이트박스 계측이 기본 · Exporter는 브릿지 · Pushgateway는 예외적 배치 케이스 · 알림은 분리 운영",
     size=10, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "05-ecosystem.png")
