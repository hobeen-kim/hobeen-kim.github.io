"""CH14 inhibition — source/target/equal 기반 억제 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # source: ClusterDown
    d.box(4, 24, 24, 8, P["brown"], ec=P["orange"], lw=1.8)
    d.text(16, 29.5, "ClusterDown", size=12, weight="bold")
    d.text(16, 26.6, "(firing · source)", size=9, color=P["orange"])

    # target: PodDown x40
    d.box(4, 9, 24, 8, P["gray"])
    d.text(16, 14.5, "PodDown ×40", size=12, weight="bold")
    d.text(16, 11.6, "(같은 cluster · target)", size=9, color=P["dim"])

    # inhibit rule (center)
    d.box(38, 15, 24, 12, P["purple"], ec=P["violet"], lw=1.8)
    d.text(50, 23, "inhibit_rule", size=12, weight="bold", color=P["violet"])
    d.text(50, 19.8, "equal: cluster", size=10)
    d.text(50, 17, "source firing 시\ntarget 억제", size=8.5, color=P["dim"])

    # right top: notify ClusterDown
    d.box(72, 24, 24, 8, P["green"], ec=P["accent"], lw=1.6)
    d.text(84, 29.5, "Slack / PagerDuty", size=11, weight="bold")
    d.text(84, 26.6, "ClusterDown 통지됨", size=9, color=P["accent"])

    # right bottom: suppressed
    d.box(72, 9, 24, 8, P["gray"])
    d.text(84, 14.5, "발송 안 됨", size=11, weight="bold", color=P["dim"])
    d.text(84, 11.6, "(suppressed)", size=9, color=P["dim"])

    # arrows: source/target -> rule
    d.arrow(28, 28, 38, 24, color=P["orange"], rad=-0.08)
    d.text(33, 27.5, "source", size=8, color=P["orange"])
    d.arrow(28, 13, 38, 17, color=P["dim"], rad=0.08)
    d.text(33, 12.3, "target", size=8, color=P["dim"])

    # clusterdown -> notify
    d.arrow(28, 30, 72, 28, color=P["accent"], rad=-0.06)
    d.text(50, 32.2, "통지됨", size=8, color=P["accent"])

    # inhibit -> suppressed
    d.arrow(56, 15, 72, 13, color=P["orange"], rad=-0.06)
    d.text(66, 15.2, "억제됨, 통지 안 됨", size=8, color=P["orange"])

    d.legend([
        Line2D([0], [0], color=P["orange"], lw=2.5, label="source / 억제 (발송 차단)"),
        Line2D([0], [0], color=P["accent"], lw=2.5, label="통지"),
    ])


diagram("14-inhibition", draw, w=13, h=6, ymax=38)
