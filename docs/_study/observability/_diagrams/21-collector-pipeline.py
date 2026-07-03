"""CH21 Collector 파이프라인 — receiver → processor → exporter (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    def chip(cx, cy, t, sub, c, bw=22, bh=7):
        d.box(cx - bw / 2, cy - bh / 2, bw, bh, P[c])
        d.text(cx, cy + 1.3, t, size=10, weight="bold")
        d.text(cx, cy - 1.6, sub, size=8, color=P["dim"])

    # 그룹 박스
    d.box(3, 5, 24, 42, P["gray"])
    d.text(15, 44, "Receivers", size=12, weight="bold", color=P["accent"])
    d.box(37, 5, 26, 42, P["gray"])
    d.text(50, 44, "Processors (순서)", size=12, weight="bold", color=P["orange"])
    d.box(73, 5, 24, 42, P["gray"])
    d.text(85, 44, "Exporters", size=12, weight="bold", color=P["violet"])

    recv = [("otlp", ":4317 / :4318", 38), ("prometheus", "스크레이프", 28),
            ("filelog", "파일 tail", 18)]
    for t, s, cy in recv:
        chip(15, cy, t, s, "blue", bw=20)

    proc = [("memory_limiter", "OOM 방지", 39), ("attributes", "속성 가공", 30),
            ("tail_sampling", "trace 샘플링", 21), ("batch", "배치 전송", 12)]
    for t, s, cy in proc:
        chip(50, cy, t, s, "brown", bw=24)
    for i in range(len(proc) - 1):
        d.arrow(50, proc[i][2] - 3.5, 50, proc[i + 1][2] + 3.5, color=P["orange"])

    exp = [("otlp", "Tempo", 38), ("prometheusrw", "Mimir", 28), ("loki", "Loki", 18)]
    for t, s, cy in exp:
        chip(85, cy, t, s, "green", bw=22)

    for _, _, cy in recv:
        d.arrow(25, cy, 38, 39, color=P["accent"], rad=-0.12)
    for _, _, cy in exp:
        d.arrow(62, 12, 74, cy, color=P["violet"], rad=0.12)

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.2, label="수신"),
        Line2D([0], [0], color=P["orange"], lw=2.2, label="가공 순서"),
        Line2D([0], [0], color=P["violet"], lw=2.2, label="내보내기"),
    ])


diagram("21-collector-pipeline", draw, w=12, h=6.2, ymax=50)
