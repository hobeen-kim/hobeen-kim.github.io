"""40장: 입력 유닛이 구성을 바꿀 때 Maintenance를 500 ms 넘게 멈추고 Initializing으로 다시 시작해 Ready가 되기까지의 시간축 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    X0, X1 = 4, 96
    T_MAX = 2400

    def tx(t):
        return X0 + (X1 - X0) * t / T_MAX

    AXIS = 26
    d.arrow(X0, AXIS, X1 + 2, AXIS, color=P["edge"], lw=1.4)
    d.text(X1 + 2, AXIS - 2.4, "시간", size=9, color=P["dim"], ha="right")
    for t in (0, 600, 1300, 1900):
        d.text(tx(t), AXIS - 2.6, f"{t} ms", size=8.6, color=P["dim"])
    d.text(tx(900) + 0.6, AXIS - 2.6, "900 ms", size=8.6, color=P["dim"], ha="left")

    def ticks(t0, t1, color):
        t = t0
        while t <= t1:
            d.ax.plot([tx(t), tx(t)], [AXIS + 0.4, AXIS + 3.4], color=color, lw=1.6)
            t += 100

    ticks(0, 600, P["accent"])
    d.text((tx(0) + tx(600)) / 2, AXIS + 5.4, "Maintenance (Ready)", size=8.8, color=P["accent"])
    d.text((tx(0) + tx(600)) / 2, AXIS + 8.2, "100 ms마다", size=8.4, color=P["dim"])

    ticks(1300, 1800, P["orange"])
    d.text((tx(1300) + tx(1800)) / 2, AXIS + 5.4, "Initializing", size=8.8, color=P["orange"])
    d.text((tx(1300) + tx(1800)) / 2, AXIS + 8.2, "새 Model ID", size=8.4, color=P["dim"])

    ticks(1900, 2300, P["accent"])
    d.text((tx(1900) + tx(2300)) / 2, AXIS + 5.4, "Ready", size=8.8, color=P["accent"])

    # 멈춘 구간
    d.ax.plot([tx(600), tx(1300)], [AXIS + 12.5, AXIS + 12.5], color=P["violet"], lw=1.3)
    d.ax.plot([tx(600), tx(600)], [AXIS + 11.5, AXIS + 12.5], color=P["violet"], lw=1.3)
    d.ax.plot([tx(1300), tx(1300)], [AXIS + 11.5, AXIS + 12.5], color=P["violet"], lw=1.3)
    d.text((tx(600) + tx(1300)) / 2, AXIS + 14.6, "송신을 500 ms보다 길게 멈춤", size=8.8,
           color=P["violet"])

    # 300 ms 타임아웃
    d.ax.plot([tx(900), tx(900)], [AXIS - 4.5, AXIS + 9.5], color=P["orange"], lw=1.4,
              ls=(0, (3, 2)))
    d.box(tx(900) - 13, 7.5, 26, 9.0, P["chip"], ec=P["orange"], lw=1.3)
    d.text(tx(900), 14.0, "300 ms 동안 없음", size=8.8, color=P["orange"], weight="bold")
    d.text(tx(900), 11.4, "VT와 기능 Working Set이", size=8.6)
    d.text(tx(900), 9.2, "할당을 모두 제거", size=8.6)

    # 풀 갱신과 응답
    d.box(tx(1300), 15.4, tx(1900) - tx(1300), 4.2, P["purple"], lw=1.0)
    d.text((tx(1300) + tx(1900)) / 2, 17.5, "풀 갱신", size=8.8)
    d.arrow(tx(1900), 14.6, tx(1900), 10.6, color=P["dim"], lw=1.3)
    d.text(tx(1900), 8.6, "End of Object Pool response", size=8.4, color=P["dim"])
    d.text(tx(1900), 6.2, "(오류 없음)", size=8.4, color=P["dim"])

    d.arrow(tx(2300), 30.6, tx(2300), 41.5, color=P["accent"], lw=1.5)
    d.text(tx(2300) + 4, 46.4, "기능 Working Set이", size=8.6, color=P["accent"], ha="right")
    d.text(tx(2300) + 4, 44.0, "Preferred Assignment를 다시 보냄", size=8.6, color=P["accent"], ha="right")


diagram("40-aux-maintenance-timeline", draw, w=12.5, h=6.4, xmax=100, ymax=50)
