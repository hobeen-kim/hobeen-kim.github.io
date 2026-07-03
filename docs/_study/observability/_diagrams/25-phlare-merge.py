"""CH25 Grafana Pyroscope — Phlare 병합 역사 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 좌: 두 소스
    d.box(3, 26, 28, 10, P["blue"])
    d.text(17, 32.5, "Pyroscope", size=12, weight="bold")
    d.text(17, 29, "이름 · 언어별 SDK · UX", size=8.5, color=P["dim"])

    d.box(3, 10, 28, 10, P["green"])
    d.text(17, 16.5, "Grafana Phlare", size=12, weight="bold")
    d.text(17, 13, "오브젝트 스토리지 아키텍처", size=8.5, color=P["dim"])

    # 중앙: 병합
    d.box(40, 18, 18, 10, P["brown"], ec=P["orange"], lw=1.8)
    d.text(49, 24, "병합", size=13, weight="bold", color=P["orange"])
    d.text(49, 20.6, "2023", size=9, color=P["dim"])

    d.arrow(31, 31, 40, 26, color=P["accent"], lw=2.0)
    d.arrow(31, 15, 40, 20, color=P["accent"], lw=2.0)

    # 우: 결과
    d.box(66, 15, 31, 16, P["gray"], ec=P["accent"], lw=1.9)
    d.text(81.5, 26, "Grafana Pyroscope", size=13, weight="bold", color=P["accent"])
    d.text(81.5, 22, "Pyroscope 이름 + Phlare 아키텍처", size=9, color=P["text"])
    d.text(81.5, 18.5, "distributor · ingester · querier\nstore-gateway · compactor",
           size=8.5, color=P["dim"])

    d.arrow(58, 23, 66, 23, color=P["orange"], lw=2.2)


diagram("25-phlare-merge", draw, w=13, h=6.2, ymax=46)
