"""CH38 스크레이프 실패·타깃 down 디버깅 흐름 다이어그램 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "up == 0 — 스크레이프 실패 타깃 디버깅 경로", size=20, weight="bold")
text(50, 56.6, "타깃이 목록에 보이는가부터 나누고, 에러 유형(네트워크·타임아웃·TLS·인증)별로 조치",
     size=12, color=C_DIM)

def node(cx, cy, w, h, title, sub, fc, ec=C_EDGE, tsize=10.5, tcolor=C_TEXT):
    box(cx - w/2, cy - h/2, w, h, fc, ec=ec, lw=1.5)
    if sub:
        text(cx, cy + h*0.17, title, size=tsize, weight="bold", color=tcolor)
        text(cx, cy - h*0.24, sub, size=7.8, color=C_DIM)
    else:
        text(cx, cy, title, size=tsize, weight="bold", color=tcolor)

# start
node(50, 51, 26, 6.0, "up == 0 알림", "마지막 스크레이프 실패", C_BROWN, ec=C_ORANGE)

# 분기 질문
node(50, 42, 34, 6.5, "Grafana Status > Targets 확인", "타깃이 목록에 보이는가?", C_GRAY, ec=C_ACCENT)

# 왼쪽: 타깃 자체 없음
node(20, 31.5, 26, 6.5, "ServiceMonitor selector\n라벨 매칭 확인", "Service Discovery > Discovered Labels", C_BLUE, tsize=9.5)

# 오른쪽: 에러 메시지 → 에러 유형
node(66, 32, 20, 5.5, "에러 유형 분류", None, C_GRAY, ec=C_ACCENT, tsize=10)

# 4 에러 유형
errs = [
    (24, "connection refused", "Pod가 메트릭 포트를\n실제로 열었는지 확인", C_GREEN),
    (43, "context deadline\nexceeded", "scrapeTimeout 조정 ·\n응답 지연 원인 조사", C_GREEN),
    (62, "x509 인증서 오류", "Endpoint TLS 설정 ·\nCA 번들 확인", C_GREEN),
    (82, "403 / 401", "bearerTokenSecret ·\nNetworkPolicy 확인", C_GREEN),
]
for cx, t, d, fc in errs:
    box(cx - 9.5, 18.5, 19, 8.5, fc)
    text(cx, 24.6, t, size=9, weight="bold")
    text(cx, 21.0, d, size=7.6, color=C_DIM)

# 수렴: 원인 수정 후 대기
node(50, 9.5, 40, 5.5, "원인 수정 후 다음 scrape_interval 대기", None, C_BLUE, ec=C_ACCENT, tsize=11)

# arrows
arrow(50, 48, 50, 45.25, color=C_ACCENT, lw=2.0)
arrow(41, 40, 24, 34.75, color=C_ORANGE, lw=1.8, rad=-0.05)
text(28, 38.6, "목록에 없음", size=8, color=C_ORANGE, weight="bold")
arrow(59, 40, 66, 34.75, color=C_ACCENT, lw=1.8, rad=0.05)
text(66, 38.6, "에러 메시지 있음", size=8, color=C_ACCENT, weight="bold")

# 에러유형 -> 4 boxes
for cx, *_ in errs:
    arrow(66, 29.25, cx, 27.0, color=C_DIM, lw=1.3, rad=0.0)

# 4 boxes -> 수렴
for cx, *_ in errs:
    arrow(cx, 18.5, 50, 12.3, color=C_GREEN, lw=1.3, rad=0.03)
# selector 확인 -> 수렴
arrow(20, 28.25, 34, 11.0, color=C_BLUE, lw=1.5, rad=0.1)

# bottom
text(50, 3.6, "핵심: up==0인데 타깃이 Targets에 보이는 경우와, 애초에 타깃 목록에 없는 경우는 원인이 완전히 다르다 — 이 둘을 먼저 구분",
     size=9.5, color=C_ACCENT, weight="bold")

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "38-scrape-debug.png")
