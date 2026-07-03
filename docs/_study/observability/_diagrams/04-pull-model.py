"""CH04 Pull 모델 — Prometheus 스크레이프와 up 메트릭 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    actors = [
        (16, P["blue"], "Prometheus"),
        (50, P["green"], "서비스 디스커버리"),
        (84, P["brown"], "타깃 (/metrics)"),
    ]
    for x, fc, name in actors:
        d.box(x - 13, 44, 26, 5.5, fc)
        d.text(x, 46.7, name, size=10.5, weight="bold")
        d.ax.plot([x, x], [5, 44], color=P["edge"], lw=1.1,
                  ls=(0, (4, 3)), zorder=1)

    # SD 질의
    d.arrow(16, 40, 50, 40, color=P["accent"])
    d.text(33, 41.6, "타깃 목록 질의", size=9, color=P["accent"])
    d.arrow(50, 36, 16, 36, color=P["violet"], ls="--")
    d.text(33, 37.6, "타깃 주소 목록", size=9, color=P["violet"])

    # loop 박스
    d.box(9, 8, 82, 24, P["chip"], ec=P["orange"], lw=1.6)
    d.text(14, 29.5, "loop  scrape_interval 마다", size=8.5,
           color=P["orange"], ha="left")

    d.arrow(16, 27, 84, 27, color=P["accent"])
    d.text(50, 28.4, "GET /metrics", size=9, color=P["accent"])

    # alt: 정상
    d.box(12, 19, 76, 6.5, P["gray"])
    d.text(16, 23.6, "alt  정상 응답", size=8, color=P["accent"], ha="left")
    d.arrow(84, 21, 16, 21, color=P["dim"], ls="--")
    d.text(58, 22.3, "메트릭 · up=1", size=8.5, color=P["accent"])

    # else: 실패
    d.box(12, 11, 76, 6.5, P["brown"])
    d.text(16, 15.6, "else  타임아웃 / 거부", size=8, color=P["orange"], ha="left")
    d.text(58, 13, "up=0  (타깃 다운)", size=8.5, color=P["orange"])


diagram("04-pull-model", draw, w=13, h=6, ymax=50)
