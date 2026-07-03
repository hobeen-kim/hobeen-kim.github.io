"""CH38 remote_write — 큐 기반 비동기 전송과 적체 전파 시퀀스 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    actors = [
        (13, "WAL / Head", P["brown"]),
        (38, "rw Queue", P["blue"]),
        (62, "Shard (오토스케일)", P["green"]),
        (87, "원격 저장소 (Mimir)", P["gray"]),
    ]
    TOP, BOT = 44, 4.5
    for x, name, fc in actors:
        d.box(x - 10, TOP, 20, 3.8, fc, ec=P["accent"], lw=1.4)
        d.text(x, TOP + 1.9, name, size=9.5, weight="bold")
        d.ax.plot([x, x], [BOT, TOP], color=P["edge"], lw=1.0,
                  ls=(0, (4, 3)), zorder=1)

    def msg(x1, x2, y, label, color, up=True):
        d.arrow(x1, y, x2, y, color=color, lw=1.7)
        mx = (x1 + x2) / 2
        d.text(mx, y + (1.1 if up else -1.1), label, size=8,
               color=color, weight="bold", va="bottom" if up else "top")

    msg(13, 38, 41, "샘플 append", P["accent"])

    d.box(26.5, 29.5, 62, 10, P["chip"], ec=P["accent"], lw=1.2)
    d.text(29, 37.6, "정상 상태", size=8.2, color=P["accent"], weight="bold", ha="left")
    msg(38, 62, 36, "배치 분배", P["accent"])
    msg(62, 87, 33, "HTTP POST (batch)", P["accent"])
    msg(87, 62, 31, "200 OK", P["accent"], up=False)

    d.box(76, 25, 22, 3.4, P["brown"], ec=P["orange"], lw=1.4)
    d.text(87, 26.7, "원격 저장소 지연", size=8, color=P["orange"], weight="bold")

    msg(62, 87, 22.5, "HTTP POST (batch)", P["orange"])
    msg(87, 62, 20.5, "5xx / timeout", P["orange"], up=False)

    d.arrow(62, 16.8, 70, 16.8, color=P["orange"], lw=1.5)
    d.arrow(70, 16.8, 70, 14.8, color=P["orange"], lw=1.5)
    d.arrow(70, 14.8, 62, 14.8, color=P["orange"], lw=1.5)
    d.text(72.5, 15.8, "지수 백오프 재시도", size=8, color=P["orange"],
           weight="bold", ha="left")

    d.box(30, 10, 42, 3.4, P["purple"], ec=P["violet"], lw=1.4)
    d.text(51, 11.7, "큐 적체 → samples_pending 증가", size=8, color=P["text"], weight="bold")

    d.box(20, 5, 44, 3.4, P["brown"], ec=P["orange"], lw=1.4)
    d.text(42, 6.7, "WAL 삭제 지연 → 로컬 디스크 압박", size=8, color=P["orange"], weight="bold")

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.5, label="정상 전송"),
        Line2D([0], [0], color=P["orange"], lw=2.5, label="지연·실패·재시도"),
        Line2D([0], [0], color=P["violet"], lw=2.5, label="적체 상태"),
    ], anchor=(0.005, 0.62))


diagram("38-remote-write", draw, w=13, h=6.4, ymax=49)
