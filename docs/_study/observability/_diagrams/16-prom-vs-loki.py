"""CH16 Prometheus 모델 vs Loki 모델 — 인덱싱 대상 비교 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # Prometheus 모델 (좌)
    d.box(5, 10, 36, 26, P["blue"])
    d.text(23, 32.5, "Prometheus 모델", size=13, weight="bold", color=P["accent"])
    d.box(9, 15, 28, 12, P["chip"])
    d.text(23, 22.5, "metric + labels", size=11.5, weight="bold")
    d.text(23, 18.5, "숫자 값 자체를 인덱싱", size=9, color=P["dim"])

    # Loki 모델 (우)
    d.box(59, 10, 36, 26, P["green"], ec=P["accent"], lw=1.8)
    d.text(77, 32.5, "Loki 모델", size=13, weight="bold", color=P["accent"])
    d.box(63, 24, 28, 6.4, P["chip"])
    d.text(77, 27.2, "labels — 인덱스 대상", size=10, weight="bold")
    d.box(63, 14, 28, 7.4, P["chip"])
    d.text(77, 18.7, "log line", size=10.5, weight="bold")
    d.text(77, 15.9, "압축 청크 · 본문 비인덱싱", size=8.5, color=P["dim"])
    d.arrow(77, 24, 77, 21.4, color=P["orange"])
    d.text(88, 22.7, "스트림 식별", size=8, color=P["orange"])

    # 철학 공유
    d.arrow(41, 23, 59, 23, color=P["violet"], ls="--", style="<|-|>")
    d.text(50, 25.4, "라벨로 식별", size=9, color=P["violet"], weight="bold")


diagram("16-prom-vs-loki", draw, w=12, h=5.2, ymax=42)
