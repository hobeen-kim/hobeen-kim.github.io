"""CH05 §6 확장 경로 — federation / remote_write (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P

    # 왼쪽 리프 Prometheus 서버들
    d.box(2, 7, 20, 38, P["gray"])
    d.text(12, 42.5, "리프 Prometheus", size=10.5, weight="bold")
    for i, t in enumerate(["팀 A", "팀 B", "팀 C"]):
        yy = 32 - i * 11
        d.box(4, yy, 16, 8, P["blue"])
        d.text(12, yy + 4, f"Prometheus\n{t}", size=9.5)

    # federation 경로 (위)
    d.box(42, 32, 22, 10, P["purple"])
    d.text(53, 37, "글로벌 Prometheus\n(federation 계층)", size=10)
    d.box(74, 32, 24, 10, P["gray"], ec=P["violet"], lw=1.6)
    d.text(86, 37, "전역 알림 / 대시보드", size=10, weight="bold",
           color=P["violet"])

    # remote_write 경로 (아래)
    d.box(42, 8, 22, 10, P["green"], ec=P["accent"], lw=1.8)
    d.text(53, 13, "Mimir / Thanos\n장기저장 · 수평확장", size=10)
    d.box(74, 8, 24, 10, P["gray"], ec=P["accent"], lw=1.6)
    d.text(86, 13, "전역 질의", size=10.5, weight="bold", color=P["accent"])

    # federation 화살표
    d.arrow(22, 35, 42, 37, color=P["violet"], rad=0.05)
    d.text(32, 40, "federation (/federate)", size=8, color=P["violet"])
    d.arrow(64, 37, 74, 37, color=P["violet"])

    # remote_write 화살표
    d.arrow(22, 30, 42, 14, color=P["accent"], rad=-0.06)
    d.text(32, 25.5, "remote_write", size=8, color=P["accent"])
    d.arrow(64, 13, 74, 13, color=P["accent"])

    d.legend([
        Line2D([0], [0], color=P["violet"], lw=2.4, label="federation (요약 pull)"),
        Line2D([0], [0], color=P["accent"], lw=2.4, label="remote_write (스트리밍)"),
    ])


diagram("05-scaling-paths", draw, w=13, h=6.2, ymax=48)
