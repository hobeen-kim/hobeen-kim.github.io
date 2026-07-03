"""CH14 severity×team 2축 라우팅 트리 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    # Root
    d.box(36, 44, 28, 5.4, P["blue"], ec=P["accent"], lw=1.8)
    d.text(50, 47, "Root", size=11, weight="bold", color=P["accent"])
    d.text(50, 44.5, "default: slack-platform-general", size=8.5, color=P["dim"])

    # severity decision
    d.box(42, 36, 16, 4.6, P["gray"], ec=P["orange"], lw=1.6)
    d.text(50, 38.3, "severity", size=10.5, weight="bold", color=P["orange"])
    d.arrow(50, 44, 50, 40.6, color=P["edge"])

    # critical branch (left)
    d.box(6, 27, 20, 4.6, P["gray"], ec=P["orange"], lw=1.6)
    d.text(16, 29.3, "team (critical)", size=9.5, weight="bold", color=P["orange"])
    d.arrow(44, 36, 20, 31.6, color=P["orange"])
    d.text(28, 34.5, "critical", size=8.5, color=P["orange"])

    crit = [
        ("payments", "pagerduty-payments"),
        ("infra", "pagerduty-infra"),
        ("기타/미지정 (fallback)", "pagerduty-platform-oncall"),
    ]
    prev_y = 27
    for i, (cond, recv) in enumerate(crit):
        yy = 21 - i * 6
        d.box(2, yy - 2.3, 30, 4.6, P["brown"])
        d.text(17, yy + 0.6, recv, size=9, weight="bold")
        d.text(17, yy - 1.3, cond, size=8, color=P["orange"])
        d.arrow(16, prev_y - (0 if i == 0 else 2.3), 16, yy + 2.3, color=P["orange"], lw=1.4)
        prev_y = yy

    # warning branch (center)
    d.box(40, 27, 20, 4.6, P["gray"], ec=P["accent"], lw=1.6)
    d.text(50, 29.3, "team (warning)", size=9.5, weight="bold", color=P["accent"])
    d.arrow(50, 36, 50, 31.6, color=P["accent"])
    d.text(56, 34, "warning", size=8.5, color=P["accent"])

    warn = [
        ("payments", "slack-payments"),
        ("infra", "slack-infra"),
    ]
    for i, (cond, recv) in enumerate(warn):
        yy = 21 - i * 6
        d.box(37, yy - 2.3, 26, 4.6, P["green"])
        d.text(50, yy + 0.6, recv, size=9, weight="bold")
        d.text(50, yy - 1.3, cond, size=8, color=P["accent"])
        d.arrow(50, 27, 50, yy + 2.3, color=P["accent"], lw=1.4)

    # info branch (right)
    d.box(70, 27, 26, 4.6, P["gray"], ec=P["violet"], lw=1.6)
    d.text(83, 29.3, "info", size=9.5, weight="bold", color=P["violet"])
    d.arrow(58, 37, 74, 31.6, color=P["violet"], rad=-0.1)
    d.text(66, 34.5, "info", size=8.5, color=P["violet"])

    d.box(70, 18, 26, 5.4, P["purple"])
    d.text(83, 20.7, "slack-info-log", size=9.5, weight="bold")
    d.text(83, 18.3, "채널만, 조용히 기록", size=8, color=P["dim"])
    d.arrow(83, 27, 83, 23.4, color=P["violet"], lw=1.4)

    d.legend([
        Line2D([0], [0], color=P["orange"], lw=2.5, label="critical (PagerDuty)"),
        Line2D([0], [0], color=P["accent"], lw=2.5, label="warning (Slack)"),
        Line2D([0], [0], color=P["violet"], lw=2.5, label="info (기록)"),
    ], anchor=(0.72, 0.02))


diagram("14-severity-team-routing", draw, w=14, h=7.5, ymax=52)
