"""CH19 수집 파이프라인 스테이지 — tail → ... → Loki push (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    stages = [
        ("tail", "파일 읽기", P["blue"]),
        ("multiline", "여러 줄 →\n한 이벤트", P["gray"]),
        ("json/regex\n/logfmt", "파싱", P["gray"]),
        ("labels\n/relabel", "라벨 부여", P["green"]),
        ("drop", "불필요\n라인 제거", P["brown"]),
        ("structured\n_metadata", "고카디널리티\n분리", P["green"]),
        ("Loki push", "distributor로", P["blue"]),
    ]
    n = len(stages)
    w, gap = 11.6, 1.6
    total = n * w + (n - 1) * gap
    x0 = (100 - total) / 2
    for i, (t, sub, fc) in enumerate(stages):
        cx = x0 + i * (w + gap) + w / 2
        endpoint = t in ("tail", "Loki push")
        d.box(cx - w / 2, 10, w, 14, fc,
              ec=(P["accent"] if endpoint else P["edge"]),
              lw=(1.7 if endpoint else 1.3))
        d.text(cx, 19.5, t, size=8.8, weight="bold")
        d.text(cx, 14, sub, size=7.5, color=P["dim"])
        if i < n - 1:
            edge = cx + w / 2
            d.arrow(edge + 0.1, 17, edge + gap - 0.1, 17, color=P["orange"])


diagram("19-pipeline-stages", draw, w=14, h=3.2, ymax=30)
