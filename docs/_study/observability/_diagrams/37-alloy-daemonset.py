"""CH37 Alloy DaemonSet — 노드별 로그·프로파일 수집 → Loki·Pyroscope push (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    def node(y, label):
        d.box(3, y, 42, 18, P["gray"])
        d.text(24, y + 15, label, size=11, weight="bold")
        d.box(6, y + 4.5, 15, 8, P["chip"])
        d.text(13.5, y + 8.5, "애플리케이션 Pod", size=9)
        d.box(26, y + 3, 16, 11, P["green"], ec=P["accent"], lw=1.6)
        d.text(34, y + 10.5, "Alloy", size=11, weight="bold", color=P["accent"])
        d.text(34, y + 8, "(DaemonSet)", size=8, color=P["dim"])
        d.text(34, y + 5, "loki.source · pyroscope.ebpf", size=7.2, color=P["dim"])
        d.arrow(21, y + 9, 26, y + 9, color=P["orange"], lw=1.6)
        d.arrow(21, y + 6.5, 26, y + 5.5, color=P["violet"], lw=1.6, rad=-0.06)
        d.text(23.5, y + 10, "로그", size=7, color=P["orange"], weight="bold")
        d.text(23.5, y + 4, "eBPF", size=7, color=P["violet"], weight="bold")

    node(26, "노드 1")
    node(5, "노드 2")

    # 백엔드
    d.box(72, 27, 24, 13, P["blue"])
    d.text(84, 35.5, "Loki", size=13, weight="bold")
    d.text(84, 31, "로그 저장", size=9, color=P["dim"])
    d.box(72, 7, 24, 13, P["brown"])
    d.text(84, 15.5, "Pyroscope", size=12.5, weight="bold")
    d.text(84, 11, "연속 프로파일 저장", size=9, color=P["dim"])

    # node1 (alloy center ~y34.5)
    d.arrow(45, 35, 72, 34, color=P["orange"], lw=1.8, rad=-0.05)
    d.arrow(45, 31, 72, 15, color=P["violet"], lw=1.8, rad=0.08)
    # node2 (alloy center ~y13.5)
    d.arrow(45, 14, 72, 32, color=P["orange"], lw=1.8, rad=-0.08)
    d.arrow(45, 11, 72, 12, color=P["violet"], lw=1.8, rad=0.04)
    d.text(59, 37, "loki.write", size=8, color=P["orange"], weight="bold")
    d.text(58, 5.6, "pyroscope.write", size=8, color=P["violet"], weight="bold")

    d.legend([
        Line2D([0], [0], color=P["orange"], lw=2.5, label="컨테이너 로그 (loki.write)"),
        Line2D([0], [0], color=P["violet"], lw=2.5, label="eBPF 프로파일 (pyroscope.write)"),
    ])


diagram("37-alloy-daemonset", draw, w=12, h=6, ymax=45)
