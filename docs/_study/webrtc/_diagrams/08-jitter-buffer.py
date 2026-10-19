"""CH08 §5 지터 버퍼 — 일정 간격 송신, 들쭉날쭉 도착, 버퍼 지연 후 일정 간격 재생 (light/dark PNG)."""
from _common import diagram

X0 = 16          # 시간축 시작 x
SCALE = 0.5      # ms → x 단위


def tx(ms):
    return X0 + ms * SCALE


def draw(d):
    P = d.P
    y_send, y_arr, y_play = 40, 25, 10
    send = [0, 20, 40, 60, 80, 100]
    delay = [18, 31, 22, 27, 50, 21]          # 네트워크 지연(ms)
    target = 40                               # 재생 = 송신 + 목표 지연

    # 축
    for y, lab in ((y_send, "송신\n(20ms 간격)"), (y_arr, "도착\n(지연이 들쭉날쭉)"),
                   (y_play, "재생\n(다시 20ms 간격)")):
        d.ax.plot([X0 - 2, 98], [y, y], color=P["edge"], lw=1.2, zorder=1)
        d.text(X0 - 3, y, lab, size=8.8, ha="right", weight="bold")

    for i, (s, dl) in enumerate(zip(send, delay)):
        a = s + dl
        p = s + target
        late = a > p
        col = P["orange"] if late else P["accent"]
        # 송신 점
        d.box(tx(s) - 1.4, y_send - 1.4, 2.8, 2.8, P["blue"], lw=1.0, r=0.01)
        d.text(tx(s), y_send + 3.2, f"#{i + 1}", size=8, color=P["dim"])
        # 송신 → 도착
        d.arrow(tx(s), y_send - 1.5, tx(a), y_arr + 1.6, color=col, lw=1.4)
        d.box(tx(a) - 1.4, y_arr - 1.4, 2.8, 2.8,
              P["brown"] if late else P["green"], lw=1.0, r=0.01)
        # 도착 → 재생
        if late:
            d.box(tx(p) - 1.4, y_play - 1.4, 2.8, 2.8, P["chip"], ec=P["orange"],
                  lw=1.2, r=0.01)
            d.text(tx(p), y_play - 4.6, f"#{i + 1} 지각 → 은닉(PLC)", size=7.8,
                   color=P["orange"])
        else:
            d.arrow(tx(a), y_arr - 1.5, tx(p), y_play + 1.6, color=P["dim"],
                    lw=1.1, ls="--")
            d.box(tx(p) - 1.4, y_play - 1.4, 2.8, 2.8, P["green"], lw=1.0, r=0.01)

    # 목표 지연 표시 (첫 패킷)
    yb = 4.0
    d.ax.plot([tx(0), tx(0)], [y_send - 1.5, yb], color=P["violet"], lw=1.0,
              ls=(0, (3, 2)))
    d.arrow(tx(0), yb, tx(target), yb, color=P["violet"], lw=1.4, style="<|-|>")
    d.text(tx(target / 2), yb - 2.0, "버퍼 목표 지연 (40ms)", size=8, color=P["violet"])

    # 시간 방향
    d.arrow(90, 47, 98, 47, color=P["dim"], lw=1.2)
    d.text(89, 47, "시간", size=8, color=P["dim"], ha="right")


diagram("08-jitter-buffer", draw, w=12, h=5.6, ymax=50)
