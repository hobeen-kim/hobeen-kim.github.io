"""CH14 route 트리 — matcher 분기와 상속 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    def cond(x, y, w, h, s, size=9.5):
        d.box(x - w / 2, y - h / 2, w, h, P["gray"], ec=P["orange"], lw=1.6)
        d.text(x, y, s, size=size, weight="bold", color=P["orange"])

    def recv(x, y, w, h, title, sub="", fc=None):
        d.box(x - w / 2, y - h / 2, w, h, fc or P["green"])
        if sub:
            d.text(x, y + 1.0, title, size=9.5, weight="bold")
            d.text(x, y - 1.1, sub, size=8, color=P["dim"])
        else:
            d.text(x, y, title, size=9.5, weight="bold")

    # Root
    d.box(32, 42, 36, 5.4, P["blue"], ec=P["accent"], lw=1.8)
    d.text(50, 45, "Root route", size=11, weight="bold", color=P["accent"])
    d.text(50, 42.5, "receiver: default-slack · group_by: [alertname, cluster]",
           size=8.2, color=P["dim"])

    # Level 1: severity=critical ?
    cond(28, 34, 26, 5, 'severity="critical" ?')
    d.arrow(45, 42, 30, 36.5, color=P["edge"])

    # critical Yes -> pagerduty
    recv(78, 34, 22, 5, "pagerduty-oncall", fc=P["brown"])
    d.arrow(41, 34, 67, 34, color=P["accent"])
    d.text(54, 35.6, "Yes · continue=false", size=8, color=P["accent"])

    # critical No -> team=payments ?
    cond(28, 24, 26, 5, 'team="payments" ?')
    d.arrow(28, 31.5, 28, 26.5, color=P["orange"])
    d.text(35.5, 29, "No", size=8, color=P["orange"])

    # payments No -> default-slack
    recv(78, 24, 26, 5, "default-slack", "루트 receiver", fc=P["gray"])
    d.arrow(41, 24, 65, 24, color=P["orange"])
    d.text(53, 25.6, "No", size=8, color=P["orange"])

    # payments Yes -> severity=warning ?
    cond(28, 14, 32, 5, 'severity="warning" ? (payments)', size=8.5)
    d.arrow(28, 21.5, 28, 16.5, color=P["accent"])
    d.text(34.5, 19, "Yes", size=8, color=P["accent"])

    # warning Yes -> slack-payments-warning
    recv(78, 17, 26, 5, "slack-payments-warning", fc=P["green"])
    d.arrow(44, 14.5, 65, 17, color=P["accent"], rad=-0.1)
    d.text(54, 17.8, "Yes", size=8, color=P["accent"])

    # warning No -> slack-payments (상속)
    recv(78, 10, 26, 5, "slack-payments", "부모 receiver 상속", fc=P["purple"])
    d.arrow(44, 13.5, 65, 10, color=P["violet"], rad=0.1)
    d.text(54, 10.6, "No · 상속", size=8, color=P["violet"])

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.5, label="matcher 일치 (Yes)"),
        Line2D([0], [0], color=P["orange"], lw=2.5, label="불일치 (No)"),
        Line2D([0], [0], color=P["violet"], lw=2.5, label="부모 설정 상속"),
    ])


diagram("14-route-tree", draw, w=13, h=7, ymax=48)
