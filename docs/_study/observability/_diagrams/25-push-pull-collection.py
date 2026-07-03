"""CH25 Pyroscope 수집 경로 — push / pull / eBPF (light/dark PNG)."""
from _common import diagram
from _common import Line2D


def draw(d):
    P = d.P

    # push 경로
    d.box(4, 38, 30, 8, P["green"])
    d.text(19, 43.2, "언어별 SDK", size=11, weight="bold")
    d.text(19, 40.4, "push 경로 (기본)", size=8.5, color=P["dim"])

    # pull 경로
    d.box(4, 24, 30, 8, P["blue"])
    d.text(19, 29.2, "/debug/pprof", size=11, weight="bold")
    d.text(19, 26.4, "pull 경로 (스크레이핑)", size=8.5, color=P["dim"])

    # eBPF 경로
    d.box(4, 10, 30, 8, P["purple"])
    d.text(19, 15.2, "pyroscope.ebpf", size=11, weight="bold")
    d.text(19, 12.4, "eBPF 경로 (무계측)", size=8.5, color=P["dim"])

    # Alloy
    d.box(44, 13, 16, 20, P["brown"], ec=P["orange"], lw=1.8)
    d.text(52, 27, "Alloy", size=13, weight="bold", color=P["orange"])
    d.text(52, 22, "pyroscope.scrape", size=8, color=P["dim"])
    d.text(52, 17.5, "pyroscope.write", size=8, color=P["dim"])

    # distributor
    d.box(70, 30, 26, 12, P["gray"], ec=P["accent"], lw=1.9)
    d.text(83, 38, "Pyroscope", size=11, weight="bold", color=P["accent"])
    d.text(83, 34.5, "distributor", size=11, weight="bold", color=P["accent"])

    # 화살표
    d.arrow(34, 42, 70, 39, color=P["accent"], lw=2.2)
    d.text(52, 43.4, "HTTP push", size=8, color=P["accent"])

    d.arrow(34, 27, 44, 24, color=P["violet"], lw=2.0)
    d.text(39, 28, "scrape", size=8, color=P["violet"])

    d.arrow(34, 13.5, 44, 17, color=P["orange"], lw=2.0)
    d.text(39, 11.6, "무계측", size=8, color=P["orange"])

    d.arrow(60, 24, 70, 33, color=P["dim"], lw=2.2)
    d.text(69, 27, "write", size=8, color=P["dim"], ha="right")

    leg = [
        Line2D([0], [0], color=P["accent"], lw=2.2, label="push (SDK → distributor)"),
        Line2D([0], [0], color=P["violet"], lw=2.2, label="pull (scrape → Alloy)"),
        Line2D([0], [0], color=P["orange"], lw=2.2, label="eBPF 무계측 → Alloy"),
        Line2D([0], [0], color=P["dim"], lw=2.2, label="Alloy → distributor"),
    ]
    d.legend(leg, loc="lower right", anchor=(0.995, 0.02))


diagram("25-push-pull-collection", draw, w=13, h=6.5, ymax=50)
