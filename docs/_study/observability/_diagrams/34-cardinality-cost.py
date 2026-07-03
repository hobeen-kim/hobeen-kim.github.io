"""CH34 카디널리티가 메모리·저장·쿼리를 동시에 압박해 비용을 지배 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # ---- 라벨 조합 ----
    d.box(2, 17, 18, 11, P["gray"])
    d.text(11, 24.5, "라벨 조합 증가", size=11, weight="bold")
    d.text(11, 21.2, "user_id · pod_uid\ntrace_id …", size=8.5, color=P["dim"])

    # ---- 카디널리티 폭발 ----
    d.box(24, 17, 18, 11, P["brown"], ec=P["orange"], lw=1.8)
    d.text(33, 24.0, "카디널리티\n폭발", size=12, weight="bold", color=P["orange"])
    d.text(33, 19.6, "고유 시계열 수 ↑↑", size=8.5, color=P["dim"])
    d.arrow(20, 22.5, 24, 22.5, color=P["orange"], lw=2.2)

    # ---- 세 축 ----
    axes = [
        (34, P["blue"], "메모리", "head 블록 · OOM · churn"),
        (22.5, P["green"], "저장", "인덱스 크기 · compaction"),
        (11, P["purple"], "쿼리", "스캔 시계열 ↑ · 지연 ↑"),
    ]
    for y, fc, t, desc in axes:
        d.box(50, y - 4, 30, 8, fc)
        d.text(56, y + 1.4, t, size=11, weight="bold", ha="left")
        d.text(56, y - 1.8, desc, size=8.3, color=P["dim"], ha="left")
        d.arrow(42, 22.5, 50, y, color=P["orange"], lw=2.0)

    # ---- 비용 ----
    d.box(84, 17, 14, 11, P["gray"], ec=P["accent"], lw=1.8)
    d.text(91, 22.5, "운영 비용", size=12, weight="bold", color=P["accent"])
    for y, *_ in axes:
        d.arrow(80, y, 84, 22.5, color=P["dim"], lw=1.5)


diagram("34-cardinality-cost", draw, w=14, h=5.9, ymax=41)
