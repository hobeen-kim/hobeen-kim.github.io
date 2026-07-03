"""CH40 Faro — 프런트엔드 관측성(RUM) 파이프라인 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # 왼쪽: 브라우저 (Faro Web SDK)
    d.box(2, 11, 20, 33, P["blue"])
    d.text(12, 41, "사용자 브라우저", size=11, weight="bold")
    d.text(12, 38.5, "(Faro Web SDK)", size=8.5, color=P["dim"])
    for i, t in enumerate([
        "에러 · 예외",
        "로그 · 커스텀 이벤트",
        "Web Vitals (LCP·INP)",
        "트레이스 (fetch/XHR)",
    ]):
        yy = 34 - i * 6
        d.box(4, yy - 2.2, 16, 4.4, P["chip"])
        d.text(12, yy, t, size=9)

    # 중앙: Alloy faro.receiver
    d.box(28, 18, 22, 26, P["green"], ec=P["accent"], lw=1.8)
    d.text(39, 41, "Alloy", size=11.5, weight="bold", color=P["accent"])
    d.text(39, 38.5, "(faro.receiver)", size=8.5, color=P["dim"])
    for i, t in enumerate([
        "HTTP 수신 (CORS·API key)",
        "rate limit · 필터",
        "신호 분기",
    ]):
        yy = 34 - i * 6
        d.box(30, yy - 2.3, 18, 4.6, P["chip"])
        d.text(39, yy, t, size=9)

    # 백엔드 API (traceparent 이어받음)
    d.box(28, 4, 22, 11, P["brown"])
    d.text(39, 11.5, "백엔드 API 서버", size=10.5, weight="bold")
    d.text(39, 8.5, "(OTel SDK가 trace 이어받음)", size=8.5, color=P["dim"])

    # 오른쪽: Loki · Tempo · Grafana
    d.box(54, 31, 20, 12, P["gray"])
    d.text(64, 39.5, "Loki", size=11, weight="bold")
    d.text(64, 35.5, "로그·이벤트·Web Vitals", size=8.5, color=P["dim"])

    d.box(54, 17, 20, 12, P["gray"])
    d.text(64, 25.5, "Tempo", size=11, weight="bold")
    d.text(64, 21.5, "프런트엔드 span", size=8.5, color=P["dim"])

    d.box(80, 23, 18, 12, P["purple"])
    d.text(89, 31, "Grafana", size=11, weight="bold")
    d.text(89, 27, "Frontend 대시보드", size=8.5, color=P["dim"])

    # 흐름 화살표
    d.arrow(22, 30, 28, 30, color=P["accent"])
    d.text(25, 32, "HTTP POST", size=8, color=P["accent"])
    d.arrow(50, 34, 54, 37, color=P["orange"])
    d.text(52, 38.6, "로그·Vitals", size=8, color=P["orange"])
    d.arrow(50, 24, 54, 23, color=P["violet"])
    d.text(52, 20.8, "트레이스", size=8, color=P["violet"])
    d.arrow(74, 36, 80, 31, color=P["accent"])
    d.arrow(74, 24, 80, 28, color=P["accent"])

    # traceparent 전파 (브라우저 → 백엔드 → Tempo)
    d.arrow(12, 11, 28, 12, color=P["violet"], ls="--")
    d.text(19, 9.2, "traceparent", size=8, color=P["violet"])
    d.arrow(50, 11, 56, 17, color=P["violet"], ls="--")
    d.text(56, 13.5, "백엔드 span", size=8, color=P["violet"])

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.5, label="수집 · 조회"),
        Line2D([0], [0], color=P["orange"], lw=2.5, label="로그·이벤트·측정값 → Loki"),
        Line2D([0], [0], color=P["violet"], lw=2.5, label="트레이스 → Tempo · traceparent 전파"),
    ], anchor=(0.005, 0.9))


diagram("40-faro-pipeline", draw, w=14, h=6.6, ymax=48)
