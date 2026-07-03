"""CH38 up==0 — 스크레이프 실패 타깃 디버깅 경로 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def node(cx, cy, w, h, title, sub, fc, ec=None, tsize=10):
        d.box(cx - w / 2, cy - h / 2, w, h, fc, ec=ec)
        if sub:
            d.text(cx, cy + h * 0.18, title, size=tsize, weight="bold")
            d.text(cx, cy - h * 0.26, sub, size=7.6, color=P["dim"])
        else:
            d.text(cx, cy, title, size=tsize, weight="bold")

    node(50, 51, 26, 6, "up == 0 알림", "마지막 스크레이프 실패", P["brown"], ec=P["orange"])
    node(50, 42, 34, 6.5, "Grafana Targets 확인", "타깃이 목록에 보이는가?", P["gray"], ec=P["accent"])

    # 좌: 타깃 자체 없음
    node(16, 30, 24, 7.5, "ServiceMonitor selector\n라벨 매칭 확인", "Discovered Labels", P["blue"], tsize=9.3)
    # 우: 에러 유형
    node(66, 33, 20, 5.5, "에러 유형 분류", None, P["gray"], ec=P["accent"])

    errs = [
        (39, "connection refused", "메트릭 포트 개방 확인"),
        (57, "context deadline\nexceeded", "scrapeTimeout 조정"),
        (74, "x509 인증서 오류", "TLS·CA 번들 확인"),
        (91, "403 / 401", "token·NetworkPolicy"),
    ]
    for cx, t, s in errs:
        d.box(cx - 8.5, 16, 17, 8, P["green"])
        d.text(cx, 21.7, t, size=8.4, weight="bold")
        d.text(cx, 18.1, s, size=7.2, color=P["dim"])

    node(50, 7, 42, 5.5, "원인 수정 후 다음 scrape_interval 대기", None, P["blue"], ec=P["accent"], tsize=10)

    d.arrow(50, 48, 50, 45.25, color=P["accent"])
    d.arrow(41, 39.5, 24, 33.5, color=P["orange"], lw=1.7, rad=-0.05)
    d.text(29, 37.5, "목록에 없음", size=8, color=P["orange"], weight="bold")
    d.arrow(59, 39.5, 66, 35.75, color=P["accent"], lw=1.7, rad=0.05)
    d.text(69, 37.5, "에러 메시지 있음", size=8, color=P["accent"], weight="bold")

    for cx, *_ in errs:
        d.arrow(66, 30.25, cx, 24, color=P["dim"], lw=1.2, rad=0.02)
    for cx, *_ in errs:
        d.arrow(cx, 16, 50, 9.75, color=P["dim"], lw=1.2, rad=0.03)
    d.arrow(16, 26.25, 32, 9.75, color=P["dim"], lw=1.3, rad=0.1)


diagram("38-scrape-debug", draw, w=13, h=6.4, ymax=56)
