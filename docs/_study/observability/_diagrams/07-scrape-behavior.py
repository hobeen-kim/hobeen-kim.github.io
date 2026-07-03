"""CH07 §1 스크레이프 동작 — up 메트릭과 타임아웃 시퀀스 (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P
    RED = P["orange"]  # 실패 흐름 강조색

    PX, TX = 40, 78

    # 라이프라인 헤드
    d.box(32.5, 43, 15, 5, P["gray"], ec=P["accent"], lw=1.5)
    d.text(40, 45.5, "Prometheus", size=10, weight="bold", color=P["accent"])
    d.box(70.5, 43, 15, 5, P["brown"])
    d.text(78, 45.5, "타깃", size=10, weight="bold")
    for x in (PX, TX):
        d.ax.plot([x, x], [5, 43], color=P["edge"], ls=(0, (4, 3)),
                  lw=1.0, zorder=1)

    # 설정 노트
    d.box(30, 37.5, 58, 4.2, P["chip"], ec=P["accent"], lw=1.2)
    d.text(59, 39.6, "scrape_interval = 15s   ·   scrape_timeout = 10s (≤ interval)",
           size=9, color=P["accent"])

    def req(y, tlabel):
        d.arrow(PX, y, TX, y, color=P["dim"])
        d.text((PX + TX) / 2, y + 1.4, "GET /metrics", size=8, color=P["dim"])
        d.text(PX - 7, y, tlabel, size=8.5, color=P["dim"], weight="bold")

    # t=0s 성공
    req(33, "t=0s")
    d.arrow(TX, 29, PX, 29, color=P["accent"], ls="--")
    d.text((PX + TX) / 2, 30.4, "200 OK", size=8, color=P["accent"])
    d.box(3, 27, 20, 4.4, P["chip"], ec=P["accent"], lw=1.3)
    d.text(13, 29.2, "up{instance} = 1", size=9, weight="bold", color=P["accent"])

    # t=15s 타임아웃
    req(21, "t=15s")
    d.arrow(TX, 17, PX + 8, 17, color=RED, ls="--", style="-")
    d.text(PX + 7, 17, "X", size=11, color=RED, weight="bold")
    d.text((PX + TX) / 2 + 4, 18.4, "타임아웃 (응답 없음)", size=8, color=RED)
    d.box(3, 15, 20, 4.4, P["chip"], ec=RED, lw=1.3)
    d.text(13, 17.2, "up{instance} = 0", size=9, weight="bold", color=RED)

    # t=30s 복구
    req(9, "t=30s")
    d.arrow(TX, 5.5, PX, 5.5, color=P["accent"], ls="--")
    d.text((PX + TX) / 2, 6.9, "200 OK (복구)", size=8, color=P["accent"])
    d.box(3, 3.5, 20, 4.4, P["chip"], ec=P["accent"], lw=1.3)
    d.text(13, 5.7, "up{instance} = 1", size=9, weight="bold", color=P["accent"])

    d.legend([
        Line2D([0], [0], color=P["dim"], lw=2.4, label="스크레이프 요청"),
        Line2D([0], [0], color=P["accent"], lw=2.4, ls="--", label="성공 → up=1"),
        Line2D([0], [0], color=RED, lw=2.4, ls="--", label="타임아웃 → up=0"),
    ], anchor=(0.62, 0.005))


diagram("07-scrape-behavior", draw, w=12, h=6.4, ymax=50)
