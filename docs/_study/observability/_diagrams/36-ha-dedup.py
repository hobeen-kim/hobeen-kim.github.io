"""CH36 Prometheus HA — 독립 레플리카와 다운스트림 중복 제거 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P
    lanes = [
        (13, "Prometheus A\n(replica=a)", P["blue"]),
        (38, "Prometheus B\n(replica=b)", P["green"]),
        (65, "Alertmanager\n클러스터", P["brown"]),
        (87, "Mimir\n(dedup 쿼리)", P["purple"]),
    ]
    top_y, bot_y = 44, 5
    X = {}
    for x, name, fc in lanes:
        d.box(x - 9, 44.5, 18, 4.6, fc)
        d.text(x, 46.8, name, size=9.3, weight="bold")
        d.ax.plot([x, x], [bot_y, top_y], color=P["edge"], lw=1.0, ls="--", zorder=1)
        X[name] = x

    A, B, AM, M = (n for _, n, _ in lanes)

    def msg(y, a, b, label, dashed=False, color=None):
        ls = "--" if dashed else "-"
        x1, x2 = X[a], X[b]
        d.arrow(x1, y, x2, y, color=color or P["accent"], lw=2.0, ls=ls)
        d.text((x1 + x2) / 2, y + 1.3, label, size=8, color=P["dim"])

    def note(y, lane, label, w=22):
        x = X[lane]
        d.box(x - w / 2, y - 1.9, w, 3.8, P["chip"], ec=P["orange"], lw=1.2)
        d.text(x, y, label, size=8, color=P["orange"])

    # 독립 스크레이프 · 룰 평가
    d.box(4, 36, 43, 5, P["chip"], ec=P["accent"], lw=1.2)
    d.text(6, 39.6, "독립적으로 스크레이프 · 룰 평가", size=8.3, color=P["accent"], ha="left")
    d.text(13, 37.4, "타깃 스크레이프", size=7.6)
    d.text(38, 37.4, "타깃 스크레이프", size=7.6)

    msg(31, A, AM, "Alert 발화", color=P["orange"])
    msg(26.5, B, AM, "동일 Alert (fingerprint 동일)", color=P["orange"])
    note(21, AM, "gossip으로 중복 인지\n1건만 발송")

    msg(15, A, M, "remote_write (replica=a)", dashed=True, color=P["violet"])
    msg(10.5, B, M, "remote_write (replica=b)", dashed=True, color=P["violet"])
    note(5, M, "쿼리 시 replica\n라벨 기준 dedup")

    d.legend([
        Line2D([0], [0], color=P["orange"], lw=2.4, label="알림 발화 → gossip dedup"),
        Line2D([0], [0], color=P["violet"], lw=2.4, ls="--", label="remote_write → replica dedup"),
    ], loc="lower left", anchor=(0.005, 0.02))


diagram("36-ha-dedup", draw, w=14, h=7.5, ymax=52)
