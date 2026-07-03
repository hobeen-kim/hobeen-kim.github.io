"""CH38 Loki/Tempo 수집 병목 — distributor·ingester 포화 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(3, 26, 18, 9, P["gray"])
    d.text(12, 32.2, "클라이언트", size=11.5, weight="bold")
    d.text(12, 29.2, "로그 / 스팬 전송", size=8.5, color=P["dim"])

    d.box(29, 26, 18, 9, P["blue"], ec=P["accent"], lw=1.8)
    d.text(38, 32.2, "Distributor", size=12, weight="bold")
    d.text(38, 29.2, "테넌트별 rate limit", size=8.2, color=P["dim"])

    d.box(55, 26, 18, 9, P["green"])
    d.text(64, 32.2, "Ingester", size=12, weight="bold")
    d.text(64, 29.2, "메모리 버퍼", size=8.5, color=P["dim"])

    d.box(81, 26, 16, 9, P["brown"])
    d.text(89, 31.5, "오브젝트\n스토리지", size=11, weight="bold")

    d.box(29, 8, 18, 8, P["brown"], ec=P["orange"], lw=1.6)
    d.text(38, 13.2, "429 응답", size=11, weight="bold", color=P["orange"])
    d.text(38, 10.2, "discarded 증가", size=8, color=P["dim"])

    d.box(55, 8, 18, 8, P["purple"], ec=P["violet"], lw=1.6)
    d.text(64, 13.2, "메모리 포화", size=11, weight="bold", color=P["text"])
    d.text(64, 10.2, "→ OOM 위험", size=8.2, color=P["dim"])

    d.arrow(21, 30.5, 29, 30.5, color=P["accent"], lw=2.0)
    d.arrow(47, 30.5, 55, 30.5, color=P["accent"], lw=2.0)
    d.text(51, 32.6, "한도 이내", size=8, color=P["accent"], weight="bold")
    d.arrow(73, 30.5, 81, 30.5, color=P["accent"], lw=2.0)
    d.text(77, 32.6, "flush", size=8, color=P["accent"], weight="bold")

    d.arrow(38, 26, 38, 16, color=P["orange"], lw=1.9)
    d.text(41.5, 21, "한도 초과", size=8, color=P["orange"], weight="bold", ha="left")

    d.arrow(64, 26, 64, 16, color=P["violet"], lw=1.9, ls="--")
    d.text(67.5, 21, "flush보다\n유입이 빠르면", size=7.8, color=P["violet"],
           weight="bold", ha="left")


diagram("38-loki-tempo-bottleneck", draw, w=12, h=5.2, ymax=38)
