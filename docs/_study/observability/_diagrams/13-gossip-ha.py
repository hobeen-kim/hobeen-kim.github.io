"""CH13 gossip HA 클러스터링 — 중복 알림 억제 시퀀스 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    actors = [
        (10, "Prometheus", P["gray"]),
        (32, "Alertmanager-1", P["green"]),
        (54, "Alertmanager-2", P["blue"]),
        (74, "Alertmanager-3", P["blue"]),
        (91, "Slack", P["brown"]),
    ]
    for x, name, c in actors:
        d.box(x - 8, 47, 16, 4, c)
        d.text(x, 49, name, size=9, weight="bold")
        d.ax.plot([x, x], [5, 47], color=P["edge"], lw=1.1, ls="--", zorder=1)

    XP, X1, X2, X3, XS = 10, 32, 53, 74, 91

    # P -> all AM
    for xt in (X1, X2, X3):
        d.arrow(XP, 44, xt, 44, color=P["accent"])
    d.text(43, 45.4, "동일 알림을 전체 인스턴스에 전송", size=8, color=P["accent"])

    # gossip cluster note
    d.box(24, 37, 60, 3.6, P["chip"], ec=P["orange"], lw=1.4)
    d.text(54, 38.8, "gossip 클러스터 (memberlist · 포트 9094)", size=8.5, color=P["orange"])

    # notification log 전파
    d.arrow(X1, 33, X2, 33, color=P["violet"], ls="--")
    d.arrow(X1, 30, X3, 30, color=P["violet"], ls="--")
    d.text(64, 34.2, "notification log 전파 (P2P)", size=8, color=P["violet"])

    # self checks
    def selfnote(x, y, s, color):
        d.box(x - 10, y - 2.0, 20, 4.0, P["chip"], ec=color, lw=1.2)
        d.text(x, y, s, size=7.8, color=P["text"])

    selfnote(X1, 24.5, "이미 통지한 알림인지 확인", P["green"])
    selfnote(X2, 24.5, "A1이 이미 보냈음 인지\n→ 통지 생략", P["violet"])
    selfnote(X3, 24.5, "A1이 이미 보냈음 인지\n→ 통지 생략", P["violet"])

    # A1 -> Slack (1회만)
    d.arrow(X1, 19, XS, 11.5, color=P["orange"], rad=-0.06)
    d.text(58, 16, "A1이 알림 전송 (1회만)", size=9, color=P["orange"])

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.5, label="알림 전송"),
        Line2D([0], [0], color=P["violet"], lw=2.5, ls="--", label="notification log gossip"),
        Line2D([0], [0], color=P["orange"], lw=2.5, label="채널로 1회 통지"),
    ])


diagram("13-gossip-ha", draw, w=14, h=7.5, ymax=53)
