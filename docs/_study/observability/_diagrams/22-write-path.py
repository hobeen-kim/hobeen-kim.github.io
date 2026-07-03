"""CH22 쓰기 경로 — distributor → ingester → blocks (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def node(cx, cy, t, sub, c, bw=16, bh=7):
        d.box(cx - bw / 2, cy - bh / 2, bw, bh, P[c])
        d.text(cx, cy + (1.3 if sub else 0), t, size=9.5, weight="bold")
        if sub:
            d.text(cx, cy - 1.6, sub, size=7.6, color=P["dim"])

    node(9, 26, "애플리케이션", "/ Collector", "blue", bw=15)
    node(26, 26, "Distributor", "trace_id 해싱", "green", bw=17)
    node(44, 38, "Ingester 1", "", "brown", bw=15, bh=5.5)
    node(44, 26, "Ingester 2", "", "orange", bw=15, bh=5.5)
    node(44, 14, "Ingester 3", "", "brown", bw=15, bh=5.5)

    node(64, 36, "WAL", "로컬 디스크", "gray", bw=18)
    node(64, 23, "Head Block", "메모리", "purple", bw=15)
    node(83, 23, "Complete Block", "cut", "green", bw=17)
    node(83, 10, "오브젝트 스토리지", "S3 / GCS", "blue", bw=18)

    d.arrow(16.5, 26, 17.5, 26, color=P["accent"])
    for cy in (38, 26, 14):
        d.arrow(34.5, 26, 36.5, cy, color=P["accent"])
    d.arrow(51.5, 26, 55, 35, color=P["orange"])
    d.arrow(51.5, 26, 56.5, 23.5, color=P["orange"])
    d.arrow(71.5, 23, 74.5, 23, color=P["accent"])
    d.text(74, 26, "cut 주기", size=8, color=P["accent"])
    d.arrow(83, 19.5, 83, 13.5, color=P["accent"])
    d.text(88.5, 16.5, "flush", size=8, color=P["accent"], weight="bold")


diagram("22-write-path", draw, w=13, h=5.6, ymax=44)
