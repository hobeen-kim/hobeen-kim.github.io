"""CH18 §7 시그널링 연결 수명 — 1시간 상한, 10분 idle, GO_AWAY 유예, 사전 재연결 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    X0, X1 = 14, 96          # 0분 ~ 65분
    def X(m):
        return X0 + (X1 - X0) * m / 65.0

    # 시간축
    y_axis = 7
    d.ax.plot([X(0), X(65)], [y_axis, y_axis], color=P["edge"], lw=1.0)
    for m in (0, 10, 20, 30, 40, 50, 60):
        d.ax.plot([X(m), X(m)], [y_axis - 0.8, y_axis + 0.8],
                  color=P["edge"], lw=1.0)
        d.text(X(m), y_axis - 2.6, f"{m}분", size=8, color=P["dim"])

    def row(y, label):
        d.text(1.5, y, label, size=8.5, ha="left")

    # 행 1: 대응 없는 연결
    y1 = 40
    row(y1, "대응 없음")
    d.box(X(0), y1 - 2, X(60) - X(0), 4, P["gray"], r=0.005)
    d.text(X(30), y1, "WS 연결", size=8, color=P["dim"])
    d.text(X(60) + 0.8, y1 + 0.2, "서버가 종료\n(최대 1시간)", size=7.5,
           color=P["orange"], ha="left")

    # 행 2: 사전 재연결 (make-before-break)
    y2 = 31
    row(y2, "사전 재연결")
    d.box(X(0), y2 - 2, X(41) - X(0), 4, P["blue"], ec=P["accent"], r=0.005)
    d.text(X(20), y2, "WS #1", size=8)
    d.box(X(40), y2 - 6.5, X(65) - X(40), 4, P["blue"], ec=P["accent"],
          r=0.005)
    d.text(X(52), y2 - 4.5, "WS #2 (다음 교체는 80분 무렵)", size=8)
    d.text(X(40) - 0.8, y2 + 3.4, "40분±지터: 새 URL로 #2 연결 → #1 종료",
           size=7.5, color=P["accent"], ha="right")

    # 행 3: GO_AWAY
    y3 = 18
    row(y3, "GO_AWAY 수신")
    d.box(X(0), y3 - 2, X(22) - X(0), 4, P["gray"], r=0.005)
    d.box(X(22), y3 - 2, X(23) - X(22), 4, P["orange"], ec=P["orange"],
          r=0.005, alpha=0.55)
    d.box(X(22.6), y3 - 6.5, X(40) - X(22.6), 4, P["blue"], ec=P["accent"],
          r=0.005)
    d.text(X(31), y3 - 4.5, "새 WS", size=8)
    d.text(X(22), y3 + 3.4, "GO_AWAY → 유예 60초 안에 재연결", size=7.5,
           color=P["orange"], ha="left")

    # 행 4: idle (오른쪽 반)
    d.box(X(40), y3 - 6.5, X(50) - X(40), 4, P["chip"], ec=P["edge"],
          r=0.005)
    d.text(X(45), y3 - 4.5, "메시지 없음 10분", size=7.5, color=P["dim"])
    d.text(X(50) + 0.8, y3 - 4.3, "idle 종료", size=7.5, color=P["orange"],
           ha="left")

    # 1시간 상한선
    d.ax.plot([X(60), X(60)], [y_axis, 46], color=P["orange"], lw=1.2,
              ls=(0, (4, 3)))
    d.text(X(60), 48, "연결 상한 3,600초", size=8, color=P["orange"])


diagram("18-reconnect-timeline", draw, w=12.5, h=5.6, ymax=51)
