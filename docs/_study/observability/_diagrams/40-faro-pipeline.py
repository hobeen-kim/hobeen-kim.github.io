"""CH40 Faro — 프런트엔드 관측성 파이프라인 다이어그램 (matplotlib → PNG)."""
from _common import (new_fig, make_helpers, save, Line2D,
                     C_BG, C_EDGE, C_TEXT, C_DIM, C_ACCENT,
                     C_BLUE, C_GREEN, C_BROWN, C_GRAY, C_ORANGE, C_VIOLET)

fig, ax = new_fig()
box, text, arrow = make_helpers(ax)

# ---- Title ----
text(50, 59.4, "Faro — 프런트엔드 관측성(RUM) 파이프라인", size=20, weight="bold")
text(50, 56.6, "브라우저(Faro Web SDK)  →  Alloy faro.receiver  →  Loki · Tempo  →  Grafana",
     size=12, color=C_DIM)

# ================= left: browser =================
box(2, 14, 26, 38, C_BLUE)
text(15, 49.6, "사용자 브라우저", size=13, weight="bold")
text(15, 47.4, "Faro Web SDK (@grafana/faro-web-sdk)", size=9, color=C_DIM)
for i, (t, d) in enumerate([
    ("에러 · 예외", "JS error · unhandled rejection · 스택"),
    ("로그 · 커스텀 이벤트", "console 캡처 · pushEvent()"),
    ("Web Vitals 측정값", "LCP · CLS · INP · TTFB"),
    ("세션 · 메타", "session id · 브라우저 · URL · 사용자"),
    ("트레이스 (OTel)", "fetch/XHR 자동 계측 span"),
]):
    yy = 43.5 - i * 5.4
    box(4, yy - 2.2, 22, 4.4, "#1b232a")
    text(15, yy + 0.6, t, size=10)
    text(15, yy - 1.2, d, size=8, color=C_DIM)

# ================= center: Alloy =================
box(37, 26, 26, 26, C_GREEN, ec=C_ACCENT, lw=2.0)
text(50, 49.6, "Alloy", size=13.5, weight="bold", color=C_ACCENT)
text(50, 47.4, "faro.receiver — 수집 엔드포인트", size=9.5, color=C_DIM)
for i, (t, d) in enumerate([
    ("HTTP 수신", "CORS 허용 도메인 · API key 검증"),
    ("rate limit · 필터", "악성/과다 트래픽 차단"),
    ("신호 분기", "로그류 → Loki · 트레이스 → Tempo"),
]):
    yy = 43 - i * 5.2
    box(39, yy - 2.1, 22, 4.2, "#1d2b24")
    text(50, yy + 0.6, t, size=10)
    text(50, yy - 1.2, d, size=8, color=C_DIM)

# browser -> alloy
arrow(28, 39, 37, 39, color=C_ACCENT, lw=2.2)
text(32.5, 41.2, "HTTP POST\n(배치 전송)", size=8, color=C_ACCENT, weight="bold")

# ================= right: backends =================
box(72, 38, 26, 14, C_GRAY)
text(85, 49.6, "Loki", size=13, weight="bold")
text(85, 47.0, "에러 · 로그 · 이벤트 · Web Vitals\n(app 라벨 + JSON 본문)", size=9, color="#d4dae0")
text(85, 41.5, "LogQL로 에러율·P75 LCP 산출", size=8.5, color=C_ACCENT, style="italic")

box(72, 22, 26, 12, C_GRAY)
text(85, 31.6, "Tempo", size=13, weight="bold")
text(85, 28.8, "프런트엔드 span\n(fetch → 백엔드 API 호출)", size=9, color="#d4dae0")
text(85, 24.8, "백엔드 span과 같은 trace로 연결", size=8.5, color=C_ACCENT, style="italic")

arrow(63, 43, 72, 45, color=C_ORANGE, lw=2.2)
arrow(63, 32, 72, 29, color=C_VIOLET, lw=2.2)

# ================= bottom: backend correlation =================
box(2, 3.5, 61, 7.5, C_BROWN)
text(32.5, 8.9, "백엔드 API 서버", size=11, weight="bold")
text(32.5, 6.2, "브라우저 fetch에 traceparent 헤더 자동 주입 → 백엔드 OTel SDK가 이어받아\n프런트 클릭부터 DB 쿼리까지 하나의 분산 트레이스로 완성", size=9, color="#d4dae0")
arrow(15, 14, 15, 11, color=C_VIOLET, lw=2.0, ls="--")
text(20.5, 12.5, "traceparent 전파", size=8.5, color=C_VIOLET)

box(72, 3.5, 26, 14.5, C_GRAY)
text(85, 15.5, "Grafana", size=13, weight="bold")
text(85, 12.4, "Frontend 대시보드\n에러 ↔ 세션 ↔ 트레이스 상관관계", size=9, color="#d4dae0")
text(85, 7.0, "메트릭(서버) · RUM(브라우저)\n한 화면에서 조회", size=8.5, color=C_ACCENT, style="italic")

leg = [
    Line2D([0], [0], color=C_ACCENT, lw=2.5, label="브라우저 → Alloy 수집"),
    Line2D([0], [0], color=C_ORANGE, lw=2.5, label="로그·이벤트·측정값 → Loki"),
    Line2D([0], [0], color=C_VIOLET, lw=2.5, label="트레이스 → Tempo / traceparent 전파"),
]
ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.33, 0.21),
          fontsize=8.5, framealpha=0.0, labelcolor=C_DIM)

import matplotlib.pyplot as plt
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "40-faro-pipeline.png")
