"""CH12 remote_write 전송 파이프라인 시퀀스 — WAL watcher·샤드 큐·재시도 (light/dark PNG)."""
from _common import diagram, Line2D


def draw(d):
    P = d.P

    actors = [
        (12, "WAL", P["brown"]),
        (35, "WAL Watcher", P["gray"]),
        (58, "Shard Queue(s)", P["green"]),
        (85, "Remote Storage\n(Mimir 등)", P["blue"]),
    ]
    for x, name, c in actors:
        d.box(x - 9, 50, 18, 4, c)
        d.text(x, 52, name, size=9.5, weight="bold")
        d.ax.plot([x, x], [6, 50], color=P["edge"], lw=1.1, ls="--", zorder=1)

    X_WAL, X_W, X_Q, X_R = 12, 35, 58, 85

    # WAL -> Watcher
    d.arrow(X_WAL, 46, X_W, 46)
    d.text(23.5, 47.4, "새 샘플 append 감지 (tail)", size=8, color=P["dim"])

    # Watcher -> Queue
    d.arrow(X_W, 42, X_Q, 42)
    d.text(46.5, 43.4, "샘플을 샤드에 분배", size=8, color=P["dim"])

    # loop box
    d.box(48, 10, 46, 28, P["chip"], ec=P["orange"], lw=1.4)
    d.text(53, 36.3, "loop", size=8.5, color=P["orange"], weight="bold")
    d.text(72, 36.3, "배치가 차거나 batch_send_deadline", size=8, color=P["orange"])

    # Queue -> Remote
    d.arrow(X_Q, 32, X_R, 32, color=P["orange"])
    d.text(71.5, 33.4, "HTTP POST (Protobuf · snappy)", size=8, color=P["orange"])

    # success
    d.text(52, 27.8, "성공 2xx", size=8, color=P["accent"], weight="bold", ha="left")
    d.arrow(X_R, 25.5, X_Q, 25.5, color=P["accent"], ls="--")
    d.text(71.5, 26.8, "ACK", size=8, color=P["accent"])

    # retryable
    d.text(52, 21.6, "재시도 가능 5xx · 429", size=8, color=P["violet"], weight="bold", ha="left")
    d.arrow(X_R, 19.5, X_Q, 19.5, color=P["violet"], ls="--")
    d.arrow(X_Q + 1, 18.5, X_Q + 1, 16, color=P["violet"], lw=1.6, rad=-1.4)
    d.text(63, 16.8, "지수 백오프 후 재시도", size=8, color=P["violet"], ha="left")

    # non-retryable
    d.text(52, 13.3, "재시도 불가 4xx (429 제외)", size=8, color=P["dim"], weight="bold", ha="left")
    d.arrow(X_Q + 1, 12.3, X_Q + 1, 10.8, color=P["dim"], lw=1.6, rad=-1.4)
    d.text(63, 11.1, "샘플 drop + 카운터 증가", size=8, color=P["dim"], ha="left")

    d.legend([
        Line2D([0], [0], color=P["accent"], lw=2.5, label="정상 흐름 · 성공 ACK"),
        Line2D([0], [0], color=P["orange"], lw=2.5, label="HTTP POST"),
        Line2D([0], [0], color=P["violet"], lw=2.5, label="재시도 (백오프)"),
        Line2D([0], [0], color=P["dim"], lw=2.5, label="drop (재시도 불가)"),
    ])


diagram("12-remote-write-seq", draw, w=14, h=8, ymax=56)
